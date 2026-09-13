"""D5 and D1 — the two slots that stopped being "not replaceable yet".

`test_media_dictionary.py` covers the dictionary's shape: that it is generated
from the loaders, that nothing is listed twice, that nothing is both
replaceable and not. These cover the two slots themselves, and the thing that
shape alone cannot check — **that a file you supply is actually the one drawn
and played.**

That gap is the whole risk here. A dictionary that lists `portraits/ash.png`
and a renderer that never opens it would pass every test in the other file and
be a lie in the one way that matters.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from alien_remake import assets, media  # noqa: E402
import pathlib  # noqa: E402

from alien_remake.core.crew import ROSTER  # noqa: E402
from alien_remake.core.nostromo import DECK_NAMES  # noqa: E402
from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.render import c64  # noqa: E402
from alien_remake.render.frontend import _PORTRAIT_X, _PORTRAIT_Y  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


# --- D5: the intro tune -------------------------------------------------------

def test_the_intro_is_no_longer_called_unreplaceable() -> None:
    """It never really was.

    `assets.find` has always taken the first `intro.wav` on the root path, so a
    supplied tune already played. The dictionary listed it as a thing to
    generate and, further down, said music could not be replaced at all — two
    statements that could not both be true, and the second was the wrong one.
    """
    unswappable = {name for name, _ in media.NOT_YET}
    assert "music" not in unswappable
    assert "intro" in {slot.key for slot in media.slots()}


def test_the_intro_slot_says_you_may_supply_your_own() -> None:
    slot = next(s for s in media.slots() if s.key == "intro")
    assert slot.swap, "the intro does not say a supplied file replaces it"
    assert "intro.wav" in slot.swap


def test_the_report_prints_what_a_supplied_file_does() -> None:
    text = media.describe()
    assert "yours instead:" in text


def test_the_swap_note_is_wrapped_to_fit() -> None:
    """The first version wrapped to 60 columns and then indented 42, so it ran
    to 102 and off the terminal. Measured against the printed line, not the
    string it was wrapped from."""
    for line in media.describe().splitlines():
        if line.strip().startswith(("drop your own", "and it plays", "length,")):
            assert len(line) <= media._REPORT_WIDTH, line


def test_only_slots_with_a_story_claim_one() -> None:
    """An empty `swap` is the honest answer for a slot nobody has worked out
    the substitution story for. It must not read as "cannot be swapped"."""
    swappable = {s.key for s in media.slots() if s.swap}
    assert swappable == set(media.SWAPPABLE)
    for key in media.SWAPPABLE:
        assert key in {k for k, *_ in assets.KNOWN_ASSETS}, key


# --- D1: crew portraits -------------------------------------------------------

def test_every_crew_member_has_a_portrait_slot() -> None:
    keys = {slot.key for slot in media.slots()}
    for crew_id, _name, _role in ROSTER:
        assert f"portrait/{crew_id}" in keys, crew_id


def test_the_portrait_slots_come_from_the_roster() -> None:
    """Enumerated, not listed — a crew change cannot leave this describing six
    portraits or eight."""
    slots = [s for s in media.slots() if s.key.startswith("portrait/")]
    assert len(slots) == len(ROSTER)


def test_portraits_are_no_longer_called_unreplaceable() -> None:
    assert "portraits" not in {name for name, _ in media.NOT_YET}


def test_a_portrait_is_found_where_the_dictionary_says_it_is(
    tmp_path, monkeypatch
) -> None:
    """The dictionary and the loader must name the same folder. They share the
    function, so this fails only if someone splits them apart."""
    folder = tmp_path / media.PORTRAIT_DIR
    folder.mkdir()
    target = folder / f"ash{media.PORTRAIT_EXT}"
    pygame.image.save(pygame.Surface((8, 8)), str(target))
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    assert media.portrait_path("ash") == target
    slot = next(s for s in media.slots() if s.key == "portrait/ash")
    assert slot.status == "present"
    assert slot.where == f"{media.PORTRAIT_DIR}/ash{media.PORTRAIT_EXT}"


def _supply(tmp_path, monkeypatch, crew_id: str,
            colour: tuple[int, int, int]) -> None:
    """Write a flat, unmistakable portrait for one crew member."""
    folder = tmp_path / media.PORTRAIT_DIR
    folder.mkdir(exist_ok=True)
    art = pygame.Surface((48, 42))
    art.fill(colour)
    pygame.image.save(art, str(folder / f"{crew_id}{media.PORTRAIT_EXT}"))
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])


def test_a_supplied_portrait_is_the_one_drawn(tmp_path, monkeypatch) -> None:
    """The test the dictionary's shape cannot do: the file reaches the screen.

    A dictionary that lists `portraits/ash.png` and a renderer that never opens
    it would pass every other test here and still be a lie.
    """
    _supply(tmp_path, monkeypatch, "ash", (255, 0, 0))
    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    try:
        renderer.draw(flow)
        # Ash is fourth left to right; the sprite is centred on its slot.
        index = next(i for i, (cid, *_) in enumerate(ROSTER) if cid == "ash")
        at = (_PORTRAIT_X[index] + 12, _PORTRAIT_Y + 10)
        assert renderer._surface.get_at(at)[:3] == (255, 0, 0)
    finally:
        renderer.close()


def test_a_portrait_is_scaled_to_the_decoded_sprite_size(
    tmp_path, monkeypatch
) -> None:
    """Drawn native, a large image would cover its neighbours — and the layout
    it would break is decoded (`_PORTRAIT_X`, 40px apart), not a choice."""
    _supply(tmp_path, monkeypatch, "ash", (255, 0, 0))
    renderer = PygameRenderer(scale=3, intro_wav=None)
    try:
        surface = renderer._portrait_surface("ash")
        assert surface is not None
        assert surface.get_size() == media.PORTRAIT_SIZE
    finally:
        renderer.close()


def test_a_neighbour_without_a_portrait_is_untouched(
    tmp_path, monkeypatch
) -> None:
    """One supplied portrait must not disturb the six drawn from the ROM."""
    _supply(tmp_path, monkeypatch, "ash", (255, 0, 0))
    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    try:
        renderer.draw(flow)
        for crew_id in ("ripley", "lambert"):
            index = next(
                i for i, (cid, *_) in enumerate(ROSTER) if cid == crew_id
            )
            at = (_PORTRAIT_X[index] + 12, _PORTRAIT_Y + 10)
            assert renderer._surface.get_at(at)[:3] != (255, 0, 0)
    finally:
        renderer.close()


def test_no_portraits_folder_draws_exactly_what_it_drew_before(
    tmp_path, monkeypatch
) -> None:
    """The decoded sprite stays the default: an install with no folder is
    unchanged, which is the whole reason this is an override and not a
    replacement."""
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    renderer = PygameRenderer(scale=3, intro_wav=None)
    try:
        assert renderer._portrait_surface("ash") is None
    finally:
        renderer.close()


def test_a_corrupt_portrait_falls_back_rather_than_crashing(
    tmp_path, monkeypatch
) -> None:
    """Somebody's bad PNG is not a reason for the game to stop."""
    folder = tmp_path / media.PORTRAIT_DIR
    folder.mkdir()
    (folder / f"ash{media.PORTRAIT_EXT}").write_bytes(b"not a png at all")
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    try:
        assert renderer._portrait_surface("ash") is None
        renderer.draw(flow)          # must not raise
    finally:
        renderer.close()


