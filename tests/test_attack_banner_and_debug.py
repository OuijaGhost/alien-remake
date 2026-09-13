"""The Alien's row-23 banner, and the (non-original) debug marker overlay."""

from __future__ import annotations

import random
from pathlib import Path

import pygame
import pytest

from alien_remake.core.flow import GameFlow, Screen
from alien_remake.core.sim import Simulation
from alien_remake.render.pygame_app import PygameRenderer
from alien_remake.render.tiles import load
from alien_remake.screens import panels

import needs                                       # noqa: E402


@pytest.fixture
def renderer() -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    r = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    yield r
    r.close()


def _playing(renderer: PygameRenderer) -> tuple[GameFlow, Simulation]:
    sim = Simulation(rng=random.Random(0))
    flow = GameFlow()
    flow.screen = Screen.PLAYING
    flow.sim = sim
    renderer._sim = sim
    renderer._ship = sim.ship
    return flow, sim


def _playing_selecting(
    renderer: PygameRenderer, crew_id: str | None = None,
) -> tuple[GameFlow, Simulation]:
    """`_playing`, plus a real `MenuController` with `crew_id` selected.

    The composite is now driven purely by room co-location with whoever the
    menu has selected (owner's request, 2026-09-06, both presets — see
    `play.py`'s `render`), so exercising it needs a real selection, not just
    a bare `_attacking`/`_attacking_crew_id` poke.
    """
    from alien_remake.core.menu import MenuController

    flow, sim = _playing(renderer)
    renderer._menu = MenuController(sim)
    if crew_id is not None:
        renderer._menu.selected_crew = crew_id
    return flow, sim


def test_the_attack_banner_is_the_roms_own_string_and_geometry() -> None:
    """**[C $8BC4/$8D10] DISC-245** — 16 bytes at row 23 col 0, name at col 16."""
    assert panels.ATTACK_BANNER == "Alien attacking "
    assert len(panels.ATTACK_BANNER) == 16      # `CPX #$10`
    assert panels.ATTACK_BANNER_ROW == 23       # $0798 -> (0x398)/40
    assert panels.ATTACK_BANNER_NAME_COL == 16  # $07A8 -> 936 % 40


def test_the_banner_appears_whenever_the_selected_crew_shares_the_aliens_room(
    renderer: PygameRenderer,
) -> None:
    """**Not the ROM's own `$8CE1` gate — a deliberate departure, both
    presets** (owner's request, 2026-09-06; see DECISIONS.md). The composite
    is driven by plain room co-location with whoever is selected, with no
    attack roll or `attack_sequence` required at all — a player reported the
    Alien wounding two crew members with the animation never appearing once,
    because neither was selected at the moment the ROM's one-shot check ran.
    """
    flow, sim = _playing_selecting(renderer)
    victim = next(c for c in sim.state.crew.values() if c.alive)
    renderer._menu.selected_crew = victim.id  # type: ignore[union-attr]
    assert sim.state.alien is not None and victim.room_id is not None

    renderer.draw(flow)
    quiet = pygame.image.tobytes(renderer._surface, "RGB")
    assert renderer._attacking is False, "armed with the Alien nowhere near"

    sim.state.alien.room_id = victim.room_id  # co-located, no attack roll at all
    renderer.draw(flow)
    attacking = pygame.image.tobytes(renderer._surface, "RGB")

    assert renderer._attacking is True, "co-location alone should arm it"
    assert attacking != quiet, "the attack banner never reached the screen"


def test_the_banner_names_the_victim(renderer: PygameRenderer) -> None:
    """`$8D0D LDA $A65E,Y` copies ten name bytes in after the message — and
    now names whoever is selected, not a fixed victim (see the test above)."""
    flow, sim = _playing_selecting(renderer)
    living = [c for c in sim.state.crew.values() if c.alive]
    assert sim.state.alien is not None

    frames = []
    for victim in living[:2]:
        assert victim.room_id is not None
        sim.state.alien.room_id = victim.room_id
        renderer._menu.selected_crew = victim.id  # type: ignore[union-attr]
        renderer.draw(flow)
        frames.append(pygame.image.tobytes(renderer._surface, "RGB"))
    assert frames[0] != frames[1], "the banner did not change with the victim"


def test_attacking_clears_when_the_selected_crew_leaves_the_aliens_room(
    renderer: PygameRenderer,
) -> None:
    """Co-location is recomputed every frame, so it drops the moment either
    side moves away — no latch left to get stuck."""
    flow, sim = _playing_selecting(renderer)
    victim = next(c for c in sim.state.crew.values() if c.alive)
    renderer._menu.selected_crew = victim.id  # type: ignore[union-attr]
    other_room = next(
        r.id for r in sim.ship.rooms.values() if r.id != victim.room_id
    )
    assert sim.state.alien is not None and victim.room_id is not None

    sim.state.alien.room_id = victim.room_id
    renderer.draw(flow)
    assert renderer._attacking is True, "setup: co-location should arm it"

    victim.room_id = other_room
    renderer.draw(flow)
    assert renderer._attacking is False, (
        "the attack animation kept running after the victim left the "
        "Alien's room"
    )


