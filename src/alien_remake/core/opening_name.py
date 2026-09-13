"""The opening death notice's **garbled name** — an original-game bug (D-081).

A player recalled that the C64 game "scrambled the name of the person that was
killed by the Alien". It does, and it is a genuine bug in the original, proved
byte-for-byte against the running machine.

`$5089`-`$509C` prints the notice::

    5089  LDA $64C2 / JSR index_x10 / TAY   ; victim slot * 10
    5092  LDA $A65E,Y / STA $06F9,X         ; copy 10 chars of the name
    50A0  LDA $50BF,Y / STA $0701,Y         ; then " HAS BEEN KILLED BY THE ALIEN"

The name table really is at `$A65E` — but that address is **under BASIC ROM**,
and the routine does not bank it out. So `LDA $A65E,Y` returns **BASIC ROM
bytes**, and the notice renders them as garbage.

Confirmed live: the notice row read `2B 69 FF 85 7A A5 2C 69` in the name field
while RAM at the same address held `8C 01 0D 02 05 12 14 A0` ("LAMBERT") and the
CONTROL panel — which reads the same table correctly, from code that *has*
banked BASIC out — showed "LAMBERT" at the same moment. Reading `$A690` through
VICE's `rom` bank reproduces the observed bytes exactly.

Since the remake is meant to be 1:1, it reproduces the bug rather than the
intended name.

**How it stopped needing the ROM (2026-08-30).** The read is from a *fixed*
address per crew slot, so what the original prints is seventy knowable bytes -
`$A668`-`$A6AD`, ten per slot. Those are captured in
:data:`GARBLED_NAME_BYTES` and the ROM is only consulted for a slot the capture
does not cover. Recording the output rather than shipping the source is the
same line `gamedata_snapshot` already draws for the deck art, and it means a
decoded behaviour no longer depends on whether the player happens to have an
emulator installed.
"""

from __future__ import annotations

from pathlib import Path

from .. import assets

#: The name table's address — under BASIC ROM, which is the whole problem.
NAME_TABLE = 0xA65E
NAME_STRIDE = 10
BASIC_ROM_BASE = 0xA000

#: **The archived VICE copy moved into `assets.find_c64_rom`**
#: (2026-08-30). It used to be a private fallback here, which meant
#: this module and the startup card searched different places and
#: disagreed about whether the ROM was present. One search now.


#: **The garbled bytes themselves, captured once (2026-08-30).**
#:
#: `$5092 LDA $A65E,Y` reads ten bytes per crew slot from under BASIC ROM, so
#: what the original prints is a fixed, knowable excerpt: seven slots of ten
#: bytes at `$A668`-`$A6AD`. **Seventy bytes of an eight-kilobyte ROM.**
#:
#: Recorded here for the same reason `gamedata_snapshot.DECK_PLANS` records the
#: deck art: it is *observed output*, not the source it came from. The ROM stays
#: unvendored - this is the handful of bytes the screen actually shows, which is
#: a decoded artefact like every other in this project, and it means the bug is
#: reproduced on every machine rather than only on one with an emulator
#: installed.
#:
#: Verified against the live capture in D-081: slot 3's `86 16 68 A8 68 A2 FA
#: 9A 48 98` is the row read off the running machine's notice.
GARBLED_NAME_BYTES: dict[int, tuple[int, ...]] = {
    1: (51, 132, 52, 165, 45, 164, 46, 133, 47, 132),      # $A668
    2: (48, 133, 49, 132, 50, 32, 29, 168, 162, 25),       # $A672
    3: (134, 22, 104, 168, 104, 162, 250, 154, 72, 152),   # $A67C
    4: (72, 169, 0, 133, 62, 133, 16, 96, 24, 165),        # $A686
    5: (43, 105, 255, 133, 122, 165, 44, 105, 255, 133),   # $A690
    6: (123, 96, 144, 6, 240, 4, 201, 171, 208, 233),      # $A69A
    7: (32, 107, 169, 32, 19, 166, 32, 121, 0, 240),       # $A6A4
}


def _basic_rom() -> bytes | None:
    # `find_c64_rom` covers your own copy, VICE's own filename, and a normal
    # VICE installation - so a player who has any C64 emulator gets the
    # original's garbled-name bug without being asked for anything.
    found = assets.find_c64_rom("basic.bin")
    for candidate in ((found,) if found is not None else ()):
        try:
            data = candidate.read_bytes()
        except OSError:
            continue
        if len(data) == 8192:
            return data
    return None


def garbled_name_codes(slot: int) -> list[int] | None:
    """The screen codes the original actually prints for victim ``slot``.

    ``slot`` is the crew's 1-based roster index (the ROM's `$64C2`). Returns
    ``None`` when the BASIC ROM isn't available, so the caller can fall back to
    the real name.
    """
    # **The captured bytes first (2026-08-30).** They are what the original
    # prints, so the bug now appears on every machine rather than only on one
    # with an emulator's ROMs lying about - which made a decoded behaviour
    # depend on the player's toolchain.
    captured = GARBLED_NAME_BYTES.get(slot)
    if captured is not None:
        return list(captured)
    # A real ROM still answers for any slot the capture does not cover, so a
    # roster that grew would degrade to reading rather than to guessing.
    rom = _basic_rom()
    if rom is None:
        return None
    off = NAME_TABLE + slot * NAME_STRIDE - BASIC_ROM_BASE
    if not (0 <= off <= len(rom) - NAME_STRIDE):
        return None
    return list(rom[off:off + NAME_STRIDE])
