"""The renderer interface + a headless null renderer (stdlib only).

The core/runner never import a concrete backend; they depend on the
:class:`Renderer` protocol, so the pygame shell and :class:`NullRenderer` are
interchangeable (logic separated from rendering). No pygame import
here, so this module is always available.
"""

from __future__ import annotations

from typing import Protocol

from ..core.orders import Order
from ..core.special_options import SpecialOption
from ..core.state import GameState


class Renderer(Protocol):
    """What the real-time loop needs from any rendering/input backend."""

    def poll_orders(self) -> list[Order]:
        """Return player orders entered since the last call (possibly empty)."""
        ...

    def poll_special_options(self) -> list[SpecialOption]:
        """Return Special Options invoked since the last call (GAME_SPEC
        §6.2 #3) — ship-wide actions, not per-crew PCS orders."""
        ...

    def render(self, state: GameState) -> None:
        """Draw one frame for the given state."""
        ...

    def should_quit(self) -> bool:
        """True once the user has asked to quit."""
        ...

    def close(self) -> None:
        """Release any backend resources."""
        ...


class NullRenderer:
    """A do-nothing renderer for headless runs and tests.

    Quits after ``quit_after`` input polls (``None`` = never), so a headless
    real-time loop terminates deterministically without a window or wall-clock.
    """

    def __init__(self, quit_after: int | None = None) -> None:
        self._quit_after = quit_after
        self._polls = 0

    def poll_orders(self) -> list[Order]:
        self._polls += 1
        return []

    def poll_special_options(self) -> list[SpecialOption]:
        return []

    def render(self, state: GameState) -> None:
        return None

    def should_quit(self) -> bool:
        return self._quit_after is not None and self._polls >= self._quit_after

    def close(self) -> None:
        return None
