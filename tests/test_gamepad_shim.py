"""Pad bindings for the two inputs a gamepad cannot otherwise reach (DISC-248).

Escape and the selection screen's Ctrl+1/Ctrl+2 chord have no pad equivalent,
so a controller cannot start a game at all. These are bound to **dedicated**
buttons, never to fire — FV-1c1/1c2 removed an invented up/down cursor and
fire-select from that screen, and making fire pick the full game would put the
invention straight back.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.core.flow import InputEvent, Screen
from alien_remake.render.pygame_app import (
    _JOY_BTN_QUIT, _JOY_BTN_SELECT_FULL, _JOY_BTN_SELECT_SHORT, PygameRenderer,
)
from alien_remake.render.tiles import load


class FakePad:
    """Minimal stand-in for `pygame.joystick.Joystick`."""

    def __init__(self) -> None:
        self.buttons = [False] * 8

    def get_numbuttons(self) -> int:
        return len(self.buttons)

    def get_button(self, i: int) -> bool:
        return self.buttons[i]

    def get_numhats(self) -> int:
        return 1

    def get_hat(self, i: int) -> tuple[int, int]:
        return (0, 0)

    def get_numaxes(self) -> int:
        return 2

    def get_axis(self, i: int) -> float:
        return 0.0


@pytest.fixture
def pad_renderer() -> tuple[PygameRenderer, FakePad]:
    charset = Path("out") / "charset.bin"
    tiles = load(charset) if charset.exists() else None
    r = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    pad = FakePad()
    r._joystick = pad  # type: ignore[assignment]
    yield r, pad
    r.close()


def _press(r: PygameRenderer, pad: FakePad, button: int, screen: Screen) -> list:
    """One complete press-and-release, as a real pair of frames would see it."""
    r._pending_input = []
    pad.buttons[button] = True
    r._poll_joystick(screen)
    events = list(r._pending_input)
    # Poll again with it released, so the edge detector sees the release. A
    # real frame always polls; skipping it here left the button "still held"
    # and swallowed the next press.
    pad.buttons[button] = False
    r._pending_input = []
    r._poll_joystick(screen)
    return events


def test_dedicated_buttons_produce_the_selection_chords(
    pad_renderer: tuple[PygameRenderer, FakePad],
) -> None:
    r, pad = pad_renderer
    assert _press(r, pad, _JOY_BTN_SELECT_FULL, Screen.GAME_SELECTION) == [
        InputEvent.SELECT_FULL
    ]
    assert _press(r, pad, _JOY_BTN_SELECT_SHORT, Screen.GAME_SELECTION) == [
        InputEvent.SELECT_SHORT
    ]


def test_fire_does_not_select_a_game(
    pad_renderer: tuple[PygameRenderer, FakePad],
) -> None:
    """The load-bearing one: this is the invention FV-1c2 removed.

    `$5F36` polls for the chord of the option you want — there is no cursor and
    no fire-select. A button that is *not* one of the two chord buttons must
    produce nothing at all on this screen.
    """
    r, pad = pad_renderer
    neutral = next(
        b for b in range(pad.get_numbuttons())
        if b not in (_JOY_BTN_SELECT_FULL, _JOY_BTN_SELECT_SHORT, _JOY_BTN_QUIT)
    )
    assert _press(r, pad, neutral, Screen.GAME_SELECTION) == [], (
        "fire selected a game — the removed invention is back"
    )


def test_the_back_button_backs_out_and_only_quits_from_the_top_menu(
    pad_renderer: tuple[PygameRenderer, FakePad],
) -> None:
    """**DISC-261** — same rule as Escape, because it is the same intent.

    This used to assert "quits from any screen". Ending the process on a
    mis-hit mid-game is harsher than anything the original does, where the only
    exit is `Q QUIT` on WELCOME.
    """
    r, pad = pad_renderer
    for screen in (Screen.GAME_SELECTION, Screen.PLAYING, Screen.INSTRUCTIONS):
        r._quit = False
        events = _press(r, pad, _JOY_BTN_QUIT, screen)
        assert InputEvent.ABANDON in events, f"{screen.name}: no back-out"
        assert InputEvent.QUIT not in events
        assert r._quit is False, f"{screen.name}: closed the program"

    r._quit = False
    events = _press(r, pad, _JOY_BTN_QUIT, Screen.WELCOME)
    assert InputEvent.QUIT in events
    assert r._quit is True


def test_fire_still_works_everywhere_else(
    pad_renderer: tuple[PygameRenderer, FakePad],
) -> None:
    """The shim must not cost the pad its ordinary button."""
    r, pad = pad_renderer
    assert _press(r, pad, _JOY_BTN_SELECT_FULL, Screen.WELCOME) == [
        InputEvent.FIRE
    ]


def test_a_held_button_fires_once(
    pad_renderer: tuple[PygameRenderer, FakePad],
) -> None:
    """Press-edge only, for the chord buttons as well as fire."""
    r, pad = pad_renderer
    pad.buttons[_JOY_BTN_SELECT_FULL] = True
    r._pending_input = []
    r._poll_joystick(Screen.GAME_SELECTION)
    first = list(r._pending_input)
    r._pending_input = []
    r._poll_joystick(Screen.GAME_SELECTION)      # still held
    second = list(r._pending_input)
    assert first == [InputEvent.SELECT_FULL]
    assert second == [], "a held button repeated the selection"
