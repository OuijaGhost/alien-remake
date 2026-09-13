"""Tests for the crew model and the Personality Control System.

The PCS is the game's central mechanic (GAME_SPEC §5): crew may obey, hesitate,
or refuse an order per their state of mind. The gate is pure and takes an injected
RNG, so a scripted generator makes every branch deterministic. Order *application*
(movement over the room/duct graph, opening grilles) is exercised through the
Simulation with calm crew (fear 0 ⇒ always obey).
"""

from __future__ import annotations

def _ticks_to_move(sim, crew) -> int:
    """**[C $7B69] P3-2** — the real room-move duration.

    A move loads `$64EE,Y` with a flat `#$40` (64) and then
    `compute_action_delay ($4042)` **adds** the per-slot and per-health terms.
    Tests used to hand-count the old `$6586`-derived 3-4 ticks, which was about
    18x too fast; they now ask for the real figure.
    """
    from alien_remake.core import constants

    return constants.MOVE_ACTION_TICKS + sim._action_delay_for(crew) + 2



import random

from alien_remake.core import constants
from alien_remake.core.alien import Alien
from alien_remake.core.crew import ROSTER, CrewMember, Role, default_crew
from alien_remake.core.items import ItemInstance
from alien_remake.core.map import (
    Junction,
    Room,
    ShipMap,
    shortest_room_path,
)
from alien_remake.core.orders import (
    Order,
    OrderOutcome,
    OrderType,
)
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GameState


class Scripted(random.Random):
    """A random.Random whose ``random()`` returns a fixed, repeating sequence."""

    def __init__(self, values: list[float]) -> None:
        super().__init__()
        self._values = values
        self._i = 0

    def random(self) -> float:  # type: ignore[override]
        v = self._values[self._i % len(self._values)]
        self._i += 1
        return v


# --- roster -------------------------------------------------------------------


def _run_out(sim, order) -> "OrderOutcome":
    """Apply ``order`` until it stops returning IN_TRANSIT (D-166: REMVGRILLE
    and MOVE TO are multi-tick actions, not instant)."""
    outcome = sim._apply_order(order)
    for _ in range(400):
        if outcome is not OrderOutcome.IN_TRANSIT:
            break
        outcome = sim._apply_order(order)
    return outcome

def test_roster_is_the_seven_named_crew_in_game_order() -> None:
    names = [name for _id, name, _role in ROSTER]
    assert names == ["Dallas", "Kane", "Ripley", "Ash", "Lambert", "Parker", "Brett"]
    # Canonical role pairing (GAME_SPEC §4).
    by_id = {cid: role for cid, _n, role in ROSTER}
    assert by_id["dallas"] is Role.CAPTAIN
    assert by_id["ripley"] is Role.WARRANT_OFFICER
    assert by_id["ash"] is Role.SCIENCE_OFFICER


def test_default_crew_places_all_seven_alive_on_a_deck() -> None:
    ship = _line_ship()
    crew = default_crew(ship, deck=0)
    assert len(crew) == 7
    assert all(c.alive and c.awake for c in crew.values())
    room_ids = {r.id for r in ship.rooms_on(0)}
    assert all(c.room_id in room_ids for c in crew.values())


# --- PCS curve (pure) ---------------------------------------------------------

def test_fear_scale_is_zero_to_ten() -> None:
    # Full disassembly (D-011): the real fear cell $7D55 is capped at 10.
    assert constants.FEAR_MIN == 0
    assert constants.FEAR_MAX == 10


def test_morale_labels_are_the_games_own_words() -> None:
    """D-059 [C $7DC5 + $7D13], byte-verified: `fear_band` computes
    ``index = 0 if value >= 5 else (4 - value)`` into the word records at
    `$7D13` (confident/stable/uneasy/shaken/broken). **High is GOOD** — the
    remake had this inverted."""
    assert [
        CrewMember("x", "X", Role.CAPTAIN, None, fear=v).morale for v in range(6)
    ] == ["broken", "shaken", "uneasy", "stable", "confident", "confident"]
    lo = CrewMember("a", "A", Role.CAPTAIN, None, fear=0)
    hi = CrewMember("b", "B", Role.CAPTAIN, None, fear=constants.FEAR_MAX)
    assert lo.morale == "broken"        # 0 = the terminal state (also "is insane")
    assert hi.morale == "confident"
    assert constants.MORALE_BANDS == (
        "confident", "stable", "uneasy", "shaken", "broken",
    )


def test_bump_fear_clamps_to_range() -> None:
    c = CrewMember("a", "A", Role.CAPTAIN, None, fear=5)
    c.bump_fear(-100)
    assert c.fear == constants.FEAR_MIN
    c.bump_fear(1000)
    assert c.fear == constants.FEAR_MAX  # == 10


# --- orders are always obeyed (1:1: no compliance roll exists in the code) -----

def test_orders_are_obeyed_regardless_of_fear() -> None:
    # D-018 (user capture + disassembly): Dallas obeyed a MOVE at fear 4; the
    # decoded order path has no compliance roll. A terrified crew member still
    # obeys — the old OBEY/DELAY/REFUSE gate was an invention and is gone.
    ship = _line_ship()
    scared = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A",
                        fear=constants.FEAR_MAX, walk_ticks=1)
    state = GameState(crew={"ripley": scared}, alien=Alien(room_id=None))
    sim = Simulation(state=state, ship=ship, rng=Scripted([0.99]))
    sim.queue_order(Order("ripley", OrderType.MOVE_TO, "B"))
    # P3-2: a move is the ROM's ~71 ticks, not one — see `_ticks_to_move`.
    seen = []
    for _ in range(_ticks_to_move(sim, scared)):
        sim.advance()
        seen.extend(o[1] for o in sim.last_outcomes)
    assert scared.room_id == "B"
    assert OrderOutcome.COMPLETED in seen


# --- movement graph -----------------------------------------------------------

