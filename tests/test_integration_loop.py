"""End-to-end tests of `run_app`'s real frame sequence (D-190).

**Why this file exists.** Four defects this project shipped were all the same
shape: every component was individually correct and *the seam between them* was
wrong. Per-component tests are structurally blind to that.

| bug | each part was right, but | caught by |
|---|---|---|
| D-186/D-187 | the sim raised the cue and the renderer could play it — the loop threw it away in between | `test_a_cue_raised_while_handling_input_is_heard` |
| P8-15 | `EXIT_ADVERT` drew correctly and `flow.finished` was set — the loop kept going | `test_the_quit_advert_ends_the_program` |
| P8-15b | the advert's entry frame was recorded in a branch that re-ran every frame | *invariant only* — `test_the_exit_advert_never_returns_to_the_front_end` |
| PV-25/D-171 | `sfx.render` produced correct PCM and the mixer played what it was given — the handoff format was wrong | `test_the_mixer_is_handed_a_container_not_raw_samples` |

**The specific blindness these fix.** `tests/test_remake_flow.py`'s `FakeRenderer`
and `FrontEndDriver` are *passive*: their `poll_input` only returns events. The
real backend is not. `MenuController.fire()` (`core/menu.py:927`) calls
`sim.apply_special_option(...)` **during** `poll_input`, so by the time
`run_app` gets the event list the sim has already been mutated and
`poll_orders()` is empty. Every fake being passive is precisely why the drain
ordering was wrong for two rounds of fixes.

So :class:`RecordingBackend` mutates the sim during `poll_input` the way the
real one does, and records the loop's observable behaviour frame by frame
instead of just its endpoint.

**Each test below fails if its fix is reverted** — that was the acceptance
criterion for the file, and it was checked by actually reverting each of the
four fixes in turn. Two of them only started failing after the test was
rewritten: `_fast_clock` ticks on every frame, and a tick runs `advance()`,
whose opening `sound_cues.clear()` silently covers for a missing clear in the
loop. Hence `_slow_clock`.

The one exception is the P8-15b row, which holds the invariant the defect broke
but is not known to fail on the defect itself — that lived in the renderer's own
frame bookkeeping, below this loop's visibility. Its docstring says so.
"""

from __future__ import annotations

from dataclasses import dataclass

from alien_remake.app import run_app
from alien_remake.core import constants
from alien_remake.core.flow import (
    GameFlow,
    InputEvent,
    Screen,
    default_simulation,
)
from alien_remake.core.modes import FrontEnd, DeathVariant, GameMode
from alien_remake.core.sound import AIRLOCK, SoundCue
from alien_remake.core.state import GameState


@dataclass
class CueObservation:
    """One `play_sound_cues` call: which frame, and what was in the queue."""

    frame: int
    #: "input" = the drain that follows `poll_input`; "tick" = the post-`advance`
    #: drain. The distinction is the whole of D-187.
    phase: str
    effects: tuple[str, ...]


class RecordingBackend:
    """An `AppRenderer` that behaves like the **real** pygame backend.

    Two things the passive test fakes do not do, both of which hid real bugs:

    1. ``poll_input`` runs a caller-supplied ``on_input`` hook, so a test can
       mutate the sim *inside the poll* exactly as `MenuController.fire()` does.
    2. ``poll_orders`` / ``poll_special_options`` return empty, because the real
       backend has already applied everything by then.

    Everything the loop does is recorded per frame rather than sampled at the
    end, so a test can assert on *ordering*, which is where seam bugs live.
    """

    def __init__(self, on_input=None, quit_after: int | None = None) -> None:  # type: ignore[no-untyped-def]
        self._on_input = on_input
        self._quit_after = quit_after
        self.frame = 0
        self.screens_drawn: list[Screen] = []
        self.cues: list[CueObservation] = []
        self.idled: list[float] = []
        self._phase = "input"
        #: Skip-turn and auto-select (2026-09-05), not the original — see
        #: `PygameRenderer.poll_skip_turn`/`select_crew`. `_skip_turn` is set
        #: by a test's `on_input` hook the same way it queues an order;
        #: `selected_crew_calls` records every `select_crew` call, in order.
        self._skip_turn = False
        self.selected_crew_calls: list[str] = []

    # --- AppRenderer ------------------------------------------------------
    def poll_input(self, screen: Screen) -> list[InputEvent]:
        self._phase = "input"
        events: list[InputEvent] = []
        if self._on_input is not None:
            events = list(self._on_input(self, screen) or ())
        return events

    def poll_orders(self) -> list:  # type: ignore[type-arg]
        return []          # as in the real backend: already applied in poll_input

    def poll_special_options(self) -> list:  # type: ignore[type-arg]
        return []

    def draw(self, flow: GameFlow) -> None:
        self.screens_drawn.append(flow.screen)
        self.frame += 1
        self._phase = "tick"   # anything after the draw is the next frame's input

    def play_sound_cues(self, state: GameState) -> tuple[str, ...]:
        effects = tuple(c.effect for c in state.sound_cues)
        self.cues.append(CueObservation(self.frame, self._phase, effects))
        self._phase = "tick"
        return effects

    def idle(self, seconds: float) -> None:
        """The real backend waits out the frame itself (and may re-present it).

        Recorded rather than slept, so a test can see the loop hand the leftover
        over exactly once a frame without the suite paying for it in wall clock.
        """
        self.idled.append(seconds)

    def should_quit(self) -> bool:
        return self._quit_after is not None and self.frame >= self._quit_after

    def close(self) -> None:
        return None

    def poll_skip_turn(self) -> bool:
        skip, self._skip_turn = self._skip_turn, False
        return skip

    def select_crew(self, crew_id: str) -> None:
        self.selected_crew_calls.append(crew_id)

    # --- helpers ----------------------------------------------------------
    def heard(self) -> set[str]:
        """Every effect the loop actually handed us, across all drains."""
        return {e for obs in self.cues for e in obs.effects}


