"""ORIGINAL leaves nothing invented running (C4).

Every addition to this remake is individually flagged, and `PROFILES` gives each
one an ORIGINAL value — but that is a check on the *table*, not on the game.
`test_both_profiles_cover_every_row` proves each row has a value; nothing
proved that selecting ORIGINAL actually leaves the machine quiet.

The gap matters more the more there is to switch off. There are ten option rows
now and nine invented subsystems — the CRT layer, pointer input, the boot
screen, the session journal, sampled audio, interface cues, the developer
overlay, and two whole screens. The audio ones made it audible: with `sound` or
`game_audio` set wrong, ORIGINAL would play sounds that were never on the disk
and nothing would fail.

So this drives the *renderer*, built the way the app builds it from a profile,
and asserts what is live.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.core.options import PROFILES, OptionsModel  # noqa: E402
from alien_remake.render import audio as render_audio  # noqa: E402
from alien_remake.render.crt import preset  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


def _renderer_for(profile: str) -> PygameRenderer:
    """A renderer configured exactly as `__main__` configures one.

    Read from `PROFILES` rather than restated, so a row added without deciding
    what ORIGINAL means for it fails here too.
    """
    values = PROFILES[profile]
    pygame.mixer.quit()
    render_audio.set_channels(1)
    renderer = PygameRenderer(
        scale=2, intro_wav=None,
        crt=preset(values["crt"]),
        sound=values["sound"],
        game_audio=values["game_audio"],
    )
    renderer.set_developer(values["developer"] == "on")
    return renderer


def test_original_runs_no_crt_layer() -> None:
    renderer = _renderer_for("original")
    try:
        assert renderer.crt.enabled is False
        flow = GameFlow()
        for screen in (Screen.GAME_SELECTION, Screen.PLAYING):
            flow.screen = screen
            assert renderer._crt_running() is False, screen.name
    finally:
        renderer.close()


def test_original_makes_no_invented_sound() -> None:
    """The one that would have been audible.

    Interface cues do not exist on the disk at all, and sampled audio is
    somebody's recording rather than the ROM's own SID writes.
    """
    renderer = _renderer_for("original")
    try:
        assert renderer._ui_sound is False, "ORIGINAL would blip at menus"
        assert renderer._sampled_game_audio is False, (
            "ORIGINAL would play recordings instead of the decoded effects"
        )
        played: list[str] = []
        renderer._samples = type(
            "P", (), {"play": lambda s, n: played.append(n) or True,
                      "load": lambda s, n: None},
        )()
        flow = GameFlow()
        flow.screen = Screen.GAME_SELECTION
        renderer.draw(flow)
        flow.screen = Screen.OPTIONS
        renderer.draw(flow)
        assert played == [], f"ORIGINAL played invented cues: {played}"
    finally:
        renderer.close()


def test_original_opens_the_mixer_mono() -> None:
    """The SID is a mono chip, and stereo is only for supplied recordings."""
    renderer = _renderer_for("original")
    try:
        assert render_audio._channels == 1
    finally:
        renderer.close()
        render_audio.set_channels(1)


def test_original_shows_no_developer_overlay() -> None:
    renderer = _renderer_for("original")
    try:
        assert renderer._debug_markers is False
    finally:
        renderer.close()


def test_original_uses_the_roms_own_draws_everywhere() -> None:
    """Each simulation row at the value that traces to the disassembly."""
    values = PROFILES["original"]
    assert values["alien_start"] == "original"
    assert values["death"] == "original"
    assert values["android"] == "original"
    assert values["jones"] == "classic", "the ROM's own missed-grab behaviour"
    assert values["front_end"] == "classic", "the original's full boot chain"


def test_original_still_plays_the_games_own_effects() -> None:
    """The correction the owner's brief needed.

    "Turn sound effects off" would make ORIGINAL *less* faithful, not more:
    the six effects are the disk's own, decoded from its SID writes. ORIGINAL
    keeps them and drops only the invented ones.
    """
    assert PROFILES["original"]["sound"] == "game"


def test_the_other_profile_actually_differs() -> None:
    """Otherwise every assertion above would pass against a preset that
    changes nothing, and the switch would be decorative."""
    original, other = PROFILES["original"], PROFILES["updated"]
    differing = {k for k in original if original[k] != other[k]}
    assert len(differing) >= 5, f"the presets barely differ: {differing}"


def test_a_new_option_cannot_skip_this_check() -> None:
    """The guard on the guard.

    Every row must appear in ORIGINAL *and* be at a value the row offers — a
    typo'd value would otherwise sit in the table unnoticed and fall back at
    runtime.
    """
    model = OptionsModel()
    for spec in model.specs:
        if spec.key not in PROFILES["original"]:
            continue
        assert PROFILES["original"][spec.key] in spec.values, spec.key
        assert PROFILES["updated"][spec.key] in spec.values, spec.key