def test_attacking_keeps_going_after_the_encounter_ends_if_still_co_located(
    renderer: PygameRenderer,
) -> None:
    """**Inverted from the ROM's own behaviour, on purpose (both presets).**
    `alien.attack_sequence` ending an encounter used to drop the composite
    outright; now presence is the only thing that matters, so a lingering
    Alien keeps showing even once its own attack_sequence flag has cleared.
    """
    flow, sim = _playing_selecting(renderer)
    victim = next(c for c in sim.state.crew.values() if c.alive)
    renderer._menu.selected_crew = victim.id  # type: ignore[union-attr]
    assert sim.state.alien is not None and victim.room_id is not None

    sim.state.alien.room_id = victim.room_id
    sim.state.alien.attack_sequence = True
    renderer.draw(flow)
    assert renderer._attacking is True, "setup: co-location should arm it"

    sim.state.alien.attack_sequence = False  # the encounter itself ended
    renderer.draw(flow)
    assert renderer._attacking is True, (
        "the composite dropped when only attack_sequence changed, even "
        "though the Alien is still standing in the room"
    )


def test_attacking_follows_a_switch_to_another_crew_member_in_the_same_room(
    renderer: PygameRenderer,
) -> None:
    """Owner's request, verbatim: "swapping to another character in the same
    room should show the animation." Two crew members share the Alien's
    room; switching the CONTROL panel between them keeps the composite up
    and relabels the banner, rather than needing a fresh attack to (re)start
    it."""
    flow, sim = _playing_selecting(renderer)
    assert sim.state.alien is not None
    room = next(iter(sim.ship.rooms))
    living = [c for c in sim.state.crew.values() if c.alive]
    assert len(living) >= 2
    first, second = living[0], living[1]
    first.room_id = room
    second.room_id = room
    sim.state.alien.room_id = room

    renderer._menu.selected_crew = first.id  # type: ignore[union-attr]
    renderer.draw(flow)
    assert renderer._attacking is True
    assert renderer._attacking_crew_id == first.id
    first_frame = pygame.image.tobytes(renderer._surface, "RGB")

    renderer._menu.selected_crew = second.id  # type: ignore[union-attr]
    renderer.draw(flow)
    assert renderer._attacking is True, (
        "switching to another crew member in the same room dropped the "
        "composite instead of following the switch"
    )
    assert renderer._attacking_crew_id == second.id
    second_frame = pygame.image.tobytes(renderer._surface, "RGB")

    assert first_frame != second_frame, "the banner did not follow the switch"


def test_debug_markers_are_off_by_default_and_inert(
    renderer: PygameRenderer,
) -> None:
    """The overlay is not the original: it must change nothing until asked.

    Off by default, and drawing with it off must be byte-identical to a
    renderer that has never heard of it.
    """
    flow, sim = _playing(renderer)
    assert renderer._debug_markers is False

    renderer.draw(flow)
    plain = pygame.image.tobytes(renderer._surface, "RGB")

    renderer._debug_markers = True
    renderer.draw(flow)
    marked = pygame.image.tobytes(renderer._surface, "RGB")

    renderer._debug_markers = False
    renderer.draw(flow)
    plain_again = pygame.image.tobytes(renderer._surface, "RGB")

    assert plain == plain_again, "the overlay leaked into the normal picture"
    # It only draws when the Alien or Jones is on the deck being viewed, so
    # find a deck where it actually shows something.
    if plain == marked:
        for deck in sim.ship.decks():
            sim.state.deck = deck
            renderer._debug_markers = False
            renderer.draw(flow)
            off = pygame.image.tobytes(renderer._surface, "RGB")
            renderer._debug_markers = True
            renderer.draw(flow)
            on = pygame.image.tobytes(renderer._surface, "RGB")
            if off != on:
                break
        else:
            pytest.fail("the overlay drew nothing on any deck")


def test_debug_markers_never_touch_the_simulation(
    renderer: PygameRenderer,
) -> None:
    """A debug view that changes play is not a debug view."""
    flow, sim = _playing(renderer)
    before = (
        sim.state.alien.room_id, sim.state.jones_room_id,
        {c.id: (c.room_id, c.alive, c.in_duct) for c in sim.state.crew.values()},
    )
    renderer._debug_markers = True
    for deck in sim.ship.decks():
        sim.state.deck = deck
        renderer.draw(flow)
    after = (
        sim.state.alien.room_id, sim.state.jones_room_id,
        {c.id: (c.room_id, c.alive, c.in_duct) for c in sim.state.crew.values()},
    )
    assert before == after


