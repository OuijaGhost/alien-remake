"""Special Options: the Command Monitor's ship-wide, context-dependent actions
(GAME_SPEC §6.2 #3 / §8).

Unlike the five PCS order verbs (``core.orders``, aimed at one crew member and
gated by their state of mind), these are direct ship/player actions with no
PCS resolution — "open airlock", "launch Narcissus", "enter hypersleep",
"initiate auto-destruct", "catch Jones". They are structured the same way
(a typed ``SpecialOption`` a renderer builds and the ``Simulation`` applies)
purely for symmetry with ``Order``; application lives in
:mod:`alien_remake.core.sim` since it mutates the world.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class SpecialOptionType(Enum):
    """The Special Options, cut to the game's own menu (1:1 fidelity).

    The decoded specials menu (`tbl_specials_menu $57A0`, DISASSEMBLY §8.5) lists
    BLOWLOCK.1/.2, SEALLOCK.1/.2, ENTER HYPERSLEEP, BOARD NARCISSUS, LAUNCH
    NARCISSUS, OVERRIDE DETONATION, and FIGHT FIRE. Mapping here:

    * ``OPEN_AIRLOCK`` / ``SEAL_AIRLOCK`` = BLOWLOCK / SEALLOCK (per airlock).
      **[C, D-037, 2026-07-24 de-invention audit]**: the real dispatch
      (specials category 2, D-032) is offered only while standing in
      **CORRIDOR 6**, not inside an airlock — `apply_blowlock ($5B04)`
      operates on a *fixed* target airlock (AIRLOCK 1 or AIRLOCK 2, picked
      via the `.1`/`.2` menu label) via two independent per-airlock flags,
      not the acting crew member's own room. `menu.py`'s ``crew_entries``
      offers both airlocks as separate entries while in CORRIDOR 6, matching
      the real 4-label menu (`BLOWLOCK.1`/`.2`, `SEALLOCK.1`/`.2`).
    * ``LAUNCH_NARCISSUS`` = LAUNCH NARCISSUS (BOARD NARCISSUS is the crew
      moving to the SHUTTLEBAY, already a MOVE order).
    * ``ENTER_HYPERSLEEP`` = ENTER HYPERSLEEP. (There is **no** EXIT HYPERSLEEP
      in the game's menu — the old EXIT_HYPERSLEEP was an invention, removed.)
      **[C, FV-2j/D-028 2026-07-11]**: the real handler was finally located —
      it's `$5939`, previously mislabeled `guard_target_is_player` (a
      pre-trace guess at its purpose). Full trace of the specials dispatch
      (`$5839`, keyed off a per-room lookup table `$5753`) shows this handler
      only fires while the acting crew member is standing in the **CRYO
      VAULT** (room id 15) — a real room-gate the remake didn't enforce
      until now (`menu.py`). It is also self-target only, and on firing it
      sets a per-crew asleep flag and moves the crew member to a location
      sentinel (`$95`), removing them from the room grid — modelled as
      `room_id = None` in `Simulation._set_hypersleep`.
    * ``INITIATE_AUTO_DESTRUCT`` — **[C-live, FV-2c 2026-07-11] CORRECTED, was
      wrongly flagged invented.** FV-1b5's "no start-the-countdown entry exists"
      reading was wrong: the crew order menu's SPECIAL section really does show
      a two-line **"SCUTTLE" / "NOSTROMO"** entry (screen RAM read live, exact
      text confirmed) — the decoded specials table's first label, "NOSTROMO",
      was misread as a section header; it is actually shorthand for this action.
      Firing it live armed the ship (border flashed yellow) and the menu
      immediately grew a new **"Override Detonation"** entry — confirming these
      are the real arm/cancel pair. `menu.py`'s label corrected from the
      invented "SCUTTLE SHIP" to the live-read "SCUTTLE NOSTROMO".
    * ``OVERRIDE_DETONATION`` — **[C-live, new FV-2c 2026-07-11]**: cancels an
      armed countdown (only appears/is valid once armed, per the live menu
      change above). The exact countdown value/timer and what happens if it
      isn't overridden in time are decoded: **PV-06 closed 2026-08-07
      (D-179)** - `$5A3E LDA $657B / BNE / JMP hull_breach`. The
      countdown is ten 255-pass wraps (D-162); the tenth finds `$657B`
      already 0 and vents the ship. There is no other exit.
    * (The old CATCH_JONES special was an invention and was removed — catching
      Jones goes through USE of the CAT BOX item, R-17.)
    """

    OPEN_AIRLOCK = auto()
    SEAL_AIRLOCK = auto()
    LAUNCH_NARCISSUS = auto()
    ENTER_HYPERSLEEP = auto()
    INITIATE_AUTO_DESTRUCT = auto()
    OVERRIDE_DETONATION = auto()
    # FIGHT FIRE. **[C $5889, D-066 2026-08-01]** — this IS a separate special,
    # correcting the earlier note in `menu.py` that called it "not a separate
    # special: modelled as USE of the fire extinguisher". `$5889` sits in the
    # specials dispatch chain (after the `CMP #$02/#$03/#$04/#$05` arms at
    # `$5869`-`$5883`), has its own 10-char menu label ("Fight Fire", `$57D4`
    # blob) and its own result label ("Fire Out  ", copied from `$5950`).
    FIGHT_FIRE = auto()


@dataclass(frozen=True)
class SpecialOption:
    """One Special-Option invocation.

    ``room_id`` targets an airlock (OPEN/SEAL_AIRLOCK); ``crew_id`` targets a
    crew member (ENTER_HYPERSLEEP); LAUNCH_NARCISSUS and INITIATE_AUTO_DESTRUCT
    need neither.
    """

    type: SpecialOptionType
    room_id: str | None = None
    crew_id: str | None = None
