"""Tests for the MNIB container parser and the ``inspect`` subcommand.

Exercises both the real source ``.nib`` (read-only invariant) and a small
synthetic fixture so failures localise to the parser, not the 327 KB dump.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from alientools import cli, nib

import needs                                       # noqa: E402

# The real source image lives in the project root (one level above tests/).
REAL_NIB = Path(__file__).resolve().parent.parent / "Alien (USA, Europe).nib"


def make_nib(
    entries: list[tuple[int, int]],
    *,
    version: int = 1,
    signature: bytes = nib.SIGNATURE,
    n_data_tracks: int | None = None,
    fill: int = 0x55,
) -> bytes:
    """Build a minimal valid (or deliberately broken) MNIB image.

    ``entries`` is a list of ``(halftrack, density_byte)`` table rows. By
    default one 8192-byte data track is emitted per entry, each filled with
    ``fill`` xored with its index so tracks are distinguishable.
    """
    header = bytearray(nib.HEADER_SIZE)
    header[: len(signature)] = signature
    if len(signature) < nib.HEADER_SIZE:
        header[len(signature)] = version
    pos = nib.TRACK_TABLE_OFFSET
    for halftrack, density in entries:
        header[pos] = halftrack
        header[pos + 1] = density
        pos += 2

    count = len(entries) if n_data_tracks is None else n_data_tracks
    body = bytearray()
    for i in range(count):
        body += bytes([(fill ^ i) & 0xFF]) * nib.TRACK_DATA_SIZE
    return bytes(header) + bytes(body)


# --- synthetic-fixture parsing -------------------------------------------------


def test_parse_synthetic_basic() -> None:
    raw = make_nib([(2, 0x03), (4, 0x02)], version=7)
    img = nib.parse(raw)
    assert img.version == 7
    assert len(img) == 2
    t0, t1 = img.tracks
    assert (t0.halftrack, t0.density, t0.flags) == (2, 3, 0)
    assert t0.track_number == 1.0 and not t0.is_halftrack
    assert t0.offset == nib.HEADER_SIZE
    assert len(t0.data) == nib.TRACK_DATA_SIZE
    assert t1.offset == nib.HEADER_SIZE + nib.TRACK_DATA_SIZE
    # Data is sliced per-track, not shared.
    assert t0.data[0] != t1.data[0]


def test_density_flags_split_from_zone() -> None:
    # 0x42 = NO_SYNC (0x40) | density 2.
    img = nib.parse(make_nib([(74, 0x42)]))
    t = img.tracks[0]
    assert t.density == 2
    assert t.flags == nib.BM_NO_SYNC
    assert t.flag_names == ("NO_SYNC",)
    assert nib.density_flag_names(0x42) == ("NO_SYNC",)
    assert nib.density_flag_names(0x00) == ()


def test_halftrack_detection() -> None:
    img = nib.parse(make_nib([(3, 0x03)]))
    t = img.tracks[0]
    assert t.is_halftrack
    assert t.track_number == 1.5


def test_table_terminates_on_zero_halftrack() -> None:
    # Three table slots but the middle entry has halftrack 0 -> stop early.
    raw = make_nib([(2, 0x03), (0, 0x00), (6, 0x03)], n_data_tracks=3)
    img = nib.parse(raw)
    assert len(img) == 1


# --- malformed containers raise NibError --------------------------------------


def test_bad_signature_raises() -> None:
    raw = make_nib([(2, 0x03)], signature=b"NOTANIBFILE!!")
    with pytest.raises(nib.NibError, match="signature"):
        nib.parse(raw)


def test_too_short_raises() -> None:
    with pytest.raises(nib.NibError, match="header"):
        nib.parse(b"MNIB-1541-RAW\x01")


def test_more_entries_than_data_raises() -> None:
    # Two table entries but only one track of data present.
    raw = make_nib([(2, 0x03), (4, 0x03)], n_data_tracks=1)
    with pytest.raises(nib.NibError, match="more than"):
        nib.parse(raw)


def test_empty_table_raises() -> None:
    raw = make_nib([(0, 0x00)], n_data_tracks=1)
    with pytest.raises(nib.NibError, match="empty"):
        nib.parse(raw)


# --- the real source image -----------------------------------------------------


def test_real_nib_layout() -> None:
    needs.need(needs.NIB)
    img = nib.read_nib(REAL_NIB)
    assert img.version == 1
    assert len(img) == 40
    # Standard 1541 density zones for tracks 1..35.
    by_track = {int(t.track_number): t for t in img.tracks}
    assert by_track[1].density == 3
    assert by_track[18].density == 2
    assert by_track[25].density == 1
    assert by_track[31].density == 0
    # The protected tail: tracks 37..40 are flagged NO_SYNC.
    assert "NO_SYNC" in by_track[37].flag_names
    assert all(len(t.data) == nib.TRACK_DATA_SIZE for t in img.tracks)
    assert img.tracks[0].offset == nib.HEADER_SIZE


def test_read_nib_does_not_modify_source() -> None:
    needs.need(needs.NIB)
    before = hashlib.sha256(REAL_NIB.read_bytes()).hexdigest()
    mtime_before = REAL_NIB.stat().st_mtime_ns
    nib.read_nib(REAL_NIB)
    after = hashlib.sha256(REAL_NIB.read_bytes()).hexdigest()
    assert before == after
    assert REAL_NIB.stat().st_mtime_ns == mtime_before


# --- the inspect subcommand ----------------------------------------------------


def test_inspect_command_on_real_nib(capsys: pytest.CaptureFixture[str]) -> None:
    needs.need(needs.NIB)
    rc = cli.main(["inspect", str(REAL_NIB)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "MNIB-1541-RAW" in out
    assert "version 1" in out
    assert "Tracks:  40" in out
    assert "NO_SYNC" in out


def test_inspect_missing_file_returns_2(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["inspect", "no-such-file.nib"])
    assert rc == 2
    assert "not found" in capsys.readouterr().err


def test_inspect_invalid_image_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.nib"
    bad.write_bytes(b"this is not an MNIB image at all, padding......" * 8)
    rc = cli.main(["inspect", str(bad)])
    assert rc == 1
    assert "cannot read image" in capsys.readouterr().err
