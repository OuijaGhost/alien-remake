"""The game's screen/state machine (headless, stdlib only).

The original *Alien* is not a cold real-time sim — it opens on a title card,
then a **game-selection** screen (the crew portraits + "Control:1 Full Game /
Control:2 Short Scenario"), then an **opening** notice ("… has been killed by
the ALIEN"), and only then the **playing** screen (map + the CONTROL-panel
menu). This module models that flow as a small state machine so the renderer
has something concrete to draw per screen and the loop has one place to route
input.

It is pure and pygame-free: input arrives as abstract :class:`InputEvent`s
(the pygame backend translates keys/joystick to these — space and the joystick
button both map to :attr:`InputEvent.FIRE`, per the original), and the flow
decides transitions and when to build the :class:`~alien_remake.core.sim.
Simulation`. Rendering and pacing live in the backend / app loop.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum, auto

from . import constants, instructions
from .options import EDITIONS, OptionsModel, is_original
from .modes import (
    AlienStart, AndroidVariant, DeathVariant, FrontEnd, GameMode, JonesCatch,
)
from .sim import Simulation
from .state import GamePhase

SimFactory = Callable[[GameMode, DeathVariant], Simulation]


#: CR4 - rows per CREDITS page. Sized to leave room for the header and
#: the same continue prompt MANUAL uses, on the 25-row field every other
#: screen draws into.
CREDITS_ROWS_PER_PAGE = 8


class Screen(Enum):
    """Which screen the game is currently showing.

    The first five are the live-captured **front-end** sequence (D-021), in
    boot order, before the animated title: a "LOADING MENU" card, the ShareData
    back-up NOTICE, the "WELCOME TO ALIEN" menu, the instructions Y/N prompt,
    and a "LOADING…. / PLUG JOYSTICK" card. Only then come the title, the crew
    selection, the opening death notice, and the game itself.
    """

    #: **Not the original, and it comes before everything.** The first-run
    #: question: updated-and-expanded, or the 1984 original (`options.
    #: EDITIONS`). Shown once, on a machine with no settings file, and never
    #: again — the answer is written to that file and changed from the options
    #: screen thereafter.
    #:
    #: It sits in front of :attr:`BOOT` rather than after it because the answer
    #: decides what the boot chain *is*: ORIGINAL runs the full loader, so a
    #: question asked afterwards would have let a sequence play that the answer
    #: was supposed to choose.
    FIRST_RUN = auto()
    #: **Not the original.** What the console window used to say, said inside
    #: the game instead (B1/B2): which settings file was read, what derived
    #: data is missing, whether a joystick was found. Shown **only when there
    #: is something to report** (B5) — a clean start goes straight to the
    #: publisher spiral, because a card that always appears is one nobody
    #: reads.
    BOOT = auto()
    LOADING_MENU = auto()    # "LOADING MENU" boot interstitial (timed)
    NOTICE = auto()          # ShareData "make a back-up copy" notice (press any key)
    WELCOME = auto()         # "WELCOME TO ALIEN" — 1 ALIEN / Q QUIT
    INSTRUCTIONS = auto()    # "DO YOU WANT INSTRUCTIONS? (Y OR N)"
    # R-12/R-31's last piece: answering Y shows the disk's own instruction
    # pages (`INSTRUCTIONS.seq`, a separate SEQ file — the text is not in
    # ALIEN.prg). Any key advances; the last page falls through to the game.
    INSTRUCTION_PAGES = auto()
    LOADING_PLAY = auto()    # "LOADING…. / PLUG JOYSTICK INTO PORT TWO" (timed)
    TITLE = auto()           # animated title card (egg + "ALIEN" + epigraph)
    GAME_SELECTION = auto()  # crew portraits + Full Game / Short Scenario
    OPENING = auto()         # "<name> has been killed by the ALIEN"
    PLAYING = auto()         # map + CONTROL panel (the actual game)
    ENDED = auto()           # win/lose result (read sim.state.phase for which)
    #: **[C MENU1 line 740/830 -> EXITO.prg] D-175** - what "Q QUIT" really
    #: does. It is not an exit: `CC=0` skips the instructions prompt and the
    #: joystick line, then MENU1 stuffs `LOAD"EXIT*",8` + `CLR:RUN` into the
    #: keyboard buffer. EXITO draws the same marquee border, three centre-out
    #: lines and a block-graphic **ONE-STEP DEALER** logo, waits
    #: `FOR XX=1TO3000`, and ends on `SYS 64738` - a **cold reset**.
    EXIT_ADVERT = auto()
    #: **[C $4405] D-176** - "DO YOU WANT AN INTRODUCTION / PRESS Y OR N".
    #: Reached only from the **SHORT** scenario: `game_init_mode ($4317)` reads
    #: `$4303` (the chosen mode) and returns immediately for FULL, so the FULL
    #: game has no introduction at all.
    INTRO_PROMPT = auto()
    #: **[C $4327] D-173** - the DECK PLAN KEY + SOUND LEGEND, shown on "Y".
    INTRO_LEGEND = auto()
    #: **Not the original.** The whole manual in one place, reachable from the
    #: selection screen: the loader's own instruction pages (the FULL game's
    #: text) followed by the DECK PLAN KEY + SOUND LEGEND that the SHORT
    #: scenario shows as its introduction. Both are the disk's words; putting
    #: them back to back is the remake's doing, because the ROM only ever
    #: offers one or the other and never from this screen.
    MANUAL = auto()
    #: **Not the original.** The options screen (`core.options`). The disk has
    #: no such screen; this exists so the four presentation/house-rule flags
    #: are reachable without a command line.
    OPTIONS = auto()
    #: **Not the original** (CR4/CR5, owner's request). A fifth row on
    #: the selection screen, `PRESS 5 CREDITS`, hidden under ORIGINAL -
    #: see `InputEvent.SELECT_CREDITS`.
    CREDITS = auto()


class InputEvent(Enum):
    """Abstract, backend-independent input (keyboard *and* joystick map to these)."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    FIRE = auto()          # space bar OR the joystick button (the original's "fire")
    SELECT_FULL = auto()   # the "1" shortcut (selection full-game AND welcome "1 ALIEN")
    SELECT_SHORT = auto()  # the "2" shortcut on the selection screen
    #: **Not the original**: "3" on the selection screen opens :attr:`Screen.
    #: MANUAL`. Bare, not a Ctrl chord - the chord requirement belongs to the
    #: ROM's own two options, which `$5F36` polls for; inventing a chord for an
    #: invented option would imitate the wrong half of the original.
    SELECT_INSTRUCTIONS = auto()
    #: **Not the original**: "4" on the selection screen opens
    #: :attr:`Screen.OPTIONS`.
    SELECT_OPTIONS = auto()
    #: **Not the original**: "5" on the selection screen opens
    #: :attr:`Screen.CREDITS`. A bare key, like `SELECT_INSTRUCTIONS` and
    #: `SELECT_OPTIONS` - the Ctrl chord belongs to the ROM's own two
    #: options, and inventing one for a third, invented row would
    #: imitate the wrong half of the original.
    SELECT_CREDITS = auto()
    YES = auto()           # "Y" on the instructions prompt
    NO = auto()            # "N" on the instructions prompt
    QUIT = auto()
    #: **Escape — back out to the top menu (DISC-261).** Not the original: the
    #: ROM has no abandon key, only `Q QUIT` on WELCOME. Distinct from
    #: :data:`QUIT` because Escape must not close the process.
    ABANDON = auto()
    #: The WELCOME menu's "Q QUIT" row specifically (D-175). Distinct from
    #: :data:`QUIT`, which still means "close the program" - on the real
    #: machine Q loads the EXITO advert and only then resets.
    QUIT_TO_ADVERT = auto()


