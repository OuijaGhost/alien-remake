"""The real item set, decoded from the game's own tables (later RE).

An :class:`ItemType` is one catalog entry (id, the game's own display name,
kind, and how many exist); an :class:`ItemInstance` is one physical item,
located either in a room or carried by a crew member (mutually exclusive).
``GameState.items`` holds every instance keyed by its id;
:mod:`alien_remake.core.sim` applies ``GET_ITEM`` / ``LEAVE_ITEM`` orders
against it, and :mod:`alien_remake.core.command_monitor` reads it for the
Weapons & Tools section.

Provenance: the catalog and every instance's **fixed starting room** come from
the item tables at ``$82CF``/``$82E3`` and the name table at ``$7C7D`` in
``ALIEN.prg`` (via :mod:`alien_remake.core.gamedata_snapshot`; evidence in
``docs/re/GAMEDATA.md``). This corrected two inventions: the manual's
"taser" is really the game's **LASER PISTOL** (the manual's counts were
otherwise exactly right — 20 items), and placement was never shuffled — e.g.
the three laser pistols always start in the ARMOURY. A tenth type,
THERMLANCE, exists in the name table but has no spawned instance. Per-item
consumable state ("...S LASER IS EXAUSTED" / "...S EXTINGUISHER IS EMPTY" /
"...S TRACKER IS SMASHED", the game's `$4B37` charge) is now modelled via
``ItemInstance.uses_left`` (charges in ``constants.CONSUMABLE_USES``); the
per-item USE *effects* are dispatched in :mod:`alien_remake.core.sim`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import constants
from . import gamedata_snapshot as data
from .map import ShipMap


class ItemKind(Enum):
    """Rough category, for grouping in the Weapons & Tools UI (GAME_SPEC §10)."""

    WEAPON = "Weapon"
    TOOL = "Tool"
    UTILITY = "Utility"


@dataclass(frozen=True)
class ItemType:
    """One catalog entry: the game's name for it, its kind, and how many exist."""

    id: str
    name: str
    kind: ItemKind
    count: int


def _slug(name: str) -> str:
    return "_".join(name.lower().split())


# Kind classification is presentation-only; ids/names/counts are [C].
# **PV-18 closed 2026-08-07 (D-179):** verified rather than assumed - a
# grep for `.kind` / `ItemKind.` outside this module finds **no consumers
# at all**, so nothing gates on the grouping and it cannot skew behaviour.
# (The ROM's own per-item behaviour is dispatched on the *instance index*
# in `resolve_attack ($498D)`, D-154, not on any category.)
_KINDS: dict[int, ItemKind] = {
    1: ItemKind.WEAPON,   # ELCTRC PRD
    2: ItemKind.WEAPON,   # INCINERATR
    3: ItemKind.UTILITY,  # TRACKER
    4: ItemKind.UTILITY,  # FIRE EXTNG
    5: ItemKind.WEAPON,   # HARPN GUN
    6: ItemKind.WEAPON,   # LASER PIST
    7: ItemKind.TOOL,     # NET
    8: ItemKind.UTILITY,  # CAT BOX
    9: ItemKind.TOOL,     # SPANNER
    10: ItemKind.WEAPON,  # THERMLANCE (no spawned instance)
}

ITEM_CATALOG: tuple[ItemType, ...] = tuple(
    ItemType(
        id=_slug(name),
        name=name,
        kind=_KINDS[type_id],
        count=sum(1 for _, t, _r in data.ITEMS if t == type_id),
    )
    for type_id, name in enumerate(data.ITEM_TYPE_NAMES, start=1)
)

ITEM_TYPES: dict[str, ItemType] = {t.id: t for t in ITEM_CATALOG}


@dataclass
class ItemInstance:
    """One physical item: which catalog entry it is, and where it currently is.

    Exactly one of ``room_id`` / ``holder`` is set once the item has been placed
    (``room_id`` at spawn; ``GET_ITEM``/``LEAVE_ITEM`` flip it to ``holder`` and
    back, see :mod:`alien_remake.core.sim`).
    """

    id: str
    type_id: str
    room_id: str | None
    holder: str | None = None
    # Remaining uses for a charge-based item (the game's `$4B37`, decoded FV-1.1:
    # LASER PIST = 10, FIRE EXTNG = 3, HARPN GUN = 1), or ``None`` for an item that
    # is not charge-based. Exhausting a charge drives the "…IS EXAUSTED/EMPTY"
    # state. FV-1.5: the TRACKER is correctly NOT charge-based (`uses_left=None`) —
    # its motion-reading USE is unlimited; the "TRACKER IS SMASHED" ($4B22) event
    # only fires when you *attack* with it ($49B5, the ATTACK path). **Wired in
    # (D-033, 2026-07-24):** that destroy-on-attack (plus the net's, same
    # mechanism) is now handled in `sim.py`'s `_resolve_attack_order` via
    # `constants.ITEM_DESTROYED_ON_ATTACK` — outside this charge model, since
    # it's an outright removal, not a decrementing counter.
    uses_left: int | None = None

    @property
    def exhausted(self) -> bool:
        """True for a consumable that has run out (can no longer be USEd)."""
        return self.uses_left is not None and self.uses_left <= 0


def spawn_items(ship: ShipMap) -> dict[str, ItemInstance]:
    """Place the 20 real item instances in their fixed starting rooms.

    Placement is table-derived, not random — the shuffled round-robin the
    remake used before the decompile audit is gone. Items whose real room
    doesn't exist on ``ship`` (synthetic test maps) are left unplaced.
    """
    counters: dict[str, int] = {}
    items: dict[str, ItemInstance] = {}
    for _index, type_id, room in data.ITEMS:
        type_slug = _slug(data.ITEM_TYPE_NAMES[type_id - 1])
        counters[type_slug] = counters.get(type_slug, 0) + 1
        iid = f"{type_slug}_{counters[type_slug]}"
        room_slug = data.ROOM_SLUGS[room]
        items[iid] = ItemInstance(
            id=iid,
            type_id=type_slug,
            room_id=room_slug if room_slug in ship.rooms else None,
            uses_left=constants.CONSUMABLE_USES.get(type_slug),
        )
    return items
