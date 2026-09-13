"""The duct network (D-083) — what a crew member finds after removing a grille.

The original's ducts join **rooms directly** via four compass tables
(`$80F5` N / `$8117` E / `$8139` S / `$815B` W), one neighbour room per room,
with a **self-reference meaning "no exit that way"**. The remake had modelled
ducts as a graph of invented `Junction` nodes instead.
"""

from __future__ import annotations

from alien_remake.core import constants
from alien_remake.core.gamedata_snapshot import (
    DUCT_DIRECTIONS,
    DUCT_NEIGHBOURS,
    ROOM_SLUGS,
)
from alien_remake.core.nostromo import nostromo_ship

N = 34


def test_tables_are_the_rom_shape() -> None:
    assert DUCT_DIRECTIONS == ("north", "east", "south", "west")
    assert len(DUCT_NEIGHBOURS) == 4
    assert all(len(t) == N for t in DUCT_NEIGHBOURS)


def test_every_room_has_at_least_one_duct_exit() -> None:
    ship = nostromo_ship()
    for slug in ROOM_SLUGS[:N]:
        assert ship.duct_exits(slug), f"{slug} has no duct exit"


def test_the_duct_graph_is_fully_connected() -> None:
    """All 34 rooms are reachable from any one of them through the ducts —
    which is what makes the network usable as a shortcut at all."""
    adj = {
        r: {t[r] for t in DUCT_NEIGHBOURS if t[r] != r and t[r] < N}
        for r in range(N)
    }
    seen, stack = {0}, [0]
    while stack:
        for nxt in adj[stack.pop()]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    assert len(seen) == N, f"unreachable rooms: {sorted(set(range(N)) - seen)}"


def test_self_reference_means_no_exit() -> None:
    """The ROM's encoding for a dead end — it must not appear as an exit."""
    ship = nostromo_ship()
    for d, table in zip(DUCT_DIRECTIONS, DUCT_NEIGHBOURS):
        for r, dest in enumerate(table):
            if dest == r:
                assert d not in ship.duct_exits(ROOM_SLUGS[r])


def test_most_edges_are_reciprocal_but_some_are_one_way() -> None:
    """Pinning the ROM as it is, not as it 'should' be: 54 of the 76 directed
    edges have a matching return edge and 22 do not. Recorded so a future
    'tidy-up' that symmetrises the graph fails this test instead of silently
    changing the map."""
    opp = {"north": "south", "south": "north", "east": "west", "west": "east"}
    idx = {d: i for i, d in enumerate(DUCT_DIRECTIONS)}
    total = recip = 0
    for d, table in zip(DUCT_DIRECTIONS, DUCT_NEIGHBOURS):
        for r, dest in enumerate(table):
            if dest == r or dest >= N:
                continue
            total += 1
            if DUCT_NEIGHBOURS[idx[opp[d]]][dest] == r:
                recip += 1
    assert (total, recip) == (76, 54)


def test_a_known_route_matches_the_decoded_tables() -> None:
    """CORRIDOR 4 is the network's busiest node — all four directions."""
    ship = nostromo_ship()
    # **D-123:** the two "OTHER LIST" rooms never existed — they were filler
    # records in the `$A71C` name table's gap, and every id from 17 up was
    # shifted by two. CORRIDOR 4's east/south neighbours are ENGINE 2 and
    # STORES 1; the *topology* is unchanged, only the names were wrong.
    assert ship.duct_exits("corridor_4") == {
        "north": "armoury",
        "east": "engine_2",
        "south": "stores_1",
        "west": "cryo_vault",
    }
    # and a dead-endish one
    assert ship.duct_exits("cryo_vault") == {"south": "corridor_4"}


def test_unknown_room_returns_no_exits() -> None:
    assert nostromo_ship().duct_exits("not-a-room") == {}


def test_entering_the_ducts_costs_one_composure() -> None:
    """[C $737E-$738D] Entering is stressful; **staying** inside is not —
    `$729C` raises composure every tick spent in there (D-059)."""
    assert constants.DUCT_ENTRY_COMPOSURE_COST == 1
    assert constants.DUCT_ENTRY_COMPOSURE_GATE == 2
