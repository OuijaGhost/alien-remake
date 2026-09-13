"""Headless tests for the pygame backend: input classification + text layout
(FV-1c2/FV-1c2b).

Runs pygame under SDL's dummy video/audio drivers (no real window/sound device
needed): injects synthetic ``KEYDOWN`` events via ``pygame.event.post`` to
exercise :meth:`PygameRenderer.poll_input`, and inspects rendered pixels to
check text-layout geometry — without a live display. This is the first test
coverage `render/pygame_app.py` has had; it establishes the pattern FV-1c2's
broader render audit can reuse.
"""

from __future__ import annotations

import os

import pytest

pygame = pytest.importorskip("pygame")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from alien_remake.core.flow import InputEvent, Screen  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


@pytest.fixture
def renderer() -> PygameRenderer:
    r = PygameRenderer()
    yield r
    pygame.quit()


def _inject(key: int, mod: int = 0) -> None:
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, mod=mod))


def test_bare_1_2_on_selection_are_rejected_under_the_classic_front_end() -> None:
    """**[C R-32/D-018]** `$5F36` polls for the Ctrl+1/Ctrl+2 chord specifically.

    FV-1c1 found this unenforced and FV-1c2 fixed it. It stays enforced under
    CLASSIC, which prints "CONTROL:1"; the quick front end prints "PRESS 1" and
    takes the bare key, so the two always agree with what is on screen
    (DISC-263).
    """
    import pygame

    from alien_remake.core.flow import InputEvent, Screen
    from alien_remake.core.modes import FrontEnd
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(scale=2, tiles=None, intro_wav=None,
                       front_end=FrontEnd.CLASSIC)
    try:
        for key in (pygame.K_1, pygame.K_2):
            pygame.event.clear()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": key, "mod": 0}))
            events = r.poll_input(Screen.GAME_SELECTION)
            assert InputEvent.SELECT_FULL not in events
            assert InputEvent.SELECT_SHORT not in events

            pygame.event.clear()
            pygame.event.post(pygame.event.Event(
                pygame.KEYDOWN, {"key": key, "mod": pygame.KMOD_LCTRL}))
            events = r.poll_input(Screen.GAME_SELECTION)
            assert events, f"Ctrl+{key} produced nothing under CLASSIC"
    finally:
        r.close()


def test_the_quick_front_end_takes_bare_1_and_2() -> None:
    """"PRESS 1" has to mean press 1 (DISC-263)."""
    import pygame

    from alien_remake.core.flow import InputEvent, Screen
    from alien_remake.core.modes import FrontEnd
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(scale=2, tiles=None, intro_wav=None,
                       front_end=FrontEnd.QUICK)
    try:
        for key, expected in ((pygame.K_1, InputEvent.SELECT_FULL),
                              (pygame.K_2, InputEvent.SELECT_SHORT)):
            pygame.event.clear()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": key, "mod": 0}))
            assert expected in r.poll_input(Screen.GAME_SELECTION)
    finally:
        r.close()


def test_developer_mode_is_a_setting_not_a_key_chord() -> None:
    """It used to be `0` and Ctrl+3 on the selection screen (DISC-263/245).

    Both are gone: undiscoverable unless you already knew, and unreachable on a
    machine with no keyboard — the same gap the options screen closes. The keys
    must now do nothing, and `set_developer` must be the only way in.
    """
    import pygame

    from alien_remake.core.flow import Screen
    from alien_remake.core.modes import FrontEnd
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(scale=2, tiles=None, intro_wav=None,
                       front_end=FrontEnd.QUICK)
    try:
        assert r._debug_markers is False
        for key, mod in ((pygame.K_0, 0), (pygame.K_3, pygame.KMOD_LCTRL)):
            pygame.event.clear()
            pygame.event.post(pygame.event.Event(
                pygame.KEYDOWN, {"key": key, "mod": mod}))
            r.poll_input(Screen.GAME_SELECTION)
            assert r._debug_markers is False, "the old chord still toggles"

        r.set_developer(True)
        assert r._debug_markers is True
        r.set_developer(False)
        assert r._debug_markers is False
    finally:
        r.close()


def test_ctrl_1_and_ctrl_2_select_on_selection(renderer: PygameRenderer) -> None:
    _inject(pygame.K_1, mod=pygame.KMOD_LCTRL)
    assert renderer.poll_input(Screen.GAME_SELECTION) == [InputEvent.SELECT_FULL]
    _inject(pygame.K_2, mod=pygame.KMOD_RCTRL)
    assert renderer.poll_input(Screen.GAME_SELECTION) == [InputEvent.SELECT_SHORT]


