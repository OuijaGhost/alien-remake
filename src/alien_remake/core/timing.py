"""Every duration in the game, and what its number actually means.

Written for one decision. The turn-based mode (T1-T8) is blocked on **T3**:
once turns are paced by the player rather than by a 7.886 Hz loop, what does
"40 ticks" mean? The answer is not the same for every constant, and that is the
whole difficulty — so this module sorts them, once, with the reason attached.

The three kinds
---------------
:attr:`Denomination.LOOP_COUNT`
    A counter reload. The ROM writes N into a byte and decrements it once per
    main-loop pass, so the number means **N passes** and nothing else. Almost
    every gameplay timer is one of these. **These survive player-paced turns
    unchanged**: "60 passes" simply becomes "60 turns' worth of progress", and
    the ratios between them — the thing that makes the Alien feel faster than
    the cat — are preserved exactly.

:attr:`Denomination.REAL_SECONDS`
    The number encodes a wall-clock duration. Either the ROM spent it in a
    blocking delay loop whose length is a fact about the 6502 (`delay_long` is
    3.128 s PAL), or it was measured against real hardware, or the game tells
    the player the duration out loud. **These are what T3 has to decide about.**
    Detached from a 7.886 Hz clock they mean nothing on their own, and one of
    them — the auto-destruct — announces its length on screen in minutes.

:attr:`Denomination.RATE`
    The pacing itself: the clocks the other two are counted against.

What this is not
----------------
It is not a re-derivation. Every value and every citation belongs to
`constants`; this only says which kind each one is, and
``test_timing_audit.py`` fails if a duration is added there without being
classified here — so the audit cannot quietly fall behind the constants it
audits.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import constants


class Denomination(Enum):
    """What a duration's number is denominated in."""

    LOOP_COUNT = "loop count"
    REAL_SECONDS = "real seconds"
    RATE = "rate"


@dataclass(frozen=True)
class Timing:
    """One constant, its value, and what the value means."""

    name: str
    value: object
    kind: Denomination
    #: What it times, in a few words.
    what: str
    #: Why it is denominated the way it is — the sentence that matters when
    #: deciding what happens to it under player-paced turns.
    why: str
    #: Is the value counted in ticks? Almost all are. `AUTO_DESTRUCT_MINUTES`
    #: is the exception that needs the flag: it is a number of *minutes*, and
    #: dividing it by the tick rate produced "1.1 s" for a nine-minute
    #: countdown — a nonsense the table printed quite happily until it was
    #: read.
    ticks: bool = True

    @property
    def seconds(self) -> float | None:
        """How long it is in real time now, or ``None`` if that is not a
        meaningful question for it (a rate, a table, or a value already in
        some other unit)."""
        if self.kind is Denomination.RATE or not self.ticks:
            return None
        if isinstance(self.value, (int, float)):
            return float(self.value) / constants.TICK_HZ
        return None

    @property
    def turn_note(self) -> str:
        """What becomes of it once a turn is however long the player takes."""
        if self.kind is Denomination.RATE:
            return "stops being the clock; the turn is"
        if self.kind is Denomination.LOOP_COUNT:
            return "unchanged - the number is turns"
        return "must be re-decided (T3)"


_LOOP: Denomination = Denomination.LOOP_COUNT
_REAL: Denomination = Denomination.REAL_SECONDS
_RATE: Denomination = Denomination.RATE