def test_the_miss_is_cached_too(tmp_path, monkeypatch) -> None:
    """A roster with no portraits costs seven searches once, not seven a
    frame."""
    calls = []

    def counting(*parts: str):
        calls.append(parts)
        return None

    # Patched *after* construction: building the renderer looks for
    # `chargen.bin`, and counting that made the first version of this test
    # fail against a lookup it was not measuring.
    renderer = PygameRenderer(scale=3, intro_wav=None)
    monkeypatch.setattr(media.assets, "find", counting)
    try:
        for _ in range(5):
            renderer._portrait_surface("ash")
        portrait_calls = [c for c in calls if c[0] == media.PORTRAIT_DIR]
        assert len(portrait_calls) == 1, f"searched {len(portrait_calls)} times"
    finally:
        renderer.close()


@pytest.mark.parametrize("crew_id", [cid for cid, *_ in ROSTER])
def test_every_crew_id_resolves_to_the_named_file(
    crew_id: str, tmp_path, monkeypatch
) -> None:
    """Each id maps to `portraits/<id>.png` under a root, and to nothing else.

    The first version of this asserted `path is None or True`, which is true of
    everything and tested nothing.
    """
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    assert media.portrait_path(crew_id) is None

    folder = tmp_path / media.PORTRAIT_DIR
    folder.mkdir(exist_ok=True)
    wanted = folder / f"{crew_id}{media.PORTRAIT_EXT}"
    wanted.write_bytes(b"")
    assert media.portrait_path(crew_id) == wanted


