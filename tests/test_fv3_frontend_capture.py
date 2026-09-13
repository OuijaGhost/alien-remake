"""Drift guards for the front-end screens transcribed live (D-064 / D-065).

These pin values read out of the **running disk** on 2026-08-01 — screen RAM
`$0400`, colour RAM `$D800` (bank `io`), and the VIC/sprite registers — while
the loader's WELCOME menu was on screen. They are not derived from a
screenshot, so a regression here means the remake stopped matching a measured
machine state, not somebody's taste.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pygame = pytest.importorskip("pygame")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from alien_remake.core.modes import FrontEnd
from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.core import constants  # noqa: E402
from alien_remake.render import c64, romfont  # noqa: E402
from alien_remake.render.frontend import (  # noqa: E402
    _BORDER_COLOUR_FRONTEND,
    _WELCOME_TM_POS,
    _WELCOME_TM_SPRITE,
    _welcome_border_colour,
)
from alien_remake.render.layout import _COLS, _ROWS  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer, _BORDER_COLOUR  # noqa: E402

# The WELCOME border ring, straight out of colour RAM. Corner cells are the
# load-bearing ones: they prove the ROM's draw order (top, right, bottom, left)
# because the side painted last is the value that survived.
_CAPTURED_TOP_ROW = (
    2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    0, 1, 2, 3, 4, 5, 6, 2,
)
_CAPTURED_BOTTOM_ROW = (
    10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    15, 0, 1, 2, 3, 4, 5, 6,
)
_CAPTURED_LEFT_COL = tuple((r + 2) % 16 for r in range(_ROWS))
_CAPTURED_RIGHT_COL = tuple(
    ((r + 2) % 16 if r < _ROWS - 1 else 6) for r in range(_ROWS)
)


def test_welcome_border_reproduces_the_captured_ring_exactly() -> None:
    assert tuple(_welcome_border_colour(0, c) for c in range(_COLS)) == _CAPTURED_TOP_ROW
    assert tuple(
        _welcome_border_colour(_ROWS - 1, c) for c in range(_COLS)
    ) == _CAPTURED_BOTTOM_ROW
    assert tuple(_welcome_border_colour(r, 0) for r in range(_ROWS)) == _CAPTURED_LEFT_COL
    assert tuple(
        _welcome_border_colour(r, _COLS - 1) for r in range(_ROWS)
    ) == _CAPTURED_RIGHT_COL


def test_welcome_border_corners_encode_the_draw_order() -> None:
    """top -> right -> bottom -> left; the last writer wins at each corner."""
    assert _welcome_border_colour(0, 0) == 2            # left beat top
    assert _welcome_border_colour(0, _COLS - 1) == 2    # right beat top
    assert _welcome_border_colour(_ROWS - 1, 0) == 10   # left beat bottom
    assert _welcome_border_colour(_ROWS - 1, _COLS - 1) == 6  # bottom beat right


def test_welcome_border_is_only_the_ring() -> None:
    for row in range(1, _ROWS - 1):
        for col in range(1, _COLS - 1):
            assert _welcome_border_colour(row, col) is None


def test_welcome_trademark_is_the_captured_sprite_bitmap() -> None:
    """Sprite 0 at (274,72), pointer $07F8=$0D -> $0340. The ROM font has no
    "™", so the loader hand-draws one; only 12x5 pixels carry ink."""
    assert _WELCOME_TM_SPRITE == (
        "#####..#...#",
        "..#....##.##",
        "..#....#.#.#",
        "..#....#...#",
        "..#....#...#",
    )
    # (274, 72) minus the VIC field origin (24, 50).
    assert _WELCOME_TM_POS == (250, 22)


def test_frontend_border_is_black_not_the_play_screens_blue() -> None:
    """D-064: `vice_vicii_get_state` reported border_color 0 on WELCOME, while
    the play screen sets `$D020` = 6 ([C $7013])."""
    assert _BORDER_COLOUR_FRONTEND == c64.rgb(c64.BLACK)
    assert _BORDER_COLOUR == c64.rgb(c64.BLUE)
    assert _BORDER_COLOUR_FRONTEND != _BORDER_COLOUR


# --- the real chargen ROM (D-065) -------------------------------------------

def test_romfont_maps_the_two_banks_the_way_the_loader_uses_them() -> None:
    """WELCOME is capitals (unshifted bank); NOTICE is mixed case (shifted)."""
    sc = romfont.RomFont.screen_code
    # Unshifted: $01-$1A are A-Z. WELCOME's screen RAM read 07 12 05 05 0E for
    # "GREEN", which is exactly this mapping.
    assert [sc(ch) for ch in "GREEN"] == [0x07, 0x12, 0x05, 0x05, 0x0E]
    # Shifted: $01-$1A are lowercase, $41-$5A uppercase.
    assert sc("a", shifted=True) == 1
    assert sc("A", shifted=True) == 0x41
    # $20-$3F maps to itself in both banks — so digits and ':' need no
    # special-casing here, unlike ALIEN's own charset where they are still [?].
    for ch in " !()0123456789:?":
        assert sc(ch) == ord(ch)
        assert sc(ch, shifted=True) == ord(ch)
    # Never guesses.
    assert sc("™") is None
    assert sc("£") is None


@pytest.mark.skipif(romfont.load() is None, reason="chargen ROM not present")
def test_romfont_glyphs_decode_to_the_real_shapes() -> None:
    font = romfont.load()
    assert font is not None
    rows = font.glyph_rows(font.screen_code("A") or 0)
    assert rows == (0x18, 0x3C, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x00)
    # '1' lives at its ASCII value in both banks.
    assert font.glyph_rows(0x31) == (0x18, 0x18, 0x38, 0x18, 0x18, 0x18, 0x7E, 0x00)


@pytest.fixture
def renderer() -> PygameRenderer:
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    if not charset.exists():
        pytest.skip("out/charset.bin not present (run `alientools chars` first)")
    r = PygameRenderer(scale=2, tiles=load(charset), intro_wav=None)
    yield r
    pygame.quit()


def test_frontend_text_lands_on_the_8px_character_grid(
    renderer: PygameRenderer,
) -> None:
    """D-065: front-end lines must be exactly 8px per character.

    The captured column positions are meaningless otherwise. SysFont is ~4.3px
    wide at this size, which used to compress every line to about half its true
    width — the row-9 rule under "FACE THE POWER OF THE UNKNOWN" is 29 cells,
    and the text above it fell visibly short of it.
    """
    if renderer._romfont is None:
        pytest.skip("chargen ROM not present")
    for text in ("A", "WELCOME TO ALIEN", "COPYRIGHT(C)1985 ALL RIGHTS RESERVED"):
        surf = renderer._render_rom_text(text, c64.rgb(c64.WHITE))
        assert surf is not None
        assert surf.get_width() == 8 * len(text)
        assert surf.get_height() == 8


def test_welcome_frame_uses_only_palette_colours(renderer: PygameRenderer) -> None:
    """Every pixel of the finished screen must be a real C64 colour."""
    flow = GameFlow()
    flow.screen = Screen.WELCOME
    renderer._draw_welcome(flow)
    palette = {c64.rgb(i) for i in range(16)}
    seen = {
        tuple(renderer._window.get_at((x, y)))[:3]
        for x in range(0, renderer._window.get_width(), 3)
        for y in range(0, renderer._window.get_height(), 3)
    }
    assert seen <= palette, f"non-palette colours on WELCOME: {seen - palette}"


def test_welcome_ring_is_actually_painted(renderer: PygameRenderer) -> None:
    """Guard the ring itself, not just the rule: sample the four corners of the
    field and check they carry their captured colours.

    **D-143** — the ring now sweeps in over ~48 frames rather than appearing
    whole, so this must let it finish: draw once to start the local frame
    counter, then draw again well past completion.
    """
    from alien_remake.render.pygame_app import _BORDER_X, _BORDER_Y

    flow = GameFlow()
    flow.screen = Screen.WELCOME
    renderer._draw_welcome(flow)
    renderer._frame_count += 200
    renderer._draw_welcome(flow)
    # Map a field cell into window space through `field_rect` (DISC-242): the
    # field is centred and integer-scaled, so `_BORDER_X * scale` is no longer
    # where it starts.
    rect = renderer.field_rect()
    s = rect.width // 320
    def cell(row: int, col: int) -> tuple[int, int, int]:
        x = rect.x + (col * 8 + 4) * s
        y = rect.y + (row * 8 + 4) * s
        return tuple(renderer._window.get_at((x, y)))[:3]

    assert cell(0, 0) == c64.rgb(2)
    assert cell(0, _COLS - 1) == c64.rgb(2)
    assert cell(_ROWS - 1, 0) == c64.rgb(10)
    assert cell(_ROWS - 1, _COLS - 1) == c64.rgb(6)
    assert cell(0, 8) == c64.rgb(8)


# --- R-37: the animated location pointer (D-082) -----------------------------

def test_pointer_frames_stop_before_the_character_glyph() -> None:
    """**[C $4FDB] P4-3 — rewritten 2026-08-02; `$B8` is never displayed.**

    `update_4 ($4FCB)` is `DEC $657A / LDA $657A / CMP #$B8 / BNE + /
    LDA #$BC / STA $657A` and only **then** `STA $07F9`. The counter reaching
    `$B8` is reset to `$BC` *before* the store, so the displayed cycle is four
    frames: `$BC $BB $BA $B9`.

    This test used to assert five frames ending on `$B8`, on D-082's reading
    that "the animation resolves into the character-position glyph". That extra
    frame is the crew icon a player reported seeing flash inside the INDICATE
    animation.
    """
    from alien_remake.render.play import (
        _CHAR_SPRITE,
        _POINTER_FRAMES,
        _SPRITE_SLOT_BASE,
    )

    slots = tuple(i + _SPRITE_SLOT_BASE for i in _POINTER_FRAMES)
    assert slots == (0xBC, 0xBB, 0xBA, 0xB9)
    assert _CHAR_SPRITE not in _POINTER_FRAMES, (
        "the character glyph is the wrap sentinel, not a frame"
    )


def test_pointer_frames_decode_to_expanding_rectangles() -> None:
    """The five slots are concentric expanding rectangles resolving into a
    figure — which is what makes this a "locate" animation rather than a blink.
    Measured as the ink width of each frame's widest row."""
    from pathlib import Path

    from alien_remake.render.play import _POINTER_FRAMES
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    if not charset.exists():
        pytest.skip("out/charset.bin not present")
    tiles = load(charset)
    widths = []
    for idx in _POINTER_FRAMES:               # all four are rectangles now
        bmp = tiles.sprites[idx]
        widest = max(
            (max(i for i, v in enumerate(row) if v)
             - min(i for i, v in enumerate(row) if v) + 1)
            for row in bmp if any(row)
        )
        widths.append(widest)
    # $BC smallest -> $B9 largest: strictly expanding.
    assert widths == sorted(widths), f"frames should expand, got {widths}"
    assert widths[-1] > widths[0]


