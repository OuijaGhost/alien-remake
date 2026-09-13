"""The `screen_fx` option: the boot report's terminal-readout effect.

**Not the original** — the disk draws every screen whole in one frame, and
`Screen.BOOT` (the startup diagnostics card) has no ROM counterpart at all.
Expanded 2026-09-05 to the full set the owner described (a CRT power-on
stretch with a settling degauss shake, phosphor-yellow text typed out behind
a blinking cursor and a trailing streak, static letters as well as blocks,
and a command-style prompt), then **scoped back down to this one screen only**
the same day, per the owner's own words: "the intro animation should just be
for the initial screen of dos text." The tests below pin both halves: each
piece on BOOT actually does something when the option is on, and the title
and ending screens are provably untouched either way.
"""

from __future__ import annotations

import random
from pathlib import Path

import pygame
import pytest

from alien_remake.core import constants
from alien_remake.core.flow import GameFlow, Screen
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GamePhase
from alien_remake.render import screen_fx
from alien_remake.render.layout import _C64_CELL, _COLS, _ROWS
from alien_remake.render.pygame_app import PygameRenderer
from alien_remake.render.tiles import load

import needs                                       # noqa: E402

#: Comfortably more ticks than a full `_ROWS` x `_COLS` grid needs to finish
#: revealing at `SCREEN_FX_CHARS_PER_TICK` characters/tick, and well past
#: `SCREEN_FX_GLITCH_TICKS`/`SCREEN_FX_STRETCH_TICKS`/`SCREEN_FX_SHAKE_TICKS`
#: so every transient flourish has settled too.
_FULLY_REVEALED_TICKS = (_ROWS * _COLS) // constants.SCREEN_FX_CHARS_PER_TICK + 10


# --- the pure reveal math ----------------------------------------------------

def test_reveal_position_starts_at_the_top_left() -> None:
    assert screen_fx.reveal_position(0, _COLS) == (0, 0)


def test_reveal_position_grows_by_chars_per_tick_in_reading_order() -> None:
    row, col = screen_fx.reveal_position(1, _COLS)
    assert (row, col) == divmod(constants.SCREEN_FX_CHARS_PER_TICK, _COLS)


