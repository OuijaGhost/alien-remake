"""Pointer input on the CONTROL panel (P1-P3).

Not the original: the disk has no pointer. What these pin is that a click does
*exactly* what the cursor keys already do — put the highlight on a row and fire
it — and that it lands on the row the player actually sees, which is the part
that can silently rot.

The panel does **not** put entry N on row N. The crew-order panel and the
CONTROL list both use fixed ROM slot maps and the INDICATE room list scrolls, so
hit-testing inverts the placement the renderer recorded while drawing rather
than recomputing it. `test_a_click_lands_on_the_row_the_player_sees` is the test
that fails if anyone replaces that with the obvious-looking arithmetic.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.core.menu import MenuController  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render.layout import _WIDTH  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


def _playing(select_crew: bool = False,
             seed: int = 7) -> tuple[PygameRenderer, GameFlow]:
    """A renderer on the play screen with the panel drawn once.

    **Seeded, and the crew member is chosen rather than named.** The opening
    kills a random crew member and hides a random android, and `entries()`
    re-derives commandability every frame (D-158) — so naming a crew member
    outright gave a panel that was the crew-order list on most runs and the
    CONTROL list on the rest, and the tests failed about one run in three
    against world state they never meant to depend on.
    """
    import random

    renderer = PygameRenderer(scale=3, intro_wav=None)
    sim = Simulation(rng=random.Random(seed))
    flow = GameFlow()
    flow.screen, flow.sim = Screen.PLAYING, sim
    renderer._menu = MenuController(sim)
    renderer._sim, renderer._ship = sim, sim.ship
    if select_crew:
        # Whoever the panel will actually keep selected: `entries()` drops a
        # selection it does not consider commandable, so this asks it.
        for entry in renderer._menu.entries():
            if entry.select_crew is None:
                continue
            renderer._menu.selected_crew = entry.select_crew
            if renderer._menu.entries()[0].label != "CONTROL":
                break
            renderer._menu.selected_crew = None
        assert renderer._menu.selected_crew is not None, "no crew is commandable"
    renderer.draw(flow)
    return renderer, flow


def _window_pos(renderer: PygameRenderer, row: int, col: int = 31) -> tuple[int, int]:
    """The middle of a panel cell, in window coordinates."""
    rect = renderer.field_rect()
    scale = max(1, rect.width // _WIDTH)
    return (rect.x + (col * 8 + 4) * scale, rect.y + (row * 8 + 4) * scale)


# --- P1: absolute cursor placement ------------------------------------------

def test_select_index_rejects_headers_and_out_of_range() -> None:
    menu = MenuController(Simulation())
    entries = menu.entries()
    header = next(i for i, e in enumerate(entries) if not e.selectable)
    before = menu.cursor

    assert menu.select_index(header) is False
    assert menu.select_index(len(entries)) is False
    assert menu.select_index(-1) is False
    assert menu.cursor == before, "a rejected index must not move the cursor"


def test_select_index_addresses_the_full_entry_list_not_the_selectables() -> None:
    """The conversion that is easy to get wrong.

    `cursor` counts selectable entries; a caller reading rows off the screen
    has full-list indices, headers included. Selecting the *n*-th line must
    land on that line, not on the *n*-th option.
    """
    menu = MenuController(Simulation())
    entries = menu.entries()
    for index, entry in enumerate(entries):
        if not entry.selectable:
            continue
        assert menu.select_index(index) is True
        assert menu.current_index() == index, f"line {index} ({entry.label!r})"


# --- P2/P3: the pointer path -------------------------------------------------

def test_a_click_lands_on_the_row_the_player_sees() -> None:
    """Hit-testing must invert the *drawn* placement, not assume row == index.

    The crew-order panel is the case that catches it: its entries are placed on
    the ROM's own fixed slots, so the mapping is nothing like the identity.
    """
    renderer, _ = _playing(select_crew=True)
    try:
        placement = renderer._panel_placement
        assert placement != list(range(len(placement))), (
            "this panel is identity-placed, so it proves nothing — pick another"
        )
        for index, row in enumerate(placement):
            if row is None:
                continue
            assert renderer.panel_entry_at(_window_pos(renderer, row)) == index
    finally:
        renderer.close()


def test_a_click_selects_a_crew_member() -> None:
    renderer, _ = _playing()
    try:
        entries = renderer._menu.entries()
        index = next(
            i for i, e in enumerate(entries)
            if e.selectable and e.select_crew is not None
            and renderer._panel_placement[i] is not None
        )
        assert renderer._menu.selected_crew is None
        renderer._pointer_down(
            _window_pos(renderer, renderer._panel_placement[index]), Screen.PLAYING
        )
        assert renderer._menu.selected_crew == entries[index].select_crew
    finally:
        renderer.close()


def test_a_click_fires_the_row_the_way_space_does() -> None:
    """One click is "cursor here, then fire" — the same path, not a second one.

    Checked through the border flash, which `_fire_menu` sets: if a click ever
    stopped going through it, the acknowledgement feedback would quietly stop and
    only a player would notice.
    """
    renderer, _ = _playing(select_crew=True)
    try:
        index = next(
            i for i, e in enumerate(renderer._menu.entries())
            if e.selectable and renderer._panel_placement[i] is not None
        )
        renderer._border_flash = 0
        renderer._pointer_down(
            _window_pos(renderer, renderer._panel_placement[index]), Screen.PLAYING
        )
        assert renderer._border_flash > 0, "a click did not go through _fire_menu"
    finally:
        renderer.close()


def test_clicks_that_should_do_nothing_do_nothing() -> None:
    """Headers, bare panel, the map side, outside the field, other screens."""
    renderer, _ = _playing(select_crew=True)
    try:
        menu = renderer._menu
        placement = renderer._panel_placement
        entries = menu.entries()
        rect = renderer.field_rect()
        before = menu.cursor

        header_row = next(
            placement[i] for i, e in enumerate(entries)
            if not e.selectable and placement[i] is not None
        )
        drawn = {r for r in placement if r is not None}
        empty_row = next(r for r in range(19) if r not in drawn)

        for pos in (
            _window_pos(renderer, header_row),        # a section label
            _window_pos(renderer, empty_row),         # panel row with no entry
            _window_pos(renderer, 2, col=4),          # the map, left of col 30
            (rect.x - 10, rect.y - 10),               # outside the field
        ):
            renderer._pointer_down(pos, Screen.PLAYING)
            assert menu.cursor == before

        # And the panel is only live on the play screen.
        renderer._pointer_down(_window_pos(renderer, 2), Screen.WELCOME)
        assert menu.cursor == before
    finally:
        renderer.close()


def _deliver(renderer: PygameRenderer, event: pygame.event.Event,
             screen: Screen = Screen.PLAYING) -> None:
    """Put one event through the real queue and the real `poll_input`."""
    pygame.event.clear()
    assert pygame.event.post(event), "the event queue refused the event"
    renderer.poll_input(screen)


def test_the_mouse_event_reaches_the_pointer_path() -> None:
    """The wiring: a left-button press must reach the pointer path."""
    renderer, _ = _playing()
    try:
        entries = renderer._menu.entries()
        index = next(
            i for i, e in enumerate(entries)
            if e.selectable and e.select_crew is not None
            and renderer._panel_placement[i] is not None
        )
        _deliver(renderer, pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1,
             "pos": _window_pos(renderer, renderer._panel_placement[index])},
        ))
        assert renderer._menu.selected_crew == entries[index].select_crew
    finally:
        renderer.close()


def test_only_the_left_button_fires() -> None:
    """The ROM has one fire control; the right button never selects/fires an
    entry, only left does (see `test_right_click_backs_out_a_selection` for
    what right-click *does* do)."""
    renderer, _ = _playing()
    try:
        index = next(
            i for i, e in enumerate(renderer._menu.entries())
            if e.selectable and renderer._panel_placement[i] is not None
        )
        _deliver(renderer, pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 3,
             "pos": _window_pos(renderer, renderer._panel_placement[index])},
        ))
        assert renderer._menu.selected_crew is None
    finally:
        renderer.close()


def test_right_click_backs_out_a_selection() -> None:
    """Owner's request: right-click should do what Escape already does during
    play - back out one level, so a mouse player can deselect a crew member
    and pick another without touching the keyboard. Not a new capability
    (DISC-262 already gives this to Escape); just a second way to reach it."""
    renderer, _ = _playing(select_crew=True)
    try:
        assert renderer._menu.selected_crew is not None, "test needs a selection"
        _deliver(renderer, pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 3, "pos": _window_pos(renderer, 2)},
        ))
        assert renderer._menu.selected_crew is None
    finally:
        renderer.close()


def test_right_click_does_nothing_off_the_play_screen() -> None:
    """Scoped to PLAYING, the same as Escape's own panel-backing-out branch -
    a right-click on a front-end screen has no ROM action to stand in for."""
    renderer, flow = _playing(select_crew=True)
    try:
        selected_before = renderer._menu.selected_crew
        _deliver(
            renderer,
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 3, "pos": _window_pos(renderer, 2)},
            ),
            screen=Screen.WELCOME,
        )
        assert renderer._menu.selected_crew == selected_before
    finally:
        renderer.close()


# --- P4: the front-end screens ------------------------------------------------

def _front(screen: Screen) -> tuple[PygameRenderer, GameFlow]:
    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = screen
    renderer.draw(flow)
    return renderer, flow


def _click_region(renderer: PygameRenderer, flow: GameFlow,
                  kind: str, index: int = 0) -> None:
    """Click the middle of a recorded region and apply what it queued."""
    renderer.draw(flow)
    region = next(
        (r for r, k, i in renderer._hot if k == kind and i == index), None
    )
    assert region is not None, f"nothing drew a {kind}/{index} region"
    rect = renderer.field_rect()
    scale = max(1, rect.width // _WIDTH)
    renderer._pending_input = []
    renderer._pointer_down(
        (rect.x + region.centerx * scale, rect.y + region.centery * scale),
        flow.screen,
    )
    for event in renderer._pending_input:
        flow.handle(event)


def test_each_chooser_row_does_what_its_key_does() -> None:
    """Clicking row N must equal pressing N — the same events, not new rules."""
    wanted = [Screen.OPENING, Screen.INTRO_PROMPT, Screen.MANUAL, Screen.OPTIONS]
    for index, expected in enumerate(wanted):
        renderer, flow = _front(Screen.GAME_SELECTION)
        try:
            _click_region(renderer, flow, "selection", index)
            assert flow.screen is expected, f"row {index}"
        finally:
            renderer.close()


def test_clicking_an_options_row_selects_it() -> None:
    renderer, flow = _front(Screen.OPTIONS)
    try:
        for index in range(len(flow.options.specs)):
            _click_region(renderer, flow, "option_row", index)
            assert flow.options.row == index
    finally:
        renderer.close()


def test_the_arrows_change_the_selected_row_both_ways() -> None:
    renderer, flow = _front(Screen.OPTIONS)
    try:
        flow.options.row = 1                       # CRT: three values
        spec = flow.options.spec
        start = flow.options.values[spec.key]
        _click_region(renderer, flow, "option_more", 1)
        assert flow.options.values[spec.key] != start
        _click_region(renderer, flow, "option_less", 1)
        assert flow.options.values[spec.key] == start, "left must undo right"
    finally:
        renderer.close()


def test_the_arrows_are_only_offered_on_the_selected_row() -> None:
    """They are drawn only there, so they must not be clickable elsewhere."""
    renderer, flow = _front(Screen.OPTIONS)
    try:
        flow.options.row = 1
        renderer.draw(flow)
        arrows = {
            i for _, k, i in renderer._hot
            if k in ("option_less", "option_more")
        }
        assert arrows == {1}
    finally:
        renderer.close()


def test_the_manual_pages_and_leaves_by_pointer() -> None:
    renderer, flow = _front(Screen.MANUAL)
    try:
        _click_region(renderer, flow, "manual_next")
        assert flow.manual_page == 1
        _click_region(renderer, flow, "manual_back")
        assert flow.manual_page == 0
        _click_region(renderer, flow, "manual_done")
        assert flow.screen is Screen.GAME_SELECTION
    finally:
        renderer.close()


def test_leaving_the_options_screen_by_pointer_commits() -> None:
    renderer, flow = _front(Screen.OPTIONS)
    saved: list[dict] = []
    flow.on_options_saved = saved.append
    try:
        _click_region(renderer, flow, "options_done")
        assert flow.screen is Screen.GAME_SELECTION
        assert saved, "leaving by pointer did not commit the options"
    finally:
        renderer.close()


# --- P5: hover ----------------------------------------------------------------

def test_hover_changes_the_picture_and_nothing_else() -> None:
    """A pointer resting on a row must never change a setting."""
    renderer, flow = _front(Screen.OPTIONS)
    try:
        before = dict(flow.options.values)
        row_before = flow.options.row

        renderer._hover = None
        renderer.draw(flow)
        plain = pygame.image.tobytes(renderer._surface, "RGB")

        renderer._hover = ("option_row", 4)
        renderer.draw(flow)
        hovered = pygame.image.tobytes(renderer._surface, "RGB")

        assert hovered != plain, "hover drew nothing"
        assert flow.options.values == before, "hover changed a setting"
        assert flow.options.row == row_before, "hover moved the cursor"
    finally:
        renderer.close()


def test_moving_the_pointer_records_what_it_is_over() -> None:
    renderer, flow = _front(Screen.GAME_SELECTION)
    try:
        region = next(
            r for r, k, i in renderer._hot if k == "selection" and i == 2
        )
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        renderer._pointer_motion(
            (rect.x + region.centerx * scale, rect.y + region.centery * scale)
        )
        assert renderer._hover == ("selection", 2)
        renderer._pointer_motion((rect.x - 20, rect.y - 20))
        assert renderer._hover is None, "off the field is not over anything"
    finally:
        renderer.close()


# --- P6: touch sizing ---------------------------------------------------------

def test_no_point_is_ever_claimed_by_two_regions() -> None:
    """The flaw the first attempt had, kept out by a test.

    Slop was originally applied by inflating every region. The rows are
    adjacent, so that made neighbours overlap and a near-miss landed on
    whichever was recorded first. It is a nearest-within-distance rule now, so
    every point has exactly one answer — swept here over the whole screen.
    """
    renderer, flow = _front(Screen.OPTIONS)
    try:
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        seen: dict[tuple[int, int], tuple[str, int] | None] = {}
        for cy in range(0, 200, 2):
            for cx in range(0, 320, 8):
                pos = (rect.x + cx * scale, rect.y + cy * scale)
                # Calling twice must agree: the answer is a function of the
                # position, not of iteration order.
                first = renderer._hot_at(pos)
                assert renderer._hot_at(pos) == first
                seen[(cx, cy)] = first
        assert any(v is not None for v in seen.values()), "nothing was hittable"
    finally:
        renderer.close()


def test_a_near_miss_lands_on_the_nearest_row() -> None:
    """Above the first row there is no neighbour to be ambiguous with, so the
    slop is doing exactly what it exists for."""
    renderer, flow = _front(Screen.OPTIONS)
    try:
        rows = sorted(
            ((r, i) for r, k, i in renderer._hot if k == "option_row"),
            key=lambda pair: pair[0].top,
        )
        first_rect, first_index = rows[0]
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        just_above = first_rect.top - 1
        hit = renderer._hot_at(
            (rect.x + first_rect.centerx * scale, rect.y + just_above * scale)
        )
        assert hit == ("option_row", first_index)
    finally:
        renderer.close()


def test_an_exact_hit_always_beats_a_nearby_one() -> None:
    renderer, flow = _front(Screen.OPTIONS)
    try:
        rows = sorted(
            ((r, i) for r, k, i in renderer._hot if k == "option_row"),
            key=lambda pair: pair[0].top,
        )
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        for region, index in rows:
            hit = renderer._hot_at(
                (rect.x + region.centerx * scale,
                 rect.y + region.centery * scale)
            )
            assert hit == ("option_row", index)
    finally:
        renderer.close()


# --- P7: the keyboard is untouched --------------------------------------------

def test_the_keyboard_still_drives_the_options_screen() -> None:
    """The pointer is a way *in*, never a replacement."""
    renderer, flow = _front(Screen.OPTIONS)
    try:
        flow.options.row = 0
        flow.handle(InputEvent.DOWN)
        assert flow.options.row == 1
        crt = flow.options.values["crt"]
        flow.handle(InputEvent.RIGHT)
        assert flow.options.values["crt"] != crt
        flow.handle(InputEvent.FIRE)
        assert flow.screen is Screen.GAME_SELECTION
    finally:
        renderer.close()


# --- the pointer is available in ORIGINAL -------------------------------------

# **Reversed 2026-08-29.** `test_the_pointer_works_under_the_original_preset`
# stood here and pinned the opposite rule: that ORIGINAL turned off remake-only
# *behaviours* while leaving the pointer, on the reasoning that an input device
# is not a rule change. The owner's later call is that ORIGINAL means the
# original machine too, which had no pointing device. The replacement is
# `test_first_run.py::test_the_pointer_is_dead_under_the_original_preset`, and
# there is still deliberately no `pointer` option row - the preset is the only
# thing that decides it.
