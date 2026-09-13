"""Structural tests for the real, table-decoded Nostromo (later RE).

These assert facts read from ALIEN.prg's own map tables (via
gamedata_snapshot), not eyeballed approximations: room/deck counts, specific
known adjacencies, the grille exception, and the off-map Narcissus rooms.
"""

from __future__ import annotations

from alien_remake.core.map import shortest_room_path
from alien_remake.core.modes import GameMode
from alien_remake.core.nostromo import (
    NARCISSUS,
    SHTTLSTORE,
    DECK_NAMES,
    SHUTTLEBAY,
    nostromo_ship,
    room_display_name,
)


def test_all_rooms_present() -> None:
    ship = nostromo_ship()
    # 34 mapped rooms + SHUTTLEBAY + SHTTLSTORE.
    assert len(ship.rooms) == 35
    assert SHUTTLEBAY in ship.rooms


def test_deck_split_comes_from_the_screen_index_not_the_address_byte() -> None:
    """**[C $7569] P3-5/P3-6, rewritten 2026-08-02 (D-116).**

    This asserted a 10/14/10 split taken from `$80D3`. That byte is **not a
    deck table** — it is the high byte of the room marker's screen address
    (`$81C9 LDA $80D3,Y -> $FC`), and 4/5/6 are screen pages. The real per-room
    deck/screen index is **`$7569`**, which `$76BB` reads to choose which of the
    three deck plans to draw, and it splits the rooms **9/16/9**.

    The evidence is in the deck plans themselves: each is an uncompressed 30x18
    grid, and they carry **9, 16 and 9** grille glyphs (`$E6`) respectively —
    matching `$7569` exactly. Placing each room's marker on the plan `$7569`
    selects lands on a grille for **31 of 34** rooms; using `$80D3` scores
    12/34, i.e. chance. Assigning rooms to decks from an address byte is why
    crew appeared to wander and INDICATE showed the wrong floor.
    """
    from alien_remake.core import gamedata_snapshot as data

    ship = nostromo_ship()
    sizes = {d: len(ship.rooms_on(d)) for d in ship.decks()}
    # D-123: only NARCISSUS is off-map now. **D-136:** it is placed relative
    # to its one REAL door — SHUTTLEBAY (room 32), `SURFACE_EXITS[32]` — not
    # AIRLOCK 2, which has no such door (`SURFACE_EXITS[1] == (13,)`).
    # DISC-244: the split is exactly 9/16/9, with no room added on top. The
    # Narcissus used to be counted onto SHUTTLEBAY's deck here, making this
    # assert 9/16/10 while the docstring above already said 9/16/9. It has its
    # own `$758B` entry - deck 3 - and `decks()` excludes that sentinel, so it
    # appears on no plan and in no deck total.
    assert sizes == {0: 9, 1: 16, 2: 9}
    assert ship.rooms["narcissus"].deck == 3
    assert 3 not in ship.decks()
    assert sorted(data.DUCT_MAP_ROOM_TEMPLATE.count(i) for i in range(3)) == [9, 9, 16]
    assert set(DECK_NAMES) == {0, 1, 2}


def test_the_deck_plans_carry_one_grille_glyph_per_room_they_hold() -> None:
    """The cross-check that settles `$7569` vs `$80D3`: 9/16/9 either way."""
    from pathlib import Path as _Path

    from alien_remake.core import gamedata_snapshot as data

    prg = _Path("out") / "Alien (USA, Europe)_files" / "ALIEN.prg"
    if not prg.exists():
        import pytest
        pytest.skip("ALIEN.prg not extracted")
    blob = prg.read_bytes()
    load = int.from_bytes(blob[:2], "little")
    rom = blob[2:]
    for index, addr in enumerate((0xA000, 0xA21C, 0xA438)):
        plan = rom[addr - load : addr - load + 30 * 18]
        assert plan.count(data.DUCT_MAP_NODE_CHAR) ==             data.DUCT_MAP_ROOM_TEMPLATE.count(index)


