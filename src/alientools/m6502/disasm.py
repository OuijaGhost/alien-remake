"""6502 disassembler: bytes + origin -> annotated, load-address-aware listing.

The engine is a straight *linear sweep* (decode each instruction, advance by its
length). It does not trace control flow — that interpretation lives elsewhere — but it
does record each instruction's branch/jump *target* so a later pass can follow
the load chain.

Two invariants matter here, mirroring the rest of the toolkit:

* **Lossless & honest.** Bytes that cannot form an instruction are emitted as
  ``.byte`` data, never guessed. With ``illegal=False`` (the default) any
  undocumented opcode becomes data; with ``illegal=True`` all 256 byte values
  decode. Either way every input byte appears exactly once in the output.
* **No silent truncation.** If an opcode's operand runs past the end of the
  buffer, the leftover bytes are emitted as ``.byte`` rather than reading out of
  bounds or fabricating an operand.
"""

from __future__ import annotations

from dataclasses import dataclass

from .opcodes import (
    ABS,
    ABX,
    ABY,
    ACC,
    ILLEGAL,
    IMM,
    IMP,
    IND,
    IZX,
    IZY,
    LEGAL,
    REL,
    UNSTABLE,
    ZP,
    ZPX,
    ZPY,
    AddrMode,
)

# Mnemonics whose absolute/indirect operand is a code address (a real jump
# target), as opposed to a data address. Used to populate Instruction.target.
_FLOW_ABS = frozenset({"JMP", "JSR"})


def _signed8(byte: int) -> int:
    """Interpret a byte as a signed two's-complement offset (-128..127)."""
    return byte - 256 if byte >= 0x80 else byte


def render_operand(mode: AddrMode, value: int | None, addr: int) -> str:
    """Render an instruction's operand to 6502 assembly text.

    ``value`` is the assembled operand (little-endian for two-byte modes) or
    ``None`` for the operand-less modes. ``addr`` is the instruction's own
    address, needed to resolve a relative branch to an absolute target.
    """
    name = mode.name
    if name == "imp":
        return ""
    if name == "acc":
        return "A"
    assert value is not None  # every non-implied mode has an operand
    if name == "imm":
        return f"#${value:02X}"
    if name == "zp":
        return f"${value:02X}"
    if name == "zpx":
        return f"${value:02X},X"
    if name == "zpy":
        return f"${value:02X},Y"
    if name == "rel":
        target = (addr + 2 + _signed8(value)) & 0xFFFF
        return f"${target:04X}"
    if name == "abs":
        return f"${value:04X}"
    if name == "abx":
        return f"${value:04X},X"
    if name == "aby":
        return f"${value:04X},Y"
    if name == "ind":
        return f"(${value:04X})"
    if name == "izx":
        return f"(${value:02X},X)"
    if name == "izy":
        return f"(${value:02X}),Y"
    raise ValueError(f"unknown addressing mode: {name!r}")  # pragma: no cover


@dataclass(frozen=True)
class Instruction:
    """One decoded item in the listing.

    For a real instruction ``mnemonic`` is the mnemonic and ``operand_text`` the
    rendered operand; for an undecodable/leftover byte ``is_data`` is ``True``,
    ``mnemonic`` is ``".byte"`` and ``operand_text`` is the byte literal.
    """

    address: int          # 16-bit address of the first byte
    raw: bytes            # the exact bytes this item consumes (1..3)
    mnemonic: str         # e.g. "LDA", "JMP", or ".byte" for data
    operand_text: str     # rendered operand ("" for implied / data has the value)
    mode: AddrMode | None  # addressing mode, or None for a data byte
    target: int | None    # branch/jump target address, else None
    is_data: bool = False  # True when this is a raw byte, not an instruction
    is_illegal: bool = False  # True for an undocumented opcode
    is_unstable: bool = False  # True for an unstable magic-constant opcode

    @property
    def length(self) -> int:
        """Number of bytes this item consumes."""
        return len(self.raw)

    @property
    def text(self) -> str:
        """The instruction/operand as assembly text, e.g. ``"LDA $1234,X"``."""
        if self.operand_text:
            return f"{self.mnemonic} {self.operand_text}"
        return self.mnemonic


