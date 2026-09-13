"""The duct map (R-41 / D-091) — the screen shown while a character is in a duct.

The decode has no live capture behind it, so it stands on **mutual
consistency between four independent tables**, and these tests pin every one
of those cross-checks:

* the RLE templates (`$A956`/`$A9C4`/`$AA6E`) vs. the per-room position tables
  (`$80B1`/`$80D3`) — every room must land on a node glyph;
* the templates vs. the per-room template index (`$7569`) — node counts must
  match room counts, 9/16/9;
* the *rendered map* vs. the compass duct tables — the runs `mark_exits` lights
  up must terminate at exactly the rooms the tables call neighbours.

That last one is the strongest: the map geometry and the movement graph are
stored in completely different places, and they agree.
"""

from __future__ import annotations

from alien_remake.core import ductmap
from alien_remake.core import gamedata_snapshot as data

_ROOMS = len(data.DUCT_MAP_ROOM_TEMPLATE)


def test_there_is_one_duct_sheet_per_deck() -> None:
    """Three sheets, indexed by the same `$7569` byte as the deck plan (D-116).

    This asserted the opposite until 2026-08-08 — "duct sheets should NOT track
    the decks", on the strength of a 12-of-34 agreement. That comparison was
    against the deck read from `$80D3`, which is not a deck table at all.
    `select_menu_template ($817D)` and `$76BB` read the *same* byte: one duct
    sheet per deck, one plan per deck.
    """
    assert len(data.DUCT_MAP_TEMPLATES) == 3
    assert _ROOMS == 34
    deck_of = [data.ROOMS[r][1] for r in range(_ROOMS)]
    assert deck_of == list(data.DUCT_MAP_ROOM_TEMPLATE), (
        "the duct sheet index and the deck index are one and the same byte"
    )


def test_every_room_sits_on_a_node_glyph() -> None:
    """Cross-check 1: `$80B1`/`$80D3` vs. the unpacked templates."""
    for room in range(_ROOMS):
        row, col = ductmap.node_cell(room)
        assert ductmap.template_for(room)[row][col] == data.DUCT_MAP_NODE_CHAR


def test_each_sheet_has_exactly_as_many_nodes_as_rooms() -> None:
    """Cross-check 2: `$7569` vs. the templates. 9 / 16 / 9."""
    for index, grid in enumerate(data.DUCT_MAP_TEMPLATES):
        nodes = sum(row.count(data.DUCT_MAP_NODE_CHAR) for row in grid)
        assert nodes == data.DUCT_MAP_ROOM_TEMPLATE.count(index)
    assert [data.DUCT_MAP_ROOM_TEMPLATE.count(i) for i in range(3)] == [9, 16, 9]


def test_templates_are_thirty_by_eighteen() -> None:
    """[C $7F33 CPY #$1E / $7F43 CPX #$12]."""
    for grid in data.DUCT_MAP_TEMPLATES:
        assert len(grid) == data.DUCT_MAP_ROWS == 18
        assert all(len(row) == data.DUCT_MAP_COLS == 30 for row in grid)


def test_the_lit_runs_reach_the_rooms_the_duct_tables_name() -> None:
    """**Cross-check 3, the decisive one.** The map's geometry and the compass
    duct tables are stored independently, yet the runs `mark_exits` lights up
    land on exactly the neighbouring rooms' nodes.

    The only permitted shortfall is an edge that leaves the sheet: rooms 7, 18
    and 25 sit on different sheets, so 7<->18 and 25<->18 cannot be drawn on
    any single screen. There must be **no** edge in the other direction — a lit
    run reaching a room the tables do not connect would mean the decode is
    wrong.
    """
    node_to_room: dict[int, dict[tuple[int, int], int]] = {}
    for room in range(_ROOMS):
        sheet = data.DUCT_MAP_ROOM_TEMPLATE[room]
        node_to_room.setdefault(sheet, {})[ductmap.node_cell(room)] = room

    unlit: set[tuple[int, int]] = set()
    for room in range(_ROOMS):
        sheet = data.DUCT_MAP_ROOM_TEMPLATE[room]
        reached = {
            node_to_room[sheet][(r, c)]
            for r, c, _code, _colour in ductmap.lit_cells(room)
            if (r, c) in node_to_room[sheet] and node_to_room[sheet][(r, c)] != room
        }
        tabled = {t[room] for t in data.DUCT_NEIGHBOURS if t[room] != room}
        assert not (reached - tabled), (
            f"room {room}: map lights up {sorted(reached - tabled)}, "
            "which the duct tables do not connect"
        )
        unlit |= {(room, other) for other in tabled - reached}

    # Exactly the four cross-sheet halves, and nothing else.
    assert unlit == {(7, 18), (18, 7), (18, 25), (25, 18)}
    for a, b in unlit:
        assert data.DUCT_MAP_ROOM_TEMPLATE[a] != data.DUCT_MAP_ROOM_TEMPLATE[b]