def _fast_clock():  # type: ignore[no-untyped-def]
    """A clock that jumps a full second per call, so every frame is also a tick."""
    t = {"v": 0.0}

    def now() -> float:
        t["v"] += 1.0
        return t["v"]

    return now


def _slow_clock():  # type: ignore[no-untyped-def]
    """A clock too slow to ever tick, so frames are input-and-draw only.

    Needed to see anything a tick would paper over — chiefly `advance()`'s
    opening `sound_cues.clear()`, which masks a missing clear in the loop on
    any frame that happens to tick.
    """
    t = {"v": 0.0}

    def now() -> float:
        t["v"] += 0.001
        return t["v"]

    return now


def _welcome_flow() -> GameFlow:
    """A flow sitting on WELCOME, the screen whose panel carries `Q QUIT`.

    The advert is only reachable from there, so a bare `GameFlow()` (which
    starts on the LOADING_MENU interstitial) silently ignores the event.

    **CLASSIC explicitly (DISC-262):** the quick front end skips WELCOME and the
    advert with it, so this fixture must ask for the original's boot chain or it
    would loop for 600 ticks and fail on a screen that no longer exists in the
    default path.
    """
    flow = GameFlow(front_end=FrontEnd.CLASSIC)
    for _ in range(600):
        if flow.screen is Screen.WELCOME:
            return flow
        if flow.screen is Screen.NOTICE:
            flow.handle(InputEvent.FIRE)   # "press any key"
        else:
            flow.tick()
    raise AssertionError(f"never reached WELCOME (stuck on {flow.screen.name})")


def _playing_flow() -> GameFlow:
    """A flow parked on the play screen with a real Simulation."""
    flow = GameFlow()
    flow.sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    flow.screen = Screen.PLAYING
    return flow


# --- seam 1: the cue drain ordering (D-186 / D-187) ---------------------------

def test_a_cue_raised_while_handling_input_is_heard() -> None:
    """A cue the *input handler* raises must reach the renderer.

    This is D-186's bug and D-187's fix. `Simulation.advance()` opens with
    `sound_cues.clear()`, so a cue raised during `poll_input` — which is when
    the real `MenuController.fire()` applies a Special Option — survives only if
    the loop drains it *before* the tick. BLOWLOCK was silent through two
    rounds of fixing because of this.

    **Reverting:** delete the `play_sound_cues` / `sound_cues.clear()` pair that
    precedes `poll_orders()` in `app.py`, and this fails — as it did in the
    build the user reported with "blowlock 1 and blowlock 2 still make no
    sound."
    """
    flow = _playing_flow()
    assert flow.sim is not None

    def on_input(backend: RecordingBackend, screen: Screen) -> list[InputEvent]:
        # What `MenuController.fire()` does: mutate the sim during the poll.
        if backend.frame == 0 and flow.sim is not None:
            flow.sim.state.sound_cues.append(SoundCue(effect=AIRLOCK))
        return []

    backend = RecordingBackend(on_input=on_input)
    run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None, max_frames=3)

    assert AIRLOCK in backend.heard(), (
        "a cue raised during poll_input was swallowed by advance()'s clear — "
        "the loop must drain handler-raised cues before ticking (D-187)"
    )
    # ...and specifically on the *input* drain of the frame that raised it.
    first = next(o for o in backend.cues if AIRLOCK in o.effects)
    assert first.phase == "input" and first.frame == 0


