"""What the game has to say before it starts, and where it says it.

Two jobs that look separate and are not.

**The report (B1).** Startup diagnostics — which settings file was read and
what it took, which derived assets are missing and where it looked, whether a
joystick was found — used to be a dozen `print(..., file=sys.stderr)` calls.
On Windows that means a console window behind the game, because `play.bat` runs
`python.exe`, which is a console application. Collecting the lines instead of
printing them lets the *game* decide where they go: a boot screen in the
window, or stderr when there is no window to draw in.

**The crash log (B4).** The console is also where an unhandled exception went.
Take the console away and it goes nowhere — so a file has to exist first. B4
lands before B3 for that reason and no other: `pythonw.exe` discards stdout and
stderr entirely, and a silent crash is worse than a console window.

The report is deliberately **not** a logging framework. It is a list of short
strings with a severity, because that is all a boot screen can show and all a
player can act on.
"""

from __future__ import annotations

import sys
import textwrap
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType

#: Width the boot screen wraps to. The field is 40 columns and the screen
#: leaves one clear each side, so a line longer than this would be truncated
#: rather than wrapped — the same trap the options help box has.
SCREEN_WIDTH = 38


@dataclass(frozen=True)
class Note:
    """One line of the report.

    ``detail`` is the part a *terminal* gets and the screen does not: how to
    produce a missing file, which directories were searched. It is real help
    and too long to be scanned off a 40-column card, and a boot screen that
    silently drops its last five lines is the failure DISC-286 already cost
    this project once.
    """

    text: str
    warning: bool = False
    detail: str = ""


@dataclass
class StartupReport:
    """What happened while the game was starting, in the order it happened."""

    notes: list[Note] = field(default_factory=list)

    def info(self, text: str, detail: str = "") -> None:
        self.notes.append(Note(text, detail=detail))

    def warn(self, text: str, detail: str = "") -> None:
        self.notes.append(Note(text, warning=True, detail=detail))

    def __bool__(self) -> bool:
        """**B5.** Whether there is anything worth showing.

        A clean start — every asset present, no settings file, a joystick or a
        deliberate keyboard — has nothing to report, and a boot screen that
        always appears is one that gets skipped without being read.
        """
        return bool(self.notes)

    def to_console(self, stream: object = None) -> None:
        """Print the report, for when there is no window to draw it in.

        `--headless`, `--help` and a failed pygame import are all console
        programs; taking their output away would be a regression, not a fix.
        """
        out = stream if stream is not None else sys.stderr
        for note in self.notes:
            print(note.text, file=out)  # type: ignore[arg-type]
            if note.detail:
                for line in note.detail.splitlines():
                    print(f"  {line.strip()}", file=out)  # type: ignore[arg-type]

    def screen_lines(self) -> list[str]:
        """The report wrapped to the boot screen's width.

        Wrapped rather than truncated: these lines carry paths, and half a path
        is worse than no path — it reads as if the file were somewhere it is
        not.
        """
        out: list[str] = []
        for note in self.notes:
            # A note may already carry its own line breaks; wrap each part
            # rather than running them together.
            for part in note.text.splitlines() or [""]:
                out.extend(
                    textwrap.wrap(
                        part.strip(), SCREEN_WIDTH, subsequent_indent="  "
                    ) or [""]
                )
        return out


def install_crash_log(directory: Path) -> Path:
    """Send unhandled exceptions to a file as well as to stderr. **B4.**

    Returns the path it will write to. Nothing is created until something
    actually crashes, so a clean run leaves no litter.

    `sys.excepthook` rather than a `try/except` around the loop: the point is
    to catch what was *not* anticipated, including failures raised before the
    window exists, and a wrapper only sees what it wraps. The previous hook is
    still called, so a terminal user keeps their traceback.
    """
    path = directory / "crash.log"
    previous = sys.excepthook

    def hook(
        kind: type[BaseException],
        value: BaseException,
        tb: TracebackType | None,
    ) -> None:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                traceback.print_exception(kind, value, tb, file=handle)
        except OSError:
            # Failing to record a crash must not replace it with a different
            # one; the traceback still reaches the previous hook below.
            pass
        previous(kind, value, tb)

    sys.excepthook = hook
    return path
