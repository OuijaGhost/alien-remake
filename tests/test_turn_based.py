"""The turn-based loop (T1/T4/T5).

One turn is "advance until something resolves". The tests worth having are the
ones that pin *why* that definition was chosen over the other two: it must keep
the per-character action delays that a fixed "everyone acts once" turn would
flatten, and it must not change how many ticks anything takes, because that is
what stops the mode re-denominating the auto-destruct.
"""

from __future__ import annotations

from alien_remake.core.modes import DeathVariant, GameMode
from alien_remake.core.orders import SURVIVING_OUTCOMES, Order, OrderType
from alien_remake.core.flow import default_simulation
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GamePhase, GameState
from alien_remake.runner import (
    MAX_TICKS_PER_TURN,
    advance_until_resolution,
    run_turn_based,
)


class _Recorder:
    """A renderer that records, and optionally quits after N renders."""

    def __init__(self, quit_after: int | None = None) -> None:
        self.frames = 0
        self.orders: list[Order] = []
        self._quit_after = quit_after

    def render(self, state: GameState) -> None:
        self.frames += 1

    def poll_orders(self) -> list[Order]:
        out, self.orders = self.orders, []
        return out

    def poll_special_options(self) -> list[object]:
        return []

    def should_quit(self) -> bool:
        return self._quit_after is not None and self.frames >= self._quit_after


def _sim() -> Simulation:
    return default_simulation(GameMode.FULL, DeathVariant.FIXED)


def _mover(sim: Simulation):
    """A crew member who can be ordered, and somewhere to send them."""
    crew = next(
        c for c in sim.state.crew.values()
        if c.alive and c.health >= 2 and c.id != sim.state.android_id
    )
    assert crew.room_id is not None
    return crew, sim.ship.door_neighbors(crew.room_id)[0]


# --- T5: advance until something resolves ---------------------------------


def test_a_turn_ends_when_an_order_resolves() -> None:
    """Not after a fixed count - when the model records an outcome."""
    sim = _sim()
    crew, destination = _mover(sim)
    sim.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))

    ticks = advance_until_resolution(sim)
    assert sim.last_outcomes, "the turn ended without anything resolving"
    assert 1 <= ticks <= MAX_TICKS_PER_TURN


def test_an_empty_turn_is_bounded_rather_than_endless() -> None:
    """With nothing queued nothing resolves, and the player must still get a go."""
    sim = _sim()
    # An empty sim takes the *idle* ceiling, so that is the one to bound here.
    ticks = advance_until_resolution(sim, max_idle_ticks=5)
    assert ticks == 5
    assert sim.state.phase is GamePhase.RUNNING


def test_a_turn_stops_the_moment_the_game_ends() -> None:
    sim = _sim()
    for crew in sim.state.crew.values():           # everyone down -> a loss
        crew.health, crew.alive = 0, False
    ticks = advance_until_resolution(sim)
    assert sim.state.phase is not GamePhase.RUNNING
    assert ticks < MAX_TICKS_PER_TURN, "it kept going after the game was over"


# --- the reason for this definition ---------------------------------------


def test_turns_do_not_change_how_many_ticks_an_order_takes() -> None:
    """T3, as a test: a turn spans real ticks, it does not replace them.

    The same order costs the same number of ticks whether it is advanced one
    tick at a time or inside a turn. That is what keeps every tick-denominated
    constant - the auto-destruct above all - meaning exactly what it meant.
    """
    # **The same named character in both runs.** `default_simulation` picks its
    # victim and android per call, so "the first eligible crew member" is not
    # the same person twice - and comparing Brett's 69 ticks against Dallas's 71
    # is exactly the apples-to-oranges this test exists to rule out.
    who = "ripley"

    by_hand = _sim()
    crew = by_hand.state.crew[who]
    crew.health = max(crew.health, 4)
    assert crew.room_id is not None
    destination = by_hand.ship.door_neighbors(crew.room_id)[0]
    by_hand.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
    manual = 0
    while manual < MAX_TICKS_PER_TURN:
        by_hand.advance()
        manual += 1
        # The same terminal-outcome rule the runner uses: IN_TRANSIT means the
        # order is still walking, and counting it as "resolved" was the bug the
        # speeds test below caught.
        if any(o not in SURVIVING_OUTCOMES for _order, o in by_hand.last_outcomes):
            break

    by_turn = _sim()
    crew2 = by_turn.state.crew[who]
    crew2.health = max(crew2.health, 4)
    assert crew2.room_id is not None
    destination2 = by_turn.ship.door_neighbors(crew2.room_id)[0]
    by_turn.queue_order(Order(crew2.id, OrderType.MOVE_TO, destination2))
    assert advance_until_resolution(by_turn) == manual


def test_the_characters_keep_their_different_speeds() -> None:
    """Why "everyone acts once" was rejected.

    The per-character delays are decoded (`compute_action_delay` and its
    tables); a fixed turn would flatten them. Under this model two characters
    given the same order resolve after different numbers of ticks.
    """
    seen = {}
    for crew_id in ("ripley", "parker"):
        sim = _sim()
        crew = sim.state.crew[crew_id]
        crew.health = max(crew.health, 4)          # health also taxes the delay
        assert crew.room_id is not None
        destination = sim.ship.door_neighbors(crew.room_id)[0]
        sim.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
        seen[crew_id] = advance_until_resolution(sim)
    assert seen["ripley"] != seen["parker"], (
        f"the two resolve identically ({seen}) - the delay table is not in play"
    )


