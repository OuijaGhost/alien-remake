"""Play-screen layout, decoded from the ROM — no pygame, no drawing.

Split out of :mod:`alien_remake.render.play` (DISC-240), which hard-imports
pygame at module level and had accumulated 294 ROM address citations — more
than most of ``core/``. What lives here is not a drawing decision: it is what
the ROM *says* about where things go and what colour they are, so it belongs
somewhere it can be read and tested without a display library.

**Colours are C64 palette indices, not RGB.** An index is what colour RAM
actually holds; converting to RGB is a rasterization step and happens at the
render boundary (see ``play.py``'s alias block). The index names come from
:mod:`.colours`, a sibling in this package — DISC-249 split them out of
``render.c64``, which had been holding the palette and the hardware colour
numbers under one name and made this module import *upwards* to reach them.

Everything below moved verbatim, citations included.
"""

from __future__ import annotations

from ..core import gamedata_snapshot as data
from ..core.menu import MenuCategory
from . import colours as c64

# CONTROL-panel band colour per menu category, read from live colour RAM
# (cols 30-39): MOVE_TO light blue, USE light green, SPECIAL light red,
# HEADER/QUIT grey. CREW/DECK reuse their order-menu counterparts - that screen
# moment is not in any capture. GET/LEAVE are the least certain entries here.
# Derivation: DISCOVERIES D-038.
#: `(first_row, last_row, colour)` per section of the CONTROL panel.
#:
#: **Fixed-height coloured blocks, not one row per entry** - the sections do not
#: resize to their contents, and every row 0-18 carries a colour. Paint fewer
#: and the bottom of the crew menu is black.
#:
#: **[C-live `narcissus_d800.bin` cols 30-39; $706F STA $D81E,Y]** 19 rows,
#: starting at screen row 0:
#:
#:     row  0      LT_GREY   the selected crew member's name
#:     rows 1-7    LT_BLUE   "move to:" + up to six destinations
#:     rows 8-10   LT_GREEN  " use:" + TWO item slots
#:     row  11     LT_RED    Get item / Leave item
#:     row  12     YELLOW    Leave item  (NOT a rule — DISC-244)
#:     rows 13-17  PURPLE    " Special:" + four option slots
#:     row  18     WHITE     quit — white paper, black ink
#:
#: The ROM's two fixed SPECIAL cells corroborate the bands: `$064E` is row 14
#: and `$0676` row 15, both inside the purple block.
#: Derivation: DISCOVERIES DISC-232, DISC-213, DISC-244.
PANEL_SECTIONS: tuple[tuple[int, int, int], ...] = (
    (0, 0, c64.LIGHT_GREY),
    (1, 7, c64.LIGHT_BLUE),
    (8, 10, c64.LIGHT_GREEN),
    (11, 11, c64.LIGHT_RED),
    (12, 12, c64.YELLOW),
    (13, 17, c64.PURPLE),
    (18, 18, c64.WHITE),
)
#: **[C $7000] DISC-235 — the CONTROL list colours its ten columns
#: differently from the crew-order panel.** Decoded from the ROM (19 rows,
#: `gamedata.CONTROL_PANEL_COLOUR_ADDR`) and confirmed cell-for-cell against a
#: live colour-RAM capture: LT_GREY 0, LT_BLUE 1-8, LT_GREEN 9, WHITE 10,
#: LT_RED 11-15, LT_GREY 16-18.
#:
#: `$7000` was dismissed once for "not matching the panel" — it was being
#: checked against a *crew* panel, which has its own layout (DISC-232). Two
#: screens, two tables.
CONTROL_SECTIONS: tuple[tuple[int, int, int], ...] = tuple(
    (row, row, colour)
    for row, colour in enumerate(data.CONTROL_PANEL_COLOURS)
)
#: The CONTROL list's own fixed slots, live-confirmed: "CONTROL" 0, "Order:" 1,
#: the seven crew 2-8, "indicate" 9, "location" 10, "display" 11, "level:" 12,
#: and the three decks 13-15.
#: **[C $7440] DISC-236** — the INDICATE screen's own bands, a third layout:
#: LT_GREY 0, LT_BLUE 1-17, LT_GREY 18. `draw_deck_map`'s `$7400` loop paints
#: rows 1-17 blue and `$7431` supplies row 18's grey restore colour.
INDICATE_SECTIONS: tuple[tuple[int, int, int], ...] = tuple(
    (row, row, colour)
    for row, colour in enumerate(data.INDICATE_PANEL_COLOURS)
)
CONTROL_SLOT_CREW_FIRST = 2
CONTROL_SLOT_DECK_FIRST = 13


