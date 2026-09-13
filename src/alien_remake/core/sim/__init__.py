"""The fixed-tick simulation driver (headless, stdlib only).

:class:`Simulation` owns a :class:`~alien_remake.core.state.GameState` and
advances it one fixed tick at a time (GAME_SPEC §2: real-time at ~``TICK_HZ``).
Player orders are **queued asynchronously** and consumed on tick boundaries; each
is put through the **Personality Control System** (GAME_SPEC §5) — the crew
may obey, hesitate, or refuse per their state of mind. The driver does no I/O and
never sleeps; real-time pacing is the renderer/runner's job, so tests step it
deterministically (a seeded ``rng`` makes the PCS reproducible too).

The Alien is a weighted-random compass walk over the real route tables,
NOT sensing/hunting the nearest crew (that model was invented and corrected,
`core.alien`) — plus combat, the three win conditions, and the Special Options
(`core.special_options`): `advance()` now moves the Alien after orders are
processed, checks for an all-crew-dead loss, and ticks any running auto-destruct
countdown; `apply_special_option` handles the ship-wide actions (airlock,
Narcissus, hypersleep, auto-destruct, catching Jones) that aren't per-crew
PCS orders.

Game modes live in `core.modes` (GAME_SPEC §9/§11 #6): the constructor takes
a `mode` (short vs. full) and a `death_variant` (fixed vs. random — which crew
member is already dead at the opening), applied only when the Simulation builds
its own starting ship/state/crew.

From the decompile audit (docs/re/GAMEDATA.md): movement now runs on the real
per-character timers — each crew member has a walk duration (ticks per room,
the game's $6586 table), Jones ambles on his own 5-tick timer, and the Alien
manages its own action countdown inside `advance_alien`. `LAUNCH_NARCISSUS`
collects survivors in the real SHUTTLEBAY (evac bay) rather than an airlock.
"""

from __future__ import annotations

import random
from collections import deque

from .. import constants, gamedata_snapshot
from ..alien import (
    JONES_ROLL_SIDES,
    add_room_damage,
    advance_alien,
    jones_dest,
    panic_dest,
    resolve_attack,
    restore_stowed_char,
    spawn_alien,
    tracker_zone,
)
from ..constants import (
    AUTO_DESTRUCT_OVERRIDE_ABOVE,
    AUTO_DESTRUCT_SUBTICKS,
    AUTO_DESTRUCT_TICKS,
    CROWD_THRESHOLD,
    FEAR_BUMP_CORPSE,
    FEAR_BUMP_CROWDED,
    HULL_BREACH_THRESHOLD,
    ITEM_DESTROYED_ON_ATTACK,
    ROOM_CAPACITY,
    ROOM_DAMAGE_PER_ATTACK,
    ROOM_DAMAGE_PER_ATTACK_HARPOON,
)
from ..crew import (
    CARRY_CAPACITY,
    CrewMember,
    assign_start_rooms,
    default_crew,
    morale_word,
)
from ..items import spawn_items
from ..map import Direction, ShipMap, move_cursor, shortest_room_path
from ..modes import (
    AlienStart, AndroidVariant, DeathVariant, GameMode, JonesCatch,
    choose_android,
    choose_opening_death,
)
from ..nostromo import nostromo_ship
from ..sound import (
    AIRLOCK,
    ATTACK_ALERT,
    GRILLE,
    MOVEMENT,
    TRACKER_ALARM,
    SoundCue,
)
from ..orders import (
    SURVIVING_OUTCOMES,
    Order,
    OrderOutcome,
    OrderType,
)
from ..special_options import SpecialOption, SpecialOptionType
from ..devtools import DevControls
from ..state import GamePhase, GameState, WinRoute
from .orders import OrderMixin
from .specials import SpecialsMixin

#: **[C $5077 `STA $793C`]** `$793C` is `$7935 + 7` — the **slot-7** character.
#: Slot 0 of that table is the Alien (`$7D45`, its parallel health table, is
#: compared against `#$32` = the Alien's 50-damage death threshold at `$60D8`),
#: so slots 1-7 are the crew in `CREW_NAMES` order and slot 7 is BRETT.
_BRETT_SLOT = 7


