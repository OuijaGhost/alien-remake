"""Sampled audio and the interface cue bus (S1-S3).

Two things need holding. **The provenance boundary:** `audio/sfx.py` claims
nothing in it is designed, so recordings and invented interface sounds must
live somewhere else and must not become a way for undecoded audio to be served
as the game's own. **And silence by default:** a player who has supplied no
files, or asked for none, must get exactly the original's noises and no others.
"""

from __future__ import annotations

import math
import os
import struct
import wave
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from alien_remake.audio import samples, sfx  # noqa: E402
from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.render import audio as render_audio  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


def _stereo_wav(path: Path, seconds: float = 0.05) -> None:
    """A real 44.1 kHz 16-bit stereo file — the format this is built for."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(44100 * seconds)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(44100)
        handle.writeframes(b"".join(
            struct.pack("<hh",
                        int(3000 * math.sin(i / 20)),
                        int(3000 * math.sin(i / 25)))
            for i in range(frames)
        ))


# --- S2: the separate system -------------------------------------------------

def test_it_loads_and_plays_a_real_stereo_file(tmp_path) -> None:
    sounds = tmp_path / "sounds"
    _stereo_wav(sounds / f"{samples.MENU_MOVE}.wav")
    render_audio.set_channels(2)
    pygame.mixer.quit()
    try:
        player = samples.SamplePlayer(sounds)
        assert player.available(samples.MENU_MOVE)
        assert player.load(samples.MENU_MOVE) is not None
        assert player.play(samples.MENU_MOVE) is True
        assert pygame.mixer.get_init()[2] == 2, "stereo files need a stereo mixer"
    finally:
        pygame.mixer.quit()
        render_audio.set_channels(1)


def test_a_missing_file_is_silent_and_reported_once(tmp_path) -> None:
    """Silence, never a crash — and one note, not one per frame."""
    player = samples.SamplePlayer(tmp_path / "sounds")
    assert player.play("nothing_here") is False
    assert player.play("nothing_here") is False
    assert player.missing == {"nothing_here"}


def test_no_directory_at_all_is_a_normal_state(tmp_path) -> None:
    player = samples.SamplePlayer(None)
    assert player.available(samples.MENU_MOVE) is False
    assert player.play(samples.MENU_MOVE) is False
    assert player.found() == []


def test_the_interface_cues_are_not_the_decoded_effects() -> None:
    """The provenance boundary, asserted rather than trusted.

    `sfx.EFFECTS` are read out of the disassembly; the interface cues are
    inventions. If a name ever appeared in both, an invented sound could be
    served as one of the game's own.
    """
    assert not set(samples.UI_CUES) & set(sfx.EFFECTS)


# --- the mixer follows the setting -------------------------------------------

def test_the_mixer_is_mono_unless_sampled_audio_asked_for_stereo() -> None:
    """Stereo doubles what every clip costs resident (22.8 MB against 45.6 MB,
    measured), and the SID is a mono chip — so it is not the default."""
    try:
        render_audio.set_channels(1)
        assert render_audio._channels == 1
        render_audio.set_channels(2)
        assert render_audio._channels == 2
    finally:
        render_audio.set_channels(1)


def test_the_renderer_opens_stereo_only_when_audio_asks() -> None:
    for sound, game_audio, wanted in (
        ("game", "original", 1),
        ("all", "original", 2),
        ("game", "enhanced", 2),
    ):
        pygame.mixer.quit()
        render_audio.set_channels(1)
        renderer = PygameRenderer(scale=2, intro_wav=None,
                                  sound=sound, game_audio=game_audio)
        try:
            assert render_audio._channels == wanted, (sound, game_audio)
        finally:
            renderer.close()
            render_audio.set_channels(1)


# --- S1: the emit bus --------------------------------------------------------

class _Spy:
    """Stands in for the player so a test can hear what was asked for."""

    def __init__(self) -> None:
        self.played: list[str] = []
        self.stopped: list[str] = []

    def play(self, name: str) -> bool:
        self.played.append(name)
        return True

    def stop(self, name: str) -> bool:
        # S6: `emit` cuts a cue's sounding copy before retriggering it, so a
        # double standing in for the player has to carry this too. Left as a
        # real part of the interface rather than made optional in `emit` -
        # a `getattr` there would hide a player that genuinely lost the method.
        self.stopped.append(name)
        return True

    def load(self, name: str) -> None:
        return None


class _MovingClock:
    """A clock that advances well past the S6 floor on every reading.

    These tests take several player actions in a row — enter a screen, move a
    row, pick a different crew member — and the suite runs them inside the same
    millisecond. Before S6 that did not matter. It does now: `emit` drops a cue
    arriving within `CUE_FLOOR_MS` of the last, so with a frozen clock the
    second action of every test was silently rate-limited and the tests failed
    against a floor they were never about.

    Real actions are at least a frame apart and usually a cursor step (about
    127 ms), so time moving between them is the *realistic* case, not a way
    round the guard. The floor has its own tests in `test_cue_debounce.py`,
    where it is the subject rather than the scenery.
    """

    def __init__(self) -> None:
        self.ms = 10_000

    def __call__(self) -> int:
        self.ms += 200
        return self.ms


@pytest.fixture(autouse=True)
def _time_passes(monkeypatch) -> None:
    """Every test in this file gets the moving clock, and gets it back.

    Through `monkeypatch` rather than by assigning the module global in a
    helper: a helper that reassigns `_now_ms` and never restores it leaves the
    clock replaced for every test that runs after, in this file or any other.
    """
    monkeypatch.setattr(render_audio, "_now_ms", _MovingClock())


def _renderer(sound: str = "all", game_audio: str = "original") -> tuple:
    renderer = PygameRenderer(scale=2, intro_wav=None,
                              sound=sound, game_audio=game_audio)
    spy = _Spy()
    renderer._samples = spy
    return renderer, spy


def test_interface_cues_are_silent_unless_switched_on() -> None:
    """`sound = game` is the default: the original's noises and no others."""
    renderer, spy = _renderer(sound="game")
    try:
        assert renderer.emit(samples.MENU_MOVE) is False
        assert spy.played == []
    finally:
        renderer.close()


