"""Decode the real game-data tables out of ``ALIEN.prg`` (the decompile's truth).

This module is the code-faithfulness bridge the remake was missing: earlier
the remake first modelled the game from the *manual* plus guesses, but the PRG
itself carries the actual tables. Each address below was located by
cross-referencing the disassembly (``out/ALIEN.asm``) with live VICE RAM
captures in ``docs/reference/`` and verified against at least one independent
signal (see ``docs/re/GAMEDATA.md`` for the full evidence trail). Summary of
what lives where:

===========  ==================================================================
``$A71C``    36 room names, 10-byte screen-code records. Ids 0-35 are the room
             numbers used everywhere else (crew/alien locations, item rooms).
             Verified: the endgame RAM capture shows ``MOVE TO: SHUTTLEBAY`` on
             screen with the ordered crew member's location byte = ``$22`` = 34
             = SHUTTLEBAY in this table.
``$80D3``    **NOT a deck table (D-116).** The high byte of each room marker's
             screen address (`$81C9 LDA $80D3,Y -> $FC`, paired with `$80B1`
             into `$FB`); its 4/5/6 values are screen *pages*. The real per-room
             deck/screen index is **`$7569`** (9/16/9), which `$76BB` reads to
             choose which deck plan to draw.
``$80F5``    Four 34-entry compass-neighbor tables (N/S/E/W, 34 bytes apart,
``$8117``    directly after the words NORTH/SOUTH/EAST/WEST/IN DUCT at $8080).
``$8139``    "No exit" is encoded as the room's own id. Every edge is mutual as
``$815B``    an undirected graph; direction-bent pairs (a-E->b, b-N->a) that
             cross decks are the deck-plan ladders.
``$8676``    34-entry per-room grille-present table (every room but CORRIDOR 6).
``$7C72``    10 item-type names, 10-byte records (+ an 11th record "SPECIAL").
``$82CF``    20 item instances: type ids (1-10).
``$82E3``    ...their start/current rooms. Verified: instances 13-15 are the
             three LASER PISTOLS in the ARMOURY; the code reads the two
             TRACKERS' and the CAT BOX's slots at fixed addresses
             ($82E9/$82EA/$82F4).
``$7935``    9 character location slots: 0 = the Alien, 1-7 = crew in CONTROL-
             panel order (DALLAS KANE RIPLEY ASH LAMBERT PARKER BRETT), 8 =
             Jones. $FE = removed/dead-without-a-body.
``$6586``    **NOT walk durations (D-122).** The pristine backup of the runtime
             block at `$656E` — `sub_beep ($6598)` copies 21 bytes from `$6583`
             over it at game start, and the crew's starting composure (`$6571`)
             lives inside. Its 4/4/3/4/3/4/3 are byte-identical to `START_FEAR`
             for that reason. The real move timer is `$7B69` + `$4042` (D-112).
``$6581``    The Alien's compass-move duration: 70 units.
``$7CEA``    4 physical-status words (O.K./WOUNDED/COLLAPSED/DEAD) then 5
             morale words (CONFIDENT/STABLE/UNEASY/SHAKEN/BROKEN).
``$887E``    The RNG's 16-byte output table (identity 0-15 -> uniform 4-bit).
``$7A3A``    Five 36-entry routing tables (precomputed next-room hops; exact
             selection semantics not yet pinned down).
===========  ==================================================================

Timing facts recovered alongside (not tables, but constants callers need):
the raster/CIA IRQ divider at $4D19 reloads ``#$08`` and fires on the wrap
below zero -> the animation/sound tick is every **9** jiffies, and the four
routines it calls are sprite/sound updates only. World pacing is the
free-running main loop at $719D decrementing the per-character timers, which
are loaded by `$7B69` (a flat `#$40`) plus `compute_action_delay ($4042)`.

Read-only: operates on already-extracted PRG bytes; never touches the .nib.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --- Table addresses (see module docstring & docs/re/GAMEDATA.md) -------------

LOAD_ADDRESS = 0x2000          # ALIEN.prg loads here; code entry is $4000.

# **[C $7948] D-123 — the room-name table has a GAP, and one special case.**
# `set_room_screen_ptr` does NOT index a flat 36-record table. It branches:
#
#     7948  ASL A / LSR A          ; strip the in-duct bit
#     794E  CMP #$11 / BCC $7984   ; rooms 0-16  -> base $A71C
#     7952  CMP #$22 / BEQ $7956   ; room 34     -> pointer $5DD1 ("NARCISSUS")
#     795F                          ; rooms 17-33 -> base $A7DA
#
# `$A71C + 17*10` would be `$A7C6`, but the ROM uses **`$A7DA`** — two records
# further on. Those two filler records are what a flat read mistook for the
# duplicate "OTHER LIST" rooms (the ones the snapshot had to suffix `_1`/`_2`).
# They are not rooms, and reading flat shifted **every name from 17 up by two**.
ROOM_NAMES_ADDR = 0xA71C           # rooms 0-16
ROOM_NAMES_HIGH_ADDR = 0xA7DA      # rooms 17-33 (after the 2-record gap)
ROOM_NAMES_SPLIT = 0x11            # $794E CMP #$11
ROOM_NARCISSUS_ID = 0x22           # $7952 CMP #$22
ROOM_NARCISSUS_NAME_ADDR = 0x5DD1  # $7956 — its own pointer
ROOM_NAME_LEN = 10
ROOM_COUNT = 35                    # ids 0-34; 34 is the Narcissus
MAPPED_ROOM_COUNT = 34         # rooms with deck/neighbor/grille entries.

#: **[C $76BB / $511F] D-116, applied 2026-08-08.** The per-room deck index,
#: values **0/1/2**, distribution 9/16/9. `$76BB LDA $7569,Y` and
#: `menu_option_dispatch ($511F)` both read it to choose which of the three deck
#: plans at `$A000`/`$A21C`/`$A438` (UPPER/MIDDLE/LOWER DECK) to paint, and
#: `select_menu_template ($817D)` reads the same byte to choose that deck's duct
#: sheet — one table, two template sets, both per-deck.
#:
#: This used to read `$80D3`, whose 4/5/6 values are the **screen page** of the
#: room's marker on the duct map (`$81C9 LDA $80D3,Y -> $FC`), not a deck. The
#: docstring above has recorded that since D-116; the code never followed. It
#: agreed with the real decks for only 12 of 34 rooms, which is why crew
#: appeared to vanish when they walked between decks.
DECK_TABLE_ADDR = 0x7569       # values 0/1/2
# **[C $40B8-$40FA] P-2, 2026-08-02: EAST and SOUTH were swapped here.**
# The routine that reports which way a room lies tests each table in turn and
# copies the matching word from the `$8080` block, which settles the order:
#   $80F5 matches -> copies $8081 "NORTH   "
#   $8117 matches -> copies $8095 "EAST    "   (was labelled SOUTH)
#   $8139 matches -> copies $808B "SOUTH   "   (was labelled EAST)
#   $815B -> WEST by elimination
# Connectivity was unaffected (the neighbour *set* per room is identical), but
# every compass label the remake produced was wrong.
NORTH_ADDR = 0x80F5
EAST_ADDR = 0x8117
SOUTH_ADDR = 0x8139
WEST_ADDR = 0x815B
GRILLE_ADDR = 0x8676

# The first 10-char record at $7C72 is blank (type ids are 1-based and the
# blank record absorbs index 0); real names start one record in.
ITEM_NAMES_ADDR = 0x7C72 + 11
ITEM_NAME_LEN = 10
ITEM_TYPE_COUNT = 10           # + an 11th "SPECIAL" record (a menu label).
ITEM_TYPES_ADDR = 0x82CF
ITEM_ROOMS_ADDR = 0x82E3
ITEM_COUNT = 20

CHAR_LOCS_ADDR = 0x7935        # 9 slots: alien, 7 crew, Jones.
# **[C $659A] D-122 — MISLABELLED. `$6586` is not a walk-ticks table.**
# `sub_beep ($6598)` copies 21 bytes from `$6583` to `$656E` at game start, so
# this region is the pristine **backup** of the runtime state block — and the
# crew's starting composure (`$6571`) sits inside it. That is why these bytes
# (4,4,3,4,3,4,3) are byte-identical to `START_FEAR` read from `$7D5D`: they
# are the same values seen twice.
#
# **Nothing in the ROM reads `$6586` as a duration.** The real room-move timer
# is `$7B69`'s flat `#$40` plus `compute_action_delay ($4042)` (D-112). The
# field is still decoded and emitted so the snapshot stays a faithful dump of
# the region, but callers must not treat it as timing.
WALK_TICKS_ADDR = 0x6586       # [?] backup block, NOT per-character durations.
ALIEN_MOVE_TICKS_ADDR = 0x6581

STATUS_WORDS_ADDR = 0x7CEA     # 4 x 10 bytes
MORALE_WORDS_ADDR = 0x7CEA + 4 * 10  # 5 x 10 bytes
RNG_TABLE_ADDR = 0x887E        # 16 bytes
# The five Alien surface route tables. Their start addresses are NOT uniformly
# spaced (strides 36/36/35/35 — verified from the loads in `alien_choose_move`
# $8A36, DISASSEMBLY §8.10), so they are listed explicitly rather than computed
# from a single base + stride. Each holds one next-room id per mapped room.
ROUTING_ADDRS = (0x7A3A, 0x7A5E, 0x7A82, 0x7AA5, 0x7AC8)


def surface_exits(routing: tuple[tuple[int, ...], ...], room: int) -> tuple[int, ...]:
    """The rooms a character on the SURFACE may walk to — **[C $7860], P-1**.

    This is the game's own "move to" list, and it is built from the five
    **routing** tables, *not* the compass tables. `$779C` chooses between the
    two menus on the in-duct flag: on the surface it reaches `$7860` (here);
    in a duct it reaches `$81EF` (the compass tables).

    The construction is reproduced exactly, because its quirks are visible:

    * the first table's entry is added **unconditionally** (`$7868`);
    * each later entry is compared only against the **immediately preceding
      accepted** value (`CMP $7947`) and skipped if equal — so a value that
      matches an *earlier* one still gets through;
    * hitting the room's own id **ends the whole list** (`CMP $7934 / BEQ
      $7908`) rather than skipping that table.

    The result is a corridor-hub deck plan: ordinary rooms open onto a single
    corridor, corridors fan out to several rooms. Lists run 1-5 entries.
    """
    out = [routing[0][room]]
    prev = out[0]
    for table in routing[1:]:
        value = table[room]
        if value == prev:
            continue
        if value == room:
            break
        out.append(value)
        prev = value
    return tuple(out)

# **The DUCT network** (D-083). Four tables, one per compass direction, each
# holding one neighbour room id per mapped room. A **self-reference means "no
# duct exit that way"**. These connect rooms to rooms *directly* — there are no
# junction nodes in the original at all.
#
# The direction assignment is not guessed: `$40B8`-`$40FA` tests a character's
# room against each table in turn and prints the matching direction word from
# the `$8080` block (" NORTH   " / " EAST    " / " SOUTH   " / " WEST    ").
# The same four tables drive the in-duct MOVE TO menu (`$81EF`-`$8271`) and the
# Alien's own duct hops (`$8AA2`-`$8ACB`).
DUCT_ADDRS: tuple[tuple[str, int], ...] = (
    ("north", 0x80F5),
    ("east", 0x8117),
    ("south", 0x8139),
    ("west", 0x815B),
)

# **The SHORT SCENARIO's fixed setup** (D-085). `$604F`, reached only from the
# Ctrl+2 branch (`$5F4E`), overwrites the randomised opening with a scripted
# one: `$6064` pins the victim to KANE (2) and `$6069` the android to ASH (4),
# then copies four 7-entry tables over the crew arrays. So SHORT is not a
# shorter FULL — it is a *fixed* scenario, which is why the earlier conclusion
# that `GameMode` had no mechanical effect was wrong.
SHORT_ADDRS: tuple[tuple[str, int], ...] = (
    ("locations", 0x608C),         # -> $7936,Y  (character slots 1-7)
    ("health", 0x6093),            # -> $7D46,Y
    ("composure", 0x609A),         # -> $7D56,Y
    ("composure_mirror", 0x60A1),  # -> $6572,Y
)
# `$604F` also starts two crew **already in the ducts** ($605A LDA #$01 ->
# $6502 and $6508, i.e. the `$6501` in-duct array at slots 1 and 7 = DALLAS and
# BRETT) and pulls three items into COMMDCENTR ($6051 LDA #$06 -> $82EA/$82F3/
# $82F4, i.e. the `$82E3` item-room array at instances 7/16/17 = a TRACKER, the
# NET and the CAT BOX).
SHORT_DUCT_SLOTS: tuple[int, ...] = (1, 7)          # $605C/$605F
SHORT_ITEM_MOVES: tuple[tuple[int, int], ...] = (   # (item instance, room)
    (7, 6), (16, 6), (17, 6),
)
SHORT_VICTIM_SLOT = 2        # $6062 LDA #$02 / STA $64C2  (KANE)
SHORT_ANDROID_SLOT = 4       # $6067 LDA #$04 / STA $64C3  (ASH)

CHAR_GONE = 0xFE               # location value: removed / dead without a body.

# --- The duct map (R-41 / D-091) --------------------------------------------
# `select_menu_template ($817D)` — called **only** from the in-duct path —
# reads a per-room byte and points `$FD/$FE` at one of three screen templates,
# which `render_message ($7F0D)` then paints. This is NOT the deck plan: the
# duct partition agrees with the deck partition for only 12 of 34 rooms.
DUCT_TEMPLATE_ADDRS = (0xA956, 0xA9C4, 0xAA6E)

#: **[C $7132/$7112/$7122]** The three deck plans, UPPER/MIDDLE/LOWER, as plain
#: uncompressed 30x18 screens `$21C` apart. `init_menu_ptr` and its two siblings
#: point `$FD/$FE` at one of these and copy 30 bytes a row into `$0400`, and
#: `menu_option_dispatch ($511F)` / `$76BB` choose between them with the same
#: `$7569` deck byte that picks the duct sheet.
#:
#: Decoding these retires the remake's only remaining dependency on a screen
#: capture for game content — it used to draw the map from
#: `docs/reference/{upper,middle,lower}deck_0400.bin`.
DECK_PLAN_ADDRS = (0xA000, 0xA21C, 0xA438)

#: **[C draw_control_panel_body $79CD]** The bottom status area is one **42-byte**
#: template, not a 40-column line, and the game copies it out in two pieces::
#:
#:     $7A10 +12 bytes -> $0702   row 19, col 10   ": damage 00%"
#:     $7A1C +30 bytes -> $0752   row 21, col 10   " is <9>,morale:<9>"
#:
#: Both status fields are **9 wide** — which is exactly "collapsed" and exactly
#: "confident", the longest word each can hold. Reading the template as 40
#: columns makes both fields look too narrow and puts the morale word off the
#: end of the row.
#: **[C $7000, `set_room_field $749B`]** the CONTROL list's per-row colour
#: table, 19 entries for panel rows 0-18, used to restore a row's normal colour
#: after the cursor blink.
#:
#: **[C $7440]** the INDICATE screen's own 19-row table.
#:
#: **There are three panel layouts, not one**, and they colour the same ten
#: columns differently: this one, INDICATE's, and the crew-order panel's
#: (`screens/panels.py`). Checking one against another is why `$7000` first
#: looked wrong.
#: Derivation: DISCOVERIES DISC-235, DISC-236, DISC-232.
INDICATE_PANEL_COLOUR_ADDR = 0x7440
CONTROL_PANEL_COLOUR_ADDR = 0x7000
CONTROL_PANEL_ROWS = 19
STATUS_TEMPLATE_ADDR = 0x7A10
STATUS_TEMPLATE_LEN = 42
#: Where each piece lands, as (source offset, length, row, column).
STATUS_TEMPLATE_PIECES = ((0, 12, 19, 10), (12, 30, 21, 10))
DECK_PLAN_COLS = 30
DECK_PLAN_ROWS = 18
#: `$817D LDA $7569,Y` — room -> template. Only 0 and 1 are tested explicitly
#: (`$818D CMP #$01`), so anything else falls through to the third template.
DUCT_TEMPLATE_INDEX_ADDR = 0x7569
#: `$81C9 LDA $80D3,Y` / `$81CE LDA $80B1,Y` — the room's screen address on the
#: map, which `mark_exits ($7F78)` then probes in four directions. NB the hi
#: table is the same `$80D3` the deck byte comes from: a screen page 4/5/6
#: doubles as the deck number, which is why one table serves both.
DUCT_POS_LO_ADDR = 0x80B1
DUCT_POS_HI_ADDR = 0x80D3
#: `$7F33 CPY #$1E` / `$7F43 CPX #$12` — the template is 30 columns x 18 rows,
#: painted from screen `$0400` with a 40-byte stride.
DUCT_MAP_COLS = 30
DUCT_MAP_ROWS = 18
DUCT_MAP_SCREEN_BASE = 0x0400
DUCT_MAP_STRIDE = 40
#: The screen code the templates use for a room node. Every one of the 34 room
#: positions lands on this glyph, and each template carries exactly as many of
#: them as it has rooms assigned (9/16/9) — the cross-check that proves the
#: template decode and the position tables agree.
DUCT_MAP_NODE_CHAR = 0xE6

