"""S6 — the floor on retriggering an interface cue.

Two failures, not one, and they need different fixes.

**Too often.** A held direction repeats the cursor at the ROM's own rate and a
pointer can cross rows faster still. Every step emits, so without a floor the
same blip fires as fast as the cursor moves.

**Over itself.** Even at the ROM's rate, a recording longer than the gap
between two steps is still sounding when the next one starts, and the two layer
up. That is D-150 exactly — stacked one-shots are what made the tracker pings
machine-gun — so the fix has the same shape: one sounding copy per cue.

The floor is derived from `MAIN_LOOP_HZ` rather than chosen, so the interesting
case is the one these test at: a **genuine** repeat, at the cadence the ROM
itself steps the cursor, must always be heard.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest  # noqa: E402

from alien_remake.audio import samples  # noqa: E402
from alien_remake.core import constants  # noqa: E402
from alien_remake.render import audio as render_audio  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402

#: What the ROM's own held-direction repeat costs, in milliseconds. `$5F36`'s
#: busy-wait is the repeat rate, so one step per main loop.
ROM_STEP_MS = 1000 / constants.MAIN_LOOP_HZ


class _Clock:
    """A hand-wound `_now_ms`."""

    def __init__(self) -> None:
        self.ms = 10_000

    def __call__(self) -> int:
        return int(self.ms)


class _Player:
    """A `SamplePlayer` that records instead of playing."""

    def __init__(self) -> None:
        self.played: list[str] = []
        self.stopped: list[str] = []

    def play(self, name: str) -> bool:
        self.played.append(name)
        return True

    def stop(self, name: str) -> bool:
        self.stopped.append(name)
        return True


@pytest.fixture
def rig(monkeypatch):
    """A renderer with interface sound on, a fake player, and a fake clock."""
    clock = _Clock()
    monkeypatch.setattr(render_audio, "_now_ms", clock)
    renderer = PygameRenderer(scale=3, intro_wav=None)
    player = _Player()
    renderer._samples = player
    renderer._ui_sound = True
    try:
        yield renderer, player, clock
    finally:
        renderer.close()


# --- the floor ----------------------------------------------------------------

def test_the_first_cue_is_always_heard(rig) -> None:
    renderer, player, _ = rig
    assert renderer.emit(samples.MENU_MOVE) is True
    assert player.played == [samples.MENU_MOVE]


def test_a_second_cue_in_the_same_frame_is_dropped(rig) -> None:
    """The pathological case: something emitting every frame, or twice in
    one."""
    renderer, player, _ = rig
    renderer.emit(samples.MENU_MOVE)
    assert renderer.emit(samples.MENU_MOVE) is False
    assert player.played == [samples.MENU_MOVE]


def test_thirty_frames_of_holding_a_key_do_not_give_thirty_blips(rig) -> None:
    """A second of a held direction at the *frame* rate, which is what an
    unguarded emit would produce."""
    renderer, player, clock = rig
    for _ in range(30):
        renderer.emit(samples.MENU_MOVE)
        clock.ms += 1000 / 30
    # A second holds about eight of the ROM's own steps, so anything near
    # thirty means the floor is not working — and anything near one means it
    # is swallowing genuine movement.
    assert 6 <= len(player.played) <= 11, len(player.played)


def test_the_roms_own_repeat_rate_is_never_swallowed(rig) -> None:
    """The floor exists to block *faster* than the cursor moves, never the
    cursor itself. Ten held steps must give ten blips."""
    renderer, player, clock = rig
    for _ in range(10):
        assert renderer.emit(samples.MENU_MOVE) is True
        clock.ms += ROM_STEP_MS
    assert len(player.played) == 10


def test_the_floor_clears_the_repeat_that_actually_produces_the_cues() -> None:
    """Measured against the mechanism, not against a chosen number.

    The held-direction repeat counts **frames**: `_joy_repeat_in` decrements
    once per `poll_input`, so two repeats are `_JOY_REPEAT_RATE` frames apart
    and the app loop caps the frame rate at 30. A slower machine only spaces
    them further out, so the closest two genuine repeats can ever land is that
    interval — and the floor has to sit under it.

    Written this way because the first version of this test asserted a full
    frame of slack, which is a stricter claim than anything here needs and
    would have forced the floor down for no reason.
    """
    frames = PygameRenderer._JOY_REPEAT_RATE
    closest_ms = frames * (1000 / 30)
    assert render_audio.CUE_FLOOR_MS < closest_ms, (
        "the floor would swallow a held direction at the ROM's own rate"
    )
    # And it is still a floor worth having: well above a single frame, so a
    # per-frame emit is cut down rather than passed through.
    assert render_audio.CUE_FLOOR_MS > 1000 / 30


def test_the_floor_is_per_cue_not_global(rig) -> None:
    """A menu blip must not be swallowed by the tube warming up behind it."""
    renderer, player, _ = rig
    assert renderer.emit(samples.CRT_WARMUP) is True
    assert renderer.emit(samples.MENU_MOVE) is True
    assert renderer.emit(samples.MENU_CHANGE) is True
    assert len(player.played) == 3


def test_the_clock_going_backwards_does_not_mute_a_cue(rig) -> None:
    """`get_ticks` wrapping or a clock reset must not leave a cue silent for
    the rest of the run — silence you cannot clear is worse than a stray blip.
    """
    renderer, player, clock = rig
    renderer.emit(samples.MENU_MOVE)
    clock.ms -= 5_000
    assert renderer.emit(samples.MENU_MOVE) is True


# --- one sounding copy ---------------------------------------------------------

def test_a_retrigger_cuts_the_copy_already_sounding(rig) -> None:
    """D-150's shape: stacking one-shots is what made the pings machine-gun."""
    renderer, player, clock = rig
    renderer.emit(samples.MENU_MOVE)
    clock.ms += ROM_STEP_MS
    renderer.emit(samples.MENU_MOVE)
    assert player.stopped == [samples.MENU_MOVE, samples.MENU_MOVE]


