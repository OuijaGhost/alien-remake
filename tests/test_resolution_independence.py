"""The game draws at 320x200 and scales once, at any window size (DISC-242).

Before this, every draw call pre-multiplied its own coordinates by
``self._scale`` (87 sites) and ``_surface`` was built at ``_WIDTH * scale``, so
the picture was only correct at an integer multiple chosen at construction. Now
the field is always native and :meth:`PygameRenderer.field_rect` decides where
it lands.

The load-bearing test here is
:func:`test_field_content_is_identical_at_every_window_size` — it is the one
that would actually catch a coordinate left multiplied by a stale scale.
"""

from __future__ import annotations

from pathlib import Path

import pygame
import pytest

from alien_remake.render.layout import _HEIGHT, _WIDTH
from alien_remake.render.pygame_app import (
    _BORDER_X, _BORDER_Y, PygameRenderer,
)
from alien_remake.render.tiles import load

#: A spread of window shapes: exact native, exact multiples, awkward
#: non-multiples, wider-than-tall, taller-than-wide, and smaller than native.
WINDOW_SIZES = [
    (384, 264), (768, 528), (1152, 792),      # exact bordered multiples
    (1000, 700), (1280, 800), (1920, 1080),   # real screens, non-exact
    (1600, 500), (500, 1000),                 # extreme aspect ratios
    (300, 200),                               # smaller than one native copy
]


@pytest.fixture
def renderer() -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    r = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    yield r
    r.close()


def _resize(r: PygameRenderer, size: tuple[int, int]) -> None:
    r._window = pygame.display.set_mode(size, pygame.RESIZABLE)


def test_draw_surface_is_native_regardless_of_window(
    renderer: PygameRenderer,
) -> None:
    for size in WINDOW_SIZES:
        _resize(renderer, size)
        assert renderer._surface.get_size() == (_WIDTH, _HEIGHT), (
            f"draw surface followed the window at {size}"
        )


def test_field_keeps_the_native_aspect_ratio_everywhere(
    renderer: PygameRenderer,
) -> None:
    """No stretching: 320:200 is preserved even in a 1600x500 letterbox."""
    for size in WINDOW_SIZES:
        _resize(renderer, size)
        rect = renderer.field_rect()
        assert rect.width * _HEIGHT == rect.height * _WIDTH, (
            f"aspect distorted at {size}: {rect.size}"
        )


def test_field_is_centred(renderer: PygameRenderer) -> None:
    for size in WINDOW_SIZES:
        _resize(renderer, size)
        rect = renderer.field_rect()
        # Off-centre by at most one pixel from integer division.
        assert abs((rect.x * 2 + rect.width) - size[0]) <= 1
        assert abs((rect.y * 2 + rect.height) - size[1]) <= 1


def test_scale_factor_is_always_a_whole_number(renderer: PygameRenderer) -> None:
    """D-056: a C64 draws hard pixels.

    A fractional factor makes some source pixels two window-pixels wide and
    their neighbours three, which reads as shimmer on a pixel-art field.
    """
    for size in WINDOW_SIZES:
        _resize(renderer, size)
        rect = renderer.field_rect()
        assert rect.width % _WIDTH == 0, f"fractional scale at {size}"
        assert rect.width // _WIDTH == rect.height // _HEIGHT
        assert rect.width // _WIDTH >= 1


def test_field_content_is_identical_at_every_window_size(
    renderer: PygameRenderer,
) -> None:
    """Resolution independence, stated directly: the window cannot change the picture.

    Driven through `draw()` across **every** screen, not one of them. A first
    version rendered only WELCOME and passed with a deliberately window-
    dependent coordinate injected into `_blit_cells` — the shared text helper
    that WELCOME happens not to use. Covering the screens the game actually has
    is what makes this test able to fail.
    """
    from alien_remake.core.flow import GameFlow, Screen

    for screen in Screen:
        frames = []
        for size in WINDOW_SIZES:
            _resize(renderer, size)
            flow = GameFlow()
            flow.screen = screen
            renderer._frame_count = 0
            # No try/except: all fourteen screens draw from a bare GameFlow, so
            # swallowing here would only ever hide a real break.
            renderer.draw(flow)
            frames.append((size, pygame.image.tobytes(renderer._surface, "RGB")))

        first_size, first = frames[0]
        for size, data in frames[1:]:
            assert data == first, (
                f"{screen.name} rendered differently at {size} than at "
                f"{first_size} - something still scales with the window"
            )