def test_the_portrait_survives_boarding_the_narcissus(
    renderer: PygameRenderer,
) -> None:
    """**[C $6667] DISC-245** — sprite 2 is independent of the deck plan.

    `place_selected_char_sprite` only writes sprite 2's position, pointer and
    colour; the VIC draws it over whatever is in the character screen. The
    Narcissus shows a cockpit instead of a deck plan (D-144), and the remake
    had the portrait buried inside `_draw_deck`, so boarding the shuttle took
    it away. The ROM never disables the sprite on that path.
    """
    # **REFERENCE too, found 2026-08-30 by installing into a fresh folder.**
    # The probe compares the portrait box against the same box with nobody
    # selected, and without the deck captures the Narcissus cockpit and the
    # blank fallback render alike - so the two boxes match and the test reports
    # a vanished portrait that is really an absent backdrop. A cold clone saw
    # this as a failure rather than a skip.
    needs.need(needs.CHARSET, needs.REFERENCE)
    from alien_remake.core.menu import MenuController
    from alien_remake.core.nostromo import NARCISSUS
    from alien_remake.render.play import _CHAR_PORTRAIT_AT

    flow, sim = _playing(renderer)
    renderer._menu = MenuController(sim)
    crew = next(c for c in sim.state.crew.values() if c.alive)
    renderer._menu.selected_crew = crew.id

    def portrait_box() -> bytes:
        x0, y0 = _CHAR_PORTRAIT_AT
        return bytes(
            v
            for x in range(x0, x0 + 24)
            for y in range(y0, y0 + 21)
            for v in tuple(renderer._surface.get_at((x, y)))[:3]
        )

    crew.room_id = "engine_2"
    sim.state.deck = sim.ship.rooms["engine_2"].deck
    renderer.draw(flow)
    on_deck = portrait_box()

    # In the shuttle the background changes, so compare against the portrait
    # being suppressed rather than against the deck frame.
    crew.room_id = NARCISSUS
    renderer.draw(flow)
    in_shuttle = portrait_box()

    renderer._menu.selected_crew = None      # nothing to draw a portrait for
    renderer.draw(flow)
    no_portrait = portrait_box()

    assert on_deck != no_portrait, "the probe box does not see the portrait"
    assert in_shuttle != no_portrait, (
        "the portrait vanished in the Narcissus cockpit"
    )


def _playing_with_menu(renderer: PygameRenderer):
    from alien_remake.core.menu import MenuController

    flow, sim = _playing(renderer)
    renderer._menu = MenuController(sim)
    return flow, sim


def test_the_debug_overlay_is_off_by_default_and_byte_identical(
    renderer: PygameRenderer,
) -> None:
    """Same contract as the marker overlay: not the original, so inert until asked."""
    flow, sim = _playing_with_menu(renderer)
    assert renderer._debug_markers is False

    renderer.draw(flow)
    plain = pygame.image.tobytes(renderer._surface, "RGB")
    renderer._debug_markers = True
    renderer.draw(flow)
    with_overlay = pygame.image.tobytes(renderer._surface, "RGB")
    renderer._debug_markers = False
    renderer._dbg_panel = None
    renderer.draw(flow)
    plain_again = pygame.image.tobytes(renderer._surface, "RGB")

    assert with_overlay != plain, "the overlay drew nothing"
    assert plain == plain_again, "the overlay leaked into the normal picture"


def test_the_overlay_never_touches_the_simulation(renderer: PygameRenderer) -> None:
    flow, sim = _playing_with_menu(renderer)
    before = (
        sim.state.tick, sim.state.alien.room_id, sim.state.jones_room_id,
        {c.id: (c.room_id, c.alive, c.fear) for c in sim.state.crew.values()},
    )
    renderer._debug_markers = True
    for _ in range(10):
        renderer.draw(flow)
    after = (
        sim.state.tick, sim.state.alien.room_id, sim.state.jones_room_id,
        {c.id: (c.room_id, c.alive, c.fear) for c in sim.state.crew.values()},
    )
    assert before == after


def test_the_frame_rate_readout_tracks_real_frame_intervals(
    renderer: PygameRenderer,
) -> None:
    """A readout that does not follow reality is worse than none.

    Fed a known interval, the reported fps must match it — this is measured
    from `_present` to `_present`, i.e. the whole frame *including* the
    overlay, so it reports what the player is getting rather than what the
    drawing code would like to claim.
    """
    import time

    flow, sim = _playing_with_menu(renderer)
    renderer._debug_markers = True
    for _ in range(25):
        renderer._debug_mark_input()
        renderer.draw(flow)
        time.sleep(0.02)                     # ~50 fps

    line = renderer._debug_lines(sim.state)[0]
    fps = float(line.split()[1])
    assert 35.0 < fps < 60.0, f"fps read {fps} for a ~50 fps feed: {line!r}"


