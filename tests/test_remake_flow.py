"""Tests for the screen/state machine and the app loop (headless, no pygame)."""

from __future__ import annotations

from alien_remake.app import run_app
from alien_remake.core import constants
from alien_remake.core.flow import (
    GameFlow,
    InputEvent,
    Screen,
    default_simulation,
)
from alien_remake.core.modes import FrontEnd, DeathVariant, GameMode
from alien_remake.core.state import GamePhase
from alien_remake.core import options


# The key that advances each input-gated front-end screen toward the game.
_FRONTEND_KEY = {
    Screen.NOTICE: InputEvent.FIRE,          # "press any key"
    Screen.WELCOME: InputEvent.SELECT_FULL,  # "1 ALIEN"
    Screen.INSTRUCTIONS: InputEvent.NO,      # "N will start the game"
}


def _tick_until(flow: GameFlow, target: Screen, limit: int = 400) -> None:
    """Drive the flow to ``target``, ticking timed cards and pressing the
    advancing key on each input-gated front-end screen along the way."""
    for _ in range(limit):
        if flow.screen is target:
            return
        key = _FRONTEND_KEY.get(flow.screen)
        if key is not None:
            flow.handle(key)
        else:
            flow.tick()
    raise AssertionError(f"never reached {target} (stuck on {flow.screen})")


# --- GameFlow transitions --------------------------------------------------

def test_flow_starts_on_the_loading_menu() -> None:
    # D-021: the disk boots into the "LOADING MENU" card, not straight to title.
    flow = GameFlow(front_end=FrontEnd.CLASSIC)  # DISC-262: this asserts the original's full boot chain
    assert flow.screen is Screen.LOADING_MENU
    assert flow.sim is None


def test_front_end_runs_loading_notice_welcome_instructions_to_title() -> None:
    # D-021 boot order: LOADING MENU -> NOTICE -> WELCOME -> INSTRUCTIONS ->
    # LOADING (plug joystick) -> TITLE, gated by the right key at each stop.
    flow = GameFlow(front_end=FrontEnd.CLASSIC)  # DISC-262: this asserts the original's full boot chain
    for _ in range(constants.LOADING_MENU_TICKS):
        flow.tick()
    assert flow.screen is Screen.NOTICE
    flow.handle(InputEvent.FIRE)                  # press any key
    assert flow.screen is Screen.WELCOME
    flow.handle(InputEvent.SELECT_FULL)           # "1 ALIEN"
    assert flow.screen is Screen.INSTRUCTIONS
    flow.handle(InputEvent.NO)                     # "N will start the game"
    assert flow.screen is Screen.LOADING_PLAY
    _tick_until(flow, Screen.TITLE)
    assert flow.screen is Screen.TITLE


def test_title_letters_animate_in_one_at_a_time() -> None:
    # R-30: "ALIEN" spells out one letter at a time over the title's duration.
    flow = GameFlow()
    _tick_until(flow, Screen.TITLE)
    assert flow.title_letters_shown == 1          # first letter shows immediately
    for _ in range(constants.TITLE_LETTER_TICKS):
        flow.tick()
    assert flow.title_letters_shown == 2          # second appears after a delay
    for _ in range(constants.TITLE_LETTER_TICKS * 10):
        if flow.screen is not Screen.TITLE:
            break
        flow.tick()
    assert flow.title_letters_shown == 5          # never more than the 5 letters


def test_title_auto_advances_on_a_timer_not_input() -> None:
    """R-30 (D-014): the real title is timed — no press-to-continue.

    **Bound to the ORIGINAL preset, 2026-08-29**, and the binding is the point
    rather than a way round a failure. The decoded claim is about the disk, and
    it is still exactly true there. What changed is that the *remake* gained a
    skip (`GameFlow.skip_title`, the owner's request): Enter or Escape finishes
    the reveal and a second press leaves. That is an addition, so it is off
    under ORIGINAL — which is where this claim can therefore still be asserted
    in full.

    The test used to build a default flow, whose options are the shipping
    middle ground and read as `custom`, so the skip applied and this failed. It
    was right to fail: a default-constructed flow is not the original, and
    asserting the original's behaviour against one was only ever true by
    coincidence.
    """
    from alien_remake.core.options import PROFILES

    flow = GameFlow(front_end=FrontEnd.CLASSIC,  # DISC-262: the full boot chain
                    current_options=dict(PROFILES["original"]))
    _tick_until(flow, Screen.TITLE)
    flow.handle(InputEvent.FIRE)                 # ignored on the title
    assert flow.screen is Screen.TITLE
    assert flow.title_letters_shown < 5, "the skip is not off under ORIGINAL"
    for _ in range(constants.TITLE_TICKS - 1):
        flow.tick()
    assert flow.screen is Screen.TITLE           # not yet
    flow.tick()
    assert flow.screen is Screen.GAME_SELECTION  # advanced on the timer


