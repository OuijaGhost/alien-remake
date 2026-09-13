"""Tests for the C64 charset/sprite extraction (SG).

The bit-level decode is lossless and deterministic, so we assert exact bitmaps
for known bytes, that the tiny stdlib PNG writer produces a spec-valid,
losslessly-decodable image, and that a real region (the extracted ALIEN PRG /
the reference $2000-$3FFF dump) decodes to a full 256-glyph charset.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import pytest

from alientools import charset

REF_DUMP = Path("archive/reference/map_2000_3ff.bin")  # a $2000-$3FFF VICE dump (PRG-shaped)
ALIEN_PRG = Path("out/Alien (USA, Europe)_files/ALIEN.prg")


# --- glyph decode -------------------------------------------------------------

def test_decode_glyph_all_set_and_clear() -> None:
    assert charset.decode_glyph(b"\xff" * 8) == tuple((1,) * 8 for _ in range(8))
    assert charset.decode_glyph(b"\x00" * 8) == tuple((0,) * 8 for _ in range(8))


def test_decode_glyph_msb_first() -> None:
    # 0x80 = leftmost pixel only; 0x81 = leftmost + rightmost.
    top = charset.decode_glyph(bytes([0x80, 0x81, 0, 0, 0, 0, 0, 0]))
    assert top[0] == (1, 0, 0, 0, 0, 0, 0, 0)
    assert top[1] == (1, 0, 0, 0, 0, 0, 0, 1)


def test_decode_glyph_bad_length() -> None:
    with pytest.raises(charset.CharsetError):
        charset.decode_glyph(b"\x00" * 7)


def test_decode_charset_count_and_shape() -> None:
    region = bytes(range(256)) * 8  # 2048 bytes -> 256 glyphs.
    glyphs = charset.decode_charset(region)
    assert len(glyphs) == charset.CHARSET_GLYPHS
    assert all(len(g) == 8 and all(len(row) == 8 for row in g) for g in glyphs)


def test_decode_charset_short_region() -> None:
    with pytest.raises(charset.CharsetError):
        charset.decode_charset(b"\x00" * 16, count=4)


# --- sprite decode ------------------------------------------------------------

def test_decode_sprite_dimensions_and_bits() -> None:
    data = bytes([0x80, 0x00, 0x01] * charset.SPRITE_H)  # first + last column set.
    sprite = charset.decode_sprite(data)
    assert len(sprite) == charset.SPRITE_H
    assert all(len(row) == charset.SPRITE_W for row in sprite)
    assert sprite[0][0] == 1 and sprite[0][charset.SPRITE_W - 1] == 1
    assert sprite[0][1] == 0


# --- region sourcing ----------------------------------------------------------

def test_region_from_prg_rejects_wrong_load() -> None:
    prg = bytes([0x00, 0x40]) + b"\x00" * charset.REGION_BYTES  # load $4000, not $2000.
    with pytest.raises(charset.CharsetError):
        charset.region_from_prg(prg)


def test_region_from_prg_rejects_short_body() -> None:
    prg = bytes([0x00, 0x20]) + b"\x00" * 100
    with pytest.raises(charset.CharsetError):
        charset.region_from_prg(prg)


def test_region_from_prg_ok() -> None:
    prg = bytes([0x00, 0x20]) + bytes(range(256)) * 40  # 10240 body bytes.
    region = charset.region_from_prg(prg)
    assert len(region) == charset.REGION_BYTES


# --- PNG writer (round-trip, spec-valid) --------------------------------------

def _decode_grayscale_png(data: bytes) -> tuple[int, int, bytes]:
    """Minimal PNG reader for the test: assumes 8-bit grayscale, filter 0."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos = 8
    width = height = 0
    idat = b""
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if tag == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert (depth, ctype) == (8, 0)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + length
    raw = zlib.decompress(idat)
    pixels = bytearray()
    stride = width + 1
    for y in range(height):
        assert raw[y * stride] == 0  # filter type None
        pixels.extend(raw[y * stride + 1:(y + 1) * stride])
    return width, height, bytes(pixels)


