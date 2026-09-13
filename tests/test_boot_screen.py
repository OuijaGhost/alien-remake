"""The boot report, the boot screen, and the crash log (B1-B5).

The console window behind the game is gone; everything it used to say has to
still reach somebody. These pin where each kind of message ends up, and that
nothing is silently dropped on the way — a boot screen that cuts its last five
lines is the same failure DISC-286 already cost this project once.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.render.layout import _ROWS  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402
from alien_remake.startup import (  # noqa: E402
    StartupReport, install_crash_log,
)

#: Rows `_draw_boot` has for report lines: it starts at 5 and stops before
#: `_ROWS - 3`, leaving the title, the rule and the footer clear.
BOOT_ROWS = (_ROWS - 3) - 5


# --- B1: the report ----------------------------------------------------------

def test_an_empty_report_is_falsey_and_a_filled_one_is_not() -> None:
    """B5 hangs off this: it is how the game decides to show the card at all."""
    report = StartupReport()
    assert not report
    report.info("something happened")
    assert report


def test_the_console_gets_the_detail_and_the_screen_does_not(capsys) -> None:
    """Detail is real help that is too long for a 40-column card.

    It must not vanish, though: a terminal user is exactly who can act on
    "capture $A000-$BFFF", so the console keeps it and the screen keeps the
    name.
    """
    report = StartupReport()
    report.warn("basic.bin", detail="make it with: capture $A000-$BFFF")
    report.to_console(sys.stdout)

    printed = capsys.readouterr().out
    assert "basic.bin" in printed
    assert "capture $A000-$BFFF" in printed, "the console lost the detail"
    assert not any("capture" in line for line in report.screen_lines()), (
        "the detail reached the screen, where it does not fit"
    )


def test_a_long_line_is_wrapped_rather_than_truncated() -> None:
    """These lines carry paths, and half a path reads as a different path."""
    report = StartupReport()
    report.info("settings from " + "C:/a/very/long/directory/name" * 3)
    lines = report.screen_lines()
    assert len(lines) > 1, "a long line was not wrapped"
    assert all(len(line) <= 38 for line in lines)
    assert "".join(line.strip() for line in lines).endswith("name")


def test_notes_that_carry_their_own_line_breaks_are_split() -> None:
    report = StartupReport()
    report.info("first line\nsecond line")
    assert report.screen_lines() == ["first line", "second line"]


# --- B2/B5: the screen -------------------------------------------------------

def _renderer(report: StartupReport) -> PygameRenderer:
    return PygameRenderer(scale=3, intro_wav=None, startup_report=report)


def test_a_clean_start_never_shows_the_card() -> None:
    """B5: a card that always appears is one nobody reads."""
    assert GameFlow(show_boot=False).screen is Screen.LOADING_MENU
    assert GameFlow(show_boot=True).screen is Screen.BOOT


def test_any_key_leaves_the_boot_screen() -> None:
    flow = GameFlow(show_boot=True)
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.LOADING_MENU


def test_the_boot_screen_advances_on_its_own_too() -> None:
    """It is meant to be readable, not to be a gate — a report nobody
    dismisses must not strand the game."""
    from alien_remake.core import constants

    flow = GameFlow(show_boot=True)
    for _ in range(constants.BOOT_TICKS + 1):
        flow.tick()
    assert flow.screen is Screen.LOADING_MENU


def test_a_click_anywhere_leaves_the_boot_screen() -> None:
    """The whole card is the target: it has one action, so hunting for a small
    hit box would be the opposite of the point."""
    report = StartupReport()
    report.info("something to say")
    renderer = _renderer(report)
    flow = GameFlow(show_boot=True)
    try:
        renderer.draw(flow)
        rect = renderer.field_rect()
        renderer._pending_input = []
        renderer._pointer_down((rect.centerx, rect.centery), flow.screen)
        for event in renderer._pending_input:
            flow.handle(event)
        assert flow.screen is Screen.LOADING_MENU
    finally:
        renderer.close()


def test_the_real_report_fits_on_the_card() -> None:
    """The regression guard.

    The first version put the full asset help on screen: 22 wrapped lines into
    17 rows, so five would have been cut with nothing saying so. This asserts
    the report a real missing-assets start produces still fits.
    """
    report = StartupReport()
    report.info("settings from C:/Users/someone/AppData/Local/alien-remake/"
                "settings.toml: crt=full, front_end=quick, jones=patient, "
                "alien_start=random, death=random, android=random")
    report.warn("missing derived data - decoded from your own disk:")
    for name in ("basic.bin", "chargen.bin"):
        report.warn(f"  {name}", detail="make it with: capture something")
    report.info("set ALIEN_REMAKE_ASSETS to point elsewhere",
                detail="searched: a, b")
    report.info("no joystick; using the keyboard (arrows/WS move, Space or "
                "Return fires)")

    assert len(report.screen_lines()) <= BOOT_ROWS, (
        "the boot report would be cut off on screen"
    )


def test_the_joystick_message_reaches_the_report_not_the_console() -> None:
    """It is reported during construction, which is why the report is a
    constructor argument rather than something set afterwards."""
    report = StartupReport()
    renderer = _renderer(report)
    try:
        assert any("joystick" in note.text for note in report.notes)
    finally:
        renderer.close()


def test_a_renderer_with_no_report_still_says_it_somewhere(capsys) -> None:
    """A test or a caller that never set a report must not lose the message."""
    renderer = PygameRenderer(scale=2, intro_wav=None)
    try:
        assert "joystick" in capsys.readouterr().err
    finally:
        renderer.close()


# --- B4: the crash log -------------------------------------------------------

def test_the_crash_log_records_an_unhandled_exception(tmp_path) -> None:
    """What the console used to catch. B3 must not land without this."""
    previous = sys.excepthook
    try:
        # Chain into a no-op: the installed hook calls whatever was there
        # before, and under pytest that is the plugin's own handler, which
        # would report this deliberate exception as a test error.
        sys.excepthook = lambda k, v, tb: None
        path = install_crash_log(tmp_path / "logs")
        assert not path.exists(), "a clean run must leave no file"

        try:
            raise ValueError("a distinctive failure")
        except ValueError as exc:
            sys.excepthook(type(exc), exc, exc.__traceback__)

        assert path.exists()
        written = path.read_text(encoding="utf-8")
        assert "a distinctive failure" in written
        assert "ValueError" in written
    finally:
        sys.excepthook = previous


def test_the_crash_log_still_calls_the_previous_hook(tmp_path) -> None:
    """A terminal user keeps their traceback; the file is an addition."""
    previous = sys.excepthook
    seen: list[BaseException] = []
    try:
        sys.excepthook = lambda k, v, tb: seen.append(v)
        install_crash_log(tmp_path / "logs")
        exc = RuntimeError("passed along")
        sys.excepthook(type(exc), exc, None)
        assert seen and str(seen[0]) == "passed along"
    finally:
        sys.excepthook = previous


def test_a_log_it_cannot_write_does_not_replace_the_crash(tmp_path) -> None:
    """Failing to record a failure must not raise a different one."""
    blocker = tmp_path / "blocked"
    blocker.write_text("not a directory", encoding="utf-8")
    previous = sys.excepthook
    reached: list[BaseException] = []
    try:
        sys.excepthook = lambda k, v, tb: reached.append(v)
        install_crash_log(blocker / "logs")
        exc = RuntimeError("the original problem")
        sys.excepthook(type(exc), exc, None)          # must not raise
        assert reached and str(reached[0]) == "the original problem"
    finally:
        sys.excepthook = previous