# --- D2: your own character set -----------------------------------------------

def test_glyphs_are_no_longer_called_unreplaceable() -> None:
    assert "glyphs" not in {name for name, _ in media.NOT_YET}
    assert "glyphs" in {slot.key for slot in media.slots()}


def test_a_supplied_charset_wins_over_the_derived_one(
    tmp_path, monkeypatch
) -> None:
    """The point of D2: you keep what came off your own disk.

    Overwriting `charset.bin` was always possible and always destructive - the
    only way to draw with a different font was to throw away the artefact you
    extracted. A separate name, searched first, lets both exist.
    """
    derived = tmp_path / media.GLYPH_FILE
    derived.write_bytes(b"derived")
    folder = tmp_path / media.GLYPH_DIR
    folder.mkdir()
    mine = folder / media.GLYPH_FILE
    mine.write_bytes(b"mine")
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    assert media.charset_path() == mine
    assert derived.read_bytes() == b"derived", "the derived charset was disturbed"


def test_without_an_override_the_derived_charset_is_used(
    tmp_path, monkeypatch
) -> None:
    derived = tmp_path / media.GLYPH_FILE
    derived.write_bytes(b"derived")
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    assert media.charset_path() == derived


def test_no_charset_at_all_is_not_an_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    assert media.charset_path() is None


def test_the_derived_charset_says_where_to_put_your_own() -> None:
    slot = next(s for s in media.slots() if s.key == "charset")
    assert slot.swap
    assert media.GLYPH_DIR in slot.swap


def test_the_game_loads_the_charset_the_dictionary_names() -> None:
    """`__main__` must go through `media.charset_path`, not its own `find`.

    The D1 lesson applied again: a dictionary that documents a folder the
    loader does not read is worse than no dictionary at all.
    """
    import alien_remake.__main__ as main_module

    source = pathlib.Path(main_module.__file__).read_text(encoding="utf-8")
    assert "media_module.charset_path()" in source
    assert 'assets.find("charset.bin")' not in source


# --- D3: your own deck plans ---------------------------------------------------

def test_map_art_is_no_longer_called_unreplaceable() -> None:
    assert "graphics" not in {name for name, _ in media.NOT_YET}
    keys = {slot.key for slot in media.slots()}
    for deck in DECK_NAMES:
        assert f"map/{media.map_name(deck)}" in keys, deck


def test_the_deck_names_come_from_the_ship_not_a_second_list() -> None:
    """A deck renamed in `nostromo.py` must rename its file too."""
    assert media.map_name(0) == "upper"
    assert media.map_name(1) == "middle"
    assert media.map_name(2) == "lower"
    for deck, name in DECK_NAMES.items():
        assert media.map_name(deck) == name.split()[0].lower()


def _supply_map(tmp_path, monkeypatch, deck: int,
                colour: tuple[int, int, int]) -> None:
    folder = tmp_path / media.MAP_DIR
    folder.mkdir(exist_ok=True)
    art = pygame.Surface((480, 288))
    art.fill(colour)
    pygame.image.save(art, str(folder / f"{media.map_name(deck)}{media.MAP_EXT}"))
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])


