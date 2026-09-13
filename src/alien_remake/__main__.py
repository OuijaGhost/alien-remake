"""Entry point: ``python -m alien_remake``.

Default launches the pygame shell. ``--headless TICKS`` runs that many ticks with
the :class:`NullRenderer` and prints the final state — needs no pygame, so CI,
tests, and machines without the optional dependency can still exercise the core.
``--mode``/``--death`` select the game length and opening-death variant (GAME_SPEC §9) — this doubles as the mode-selection front end the disassembly
found is otherwise ``[I]`` inside ``ALIEN`` itself, after ``SYS 16384``.
"""

from __future__ import annotations

from dataclasses import dataclass

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from collections.abc import Iterator
from typing import NamedTuple

from . import assets
from .startup import StartupReport, install_crash_log
from .app import run_app
from .core.flow import GameFlow, default_simulation
from .core.modes import (
    AlienStart, AndroidVariant, DeathVariant, FrontEnd, GameMode, JonesCatch,
)
from .core.sim import Simulation
from .render.base import NullRenderer, Renderer
from .runner import run_realtime, run_turn_based


class DeriveStep(NamedTuple):
    """One line of progress from :func:`derive_assets_from`.

    ``label`` is what to show a human; ``ok`` is whether it succeeded (a failed
    *optional* step, like the BASIC listing, still reports ``ok=True`` - it is
    a convenience, not a requirement to reach the game). The CLI path prints
    each one as it arrives; a future in-game screen renders the same sequence
    instead of scraping stdout or shelling out to watch a subprocess.
    """

    label: str
    ok: bool


def derive_assets_from(nib: Path) -> "Iterator[DeriveStep]":
    """Do the actual derivation, yielding one :class:`DeriveStep` per stage.

    **The reusable core F-1 needs.** Everything `--derive-assets` does, with no
    dependency on stdout, argv, or being run as a subprocess - a generator, so
    a caller can show each step as it happens (a CLI print, or a progress line
    on a future first-run screen) without the two ever needing to agree on a
    text format to scrape. Raises nothing a caller has to catch for the
    required steps to be considered failed: that is `ok=False` on the yielded
    step, exactly once, and the generator still returns afterward so the caller
    decides whether to stop.
    """
    from alientools.cli import main as alientools_main

    for step, argv_ in (
        ("extracting the disk", ["extract", str(nib), "--out", "out"]),
        # **Pass the image through.** `chars` defaults to the .nib filename, so
        # leaving it off worked only for users who happened to have that exact
        # file: a .d64 or .g64 owner got "file not found" and no charset.
        ("decoding the charset and sprites", ["chars", str(nib)]),
    ):
        yield DeriveStep(step, alientools_main(argv_) == 0)

    from .audio.intro import DEFAULT_OUT, DEFAULT_PRG, render_intro, write_wav

    if DEFAULT_PRG.exists():
        write_wav(render_intro(DEFAULT_PRG), DEFAULT_OUT)
        yield DeriveStep("rendering the SID intro", True)
    else:
        yield DeriveStep("rendering the SID intro (skipped: ALIEN.prg missing)", True)

    from .audio import sfx

    written = sfx.export_all(Path("out"))
    yield DeriveStep(f"rendering the sound effects ({len(written)} clips)", True)

    # **The loader's BASIC, as a readable listing.** Nothing in the game reads
    # it; two tests do, so without it a fresh clone *failed* the `out/` guard
    # rather than skipping - found 2026-08-30 by installing into an empty
    # folder. Best-effort: it is a convenience for running the suite, and a
    # first run that could not produce it should still reach the game, hence
    # `ok=True` regardless of what happens inside this block.
    try:
        import subprocess

        tool = Path(__file__).resolve().parent.parent.parent / "tools" / "basic_listing.py"
        if tool.is_file():
            subprocess.run([sys.executable, str(tool)], check=False,
                           capture_output=True)
            listing = Path("out") / "MENU1_EXITO.bas.txt"
            made = listing.is_file()
        else:
            made = False
    except Exception:                    # pragma: no cover - convenience only
        made = False
    yield DeriveStep(
        "listing the loader's BASIC" + ("" if made else " (skipped)"), True
    )