# --- T4: the loop ----------------------------------------------------------


def test_the_loop_renders_once_per_turn_and_never_sleeps() -> None:
    """It takes no `sleep` argument at all, so it cannot pace itself by a clock."""
    import inspect

    sim = _sim()
    renderer = _Recorder()
    turns = run_turn_based(sim, renderer, max_turns=4)
    assert turns == 4 and renderer.frames == 4
    assert "sleep" not in inspect.signature(run_turn_based).parameters


def test_the_loop_stops_when_the_renderer_quits() -> None:
    sim = _sim()
    renderer = _Recorder(quit_after=2)
    assert run_turn_based(sim, renderer, max_turns=99) == 2


# --- T7: a turn's sound is the turn's, not its last instant's --------------


def test_a_turn_keeps_the_cues_from_every_tick_it_spanned() -> None:
    """`advance()` clears `sound_cues`, so a long turn would drop all but the last.

    The walk itself makes the noise - a movement blip per step - and a turn that
    surfaced only its final tick would be silent for the journey and then click
    once on arrival.
    """
    sim = _sim()
    crew, destination = _mover(sim)
    sim.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
    advance_until_resolution(sim)
    assert sim.state.sound_cues, "the whole turn's audio was lost"


def test_the_cues_are_coalesced_rather_than_burst() -> None:
    """Twenty identical blips at once is a burst, not a walk.

    One of each distinct cue, in the order the machine first produced it.
    """
    sim = _sim()
    crew, destination = _mover(sim)
    sim.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
    advance_until_resolution(sim)

    keys = [(c.effect, c.crew_id) for c in sim.state.sound_cues]
    assert len(keys) == len(set(keys)), f"duplicate cues survived: {keys}"


def test_coalescing_does_not_touch_the_simulation() -> None:
    """Presentation only: the ticks still happened one at a time.

    Same order, same tick cost, whether or not anything listened.
    """
    quiet = _sim()
    crew, destination = _mover(quiet)
    quiet.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
    ticks = advance_until_resolution(quiet)
    assert quiet.state.crew[crew.id].room_id == destination
    assert ticks > 1, "the move resolved instantly; the delay was skipped"


# --- T8: the real-time path must stay exactly as it was --------------------


def test_realtime_still_advances_exactly_one_tick_per_iteration() -> None:
    """Its contract, asserted rather than assumed.

    The turn-based loop was added *beside* this one, sharing the simulation but
    not its pacing. If `advance_until_resolution` ever leaked into the
    real-time path, a single iteration would swallow a whole action and the
    30 fps loop would stutter a room-move at a time.
    """
    from alien_remake.runner import run_realtime

    sim = _sim()
    renderer = _Recorder()
    before = sim.state.tick
    ticks = run_realtime(sim, renderer, max_ticks=5, sleep=lambda _s: None,
                         now=lambda: 0.0)
    assert ticks == 5
    assert sim.state.tick - before == 5, "an iteration advanced more than one tick"
    assert renderer.frames == 5, "real time renders once per tick"


def test_the_two_loops_do_not_share_pacing_arguments() -> None:
    """One is clock-paced and one is event-paced; the signatures should say so."""
    import inspect

    from alien_remake.runner import run_realtime

    realtime = inspect.signature(run_realtime).parameters
    turns = inspect.signature(run_turn_based).parameters
    assert "sleep" in realtime and "tick_hz" in realtime
    assert "sleep" not in turns and "tick_hz" not in turns


# --- the two ceilings answer different questions ---------------------------


def test_an_idle_turn_is_short_and_a_pending_one_is_not() -> None:
    """One ceiling for both would be a bug whichever value it took.

    An idle turn bounded by the pending ceiling hands the world 256 ticks --
    four Alien actions -- before the player is asked again, which is long enough
    to be killed without a chance to react. A pending turn bounded by the idle
    ceiling truncates every action instead.
    """
    from alien_remake.runner import MAX_IDLE_TICKS_PER_TURN

    idle = _sim()
    assert advance_until_resolution(idle) == MAX_IDLE_TICKS_PER_TURN

    busy = _sim()
    crew, destination = _mover(busy)
    busy.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
    spent = advance_until_resolution(busy)
    assert spent > MAX_IDLE_TICKS_PER_TURN, (
        f"a real action finished in {spent} ticks -- the idle ceiling truncated it"
    )


def test_an_idle_turn_still_lets_the_world_move_once() -> None:
    """Doing nothing is a choice, not a pause: the Alien still gets its action."""
    from alien_remake.core import constants

    from alien_remake.runner import MAX_IDLE_TICKS_PER_TURN

    assert MAX_IDLE_TICKS_PER_TURN >= constants.ALIEN_MOVE_TICKS
    sim = _sim()
    before = sim.state.tick
    advance_until_resolution(sim)
    assert sim.state.tick - before >= constants.ALIEN_MOVE_TICKS
