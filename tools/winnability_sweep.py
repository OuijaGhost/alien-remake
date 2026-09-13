"""The winnability sweep. **Run this before and after any combat change.**

DISC-204 established the rule this exists to enforce: a game that cannot be won
must never ship, and the suite cannot tell you that on its own because a unit
test proves a win *check* fires, not that a win is *reachable*.

So this plays real games. It drives the same scripted-hunter policy
`test_a_scripted_hunter_can_kill_the_alien` uses - arm the crew, walk them to
the Alien, swing - over N seeds, and reports won / lost / still-running.

It also answers DISC-258's standing question by running the sweep twice: with
the pre-add weapon breach gates off (what ships) and on (what the ROM does).
The gates are patched in **here** rather than in the shipping code, so the
question can be measured without first committing the answer.

    python tools/winnability_sweep.py [seeds]

Takes a few minutes for 16 seeds; the games are real and some run to the cap.

A second mode sweeps turn-based mode's own `TURN_ACTIONS_PER_TURN` the same
way, for the same reason - a value chosen once by feel (owner's own phrasing,
"roughly one room move and one action") deserves the same evidence-based
check as the weapon gates got, not just a guess left standing forever::

    python tools/winnability_sweep.py --turns --ap 1,2,3,4 [seeds]
"""
from __future__ import annotations

import random
import sys

from alien_remake.core import constants as K
from alien_remake.core.alien import Alien, weapon_would_breach
from alien_remake.core.crew import CrewMember
from alien_remake.core.map import ShipMap
from alien_remake.core.orders import Order, OrderType
from alien_remake.core.sim import Simulation
from alien_remake.core.modes import DeathVariant, GameMode
from alien_remake.core.state import GamePhase, GameState
from alien_remake.runner import advance_until_resolution

WEAPONS = ("harpn_gun", "incineratr", "laser_pist", "elctrc_prd", "spanner")


def _room_gate_and_amount(item_type_id: str) -> tuple[int, int]:
    """(gate, per-hit amount) for whichever weapon is landing the hit."""
    if item_type_id == "harpn_gun":
        return K.ROOM_BREACH_GATE_HARPOON, K.ROOM_DAMAGE_PER_ATTACK_HARPOON
    return K.ROOM_BREACH_GATE_OTHER, K.ROOM_DAMAGE_PER_ATTACK


def _nearest_safe_room(
    state: GameState, ship: ShipMap, start: str, gate: int, amount: int,
    *, max_hops: int = 8,
) -> str | None:
    """BFS outward over doors for the nearest room a hit would not breach.

    A single door-neighbor is not always enough - a heavily-corroded cluster
    of adjacent rooms (the Alien has been lingering nearby the whole game)
    can leave every immediate neighbor as hot as the room being fled. Search
    a few hops out rather than give up after one, since `MOVE_TO` already
    walks a multi-room path in one order - there is no cost to picking a
    farther-but-actually-safe room over a nearer dead end.
    """
    seen = {start}
    frontier = [start]
    for _ in range(max_hops):
        next_frontier = []
        for room in frontier:
            for neighbor in ship.door_neighbors(room):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                if state.room_damage.get(neighbor, 0) + amount < gate:
                    return neighbor
                next_frontier.append(neighbor)
        frontier = next_frontier
        if not frontier:
            break
    return None


