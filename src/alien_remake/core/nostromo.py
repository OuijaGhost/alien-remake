"""The Nostromo topology, decoded from the game's own map tables (later RE).

Provenance — this replaces two generations of approximation
--------------------------------------------------------------
A placeholder ship was invented first (:func:`~alien_remake.core.map.default_ship`);
SM transcribed deck grids by eye from screenshots. Both are superseded: the
real map lives in ``ALIEN.prg`` itself — a 34-room graph with per-room deck
assignment, four compass-neighbor tables (N/S/E/W; "no exit" encoded as a
self-loop), and a per-room grille table, all decoded by
``alientools.gamedata`` (addresses + evidence in ``docs/re/GAMEDATA.md``) and
snapshotted into :mod:`alien_remake.core.gamedata_snapshot` so the remake runs
without the disk image present.

Facts carried over verbatim from the tables:

* 35 named locations; ids 0-33 are the deck-mapped rooms (SHUTTLEBAY/32 and
  SHTTLSTORE/33 among them, ordinary rooms with real doors — corrected by
  D-123, this note was stale before that fix). Only **34, NARCISSUS**, is off
  the deck plans. It **does** have a `$7569` entry — `$758B` is **3**, one past
  the three real decks (DISC-244; the previous claim that it had none was
  wrong). Its position is placed relative to its one real door, from
  SHUTTLEBAY (`SURFACE_EXITS[32]`, D-136).
* Decks split **9/16/9** over the 34 mapped rooms, plus the Narcissus alone on
  the sentinel deck 3 (counted from `$7569` itself, DISC-244). The "10/14/10"
  this line used to claim came from the superseded `$80D3` reading that D-116
  replaced, and survived that correction; 0=Upper, 1=Middle, 2=Lower.
  **Confirmed live** (2026-07-11, user-assisted INDICATE LOCATION
  screenshots — this stale ``[?]`` was left over from before that work
  and corrected here, D-036 de-invention audit, 2026-07-24; see
  ``DECK_NAMES``/``_RAW_DECKS`` below for the full citation).
* Cross-deck edges are the deck plan's ladders ("LADDER UP/DOWN" in the game's
  own key text).
* Every room has a grille except CORRIDOR 6.

**Corrected 2026-08-02 (P-1 / D-086): the compass tables are the DUCT network,
not the doors.** `$779C` picks the "move to" menu on the in-duct flag — a
character on the surface gets `$7860`'s list, built from the five **routing**
tables (`SURFACE_EXITS`), while one inside a duct gets `$81EF`'s, built from the
compass tables. This module used to wire every compass neighbour as a door,
which is why crew could walk between rooms that are not connected; the two
graphs disagree for 31 of 34 rooms. Doors now come from `SURFACE_EXITS` and the
duct graph is `ShipMap.duct_exits()`. The old `Junction` wiring is gone.

**2026-08-06 (D-136): the SHUTTLEBAY docking note above is retired.** SHUTTLEBAY
is an ordinary mapped room reached the same way as any other, through
``SURFACE_EXITS`` (D-123 already established this; the invented AIRLOCK-2 door
this note used to describe was never removed alongside it, and
``SURFACE_EXITS[1]`` disproves it outright — AIRLOCK 2's only real exit is
CORRIDOR 6). NARCISSUS's own door to SHUTTLEBAY was never invented either; it
is simply the real ``SURFACE_EXITS[32]`` entry the generic door-building loop
already wires.

Still approximate (documented, not table-derived):
* On-screen (x, y) placement: computed by a BFS layout over the compass
  edges — the real per-deck pixel layout lives in the game's screen data and
  is not decoded; positions here only drive the fallback renderer/markers.
"""

from __future__ import annotations

from . import gamedata_snapshot as data
from .map import Grille, Room, ShipMap
from .modes import GameMode

# Raw deck byte -> (deck index, display name). 4=Upper/5=Middle/6=Lower is
# [C-live] (2026-07-11): confirmed via live INDICATE LOCATION reads —
# room 0 (AIRLOCK 1, raw 4) displayed under "UPPER DECK"; room 6 (COMMDCENTR,
# raw 5) under "MIDDLE DECK" (also independently confirmed by the 10/14/10
# room-count match against GAMEDATA.md's deck table). See docs/re/GAMEDATA.md.
DECK_NAMES: dict[int, str] = {0: "Upper Deck", 1: "Middle Deck", 2: "Lower Deck"}
# **[C $7569] D-116, applied 2026-08-08.** The deck byte is now $7569's own
# 0/1/2, so this is the identity. It used to translate $80D3's 4/5/6, which were
# duct-map screen *pages*, not decks.
_RAW_DECKS: dict[int, int] = {0: 0, 1: 1, 2: 2}

_DIRECTIONS = ("north", "south", "east", "west")
_OFFSETS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}

