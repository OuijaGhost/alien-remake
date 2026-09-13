"""Find the derived asset files, from any working directory.

Every asset the remake loads at runtime was **derived from the original disk**
by ``alientools`` — the charset, the sprites, the intro tune, the BASIC ROM the
opening's garbled names are read out of. None of it can be shipped (it is the
1984 game's copyrighted data), so it is always user-supplied and always
optional: the game runs without any of it, in a degraded form.

That "optional" is exactly why locating it was a silent bug. Every call site
used a bare relative ``Path("out")/...``, so launching from anywhere but the
project root — a desktop shortcut, an installed entry point, Explorer's "Open
with" — found nothing and said nothing. The visible result was not merely
missing music: :func:`~alien_remake.core.opening_name.garbled_name_codes`
returns ``None`` without the BASIC ROM, so the opening prints the crew member's
*clean* name where the original prints the garbled one. A wrong working
directory quietly changed replica behaviour.

Search order, first hit wins:

1. ``$ALIEN_REMAKE_ASSETS`` — an explicit override, for packaged builds and for
   pointing at a second decode.
2. ``./out`` relative to the current directory — the existing dev workflow,
   preserved so ``python -m alien_remake`` from the repo behaves as it always
   has.
3. ``<repo>/out`` resolved from this file's own location — makes an editable
   install work from any directory.
4. ``<exe>/out`` when frozen (PyInstaller and friends set ``sys.frozen``).
5. The per-user data directory — ``%LOCALAPPDATA%\\alien-remake`` on Windows,
   ``$XDG_DATA_HOME`` or ``~/.local/share/alien-remake`` elsewhere. This is the
   one that makes an installed copy work, and the one a Linux/Steam build would
   use later; it costs a single ``sys.platform`` branch today.

Stdlib only, no pygame, importable from ``core`` — resolution is not a
rendering concern.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

#: Point this at a directory of decoded assets to override the search.
ENV_VAR = "ALIEN_REMAKE_ASSETS"

#: The historical name of the derived-output directory (``out/``), kept because
#: it is what ``alientools`` writes and what the docs and gitignore say.
DERIVED_DIR = "out"

#: Where the extracted CBM-DOS files land, under an asset root.
FILES_DIR = "Alien (USA, Europe)_files"


#: Force where settings and logs live. Set it and nothing below is consulted.
HOME_VAR = "ALIEN_REMAKE_HOME"


def _platform_data_dir() -> Path:
    """Per-user data directory, following each platform's own convention."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        return Path(base) / "alien-remake" if base else (
            Path.home() / "AppData" / "Local" / "alien-remake"
        )
    xdg = os.environ.get("XDG_DATA_HOME")
    return Path(xdg) / "alien-remake" if xdg else (
        Path.home() / ".local" / "share" / "alien-remake"
    )


def _beside_the_game() -> Path | None:
    """The working directory, if this looks like a copy you can write to.

    **Owner, 2026-08-30: "the log should be in the work folder."** Quite right
    for the case that actually exists — somebody running the game out of a
    checkout expects `logs/` and `settings.toml` to be *there*, not three
    directories deep in `AppData`, and having to be told where they went is a
    sign the default is wrong.

    The platform convention is not wrong either, though: it exists for the
    installed copy, where the program may sit somewhere unwritable and putting
    a log beside the executable either fails or scatters one player's data
    through another's. So both, chosen by whether writing there would work.

    "Looks like a copy you can write to" is deliberately two tests. `out/` says
    this is the game's own directory rather than whatever shell happened to be
    open — a bare `cd /` should not collect a `logs/` folder. Writability says
    the choice will not fail at the moment somebody needs the log.
    """
    here = Path.cwd()
    if not (here / DERIVED_DIR).is_dir():
        return None
    try:
        probe = here / ".alien-remake-write-test"
        probe.touch()
        probe.unlink()
    except OSError:
        return None
    return here


def _user_data_dir() -> Path:
    """Where settings and session logs live.

    In order: :data:`HOME_VAR` if set, the game's own directory when it is
    writable (:func:`_beside_the_game`), else the platform convention.
    """
    forced = os.environ.get(HOME_VAR)
    if forced:
        return Path(forced)
    local = _beside_the_game()
    return local if local is not None else _platform_data_dir()