class Simulation(OrderMixin, SpecialsMixin):
    """Drives a :class:`GameState` forward in fixed ticks."""

    def __init__(
        self,
        state: GameState | None = None,
        ship: ShipMap | None = None,
        rng: random.Random | None = None,
        mode: GameMode = GameMode.FULL,
        death_variant: DeathVariant = DeathVariant.ORIGINAL,
        alien_start: AlienStart = AlienStart.ORIGINAL,
        jones_catch: JonesCatch = JonesCatch.PATIENT,
        android_variant: AndroidVariant = AndroidVariant.ORIGINAL,
        weapon_breach_gates: bool = False,
    ) -> None:
        # `mode`/`death_variant` (GAME_SPEC §9/§11 #6) only shape a state
        # the Simulation builds itself — same "only touch what we own"
        # convention as the ship/crew/items/Alien defaults below, so an
        # explicitly-supplied GameState is never mutated out from under a test.
        self.state = (
            state if state is not None else GameState(mode=mode)
        )
        # The ship topology: the SM oracle-transcribed Nostromo, owned here (not
        # on GameState). `default_ship` remains the documented fallback.
        self.ship = ship if ship is not None else nostromo_ship(mode)
        # Randomness source for the PCS gate; injectable/seedable for tests.
        self.rng = rng if rng is not None else random.Random()
        #: **Developer-mode switches only** (`core.devtools`). All off is the
        #: shipping game, and `advance` consults them at exactly two points.
        self.dev = DevControls()
        # Whether a missed grab spooks the cat (DISC-262).
        self.jones_catch = jones_catch
        # Which crew can be the hidden android. Must be set before the opening
        # runs below, which is what draws them.
        self.android_variant = android_variant
        #: **[C $4A8D/$4AF6] DEC-044 — the ROM's pre-add weapon breach gates,
        #: OFF by default (ORIGINAL's exact shipped behaviour).** Decoded and
        #: measured (DISC-258/DISC-289) to make the game unwinnable at the
        #: values that shipped when this was written; retuned and enabled for
        #: the UPDATED preset only (`__main__.py` sets this from
        #: `not options.is_original(...)`, same gate `pointer_allowed` uses).
        #: See `_resolve_attack_order` for where it is actually checked.
        self.weapon_breach_gates = weapon_breach_gates
        # Populate the seven crew unless the caller already staged some on
        # the state. Placed on the top deck (the opening, GAME_SPEC §9).
        if not self.state.crew:
            self.state.crew = default_crew(self.ship)
            if mode is GameMode.SHORT:
                self._apply_short_scenario()
            else:
                self._apply_full_opening(death_variant)
        # Populate the item catalog unless the caller already staged some.
        # Placement is the game's own fixed table (later RE), not random.
        if not self.state.items:
            self.state.items = spawn_items(self.ship)
            if mode is GameMode.SHORT:
                self._apply_short_item_moves()
        # Spawn the Alien unless the caller already staged one.
        if self.state.alien is None:
            # `alien_start` defaults to the ROM's fixed AIRLOCK 1 (`$7935` slot
            # 0). RANDOM is an added rule (DISC-260) and keeps the creature off
            # the crew's own starting rooms, so a game cannot open with it
            # already standing among them.
            self.state.alien = spawn_alien(
                self.ship, alien_start, self.rng,
                avoid={c.room_id for c in self.state.crew.values() if c.room_id},
            )
        # Place Jones the cat unless the caller already staged it — round-
        # robin like the crew, on the same starting deck (GAME_SPEC §9).
        if self.state.jones_room_id is None and not self.state.jones_caught:
            rooms = self.ship.rooms_on(self.state.deck)
            self.state.jones_room_id = rooms[0].id if rooms else None
        # Structured PCS orders, queued and consumed on tick boundaries.
        self._orders: deque[Order] = deque()
        # Jones's walk countdown (he moves on the shared timer
        # engine — slot 8 of the game's character arrays — not by coin-flip).
        self._jones_timer = constants.JONES_MOVE_TICKS   # D-153 ($88B6)
        #: $657E — the destination picked one move AHEAD (D-156).
        self._jones_next: str | None = None
        # **[C $64EE] P5-6 — characters act on TURNS, not on every tick.**
        # The ROM gives each character an action countdown (`$64EE,Y`) loaded
        # with `$7B69`'s `#$40` plus `compute_action_delay`, and the routines
        # that hurt or unnerve people hang off that: the android's attack is
        # reached from `dispatch_char_action` during its own turn, and
        # `raise_crowd_fear` is called once per **Alien** turn (`$4CC3`, inside
        # the `$4CB3` block). Running them per tick made the android wound
        # someone ~60x too often — four of seven crew were unusable within
        # three seconds of starting.
        #: Ids whose `$64EE,Y` expired on this pass — recomputed by
        #: `_pump_characters` at the top of every `advance` (D-168).
        self._due: set[str] = set()
        # Per-tick record of what happened to each processed order (for the
        # Command Monitor UI and tests). Reset every advance().
        self.last_outcomes: list[tuple[Order, OrderOutcome]] = []
        # D-059: crew whose death has already applied the ship-wide composure
        # hit (`$47DC`/`$5A0D` fire once per death, not per tick). Seeded with
        # anyone already dead at construction (the opening death is a scenario
        # premise, not an event the survivors witness).
        self._mourned_dead: set[str] = {
            c.id for c in self.state.crew.values() if not c.alive
        }

    def _apply_full_opening(self, death_variant: DeathVariant) -> None:
        """The randomised FULL opening (GAME_SPEC §9)."""
        dead_id = choose_opening_death(list(self.state.crew), death_variant, self.rng)
        dead = self.state.crew[dead_id]
        dead.alive = False
        dead.awake = False
        dead.health = 0  # found dead at the opening -> "DEAD" status
        assign_start_rooms(self.state.crew, self.ship)
        self.state.opening_dead_crew_id = dead_id
        # **[C $5074-$5077] the opening always seats the survivors 3 + 3, and
        # BRETT is the floater who fills the gap.**
        #
        #     506E  LDA $50EC,Y / STA $64C2   ; the victim's slot
        #     5074  LDA $510C,Y               ; ...and, SAME Y, a room
        #     5077  STA $793C                 ; -> $7935+7, Brett's own slot
        #
        # One RNG draw indexes both tables, so Brett's destination is locked to
        # the victim and all 16 entries pair the victim with the room they
        # started in. The template seats three in COMMDCENTR, three in MESS and
        # Brett in AIRLOCK 1; moving him into the vacancy restores 3-and-3
        # however the roll lands. His airlock entry is a parking slot the
        # opening overwrites every game - he is never there in play.
        # Derivation: DISCOVERIES DISC-229.
        brett_id = next(
            (c.id for c in self.state.crew.values()
             if self._slot_of(c) == _BRETT_SLOT),
            None,
        )
        brett = self.state.crew.get(brett_id) if brett_id else None
        if brett is not None and brett.alive and dead.room_id is not None:
            brett.room_id = dead.room_id
        # [C $507A-$5086] D-080: the android is rolled right after the
        # victim and re-rolled until it differs from them.
        self.state.android_id = choose_android(
            list(self.state.crew), dead_id, self.rng, self.android_variant
        )

    def _apply_short_item_moves(self) -> None:
        """SHORT pulls three items into COMMDCENTR — [C $6051-$6057], D-085.

        `$604F` writes room 6 into the `$82E3` item-room array at instances
        7, 16 and 17 — a TRACKER, the NET and the CAT BOX — i.e. straight into
        the room where three of the crew start. The short game hands you the
        tracker and the cat box up front instead of making you hunt for them.

        Separate from :meth:`_apply_short_scenario` only because the item
        catalog is spawned after the crew block.
        """
        from ..gamedata_snapshot import ROOM_SLUGS, SHORT_ITEM_MOVES

        by_index = list(self.state.items.values())
        for instance, room in SHORT_ITEM_MOVES:
            if instance < len(by_index) and room < len(ROOM_SLUGS):
                by_index[instance].room_id = ROOM_SLUGS[room]
                by_index[instance].holder = None

    def _apply_short_scenario(self) -> None:
        """The SHORT SCENARIO's **fixed** opening — [C $604F], D-085.

        SHORT is not "FULL but quicker": `$604F` (reached only from the Ctrl+2
        branch at `$5F4E`) overwrites the randomised opening with a scripted
        one. It pins the victim to **KANE** (`$6062 LDA #$02 / STA $64C2`) and
        the android to **ASH** (`$6067 LDA #$04 / STA $64C3`), then copies four
        7-entry tables over the crew arrays — locations (`$608C` -> `$7936,Y`),
        health (`$6093` -> `$7D46,Y`), composure (`$609A` -> `$7D56,Y`) and the
        composure mirror (`$60A1` -> `$6572,Y`).

        The result is a far more desperate start than FULL: Dallas and Brett on
        1 health, Ash on 0, and the survivors split across LIVNG QTRS / COMMD
        CENTR / STORES 1. **This is why the earlier "GameMode has no mechanical
        effect" conclusion was wrong** — it was drawn after the invented
        oxygen budget was removed, without checking whether the ROM had its own
        mode-specific setup. It does.
        """
        from ..gamedata_snapshot import (
            CREW_NAMES,
            ROOM_SLUGS,
            SHORT_ANDROID_SLOT,
            SHORT_DUCT_SLOTS,
            SHORT_SCENARIO,
            SHORT_VICTIM_SLOT,
        )

        locs, health, composure, _mirror = SHORT_SCENARIO
        roster = list(self.state.crew)
        for slot, name in enumerate(CREW_NAMES, start=1):
            cid = name.lower()
            crew = self.state.crew.get(cid)
            if crew is None:
                continue
            i = slot - 1
            room = locs[i]
            crew.health = health[i]
            crew.fear = composure[i]
            if room == constants.CHAR_GONE_MARKER:
                crew.alive = False
                crew.awake = False
                crew.room_id = None
            else:
                crew.alive = crew.health > 0
                crew.room_id = ROOM_SLUGS[room] if room < len(ROOM_SLUGS) else None
        victim = CREW_NAMES[SHORT_VICTIM_SLOT - 1].lower()
        self.state.opening_dead_crew_id = victim if victim in roster else None
        android = CREW_NAMES[SHORT_ANDROID_SLOT - 1].lower()
        self.state.android_id = android if android in roster else None
        # [C $605A-$605F] Two crew start **already in the ducts** — `$6502` and
        # `$6508`, i.e. the `$6501` in-duct array at slots 1 and 7.
        for slot in SHORT_DUCT_SLOTS:
            crew = self.state.crew.get(CREW_NAMES[slot - 1].lower())
            if crew is not None:
                crew.in_duct = True


    def select_deck(self, deck: int) -> bool:
        """Switch the map view to ``deck`` if it exists; True on success."""
        if deck in self.ship.decks():
            self.state.deck = deck
            return True
        return False

    def move_cursor(self, direction: Direction) -> tuple[int, int]:
        """Move the map cursor one step on the current deck (clamped)."""
        x, y = self.state.cursor
        self.state.cursor = move_cursor(self.ship, self.state.deck, x, y, direction)
        return self.state.cursor





    def morale_for(self, crew: CrewMember) -> str:
        """Mother's state-of-mind word — **[C $7DCB] PV-07 / D-163.**

        `fear_band` reads **`$6571,Y`**, the *derived* composure cell that
        `init_char_turn` writes, not the raw `$7D55`. So the word on the panel
        already includes the companion-support term (D-151): a shaky crew
        member standing with a steady colleague **reads calmer**, and reads
        worse again the moment that colleague leaves the room. The remake
        showed the bare base value, so the panel never reacted to company at
        all — even though the panic gate it is meant to warn you about does.
        """
        return morale_word(self.effective_composure(crew))

    def effective_composure(self, crew: CrewMember) -> int:
        """This turn's **effective** composure — **[C $4784] D-151.**

        The PCS keeps *two* values per character, and the remake only had
        one. `$7D55,Y` is the character's own **base** composure, changed by
        real events (deaths, wounds, hiding in a duct, crowding). `$6571,Y`
        is what every gate actually reads, and `init_char_turn ($4784)`
        recomputes it at the start of each character's turn::

            47A2  STA $4781                  ; modifier := 0
            47B3  LDA $7935,Y / STA $457F    ; the actor's room
            47B9  LDX #$01                   ; ...loop the other slots
            47BB  CPX $64B1 / BEQ next       ;   skip self
            47C0  LDA $7935,X / CMP $457F    ;   same room only
            47C8  LDA $6501,X / BNE next     ;   ...and on the surface
            47F1  LDA $7D45,X / CMP #$02
            47F6  BCS $47FE
            47F8  DEC $4781                  ;   collapsed mate: modifier -1
            47FE  LDA $7D55,X / ADC $4781
            4805  SEC / SBC #$02 / STA $4781 ;   else modifier += theirs - 2
            4832  LDA $7D55,Y / ADC $4781    ; effective = base + modifier
            483F  BPL / LDA #$00             ; ...floored at 0
            4843  STA $6571,Y

        So **company steadies you**: each co-located, surfaced crew member
        contributes `their base composure - 2`, which is positive for anyone
        calmer than "uneasy" and negative for anyone worse; a collapsed
        companion (health < 2) costs a flat 1. This is the manual's "knowing
        that others of the crew are on their way to help", implemented.

        Missing it is why the crew panicked so readily: every gate
        (`$5170` panic-wander, `$7757` selection, `$5459` the android,
        `$4E16` the heartbeat rate, `$7DC5` the MORALE word) was reading a
        bare base value with no support term.

        A character **inside a duct** skips the scan entirely (`$47A8 LDA
        $6501,Y / BNE`) — alone in the walls there is nobody to draw on — so
        their effective composure is just their base.
        """
        base = int(crew.fear)
        if crew.in_duct or crew.room_id is None:
            return max(constants.FEAR_MIN, base)
        modifier = 0
        for other in self.state.crew.values():
            if other.id == crew.id or not other.alive:
                continue
            if other.room_id != crew.room_id or other.in_duct:
                continue
            if other.health < constants.COMPANION_SUPPORT_MIN_HEALTH:
                modifier -= 1                                   # $47F8
            else:
                modifier += int(other.fear) - constants.COMPANION_SUPPORT_PIVOT
        return max(constants.FEAR_MIN, base + modifier)          # $483F






    def _slot_of(self, crew: CrewMember) -> int:
        """This crew member's character slot (1-7), or 0 if not a real one.

        The slot is what both per-character timing tables are indexed by —
        `$4032` (`compute_action_delay`) and `$403A` (REMVGRILLE, D-166).
        """
        from ..gamedata_snapshot import CREW_NAMES

        try:
            return [n.lower() for n in CREW_NAMES].index(crew.id) + 1
        except ValueError:
            return 0







    def _room_occupants(self, room_id: str, *, exclude: str | None = None) -> int:
        """Count alive crew currently in ``room_id`` (optionally excluding one)."""
        return sum(
            1
            for c in self.state.crew.values()
            if c.alive and c.room_id == room_id and c.id != exclude
        )



    def _android_ignores_order(self, crew: CrewMember) -> bool:
        """True when the android should silently discard this order ([C $5265]).

        The gate is precise: the crew member must **be the android**, share the
        Alien's room *and* duct state (`$5272`/`$527A`), and still be healthy
        (`$528A CMP #$04` — below that the ROM sends it to `char_wander`
        instead, so it panics rather than stonewalls).
        """
        if crew.id != self.state.android_id:
            return False
        # [C $526A] Once `$64CC` is set the android is diverted to `$52F1`
        # instead, which only ever attacks or `char_wander`s — it never reaches
        # `dispatch_char_action`, so a revealed android obeys nothing at all.
        if self.state.android_revealed:
            return True
        alien = self.state.alien
        if alien is None or alien.room_id != crew.room_id:
            return False
        if crew.in_duct != getattr(alien, "in_duct", False):
            return False
        return crew.health >= constants.ANDROID_OBEY_MIN_HEALTH

    def _reveal_android(self) -> None:
        """Set `$64CC` once the android is found out ([C $52A4-$52DA]).

        Requires the Alien to have taken `>= 6` damage — the crew have been
        fighting it — **and** a crew member to be standing in the android's room
        who is out of the ducts, health >= 2 and not broken. The ROM also writes
        the flag to `$D021`, flashing the background: the player's only tell.
        """
        state = self.state
        if state.android_revealed or state.android_id is None:
            return
        alien = state.alien
        if alien is None or alien.damage < constants.ANDROID_REVEAL_ALIEN_DAMAGE:
            return
        android = state.crew.get(state.android_id)
        if android is None or not android.alive or android.room_id is None:
            return
        for crew in state.crew.values():
            if crew.id == state.android_id or not crew.alive:
                continue
            if crew.room_id != android.room_id or crew.in_duct:
                continue
            if crew.health < constants.ANDROID_REVEAL_MIN_HEALTH:
                continue
            if crew.fear == constants.FEAR_MIN:      # $52CA composure 0 -> skip
                continue
            state.android_revealed = True
            # **[C $52D4] `LDA $7214 / STA $64CC`** — `$7214` is written only at
            # `$723E STY $7214`, the *acting* character's slot, so `$64CC`
            # records **the android itself**, not the crew member it found. The
            # next instruction (`$52DA STA $D021`) flashes the background with
            # that same slot number: being locked out of selection IS the tell.
            state.locked_crew_id = state.android_id
            # `$52DA STA $D021` — the same slot number goes to the background
            # register, recolouring every glyph's ink at once.
            state.background_colour = self._slot_of(android)
            return

    def _attack_sequence_active(self) -> bool:
        """Is `$6562` raised this pass? — **[C $8CD9/$8C85] PV-12/D-165.**

        `$8CD9 INC $6562` fires as an Alien/crew encounter begins and
        `reset_attack_state ($8C85 STA $6562` = 0`)` clears it on the next
        move pass, so the latch is live for exactly one pass. The remake
        already emits `ATTACK_ALERT` on that same event and wipes
        `state.sound_cues` at the top of each `advance`, so the presence of
        that cue is the latch — no extra state required.

        Note `check_6562 ($8E32)` **loads `$6562` and then falls into an
        unconditional `JMP $8E39`**, so its own guard is dead code: the
        tracker scan runs during an attack sequence regardless. That is
        modelled by simply not gating `_scan_trackers` on this.
        """
        return any(cue.effect == ATTACK_ALERT for cue in self.state.sound_cues)

    def _apply_android_attack(self) -> None:
        """The **revealed** android's own turn — **[C $52F1] D-152**.

        D-126 established that `$5265` routes the android here only once
        `$64CC` is set; this is that path in full, and its gates are NOT the
        ones the old docstring cited. `$5439`/`$5459` is a *different*
        routine (a `sub_char_special` action-code-3 handler reached from
        `$8754`); the revealed android's turn is `$52F1`, and it differs on
        three counts — a duct test the other path lacks, a composure test at
        a different threshold **on a different cell**, and two pre-scan
        escapes::

            52FC  CMP $7935 / BNE $5309      ; same room as the ALIEN...
            5301  LDA $6501 / BNE $5309      ; ...and it is surfaced?
            5306  JMP char_wander            ;   -> the android FLEES
            5309  LDA $6562 / BEQ $5311
            530E  JMP char_wander            ; attack sequence -> FLEES
            5311  LDY #$01                   ; ...else scan for a victim
            5313  CPY $64C3 / BEQ next       ;   not itself
            5318  LDA $6501,Y / BNE next     ;   not inside a duct
            531D  LDA $7D45,Y / CMP #$02     ;   health >= 2
            5324  LDA $7D55,Y / BEQ next     ;   BASE composure != 0
            5329  LDA $7935,Y / CMP $53E3    ;   same room as the android
            5331  JMP $5345                  ;   -> wound them (" HITS ")
            5339  LDY $7214 / JMP char_wander; nobody -> wander

        Two corrections that materially change who gets hurt:

        * **`$5324` reads `$7D55` — the BASE composure — and skips only on
          exactly 0**, where we were testing the *effective* value against a
          threshold of 2 (D-151's `$5459` citation, which belongs to the
          other routine). That spared anyone merely shaken.
        * **`$5318` skips a victim inside a duct entirely**, which we never
          checked — the android could reach into the walls.

        **PV-12 closed 2026-08-07 (D-165) — `$6562` is now modelled.**
        Enumerating its four readers pins it down as the **attack-sequence
        latch**: `$8CD9 INC $6562` raises it when an Alien/crew encounter
        fires (the same instruction that arms `$64A3` and, for the selected
        character, writes "ATTACK" into `$064E`), and `reset_attack_state
        ($8C85)` clears it on the next move pass — so it is live for exactly
        one pass. While raised it suppresses three things: this android
        attack (`$5309` -> `char_wander`), character-turn selection (`$8DF0
        LDA $6562 / BNE rts`), and the Alien's room corrosion (`$8EBD`).

        The remake raises `SoundCue(ATTACK_ALERT)` on precisely the ROM event
        that sets it (D-090 cites `$8CD9-$8CF3` for that cue), and clears the
        cue list at the top of every `advance` — so the cue list **is** the
        latch, at the same one-pass granularity, without inventing new state.
        """
        android_id = self.state.android_id
        if android_id is None:
            return
        android = self.state.crew.get(android_id)
        if android is None or not android.alive or android.room_id is None:
            return

        def wander() -> None:
            """`char_wander ($5203)` — the android's own escape/idle move."""
            assert android is not None and android.room_id is not None
            dest = panic_dest(
                self.ship, android.room_id,
                self.rng.randrange(constants.ALIEN_ROLL_SIDES),
            )
            if dest is not None:
                android.room_id = dest

        # **[C $5309] PV-12/D-165** — an attack sequence is in progress, so the
        # android does not press its own attack; it wanders. Checked before the
        # co-location test because the ROM checks it second and both end in
        # `char_wander`, making the order unobservable — but this one also
        # covers encounters happening elsewhere on the ship.
        if self._attack_sequence_active():
            wander()
            return

        # $52FC-$5306: it will not attack in front of a surfaced Alien; it runs.
        alien = self.state.alien
        if (
            alien is not None
            and alien.alive
            and not alien.in_duct
            and alien.room_id == android.room_id
        ):
            wander()
            return

        for crew in self.state.crew.values():
            if crew.id == android_id or not crew.alive:
                continue                                       # $5313
            if crew.in_duct:
                continue                                       # $5318
            if crew.health < constants.ANDROID_ATTACK_MIN_HEALTH:
                continue                                       # $531D
            if crew.fear == constants.FEAR_MIN:
                continue                    # $5324 — BASE composure, == 0 only
            if crew.room_id != android.room_id:
                continue                                       # $5329
            crew.wound()                    # $5345 -> alien_wound_crew ($5354)
            # **NOTE — this path does NOT touch `$64CC`.** The only writer is
            # `$52D7`, on the *reveal* path, and it stores `$7214` — the
            # acting slot, i.e. the android itself (D-126).
            return                                # the ROM wounds one per pass
        wander()                                  # $5339: nobody here to hurt

    def _apply_panic_wander(self) -> None:
        """Panicking crew bolt instead of obeying (`char_wander $5203`).

        **[C $5170-$5262], corrected 2026-08-06 (D-130) — P6-3.** The original
        model checked only "shares a room with the surfaced Alien," evaluated
        every tick, which sent every crew member of every composure bolting
        the instant the Alien attacked anyone. The real entry gate is
        `resolve_char_move` — the per-character engine's own turn-resolution
        routine, run at *that character's* cadence, not every tick::

            5170  LDA $6571,Y / CMP #$02 / BCC $517A   ; composure < 2, else
                                                        ; ordinary dispatch
            517A  LDA $6501,Y / BNE $5182              ; in a duct -> ordinary
            51DF  LDA $6571,Y / BEQ $51E7               ; composure == 0 ->
                                                        ; wanders unless also
                                                        ; sharing a SURFACED
                                                        ; Alien's room (a
                                                        ; different, undecoded
                                                        ; outcome at $51F4)
            5252  ...composure == 1 path: wanders ONLY when sharing a room
                  with a surfaced Alien...

        So an ordinary-composure (>= 2) crew member never wanders at all —
        composure has to already be broken or nearly broken. Once triggered,
        the walk itself is unchanged: an **Alien-style random walk** (rolls
        `rng` 0-15 through the Alien's own route tables,
        :func:`alien.panic_dest`, `$5214-$524F`) that clears the pending order
        (`STA $650C,Y = 0`).

        **The `$51F4` `[?]` is resolved — D-157 (2026-08-07).** It was read as
        "a different, undecoded outcome," so the one case where a broken crew
        member is standing next to a surfaced Alien was the only case that
        still obeyed orders. Byte-level, `$51F4` is not a branch target that
        goes anywhere else — it is three stores that **fall straight through**
        into `char_wander`::

            51F4  A9 00 / 99 0C 65   STA $650C,Y   ; drop the pending order
            51F9  A9 28 / 99 EE 64   STA $64EE,Y   ; re-arm the 40-tick timer
            51FE  A9 01 / 99 C4 64   STA $64C4,Y   ; mark the move pending
            5203  char_wander:       ...           ; <- no JMP at $5200-$5202

        (`$5200` is a 3-byte `STA abs,Y` ending at `$5202`; `char_wander`
        begins at `$5203`.) So composure 0 wanders **unconditionally** — the
        co-located case just clears the order and resets the cadence first.
        """
        alien = self.state.alien
        if alien is None or not alien.alive:
            return
        for crew in self.state.crew.values():
            if not crew.alive or not crew.awake or crew.in_duct:
                continue                                          # $517A
            if crew.room_id is None:
                continue
            # **[C $5170] D-151** — this gate reads `$6571`, the EFFECTIVE
            # composure (base + companion support), not the bare base.
            composure = self.effective_composure(crew)
            if composure >= constants.PANIC_WANDER_MAX_COMPOSURE:
                continue                                           # $5170
            if not self._turn_due(crew):
                continue  # only on this character's own turn
            alien_surfaced_here = (
                not alien.in_duct
                and alien.room_id is not None
                and crew.room_id == alien.room_id
            )
            if composure == constants.FEAR_MIN:
                pass  # $51E7-$51F4 — every path falls into char_wander (D-157)
            elif not alien_surfaced_here:
                continue  # $5252 — composure 1 wanders only when co-located
            # **[C $5203-$522B] DISC-233 — the order and the turn go FIRST,
            # and unconditionally.** `char_wander` opens with `$5205 STA
            # $650C,Y = 0` (drop the pending order) *before* it rolls, and
            # every arm of the roll converges on `$521B`, which stores the
            # destination, re-arms `$64EE,Y` to 40 (`$5221 LDA #$28`) and sets
            # the move-pending flag. There is no "did the destination change?"
            # test anywhere in it.
            #
            # That matters for a **self-referencing** room. AIRLOCK 1's entries
            # in all three of the bands `_panic_route_band` can reach point
            # back at AIRLOCK 1, so a panicking character there does not move -
            # in the ROM either. But the ROM still drops their order and burns
            # forty passes each time, which is the difference: the remake used
            # to `continue` out and leave both intact, so a panicking crew
            # member in such a room kept obeying orders as if nothing had
            # happened. Standing still is faithful; carrying on is not.
            self._orders = deque(
                o for o in self._orders if o.crew_id != crew.id
            )                                                   # $5205
            crew.step_timer = constants.PANIC_WANDER_TICKS      # $5221
            roll = self.rng.randrange(constants.ALIEN_ROLL_SIDES)
            dest = panic_dest(self.ship, crew.room_id, roll)
            if dest is not None:
                crew.room_id = dest      # $521E — a no-op when it self-refers


    def _pump_characters(self) -> set[str]:
        """`char_pump ($7216)` — **the one and only clock. [C] D-168/PV-34.**

        The ROM keeps exactly one countdown per character, `$64EE,Y`, and
        `char_pump` decrements **every** one of them once per main-loop pass in
        a co-routine loop with `check_deferred_move`::

            7226  LDA $64EE,Y / BNE $722E
            722B  JMP check_deferred_move    ; already 0 -> inert, no turn
            722E  SEC / SBC #$01 / STA $64EE,Y
            7234  BEQ $7239                  ; reached exactly 0 -> resolve
            7239  STY $7214 / JMP resolve_char_move

        Everything that character does hangs off that single expiry: the
        pending order, the panic branch, the android's attack. The remake used
        to run **two** independent clocks — `crew.step_timer`, decremented
        inside `_apply_order`, and a separate turn-timer dict read by a
        `_turn_due` helper — seeded with the same expression and counted down apart,
        so an order and a panic roll could disagree about whose turn it was.

        Returns the ids that came due this pass, in **slot order** (D-166:
        more than one character can resolve in a single pass, and who goes
        first is positional, not fair).
        """
        due: set[str] = set()
        for crew in self.state.crew.values():
            if not crew.alive:
                continue
            if crew.step_timer > 0:
                crew.step_timer -= 1                       # $722E
                if crew.step_timer == 0:
                    due.add(crew.id)                       # $7234 BEQ
            # **A character already at zero is SKIPPED — [C $7226-$722B].**
            #
            #     7226  LDA $64EE,Y
            #     7229  BNE $722E              ; counting -> decrement it
            #     722B  JMP check_deferred_move ; already 0 -> no turn at all
            #
            # so a turn happens only on the pass a countdown *reaches* zero,
            # never while it sits there. An idle crew member with no order does
            # nothing, indefinitely.
            #
            # This used to add them every pass, which gave an idle character a
            # turn ~7.9 times a second. Measured on the running game, the
            # opposite is true: `$6571` never moved for a crew member standing
            # in a room with six companions for 33 s, because nothing recomputed
            # it (DISC-279), and a panicked one never wandered (DISC-281).
            # Derivation: DISCOVERIES DISC-287.
        return due

    def _turn_due(self, crew: CrewMember) -> bool:
        """Did this character's turn come round on this pass? — [C $64EE].

        A pure read of `_pump_characters`' result; the countdown itself lives
        there, so there is exactly one place that decrements.
        """
        return crew.id in self._due

    def _apply_fear_stressors(self) -> None:
        """Raise crew fear from the decoded stressors (DISASSEMBLY §8.9, D-011).

        * **Crowding** — while at least ``CROWD_THRESHOLD`` (3) crew share a room,
          each of them **who is already unnerved** gets ``FEAR_BUMP_CROWDED``
          (the game's ``raise_crowd_fear $4CE8``: "some get nervous when they're
          all in a room at once"). **D-031 (2026-07-24), applied to code:** the
          real routine reads `LDA $7D55,X / BEQ skip` *before* the `INC` — a
          crew member whose fear is currently exactly 0 (calm) is skipped
          entirely. Crowding only amplifies existing unease; it cannot spook a
          calm crew member on its own. This was found while re-examining why
          the live runs never observed a single fear rise despite
          apparently-satisfied crowding: if the tested crew's fear had already
          decayed to 0 by the time crowding was engineered, the real game would
          produce exactly that null result too — a plausible, code-supported
          explanation for the earlier mystery, not just a guess.
        * **Corpse** — a crew member sharing a room with a *dead* crew member gets
          ``FEAR_BUMP_CORPSE`` (the "'S BODY IS HERE" stressor). Whether this one
          shares the same zero-fear skip is unconfirmed (`[?]`, D-031) — the exact
          corpse-discovery `INC $7D55` site couldn't be pinned down separately
          from `raise_crowd_fear` in this pass, so it is still applied
          unconditionally here.

        Fear is clamped to 0..``FEAR_MAX`` by ``CrewMember.bump_fear``.
        """
        by_room: dict[str, list[CrewMember]] = {}
        rooms_with_corpse: set[str] = set()
        for c in self.state.crew.values():
            if c.room_id is None:
                continue
            if c.alive:
                by_room.setdefault(c.room_id, []).append(c)
            else:
                rooms_with_corpse.add(c.room_id)
        for room_id, occupants in by_room.items():
            if len(occupants) >= CROWD_THRESHOLD:
                for c in occupants:
                    if c.fear > 0:  # D-031: raise_crowd_fear skips fear==0
                        c.bump_fear(FEAR_BUMP_CROWDED)
        # **DIRECTION CORRECTED (D-059).** The old rule raised the value by
        # +1 per tick for every crew member sharing a room with a corpse. The
        # value is **composure** (high = calm), and the ROM's death stressor
        # is `$47DC`/`$5A0D`: a one-shot `DEC $7D55,X` looped over **every**
        # crew slot (1..7), floored at 0, fired when a crew member's
        # "just died" flag `$64A9,X` is set — ship-wide, not room-local, and
        # once per death rather than per tick.
        newly_dead = {
            c.id for c in self.state.crew.values() if not c.alive
        } - self._mourned_dead
        if newly_dead:
            self._mourned_dead |= newly_dead
            for c in self.state.crew.values():
                if c.alive:
                    c.bump_fear(constants.COMPOSURE_HIT_CREW_DEATH)

    def _advance_jones(self) -> None:
        """Jones ambles between rooms — **[C $88AB / $8971] D-153/D-156.**

        `char_pump` calls `sub_88ab_prechar` once per main-loop pass, and it
        acts only when its own countdown wraps::

            88B1  DEC $657F / BNE rts        ; only every $657F passes
            88B6  LDA #$28 / STA $657F       ; reload = 40
            88BB  LDA $657E / CMP $7935      ; the CANDIDATE vs the ALIEN's room
            88C1  BEQ rts                    ;   -> veto: he stays put
            88C3  STA $657D                  ; else commit: that is his room
            88C6  JSR guard_6580             ; the notice + the run animation
            88C9  JMP $8971                  ; ...then pick the NEXT candidate

        Two structural details worth keeping. The destination is **chosen one
        step ahead** into `$657E` and only vetoed against the Alien when it is
        *committed*, so a cat heading somewhere the creature then walks into
        simply stalls for a turn. And the pick itself (`$8971`) is **not** a
        uniform choice among door neighbours — it rolls `AND #$07` and reads
        the **same five route tables the Alien uses**, through Jones's own
        band mapping (`alien.jones_dest`). That closes the `[?]` D-036 opened
        and D-153 carried forward.
        """
        if self.state.jones_caught or self.state.jones_room_id is None:
            return
        self._jones_timer -= 1
        if self._jones_timer > 0:
            return
        self._jones_timer = constants.JONES_MOVE_TICKS          # $88B6
        # $8971 picks one move ahead; seed it on the first pass.
        if self._jones_next is None:
            self._jones_next = jones_dest(
                self.ship, self.state.jones_room_id,
                self.rng.randrange(JONES_ROLL_SIDES),
            )
            return
        candidate = self._jones_next
        alien = self.state.alien
        if (
            candidate is None
            or (alien is not None and alien.alive and candidate == alien.room_id)
        ):
            # $88BB-$88C1: he will not walk into the Alien; the move is
            # abandoned and the same candidate is re-tested next pass.
            return
        self.state.jones_room_id = candidate                    # $88C3
        self._jones_next = jones_dest(                          # $88C9 -> $8971
            self.ship, candidate, self.rng.randrange(JONES_ROLL_SIDES)
        )

    def advance(self) -> None:
        """Advance the world by exactly one fixed tick (GAME_SPEC §2).

        No-op once the game has ended. Step order: run the PCS order queue
        (an obeyed ``ATTACK`` may already end the game), move the Alien and Jones, tick the clock, run any auto-destruct countdown (§8),
        and check for a hull breach and an all-crew-dead loss —
        each guarded so an earlier win/loss this same tick is never overwritten.
        """
        if self.state.phase is not GamePhase.RUNNING:
            return

        # Cues are per-tick; the presentation layer drains them after advance().
        self.state.sound_cues.clear()
        # **[C `clear_line_07c0 ($5BE7)`] DISC-231** — the transient row-24
        # banner expires and blanks the row again. The ROM does this at the end
        # of a blocking `delay_long`; the remake counts it down instead.
        if self.state.notice_ticks > 0:
            self.state.notice_ticks -= 1
            if self.state.notice_ticks == 0:
                self.state.notice = None
        # **[C $7216] D-168/PV-34 — `char_pump` first.** One decrement of every
        # character's `$64EE,Y`, before anything reads it, so orders, the panic
        # branch and the android's turn all agree on whose turn this is.
        self._due = self._pump_characters()
        # Snapshot positions so the movement blip can be raised the way the ROM
        # raises it — on a *completed* move (see step 3.8).
        alien0 = self.state.alien.room_id if self.state.alien is not None else None
        crew0 = {c.id: c.room_id for c in self.state.crew.values()}
        jones0 = self.state.jones_room_id

        # 1) Consume queued orders through the PCS gate; ATTACK may end
        #    the game right here (win route 2/3, see _resolve_attack_order).
        self._process_orders()

        # 2) The Alien senses/hunts/moves and may kill an undefended crew
        #    member (GAME_SPEC §11 #2).
        alien_acted = False
        # **Developer mode only** (`core.devtools`). Frozen means "not given its
        # turn", never removed or killed: both of those are win conditions the
        # ROM checks for, so either would end the run being tested. Off by
        # default, so the decoded path below is untouched in a real game.
        if (
            self.state.phase is GamePhase.RUNNING
            and self.state.alien is not None
            and self.dev.alien_may_act()
        ):
            before = self.state.alien.timer
            advance_alien(
                self.ship, self.state, self.state.alien, self.rng,
                corrode_rate=(
                    constants.UPDATED_ALIEN_CORRODE_RATE
                    if self.weapon_breach_gates
                    else constants.ALIEN_CORRODE_RATE
                ),
            )
            # `advance_alien` reloads the timer on the tick it acts (D-100's
            # one-pass model), so a timer that did not simply decrease is a turn.
            alien_acted = self.state.alien.timer >= before

        # 2.5) [C $7302 -> $59A7] P2-17: a body the Alien is carrying is
        #      dropped into the ducting once the Alien is inside it.
        if self.state.phase is GamePhase.RUNNING and self.state.alien is not None:
            restore_stowed_char(self.state, self.state.alien)

        # 3) Jones wanders on his own (GAME_SPEC §8).
        if self.state.phase is GamePhase.RUNNING and self.dev.jones_may_act():
            self._advance_jones()

        # 3.5) PCS fear stressors from crowding / corpses (D-011). Run after the
        #      Alien may have killed someone, so a fresh corpse frightens at once.
        # [C $4CC3] `raise_crowd_fear` runs once per ALIEN turn, not per tick.
        if self.state.phase is GamePhase.RUNNING and alien_acted:
            self._apply_fear_stressors()

        # 3.6) Panic-wander (FV-2.11 / D-043, `char_wander $5203`): crew sharing
        #      a room with the surfaced Alien bolt instead of obeying. After the
        #      Alien has moved and after its encounter/wound resolution, so a
        #      crew member it just walked in on reacts on the same tick.
        # [C $5203] `char_wander` is likewise a character-turn action.
        if self.state.phase is GamePhase.RUNNING:
            self._apply_panic_wander()

        # 3.7) The android turns on the crew (D-080, `$5439`). After the Alien
        #      and the panic pass, so a crew member driven into its room by
        #      either is attacked on the same tick.
        # [C $52F1] The android attacks on **its own turn, and only once it has
        # been found out**. `$5265` routes the android's turn on `$64CC`:
        # `$526D BEQ $5272` takes the *unrevealed* android down the ordinary
        # `dispatch_char_action` road (it obeys orders and passes for crew),
        # while `$526F JMP $52F1` — the revealed path — is the only route into
        # the co-located-crew scan that ends in the attack at `$5345`.
        # Attacking from tick 0 was an invention, and the dominant cause of the
        # player's "the crew all became gradually uncontrollable": the android
        # ground its roommate down to health < 2 in the first two minutes.
        if self.state.phase is GamePhase.RUNNING:
            android = self.state.crew.get(self.state.android_id or "")
            if (
                android is not None
                and self.state.android_revealed
                and self._turn_due(android)
            ):
                self._apply_android_attack()
            self._reveal_android()

        # 3.8) The movement blip. **[C $8C80]** `reset_attack_state` is called
        #      from the two movement paths (`$72F9`, `$7E5A`) and always plays
        #      one of the two voice-2 noise blips: `sfx_blip_a` (deep, freq
        #      `$0100`) if the grille-burst flag `$651B` is set, else
        #      `sfx_blip_b` (bright, freq `$5000`) — and it clears the flag, so
        #      the grille sound happens once per burst (D-088). Both are muted
        #      while an attack sequence runs; that guard is `sound.audible`.
        if self.state.phase is GamePhase.RUNNING:
            alien = self.state.alien
            burst = alien is not None and alien.burst_grille_room is not None
            crew_moved = any(
                c.room_id != crew0.get(c.id) for c in self.state.crew.values()
            )
            alien_moved = alien is not None and alien.room_id != alien0
            jones_moved = self.state.jones_room_id != jones0
            moved = burst or alien_moved or crew_moved
            if moved:
                self.state.sound_cues.append(SoundCue(GRILLE if burst else MOVEMENT))
            # **[C $72F9/$72FC] D-150 — the alarm is a LATCH, recomputed.**
            # `reset_attack_state ($8C80)` clears `$64B6` and `check_6562
            # ($8E32)` re-arms it, back to back on every move pass, gated
            # only on `$6517` (any character's move resolved) — never on a
            # USE order (D-129). So the right model is "recompute from
            # scratch", not "fire an event": `_scan_trackers` re-arms only
            # while a tracker is genuinely HELD and something is in its
            # zone, which is what makes putting the tracker down silence it.
            # The ping itself is a continuously-running IRQ pulse whose rate
            # is fixed (`$4D03` = 18 IRQ ticks, `sfx.TRACKER_DIVIDER`), so
            # no per-detection sound cue is raised here — the renderer loops
            # the pulse while the latch is set, exactly as it does the
            # heartbeat. Pushing a fresh one-shot clip per detection is what
            # made the pings machine-gun.
            self._scan_trackers()
            # **[C $7305] D-155** — `check_deferred_move` calls
            # `apply_blowlock` on every move pass, so an open airlock vents
            # CONTINUOUSLY: walk into one later and it still kills you. We
            # used to vent once, at the moment of opening.
            self._vent_open_airlocks()
            if alien is not None:
                alien.burst_grille_room = None  # `$8C8F STA $651B` clears it

        # 3.9) **[C $5684] P2-18 — an unfought engine fire burns.**
        #      `mainloop_sub_5684` does `INC $64CE / BNE rts`, so it acts once
        #      every 256 passes, then walks the three fire rooms and adds a
        #      point of damage to any whose alarm is still lit.
        if (
            self.state.phase is GamePhase.RUNNING
            and self.state.tick % constants.FIRE_SPREAD_EVERY_TICKS == 0
        ):
            for index in constants.FIRE_ROOM_INDICES:
                room = gamedata_snapshot.ROOM_SLUGS[index]
                if self.state.room_alarm.get(room):
                    add_room_damage(self.state, room, 1)

        # 4) Advance the real-time clock.
        self.state.tick += 1

        # 5) (Oxygen/TOOH used to drain here and end the game at zero. Removed
        #    2026-08-01 — FV-2.5 / D-062: the C64 game has NO oxygen system, so
        #    this was a pure invention that lost every run after ~7500 ticks.
        #    See the evidence block in `constants.py`. There is no global time
        #    limit; the only clock that can end a game is the player's own
        #    auto-destruct, next.)

        # 6) Auto-destruct (GAME_SPEC §8): reaching zero destroys the ship
        #    with anyone still aboard.
        if self.state.phase is GamePhase.RUNNING and self.state.auto_destruct_ticks is not None:
            self.state.auto_destruct_ticks -= 1
            if self.state.auto_destruct_ticks <= 0:
                # [C $5A43 `JMP hull_breach`] DISC-234 — the countdown running
                # out runs the same destruction sequence a breach does, so it
                # goes through the same handler (DISC-258).
                self._hull_breach()

        # 7) Hull breach — **an EQUALITY, not a threshold (DISC-204)**::
        #
        #        5658  CMP #$14        ; exactly 20?
        #        565A  BNE $565F       ; no  -> just latch alarm stage 2
        #        565C  JMP hull_breach ; yes -> the ship is destroyed
        #
        #    A room pushed *past* 20 never breaches. It latches critical
        #    (`$651C,X` = 2) and is then permanently safe, because the counter
        #    only ever climbs and can never equal 20 again.
        #
        #    That is a real mechanic, not an oversight: a big weapon hit
        #    (harpoon +15) can deliberately "burn out" a room, after which it is
        #    safe to keep fighting in. Using `>=` here made every room that
        #    crossed 20 fatal and turned a tactical option into a death
        #    sentence — see `tests/test_winnability.py`.
        if self.state.phase is GamePhase.RUNNING and any(
            d == HULL_BREACH_THRESHOLD for d in self.state.room_damage.values()
        ):
            self._hull_breach()                  # $565C JMP hull_breach

        # 8) **[C $5B56-$5B7E] P2-20 — "is anyone still in play?", read in full.**
        #    This used to be a plain all-crew-dead check. The ROM's scan is a
        #    good deal stricter, and a crew member only counts if **every** one
        #    of these holds:
        #
        #      `$5B5B CMP #$02 / BCC next`  health **>= 2** — someone COLLAPSED
        #                                   on 1 health does not count
        #      `$5B5F/$5B64`                not a **revealed android** (D-084)
        #      `$5B6C BEQ next`             composure `$7D55,Y` **> 0** — nobody
        #                                   who is BROKEN counts either
        #      `$5B7C BNE next`             not in **hypersleep** (`$64D1,Y`)
        #
        #    If nobody qualifies, `$5B76 JMP endgame_dispatch` ends the game.
        #    So a ship where everyone is collapsed, broken or asleep is lost
        #    just as surely as one where everyone is dead — which is a real
        #    part of why the PCS matters.
        if self.state.phase is GamePhase.RUNNING and not any(
            self._counts_as_in_play(c) for c in self.state.crew.values()
        ):
            self.state.phase = GamePhase.LOST

    def _hull_breach(self) -> None:
        """`hull_breach ($5D17)` — **the ship goes, and it takes the crew.**

        Four sites jump here: two weapon hits (`$4A91`/`$4AFA`), the room-damage
        equality (`$565C`) and the auto-destruct running out (`$5A43`). The
        remake reached the same *flags* from two of them and stopped there,
        which is not what the routine does. Its tail is unambiguous::

            5DB5  LDY #$01
            5DB7  LDA #$01
            5DB9  STA $7D45,Y     ; every crew member's health -> 1
            5DBC  INY / CPY #$08 / BNE
            5DC1  LDA #$64
            5DC3  STA $7D45       ; the ALIEN's health -> 100
            5DC6  LDA #$01 / STA $64CF   ; the ship is destroyed
            5DCB  STA $657B
            5DCE  JMP endgame_dispatch

        **Health 1 is below the acting threshold** (`$52C0 CMP #$02 / BCS`, and
        `HEALTH_WOUNDED_AT_LEAST`), so the whole crew is incapacitated — they
        are not survivors. Without this the ending counted six of them as
        having come through a hull breach unharmed, and with the android alive
        it reported the Nostromo brought safely home. A player reported exactly
        that: "Parker returned the ship safely to earth" after an attack
        destroyed it (DISC-258).

        The Alien going to 100 is the same statement from the other side: the
        creature is emphatically not killed by the ship breaking up.
        """
        for crew in self.state.crew.values():         # $5DB9
            if crew.alive:
                crew.health = 1
        # `$5DC1 LDA #$64 / STA $7D45` puts the Alien's own cell to 100. The
        # remake models that cell as accumulated *wounds* counting up to
        # `ALIEN_DAMAGE_TO_KILL`, so the faithful statement of "emphatically not
        # killed by the ship breaking up" is zero wounds, not the literal 100.
        if self.state.alien is not None:              # $5DC1
            self.state.alien.damage = 0
        self.state.ship_destructing = True            # $5DC6
        self.state.ship_destroyed = True
        self.state.phase = GamePhase.LOST             # $5DCE endgame_dispatch

    def _counts_as_in_play(self, crew: CrewMember) -> bool:
        """Does this crew member keep the game alive? — [C $5B56-$5B7E]."""
        if not crew.alive or crew.health < constants.CREW_INCAPACITATED_BELOW:
            return False                       # `$5B5B CMP #$02 / BCC`
        if crew.id == self.state.android_id and self.state.android_revealed:
            return False                       # `$5B5F`/`$5B64`
        if crew.fear <= 0:
            return False                       # `$5B6C LDA $7D55,Y / BEQ`
        if not crew.awake:
            return False                       # `$5B7C LDA $64D1,Y / BNE`
        return True









    def run(self, ticks: int) -> None:
        """Advance up to ``ticks`` fixed ticks, stopping early if the game ends."""
        for _ in range(ticks):
            if self.state.phase is not GamePhase.RUNNING:
                break
            self.advance()
