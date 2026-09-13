"""Tests for game modes & the opening's already-dead crew member.

Covers the pure helpers in `core.modes`, `nostromo_ship`'s short-mode deck
trim, and how `Simulation` wires both into a freshly-built game (never
touching a state/ship the caller supplied explicitly).
"""

from __future__ import annotations

import random

from alien_remake.core import constants
from alien_remake.core.crew import CrewMember, Role
from alien_remake.core.modes import (
    DeathVariant,
    GameMode,
    choose_opening_death,
)
from alien_remake.core.nostromo import nostromo_ship
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GameState


# --- core.modes: pure helpers -----------------------------------------------

def test_starting_oxygen_helper_stays_removed() -> None:
    """De-invention guard (FV-2.5 / D-062): there is no per-mode oxygen budget
    because there is no oxygen system."""
    from alien_remake.core import modes
    assert not hasattr(modes, "starting_oxygen")


def test_choose_opening_death_fixed_names_the_observed_casualty() -> None:
    crew_ids = ["dallas", "lambert", "ripley"]
    assert (
        choose_opening_death(crew_ids, DeathVariant.FIXED, random.Random(0))
        == constants.FIXED_OPENING_DEATH_ID
    )


def test_choose_opening_death_fixed_falls_back_when_id_absent() -> None:
    crew_ids = ["alpha", "beta"]  # no "lambert"
    assert (
        choose_opening_death(crew_ids, DeathVariant.FIXED, random.Random(0))
        == "alpha"
    )


def test_choose_opening_death_random_draws_from_the_roster() -> None:
    crew_ids = ["dallas", "lambert", "ripley"]
    # A seeded rng makes the draw deterministic; just assert it's a member and
    # that a different seed can pick a different one (not hard-wired to FIXED).
    picked = {
        choose_opening_death(crew_ids, DeathVariant.ORIGINAL, random.Random(seed))
        for seed in range(20)
    }
    assert picked <= set(crew_ids)
    assert len(picked) > 1


# --- nostromo_ship: mode does not change the topology (later RE) ---------

def test_short_mode_keeps_the_real_topology() -> None:
    # From the disassembly: nothing in the decoded tables supports a different map for
    # the SHORT SCENARIO; the known difference is the starting budget.
    full = nostromo_ship(GameMode.FULL)
    short = nostromo_ship(GameMode.SHORT)
    assert full.decks() == [0, 1, 2]
    assert short.decks() == [0, 1, 2]
    assert set(full.rooms) == set(short.rooms)


def test_short_mode_ship_still_well_formed() -> None:
    ship = nostromo_ship(GameMode.SHORT)
    assert ship.airlock_rooms(), "short ship must still have an airlock"
    for room_id in ship.airlock_rooms():
        assert room_id in ship.rooms


# --- Simulation wiring -------------------------------------------------------

def test_simulation_full_mode_is_the_default() -> None:
    sim = Simulation()
    assert sim.state.mode is GameMode.FULL
    assert sim.ship.decks() == [0, 1, 2]


def test_simulation_short_mode_currently_changes_nothing() -> None:
    """Honest state of SHORT mode (FV-1.9), not an endorsement of it.

    Its only ever-modelled difference was a smaller oxygen budget, and that
    whole system was an invention (FV-2.5 / D-062). `nostromo_ship()` ignores
    mode by design, so SHORT and FULL are now mechanically identical. What the
    SHORT SCENARIO really changes is unresolved `[?]` — this test pins the
    *current, truthful* behaviour so a future fix has to update it deliberately
    rather than a guess sliding in unnoticed.
    """
    short, full = Simulation(mode=GameMode.SHORT), Simulation(mode=GameMode.FULL)
    assert short.state.mode is GameMode.SHORT
    assert short.ship.decks() == full.ship.decks() == [0, 1, 2]
    assert len(short.ship.rooms) == len(full.ship.rooms)


def test_simulation_fixed_death_kills_exactly_the_canon_casualty() -> None:
    sim = Simulation(death_variant=DeathVariant.FIXED)
    dead_id = constants.FIXED_OPENING_DEATH_ID
    assert sim.state.opening_dead_crew_id == dead_id
    dead = sim.state.crew[dead_id]
    assert dead.alive is False
    assert dead.awake is False
    others_alive = [c for cid, c in sim.state.crew.items() if cid != dead_id]
    assert all(c.alive and c.awake for c in others_alive)
    assert len(sim.state.crew) == 7  # the body stays on the roster, just dead


