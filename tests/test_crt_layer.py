"""The CRT layer (DISC-264) — a look, never a fact.

Two things have to stay true, and both are the kind that rot silently:

* **Off is off.** With the effect disabled the window must get the pixels it
  got before the layer existed. An "off" switch that still round-trips through
  numpy would be worse than no switch, because every fidelity test in this
  suite reads `_surface` and would keep passing while the player saw something
  else.
* **The field is never modified.** `_surface` is the replica's contract. The
  chain reads it and writes the window; if that ever inverts, a decode error
  and a filter become indistinguishable.

The look itself is not asserted here — it is judged by eye through
`tools/crt_bench.py`. What is asserted is the plumbing around it.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pygame = pytest.importorskip("pygame")
np = pytest.importorskip("numpy")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from alien_remake.core.flow import GameFlow, Screen            # noqa: E402
from alien_remake.core.menu import (                           # noqa: E402
    GENTLE_VIEW_CHANGE,
    MenuController,
)
from alien_remake.core.sim import Simulation                   # noqa: E402
from alien_remake.render.crt import (                          # noqa: E402
    BURST_SECONDS,
    DEGAUSS_SECONDS,
    GLITCH_FULL,
    GLITCH_GENTLE,
    GLITCH_SECONDS,
    PRESETS,
    CrtProcessor,
    CrtSettings,
    mask_gain,
    preset,
    shadow_mask,
)
from alien_remake.render.layout import _HEIGHT, _WIDTH         # noqa: E402
from alien_remake.render.pygame_app import (                   # noqa: E402
    _CRT_SCREENS,
    PygameRenderer,
)
from alien_remake.render.tiles import load                     # noqa: E402


@pytest.fixture
def renderer() -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    r = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    yield r
    r.close()


def _window_bytes(r: PygameRenderer, screen: Screen) -> bytes:
    flow = GameFlow()
    flow.screen = screen
    r._frame_count = 0
    r.draw(flow)
    r._present()
    return pygame.image.tobytes(r._window, "RGB")


# --- off must be indistinguishable ---------------------------------------


def test_every_screen_is_byte_identical_with_the_layer_off(
    renderer: PygameRenderer,
) -> None:
    """The guard the plan called for, across all the screens the game has."""
    clean = {s: _window_bytes(renderer, s) for s in Screen}
    renderer.crt = preset("off")
    for screen in Screen:
        assert _window_bytes(renderer, screen) == clean[screen], (
            f"{screen.name} changed with --crt off"
        )


def test_off_does_not_even_build_the_processor(renderer: PygameRenderer) -> None:
    """Its noise bank is ~2 MB; a player who leaves the effect off pays none of it."""
    for screen in Screen:
        _window_bytes(renderer, screen)
    assert renderer._crt is None


def test_nothing_is_composited_when_the_layer_is_off(
    renderer: PygameRenderer,
) -> None:
    """The off path must not even build the whole-screen canvas."""
    renderer.crt = preset("off")
    renderer._crt_live = True
    renderer._paint()
    assert renderer._canvas is None and renderer._crt is None


# --- on: the right screens, and the field untouched -----------------------


def test_the_effect_covers_every_screen(renderer: PygameRenderer) -> None:
    """Owner's call, 2026-08-28: the tube is on from boot.

    This reverses DISC-264, which kept the layer out of the loader screens on
    the reasoning that they are seen before a player has agreed to anything.
    The owner's position is that a tube is a tube from the moment it is on, and
    switching the effect in at the play screen reads as a glitch. So the `crt`
    setting is now the only gate, and this asserts the *opposite* of what the
    old test did.

    Compares the *window*, because that is the only place the layer writes.
    """
    clean = {s: _window_bytes(renderer, s) for s in Screen}
    renderer.crt = preset("full")
    renderer._crt = None                     # rebuild against the new settings

    unchanged = [s.name for s in Screen if _window_bytes(renderer, s) == clean[s]]
    # A handful of screens are a flat fill with nothing on them yet; the layer
    # has nothing to work with there and that is not a failure. What must not
    # happen is the *front end as a class* staying clean.
    front_end_changed = [
        s.name for s in (Screen.LOADING_MENU, Screen.NOTICE, Screen.TITLE,
                         Screen.GAME_SELECTION)
        if _window_bytes(renderer, s) != clean[s]
    ]
    assert front_end_changed, (
        f"the tube is on but no loader screen changed; unchanged={unchanged}"
    )


def test_the_chain_never_writes_to_the_field(renderer: PygameRenderer) -> None:
    """`_surface` is the fidelity contract; the tube only ever reads it."""
    renderer.crt = preset("full")
    flow = GameFlow()
    flow.screen = Screen.PLAYING
    flow.sim = Simulation()
    renderer._sim, renderer._ship = flow.sim, flow.sim.ship
    renderer._menu = MenuController(flow.sim)
    renderer.draw(flow)
    before = pygame.image.tobytes(renderer._surface, "RGB")
    for _ in range(8):
        renderer._retube()
    assert pygame.image.tobytes(renderer._surface, "RGB") == before


def test_idle_sleeps_rather_than_spinning_when_the_layer_is_off(
    renderer: PygameRenderer, monkeypatch: pytest.MonkeyPatch
) -> None:
    slept: list[float] = []
    tubed: list[int] = []
    monkeypatch.setattr("alien_remake.render.pygame_app.time.sleep", slept.append)
    monkeypatch.setattr(PygameRenderer, "_retube", lambda self: tubed.append(1))
    renderer.idle(0.033)
    assert slept == [0.033] and not tubed


def test_idle_refreshes_the_tube_at_120hz_over_a_30fps_frame(
    renderer: PygameRenderer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The owner's requirement, stated as a count.

    A 30 fps frame leaves ~33 ms; at `TUBE_HZ` that is three extra presents
    plus the game's own, i.e. four refreshes for one drawn frame.
    """
    clock = [0.0]
    tubed: list[int] = []

    def _advance(seconds: float) -> None:
        clock[0] += seconds

    monkeypatch.setattr(
        "alien_remake.render.pygame_app.time.perf_counter", lambda: clock[0]
    )
    monkeypatch.setattr("alien_remake.render.pygame_app.time.sleep", _advance)
    monkeypatch.setattr(PygameRenderer, "_retube", lambda self: tubed.append(1))
    renderer.crt = preset("full")
    renderer._crt_live = True
    renderer.idle(1 / 30)
    assert len(tubed) == 3, f"{len(tubed) + 1} refreshes in a 30 fps frame"