def test_the_field_lands_at_field_rect_on_both_present_paths(
    renderer: PygameRenderer,
) -> None:
    """`_present` has two blit paths and DISC-239 found only one had been fixed.

    The `_border_flash` early return is the easy one to miss; a stale offset
    there would make the field jump for the duration of every command-accept
    rainbow. Not asserted via the margins — `_draw_border_noise` paints those
    deliberately multicoloured, which is the whole point of the flash — but by
    filling the field with a colour the border never uses and finding it exactly
    where `field_rect` says it should be.
    """
    probe = (3, 251, 177)          # not in the C64 palette, so unmistakable
    _resize(renderer, (1000, 700))

    for flash in (0, 3):
        renderer._surface.fill(probe)
        renderer._border_flash = flash
        renderer._present()
        rect, win = renderer.field_rect(), renderer._window

        assert tuple(win.get_at(rect.center))[:3] == probe, (
            f"field missing from its own rect with flash={flash}"
        )
        for corner in (
            (rect.x, rect.y), (rect.right - 1, rect.y),
            (rect.x, rect.bottom - 1), (rect.right - 1, rect.bottom - 1),
        ):
            assert tuple(win.get_at(corner))[:3] == probe, (
                f"field not filling its rect to the corner with flash={flash}"
            )
        # ...and immediately outside it, the field must NOT be there.
        assert tuple(win.get_at((rect.x - 1, rect.centery)))[:3] != probe
        assert tuple(win.get_at((rect.right, rect.centery)))[:3] != probe


def test_resize_event_updates_the_geometry(renderer: PygameRenderer) -> None:
    """A VIDEORESIZE must be picked up with no other state to refresh."""
    _resize(renderer, (768, 528))
    before = renderer.field_rect()
    pygame.event.post(
        pygame.event.Event(pygame.VIDEORESIZE, {"w": 1152, "h": 792,
                                                "size": (1152, 792)})
    )
    renderer.poll_input(None)
    after = renderer.field_rect()
    assert after != before
    assert after.width // _WIDTH == 3


def test_fullscreen_toggle_restores_the_previous_window_size(
    renderer: PygameRenderer,
) -> None:
    """Leaving fullscreen must not snap back to the default size.

    Needs an actual display mode change to observe, which a machine with no
    real monitor (a headless CI runner, a remote session with no attached
    display) cannot honestly provide — SDL's fallback there is a fixed fake
    desktop size regardless of what windowed size was requested, on the way
    in *and* the way back out, which looks identical to the bug this guards
    against without being one. Detected by probing with the test's own
    baseline size before trusting the real assertion below, rather than
    trying to name every CI/remote-desktop environment that does this.
    """
    _resize(renderer, (1000, 700))
    renderer._windowed_size = (1000, 700)
    # Probe with the *exact* sequence the bug lives in - fullscreen, then
    # back - not just a plain resize, which this same environment honours
    # fine on its own. Only a real display can prove a fullscreen round
    # trip restores the size it left; a headless/remote one silently
    # substitutes its own fake desktop size on the way back out too.
    pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    probed = pygame.display.set_mode((1000, 700), pygame.RESIZABLE).get_size()
    if probed != (1000, 700):
        pytest.skip(
            "no real display to resize - a fullscreen round trip does not "
            f"restore the requested size on this machine (got {probed})"
        )
    assert not renderer._fullscreen

    renderer._toggle_fullscreen()
    assert renderer._fullscreen
    renderer._toggle_fullscreen()
    assert not renderer._fullscreen
    assert renderer._window.get_size() == (1000, 700)


