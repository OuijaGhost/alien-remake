"""CR1/CR2/CR3: the credits data, before there is a screen to show it.

Nothing here should be inventable — every row has to trace to something already
written down (a manifest entry, or the project's own stated sources), which is
what CR1 asked for.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake import assets, media


def _root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate every asset lookup to ``tmp_path`` alone.

    Setting only ``$ALIEN_REMAKE_ASSETS`` is not enough: `asset_roots()` puts
    the override first but still falls through to the checkout's own `out/`
    and the platform data dir if the override has no `sounds/` subfolder of
    its own (the common case here, since these tests want "nothing supplied").
    A real `out/sounds/sounds.toml` on the machine running the suite - which
    now exists, once anyone actually sets up their own supplied audio - was
    silently leaking through and failing these tests. Patching
    `asset_roots()` itself is the only isolation that actually isolates.
    """
    monkeypatch.setenv(assets.ENV_VAR, str(tmp_path))
    monkeypatch.setattr(assets, "asset_roots", lambda: (tmp_path,))
    return tmp_path


def test_project_credits_match_the_readme_s_own_wording() -> None:
    """One fact, one place: the in-game screen must not drift from the doc."""
    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(
        encoding="utf-8"
    )
    for entry in media.PROJECT_CREDITS:
        # Not a byte-for-byte match (the README is prose, this is data) but the
        # names that matter must both appear, or the two have quietly diverged.
        for word in ("Paul Clansey", "OuijaGhost"):
            if word in entry.get("author", ""):
                assert word in readme, f"{word!r} is in media.py but not README.md"


def test_credits_with_nothing_supplied_is_just_the_project_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root(tmp_path, monkeypatch)
    rows = media.credits()
    assert rows == list(media.PROJECT_CREDITS)


def test_a_manifest_entry_with_no_title_or_author_is_not_a_credit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CR1's own rule: a file present with nothing to say about it stays quiet."""
    root = _root(tmp_path, monkeypatch)
    (root / "portraits").mkdir()
    (root / "portraits" / "manifest.toml").write_text(
        '["ripley.png"]\nlicence = "CC0"\n', encoding="utf-8"
    )
    (root / "portraits" / "ripley.png").write_bytes(b"")
    rows = media.credits()
    assert rows == list(media.PROJECT_CREDITS), "an untitled entry became a credit"


def test_a_portrait_manifest_entry_is_picked_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path, monkeypatch)
    (root / "portraits").mkdir()
    (root / "portraits" / "manifest.toml").write_text(
        '["ripley.png"]\ntitle = "Ripley"\nauthor = "An Artist"\n',
        encoding="utf-8",
    )
    (root / "portraits" / "ripley.png").write_bytes(b"")
    rows = media.credits()
    added = [r for r in rows if r.get("file") == "ripley.png"]
    assert added == [{"file": "ripley.png", "title": "Ripley", "author": "An Artist"}]


def test_a_sound_manifest_entry_is_still_picked_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The pre-existing mechanism CR2 generalised must keep working."""
    root = _root(tmp_path, monkeypatch)
    (root / "sounds").mkdir()
    (root / "sounds" / "sounds.toml").write_text(
        '[crt_warmup]\nfile = "x.wav"\ntitle = "A Sound"\nauthor = "Someone"\n'
        'source = "https://example.com"\nlicence = "CC0 1.0"\n',
        encoding="utf-8",
    )
    (root / "sounds" / "x.wav").write_bytes(b"")
    rows = media.credits()
    titles = [r.get("title") for r in rows]
    assert "A Sound" in titles


def test_a_sound_credit_carries_its_own_file_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Owner's request (2026-09-04): the credits screen shows which file a
    credit is for, not just the recording's own title - so a player can
    match a row to a name in their own `sounds/` folder."""
    root = _root(tmp_path, monkeypatch)
    (root / "sounds").mkdir()
    (root / "sounds" / "sounds.toml").write_text(
        '[crt_warmup]\nfile = "838727__example.wav"\ntitle = "A Sound"\n'
        'author = "Someone"\n',
        encoding="utf-8",
    )
    (root / "sounds" / "838727__example.wav").write_bytes(b"")
    rows = media.credits()
    row = next(r for r in rows if r.get("title") == "A Sound")
    assert row.get("file") == "838727__example.wav"


