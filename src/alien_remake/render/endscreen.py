"""The ending screen and the hull-breach spiral that can precede it.

Split out of :mod:`.frontend` (DISC-250), which had grown to 1,651 lines and at
least four distinct screens. The cut was derived from a call graph rather than
eyeballed: of the 24 module-level names these two methods touch, **all 24 are
used by nothing else in the module**, and the methods themselves call only
`_blit_cells`, `_blit_wrapped` and each other. That made this the one screen
that comes out whole.

The ending is **composed, not picked** (`select_outcome $60A9`, D-077): up to
four independent lines land on fixed rows, one per outcome axis. The decoded
strings and their row numbers live a layer further down, in
:mod:`alien_remake.screens.ending`; what is here is the drawing.
"""

from __future__ import annotations

import pygame  # the project's one optional runtime dependency (D-009)

from ..core import constants
from ..core.crew import CrewMember
from ..core.flow import GameFlow
from ..core.nostromo import NARCISSUS
from ..core.scoring import competence_rating
from ..core.state import GameState
from ..screens import ending
from . import c64
from .layout import _C64_CELL, _COLS, _ROWS
from .protocol import RendererState

_MENU_BG = c64.rgb(c64.GREEN)
_ENDING_ALIEN_DEAD = ending.ENDING_ALIEN_DEAD
_ENDING_EGGS = ending.ENDING_EGGS
_ENDING_NARCISSUS = ending.ENDING_NARCISSUS
_ENDING_ALL_CREW_LOST = ending.ENDING_ALL_CREW_LOST
_ENDING_NOSTROMO_RETURNS = ending.ENDING_NOSTROMO_RETURNS
_ENDING_NOSTROMO_DESTROYED = ending.ENDING_NOSTROMO_DESTROYED
_ENDING_BRINGS_BACK = ending.ENDING_BRINGS_BACK
_ENDING_IS_INSANE = ending.ENDING_IS_INSANE
_ENDING_SURVIVORS = ending.ENDING_SURVIVORS
_ENDING_COMPETENCE = ending.ENDING_COMPETENCE
_ENDING_PRESS_ANY_KEY = ending.ENDING_PRESS_ANY_KEY
_ENDING_ROWS = ending.ENDING_ROWS
_ENDING_BRINGS_BACK_COL = ending.ENDING_BRINGS_BACK_COL
_ENDING_NAME_VISIBLE = ending.ENDING_NAME_VISIBLE
_END_RATING_ROW = ending.END_RATING_ROW
_END_RATING_DIGIT_COL = ending.END_RATING_DIGIT_COL
_END_PRESS_KEY_ROW = ending.END_PRESS_KEY_ROW
_END_PRESS_KEY_COL = ending.END_PRESS_KEY_COL
_END_SURVIVOR_HEADER_ROW = ending.END_SURVIVOR_HEADER_ROW
_END_SURVIVOR_FIRST_ROW = ending.END_SURVIVOR_FIRST_ROW
_END_SURVIVOR_ROWS = ending.END_SURVIVOR_ROWS


_BREACH_PALETTE: tuple[int, ...] = (0x02, 0x08, 0x07, 0x01, 0x07, 0x08)
#: `$5D17 LDA #$20` / `$5D25 LDA #$05` — the blanking pass writes `$20` over
#: screen RAM from `$05EB`; the six colour passes write to colour RAM from
#: `$D9EB` (`$5D6C LDA #$D9`). Both start from the same offset, `$1EB` = 491
#: (row 12, col 11). NB the first cell actually *written* is `ptr + leg` = 507,
#: since `$5C55` opens `LDY $64E1` and counts down.
_BREACH_START = 0x05EB - 0x0400
#: `$5C42` seeds `$64E0` (run) at 1 and `$64E1` (leg) at `$10`; `$5C63 CMP #$28`
#: ends it.
_BREACH_RUN0, _BREACH_LEG0, _BREACH_LEG_END = 1, 0x10, 0x28