def test_bare_1_still_works_on_welcome(renderer: PygameRenderer) -> None:
    """WELCOME's real prompt is the genuinely-bare "1 ALIEN" / "Q QUIT" — must
    stay unmodified by the GAME_SELECTION-only Ctrl check."""
    _inject(pygame.K_1, mod=0)
    assert renderer.poll_input(Screen.WELCOME) == [InputEvent.SELECT_FULL]


def test_escape_on_the_play_screen_is_the_panels_quit_row() -> None:
    """**DISC-262** — Escape does what choosing "back" in the PCS menu does
    (labelled "quit" in the decoded ROM, `[C $A715]`; shown as "back" since
    2026-09-05 — see `core/menu.py`'s own comment on why).

    That row is `back=True`: it leaves a crew member's order list and returns to
    the CONTROL list. So Escape is an undo for "I opened the wrong menu", not an
    exit. It went through two earlier meanings — closing the program (harsh
    enough that a mis-hit lost the pass) and abandoning to the front end
    (still too much while you are mid-order).
    """
    import random

    import pygame

    from alien_remake.core.flow import Screen
    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(scale=2, tiles=None, intro_wav=None)
    try:
        sim = Simulation(rng=random.Random(0))
        r._sim, r._ship = sim, sim.ship
        r._menu = MenuController(sim)
        crew = next(c for c in sim.state.crew.values() if c.alive)
        r._menu.selected_crew = crew.id
        assert r._menu.selected_crew is not None

        pygame.event.clear()
        pygame.event.post(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0})
        )
        r._quit = False
        r.poll_input(Screen.PLAYING)

        assert r._quit is False, "Escape closed the program from the play screen"
        assert r._menu.selected_crew is None, (
            "Escape did not back out of the crew's order list"
        )
    finally:
        r.close()


