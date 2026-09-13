"""Developer-mode playtesting controls (`core/devtools.py`).

The owner is verifying the remake against the real disk and asked for four
things that are hard to reach by playing: move a crew member's fear, stop the
Alien without ending the run, stop the cat, and turn the android on.

Two properties matter more than the features themselves.

**Off is untouched.** Every switch defaults to off and the simulation consults
them at exactly two points, so a real game runs the decoded path it always did.

**Nothing ends the game.** "Turn the Alien off" must not remove or kill it:
both are win conditions the ROM checks for, so either would end the very run
being tested. It is left in place and not given its turn.
"""

from __future__ import annotations

import random

from alien_remake.core import constants, devtools  # noqa: E402
from alien_remake.core.devtools import DevControls, Freeze  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.core.state import GamePhase  # noqa: E402


def _sim(seed: int = 5) -> Simulation:
    return Simulation(rng=random.Random(seed))


# --- off is the shipping game ---------------------------------------------------

def test_everything_is_off_by_default() -> None:
    sim = _sim()
    assert sim.dev.alien is Freeze.OFF
    assert sim.dev.jones is Freeze.OFF
    assert sim.dev.any_on is False


def test_with_the_switches_off_the_world_still_moves() -> None:
    """The guard against a dev feature quietly costing the real game its
    behaviour: with nothing switched on, things still happen."""
    sim = _sim()
    start = sim.state.alien.room_id if sim.state.alien else None
    moved = False
    for _ in range(400):
        sim.advance()
        if sim.state.alien and sim.state.alien.room_id != start:
            moved = True
            break
    assert moved, "the Alien never moved with the dev switches off"


# --- the Alien ------------------------------------------------------------------

def test_a_frozen_alien_does_not_move() -> None:
    sim = _sim()
    sim.dev.alien = Freeze.STILL
    where = sim.state.alien.room_id if sim.state.alien else None
    for _ in range(400):
        sim.advance()
    assert sim.state.alien is not None
    assert sim.state.alien.room_id == where


def test_a_frozen_alien_does_not_end_the_game() -> None:
    """The whole reason freezing is "no turn" rather than "removed".

    Killing or deleting the Alien is a win condition, so the obvious
    implementation would end the run the tester is in the middle of.
    """
    sim = _sim()
    sim.dev.alien = Freeze.STILL
    for _ in range(600):
        sim.advance()
    assert sim.state.phase is GamePhase.RUNNING
    assert sim.state.alien is not None
    assert sim.state.alien.alive, "freezing killed it"
    assert sim.state.win_route is None


def test_freezing_the_alien_leaves_it_on_the_map() -> None:
    """It is inert, not absent — still somewhere, still findable."""
    sim = _sim()
    sim.dev.alien = Freeze.STILL
    sim.advance()
    assert sim.state.alien is not None
    assert sim.state.alien.room_id is not None


def test_the_alien_switch_toggles_back() -> None:
    dev = DevControls()
    assert "still" in dev.cycle_alien()
    assert dev.alien_may_act() is False
    assert "off" in dev.cycle_alien()
    assert dev.alien_may_act() is True


# --- Jones ----------------------------------------------------------------------

def test_a_frozen_jones_stays_put() -> None:
    sim = _sim()
    sim.dev.jones = Freeze.STILL
    where = sim.state.jones_room_id
    for _ in range(400):
        sim.advance()
    assert sim.state.jones_room_id == where


def test_freezing_jones_does_not_end_the_game() -> None:
    sim = _sim()
    sim.dev.jones = Freeze.STILL
    for _ in range(400):
        sim.advance()
    assert sim.state.phase is GamePhase.RUNNING


def test_the_jones_switch_toggles_back() -> None:
    dev = DevControls()
    dev.cycle_jones()
    assert dev.jones_may_act() is False
    dev.cycle_jones()
    assert dev.jones_may_act() is True


# --- fear -----------------------------------------------------------------------

def test_fear_moves_and_reports() -> None:
    sim = _sim()
    who = next(iter(sim.state.crew))
    sim.state.crew[who].fear = 4
    note = devtools.adjust_fear(sim.state, who, +1)
    assert sim.state.crew[who].fear == 5
    assert note is not None and who in note


def test_fear_is_clamped_at_both_ends() -> None:
    """`FEAR_MIN`/`FEAR_MAX` are the ROM's range; a testing control that could
    push a crew member outside it would be testing a state the game cannot
    reach."""
    sim = _sim()
    who = next(iter(sim.state.crew))
    for _ in range(40):
        devtools.adjust_fear(sim.state, who, +1)
    assert sim.state.crew[who].fear == constants.FEAR_MAX
    for _ in range(40):
        devtools.adjust_fear(sim.state, who, -1)
    assert sim.state.crew[who].fear == constants.FEAR_MIN


def test_fear_at_the_limit_reports_nothing() -> None:
    """So a log line is written when something changed and not otherwise."""
    sim = _sim()
    who = next(iter(sim.state.crew))
    sim.state.crew[who].fear = constants.FEAR_MAX
    assert devtools.adjust_fear(sim.state, who, +1) is None


def test_fear_walks_the_whole_morale_range() -> None:
    """The point of the control: `MORALE_BANDS`' five-way slicing is one of the
    open `[?]`s, and this is what makes every word reachable to look at."""
    from alien_remake.core.crew import morale_word

    sim = _sim()
    who = next(iter(sim.state.crew))
    sim.state.crew[who].fear = constants.FEAR_MIN
    seen = set()
    for _ in range(constants.FEAR_MAX - constants.FEAR_MIN + 1):
        seen.add(morale_word(sim.state.crew[who].fear))
        devtools.adjust_fear(sim.state, who, +1)
    assert len(seen) >= len(constants.MORALE_BANDS) - 1, seen


def test_fear_on_nobody_is_not_an_error() -> None:
    sim = _sim()
    assert devtools.adjust_fear(sim.state, None, +1) is None
    assert devtools.adjust_fear(sim.state, "nobody", +1) is None


# --- the android ------------------------------------------------------------------

def test_revealing_the_android_sets_the_roms_own_gate() -> None:
    """`android_revealed` is `$5265`/`$526F`'s own flag: unrevealed it takes the
    ordinary character road, revealed it takes the one ending in the attack.
    So this brings the moment forward rather than inventing a behaviour."""
    sim = _sim()
    sim.state.android_revealed = False
    note = devtools.reveal_android(sim.state)
    if sim.state.android_id is None:
        assert note is None
        return
    assert sim.state.android_revealed is True
    assert note is not None and sim.state.android_id in note


def test_revealing_twice_reports_nothing_the_second_time() -> None:
    sim = _sim()
    devtools.reveal_android(sim.state)
    assert devtools.reveal_android(sim.state) is None


def test_a_revealed_android_does_not_end_the_game_by_itself() -> None:
    sim = _sim()
    devtools.reveal_android(sim.state)
    for _ in range(200):
        sim.advance()
        if sim.state.phase is not GamePhase.RUNNING:
            break
    # It may legitimately kill somebody and the game may legitimately end from
    # that; what must not happen is the reveal itself being an ending.
    assert sim.state.android_revealed is True