def test_the_overlay_reports_the_real_mixer_and_memory(
    renderer: PygameRenderer,
) -> None:
    """The audio row must reflect the actual device, not a hardcoded guess."""
    from alien_remake.core import sound

    flow, sim = _playing_with_menu(renderer)
    renderer._sound(sound.GRILLE)
    renderer._debug_markers = True
    renderer.draw(flow)
    lines = renderer._debug_lines(sim.state)

    init = pygame.mixer.get_init()
    audio = next(ln for ln in lines if ln.startswith("audio"))
    if init is None:
        assert "off" in audio
    else:
        assert f"{init[0] // 1000}k/{init[2]}ch" in audio
        assert "clip" in audio

    memory = next(ln for ln in lines if ln.startswith("mem"))
    assert "n/a" in memory or "M" in memory


def test_the_overlay_costs_almost_nothing_per_frame(
    renderer: PygameRenderer,
) -> None:
    """It rebuilds at 4 Hz and blits a cached panel on every other frame.

    Composing it every frame measured 1.13 ms against a 0.75 ms draw — the
    debugger costing more than the thing being debugged. Guarded rather than
    just fixed, because the natural way to add a field is inside the compose.
    """
    import time

    flow, sim = _playing_with_menu(renderer)
    renderer._debug_markers = True
    renderer.draw(flow)                      # build the panel once

    t0 = time.perf_counter()
    for _ in range(40):
        renderer.draw(flow)
    with_overlay = (time.perf_counter() - t0) / 40

    renderer._debug_markers = False
    t0 = time.perf_counter()
    for _ in range(40):
        renderer.draw(flow)
    without = (time.perf_counter() - t0) / 40

    overhead_ms = (with_overlay - without) * 1000
    assert overhead_ms < 0.5, (
        f"the overlay adds {overhead_ms:.2f} ms a frame; it should be blitting "
        "a cached panel, not re-composing one"
    )


def test_the_overlay_distinguishes_a_ducted_alien(renderer: PygameRenderer) -> None:
    """**DISC-257** — a ducted creature is in a different space, and must look it.

    The duct network is a separate graph reached through the compass tables
    (`$81EF`, D-086), so an Alien crawling it moves between rooms that share no
    door. That is correct behaviour, but the overlay drew it in the same colour
    as a surfaced one, which made it look like teleporting — a player watching
    debug mode reported exactly that.
    """
    flow, sim = _playing_with_menu(renderer)
    assert sim.state.alien is not None
    alien = sim.state.alien
    alien.room_id = next(iter(sim.ship.rooms))
    sim.state.deck = sim.ship.rooms[alien.room_id].deck
    renderer._debug_markers = True

    alien.in_duct = False
    renderer._dbg_panel = None
    surfaced_line = renderer._debug_lines(sim.state)[1]
    renderer.draw(flow)
    surfaced_px = pygame.image.tobytes(renderer._surface, "RGB")

    alien.in_duct = True
    renderer._dbg_panel = None
    ducted_line = renderer._debug_lines(sim.state)[1]
    renderer.draw(flow)
    ducted_px = pygame.image.tobytes(renderer._surface, "RGB")

    assert surfaced_line.endswith("room")
    assert ducted_line.endswith("DUCT")
    assert surfaced_px != ducted_px, (
        "the marker looks identical in both spaces — this is what made duct "
        "movement read as teleporting"
    )


def test_a_ducted_alien_really_does_move_between_roomless_doors() -> None:
    """The behaviour behind the report, asserted so it is not 'fixed' later.

    Rooms the duct connects are *not* door neighbours. That is the point of the
    ducting (D-086) and the reason the overlay had to say which space it is in.
    """
    import random

    from alien_remake.core.flow import default_simulation
    from alien_remake.core.modes import DeathVariant, GameMode

    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    sim.rng = random.Random(3)
    alien = sim.state.alien
    assert alien is not None

    previous = (alien.room_id, alien.in_duct)
    duct_hops = no_door_surfaced = 0
    for _ in range(3000):
        sim.advance()
        current = (alien.room_id, alien.in_duct)
        if current != previous:
            (r0, d0), (r1, d1) = previous, current
            if r0 != r1:
                if d0 or d1:
                    duct_hops += 1
                elif r1 not in sim.ship.door_neighbors(r0):
                    no_door_surfaced += 1
            previous = current
        if sim.state.phase.name != "RUNNING":
            break

    assert duct_hops > 0, "the Alien never used the ducts in 3000 ticks"
    assert no_door_surfaced == 0, (
        f"{no_door_surfaced} surfaced hops between rooms with no door — that "
        "would be a real movement bug, not duct travel"
    )
