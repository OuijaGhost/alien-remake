"""The opening notice's garbled name — an original-game bug (D-081).

`$5092 LDA $A65E,Y` reads the crew-name table without banking BASIC ROM out, so
the notice prints ROM bytes. Proved byte-for-byte against the running machine:
the notice row read `2B 69 FF 85 7A A5 2C 69` while RAM at the same address held
"Lambert" and the CONTROL panel showed "Lambert" correctly at the same instant.
"""

from __future__ import annotations

import pytest

from alien_remake.core import opening_name

_HAVE = opening_name.garbled_name_codes(5) is not None
_needs = pytest.mark.skipif(not _HAVE, reason="BASIC ROM not available")


def test_name_table_sits_under_basic_rom() -> None:
    """That is the entire cause: $A65E is in the $A000-$BFFF ROM window."""
    assert 0xA000 <= opening_name.NAME_TABLE <= 0xBFFF
    assert opening_name.NAME_STRIDE == 10


@_needs
def test_lambert_reproduces_the_bytes_captured_live() -> None:
    """The exact bytes read off the real machine's notice row."""
    assert opening_name.garbled_name_codes(5)[:8] == [
        0x2B, 0x69, 0xFF, 0x85, 0x7A, 0xA5, 0x2C, 0x69
    ]


@_needs
def test_every_possible_victim_yields_garbage_not_a_name() -> None:
    """All three victims ($50EC = DALLAS/KANE/LAMBERT) are affected."""
    from alien_remake.core import constants

    assert len(constants.OPENING_VICTIM_CANDIDATES) == 3
    for slot in (1, 2, 5):
        codes = opening_name.garbled_name_codes(slot)
        assert codes is not None and len(codes) == 10
        # A real name would decode to letters (screen codes 1-26) throughout
        # its non-blank part; ROM bytes do not.
        letters = sum(1 for c in codes if 1 <= (c & 0x7F) <= 26)
        assert letters < len(codes) // 2, f"slot {slot} looks like real text"


@_needs
def test_slots_differ_from_each_other() -> None:
    """Each victim indexes a different 10 bytes of ROM, so the garbage differs."""
    seen = {tuple(opening_name.garbled_name_codes(s) or ()) for s in (1, 2, 5)}
    assert len(seen) == 3


def test_missing_rom_degrades_to_none() -> None:
    """Callers fall back to the real name rather than crashing."""
    assert opening_name.garbled_name_codes(999) is None


def test_the_overlap_with_the_message_is_exactly_two_columns() -> None:
    """**[C $5092/$50A0] P5-5.** `$06F9` (name) and `$0701` (message) are 8
    screen cells apart, so with a 10-char name field the message overlaps
    exactly its LAST TWO columns — the garbled-name effect (D-081), not a
    mis-positioning that should be "fixed" by moving the fields further
    apart. Pinned directly from the renderer's own named constants + the
    real field widths, so a future change to either can't silently widen or
    remove the overlap.
    """
    from alien_remake.render.frontend import _OPENING_MSG_COL, _OPENING_NAME_COL

    message = " has been killed by the ALIEN"
    name_field_width = opening_name.NAME_STRIDE  # the ROM's 10-char field
    name_end_col = _OPENING_NAME_COL + name_field_width  # exclusive
    overlap = name_end_col - _OPENING_MSG_COL

    assert overlap == 2, "the original overlaps exactly the name's last two columns"
    assert len(message) == 29, "the ROM's own 29-char message field width"


def test_the_message_keeps_the_roms_own_mixed_case() -> None:
    """**[C $0701, live oracle]** Lowercase, "ALIEN" excepted.

    `tools/vice-mcp/opening_row19.json` — `" +??E?%,? HAS BEEN KILLED BY THE
    ALIEN"` — predates DISC-215's case-bit fix and is an artifact of the old
    decoder, not the ROM's bytes. A fresh live-oracle read of screen RAM at
    `$0701` decodes to `" has been killed by the ALIEN"`::

        A0 08 01 13 A0 02 05 05 0E A0 0B 09 0C 0C 05 04 A0 02 19 A0 14 08 05
        A0 81 8C 89 85 8E A0 A0

    `$81 8C 89 85 8E` is `ALIEN` — the high bit selects case (DISC-215), so
    only that word is capitals; the rest is `0x01-0x1A` lowercase.
    """
    from alientools.gamedata import _screen_char

    codes = [
        0xA0, 0x08, 0x01, 0x13, 0xA0, 0x02, 0x05, 0x05, 0x0E, 0xA0, 0x0B, 0x09,
        0x0C, 0x0C, 0x05, 0x04, 0xA0, 0x02, 0x19, 0xA0, 0x14, 0x08, 0x05, 0xA0,
        0x81, 0x8C, 0x89, 0x85, 0x8E, 0xA0, 0xA0,
    ]
    decoded = "".join(_screen_char(c) for c in codes)
    assert decoded.rstrip() == " has been killed by the ALIEN"


def test_the_opening_notice_is_green_paper_black_ink_confirmed_live() -> None:
    """**[C-live, VICE]** Green background, black ink — not white, not swapped.

    Re-checked directly against the running original disk after a player
    report asked for "green background with white text": paused right after
    `sub_5049`'s `JSR` returns (`$7054`), `$D021` read back `$F5` (low nibble
    5 = green) and colour RAM for row 19 read uniformly `$00` (black) across
    every cell of the message. That is exactly D-145's finding and exactly
    what `_draw_opening` already draws; the report doesn't hold up against a
    fresh live capture, so the colours are unchanged (DISC-220).
    """
    import inspect

    from alien_remake.render import frontend

    src = inspect.getsource(frontend.FrontEndMixin._draw_opening)
    assert "c64.GREEN" in src and "c64.BLACK" in src


def test_the_message_uses_aliens_own_charset_not_the_loader_rom_font() -> None:
    """**DISC-220 (2nd pass):** the notice is drawn by `ALIEN.prg`, not a loader.

    `_draw_opening`'s comment already says the notice "sits on the SELECTION
    screen's own cleared field" - and `_draw_selection` draws its own text
    through ALIEN's cut-out charset (`c64_font=True`, the default), not the
    loader's ROM font. `_draw_opening` called `_blit_cells` without that flag,
    so it silently used `c64_font=False` - the ROM's **unshifted** bank, which
    has no lowercase glyphs at all. Setting the message text lowercase (the
    first half of DISC-220) rendered as capitals anyway, because the font
    being used cannot draw lowercase regardless of the string's case.
    """
    import inspect
    import re

    from alien_remake.render import frontend

    src = inspect.getsource(frontend.FrontEndMixin._draw_opening)
    for call in re.finditer(r"self\._blit_cells\((?:[^()]|\([^()]*\))*\)", src):
        assert "c64_font=True" in call.group(0) or "codes" in call.group(0), (
            "a _draw_opening text call is missing c64_font=True: "
            + call.group(0)
        )