def test_firing_the_skip_turn_row_reaches_poll_skip_turn() -> None:
    """**Not the original** (2026-09-05). The "Skip turn" CONTROL-panel row
    (`MenuController.entries()`, turns_on-gated) and the `K` key both end up
    read by `poll_skip_turn()` — this pins the menu path end to end."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(scale=2, tiles=None, intro_wav=None)
    try:
        sim = Simulation(rng=random.Random(0))
        r._sim, r._ship = sim, sim.ship
        r._menu = MenuController(sim)
        r._menu.turns_on = True
        crew = next(c for c in sim.state.crew.values() if c.alive)
        r._menu.selected_crew = crew.id

        entries = r._menu.entries()
        skip_index = next(i for i, e in enumerate(entries) if e.skip_turn)
        selectable = [i for i, e in enumerate(entries) if e.selectable]
        r._menu.cursor = selectable.index(skip_index)
        r._menu.fire()

        assert r.poll_skip_turn() is True
        assert r.poll_skip_turn() is False, "the flag must clear after reading"
    finally:
        r.close()


def test_escape_off_the_play_screen_abandons_without_quitting() -> None:
    """There is no panel to back out of, so it returns to the front end."""
    import pygame

    from alien_remake.core.flow import InputEvent, Screen
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(scale=2, tiles=None, intro_wav=None)
    try:
        for screen in (Screen.GAME_SELECTION, Screen.INSTRUCTIONS):
            pygame.event.clear()
            pygame.event.post(
                pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0})
            )
            r._quit = False
            events = r.poll_input(screen)
            assert InputEvent.ABANDON in events, f"{screen.name}: no back-out"
            assert InputEvent.QUIT not in events
            assert r._quit is False, f"{screen.name}: Escape closed the program"
    finally:
        r.close()


def test_abandoning_returns_the_flow_to_its_front_ends_home() -> None:
    """`home` depends on the front end (DISC-262).

    Quick has no WELCOME screen, so backing out there would strand the player on
    a screen its boot chain never shows. It goes to the selection instead.
    """
    from alien_remake.core.flow import GameFlow, InputEvent, Screen
    from alien_remake.core.modes import FrontEnd

    for front_end, home in (
        (FrontEnd.QUICK, Screen.GAME_SELECTION),
        (FrontEnd.CLASSIC, Screen.WELCOME),
    ):
        flow = GameFlow(front_end=front_end)
        flow.screen = Screen.GAME_SELECTION
        flow.handle(InputEvent.SELECT_FULL)
        assert flow.sim is not None

        flow.handle(InputEvent.ABANDON)
        assert flow.screen is home, f"{front_end.value}: went to {flow.screen.name}"
        assert flow.sim is None, "the abandoned game is still attached"
        assert not flow.finished, "backing out must not end the program"
        assert flow.abandon() is False, "nothing left to abandon at home"

def _leftmost_lit_column(
    surface: "pygame.Surface", y_top: int, height: int, background: tuple
) -> int:
    """The first x (scanning left to right) lit (!= ``background``) anywhere in
    the row band ``[y_top, y_top + height)`` — robust to font baseline/padding
    quirks that make a single fixed row unreliable."""
    for x in range(surface.get_width()):
        for y in range(y_top, y_top + height):
            if tuple(surface.get_at((x, y)))[:3] != background:
                return x
    raise AssertionError(f"rows {y_top}..{y_top + height} are entirely background")


def test_the_notice_screen_is_laid_out_from_menu1s_own_basic() -> None:
    """The back-up notice, at MENU1's coordinates rather than a flow layout.

    **[C MENU1.prg 505-565]** Each `PRINT` opens with two cursor-downs, so the
    rows step by three from row 2, and each line carries its own indent. The
    block is deliberately ragged; a shared paragraph helper used to left-align
    all seven at one x, on the strength of a "clean left-flush block" reading of
    a live capture. `out/vice_shots/boot_015_notice.png` shows the ragged
    indents plainly — "in a safe place." sits four columns in from its
    neighbours — so that reading was simply wrong.

    The trademark is sprite 0 (`556 CO=33:RO=18:CL=1:GOSUB3000`), positioned by
    the subroutine's own arithmetic, not by where a line of text happens to end.
    """
    from alien_remake.render.frontend import FrontEndMixin as FrontEnd

    rows = [row for row, _, _ in FrontEnd._NOTICE_LINES]
    assert rows == [2, 5, 8, 11, 14, 17, 20], "two cursor-downs plus a newline"
    cols = [col for _, col, _ in FrontEnd._NOTICE_LINES]
    assert cols == [9, 7, 8, 8, 13, 9, 7]
    assert len(set(cols)) > 1, "the block is ragged, not flush"

    # GOSUB 3000: CO=(CO*8)+18, (RO*8)+40, less the (24, 50) sprite origin.
    assert FrontEnd._NOTICE_TM_POS == (282 - 24, 184 - 50)
    # The same arithmetic must reproduce the two other GOSUB 3000 call sites,
    # whose positions were read off the running disk (D-064).
    from alien_remake.render.frontend import (
        _GREEN_VALLEY_TM_POS, _WELCOME_TM_POS,
    )
    assert (27 * 8 + 18 - 24, 14 * 8 + 40 - 50) == _GREEN_VALLEY_TM_POS  # 311
    assert (32 * 8 + 18 - 24, 4 * 8 + 40 - 50) == _WELCOME_TM_POS        # 621


# --- R-01: real-charset text rendering ---------------------------------------


@pytest.fixture
def renderer_with_tiles() -> PygameRenderer:
    """A renderer with the game's own extracted charset loaded, so
    `_render_c64_text`'s real path (not the None/no-tiles fallback) runs."""
    from pathlib import Path

    from alien_remake.render.tiles import load

    charset_path = Path("out") / "charset.bin"
    if not charset_path.exists():
        pytest.skip("out/charset.bin not present (run `alientools chars` first)")
    tiles = load(charset_path)
    r = PygameRenderer(tiles=tiles)
    yield r
    pygame.quit()