# --- P2-13: the GREEN VALLEY spiral is animated ------------------------------

def test_spiral_replays_the_loaders_basic_exactly() -> None:
    """**[C MENU1.prg lines 150-280] D-104.** The loader's first screen is a
    colour-RAM spiral: 22 concentric rings (Q sweeping 11 -> 1 -> 11), each a
    flat colour, cycling 0-15 from a start of 8. Ring Q spans rows Q..25-Q and
    columns Q..39-Q.
    """
    from alien_remake.render.frontend import _SPIRAL_RINGS, spiral_colours
    from alien_remake.render.layout import _SPIRAL_START_COLOUR

    assert _SPIRAL_RINGS == tuple(range(11, 0, -1)) + tuple(range(1, 12))
    assert len(_SPIRAL_RINGS) == 22
    assert _SPIRAL_START_COLOUR == 8

    # One ring drawn: exactly the ring Q=11's perimeter, in colour 9.
    one = spiral_colours(1)
    top, bottom, left, right = 11, 25 - 11, 11, 39 - 11
    assert one[top][right] == 9 and one[bottom][left] == 9
    assert one[top][left] == 9
    # ...and nothing outside it.
    assert one[top - 1][right] is None
    assert one[top][left - 1] is None

    # Each ring is a single flat colour — unlike the WELCOME ring's gradient.
    assert len({one[top][c] for c in range(left, right + 1)}) == 1


def test_spiral_geometry_matches_the_basic_formulae() -> None:
    """`UL=CM+Q+Q*WD`, `UR=CM+Q*WD+(T1-Q)`, `LL=CM+(T2-Q)*WD+Q`,
    `LR=CM+(T1-Q)+WD*(T2-Q)` with WD=40, T1=39, T2=25."""
    from alien_remake.render.frontend import spiral_colours

    grid = spiral_colours(22)
    # The outermost ring the spiral ever reaches is Q=1 -> rows 1..24, cols 1..38.
    assert grid[1][1] is not None and grid[24][38] is not None
    # Row 0 and column 0 are never painted — the spiral starts one cell in.
    assert all(v is None for v in grid[0])
    assert all(row[0] is None for row in grid)
    assert all(row[39] is None for row in grid)


def test_the_spiral_animates_rather_than_settling() -> None:
    """The whole point of P2-13: successive steps must differ."""
    from alien_remake.render.frontend import _SPIRAL_RINGS, spiral_colours

    seen = {
        tuple(tuple(r) for r in spiral_colours(k))
        for k in range(1, len(_SPIRAL_RINGS) + 1)
    }
    assert len(seen) == len(_SPIRAL_RINGS), "every step should look different"


