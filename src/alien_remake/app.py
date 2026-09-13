"""The graphical app loop: drives the screen flow, paced in real time.

Unlike :func:`~alien_remake.runner.run_realtime` (which only knows how to run a
*single already-built Simulation* and is what ``--headless`` uses), this loop
drives the whole :class:`~alien_remake.core.flow.GameFlow`: title → selection →
opening → play → end. Input is polled once per frame as abstract
:class:`~alien_remake.core.flow.InputEvent`s and routed to the flow; while the
flow is on the play screen, the Simulation is advanced at ``tick_hz`` and player
orders/Special Options are drained from the same backend.

The backend is duck-typed (see :class:`AppRenderer`) so a headless fake can
drive the loop in tests without pygame.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from .core.alien import weapon_would_breach
from .core.constants import (
    NOTICE_TICKS, TICK_HZ, TURN_ALIEN_ACTOR, TURN_CREATURE_SLOT_TICKS,
)
from .core.flow import TIMED_SCREENS, GameFlow, InputEvent, Screen
from .core.journal import Journal
from .core.orders import Order, OrderType
from .core.special_options import SpecialOption
from .core.state import GameState


class AppRenderer(Protocol):
    """What :func:`run_app` needs from a screen-aware rendering/input backend."""

    def poll_input(self, screen: Screen) -> list[InputEvent]:
        """Drain input for this frame as abstract events (screen-dependent)."""
        ...

    def poll_orders(self) -> list[Order]:
        """Play-screen orders classified during the last :meth:`poll_input`."""
        ...

    def poll_special_options(self) -> list[SpecialOption]:
        """Play-screen Special Options from the last :meth:`poll_input`."""
        ...

    def draw(self, flow: GameFlow) -> None:
        """Draw the screen the flow is currently on."""
        ...

    def play_sound_cues(self, state: GameState) -> tuple[str, ...]:
        """Play the tick's SID cues, gated as the ROM gates them (D-088)."""
        ...

    def idle(self, seconds: float) -> None:
        """Wait out the rest of the frame. **Optional** -- see `run_app`."""
        ...

    def should_quit(self) -> bool: ...

    def close(self) -> None: ...