def test_surface_doors_come_from_the_routing_tables() -> None:
    """**[C $7860] P-1.** This test used to assert that the *compass* tables
    were the walkable doors — they are the **duct** network. `$779C` picks the
    "move to" menu on the in-duct flag: surface -> `$7860` (routing tables),
    in-duct -> `$81EF` (compass tables). The two disagree for 31 of 34 rooms.

    The routing tables give a corridor-hub deck plan, which is the point: an
    ordinary room opens onto one corridor, not onto three arbitrary rooms.
    """
    ship = nostromo_ship()
    assert ship.door_neighbors("airlock_1") == ["corridor_6"]
    assert ship.door_neighbors("armoury") == ["corridor_3"]
    assert ship.door_neighbors("commdcentr") == ["corridor_1"]
    # ...and a corridor fans out.
    assert set(ship.door_neighbors("corridor_6")) == {
        "airlock_1", "airlock_2", "computer", "mess", "stores_3",
    }


def test_narcissus_connects_only_through_shuttlebay_not_airlock_2() -> None:
    """**[C $7935 row 32] P5-2, D-136.**

    `SURFACE_EXITS[1]` (AIRLOCK 2) is `(13,)` — CORRIDOR 6 only; it never
    lists SHUTTLEBAY. The old model wired an extra, invented AIRLOCK-2 <->
    SHUTTLEBAY door "for docking," which also meant NARCISSUS (drawn beside
    AIRLOCK 2 for rendering) inherited AIRLOCK 2's deck rather than its own
    real neighbour's — the player's "leaving the Narcissus puts the crew
    member on the wrong deck." `SURFACE_EXITS[32]` already lists room 34
    (NARCISSUS) directly, so the connection was never missing — only
    mis-anchored.
    """
    ship = nostromo_ship()
    assert "shuttlebay" not in ship.door_neighbors("airlock_2")
    assert ship.door_neighbors("airlock_2") == ["corridor_6"]
    assert "narcissus" in ship.door_neighbors("shuttlebay")
    assert ship.door_neighbors("narcissus") == ["shuttlebay"]
    # NARCISSUS is placed on SHUTTLEBAY's real deck, not AIRLOCK 2's.
    # DISC-244: NOT shuttlebay's deck. `$758B` gives the Narcissus deck 3, a
    # sentinel past the three real decks, which is what stops the location
    # pointer being drawn for it (`update_item_sprite $7C3D` parks the sprite
    # when the target's deck differs from the acting character's).
    assert ship.rooms["narcissus"].deck == 3
    assert ship.rooms["shuttlebay"].deck == 2


def test_compass_exits_are_the_duct_network_not_doors() -> None:
    """The compass tables survive as `Room.exits` / `duct_exits()` — reachable
    only through an open grille, and deliberately NOT walkable."""
    ship = nostromo_ship()
    # AIRLOCK 1's compass neighbours are vents, not doorways.
    assert ship.duct_exits("airlock_1") == {
        "east": "stores_2",
        "south": "mess",
        "west": "livng_qtrs",
    }
    for dest in ship.duct_exits("airlock_1").values():
        assert dest not in ship.door_neighbors("airlock_1")


def test_every_surface_door_is_walkable_both_ways() -> None:
    ship = nostromo_ship()
    for room in ship.rooms.values():
        for dest in ship.door_neighbors(room.id):
            assert room.id in ship.door_neighbors(dest), (room.id, dest)


def test_grille_everywhere_except_corridor_6() -> None:
    ship = nostromo_ship()
    grille_rooms = {g.room_id for g in ship.grilles}
    assert "corridor_6" not in grille_rooms
    # Every other mapped room has one (the off-map Narcissus rooms have none).
    # D-123: the off-map rooms are now SHUTTLEBAY/SHTTLSTORE/NARCISSUS.
    # D-123: SHUTTLEBAY/SHTTLSTORE are mapped rooms now; only NARCISSUS is not.
    mapped = {r.id for r in ship.rooms.values()} - {NARCISSUS}
    assert grille_rooms == mapped - {"corridor_6"}


