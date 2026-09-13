"""Grille -> duct entry, end to end (P-5).

The sequence a player performs: REMVGRILLE, then move through the grille into
the ducting, then navigate a *different* graph from the one on the surface.
"""

from __future__ import annotations

import random
from pathlib import Path

from alien_remake.core import constants
from alien_remake.core.menu import _reachable_move_targets
from alien_remake.core.orders import Order, OrderOutcome, OrderType
from alien_remake.core.sim import Simulation

import needs                                       # noqa: E402


def _sim_with_crew_in(room: str, seed: int = 5):
    sim = Simulation(rng=random.Random(seed))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.room_id = room
    crew.in_duct = False
    return sim, crew



def _pull_grille(sim, crew) -> "OrderOutcome":
    """Issue REMVGRILLE and run it to completion.

    **[C $845A] D-166** — it is not instant: `$403A,Y` gives 80-180 passes by
    character (Parker/Brett 80, Ripley/Lambert 180) plus
    `compute_action_delay`, so these tests have to let the action run rather
    than asserting on the first tick.
    """
    order = Order(crew.id, OrderType.REMOVE_GRILL)
    outcome = sim._apply_order(order)
    for _ in range(400):
        if outcome is not OrderOutcome.IN_TRANSIT:
            break
        outcome = sim._apply_order(order)
    return outcome

def test_move_menu_switches_graph_on_the_in_duct_flag() -> None:
    """[C $779C] The load-bearing behaviour: surface -> routing graph,
    in duct -> compass graph. They must actually differ."""
    # NB pick a room where the graphs actually differ — they coincide for 3 of
    # the 34 rooms (COMMDCENTR is one), which would make this test vacuous.
    sim, crew = _sim_with_crew_in("airlock_1")
    surface = set(_reachable_move_targets(sim, crew.id))
    crew.in_duct = True
    in_duct = set(_reachable_move_targets(sim, crew.id))
    assert surface == {"corridor_6"}
    assert in_duct == set(sim.ship.duct_exits("airlock_1").values())
    assert surface != in_duct


def test_the_ducts_reach_rooms_the_doors_do_not() -> None:
    """Otherwise there would be no reason to crawl."""
    sim, crew = _sim_with_crew_in("airlock_1")
    surface = set(_reachable_move_targets(sim, crew.id))
    crew.in_duct = True
    in_duct = set(_reachable_move_targets(sim, crew.id))
    assert in_duct - surface, "the ducts should open up new rooms"
    assert surface == {"corridor_6"}
    # D-123: same rooms, corrected names (the ids never moved).
    assert in_duct == {"livng_qtrs", "mess", "stores_2"}


def test_remove_grill_opens_the_rooms_grille() -> None:
    sim, crew = _sim_with_crew_in("commdcentr")
    grille = next(g for g in sim.ship.grilles if g.room_id == "commdcentr")
    assert not grille.is_open
    assert _pull_grille(sim, crew) is OrderOutcome.COMPLETED
    assert grille.is_open


def test_corridor_6_has_no_grille_to_remove() -> None:
    """[C $8676] The one room without one."""
    sim, crew = _sim_with_crew_in("corridor_6")
    assert sim._apply_order(
        Order(crew.id, OrderType.REMOVE_GRILL)
    ) is OrderOutcome.BLOCKED


def test_entering_the_ducts_costs_one_composure() -> None:
    """[C $737E-$738D] Entering is the frightening part; `$729C` then raises
    composure for every tick spent inside (D-059/D-083)."""
    sim, crew = _sim_with_crew_in("airlock_1")
    crew.fear = 4
    # The grille has to come off first — that is the whole sequence.
    assert _pull_grille(sim, crew) is OrderOutcome.COMPLETED
    before = crew.fear
    # **P2-2:** entering is now the explicit "MOVE TO: GRILLE" choice
    # (`$8729` writes the label into the MOVE TO column), not a side effect of
    # ordering an ordinary move that happens to be a duct neighbour.
    assert sim._apply_order(
        Order(crew.id, OrderType.USE_GRILLE)
    ) is OrderOutcome.COMPLETED
    assert crew.in_duct is True
    assert crew.fear == before - constants.DUCT_ENTRY_COMPOSURE_COST