# Off-map rooms (the Narcissus). SHUTTLEBAY doubles as the evacuation bay the
# LAUNCH NARCISSUS special needs everyone aboard for.
# **[C $7948] D-123 — the room ids shifted when the name-table gap was found.**
# A flat read of `$A71C` invented two "OTHER LIST" rooms at 17/18 and pushed
# everything after them up by two. With the gap honoured there are **35** rooms
# (0-34): SHUTTLEBAY is **32**, SHTTLSTORE **33**, and **34 is NARCISSUS** —
# which is also why `$5776` puts LAUNCH NARCISSUS on room 34.
SHUTTLEBAY = data.ROOM_SLUGS[32]
SHTTLSTORE = data.ROOM_SLUGS[33]
#: **[C $758B] DISC-244 — the Narcissus's deck is 3, and that is the point.**
#: `tbl_room_deck ($7569)` runs 35 entries, not the 34 the duct map needs, and
#: its last one is `03` — one past Upper/Middle/Lower. Nothing can match it,
#: because `$64F7`'s deck is only ever 0-2 for a crew member aboard the ship.
#:
#: That sentinel is load-bearing. `update_item_sprite ($7C3D)` reads the target
#: room's deck, compares it with the acting character's
#: (`CMP $4BEF / BEQ $7C5D`), and on a mismatch writes **`$D002 = 0`** — parking
#: the location pointer off the left edge instead of positioning it. So
#: highlighting NARCISSUS in "move to:" shows no marker box, which is what the
#: deck-3 entry buys.
#:
#: The remake used to give it `shuttlebay_room.deck` (2), so the box appeared.
NARCISSUS_DECK = 3

NARCISSUS = data.ROOM_SLUGS[34]


def room_display_name(slug: str) -> str:
    """The game's own 10-char display name for a room slug."""
    return data.ROOM_NAMES[data.ROOM_SLUGS.index(slug)]


def _layout_deck(room_ids: list[int], exits: dict[int, dict[str, int]]) -> dict[int, tuple[int, int]]:
    """Best-effort (x, y) per room from the compass edges (same deck only).

    BFS from the deck's first room, stepping N/S/E/W offsets; a collision
    probes outward on x until a free cell is found. Cosmetic only — the map
    view's real art is the captured backdrop; these coordinates just place
    markers and the fallback grid.
    """
    pos: dict[int, tuple[int, int]] = {}
    taken: set[tuple[int, int]] = set()
    for start in room_ids:
        if start in pos:
            continue
        pos[start] = _free_cell((0, len(taken) and (max(y for _, y in taken) + 2) or 0), taken)
        taken.add(pos[start])
        queue = [start]
        while queue:
            cur = queue.pop(0)
            cx, cy = pos[cur]
            for direction, dest in exits[cur].items():
                if dest not in exits or dest in pos or dest == cur:
                    continue  # off-deck, placed, or self
                dx, dy = _OFFSETS[direction]
                cell = _free_cell((cx + dx, cy + dy), taken)
                pos[dest] = cell
                taken.add(cell)
                queue.append(dest)
    # Normalize to non-negative coords.
    min_x = min(x for x, _ in pos.values())
    min_y = min(y for _, y in pos.values())
    return {r: (x - min_x, y - min_y) for r, (x, y) in pos.items()}


def _free_cell(cell: tuple[int, int], taken: set[tuple[int, int]]) -> tuple[int, int]:
    x, y = cell
    while (x, y) in taken:
        x += 1
    return (x, y)


