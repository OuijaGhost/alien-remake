"""The SPECIAL panel: ship-wide actions, as opposed to per-crew orders.

Split out of `sim.py` (DISC-196). These are the options `$57B6` lists —
BLOWLOCK, SEALLOCK, FIGHT FIRE, LAUNCH NARCISSUS, ENTER HYPERSLEEP, OVERRIDE
DETONATION, GET JONES — and they differ from orders in three ways that matter:

- they take effect **immediately**, not on the actor's next turn;
- most are gated by *where the selected character is*: `_can_use_specials` reads
  the per-room table `$5753`, so an option offered in one room is absent in the
  next;
- several are irreversible and end the game (LAUNCH NARCISSUS; BLOWLOCK with the
  Alien aboard).

Because they apply during input handling rather than on the tick, any sound they
raise must be drained before the next `advance()` clears the queue — see
`app.run_app` and `tests/test_integration_loop.py`.
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
    DeathVariant, GameMode, JonesCatch, choose_android, choose_opening_death,
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
from ..state import GamePhase, GameState, WinRoute
from .protocol import SimulationState


class SpecialsMixin(SimulationState):
    """`Simulation`'s Special Options. Mixed in by `sim/__init__.py`."""

    def _can_use_specials(self, crew_id: str | None) -> bool:
        """The specials dispatcher's own two gates — **[C $583F] PV-04/D-163.**

        `$5839`, the routine `route_command` hands every panel row `>= $10` to,
        refuses **before** dispatching on the option code::

            583F  LDY $64FB
            5842  LDA $6571,Y / BEQ $5888   ; effective composure 0 -> nothing
            5847  LDA $7D45,Y / CMP #$02
            584C  BCC $5888                 ; health below 2 -> nothing

        Note this is the *handler*, not the draw: `guard_target_alive ($56B4)`
        still puts the row on the panel. So a broken crew member sees the
        option and pressing it does nothing — the same shape as GET JONES
        (D-160) and the airlock vent.

        The composure test matters because it has **no companion escape**.
        `guard_alien_present ($7757/$7768)` lets you *select* a broken crew
        member so long as somebody functional is with them; `$5842` does not,
        so an accompanied but broken crew member can still take ordinary
        orders and yet cannot work a single Special Option. That asymmetry was
        not modelled.
        """
        if crew_id is None:
            return True          # ship-level options carry no acting character
        crew = self.state.crew.get(crew_id)
        if crew is None:
            return True
        if crew.health < constants.CREW_INCAPACITATED_BELOW:      # $5847
            return False
        return self.effective_composure(crew) != 0                # $5842
    def apply_special_option(self, option: SpecialOption) -> bool:
        """Apply one Special Option (the game's `$57A0` menu, 1:1); True if it
        took effect. These are direct ship/player actions, not per-crew orders.
        (EXIT_HYPERSLEEP and CATCH_JONES were removed — neither exists in the
        game's specials menu; Jones is caught via USE of the CAT BOX item.)
        """
        if self.state.phase is not GamePhase.RUNNING:
            return False
        if not self._can_use_specials(option.crew_id):
            return False
        t = option.type

        if t is SpecialOptionType.OPEN_AIRLOCK:
            return self._open_airlock(option.room_id)
        if t is SpecialOptionType.SEAL_AIRLOCK:
            if option.room_id is None or option.room_id not in self.ship.airlock_rooms():
                return False
            self.state.airlocks_open[option.room_id] = False
            # **[C $5904] D-186 - sealing makes the same noise as blowing.**
            # BLOWLOCK and SEALLOCK are the same option code (2) reaching the
            # same routine, and `blowlock_sfx` plays its hiss at `$5904`-`$5915`
            # *before* `$591F`/`$592E` even look at which way the flag is about
            # to flip. The sound is unconditional on the direction; only the
            # remake's OPEN path was raising it.
            self.state.sound_cues.append(SoundCue(AIRLOCK))
            return True
        if t is SpecialOptionType.LAUNCH_NARCISSUS:
            return self._launch_narcissus()
        if t is SpecialOptionType.ENTER_HYPERSLEEP:
            # [C $593C] D-080: `guard_target_is_player` RTSes immediately when
            # the commanded character is the android — it cannot go under.
            if option.crew_id is not None and option.crew_id == self.state.android_id:
                return False
            return self._set_hypersleep(option.crew_id, awake=False)
        if t is SpecialOptionType.INITIATE_AUTO_DESTRUCT:
            if self.state.auto_destruct_ticks is not None:
                return False
            self.state.auto_destruct_ticks = AUTO_DESTRUCT_TICKS
            # [C $58E5 `set_result_win`] DISC-230 — arming SCUTTLE raises the
            # `$64CF` "the ship is going to be destroyed" flag the ending reads.
            self.state.ship_destructing = True
            return True
        if t is SpecialOptionType.OVERRIDE_DETONATION:
            # [C-live FV-2c]: cancels an armed countdown (confirmed live — firing
            # SCUTTLE NOSTROMO makes an OVERRIDE DETONATION entry appear on the
            # crew menu; only valid while armed).
            # **[C $585E] R-28b/D-060: the override EXPIRES.** The ROM gates it
            # on `LDA $657B / CMP #$05 / BCC skip` — you may only cancel while
            # at least 5 of the 9 countdown units remain. Past that the
            # detonation is irreversible.
            if self.state.auto_destruct_ticks is None:
                return False
            if self.state.auto_destruct_minutes_left < AUTO_DESTRUCT_OVERRIDE_ABOVE:
                return False
            self.state.auto_destruct_ticks = None
            # [C $58F6 `clear_result_flag`] the override zeroes `$64CF` too.
            self.state.ship_destructing = False
            return True
        if t is SpecialOptionType.FIGHT_FIRE:
            return self._fight_fire(option.crew_id)
        raise AssertionError(f"unhandled special option: {t}")  # pragma: no cover
    def _post_notice(self, text: str) -> None:
        """Show a transient row-24 banner — **[C $07C0 + `delay_long`].**

        The ROM writes the message, blocks in `delay_long ($561C)`, then blanks
        the row and restores the border. `delay` itself blacks the border
        (`$5626-$5628`), which is the visible "freeze" that goes with these.
        """
        self.state.notice = text
        self.state.notice_ticks = constants.NOTICE_TICKS

    def _fight_fire(self, crew_id: str | None) -> bool:
        """FIGHT FIRE (`$5889`) — **[C, D-066 2026-08-01]**, traced in full.

        The ROM handler, instruction for instruction::

            5889  LDY $64FB            ; the commanded character
            588C  JSR find_room_object ; an object in that character's room
            588F  TYA
            5890  CMP #$08 / BCC rts   ; gate: object index must be
            5894  CMP #$0B / BCS rts   ;   8, 9 or 10 (the extinguisher band)
            5898  TAX
            5899  LDA $4B37,X          ; its remaining charge
            589C  BNE spend
            589E  ; charge 0 -> print "EXTINGUISHER IS EMPTY" ($4B5A) and RTS
            58AC  spend: DEC $4B37,X   ; consume one charge
            58AF  ; SID: the extinguisher hiss
            58C6  LDA $7935,Y / TAX    ; X = the character's ROOM
            58CC  STA $651C,X          ; clear the room's damage-ALARM latch
            58CF  STA $5753,X          ; clear a second per-room flag
            58D2  STA $64D0            ; clear a global flag
            58D5  ; show "FIRE OUT  " ($5950)

        Two things this pins down:

        * It **never touches `$653F`** (structural damage) — confirming D-044:
          accumulated damage is permanent and the extinguisher only *silences*
          the alarm, which will return on the next damage tick.
        * An **empty** extinguisher fails outright: the message prints and the
          alarm is NOT cleared. The remake previously spent the charge and
          cleared regardless.

        **PV-17 closed 2026-08-07 (D-163) — both cells are now traced.**
        `$5753,X` is the **per-room SPECIAL-OPTION code table**, not a bare
        fire flag: `guard_target_alive ($56C1)` reads it by the acting
        character's room and caches it in **`$64D0`**, which is simply *which
        option is selected*; the dispatcher `$5839` then branches on it
        (1 = SCUTTLE/OVERRIDE, 2 = BLOWLOCK, 3 = HYPERSLEEP, 5 = LAUNCH,
        anything else -> `$5889`, this handler). So clearing `$5753,X` and
        `$64D0` is exactly "FIGHT FIRE is no longer offered here", which the
        remake already expresses by dropping the alarm — the menu derives the
        row from `room_alarm` rather than mirroring the byte. Nothing further
        to model.
        """
        if crew_id is None or crew_id not in self.state.crew:
            return False
        crew = self.state.crew[crew_id]
        if not crew.alive:
            return False
        room_id = crew.room_id
        if room_id is None:
            return False
        # `find_room_object` looks in the acting character's ROOM, so a
        # extinguisher lying on the floor counts, not just a carried one.
        item = next(
            (
                i for i in self.state.items.values()
                if i.type_id == "fire_extng"
                and (i.room_id == room_id or i.holder == crew_id)
            ),
            None,
        )
        if item is None:
            return False
        if item.uses_left is not None and item.uses_left <= 0:
            return False          # "…EXTINGUISHER IS EMPTY" — no effect
        if item.uses_left is not None:
            item.uses_left -= 1
        self.state.room_alarm.pop(room_id, None)
        self.state.room_fire.pop(room_id, None)   # $58CF STA $5753,X
        self._post_notice(constants.NOTICE_FIRE_OUT)   # $58D5 -> $5950
        return True
    def _open_airlock(self, room_id: str | None) -> bool:
        """BLOWLOCK — **[C $591F/$5B04] D-155.** Opens the lock and vents it.

        Both locks are simple **toggles** (`$5922`/`$5931 EOR #$01`);
        BLOWLOCK and SEALLOCK are the same option flipping one flag. Opening
        does not vent once and finish: `apply_blowlock` is called from
        `check_deferred_move ($7305)` on **every move pass**, so an open lock
        keeps venting and anyone who walks in later dies too. That continuous
        part is `_vent_open_airlocks`, run each tick.
        """
        if room_id is None or room_id not in self.ship.airlock_rooms():
            return False
        self.state.airlocks_open[room_id] = True
        # [C $586D] D-088: the blow-lock path calls `blowlock_sfx ($5904)`
        # before applying the vent — a noise crack with no mute guard.
        self.state.sound_cues.append(SoundCue(AIRLOCK))
        self._vent_open_airlocks()
        return True
    def _vent_open_airlocks(self) -> None:
        """Vent every open airlock — **[C $5A6A `blowlock_vent`] D-155.**

        Four separate effects, three of which the remake was missing::

            5A6C  LDA $82E3,Y / CMP $5AD7      ; items lying in the room...
            5A74  LDA #$BD / STA $82E3,Y       ;   -> blown into space
            5A80  LDA $6501,Y / BNE next       ; crew in a DUCT are SAFE
            5A8D  LDA #$00 / STA $7D45,Y       ; ...otherwise killed
            5A92  LDA #$BD / STA $7935,Y       ;   and blown out
            5A9E  ...items held by them -> $BD ;   with everything they carried
            5ABF  LDA $6501 / BNE rts          ; a ducted Alien is SAFE
            5ACC  LDA $7D45 / CMP #$06 / BCC rts  ; **damage < 6 -> untouched**
            5AD3  JSR alien_maybe_hide         ; else roll for it

        The Alien gate is the big one: a **healthy Alien simply ignores an
        open airlock**. Only once it has taken 6+ damage can the vent reach
        it, and even then `alien_maybe_hide ($5ADD)` rolls — `rng >= damage`
        and it survives with +1 damage and a long delay; otherwise it goes
        out. So the lock is a finisher for a wounded creature, not the
        instant kill the remake made it.

        **Jones is untouched** — `$657D` is never referenced by the vent.
        """
        for room_id, is_open in list(self.state.airlocks_open.items()):
            if not is_open:
                continue

            # $5A6C: anything lying in the room goes to space.
            for item_id, item in list(self.state.items.items()):
                if item.room_id == room_id:
                    del self.state.items[item_id]

            # $5A7E-$5ABD: crew on the surface here are killed and blown out,
            # taking whatever they carried with them.
            for crew in self.state.crew.values():
                if not crew.alive or crew.room_id != room_id:
                    continue
                if crew.in_duct:
                    continue                                   # $5A80: safe
                crew.health = 0                                # $5A8D
                crew.alive = False
                for item_id in list(crew.carried):             # $5A9E
                    self.state.items.pop(item_id, None)
                crew.carried.clear()

            # $5ABF-$5AD3: the Alien, only if surfaced here AND already hurt.
            alien = self.state.alien
            if (
                alien is None
                or not alien.alive
                or alien.room_id != room_id
                or getattr(alien, "in_duct", False)            # $5ABF
                or alien.damage < constants.ALIEN_VENT_MIN_DAMAGE   # $5ACF
            ):
                continue
            roll = self.rng.randrange(constants.ALIEN_VENT_ROLL_SIDES)
            if roll >= alien.damage:                           # $5AE0 BCS
                # **[C $5AEE-$5B00] PV-16 — surviving the vent THROWS it.**
                # The remake only added the damage point and left the creature
                # standing in the lock, so a survived vent changed nothing you
                # could see. The ROM does four things::
                #
                #     5AEE  JSR rng / LSR / LSR / STA $64E6  ; dest = roll >> 2
                #     5AF6  LDA #$78 / STA $64EE             ; 120-pass stun
                #     5AFB  LDA #$00 / STA $6501             ; forced to the SURFACE
                #     5B00  INC $7D45                        ; +1 damage
                #
                # `rng` is a flat 0-15, so `>> 2` is **rooms 0-3** — AIRLOCK 1,
                # AIRLOCK 2, the ARMOURY and CARGOPOD 1. Half of those put it
                # straight back in a lock, which is why blowing one repeatedly
                # is a real tactic rather than a single wasted chance.
                alien.damage += constants.ALIEN_VENT_SURVIVE_DAMAGE
                throw = self.rng.randrange(constants.ALIEN_VENT_ROLL_SIDES) >> 2
                dest = gamedata_snapshot.ROOM_SLUGS[throw]
                if dest in self.ship.rooms:
                    alien.room_id = dest                       # $5AEE
                alien.dest_id = None
                alien.in_duct = False                          # $5AFB
                alien.timer = constants.ALIEN_VENT_STUN_TICKS  # $5AF6
                continue
            alien.alive = False                                # $5AE5: gone
            self.state.win_route = WinRoute.ALIEN_AIRLOCKED
            self.state.phase = GamePhase.WON
    def _launch_narcissus(self) -> bool:
        """Win route 1 (LAUNCH NARCISSUS), corrected against the full disassembly.

        The decoded launch validator (`$5B95` → the `$5B9E` loop + `check_mother_
        refuses $5B1F`) refuses the launch unless BOTH:

        * **every alive crew member is aboard** the Narcissus (location `$22` =
          the SHUTTLEBAY / evac bay) — else "MOTHER REFUSES LAUNCH" (`$5B80`); and
        * **Jones has been caught** (the CAT BOX is aboard, `$7CC3`) — else
          "GO GET JONES" (`$5C33`).

        (The effective survivor cap is emergent: the evac room's occupancy limit
        (`ROOM_CAPACITY`) bounds how many can be aboard at once, so with more
        alive crew than fit, they can't all board and the launch stays refused —
        matching the user's "escape pod max occupancy" observation.)
        """
        evac = self.ship.evac_rooms()
        survivors = [c for c in self.state.crew.values() if c.alive]
        if not evac or not survivors:
            return False
        # MOTHER REFUSES LAUNCH: not every survivor is aboard.
        # **[C $5BD3-$5BD8] D-152 — the android is skipped UNLESS revealed.**
        # `CPY $64C3 / BNE $5BDD` then `LDA $64CC / BEQ $5BCB`: a crew member
        # who is the android and is NOT yet found out is passed over by the
        # left-behind scan entirely, so it never blocks the evacuation. Once
        # revealed it counts like anyone else and must be aboard. You can
        # therefore leave the thing on the ship without knowing it — which is
        # rather the point of not knowing which of them it is.
        def blocks_launch(c: CrewMember) -> bool:
            if c.id == self.state.android_id and not self.state.android_revealed:
                return False                      # $5BD8
            return c.room_id not in evac
        if any(blocks_launch(c) for c in survivors):
            self._post_notice(constants.NOTICE_MOTHER_REFUSES)   # $5B80
            return False
        # **[C $5B1F check_mother_refuses] D-153 — "GO GET JONES" is about the
        # CONTAINER's location, not a boolean.** The routine finds whichever
        # item was renamed to hold the cat, reads its location byte, and
        # allows the launch only if it is `$22` (the NARCISSUS) or is carried
        # by a character who is themselves in the NARCISSUS::
        #
        #     5B3B  LDA $82E3,Y / CMP #$22 / BEQ allow   ; the box is aboard
        #     5B42  CMP #$80 / BCC refuse                ; ...lying in a room
        #     5B46  AND #$07 / TAY / LDA $7935,Y
        #     5B4C  CMP #$22 / BNE refuse                ; ...holder aboard?
        #
        # So catching him is only half of it: somebody has to actually carry
        # the net or box into the shuttle. We used to accept a bare
        # `jones_caught`, which let you launch with the cat still on the ship.
        if not self.state.jones_caught:
            self._post_notice(constants.NOTICE_GO_GET_JONES)     # $5C33
            return False
        container = (
            self.state.items.get(self.state.jones_container_id)
            if self.state.jones_container_id is not None else None
        )
        if container is not None:
            if container.room_id is not None:
                if container.room_id not in evac:            # $5B3E/$5B42
                    return False
            else:
                holder = (
                    self.state.crew.get(container.holder)
                    if container.holder is not None else None
                )
                if holder is None or holder.room_id not in evac:   # $5B4C
                    return False
        # [C $95B7, reached via `$5C18 JSR play_note_b`] DISC-230 — the launch
        # raises `$64E3`; the ending screen and the hull-breach path both read
        # it to tell "aboard the shuttle" from "left on the ship".
        self.state.narcissus_launched = True
        self.state.win_route = WinRoute.EVACUATED
        self.state.phase = GamePhase.WON
        return True
    def _set_hypersleep(self, crew_id: str | None, *, awake: bool) -> bool:
        """Toggle one crew member's hypersleep state.

        [C-live/FV-2.9, D-028, 2026-07-11]: the real handler
        (`$5939`, previously mislabeled `guard_target_is_player`) is
        room-gated to the CRYO VAULT (`menu.py` enforces this on the
        selectable side; re-checked here too) and self-target only. On entry
        it sets a per-crew asleep flag and moves the crew member's location
        to a sentinel value, **removing them from the room grid entirely** —
        modelled here as `room_id = None`. This has a real, faithful side
        effect for free: every Alien-encounter check elsewhere compares
        `crew.room_id == alien.room_id`, which can never match `None`, so a
        sleeping crew member is naturally unreachable by the Alien, matching
        the ROM's behaviour without a bespoke "is protected" flag. There is
        no EXIT HYPERSLEEP in the game's menu (D-018), so this is one-way in
        practice; the ``awake=True`` branch is kept for symmetry/tests only.
        ``awake_crew`` is kept in lockstep but drives nothing — the oxygen
        model it once fed was removed outright (FV-2.5 / D-062).
        """
        if crew_id is None:
            return False
        crew = self.state.crew.get(crew_id)
        if crew is None or not crew.alive or crew.awake == awake:
            return False
        if not awake and crew.room_id != "cryo_vault":
            return False
        crew.awake = awake
        if not awake:
            crew.room_id = None
        self.state.awake_crew = max(0, self.state.awake_crew + (1 if awake else -1))
        return True
    def _catch_jones(self, crew_id: str | None) -> bool:
        """Try to catch Jones — **[C $8787-$880E] D-153: it is a ROLL.**

        The remake treated this as automatic with the cat box. The ROM does
        rather more::

            8791  LDY $64FB / LDA $883C,Y / STA $6518  ; per-character threshold
            879A  LDA $829A / CMP #$10 / BNE $87C9     ; holding the NET?
            87A1  DEC $6518 x4                         ;   -> 4 better odds
            87AD  JSR rng / CMP $6518 / BCS success    ; roll >= threshold?
            87C9  CMP #$11 / BEQ ...                   ; else the CAT BOX
            87B6  copy "Jones:Net" / 87D7 "Jones:Box"  ; rename the container
            87EE  LDA #$00 / STA $6580                 ; he is no longer loose

        So: **the NET catches him too** (and markedly better — the roll table
        is a flat 0-15, and the thresholds are 13-15, so the box alone is a
        1-in-16 to 3-in-16 shot while the net is 5-to-7), the odds are
        **per character** (`$883C`, decoded into
        `constants.JONES_CATCH_THRESHOLD`), and a failed attempt simply does
        nothing — you try again. The catching item is **renamed** to hold
        him, which is what `check_mother_refuses` later looks for; we record
        it as `state.jones_container_id`.
        """
        if crew_id is None or self.state.jones_caught:
            return False
        if self.state.jones_room_id is None:
            return False
        # **[C $878C `LDA #$01 / STA $657F`] D-160 — the grab spooks him.**
        # Before rolling anything, the handler slams Jones's move counter down
        # to 1, so he steps on the very next pass whether you catch him or
        # not. A missed grab does not simply cost you the attempt: the cat
        # bolts, and you have to find him again.
        #
        # `JonesCatch.PATIENT` (the default, DISC-262) skips that. The roll
        # below is untouched — only the number of attempts you get changes, not
        # their odds. With the box at 6-19% the ROM's behaviour is one shot per
        # encounter, which the owner reported as far harder than they remember.
        if self.jones_catch is JonesCatch.CLASSIC:
            self._jones_timer = 1
        crew = self.state.crew.get(crew_id)
        if crew is None or not crew.alive or crew.room_id != self.state.jones_room_id:
            return False
        item = self.state.items.get(crew.holding) if crew.holding is not None else None
        if item is None or item.type_id not in constants.JONES_CATCHERS:
            return False                              # $879A/$87C9: neither
        # `LDY $64FB` — the same slot register `_slot_of` already decodes for
        # every other per-character table ($4032, $403A). This used to
        # reimplement it as `list(self.state.crew).index(crew_id) + 1`, which
        # happens to agree today because `default_crew` builds the dict in
        # `CREW_NAMES` order, but that agreement isn't guaranteed by anything —
        # `_slot_of` is the one place this lookup is supposed to live.
        slot = self._slot_of(crew)
        if slot == 0:
            return False
        thresholds = constants.JONES_CATCH_THRESHOLD
        threshold = thresholds[slot] if slot < len(thresholds) else thresholds[-1]
        if item.type_id == "net" or self.jones_catch is JonesCatch.EASY:
            # $87A1-$87AA for the net. **`EASY` extends the same four points to
            # the cat box** — an added rule, not the ROM (DISC-269), and sized
            # deliberately to a step the ROM itself takes rather than to a
            # number picked to feel right. The per-character table underneath is
            # untouched, so Ripley/Ash/Lambert stay the best at this and Parker
            # stays the worst.
            threshold -= constants.JONES_CATCH_NET_BONUS
        roll = self.rng.randrange(constants.JONES_CATCH_ROLL_SIDES)
        if roll < threshold:                                       # $87B0 BCS
            return False                      # a miss: try again, nothing lost
        self.state.jones_caught = True                             # $87EE
        self.state.jones_container_id = item.id       # $87B6/$87D7: the rename
        self.state.jones_room_id = None
        return True
