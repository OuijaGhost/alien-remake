"""The `screen_fx` option: an optional terminal-readout effect for the boot
report screen only. **Not the original.**

The disk draws every screen whole, in one frame — there is no transition of
any kind to trace this to, and `Screen.BOOT` itself (the startup diagnostics
card) has no ROM counterpart at all. This exists because the owner asked for
something in the general shape of an old terminal readout (per the owner's
own description of the technique behind `load.mov`, a piece of unrelated
third-party footage reviewed only for that technique and never reproduced
here): the picture growing in from a thin CRT-power-on band with a settling
degauss shake, phosphor-yellow text typed out a character at a time behind a
blinking cursor and a trailing streak, static that throws in letters as well
as blocks, and a command-style prompt once revealed.

**Scoped to BOOT only (2026-09-05).** An earlier pass also wired this into
the title and ending screens; the owner's own words narrowed it back down:
"the intro animation should just be for the initial screen of dos text."
Those two screens draw exactly as they did before this option existed.

All pure functions of the tick count, so a screen that redraws from scratch
every frame (as this renderer already does everywhere else) needs no extra
state beyond the tick count itself:

* :func:`reveal_position` — where the "typing" has reached.
* :func:`apply_terminal_fx` — masks everything after that position, and
  draws the cursor and the trailing streak there.
* :func:`glitch_cell_positions` / :func:`glitch_letter_cells` — a fading
  burst of static (blocks and, separately, actual letters — the caller draws
  the letters, since this module has no font to blit one with) over the
  first `constants.SCREEN_FX_GLITCH_TICKS` ticks.
* :func:`apply_power_on` — the CRT stretch-in and degauss shake, applied
  once near the start of the screen's life, over whatever the caller has
  already drawn (typed text, glitch, streak and all).
* the prompt line itself is drawn by the caller (`render/frontend.py`'s
  `_draw_boot`) as ordinary text, once revealed — a plain string is not this
  module's concern.

Pure presentation, gated behind the `screen_fx` option (off by default, like
every other remake-only addition) and applied as a mask/overlay/transform
over an otherwise unchanged draw — it never changes what the screen says,
only how much of it is visible, what sits on top of it, and how the whole
picture is warped, on a given frame. `core/flow.py` counts the ticks this
reads (`GameFlow._screen_ticks`, reset whenever a screen is entered).
"""

from __future__ import annotations

import pygame  # the project's one optional runtime dependency (D-009)

from ..core import constants

#: A handful of desaturated tones — CRT snow is grey/white noise, not the
#: screen's own colour palette, so a glitch cell reads as static rather than
#: as corrupted content.
_GLITCH_PALETTE: tuple[tuple[int, int, int], ...] = (
    (60, 60, 60), (140, 140, 140), (200, 200, 200), (90, 110, 90),
)

#: What a glitch *letter* is drawn from — upper-case and digits (the game's
#: own charset), plus a few block/symbol glyphs so it reads as corrupted
#: readout noise rather than a word trying to form.
_GLITCH_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&@*+="

#: Phosphor yellow — the owner's own reference: "the text should be yellow
#: like in the original video." Distinct from the C64 palette's own YELLOW
#: (used elsewhere for player-facing UI) so this screen reads as its own
#: amber terminal rather than borrowing the game's UI colour by coincidence.
PHOSPHOR_YELLOW: tuple[int, int, int] = (255, 210, 60)

#: The trailing streak's colour — "hot yellowish green phosphor lines,"
#: brighter and greener than the text itself so it reads as a scan
#: highlight passing through, not as differently-coloured text.
STREAK_COLOUR: tuple[int, int, int] = (210, 255, 120)

#: A bog-standard linear congruential generator, chosen only because it is
#: deterministic and needs no `random.Random` instance threading through
#: render code that has none. The same tick always produces the same cells,
#: which is what makes this testable and makes two runs at the same tick
#: look identical.
_LCG_A, _LCG_C, _LCG_M = 1103515245, 12345, 2**31


