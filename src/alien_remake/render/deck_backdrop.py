"""Real per-deck map art decoded from captured screen-RAM dumps.

A fidelity fix to the renderer's map
view was a uniform grid of identical placeholder tiles, which looks nothing
like the real game. `docs/reference/{upper,middle,lower}deck_0400.bin` are VICE
captures of C64 screen RAM (`$0400-$07E7`) taken while each deck's map screen
was on-screen in the real game — an **oracle input**, exactly like the deck
screenshots `core/nostromo.py` was transcribed from (DECISIONS D-010 #2), except
here we have the exact bytes instead of eyeballed pixels. A screen-RAM byte is a
direct index into the loaded character set, so decoding is a lossless lookup
into the same 256-glyph charset `alientools.charset` already extracts from
ALIEN's own `$2000-$3FFF` (SG) — no guessing which glyph is a wall or a floor
tile the way the placeholder had to.

Only the **top 17 rows** (0-16) of each 40x25 capture are reused: that's the
ship map plus the CONTROL panel's row labels, which never change between game
states. Rows 17-24 hold a *dynamic* status/message snapshot from whatever
moment the capture was taken (e.g. one dump reads "... has been killed by the
ALIEN") — baking that in verbatim would misleadingly show a fixed message
regardless of live game state, so the renderer draws its own live status text
there instead.

**Per-cell colour: CONFIRMED uniform, not per-glyph (D-029, 2026-07-24).**
`docs/reference/colors.bin` is a VICE colour-RAM (`$D800-$DBE7`) capture in
the same format as the screen-RAM dumps above (2-byte load address + 1000
bytes, 40x25). Decoding it row-by-row shows the **entire 30-column map field
is flat colour 5 (green) on every one of the top 17 rows, regardless of which
glyph occupies each cell** (wall-stroke cells and floor cells alike) — i.e.
there is no per-glyph colour variation to recover; a single flat green really
is the real screen's behaviour, not a placeholder simplification. This
matches the disassembly: `draw_deck_map_body ($73D0)`/the control-panel
colour setup (`$7400-$7423`, `$7993 paint_map_colors`) fill colour RAM in
bulk per *region* (`STA ($ptr),Y` loops over a fixed row/col span), never
branching on the screen-code byte being painted — so bulk-region colour fills
are how the original does it too. The CONTROL-panel's per-band colours
(light-blue move-to, light-green use, light-red get/leave/special, light-grey
header/status) are the other bands in the same capture and are already wired
in `pygame_app.py`'s ``_BAND_COLOUR`` / `c64.py`. This closes the "per-cell
colour/marker-alignment" half of FV-2.14 — see `DISCOVERIES.md` D-029.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SCREEN_COLS = 40
SCREEN_ROWS = 25
BACKDROP_ROWS = 17  # rows 0-16: the ship map + the always-static CONTROL labels.

# Deck index -> capture filename under docs/reference/ (oracle captures, not
# derived from the .nib — see the module docstring).
_DECK_FILES: dict[int, str] = {
    0: "upperdeck_0400.bin",
    1: "middledeck_0400.bin",
    2: "lowerdeck_0400.bin",
}


@dataclass(frozen=True)
class DeckBackdrop:
    """One deck's decoded screen-code grid: ``codes[row][col]`` is a charset index."""

    codes: tuple[tuple[int, ...], ...]  # BACKDROP_ROWS rows of SCREEN_COLS codes each


def decode_screen_dump(data: bytes) -> tuple[tuple[int, ...], ...]:
    """Decode a VICE ``save`` capture into a ``BACKDROP_ROWS`` x ``SCREEN_COLS`` grid.

    VICE's monitor ``save`` prepends a 2-byte little-endian load address (here
    ``$0400``, screen RAM); stripped here since the byte *position* already
    encodes row/column for a standard 40-column text screen.
    """
    body = data[2:] if len(data) >= 2 else data
    screen = body[: SCREEN_COLS * SCREEN_ROWS]
    return tuple(
        tuple(screen[r * SCREEN_COLS : (r + 1) * SCREEN_COLS])
        for r in range(BACKDROP_ROWS)
    )


def load_deck_backdrops(reference_dir: Path) -> dict[int, DeckBackdrop]:
    """Load whichever deck captures exist under ``reference_dir``.

    Decks with no matching file are simply absent from the result (the renderer
    falls back to the placeholder grid for those) rather than raising — the
    captures are optional oracle material, not a required asset.
    """
    out: dict[int, DeckBackdrop] = {}
    for deck, filename in _DECK_FILES.items():
        path = reference_dir / filename
        if not path.exists():
            continue
        out[deck] = DeckBackdrop(codes=decode_screen_dump(path.read_bytes()))
    return out
