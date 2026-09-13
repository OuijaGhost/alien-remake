"""GCR codec and 1541 sector decoder (the single source of truth for decode).

A 1541 floppy stores data as *Group Coded Recording* (GCR): every 4-bit nibble
is written as a fixed 5-bit code, chosen so the bit stream never has too many
consecutive equal bits (the drive needs flux transitions to stay in sync). Four
data bytes therefore become five GCR bytes, and a clean run of ``1`` bits longer
than any legal GCR pattern can produce is a **sync mark** that frames a block.

On the disk each sector is two blocks, each preceded by a sync mark:

* a **header block** — 8 bytes ``[$08, checksum, sector, track, id2, id1, $0f,
  $0f]`` → 10 GCR bytes — whose checksum is ``sector ^ track ^ id2 ^ id1``;
* a **data block** — 260 bytes ``[$07, <256 data bytes>, checksum, $00, $00]`` →
  325 GCR bytes — whose checksum is the XOR of the 256 data bytes.

This module provides the raw codec (:func:`encode` / :func:`decode`), helpers to
build block images (used by tests and the round-trip invariant), and a track
scanner (:func:`scan_sectors` / :func:`decode_track` / :func:`decode_image`) that
locates sync marks, decodes the blocks, and **reports** per-sector checksum
status. Decoding is lossless and never silently repairs data: a bad checksum or
an undecodable block is recorded, not "fixed" — so copy-protection artefacts stay
visible.
"""

from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass

from . import nib

# --- the 4 <-> 5 bit GCR tables ----------------------------------------------

# GCR_ENCODE[nibble] = the 5-bit code written to disk for that nibble. This is
# the standard Commodore 1541 table; the codes were chosen to avoid long runs of
# equal bits. It is the single source of truth — the decode table is derived.
GCR_ENCODE: tuple[int, ...] = (
    0x0A,  # 0000 -> 01010
    0x0B,  # 0001 -> 01011
    0x12,  # 0010 -> 10010
    0x13,  # 0011 -> 10011
    0x0E,  # 0100 -> 01110
    0x0F,  # 0101 -> 01111
    0x16,  # 0110 -> 10110
    0x17,  # 0111 -> 10111
    0x09,  # 1000 -> 01001
    0x19,  # 1001 -> 11001
    0x1A,  # 1010 -> 11010
    0x1B,  # 1011 -> 11011
    0x0D,  # 1100 -> 01101
    0x1D,  # 1101 -> 11101
    0x1E,  # 1110 -> 11110
    0x15,  # 1111 -> 10101
)

# GCR_DECODE[5-bit code] = nibble, or -1 if the code is not a legal GCR pattern.
GCR_DECODE: tuple[int, ...] = tuple(
    next((nibble for nibble, code in enumerate(GCR_ENCODE) if code == c), -1)
    for c in range(32)
)

HEADER_ID = 0x08  # first byte of a decoded header block
DATA_ID = 0x07  # first byte of a decoded data block

# A real header gap byte is $0F; the data block's trailing bytes are $00. Sync is
# a run of at least this many consecutive 1 bits (no legal GCR data reaches it).
MIN_SYNC_BITS = 10

# Logical sectors per track keyed by 1541 density zone (speed zone). The whole
# disk's geometry in one place; expected sector counts come from here.
SECTORS_BY_DENSITY: dict[int, int] = {3: 21, 2: 19, 1: 18, 0: 17}

SECTOR_SIZE = 256


class GcrError(Exception):
    """A GCR group could not be decoded (bad length or an illegal 5-bit code).

    Raised by the raw codec; the track scanner catches it and records the
    affected block as undecodable rather than propagating — illegal GCR on a
    protected track is data to report, not a crash.
    """


# --- the raw codec ------------------------------------------------------------