def test_switched_on_a_cue_reaches_the_player() -> None:
    renderer, spy = _renderer(sound="all")
    try:
        assert renderer.emit(samples.MENU_MOVE) is True
        assert spy.played == [samples.MENU_MOVE]
    finally:
        renderer.close()


# --- S3: the consumers -------------------------------------------------------

def test_moving_and_changing_sound_once_each() -> None:
    renderer, spy = _renderer(sound="all")
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    try:
        renderer.draw(flow)
        assert spy.played[-1] == samples.SCREEN_ENTER

        flow.handle(InputEvent.SELECT_OPTIONS)
        renderer.draw(flow)
        assert spy.played[-1] == samples.SCREEN_ENTER

        before = len(spy.played)
        renderer.draw(flow)
        assert len(spy.played) == before, "an unchanged frame made a noise"

        flow.handle(InputEvent.DOWN)
        renderer.draw(flow)
        assert spy.played[-1] == samples.MENU_MOVE

        flow.handle(InputEvent.RIGHT)
        renderer.draw(flow)
        assert spy.played[-1] == samples.MENU_CHANGE
    finally:
        renderer.close()


def test_arriving_somewhere_sounds_once_not_twice() -> None:
    """A screen change and a row change in the same frame are one event.

    Two blips together read as a fault, and arriving is the bigger of the two.
    """
    renderer, spy = _renderer(sound="all")
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    try:
        renderer.draw(flow)
        spy.played.clear()
        flow.handle(InputEvent.SELECT_OPTIONS)
        flow.options.row = 3
        renderer.draw(flow)
        assert spy.played == [samples.SCREEN_ENTER]
    finally:
        renderer.close()


# --- the game's own effects, from recordings ---------------------------------

def test_sampled_game_audio_replaces_the_synth_when_a_file_exists(
    tmp_path,
) -> None:
    sounds = tmp_path / "sounds"
    _stereo_wav(sounds / "grille.wav")
    pygame.mixer.quit()
    render_audio.set_channels(2)
    renderer = PygameRenderer(scale=2, intro_wav=None, game_audio="enhanced")
    try:
        renderer._samples = samples.SamplePlayer(sounds)
        renderer._sfx_cache.clear()
        assert renderer._sound("grille") is not None
    finally:
        renderer.close()
        pygame.mixer.quit()
        render_audio.set_channels(1)


def test_a_missing_recording_falls_back_to_the_original(tmp_path) -> None:
    """A half-finished sound pack degrades to the synth, not to silence."""
    renderer = PygameRenderer(scale=2, intro_wav=None, game_audio="enhanced")
    try:
        renderer._samples = samples.SamplePlayer(tmp_path / "empty")
        renderer._sfx_cache.clear()
        # No file for this effect: the decoded path still answers (or the
        # device is absent, which is silence either way — never an exception).
        renderer._sound("grille")
    finally:
        renderer.close()


# --- the manifest, and the credits it carries --------------------------------

def _manifest(tmp_path, body: str) -> Path:
    sounds = tmp_path / "sounds"
    sounds.mkdir(parents=True, exist_ok=True)
    (sounds / samples.MANIFEST).write_text(body, encoding="utf-8")
    return sounds


