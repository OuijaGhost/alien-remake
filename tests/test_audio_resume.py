"""The mixer must survive the machine going to sleep (DISC-247).

SDL audio devices frequently do not survive a suspend. Every audio call in
`render/audio.py` is wrapped in `except`, so the failure is not a crash — it is
the game continuing to play in **total silence**, which costs two mechanics:
the heartbeat is composure-paced (D-145) and the tracker ping carries
information the player acts on.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.render.pygame_app import PygameRenderer
from alien_remake.render.tiles import load


@pytest.fixture
def renderer() -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    r = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    yield r
    r.close()


def test_first_call_only_takes_a_reference(renderer: PygameRenderer) -> None:
    """With nothing to compare against, a resume cannot be inferred."""
    renderer._clock_ref = None
    assert renderer.check_for_resume() is False
    assert renderer._clock_ref is not None


def test_ordinary_frames_are_not_mistaken_for_a_resume(
    renderer: PygameRenderer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both clocks advancing together is just time passing.

    A frame hitch — even a long one — moves the two clocks by the same amount,
    so the difference stays near zero.
    """
    import alien_remake.render.audio as audio_mod

    wall, mono = 1_000_000.0, 500.0
    monkeypatch.setattr(audio_mod.time, "time", lambda: wall)
    monkeypatch.setattr(audio_mod.time, "perf_counter", lambda: mono)
    renderer._clock_ref = None
    renderer.check_for_resume()

    for elapsed in (0.016, 0.5, 4.0, 60.0):     # ordinary frames and a long stall
        wall += elapsed
        mono += elapsed
        assert renderer.check_for_resume() is False, (
            f"{elapsed}s of real time was read as a resume"
        )


def test_a_wall_clock_jump_past_the_monotonic_one_is_a_resume(
    renderer: PygameRenderer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The signal: wall clock advances, monotonic does not.

    On Linux `perf_counter` is CLOCK_MONOTONIC, which does not tick while
    suspended — that divergence is what identifies the resume, with no platform
    API involved.
    """
    import alien_remake.render.audio as audio_mod

    wall, mono = 1_000_000.0, 500.0
    monkeypatch.setattr(audio_mod.time, "time", lambda: wall)
    monkeypatch.setattr(audio_mod.time, "perf_counter", lambda: mono)
    renderer._clock_ref = None
    renderer.check_for_resume()

    rebuilt: list[bool] = []
    monkeypatch.setattr(
        type(renderer), "_rebuild_mixer", lambda self: rebuilt.append(True)
    )

    wall += 3600.0          # an hour of sleep...
    mono += 0.02            # ...that the monotonic clock did not see
    assert renderer.check_for_resume() is True
    assert rebuilt == [True], "the mixer was not rebuilt"


def test_the_rebuild_discards_state_that_belonged_to_the_old_device(
    renderer: PygameRenderer,
) -> None:
    """Cached Sounds and live channels belong to the device that went away.

    `pygame.mixer.init()` is a no-op when the mixer is already initialised, so
    it cannot revive a dead device on its own — the teardown and the cache
    clear are what make the rebuild work.
    """
    renderer._sfx_cache["stale"] = object()
    renderer._attacking = True
    renderer._attacking_crew_id = "dallas"
    renderer._heartbeat_composure = 3

    renderer._rebuild_mixer()

    assert renderer._sfx_cache == {}, "stale Sounds kept from the dead device"
    assert renderer._tracker_channel is None
    assert renderer._heartbeat_channel is None
    assert renderer._heartbeat_composure is None
    assert renderer._attacking is False
    assert renderer._attacking_crew_id is None


def test_resume_is_checked_every_frame(
    renderer: PygameRenderer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A check that is never called protects nothing."""
    from alien_remake.core.flow import Screen

    calls: list[bool] = []
    monkeypatch.setattr(
        type(renderer), "check_for_resume", lambda self: calls.append(True)
    )
    renderer.poll_input(Screen.WELCOME)
    renderer.poll_input(Screen.WELCOME)
    assert len(calls) == 2
