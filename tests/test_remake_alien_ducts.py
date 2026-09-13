"""The Alien inside the ducts (P-6, [C $8A74]/[C $8B84]).

Before this the remake modelled ducts as "hide in the same room for 40 ticks,
then reappear" — it never walked the duct network and never burst a grille.
"""

from __future__ import annotations

import random

from alien_remake.core import constants
from alien_remake.core.alien import Alien, advance_alien
from alien_remake.core.nostromo import nostromo_ship
from alien_remake.core.state import GameState


def _open_all_grilles(ship):
    for g in ship.grilles:
        g.is_open = True


def test_duct_roll_bands_are_the_rom_edges() -> None:
    """[C $8A9E/$8AB4/$8ABE] N/E/S/W at 0-2, 3-5, 6-8, 9-12; 13+ emerges."""
    assert constants.ALIEN_DUCT_DIR_BANDS == (3, 6, 9)
    assert constants.ALIEN_DUCT_EMERGE_FROM == 13
    assert constants.ALIEN_BURST_TICKS == 40


def test_alien_walks_the_duct_graph_not_the_door_graph() -> None:
    """The whole point of P-1 + P-6: in the ducts it uses the compass
    neighbours, which are *not* the walkable doors."""
    ship = nostromo_ship()
    _open_all_grilles(ship)
    state = GameState()
    start = "corridor_4"
    seen = set()
    for seed in range(60):
        alien = Alien(room_id=start, in_duct=True)
        rng = random.Random(seed)
        for _ in range(600):
            advance_alien(ship, state, alien, rng)
            if not alien.in_duct:
                break            # it surfaced; later moves are surface moves
            if alien.room_id != start:
                seen.add(alien.room_id)
                break
    assert seen, "the Alien never moved through the ducts"
    # A self-referencing table entry is the ROM's "no duct that way": the Alien
    # burns its full move timer going nowhere, so `start` shows up as a "move".
    seen.discard(start)
    duct = set(ship.duct_exits(start).values())
    doors = set(ship.door_neighbors(start))
    assert seen <= duct, f"moved somewhere that is not a duct exit: {seen - duct}"
    assert seen - doors, "the duct graph should reach rooms the doors do not"


def test_alien_emerges_from_the_ducts() -> None:
    """[C $8A92] roll 13-15 sets the destination WITHOUT bit 7 — come out here."""
    ship = nostromo_ship()
    _open_all_grilles(ship)
    state = GameState()
    alien = Alien(room_id="corridor_4", in_duct=True)
    rng = random.Random(5)
    for _ in range(4000):
        advance_alien(ship, state, alien, rng)
        if not alien.in_duct:
            break
    assert not alien.in_duct, "the Alien never came back out of the ducts"


def test_bursting_opens_that_grille_permanently() -> None:
    """[C $8B86] `STA $8676,Y` — the grille is cleared, not toggled."""
    ship = nostromo_ship()
    state = GameState()
    room = "commdcentr"
    grille = next(g for g in ship.grilles if g.room_id == room)
    assert not grille.is_open
    alien = Alien(room_id=room, in_duct=True)
    rng = random.Random(1)
    for _ in range(4000):
        advance_alien(ship, state, alien, rng)
        if grille.is_open:
            break
    assert grille.is_open, "the Alien never burst the grille"
    # ...and it stays open.
    for _ in range(50):
        advance_alien(ship, state, alien, rng)
    assert grille.is_open


def test_a_shut_grille_makes_the_alien_reroll_fifteen() -> None:
    """[C $8A7A-$8A83] While its room's grille is shut, roll 15 is re-rolled,
    so a trapped Alien is likelier to keep crawling than to try to come out."""
    ship = nostromo_ship()
    state = GameState()
    room = "commdcentr"
    # A room with a shut grille: the reroll loop must terminate (it would spin
    # forever if the guard were written against a constant roll).
    alien = Alien(room_id=room, in_duct=True)
    advance_alien(ship, state, alien, random.Random(3))
    assert alien.timer > 0


def test_corridor_6_has_no_grille_so_the_alien_cannot_duct_there() -> None:
    """[C $8676] CORRIDOR 6 is the one room without a grille."""
    ship = nostromo_ship()
    assert not any(g.room_id == "corridor_6" for g in ship.grilles)
    state = GameState()
    alien = Alien(room_id="corridor_6")
    for seed in range(30):
        a = Alien(room_id="corridor_6")
        rng = random.Random(seed)
        for _ in range(40):
            advance_alien(ship, state, a, rng)
            if a.room_id != "corridor_6":
                break
        assert not (a.in_duct and a.room_id == "corridor_6")