def test_render_c64_text_confirmed_string_returns_a_surface(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """R-01: every character of "Dallas Kane" is in the confirmed mapping
    (lower/upper a-z + space) — real-charset rendering must actually fire,
    not silently fall back."""
    from alien_remake.render import c64

    surf = renderer_with_tiles._render_c64_text("Dallas Kane", c64.rgb(c64.WHITE))
    assert surf is not None
    assert surf.get_width() == len("Dallas Kane") * 8  # unscaled, 8px/cell


def test_render_c64_text_paints_the_letter_shape_not_its_complement(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """**DISC-225.** `fg` must land on the glyph's 0-bits (the letter), not
    the 1-bits (the paper-shaped majority) — verified against a real capture:
    rendering `docs/reference/narcissus_0400.bin` row 19 both ways and
    comparing to `_screen_char`'s already-correct decode shows the 0-bit
    reading is the one that reads as "Narcissus : damage 00%"; the 1-bit
    reading is the same shapes in the complementary colour.

    `_render_c64_text` had this backwards (`if on: paint fg`). It went
    unnoticed because every existing caller passed its (paper, ink) pair
    swapped into (fg, bg), which cancels the inversion whenever `bg` is
    given — `surf.fill(bg)` then `fg` overpaints everything except the
    letter, so the letter shows `bg`. The `bg=None` colorkey path has
    nothing to cancel against, so a caller relying on it (the opening death
    notice's message, once DISC-220 moved it onto this path) painted a
    solid ink-coloured block with a paper-coloured letter-shaped hole -
    "the colours are swapped" from a few feet back, even though the
    (fg, bg) *values* passed were correct.

    This checks the space glyph (`$A0`, all 1-bits) stays fully transparent
    and a letter glyph (`a` = `$01`) paints *some* pixels — the specific
    failure mode (letter cells solid, spaces holed) is the inverse of both.
    """
    from alien_remake.render import c64

    ink = c64.rgb(c64.BLACK)
    space = renderer_with_tiles._render_c64_text(" ", ink)
    assert space is not None
    painted = sum(
        1
        for y in range(space.get_height())
        for x in range(space.get_width())
        if tuple(space.get_at((x, y)))[:3] == ink
    )
    assert painted == 0, "a space ($A0, all 1-bits) must paint nothing"

    letter = renderer_with_tiles._render_c64_text("a", ink)
    assert letter is not None
    painted = sum(
        1
        for y in range(letter.get_height())
        for x in range(letter.get_width())
        if tuple(letter.get_at((x, y)))[:3] == ink
    )
    assert 0 < painted < 8 * 8, "a letter must paint its shape, not fill the cell"


def test_render_c64_text_unconfirmed_character_returns_none(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """R-01: characters not yet independently confirmed against a real
    rendered image (digits, period, and others — see the module-level
    `_ASCII_TO_SCREEN_CODE` comment for the two that were tried and
    disproven live) must fall back to the system font, not guess a glyph."""
    from alien_remake.render import c64

    white = c64.rgb(c64.WHITE)
    # P-7: "O.K." now renders — `.` is `$AE`, the byte the ROM itself writes
    # (its glyph is blank, which is how the original draws it too).
    assert renderer_with_tiles._render_c64_text("O.K.", white) is not None
    # D-078: digits ARE now located ($B0-$B9), so this renders rather than
    # falling back. The period above is still unmapped ($AE is blank).
    assert renderer_with_tiles._render_c64_text("CONTROL:1", white) is not None
    # D-078: '%' is $A5, verified by rendering it — so this renders too.
    assert renderer_with_tiles._render_c64_text("50%", white) is not None


def test_c64_or_sysfont_falls_back_without_tiles(renderer: PygameRenderer) -> None:
    """`renderer` (module fixture) has no tileset — every call must use
    SysFont, never crash, regardless of character content."""
    from alien_remake.render import c64

    surf = renderer._c64_or_sysfont("Dallas", c64.rgb(c64.WHITE))
    assert surf.get_width() > 0


# --- R-05: the Alien's real animated sprite ----------------------------------


def test_alien_sprite_frames_are_valid_tileset_indices(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """R-05: `_ALIEN_SPRITE_FRAMES` (decoded from `tbl_alien_anim $4EDC`) must
    index real, loaded sprite slots — a bounds check against the actual
    tileset, not just a hardcoded table."""
    from alien_remake.render.pygame_app import _ALIEN_SPRITE_FRAMES

    assert set(_ALIEN_SPRITE_FRAMES) == {0, 1, 2, 3}  # only 4 distinct frames
    for frame in _ALIEN_SPRITE_FRAMES:
        assert frame < len(renderer_with_tiles._tiles.sprites)


def test_alien_is_never_drawn_on_the_map(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """**D-041: the Alien must NOT appear on the deck map at all.**

    R-05 briefly drew it as a persistent sprite (and before that, a red
    "X") wherever it stood — user-confirmed invented: the original never
    reveals the Alien's position that way; you locate movement via the
    ambiguous TRACKER alarm instead. Guards the removal by rendering two
    frames that differ *only* in where the Alien is, and asserting the
    output pixels are identical — if any code path drew it, moving it
    would change the frame.
    """
    from alien_remake.core.sim import Simulation

    sim = Simulation()
    assert sim.state.alien is not None
    renderer_with_tiles._ship = sim.ship
    rooms_on_deck = [r.id for r in sim.ship.rooms_on(sim.state.deck)]
    assert len(rooms_on_deck) >= 2, "need two rooms on one deck to move between"

    sim.state.alien.room_id = rooms_on_deck[0]
    renderer_with_tiles.render(sim.state)
    first = pygame.image.tobytes(renderer_with_tiles._surface, "RGB")

    sim.state.alien.room_id = rooms_on_deck[1]
    renderer_with_tiles.render(sim.state)
    second = pygame.image.tobytes(renderer_with_tiles._surface, "RGB")

    assert first == second, "moving the Alien changed the frame - it is being drawn"


def test_menu_panel_crew_names_render_via_real_charset(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """R-01's actual target: the CONTROL-panel labels (crew names, room
    names, specials labels) render through the real charset, not SysFont,
    when a tileset is loaded — the visual regression this whole feature is
    for. Checks by comparing the label's real-charset render against what
    the (now-bypassed) SysFont would have produced: they must differ, since
    the two fonts draw visibly different glyphs for the same text."""
    from alien_remake.render import c64

    fg = c64.rgb(c64.WHITE)
    real = renderer_with_tiles._c64_or_sysfont("Dallas", fg)
    sysfont_only = renderer_with_tiles._font.render("Dallas", True, fg)
    assert real.get_size() != sysfont_only.get_size()


def test_jones_is_never_drawn_on_the_map(
    renderer_with_tiles: PygameRenderer,
) -> None:
    """**D-046: Jones must NOT appear on the deck map either.**

    The game's own deck-plan key (`$4460`) enumerates exactly five map
    symbols - "Location Ptr", "Grille", "Ladder Up", "Character Postn",
    "Ladder Down" - with no cat symbol (and no Alien symbol, see
    `test_alien_is_never_drawn_on_the_map`). Same two-frame pixel-identity
    guard: move Jones and the frame must not change.
    """
    from alien_remake.core.sim import Simulation

    sim = Simulation()
    renderer_with_tiles._ship = sim.ship
    # D-158: row 24 legitimately reacts to Jones (`guard_6580`'s "<NAME> SEES
    # JONES" branch, $8932), so the two probe rooms have to be ones nobody is
    # standing in - otherwise this pixel-identity guard trips on the notice
    # rather than on a map symbol, which is what it exists to catch.
    occupied = {c.room_id for c in sim.state.crew.values() if c.alive}
    rooms_on_deck = [
        r.id for r in sim.ship.rooms_on(sim.state.deck) if r.id not in occupied
    ]
    assert len(rooms_on_deck) >= 2

    sim.state.jones_caught = False
    sim.state.jones_room_id = rooms_on_deck[0]
    renderer_with_tiles.render(sim.state)
    first = pygame.image.tobytes(renderer_with_tiles._surface, "RGB")

    sim.state.jones_room_id = rooms_on_deck[1]
    renderer_with_tiles.render(sim.state)
    second = pygame.image.tobytes(renderer_with_tiles._surface, "RGB")

    assert first == second, "moving Jones changed the frame - he is being drawn"


# --- R-18: joystick input (port 2 stand-in) ----------------------------------


class _FakeJoystick:
    """A scriptable stand-in for `pygame.joystick.Joystick` (no hardware)."""

    def __init__(self) -> None:
        self.hat = (0, 0)
        self.buttons = [False]

    def get_numhats(self) -> int:
        return 1

    def get_hat(self, _i: int) -> tuple[int, int]:
        return self.hat

    def get_numaxes(self) -> int:
        return 0

    def get_numbuttons(self) -> int:
        return len(self.buttons)

    def get_button(self, i: int) -> bool:
        return self.buttons[i]


def test_joystick_direction_fires_once_then_auto_repeats(
    renderer: PygameRenderer,
) -> None:
    """R-18: a held direction must fire once on push and then auto-repeat at a
    steady rate — not once per frame (which would make the cursor unusable)."""
    joy = _FakeJoystick()
    renderer._joystick = joy  # type: ignore[assignment]

    joy.hat = (0, 1)  # pygame hats are y-up, so this is "up"
    renderer._pending_input = []
    renderer._poll_joystick(Screen.WELCOME)
    assert renderer._pending_input == [InputEvent.UP]      # the push edge

    # Held: silent until the repeat delay elapses, then one event.
    fired = 0
    for _ in range(renderer._JOY_REPEAT_DELAY):
        renderer._pending_input = []
        renderer._poll_joystick(Screen.WELCOME)
        fired += renderer._pending_input.count(InputEvent.UP)
    assert fired == 1, "a held direction should repeat, but only on schedule"


def test_joystick_centred_emits_nothing(renderer: PygameRenderer) -> None:
    joy = _FakeJoystick()
    renderer._joystick = joy  # type: ignore[assignment]
    for _ in range(5):
        renderer._pending_input = []
        renderer._poll_joystick(Screen.WELCOME)
        assert renderer._pending_input == []


def test_joystick_button_fires_on_the_press_edge_only(
    renderer: PygameRenderer,
) -> None:
    """The single C64 joystick button = FIRE; holding it must not repeat."""
    joy = _FakeJoystick()
    renderer._joystick = joy  # type: ignore[assignment]

    joy.buttons = [True]
    renderer._pending_input = []
    renderer._poll_joystick(Screen.WELCOME)
    assert renderer._pending_input == [InputEvent.FIRE]

    renderer._pending_input = []
    renderer._poll_joystick(Screen.WELCOME)
    assert renderer._pending_input == []      # still held -> no repeat

    joy.buttons = [False]
    renderer._poll_joystick(Screen.WELCOME)
    joy.buttons = [True]
    renderer._pending_input = []
    renderer._poll_joystick(Screen.WELCOME)
    assert renderer._pending_input == [InputEvent.FIRE]   # re-press fires again


def test_no_joystick_attached_is_harmless(renderer: PygameRenderer) -> None:
    """The keyboard scheme must keep working with no joystick present."""
    renderer._joystick = None
    renderer._pending_input = []
    renderer._poll_joystick(Screen.PLAYING)
    assert renderer._pending_input == []


# --- "back" and "Skip turn" row colours (2026-09-05), not the original ------

def _crew_panel(renderer: PygameRenderer):  # type: ignore[no-untyped-def]
    """A crew member's order menu, ready to render."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    renderer._sim, renderer._ship = sim, sim.ship
    renderer._menu = MenuController(sim)
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    renderer._menu.selected_crew = crew.id
    return sim


def _row_pixel(renderer: PygameRenderer, row: int) -> tuple[int, int, int]:
    from alien_remake.render.play import _PANEL_COL

    x = (_PANEL_COL + 1) * 8
    y = row * 8 + 4
    return tuple(renderer._surface.get_at((x, y)))[:3]  # type: ignore[return-value]


def test_the_back_row_is_white_on_red(renderer: PygameRenderer) -> None:
    from alien_remake.render import c64

    sim = _crew_panel(renderer)
    renderer.render(sim.state, present=False)
    back_row = next(
        row for entry, row in zip(renderer._menu.entries(), renderer._panel_placement)
        if entry.back and row is not None
    )
    assert _row_pixel(renderer, back_row) == c64.rgb(c64.RED)[:3]


def test_the_skip_turn_row_is_cyan_when_turns_is_on(
    renderer: PygameRenderer,
) -> None:
    from alien_remake.render import c64

    sim = _crew_panel(renderer)
    renderer._menu.turns_on = True
    renderer.render(sim.state, present=False)
    entries = renderer._menu.entries()
    skip_row = next(
        row for entry, row in zip(entries, renderer._panel_placement)
        if entry.skip_turn and row is not None
    )
    assert _row_pixel(renderer, skip_row) == c64.rgb(c64.CYAN)[:3]


def test_no_skip_turn_row_when_turns_is_off(renderer: PygameRenderer) -> None:
    sim = _crew_panel(renderer)
    renderer._menu.turns_on = False
    renderer.render(sim.state, present=False)
    assert not any(e.skip_turn for e in renderer._menu.entries())


def test_the_indicate_screens_own_back_row_keeps_its_captured_colour(
    renderer: PygameRenderer,
) -> None:
    """`test_every_panel_row_carries_its_own_tables_band_colour`'s own job,
    restated as the reason the override must not apply here: the INDICATE
    LOCATION list's "back" row is checked against a *live capture* of the
    real colour RAM, which red-on-white would silently break."""
    from alien_remake.render import c64

    sim = _crew_panel(renderer)
    renderer._menu.indicating = True
    renderer.render(sim.state, present=False)
    entries = renderer._menu.entries()
    back_row = next(
        row for entry, row in zip(entries, renderer._panel_placement)
        if entry.back and row is not None
    )
    assert _row_pixel(renderer, back_row) != c64.rgb(c64.RED)[:3]