def reveal_position(ticks: int, cols: int) -> tuple[int, int]:
    """Row and column of the typewriter's cursor after ``ticks`` ticks.

    Every column of every row before this position is revealed; this column
    onward, on this row, and every row after it, is not. Grows
    `constants.SCREEN_FX_CHARS_PER_TICK` characters per tick in reading
    order (left to right, top to bottom) — a straight character count, not a
    per-row reset, so it does not matter how many of a row's columns
    actually carry text: blank columns cost the same one tick apiece as
    lettered ones, same as a real typewriter would.
    """
    total = max(0, ticks) * max(1, constants.SCREEN_FX_CHARS_PER_TICK)
    return divmod(total, max(1, cols))


def fully_revealed(ticks: int, total_rows: int, cols: int) -> bool:
    """Whether the whole grid has finished revealing."""
    row, _col = reveal_position(ticks, cols)
    return row >= total_rows


def glitch_cell_positions(
    tick: int, cols: int, rows: int, count: int
) -> list[tuple[int, int]]:
    """``count`` deterministic (row, col) cells to show as static on ``tick``.

    Deterministic per tick — a fixed LCG seeded from the tick number — rather
    than drawn from an RNG object, since none of this module's callers carry
    one (screen draws have no `Simulation` to hand it a seeded generator).
    """
    total = max(1, cols * rows)
    seed = (tick * 2654435761 + 0x9E3779B1) & 0xFFFFFFFF
    out: list[tuple[int, int]] = []
    x = seed
    for _ in range(max(0, count)):
        x = (_LCG_A * x + _LCG_C) % _LCG_M
        row, col = divmod(x % total, cols)
        out.append((row, col))
    return out


def glitch_letter_cells(
    tick: int, cols: int, rows: int, count: int
) -> list[tuple[int, int, str]]:
    """``count`` deterministic (row, col, letter) glitch letters on ``tick``.

    A sibling of :func:`glitch_cell_positions` with a different LCG seed (so
    the two do not land on the same cells every time) and a character
    attached — "random letters as well as blocks," the owner's own words.
    This module has no font to draw one with, so the caller
    (`render/frontend.py`'s `_draw_boot`) does the actual blitting; this only
    says which cells and which letters.
    """
    total = max(1, cols * rows)
    seed = (tick * 2246822519 + 0x85EBCA6B) & 0xFFFFFFFF
    out: list[tuple[int, int, str]] = []
    x = seed
    for _ in range(max(0, count)):
        x = (_LCG_A * x + _LCG_C) % _LCG_M
        row, col = divmod(x % total, cols)
        x = (_LCG_A * x + _LCG_C) % _LCG_M
        letter = _GLITCH_LETTERS[x % len(_GLITCH_LETTERS)]
        out.append((row, col, letter))
    return out


