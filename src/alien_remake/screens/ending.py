"""The ending screen, decoded from the ROM — no pygame, no drawing.

Split out of :mod:`alien_remake.render.frontend` (DISC-240) for the same reason
as :mod:`.panels`: these are the ROM's own strings and screen offsets, each one
cited to the byte table it came from, and they were only readable with pygame
installed.

The ending is **composed, not picked** (`select_outcome $60A9`): up to four
independent lines land on fixed rows, one per outcome axis. Row numbers here
are the ROM's screen addresses divided out — ``row = ($addr - $0400) / 40`` —
so they can be checked against the disassembly directly.

Everything below moved verbatim, citations included.
"""

from __future__ import annotations

# The game's real end-screen text (decoded from the endings table at $6314),
# keyed by win route; a loss is "ALL CREW LOST".
# **[C $60A9-$617F] D-077: the ending is COMPOSED, not picked.** The remake
# used to show one `_WIN_MESSAGES` line. `select_outcome` writes up to four
# *independent* lines to fixed screen rows, one per outcome axis — which is
# exactly what two independent live captures showed ("three stacked outcome
# lines", FV-1c2b + FV-2d), on different combinations each time:
#
#   $04F0 (row 6)  "THE ALIEN IS DEAD"                      ($6372, 17)
#   $0540 (row 8)  "THE NARCISSUS RETURNS TO EARTH"         ($63BA, 30)
#   $0590 (row 10) "THE ALIEN AND ITS EGGS ARE UNLEASHED
#                   UPON THE PLANET"                        ($6383, 55)
#   $0608 (row 13) "ALL CREW LOST"                          ($63D8, 13)
#
# (Row = ($addr - $0400) / 40.) The ship-fate lines come from the
# `draw_ending_*` helpers at `$62B6`/`$62DC`/`$62EA`.
# **DISC-230 — decoded from the ROM's own byte tables, mixed case included.**
# These were transcribed in ALL CAPS before DISC-215's case-bit fix; every one
# of them is `$xx`-decoded below and the originals are sentence case.
ENDING_ALIEN_DEAD = "The Alien is dead"                       # $6372, 17
#: `$6383`, **55 cells in one linear copy** to `$0590` (row 10 col 0) — so it
#: wraps onto row 11 by itself; the four trailing spaces are part of the stored
#: string and are what pad row 10 out to the wrap.
ENDING_EGGS = "The Alien and its eggs are unleashed    upon the planet"
ENDING_NARCISSUS = "The Narcissus returns to Earth"           # $63BA, 30
ENDING_ALL_CREW_LOST = "All crew lost"                        # $63D8, 13
#: **[C $60AE-$60D0] The ship's own fate, drawn FIRST at `$0478` (row 3).**
#: `select_outcome` branches on `$64CF` — "the ship is going to be destroyed",
#: set by arming SCUTTLE and by a hull breach alike:
#:   * clear -> `$633C` "The Nostromo returns to Earth" (`draw_ending_lost`)
#:   * set, and the ANDROID (`$64C3`) is alive (`health >= 2`) and **not**
#:     aboard the Narcissus -> `draw_ending_survivor ($62B6)` writes its name
#:     at `$0478` then `$6314` at `$0480`, and **clears `$64CF`** ($62D6) —
#:     the android overrides the destruct and brings the ship home.
#:   * set otherwise -> `$6359` "The Nostromo is destroyed"
#: The remake drew none of this: the ship's fate line was simply missing.
ENDING_NOSTROMO_RETURNS = "The Nostromo returns to Earth"     # $633C, 29
ENDING_NOSTROMO_DESTROYED = "The Nostromo is destroyed"       # $6359, 25
#: `$6314`, 40 cells from `$0480` (row 3 col 8) — so it overlaps the 10-cell
#: name at `$0478` by two, exactly like the opening notice (D-145), and wraps
#: its last 8 characters onto row 4.
ENDING_BRINGS_BACK = " brings the Nostromo back       to Earth"
ENDING_IS_INSANE = "is insane"                                # $63E5, 9
ENDING_SURVIVORS = "Survivors:"                               # $63EE, 10
ENDING_COMPETENCE = "Competence Rating:   %"                  # $63F8, 22
ENDING_PRESS_ANY_KEY = "press any key"                        # $6475, 13
#: Row = `($addr - $0400) / 40`. `nostromo` is `$0478`, `alien` `$04F0`,
#: `ship` (the Narcissus line) `$0540`, `eggs` `$0590`, `crew` `$0608`.
ENDING_ROWS = {"nostromo": 3, "alien": 6, "ship": 8, "eggs": 10, "crew": 13}
#: `$0480` — the survivor-variant text starts eight columns in.
ENDING_BRINGS_BACK_COL = 8
#: `$62B6` copies ten name bytes to `$0478`; `$6314` then overwrites the last
#: two, so only eight survive — the same truncation the opening notice has.
ENDING_NAME_VISIBLE = 8
# The rest of the ending screen, at the ROM's own screen offsets: the rating
# text goes to `$0770` (row 22) with its two digits at `$0783`/`$0784`
# (row 22, cols 19-20), and "PRESS ANY KEY" to `$07D8` (row 24).
END_RATING_ROW = 22
END_RATING_DIGIT_COL = 19
END_PRESS_KEY_ROW = 24
#: `$07D8` is row 24 column **24**, not centred.
END_PRESS_KEY_COL = 24
# `$0608` (row 13) holds EITHER "All crew lost" or "Survivors:" — they are the
# two arms of `$6166`'s scan, never both — and the names run from `$0630`
# (row 14), one row apart (`$6204 ADC #$28`). These were 15/16.
END_SURVIVOR_HEADER_ROW = 13
END_SURVIVOR_FIRST_ROW = 14
# Rows 16-21 inclusive, so the list can never reach the rating on row 22 —
# which is what corrupted it (P-8).
END_SURVIVOR_ROWS = END_RATING_ROW - END_SURVIVOR_FIRST_ROW