def test_a_cue_can_point_at_a_file_with_any_name(tmp_path) -> None:
    """A downloaded sound keeps the name that carries its provenance.

    `838727__sanderboah__...` says who made it and where to find it again;
    renaming it to `crt_warmup.wav` throws that away to satisfy a lookup.
    """
    original = "838727__sanderboah__computer-crt-monitor-turn-onoff.wav"
    sounds = _manifest(tmp_path, f'[crt_warmup]\nfile = "{original}"\n')
    _stereo_wav(sounds / original)

    player = samples.SamplePlayer(sounds)
    assert player.path_for(samples.CRT_WARMUP).name == original
    assert player.available(samples.CRT_WARMUP)


def test_the_plain_name_still_works_without_a_manifest(tmp_path) -> None:
    sounds = tmp_path / "sounds"
    _stereo_wav(sounds / f"{samples.MENU_MOVE}.wav")
    player = samples.SamplePlayer(sounds)
    assert player.manifest == {}
    assert player.available(samples.MENU_MOVE)


def test_a_broken_manifest_is_ignored_not_fatal(tmp_path) -> None:
    """A typo in an optional credits file must not stop the game starting."""
    sounds = _manifest(tmp_path, "this is not [valid toml")
    _stereo_wav(sounds / f"{samples.MENU_MOVE}.wav")
    player = samples.SamplePlayer(sounds)
    assert player.manifest == {}
    assert player.available(samples.MENU_MOVE), "the fallback still works"


def test_a_claimed_file_is_not_counted_as_a_cue_of_its_own(tmp_path) -> None:
    """Otherwise `crt_warmup` and the file backing it both show up, and the
    startup report says one recording more than there is."""
    original = "838727__sanderboah__crt.wav"
    sounds = _manifest(tmp_path, f'[crt_warmup]\nfile = "{original}"\n')
    _stereo_wav(sounds / original)
    assert samples.SamplePlayer(sounds).found() == ["crt_warmup"]


def test_the_manifest_carries_credits_for_a_credits_screen(tmp_path) -> None:
    sounds = _manifest(tmp_path, (
        '[crt_warmup]\n'
        'file = "x.wav"\n'
        'title = "Computer CRT monitor turn on/off"\n'
        'author = "Sanderboah"\n'
        'source = "https://freesound.org/people/Sanderboah/sounds/838727/"\n'
        'licence = "CC0 1.0"\n'
    ))
    _stereo_wav(sounds / "x.wav")
    credits = samples.SamplePlayer(sounds).credits()
    assert len(credits) == 1
    entry = credits[0]
    assert entry["cue"] == "crt_warmup"
    assert entry["author"] == "Sanderboah"
    assert entry["licence"] == "CC0 1.0"


def test_an_entry_with_no_attribution_is_not_a_credit(tmp_path) -> None:
    """A bare file mapping is routing, not something to put on a screen."""
    sounds = _manifest(tmp_path, '[crt_warmup]\nfile = "x.wav"\n')
    _stereo_wav(sounds / "x.wav")
    assert samples.SamplePlayer(sounds).credits() == []


# --- S4: the warm-up ---------------------------------------------------------

def test_the_warmup_needs_the_tube_to_be_on() -> None:
    """A tube warming up over a picture that is not a tube is a sound for
    something that is not happening."""
    from alien_remake.render.crt import preset

    for crt, sound, wanted in (
        ("off", "all", False),
        ("full", "all", True),
        ("full", "game", False),
    ):
        played: list[str] = []
        renderer = PygameRenderer(scale=2, intro_wav=None, sound=sound,
                                  crt=preset(crt))
        renderer._samples = _Spy()
        renderer._samples.played = played
        try:
            flow = GameFlow()
            flow.screen = Screen.GAME_SELECTION
            renderer.draw(flow)
            assert (samples.CRT_WARMUP in played) is wanted, (crt, sound)
        finally:
            renderer.close()


def test_the_warmup_sounds_once_not_every_frame() -> None:
    from alien_remake.render.crt import preset

    renderer = PygameRenderer(scale=2, intro_wav=None, sound="all",
                              crt=preset("full"))
    spy = _Spy()
    renderer._samples = spy
    try:
        flow = GameFlow()
        flow.screen = Screen.GAME_SELECTION
        for _ in range(5):
            renderer.draw(flow)
        assert spy.played.count(samples.CRT_WARMUP) == 1
    finally:
        renderer.close()


