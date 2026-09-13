"""Tests for the minimal 6502 CPU emulator (`alien_remake.audio.mos6502`).

Correctness-critical (this is core logic driving the SID player),
so it is hand-tested against known byte sequences and hardware semantics.
Layered: registers/flags/arithmetic first, then
control flow (branches, JSR/RTS), then indexed addressing, then the
fail-loud error paths.
"""

from __future__ import annotations

import pytest

from alien_remake.audio.mos6502 import Cpu, CpuError, MemoryBus


def make_cpu(code: bytes, origin: int = 0x0800) -> tuple[Cpu, MemoryBus]:
    bus = MemoryBus()
    bus.load(origin, code)
    cpu = Cpu(bus)
    cpu.pc = origin
    return cpu, bus


def run_n(cpu: Cpu, n: int) -> None:
    for _ in range(n):
        cpu.step()


# --- registers / immediate loads / stores -------------------------------------


def test_lda_immediate_sets_a_and_flags() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0x00, 0xA9, 0x80, 0xA9, 0x01]))
    cpu.step()
    assert cpu.a == 0x00 and cpu.z is True and cpu.n is False
    cpu.step()
    assert cpu.a == 0x80 and cpu.z is False and cpu.n is True
    cpu.step()
    assert cpu.a == 0x01 and cpu.z is False and cpu.n is False


def test_sta_lda_zp_round_trip() -> None:
    cpu, bus = make_cpu(bytes([0xA9, 0x42, 0x85, 0x10, 0xA9, 0x00, 0xA5, 0x10]))
    run_n(cpu, 4)
    assert bus.read(0x10) == 0x42
    assert cpu.a == 0x42


def test_ldx_ldy_and_transfers() -> None:
    cpu, _ = make_cpu(bytes([0xA2, 0x05, 0xA0, 0x07, 0x8A, 0xA8]))
    run_n(cpu, 2)
    assert cpu.x == 5 and cpu.y == 7
    cpu.step()  # TXA
    assert cpu.a == 5
    cpu.step()  # TAY
    assert cpu.y == 5


# --- arithmetic: ADC/SBC with carry and overflow ------------------------------


def test_adc_basic_carry_out() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0xFF, 0x18, 0x69, 0x02]))  # LDA #$FF; CLC; ADC #$02
    run_n(cpu, 3)
    assert cpu.a == 0x01
    assert cpu.c is True
    assert cpu.z is False


def test_adc_signed_overflow() -> None:
    # $7F + $01 = $80 -> signed overflow (positive + positive = negative)
    cpu, _ = make_cpu(bytes([0xA9, 0x7F, 0x18, 0x69, 0x01]))
    run_n(cpu, 3)
    assert cpu.a == 0x80
    assert cpu.v is True
    assert cpu.n is True
    assert cpu.c is False


def test_adc_respects_incoming_carry() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0x01, 0x38, 0x69, 0x01]))  # LDA #1; SEC; ADC #1
    run_n(cpu, 3)
    assert cpu.a == 0x03  # 1 + 1 + carry-in(1)


def test_sbc_basic_with_borrow() -> None:
    # SEC (no borrow) then SBC: 0x05 - 0x01 = 0x04, carry stays set (no borrow)
    cpu, _ = make_cpu(bytes([0xA9, 0x05, 0x38, 0xE9, 0x01]))
    run_n(cpu, 3)
    assert cpu.a == 0x04
    assert cpu.c is True


def test_sbc_underflow_clears_carry() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0x00, 0x38, 0xE9, 0x01]))  # 0 - 1
    run_n(cpu, 3)
    assert cpu.a == 0xFF
    assert cpu.c is False  # carry clear means a borrow occurred


def test_decimal_mode_adc_raises() -> None:
    cpu, _ = make_cpu(bytes([0xF8, 0xA9, 0x09, 0x69, 0x01]))  # SED; LDA #9; ADC #1
    cpu.step()  # SED
    cpu.step()  # LDA
    with pytest.raises(CpuError, match="decimal"):
        cpu.step()  # ADC in decimal mode -> fail loud


# --- flags after CMP / logic ops ----------------------------------------------


def test_cmp_equal_sets_zero_and_carry() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0x10, 0xC9, 0x10]))
    run_n(cpu, 2)
    assert cpu.z is True
    assert cpu.c is True  # A >= operand
    assert cpu.n is False


def test_cmp_less_than_clears_carry_sets_negative() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0x01, 0xC9, 0x05]))
    run_n(cpu, 2)
    assert cpu.c is False
    assert cpu.n is True  # (1 - 5) & 0xFF = 0xFC -> bit7 set