def test_selection_is_ctrl_1_ctrl_2_only() -> None:
    # R-32: the real selection loop polls only for Ctrl+1 / Ctrl+2 — no cursor,
    # no fire-select, under ORIGINAL. Up/down/fire do nothing there (DEC-047
    # gates the reintroduced cursor to everything that is not ORIGINAL, so
    # this needs to ask for ORIGINAL explicitly rather than trust the
    # constructor's own defaults, which are not it).
    flow = GameFlow(current_options=dict(options.PROFILES["original"]))
    _tick_until(flow, Screen.GAME_SELECTION)
    for ignored in (InputEvent.UP, InputEvent.DOWN, InputEvent.FIRE):
        flow.handle(ignored)
        assert flow.screen is Screen.GAME_SELECTION
        assert flow.sim is None
    flow.handle(InputEvent.SELECT_SHORT)         # Ctrl+2
    # **[C $4317] D-176** - SHORT does not go straight to the opening: it goes
    # to "DO YOU WANT AN INTRODUCTION". `game_init_mode` branches on the mode
    # in `$4303` and only the FULL path returns immediately.
    assert flow.screen is Screen.INTRO_PROMPT
    flow.handle(InputEvent.NO)                   # $4425 CMP #$27
    assert flow.screen is Screen.OPENING


def test_selection_has_a_highlight_bar_cursor_under_updated() -> None:
    """**DEC-047** — reintroduced, gated to everything that is not ORIGINAL.

    Up/down moves `selection_row` and wraps; fire activates whichever row
    it is sitting on, in the same order `_draw_selection` draws them
    (FULL, SHORT, INSTRUCTIONS, OPTIONS, CREDITS).
    """
    flow = GameFlow(current_options=dict(options.PROFILES["updated"]))
    _tick_until(flow, Screen.GAME_SELECTION)
    assert flow.selection_row == 0

    flow.handle(InputEvent.DOWN)
    assert flow.selection_row == 1
    assert flow.screen is Screen.GAME_SELECTION, "down alone must not select"

    flow.handle(InputEvent.UP)
    assert flow.selection_row == 0

    flow.handle(InputEvent.UP)          # wraps to the last row (CREDITS, 4)
    assert flow.selection_row == 4

    flow.handle(InputEvent.DOWN)
    assert flow.selection_row == 0
    flow.handle(InputEvent.FIRE)        # row 0 == SELECT_FULL
    assert flow.sim is not None
    assert flow.screen not in (Screen.GAME_SELECTION,)


def test_selection_cursor_fires_the_row_it_is_on() -> None:
    """A non-zero row's fire reaches the *matching* screen, not always FULL."""
    flow = GameFlow(current_options=dict(options.PROFILES["updated"]))
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.DOWN)
    flow.handle(InputEvent.DOWN)        # row 2 == SELECT_INSTRUCTIONS
    assert flow.selection_row == 2
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.MANUAL
    assert flow.sim is None, "INSTRUCTIONS does not start a game"


def test_ctrl_1_starts_the_full_game() -> None:
    flow = GameFlow()
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.SELECT_FULL)          # Ctrl+1
    assert flow.screen is Screen.OPENING
    assert flow.sim is not None
    assert flow.sim.state.mode is GameMode.FULL


