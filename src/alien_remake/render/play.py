"""The play screen: the deck map, the CONTROL panel, and the live overlays.

The last of the three-way split of `pygame_app.py` (D-191). Where
:mod:`.frontend` transcribes static screens, this module draws *state* — and
almost everything in it is a specific ROM behaviour rather than a presentation
choice:

- the INDICATE LOCATION marker is sprite 1 cycling `$BC`-`$B8` once per IRQ
  tick (`$4FCB`, R-37/D-082), not a flashing box;
- the attacking Alien is a 2x3 sprite grid, not one sprite (`$4E87`+`$4D58`,
  R-40/D-096);
- the heartbeat marker pulses through the ROM's own colour cycle
  (`$4ED4` -> `$D027`, R-19/D-045) on a constant 7-tick reload (D-061);
- Jones's run and the CONTROL panel's colour bands come from the real colour
  RAM captures.

The primitives it draws *with* — the text renderers, the sprite cache, the two
Narcissus screens — stay in :mod:`.pygame_app`, because the front end needs them
too. See :mod:`.protocol` for the shared attribute surface.
"""

from __future__ import annotations

from collections.abc import Sequence

import pygame  # the project's one optional runtime dependency (D-009)

from .. import media
from ..core import constants, ductmap
from ..core import gamedata_snapshot as data
from ..core.crew import CrewMember
from ..core.map import ShipMap
from ..core.menu import MenuCategory, MenuEntry
from ..core.nostromo import NARCISSUS
from ..core.state import GameState
from alientools.charset import Bitmap
from . import c64
from .deck_backdrop import DeckBackdrop
from .layout import (
    _C64_CELL, _CELL, _COLS, _FRAME_HZ, _HEIGHT, _JONES_X_END, _JONES_X_START,
    _JONES_X_STEP, _MAP_COLS, _PORTRAIT_SLOTS, _ROWS, _WIDTH,
)
from ..screens import panels
from .protocol import RendererState

# Glyph index used to tile a room cell when authentic tiles are loaded but no
# real per-deck backdrop capture is available (see deck_backdrop.py — this is
# the fallback path, for the SURFACE map only). The per-glyph meaning of
# ALIEN's custom charset was a `[?]`; **closed 2026-08-29 by the owner
# comparing the running remake with the disk: "the surface map looks
# correct."** That is the only evidence this one could ever have had - the
# glyph mapping is not written down anywhere in the image, so what settles it
# is somebody looking at both.
#
# **The duct view's own note here — "a separate question and still open" —
# was stale, closed 2026-09-05 (P9-B goal session).** `_draw_duct_map` does
# not use `_ROOM_GLYPH` at all: it paints from `data.DUCT_MAP_ROOM_TEMPLATE`,
# a real per-room decoded table (`select_menu_template $817D`, D-091), whose
# ten glyphs and colouring (`mark_exits $7F78`: your own node white, the runs
# leading away light blue, everything else invisible) were fully decoded from
# the disassembly alone — D-092 is explicit that this took **no live
# capture**, cross-checked four independent ways (all 34 room positions land
# on the node glyph; each sheet's node count matches its room-assignment
# table; etc). There was never a comparable open question for ducts the way
# there was for the surface fallback tile - this comment just never said so.
_ROOM_GLYPH = 0xA0
# The map field's real colour (colour RAM over the map columns = green, on the
# black screen background; docs/reference/colors.bin, DECODED via render/c64.py).
_BACKDROP_COLOR = c64.rgb(c64.GREEN)
# **Screen-layout data now lives in `alien_remake.screens.panels` (DISC-240)**
# — the decoded ROM tables were stranded behind this module's pygame import.
# This module keeps the drawing code. Aliased rather than re-spelled so the
# call sites below, and the tests that import these names from here, are
# unchanged. Read the citations in `screens/panels.py`.
_PANEL_SECTIONS = panels.PANEL_SECTIONS
_CONTROL_SECTIONS = panels.CONTROL_SECTIONS
_INDICATE_SECTIONS = panels.INDICATE_SECTIONS
_CONTROL_SLOT_CREW_FIRST = panels.CONTROL_SLOT_CREW_FIRST
_CONTROL_SLOT_DECK_FIRST = panels.CONTROL_SLOT_DECK_FIRST
_PANEL_SLOT_NAME = panels.PANEL_SLOT_NAME
_PANEL_SLOT_MOVE_HEADER = panels.PANEL_SLOT_MOVE_HEADER
_PANEL_SLOT_MOVE_FIRST = panels.PANEL_SLOT_MOVE_FIRST
_PANEL_SLOT_MOVE_LAST = panels.PANEL_SLOT_MOVE_LAST
_PANEL_SLOT_USE_HEADER = panels.PANEL_SLOT_USE_HEADER
_PANEL_SLOT_USE_FIRST = panels.PANEL_SLOT_USE_FIRST
_PANEL_SLOT_USE_LAST = panels.PANEL_SLOT_USE_LAST
_PANEL_SLOT_ITEM = panels.PANEL_SLOT_ITEM
_PANEL_SLOT_LEAVE = panels.PANEL_SLOT_LEAVE
_PANEL_SLOT_SPECIAL_HEADER = panels.PANEL_SLOT_SPECIAL_HEADER
_PANEL_SLOT_SPECIAL_FIRST = panels.PANEL_SLOT_SPECIAL_FIRST
_PANEL_SLOT_SPECIAL_LAST = panels.PANEL_SLOT_SPECIAL_LAST
_PANEL_SLOT_QUIT = panels.PANEL_SLOT_QUIT
_C64_COLS = panels.C64_COLS
_GREY_BAR_ROW = panels.GREY_BAR_ROW
_GREY_BAR_COLS = panels.GREY_BAR_COLS
_PANEL_COL = panels.PANEL_COL
_STATUS_ROW = panels.STATUS_ROW
_PANEL_VISIBLE_ROWS = panels.PANEL_VISIBLE_ROWS
_JONES_NOTICE_ROW = panels.JONES_NOTICE_ROW
_ATTACK_BANNER = panels.ATTACK_BANNER
_ATTACK_BANNER_ROW = panels.ATTACK_BANNER_ROW
_ATTACK_BANNER_NAME_COL = panels.ATTACK_BANNER_NAME_COL
_JONES_NOTICE = panels.JONES_NOTICE
_JONES_SEEN_SUFFIX = panels.JONES_SEEN_SUFFIX
_JONES_NAME_WIDTH = panels.JONES_NAME_WIDTH
_JONES_NOTICE_COLOUR = panels.JONES_NOTICE_COLOUR
# `screens/` stores C64 colour *indices* (what colour RAM holds); RGB is a
# rasterization step, so the conversion happens here at the render boundary.
_BOTTOM_BANDS: tuple[tuple[int, int, tuple[int, int, int]], ...] = tuple(
    (first, last, c64.rgb(index)) for first, last, index in panels.BOTTOM_BANDS
)
_BAND_COLOUR = {cat: c64.rgb(index) for cat, index in panels.BAND_COLOUR.items()}
# The standing-person sprite used as the current character's map-location
# marker (the little figure on the deck map; docs/reference/upper deck.png).
# **[C $4F33] confirmed 2026-07-24 (D-045):** `update_2 ($4F19)` writes
# `LDA #$B8 / STA $07F8` — sprite 0's pointer is `$B8`, and slot index =
# `$B8 - $A0` = 24. The pre-existing guess was exactly right.
#: A C64 hardware sprite, which is what a room marker is drawn as - and
#: therefore the size of the box you can hover to pick that room (M1/M2).
_MARKER_W, _MARKER_H = 24, 21