def test_the_spiral_is_not_the_welcome_ring() -> None:
    """They are different effects and were easy to confuse: the WELCOME ring
    (D-064) is a per-cell gradient captured live, while each spiral ring is one
    flat colour."""
    from alien_remake.render.frontend import spiral_colours

    grid = spiral_colours(22)
    ring_row = [grid[1][c] for c in range(2, 39)]
    assert len(set(ring_row)) == 1, "a spiral ring is flat"
    assert len(set(_CAPTURED_TOP_ROW)) > 1, "the WELCOME ring is a gradient"


# --- P3-13: no in-game string may fall back to SysFont ------------------------

def test_every_status_line_renders_in_the_games_own_charset() -> None:
    """**R-01 / P3-13.** The whole point of the charset work is that no in-game
    string falls back to `SysFont` — a fallback renders at a different size and
    face to everything around it, which is exactly what the player saw.

    The culprit was a `"-"` placeholder for an empty ALSO HERE field: one
    unmapped character makes the *entire line* fail the charset path. This test
    pins the alphabet the status lines actually use, so the next stray glyph is
    caught here rather than in play.
    """
    from alien_remake.render.pygame_app import _ASCII_TO_SCREEN_CODE

    samples = [
        "COMMDCENTR  DAMAGE 00%   GRILLE IN PLACE",
        "COMMDCENTR  DAMAGE 99% :WARNING:   GRILLE REMOVED",
        "DALLAS IS O.K.    MORALE:CONFIDENT",
        "ALSO HERE: RIPLEY, PARKER",
        "ALSO HERE: ",
        ":WARNING: COMPUTER MALFUNCTION",
        "TRACKER ALARM: SOMETHING MOVING",
        "NO CREW",
    ]
    for text in samples:
        missing = sorted({c for c in text if c not in _ASCII_TO_SCREEN_CODE})
        assert not missing, f"{text!r} would fall back to SysFont: {missing}"


def test_the_dash_placeholder_is_gone() -> None:
    """It was never a ROM glyph — `-` is absent from the charset map, and the
    original leaves an empty field as blanks (`$A0`)."""
    from alien_remake.render.pygame_app import _ASCII_TO_SCREEN_CODE

    assert "-" not in _ASCII_TO_SCREEN_CODE, (
        "if a dash is ever mapped it must be because a real glyph was decoded"
    )


# --- P3-8 / P3-11: Q quits, and the border flash is raster-banded ------------

def test_q_on_the_welcome_screen_loads_the_exit_advert(
    renderer: PygameRenderer,
) -> None:
    """**[C MENU1 740/830 -> EXITO.prg] D-175, PV-01 - Q does not exit.**

    P3-8 made Q end the program, which is what the player reported as wrong.
    MENU1 line 740 sets `CC=0` / `P$(0)="EXIT*"` (skipping the instructions
    prompt and the joystick line), and line 830 stuffs `LOAD"EXIT*",8` into the
    keyboard buffer. EXITO draws the marquee, three centre-out lines and a
    block-graphic **ONE-STEP DEALER** logo, waits `FOR XX=1TO3000`, then
    `SYS 64738` - a cold reset, which lands you back at the boot screen.
    """
    from alien_remake.core.flow import GameFlow, Screen as _S
    from alien_remake.render.pygame_app import _MENU_KEYS

    assert _MENU_KEYS[pygame.K_q] is InputEvent.QUIT_TO_ADVERT
    assert renderer.should_quit() is False
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=0))
    events = renderer.poll_input(_S.WELCOME)
    assert InputEvent.QUIT_TO_ADVERT in events
    assert renderer.should_quit() is False, "Q must NOT end the program"

    flow = GameFlow(front_end=FrontEnd.CLASSIC)  # DISC-262: this asserts the original's full boot chain
    flow.screen = _S.WELCOME
    flow.handle(InputEvent.QUIT_TO_ADVERT)
    assert flow.screen is _S.EXIT_ADVERT

    # It holds for EXITO's `FOR XX=1TO3000` and then the program ends.
    # **Corrected 2026-08-07 (D-185):** this first asserted a loop back to
    # LOADING_MENU, on the reading that `SYS 64738` "restarts the machine".
    # A reset leaves a bare BASIC READY prompt with the game gone - it does
    # not replay the loader - so for a program that *is* only the game the
    # faithful equivalent is to exit.
    for _ in range(constants.EXIT_ADVERT_TICKS - 1):
        flow.tick()
        assert not flow.finished, "the advert must hold, not flash past"
        assert flow.screen is _S.EXIT_ADVERT
    flow.tick()
    assert flow.finished, "SYS 64738 ends the program"
    assert flow.screen is _S.EXIT_ADVERT, "...still showing the advert as it goes"



def test_the_border_flash_shows_the_whole_palette_at_once(
    renderer: PygameRenderer,
) -> None:
    """**P3-11.** `wait_keypress_flash ($8660)` runs `INC $D020` on **every
    input poll** — thousands of times a second — so `$D020` changes many times
    within one displayed frame and the border reads as a dense stack of colour
    bands. Stepping one palette entry per rendered frame gave a slow readable
    cycle: right colours, wrong rate.
    """
    renderer._border_flash = 3
    renderer._frame_count = 0
    renderer._present()
    window = renderer._window
    seen = {
        tuple(window.get_at((2, y)))[:3]
        for y in range(0, window.get_height(), 2)
    }
    assert len(seen) >= 8, f"expected many bands in one frame, saw {len(seen)}"
    palette = {c64.rgb(i) for i in range(16)}
    assert seen <= palette, "bands must be real C64 colours"


def test_the_border_flash_survives_the_play_screens_own_border_colour(
    renderer: PygameRenderer,
) -> None:
    """**DISC-221.** The play screen never passes ``border=None`` to `_present`.

    Once SCUTTLE's blue/yellow flash shipped (`_play_border`, DISC-212), every
    play-screen frame calls `_present(self._play_border(state))` with a
    concrete colour — never `None`. `_present` used to only run the "command
    accepted" rainbow when `border is None`, so passing any real colour (the
    play screen's ordinary blue included) silently suppressed it. The two
    features never overlap in the ROM (`wait_keypress_flash` blocks the main
    loop while it runs), so the flash must win regardless of what `border` the
    caller passes.
    """
    renderer._border_flash = 3
    renderer._frame_count = 0
    renderer._present(c64.rgb(c64.BLUE))          # what the play screen sends
    window = renderer._window
    seen = {
        tuple(window.get_at((2, y)))[:3]
        for y in range(0, window.get_height(), 2)
    }
    assert len(seen) >= 8, "a concrete border colour must not suppress the flash"


# --- P3-7 / P3-10 -------------------------------------------------------------