# Crew slot order (slots 1-7 of the character arrays) — the game's CONTROL
# panel order, verified against the panel text at $A648 and the endgame capture.
#: **[C $A65E]** The crew-name table the CONTROL panel reads — 10-byte records,
#: `LDA $A65E,Y` from a dozen sites. Record 0 is the " Order:" header and record
#: 8 is " indicate ", so the seven crew are records 1-7.
#:
#: Decoded rather than hardcoded since 2026-08-08, which is what puts the case
#: back ("Dallas", not "DALLAS"). **Record 5 really is "Lambe"** — `$A690` reads
#: `8C 01 0D 02 05 A0 A0 A0 A0 A0`, five letters and five spaces. The
#: game-selection screen spells LAMBERT in full from its own table; this one,
#: the one the in-game panel uses, is truncated. Kept as the ROM has it.
CREW_NAME_TABLE_ADDR = 0xA65E
CREW_NAME_LEN = 10
CREW_NAME_FIRST_RECORD = 1

#: **[C $4EC4-$4ECB] The disk stores "Lambe"; the code writes the "rt" in.**
#:
#:     4EC4  LDA #$12 / STA $A695      ; 'r'
#:     4EC9  LDA #$14 / STA $A696      ; 't'
#:
#: `$A690` on the disk really is `8C 01 0D 02 05 A0 A0 A0 A0 A0` — five letters
#: and five spaces — while live RAM reads `...05 12 14 A0`. Diffing a 256-byte
#: window of the running machine against the file shows **exactly these two
#: bytes** differing, so it is a deliberate runtime patch, not a bad sector.
#: Every other name in the table is complete on disk.
CREW_NAME_PATCHES: tuple[tuple[int, int], ...] = ((0xA695, 0x12), (0xA696, 0x14))


