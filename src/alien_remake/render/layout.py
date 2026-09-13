"""Screen geometry and timing shared by both halves of the renderer (D-191).

When `pygame_app.py` was split into a front end and a play screen, a handful of
constants turned out to be needed by both: the 320x200 field and its 40x25 cell
grid, the sprite bank base, the app's frame rate, and the reveal/poke rates the
loader animations are paced by.

They live here rather than in either half so neither has to import the other for
them — `pygame_app` composes the mixins, so a constant owned by one half and
borrowed by the other would make the dependency run backwards.

Every value is measured off the real machine or read from the ROM; the comments
carry the provenance.
"""

from __future__ import annotations

_WIDTH = 320
_HEIGHT = 200
# The text grid itself (320x200 / 8x8).
_COLS = _WIDTH // 8    # 40
_ROWS = _HEIGHT // 8   # 25
#: **[C $061D] D-176 - all four descriptions share ONE slot.** `$44D6` (the
#: heartbeat) and then each of `$4500`/`$4554`/`$452A` are copied to the *same*
#: address, row 13 col 21, so they **replace each other in place** rather than
#: stacking down the screen. The 42-char field wraps onto row 14 at col 0.
_KEY_SLOT_ROW, _KEY_SLOT_COL = 13, 21
_SPRITE_BANK_BASE = 0x2000        # bank base for `pointer*64` sprite data
_C64_CELL = 8                     # C64 character cell size (px)
# [C $4FCB] R-37/D-082: sprite 1's pointer cycles VIC slots $BC -> $BB -> $BA
# -> $B9 -> $B8 and wraps, once per IRQ tick. Decoded, $BC..$B9 are concentric
# expanding rectangles (ink spans 9/11/13/15) and $B8 resolves into a small
# figure (span 7) — a zoom-in "locate" animation.
#
# `tiles.sprites` is indexed from VIC slot $A0, which is why `_CHAR_SPRITE` is
# 24 for slot $B8; the same offset applies here. Note the last pointer frame IS
# `_CHAR_SPRITE` — the animation resolves into the very glyph used for a
# character's position marker, which is what makes it read as "here they are".
#: The renderer's nominal frame rate, used to scale the ROM's IRQ-paced
#: animations onto the display clock.
_FRAME_HZ = 30.0
# **[C $5EF7] R-09 CONFIRMED (2026-07-24, D-049):** `main_dispatch ($5ECE)`
# writes sprite pointers `$BD..$C3` into `$07F8..$07FE`, i.e. slots
# `$BD-$A0` = **29..35** — exactly this tuple, in this order. It also zeroes
# all eight sprite colour registers (`$5EEF: STA $D027,Y`, A=0), so the
# portraits really are drawn **black**, as the remake already did.
_PORTRAIT_SLOTS = (29, 30, 31, 32, 33, 34, 35)
_SPIRAL_START_COLOUR = 8      # line 150 `W=7` then line 170 `W=W+1`
_SPIRAL_ROWS, _SPIRAL_COLS = 25, 40
_SPIRAL_T1, _SPIRAL_T2 = 39, 25
# The reveal rates below are **derived from one live measurement**, not
# estimated. `[C-live]` the GREEN VALLEY screen: the spiral takes ~11.0 s for
# the 1804 POKEs its BASIC performs = 6.10 ms per POKE, which gives the border
# (260 POKEs) 1.585 s = 48 frames at 30 fps. The centre-out text is PRINTs, not
# POKEs, so it has its own anchor: ~2.2 s for 12 steps = 5.5 frames.
# Derivation: DISCOVERIES D-183, D-142.
#: **Front-end animation speed, player-directed (DISC-211).** Applied to the
#: *frame counter* the loader and WELCOME reveals read, never to the constants
#: below — those are `[C-live]` measurements and must keep saying what the
#: machine actually did.
#:
#: Scaling the frame rather than the rate also avoids an integer-rounding trap:
#: dividing `_TEXT_REVEAL_RATE` (6 frames) by 1.25 rounds to 4, which is 33%
#: faster, not 20%. Scaling the input keeps the ratio exact.
FRONTEND_SPEEDUP = 1.25        # 1.25x = each animation takes 80% as long

_BASIC_POKE_S = 11.0 / 1804.0          # [C-live D-142] / the counted POKEs
_TEXT_REVEAL_STEP_S = 2.2 / 12.0       # [C-live D-142] the residual / 12 steps
_TEXT_REVEAL_RATE = max(1, round(_TEXT_REVEAL_STEP_S * _FRAME_HZ))
#: **PV-27 / D-183** - derived, not assumed: the MARQUIE routine's 260 POKEs
#: at the measured 6.10 ms each is 1.585 s, i.e. 47.6 frames at `_FRAME_HZ`.
_BORDER_REVEAL_POKES = 40 * 2 + 25 * 4 + 40 * 2      # lines 3010/3020-3030/3040

_CELL = 36  # map grid cell size (unscaled px)
_JONES_X_START, _JONES_X_END, _JONES_X_STEP = 0x00, 0xF0, 4
# The captured backdrop's left columns are the ship map; the rest is the
# CONTROL panel's static labels, cropped off so the two don't overlap.
_MAP_COLS = 30
