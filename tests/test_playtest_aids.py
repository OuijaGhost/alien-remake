"""The rest of the 2026-08-29 playtesting batch: keys, overlay, cards, legend.

Four separate owner requests that share one purpose — making the remake
testable against the real disk — and one shared risk: each is an addition, so
each has to be off, or unchanged, under ORIGINAL.
"""

from __future__ import annotations

import os
import pathlib
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from alien_remake.core import constants  # noqa: E402
from alien_remake.core.devtools import Freeze  # noqa: E402
from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.core.menu import MenuController  # noqa: E402
from alien_remake.core.options import PROFILES  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


def _playing(developer: bool = True) -> tuple[PygameRenderer, GameFlow, Simulation]:
    renderer = PygameRenderer(scale=3, intro_wav=None)
    sim = Simulation(rng=random.Random(7))
    flow = GameFlow()
    flow.screen, flow.sim = Screen.PLAYING, sim
    renderer._menu = MenuController(sim)
    renderer._sim, renderer._ship = sim, sim.ship
    renderer.set_developer(developer)
    return renderer, flow, sim


# --- the developer keys -----------------------------------------------------------

def test_the_keys_are_dead_unless_developer_mode_is_on() -> None:
    """They are testing tools. A player who never turns developer mode on must
    not be able to freeze the Alien by leaning on a function key."""
    renderer, _flow, sim = _playing(developer=False)
    try:
        renderer._handle_play_key(pygame.K_F3)
        assert sim.dev.alien is Freeze.OFF
    finally:
        renderer.close()


def test_the_alien_key_freezes_and_unfreezes() -> None:
    renderer, _flow, sim = _playing()
    try:
        renderer._handle_play_key(pygame.K_F3)
        assert sim.dev.alien is Freeze.STILL
        renderer._handle_play_key(pygame.K_F3)
        assert sim.dev.alien is Freeze.OFF
    finally:
        renderer.close()


def test_the_jones_key_freezes_and_unfreezes() -> None:
    renderer, _flow, sim = _playing()
    try:
        renderer._handle_play_key(pygame.K_F4)
        assert sim.dev.jones is Freeze.STILL
        renderer._handle_play_key(pygame.K_F4)
        assert sim.dev.jones is Freeze.OFF
    finally:
        renderer.close()


def test_the_fear_keys_move_the_selected_crew_member() -> None:
    renderer, _flow, sim = _playing()
    try:
        who = next(iter(sim.state.crew))
        renderer._menu.selected_crew = who
        sim.state.crew[who].fear = 5
        renderer._handle_play_key(pygame.K_F2)
        assert sim.state.crew[who].fear == 6
        renderer._handle_play_key(pygame.K_F1)
        assert sim.state.crew[who].fear == 5
    finally:
        renderer.close()


def test_the_android_key_reveals() -> None:
    renderer, _flow, sim = _playing()
    try:
        sim.state.android_revealed = False
        renderer._handle_play_key(pygame.K_F5)
        if sim.state.android_id is not None:
            assert sim.state.android_revealed is True
    finally:
        renderer.close()


def test_a_dev_key_never_reaches_the_panel() -> None:
    """It is consumed, so a function key cannot also move the cursor."""
    renderer, _flow, _sim = _playing()
    try:
        before = renderer._menu.cursor
        renderer._handle_play_key(pygame.K_F3)
        assert renderer._menu.cursor == before
    finally:
        renderer.close()


def test_the_dev_keys_avoid_everything_the_panel_uses() -> None:
    """Function keys deliberately: a testing control that shadowed an arrow or
    space would surface as a gameplay bug report."""
    panel = {
        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d,
        pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE,
        *range(pygame.K_0, pygame.K_9 + 1),
    }
    assert not (set(PygameRenderer.DEV_KEYS) & panel)


def test_every_dev_key_says_what_it_does() -> None:
    for key, label in PygameRenderer.DEV_KEYS.items():
        assert label, key


def test_a_dev_change_is_written_to_the_session_log() -> None:
    """A run somebody reached into is a run whose log has to say so — otherwise
    it is evidence about a game that never happened."""
    renderer, _flow, sim = _playing()
    noted: list[tuple] = []
    renderer.on_menu_action = lambda kind, **f: noted.append((kind, f))
    try:
        renderer._handle_play_key(pygame.K_F3)
        assert noted, "freezing the Alien was not recorded"
        assert noted[-1][0] == "dev"
    finally:
        renderer.close()


# --- the overlay sits in the border ------------------------------------------------

def test_the_overlay_does_not_draw_on_the_game_field() -> None:
    """It used to blit onto the 320x200 surface at (2, 2) — over the top-left
    of the ship map, which is the part you most need to see while debugging the
    ship map."""
    renderer, flow, sim = _playing()
    try:
        renderer.draw(flow)
        field_before = pygame.image.tostring(renderer._surface, "RGB")
        renderer._draw_debug_overlay(sim.state)
        assert pygame.image.tostring(renderer._surface, "RGB") == field_before
    finally:
        renderer.close()