#: The ROM writes each panel element to a **fixed screen cell**, not down a
#: list — which is what keeps every label on its own band's colour. Slots per
#: category, in the order `crew_entries` emits them.
PANEL_SLOT_NAME = 0
PANEL_SLOT_MOVE_HEADER = 1
PANEL_SLOT_MOVE_FIRST, PANEL_SLOT_MOVE_LAST = 2, 7
PANEL_SLOT_USE_HEADER = 8
PANEL_SLOT_USE_FIRST, PANEL_SLOT_USE_LAST = 9, 10
#: **[C $05D6 / $05FE] DISC-244 — Get and Leave are two rows, not one.**
#: `draw_item_row2 ($8387)` writes " Get item " to `$05D6` = row 11, and
#: `list_room_items ($83E0)` writes "Leave item" to `$05FE` = **row 12**. They
#: are independent: Get appears iff the room holds an object (`$836F CPX #$FF`)
#: with **no test of what the character is carrying**, and Leave appears iff the
#: character is carrying something (`$83DA CPX #$00`). Both at once is normal.
#:
#: The remake mapped both categories onto slot 11, so with an item in the room
#: *and* one in hand the two entries collided and Get came and went.
PANEL_SLOT_ITEM = 11
PANEL_SLOT_LEAVE = 12
PANEL_SLOT_SPECIAL_HEADER = 13
#: `$064E` = row 14 col 30 and `$0676` = row 15 col 30 are the first two.
PANEL_SLOT_SPECIAL_FIRST, PANEL_SLOT_SPECIAL_LAST = 14, 17
PANEL_SLOT_QUIT = 18

