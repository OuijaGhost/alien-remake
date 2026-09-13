"""Tests for the ALIEN.prg game-data decoder (from the decompile audit).

Assertions pin the facts that were verified against independent signals
(docs/re/GAMEDATA.md): the room-id/name alignment via the endgame capture's
SHUTTLEBAY order, the item table via the ARMOURY laser pistols and the
fixed-address tracker/cat-box reads, and the map's undirected consistency.
Skipped wholesale if the extracted PRG isn't present (fresh clone).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alientools import gamedata

PRG_PATH = (
    Path(__file__).resolve().parents[1]
    / "out"
    / "Alien (USA, Europe)_files"
    / "ALIEN.prg"
)

pytestmark = pytest.mark.skipif(
    not PRG_PATH.exists(), reason="extracted ALIEN.prg not present"
)


@pytest.fixture(scope="module")
def gd() -> gamedata.GameData:
    return gamedata.load_gamedata(PRG_PATH)


def test_room_names_align_with_the_capture_verified_ids(gd: gamedata.GameData) -> None:
    # Id 34 = SHUTTLEBAY: the endgame RAM capture shows the ordered crew
    # member's location byte $22 with "MOVE TO: SHUTTLEBAY" on screen.
    # **D-123:** room 34 has its own name pointer `$5DD1` and is the
    # NARCISSUS. The old flat read of `$A71C` ignored a 2-record gap at
    # room 17 and shifted every later name by two, which is how this
    # came to say SHUTTLEBAY (really room 32).
    assert gd.room_names[34] == "Narcissus"
    assert gd.room_names[32] == "ShuttleBay"
    assert "OTHER LIST" not in gd.room_names
    assert gd.room_names[2] == "Armoury"
    assert gd.room_names[0] == "Airlock 1"


def test_deck_table_is_7569_and_splits_9_16_9(gd: gamedata.GameData) -> None:
    """[C $7569] D-116 — the deck index, not `$80D3`'s duct-map screen pages.

    `$76BB LDA $7569,Y` and `menu_option_dispatch ($511F)` both read this byte
    to pick between the deck plans at `$A000`/`$A21C`/`$A438`, which decode to
    "UPPER DECK", "MIDDLE DECK" and "LOWER DECK". `$80D3` is the high byte of
    the room marker's *duct-map* screen address — its 4/5/6 are pages
    `$04xx`-`$06xx` — and it agreed with the real decks for only 12 of 34 rooms.
    """
    assert gamedata.DECK_TABLE_ADDR == 0x7569
    sizes = {d: sum(1 for r in gd.rooms if r.deck == d) for d in (0, 1, 2)}
    assert sizes == {0: 9, 1: 16, 2: 9}


def test_map_is_consistent_as_an_undirected_graph(gd: gamedata.GameData) -> None:
    # Every real exit a->b has some direction leading b->a (direction pairs
    # may bend, e.g. east one way / north back — the deck plan's ladders).
    by_id = {r.room_id: r for r in gd.rooms}
    for room in gd.rooms:
        for dest in room.exits.values():
            assert room.room_id in by_id[dest].exits.values(), (room.room_id, dest)


def test_grille_table_excludes_only_corridor_6(gd: gamedata.GameData) -> None:
    no_grille = [r.name for r in gd.rooms if not r.has_grille]
    assert no_grille == ["Corridor 6"]


def test_item_table_matches_the_verified_placements(gd: gamedata.GameData) -> None:
    assert len(gd.items) == 20
    # The three LASER PISTOLs start in the ARMOURY (room 2).
    lasers = [it for it in gd.items if it.type_name == "Laser Pist"]
    assert [it.start_room for it in lasers] == [2, 2, 2]
    # Items 6/7 are the two TRACKERs (the code reads their location slots at
    # fixed addresses $82E9/$82EA) and item 17 the CAT BOX ($82F4).
    assert gd.items[6].type_name == "Tracker"
    assert gd.items[7].type_name == "Tracker"
    assert gd.items[17].type_name == "Cat Box"


def test_item_counts_match_the_manual_with_the_laser_rename(gd: gamedata.GameData) -> None:
    counts: dict[str, int] = {}
    for it in gd.items:
        counts[it.type_name] = counts.get(it.type_name, 0) + 1
    assert counts == {
        "Elctrc Prd": 3,
        "Incineratr": 3,
        "Tracker": 2,
        "Fire Extng": 4,
        "Harpn Gun": 1,
        "Laser Pist": 3,
        "Net": 1,
        "Cat Box": 1,
        "Spanner": 2,
    }


def test_crew_and_timing_constants(gd: gamedata.GameData) -> None:
    assert gd.crew_names == (
        "Dallas", "Kane", "Ripley", "Ash", "Lambert", "Parker", "Brett",
    )
    # Static start rooms: 3x COMMDCENTR (6), 3x LIFE SUPPT (27), Brett at init.
    assert gd.crew_start_rooms == (6, 6, 6, 27, 27, 27, 0)
    assert gd.crew_walk_ticks == (4, 4, 3, 4, 3, 4, 3)
    assert gd.jones_walk_ticks == 5
    assert gd.alien_move_ticks == 70


def test_words_and_rng(gd: gamedata.GameData) -> None:
    assert gd.status_words == ("O.K.", "wounded", "collapsed", "DEAD")
    assert gd.morale_words == ("confident", "stable", "uneasy", "shaken", "broken")
    # Identity table -> the RNG is uniform 0-15.
    assert gd.rng_table == tuple(range(16))


def test_alien_route_tables_decode_to_valid_rooms(gd: gamedata.GameData) -> None:
    # Full disassembly §8.10: five surface route tables at the (non-uniformly
    # spaced) addresses $7A3A/$7A5E/$7A82/$7AA5/$7AC8, one next-room id per mapped
    # room. Every entry must be a real room id (the old uniform-36 stride read
    # garbage like 173 from tables 3-4).
    assert len(gd.routing) == 5
    for table in gd.routing:
        # **D-167:** routing is ROOM_COUNT (35), not MAPPED_ROOM_COUNT (34).
        # The five bases are 36/36/35/35 apart, so every table has a row for
        # room 34; truncating at 34 left the NARCISSUS with no routing data at
        # all, even though `$89D0 LDX #$22 / CPX $7935` shows the ROM expects
        # the Alien to be able to stand there. (The DUCT tables really are 34 —
        # their bases are 34 apart; there is no ducting in the shuttle.)
        assert len(table) == gamedata.ROOM_COUNT
        assert all(0 <= dest < len(gd.room_names) for dest in table)


def test_wrong_load_address_is_rejected() -> None:
    with pytest.raises(gamedata.GamedataError):
        gamedata.decode_gamedata(bytes([0x00, 0x10]) + bytes(0x9000))


def test_checked_in_snapshot_matches_a_fresh_decode(gd: gamedata.GameData) -> None:
    """The remake's generated snapshot module must never drift from the PRG."""
    snapshot_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "alien_remake"
        / "core"
        / "gamedata_snapshot.py"
    )
    assert snapshot_path.read_text(encoding="utf-8") == gamedata.emit_python(gd)