def _line_ship() -> ShipMap:
    """Rooms A-B-C in a door chain on deck 0 (plus a spare deck-0 room D)."""
    m = ShipMap()
    for i, rid in enumerate("ABCD"):
        m.add_room(Room(rid, 0, rid, i, 0))
    m.add_door("A", "B")
    m.add_door("B", "C")
    m.add_door("C", "D")
    return m


def test_shortest_room_path_over_doors() -> None:
    ship = _line_ship()
    assert shortest_room_path(ship, "A", "A") == ["A"]
    assert shortest_room_path(ship, "A", "C") == ["A", "B", "C"]


def test_shortest_room_path_unreachable_is_none() -> None:
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0))
    m.add_room(Room("B", 1, "B", 0, 1))  # no door, no open grille
    assert shortest_room_path(m, "A", "B") is None


def test_grille_opens_a_duct_route_between_decks() -> None:
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0))
    m.add_room(Room("B", 1, "B", 0, 1))
    m.add_junction(Junction("jA", 0, 0, 0))
    m.add_junction(Junction("jB", 1, 0, 1))
    m.add_duct("jA", "jB")
    m.add_grille("A", "jA")
    m.add_grille("B", "jB")
    assert shortest_room_path(m, "A", "B") is None  # grilles closed
    m.open_grille("A", "jA")
    m.open_grille("B", "jB")
    assert shortest_room_path(m, "A", "B") == ["A", "B"]


# --- order application through the sim -----------------------------------------

def _sim_with_crew_at(room: str, ship: ShipMap) -> Simulation:
    # alien=Alien(room_id=None) keeps these movement/PCS tests Alien-free (# added Alien proximity as a fear *source*, GAME_SPEC §11 #1 — out of scope
    # here, where crew must stay calm/obedient by construction).
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)},
        alien=Alien(room_id=None),
    )
    return Simulation(state=state, ship=ship)  # default RNG; calm crew always obeys


def test_move_to_takes_the_roms_full_move_duration() -> None:
    """**[C $7B69] P3-2 — rewritten 2026-08-02; the old test pinned a move that
    was ~18x too fast.**

    It asserted a room step completes in the crew member's `$6586` walk value
    (3 ticks for Ripley, about 0.4 s). The move handler actually loads a flat
    `#$40` = **64** into `$64EE,Y` and only then calls `compute_action_delay`,
    which **adds** `$4032[slot] + $402B[health]` — so a healthy crew member
    takes ~71 ticks (~9 s at 7.886 Hz) and one on 2 health takes ~119 (~15 s).
    That delay is the thing a player notices most, and we had removed it.
    """
    from alien_remake.core import constants

    sim = _sim_with_crew_at("A", _line_ship())
    ripley = sim.state.crew["ripley"]
    sim.queue_order(Order("ripley", OrderType.MOVE_TO, "B"))

    expected = constants.MOVE_ACTION_TICKS + sim._action_delay_for(ripley)
    assert expected >= 64, "the base alone is 64 ticks"
    for _ in range(expected - 1):
        sim.advance()
        assert ripley.room_id == "A", "should still be walking"
    sim.advance()
    assert ripley.room_id == "B"


def test_being_wounded_makes_the_walk_much_longer() -> None:
    """The health term dominates: `$402B` is +48 ticks at 2 health."""
    from alien_remake.core import constants

    sim = _sim_with_crew_at("A", _line_ship())
    ripley = sim.state.crew["ripley"]
    healthy = constants.MOVE_ACTION_TICKS + sim._action_delay_for(ripley)
    ripley.health = 2
    hurt = constants.MOVE_ACTION_TICKS + sim._action_delay_for(ripley)
    assert hurt - healthy == 48


def test_move_to_unreachable_is_blocked_and_dropped() -> None:
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0))
    m.add_room(Room("Z", 0, "Z", 5, 5))  # no connection
    sim = _sim_with_crew_at("A", m)
    sim.queue_order(Order("ripley", OrderType.MOVE_TO, "Z"))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.pending_orders == 0
    assert sim.state.crew["ripley"].room_id == "A"


def test_remove_grill_opens_the_crews_room_grille() -> None:
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0))
    m.add_junction(Junction("jA", 0, 0, 0))
    grille = m.add_grille("A", "jA")
    sim = _sim_with_crew_at("A", m)
    sim.queue_order(Order("ripley", OrderType.REMOVE_GRILL))
    # **D-166** — REMVGRILLE takes `$403A,Y` passes (80-180 by character) plus
    # `compute_action_delay`, so run it out rather than asserting on tick 1.
    for _ in range(400):
        sim.advance()
        if grille.is_open:
            break
    assert grille.is_open
    assert sim.last_outcomes[0][1] is OrderOutcome.COMPLETED


def test_get_and_leave_item_toggle_what_the_crew_holds() -> None:
    # Item pick-up/hand-off validation lives in core.items; see
    # tests/test_remake_items.py for the fuller item-model coverage.
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.state.items["taser_1"] = ItemInstance("taser_1", "taser", room_id="A")
    sim.queue_order(Order("ripley", OrderType.GET_ITEM, "taser_1"))
    sim.advance()
    assert sim.state.crew["ripley"].holding == "taser_1"
    assert sim.state.items["taser_1"].room_id is None
    assert sim.state.items["taser_1"].holder == "ripley"
    sim.queue_order(Order("ripley", OrderType.LEAVE_ITEM))
    sim.advance()
    assert sim.state.crew["ripley"].holding is None
    assert sim.state.items["taser_1"].room_id == "A"
    assert sim.state.items["taser_1"].holder is None


