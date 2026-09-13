"""Tests for the headless Alien-remake core.

The core must be fully exercisable without pygame: a fixed-tick simulation, the
loss paths, async order queueing, and the real-time runner driven with an
injected (no-op) clock so the suite stays fast and deterministic.
"""

from __future__ import annotations

from alien_remake.core import constants
from alien_remake.core.alien import Alien
from alien_remake.core.orders import Order, OrderType
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GamePhase, GameState
from alien_remake.render.base import NullRenderer
from alien_remake.runner import run_realtime


def test_constants_trace_to_spec() -> None:
    # From the disassembly: the IRQ divider at $4D19 fires every NINE jiffies (reload
    # #$08, firing on the wrap below zero) — and it only drives sprites/sound.
    assert constants.IRQ_JIFFIES_PER_ANIM_TICK == 9
    # The IRQ paces sprite/sound animation only.
    assert constants.ANIM_HZ == 60.0 / 9.0
    # [C-live] R-29: the WORLD clock is the free-running main loop at $719D,
    # measured at 7.886 Hz (158 passes / 20.035 emulated s). It is NOT the
    # IRQ-derived animation rate — that conflation was the old approximation.
    assert constants.MAIN_LOOP_HZ == 7.886
    assert constants.TICK_HZ == constants.MAIN_LOOP_HZ
    assert constants.TICK_HZ != constants.ANIM_HZ


def test_advance_ticks_the_clock() -> None:
    sim = Simulation()
    sim.advance()
    sim.advance()
    assert sim.state.tick == 2
    assert sim.state.phase is GamePhase.RUNNING


def test_no_oxygen_system_exists() -> None:
    """De-invention guard (FV-2.5 / D-062).

    The C64 game has **no oxygen system**: R-22's monotonic-decrease scan of all
    game RAM found no counter; the complete 117-string inventory of ALIEN.prg
    has no OXYGEN/AIR/TOOH text; the status template ($7A10) shows only DAMAGE
    and MORALE; and the jiffy clock $A0-$A2 is never read. Keep it gone — the
    invented drain silently lost every run after ~7500 ticks.
    """
    for name in ("START_OXYGEN", "OXYGEN_PER_TICK", "SHORT_START_OXYGEN"):
        assert not hasattr(constants, name), f"{name} is an invention; must stay removed"
    assert not hasattr(GameState(), "oxygen"), "GameState.oxygen must stay removed"


def test_no_global_time_limit() -> None:
    """Nothing ends the game merely because time passed (FV-2.5 / D-062)."""
    sim = Simulation(GameState(awake_crew=3, alien=Alien(room_id=None)))
    sim.run(8000)  # comfortably past the old 7500-unit "budget"
    assert sim.state.tick == 8000
    assert sim.state.phase is GamePhase.RUNNING


def test_advance_is_a_noop_once_ended() -> None:
    # Auto-destruct is the only clock that can end a game (D-060).
    sim = Simulation(GameState(auto_destruct_ticks=1))
    sim.advance()  # -> LOST
    assert sim.state.phase is GamePhase.LOST
    tick_at_loss = sim.state.tick
    sim.advance()  # ignored
    assert sim.state.tick == tick_at_loss


def test_orders_are_queued_then_consumed_on_tick() -> None:
    sim = Simulation()  # calm default crew (fear 0) always obeys
    sim.queue_order(Order("ripley", OrderType.GET_ITEM, "taser"))
    sim.queue_order(Order("parker", OrderType.LEAVE_ITEM))
    assert sim.pending_orders == 2
    sim.advance()
    assert sim.pending_orders == 0  # both completed on the tick


def test_run_realtime_with_null_renderer_is_deterministic() -> None:
    sim = Simulation(GameState(awake_crew=1))
    slept: list[float] = []
    ticks = run_realtime(
        sim,
        NullRenderer(),
        max_ticks=10,
        sleep=slept.append,        # capture instead of sleeping
        now=lambda: 0.0,           # frozen clock -> full period "remaining"
    )
    assert ticks == 10
    assert sim.state.tick == 10
    # The loop breaks on the final tick before sleeping, so it sleeps max_ticks-1
    # times; with a frozen clock each sleep is the full tick period.
    assert len(slept) == 9
    assert all(s == 1.0 / constants.TICK_HZ for s in slept)


def test_run_realtime_stops_when_renderer_quits() -> None:
    sim = Simulation()
    # NullRenderer(quit_after=3) reports should_quit() True once polled 3 times.
    ticks = run_realtime(sim, NullRenderer(quit_after=3), sleep=lambda _: None)
    assert ticks == 3


def test_run_realtime_stops_when_game_lost() -> None:
    sim = Simulation(GameState(auto_destruct_ticks=2, awake_crew=1))
    ticks = run_realtime(sim, NullRenderer(), max_ticks=100, sleep=lambda _: None)
    assert sim.state.phase is GamePhase.LOST
    assert ticks == 2
