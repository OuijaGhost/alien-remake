"""Player orders (corrected to the FULL disassembly).

An :class:`Order` is a structured instruction aimed at one crew member. Orders
are queued asynchronously and consumed on tick boundaries by
:class:`~alien_remake.core.sim.Simulation`.

**1:1 fidelity note — the "PCS obedience gate" was an invention and is gone.**
The manual reads as if crew may refuse orders, but the decoded program has no
compliance roll anywhere on the order path: issuing a MOVE order writes the
destination and the crew member walks there after their action-timer delay
(D-018 — Dallas obeyed at fear 4). What fear *actually* does in the code is
raise the tempo (`fear_alert $4E16`) and enable a panic branch (`$52C0` →
`char_wander $5203`) — traced statically (D-026): panicking crew take
an Alien-style random walk over the Alien's own route tables, triggered by
sharing a room with the Alien, low health, or (narrower than first thought)
being co-located with another disturbed crew member once the Alien has taken
damage >=6. See `constants.py`'s fear-band comment for the full trace. Not
yet implemented in the remake (crew simply keep obeying queued orders) — a
real, filed gap, not an invention.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class OrderType(Enum):
    """The order verbs."""

    # [C $A86E] the decoded order menu is MOVE TO / GET ITEM / LEAVE ITEM / USE /
    # ATTACK / SPECIAL / QUIT (GAMEDATA §1.7). These five map to it directly:
    GET_ITEM = auto()      # pick up a named item in the crew's current room
    LEAVE_ITEM = auto()    # drop / hand off the carried item
    ATTACK = auto()        # attack the Alien directly (bare hands / a weapon)
    USE = auto()           # use the held item — effect depends on the item
    MOVE_TO = auto()       # travel toward a target room
    # [C $86F0] FV-1.4 confirmed REAL (initially suspected invented, then traced):
    # `draw_grille_option ($86F0)` checks the grille table `$8676,Y` for the
    # current room and, when it has a grille, draws the option whose label
    # `$86E6` decodes to **"REMVGRILLE"** — exactly the remake's "REMV GRILLE"
    # (vs the status string `$86C8` = "GRILLE IN PLACE"). So a contextual
    # grille-remove action exists, matching menu.py's grille-gated SPECIAL entry.
    #: **[C $829A/$829B] Bring the spare item to hand (DISC-261).** Not a verb
    #: on the ROM's order menu: the original has two carry slots and `$829A` is
    #: the active one, so choosing the second row promotes it. Modelled as an
    #: order so it goes through the same pipeline as everything else.
    SELECT_ITEM = auto()
    REMOVE_GRILL = auto()  # [C $86F0] open the grille in the crew's current room
    # **[C $86F0/$046E] P2-2.** Once a grille is REMOVED, `draw_grille_option`
    # stops drawing "REMVGRILLE" in the SPECIAL column ($064E, row 14) and
    # instead writes **"GRILLE"** into the **MOVE TO** column ($046E, row 2) —
    # i.e. the opened grille becomes a *destination you choose*, not something
    # that happens to you. Crossing it toggles the character between the
    # surface and the ducting for that same room. The remake used to slip a
    # crew member into the ducts as a side effect of an ordinary MOVE TO,
    # which is the bug the player reported.
    USE_GRILLE = auto()
    # **[C $8437 -> $8784] P8-3/D-160 — "GET JONES", a real panel row.**
    # `route_command` dispatches panel cursor row 15 (`$64E5` = $0F, below the
    # `#$10` Special-Options band and not the `#$0E` case) straight into
    # `$8784`, whose first act is `LDA $0676 / CMP #$A0 / BEQ rts` — it does
    # nothing unless `guard_6580` has actually written the option into the
    # slot. So the catch is its own order, offered contextually, NOT a side
    # effect of USE-ing a net or a cat box (D-153 wired it that way; the ROM's
    # USE path for both items is `resolve_attack $4940`).
    GET_JONES = auto()


@dataclass(frozen=True)
class Order:
    """One instruction to one crew member.

    ``target`` meaning depends on ``type``: a room id for ``MOVE_TO``, an item id
    for ``GET_ITEM`` (``LEAVE_ITEM``/``REMOVE_GRILL``/``ATTACK``/``USE`` need none).
    """

    crew_id: str
    type: OrderType
    target: str | None = None


class OrderOutcome(Enum):
    """What actually happened to an order on a tick (for tests + the monitor UI)."""

    COMPLETED = auto()   # finished (grille opened, item taken, arrived)
    IN_TRANSIT = auto()  # a MOVE step underway, not yet at the destination — retries
    INVALID = auto()     # malformed (unknown/dead crew, missing target) — dropped
    BLOCKED = auto()     # couldn't act (no path, no grille, item exhausted) — dropped


# Outcomes that keep the order in the queue for another tick.
SURVIVING_OUTCOMES: frozenset[OrderOutcome] = frozenset({OrderOutcome.IN_TRANSIT})
