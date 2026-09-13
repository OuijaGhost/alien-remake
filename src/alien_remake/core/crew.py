"""The Nostromo crew and the Personality Control System state.

Seven crew (plus the cat Jones) each have a **role** and a hidden
**state of mind** ("fear", 0..255) — the heart of the Personality Control System
(GAME_SPEC §5): Mother reports it qualitatively, and it raises the tempo of a
crew member's own actions and can trigger a panic random-walk, but — corrected,
`core.orders`' own note — it never gates whether an *order* is obeyed: the
decoded program has no compliance roll at all (D-018/D-026). This module is
pure data + the fear→behaviour curve; order *resolution* lives in
:mod:`alien_remake.core.orders` and application in :mod:`alien_remake.core.sim`.

The roster and its on-screen order are verified against the game's own CONTROL
panel (``docs/reference/opening scenario 2.png``): Dallas, Kane, Ripley, Ash,
Lambert, Parker, Brett. The name→role pairing is the film's canon (GAME_SPEC §4
[I]); the Report Monitor is the place to correct it if the game differs.

**Stale `[?]` removed 2026-09-05 (P9-B goal session):** this docstring used to
close with "Numeric fear ranges / obey curve are calibration `[?]` (GAME_SPEC
§11 #1)". There is no obey curve — D-018/D-026 traced the order path and found
no compliance roll anywhere on it, so "calibrating" one was never a live
question — and the morale word banding (`morale_word`, `$7DC5 fear_band`) has
been fully decoded and live-confirmed since D-024/FV-2g (2026-07-11). Neither
half of this note was still open; it was never updated when both closed.
"""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from enum import Enum

from . import constants
from .gamedata_snapshot import STATUS_WORDS
from .map import ShipMap


class Role(Enum):
    """A crew member's shipboard role.

    [?] COSMETIC / film-canon (GAME_SPEC §4, tagged [I]). The decoded game stores
    the crew *names* (`gamedata_snapshot.CREW_NAMES`) but no role/rank table was
    found — roles are the film's canon, used only for display and never gating
    behaviour. Confirm against the manual/CONTROL panel or drop; does not affect
    1:1 gameplay fidelity. See docs/re/FAITHFULNESS.md.
    """

    CAPTAIN = "Captain"
    EXECUTIVE_OFFICER = "Executive Officer"
    WARRANT_OFFICER = "Warrant Officer"
    NAVIGATOR = "Navigator"
    SCIENCE_OFFICER = "Science Officer"
    CHIEF_ENGINEER = "Chief Engineer"
    ENGINEERING_TECHNICIAN = "Engineering Technician"


# Canonical roster, in the game's CONTROL-panel order (see module docstring).
# (crew id, display name, role).
ROSTER: tuple[tuple[str, str, Role], ...] = (
    ("dallas", "Dallas", Role.CAPTAIN),
    ("kane", "Kane", Role.EXECUTIVE_OFFICER),
    ("ripley", "Ripley", Role.WARRANT_OFFICER),
    ("ash", "Ash", Role.SCIENCE_OFFICER),
    ("lambert", "Lambert", Role.NAVIGATOR),
    ("parker", "Parker", Role.CHIEF_ENGINEER),
    ("brett", "Brett", Role.ENGINEERING_TECHNICIAN),
)


def morale_word(composure: int) -> str:
    """Mother's state-of-mind word for a composure value — **[C $7DC5]**.

    `fear_band`'s own arithmetic, byte for byte::

        7DCB  LDA $6571,Y        ; the EFFECTIVE composure, not `$7D55`
        7DCE  CMP #$05 / BCC $7DD7
        7DD2  LDA #$00           ; >= 5 -> index 0
        7DDA  LDA #$04 / SEC / SBC $7946   ; else index = 4 - composure

    so composure **4 and above** share index 0, and 3/2/1/0 map to 1/2/3/4.
    The words come from five 10-byte records at `$7D13`
    (CONFIDENT/STABLE/UNEASY/SHAKEN/BROKEN); a sixth would land on `$7D45`,
    the health array, which is how we know the table is exactly five long.
    """
    idx = 0 if composure >= 5 else max(0, 4 - composure)
    return constants.MORALE_BANDS[idx]


def _clamp_fear(value: int) -> int:
    return max(constants.FEAR_MIN, min(constants.FEAR_MAX, value))