# --- the trigger boundary -------------------------------------------------


def test_the_menu_reports_view_changes_without_knowing_about_the_renderer() -> None:
    """The three the owner named, plus the gentle deck change."""
    sim = Simulation()
    menu = MenuController(sim)
    crew = next(
        c for c in sim.state.crew.values()
        if c.alive and menu.sim.state.crew[c.id].health > 1
    )

    start = menu.view_epoch
    menu.selected_crew = crew.id
    menu.back()
    assert menu.view_epoch == start + 1 and menu.view_epoch_strength == 1.0

    entries = menu.entries()
    rows = menu._selectable(entries)          # cursor indexes *selectable* rows
    crew_row = next(
        i for i, idx in enumerate(rows) if entries[idx].select_crew == crew.id
    )
    menu.cursor = crew_row
    menu.fire()
    assert menu.selected_crew == crew.id, "the probe never selected anyone"
    assert menu.view_epoch == start + 2

    menu.back()
    other = next(d for d in sim.ship.decks() if d != sim.state.deck)
    entries = menu.entries()
    rows = menu._selectable(entries)
    menu.cursor = next(
        i for i, idx in enumerate(rows) if entries[idx].select_deck == other
    )
    before = menu.view_epoch
    menu.fire()
    assert menu.view_epoch == before + 1
    assert menu.view_epoch_strength == GENTLE_VIEW_CHANGE


def test_queued_view_changes_do_not_all_fire_when_the_effect_comes_on(
    renderer: PygameRenderer,
) -> None:
    """Epochs are consumed even when the layer is not running.

    Otherwise every menu move made with the effect off would go off at once the
    moment it was switched on. The screen used to be what stopped the layer
    running; now that it runs everywhere, the only thing that does is the
    setting, so that is what this drives.
    """
    sim = Simulation()
    renderer._menu = MenuController(sim)
    renderer.crt = preset("off")
    renderer._crt = None
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    for _ in range(5):
        renderer._menu._view_changed()
        renderer.draw(flow)

    renderer.crt = preset("full")
    renderer._crt = None
    renderer.draw(flow)
    assert renderer._crt is None or not renderer._crt.glitching, (
        "a backlog of view changes fired the moment the tube came on"
    )


# --- the processor itself -------------------------------------------------


def test_process_returns_the_input_untouched_when_disabled() -> None:
    proc = CrtProcessor((_WIDTH, _HEIGHT), CrtSettings(enabled=False))
    frame = np.zeros((_WIDTH, _HEIGHT, 3), dtype=np.uint8)
    assert proc.process(frame) is frame


def test_process_leaves_its_input_alone() -> None:
    """The chain copies; it must not scribble on the caller's array."""
    proc = CrtProcessor((_WIDTH, _HEIGHT), CrtSettings(enabled=True))
    rng = np.random.default_rng(3)
    frame = rng.integers(0, 256, (_WIDTH, _HEIGHT, 3), dtype=np.uint8)
    original = frame.copy()
    proc.glitch()
    proc.advance(1 / 120)
    proc.process(frame)
    assert np.array_equal(frame, original)


