"""Two bugs the owner hit in play on 2026-08-30, and the log that settled one.

Both were in the *presentation*: the simulation had it right in each case, which
is why the session log was what distinguished "the game is wrong" from "the
screen is lying about it".
"""

from __future__ import annotations

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from alien_remake.core import menu as menu_mod  # noqa: E402
from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.core.menu import MenuController  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render.layout import _WIDTH  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


# --- 1. the catch renames the catching item, not every cat box --------------------

def _caught_with(type_id: str) -> tuple[Simulation, str]:
    """A run where Jones is in the item of this type, and someone else has the
    other one."""
    sim = Simulation(rng=random.Random(4))
    item = next(i for i in sim.state.items.values() if i.type_id == type_id)
    sim.state.jones_caught = True
    sim.state.jones_container_id = item.id
    sim.state.jones_room_id = None
    return sim, item.id


def test_the_net_that_caught_him_says_so() -> None:
    """Owner: "when ripley caught jones with the net, the Catbox ash was
    carrying changed to Jones: Box."

    `$87B6` copies "Jones:Net" and `$87D7` "Jones:Box" - two labels, applied to
    whichever item made the catch.
    """
    sim, net_id = _caught_with("net")
    assert menu_mod._item_label("net", sim.state, net_id) == menu_mod.JONES_NET_LABEL


def test_a_box_that_caught_him_still_says_box() -> None:
    sim, box_id = _caught_with("cat_box")
    assert menu_mod._item_label("cat_box", sim.state, box_id) == menu_mod.JONES_BOX_LABEL


def test_someone_elses_box_is_not_renamed() -> None:
    """The actual complaint: a cat box on the other side of the ship announced
    it had the cat, because the old test was on the item's *type*."""
    sim, net_id = _caught_with("net")
    box = next(i for i in sim.state.items.values() if i.type_id == "cat_box")
    assert box.id != net_id
    assert menu_mod._item_label("cat_box", sim.state, box.id) == "Cat Box"


def test_nothing_is_renamed_before_the_catch() -> None:
    sim = Simulation(rng=random.Random(4))
    for type_id, plain in (("net", "Net"), ("cat_box", "Cat Box")):
        item = next(i for i in sim.state.items.values() if i.type_id == type_id)
        assert menu_mod._item_label(type_id, sim.state, item.id) == plain


def test_without_an_item_id_it_does_not_guess() -> None:
    """A wrong "Jones:" on the wrong row is worse than no marker - the panel is
    the only place the original tells you where the cat is."""
    sim, net_id = _caught_with("net")
    assert menu_mod._item_label("net", sim.state, None) == "Net"


def test_the_panel_row_carries_the_label() -> None:
    """End to end, since the label being right in isolation is not the bug."""
    sim, net_id = _caught_with("net")
    holder = next(c for c in sim.state.crew.values() if c.alive and c.awake)
    net = sim.state.items[net_id]
    net.room_id, net.holder = None, holder.id
    holder.carried.append(net.id)
    holder.holding = net.id
    control = MenuController(sim)
    control.selected_crew = holder.id
    labels = [e.label for e in control.entries()]
    assert menu_mod.JONES_NET_LABEL in labels, labels


# --- 2. hovering a room highlights that room ----------------------------------------

def _playing() -> tuple[PygameRenderer, GameFlow, Simulation]:
    renderer = PygameRenderer(scale=3, intro_wav=None)
    sim = Simulation(rng=random.Random(7))
    flow = GameFlow()
    flow.screen, flow.sim = Screen.PLAYING, sim
    renderer._menu = MenuController(sim)
    renderer._sim, renderer._ship = sim, sim.ship
    for entry in renderer._menu.entries():
        if entry.select_crew is None:
            continue
        renderer._menu.selected_crew = entry.select_crew
        if renderer._menu.entries()[0].label != "CONTROL":
            break
        renderer._menu.selected_crew = None
    renderer.draw(flow)
    return renderer, flow, sim


def test_hovering_a_rooms_marker_picks_that_room() -> None:
    """Owner: "I can generally move the mouse to the top left to highlight a
    room, but the actual room to the top left doesn't highlight."

    The boxes were laid on the internal grid (`ox + room.x * cell_w`) while the
    map and every marker on it come from the ROM's decoded table
    (`$758D`/`$75B1`). Two different layouts, so a room's box sat nowhere near
    the room.
    """
    renderer, _flow, sim = _playing()
    try:
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        checked = 0
        for room_id, index in renderer._menu.move_destinations().items():
            room = sim.ship.rooms.get(room_id)
            if room is None or room.deck != renderer._view_deck:
                continue
            at = renderer._room_marker_px(room_id)
            if at is None:
                continue
            centre = (rect.x + int((at[0] + 12) * scale),
                      rect.y + int((at[1] + 10) * scale))
            hit = renderer._hot_at(centre)
            assert hit == ("room", index), (
                f"hovering {room_id}'s own marker picked {hit}"
            )
            checked += 1
        assert checked, "no on-deck destination to check"
    finally:
        renderer.close()


def test_the_hot_box_is_the_size_of_the_marker_you_see() -> None:
    """A C64 hardware sprite is 24x21, and that is what is drawn - so that is
    what should be hoverable."""
    from alien_remake.render.play import _MARKER_H, _MARKER_W

    assert (_MARKER_W, _MARKER_H) == (24, 21)
    renderer, _flow, sim = _playing()
    try:
        rooms = [(r, k, i) for r, k, i in renderer._hot if k == "room"]
        if not rooms:
            return
        for rect_, _kind, _index in rooms:
            assert (rect_.width, rect_.height) == (_MARKER_W, _MARKER_H)
    finally:
        renderer.close()


def test_a_synthetic_map_still_falls_back_to_the_grid() -> None:
    """`_room_marker_px` returns None for rooms outside the real 36-entry
    table, and the grid is what those tests have."""
    renderer, _flow, _sim = _playing()
    try:
        assert renderer._room_marker_px("not_a_real_room") is None
    finally:
        renderer.close()