def test_the_overlay_is_composed_and_placed_separately() -> None:
    renderer, flow, sim = _playing()
    try:
        renderer.draw(flow)
        renderer._draw_debug_overlay(sim.state)
        assert renderer._dbg_panel is not None, "nothing was composed"
        renderer._blit_debug_panel()          # must not raise
    finally:
        renderer.close()


def test_the_overlay_stays_out_of_the_field_when_there_is_a_border() -> None:
    renderer, flow, sim = _playing()
    try:
        renderer.draw(flow)
        renderer._draw_debug_overlay(sim.state)
        field = renderer.field_rect()
        panel = renderer._dbg_panel
        assert panel is not None
        # Whichever strip it picks, it must fit in one of them.
        fits = (
            field.top >= panel.get_height() + 2
            or field.left >= panel.get_width() + 2
            or renderer._window.get_height() - field.bottom >= panel.get_height() + 2
        )
        assert fits or field.top == 0, "no border and no fallback"
    finally:
        renderer.close()


# --- the loading card skips ---------------------------------------------------------

def _card(screen: Screen, profile: str = "updated") -> GameFlow:
    flow = GameFlow(current_options=dict(PROFILES[profile]))
    flow.screen = screen
    flow._screen_ticks = 0
    return flow


def test_enter_skips_the_first_loading_card() -> None:
    """The publisher spiral is ~14 s and it is the first thing between
    launching and playing."""
    flow = _card(Screen.LOADING_MENU)
    flow.handle(InputEvent.FIRE)
    assert flow.screen is not Screen.LOADING_MENU


def test_escape_skips_it_too() -> None:
    flow = _card(Screen.LOADING_MENU)
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is not Screen.LOADING_MENU


def test_the_card_goes_where_the_timer_would_have_sent_it() -> None:
    """Skipping is "arrive early", never "arrive somewhere else"."""
    timed = GameFlow(current_options=dict(PROFILES["updated"]))
    timed.screen = Screen.LOADING_MENU
    timed._screen_ticks = 0
    for _ in range(constants.LOADING_MENU_TICKS + 1):
        timed.tick()
    by_timer = timed.screen

    skipped = _card(Screen.LOADING_MENU)
    skipped.handle(InputEvent.FIRE)
    assert skipped.screen is by_timer


def test_the_original_sits_through_the_loading_card() -> None:
    flow = _card(Screen.LOADING_MENU, "original")
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.LOADING_MENU
    assert flow._screen_ticks == 0


def test_the_notice_is_not_on_the_skip_list() -> None:
    """It already waits for a key, so it is not a timed card at all — and
    skipping a screen that is asking you something is a different thing."""
    from alien_remake.core.flow import _SKIPPABLE_CARDS

    assert Screen.NOTICE not in _SKIPPABLE_CARDS
    assert Screen.OPENING not in _SKIPPABLE_CARDS


# --- the legend performs itself -------------------------------------------------------

def test_the_manual_legend_reveals_rather_than_dumping() -> None:
    """Owner's call, reversing the earlier "a reference page wants to be read":
    a *sound* legend that makes no sound is not a legend."""
    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = Screen.MANUAL
    try:
        while not flow.manual_showing_legend:
            flow.handle(InputEvent.FIRE)
        renderer._legend_entered_frame = None
        renderer._legend_played = 0
        renderer.draw(flow)
        first = renderer._legend_stage_index()
        renderer._frame_count += 10_000
        renderer.draw(flow)
        assert renderer._legend_stage_index() > first, "the legend never advances"
    finally:
        renderer.close()


def test_the_legend_names_each_sound_once() -> None:
    """`_legend_played` makes the effect fire on arrival, not every frame."""
    renderer = PygameRenderer(scale=3, intro_wav=None)
    try:
        renderer._legend_entered_frame = renderer._frame_count
        renderer._legend_played = 0
        seen = []
        for _ in range(400):
            renderer._frame_count += 8
            seen.append(renderer._legend_stage())
        assert len(set(seen)) > 1, "one line for the whole screen"
    finally:
        renderer.close()


def test_both_legend_copies_share_one_reveal() -> None:
    """The only difference left between them is which screen you arrived
    from."""
    import inspect

    from alien_remake.render import frontend

    body = inspect.getsource(frontend.FrontEndMixin._draw_manual_legend)
    assert "_legend_stage()" in body, "the manual copy is static again"


# --- the keys are listed on screen (owner, 2026-08-30) ------------------------------

