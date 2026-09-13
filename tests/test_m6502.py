"""Tests for the pure-Python 6502 disassembler engine.

Layered smallest-first: the opcode tables are well-formed and cover all 256 byte
values; the addressing-mode renderer produces canonical operand text; a known
hand-assembled byte sequence disassembles instruction-for-instruction; and the
edge cases (PRG header, illegal opcodes, truncated operands, branch targets)
behave per the module's lossless/honest invariants.
"""

from __future__ import annotations

import pytest

from alientools.m6502 import (
    Instruction,
    disassemble_memory,
    disassemble_prg,
    format_listing,
)
from alientools.m6502 import opcodes
from alientools.m6502.disasm import render_operand


# --- the opcode tables --------------------------------------------------------


def test_legal_table_has_151_opcodes() -> None:
    # The documented NMOS 6502 has exactly 151 legal opcodes.
    assert len(opcodes.LEGAL) == 151


def test_tables_are_disjoint_and_cover_all_256() -> None:
    legal = set(opcodes.LEGAL)
    illegal = set(opcodes.ILLEGAL)
    assert legal.isdisjoint(illegal)
    assert legal | illegal == set(range(256))


def test_operand_sizes_are_sane() -> None:
    # Every entry's addressing mode declares 0, 1, or 2 operand bytes.
    for mnemonic, mode in list(opcodes.LEGAL.values()) + list(
        opcodes.ILLEGAL.values()
    ):
        assert mode.size in (0, 1, 2)
        assert mnemonic


# --- operand rendering --------------------------------------------------------


def test_render_each_addressing_mode() -> None:
    addr = 0x1000
    assert render_operand(opcodes.IMP, None, addr) == ""
    assert render_operand(opcodes.ACC, None, addr) == "A"
    assert render_operand(opcodes.IMM, 0x42, addr) == "#$42"
    assert render_operand(opcodes.ZP, 0x42, addr) == "$42"
    assert render_operand(opcodes.ZPX, 0x42, addr) == "$42,X"
    assert render_operand(opcodes.ZPY, 0x42, addr) == "$42,Y"
    assert render_operand(opcodes.ABS, 0x1234, addr) == "$1234"
    assert render_operand(opcodes.ABX, 0x1234, addr) == "$1234,X"
    assert render_operand(opcodes.ABY, 0x1234, addr) == "$1234,Y"
    assert render_operand(opcodes.IND, 0x1234, addr) == "($1234)"
    assert render_operand(opcodes.IZX, 0x42, addr) == "($42,X)"
    assert render_operand(opcodes.IZY, 0x42, addr) == "($42),Y"


def test_relative_branch_targets() -> None:
    # BNE at $1000 with +$10 -> $1012 (addr + 2 + offset).
    assert render_operand(opcodes.REL, 0x10, 0x1000) == "$1012"
    # Backward branch: $80 == -128 -> $1000 + 2 - 128 = $0F82.
    assert render_operand(opcodes.REL, 0x80, 0x1000) == "$0F82"
    # Wrap across the 16-bit boundary stays in range.
    assert render_operand(opcodes.REL, 0x00, 0xFFFE) == "$0000"


# --- disassembly of a known sequence -----------------------------------------


def test_disassemble_known_sequence() -> None:
    # A short hand-assembled routine at $C000:
    #   C000  A9 01     LDA #$01
    #   C002  8D 20 D0  STA $D020
    #   C005  20 00 FF  JSR $FF00
    #   C008  4C 00 C0  JMP $C000
    #   C00B  60        RTS
    code = bytes([
        0xA9, 0x01,
        0x8D, 0x20, 0xD0,
        0x20, 0x00, 0xFF,
        0x4C, 0x00, 0xC0,
        0x60,
    ])
    out = disassemble_memory(code, 0xC000)
    assert [i.text for i in out] == [
        "LDA #$01",
        "STA $D020",
        "JSR $FF00",
        "JMP $C000",
        "RTS",
    ]
    assert [i.address for i in out] == [0xC000, 0xC002, 0xC005, 0xC008, 0xC00B]
    assert [i.length for i in out] == [2, 3, 3, 3, 1]
    # Flow targets recorded for JSR/JMP, absent elsewhere.
    assert out[2].target == 0xFF00
    assert out[3].target == 0xC000
    assert out[0].target is None