def test_changing_character_sounds_once_per_swap() -> None:
    """`menu_select` had no consumer: a file dropped in under that name was
    silent. Picking a different crew member is the swap a player makes most
    often, so that is what raises it."""
    renderer, spy = _renderer(sound="all")
    try:
        import random

        from alien_remake.core.menu import MenuController
        from alien_remake.core.sim import Simulation

        sim = Simulation(rng=random.Random(7))
        flow = GameFlow()
        flow.screen, flow.sim = Screen.PLAYING, sim
        renderer._menu = MenuController(sim)
        renderer._sim, renderer._ship = sim, sim.ship
        renderer.draw(flow)
        spy.played.clear()

        crew = [e.select_crew for e in renderer._menu.entries() if e.select_crew]
        renderer._menu.selected_crew = crew[0]
        renderer.draw(flow)
        assert spy.played.count(samples.MENU_SELECT) == 1

        renderer.draw(flow)
        assert spy.played.count(samples.MENU_SELECT) == 1, "repeated on a still frame"

        renderer._menu.selected_crew = crew[1]
        renderer.draw(flow)
        assert spy.played.count(samples.MENU_SELECT) == 2

        renderer._menu.selected_crew = None
        renderer.draw(flow)
        assert spy.played.count(samples.MENU_SELECT) == 2, "deselecting is not a swap"
    finally:
        renderer.close()


def test_a_manifest_entry_naming_a_missing_file_is_simply_silent(tmp_path) -> None:
    """Filed-but-not-yet-supplied is a normal state.

    A cue can be credited and pointed at a filename before the file is there —
    it degrades to silence, exactly as a cue with no entry does.
    """
    sounds = _manifest(tmp_path, '[menu_select]\nfile = "not-here-yet.wav"\n')
    player = samples.SamplePlayer(sounds)
    assert player.available(samples.MENU_SELECT) is False
    assert player.play(samples.MENU_SELECT) is False
    assert samples.MENU_SELECT not in player.found()


# --- a cue is a set of recordings, not one -----------------------------------

def test_a_folder_named_after_a_cue_holds_its_variants(tmp_path) -> None:
    """The way to add more: drop a file in, no manifest edit, no renaming.

    Three different clicks for the same action sound like a machine; one played
    three times sounds like a sample.
    """
    folder = tmp_path / "sounds" / samples.MENU_SELECT
    for name in ("first", "second", "third"):
        _stereo_wav(folder / f"{name}.wav")
    player = samples.SamplePlayer(tmp_path / "sounds")
    assert [p.stem for p in player.variants(samples.MENU_SELECT)] == [
        "first", "second", "third"
    ]
    assert player.available(samples.MENU_SELECT)


def test_the_manifest_can_list_several_files(tmp_path) -> None:
    sounds = _manifest(tmp_path, (
        '[menu_select]\nfiles = ["one.wav", "two.wav"]\n'
    ))
    _stereo_wav(sounds / "one.wav")
    _stereo_wav(sounds / "two.wav")
    player = samples.SamplePlayer(sounds)
    assert [p.name for p in player.variants(samples.MENU_SELECT)] == [
        "one.wav", "two.wav"
    ]


def test_a_single_file_still_works(tmp_path) -> None:
    """One recording is the ordinary case and must not have got harder."""
    sounds = tmp_path / "sounds"
    _stereo_wav(sounds / f"{samples.MENU_MOVE}.wav")
    player = samples.SamplePlayer(sounds)
    assert len(player.variants(samples.MENU_MOVE)) == 1
    assert player.play(samples.MENU_MOVE) is True


def test_variants_are_used_and_never_repeat_back_to_back(tmp_path) -> None:
    """True randomness clumps, and the same clip twice running reads as a stuck
    sound — which is the opposite of what having variants is for."""
    folder = tmp_path / "sounds" / samples.MENU_SELECT
    for name in ("a", "b", "c"):
        _stereo_wav(folder / f"{name}.wav")
    player = samples.SamplePlayer(tmp_path / "sounds")

    played: list[str] = []
    for _ in range(30):
        assert player.play(samples.MENU_SELECT) is True
        played.append(player._last[samples.MENU_SELECT].stem)

    assert set(played) == {"a", "b", "c"}, "some variant was never used"
    assert not any(x == y for x, y in zip(played, played[1:])), (
        "the same recording played twice in a row"
    )


def test_two_variants_alternate_rather_than_stall(tmp_path) -> None:
    """The edge case of the no-repeat rule: with two files it must not run out
    of choices and refuse to play."""
    folder = tmp_path / "sounds" / samples.MENU_SELECT
    for name in ("a", "b"):
        _stereo_wav(folder / f"{name}.wav")
    player = samples.SamplePlayer(tmp_path / "sounds")
    for _ in range(6):
        assert player.play(samples.MENU_SELECT) is True


def test_a_cue_folder_is_not_mistaken_for_a_loose_recording(tmp_path) -> None:
    sounds = tmp_path / "sounds"
    _stereo_wav(sounds / samples.MENU_SELECT / "x.wav")
    _stereo_wav(sounds / f"{samples.MENU_MOVE}.wav")
    assert samples.SamplePlayer(sounds).found() == [
        samples.MENU_MOVE, samples.MENU_SELECT
    ]
