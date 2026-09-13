"""Minimal NMOS 6502 CPU emulator for driving the original SID player.

Real *execution* semantics (registers, flags, stack, memory) for the **legal**
instruction set only, built on the same opcode table the disassembler already
trusts — :data:`alientools.m6502.opcodes.LEGAL` is imported as the single source
of truth for which opcodes exist and how many operand bytes follow them.

Fail-loud territory (the project's "fail loud on real corruption" convention):
anything outside the verified set raises :class:`CpuError` instead of guessing —

- an opcode not in the legal table (illegal/undocumented, or a JAM byte),
- ``BRK`` (reaching one means we are executing data),
- decimal-mode ``ADC``/``SBC`` (the game's player never sets the D flag; if it
  ever does, we want to know, not silently compute the binary result),
- blowing the caller's instruction budget (a hang would otherwise spin forever).

Deliberately **not** modelled, because the driver invokes the game's IRQ
handler directly at the simulated jiffy cadence: cycle counting, interrupt
delivery/RTI timing, and the I/O chips themselves (the :class:`MemoryBus` hooks
let the driver stand in for the few registers the player reads).
"""

from __future__ import annotations

from collections.abc import Callable

from alientools.m6502.opcodes import LEGAL

_BRANCH_MNEMONICS = frozenset(
    {"BCC", "BCS", "BEQ", "BNE", "BMI", "BPL", "BVC", "BVS"}
)


class CpuError(RuntimeError):
    """Execution left the emulator's verified territory (see module docs)."""


class MemoryBus:
    """A flat 64 KiB memory with per-address read hooks and a write listener.

    ``read_hooks[addr]`` replaces reads of one address (used to stand in for
    hardware registers such as ``$D019``/``$D41C``); ``write_listener`` observes
    *every* write (address, value) after it lands in RAM — the driver uses
    it to capture the ``$D400–$D418`` SID register stream.
    """

    def __init__(self) -> None:
        self.ram = bytearray(0x10000)
        self.read_hooks: dict[int, Callable[[], int]] = {}
        self.write_listener: Callable[[int, int], None] | None = None

    def load(self, addr: int, data: bytes) -> None:
        """Copy ``data`` into RAM at ``addr`` (no hooks/listener fired)."""
        end = addr + len(data)
        if addr < 0 or end > 0x10000:
            raise CpuError(f"load of {len(data)} bytes at ${addr:04X} exceeds 64 KiB")
        self.ram[addr:end] = data

    def read(self, addr: int) -> int:
        addr &= 0xFFFF
        hook = self.read_hooks.get(addr)
        if hook is not None:
            return hook() & 0xFF
        return self.ram[addr]

    def write(self, addr: int, value: int) -> None:
        addr &= 0xFFFF
        value &= 0xFF
        self.ram[addr] = value
        if self.write_listener is not None:
            self.write_listener(addr, value)


