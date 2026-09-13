"""The C64 16-colour palette + the game's real screen colours (decoded).

Colours are the **Colodore** palette (GTK3VICE 3.x's default), so the remake's
output matches the reference screenshots the user captured. The per-screen
colour assignments were read from the live captures the user provided —
``docs/reference/vic.bin`` (VIC-II registers: border = blue, background =
black) and ``docs/reference/colors.bin`` (colour RAM: the map field is green,
and the CONTROL panel is horizontal bands — light-blue over the move-to list,
light-green/white for use, light-red for get/leave/special, and grey/green/
orange/yellow for the bottom status lines).
"""

from __future__ import annotations

# Colodore palette, index 0-15 -> RGB (VICE default).
PALETTE: tuple[tuple[int, int, int], ...] = (
    (0x00, 0x00, 0x00),  # 0  black
    (0xFF, 0xFF, 0xFF),  # 1  white
    (0x81, 0x33, 0x38),  # 2  red
    (0x75, 0xCE, 0xC8),  # 3  cyan
    (0x8E, 0x3C, 0x97),  # 4  purple
    (0x56, 0xAC, 0x4D),  # 5  green
    (0x2E, 0x2C, 0x9B),  # 6  blue
    (0xED, 0xF1, 0x71),  # 7  yellow
    (0x8E, 0x50, 0x29),  # 8  orange
    (0x55, 0x38, 0x00),  # 9  brown
    (0xC4, 0x6C, 0x71),  # 10 light red
    (0x4A, 0x4A, 0x4A),  # 11 dark grey
    (0x7B, 0x7B, 0x7B),  # 12 grey
    (0xA9, 0xFF, 0x9F),  # 13 light green
    (0x70, 0x6D, 0xEB),  # 14 light blue
    (0xB2, 0xB2, 0xB2),  # 15 light grey
)

# The sixteen colour *numbers* are ROM truth, not a rendering choice, so they
# live below the render boundary in `screens.colours` (DISC-249). Re-exported
# here because `c64.WHITE` is spelled that way at ~120 call sites, and because
# a palette module is a reasonable place to look for them.
from ..screens.colours import (
    BLACK, BLUE, CYAN, GREEN, LIGHT_BLUE, LIGHT_GREEN, LIGHT_GREY, LIGHT_RED,
    ORANGE, PURPLE, RED, WHITE, YELLOW,
)

#: This module's surface: the palette and `rgb()` are its own, the sixteen
#: colour names are re-exported from `screens.colours`. Listing them is what
#: makes the re-export explicit under `strict = true`.
__all__ = [
    "PALETTE", "rgb",
    "BLACK", "BLUE", "CYAN", "GREEN", "LIGHT_BLUE", "LIGHT_GREEN",
    "LIGHT_GREY", "LIGHT_RED", "ORANGE", "PURPLE", "RED", "WHITE", "YELLOW",
]


def rgb(index: int) -> tuple[int, int, int]:
    """RGB for a C64 colour index (0-15)."""
    return PALETTE[index % 16]