def encode(data: bytes) -> bytes:
    """GCR-encode bytes (length a multiple of 4) into 5/4 as many GCR bytes."""
    if len(data) % 4 != 0:
        raise GcrError(f"encode needs a multiple of 4 bytes, got {len(data)}")
    bitbuf = 0
    nbits = 0
    out = bytearray()
    for byte in data:
        for nibble in (byte >> 4, byte & 0x0F):
            bitbuf = (bitbuf << 5) | GCR_ENCODE[nibble]
            nbits += 5
            while nbits >= 8:
                nbits -= 8
                out.append((bitbuf >> nbits) & 0xFF)
    return bytes(out)


def decode(gcr: bytes) -> bytes:
    """GCR-decode bytes (length a multiple of 5) back to 4/5 as many bytes.

    Raises :class:`GcrError` on an illegal 5-bit code so callers can tell real
    data from protection garbage; this function never guesses a nibble.
    """
    if len(gcr) % 5 != 0:
        raise GcrError(f"decode needs a multiple of 5 bytes, got {len(gcr)}")
    bitbuf = 0
    nbits = 0
    nibbles: list[int] = []
    for byte in gcr:
        bitbuf = (bitbuf << 8) | byte
        nbits += 8
        while nbits >= 5:
            nbits -= 5
            code = (bitbuf >> nbits) & 0x1F
            nibble = GCR_DECODE[code]
            if nibble < 0:
                raise GcrError(f"illegal GCR code {code:#04x}")
            nibbles.append(nibble)
    out = bytearray()
    for i in range(0, len(nibbles), 2):
        out.append((nibbles[i] << 4) | nibbles[i + 1])
    return bytes(out)


# --- block images (also exercised by the round-trip test) ---------------------


def header_checksum(sector: int, track: int, id2: int, id1: int) -> int:
    """The 1541 header checksum: XOR of the four identity bytes."""
    return sector ^ track ^ id2 ^ id1


def data_checksum(data: bytes) -> int:
    """The 1541 data-block checksum: XOR of the 256 payload bytes."""
    checksum = 0
    for b in data:
        checksum ^= b
    return checksum


def build_header_image(
    track: int, sector: int, *, id1: int = 0x30, id2: int = 0x30
) -> bytes:
    """GCR-encode a header block for ``(track, sector)`` -> 10 GCR bytes."""
    block = bytes(
        [
            HEADER_ID,
            header_checksum(sector, track, id2, id1),
            sector,
            track,
            id2,
            id1,
            0x0F,
            0x0F,
        ]
    )
    return encode(block)


def build_data_image(data: bytes) -> bytes:
    """GCR-encode a 256-byte data block -> 325 GCR bytes."""
    if len(data) != SECTOR_SIZE:
        raise GcrError(f"data block needs {SECTOR_SIZE} bytes, got {len(data)}")
    block = bytes([DATA_ID]) + data + bytes([data_checksum(data), 0x00, 0x00])
    return encode(block)


def build_sector_image(
    track: int,
    sector: int,
    data: bytes,
    *,
    id1: int = 0x30,
    id2: int = 0x30,
    sync: int = 5,
    gap: int = 8,
) -> bytes:
    """Build a synthetic on-disk image of one sector (sync+header+gap+sync+data).

    Used by tests and to demonstrate the lossless round-trip invariant: feeding
    the result to :func:`scan_sectors` recovers the sector byte-for-byte.
    """
    sync_mark = b"\xff" * sync
    gap_bytes = b"\x55" * gap
    return (
        sync_mark
        + build_header_image(track, sector, id1=id1, id2=id2)
        + gap_bytes
        + sync_mark
        + build_data_image(data)
        + gap_bytes
    )


# --- the track scanner --------------------------------------------------------