#: Every duration in `constants`, classified. Order is by kind then by name, so
#: the generated table reads as an argument rather than as an alphabet.
TIMINGS: tuple[Timing, ...] = (
    # --- the clocks ----------------------------------------------------------
    Timing("TICK_HZ", constants.TICK_HZ, _RATE,
           "the simulation's tick rate",
           "the measured main-loop rate; every LOOP_COUNT below is counted "
           "against this and nothing else"),
    Timing("MAIN_LOOP_HZ", constants.MAIN_LOOP_HZ, _RATE,
           "the ROM's own main-loop rate",
           "measured on real hardware; also the cursor's repeat rate, which is "
           "why the sound debounce is derived from it"),
    Timing("ANIM_HZ", constants.ANIM_HZ, _RATE,
           "the sprite-animation rate",
           "the 60 Hz jiffy divided by the ROM's 9-jiffy animation divider"),
    Timing("JIFFY_HZ", constants.JIFFY_HZ, _RATE,
           "the C64's IRQ rate",
           "a fact about the machine, not about the game"),
    Timing("IRQ_JIFFIES_PER_ANIM_TICK", constants.IRQ_JIFFIES_PER_ANIM_TICK,
           _RATE, "jiffies per animation step",
           "the divider between the two rates above"),

    # --- action costs: the AP scale, already in the right units --------------
    Timing("MOVE_ACTION_TICKS", constants.MOVE_ACTION_TICKS, _LOOP,
           "a crew member walking to another room",
           "[C $48F7] a flat $40 armed into the action counter, before the "
           "slot and health terms are added. **This is the natural unit of "
           "one turn's work** and the obvious thing to price AP against"),
    Timing("ATTACK_ACTION_TICKS", constants.ATTACK_ACTION_TICKS, _LOOP,
           "an ATTACK or a USE",
           "[C $48F7 LDA #$28] the same counter, armed with $28 - so an attack "
           "is 40/64 of a move, a ratio that survives any re-pacing"),
    Timing("GRILLE_ACTION_TICKS", constants.GRILLE_ACTION_TICKS, _LOOP,
           "REMVGRILLE, per crew slot",
           "a per-character table: the engineers are quick at it and the "
           "captain is slow. Characterisation expressed as duration, so it "
           "must survive as duration"),
    Timing("ACTION_DELAY_BY_SLOT", constants.ACTION_DELAY_BY_SLOT, _LOOP,
           "the per-crew-member surcharge on any action",
           "[C $4032] added to every action's cost; who you send changes how "
           "long it takes, which is a mechanic and not flavour"),
    Timing("ACTION_DELAY_BY_HEALTH", constants.ACTION_DELAY_BY_HEALTH, _LOOP,
           "the wounded surcharge on any action",
           "a hurt crew member is slower - 48 extra passes at 2 health, which "
           "nearly doubles a move"),

    # --- the world's own timers ----------------------------------------------
    Timing("ALIEN_MOVE_TICKS", constants.ALIEN_MOVE_TICKS, _LOOP,
           "the Alien's surface move timer",
           "[C $8A4A] a counter reload. Its *ratio* to MOVE_ACTION_TICKS is "
           "the chase: the Alien moves about once for every crew move"),
    Timing("ALIEN_DUCT_TICKS", constants.ALIEN_DUCT_TICKS, _LOOP,
           "how long the Alien stays in a duct", "a counter reload"),
    Timing("ALIEN_DUCT_TRAVEL_TICKS", constants.ALIEN_DUCT_TRAVEL_TICKS, _LOOP,
           "duct-to-duct travel", "a counter reload"),
    Timing("ALIEN_BURST_TICKS", constants.ALIEN_BURST_TICKS, _LOOP,
           "the burst out of a grille", "a counter reload"),
    Timing("ALIEN_PURSUIT_TICKS", constants.ALIEN_PURSUIT_TICKS, _LOOP,
           "how long it keeps chasing", "a counter reload"),
    Timing("ALIEN_NET_ENTANGLE_TICKS", constants.ALIEN_NET_ENTANGLE_TICKS,
           _LOOP, "how long the net holds it", "a counter reload"),
    Timing("ALIEN_ENCOUNTER_HOLD_TICKS", constants.ALIEN_ENCOUNTER_HOLD_TICKS,
           _LOOP, "the pause on meeting the crew", "a counter reload"),
    Timing("ALIEN_VENT_STUN_TICKS", constants.ALIEN_VENT_STUN_TICKS, _LOOP,
           "how long a venting stuns it", "a counter reload"),
    Timing("JONES_MOVE_TICKS", constants.JONES_MOVE_TICKS, _LOOP,
           "the cat changing rooms", "a counter reload"),
    Timing("JONES_WALK_TICKS", constants.JONES_WALK_TICKS, _LOOP,
           "the cat's walk animation step", "presentation, not a rule"),
    Timing("PANIC_WANDER_TICKS", constants.PANIC_WANDER_TICKS, _LOOP,
           "a panicking crew member wandering", "a counter reload"),
    Timing("FIRE_SPREAD_EVERY_TICKS", constants.FIRE_SPREAD_EVERY_TICKS, _LOOP,
           "how often an unfought fire eats another point",
           "[C $5684] `INC $64CE / BNE rts` - it fires on the byte wrapping, "
           "so 256 passes exactly. A pure loop count, and the one that decides "
           "whether a fire is a crisis or a nuisance"),
    Timing("HEARTBEAT_DIVIDER_BY_COMPOSURE",
           constants.HEARTBEAT_DIVIDER_BY_COMPOSURE, _LOOP,
           "the heartbeat's IRQ divider, by composure",
           "[C $4E16] paces voice 1's sound; a calmer crew member's heart "
           "audibly beats slower. Audio, not a rule"),

    # --- calibrated to real seconds: the T3 problem ---------------------------
    Timing("AUTO_DESTRUCT_TICKS", constants.AUTO_DESTRUCT_TICKS, _REAL,
           "the whole self-destruct countdown",
           "**the hard one.** Mechanically it is 10 wraps of a 255 counter, so "
           "it looks like a loop count - but the game *says* NINE MINUTES on "
           "screen, and a player who takes an hour over nine minutes' worth of "
           "turns has been told something untrue. Re-pacing turns makes this "
           "either trivial or unsurvivable, and it is a judgement, not a bug"),
    Timing("AUTO_DESTRUCT_SUBTICKS", constants.AUTO_DESTRUCT_SUBTICKS, _REAL,
           "one wrap of the countdown byte",
           "[C $5A39] `LDA #$FF` - the reload the ten wraps are made of"),
    Timing("AUTO_DESTRUCT_MINUTES", constants.AUTO_DESTRUCT_MINUTES, _REAL,
           "the number the game says out loud",
           "the announced figure, which is what makes the countdown a promise "
           "about real time rather than about turns", ticks=False),
    Timing("NOTICE_TICKS", constants.NOTICE_TICKS, _REAL,
           "how long a row-24 banner is held",
           "[C $561C] one blocking `delay_long`; the remake cannot block, so "
           "it holds the banner for the equivalent instead. A reading time"),
    Timing("TITLE_TICKS", constants.TITLE_TICKS, _REAL,
           "the whole title card",
           "eight `delay_long`s = 25.0 s PAL. Front end, so T3 need not "
           "answer for it - but it is why the skip exists"),
    Timing("TITLE_LETTER_TICKS", constants.TITLE_LETTER_TICKS, _REAL,
           "the gap between title letters", "one `delay_long` = 3.128 s PAL"),
    Timing("TITLE_REVEALED_TICKS", constants.TITLE_REVEALED_TICKS, _REAL,
           "when the fifth letter has landed",
           "four letter gaps; the point the skip fast-forwards to"),
    Timing("OPENING_TICKS", constants.OPENING_TICKS, _REAL,
           "the opening death notice",
           "[C $50B8/$50BB] two `delay_long`s = 6.256 s. A reading time"),
    Timing("INTRO_LEGEND_TICKS", constants.INTRO_LEGEND_TICKS, _REAL,
           "the deck-plan key and sound legend",
           "`delay_long`-paced, and a reading time"),
    Timing("LOADING_MENU_TICKS", constants.LOADING_MENU_TICKS, _REAL,
           "the GREEN VALLEY spiral",
           "[C-live] measured at ~14.1 s against the real disk - BASIC's POKE "
           "loop is genuinely that slow"),
    Timing("LOADING_PLAY_TICKS", constants.LOADING_PLAY_TICKS, _REAL,
           "the PLUG JOYSTICK card",
           "[?] not paced by the ROM at all: it shows while the loader reads "
           "the next file, so its length is drive I/O. Left at a plausible 3 s"),
    Timing("EXIT_ADVERT_TICKS", constants.EXIT_ADVERT_TICKS, _REAL,
           "the ONE-STEP DEALER advert",
           "[C EXITO 1100] `FOR XX=1TO3000` before `SYS 64738`"),
    Timing("BOOT_TICKS", constants.BOOT_TICKS, _REAL,
           "the remake's own startup card",
           "not the original at all; a reading time chosen for this remake"),
    Timing("TURN_CREATURE_SLOT_TICKS", constants.TURN_CREATURE_SLOT_TICKS, _REAL,
           "the Alien/Jones initiative slot's own tick ceiling",
           "not the original at all - the disk has no turn-based mode, let "
           "alone initiative. Bounds how long a creature's autonomous slot "
           "runs before initiative passes on, chosen as a reading-time-scale "
           "window rather than derived from any ROM constant"),
    Timing("SCREEN_FX_CHARS_PER_TICK", constants.SCREEN_FX_CHARS_PER_TICK, _RATE,
           "the `screen_fx` typewriter's pace",
           "not the original at all - the divider between the tick rate and "
           "how fast the boot/title/ending reveal types out, one character "
           "at a time"),
    Timing("SCREEN_FX_GLITCH_TICKS", constants.SCREEN_FX_GLITCH_TICKS, _REAL,
           "the `screen_fx` static flourish's own duration",
           "not the original at all - a fixed, fading burst of static at the "
           "start of a screen entered with `screen_fx` on, chosen as a "
           "reading-time-scale flourish rather than derived from any ROM "
           "constant"),
    Timing("SCREEN_FX_CURSOR_BLINK_TICKS", constants.SCREEN_FX_CURSOR_BLINK_TICKS,
           _REAL, "the `screen_fx` typing cursor's blink rate",
           "not the original at all - the conventional terminal-cursor "
           "blink rate, not derived from anything ROM-side"),
    Timing("SCREEN_FX_STRETCH_TICKS", constants.SCREEN_FX_STRETCH_TICKS, _REAL,
           "the `screen_fx` CRT power-on stretch's own duration",
           "not the original at all - how long the boot report takes to grow "
           "from a thin band to full height, a flourish scaled to stay well "
           "inside BOOT_TICKS's own timeout"),
    Timing("SCREEN_FX_SHAKE_TICKS", constants.SCREEN_FX_SHAKE_TICKS, _REAL,
           "the `screen_fx` degauss shake's own duration",
           "not the original at all - a decaying wobble riding along with "
           "the power-on stretch, in the same shape (miniaturised) as the "
           "CRT layer's own deck-change degauss transient"),
)


