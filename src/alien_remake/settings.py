"""Persistent options, for the places a command line cannot reach.

Steam's Game Mode launches a program with no arguments and no terminal, so on a
Steam Deck `--crt full` has nowhere to go. This is that missing channel: a small
file of the same options, read at startup, with **the command line still
winning** wherever it is given.

Deliberately tiny and hand-editable. It uses `tomllib`, which is in the standard
library from 3.11, so the toolkit's stdlib-only rule survives::

    # ~/.local/share/alien-remake/settings.toml   (or %LOCALAPPDATA% on Windows)
    crt = "subtle"
    front_end = "quick"
    jones = "patient"
    alien_start = "airlock"

Unknown keys are ignored rather than fatal: a file written by a later version
should not stop an earlier one starting. A malformed file is reported once, on
stderr, and then ignored for the same reason — the game still runs.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any

from . import assets

#: The file name, inside the per-user data directory `assets` already defines.
FILENAME = "settings.toml"

#: Every option this file may carry, and the CLI flag each one mirrors. Keeping
#: the two in step is what makes "the command line wins" meaningful rather than
#: a claim: a key with no flag would be a setting nobody could override.
KEYS: tuple[str, ...] = (
    "crt", "front_end", "jones", "alien_start", "mode", "death", "android",
    "developer", "sound", "game_audio", "turns", "screen_fx",
)

#: Bumped when a *value* changes meaning rather than merely being added. Files
#: written before versioning have no key and read as version 1.
VERSION = 3
VERSION_KEY = "version"

#: Version 1 spelled the original's behaviour after where it happens to put
#: things (`airlock`, `rom`); version 2 calls it `original` throughout.
#: Version 3 renames `game_audio`'s `sampled` to `enhanced` (2026-09-05) — the
#: word alone no longer says the option also runs a loudness spec check and
#: is where new audio files go, so it was worth a clearer name (`core.options`
#: has the full reasoning).
#:
#: `death` is why this needs a version rather than a plain alias table: v1's
#: `random` meant the ROM's three-name table and v2's `random` means the whole
#: crew. The same word, opposite ends of the choice — so a v1 file read as v2
#: would silently start opening on crew members the original never kills.
#: `game_audio`'s `sampled` carried one meaning throughout, so its own rename
#: is a plain substitution regardless of which older version wrote it — safe
#: to fold into the same table rather than needing its own migration step.
_V1_VALUES: dict[str, dict[str, str]] = {
    "alien_start": {"airlock": "original"},
    "android": {"rom": "original", "any": "random"},
    "death": {"random": "original", "any": "random"},
    "game_audio": {"sampled": "enhanced"},
}


def _migrate(raw: dict[str, str], version: int) -> dict[str, str]:
    """Bring an older file up to the current value spelling."""
    if version >= VERSION:
        return raw
    return {
        key: _V1_VALUES.get(key, {}).get(value, value)
        for key, value in raw.items()
    }


def path() -> Path:
    """Where the settings file lives. Not created unless the user writes one."""
    return assets._user_data_dir() / FILENAME


def load(source: Path | None = None) -> dict[str, str]:
    """Read the settings file. Returns `{}` when there is nothing usable.

    Never raises: a missing file is the normal case, and a broken one must not
    stop the game — it is an options file, not a save.
    """
    target = source if source is not None else path()
    try:
        raw: dict[str, Any] = tomllib.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"alien-remake: ignoring {target}: {exc}", file=sys.stderr)
        return {}
    version = raw.get(VERSION_KEY)
    values = {k: str(v) for k, v in raw.items() if k in KEYS and v is not None}
    return _migrate(values, int(version) if isinstance(version, int) else 1)


def is_first_run(
    args: Any,
    defaults: dict[str, str],
    target: Path | None = None,
) -> bool:
    """Has this machine never been asked which edition it wants?

    Two conditions, and the second is the less obvious one.

    **Is there a settings file** — asked of the file, not of what :func:`load`
    made of it. A corrupt or unreadable file reads back as no settings at all,
    but a player whose file went bad has still run the game before and must not
    be met with a question they already answered. Existence is the record that
    they were asked; the contents are only what they said.

    **Did they ask for something on the command line** — because the first-run
    screen writes a whole profile, and a player who typed `--crt full` would
    watch it be overwritten by an answer to a question they never wanted. The
    rest of this module exists to make the command line win, and opening with a
    screen that overrides it would contradict that in the first second.

    Note that a *later* version adding a key to :data:`KEYS` does not re-ask:
    the file is still there.
    """
    if (target if target is not None else path()).exists():
        return False
    return not any(
        hasattr(args, key) and getattr(args, key) != defaults.get(key)
        for key in KEYS
    )


def apply(args: Any, defaults: dict[str, str], settings: dict[str, str]) -> list[str]:
    """Fill in argparse values the user left at their default.

    `defaults` is what the parser would produce with no arguments at all, so a
    value that still equals its default was *not* asked for and the file may
    speak. Returns the names it filled, for the caller to report.

    This is the whole precedence rule, and it is deliberately one comparison:
    anything cleverer (tracking which flags appeared on the line) buys nothing
    a player would notice and adds a way for the two to disagree.
    """
    used = []
    for key, value in settings.items():
        if not hasattr(args, key):
            continue
        if getattr(args, key) == defaults.get(key):
            setattr(args, key, value)
            used.append(f"{key}={value}")
    return used


def save(values: dict[str, str], target: Path | None = None) -> Path | None:
    """Write the options file. Returns the path written, or ``None`` on failure.

    Writing is why this module exists at all now: the options screen has to
    outlive the process, and a player who reached it has no terminal to pass
    flags on next time.

    Hand-rolled TOML rather than a writer dependency — the file is a flat map
    of short strings, `tomllib` is read-only, and the runtime stays stdlib-only.
    Only known keys are written, so a stray value cannot end up in a file the
    loader would then ignore anyway.

    Never raises. A read-only or full disk must not take the game down mid-menu;
    the options simply do not persist, and the caller reports that.
    """
    path_ = target if target is not None else path()
    lines = [
        "# alien-remake options, written by the in-game options screen.",
        "# Command-line flags still win over anything set here.",
        f"{VERSION_KEY} = {VERSION}",
    ]
    for key in KEYS:
        value = values.get(key)
        if value is None:
            continue
        # Values are enum-style words (`off`, `quick`, `airlock`), so the only
        # escaping that can matter is the quote itself.
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key} = "{escaped}"')
    try:
        path_.parent.mkdir(parents=True, exist_ok=True)
        path_.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"alien-remake: could not save {path_}: {exc}", file=sys.stderr)
        return None
    return path_
