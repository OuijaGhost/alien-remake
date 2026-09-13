"""The game's own instruction pages, extracted from the loader's BASIC.

R-12/R-31 had "the 10 instruction pages" as their last open piece, and the
answer to "Y" on the DO YOU WANT INSTRUCTIONS? prompt was a stub that went
straight to the game.

**★ The obvious source is the wrong one.** The disk carries an
`INSTRUCTIONS.seq` file, and it is tempting to treat that as the screen text —
it is not. `MENU1.prg`'s BASIC opens it only behind a *printer* prompt::

    PRINT "   WOULD YOU LIKE THE INSTRUCTIONS."
    PRINT "      SENT TO THE PRINTER?  (Y/N)"
    ...
    F$ = "INSTRUCTIONS,S,R" : OPEN 15,8,15 : OPEN 2,8,2,F$

and its lines run to **69 characters**, which cannot fit a 40-column screen. It
is the printer copy, with wide margins.

The **on-screen** text is a long run of BASIC `PRINT` statements in the same
program (lines 10080-12180), already hand-wrapped by the authors to <= 40
columns, e.g.::

    PRINT " THE OBJECT OF THE GAME IS TO DESTROY"
    PRINT "THE ALIEN OR DRIVE IT AWAY FROM THE"

Pages are delimited by `PRINT CHR$(147)` (clear screen) — there are exactly
**10** of them, which is where "the 10 instruction pages" came from — and each
ends with "PUSH ANY KEY TO CONTINUE".

So everything here is extracted, not authored: the wording, the line breaks and
the page boundaries are the loader's own.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .. import assets

def default_menu1() -> Path | None:
    """The extracted loader BASIC, found from any working directory."""
    return assets.find(assets.FILES_DIR, "MENU1.prg")

#: The BASIC line-number range holding the on-screen instructions.
FIRST_LINE, LAST_LINE = 10080, 12180

_TOK_PRINT = 0x99
_TOK_CHR = 0xC7
_TOK_SPC = 0xA6
_TOK_TAB = 0xA3
_CLEAR_SCREEN = b"\xc7(147)"


def _basic_lines(path: Path) -> list[tuple[int, bytes]]:
    """Walk the BASIC linked list -> [(line number, tokenised body)]."""
    raw = path.read_bytes()
    load, mem = raw[0] | raw[1] << 8, raw[2:]
    out: list[tuple[int, bytes]] = []
    addr, i = load, 0
    while i < len(mem) - 4:
        nxt = mem[i] | mem[i + 1] << 8
        if nxt == 0:
            break
        num = mem[i + 2] | mem[i + 3] << 8
        end = i + (nxt - addr)
        if end <= i or end > len(mem):
            break
        out.append((num, mem[i + 4:end - 1]))
        addr, i = nxt, end
    return out


def _text(chunk: bytes) -> str:
    """A PETSCII string literal -> ASCII, dropping colour/RVS control codes."""
    out = []
    for b in chunk:
        if 0xC1 <= b <= 0xDA:
            out.append(chr(b - 0x80))
        elif 0x41 <= b <= 0x5A:
            out.append(chr(b))
        elif 0x61 <= b <= 0x7A:
            out.append(chr(b - 32))
        elif b == 0x20 or 0x21 <= b <= 0x3F:
            out.append(chr(b))
        # everything else is a colour / reverse-video / cursor control code
    return "".join(out)


def _rows_from_line(body: bytes) -> list[str]:
    """The screen rows one BASIC line prints (a bare PRINT emits a blank row)."""
    rows: list[str] = []
    for stmt in body.split(b":"):
        if _TOK_PRINT not in stmt:
            continue
        stmt = stmt[stmt.index(_TOK_PRINT) + 1:]
        row, i = "", 0
        while i < len(stmt):
            b = stmt[i]
            if b == 0x22:                                  # a quoted literal
                j = stmt.find(b'"', i + 1)
                if j < 0:
                    j = len(stmt)
                row += _text(stmt[i + 1:j])
                i = j + 1
                continue
            if b in (_TOK_SPC, _TOK_TAB):
                # `SPC(` and `TAB(` are SINGLE tokens that already include the
                # open paren — there is no "(" byte after them, so the digits
                # start immediately and run to ")".
                j = stmt.find(b")", i)
                if j < 0:
                    break
                digits = stmt[i + 1:j].decode("ascii", "ignore").strip()
                if digits.isdigit():
                    row += " " * int(digits)
                i = j + 1
                continue
            i += 1
        rows.append(row.rstrip())
    return rows


def pages(path: Path | None = None) -> list[list[str]]:
    """The 10 instruction screens, in order, as lists of screen rows.

    Returns ``[]`` when `MENU1.prg` has not been extracted, so a checkout
    without `out/` still runs.

    **Cached (DISC-255).** This reads `MENU1.prg` off disk and re-tokenises its
    BASIC, which `_draw_instruction_pages` was calling **once per frame** —
    1.5 ms of file I/O and parsing thirty times a second, for a file that
    cannot change while the game is running. The result is a pure function of
    the path, so an `lru_cache` is the whole fix.

    Callers must not mutate the returned lists; they are shared now.
    """
    menu1 = path if path is not None else default_menu1()
    if menu1 is None:                               # not extracted anywhere
        return []
    return _pages_for(menu1)


@lru_cache(maxsize=4)
def _pages_for(menu1: Path) -> list[list[str]]:
    """The parse itself, cached on the **resolved** file.

    Keyed on the resolved path rather than `pages()`'s optional argument: with
    the default `None` as the key, a cached result would survive
    `$ALIEN_REMAKE_ASSETS` pointing somewhere else, and a test that moves the
    asset root would get the previous answer. Caught exactly that way.
    """
    try:
        lines = _basic_lines(menu1)
    except OSError:
        return []
    out: list[list[str]] = []
    current: list[str] | None = None
    for num, body in lines:
        if not (FIRST_LINE <= num <= LAST_LINE):
            continue
        if _CLEAR_SCREEN in body:                   # PRINT CHR$(147) — new page
            if current:
                out.append(current)
            current = []
        if current is None:
            continue
        for row in _rows_from_line(body):
            # The trailing prompt is the renderer's to draw, not page content.
            if "ANY KEY TO CONTINUE" in row:
                continue
            current.append(row)
    if current:
        out.append(current)
    # Trim the blank rows that fall at a page's head or tail.
    trimmed = []
    for page in out:
        while page and not page[0]:
            page.pop(0)
        while page and not page[-1]:
            page.pop()
        if page:
            trimmed.append(page)
    return trimmed