#: **[C $8332]** `scan_room_objects` clears two carry slots (`$829A`/`$829B`),
#: so a crew member's hands hold two items.
CARRY_CAPACITY = 2


@dataclass
class CrewMember:
    """One crew member's full state (position, PCS state of mind, what they hold)."""

    id: str
    name: str
    role: Role
    room_id: str | None          # current room; None if unplaced/removed
    # Hidden state of mind, 0..10 (GAME_SPEC §5). [C $7D5D] FV-1b4 applied the real
    # PER-CREW start fear (template `$7D5D` → `$7D55`): [Dallas 4, Kane 4, Ripley 3,
    # Ash 4, Lambert 3, Parker 4, Brett 3] — see `START_FEAR`; `default_crew` sets
    # it, so crew begin UNEASY/SHAKEN rather than CONFIDENT. This field default
    # (FEAR_MIN = 0 = calm) is only for a bare/synthetic CrewMember.
    # **P2-20, corrected 2026-08-02.** The default used to be `FEAR_MIN` — and
    # since this value is **composure** (high = calm), that meant every bare
    # `CrewMember(...)` was born BROKEN. Real crew never are: `default_crew`
    # seeds them from the ROM's own `$7D5D` table (`START_FEAR`, 3-4), and the
    # SHORT scenario from `$609A`. The old default only ever showed up in test
    # fixtures, where it silently made crew members that the ROM's
    # "is anyone still in play" scan (`$5B6C BEQ`) would have discounted.
    # Defaulted to the top of the real starting range instead.
    fear: int = 4
    # Physical health (full disassembly §8.9: the game's `$7D45[1..7]`, counting
    # down as the Alien wounds them; below 2 = incapacitated, see `wound`).
    # [C $7D4D] FV-1b3b applied the real PER-CREW start health (the template
    # `$7D4D` → `$7D45`): [Dallas 6, Kane 5, Ripley 4, Ash 5, Lambert 4, Parker 6,
    # Brett 5] — see `START_HEALTH`; `default_crew` sets it. `full_health` records
    # each member's own maximum so `status`/`effective_walk_ticks` compare against
    # the right baseline (tougher crew survive ~4 wounds, frailer ~2). The scalar
    # `constants.CREW_START_HEALTH` (4) is only the default for a bare/synthetic
    # CrewMember built without a per-crew value.
    health: int = constants.CREW_START_HEALTH
    full_health: int = constants.CREW_START_HEALTH  # this member's own maximum
    alive: bool = True           # can still act (health >= incapacitation floor)
    awake: bool = True           # out of hypersleep ("ENTER HYPERSLEEP", $57D4)
    # **[C $6501,Y] R-10 (D-055): the per-character "in the ducting" flag.**
    # The ROM keeps one per character and several routines branch on it —
    # `place_selected_char_sprite ($6667)` colours the on-screen portrait from
    # it, `resolve_char_move ($5156)` gates movement on the room's grille, and
    # `$729C` adjusts state-of-mind each tick spent crawling. Set here while a
    # crew member's current move step crosses the **duct** network rather than
    # a door (i.e. the two rooms have no direct door between them, so the only
    # route is room -> grille -> junction -> grille -> room).
    in_duct: bool = False
    # **[C $829A/$829B] P2-16 — a crew member carries TWO items, not one.**
    # `scan_room_objects ($8332)` clears exactly two bytes to `$FF`, and
    # `list_room_items ($83AF/$83C6)` refills them by scanning the item-location
    # array for the two holder encodings (`char + $A0` -> `$829A`, drawn at
    # panel row 9; `char + $80` -> `$829B`, row 10). Two slots, two rows.
    carried: list[str] = field(default_factory=list)
    #: Convenience for the single-item callers that predate the two-slot model:
    #: ``CrewMember(..., holding_init="x")`` still works and seeds `carried`.
    holding_init: InitVar[str | None] = None

    def __post_init__(self, holding_init: str | None) -> None:
        if holding_init is not None and holding_init not in self.carried:
            self.carried.append(holding_init)

    @property
    def holding(self) -> str | None:
        """The item a single-item caller means: the **most recent** pickup.

        Kept as a property so the large amount of existing code written against
        a one-item model keeps working, while the underlying state is the
        ROM's two slots.
        """
        return self.carried[-1] if self.carried else None

    @holding.setter
    def holding(self, item_id: str | None) -> None:
        """Put ``item_id`` in hand — promoting it if it is already carried.

        The getter defines "in hand" as ``carried[-1]``, so assigning something
        already in the list has to **move it there**. It used to be a silent
        no-op in that case, which made `SELECT_ITEM` (DISC-261) appear to do
        nothing: swapping to the spare set a value the property already
        reported and the list never changed.
        """
        if item_id is None:
            self.carried.clear()
            return
        if item_id in self.carried:
            self.carried.remove(item_id)      # promote to the active slot
        self.carried.append(item_id)
        del self.carried[:-CARRY_CAPACITY]
    # Ticks per room move (later RE: the game's own per-character walk
    # durations, $6586 — the crew genuinely walk at different speeds).
    # **[C $659A] D-122 — `$6586` is NOT a walk-ticks table.** It is the
    # pristine **backup** of the runtime block at `$656E`: `sub_beep ($6598)`
    # copies 21 bytes from `$6583` to `$656E` at game start, and the crew's
    # starting composure (`$6571`) lives inside that block. Which is why
    # "walk ticks" (4,4,3,4,3,4,3) and `START_FEAR` (4,4,3,4,3,4,3) are
    # identical — they are the same bytes read twice under two names. Nothing
    # in the ROM reads `$6586` as a duration.
    #
    # The real room-move duration is `$7B69`'s flat `#$40` plus
    # `compute_action_delay` (D-112), which `sim` now uses. This field is kept
    # only because tests construct crew with it; it drives nothing.
    walk_ticks: int = 4
    # Countdown of the walk in progress; a MOVE_TO step lands when it hits 0.
    step_timer: int = 0

    # (1:1 fidelity: the old `compliance`/`refusal_bias` obey-probability curve
    #  was an invention and was removed — the decoded program has no compliance
    #  roll on the order path (D-018: Dallas obeyed at fear 4). Fear's real
    #  effects are tempo (`fear_alert $4E16`) and a panic branch (`$52C0`),
    #  now statically traced (D-026) but not yet implemented; see
    #  core/orders.py and core/constants.py.)

    @property
    def composure(self) -> int:
        """Alias for :attr:`fear` under its **correct** meaning (D-059).

        The field is misnamed. `$7D55`/`$6571` is **composure**: high = calm
        and in control, 0 = broken. The `fear` name predates the decode and
        is kept only to avoid a sweeping rename; new code should read this.
        """
        return self.fear

    @property
    def morale(self) -> str:
        """The state-of-mind word Mother reports (GAME_SPEC §5).

        **[C $7DC5 + $7D13], byte-verified 2026-07-24 (D-059) — this was
        INVERTED.** `fear_band ($7DC5)` computes
        ``index = 0 if value >= 5 else (4 - value)`` and indexes the 10-byte
        word records at `$7D13`, which decode to
        ``confident / stable / uneasy / shaken / broken``. So:

            value 0 -> broken   ·  1 -> shaken  ·  2 -> uneasy
            value 3 -> stable   ·  4+ -> confident

        i.e. **high is GOOD**. The remake computed
        ``idx = fear * 5 // 11``, which maps 0 -> CONFIDENT and 10 -> BROKEN —
        exactly backwards. The two formulas happen to agree at value 3 (both
        give STABLE), which is precisely the single data point FV-2g used to
        "confirm" the decode live, so that check never discriminated between
        them. Resolved by decoding the word table itself rather than trusting
        the transcription.
        **PV-07 closed 2026-08-07 (D-163): the 5-way slicing is decoded, not a
        guess** — `$7DCE CMP #$05 / BCC` then `$7DDA LDA #$04 / SEC / SBC`, so
        the bands are exactly ``>=4 · 3 · 2 · 1 · 0``, and `index_x10` walks a
        table of five 10-byte records at `$7D13` (index 5 would land on
        `$7D45`, the health array — proof the table is exactly five long),
        copying **9** chars to `$0767` = **row 21, col 31**, inside the CONTROL
        panel. This formula is byte-for-byte the ROM's.

        **But it must be fed the EFFECTIVE composure.** `$7DCB LDA $6571,Y`
        reads the derived cell (base + companion support, D-151), not the raw
        `$7D55`. Prefer :meth:`Simulation.morale_for`, which does; this
        property is the raw-cell reading and is kept for tests and for callers
        with no Simulation to hand.
        """
        return morale_word(self.fear)

    @property
    def is_insane(self) -> bool:
        """Terminal state-of-mind, reported as "is insane" in the endgame.

        **[C $61E2/$63E5]:** `select_outcome`'s per-survivor loop does
        `LDA $7D55,Y / BNE skip` — a crew member whose state-of-mind cell is
        **exactly 0** gets the `$63E5` string "is insane" appended to their
        name in the end-of-game report, *and* costs 3 Competence points
        (`$61F6: LDA $6411 / SEC / SBC #$03`). This is the same value the
        morale word derives from, and the decoded `fear_band` likewise maps
        0 to the worst band — so both ROM sites agree that **0 is the
        terminal/worst state**, which is what this models.

        (The Competence deduction itself isn't modelled: the remake has no
        Competence Rating mechanic at all — see D-034.)
        """
        return self.fear == constants.FEAR_MIN

    @property
    def status(self) -> str:
        """The crew member's physical status word the panel reports.

        Uses the game's own four status words (decoded to
        ``gamedata_snapshot.STATUS_WORDS``), banded exactly as `health_band
        ($7D94)` does — **[C, D-069 2026-08-01]**::

            health >= 4   -> "O.K."        ($7D9B CMP #$04 -> index 0)
            health 2 or 3 -> "WOUNDED"     (index 1; 2 arrives via `3 - health`)
            health 1      -> "COLLAPSED"   (index 2)
            health 0      -> "DEAD"        (index 3)

        **The O.K./WOUNDED boundary is an absolute 4, not this member's own
        maximum.** That was the bug: start health is per-crew (6/5/4/5/4/6/5),
        so `health >= full_health` made Dallas (max 6) read "WOUNDED" at health
        5, where the real game still reads "O.K.". The COLLAPSED/DEAD split
        already matched, since the acting floor is health < 2 either way.
        """
        # The words come from the game's own `$7CEB` table (STATUS_WORDS) rather
        # than being spelled here, so their **case** is the ROM's: "O.K." and
        # "DEAD" really are capitals while "wounded" and "collapsed" are not.
        if self.health <= 0:
            return STATUS_WORDS[3]
        if self.health < constants.HEALTH_WOUNDED_AT_LEAST:
            return STATUS_WORDS[2]
        idx = 0 if self.health >= constants.HEALTH_OK_AT_LEAST else 1
        return STATUS_WORDS[idx]

    def bump_fear(self, delta: int) -> None:
        """Adjust fear by ``delta`` (clamped to the valid range).

        The knob is exposed here; the *sources* of fear (crowding, corpses, the Alien
        in your room — the decoded stressors, D-011) are wired in the sim/Alien.
        """
        self.fear = _clamp_fear(self.fear + delta)

    def wound(self, amount: int = constants.ALIEN_WOUND_AMOUNT) -> None:
        """Take ``amount`` wounds (full disassembly §8.9: DEC `$7D45,X`).

        Health floors at 0; dropping **below** ``CREW_INCAPACITATED_BELOW`` clears
        ``alive`` — the crew member is out of the game (the `$52C0` actor gate
        requires health >= 2 to act).
        """
        self.health = max(0, self.health - amount)
        if self.health < constants.CREW_INCAPACITATED_BELOW:
            self.alive = False