class GamedataError(ValueError):
    """The bytes handed in are not the expected ALIEN program."""


#: **[C D-078 / P-7]** The punctuation ALIEN's charset actually uses. Masking
#: `& $7F` gets `%`, `,`, `.` and the digits right *by coincidence* (`$A5 & $7F`
#: is `$25` = `%`), but it is a coincidence — the glyphs live in the
#: reverse-video half and the ASCII slots hold unrelated shapes. `:` and the
#: space break the coincidence outright: `$1C` masks to `$1C`, not `$3A`, and
#: `$A0` masks to `$20` only because the space happens to be at `$20` too.
#:
#: `$AE` is the ROM's period and **renders blank** — this font has no period
#: glyph, so the template's dotted runs draw as solid band. Decoding it as `.`
#: reproduces the ROM's bytes; the renderer maps it back to `$AE`.
_ROM_PUNCTUATION = {0xA0: " ", 0x1C: ":", 0xA5: "%", 0xAE: ".", 0xAC: ","}


def _screen_char(c: int) -> str:
    """One screen code -> ascii, **preserving case** (D-116 follow-up).

    ALIEN's charset puts **lowercase a-z at `$01`-`$1A` and the capitals at
    `$81`-`$9A`** — the high bit selects case, it is not reverse video. `$A65E`
    reads `84 01 0C 0C 01 13` = "Dallas", and the panel labels are stored the
    same way: `$A898` "move to:", `$A8DF` "use:", `$7CE2` "Special:", `$A715`
    "quit", `$82AA` "Get item", and the room names at `$A71C` as
    "Airlock #1" / "Armoury" / "CargoPod#1".

    This used to `c &= 0x7F` first, discarding exactly the bit that carries the
    case, and then map everything to capitals — so every decoded string came out
    shouting. That is why the remake's panel read `MOVE TO:` / `SHUTTLEBAY`
    where the original reads `move to:` / `ShuttleBay`.
    """
    if 0x81 <= c <= 0x9A:
        return chr(c - 0x80 + 64)       # capitals
    if 1 <= c <= 26:
        return chr(c + 96)              # lowercase
    if c in _ROM_PUNCTUATION:
        return _ROM_PUNCTUATION[c]
    c &= 0x7F
    if c == 0:
        return "@"
    if 32 <= c <= 63:
        return chr(c)
    return " "


