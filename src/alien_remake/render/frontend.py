"""The front end: every screen before (and after) the game itself.

Split out of :mod:`.pygame_app` (D-191). This is the loading interstitials, the
GREEN VALLEY PUBLISHING advert, the NOTICE and WELCOME menus, the instruction
pages, the title, the mode selection, the opening scenario, the two legend
screens, the quit advert, and the ending — 27 methods and ~900 lines, none of
which the play screen touches.

**Why it is this big.** These screens are the most *transcribed* part of the
remake: their content comes from real captures of the running disk
(`docs/reference/*_0400.bin`) and from the ROM's own screen-code tables, not
from a description of them. The spiral wipe, the border sweep, the sequential
text growth and the title's letter-by-letter build are all reproductions of
specific routines, and the constants here are the captured values.

Kept separate from :mod:`.play` because the two share almost nothing: the front
end draws PETSCII into a 40x25 grid, while the play screen composites sprites
and backdrops. What they do share — the text renderers and sprite cache — stays
in :mod:`.pygame_app`.
"""

from __future__ import annotations

from typing import Sequence

import pygame  # the project's one optional runtime dependency (D-009)

from .. import media
from ..core import constants, opening_name, sound
from ..core import gamedata_snapshot as data
from ..core.flow import SELECTION_OPTIONS, GameFlow
from ..core.crew import ROSTER
from ..core.modes import FrontEnd
from ..core.options import EDITION_WIDTH, EDITIONS, HELP_WIDTH, PRESET_KEY
from ..core.nostromo import NARCISSUS
from ..core.scoring import competence_rating
from ..core.state import GamePhase, WinRoute
from ..screens import ending
from . import c64
from .layout import (
    _BASIC_POKE_S, _BORDER_REVEAL_POKES, _C64_CELL, _COLS, _FRAME_HZ, _HEIGHT,
    _KEY_SLOT_COL, _KEY_SLOT_ROW, _PORTRAIT_SLOTS, _ROWS, _SPIRAL_COLS,
    _SPIRAL_ROWS, _SPIRAL_START_COLOUR, _SPIRAL_T1, _SPIRAL_T2,
    FRONTEND_SPEEDUP,
    _SPRITE_BANK_BASE, _TEXT_REVEAL_RATE, _WIDTH,
)
from .protocol import RendererState

_BORDER_COLOUR_FRONTEND = c64.rgb(c64.BLACK)
# [C-live] R-13: the opening death notice lands on the play screen's message
# row — read as row 19 on a real boot, with the CONTROL panel already drawn.
_OPENING_MSG_ROW = 19
# **[C $5092/$50A0] P5-5 — the ROM's own two field starts.** `$06F9` is the
# name field (row 19, screen col 1); `$0701` is the " has been killed..."
# field (col 9). $0701 - $06F9 = 8, so with a 10-char name field the message
# overlaps exactly its last TWO columns (9, 10) — the garbled-name effect
# (D-081), not a positioning bug. Named here so the geometry is asserted by a
# test instead of living only as magic numbers in `_draw_opening`.
_OPENING_NAME_COL = 1
_OPENING_MSG_COL = 9
def _welcome_border_colour(row: int, col: int, phase: int = 0) -> int | None:
    """C64 colour index for a WELCOME border cell, or ``None`` if not on the ring.

    Reproduces all 130 captured ring cells exactly at ``phase = 0``. Checks run
    in *reverse* draw order (left, bottom, right, top) so the side painted last
    wins at the four corners, matching the capture.

    **[C MENU1.prg lines 330-380 + 600 + 730] The ring is STATIC — it is drawn
    exactly once.** D-119 called it a chase; that was an invention (D-127). The
    routine that paints it is the loader's own `****MARQUIE****`::

        340 FOR T=1024 TO 1063 : POKE T+54273, T-1023 : POKE T,160 : NEXT   ' top
        350 FOR T=1024 TO 2024-40 STEP 40 : K=K+1 : POKE T+54272,K ...      ' left
        360 POKE T+54311,K : POKE T+T1,160 : NEXT                           ' right
        370 FOR T=1984 TO 2023 : POKE T+54273, T-1984 : NEXT                ' bottom

    i.e. blanks (`160` = `$A0`) with a colour ramp running around the edge.

    **The colour writes are off by one and that is the whole story.** Colour RAM
    for screen cell `T` is `T+54272`, but lines 340/370 poke `T+54273` — the
    cell to the *right*. So cell 1024 never receives a colour from the top-row
    pass; its colour comes only from line 350's first iteration, where `K` has
    just been incremented from 1 to 2. That is precisely why the live capture's
    top row reads `2,1,2,3,4,5,...`, and it needs no animation to explain it.

    **There is no loop.** `MARQUIE` has exactly one caller — line 600,
    `MM=9:PRINTCHR$(147):GOSUB330` — and the screen it paints then sits under
    line 730, `GETC$:IFC$=""THEN730`, a bare key-wait that pokes nothing. The
    ring is drawn once and never touched again. (The GREEN VALLEY *spiral* at
    line 150 is genuinely animated, but it is a one-shot 22-ring wipe from
    lines 200/210, not a running loop either.)

    ``phase`` is therefore always 0 in the app and is retained only so the
    existing drift guards can assert the ramp shape.
    """
    if not (row == 0 or row == _ROWS - 1 or col == 0 or col == _COLS - 1):
        return None
    if col == 0:                 # left column painted last
        return (row + 2 + phase) % 16
    if row == _ROWS - 1:         # then the bottom row
        return (col - 1 + phase) % 16
    if col == _COLS - 1:         # then the right column
        return (row + 2 + phase) % 16
    return (col + phase) % 16    # top row painted first
# Sprite 0's hand-drawn "™" (the ROM font has no such glyph): pointer `$07F8`
# = $0D -> data `$0340`, hi-res, unexpanded, `$D027` = 1 (WHITE). Only the
# top-left 12x5 pixels of the 24x21 sprite carry ink.
# ($D000,$D001) = (274, 72) with the `$D010` MSB set, minus the field origin
# (VIC 24, 50) -> 2px above the row-3 text top, i.e. a true superscript.
_WELCOME_TM_POS = (250, 22)
# The loader's own ™ placement: `311 CO=27:RO=14` through the sprite setup at
# line 3000 gives registers (234, 152), less the VIC field origin (24, 50).
_GREEN_VALLEY_TM_POS = (210, 102)
# The menu screens' green field + black text (the real C64 green, render/c64.py).
# **Ending-screen data now lives in `alien_remake.screens.ending` (DISC-240)**
# — decoded ROM strings and screen offsets, previously stranded behind this
# module's pygame import. Aliased so the drawing code below is unchanged.
# The game's own sprites (identified in out/sprites.png): the alien egg on the
# title screen, and the seven crew face portraits on the selection screen. The
# portraits sit in a single staggered row (game menu.png) — names alternate
# above/below so the labels don't collide; left-to-right that reads Dallas,
# Kane, Ripley, Ash, Lambert, Parker, Brett. The slot->identity mapping is a
# **PV-29 closed 2026-08-07 (D-179): the tie is decoded and exact.**
# `place_selected_char_sprite ($666C)` does `LDY $64FB / TYA / CLC /
# ADC #$BC / STA $07FA` - the portrait's sprite pointer is literally
# `$BC + the character slot`. Slots 1-7 therefore map to pointers
# `$BD`-`$C3`, i.e. `_PORTRAIT_SLOTS = (29..35)` in roster order, which
# is what this tuple already held. Not best-effort: arithmetic.
# The title's alien egg is **8 multicolor sprites**, not one (init_c $5DEB,
# verified against ALIEN.prg): sprite pointers $C9-$D0 → graphics-bank
# $3240-$343F, all sprite colour 5 (green) with shared multicolor $D025=7
# (yellow) / $D026=1 (white), positioned by the 16-byte table at $5DDB. Each
# tuple is (pointer, VIC-X, VIC-Y); screen pixel = (X-24, Y-50). The layout is
# 2-3-3 (a narrow top over two wider rows) — the egg cracked open over its nest.
_EGG_SPRITES = (
    (0xC9, 157, 106), (0xCA, 181, 106),
    (0xCB, 145, 127), (0xCC, 169, 127), (0xCD, 193, 127),
    (0xCE, 145, 148), (0xCF, 169, 148), (0xD0, 193, 148),
)
# Multicolor bit-pair → C64 colour index: 01=$D025 yellow, 10=sprite colour
# (green), 11=$D026 white (00 is transparent).
_EGG_MC = {1: c64.YELLOW, 2: c64.GREEN, 3: c64.WHITE}
# **[C $4460-$44B3] D-173 - the deck-plan key's own glyphs, finally extracted.**
# D-046 cited this key for *which* five symbols exist; the bytes it draws them
# with were never read. Decoding the key's strings (they are reverse-video
# screen codes, `$A0` = blank) leaves exactly three non-letter glyphs:
#
#     $4471  "LOCATION PTR" ... $E6 ... "GRILLE"        -> GRILLE      = $E6
#     $4492  $D3 ... "LADDER UP"                        -> LADDER UP   = $D3
#     $44A0  "CHARACTER POSTN" ... $D1 ... "LADDER DOWN" -> LADDER DOWN = $D1
#
# LOCATION PTR and CHARACTER POSTN carry no inline glyph because they are
# **sprites**, placed by the same routine at `$4371`-`$437E`
# ($D000/$D002 = X $28, $D001 = Y $6E, $D003 = Y $4E).
# **[C EXITO.prg lines 450-520] D-175 - the Q/QUIT advert's block-graphic
# logo.** Rendered through the real chargen ROM it reads **"ONE-STEP DEALER"**:
# lines 450-480 draw ONE-STEP in WHITE (`{5}`) on rows 12-15, lines 490-520
# draw DEALER in BLUE (`{31}`) on rows 18-21. Stored as the BASIC's own PETSCII
# so the glyphs stay the machine's rather than a redrawing of them.
#: **[C $443C/$4457] D-176** - the SHORT scenario's introduction prompt.
_INTRO_PROMPT_LINES: tuple[tuple[int, int, str], ...] = (
    (0, 0, "DO YOU WANT AN INTRODUCTION"),   # $443C -> $0400
    (1, 22, "PRESS Y OR N"),                 # $4457 -> $0456
)
#: **[C $4463-$44FF] D-173** - the DECK PLAN KEY + SOUND LEGEND. Rows/columns
#: are the screen offsets the routine writes to, so the layout is the ROM's.
#: `{G}`/`{U}`/`{D}` stand in for the three inline glyphs it draws
#: (GRILLE `$E6`, LADDER UP `$D3`, LADDER DOWN `$D1`).
_KEY_SCREEN_LINES: tuple[tuple[int, int, str], ...] = (
    (2, 2, "DECK PLAN KEY:"),                             # $4463 -> $0452
    (4, 6, "LOCATION PTR       {G}  GRILLE"),             # $4471 -> $04A6
    (6, 25, "{U}  LADDER UP"),                            # $4492 -> $0509
    (8, 6, "CHARACTER POSTN    {D}  LADDER DOWN"),        # $44A0 -> $0546
    (13, 0, "THIS IS THE SOUND OF "),                     # $44C1 -> $0608
)
_KEY_HEARTBEAT_TEXT = "THE HEARTBEAT OF    THE CURRENT CHARACTER."   # $44D6
#: The three sound demos, in the order `$4389`-`$43D0` plays them, each with
#: the effect it fires as it names itself.
_KEY_SOUND_LINES: tuple[tuple[str, str | None], ...] = (
    ("A GRILLE BEING REMOVED.", sound.GRILLE),            # $4500 + sfx_blip_a
    ("SOMETHING MOVING BETWEEN LOCATIONS.", sound.MOVEMENT),  # $4554 + blip_b
    ("THE TRACKER ALARM.", sound.TRACKER_ALARM),          # $452A + $64B6=$21
)
#: Row of the first option on the options screen (DEC-028). The preset row
#: sits here with a rule under it, then the six settings, ending clear of the
#: two hint rows at 22/23.
def _wrap_note(text: str) -> list[str]:
    """One report line, wrapped to the screen rather than truncated.

    These lines carry file paths, and half a path is worse than none - it reads
    as if the file were somewhere it is not.
    """
    import textwrap

    out: list[str] = []
    # Some notes arrive already broken into lines (the asset report explains
    # each missing file on a second, indented line), so split on those first
    # rather than letting the wrapper run them together.
    for part in text.splitlines() or [""]:
        out.extend(
            textwrap.wrap(part.strip(), _COLS - 4, subsequent_indent="  ")
            or [""]
        )
    return out