def test_chroma_bleed_keeps_luma_sharp() -> None:
    """The mistake worth a test: blurring all three channels looks out of focus.

    A single bright column on black. Blurring luma spreads its *brightness*
    sideways; bleeding only chroma leaves the column's total luma where it was.
    """
    settings = CrtSettings(
        enabled=True, scanlines=False, noise=False, interlace=False,
        bloom=False, mask=False, chroma_bleed=True, chroma_bleed_width=3,
    )
    proc = CrtProcessor((64, 8), settings)
    frame = np.zeros((64, 8, 3), dtype=np.uint8)
    frame[32, :, :] = 255
    out = proc.process(frame)
    luma = out.astype(np.int32).sum(axis=2)[:, 0]
    # The neighbouring columns were black and must stay dark: a luma blur puts
    # roughly a quarter of the column's brightness into each of them.
    assert luma[32] > 600, "the bright column lost its own luma"
    assert luma[31] < 60 and luma[33] < 60, "luma smeared - this is a blur, not NTSC"


def test_the_glitch_decays_and_the_stronger_one_wins() -> None:
    proc = CrtProcessor((_WIDTH, _HEIGHT), CrtSettings(enabled=True))
    assert not proc.glitching
    proc.glitch(GENTLE_VIEW_CHANGE)
    gentle = proc._glitch_level
    proc.glitch(1.0)
    assert proc._glitch_level > gentle, "a full glitch did not override a gentle one"
    proc.advance(GLITCH_SECONDS / 2)
    assert 0.0 < proc._glitch_level < 1.0, "the transient does not decay"
    proc.advance(GLITCH_SECONDS)
    assert not proc.glitching


def test_the_tube_advances_on_real_time_not_frames() -> None:
    """So the look is the same whatever frame rate the loop actually achieves."""
    slow = CrtProcessor((_WIDTH, _HEIGHT), CrtSettings(enabled=True))
    fast = CrtProcessor((_WIDTH, _HEIGHT), CrtSettings(enabled=True))
    slow.advance(1 / 30)
    for _ in range(4):
        fast.advance(1 / 120)
    assert slow._phase == pytest.approx(fast._phase)


def test_every_cli_preset_builds() -> None:
    for name in PRESETS:
        settings = preset(name)
        assert isinstance(settings, CrtSettings)
        assert settings.enabled == (name != "off")
    with pytest.raises(ValueError):
        preset("crt")


# --- the two transients are different faults, not two volumes -------------