def breach_spiral_cells() -> list[int]:
    """Every screen offset `animate_fill_row ($5C42)` writes, in order.

    A **transliteration of the ROM's pointer arithmetic**, not a reconstructed
    geometry — each step below is the corresponding instruction, so the cell
    order is the machine's rather than a spiral that merely looks similar::

        5C55  LDY $64E1 / STA ($FB),Y / DEY / BPL   ; leg..0, downward
        5C63  CMP #$28 / BNE                        ; ...until leg hits 40
        5C70  INC $64E1                             ; leg++
        5C77  ADC #$28 / STA ($FB),Y=0  x $64E0     ; run cells DOWN
        5C90  INC $64E0                             ; run++
        5C98  LDY #$01 .. CPY $64E1 / BCC / BEQ     ; 1..leg, rightward
        5CA8  ADC $64E1 / INC $64E1                 ; step right, leg++
        5CBB  SBC #$28 / STA ($FB),Y=0  x $64E0     ; run cells UP
        5CD4  INC $64E0 / SBC $64E1                 ; run++, step left
        5CE6  JMP $5C55

    The pointer starts at `$05EB` (row 12, col 11) and it spirals out until
    it has covered
    **all 1000 cells** — verified by enumeration, not assumed. 1012 of the
    writes are on screen (twelve cells are painted twice where the turns
    overlap) and exactly one lands on `$03FF`, the byte before screen RAM;
    that stray write is the ROM's own and is simply dropped here.

    **This is NOT the loader's spiral** (`SPIRAL_CELLS`, DISC-207): different
    start, different growth, and it fills colour RAM rather than a char grid.
    """
    out: list[int] = []
    run, leg = _BREACH_RUN0, _BREACH_LEG0
    ptr = _BREACH_START

    def put(offset: int) -> None:
        if 0 <= offset < _COLS * _ROWS:      # `$03FF` is off-screen; drop it
            out.append(offset)

    while True:
        for y in range(leg, -1, -1):                     # $5C55
            put(ptr + y)
        if leg == _BREACH_LEG_END:                       # $5C63
            return out
        leg += 1                                         # $5C70
        for _ in range(run):                             # $5C77
            ptr += _COLS
            put(ptr)
        run += 1                                         # $5C90
        y = 1                                            # $5C93
        while True:                                      # $5C98
            put(ptr + y)
            y += 1
            if y > leg:
                break
        ptr += leg                                       # $5CA8
        leg += 1                                         # $5CB4
        for _ in range(run):                             # $5CBB
            ptr -= _COLS
            put(ptr)
        run += 1                                         # $5CD4
        ptr -= leg                                       # $5CD7


#: Built once — the order is fixed, so there is no reason to re-walk it.
BREACH_SPIRAL: tuple[int, ...] = tuple(breach_spiral_cells())


