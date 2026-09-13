"""Assemble decoded sectors into a standard ``.d64`` image (derived output).

A ``.d64`` is the canonical Commodore disk image: the 683 logical sectors of a
35-track 1541 disk, stored back-to-back in (track, sector) order, 256 bytes each
(174 848 bytes total). This module takes the per-track decode from :mod:`gcr` and
lays its sectors into that flat image, **flagging** rather than hiding anything
non-standard: sectors the decoder could not recover are recorded as *missing*,
sectors whose checksum failed are recorded as *bad* (their recovered bytes are
still written so the image is usable), and tracks beyond the standard 35 — the
copy-protected over-format tail of this disk — are noted as *extra* and left out
of the standard image.

This is a derived artefact: it is reproducible from the
``.nib`` and written only under ``out/``. The source image is never touched here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import gcr

# Standard 1541 geometry: 35 tracks, sector count per density zone.
STANDARD_TRACKS = 35
SECTOR_SIZE = gcr.SECTOR_SIZE  # 256

# (first_track, last_track, sectors_per_track) for the four 1541 speed zones.
_ZONES: tuple[tuple[int, int, int], ...] = (
    (1, 17, 21),
    (18, 24, 19),
    (25, 30, 18),
    (31, 35, 17),
)


def sectors_per_track(track: int) -> int:
    """Standard sector count for a 1541 track (1..35)."""
    for first, last, count in _ZONES:
        if first <= track <= last:
            return count
    raise ValueError(f"track {track} is outside the standard 1..{STANDARD_TRACKS}")


def d64_offset(track: int, sector: int) -> int:
    """Byte offset of ``(track, sector)`` within a standard ``.d64`` image."""
    if not 1 <= track <= STANDARD_TRACKS:
        raise ValueError(f"track {track} out of range")
    if not 0 <= sector < sectors_per_track(track):
        raise ValueError(f"sector {sector} out of range for track {track}")
    offset = 0
    for t in range(1, track):
        offset += sectors_per_track(t) * SECTOR_SIZE
    return offset + sector * SECTOR_SIZE


def image_size() -> int:
    """Total size in bytes of a standard 35-track ``.d64`` image (174 848)."""
    return sum(sectors_per_track(t) for t in range(1, STANDARD_TRACKS + 1)) * SECTOR_SIZE


@dataclass(frozen=True)
class SectorRef:
    """A (track, sector) coordinate used to flag missing/bad sectors."""

    track: int
    sector: int

    def __str__(self) -> str:
        return f"{self.track}/{self.sector}"


@dataclass(frozen=True)
class D64Image:
    """A standard ``.d64`` image assembled from decoded sectors, plus its flaws."""

    data: bytes  # exactly image_size() bytes
    missing: tuple[SectorRef, ...]  # standard sectors the decoder did not recover
    bad: tuple[SectorRef, ...]  # sectors written despite a failed checksum
    extra_tracks: tuple[int, ...]  # tracks > 35 that carried sectors (the tail)

    @property
    def is_standard(self) -> bool:
        """True when every standard sector decoded cleanly (a perfect image)."""
        return not self.missing and not self.bad


def assemble(decoded: tuple[gcr.TrackDecode, ...]) -> D64Image:
    """Lay decoded sectors into a standard ``.d64`` image, flagging the rest.

    Only whole tracks 1..35 contribute to the image. Half-tracks and the
    over-format tail (tracks > 35) are excluded from the standard layout; any
    tail track that carried sectors is reported in ``extra_tracks``.
    """
    by_ts: dict[tuple[int, int], gcr.SectorResult] = {}
    extra: set[int] = set()
    for d in decoded:
        if d.halftrack % 2 != 0:
            continue  # half-tracks are not part of the standard image
        track = d.halftrack // 2
        if track < 1:
            continue
        if track > STANDARD_TRACKS:
            if d.sectors:
                extra.add(track)
            continue
        for s in d.sectors:
            if 0 <= s.sector < sectors_per_track(track):
                by_ts[(track, s.sector)] = s

    buf = bytearray(image_size())
    missing: list[SectorRef] = []
    bad: list[SectorRef] = []
    for track in range(1, STANDARD_TRACKS + 1):
        for sector in range(sectors_per_track(track)):
            res = by_ts.get((track, sector))
            if res is None:
                missing.append(SectorRef(track, sector))
                continue
            off = d64_offset(track, sector)
            buf[off : off + SECTOR_SIZE] = res.data
            if not res.ok:
                bad.append(SectorRef(track, sector))

    return D64Image(
        data=bytes(buf),
        missing=tuple(missing),
        bad=tuple(bad),
        extra_tracks=tuple(sorted(extra)),
    )


def export(image: D64Image, path: str | Path) -> Path:
    """Write the assembled image to ``path`` (creating parent dirs). Returns it."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(image.data)
    return p


def format_assembly(image: D64Image) -> str:
    """Render a short, testable summary of an assembled image."""
    lines: list[str] = []
    lines.append(
        f"D64:     {len(image.data)} bytes "
        f"({STANDARD_TRACKS} tracks, {len(image.data) // SECTOR_SIZE} sectors)"
    )
    if image.is_standard:
        lines.append("Status:  standard (all sectors recovered, checksums OK)")
    else:
        lines.append(
            f"Status:  {len(image.missing)} missing, "
            f"{len(image.bad)} bad-checksum sector(s)"
        )
    if image.bad:
        lines.append("Bad:     " + ", ".join(str(r) for r in image.bad))
    if image.missing:
        shown = ", ".join(str(r) for r in image.missing[:20])
        more = "" if len(image.missing) <= 20 else f", +{len(image.missing) - 20} more"
        lines.append("Missing: " + shown + more)
    if image.extra_tracks:
        lines.append(
            "Tail:    tracks "
            + ", ".join(str(t) for t in image.extra_tracks)
            + " (over-format / protection — excluded from the standard image)"
        )
    return "\n".join(lines)