def _decode_one(
    data: bytes, pos: int, origin: int, *, illegal: bool
) -> Instruction:
    """Decode the single item starting at ``data[pos]`` (address ``origin+pos``).

    Returns an :class:`Instruction`; falls back to a one-byte ``.byte`` datum
    when the opcode is unknown (in the chosen table) or its operand would run
    past the end of the buffer.
    """
    addr = (origin + pos) & 0xFFFF
    opcode = data[pos]

    entry = LEGAL.get(opcode)
    is_illegal = False
    if entry is None and illegal:
        entry = ILLEGAL.get(opcode)
        is_illegal = entry is not None

    if entry is None:
        # Unknown opcode for the active table: emit it as raw data.
        return Instruction(
            address=addr,
            raw=data[pos : pos + 1],
            mnemonic=".byte",
            operand_text=f"${opcode:02X}",
            mode=None,
            target=None,
            is_data=True,
        )

    mnemonic, mode = entry
    end = pos + 1 + mode.size
    if end > len(data):
        # Operand bytes are missing — do not read OOB or invent them; emit the
        # opcode byte as data and let the sweep re-decode the remainder.
        return Instruction(
            address=addr,
            raw=data[pos : pos + 1],
            mnemonic=".byte",
            operand_text=f"${opcode:02X}",
            mode=None,
            target=None,
            is_data=True,
        )

    operand_bytes = data[pos + 1 : end]
    if mode.size == 0:
        value: int | None = None
    elif mode.size == 1:
        value = operand_bytes[0]
    else:
        value = operand_bytes[0] | (operand_bytes[1] << 8)  # little-endian

    target: int | None = None
    if mode is REL:
        assert value is not None
        target = (addr + 2 + _signed8(value)) & 0xFFFF
    elif mnemonic in _FLOW_ABS and mode in (ABS, IND):
        target = value

    return Instruction(
        address=addr,
        raw=data[pos:end],
        mnemonic=mnemonic,
        operand_text=render_operand(mode, value, addr),
        mode=mode,
        target=target,
        is_illegal=is_illegal,
        is_unstable=opcode in UNSTABLE,
    )


def decode_at(
    data: bytes | bytearray, pos: int, origin: int, *, illegal: bool = False
) -> Instruction:
    """Decode the single instruction/datum beginning at ``data[pos]``.

    Public wrapper over the internal decoder so control-flow analysis
    (:mod:`alientools.m6502.trace`) can decode one instruction at an arbitrary
    position without re-implementing the opcode table. ``origin`` is the load
    address of ``data[0]``; the returned :class:`Instruction` carries its own
    absolute ``address`` and, for flow instructions, ``target``.
    """
    return _decode_one(bytes(data), pos, origin, illegal=illegal)


def disassemble_memory(
    data: bytes | bytearray, origin: int, *, illegal: bool = False
) -> list[Instruction]:
    """Linearly disassemble a raw memory region loaded at ``origin``.

    ``origin`` is the 16-bit address the first byte occupies. Set
    ``illegal=True`` to decode the undocumented opcode set (otherwise those
    bytes are emitted as data). Every input byte appears in exactly one returned
    item.
    """
    if not 0 <= origin <= 0xFFFF:
        raise ValueError(f"origin out of 16-bit range: {origin:#x}")
    blob = bytes(data)
    out: list[Instruction] = []
    pos = 0
    while pos < len(blob):
        instr = _decode_one(blob, pos, origin, illegal=illegal)
        out.append(instr)
        pos += instr.length
    return out


def disassemble_prg(
    data: bytes | bytearray, *, illegal: bool = False
) -> tuple[int, list[Instruction]]:
    """Disassemble a CBM ``PRG``: a 2-byte little-endian load address + code.

    Returns ``(load_address, instructions)``. Raises :class:`ValueError` if the
    buffer is too short to even hold the load-address header.
    """
    blob = bytes(data)
    if len(blob) < 2:
        raise ValueError("PRG too short: missing 2-byte load-address header")
    load = blob[0] | (blob[1] << 8)
    return load, disassemble_memory(blob[2:], load, illegal=illegal)


def format_listing(
    instructions: list[Instruction], *, show_bytes: bool = True
) -> str:
    """Render instructions as an annotated text listing.

    Each line is ``ADDR  BYTES  MNEMONIC OPERAND`` with illegal/unstable
    instructions flagged in a trailing comment. With ``show_bytes=False`` the hex
    byte column is omitted (a terser listing).
    """
    lines: list[str] = []
    for ins in instructions:
        addr = f"{ins.address:04X}"
        body = ins.text
        if ins.is_unstable:
            body += "  ; unstable illegal opcode"
        elif ins.is_illegal:
            body += "  ; illegal opcode"
        if show_bytes:
            hexb = " ".join(f"{b:02X}" for b in ins.raw)
            lines.append(f"{addr}  {hexb:<8}  {body}")
        else:
            lines.append(f"{addr}  {body}")
    return "\n".join(lines)