def test_opening_shows_a_dead_crew_member_then_times_out_to_play() -> None:
    # R-13 (D-014): the death notice clears on a TIMEOUT, no press-to-continue.
    flow = GameFlow(death_variant=DeathVariant.FIXED)
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.SELECT_FULL)          # -> opening (sim built)
    assert flow.sim is not None
    dead = flow.sim.state.opening_dead_crew_id
    assert dead is not None
    assert flow.sim.state.crew[dead].alive is False
    flow.handle(InputEvent.FIRE)                 # ignored on the opening
    assert flow.screen is Screen.OPENING
    _tick_until(flow, Screen.PLAYING)            # times out to play
    assert flow.screen is Screen.PLAYING


def test_sync_phase_moves_to_ended_when_the_game_is_over() -> None:
    flow = GameFlow()
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.SELECT_FULL)
    _tick_until(flow, Screen.PLAYING)
    assert flow.sim is not None
    flow.sim.state.phase = GamePhase.LOST        # simulate a loss
    flow.sync_phase()
    assert flow.screen is Screen.ENDED


def test_key_on_the_end_screen_returns_to_the_title() -> None:
    flow = GameFlow()
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.SELECT_FULL)
    _tick_until(flow, Screen.PLAYING)
    assert flow.sim is not None
    flow.sim.state.phase = GamePhase.WON
    flow.sync_phase()
    flow.handle(InputEvent.FIRE)                 # "press any key" -> restart
    assert flow.screen is Screen.TITLE
    assert flow.sim is None


def test_default_simulation_initialises_awake_crew() -> None:
    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    awake = sum(1 for c in sim.state.crew.values() if c.alive and c.awake)
    assert sim.state.awake_crew == awake
    assert awake == 6  # 7 crew minus the opening death


# --- run_app loop (with a scripted fake backend) ---------------------------

class FakeRenderer:
    """A headless AppRenderer: replays a script of per-frame input events."""

    def __init__(self, script: list[list[InputEvent]]) -> None:
        self._script = script
        self._frame = 0
        self.screens_drawn: list[Screen] = []
        self.cues_played: list[tuple[str, ...]] = []
        self._quit = False

    def poll_input(self, screen: Screen) -> list[InputEvent]:
        events = self._script[self._frame] if self._frame < len(self._script) else []
        self._frame += 1
        if InputEvent.QUIT in events:
            self._quit = True
        return events

    def poll_orders(self) -> list:  # type: ignore[type-arg]
        return []

    def poll_special_options(self) -> list:  # type: ignore[type-arg]
        return []

    def draw(self, flow: GameFlow) -> None:
        self.screens_drawn.append(flow.screen)

    def play_sound_cues(self, state) -> tuple[str, ...]:  # type: ignore[no-untyped-def]
        cues = tuple(c.effect for c in state.sound_cues)
        self.cues_played.append(cues)
        return cues

    def should_quit(self) -> bool:
        return self._quit

    def close(self) -> None:
        return None


class FrontEndDriver:
    """A backend that plays through the front end: it presses the advancing key
    on each input-gated screen and Ctrl+1 at selection, letting timed cards tick."""

    def __init__(self) -> None:
        self.screens_drawn: list[Screen] = []
        self.cues_played: list[tuple[str, ...]] = []
        self._quit = False

    def poll_input(self, screen: Screen) -> list[InputEvent]:
        key = _FRONTEND_KEY.get(screen)
        if key is not None:
            return [key]
        if screen is Screen.GAME_SELECTION:
            return [InputEvent.SELECT_FULL]
        return []

    def poll_orders(self) -> list:  # type: ignore[type-arg]
        return []

    def poll_special_options(self) -> list:  # type: ignore[type-arg]
        return []

    def draw(self, flow: GameFlow) -> None:
        self.screens_drawn.append(flow.screen)

    def play_sound_cues(self, state) -> tuple[str, ...]:  # type: ignore[no-untyped-def]
        cues = tuple(c.effect for c in state.sound_cues)
        self.cues_played.append(cues)
        return cues

    def should_quit(self) -> bool:
        return self._quit

    def close(self) -> None:
        return None