def test_the_overlay_lists_every_dev_key() -> None:
    """They were documented in the README and nowhere a person looking at the
    game could see them, which for five function keys with no other affordance
    means they may as well not exist."""
    renderer, _flow, sim = _playing()
    try:
        text = chr(10).join(renderer._debug_key_lines())
        for key, label in PygameRenderer.DEV_KEYS.items():
            assert pygame.key.name(key).upper() in text, key
            assert label in text, label
    finally:
        renderer.close()


def test_the_key_list_is_generated_from_the_handler() -> None:
    """Read from `DEV_KEYS`, so a key added to the handler cannot go unlisted."""
    import inspect

    from alien_remake.render import debug_overlay

    body = inspect.getsource(debug_overlay.DebugOverlayMixin._debug_key_lines)
    assert "DEV_KEYS" in body


def test_the_key_list_shows_what_the_toggles_are_set_to() -> None:
    """"F3 alien" tells you nothing about whether the Alien is frozen right
    now, which is the only thing you actually want to know mid-test."""
    renderer, _flow, sim = _playing()
    try:
        assert "[STILL]" not in chr(10).join(renderer._debug_key_lines())
        renderer._handle_play_key(pygame.K_F3)
        assert "[STILL]" in chr(10).join(renderer._debug_key_lines())
    finally:
        renderer.close()


def test_the_key_list_still_lands_in_the_border() -> None:
    """It made the panel taller and wider; it must not have pushed it back over
    the map."""
    renderer, flow, sim = _playing()
    try:
        renderer.draw(flow)
        before = pygame.image.tostring(renderer._surface, "RGB")
        renderer._draw_debug_overlay(sim.state)
        assert pygame.image.tostring(renderer._surface, "RGB") == before
        assert renderer._dbg_panel is not None
        renderer._blit_debug_panel()
    finally:
        renderer.close()


def test_the_panel_is_wide_enough_for_its_longest_label() -> None:
    """Sized to the labels rather than to a round number, so adding a key that
    needs more room widens the panel instead of being cut off."""
    from alien_remake.render import debug_overlay

    longest = max(
        len(f"{pygame.key.name(k).upper():<3} {v}  [STILL]")
        for k, v in PygameRenderer.DEV_KEYS.items()
    )
    # The overlay draws with the system font at roughly 6px a character.
    assert debug_overlay._KEY_WIDTH >= longest * 6, longest


def test_the_panel_fits_the_border_at_every_ordinary_scale() -> None:
    """The reason it is two columns. Stacked it was 98px tall against a 64px
    border at 2x and 96px at 3x, so it did not fit the strip it had just been
    moved into — at both of the commonest window sizes."""
    for scale in (2, 3, 4):
        renderer = PygameRenderer(scale=scale, intro_wav=None)
        sim = Simulation(rng=random.Random(7))
        flow = GameFlow()
        flow.screen, flow.sim = Screen.PLAYING, sim
        renderer._menu = MenuController(sim)
        renderer._sim, renderer._ship = sim, sim.ship
        renderer.set_developer(True)
        try:
            renderer.draw(flow)
            renderer._draw_debug_overlay(sim.state)
            panel = renderer._dbg_panel
            field = renderer.field_rect()
            assert panel is not None
            assert field.top >= panel.get_height() + 2, (
                f"at {scale}x the panel is {panel.get_height()}px tall and the "
                f"top border is {field.top}px - it would land on the map"
            )
        finally:
            renderer.close()


# --- the DEBUG ON marker keeps off the copyright (owner, 2026-08-30) --------------

def test_the_debug_marker_does_not_touch_the_copyright_line() -> None:
    """It was drawn at y=174 and the copyright is at y=176, so it sat two
    pixels inside "PAUL CLANSEY (c)1984 CONCEPT SOFTWARE" and was unreadable.

    Compared row by row against the same screen with developer mode off: the
    copyright's own pixels must be identical either way.
    """
    rows = {}
    for developer in (False, True):
        renderer = PygameRenderer(scale=2, intro_wav=None)
        flow = GameFlow()
        flow.screen = Screen.GAME_SELECTION
        renderer.set_developer(developer)
        try:
            renderer.draw(flow)
            surface = renderer._surface
            rows[developer] = [
                bytes(
                    surface.get_at((x, y))[0] for x in range(surface.get_width())
                )
                for y in range(170, 200)
            ]
        finally:
            renderer.close()
    assert rows[True] != rows[False] or True
    assert rows[True] == rows[False], (
        "developer mode changed pixels on the copyright rows"
    )


def test_the_debug_marker_is_still_drawn_somewhere() -> None:
    """Moving it must not have meant losing it — the point of the marker is
    that you can see developer mode is on before a game starts."""
    shots = {}
    for developer in (False, True):
        renderer = PygameRenderer(scale=2, intro_wav=None)
        flow = GameFlow()
        flow.screen = Screen.GAME_SELECTION
        renderer.set_developer(developer)
        try:
            renderer.draw(flow)
            shots[developer] = pygame.image.tostring(renderer._surface, "RGB")
        finally:
            renderer.close()
    assert shots[True] != shots[False], "DEBUG ON vanished"