_CHAR_SPRITE = 24
# [C $4ED4/$4F38-$4F48]: the current character's marker **pulses** — the
# game's own heartbeat. `update_2` counts `$64C1` down 7->0 (reloading 7) and
# writes `$4ED4,Y` into sprite 0's colour register `$D027` each step. The
# table is a symmetric black->grey->white->grey ramp, i.e. a beat. This is the
# visual half of the "This is the sound of the heartbeat of the current
# character." cue (`$44BC`); the audio half is R-21 (no SID SFX yet).
_HEARTBEAT_COLOURS = (0x00, 0x0B, 0x0C, 0x0F, 0x01, 0x0F, 0x0C, 0x0B)
# **P2-10 CORRECTION (2026-08-02): the marker's pulse rate is a CONSTANT.**
# This used to derive the period from `constants.heartbeat_divider(fear)`, on
# the reasoning that D-061 had shown the beat races with composure. That
# conflated two different things. `fear_alert ($4E16)`'s `$4D02` divider paces
# **voice 1's sound**; the on-screen colour cycle is paced by `update_2`, which
# reloads a fixed **7** (`$4F38 DEC $64C1 / BPL / $4F3D LDA #$07`) with no
# reference to composure at all. The composure-dependent marker was therefore an
# invention and is removed — the player's report ("transitions from white to
# black in rhythmic fashion") describes exactly this steady cycle.
_HEARTBEAT_PERIOD_TICKS = 7          # [C $4F3D] LDA #$07 -> $64C1
_SPRITE_SLOT_BASE = 0xA0
# **[C $4FDB] P4-3 — `$B8` is the WRAP SENTINEL and is never displayed.**
# `update_4 ($4FCB)` is `DEC $657A / LDA $657A / CMP #$B8 / BNE + / LDA #$BC /
# STA $657A` and only *then* `STA $07F9`. So the moment the counter reaches
# `$B8` it is reset to `$BC` **before the store** — the cycle actually shown is
# four frames, `$BC $BB $BA $B9`.
#
# D-082 read the wrap as "the animation resolves into the very glyph used for a
# character's position marker" and included `$B8`. That is the single frame of
# the crew icon the player sees flashing inside the INDICATE animation.
_POINTER_FRAMES = tuple(
    slot - _SPRITE_SLOT_BASE for slot in (0xBC, 0xBB, 0xBA, 0xB9)
)
# Slows the IRQ-rate cycle to the renderer's frame clock, the same way
# `_HEARTBEAT_PERIOD_TICKS` divides `_frame_count` for the heartbeat.
_POINTER_RATE = 4
# --- the Alien attack composite (D-096) --------------------------------
# **[C $4E87 + $4D58]** The attacking Alien is not one sprite but a **2x3 grid
# of six X/Y-expanded sprites**, assembled by a raster multiplexer.
#
# `sub_4e87 ($4E87)`, run at play-screen setup ($7046), fixes the geometry:
# `$D01D = $F0` and `$D017 = $F0` expand sprites 4-7 in both axes (so each
# covers 48x42 px), `$D008`/`$D00C` put the left column at X=$5A and
# `$D00A`/`$D00E` the right at X=$8A, `$D00D`/`$D00F` put sprites 6/7 at Y=$61,
# `$D010 = 0` (no X MSB), and `$D02B`-`$D02E` colour all four **green** ($05).
#
# `irq_raster_split ($4D58)` then shows sprites 4 and 5 **twice per frame**,
# toggling on `$64B9`: once at Y=$37 with pointers from `$4D04`/`$4D05`, and
# again at Y=$8B with `$4D06`/`$4D07`. Six images, two sprites.
#
# The spacing is the proof: 48 px apart horizontally and 42 px vertically is
# exactly one expanded sprite, so the six tiles abut edge to edge — and
# rendering them does produce a single coherent Alien.
_ATTACK_X = (0x5A, 0x8A)
_ATTACK_Y = (0x37, 0x61, 0x8B)
_ATTACK_COLOUR = 0x05                    # $D02B-$D02E
_ATTACK_EXPAND = 2                       # $D017 / $D01D = $F0
#: Pointer for each cell, as an offset from the animation frame. `update_1
#: ($4EE8)` walks `ADC #$04` five times from `$A0 + f`; `begin_active_play
#: ($4F95)` writes the sixth, `$B4`, as a **static** slot that does not animate.
_ATTACK_SLOTS: tuple[tuple[int | None, ...], ...] = (
    (0xA0, 0xA4),   # Y = $37, from $4D04 / $4D05
    (0xA8, 0xAC),   # Y = $61, sprites 6/7 direct ($07FE / $07FF)
    (0xB0, None),   # Y = $8B, from $4D06 / $4D07 — $B4 is fixed
)
_ATTACK_STATIC_SLOT = 0xB4
#: `tbl_alien_anim ($4EDC)` — a 12-step ping-pong over 4 frames, indexed by
#: `$64BF` counting 11 -> 0 and reloading (`$4EEE`-`$4EFB`).
_ATTACK_FRAMES: tuple[int, ...] = (0, 1, 1, 2, 2, 3, 3, 2, 2, 1, 1, 0)
# --- Jones's run (D-089) ----------------------------------------------
# **[C $4F7A]** Sprite 3 is a five-frame running cat. The ROM's loop is
#     INC $64C0 / LDA $64C0 / CMP #$C9 / BNE + / LDA #$C4 / STA $64C0
#     + LDA $64C0 / STA $07FB          ; sprite 3's pointer
# so the pointer cycles $C4 -> $C8 and wraps. Rendering those five slots out of
# `out/charset.bin` shows a quadruped with a long tail, legs cycling; $C9 —
# which the `CMP #$C9` deliberately excludes — is a different shape, so the
# five-frame run is the animation, not a slice of a larger strip.
_JONES_FRAMES = tuple(slot - _SPRITE_SLOT_BASE for slot in range(0xC4, 0xC9))
_JONES_Y = 0x92
# VIC sprite coordinates are relative to the display field's origin.
_SPRITE_ORIGIN = (24, 50)
# **P2-8, corrected 2026-08-02.** `update_3 ($4F52)` steps the pointer and
# advances X by 4 **once per IRQ tick** — the measured 60 Hz jiffy divided by
# the 9-jiffy animation divider, i.e. `constants.ANIM_HZ` ~= 6.7 Hz. Driving it
# off the renderer's frame counter at 2 frames/step ran it at ~30 Hz, roughly
# **4.5x too fast**, which is what the player saw. Scaled to the real rate.
_JONES_RATE = max(1, round(_FRAME_HZ / constants.ANIM_HZ))
#: **[C $4F57]** `update_3` writes `LDA #$08 / STA $D02A` — sprite 3 is
#: **orange**, not white. The player remembered it as red, which is what
#: C64 orange looks like on a composite CRT next to the black backdrop; the ROM
#: byte wins, and it is at least emphatically not the white we were drawing.
_JONES_COLOUR = 0x08
def jones_run_armed(
    jones_room_id: str | None,
    jones_caught: bool,
    selected_crew: CrewMember | None,
) -> bool:
    """Would `guard_6580 ($88CC)` start Jones running? (D-089)

    Four consecutive ROM tests have to pass before `$8919 JSR
    maybe_clear_64ba` arms the sprite, and the player's recollection — "the
    Jones animation only plays when a crew member is selected and Jones is in
    the same room" — is the observable shape of the first three:

    * `$88F9 CMP $64F7` — Jones's room (`$657D`) is the **displayed** room.
    * `$8901 LDY $64FB / BEQ $8932` — **a character is selected** at all.
    * `$8903 CPY #$08 / BCS $8932` — that selection is a crew member (slot < 8),
      not Jones himself (slot 8).
    * `$8907 LDA $6501,Y / BNE $8932` — and that crew member is **on the
      surface**, not inside a duct. This last one is not in the player's
      description but is in the code, so it is modelled.

    The remake's displayed room is the selected crew member's room, which
    collapses the first test into "Jones is in the room you are looking at".
    """
    if jones_caught or jones_room_id is None or selected_crew is None:
        return False
    if not selected_crew.alive or selected_crew.in_duct:
        return False
    return selected_crew.room_id == jones_room_id
def jones_notice_text(
    state: GameState, selected_crew: CrewMember | None
) -> str | None:
    """Row 24's cat notice — **[C $88CC `guard_6580`] D-158**, both branches.

    The ROM blanks the row every pass (`$88D2` fills 22 spaces) and then
    re-derives it, so this is a pure function of the current state rather than
    anything latched at click time. There are two outcomes, not one::

        88F4  LDA $657D / CMP $64F7 / BNE $8932  ; Jones in the DISPLAYED room?
        88FE  LDY $64FB / BEQ $8932              ;   ...and a character selected
        8903  CPY #$08  / BCS $8932              ;   ...that is a crew slot
        8907  LDA $6501,Y / BNE $8932            ;   ...on the surface
        890C  -> "JONES IS HERE" ($884A) + the GET JONES option ($8860)

        8932  LDY #$01                           ; otherwise scan the crew:
        8934  LDA $7935,Y / CMP $657D / BEQ ...  ;   anyone in JONES's room
        8944  LDA $6501,Y / BNE next             ;   who is on the surface
        8949  LDA $7D45,Y / CMP #$02 / BCC next  ;   and not collapsed
        8950  -> "<NAME>" ($A65E + Y*10) + " SEES JONES " ($8844)

    The remake only ever drew the first, so the cat vanished from the display
    entirely whenever you were watching a different room — even with a crew
    member standing right next to him.
    """
    if state.jones_caught or state.jones_room_id is None:
        return None
    if jones_run_armed(state.jones_room_id, state.jones_caught, selected_crew):
        return _JONES_NOTICE                                       # $890C
    for crew in state.crew.values():                               # $8932
        if crew.room_id != state.jones_room_id:                    # $8934
            continue
        if crew.in_duct:                                           # $8944
            continue
        if crew.health < constants.CREW_INCAPACITATED_BELOW:       # $8949
            continue
        return crew.name.upper().ljust(_JONES_NAME_WIDTH) + _JONES_SEEN_SUFFIX
    return None
# **[C $6667] R-10 (D-053): the current-character portrait indicator.**
# `place_selected_char_sprite ($6667)` (formerly mislabelled
# `place_alien_sprite`, D-041) puts **sprite 2** at the fixed VIC position
# `($1C, $A9)` -> screen `(4, 119)`, with pointer `$64FB + $BC` — i.e. the
# *selected crew member's own portrait* (crew 1 -> `$BD` = slot 29 = Dallas,
# matching `_PORTRAIT_SLOTS`) — and sets its colour register `$D029` from
# that character's **duct flag** `$6501,Y`: 0 while in a room, 1 while
# crawling the ducts. So the play screen carries a portrait of whoever you
# are commanding, which changes colour when they are in the vents.
_CHAR_PORTRAIT_AT = (4, 119)      # unscaled screen px, sprite top-left
_CHAR_PORTRAIT_ROOM_COLOUR = c64.BLACK   # `$6501,Y == 0` -> colour 0
_CHAR_PORTRAIT_DUCT_COLOUR = c64.WHITE   # `$6501,Y == 1` -> colour 1
# **[C $758D/$75B1] R-08 (D-058): the game's own per-room marker positions.**
# `$76D7` positions **sprite 1** — the deck-plan key's "Location Ptr" — by
# indexing two 36-entry tables with the character's own room
# (`$64F7`, loaded from `$7935,Y` at `$778E`):
#     `LDA $758D,Y / STA $D002`   (sprite 1 X)
#     `LDA $75B1,Y / STA $D003`   (sprite 1 Y)
# Decoded and converted to screen pixels (`VIC_X - 24`, `VIC_Y - 50`), which
# lines up with the map drawn at the field origin. **32 of the 34 mapped
# rooms get a unique position**; the two exceptions (CORRIDOR 6 / CRYO VAULT
# and ENGINEERNG / INFIRMARY each share a spot on their deck) are left as
# decoded rather than "corrected" — they are what the ROM contains.
# This replaces the BFS-computed internal grid the markers used to be scaled
# onto, which was never more than an approximation (DECISIONS D-010 #2).
_ROOM_MARKER_X: tuple[int, ...] = (112, 112, 152, 112, 112, 112, 16, 160, 56, 92, 136, 152, 136, 128, 152, 128, 72, 200, 200, 200, 72, 72, 120, 72, 120, 188, 64, 104, 64, 152, 160, 160, 64, 68, 80)
_ROOM_MARKER_Y: tuple[int, ...] = (24, 96, -4, 16, 72, 102, 60, 56, 64, 56, 24, 56, 96, 64, 64, 64, 96, 16, 72, 104, 120, 24, 4, 96, 124, 72, 48, 64, 88, 124, 24, 100, 72, 20, 40)