def _text(body: bytes, addr: int, length: int) -> str:
    raw = body[addr - LOAD_ADDRESS : addr - LOAD_ADDRESS + length]
    return " ".join("".join(_screen_char(b) for b in raw).split())


def _crew_names(body: bytes) -> tuple[str, ...]:
    """The seven crew names from `$A65E`, with the `$4EC4` runtime patch applied."""
    patched = bytearray(body)
    for addr, value in CREW_NAME_PATCHES:
        patched[addr - LOAD_ADDRESS] = value
    return tuple(
        _text(
            bytes(patched),
            CREW_NAME_TABLE_ADDR + (CREW_NAME_FIRST_RECORD + i) * CREW_NAME_LEN,
            CREW_NAME_LEN,
        )
        for i in range(7)
    )


def _bytes_at(body: bytes, addr: int, length: int) -> tuple[int, ...]:
    return tuple(body[addr - LOAD_ADDRESS : addr - LOAD_ADDRESS + length])


def decode_deck_plan(body: bytes, addr: int) -> tuple[tuple[int, ...], ...]:
    """One deck plan as a 30x18 grid of screen codes.

    Unlike the duct sheets these are not run-length encoded: `$7142` onward
    simply copies `($FD),Y` to `($FB),Y` for 30 columns, adds `$1E` to the
    source and `$28` to the destination, and repeats for 18 rows.
    """
    out = []
    base = addr - LOAD_ADDRESS
    for row in range(DECK_PLAN_ROWS):
        start = base + row * DECK_PLAN_COLS
        out.append(tuple(body[start : start + DECK_PLAN_COLS]))
    return tuple(out)


