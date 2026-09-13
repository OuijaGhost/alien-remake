"""The options file exists for one reason: Game Mode passes no arguments.

So the two things worth pinning are that it reaches the game at all, and that it
never beats something the player actually typed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake import settings


def _write(tmp_path: Path, text: str) -> Path:
    target = tmp_path / settings.FILENAME
    target.write_text(text, encoding="utf-8")
    return target


def test_a_missing_file_is_the_normal_case(tmp_path: Path) -> None:
    assert settings.load(tmp_path / "nothing.toml") == {}


def test_values_are_read_and_stringified(tmp_path: Path) -> None:
    src = _write(tmp_path, 'crt = "subtle"\nfront_end = "classic"\n')
    assert settings.load(src) == {"crt": "subtle", "front_end": "classic"}


def test_unknown_keys_are_ignored_not_fatal(tmp_path: Path) -> None:
    """A file from a later version must not stop an earlier one starting."""
    src = _write(tmp_path, 'crt = "full"\nwarp_drive = "on"\n')
    assert settings.load(src) == {"crt": "full"}


def test_a_broken_file_is_reported_and_ignored(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """It is an options file, not a save: it must never stop the game."""
    src = _write(tmp_path, "crt = = = broken")
    assert settings.load(src) == {}
    assert "ignoring" in capsys.readouterr().err


def test_the_command_line_wins(tmp_path: Path) -> None:
    """The whole precedence rule, stated as a test."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--crt", default="off")
    parser.add_argument("--jones", default="patient")

    defaults = vars(parser.parse_args([]))
    stored = {"crt": "full", "jones": "easy"}

    # Nothing typed: the file speaks for both.
    args = parser.parse_args([])
    used = settings.apply(args, defaults, stored)
    assert (args.crt, args.jones) == ("full", "easy")
    assert sorted(used) == ["crt=full", "jones=easy"]

    # One typed: the file fills only the other.
    args = parser.parse_args(["--crt", "subtle"])
    settings.apply(args, defaults, stored)
    assert args.crt == "subtle", "the file overrode an explicit flag"
    assert args.jones == "easy"


def test_every_key_mirrors_a_real_flag() -> None:
    """A key with no flag would be a setting nobody could override.

    Walks the real parser, so adding a key here without adding the flag fails.
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
    help_text = buffer.getvalue()
    for key in settings.KEYS:
        flag = "--" + key.replace("_", "-")
        assert flag in help_text, f"{key} has no {flag} to override"
    assert isinstance(argparse.ArgumentParser, type)


@pytest.mark.real_user_data
def test_the_platform_convention_is_still_the_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On a Deck this lands in ~/.local/share, which is what the README says.

    **It is the fallback now rather than the answer (owner, 2026-08-30):**
    settings and logs go beside the game when that is writable, because
    somebody running out of a checkout expects to find them there. The
    convention still governs the installed copy, where the program may sit
    somewhere it cannot write.
    """
    from alien_remake import assets

    monkeypatch.setattr(assets.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", "/home/deck/.local/share")
    assert assets._platform_data_dir() == Path("/home/deck/.local/share/alien-remake")


@pytest.mark.real_user_data
def test_the_work_folder_wins_when_it_is_writable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The owner's case: run it out of a checkout, find the log in the
    checkout."""
    from alien_remake import assets

    (tmp_path / assets.DERIVED_DIR).mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(assets.HOME_VAR, raising=False)
    assert assets._user_data_dir() == tmp_path
    assert settings.path().parent == tmp_path


@pytest.mark.real_user_data
def test_a_directory_that_is_not_the_game_is_left_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`out/` is what says "this is the game's own folder". Without that test a
    bare `cd /` would start collecting a `logs/` directory."""
    from alien_remake import assets

    monkeypatch.chdir(tmp_path)          # no out/ here
    monkeypatch.delenv(assets.HOME_VAR, raising=False)
    assert assets._user_data_dir() != tmp_path


@pytest.mark.real_user_data
def test_the_home_variable_overrides_everything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from alien_remake import assets

    (tmp_path / assets.DERIVED_DIR).mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(assets.HOME_VAR, str(tmp_path / "elsewhere"))
    assert assets._user_data_dir() == tmp_path / "elsewhere"
