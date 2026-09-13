"""Open a 1541 disk image in any of the three formats people actually have.

The toolkit was written against ``.nib`` because that is what preserves this
disk's copy protection. But most surviving copies of a C64 game are ``.d64``,
and ``.g64`` is what a modern imaging tool writes, so requiring ``.nib`` shut
out most users for no decoding reason.

All three arrive at the same currency, :class:`gcr.TrackDecode` per track, so
everything downstream (``cbmdos``, ``loader``, the asset derivation) is format
blind::

    .nib  MNIB-1541-RAW, raw GCR + a halftrack table   -> gcr.decode_image
    .g64  GCR-1541, per-track byte streams + offsets   -> gcr.decode_track
    .d64  logical sectors, no GCR at all               -> synthesised directly

**What you lose with .d64.** It stores only what a 1541 could read normally, so
the protection is gone: the non-standard tracks, the density oddities, the
sectors with deliberately bad checksums. The game's own files are all there and
extract fine — the disk's *structure* is what a ``.d64`` cannot carry, and
`inspect` says so rather than inventing it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import gcr, nib

#: Extensions understood by :func:`load`, best first.
SUFFIXES: tuple[str, ...] = (".nib", ".g64", ".d64")

_G64_SIGNATURE = b"GCR-1541"
_D64_SECTOR = 256


class ImageError(Exception):
    """The container is malformed — as opposed to merely protected."""


@dataclass(frozen=True)
class DiskImage:
    """A disk image of any supported format, decoded to logical sectors."""

    path: Path
    kind: str                             # "nib" | "g64" | "d64"
    decoded: tuple[gcr.TrackDecode, ...]
    #: Present only for `.nib`: the parsed container, for `inspect`.
    container: nib.NibImage | None = None

    @property
    def carries_protection(self) -> bool:
        """False for `.d64`, which cannot represent a non-standard track."""
        return self.kind != "d64"


def load(path: str | Path) -> DiskImage:
    """Read and decode a disk image. **Opens the source read-only.**"""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".nib":
        image = nib.read_nib(p)
        return DiskImage(p, "nib", gcr.decode_image(image), image)
    if suffix == ".g64":
        return DiskImage(p, "g64", _decode_g64(p.read_bytes()))
    if suffix == ".d64":
        return DiskImage(p, "d64", _decode_d64(p.read_bytes()))
    raise ImageError(
        f"unsupported image type {p.suffix or '(none)'}; expected one of "
        + ", ".join(SUFFIXES)
    )


def _decode_g64(raw: bytes) -> tuple[gcr.TrackDecode, ...]:
    """Parse a G64 container and run the GCR decoder over each track.

    Layout: an 8-byte signature, version, track count, a 2-byte maximum track
    size, then two parallel 32-bit tables — byte offsets to each halftrack's
    data, and each halftrack's speed zone. A zero offset means the halftrack was
    not imaged, which is normal: most images hold only the whole tracks.

    Each track's data begins with its own little-endian 2-byte length, because a
    real track's length varies with its speed zone and with how the drive that
    wrote it was running.
    """
    if len(raw) < 12 or raw[:8] != _G64_SIGNATURE:
        raise ImageError("not a G64 image (bad signature)")
    count = raw[9]
    table = 12
    speeds = table + count * 4
    if len(raw) < speeds + count * 4:
        raise ImageError(f"G64 header claims {count} halftracks, file is too short")

    out: list[gcr.TrackDecode] = []
    for i in range(count):
        offset = int.from_bytes(raw[table + i * 4: table + i * 4 + 4], "little")
        if offset == 0:
            continue                      # halftrack not imaged
        if offset + 2 > len(raw):
            raise ImageError(f"halftrack {i} points past the end of the file")
        length = int.from_bytes(raw[offset: offset + 2], "little")
        data = raw[offset + 2: offset + 2 + length]
        density = int.from_bytes(
            raw[speeds + i * 4: speeds + i * 4 + 4], "little"
        ) & 3
        # G64 indexes halftracks from 0 for track 1, where MNIB counts
        # halftracks from 2. `decode_track` wants the MNIB convention.
        out.append(gcr.decode_track(nib.NibTrack(
            index=i, halftrack=i + 2, density=density, flags=0,
            offset=offset, data=data,
        )))
    return tuple(out)


def _decode_d64(raw: bytes) -> tuple[gcr.TrackDecode, ...]:
    """Read a sector image straight into decoded sectors.

    There is no GCR here and nothing to verify: a `.d64` holds what the drive
    already recovered, so every sector is reported `ok`. That is honest rather
    than optimistic — the checksums were checked when the image was made, and
    this format has no room to record what they said.
    """
    tracks = len(raw) // _D64_SECTOR
    if tracks == 0:
        raise ImageError("empty file")
    out: list[gcr.TrackDecode] = []
    at = 0
    for track in range(1, 36):
        count = _sectors_on(track)
        sectors: list[gcr.SectorResult] = []
        for sector in range(count):
            end = at + _D64_SECTOR
            if end > len(raw):
                break
            sectors.append(gcr.SectorResult(
                track=track, sector=sector, header_ok=True, data_ok=True,
                data=raw[at:end],
            ))
            at = end
        if not sectors:
            break
        out.append(gcr.TrackDecode(
            halftrack=track * 2, density=_density_of(track),
            expected=count, sectors=tuple(sectors),
            sync_count=0, flag_names=(),
        ))
    if not out:
        raise ImageError(f"file is {len(raw)} bytes; too short for any track")
    return tuple(out)


def _sectors_on(track: int) -> int:
    """Sectors in a standard 1541 track — the four speed zones."""
    if track <= 17:
        return 21
    if track <= 24:
        return 19
    if track <= 30:
        return 18
    return 17


def _density_of(track: int) -> int:
    """The speed zone a standard track belongs to (3 is fastest, track 1)."""
    if track <= 17:
        return 3
    if track <= 24:
        return 2
    if track <= 30:
        return 1
    return 0


def find(directory: str | Path = ".") -> Path | None:
    """The first disk image in ``directory``, preferring the richest format."""
    where = Path(directory)
    for suffix in SUFFIXES:
        matches = sorted(where.glob(f"*{suffix}"))
        if matches:
            return matches[0]
    return None