def decode_duct_template(body: bytes, addr: int) -> tuple[tuple[int, ...], ...]:
    """Unpack one duct-map screen template into a 30x18 grid of screen codes.

    **[C $7F0D]** `render_message` is the unpacker (the name is a misnomer —
    it paints a whole map, not a message). Reading `($FD),Y`::

        b == 0        -> end of template          ($7F27 BEQ)
        b <  $82      -> a run of `b` blank cells ($7F2B BCC -> $7F48)
        b >= $82      -> one literal screen code  ($7F30 STA ($FB),Y)

    Cells advance across 30 columns (`$7F33 CPY #$1E`) then down a row with a
    40-byte stride (`$7F3A ADC #$28`), for 18 rows (`$7F43 CPX #$12`).

    The blank run writes `$00` explicitly ($7F4B), so "blank" is a real cell
    value here rather than a skip — which matters because `mark_exits` later
    probes neighbouring cells to decide which directions are open.
    """
    grid = [[0] * DUCT_MAP_COLS for _ in range(DUCT_MAP_ROWS)]
    row = col = 0
    i = addr - LOAD_ADDRESS
    while row < DUCT_MAP_ROWS:
        if i >= len(body):
            raise GamedataError(f"duct template ${addr:04X} ran off the end of the PRG")
        b = body[i]
        i += 1
        if b == 0:
            break
        repeat = 1 if b >= 0x82 else b
        for _ in range(repeat):
            if row >= DUCT_MAP_ROWS:
                break
            if b >= 0x82:
                grid[row][col] = b
            col += 1
            if col == DUCT_MAP_COLS:
                col = 0
                row += 1
    return tuple(tuple(r) for r in grid)


def decode_duct_map(body: bytes) -> tuple[
    tuple[tuple[tuple[int, ...], ...], ...], tuple[int, ...], tuple[tuple[int, int], ...]
]:
    """The whole duct map: three templates, room->template, room->(row, col).

    Returns ``(templates, room_template, room_cell)``. Raises if the three
    tables disagree — every room must sit on a :data:`DUCT_MAP_NODE_CHAR`
    node, and each template must carry exactly as many nodes as it has rooms.
    That mutual check is what makes this decode trustworthy without a live
    capture.
    """
    templates = tuple(
        decode_duct_template(body, a) for a in DUCT_TEMPLATE_ADDRS
    )
    raw = _bytes_at(body, DUCT_TEMPLATE_INDEX_ADDR, MAPPED_ROOM_COUNT)
    # `$818D CMP #$01 / BNE $819C` — 0 and 1 dispatch explicitly, anything else
    # falls through to the third template.
    room_template = tuple(b if b < 2 else 2 for b in raw)
    lo = _bytes_at(body, DUCT_POS_LO_ADDR, MAPPED_ROOM_COUNT)
    hi = _bytes_at(body, DUCT_POS_HI_ADDR, MAPPED_ROOM_COUNT)
    cells: list[tuple[int, int]] = []
    for room, (l, h) in enumerate(zip(lo, hi)):
        offset = ((h << 8) | l) - DUCT_MAP_SCREEN_BASE
        row, col = divmod(offset, DUCT_MAP_STRIDE)
        if not (0 <= row < DUCT_MAP_ROWS and 0 <= col < DUCT_MAP_COLS):
            raise GamedataError(
                f"room {room}'s duct position ${(h << 8) | l:04X} is off the map"
            )
        if templates[room_template[room]][row][col] != DUCT_MAP_NODE_CHAR:
            raise GamedataError(
                f"room {room} sits on ${templates[room_template[room]][row][col]:02X}, "
                f"not a ${DUCT_MAP_NODE_CHAR:02X} node"
            )
        cells.append((row, col))
    for idx, grid in enumerate(templates):
        nodes = sum(r.count(DUCT_MAP_NODE_CHAR) for r in grid)
        assigned = room_template.count(idx)
        if nodes != assigned:
            raise GamedataError(
                f"duct template {idx} has {nodes} nodes but {assigned} rooms"
            )
    return templates, room_template, tuple(cells)


@dataclass(frozen=True)
class RoomData:
    """One mapped room: real name, deck (4/5/6 raw), compass exits, grille."""

    room_id: int
    name: str
    deck: int
    north: int
    south: int
    east: int
    west: int
    has_grille: bool

    @property
    def exits(self) -> dict[str, int]:
        """Real exits only (the tables encode 'no exit' as the room's own id)."""
        out = {}
        for direction in ("north", "south", "east", "west"):
            dest = getattr(self, direction)
            if dest != self.room_id:
                out[direction] = dest
        return out


@dataclass(frozen=True)
class ItemData:
    """One of the 20 item instances: its type and fixed starting room."""

    index: int
    type_id: int      # 1-10, indexes the type-name table.
    type_name: str
    start_room: int


@dataclass(frozen=True)
class GameData:
    """Everything decoded from the PRG's own tables."""

    room_names: tuple[str, ...]          # 36, index = room id
    rooms: tuple[RoomData, ...]          # the 34 mapped rooms
    item_type_names: tuple[str, ...]     # 10
    items: tuple[ItemData, ...]          # 20
    crew_names: tuple[str, ...]          # 7, character-slot order
    crew_start_rooms: tuple[int, ...]    # 7 (static PRG values; 0 = set at init)
    crew_walk_ticks: tuple[int, ...]     # [?] see WALK_TICKS_ADDR — NOT durations
    jones_walk_ticks: int
    alien_move_ticks: int                # 70: units per Alien compass move
    status_words: tuple[str, ...]        # O.K./WOUNDED/COLLAPSED/DEAD
    morale_words: tuple[str, ...]        # CONFIDENT..BROKEN
    rng_table: tuple[int, ...]           # 16 entries (identity -> uniform 0-15)
    routing: tuple[tuple[int, ...], ...]  # 5 x 35 next-room tables (D-167: incl. room 34)
    ducts: tuple[tuple[int, ...], ...]   # 4 x 34 duct neighbours, N/E/S/W
    short_scenario: tuple[tuple[int, ...], ...]  # 4 x 7 SHORT-mode crew tables
    # The duct map (R-41 / D-091): three 30x18 screen templates, the
    # per-room template index, and each room's (row, col) node on it.
    duct_templates: tuple[tuple[tuple[int, ...], ...], ...]
    deck_plans: tuple[tuple[tuple[int, ...], ...], ...]
    status_template: str
    control_panel_colours: tuple[int, ...]
    indicate_panel_colours: tuple[int, ...]
    duct_room_template: tuple[int, ...]
    duct_room_cell: tuple[tuple[int, int], ...]