def test_the_input_drain_does_not_replay_a_cue_on_the_next_tick() -> None:
    """Draining early must also *clear*, or a cue is heard on every frame.

    The counterweight to the test above. It needs a **slow clock**: with a tick
    every frame, `advance()`'s own opening `sound_cues.clear()` covers for a
    missing clear and the bug stays invisible. `run_app` draws at 30fps and
    ticks at ~7.9Hz, so most real frames do *not* tick — and on those, an
    undrained queue is replayed by the next frame's input drain. A blowlock
    crack would machine-gun about four times.

    (This was written with `_fast_clock` first, and passed with the clear
    reverted. That is exactly the blindness the file exists to remove, which is
    why the reversion check is part of its contract, not a nicety.)
    """
    flow = _playing_flow()
    assert flow.sim is not None

    def on_input(backend: RecordingBackend, screen: Screen) -> list[InputEvent]:
        if backend.frame == 0 and flow.sim is not None:
            flow.sim.state.sound_cues.append(SoundCue(effect=AIRLOCK))
        return []

    backend = RecordingBackend(on_input=on_input)
    run_app(flow, backend, now=_slow_clock(), sleep=lambda _: None, max_frames=5)

    plays = sum(o.effects.count(AIRLOCK) for o in backend.cues)
    assert plays == 1, f"the airlock cue was heard {plays}x — the early drain must clear"


# --- seam 2 & 3: the quit advert (P8-15) --------------------------------------

def test_the_quit_advert_ends_the_program() -> None:
    """`Q QUIT` holds the advert, then the **program exits** (D-185).

    EXITO ends on `SYS 64738`. The remake first looped back to LOADING_MENU
    instead — the user's report was "This should just hold on the advert screen
    for a moment before closing." `GameFlow.tick` sets `finished`; `run_app`'s
    `while` has to honour it.

    **Reverting:** change `run_app`'s condition back to
    `while not renderer.should_quit():` and this hangs to `max_frames`.
    """
    flow = _welcome_flow()
    flow.handle(InputEvent.QUIT_TO_ADVERT)
    assert flow.screen is Screen.EXIT_ADVERT

    # Generous headroom: if the loop honours `finished` it stops well short.
    cap = constants.EXIT_ADVERT_TICKS * 4 + 50
    backend = RecordingBackend()
    frames = run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None,
                     max_frames=cap)

    assert flow.finished, "the advert never finished"
    assert frames < cap, "run_app ignored flow.finished and ran to max_frames"


def test_the_exit_advert_never_returns_to_the_front_end() -> None:
    """The advert holds, then ends — it never re-enters the menu.

    P8-15's second half. The screen's entry frame was recorded in a branch that
    re-ran every frame, so the hold restarted continuously and the flow fell
    back to the top-level screen.

    **Honest scope.** Unlike its three neighbours this one is *not* known to
    fail on the original defect: that lived in `PygameRenderer`'s own
    `_exit_entered_frame` bookkeeping, which the loop cannot observe. What it
    does hold is the flow-level invariant the defect violated — the advert is
    terminal and leads nowhere. Covering the renderer half needs a display, so
    it stays uncovered; said plainly here rather than implied by this test's
    existence.
    """
    flow = _welcome_flow()
    flow.handle(InputEvent.QUIT_TO_ADVERT)

    backend = RecordingBackend()
    run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None,
            max_frames=constants.EXIT_ADVERT_TICKS * 4 + 50)

    assert set(backend.screens_drawn) == {Screen.EXIT_ADVERT}, (
        "the advert flowed into another screen instead of ending: "
        f"{sorted({s.name for s in backend.screens_drawn})}"
    )
    # It really did hold, rather than ending on frame 1.
    assert len(backend.screens_drawn) >= constants.EXIT_ADVERT_TICKS


# --- seam 4: the PCM -> mixer handoff (PV-25 / D-171) -------------------------