def _hunter_order(
    state: GameState, crew: CrewMember, alien: Alien, ship: ShipMap,
    *, weapon_breach_gates: bool = False,
) -> Order | None:
    """The hunter policy's decision for one crew member: arm, then hunt.

    Shared by the real-time sweep and the turn-based one below, so the two
    measure the *same* policy under a different pacing model rather than two
    different fighters that happen to both be called "hunter".

    **Gate-aware since DEC-044.** A naive hunter that keeps swinging in the
    same room regardless of accumulated damage found every DEC-044 seed
    breaching after exactly 5-6 hits landed in a handful of ticks - real
    damage, immediately followed by a real breach, not a bug. DISC-289
    already named the missing half of this: "the original must expect a
    fight that moves across the ship." So when the next hit would push the
    room to or past its gate, retreat toward the nearest room that would
    not breach instead of landing it - the Alien has to be fought room by
    room, the way ALIEN_DAMAGE_TO_KILL (several times more hits than one
    room safely absorbs) implies it must be.

    **Tried and reverted: harpoon-seeking across the whole ship.** A version
    of this sent every unarmed crew member toward the harpoon specifically,
    wherever it spawned, before settling for a nearer weapon. Measured
    worse, not better - a room-to-room walk costs ~64-74 ticks each, so a
    harpoon several rooms away cost far more chase time than the weapon
    already in the room paid for in extra swings, and stranded seeds that
    used to win at all "running" with zero damage dealt by the cap. Grabbing
    whatever is nearest is the better policy here, not the naive one.
    """
    holding = next(
        (i for i in state.items.values()
         if i.holder == crew.id and i.type_id in WEAPONS),
        None,
    )
    if holding is not None:
        if crew.room_id == alien.room_id and alien.room_id is not None:
            room_id = alien.room_id
            if weapon_breach_gates:
                gate, amount = _room_gate_and_amount(holding.type_id)
                current = state.room_damage.get(room_id, 0)
                if current + amount >= gate:
                    safe = _nearest_safe_room(state, ship, room_id, gate, amount)
                    if safe is not None:
                        return Order(crew.id, OrderType.MOVE_TO, safe)
                    return None  # nowhere safe within range - hold position
            return Order(crew.id, OrderType.ATTACK)
        return Order(crew.id, OrderType.MOVE_TO, alien.room_id)
    here = [i for i in state.items.values()
            if i.room_id == crew.room_id and i.type_id in WEAPONS]
    if here:
        return Order(crew.id, OrderType.GET_ITEM, here[0].id)
    return None


def play(
    seed: int, cap: int = 6000, *, weapon_breach_gates: bool = False,
) -> tuple[str, int, int]:
    """One game under the hunter policy. Returns (outcome, alien damage, ticks).

    ``weapon_breach_gates`` drives `Simulation`'s own flag directly (DEC-044)
    rather than monkeypatching `add_room_damage` the way this used to - the
    gate is real production code now, not something this tool has to
    simulate on the side.
    """
    sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.ORIGINAL,
                     rng=random.Random(seed),
                     weapon_breach_gates=weapon_breach_gates)
    state = sim.state
    ignored: dict[str, int] = {}
    ticks = 0
    for ticks in range(1, cap + 1):
        if state.phase is not GamePhase.RUNNING:
            break
        alien = state.alien
        if alien is None:
            break
        busy = {o.crew_id for o in sim._orders}
        if alien.alive and alien.room_id:
            for crew in state.crew.values():
                if crew.id in busy or not crew.alive or not crew.awake:
                    continue
                if crew.health < 2 or crew.in_duct or ignored.get(crew.id, 0) >= 5:
                    continue
                order = _hunter_order(
                    state, crew, alien, sim.ship,
                    weapon_breach_gates=weapon_breach_gates,
                )
                if order is not None:
                    sim.queue_order(order)
        sim.advance()
        for order, outcome in sim.last_outcomes:
            if outcome.name == "BLOCKED":
                ignored[order.crew_id] = ignored.get(order.crew_id, 0) + 1
            elif outcome.name == "COMPLETED":
                ignored[order.crew_id] = 0
    alien = state.alien
    dmg = alien.damage if alien else 0
    if state.phase is GamePhase.WON:
        return "won", dmg, ticks
    if state.phase is GamePhase.RUNNING:
        return "running", dmg, ticks
    return "lost", dmg, ticks