def _room_name_addr(room: int) -> int:
    """Where room ``room``'s 10-char name record lives — **[C $7948]**.

    Three cases, exactly as `set_room_screen_ptr` branches: rooms below
    `$11` from `$A71C`, room `$22` from its own pointer `$5DD1`, and the rest
    from `$A7DA` — which is two records past where a flat table would put
    them. See `ROOM_NAMES_ADDR` for why that gap matters.
    """
    if room == ROOM_NARCISSUS_ID:
        return ROOM_NARCISSUS_NAME_ADDR
    if room < ROOM_NAMES_SPLIT:
        return ROOM_NAMES_ADDR + room * ROOM_NAME_LEN
    return ROOM_NAMES_HIGH_ADDR + (room - ROOM_NAMES_SPLIT) * ROOM_NAME_LEN


def decode_gamedata(prg: bytes) -> GameData:
    """Decode the tables from a raw ``ALIEN.prg`` (2-byte load header + body)."""
    if len(prg) < 2:
        raise GamedataError("not a PRG: fewer than 2 bytes")
    load = prg[0] | (prg[1] << 8)
    if load != LOAD_ADDRESS:
        raise GamedataError(
            f"expected load ${LOAD_ADDRESS:04X} (ALIEN), got ${load:04X}"
        )
    body = prg[2:]
    if len(body) < RNG_TABLE_ADDR + 16 - LOAD_ADDRESS:
        raise GamedataError("PRG body too short to hold the game tables")

    room_names = tuple(
        _text(body, _room_name_addr(i), ROOM_NAME_LEN) for i in range(ROOM_COUNT)
    )
    decks = _bytes_at(body, DECK_TABLE_ADDR, MAPPED_ROOM_COUNT)
    north = _bytes_at(body, NORTH_ADDR, MAPPED_ROOM_COUNT)
    south = _bytes_at(body, SOUTH_ADDR, MAPPED_ROOM_COUNT)
    east = _bytes_at(body, EAST_ADDR, MAPPED_ROOM_COUNT)
    west = _bytes_at(body, WEST_ADDR, MAPPED_ROOM_COUNT)
    grille = _bytes_at(body, GRILLE_ADDR, MAPPED_ROOM_COUNT)
    rooms = tuple(
        RoomData(
            room_id=i,
            name=room_names[i],
            deck=decks[i],
            north=north[i],
            south=south[i],
            east=east[i],
            west=west[i],
            has_grille=bool(grille[i]),
        )
        for i in range(MAPPED_ROOM_COUNT)
    )

    type_names = tuple(
        _text(body, ITEM_NAMES_ADDR + i * ITEM_NAME_LEN, ITEM_NAME_LEN)
        for i in range(ITEM_TYPE_COUNT)
    )
    type_ids = _bytes_at(body, ITEM_TYPES_ADDR, ITEM_COUNT)
    item_rooms = _bytes_at(body, ITEM_ROOMS_ADDR, ITEM_COUNT)
    items = tuple(
        ItemData(
            index=i,
            type_id=type_ids[i],
            type_name=type_names[type_ids[i] - 1],
            start_room=item_rooms[i],
        )
        for i in range(ITEM_COUNT)
    )

    char_locs = _bytes_at(body, CHAR_LOCS_ADDR, 9)
    walk = _bytes_at(body, WALK_TICKS_ADDR, 9)
    duct_templates, duct_room_template, duct_room_cell = decode_duct_map(body)

    return GameData(
        room_names=room_names,
        rooms=rooms,
        item_type_names=type_names,
        items=items,
        crew_names=_crew_names(body),
        crew_start_rooms=char_locs[1:8],
        crew_walk_ticks=walk[1:8],
        jones_walk_ticks=walk[8],
        alien_move_ticks=body[ALIEN_MOVE_TICKS_ADDR - LOAD_ADDRESS],
        status_words=tuple(
            _text(body, STATUS_WORDS_ADDR + i * 10, 10) for i in range(4)
        ),
        morale_words=tuple(
            _text(body, MORALE_WORDS_ADDR + i * 10, 10) for i in range(5)
        ),
        rng_table=_bytes_at(body, RNG_TABLE_ADDR, 16),
        # **D-167: routing is ROOM_COUNT (35), not MAPPED_ROOM_COUNT (34).**
        # The gaps between the five bases are 36/36/35/35, so every table has a
        # row for room 34, and it is a real one: the NARCISSUS reads
        # `shuttlebay, shuttlebay, self, self, self`, which under the
        # `surface_exits` rule yields exactly one exit, back to the shuttlebay.
        # Truncating at 34 dropped that row from `ALIEN_ROUTES`, so every
        # consumer (the Alien's own moves, `jones_dest`, `panic_dest`,
        # `tracker_zone`, and now the MOVE TO menu) silently had **no data at
        # all** for a character or creature in the Narcissus — and `$89D0
        # LDX #$22 / CPX $7935` proves the ROM expects the Alien to be there.
        # The duct tables really are 34 (their bases are 34 apart): there is no
        # ducting in the shuttle.
        routing=tuple(
            _bytes_at(body, addr, ROOM_COUNT) for addr in ROUTING_ADDRS
        ),
        ducts=tuple(
            _bytes_at(body, addr, MAPPED_ROOM_COUNT) for _, addr in DUCT_ADDRS
        ),
        short_scenario=tuple(
            _bytes_at(body, addr, 7) for _, addr in SHORT_ADDRS
        ),
        duct_templates=duct_templates,
        deck_plans=tuple(
            decode_deck_plan(body, a) for a in DECK_PLAN_ADDRS
        ),
        control_panel_colours=_bytes_at(
            body, CONTROL_PANEL_COLOUR_ADDR, CONTROL_PANEL_ROWS
        ),
        indicate_panel_colours=_bytes_at(
            body, INDICATE_PANEL_COLOUR_ADDR, CONTROL_PANEL_ROWS
        ),
        status_template="".join(
            _screen_char(c)
            for c in _bytes_at(body, STATUS_TEMPLATE_ADDR, STATUS_TEMPLATE_LEN)
        ),
        duct_room_template=duct_room_template,
        duct_room_cell=duct_room_cell,
    )