def apply_terminal_fx(
    surface: "pygame.Surface",
    cell: int,
    ticks: int,
    total_rows: int,
    total_cols: int,
    *,
    glitch: bool = True,
    cursor: bool = True,
) -> None:
    """Mask everything past the reveal position, then lay the glitch, the
    trailing streak and the cursor on top — in that order, so they draw over
    the masked (black) area rather than hidden by it. Glitch *letters* are
    not drawn here (see :func:`glitch_letter_cells`'s own docstring); the
    caller draws those itself, after this call.
    """
    row, col = reveal_position(ticks, total_cols)
    width, height = surface.get_width(), surface.get_height()

    if row < total_rows:
        # The cursor's own row: blank from its column onward.
        x0 = min(col, total_cols) * cell
        y0 = row * cell
        if x0 < width:
            surface.fill((0, 0, 0), (x0, y0, width - x0, cell))
        # Every row after it: blank entirely.
        y1 = (row + 1) * cell
        if y1 < height:
            surface.fill((0, 0, 0), (0, y1, width, height - y1))

    if glitch and ticks < constants.SCREEN_FX_GLITCH_TICKS:
        # Fades out as `ticks` climbs toward the ceiling - a burst at the
        # start of the screen, not a steady hum for its whole duration.
        remaining = constants.SCREEN_FX_GLITCH_TICKS - ticks
        count = remaining * 2
        for i, (grow, gcol) in enumerate(
            glitch_cell_positions(ticks, total_cols, total_rows, count)
        ):
            colour = _GLITCH_PALETTE[(grow + gcol + ticks + i) % len(_GLITCH_PALETTE)]
            surface.fill(colour, (gcol * cell, grow * cell, cell, cell))

    if row < total_rows and col > 0:
        # **The streak (2026-09-05), not the original.** "Hot yellowish
        # green phosphor lines streak across the image as the text forms on
        # each line." An additive glow trailing the last few columns of the
        # write head, not a flat overlay - `BLEND_RGB_ADD` brightens what is
        # already there (the just-typed characters) rather than covering it,
        # which is what makes it read as a scan highlight passing through
        # instead of a different-coloured stripe painted over the text.
        span = min(8, col)
        x0 = (col - span) * cell
        y0 = row * cell
        surface.fill(
            STREAK_COLOUR, (x0, y0, span * cell, cell),
            special_flags=pygame.BLEND_RGB_ADD,
        )

    if cursor and row < total_rows and col < total_cols:
        # A blinking underline, the conventional terminal cursor shape -
        # `constants.SCREEN_FX_CURSOR_BLINK_TICKS` ticks per half-cycle.
        on = (ticks // max(1, constants.SCREEN_FX_CURSOR_BLINK_TICKS)) % 2 == 0
        if on:
            x0, y0 = col * cell, row * cell
            surface.fill(
                (140, 220, 140), (x0, y0 + cell - max(1, cell // 6), cell, max(1, cell // 6))
            )


def apply_power_on(surface: "pygame.Surface", ticks: int) -> None:
    """The CRT power-on stretch and its settling degauss shake.

    "The animation should begin with a classic CRT turning off [sic: on]
    stretch of the image from small to filling the screen. Add the shake
    animation that looks like degaussing to this opening animation that
    settles quickly." (the owner's own words). Transforms whatever is
    already on ``surface`` — typed text, glitch, streak, all of it — rather
    than drawing anything of its own, so it has to run *last*, right before
    the caller's own `_present()`.

    Built standalone with plain `pygame.transform`/blit calls rather than
    reusing `render/crt.py`'s own `_degauss` (the deck-change transient this
    is modelled on): that one is a numpy pass over the *whole composited
    window*, gated behind the separate `crt` option being on at all, and
    this has to run whether or not it is.
    """
    stretch_ticks = constants.SCREEN_FX_STRETCH_TICKS
    shake_ticks = constants.SCREEN_FX_SHAKE_TICKS
    if ticks >= max(stretch_ticks, shake_ticks):
        return
    width, height = surface.get_width(), surface.get_height()
    frame = surface.copy()

    if ticks < stretch_ticks:
        # Grows from a thin band to full height - the reverse, frame for
        # frame, of the classic "tube collapsing to a dot" power-off shape.
        fraction = (ticks + 1) / stretch_ticks
        band_height = max(2, round(height * fraction))
        scaled = pygame.transform.scale(frame, (width, band_height))
        surface.fill((0, 0, 0))
        surface.blit(scaled, (0, (height - band_height) // 2))
        frame = surface.copy()  # what the shake pass below displaces

    if ticks < shake_ticks:
        # A decaying horizontal wobble - "settles quickly": straight-line
        # falloff to nothing by `shake_ticks`, alternating direction each
        # tick so it reads as a shudder rather than a slide in one direction.
        decay = 1.0 - (ticks / shake_ticks)
        amplitude = 5  # pixels, at ticks == 0
        offset = round(amplitude * decay) * (1 if ticks % 2 == 0 else -1)
        if offset:
            surface.fill((0, 0, 0))
            surface.blit(frame, (offset, 0))