def test_a_broken_crew_member_loses_no_further_composure() -> None:
    """[C $7381 CMP #$02 / BCC] the gate; and `$7385 BEQ` skips at 0."""
    sim, crew = _sim_with_crew_in("airlock_1")
    crew.fear = 1                       # below the $6571 >= 2 gate
    _pull_grille(sim, crew)
    sim._apply_order(Order(crew.id, OrderType.USE_GRILLE))
    assert crew.fear == 1


def test_a_shut_grille_keeps_them_out_of_the_ducts() -> None:
    """Without REMVGRILLE there is no way in — the crew member stays on the
    surface graph and walks the long way round instead.

    (That multi-room walk is a remake convenience: the real CONTROL panel only
    ever offers *direct* connections, so this order could not be issued in the
    original. What matters here is that `in_duct` never gets set.)
    """
    sim, crew = _sim_with_crew_in("airlock_1")
    target = sim.ship.duct_exits("airlock_1")["east"]      # recrtnarea
    assert target not in _reachable_move_targets(sim, crew.id)  # not offered
    # D-168/PV-34: the clock is pumped once per pass by
    # `_pump_characters`, not decremented inside `_apply_order`, so a
    # direct call acts when `$64EE,Y` is already 0.
    crew.step_timer = 0
    sim._apply_order(Order(crew.id, OrderType.MOVE_TO, target))
    assert crew.in_duct is False
    assert crew.room_id in sim.ship.door_neighbors("airlock_1")


def test_moving_along_the_ducts_needs_no_further_grille() -> None:
    """[C $81EF] Once inside, movement is free along the compass graph."""
    sim, crew = _sim_with_crew_in("airlock_1")
    crew.in_duct = True
    target = sim.ship.duct_exits("airlock_1")["west"]    # lab_stores
    # D-168/PV-34: the clock is pumped once per pass by
    # `_pump_characters`, not decremented inside `_apply_order`, so a
    # direct call acts when `$64EE,Y` is already 0.
    crew.step_timer = 0
    sim._apply_order(Order(crew.id, OrderType.MOVE_TO, target))
    assert crew.room_id == target
    assert crew.in_duct is True


# --- P2-2 / P2-3 / P2-4: the grille is a DESTINATION, not a side effect ------

def _labels(sim, crew, category):
    from alien_remake.core.menu import crew_entries
    return [e.label for e in crew_entries(sim, crew.id)
            if e.category.name == category]


def test_the_grille_moves_between_the_special_and_move_to_columns() -> None:
    """**[C $86F0] `draw_grille_option` writes to two different screen slots.**

    Grille in place  -> "RemvGrille" ($86E6) into `$064E`, row 14 = SPECIAL.
    Grille removed   -> "GRILLE"     ($86BE) into `$046E`, row  2 = MOVE TO,
                        and the SPECIAL slot is blanked ($8733).

    So an opened grille becomes a **destination you choose**. A player reported
    that removing a grille and then ordering an ordinary move dumped the crew
    member into the ducting instead of the room they asked for; that implicit
    conversion is gone.
    """
    sim, crew = _sim_with_crew_in("airlock_1")
    # Keep the Alien elsewhere (P5-4/D-132 added an "Attack" SPECIAL entry
    # while it shares the crew member's room) — unrelated to what this test
    # isolates.
    if sim.state.alien is not None:
        sim.state.alien.room_id = next(
            r for r in sim.ship.rooms if r != crew.room_id
        )
    assert _labels(sim, crew, "SPECIAL") == ["RemvGrille"]
    assert "GRILLE" not in _labels(sim, crew, "MOVE_TO")

    _pull_grille(sim, crew)
    assert "RemvGrille" not in _labels(sim, crew, "SPECIAL")
    assert "GRILLE" in _labels(sim, crew, "MOVE_TO")


