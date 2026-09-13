"""Developer-mode controls for playtesting. **None of this is the original.**

The owner is verifying the remake against the real disk, and several of the
things that most need checking are hard to reach by playing: what the morale
words look like across the whole fear range, what the CONTROL panel offers when
the Alien is not in the way, what the duct view does, what the android does once
it turns.

Waiting for a seeded run to produce each of those is not testing, it is
fishing. So these put the state where you need it.

The rules this module lives by
------------------------------
* **Nothing here runs unless developer mode is on.** The flags default to off
  and `Simulation.advance` consults them at exactly two points; with them off
  the decoded path is byte-for-byte what it was.
* **Nothing here ends the game.** "Turn the Alien off" is the request, and the
  obvious implementation — removing it, or killing it — is the wrong one: both
  are win conditions the ROM checks for, so the screen would go to a result and
  the thing you were trying to test would be over. The Alien is instead left in
  place and **not given its turn**, which is inert without being absent.
* **Everything is a state change, recorded.** Each helper returns what it did so
  the caller can note it in the session log, because a run where the tester
  reached in and moved something is a run whose log must say so — otherwise it
  is evidence of a game that does not exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import constants
from .state import GameState


class Freeze(Enum):
    """What a dev freeze does to a mover."""

    #: Behaving as the game says.
    OFF = "off"
    #: Left where it is and never given its turn. Still on the map, still
    #: collidable, simply not acting — which is what "off" has to mean for
    #: anything the win conditions look at.
    STILL = "still"


@dataclass
class DevControls:
    """The dev switches for one run. All off is the shipping game."""

    #: The Alien keeps its position and its presence but takes no turn.
    alien: Freeze = Freeze.OFF
    #: Jones likewise — he stays where he is instead of wandering.
    jones: Freeze = Freeze.OFF

    @property
    def any_on(self) -> bool:
        """Is anything interfering? For the log, and for the overlay to say so."""
        return self.alien is not Freeze.OFF or self.jones is not Freeze.OFF

    # --- the two the simulation asks about ---------------------------------

    def alien_may_act(self) -> bool:
        return self.alien is Freeze.OFF

    def jones_may_act(self) -> bool:
        return self.jones is Freeze.OFF

    # --- one-shot state changes --------------------------------------------

    def cycle_alien(self) -> str:
        self.alien = Freeze.STILL if self.alien is Freeze.OFF else Freeze.OFF
        return f"alien={self.alien.value}"

    def cycle_jones(self) -> str:
        self.jones = Freeze.STILL if self.jones is Freeze.OFF else Freeze.OFF
        return f"jones={self.jones.value}"


def adjust_fear(state: GameState, crew_id: str | None, delta: int) -> str | None:
    """Move one crew member's fear, clamped. Returns what changed.

    **Fear counts up**, which is the thing to keep hold of: the ROM stores fear
    and the morale word is derived from it, so raising this makes somebody
    *less* composed. `MORALE_BANDS` slices it five ways and that slicing is one
    of the open `[?]`s — walking a crew member through the whole range and
    reading the words off the panel is how it gets settled.
    """
    crew = state.crew.get(crew_id or "")
    if crew is None:
        return None
    before = crew.fear
    crew.fear = max(constants.FEAR_MIN, min(constants.FEAR_MAX, crew.fear + delta))
    if crew.fear == before:
        return None
    return f"{crew.id} fear {before} -> {crew.fear}"


def reveal_android(state: GameState) -> str | None:
    """Turn the android on now, rather than waiting for it to be found out.

    `android_revealed` is the ROM's own gate (`$5265`/`$526F`): unrevealed, the
    android takes the ordinary character road and obeys orders; revealed, it
    takes the road that ends in the attack at `$5345`. So setting the flag is
    exactly what the game does when it discovers itself — this brings the moment
    forward, it does not invent a behaviour.

    Returns ``None`` when there is no android or it is already out, so a second
    press is not reported as an event that did not happen.
    """
    if state.android_id is None or state.android_revealed:
        return None
    state.android_revealed = True
    return f"android revealed: {state.android_id}"
