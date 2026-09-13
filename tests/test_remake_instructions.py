"""The instruction pages (D-079), extracted from the loader's own BASIC.

The load-bearing finding here is a **negative** one: `INSTRUCTIONS.seq` on the
disk is the *printer* copy, not the screen text. Using it would have shipped
69-column text onto a 40-column screen.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.core import instructions
from alien_remake.core.flow import GameFlow, InputEvent, Screen

_HAVE = bool(instructions.pages())
_needs = pytest.mark.skipif(not _HAVE, reason="out/ not extracted")


@_needs
def test_exactly_ten_pages() -> None:
    """`PRINT CHR$(147)` (clear screen) appears exactly 10 times in BASIC lines
    10080-12180 — which is where "the 10 instruction pages" came from."""
    assert len(instructions.pages()) == 10


@_needs
def test_every_row_fits_a_40_column_screen() -> None:
    """The authors hand-wrapped the screen copy; nothing needs re-wrapping.

    This is the check that would have caught using `INSTRUCTIONS.seq` instead:
    its lines run to 69 characters.
    """
    for i, page in enumerate(instructions.pages()):
        for row in page:
            assert len(row) <= 40, f"page {i + 1}: {len(row)} cols: {row!r}"


@_needs
def test_pages_carry_the_games_own_headings() -> None:
    text = ["\n".join(p) for p in instructions.pages()]
    joined = "\n".join(text)
    for heading in ("THE GAME", "PERSONALITY CONTROL SYSTEM",
                    "SCREEN DISPLAYS", "COMMAND MONITOR", "HINTS FOR SURVIVAL"):
        assert heading in joined, heading
    assert all(p[0].strip() == "INSTRUCTIONS" for p in instructions.pages())


@_needs
def test_the_continue_prompt_is_not_page_content() -> None:
    """The renderer draws it; it must not be baked into the text."""
    for page in instructions.pages():
        assert not any("ANY KEY TO CONTINUE" in row for row in page)


@_needs
def test_seq_file_is_the_printer_copy_not_the_screen_copy() -> None:
    """Guard the D-079 finding itself, so nobody 'simplifies' back to the SEQ.

    `INSTRUCTIONS.seq` is opened by the BASIC only behind "SENT TO THE
    PRINTER? (Y/N)", and its lines are far too wide for a C64 screen.
    """
    seq = Path("out") / "Alien (USA, Europe)_files" / "INSTRUCTIONS.seq"
    if not seq.exists():
        pytest.skip("SEQ not extracted")
    widest = max(len(line) for line in seq.read_bytes().split(b"\x0d"))
    assert widest > 40, "the SEQ is the wide printer copy, not 40-column screen text"


def test_missing_file_degrades_quietly() -> None:
    assert instructions.pages(Path("does-not-exist.prg")) == []


@_needs
def test_yes_shows_the_pages_and_paging_resumes_the_boot() -> None:
    flow = GameFlow()
    flow.screen = Screen.INSTRUCTIONS
    flow.handle(InputEvent.YES)
    assert flow.screen is Screen.INSTRUCTION_PAGES
    assert flow.instruction_page == 0
    for _ in range(len(instructions.pages())):
        flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.LOADING_PLAY


def test_no_skips_straight_past_the_pages() -> None:
    flow = GameFlow()
    flow.screen = Screen.INSTRUCTIONS
    flow.handle(InputEvent.NO)
    assert flow.screen is Screen.LOADING_PLAY