def test_alt_enter_and_f11_both_toggle_fullscreen() -> None:
    """Alt+Enter must be caught before the key tables — Return is bound to FIRE."""
    from alien_remake.render.pygame_app import _is_fullscreen_key

    f11 = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_F11, "mod": 0})
    alt_enter = pygame.event.Event(
        pygame.KEYDOWN, {"key": pygame.K_RETURN, "mod": pygame.KMOD_LALT}
    )
    bare_enter = pygame.event.Event(
        pygame.KEYDOWN, {"key": pygame.K_RETURN, "mod": 0}
    )
    assert _is_fullscreen_key(f11)
    assert _is_fullscreen_key(alt_enter)
    assert not _is_fullscreen_key(bare_enter), "bare Return is FIRE, not fullscreen"


def test_native_window_still_places_the_field_at_the_vic_border(
    renderer: PygameRenderer,
) -> None:
    """At 1x the geometry must still be the authentic 32px VIC border."""
    _resize(renderer, (_WIDTH + 2 * _BORDER_X, _HEIGHT + 2 * _BORDER_Y))
    assert renderer.field_rect() == pygame.Rect(
        _BORDER_X, _BORDER_Y, _WIDTH, _HEIGHT
    )


def test_the_scale_is_maximal_no_step_is_wasted(renderer: PygameRenderer) -> None:
    """The chosen factor must be the largest whole one that fits.

    The first implementation measured the fit against the *bordered* 384x264
    composition, which silently cost a whole step at most real display sizes —
    1366x768 got 2x and filled 24% of the screen where 3x fits and fills 55%.
    Nothing failed; the picture was simply small. This is the invariant that
    would have caught it.
    """
    for size in WINDOW_SIZES + [(1366, 768), (1440, 900), (1600, 900), (2560, 1440)]:
        _resize(renderer, size)
        rect = renderer.field_rect()
        scale = rect.width // _WIDTH
        bigger = scale + 1
        assert not (_WIDTH * bigger <= size[0] and _HEIGHT * bigger <= size[1]), (
            f"{size} chose {scale}x but {bigger}x fits — a whole step wasted"
        )


def test_1280x800_fills_exactly_because_320x200_is_16_to_10(
    renderer: PygameRenderer,
) -> None:
    """The pleasing case, and a claim `field_rect`'s docstring makes.

    An earlier rule gave 3x here, so the docstring was describing behaviour the
    code did not have. Pinned so the prose cannot drift from it again.
    """
    _resize(renderer, (1280, 800))
    assert renderer.field_rect() == pygame.Rect(0, 0, 1280, 800)


def test_the_authentic_32px_border_survives_at_the_native_size(
    renderer: PygameRenderer,
) -> None:
    """Filling the screen better must not cost the real VIC geometry at 1x/2x.

    These are the sizes the game actually opens at, and there the border is
    exactly 32 native pixels — the elastic border only shows up above them.
    """
    for scale in (1, 2, 3):
        _resize(renderer, ((_WIDTH + 2 * _BORDER_X) * scale,
                           (_HEIGHT + 2 * _BORDER_Y) * scale))
        rect = renderer.field_rect()
        assert rect.width // _WIDTH == scale
        assert rect.x == _BORDER_X * scale and rect.y == _BORDER_Y * scale