# Opening placement — **[C $65FF/$793D + $5074-$5077] DISC-229.**
#
# `new_game`'s init loop copies three parallel templates into the runtime
# arrays (8 entries: slot 0 is the Alien, slots 1-7 the crew)::
#
#     65FF  LDA $793D,Y / STA $7935,Y    ; locations
#     6605  LDA $7D4D,Y / STA $7D45,Y    ; health
#     660B  LDA $7D5D,Y / STA $7D55,Y    ; stress
#
# `$793D` = `00 06 06 06 1B 1B 1B 00`: the Alien in AIRLOCK 1, DALLAS/KANE/
# RIPLEY in COMMDCENTR, ASH/LAMBERT/PARKER in MESS, and BRETT parked in
# AIRLOCK 1 too.
#
# **The template is not the final placement.** One RNG draw indexes both
# `$50EC,Y` (the victim) and `$510C,Y` (a room), and the room is stored to
# `$793C` - Brett's slot. Every pair moves Brett into the victim's room, so play
# always opens with three crew in COMMDCENTR and three in MESS, and Brett's
# AIRLOCK 1 entry is a parking slot overwritten every game. Applied in
# `Simulation._apply_full_opening`, not here.
#
# `START_ROOMS` below is **not used** on the real ship - `assign_start_rooms`
# reads the decoded `CREW_START_ROOMS`. It is the synthetic-map fallback only.
# Derivation: DISCOVERIES DISC-229.
START_ROOMS: tuple[str, ...] = (
    "commdcentr", "commdcentr", "commdcentr",
    "life_suppt", "life_suppt", "life_suppt", "life_suppt",
)