@dataclass(frozen=True)
class SectorResult:
    """One decoded sector and the status of its two checksums."""

    track: int
    sector: int
    header_ok: bool
    data_ok: bool
    data: bytes  # 256 bytes of payload (present even if data_ok is False)

    @property
    def ok(self) -> bool:
        """True only when both the header and the data checksum verify."""
        return self.header_ok and self.data_ok

    @property
    def status(self) -> str:
        if self.ok:
            return "ok"
        if not self.header_ok and not self.data_ok:
            return "bad"
        return "bad_data" if not self.data_ok else "bad_header"


def _bits(data: bytes) -> list[int]:
    """Expand bytes to a flat list of bits, most-significant bit first."""
    out: list[int] = []
    for byte in data:
        out.extend((byte >> i) & 1 for i in range(7, -1, -1))
    return out


def _find_syncs(bits: list[int]) -> list[int]:
    """Return the bit index just past each sync mark (the first data bit)."""
    syncs: list[int] = []
    ones = 0
    for i, bit in enumerate(bits):
        if bit:
            ones += 1
        else:
            if ones >= MIN_SYNC_BITS:
                syncs.append(i)  # this 0 is the first bit of the next block
            ones = 0
    return syncs


def _read_gcr(bits: list[int], start: int, count: int) -> bytes:
    """Read ``count`` bytes (MSB first) from the bit list at ``start``."""
    end = start + count * 8
    if end > len(bits):
        raise IndexError("block runs past the end of the track")
    out = bytearray()
    pos = start
    for _ in range(count):
        byte = 0
        for k in range(8):
            byte = (byte << 1) | bits[pos + k]
        out.append(byte)
        pos += 8
    return bytes(out)


def scan_sectors(data: bytes) -> tuple[SectorResult, ...]:
    """Decode every sector found in a raw GCR track, deduped by sector number.

    Walks the sync marks, pairs each header block with the data block that
    follows it, and verifies both checksums. Undecodable or unpaired blocks are
    skipped (a header gone bad simply yields no sector for that slot). When a
    track's loop redundancy yields the same sector twice, a checksum-good copy
    wins over a bad one. Returns results sorted by sector number.
    """
    bits = _bits(data)
    sectors: dict[int, SectorResult] = {}
    pending: tuple[int, int, bool] | None = None  # (track, sector, header_ok)

    for start in _find_syncs(bits):
        try:
            block_id = decode(_read_gcr(bits, start, 5))[0]
        except (GcrError, IndexError):
            continue

        if block_id == HEADER_ID:
            try:
                hdr = decode(_read_gcr(bits, start, 10))
            except (GcrError, IndexError):
                pending = None
                continue
            _id, checksum, sector, track, id2, id1 = hdr[:6]
            pending = (track, sector, checksum == header_checksum(sector, track, id2, id1))

        elif block_id == DATA_ID:
            if pending is None:
                continue  # data block with no header we can attribute it to
            try:
                blk = decode(_read_gcr(bits, start, 325))
            except (GcrError, IndexError):
                pending = None
                continue
            track, sector, header_ok = pending
            pending = None
            payload = blk[1 : 1 + SECTOR_SIZE]
            result = SectorResult(
                track=track,
                sector=sector,
                header_ok=header_ok,
                data_ok=blk[1 + SECTOR_SIZE] == data_checksum(payload),
                data=payload,
            )
            existing = sectors.get(sector)
            if existing is None or (result.ok and not existing.ok):
                sectors[sector] = result

    return tuple(sectors[s] for s in sorted(sectors))


@dataclass(frozen=True)
class TrackDecode:
    """The decode outcome for one physical track."""

    halftrack: int
    density: int
    expected: int  # sectors a standard track in this zone should carry
    sectors: tuple[SectorResult, ...]
    sync_count: int
    flag_names: tuple[str, ...]

    @property
    def track_number(self) -> float:
        return self.halftrack / 2

    @property
    def found(self) -> int:
        return len(self.sectors)

    @property
    def good(self) -> int:
        return sum(1 for s in self.sectors if s.ok)

    @property
    def bad(self) -> int:
        return self.found - self.good

    @property
    def missing(self) -> int:
        return max(self.expected - self.found, 0)


