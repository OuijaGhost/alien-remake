"""The duct map — the screen shown while a character is inside the ducting.

R-41 / D-091. The player remembered "a different map with a different layout"
when crew entered the ducts, and that is exactly what the ROM does:
`select_menu_template ($817D)`, reached **only** from the in-duct path, picks
one of three 30x18 screen templates (`$A956` / `$A9C4` / `$AA6E`) from the
per-room table at `$7569` and paints it with `render_message ($7F0D)`. It is
not the deck plan — the duct partition and the deck partition agree for only
12 of 34 rooms, and the templates are pipe diagrams rather than room outlines.

The decode is cross-validated three ways (`alientools.gamedata.decode_duct_map`):
every one of the 34 room positions from `$80B1`/`$80D3` lands on the templates'
dedicated node glyph `$E6`, and each template carries exactly as many nodes as
it has rooms assigned (9 / 16 / 9).

Why most of the map is invisible
--------------------------------
`clear_map_colors ($7EE5)` blacks out the whole 30x18 colour area first, and
only then does `mark_exits ($7F78)` light anything up. Since the background is
black too, **the template is drawn in full but you only see the part you can
reach**: your own node in white, and the pipe runs leading away from it in
light blue. That is what makes the duct view feel sparse and disorienting
compared with the deck plan, and it is why this module returns a *colour* grid
rather than a visibility mask — the ROM's mechanism is colour, not clipping.
"""

from __future__ import annotations

from . import gamedata_snapshot as data

#: `$7F7D LDA #$01` — the character's own node.
COLOUR_HERE = 0x01
#: `$7F85 LDA #$0E` — the reachable pipe runs. Both values reach the colour
#: RAM through `set_color_at_ptr ($7FC0)`, which is **self-modifying**: the
#: `STA $7FC9` patches the operand of the `LDA #$0E` at `$7FC8`, so one routine
#: paints in whichever colour was last stashed.
COLOUR_REACHABLE = 0x0E
#: Unlit cells. Black on a black background — drawn, but invisible.
COLOUR_HIDDEN = 0x00

#: `$8005 CMP #$C7 / $8007 BCC` — a character **below** `$C7` is pipe and the
#: walk continues through it; `$C7` and above **stops** the walk. The templates
#: use only ten glyphs and the split is exactly right: `$C0`-`$C5` are the pipe
#: and corner pieces (179 of the 241 painted cells), while `$C7`, `$E6` (the
#: room node), `$E7` and `$E8` are terminators. So a run of light travels along
#: the ducting and halts at the next room.
RUN_STOPS_AT_LEAST = 0xC7

#: `$6500` — the direction just travelled, as the bit `mark_exits` sets before
#: each probe: 1 = up, 2 = right, 4 = down, 8 = left.
_UP, _RIGHT, _DOWN, _LEFT = 1, 2, 4, 8
_DELTA: dict[int, tuple[int, int]] = {
    _UP: (-1, 0), _RIGHT: (0, 1), _DOWN: (1, 0), _LEFT: (0, -1),
}
#: The four probes `mark_exits ($7F8F`-`$7FBC)` fires from the node, in order.
#: Order is preserved because a later probe may re-colour a cell an earlier one
#: already lit.
_PROBES: tuple[int, ...] = (_UP, _RIGHT, _DOWN, _LEFT)


def template_for(room_index: int) -> tuple[tuple[int, ...], ...]:
    """The 30x18 screen-code grid room ``room_index`` shows in the ducts."""
    return data.DUCT_MAP_TEMPLATES[data.DUCT_MAP_ROOM_TEMPLATE[room_index]]


def node_cell(room_index: int) -> tuple[int, int]:
    """``(row, col)`` of the room's node on its own template."""
    return data.DUCT_MAP_ROOM_CELL[room_index]


