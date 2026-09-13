"""Tests for the real per-deck backdrop decoder (follow-up, headless, no pygame)."""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.render.deck_backdrop import (
    BACKDROP_ROWS,
    SCREEN_COLS,
    decode_screen_dump,
    load_deck_backdrops,
)

REFERENCE_DIR = Path(__file__).resolve().parents[1] / "archive" / "reference"


def _fake_dump(fill: int) -> bytes:
    header = bytes([0x00, 0x04])  # VICE load-address header: $0400
    body = bytes([fill]) * (SCREEN_COLS * 25)
    return header + body


def test_decode_screen_dump_strips_header_and_shapes_the_grid() -> None:
    codes = decode_screen_dump(_fake_dump(0xA0))
    assert len(codes) == BACKDROP_ROWS
    assert all(len(row) == SCREEN_COLS for row in codes)
    assert codes[0][0] == 0xA0
    assert codes[-1][-1] == 0xA0


def test_decode_screen_dump_tolerates_a_short_capture() -> None:
    # Fewer than BACKDROP_ROWS*SCREEN_COLS body bytes: rows past the data are empty.
    codes = decode_screen_dump(bytes([0x00, 0x04]) + bytes([1, 2, 3]))
    assert codes[0][:3] == (1, 2, 3)
    assert codes[1] == ()


def test_load_deck_backdrops_skips_missing_files(tmp_path: Path) -> None:
    (tmp_path / "upperdeck_0400.bin").write_bytes(_fake_dump(0x05))
    backdrops = load_deck_backdrops(tmp_path)
    assert set(backdrops) == {0}  # only the deck whose file exists
    assert backdrops[0].codes[0][0] == 0x05


def test_load_deck_backdrops_on_a_directory_with_nothing_is_empty(tmp_path: Path) -> None:
    assert load_deck_backdrops(tmp_path) == {}


@pytest.mark.skipif(
    not REFERENCE_DIR.exists(), reason="archive/reference captures not present"
)
def test_real_captures_decode_to_the_expected_shape() -> None:
    backdrops = load_deck_backdrops(REFERENCE_DIR)
    assert set(backdrops) == {0, 1, 2}
    for backdrop in backdrops.values():
        assert len(backdrop.codes) == BACKDROP_ROWS
        assert all(len(row) == SCREEN_COLS for row in backdrop.codes)
        # 0xA0 (the background/floor fill) is the single most common code in
        # every real capture — everything else is wall/text glyphs sprinkled
        # sparsely by comparison.
        from collections import Counter

        flat = [c for row in backdrop.codes for c in row]
        [(top_code, _top_count)] = Counter(flat).most_common(1)
        assert top_code == 0xA0
