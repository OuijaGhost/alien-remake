"""Load the game's original C64 tiles for the remake (headless, stdlib only).

The remake draws with the game's **own** graphics rather than invented art
(DECISIONS D-009): the toolkit's ``alientools.charset`` extracts ALIEN's charset
+ sprites from the disk, and this module loads those bitmaps into a
backend-agnostic :class:`TileSet`. It imports no pygame, so the core and its
tests can reason about tiles headlessly; :mod:`alien_remake.render.pygame_app`
turns a :class:`TileSet` into GPU/blittable Surfaces at draw time.

A tile here is a grid of 0/1 pixels (:data:`alientools.charset.Bitmap`) — the
lossless bit expansion of a glyph/sprite. *Which* glyph means wall vs. floor is
still a ``[?]`` (the map is a grid; the glyph mapping is chosen in the
render layer), so this loader stays neutral: it just makes the authentic tiles
available.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alientools import charset
from alientools.charset import Bitmap


@dataclass(frozen=True)
class TileSet:
    """The original C64 glyphs + sprites, ready for a backend to rasterize."""

    glyphs: list[Bitmap]
    sprites: list[Bitmap]
    #: The raw ``$2000-$3FFF`` graphics-bank bytes this set was decoded from,
    #: kept so a backend can decode *multicolor* sprites (bit-pair pixels) that
    #: the single-colour :attr:`sprites` bitmaps can't represent — e.g. the
    #: title's 8-sprite alien egg (pointers ``$C9-$D0`` → bank ``$3240-$343F``).
    region: bytes

    @property
    def glyph_size(self) -> tuple[int, int]:
        return (charset.GLYPH_W, charset.GLYPH_H)

    @property
    def sprite_size(self) -> tuple[int, int]:
        return (charset.SPRITE_W, charset.SPRITE_H)

    def glyph(self, index: int) -> Bitmap:
        """Return glyph ``index`` (0-255), wrapping so callers never index out."""
        return self.glyphs[index % len(self.glyphs)]


def from_region(region: bytes) -> TileSet:
    """Build a :class:`TileSet` from a raw ``$2000-$3FFF`` graphics region."""
    return TileSet(
        glyphs=charset.decode_charset(region),
        sprites=charset.decode_sprites(region),
        region=bytes(region),
    )


def load(path: str | Path) -> TileSet:
    """Load a :class:`TileSet` from ``out/charset.bin`` or an ``ALIEN`` PRG.

    Accepts either the derived 8 KiB region dump (``charset.bin``) or the full
    PRG (2-byte load header + body); the load header is detected and stripped.
    """
    data = Path(path).read_bytes()
    if len(data) >= 2 and (data[0] | (data[1] << 8)) == charset.CHARSET_LOAD:
        region = charset.region_from_prg(data)
    else:
        region = data
    return from_region(region)
