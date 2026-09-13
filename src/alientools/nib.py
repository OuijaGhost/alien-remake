"""Parse the ``MNIB-1541-RAW`` nibble-dump container (read-only).

A ``.nib`` file is a raw GCR dump of a 1541 floppy as produced by *nibtools*.
Layout::

    offset 0x000  256-byte header
                    0x00  13-byte ASCII signature "MNIB-1541-RAW"
                    0x0D  1-byte version
                    0x0E  2 bytes (unused, zero in practice)
                    0x10  track table: 2 bytes per track
                            byte 0 = halftrack number (track N is at 2*N)
                            byte 1 = density (low 2 bits) | flag bits
                    ...   table ends at the first entry whose halftrack is 0
    offset 0x100  track data: 8192 (0x2000) raw GCR bytes per track entry

This module only *reads* the container: it opens the file read-only, validates
the signature, parses the track table, and slices the per-track GCR data. It
performs no GCR decoding (that is ``gcr.py``) and never writes to the
source image — the read-only invariant.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

SIGNATURE = b"MNIB-1541-RAW"
HEADER_SIZE = 256
TRACK_TABLE_OFFSET = 16
TRACK_ENTRY_SIZE = 2
TRACK_DATA_SIZE = 0x2000  # 8192 raw GCR bytes per track

# Density byte: low two bits are the 1541 density zone (0..3); the upper bits
# are nibtools status flags describing how the track was read.
DENSITY_MASK = 0x03

# nibtools status-flag bits (gcr.h). Kept as a single source of truth so the
# inspector and the later analysis agree on names.
BM_MATCH = 0x10  # track matched a known pattern during read
BM_NO_CYCLE = 0x20  # no track cycle (loop point) found
BM_NO_SYNC = 0x40  # no sync mark found on the track
BM_FF_TRACK = 0x80  # track is all $FF (killer / unformatted)

_FLAG_NAMES: tuple[tuple[int, str], ...] = (
    (BM_MATCH, "MATCH"),
    (BM_NO_CYCLE, "NO_CYCLE"),
    (BM_NO_SYNC, "NO_SYNC"),
    (BM_FF_TRACK, "FF_TRACK"),
)


class NibError(Exception):
    """The container is malformed (bad signature, truncated, inconsistent).

    Distinct from "this track looks like copy protection": that is reported,
    not raised. ``NibError`` means the *file* could not be parsed at all.
    """


def density_flag_names(density_byte: int) -> tuple[str, ...]:
    """Return the names of the status flags set in a raw density byte."""
    return tuple(name for bit, name in _FLAG_NAMES if density_byte & bit)


@dataclass(frozen=True)
class NibTrack:
    """One entry from the track table plus its raw GCR data.

    ``data`` is the verbatim 8192-byte GCR track; this module never decodes it.
    """

    index: int  # 0-based position in the track table
    halftrack: int  # raw halftrack byte; track N is stored at halftrack 2*N
    density: int  # 1541 density zone, 0..3
    flags: int  # status-flag bits from the density byte (upper bits)
    offset: int  # byte offset of this track's data within the file
    data: bytes  # raw GCR bytes (length == TRACK_DATA_SIZE)

    @property
    def track_number(self) -> float:
        """Physical track number. Whole tracks live on even halftracks."""
        return self.halftrack / 2

    @property
    def is_halftrack(self) -> bool:
        """True for the odd halftracks that sit between whole tracks."""
        return self.halftrack % 2 == 1

    @property
    def flag_names(self) -> tuple[str, ...]:
        """Human-readable names of the status flags set on this track."""
        return density_flag_names(self.flags)


@dataclass(frozen=True)
class NibImage:
    """A parsed ``MNIB-1541-RAW`` container."""

    version: int
    tracks: tuple[NibTrack, ...]
    source: Path | None = None  # where it was read from, if from a file

    def __iter__(self) -> Iterator[NibTrack]:
        return iter(self.tracks)

    def __len__(self) -> int:
        return len(self.tracks)


def parse(raw: bytes, *, source: Path | None = None) -> NibImage:
    """Parse the bytes of an ``MNIB-1541-RAW`` container.

    Raises :class:`NibError` if the signature is wrong, the header is too
    short, or the track table claims more tracks than the file contains data
    for. Trailing data beyond the last table entry is left unparsed.
    """
    if len(raw) < HEADER_SIZE:
        raise NibError(
            f"file is {len(raw)} bytes; need at least a {HEADER_SIZE}-byte header"
        )
    if raw[: len(SIGNATURE)] != SIGNATURE:
        got = raw[: len(SIGNATURE)]
        raise NibError(f"bad signature: expected {SIGNATURE!r}, got {got!r}")

    version = raw[len(SIGNATURE)]

    available = (len(raw) - HEADER_SIZE) // TRACK_DATA_SIZE
    if available == 0:
        raise NibError("no track data after the header")

    tracks: list[NibTrack] = []
    pos = TRACK_TABLE_OFFSET
    index = 0
    while pos + TRACK_ENTRY_SIZE <= HEADER_SIZE:
        halftrack = raw[pos]
        if halftrack == 0:
            break  # zero halftrack terminates the table
        density_byte = raw[pos + 1]

        if index >= available:
            raise NibError(
                f"track table lists more than {available} tracks but the file "
                f"only holds {available} track(s) of data"
            )

        data_offset = HEADER_SIZE + index * TRACK_DATA_SIZE
        data = raw[data_offset : data_offset + TRACK_DATA_SIZE]
        if len(data) != TRACK_DATA_SIZE:
            raise NibError(
                f"track {index} truncated: expected {TRACK_DATA_SIZE} bytes, "
                f"got {len(data)}"
            )

        tracks.append(
            NibTrack(
                index=index,
                halftrack=halftrack,
                density=density_byte & DENSITY_MASK,
                flags=density_byte & ~DENSITY_MASK,
                offset=data_offset,
                data=data,
            )
        )
        pos += TRACK_ENTRY_SIZE
        index += 1

    if not tracks:
        raise NibError("track table is empty")

    return NibImage(version=version, tracks=tuple(tracks), source=source)


def read_nib(path: str | Path) -> NibImage:
    """Read and parse a ``.nib`` file. Opens the source **read-only**."""
    p = Path(path)
    with p.open("rb") as fh:  # binary read; never opened for writing
        raw = fh.read()
    return parse(raw, source=p)


def format_inspect(image: NibImage) -> str:
    """Render a human-readable track/density layout report.

    Returned as a string so :mod:`alientools.cli` stays the only module that
    touches stdout (and so the report is unit-testable).
    """
    lines: list[str] = []
    if image.source is not None:
        lines.append(f"File:    {image.source}")
    lines.append(f"Format:  {SIGNATURE.decode('ascii')}  version {image.version}")
    lines.append(
        f"Tracks:  {len(image.tracks)}  "
        f"(header {HEADER_SIZE} bytes, {TRACK_DATA_SIZE} GCR bytes/track)"
    )
    lines.append("")
    lines.append(f"{'Track':>6}  {'Half':>4}  {'Dens':>4}  {'Offset':>8}  Flags")
    lines.append(f"{'-' * 6}  {'-' * 4}  {'-' * 4}  {'-' * 8}  {'-' * 16}")
    for t in image.tracks:
        track = (
            f"{int(t.track_number)}"
            if not t.is_halftrack
            else f"{t.track_number:g}"
        )
        flags = ",".join(t.flag_names) if t.flags else "-"
        lines.append(
            f"{track:>6}  {t.halftrack:>4}  {t.density:>4}  "
            f"0x{t.offset:06x}  {flags}"
        )
    return "\n".join(lines)
