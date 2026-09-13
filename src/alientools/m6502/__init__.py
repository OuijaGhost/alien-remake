"""Pure-Python 6502 disassembler (engine only; no disk dependency).

This subpackage is the single source of truth for turning raw 6502 machine code
into a readable, load-address-aware listing. It is deliberately standalone — it
takes ``bytes`` and an origin, not a ``.nib`` — so it is unit-testable against
known byte sequences without any disk extraction ("does not yet
depend on the disk extraction"; the ``disasm`` subcommand that wires it to the
extracted program is `loader.py`).

Public API:

* :data:`opcodes.LEGAL` / :data:`opcodes.ILLEGAL` — the opcode tables.
* :class:`disasm.Instruction` — one decoded instruction.
* :func:`disasm.disassemble_memory` — decode a raw memory region at an origin.
* :func:`disasm.disassemble_prg` — decode a CBM ``PRG`` (2-byte load header).
* :func:`disasm.format_listing` — render instructions as an annotated listing.
"""

from __future__ import annotations

from .disasm import (
    Instruction,
    decode_at,
    disassemble_memory,
    disassemble_prg,
    format_listing,
)
from .opcodes import ILLEGAL, LEGAL
from .trace import CodeMap, trace_code

__all__ = [
    "Instruction",
    "decode_at",
    "disassemble_memory",
    "disassemble_prg",
    "format_listing",
    "LEGAL",
    "ILLEGAL",
    "CodeMap",
    "trace_code",
]