def test_frightened_crew_still_completes_a_move_order() -> None:
    # 1:1 fidelity: no refusal/hesitation roll exists in the decoded order path —
    # even at max fear the order is executed (only the walk timer applies).
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A",
                                   fear=10, walk_ticks=2)},
        alien=Alien(room_id=None),
    )
    sim = Simulation(state=state, ship=ship, rng=Scripted([0.9]))
    sim.queue_order(Order("ripley", OrderType.MOVE_TO, "B"))
    # P3-2: partway through the ROM's full move duration, still walking...
    ripley = sim.state.crew["ripley"]
    total = _ticks_to_move(sim, ripley)
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.IN_TRANSIT
    assert sim.pending_orders == 1
    for _ in range(total):
        sim.advance()
    assert ripley.room_id == "B"
    assert sim.pending_orders == 0


def test_status_words_are_the_games_own() -> None:
    # The four status words come straight from the decoded snapshot.
    from alien_remake.core.gamedata_snapshot import STATUS_WORDS
    c = CrewMember("a", "A", Role.CAPTAIN, "A")
    assert c.status == "O.K." and c.status in STATUS_WORDS
    c.wound()
    assert c.status == "wounded" and "wounded" in STATUS_WORDS
    assert set(STATUS_WORDS) >= {"O.K.", "wounded", "collapsed", "DEAD"}


def test_injury_lengthens_the_walk_duration() -> None:
    # RW-7 (§8.9): a wounded crew member is slower to act (health-indexed delay).
    c = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A", walk_ticks=3)
    c.wound()                                    # health 4 -> 3


def test_crowding_raises_fear_but_a_pair_does_not() -> None:
    # Full disassembly (D-011, raise_crowd_fear $4CE8): >=3 crew sharing a room
    # each get more nervous per tick; fewer than that do not. D-031: the real
    # routine also skips anyone whose fear is already 0, so this fixture seeds
    # the trio with a starting fear to actually observe the bump.
    ship = _line_ship()
    trio = {
        cid: CrewMember(cid, cid.title(), Role.CAPTAIN, "A", fear=1)
        for cid in ("a", "b", "c")
    }
    trio["d"] = CrewMember("d", "D", Role.CAPTAIN, "B", fear=1)  # alone in B
    sim = Simulation(state=GameState(crew=trio, alien=Alien(room_id=None)), ship=ship)
    sim.advance()
    assert all(sim.state.crew[c].fear == 1 + constants.FEAR_BUMP_CROWDED for c in "abc")
    assert sim.state.crew["d"].fear == 1  # not crowded


def test_crowding_does_not_spook_a_calm_crew_member() -> None:
    # D-031: `raise_crowd_fear ($4CE8)` reads `LDA $7D55,X / BEQ skip` before
    # the `INC` -- crowding only amplifies existing unease, it cannot create
    # fear from a calm (fear==0) baseline on its own.
    ship = _line_ship()
    trio = {
        cid: CrewMember(cid, cid.title(), Role.CAPTAIN, "A", fear=0)
        for cid in ("a", "b", "c")
    }
    sim = Simulation(state=GameState(crew=trio, alien=Alien(room_id=None)), ship=ship)
    sim.advance()
    assert all(sim.state.crew[c].fear == 0 for c in "abc")


def test_a_crew_death_lowers_everyones_composure_once() -> None:
    """D-059 [C $47DC/$5A0D]: a death fires a one-shot `DEC $7D55,X` looped
    over **every** crew slot — ship-wide, not room-local, and once per death
    rather than per tick. (The old test asserted a per-tick +1 for sharing a
    room with a corpse, which had the direction *and* the scope wrong.)"""
    ship = _line_ship()
    crew = {
        "a": CrewMember("a", "A", Role.CAPTAIN, "A", fear=5),
        "b": CrewMember("b", "B", Role.CAPTAIN, "D", fear=5),   # far away
        "doomed": CrewMember("doomed", "D", Role.CAPTAIN, "A", fear=5),
    }
    sim = Simulation(
        state=GameState(crew=crew, alien=Alien(room_id=None)), ship=ship
    )
    sim.advance()
    before = (crew["a"].fear, crew["b"].fear)
    crew["doomed"].alive = False          # someone dies
    sim.advance()
    assert crew["a"].fear == before[0] - 1
    assert crew["b"].fear == before[1] - 1, "the hit is ship-wide, not room-local"
    steady = (crew["a"].fear, crew["b"].fear)
    sim.advance()
    assert (crew["a"].fear, crew["b"].fear) == steady, "must fire once, not per tick"


def _retired_test_corpse_in_the_room_raises_fear() -> None:
    ship = _line_ship()
    crew = {
        "live": CrewMember("live", "Live", Role.CAPTAIN, "A"),
        "dead": CrewMember("dead", "Dead", Role.NAVIGATOR, "A", alive=False),
    }
    sim = Simulation(state=GameState(crew=crew, alien=Alien(room_id=None)), ship=ship)
    sim.advance()
    assert sim.state.crew["live"].fear == constants.FEAR_BUMP_CORPSE


def test_move_waits_when_the_destination_room_is_full() -> None:
    # R-16b (D-018): a crew member whose destination already holds ROOM_CAPACITY
    # others waits rather than entering.
    ship = _line_ship()
    crew = {
        cid: CrewMember(cid, cid.title(), Role.CAPTAIN, "B")
        for cid in ("x", "y", "z")   # three already in B (full)
    }
    crew["mover"] = CrewMember("mover", "Mover", Role.WARRANT_OFFICER, "A", walk_ticks=1)
    sim = Simulation(state=GameState(crew=crew, alien=Alien(room_id=None)), ship=ship)
    sim.queue_order(Order("mover", OrderType.MOVE_TO, "B"))
    mover = sim.state.crew["mover"]
    for _ in range(_ticks_to_move(sim, mover)):
        sim.advance()
    assert mover.room_id == "A"          # still waiting outside B
    assert sim.last_outcomes[0][1] is OrderOutcome.IN_TRANSIT
    # Free a slot: one of the three leaves B; now the mover can enter.
    sim.state.crew["z"].room_id = "C"
    for _ in range(_ticks_to_move(sim, mover)):
        sim.advance()
    assert sim.state.crew["mover"].room_id == "B"