def test_an_ordinary_move_never_vents_a_crew_member() -> None:
    """The reported bug, pinned: with the grille open, a normal MOVE TO to a
    room that also happens to be a duct neighbour must stay on the surface."""
    sim, crew = _sim_with_crew_in("airlock_1")
    _pull_grille(sim, crew)
    vent = sim.ship.duct_exits("airlock_1")["east"]
    assert vent not in sim.ship.door_neighbors("airlock_1")
    # D-168/PV-34: the clock is pumped once per pass by
    # `_pump_characters`, not decremented inside `_apply_order`, so a
    # direct call acts when `$64EE,Y` is already 0.
    crew.step_timer = 0
    sim._apply_order(Order(crew.id, OrderType.MOVE_TO, vent))
    assert crew.in_duct is False


def test_crossing_the_grille_toggles_and_needs_it_open() -> None:
    sim, crew = _sim_with_crew_in("airlock_1")
    # Shut: the option is not offered and the order is refused.
    assert sim._apply_order(
        Order(crew.id, OrderType.USE_GRILLE)
    ) is OrderOutcome.BLOCKED
    _pull_grille(sim, crew)
    assert sim._apply_order(
        Order(crew.id, OrderType.USE_GRILLE)
    ) is OrderOutcome.COMPLETED
    assert crew.in_duct is True and crew.room_id == "airlock_1"
    # ...and back out again, at the same place.
    sim._apply_order(Order(crew.id, OrderType.USE_GRILLE))
    assert crew.in_duct is False and crew.room_id == "airlock_1"


def test_inside_a_duct_the_menu_names_directions_not_rooms() -> None:
    """**[C $81EF] P2-3.** The in-duct MOVE TO list is built from the four
    compass tables, each self-reference skipped (`$81F2 CMP $7934 / BEQ`) and
    each survivor labelled from the `$8080` word block — NORTH/EAST/SOUTH/WEST,
    never a room name. That is what makes duct travel disorienting: you are
    told which way you may go, never where it leads.
    """
    from alien_remake.core.menu import DUCT_DIRECTION_LABELS

    sim, crew = _sim_with_crew_in("airlock_1")
    _pull_grille(sim, crew)
    sim._apply_order(Order(crew.id, OrderType.USE_GRILLE))

    move_to = _labels(sim, crew, "MOVE_TO")
    directions = [l for l in move_to if l != "GRILLE"]
    assert directions, "a duct junction should offer some direction"
    assert set(directions) <= set(DUCT_DIRECTION_LABELS.values())
    # No room name leaks in.
    room_names = {r.name.strip() for r in sim.ship.rooms.values()}
    assert not (set(directions) & room_names)
    # Only the directions that actually exist here are listed.
    exits = sim.ship.duct_exits("airlock_1")
    expected = {
        DUCT_DIRECTION_LABELS[d]
        for d, dest in exits.items() if dest != "airlock_1"
    }
    assert set(directions) == expected


def test_a_grille_can_be_removed_from_inside_the_ducting() -> None:
    """**P2-4.** `draw_grille_option` keys off `$64F7` (the displayed room), not
    the character's surface/duct state, so a crew member crawling the ducts can
    open a still-shut grille from the inside and climb out there."""
    sim, crew = _sim_with_crew_in("airlock_1")
    _pull_grille(sim, crew)
    sim._apply_order(Order(crew.id, OrderType.USE_GRILLE))
    crew.room_id = sim.ship.duct_exits("airlock_1")["east"]   # crawl along

    assert "RemvGrille" in _labels(sim, crew, "SPECIAL")
    assert "GRILLE" not in _labels(sim, crew, "MOVE_TO")
    assert _pull_grille(sim, crew) is OrderOutcome.COMPLETED
    assert "GRILLE" in _labels(sim, crew, "MOVE_TO")
    sim._apply_order(Order(crew.id, OrderType.USE_GRILLE))
    assert crew.in_duct is False