def run_app(
    flow: GameFlow,
    renderer: AppRenderer,
    *,
    journal: Journal | None = None,
    tick_hz: float = TICK_HZ,
    frame_hz: float = 30.0,
    now: Callable[[], float] = time.perf_counter,
    sleep: Callable[[float], None] = time.sleep,
    max_frames: int | None = None,
) -> int:
    """Run the screen-driven loop until the user quits (or ``max_frames``).

    Returns the number of frames drawn. The loop runs at ``frame_hz`` for
    responsive menus; the Simulation only advances on the ``tick_hz`` schedule
    while the flow is on the play screen, so world time is independent of the
    display frame rate.
    """
    # The backend may want the frame's leftover time rather than a plain
    # sleep: the CRT layer re-presents the same field at 120 Hz while the game
    # keeps drawing at 30 (DISC-264). Looked up rather than required, because
    # the headless fakes this loop is deliberately testable with do not have it
    # -- and because the loop must stay honest about who is doing the waiting.
    idle = getattr(renderer, "idle", None)
    tick_period = 1.0 / tick_hz
    frame_period = 1.0 / frame_hz
    last_tick = now()
    frames = 0

    # `flow.finished` is EXITO's `SYS 64738`: the Q/QUIT advert has held its
    # `FOR XX=1TO3000` and the program ends (D-185).
    while not renderer.should_quit() and not flow.finished:
        frame_start = now()

        for event in renderer.poll_input(flow.screen):
            flow.handle(event)

        if flow.screen is Screen.PLAYING and flow.sim is not None:
            # **[C $5904] D-187 — drain the handler-raised cues HERE.**
            # `MenuController.fire()` applies orders and Special Options
            # *straight to the sim* during `poll_input` above (which is why
            # `poll_orders`/`poll_special_options` are always empty). So by this
            # point `blowlock_sfx`'s crack is already sitting in `sound_cues` -
            # and `advance()` below opens with `sound_cues.clear()`, so unless
            # it is played now it is thrown away. That silence was the whole of
            # D-186's bug; D-186's own fix drained inside the
            # `poll_special_options` loop, which never iterates.
            renderer.play_sound_cues(flow.sim.state)
            flow.sim.state.sound_cues.clear()
            new_orders = renderer.poll_orders()
            new_specials = renderer.poll_special_options()
            for order in new_orders:
                flow.sim.queue_order(order)
            for option in new_specials:
                flow.sim.apply_special_option(option)
            # **C2/T6 — turns, read live off the options screen (DISC-292's
            # `run_turn_based`/`advance_until_resolution`, now reachable from
            # the game's own window instead of only `--headless-turns`).**
            # Checked every frame, the same as `crt`/`front_end` above it on
            # the options screen — "changes apply at once" is already this
            # screen's own rule, and turns has nowhere else to live: it is not
            # a simulation rule like `jones`/`death` (nothing in `_LiveRules`
            # changes), only how often this loop is willing to call `advance`.
            turn_based = flow.options.values.get("turns") == "on"
            advanced = False
            if turn_based:
                # **Nothing moves until you act.** A tabletop turn-based game
                # does not clock-tick while you are still deciding, and the
                # help text on the options row says exactly that - so unlike
                # `run_turn_based`'s own reference loop (built for a headless
                # harness that must always make forward progress every
                # iteration), this only calls `advance_until_resolution` when
                # an order or Special Option actually arrived THIS frame.
                # `advance_until_resolution`'s own idle ceiling is real and
                # tested (`test_turn_based.py`) but is simply never reached
                # from here, because idle-with-nothing-queued is exactly the
                # "still deciding" state this branch leaves alone.
                #
                # **`flow.sim._orders`, not just `new_orders`/`new_specials`.**
                # The real backend's `MenuController.fire()` calls
                # `sim.queue_order`/`apply_special_option` directly *during*
                # `poll_input` (D-187's own finding) — `poll_orders()` and
                # `poll_special_options()` always come back empty for it, and
                # only the passive test fakes route orders through them. So
                # the actual "did something happen this frame" signal for real
                # play is whether an order is now sitting in the queue; a
                # Special Option has no such queue (it applies immediately),
                # which is the one gap here — a special fired with no order
                # also pending will not itself trigger an advance this frame.
                #
                # **Initiative gate — not the original.** `flow.turn_order` is
                # only non-empty when the "turns" option rolled one at `_start`
                # (`GameFlow._roll_initiative`); the disk has no such mode at
                # all, so an un-rolled order list (turns flipped on mid-run
                # without a restart) falls back to the plain event-driven pace
                # above rather than assume an actor that was never assigned.
                # A dead crew member still occupies their rolled slot (the
                # roster in `turn_order` is fixed at `_roll_initiative` and
                # never reshuffled), so skip straight past anyone who can no
                # longer act rather than stall the whole game waiting for
                # orders nobody can give. Bounded by `len(turn_order)` so an
                # all-dead crew can't spin forever before reaching Alien/Jones.
                for _ in range(len(flow.turn_order)):
                    actor = flow.current_turn_actor()
                    dead_crew = (
                        actor in flow.sim.state.crew
                        and not flow.sim.state.crew[actor].alive
                    )
                    if not dead_crew:
                        break
                    flow.advance_turn_actor()
                # **Auto-select (2026-09-05), not the original.** Whichever
                # crew member's order menu was open belongs to whoever's turn
                # it *was* — a player who has to manually re-navigate to the
                # new actor every time initiative passes is fighting the
                # feature. `select_crew` is optional (`getattr`, the same
                # pattern as `idle` below) so headless fakes need not grow it.
                select_crew = getattr(renderer, "select_crew", None)
                sim = flow.sim

                def _advance_actor() -> None:
                    flow.advance_turn_actor()
                    new_actor = flow.current_turn_actor()
                    if select_crew is not None and new_actor in sim.state.crew:
                        select_crew(new_actor)

                actor = flow.current_turn_actor()
                if flow.turn_order and actor in flow.sim.state.crew:
                    # **Skip turn (2026-09-05), not the original.** Checked
                    # before the out-of-turn filtering below: a skip ends the
                    # actor's turn unconditionally, so whatever is sitting in
                    # the queue for them is abandoned along with the rest of
                    # their action points, not resolved first.
                    from collections import deque

                    poll_skip_turn = getattr(renderer, "poll_skip_turn", None)
                    if poll_skip_turn is not None and poll_skip_turn():
                        flow.sim._orders = deque(
                            o for o in flow.sim._orders if o.crew_id != actor
                        )
                        _advance_actor()
                    else:
                        # Someone other than the crew member whose slot is
                        # live right now may already be sitting in the queue —
                        # `MenuController.fire()` queued it straight onto
                        # `flow.sim._orders` during `poll_input`, above,
                        # before this gate ever saw it. Drop it and say why,
                        # rather than let it fire silently out of turn.
                        out_of_turn = [
                            o for o in flow.sim._orders if o.crew_id != actor
                        ]
                        if out_of_turn:
                            flow.sim._orders = deque(
                                o for o in flow.sim._orders if o.crew_id == actor
                            )
                            waiting_for = flow.sim.state.crew[actor].name
                            flow.sim.state.notice = f"WAIT FOR {waiting_for.upper()}"
                            flow.sim.state.notice_ticks = NOTICE_TICKS
                        if flow.sim._orders or new_orders or new_specials:
                            from .runner import advance_until_resolution

                            # **DEC-045 — a forced DEC-044 retreat is free.**
                            # Captured *before* the order resolves: is the
                            # queued order for this actor a MOVE_TO, issued
                            # while standing somewhere `weapon_would_breach`
                            # says is too hot to land another hit in right
                            # now? If so, fleeing it is not a choice DEC-044
                            # left the player, and charging a full action
                            # point for landing zero progress toward the
                            # kill is what made turn-based UPDATED need an
                            # unreasonably large AP budget just to be
                            # winnable at all (see the AP sweep this
                            # decision cites). Real ATTACK orders, and any
                            # MOVE_TO issued from a room that is not
                            # gate-critical, are charged exactly as before.
                            crew = flow.sim.state.crew.get(actor)
                            fleeing_the_gate = False
                            if crew is not None and flow.sim.weapon_breach_gates:
                                pending = next(
                                    (o for o in flow.sim._orders
                                     if o.crew_id == actor), None,
                                )
                                if (pending is not None
                                        and pending.type is OrderType.MOVE_TO):
                                    held = (
                                        flow.sim.state.items.get(crew.holding)
                                        if crew.holding is not None else None
                                    )
                                    fleeing_the_gate = weapon_would_breach(
                                        flow.sim.state, crew.room_id,
                                        held.type_id if held is not None else None,
                                    )

                            advance_until_resolution(flow.sim)
                            advanced = True
                            flow.turn_count += 1
                            # One action point per order that actually
                            # reached a terminal outcome for the actor whose
                            # turn this is ("roughly one room move and one
                            # action" — the user's own phrasing for
                            # `TURN_ACTIONS_PER_TURN`). A MOVE_TO that is
                            # still `IN_TRANSIT` has not spent its point yet;
                            # `last_outcomes` only ever holds terminal
                            # outcomes in the first place (see
                            # `advance_until_resolution`'s own docstring).
                            if (
                                any(
                                    order.crew_id == actor
                                    for order, _outcome in flow.sim.last_outcomes
                                )
                                and not fleeing_the_gate
                            ):
                                flow.turn_actions_left -= 1
                                if flow.turn_actions_left <= 0:
                                    _advance_actor()
                elif flow.turn_order:
                    # The Alien's or Jones's own slot — neither takes player
                    # orders, so nothing here waits on `new_orders`/
                    # `new_specials` the way a crew slot does. Run its turn out
                    # to a bounded tick ceiling immediately and hand initiative
                    # straight back, same as a crew member spending their last
                    # action point.
                    from .runner import advance_until_resolution

                    advance_until_resolution(
                        flow.sim,
                        max_ticks=TURN_CREATURE_SLOT_TICKS,
                        max_idle_ticks=TURN_CREATURE_SLOT_TICKS,
                    )
                    advanced = True
                    flow.turn_count += 1
                    # **The creature-turn notice, not the original.** Set
                    # *after* the slot has already run its course, not before
                    # — a notice set going in would just be decremented away
                    # by `advance_until_resolution`'s own ticks before this
                    # frame is ever drawn (row 24 is a live simulation fact,
                    # ticked down once per `Simulation.advance()`, and the
                    # whole creature slot runs inline here, before `draw()`
                    # is called even once). Says *that* the Alien or Jones
                    # acted, never *what* — the point of a creature's own
                    # turn is that the player does not get to watch it decide.
                    label = "THE ALIEN" if actor == TURN_ALIEN_ACTOR else "JONES"
                    flow.sim.state.notice = f"{label} TOOK ITS TURN"
                    flow.sim.state.notice_ticks = NOTICE_TICKS
                    _advance_actor()
                elif flow.sim._orders or new_orders or new_specials:
                    from .runner import advance_until_resolution

                    advance_until_resolution(flow.sim)
                    advanced = True
                    flow.turn_count += 1
            elif frame_start - last_tick >= tick_period:
                flow.sim.advance()
                advanced = True
            if advanced:
                # Developer-mode session log, after the tick(s) resolved and
                # before the cues are cleared, so a line carries the state and
                # the noises it made together. Off by default and a single
                # attribute check when off (`core.journal`).
                if journal is not None:
                    journal.record(flow.sim.state)
                    # **R6.** The state a tick leaves behind does not say
                    # whether an order succeeded or was refused - a crew member
                    # who ignored an instruction looks identical to one never
                    # given it. `last_outcomes` is the one place that
                    # distinction exists, and only for the tick(s) it happened
                    # on, so it has to be caught here or it is gone.
                    for order, outcome in flow.sim.last_outcomes:
                        journal.note(
                            "outcome", crew=order.crew_id, type=order.type.name,
                            target=order.target, result=outcome.name,
                        )
                # The tick's SID call sites, gated by the ROM's own selection /
                # attack-mute tests (D-088/D-090). `advance_until_resolution`
                # already coalesces a whole turn's cues to one of each
                # distinct effect (T7), so this plays the same shape of thing
                # either way.
                renderer.play_sound_cues(flow.sim.state)
                # **DISC-226.** Without this, this tick's cues stay sitting in
                # `sound_cues` until the drain step at the top of the *next*
                # frame plays them again before clearing them — every cue
                # (movement blip, attack siren, grille burst) played twice,
                # one frame apart, for the whole run. Clear immediately,
                # matching the drain step above.
                flow.sim.state.sound_cues.clear()
                last_tick = frame_start
                flow.sync_phase()
        elif flow.screen in TIMED_SCREENS:
            # The timed cards (loading interstitials, title, opening notice)
            # advance on the same tick schedule — no input (R-30 / R-13 / D-021).
            if frame_start - last_tick >= tick_period:
                flow.tick()
                last_tick = frame_start
        elif flow.screen is Screen.ENDED:
            # **screen_fx (2026-09-04), not the original.** ENDED is not a
            # timed screen — it waits for any key via `_on_ended`, with no
            # auto-transition of its own — so `flow.tick()` (which only acts
            # on `TIMED_SCREENS`) never runs here and `_screen_ticks` would
            # otherwise sit frozen at whatever `sync_phase()` reset it to.
            # The wipe-in option reads it to pace the reveal, so it still
            # needs counting even though nothing here times out on it.
            if frame_start - last_tick >= tick_period:
                flow._screen_ticks += 1
                last_tick = frame_start

        renderer.draw(flow)
        frames += 1
        if max_frames is not None and frames >= max_frames:
            break

        remaining = frame_period - (now() - frame_start)
        if remaining > 0:
            # A backend with `idle` owns its own waiting -- including, for the
            # pygame one, deciding to spend the time refreshing the tube. The
            # injected `sleep` stays the fallback and the pacing hook for the
            # fakes that do not have it.
            if idle is not None:
                idle(remaining)
            else:
                sleep(remaining)

    return frames