def test_every_byte_accounted_for() -> None:
    # The concatenated raw bytes of all items reproduce the input exactly.
    code = bytes(range(256))
    out = disassemble_memory(code, 0x0800, illegal=True)
    assert b"".join(i.raw for i in out) == code


def test_branch_instruction_has_target() -> None:
    #   2000  D0 FE   BNE $2000   (tight loop onto itself)
    out = disassemble_memory(bytes([0xD0, 0xFE]), 0x2000)
    assert out[0].text == "BNE $2000"
    assert out[0].target == 0x2000


# --- PRG handling -------------------------------------------------------------


def test_disassemble_prg_strips_load_header() -> None:
    # PRG: load address $0801 (BASIC start), then LDX #$00.
    prg = bytes([0x01, 0x08, 0xA2, 0x00])
    load, out = disassemble_prg(prg)
    assert load == 0x0801
    assert len(out) == 1
    assert out[0].address == 0x0801
    assert out[0].text == "LDX #$00"


def test_disassemble_prg_rejects_short_buffer() -> None:
    with pytest.raises(ValueError):
        disassemble_prg(b"\x01")


# --- illegal opcodes & lossless data fallback --------------------------------


def test_illegal_opcode_is_data_by_default_but_decodes_when_enabled() -> None:
    # $07 is SLO $nn (illegal). Default: emitted as a data byte.
    default = disassemble_memory(bytes([0x07, 0x10, 0x00]), 0x4000)
    assert default[0].is_data
    assert default[0].text == ".byte $07"
    # The leftover $10 00 then re-decodes as a BPL branch.
    assert default[1].mnemonic == "BPL"
    # With illegal=True it decodes as the documented illegal form.
    enabled = disassemble_memory(bytes([0x07, 0x10]), 0x4000, illegal=True)
    assert enabled[0].is_illegal
    assert enabled[0].text == "SLO $10"
    assert enabled[0].length == 2


def test_unstable_opcode_flagged() -> None:
    # $9C is SHY $nnnn,X — an unstable magic-constant store.
    out = disassemble_memory(bytes([0x9C, 0x00, 0x20]), 0x5000, illegal=True)
    assert out[0].is_unstable
    assert out[0].is_illegal
    assert out[0].text == "SHY $2000,X"


def test_truncated_operand_falls_back_to_data() -> None:
    # LDA abs ($AD) needs two operand bytes; only one is present.
    out = disassemble_memory(bytes([0xAD, 0x34]), 0x6000)
    assert out[0].is_data and out[0].text == ".byte $AD"
    assert out[1].is_data and out[1].text == ".byte $34"


def test_unknown_opcode_without_illegal_is_data() -> None:
    out = disassemble_memory(bytes([0xFF]), 0x7000)
    assert out[0].is_data
    assert out[0].text == ".byte $FF"
    assert out[0].length == 1


def test_origin_out_of_range_rejected() -> None:
    with pytest.raises(ValueError):
        disassemble_memory(b"\xEA", 0x10000)


# --- listing formatting -------------------------------------------------------


def test_format_listing_columns_and_flags() -> None:
    code = bytes([0xA9, 0x01, 0x07, 0x10])  # LDA #$01 ; then illegal SLO $10
    listing = format_listing(disassemble_memory(code, 0xC000, illegal=True))
    lines = listing.splitlines()
    assert lines[0] == "C000  A9 01     LDA #$01"
    assert lines[1].startswith("C002  07")
    assert "illegal opcode" in lines[1]


def test_format_listing_without_bytes() -> None:
    out = disassemble_memory(bytes([0xEA]), 0x1000)
    assert format_listing(out, show_bytes=False) == "1000  NOP"


def test_instruction_is_frozen() -> None:
    out = disassemble_memory(bytes([0xEA]), 0)
    with pytest.raises(Exception):
        out[0].address = 1  # type: ignore[misc]
    assert isinstance(out[0], Instruction)