def test_invalid_orders_are_dropped() -> None:
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.queue_order(Order("nobody", OrderType.MOVE_TO, "B"))       # unknown crew
    sim.queue_order(Order("ripley", OrderType.MOVE_TO, None))      # missing target
    sim.advance()
    assert [o for _, o in sim.last_outcomes] == [OrderOutcome.INVALID, OrderOutcome.INVALID]
    assert sim.pending_orders == 0


def test_simulation_populates_default_crew_when_state_has_none() -> None:
    sim = Simulation()
    assert len(sim.state.crew) == 7
    assert "ripley" in sim.state.crew


def test_start_rooms_come_from_the_roms_fixed_table() -> None:
    """**[C $65FF/$793D] D-125 — rewritten 2026-08-02; the fill rule was invented.**

    This asserted "first three alive in roster order -> COMMDCENTR, the rest ->
    LIFE SUPPT", i.e. a placement that **depends on who died**. The ROM cannot
    do that: `new_game`'s init loop copies a fixed template::

        65FF  LDA $793D,Y / STA $7935,Y    ; locations
        6605  LDA $7D4D,Y / STA $7D45,Y    ; health
        660B  LDA $7D5D,Y / STA $7D55,Y    ; stress

    `$793D` puts DALLAS/KANE/RIPLEY in COMMDCENTR, ASH/LAMBERT/PARKER in
    **MESS**, and **BRETT in AIRLOCK 1** — where the Alien also starts. Only
    the victim moves afterwards, to `$FE` (`$50AB-$50B5`).

    The old rule's "Life Suppt" was room 27 read under the pre-D-123 name
    shift; room 27 is MESS. And it dropped Brett's airlock start entirely.
    """
    import random

    from alien_remake.core import gamedata_snapshot as data
    from alien_remake.core.sim import Simulation

    expected = {
        cid: data.ROOM_SLUGS[data.CREW_START_ROOMS[i]]
        for i, (cid, _n, _r) in enumerate(ROSTER)
    }
    assert expected["dallas"] == "commdcentr"
    assert expected["ash"] == "mess"
    assert expected["brett"] == "airlock_1"

    # **DISC-229 — the TEMPLATE is not the final placement for Brett.**
    # `$5074-$5077` overwrites his live slot (`$793C`) with the victim's own
    # room on every opening, so only the five crew who are never the victim
    # keep their template room unconditionally. Brett is checked separately by
    # `test_the_opening_seats_six_survivors_three_and_three_never_the_airlock`.
    never_the_victim = ("ripley", "ash", "parker")
    for seed in range(4):
        sim = Simulation(rng=random.Random(seed))
        for cid in never_the_victim:
            assert sim.state.crew[cid].room_id == expected[cid], (
                f"{cid} should always start in {expected[cid]}"
            )


def test_the_alien_starts_in_airlock_1_alone() -> None:
    """`$793D`'s slot 0 is the Alien's own location: room 0, AIRLOCK 1.

    **DISC-229:** Brett's template entry is the same room, but the opening
    always moves him out (`$5077 STA $793C`) before play begins — so the
    Alien starts there *alone*. This test used to assert the opposite.
    """
    import random

    from alien_remake.core.sim import Simulation

    for seed in range(6):
        sim = Simulation(rng=random.Random(seed))
        assert sim.state.alien is not None
        assert sim.state.alien.room_id == "airlock_1"
        here = [
            c.id for c in sim.state.crew.values()
            if c.alive and c.room_id == "airlock_1"
        ]
        assert here == [], f"seed {seed}: {here} should not be in the airlock"


def test_crew_tables_match_decoded_snapshot() -> None:
    """FV-1.3 [C]: crew.py hand-copies names/walk-ticks that really live in the
    drift-guarded `gamedata_snapshot` (decoded from ALIEN.prg's `$6586` etc.).

    Nothing imports the snapshot's crew tables, so the two could silently desync
    on a `gamedata` regen. Pin them together. (Start health `$7D4D` is now applied
    — FV-1b3b — and pinned by `test_crew_start_health_is_decoded`; start fear
    `$7D5D` is decoded but not yet applied — FV-1.7.)
    """
    from alien_remake.core import gamedata_snapshot as gd
    from alien_remake.core.crew import ROSTER, WALK_TICKS

    assert tuple(name for _id, name, _role in ROSTER) == tuple(
        n.title() for n in gd.CREW_NAMES
    )
    assert WALK_TICKS == gd.CREW_WALK_TICKS
    assert constants.JONES_WALK_TICKS == gd.JONES_WALK_TICKS


def test_crew_start_health_is_decoded() -> None:
    """FV-1b3b [C $7D4D]: per-crew start health, ROSTER order (the template
    new_game copies into `$7D45`). Pins the hand-transcribed values."""
    from alien_remake.core.crew import START_HEALTH

    assert START_HEALTH == (6, 5, 4, 5, 4, 6, 5)


def test_default_crew_applies_per_crew_health() -> None:
    """FV-1b3b: `default_crew` sets each member's health + full_health to their
    decoded start value — not the old uniform 4."""
    from alien_remake.core.crew import default_crew
    from alien_remake.core.nostromo import nostromo_ship

    crew = default_crew(nostromo_ship())
    assert (crew["dallas"].health, crew["dallas"].full_health) == (6, 6)
    assert (crew["ripley"].health, crew["ripley"].full_health) == (4, 4)
    assert (crew["parker"].health, crew["parker"].full_health) == (6, 6)
    # All start O.K. (health == their own full_health).
    assert all(c.status == "O.K." for c in crew.values())