def play_turns(
    seed: int, ap_per_turn: int, cap_turns: int = 3000, *,
    weapon_breach_gates: bool = False,
) -> tuple[str, int, int]:
    """One turn-based game under the hunter policy. Returns (outcome, alien
    damage, turn count).

    Reproduces `app.py`'s own turn loop (initiative roll, one action point
    spent per order that reaches a terminal outcome, the creature slots
    running out to `TURN_CREATURE_SLOT_TICKS` with no player input) without
    going through `GameFlow` or a renderer - this only needs `Simulation`
    and `runner.advance_until_resolution`, both headless already. Takes
    `ap_per_turn` as a plain parameter rather than patching
    `constants.TURN_ACTIONS_PER_TURN`, since nothing here reads the module
    constant directly (unlike `patch_gates`, which has to intercept a call
    site inside `sim`).
    """
    sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.ORIGINAL,
                     rng=random.Random(seed),
                     weapon_breach_gates=weapon_breach_gates)
    state = sim.state
    order = list(state.crew.keys()) + [K.TURN_ALIEN_ACTOR, K.TURN_JONES_ACTOR]
    sim.rng.shuffle(order)
    index = 0
    actions_left = ap_per_turn
    ignored: dict[str, int] = {}
    turns = 0
    while turns < cap_turns and state.phase is GamePhase.RUNNING:
        actor = order[index % len(order)]
        alien = state.alien
        if actor in (K.TURN_ALIEN_ACTOR, K.TURN_JONES_ACTOR):
            advance_until_resolution(
                sim, max_ticks=K.TURN_CREATURE_SLOT_TICKS,
                max_idle_ticks=K.TURN_CREATURE_SLOT_TICKS,
            )
            index += 1
            actions_left = ap_per_turn
            turns += 1
            continue
        crew = state.crew.get(actor)
        gave_order = False
        if (crew is not None and crew.alive and crew.awake and crew.health >= 2
                and not crew.in_duct and alien is not None and alien.alive
                and ignored.get(actor, 0) < 5):
            decided = _hunter_order(
                state, crew, alien, sim.ship,
                weapon_breach_gates=weapon_breach_gates,
            )
            if decided is not None:
                sim.queue_order(decided)
                gave_order = True
        # DEC-045: a MOVE_TO issued from a room the gate has made too hot
        # to fight in right now doesn't cost the action point - mirrors
        # app.py's own exemption exactly, so this sweep measures the real
        # rule rather than a stricter one that would understate win rate.
        fleeing_the_gate = False
        if (gave_order and weapon_breach_gates and crew is not None
                and sim._orders and sim._orders[-1].type == OrderType.MOVE_TO):
            held = (state.items.get(crew.holding)
                    if crew.holding is not None else None)
            fleeing_the_gate = weapon_would_breach(
                state, crew.room_id, held.type_id if held is not None else None,
            )
        if gave_order or sim._orders:
            advance_until_resolution(sim)
            turns += 1
            for o, outcome in sim.last_outcomes:
                if outcome.name == "BLOCKED":
                    ignored[o.crew_id] = ignored.get(o.crew_id, 0) + 1
                elif outcome.name == "COMPLETED":
                    ignored[o.crew_id] = 0
            if (any(o.crew_id == actor for o, _ in sim.last_outcomes)
                    and not fleeing_the_gate):
                actions_left -= 1
                if actions_left <= 0:
                    index += 1
                    actions_left = ap_per_turn
        else:
            # Nothing to do this slot (unarmed, no weapon in the room, or
            # already given up on this actor 5 times) - skip it outright
            # rather than spin forever, same as a player pressing [K] SKIP.
            index += 1
            actions_left = ap_per_turn
            turns += 1
    alien = state.alien
    dmg = alien.damage if alien else 0
    if state.phase is GamePhase.WON:
        return "won", dmg, turns
    if state.phase is GamePhase.RUNNING:
        return "running", dmg, turns
    return "lost", dmg, turns