class EndScreenMixin(RendererState):
    """The end-of-game screen. Mixed into :class:`~.pygame_app.PygameRenderer`."""

    #: `[?]` **The one thing here that is not decoded.** The ROM's pace comes
    #: from `anim_sound_tick ($5CEA)`'s delay loop running once per cell, which
    #: has no clean frame equivalent; this is chosen so all seven passes take
    #: about four seconds at `_FRAME_HZ`, which is the right order of magnitude
    #: for the ROM's ~7,000 delayed writes. Everything else — the cell order,
    #: the palette, the pass count — is the machine's.
    _BREACH_CELLS_PER_FRAME = 60

    def _draw_breach_animation(self) -> bool:
        """The burning-ship spiral — **[C hull_breach $5D17].** True while running.

        Seven passes over `BREACH_SPIRAL`, in the ROM's own order::

            5D2E  JSR animate_fill_row     ; pass 0: blank the screen ($20)
            5D63  loop Y=0..5:             ; passes 1-6: colour RAM,
                    $64DD = $5D11,Y        ;   RED ORANGE YELLOW WHITE
                    $FC = $D9              ;   YELLOW ORANGE
                    JSR animate_fill_row
            5C6A  LDA #$00 / STA $D020     ; ...and the border ends BLACK

        The remake has no separate colour RAM, so the blanking pass paints the
        field black and each colour pass paints its own colour over the cells
        as the spiral reaches them — the same visible result as recolouring a
        screen already filled with `$A0` solids ($5D48).
        """
        total = len(BREACH_SPIRAL)
        passes = 1 + len(_BREACH_PALETTE)
        drawn = self._frame_count * self._BREACH_CELLS_PER_FRAME
        if drawn >= total * passes:
            return False                      # finished; fall through
        cell = _C64_CELL
        done_passes, into = divmod(drawn, total)
        for p in range(done_passes + 1):
            colour = (
                c64.rgb(c64.BLACK) if p == 0
                else c64.rgb(_BREACH_PALETTE[p - 1])
            )
            upto = total if p < done_passes else into
            for off in BREACH_SPIRAL[:upto]:
                row, col = divmod(off, _COLS)
                self._surface.fill(colour, (col * cell, row * cell, cell, cell))
        self._present(c64.rgb(c64.BLACK))     # $5C6A — the border ends black
        return True

    def _draw_end(self, flow: GameFlow) -> None:
        """The result screen, following `select_outcome ($60A9)`'s own order.

        **DISC-230 — traced in full.** The routine composes four independent
        lines at four fixed rows; the remake was drawing three of them, centred,
        and omitting the ship's fate entirely.

        1. **row 3, `$0478` — the SHIP.** Branches on `$64CF` (the "going to be
           destroyed" flag, raised by SCUTTLE *and* by a hull breach):

               60AE  LDA $64CF / BEQ $60D0     ; clear -> "returns to Earth"
               60B3  LDY $64C3                 ; the ANDROID's slot
               60B6  LDA $7D45,Y / CMP #$02    ; ...alive?
               60BD  LDA $7935,Y / CMP #$22    ; ...and NOT aboard the shuttle?
               60C4  JSR draw_ending_survivor  ;   -> "<name> brings it back"
               60CA  JSR draw_ending_survivors ;   -> "is destroyed"

           The android arm also **clears `$64CF`** (`$62D6`), which is what
           re-enables the damage term in the rating at `$6229`.
        2. **row 6, `$04F0` — the ALIEN**, if its damage reached 50 (`$60D8
           CMP #$32`).
        3. **row 8, `$0540` — the NARCISSUS**, if it launched (`$64E3`).
        4. **row 10, `$0590` — the EGGS**, the no-Alien-kill ending, 55 cells
           so it wraps onto row 11.

        Then row 13 is "All crew lost" *or* "Survivors:" (the two arms of
        `$6166`'s scan, never both), names from row 14 one apart, and the
        rating at row 22. Everything is written at **column 0** — none of it is
        centred, which is what `_blit_center` was doing.
        """
        assert flow.sim is not None
        state = flow.sim.state
        # **[C hull_breach $5D17] DISC-234** — when the ship actually blew up,
        # the destruction animation runs to completion *before* the ending is
        # drawn (`$5DCE JMP endgame_dispatch` is the last thing it does).
        if state.ship_destroyed and self._draw_breach_animation():
            return
        self._surface.fill((0, 0, 0))
        alien = state.alien
        alien_dead = alien is not None and alien.damage >= constants.ALIEN_DAMAGE_TO_KILL
        survivors = [c for c in state.crew.values() if c.alive]

        # 1) The ship's fate (row 3). `$64CF` is `state.ship_destructing`.
        if not state.ship_destructing:
            self._blit_cells(_ENDING_NOSTROMO_RETURNS, 0,
                             _ENDING_ROWS["nostromo"], _MENU_BG, c64_font=True)
        else:
            android = state.crew.get(state.android_id or "")
            saved = (
                android is not None
                and android.health >= constants.CREW_INCAPACITATED_BELOW
                and not (state.narcissus_launched and android.room_id is None)
                and android.room_id != NARCISSUS
            )
            if saved and android is not None:
                # `$62B6`: ten name bytes to `$0478`, then `$6314` over the
                # last two from `$0480` — only eight of the name survive.
                self._blit_cells(android.name[:_ENDING_NAME_VISIBLE], 0,
                                 _ENDING_ROWS["nostromo"], _MENU_BG, c64_font=True)
                self._blit_wrapped(_ENDING_BRINGS_BACK, _ENDING_BRINGS_BACK_COL,
                                   _ENDING_ROWS["nostromo"], _MENU_BG, c64_font=True)
            else:
                self._blit_cells(_ENDING_NOSTROMO_DESTROYED, 0,
                                 _ENDING_ROWS["nostromo"], _MENU_BG, c64_font=True)

        # 2) The Alien (row 6) — `$60D8 CMP #$32`, tested on every ending.
        if alien_dead:
            self._blit_cells(_ENDING_ALIEN_DEAD, 0,
                             _ENDING_ROWS["alien"], _MENU_BG, c64_font=True)
        # 3) The Narcissus (row 8) — `$614F LDA $64E3`.
        if state.narcissus_launched:
            self._blit_cells(_ENDING_NARCISSUS, 0,
                             _ENDING_ROWS["ship"], _MENU_BG, c64_font=True)
        # 4) The eggs (row 10, wrapping to 11) — the not-killed ending.
        if not alien_dead:
            self._blit_wrapped(_ENDING_EGGS, 0, _ENDING_ROWS["eggs"],
                               _MENU_BG, c64_font=True)

        # Row 13: the two arms of `$6166`, never both.
        if survivors:
            self._blit_cells(_ENDING_SURVIVORS, 0,
                             _END_SURVIVOR_HEADER_ROW, _MENU_BG, c64_font=True)
            row = _END_SURVIVOR_FIRST_ROW
            for c in survivors[:_END_SURVIVOR_ROWS]:
                # `$61E7` appends "is insane" nine cells in, over the name's
                # own field, when the composure cell is exactly 0.
                self._blit_cells(c.name[:_COLS], 0, row, _MENU_BG, c64_font=True)
                if c.is_insane:
                    self._blit_cells(_ENDING_IS_INSANE, 9, row, _MENU_BG, c64_font=True)
                row += 1
        else:
            self._blit_cells(_ENDING_ALL_CREW_LOST, 0,
                             _ENDING_ROWS["crew"], _MENU_BG, c64_font=True)

        rating = competence_rating(state)
        self._blit_cells(_ENDING_COMPETENCE, 0, _END_RATING_ROW, _MENU_BG, c64_font=True)
        self._blit_cells(f"{rating:02d}", _END_RATING_DIGIT_COL,
                         _END_RATING_ROW, _MENU_BG, c64_font=True)
        # `$6475` (13 bytes, lowercase) -> `$07D8` = row 24, **column 24**
        # (`$645E-$6467` copies it verbatim). Was an invented, centred,
        # shouted "PRESS ANY KEY" at column 13.
        self._blit_cells(_ENDING_PRESS_ANY_KEY, _END_PRESS_KEY_COL,
                         _END_PRESS_KEY_ROW, _MENU_BG, c64_font=True)
        # **`screen_fx` does not touch this screen.** DISC-311/313 wired it
        # in briefly; DISC-314 scoped it back down to the boot report only,
        # per the owner's own words: "the intro animation should just be for
        # the initial screen of dos text." This screen's `PRESS ANY KEY` is
        # decoded ROM text (`$6475`, the comment above) either way, so it was
        # never going to carry the option's own prompt line regardless.
        self._present()