def test_tougher_crew_survive_more_wounds() -> None:
    """FV-1b3b: survivability is per-crew — Dallas (6) outlasts Ripley (4).

    Incapacitation is a fixed floor (health < 2), so Dallas takes 5 wounds to
    drop (6->1) and Ripley only 3 (4->1).

    **Status bands corrected 2026-08-01 (D-069).** This test used to assert
    "WOUNDED shows relative to each own maximum", so a once-wounded Dallas
    (6->5) had to read WOUNDED. `health_band ($7D94)` says otherwise: the
    O.K./WOUNDED boundary is an **absolute 4**, so Dallas still reads O.K. at 5
    while Ripley (4->3) reads WOUNDED. Survivability is per-crew; the *word* is
    not.
    """
    from alien_remake.core.crew import default_crew
    from alien_remake.core.nostromo import nostromo_ship

    crew = default_crew(nostromo_ship())
    dallas, ripley = crew["dallas"], crew["ripley"]
    dallas.wound()  # 6 -> 5
    ripley.wound()  # 4 -> 3
    assert dallas.status == "O.K."      # 5 >= 4  ($7D9B CMP #$04)
    assert ripley.status == "wounded"   # 3 -> index 1
    dallas.wound()                      # 6 -> 4, still at the boundary
    assert dallas.status == "O.K."
    dallas.wound()                      # 4 -> 3
    assert dallas.status == "wounded"
    for _ in range(2):
        ripley.wound()  # 3 -> 1
    assert not ripley.alive          # health 1 < floor 2
    assert ripley.status == "collapsed"
    assert dallas.alive              # dallas is only at 3


def test_health_band_matches_the_rom_chain() -> None:
    """[C $7D94] D-069 — the full mapping, including the two quirks: health 2
    AND 3 both read WOUNDED (2 arrives via `3 - health`), and the O.K. cut is
    absolute, independent of the member's own maximum."""
    expected = {0: "DEAD", 1: "collapsed", 2: "wounded", 3: "wounded",
                4: "O.K.", 5: "O.K.", 6: "O.K."}
    for full in (4, 5, 6):           # every real per-crew maximum
        for health, word in expected.items():
            c = CrewMember("x", "X", Role.CAPTAIN, "A", health=health,
                           full_health=full)
            assert c.status == word, f"health {health} (max {full})"


def test_crew_start_fear_is_decoded() -> None:
    """FV-1b4 [C $7D5D]: per-crew start fear, ROSTER order (template `$7D5D`)."""
    from alien_remake.core.crew import START_FEAR

    assert START_FEAR == (4, 4, 3, 4, 3, 4, 3)


def test_default_crew_start_composure_and_morale() -> None:
    """FV-1b4 [C $7D5D]: crew start at 4/4/3/4/3/4/3. **D-059 corrected what
    that means:** the value is composure (high = calm), so the opening roster
    reads CONFIDENT/STABLE — a calm crew before things go wrong — not the
    UNEASY/SHAKEN the inverted formula used to produce."""
    from alien_remake.core.crew import default_crew
    from alien_remake.core.nostromo import nostromo_ship

    crew = default_crew(nostromo_ship())
    assert crew["dallas"].fear == 4 and crew["ripley"].fear == 3
    assert all(c.fear > 0 for c in crew.values())
    assert crew["dallas"].morale == "confident"   # value 4 -> index 0
    assert crew["ripley"].morale == "stable"      # value 3 -> index 1
    assert all(c.morale in ("confident", "stable") for c in crew.values())


# --- FV-2.11 / D-043: panic-wander ------------------------------------------


def test_crew_sharing_a_room_with_the_surfaced_alien_bolt() -> None:
    """[C $5170/$5252 -> $5203]: a **nearly-broken** (composure 1) crew member
    in the same room as the *surfaced* Alien stops obeying and takes an
    Alien-style random walk (`char_wander`).

    **D-130 corrected the gate 2026-08-06 (P6-3):** `resolve_char_move` skips
    straight to ordinary dispatch when composure >= 2 (`$5170 CMP #$02 /
    BCC`), so this only fires for crew already close to breaking — an
    ordinary-composure crew member sharing the Alien's room must NOT bolt.
    """
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    # corridor_1 is a room whose panic-table entry moves under every band
    # (commdcentr, by contrast, self-loops on 2 of 3 - see the idle test below).
    start = "corridor_1"
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
    ripley.fear = 1  # $51DF/$5252's composure-1 path
    state = GameState(crew={"ripley": ripley}, alien=Alien(room_id=start))
    sim = Simulation(state=state, ship=ship, rng=random.Random(7))
    # Called directly (not via advance()): a full tick would also run the
    # Alien's own co-located wound pass, which drops composure further and
    # changes which of $51DF's branches applies — a real interaction, but not
    # what this test is isolating.
    # **Arm a countdown so a turn comes round - [C $7226] DISC-287.**
    # `char_pump` skips a character already at zero, so the panic
    # branch is reachable only on the pass a timer *reaches* zero.
    # Leaving them idle tested a turn the ROM never gives.
    for _c in sim.state.crew.values():
        _c.step_timer = 1
    sim._due = sim._pump_characters()   # D-168: $7226 first
    sim._apply_panic_wander()
    assert ripley.room_id != start, "panicking crew should bolt from the Alien"


def test_ordinary_composure_crew_do_not_bolt_from_the_alien() -> None:
    """**[C $5170] P6-3/D-130** — the regression this guards against: the old
    model wandered ANY co-located crew member regardless of composure, which
    sent everyone bolting the instant the Alien attacked anyone. Composure
    `>= PANIC_WANDER_MAX_COMPOSURE` must fall through to ordinary dispatch.
    """
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    start = "corridor_1"
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
    assert ripley.fear >= constants.PANIC_WANDER_MAX_COMPOSURE
    state = GameState(crew={"ripley": ripley}, alien=Alien(room_id=start))
    sim = Simulation(state=state, ship=ship, rng=random.Random(7))
    for _ in range(50):
        # DISC-287: arm a turn (char_pump skips an idle character)
        for _c in sim.state.crew.values():
            _c.step_timer = 1
        sim._due = sim._pump_characters()   # D-168: $7226 first
        sim._apply_panic_wander()
    assert ripley.room_id == start, "steady crew must not panic-wander"