def _derive_assets(nib_arg: str | None) -> int:
    """The CLI face of :func:`derive_assets_from`: print each step, then report.

    Deliberately *not* automatic on launch: it writes ~9 MB and takes a few
    seconds, and a game that silently starts doing that is worse than one that
    tells you what to run. (A first-run *screen* that asks first, per F-1, is
    not the same thing as doing it silently - that is the feature this
    function's twin exists to support.)
    """
    nib = Path(nib_arg) if nib_arg else _find_nib()
    if nib is None or not nib.exists():
        print(
            "alien-remake: no disk image found (.nib, .g64 or .d64). Pass one:",
            '  python -m alien_remake --derive-assets "path/to/Alien.d64"',
            sep="\n",
            file=sys.stderr,
        )
        return 2

    print(f"alien-remake: deriving assets from {nib.name}")
    for step in derive_assets_from(nib):
        print(f"  {step.label}...")
        if not step.ok:
            print(f"alien-remake: {step.label} failed", file=sys.stderr)
            return 1

    absent = assets.report()
    if absent:
        # ASCII only, like `assets.report()` itself: a default Windows console
        # is cp1252 (DISC-241).
        print(
            "",
            "Still missing. These are C64 *system* ROMs, not on the Alien disk"
            " - supply them from your own machine or a VICE install:",
            *absent,
            sep="\n",
            file=sys.stderr,
        )
    else:
        print("\nalien-remake: everything derived. Run `python -m alien_remake`.")
    return 0