def test_the_mixer_is_handed_a_container_not_raw_samples() -> None:
    """`sfx` output must reach the mixer as a parseable WAV, not raw bytes.

    Not loop-level — this seam is inside the renderer — but the same shape, and
    the same blindness: `sfx.render` was correct and the mixer played what it
    was given, so both sides' tests passed while every clip came out at double
    speed an octave high. `pygame.mixer.Sound(buffer=...)` reinterprets bytes
    as samples *already in the mixer's format*; ours are mono, the mixer is
    stereo. Only a file-like object makes pygame parse the container.

    Checked structurally because asserting it properly needs an audio device.

    **Reverting:** change either call site back to `Sound(buffer=...)`.
    """
    import re
    from pathlib import Path

    from alien_remake.audio import sfx

    wav = sfx.wav_bytes(sfx.render("airlock", sample_rate=22050), 22050)
    assert wav[:4] == b"RIFF" and wav[8:12] == b"WAVE", (
        "wav_bytes no longer emits a RIFF container, so BytesIO cannot help"
    )

    # Scan the whole render package, not one file: D-191 moved these calls out
    # of `pygame_app.py` into `audio.py` and this test went green by looking at
    # the wrong module. A guard pinned to a path is a guard a refactor disarms.
    root = Path(__file__).resolve().parent.parent / "src" / "alien_remake" / "render"
    seen = 0
    for path in sorted(root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        # Skip comments: D-171's own explanatory comment quotes the call it
        # forbids, so scanning raw text always matches itself.
        code = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("#")
        )
        assert not re.search(r"mixer\.Sound\(\s*buffer\s*=", code), (
            f"{path.name}: pygame.mixer.Sound(buffer=...) reads raw samples in "
            "the mixer's format; our PCM is mono, so this halves every clip's "
            "length (D-171). Wrap it in io.BytesIO so pygame parses the WAV."
        )
        seen += code.count("io.BytesIO(sfx.wav_bytes(")
    assert seen >= 2, (
        f"only {seen} BytesIO-wrapped Sound construction(s) found; expected the "
        "one-shot and heartbeat call sites. Did one lose its wrapper?"
    )


# --- the property that makes the harness worth keeping ------------------------

def test_the_backend_contract_matches_the_real_one() -> None:
    """`RecordingBackend` must stay a faithful stand-in for the pygame backend.

    The harness is only as good as its fake. If `AppRenderer` grows a method,
    this fails and the fake gets updated — otherwise the harness silently stops
    covering the new seam, which is exactly how it would rot.
    """
    from alien_remake.app import AppRenderer

    required = {
        name for name in dir(AppRenderer)
        if not name.startswith("_") and callable(getattr(AppRenderer, name, None))
    }
    missing = {name for name in required if not hasattr(RecordingBackend, name)}
    assert not missing, f"RecordingBackend is missing AppRenderer methods: {missing}"


# --- C2/T6: turns, as an in-game option (2026-09-03) -------------------------

def test_turns_off_paces_on_the_wall_clock_as_before() -> None:
    """The default. Nothing about this loop's real-time path changes."""
    flow = _playing_flow()
    assert flow.sim is not None
    flow.options.values["turns"] = "off"
    before = flow.sim.state.tick
    run_app(flow, RecordingBackend(), now=_fast_clock(), sleep=lambda _: None,
            max_frames=3)
    assert flow.sim.state.tick == before + 3, (
        "turns=off must still advance exactly one tick per fast-clock frame"
    )


def test_turns_on_does_not_advance_with_nothing_queued() -> None:
    """The defining behaviour: a turn-based game does not clock-tick while
    you are still deciding. `flow.sim._orders` stays empty for all 5 frames -
    the same "no order this frame" state a player looking at the menu is in."""
    flow = _playing_flow()
    assert flow.sim is not None
    flow.options.values["turns"] = "on"
    before = flow.sim.state.tick
    run_app(flow, RecordingBackend(), now=_fast_clock(), sleep=lambda _: None,
            max_frames=5)
    assert flow.sim.state.tick == before, (
        "turns=on advanced with nothing queued - it should pause, not tick"
    )