# The front-end screens the app loop advances on the tick timer (no input),
# each paired with the screen it flows into and the constant that times it.
# The title and opening are timed too (see `_timed_next`).
def _timed_next(
    front_end: "FrontEnd" = None,  # type: ignore[assignment]
) -> dict["Screen", tuple[int, "Screen"]]:
    from .modes import FrontEnd as _FE

    if front_end is None:
        front_end = _FE.QUICK
    if front_end is _FE.QUICK:
        # **Four screens, in order (DISC-263).** The GREEN VALLEY publisher
        # spiral (`LOADING_MENU`), the back-up notice, the Joseph Conrad egg
        # title, then the game choice. Only the notice waits for a key.
        #
        # An earlier pass had this as title -> notice -> selection, which put
        # the publisher card after the game's own title and dropped the spiral
        # entirely. `LOADING_MENU` is the spiral; the "PLUG JOYSTICK INTO PORT
        # TWO" card that quick *does* skip is `LOADING_PLAY`, a different
        # screen with a confusingly similar name.
        return {
            Screen.BOOT: (constants.BOOT_TICKS, Screen.LOADING_MENU),
            Screen.LOADING_MENU: (constants.LOADING_MENU_TICKS, Screen.NOTICE),
            Screen.TITLE: (constants.TITLE_TICKS, Screen.GAME_SELECTION),
            Screen.OPENING: (constants.OPENING_TICKS, Screen.PLAYING),
            Screen.INTRO_LEGEND: (constants.INTRO_LEGEND_TICKS, Screen.OPENING),
        }
    return {
        Screen.BOOT: (constants.BOOT_TICKS, Screen.LOADING_MENU),
        Screen.LOADING_MENU: (constants.LOADING_MENU_TICKS, Screen.NOTICE),
        Screen.LOADING_PLAY: (constants.LOADING_PLAY_TICKS, Screen.TITLE),
        Screen.TITLE: (constants.TITLE_TICKS, Screen.GAME_SELECTION),
        Screen.OPENING: (constants.OPENING_TICKS, Screen.PLAYING),
        # EXITO's `FOR XX=1TO3000` then `SYS 64738`. **Corrected 2026-08-07:**
        # this used to loop back to LOADING_MENU on the reasoning that a cold
        # reset "restarts the machine". That is wrong for a remake. On the real
        # thing `SYS 64738` drops you to a bare BASIC READY prompt with the
        # game gone - it does not replay the loader. The honest equivalent for
        # a program that *is* only the game is to **quit**, which is also what
        # the player expects from a menu option labelled QUIT. So the advert
        # holds for its `FOR XX=1TO3000` and the app then exits.
        # (The successor is itself: `tick` sets `finished` and returns before
        # the transition is ever taken, so the advert stays on screen as the
        # program closes.)
        Screen.EXIT_ADVERT: (constants.EXIT_ADVERT_TICKS, Screen.EXIT_ADVERT),
        # $43D0's last delay_long then prompt_and_wait; the legend is timed
        # into its own PRESS ANY KEY, which `_on_intro_legend` consumes.
        Screen.INTRO_LEGEND: (constants.INTRO_LEGEND_TICKS, Screen.OPENING),
    }