def _still(width: int = 64, height: int = 64) -> "np.ndarray":
    """A single bright cross, so displacement is measurable *unambiguously*.

    Stripes were the first attempt and they lie: `argmax` on a periodic pattern
    reports the offset modulo the period, so a smooth one-pixel bend that
    happens to cross a stripe boundary reads as a seven-pixel tear. One column
    and one row, in different channels, cannot do that.
    """
    frame = np.zeros((width, height, 3), dtype=np.uint8)
    frame[width // 4, :, 1] = 200          # one vertical line  (green)
    frame[:, height // 4, 0] = 200         # one horizontal line (red)
    return frame


def _bare(**kw: object) -> CrtSettings:
    """Only the transient under test: no tube stages to confuse the measurement."""
    base = dict(
        enabled=True, scanlines=False, chroma_bleed=False, noise=False,
        interlace=False, bloom=False, raster=False, motion_blur=0.0,
        chroma_shift=False,
        # The mask is applied by the renderer at window size, but its *gain*
        # compensation lives in the chain -- leaving it on would brighten every
        # measurement below by a fifth.
        mask=False,
    )
    return CrtSettings(**{**base, **kw})  # type: ignore[arg-type]


def test_the_degauss_bends_the_picture_where_the_scramble_tears_it() -> None:
    """The owner's note: the gentle effect looked like the full one turned down.

    It is now a different fault, and this is the measurable difference. A
    degauss *warps* - a smooth displacement across the field, so neighbouring
    lines never part company - where a scramble loses horizontal lock and
    throws rows against each other. Both move the picture; only one tears it.
    """
    frame = _still(64, 128)
    proc = CrtProcessor((64, 128), _bare(flash_glow=0.0))
    proc.glitch(GLITCH_GENTLE)
    worst_step = 0
    vertical_moves = 0
    for _ in range(60):
        proc.advance(1 / 120)
        out = proc.process(frame)
        offsets = [int(np.argmax(out[:, y, 1])) for y in range(0, 128, 8)]
        steps = [abs(b - a) for a, b in zip(offsets, offsets[1:])]
        worst_step = max([worst_step, *steps])
        vertical_moves += int(np.argmax(out[0, :, 0]) != np.argmax(frame[0, :, 0]))
    assert worst_step <= 1, (
        f"neighbouring lines parted by {worst_step}px - that is a tear, not a warp"
    )
    assert vertical_moves == 0, "the degauss rolled vertically"


def test_the_degauss_warps_at_all() -> None:
    """A bend that never bends is indistinguishable from the guard above."""
    frame = _still(64, 128)
    proc = CrtProcessor((64, 128), _bare(degauss_warp=8.0, flash_glow=0.0))
    proc.glitch(GLITCH_GENTLE)
    spread = 0
    for _ in range(80):
        proc.advance(1 / 120)
        out = proc.process(frame)
        offsets = [int(np.argmax(out[:, y, 1])) for y in range(0, 128, 8)]
        spread = max(spread, max(offsets) - min(offsets))
    assert spread >= 2, "the picture never actually bent"


def test_the_cathode_bloom_brightens_and_then_clears() -> None:
    """The white the owner asked for: the face of the tube lighting up."""
    frame = np.full((64, 64, 3), 40, dtype=np.uint8)
    proc = CrtProcessor((64, 64), _bare(degauss_warp=0.0, flash_glow=0.5))
    proc.glitch(GLITCH_GENTLE)
    proc.advance(1 / 120)
    lit = proc.process(frame)
    centre, corner = int(lit[32, 32, 0]), int(lit[0, 0, 0])
    assert centre > 70, "no bloom at the centre of the tube"
    assert centre > corner, "the bloom is flat - it should fall off to the edges"
    proc.advance(DEGAUSS_SECONDS)
    assert np.array_equal(proc.process(frame), frame), "the bloom never cleared"


def test_the_degauss_settings_are_not_scaled_down_twice() -> None:
    """`degauss_warp = 5.0` must mean 5 pixels, not 5 times GLITCH_GENTLE.

    `level` already carries the strength that selected the gentle path, so
    scaling by it again silently made every degauss number mean a third of what
    it said - which is most of why the effect read as invisible.
    """
    frame = _still(64, 128)
    proc = CrtProcessor((64, 128), _bare(degauss_warp=12.0, flash_glow=0.0))
    proc.glitch(GLITCH_GENTLE)
    spread = 0
    for _ in range(80):
        proc.advance(1 / 120)
        out = proc.process(frame)
        offsets = [int(np.argmax(out[:, y, 1])) for y in range(0, 128, 8)]
        spread = max(spread, max(offsets) - min(offsets))
    assert spread >= 6, f"12px of warp produced {spread}px of bend"


def test_the_degauss_actually_moves_and_then_settles() -> None:
    frame = _still()
    proc = CrtProcessor((64, 64), _bare())
    proc.glitch(GLITCH_GENTLE)
    moved = 0
    for _ in range(int(DEGAUSS_SECONDS * 120)):
        proc.advance(1 / 120)
        if not np.array_equal(proc.process(frame), frame):
            moved += 1
    assert moved > 10, "the degauss is invisible"
    proc.advance(0.01)
    assert not proc.glitching
    assert np.array_equal(proc.process(frame), frame), "it never settled"


def test_the_full_glitch_does_tear_the_picture() -> None:
    """The other half of the pair: the scramble loses horizontal lock."""
    frame = _still()
    proc = CrtProcessor((64, 64), _bare())
    proc.glitch()
    torn = 0
    for _ in range(int(GLITCH_SECONDS * 120)):
        proc.advance(1 / 120)
        out = proc.process(frame)
        offsets = {int(np.argmax(out[:, y, 1])) for y in range(0, 64, 8)}
        torn += len(offsets) > 1
    assert torn > 5, "the scramble is not displacing rows against each other"


def test_the_full_glitch_is_the_shorter_of_the_two() -> None:
    """Owner's call: the scramble takes less time, the degauss settles slowly."""
    assert GLITCH_SECONDS < DEGAUSS_SECONDS


# --- the always-on additions ----------------------------------------------


def test_motion_blur_converges_on_a_still_picture() -> None:
    """A trail must not permanently darken or haze a frame that is not moving."""
    frame = _still()
    proc = CrtProcessor((64, 64), _bare(motion_blur=0.6))
    for _ in range(40):
        proc.advance(1 / 120)
        out = proc.process(frame)
    assert np.abs(out.astype(int) - frame.astype(int)).max() <= 1


def test_motion_blur_leaves_a_trail_while_the_picture_moves() -> None:
    """And it must actually do something: two different frames must blend."""
    black = np.zeros((64, 64, 3), dtype=np.uint8)
    white = np.full((64, 64, 3), 255, dtype=np.uint8)
    proc = CrtProcessor((64, 64), _bare(motion_blur=0.6))
    proc.advance(1 / 120)
    proc.process(white)
    proc.advance(1 / 120)
    after = proc.process(black)
    assert after.max() > 100, "black after white showed no persistence"


def test_the_raster_bar_rolls_on_wall_clock_and_wraps() -> None:
    """Speed is in field lines per second, so it is the number the owner dialled."""
    frame = np.full((64, 64, 3), 120, dtype=np.uint8)
    proc = CrtProcessor((64, 64), _bare(raster=True, raster_strength=0.3,
                                        raster_speed=64.0, raster_height=8))
    seen = []
    for _ in range(4):
        proc.advance(0.25)                       # a quarter of a full pass
        out = proc.process(frame)
        rows = np.where(out[0, :, 0] != 120)[0]
        seen.append(int(rows[0]) if len(rows) else -1)
    assert len(set(seen)) > 1, "the bar is not moving"
    assert all(0 <= v < 64 for v in seen), "the bar left the field"


def test_scanline_blur_softens_vertically_without_erasing_the_lines() -> None:
    """Blurring the finished pattern would cancel the scanlines outright.

    So the softening goes on *before* the lines do, and both must survive: a
    vertical edge stays sharp (this is a vertical filter) while alternate rows
    still differ.
    """
    frame = np.zeros((32, 32, 3), dtype=np.uint8)
    frame[:, 16:, :] = 255                      # a horizontal edge across rows
    settings = _bare(scanlines=True, scanline_depth=0.15, scanline_blur=0.5)
    out = CrtProcessor((32, 32), settings).process(frame)
    assert 0 < out[0, 15, 1] < 255, "the vertical transition was not softened"
    # Sampled inside the lit half: two black rows differ by nothing whatever
    # the filter does, which would make this pass for the wrong reason.
    even, odd = int(out[0, 20, 1]), int(out[0, 21, 1])
    assert even != odd, "the scanlines were blurred away entirely"


# --- the phosphor mask ----------------------------------------------------


def test_the_mask_is_rgb_triads_and_nothing_is_fully_dark() -> None:
    """Each triad lights one column of each colour; the rest is dimmed, not off.

    Killing two thirds of the light outright is what makes a naive mask look
    like a grid drawn over the game rather than glass in front of it.
    """
    mask = shadow_mask((12, 4), pitch=3, strength=0.35, stagger=False)
    assert mask.shape == (12, 4, 3)
    for channel in range(3):
        column = mask[channel, 0]
        assert int(column[channel]) == 255, "the lit subpixel is not at full"
        others = [int(column[c]) for c in range(3) if c != channel]
        assert all(0 < v < 255 for v in others), "neighbours are off, not dimmed"
    # One full triad, so every column is lit in exactly one channel.
    lit_per_column = [(mask[x, 0] == 255).sum() for x in range(3)]
    assert lit_per_column == [1, 1, 1]


def test_a_stagger_offsets_alternate_bands() -> None:
    """Slot mask (offset rows) against aperture grille (unbroken stripes)."""
    grille = shadow_mask((12, 12), pitch=3, stagger=False)
    assert np.array_equal(grille[:, 0], grille[:, 7]), "grille stripes should not break"
    slot = shadow_mask((12, 12), pitch=3, stagger=True)
    assert not np.array_equal(slot[:, 0], slot[:, 4]), "the bands did not stagger"


def test_the_mask_gain_restores_the_average_brightness() -> None:
    """A mask darkens; the gain is what stops the game looking dimmer for it."""
    strength = 0.35
    mask = shadow_mask((90, 4), pitch=3, strength=strength).astype(float) / 255.0
    assert mask.mean() == pytest.approx(1.0 / mask_gain(strength), abs=0.01)


def test_the_mask_is_skipped_when_a_game_pixel_is_smaller_than_a_triad(
    renderer: PygameRenderer,
) -> None:
    """Three phosphors need three subpixels. Below that it would eat the picture."""
    # The owner's tuned default leaves the mask off, so ask for it explicitly:
    # this test is about the geometry rule, not about what ships enabled.
    renderer.crt = preset("full").replace(mask=True)
    renderer._crt_live = True
    assert renderer._mask_surface((_WIDTH * 2, _HEIGHT * 2)) is None
    assert renderer._mask_surface((_WIDTH * 3, _HEIGHT * 3)) is not None


def test_the_mask_is_never_applied_with_the_layer_off(
    renderer: PygameRenderer,
) -> None:
    renderer.crt = preset("off").replace(mask=True)
    renderer._crt_live = True
    assert renderer._mask_surface((_WIDTH * 4, _HEIGHT * 4)) is None
    renderer.crt = preset("full").replace(mask=True)
    renderer._crt_live = False
    assert renderer._mask_surface((_WIDTH * 4, _HEIGHT * 4)) is None


def test_the_mask_pitch_stays_in_screen_pixels_as_the_window_grows(
    renderer: PygameRenderer,
) -> None:
    """It belongs to the tube, not the signal.

    A mask that scaled with the game's pixels would be a texture on the sprite
    sheet; a real one is a fixed sheet of steel the picture is thrown against.
    """
    renderer.crt = preset("full").replace(mask=True)
    renderer._crt_live = True
    pitches = []
    for scale in (3, 4, 6):
        surface = renderer._mask_surface((_WIDTH * scale, _HEIGHT * scale))
        assert surface is not None
        row = pygame.surfarray.array3d(surface)[:12, 0, 0]
        pitches.append(tuple(int(v) for v in row))
    assert len(set(pitches)) == 1, "the triad pitch followed the window size"


# --- one family of transient, led by the chroma shift (DISC-267) ----------


def _chroma_bare(**kw: object) -> CrtSettings:
    """The transient with colour separation *on* and the tube stages off."""
    base = dict(
        enabled=True, scanlines=False, chroma_bleed=False, noise=False,
        interlace=False, bloom=False, raster=False, motion_blur=0.0,
        mask=False, flash_glow=0.0,
    )
    return CrtSettings(**{**base, **kw})  # type: ignore[arg-type]


def _red_offset(out: "np.ndarray", frame: "np.ndarray") -> int:
    """How far the red channel moved, in pixels."""
    return int(np.argmax(out[:, 8, 0])) - int(np.argmax(frame[:, 8, 0]))


def test_both_transients_separate_colour_from_luma() -> None:
    """The owner's pick: chroma shift is the character of *both* now.

    A white column has no colour of its own, so any red/blue split in the
    output came from the transient rather than from the source.
    """
    frame = np.zeros((64, 16, 3), dtype=np.uint8)
    frame[32, :, :] = 255
    for strength in (GLITCH_FULL, GLITCH_GENTLE):
        proc = CrtProcessor((64, 16), _chroma_bare(wave=False, degauss_warp=0.0))
        proc.glitch(strength)
        split = 0
        for _ in range(24):
            proc.advance(1 / 120)
            out = proc.process(frame)
            reds = np.where(out[:, 8, 0] > 100)[0]
            blues = np.where(out[:, 8, 2] > 100)[0]
            if len(reds) and len(blues):
                split = max(split, abs(int(reds[0]) - int(blues[0])))
        assert split >= 2, f"no colour separation at strength {strength}"


def test_the_deck_change_now_carries_the_chroma_shift() -> None:
    """"Use the chroma shift for moving between floors" — the gentle path.

    Measured on the gentle strength specifically, because that is the one the
    deck change fires and the one that used to be a pure warp.
    """
    frame = np.zeros((64, 16, 3), dtype=np.uint8)
    frame[32, :, :] = 255
    proc = CrtProcessor((64, 16), _chroma_bare(degauss_warp=0.0, wave=False))
    proc.glitch(GLITCH_GENTLE)
    moved = 0
    for _ in range(60):
        proc.advance(1 / 120)
        if _red_offset(proc.process(frame), frame) != 0:
            moved += 1
    assert moved > 5, "the deck change did not shift colour"


def test_the_chroma_shift_springs_back_rather_than_sliding_once() -> None:
    """The gentle one swings with the ring: colour goes both ways and settles."""
    frame = np.zeros((64, 16, 3), dtype=np.uint8)
    frame[32, :, :] = 255
    proc = CrtProcessor((64, 16), _chroma_bare(degauss_warp=0.0, wave=False))
    proc.glitch(GLITCH_GENTLE)
    offsets = []
    for _ in range(80):
        proc.advance(1 / 120)
        offsets.append(_red_offset(proc.process(frame), frame))
    assert max(offsets) > 0 and min(offsets) < 0, "colour only ever went one way"
    assert offsets[-1] == 0, "colour never came back into register"


def test_the_flash_fires_on_the_full_glitch_too() -> None:
    """"Mix the bright flash ... with the chroma shift effect" — both paths."""
    frame = np.full((64, 64, 3), 40, dtype=np.uint8)
    for strength in (GLITCH_FULL, GLITCH_GENTLE):
        proc = CrtProcessor(
            # luma_invert off: at full strength it flips half the frame, and a
            # corner at 255-40 would read brighter than the lit centre.
            (64, 64), _chroma_bare(wave=False, degauss_warp=0.0,
                                   chroma_shift=False, luma_invert=False,
                                   flash_glow=0.5)
        )
        proc.glitch(strength)
        proc.advance(1 / 120)
        lit = proc.process(frame)
        assert int(lit[32, 32, 0]) > 70, f"no flash at strength {strength}"
        assert int(lit[32, 32, 0]) > int(lit[0, 0, 0]), "the flash is flat"


def test_no_two_glitches_trace_the_same_curve() -> None:
    """Owner's note: the waves must not repeat exactly.

    Two firings of the *same* processor are compared, so this is about the
    per-firing roll and not about seeding two objects differently.
    """
    frame = _still(64, 64)
    proc = CrtProcessor((64, 64), _chroma_bare(chroma_shift=False))

    def curve() -> tuple[int, ...]:
        proc.glitch()
        rows = []
        for _ in range(12):
            proc.advance(1 / 120)
            out = proc.process(frame)
            rows.append(int(np.argmax(out[:, 8, 1])))
        proc.advance(GLITCH_SECONDS)          # let it finish before the next
        return tuple(rows)

    curves = {curve() for _ in range(6)}
    assert len(curves) > 1, "every firing displaced the picture identically"


def test_the_randomness_is_seeded_so_a_run_is_reproducible() -> None:
    """The variation is in the look, not in the tests.

    Two processors built with the same seed must agree exactly; a different
    seed must not. Without this, a rendering test could fail once a fortnight
    and never be reproducible.
    """
    frame = _still(64, 64)

    def run(seed: int) -> bytes:
        proc = CrtProcessor((64, 64), _chroma_bare(), seed=seed)
        proc.glitch()
        proc.advance(1 / 120)
        return proc.process(frame).tobytes()

    assert run(7) == run(7)
    assert run(7) != run(8)


# --- the VIC border is part of the picture (DISC-268) ---------------------


def _play(renderer: PygameRenderer, size: tuple[int, int]) -> GameFlow:
    """Put the renderer on the play screen at a given window size."""
    renderer._window = pygame.display.set_mode(size, pygame.RESIZABLE)
    renderer._scaled = None
    flow = GameFlow()
    flow.screen = Screen.PLAYING
    flow.sim = Simulation()
    renderer._sim, renderer._ship = flow.sim, flow.sim.ship
    renderer._menu = MenuController(flow.sim)
    renderer.draw(flow)
    return flow


def test_the_border_goes_through_the_chain_too(renderer: PygameRenderer) -> None:
    """Scanlines that stop at the edge of the game field give the trick away.

    Sampled in the border margin, well outside `field_rect`, where the only
    thing that can vary between rows is the tube.
    """
    renderer.crt = preset("full").replace(scanline_depth=0.5, noise=False,
                                          motion_blur=0.0, raster=False)
    _play(renderer, (_WIDTH * 3 + 120, _HEIGHT * 3 + 120))
    renderer._present()
    rect = renderer.field_rect()
    assert rect.y >= 6, "no border to sample - the test proves nothing"
    column = rect.x + rect.width // 2
    rows = [renderer._window.get_at((column, y))[:3] for y in range(0, rect.y - 1)]
    assert len(set(rows)) > 1, "the border is flat - the tube stopped at the field"


def test_the_border_is_untouched_with_the_layer_off(
    renderer: PygameRenderer,
) -> None:
    """And off, it must be exactly the flat VIC blue it always was."""
    renderer.crt = preset("off")
    _play(renderer, (_WIDTH * 3 + 120, _HEIGHT * 3 + 120))
    renderer._present()
    rect = renderer.field_rect()
    column = rect.x + rect.width // 2
    rows = {renderer._window.get_at((column, y))[:3] for y in range(0, rect.y - 1)}
    assert len(rows) == 1, f"the border varies with the layer off: {rows}"


def test_the_field_lands_in_the_same_place_with_the_layer_on(
    renderer: PygameRenderer,
) -> None:
    """The canvas is hung so the field cannot shift when the CRT comes on.

    Its offset is rounded up from `field_rect` and the origin made negative to
    match, precisely so switching the layer on does not move the picture by up
    to `scale - 1` pixels.
    """
    for size in ((_WIDTH * 3 + 77, _HEIGHT * 3 + 41), (1280, 800), (1000, 700)):
        renderer.crt = preset("off")
        _play(renderer, size)
        rect = renderer.field_rect()
        renderer.crt = preset("full")
        renderer._crt = None
        canvas, offset, origin, scale = renderer._tube_layout()
        landed = (origin[0] + offset[0] * scale, origin[1] + offset[1] * scale)
        assert landed == rect.topleft, f"field moved at {size}: {landed} vs {rect.topleft}"
        covered = (origin[0] + canvas.get_width() * scale,
                   origin[1] + canvas.get_height() * scale)
        assert covered[0] >= size[0] and covered[1] >= size[1], (
            f"the canvas leaves a gap at {size}"
        )


def test_the_canvas_stays_at_c64_resolution(renderer: PygameRenderer) -> None:
    """Covering the border must not turn this into a window-resolution filter."""
    renderer.crt = preset("full")
    _play(renderer, (1920, 1080))
    renderer._crt = None
    canvas, _, _, _ = renderer._tube_layout()
    assert canvas.get_width() < _WIDTH * 1.5 and canvas.get_height() < _HEIGHT * 1.5


# --- the static rides the command-accept flash ----------------------------


def test_the_burst_adds_static_and_decays() -> None:
    frame = np.full((64, 64, 3), 80, dtype=np.uint8)
    quiet = CrtSettings(
        enabled=True, scanlines=False, chroma_bleed=False, interlace=False,
        bloom=False, raster=False, motion_blur=0.0, mask=False,
        noise=True, noise_amount=0, burst_noise=60,
    )
    proc = CrtProcessor((64, 64), quiet)
    proc.advance(1 / 120)
    assert np.array_equal(proc.process(frame), frame), "static before the burst"
    proc.burst()
    proc.advance(1 / 120)
    assert not np.array_equal(proc.process(frame), frame), "the burst added nothing"
    proc.advance(BURST_SECONDS)
    assert np.array_equal(proc.process(frame), frame), "the burst never stopped"


def test_the_burst_does_not_rebuild_the_noise_bank() -> None:
    """It changes amount every frame; caching that would cost 2M ops a frame."""
    proc = CrtProcessor((64, 64), CrtSettings(enabled=True, noise_amount=7,
                                              burst_noise=40))
    frame = np.full((64, 64, 3), 80, dtype=np.uint8)
    proc.advance(1 / 120)
    proc.process(frame)
    cached = proc._noise_scaled
    proc.burst()
    for _ in range(8):
        proc.advance(1 / 120)
        proc.process(frame)
    assert proc._noise_scaled is cached, "the bank was rebuilt mid-burst"


# --- the deck change actually reaches the layer (DISC-268) ----------------


def test_a_deck_change_takes_the_gentle_path_not_the_scramble(
    renderer: PygameRenderer,
) -> None:
    """The reported bug: changing floors did nothing visible.

    `GENTLE_VIEW_CHANGE` (0.35) was passed straight to `glitch()`, whose gentle
    test is `<= GLITCH_GENTLE` (0.30) -- so it took the *scramble* path. The
    renderer now classifies on the midpoint and substitutes the layer's own
    constants, so the two modules' numbers no longer have to match.
    """
    renderer.crt = preset("full")
    flow = _play(renderer, (_WIDTH * 3, _HEIGHT * 3))
    assert renderer._crt is not None
    renderer._menu._view_changed(GENTLE_VIEW_CHANGE)
    renderer.draw(flow)
    assert renderer._crt.glitching, "a deck change fired nothing at all"
    assert renderer._crt._gentle, "a deck change took the scramble path"

    renderer._menu._view_changed(1.0)
    renderer.draw(flow)
    assert not renderer._crt._gentle, "selecting a crew member went gentle"


def test_indicating_a_room_on_another_deck_glitches() -> None:
    """The other half of the report: INDICATE jumps a floor with no glitch.

    Opening the list fired; choosing a room on another deck -- which switches
    the map to that deck -- did not.
    """
    sim = Simulation()
    menu = MenuController(sim)
    elsewhere = next(
        room for room in sim.ship.rooms.values() if room.deck != sim.state.deck
    )
    before = menu.view_epoch
    menu.indicating = True
    entries = menu.entries()
    rows = menu._selectable(entries)
    row = next(
        (i for i, idx in enumerate(rows)
         if entries[idx].indicate_room == elsewhere.id),
        None,
    )
    if row is None:                      # page two holds the rest of the rooms
        menu.indicate_page = 1
        entries = menu.entries()
        rows = menu._selectable(entries)
        row = next(
            i for i, idx in enumerate(rows)
            if entries[idx].indicate_room == elsewhere.id
        )
    menu.cursor = row
    menu.fire()
    assert sim.state.deck == elsewhere.deck, "the probe did not change deck"
    assert menu.view_epoch > before, "changing deck by INDICATE fired nothing"


# --- the view follows the crew, and the tube follows the view (DISC-269) ---


def test_a_crew_member_changing_floors_glitches(renderer: PygameRenderer) -> None:
    """The reported bug, and the path no wiring could have caught.

    `[C $4CC7-$4CE2]` the map follows the selected crew member's deck, and
    `play.py` does that by assigning `state.deck` directly — inside `render()`,
    after the trigger check has already run, and through no menu action at all.
    So the view jumped a floor with nothing to observe it. The renderer now
    watches the state instead of the call sites.
    """
    renderer.crt = preset("full")
    flow = _play(renderer, (_WIDTH * 3, _HEIGHT * 3))
    renderer._present()
    sim = flow.sim
    assert sim is not None
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    renderer._menu.selected_crew = crew.id
    renderer.draw(flow)                       # settle: remember where they are
    assert renderer._crt is not None
    renderer._crt.advance(DEGAUSS_SECONDS + GLITCH_SECONDS)
    assert not renderer._crt.glitching

    here = sim.ship.rooms[crew.room_id].deck
    crew.room_id = next(
        r.id for r in sim.ship.rooms.values() if r.deck != here
    )
    renderer.draw(flow)
    assert renderer._crt.glitching, "the crew changed floors and nothing fired"
    assert renderer._crt._gentle, "a floor change should be the gentle one"


def test_the_map_jumping_a_floor_glitches_however_it_happened(
    renderer: PygameRenderer,
) -> None:
    """Observing the state covers paths that do not exist yet.

    DISC-268 wired the deck changes by name and still missed one. Whatever moves
    `state.deck` — a menu row, INDICATE, the crew-follow in `play.py`, or
    something added later — the map just jumped a floor.
    """
    renderer.crt = preset("full")
    flow = _play(renderer, (_WIDTH * 3, _HEIGHT * 3))
    renderer._present()
    sim = flow.sim
    assert sim is not None
    renderer._menu.selected_crew = None       # nothing to follow, nothing to fight
    renderer.draw(flow)
    assert renderer._crt is not None
    renderer._crt.advance(DEGAUSS_SECONDS + GLITCH_SECONDS)

    sim.state.deck = next(d for d in sim.ship.decks() if d != sim.state.deck)
    renderer.draw(flow)
    assert renderer._crt.glitching, "the map moved a floor with no glitch"


def test_the_first_frame_does_not_glitch(renderer: PygameRenderer) -> None:
    """Arriving on the play screen is not a deck change.

    The remembered deck starts as `None` precisely so the first observation
    seeds it rather than reading as a jump.
    """
    renderer.crt = preset("full")
    flow = _play(renderer, (_WIDTH * 3, _HEIGHT * 3))
    renderer._present()
    assert renderer._crt is not None
    assert not renderer._crt.glitching