def assign_start_rooms(crew: dict[str, CrewMember], ship: ShipMap) -> None:
    """Place the crew on `$793D`'s fixed table — **[C $65FF]**.

    A no-op on ships without the real rooms (synthetic test maps keep whatever
    `default_crew` chose).
    """
    from . import gamedata_snapshot as _data

    for i, (cid, _name, _role) in enumerate(ROSTER):
        member = crew.get(cid)
        if member is None or i >= len(_data.CREW_START_ROOMS):
            continue
        room = _data.ROOM_SLUGS[_data.CREW_START_ROOMS[i]]
        if room in ship.rooms:
            member.room_id = room


# Per-crew walk durations in ticks/room. [C $6586] — this is exactly
# `gamedata_snapshot.CREW_WALK_TICKS` (slots 1-7 of `$6586`; slot 0 = Alien,
# slot 8 = Jones = 5). Hand-copied here rather than imported, which is a **drift
# risk**: `test_crew_tables_match_decoded_snapshot` pins it so a future
# `gamedata` regen can't silently desync the two. ROSTER order:
# Dallas 4, Kane 4, Ripley 3, Ash 4, Lambert 3, Parker 4, Brett 3.
WALK_TICKS: tuple[int, ...] = (4, 4, 3, 4, 3, 4, 3)