def asset_roots() -> tuple[Path, ...]:
    """The directories searched for assets, in priority order, deduplicated.

    Not cached: ``$ALIEN_REMAKE_ASSETS`` and the working directory are both
    things a caller (and a test) may legitimately change at runtime.
    """
    roots: list[Path] = []
    override = os.environ.get(ENV_VAR)
    if override:
        roots.append(Path(override))
    roots.append(Path.cwd() / DERIVED_DIR)
    # This file is <repo>/src/alien_remake/assets.py, so two parents up is the
    # checkout root — an editable install then works from any directory.
    roots.append(Path(__file__).resolve().parent.parent.parent / DERIVED_DIR)
    if getattr(sys, "frozen", False):  # pragma: no cover - packaged builds only
        roots.append(Path(sys.executable).resolve().parent / DERIVED_DIR)
    roots.append(_user_data_dir())

    seen: set[Path] = set()
    unique: list[Path] = []
    for root in roots:
        try:
            key = root.resolve()
        except OSError:  # pragma: no cover - unresolvable path, just skip
            continue
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return tuple(unique)


def find(*parts: str) -> Path | None:
    """Return the first existing ``<root>/<*parts>``, or ``None``.

    ``None`` is a normal answer — every asset is optional — so callers keep
    their existing fallbacks. Use :func:`report` to tell the user what is
    missing rather than degrading in silence.
    """
    for root in asset_roots():
        candidate = root.joinpath(*parts)
        if candidate.exists():
            return candidate
    return None


#: What the game looks for, why it wants it, and how to produce it. Ordered by
#: how visible its absence is. Kept here so there is one list to update when an
#: asset is added, and so :func:`report` can explain itself.
KNOWN_ASSETS: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    ("charset", ("charset.bin",),
     "the game's own glyphs and sprites",
     "python -m alientools chars"),
    ("intro", ("intro.wav",),
     "the SID intro tune",
     "python -m alien_remake.audio.intro"),
    ("basic_rom", ("basic.bin",),
     "the BASIC ROM the opening's garbled victim name is read out of",
     "capture $A000-$BFFF, or use a VICE basic-901226-01.bin"),
    ("chargen", ("chargen.bin",),
     "the C64 character generator, for text the game's own charset lacks",
     "capture $D000-$DFFF from the chargen ROM"),
    ("menu1", (FILES_DIR, "MENU1.prg"),
     "the loader's BASIC, source of the on-screen instructions",
     "python -m alientools extract \"Alien (USA, Europe).nib\" --out out/"),
)


#: Assets that are **not** derived from the Alien disk and are **not** required.
#:
#: `basic.bin` and `chargen.bin` are C64 ROM images - the machine's, not the
#: game's - so no amount of extracting the .nib will produce them, and the
#: startup card telling a player their disk was decoded badly is simply untrue.
#: The game runs without both: the first only garbles the opening victim's name
#: the way the original does by reading whatever BASIC left in memory, and the
#: second only supplies glyphs the game's own charset lacks.
#:
#: Named here rather than as a fifth field on :data:`KNOWN_ASSETS` because that
#: tuple is unpacked in four places, and a set is the smaller change.
OPTIONAL: frozenset[str] = frozenset({"basic_rom", "chargen"})

#: Where the optional ones actually come from, since "decode your disk" is
#: wrong for both and a player following that advice will not find them.
OPTIONAL_SOURCE = (
    "these two are C64 ROM images, not game data - install VICE (or any C64 "
    "emulator) and they are found automatically, or drop "
    "basic-901226-01.bin and chargen-901225-01.bin into out/"
)


#: The two C64 ROMs, and the names VICE gives them. **Never vendored.** They
#: are Commodore's, and the whole project's convention is that a source is
#: located rather than copied in - which here is also the one thing that could
#: actually cause trouble for a public repository.
C64_ROMS: dict[str, tuple[str, int]] = {
    # our name    -> (the name VICE ships, exact size in bytes)
    "basic.bin": ("basic-901226-01.bin", 8192),
    "chargen.bin": ("chargen-901225-01.bin", 4096),
}


