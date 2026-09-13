"""Click a room to move there, and the box that shows which (M1-M6).

The rule the owner asked for is the one worth pinning: **the clickable rooms
are exactly the ones the panel offers**, so a click can never send someone
somewhere the menu would not have let you pick. That set is read from the
panel rather than re-derived, and these tests hold the two together.
"""

from __future__ import annotations

import hashlib
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from alien_remake import assets  # noqa: E402
from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.core.menu import MenuController  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render.layout import _WIDTH  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


def _playing(seed: int = 7, select: bool = True):
    """The play screen with a commandable crew member selected, drawn once.

    Seeded, and the crew member is *found* rather than named: the opening kills
    someone at random and `entries()` re-derives commandability every frame
    (D-158), so naming one gives a different panel on different seeds.
    """
    tiles = None
    charset = assets.find("charset.bin")
    if charset is not None:
        from alien_remake.render.tiles import load as load_tiles

        tiles = load_tiles(charset)
    renderer = PygameRenderer(scale=3, intro_wav=None, tiles=tiles)
    sim = Simulation(rng=random.Random(seed))
    flow = GameFlow()
    flow.screen, flow.sim = Screen.PLAYING, sim
    renderer._menu = MenuController(sim)
    renderer._sim, renderer._ship = sim, sim.ship
    renderer.draw(flow)
    if select:
        for entry in renderer._menu.entries():
            if entry.select_crew is None:
                continue
            renderer._menu.selected_crew = entry.select_crew
            if renderer._menu.entries()[0].label != "CONTROL":
                break
            renderer._menu.selected_crew = None
        renderer.draw(flow)
    return renderer, flow


def _rooms(renderer: PygameRenderer) -> list[tuple[pygame.Rect, int]]:
    return [(r, i) for r, k, i in renderer._hot if k == "room"]


