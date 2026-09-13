"""The **standard C64 character ROM** — the font the loader screens really use.

D-065 (2026-08-01). ALIEN's own charset (``render.tiles``) is a *cut-out* font
and is correct for the play screen, but the front-end screens (LOADING /
NOTICE / WELCOME / INSTRUCTIONS) are drawn by the loader programs
(``MENU``/``MENUA``/``MENU1``) **before** ``ALIEN.prg`` ever repoints the VIC at
its own charset (``set_charbase $400A`` sets ``$D018`` -> ``$2000``). They use
the machine's ROM font — see D-047. Until now the remake approximated that with
``pygame.font.SysFont("monospace")``, which is ~4.3px wide inside an 8px cell
and reads visibly sparse and un-C64.

This module loads the real 4KB chargen ROM so those screens can be drawn
pixel-exact instead. The ROM is **not vendored into the repo** (it is
Commodore's, and reproducing it here would make it a *source* rather than a
derived artifact, against the project's conventions): it is located at runtime
from paths that already exist on this machine, and every entry point degrades
to ``None`` when it isn't found, so the SysFont path stays as the fallback and
nothing hard-depends on it.

Layout: 4096 bytes = two 2KB banks of 256 glyphs x 8 rows, MSB-left.

* bank 0 — **unshifted** (uppercase + graphics). Screen codes ``$01-$1A`` are
  ``A-Z``. This is what WELCOME uses (its screen RAM reads ``07 12 05 05 0E``
  for "GREEN", and it renders in capitals).
* bank 1 — **shifted** (lowercase + uppercase). ``$01-$1A`` are ``a-z`` and
  ``$41-$5A`` are ``A-Z``. This is what NOTICE uses — its text is genuinely
  mixed case ("We strongly suggest you").

In both banks the ASCII range ``$20-$3F`` (space, punctuation, digits, ``:``)
maps to itself, which is why digits and ``:`` need no special-casing here —
unlike ALIEN's custom charset, where their positions are still ``[?]``.
"""

from __future__ import annotations

from pathlib import Path

from .. import assets

# Where the real ROM already lives on this machine. Checked in order; the first
# readable 4096-byte file wins. `out/` comes first so a deliberate local copy
# (a derived artifact, per the project's conventions) overrides the tool's.
#: **The archived VICE copy moved into `assets.find_c64_rom`**
#: (2026-08-30). It used to be a private fallback here, which meant
#: this module and the startup card searched different places and
#: disagreed about whether the ROM was present. One search now.


def _search_paths() -> tuple[Path, ...]:
    """Candidates in order. Resolved per call — the working directory and
    ``$ALIEN_REMAKE_ASSETS`` can both change between calls."""
    # As `opening_name`: your own copy first, then any VICE install, so the
    # loader screens are drawn in the real C64 font on any machine that has an
    # emulator rather than only on one that has been told about this.
    found = assets.find_c64_rom("chargen.bin")
    return (found,) if found is not None else ()

_ROM_BYTES = 4096
_BANK_BYTES = 2048


class RomFont:
    """An 8x8 glyph source backed by the C64 character ROM."""

    def __init__(self, data: bytes) -> None:
        if len(data) != _ROM_BYTES:
            raise ValueError(f"chargen ROM must be {_ROM_BYTES} bytes, got {len(data)}")
        self._data = data

    @staticmethod
    def screen_code(ch: str, *, shifted: bool = False) -> int | None:
        """Screen code for ``ch`` in the selected bank, or ``None`` if unmapped.

        Never guesses: an unmapped character returns ``None`` so the caller can
        fall back rather than draw a wrong glyph.
        """
        o = ord(ch)
        if shifted:
            if "a" <= ch <= "z":
                return o - 0x60          # $01-$1A are lowercase in bank 1
            if "A" <= ch <= "Z":
                return o                 # $41-$5A are uppercase in bank 1
        else:
            if "A" <= ch <= "Z":
                return o - 0x40          # $01-$1A are uppercase in bank 0
            if "a" <= ch <= "z":
                return o - 0x60          # bank 0 has no lowercase; show capitals
        if 0x20 <= o <= 0x3F:
            return o                     # space, punctuation, digits, ':'
        if ch == "@":
            return 0
        return None

    def glyph_rows(self, code: int, *, shifted: bool = False) -> tuple[int, ...]:
        """The 8 bitmap rows for ``code`` (each an 8-bit int, MSB = leftmost)."""
        base = (_BANK_BYTES if shifted else 0) + (code & 0xFF) * 8
        return tuple(self._data[base:base + 8])

    def text_rows(self, text: str, *, shifted: bool = False) -> list[tuple[int, ...]] | None:
        """Per-character bitmaps for ``text``, or ``None`` if any char is unmapped."""
        out: list[tuple[int, ...]] = []
        for ch in text:
            code = self.screen_code(ch, shifted=shifted)
            if code is None:
                return None
            out.append(self.glyph_rows(code, shifted=shifted))
        return out


def load(path: Path | None = None) -> RomFont | None:
    """Load the chargen ROM, or ``None`` when it isn't available.

    Returning ``None`` rather than raising is deliberate: the ROM is optional,
    and the renderer must still work (via SysFont) on a machine without it.
    """
    candidates = (path,) if path is not None else _search_paths()
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            data = candidate.read_bytes()
        except OSError:
            continue
        if len(data) == _ROM_BYTES:
            return RomFont(data)
    if path is None:
        embedded = _embedded()
        if embedded is not None:
            return embedded
    return None


def _embedded() -> RomFont | None:
    """The glyph table, if this checkout carries one. **Optional by design.**

    `render.c64font_data` is not part of the package: it is generated by
    `tools/embed_c64_font.py` from a ROM the person running it already has, and
    it is imported here defensively so that a checkout without it behaves
    exactly as this module did before the option existed - SysFont, and no
    complaint.

    That is the whole arrangement. Including Commodore's glyph bitmaps is a
    judgement about redistribution rather than a technical question, so the code
    is built to work either way and the bytes are one file that can be added or
    deleted without touching anything else.
    """
    try:
        # No `type: ignore` needed while the module is committed. If it is
        # deleted (which is the supported way to undo the decision to embed the
        # font) mypy will want one back - the `except ImportError` below is
        # what makes the runtime work either way.
        from . import c64font_data
    except ImportError:
        return None
    try:
        data = c64font_data.glyph_rom()
    except Exception:                        # pragma: no cover - corrupt table
        return None
    return RomFont(data) if len(data) == _ROM_BYTES else None
