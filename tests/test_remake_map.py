"""Topology tests for alien_remake.core.map.

"""
from alien_remake.core.map import (
    Direction,
    Room,
    Junction,
    Grille,
    ShipMap,
    move_cursor,
    default_ship,
)
import pytest


@pytest.fixture
def simple_map():
    m = ShipMap()
    # Deck 0
    r1 = Room("r1", 0, "Room 1", 0, 0)
    r2 = Room("r2", 0, "Room 2", 2, 2)
    # Deck 1
    r3 = Room("r3", 1, "Room 3", 5, 5)
    m.add_room(r1)
    m.add_room(r2)
    m.add_room(r3)

    # Junctions
    j1 = Junction("j1", 0, 0, 0)
    j2 = Junction("j2", 0, 5, 5)
    m.add_junction(j1)
    m.add_junction(j2)

    # Connection
    m.add_door("r1", "r2")
    m.add_duct("j1", "j2")
    m.add_grille("r1", "j1")

    return m


def test_direction_values():
    assert Direction.NORTH.value == (0, -1)
    assert Direction.SOUTH.value == (0, 1)
    assert Direction.EAST.value == (1, 0)
    assert Direction.WEST.value == (-1, 0)


def test_room_junction_dataclasses():
    r = Room("id", 1, "Name", 10, 20)
    assert r.id == "id"
    assert r.deck == 1
    assert r.x == 10
    assert r.y == 20

    j = Junction("jid", 1, 5, 6)
    assert j.id == "jid"
    assert j.x == 5
    assert j.y == 6


def test_ship_map_additions(simple_map):
    assert "r1" in simple_map.rooms
    assert "j1" in simple_map.junctions
    assert ("r1", "r2") in simple_map.doors or ("r2", "r1") in simple_map.doors
    assert len(simple_map.grilles) == 1


def test_ship_map_add_errors(simple_map):
    with pytest.raises(KeyError, match="door references an unknown room"):
        simple_map.add_door("r1", "nonexistent")
    with pytest.raises(KeyError, match="duct references an unknown junction"):
        simple_map.add_duct("j1", "nonexistent")
    with pytest.raises(KeyError, match="grille references an unknown junction"):
        simple_map.add_grille("r1", "nonexistent")
    with pytest.raises(KeyError, match="grille references an unknown room"):
        simple_map.add_grille("nonexistent")
    # P-1: the real ship's grilles are per-room ([C $8676]); the junction
    # argument is optional scaffolding for synthetic maps only.
    simple_map.add_grille("r1")


def test_ship_map_queries(simple_map):
    assert simple_map.decks() == [0, 1]
    # Check rooms_on sorting (y then x)
    rooms_deck_0 = simple_map.rooms_on(0)
    assert len(rooms_deck_0) == 2
    assert rooms_deck_0[0].id == "r1"
    assert rooms_deck_0[1].id == "r2"

    # Door neighbors
    assert simple_map.door_neighbors("r1") == ["r2"]
    assert simple_map.door_neighbors("r2") == ["r1"]
    assert simple_map.door_neighbors("r3") == []

    # Duct neighbors
    assert simple_map.duct_neighbors("j1") == ["j2"]
    assert simple_map.duct_neighbors("j2") == ["j1"]


def test_grille_logic(simple_map):
    # Check existence
    g = simple_map.grille_between("r1", "j1")
    assert g is not None
    assert not g.is_open

    # Check non-existence
    assert simple_map.grille_between("r2", "j1") is None

    # Open grille
    success = simple_map.open_grille("r1", "j1")
    assert success is True
    assert g.is_open is True

    # Opening non-existent
    assert simple_map.open_grille("r2", "j1") is False

    # Duct access (only if open)
    # Initially j1 was not accessible from r1 via an open grille? 
    # Actually, in our setup we added a closed one.
    # After opening:
    assert "j1" in simple_map.duct_access("r1")

    # Check access if closed
    m2 = ShipMap()
    m2.add_room(Room("r", 0, "R", 0, 0))
    m2.add_junction(Junction("j", 0, 0, 0))
    m2.add_grille("r", "j")
    assert "j" not in m2.duct_access("r")


def test_move_cursor_clamping(simple_map):
    # Deck 0 has rooms at (0,0) and (2,2). Bounding box: x[0,2], y[0,2]
    # Move from center (1,1) East
    assert move_cursor(simple_map, 0, 1, 1, Direction.EAST) == (2, 1)
    # Move West beyond bounds
    assert move_cursor(simple_map, 0, 0, 0, Direction.WEST) == (0, 0)
    # Move North beyond bounds
    assert move_cursor(simple_map, 0, 1, 0, Direction.NORTH) == (1, 0)
    # Move South beyond bounds
    assert move_cursor(simple_map, 0, 1, 2, Direction.SOUTH) == (1, 2)


def test_move_cursor_empty_deck():
    m = ShipMap()
    m.add_room(Room("r1", 1, "R", 5, 5)) # Deck 1 has a room
    # Deck 0 is empty
    assert move_cursor(m, 0, 10, 10, Direction.EAST) == (10, 10)


def test_default_ship():
    m = default_ship()
    assert len(m.decks()) == 3
    assert "bridge" in m.rooms
    assert "engine" in m.rooms
    assert "j0" in m.junctions
    # Check a specific connection from the implementation
    assert "nav" in m.door_neighbors("bridge")
    # Check grille and access
    assert m.grille_between("bridge", "j0") is not None
    m.open_grille("bridge", "j0")
    assert "j0" in m.duct_access("bridge")