def test_airlocks_are_the_real_two() -> None:
    ship = nostromo_ship()
    assert ship.airlock_rooms() == ["airlock_1", "airlock_2"]
    # D-123: the evacuation craft is NARCISSUS (room 34), which is also
    # where `$5776` puts LAUNCH NARCISSUS.
    assert ship.evac_rooms() == [NARCISSUS]


def test_ship_is_fully_connected_by_doors() -> None:
    ship = nostromo_ship()
    start = "commdcentr"
    for room_id in ship.rooms:
        assert shortest_room_path(ship, start, room_id) is not None, room_id


def test_display_names_come_from_the_game() -> None:
    assert room_display_name("armoury") == "Armoury"
    assert room_display_name("shuttlebay") == "ShuttleBay"


def test_mode_no_longer_changes_the_topology() -> None:
    # The "short mode drops a deck" reading was a guess; the decoded tables have
    # one map. SHORT differs in budget, not topology.
    full = nostromo_ship(GameMode.FULL)
    short = nostromo_ship(GameMode.SHORT)
    assert set(full.rooms) == set(short.rooms)


def test_the_narcissus_never_gets_a_location_marker(monkeypatch) -> None:
    """**[C $7C3D] DISC-244** — highlighting NARCISSUS shows no marker box.

    `update_item_sprite` compares the target room's deck with the acting
    character's and, on a mismatch, writes `$D002 = 0` — parking the pointer
    sprite off the left edge rather than positioning it. The Narcissus's deck
    is `$758B` = 3, which no crew member aboard the ship can be on, so the
    comparison can never match while they are still on the Nostromo.

    The remake gave it SHUTTLEBAY's deck, so the box appeared when a crew
    member in the ShuttleBay highlighted it in "move to:".
    """
    ship = nostromo_ship()
    narcissus = ship.rooms["narcissus"]

    # It is on no drawable deck...
    assert narcissus.deck not in ship.decks()
    # ...so it is in no deck's room list, which is what the renderer iterates.
    for deck in ship.decks():
        assert narcissus not in ship.rooms_on(deck)
    # ...and it still has its one real door, from SHUTTLEBAY (D-136).
    assert "narcissus" in ship.door_neighbors(SHUTTLEBAY)


def test_duct_crawlers_are_not_listed_as_also_here() -> None:
    """**[C $7E76] DISC-244** — `LDA $6501,Y / BNE` skips anyone in a duct.

    The co-occupant scan tests same-room, not-yourself, **and not-in-a-duct**.
    The remake had the first two, so someone in the vents — who still carries
    the room's id — was listed as standing next to you.
    """
    import random

    from alien_remake.core.sim import Simulation
    from alien_remake.render.play import co_occupants

    sim = Simulation(rng=random.Random(0))
    living = [c for c in sim.state.crew.values() if c.alive]
    viewer, roommate, crawler = living[:3]
    room = viewer.room_id
    # Clear the room first: the opening seats survivors 3+3 (DISC-229), so it
    # already has occupants that would otherwise muddy the assertions.
    for c in sim.state.crew.values():
        c.in_duct = False
        if c not in (viewer, roommate, crawler):
            c.room_id = None
    for c in (viewer, roommate, crawler):
        c.room_id = room

    assert set(co_occupants(sim.state, viewer)) == {roommate.name, crawler.name}
    assert viewer.name not in co_occupants(sim.state, viewer)   # $7E71

    crawler.in_duct = True
    assert set(co_occupants(sim.state, viewer)) == {roommate.name}, (
        "a crew member in the ducts is not in the room with you ($7E76)"
    )

    # The ROM tests the *candidate's* flag, not the viewer's, so a crawler is
    # still shown the room's occupants. Asymmetric, and deliberately so.
    assert set(co_occupants(sim.state, crawler)) == {viewer.name, roommate.name}

    # Dead crew are never listed either.
    roommate.alive = False
    assert co_occupants(sim.state, viewer) == []