def test_the_welcome_ring_is_the_loaders_marquee_and_rotates() -> None:
    """**[C MENU1.prg 330-380] P3-7.** The ring is the loader's own
    `****MARQUIE****` routine — blanks (`160` = `$A0`) with a colour ramp poked
    around the screen edge (`POKE T+54273, T-1023` along the top). It is a
    **chase**: the captured screen was one frame of it, and ours never moved.
    """
    from alien_remake.render.frontend import _welcome_border_colour
    from alien_remake.render.layout import _COLS

    # phase 0 still reproduces the live capture exactly (the drift guards above
    # depend on this).
    assert tuple(
        _welcome_border_colour(0, c) for c in range(_COLS)
    ) == _CAPTURED_TOP_ROW

    # ...and advancing the phase rotates the ramp rather than redrawing it.
    for phase in (1, 5, 15):
        rotated = tuple(_welcome_border_colour(0, c, phase) for c in range(_COLS))
        assert rotated != _CAPTURED_TOP_ROW
        assert rotated == tuple((v + phase) % 16 for v in _CAPTURED_TOP_ROW)
    # A full 16 steps returns to the start.
    assert tuple(
        _welcome_border_colour(0, c, 16) for c in range(_COLS)
    ) == _CAPTURED_TOP_ROW


def test_joystick_detection_is_rerunnable(renderer: PygameRenderer) -> None:
    """**P3-10.** Detection used to run once, at construction, in silence — so
    a stick plugged in later was never seen and the player had no way to know
    whether one had been found."""
    assert hasattr(renderer, "_open_joystick")
    renderer._open_joystick()          # must be safe to call again
    # With no device attached the keyboard scheme stays fully functional.
    assert renderer._joystick is None or renderer._joystick.get_init()


def test_front_end_screens_actually_animate_through_draw(
    renderer: PygameRenderer,
) -> None:
    """**P5-9 — the regression this catches is subtle and bit us twice.**

    The GREEN VALLEY spiral (D-104) and the WELCOME marquee (D-119) were both
    implemented *and unit-tested* while standing completely still in the game:
    `_frame_count` was incremented inside `render()`, which only runs on the
    play screen, and the existing tests set the counter by hand.

    So this drives `draw()` — the app loop's actual per-frame call — and
    asserts the pixels change. Testing a draw helper is not testing the loop.

    **Amended 2026-08-06, twice. D-127 said only the spiral animates** —
    `MARQUIE` has one caller and is never repainted, so it can't be a
    repeating chase. **D-143 corrects the conclusion drawn from that fact**:
    "never repainted" is not "instant" — live capture
    (`capture_welcome_buildup.py`) caught the border sweeping in and every
    text line visibly mid-growth (partial strings like "CHOOSOVE" and
    "COPYRIGHRESERVED"), confirming a real one-time build-up animation on
    WELCOME too, just one that never loops. Both screens must show motion
    over their first 30 frames now.
    """
    import hashlib

    from alien_remake.core.flow import GameFlow, Screen

    def _frames(screen: Screen) -> int:
        flow = GameFlow()
        flow.screen = screen
        seen = set()
        for _ in range(30):
            renderer.draw(flow)
            seen.add(
                hashlib.md5(
                    pygame.image.tostring(renderer._surface, "RGB")
                ).hexdigest()
            )
        return len(seen)

    # [C MENU1.prg 150/200/210] the spiral is a real animation.
    assert _frames(Screen.LOADING_MENU) > 1, "GREEN VALLEY spiral is frozen"
    # [C MENU1.prg 330-380 + 610-720, D-143] the border sweep + per-line
    # CENTER ROUTINE growth are real animations too — just one-shot, not a
    # repeating loop.
    assert _frames(Screen.WELCOME) > 1, "the WELCOME build-up is frozen"


def test_the_frame_counter_advances_on_every_screen(
    renderer: PygameRenderer,
) -> None:
    """The mechanism behind the above: `draw()` must tick the counter for all
    screens, not just the play path."""
    from alien_remake.core.flow import GameFlow, Screen

    for screen in (Screen.LOADING_MENU, Screen.NOTICE, Screen.WELCOME,
                   Screen.TITLE, Screen.GAME_SELECTION):
        flow = GameFlow()
        flow.screen = screen
        before = renderer._frame_count
        renderer.draw(flow)
        assert renderer._frame_count == before + 1, f"stalled on {screen.name}"