#: **[C $7A10] The status template, one 40-column line.**
#:
#:     col: 0123456789012345678901234567890123456789
#:          : damage 00% is .........,morale:.......
#:
#: `:` at 0, `damage` 2-7, the percentage 9-11, `is` 13-14, a **9-wide** status
#: field at 16-24, `,` at 25, `morale:` 26-32 and a **7-wide** word at 33-39.
#:
#: The game splits it across two rows, each prefixed with a 10-column name:
#: the room row gets template columns 0-11 written at screen column 10
#: ("Narcissus : damage 00%"), the crew row gets columns 12-39 in place
#: ("Kane        is O.K.      ,morale:confident").
#:
#: The remake used free-form spacing, so nothing lined up with the original.
#:
#: **[C draw_control_panel_body $79CD]** Where each piece of the template lands.
#: `copy10_ptr` puts a 10-column *name* at column 0 of rows 19 and 21; the
#: template's two halves both start at **column 10**.
_ROOM_ROW, _CREW_ROW, _ALSO_ROW = 19, 21, 22
_NAME_W = 10
_TEMPLATE_COL = 10
#: Fields inside the crew row, in *screen* columns (template index - 12 + 10).
_DAMAGE_COL = 19            # template 9-10, then `%` at 11
_STATUS_COL, _STATUS_W = 14, 9
_MORALE_COL, _MORALE_W = 31, 9
#: `$7E82` writes "also here:" (`$7EDB`) to `$0770` = row 22 col 0, then each
#: co-occupant's name to `$077B`/`$0786`/`$078E`. The last two overlap by two
#: columns, which only shows with a fourth body in the room — `ROOM_CAPACITY`
#: is 3, so the third slot is a fallback the game rarely reaches.
_ALSO_NAME_COLS = (11, 22, 30)


def _place(cells: list[str], col: int, text: str) -> None:
    for i, ch in enumerate(text):
        if 0 <= col + i < len(cells):
            cells[col + i] = ch


def co_occupants(state: GameState, crew: CrewMember) -> list[str]:
    """Who the ROM lists under "also here:" for ``crew``.

    **[C $7E68-$7E79]** Three tests per crew member, and the remake was missing
    the third::

        $7E69  LDA $7935,Y / CMP $7947   same room as the selected one?
        $7E71  CPY $64FB                 not the selected one themselves?
        $7E76  LDA $6501,Y / BNE $7ED2   **not in a duct**

    `$6501,Y` is the in-duct flag — the same cell that recolours the play
    screen's portrait (D-053). Someone crawling the vents still carries the
    room's id, so without that third test they were listed as standing next to
    you. The ducts are a separate space (DISC-244).

    The ROM filters the *listed* crew only, never the viewer: a duct-crawler is
    still shown the room's occupants, because `$6501,Y` indexes the candidate,
    not `$64FB`. That asymmetry is the ROM's and is left as found.
    """
    return [
        c.name for c in state.crew.values()
        if c.alive
        and c.room_id == crew.room_id
        and c.id != crew.id
        and not c.in_duct
    ]


def bottom_panel_rows(
    room_name: str,
    damage_pct: int,
    crew_name: str,
    status: str,
    morale: str,
    also_here: Sequence[str] = (),
) -> list[str]:
    """Rows 18-24 of the play screen, laid out at the ROM's own columns.

    **[C draw_control_panel_body $79CD]** The status area is a single **42-byte**
    template at `$7A10` — not a 40-column line — copied out in two pieces::

        $7A10 +$0C -> $0702   row 19 col 10   ": damage 00%"
        $7A1C +$1E -> $0752   row 21 col 10   " is <9>,morale:<9>"
        $070E fill $AE x $3A  row 19 col 22 through row 20
        $0770 fill $A0 x $28  row 22

    Both fields are **9 wide**, which is exactly "collapsed" and exactly
    "confident" — the longest word each can hold. Reading the template as 40
    columns made both look too narrow and pushed the morale word off the row.

    The `$AE` fill decodes as `.` but **renders blank** (D-078/P-7): this font
    has no period glyph, so those runs draw as solid band, not dots.
    """
    rows = [[" "] * _C64_COLS for _ in range(7)]

    def put(row: int, col: int, text: str) -> None:
        _place(rows[row - _GREY_BAR_ROW], col, text)

    put(_ROOM_ROW, 0, room_name[:_NAME_W])
    put(_ROOM_ROW, _TEMPLATE_COL, ":")
    put(_ROOM_ROW, _TEMPLATE_COL + 2, "damage")
    put(_ROOM_ROW, _DAMAGE_COL, f"{min(99, damage_pct):02d}%")

    put(_CREW_ROW, 0, crew_name[:_NAME_W])
    put(_CREW_ROW, _TEMPLATE_COL + 1, "is")
    put(_CREW_ROW, _STATUS_COL, status[:_STATUS_W])
    put(_CREW_ROW, _STATUS_COL + _STATUS_W, ",morale:")
    put(_CREW_ROW, _MORALE_COL, morale[:_MORALE_W])

    if also_here:
        put(_ALSO_ROW, 0, "also here:")                       # $7EDB
        for name, col in zip(also_here, _ALSO_NAME_COLS):
            put(_ALSO_ROW, col, name[:_NAME_W])

    return ["".join(r) for r in rows]