def test_remvgrille_is_the_slowest_action_and_has_its_own_aptitude_table() -> None:
    """**[C $845A `LDA $403A,Y`] D-166** — a second per-character timing table.

    The grille handler loads `$403A,Y` into `$64EE,Y` and adds
    `compute_action_delay` on top, exactly as the move does with its flat
    `#$40`. Two things follow. It is the **slowest action in the game** — up to
    180 passes, ~23 s, where a room move is 64 — and its profile is nearly the
    *inverse* of the movement one: Parker and Brett (the engineers) are fastest
    at a grille, Ripley and Lambert slowest, where `$4032` has Ripley quickest
    on the move and Parker slowest. The remake opened grilles instantly,
    losing both the commitment and the characterisation.
    """
    needs.need(needs.ALIEN_PRG)
    from alien_remake.core import constants
    from alien_remake.core.gamedata_snapshot import CREW_NAMES

    # Byte-pinned against the PRG rather than transcribed.
    prg = Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    table = list(prg[2:][0x403A - load : 0x403A - load + 8])
    assert tuple(table) == constants.GRILLE_ACTION_TICKS

    by_name = {n: table[i + 1] for i, n in enumerate(CREW_NAMES)}
    assert by_name["Parker"] == 80 and by_name["Brett"] == 80    # engineers
    assert by_name["Ripley"] == 180 and by_name["Lambert"] == 180
    # ...and it is not the movement profile: there Ripley is the FASTEST.
    move = [constants.action_delay(s, 6) for s in range(1, 8)]
    assert move[CREW_NAMES.index("Ripley")] == min(move)
    assert by_name["Ripley"] == max(table)

    # And it really costs that many ticks in play. **D-168/PV-34:** the clock
    # is armed by `queue_order` ($7B69) and decremented once per pass by
    # `_pump_characters` ($7226), so measure it through `advance()` rather than
    # by re-calling the handler.
    sim, crew = _sim_with_crew_in("commdcentr")
    grille = next(g for g in sim.ship.grilles if g.room_id == "commdcentr")
    slot = sim._slot_of(crew)
    expected = constants.grille_action_ticks(slot) + sim._action_delay_for(crew)
    sim.queue_order(Order(crew.id, OrderType.REMOVE_GRILL))
    assert crew.step_timer == expected, "queue_order arms $64EE,Y at issue time"
    ticks = 0
    while not grille.is_open:
        sim.advance()
        ticks += 1
        assert ticks < 400, "the grille never came off"
    assert ticks == expected


def test_move_to_is_the_roms_ordered_walk_not_a_sorted_set() -> None:
    """**[C $7860/$81EF] D-167 — PV-33/PV-02.**

    The panel's MOVE TO list is built into `$7917,Y` (read back at `$7B4E` as
    `$7914,Y`, the +3 offset being the cursor row of the first entry) by two
    builders with *different* rules:

    * surface `$7860` — walk the five route tables in order; skip an entry
      equal to the last accepted one (`$7883 CMP $7947`); **end the whole
      list** on one equal to the current room (`$7888 BEQ $7908`).
    * duct `$81EF` — walk the four compass tables; an entry equal to the
      current room is merely **skipped** (`$81F2`), never a terminator.

    The remake sorted a set, which got the contents right for 34 of 35 rooms
    but the order wrong for 10 — and order matters because the cursor is
    positional (P3-1).
    """
    from alien_remake.core.alien import surface_move_targets
    from alien_remake.core.gamedata_snapshot import ALIEN_ROUTES, ROOM_SLUGS
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()

    # The order is the tables' order, not alphabetical.
    got = surface_move_targets(ship, "corridor_6")
    assert got == ["mess", "airlock_1", "computer", "stores_3", "airlock_2"]
    assert got != sorted(got), "a sorted set would reorder this room"

    # The terminate rule: replay it by hand for every room and agree.
    for room in ship.rooms:
        idx = ROOM_SLUGS.index(room)
        expect: list[str] = []
        last = None
        for table in ALIEN_ROUTES:
            dest = ROOM_SLUGS[table[idx]]
            if dest == room:
                break                       # $7888 -- ends the list
            if dest != last:
                expect.append(dest)
                last = dest
        assert surface_move_targets(ship, room) == expect, room

    # D-167: the NARCISSUS has a real routing row that the 34-entry snapshot
    # was dropping -- shuttlebay, shuttlebay, then three self-references.
    assert surface_move_targets(ship, "narcissus") == ["shuttlebay"]