def test_panic_wander_drops_the_queued_order() -> None:
    """`char_wander` opens with `STA $650C,Y = 0` — the pending action is
    cleared, so panic overrides the player's instruction rather than resuming
    it afterwards."""
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    start = "corridor_1"
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
    ripley.fear = 1
    state = GameState(crew={"ripley": ripley}, alien=Alien(room_id=start))
    sim = Simulation(state=state, ship=ship, rng=random.Random(7))
    target = ship.door_neighbors(start)[0]
    sim.queue_order(Order("ripley", OrderType.MOVE_TO, target))
    # D-168: queue_order arms `$64EE,Y` ($7B69), so wind it down to the
    # pass it expires on -- that is the pass the panic branch can take.
    ripley.step_timer = 1
    # DISC-287: arm a turn (char_pump skips an idle character)
    for _c in sim.state.crew.values():
        _c.step_timer = 1
    sim._due = sim._pump_characters()   # D-168: $7226 first
    sim._apply_panic_wander()
    assert sim.pending_orders == 0, "the queued order must be dropped on panic"


def test_no_panic_while_the_alien_is_hidden_in_a_duct() -> None:
    """`$5252` checks the Alien's duct flag (`$6501`) FIRST: an Alien hiding in
    the ducts is not an encounter, so co-located crew carry on normally."""
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    start = "commdcentr"
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
    state = GameState(
        crew={"ripley": ripley},
        alien=Alien(room_id=start, in_duct=True, timer=99),
    )
    sim = Simulation(state=state, ship=ship, rng=random.Random(7))
    sim.advance()
    assert ripley.room_id == start, "a ducted Alien must not trigger panic"


def test_crew_elsewhere_do_not_panic() -> None:
    """Panic is room-local: only crew sharing the Alien's room bolt."""
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    far = "cryo_vault"
    parker = CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, far)
    state = GameState(crew={"parker": parker}, alien=Alien(room_id="commdcentr"))
    sim = Simulation(state=state, ship=ship, rng=random.Random(7))
    sim.advance()
    assert parker.room_id == far


def test_panic_route_band_matches_the_decoded_comparison_chain() -> None:
    """[C $5214-$524F]: panic uses its OWN band mapping, not the Alien's -
    only tables 2/3/4 are ever used, and 3 and 4 each appear twice."""
    from alien_remake.core.alien import _panic_route_band

    assert [_panic_route_band(r) for r in range(16)] == [
        4, 4, 4,        # roll 0-2  -> $7AC8
        3, 3, 3,        # roll 3-5  -> $7AA5
        2, 2, 2,        # roll 6-8  -> $7A82
        3, 3, 3,        # roll 9-11 -> $7AA5
        4, 4, 4, 4,     # roll >=12 -> $7AC8
    ]


def test_panic_in_a_self_looping_room_leaves_the_crew_put() -> None:
    """The Alien's route tables contain **self-loops** (an entry pointing at its
    own room = idle), and panic reuses those tables verbatim. COMMDCENTR
    self-loops on 2 of its 3 panic bands, so a panicking crew member there
    often does not actually move - real ROM behaviour, not a failed lookup.
    """
    from alien_remake.core.alien import panic_dest
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    # rolls 3-5 and 9-15 -> bands 3/4, both self-loops for commdcentr
    assert panic_dest(ship, "commdcentr", 3) == "commdcentr"
    assert panic_dest(ship, "commdcentr", 12) == "commdcentr"
    # roll 6-8 -> band 2, a real move
    assert panic_dest(ship, "commdcentr", 6) == "corridor_1"


def test_is_insane_is_the_zero_state_of_mind() -> None:
    """R-26 [C $61E2/$63E5]: `select_outcome` appends "is insane" to a
    survivor whose state-of-mind cell reads exactly 0 (`LDA $7D55,Y / BNE
    skip`). Both ROM sites that read this cell — the endgame report and the
    decoded `fear_band` — treat 0 as the terminal/worst state."""
    calm = CrewMember("a", "A", Role.CAPTAIN, None, fear=constants.FEAR_MIN)
    other = CrewMember("b", "B", Role.CAPTAIN, None, fear=3)
    assert calm.is_insane is True
    assert other.is_insane is False