def sweep_turns(
    ap_per_turn: int, seeds: range, *, weapon_breach_gates: bool = False,
) -> dict[str, int]:
    tally = {"won": 0, "lost": 0, "running": 0}
    total_turns = 0
    kill_target = (
        K.UPDATED_ALIEN_DAMAGE_TO_KILL if weapon_breach_gates
        else K.ALIEN_DAMAGE_TO_KILL
    )
    for seed in seeds:
        outcome, dmg, turns = play_turns(
            seed, ap_per_turn, weapon_breach_gates=weapon_breach_gates,
        )
        tally[outcome] += 1
        total_turns += turns
        print(f"    seed {seed:2d}: {outcome:<8} alien damage "
              f"{dmg:2d}/{kill_target}  ({turns} turns)")
    n = tally["won"] + tally["lost"] + tally["running"]
    avg = total_turns / n if n else 0
    print(f"  ap={ap_per_turn}: {tally['won']} won, {tally['lost']} lost, "
          f"{tally['running']} still running at the cap; "
          f"avg {avg:.0f} turns")
    return tally




def sweep(
    label: str, seeds: range, *, weapon_breach_gates: bool = False,
) -> dict[str, int]:
    tally = {"won": 0, "lost": 0, "running": 0}
    best = 0
    for seed in seeds:
        outcome, dmg, ticks = play(seed, weapon_breach_gates=weapon_breach_gates)
        tally[outcome] += 1
        best = max(best, dmg)
        print(f"    seed {seed:2d}: {outcome:<8} alien damage "
              f"{dmg:2d}/{K.ALIEN_DAMAGE_TO_KILL}  ({ticks} ticks)")
    print(f"  {label}: {tally['won']} won, {tally['lost']} lost, "
          f"{tally['running']} still running at the cap; "
          f"best alien damage {best}/{K.ALIEN_DAMAGE_TO_KILL}")
    return tally


def _run_ap_sweep(argv: list[str]) -> None:
    """`--turns --ap 1,2,3,4 [--original] [seeds]` - the turn-based AP sweep.

    Same methodology as the plain sweep above (seeded games, win/loss
    tallied), applied to `TURN_ACTIONS_PER_TURN` instead of the weapon
    breach gates - the evidence base for picking that constant instead of
    guessing it, the way DISC-258/DISC-289 did for the gates.

    **Defaults to `weapon_breach_gates=True` (DEC-045)** - the AP question
    that actually needed answering was "how hard is turn-based UPDATED with
    DEC-044's gate-aware retreat", not ORIGINAL (which has no gate at all,
    so nothing about DEC-044 changes its own turn-based difficulty). Pass
    `--original` to sweep ORIGINAL's own numbers instead.
    """
    ap_values = [2]
    n = 16
    args = list(argv)
    gates = True
    if "--original" in args:
        gates = False
        args.remove("--original")
    if "--ap" in args:
        i = args.index("--ap")
        ap_values = [int(v) for v in args[i + 1].split(",")]
        del args[i:i + 2]
    if args:
        n = int(args[0])
    label = "UPDATED (gates on)" if gates else "ORIGINAL (gates off)"
    print(f"Turn-based AP sweep, {n} seeds each, {label}\n")
    results = {}
    for ap in ap_values:
        results[ap] = sweep_turns(ap, range(n), weapon_breach_gates=gates)
        print()
    print("VERDICT: " + " -> ".join(
        f"ap={ap} {t['won']}/{n} won" for ap, t in results.items()
    ))


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv and argv[0] == "--turns":
        _run_ap_sweep(argv[1:])
    else:
        n = int(argv[0]) if argv else 16
        print(f"DISC-258/DEC-044, {n} seeds\n")
        print("GATES OFF (ORIGINAL - what it ships, permanently)")
        off = sweep("gates off", range(n), weapon_breach_gates=False)
        print()
        print("GATES ON, DEC-044 retuned values (UPDATED)")
        on = sweep("gates on", range(n), weapon_breach_gates=True)
        print()
        print(f"VERDICT: off {off['won']}/{n} won -> on {on['won']}/{n} won")
