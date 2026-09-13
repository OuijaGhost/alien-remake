"""Recursive-descent control-flow tracer: separate code from data *honestly*.

A linear sweep (``disasm.disassemble_memory``) decodes every byte in order and so
mis-reads data tables as instructions. This module instead **follows execution**
from a set of seed addresses — taking both sides of every branch, the target and
the fall-through of every ``JSR``, and the target of every unconditional ``JMP``
— and records exactly which bytes are reached as code. Everything not reached is
data (or unreachable padding).

This is the piece that lets the toolkit produce a *fully classified* disassembly
of a program whose code and data are interleaved (see the ``codemap`` command).

Invariants, matching the rest of the toolkit:

* **Honest, never guessed.** A trace stops the moment it would step onto a byte
  that is not a legal instruction (with ``illegal=False``), onto a declared data
  ``barrier``, or off the end of the buffer — it does not fabricate flow.
* **Deterministic.** Given the same bytes and seeds the reached set is identical;
  the worklist order does not affect the result.
* **Static only.** Computed/indirect transfers (``JMP ($nnnn)``, RTS-dispatch)
  cannot be followed statically, so their destinations must be supplied as seeds
  if they are to be reached — the tracer never invents them.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .disasm import decode_at

# Mnemonics that end a straight-line run with no fall-through.
_TERMINATORS = frozenset({"RTS", "RTI", "BRK", "JAM"})
# Conditional branches: both the target and the fall-through are reachable.
_BRANCHES = frozenset({"BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS"})


@dataclass(frozen=True)
class CodeMap:
    """The result of a control-flow trace.

    ``code_starts`` are the addresses that begin a reached instruction;
    ``code_bytes`` is every byte covered by those instructions (so an address is
    "code" iff it is in ``code_bytes``). Both are absolute 16-bit addresses.
    """

    origin: int
    length: int
    seeds: frozenset[int]
    code_starts: frozenset[int]
    code_bytes: frozenset[int]

    @property
    def end(self) -> int:
        """One past the last address covered by the traced region."""
        return self.origin + self.length

    def is_code(self, addr: int) -> bool:
        """True if ``addr`` is covered by a reached instruction."""
        return addr in self.code_bytes


def trace_code(
    data: bytes | bytearray,
    origin: int,
    seeds: Iterable[int],
    *,
    illegal: bool = False,
    barriers: Iterable[int] = (),
) -> CodeMap:
    """Trace reachable code in ``data`` (loaded at ``origin``) from ``seeds``.

    Each seed is an entry address (the SYS/RESET/IRQ vector, a jump-table target,
    …). The walk follows branches (both ways), ``JSR`` (target + fall-through) and
    unconditional ``JMP`` (target only); it stops at returns/BRK/JAM, at indirect
    jumps (whose destination is not statically known), at ``barriers`` (addresses
    declared to be data), and at any byte that does not decode as a legal
    instruction. Returns a :class:`CodeMap` of the reached instructions.
    """
    blob = bytes(data)
    end = origin + len(blob)
    barrier_set = frozenset(barriers)

    def in_range(addr: int) -> bool:
        return origin <= addr < end

    code_starts: set[int] = set()
    code_bytes: set[int] = set()
    seed_set = frozenset(s for s in seeds if in_range(s))
    work: list[int] = list(seed_set)

    while work:
        addr = work.pop()
        while True:
            if addr in code_starts:
                break  # already traced from here
            if not in_range(addr) or addr in barrier_set:
                break
            instr = decode_at(blob, addr - origin, origin, illegal=illegal)
            if instr.is_data:
                break  # ran onto a non-instruction byte -> not code
            code_starts.add(addr)
            for off in range(instr.length):
                code_bytes.add(addr + off)

            mnem = instr.mnemonic
            if mnem in _TERMINATORS:
                break
            if mnem == "JMP":
                # Absolute JMP: follow the target, no fall-through. Indirect JMP:
                # destination is a pointer we can't resolve statically -> stop.
                if instr.mode is not None and instr.mode.name == "abs":
                    if instr.target is not None and in_range(instr.target):
                        work.append(instr.target)
                break
            if mnem == "JSR":
                if instr.target is not None and in_range(instr.target):
                    work.append(instr.target)
            elif mnem in _BRANCHES:
                if instr.target is not None and in_range(instr.target):
                    work.append(instr.target)
            # fall through to the next instruction
            addr += instr.length

    return CodeMap(
        origin=origin,
        length=len(blob),
        seeds=seed_set,
        code_starts=frozenset(code_starts),
        code_bytes=frozenset(code_bytes),
    )