def test_crew_are_in_duct_only_when_they_take_a_decoded_duct_exit() -> None:
    """`in_duct` tracks the ROM's `$6501,Y`.

    **Rewritten for P-1/P-5.** This test used to build a synthetic
    junction/duct map and assert that *any* step lacking a door implied the
    ducting. Both halves were the invented model: the original has no junction
    nodes, and a duct step is one that takes a **decoded compass exit** through
    an **open grille** ([C $779C]/[C $81EF]), not one inferred from a missing
    door. Uses the real ship so the decoded graphs are in play.
    """
    import random

    from alien_remake.core.sim import Simulation as _Sim

    sim = _Sim(rng=random.Random(5))
    ripley = next(c for c in sim.state.crew.values() if c.alive)
    ripley.room_id = "airlock_1"
    ripley.in_duct = False
    ripley.walk_ticks = 1

    # A surface step along the routing graph: not in the ducting.
    door = sim.ship.door_neighbors("airlock_1")[0]
    # D-168/PV-34: the clock is pumped once per pass by
    # `_pump_characters`, not decremented inside `_apply_order`, so a
    # direct call acts when `$64EE,Y` is already 0.
    ripley.step_timer = 0
    sim._apply_order(Order(ripley.id, OrderType.MOVE_TO, door))
    assert ripley.room_id == door and ripley.in_duct is False

    # **P2-2, updated 2026-08-02.** Entering the ducting is no longer implied
    # by taking a step that happens to be a duct neighbour — that was the bug
    # a player hit (remove a grille, order a normal move, end up in the vents).
    # The ROM makes the opened grille its own MOVE TO entry (`$8729` writes
    # "GRILLE" into the MOVE TO column `$046E`), so it takes two deliberate
    # orders: REMVGRILLE, then cross it.
    ripley.room_id = "airlock_1"
    ripley.in_duct = False
    _run_out(sim, Order(ripley.id, OrderType.REMOVE_GRILL))
    vent = sim.ship.duct_exits("airlock_1")["east"]
    assert vent not in sim.ship.door_neighbors("airlock_1")

    # An ordinary move to that room is NOT a duct step any more.
    # D-168/PV-34: the clock is pumped once per pass by
    # `_pump_characters`, not decremented inside `_apply_order`, so a
    # direct call acts when `$64EE,Y` is already 0.
    ripley.step_timer = 0
    sim._apply_order(Order(ripley.id, OrderType.MOVE_TO, vent))
    assert ripley.in_duct is False, "an ordinary MOVE TO must never vent them"

    # Crossing the grille does put them inside, at the same location.
    ripley.room_id = "airlock_1"
    sim._apply_order(Order(ripley.id, OrderType.USE_GRILLE))
    assert ripley.in_duct is True and ripley.room_id == "airlock_1"

    # ...and from inside, the compass exit is now available.
    # D-168/PV-34: the clock is pumped once per pass by
    # `_pump_characters`, not decremented inside `_apply_order`, so a
    # direct call acts when `$64EE,Y` is already 0.
    ripley.step_timer = 0
    sim._apply_order(Order(ripley.id, OrderType.MOVE_TO, vent))
    assert ripley.room_id == vent and ripley.in_duct is True

    # Crossing back out at the far end needs that room's grille open too.
    _run_out(sim, Order(ripley.id, OrderType.REMOVE_GRILL))
    sim._apply_order(Order(ripley.id, OrderType.USE_GRILLE))
    assert ripley.in_duct is False


# --- D-151: the PCS keeps TWO values, and company steadies you ---------------

def test_effective_composure_adds_the_companion_support_term() -> None:
    """**[C $4784 init_char_turn] D-151.**

    `$7D55` is the character's own base composure; `$6571` — what every gate
    actually reads — is recomputed each turn as base plus, for each
    co-located surfaced crew member, `their base - 2`. The remake modelled
    only the base, so nobody ever got the steadying effect of company and the
    crew hit the panic threshold far too readily.
    """
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    room = "commdcentr"
    lone = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)
    lone.fear = 2
    state = GameState(crew={"ripley": lone}, alien=Alien(room_id=None))
    sim = Simulation(state=state, ship=ship, rng=random.Random(0))

    # Alone: effective == base (no companions, $4781 stays 0).
    assert sim.effective_composure(lone) == 2

    # A calm companion (base 5) contributes 5 - 2 = +3.
    calm = CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, room)
    calm.fear = 5
    sim.state.crew["parker"] = calm
    assert sim.effective_composure(lone) == 2 + 3

    # A shaky one (base 1) contributes 1 - 2 = -1.
    calm.fear = 1
    assert sim.effective_composure(lone) == 2 - 1

    # A collapsed one costs a flat 1, whatever their composure ($47F8).
    calm.fear = 9
    calm.health = 1
    assert sim.effective_composure(lone) == 2 - 1

    # Never negative ($483F BPL / LDA #$00).
    lone.fear = 0
    assert sim.effective_composure(lone) == 0


def test_companion_support_needs_the_same_room_and_the_surface() -> None:
    """`$47C0 CMP $457F` (same room) and `$47C8 LDA $6501,X / BNE` (surface):
    someone in another room, or in a duct, contributes nothing. And a
    character who is themselves in a duct skips the scan entirely
    (`$47A8`) — alone in the walls there is nobody to draw on."""
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    room = "commdcentr"
    subject = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)
    subject.fear = 2
    mate = CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, room)
    mate.fear = 6                                  # would contribute +4
    state = GameState(
        crew={"ripley": subject, "parker": mate}, alien=Alien(room_id=None)
    )
    sim = Simulation(state=state, ship=ship, rng=random.Random(0))
    assert sim.effective_composure(subject) == 6   # 2 + 4

    mate.in_duct = True                            # $47C8: not on the surface
    assert sim.effective_composure(subject) == 2
    mate.in_duct = False

    mate.room_id = "cryo_vault"                    # $47C0: a different room
    assert sim.effective_composure(subject) == 2
    mate.room_id = room

    subject.in_duct = True                         # $47A8: the scan is skipped
    assert sim.effective_composure(subject) == 2


def test_company_keeps_a_shaky_crew_member_out_of_panic() -> None:
    """The behavioural payoff, and the player's actual complaint: a crew
    member whose own composure is below the `$5170` panic threshold does NOT
    panic while a steady colleague is standing with them."""
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    start = "corridor_1"
    shaky = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
    shaky.fear = 1                                  # below the gate on its own
    state = GameState(crew={"ripley": shaky}, alien=Alien(room_id=start))
    sim = Simulation(state=state, ship=ship, rng=random.Random(7))
    # DISC-287: arm a turn (char_pump skips an idle character)
    for _c in sim.state.crew.values():
        _c.step_timer = 1
    sim._due = sim._pump_characters()   # D-168: $7226 first
    sim._apply_panic_wander()
    assert shaky.room_id != start, "alone and shaky -> bolts"

    # Same setup, but with a composed colleague in the room.
    shaky2 = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
    shaky2.fear = 1
    steady = CrewMember("dallas", "Dallas", Role.CAPTAIN, start)
    steady.fear = 6                                 # contributes +4
    state2 = GameState(
        crew={"ripley": shaky2, "dallas": steady}, alien=Alien(room_id=start)
    )
    sim2 = Simulation(state=state2, ship=ship, rng=random.Random(7))
    assert sim2.effective_composure(shaky2) >= constants.PANIC_WANDER_MAX_COMPOSURE
    for _ in range(50):
        sim2._due = sim2._pump_characters()
        sim2._due = sim2._pump_characters()
        sim2._apply_panic_wander()
    assert shaky2.room_id == start, "company should hold them steady"


