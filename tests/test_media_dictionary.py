"""The replaceable-media dictionary (`--media`).

Its whole value is being complete and current. A list of file names that has
fallen behind the code is worse than no list, because a reader trusts it — so
these assert it is *generated from* the loaders rather than restated beside
them, and that a new slot cannot be added without appearing.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from alien_remake import assets, media  # noqa: E402
from alien_remake.audio import samples, sfx  # noqa: E402


def test_every_sound_the_game_can_load_is_listed() -> None:
    """Both halves: the decoded effects a recording can replace, and the
    interface cues that only exist if you supply them."""
    keys = {slot.key for slot in media.slots()}
    for effect in sfx.EFFECTS:
        assert effect in keys, f"{effect} can be replaced but is not listed"
    for cue in samples.UI_CUES:
        assert cue in keys, f"{cue} can be supplied but is not listed"


def test_every_derived_asset_is_listed() -> None:
    keys = {slot.key for slot in media.slots()}
    for key, *_ in assets.KNOWN_ASSETS:
        assert key in keys, f"{key} is loaded but not listed"


def test_nothing_is_listed_twice() -> None:
    keys = [slot.key for slot in media.slots()]
    assert len(keys) == len(set(keys))


def test_a_slot_says_where_the_file_goes() -> None:
    for slot in media.slots():
        assert slot.where, f"{slot.key} does not say where its file goes"
        assert slot.what, f"{slot.key} does not say what it is"


def test_status_reflects_what_is_actually_there(tmp_path, monkeypatch) -> None:
    """Present, absent, and the count when a cue has several recordings."""
    sounds = tmp_path / samples.DIRECTORY
    (sounds / samples.MENU_MOVE).mkdir(parents=True)
    for name in ("a", "b"):
        (sounds / samples.MENU_MOVE / f"{name}.wav").write_bytes(b"RIFF")
    (sounds / f"{samples.MENU_CHANGE}.wav").write_bytes(b"RIFF")
    monkeypatch.setattr(assets, "asset_roots", lambda: [tmp_path])

    by_key = {slot.key: slot for slot in media.slots()}
    assert by_key[samples.MENU_MOVE].status == "2 files"
    assert by_key[samples.MENU_CHANGE].status == "present"
    assert by_key[samples.SCREEN_ENTER].status == "absent"


def test_the_text_names_the_roots_it_searched() -> None:
    """A file in the wrong folder is the likeliest reason something is absent,
    so the report has to say where it looked."""
    text = media.describe()
    for root in assets.asset_roots():
        assert str(root) in text


def test_what_is_not_replaceable_is_said_rather_than_omitted() -> None:
    """Leaving them off would let a reader assume they were forgotten."""
    text = media.describe()
    assert "not replaceable yet" in text
    for name, _ in media.NOT_YET:
        assert name in text


def test_a_thing_cannot_be_both_replaceable_and_not() -> None:
    """The list of what is unsupported must not name something that is."""
    keys = {slot.key for slot in media.slots()}
    for name, _ in media.NOT_YET:
        assert name not in keys, f"{name} is listed as both"
