"""6502 opcode and addressing-mode tables (the single source of truth).

Every entry maps an opcode byte to a ``(mnemonic, AddrMode)`` pair. The 151
legal NMOS 6502 instructions live in :data:`LEGAL`; the remaining 105 opcodes
(the stable "undocumented" instructions plus the JAM/KIL halts) live in
:data:`ILLEGAL`. Together they cover all 256 byte values, so a disassembly that
opts into the illegal set never produces a raw ``.byte`` placeholder.

An :class:`AddrMode` carries only the operand *size* (bytes that follow the
opcode); rendering an operand to text is the disassembler's job
(:func:`alientools.m6502.disasm.render_operand`) because the relative-branch and
jump modes need the instruction's own address to compute a target.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AddrMode:
    """A 6502 addressing mode.

    ``size`` is the number of operand bytes that follow the opcode (0, 1, or 2).
    ``name`` is the short tag used by the operand renderer.
    """

    name: str
    size: int


# The thirteen NMOS 6502 addressing modes. Singletons so identity comparison and
# table sharing both work; the renderer switches on ``mode.name``.
IMP = AddrMode("imp", 0)  # implied:            RTS
ACC = AddrMode("acc", 0)  # accumulator:        ASL A
IMM = AddrMode("imm", 1)  # immediate:          LDA #$nn
ZP = AddrMode("zp", 1)    # zero page:          LDA $nn
ZPX = AddrMode("zpx", 1)  # zero page,X:        LDA $nn,X
ZPY = AddrMode("zpy", 1)  # zero page,Y:        LDX $nn,Y
REL = AddrMode("rel", 1)  # relative (branch):  BNE $nnnn
ABS = AddrMode("abs", 2)  # absolute:           LDA $nnnn
ABX = AddrMode("abx", 2)  # absolute,X:         LDA $nnnn,X
ABY = AddrMode("aby", 2)  # absolute,Y:         LDA $nnnn,Y
IND = AddrMode("ind", 2)  # indirect:           JMP ($nnnn)
IZX = AddrMode("izx", 1)  # (indirect,X):       LDA ($nn,X)
IZY = AddrMode("izy", 1)  # (indirect),Y:       LDA ($nn),Y


# --- legal instruction set (151 opcodes) -------------------------------------

LEGAL: dict[int, tuple[str, AddrMode]] = {
    # ADC
    0x69: ("ADC", IMM), 0x65: ("ADC", ZP), 0x75: ("ADC", ZPX),
    0x6D: ("ADC", ABS), 0x7D: ("ADC", ABX), 0x79: ("ADC", ABY),
    0x61: ("ADC", IZX), 0x71: ("ADC", IZY),
    # AND
    0x29: ("AND", IMM), 0x25: ("AND", ZP), 0x35: ("AND", ZPX),
    0x2D: ("AND", ABS), 0x3D: ("AND", ABX), 0x39: ("AND", ABY),
    0x21: ("AND", IZX), 0x31: ("AND", IZY),
    # ASL
    0x0A: ("ASL", ACC), 0x06: ("ASL", ZP), 0x16: ("ASL", ZPX),
    0x0E: ("ASL", ABS), 0x1E: ("ASL", ABX),
    # branches
    0x90: ("BCC", REL), 0xB0: ("BCS", REL), 0xF0: ("BEQ", REL),
    0x30: ("BMI", REL), 0xD0: ("BNE", REL), 0x10: ("BPL", REL),
    0x50: ("BVC", REL), 0x70: ("BVS", REL),
    # BIT
    0x24: ("BIT", ZP), 0x2C: ("BIT", ABS),
    # BRK
    0x00: ("BRK", IMP),
    # flag clears/sets
    0x18: ("CLC", IMP), 0xD8: ("CLD", IMP), 0x58: ("CLI", IMP),
    0xB8: ("CLV", IMP), 0x38: ("SEC", IMP), 0xF8: ("SED", IMP),
    0x78: ("SEI", IMP),
    # CMP / CPX / CPY
    0xC9: ("CMP", IMM), 0xC5: ("CMP", ZP), 0xD5: ("CMP", ZPX),
    0xCD: ("CMP", ABS), 0xDD: ("CMP", ABX), 0xD9: ("CMP", ABY),
    0xC1: ("CMP", IZX), 0xD1: ("CMP", IZY),
    0xE0: ("CPX", IMM), 0xE4: ("CPX", ZP), 0xEC: ("CPX", ABS),
    0xC0: ("CPY", IMM), 0xC4: ("CPY", ZP), 0xCC: ("CPY", ABS),
    # DEC / DEX / DEY
    0xC6: ("DEC", ZP), 0xD6: ("DEC", ZPX), 0xCE: ("DEC", ABS),
    0xDE: ("DEC", ABX), 0xCA: ("DEX", IMP), 0x88: ("DEY", IMP),
    # EOR
    0x49: ("EOR", IMM), 0x45: ("EOR", ZP), 0x55: ("EOR", ZPX),
    0x4D: ("EOR", ABS), 0x5D: ("EOR", ABX), 0x59: ("EOR", ABY),
    0x41: ("EOR", IZX), 0x51: ("EOR", IZY),
    # INC / INX / INY
    0xE6: ("INC", ZP), 0xF6: ("INC", ZPX), 0xEE: ("INC", ABS),
    0xFE: ("INC", ABX), 0xE8: ("INX", IMP), 0xC8: ("INY", IMP),
    # JMP / JSR
    0x4C: ("JMP", ABS), 0x6C: ("JMP", IND), 0x20: ("JSR", ABS),
    # LDA / LDX / LDY
    0xA9: ("LDA", IMM), 0xA5: ("LDA", ZP), 0xB5: ("LDA", ZPX),
    0xAD: ("LDA", ABS), 0xBD: ("LDA", ABX), 0xB9: ("LDA", ABY),
    0xA1: ("LDA", IZX), 0xB1: ("LDA", IZY),
    0xA2: ("LDX", IMM), 0xA6: ("LDX", ZP), 0xB6: ("LDX", ZPY),
    0xAE: ("LDX", ABS), 0xBE: ("LDX", ABY),
    0xA0: ("LDY", IMM), 0xA4: ("LDY", ZP), 0xB4: ("LDY", ZPX),
    0xAC: ("LDY", ABS), 0xBC: ("LDY", ABX),
    # LSR
    0x4A: ("LSR", ACC), 0x46: ("LSR", ZP), 0x56: ("LSR", ZPX),
    0x4E: ("LSR", ABS), 0x5E: ("LSR", ABX),
    # NOP
    0xEA: ("NOP", IMP),
    # ORA
    0x09: ("ORA", IMM), 0x05: ("ORA", ZP), 0x15: ("ORA", ZPX),
    0x0D: ("ORA", ABS), 0x1D: ("ORA", ABX), 0x19: ("ORA", ABY),
    0x01: ("ORA", IZX), 0x11: ("ORA", IZY),
    # stack
    0x48: ("PHA", IMP), 0x08: ("PHP", IMP), 0x68: ("PLA", IMP),
    0x28: ("PLP", IMP),
    # ROL / ROR
    0x2A: ("ROL", ACC), 0x26: ("ROL", ZP), 0x36: ("ROL", ZPX),
    0x2E: ("ROL", ABS), 0x3E: ("ROL", ABX),
    0x6A: ("ROR", ACC), 0x66: ("ROR", ZP), 0x76: ("ROR", ZPX),
    0x6E: ("ROR", ABS), 0x7E: ("ROR", ABX),
    # returns
    0x40: ("RTI", IMP), 0x60: ("RTS", IMP),
    # SBC
    0xE9: ("SBC", IMM), 0xE5: ("SBC", ZP), 0xF5: ("SBC", ZPX),
    0xED: ("SBC", ABS), 0xFD: ("SBC", ABX), 0xF9: ("SBC", ABY),
    0xE1: ("SBC", IZX), 0xF1: ("SBC", IZY),
    # STA / STX / STY
    0x85: ("STA", ZP), 0x95: ("STA", ZPX), 0x8D: ("STA", ABS),
    0x9D: ("STA", ABX), 0x99: ("STA", ABY), 0x81: ("STA", IZX),
    0x91: ("STA", IZY),
    0x86: ("STX", ZP), 0x96: ("STX", ZPY), 0x8E: ("STX", ABS),
    0x84: ("STY", ZP), 0x94: ("STY", ZPX), 0x8C: ("STY", ABS),
    # transfers
    0xAA: ("TAX", IMP), 0xA8: ("TAY", IMP), 0xBA: ("TSX", IMP),
    0x8A: ("TXA", IMP), 0x9A: ("TXS", IMP), 0x98: ("TYA", IMP),
}


# --- stable undocumented ("illegal") opcodes (105 opcodes) -------------------
#
# These complete the 256-entry space. They follow the conventional names used by
# the 6502 illegal-opcode literature (SLO/RLA/SRE/RRA/SAX/LAX/DCP/ISC/...). The
# unstable magic-constant variants (XAA/AHX/SHY/SHX/TAS/LAS/LXA) are included for
# completeness so every byte decodes; they are tagged in :data:`UNSTABLE`.

ILLEGAL: dict[int, tuple[str, AddrMode]] = {
    # JAM / KIL — these lock the CPU; useful to flag in protected code.
    0x02: ("JAM", IMP), 0x12: ("JAM", IMP), 0x22: ("JAM", IMP),
    0x32: ("JAM", IMP), 0x42: ("JAM", IMP), 0x52: ("JAM", IMP),
    0x62: ("JAM", IMP), 0x72: ("JAM", IMP), 0x92: ("JAM", IMP),
    0xB2: ("JAM", IMP), 0xD2: ("JAM", IMP), 0xF2: ("JAM", IMP),
    # undocumented NOPs (various sizes / addressing modes)
    0x1A: ("NOP", IMP), 0x3A: ("NOP", IMP), 0x5A: ("NOP", IMP),
    0x7A: ("NOP", IMP), 0xDA: ("NOP", IMP), 0xFA: ("NOP", IMP),
    0x80: ("NOP", IMM), 0x82: ("NOP", IMM), 0x89: ("NOP", IMM),
    0xC2: ("NOP", IMM), 0xE2: ("NOP", IMM),
    0x04: ("NOP", ZP), 0x44: ("NOP", ZP), 0x64: ("NOP", ZP),
    0x14: ("NOP", ZPX), 0x34: ("NOP", ZPX), 0x54: ("NOP", ZPX),
    0x74: ("NOP", ZPX), 0xD4: ("NOP", ZPX), 0xF4: ("NOP", ZPX),
    0x0C: ("NOP", ABS),
    0x1C: ("NOP", ABX), 0x3C: ("NOP", ABX), 0x5C: ("NOP", ABX),
    0x7C: ("NOP", ABX), 0xDC: ("NOP", ABX), 0xFC: ("NOP", ABX),
    # SLO (ASL + ORA)
    0x07: ("SLO", ZP), 0x17: ("SLO", ZPX), 0x0F: ("SLO", ABS),
    0x1F: ("SLO", ABX), 0x1B: ("SLO", ABY), 0x03: ("SLO", IZX),
    0x13: ("SLO", IZY),
    # RLA (ROL + AND)
    0x27: ("RLA", ZP), 0x37: ("RLA", ZPX), 0x2F: ("RLA", ABS),
    0x3F: ("RLA", ABX), 0x3B: ("RLA", ABY), 0x23: ("RLA", IZX),
    0x33: ("RLA", IZY),
    # SRE (LSR + EOR)
    0x47: ("SRE", ZP), 0x57: ("SRE", ZPX), 0x4F: ("SRE", ABS),
    0x5F: ("SRE", ABX), 0x5B: ("SRE", ABY), 0x43: ("SRE", IZX),
    0x53: ("SRE", IZY),
    # RRA (ROR + ADC)
    0x67: ("RRA", ZP), 0x77: ("RRA", ZPX), 0x6F: ("RRA", ABS),
    0x7F: ("RRA", ABX), 0x7B: ("RRA", ABY), 0x63: ("RRA", IZX),
    0x73: ("RRA", IZY),
    # SAX (store A & X)
    0x87: ("SAX", ZP), 0x97: ("SAX", ZPY), 0x8F: ("SAX", ABS),
    0x83: ("SAX", IZX),
    # LAX (LDA + LDX)
    0xA7: ("LAX", ZP), 0xB7: ("LAX", ZPY), 0xAF: ("LAX", ABS),
    0xBF: ("LAX", ABY), 0xA3: ("LAX", IZX), 0xB3: ("LAX", IZY),
    # DCP (DEC + CMP)
    0xC7: ("DCP", ZP), 0xD7: ("DCP", ZPX), 0xCF: ("DCP", ABS),
    0xDF: ("DCP", ABX), 0xDB: ("DCP", ABY), 0xC3: ("DCP", IZX),
    0xD3: ("DCP", IZY),
    # ISC (INC + SBC)
    0xE7: ("ISC", ZP), 0xF7: ("ISC", ZPX), 0xEF: ("ISC", ABS),
    0xFF: ("ISC", ABX), 0xFB: ("ISC", ABY), 0xE3: ("ISC", IZX),
    0xF3: ("ISC", IZY),
    # immediate ALU oddments
    0x0B: ("ANC", IMM), 0x2B: ("ANC", IMM), 0x4B: ("ALR", IMM),
    0x6B: ("ARR", IMM), 0xCB: ("AXS", IMM), 0xEB: ("SBC", IMM),
    # unstable magic-constant variants
    0x8B: ("XAA", IMM), 0xAB: ("LAX", IMM), 0x9F: ("AHX", ABY),
    0x93: ("AHX", IZY), 0x9C: ("SHY", ABX), 0x9E: ("SHX", ABY),
    0x9B: ("TAS", ABY), 0xBB: ("LAS", ABY),
}

# Opcodes whose behaviour is unstable on real hardware (depend on analog effects
# / power state). Disassembly is fine; flag them so later analysis treats any
# match as suspicious rather than intentional.
UNSTABLE: frozenset[int] = frozenset(
    {0x8B, 0xAB, 0x9F, 0x93, 0x9C, 0x9E, 0x9B, 0xBB}
)