BAND_COLOUR = {
    MenuCategory.HEADER: c64.LIGHT_GREY,
    MenuCategory.CREW: c64.LIGHT_BLUE,
    MenuCategory.DECK: c64.LIGHT_GREEN,
    MenuCategory.INDICATE: c64.LIGHT_GREEN,
    MenuCategory.MOVE_TO: c64.LIGHT_BLUE,
    MenuCategory.USE: c64.LIGHT_GREEN,
    MenuCategory.GET: c64.LIGHT_RED,
    MenuCategory.LEAVE: c64.LIGHT_RED,
    MenuCategory.SPECIAL: c64.PURPLE,
    MenuCategory.QUIT: c64.WHITE,
}
# **[C paint_map_colors $7993]** The bottom seven rows are coloured in one pass,
# 40 columns wide (`CPY #$28`), and the bands are **two rows tall**::
#
#     $DAD0 <- $0F   row 18       light grey
#     $DAF8/$DB20 <- $0D   rows 19-20   light green
#     $DB48/$DB70 <- $08   rows 21-22   orange
#     $DB98/$DBC0 <- $07   rows 23-24   yellow
#
# The remake stacked one row per line of text from row 18 down, so the bottom of
# the screen was three thin stripes where the original has blocks.
BOTTOM_BANDS: tuple[tuple[int, int, int], ...] = (
    (18, 18, c64.LIGHT_GREY),
    (19, 20, c64.LIGHT_GREEN),
    (21, 22, c64.ORANGE),
    (23, 24, c64.YELLOW),
)
# `$79B7` fills `$06D0` (row 18, col 0) with `$A0` for **`$1E` = 30** cells, so
# the grey runs only to the edge of the view window; the CONTROL panel owns
# columns 30-39 of the same row.
C64_COLS = 40
GREY_BAR_ROW = 18
GREY_BAR_COLS = 30
# The 40x25 grid: the ship map occupies columns 0-29 and rows 0-16, the
# CONTROL panel columns 30-39, and the status lines the rows below
# (`docs/reference/*_0400.bin` + `colors.bin`).
PANEL_COL = 30
STATUS_ROW = 18
# **P5-8, D-133 — the scroll window; its row budget corrected by DISC-232.**
# INDICATE LOCATION's room list is 36 entries (34 rooms + header + QUIT), so it
# cannot fit unscrolled: `MenuController.move` already wraps the *cursor*
# correctly (`% len(selectable)`), but with no scroll window the wrapped-to
# entry near the bottom was drawn off the visible panel entirely — which is
# what "moving up does nothing" looks like from the player's seat. No
# windowing/paging scheme for that list has been decoded (there is no evidence
# it existed in the original at all, since the ROM's own per-room marker tables
# are indexed directly and never described as a scrollable menu); this keeps
# the highlighted row inside the panel's real budget.
#
# D-133 put that budget at "rows 1-17, 17 rows", from DISC-213's screenshot
# reading. The live colour-RAM capture says **rows 0-18, 19 rows** — the panel
# starts at screen row 0 (`$706F` fills colour RAM row 0 cols 30-39) and its
# `quit` row is 18, the same row the bottom status band starts on (the ROM
# paints row 18 grey for 30 cells and white for the panel's ten).
PANEL_VISIBLE_ROWS = STATUS_ROW + 1
# **[C $890C-$8917 / C-live] D-149 — "Jones is here".** `guard_6580 ($88CC)`,
# on the same path that arms the cat's run, copies the 22-byte string at
# `$884A` into **`$07C0` = row 24, col 0** before calling
# `maybe_clear_64ba` — so the run animation and this notice always arrive
# together, behind the identical four gates (`$88F9`-`$890A`, i.e.
# `jones_run_armed`). The string decodes to "Jones is here" padded with
# `$A0`; the live capture reads colour RAM 7 (YELLOW) across that row.
# `$88D2` blanks the same 22 cells at the top of every pass, so the notice
# shows exactly while the condition holds.
JONES_NOTICE_ROW = 24
JONES_NOTICE = "JONES IS HERE"
#: **[C $8844] D-158** — the *other* row-24 notice. `guard_6580`'s untaken
#: branch (`$8932`) scans the crew for anyone sharing Jones's room and, if it
#: finds one, writes their 10-char name from the roster table `$A65E` into
#: `$07C0` followed by this string at `$07CA`. So the cat is reported even
#: while you are looking at another deck — you just get told *who* can see him
#: instead of being offered the catch.
JONES_SEEN_SUFFIX = " SEES JONES "
JONES_NAME_WIDTH = 10            # [C $8951] `index_x10` -> 10 bytes per name
JONES_NOTICE_COLOUR = 7          # [C-live] colour RAM at row 24


#: **[C $8BC4 / $8D10] DISC-245 — the Alien's attack banner, on row 23.**
#: When `find_crew_with_alien ($8C49)` turns up a victim and that victim is the
#: character you are viewing (`$8CE1 CPY $64FB`), the ROM writes 16 bytes from
#: `$8BC4` to `$0798` = row 23 col 0, then the victim's 10-char name out of the
#: roster table `$A65E` to `$07A8` = row 23 col 16. So the line reads
#: "Alien attacking Dallas".
#:
#: It is cleared by the blanking loop at `$8CCC-$8CD6`, which fills `$0798` with
#: `$A0` for `#$27` cells the moment no victim is found.
#:
#: The same `$8CE1` gate governs the siren and the attack animation (D-096), so
#: all three appear and vanish together.
ATTACK_BANNER = "Alien attacking "
ATTACK_BANNER_ROW = 23
ATTACK_BANNER_NAME_COL = 16
