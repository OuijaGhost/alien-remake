"""Extract the game's own C64 character set (and sprites) as derived artefacts.

``ALIEN`` loads at ``$2000`` and its first 8 KiB (``$2000-$3FFF``) is graphics
**data**, not code (/ DISCOVERIES D-007; the entry point is ``$4000``). At
init the game does ``LDA $D018 / AND #$F0 / ADC #$08 / STA $D018`` (codemap
``$400A``), which points the VIC-II character base at ``$2000`` within its bank:
the custom 256-glyph character set lives in the first 2 KiB of the region, and
the remaining 6 KiB (``$2800-$3FFF``) holds sprite data.

This module turns that region into **derived** artefacts (DECISIONS D-009): the
256 8x8 glyphs and the 24x21 sprites, plus a tiny stdlib PNG writer so the
toolkit can emit ``out/charset.png`` / ``out/sprites.png`` without any
third-party dependency (Phase 1 stays stdlib-only). Decoding is a pure,
lossless bit expansion (each glyph byte -> 8 pixels, MSB first); the exact
*meaning* of individual glyphs (which is a wall, which a floor) is a ``[?]`` the
remake layer resolves, not this decoder.

Nothing here writes the source ``.nib``; it operates on already-extracted bytes.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

# --- Region geometry (single source of truth for the $2000-$3FFF layout) ------

CHARSET_LOAD = 0x2000  # ALIEN's load address; the graphics region starts here.
REGION_BYTES = 0x2000  # $2000-$3FFF inclusive = 8 KiB.

GLYPH_BYTES = 8        # one C64 text glyph = 8 bytes (8 rows).
GLYPH_W = 8
GLYPH_H = 8
CHARSET_GLYPHS = 256   # a full C64 character set.
CHARSET_BYTES = CHARSET_GLYPHS * GLYPH_BYTES  # 2048 -> first 2 KiB of the region.

SPRITE_OFFSET = CHARSET_BYTES  # sprites follow the charset, at $2800.
SPRITE_BYTES = 64      # a C64 sprite is 63 bytes (24x21) padded to a 64 boundary.
SPRITE_W = 24
SPRITE_H = 21
SPRITE_ROW_BYTES = SPRITE_W // 8  # 3 bytes per sprite row.
SPRITE_SLOTS = (REGION_BYTES - SPRITE_OFFSET) // SPRITE_BYTES  # 96 slots in 6 KiB.


class CharsetError(ValueError):
    """The bytes handed in are not the expected ALIEN graphics region."""


Bitmap = tuple[tuple[int, ...], ...]  # rows of 0/1 pixels, top-to-bottom.


# --- Bit decode (pure, lossless) ----------------------------------------------

def decode_glyph(data: bytes) -> Bitmap:
    """Expand one 8-byte C64 glyph into an 8x8 grid of 0/1 pixels (MSB first)."""
    if len(data) != GLYPH_BYTES:
        raise CharsetError(f"glyph needs {GLYPH_BYTES} bytes, got {len(data)}")
    return tuple(
        tuple((byte >> (7 - col)) & 1 for col in range(GLYPH_W)) for byte in data
    )


def decode_charset(region: bytes, count: int = CHARSET_GLYPHS) -> list[Bitmap]:
    """Decode the first ``count`` glyphs from a graphics region (charset at $2000)."""
    need = count * GLYPH_BYTES
    if len(region) < need:
        raise CharsetError(f"need {need} bytes for {count} glyphs, got {len(region)}")
    return [decode_glyph(region[i * GLYPH_BYTES:(i + 1) * GLYPH_BYTES]) for i in range(count)]


def decode_sprite(data: bytes) -> Bitmap:
    """Expand one C64 sprite (63 significant bytes, 24x21) into a 0/1 bitmap."""
    if len(data) < SPRITE_ROW_BYTES * SPRITE_H:
        raise CharsetError(
            f"sprite needs {SPRITE_ROW_BYTES * SPRITE_H} bytes, got {len(data)}"
        )
    rows: list[tuple[int, ...]] = []
    for r in range(SPRITE_H):
        base = r * SPRITE_ROW_BYTES
        row: list[int] = []
        for b in range(SPRITE_ROW_BYTES):
            byte = data[base + b]
            row.extend((byte >> (7 - bit)) & 1 for bit in range(8))
        rows.append(tuple(row))
    return tuple(rows)


# --- Multicolor sprites (R-03) ------------------------------------------------
#
# A C64 sprite drawn with its multicolor bit set trades horizontal resolution
# for colour: the 24 bits of each row are read as **12 bit-PAIRS**, each
# painted as a double-width pixel. The pair value selects the source colour:
#
#   00 -> transparent (the background shows through)
#   01 -> the shared multicolor register 0 (`$D025`)
#   10 -> this sprite's own colour (`$D027+n`)
#   11 -> the shared multicolor register 1 (`$D026`)
#
# The hi-res :func:`decode_sprite` above cannot represent this — it would
# decode a multicolor sprite as meaningless "noise", which is exactly what the
# title screen's alien egg looked like before D-021 handled it inline. This
# decoder returns the raw 0-3 pair values so a caller can map them to whatever
# palette the routine that draws them installs.

#: One multicolor sprite row: 12 values in 0-3 (see the table above).
MC_SPRITE_W = SPRITE_W // 2  # 12 double-width pixels per row.
MCBitmap = tuple[tuple[int, ...], ...]


def decode_sprite_multicolor(data: bytes) -> MCBitmap:
    """Expand one C64 sprite as **multicolor**: 12x21 values in 0-3.

    Same 63 significant bytes as :func:`decode_sprite`, but each row's 3 bytes
    are read as 12 bit-pairs rather than 24 individual bits. Values are the
    raw pair codes (0 = transparent, 1 = `$D025`, 2 = sprite colour,
    3 = `$D026`); mapping them to actual colours is the caller's job, since
    the registers are set by whichever routine draws the sprite.
    """
    if len(data) < SPRITE_ROW_BYTES * SPRITE_H:
        raise CharsetError(
            f"sprite needs {SPRITE_ROW_BYTES * SPRITE_H} bytes, got {len(data)}"
        )
    rows: list[tuple[int, ...]] = []
    for r in range(SPRITE_H):
        base = r * SPRITE_ROW_BYTES
        row: list[int] = []
        for b in range(SPRITE_ROW_BYTES):
            byte = data[base + b]
            # Bit-pairs, most significant first: bits 7-6, 5-4, 3-2, 1-0.
            row.extend((byte >> (6 - 2 * pair)) & 0b11 for pair in range(4))
        rows.append(tuple(row))
    return tuple(rows)


def decode_sprites_multicolor(
    region: bytes, count: int = SPRITE_SLOTS
) -> list[MCBitmap]:
    """Decode every sprite slot as multicolor (see :func:`decode_sprite_multicolor`)."""
    out: list[MCBitmap] = []
    for i in range(count):
        base = SPRITE_OFFSET + i * SPRITE_BYTES
        chunk = region[base:base + SPRITE_BYTES]
        if len(chunk) < SPRITE_ROW_BYTES * SPRITE_H:
            break  # region ran out; stop rather than pad with garbage.
        out.append(decode_sprite_multicolor(chunk))
    return out


def decode_sprites(region: bytes, count: int = SPRITE_SLOTS) -> list[Bitmap]:
    """Decode the sprite slots that follow the charset ($2800 onward)."""
    out: list[Bitmap] = []
    for i in range(count):
        base = SPRITE_OFFSET + i * SPRITE_BYTES
        chunk = region[base:base + SPRITE_BYTES]
        if len(chunk) < SPRITE_ROW_BYTES * SPRITE_H:
            break  # region ran out; stop rather than pad with garbage.
        out.append(decode_sprite(chunk))
    return out


# --- Region sourcing ----------------------------------------------------------

def region_from_prg(prg: bytes) -> bytes:
    """Return the 8 KiB ``$2000-$3FFF`` graphics region from an ``ALIEN`` PRG.

    ``prg`` is a CBM PRG: a 2-byte little-endian load address followed by the
    body. Verifies the load address is ``$2000`` (so this really is ALIEN) and
    returns the first :data:`REGION_BYTES` body bytes.
    """
    if len(prg) < 2:
        raise CharsetError("not a PRG: fewer than 2 bytes")
    load = prg[0] | (prg[1] << 8)
    if load != CHARSET_LOAD:
        raise CharsetError(
            f"expected load ${CHARSET_LOAD:04X} (ALIEN), got ${load:04X}"
        )
    body = prg[2:]
    if len(body) < REGION_BYTES:
        raise CharsetError(
            f"PRG body {len(body)} bytes < {REGION_BYTES}-byte graphics region"
        )
    return body[:REGION_BYTES]


# --- Minimal stdlib PNG writer (grayscale, 8-bit) -----------------------------

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    body = tag + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def _grayscale_png(width: int, height: int, pixels: bytes) -> bytes:
    """Encode a width*height grayscale image (one byte/pixel) as PNG bytes."""
    if len(pixels) != width * height:
        raise CharsetError(f"pixel buffer is {len(pixels)}, expected {width * height}")
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None) for each scanline.
        raw.extend(pixels[y * width:(y + 1) * width])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)  # 8-bit grayscale.
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )


def _tile_sheet(tiles: list[Bitmap], cols: int, scale: int) -> bytes:
    """Lay out equal-size bitmaps into a grid and encode as a grayscale PNG.

    Foreground (1) -> white (255) on a black (0) background; each tile is
    nearest-neighbour scaled by ``scale``. Tiles must all share the first tile's
    dimensions (glyphs are 8x8, sprites 24x21).
    """
    if not tiles:
        raise CharsetError("no tiles to render")
    if scale < 1:
        raise CharsetError("scale must be >= 1")
    th = len(tiles[0])
    tw = len(tiles[0][0])
    rows = (len(tiles) + cols - 1) // cols
    width = cols * tw * scale
    height = rows * th * scale
    buf = bytearray(width * height)  # zero-filled = black background.
    for idx, tile in enumerate(tiles):
        gx = (idx % cols) * tw * scale
        gy = (idx // cols) * th * scale
        for y, line in enumerate(tile):
            for x, on in enumerate(line):
                if not on:
                    continue
                px0 = gx + x * scale
                py0 = gy + y * scale
                for dy in range(scale):
                    base = (py0 + dy) * width + px0
                    for dx in range(scale):
                        buf[base + dx] = 255
    return _grayscale_png(width, height, bytes(buf))


def charset_png(glyphs: list[Bitmap], cols: int = 16, scale: int = 1) -> bytes:
    """Render 256 glyphs into a 16x16 tile atlas (128x128 at scale 1)."""
    return _tile_sheet(glyphs, cols, scale)


def sprite_sheet_png(sprites: list[Bitmap], cols: int = 8, scale: int = 1) -> bytes:
    """Render the decoded sprites into a grid sheet."""
    return _tile_sheet(sprites, cols, scale)


#: Grey levels used to visualise the four multicolor pair codes in the derived
#: PNG. These are **not** the game's colours (those live in `$D025`/`$D026`/
#: `$D027+n`, set by whichever routine draws the sprite) — just four
#: distinguishable levels so the shape is legible in a static sheet.
MC_PREVIEW_LEVELS = (0, 96, 176, 255)


def sprite_sheet_multicolor_png(
    sprites: list[MCBitmap], cols: int = 8, scale: int = 1
) -> bytes:
    """Render multicolor-decoded sprites into a grid sheet (R-03).

    Each 12-wide multicolor row is drawn at **double width** so the sheet keeps
    the sprite's real 24x21 aspect. Pair codes map to
    :data:`MC_PREVIEW_LEVELS` greys, not to the game's real palette.
    """
    if not sprites:
        raise CharsetError("no tiles to render")
    if scale < 1:
        raise CharsetError("scale must be >= 1")
    th = len(sprites[0])
    tw = len(sprites[0][0]) * 2  # double-width pixels
    rows = (len(sprites) + cols - 1) // cols
    width = cols * tw * scale
    height = rows * th * scale
    buf = bytearray(width * height)
    for idx, tile in enumerate(sprites):
        gx = (idx % cols) * tw * scale
        gy = (idx // cols) * th * scale
        for y, line in enumerate(tile):
            for x, val in enumerate(line):
                if not val:
                    continue
                level = MC_PREVIEW_LEVELS[val]
                px0 = gx + x * 2 * scale
                py0 = gy + y * scale
                for dy in range(scale):
                    base = (py0 + dy) * width + px0
                    for dx in range(2 * scale):
                        buf[base + dx] = level
    return _grayscale_png(width, height, bytes(buf))


@dataclass(frozen=True)
class Assets:
    """The decoded graphics from ALIEN's ``$2000-$3FFF`` region."""

    region: bytes             # the raw 8 KiB (derived; reproducible from the .nib)
    glyphs: list[Bitmap]      # 256 8x8 character glyphs
    sprites: list[Bitmap]     # 24x21 sprite bitmaps (best-effort; boundaries [?])


def decode_assets(prg: bytes) -> Assets:
    """Decode the charset and sprites from an ``ALIEN`` PRG's graphics region."""
    region = region_from_prg(prg)
    return Assets(
        region=region,
        glyphs=decode_charset(region),
        sprites=decode_sprites(region),
    )
