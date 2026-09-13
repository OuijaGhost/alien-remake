"""Nostromo ship topology for the remake (headless, stdlib only).

The ship is **decks** → **rooms** connected by **doors**, plus a separate
**ducting** network of **junctions** connected by vents; **grilles** gate access
between a room and the duct network and can be opened (`REMOVE GRILL`, GAME_SPEC
§3, §5). Pure data + queries; no rendering.

The exact layout is a calibration `[?]` (GAME_SPEC §11 #4): :func:`default_ship`
is a faithful *starter* topology expressed as data. As of SM the live map is the
oracle-transcribed :func:`~alien_remake.core.nostromo.nostromo_ship`;
``default_ship`` remains the documented fallback.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class Direction(Enum):
    """Cursor / movement directions on a deck grid."""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)


@dataclass(frozen=True)
class Room:
    """A room on a deck, placed at integer grid coords for the map view."""

    id: str
    deck: int
    name: str
    x: int
    y: int
    # Whether this room is one of the ship's airlocks. From the disassembly: the real
    # game has exactly two (AIRLOCK 1 / AIRLOCK 2), targeted by the BLOW LOCK /
    # SEAL LOCK specials and the blast-out-the-airlock win route.
    is_airlock: bool = False
    # The Narcissus' bay (real id 34, SHUTTLEBAY): where LAUNCH NARCISSUS
    # collects the survivors. Distinct from the airlocks in the real game.
    is_evac_bay: bool = False
    # Real compass exits ("north"/"south"/"east"/"west" -> room id), straight
    # from the game's neighbor tables. Empty for synthetic ships (default_ship)
    # — movement falls back to door adjacency there.
    exits: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Junction:
    """A duct junction (vent meeting point) on a deck."""

    id: str
    deck: int
    x: int
    y: int


@dataclass
class Grille:
    """A room's removable grille — the gate onto the duct network.

    **[C $8676] P-1:** the original keeps one flag per *room*, not a link to a
    junction; `junction_id` is optional scaffolding for the synthetic test maps
    that predate the real topology being decoded. On the real ship a grille
    belongs to a room, and where the ducts then lead is
    :meth:`ShipMap.duct_exits`.
    """

    room_id: str
    junction_id: str | None = None
    is_open: bool = False


def _key(a: str, b: str) -> tuple[str, str]:
    """Order-independent key for an undirected edge."""
    return (a, b) if a <= b else (b, a)


@dataclass
class ShipMap:
    """The whole ship: rooms, junctions, doors, ducts and grilles.

    ``doors`` and ``ducts`` are undirected adjacency stored as sorted-pair keys;
    use the query helpers rather than touching them directly.
    """

    rooms: dict[str, Room] = field(default_factory=dict)
    junctions: dict[str, Junction] = field(default_factory=dict)
    doors: set[tuple[str, str]] = field(default_factory=set)
    ducts: set[tuple[str, str]] = field(default_factory=set)
    grilles: list[Grille] = field(default_factory=list)

    # --- construction -------------------------------------------------------
    def add_room(self, room: Room) -> None:
        self.rooms[room.id] = room

    def add_junction(self, junction: Junction) -> None:
        self.junctions[junction.id] = junction

    def add_door(self, room_a: str, room_b: str) -> None:
        """Connect two rooms with a door (both must exist)."""
        if room_a not in self.rooms or room_b not in self.rooms:
            raise KeyError("door references an unknown room")
        self.doors.add(_key(room_a, room_b))

    def add_duct(self, junction_a: str, junction_b: str) -> None:
        """Connect two junctions with a vent (both must exist)."""
        if junction_a not in self.junctions or junction_b not in self.junctions:
            raise KeyError("duct references an unknown junction")
        self.ducts.add(_key(junction_a, junction_b))

    def add_grille(self, room_id: str, junction_id: str | None = None) -> Grille:
        """Add a (closed) grille to ``room_id``.

        ``junction_id`` is only for synthetic test maps built on the old
        junction model; the real ship passes nothing (P-1).
        """
        if room_id not in self.rooms:
            raise KeyError("grille references an unknown room")
        if junction_id is not None and junction_id not in self.junctions:
            raise KeyError("grille references an unknown junction")
        g = Grille(room_id, junction_id)
        self.grilles.append(g)
        return g

    # --- queries ------------------------------------------------------------
    #: **[C $758B] DISC-244.** `tbl_room_deck` gives the Narcissus deck **3**,
    #: one past Upper/Middle/Lower. It is a sentinel meaning "on no deck plan",
    #: not a fourth deck: the ROM's CONTROL list has exactly three deck rows
    #: (13-15, DISC-232) and there is no plan to draw for it.
    SENTINEL_DECK = 3

    def decks(self) -> list[int]:
        """The selectable decks — those with a deck plan — ascending.

        Excludes :data:`SENTINEL_DECK`. Including it put a fourth entry on the
        CONTROL panel's three-row deck list.
        """
        return sorted(
            {r.deck for r in self.rooms.values() if r.deck != self.SENTINEL_DECK}
        )

    def rooms_on(self, deck: int) -> list[Room]:
        """Rooms on a deck, ordered by (y, x) for a stable map layout."""
        return sorted(
            (r for r in self.rooms.values() if r.deck == deck),
            key=lambda r: (r.y, r.x),
        )

    def door_neighbors(self, room_id: str) -> list[str]:
        """Rooms reachable from ``room_id`` through a single door."""
        out = [b for (a, b) in self.doors if a == room_id]
        out += [a for (a, b) in self.doors if b == room_id]
        return sorted(out)

    def duct_neighbors(self, junction_id: str) -> list[str]:
        """Junctions reachable from ``junction_id`` through one vent.

        **The junction model is an invention** — kept only for the synthetic
        test maps that were built on it. The original has no junction nodes at
        all; see :meth:`duct_exits` for what the ROM actually does.
        """
        out = [b for (a, b) in self.ducts if a == junction_id]
        out += [a for (a, b) in self.ducts if b == junction_id]
        return sorted(out)

    def duct_exits(self, room_id: str) -> dict[str, str]:
        """Where the ducts lead from ``room_id`` — **[C, D-083]**.

        The real duct network connects **rooms directly**, one table per compass
        direction: `$80F5` (N), `$8117` (E), `$8139` (S), `$815B` (W), each
        holding one neighbour room id per room. A **self-reference means "no
        duct exit that way"**, which is how the ROM encodes a dead end.

        The direction assignment is not guessed: `$40B8`-`$40FA` tests a
        character's room against each table in turn and prints the matching word
        from the `$8080` block (" NORTH " / " EAST " / " SOUTH " / " WEST "). The
        same four tables drive the in-duct MOVE TO menu (`$81EF`-`$8271`) and the
        Alien's duct hops (`$8AA2`-`$8ACB`).

        Returns ``{}`` for a room outside the real 34 (synthetic test maps).
        """
        from .gamedata_snapshot import (
            DUCT_DIRECTIONS,
            DUCT_NEIGHBOURS,
            ROOM_SLUGS,
        )

        try:
            idx = ROOM_SLUGS.index(room_id)
        except ValueError:
            return {}
        out: dict[str, str] = {}
        for d, table in zip(DUCT_DIRECTIONS, DUCT_NEIGHBOURS):
            if idx >= len(table):
                continue
            dest = table[idx]
            if dest == idx or dest >= len(ROOM_SLUGS):
                continue                       # self-reference = no exit
            out[d] = ROOM_SLUGS[dest]
        return out

    def grille_between(self, room_id: str, junction_id: str) -> Grille | None:
        for g in self.grilles:
            if g.room_id == room_id and g.junction_id == junction_id:
                return g
        return None

    def open_grille(self, room_id: str, junction_id: str) -> bool:
        """Open the grille between a room and junction; True if one was found."""
        g = self.grille_between(room_id, junction_id)
        if g is None:
            return False
        g.is_open = True
        return True

    def duct_access(self, room_id: str) -> list[str]:
        """Junctions a body can enter from ``room_id`` (via an *open* grille).

        Only meaningful on synthetic test maps built with the junction model;
        the real ship has no junctions (P-1) and uses :meth:`duct_exits`.
        """
        return sorted(
            g.junction_id
            for g in self.grilles
            if g.room_id == room_id and g.is_open and g.junction_id is not None
        )

    def airlock_rooms(self) -> list[str]:
        """Ids of every room flagged as an airlock, sorted."""
        return sorted(r.id for r in self.rooms.values() if r.is_airlock)

    def evac_rooms(self) -> list[str]:
        """Where LAUNCH NARCISSUS collects the survivors: the evac bay(s).

        The real ship's SHUTTLEBAY (later RE). Synthetic ships that predate
        the flag (``default_ship``) fall back to their airlocks, which the Alien work had
        conflated with the evac bay.
        """
        evac = sorted(r.id for r in self.rooms.values() if r.is_evac_bay)
        return evac or self.airlock_rooms()


def _composite_neighbors(ship: ShipMap) -> Callable[[str], list[str]]:
    """Build the shared room+junction neighbor function: doors between rooms,
    plus duct travel through *open* grilles only. Both crew movement
    (``shortest_room_path``) and the Alien's sensing/movement (``rooms_reachable_from``) walk this same composite graph.
    """
    rooms_from_junction: dict[str, list[str]] = {}
    for g in ship.grilles:
        if g.is_open and g.junction_id is not None:
            rooms_from_junction.setdefault(g.junction_id, []).append(g.room_id)

    def neighbors(node: str) -> list[str]:
        if node in ship.rooms:
            return ship.door_neighbors(node) + ship.duct_access(node)
        return ship.duct_neighbors(node) + rooms_from_junction.get(node, [])

    return neighbors


def rooms_reachable_from(ship: ShipMap, start_room: str) -> dict[str, int]:
    """Room-hop BFS distances from ``start_room`` (junctions collapsed out).

    Includes ``start_room`` itself at distance 0. Same composite door+open-duct
    graph as :func:`shortest_room_path`, but returns every reachable room's
    distance rather than a path to one destination — what the Alien's sensing
    model (GAME_SPEC §11 #2) needs to find the *nearest* crew member.
    """
    if start_room not in ship.rooms:
        return {}
    neighbors = _composite_neighbors(ship)
    dist: dict[str, int] = {start_room: 0}
    queue: list[str] = [start_room]
    while queue:
        node = queue.pop(0)
        for nxt in neighbors(node):
            if nxt in dist:
                continue
            dist[nxt] = dist[node] + (1 if nxt in ship.rooms else 0)
            queue.append(nxt)
    return {r: d for r, d in dist.items() if r in ship.rooms}


def shortest_room_path(
    ship: ShipMap, start_room: str, goal_room: str
) -> list[str] | None:
    """Shortest room-to-room path over the composite crew-movement graph.

    Crew travel through **doors** and, where a **grille is open**, through the
    **duct** network (room → junction → … → junction → room). This BFS walks
    both room and junction nodes but returns only the **rooms** visited from
    ``start_room`` to ``goal_room`` inclusive (junctions collapsed out), or
    ``None`` if no such path exists. Removing a grille (``open_grille``) can thus
    shorten or unlock a route — the reason ``REMOVE_GRILL`` matters for movement
    (GAME_SPEC §3, §5).
    """
    if start_room not in ship.rooms or goal_room not in ship.rooms:
        return None
    if start_room == goal_room:
        return [start_room]

    neighbors = _composite_neighbors(ship)
    prev: dict[str, str | None] = {start_room: None}
    queue: list[str] = [start_room]
    while queue:
        node = queue.pop(0)
        if node == goal_room:
            break
        for nxt in neighbors(node):
            if nxt not in prev:
                prev[nxt] = node
                queue.append(nxt)

    if goal_room not in prev:
        return None
    # Reconstruct, keeping only room nodes.
    chain: list[str] = []
    cur: str | None = goal_room
    while cur is not None:
        if cur in ship.rooms:
            chain.append(cur)
        cur = prev[cur]
    chain.reverse()
    return chain


def move_cursor(
    ship: ShipMap, deck: int, x: int, y: int, direction: Direction
) -> tuple[int, int]:
    """Move a map cursor one step, clamped to the deck's room bounding box.

    Returns the new ``(x, y)``. With no rooms on the deck the cursor does not
    move. The cursor is a free grid pointer (it is not constrained to land on a
    room), matching the original's "move the cursor to watch crew".
    """
    rooms = ship.rooms_on(deck)
    if not rooms:
        return (x, y)
    dx, dy = direction.value
    nx, ny = x + dx, y + dy
    xs = [r.x for r in rooms]
    ys = [r.y for r in rooms]
    nx = max(min(xs), min(max(xs), nx))
    ny = max(min(ys), min(max(ys), ny))
    return (nx, ny)


def default_ship() -> ShipMap:
    """A synthetic 3-deck starter Nostromo — **test scaffolding only**.

    **PV-23 closed 2026-08-07 (D-179).** The note asked whether anything
    outside the tests still reaches for this fallback. Nothing does: a scan of
    `src/` finds **no call site at all** (only prose references), because
    `Simulation` defaults to `nostromo.nostromo_ship(mode)`, the
    oracle-transcribed real map. Kept because five tests build deliberately
    tiny maps with it, but it is **not** a claim about the ship and nothing
    should read it as one.
    

    Deck 0 (top): bridge area; Deck 1 (mid): living/medical; Deck 2 (lower):
    engineering. Each deck's rooms are linked by doors; a duct network of
    junctions spans the decks with a grille into one room per deck.
    """
    m = ShipMap()
    layout: dict[int, list[tuple[str, str, int, int]]] = {
        0: [("bridge", "Bridge", 1, 0), ("nav", "Navigation", 0, 0),
            ("comms", "Comms", 2, 0)],
        1: [("galley", "Galley", 0, 1), ("med", "Medical", 1, 1),
            ("quarters", "Crew Quarters", 2, 1)],
        2: [("engine", "Engine Room", 1, 2), ("airlock", "Airlock", 0, 2),
            ("cargo", "Cargo Bay", 2, 2)],
    }
    for deck, rooms in layout.items():
        for rid, name, x, y in rooms:
            # "airlock" doubles as the ship's one airlock/evac bay:
            # blast-the-Alien and evacuate-via-Narcissus both target it.
            m.add_room(Room(rid, deck, name, x, y, is_airlock=(rid == "airlock")))
        m.add_junction(Junction(f"j{deck}", deck, 1, deck))
    # Doors within each deck (a simple chain).
    for deck, rooms in layout.items():
        ids = [r[0] for r in rooms]
        for a, b in zip(ids, ids[1:]):
            m.add_door(a, b)
    # Vertical duct spine + one grille per deck into a central room.
    m.add_duct("j0", "j1")
    m.add_duct("j1", "j2")
    for deck, room_id in ((0, "bridge"), (1, "med"), (2, "engine")):
        m.add_grille(room_id, f"j{deck}")
    return m