def test_turns_on_advances_once_an_order_is_queued() -> None:
    """The real backend's own shape: `MenuController.fire()` calls
    `sim.queue_order` directly *during* `poll_input` (D-187), never through
    `poll_orders()` - so this is what the loop must actually react to, not
    the passive fakes' return-a-list path `test_only_the_left_button_fires`-
    style tests use elsewhere."""
    from alien_remake.core.orders import Order, OrderType

    flow = _playing_flow()
    assert flow.sim is not None
    flow.options.values["turns"] = "on"
    crew = next(c for c in flow.sim.state.crew.values() if c.alive)
    assert crew.room_id is not None
    dest = flow.sim.ship.door_neighbors(crew.room_id)[0]

    queued = {"done": False}

    def on_input(backend: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        if not queued["done"] and flow.sim is not None:
            flow.sim.queue_order(Order(crew.id, OrderType.MOVE_TO, dest))
            queued["done"] = True
        return []

    before = flow.sim.state.tick
    run_app(flow, RecordingBackend(on_input=on_input), now=_fast_clock(),
            sleep=lambda _: None, max_frames=2)
    assert flow.sim.state.tick > before, (
        "turns=on with an order actually queued (via sim.queue_order, the "
        "real backend's own path) must advance - it did not"
    )
    assert not flow.sim._orders, (
        "the order should have resolved (or hit its ceiling) within one "
        "advance_until_resolution call, not still be sitting in the queue"
    )


# --- initiative (2026-09-04, not the original) -------------------------------
#
# The user's own request: "an initiative based system where the game randomly
# assigns an order for turns at the start between all characters and
# creatures. The action points to allow roughly one room move and one
# action." `_playing_flow` builds `flow.sim` directly rather than going through
# `GameFlow._start()`, so these tests roll initiative by hand the same way
# `_start()` would, rather than drive the whole front-end chain just to reach
# the play screen.

def _playing_flow_with_initiative() -> GameFlow:
    flow = _playing_flow()
    flow.options.values["turns"] = "on"
    flow._roll_initiative()
    return flow


def test_initiative_covers_every_crew_member_and_both_creatures_once() -> None:
    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    expected = set(flow.sim.state.crew.keys()) | {
        constants.TURN_ALIEN_ACTOR, constants.TURN_JONES_ACTOR,
    }
    assert set(flow.turn_order) == expected
    assert len(flow.turn_order) == len(expected), "no actor should appear twice"


def test_an_order_for_someone_other_than_the_current_actor_is_rejected() -> None:
    """`MenuController.fire()` queues straight onto `flow.sim._orders` during
    `poll_input` (D-187) — nothing stops the player from picking whichever
    crew member's menu is on screen. The initiative gate has to catch it
    there, after the fact, the same way the wrong-turn order actually arrives.
    """
    from alien_remake.core.orders import Order, OrderType

    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    # Force a crew member's slot up first, regardless of how the shuffle
    # landed - this test is about the gate rejecting the wrong crew id, not
    # about who initiative happened to pick.
    actor = next(iter(flow.sim.state.crew))
    flow.turn_order = [actor, *(a for a in flow.turn_order if a != actor)]
    flow.turn_actor_index = 0
    someone_else = next(
        c for c in flow.sim.state.crew.values() if c.alive and c.id != actor
    )

    queued = {"done": False}

    def on_input(backend: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        if not queued["done"] and flow.sim is not None:
            flow.sim.queue_order(Order(someone_else.id, OrderType.ATTACK))
            queued["done"] = True
        return []

    before = flow.sim.state.tick
    run_app(flow, RecordingBackend(on_input=on_input), now=_fast_clock(),
            sleep=lambda _: None, max_frames=2)
    assert flow.sim.state.tick == before, (
        "an out-of-turn order must not advance the sim at all"
    )
    assert flow.sim.state.notice is not None, (
        "the player should be told whose turn it actually is"
    )


def test_two_resolved_actions_pass_initiative_to_the_next_actor() -> None:
    """`TURN_ACTIONS_PER_TURN = 2` — "roughly one room move and one action" —
    so the second order for the same actor should hand initiative on."""
    from alien_remake.core.orders import Order, OrderType

    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    actor = next(iter(flow.sim.state.crew))
    flow.turn_order = [actor, *(a for a in flow.turn_order if a != actor)]
    flow.turn_actor_index = 0

    orders_left = [
        Order(actor, OrderType.ATTACK), Order(actor, OrderType.ATTACK),
    ]

    def on_input(backend: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        if orders_left and flow.sim is not None:
            flow.sim.queue_order(orders_left.pop(0))
        return []

    run_app(flow, RecordingBackend(on_input=on_input), now=_fast_clock(),
            sleep=lambda _: None, max_frames=2)
    assert flow.current_turn_actor() != actor, (
        "two resolved orders should have spent both action points and "
        "advanced initiative to the next actor"
    )


def test_a_creature_slot_auto_resolves_without_waiting_for_input() -> None:
    """Neither the Alien nor Jones takes player orders, so their slot must not
    just sit there forever waiting for `new_orders` the way a crew slot does."""
    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    # Force the roll so the Alien's slot is up first, regardless of how the
    # shuffle landed.
    flow.turn_order = [constants.TURN_ALIEN_ACTOR, *(
        a for a in flow.turn_order if a != constants.TURN_ALIEN_ACTOR
    )]
    flow.turn_actor_index = 0

    before_tick = flow.sim.state.tick
    before_actor = flow.current_turn_actor()
    run_app(flow, RecordingBackend(), now=_fast_clock(), sleep=lambda _: None,
            max_frames=1)
    assert flow.sim.state.tick > before_tick, (
        "the Alien's slot should have run on its own, with no order queued"
    )
    assert flow.current_turn_actor() != before_actor, (
        "a creature slot should hand initiative on immediately, not wait "
        "for action points that don't apply to it"
    )


def test_a_creature_slot_posts_a_notice_naming_no_detail() -> None:
    """The player must be told *that* a creature acted, never *what* it did."""
    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    flow.turn_order = [constants.TURN_ALIEN_ACTOR, *(
        a for a in flow.turn_order if a != constants.TURN_ALIEN_ACTOR
    )]
    flow.turn_actor_index = 0

    run_app(flow, RecordingBackend(), now=_fast_clock(), sleep=lambda _: None,
            max_frames=1)
    assert flow.sim.state.notice is not None
    assert "ALIEN" in flow.sim.state.notice
    for word in ("ATTACK", "MOVE", "ROOM", "HIT"):
        assert word not in flow.sim.state.notice, (
            f"the creature-turn notice must not describe what happened "
            f"(found {word!r})"
        )


# --- skip turn + auto-select (2026-09-05, not the original) -----------------

def test_skip_turn_advances_initiative_without_resolving_anything() -> None:
    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    actor = next(iter(flow.sim.state.crew))
    flow.turn_order = [actor, *(a for a in flow.turn_order if a != actor)]
    flow.turn_actor_index = 0
    before_tick = flow.sim.state.tick

    backend = RecordingBackend()

    def on_input(b: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        b._skip_turn = True
        return []

    backend._on_input = on_input
    run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None, max_frames=1)
    assert flow.current_turn_actor() != actor, (
        "skipping must hand initiative to the next actor"
    )
    assert flow.sim.state.tick == before_tick, (
        "a skip must not advance the simulation - nothing was resolved"
    )


def test_skip_turn_drops_any_order_already_queued_for_the_skipping_actor() -> None:
    from alien_remake.core.orders import Order, OrderType

    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    actor = next(iter(flow.sim.state.crew))
    flow.turn_order = [actor, *(a for a in flow.turn_order if a != actor)]
    flow.turn_actor_index = 0

    backend = RecordingBackend()

    def on_input(b: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        if flow.sim is not None:
            flow.sim.queue_order(Order(actor, OrderType.ATTACK))
        b._skip_turn = True
        return []

    backend._on_input = on_input
    run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None, max_frames=1)
    assert not flow.sim._orders, (
        "skipping must drop the actor's own queued order, not resolve it first"
    )


def test_advancing_the_actor_auto_selects_the_next_crew_member() -> None:
    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    actor = next(iter(flow.sim.state.crew))
    other = next(a for a in flow.sim.state.crew if a != actor)
    flow.turn_order = [actor, other]
    flow.turn_actor_index = 0

    backend = RecordingBackend()

    def on_input(b: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        b._skip_turn = True
        return []

    backend._on_input = on_input
    run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None, max_frames=1)
    assert backend.selected_crew_calls == [other], (
        "advancing to a crew member's slot should auto-select them in the "
        "CONTROL panel"
    )


def test_advancing_to_a_creature_slot_does_not_call_select_crew() -> None:
    flow = _playing_flow_with_initiative()
    assert flow.sim is not None
    actor = next(iter(flow.sim.state.crew))
    flow.turn_order = [actor, constants.TURN_ALIEN_ACTOR]
    flow.turn_actor_index = 0

    backend = RecordingBackend()

    def on_input(b: RecordingBackend, screen) -> list[InputEvent]:  # type: ignore[no-untyped-def]
        b._skip_turn = True
        return []

    backend._on_input = on_input
    run_app(flow, backend, now=_fast_clock(), sleep=lambda _: None, max_frames=1)
    assert backend.selected_crew_calls == [], (
        "select_crew is a CONTROL-panel concept - it has nothing to select "
        "for the Alien's or Jones's own slot"
    )