def test_your_own_node_stays_white() -> None:
    """`mark_exits` paints the node white *before* tracing the runs, so a
    follower that wandered back over it would erase your position marker. It
    never does — which is a live check on the walker's backtrack rule
    (`$800C`/`$802C`/`$804C`)."""
    for room in range(_ROOMS):
        row, col = ductmap.node_cell(room)
        assert ductmap.colour_grid(room)[row][col] == ductmap.COLOUR_HERE


def test_only_the_two_rom_colours_are_ever_used() -> None:
    for room in range(_ROOMS):
        used = {v for row in ductmap.colour_grid(room) for v in row}
        assert used <= {
            ductmap.COLOUR_HIDDEN, ductmap.COLOUR_HERE, ductmap.COLOUR_REACHABLE
        }


def test_most_of_the_sheet_is_left_dark() -> None:
    """The whole point of the duct view: you see the run you are on, not the
    network. If this ever inverted, the map would be giving away the layout."""
    for room in range(_ROOMS):
        painted = sum(
            1 for row in ductmap.template_for(room) for v in row if v != 0
        )
        assert 0 < len(ductmap.lit_cells(room)) < painted


def test_run_terminators_are_the_node_glyphs() -> None:
    """[C $8005 CMP #$C7] — the split is not arbitrary: every glyph at or above
    `$C7` is a room node or endpoint, and everything below is pipe."""
    glyphs = {
        v for grid in data.DUCT_MAP_TEMPLATES for row in grid for v in row if v
    }
    assert glyphs == {0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC7, 0xE6, 0xE7, 0xE8}
    assert data.DUCT_MAP_NODE_CHAR >= ductmap.RUN_STOPS_AT_LEAST
    # The two commonest glyphs are the straight runs, and both walk through.
    assert 0xC0 < ductmap.RUN_STOPS_AT_LEAST
    assert 0xC1 < ductmap.RUN_STOPS_AT_LEAST


# --- R-43: CORRIDOR 6, the through-route you can never enter -----------------

def test_corridor_6_is_a_duct_junction_with_no_way_in() -> None:
    """The one room with **no grille** (`$8676`) is still a duct junction.

    This looked like a contradiction — the duct map draws an `$E6` there, and
    the DECK PLAN KEY defines `$E6` as GRILLE (D-094). It is not. CORRIDOR 6
    has four mutual duct neighbours, so the ducting **runs through** it; what
    it lacks is a grille, which is the *entrance*. So it is a segment you can
    traverse but can never enter or leave — the only such room on the ship, and
    the one place where the map's grille glyph overstates what is really there.
    """
    room = data.ROOM_NAMES.index("Corridor 6")
    assert data.ROOMS[room][6] == 0, "CORRIDOR 6 should be the grille-less room"
    assert [r for r in range(_ROOMS) if not data.ROOMS[r][6]] == [room]

    neighbours = {t[room] for t in data.DUCT_NEIGHBOURS if t[room] != room}
    assert len(neighbours) == 4, "it is a junction, not a dead end"
    # ...and every one of those links is mutual, so it is genuinely traversable.
    for other in neighbours:
        assert room in {t[other] for t in data.DUCT_NEIGHBOURS if t[other] != other}


def test_entering_a_duct_needs_a_grille_but_travelling_does_not() -> None:
    """[C $779C/$81EF] The rule that makes CORRIDOR 6 coherent: the grille
    gates *entry*, while movement inside the ducting follows the compass graph
    freely."""
    import random

    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(11))
    slug = data.ROOM_SLUGS[data.ROOM_NAMES.index("Corridor 6")]
    crew = next(iter(sim.state.crew.values()))
    crew.room_id = slug
    target = next(iter(sim.ship.duct_exits(slug).values()))

    crew.in_duct = False
    assert sim._duct_step_target(crew, target) is None   # no grille -> no entry
    crew.in_duct = True
    assert sim._duct_step_target(crew, target) == target  # but passage is fine
