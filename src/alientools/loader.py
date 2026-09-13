"""Locate the boot/first-loaded program and trace the visible load chain.

A 1541 game disk is normally started with ``LOAD"*",8,1``: the drive loads the
**first file in the directory** to the load address embedded in its first two
bytes, then ``RUN`` (or an auto-start ``SYS``) hands control to it. That first
file is the *boot/loader*; from there control passes to the other files. This
module identifies that boot file over the sectors :mod:`gcr` decoded (never the
raw disk) and produces a plain-text *load-chain* report.

The report is deliberately **descriptive, not interpretive**: it states the
directory order, each PRG's load/last address (read straight from its 2-byte CBM
header) and size, and which file ``LOAD"*"`` would run first. *How* the loader
then pulls in the rest — which file loads which, and the custom track reads a
copy-protected loader may use — is decided by reading the disassembly, which is
a later, human-reviewed pass. So this module reports only what is
visible from the filesystem, and flags partial/uncertain results rather than
guessing (fail soft on protection; lossless and honest).

The source ``.nib`` is never touched here.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import cbmdos, gcr

# A whole-disk decode: one entry per (half)track, as produced by gcr.decode_image.
DecodedImage = tuple[gcr.TrackDecode, ...]


@dataclass(frozen=True)
class LoadedFile:
    """One directory file with its extracted bytes and decoded load metadata."""

    entry: cbmdos.DirEntry
    data: bytes          # extracted file bytes (PRG: 2-byte header + body)
    complete: bool       # False if the sector chain was partial (flagged)

    @property
    def is_prg(self) -> bool:
        return self.entry.type_name == "PRG"

    @property
    def load_address(self) -> int | None:
        """The PRG load address (first two bytes, little-endian), else None."""
        if not self.is_prg or len(self.data) < 2:
            return None
        return self.data[0] | (self.data[1] << 8)

    @property
    def body_len(self) -> int:
        """Bytes of actual code/data (PRG: total minus the 2-byte header)."""
        if self.is_prg and len(self.data) >= 2:
            return len(self.data) - 2
        return len(self.data)

    @property
    def last_address(self) -> int | None:
        """The address of the final loaded byte, ``load + body_len - 1``."""
        load = self.load_address
        if load is None or self.body_len == 0:
            return None
        return (load + self.body_len - 1) & 0xFFFF


def load_directory(decoded: DecodedImage) -> list[LoadedFile]:
    """Extract every directory file in directory order.

    Returns one :class:`LoadedFile` per directory entry, each carrying its raw
    bytes and a ``complete`` flag. Raises :class:`cbmdos.CbmDosError` if the
    directory itself cannot be read.
    """
    smap = cbmdos.build_sector_map(decoded)
    out: list[LoadedFile] = []
    for entry in cbmdos.read_directory(smap):
        data, complete = cbmdos.extract_file(smap, entry)
        out.append(LoadedFile(entry=entry, data=data, complete=complete))
    return out


def boot_file(decoded: DecodedImage) -> LoadedFile:
    """Return the first-loaded file: the first directory entry (``LOAD"*"``).

    Raises :class:`cbmdos.CbmDosError` if the directory has no usable files.
    """
    files = load_directory(decoded)
    if not files:
        raise cbmdos.CbmDosError("directory is empty: no boot file to load")
    return files[0]


def format_load_chain(decoded: DecodedImage) -> str:
    """Render the visible load chain as plain text (descriptive, not interpretive).

    Lists the disk name and every directory file in order with type, load/last
    address and size, marks the file ``LOAD"*",8,1`` runs first, and notes that
    the inter-file load order is established from the disassembly.
    """
    smap = cbmdos.build_sector_map(decoded)
    bam = cbmdos.read_bam(smap)
    files = load_directory(decoded)

    lines: list[str] = []
    lines.append(f'Disk: "{bam.name_text}" {cbmdos.petscii_to_ascii(bam.disk_id)}')
    lines.append("")
    lines.append("Directory order (LOAD\"*\",8,1 runs the first file):")
    header = f"  {'#':>2}  {'name':<18} {'type':<4} {'load':>5} {'last':>5} {'bytes':>7}  flags"
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    for i, f in enumerate(files):
        load = f"${f.load_address:04X}" if f.load_address is not None else "  -  "
        last = f"${f.last_address:04X}" if f.last_address is not None else "  -  "
        flags: list[str] = []
        if i == 0:
            flags.append("BOOT (loaded first)")
        if not f.complete:
            flags.append("PARTIAL chain")
        lines.append(
            f"  {i:>2}  {f.entry.name_text:<18} {f.entry.type_name:<4} "
            f"{load:>5} {last:>5} {len(f.data):>7}  {', '.join(flags)}"
        )
    lines.append("")
    lines.append(
        "Note: the order in which the boot loader pulls in the remaining files "
        "(and any custom raw-track reads used by the copy protection) is "
        "interpreted from the disassembly, not asserted here."
    )
    return "\n".join(lines)