def _first_run_asset_wizard() -> bool:
    """A native file picker + progress window for a first run with no
    derived assets (F-1). **Not the original** — there is nothing here for
    the ROM to have a say in, since the disk never offered this either.

    **Native OS dialog, not an in-game C64-styled browser** — the design
    choice this pass did not make for you (see `todo.md`, F-1), decided
    here: the picker has to search the player's whole filesystem for a file
    that could be anywhere, and a native dialog already does that (recent
    files, search, drive navigation) far better than anything worth
    building from scratch for a once-per-install action with no fidelity
    stakes either way.

    Returns True if assets were actually derived (the caller's subsequent
    `assets.report()` will then find them), False if the user skipped,
    cancelled, or tkinter is unavailable — the game still runs exactly as it
    always has, printing the same "missing derived data" message instead.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:  # pragma: no cover - platform-dependent, not this repo's call
        return False

    root = tk.Tk()
    root.title("Alien - first run")
    root.resizable(False, False)
    chosen: list[Path] = []

    def browse() -> None:
        path = filedialog.askopenfilename(
            parent=root, title="Choose your Alien disk image",
            filetypes=[("C64 disk images", "*.nib *.g64 *.d64"),
                       ("All files", "*.*")],
        )
        if path:
            chosen.append(Path(path))
            root.quit()

    def skip() -> None:
        root.quit()

    tk.Label(
        root, padx=16, pady=12, justify="left",
        text=(
            "Alien needs your own disk image to run.\n"
            "No game data is distributed with this project -\n"
            "point it at a .nib, .g64 or .d64 of the original disk."
        ),
    ).pack()
    buttons = tk.Frame(root, pady=8)
    tk.Button(buttons, text="Browse...", command=browse, width=12).pack(
        side="left", padx=6)
    tk.Button(buttons, text="Skip", command=skip, width=12).pack(
        side="left", padx=6)
    buttons.pack()
    root.protocol("WM_DELETE_WINDOW", skip)
    root.eval("tk::PlaceWindow . center")
    root.mainloop()

    if not chosen:
        root.destroy()
        return False

    nib = chosen[0]
    # Reused for the progress display rather than a second window - one
    # dialog for the whole first run, not two.
    for widget in root.winfo_children():
        widget.destroy()
    progress = tk.Label(
        root, padx=16, pady=16, justify="left", text=f"Reading {nib.name}..."
    )
    progress.pack()
    root.deiconify()
    root.update()

    ok = True
    # **Advanced one step per `update()`, not run to completion first.** This
    # is the same generator `--derive-assets` prints from the CLI
    # (`derive_assets_from`); driving it here rather than blocking on it
    # whole is what turns "printing a path and a command" into an actual
    # progress line, per F-1's own wording.
    for step in derive_assets_from(nib):
        progress.config(text=f"{step.label}...")
        root.update()
        if not step.ok:
            ok = False
            break
    progress.config(
        text="Done." if ok else
        f"{step.label} failed - see the console for details."
    )
    root.update()
    root.after(900 if ok else 2500, root.quit)
    root.mainloop()
    root.destroy()
    return ok


def _find_nib() -> Path | None:
    """The user's disk image, if it is sitting somewhere obvious.

    Any supported format - `.nib` preferred because it carries the protection,
    then `.g64`, then `.d64`.
    """
    from alientools import diskimage

    for directory in (Path.cwd(), Path(__file__).resolve().parent.parent.parent):
        found = diskimage.find(directory)
        if found is not None:
            return found
    return None


@dataclass
class _LiveRules:
    """The simulation flags the in-game options screen can change.

    Mutable and read at game-start time, so a change on that screen applies to
    the next game rather than the next launch. None is consulted by a game
    already running: the ROM fixes all of them at `new_game`, and changing one
    under a live simulation would be a behaviour the original has no
    equivalent for — the opening death and the android are *drawn once*, at
    the opening, so there is nothing to re-decide mid-game.
    """

    alien_start: AlienStart
    jones: JonesCatch
    death: DeathVariant
    android: AndroidVariant
    #: DEC-044 — not its own options row. Keyed on the whole profile, the
    #: same way `options.pointer_allowed` keys the mouse: any single row off
    #: ORIGINAL already means "not ORIGINAL", and a game that cannot be won
    #: is exactly the kind of thing that precedent exists to keep off the
    #: one preset that has to match the disk exactly.
    weapon_breach_gates: bool


def _build_parser() -> argparse.ArgumentParser:
    """The command-line parser, on its own so it can be inspected.

    Split out of `main` because the in-game options screen mirrors four of
    these flags, and `test_options_screen.py` reads the choices off the parser
    itself rather than restating them — a restated list agrees with itself and
    nothing else.
    """

    parser = argparse.ArgumentParser(
        prog="alien-remake",
        description="Faithful remake of the 1984 C64 game 'Alien' (work in progress).",
    )
    parser.add_argument(
        "--headless",
        type=int,
        metavar="TICKS",
        help="run TICKS ticks with no window and print the final state (no pygame)",
    )
    parser.add_argument(
        "--headless-turns",
        type=int,
        metavar="TURNS",
        help=(
            # ASCII only: argparse prints this to a cp1252 console (DISC-241).
            "like --headless, but paced in TURNS instead of ticks. One turn is "
            "'advance until an order resolves' (DISC-292), so a turn spans "
            "however many ticks the action really took - a room move is 64 to "
            "74 of them. Ticks are unchanged, so every timed thing in the game "
            "behaves exactly as it does in real time"
        ),
    )
    parser.add_argument(
        "--awake-crew",
        type=int,
        default=None,
        metavar="N",
        help=(
            "override how many crew are out of hypersleep "
            "each tick, GAME_SPEC s.7); default: however many of the starting "
            "seven-crew roster start awake (all but the one already dead)"
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("full", "short"),
        default="full",
        help=(
            "game length (GAME_SPEC s.9/s.11 #6): 'full' (all decks) "
            "or 'short' (fewer decks)"
        ),
    )
    parser.add_argument(
        "--death",
        # Same order the options screen cycles them in, which
        # `test_options_screen.py` enforces: the ROM's own behaviour first,
        # the added rule next, the testing aid last.
        choices=("original", "random", "fixed"),
        default="original",
        help=(
            "which crew member is already dead at the opening (GAME_SPEC s.9): "
            "'random' (the ROM's only real behaviour, D-170/PV-20 - it draws "
            "from a three-name table at $50EC, so only Dallas, Kane or Lambert "
            "can ever be the one found dead), 'any' (an added rule, NOT the "
            "original: draw from the whole crew, so Ripley, Ash, Parker or "
            "Brett can open dead too), or 'fixed' (always Lambert, a "
            "remake-only testing aid - NOT a fidelity claim)"
        ),
    )
    parser.add_argument(
        "--sound",
        choices=("off", "game", "all"),
        default="game",
        help=(
            "'off' is silent; 'game' plays the original's own effects, decoded "
            "from its SID writes; 'all' adds menu and boot sounds the original "
            "does not have, played from .wav files you put in a 'sounds' "
            "folder beside the other derived data. NOT the original"
        ),
    )
    parser.add_argument(
        "--game-audio",
        choices=("original", "enhanced"),
        default="original",
        help=(
            "where the game's own effects come from and how they mix: "
            "'original' emulates the SID from the code itself and leaves "
            "mixing exactly as it always was. 'enhanced' (renamed from "
            "'sampled' 2026-09-05) plays your own recordings from the "
            "'sounds' folder instead (44.1 kHz stereo or better), falling "
            "back to the synth for any that are absent, applies the "
            "loudness spec check against those recordings (see the boot "
            "report and the developer overlay), and is where new audio "
            "files get added. Opens the mixer in stereo, which doubles "
            "what the clips cost resident - 22.8 MB against 45.6 MB, "
            "measured"
        ),
    )
    parser.add_argument(
        "--developer",
        choices=("off", "on"),
        default="off",
        help=(
            "development tools, not a way to play: draws the Alien and the cat "
            "on the map, and unlocks '--death fixed'. NOT the original, and it "
            "changes nothing the simulation does"
        ),
    )
    parser.add_argument(
        "--android",
        choices=("original", "random"),
        default="original",
        help=(
            "which crew member can be the hidden android: 'rom' (the "
            "original - $50FC holds Dallas, Kane, Ash and Parker, so the "
            "other three never are) or 'any' (an added rule, NOT the original: "
            "draw from the whole crew). Either way the android is never the "
            "crew member found dead at the opening, which is the ROM's own "
            "rule"
        ),
    )
    parser.add_argument(
        "--turns",
        choices=("off", "on"),
        default="off",
        help=(
            "pace the game by order instead of by clock: 'off' (default, "
            "real time) or 'on' (nothing advances until you give an order, "
            "which then runs to whatever it costs in one step - see "
            "--headless-turns for the same mode without a window). Ticks and "
            "per-action costs are unchanged either way. NOT the original"
        ),
    )
    parser.add_argument(
        "--screen-fx",
        dest="screen_fx",
        choices=("off", "on"),
        default="off",
        help=(
            "on the boot report screen only: a CRT power-on stretch with a "
            "settling degauss shake, text typed out in phosphor yellow "
            "behind a blinking cursor and a trailing streak, static that "
            "throws in letters as well as blocks, and a command-style "
            "prompt once revealed. 'off' (default) or 'on'. Purely "
            "cosmetic - no screen's content changes either way. NOT the "
            "original"
        ),
    )
    parser.add_argument(
        "--jones",
        choices=("patient", "classic", "easy"),
        default="patient",
        help=(
            "what a missed grab at the cat does: 'patient' (default - he stays "
            "put, so you can try again), 'classic' (the ROM - $878C spooks him "
            "on the next pass whether you catch him or not), or 'easy' (a house "
            "rule, NOT the original: the cat box gets the same +4 the ROM gives "
            "the net, so Ripley catches at 44%% instead of 19%%). The ROM's "
            "per-character table applies throughout - Ripley, Ash and Lambert "
            "are the best at this and Parker the worst"
        ),
    )
    parser.add_argument(
        "--front-end",
        choices=("quick", "classic"),
        default="quick",
        help=(
            "how much of the loader's boot chain to play: 'quick' (default - "
            "title, back-up notice, then the Ctrl+1/Ctrl+2 selection) or "
            "'classic' (the original's full chain, including the LOADING / "
            "PLUG JOYSTICK cards, the WELCOME menu and the Q QUIT advert)"
        ),
    )
    parser.add_argument(
        "--alien-start",
        choices=("original", "random"),
        default="original",
        help=(
            # ASCII only: argparse prints this to a console that is cp1252
            # by default on Windows (DISC-241).
            "where the Alien begins: 'airlock' (the ROM - $7935 slot 0 is "
            "AIRLOCK 1, upper deck, every game) or 'random' (an added rule, NOT "
            "the original: any mapped room except the Narcissus and the crew's "
            "own starting rooms). Movement is unchanged either way"
        ),
    )
    parser.add_argument(
        "--crt",
        choices=("off", "subtle", "full"),
        default="off",
        help=(
            # ASCII only: argparse prints this to a cp1252 console (DISC-241).
            "analog CRT presentation, on every screen from boot: 'off' "
            "(default, pixel exact), 'subtle' or 'full'. Both run the same "
            "effects - scanlines, NTSC chroma bleed, RF noise, glow and a "
            "scrambled-channel glitch when the view changes - with 'subtle' "
            "at about two thirds the strength of 'full'. NOT the original: it "
            "is a look, not a fact, and it never changes what the game draws"
        ),
    )
    parser.add_argument(
        "--media",
        action="store_true",
        help=(
            "list every file you can supply or replace - sounds, and the data "
            "derived from your disk - with where each one goes and whether it "
            "is there, then exit"
        ),
    )
    parser.add_argument(
        "--media-doc",
        action="store_true",
        help=(
            "print docs/MEDIA.md - the same list as --media, as a document "
            "with the file-format requirements - then exit"
        ),
    )
    parser.add_argument(
        "--replay",
        metavar="LOG",
        help=(
            "summarise a session log as a page of prose with tick numbers - "
            "what happened, what was ordered, and how to read the fields - "
            "then exit. Pass --around to slice near a moment instead"
        ),
    )
    parser.add_argument(
        "--around",
        type=int,
        metavar="TICK",
        help="with --replay: print the resolved ticks either side of this one",
    )
    parser.add_argument(
        "--span",
        type=int,
        default=40,
        metavar="N",
        help="with --around: how many ticks either side (default 40)",
    )
    parser.add_argument(
        "--timing",
        action="store_true",
        help=(
            "list every duration in the game with what its number means - a "
            "counter reload, or a real wall-clock second - then exit"
        ),
    )
    parser.add_argument(
        "--derive-assets",
        nargs="?",
        const="",
        metavar="NIB",
        help=(
            "one-time first run: decode your own copy of the disk (.nib, "
            ".g64 or .d64) into "
            "everything the game needs (charset, sprites, loader BASIC, the "
            "SID intro), then report anything still missing. Optionally takes "
            "the path to the image; otherwise looks for one beside you"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # **Steam's Game Mode gives a program no arguments**, so anything a Deck
    # player wants has to come from a file. Values the user actually typed win;
    # the file only fills what is still at its default (see `settings.apply`).
    from . import settings as user_settings

    # **B1.** Startup diagnostics are collected, not printed: the graphical
    # path shows them on a boot screen inside the window, and the console paths
    # print the same report to stderr. See `startup.StartupReport`.
    report = StartupReport()

    stored = user_settings.load()
    parser_defaults = vars(parser.parse_args([]))
    if stored:
        used = user_settings.apply(args, parser_defaults, stored)
        if used:
            report.info(
                "settings from " + str(user_settings.path()) + ": "
                + ", ".join(used)
            )

    # **Is this the first launch?** The rule is `settings.is_first_run`, which
    # is where the two conditions and their reasons live.
    first_run = user_settings.is_first_run(args, parser_defaults)

    if args.media:
        from . import media

        print(media.describe())
        return 0

    if args.media_doc:
        from . import media

        print(media.document())
        return 0

    if args.replay:
        from . import replay as replay_module

        log = Path(args.replay)
        if not log.is_file():
            print(f"alien-remake: no such log: {log}", file=sys.stderr)
            return 2
        if args.around is not None:
            ticks = replay_module.states(log)
            for t_ in replay_module.window(ticks, around=args.around,
                                           span=args.span):
                print(f"t{t_.tick} ({t_.seconds:.1f}s) {t_.state}")
                for ev in t_.events:
                    print(f"    event {ev}")
        else:
            print(replay_module.summarise(log))
        return 0

    if args.timing:
        from .core import timing

        print(timing.describe())
        return 0

    if args.derive_assets is not None:
        return _derive_assets(args.derive_assets or None)

    mode = GameMode.SHORT if args.mode == "short" else GameMode.FULL
    death_variant = {
        "original": DeathVariant.ORIGINAL,
        "random": DeathVariant.RANDOM,
    }.get(args.death, DeathVariant.FIXED)
    android_variant = (
        AndroidVariant.RANDOM if args.android == "random"
        else AndroidVariant.ORIGINAL
    )
    alien_start = (
        AlienStart.RANDOM if args.alien_start == "random"
        else AlienStart.ORIGINAL
    )
    jones_catch = {
        "classic": JonesCatch.CLASSIC,
        "easy": JonesCatch.EASY,
    }.get(args.jones, JonesCatch.PATIENT)

    # DEC-044: keyed on the whole profile at launch, same as `make_sim`
    # reads `live.death` etc. below rather than the launch-time value — see
    # `_options_changed` for where a later change on the options screen
    # updates this same field.
    from .core import options as options_module

    # What the game is actually launching with, in the options screen's own
    # vocabulary. Built here (rather than down by `GameFlow`, where a copy of
    # this map used to live on its own) because DEC-044 needs the same
    # whole-profile question `options.pointer_allowed` already asks the
    # mouse, and a second copy of this map is how a future option could come
    # to disagree with itself about what "the current options" are.
    current_options = {
        "crt": args.crt, "front_end": args.front_end, "jones": args.jones,
        "alien_start": args.alien_start, "death": args.death,
        "android": args.android, "developer": args.developer,
        "sound": args.sound, "game_audio": args.game_audio,
        "turns": args.turns, "screen_fx": args.screen_fx,
    }

    # Mutable so the in-game options screen can change them between games; the
    # factory below reads them at call time rather than closing over the
    # start-up value, which is what makes a change on that screen take effect
    # on the very next game rather than the next launch.
    live = _LiveRules(
        alien_start=alien_start, jones=jones_catch, death=death_variant,
        android=android_variant,
        weapon_breach_gates=not options_module.is_original(current_options),
    )

    def make_sim(m: GameMode, dv: DeathVariant) -> Simulation:
        # Build the starting sim (with its awake-crew count initialised),
        # honouring an explicit --awake-crew override if given.
        # `dv` is the flow's own idea of the variant; `live.death` is what the
        # options screen last set, and it wins for the same reason the other
        # three do — it is the current choice, not the launch-time one.
        sim = default_simulation(
            m, live.death, live.alien_start, live.jones, live.android,
            live.weapon_breach_gates,
        )
        if args.awake_crew is not None:
            sim.state.awake_crew = args.awake_crew
        return sim

    if args.headless_turns is not None:
        # The turn-based loop, reachable. It shares the simulation with the
        # real-time one and differs only in when it stops to ask for input, so
        # the reported tick count is directly comparable with --headless.
        report.to_console()
        sim = make_sim(mode, death_variant)
        turn_renderer: Renderer = NullRenderer(quit_after=args.headless_turns)
        turns = run_turn_based(sim, turn_renderer, max_turns=args.headless_turns)
        s = sim.state
        print(f"turns={turns} tick={s.tick} phase={s.phase.name}")
        return 0

    if args.headless is not None:
        # A console program: there is no window to draw the report in, so it
        # prints, exactly as it always did (B1).
        report.to_console()
        # Headless keeps the old behaviour: build the sim straight from the CLI
        # flags (no title/selection screens) and run it to completion.
        sim = make_sim(mode, death_variant)
        headless: Renderer = NullRenderer(quit_after=args.headless)
        run_realtime(sim, headless, max_ticks=args.headless, sleep=lambda _: None)
        s = sim.state
        print(f"tick={s.tick} phase={s.phase.name}")
        return 0

    # Graphical mode needs the optional pygame dependency.
    try:
        from .render.pygame_app import PygameRenderer
    except ImportError:
        report.to_console()
        print(
            "alien-remake: pygame is not installed. Install the remake extra "
            "('pip install -e .[remake]') or run with --headless N.",
            file=sys.stderr,
        )
        return 2

    # **F-1: a first run with no disk image gets asked for one, instead of a
    # path and a command.** Gated on both halves - `missing_required()` (there
    # is actually a gap) and `_find_nib()` (nothing to derive from was found
    # automatically) - so a working install, or one that already has a nib
    # sitting somewhere `--derive-assets` would have found on its own, never
    # sees this at all.
    if assets.missing_required() and _find_nib() is None:
        if _first_run_asset_wizard():
            report.info("assets derived from the disk image you chose")

    # Load the game's own extracted C64 tiles if the derived asset exists
    # (produced by `python -m alientools chars`); fall back to primitives (D-009).
    from .render.tiles import TileSet, load as load_tiles

    tiles: TileSet | None = None
    # **D2.** A supplied `glyphs/charset.bin` wins over the derived one, so a
    # replacement charset does not have to overwrite what came off your disk.
    # `media` owns the location for the same reason it owns the portraits':
    # the dictionary that documents the folder is the code that reads it.
    from . import media as media_module

    default_tiles = media_module.charset_path()
    if default_tiles is not None:
        tiles = load_tiles(default_tiles)

    # Say what is missing, once. Every derived asset is optional and the game
    # runs without it, but silence is what let a wrong working directory pass
    # for a working install - and a missing BASIC ROM does not merely mute the
    # music, it makes the opening print the crew member's clean name where the
    # original prints the garbled one.
    if absent := assets.report():
        searched = ", ".join(str(root) for root in assets.asset_roots())
        # **Required and optional are different things, and saying so is the
        # whole of this (owner, 2026-08-30).** The card used to head every
        # absence with "missing derived data - decoded from your own disk",
        # which for `basic.bin` and `chargen.bin` is untrue twice over: they
        # are C64 ROM images rather than game data, and the game runs fine
        # without them. A working install was being told it was broken.
        required = assets.missing_required()
        optional = assets.missing_optional()
        if required:
            report.warn("missing derived data - decoded from your own disk:")
            for missing in absent:
                name, _, how = missing.strip().partition(chr(10))
                short = name.split(" - ")[0].strip()
                if any(short.endswith(r) for r in required):
                    # The name goes on the screen; how to produce it is long,
                    # and belongs in a terminal where it can be read and copied.
                    report.warn(f"  {short}", detail=how)
            report.info(f"set {assets.ENV_VAR} to point elsewhere",
                        detail=f"searched: {searched}")
        if optional:
            report.info(
                "optional extras absent (the game runs without them): "
                + ", ".join(optional),
                detail=assets.OPTIONAL_SOURCE,
            )

    # Graphical mode runs the full screen flow (title -> game selection ->
    # opening -> play). The player picks Full/Short on the selection screen, so
    # --mode is ignored here; --death still sets the opening-death variant.
    front_end = (
        FrontEnd.CLASSIC if args.front_end == "classic" else FrontEnd.QUICK
    )
    from .render.crt import preset as crt_preset

    # The renderer is built **before** the flow: opening the joystick is
    # one of the things that reports (B1), so asking `bool(report)` any
    # earlier would decide there was nothing to say and skip the boot
    # screen for the one message a player most often wants.
    gui = PygameRenderer(
        tiles=tiles, front_end=front_end, crt=crt_preset(args.crt),
        startup_report=report, sound=args.sound, game_audio=args.game_audio,
    )
    flow = GameFlow(
        death_variant=death_variant,
        sim_factory=make_sim,
        front_end=front_end,
        # **B5.** `bool(report)` is "is there anything to say" — a clean
        # start skips the card entirely rather than showing an empty one.
        show_boot=bool(report),
        # The first-run edition question, in front of all of it. It commits
        # through `on_options_saved` like any other option change, which is
        # what writes the file that stops it being asked twice.
        ask_edition=first_run,
        current_options=current_options,
    )
    # The developer-mode session log (`core.journal`). Created either way so
    # the options screen can switch it on mid-run; it opens no file until it is
    # enabled.
    from .core.journal import Journal

    # **B4, and it lands before B3 deliberately.** With `pythonw` there is no
    # console for a traceback to reach, so the file has to exist first — a
    # silent crash is worse than a console window. Nothing is written unless
    # something actually goes wrong.
    logs = user_settings.path().parent / "logs"
    crash_log = install_crash_log(logs)

    journal = Journal(logs)
    # **Always recording** (owner, 2026-08-29), under every preset including
    # ORIGINAL. A log is written outside the game: it reaches neither the
    # screen nor the simulation, which is the line DEC-039 draws, and the crash
    # log has always installed unconditionally on the same reasoning.
    journal.set_enabled(True)
    if args.developer == "on":
        # Reported only in developer mode, which is the "silently" half of the
        # request. `bool(report)` decides whether the boot card appears at all
        # (B5), so a line every launch would make a card that always appears —
        # the exact thing B5 exists to avoid.
        #
        # The *directory*, not the file: the log is opened by the first line
        # written, so there is no filename yet — and the folder is what a
        # player needs to find it in anyway.
        report.info(f"recording to {logs}")
    if args.sound == "all" or args.game_audio == "enhanced":
        found = gui._samples.found()
        if found:
            report.info(f"sounds: {len(found)} recording(s) loaded")
            # **Loudness spec check (2026-09-05), not the original.** The
            # ROM's own SID audio has no concept of LUFS; this only exists so
            # a dropped-in recording that is wildly louder or quieter than
            # the game's own mix is caught here, not by ear mid-game. See
            # `constants.SOUND_TARGET_LUFS`'s own comment for where the
            # number comes from.
            from .core import constants

            # Computed once, here, and handed to the debug overlay too
            # (`gui._dbg_audio_spec`) rather than let it recompute the same
            # thing lazily on first draw — K-weighting a real-world clip is
            # not cheap, and the render loop has to stay fast every frame.
            spec = gui._samples.loudness_report()
            gui._dbg_audio_spec = spec
            for entry in spec:
                if not entry.in_spec:
                    report.warn(
                        f"{entry.path.name}: {entry.lufs:.1f} LUFS, outside "
                        f"the {constants.SOUND_TARGET_LUFS:.0f}"
                        f"±{constants.SOUND_LUFS_TOLERANCE:.0f} LUFS "
                        f"range this game's own effects sit in",
                        detail=f"cue {entry.cue!r} - remix or replace the "
                               f"file if it sounds out of place",
                    )
        else:
            report.warn("sampled audio is on but no 'sounds' folder was found",
                        detail="put .wav files named after each effect in a "
                               "'sounds' folder beside the other derived data")
    gui.on_menu_action = journal.note
    gui.set_developer(args.developer == "on")
    gui.set_pointer_enabled(options_module.pointer_allowed(current_options))

    def _options_changed(values: dict[str, str]) -> None:
        """Apply the options screen's choices, then write them to disk.

        Applied live where a value has somewhere live to go: the CRT is a
        renderer object that can simply be swapped, and the front end decides
        what the selection screen prints and whether it wants the Ctrl chord.
        The two simulation flags go through `live`, so they are picked up by
        the next game started — which is the next thing the player does.

        Saving is best-effort by design (`settings.save` never raises): a
        read-only disk should cost you the persistence, not the pass.
        """
        live.alien_start = (
            AlienStart.RANDOM if values.get("alien_start") == "random"
            else AlienStart.ORIGINAL
        )
        live.jones = {
            "classic": JonesCatch.CLASSIC,
            "easy": JonesCatch.EASY,
        }.get(values.get("jones", ""), JonesCatch.PATIENT)
        live.death = {
            "random": DeathVariant.RANDOM,
            "fixed": DeathVariant.FIXED,
        }.get(values.get("death", ""), DeathVariant.ORIGINAL)
        live.android = (
            AndroidVariant.RANDOM if values.get("android") == "random"
            else AndroidVariant.ORIGINAL
        )
        live.weapon_breach_gates = not options_module.is_original(values)
        chosen_front = (
            FrontEnd.CLASSIC if values.get("front_end") == "classic"
            else FrontEnd.QUICK
        )
        flow.set_front_end(chosen_front)
        gui.set_front_end(chosen_front)
        gui.set_crt(crt_preset(values.get("crt", "off")))
        developer_on = values.get("developer") == "on"
        gui.set_audio(values.get("sound", "game"),
                      values.get("game_audio", "original"))
        gui.set_developer(developer_on)
        # **The mouse is off under ORIGINAL** (owner, 2026-08-29). Applied
        # through the same callback as everything else, so choosing the
        # original edition at first run takes the pointer away immediately
        # rather than at the next launch.
        gui.set_pointer_enabled(options_module.pointer_allowed(values))
        # The journal is **not** touched here any more: it records whatever
        # the preset is, so switching developer mode off mid-run must not throw
        # away the recording of the very session being investigated.
        if developer_on:
            print(f"alien-remake: recording to {logs}", file=sys.stderr)
        user_settings.save(values)

    flow.on_options_saved = _options_changed
    try:
        run_app(flow, gui, journal=journal)
    finally:
        journal.close()
        gui.close()
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