def test_run_app_drives_the_flow_through_every_screen() -> None:
    # A moving clock lets the timed cards tick; the driver presses the advancing
    # key on each front-end screen and Ctrl+1 at selection. The loop should walk
    # the whole boot sequence and end on the play screen.
    flow = GameFlow(front_end=FrontEnd.CLASSIC)  # DISC-262: this asserts the original's full boot chain
    n_frames = (constants.LOADING_MENU_TICKS + constants.LOADING_PLAY_TICKS
                + constants.TITLE_TICKS + constants.OPENING_TICKS + 16)
    renderer = FrontEndDriver()
    clock = {"t": 0.0}

    def now() -> float:
        clock["t"] += 1.0  # +1s per call — always past a tick period
        return clock["t"]

    run_app(flow, renderer, now=now, sleep=lambda _: None, max_frames=n_frames)
    seen = set(renderer.screens_drawn)
    assert {
        Screen.LOADING_MENU, Screen.NOTICE, Screen.WELCOME, Screen.INSTRUCTIONS,
        Screen.LOADING_PLAY, Screen.TITLE, Screen.GAME_SELECTION, Screen.OPENING,
        Screen.PLAYING,
    } <= seen
    assert flow.screen is Screen.PLAYING  # ended on the play screen


def test_run_app_advances_the_sim_on_the_play_screen() -> None:
    flow = GameFlow()
    # Drive the timed intro to the play screen, then run frames with a moving clock.
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.SELECT_FULL)
    _tick_until(flow, Screen.PLAYING)
    assert flow.screen is Screen.PLAYING
    assert flow.sim is not None

    clock = {"t": 0.0}

    def now() -> float:
        clock["t"] += 1.0  # +1s per call — far longer than a tick period
        return clock["t"]

    renderer = FakeRenderer([[] for _ in range(5)])
    run_app(flow, renderer, now=now, sleep=lambda _: None, max_frames=5)
    assert flow.sim.state.tick > 0  # the world advanced while playing


def test_run_app_never_plays_the_same_ticks_cues_twice() -> None:
    """**DISC-226.** Every tick's cues used to play on two consecutive frames.

    `run_app`'s play-screen branch drains and clears `sound_cues` once per
    frame *before* checking whether this frame is also a tick boundary
    (D-187's fix for D-186's silent-cue bug). When it *is* a tick boundary,
    `advance()` repopulates `sound_cues` and a second `play_sound_cues` call
    plays them — but nothing cleared them afterward, so they sat there until
    the *next* frame's drain step played the same cues again before finally
    clearing them. Every movement blip, attack siren and grille burst played
    twice, one frame apart, for the whole run - reported as "the movement
    sound is faster and faster" and misread as the Alien moving unrealistically
    often, since the sound gives no indication of who moved (DISC-225's sibling
    finding: crew and Alien share one cue).

    A 1-real-second-per-frame clock makes every frame a tick boundary, so any
    genuine double-play shows up as two identical non-empty entries in a row.
    """
    # **Seeded.** `GameFlow()` builds its Simulation with an unseeded
    # `random.Random()`, so the opening death, the android and every
    # subsequent roll come from OS entropy — and a draw where the game ends
    # early produces no cues at all, tripping the "must have produced at
    # least one" guard below. Observed failing once in a full-suite run while
    # passing in isolation; seeding removes the flake without weakening what
    # the test actually checks (that no cue is played on two frames running).
    import random as _random

    from alien_remake.core.modes import DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    flow = GameFlow(
        sim_factory=lambda mode, dv: Simulation(
            mode=mode, death_variant=dv, rng=_random.Random(0)
        )
    )
    _tick_until(flow, Screen.GAME_SELECTION)
    flow.handle(InputEvent.SELECT_FULL)
    _tick_until(flow, Screen.PLAYING)
    assert flow.sim is not None

    clock = {"t": 0.0}

    def now() -> float:
        clock["t"] += 1.0
        return clock["t"]

    frames = 200  # several multiples of ALIEN_MOVE_TICKS (60), so cues occur
    renderer = FakeRenderer([[] for _ in range(frames)])
    run_app(flow, renderer, now=now, sleep=lambda _: None, max_frames=frames)

    non_empty = [c for c in renderer.cues_played if c]
    assert non_empty, "the run must have produced at least one sound cue"
    # No two *consecutive frame* entries repeat the same non-empty cue tuple.
    for i in range(1, len(renderer.cues_played)):
        prev, cur = renderer.cues_played[i - 1], renderer.cues_played[i]
        if prev and cur:
            assert prev != cur, (
                f"frame {i - 1} and {i} both played {cur!r} - a tick's cues "
                "were played twice"
            )
