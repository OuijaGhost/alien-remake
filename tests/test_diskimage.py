"""`.nib`, `.g64` and `.d64` all have to reach the same decoded sectors.

Requiring `.nib` shut out most users for no decoding reason: it is the format
that preserves this disk's protection, but the *files* extract identically from
a plain sector image, and that is all the game needs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alientools import cbmdos, diskimage, nib

import needs                                       # noqa: E402


def _names(image: diskimage.DiskImage) -> set[str]:
    smap = cbmdos.build_sector_map(image.decoded)
    return {e.name_text.strip() for e in cbmdos.read_directory(smap)}


def _make_g64(tracks: list[tuple[int, int, bytes]]) -> bytes:
    """Build a G64 container from `(halftrack_index, speed, gcr_bytes)`."""
    count = max(i for i, _, _ in tracks) + 1
    header = bytearray(b"GCR-1541" + bytes([0, count]) + (7928).to_bytes(2, "little"))
    offsets = bytearray(count * 4)
    speeds = bytearray(count * 4)
    body = bytearray()
    base = len(header) + len(offsets) + len(speeds)
    for index, speed, data in tracks:
        offsets[index * 4: index * 4 + 4] = (base + len(body)).to_bytes(4, "little")
        speeds[index * 4: index * 4 + 4] = speed.to_bytes(4, "little")
        body += len(data).to_bytes(2, "little") + data
    return bytes(header + offsets + speeds + body)


# --- the container parsers -------------------------------------------------


def test_an_unimaged_halftrack_is_skipped_not_faked() -> None:
    """A zero offset means "not imaged", which is normal and not an error.

    Most G64s hold only whole tracks, so treating a zero offset as a real track
    would invent 42 empty ones.
    """
    raw = _make_g64([(0, 3, b"\xff" * 512), (2, 3, b"\xff" * 512)])
    decoded = diskimage._decode_g64(raw)
    assert len(decoded) == 2, "the unimaged halftrack was not skipped"


def test_g64_speed_zone_becomes_the_density() -> None:
    raw = _make_g64([(0, 3, b"\xff" * 256), (30, 1, b"\xff" * 256)])
    decoded = diskimage._decode_g64(raw)
    assert [d.density for d in decoded] == [3, 1]


def test_a_truncated_g64_is_an_error_not_a_silent_short_read() -> None:
    raw = _make_g64([(0, 3, b"\xff" * 256)])
    with pytest.raises(diskimage.ImageError):
        diskimage._decode_g64(raw[:20])
    with pytest.raises(diskimage.ImageError):
        diskimage._decode_g64(b"not a g64 at all" * 4)


def test_d64_geometry_is_the_four_speed_zones() -> None:
    """683 sectors across 35 tracks, or the tracks land in the wrong places."""
    raw = bytes(683 * 256)
    decoded = diskimage._decode_d64(raw)
    assert len(decoded) == 35
    assert [len(d.sectors) for d in decoded[:1]] == [21]
    assert [len(d.sectors) for d in decoded[17:18]] == [19]
    assert [len(d.sectors) for d in decoded[24:25]] == [18]
    assert [len(d.sectors) for d in decoded[34:35]] == [17]
    assert sum(len(d.sectors) for d in decoded) == 683


def test_a_short_d64_stops_where_the_data_stops() -> None:
    """A truncated image should yield the tracks it has, not raise or pad."""
    decoded = diskimage._decode_d64(bytes(21 * 256 * 2))
    assert len(decoded) == 2
    with pytest.raises(diskimage.ImageError):
        diskimage._decode_d64(b"")


def test_an_unsupported_extension_says_so(tmp_path: Path) -> None:
    bad = tmp_path / "disk.zip"
    bad.write_bytes(b"PK\x03\x04")
    with pytest.raises(diskimage.ImageError) as exc:
        diskimage.load(bad)
    assert ".nib" in str(exc.value) and ".d64" in str(exc.value)


def test_find_prefers_the_format_that_carries_the_protection(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.d64").write_bytes(b"")
    (tmp_path / "a.g64").write_bytes(b"")
    assert diskimage.find(tmp_path).name == "a.g64"
    (tmp_path / "c.nib").write_bytes(b"")
    assert diskimage.find(tmp_path).name == "c.nib"
    assert diskimage.find(tmp_path / "nowhere") is None


def test_only_a_d64_reports_that_it_cannot_carry_protection() -> None:
    assert not diskimage.DiskImage(Path("x.d64"), "d64", ()).carries_protection
    assert diskimage.DiskImage(Path("x.g64"), "g64", ()).carries_protection


# --- against the real disk -------------------------------------------------


def test_a_d64_extracts_the_same_files_as_the_nib() -> None:
    """The point of the whole exercise, measured rather than assumed.

    The `.d64` is the one this toolkit exported from the `.nib`, so if the two
    disagree the fault is in reading it back, not in the disk.
    """
    needs.need(needs.NIB)
    exported = needs.REPO / "out" / f"{needs.NIB.stem}.d64"
    if not exported.exists():
        pytest.skip("run `alientools extract` first to produce the .d64")

    from_nib = diskimage.load(needs.NIB)
    from_d64 = diskimage.load(exported)
    assert _names(from_nib) == _names(from_d64)

    smap_nib = cbmdos.build_sector_map(from_nib.decoded)
    smap_d64 = cbmdos.build_sector_map(from_d64.decoded)
    for entry in cbmdos.read_directory(smap_nib):
        name = entry.name_text.strip()
        other = next(
            e for e in cbmdos.read_directory(smap_d64)
            if e.name_text.strip() == name
        )
        assert cbmdos.extract_file(smap_nib, entry)[0] == \
            cbmdos.extract_file(smap_d64, other)[0], f"{name} differs"


def test_a_g64_built_from_the_real_tracks_decodes_the_same() -> None:
    """Wrap the disk's own GCR in a G64 container and read it back."""
    needs.need(needs.NIB)
    source = nib.read_nib(needs.NIB)
    whole = [t for t in source.tracks if t.halftrack % 2 == 0]
    raw = _make_g64([(t.halftrack - 2, t.density, t.data) for t in whole])

    decoded = diskimage._decode_g64(raw)
    rebuilt = diskimage.DiskImage(Path("rebuilt.g64"), "g64", decoded)
    assert _names(rebuilt) == _names(diskimage.load(needs.NIB))


def test_the_nib_is_still_opened_read_only() -> None:
    """The project's oldest invariant, extended to the new entry point."""
    needs.need(needs.NIB)
    before = needs.NIB.stat().st_mtime_ns, needs.NIB.read_bytes()
    diskimage.load(needs.NIB)
    assert (needs.NIB.stat().st_mtime_ns, needs.NIB.read_bytes()) == before
