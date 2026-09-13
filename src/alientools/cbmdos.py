"""Reconstruct the CBM-DOS filesystem from decoded sectors (read-only).

A 1541 disk's directory lives on **track 18**: sector 0 is the *BAM* (block
availability map, plus the disk name / id / DOS type and a pointer to the first
directory sector), and the directory itself is a chain of sectors starting at
18/1, each holding eight 32-byte entries. A file is a chain of 256-byte sectors
whose first two bytes link to the next sector; on the final sector the link
track is ``0`` and the link sector is the index of the last used byte.

This module follows those chains over the sectors :mod:`gcr` decoded — never the
raw disk — and **reports** incompleteness rather than guessing: a chain that runs
into a missing or undecodable sector yields a *partial* file, flagged, not a
crash. The source ``.nib`` is never touched here (the read-only invariant).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import gcr

DIR_TRACK = 18
BAM_SECTOR = 0
DIR_START_SECTOR = 1

ENTRY_SIZE = 32
ENTRIES_PER_SECTOR = 8
PAD = 0xA0  # CBM filenames are padded with $A0 (shifted space)

# Low nibble of the entry type byte -> file type name.
FILE_TYPES: dict[int, str] = {0: "DEL", 1: "SEQ", 2: "PRG", 3: "USR", 4: "REL"}
TYPE_CLOSED = 0x80  # bit 7: file is properly closed (clear => "*" splat file)
TYPE_LOCKED = 0x40  # bit 6: file is locked (">")

# A sector map is keyed by (track, sector); the value carries the 256-byte data.
SectorMap = dict[tuple[int, int], gcr.SectorResult]


class CbmDosError(Exception):
    """The filesystem could not be read (e.g. the directory track is missing)."""


def build_sector_map(decoded: tuple[gcr.TrackDecode, ...]) -> SectorMap:
    """Index every decoded sector of the whole tracks by ``(track, sector)``.

    Includes checksum-bad sectors (their recovered bytes are still the best we
    have); callers can consult :attr:`gcr.SectorResult.ok` if they care.
    """
    smap: SectorMap = {}
    for d in decoded:
        if d.halftrack % 2 != 0:
            continue
        track = d.halftrack // 2
        for s in d.sectors:
            smap[(track, s.sector)] = s
    return smap


def _strip_pad(raw: bytes) -> bytes:
    """Strip trailing $A0 padding from a CBM name field."""
    end = len(raw)
    while end > 0 and raw[end - 1] == PAD:
        end -= 1
    return raw[:end]


def petscii_to_ascii(raw: bytes) -> str:
    """Best-effort PETSCII -> ASCII for display / filenames (lossy, printable).

    Letters (both PETSCII cases) fold to uppercase ASCII; printable punctuation
    and digits pass through; anything else becomes ``.``.
    """
    out: list[str] = []
    for b in raw:
        if 0x41 <= b <= 0x5A or 0xC1 <= b <= 0xDA:  # PETSCII A-Z (either case)
            out.append(chr((b & 0x7F) if b < 0x80 else (b - 0x80)))
        elif 0x20 <= b <= 0x40 or b in (0x5B, 0x5D):  # space, digits, punctuation
            out.append(chr(b))
        else:
            out.append(".")
    return "".join(out)


@dataclass(frozen=True)
class BamInfo:
    """Header fields parsed from the BAM sector (18/0)."""

    disk_name: bytes  # raw, padding stripped
    disk_id: bytes  # 2 bytes
    dos_type: bytes  # 2 bytes, e.g. b"2A"
    first_dir_track: int
    first_dir_sector: int

    @property
    def name_text(self) -> str:
        return petscii_to_ascii(self.disk_name)


@dataclass(frozen=True)
class DirEntry:
    """One directory entry (a file)."""

    name: bytes  # raw filename, padding stripped
    file_type: int  # low nibble of the type byte (0..4)
    closed: bool
    locked: bool
    start_track: int
    start_sector: int
    size_sectors: int

    @property
    def type_name(self) -> str:
        return FILE_TYPES.get(self.file_type, f"?{self.file_type:X}")

    @property
    def name_text(self) -> str:
        return petscii_to_ascii(self.name)

    def filename(self) -> str:
        """A filesystem-safe name for extraction, e.g. ``BOOT.prg``."""
        stem = "".join(
            c if (c.isalnum() or c in "._-") else "_"
            for c in self.name_text
        ).strip("_") or "FILE"
        return f"{stem}.{self.type_name.lower()}"


def read_bam(smap: SectorMap) -> BamInfo:
    """Parse the BAM header from sector 18/0."""
    sec = smap.get((DIR_TRACK, BAM_SECTOR))
    if sec is None:
        raise CbmDosError(f"BAM sector {DIR_TRACK}/{BAM_SECTOR} not available")
    data = sec.data
    return BamInfo(
        disk_name=_strip_pad(data[144:160]),
        disk_id=data[162:164],
        dos_type=data[165:167],
        first_dir_track=data[0],
        first_dir_sector=data[1],
    )


def read_directory(smap: SectorMap) -> list[DirEntry]:
    """Follow the directory chain from the BAM, returning every used entry."""
    bam_sec = smap.get((DIR_TRACK, BAM_SECTOR))
    if bam_sec is None:
        raise CbmDosError(f"directory track {DIR_TRACK} not available")
    track = bam_sec.data[0] or DIR_TRACK
    sector = bam_sec.data[1] or DIR_START_SECTOR

    entries: list[DirEntry] = []
    visited: set[tuple[int, int]] = set()
    while track != 0 and (track, sector) not in visited:
        visited.add((track, sector))
        sec = smap.get((track, sector))
        if sec is None:
            break  # chain runs into a missing sector; stop (reported by caller)
        data = sec.data
        for i in range(ENTRIES_PER_SECTOR):
            entry = data[i * ENTRY_SIZE : (i + 1) * ENTRY_SIZE]
            type_byte = entry[2]
            if type_byte == 0:
                continue  # empty / scratched slot
            entries.append(
                DirEntry(
                    name=_strip_pad(entry[5:21]),
                    file_type=type_byte & 0x0F,
                    closed=bool(type_byte & TYPE_CLOSED),
                    locked=bool(type_byte & TYPE_LOCKED),
                    start_track=entry[3],
                    start_sector=entry[4],
                    size_sectors=entry[28] | (entry[29] << 8),
                )
            )
        track, sector = data[0], data[1]
    return entries


def extract_file(smap: SectorMap, entry: DirEntry) -> tuple[bytes, bool]:
    """Follow ``entry``'s sector chain. Returns ``(data, complete)``.

    ``complete`` is False if the chain hit a missing sector or looped — the bytes
    recovered so far are still returned (lossless, partial, flagged).
    """
    out = bytearray()
    track, sector = entry.start_track, entry.start_sector
    visited: set[tuple[int, int]] = set()
    while track != 0:
        if (track, sector) in visited:
            return bytes(out), False  # chain loops; bail
        visited.add((track, sector))
        sec = smap.get((track, sector))
        if sec is None:
            return bytes(out), False  # missing sector; partial
        data = sec.data
        next_track, next_sector = data[0], data[1]
        if next_track == 0:
            # Last sector: next_sector is the index of the last used byte.
            out += data[2 : next_sector + 1] if next_sector >= 2 else b""
            return bytes(out), True
        out += data[2:SECTOR_SIZE]
        track, sector = next_track, next_sector
    return bytes(out), True


SECTOR_SIZE = gcr.SECTOR_SIZE


def format_dir(smap: SectorMap) -> str:
    """Render a CBM-style directory listing as text (read-only)."""
    bam = read_bam(smap)
    entries = read_directory(smap)
    lines: list[str] = []
    lines.append(
        f'0 "{bam.name_text:<16}" {petscii_to_ascii(bam.disk_id)} '
        f"{petscii_to_ascii(bam.dos_type)}"
    )
    for e in entries:
        flag = " " if e.closed else "*"
        lock = "<" if e.locked else " "
        lines.append(
            f'{e.size_sectors:<4d} "{e.name_text}"{flag}{e.type_name}{lock}'
            f"   [{e.start_track}/{e.start_sector}]"
        )
    lines.append(f"{len(entries)} file(s).")
    return "\n".join(lines)