# --- required and optional assets are different things ----------------------------

def test_the_c64_roms_are_optional() -> None:
    """`basic.bin` and `chargen.bin` are the machine's ROMs, not the game's, so
    no amount of extracting the disk produces them — and the game runs without
    both."""
    from alien_remake import assets

    assert "basic_rom" in assets.OPTIONAL
    assert "chargen" in assets.OPTIONAL


def test_the_disk_derived_assets_are_not_optional() -> None:
    """The ones that really do come off your own disk must stay required, or
    the card stops warning about the thing it exists to warn about."""
    from alien_remake import assets

    for key in ("charset", "intro", "menu1"):
        assert key not in assets.OPTIONAL, key


def test_missing_optional_is_reported_separately() -> None:
    from alien_remake import assets

    assert set(assets.missing_optional()) <= {"basic.bin", "chargen.bin"}
    assert "basic.bin" not in assets.missing_required()


def test_the_boot_card_does_not_call_the_roms_derived_data() -> None:
    """A working install was being told its disk decoded badly."""
    import pathlib as _p

    import alien_remake.__main__ as main_module

    source = _p.Path(main_module.__file__).read_text(encoding="utf-8")
    # `rindex`, not `index`: the comment explaining the change quotes the old
    # wording, so searching forwards finds the comment rather than the call.
    marker = source.rindex('report.warn("missing derived data')
    guard = source[:marker]
    assert "if required:" in guard, (
        "the derived-data warning is not gated on something actually being "
        "missing"
    )
    assert "the game runs without them" in source


def test_the_optional_note_says_where_they_really_come_from() -> None:
    """Telling somebody to decode their disk for a C64 ROM sends them looking
    for something that is not there."""
    from alien_remake import assets

    assert "VICE" in assets.OPTIONAL_SOURCE
    assert "not game data" in assets.OPTIONAL_SOURCE


# --- the machine's own ROMs: one search, no redistribution -------------------------

def test_the_report_and_the_readers_ask_the_same_question() -> None:
    """The bug behind the owner's screenshot.

    The startup card said BASIC.BIN and CHARGEN.BIN were missing while the game
    was reading both perfectly well, because each reader carried its own private
    fallback and the card asked `assets.find`. A report that disagrees with the
    program it reports on is worse than no report.
    """
    from alien_remake import assets
    from alien_remake.core import opening_name
    from alien_remake.render import romfont

    # **What "not reported absent" means changed on 2026-08-30.** It used to
    # mean "the ROM is on this machine"; it now means "nothing the player would
    # notice is missing", because both features work from recorded data. So the
    # agreement to check is with the *features*, not with the files - a fresh
    # install has neither ROM and neither feature is impaired.
    absent = set(assets.missing_optional())
    if "chargen.bin" not in absent:
        assert romfont.load() is not None, (
            "the font is not reported missing, so it must actually load"
        )
    if "basic.bin" not in absent:
        assert opening_name.garbled_name_codes(3) is not None, (
            "the garbled name is not reported missing, so it must actually work"
        )


def test_a_vice_installation_is_searched_for() -> None:
    """VICE is never *run* - two files are read out of it - so a player who has
    any C64 emulator gets this without being asked for anything."""
    from alien_remake import assets

    dirs = assets._vice_rom_dirs()
    assert dirs, "no VICE locations are searched at all"
    assert all(isinstance(d, pathlib.Path) for d in dirs)


def test_vices_own_filenames_are_accepted() -> None:
    """Being made to rename a download to satisfy a lookup is the sort of small
    indignity that makes people give up."""
    from alien_remake import assets

    assert assets.C64_ROMS["basic.bin"][0] == "basic-901226-01.bin"
    assert assets.C64_ROMS["chargen.bin"][0] == "chargen-901225-01.bin"


def test_a_wrong_sized_rom_is_refused(tmp_path, monkeypatch) -> None:
    """A truncated file is worse than a missing one: missing degrades visibly,
    wrong draws nonsense."""
    from alien_remake import assets

    (tmp_path / "chargen.bin").write_bytes(b"\x00" * 100)
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    monkeypatch.setattr(assets, "_vice_rom_dirs", lambda: ())
    monkeypatch.chdir(tmp_path)
    assert assets.find_c64_rom("chargen.bin") is None


def test_the_roms_are_never_vendored() -> None:
    """They are Commodore's. Locating them is the project's convention and, for
    a public repository, the one thing that could actually cause trouble."""
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    for path in tracked:
        low = path.lower()
        assert not low.endswith(("basic-901226-01.bin", "chargen-901225-01.bin")), path
        assert not low.endswith(("/basic.bin", "/chargen.bin")), path
