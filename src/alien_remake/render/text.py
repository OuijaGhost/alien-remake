"""Writing text onto the C64 character grid — the renderer's shared toolkit.

Split out of :mod:`.frontend` (DISC-251). The call graph made this cut obvious
and DISC-250 recorded it before doing it: these nine methods have **zero
internal dependencies** — none of them calls anything in `frontend` except
`_c64_or_sysfont` — while **thirteen** methods outside depend on them. That is
the shape of a toolkit, not of a screen.

They are also the reason the remaining screens could not be separated. Every one
of welcome, opening, notice, intro, loading, title, selection and instructions
reaches for these, so any attempt to move a screen dragged them along.

Each writes on the exact 8x8 grid rather than at free pixel positions, because
the ROM writes screen codes into `$0400+n` and colour into `$D800+n`; a glyph
that is not cell-aligned is not something the original could have drawn.
"""

from __future__ import annotations

import pygame  # the project's one optional runtime dependency (D-009)

from . import c64
from .layout import _C64_CELL, _COLS
from .protocol import RendererState

_WELCOME_TM_SPRITE = (
    "#####..#...#",
    "..#....##.##",
    "..#....#.#.#",
    "..#....#...#",
    "..#....#...#",
)


class TextMixin(RendererState):
    """The text helpers. Mixed into :class:`~.pygame_app.PygameRenderer`."""

    def _blit_center(self, text: str, y: int, colour: tuple[int, int, int],
                     *, big: bool = False, bg: tuple[int, int, int] | None = None,
                     c64_font: bool = True) -> None:
        """Blit ``text`` horizontally centred, at unscaled row ``y``.

        R-01: real charset when every character is confirmed (never for
        ``big``, which is only used for a placeholder heading with no
        decoded-glyph equivalent), else the system-font fallback.
        """
        surf = self._c64_or_sysfont(text, colour, bg, big=big, c64_font=c64_font)
        x = (self._surface.get_width() - surf.get_width()) // 2
        self._surface.blit(surf, (x, y))
    def _blit_cells(self, text: str, col: int, row: int,
                    colour: tuple[int, int, int], *,
                    bg: tuple[int, int, int] | None = None,
                    c64_font: bool = False) -> None:
        """Blit ``text`` on the exact 8x8 **character grid**, one glyph per cell.

        D-064: the front-end screens are C64 *text* screens — every character
        occupies exactly one 8x8 cell — so the column positions transcribed
        from the live capture only hold if the remake lays glyphs out the same
        way. `SysFont` at this size is ~4.3px per character, so drawing a
        captured-column string as one `font.render` call compressed it to about
        half its true width. That was visible immediately: the row-9 rule under
        "FACE THE POWER OF THE UNKNOWN" is exactly 29 cells wide (cols 6-34,
        measured from screen RAM), and the text above it fell far short.
        Each glyph is centred within its own cell, so the line spans exactly
        ``len(text)`` columns regardless of the host font's metrics.

        ``c64_font`` defaults False — the loader screens (D-047) genuinely use
        the standard chargen ROM. **DISC-220:** the opening notice is not a
        loader screen; it is drawn by `ALIEN.prg` on the SELECTION screen's own
        field, which already uses ALIEN's cut-out charset (`_draw_selection`),
        so its caller passes `c64_font=True`.
        """
        cell = 8
        for i, ch in enumerate(text):
            cx, cy = (col + i) * cell, row * cell
            if bg is not None:
                self._surface.fill(bg, (cx, cy, cell, cell))
            if ch == " ":
                continue
            g = self._c64_or_sysfont(ch, colour, c64_font=c64_font)
            self._surface.blit(
                g, (cx + (cell - g.get_width()) // 2,
                    cy + (cell - g.get_height()) // 2),
            )
    def _blit_at(self, text: str, x: int, y: int,
                 colour: tuple[int, int, int], *,
                 bg: tuple[int, int, int] | None = None,
                 c64_font: bool = True) -> None:
        """Blit ``text`` at unscaled ``(x, y)`` (R-01: real charset when possible)."""
        self._surface.blit(
            self._c64_or_sysfont(text, colour, bg, c64_font=c64_font),
            (x, y),
        )

    def _blit_c64_text(self, codes: "list[int] | bytes", col: int, row: int,
                       colour: tuple[int, int, int]) -> None:
        """Draw screen ``codes`` via the game's own charset as cut-out text — the
        glyph's 0-bits painted in ``colour`` (the title's light-green $D021 seen
        through the black field), the 1-bits left as the black field. Faithful to
        how the C64 renders these cells (colour RAM = black), used by the title."""
        if self._tiles is None:
            return
        for i, code in enumerate(codes):
            glyph = self._tiles.glyph(code)
            cx = (col + i) * _C64_CELL
            cy = row * _C64_CELL
            for y, line in enumerate(glyph):
                for x, on in enumerate(line):
                    if not on:  # 0-bit -> the letter shape shows $D021
                        self._surface.fill(colour, ((cx + x), (cy + y), 1, 1))

    def _blit_tm(self, x: int, y: int) -> None:
        """Draw the loader's hand-made "™" bitmap at unscaled ``(x, y)``."""
        white = c64.rgb(c64.WHITE)
        for dy, bits in enumerate(_WELCOME_TM_SPRITE):
            for dx, ch in enumerate(bits):
                if ch == "#":
                    self._surface.fill(white, ((x + dx), (y + dy), 1, 1))

    def _blit_wrapped(
        self, text: str, col: int, row: int, fg: tuple[int, int, int],
        *, c64_font: bool = False,
    ) -> None:
        """Write ``text`` into screen RAM from (row, col), **wrapping**.

        The ROM copies a fixed-length field straight into `$0400+n`, so a
        string running past column 39 simply continues on the next row. Two of
        this screen's fields do exactly that, which is why laying them out as
        separate centred lines got the shape wrong.
        """
        pos = row * 40 + col
        while text:
            room = 40 - (pos % 40)
            run, text = text[:room], text[room:]
            self._surface.blit(
                self._c64_or_sysfont(
                    run, fg,
                    None if c64_font else c64.rgb(c64.BLACK),
                    c64_font=c64_font,
                ),
                ((pos % 40) * _C64_CELL, (pos // 40) * _C64_CELL),
            )
            pos += len(run)
    def _blit_screen_code(
        self, code: int, col: int, row: int, fg: tuple[int, int, int]
    ) -> None:
        """One chargen-ROM glyph by **screen code**, for the key's symbols."""
        if self._romfont is None:
            return
        glyph = self._romfont.glyph_rows(code)
        x0, y0 = col * _C64_CELL, row * _C64_CELL
        for py in range(8):
            bits = glyph[py]
            for px in range(8):
                if bits & (0x80 >> px):
                    self._surface.fill(fg, (x0 + px, y0 + py, 1, 1))

    def _blit_petscii(
        self, raw: str, col: int, row: int,
        fg: tuple[int, int, int], bg: tuple[int, int, int],
    ) -> None:
        """Blit a run of raw **PETSCII** codes through the chargen ROM.

        The logo is block graphics, so it cannot go through the ASCII helpers -
        it has to be drawn as the machine draws it. PETSCII `$C0-$DF` map to
        screen codes `$40-$5F` and `$A0-$BF` to `$60-$7F`; anything else falls
        back to a space rather than guessing a glyph.
        """
        if self._romfont is None:
            return
        for k, ch in enumerate(raw):
            c = ord(ch)
            if 0xC0 <= c <= 0xDF:
                code = c - 0x80
            elif 0xA0 <= c <= 0xBF:
                code = c - 0x40
            elif 0x20 <= c <= 0x3F:
                code = c
            else:
                continue
            glyph = self._romfont.glyph_rows(code)
            x0 = (col + k) * _C64_CELL
            y0 = row * _C64_CELL
            for py in range(8):
                bits = glyph[py]
                if not bits:
                    continue
                for px in range(8):
                    if bits & (0x80 >> px):
                        self._surface.fill(fg, (x0 + px, y0 + py, 1, 1))

    def _blit_center_keyed(
        self,
        segments: tuple[tuple[str, tuple[int, int, int] | None], ...],
        y: int,
        colour: tuple[int, int, int],
    ) -> None:
        """Blit a centred line whose *key* letters are reverse-highlighted.

        R-36 [C-live `boot_025_instructions.png`]: the real front-end boxes
        the individual key you press (the "1"/"Q" idiom from WELCOME, applied
        to "Y"/"N"/"RESTORE" mid-sentence). Each segment is
        ``(text, highlight_bg_or_None)``; a segment with a background is drawn
        reverse-video (dark text on that colour), the rest plain.
        """
        surfaces = [
            self._c64_or_sysfont(text, c64.rgb(c64.BLACK), bg, c64_font=False)
            if bg is not None
            else self._c64_or_sysfont(text, colour, c64_font=False)
            for text, bg in segments
        ]
        total = sum(s.get_width() for s in surfaces)
        x = (self._surface.get_width() - total) // 2
        for surf in surfaces:
            self._surface.blit(surf, (x, y))
            x += surf.get_width()