class PlayMixin(RendererState):
    """`PygameRenderer`'s play-screen drawing."""

    def _selected_crew(self, state: GameState) -> CrewMember | None:
        """The crew member `$64FB` points at, or None if nothing is selected."""
        crew_id = self._menu.selected_crew if self._menu is not None else None
        return state.crew.get(crew_id) if crew_id is not None else None
    # --- tiles --------------------------------------------------------------
    def _glyph_surface(self, bitmap: Bitmap, colour: tuple[int, int, int]) -> pygame.Surface:
        """Rasterize a 0/1 tile bitmap into a scaled pygame Surface (fg on clear)."""
        w, h = len(bitmap[0]), len(bitmap)
        surf = pygame.Surface((w, h))
        surf.set_colorkey((0, 0, 0))
        surf.fill((0, 0, 0))
        for y, row in enumerate(bitmap):
            for x, on in enumerate(row):
                if on:
                    surf.set_at((x, y), colour)
        target = (_CELL - 6)
        return pygame.transform.scale(surf, (target, target))
    def _room_tile(self) -> pygame.Surface | None:
        """The cached, scaled Surface for a room cell, or None without tiles."""
        if self._tiles is None:
            return None
        if _ROOM_GLYPH not in self._tile_cache:
            self._tile_cache[_ROOM_GLYPH] = self._glyph_surface(
                self._tiles.glyph(_ROOM_GLYPH), (0, 160, 0)
            )
        return self._tile_cache[_ROOM_GLYPH]
    def _room_marker_px(self, room_id: str) -> tuple[int, int] | None:
        """The ROM's own screen position for ``room_id``'s map marker.

        Returns unscaled (x, y) from `$758D`/`$75B1`, or ``None`` for a room
        that isn't in the real 36-entry table (synthetic test maps), so the
        caller can fall back to the internal grid.
        """
        from ..core.gamedata_snapshot import ROOM_SLUGS

        try:
            idx = ROOM_SLUGS.index(room_id)
        except ValueError:
            return None
        if idx >= len(_ROOM_MARKER_X):
            return None
        return (_ROOM_MARKER_X[idx], _ROOM_MARKER_Y[idx])
    def _supplied_deck_art(self, deck: int) -> pygame.Surface | None:
        """One deck's plan as an image the player supplied, or ``None``. **D3.**

        Scaled to :data:`~alien_remake.media.MAP_SIZE`. The CONTROL panel starts
        at column 30 and the status rows below the map are drawn live every
        frame, so an image left at its own size would be painting over screen
        furniture rather than over the map — and both of those positions are
        decoded, not chosen.

        Cached including the misses, and separately from `_backdrop_cache`
        because that one holds the *result* and this holds the source: a deck
        with no supplied art must not pay a filesystem search per frame.

        Best-effort. A bad PNG falls through to the game's own plan rather than
        leaving the map blank, which is the failure a player would read as the
        game being broken rather than their file being.
        """
        if deck in self._deck_art_cache:
            return self._deck_art_cache[deck]
        surface: pygame.Surface | None = None
        path = media.map_path(deck)
        if path is not None:
            try:
                loaded = pygame.image.load(str(path)).convert_alpha()
                surface = pygame.transform.smoothscale(loaded, media.MAP_SIZE)
            except Exception:      # pragma: no cover - depends on the file
                surface = None
        self._deck_art_cache[deck] = surface
        return surface

    def _rasterize_backdrop(self, backdrop: DeckBackdrop) -> pygame.Surface:
        """Draw a deck's captured ship-map columns at native (unscaled) resolution."""
        assert self._tiles is not None
        gw, gh = self._tiles.glyph_size
        cols = min(_MAP_COLS, len(backdrop.codes[0]))
        rows = len(backdrop.codes)
        surf = pygame.Surface((cols * gw, rows * gh))
        surf.fill((0, 0, 0))
        for row, code_row in enumerate(backdrop.codes):
            for col, code in enumerate(code_row[:cols]):
                bmp = self._tiles.glyph(code)
                for y, line in enumerate(bmp):
                    for x, on in enumerate(line):
                        if on:
                            surf.set_at((col * gw + x, row * gh + y), _BACKDROP_COLOR)
        return surf
    def _rasterize_codes(
        self, codes: tuple[tuple[int, ...], ...]
    ) -> pygame.Surface:
        """Draw a grid of screen codes with the game's own charset, unscaled."""
        assert self._tiles is not None
        gw, gh = self._tiles.glyph_size
        cols = min(_MAP_COLS, len(codes[0]))
        surf = pygame.Surface((cols * gw, len(codes) * gh))
        surf.fill((0, 0, 0))
        for row, code_row in enumerate(codes):
            for col, code in enumerate(code_row[:cols]):
                for y, line in enumerate(self._tiles.glyph(code)):
                    for x, on in enumerate(line):
                        if on:
                            surf.set_at((col * gw + x, row * gh + y), _BACKDROP_COLOR)
        return surf

    def _backdrop_surface(self, deck: int) -> pygame.Surface | None:
        """The real captured map art for ``deck``, at native pixel scale (undistorted).

        Returns None if there's no tileset or no capture for this deck — the
        caller falls back to the placeholder grid (see ``deck_backdrop.py``).
        """
        # **D3 — your own deck plan, if you supplied one.** Answered before the
        # tileset is even consulted: rasterizing the game's own plan needs the
        # charset to draw the screen codes with, but an image does not, so a
        # player who has map art and no extracted disk still gets a map.
        supplied = self._supplied_deck_art(deck)
        if supplied is not None:
            if deck not in self._backdrop_cache:
                self._backdrop_cache[deck] = supplied
            return self._backdrop_cache[deck]
        if self._tiles is None:
            return None
        # **[C $7132/$7112/$7122] Decoded from the ROM, not captured.**
        # `init_menu_ptr` and its siblings copy one of three uncompressed 30x18
        # screens at `$A000`/`$A21C`/`$A438` straight into `$0400`. Those decode
        # to "UPPER DECK", "MIDDLE DECK" and "LOWER DECK", so the map art comes
        # out of the program itself.
        #
        # This used to read `docs/reference/{upper,middle,lower}deck_0400.bin` —
        # VICE screen captures — which was the project's last dependency on a
        # capture for game *content* rather than for verification. The captures
        # remain the fallback if the snapshot is somehow unavailable.
        codes = data.DECK_PLANS[deck] if deck < len(data.DECK_PLANS) else None
        if codes is None and deck not in self._backdrops:
            return None
        if deck not in self._backdrop_cache:
            raw = (
                self._rasterize_codes(codes)
                if codes is not None
                else self._rasterize_backdrop(self._backdrops[deck])
            )
            target = (raw.get_width(), raw.get_height())
            self._backdrop_cache[deck] = pygame.transform.scale(raw, target)
        return self._backdrop_cache[deck]
    # --- rendering ----------------------------------------------------------
    def render(self, state: GameState, *, present: bool = True) -> None:
        """Draw the play screen: coloured deck map, CONTROL panel, status line.

        ``present=False`` leaves the finished frame on ``_surface`` without
        flipping, so a caller can overlay on top of it — the OPENING notice does
        this, because on the real machine it is the play screen with a message,
        not a screen of its own.
        """
        self._last_state = state
        # **[C $4CC9-$4CE2] The deck plan DOES follow the selected character.**
        # Every pass::
        #
        #     4CC9  LDY $64FB / BEQ          ; someone is selected
        #     4CCE  LDA $7935,Y / STA $64F7  ; ...their room, right now
        #     4CD4  LDA $6501,Y / BEQ $4CE2  ; in a duct?
        #     4CD9  JSR select_menu_template ;   yes -> that deck's duct sheet
        #     4CE2  JSR menu_option_dispatch ;   no  -> the deck plan
        #
        # and `menu_option_dispatch ($511C)` does `LDA $7569,Y` then
        # `init_menu_ptr`/`menu2`/`menu3`, each of which **copies 30x18 bytes of
        # a deck plan into `$0400`** from `$A000`/`$A21C`/`$A438` — the screens
        # that decode to "UPPER DECK", "MIDDLE DECK", "LOWER DECK".
        #
        # D-131 concluded otherwise and was wrong: it read `$511C` as only
        # positioning sprite 0 and stopped before the `init_menu_ptr` calls. The
        # manual line it leaned on ("EACH DECK OF THE SHIP CAN BE SELECTED FROM
        # THE MENU") describes the menu, not the only way the view changes.
        #
        # **W1 — and the follow stays exactly as decoded except for one thing.**
        # The wheel changes floor, and this ran every frame, so a scroll was
        # undone before it could be drawn. Suppressing the follow generally
        # would have broken the ROM's own behaviour; suppressing it only for a
        # *deliberate wheel* does not. Every other path — selecting someone,
        # the panel's deck rows, the sim moving them — still snaps the view to
        # the selected character, and the override is dropped the moment they
        # actually move, so a walking crew member takes the view back. The ROM
        # has no wheel, so the exception applies only where there was nothing
        # to contradict.
        if self._menu is not None and self._menu.selected_crew is not None:
            followed = state.crew.get(self._menu.selected_crew)
            if followed is not None and followed.alive and followed.room_id:
                room = self._ship.rooms.get(followed.room_id) if self._ship else None
                if room is not None:
                    # Keyed on the *room*, not the deck: a scroll should be
                    # a look, and the next time the character moves at all
                    # the view is theirs again. Keyed on the deck, the map
                    # stayed on the wrong floor until they changed floor.
                    where = (self._menu.selected_crew, followed.room_id)
                    if where != self._followed_where:
                        self._followed_where = where
                        self._deck_override = False
                    if not self._deck_override and room.deck != state.deck:
                        state.deck = room.deck
        elif self._menu is not None:
            self._followed_where = None
        self._view_deck = state.deck  # the CONTROL panel's deck selection
        # **NOT the ROM's own rule — a deliberate departure, both presets
        # (owner's request, 2026-09-06; see DECISIONS.md).** `$8CE1 CPY
        # $64FB` only ever draws the composite once, for whichever single
        # crew member happened to be selected the instant an encounter
        # *began*, and drops it again on the next movement blip regardless of
        # whether the Alien is still there. A player who was looking at
        # someone else when that one check ran, or who switched to the
        # victim afterwards, never saw it at all — reported directly: two
        # crew members were attacked and the ship breached without the
        # Alien ever appearing on screen.
        #
        # The replacement is a plain, continuously-recomputed fact instead of
        # a one-shot latch: **whoever is currently selected shares a room
        # with a living, surfaced Alien.** Recomputed fresh every frame from
        # `state.alien`/`state.crew`, not from a sound cue, so it starts the
        # moment you look at (or walk into) the right room, updates the
        # instant you switch to a different crew member in that same room
        # (no need to re-trigger anything), and drops the moment either one
        # leaves — never a stale latch to get stuck on.
        alien = state.alien
        selected_crew = self._selected_crew(state)
        co_located = (
            alien is not None and alien.alive and not alien.in_duct
            and selected_crew is not None and selected_crew.alive
            and not selected_crew.in_duct
            and selected_crew.room_id == alien.room_id
        )
        if co_located:
            assert selected_crew is not None       # narrows for mypy
            if not self._attacking or self._attacking_crew_id != selected_crew.id:
                self._start_attack_composite(selected_crew.id)
        elif self._attacking:
            self._stop_attack_composite()
        self._surface.fill(c64.rgb(c64.BLACK))
        # **[C $8D1A] P3-4 — the attack BLANKS the map first.**
        # `begin_active_seq` calls `clear_map_colors ($7EE5)` — which fills the
        # whole 30x18 colour area with 0 — *before* `begin_active_play`. Black
        # ink on a black background makes the deck plan vanish, and only then
        # is the Alien composite drawn. We used to paint the creature straight
        # over a still-visible map, which is what the player reported.
        if not self._attacking:
            # **[C $5134-$513B/$4F25] D-144 — the NARCISSUS cockpit.**
            # `menu_option_dispatch` builds the map view from the selected
            # character's own room (`$7569,Y`, the per-room deck byte); rooms
            # 0-33 give 0/1/2 (upper/middle/lower) and load one of the three
            # deck templates, but NARCISSUS (34) has no entry in that table at
            # all — reading past its end lands on `$03`, which the ROM's own
            # `CMP #$02 / BEQ` chain treats as "none of the above" and calls
            # `setup_cursor_sprite` instead of any deck-template loader.
            # `update_2` ($4F25 `CMP #$22`) independently confirms room 34 is
            # special-cased: it skips the character-marker heartbeat update
            # for it. Live-captured and code-confirmed: no deck plan is drawn
            # for NARCISSUS at all — the player sees the shuttle's cockpit.
            selected_id = (
                self._menu.selected_crew if self._menu is not None else None
            )
            selected_crew = state.crew.get(selected_id) if selected_id else None
            if selected_crew is not None and selected_crew.room_id == NARCISSUS:
                self._draw_narcissus_cockpit()
            else:
                self._draw_deck(state)
            # Sprite 2, drawn on BOTH paths: the VIC does not care which
            # background is underneath it ($6667, DISC-245).
            self._draw_char_portrait(state)
        # The composite sits on sprites 4-7, which the VIC draws over the
        # character screen — so it goes on after the map either way (D-096).
        self._draw_attack_animation()
        self._draw_menu_panel(state)
        self._draw_status_line(state)
        self._draw_grille_caption(state)  # [C $8710] row 19, col 25
        self._draw_debug_markers(state)  # Ctrl+3; NOT the original
        self._draw_attack_banner(state)  # $8BC4, row 23
        self._draw_notice_line(state)   # $55C9, row 24
        self._draw_jones_notice(state)    # D-149
        self._update_heartbeat(state)     # D-145
        self._update_tracker_ping(state)  # D-150
        self._draw_debug_overlay(state)   # Ctrl+3; NOT the original
        if present:
            self._present(self._play_border(state))

    @staticmethod
    def _ink(state: GameState) -> tuple[int, int, int]:
        """`$D021` — the colour every cut-out glyph shows through (D-050).

        Normally black (`$7027`), but the android reveal writes its own slot
        number here (`$52DA`), so the whole screen's lettering changes colour
        at once. DISC-231: that is the ROM's only visual tell, and the remake
        had none.
        """
        return c64.rgb(state.background_colour)

    @staticmethod
    def _play_border(state: GameState) -> tuple[int, int, int]:
        """The play screen's border — **blue, flashing yellow while scuttling.**

        `mainloop_sub_5a26 ($5A26)` runs once per main-loop pass and, whenever
        the auto-destruct flag `$64CF` is set, toggles the bottom bit of the
        border colour before ticking the countdown::

            5A26  LDA $64CF / BNE $5A2C   ; armed?
            5A2B  RTS                     ; no  -> leave the border alone
            5A2C  LDA $D020
            5A2F  EOR #$01                ; yes -> toggle bit 0
            5A31  STA $D020
            5A34  DEC $657C               ; ...then the countdown

        `start_game` sets the border to **`#$06` BLUE** (`$7054`), so `EOR #$01`
        swaps it to **`$07` YELLOW** — the flash the player sees. It stops when
        the ship goes up, or when OVERRIDE DETONATION calls `clear_result_flag
        ($58F6)`, which zeroes `$64CF` *and* explicitly restores `#$06`
        (`$58FE-$5900`) rather than leaving it on whichever half of the toggle
        it happened to be.

        One toggle per **pass**, not per frame: the remake draws at 30fps and
        ticks at ~7.9Hz, so this keys off `state.tick`.
        """
        # **[C $5626-$5628] DISC-231** — `delay` blacks the border for the whole
        # of its blocking pause and every caller restores `#$06` afterwards, so
        # a transient banner shows against a black border. Checked first: the
        # ROM is *inside* `delay` here, so nothing else is toggling it.
        if state.notice:
            return c64.rgb(constants.NOTICE_BORDER)
        if state.auto_destruct_ticks is None:
            return c64.rgb(c64.BLUE)                    # $7054 LDA #$06
        return c64.rgb(c64.YELLOW if state.tick % 2 else c64.BLUE)
    @staticmethod
    def _panel_rows(entries: "list[MenuEntry]") -> list[int | None]:
        """Which panel row each entry occupies — **[C-live] DISC-232.**

        The ROM writes each element of the crew-order panel to a **fixed
        screen cell** (`$064E` and `$0676` are two of them), not down a
        running list, which is what keeps every label on its own colour band.
        Drawing them sequentially instead put "use:" on the blue block,
        "Special:" on the red one and so on — the owner's "some words on the
        wrong colour background" — and ran the tail off the painted area.

        Returns a row per entry, or ``None`` for one that overflows its slot
        band (the ROM simply has nowhere to put it either). A panel with no
        crew selected — the CONTROL list, the INDICATE room list — has no such
        fixed map, so those fall back to sequential rows.
        """
        rows: list[int | None] = []
        # The three multi-slot bands, each consumed in order.
        nxt = {
            MenuCategory.MOVE_TO: _PANEL_SLOT_MOVE_FIRST,
            MenuCategory.USE: _PANEL_SLOT_USE_FIRST,
            MenuCategory.SPECIAL: _PANEL_SLOT_SPECIAL_FIRST,
        }
        last = {
            MenuCategory.MOVE_TO: _PANEL_SLOT_MOVE_LAST,
            MenuCategory.USE: _PANEL_SLOT_USE_LAST,
            MenuCategory.SPECIAL: _PANEL_SLOT_SPECIAL_LAST,
        }
        header_slots = iter(
            (_PANEL_SLOT_NAME, _PANEL_SLOT_MOVE_HEADER,
             _PANEL_SLOT_USE_HEADER, _PANEL_SLOT_SPECIAL_HEADER)
        )
        for entry in entries:
            cat = entry.category
            if cat is MenuCategory.HEADER:
                rows.append(next(header_slots, None))
            elif cat in nxt:
                row = nxt[cat]
                rows.append(row if row <= last[cat] else None)
                nxt[cat] = row + 1
            elif cat is MenuCategory.GET:
                rows.append(_PANEL_SLOT_ITEM)      # $05D6, row 11
            elif cat is MenuCategory.LEAVE:
                rows.append(_PANEL_SLOT_LEAVE)     # $05FE, row 12 (DISC-244)
            elif cat is MenuCategory.QUIT:
                rows.append(_PANEL_SLOT_QUIT)
            else:
                rows.append(None)
        return rows

    @staticmethod
    def _control_rows(entries: "list[MenuEntry]") -> list[int | None]:
        """The CONTROL list's fixed rows — **[C-live] DISC-235.**

        Live-confirmed cell for cell: "CONTROL" 0, "Order:" 1, the seven crew
        2-8, "indicate" 9, "location" 10, "display" 11, "level:" 12, the three
        decks 13-15, and rows 16-18 left grey and empty.

        Note "indicate"/"location" is one wrapped label straddling **two
        different colours** (green then white), which is why the rows are
        assigned positionally rather than by category.
        """
        rows: list[int | None] = []
        crew_next = _CONTROL_SLOT_CREW_FIRST
        deck_next = _CONTROL_SLOT_DECK_FIRST
        header_seen = 0
        for entry in entries:
            cat = entry.category
            if cat is MenuCategory.CREW:
                rows.append(crew_next if crew_next <= 8 else None)
                crew_next += 1
            elif cat is MenuCategory.DECK:
                rows.append(deck_next if deck_next <= 15 else None)
                deck_next += 1
            elif cat is MenuCategory.INDICATE:
                # "indicate" then its wrapped "location" row.
                rows.append(9 if entry.selectable else 10)
            elif cat is MenuCategory.HEADER:
                # CONTROL, Order:, then display / level: after the crew block.
                rows.append((0, 1, 11, 12)[header_seen]
                            if header_seen < 4 else None)
                header_seen += 1
            else:
                rows.append(None)
        return rows

    def _draw_menu_panel(self, state: GameState) -> None:
        """The right-side CONTROL panel: coloured section bands + the cursor.

        The bands are painted first so **every** row of the panel carries a
        colour whether or not an entry sits on it (DISC-213) — and they now
        cover all nineteen, rows 0-18, which is what removes the black
        sections at the bottom (DISC-232).
        """
        if self._menu is None:
            return
        # R-02: the panel is exactly columns 30-39 of the 40x25 grid.
        px = _PANEL_COL * _C64_CELL
        width = self._surface.get_width() - px
        entries = self._menu.entries()
        cursor_idx = self._menu.current_index()
        row_h = 8
        crew_panel = (
            self._menu.selected_crew is not None
            and not self._menu.getting_item
            and not self._menu.indicating
        )
        # **DISC-232/235/236 — three screens, three colour tables.** The
        # crew-order panel's bands are live-captured (`_PANEL_SECTIONS`); the
        # CONTROL list's are `$7000`; the INDICATE screen's are `$7440`. All
        # three colour the same ten columns to different schemes, which is why
        # a table checked against the wrong screen looks like nonsense.
        if crew_panel:
            sections = _PANEL_SECTIONS
        elif self._menu.indicating:
            sections = _INDICATE_SECTIONS        # $7440
        else:
            sections = _CONTROL_SECTIONS         # $7000
        # DISC-232: the panel starts at screen row 0 (`$706F` fills colour RAM
        # row 0 cols 30-39), so there is no `+ 1` offset here any more.
        for first, last_row, colour in sections:
            pygame.draw.rect(
                self._surface, c64.rgb(colour),
                (px, first * row_h, width, (last_row - first + 1) * row_h),
            )

        # A crew-order panel uses the ROM's fixed slots (DISC-232); so does the
        # CONTROL list, with its own map (DISC-235). Only the INDICATE room
        # list — 34 rooms, longer than the panel — stays sequential, with a
        # scroll window so a wrapped-to cursor is always on screen.
        if crew_panel:
            placed = self._panel_rows(entries)
        elif not self._menu.indicating and not self._menu.getting_item:
            placed = self._control_rows(entries)
        else:
            window_start = 0
            if len(entries) > _PANEL_VISIBLE_ROWS:
                max_start = len(entries) - _PANEL_VISIBLE_ROWS
                if cursor_idx is not None:
                    window_start = max(0, min(cursor_idx, max_start))
            placed = [
                (n - window_start) if 0 <= n - window_start < _PANEL_VISIBLE_ROWS
                else None
                for n in range(len(entries))
            ]

        # **DISC-238 — the paper comes from the ROW, not the entry's category.**
        # The ROM colours these ten columns strictly by row, from whichever of
        # the three tables is in force; `_BAND_COLOUR` is a per-category
        # approximation that predates them. The two agree on the crew panel by
        # coincidence and disagree badly on INDICATE, where every row is
        # category INDICATE and the whole list came out light green over its
        # real blue band.
        # P2/P3: what the pointer will hit-test against. Recorded here, at the
        # one place the layout is decided, so a click can never disagree with
        # what was drawn.
        self._panel_placement = list(placed)
        row_colour = {
            r: c64.rgb(colour)
            for first, last_row, colour in sections
            for r in range(first, last_row + 1)
        }
        for i, (entry, row) in enumerate(zip(entries, placed)):
            if row is None:
                continue
            py = row * row_h
            band = row_colour.get(row, _BAND_COLOUR[entry.category])
            highlighted = i == cursor_idx
            # **Not the original (2026-09-05).** "back" (decoded ROM text
            # "quit", `[C $A715]`) gets fixed white-on-red rather than
            # whatever band its row inherited, so the one row that always
            # exits the current menu cannot be mistaken for a plain list
            # item. "Skip turn" (turns-mode only, also not the original)
            # gets a colour of its own for the same reason — a player
            # scanning the special-actions area for it should not have to
            # read every row.
            #
            # **Scoped off the INDICATE screen.** Its own "back" row lands on
            # a row number that changes with the page (`INDICATE_LABEL_QUIT`),
            # and `test_every_panel_row_carries_its_own_tables_band_colour`
            # checks that row against a *live capture* of the real colour
            # RAM — a decoded fact this override must not paint over. The
            # crew panel and the GET ITEM submenu have no such captured-colour
            # test locking their "back" row, so the override is fine there.
            own_colour = (
                not self._menu.indicating and (entry.back or entry.skip_turn)
            )
            if own_colour and entry.back:
                base_ink, base_band = c64.rgb(c64.WHITE), c64.rgb(c64.RED)
            elif own_colour and entry.skip_turn:
                base_ink, base_band = self._ink(state), c64.rgb(c64.CYAN)
            else:
                base_ink, base_band = self._ink(state), band
            # D-050: paper = the band's colour-RAM colour, ink = `$D021`
            # black. A highlighted row inverts that (the ROM's cursor is a
            # different colour-RAM value; modelled here as a swap).
            paper = base_ink if highlighted else base_band
            ink = base_band if highlighted else base_ink
            # Only a highlighted row repaints its background — everything
            # else keeps the section block already laid down underneath,
            # *unless* this row has its own fixed colour, which the section
            # painted over it earlier has to be replaced regardless.
            if highlighted or own_colour:
                pygame.draw.rect(self._surface, paper, (px, py, width, row_h))
            # D-052: no ">" arrow — the panel is only 10 columns wide and the
            # captured rows show no cursor glyph; selection is shown by the
            # row's own reverse-video inversion (the paper/ink swap above).
            label_surf = self._c64_or_sysfont(entry.label, ink, paper)
            self._surface.blit(label_surf, (px, py))
            if entry.skip_turn:
                # "Bold": a classic bitmap-font double-strike, one pixel to
                # the right — there is no bold variant of either font this
                # renderer draws with.
                self._surface.blit(label_surf, (px + 1, py))

    def _draw_jones_notice(self, state: GameState) -> None:
        """**[C $890C] D-149** — "Jones is here" on row 24 while the cat is in
        the selected crew member's room.

        `guard_6580` writes this string and arms the run animation from the
        same code path, past the same four gates, so the notice and the cat's
        dash are one event — which is why `jones_run_armed` is reused here
        verbatim rather than re-deriving the condition. Drawn as a filled
        yellow band with dark lettering, matching the other status rows and
        the live capture's colour RAM.
        """
        text = jones_notice_text(state, self._selected_crew(state))
        if text is None:
            return
        band = c64.rgb(_JONES_NOTICE_COLOUR)
        y = _JONES_NOTICE_ROW * _C64_CELL
        pygame.draw.rect(
            self._surface, band, (0, y, self._surface.get_width(), _C64_CELL)
        )
        self._surface.blit(
            self._c64_or_sysfont(text, self._ink(state), band),
            (0, y),
        )
    #: **[C $8710]** `LDA $86C8,Y / STA $0711,Y` for Y=0..14 — 15 characters at
    #: columns 25-39. Both original screenshots show it sharing the **room and
    #: damage** line ("CommdCentr : damage 00%   Grille in place"), which is the
    #: first of the status rows, not the crew line below it.
    #:
    #: It briefly lived on the crew line, where it forced a truncation at column
    #: 24 that cut "MORALE:CONFIDENT" down to "MORALE:C".
    #: `$0711` is row **19**, column 25 - the room line, not row 18.
    _GRILLE_CAPTION_ROW = _ROOM_ROW
    _GRILLE_CAPTION_COL = 25

    def _draw_status_line(self, state: GameState) -> None:
        """The bottom seven rows: four colour bands and the ROM's template."""
        row_h = _C64_CELL
        w = self._surface.get_width()

        # **[C paint_map_colors $7993]** The bands first, two rows tall each.
        # Row 18's char fill is only 30 wide (`$79B7`), so the grey stops at the
        # edge of the view window and the CONTROL panel keeps columns 30-39.
        for first, last, band in _BOTTOM_BANDS:
            width = _GREY_BAR_COLS * _C64_CELL if first == _GREY_BAR_ROW else w
            pygame.draw.rect(
                self._surface, band,
                (0, first * row_h, width, (last - first + 1) * row_h),
            )

        crew_id = self._menu.selected_crew if self._menu is not None else None
        crew = state.crew.get(crew_id) if crew_id else None
        if crew is None:
            # No crew selected: show the first living crew member's readout.
            crew = next((c for c in state.crew.values() if c.alive), None)
        if crew is None or crew.room_id is None or self._ship is None:
            return

        room = self._ship.rooms.get(crew.room_id)
        room_name = room.name if room is not None else crew.room_id
        # Real structural (acid) damage for this room, as a % of the breach
        # threshold (full disassembly §8.6).
        damage = state.room_damage.get(crew.room_id, 0)
        dmg_pct = 100 * damage // constants.HULL_BREACH_THRESHOLD
        here = co_occupants(state, crew)
        # **[C $7DCB] D-163** — `fear_band` reads `$6571`, the *derived*
        # composure, so the panel word includes the companion-support term
        # (D-151). `crew.morale` is the raw cell and would never react to
        # company.
        morale = (
            self._sim.morale_for(crew) if self._sim is not None else crew.morale
        )
        rows = bottom_panel_rows(
            room_name, dmg_pct, crew.name, crew.status, morale, here
        )
        for row, band_ix in ((_ROOM_ROW, 1), (_CREW_ROW, 2), (_ALSO_ROW, 2)):
            _, _, paper = _BOTTOM_BANDS[band_ix]
            # D-050: paper = the band colour, ink = `$D021` black.
            self._surface.blit(
                self._c64_or_sysfont(rows[row - _GREY_BAR_ROW],
                                     self._ink(state), paper),
                (0, row * row_h),
            )

    #: **[C draw_damage_warning $55C9]** The malfunction banner is copied to
    #: **`$07C0` = row 24, column 0** — the same address the Jones notice uses
    #: (`$890C`, D-149). Row 24 is the ROM's shared notice line. **Row 23 is not
    #: blank** as this note used to claim — it carries the Alien's attack
    #: banner (`$8BC4` -> `$0798`, DISC-245), which is simply absent from a
    #: capture taken while nothing is attacking.
    #:
    #: The remake appended ":WARNING:" to the room line and pushed the
    #: malfunction onto a fourth row of its own; neither has anywhere to go once
    #: the grille caption takes row 19's columns 25-39.
    #: Debug overlay colours. Light red / light blue so they read as obviously
    #: not-the-game against the map's green and the markers' white.
    _DEBUG_ALIEN_COLOUR = c64.LIGHT_RED
    _DEBUG_JONES_COLOUR = c64.LIGHT_BLUE
    #: **A ducted Alien is in a different space (DISC-257).** The duct network
    #: is a separate graph reached through the compass tables (`$81EF`, D-086),
    #: so a creature crawling it moves between rooms that share no door — which
    #: is correct, and looked like teleporting when this overlay drew it in the
    #: same colour as a surfaced one. Dark red means "in the vents, not in the
    #: room you are looking at".
    _DEBUG_ALIEN_DUCT_COLOUR = c64.RED

    def _draw_debug_markers(self, state: GameState) -> None:
        """Show where the Alien and Jones are. **Not the original.**

        There is no such mode in the ROM — this is a development aid, toggled
        with Ctrl+3 on the game-selection screen, and it is deliberately
        confined to the renderer: it reads state and draws, and changes nothing
        about how the game plays. Both use the same crew figure the real
        location marker uses (`_CHAR_SPRITE`, `$4F33`), recoloured.

        Off by default, and off in every screenshot the fidelity tests compare.
        """
        if not self._debug_markers or self._ship is None:
            return
        alien = state.alien
        alien_colour = (
            self._DEBUG_ALIEN_DUCT_COLOUR
            if alien is not None and alien.in_duct
            else self._DEBUG_ALIEN_COLOUR
        )
        for room_id, colour in (
            (alien.room_id if alien is not None and alien.alive else None,
             alien_colour),
            (None if state.jones_caught else state.jones_room_id,
             self._DEBUG_JONES_COLOUR),
        ):
            if room_id is None:
                continue
            room = self._ship.rooms.get(room_id)
            if room is None or room.deck != self._view_deck:
                continue
            real = self._room_marker_px(room_id)
            if real is None:
                continue
            self._blit_sprite(
                _CHAR_SPRITE, real[0] + 12, real[1] + 10, c64.rgb(colour)
            )

    def _draw_char_portrait(self, state: GameState) -> None:
        """The commanded crew member's portrait — **[C $6667] DISC-245.**

        `place_selected_char_sprite` writes sprite 2's registers and nothing
        else::

            $6667  LDA #$A9 / STA $D005    Y = 169 -> screen y 119
            $666F  TYA / ADC #$BC / STA $07FA   pointer = $BC + slot
            $6676  LDA $6501,Y / STA $D029  colour = the duct flag (D-053)
            $667C  LDA #$1C / STA $D004    X = 28  -> screen x 4

        Sprites are drawn by the VIC over whatever is in the character screen,
        so this is **independent of the deck plan** — nothing in it consults
        `$7569` or a deck template.

        That is why it lives here and not inside `_draw_deck`. The Narcissus
        draws a cockpit instead of a deck plan (D-144), and with the portrait
        buried in the deck path, boarding the shuttle silently took it away.
        The ROM never disables sprite 2 on that path.
        """
        marker_id = self._menu.selected_crew if self._menu is not None else None
        marker = state.crew.get(marker_id) if marker_id else None
        if marker is None or not marker.alive:
            return
        roster_ids = list(state.crew)
        if marker.id not in roster_ids:
            return
        slot = _PORTRAIT_SLOTS[
            min(roster_ids.index(marker.id), len(_PORTRAIT_SLOTS) - 1)
        ]
        self._blit_portrait(
            marker.id,
            slot,
            _CHAR_PORTRAIT_AT[0] + 12,
            _CHAR_PORTRAIT_AT[1] + 10,
            c64.rgb(
                _CHAR_PORTRAIT_DUCT_COLOUR if marker.in_duct
                else _CHAR_PORTRAIT_ROOM_COLOUR
            ),
            # Black in a room, white in a duct (`$6501,Y`) — the colour says
            # where they are, so supplied art must not flatten it (D4).
            varies=True,
        )

    def _draw_attack_banner(self, state: GameState) -> None:
        """"Alien attacking <name>" on row 23 — **[C $8BC4/$8D10] DISC-245.**

        String and geometry are the ROM's own. *When* it is shown is not any
        more, both presets (owner's request, 2026-09-06): whoever is
        currently selected while co-located with the Alien, not only the one
        crew member `$8CE1 CPY $64FB` happened to pick at encounter-start —
        see `play.py`'s room-co-location check, which the siren and the
        animation now share. The name comes from the roster table at `$A65E`,
        ten bytes, at column 16; `$8CCC` blanks the row the moment there is
        no victim.
        """
        if not self._attacking or self._attacking_crew_id is None:
            return
        victim = state.crew.get(self._attacking_crew_id)
        if victim is None:
            return
        cells = [" "] * _C64_COLS
        _place(cells, 0, _ATTACK_BANNER)
        _place(cells, _ATTACK_BANNER_NAME_COL, victim.name[:_NAME_W])
        _, _, paper = _BOTTOM_BANDS[3]          # rows 23-24, yellow
        self._surface.blit(
            self._c64_or_sysfont("".join(cells).rstrip(), self._ink(state), paper),
            (0, _ATTACK_BANNER_ROW * _C64_CELL),
        )

    _NOTICE_ROW = 24

    def _draw_notice_line(self, state: GameState) -> None:
        """Row 24: the malfunction banner, in the ROM's own wording."""
        # **[C $5A26] DISC-230 — the auto-destruct countdown owns this row.**
        # `mainloop_sub_5a26` posts its banner through the very same
        # `draw_damage_warning ($55C9)` every malfunction uses, so an armed
        # countdown simply occupies the notice line. It was decoded into
        # `MALFUNCTION_MESSAGES[7]`/`[8]` long ago and never displayed, leaving
        # a player racing the clock with no on-screen indication of the time
        # left. Checked first because the ROM's countdown re-posts it on every
        # wrap, overwriting whatever else was there.
        banner = (
            constants.auto_destruct_banner(state.auto_destruct_minutes_left)
            if state.auto_destruct_ticks is not None
            else None
        )
        if (not state.notice and not banner and not state.malfunction
                and not state.tracker_alarm):
            return
        # D-072/D-073: raised by the same event that latches a room's alarm
        # (`damage_room_b $5587` falls through to the dispatcher at `$55C1`).
        # The ":WARNING:" prefix is the ROM's own `$5485`.
        # **[C $07C0] DISC-231** — a transient banner (MOTHER refuses launch /
        # Go get Jones / Fire Out) owns the row outright while it is up: the
        # ROM writes it, blocks, then blanks the row.
        if state.notice:
            text = state.notice
        elif banner:
            text = banner
        elif state.malfunction:
            text = f"WARNING:{state.malfunction}"
        else:
            # D-041 ([C $451C]): the TRACKER alert names neither a room nor an
            # entity — the ROM's sound legend proves it ("SOMETHING moving
            # between locations"), so this must never hint at the Alien.
            text = "SOMETHING IS MOVING"
        _, _, paper = _BOTTOM_BANDS[3]
        self._surface.blit(
            self._c64_or_sysfont(text[:_C64_COLS], self._ink(state), paper),
            (0, self._NOTICE_ROW * _C64_CELL),
        )

    def _draw_grille_caption(self, state: GameState) -> None:
        """The GRILLE IN PLACE / REMOVED caption, at the ROM's own position."""
        crew_id = self._menu.selected_crew if self._menu is not None else None
        crew = state.crew.get(crew_id) if crew_id else None
        if crew is None:
            crew = next((c for c in state.crew.values() if c.alive), None)
        if crew is None or crew.room_id is None:
            return
        caption = self._grille_text(crew.room_id)
        if not caption:
            return
        # The caption sits **inside** the room band, so it takes that band's
        # colours - `paint_map_colors` gives row 19 `$0D` like the rest of the
        # line. Drawing it light grey on the default background made it a
        # different colour from the text it shares a row with.
        _, _, paper = _BOTTOM_BANDS[1]
        self._surface.blit(
            self._c64_or_sysfont(caption[:15], self._ink(state), paper),
            (self._GRILLE_CAPTION_COL * _C64_CELL,
             self._GRILLE_CAPTION_ROW * _C64_CELL),
        )

    def _grille_text(self, room_id: str) -> str:
        if self._ship is None:
            return ""
        for g in self._ship.grilles:
            if g.room_id == room_id:
                # **[C $86C8 / $86D7]** The ROM's own casing, 15 characters
                # each: `87 12 09 0C 0C 05 ...` is "Grille in place", not the
                # shouted form (DISC-215 - the charset's high bit selects case).
                return "Grille removed" if g.is_open else "Grille in place"
        return ""
    def _draw_attack_animation(self) -> None:
        """Draw the six-sprite Alien composite over the screen (D-096).

        Runs only while :attr:`_attacking`, which is now a plain
        room-co-location fact (owner's request, 2026-09-06, both presets —
        see the check in `play.py`'s `render`), not the ROM's own one-shot
        `$8CE1` gate: it starts the moment the selected crew member shares a
        room with a living, surfaced Alien and drops the moment either one
        leaves, regardless of who was selected when the encounter began.
        """
        if self._tiles is None or not self._attacking:
            return
        frame = _ATTACK_FRAMES[
            (self._frame_count // _POINTER_RATE) % len(_ATTACK_FRAMES)
        ]
        for row, slots in enumerate(_ATTACK_SLOTS):
            for col, base in enumerate(slots):
                slot = _ATTACK_STATIC_SLOT if base is None else base + frame
                surf = self._sprite_surface(
                    slot - _SPRITE_SLOT_BASE, c64.rgb(_ATTACK_COLOUR)
                )
                if surf is None:
                    continue
                w = surf.get_width() * _ATTACK_EXPAND
                h = surf.get_height() * _ATTACK_EXPAND
                big = pygame.transform.scale(surf, (w, h))
                x = (_ATTACK_X[col] - _SPRITE_ORIGIN[0])
                y = (_ATTACK_Y[row] - _SPRITE_ORIGIN[1])
                self._surface.blit(big, (x, y))
    def _draw_duct_map(self, crew: CrewMember) -> None:
        """Paint the duct sheet for the room ``crew`` is inside (D-091).

        `select_menu_template ($817D)` picks the sheet, `render_message
        ($7F0D)` paints its 30x18 cells from screen `$0400`, and `mark_exits
        ($7F78)` colours exactly two things: your own node white, and the duct
        runs leading away from it light blue. **Everything else is left black**
        — painted, but invisible against the black background — which is why
        the duct view shows only the part of the network you can reach from
        where you stand. `core.ductmap` computes that colour grid; this method
        only blits it.
        """
        if self._tiles is None:
            return
        try:
            room_index = data.ROOM_SLUGS.index(crew.room_id)
        except ValueError:
            return
        if room_index >= len(data.DUCT_MAP_ROOM_TEMPLATE):
            return          # the off-map Narcissus rooms have no duct sheet
        for row, col, code, colour in ductmap.lit_cells(room_index):
            self._blit_codes([code], col, row, c64.rgb(colour))
    def _draw_deck(self, state: GameState) -> None:
        """Draw rooms on the watched deck, crew markers, and the target cursor.

        Markers are placed by scaling our internal room-grid coordinates (x, y)
        into whatever pixel footprint the map actually occupies this frame —
        the real backdrop's native size when one's loaded, or the placeholder
        grid's fixed cell size otherwise — rather than a hardcoded cell size,
        so they land inside the visible map either way. Precise alignment onto
        the real backdrop's *actual* per-room boundaries (rather than our
        coarse internal grid, DECISIONS D-010 #2 / core/nostromo.py) is a
        follow-up: it needs the real room boundaries extracted from the
        capture, not just its background art.
        """
        if self._ship is None:
            return
        # R-41 / D-091: a character inside the ducting gets a **different map**
        # — one of three duct sheets, not the deck plan. `$779C` switches on
        # the same in-duct flag the MOVE TO menu switches on, so the map and
        # the menu always agree about which network you are travelling.
        selected = self._selected_crew(state)
        if selected is not None and selected.in_duct:
            self._draw_duct_map(selected)
            return
        # R-02: the ship map starts at the very top-left of the 40x25 field
        # (columns 0-29, rows 0-16), matching the captured screen RAM.
        ox = oy = 0
        rooms = self._ship.rooms_on(self._view_deck)
        grid_cols = max((r.x for r in rooms), default=0) + 1
        grid_rows = max((r.y for r in rooms), default=0) + 1
        backdrop = self._backdrop_surface(self._view_deck)
        if backdrop is not None:
            # Real captured map art (deck_backdrop.py) — the authentic room
            # shapes/walls, not a uniform grid of placeholder tiles.
            self._surface.blit(backdrop, (ox, oy))
            cell_w = backdrop.get_width() / grid_cols
            cell_h = backdrop.get_height() / grid_rows
        else:
            tile = self._room_tile()  # authentic C64 tile, or None -> primitive box
            for room in rooms:
                rx, ry = ox + room.x * _CELL, oy + room.y * _CELL
                if tile is not None:
                    self._surface.blit(tile, (rx, ry))
                else:
                    pygame.draw.rect(
                        self._surface, (40, 90, 40),
                        (rx, ry, (_CELL - 6), (_CELL - 6)), 1,
                    )
            cell_w = cell_h = _CELL
        # INDICATE LOCATION — **the ROM's own animated pointer (D-082).**
        # This was a flashing white box; the original uses **sprite 1**, whose
        # pointer `$4FCB` cycles `$BC -> $BB -> $BA -> $B9 -> $B8` once per IRQ
        # tick (`DEC $657A`, wrapping `$B8` -> `$BC`, `STA $07F9`), drawn WHITE
        # (`$D028 = 1`) and shown only while `$64BE` is set. Those five slots
        # decode to concentric expanding rectangles resolving into a figure —
        # a zoom-in "locate" animation. Position comes from `$758D`/`$75B1`
        # indexed by the target room (`$76D7`), the same tables as the
        # character marker (D-058).
        # **[C $7C3D] P4-2** — the same pointer animation previews the MOVE TO
        # destination the cursor is hovering, not just INDICATE LOCATION.
        # **M1/M2 — the clickable rooms, recorded as they are drawn.**
        # Only destinations the panel is offering, and only on the deck being
        # shown, since only those were drawn. Recorded with the cell size the
        # frame actually used: with the captured backdrop that is
        # `backdrop.width / grid_cols`, without it a flat `_CELL`, and
        # hit-testing against the wrong one lands a click a room away.
        self._hot_clear()
        destinations: dict[str, int] = (
            self._menu.move_destinations() if self._menu is not None else {}
        )
        for room_id, entry_index in destinations.items():
            droom = self._ship.rooms.get(room_id)
            if droom is None or droom.deck != self._view_deck:
                continue                      # a ladder's far side: not drawn
            # **Where the room actually IS, not where the grid says (owner's
            # playtest, 2026-08-30).** These boxes used to be laid out on the
            # internal grid - `ox + droom.x * cell_w` - while the map art and
            # every marker on it are placed from the ROM's own decoded table
            # (`$758D`/`$75B1`, `_room_marker_px`). The two layouts are not the
            # same shape, so the hover box for a room sat somewhere else
            # entirely: rooms lit up, but never the one under the pointer.
            #
            # The marker is a 24x21 hardware sprite drawn from that position,
            # so targeting the same rectangle means the thing you can hover is
            # exactly the thing you can see. The grid stays as the fallback for
            # synthetic test maps, which is what `_room_marker_px` returns
            # `None` for.
            at = self._room_marker_px(room_id)
            if at is not None:
                box = pygame.Rect(at[0], at[1], _MARKER_W, _MARKER_H)
            else:
                box = pygame.Rect(
                    int(ox + droom.x * cell_w), int(oy + droom.y * cell_h),
                    max(1, int(cell_w)), max(1, int(cell_h)),
                )
            self._hot_add(box, "room", entry_index)

        indicated = self._menu.indicated_room_id if self._menu is not None else None
        if indicated is None and self._menu is not None:
            indicated = self._menu.previewed_room_id
        # **M4 — the pointer follows the mouse too.** The ROM's own `$4FCB`
        # animation is five sprite frames of concentric expanding rectangles
        # (D-082), already used to preview the destination the *cursor* is
        # browsing (P4-2). Hovering the map is the same act with a different
        # input, so it drives the same animation rather than a second one
        # invented alongside it.
        if indicated is None and self._menu is not None:
            indicated = self._menu.hovered_room_id
        if indicated is not None:
            iroom = self._ship.rooms.get(indicated)
            if iroom is not None and iroom.deck == self._view_deck:
                frame = _POINTER_FRAMES[
                    (self._frame_count // _POINTER_RATE) % len(_POINTER_FRAMES)
                ]
                real = self._room_marker_px(indicated)
                if real is not None:
                    px, py = int((real[0] + 12)), int((real[1] + 10))
                else:
                    px = int(ox + iroom.x * cell_w + cell_w // 2)
                    py = int(oy + iroom.y * cell_h + cell_h // 2)
                self._blit_sprite(frame, px, py, c64.rgb(c64.WHITE))
        # The current character's location marker: the game's person sprite at
        # the selected crew member's room (a single figure, as in the original).
        marker_id = self._menu.selected_crew if self._menu is not None else None
        marker = state.crew.get(marker_id) if marker_id else None
        if marker is not None and marker.alive and marker.room_id is not None:
            mroom = self._ship.rooms.get(marker.room_id)
            if mroom is not None and mroom.deck == self._view_deck:
                # R-08 (D-058): the ROM's own per-room marker position when the
                # room is in its table; the internal grid only as a fallback.
                real = self._room_marker_px(marker.room_id)
                if real is not None:
                    cx = int((real[0] + 12))
                    cy = int((real[1] + 10))
                else:
                    cx = int(ox + mroom.x * cell_w + cell_w // 2)
                    cy = int(oy + mroom.y * cell_h + cell_h // 2)
                # R-19 (D-045): pulse the marker through the ROM's own
                # heartbeat colour cycle (`$4ED4` -> `$D027`) instead of a
                # static white.
                # D-061: rate from the ROM's own composure->divider table.
                # [C $4F38-$4F3F] a constant 7-tick reload — NOT composure.
                period = _HEARTBEAT_PERIOD_TICKS
                beat = _HEARTBEAT_COLOURS[
                    (self._frame_count // period) % len(_HEARTBEAT_COLOURS)
                ]
                # `varies=True`: the colour *is* the heartbeat, so a supplied
                # sprite has to keep it or the beat is gone (D4).
                self._blit_sprite(_CHAR_SPRITE, cx, cy, c64.rgb(beat),
                                  varies=True)
        # Jones's run (D-089). Note this is **not** a map marker — it is
        # sprite 3 crossing the screen at a fixed Y, independent of the deck
        # plan, which is why it coexists with the "no cat symbol" finding
        # below. Armed by `jones_run_armed`, it advances 4 px per tick from
        # X=0 and disappears at X=$F0.
        armed = jones_run_armed(
            state.jones_room_id, state.jones_caught, self._selected_crew(state)
        )
        if armed and self._jones_x is None:
            self._jones_x = _JONES_X_START      # maybe_clear_64ba ($4FFC)
            self._jones_stop = False
        elif armed:
            # **[C $4FF4-$4FFB] D-146** — re-arming while already running just
            # clears any pending stop; the loop carries on uninterrupted.
            self._jones_stop = False
        elif self._jones_x is not None:
            # Arming condition dropped: a stop is REQUESTED ($64BA), but the
            # cat finishes its current crossing to the right edge first — it
            # is never blanked mid-run (P3-15/D-146; we used to kill it here).
            self._jones_stop = True
        if self._jones_x is not None:
            frame = _JONES_FRAMES[
                (self._frame_count // _JONES_RATE) % len(_JONES_FRAMES)
            ]
            self._blit_sprite(
                frame,
                int((self._jones_x - _SPRITE_ORIGIN[0])),
                int((_JONES_Y - _SPRITE_ORIGIN[1])),
                c64.rgb(_JONES_COLOUR),
            )
            # **P3-15.** `update_3 ($4F5C)` steps X and the leg frame from ONE
            # clock (once per animation tick). **D-146:** the add is 8-bit —
            # past $F0 with no stop pending it wraps through $FF -> $00 and
            # the run loops; only a pending stop ends it, at the edge.
            if self._frame_count % _JONES_RATE == 0:
                self._jones_x = (self._jones_x + _JONES_X_STEP) & 0xFF
                if self._jones_x >= _JONES_X_END and self._jones_stop:
                    self._jones_x = None    # `$4F6E`: blank + clear the flag
                    self._jones_stop = False