def test_green_valley_spiral_completes_before_the_screen_times_out(
    renderer: PygameRenderer,
) -> None:
    """**D-140.** "The GREEN VALLEY animation is extremely close, but cuts
    off early." `draw()` runs at the app's real 30 fps while the LOADING_MENU
    timeout is measured in flow ticks (`TICK_HZ` ~= 7.886) — a mismatch that,
    at the old `LOADING_MENU_TICKS`, moved the screen on partway through the
    spiral's outward sweep.

    Reproduces the actual `run_app` loop structure (draw every frame, tick
    only every `1/TICK_HZ`) with a virtual clock instead of real sleeps, and
    asserts the spiral reaches its final ring at least once before the
    screen transitions away.
    """
    from alien_remake.core import constants
    from alien_remake.core.flow import GameFlow, Screen
    from alien_remake.render.frontend import _SPIRAL_RATE, _SPIRAL_RINGS

    frame_hz = 30.0
    frame_period = 1.0 / frame_hz
    tick_period = 1.0 / constants.TICK_HZ

    flow = GameFlow(front_end=FrontEnd.CLASSIC)  # DISC-262: this asserts the original's full boot chain
    assert flow.screen is Screen.LOADING_MENU
    clock = 0.0
    last_tick = 0.0
    max_steps = 0
    for _ in range(10_000):
        if flow.screen is not Screen.LOADING_MENU:
            break
        if clock - last_tick >= tick_period:
            flow.tick()
            last_tick = clock
        renderer.draw(flow)
        steps = 1 + (renderer._frame_count // _SPIRAL_RATE) % len(_SPIRAL_RINGS)
        max_steps = max(max_steps, steps)
        clock += frame_period
    else:
        pytest.fail("LOADING_MENU never timed out")

    assert max_steps == len(_SPIRAL_RINGS), (
        f"spiral only reached ring {max_steps} of {len(_SPIRAL_RINGS)} "
        "before the screen moved on"
    )


def test_spiral_holds_on_the_finished_picture_instead_of_looping(
    renderer: PygameRenderer,
) -> None:
    """**[C MENU1.prg 200/210] D-142.** The BASIC sweeps the 22 rings exactly
    once (`FOR Q=11 TO 1 STEP -1` then `FOR Q=1 TO 11`, no repeat) and then
    holds while it prints the publisher name and runs its pause — it never
    restarts a second sweep. `_draw_loading_menu` must clamp at completion,
    not wrap via modulo, or the screen would visibly reset partway through
    its long (~14s) real lifetime.
    """
    from alien_remake.core.flow import GameFlow, Screen
    from alien_remake.render.frontend import SPIRAL_CELLS, text_reveal_steps
    from alien_remake.render.layout import (
        _BASIC_POKE_S,
        _FRAME_HZ,
        _TEXT_REVEAL_RATE,
    )

    flow = GameFlow()
    flow.screen = Screen.LOADING_MENU
    # DISC-207: the sweep is paced per POKE, not per ring.
    frames_to_finish = int(len(SPIRAL_CELLS) * _FRAME_HZ * _BASIC_POKE_S)
    # **D-143** — the spiral itself holds once done, but "GREEN VALLEY" then
    # "PUBLISHING" still grow in afterward (sequentially) before everything
    # is truly static; wait for both to finish too.
    # DISC-210: `300 B$="{05}GREEN VALLEY"` — the leading colour code counts
    # toward LEN, so that line runs 7 steps, not 6.
    text_frames = (
        text_reveal_steps("GREEN VALLEY") + text_reveal_steps("PUBLISHING ")
    ) * _TEXT_REVEAL_RATE
    settled = frames_to_finish + text_frames

    renderer._frame_count = settled
    renderer.draw(flow)
    last_frame = pygame.image.tobytes(renderer._surface, "RGB")

    # Long past completion — the picture must be identical, not reset.
    renderer._frame_count = settled * 5
    renderer.draw(flow)
    assert pygame.image.tobytes(renderer._surface, "RGB") == last_frame, (
        "the spiral must hold on the finished picture, not loop"
    )


# --- D-143: the CENTER ROUTINE text-growth reveal, live-confirmed ------------

def test_text_reveal_mask_matches_the_center_routine_algorithm() -> None:
    """**[C MENU1.prg 2040-2060]** `LEFT$(B$,N)+RIGHT$(B$,N)` at each N —
    pin the exact sequence for a known string so the growth shape can't
    silently drift (e.g. reversed, off-by-one, or growing from the wrong end).
    """
    from alien_remake.render.frontend import text_reveal_mask, text_reveal_steps

    text = "PUBLISHING"  # 10 chars, even -> steps = 5
    assert text_reveal_steps(text) == 5
    assert text_reveal_mask(text, 0) == "          "
    assert text_reveal_mask(text, 1) == "P        G"
    assert text_reveal_mask(text, 2) == "PU      NG"
    assert text_reveal_mask(text, 5) == "PUBLISHING"
    # Past completion clamps rather than raising or corrupting.
    assert text_reveal_mask(text, 99) == "PUBLISHING"
    assert text_reveal_mask(text, -1) == "          "


def test_text_reveal_mask_odd_length() -> None:
    from alien_remake.render.frontend import text_reveal_mask, text_reveal_steps

    text = "ALIEN"  # 5 chars, odd -> ceil(5/2) = 3 steps
    assert text_reveal_steps(text) == 3
    assert text_reveal_mask(text, 1) == "A   N"
    assert text_reveal_mask(text, 2) == "AL EN"
    assert text_reveal_mask(text, 3) == "ALIEN"


def test_sequential_reveal_completes_one_line_before_the_next_starts() -> None:
    """**[C]** The BASIC's own sequencing: each GOSUB390 call runs to
    completion before the next PRINT/GOSUB statement executes — never two
    lines growing at once, matching the live capture's strict top-to-bottom
    order (row 3, then 6, then 8, then 12...).
    """
    from alien_remake.render.frontend import sequential_reveal_n, text_reveal_steps
    from alien_remake.render.layout import _TEXT_REVEAL_RATE

    lines = ("AB", "WXYZ")  # steps: 1, 2
    # Before anything: both zero.
    assert sequential_reveal_n(0, lines) == [0, 0]
    # Mid-way through line 1 only.
    assert sequential_reveal_n(_TEXT_REVEAL_RATE - 1, lines) == [0, 0]
    # Line 1 exactly finishes; line 2 has not started.
    n1 = text_reveal_steps("AB")
    assert sequential_reveal_n(n1 * _TEXT_REVEAL_RATE, lines) == [1, 0]
    # One frame into line 2.
    assert sequential_reveal_n(n1 * _TEXT_REVEAL_RATE + 1, lines)[0] == 1
    assert sequential_reveal_n(n1 * _TEXT_REVEAL_RATE + 1, lines)[1] >= 0
    # Both fully done well past the total budget.
    n2 = text_reveal_steps("WXYZ")
    total = (n1 + n2) * _TEXT_REVEAL_RATE
    assert sequential_reveal_n(total * 10, lines) == [1, n2]


def test_welcome_lines_reveal_top_to_bottom_through_real_draw_calls(
    renderer: PygameRenderer,
) -> None:
    """**D-143, live-confirmed** (`capture_welcome_buildup.py`): rows appear
    strictly in top-to-bottom order — row 6 ("WELCOME TO ALIEN") must not
    show before row 3 ("GREEN VALLEY PUBLISHING") has already appeared, etc.
    Driven through real `draw()` calls, not the model function directly.
    """
    from alien_remake.core.flow import GameFlow, Screen

    flow = GameFlow()
    flow.screen = Screen.WELCOME

    def row_has_ink(row: int) -> bool:
        s = 1  # DISC-242: the draw surface is native
        surf = renderer._surface
        y = row * 8 * s + 4 * s
        black = c64.rgb(c64.BLACK)
        return any(
            tuple(surf.get_at((x, y)))[:3] != black
            for x in range(0, surf.get_width(), 2)
        )

    first_seen: dict[int, int] = {}
    rows_of_interest = (3, 6, 8, 20, 21, 23)
    for frame in range(400):
        renderer.draw(flow)
        for row in rows_of_interest:
            if row not in first_seen and row_has_ink(row):
                first_seen[row] = frame

    assert set(first_seen) == set(rows_of_interest), (
        f"not all rows ever appeared: {first_seen}"
    )
    ordered = [first_seen[r] for r in rows_of_interest]
    assert ordered == sorted(ordered), (
        f"rows did not appear top-to-bottom: {first_seen}"
    )


def test_welcome_menu_items_never_appear_partially_grown(
    renderer: PygameRenderer,
) -> None:
    """**[C MENU1.prg 670-690]** "1) ALIEN"/"Q QUIT" print via `PRINTTAB` —
    instant, never the CENTER ROUTINE — so once visible they must be whole,
    never caught as a partial string the way "CHOOSOVE" was live-captured
    for a GOSUB390 line.
    """
    from alien_remake.core.flow import GameFlow, Screen

    flow = GameFlow()
    flow.screen = Screen.WELCOME

    def label_region():
        # Columns 14-21 of row 12 covers the key cell + "ALIEN" (D-064).
        s = 1  # DISC-242: the draw surface is native
        x0, y0 = 14 * 8 * s, 12 * 8 * s
        w, h = 8 * 8 * s, 8 * s
        return renderer._surface.subsurface((x0, y0, w, h)).copy()

    def region_bytes(surf) -> bytes:
        return pygame.image.tobytes(surf, "RGB")

    # A fully-settled reference, far past every line's budget.
    for _ in range(600):
        renderer.draw(flow)
    settled = region_bytes(label_region())
    black_row = region_bytes(pygame.Surface(label_region().get_size()))

    # Replay from a fresh renderer and find the first frame this region is
    # not all-black; it must ALREADY match the settled reference exactly —
    # a genuine growth animation would show intermediate states in between.
    renderer._welcome_entered_frame = None
    renderer._frame_count = 0
    flow2 = GameFlow()
    flow2.screen = Screen.WELCOME
    seen_full = False
    for _ in range(600):
        renderer.draw(flow2)
        current = region_bytes(label_region())
        if current != black_row:
            assert current == settled, (
                "the ALIEN/key region appeared in a state that isn't its "
                "final form -- it should be an instant PRINTTAB, not a "
                "growth animation"
            )
            seen_full = True
            break
    assert seen_full, "the ALIEN label never appeared at all"


# --- D-145: the opening death notice's real colours + name truncation --------

def test_opening_notice_is_black_on_green_like_the_selection_screen(
    renderer: PygameRenderer,
) -> None:
    """**[C-live] D-145.** `game_init_mode` clears the screen to `$A0` but
    never touches colour RAM, which `sub_screen_setup ($5FC3)` left at 5
    (GREEN) — so the notice sits on a full-green field with black `$D021`
    ink, and a black border. Confirmed frame-by-frame in the player's own
    recording. This used to be white text on black.
    """
    from alien_remake.core.flow import GameFlow, InputEvent, Screen

    flow = GameFlow()
    for _ in range(3000):
        if flow.screen is Screen.NOTICE:
            flow.handle(InputEvent.FIRE)
        elif flow.screen is Screen.WELCOME:
            flow.handle(InputEvent.SELECT_FULL)
        elif flow.screen is Screen.INSTRUCTIONS:
            flow.handle(InputEvent.NO)
        elif flow.screen is Screen.GAME_SELECTION:
            flow.handle(InputEvent.SELECT_FULL)
        elif flow.screen is Screen.OPENING:
            break
        flow.tick()
    assert flow.screen is Screen.OPENING
    renderer.draw(flow)

    green = c64.rgb(c64.GREEN)
    surf = renderer._surface
    # The field is overwhelmingly green...
    seen = [
        tuple(surf.get_at((x, y)))[:3]
        for x in range(0, surf.get_width(), 7)
        for y in range(0, surf.get_height(), 7)
    ]
    assert seen.count(green) > 0.8 * len(seen), "the notice screen should be green"
    # ...and the border black, not the play screen's blue.
    assert tuple(renderer._window.get_at((2, 2)))[:3] == c64.rgb(c64.BLACK)


def test_opening_notice_message_is_not_overprinted_by_the_garbled_name(
    renderer: PygameRenderer,
) -> None:
    """**D-145.** `$50A0`'s message write physically overwrites the name's
    last two cells in screen RAM, so only 8 garbled characters survive. Our
    `_blit_cells` skips spaces (drawing no paper), so drawing all 10 left two
    garbled glyphs sitting *under* "HAS" — the "too much of the corrupt name
    overlapping the words" the player reported. The message's own columns
    must carry only message ink.
    """
    from alien_remake.render.frontend import (
        _OPENING_MSG_COL,
        _OPENING_MSG_ROW,
        _OPENING_NAME_COL,
    )

    visible = _OPENING_MSG_COL - _OPENING_NAME_COL
    assert visible == 8, "the ROM's own geometry: 8 name cells survive"

    # Render the notice twice: once with a real garbled name, once with the
    # name suppressed. The message's own columns must look identical, i.e.
    # no name ink bleeds into them.
    from alien_remake.core.flow import GameFlow, InputEvent, Screen

    flow = GameFlow()
    for _ in range(3000):
        if flow.screen is Screen.NOTICE:
            flow.handle(InputEvent.FIRE)
        elif flow.screen is Screen.WELCOME:
            flow.handle(InputEvent.SELECT_FULL)
        elif flow.screen is Screen.INSTRUCTIONS:
            flow.handle(InputEvent.NO)
        elif flow.screen is Screen.GAME_SELECTION:
            flow.handle(InputEvent.SELECT_FULL)
        elif flow.screen is Screen.OPENING:
            break
        flow.tick()
    renderer.draw(flow)

    s = 1  # DISC-242: the draw surface is native
    y0 = _OPENING_MSG_ROW * 8 * s
    msg_x0 = _OPENING_MSG_COL * 8 * s
    with_name = renderer._surface.subsurface(
        (msg_x0, y0, 28 * 8 * s, 8 * s)
    ).copy()

    assert flow.sim is not None
    flow.sim.state.opening_dead_crew_id = None    # no name drawn at all
    renderer.draw(flow)
    without_name = renderer._surface.subsurface(
        (msg_x0, y0, 28 * 8 * s, 8 * s)
    ).copy()

    assert pygame.image.tobytes(with_name, "RGB") == pygame.image.tobytes(
        without_name, "RGB"
    ), "garbled name ink is bleeding into the message's columns"


def test_the_exit_advert_actually_renders(renderer: PygameRenderer) -> None:
    """**[C EXITO.prg] D-175, PV-01 — the screen, not just the transition.**

    A flow test proves `Q` reaches EXIT_ADVERT; it does not prove anything is
    drawn. This one runs the reveal out and checks the three colour bands the
    BASIC specifies actually appear: RED text (lines 410-430, `{28}`), the
    WHITE **ONE-STEP** logo (450-480, `{5}`) and the BLUE **DEALER** logo
    (490-520, `{31}`), inside the MARQUIE border.

    It exists because the first cut of this screen passed its flow test while
    rendering **solid black** — three separate faults (a dispatch branch that
    never landed, ALIEN's cut-out charset used where the loader's chargen ROM
    belongs, and an entered-frame reset that fired every frame so the reveal
    never advanced). Testing a transition is not testing a screen.
    """
    from alien_remake.core.flow import GameFlow, Screen as _S

    flow = GameFlow()
    flow.screen = _S.EXIT_ADVERT
    for _ in range(300):
        renderer.draw(flow)

    seen = {
        tuple(renderer._surface.get_at((x, y)))[:3]
        for y in range(0, renderer._surface.get_height(), 2)
        for x in range(0, renderer._surface.get_width(), 2)
    }
    assert c64.rgb(c64.RED) in seen, "the three advert lines are missing"
    assert c64.rgb(c64.WHITE) in seen, "the ONE-STEP logo is missing"
    assert c64.rgb(c64.BLUE) in seen, "the DEALER logo is missing"
    # ...and the text really is text, on its own rows (5/7/9 of a 25-row grid).
    s = 1  # DISC-242: the draw surface is native
    for row in (5, 7, 9):
        band = {
            tuple(renderer._surface.get_at((x, row * 8 * s + 6)))[:3]
            for x in range(0, renderer._surface.get_width(), 2)
        }
        assert c64.rgb(c64.RED) in band, f"row {row} carries no advert text"


def test_the_short_scenario_intro_screens_render(renderer: PygameRenderer) -> None:
    """**[C $4405/$4327] D-176, PV-38** — the two screens FULL never shows.

    `game_init_mode ($4317)` branches on the mode in `$4303`: FULL returns
    immediately, SHORT goes to `$4405` and asks "DO YOU WANT AN INTRODUCTION".
    Y then runs the DECK PLAN KEY + SOUND LEGEND.

    The load-bearing detail is the **varying slot**: `$44D6` (the heartbeat)
    and each of `$4500`/`$4554`/`$452A` are copied to the *same* address,
    `$061D` = row 13 col 21, so exactly one is on screen at a time and it
    composes with the fixed prefix at `$0608` into a sentence — "THIS IS THE
    SOUND OF" + "A GRILLE BEING REMOVED.". Laying them out as separate centred
    lines (the first cut) both truncated off the right edge and lost the
    sentence.
    """
    from alien_remake.core.flow import GameFlow, Screen as _S

    flow = GameFlow()
    flow.screen = _S.INTRO_PROMPT
    renderer.draw(flow)
    s = 1  # DISC-242: the draw surface is native
    for row in (0, 1):                       # $443C -> $0400, $4457 -> $0456
        band = {
            tuple(renderer._surface.get_at((x, row * 8 * s + 6)))[:3]
            for x in range(0, renderer._surface.get_width(), 2)
        }
        assert c64.rgb(c64.LIGHT_BLUE) in band, f"prompt row {row} is empty"

    flow.screen = _S.INTRO_LEGEND
    for _ in range(400):
        renderer.draw(flow)
    seen = {
        tuple(renderer._surface.get_at((x, y)))[:3]
        for y in range(0, renderer._surface.get_height(), 2)
        for x in range(0, renderer._surface.get_width(), 2)
    }
    assert c64.rgb(c64.LIGHT_BLUE) in seen, "the deck-plan key is missing"
    assert c64.rgb(c64.WHITE) in seen, "the varying sound slot is missing"

    # The wrap onto row 14 only happens while the slot holds a string longer
    # than the 19 columns left on row 13 - the 42-char heartbeat line does,
    # "THE TRACKER ALARM." (18) does not. So check it at the opening stage,
    # which is where the ROM's own field is widest.
    fresh = GameFlow()
    fresh.screen = _S.INTRO_LEGEND
    renderer._legend_entered_frame = None
    renderer.draw(fresh)
    for row in (13, 14):
        band = {
            tuple(renderer._surface.get_at((x, row * 8 * s + 6)))[:3]
            for x in range(0, renderer._surface.get_width(), 2)
        }
        assert len(band) > 1, f"row {row} of the heartbeat line is blank"


def test_the_notice_sprite_registers_come_from_menu1s_basic() -> None:
    """**PV-32 (NOTICE half) / D-180** — computed, not captured.

    The register asked for a live capture of "the NOTICE screen's own sprite
    registers". They are never written by `ALIEN.prg` at all: this is MENU1's
    screen, and its BASIC works them out in the open —

        556   CO = 33 : RO = 18 : CL = 1 : GOSUB 3000
        3025  CO = (CO*8)+18            -> 282, so the X MSB is set
        3026/3030  POKE 53264,msb : POKE 53248,X-256 : POKE 53249,(RO*8)+40
        3020  POKE 53287,CL             -> sprite 0 colour
        3030  POKE 2040,13              -> data at 13*64 = $0340

    so X = 282, Y = 184, colour 1 (white), pointer 13. Arithmetic in a listing
    we already have — no oracle needed.
    """
    CO, RO, CL = 33, 18, 1
    x = CO * 8 + 18
    msb, x_lo = (1, x - 256) if x > 255 else (0, x)
    assert (x, msb, x_lo) == (282, 1, 26)
    assert RO * 8 + 40 == 184
    assert CL == 1
    assert 13 * 64 == 0x0340


def test_instruction_screen_colours_come_from_menu1s_own_control_codes() -> None:
    """**PV-32 (header shade) / D-182** — stated in the BASIC, never a guess.

    R-36 hedged on "the exact shade of the spaced A L I E N header", and the
    register carried it as needing a live capture. It is in the listing:

        10006  PRINTTAB(15)"{28}{17}A L I E N"      -> CHR$(28) = RED
        10010  PRINT...TAB(7)"{158}DO YOU WANT..."  -> CHR$(158) = YELLOW

    So `c64.RED` and `c64.YELLOW` are the ROM's own choices.
    """
    from pathlib import Path

    listing = Path("out/MENU1_EXITO.bas.txt")
    if not listing.exists():
        pytest.skip("MENU1 listing not extracted")
    text = listing.read_text(encoding="utf-8", errors="replace")
    assert '10006 PRINTTAB(15)"{28}{17}A L I E N"' in text
    assert '{158}DO YOU WANT INSTRUCTIONS?' in text


def test_the_logo_rows_share_one_column_via_the_center_routine() -> None:
    """**D-185** — the four rows of each logo word must start in one column.

    They are horizontal slices of the same block-graphic glyphs. Centring each
    on its own length put row 0 one column right of the rest and sheared the
    letter tops off — which the player saw as "split in half and formatted
    strangely", and which a glance at a render missed because the word was
    still readable.

    EXITO's CENTER ROUTINE supplies the column (`2010 M=LEN(B$)`, pad odd,
    `2050 PRINT SPC(21-N)` with `N=M/2` → start at `21 - M/2`), and the reason
    the rows agree is that each word's **first** line carries a leading colour
    code (`{5}` on line 450, `{31}` on 490) that counts toward `LEN` but prints
    no column. The control character is load-bearing for the layout.
    """
    from alien_remake.render.frontend import (
        _EXIT_LOGO_BOTTOM,
        _EXIT_LOGO_TOP,
        _center_routine_col,
    )

    for rows, expected in ((_EXIT_LOGO_TOP, 3), (_EXIT_LOGO_BOTTOM, 6)):
        cols = [
            _center_routine_col(r, colour_code=(k == 0))
            for k, r in enumerate(rows)
        ]
        assert len(set(cols)) == 1, f"rows must align, got {cols}"
        assert cols[0] == expected

    # The regression, precisely: the colour code only moves a row whose length
    # is **even**, because `2020`'s odd-length padding already absorbs it
    # otherwise. ONE-STEP's first row is 34 (even) and drifts to column 4
    # without it; DEALER's is 29 (odd) and lands on 6 either way. So the bug
    # showed on one word and not the other, which is exactly how it read as
    # "split in half".
    assert len(_EXIT_LOGO_TOP[0]) % 2 == 0
    assert _center_routine_col(_EXIT_LOGO_TOP[0]) == 4          # the old, wrong column
    assert _center_routine_col(_EXIT_LOGO_TOP[0], colour_code=True) == 3
    assert len(_EXIT_LOGO_BOTTOM[0]) % 2 == 1
    assert _center_routine_col(_EXIT_LOGO_BOTTOM[0]) == 6       # unaffected


# --- the loader's spiral + CENTER ROUTINE, from MENU1.prg's BASIC (DISC-207) --

def test_the_spiral_pokes_one_cell_at_a_time_out_then_back() -> None:
    """BASIC lines 200-280 draw the spiral cell by cell, not ring by ring.

        200 FORQ=11TO1STEP-1:GOSUB220:NEXT   ; grow  innermost -> largest
        210 FORQ=1TO11:GOSUB220:NEXT         ; shrink largest  -> back to start
        240/250/260/270                      ; top, right, bottom, left = clockwise

    The independent check on the cell count: at `_BASIC_POKE_S` (6.10 ms,
    measured live) the sweep takes **11.0 s** — which is the figure that
    measurement was derived from in the first place. Counting the POKEs out of
    the listing and timing the animation on the real machine agree.
    """
    from alien_remake.render.frontend import SPIRAL_CELLS
    from alien_remake.render.layout import _BASIC_POKE_S

    assert len(SPIRAL_CELLS) == 1804
    assert len(SPIRAL_CELLS) * _BASIC_POKE_S == pytest.approx(11.0, abs=0.05)

    # It starts on the innermost ring and its first edge runs left -> right.
    first_rows = {r for r, _, _ in SPIRAL_CELLS[:6]}
    assert first_rows == {11}, "the first ring drawn is the innermost (Q=11)"
    assert [c for _, c, _ in SPIRAL_CELLS[:4]] == [12, 13, 14, 15]

    # The widest ring is reached in the middle of the sweep, not at the end.
    widest = max(range(len(SPIRAL_CELLS)), key=lambda i: SPIRAL_CELLS[i][1])
    assert 0.3 < widest / len(SPIRAL_CELLS) < 0.7, (
        "the largest rectangle should be the turning point, with the sweep "
        "coming back down afterwards"
    )


def test_the_name_grows_outward_from_its_centre() -> None:
    """`440 PRINTSPC(21-N)LEFT$(B$,N);RIGHT$(B$,N)` — the two halves are printed
    **adjacent**, so the first and last letters appear together in the middle
    and are pushed apart as more arrive.

    The previous model blanked the middle of a fixed-width string, which put
    every letter straight into its final position and merely filled the gap.
    Nothing moved, which is a visibly different animation.
    """
    from alien_remake.render.frontend import center_routine_step

    assert center_routine_step("GREEN VALLEY", 1) == ("GY", 20)
    assert center_routine_step("GREEN VALLEY", 2) == ("GREY", 19)
    assert center_routine_step("GREEN VALLEY", 6) == ("GREEN VALLEY", 15)

    # Odd lengths get the BASIC's pad at line 410 before halving.
    shown, col = center_routine_step("PUBLISHING ", 1)
    assert len(shown) == 2 and col == 20

    # Every step is centred on the same column pair as the finished word.
    for n in range(1, 7):
        shown, col = center_routine_step("GREEN VALLEY", n)
        assert col + len(shown) / 2 == pytest.approx(21.0)


def test_a_leading_colour_code_shifts_the_centre_routine(  # DISC-210
) -> None:
    """`300 B$="{05}GREEN VALLEY"` — the colour code costs a `LEN` slot but no
    column.

    Line 400 measures `LEN(B$)` including the `CHR$(5)`, so a 12-character name
    behaves as 13: line 410 pads it to 14, the loop runs **7** steps rather than
    6, and `SPC(21-N)` lands the text at column **14**. Line 310's
    `B$="PUBLISHING "` has no colour code and stays at column 15 with 6 steps —
    the two lines are genuinely a column apart on the real screen.

    Getting this wrong put the publisher's name one cell right of where the
    loader puts it, which also squeezed the gap before the ™ sprite.
    """
    from alien_remake.render.frontend import center_routine_step

    assert center_routine_step("GREEN VALLEY", 7, colour_code=True) == (
        "GREEN VALLEY ", 14
    )
    assert center_routine_step("PUBLISHING ", 6) == ("PUBLISHING  ", 15)

    # The first step is the colour code plus the pad: nothing visible yet.
    shown, _ = center_routine_step("GREEN VALLEY", 1, colour_code=True)
    assert shown.strip() == ""


def test_the_welcome_screen_reveals_in_the_basics_order() -> None:  # DISC-209
    """Lines 610-720 reveal nine things in a fixed order, all via `GOSUB 390`.

    Box top rule, publisher name, box bottom rule, WELCOME TO ALIEN, FACE THE
    POWER OF THE UNKNOWN, its underline, then the two footer lines and the
    copyright. `1 ALIEN`/`Q QUIT` are `PRINT`ed whole by lines 670-690 and do
    not grow at all.

    The rules and the underline used to appear instantly, and the text used the
    fixed-position mask, so nothing on this screen actually moved.
    """
    from alien_remake.render.frontend import (
        _BORDER_REVEAL_RATE,
        _BORDER_REVEAL_TOTAL_STEPS,
        sequential_reveal_n,
        text_reveal_steps,
    )

    lines = (
        "X" * 35, "GREEN VALLEY PUBLISHING", "X" * 33, "WELCOME TO ALIEN",
        "FACE THE POWER OF THE UNKNOWN", "X" * 29, "CHOOSE ONE OF THE ABOVE",
        "PLEASE LEAVE DISKETTE IN DRIVE", "COPYRIGHT(C)1985 ALL RIGHTS RESERVED",
    )
    border = int(_BORDER_REVEAL_TOTAL_STEPS / _BORDER_REVEAL_RATE)

    finished_at: list[int] = []
    for i, line in enumerate(lines):
        frame = 0
        while frame < 5000:
            if sequential_reveal_n(frame, lines)[i] >= text_reveal_steps(line):
                finished_at.append(frame + border)
                break
            frame += 1
        else:  # pragma: no cover
            raise AssertionError(f"{line!r} never completed")

    assert finished_at == sorted(finished_at), (
        f"the nine reveals must complete in the BASIC's order: {finished_at}"
    )
    assert finished_at[0] > border, "the outer border sweeps in first"
