"""The in-game options screen's model — headless, stdlib only.

**Not the original.** *Alien* has no options screen: the disk offers Full Game
or Short Scenario and nothing else. This is a remake-only front end onto the
four house-rule/presentation flags that already exist as command-line switches,
added so a player without a terminal (a Steam Deck in Game Mode, say) can reach
them at all. Nothing here changes what the ROM does; two of the four options
*select* between the ROM's behaviour and a documented deviation, and say so.

The model is deliberately separate from the renderer so the whole screen —
cursor movement, value cycling, the help text, what gets written to disk — is
testable without pygame. The renderer only draws what this reports.

Each option mirrors one flag in ``__main__``'s parser and one key in
``settings``. That correspondence is the point: an option here that no flag
matched would be a setting the file could not round-trip, and
``test_options_screen.py`` fails if the three ever drift apart.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class OptionSpec:
    """One row of the options screen.

    ``key`` is both the settings-file key and the ``argparse`` destination, so
    the saved file feeds straight back through ``settings.apply``.
    ``values`` is in cycling order, and ``help_text`` is what the box at the
    top of the screen explains while the row is selected.
    """

    key: str
    label: str
    values: tuple[str, ...]
    help_text: tuple[str, ...]


#: The four options, in screen order. Wording is compressed from the same
#: switches' ``--help`` so the two cannot say different things about what a
#: value does; where a value is a deviation, the text says so rather than
#: leaving the player to assume the whole screen is the original.
#: The key of the synthetic first row. It is not a setting in its own right —
#: it reads back as whichever profile the *other* rows currently match, and
#: changing it writes a whole profile into them. Kept out of
#: :data:`~alien_remake.settings.KEYS` for that reason: storing it would give
#: the file two sources of truth that could disagree.
PRESET_KEY = "preset"

#: What each profile sets. ``original`` is every row at the ROM's own
#: behaviour, so the game plays as the disk does and every remake-only
#: deviation is off. ``updated`` is the remake's own added rules, on.
#:
#: **Renamed from ``ouijaghost`` 2026-09-06** (owner's request) — the value,
#: the on-screen label (`value.upper()` in `frontend.py`, so this rename is
#: the only place that needed to change), and every reference to it. Nothing
#: about what the preset *does* changed, and **no settings.toml migration was
#: needed**: `preset` is deliberately excluded from `settings.KEYS` (see
#: :data:`PRESET_KEY`'s own comment) and is never itself written to the file
#: — it is computed from the other rows by :func:`profile_of` every time. An
#: old save still carries the same `crt`/`jones`/`alien_start`/... values it
#: always did, so it now simply reports as `updated` instead of `ouijaghost`
#: with no read-time translation required.
#:
#: The two screens themselves (this one and the manual) are deliberately *not*
#: switched off by ``original``. They are how you get back, and a preset that
#: hid the control that set it would strand a player with no command line —
#: which is the exact situation this screen exists to fix.
PROFILES: dict[str, dict[str, str]] = {
    "original": {
        "crt": "off", "front_end": "classic", "jones": "classic",
        "alien_start": "original", "death": "original",
        "android": "original", "developer": "off",
        "sound": "game", "game_audio": "original", "turns": "off",
        "screen_fx": "off",
    },
    "updated": {
        "crt": "subtle", "front_end": "quick", "jones": "patient",
        "alien_start": "random", "death": "random", "android": "random",
        "developer": "off", "sound": "all", "game_audio": "enhanced",
        # **Owner, 2026-09-06:** the one added-rule row that stays "off" even
        # under this preset elsewhere is `turns` (a pacing overhaul, opt-in
        # regardless of preset - see `turns`'s own comment); `screen_fx` is a
        # purely cosmetic boot-screen flourish with the same "off under
        # ORIGINAL" guarantee, so UPDATED turning it on by default doesn't
        # carry the same risk turns would.
        "turns": "off", "screen_fx": "on",
    },
}

#: Shown on the preset row when the other rows match neither profile — which
#: includes the shipping defaults, deliberately. They are a middle ground (the
#: quick front end and the forgiving cat, but the ROM's Alien start and its
#: opening-death table), so calling them either profile would be untrue.
CUSTOM = "custom"

def profile_of(values: Mapping[str, str]) -> str:
    """Which profile a set of values *is* — or :data:`CUSTOM`.

    A free function because two very different callers need the same answer and
    must not each carry their own copy of it: the options screen's preset row,
    and the rule that the mouse is off under the original (see
    :func:`pointer_allowed`). A second definition is how they would end up
    disagreeing about what "the original" means.
    """
    for name, wanted in PROFILES.items():
        if all(values.get(k) == v for k, v in wanted.items()):
            return name
    return CUSTOM


def is_original(values: Mapping[str, str]) -> bool:
    """Are these settings exactly the 1984 disk's behaviour?

    The one place that question is answered. Two features now turn on it — the
    mouse (:func:`pointer_allowed`) and the title-card skip — and a second
    definition is how they would come to disagree about what "the original"
    means.
    """
    return profile_of(values) == "original"


def pointer_allowed(values: Mapping[str, str]) -> bool:
    """Is the mouse live? **No, under ORIGINAL** (owner's call, 2026-08-29).

    This reverses the call of 2026-08-28, which had the pointer available
    everywhere on the grounds that an input device is not a rule change — the
    same substitution as mapping a keyboard to the original's port-two
    joystick. The owner's decision is that ORIGINAL means the original
    *machine* too: the C64 that ran this disk had a joystick and a keyboard and
    no pointing device, so a mouse is an addition like any other and goes off
    with the rest of them.

    Keyed on the whole profile rather than a row of its own, deliberately.
    There is no `pointer` option to switch, so the only way to have a mouse is
    to be somewhere other than the original — and stepping any single row off
    ORIGINAL brings it back, which is the same rule the preset row already
    reports when it starts reading `custom`.

    **The lock-out this could become.** A player with *only* a pointer would
    choose ORIGINAL and have no way back to the options screen. It is not a
    live hazard today: every input this build supports (keyboard, joystick,
    mouse) comes on hardware that has at least one of the other two, and touch
    is not wired up. When `FINGERDOWN` lands it will be, and the answer then is
    an exception for the remake's own screens — see todo.md.
    """
    return not is_original(values)


@dataclass(frozen=True)
class Edition:
    """One answer to the first-run question (:data:`EDITIONS`)."""

    #: The profile in :data:`PROFILES` this answer applies.
    profile: str
    label: str
    #: What it means, for the box under the choice.
    lines: tuple[str, ...]


#: **The first thing the game asks, once.** Not the original: the disk starts
#: loading the moment you turn the machine on. It exists because the remake
#: ships two genuinely different things — a reconstruction of the 1984 disk,
#: and that plus everything added since — and a player who is handed one of
#: them silently has no way to know the other was there.
#:
#: Asked before anything else because the answer decides what "anything else"
#: is: ORIGINAL plays the full loader chain, so the question cannot come after
#: a boot sequence that the answer would have changed.
#:
#: Updated first, because it is the one a player who has not seen either should
#: meet first — it has the options screen, so it is also the one you can leave.
EDITIONS: tuple[Edition, ...] = (
    Edition(
        profile="updated",
        label="UPDATED AND EXPANDED",
        lines=(
            "THE GAME WITH EVERY ADDITION ON:",
            "THE MOUSE, THE CRT LOOK, THE QUICK",
            "BOOT, AND THE RULES THAT DRAW FROM",
            "THE WHOLE CREW INSTEAD OF THE",
            "ORIGINAL'S SHORT LISTS.",
        ),
    ),
    Edition(
        profile="original",
        label="ORIGINAL",
        lines=(
            "THE GAME AS THE 1984 DISK PLAYS IT.",
            "THE FULL LOADING SEQUENCE, NO CRT",
            "EFFECT, NO MOUSE, AND ONLY THE",
            "RULES THE CODE ITSELF HAS. NOTHING",
            "ADDED ANYWHERE.",
        ),
    ),
)

#: How wide a line of :attr:`Edition.lines` may be. Same reasoning and the same
#: box as :data:`HELP_WIDTH`, and the same test enforces both.
EDITION_WIDTH = 36


OPTION_SPECS: tuple[OptionSpec, ...] = (
    OptionSpec(
        key=PRESET_KEY,
        label="PRESET",
        values=("original", "updated"),
        help_text=(
            "SETS EVERY OPTION BELOW AT ONCE.",
            "ORIGINAL: THE GAME AS THE DISK",
            "PLAYS IT - EVERY ADDITION OFF, AND",
            "NO MOUSE. UPDATED: THE ADDED",
            "RULES ON. CUSTOM FOR ANY OTHER MIX.",
        ),
    ),
    OptionSpec(
        key="crt",
        label="CRT",
        values=("off", "subtle", "full"),
        help_text=(
            "ANALOG CRT LOOK, ON EVERY SCREEN.",
            "SAME EFFECTS EITHER WAY: SCANLINES,",
            "CHROMA BLEED, RF NOISE, GLOW.",
            "SUBTLE IS FULL AT TWO THIRDS.",
            "A LOOK, NOT THE ORIGINAL.",
        ),
    ),
    OptionSpec(
        key="front_end",
        label="FRONT END",
        values=("quick", "classic"),
        help_text=(
            "HOW MUCH OF THE LOADER TO PLAY.",
            "QUICK: TITLE, NOTICE, THEN THIS",
            "SCREEN. CLASSIC: THE FULL ORIGINAL",
            "CHAIN - LOADING CARDS, THE WELCOME",
            "MENU AND THE Q QUIT ADVERT.",
        ),
    ),
    OptionSpec(
        key="jones",
        label="JONES",
        values=("patient", "classic", "easy"),
        help_text=(
            "WHAT A MISSED GRAB AT THE CAT DOES.",
            "ORIGINAL: HE IS SPOOKED ON THE NEXT",
            "PASS EITHER WAY. PATIENT LETS YOU",
            "RETRY. EASY GIVES THE BOX THE NET'S",
            "ODDS - AN ADDED RULE.",
        ),
    ),
    OptionSpec(
        key="alien_start",
        label="ALIEN START",
        values=("original", "random"),
        help_text=(
            "WHERE THE ALIEN BEGINS.",
            "ORIGINAL: THE SAME PLACE EVERY GAME,",
            "AS THE DISK DOES IT. RANDOM: ANY",
            "MAPPED ROOM BAR THE SHUTTLE AND THE",
            "CREW'S OWN - AN ADDED RULE.",
        ),
    ),
    OptionSpec(
        key="sound",
        values=("off", "game", "all"),
        label="SOUND",
        help_text=(
            "OFF IS SILENT. GAME PLAYS THE",
            "ORIGINAL'S OWN EFFECTS - GRILLE,",
            "TRACKER, HEARTBEAT. ALL ADDS MENU",
            "AND BOOT SOUNDS THE ORIGINAL DOES",
            "NOT HAVE, FROM FILES YOU SUPPLY.",
        ),
    ),
    OptionSpec(
        key="game_audio",
        values=("original", "enhanced"),
        label="GAME AUDIO",
        help_text=(
            "ORIGINAL: SID-EMULATED EFFECTS, MIX",
            "UNCHANGED. ENHANCED: YOUR OWN",
            "RECORDINGS FROM THE SOUNDS FOLDER",
            "(SYNTH IF ABSENT), A LOUDNESS SPEC",
            "CHECK, AND WHERE NEW FILES GO.",
        ),
    ),
    OptionSpec(
        key="developer",
        label="DEVELOPER",
        values=("off", "on"),
        help_text=(
            "TOOLS FOR WORKING ON THE GAME, NOT",
            "FOR PLAYING IT. SHOWS THE ALIEN AND",
            "THE CAT ON THE MAP, AND UNLOCKS THE",
            "FIXED OPENING DEATH. THE SESSION LOG",
            "IS ALWAYS ON, WHATEVER THIS SAYS.",
        ),
    ),
    OptionSpec(
        key="death",
        label="OPENING DEATH",
        values=("original", "random", "fixed"),
        help_text=(
            "WHO IS FOUND DEAD AT THE OPENING.",
            "ORIGINAL DRAWS FROM A SHORT FIXED",
            "LIST, SO MOST OF THE CREW ARE NEVER",
            "THE ONE. RANDOM DRAWS FROM ALL SEVEN",
            "- AN ADDED RULE.",
        ),
    ),
    OptionSpec(
        key="android",
        label="ANDROID",
        values=("original", "random"),
        help_text=(
            "WHO MAY BE THE HIDDEN ANDROID.",
            "ORIGINAL DRAWS FROM A SHORT FIXED",
            "LIST, SO SOME OF THE CREW NEVER ARE.",
            "RANDOM DRAWS FROM ALL SEVEN - AN",
            "ADDED RULE. NEVER THE ONE WHO DIED.",
        ),
    ),
    OptionSpec(
        key="turns",
        label="TURNS",
        values=("off", "on"),
        help_text=(
            "PACE THE GAME BY ORDER, NOT CLOCK.",
            "ON: NOTHING MOVES UNTIL YOU GIVE AN",
            "ORDER, WHICH THEN RUNS TO WHATEVER",
            "IT COSTS IN ONE STEP. TICKS AND",
            "COSTS UNCHANGED - AN ADDED RULE.",
        ),
    ),
    OptionSpec(
        key="screen_fx",
        label="SCREEN FX",
        values=("off", "on"),
        help_text=(
            "ON THE BOOT REPORT SCREEN: A CRT",
            "POWER-ON, TEXT TYPED IN PHOSPHOR",
            "YELLOW WITH A CURSOR AND STREAK,",
            "STATIC LETTERS/BLOCKS, A PROMPT.",
            "COSMETIC - NO CONTENT EVER CHANGES.",
        ),
    ),
)

#: How wide a help line may be, in characters. The screen is 40 columns, the
#: box is drawn from column 1, and its text starts at column 3 — so 36 is what
#: is left before a line runs into the border. `test_options_screen.py` enforces it,
#: because an over-long line is silently truncated on screen rather than
#: wrapping, and the sentence just stops mid-word.
HELP_WIDTH = 36


class OptionsModel:
    """Cursor + values for the options screen.

    Values start from whatever the game is actually running with, so opening
    the screen shows the truth rather than the defaults — including values that
    came from the command line this launch.
    """

    def __init__(self, current: dict[str, str] | None = None) -> None:
        self.specs = OPTION_SPECS
        self.row = 0
        #: Only the real settings. The preset row is derived (:attr:`profile`),
        #: so it is deliberately absent here — two sources of truth for the
        #: same thing is how a screen ends up disagreeing with itself.
        self.values: dict[str, str] = {}
        for spec in self.specs:
            if spec.key == PRESET_KEY:
                continue
            want = (current or {}).get(spec.key)
            self.values[spec.key] = (
                want if want in spec.values else spec.values[0]
            )

    @property
    def profile(self) -> str:
        """Which profile the current settings *are* — or :data:`CUSTOM`.

        Read from the settings rather than remembered, so changing any single
        row below immediately shows the preset as custom instead of leaving it
        claiming a profile it no longer describes.
        """
        return profile_of(self.values)

    def apply_profile(self, name: str) -> None:
        """Set every row from a profile. Unknown names are ignored."""
        for key, value in PROFILES.get(name, {}).items():
            if key in self.values:
                self.values[key] = value

    def displayed(self, spec: OptionSpec) -> str:
        """What the screen shows for one row."""
        if spec.key == PRESET_KEY:
            return self.profile
        return self.values[spec.key]

    @property
    def spec(self) -> OptionSpec:
        """The row the cursor is on."""
        return self.specs[self.row]

    def move(self, delta: int) -> None:
        """Move the cursor, wrapping — the list is short enough that wrapping
        is quicker than stopping at the ends."""
        self.row = (self.row + delta) % len(self.specs)

    def choices(self, spec: OptionSpec) -> tuple[str, ...]:
        """The values a row will actually cycle through right now.

        `fixed` pins the opening death so a run repeats — a development aid,
        not a way to play, and it is a fidelity claim nobody should be able to
        make by accident. So it is offered only while DEVELOPER is on, and a
        value already set is never yanked out from under the cursor.
        """
        if spec.key != "death" or self.values.get("developer") == "on":
            return spec.values
        keep = self.values.get(spec.key)
        return tuple(v for v in spec.values if v != "fixed" or v == keep)

    def change(self, delta: int) -> str:
        """Cycle the selected row's value and return the new one.

        Wraps in both directions, so left and right both reach every value.
        """
        spec = self.spec
        if spec.key == PRESET_KEY:
            # From `custom` there is no "next" to step from, so either
            # direction has to land somewhere definite: left takes the first
            # profile, right the last. From a profile it simply alternates.
            here = self.profile
            if here in spec.values:
                i = spec.values.index(here)
                name = spec.values[(i + delta) % len(spec.values)]
            else:
                name = spec.values[0] if delta < 0 else spec.values[-1]
            self.apply_profile(name)
            return name
        allowed = self.choices(spec)
        i = allowed.index(self.values[spec.key])
        value = allowed[(i + delta) % len(allowed)]
        self.values[spec.key] = value
        return value

    def as_dict(self) -> dict[str, str]:
        """The current selection, ready for ``settings.save``."""
        return dict(self.values)