def decode_track(track: nib.NibTrack) -> TrackDecode:
    """Decode one :class:`alientools.nib.NibTrack` into a :class:`TrackDecode`."""
    bits = _bits(track.data)
    return TrackDecode(
        halftrack=track.halftrack,
        density=track.density,
        expected=SECTORS_BY_DENSITY.get(track.density, 0),
        sectors=scan_sectors(track.data),
        sync_count=len(_find_syncs(bits)),
        flag_names=track.flag_names,
    )


def decode_image(image: nib.NibImage) -> tuple[TrackDecode, ...]:
    """Decode every track of a parsed MNIB image."""
    return tuple(decode_track(t) for t in image.tracks)


def format_tracks(
    decoded: "tuple[TrackDecode, ...]", *, source: "Path | None" = None
) -> str:
    """The per-track report for tracks that arrived without an MNIB container.

    `.g64` and `.d64` have no MNIB header to describe, so this prints what is
    actually known: where each track's sectors landed and how they verified.
    """
    lines: list[str] = []
    if source is not None:
        lines.append(f"File:    {source}")
    lines.append(f"Tracks:  {len(decoded)}")
    lines.append("")
    lines.append("track  density  sectors  good  bad  missing")
    for d in decoded:
        good = sum(1 for s in d.sectors if s.ok)
        bad = sum(1 for s in d.sectors if not s.ok)
        missing = max(0, d.expected - len(d.sectors))
        lines.append(
            f"{d.track_number:5g}  {d.density:7d}  {len(d.sectors):7d}  "
            f"{good:4d}  {bad:3d}  {missing:7d}"
        )
    return "\n".join(lines)


def format_decode(image: nib.NibImage) -> str:
    """Render a per-track good/bad/missing sector report as text.

    Returned as a string so :mod:`alientools.cli` stays the only module that
    touches stdout (and so the report is unit-testable).
    """
    decoded = decode_image(image)
    lines: list[str] = []
    if image.source is not None:
        lines.append(f"File:    {image.source}")
    lines.append(
        f"Format:  {nib.SIGNATURE.decode('ascii')}  version {image.version}"
    )
    lines.append("")
    lines.append(
        f"{'Track':>6}  {'Dens':>4}  {'Sync':>4}  {'Good':>4}  "
        f"{'Bad':>4}  {'Miss':>4}  {'Exp':>4}  Status"
    )
    lines.append(
        f"{'-' * 6}  {'-' * 4}  {'-' * 4}  {'-' * 4}  "
        f"{'-' * 4}  {'-' * 4}  {'-' * 4}  {'-' * 24}"
    )

    tot_good = tot_bad = tot_missing = 0
    for d in decoded:
        track = (
            f"{int(d.track_number)}"
            if d.halftrack % 2 == 0
            else f"{d.track_number:g}"
        )
        notes: list[str] = list(d.flag_names)
        if d.bad:
            bad_list = ",".join(
                str(s.sector) for s in d.sectors if not s.ok
            )
            notes.append(f"bad:{bad_list}")
        if d.expected and d.found == d.expected and d.bad == 0:
            status = "OK"
        elif d.found == 0:
            status = "no sectors" + (f" ({','.join(notes)})" if notes else "")
        else:
            status = ", ".join(notes) if notes else "partial"
        lines.append(
            f"{track:>6}  {d.density:>4}  {d.sync_count:>4}  {d.good:>4}  "
            f"{d.bad:>4}  {d.missing:>4}  {d.expected:>4}  {status}"
        )
        tot_good += d.good
        tot_bad += d.bad
        tot_missing += d.missing

    lines.append("")
    lines.append(
        f"Totals:  {tot_good} good, {tot_bad} bad-checksum, "
        f"{tot_missing} missing sector(s) across {len(decoded)} tracks."
    )
    return "\n".join(lines)