class Cpu:
    """A 6502 core over a :class:`MemoryBus`. One instruction per :meth:`step`."""

    #: Return address used by :meth:`call`; execution stops when PC reaches it.
    SENTINEL = 0xFFFF

    def __init__(self, bus: MemoryBus) -> None:
        self.bus = bus
        self.a = 0
        self.x = 0
        self.y = 0
        self.sp = 0xFD
        self.pc = 0
        # Status flags (P register), kept unpacked for speed/clarity.
        self.c = False  # carry
        self.z = False  # zero
        self.i = True   # interrupt disable
        self.d = False  # decimal
        self.v = False  # overflow
        self.n = False  # negative

    # ------------------------------------------------------------------ util

    def _fetch(self) -> int:
        value = self.bus.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def _fetch_word(self) -> int:
        lo = self._fetch()
        hi = self._fetch()
        return lo | (hi << 8)

    def _push(self, value: int) -> None:
        self.bus.write(0x0100 | self.sp, value)
        self.sp = (self.sp - 1) & 0xFF

    def _pop(self) -> int:
        self.sp = (self.sp + 1) & 0xFF
        return self.bus.read(0x0100 | self.sp)

    def _set_zn(self, value: int) -> int:
        value &= 0xFF
        self.z = value == 0
        self.n = bool(value & 0x80)
        return value

    def _pack_status(self, *, brk: bool) -> int:
        return (
            (0x01 if self.c else 0)
            | (0x02 if self.z else 0)
            | (0x04 if self.i else 0)
            | (0x08 if self.d else 0)
            | (0x10 if brk else 0)
            | 0x20  # the unused bit always reads 1
            | (0x40 if self.v else 0)
            | (0x80 if self.n else 0)
        )

    def _unpack_status(self, p: int) -> None:
        self.c = bool(p & 0x01)
        self.z = bool(p & 0x02)
        self.i = bool(p & 0x04)
        self.d = bool(p & 0x08)
        self.v = bool(p & 0x40)
        self.n = bool(p & 0x80)

    # ------------------------------------------------------ operand resolution

    def _resolve(self, mode_name: str) -> int | None:
        """Return the operand's effective address (None for imp/acc)."""
        if mode_name in ("imp", "acc"):
            return None
        if mode_name == "imm":
            addr = self.pc
            self.pc = (self.pc + 1) & 0xFFFF
            return addr
        if mode_name == "zp":
            return self._fetch()
        if mode_name == "zpx":
            return (self._fetch() + self.x) & 0xFF
        if mode_name == "zpy":
            return (self._fetch() + self.y) & 0xFF
        if mode_name == "abs":
            return self._fetch_word()
        if mode_name == "abx":
            return (self._fetch_word() + self.x) & 0xFFFF
        if mode_name == "aby":
            return (self._fetch_word() + self.y) & 0xFFFF
        if mode_name == "ind":
            # JMP ($nnnn) — with the authentic NMOS page-wrap bug.
            ptr = self._fetch_word()
            lo = self.bus.read(ptr)
            hi = self.bus.read((ptr & 0xFF00) | ((ptr + 1) & 0xFF))
            return lo | (hi << 8)
        if mode_name == "izx":
            ptr = (self._fetch() + self.x) & 0xFF
            return self.bus.read(ptr) | (self.bus.read((ptr + 1) & 0xFF) << 8)
        if mode_name == "izy":
            ptr = self._fetch()
            base = self.bus.read(ptr) | (self.bus.read((ptr + 1) & 0xFF) << 8)
            return (base + self.y) & 0xFFFF
        if mode_name == "rel":
            offset = self._fetch()
            if offset >= 0x80:
                offset -= 0x100
            return (self.pc + offset) & 0xFFFF
        raise CpuError(f"unknown addressing mode {mode_name!r}")  # pragma: no cover

    # --------------------------------------------------------------- ALU bits

    def _adc(self, value: int) -> None:
        if self.d:
            raise CpuError(f"decimal-mode ADC at ${self.pc:04X} is not implemented")
        total = self.a + value + (1 if self.c else 0)
        self.c = total > 0xFF
        result = total & 0xFF
        self.v = bool(~(self.a ^ value) & (self.a ^ result) & 0x80)
        self.a = self._set_zn(result)

    def _sbc(self, value: int) -> None:
        if self.d:
            raise CpuError(f"decimal-mode SBC at ${self.pc:04X} is not implemented")
        self._adc(value ^ 0xFF)

    def _compare(self, reg: int, value: int) -> None:
        self.c = reg >= value
        self._set_zn((reg - value) & 0xFF)

    def _rmw(self, mode_name: str, addr: int | None, fn: Callable[[int], int]) -> None:
        """Read-modify-write helper for ASL/LSR/ROL/ROR/INC/DEC."""
        if mode_name == "acc":
            self.a = fn(self.a)
        else:
            assert addr is not None
            self.bus.write(addr, fn(self.bus.read(addr)))

    def _asl(self, value: int) -> int:
        self.c = bool(value & 0x80)
        return self._set_zn((value << 1) & 0xFF)

    def _lsr(self, value: int) -> int:
        self.c = bool(value & 0x01)
        return self._set_zn(value >> 1)

    def _rol(self, value: int) -> int:
        carry_in = 1 if self.c else 0
        self.c = bool(value & 0x80)
        return self._set_zn(((value << 1) | carry_in) & 0xFF)

    def _ror(self, value: int) -> int:
        carry_in = 0x80 if self.c else 0
        self.c = bool(value & 0x01)
        return self._set_zn((value >> 1) | carry_in)

    # ------------------------------------------------------------------- step

    def step(self) -> None:
        """Execute exactly one instruction at PC."""
        op_addr = self.pc
        opcode = self._fetch()
        entry = LEGAL.get(opcode)
        if entry is None:
            raise CpuError(
                f"opcode ${opcode:02X} at ${op_addr:04X} is outside the legal set"
            )
        mnemonic, mode = entry

        if mnemonic == "BRK":
            raise CpuError(f"BRK at ${op_addr:04X} — executing data?")

        if mnemonic in _BRANCH_MNEMONICS:
            target = self._resolve(mode.name)
            assert target is not None
            taken = {
                "BCC": not self.c, "BCS": self.c,
                "BNE": not self.z, "BEQ": self.z,
                "BPL": not self.n, "BMI": self.n,
                "BVC": not self.v, "BVS": self.v,
            }[mnemonic]
            if taken:
                self.pc = target
            return

        if mnemonic == "JMP":
            target = self._resolve(mode.name)
            assert target is not None
            self.pc = target
            return
        if mnemonic == "JSR":
            target = self._fetch_word()
            ret = (self.pc - 1) & 0xFFFF
            self._push(ret >> 8)
            self._push(ret & 0xFF)
            self.pc = target
            return
        if mnemonic == "RTS":
            lo = self._pop()
            hi = self._pop()
            self.pc = ((lo | (hi << 8)) + 1) & 0xFFFF
            return
        if mnemonic == "RTI":
            self._unpack_status(self._pop())
            lo = self._pop()
            hi = self._pop()
            self.pc = lo | (hi << 8)
            return

        addr = self._resolve(mode.name)

        if mnemonic == "LDA":
            assert addr is not None
            self.a = self._set_zn(self.bus.read(addr))
        elif mnemonic == "LDX":
            assert addr is not None
            self.x = self._set_zn(self.bus.read(addr))
        elif mnemonic == "LDY":
            assert addr is not None
            self.y = self._set_zn(self.bus.read(addr))
        elif mnemonic == "STA":
            assert addr is not None
            self.bus.write(addr, self.a)
        elif mnemonic == "STX":
            assert addr is not None
            self.bus.write(addr, self.x)
        elif mnemonic == "STY":
            assert addr is not None
            self.bus.write(addr, self.y)
        elif mnemonic == "AND":
            assert addr is not None
            self.a = self._set_zn(self.a & self.bus.read(addr))
        elif mnemonic == "ORA":
            assert addr is not None
            self.a = self._set_zn(self.a | self.bus.read(addr))
        elif mnemonic == "EOR":
            assert addr is not None
            self.a = self._set_zn(self.a ^ self.bus.read(addr))
        elif mnemonic == "ADC":
            assert addr is not None
            self._adc(self.bus.read(addr))
        elif mnemonic == "SBC":
            assert addr is not None
            self._sbc(self.bus.read(addr))
        elif mnemonic == "CMP":
            assert addr is not None
            self._compare(self.a, self.bus.read(addr))
        elif mnemonic == "CPX":
            assert addr is not None
            self._compare(self.x, self.bus.read(addr))
        elif mnemonic == "CPY":
            assert addr is not None
            self._compare(self.y, self.bus.read(addr))
        elif mnemonic == "BIT":
            assert addr is not None
            value = self.bus.read(addr)
            self.z = (self.a & value) == 0
            self.n = bool(value & 0x80)
            self.v = bool(value & 0x40)
        elif mnemonic == "INC":
            self._rmw(mode.name, addr, lambda v: self._set_zn(v + 1))
        elif mnemonic == "DEC":
            self._rmw(mode.name, addr, lambda v: self._set_zn(v - 1))
        elif mnemonic == "ASL":
            self._rmw(mode.name, addr, self._asl)
        elif mnemonic == "LSR":
            self._rmw(mode.name, addr, self._lsr)
        elif mnemonic == "ROL":
            self._rmw(mode.name, addr, self._rol)
        elif mnemonic == "ROR":
            self._rmw(mode.name, addr, self._ror)
        elif mnemonic == "INX":
            self.x = self._set_zn(self.x + 1)
        elif mnemonic == "INY":
            self.y = self._set_zn(self.y + 1)
        elif mnemonic == "DEX":
            self.x = self._set_zn(self.x - 1)
        elif mnemonic == "DEY":
            self.y = self._set_zn(self.y - 1)
        elif mnemonic == "TAX":
            self.x = self._set_zn(self.a)
        elif mnemonic == "TAY":
            self.y = self._set_zn(self.a)
        elif mnemonic == "TXA":
            self.a = self._set_zn(self.x)
        elif mnemonic == "TYA":
            self.a = self._set_zn(self.y)
        elif mnemonic == "TSX":
            self.x = self._set_zn(self.sp)
        elif mnemonic == "TXS":
            self.sp = self.x  # no flags
        elif mnemonic == "PHA":
            self._push(self.a)
        elif mnemonic == "PLA":
            self.a = self._set_zn(self._pop())
        elif mnemonic == "PHP":
            self._push(self._pack_status(brk=True))
        elif mnemonic == "PLP":
            self._unpack_status(self._pop())
        elif mnemonic == "CLC":
            self.c = False
        elif mnemonic == "SEC":
            self.c = True
        elif mnemonic == "CLI":
            self.i = False
        elif mnemonic == "SEI":
            self.i = True
        elif mnemonic == "CLD":
            self.d = False
        elif mnemonic == "SED":
            self.d = True  # ADC/SBC will fail loud if it is ever *used*
        elif mnemonic == "CLV":
            self.v = False
        elif mnemonic == "NOP":
            pass
        else:  # pragma: no cover - the legal table is fully handled above
            raise CpuError(f"unhandled mnemonic {mnemonic} at ${op_addr:04X}")

    # ------------------------------------------------------------------- run

    def run(
        self,
        *,
        stop: Callable[[int], bool],
        max_instructions: int = 1_000_000,
    ) -> int:
        """Step until ``stop(pc)`` is true; return the instruction count.

        Raises :class:`CpuError` if ``max_instructions`` is exceeded — the
        hard cap that keeps an unexpected code path from hanging the render.
        """
        executed = 0
        while not stop(self.pc):
            if executed >= max_instructions:
                raise CpuError(
                    f"instruction budget ({max_instructions}) exhausted at "
                    f"${self.pc:04X}"
                )
            self.step()
            executed += 1
        return executed

    def call(self, addr: int, *, max_instructions: int = 100_000) -> int:
        """JSR-like: run the subroutine at ``addr`` until its final RTS."""
        ret = (self.SENTINEL - 1) & 0xFFFF
        self._push(ret >> 8)
        self._push(ret & 0xFF)
        self.pc = addr
        return self.run(
            stop=lambda pc: pc == self.SENTINEL, max_instructions=max_instructions
        )