#: **Not the original.** The timed cards Enter or Escape may skip past in the
#: updated version. The loading cards are on the list because they are the
#: first thing between launching the game and playing it, and a player who has
#: seen the publisher spiral once does not need fourteen more seconds of it;
#: the title is there for its own reason (`GameFlow.skip_card`).
#:
#: `NOTICE` is deliberately absent - it already waits for a key, so it is not a
#: timed card at all. `OPENING` is absent too: it is the game telling you who
#: died, which is information rather than a wait.
_SKIPPABLE_CARDS: frozenset["Screen"] = frozenset({
    Screen.LOADING_MENU, Screen.LOADING_PLAY, Screen.TITLE,
})

#: Screens that advance purely on the tick timer (no player input).
#: Every screen that advances on a timer under **either** front end.
#:
#: The union matters: `run_app` consults this to decide which screens tick, and
#: computing it from one front end's table silently froze the other's cards
#: (DISC-262). The quick chain does not time LOADING_MENU, so a classic boot sat
#: on it forever.
TIMED_SCREENS: frozenset[Screen] = frozenset(
    set(_timed_next(FrontEnd.CLASSIC)) | set(_timed_next(FrontEnd.QUICK))
)


# The two options on the game-selection screen, in on-screen order — the
# original's "Control:1 Full Game / Control:2 Short Scenario" (decoded from the
# PRG title text at $5F70/$5F87).
SELECTION_OPTIONS: tuple[tuple[str, GameMode], ...] = (
    ("FULL GAME", GameMode.FULL),
    ("SHORT SCENARIO", GameMode.SHORT),
)


def default_simulation(
    mode: GameMode,
    death_variant: DeathVariant,
    alien_start: AlienStart = AlienStart.ORIGINAL,
    jones_catch: JonesCatch = JonesCatch.PATIENT,
    android_variant: AndroidVariant = AndroidVariant.ORIGINAL,
    weapon_breach_gates: bool = False,
) -> Simulation:
    """Build a starting Simulation and initialise its awake-crew count.

    ``awake_crew`` (informational since FV-2.5/D-062 retired the invented
    oxygen system) is set to however many
    of the built roster start alive and awake — the correct home for what
    ``__main__`` used to patch by hand. Only touches a state the Simulation
    built itself (it always does here), never a caller-supplied one.
    """
    sim = Simulation(
        mode=mode, death_variant=death_variant, alien_start=alien_start,
        jones_catch=jones_catch, android_variant=android_variant,
        weapon_breach_gates=weapon_breach_gates,
    )
    sim.state.awake_crew = sum(
        1 for c in sim.state.crew.values() if c.alive and c.awake
    )
    return sim