def _playing_renderer() -> tuple:
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    renderer = PygameRenderer(scale=2, intro_wav=None)
    sim = Simulation(rng=random.Random(11))
    flow = GameFlow()
    flow.screen, flow.sim = Screen.PLAYING, sim
    renderer._menu = MenuController(sim)
    renderer._sim, renderer._ship = sim, sim.ship
    return renderer, flow, sim


def test_a_supplied_deck_plan_is_the_one_drawn(tmp_path, monkeypatch) -> None:
    """The failure the dictionary's shape cannot catch: listed, never loaded."""
    _supply_map(tmp_path, monkeypatch, 0, (255, 0, 255))
    renderer, flow, sim = _playing_renderer()
    try:
        sim.state.deck = 0
        renderer.draw(flow)
        surface = renderer._backdrop_surface(0)
        assert surface is not None
        assert surface.get_at((4, 4))[:3] == (255, 0, 255)
    finally:
        renderer.close()


def test_a_supplied_plan_is_scaled_to_the_map_field(tmp_path, monkeypatch) -> None:
    """The panel starts at column 30 and the status rows are drawn live, so an
    image left at its own size would paint over screen furniture - and both of
    those positions are decoded, not chosen."""
    _supply_map(tmp_path, monkeypatch, 1, (0, 255, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        art = renderer._supplied_deck_art(1)
        assert art is not None
        assert art.get_size() == media.MAP_SIZE
    finally:
        renderer.close()


def test_a_deck_left_alone_still_draws_the_games_own_plan(
    tmp_path, monkeypatch
) -> None:
    """One supplied deck must not disturb the other two."""
    _supply_map(tmp_path, monkeypatch, 0, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        assert renderer._supplied_deck_art(0) is not None
        assert renderer._supplied_deck_art(1) is None
        assert renderer._supplied_deck_art(2) is None
    finally:
        renderer.close()


def test_supplied_art_replaces_the_plan_rather_than_filling_a_gap(
    tmp_path, monkeypatch
) -> None:
    """Checked *before* the decoded snapshot, not after.

    Read the other way round it would only ever appear on a machine whose
    snapshot was missing, which is never - and the file would look ignored.
    """
    _supply_map(tmp_path, monkeypatch, 0, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        from alien_remake.core import gamedata_snapshot as snapshot

        assert snapshot.DECK_PLANS[0], "the decoded plan is present"
        surface = renderer._backdrop_surface(0)
        assert surface is not None
        assert surface.get_at((4, 4))[:3] == (255, 0, 255)
    finally:
        renderer.close()


def test_a_corrupt_deck_plan_falls_back_to_the_games_own(
    tmp_path, monkeypatch
) -> None:
    """A blank map reads as the game being broken, not the file.

    Given a real charset, because the fallback *is* the game rasterizing its
    own screen codes and that needs glyphs to draw them with. The first version
    of this test asserted the fallback produced a surface on a renderer with no
    tileset, which was asking the wrong thing: with nothing to draw with there
    is no map either way, and the assertion would have passed for a build that
    silently used the corrupt file.
    """
    from alien_remake.render.tiles import load as load_tiles

    real = assets.find(media.GLYPH_FILE)
    if real is None:
        pytest.skip("needs the derived charset.bin")
    tiles = load_tiles(real)

    folder = tmp_path / media.MAP_DIR
    folder.mkdir()
    (folder / f"upper{media.MAP_EXT}").write_bytes(b"not a png")
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    renderer, flow, sim = _playing_renderer()
    renderer._tiles = tiles
    try:
        assert renderer._supplied_deck_art(0) is None
        sim.state.deck = 0
        renderer.draw(flow)              # must not raise
        drawn = renderer._backdrop_surface(0)
        assert drawn is not None, "the fallback did not draw"
    finally:
        renderer.close()


def test_the_deck_art_miss_is_cached(tmp_path, monkeypatch) -> None:
    calls = []

    def counting(*parts: str):
        calls.append(parts)
        return None

    renderer, _flow, _sim = _playing_renderer()
    monkeypatch.setattr(media.assets, "find", counting)
    try:
        for _ in range(5):
            renderer._supplied_deck_art(0)
        assert len([c for c in calls if c[0] == media.MAP_DIR]) == 1
    finally:
        renderer.close()


# --- D4: your own sprites -------------------------------------------------------
#
# The owner's ruling is what shapes these: "the layout should be the same. This
# is just to replace the graphics that make the layout. These should be
# interchangeable with the original game and not change the gameplay in any
# way." So there are two things to hold. A supplied file must be *used*, and it
# must change nothing but the picture.


def test_every_drawn_sprite_has_a_slot() -> None:
    keys = {slot.key for slot in media.slots()}
    for index in media.SPRITE_ROLES:
        assert f"sprite/{index}" in keys, index
    assert "title_egg" in keys


def test_the_sprite_roles_match_the_decoded_tables() -> None:
    """`media` cannot import `render.play` — it would drag pygame into a
    headless module — so the role table is a copy. This is the guard that stops
    the copy rotting: it reads the decoded tables and fails if they move.
    """
    from alien_remake.render import play

    base = play._SPRITE_SLOT_BASE
    expected = {play._CHAR_SPRITE}
    expected |= set(play._POINTER_FRAMES)
    expected |= set(play._JONES_FRAMES)
    for slots in play._ATTACK_SLOTS:
        for slot in slots:
            if slot is not None:
                expected |= {slot - base + frame for frame in range(4)}
    expected.add(play._ATTACK_STATIC_SLOT - base)

    listed = set(media.SPRITE_ROLES)
    assert expected - listed == set(), f"undocumented sprites: {expected - listed}"


def test_the_portrait_slots_are_not_offered_twice() -> None:
    """They are addressed by crew id under `portraits/` (D1). Two ways to
    supply the same picture is two files that can disagree about Ripley."""
    from alien_remake.render.layout import _PORTRAIT_SLOTS

    for slot in _PORTRAIT_SLOTS:
        assert slot not in media.SPRITE_ROLES, slot


def _supply_sprite(tmp_path, monkeypatch, index: int,
                   colour: tuple[int, int, int]) -> None:
    folder = tmp_path / media.SPRITE_DIR
    folder.mkdir(exist_ok=True)
    art = pygame.Surface((48, 42))
    art.fill(colour)
    pygame.image.save(art, str(folder / f"{index}{media.SPRITE_EXT}"))
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])


def test_a_supplied_sprite_is_the_one_drawn(tmp_path, monkeypatch) -> None:
    from alien_remake.render import play

    _supply_sprite(tmp_path, monkeypatch, play._CHAR_SPRITE, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        surf = renderer._sprite_surface(play._CHAR_SPRITE, (0, 255, 0))
        assert surf is not None
        assert surf.get_at((4, 4))[:3] == (255, 0, 255)
    finally:
        renderer.close()


def test_a_supplied_sprite_is_scaled_to_the_hardware_size(
    tmp_path, monkeypatch
) -> None:
    """24x21 comes from the machine, never from the file - that is what keeps a
    replacement from moving or resizing anything."""
    _supply_sprite(tmp_path, monkeypatch, 24, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        art = renderer._supplied_sprite(24)
        assert art is not None
        assert art.get_size() == media.SPRITE_SIZE
    finally:
        renderer.close()


def test_a_sprite_left_alone_is_untouched(tmp_path, monkeypatch) -> None:
    _supply_sprite(tmp_path, monkeypatch, 24, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        assert renderer._supplied_sprite(24) is not None
        assert renderer._supplied_sprite(25) is None
    finally:
        renderer.close()


def test_the_sprite_miss_is_cached(tmp_path, monkeypatch) -> None:
    """The alien is six sprites a frame and the map redraws every frame."""
    calls = []

    def counting(*parts: str):
        calls.append(parts)
        return None

    renderer, _flow, _sim = _playing_renderer()
    monkeypatch.setattr(media.assets, "find", counting)
    try:
        for _ in range(20):
            renderer._supplied_sprite(24)
        assert len([c for c in calls if c[0] == media.SPRITE_DIR]) == 1
    finally:
        renderer.close()


def test_a_corrupt_sprite_falls_back_to_the_games_own(
    tmp_path, monkeypatch
) -> None:
    folder = tmp_path / media.SPRITE_DIR
    folder.mkdir()
    (folder / f"24{media.SPRITE_EXT}").write_bytes(b"not a png")
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    renderer, _flow, _sim = _playing_renderer()
    try:
        assert renderer._supplied_sprite(24) is None
    finally:
        renderer.close()


# --- D4: what a substitution must NOT change ------------------------------------

def test_a_fixed_ink_is_simply_replaced(tmp_path, monkeypatch) -> None:
    """Jones is always colour 8 and the alien always 5. There the colour is
    decoration, and a supplied picture replaces it outright."""
    from alien_remake.render import play

    jones = play._JONES_FRAMES[0]
    _supply_sprite(tmp_path, monkeypatch, jones, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        surf = renderer._sprite_surface(jones, (0, 0, 255))
        assert surf is not None
        assert surf.get_at((4, 4))[:3] == (255, 0, 255), "the ink tinted the art"
    finally:
        renderer.close()


def test_the_heartbeat_survives_a_supplied_marker(tmp_path, monkeypatch) -> None:
    """The marker's colour *is* the heartbeat (`$4ED4`, reloaded every 7 ticks).

    Art drawn flat over it would delete a signal the original gives the player,
    which is what the owner's "not change the gameplay in any way" rules out.
    So the ramp is washed over the supplied picture instead: still the player's
    art, still beating.
    """
    from alien_remake.render import play

    _supply_sprite(tmp_path, monkeypatch, play._CHAR_SPRITE, (128, 128, 128))
    renderer, _flow, _sim = _playing_renderer()
    try:
        art = renderer._supplied_sprite(play._CHAR_SPRITE)
        assert art is not None
        seen = {
            renderer._signalled(art, play._CHAR_SPRITE,
                                c64.rgb(step)).get_at((4, 4))[:3]
            for step in play._HEARTBEAT_COLOURS
        }
        assert len(seen) > 1, "the marker stopped beating"
    finally:
        renderer.close()


def test_the_duct_signal_survives_a_supplied_portrait(
    tmp_path, monkeypatch
) -> None:
    """Black in a room, white in a duct (`$6501,Y`) — the colour says *where
    they are*. D1 shipped without this and a supplied portrait flattened it."""
    from alien_remake.render import play

    _supply(tmp_path, monkeypatch, "ash", (128, 128, 128))
    renderer, _flow, _sim = _playing_renderer()
    try:
        art = renderer._portrait_surface("ash")
        assert art is not None
        in_room = renderer._signalled(
            art, "ash", c64.rgb(play._CHAR_PORTRAIT_ROOM_COLOUR)
        ).get_at((4, 4))[:3]
        in_duct = renderer._signalled(
            art, "ash", c64.rgb(play._CHAR_PORTRAIT_DUCT_COLOUR)
        ).get_at((4, 4))[:3]
        assert in_room != in_duct, "you can no longer tell a duct from a room"
    finally:
        renderer.close()


def test_the_wash_leaves_the_picture_recognisable(tmp_path, monkeypatch) -> None:
    """Half strength, not a repaint: the point is to keep both the art and the
    signal, and a full-strength wash would just be the old flat ink again."""
    from alien_remake.render import play

    _supply_sprite(tmp_path, monkeypatch, play._CHAR_SPRITE, (255, 0, 0))
    renderer, _flow, _sim = _playing_renderer()
    try:
        art = renderer._supplied_sprite(play._CHAR_SPRITE)
        assert art is not None
        washed = renderer._signalled(art, play._CHAR_SPRITE, (0, 0, 0))
        red = washed.get_at((4, 4))[0]
        assert red > 0, "the wash painted the art out"
        assert red < 255, "the wash did nothing"
    finally:
        renderer.close()


def test_a_sprite_override_moves_nothing(tmp_path, monkeypatch) -> None:
    """The owner's ruling, as a test: the layout stays the original's.

    Every sprite is centred on a decoded position, and the drawn size comes
    from `SPRITE_SIZE`, so a supplied file of any dimensions lands in exactly
    the same rectangle as the ROM's own.
    """
    from alien_remake.render import play

    renderer, _flow, _sim = _playing_renderer()
    try:
        before = renderer._sprite_surface(play._CHAR_SPRITE, (255, 255, 255))
    finally:
        renderer.close()

    _supply_sprite(tmp_path, monkeypatch, play._CHAR_SPRITE, (255, 0, 255))
    renderer, _flow, _sim = _playing_renderer()
    try:
        after = renderer._sprite_surface(play._CHAR_SPRITE, (255, 255, 255))
        assert after is not None
        if before is not None:
            assert after.get_size() == before.get_size()
        assert after.get_size() == media.SPRITE_SIZE
    finally:
        renderer.close()


# --- D4: the title egg ------------------------------------------------------------

def test_a_supplied_title_egg_is_the_one_drawn(tmp_path, monkeypatch) -> None:
    art = pygame.Surface((640, 400))
    art.fill((255, 0, 255))
    pygame.image.save(art, str(tmp_path / media.TITLE_ART))
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    renderer = PygameRenderer(scale=2, intro_wav=None)
    try:
        egg = renderer._title_egg_surface()
        assert egg is not None
        assert egg.get_size() == media.TITLE_ART_SIZE
        assert egg.get_at((4, 4))[:3] == (255, 0, 255)
    finally:
        renderer.close()


def test_the_title_egg_needs_no_extracted_disk(tmp_path, monkeypatch) -> None:
    """Composing the ROM's egg needs the sprite bank; an image does not."""
    art = pygame.Surface((320, 200))
    art.fill((0, 255, 255))
    pygame.image.save(art, str(tmp_path / media.TITLE_ART))
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    renderer = PygameRenderer(scale=2, intro_wav=None)
    try:
        renderer._tiles = None
        assert renderer._title_egg_surface() is not None
    finally:
        renderer.close()


def test_without_a_supplied_egg_nothing_changes(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])
    renderer = PygameRenderer(scale=2, intro_wav=None)
    try:
        renderer._tiles = None
        assert renderer._title_egg_surface() is None
    finally:
        renderer.close()


# --- D4: the layout itself stays put ---------------------------------------------

def test_layouts_stay_on_the_not_yet_list_by_decision() -> None:
    """Not for want of a mechanism. The owner's ruling is that the layout stays
    the original's, so the reason given has to say *decided*, not *missing*."""
    reasons = dict(media.NOT_YET)
    assert "layouts" in reasons
    assert "deliberately" in reasons["layouts"]


def test_every_drawn_size_is_a_constant_not_a_file_property() -> None:
    """The guarantee, stated once: what a supplied file *is* never decides how
    big it is drawn, so it cannot push anything else out of place.

    Each override path scales to a module constant, and those constants come
    from the machine: a hardware sprite, the map field, the display. The first
    version of this test looked for commas in filenames as a proxy for
    coordinates, which said nothing and failed on `Alien (USA, Europe)`.
    """
    assert media.SPRITE_SIZE == (24, 21)          # a C64 hardware sprite
    assert media.PORTRAIT_SIZE == (24, 21)        # the same
    assert media.MAP_SIZE == (240, 144)           # 30 x 18 cells at 8x8
    assert media.TITLE_ART_SIZE == (320, 200)     # the whole display

    source = pathlib.Path(media.__file__).read_text(encoding="utf-8")
    assert "get_width" not in source, (
        "media decided a size from an image rather than from the machine"
    )


def _playing_with_crew(seed: int = 7):
    """A play-screen renderer with a crew member actually selected.

    Asked of the panel rather than named: `entries()` re-derives commandability
    every frame (D-158), so a hard-coded name gives the crew-order list on some
    seeds and the CONTROL list on others.
    """
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    renderer = PygameRenderer(scale=2, intro_wav=None)
    sim = Simulation(rng=random.Random(seed))
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
    return renderer, flow, sim


def _washes(renderer) -> list:
    """Record every `_signalled` call the next draw makes."""
    seen: list = []
    original = renderer._signalled

    def spy(art, key, colour):
        seen.append(key)
        return original(art, key, colour)

    renderer._signalled = spy   # type: ignore[method-assign]
    return seen


def test_the_marker_call_site_asks_for_its_signal_back(
    tmp_path, monkeypatch
) -> None:
    """Drives the real draw, not the helper.

    The helper-only tests above would pass even if `varies=True` were dropped
    from the call site - which is the mistake that would actually happen. This
    is the one that notices.
    """
    from alien_remake.render import play

    _supply_sprite(tmp_path, monkeypatch, play._CHAR_SPRITE, (128, 128, 128))
    renderer, flow, _sim = _playing_with_crew()
    try:
        if renderer._menu.selected_crew is None:
            pytest.skip("no crew is commandable on this seed")
        seen = _washes(renderer)
        renderer.draw(flow)
        assert play._CHAR_SPRITE in seen, (
            "the heartbeat marker was drawn flat - `varies=True` is gone"
        )
    finally:
        renderer.close()


def test_the_portrait_call_site_asks_for_its_signal_back(
    tmp_path, monkeypatch
) -> None:
    """Same again for the duct/room colour that D1 originally flattened."""
    renderer, flow, _sim = _playing_with_crew()
    try:
        crew_id = renderer._menu.selected_crew
        if crew_id is None:
            pytest.skip("no crew is commandable on this seed")
    finally:
        renderer.close()

    _supply(tmp_path, monkeypatch, crew_id, (128, 128, 128))
    renderer, flow, _sim = _playing_with_crew()
    try:
        seen = _washes(renderer)
        renderer.draw(flow)
        assert crew_id in seen, (
            "the marker portrait was drawn flat - a duct now looks like a room"
        )
    finally:
        renderer.close()


# --- the generated document ------------------------------------------------------

def test_the_committed_media_document_is_current() -> None:
    """`docs/MEDIA.md` is generated. If this fails, run:

        python -c "import pathlib; from alien_remake import media;         pathlib.Path('docs/MEDIA.md').write_text(media.document()+chr(10),         encoding='utf-8', newline='')"
    """
    doc = pathlib.Path(__file__).resolve().parent.parent / "docs" / "MEDIA.md"
    assert doc.is_file(), "docs/MEDIA.md is missing"
    assert doc.read_text(encoding="utf-8") == media.document() + chr(10), (
        "docs/MEDIA.md is out of date - regenerate it (see this docstring)"
    )


def test_the_document_carries_no_machine_specific_truth() -> None:
    """It is committed, so it is read on machines other than this one.

    A resolved asset root is one person's home directory, and a "present /
    absent" column is true for one machine at one moment. Both were in the
    first draft; both would have made the file misleading for every other
    reader *and* impossible to keep current.
    """
    text = media.document()
    for root in assets.asset_roots():
        assert str(root) not in text, f"{root} is baked into the document"
    assert "absent" not in text
    assert "--media" in text, "it must point at the live view instead"


def test_every_slot_kind_states_a_file_format() -> None:
    """The owner asked for "file descriptions that are required such as khz for
    audio or resolution for graphics" — so a kind with no stated requirement is
    a gap, not a default."""
    kinds = {slot.kind for slot in media.slots()}
    for kind in kinds:
        assert media.requirement(kind), f"{kind} does not say what a file must be"


def test_the_audio_requirement_names_the_mixers_own_rate() -> None:
    """44100 is not a preference: it is `sfx.EXPORT_SAMPLE_RATE`, which is what
    the mixer opens at, so anything else costs a resample."""
    from alien_remake.audio import sfx

    for kind in ("sound (the game's own)", "sound (added)"):
        assert str(sfx.EXPORT_SAMPLE_RATE) in media.requirement(kind), kind


def test_every_sound_says_what_it_is() -> None:
    """Every effect row used to read "replaces the emulated SID effect", which
    tells somebody choosing a recording nothing about what they are choosing it
    for."""
    from alien_remake.audio import samples, sfx

    for name in tuple(sfx.EFFECTS) + tuple(samples.UI_CUES):
        assert name in media.SOUND_MEANING, name
        assert media.SOUND_MEANING[name], name