def test_the_disassembly_is_not_a_credit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Owner's request (2026-09-04): `docs/re/` is documentation about the
    game, not something the credits screen needs to list."""
    _root(tmp_path, monkeypatch)
    titles = [r.get("title", "") for r in media.credits()]
    assert not any("disassembly" in t.lower() for t in titles)


def test_credits_lines_wrap_instead_of_truncating(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The bug this replaces: a long author/licence/URL used to be cut at
    the screen width with no sign anything was missing."""
    root = _root(tmp_path, monkeypatch)
    (root / "sounds").mkdir()
    long_source = "https://freesound.org/people/" + "a" * 60 + "/sounds/1/"
    (root / "sounds" / "sounds.toml").write_text(
        f'[crt_warmup]\nfile = "x.wav"\ntitle = "A Sound"\n'
        f'author = "Someone With An Unusually Long Display Name Indeed"\n'
        f'source = "{long_source}"\nlicence = "CC0 1.0"\n',
        encoding="utf-8",
    )
    (root / "sounds" / "x.wav").write_bytes(b"")
    lines = media.credits_lines()
    assert all(len(line) <= 40 for line in lines), (
        "a credits line exceeded the screen width - it should have wrapped"
    )
    # Reconstruct the unwrapped text: strip each continuation line's 2-space
    # indent and join with nothing, since a wrap can split mid-word with no
    # space inserted at the break.
    joined = "".join(line.strip() if line.startswith("  ") else line
                      for line in lines)
    assert long_source in joined, (
        "the long source line was truncated rather than wrapped across lines"
    )


def test_credits_pages_grows_when_lines_wrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`GameFlow.credits_pages()` must count wrapped lines, not entries, or
    the footer's page count and the actual content disagree."""
    from alien_remake.core.flow import GameFlow

    root = _root(tmp_path, monkeypatch)
    (root / "sounds").mkdir()
    (root / "sounds" / "sounds.toml").write_text(
        '[crt_warmup]\nfile = "x.wav"\ntitle = "A Sound"\n'
        'author = "Someone Whose Name Is Long Enough To Wrap Onto A '
        'Second Line All By Itself"\n'
        'source = "https://freesound.org/people/someone/sounds/1/"\n'
        'licence = "CC0 1.0 Universal (public domain dedication)"\n',
        encoding="utf-8",
    )
    (root / "sounds" / "x.wav").write_bytes(b"")
    flow = GameFlow()
    lines = media.credits_lines()
    from alien_remake.core.flow import CREDITS_ROWS_PER_PAGE

    expected = max(1, -(-len(lines) // CREDITS_ROWS_PER_PAGE))
    assert flow.credits_pages() == expected


def test_map_and_sprite_manifests_are_read_from_their_own_folders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path, monkeypatch)
    (root / "map").mkdir()
    (root / "map" / "manifest.toml").write_text(
        '["upper.png"]\ntitle = "Upper deck art"\nauthor = "Cartographer"\n',
        encoding="utf-8",
    )
    (root / "map" / "upper.png").write_bytes(b"")
    (root / "sprites").mkdir()
    (root / "sprites" / "manifest.toml").write_text(
        '["24.png"]\ntitle = "Marker sprite"\nauthor = "Pixel Person"\n',
        encoding="utf-8",
    )
    (root / "sprites" / "24.png").write_bytes(b"")

    rows = media.credits()
    titles = {r.get("title") for r in rows}
    assert {"Upper deck art", "Marker sprite"} <= titles


def test_a_broken_manifest_does_not_crash_the_screen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same contract as the sound manifest: a typo must not stop the game."""
    root = _root(tmp_path, monkeypatch)
    (root / "portraits").mkdir()
    (root / "portraits" / "manifest.toml").write_text(
        "this is not = = valid toml [[[", encoding="utf-8"
    )
    assert media.credits() == list(media.PROJECT_CREDITS)


def test_media_credit_returns_none_for_a_file_with_no_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path, monkeypatch)
    (root / "portraits").mkdir()
    present = root / "portraits" / "ripley.png"
    present.write_bytes(b"")
    assert media._media_credit(present) is None
    assert media._media_credit(None) is None