def test_broken_crew_bolt_even_from_a_surfaced_alien_in_the_room() -> None:
    """**[C $51E7-$5203] D-157** — the `$51F4` fall-through.

    `$51F4` was previously read as "a different, undecoded outcome," so
    composure-0 crew standing with a *surfaced* Alien were the one case that
    still obeyed orders. Byte-level there is no branch there: `$5200` is a
    three-byte `STA $64C4,Y` ending at `$5202` and `char_wander` begins at
    `$5203`, so the three stores fall straight into the wander. A broken crew
    member bolts whether the Alien is on the surface, in a duct, or elsewhere.
    """
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    start = "corridor_1"
    for alien_in_duct in (False, True):
        broken = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, start)
        broken.fear = constants.FEAR_MIN            # $51DF: composure == 0
        state = GameState(
            crew={"ripley": broken},
            alien=Alien(room_id=start, in_duct=alien_in_duct),
        )
        sim = Simulation(state=state, ship=ship, rng=random.Random(7))
        assert sim.effective_composure(broken) == constants.FEAR_MIN
        # DISC-287: arm a turn (char_pump skips an idle character)
        for _c in sim.state.crew.values():
            _c.step_timer = 1
        sim._due = sim._pump_characters()   # D-168: $7226 first
        sim._apply_panic_wander()
        assert broken.room_id != start, (
            f"composure 0 must wander (alien_in_duct={alien_in_duct})"
        )


def test_the_opening_seats_six_survivors_three_and_three_never_the_airlock() -> None:
    """**DISC-229** — Brett backfills the victim's room; nobody starts in the
    airlock.

    `$793D` parks Brett in AIRLOCK 1, but `$5074-$5077` overwrites his live
    slot (`$793C`) with the victim's own room on every opening, so the six
    survivors always come out three in COMMDCENTR and three in MESS. The
    remake used to leave him in the airlock alongside the Alien, which the
    owner correctly reported never happens in the real game.
    """
    import collections

    from alien_remake.core.flow import default_simulation
    from alien_remake.core.modes import DeathVariant, GameMode

    for _ in range(30):
        sim = default_simulation(GameMode.FULL, DeathVariant.ORIGINAL)
        alive = [c for c in sim.state.crew.values() if c.alive]
        assert len(alive) == 6
        rooms = collections.Counter(c.room_id for c in alive)
        assert sorted(rooms.values()) == [3, 3], rooms
        assert "airlock_1" not in rooms, "no survivor starts in the airlock"

        brett = sim.state.crew["brett"]
        dead = sim.state.crew[sim.state.opening_dead_crew_id or ""]
        assert brett.room_id == dead.room_id, "Brett fills the vacated room"


def test_panic_drops_the_order_and_burns_the_turn_even_when_it_cannot_move() -> None:
    """**[C $5203-$522B] DISC-233** — `char_wander` has no "did it change?" test.

    It opens with `$5205 STA $650C,Y = 0`, dropping the pending order *before*
    it rolls, and every arm converges on `$521B`, which stores the destination
    and re-arms `$64EE,Y` to 40 (`$5221 LDA #$28`).

    AIRLOCK 1 self-references in all three route bands `_panic_route_band` can
    reach, so a panicking character there genuinely cannot move — in the ROM
    either. But the ROM still drops their order and burns forty passes. The
    remake used to `continue` out of the whole branch on a self-reference,
    leaving both intact, so a panicking crew member in such a room carried on
    obeying orders as though nothing had happened.
    """
    import random

    from alien_remake.core import constants
    from alien_remake.core.alien import panic_dest
    from alien_remake.core.orders import Order, OrderType
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.room_id = "airlock_1"
    crew.in_duct = False
    crew.fear = constants.FEAR_MIN          # composure 0 -> wanders always
    crew.step_timer = 0                     # its turn is due

    # Every band this room can reach really does point back at itself.
    dests = {
        panic_dest(sim.ship, "airlock_1", roll)
        for roll in range(constants.ALIEN_ROLL_SIDES)
    }
    assert dests == {"airlock_1"}, f"expected a dead end, got {dests}"

    sim.queue_order(Order(crew.id, OrderType.MOVE_TO, "corridor_6"))
    sim._due = {crew.id}
    sim._apply_panic_wander()

    assert crew.room_id == "airlock_1", "no band can move them, in ROM or remake"
    assert not [o for o in sim._orders if o.crew_id == crew.id], (
        "$5205 drops the pending order before the roll"
    )
    assert crew.step_timer == constants.PANIC_WANDER_TICKS, (
        "$5221 re-arms the turn timer to 40 whatever the roll produced"
    )


def test_an_idle_character_never_takes_a_turn() -> None:
    """**[C $7226-$722B] DISC-287** — the clock only fires on the way to zero.

        7226  LDA $64EE,Y
        7229  BNE $722E              ; counting -> decrement
        722B  JMP check_deferred_move ; already 0 -> no turn at all

    So a crew member with nothing to do does nothing, indefinitely. The remake
    used to hand them a turn every pass - about eight a second - which is what
    made an idle character recompute their companion support, and let a
    panicked one wander, neither of which the running game does (DISC-279,
    DISC-281).
    """
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    idle = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "corridor_1")
    busy = CrewMember("parker", "Parker", Role.WARRANT_OFFICER, "corridor_1")
    busy.step_timer = 1                       # one pass from coming due
    state = GameState(crew={"ripley": idle, "parker": busy})
    sim = Simulation(state=state, ship=ship, rng=random.Random(1))

    due = sim._pump_characters()
    assert "parker" in due, "a countdown reaching zero must give a turn"
    assert "ripley" not in due, "an idle character must not get one"

    # ...and it stays that way: idling is not a countdown that keeps expiring.
    for _ in range(20):
        assert "ripley" not in sim._pump_characters()