def test_charset_png_dimensions_and_pixels() -> None:
    # Glyph 0 fully set, glyph 1 fully clear; the rest clear.
    region = bytearray(charset.CHARSET_BYTES)
    region[0:8] = b"\xff" * 8
    glyphs = charset.decode_charset(bytes(region))
    png = charset.charset_png(glyphs)  # 16x16 grid of 8x8 -> 128x128
    w, h, pixels = _decode_grayscale_png(png)
    assert (w, h) == (128, 128)
    # Top-left 8x8 tile (glyph 0) is white; the tile to its right (glyph 1) black.
    assert pixels[0] == 255 and pixels[7] == 255
    assert pixels[8] == 0


def test_tile_sheet_scale() -> None:
    glyphs = charset.decode_charset(bytes(charset.CHARSET_BYTES))
    png = charset.charset_png(glyphs, scale=2)
    w, h, _ = _decode_grayscale_png(png)
    assert (w, h) == (256, 256)


# --- real data ----------------------------------------------------------------

def _real_prg() -> bytes | None:
    for p in (ALIEN_PRG, REF_DUMP):
        if p.exists():
            return p.read_bytes()
    return None


def test_real_region_decodes_full_charset() -> None:
    prg = _real_prg()
    if prg is None:
        pytest.skip("no extracted ALIEN.prg or reference dump available")
    assets = charset.decode_assets(prg)
    assert len(assets.region) == charset.REGION_BYTES
    assert len(assets.glyphs) == charset.CHARSET_GLYPHS
    assert len(assets.sprites) == charset.SPRITE_SLOTS
    # Sanity: a real font is neither all-blank nor all-set.
    lit = sum(sum(row) for g in assets.glyphs for row in g)
    assert 0 < lit < charset.CHARSET_GLYPHS * 64


# --- R-03: multicolor sprite decoding ----------------------------------------


def test_decode_sprite_multicolor_reads_bit_pairs() -> None:
    """R-03: a multicolor sprite row is 12 double-width pixels read as bit
    PAIRS (00 transparent / 01 $D025 / 10 sprite colour / 11 $D026), not 24
    individual bits. `0b00011011` must decode to the four codes 0,1,2,3."""
    data = bytes([0b00011011, 0x00, 0x00] * charset.SPRITE_H)
    mc = charset.decode_sprite_multicolor(data)
    assert len(mc) == charset.SPRITE_H
    assert len(mc[0]) == charset.MC_SPRITE_W == 12
    assert mc[0][:4] == (0, 1, 2, 3)      # the pairs of the first byte
    assert mc[0][4:] == (0,) * 8          # the two zero bytes


def test_decode_sprite_multicolor_rejects_short_data() -> None:
    with pytest.raises(charset.CharsetError):
        charset.decode_sprite_multicolor(b"\x00" * 10)


def test_decode_sprites_multicolor_covers_every_slot() -> None:
    region = bytes(charset.REGION_BYTES)
    mc = charset.decode_sprites_multicolor(region)
    assert len(mc) == charset.SPRITE_SLOTS
    assert all(len(row) == charset.MC_SPRITE_W for sprite in mc for row in sprite)


def test_multicolor_sheet_is_double_width_and_a_valid_png() -> None:
    """The sheet keeps the sprite's real 24x21 aspect by drawing each of the
    12 multicolor pixels double-width."""
    region = bytes(charset.REGION_BYTES)
    mc = charset.decode_sprites_multicolor(region)[:8]
    png = charset.sprite_sheet_multicolor_png(mc, cols=8, scale=1)
    width, height, _pixels = _decode_grayscale_png(png)
    # 8 sprites across, each 12 pairs * 2 = 24px wide.
    assert (width, height) == (8 * 24, charset.SPRITE_H)