class GameFlow:
    """The screen state machine: current screen + the active Simulation.

    Input is fed one :class:`InputEvent` at a time to :meth:`handle`; the app
    loop advances the Simulation while :attr:`screen` is ``PLAYING`` and calls
    :meth:`sync_phase` after each tick so a win/loss moves to the end screen.
    """

    def __init__(
        self,
        *,
        death_variant: DeathVariant = DeathVariant.ORIGINAL,
        sim_factory: SimFactory | None = None,
        front_end: FrontEnd = FrontEnd.QUICK,
        current_options: dict[str, str] | None = None,
        show_boot: bool = False,
        ask_edition: bool = False,
    ) -> None:
        self.front_end = front_end
        # Both front ends open on the publisher spiral; they diverge after the
        # back-up notice (DISC-263). The boot report, when there is one, goes
        # in front of that (B2/B5) — it is the remake's own screen and the only
        # thing before the loader.
        #: Where the loader starts once anything in front of it is done with.
        #: Held rather than recomputed so the first-run screen has somewhere
        #: definite to hand over to, and so the boot report is not skipped by
        #: being asked a question first.
        self._loader_start = Screen.BOOT if show_boot else Screen.LOADING_MENU
        self.screen = (
            Screen.FIRST_RUN if ask_edition else self._loader_start
        )
        #: Which answer the first-run question is sitting on.
        self.edition_row = 0
        # Which instruction page is showing (R-12/R-31; INSTRUCTION_PAGES only).
        self.instruction_page = 0
        #: Which page of the remake-only MANUAL screen is showing. Separate
        #: from `instruction_page` so opening the manual cannot disturb the
        #: boot chain's own position in the same text.
        self.manual_page = 0
        #: Which page of the CREDITS screen is showing (CR4).
        self.credits_page = 0
        #: The remake-only options screen's model. Seeded with what the game is
        #: actually running with, so the screen opens on the truth rather than
        #: on the defaults.
        self.options = OptionsModel(current_options)
        #: Called with the option map when the player leaves the options
        #: screen. The flow stays pure: persisting and applying are the app's
        #: job, and a headless test can pass nothing and still drive the screen.
        self.on_options_saved: Callable[[dict[str, str]], None] | None = None
        self.death_variant = death_variant
        self.sim: Simulation | None = None
        #: **T6 — how many turns have resolved, under `turns` mode only.**
        #: A presentation counter, not a simulation fact: real time counts
        #: ticks (`sim.state.tick`) regardless of pacing, but "turn 12" only
        #: means anything once the game is being paced by order-resolution
        #: rather than the clock. Maintained by `app.run_app`, read by the
        #: renderer; 0 under real-time pacing, where it is never drawn.
        self.turn_count = 0
        #: **Initiative order, under `turns` mode only (owner's request,
        #: 2026-09-05).** Every crew member plus the Alien and Jones,
        #: shuffled once when a turn-based game starts — see `_roll_initiative`.
        #: Empty under real-time pacing, where whose-turn-is-it has no meaning.
        self.turn_order: list[str] = []
        #: Index into `turn_order` — whose slot is live right now.
        self.turn_actor_index = 0
        #: Action points left in the *current* actor's slot
        #: (`constants.TURN_ACTIONS_PER_TURN` at the start of each one). Only
        #: meaningful for a crew actor; the Alien's and Jones's slots run on a
        #: tick budget instead (`app.run_app`), not a point count.
        self.turn_actions_left = 0
        self._sim_factory: SimFactory = sim_factory or default_simulation
        self._timed_next = _timed_next(front_end)
        # The mode chosen on the selection screen (only meaningful once a game
        # has started); the real selection screen has NO live cursor — see
        # `_on_selection` — so there is no `selection_index` any more.
        self._chosen_mode: GameMode = GameMode.FULL
        #: Set once the Q/QUIT advert has held its `FOR XX=1TO3000`; the app
        #: loop polls it and closes (EXITO's `SYS 64738`).
        self.finished = False
        # Ticks elapsed on the current *timed* screen (TITLE / OPENING). The
        # real title auto-advances and the opening death notice clears on a
        # timeout, with no press-to-continue (R-30 / R-13, live-confirmed).
        self._screen_ticks = 0

    @property
    def selected_mode(self) -> GameMode:
        return self._chosen_mode

    @property
    def title_letters_shown(self) -> int:
        """How many of the 5 "ALIEN" title letters have animated in (0..5).

        The original spells the title out one reverse-video letter at a time with
        a delay between each (`$5E90`); the renderer reveals the first N letters
        of "ALIEN". Off the title screen the word is fully shown.
        """
        if self.screen is not Screen.TITLE:
            return 5
        return min(5, self._screen_ticks // constants.TITLE_LETTER_TICKS + 1)

    def handle(self, event: InputEvent) -> None:
        """Route one input event through the current screen's transitions.

        ``QUIT`` is a loop concern (the backend flips its own quit flag); the
        flow simply ignores it here. The TITLE and OPENING screens are **timed**
        (see :meth:`tick`) and consume no input — matching the original, which
        has no press-to-continue on either.
        """
        if event is InputEvent.QUIT:
            return
        if event is InputEvent.ABANDON:
            # **The title card's skip (owner, 2026-08-29).** Escape here means
            # "get on with it", not "abandon" — there is no game yet to back
            # out of. Taken before the abandon branch so it cannot be read as
            # one, and refused outright under ORIGINAL, where the card is 25
            # seconds because the disk's is.
            if self.screen in _SKIPPABLE_CARDS:
                if self.skip_card():
                    return
            # Escape does not back out of the first-run question, because there
            # is nowhere behind it and no unanswered state to go on with — it
            # takes whichever answer is highlighted, the same as fire.
            if self.screen is Screen.FIRST_RUN:
                self._on_first_run(InputEvent.FIRE)
                return
            # The two remake-only screens back out to the selection screen they
            # were opened from. They hold no game, so `abandon()`'s "drop the
            # simulation" path is not what they want - and on OPTIONS, leaving
            # is also what commits the choices.
            if self.screen is Screen.MANUAL:
                self._leave_manual()
                return
            if self.screen is Screen.OPTIONS:
                self._leave_options()
                return
            if self.screen is Screen.CREDITS:
                self._leave_credits()
                return
            # Backs out of a game in progress; on WELCOME there is nothing to
            # back out of and `abandon()` says so, leaving the caller's quit
            # decision alone.
            self.abandon()
            return
        if self.screen in _SKIPPABLE_CARDS:
            # Timed cards that take no input in the original. Enter (FIRE) or
            # Escape skips them in the updated version only - see `skip_card`.
            if event is InputEvent.FIRE:
                self.skip_card()
        elif self.screen is Screen.FIRST_RUN:
            self._on_first_run(event)
        elif self.screen is Screen.BOOT:
            self._on_boot(event)
        elif self.screen is Screen.NOTICE:
            self._on_notice(event)
        elif self.screen is Screen.WELCOME:
            self._on_welcome(event)
        elif self.screen is Screen.INTRO_PROMPT:
            self._on_intro_prompt(event)
        elif self.screen is Screen.INTRO_LEGEND:
            self._on_intro_legend(event)
        elif self.screen is Screen.INSTRUCTIONS:
            self._on_instructions(event)
        elif self.screen is Screen.INSTRUCTION_PAGES:
            self._on_instruction_pages(event)
        elif self.screen is Screen.GAME_SELECTION:
            self._on_selection(event)
        elif self.screen is Screen.MANUAL:
            self._on_manual(event)
        elif self.screen is Screen.OPTIONS:
            self._on_options(event)
        elif self.screen is Screen.CREDITS:
            self._on_credits(event)
        elif self.screen is Screen.ENDED:
            self._on_ended(event)
        # LOADING_* / TITLE / OPENING are timed (tick); PLAYING polls separately.

    def tick(self) -> None:
        """Advance the timed cards (loading interstitials, title, opening).

        The app loop calls this every frame while on a screen in
        :data:`TIMED_SCREENS`. Each such screen auto-advances to its successor
        after its configured number of ticks — the two "LOADING…" cards, the
        animated TITLE (R-30: timed + animated, not press-to-continue), and the
        OPENING death notice all clear on a timeout, never on input.
        """
        transition = self._timed_next.get(self.screen)
        if transition is None:
            return
        threshold, nxt = transition
        self._screen_ticks += 1
        # **[C EXITO 1100/4000] the advert holds, then the program ends.**
        # `FOR XX=1TO3000` then `SYS 64738`. A reset leaves a bare BASIC READY
        # prompt with the game gone, so for a program that *is* only the game
        # the faithful equivalent is to exit - not to replay the loader.
        if (
            self.screen is Screen.EXIT_ADVERT
            and self._screen_ticks >= constants.EXIT_ADVERT_TICKS
        ):
            self.finished = True
            return
        if self._screen_ticks >= threshold:
            self._screen_ticks = 0
            self.screen = nxt

    def _on_notice(self, event: InputEvent) -> None:
        """ShareData back-up notice — any key ("PRESS ANY KEY TO CONTINUE").

        CLASSIC goes on to the WELCOME menu, as the loader does. QUICK goes
        straight to the selection: the notice is the second of its three
        screens (DISC-262).
        """
        if event in (InputEvent.FIRE, InputEvent.SELECT_FULL, InputEvent.YES,
                     InputEvent.NO):
            self._screen_ticks = 0
            self.screen = (
                Screen.WELCOME if self.front_end is FrontEnd.CLASSIC
                else Screen.TITLE
            )

    def _on_welcome(self, event: InputEvent) -> None:
        """"WELCOME TO ALIEN" menu - **[C MENU1 lines 730-833] D-175.**

        Two options, and only two: line 895's `DATA1,15` sets `NM=1` so the
        numbered list is just "1 ALIEN", and line 690 prints a fixed `Q QUIT`
        row beneath it.

        `1` goes to the instructions prompt (line 770 `IFCC<>0THENGOSUB10000`).
        **`Q` does not exit** - line 740 sets `CC=0` and `P$(0)="EXIT*"`, which
        skips both the instructions prompt and the "PLUG JOYSTICK" line, then
        line 830 loads EXITO. The remake used to route Q straight to
        `InputEvent.QUIT` and close the window, which is the behaviour the
        player reported as wrong.
        """
        if event is InputEvent.SELECT_FULL:            # the "1 ALIEN" option
            self.screen = Screen.INSTRUCTIONS
        elif event is InputEvent.QUIT_TO_ADVERT:       # the "Q QUIT" row
            self.screen = Screen.EXIT_ADVERT

    def _on_intro_prompt(self, event: InputEvent) -> None:
        """"DO YOU WANT AN INTRODUCTION / PRESS Y OR N" - **[C $4405] D-176.**

        `$441F LDA $C5 / CMP #$19 / BEQ` takes Y to the DECK PLAN KEY screen;
        `$4425 CMP #$27 / BEQ` takes N straight on to the game. Anything else
        loops (`$4429 JMP $441F`), so the prompt really does wait for one of
        the two keys.
        """
        if event is InputEvent.YES:
            self.screen = Screen.INTRO_LEGEND
        elif event is InputEvent.NO:
            self.screen = Screen.OPENING

    def _on_intro_legend(self, event: InputEvent) -> None:
        """The legend ends on `prompt_and_wait ($43E5)` - any key."""
        if event in (InputEvent.FIRE, InputEvent.SELECT_FULL, InputEvent.YES,
                     InputEvent.NO):
            self.screen = Screen.OPENING

    def _on_instructions(self, event: InputEvent) -> None:
        """"DO YOU WANT INSTRUCTIONS? (Y OR N)".

        **Y now shows the real instruction pages** (R-12/R-31's last open
        piece; it used to be a stub that behaved like N). N skips straight to
        the "LOADING…/PLUG JOYSTICK" card -> title, as before. If the SEQ file
        isn't present, Y degrades to N rather than showing an empty screen.
        """
        if event is InputEvent.YES and instructions.pages():
            self._screen_ticks = 0
            self.instruction_page = 0
            self.screen = Screen.INSTRUCTION_PAGES
        elif event in (InputEvent.NO, InputEvent.YES, InputEvent.FIRE):
            self._screen_ticks = 0
            self.screen = Screen.LOADING_PLAY

    def _on_instruction_pages(self, event: InputEvent) -> None:
        """Any key turns the page; past the last one the boot chain resumes."""
        if event not in (InputEvent.YES, InputEvent.NO, InputEvent.FIRE,
                         InputEvent.SELECT_FULL, InputEvent.SELECT_SHORT):
            return
        self.instruction_page += 1
        if self.instruction_page >= len(instructions.pages()):
            self._screen_ticks = 0
            self.screen = Screen.LOADING_PLAY

    def skip_card(self) -> bool:
        """Enter or Escape on a timed front-end card. **Not the original.**

        Two cards answer to this. The **loading card** you meet first (the
        GREEN VALLEY spiral, and the PLUG JOYSTICK card on the classic chain)
        simply advances - there is nothing on it to finish, so one press is the
        whole story.

        The **title** is the interesting one and keeps its two-step behaviour:

        Two presses, two different things, which is the whole of the owner's
        request:

        * **while the word is still spelling out** — jump to the moment the
          fifth letter lands (:data:`~alien_remake.core.constants.
          TITLE_REVEALED_TICKS`) and stop there. The card then holds and times
          out exactly as it would have: what is left is the ROM's three
          trailing `delay_long`s, about 12 seconds of the finished logo. So the
          skip removes the *waiting to read it*, not the card.
        * **once it is complete** — go to the next screen now.

        Returns whether it did anything, so the caller can tell a skip from a
        press that should fall through to its ordinary meaning (Escape's, off
        this screen, is abandon).

        **Refused under ORIGINAL.** The 25-second title is 25 seconds because
        the disk's is — eight `delay_long`s — and a way to cut it short is an
        addition like any other. `options.is_original` is the same question the
        mouse asks, deliberately: one definition of "the original".
        """
        if self.screen not in _SKIPPABLE_CARDS:
            return False
        if is_original(self.options.values):
            return False
        if self.screen is not Screen.TITLE:
            # A loading card has no reveal to finish; one press advances it.
            return self._advance_card()
        if self._screen_ticks < constants.TITLE_REVEALED_TICKS:
            self._screen_ticks = constants.TITLE_REVEALED_TICKS
            return True
        return self._advance_card()

    def _advance_card(self) -> bool:
        """Go to whatever this timed card flows into, now."""
        transition = self._timed_next.get(self.screen)
        if transition is None:
            return False
        self._screen_ticks = 0
        self.screen = transition[1]
        return True

    def _on_first_run(self, event: InputEvent) -> None:
        """The first-run question: pick an edition, and that is the last of it.

        Any of the four directions moves between the two answers — the list is
        vertical but a player reaching for left/right on two side-by-side ideas
        is not wrong, and there is nothing else here for those keys to do.
        "1" and "2" pick outright, matching every other numbered choice in the
        game.

        Choosing applies the whole profile and commits it, which is what makes
        this the *first*-run question rather than every-run: `on_options_saved`
        writes the settings file, and a settings file is exactly what stops it
        being asked again.
        """
        if event in (InputEvent.UP, InputEvent.LEFT):
            self.edition_row = (self.edition_row - 1) % len(EDITIONS)
            return
        if event in (InputEvent.DOWN, InputEvent.RIGHT):
            self.edition_row = (self.edition_row + 1) % len(EDITIONS)
            return
        if event is InputEvent.SELECT_FULL:
            self.edition_row = 0
        elif event is InputEvent.SELECT_SHORT:
            self.edition_row = 1
        elif event is not InputEvent.FIRE:
            return
        self.choose_edition(self.edition_row)

    def choose_edition(self, index: int) -> None:
        """Apply the chosen edition and start the loader.

        Public because the answer is not only ever given by a key: the pointer
        clicks a row, and both must go through the one path that applies the
        profile *and* commits it. An answer that applied without saving would
        ask again next launch, which is the one thing this screen must not do.
        """
        edition = EDITIONS[index % len(EDITIONS)]
        self.options.apply_profile(edition.profile)
        self._commit_options()
        self._screen_ticks = 0
        self.screen = self._loader_start

    def _on_boot(self, event: InputEvent) -> None:
        """Any key or click leaves the boot report and starts the loader.

        It also auto-advances (see `_timed_next`), so a report nobody dismisses
        does not strand the game — the point is to be readable, not to be a
        gate.
        """
        self._screen_ticks = 0
        self.screen = Screen.LOADING_MENU

    def _on_selection(self, event: InputEvent) -> None:
        """Game-selection input — Ctrl+1 / Ctrl+2 ONLY (D-018 live-confirmed
        `$5F36` polls keyboard latch `$91` for exactly these two chords).

        The invented up/down cursor, ">" marker, and fire-select are correctly
        removed here (this module only sees the already-classified
        ``SELECT_FULL``/``SELECT_SHORT`` events, not raw keys).

        The CHORD requirement is enforced in the backend, where the raw key and
        its modifiers are still visible: `render/pygame_app.py` drops
        `SELECT_FULL`/`SELECT_SHORT` on GAME_SELECTION unless `KMOD_CTRL` is
        held. WELCOME's "1 ALIEN" is genuinely bare and stays unmodified. (FV-1c1
        found this unenforced and FV-1c2 fixed it; the gap notice that used to
        stand here outlived the gap by a month.)
        """
        if event is InputEvent.SELECT_FULL:
            self._start(GameMode.FULL)
        elif event is InputEvent.SELECT_SHORT:
            self._start(GameMode.SHORT)
        elif event is InputEvent.SELECT_INSTRUCTIONS:
            self.manual_page = 0
            self._screen_ticks = 0
            self.screen = Screen.MANUAL
        elif event is InputEvent.SELECT_OPTIONS:
            self.options.row = 0
            self._screen_ticks = 0
            self.screen = Screen.OPTIONS
        elif event is InputEvent.SELECT_CREDITS:
            # **Hidden under ORIGINAL** (owner). The standing rule is that
            # ORIGINAL never hides the remake's own screens - MANUAL and
            # OPTIONS are how you get back to the game if you land on one by
            # accident, so both stay reachable regardless of preset. CREDITS
            # is not a way back, and crediting supplied media that ORIGINAL
            # has none of would be a screen advertising additions that are
            # switched off. The renderer does not draw this row under
            # ORIGINAL; this branch is the second half of "hidden", the one
            # a stray keypress cannot bypass - a row that still answers when
            # it is not shown would be worse than no row at all.
            if is_original(self.options.as_dict()):
                return
            self.credits_page = 0
            self._screen_ticks = 0
            self.screen = Screen.CREDITS

    # --- the two remake-only screens ---------------------------------------

    def manual_pages(self) -> int:
        """How many pages the MANUAL screen has: the loader's instruction text
        plus one for the deck-plan key and sound legend.

        The legend is a single page because that is how the ROM shows it — one
        screen teaching both halves of the display — so it needs no paging of
        its own, only a place at the end.
        """
        return len(instructions.pages()) + 1

    @property
    def manual_showing_legend(self) -> bool:
        """True on the last page, where the deck-plan key replaces the text."""
        return self.manual_page >= len(instructions.pages())

    def _on_manual(self, event: InputEvent) -> None:
        """Any key turns the page; past the last one, back to the selection."""
        if event not in (InputEvent.YES, InputEvent.NO, InputEvent.FIRE,
                         InputEvent.SELECT_FULL, InputEvent.SELECT_SHORT,
                         InputEvent.SELECT_INSTRUCTIONS,
                         InputEvent.SELECT_OPTIONS, InputEvent.RIGHT,
                         InputEvent.DOWN):
            # Left/up page backwards, so a reader who overshoots is not made to
            # cycle the whole manual to get back.
            if event in (InputEvent.LEFT, InputEvent.UP):
                self.manual_page = max(0, self.manual_page - 1)
            return
        self.manual_page += 1
        if self.manual_page >= self.manual_pages():
            self._leave_manual()

    def _leave_manual(self) -> None:
        self.manual_page = 0
        self._screen_ticks = 0
        self.screen = Screen.GAME_SELECTION

    def credits_pages(self) -> int:
        """How many pages CREDITS has, at `CREDITS_ROWS_PER_PAGE` rows each.

        Reuses `media.credits_lines()` rather than a page count of its own,
        so a supplied file appearing or disappearing (or a long line
        wrapping to two) changes the page count for free instead of needing
        a second place updated. Counted in *lines*, not entries — an entry
        with a wrapped URL takes more than one row, same as `_draw_credits`.
        """
        from .. import media

        rows = len(media.credits_lines())
        return max(1, -(-rows // CREDITS_ROWS_PER_PAGE))

    def _on_credits(self, event: InputEvent) -> None:
        """Any key turns the page; past the last one, back to the selection.

        **The exact shape of `_on_manual`** (CR4: "reuse that rather than
        inventing a third scrolling mechanism"). Left/up page backwards for
        the same reason: a reader who overshoots should not have to cycle
        the whole list to get back.
        """
        if event in (InputEvent.LEFT, InputEvent.UP):
            self.credits_page = max(0, self.credits_page - 1)
            return
        self.credits_page += 1
        if self.credits_page >= self.credits_pages():
            self._leave_credits()

    def _leave_credits(self) -> None:
        self.credits_page = 0
        self._screen_ticks = 0
        self.screen = Screen.GAME_SELECTION

    def _on_options(self, event: InputEvent) -> None:
        """Up/down pick a row, left/right change its value, fire leaves.

        Changing a value takes effect the moment it changes rather than on
        leaving: `on_options_saved` is what persists, and the app applies what
        it can live, so a player can see `crt` change under them while the
        screen is still open.
        """
        if event in (InputEvent.UP, InputEvent.DOWN):
            self.options.move(-1 if event is InputEvent.UP else 1)
        elif event in (InputEvent.LEFT, InputEvent.RIGHT):
            self.options.change(-1 if event is InputEvent.LEFT else 1)
            self._commit_options()
        elif event in (InputEvent.FIRE, InputEvent.NO):
            self._leave_options()

    def _leave_options(self) -> None:
        self._commit_options()
        self._screen_ticks = 0
        self.screen = Screen.GAME_SELECTION

    def _commit_options(self) -> None:
        """Hand the current selection to whoever is listening (the app)."""
        if self.on_options_saved is not None:
            self.on_options_saved(self.options.as_dict())

    def _start(self, mode: GameMode) -> None:
        """Begin a game — **[C $5F3F/$5F51 -> $7013 start_game] D-176.**

        Selecting a mode writes it to `$4303` (1 = FULL, 2 = SHORT) and jumps
        to `start_game`, which calls `game_init_mode ($4304)`. That routine
        branches on the mode: **FULL returns immediately**, while **SHORT** goes
        to `$4405` and asks "DO YOU WANT AN INTRODUCTION". So the introduction
        is not a general front-end screen — it belongs to the SHORT scenario,
        which is the beginner one, and the FULL game never offers it.
        """
        self._chosen_mode = mode
        self.sim = self._sim_factory(mode, self.death_variant)
        self._screen_ticks = 0
        self.turn_count = 0
        if self.options.values.get("turns") == "on":
            self._roll_initiative()
        else:
            self.turn_order = []
        self.screen = (
            Screen.INTRO_PROMPT if mode is GameMode.SHORT else Screen.OPENING
        )

    def _roll_initiative(self) -> None:
        """Shuffle the initiative order for a new turn-based game.

        **Not the original** (owner's request, 2026-09-05): every crew
        member plus the Alien and Jones, in one random order fixed for the
        whole game — rolled from `self.sim.rng` so a seeded game's turn
        order reproduces along with everything else about it.
        """
        assert self.sim is not None
        participants = list(self.sim.state.crew.keys()) + [
            constants.TURN_ALIEN_ACTOR, constants.TURN_JONES_ACTOR,
        ]
        self.sim.rng.shuffle(participants)
        self.turn_order = participants
        self.turn_actor_index = 0
        self.turn_actions_left = self._turn_actions_per_turn()

    def _turn_actions_per_turn(self) -> int:
        """How many action points a turn starts with (DEC-045).

        `constants.TURN_ACTIONS_PER_TURN` (the ROM has no turn-based mode at
        all, so there is no decoded value to preserve either way) under
        ORIGINAL; `UPDATED_TURN_ACTIONS_PER_TURN` under UPDATED, keyed on
        the same `weapon_breach_gates` flag DEC-044 already uses for "is
        this the Updated combat model" — DEC-044's gate-aware retreat makes
        turn-based UPDATED harder than real-time at the ROM-adjacent default
        (a retreat spends a whole action point landing no hit), so it needed
        its own re-swept number the same way `ALIEN_DAMAGE_TO_KILL` did.
        """
        updated = self.sim is not None and self.sim.weapon_breach_gates
        return (
            constants.UPDATED_TURN_ACTIONS_PER_TURN if updated
            else constants.TURN_ACTIONS_PER_TURN
        )

    def current_turn_actor(self) -> str | None:
        """Whose initiative slot is live, or `None` outside `turns` mode."""
        if not self.turn_order:
            return None
        return self.turn_order[self.turn_actor_index % len(self.turn_order)]

    def advance_turn_actor(self) -> None:
        """Pass initiative to the next name in `turn_order`, wrapping."""
        if not self.turn_order:
            return
        self.turn_actor_index = (self.turn_actor_index + 1) % len(self.turn_order)
        self.turn_actions_left = self._turn_actions_per_turn()

    def set_front_end(self, front_end: FrontEnd) -> None:
        """Switch boot chains — the options screen's `front_end` row.

        The timed-transition table is per front end, so it has to be rebuilt
        with it; leaving the old one behind is how a classic boot ends up
        sitting forever on a card the quick chain never times (DISC-262).
        Changing this mid-run only affects screens not yet shown, which for a
        player on the options screen means the next boot and this selection
        screen's own prompt.
        """
        self.front_end = front_end
        self._timed_next = _timed_next(front_end)

    def abandon(self) -> bool:
        """Drop the game in progress and return to the top menu.

        **Not the original (DISC-261).** The ROM has no abandon key: the only
        way out is `Q QUIT` on WELCOME, and the end screen's own path back is
        `$646F -> $5E74` to TITLE. Escape used to end the *process*, which is a
        harsher thing than any key in the original does and loses the front end
        with it.

        Returns ``False`` when there is nothing to abandon — already on WELCOME
        — so the caller can decide what Escape means there. Deliberately not
        "quit if pressed twice": ending the program is `Q QUIT`'s job, and an
        accidental double-tap should not close the game.
        """
        home = (
            Screen.WELCOME if self.front_end is FrontEnd.CLASSIC
            else Screen.GAME_SELECTION
        )
        if self.screen is home:
            return False
        self.sim = None
        self._chosen_mode = GameMode.FULL
        self._screen_ticks = 0
        self.screen = home
        return True

    def _on_ended(self, event: InputEvent) -> None:
        # The end screen waits for ANY key ("press any key", live-confirmed R-33).
        # The original's game-over path returns to the title routine ($646F →
        # $5E74), not through the whole front-end, so restart at TITLE.
        if event in (InputEvent.FIRE, InputEvent.SELECT_FULL, InputEvent.YES,
                     InputEvent.NO):
            self.screen = Screen.TITLE
            self.sim = None
            self._chosen_mode = GameMode.FULL
            self._screen_ticks = 0

    def sync_phase(self) -> None:
        """Move to the end screen once the running game has been won or lost."""
        if (
            self.screen is Screen.PLAYING
            and self.sim is not None
            and self.sim.state.phase is not GamePhase.RUNNING
        ):
            self.screen = Screen.ENDED
            # **screen_fx (2026-09-04), not the original.** Every other screen
            # transition in this file resets `_screen_ticks`; this one didn't
            # need to before because `_draw_end` never read it. The wipe-in
            # does, so it has to start counting from the moment the ending
            # was actually reached, not carry over PLAYING's own tick count.
            self._screen_ticks = 0