def test_a_dropped_cue_does_not_cut_anything(rig) -> None:
    """A cue refused by the floor must leave the sounding one alone — cutting
    it would make the blip *shorter* the faster you moved, which is the
    opposite of the intent."""
    renderer, player, _ = rig
    renderer.emit(samples.MENU_MOVE)
    player.stopped.clear()
    assert renderer.emit(samples.MENU_MOVE) is False
    assert player.stopped == []


def test_stopping_one_cue_leaves_the_others_playing() -> None:
    """`SamplePlayer.stop` touches only the channel of the cue named."""

    class _Channel:
        def __init__(self) -> None:
            self.busy = True

        def get_busy(self) -> bool:
            return self.busy

        def stop(self) -> None:
            self.busy = False

    player = samples.SamplePlayer(None)
    warmup, move = _Channel(), _Channel()
    player._channels = {samples.CRT_WARMUP: warmup, samples.MENU_MOVE: move}

    assert player.stop(samples.MENU_MOVE) is True
    assert move.busy is False
    assert warmup.busy is True, "cutting a blip silenced the tube"


def test_stopping_a_cue_that_finished_is_not_an_error() -> None:
    class _Done:
        def get_busy(self) -> bool:
            return False

        def stop(self) -> None:  # pragma: no cover - must not be reached
            raise AssertionError("stopped a channel that was already finished")

    player = samples.SamplePlayer(None)
    player._channels = {samples.MENU_MOVE: _Done()}
    assert player.stop(samples.MENU_MOVE) is False


def test_stopping_a_cue_that_never_played_is_not_an_error() -> None:
    assert samples.SamplePlayer(None).stop(samples.MENU_MOVE) is False


def test_a_full_mixer_is_not_an_error() -> None:
    """`Sound.play()` returns None when every channel is busy. The cue is not
    heard, which is fine; what must not happen is a crash on the next one."""

    class _Sound:
        def play(self):
            return None

    player = samples.SamplePlayer(None)
    player.variants = lambda name: [object()]           # type: ignore[assignment]
    player.load = lambda name, path=None: _Sound()      # type: ignore[assignment]
    assert player.play(samples.MENU_MOVE) is True
    assert player.stop(samples.MENU_MOVE) is False


def test_silence_costs_nothing(rig) -> None:
    """With interface sound off, the floor is never even consulted — the
    default game is exactly as quiet as the original."""
    renderer, player, _ = rig
    renderer._ui_sound = False
    for _ in range(5):
        assert renderer.emit(samples.MENU_MOVE) is False
    assert player.played == []
    assert renderer._cue_last_ms == {}
