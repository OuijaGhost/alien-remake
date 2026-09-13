"""Regression/oracle verification (updated for 1:1 fidelity).

The original suite verified the PCS obedience gate's empirical obey rate
against `CrewMember.compliance` — but the full disassembly showed that entire
gate was an **invention** (no compliance roll exists on the decoded order path;
D-018: crew obey MOVE orders regardless of fear). Those tests are replaced by a
regression that pins the corrected behaviour: orders are always executed.

The wall-clock pacing check remains: `runner.run_realtime` against the real
clock, guarding the `TICK_HZ` cadence (GAME_SPEC §2, raster-IRQ divider).

Numbers with no recovered oracle (oxygen rate, item odds) are documented in
`docs/re/VICE_CHECKS.md`, not coded around.
"""

from __future__ import annotations

import random

from alien_remake.core import constants as _constants
import time

from alien_remake.core import constants
from alien_remake.core.alien import Alien
from alien_remake.core.crew import CrewMember, Role
from alien_remake.core.map import Room, ShipMap
from alien_remake.core.orders import Order, OrderOutcome, OrderType
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GameState
from alien_remake.render.base import NullRenderer
from alien_remake.runner import run_realtime


def test_orders_execute_at_every_fear_level() -> None:
    # 1:1 regression: the decoded order path has no compliance roll, so a MOVE
    # order completes at fear 0, mid, and max alike (only the walk timer applies).
    for fear in (0, 5, constants.FEAR_MAX):
        ship = ShipMap()
        ship.add_room(Room("A", 0, "A", 0, 0))
        ship.add_room(Room("B", 0, "B", 1, 0))
        ship.add_door("A", "B")
        crew = CrewMember("t", "Test", Role.CAPTAIN, "A", fear=fear, walk_ticks=1)
        # **P3-2/D-103:** a second, calm crew member keeps the game running.
        # With only a fear-0 character aboard the endgame scan ends it
        # immediately (`$5B6C LDA $7D55,Y / BEQ` — nobody BROKEN counts as in
        # play), and `advance()` returns before any order is processed. That is
        # correct behaviour; this test is about fear not *blocking an order*,
        # so the two must be kept apart.
        keeper = CrewMember("k", "Keeper", Role.CAPTAIN, "B", fear=5)
        sim = Simulation(
            state=GameState(crew={"t": crew, "k": keeper}, alien=Alien(room_id=None)),
            ship=ship,
            rng=random.Random(99),
        )
        sim.queue_order(Order("t", OrderType.MOVE_TO, "B"))
        # P3-2: a room move is the ROM's flat `#$40` plus the per-slot and
        # per-health delays (`$7B69` -> `compute_action_delay $4042`), not one
        # tick. What this test is really about is that fear never blocks the
        # order, so run the move out and check it completed.
        seen = []
        for _ in range(_constants.MOVE_ACTION_TICKS + sim._action_delay_for(crew) + 2):
            sim.advance()
            seen.extend(o[1] for o in sim.last_outcomes)
        assert crew.room_id == "B", f"order must execute at fear={fear}"
        assert OrderOutcome.COMPLETED in seen


def test_runner_honors_tick_hz_against_the_real_wall_clock() -> None:
    """A real (unmocked) clock run stays close to the ~6.25 Hz tick rate.

    This is a self-consistency check, not a comparison to a captured original-game
    recording — it guards against a
    regression that silently breaks the pacing loop's honoring of TICK_HZ.
    """
    sim = Simulation()
    ticks = 8
    expected_seconds = ticks / constants.TICK_HZ
    start = time.perf_counter()
    ran = run_realtime(sim, NullRenderer(), max_ticks=ticks)
    elapsed = time.perf_counter() - start
    assert ran == ticks
    # Wide tolerance: this only needs to catch a broken pacing loop (e.g. no
    # sleep at all, or sleeping a fixed unrelated duration), not measure jitter.
    assert 0.5 * expected_seconds <= elapsed <= 2.0 * expected_seconds
