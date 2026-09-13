"""Bridges the headless :class:`Simulation` to a :class:`Renderer`.

The simulation core never sleeps; this runner is the **only** place wall-clock
pacing happens, so the model stays deterministic for tests. The pace target is
``TICK_HZ`` (GAME_SPEC §2). ``sleep`` and ``now`` are injectable so tests can run
the loop with no real delay.

Two loops share that core:

* :func:`run_realtime` - the original. One fixed tick per iteration, sleeping
  off the remainder, which is what the ROM's main loop does.
* :func:`run_turn_based` - **one turn is "advance until something resolves"**
  (T1, option 2). It sleeps not at all.

**Why that definition of a turn, and what it costs** (T1/T3, decided
2026-08-18):

One turn = one tick is faithful but nearly empty - a single room move is three
or four of them, so the player would spend most turns pressing nothing. One turn
= everyone acts once is the classic roguelike answer and was rejected in the
register: the characters have *different* action delays (`$6586`, and the
per-character tables behind `compute_action_delay`), and flattening them deletes
a decoded mechanic that is most of the game's characterisation.

"Advance until something resolves" keeps every one of those and asks the player
for input exactly when there is something to decide.

**The consequence that settles T3.** This loop advances *real ticks* - it does
not substitute turns for them. A turn simply spans however many ticks the next
resolution took. So every tick-denominated constant keeps its exact meaning: the
auto-destruct is still 2550 passes, `FIRE_SPREAD_EVERY_TICKS` still fires on the
same schedule, and the row-24 banner still expires when it did. Nothing needs
re-denominating, and the mode cannot make the destruct trivial or unsurvivable,
because it does not change how many ticks anything takes. That is the whole
reason this definition was the recommended one.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from .core.constants import TICK_HZ
from .core.orders import SURVIVING_OUTCOMES
from .core.sound import SoundCue
from .core.sim import Simulation
from .core.state import GamePhase
from .render.base import Renderer

#: The ceiling on a turn that is **waiting for something**, in ticks.
#:
#: It must exceed the slowest ordinary action or it truncates one, which is
#: worse than useless: the turn ends with the order still in flight and the
#: player is asked to act again for no reason. Measured, not guessed - a room
#: move costs 64 ticks for Ripley and 74 for Parker, and REMVGRILLE is 180 for
#: Ripley or Lambert before the wounded penalty of +48. 256 clears all of it.
MAX_TICKS_PER_TURN = 256

#: The ceiling on an **idle** turn - one with no orders in flight at all.
#:
#: These are different questions and giving them one answer is a bug either way
#: round. Bound an idle turn by `MAX_TICKS_PER_TURN` and the player who issues
#: no order hands the world 256 ticks - thirty-two seconds, four Alien actions -
#: before being asked again, which is long enough for the Alien to reach someone
#: and kill them with no chance to react. Bound a *pending* turn by this one and
#: every action gets truncated.
#:
#: One Alien action (`ALIEN_MOVE_TICKS`) is the natural quantum for doing
#: nothing: the world moves once, then you are asked again.
MAX_IDLE_TICKS_PER_TURN = 60


def run_realtime(
    sim: Simulation,
    renderer: Renderer,
    *,
    tick_hz: float = TICK_HZ,
    max_ticks: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.perf_counter,
) -> int:
    """Run the real-time loop until the game ends, the user quits, or ``max_ticks``.

    Each iteration: poll the renderer for orders, advance one fixed tick, render,
    then sleep off the remainder of the tick period. Returns the number of ticks
    run.
    """
    period = 1.0 / tick_hz
    ticks = 0
    while sim.state.phase is GamePhase.RUNNING and not renderer.should_quit():
        start = now()
        for order in renderer.poll_orders():
            sim.queue_order(order)
        for option in renderer.poll_special_options():
            sim.apply_special_option(option)
        sim.advance()
        renderer.render(sim.state)
        ticks += 1
        if max_ticks is not None and ticks >= max_ticks:
            break
        remaining = period - (now() - start)
        if remaining > 0:
            sleep(remaining)
    return ticks


def advance_until_resolution(
    sim: Simulation,
    *,
    max_ticks: int = MAX_TICKS_PER_TURN,
    max_idle_ticks: int = MAX_IDLE_TICKS_PER_TURN,
) -> int:
    """Advance until an order resolves or the game ends. Returns ticks spent.

    T5. Pure - no wall clock, no renderer - so it is usable from a test, a
    turn-based loop, or a headless probe.

    "Something resolved" means an order reached a **terminal** outcome. It is
    deliberately not "`last_outcomes` is non-empty": a MOVE reports
    `IN_TRANSIT` on the tick it is accepted and every tick it is still walking,
    so that reading ends the turn immediately and the mode collapses back into
    one-turn-per-tick. The first version of this did exactly that, and the test
    that compares Ripley against Parker caught it - both "resolved" in one tick,
    which is the tell that no delay was being waited out at all.

    `SURVIVING_OUTCOMES` is the model's own name for the ones that keep an order
    in the queue, so the terminal set is its complement and stays correct if a
    new outcome is added.

    Two ceilings, because they answer different questions. ``max_ticks`` bounds
    a turn that is waiting for an action to finish, and has to clear the slowest
    one. ``max_idle_ticks`` bounds a turn with nothing in flight at all, and
    wants to be *short*: a player who issues no order should not hand the world
    four Alien actions before being asked again. Neither is a budget - nothing
    is being spent, and the simulation is identical either way.
    """
    ticks = 0
    # **Collect the cues as we go (T7).** `Simulation.advance()` opens by
    # clearing `sound_cues`, so a turn spanning seventy ticks would surface only
    # the seventieth tick's audio and silently drop the rest -- the movement
    # blips of the walk, the grille burst that happened on the way. Gathering
    # them here is what makes a turn's sound the turn's, rather than its last
    # instant's.
    heard: list[SoundCue] = []
    # Nothing queued and nobody mid-action: this is an idle turn, so use the
    # short ceiling. Checked once up front rather than per tick - an order
    # arriving mid-turn is the *next* turn's business, and re-deciding halfway
    # would make a turn's length depend on when the world happened to act.
    idle = not sim._orders and all(
        crew.step_timer == 0 for crew in sim.state.crew.values()
    )
    ceiling = max_idle_ticks if idle else max_ticks
    while ticks < ceiling:
        sim.advance()
        ticks += 1
        heard.extend(sim.state.sound_cues)
        if sim.state.phase is not GamePhase.RUNNING:
            break
        if any(outcome not in SURVIVING_OUTCOMES
               for _order, outcome in sim.last_outcomes):
            break

    # ...and coalesce them, because playing twenty identical movement blips at
    # once is a burst, not a walk. First occurrence of each distinct cue wins,
    # so the order the machine produced them in survives. This is presentation
    # only: the simulation already happened, tick by tick, unchanged.
    seen: set[tuple[str, str | None]] = set()
    coalesced: list[SoundCue] = []
    for cue in heard:
        key = (cue.effect, cue.crew_id)
        if key not in seen:
            seen.add(key)
            coalesced.append(cue)
    sim.state.sound_cues[:] = coalesced
    return ticks


def run_turn_based(
    sim: Simulation,
    renderer: Renderer,
    *,
    max_turns: int | None = None,
    max_ticks_per_turn: int = MAX_TICKS_PER_TURN,
) -> int:
    """Run the turn-based loop until the game ends or the user quits.

    Returns the number of **turns** taken. Each iteration takes the player's
    orders, advances until one of them resolves, and renders once - so the
    screen updates on events rather than on a clock, and the loop never sleeps.
    """
    turns = 0
    while sim.state.phase is GamePhase.RUNNING and not renderer.should_quit():
        for order in renderer.poll_orders():
            sim.queue_order(order)
        for option in renderer.poll_special_options():
            sim.apply_special_option(option)
        advance_until_resolution(sim, max_ticks=max_ticks_per_turn)
        renderer.render(sim.state)
        turns += 1
        if max_turns is not None and turns >= max_turns:
            break
    return turns