def test_scaling_introduces_no_new_colours(renderer: PygameRenderer) -> None:
    """D-056, enforced at the one place that could break it.

    Blended edges produce colours outside the 16-entry palette and read as
    "modern"; the whole codebase passes `antialias=False` to avoid it. Scaling
    is now the only step that could reintroduce blending, so `transform.scale`
    (nearest-neighbour) must stay — `smoothscale` would fail this.

    This also closes step 5 of the resolution-independence plan. That step was
    conditional ("if crisper text at large window sizes still matters"), and it
    does not: at an integer factor every source pixel becomes a solid block of
    exactly its own colour, so the ROM's glyph bitmaps are reproduced perfectly
    at any size. Vector-tracing the charset would make text *less* faithful, not
    more, by anti-aliasing shapes the ROM defines as hard pixels.
    """
    from alien_remake.core.flow import GameFlow, Screen

    flow = GameFlow()
    flow.screen = Screen.WELCOME

    _resize(renderer, (_WIDTH, _HEIGHT))
    renderer._frame_count = 200
    renderer.draw(flow)
    native = renderer._window.copy()
    palette = {
        tuple(native.get_at((x, y)))[:3]
        for x in range(0, _WIDTH, 2) for y in range(0, _HEIGHT, 2)
    }

    for k in (2, 4, 6):
        _resize(renderer, (_WIDTH * k, _HEIGHT * k))
        renderer._frame_count = 200
        renderer.draw(flow)
        big = renderer._window
        scaled = {
            tuple(big.get_at((x, y)))[:3]
            for x in range(0, _WIDTH * k, 5) for y in range(0, _HEIGHT * k, 5)
        }
        assert not (scaled - palette), (
            f"{k}x scaling invented colours {scaled - palette} — this is "
            "smoothscale/anti-aliasing creeping in (D-056)"
        )


def test_each_source_pixel_becomes_a_solid_block(renderer: PygameRenderer) -> None:
    """Nearest-neighbour, checked structurally rather than by colour count."""
    from alien_remake.core.flow import GameFlow, Screen

    flow = GameFlow()
    flow.screen = Screen.WELCOME
    k = 5

    _resize(renderer, (_WIDTH, _HEIGHT))
    renderer._frame_count = 200
    renderer.draw(flow)
    native = renderer._window.copy()

    _resize(renderer, (_WIDTH * k, _HEIGHT * k))
    renderer._frame_count = 200
    renderer.draw(flow)
    big = renderer._window

    for y in range(0, _HEIGHT, 7):
        for x in range(0, _WIDTH, 11):
            want = tuple(native.get_at((x, y)))[:3]
            for dy in (0, k // 2, k - 1):
                for dx in (0, k // 2, k - 1):
                    assert tuple(big.get_at((x * k + dx, y * k + dy)))[:3] == want, (
                        f"source pixel ({x},{y}) is not a solid {k}x{k} block"
                    )


def test_the_border_noise_bands_are_c64_raster_lines_not_screen_pixels(
    renderer: PygameRenderer,
) -> None:
    """**DISC-261** — a regression from DISC-242's `* s` sweep.

    `wait_keypress_flash ($8660)` runs `INC $D020` on every input poll, so the
    border comes out as a stack of *raster-line* bands. The thickness was
    `max(1, s)`; the sweep that deleted every scale factor rewrote it to 1,
    because it read as a coordinate and was actually a thickness. The bands then
    became one screen pixel each — at 4x that is 800 hair-thin stripes against a
    picture drawn at 200 lines.

    Counted down the border rather than asserted on the constant, so it stays
    true however the scaling is expressed.
    """
    counts = []
    for size in ((384, 264), (768, 528), (1280, 800), (1920, 1080)):
        _resize(renderer, size)
        renderer._frame_count = 3
        renderer._border_flash = 2
        renderer._draw_border_noise()
        runs, previous = 0, None
        for y in range(size[1]):
            colour = tuple(renderer._window.get_at((1, y)))[:3]
            if colour != previous:
                runs += 1
                previous = colour
        counts.append((size, runs))

    for size, runs in counts:
        assert runs <= 2 * _HEIGHT, (
            f"{size}: {runs} bands — the border is being drawn at window "
            f"resolution, not at the field's {_HEIGHT} raster lines"
        )
    # And it must not simply grow with the window.
    biggest = max(runs for _, runs in counts)
    smallest = min(runs for _, runs in counts)
    assert biggest - smallest < _HEIGHT, (
        f"band count ranges {smallest}..{biggest} across window sizes; it "
        "should be roughly constant"
    )
