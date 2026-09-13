"""One-off script: render the six README screenshots the owner asked for.

Not part of the game or the toolkit - run by hand, from a checkout with
``out/`` already derived (``python -m alien_remake --derive-assets``), to
(re)generate ``docs/img/alien_attack.png``, ``docs/img/jones_running.png``,
``docs/img/narcissus.png``, ``docs/img/title_egg.png``, ``docs/img/duct_view.png``
and ``docs/img/crt_view_change.png``.

    python tools/readme_screenshots.py

Each scene reaches into ``PygameRenderer``'s own attributes directly rather
than driving input for however many ticks it would take to get there for
real - this is a screenshot tool, not a test of how those states are
reached (the existing test suite already covers that).
"""

from __future__ import annotations

import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from alien_remake.core import constants  # noqa: E402
from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.core.menu import MenuController  # noqa: E402
from alien_remake.core.nostromo import NARCISSUS  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render import crt as crt_mod  # noqa: E402
from alien_remake.render.crt import CrtSettings  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402
from alien_remake.render.tiles import load  # noqa: E402

OUT = Path("docs/img")


def _renderer(*, crt: CrtSettings | None = None) -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    return PygameRenderer(scale=2, tiles=tiles, intro_wav=None, crt=crt)


def _save(renderer: PygameRenderer, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pygame.image.save(renderer._surface, str(OUT / name))
    print(f"wrote {OUT / name}")


def _save_window(renderer: PygameRenderer, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pygame.image.save(renderer._window, str(OUT / name))
    print(f"wrote {OUT / name}")


def _playing(renderer: PygameRenderer) -> tuple[GameFlow, Simulation]:
    sim = Simulation(rng=random.Random(0))
    flow = GameFlow()
    flow.screen = Screen.PLAYING
    flow.sim = sim
    renderer._sim = sim
    renderer._ship = sim.ship
    renderer._menu = MenuController(sim)
    return flow, sim


def _select(renderer: PygameRenderer, crew_id: str) -> None:
    assert renderer._menu is not None
    renderer._menu.selected_crew = crew_id


def alien_attack() -> None:
    r = _renderer()
    flow, sim = _playing(r)
    victim = next(c for c in sim.state.crew.values() if c.alive)
    assert sim.state.alien is not None and victim.room_id is not None
    sim.state.alien.room_id = victim.room_id
    sim.state.alien.attack_sequence = True
    r._attacking = True
    r._attacking_crew_id = victim.id
    _select(r, victim.id)
    r.draw(flow)
    _save(r, "alien_attack.png")
    r.close()


def jones_running() -> None:
    r = _renderer()
    flow, sim = _playing(r)
    selected = next(c for c in sim.state.crew.values() if c.alive)
    _select(r, selected.id)
    # jones_run_armed just needs Jones in the selected crew member's room and
    # not caught; the animation itself is driven by `_jones_x` below.
    sim.state.jones_caught = False
    sim.state.jones_room_id = selected.room_id
    r._jones_x = 0x60  # mid-crossing, well clear of both edges
    r._jones_stop = False
    r.draw(flow)
    _save(r, "jones_running.png")
    r.close()


def narcissus() -> None:
    r = _renderer()
    flow, sim = _playing(r)
    selected = next(c for c in sim.state.crew.values() if c.alive)
    selected.room_id = NARCISSUS
    _select(r, selected.id)
    r.draw(flow)
    _save(r, "narcissus.png")
    r.close()


def title_egg() -> None:
    r = _renderer()
    flow = GameFlow()
    flow.screen = Screen.TITLE
    flow._screen_ticks = constants.TITLE_LETTER_TICKS * 6  # all 5 letters in
    r.draw(flow)
    _save(r, "title_egg.png")
    r.close()


def duct_view() -> None:
    r = _renderer()
    flow, sim = _playing(r)
    selected = next(c for c in sim.state.crew.values() if c.alive)
    selected.in_duct = True
    _select(r, selected.id)
    r.draw(flow)
    _save(r, "duct_view.png")
    r.close()


def crt_view_change() -> None:
    settings = CrtSettings(enabled=True)
    r = _renderer(crt=settings)
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    r.draw(flow)                     # builds the tube (_tube_layout / _crt)
    assert r._crt is not None
    r._crt.glitch(crt_mod.GLITCH_GENTLE)
    r._crt.advance(0.04)             # near the peak of the ~0.70s degauss
    r._paint()
    _save_window(r, "crt_view_change.png")
    r.close()


def main() -> None:
    alien_attack()
    jones_running()
    narcissus()
    title_egg()
    duct_view()
    crt_view_change()


if __name__ == "__main__":
    main()