def colour_grid(room_index: int) -> tuple[tuple[int, ...], ...]:
    """Colour RAM for the duct map as `mark_exits ($7F78)` leaves it.

    Black everywhere (`clear_map_colors $7EE5`), then the character's node in
    white, then a light-blue trace out of the node in each of the four
    directions. The trace is not a straight line: `color_if_char ($7FFE)` is a
    **pipe follower** that turns corners, so what lights up is the actual duct
    run leading away from you, all the way to the next room node.
    """
    grid = template_for(room_index)
    rows, cols = len(grid), len(grid[0])
    colours = [[COLOUR_HIDDEN] * cols for _ in range(rows)]
    row, col = node_cell(room_index)
    colours[row][col] = COLOUR_HERE
    for probe in _PROBES:
        drow, dcol = _DELTA[probe]
        _follow(grid, colours, row + drow, col + dcol, probe)
    return tuple(tuple(r) for r in colours)


def _follow(
    grid: tuple[tuple[int, ...], ...],
    colours: list[list[int]],
    row: int,
    col: int,
    came: int,
) -> None:
    """Trace one duct run — `color_if_char ($7FFE)` and its `$800A` loop.

    ``came`` is the ROM's `$6500`: the direction just travelled. At each step
    the follower tries **up, right, down, left in that order**, skipping the
    one that would double back (`$800C CMP #$04` skips up, `$802C CMP #$08`
    skips right, `$804C CMP #$01` skips down). Left is never skipped, because
    having moved left sets `$6500 = 8`, which already blocks right.

    Two faithful details worth keeping:

    * a blank cell **ends** the probe (`$7FFE BEQ`), and the ROM undoes the
      peek before trying the next direction (`$8027 JSR peek_down` etc.);
    * the final left branch (`$806D`) colours **unconditionally**, with no
      blank check — so the ROM would happily walk off into empty map. A
      ``seen`` guard is added here; on the real templates it never triggers,
      but reproducing an unbounded loop is not fidelity.
    """
    rows, cols = len(grid), len(grid[0])

    def char_at(r: int, c: int) -> int:
        return grid[r][c] if 0 <= r < rows and 0 <= c < cols else 0

    char = char_at(row, col)
    if char == 0:                       # `$7FFE BEQ $8009`
        return
    colours[row][col] = COLOUR_REACHABLE
    if char >= RUN_STOPS_AT_LEAST:      # `$8007 BCC` — only below $C7 walks on
        return

    seen = {(row, col)}
    # `$800A`: the direction that would double back, per the ROM's three tests.
    # Keyed by the direction being *tried*, valued by the `$6500` that skips
    # it: `$800C` skips up when came==down, `$802C` skips right when
    # came==left, `$804C` skips down when came==up. Left has no test.
    blocked_by = {_UP: _DOWN, _RIGHT: _LEFT, _DOWN: _UP}
    while True:
        for direction in _PROBES:
            if blocked_by.get(direction) == came:
                continue
            drow, dcol = _DELTA[direction]
            nrow, ncol = row + drow, col + dcol
            char = char_at(nrow, ncol)
            if char == 0 and direction is not _LEFT:
                continue                # blank: undo the peek, try the next
            if not (0 <= nrow < rows and 0 <= ncol < cols):
                return
            colours[nrow][ncol] = COLOUR_REACHABLE
            if char >= RUN_STOPS_AT_LEAST or (nrow, ncol) in seen:
                return
            row, col, came = nrow, ncol, direction
            seen.add((row, col))
            break
        else:
            return


def lit_cells(room_index: int) -> tuple[tuple[int, int, int, int], ...]:
    """Every visible cell as ``(row, col, screen_code, colour)``.

    Cells left black are omitted: they are painted by the ROM but invisible
    against the black background, so a renderer that skips them produces the
    same picture with less work.
    """
    grid = template_for(room_index)
    colours = colour_grid(room_index)
    return tuple(
        (r, c, grid[r][c], colours[r][c])
        for r in range(len(grid))
        for c in range(len(grid[0]))
        if colours[r][c] != COLOUR_HIDDEN and grid[r][c] != 0
    )
