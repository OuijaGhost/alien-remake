"""Tests for the recursive-descent tracer and the ALIEN code/data classifier.

Two layers, smallest-first:

* :mod:`alientools.m6502.trace` on tiny hand-assembled programs — it must follow
  branches/JSR/JMP, stop at returns, and *not* trace data that sits after a
  terminator (the whole point of control-flow vs. linear-sweep decoding).
* :mod:`alientools.codemap` — IRQ-vector discovery, byte classification, symbol
  parsing, and listing emission on synthetic bytes, plus a census sanity check
  against the real ``ALIEN.prg`` when it is present.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alientools import codemap
from alientools.m6502 import trace_code

PRG_PATH = (
    Path(__file__).resolve().parents[1]
    / "out"
    / "Alien (USA, Europe)_files"
    / "ALIEN.prg"
)


# --- the generic tracer -------------------------------------------------------


def test_trace_follows_jsr_and_stops_at_rts() -> None:
    # $1000: JSR $1006 ; JMP $1009        (call sub, then jump past data)
    # $1006: LDA #$01  ; RTS              (the subroutine)
    # $1009: NOP       ; RTS
    prog = bytes([
        0x20, 0x06, 0x10,   # 1000 JSR $1006
        0x4C, 0x09, 0x10,   # 1003 JMP $1009
        0xA9, 0x01,         # 1006 LDA #$01
        0x60,               # 1008 RTS
        0xEA,               # 1009 NOP
        0x60,               # 100A RTS
    ])
    cm = trace_code(prog, 0x1000, [0x1000])
    assert cm.code_starts == {0x1000, 0x1003, 0x1006, 0x1008, 0x1009, 0x100A}
    # every byte is reached as code here
    assert cm.code_bytes == set(range(0x1000, 0x100B))


def test_trace_does_not_decode_data_after_a_terminator() -> None:
    # $2000: LDA #$05 ; RTS ; .byte AD 20 03 (data that *looks* like LDA $0320)
    prog = bytes([0xA9, 0x05, 0x60, 0xAD, 0x20, 0x03])
    cm = trace_code(prog, 0x2000, [0x2000])
    assert cm.code_starts == {0x2000, 0x2002}
    # the three trailing bytes are NOT code (they follow the RTS)
    assert 0x2003 not in cm.code_bytes
    assert 0x2005 not in cm.code_bytes


def test_trace_takes_both_sides_of_a_branch() -> None:
    # $3000: BNE $3004 ; NOP(fallthrough) ; RTS ; RTS(branch target)
    prog = bytes([
        0xD0, 0x02,   # 3000 BNE $3004
        0xEA,         # 3002 NOP  (fall-through)
        0x60,         # 3003 RTS
        0x60,         # 3004 RTS  (branch target)
    ])
    cm = trace_code(prog, 0x3000, [0x3000])
    assert cm.code_starts == {0x3000, 0x3002, 0x3003, 0x3004}


def test_trace_stops_at_indirect_jmp() -> None:
    # $4000: JMP ($4003) ; .byte 00 50   (pointer, not code)
    prog = bytes([0x6C, 0x03, 0x40, 0x00, 0x50])
    cm = trace_code(prog, 0x4000, [0x4000])
    assert cm.code_starts == {0x4000}
    assert 0x4003 not in cm.code_bytes  # the pointer bytes are data


def test_trace_respects_barriers() -> None:
    # A JSR into a declared barrier is not entered.
    prog = bytes([0x20, 0x03, 0x50, 0x60, 0xA9, 0x01])  # 5000 JSR $5003; 5003 RTS...
    cm = trace_code(prog, 0x5000, [0x5000], barriers=range(0x5003, 0x5006))
    assert 0x5003 not in cm.code_starts


def test_trace_is_seed_order_independent() -> None:
    prog = bytes([0xA9, 0x01, 0x60, 0xA9, 0x02, 0x60])
    a = trace_code(prog, 0x6000, [0x6000, 0x6003])
    b = trace_code(prog, 0x6000, [0x6003, 0x6000])
    assert a.code_starts == b.code_starts


# --- ALIEN codemap layer (synthetic) ------------------------------------------


def test_discover_irq_seeds_recovers_vector_target() -> None:
    # LDA #$08 / STA $0314 ; LDA #$4D / STA $0315  -> IRQ handler at $4D08
    body = bytes([0xA9, 0x08, 0x8D, 0x14, 0x03, 0xA9, 0x4D, 0x8D, 0x15, 0x03])
    seeds = codemap.discover_irq_seeds(body, 0x2000)  # origin covers $4D08? no
    # $4D08 is outside this tiny body, so it is filtered out...
    assert seeds == set()
    # ...but with a body large enough to contain the target it is returned.
    big = bytearray(0x3000)
    big[0:10] = body
    seeds = codemap.discover_irq_seeds(bytes(big), 0x2000)
    assert seeds == {0x4D08}


def test_load_symbols_parses_vice_labels() -> None:
    text = "al C:4000 .entry\nal C:4D08 .irq\n# comment\nnot a label\n"
    assert codemap.load_symbols(text) == {0x4000: "entry", 0x4D08: "irq"}


def test_classify_counts_every_byte_once() -> None:
    # Body spans $2000-$400F so it reaches past the $2000-$3FFF graphics bank.
    # Put a code RTS at $4002, three $FF padding bytes, and a data byte at $4008.
    body = bytearray(0x2010)          # covers $2000..$400F
    body[0x2002] = 0x60               # $4002 RTS (code, seeded below)
    body[0x2005] = body[0x2006] = body[0x2007] = 0xFF  # $4005-$4007 padding
    body[0x2008] = 0x42               # $4008 a data byte
    prg = bytes([0x00, 0x20]) + bytes(body)
    load, b, cm = codemap.build_codemap(prg, extra_seeds=(0x4002,))
    census = codemap.classify(load, b, cm)
    # every byte lands in exactly one class
    assert census.code + census.gfx + census.pad + census.data == census.total
    assert census.total == len(b)
    assert census.gfx == 0x2000       # the whole $2000-$3FFF bank
    assert census.pad == 3            # the three $FF bytes
    assert census.code >= 1           # at least the $4002 RTS


def test_emit_listing_labels_and_separates_data() -> None:
    # code at $4000 (RTS) then a data byte $99 at $4001, with a label on $4000.
    prg = bytes([0x00, 0x40, 0x60, 0x99])
    load, body, cm = codemap.build_codemap(prg, extra_seeds=(0x4000,))
    listing = codemap.emit_listing(load, body, cm, {0x4000: "start"})
    assert "start:" in listing
    assert "4000  60" in listing and "RTS" in listing
    assert ".byte 99" in listing  # the data byte is not decoded as an instruction


# --- against the real program (skipped on a fresh clone) ----------------------

_needs_prg = pytest.mark.skipif(
    not PRG_PATH.exists(), reason="extracted ALIEN.prg not present"
)


@_needs_prg
def test_real_alien_census_is_stable() -> None:
    load, body, cm = codemap.build_codemap(PRG_PATH.read_bytes())
    census = codemap.classify(load, body, cm)
    assert load == 0x2000
    assert census.total == len(body)
    # every byte accounted for exactly once
    assert census.code + census.gfx + census.pad + census.data == census.total
    # graphics bank is exactly $2000-$3FFF
    assert census.gfx == 0x2000
    # coverage: recursive descent reaches the bulk of the real code (~15.8 KB).
    assert census.instructions > 6000
    assert census.code > 15000
    # two well-known seeds (SYS entry + discovered IRQ) suffice for full coverage
    assert census.seeds == 2


@_needs_prg
def test_real_alien_irq_handler_is_discovered() -> None:
    load, body, _ = codemap.build_codemap(PRG_PATH.read_bytes())
    # ALIEN installs its raster IRQ at $4D08 (docs/re/DISASSEMBLY.md §4).
    assert 0x4D08 in codemap.discover_irq_seeds(body, load)