# Per-crew starting health. [C $7D4D] — the template new_game copies into the
# working health table `$7D45` (slots 1-7; slot 0 = the Alien wound counter, slot
# 8 = Jones). ROSTER order: Dallas 6, Kane 5, Ripley 4, Ash 5, Lambert 4, Parker
# 6, Brett 5. Hand-transcribed from the PRG (not yet in the snapshot — filed to add
# it to the `gamedata` decoder); pinned by `test_crew_start_health_is_decoded`.
START_HEALTH: tuple[int, ...] = (6, 5, 4, 5, 4, 6, 5)

# Per-crew starting fear/state-of-mind (0..10). [C $7D5D] — the template
# new_game copies into `$7D55`. ROSTER order: Dallas 4, Kane 4, Ripley 3, Ash 4,
# Lambert 3, Parker 4, Brett 3. So crew begin UNEASY/SHAKEN, NOT calm (0) —
# Mother's opening morale report is non-CONFIDENT. `default_crew` applies it;
# pinned by `test_crew_start_fear_is_decoded`. **Stale parenthetical removed
# 2026-09-05 (P9-B goal session):** this used to read "(Same [?] on the
# morale word banding as elsewhere — the value is [C], the 5-way slicing a
# guess.)", but `morale_word` (`$7DC5 fear_band`) has been fully decoded and
# live-confirmed since D-024/FV-2g (2026-07-11) — fear 0/1/2/3 select a
# distinct word each, and every value from 4 up collapses onto CONFIDENT.
# There is no guess left in the banding; the note here was simply never
# updated when that landed.
START_FEAR: tuple[int, ...] = (4, 4, 3, 4, 3, 4, 3)


def default_crew(ship: ShipMap, deck: int = 0) -> dict[str, CrewMember]:
    """Place the seven crew in the game's real starting rooms.

    Falls back to round-robin over ``deck``'s rooms only when the real rooms
    aren't on ``ship`` (synthetic test maps). Leaves everyone alive and awake —
    the crew member already dead at scenario start (GAME_SPEC §9) is
    chosen by ``core.modes.choose_opening_death`` and applied by the caller
    (normally ``Simulation.__init__``), not here.
    """
    fallback = ship.rooms_on(deck)
    crew: dict[str, CrewMember] = {}
    for i, (cid, name, role) in enumerate(ROSTER):
        if START_ROOMS[i] in ship.rooms:
            room_id: str | None = START_ROOMS[i]
        else:
            room_id = fallback[i % len(fallback)].id if fallback else None
        crew[cid] = CrewMember(
            id=cid, name=name, role=role, room_id=room_id, walk_ticks=WALK_TICKS[i],
            health=START_HEALTH[i], full_health=START_HEALTH[i],  # [C $7D4D]
            fear=START_FEAR[i],                                    # [C $7D5D]
        )
    return crew