def _click(renderer: PygameRenderer, rect: pygame.Rect, flow: GameFlow) -> None:
    field = renderer.field_rect()
    scale = max(1, field.width // _WIDTH)
    renderer._pointer_down(
        (field.x + rect.centerx * scale, field.y + rect.centery * scale),
        flow.screen,
    )


def _hover(renderer: PygameRenderer, rect: pygame.Rect) -> None:
    field = renderer.field_rect()
    scale = max(1, field.width // _WIDTH)
    renderer._pointer_motion(
        (field.x + rect.centerx * scale, field.y + rect.centery * scale)
    )


# --- M2/M5: only what the panel offers ---------------------------------------

def test_the_clickable_rooms_are_the_panel_s_own_destinations() -> None:
    """The owner's rule, asserted directly."""
    renderer, flow = _playing()
    try:
        destinations = renderer._menu.move_destinations()
        entries = renderer._menu.entries()
        clickable = {
            entries[i].order.target for _, i in _rooms(renderer)
            if entries[i].order is not None
        }
        on_deck = {
            room for room in destinations
            if renderer._ship.rooms[room].deck == renderer._view_deck
        }
        assert clickable == on_deck
        assert clickable, "nothing was clickable, so this proves nothing"
    finally:
        renderer.close()


def test_no_selection_means_no_clickable_rooms() -> None:
    """M5. With nobody picked there are no destinations, so no regions, so a
    click on the map cannot pick someone implicitly."""
    renderer, flow = _playing(select=False)
    try:
        assert renderer._menu.selected_crew is None
        assert _rooms(renderer) == []
    finally:
        renderer.close()


def test_a_room_the_panel_does_not_offer_is_inert() -> None:
    renderer, flow = _playing()
    try:
        offered = {
            renderer._menu.entries()[i].order.target for _, i in _rooms(renderer)
        }
        others = [
            room for room, r in renderer._ship.rooms.items()
            if r.deck == renderer._view_deck and room not in offered
        ]
        assert others, "every room on this deck is offered; pick another seed"
        before = renderer._menu.cursor
        field = renderer.field_rect()
        scale = max(1, field.width // _WIDTH)
        for room in others[:5]:
            far = renderer._ship.rooms[room]
            renderer._pointer_down(
                (field.x + int(far.x * 8 + 4) * scale,
                 field.y + int(far.y * 8 + 4) * scale),
                Screen.PLAYING,
            )
        assert renderer._menu.cursor == before
    finally:
        renderer.close()


def test_a_destination_on_another_deck_is_not_clickable() -> None:
    """The measured caveat: 6 of 72 destinations are up or down a ladder.

    The map shows one deck, so those can never be clicked — the panel stays the
    way to reach them, and this asserts the map does not pretend otherwise.

    **The case is set up deliberately, not hoped for.** Written against a seed
    first, it passed while proving nothing: every crew member happened to start
    somewhere with a single same-deck destination, so the loop body never ran.
    `corridor_1` is one of the six rooms that genuinely has a ladder.
    """
    renderer, flow = _playing()
    try:
        crew_id = renderer._menu.selected_crew
        assert crew_id is not None
        flow.sim.state.crew[crew_id].room_id = "corridor_1"
        renderer._view_deck = renderer._ship.rooms["corridor_1"].deck
        renderer.draw(flow)

        destinations = renderer._menu.move_destinations()
        cross = [
            room for room in destinations
            if renderer._ship.rooms[room].deck != renderer._view_deck
        ]
        assert cross, "this room was supposed to have a ladder"

        entries = renderer._menu.entries()
        clickable = {entries[i].order.target for _, i in _rooms(renderer)}
        for room in cross:
            assert room not in clickable, f"{room} is off-deck but clickable"
            assert room in destinations, "the panel must still offer it"
    finally:
        renderer.close()


# --- M3: one path to an order ------------------------------------------------

def test_clicking_a_room_orders_the_same_move_the_menu_would() -> None:
    """Same entry, so the PCS gate, the countdown and the journal all agree."""
    def run(by_mouse: bool) -> tuple[int, str | None]:
        renderer, flow = _playing()
        try:
            crew_id = renderer._menu.selected_crew
            assert crew_id is not None
            rect, index = _rooms(renderer)[0]
            target = renderer._menu.entries()[index].order.target
            if by_mouse:
                _click(renderer, rect, flow)
            else:
                renderer._menu.select_index(index)
                renderer._menu.fire()
            timer = flow.sim.state.crew[crew_id].step_timer
            for _ in range(200):
                flow.sim.advance()
            return timer, flow.sim.state.crew[crew_id].room_id
        finally:
            renderer.close()

    assert run(True) == run(False)


def test_the_click_actually_moves_them_there() -> None:
    renderer, flow = _playing()
    try:
        crew_id = renderer._menu.selected_crew
        rect, index = _rooms(renderer)[0]
        target = renderer._menu.entries()[index].order.target
        assert flow.sim.state.crew[crew_id].room_id != target
        _click(renderer, rect, flow)
        for _ in range(200):
            flow.sim.advance()
        assert flow.sim.state.crew[crew_id].room_id == target
    finally:
        renderer.close()


# --- M4: the box that shows which room --------------------------------------

def test_hovering_a_room_marks_it_without_moving_the_cursor() -> None:
    """Hover changes the picture and nothing else (P5).

    Moving the cursor would change what the space bar fires, so a mouse resting
    on the map must not redirect the keyboard.
    """
    renderer, flow = _playing()
    try:
        rect, index = _rooms(renderer)[0]
        target = renderer._menu.entries()[index].order.target
        before = renderer._menu.cursor
        _hover(renderer, rect)
        assert renderer._menu.hovered_room_id == target
        assert renderer._menu.cursor == before
    finally:
        renderer.close()


def test_the_mark_clears_when_the_pointer_leaves() -> None:
    renderer, flow = _playing()
    try:
        rect, _ = _rooms(renderer)[0]
        _hover(renderer, rect)
        assert renderer._menu.hovered_room_id is not None
        field = renderer.field_rect()
        renderer._pointer_motion((field.x - 40, field.y - 40))
        assert renderer._menu.hovered_room_id is None
    finally:
        renderer.close()


@pytest.mark.skipif(
    assets.find("charset.bin") is None, reason="no charset -> no sprites to draw"
)
def test_the_marker_over_a_hovered_room_is_animated() -> None:
    """The owner asked for an animated rectangle, and the ROM already has one.

    `$4FCB` cycles five sprite slots that decode to concentric expanding boxes
    (D-082) — the same animation the cursor's own destination preview uses
    (P4-2). Hovering drives that rather than a second one drawn alongside, so
    this asserts the frames actually differ.
    """
    from alien_remake.render.play import _POINTER_FRAMES, _POINTER_RATE

    renderer, flow = _playing()
    try:
        rect, _ = _rooms(renderer)[0]
        _hover(renderer, rect)
        seen = set()
        for step in range(len(_POINTER_FRAMES)):
            renderer._frame_count = step * _POINTER_RATE
            renderer.draw(flow)
            seen.add(hashlib.md5(
                pygame.image.tobytes(renderer._surface, "RGB")
            ).hexdigest())
        assert len(seen) > 1, "the hover marker did not animate"
    finally:
        renderer.close()


# --- W1-W6: the wheel, and aiming by hover ------------------------------------

def test_the_wheel_changes_floor_and_clamps() -> None:
    """W1. Up means up: deck 0 is the upper deck, so scrolling up lowers the
    number. Clamped rather than wrapped — a jump from the top of the ship to
    the bottom reads as a glitch."""
    renderer, flow = _playing()
    try:
        decks = sorted(flow.sim.ship.decks())
        for _ in range(len(decks) + 2):
            renderer._pointer_wheel(1, Screen.PLAYING)
        assert flow.sim.state.deck == decks[0]
        for _ in range(len(decks) + 2):
            renderer._pointer_wheel(-1, Screen.PLAYING)
        assert flow.sim.state.deck == decks[-1]
    finally:
        renderer.close()


def test_a_scrolled_deck_survives_being_drawn() -> None:
    """The obstacle W1 actually had.

    The view follows the selected crew member's deck, which the ROM does every
    pass ($511C). Re-asserting it every frame undid a scroll before it could be
    drawn — which is exactly when a player wants another floor.
    """
    renderer, flow = _playing()
    try:
        renderer.draw(flow)
        before = flow.sim.state.deck
        renderer._pointer_wheel(1, Screen.PLAYING)
        scrolled = flow.sim.state.deck
        if scrolled == before:                       # already on the top deck
            renderer._pointer_wheel(-1, Screen.PLAYING)
            scrolled = flow.sim.state.deck
        assert scrolled != before
        renderer.draw(flow)
        renderer.draw(flow)
        assert flow.sim.state.deck == scrolled, "the scroll was undone"
    finally:
        renderer.close()


def test_the_selected_character_takes_the_view_back_when_they_move() -> None:
    """The override is a look, not a mode. Any move hands the view back —
    keyed on the room rather than the deck, or the map sat on the wrong floor
    until they happened to change floor."""
    renderer, flow = _playing()
    try:
        crew_id = renderer._menu.selected_crew
        assert crew_id is not None
        renderer.draw(flow)
        home = flow.sim.state.deck
        renderer._pointer_wheel(1, Screen.PLAYING)
        if flow.sim.state.deck == home:
            renderer._pointer_wheel(-1, Screen.PLAYING)
        renderer.draw(flow)
        assert flow.sim.state.deck != home

        elsewhere = next(
            r for r in flow.sim.ship.rooms.values()
            if r.deck == home and r.id != flow.sim.state.crew[crew_id].room_id
        )
        flow.sim.state.crew[crew_id].room_id = elsewhere.id
        renderer.draw(flow)
        assert flow.sim.state.deck == home, "moving did not reclaim the view"
    finally:
        renderer.close()


def test_hovering_aims_the_cursor() -> None:
    """W2, reversing M4 on the owner's call. The consequence is the point:
    after hovering, the space bar fires *that* room."""
    renderer, flow = _playing()
    try:
        rect, index = _rooms(renderer)[0]
        target = renderer._menu.entries()[index].order.target
        _hover(renderer, rect)
        aimed = renderer._menu.entries()[renderer._menu.current_index()]
        assert aimed.order is not None and aimed.order.target == target
    finally:
        renderer.close()


def test_aiming_by_hover_is_silent() -> None:
    """No cue as the pointer crosses rooms — a blip per room would be a
    machine-gun, and the aim is not an action."""
    renderer, flow = _playing()
    played: list[str] = []
    renderer._ui_sound = True
    renderer._samples = type(
        "P", (), {"play": lambda s, n: played.append(n) or True,
                  "load": lambda s, n: None},
    )()
    try:
        renderer.draw(flow)
        played.clear()
        for rect, _ in _rooms(renderer):
            _hover(renderer, rect)
            renderer.draw(flow)
        assert played == [], f"hovering made a noise: {played}"
    finally:
        renderer.close()


def test_a_room_on_another_floor_can_be_reached_by_scrolling() -> None:
    """W3/W4 — the whole point of the wheel.

    A ladder destination could be ordered from the panel but never clicked,
    because the map only ever showed one deck. Scroll to its floor and it is
    drawn, so it is clickable, marked and orderable like any other.
    """
    renderer, flow = _playing()
    try:
        crew_id = renderer._menu.selected_crew
        flow.sim.state.crew[crew_id].room_id = "corridor_1"
        renderer.draw(flow)

        cross = [
            room for room in renderer._menu.move_destinations()
            if renderer._ship.rooms[room].deck != flow.sim.state.deck
        ]
        assert cross, "corridor_1 was supposed to have a ladder"
        target = cross[0]
        want = renderer._ship.rooms[target].deck

        for _ in range(len(flow.sim.ship.decks()) + 2):
            if flow.sim.state.deck == want:
                break
            renderer._pointer_wheel(1 if want < flow.sim.state.deck else -1,
                                    Screen.PLAYING)
        assert flow.sim.state.deck == want
        renderer.draw(flow)

        entries = renderer._menu.entries()
        rect = next(
            r for r, k, i in renderer._hot
            if k == "room" and entries[i].order.target == target
        )
        _hover(renderer, rect)
        assert renderer._menu.hovered_room_id == target

        _click(renderer, rect, flow)
        for _ in range(400):
            flow.sim.advance()
        assert flow.sim.state.crew[crew_id].room_id == target
    finally:
        renderer.close()


def test_the_narcissus_still_cannot_be_scrolled_to() -> None:
    """The one destination the wheel does not reach.

    The Narcissus sits on a sentinel deck that `ship.decks()` does not list, so
    `select_deck` refuses it and the map can never show it. Five of the six
    ladder destinations became clickable; this is the sixth, and the panel
    stays the way there.
    """
    renderer, flow = _playing()
    try:
        assert renderer._ship.rooms["narcissus"].deck not in flow.sim.ship.decks()
        assert flow.sim.select_deck(renderer._ship.rooms["narcissus"].deck) is False
    finally:
        renderer.close()


def test_the_wheel_moves_the_options_cursor_too() -> None:
    """W5. A wheel that works on one screen and is dead on the next feels
    broken."""
    from alien_remake.core.flow import GameFlow as _Flow

    renderer = PygameRenderer(scale=2, intro_wav=None)
    flow = _Flow()
    flow.screen = Screen.OPTIONS
    try:
        renderer.draw(flow)
        before = flow.options.row
        renderer._pending_input = []
        renderer._pointer_wheel(-1, Screen.OPTIONS)
        for event in renderer._pending_input:
            flow.handle(event)
        assert flow.options.row != before
    finally:
        renderer.close()
