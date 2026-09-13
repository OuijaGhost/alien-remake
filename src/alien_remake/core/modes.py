"""Game modes & the opening scenario (GAME_SPEC §9 / §11 #6).

The manual names two axes of variation at game start: a **short** vs. **full**
length, and whether the crew member who is already dead when the game opens is
a **fixed** (canonical) casualty or **random**. Both are picked once, at
:class:`~alien_remake.core.sim.Simulation` construction, and only take effect
when the caller lets the simulation build its own starting state/ship/crew
(the same "only touch what we own" convention `sim.py` already uses for the
ship/crew/items/Alien) — an explicitly-supplied `GameState` is never mutated
out from under a test.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from enum import Enum

from . import constants


class GameMode(Enum):
    """Short vs. full game length (GAME_SPEC §9, default strategy §11 #6)."""

    FULL = "full"
    SHORT = "short"


class FrontEnd(Enum):
    """How much of the loader's boot chain to play through.

    ``CLASSIC`` is the original's, in full: the "LOADING... PLUG JOYSTICK INTO
    PORT TWO" card, the back-up NOTICE, "WELCOME TO ALIEN / FACE THE POWER OF
    THE UNKNOWN" with its `1 ALIEN` / `Q QUIT` rows, the instructions prompt,
    a second loading card, the title, and only then the Ctrl+1/Ctrl+2 selection.

    ``QUICK`` is the **default (DISC-262, owner's instruction)** and plays three
    screens in order: the title, the back-up notice, and the selection. It skips
    the two loading cards, the WELCOME menu and the EXIT advert.

    **This is the one place the remake's default is knowingly not the ROM's.**
    The skipped screens are all loader ceremony — a disk that is not loading,
    a joystick prompt for a keyboard, and a `Q QUIT` row nobody uses — and every
    one of them is still reachable with ``--front-end classic``.
    """

    CLASSIC = "classic"
    QUICK = "quick"


class JonesCatch(Enum):
    """How the cat behaves when a grab misses.

    ``CLASSIC`` is the ROM. `$878C LDA #$01 / STA $657F` slams Jones's move
    counter to 1 *before* rolling anything, so he steps on the very next pass
    whether you catch him or not (D-160). With the cat box's decoded odds of
    6-19% per character (`$883C`), that is one shot per encounter and then you
    hunt him again.

    ``PATIENT`` is the **default (DISC-262, owner's instruction)**: the roll is
    untouched, but a miss no longer spooks him, so you can try again while he is
    still in the room. It changes how many attempts you get, never their odds.

    ``EASY`` is an **added rule, NOT the original (DISC-269)**: it gives the cat
    box the same four-point threshold improvement the ROM reserves for the net
    (`$87A1-$87AA`), so the box catches at the net's rate — Ripley 44% instead
    of 19%. Nothing else moves; the per-character table is still the ROM's, so
    Ripley, Ash and Lambert stay the best at it and Parker stays the worst.

    Worth knowing either way: the **net is far better than the box** — 31-44%
    against 6-19%, because `$87A1` improves the threshold by four. That is
    decoded, not an added rule, and the game never tells you. It is also why
    ``EASY`` is defined as "the box behaves like the net" rather than as an
    arbitrary bonus: the size of the change is one the ROM itself uses.
    """

    CLASSIC = "classic"
    PATIENT = "patient"
    EASY = "easy"


class AlienStart(Enum):
    """Where the Alien begins. **`RANDOM` is NOT the original (DISC-260).**

    `AIRLOCK` is the ROM: `$7935`'s slot 0 is the Alien's own room and reads
    `$00` — AIRLOCK 1, on the upper deck, every game. Two independent live
    boots agree (D-014).

    `RANDOM` is a deliberate added rule, added because the fixed start makes the
    creature's first ten minutes predictable: it always begins on deck 0 and,
    with only 4 of its 169 route entries crossing a deck and a 60-pass move
    timer, usually stays there for longer than a game lasts (DISC-259). Seeding
    it anywhere on the ship lets the same unchanged movement rules produce a
    game where it may already be below you.

    Nothing about how it *moves* changes — that stays the ROM's route tables.
    """

    #: The ROM: `$7935` slot 0, every game.
    ORIGINAL = "original"
    RANDOM = "random"


class DeathVariant(Enum):
    """Which crew member is already dead at the opening (GAME_SPEC §9).

    [C-live D-014] the FULL game's opening death is **RANDOM** (three boots:
    Lambert / Kane / Lambert) — so `RANDOM` is the real default (and is
    **PV-20 closed 2026-08-07 (D-170): there is no fixed-death mode in the
    ROM, and now we can say so definitively rather than "none was found".**
    `$64C2`, the opening victim slot, has **exactly two writers** in the whole
    image: `$5071`, inside the randomised pick (`JSR rng / LDA $50EC,Y`), and
    `$6064 LDA #$02`, the SHORT scenario pinning it to KANE (D-085). No third
    path exists, so `FIXED_OPENING_DEATH_ID = "lambert"` never described
    anything - it was a single live observation of the *random* draw.

    `DeathVariant.FIXED` is therefore kept **only as a remake testing aid**
    (`--death fixed` makes a run reproducible); it is explicitly **not** a
    fidelity claim, and nothing should read it as one.
    """

    FIXED = "fixed"
    #: The original: draw from `$50EC`, a fixed three-name candidate table.
    ORIGINAL = "original"
    #: **An added rule, NOT the original.** Draw the victim from the *whole*
    #: crew instead of the three-name table `$50EC` holds, so a crew member
    #: the original could never open on can be found dead here. Everything
    #: downstream already copes — Brett is reseated into whatever room the
    #: victim vacated rather than through `$510C,Y`'s paired lookup, which
    #: only covers the original three.
    RANDOM = "random"


# (`starting_oxygen()` lived here. Removed 2026-08-01 — FV-2.5 / D-062: the
# C64 game has no oxygen system at all, so there is no per-mode budget to
# return. Short mode's real difference is its smaller ship.)


class AndroidVariant(Enum):
    """Which crew members can be the hidden android.

    **[C $50FC] D-080.** The ROM rolls a four-entry table —
    DALLAS/KANE/ASH/PARKER — and re-rolls while it equals the opening victim,
    so three of the seven can never be the android at all. `ROM` reproduces
    that. `ANY` is **an added rule, NOT the original**: it draws from the whole
    crew, so Ripley, Lambert or Brett can be the android too.

    The victim is excluded either way. That is the ROM's own invariant
    (`CMP $64C2 / BEQ` re-rolls), and an android who is already dead at the
    opening would make the mechanic vacuous rather than harder.
    """

    #: The original: draw from `$50FC`, a fixed four-name candidate table.
    ORIGINAL = "original"
    #: **An added rule, NOT the original**: draw from the whole crew.
    RANDOM = "random"


def choose_android(
    crew_ids: Sequence[str],
    victim_id: str,
    rng: random.Random,
    variant: AndroidVariant = AndroidVariant.ORIGINAL,
) -> str | None:
    """Pick the hidden android (`$64C3`), or ``None`` for a trimmed roster.

    **[C $507A-$5086] D-080.** The ROM rolls `$50FC` (= DALLAS/KANE/ASH/PARKER)
    and **re-rolls while it equals the opening victim** (`CMP $64C2 / BEQ`), so
    the android is always someone other than the crew member found dead.

    ``variant`` widens only the *candidate table*, never the victim exclusion:
    :attr:`AndroidVariant.RANDOM` is an added rule that lets any surviving crew
    member be the android. Falls back to the full roster when the candidates
    are absent, so a trimmed test roster still gets one.
    """
    if variant is AndroidVariant.RANDOM:
        pool = [c for c in crew_ids if c != victim_id]
    else:
        pool = [
            c for c in crew_ids
            if c in constants.ANDROID_CANDIDATES and c != victim_id
        ]
    return rng.choice(pool) if pool else None


def choose_opening_death(
    crew_ids: Sequence[str], variant: DeathVariant, rng: random.Random
) -> str:
    """Pick which crew member is already dead at scenario start (GAME_SPEC §9).

    FIXED always names the same crew member
    (`constants.FIXED_OPENING_DEATH_ID`); RANDOM draws uniformly from
    `crew_ids`, matching the manual's "which crew member dies first is
    random" variant. Falls back to the first id if the fixed one isn't present
    (e.g. a trimmed test roster).
    """
    if variant is DeathVariant.RANDOM:
        # The added rule: no candidate table at all, so anyone can be the one
        # found dead. Deliberately kept as its own branch rather than an empty
        # filter, so the ROM's table below stays readable as the real thing.
        return rng.choice(list(crew_ids))
    if variant is DeathVariant.ORIGINAL:
        # **[C $50EC] D-080:** the ROM's candidate table holds only 1/2/5 —
        # DALLAS, KANE, LAMBERT. Drawing uniformly from all seven (as this did)
        # could open by killing Ripley, Ash, Parker or Brett, which the original
        # never does. Fall back to the full roster only for trimmed test rosters.
        pool = [c for c in crew_ids if c in constants.OPENING_VICTIM_CANDIDATES]
        return rng.choice(pool or list(crew_ids))
    if constants.FIXED_OPENING_DEATH_ID in crew_ids:
        return constants.FIXED_OPENING_DEATH_ID
    return next(iter(crew_ids))