def test_simulation_random_death_is_reproducible_from_a_seeded_rng() -> None:
    sim_a = Simulation(rng=random.Random(7), death_variant=DeathVariant.ORIGINAL)
    sim_b = Simulation(rng=random.Random(7), death_variant=DeathVariant.ORIGINAL)
    assert sim_a.state.opening_dead_crew_id == sim_b.state.opening_dead_crew_id
    assert sim_a.state.opening_dead_crew_id in sim_a.state.crew


def test_simulation_leaves_an_explicit_state_untouched() -> None:
    # Same "only touch what we own" convention as ship/items/Alien: a state
    # that already has crew skips the opening death entirely.
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")},
    )
    sim = Simulation(state=state, mode=GameMode.SHORT, death_variant=DeathVariant.ORIGINAL)
    assert sim.state.opening_dead_crew_id is None
    assert sim.state.crew["ripley"].alive is True


# --- SHORT is a FIXED scenario, not a shorter FULL (D-085) -------------------

def test_short_scenario_is_scripted_not_random() -> None:
    """[C $604F] Reached only from the Ctrl+2 branch, it overwrites the
    randomised opening: victim = KANE ($6062), android = ASH ($6067), plus four
    7-entry tables of locations/health/composure. Two different seeds must give
    identical state — nothing about SHORT is rolled."""
    import random

    a = Simulation(mode=GameMode.SHORT, rng=random.Random(1))
    b = Simulation(mode=GameMode.SHORT, rng=random.Random(999))
    for sim in (a, b):
        assert sim.state.opening_dead_crew_id == "kane"
        assert sim.state.android_id == "ash"
    assert (
        {c.id: (c.room_id, c.health, c.fear) for c in a.state.crew.values()}
        == {c.id: (c.room_id, c.health, c.fear) for c in b.state.crew.values()}
    )


def test_short_scenario_matches_the_decoded_tables() -> None:
    """The exact opening the ROM scripts — a far more desperate one than FULL."""
    import random

    from alien_remake.core.gamedata_snapshot import ROOM_SLUGS, SHORT_SCENARIO

    sim = Simulation(mode=GameMode.SHORT, rng=random.Random(4))
    locs, health, composure, _ = SHORT_SCENARIO
    order = ("dallas", "kane", "ripley", "ash", "lambert", "parker", "brett")
    for i, cid in enumerate(order):
        crew = sim.state.crew[cid]
        assert crew.health == health[i], cid
        assert crew.fear == composure[i], cid
        if locs[i] == 0xFE:
            assert crew.room_id is None and not crew.alive
        else:
            assert crew.room_id == ROOM_SLUGS[locs[i]], cid


def test_short_and_full_now_differ() -> None:
    """This is what FV-1.9 got wrong: after the invented oxygen budget was
    removed the modes looked identical, but the ROM has its own SHORT setup."""
    import random

    short = Simulation(mode=GameMode.SHORT, rng=random.Random(7))
    full = Simulation(mode=GameMode.FULL, rng=random.Random(7))
    s = {c.id: (c.room_id, c.health, c.fear) for c in short.state.crew.values()}
    f = {c.id: (c.room_id, c.health, c.fear) for c in full.state.crew.values()}
    assert s != f


def test_short_starts_two_crew_already_in_the_ducts() -> None:
    """[C $605A-$605F] `$6502`/`$6508` = 1 — the `$6501` in-duct array at
    slots 1 and 7, i.e. DALLAS and BRETT."""
    import random

    short = Simulation(mode=GameMode.SHORT, rng=random.Random(2))
    assert sorted(c.id for c in short.state.crew.values() if c.in_duct) == [
        "brett", "dallas"
    ]
    full = Simulation(mode=GameMode.FULL, rng=random.Random(2))
    assert not any(c.in_duct for c in full.state.crew.values())


def test_short_pulls_three_items_into_commdcentr() -> None:
    """[C $6051-$6057] room 6 into the `$82E3` item-room array at instances
    7/16/17 — a TRACKER, the NET and the CAT BOX, straight into the room where
    three of the crew start."""
    import random

    short = Simulation(mode=GameMode.SHORT, rng=random.Random(2))
    there = sorted(
        i.type_id for i in short.state.items.values() if i.room_id == "commdcentr"
    )
    for expect in ("cat_box", "net", "tracker"):
        assert expect in there, expect
    full = Simulation(mode=GameMode.FULL, rng=random.Random(2))
    full_there = {
        i.type_id for i in full.state.items.values() if i.room_id == "commdcentr"
    }
    assert "cat_box" not in full_there and "net" not in full_there