def test_and_ora_eor_flags() -> None:
    cpu, _ = make_cpu(
        bytes([0xA9, 0xFF, 0x29, 0x0F, 0xA9, 0x00, 0x09, 0x00, 0xA9, 0x0F, 0x49, 0x0F])
    )
    run_n(cpu, 2)
    assert cpu.a == 0x0F and cpu.z is False
    run_n(cpu, 2)
    assert cpu.a == 0x00 and cpu.z is True
    run_n(cpu, 2)
    assert cpu.a == 0x00 and cpu.z is True  # XOR with itself-equivalent -> 0


def test_bit_sets_v_and_n_from_memory_z_from_and() -> None:
    cpu, bus = make_cpu(bytes([0xA9, 0x00, 0x24, 0x10]))  # LDA #0; BIT $10
    bus.write(0x10, 0xC0)  # bits 7 and 6 set
    run_n(cpu, 2)
    assert cpu.n is True
    assert cpu.v is True
    assert cpu.z is True  # A(0) & mem(0xC0) == 0


# --- shifts / rotates / inc-dec -----------------------------------------------


def test_asl_accumulator_sets_carry() -> None:
    cpu, _ = make_cpu(bytes([0xA9, 0x81, 0x0A]))  # LDA #$81; ASL A
    run_n(cpu, 2)
    assert cpu.a == 0x02
    assert cpu.c is True


def test_ror_rotates_carry_in() -> None:
    cpu, _ = make_cpu(bytes([0x38, 0xA9, 0x00, 0x6A]))  # SEC; LDA #0; ROR A
    run_n(cpu, 3)
    assert cpu.a == 0x80  # carry-in shifted into bit 7


def test_inc_dec_memory_and_registers() -> None:
    cpu, bus = make_cpu(bytes([0xE6, 0x20, 0xC6, 0x21, 0xE8, 0xCA, 0xC8, 0x88]))
    bus.write(0x20, 0x01)
    bus.write(0x21, 0x01)
    cpu.step()
    assert bus.read(0x20) == 0x02
    cpu.step()
    assert bus.read(0x21) == 0x00
    cpu.step()
    assert cpu.x == 1
    cpu.step()
    assert cpu.x == 0
    cpu.step()
    assert cpu.y == 1
    cpu.step()
    assert cpu.y == 0


# --- branches ------------------------------------------------------------------


def test_beq_taken_and_not_taken() -> None:
    # LDA #0 -> BEQ +2 (skips the next LDA #$FF) -> LDA #$11
    code = bytes([0xA9, 0x00, 0xF0, 0x02, 0xA9, 0xFF, 0xA9, 0x11])
    cpu, _ = make_cpu(code)
    run_n(cpu, 3)  # LDA, BEQ (taken), then the LDA at the branch target
    assert cpu.a == 0x11


def test_bne_not_taken_falls_through() -> None:
    code = bytes([0xA9, 0x00, 0xD0, 0x02, 0xA9, 0x22])
    cpu, _ = make_cpu(code)
    run_n(cpu, 3)
    assert cpu.a == 0x22  # BNE not taken (Z set) -> falls through to LDA #$22


def test_branch_backward_negative_offset() -> None:
    # At $0802: DEX; BNE back to $0802 (offset -2) until X==0, then LDA #$99
    code = bytes([0xA2, 0x03, 0xCA, 0xD0, 0xFD, 0xA9, 0x99])
    cpu, _ = make_cpu(code)
    cpu.run(stop=lambda pc: cpu.a == 0x99, max_instructions=100)
    assert cpu.x == 0
    assert cpu.a == 0x99


# --- JSR / RTS stack behaviour ---------------------------------------------


def test_jsr_rts_round_trip() -> None:
    # main: JSR sub; LDA #$AA; (halt via sentinel)
    # sub ($0810): LDA #$55; RTS
    main = bytes([0x20, 0x10, 0x08, 0xA9, 0xAA])
    cpu, bus = make_cpu(main, origin=0x0800)
    bus.load(0x0810, bytes([0xA9, 0x55, 0x60]))
    cpu.step()  # JSR $0810
    assert cpu.pc == 0x0810
    assert cpu.sp == 0xFB  # two bytes pushed
    cpu.step()  # LDA #$55 inside the subroutine
    assert cpu.a == 0x55
    cpu.step()  # RTS
    assert cpu.pc == 0x0803  # back after the 3-byte JSR
    assert cpu.sp == 0xFD
    cpu.step()  # LDA #$AA back in main
    assert cpu.a == 0xAA


def test_call_helper_runs_subroutine_to_completion() -> None:
    bus = MemoryBus()
    bus.load(0x0900, bytes([0xA9, 0x7B, 0x60]))  # LDA #$7B; RTS
    cpu = Cpu(bus)
    executed = cpu.call(0x0900)
    assert cpu.a == 0x7B
    assert executed == 2


