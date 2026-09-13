"""The state `Simulation` shares with its mixins (DISC-196).

`Simulation` was split into `sim/orders.py` and `sim/specials.py`. The pieces
are mixins rather than free functions because they all mutate the same world:
`self.state`, the ship, the RNG, and the per-crew turn timers.

Under mypy's `strict = true` a mixin that reads `self.state` cannot type-check
alone, so the shared surface is declared here once and inherited by both mixins
and by `Simulation`. A typo becomes an error instead of an `AttributeError` on
some tick that only happens ten minutes into a game.

**Annotations only.** `Simulation.__init__` stays the single place any of this is
actually initialised.
"""

from __future__ import annotations

import random
from collections import deque

from ..crew import CrewMember
from ..map import ShipMap
from ..orders import Order, OrderOutcome
from ..modes import JonesCatch
from ..state import GameState


class SimulationState:
    """Shared simulation state, declared for the mixins' benefit."""

    #: The whole mutable world for this tick.
    state: GameState
    #: Room topology and connections; the sim never mutates it.
    ship: ShipMap
    #: The one seeded RNG — everything random draws from here, so a game
    #: replays exactly from its seed.
    rng: random.Random
    #: Pending orders, oldest first. An order is a *standing intention*: a new
    #: one for the same crew member replaces theirs rather than stacking.
    _orders: deque[Order]
    #: Ids whose `$64EE,Y` expired this pass, recomputed by `_pump_characters`
    #: at the top of every `advance` (D-168).
    _due: set[str]
    #: Crew whose death has already applied the ship-wide composure hit, so
    #: `$47DC`/`$5A0D` fire once per death rather than once per tick (D-059).
    _mourned_dead: set[str]
    _jones_timer: int
    #: Added rule for a missed grab (DISC-262).
    jones_catch: "JonesCatch"
    #: DEC-044 — the ROM's pre-add weapon breach gates. False under ORIGINAL.
    weapon_breach_gates: bool
    _jones_next: str | None
    #: What happened to each order processed this tick; reset every `advance`.
    last_outcomes: list[tuple[Order, OrderOutcome]]

    # --- methods the mixins call but do not own ---------------------------
    def effective_composure(self, crew: CrewMember) -> int:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _hull_breach(self) -> None:
        """`hull_breach ($5D17)` — reached from four sites, owned by `Simulation`."""
        raise NotImplementedError

    def _slot_of(self, crew: CrewMember) -> int:
        raise NotImplementedError

    def _room_occupants(self, room_id: str, *, exclude: str | None = None) -> int:
        raise NotImplementedError

    def _android_ignores_order(self, crew: CrewMember) -> bool:
        raise NotImplementedError

    def _catch_jones(self, crew_id: str | None) -> bool:
        raise NotImplementedError

    def _post_notice(self, text: str) -> None:
        """The transient row-24 banner (`SpecialsMixin`, DISC-231) - declared
        here so `OrderMixin` can raise it too (combat's own banners)."""
        raise NotImplementedError
