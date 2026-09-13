"""FV-3.2 — headless rendered-frame regression harness.

The title-screen lesson, automated: a rendering regression should fail a gate
instead of waiting for a human to look at a screenshot. Several real bugs this
project shipped were *only* visible in a rendered frame — the inverted
paper/ink model (D-050), the panel truncated by an inside-the-field border
(D-051), ALIEN's charset wrongly applied to the loader screens (D-047), and
markers drawn for entities the map never shows (D-041/D-046).

These are **structural** checks (grid geometry, palette membership, presence
or absence of a marker), not golden-image diffs — a byte-exact reference would
break on any deliberate change and tell you nothing about *what* moved.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import needs                                       # noqa: E402

pygame = pytest.importorskip("pygame")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render import c64  # noqa: E402
from alien_remake.render.layout import _HEIGHT, _WIDTH  # noqa: E402
from alien_remake.render.pygame_app import (  # noqa: E402
    PygameRenderer,
    _BORDER_X,
    _BORDER_Y,
)


@pytest.fixture
def renderer() -> PygameRenderer:
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    if not charset.exists():
        pytest.skip("out/charset.bin not present (run `alientools chars` first)")
    r = PygameRenderer(scale=2, tiles=load(charset), intro_wav=None)
    yield r
    pygame.quit()


def _colours(surface: "pygame.Surface") -> set[tuple[int, int, int]]:
    """Every distinct RGB in a surface (sampled on a 2px lattice for speed)."""
    return {
        tuple(surface.get_at((x, y)))[:3]
        for x in range(0, surface.get_width(), 2)
        for y in range(0, surface.get_height(), 2)
    }


def _play_frame(renderer: PygameRenderer) -> tuple[Simulation, GameFlow]:
    sim = Simulation()
    flow = GameFlow()
    flow.screen = Screen.PLAYING
    flow.sim = sim
    renderer.draw(flow)
    return sim, flow


# --- geometry (D-051) ----------------------------------------------------------

def test_field_is_exactly_the_40x25_text_area(renderer: PygameRenderer) -> None:
    """R-02/D-051: `_surface` must be the 320x200 field itself — 40x25 8px
    cells — so column/row arithmetic is exact. The border lives outside it."""
    # DISC-242: the draw surface is native at every window size, so this is a
    # plain equality now rather than something multiplied by the current scale.
    assert renderer._surface.get_size() == (_WIDTH, _HEIGHT)
    assert _WIDTH // 8 == 40 and _HEIGHT // 8 == 25


def test_window_adds_the_border_around_the_field(renderer: PygameRenderer) -> None:
    """The *window* scale is now independent of the draw scale (DISC-242).

    This assertion used to read `_scale` for both, which is exactly the coupling
    that made the game correct only at integer multiples typed in at startup.
    """
    s = renderer._window_scale
    assert renderer._window.get_size() == (
        (_WIDTH + 2 * _BORDER_X) * s,
        (_HEIGHT + 2 * _BORDER_Y) * s,
    )


def test_border_is_actually_drawn_around_the_field(renderer: PygameRenderer) -> None:
    """The frame outside the field must be the border colour — this is what
    regressed when the border was painted *over* the field instead."""
    _play_frame(renderer)
    win = renderer._window
    border = c64.rgb(c64.BLUE)
    # A pixel in each of the four margins.
    assert tuple(win.get_at((2, 2)))[:3] == border
    assert tuple(win.get_at((win.get_width() - 3, 2)))[:3] == border
    assert tuple(win.get_at((2, win.get_height() - 3)))[:3] == border
    # ...and the field's own top-left is NOT the border colour. Ask the renderer
    # where the field landed rather than assuming a fixed offset: it is centred
    # now, and the border is elastic (DISC-242).
    rect = renderer.field_rect()
    assert tuple(win.get_at((rect.x + 4, rect.y + 4)))[:3] != border


# --- the map shows only what the deck-plan key lists (D-041 / D-046) -----------

def test_moving_the_alien_never_changes_the_frame(renderer: PygameRenderer) -> None:
    """D-041: the game's deck-plan key lists five symbols and the Alien is not
    one of them. Moving it must not alter a single pixel."""
    sim, flow = _play_frame(renderer)
    assert sim.state.alien is not None
    rooms = [r.id for r in sim.ship.rooms_on(sim.state.deck)]
    assert len(rooms) >= 2

    sim.state.alien.room_id = rooms[0]
    renderer.draw(flow)
    first = pygame.image.tobytes(renderer._surface, "RGB")
    sim.state.alien.room_id = rooms[1]
    renderer.draw(flow)
    assert pygame.image.tobytes(renderer._surface, "RGB") == first


def test_moving_jones_never_changes_the_frame(renderer: PygameRenderer) -> None:
    """D-046: nor is the cat — the key has no cat symbol either."""
    sim, flow = _play_frame(renderer)
    # D-158: probe only rooms nobody occupies. `guard_6580`'s untaken branch
    # ($8932) writes "<NAME> SEES JONES" to row 24 when a crew member shares
    # the cat's room, which is a real ROM behaviour and would trip this guard
    # for the wrong reason — the guard is about the MAP having no cat symbol.
    occupied = {c.room_id for c in sim.state.crew.values() if c.alive}
    rooms = [
        r.id for r in sim.ship.rooms_on(sim.state.deck) if r.id not in occupied
    ]
    assert len(rooms) >= 2
    sim.state.jones_caught = False

    sim.state.jones_room_id = rooms[0]
    renderer.draw(flow)
    first = pygame.image.tobytes(renderer._surface, "RGB")
    sim.state.jones_room_id = rooms[1]
    renderer.draw(flow)
    assert pygame.image.tobytes(renderer._surface, "RGB") == first


# --- palette (D-050) -----------------------------------------------------------

def test_play_frame_uses_only_real_c64_colours(renderer: PygameRenderer) -> None:
    """Every pixel must come from the 16-colour Colodore palette — a stray
    hand-picked RGB is how invented colours creep in."""
    _play_frame(renderer)
    palette = set(c64.PALETTE)
    stray = _colours(renderer._surface) - palette
    assert not stray, f"non-C64 colours on the play screen: {sorted(stray)}"


def test_selection_frame_uses_only_real_c64_colours(
    renderer: PygameRenderer,
) -> None:
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    renderer.draw(flow)
    stray = _colours(renderer._surface) - set(c64.PALETTE)
    assert not stray, f"non-C64 colours on the selection screen: {sorted(stray)}"


def test_selection_screen_is_predominantly_green(renderer: PygameRenderer) -> None:
    """D-050: `sub_screen_setup ($5FC3)` fills colour RAM with 5 (green) and
    the screen with `$A0`, so the selection screen reads green with black
    lettering — not black with green lettering, which is how it rendered
    while the paper/ink model was inverted."""
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    renderer.draw(flow)
    surf = renderer._surface
    green = c64.rgb(c64.GREEN)
    black = c64.rgb(c64.BLACK)
    counts = {green: 0, black: 0}
    for x in range(0, surf.get_width(), 3):
        for y in range(0, surf.get_height(), 3):
            px = tuple(surf.get_at((x, y)))[:3]
            if px in counts:
                counts[px] += 1
    assert counts[green] > counts[black], "selection screen should be green-dominant"


# --- the CONTROL panel occupies its real columns (D-051 / D-052) ---------------

def test_panel_starts_at_column_30_and_is_not_truncated(
    renderer: PygameRenderer,
) -> None:
    """The panel is columns 30-39. Its labels must fit inside the field —
    the truncation bug drew them past the right edge."""
    from alien_remake.render.play import _PANEL_COL

    sim, flow = _play_frame(renderer)
    # Give the panel a selection so the order menu (its widest content) draws.
    cid = next(c.id for c in sim.state.crew.values() if c.alive and c.awake)
    assert renderer._menu is not None
    renderer._menu.selected_crew = cid
    renderer.draw(flow)

    s = 1  # DISC-242: the draw surface is native
    panel_x = _PANEL_COL * 8 * s
    assert panel_x < renderer._surface.get_width()
    # Every panel label must be at most the panel's 10 columns wide.
    for entry in renderer._menu.entries():
        assert len(entry.label) <= 10, f"{entry.label!r} overflows the 10-col panel"


# --- the loader screens use the ROM font, not ALIEN's charset (D-047) ---------

@pytest.mark.parametrize(
    "screen", [Screen.NOTICE, Screen.WELCOME, Screen.INSTRUCTIONS]
)
def test_front_end_screens_do_not_use_the_custom_charset(
    renderer: PygameRenderer, screen: Screen
) -> None:
    """D-047: LOADING/NOTICE/WELCOME/INSTRUCTIONS are drawn by the *loader*
    programs, which run before `set_charbase ($400A)` points the VIC at
    ALIEN's own font — so they use the standard C64 ROM font. ALIEN's charset
    is cut-out (letters are the 0-bits), which makes text render as solid
    slabs; a slab-heavy frame here means the R-01 regression is back.
    """
    flow = GameFlow()
    flow.screen = screen
    renderer.draw(flow)
    surf = renderer._surface
    black = c64.rgb(c64.BLACK)
    lit = sum(
        1
        for x in range(0, surf.get_width(), 2)
        for y in range(0, surf.get_height(), 2)
        if tuple(surf.get_at((x, y)))[:3] != black
    )
    total = (surf.get_width() // 2) * (surf.get_height() // 2)
    # Stroke text lights a small fraction of the screen; cut-out slabs light
    # a large one. 25% is far above any stroke-font layout here.
    assert lit / total < 0.25, (
        f"{screen.name} is {lit / total:.0%} lit — looks like cut-out slab text"
    )


def test_the_view_follows_the_selected_crew_member_between_decks() -> None:
    """**[C $4CC9-$4CE2] RETRACTS D-131.** The deck plan does follow them.

    Every pass the ROM copies the selected character's current room into
    `$64F7` and redraws from it: `menu_option_dispatch ($511C)` reads
    `$7569,Y` and calls `init_menu_ptr`/`menu2`/`menu3`, each of which copies a
    **30x18 deck plan** from `$A000`/`$A21C`/`$A438` into `$0400`. Those decode
    to "UPPER DECK", "MIDDLE DECK" and "LOWER DECK".

    D-131 read `$511C` as only positioning sprite 0 and stopped short of the
    `init_menu_ptr` calls, then leaned on the manual's "EACH DECK OF THE SHIP
    CAN BE SELECTED FROM THE MENU" — which describes the menu, not the only way
    the view changes. Reported by the player as crew vanishing from the screen
    on a deck change, needing a quit-and-reselect to get the view back.
    """
    from alien_remake.core.flow import GameFlow, Screen
    from alien_remake.core.sim import Simulation
    from alien_remake.core.modes import DeathVariant, GameMode
    from alien_remake.render.pygame_app import PygameRenderer

    renderer = PygameRenderer()
    try:
        sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.FIXED)
        flow = GameFlow()
        flow.sim = sim
        flow.screen = Screen.PLAYING
        renderer.draw(flow)
        assert renderer._menu is not None

        crew = next(
            c for c in sim.state.crew.values() if c.alive and c.room_id is not None
        )
        renderer._menu.selected_crew = crew.id
        home = sim.ship.rooms[crew.room_id].deck

        # Park the view on another deck, then redraw: it must come back to them.
        other = next(d for d in sim.ship.decks() if d != home)
        sim.state.deck = other
        renderer.draw(flow)
        assert sim.state.deck == home, "the view must follow the selection"

        # And it must keep following when they walk to another deck.
        elsewhere = next(
            r for r in sim.ship.rooms.values() if r.deck != home
        )
        crew.room_id = elsewhere.id
        renderer.draw(flow)
        assert sim.state.deck == elsewhere.deck
    finally:
        renderer.close()


def test_indicate_list_wrap_stays_inside_the_visible_panel(
    renderer: PygameRenderer,
) -> None:
    """**P5-8/D-133.** `MenuController.move` already wraps the cursor
    correctly (`% len(selectable)`); the reported bug is that the panel drew
    every entry from row 1 with no scroll window, so wrapping from the top of
    a 36-entry INDICATE list to the bottom put the highlighted row far below
    the panel's real 17-row budget (`_STATUS_ROW - 1`) — invisible, which is
    exactly what "moving up does nothing" looks like from the player's seat.
    """
    from alien_remake.render.play import _PANEL_COL, _STATUS_ROW

    sim, flow = _play_frame(renderer)
    assert renderer._menu is not None
    cid = next(c.id for c in sim.state.crew.values() if c.alive and c.awake)
    renderer._menu.selected_crew = cid
    renderer._menu.indicating = True
    renderer._menu.cursor = 0

    renderer._menu.move(-1)  # UP from the top -> should wrap to the bottom
    renderer.draw(flow)

    s = 1  # DISC-242: the draw surface is native
    cursor_idx = renderer._menu.current_index()
    assert cursor_idx is not None and cursor_idx > 0, "should have wrapped"

    # The highlighted row must be drawn within the panel's visible band —
    # i.e. some row strictly above the status band, not off past it.
    px = _PANEL_COL * 8 * s + 2
    # DISC-232: the panel is rows 0-18 inclusive (19 rows), live-confirmed
    # from colour RAM — this used to stop at row 17 on DISC-213's short table.
    visible_bottom_y = (_STATUS_ROW + 1) * 8 * s
    found = False
    for y in range(0, visible_bottom_y, 8 * s):
        colour = tuple(renderer._surface.get_at((px, y)))[:3]
        if colour == (0, 0, 0):  # D-050: highlighted row's paper is black
            found = True
            break
    assert found, "the wrapped-to cursor row must be drawn inside the panel"


def test_indicate_list_never_bleeds_into_the_status_band(
    renderer: PygameRenderer,
) -> None:
    """**P5-7 — resolved as a side effect of D-133 (P5-8's scroll fix).**

    Before the panel had a scroll window, INDICATE's 36-entry room list
    overflowed past row 17 into the status band (row 18+, `_STATUS_ROW`),
    which `_draw_status_line` then partially overwrote since it draws last —
    "GRILLE IN PLACE / MORALE / ALSO HERE drawn over the room list." With the
    panel now bounded to its real 17-row budget, the two can never overlap.
    """
    from alien_remake.render.play import (
        _BOTTOM_BANDS, _PANEL_COL, _PANEL_SECTIONS, _STATUS_ROW,
    )
    from alien_remake.render import c64

    sim, flow = _play_frame(renderer)
    assert renderer._menu is not None
    cid = next(c.id for c in sim.state.crew.values() if c.alive and c.awake)
    renderer._menu.selected_crew = cid
    renderer._menu.indicating = True
    renderer.draw(flow)

    s = 1  # DISC-242: the draw surface is native
    px = _PANEL_COL * 8 * s + 2
    # **DISC-232** — the panel's own palette and the status bands genuinely
    # SHARE colours (LT_GREY, LT_GREEN and YELLOW all appear in both), so
    # "is this pixel a status colour" can no longer detect a bleed. What the
    # bug actually was is content drawn *below* the panel, so check that
    # instead: every panel row carries one of the panel's OWN band colours,
    # and none is left black.
    # Every panel row must carry *something* — a band colour, or the cursor's
    # own inverted bar. A row that is entirely black is an unpainted row, which
    # is the bug (DISC-232: rows 16-18 were outside the old 16-row table).
    # Scan the row rather than sampling one pixel: a label's glyph ink is black
    # by design (D-050), so a single probe can land on a letter stroke.
    for row in range(0, _STATUS_ROW + 1):
        y = row * 8 * s + 4
        seen = {
            tuple(renderer._surface.get_at((x, y)))[:3]
            for x in range(_PANEL_COL * 8 * s, renderer._surface.get_width())
        }
        assert seen != {(0, 0, 0)}, f"row {row} of the panel is entirely black"
    assert _PANEL_SECTIONS[-1][1] == _STATUS_ROW, (
        "the panel's last row is 18 - the same row the status band starts on, "
        "which the ROM paints white for `quit` over the grey bar's 30 cells"
    )
    status_colours = {tuple(c) for _, _, c in _BOTTOM_BANDS}
    # Sample near the left edge (x=1) — clear of any glyph ink, which starts
    # at x=8*s — to read the row's plain background colour.
    status_row_colour = tuple(
        renderer._surface.get_at((1, _STATUS_ROW * 8 * s))
    )[:3]
    assert status_row_colour in status_colours, "sanity: row 18 IS the status band"


def _boot_to_playing(seed: int):
    """Drive `GameFlow` through the real front-end chain to `PLAYING`, the
    way `run_app` does — not by constructing a bare `Simulation`."""
    import random

    from alien_remake.core.flow import GameFlow, InputEvent, Screen

    flow = GameFlow()
    for _ in range(2000):
        if flow.screen is Screen.NOTICE:
            flow.handle(InputEvent.FIRE)
        elif flow.screen is Screen.WELCOME:
            flow.handle(InputEvent.SELECT_FULL)
        elif flow.screen is Screen.INSTRUCTIONS:
            flow.handle(InputEvent.NO)
        elif flow.screen is Screen.GAME_SELECTION:
            flow.handle(InputEvent.SELECT_FULL)
            flow.sim.rng = random.Random(seed)
        elif flow.screen is Screen.PLAYING:
            return flow
        flow.tick()
    raise RuntimeError(f"never reached PLAYING (stuck on {flow.screen})")


def _reachable_crew_names(renderer: PygameRenderer) -> set[str]:
    """Walk the CONTROL list purely through `_handle_play_key` (DOWN), the
    same call the real keyboard/joystick handler makes — not `Simulation`."""
    from alien_remake.core.menu import MenuCategory

    assert renderer._menu is not None
    renderer._menu.selected_crew = None
    renderer._menu.cursor = 0
    renderer._menu.indicating = False
    seen: set[str] = set()
    n_crew = len(
        [e for e in renderer._menu.entries() if e.category is MenuCategory.CREW]
    )
    for _ in range(n_crew + 2):
        idx = renderer._menu.current_index()
        if idx is not None:
            entry = renderer._menu.entries()[idx]
            if entry.category is MenuCategory.CREW:
                seen.add(entry.label)
        renderer._handle_play_key(pygame.K_DOWN)
    return seen


@pytest.mark.parametrize("seed", range(6))
def test_every_living_crew_member_is_reachable_through_the_real_panel(
    seed: int,
) -> None:
    """**P7-VERIFY closes P3-1 the way the standing correction demands.**

    P3-1 ("three crew cannot be selected at the start of a LONG game") was
    closed twice on `Simulation`/`MenuController` evidence alone and reopened
    twice by the same player report — the exact failure mode the standing
    correction warns about (a passing headless check is not evidence the
    player sees the change). This drives the ACTUAL boot chain (`GameFlow`)
    to `PLAYING`, builds the real `PygameRenderer` + `MenuController` the app
    loop builds, and navigates with `_handle_play_key(K_DOWN)` — the same
    call a real keyboard press makes — never touching `Simulation` directly.
    """
    flow = _boot_to_playing(seed)
    renderer = PygameRenderer(intro_wav=None)
    renderer.draw(flow)  # builds renderer._menu, same as the app loop's first frame

    for ticks in (0, 300):
        for _ in range(ticks):
            flow.tick()
        renderer.draw(flow)
        live = {c.name for c in flow.sim.state.crew.values() if c.alive}
        reachable = _reachable_crew_names(renderer)
        missing = live - reachable
        assert not missing, (
            f"seed={seed} ticks={ticks}: {missing} unreachable via the panel"
        )
    pygame.quit()


def test_narcissus_shows_the_cockpit_not_the_deck_map(
    renderer: PygameRenderer,
) -> None:
    """**[C $5134-$513B/$4F25] D-144**, live-confirmed by the player's own
    VICE capture (`out/Cockpit.png`): `menu_option_dispatch` skips every
    deck-template loader for a character in NARCISSUS and calls
    `setup_cursor_sprite` instead; `update_2` independently confirms room 34
    is special-cased (`$4F25 CMP #$22`, skips the marker heartbeat). The
    remake must show a different scene, not the ordinary deck plan, when the
    selected crew member is there.
    """
    from alien_remake.core.nostromo import NARCISSUS

    sim, flow = _play_frame(renderer)
    cid = next(c.id for c in sim.state.crew.values() if c.alive)
    assert renderer._menu is not None
    renderer._menu.selected_crew = cid

    sim.state.crew[cid].room_id = next(
        r for r in sim.ship.rooms if r != NARCISSUS
    )
    renderer.draw(flow)
    elsewhere_frame = pygame.image.tobytes(renderer._surface, "RGB")

    sim.state.crew[cid].room_id = NARCISSUS
    renderer.draw(flow)
    narcissus_frame = pygame.image.tobytes(renderer._surface, "RGB")

    assert narcissus_frame != elsewhere_frame, (
        "the map area must look different once the selected crew member "
        "boards the Narcissus"
    )


def test_narcissus_cockpit_uses_only_c64_palette_colours(
    renderer: PygameRenderer,
) -> None:
    from alien_remake.core.nostromo import NARCISSUS

    sim, flow = _play_frame(renderer)
    cid = next(c.id for c in sim.state.crew.values() if c.alive)
    assert renderer._menu is not None
    renderer._menu.selected_crew = cid
    sim.state.crew[cid].room_id = NARCISSUS
    renderer.draw(flow)

    palette = set(c64.PALETTE)
    stray = _colours(renderer._surface) - palette
    assert not stray, f"non-C64 colours in the cockpit view: {sorted(stray)}"


def test_narcissus_cockpit_does_not_animate_the_standing_figure(
    renderer: PygameRenderer,
) -> None:
    """**[C $4F25-$4F4B]** `update_2` returns immediately (`BEQ $4F4B`) for a
    character in NARCISSUS instead of running the normal heartbeat colour
    cycle — the figure is drawn once, statically, not pulsing."""
    from alien_remake.core.nostromo import NARCISSUS

    sim, flow = _play_frame(renderer)
    cid = next(c.id for c in sim.state.crew.values() if c.alive)
    assert renderer._menu is not None
    renderer._menu.selected_crew = cid
    sim.state.crew[cid].room_id = NARCISSUS

    frames = set()
    for _ in range(30):
        renderer.draw(flow)
        frames.add(pygame.image.tobytes(renderer._surface, "RGB"))
    assert len(frames) == 1, "the cockpit scene should be static, not pulsing"


def test_narcissus_cockpit_is_drawn_from_the_real_machine_capture() -> None:
    """**[C-live] D-147 — the cockpit is the machine's own screen+colour RAM.**

    `docs/reference/narcissus_0400.bin` / `narcissus_d800.bin` were captured
    by running the ROM's own selection routine (`guard_alien_present $7720`)
    live with a crew member poked into room 34
    (`tools/vice-mcp/capture_cockpit_real.py`). The picture is three glyphs
    plus colour RAM — `$A0` solid hull, `$20` clear window, `$EE`/`$EF`
    dials — which is why no stored 540-byte template exists in the PRG and
    every static search for one failed.

    This pins the capture's own shape, so a re-render that silently loses it
    (or an accidental return to the hand-drawn approximation) fails.
    """
    from pathlib import Path

    ref = Path("archive") / "reference"
    scr_p, col_p = ref / "narcissus_0400.bin", ref / "narcissus_d800.bin"
    if not (scr_p.exists() and col_p.exists()):
        pytest.skip("narcissus captures not present")
    scr = scr_p.read_bytes()
    col = col_p.read_bytes()
    # Same 2-byte load-address format as the deck captures.
    assert scr[:2] == b"\x00\x04" and len(scr) == 1002
    assert col[:2] == b"\xd8\x00"[::-1] and len(col) == 1002

    body = scr[2:]
    map_codes = {body[r * 40 + c] for r in range(18) for c in range(30)}
    # Exactly the three-glyph vocabulary described above.
    assert map_codes <= {0x20, 0xA0, 0xEE, 0xEF}, sorted(map_codes)
    assert 0xA0 in map_codes and 0x20 in map_codes   # hull and window
    assert {0xEE, 0xEF} & map_codes                  # the dials

    colours = {col[2:][r * 40 + c] & 0x0F for r in range(18) for c in range(30)}
    assert 9 in colours, "the brown pilot chairs must be in the capture"
    assert colours & {11, 12, 15}, "the hull greys must be in the capture"


def test_the_bottom_panel_matches_the_captured_screen_row_for_row() -> None:
    """The status area, checked against the original's own screen RAM.

    **[C draw_control_panel_body $79CD]** `$7A10` is a **42-byte** template that
    the game copies out in two pieces, both starting at **column 10**::

        $7A10 +$0C -> $0702   row 19   ": damage 00%"
        $7A1C +$1E -> $0752   row 21   " is <9>,morale:<9>"

    Both fields are **9 wide** - exactly "collapsed", exactly "confident".

    The first attempt at this read the template as 40 columns, which makes the
    morale field 7 wide, and then right-anchored the `,morale:` run to column 39
    to stop "confident" being clipped to "confide". It looked right in isolation
    and was wrong: the mistake was checking my own arithmetic instead of the
    capture sitting in `docs/reference/`. This test compares against that.

    NB the `.bin` captures carry a **2-byte load address** - `narcissus_0400.bin`
    is 1002 bytes, not 1000. Reading them without skipping it shifts every
    column by two, which is what made the layout look off-by-two.
    """
    needs.need(needs.REFERENCE)
    import pathlib as _pathlib

    from alientools.gamedata import _screen_char
    from alien_remake.render.play import bottom_panel_rows

    scr = _pathlib.Path("archive/reference/narcissus_0400.bin").read_bytes()[2:]
    rows = bottom_panel_rows("Narcissus", 0, "Kane", "O.K.", "confident", [])

    for row in (19, 20, 21, 22, 23):
        rom = "".join(_screen_char(b) for b in scr[row * 40:row * 40 + 40])
        mine = rows[row - 18]
        # `$AE` decodes as `.` but renders blank (D-078/P-7) - this font has no
        # period glyph - so the template's fill and a plain space are the same
        # pixels. Compare the text, not the filler.
        assert rom.replace(".", " ").rstrip() == mine.replace(".", " ").rstrip(), (
            f"row {row}: ROM |{rom}| got |{mine}|"
        )

    crew = rows[21 - 18]
    assert crew.index("is") == 11
    assert crew.index("O.K.") == 14
    assert crew.index(",morale:") == 23
    assert crew.endswith("confident"), "the 9-wide field fits it exactly"
    assert len(crew) == 40


def test_the_status_template_is_42_bytes_with_two_nine_wide_fields() -> None:
    """The decoded template, straight from `$7A10`.

    Pinned because a 40-column reading is *almost* right - it only loses the
    last two bytes, and those two are the tail of the morale field.
    """
    from alien_remake.core.gamedata_snapshot import (
        STATUS_TEMPLATE, STATUS_TEMPLATE_PIECES,
    )

    assert len(STATUS_TEMPLATE) == 42
    assert STATUS_TEMPLATE == ": damage 00% is .........,morale:........."
    assert STATUS_TEMPLATE_PIECES == ((0, 12, 19, 10), (12, 30, 21, 10))
    # Every word each field must hold, and the longest is exactly the width.
    assert max(len(w) for w in ("O.K.", "wounded", "collapsed", "DEAD")) == 9
    assert max(len(w) for w in
               ("confident", "stable", "uneasy", "shaken", "broken")) == 9


def test_the_portrait_sits_where_place_selected_char_sprite_puts_it() -> None:
    """**[C place_selected_char_sprite $6667]** Sprite 2 at VIC `($1C, $A9)`.

    Sprite coordinates count from the border, so the visible-screen position is
    `(28-24, 169-50)` = `(4, 119)` - the bottom-left of the view window, since a
    sprite is 21 rows tall and the window ends at row 17.

    Reported as sitting too high and colliding with the status band. It does
    not; the position has been right all along. What made it look wrong is that
    `$D029` takes its colour from the character's duct flag (`$6501,Y`) - **0,
    black, while they are in a room** - so the portrait is black-on-black unless
    the deck plan is actually drawn behind it. Without a tileset the renderer
    falls back to a placeholder grid on a black field and the portrait vanishes.
    """
    from alien_remake.render.play import (
        _CHAR_PORTRAIT_AT, _CHAR_PORTRAIT_DUCT_COLOUR, _CHAR_PORTRAIT_ROOM_COLOUR,
        _STATUS_ROW,
    )
    from alien_remake.render import c64

    assert _CHAR_PORTRAIT_AT == (0x1C - 24, 0xA9 - 50) == (4, 119)
    # 21 rows tall, and the view window runs to the end of row 17.
    assert _CHAR_PORTRAIT_AT[1] + 21 <= _STATUS_ROW * 8, "must not reach the band"
    assert _CHAR_PORTRAIT_AT[1] + 21 > (_STATUS_ROW - 3) * 8, "sits at the bottom"
    # `LDA $6501,Y / STA $D029` - the flag *is* the colour index.
    assert _CHAR_PORTRAIT_ROOM_COLOUR == c64.BLACK == 0
    assert _CHAR_PORTRAIT_DUCT_COLOUR == c64.WHITE == 1


def test_the_grille_caption_keeps_the_roms_own_casing() -> None:
    """**[C $86C8 / $86D7 / $86E6]** Mixed case, not shouted.

        86C8  87 12 09 0C 0C 05 A0 09 0E A0 10 0C 01 03 05  "Grille in place"
        86D7  87 12 09 0C 0C 05 A0 12 05 0D 0F 16 05 04 A0  "Grille removed "
        86E6  92 05 0D 16 87 12 09 0C 0C 05                 "RemvGrille"

    The high bit selects case in this charset (DISC-215), so `$87` is `G` and
    `$12` is `r`. Both captions are exactly 15 characters and the label 10.
    """
    from alientools.gamedata import _screen_char

    def decode(*codes: int) -> str:
        return "".join(_screen_char(c) for c in codes)

    assert decode(0x87, 0x12, 0x09, 0x0C, 0x0C, 0x05, 0xA0, 0x09, 0x0E, 0xA0,
                  0x10, 0x0C, 0x01, 0x03, 0x05) == "Grille in place"
    assert decode(0x92, 0x05, 0x0D, 0x16, 0x87, 0x12, 0x09, 0x0C, 0x0C,
                  0x05) == "RemvGrille"


def test_the_panel_bands_match_the_live_colour_ram_capture() -> None:
    """**DISC-232** — the panel is 19 rows (0-18), read off real colour RAM.

    `docs/reference/narcissus_d800.bin` cols 30-39 is a live capture of an
    actual crew-order panel. DISC-213 built the old table from screenshots and
    got 16 rows with `quit` on row 15; the capture disagrees on every band
    below row 0 and puts `quit` on **row 18**, leaving rows 16-18 unpainted —
    the black sections at the bottom of the crew menu.

    It also dissolves the `$064E`/`$0676` "conflict": row 14 and row 15 are
    both inside this PURPLE Special block, and the same capture shows
    "Get Jones" sitting on row 15.
    """
    needs.need(needs.REFERENCE)
    import pathlib as _pathlib

    from alientools.gamedata import _screen_char
    from alien_remake.render.play import _PANEL_SECTIONS

    col = _pathlib.Path("archive/reference/narcissus_d800.bin").read_bytes()[2:]
    scr = _pathlib.Path("archive/reference/narcissus_0400.bin").read_bytes()[2:]

    # Expand the table into a per-row colour, then compare against the capture.
    want: dict[int, int] = {}
    for first, last, colour in _PANEL_SECTIONS:
        for row in range(first, last + 1):
            want[row] = colour
    assert sorted(want) == list(range(0, 19)), "the panel is rows 0-18, no gaps"

    for row in range(0, 19):
        cells = set(col[row * 40 + 30 : row * 40 + 40])
        assert len(cells) == 1, f"row {row} of the real panel is not one colour"
        assert cells.pop() == want[row], f"row {row} band colour"

    # The two fixed SPECIAL cells the ROM writes are both in the purple block.
    assert want[14] == want[15] == 4, "PURPLE"
    assert (0x064E - 0x0400) // 40 == 14 and (0x064E - 0x0400) % 40 == 30
    assert (0x0676 - 0x0400) // 40 == 15 and (0x0676 - 0x0400) % 40 == 30
    # ...and the capture proves it: GET JONES really is on row 15.
    row15 = "".join(_screen_char(b) for b in scr[15 * 40 + 30 : 15 * 40 + 40])
    assert row15.strip() == "Get Jones"
    # `quit` is on row 18, not 15 — which is what DISC-213 had wrong.
    row18 = "".join(_screen_char(b) for b in scr[18 * 40 + 30 : 18 * 40 + 40])
    assert "quit" in row18


def test_each_crew_panel_label_lands_on_its_own_colour_band() -> None:
    """**DISC-232** — the ROM writes fixed cells, so labels never drift.

    Drawing the entry list sequentially put `use:` on the blue block and
    `Special:` on the red one as soon as any optional row (Leave item, GET
    JONES) was absent — the owner's "some words on the wrong colour
    background". Slots are fixed per category instead.
    """
    import random

    from alien_remake.core.menu import MenuCategory, MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render.play import PlayMixin, _PANEL_SECTIONS

    band_of: dict[int, int] = {}
    for first, last, colour in _PANEL_SECTIONS:
        for row in range(first, last + 1):
            band_of[row] = colour

    expected = {
        MenuCategory.MOVE_TO: 14,   # LT_BLUE
        MenuCategory.USE: 13,       # LT_GREEN
        MenuCategory.GET: 10,       # LT_RED
        MenuCategory.LEAVE: 10,     # LT_RED
        MenuCategory.SPECIAL: 4,    # PURPLE
        MenuCategory.QUIT: 1,       # WHITE
    }

    for seed in range(6):
        sim = Simulation(rng=random.Random(seed))
        menu = MenuController(sim)
        crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
        menu.selected_crew = crew.id
        entries = menu.entries()
        rows = PlayMixin._panel_rows(entries)
        for entry, row in zip(entries, rows):
            if row is None:
                continue
            assert 0 <= row <= 18
            if entry.category in expected:
                assert band_of[row] == expected[entry.category], (
                    f"{entry.label!r} ({entry.category.name}) landed on row "
                    f"{row}, band {band_of[row]}"
                )
        # No two entries may share a row.
        placed = [r for r in rows if r is not None]
        assert len(placed) == len(set(placed)), f"seed {seed}: overlapping rows"


def test_the_control_list_uses_its_own_rom_colour_table() -> None:
    """**[C $7000] DISC-235** — two screens, two tables.

    `$7000` is the CONTROL list's per-row colour table (`$749C LDA $7000,Y`,
    read with `$64E5` to restore a row's normal colour after the cursor
    blink). It was dismissed once for "not matching the panel" — it was being
    checked against a *crew* panel, which has its own layout (DISC-232).

    Decoded from the ROM and confirmed against a live colour-RAM capture of
    the CONTROL list: LT_GREY 0, LT_BLUE 1-8, LT_GREEN 9, WHITE 10, LT_RED
    11-15, LT_GREY 16-18 — with the seven crew on rows 2-8 and the three decks
    on 13-15.
    """
    import random

    from alien_remake.core import gamedata_snapshot as data
    from alien_remake.core.menu import MenuCategory, MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render.play import _CONTROL_SECTIONS, PlayMixin

    assert data.CONTROL_PANEL_COLOURS == (
        15,                                  # row 0   LT_GREY  "CONTROL"
        14, 14, 14, 14, 14, 14, 14, 14,      # 1-8     LT_BLUE  Order: + crew
        13,                                  # 9       LT_GREEN "indicate"
        1,                                   # 10      WHITE    "location"
        10, 10, 10, 10, 10,                  # 11-15   LT_RED   display + decks
        15, 15, 15,                          # 16-18   LT_GREY  empty
    )
    assert len(_CONTROL_SECTIONS) == 19
    # ...and it is NOT the crew panel's table.
    from alien_remake.render.play import _PANEL_SECTIONS

    assert _CONTROL_SECTIONS != _PANEL_SECTIONS

    sim = Simulation(rng=random.Random(0))
    menu = MenuController(sim)
    menu.selected_crew = None
    entries = menu.entries()
    rows = PlayMixin._control_rows(entries)
    by_row = {r: e for e, r in zip(entries, rows) if r is not None}

    assert by_row[0].label == "CONTROL"
    assert by_row[1].label == "Order:"
    crew_rows = [r for e, r in zip(entries, rows)
                 if e.category is MenuCategory.CREW]
    assert crew_rows == [2, 3, 4, 5, 6, 7, 8], "seven crew on rows 2-8"
    assert by_row[9].label == "indicate" and by_row[10].label == "location"
    assert by_row[11].label == "display" and by_row[12].label == "level:"
    deck_rows = [r for e, r in zip(entries, rows)
                 if e.category is MenuCategory.DECK]
    assert deck_rows == [13, 14, 15], "three decks on rows 13-15"
    placed = [r for r in rows if r is not None]
    assert len(placed) == len(set(placed)), "no two entries share a row"


def test_every_panel_row_carries_its_own_tables_band_colour() -> None:
    """**DISC-238** — the paper comes from the ROW, not the entry's category.

    The ROM colours the panel's ten columns strictly by row, from whichever of
    the three tables is in force (crew panel live-captured, CONTROL `$7000`,
    INDICATE `$7440`). `_BAND_COLOUR` is a per-category approximation that
    predates them: it agrees with the crew panel by coincidence and disagrees
    badly on INDICATE, where every row is category INDICATE and the whole list
    drew light green over its real light-blue band.
    """
    import random

    from alien_remake.core import gamedata_snapshot as data
    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render import c64, tiles
    from alien_remake.render.pygame_app import PygameRenderer
    from alien_remake.render.play import _PANEL_COL, _PANEL_SECTIONS

    r = PygameRenderer(intro_wav=None)
    try:
        sim = Simulation(rng=random.Random(0))
        r._ship, r._sim = sim.ship, sim
        r._menu = MenuController(sim)
        crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
        s = 1  # DISC-242: the draw surface is native

        def rows_ok(expected: "tuple[int, ...]") -> list[int]:
            r.render(sim.state, present=False)
            bad = []
            for row, colour in enumerate(expected):
                want = c64.rgb(colour)
                seen = {
                    tuple(r._surface.get_at((x, row * 8 * s + 4)))[:3]
                    for x in range(_PANEL_COL * 8 * s, r._surface.get_width())
                }
                if want not in seen:
                    bad.append(row)
            return bad

        # CONTROL list -> $7000
        r._menu.selected_crew = None
        assert rows_ok(data.CONTROL_PANEL_COLOURS) == []

        # INDICATE -> $7440 (the one the category map got wrong)
        r._menu.selected_crew = crew.id
        r._menu.indicating = True
        for page in (0, 1):
            r._menu.indicate_page = page
            assert rows_ok(data.INDICATE_PANEL_COLOURS) == [], f"page {page}"

        # Crew order panel -> the live-captured table
        r._menu.indicating = False
        crew_bands = tuple(
            colour
            for first, last, colour in _PANEL_SECTIONS
            for _ in range(first, last + 1)
        )
        assert rows_ok(crew_bands) == []
    finally:
        import pygame

        pygame.quit()