#: **Moved up one row (2026-09-03, C2's `turns` row).** The eleventh option
#: pushed the last row onto the hint line at row 22 - the same squeeze C4's
#: layout guards already caught once for the tenth. Reclaimed by trimming the
#: help box below (9 cells tall -> 8) rather than the list, which is the
#: whole reason the box exists.
_OPTION_FIRST_ROW = 9
_KEY_PRESS_ANY = "PRESS ANY KEY"                              # $6475 -> $07D8
_EXIT_LOGO_TOP: tuple[str, ...] = (
    "\xcf\xb7\xd0 \xaa\xb7\xd0 \xaa  \xcf\xb7\xb7    \xce\xb7\xcd \xb7\xd0\xb7\xb7 \xcf\xb7\xb7 \xcf\xb7\xcd",
    "\xb4 \xaa \xaa \xaa \xaa  \xcc\xaf  \xaf\xaf \xcd    \xaa   \xcc\xaf  \xcc\xaf\xce ",
    "\xb4 \xaa \xaa \xaa \xaa  \xb4       \xb7\xcd  \xaa   \xb4   \xb4    ",
    "\xcc\xaf\xba \xaa \xaa\xaf\xba  \xcc\xaf\xaf    \xcd\xaf\xce  \xaa   \xcc\xaf\xaf \xb4\xa0   ",
)
_EXIT_LOGO_BOTTOM: tuple[str, ...] = (
    "\xcf\xb7\xcd  \xcf\xb7\xb7  \xce\xb7\xcd  \xb4    \xcf\xb7\xb7  \xcf\xb7\xcd ",
    "\xb4 \xaa  \xcc\xaf   \xcc\xaf\xba  \xb4    \xcc\xaf   \xcc\xaf\xce ",
    "\xb4 \xaa  \xb4    \xb4 \xaa  \xb4    \xb4    \xb4 \xcd ",
    "\xcc\xaf\xce  \xcc\xaf\xaf  \xb4 \xaa  \xcc\xaf\xaf  \xcc\xaf\xaf  \xb4 \xaa ",
)
#: EXITO lines 410/420/430 - `{28}` is RED, and 420/430 inherit it.
_EXIT_LINES: tuple[tuple[int, str], ...] = (
    (5, "THESE AND MANY MORE"),
    (7, "FINE PROGRAMS MAY BE FOUND"),
    (9, "AT YOUR NEARBY"),
)
_KEY_GRILLE_GLYPH = 0xE6
_KEY_LADDER_UP_GLYPH = 0xD3
_KEY_LADDER_DOWN_GLYPH = 0xD1
# The title text, exactly as init_c/$5E74 writes it. The five "ALIEN" letters
# are the game's own glyphs $81/$8C/$89/$85/$8E on row 1 at columns 9,14,19,24,29
# (screen $0431/$0436/$043B/$0440/$0445); the epigraph screen codes go to row 22
# col 3 ($0773) and row 24 col 23 ($07D7). It is **cut-out** text: the glyph's
# 0-bits show the $D021 light-green background through the solid-black field, so
# the colour is light green (index $0D), not white — no colour-RAM write occurs.
_TITLE_LETTER_CODES = (0x81, 0x8C, 0x89, 0x85, 0x8E)
_TITLE_LETTER_COLS = (9, 14, 19, 24, 29)
_TITLE_LETTER_ROW = 1
# The two epigraph strings as the game's raw screen codes (from $5E4A / $5E67) —
# rendered through the game's charset they read 'We live as we dream : Alone' and
# 'JOSEPH CONRAD'. Kept as codes (not ASCII) so the exact custom glyphs are used.
_EPIGRAPH1 = bytes((
    0xC9, 0x97, 0x05, 0xA0, 0x0C, 0x09, 0x16, 0x05, 0xA0, 0x01, 0x13, 0xA0,
    0x17, 0x05, 0xA0, 0x04, 0x12, 0x05, 0x01, 0x0D, 0xA0, 0x1C, 0xA0, 0x81,
    0x0C, 0x0F, 0x0E, 0x05, 0xC9,
))
_EPIGRAPH1_AT = (3, 22)           # (col, row)
_EPIGRAPH2 = bytes((
    0x8A, 0x0F, 0x13, 0x05, 0x10, 0x08, 0xA0, 0x83, 0x0F, 0x0E, 0x12, 0x01, 0x04,
))
_EPIGRAPH2_AT = (23, 24)
def _center_routine_col(text: str, *, colour_code: bool = False) -> int:
    """Start column for BASIC's CENTER ROUTINE - **[C MENU1 390 / EXITO 2000].**

    ``2010 M=LEN(B$)`` · ``2020 IF M/2<>INT(M/2) THEN B$=B$+" ":M=M+1`` ·
    ``2050 PRINT SPC(21-N)...`` with ``N = M/2`` at full reveal, so the text
    begins at column ``21 - M/2``.

    ``colour_code`` adds the one character a leading colour control (``{5}``,
    ``{28}``, ``{31}``) occupies in ``B$``: it counts toward ``LEN`` but prints
    nothing. That is not a detail to skip - it is what makes a multi-line
    block-graphic logo line up, since only its first row carries one.
    """
    m = len(text) + (1 if colour_code else 0)
    if m % 2:
        m += 1
    return max(0, 21 - m // 2)
# **[C $5EC0] exact positions (D-049).** `main_dispatch` copies the 14-byte
# table at `$5EC0` straight into `$D000` (sprite X/Y pairs) and sets
# `$D010 = #$40` (sprite 6's X high bit). Decoded VIC coords, all on one row:
#   (48,82) (88,82) (128,82) (168,82) (208,82) (248,82) (288,82)
# Screen pixels are `(VIC_X - 24, VIC_Y - 50)` -> x = 24,64,104,144,184,224,264
# at y = 32. The remake previously spaced them evenly by a computed cell
# width, which was close but not the real layout.
_PORTRAIT_X = (24, 64, 104, 144, 184, 224, 264)   # unscaled screen px, left edge
_PORTRAIT_Y = 32                                   # unscaled screen px, top edge
# (name, is-above) per left-to-right portrait position, from game menu.png.
_PORTRAIT_LABELS = (
    ("Dallas", False), ("Kane", True), ("Ripley", False), ("Ash", True),
    ("Lambert", False), ("Parker", True), ("Brett", False),
)
# --- The GREEN VALLEY PUBLISHING loading screen (D-104) ---------------
# **[C MENU1.prg BASIC lines 150-320]** the loader's first screen is animated,
# and the animation is a **colour-RAM spiral** written in BASIC::
#
#   150 W=7 : REM ****SPIRAL****
#   160 CM=55296 : WD=40 : T1=39 : T2=25
#   200 FOR Q=11 TO 1 STEP -1 : GOSUB 220 : NEXT      ; sweep inward -> out
#   210 FOR Q=1 TO 11 : GOSUB 220 : NEXT              ; then back in
#   220 UL=CM+Q+Q*WD : UR=CM+Q*WD+(T1-Q)
#       LL=CM+(T2-Q)*WD+Q : LR=CM+(T1-Q)+WD*(T2-Q)
#   230 W=W+1 : IF W>15 THEN W=0                      ; next colour per ring
#   240 top edge  250 right edge  260 bottom  270 left  280 RETURN
#   300 VT=13 : B$="GREEN VALLEY"    310 VT=14 : B$="PUBLISHING "
#
# So it paints 22 concentric rectangular rings, each one flat colour, cycling
# 0-15, sweeping from ring 11 out to ring 1 and back again — then prints the
# publisher's name across the middle. Ring Q spans rows Q..25-Q and columns
# Q..39-Q. Note this is a *different* effect from the WELCOME screen's ring
# (D-064), which is a per-cell gradient captured live; the two were easy to
# confuse because both are rainbow rectangles.
_SPIRAL_RINGS: tuple[int, ...] = tuple(range(11, 0, -1)) + tuple(range(1, 12))
# **[C-live] D-142 — measured against the real machine (WarpMode off,
# `tools/vice-mcp/measure_greenvalley.py`), 2026-08-06.** BASIC's own
# POKE-loop drawing speed is genuinely slow: the spiral took ~11.0s to sweep
# all 22 rings once on the real disk image, and the whole GREEN VALLEY
# screen (spiral + "GREEN VALLEY"/"PUBLISHING" text + the `320
# FORXX=1TO900:NEXTXX` pause) ran ~14.1s before the WELCOME menu appeared —
# 5-6x longer than this remake's earlier hand-picked guesses (D-140/D-141).
# 11.0s at the app's real 30 fps is ~331 frames / 22 rings ~= 15
# frames/ring.
_SPIRAL_RATE = 15
def spiral_colours(steps: int) -> list[list[int | None]]:
    """Colour RAM after ``steps`` rings of the loader's spiral have been drawn.

    A direct replay of BASIC lines 220-280, in their own draw order (top,
    right, bottom, left) so later edges overwrite earlier ones at the corners
    exactly as the ROM leaves them. ``None`` means "never painted".
    """
    grid: list[list[int | None]] = [
        [None] * _SPIRAL_COLS for _ in range(_SPIRAL_ROWS)
    ]
    colour = _SPIRAL_START_COLOUR
    for ring in _SPIRAL_RINGS[: max(0, steps)]:
        colour = 0 if colour + 1 > 15 else colour + 1        # line 230
        top, bottom = ring, _SPIRAL_T2 - ring
        left, right = ring, _SPIRAL_T1 - ring
        for c in range(left + 1, right + 1):                 # 240 top
            grid[top][c] = colour
        for r in range(top, bottom + 1):                     # 250 right
            grid[r][right] = colour
        for c in range(right - 1, left - 1, -1):             # 260 bottom
            grid[bottom][c] = colour
        for r in range(bottom, top - 1, -1):                 # 270 left
            grid[r][left] = colour
    return grid
#: **[C $5D11] DISC-234** — the hull-breach fire palette, six passes.


def spiral_cells() -> list[tuple[int, int, int]]:
    """Every `POKE` the spiral makes, in order — `(row, col, colour)`.

    BASIC lines 200-280, and the animation really is **one block at a time**:
    the loader pokes colour RAM cell by cell and BASIC is slow enough that you
    watch it crawl. Drawing a whole ring per frame, as this used to, produced a
    stepping rectangle instead::

        200 FORQ=11TO1STEP-1:GOSUB220:NEXT   ; grow  innermost -> largest
        210 FORQ=1TO11:GOSUB220:NEXT         ; shrink largest  -> back
        230 W=W+1:IFW>15THENW=0              ; next colour, per ring
        240 FOR N=UL+1TOUR      : top    left -> right   ┐
        250 FOR N=URTOLRSTEPWD  : right  top  -> bottom  │ clockwise
        260 FOR N=LR-1TOLLSTEP-1: bottom right-> left    │
        270 FORN=LLTOULSTEP-WD  : left   bottom -> top   ┘

    Each ring is drawn clockwise; what reverses on the second pass is the
    *sequence of rings*, which is what reads as the sweep coming back down.
    """
    out: list[tuple[int, int, int]] = []
    colour = _SPIRAL_START_COLOUR
    for ring in _SPIRAL_RINGS:
        colour = 0 if colour + 1 > 15 else colour + 1        # line 230
        top, bottom = ring, _SPIRAL_T2 - ring
        left, right = ring, _SPIRAL_T1 - ring
        for c in range(left + 1, right + 1):                 # 240
            out.append((top, c, colour))
        for r in range(top, bottom + 1):                     # 250
            out.append((r, right, colour))
        for c in range(right - 1, left - 1, -1):             # 260
            out.append((bottom, c, colour))
        for r in range(bottom, top - 1, -1):                 # 270
            out.append((r, left, colour))
    return out


#: Every cell the spiral paints, built once. ~6.1 ms per POKE
#: (`_BASIC_POKE_S`) makes the whole sweep about 11 s, which is what the live
#: measurement it was derived from actually timed.
SPIRAL_CELLS: tuple[tuple[int, int, int], ...] = tuple(spiral_cells())


def center_routine_step(
    text: str, n: int, *, colour_code: bool = False
) -> tuple[str, int]:
    """One step of the CENTER ROUTINE — the visible string and its column.

    BASIC lines 400-450::

        400 M=LEN(B$)
        410 IFM/2<>INT(M/2)THENB$=B$+" ":M=M+1
        420 FORN=1TOM/2
        440 PRINTSPC(21-N)LEFT$(B$,N);RIGHT$(B$,N);

    `LEFT$(B$,N)` and `RIGHT$(B$,N)` are printed **adjacent**, starting at
    column `21-N`. So the first and last characters appear together in the
    middle and are pushed apart as more arrive — the word grows outward from
    its centre.

    The old model blanked the middle of a fixed-width string instead, which put
    every letter straight into its final position and merely filled the gap in.
    That is a different animation: nothing ever moves.
    """
    # `300 B$="{05}GREEN VALLEY"` — a leading PETSCII colour code counts toward
    # `LEN` at line 400 but prints no column, so it lengthens the string by one
    # (an extra step, and a different pad) while shifting the visible text one
    # column left. `310 B$="PUBLISHING "` has none. Getting this wrong put the
    # publisher's name a cell to the right of where the loader puts it.
    body = ("" + text) if colour_code else text
    padded = body + " " if len(body) % 2 else body
    half = len(padded) // 2
    n = max(0, min(n, half))
    if n == 0:
        return "", 21
    shown = padded[:n] + padded[-n:]
    return shown.replace("", ""), 21 - n


def reveal_from_centre(text: str, n: int, final_col: int) -> tuple[str, int]:
    """Step ``n`` of the CENTER ROUTINE, converging on a *captured* column.

    `center_routine_step` reproduces the BASIC's own `SPC(21-N)` arithmetic,
    which is right when the whole printed string is known. On the WELCOME
    screen it is not: line 620's `B$` carries embedded colour codes and the
    box's side bars, which count toward `LEN` but do not print where the name
    does. D-064 read the real final positions off the running disk, so those
    are kept and the growth is centred on them — same animation, landing where
    the capture says.
    """
    padded = text + " " if len(text) % 2 else text
    half = len(padded) // 2
    n = max(0, min(n, half))
    if n == 0:
        return "", final_col + half
    return padded[:n] + padded[-n:], final_col + half - n


def text_reveal_steps(text: str) -> int:
    """How many growth steps ``text`` needs — `M/2` in the BASIC, ceilinged."""
    return (len(text) + 1) // 2
def text_reveal_mask(text: str, n: int) -> str:
    """``text`` with everything but its outer ``n`` characters blanked out —
    the on-screen result of the CENTER ROUTINE's `LEFT$(B$,N)+RIGHT$(B$,N)`
    at step ``n``, expressed as a same-length string so it can be handed
    straight to the existing fixed-position blit helpers (which already skip
    spaces). ``n <= 0`` is fully blank; ``n >= text_reveal_steps(text)`` is
    the complete string.
    """
    length = len(text)
    if length == 0:
        return text
    n = max(0, min(n, text_reveal_steps(text)))
    if n == 0:
        return " " * length
    if 2 * n >= length:
        return text
    # `text[-n:]` would be `text[:]` at n==0 (Python's `-0 == 0`), already
    # handled above; safe here since n > 0.
    return text[:n] + " " * (length - 2 * n) + text[-n:]
def sequential_reveal_n(local_frame: int, texts: Sequence[str],
                        rate: int = _TEXT_REVEAL_RATE) -> list[int]:
    """Per-line growth step for a block of lines revealed **in order, one
    completing before the next starts** — the BASIC's own sequencing (each
    GOSUB390/2000 call runs to completion before the next PRINT/GOSUB
    statement executes). Returns one ``n`` per line in ``texts``, suitable
    for :func:`text_reveal_mask`.
    """
    out: list[int] = []
    budget = local_frame
    for text in texts:
        steps = text_reveal_steps(text)
        frames_needed = steps * rate
        if budget <= 0:
            out.append(0)
        elif budget >= frames_needed:
            out.append(steps)
            budget -= frames_needed
        else:
            out.append(budget // rate)
            budget = 0
    return out
# --- The WELCOME border's sweep-in reveal (D-143, retracts D-127's "static
# forever" reading of the ANIMATION — the off-by-one colour math D-127 found
# is untouched and still correct) ---------------------------------------------
# **[C MENU1.prg 330-380]** `****MARQUIE****` has exactly one caller and is
# never repainted afterward (D-127's "drawn once, never a loop" holds), but
# "drawn once" is not "drawn instantly": three POKE loops execute in order —
# top row left-to-right (40 cells), both side columns top-to-bottom together
# (25 rows x 2 cells), then the bottom row left-to-right (40 cells) — and
# BASIC's interpreted POKE loops are slow enough to see (D-142 measured the
# spiral at ~6ms/poke; live capture confirmed the border visibly assembling
# in stages, not popping in). `_welcome_border_reveal_step` orders every ring
# cell by which of those three passes first paints it; `_welcome_border_colour`
# (unchanged) still owns what colour each cell ends up — this only gates
# *when* it starts showing.
_BORDER_REVEAL_TOTAL_STEPS = _COLS + _ROWS + _COLS  # 40 + 25 + 40 = 105
_BORDER_REVEAL_RATE = _BORDER_REVEAL_TOTAL_STEPS / (
    _BORDER_REVEAL_POKES * _BASIC_POKE_S * _FRAME_HZ
)
def _welcome_border_reveal_step(row: int, col: int) -> int | None:
    """The sweep step at which (row, col) first gets painted, or ``None`` if
    it is never on the ring at all (matches `_welcome_border_colour`'s own
    membership test)."""
    if row == 0:
        return col                                    # top row, L to R
    if row == _ROWS - 1:
        if col in (0, _COLS - 1):
            return _COLS + (_ROWS - 1)                 # sides reach it first
        return _COLS + _ROWS + col                     # bottom row, L to R
    if col == 0 or col == _COLS - 1:
        return _COLS + row                             # sides, top to bottom
    return None


# The text toolkit moved to `.text` (DISC-251) — nine `_blit_*` helpers with no
# internal dependencies that thirteen methods here depend on. Re-exported
# because tests spell them against this module.
from .text import (  # noqa: E402
    TextMixin, _WELCOME_TM_SPRITE,
)

# The end screen moved to `.endscreen` (DISC-250). Every name it took is
# re-exported here, because tests and `pygame_app` spell them against this
# module; the ending *strings* live a layer further down again, in
# `screens.ending`. `__all__` makes the re-export explicit under `strict`.
from .endscreen import (  # noqa: E402
    _ENDING_ALIEN_DEAD, _ENDING_EGGS, _ENDING_NARCISSUS,
    _ENDING_ALL_CREW_LOST, _ENDING_NOSTROMO_RETURNS, _ENDING_NOSTROMO_DESTROYED,
    _ENDING_BRINGS_BACK, _ENDING_IS_INSANE, _ENDING_SURVIVORS,
    _ENDING_COMPETENCE, _ENDING_PRESS_ANY_KEY, _ENDING_ROWS,
    _ENDING_BRINGS_BACK_COL, _ENDING_NAME_VISIBLE, _END_RATING_ROW,
    _END_RATING_DIGIT_COL, _END_PRESS_KEY_ROW, _END_PRESS_KEY_COL,
    _END_SURVIVOR_HEADER_ROW, _END_SURVIVOR_FIRST_ROW, _END_SURVIVOR_ROWS,
    _BREACH_PALETTE, _BREACH_START, _BREACH_RUN0,
    _BREACH_LEG0, _BREACH_LEG_END, breach_spiral_cells,
    BREACH_SPIRAL, _MENU_BG,
)

__all__ = [
    "FrontEndMixin", "SPIRAL_CELLS", "spiral_cells", "text_reveal_steps",
    "TextMixin", "_WELCOME_TM_SPRITE",
    '_ENDING_ALIEN_DEAD',
    '_ENDING_EGGS',
    '_ENDING_NARCISSUS',
    '_ENDING_ALL_CREW_LOST',
    '_ENDING_NOSTROMO_RETURNS',
    '_ENDING_NOSTROMO_DESTROYED',
    '_ENDING_BRINGS_BACK',
    '_ENDING_IS_INSANE',
    '_ENDING_SURVIVORS',
    '_ENDING_COMPETENCE',
    '_ENDING_PRESS_ANY_KEY',
    '_ENDING_ROWS',
    '_ENDING_BRINGS_BACK_COL',
    '_ENDING_NAME_VISIBLE',
    '_END_RATING_ROW',
    '_END_RATING_DIGIT_COL',
    '_END_PRESS_KEY_ROW',
    '_END_PRESS_KEY_COL',
    '_END_SURVIVOR_HEADER_ROW',
    '_END_SURVIVOR_FIRST_ROW',
    '_END_SURVIVOR_ROWS',
    '_BREACH_PALETTE',
    '_BREACH_START',
    '_BREACH_RUN0',
    '_BREACH_LEG0',
    '_BREACH_LEG_END',
    'breach_spiral_cells',
    'BREACH_SPIRAL',
    '_MENU_BG',
]


class FrontEndMixin(RendererState):
    """`PygameRenderer`'s front-end screens.

    Draws into `self._surface` using the shared text/sprite helpers that stay on
    `PygameRenderer`; see :mod:`.protocol` for the shared attribute surface.
    """

    # --- text helpers -------------------------------------------------------
    def _draw_title(self, flow: GameFlow) -> None:
        """The title screen, rebuilt from the ROM (init_c $5DEB / $5E74), NOT
        invented: a **solid-black** field (clear_screen_fill tiles char $A0), the
        **8-sprite multicolor alien egg** centred, the five "ALIEN" letters
        spelling in one at a time as the game's own cut-out glyphs on row 1, and
        the mixed-case epigraph ('We live as we dream : Alone' / 'JOSEPH CONRAD')
        rendered through the game's charset. Matches out/vice_shots/boot_078."""
        self._surface.fill(c64.rgb(c64.BLACK))
        egg = self._title_egg_surface()
        if egg is not None:
            self._surface.blit(egg, (0, 0))
        green = c64.rgb(c64.LIGHT_GREEN)  # the $D021 seen through the cut-out text
        if self._tiles is not None:
            # R-30: the letters spell in one at a time ($5E90).
            for i in range(flow.title_letters_shown):
                self._blit_c64_text([_TITLE_LETTER_CODES[i]], _TITLE_LETTER_COLS[i],
                                    _TITLE_LETTER_ROW, green)
            self._blit_c64_text(_EPIGRAPH1, *_EPIGRAPH1_AT, green)
            self._blit_c64_text(_EPIGRAPH2, *_EPIGRAPH2_AT, green)
        else:
            # No extracted charset available (fresh clone): plain-font fallback.
            shown = "ALIEN"[:flow.title_letters_shown]
            self._blit_center(" ".join(shown), 12, green)
            self._blit_center("'WE LIVE AS WE DREAM : ALONE'", 176, green)
            self._blit_center("JOSEPH CONRAD", 186, green)
        # **`screen_fx` does not touch this screen.** DISC-311/313 wired it
        # in briefly; DISC-314 scoped it back down to the boot report only,
        # per the owner's own words: "the intro animation should just be for
        # the initial screen of dos text." This screen is a graphic one (the
        # egg + logo), not a text readout, and draws exactly as it did before
        # the option existed.
        # **[C-live] D-145** — the title/egg screen's border is BLACK, not the
        # play screen's blue: confirmed frame-by-frame in the player's own
        # recording (the starfield runs straight out into the border).
        self._present(_BORDER_COLOUR_FRONTEND)
    def _title_egg_surface(self) -> pygame.Surface | None:
        """Compose the title's 8 multicolor egg sprites from the game's own
        sprite data (``TileSet.region``), cached + pre-scaled. None without a
        tileset (the fallback title then shows no egg)."""
        # **D4 — a supplied egg, if there is one.** Answered before the
        # tileset, for the reason the deck plans are: composing the ROM's egg
        # needs the sprite bank, an image does not.
        if self._title_egg is None:
            supplied = media.title_art_path()
            if supplied is not None:
                try:
                    loaded = pygame.image.load(str(supplied)).convert_alpha()
                    self._title_egg = pygame.transform.smoothscale(
                        loaded, media.TITLE_ART_SIZE
                    )
                    return self._title_egg
                except Exception:  # pragma: no cover - depends on the file
                    pass
        if self._tiles is None:
            return None
        if self._title_egg is None:
            region = self._tiles.region
            surf = pygame.Surface((_WIDTH, _HEIGHT))
            surf.set_colorkey((0, 0, 0))
            surf.fill((0, 0, 0))
            for ptr, vx, vy in _EGG_SPRITES:
                off = ptr * 64 - _SPRITE_BANK_BASE
                data = region[off:off + 63]  # 21 rows * 3 bytes
                x0, y0 = vx - 24, vy - 50    # VIC coords -> screen pixels
                for row in range(21):
                    for bcol in range(3):
                        b = data[row * 3 + bcol]
                        for pair in range(4):
                            val = (b >> (6 - 2 * pair)) & 3
                            if val == 0:
                                continue     # transparent
                            colour = c64.rgb(_EGG_MC[val])
                            x = x0 + (bcol * 4 + pair) * 2  # multicolor: 2px wide
                            surf.fill(colour, (x, y0 + row, 2, 1))
            self._title_egg = pygame.transform.scale(
                surf, (_WIDTH, _HEIGHT))
        return self._title_egg
    # --- front-end (loading / notice / welcome / instructions) --------------
    def _draw_loading_menu(self, flow: GameFlow) -> None:
        """The GREEN VALLEY PUBLISHING loading screen — **animated**.

        The loader paints a colour-RAM spiral (see :func:`spiral_colours`) and
        then prints the publisher across the middle. This used to be a static
        "LOADING MENU" caption; the spiral is the screen.

        **[C MENU1.prg 200/210] D-142** — the BASIC sweeps the 22 rings
        **exactly once** (`FOR Q=11 TO 1 STEP -1` then `FOR Q=1 TO 11`, no
        repeat), then holds on the finished picture while it prints the
        publisher name and runs its post-spiral pause. `steps` is clamped at
        completion rather than wrapping via modulo, so this remake does the
        same: draw once, then hold.

        **[C MENU1.prg 300/310, D-143]** the two name lines are not printed
        whole — both go through the CENTER ROUTINE (`GOSUB390`), which grows
        each line outward from a fixed centre column one character-pair per
        pass, "GREEN VALLEY" completing before "PUBLISHING" starts. Live
        capture confirmed this directly (`tools/vice-mcp/
        capture_intro_animation.py`): "PUBLISHING" was caught as a lone "P"
        mid-growth before settling.
        """
        self._surface.fill(c64.rgb(c64.BLACK))
        # One POKE per `_BASIC_POKE_S`, not one ring per N frames: the loader
        # paints colour RAM a cell at a time and you can watch it travel.
        frame = self._frame_count * FRONTEND_SPEEDUP
        drawn = min(
            len(SPIRAL_CELLS), int(frame / (_FRAME_HZ * _BASIC_POKE_S))
        )
        for row, col, colour in SPIRAL_CELLS[:drawn]:
            self._surface.fill(
                c64.rgb(colour), (col * 8, row * 8, 8, 8)
            )
        # BASIC lines 300/311: the name centred on rows 13 and 14, growing in
        # only after the spiral itself has finished (300/310 run after the
        # GOSUB150 spiral call returns).
        spiral_frames = len(SPIRAL_CELLS) * _FRAME_HZ * _BASIC_POKE_S
        text_frame = int(max(0.0, frame - spiral_frames))
        # Line 310’s B$ is "PUBLISHING " — the trailing space is real, so line
        # 410 pads it to 12 and the routine runs 6 steps, not 5.
        n1, n2 = sequential_reveal_n(
            text_frame, ("GREEN VALLEY", "PUBLISHING ")
        )
        # **White, not green** — `300 B$="{05}GREEN VALLEY"`, and CHR$(5) is
        # PETSCII white; the colour carries over to line 310's "PUBLISHING ".
        #
        # **Rows 12 and 13.** The CENTER ROUTINE homes with `CHR$(19)` then
        # emits `VT-1` cursor-downs (`430 LEFT$(CUR$,VT-1)`), so `VT=13` lands
        # on row 12 and `VT=14` on row 13 — both were a row low.
        #
        # `_blit_at` scales its own coordinates; these are unscaled cells.
        white = c64.rgb(c64.WHITE)
        for row, word, n, cc in (
            (12, "GREEN VALLEY", n1, True),      # 300: B$ carries `{05}`
            (13, "PUBLISHING ", n2, False),      # 310: it does not
        ):
            shown, col = center_routine_step(word, n, colour_code=cc)
            if shown:
                self._blit_at(shown, col * 8, row * 8, white, c64_font=False)
        # `311 CO=27:RO=14:CL=1:GOSUB3000` — the trademark is **sprite 0**, 15
        # bytes read from line 10's DATA, white (`POKE53287,CL`, CL=1).
        # `3025 CO=(CO*8)+18` and `3030 POKE53249,(RO*8)+40` give registers
        # (234, 152); less the VIC field origin (24, 50) that is screen
        # (210, 102) — a superscript riding the top of the PUBLISHING row. The
        # DATA renders to the same glyph as `_WELCOME_TM_SPRITE`.
        if n2 >= text_reveal_steps("PUBLISHING "):
            self._blit_tm(*_GREEN_VALLEY_TM_POS)
        self._present(_BORDER_COLOUR_FRONTEND)
    def _draw_loading_play(self, flow: GameFlow) -> None:
        """The "LOADING…. / PLUG JOYSTICK INTO PORT TWO" card (D-021)."""
        self._surface.fill(c64.rgb(c64.BLACK))
        blue = c64.rgb(c64.BLUE)
        self._blit_center("LOADING....", 88, blue, c64_font=False)
        self._blit_center("PLUG JOYSTICK INTO PORT TWO", 112, blue, c64_font=False)
        self._present(_BORDER_COLOUR_FRONTEND)
    #: **[C MENU1.prg 505-555]** The notice's seven lines, as `(row, column,
    #: text)`. Each `PRINT` opens with two cursor-downs (`{17}{17}`), so the
    #: rows step by three from row 2, and each carries **its own indent** — 9,
    #: 7, 8, 8, 13, 9, 7. It is not a left-flush block and not centred.
    #:
    #: A shared paragraph helper used to left-align all seven at one x chosen to
    #: centre the widest, squaring off a deliberately ragged block. It claimed a
    #: live capture as its source; `boot_015_notice.png` shows the ragged
    #: indents plainly, so the claim never held.
    _NOTICE_LINES: tuple[tuple[int, int, str], ...] = (
        (2, 9, "We strongly suggest you"),
        (5, 7, "make a back-up copy of this"),
        (8, 8, "diskette for everyday use."),
        (11, 8, "Please store the original"),
        (14, 13, "in a safe place."),
        (17, 9, "Green Valley Publishing"),
        (20, 7, "a division of ShareData, Inc."),
    )
    #: **[C MENU1.prg 556 -> 3000]** `CO=33 : RO=18 : CL=1`, and the subroutine
    #: does `CO=(CO*8)+18` = **282** (so the X MSB is set) and `(RO*8)+40` =
    #: **184**. Sprite coordinates count from the border, so the visible-screen
    #: position is `(282-24, 184-50)`. The same arithmetic reproduces the two
    #: other `GOSUB 3000` call sites exactly — line 311's `(210, 102)` and line
    #: 621's `(250, 22)` — which is what makes it trustworthy here.
    #:
    #: The mark used to be positioned by paragraph flow, off the right edge of
    #: whichever line happened to be fifth.
    _NOTICE_TM_POS = (33 * 8 + 18 - 24, 18 * 8 + 40 - 50)
    #: **[C MENU1.prg 560/565]** The footer: a 25-cell bar of PETSCII 164
    #: (screen code `$64`) on row 22, then the reverse-video prompt on row 23,
    #: both yellow and both indented 9. The remake centred a single yellow
    #: prompt on row 21 and drew no bar.
    _NOTICE_FOOTER_COL = 9
    _NOTICE_FOOTER_W = 25
    _NOTICE_BAR_ROW, _NOTICE_PROMPT_ROW = 22, 23
    _NOTICE_BAR_CODE = 0xA4 - 0x40

    def _draw_notice(self, flow: GameFlow) -> None:
        """The ShareData back-up notice, laid out from MENU1's own BASIC."""
        self._surface.fill(c64.rgb(c64.BLACK))
        # D-065: this screen is genuinely mixed-case, so it is the loader's
        # SHIFTED chargen bank (lowercase + uppercase), unlike WELCOME.
        self._rom_shifted = True
        white, yellow = c64.rgb(c64.WHITE), c64.rgb(c64.YELLOW)
        for row, col, text in self._NOTICE_LINES:
            self._blit_cells(text, col, row, white)
        # D-065: "™" has no chargen glyph, and leaving it in the string made
        # that one line fall back to SysFont while its neighbours rendered in
        # the ROM font. It is sprite 0 in the original, drawn separately here.
        self._blit_tm(*self._NOTICE_TM_POS)
        for i in range(self._NOTICE_FOOTER_W):
            self._blit_screen_code(
                self._NOTICE_BAR_CODE, self._NOTICE_FOOTER_COL + i,
                self._NOTICE_BAR_ROW, yellow,
            )
        self._blit_cells(
            "PRESS ANY KEY TO CONTINUE", self._NOTICE_FOOTER_COL,
            self._NOTICE_PROMPT_ROW, c64.rgb(c64.BLACK), bg=yellow,
        )
        self._present(_BORDER_COLOUR_FRONTEND)

    def _draw_welcome(self, flow: GameFlow) -> None:
        """The "WELCOME TO ALIEN" front-end menu.

        **R-34 CLOSED (D-064, 2026-08-01).** Every element below was read out of
        the *running disk* — screen RAM `$0400`, colour RAM `$D800` (bank `io`)
        and the VIC/sprite registers — while the loader's WELCOME menu was on
        screen, rather than eyeballed from a screenshot. Text sits at its
        captured row/column instead of being centred, and two lines the remake
        drew CYAN are really LIGHT BLUE (`$0E`).
        """
        self._rom_shifted = False   # D-065: capitals -> unshifted chargen bank
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue, red = (
            c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE), c64.rgb(c64.RED),
        )
        # **[C MENU1.prg 330-380/600-720] D-143** — live capture proved this
        # screen builds up in stages, not all at once: the border sweeps in
        # (MARQUIE), then each text line grows outward from its centre,
        # completing top-to-bottom before the next line starts (the same
        # CENTER ROUTINE the GREEN VALLEY screen uses). `capture_welcome_
        # buildup.py` caught this directly — "FACE THE POWER OF THE UNKNOWN"
        # as a lone "F", "CHOOSE ONE OF THE ABOVE" as "CHOOSOVE", "COPYRIGHT
        # (C)1985..." as "COPYRIGHRESERVED" — genuine mid-growth frames, not
        # rendering glitches.
        if self._welcome_entered_frame is None:
            self._welcome_entered_frame = self._frame_count
        # DISC-211: the whole screen runs `FRONTEND_SPEEDUP` faster. Scaling
        # the frame keeps every measured rate below exactly as measured.
        local_frame = int(
            (self._frame_count - self._welcome_entered_frame) * FRONTEND_SPEEDUP
        )

        self._draw_welcome_border(local_frame)

        # **[C MENU1.prg 610-720]** Not every line here uses the CENTER
        # ROUTINE. `640/650/660/700/710/720` all `GOSUB390`; but the "1)
        # ALIEN"/"Q QUIT" item list (`670-690`) prints via `PRINTTAB` — a
        # direct, instant print, never caught mid-growth live (matching the
        # source: no `GOSUB390` on that path). So those two rows are excluded
        # from the growth sequence entirely, and print whole from frame one.
        # `610`/`630` (the box's top/bottom rule) and `660` (the row-9
        # underline, `N$(3)`) DO go through `GOSUB390` and so still cost real
        # time before the lines after them start, even though this remake
        # draws those three as instant shapes rather than growing glyphs —
        # included below as length-only placeholders so later lines are not
        # sequenced too early.
        lines = (
            "X" * 35,                          # 610: box top rule [C]
            "GREEN VALLEY PUBLISHING",          # 620
            "X" * 33,                          # 630: box bottom rule [C]
            "WELCOME TO ALIEN",                 # 640
            "FACE THE POWER OF THE UNKNOWN",    # 650
            "X" * 29,                          # 660: row-9 underline [C]
            "CHOOSE ONE OF THE ABOVE",          # 700
            "PLEASE LEAVE DISKETTE IN DRIVE",   # 710
            "COPYRIGHT(C)1985 ALL RIGHTS RESERVED",  # 720
        )
        # The border sweep (~48 frames, D-143) runs before any text starts,
        # same as the BASIC calling MARQUIE before it ever reaches the first
        # GOSUB390 text line.
        text_frame = max(0, local_frame - int(_BORDER_REVEAL_TOTAL_STEPS
                                              / _BORDER_REVEAL_RATE))
        (n_box_top, n_header, n_box_bottom, n_welcome, n_face,
         n_underline, n_choose, n_leave, n_copyright) = sequential_reveal_n(
            text_frame, lines
        )

        # The publisher banner's box: rows 2-4, cols 3-35, colour RED ($02).
        # Screen codes $55/$43/$49 (top), $42 (sides), $4A/$43/$4B (bottom) —
        # the ROM font's rounded-corner line-draw set, which paints a line
        # through the middle of each cell, so a 1px outline is the faithful
        # rendering of those glyphs.
        # **[C MENU1.prg 610/630]** The two rules are `GOSUB 390` calls like
        # everything else, so the box grows outward from its middle before the
        # name starts. It used to appear whole.
        # `610` and `630` are two **separate** CENTER ROUTINE calls with the
        # name between them, so the two rules grow independently: top, name,
        # bottom. Driving one rectangle off both counters made it grow, snap
        # back to nothing when the second counter started, and grow again.
        x0, y0 = 3 * 8 + 4, 2 * 8 + 4
        full_w, box_h = 33 * 8 - 8, 3 * 8 - 8
        cx, lw = x0 + full_w / 2, 1

        def rule(n: int, y: int) -> None:
            frac = min(1.0, n / max(1, text_reveal_steps(lines[0])))
            if frac <= 0:
                return
            w = max(2, int(full_w * frac))
            pygame.draw.rect(
                self._surface, red, pygame.Rect(int(cx - w / 2), y, w, lw)
            )

        rule(n_box_top, y0)                       # 610: VT=3 -> row 2
        rule(n_box_bottom, y0 + box_h - lw)       # 630: VT=5 -> row 4
        # The side bars belong to line 620's own `B$`, so they arrive with the
        # name rather than with either rule.
        if n_header > 0:
            for x in (x0, x0 + full_w - lw):
                pygame.draw.rect(
                    self._surface, red, pygame.Rect(x, y0, lw, box_h)
                )
        shown, col = reveal_from_centre("GREEN VALLEY PUBLISHING", n_header, 8)
        if shown:
            self._blit_cells(shown, col, 3, white)
        # 621: the trademark, once the name it belongs to is complete.
        if n_header >= text_reveal_steps("GREEN VALLEY PUBLISHING"):
            self._draw_welcome_tm()
        shown, col = reveal_from_centre("WELCOME TO ALIEN", n_welcome, 13)
        if shown:
            self._blit_cells(shown, col, 6, white)
        shown, col = reveal_from_centre(
            "FACE THE POWER OF THE UNKNOWN", n_face, 6
        )
        if shown:
            self._blit_cells(shown, col, 8, white)
        # Row 9, cols 6-34 is a run of screen code `$77`.
        # **PV-32 (underline) closed 2026-08-07 (D-182) - read from the char
        # ROM instead of approximated.** `$77`'s bitmap is `FF FF 00 00 00 00
        # 00 00`: a 2-pixel bar at the **very top** of the cell, rows 0-1. The
        # old rect started one scaled pixel down, so the rule sat a pixel low
        # against the real screen. Drawing the glyph itself removes the guess
        # entirely.
        # 660 is a `GOSUB 390` too, so the rule grows from the middle.
        rule_n = min(n_underline, 15)
        for i in range(2 * rule_n):
            col = int(6 + 29 / 2 - rule_n) + i
            if 6 <= col < 35:
                self._blit_screen_code(0x77, col, 9, white)
        # The two options: a reverse-video key cell at col 14, label from col 16.
        # Captured as screen codes $B1 (reverse '1') and $91 (reverse 'Q').
        # **[C MENU1.prg 670-690]** `PRINTTAB` — instant, never a GOSUB390
        # growth (D-143): shown in full as soon as the item-list loop reaches
        # it, which is between the box-bottom-rule and row-9-underline budget
        # slots above finishing and "CHOOSE ONE OF THE ABOVE" starting. Since
        # this remake always draws the WELCOME screen state for "whatever
        # frame we're on" rather than modelling that exact mid-sequence gate,
        # showing them once the underline's slot has started is close enough
        # to their real spot without inventing a growth animation they never
        # had.
        # Lines 670-690 run *before* line 700, so both options are on screen
        # before "CHOOSE ONE OF THE ABOVE" starts growing — they used to wait
        # for it.
        if n_underline >= text_reveal_steps(lines[5]):
            self._draw_welcome_option("1", "ALIEN", 12)
            self._draw_welcome_option("Q", "QUIT", 15)
        for text, final_col, row, colour, n in (
            ("CHOOSE ONE OF THE ABOVE", 8, 20, ltblue, n_choose),          # 700
            ("PLEASE LEAVE DISKETTE IN DRIVE", 5, 21, ltblue, n_leave),    # 710
            ("COPYRIGHT(C)1985 ALL RIGHTS RESERVED", 2, 23, white,
             n_copyright),                                                 # 720
        ):
            shown, col = reveal_from_centre(text, n, final_col)
            if shown:
                self._blit_cells(shown, col, row, colour)
        self._present(_BORDER_COLOUR_FRONTEND)
    def _draw_welcome_border(self, local_frame: int) -> None:
        """The rainbow ring around the WELCOME screen (D-064), sweeping in
        over ``local_frame`` frames rather than appearing whole (D-143).

        A 1-cell border of solid blocks (screen code `$A0`) whose colour walks
        a 16-entry ramp. Reading the ring back cell-by-cell gives four
        independent side rules; the **corners disambiguate the draw order** —
        at (0,0) and (24,0) the left column's value survives, at (0,39) the
        right column's, and at (24,39) the bottom row's. So the ROM paints
        top -> right -> bottom -> left, and later writes win. All 130 ring
        cells' final colours are reproduced exactly by `_welcome_border_colour`
        (D-064, unchanged); `_welcome_border_reveal_step` only gates *when*
        each cell starts showing, matching MARQUIE's own three-pass draw
        order (top row, both sides together, bottom row) — the sweep-in
        confirmed live in `capture_welcome_buildup.py`.
        """
        revealed = local_frame / _BORDER_REVEAL_RATE
        for row in range(_ROWS):
            for col in range(_COLS):
                step = _welcome_border_reveal_step(row, col)
                if step is None or step > revealed:
                    continue
                idx = _welcome_border_colour(row, col)
                if idx is None:
                    continue
                self._surface.fill(
                    c64.rgb(idx), (col * 8, row * 8, 8, 8)
                )
    def _draw_welcome_tm(self) -> None:
        """The "™" after PUBLISHING — a **sprite**, not a character (D-064).

        The C64 ROM font has no ™ glyph, so the loader hand-draws one: sprite 0
        enabled at ($D000,$D001) = (274, 72) with `$D010` bit 0 set, hi-res, no
        expansion, colour `$D027` = 1 (WHITE), pointer `$07F8` = $0D -> data at
        `$0340`. Only the top-left 12x5 pixels of the 24x21 sprite are used.
        Field coords: (274-24, 72-50) = (250, 22) — i.e. it sits 2px above the
        row-3 text baseline, which is what makes it read as a superscript.
        """
        self._blit_tm(*_WELCOME_TM_POS)
    def _draw_intro_prompt(self, flow: GameFlow) -> None:
        """"DO YOU WANT AN INTRODUCTION / PRESS Y OR N" - **[C $4405] D-176.**

        Reached only from the SHORT scenario (`game_init_mode $4317` returns
        immediately for FULL), and it waits on exactly two keys - `$441F CMP
        #$19` (Y) and `$4425 CMP #$27` (N), anything else looping back.

        Drawn with the loader's chargen ROM like every other front-end screen
        (D-047): `game_init_mode` runs before `set_charbase ($400A)` points the
        VIC at ALIEN's own charset.
        """
        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        for row, col, text in _INTRO_PROMPT_LINES:
            self._surface.blit(
                self._c64_or_sysfont(
                    text, c64.rgb(c64.LIGHT_BLUE), c64.rgb(c64.BLACK),
                    c64_font=False,
                ),
                (col * _C64_CELL, row * _C64_CELL),
            )
        self._present(c64.rgb(c64.BLACK))
    def _draw_intro_legend(self, flow: GameFlow) -> None:
        """The DECK PLAN KEY + SOUND LEGEND - **[C $4327-$43D3] D-173/D-176.**

        One screen that teaches both halves of the display: the five map
        symbols the deck plan uses, and the four sounds. The sound half reveals
        a line at a time, **playing each effect as it names it**, paced by
        `delay_long` (3.128 s, D-172) - eight of them before `prompt_and_wait`
        spins for a key.

        The three inline glyphs are the ROM's own (`$E6`/`$D3`/`$D1`, D-173);
        LOCATION PTR and CHARACTER POSTN have none because the routine places
        them as **sprites** (`$4371`-`$437E`), which is why their rows read as
        a label with a gap where the marker goes.
        """
        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        glyphs = {
            "{G}": _KEY_GRILLE_GLYPH,
            "{U}": _KEY_LADDER_UP_GLYPH,
            "{D}": _KEY_LADDER_DOWN_GLYPH,
        }
        for row, col, text in _KEY_SCREEN_LINES:
            x = col
            k = 0
            while k < len(text):
                tag = text[k:k + 3]
                if tag in glyphs:
                    self._blit_screen_code(
                        glyphs[tag], x, row, c64.rgb(c64.WHITE)
                    )
                    x += 1
                    k += 3
                    continue
                end = text.find("{", k)
                run = text[k:] if end < 0 else text[k:end]
                self._surface.blit(
                    self._c64_or_sysfont(
                        run, c64.rgb(c64.LIGHT_BLUE), c64.rgb(c64.BLACK),
                        c64_font=False,
                    ),
                    (x * _C64_CELL, row * _C64_CELL),
                )
                x += len(run)
                k += len(run)

        slot = self._legend_stage()
        self._blit_wrapped(slot, _KEY_SLOT_COL, _KEY_SLOT_ROW, c64.rgb(c64.WHITE))
        if self._legend_stage_index() > len(_KEY_SOUND_LINES):
            self._surface.blit(
                self._c64_or_sysfont(
                    _KEY_PRESS_ANY, c64.rgb(c64.YELLOW), c64.rgb(c64.BLACK),
                    c64_font=False,
                ),
                (23 * _C64_CELL, 24 * _C64_CELL),
            )
        self._present(c64.rgb(c64.BLACK))
    def _legend_stage_index(self) -> int:
        """How far the legend's reveal has got. 0 = the heartbeat line.

        Paced by `delay_long` (D-172), the same interval the title letters use,
        because it is the same routine's delay.
        """
        if self._legend_entered_frame is None:
            self._legend_entered_frame = self._frame_count
        local = self._frame_count - self._legend_entered_frame
        per = max(
            1, int(constants.TITLE_LETTER_TICKS * _FRAME_HZ / constants.TICK_HZ)
        )
        return local // per

    def _legend_stage(self) -> str:
        """The one description currently on screen, playing its sound as it
        arrives. **[C $061D]**

        The ROM copies the heartbeat description and then each sound name to
        the *same* address, so exactly one is on screen at a time and each
        replaces the last — which is why this returns a single line rather than
        a list. The effect fires on the frame its name appears
        ($439F/$43B8/$43CB), and `_legend_played` makes that once per arrival
        rather than once per frame.
        """
        stage = self._legend_stage_index()
        if stage <= 0:
            return _KEY_HEARTBEAT_TEXT
        n = min(stage, len(_KEY_SOUND_LINES)) - 1
        slot, effect = _KEY_SOUND_LINES[n]
        if effect and self._legend_played <= n:
            self._legend_played = n + 1
            clip = self._sound(effect)
            if clip is not None:
                try:
                    clip.play()              # type: ignore[attr-defined]
                except Exception:            # pragma: no cover - no audio device
                    pass
        return slot

    def _draw_exit_advert(self, flow: GameFlow) -> None:
        """The **Q QUIT** destination - **[C EXITO.prg] D-175, PV-01.**

        `Q` on the WELCOME menu was routed straight to `InputEvent.QUIT` and
        closed the window. On the real disk it does not exit: MENU1 line 740
        sets `CC=0` / `P$(0)="EXIT*"` and line 830 stuffs `LOAD"EXIT*",8` into
        the keyboard buffer. EXITO then draws this screen - the same MARQUIE
        border and the same centre-out CENTER ROUTINE the WELCOME menu uses -
        holds for `FOR XX=1TO3000`, and ends on **`SYS 64738`, a cold reset**.

        Layout straight from the BASIC: black border and background (line 400),
        three RED lines at rows 5/7/9 (410-430, `{28}`), then the block-graphic
        logo - **ONE-STEP** in WHITE on rows 12-15 (450-480, `{5}`) and
        **DEALER** in BLUE on rows 18-21 (490-520, `{31}`).
        """
        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        if self._exit_entered_frame is None:
            self._exit_entered_frame = self._frame_count
        local = self._frame_count - self._exit_entered_frame
        self._draw_welcome_border(local)                     # GOSUB 3000
        # The three text lines grow from their centres, in order (GOSUB 2000 is
        # the same routine as MENU1's 390).
        steps = sequential_reveal_n(local, [t for _, t in _EXIT_LINES])
        for (row, text), n in zip(_EXIT_LINES, steps):
            shown = text_reveal_mask(text, n)
            col = _center_routine_col(text, colour_code=row == 5)
            # **D-047: `c64_font=False`.** EXITO is a *loader* program - it
            # runs long before `ALIEN.prg` points the VIC at its own charset
            # (`set_charbase $400A`), so this screen uses the machine's
            # chargen ROM like every other front-end screen. Passing the
            # custom cut-out charset here renders nothing legible.
            self._surface.blit(
                self._c64_or_sysfont(
                    shown, c64.rgb(c64.RED), c64.rgb(c64.BLACK), c64_font=False
                ),
                (col * _C64_CELL, row * _C64_CELL),
            )
        # **The logo's four rows must share ONE start column** - they are
        # horizontal slices of the same glyphs. Centring each row on its own
        # length (the first cut) put row 0 one column right of the rest and
        # sheared the tops off the letters.
        #
        # The BASIC's CENTER ROUTINE gives the column: `2010 M=LEN(B$)`,
        # `2020 IF M/2<>INT(M/2) THEN M=M+1`, then `2050 PRINT SPC(21-N)` with
        # `N = M/2` at full reveal - so the text starts at **21 - M/2**. The
        # subtlety is that each word's first line carries a leading colour code
        # (`{5}` on 450, `{31}` on 490) which **counts toward `LEN` but prints
        # no column**, and that is exactly what makes all four rows agree: with
        # it counted they come out at 3 and 6 respectively.
        for rows, top, colour in (
            (_EXIT_LOGO_TOP, 12, c64.WHITE),
            (_EXIT_LOGO_BOTTOM, 18, c64.BLUE),
        ):
            col = _center_routine_col(rows[0], colour_code=True)
            for k, raw in enumerate(rows):
                self._blit_petscii(
                    raw, col, top + k, c64.rgb(colour), c64.rgb(c64.BLACK)
                )
        self._present(c64.rgb(c64.BLACK))   # EXITO line 400: POKE53280,0
    def _draw_welcome_option(self, key: str, label: str, row: int) -> None:
        """One WELCOME menu row at its captured column (D-064): a reverse-video
        key cell at col 14, then the label from col 16."""
        self._blit_cells(key, 14, row, c64.rgb(c64.BLACK), bg=c64.rgb(c64.WHITE))
        self._blit_cells(label, 16, row, c64.rgb(c64.WHITE))
    def _draw_instruction_pages(self, flow: GameFlow) -> None:
        """The disk's own instruction text, a screenful at a time.

        The copy comes from `INSTRUCTIONS.seq` — a separate SEQ file on the
        disk, not part of `ALIEN.prg` — so the wording, the line breaks and the
        indentation below are the disk's bytes, transcribed rather than
        written. The file carries **no page markers** (its only control byte is
        `$0D`), so the original's own display program must page by screenful;
        `core.instructions.pages()` does the same.
        """
        from ..core import instructions

        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue = c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE)
        book = instructions.pages()
        if not book:
            self._present(_BORDER_COLOUR_FRONTEND)
            return
        page = book[min(flow.instruction_page, len(book) - 1)]
        # **From row 0, not row 1.** The longest pages the loader's BASIC
        # produces are 24 lines, and an indented start left room for only 22 -
        # so the last two lines of pages 5-8 were silently cut, mid-sentence
        # ("...IT'S YOUR / REAL TIME INFORMATION WINDOW." simply stopped).
        # Row 0 to row 23 is exactly 24, with the footer on row 24.
        for row, line in enumerate(page[: _ROWS - 1]):
            if line.strip():
                # The file's own leading spaces are its indentation; keep them
                # by drawing from column 0 on the character grid.
                self._blit_cells(line[: _COLS], 0, row, white)
        self._blit_cells("PRESS ANY KEY", 13, _ROWS - 1, ltblue)
        self._present(_BORDER_COLOUR_FRONTEND)
    def _draw_instructions(self, flow: GameFlow) -> None:
        """The instructions prompt (boot_025_instructions.png).

        R-36 [C-live]: the real screen **reverse-highlights the key letters**
        mid-sentence — small blue boxes around just the "Y"/"N" in "(Y OR N)"
        and the leading "N" of "N WILL START THE GAME", and a pink/red box
        around "RESTORE" — the same "here's the key you press" idiom as
        WELCOME's "1"/"Q" boxes. It also renders the question in bright
        yellow rather than white. Both fixed here.

        **PV-32 closed 2026-08-07 (D-182): the shade is RED, and MENU1 says so.**
        R-36 hedged ("pink/magenta ... maybe not the exact Colodore shade") and
        the note carried that forward as unverified. It never needed a capture -
        this screen is MENU1's, and its line 10006 is
        `PRINTTAB(15)"{28}{17}A L I E N"`, where `CHR$(28)` is **red**. (Line
        10010's `{158}` is likewise the yellow already used for the question.)
        `c64.RED` was right all along.
        """
        self._surface.fill(c64.rgb(c64.BLACK))
        white, cyan = c64.rgb(c64.WHITE), c64.rgb(c64.CYAN)
        blue, pink = c64.rgb(c64.BLUE), c64.rgb(c64.LIGHT_RED)
        self._blit_center("A L I E N", 24, c64.rgb(c64.RED), c64_font=False)
        self._blit_center("DO YOU WANT INSTRUCTIONS?", 56, c64.rgb(c64.YELLOW), c64_font=False)
        self._blit_center_keyed(
            (("(", None), ("Y", blue), (" OR ", None), ("N", blue), (")", None)),
            80, cyan,
        )
        self._blit_center_keyed(
            (("N", blue), (" WILL START THE GAME", None)), 104, white,
        )
        self._blit_center_keyed(
            (("PRESS ", None), ("RESTORE", pink), (" TO EXIT THE PROGRAM", None)),
            144, c64.rgb(c64.YELLOW),
        )
        self._present()
    def _draw_first_run(self, flow: GameFlow) -> None:
        """The first-run question — **not the original**, and asked once.

        Two answers with the highlighted one explained underneath, in the same
        boxed-help shape as the options screen: this *is* the preset row, met
        before there is a screen to meet it on, and a player deciding between
        two editions of a game they have not played needs the difference spelt
        out at the moment of choosing rather than in a manual.

        Deliberately plain. It is the remake's own screen and the only thing
        the disk would never show, so dressing it in the loader's spiral or its
        PETSCII frame would pass off an invention as a decoded thing.
        """
        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue = c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE)
        yellow, green = c64.rgb(c64.YELLOW), c64.rgb(c64.GREEN)
        self._hot_clear()

        self._blit_cells("ALIEN", 17, 1, white)
        self._blit_cells("CHOOSE HOW YOU WANT TO PLAY", 6, 3, yellow)
        self._blit_cells("-" * 36, 2, 4, ltblue)

        for i, edition in enumerate(EDITIONS):
            row = 6 + i * 2
            selected = i == flow.edition_row
            hovered = self._hover == ("edition", i)
            # The click is the number key, not a second route: `_on_first_run`
            # already answers to "1" and "2", so the pointer reaches the same
            # handler by the same events the keyboard produces.
            self._hot_cells(2, row, 34, "edition", i)
            marker = ">" if selected else ("-" if hovered else " ")
            self._blit_cells(marker, 2, row, yellow)
            self._blit_cells(f"{i + 1}", 4, row, green)
            self._blit_cells(
                edition.label[:30], 6, row,
                white if selected or hovered else ltblue,
            )

        # The same 1px rule the options screen uses, for the same reason: the
        # explanation belongs on screen while the choice is live.
        # Nine rows, not eight: rows 11-19, so the label sits on 12, the five
        # lines run 14-18 and the bottom rule closes on 19. At eight the rule
        # was drawn straight through the last line of the explanation.
        x0, y0 = 1 * _C64_CELL, 11 * _C64_CELL
        w, h = 38 * _C64_CELL, 9 * _C64_CELL
        pygame.draw.rect(self._surface, ltblue, pygame.Rect(x0, y0, w, h), 1)
        chosen = EDITIONS[flow.edition_row % len(EDITIONS)]
        self._blit_cells(chosen.label[:EDITION_WIDTH], 3, 12, yellow)
        for i, line in enumerate(chosen.lines[:5]):
            self._blit_cells(line[:EDITION_WIDTH], 3, 14 + i, ltblue)

        self._blit_cells("UP/DOWN PICK   SPACE CHOOSES", 6, 21, green)
        self._blit_cells("OR PRESS 1 OR 2", 12, 22, green)
        # Said here because it is the one thing that makes an irreversible-
        # looking question reversible, and a player who does not know it will
        # hesitate over a choice that costs nothing.
        self._blit_cells("YOU CAN CHANGE THIS IN OPTIONS LATER", 2, 23, ltblue)
        self._present(_BORDER_COLOUR_FRONTEND)

    def _draw_boot(self, flow: GameFlow) -> None:
        """The startup report, in the game's own font — **not the original**.

        This is what the console window behind the game used to say (B1/B2).
        It is drawn here rather than printed so it can be styled and, on
        Windows, so the console can go away entirely without the messages going
        with it.

        Warnings are yellow and plain notes light blue: the distinction that
        matters is "something is missing and the game will be poorer for it"
        against "here is what I did", and a player scanning the screen should
        be able to tell them apart without reading. **`screen_fx` on**
        replaces this with a single phosphor-yellow tone throughout (the
        owner's own words: "the text should be yellow like in the original
        video") — the warn/note distinction is a remake-authoring convenience
        for the plain screen, not something the effect needs to preserve.
        """
        from . import screen_fx

        fx = flow.options.values.get("screen_fx") == "on"
        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue = c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE)
        yellow = c64.rgb(c64.YELLOW)
        header_colour = screen_fx.PHOSPHOR_YELLOW if fx else white
        rule_colour = screen_fx.PHOSPHOR_YELLOW if fx else ltblue
        note_colour = screen_fx.PHOSPHOR_YELLOW if fx else ltblue
        warn_colour = screen_fx.PHOSPHOR_YELLOW if fx else yellow
        self._hot_clear()

        self._blit_cells("ALIEN", 17, 1, header_colour)
        self._blit_cells("-" * 36, 2, 3, rule_colour)

        report = self.startup_report
        row = 5
        if report is not None:
            for note in report.notes:
                colour = warn_colour if note.warning else note_colour
                for line in _wrap_note(note.text):
                    if row >= _ROWS - 3:
                        break
                    self._blit_cells(line[:_COLS], 2, row, colour)
                    row += 1

        # **The prompt line (2026-09-05), `screen_fx` only.** This card's own
        # text, not ROM data (unlike the ending screen's decoded `PRESS ANY
        # KEY` - see that call site's own comment on why it does not get
        # one), so it is free to carry a command-style "> " when the option
        # is on - the owner's own description of the technique named this as
        # a distinct piece from the typing cursor.
        press_key = "PRESS ANY KEY"
        self._blit_cells(
            f"> {press_key}" if fx else press_key,
            11 if fx else 13, _ROWS - 2, header_colour,
        )
        # The whole screen is the target: this card has one action, and asking
        # a player to find a small one would be the opposite of the point.
        self._hot_add(pygame.Rect(0, 0, _WIDTH, _HEIGHT), "boot_done")
        if fx:
            # **Not the original (2026-09-04, expanded 2026-09-05, scoped to
            # this screen only 2026-09-05).** BOOT is timed (`TIMED_SCREENS`),
            # so `flow._screen_ticks` is already counted for it with no extra
            # plumbing. See :mod:`.screen_fx` for why this is the only screen
            # left carrying the effect.
            ticks = flow._screen_ticks
            screen_fx.apply_terminal_fx(
                self._surface, _C64_CELL, ticks, _ROWS, _COLS
            )
            # **Letters in the noise (2026-09-05), not the original:** "random
            # letters as well as blocks should appear in the noise."
            # `apply_terminal_fx` already drew the block static; this module
            # has no font to draw a letter with, so it is done here, using
            # the same fading-count shape as the blocks.
            if ticks < constants.SCREEN_FX_GLITCH_TICKS:
                remaining = constants.SCREEN_FX_GLITCH_TICKS - ticks
                for grow, gcol, letter in screen_fx.glitch_letter_cells(
                    ticks, _COLS, _ROWS, remaining
                ):
                    self._blit_cells(letter, gcol, grow, screen_fx.STREAK_COLOUR)
            # **The CRT power-on + degauss (2026-09-05), not the original:**
            # transforms everything drawn above, so it has to run last.
            screen_fx.apply_power_on(self._surface, ticks)
        self._present(_BORDER_COLOUR_FRONTEND)

    def _draw_manual(self, flow: GameFlow) -> None:
        """The whole manual in one place — **not the original**.

        Pages 0..n-1 are the loader's own instruction text (the same bytes
        `_draw_instruction_pages` shows on the boot chain, so the wording and
        line breaks stay the disk's). The last page is the DECK PLAN KEY +
        SOUND LEGEND that the SHORT scenario shows as its introduction, drawn
        **static**: the ROM reveals it a line at a time and plays each effect
        as it names it, which is right for an introduction you are being walked
        through and wrong for a reference page you opened deliberately.
        """
        from ..core import instructions

        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue = c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE)
        yellow = c64.rgb(c64.YELLOW)
        self._hot_clear()
        book = instructions.pages()

        if flow.manual_showing_legend:
            self._draw_manual_legend()
            if not book:
                # Without the derived assets there is no instruction text at
                # all, so the manual is this one page. Say why, rather than
                # letting it look as though the text was simply lost.
                self._blit_cells("INSTRUCTION PAGES NEED THE DISK - SEE README",
                                 0, _ROWS - 3, white)
        else:
            page = book[min(flow.manual_page, len(book) - 1)]
            # Row 0 for the same reason as the boot chain's copy: the longest
            # pages are 24 lines and anything less loses the end of them.
            for row, line in enumerate(page[: _ROWS - 1]):
                if line.strip():
                    # The file's own leading spaces are its indentation.
                    self._blit_cells(line[: _COLS], 0, row, white)

        # One row, so a full 24-line page still fits above it. The keys and
        # the position share it; at 38 characters the longest form still clears
        # the 40-column screen.
        total = flow.manual_pages()
        footer = (f"SPACE NEXT  LEFT BACK  ESC DONE  "
                  f"{flow.manual_page + 1}/{total}")
        self._blit_cells(footer[:_COLS], 0, _ROWS - 1, yellow)
        # P4: the footer's three words are the three things a pointer can do
        # here, so they are the three regions — clicking the word that names
        # the action is more discoverable than halves of the page, and it
        # cannot be got wrong by a reader who has not been told the rule.
        self._hot_cells(0, _ROWS - 1, 10, "manual_next")
        self._hot_cells(12, _ROWS - 1, 9, "manual_back")
        self._hot_cells(23, _ROWS - 1, 8, "manual_done")
        self._present(_BORDER_COLOUR_FRONTEND)

    def _draw_credits(self, flow: GameFlow) -> None:
        """CR4: **the exact shape of `_draw_manual`**, reusing its paging
        instead of inventing a third scrolling mechanism. Lines come from
        `media.credits_lines()` (CR1/CR2/CR3), already wrapped to the
        screen's own width - nothing here composes or truncates text, it
        only colours and places lines that call already produced.

        **Wrapped, not truncated (owner, 2026-09-04).** A long licence name
        or a Freesound.org URL used to be cut at column 40 with no sign
        anything was missing. `credits_lines()` wraps instead, and the two
        share the one convention that makes colouring possible without extra
        bookkeeping here: a line with no leading indent is a title, one
        starting with two spaces is a detail line under it, and an empty
        line is the gap between entries.
        """
        from .. import media
        from ..core.flow import CREDITS_ROWS_PER_PAGE

        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue = c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE)
        yellow = c64.rgb(c64.YELLOW)
        self._hot_clear()

        lines = media.credits_lines()
        self._blit_cells("CREDITS", 0, 0, white)
        start = flow.credits_page * CREDITS_ROWS_PER_PAGE
        page = lines[start:start + CREDITS_ROWS_PER_PAGE]
        for i, line in enumerate(page):
            if not line:
                continue
            colour = white if line.startswith("  ") else ltblue
            self._blit_cells(line[:_COLS], 0, 2 + i, colour)

        total = flow.credits_pages()
        footer = (f"SPACE NEXT  LEFT BACK  ESC DONE  "
                  f"{flow.credits_page + 1}/{total}")
        self._blit_cells(footer[:_COLS], 0, _ROWS - 1, yellow)
        self._hot_cells(0, _ROWS - 1, 10, "manual_next")
        self._hot_cells(12, _ROWS - 1, 9, "manual_back")
        self._hot_cells(23, _ROWS - 1, 8, "manual_done")
        self._present(_BORDER_COLOUR_FRONTEND)

    def _draw_manual_legend(self) -> None:
        """The deck-plan key and sound legend, revealed a line at a time.

        Same text and same rows as `_draw_intro_legend` (the ROM's own screen
        offsets) **and now the same reveal**: each sound's description appears
        as the sound itself plays.

        **This reverses a decision (owner, 2026-08-29).** It used to draw all
        four descriptions at once and play nothing, on the reasoning that a
        reference page you opened deliberately wants to be read rather than
        performed. The owner's call is that a *sound* legend which makes no
        sound is not a legend at all — you cannot learn what the tracker sounds
        like from the words "TRACKER ALARM". The reveal is the point of the
        screen, not decoration on it.

        So the two copies now share `_legend_stage`, and the only difference
        left between them is where you arrive from.
        """
        glyphs = {
            "{G}": _KEY_GRILLE_GLYPH,
            "{U}": _KEY_LADDER_UP_GLYPH,
            "{D}": _KEY_LADDER_DOWN_GLYPH,
        }
        for row, col, text in _KEY_SCREEN_LINES:
            x, k = col, 0
            while k < len(text):
                tag = text[k:k + 3]
                if tag in glyphs:
                    self._blit_screen_code(glyphs[tag], x, row,
                                           c64.rgb(c64.WHITE))
                    x += 1
                    k += 3
                    continue
                end = text.find("{", k)
                run = text[k:] if end < 0 else text[k:end]
                self._surface.blit(
                    self._c64_or_sysfont(run, c64.rgb(c64.LIGHT_BLUE),
                                         c64.rgb(c64.BLACK), c64_font=False),
                    (x * _C64_CELL, row * _C64_CELL),
                )
                x += len(run)
                k += len(run)
        slot = self._legend_stage()
        self._blit_wrapped(slot, _KEY_SLOT_COL, _KEY_SLOT_ROW,
                           c64.rgb(c64.WHITE))

    def _draw_options(self, flow: GameFlow) -> None:
        """The options screen — **not the original** (`core.options`).

        A help box across the top explains whichever row the cursor is on, so
        the meaning of a value is on screen at the moment it can be changed
        rather than in a manual. Values sit between arrows to show they cycle;
        the ROM's own screens never do this, which is exactly why the affordance
        has to be explicit here.
        """
        self._rom_shifted = False
        self._surface.fill(c64.rgb(c64.BLACK))
        white, ltblue = c64.rgb(c64.WHITE), c64.rgb(c64.LIGHT_BLUE)
        yellow, green = c64.rgb(c64.YELLOW), c64.rgb(c64.GREEN)
        model = flow.options

        self._blit_cells("OPTIONS", 16, 0, white)

        # The help box: a 1px rule around rows 2-9, with the selected option's
        # explanation inside. Drawn as rects rather than line-draw glyphs -
        # the ROM's box (WELCOME's publisher banner) is a real PETSCII frame,
        # and borrowing those glyphs here would dress an invented screen as a
        # decoded one.
        # Rows 1-8 (2026-09-03, C2's `turns` row: was 1-9, trimmed by one to
        # reclaim a row for the eleventh option rather than squeeze the list).
        # The five help-text lines below still fit: they run rows 4-8.
        # `_OPTION_FIRST_ROW` moved 10 -> 9 (2026-09-04, `screen_fx`'s row: the
        # twelfth option) for the same reason - the gap between the box and
        # the list was the one row of slack left, so this is the one that
        # goes when the list grows again.
        x0, y0 = 1 * _C64_CELL, 1 * _C64_CELL
        w, h = 38 * _C64_CELL, 8 * _C64_CELL
        pygame.draw.rect(self._surface, ltblue, pygame.Rect(x0, y0, w, h), 1)
        spec = model.spec
        self._blit_cells(spec.label[:HELP_WIDTH], 3, 2, yellow)
        for i, line in enumerate(spec.help_text[:5]):
            self._blit_cells(line[:HELP_WIDTH], 3, 4 + i, ltblue)

        # Seven rows on single spacing rather than four on double: the list
        # outgrew the airier layout, and squeezing the help box instead would
        # cost the explanation that is the point of the screen.
        self._hot_clear()
        self._options_model = model
        for i, row_spec in enumerate(model.specs):
            # The preset owns row 0 and the rule under it owns the next, so
            # every real setting sits one lower than its index.
            row = _OPTION_FIRST_ROW + i + (1 if i else 0)
            selected = i == model.row
            value = model.displayed(row_spec)
            # P4/P5: the whole line picks the row; the two arrows change it.
            # Recorded here, where the row is decided, so a click cannot land
            # anywhere but on what was drawn.
            self._hot_cells(2, row, 17, "option_row", i)
            hovered = self._hover == ("option_row", i)
            marker = ">" if selected else ("-" if hovered else " ")
            self._blit_cells(marker, 2, row, yellow)
            self._blit_cells(row_spec.label[:14], 4, row,
                             white if selected else
                             (white if hovered else ltblue))
            # Arrows are drawn only on the selected row: they say "these keys
            # do something *now*", and showing them on every row would suggest
            # seven independently changeable things under one cursor.
            shown = f"< {value.upper()} >" if selected else value.upper()
            self._blit_cells(shown[:20], 19, row, yellow if selected else white)
            if selected:
                # `< ` and ` >` sit at the ends of the drawn string, so their
                # columns follow the value's own length rather than a guess.
                self._hot_cells(19, row, 2, "option_less", i)
                self._hot_cells(19 + len(shown) - 2, row, 2, "option_more", i)
            # The preset is a control over the rows under it, not another row
            # like them, so it gets a rule to sit above rather than being
            # silently one of the list.
            if row_spec.key == PRESET_KEY:
                self._blit_cells("-" * 36, 2, row + 1, ltblue)

        self._blit_cells("UP/DOWN PICK   LEFT/RIGHT CHANGE", 4, 22, green)
        self._blit_cells("SPACE OR ESC RETURNS - SAVED", 6, 23, ltblue)
        self._hot_cells(6, 23, 28, "options_done")
        self._present(_BORDER_COLOUR_FRONTEND)

    def _draw_selection(self, flow: GameFlow) -> None:
        """The crew portraits + Full Game / Short Scenario chooser
        (matching docs/reference/game menu.png)."""
        # CR5: keep the pointer's copy of the settings fresh from here too, not
        # only from `_draw_options` - a click on this screen has to agree with
        # what this screen just drew, even if OPTIONS was never opened this
        # session (in which case `_options_model` would otherwise still be the
        # `None` it starts as, and the fifth row's click would silently miss).
        self._options_model = flow.options
        # **[C $5FC3] D-050:** `sub_screen_setup` sets `$D021 = 0` (BLACK),
        # fills colour RAM with 5 (GREEN) and the screen with `$A0` (solid) —
        # so every cell renders green, and a text cell (a cut-out glyph, same
        # green colour RAM) shows its letters in the black `$D021` through the
        # green fill. i.e. **paper = green, ink = black**. The remake had this
        # inverted (black fill, green letters).
        paper, ink = c64.rgb(c64.GREEN), c64.rgb(c64.BLACK)
        fg = ink  # sprites: `$5EEF` zeroes $D027-$D02E, so portraits are black
        self._surface.fill(paper)
        # Seven portraits in one staggered row; names alternate above/below.
        # D-049: the ROM's own sprite X/Y table, not an even-spacing guess.
        # `_blit_sprite` centres on (cx, cy), so offset by half the 24x21 sprite.
        for i, slot in enumerate(_PORTRAIT_SLOTS):
            cx = (_PORTRAIT_X[i] + 12)
            cy = (_PORTRAIT_Y + 10)
            # D1: the player's own portrait if there is one, the ROM's sprite
            # otherwise. `ROSTER` is in the same order as the decoded slot
            # table, which is what makes the index shared.
            self._blit_portrait(ROSTER[i][0], slot, cx, cy, fg)
            name, above = _PORTRAIT_LABELS[i]
            name_surf = self._c64_or_sysfont(name, ink, paper)
            lx = cx - name_surf.get_width() // 2
            ly = cy - 26 if above else cy + 22
            self._surface.blit(name_surf, (lx, ly))

        # R-32: the real selection has NO cursor/marker — you press the key for
        # the option you want. List both plainly, no highlight.
        #
        # **The prompt follows the front end (DISC-263).** CLASSIC prints the
        # ROM's own "CONTROL:1 / CONTROL:2", because that is the chord `$5F36`
        # polls for. QUICK takes bare 1 and 2, so printing the chord would be
        # instructing the player to press something that does nothing.
        chord = flow.front_end is FrontEnd.CLASSIC
        self._blit_at("GAME SELECTION:", 40, 108, ink, bg=paper)
        # P4: this screen is laid out in pixels at a 12px pitch, not character
        # cells, so its regions are recorded in pixels too rather than being
        # forced through the cell helper.
        self._hot_clear()
        # **DEC-047, UPDATED only.** ORIGINAL's real screen has no cursor at
        # all (R-32/D-018 - you press the key for what you want), so
        # `flow.selection_row` only ever moves under UPDATED; `is_orig` here
        # is the same test `flow._on_selection` gates the cursor keys on,
        # kept in sync deliberately rather than duplicated with its own
        # logic that could drift from it.
        from ..core.options import is_original
        is_orig = is_original(flow.options.as_dict())

        def _row_hot(n: int) -> None:
            rect = pygame.Rect(44, 122 + n * 12, 180, 12)
            self._hot_add(rect, "selection", n)
            # P5: the row under the pointer gets the paper/ink swap the panel
            # uses for its cursor. This screen has no cursor of its own under
            # ORIGINAL -- the ROM's has none either (R-32) -- so a hover is
            # the only highlight there; under UPDATED the keyboard/joystick
            # cursor (`flow.selection_row`) draws the same highlight too.
            if self._hover == ("selection", n) or (
                not is_orig and flow.selection_row == n
            ):
                pygame.draw.rect(self._surface, ink, rect)

        for i, (label, _mode) in enumerate(SELECTION_OPTIONS):
            key = f"CONTROL:{i + 1}" if chord else f"PRESS {i + 1}"
            _row_hot(i)
            lit = self._hover == ("selection", i) or (
                not is_orig and flow.selection_row == i
            )
            self._blit_at(f"{key}    {label}", 48, 126 + i * 12,
                          paper if lit else ink,
                          bg=ink if lit else paper)
        # **Not the original.** The ROM's screen has exactly two rows; these
        # two are the remake's, and they print as bare "PRESS 3"/"PRESS 4"
        # under either front end because neither is a chord the ROM polls for
        # - labelling them CONTROL:3/CONTROL:4 would dress an invented option
        # as a decoded one.
        extra = len(SELECTION_OPTIONS)
        extra_rows = ["INSTRUCTIONS", "OPTIONS"]
        # **CR5 — hidden under ORIGINAL, not merely unreached.** The row is
        # left off the list entirely rather than drawn and ignored, matching
        # `flow._on_selection`'s own refusal: a row that still answers a key
        # it does not show would be worse than no row, and one that is drawn
        # but does nothing on fire would be the same trap from the other side.
        if not is_orig:
            extra_rows.append("CREDITS")
        for j, label in enumerate(extra_rows):
            _row_hot(extra + j)
            lit = self._hover == ("selection", extra + j) or (
                not is_orig and flow.selection_row == extra + j
            )
            self._blit_at(f"PRESS {extra + j + 1}    {label}", 48,
                          126 + (extra + j) * 12,
                          paper if lit else ink,
                          bg=ink if lit else paper)
        if not chord and self._debug_markers:
            # Armed with 0, so it is visible that it is on before a game starts.
            #
            # **Moved to the top, 2026-08-30 (owner).** It used to follow the
            # option rows at `126 + 4 * 12` = 174, and the copyright line is
            # drawn at 176 - so it was two pixels into "PAUL CLANSEY (c)1984
            # CONCEPT SOFTWARE" and unreadable underneath it. The band above
            # the portraits is the only part of this screen with nothing in it:
            # the crew names sit at y=16, so a line at y=2 clears them.
            self._blit_at("DEBUG ON", 8, 2, ink, bg=paper)
        # **Follows the row count, not a fixed 176 (found 2026-09-03 taking a
        # real screenshot for README.md).** CR5's CREDITS row is a THIRD extra
        # row under any non-ORIGINAL profile, landing at `126 + 4*12` = 174 -
        # the exact collision the comment above already fixed once for
        # DEBUG ON, reopened from the other side once `extra_rows` could hold
        # three items instead of two. Same 2px gap convention as before.
        copyright_y = 126 + (extra + len(extra_rows)) * 12 + 2
        self._blit_center(
            "PAUL CLANSEY   c1984   CONCEPT SOFTWARE", copyright_y, ink, bg=paper
        )
        # **[C-live] D-145** — the selection screen's border is GREEN, matching
        # its own green field, so the inset frame reads as one solid block:
        # confirmed frame-by-frame in the player's own recording. (`$5FC3`
        # fills colour RAM with 5; the border register is set to match.)
        self._present(paper)
    def _draw_opening(self, flow: GameFlow) -> None:
        """The opening death notice — a **separate pre-screen** (P-4).

        `start_game` runs, in order::

            704E  JSR game_init_mode   ; clears $0400-$06E8 to $A0
            7051  JSR sub_5049         ; the notice, then 2x delay_long
            7054  LDA #$06 / STA $D020 ; ...and only NOW the play screen is built
            7065  LDA $01 / AND #$FE   ; ...and only now is BASIC ROM banked out

        So the notice sits alone on a cleared screen and times out into play.

        **This reverts R-13.** I had made it an overlay on the play screen after
        a live capture appeared to show it there — but the sampling only began
        once the screen already matched the play-screen detector, by which time
        the play screen had been drawn *over* the notice, leaving its text in
        row 19. The user, who has played the original, was right.

        `$7065` also settles D-081 from the code side: BASIC is banked out only
        **after** `sub_5049`, so `$5092 LDA $A65E,Y` really does read ROM — which
        is why the name comes out garbled, and it still does here.
        """
        # **[C-live] D-145** — the notice sits on the SELECTION screen's own
        # cleared field: `game_init_mode` fills `$0400-$06E8` with `$A0`
        # (solid) but never touches colour RAM, which `sub_screen_setup`
        # ($5FC3) left at 5 (GREEN) — so the whole field reads green with
        # black `$D021` ink, exactly like `_draw_selection`. Confirmed frame
        # by frame in the player's own recording: a full-green screen with
        # the message in black, black border. This used to fill black and
        # draw white text.
        paper, ink = c64.rgb(c64.GREEN), c64.rgb(c64.BLACK)
        self._surface.fill(paper)
        crew = None
        if flow.sim is not None:
            dead_id = flow.sim.state.opening_dead_crew_id
            crew = flow.sim.state.crew.get(dead_id) if dead_id else None
        # **The ROM's own geometry, and why the name is TRUNCATED here
        # (D-145).** `$5092` writes the 10-char name to `$06F9` (row 19,
        # col 1); `$50A0` then writes the 29-char message to `$0701`
        # (row 19, col 9) — a real screen-RAM write that **overwrites** the
        # name's last two cells. So only the first 8 name characters ever
        # survive on screen. `_blit_cells` skips spaces (it draws no paper),
        # so the message's own leading space could not erase them the way
        # the ROM's `STA` does; drawing all 10 left two garbled glyphs
        # sitting under "has", which is the "too much of the corrupt name
        # overlapping the words" the player reported.
        #
        # **The casing was still wrong (DISC-220).** `tools/vice-mcp/
        # opening_row19.json` — `" +??E?%,? HAS BEEN KILLED BY THE ALIEN"` — was
        # captured and decoded before DISC-215's case-bit fix, so its ALL-CAPS
        # reading is the pre-fix decoder's artifact, not the ROM's byte values.
        # A fresh live-oracle read of `$0701` decodes to `" has been killed by
        # the ALIEN"` — lowercase except the name, exactly like every other
        # panel string DISC-215 restored. The JSON capture's *garbled prefix* is
        # still trustworthy (it isn't case-sensitive noise); only its message
        # text is stale.
        visible = _OPENING_MSG_COL - _OPENING_NAME_COL      # 8
        codes = None
        if crew is not None and flow.sim is not None:
            roster = list(flow.sim.state.crew)
            if crew.id in roster:
                codes = opening_name.garbled_name_codes(roster.index(crew.id) + 1)
        if codes is not None:
            self._blit_codes(
                codes[:visible], _OPENING_NAME_COL, _OPENING_MSG_ROW, ink
            )
        elif crew is not None:
            self._blit_cells(
                crew.name[:visible],
                _OPENING_NAME_COL, _OPENING_MSG_ROW, ink,
                c64_font=True,
            )
        self._blit_cells(
            " has been killed by the ALIEN",
            _OPENING_MSG_COL,
            _OPENING_MSG_ROW,
            ink,
            c64_font=True,
        )
        self._present(_BORDER_COLOUR_FRONTEND)

