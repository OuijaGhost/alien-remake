"""Whole-image code/data classification for the extracted ALIEN program.

Wraps the generic control-flow tracer (:mod:`alientools.m6502.trace`) with the
ALIEN-specific facts needed to classify *every* byte of ``ALIEN.prg`` and emit a
clean, fully separated disassembly listing:

* the program loads at ``$2000`` and is entered via ``SYS 16384`` (``$4000``);
* ``$2000-$3FFF`` is the graphics bank (charset + sprites) — never code;
* the raster IRQ handler is installed into ``$0314/$0315`` and so is reached by
  interrupt, not by a call — its address is *discovered* from the vector-install
  code so the trace does not depend on a hand-authored symbol file.

Every byte ends up in exactly one class — CODE (reached by the trace), GFX (the
graphics bank), PAD (``$FF`` fill = uninitialised work RAM), or DATA (everything
else: tables, text, screen templates). Optional symbols (the ``alien.sym`` label
file) are applied to the listing but are *not* required for the classification.

This makes ``docs/re/ALIEN.annotated.asm`` a **derived** artifact, reproducible
from the ``.nib`` (extract -> this command), per the derived-output invariant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .m6502 import CodeMap, Instruction, decode_at, trace_code

# --- ALIEN-specific layout constants (documented in docs/re/DISASSEMBLY.md) ---
ALIEN_LOAD = 0x2000          # ALIEN.prg load address
ALIEN_ENTRY = 0x4000         # SYS 16384 entry point
GFX_RANGE = range(0x2000, 0x4000)  # charset ($2000-$27FF) + sprites ($2800-$3FFF)
PAD_BYTE = 0xFF              # uninitialised work-RAM / padding fill


class CodemapError(Exception):
    """Raised when the input is not a usable ALIEN PRG."""


class ByteClass(Enum):
    """The class assigned to each byte of the image."""

    CODE = "code"
    GFX = "gfx"
    PAD = "pad"
    DATA = "data"


@dataclass(frozen=True)
class Census:
    """Byte-count summary of a classified image."""

    total: int
    code: int
    gfx: int
    pad: int
    data: int
    instructions: int
    seeds: int

    @property
    def payload(self) -> int:
        """Real code+data payload (excludes gfx bank and $FF padding)."""
        return self.code + self.data

    @property
    def code_pct(self) -> float:
        """CODE as a percentage of the real payload."""
        return 100.0 * self.code / self.payload if self.payload else 0.0


def discover_irq_seeds(data: bytes, origin: int) -> set[int]:
    """Recover IRQ-handler entry addresses from the vector-install code.

    Looks for the idiomatic ``LDA #lo / STA $0314`` and ``LDA #hi / STA $0315``
    writes to the KERNAL IRQ vector and pairs them into a target address. The
    handler runs via interrupt (not a call), so seeding it is what lets the trace
    reach the raster IRQ code without a hand-supplied entry list.
    """
    lo = hi = None
    # A9 xx 8D 14 03  (LDA #imm ; STA $0314)  and  A9 xx 8D 15 03 (STA $0315)
    for i in range(len(data) - 4):
        if data[i] == 0xA9 and data[i + 2] == 0x8D and data[i + 4] == 0x03:
            vec = data[i + 3]
            if vec == 0x14:
                lo = data[i + 1]
            elif vec == 0x15:
                hi = data[i + 1]
    seeds: set[int] = set()
    if lo is not None and hi is not None:
        addr = lo | (hi << 8)
        if origin <= addr < origin + len(data):
            seeds.add(addr)
    return seeds


def build_codemap(
    prg: bytes, *, extra_seeds: tuple[int, ...] = ()
) -> tuple[int, bytes, CodeMap]:
    """Trace ``ALIEN.prg`` and return ``(load, body, codemap)``.

    Seeds are the SYS entry, any discovered IRQ handler, plus ``extra_seeds``
    (e.g. code labels, if a caller wants to be extra sure of jump-table targets).
    The graphics bank is a barrier so a stray decode can never wander into it.
    """
    if len(prg) < 3:
        raise CodemapError("PRG too short: missing load header + body")
    load = prg[0] | (prg[1] << 8)
    body = prg[2:]
    seeds = {ALIEN_ENTRY, *extra_seeds}
    seeds |= discover_irq_seeds(body, load)
    codemap = trace_code(body, load, seeds, barriers=GFX_RANGE)
    return load, body, codemap


def classify(load: int, body: bytes, codemap: CodeMap) -> Census:
    """Count every byte of the image into a :class:`Census`."""
    code = gfx = pad = data = 0
    for i, byte in enumerate(body):
        addr = load + i
        if addr in GFX_RANGE:
            gfx += 1
        elif addr in codemap.code_bytes:
            code += 1
        elif byte == PAD_BYTE:
            pad += 1
        else:
            data += 1
    return Census(
        total=len(body),
        code=code,
        gfx=gfx,
        pad=pad,
        data=data,
        instructions=len(codemap.code_starts),
        seeds=len(codemap.seeds),
    )


def load_symbols(text: str) -> dict[int, str]:
    """Parse a VICE label file (``al C:XXXX .name`` lines) into ``{addr: name}``."""
    labels: dict[int, str] = {}
    for line in text.splitlines():
        m = re.match(r"al\s+C:([0-9A-Fa-f]{4})\s+\.(\S+)", line)
        if m:
            labels[int(m.group(1), 16)] = m.group(2)
    return labels


def _gloss(chunk: bytes) -> str:
    """Printable-ASCII gloss for a data row (non-printables shown as '.')."""
    return "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in chunk)


def _operand_text(instr: Instruction, labels: dict[int, str]) -> str:
    """Instruction operand, substituting a label for a resolved flow target."""
    if instr.target is not None and instr.target in labels:
        if instr.mnemonic in ("JMP", "JSR") or instr.mnemonic.startswith("B"):
            return labels[instr.target]
    return instr.operand_text


def emit_listing(
    load: int, body: bytes, codemap: CodeMap, labels: dict[int, str]
) -> str:
    """Render the fully classified listing (code as instructions, rest as data).

    Labels are emitted as ``name:`` lines and substituted into flow operands. The
    graphics bank is collapsed to a single note. Data runs are 16-byte ``.byte``
    rows with an ASCII gloss, never decoded as instructions.
    """
    lines: list[str] = []
    end = load + len(body)
    addr = load
    while addr < end:
        if addr in labels:
            lines.append(f"\n{labels[addr]}:")
        if addr in GFX_RANGE:
            lines.append(
                f"{addr:04X}  ; --- graphics bank "
                f"${GFX_RANGE.start:04X}-${GFX_RANGE.stop - 1:04X} "
                f"(charset + sprites, data) ---"
            )
            addr = GFX_RANGE.stop
            continue
        if addr in codemap.code_starts:
            instr = decode_at(body, addr - load, load)
            hexb = " ".join(f"{b:02X}" for b in instr.raw)
            operand = _operand_text(instr, labels)
            body_txt = f"{instr.mnemonic} {operand}".rstrip()
            lines.append(f"{addr:04X}  {hexb:<9} {body_txt}".rstrip())
            addr += instr.length
            continue
        # data run: gather until the next code start, label, or gfx bank
        start = addr
        run: list[int] = []
        while (
            addr < end
            and addr not in codemap.code_starts
            and addr not in GFX_RANGE
            and (addr == start or addr not in labels)
        ):
            run.append(body[addr - load])
            addr += 1
        for k in range(0, len(run), 16):
            chunk = bytes(run[k : k + 16])
            hexb = " ".join(f"{b:02X}" for b in chunk)
            lines.append(f"{start + k:04X}  .byte {hexb:<47} ; {_gloss(chunk)}")
    return "\n".join(lines)


def format_census(census: Census, load: int, end: int) -> str:
    """One-block human-readable census report (ASCII, for the CLI)."""
    rows = [
        f"program ${load:04X}-${end:04X}  {census.total} bytes",
        f"  graphics bank $2000-$3FFF          : {census.gfx:6d} bytes",
        f"  reached as CODE                    : {census.code:6d} bytes"
        f"  ({census.instructions} instructions, {census.seeds} seeds)",
        f"  $FF work-RAM / padding             : {census.pad:6d} bytes",
        f"  data (tables + text + templates)   : {census.data:6d} bytes",
        f"  CODE as % of real payload          : {census.code_pct:.1f}%",
    ]
    return "\n".join(rows)
