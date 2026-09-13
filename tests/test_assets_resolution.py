"""Derived assets must be found from any working directory (DISC-241).

Every runtime asset used a bare relative ``Path("out")/...``, so the game only
found its own data when launched from the project root. Anywhere else it
degraded in silence — and not only by losing music: without ``basic.bin``,
`opening_name.garbled_name_codes` returns ``None`` and the opening prints the
victim's *clean* name where the original prints the garbled one. A wrong
working directory changed replica behaviour.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from alien_remake import assets


@pytest.fixture(autouse=True)
def _clear_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never let the developer's own environment decide these outcomes."""
    monkeypatch.delenv(assets.ENV_VAR, raising=False)


def test_finds_assets_from_a_foreign_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The actual bug: chdir away from the repo and the game went blind."""
    monkeypatch.chdir(tmp_path)
    # The repo-root fallback is derived from this module's own location, so it
    # keeps working no matter where the process was started.
    assert Path.cwd() != Path(assets.__file__).resolve().parent.parent.parent

    if not (Path(assets.__file__).resolve().parent.parent.parent
            / assets.DERIVED_DIR / "charset.bin").exists():
        pytest.skip("out/charset.bin not built in this checkout")

    # What every call site used to do, and why the bug was silent: from here,
    # the old relative path resolves to nothing at all and raises nothing.
    assert not (Path("out") / "charset.bin").exists()

    found = assets.find("charset.bin")
    assert found is not None and found.exists()


def test_env_override_wins_over_everything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "charset.bin").write_bytes(b"decoy")
    monkeypatch.setenv(assets.ENV_VAR, str(tmp_path))
    found = assets.find("charset.bin")
    assert found is not None and found.read_bytes() == b"decoy"


def test_env_override_is_read_per_call_not_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`asset_roots` must not memoise: tests and callers change the env."""
    first, second = tmp_path / "a", tmp_path / "b"
    for d, payload in ((first, b"A"), (second, b"B")):
        d.mkdir()
        (d / "charset.bin").write_bytes(payload)
    monkeypatch.setenv(assets.ENV_VAR, str(first))
    found_a = assets.find("charset.bin")
    monkeypatch.setenv(assets.ENV_VAR, str(second))
    found_b = assets.find("charset.bin")
    assert found_a is not None and found_a.read_bytes() == b"A"
    assert found_b is not None and found_b.read_bytes() == b"B"


def test_missing_asset_returns_none_rather_than_raising() -> None:
    """Every asset is optional; absence is a normal answer, not an error."""
    assert assets.find("no-such-asset-should-ever-exist.bin") is None


def test_search_roots_are_deduplicated_and_ordered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    roots = assets.asset_roots()
    resolved = [r.resolve() for r in roots]
    assert len(resolved) == len(set(resolved)), "duplicate root searched twice"
    # cwd/out must be consulted before the per-user directory, so a developer's
    # local decode always beats an installed copy.
    assert roots[0].resolve() == (Path.cwd() / assets.DERIVED_DIR).resolve()


@pytest.mark.real_user_data
def test_user_data_dir_follows_the_platform_convention(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One `sys.platform` branch is all the Linux/Deck path costs today.

    Asks `_platform_data_dir` rather than `_user_data_dir`, because since
    2026-08-30 the latter prefers the game's own folder when that is
    writable (owner: "the log should be in the work folder") and only falls
    back to the convention. The convention itself is unchanged and is what
    this pins.
    """
    monkeypatch.setattr(assets.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\test\AppData\Local")
    assert assets._platform_data_dir() == Path(r"C:\Users\test\AppData\Local\alien-remake")

    monkeypatch.setattr(assets.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", "/home/deck/.local/share")
    assert assets._platform_data_dir() == Path("/home/deck/.local/share/alien-remake")

    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    assert assets._platform_data_dir() == Path.home() / ".local" / "share" / "alien-remake"


def test_report_is_ascii_for_the_windows_console() -> None:
    """`sys.stderr` is cp1252 on a default Windows console.

    The rest of this codebase's prose uses em-dashes freely; this string is the
    one that gets printed to a terminal, so it may not.
    """
    for line in assets.report():
        line.encode("ascii")
    for _, _, why, how in assets.KNOWN_ASSETS:
        (why + how).encode("ascii")


def test_report_names_every_missing_asset_and_how_to_make_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Silence about a missing asset is what made this a bug, not a limitation."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(assets.ENV_VAR, str(tmp_path))   # empty dir: all missing
    # Also neutralise the repo-root fallback so nothing resolves.
    monkeypatch.setattr(assets, "asset_roots", lambda: (tmp_path,))
    lines = assets.report()
    assert len(lines) == len(assets.KNOWN_ASSETS)
    for _, parts, _, how in assets.KNOWN_ASSETS:
        assert any("/".join(parts) in ln and how in ln for ln in lines)


def test_report_is_empty_when_everything_resolves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(assets, "asset_roots", lambda: (tmp_path,))
    (tmp_path / assets.FILES_DIR).mkdir()
    for _, parts, _, _ in assets.KNOWN_ASSETS:
        tmp_path.joinpath(*parts).write_bytes(b"x")
    assert assets.report() == []


def test_opening_name_no_longer_needs_the_rom_at_all(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Rewritten 2026-08-30.** This used to assert that no ROM meant `None`,
    so the caller showed the real name — the graceful degradation.

    There is nothing to degrade to any more: the seventy bytes the original
    prints are captured (`GARBLED_NAME_BYTES`), so the bug is reproduced on
    every machine. `None` is now reserved for a slot outside the capture, which
    only a grown roster could produce.
    """
    from alien_remake.core import opening_name

    monkeypatch.setattr(assets, "asset_roots", lambda: (tmp_path,))
    monkeypatch.setattr(assets, "find_c64_rom", lambda name: None)
    assert opening_name.garbled_name_codes(1) == list(
        opening_name.GARBLED_NAME_BYTES[1]
    )
    assert opening_name.garbled_name_codes(99) is None


def test_instructions_return_no_pages_without_menu1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`pages()` promises `[]` when MENU1.prg is absent — now including unresolvable."""
    from alien_remake.core import instructions

    monkeypatch.setattr(assets, "asset_roots", lambda: (tmp_path,))
    assert instructions.default_menu1() is None
    assert instructions.pages() == []


def test_everything_argparse_prints_is_ascii() -> None:
    """A Windows console is cp1252 by default, and argparse writes straight to it.

    DISC-241 held `assets.report()` to ASCII for this reason. The lesson did not
    generalise on its own: `--alien-start`'s help text shipped with an em-dash
    and rendered as `?` (DISC-260). Two occurrences is enough to automate.

    This walks the real parser rather than grepping the source, so it also
    covers `prog`, the description, metavars and choices.
    """
    import argparse
    import io
    from contextlib import redirect_stdout

    from alien_remake.__main__ import main

    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            main(["--help"])
    except SystemExit:
        pass

    text = buffer.getvalue()
    assert text, "argparse printed nothing — the probe is not reaching --help"
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        bad = text[exc.start:exc.end]
        line = next(
            (ln for ln in text.split("\n") if bad in ln), ""
        ).strip()
        raise AssertionError(
            f"non-ASCII {bad!r} in --help output, which a cp1252 console "
            f"mangles: {line[:90]!r}"
        ) from None
    assert isinstance(argparse.ArgumentParser, type)   # import is load-bearing
