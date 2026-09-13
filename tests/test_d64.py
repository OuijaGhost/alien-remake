"""Tests for assembling decoded sectors into a standard ``.d64`` image.

Geometry first (offsets / sizes), then synthetic assembly that exercises the
missing / bad / tail flagging, then the real source ``.nib`` which (per D-003)
has a perfectly standard 35-track area and a protected tail.
"""

from __future__ import annotations

from pathlib import Path

from alientools import d64, gcr, nib

import needs                                       # noqa: E402

REAL_NIB = Path(__file__).resolve().parent.parent / "Alien (USA, Europe).nib"


def _sector(track: int, sector: int, data: bytes, *, ok: bool = True) -> gcr.SectorResult:
    return gcr.SectorResult(
        track=track,
        sector=sector,
        header_ok=ok,
        data_ok=ok,
        data=data.ljust(gcr.SECTOR_SIZE, b"\x00")[: gcr.SECTOR_SIZE],
    )


def _track(halftrack: int, density: int, sectors: tuple[gcr.SectorResult, ...]) -> gcr.TrackDecode:
    return gcr.TrackDecode(
        halftrack=halftrack,
        density=density,
        expected=gcr.SECTORS_BY_DENSITY.get(density, 0),
        sectors=sectors,
        sync_count=len(sectors),
        flag_names=(),
    )


# --- geometry -----------------------------------------------------------------


def test_sectors_per_track_zones() -> None:
    assert d64.sectors_per_track(1) == 21
    assert d64.sectors_per_track(17) == 21
    assert d64.sectors_per_track(18) == 19
    assert d64.sectors_per_track(25) == 18
    assert d64.sectors_per_track(35) == 17


def test_d64_offsets_and_size() -> None:
    assert d64.d64_offset(1, 0) == 0
    assert d64.d64_offset(1, 1) == 256
    assert d64.d64_offset(2, 0) == 21 * 256
    assert d64.d64_offset(18, 0) == 17 * 21 * 256
    assert d64.image_size() == 174848  # the canonical 35-track .d64 size


# --- synthetic assembly -------------------------------------------------------


def test_assemble_flags_missing_bad_and_tail() -> None:
    # Track 1 (halftrack 2): sector 0 good, sector 1 bad-checksum, the rest missing.
    good = _sector(1, 0, b"\xaa" * 256)
    bad = _sector(1, 1, b"\xbb" * 256, ok=False)
    t1 = _track(2, 3, (good, bad))
    # A tail track beyond 35 (halftrack 80 -> track 40) with one sector.
    tail = _track(80, 2, (_sector(40, 0, b"\xcc" * 256),))

    img = d64.assemble((t1, tail))

    assert len(img.data) == d64.image_size()
    # Good sector landed at its offset; bad sector's recovered bytes still written.
    assert img.data[0:256] == b"\xaa" * 256
    assert img.data[256:512] == b"\xbb" * 256
    assert d64.SectorRef(1, 1) in img.bad
    # Everything else on track 1 (and all of tracks 2..35) is missing.
    assert d64.SectorRef(1, 2) in img.missing
    assert len(img.missing) == d64.image_size() // 256 - 2
    # The over-format tail is reported, not placed in the standard image.
    assert img.extra_tracks == (40,)
    assert not img.is_standard


def test_assemble_perfect_image_is_standard() -> None:
    # density is irrelevant to assembly (it keys on halftrack + standard geometry).
    tracks = [
        _track(
            track * 2,
            0,
            tuple(
                _sector(track, s, bytes([track]) * 256)
                for s in range(d64.sectors_per_track(track))
            ),
        )
        for track in range(1, 36)
    ]
    img = d64.assemble(tuple(tracks))
    assert img.is_standard
    assert img.missing == () and img.bad == () and img.extra_tracks == ()


# --- the real source image ----------------------------------------------------


def test_real_nib_assembles_to_standard_image() -> None:
    needs.need(needs.NIB)
    decoded = gcr.decode_image(nib.read_nib(REAL_NIB))
    img = d64.assemble(decoded)
    assert len(img.data) == 174848
    # D-003: the standard area decodes 100% clean, so the .d64 is perfect.
    assert img.is_standard
    # The protected tail (36..40) is reported as extra, never in the image.
    assert all(t > 35 for t in img.extra_tracks)


def test_export_writes_image(tmp_path: Path) -> None:
    needs.need(needs.NIB)
    decoded = gcr.decode_image(nib.read_nib(REAL_NIB))
    img = d64.assemble(decoded)
    out = d64.export(img, tmp_path / "alien.d64")
    assert out.read_bytes() == img.data
    assert len(out.read_bytes()) == 174848