def load_gamedata(path: str | Path) -> GameData:
    """Decode straight from an ``ALIEN.prg`` on disk."""
    return decode_gamedata(Path(path).read_bytes())


def format_report(gd: GameData) -> str:
    """Human-readable dump of the decoded tables (the ``gamedata`` subcommand)."""
    lines: list[str] = []
    lines.append("ALIEN.prg game data (decoded from the program's own tables)")
    lines.append("")
    lines.append("Rooms (id, name, deck, exits, grille):")
    for r in gd.rooms:
        exits = ", ".join(
            f"{d[0].upper()}->{gd.room_names[t]}" for d, t in r.exits.items()
        )
        grille = "grille" if r.has_grille else "NO grille"
        lines.append(f"  {r.room_id:2d} {r.name:<10s} deck{r.deck} [{grille}] {exits}")
    lines.append(f"  34 {gd.room_names[34]:<10s} (off-map: the Narcissus)")
    lines.append(f"  35 {gd.room_names[35]:<10s} (off-map)")
    lines.append("")
    lines.append("Items (20 instances, fixed starting rooms):")
    for it in gd.items:
        lines.append(
            f"  #{it.index:2d} type{it.type_id:2d} {it.type_name:<10s} "
            f"@ {gd.room_names[it.start_room]}"
        )
    lines.append("")
    lines.append(f"Crew (slot order): {', '.join(gd.crew_names)}")
    starts = ", ".join(
        gd.room_names[r] if r not in (0x00, CHAR_GONE) else "(set at init)"
        for r in gd.crew_start_rooms
    )
    lines.append(f"Crew start rooms:  {starts}")
    lines.append(f"$6586 backup blk:  {', '.join(map(str, gd.crew_walk_ticks))}"
                 f"  (Jones: {gd.jones_walk_ticks})")
    lines.append(f"Alien move ticks:  {gd.alien_move_ticks}")
    lines.append(f"Status words:      {', '.join(gd.status_words)}")
    lines.append(f"Morale words:      {', '.join(gd.morale_words)}")
    return "\n".join(lines)


# --- Snapshot generation (the remake's offline copy) ---------------------------

def slugify(name: str) -> str:
    """Room/item display name -> a stable python-identifier-ish id."""
    return "_".join(name.lower().split())