def nostromo_ship(mode: GameMode = GameMode.FULL) -> ShipMap:
    """Build the real Nostromo from the decoded tables.

    ``mode`` does not change the topology: the "short mode drops a deck" reading
    was a guess, and nothing in the decoded data supports a different map for
    the SHORT SCENARIO.

    **PV-21 closed 2026-08-07 (D-169) - this note was stale.** It said the
    SHORT SCENARIO's differences were "entirely ``[?]``", which was true when
    FV-1.9 removed the invented oxygen budget but was superseded by **D-085**:
    `$604F` overwrites the randomised opening with a **scripted** one - victim
    pinned to KANE, android to ASH, four 7-entry tables copied over the crew
    arrays, DALLAS and BRETT started inside the ducts, and a tracker, the net
    and the cat box pulled into COMMD CENTR. All of it is decoded, extracted
    into ``gamedata_snapshot.SHORT_SCENARIO``/``SHORT_ITEM_MOVES`` and applied
    by :meth:`Simulation._apply_short_scenario`. What remains true is only the
    narrow claim this function makes: the **topology** is mode-independent.
    """
    del mode  # topology is mode-independent (see docstring)
    m = ShipMap()

    slugs = data.ROOM_SLUGS
    exits_by_id: dict[int, dict[str, int]] = {}
    deck_of: dict[int, int] = {}
    grille_of: dict[int, bool] = {}
    for room_id, deck_raw, n, s, e, w, grille in data.ROOMS:
        compass = dict(zip(_DIRECTIONS, (n, s, e, w)))
        exits_by_id[room_id] = {
            d: t for d, t in compass.items() if t != room_id
        }
        # **[C $7569 vs $80D3] P3-5/P3-6, corrected 2026-08-02 (D-116).**
        # The deck came from `$80D3`, which is NOT a deck table — it is the
        # **high byte of the room marker's screen address** (`$81C9 LDA
        # $80D3,Y -> $FC`), and its 4/5/6 values are screen pages, not decks.
        # The real per-room screen index is **`$7569`**, which `$76BB` reads on
        # the INDICATE path to pick which of the three deck plans to draw
        # (`init_menu_ptr` / `init_ptr_menu2` / `init_ptr_menu3`).
        #
        # Decisive check: place each room's marker (`$80B1`/`$80D3`) on the
        # deck template `$7569` selects and it lands on that plan's GRILLE
        # glyph `$E6` for **31 of 34** rooms; doing the same with `$80D3` as
        # the deck scores **12 of 34**, i.e. chance. The three deck plans carry
        # 9/16/9 grille glyphs, matching `$7569`'s 9/16/9 room split exactly —
        # not `$80D3`'s 10/14/10.
        deck_of[room_id] = data.DUCT_MAP_ROOM_TEMPLATE[room_id]
        grille_of[room_id] = bool(grille)

    # Per-deck cosmetic layout over the same-deck subgraph.
    coords: dict[int, tuple[int, int]] = {}
    for deck in (0, 1, 2):
        ids = [r for r, d in deck_of.items() if d == deck]
        same_deck_exits = {
            r: {d: t for d, t in exits_by_id[r].items() if deck_of.get(t) == deck}
            for r in ids
        }
        coords.update(_layout_deck(ids, same_deck_exits))

    for room_id in exits_by_id:
        x, y = coords[room_id]
        m.add_room(
            Room(
                id=slugs[room_id],
                deck=deck_of[room_id],
                name=data.ROOM_NAMES[room_id],
                x=x,
                y=y,
                is_airlock=room_id in (0, 1),  # AIRLOCK 1 / AIRLOCK 2 (real)
                # NB these are the **compass** exits, which P-1 established are
                # the DUCT network, not the walkable doors. Kept direction-keyed
                # because the in-duct menu is the only place directions appear;
                # surface walking uses `door_neighbors` (SURFACE_EXITS).
                exits={d: slugs[t] for d, t in exits_by_id[room_id].items()},
            )
        )

    # The Narcissus (off the deck maps). **[C $7935 row 32] P5-1/P5-2, D-136.**
    # D-123: only NARCISSUS (34) is off the deck plans now — SHUTTLEBAY (32)
    # and SHTTLSTORE (33) are ordinary mapped rooms with their own real
    # `$7569` deck, which the flat-table error had pushed out of range. Its
    # position and deck are placed relative to **SHUTTLEBAY**, its one real
    # connection (below) — not AIRLOCK 2, which `SURFACE_EXITS[1] = (13,)`
    # shows has no such door at all (see the removed invented edge below).
    shuttlebay_room = m.rooms[SHUTTLEBAY]
    for off_id, off_x in ((34, shuttlebay_room.x + 1),):
        m.add_room(
            Room(
                id=slugs[off_id],
                deck=NARCISSUS_DECK,
                name=data.ROOM_NAMES[off_id],
                x=off_x,
                y=shuttlebay_room.y + 1,
                is_evac_bay=(off_id == 34),  # NARCISSUS is the evac craft
            )
        )
    # **REMOVED (D-136): `m.add_door(slugs[1], SHUTTLEBAY)` — invented.**
    # `SURFACE_EXITS[1]` (AIRLOCK 2) is `(13,)` — CORRIDOR 6 only, never
    # SHUTTLEBAY. The real SHUTTLEBAY<->NARCISSUS door isn't invented at all:
    # `SURFACE_EXITS[32] = (33, 34, 4, 16)` already lists room 34 (NARCISSUS)
    # as a direct neighbour, so the generic SURFACE_EXITS loop below wires it
    # for free once NARCISSUS exists as a room. `m.add_door(SHUTTLEBAY,
    # SHTTLSTORE)` is likewise now redundant with that same loop (33 is also
    # in SHUTTLEBAY's real exit list) and is dropped rather than left as a
    # confusing duplicate.

    # **[C $7860] P-1 — DOORS come from the ROUTING tables, not the compass
    # tables.** `$779C` picks the "move to" menu on the in-duct flag: a
    # character on the surface gets `$7860`'s list, built from the five routing
    # tables; one inside a duct gets `$81EF`'s, built from the compass tables.
    # This module used to wire every *compass* neighbour as a door, which is the
    # duct graph — the two disagree for 31 of 34 rooms (D-086), and it let crew
    # walk between rooms that are not connected. `SURFACE_EXITS` is the game's
    # own menu, reproduced by `alientools.gamedata.surface_exits`.
    for room_id in exits_by_id:
        if room_id >= len(data.SURFACE_EXITS):
            continue
        for dest in data.SURFACE_EXITS[room_id]:
            if dest < len(slugs) and dest != room_id:
                m.add_door(slugs[room_id], slugs[dest])

    # Grilles are per-room ([C $8676]); where the ducts lead from a room is
    # `ShipMap.duct_exits()` (the compass tables). No junction nodes exist in
    # the original, so none are built here — the `Junction` API remains only
    # for synthetic test maps.
    for room_id, has_grille in grille_of.items():
        if has_grille:
            m.add_grille(slugs[room_id])

    return m
