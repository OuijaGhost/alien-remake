"""C64 colour indices — what colour RAM actually holds.

Split out of :mod:`alien_remake.render.c64` (DISC-249), which was two things
under one name: a **palette** (the Colodore RGB values, a rendering choice that
could be swapped for VICE's older one without changing a single fact about the
game) and this — the hardware's sixteen colour numbers, which are ROM truth and
appear directly in the decoded tables (`$7000`, `$7440`, `paint_map_colors
$7993`).

Only the second belongs below the render boundary. :mod:`alien_remake.screens`
stores indices rather than RGB precisely so it does not depend on a palette,
and it was reaching up into ``render`` for these names to do it — an import
that ran backwards and was only safe because ``render/__init__.py`` is
deliberately pygame-free.

``render.c64`` re-exports every name here, so ``c64.WHITE`` keeps working at its
~120 call sites; that direction (render -> screens) is the correct one.
"""

from __future__ import annotations

# Named colour indices used across the renderer (see module docstring).
BLACK = 0
WHITE = 1
RED = 2             # instructions-screen "A L I E N" title letters
CYAN = 3            # front-end prompt text ("CHOOSE ONE OF THE ABOVE")
PURPLE = 4
GREEN = 5           # the map field ($D800 colour RAM over the map columns)
BLUE = 6            # the border ($D020); "LOADING MENU" / "LOADING…" cards
YELLOW = 7
ORANGE = 8
LIGHT_RED = 10      # get / leave / special band
LIGHT_GREEN = 13    # use band
LIGHT_BLUE = 14     # move-to band
LIGHT_GREY = 15     # header / status band
