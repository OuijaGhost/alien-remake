"""The Alien: movement and combat, corrected against the decompiled routine.

Corrected against the FULL disassembly (``docs/re/DISASSEMBLY.md`` §8.10): the
Alien does not sense/hunt the nearest crew. Each time it finishes an action it
rolls a uniform 0-15 (``rng $888F``) in ``alien_choose_move ($8A36)`` and:

* **roll 0-11** — a **surface move** to the next room read from one of five
  precomputed **route tables** (``$7A3A/$7A5E/$7A82/$7AA5/$7AC8``, one next-room
  id per room), selected by roll band (0-2, 3-4, 5-6, 7-8, 9-11 → tables 0..4).
  The real tables are ported via ``gamedata`` (``ALIEN_ROUTES`` in the snapshot)
  and applied here on the real ship; synthetic test maps fall back to a compass
  approximation (``_compass_dest``). The move takes ``ALIEN_MOVE_TICKS`` (**60**
  — corrected from 70, D-038, 2026-07-24: every surface-move branch in
  ``alien_choose_move ($8A36)`` converges on ``$8A47``, which loads a literal
  ``LDA #$3C``; the old ``70`` came from ``$6581``, which is read only inside
  the *separate* in-duct dispatcher ``alien_ai ($8A74)`` for duct-to-duct
  travel — a distinct, currently-unmodeled mechanic, not the surface timer),
  or the shorter ``ALIEN_PURSUIT_TICKS`` when the wounded Alien is hunting (see
  ``_roll_hunt``).
* **roll 12-15** — slips into its room's duct through the grille and stays
  hidden for ``ALIEN_DUCT_TICKS`` (40) ticks. (The "ALIEN GONE THROUGH GRILLE"
  message.) Rooms without a grille reroll into a surface move.

The encounter side is **doubly random**, and wounds exactly one crew member
(D-177, ``$413C``-``$41F7``). ``$4152 CMP #$07`` skips the attack entirely on 7
of 16 actions; when it does act, one victim is chosen from up to three
co-located candidates and takes a single point. Crew are **wounded**, not
instantly killed (``CrewMember.wound``), and there is no "armed crew are
exempt" rule — nothing on that path looks at what anyone carries.

Meeting crew also **holds the Alien in the room** for 40 passes (D-188): the
encounter is reached by ``$8AE1 JMP $413C``, a JMP, so the pass never falls
through to the move dispatch at ``$8AE4``.

Crew→Alien combat *is* deterministic per item (``resolve_attack`` /
``constants.ITEM_ATTACK_DAMAGE``) — that half of FV-1.6 stands.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import constants
from .gamedata_snapshot import ALIEN_ROUTES, ROOM_SLUGS
from .map import Grille, ShipMap
from .sound import ATTACK_ALERT, SoundCue

if TYPE_CHECKING:
    from .modes import AlienStart
    from .state import GameState

_DIRECTIONS = ("north", "south", "east", "west")

# Reverse of ROOM_SLUGS: the real room slug -> its game location index, so the
# Alien's route tables (indexed by location id) can be applied on the real ship.
_SLUG_TO_INDEX: dict[str, int] = {slug: i for i, slug in enumerate(ROOM_SLUGS)}


def _route_band(roll: int, bounds: tuple[int, ...] | None = None) -> int:
    """Which of the five route tables a surface roll uses (§8.10).

    ``bounds`` are the ROM's own comparison chain — **which chain depends on the
    grille**: `$8A40`'s 3/5/7/9 when the room's grille is already open,
    `$89E8`'s 3/6/9/12 when it is still in place. Defaults to the open-grille
    chain for callers that predate the split.
    """
    for band, upper in enumerate(bounds or constants.ROUTE_BAND_BOUNDS):
        if roll < upper:
            return band
    return 4  # the last band always falls through to table 4


def _route_dest(
    ship: ShipMap, room_id: str, roll: int, bounds: tuple[int, ...] | None = None
) -> str | None:
    """Next room from the real route tables, or ``None`` if unavailable here.

    Full disassembly §8.10: the surface move looks up ``ALIEN_ROUTES[band][idx]``
    where ``idx`` is the Alien's current location id. Returns ``None`` when the
    room isn't a real mapped room (synthetic test maps) or the destination isn't
    on this ship, so the caller can fall back to the compass model.
    """
    idx = _SLUG_TO_INDEX.get(room_id)
    if idx is None:
        return None
    table = ALIEN_ROUTES[_route_band(roll, bounds)]
    if idx >= len(table):
        return None
    dest_slug = ROOM_SLUGS[table[idx]]
    return dest_slug if dest_slug in ship.rooms else None


def _panic_route_band(roll: int) -> int:
    """Which route table a **panicking crew member** uses (`char_wander $5203`).

    [C $5214-$524F] — a *different* band mapping from the Alien's own
    (`_route_band`), byte-traced from the comparison chain:
    ``roll >= 12 -> $7AC8`` · ``9-11 -> $7AA5`` · ``6-8 -> $7A82`` ·
    ``3-5 -> $7AA5`` · ``0-2 -> $7AC8``. Only **three** of the five tables
    are ever used (indices 2/3/4 = ``$7A82``/``$7AA5``/``$7AC8``), and two of
    them appear twice — so a panicking crew member roams on the Alien's own
    routing data but with its own, more repetitive distribution.
    """
    if roll >= 12:
        return 4
    if roll >= 9:
        return 3
    if roll >= 6:
        return 2
    if roll >= 3:
        return 3
    return 4


#: **[C $8974-$89A6] D-156 — Jones's own route-band mapping.**
#: His destination picker rolls `rng AND #$07` (0-7) and maps it onto the same
#: five route tables the Alien uses, but with bands all of its own::
#:
#:     897A  CPX #$02 / BCC -> $7A3A   ; rolls 0-1
#:     8985  CPX #$04 / BCC -> $7A5E   ; rolls 2-3
#:     898F  CPX #$05 / BCC -> $7A82   ; roll  4
#:     8999  CPX #$06 / BCC -> $7AA5   ; roll  5
#:     89A3           else -> $7AC8    ; rolls 6-7
#:
#: Distinct from both the Alien's own bands and `_panic_route_band`'s — three
#: different mappings over the same five tables.
_JONES_ROUTE_BANDS: tuple[int, ...] = (0, 0, 1, 1, 2, 3, 4, 4)
JONES_ROLL_SIDES = 8              # $8974 AND #$07


def jones_dest(ship: ShipMap, room_id: str, roll: int) -> str | None:
    """Where Jones will amble next (`$8971`) — the Alien's route tables again.

    This closes the `[?]` D-036 opened and D-153 carried: his move is not a
    uniform pick among door neighbours, it is the **same five route tables**
    (`ALIEN_ROUTES`) the creature and `panic_dest` use, read through
    `_JONES_ROUTE_BANDS`. ``None`` when the room or destination is off this
    ship (synthetic test maps), so the caller can leave him put.
    """
    idx = _SLUG_TO_INDEX.get(room_id)
    if idx is None:
        return None
    band = _JONES_ROUTE_BANDS[roll % len(_JONES_ROUTE_BANDS)]
    table = ALIEN_ROUTES[band]
    if idx >= len(table):
        return None
    dest_slug = ROOM_SLUGS[table[idx]]
    return dest_slug if dest_slug in ship.rooms else None


def tracker_zone(room_id: str) -> list[str]:
    """The six rooms a held tracker watches — **[C $8DB6-$8DD1] D-150**.

    `resolve_char_display_loc` builds `$6565..$656A` from the holder's own
    room plus that room's entry in **each of the five route tables**
    (`$7A3A`, `$7A5E`, `$7A82`, `$7AA5`, `$7AC8` — the same `ALIEN_ROUTES`
    the Alien's own movement and `panic_dest` use). Index 0 is the holder's
    room; 1-5 are its neighbours. The scans that follow index this array, so
    the tracker's range is **the holder's room plus its five route
    neighbours**, not the ship — which is the long-standing `[?]` on
    `_use_tracker` finally answered.
    """
    idx = _SLUG_TO_INDEX.get(room_id)
    if idx is None:
        return []
    zone = [room_id]
    for table in ALIEN_ROUTES:
        if idx < len(table):
            zone.append(ROOM_SLUGS[table[idx]])
    return zone


def surface_move_targets(ship: ShipMap, room_id: str) -> list[str]:
    """The MOVE TO list a **surfaced** crew member is offered — [C $7860] D-167.

    Not a sorted set of neighbours. The builder walks the five route tables in
    fixed order and applies two different tests per entry::

        7883  CMP $7947 / BEQ next    ; == the LAST ACCEPTED entry -> skip it
        7888  CMP $7934 / BEQ $7908   ; == the CURRENT ROOM -> END THE LIST

    That second branch is the one that matters: a self-referencing table entry
    does not merely get skipped, it **terminates the whole list**, so every
    later table is never consulted. A room whose second route entry points at
    itself offers exactly one destination however rich its remaining tables
    are. (`gamedata.surface_exits` already terminates this way; what is new is
    that the *menu* is built by the same walk.)

    The dedupe is also weaker than a set: `$7947` holds only the **last
    accepted** destination, so A, B, A lists all three — a repeat is dropped
    only when it is consecutive. And the order is the tables' order, which is
    what the panel cursor indexes positionally.
    """
    idx = _SLUG_TO_INDEX.get(room_id)
    if idx is None:                      # synthetic map: fall back to doors
        return sorted(ship.door_neighbors(room_id))
    out: list[str] = []
    last: str | None = None
    for table in ALIEN_ROUTES:
        if idx >= len(table):
            break
        dest = ROOM_SLUGS[table[idx]]
        if dest == room_id:
            break                        # $7888 BEQ $7908 -- ends the list
        if dest == last:
            continue                     # $7883 -- consecutive repeat only
        if dest in ship.rooms:
            out.append(dest)
            last = dest
    return out


def duct_move_targets(ship: ShipMap, room_id: str) -> dict[str, str]:
    """The in-duct MOVE TO list, by compass direction — [C $81EF] D-167.

    The duct builder walks the four compass tables and applies **only** the
    current-room test (`$81F2 CMP $7934 / BEQ next`), and that test is a
    **skip**, not a terminate — the asymmetry with the surface builder above.
    There is no `$7947` last-accepted dedupe either, because each slot is
    labelled with its own fixed direction word (`$807F` NORTH / `$8093` EAST /
    `$8089` SOUTH / `$809D` WEST) rather than a room name, so two
    directions leading to the same room are still two distinct choices.
    """
    exits = ship.duct_exits(room_id)
    out: dict[str, str] = {}
    for direction in ("north", "east", "south", "west"):
        dest = exits.get(direction)
        if dest is None or dest == room_id:      # $81F2 -- skip, not stop
            continue
        if dest in ship.rooms:
            out[direction] = dest
    return out


def panic_dest(ship: ShipMap, room_id: str, roll: int) -> str | None:
    """Where a panicking crew member bolts to (`char_wander $5203`).

    Same table lookup as the Alien's surface move, but through
    :func:`_panic_route_band`. ``None`` when the room/destination isn't on
    this ship (synthetic test maps), so the caller can leave them put.
    """
    idx = _SLUG_TO_INDEX.get(room_id)
    if idx is None:
        return None
    table = ALIEN_ROUTES[_panic_route_band(roll)]
    if idx >= len(table):
        return None
    dest_slug = ROOM_SLUGS[table[idx]]
    return dest_slug if dest_slug in ship.rooms else None


@dataclass
class Alien:
    """The Alien's state: where it is, its current action countdown, and life."""

    room_id: str | None
    alive: bool = True
    # Ticks left on the current action (a move-in-progress or a duct stay).
    timer: int = 0
    # Where the in-progress move lands (may equal room_id: a blocked/idle roll).
    dest_id: str | None = None
    # Hidden in its room's duct (crew in the room are safe; it's unseen).
    in_duct: bool = False
    # Set to the room whose grille it has just torn open ([C $8B84], P-6), for
    # the renderer's "GRILLE BURSTS OPEN" message; cleared once shown.
    burst_grille_room: str | None = None
    #: The ROM's `$6563`. Corrosion at the top of a dispatch reads the flag the
    #: *previous* dispatch left set, because `$89B1 JSR guard_6562` runs before
    #: the move logic while `$8AE4`/`$8B13` run after it.
    corrode_pending: bool = False
    #: The ROM's `$64B4` — the hunting latch, set by `$4CB3` when the
    #: aggression roll lands and cleared at `$8A09` once the provoked move
    #: completes. While set the creature does **not** corrode (`$89AF`), will
    #: not enter a duct (`$89CE`/`$8A90`), and moves on the 20-tick pursuit
    #: timer. A wounded Alien stops eating the ship and comes after you.
    hunting: bool = False
    #: The ROM's `$6562` — an attack sequence is on screen (`$8CD9 INC $6562`,
    #: cleared by `reset_attack_state $8C80`). Corrosion is off while it is.
    attack_sequence: bool = False
    #: **DISC-325/DEC-046 — a fractional-rate accumulator, not the ROM's own
    #: state.** The ROM's `guard_6562` is unconditional: eligible means it
    #: corrodes, every time, `+1`. `corrode_rate` (a caller-supplied fraction,
    #: `advance_alien`/`_resolve_surface_action`) is credited here each
    #: eligible action and only actually adds `ROOM_DAMAGE_ALIEN_PER_ACTION`
    #: once the credit reaches a whole point — a Bresenham-style accumulator
    #: so a rate below 1.0 lands smoothly rather than in lumps, and touches
    #: no RNG (ORIGINAL's own seeded trajectories stay reproducible from
    #: every other roll). `ALIEN_CORRODE_RATE` (ORIGINAL, ~0.71 — DISC-325)
    #: and `UPDATED_ALIEN_CORRODE_RATE` (DEC-044's own further throttle) are
    #: both expressed through this one field now.
    corrode_credit: float = 0.0
    # Accumulated wounds (full disassembly §8.8: the game's `$7D45[0]`, counting
    # up); the Alien dies once this reaches `ALIEN_DAMAGE_TO_KILL`.
    damage: int = 0
    # Escalating aggression (full disassembly §8.10: the game's `$4781`), grown
    # from the Alien's own wounds; drives the hunt-faster pursuit timer.
    aggression: int = 0


@dataclass(frozen=True)
class AttackResult:
    """Outcome of one crew ``ATTACK`` against the Alien (full disassembly §8.8)."""

    hit: bool     # a lethal weapon landed a wounding blow (spills acid — §8.6)
    killed: bool  # the Alien's accumulated wounds reached the lethal threshold


def add_room_damage(state: GameState, room_id: str | None, amount: int) -> None:
    """Add structural damage to a room's accumulator (`$653F,X`, DISASSEMBLY §8.6).

    **PV-13 closed 2026-08-07 (D-165): the "only 20 entries" claim was wrong,**
    and the remake's broad coverage is right. The tables are laid out back to
    back and the gaps give their size exactly::

        $651C  alarm stages   ($653F - $651C = 35 = the room count)
        $653F  raw damage     ($6562 - $653F = 35, and $6562 is the next
                               known cell, the attack-sequence latch)

    and the init wipe at `$65A9` (`STA $64A0,Y / CPY #$CE`) clears
    `$64A0`-`$656D`, spanning both. The scoring sweep independently walks
    `$653F,Y` to `$6269 CPY #$22` = **34 rooms** — it skips only room 34, the
    NARCISSUS, which is the shuttle rather than part of the ship.

    The "20" came from `mainloop_sub_5684`'s `CPX #$14`, which is the **fire
    burn loop's** bound (rooms `$11`-`$13`), not a table size — the same
    mistake in kind as reading `$5753` as a fire flag (D-163).
    """
    if room_id is None or amount <= 0:
        return
    state.room_damage[room_id] = state.room_damage.get(room_id, 0) + amount
    # `damage_room_b ($5587)`: once a room's raw damage reaches the alarm
    # threshold, raise the `$651C` alarm stage — **but only while it reads 0**
    # (`$559E: LDA $651C,X / BNE skip`), so it fires once per silencing, not
    # every tick. The FIGHT FIRE / extinguisher handler is the only thing that
    # resets it (D-044); the damage itself is never reduced.
    damage = state.room_damage[room_id]
    if damage < constants.ROOM_ALARM_DAMAGE_THRESHOLD:
        return                                     # `$5593 RTS`
    if damage >= constants.ROOM_ALARM_CRITICAL_THRESHOLD:
        # **[C $5598 -> $5658] D-164 — the CRITICAL stage.** Past 15 the
        # routine takes a different exit entirely: it latches `$651C,X` to
        # **2** (once) and draws the long 30-char warning. Crucially it never
        # reaches `$55B1`, so **FIGHT FIRE is not re-armed** — an engine room
        # this badly damaged that has already been extinguished once can never
        # be fought again. (`hull_breach` at exactly 20 is handled by
        # `Simulation.advance`'s own threshold sweep, which is equivalent.)
        if state.room_alarm.get(room_id) != constants.ROOM_ALARM_STAGE_CRITICAL:
            state.room_alarm[room_id] = constants.ROOM_ALARM_STAGE_CRITICAL
            _raise_malfunction(state, room_id, arm_fire=False)
        return
    # `$559E: LDA $651C,X / BNE skip` — stage 1 latches only from 0, so it
    # fires once per silencing rather than every tick. FIGHT FIRE is the only
    # thing that resets it (D-044); the damage itself is never reduced.
    if not state.room_alarm.get(room_id):
        state.room_alarm[room_id] = 1
        _raise_malfunction(state, room_id, arm_fire=True)      # `$55B1`


def weapon_would_breach(
    state: GameState, room_id: str | None, item_type_id: str | None,
) -> bool:
    """Would landing a hit with ``item_type_id`` in ``room_id`` breach the
    ship outright right now, under DEC-044's retuned pre-add gate?

    **Matches `_resolve_attack_order`'s own check exactly** (current damage
    already at/past the gate — not "would adding this hit reach it", which
    is a different, more conservative question the gate does not actually
    ask): factored out so `app.py`'s turn-based loop can ask the same thing
    *before* committing to an order — DEC-045 uses it to tell a forced
    tactical retreat (fleeing a room the gate has made too hot to fight in
    right now) from an ordinary move, so the former doesn't cost a whole
    action point for landing zero progress toward the kill.
    """
    if room_id is None:
        return False
    gate = (
        constants.ROOM_BREACH_GATE_HARPOON if item_type_id == "harpn_gun"
        else constants.ROOM_BREACH_GATE_OTHER
    )
    return state.room_damage.get(room_id, 0) >= gate


def _raise_malfunction(
    state: GameState, room_id: str, *, arm_fire: bool = True
) -> None:
    """Display the room's malfunction banner as the alarm latches (D-073).

    This is not a separate event: `damage_room_b ($5587)` raises the `$651C`
    latch at `$55A6` and then falls **straight through** to the message
    dispatcher at `$55C1`, so the banner and the alarm are one and the same
    trigger. The message comes from the static per-room table `$54A3`; rooms in
    the 17-19 band additionally get the FIRE flag `$5753,X = 6` (`$55B1`),
    which is exactly the set `$54A3` marks as malfunction type 4.
    """
    from .gamedata_snapshot import ROOM_SLUGS

    try:
        idx = ROOM_SLUGS.index(room_id)
    except ValueError:
        return                      # synthetic test map, not a real room
    kind = constants.ROOM_MALFUNCTION_TYPE.get(idx)
    if kind is None:
        return                      # `$55C4 BEQ` — this room has no malfunction
    message = constants.MALFUNCTION_MESSAGES[kind]
    if kind == constants.MALFUNCTION_FIRE_TYPE:
        # `$55F2 LDA #$04 / CMP $53E4` — type 4 alone appends the room name.
        message += room_id.replace("_", " ").upper()
        # **[C $55B1] D-164** — `LDA #$06 / STA $5753,X`, the write that puts
        # FIGHT FIRE on the panel, sits on the 4..14 branch only. `arm_fire` is
        # False on the critical (>= 15) path, which never reaches it.
        if arm_fire:
            state.room_fire[room_id] = constants.ROOM_FIRE_FLAG
    state.malfunction = message


def spawn_alien(
    ship: ShipMap,
    start: "AlienStart | None" = None,
    rng: random.Random | None = None,
    avoid: "Iterable[str]" = (),
) -> Alien:
    """Place the Alien at scenario start.

    RW-8 resolved (D-014): the static location table (`$7935` slot 0 == 0) and
    two independent live boots all show the Alien starting at **room id 0 =
    AIRLOCK 1**. (An earlier CARGOPOD 2 reading was a misinterpretation of one
    capture.) Falls back to the deepest room of the lowest deck on synthetic
    test maps without the real rooms.

    ``start=AlienStart.RANDOM`` is an **added rule, not the ROM** (DISC-260) —
    see :class:`~alien_remake.core.modes.AlienStart`. It draws from the mapped
    rooms only: the Narcissus is excluded because it is off the deck plans
    entirely (deck 3, DISC-244), and ``avoid`` excludes the crew's own starting
    rooms so the game does not open with the creature already on top of them.
    """
    from .modes import AlienStart

    if start is AlienStart.RANDOM and rng is not None:
        blocked = set(avoid) | {NARCISSUS_SLUG}
        choices = sorted(
            r.id for r in ship.rooms.values()
            if r.id not in blocked and r.deck in ship.decks()
        )
        if choices:
            return Alien(room_id=choices[rng.randrange(len(choices))])
    if "airlock_1" in ship.rooms:
        return Alien(room_id="airlock_1")
    decks = ship.decks()
    if not decks:
        return Alien(room_id=None)
    rooms = ship.rooms_on(max(decks))
    return Alien(room_id=rooms[-1].id if rooms else None)


def _compass_dest(ship: ShipMap, room_id: str, roll: int, rng: random.Random) -> str:
    """The decoded direction pick: roll < 3 N, < 6 S, < 9 E, else W.

    Reads the room's real compass exits; a blocked direction returns the room
    itself (the original moves the Alien "to" its own room — an idle). On
    synthetic maps without compass data, falls back to a random door neighbor.
    """
    room = ship.rooms[room_id]
    if not room.exits:
        neighbors = ship.door_neighbors(room_id)
        return rng.choice(neighbors) if neighbors else room_id
    n, s, e = constants.ALIEN_DIR_BOUNDS
    direction = "west"
    if roll < n:
        direction = "north"
    elif roll < s:
        direction = "south"
    elif roll < e:
        direction = "east"
    return room.exits.get(direction, room_id)


def _room_has_grille(ship: ShipMap, room_id: str) -> bool:
    return any(g.room_id == room_id for g in ship.grilles)


def _grille(ship: ShipMap, room_id: str) -> "Grille | None":
    """The room's grille, or ``None`` if it has none."""
    for g in ship.grilles:
        if g.room_id == room_id:
            return g
    return None


def _grille_is_shut(ship: ShipMap, room_id: str) -> bool:
    """[C $8676] Nonzero = the grille is still in place; 0 = removed/burst."""
    g = _grille(ship, room_id)
    return g is not None and not g.is_open


def _burst_grille(ship: ShipMap, alien: Alien, room_id: str) -> bool:
    """The Alien tears a grille open — **[C $8B84]**, P-6.

    Reached whenever it tries to cross a grille still in place, from either
    side: emerging into a room (`$8B7F`) or ducking into one from the surface
    (`$8BB4`). It does **not** move this turn — it clears that room's `$8676`
    byte (the grille is gone permanently), pauses 40 ticks and raises the
    "GRILLE BURSTS OPEN" event. Returns True if a grille was actually burst.
    """
    g = _grille(ship, room_id)
    if g is None or g.is_open:
        return False
    g.is_open = True                       # $8B86 STA $8676,Y
    alien.dest_id = None                   # $8B94 RTS — no move this turn
    alien.timer = constants.ALIEN_BURST_TICKS
    alien.burst_grille_room = room_id      # for the renderer's message
    return True


def _begin_duct_action(ship: ShipMap, alien: Alien, rng: random.Random) -> None:
    """The Alien's move while **inside** the ducts — [C $8A74], P-6.

    Roll bands pick a compass (duct) neighbour: 0-2 N, 3-5 E, 6-8 S, 9-12 W;
    **13-15 emerges into the current room** (`$8A92` sets the destination
    without bit 7, which `$8B6F` reads as "come out here"). While the current
    room's grille is still shut, roll 15 is re-rolled (`$8A7A`-`$8A83`).
    """
    assert alien.room_id is not None
    while True:
        roll = rng.randrange(constants.ALIEN_ROLL_SIDES)
        if roll == constants.ALIEN_DUCT_BLOCKED_REROLL and _grille_is_shut(
            ship, alien.room_id
        ):
            continue                       # $8A83 JMP $8A7C
        break
    if roll >= constants.ALIEN_DUCT_EMERGE_FROM:
        # Emerge here — bursting the grille first if it is still shut.
        if _burst_grille(ship, alien, alien.room_id):
            return
        alien.in_duct = False              # $8B95 STA $6501 = 0
        alien.dest_id = alien.room_id
        alien.timer = constants.ALIEN_DUCT_TICKS
        return
    exits = ship.duct_exits(alien.room_id)
    order = [d for d in ("north", "east", "south", "west")]
    band = sum(1 for edge in constants.ALIEN_DUCT_DIR_BANDS if roll >= edge)
    dest = exits.get(order[band])
    # A self-referencing table entry means no duct that way; the ROM would move
    # the Alien onto itself, which is a no-op — model it as staying put.
    alien.dest_id = dest if dest is not None else alien.room_id
    # [C $8AAB `LDA $6581`] duct travel has its own, SLOWER duration (70) than
    # a surface move's literal 60 — crawling vs walking.
    alien.timer = constants.ALIEN_DUCT_TRAVEL_TICKS
    alien.in_duct = True


#: `$89C4`'s loop is unbounded in the ROM; bound it here so a pathological map
#: cannot hang the simulation. 64 rolls makes an accidental exit astronomically
#: unlikely on the real ship (worst real room still has 2 of 16 outcomes valid).
_MAX_MOVE_ROLLS = 64
#: **[C $89D0 `LDX #$22`]** the Alien never enters a duct from room 34 -- which
#: is the NARCISSUS, not the shuttlebay (32). The index was always right; the
#: name was wrong (D-159).
_NARCISSUS_SLUG = ROOM_SLUGS[0x22]
#: Public alias — `spawn_alien` excludes it from a random start.
NARCISSUS_SLUG = _NARCISSUS_SLUG


def _begin_action(ship: ShipMap, alien: Alien, rng: random.Random) -> None:
    """Roll the next action exactly as the decoded routine does."""
    assert alien.room_id is not None
    if alien.in_duct:
        _begin_duct_action(ship, alien, rng)
        return
    # **[C $89C4] P2-19 — `alien_choose_move` is a RE-ROLL LOOP, not a single
    # roll.** Every rejected outcome does `JMP $89C4` and rolls again:
    #
    #   `$89CE BNE $89C4`  — refuse the duct while a move is already in flight
    #   `$89D5 BEQ $89C4`  — refuse the duct from room $22 (SHUTTLEBAY)
    #   `$8A04 JMP $89C4`  — **refuse a destination equal to the Alien's own
    #                        room** (`$89FF CPX $64E6`)
    #
    # That last one is the one that mattered. The route tables encode "no exit
    # this way" as a **self-reference** (the same convention as the compass
    # tables, D-083, and the reason `gamedata.surface_exits` terminates on one),
    # and three of AIRLOCK 2's five entries are self-references. The remake took
    # them at face value, so the Alien "moved" to the room it was already in and
    # **parked** — 70% of one measured game in a single room — grinding that
    # room's damage to the breach threshold and ending the game on its own,
    # often before the player had seen the creature at all.
    # **[C $89BF/$89C2] P2-21 — which distribution applies depends on whether
    # this room's grille is still in place.** An open grille makes the Alien
    # four times likelier to take the duct (25% vs 6.25%) and narrows the
    # spread of its surface destinations. See `constants` for the full table.
    shut = _grille_is_shut(ship, alien.room_id)
    duct_at = (
        constants.ALIEN_DUCT_THRESHOLD_GRILLE_SHUT if shut
        else constants.ALIEN_DUCT_THRESHOLD_GRILLE_OPEN
    )
    bounds = (
        constants.ROUTE_BAND_BOUNDS_GRILLE_SHUT if shut
        else constants.ROUTE_BAND_BOUNDS_GRILLE_OPEN
    )
    # **[C $89F7] D-159 — the hunt latch `$64B4`, rolled ONCE per action.**
    # The ROM reads it a single time after picking a destination, and it is
    # what decides *both* the self-reference re-roll and the move duration.
    # Rolled here, before the destination loop, so one latch governs the whole
    # action exactly as `$64B4` does. `alien_choose_move` (the grille-open
    # path, `$8A36`) never consults it at all — hence the `shut and` guards.
    hunting = shut and _roll_hunt(alien, rng)
    for _ in range(_MAX_MOVE_ROLLS):
        roll = rng.randrange(constants.ALIEN_ROLL_SIDES)
        if roll >= duct_at:
            if alien.room_id == _NARCISSUS_SLUG:
                continue                       # `$89D0-$89D5` re-roll
            if _room_has_grille(ship, alien.room_id):
                # [C $89D7/$8BB1] It wants the duct. If the grille is still shut
                # it bursts it instead of moving (P-6); otherwise it slips in.
                if _burst_grille(ship, alien, alien.room_id):
                    return
                alien.in_duct = True
                alien.dest_id = alien.room_id
                alien.timer = constants.ALIEN_DUCT_TICKS
                return
            continue                           # no grille here: roll again
        # Real ship: the game's own route tables (§8.10); synthetic maps without
        # them fall back to the compass approximation.
        dest = _route_dest(ship, alien.room_id, roll, bounds)
        if dest is None:
            dest = _compass_dest(ship, alien.room_id, roll, rng)
        if dest == alien.room_id:
            # **[C $89F7-$8A04] D-159 — this rejection is CONDITIONAL.**
            #
            #     89F7  LDX $64B4 / BEQ $8A11   ; not hunting -> RTS, accepted
            #     89FF  CPX $64E6 / BNE $8A07
            #     8A04  JMP $89C4               ; hunting -> re-roll
            #
            # P2-19 made it unconditional. The route tables encode "no exit
            # this way" as a self-reference, and on an ordinary turn the ROM
            # simply **accepts it and stays put for 60 passes** — which is how
            # the creature lingers anywhere at all. Both airlocks self-refer on
            # 9 of 16 rolls, so re-rolling them away meant our Alien never sat
            # in a lock long enough to be vented; the BLOWLOCK win route was
            # effectively unreachable. No room's whole route row self-refers,
            # so the ROM's loop always terminates.
            if hunting:
                continue                       # `$8A04 JMP $89C4`
            alien.in_duct = False
            alien.dest_id = None               # `$89FA BEQ $8A11`: hold position
            alien.timer = constants.ALIEN_MOVE_TICKS          # `$89F2` #$3C
            return
        alien.in_duct = False
        alien.dest_id = dest
        if hunting:
            alien.aggression = 0               # `$8A09 STX $64B4` — latch spent
            alien.hunting = True               # `$4CB8 STA $64B4` — no corroding
            alien.timer = constants.ALIEN_PURSUIT_TICKS       # `$8A0C` #$14
        else:
            alien.timer = constants.ALIEN_MOVE_TICKS          # `$89F2` #$3C
        return
    # Every roll wanted a duct this room does not have. The ROM would spin
    # here; hold position instead of looping forever, and try again next action.
    alien.in_duct = False
    alien.dest_id = None
    alien.timer = constants.ALIEN_MOVE_TICKS


def _roll_hunt(alien: Alien, rng: random.Random) -> bool:
    """Is `$64B4` set for this action? — **[C $4C9C-$4CB8]**

    `$4781` is a threat accumulator that grows by `damage/4` every pass; when
    `rng(0-15) < $4781` the game sets `$64B4` (and `$64A0`) and gives the
    creature a provoked turn. An undamaged Alien never hunts (the accumulator
    stays 0), so this returns early **without consuming an rng draw** — the
    unhurt Alien's RNG sequence is unchanged, which several calibrated tests
    depend on.

    The latch it models is consumed at `$8A09` once a hunting turn actually
    produces a move, which is why `_begin_action` zeroes `aggression` there.
    """
    if alien.damage <= 0:
        return False
    alien.aggression = min(
        constants.ALIEN_ROLL_SIDES - 1,
        alien.aggression + alien.damage // constants.AGGRESSION_DAMAGE_DIVISOR,
    )
    return rng.randrange(constants.ALIEN_ROLL_SIDES) < alien.aggression


def advance_alien(
    ship: ShipMap, state: GameState, alien: Alien, rng: random.Random,
    *, corrode_rate: float = constants.ALIEN_CORRODE_RATE,
) -> None:
    """One tick: count the current action down; on arrival, surface/move and
    resolve the encounter (frighten crew, maybe kill the undefended).

    No-op once the Alien is dead or unplaced.

    ``corrode_rate`` is a caller-supplied override (DISC-325/DEC-046):
    `Simulation` passes `constants.ALIEN_CORRODE_RATE` (ORIGINAL) or
    `UPDATED_ALIEN_CORRODE_RATE` (UPDATED, DEC-044's own further throttle on
    top). Neither is the ROM's own literal behaviour (an unconditional `+1`
    every eligible action, i.e. rate 1.0) — see `ALIEN_CORRODE_RATE`'s own
    comment in `constants.py` for why ORIGINAL itself no longer uses that
    literal reading. `alien.corrode_credit` is where the fraction actually
    accumulates; see its own docstring.
    """
    if not alien.alive or alien.room_id is None:
        return

    # **[C $8ACE] P2-21 — one action is ONE pass, not two.** `alien_tick` is
    # `DEC $64EE / BEQ` and then does everything in a single visit: arrive
    # (`$8AD4 JSR alien_arrive`), set the `$6563` arrived-flag, corrode, and
    # dispatch the next move. This function used to split that across two
    # ticks — land the move on one, `_begin_action` on the next — and **both
    # branches fell through to the corrosion and encounter code**, so the
    # Alien damaged its room and wounded co-located crew **twice per action
    # cycle**. Halving that is not a tuning choice; it is what the ROM does.
    if alien.timer > 0:
        alien.timer -= 1
        if alien.timer > 0:
            return

    # --- one alien action pass ------------------------------------------
    # Land whatever move was in flight (`alien_arrive $5B56`).
    # `$8B03 LDA $7935 / CMP $64E6 / BEQ $8B13 INC $6563` — the corrosion flag
    # rises only when the Alien's room equals its **destination**, i.e. it did
    # not move this dispatch. Moving in does not corrode; lingering does.
    # `$89B1 JSR guard_6562` runs at the top of the dispatch, so corrosion is
    # decided by the flag the previous pass left behind, not by this one.
    # `guard_6562 ($8EBD)`'s three gates, in the ROM's own order: no attack
    # sequence on screen, not hunting, and `$6563` set by the previous pass.
    corrode = (
        alien.corrode_pending
        and not alien.attack_sequence      # `$8EBD LDA $6562 / BNE rts`
        and not alien.hunting              # `$89AF LDX $64B4 / BNE`
    )
    alien.hunting = False                  # `$8A09` — the latch is spent
    arrived = alien.dest_id is None or alien.dest_id == alien.room_id
    if alien.dest_id is not None:
        alien.room_id = alien.dest_id
    alien.dest_id = None
    # P-6: `in_duct` is not cleared unconditionally — the Alien travels
    # duct-to-duct and only surfaces when its own roller says to (`$8A92`),
    # or after bursting a grille.
    surfaced = not alien.in_duct
    if surfaced and _resolve_surface_action(
        ship, state, alien, rng, corrode=corrode, corrode_rate=corrode_rate
    ):
        # **[C $8AE1] D-188 - after meeting crew the Alien STAYS PUT.**
        # `alien_tick` reaches the encounter with a **JMP**, not a JSR::
        #
        #     8AD7  LDA $64A3 / BEQ $8AE4     ; nobody here -> ordinary turn
        #     8ADC  LDA $64A0 / BNE $8AE4
        #     8AE1  JMP $413C                 ; met crew -> jump away
        #     8AE4  ...clear $6563, redraw, then pick the next move...
        #
        # so an encounter pass never reaches `$8AE4` and never dispatches a
        # move. `$413C`'s own first act is `LDA #$28 / STA $64EE` - it re-arms
        # the timer to **40 passes (~5 s)** and returns. The creature holds the
        # room for that long before taking a normal turn.
        #
        # The remake fell straight through to `_begin_action` and chose a new
        # destination on the same pass, so it hit someone and immediately
        # walked out - exactly what the player reported. The hold applies on a
        # **miss** too: `$413C` re-arms before `$4152`'s roll is even taken.
        alien.dest_id = None
        alien.timer = constants.ALIEN_ENCOUNTER_HOLD_TICKS
        # `$8CD9 INC $6562` — the ATTACK panel is up, so the next pass does not
        # corrode. `reset_attack_state ($8C80)` clears it when the sequence ends.
        alien.attack_sequence = True
        return
    # `$8AE4`: `STY $6563` clears the flag, then `$8B13 INC $6563` re-raises it
    # only when `$7935 == $64E6` — the Alien sat still rather than moving in.
    # An encounter pass returned above without reaching here, so it leaves the
    # flag alone: **the Alien does not corrode the room it is holding after
    # meeting crew**, which is the state the remake used to corrode hardest in.
    alien.corrode_pending = arrived
    alien.attack_sequence = False          # `reset_attack_state ($8C80)`
    _begin_action(ship, alien, rng)
    return


def _resolve_surface_action(
    ship: ShipMap, state: GameState, alien: Alien,
    rng: random.Random | None = None, *, corrode: bool = True,
    corrode_rate: float = constants.ALIEN_CORRODE_RATE,
) -> bool:
    """Corrosion + encounter for one action the Alien spends on the surface.

    ``rng`` is required for the encounter (D-177: `$4152`'s attack roll and
    `$41B8`/`$41C4`'s victim pick). Callers without one get the corrosion
    only, which is what the old signature effectively did.

    Returns **True if the encounter path was entered at all** - i.e. the Alien
    met co-located crew - whether or not the attack roll then landed. `$413C`
    re-arms the timer before `$4152` rolls, so the hold happens either way
    and the caller needs to know (D-188).
    """
    assert alien.room_id is not None

    # Acid blood / tearing. `guard_6562 ($8EBD)` does `INC $653F,X` for the
    # Alien's room behind three gates: no attack sequence on screen (`$6562`),
    # the Alien not in a duct (`$6501`), and **`$6563` set** — which `$8B13`
    # raises only when the Alien is sitting at its destination rather than
    # moving into it. The creature corrodes a room it **lingers in**, not every
    # room it passes through.
    #
    # This matters more than it looks. Corroding on every action instead
    # breached a room every ~500-2000 ticks with nobody doing anything, which
    # put the kill route out of reach: the ship died long before 50 damage
    # could be dealt.
    #
    # **DISC-325/DEC-046: `corrode_rate` is not 1.0 even here, under
    # ORIGINAL.** See `constants.ALIEN_CORRODE_RATE`'s own comment - the
    # ROM's own "+1, every eligible action" was found, after everything else
    # about this gate was independently confirmed correct, to still run
    # ~1.4x hotter than the disk's own measured rate. `corrode_credit`
    # accumulates the fractional rate smoothly rather than in lumps.
    if corrode:
        alien.corrode_credit += corrode_rate
        if alien.corrode_credit >= 1.0:
            add_room_damage(
                state, alien.room_id, constants.ROOM_DAMAGE_ALIEN_PER_ACTION
            )
            alien.corrode_credit -= 1.0

    # Encounter resolution in the (possibly new) room; odds are [?]. Fear rises
    # only for crew who actually share the Alien's room (a decoded stressor,
    # DISASSEMBLY §8.9); mere adjacency does not frighten (that was an invention).
    # **DIRECTION CORRECTED (D-059).** This used to *raise* the value for
    # merely sharing a room with the Alien. The value is **composure** (high =
    # calm), and the ROM's only Alien-related site is `$4230`, which
    # **decrements** — and does so when the Alien actually *wounds* someone,
    # not on proximity alone. Applied on the wound path below instead.

    # A landed attack **wounds** rather than kills: `DEC $7D45,X`, with
    # incapacitation following only once health falls below the floor (see
    # `CrewMember.wound`).
    #
    # **[C $4152-$41F7] It is doubly random and wounds exactly one.**
    # `$4155 CMP #$07 / BCC rts` means the Alien does nothing at all on 7 of 16
    # actions; when it does act, one victim is chosen from the co-located
    # candidates. A crowded room therefore spreads the same single wound rather
    # than multiplying it. There is no "armed crew are exempt" rule — nothing on
    # this path looks at what anyone carries — though an armed crew member can
    # still fight back with their own ATTACK order.
    #
    # `alien_wound_crew ($5354)` is a misnomer and is *not* this routine: both
    # its callers pass `$64C3`, the android's slot.
    #
    # Derivation: DISCOVERIES D-177.
    if rng is None:
        return False                 # a caller with no rng cannot roll
    # Candidates first: `$413C` is only *reached* when `alien_tick ($8AD7)`
    # finds `$64A3` set, and `$8CDC` sets that when the Alien has actually met
    # crew. So an empty room never gets as far as `$4152`'s roll - collecting
    # first keeps the RNG sequence aligned with the machine's.
    candidates = [
        c for c in state.crew.values()
        if c.alive
        and c.room_id == alien.room_id
        and not c.in_duct                                   # $4189 $6501,Y
        and c.health >= constants.CREW_INCAPACITATED_BELOW  # $418E CMP #$02
    ][: constants.ALIEN_VICTIM_SLOTS]                       # $64A4-$64A6
    if not candidates:
        return False
    if rng.randrange(constants.ALIEN_ROLL_SIDES) < constants.ALIEN_ATTACK_ROLL_AT_LEAST:
        # The roll missed - but `$413C` already re-armed `$64EE` to 40
        # *before* `$4152`, so the Alien still holds the room (D-188).
        return True                                         # $4157 BCS
    if len(candidates) == 1:
        victim = candidates[0]                              # $41AA CPX #$01
    elif len(candidates) == 2:
        victim = candidates[rng.randrange(2)]               # $41B8 LSR
    else:
        roll = rng.randrange(constants.ALIEN_ROLL_SIDES)    # $41C4
        lo, hi = constants.ALIEN_VICTIM_BANDS
        victim = candidates[0 if roll < lo else 1 if roll < hi else 2]

    victim.wound(constants.ALIEN_WOUND_AMOUNT)              # $41F7 DEC $7D45,X
    # **[C $41C4 alien_attacks_crew] "ALIEN WOUNDS <crew>" - the only feedback
    # this event had before now was the `ATTACK_ALERT` sound cue below; there
    # was no text at all.** Same row-24 banner mechanism DISC-231 already
    # built for the other transient notices.
    state.notice = constants.NOTICE_ALIEN_WOUNDS.format(name=victim.name)
    state.notice_ticks = constants.NOTICE_TICKS
    # **[C $4227 `CMP #$03 / BNE $4206`] the composure hit is gated on the new
    # health being exactly 3**, not taken on every wound. So a crew member pays
    # one composure crossing out of O.K. and nothing for the wounds after it.
    # Docking every time made crews panic roughly four times too fast.
    # Derivation: DISCOVERIES DISC-270, D-059.
    if victim.health == constants.COMPOSURE_HIT_HEALTH_EXACTLY:
        victim.bump_fear(constants.COMPOSURE_HIT_ALIEN_ATTACK)
    # [C $8CD9-$8CF3] D-090: reaching the attack sequence raises the siren +
    # the five-sprite animation - but only for the *selected* character
    # (`$8CE1 CPY $64FB`). The cue is raised unconditionally here and gated at
    # presentation time by `sound.audible`.
    state.sound_cues.append(SoundCue(ATTACK_ALERT, crew_id=victim.id))
    # **[C $4292/$599E] P2-17 - the Alien carries its kill away.**
    # `alien_death_effects` stows the victim when the slot is free
    # (`$429E LDA $64DC / BNE skip`); `stow_char` parks their location at the
    # off-map sentinel `$BB`. `restore_stowed_char` puts them back later,
    # inside the ducting wherever the Alien then is.
    if not victim.alive and state.stowed_crew_id is None:
        state.stowed_crew_id = victim.id
        victim.room_id = None
    return True


def restore_stowed_char(state: GameState, alien: Alien) -> None:
    """Deposit a carried body in the ducting — **[C $59A7] P2-17**.

    `restore_stowed_char` runs only while the **Alien itself is in a duct**
    (`$59A7 LDA $6501 / BEQ rts`), scans the crew for anyone already sharing
    that duct position (`$59AE`-`$59B9` — if someone is there it waits), and
    otherwise writes the stowed character into the ducting at the Alien's own
    location (`$59C3 LDA #$01 / STA $6501,X`, `$59C8 LDA $7935 / STA $7935,X`)
    and clears the slot.

    So a body does not stay where its owner died: the Alien drags it into the
    vents and leaves it somewhere along its own route.
    """
    victim_id = state.stowed_crew_id
    if victim_id is None or not alien.in_duct or alien.room_id is None:
        return
    for other in state.crew.values():
        if other.id != victim_id and other.in_duct and other.room_id == alien.room_id:
            return                      # `$59B9 BEQ` — occupied, try later
    victim = state.crew.get(victim_id)
    if victim is None:
        state.stowed_crew_id = None
        return
    victim.room_id = alien.room_id
    victim.in_duct = True
    state.stowed_crew_id = None


def resolve_attack(
    alien: Alien, item_type_id: str | None,
    *, damage_to_kill: int = constants.ALIEN_DAMAGE_TO_KILL,
) -> AttackResult:
    """Resolve a crew member's ``ATTACK`` against the Alien (full disassembly §8.8).

    **Deterministic — there is NO RNG (corrected from the invented
    hit-chance).** `resolve_attack ($4940)` branches on the held item's id and
    wounds the Alien by a fixed, per-item amount (`constants.ITEM_ATTACK_DAMAGE`):
    the electric prod / incinerator / spanner / laser / **tracker** do **+1**
    (D-033: the tracker's "smashed" path does land a wound, corrected from an
    earlier "no wound" misread), the harpoon does **+5** guaranteed, and the
    extinguisher/cat box do **0**. Wounds accumulate on `$7D45[0]`; the Alien
    dies once they reach ``damage_to_kill`` - the ROM's own `$32` = 50 by
    default, a war of attrition. **DEC-044:** UPDATED's `Simulation` passes a
    lower, sweep-derived value instead - the weapon-breach gate means one
    room can no longer absorb a full 50-wound fight, so the number it takes
    to win had to come down with it. See `ROOM_BREACH_GATE_OTHER`'s comment
    in `constants.py` and `tools/winnability_sweep.py`, which picked it.

    **The net (D-033) is the one item with no wound but a real side effect:**
    it adds `ALIEN_NET_ENTANGLE_TICKS` to the Alien's own move timer,
    entangling it and delaying its next move — applied here directly to
    ``alien.timer`` regardless of ``hit``/``killed``.

    Returns an :class:`AttackResult`; a landed ``hit`` (damage > 0) is what spills
    acid into the room (the caller applies `ROOM_DAMAGE_PER_ATTACK` or, for the
    harpoon specifically, `ROOM_DAMAGE_PER_ATTACK_HARPOON` — the harpoon hits the
    room much harder too, D-027, §8.6). The net and the tracker are both
    consumed by this specific use (`ITEM_DESTROYED_ON_ATTACK`, D-033); the
    caller (`sim.py`) is responsible for removing the item instance.

    (Charge-check-on-attack for the laser/extinguisher — the effect that needs
    the item *instance*, not just its type — is filed for a follow-up; this
    models the wound/entangle outcome.)
    """
    if not alien.alive:
        return AttackResult(hit=False, killed=False)
    if item_type_id == "net":
        alien.timer += constants.ALIEN_NET_ENTANGLE_TICKS
        return AttackResult(hit=False, killed=False)
    damage = constants.ITEM_ATTACK_DAMAGE.get(item_type_id or "", 0)
    if damage <= 0:
        return AttackResult(hit=False, killed=False)
    alien.damage += damage
    if alien.damage >= damage_to_kill:
        alien.alive = False
        return AttackResult(hit=True, killed=True)
    return AttackResult(hit=True, killed=False)