def _vice_rom_dirs() -> tuple[Path, ...]:
    """Where a normal VICE install keeps its ROMs, per platform.

    **VICE is never run.** The remake reads two files out of it and nothing
    else, so this is a file search, not a dependency - a player who already has
    any C64 emulator installed gets the fidelity for free and never learns that
    these files exist.

    Ordered, and deliberately generous: an install somewhere unusual still
    works by copying the two files into `out/`, which is what the search in
    `find` already covers.
    """
    dirs: list[Path] = []
    if sys.platform == "win32":
        for var in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
            base = os.environ.get(var)
            if base:
                dirs += [Path(base) / "VICE" / "C64", Path(base) / "VICE"]
        dirs.append(Path("C:/VICE/C64"))
    elif sys.platform == "darwin":
        dirs += [
            Path("/Applications/VICE/C64"),
            Path("/opt/homebrew/share/vice/C64"),
            Path("/usr/local/share/vice/C64"),
        ]
    else:
        dirs += [
            Path("/usr/share/vice/C64"),
            Path("/usr/local/share/vice/C64"),
            Path("/usr/lib/vice/C64"),
            Path.home() / ".local" / "share" / "vice" / "C64",
        ]
    return tuple(dirs)


def find_c64_rom(name: str) -> Path | None:
    """One of the machine's own ROMs: yours first, then any VICE install.

    ``name`` is our name for it (`basic.bin`, `chargen.bin`). Checked in order:

    1. the asset roots, so a copy you placed yourself always wins;
    2. the same file under VICE's own name in the asset roots, so dropping the
       download in unrenamed works too - being made to rename a file to satisfy
       a lookup is the sort of small indignity that makes people give up;
    3. a normal VICE installation for this platform.

    The size is checked because a truncated or wrong file is worse than a
    missing one: missing degrades gracefully and visibly, wrong draws nonsense.
    """
    vice_name, size = C64_ROMS[name]
    candidates: list[Path] = []
    for stem in (name, vice_name):
        got = find(stem)
        if got is not None:
            candidates.append(got)
    for directory in _vice_rom_dirs():
        candidates.append(directory / vice_name)
    # The copy archived in this checkout, last. It is a developer convenience
    # rather than a shipped asset - but it must be part of *this* search, not a
    # separate one in each reader, which is exactly the bug this replaced: the
    # readers found these files here while the startup card, asking a different
    # question, reported them missing. A report that disagrees with the program
    # it reports on is worse than no report.
    candidates.append(
        Path("Archive") / "vice-mcp" / "HeadlessVICE-windows-x86_64" / "C64"
        / vice_name
    )
    for candidate in candidates:
        try:
            if candidate.stat().st_size == size:
                return candidate
        except OSError:
            continue
    return None


def missing_required() -> list[str]:
    """The assets whose absence actually costs the player something."""
    return [
        "/".join(parts) for key, parts, _why, _how in KNOWN_ASSETS
        if key not in OPTIONAL and find(*parts) is None
    ]


def _covered_without_the_rom(key: str) -> bool:
    """Would this ROM's absence actually cost the player anything?

    Both of the optional ROMs now have the thing they were needed *for* recorded
    in the source, so absent is no longer the same as missing:

    * `basic_rom` - the opening notice's garbled name is seventy captured bytes
      (`opening_name.GARBLED_NAME_BYTES`), so the bug is reproduced regardless;
    * `chargen` - the glyph table may be embedded
      (`render.c64font_data`, optional), in which case the loader screens are
      drawn in the real font regardless.

    Reporting a file as absent when nothing depends on it any more is how a
    working install gets told it is broken, which is the mistake this whole
    thread of work started from.
    """
    if key == "basic_rom":
        return True
    if key == "chargen":
        try:
            from .render import c64font_data  # noqa: F401
        except ImportError:
            return False
        return True
    return False


def missing_optional() -> list[str]:
    """The absent extras **that would actually change something**.

    Asks `find_c64_rom`, so a player with VICE installed is told nothing at all;
    and asks `_covered_without_the_rom`, so a player with neither is also told
    nothing when the thing the ROM was for is recorded in the source anyway.
    """
    return [
        "/".join(parts) for key, parts, _why, _how in KNOWN_ASSETS
        if key in OPTIONAL
        and find_c64_rom("/".join(parts)) is None
        and not _covered_without_the_rom(key)
    ]


def report() -> list[str]:
    """One line per missing asset, naming what it costs and how to make it.

    Empty when everything resolved. The launcher prints this once at startup;
    silence about a missing asset is what made this a bug rather than a
    limitation.
    """
    missing = []
    for _, parts, why, how in KNOWN_ASSETS:
        if find(*parts) is None:
            # ASCII only: this reaches a Windows console, which is cp1252 by
            # default and cannot carry the em-dash used elsewhere in this
            # codebase's prose.
            missing.append(f"  {'/'.join(parts)} - {why}\n      make it with: {how}")
    return missing
