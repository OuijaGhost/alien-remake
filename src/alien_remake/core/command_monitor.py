"""Command Monitor data model (GAME_SPEC §6.2): Damage Reports + Weapons & Tools.

Pure, headless queries over a :class:`~alien_remake.core.map.ShipMap` and a
:class:`~alien_remake.core.state.GameState` — no rendering, so the renderer draws
whatever these return and tests can assert facts without a pygame window. The
other two Command Monitor sections need nothing new here: **TOOH** (§6.2 #4) is
and **Special Options** (§6.2 #3)
are context-dependent on the Alien/win conditions and are wired there.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import constants
from .items import ItemInstance
from .map import ShipMap
from .state import GameState


@dataclass(frozen=True)
class RoomStatus:
    """One Damage Report line: grille state, occupants, items, and hull damage."""

    room_id: str
    name: str
    grille_open: bool
    occupant_names: tuple[str, ...]
    item_ids: tuple[str, ...]
    # Structural (acid) damage now that the Alien exists: the raw accumulator and
    # its 0/1/2 stage (intact/damaged/severe), so the renderer can flash a
    # "WARNING STRUCTURAL DAMAGE" for a damaged room (full disassembly §8.6).
    damage: int = 0
    damage_stage: int = 0


@dataclass(frozen=True)
class CrewStatus:
    """One CONTROL-panel crew line: physical status + Mother's state-of-mind word."""

    crew_id: str
    name: str
    status: str   # O.K. / WOUNDED / COLLAPSED / DEAD
    morale: str   # CONFIDENT..BROKEN
    room_id: str | None


def damage_report(ship: ShipMap, state: GameState, deck: int) -> list[RoomStatus]:
    """Per-room status for every room on ``deck`` (GAME_SPEC §6.2 #1).

    Reports each room's grille, who and what is in it, and — now that the Alien's
    acid blood damages the ship (§8.6) — its structural damage + stage, so the
    Damage Report finally shows real hull damage, not just occupancy.
    """
    occupants: dict[str, list[str]] = {}
    for crew in state.crew.values():
        if crew.alive and crew.room_id is not None:
            occupants.setdefault(crew.room_id, []).append(crew.name)
    items_by_room: dict[str, list[str]] = {}
    for item in state.items.values():
        if item.room_id is not None:
            items_by_room.setdefault(item.room_id, []).append(item.id)

    reports = []
    for room in ship.rooms_on(deck):
        grille_open = any(g.room_id == room.id and g.is_open for g in ship.grilles)
        damage = state.room_damage.get(room.id, 0)
        reports.append(
            RoomStatus(
                room_id=room.id,
                name=room.name,
                grille_open=grille_open,
                occupant_names=tuple(sorted(occupants.get(room.id, ()))),
                item_ids=tuple(sorted(items_by_room.get(room.id, ()))),
                damage=damage,
                damage_stage=constants.damage_stage(damage),
            )
        )
    return reports


def structural_warnings(ship: ShipMap, state: GameState) -> list[RoomStatus]:
    """Every damaged room across the whole ship, worst first (the game's
    "WARNING STRUCTURAL DAMAGE TO <room>" messages, §8.6). Empty when intact."""
    warned = [
        RoomStatus(
            room_id=room.id,
            name=room.name,
            grille_open=False,
            occupant_names=(),
            item_ids=(),
            damage=dmg,
            damage_stage=constants.damage_stage(dmg),
        )
        for room in ship.rooms.values()
        if (dmg := state.room_damage.get(room.id, 0)) > 0
    ]
    warned.sort(key=lambda r: (-r.damage, r.room_id))
    return warned


def crew_status(state: GameState) -> list[CrewStatus]:
    """The CONTROL-panel crew lines: each crew member's physical status and
    Mother's state-of-mind word (GAME_SPEC §5/§6.2), in the roster order."""
    return [
        CrewStatus(
            crew_id=c.id,
            name=c.name,
            status=c.status,
            morale=c.morale,
            room_id=c.room_id,
        )
        for c in state.crew.values()
    ]


def items_in_room(state: GameState, room_id: str) -> list[ItemInstance]:
    """Items currently lying in ``room_id`` (GAME_SPEC §6.2 #2, Weapons & Tools)."""
    return sorted(
        (item for item in state.items.values() if item.room_id == room_id),
        key=lambda item: item.id,
    )


#: **[C $8C5B CMP #$02] DISC-246** — the Alien passes over anyone already down.
ATTACK_MIN_HEALTH = 2


def crew_with_alien(state: GameState) -> str | None:
    """The crew member the Alien has found, or ``None``.

    **[C find_crew_with_alien $8C49] DISC-246.** Walks slots 1-7 and returns the
    **first** that satisfies all three tests::

        $8C4B  LDA $7935,Y / CMP $7935   same room as the Alien (slot 0)
        $8C53  LDA $6501,Y / CMP $6501   **same space** - both surfaced, or
                                         both in the ducts
        $8C5B  LDA $7D45,Y / CMP #$02    health >= 2; already-down crew are
               BCC skip                  passed over

    Two of those are easy to get subtly wrong. The duct test is a *comparison
    between the two flags*, not "the Alien is surfaced": an Alien in the vents
    finds a crew member in the vents, and ignores one standing in the room. And
    the scan stops at the first match, so with two people in the room the Alien
    is only ever engaging the lower-numbered one — which is what `$8CE1
    CPY $64FB` then tests the selected character against.

    Returns the crew id rather than a slot so callers do not have to know the
    roster's ordering; ``None`` is the ROM's ``Y == 8``.
    """
    alien = state.alien
    if alien is None or not alien.alive or alien.room_id is None:
        return None
    for crew in state.crew.values():          # roster order == slot order
        if not crew.alive:
            continue
        if crew.room_id != alien.room_id:     # $8C4E
            continue
        if crew.in_duct != alien.in_duct:     # $8C56 — same space, not "surfaced"
            continue
        if crew.health < ATTACK_MIN_HEALTH:   # $8C5E/$8C60
            continue
        return crew.id
    return None