def emit_python(gd: GameData) -> str:
    """Render the decoded data as a generated Python module for the remake.

    The remake must run without the disk image present, so it consumes a
    checked-in snapshot module rather than decoding the PRG at runtime. The
    snapshot is a **derived artifact**: regenerate with
    ``python -m alientools gamedata --emit-python`` and never hand-edit it;
    a test compares it against a fresh decode whenever the PRG is available.
    """
    lines: list[str] = []
    lines.append('"""GENERATED by `python -m alientools gamedata --emit-python`.')
    lines.append("")
    lines.append("Real game data decoded from ALIEN.prg's own tables (see")
    lines.append("alientools.gamedata for addresses and docs/re/GAMEDATA.md for the")
    lines.append('evidence). Do NOT hand-edit; regenerate instead."""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    base_slugs = [slugify(n) for n in gd.room_names]
    # Disambiguate duplicate names (the two OTHER LIST rooms).
    dupes = {s for s in base_slugs if base_slugs.count(s) > 1}
    seen: dict[str, int] = {}
    slugs = []
    for s in base_slugs:
        if s in dupes:
            seen[s] = seen.get(s, 0) + 1
            slugs.append(f"{s}_{seen[s]}")
        else:
            slugs.append(s)
    lines.append(f"ROOM_SLUGS: tuple[str, ...] = {tuple(slugs)!r}")
    lines.append("")
    lines.append(f"ROOM_NAMES: tuple[str, ...] = {tuple(gd.room_names)!r}")
    lines.append("")
    rooms = tuple(
        (r.room_id, r.deck, r.north, r.south, r.east, r.west, int(r.has_grille))
        for r in gd.rooms
    )
    lines.append("# (room_id, deck, north, south, east, west, grille) per mapped room;")
    lines.append("# a compass entry equal to room_id means no exit that way.")
    lines.append(f"ROOMS: tuple[tuple[int, int, int, int, int, int, int], ...] = {rooms!r}")
    lines.append("")
    lines.append(f"ITEM_TYPE_NAMES: tuple[str, ...] = {tuple(gd.item_type_names)!r}")
    lines.append("")
    items = tuple((it.index, it.type_id, it.start_room) for it in gd.items)
    lines.append("# (index, type_id 1-10, start_room) per item instance.")
    lines.append(f"ITEMS: tuple[tuple[int, int, int], ...] = {items!r}")
    lines.append("")
    lines.append(f"CREW_NAMES: tuple[str, ...] = {tuple(gd.crew_names)!r}")
    lines.append(f"CREW_START_ROOMS: tuple[int, ...] = {tuple(gd.crew_start_rooms)!r}")
    lines.append(f"CREW_WALK_TICKS: tuple[int, ...] = {tuple(gd.crew_walk_ticks)!r}")
    lines.append(f"JONES_WALK_TICKS = {gd.jones_walk_ticks}")
    lines.append(f"ALIEN_MOVE_TICKS = {gd.alien_move_ticks}")
    lines.append(f"STATUS_WORDS: tuple[str, ...] = {tuple(gd.status_words)!r}")
    lines.append(f"MORALE_WORDS: tuple[str, ...] = {tuple(gd.morale_words)!r}")
    lines.append("")
    # The five Alien surface route tables ($7A3A.., DISASSEMBLY §8.10): each is a
    # next-room id indexed by the Alien's current room; the roll band picks which
    # table.
    routes = tuple(tuple(t) for t in gd.routing)
    lines.append("# Five Alien surface route tables: ALIEN_ROUTES[band][room_id] =")
    lines.append("# next room id (roll-band selected; $7A3A.., DISASSEMBLY §8.10).")
    lines.append(f"ALIEN_ROUTES: tuple[tuple[int, ...], ...] = {routes!r}")
    lines.append("")
    # The SURFACE walk graph, built by the game's own $7860 algorithm from the
    # routing tables above (P-1). This — not the compass tables — is what a
    # character on the surface may walk to.
    surf = tuple(surface_exits(gd.routing, r) for r in range(MAPPED_ROOM_COUNT))
    lines.append("# SURFACE_EXITS[room_id] = the rooms a character may walk to")
    lines.append("# on the surface, in the game's own menu order ($7860).")
    lines.append(f"SURFACE_EXITS: tuple[tuple[int, ...], ...] = {surf!r}")
    lines.append("")
    # The DUCT network ($80F5/$8117/$8139/$815B, D-083): four compass tables of
    # room->room neighbours. A self-reference means "no duct exit that way".
    ducts = tuple(tuple(t) for t in gd.ducts)
    lines.append("# The DUCT network: DUCT_NEIGHBOURS[dir][room_id] = the room")
    lines.append("# reached by crawling that way, or the room itself for no exit.")
    lines.append("# Order is N, E, S, W ($80F5/$8117/$8139/$815B); the direction")
    lines.append("# assignment comes from $40B8-$40FA printing the matching word.")
    lines.append(
        f"DUCT_DIRECTIONS: tuple[str, ...] = {tuple(d for d, _ in DUCT_ADDRS)!r}"
    )
    lines.append(f"DUCT_NEIGHBOURS: tuple[tuple[int, ...], ...] = {ducts!r}")
    lines.append("")
    # The SHORT SCENARIO's scripted setup ($604F, D-085).
    short = tuple(tuple(t) for t in gd.short_scenario)
    lines.append("# SHORT SCENARIO ($604F): a FIXED opening, not a shorter FULL.")
    lines.append("# Order matches SHORT_FIELDS; each is 7 entries, crew slots 1-7.")
    lines.append(
        f"SHORT_FIELDS: tuple[str, ...] = {tuple(n for n, _ in SHORT_ADDRS)!r}"
    )
    lines.append(f"SHORT_SCENARIO: tuple[tuple[int, ...], ...] = {short!r}")
    lines.append(f"SHORT_VICTIM_SLOT = {SHORT_VICTIM_SLOT}")
    lines.append(f"SHORT_ANDROID_SLOT = {SHORT_ANDROID_SLOT}")
    lines.append(f"SHORT_DUCT_SLOTS: tuple[int, ...] = {SHORT_DUCT_SLOTS!r}")
    lines.append("")
    # The duct map (R-41 / D-091): the screen the game shows while a character
    # is inside the ducting. Three templates, not the three deck plans.
    lines.append("# The DUCT MAP ($817D -> $A956/$A9C4/$AA6E, painted by $7F0D).")
    lines.append("# One sheet per DECK, indexed by the same $7569 byte as the deck plan.")
    lines.append(f"DUCT_MAP_COLS = {DUCT_MAP_COLS}")
    lines.append(f"DUCT_MAP_ROWS = {DUCT_MAP_ROWS}")
    lines.append(f"DUCT_MAP_NODE_CHAR = {DUCT_MAP_NODE_CHAR:#04x}")
    lines.append(
        "DUCT_MAP_TEMPLATES: tuple[tuple[tuple[int, ...], ...], ...] = "
        f"{gd.duct_templates!r}"
    )
    lines.append("")
    lines.append("# The three DECK PLANS ($7132/$7112/$7122 -> $A000/$A21C/$A438),")
    lines.append("# uncompressed 30x18 screens copied straight into $0400.")
    lines.append(f"DECK_PLAN_COLS = {DECK_PLAN_COLS}")
    lines.append(f"DECK_PLAN_ROWS = {DECK_PLAN_ROWS}")
    lines.append(
        "DECK_PLANS: tuple[tuple[tuple[int, ...], ...], ...] = "
        f"{gd.deck_plans!r}"
    )
    lines.append("")
    lines.append("# The bottom status template ($7A10, 42 bytes) and where its")
    lines.append("# two pieces land: (src offset, length, row, col).")
    lines.append("")
    lines.append("# The CONTROL list's per-row colour table ($7000, 19 rows).")
    lines.append(
        "CONTROL_PANEL_COLOURS: tuple[int, ...] = "
        f"{gd.control_panel_colours!r}"
    )
    lines.append("# The INDICATE screen's per-row colour table ($7440).")
    lines.append(
        "INDICATE_PANEL_COLOURS: tuple[int, ...] = "
        f"{gd.indicate_panel_colours!r}"
    )
    lines.append("")
    lines.append(f"STATUS_TEMPLATE = {gd.status_template!r}")
    lines.append(
        "STATUS_TEMPLATE_PIECES: tuple[tuple[int, int, int, int], ...] = "
        f"{STATUS_TEMPLATE_PIECES!r}"
    )
    lines.append("")
    lines.append(
        f"DUCT_MAP_ROOM_TEMPLATE: tuple[int, ...] = {gd.duct_room_template!r}"
    )
    lines.append(
        "DUCT_MAP_ROOM_CELL: tuple[tuple[int, int], ...] = "
        f"{gd.duct_room_cell!r}"
    )
    lines.append(
        f"SHORT_ITEM_MOVES: tuple[tuple[int, int], ...] = {SHORT_ITEM_MOVES!r}"
    )
    lines.append("")
    return "\n".join(lines)