def by_kind(kind: Denomination) -> tuple[Timing, ...]:
    """Every timing of one kind, in declared order."""
    return tuple(t for t in TIMINGS if t.kind is kind)


def describe() -> str:
    """The audit as text — what `--timing` prints and `docs/TIMING.md` holds."""
    lines = [
        "# Timing constants",
        "",
        "*Generated by `python -m alien_remake --timing`. Do not edit by "
        "hand: `alien_remake.core.timing` is the source, and a test fails if "
        "this file falls behind it.*",
        "",
        f"The simulation runs at **{constants.TICK_HZ} Hz**, the rate measured "
        "off the real machine's main loop. Every duration below is counted "
        "against that.",
        "",
        "The question this answers is T3's: **once a turn is however long the "
        "player takes, what does each of these numbers mean?**",
        "",
    ]
    headings = {
        Denomination.LOOP_COUNT: (
            "Loop counts — these survive player-paced turns",
            "A counter the ROM decrements once per main-loop pass. The number "
            "means *N passes* and nothing else, so under turns it means *N "
            "turns* and every ratio between them is preserved. The Alien "
            "staying twice as fast as the cat is a property of these numbers, "
            "not of the clock.",
        ),
        Denomination.REAL_SECONDS: (
            "Calibrated to real seconds — these are what T3 must decide",
            "The number encodes a wall-clock duration: a blocking `delay_long` "
            "(3.128 s on PAL hardware), a measurement against a real drive, or "
            "a figure the game says out loud. Detached from a fixed clock they "
            "mean nothing by themselves.",
        ),
        Denomination.RATE: (
            "Rates — the clocks everything else is counted against",
            "Under player-paced turns these stop being the pacing; the turn "
            "is.",
        ),
    }
    for kind in (Denomination.LOOP_COUNT, Denomination.REAL_SECONDS,
                 Denomination.RATE):
        title, blurb = headings[kind]
        lines += [f"## {title}", "", blurb, "",
                  "| constant | value | now | what it times | why |",
                  "|---|---|---|---|---|"]
        for t in by_kind(kind):
            seconds = t.seconds
            when = f"{seconds:.1f} s" if seconds is not None else "-"
            value = (
                ", ".join(str(v) for v in t.value)
                if isinstance(t.value, tuple)
                else str(t.value)
            )
            if isinstance(t.value, dict):
                value = ", ".join(f"{k}:{v}" for k, v in t.value.items())
            lines.append(
                f"| `{t.name}` | {value} | {when} | {t.what} | {t.why} |"
            )
        lines.append("")
    return "\n".join(lines)
