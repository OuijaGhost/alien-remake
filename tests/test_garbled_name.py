"""The opening notice's garbled victim name (D-081), without needing a ROM.

`$5092 LDA $A65E,Y` reads ten bytes per crew slot from under BASIC ROM without
banking it out, so the original prints ROM bytes where the name should be. That
is a real bug in the 1984 game and the remake reproduces it.

It used to reproduce it only on a machine that had a C64 BASIC ROM lying about,
which made a **decoded behaviour depend on the player's toolchain** - the same
game showing different things to different people for reasons nothing to do with
the game. The read is from a fixed address per slot, so the output is seventy
knowable bytes, and those are captured.
"""

from __future__ import annotations

import pytest

from alien_remake import assets  # noqa: E402
from alien_remake.core import opening_name  # noqa: E402


def test_every_crew_slot_has_its_bytes() -> None:
    """Seven slots, ten bytes each - the stride the ROM routine uses."""
    assert set(opening_name.GARBLED_NAME_BYTES) == set(range(1, 8))
    for slot, row in opening_name.GARBLED_NAME_BYTES.items():
        assert len(row) == opening_name.NAME_STRIDE, slot
        assert all(0 <= b <= 255 for b in row), slot


def test_the_capture_matches_a_real_rom_byte_for_byte() -> None:
    """The whole claim. Skips where no ROM is available, because then there is
    nothing to check against - not because the capture is in doubt."""
    found = assets.find_c64_rom("basic.bin")
    if found is None:
        pytest.skip("no BASIC ROM on this machine to check against")
    rom = found.read_bytes()
    for slot, row in opening_name.GARBLED_NAME_BYTES.items():
        off = (opening_name.NAME_TABLE + slot * opening_name.NAME_STRIDE
               - opening_name.BASIC_ROM_BASE)
        assert list(rom[off:off + opening_name.NAME_STRIDE]) == list(row), slot


def test_it_garbles_with_no_rom_at_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """The point of the change: the bug is reproduced everywhere now."""
    monkeypatch.setattr(assets, "find_c64_rom", lambda name: None)
    codes = opening_name.garbled_name_codes(3)
    assert codes == list(opening_name.GARBLED_NAME_BYTES[3])


def test_slot_three_is_the_row_read_off_the_running_machine() -> None:
    """D-081 recorded `86 16 68 A8 68 A2 FA 9A 48 98` from the live notice."""
    assert opening_name.GARBLED_NAME_BYTES[3] == (
        0x86, 0x16, 0x68, 0xA8, 0x68, 0xA2, 0xFA, 0x9A, 0x48, 0x98
    )


def test_it_is_not_the_real_name() -> None:
    """RAM at the same address holds "LAMBERT"; the ROM does not. If these ever
    coincide the bug has stopped being reproduced."""
    lambert = [0x8C, 0x01, 0x0D, 0x02, 0x05, 0x12, 0x14, 0xA0]
    for row in opening_name.GARBLED_NAME_BYTES.values():
        assert list(row[:len(lambert)]) != lambert


def test_an_unknown_slot_still_asks_the_rom(monkeypatch: pytest.MonkeyPatch) -> None:
    """A roster that grew would degrade to reading a ROM rather than to
    guessing - and to `None` if there is none, which the caller handles."""
    monkeypatch.setattr(assets, "find_c64_rom", lambda name: None)
    assert opening_name.garbled_name_codes(99) is None


def test_seventy_bytes_is_all_it_takes() -> None:
    """Recorded because the size is the argument: this is observed output, the
    way `gamedata_snapshot` records the deck art, not a vendored ROM."""
    total = sum(len(r) for r in opening_name.GARBLED_NAME_BYTES.values())
    assert total == 70