def test_nested_jsr_stack_depth() -> None:
    # outer JSRs to inner, inner JSRs to innermost, all RTS back to a sentinel.
    bus = MemoryBus()
    bus.load(0x1000, bytes([0x20, 0x10, 0x10, 0x60]))  # JSR $1010; RTS
    bus.load(0x1010, bytes([0x20, 0x20, 0x10, 0x60]))  # JSR $1020; RTS
    bus.load(0x1020, bytes([0xA9, 0x01, 0x60]))  # LDA #1; RTS
    cpu = Cpu(bus)
    cpu.call(0x1000)
    assert cpu.a == 0x01


# --- indexed addressing modes --------------------------------------------------


def test_absolute_x_and_y_indexed() -> None:
    cpu, bus = make_cpu(bytes([0xBD, 0x00, 0x20, 0xB9, 0x00, 0x20]))  # LDA $2000,X ; LDA $2000,Y
    bus.write(0x2005, 0x11)
    bus.write(0x2007, 0x22)
    cpu.x = 5
    cpu.step()
    assert cpu.a == 0x11
    cpu.y = 7
    cpu.step()
    assert cpu.a == 0x22


def test_zero_page_x_wraps() -> None:
    cpu, bus = make_cpu(bytes([0xB5, 0xFF]))  # LDA $FF,X
    cpu.x = 0x02
    bus.write(0x01, 0x77)  # ($FF + 2) & 0xFF = 0x01
    cpu.step()
    assert cpu.a == 0x77


def test_indexed_indirect_izx() -> None:
    # LDA ($10,X) with X=4 -> pointer at $14/$15 -> target address
    cpu, bus = make_cpu(bytes([0xA1, 0x10]))
    cpu.x = 4
    bus.write(0x14, 0x00)
    bus.write(0x15, 0x30)
    bus.write(0x3000, 0x99)
    cpu.step()
    assert cpu.a == 0x99


def test_indirect_indexed_izy() -> None:
    # LDA ($10),Y: pointer at $10/$11 -> base, + Y
    cpu, bus = make_cpu(bytes([0xB1, 0x10]))
    cpu.y = 3
    bus.write(0x10, 0x00)
    bus.write(0x11, 0x40)
    bus.write(0x4003, 0x66)
    cpu.step()
    assert cpu.a == 0x66


# --- stack push/pull -----------------------------------------------------------


def test_pha_pla_round_trip() -> None:
    # LDA #$37; PHA; LDA #$00; PLA -> A should be restored to $37
    cpu, _ = make_cpu(bytes([0xA9, 0x37, 0x48, 0xA9, 0x00, 0x68]))
    run_n(cpu, 3)
    assert cpu.a == 0x00
    cpu.step()  # PLA
    assert cpu.a == 0x37


def test_php_plp_preserves_flags() -> None:
    cpu, _ = make_cpu(bytes([0x38, 0xF8, 0x08, 0x18, 0xD8, 0x28]))  # SEC; SED; PHP; CLC; CLD; PLP
    run_n(cpu, 5)
    assert cpu.c is False and cpu.d is False
    cpu.step()  # PLP restores the pushed C=1, D=1
    assert cpu.c is True
    assert cpu.d is True


# --- fail-loud error paths -------------------------------------------------


def test_illegal_opcode_raises_cpu_error() -> None:
    cpu, _ = make_cpu(bytes([0x02]))  # JAM
    with pytest.raises(CpuError, match="outside the legal set"):
        cpu.step()


def test_brk_raises_cpu_error() -> None:
    cpu, _ = make_cpu(bytes([0x00]))
    with pytest.raises(CpuError, match="BRK"):
        cpu.step()


def test_run_respects_instruction_budget() -> None:
    # An infinite loop: JMP back to itself.
    cpu, _ = make_cpu(bytes([0x4C, 0x00, 0x08]))
    with pytest.raises(CpuError, match="budget"):
        cpu.run(stop=lambda pc: False, max_instructions=50)


# --- memory bus write observation -----------------------------------------


def test_write_listener_observes_every_store() -> None:
    seen: list[tuple[int, int]] = []
    bus = MemoryBus()
    bus.write_listener = lambda addr, value: seen.append((addr, value))
    bus.load(0x0800, bytes([0xA9, 0x42, 0x8D, 0x00, 0xD4]))  # LDA #$42; STA $D400
    cpu = Cpu(bus)
    cpu.pc = 0x0800
    run_n(cpu, 2)
    assert seen == [(0xD400, 0x42)]


def test_read_hook_overrides_memory() -> None:
    bus = MemoryBus()
    bus.read_hooks[0xD019] = lambda: 0xAB
    bus.load(0x0800, bytes([0xAD, 0x19, 0xD0]))  # LDA $D019
    cpu = Cpu(bus)
    cpu.pc = 0x0800
    cpu.step()
    assert cpu.a == 0xAB