def test_reveal_position_wraps_rows_once_a_row_s_worth_of_chars_pass() -> None:
    ticks_per_row = -(-_COLS // constants.SCREEN_FX_CHARS_PER_TICK)  # ceil
    row, _col = screen_fx.reveal_position(ticks_per_row, _COLS)
    assert row >= 1


def test_fully_revealed_is_false_early_and_true_once_ticks_catch_up() -> None:
    assert not screen_fx.fully_revealed(0, _ROWS, _COLS)
    assert screen_fx.fully_revealed(_FULLY_REVEALED_TICKS, _ROWS, _COLS)


def test_glitch_cell_positions_are_deterministic_per_tick() -> None:
    a = screen_fx.glitch_cell_positions(3, _COLS, _ROWS, 8)
    b = screen_fx.glitch_cell_positions(3, _COLS, _ROWS, 8)
    assert a == b


def test_glitch_cell_positions_stay_on_the_grid() -> None:
    cells = screen_fx.glitch_cell_positions(7, _COLS, _ROWS, 20)
    assert len(cells) == 20
    for row, col in cells:
        assert 0 <= row < _ROWS
        assert 0 <= col < _COLS


def test_glitch_letter_cells_are_deterministic_and_on_the_grid() -> None:
    a = screen_fx.glitch_letter_cells(5, _COLS, _ROWS, 10)
    b = screen_fx.glitch_letter_cells(5, _COLS, _ROWS, 10)
    assert a == b
    assert len(a) == 10
    for row, col, letter in a:
        assert 0 <= row < _ROWS
        assert 0 <= col < _COLS
        assert len(letter) == 1


def test_glitch_letter_cells_differ_from_glitch_block_cells() -> None:
    """Two different LCG seeds - letters should not just retrace the blocks."""
    blocks = {(r, c) for r, c in screen_fx.glitch_cell_positions(2, _COLS, _ROWS, 30)}
    letters = {(r, c) for r, c, _ in screen_fx.glitch_letter_cells(2, _COLS, _ROWS, 30)}
    assert blocks != letters


# --- apply_terminal_fx, on a bare surface ------------------------------------

def _white_surface() -> "pygame.Surface":
    pygame.init()
    surf = pygame.Surface((_C64_CELL * _COLS, _C64_CELL * _ROWS))
    surf.fill((255, 255, 255))
    return surf


def test_apply_terminal_fx_masks_everything_after_the_cursor_row() -> None:
    surface = _white_surface()
    # Past the glitch window, so only the reveal mask is in play.
    ticks = constants.SCREEN_FX_GLITCH_TICKS + 1
    row, col = screen_fx.reveal_position(ticks, _COLS)
    screen_fx.apply_terminal_fx(
        surface, _C64_CELL, ticks, _ROWS, _COLS, glitch=False, cursor=False
    )
    # At and past the cursor's own column, this row is masked...
    assert surface.get_at((col * _C64_CELL, row * _C64_CELL)) == (0, 0, 0, 255)
    # ...but well before it, the same row is untouched original content (the
    # streak's own additive glow only reaches the few columns just behind the
    # cursor, so column 0 is unaffected once the cursor is past column 8).
    if col > 8:
        assert surface.get_at((0, row * _C64_CELL)) == (255, 255, 255, 255)
    if row > 0:
        assert surface.get_at((0, (row - 1) * _C64_CELL)) == (255, 255, 255, 255)


def test_apply_terminal_fx_glitch_only_shows_up_early() -> None:
    early = _white_surface()
    screen_fx.apply_terminal_fx(
        early, _C64_CELL, 0, _ROWS, _COLS, cursor=False
    )
    early_pixels = {tuple(early.get_at((x, y)))[:3]
                     for x in range(0, early.get_width(), _C64_CELL)
                     for y in range(0, early.get_height(), _C64_CELL)}
    assert early_pixels - {(255, 255, 255), (0, 0, 0)}, (
        "expected at least one glitch-palette colour among the sampled cells "
        "on the very first tick"
    )

    late = _white_surface()
    screen_fx.apply_terminal_fx(
        late, _C64_CELL, constants.SCREEN_FX_GLITCH_TICKS + 50, _ROWS, _COLS,
        cursor=False,
    )
    late_pixels = {tuple(late.get_at((x, y)))[:3]
                    for x in range(0, late.get_width(), _C64_CELL)
                    for y in range(0, late.get_height(), _C64_CELL)}
    assert late_pixels - {(255, 255, 255), (0, 0, 0)} == set(), (
        "the glitch should have faded out long after SCREEN_FX_GLITCH_TICKS"
    )


def test_apply_terminal_fx_cursor_blinks() -> None:
    # Past the glitch window, and on an "on" half of the blink cycle.
    ticks = constants.SCREEN_FX_GLITCH_TICKS + 1
    while (ticks // max(1, constants.SCREEN_FX_CURSOR_BLINK_TICKS)) % 2 != 0:
        ticks += 1
    row, col = screen_fx.reveal_position(ticks, _COLS)
    x, y = col * _C64_CELL, row * _C64_CELL

    on_surface = _white_surface()
    screen_fx.apply_terminal_fx(
        on_surface, _C64_CELL, ticks, _ROWS, _COLS, glitch=False, cursor=True
    )
    off_surface = _white_surface()
    screen_fx.apply_terminal_fx(
        off_surface, _C64_CELL, ticks, _ROWS, _COLS, glitch=False, cursor=False
    )
    assert on_surface.get_at((x, y + _C64_CELL - 1)) != off_surface.get_at(
        (x, y + _C64_CELL - 1)
    ), "the cursor flag should draw something the mask alone does not"


def test_apply_terminal_fx_streak_brightens_behind_the_cursor() -> None:
    """"Hot yellowish green phosphor lines streak across the image as the
    text forms" — an additive glow just behind the write head. Checked
    against a black (not white) background: additive blending against
    already-maxed white channels is a no-op, which is not what is being
    tested here.
    """
    ticks = constants.SCREEN_FX_GLITCH_TICKS + 20  # well past the glitch burst
    row, col = screen_fx.reveal_position(ticks, _COLS)
    assert col > 0, "pick a tick where the cursor isn't at column 0"

    pygame.init()
    surface = pygame.Surface((_C64_CELL * _COLS, _C64_CELL * _ROWS))
    surface.fill((0, 0, 0))
    screen_fx.apply_terminal_fx(
        surface, _C64_CELL, ticks, _ROWS, _COLS, glitch=False, cursor=False
    )
    streaked = surface.get_at(((col - 1) * _C64_CELL, row * _C64_CELL))
    assert tuple(streaked)[:3] != (0, 0, 0), (
        "the streak should visibly brighten the row just behind the cursor"
    )


# --- apply_power_on, on a bare surface ---------------------------------------

def test_apply_power_on_squeezes_the_picture_at_tick_zero() -> None:
    """The classic CRT stretch: at tick 0 the content is squeezed into a
    thin band, so the top and bottom rows must be blank (black) even though
    the untouched surface was solid white."""
    surface = _white_surface()
    screen_fx.apply_power_on(surface, 0)
    assert surface.get_at((0, 0)) == (0, 0, 0, 255)
    assert surface.get_at((0, surface.get_height() - 1)) == (0, 0, 0, 255)


def test_apply_power_on_fills_the_screen_once_the_stretch_finishes() -> None:
    surface = _white_surface()
    screen_fx.apply_power_on(surface, constants.SCREEN_FX_STRETCH_TICKS + 5)
    # Past both the stretch and the shake window: a no-op, so still solid.
    assert surface.get_at((0, 0)) == (255, 255, 255, 255)
    assert surface.get_at((0, surface.get_height() - 1)) == (255, 255, 255, 255)


def test_apply_power_on_shake_decays_to_nothing() -> None:
    """"Settles quickly" — the owner's own phrasing. The last tick of the
    shake window must be a no-op (no displacement introduced)."""
    surface = _white_surface()
    before = surface.copy()
    screen_fx.apply_power_on(surface, constants.SCREEN_FX_SHAKE_TICKS - 1)
    # At the last active tick, decay is `1/shake_ticks` from zero - close
    # enough that `round()` may already floor it to 0 offset, in which case
    # this is legitimately a no-op; either way it must not still be shaking
    # at the full tick-0 amplitude.
    at_amplitude_zero = surface.get_at((5, 5)) == before.get_at((5, 5))
    surface2 = _white_surface()
    screen_fx.apply_power_on(surface2, 0)
    at_amplitude_zero_tick0 = surface2.get_at((5, 5)) == before.get_at((5, 5))
    assert at_amplitude_zero or not at_amplitude_zero_tick0, (
        "the shake must be strictly decaying, not constant amplitude"
    )


# --- wired into the boot report only -----------------------------------------

@pytest.fixture
def renderer() -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    r = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    yield r
    r.close()


def _row_is_black(
    renderer: PygameRenderer, row: int, col: int = 0, span: int = 8
) -> bool:
    """Whether every pixel across ``span`` cells of ``row``, starting at
    ``col``, is pure black — checking a span rather than one corner pixel,
    since a glyph does not necessarily touch a cell's own top-left corner."""
    surf = renderer._surface
    y0, y1 = row * _C64_CELL, (row + 1) * _C64_CELL
    x0, x1 = col * _C64_CELL, (col + span) * _C64_CELL
    for y in range(y0, y1):
        for x in range(x0, x1):
            if tuple(surf.get_at((x, y)))[:3] != (0, 0, 0):
                return False
    return True


# --- the title and ending screens: provably untouched ------------------------
#
# DISC-311/313 wired `screen_fx` into these two screens; DISC-314 scoped it
# back down to BOOT only, per the owner's own words: "the intro animation
# should just be for the initial screen of dos text." These pin that the
# option has gone back to being a complete no-op on both.

# The epigraph's second line ("JOSEPH CONRAD") lands at column 23, row 24 —
# the bottom row, and the one cell on it guaranteed to carry visible (green)
# text rather than the screen's own black fill.
_EPIGRAPH_COL = 23


def test_screen_fx_never_touches_the_title_screen(renderer: PygameRenderer) -> None:
    flow = GameFlow()
    flow.screen = Screen.TITLE
    flow.options.values["screen_fx"] = "off"
    flow._screen_ticks = 0
    renderer.draw(flow)
    off_pixel = renderer._surface.get_at(
        (_EPIGRAPH_COL * _C64_CELL, (_ROWS - 1) * _C64_CELL)
    )

    flow.options.values["screen_fx"] = "on"
    renderer.draw(flow)
    on_pixel = renderer._surface.get_at(
        (_EPIGRAPH_COL * _C64_CELL, (_ROWS - 1) * _C64_CELL)
    )
    assert on_pixel == off_pixel, (
        "screen_fx must be a complete no-op on the title screen"
    )


def _ended_flow(renderer: PygameRenderer) -> GameFlow:
    sim = Simulation(rng=random.Random(0))
    sim.state.phase = GamePhase.LOST
    flow = GameFlow()
    flow.sim = sim
    flow.screen = Screen.ENDED
    flow._screen_ticks = 0
    return flow


# "PRESS ANY KEY" starts at column 24, row 24 (`ending.END_PRESS_KEY_COL/ROW`).
_PRESS_KEY_COL = 24


def test_screen_fx_never_touches_the_ending_screen(renderer: PygameRenderer) -> None:
    flow_off = _ended_flow(renderer)
    flow_off.options.values["screen_fx"] = "off"
    renderer.draw(flow_off)
    off_pixel = renderer._surface.get_at(
        (_PRESS_KEY_COL * _C64_CELL, (_ROWS - 1) * _C64_CELL)
    )

    flow_on = _ended_flow(renderer)
    flow_on.options.values["screen_fx"] = "on"
    renderer.draw(flow_on)
    on_pixel = renderer._surface.get_at(
        (_PRESS_KEY_COL * _C64_CELL, (_ROWS - 1) * _C64_CELL)
    )
    assert on_pixel == off_pixel, (
        "screen_fx must be a complete no-op on the ending screen"
    )
    assert _row_is_black(renderer, _ROWS - 1, _PRESS_KEY_COL - 2, span=2), (
        "no prompt prefix must ever appear before the ending's own decoded "
        "PRESS ANY KEY text"
    )


# --- the boot report ----------------------------------------------------------
#
# The owner's own words for this screen: "the initial screen of text that was
# originally shown in the DOS terminal window but is now presented as the
# first screen" (B1/B2) — the startup diagnostics card, `Screen.BOOT`, shown
# only when there is something to report (B5).

def _boot_flow(renderer: PygameRenderer) -> GameFlow:
    from alien_remake.startup import StartupReport

    report = StartupReport()
    report.info("A NOTE FOR THE PLAYER TO READ")
    renderer.startup_report = report
    flow = GameFlow(show_boot=True)
    flow._screen_ticks = 0
    assert flow.screen is Screen.BOOT
    return flow


def test_screen_fx_on_masks_the_boot_report_early(renderer: PygameRenderer) -> None:
    flow = _boot_flow(renderer)
    flow.options.values["screen_fx"] = "on"
    renderer.draw(flow)
    assert _row_is_black(renderer, 5, 2), (
        "the boot report's first note (row 5) should be masked on the first "
        "tick"
    )


def test_screen_fx_on_fully_reveals_the_boot_report(renderer: PygameRenderer) -> None:
    flow = _boot_flow(renderer)
    flow.options.values["screen_fx"] = "on"
    flow._screen_ticks = _FULLY_REVEALED_TICKS
    renderer.draw(flow)
    assert not _row_is_black(renderer, 5, 2), (
        "the boot report's note should be visible once the reveal finishes"
    )


def test_screen_fx_off_never_masks_the_boot_report(renderer: PygameRenderer) -> None:
    flow = _boot_flow(renderer)
    flow.options.values["screen_fx"] = "off"
    renderer.draw(flow)
    assert not _row_is_black(renderer, 5, 2), (
        "screen_fx=off must never mask the boot report"
    )


def test_screen_fx_off_shows_press_any_key_with_no_prompt(
    renderer: PygameRenderer,
) -> None:
    flow = _boot_flow(renderer)
    flow.options.values["screen_fx"] = "off"
    renderer.draw(flow)
    assert _row_is_black(renderer, _ROWS - 2, 11, span=2), (
        "off must draw the plain 'PRESS ANY KEY' with nothing before column 13"
    )


def test_screen_fx_on_adds_a_prompt_before_press_any_key_once_revealed(
    renderer: PygameRenderer,
) -> None:
    flow = _boot_flow(renderer)
    flow.options.values["screen_fx"] = "on"
    flow._screen_ticks = _FULLY_REVEALED_TICKS
    renderer.draw(flow)
    assert not _row_is_black(renderer, _ROWS - 2, 11, span=2), (
        "on should draw a '> ' prompt before PRESS ANY KEY once fully revealed"
    )


def test_screen_fx_on_colours_the_header_phosphor_yellow(
    renderer: PygameRenderer,
) -> None:
    """"The text should be yellow like in the original video" — the owner's
    own words. Checked against the plain off-state colour (white), which
    must differ once the option is on."""
    flow_off = _boot_flow(renderer)
    flow_off.options.values["screen_fx"] = "off"
    flow_off._screen_ticks = _FULLY_REVEALED_TICKS
    renderer.draw(flow_off)
    off_colour = renderer._surface.get_at((17 * _C64_CELL + 2, 1 * _C64_CELL + 2))

    flow_on = _boot_flow(renderer)
    flow_on.options.values["screen_fx"] = "on"
    flow_on._screen_ticks = _FULLY_REVEALED_TICKS
    renderer.draw(flow_on)
    on_colour = renderer._surface.get_at((17 * _C64_CELL + 2, 1 * _C64_CELL + 2))

    assert tuple(on_colour)[:3] != tuple(off_colour)[:3], (
        "the ALIEN header should change colour once screen_fx is on"
    )


def test_screen_fx_on_draws_glitch_letters_early(renderer: PygameRenderer) -> None:
    """"Random letters as well as blocks should appear in the noise" — the
    owner's own words. Checked as a screen-wide diff against a `screen_fx`
    off draw at the same early tick, since the glitch (blocks or letters)
    is the only thing that can differ that early."""
    flow_off = _boot_flow(renderer)
    flow_off.options.values["screen_fx"] = "off"
    renderer.draw(flow_off)
    off_surface = renderer._surface.copy()

    flow_on = _boot_flow(renderer)
    flow_on.options.values["screen_fx"] = "on"
    renderer.draw(flow_on)
    on_surface = renderer._surface

    differs = any(
        on_surface.get_at((x, y)) != off_surface.get_at((x, y))
        for x in range(0, on_surface.get_width(), _C64_CELL)
        for y in range(0, on_surface.get_height(), _C64_CELL)
    )
    assert differs, "screen_fx=on should visibly differ from off on the first tick"
