"""Can the game actually be won? Yes — and here is what was stopping it.

The suite had 724 tests and not one played a real game to a victory. The two
existing win tests stage a two-room ship with the Alien, an armed crew member
and an open airlock already in place, then fire one order: they prove the win
*check* fires, not that a win is *reachable*.

Writing the real thing found the game unwinnable, and chasing that down through
the live oracle found the cause — the hull-breach test is an **equality**, not a
threshold (DISC-204). With that corrected, 10 of 12 seeded games are won by
killing the Alien and 2 are lost. A game.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import winnability_sweep  # noqa: E402

from alien_remake.core import constants as K
from alien_remake.core.crew import CrewMember
from alien_remake.core.flow import default_simulation
from alien_remake.core.sim import Simulation
from alien_remake.core.modes import DeathVariant, GameMode
from alien_remake.core.map import Room, ShipMap  # noqa: F401
from alien_remake.core.orders import Order, OrderType
from alien_remake.core.state import GamePhase, GameState, WinRoute

def _line_ship() -> ShipMap:
    """Two adjacent rooms; enough to exercise the breach test."""
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0))
    m.add_room(Room("B", 0, "B", 1, 0))
    m.add_door("A", "B")
    return m


WEAPONS = ("harpn_gun", "incineratr", "laser_pist", "elctrc_prd", "spanner")


def test_a_room_pushed_past_twenty_is_permanently_safe() -> None:
    """The hull breach is an equality, which makes overshoot a *tactic*.

        5658  CMP #$14        ; exactly 20?
        565A  BNE $565F       ; no  -> just latch alarm stage 2
        565C  JMP hull_breach ; yes -> the ship is destroyed

    The counter only ever climbs, so a room carried past 20 can never equal it
    again: it latches critical and is then safe to fight in forever. A harpoon
    hit (+15) can deliberately burn a room out.

    The remake used `>=`, reasoning that "overshooting 20 must not make a room
    immortal" — but in the original it does exactly that. Treating every
    crossing as fatal is what made the kill route unreachable: 50 damage at
    +1 a hit costs 300 hull, which is impossible if no room may ever pass 20,
    and routine if rooms can be burnt out first.
    """
    ship = _line_ship()
    state = GameState(crew={})
    sim = Simulation(state=state, ship=ship)

    state.room_damage["A"] = K.HULL_BREACH_THRESHOLD + 5      # overshot
    state.room_damage["B"] = K.HULL_BREACH_THRESHOLD - 1      # one short
    sim.advance()
    assert state.phase is GamePhase.RUNNING, "overshoot must not breach"

    state.room_damage["B"] = K.HULL_BREACH_THRESHOLD          # exactly 20
    sim.advance()
    assert state.phase is GamePhase.LOST, "landing exactly on 20 must breach"


def test_the_narcissus_holds_fewer_crew_than_the_launch_requires() -> None:
    """The evacuation route is blocked by a capacity/eligibility contradiction.

    `_launch_narcissus` refuses unless **every alive crew member** is aboard the
    evac room (`$5B9E` + `check_mother_refuses $5B1F`). But the evac room is an
    ordinary room and obeys `ROOM_CAPACITY`, so at most 3 can be in it.

    With 6 crew alive after the opening death, the launch can therefore never be
    granted: crew 4-6 cannot board, so the "everyone aboard" test can never
    pass. Observed directly — 8 seeded games all plateau at exactly 3 aboard.

    That is not necessarily *wrong* (the ROM has the same shape, and it is why
    the real game is brutal), but it means an evacuation win requires being
    reduced to <= 3 survivors first. Nothing in the remake tells the player
    that, and no test covered it.
    """
    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    alive = sum(1 for c in sim.state.crew.values() if c.alive)

    assert alive == 6, "the opening kills one of the seven"
    assert K.ROOM_CAPACITY == 3
    assert alive > K.ROOM_CAPACITY, (
        "if the crew now fit in the Narcissus, the evacuation route just became "
        "reachable from the start — add a test that actually flies it"
    )


def test_a_scripted_hunter_can_kill_the_alien() -> None:
    """End-to-end: a real game, a real player policy, and the wall it hits.

    The test the suite was missing: it builds the actual Nostromo, arms the
    crew, hunts the Alien and plays to a conclusion. Over 12 seeds this policy
    wins 10 and loses 2, which is the point — a game that is always winnable is
    as broken as one that never is.

    The policy is the interesting part, and two details in it are ROM
    behaviour rather than convenience:

    - **Only order an idle crew member.** `queue_order` re-arms the turn timer
      at issue time (`$7B69`), so re-issuing every tick freezes someone in
      place forever. The first version of this probe issued 7,759 MOVE orders
      and never completed one.
    - **Give up on a crew member who stops responding.** The android silently
      drops orders (`$5265`); the first probe spent an entire game ordering the
      android to attack while it stood next to the Alien ignoring every one.
    """
    # Seed at construction, not after. `Simulation.__init__` defaults to
    # `random.Random()` — seeded from OS entropy, not from the global RNG — and
    # draws the android and the opening death with it *during* construction. So
    # assigning `sim.rng` afterwards leaves those two choices random, and this
    # test order-dependent: it passed alone and failed once per suite run.
    #
    # **Re-anchored from seed 1 to seed 0 (DISC-229).** Brett now backfills the
    # opening victim's room instead of being left in AIRLOCK 1 with the Alien,
    # which changes where a crew member is standing from tick 0 and therefore
    # every subsequent roll — each seed traces a different game now. Re-swept
    # 16 seeds after the change: 13 won, 2 lost, 1 still running at the cap,
    # so the property this test guards (winnable, but not *always*) still
    # holds; only this seed's label moved.
    sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.ORIGINAL,
                     rng=random.Random(0))
    state = sim.state
    ignored: dict[str, int] = {}

    for _ in range(6000):
        if state.phase is not GamePhase.RUNNING:
            break
        alien = state.alien
        assert alien is not None
        busy = {o.crew_id for o in sim._orders}
        if alien.alive and alien.room_id:
            for crew in state.crew.values():
                if crew.id in busy or not crew.alive or not crew.awake:
                    continue
                if crew.health < 2 or crew.in_duct or ignored.get(crew.id, 0) >= 5:
                    continue
                armed = any(
                    i.holder == crew.id and i.type_id in WEAPONS
                    for i in state.items.values()
                )
                if armed:
                    target = (
                        OrderType.ATTACK
                        if crew.room_id == alien.room_id
                        else OrderType.MOVE_TO
                    )
                    sim.queue_order(
                        Order(crew.id, target, alien.room_id)
                        if target is OrderType.MOVE_TO
                        else Order(crew.id, target)
                    )
                else:
                    here = [
                        i for i in state.items.values()
                        if i.room_id == crew.room_id and i.type_id in WEAPONS
                    ]
                    if here:
                        sim.queue_order(Order(crew.id, OrderType.GET_ITEM, here[0].id))
        sim.advance()
        for order, outcome in sim.last_outcomes:
            if outcome.name == "BLOCKED":
                ignored[order.crew_id] = ignored.get(order.crew_id, 0) + 1
            elif outcome.name == "COMPLETED":
                ignored[order.crew_id] = 0

    alien = state.alien
    assert alien is not None
    assert state.phase is GamePhase.WON, (
        f"the hunt failed: phase={state.phase.name}, alien damage="
        f"{alien.damage}/{K.ALIEN_DAMAGE_TO_KILL}. Seed 0 is a winnable game; "
        "if this regresses, the breach test or the order pipeline has moved."
    )
    assert state.win_route is WinRoute.ALIEN_KILLED
    assert not alien.alive and alien.damage >= K.ALIEN_DAMAGE_TO_KILL


def test_the_evacuation_route_can_actually_be_flown() -> None:
    """Win route EVACUATED, demonstrated rather than described (DISC-253).

    The test above documents *why* it is normally blocked — `_launch_narcissus`
    needs every living crew member aboard (`$5B9E` + `check_mother_refuses
    $5B1F`), and the evac room is an ordinary room bound by `ROOM_CAPACITY`, so
    with six alive after the opening death nobody can satisfy it. It then said
    "an evacuation win requires being reduced to <= 3 survivors first" and left
    that untested.

    This flies it: reduce to capacity, board, catch the cat, launch.
    """
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    alive = [c for c in sim.state.crew.values() if c.alive]
    for casualty in alive[K.ROOM_CAPACITY:]:
        casualty.alive = False

    evac = sim.ship.evac_rooms()[0]
    survivors = [c for c in sim.state.crew.values() if c.alive]
    assert len(survivors) == K.ROOM_CAPACITY
    for c in survivors:
        c.room_id, c.in_duct = evac, False

    # "GO GET JONES" ($5C33) refuses the launch until the cat box is aboard.
    sim.state.jones_caught = False
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS)
    ), "the launch must be refused while Jones is still loose"
    assert sim.state.phase is not GamePhase.WON

    sim.state.jones_caught = True
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS)
    )
    assert sim.state.phase is GamePhase.WON
    assert sim.state.win_route is WinRoute.EVACUATED


def test_the_airlock_route_can_actually_be_flown() -> None:
    """Win route ALIEN_AIRLOCKED, which had no test at all (DISC-253).

    `$5ACC LDA $7D45 / CMP #$06 / BCC rts` — **a healthy Alien ignores an open
    airlock entirely**. Only once it has taken 6+ damage does the vent reach it,
    and then `alien_maybe_hide ($5ADD)` rolls: `rng >= damage` and it survives,
    thrown to one of rooms 0-3 with +1 damage; otherwise it goes out.

    So the lock is a finisher for a wounded creature, not an instant kill — and
    because the roll is against its damage, a more wounded Alien is *easier* to
    vent. Both halves are asserted here.
    """
    import random

    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    lock_of = lambda s: s.ship.airlock_rooms()[0]

    # A healthy Alien is untouched, however long the lock stands open.
    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    sim.rng = random.Random(0)
    lock = lock_of(sim)
    for c in sim.state.crew.values():
        if c.room_id == lock:
            c.room_id = None
    assert sim.state.alien is not None
    sim.state.alien.room_id, sim.state.alien.in_duct = lock, False
    sim.state.alien.damage = K.ALIEN_VENT_MIN_DAMAGE - 1
    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id=lock))
    for _ in range(50):
        sim.advance()
        sim.state.alien.room_id, sim.state.alien.in_duct = lock, False
    assert sim.state.phase is not GamePhase.WON, (
        "a healthy Alien must ignore an open lock ($5ACC CMP #$06)"
    )

    # A wounded one goes out. Seeded, and the roll is generous enough that this
    # is not flaky: it won on all 60 seeds when this was written.
    wins = 0
    for seed in range(8):
        sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
        sim.rng = random.Random(seed)
        lock = lock_of(sim)
        for c in sim.state.crew.values():
            if c.room_id == lock:
                c.room_id = None
        assert sim.state.alien is not None
        alien = sim.state.alien
        alien.room_id, alien.in_duct = lock, False
        alien.damage = K.ALIEN_VENT_MIN_DAMAGE
        sim.apply_special_option(
            SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id=lock)
        )
        for _ in range(200):
            sim.advance()
            if sim.state.phase is GamePhase.WON:
                assert sim.state.win_route is WinRoute.ALIEN_AIRLOCKED
                wins += 1
                break
            if not alien.alive:
                break
            alien.room_id, alien.in_duct = lock, False   # herd it back in
    assert wins == 8, f"the airlock route won only {wins}/8 seeded attempts"


def test_every_win_route_is_demonstrated_here() -> None:
    """Self-maintaining: a new `WinRoute` with no test fails this (DISC-253).

    Two of the three went untested for months, and the gap was invisible —
    `test_winnability.py` existed, passed, and covered only ALIEN_KILLED, while
    `FAITHFULNESS.md` still said no route was reachable at all. Counting the
    enum against this file's own source is what makes the omission loud.
    """
    from pathlib import Path

    source = Path(__file__).read_text(encoding="utf-8")
    missing = [
        route.name for route in WinRoute
        if f"WinRoute.{route.name}" not in source
    ]
    assert not missing, (
        f"win routes with no end-to-end test in this file: {missing}. "
        "Each one is a way to finish the game that nothing proves is reachable."
    )


def _armed_alone_with_alien(sim: Simulation, weapon_type: str) -> CrewMember:
    """One living crew member, alone with the Alien, holding ``weapon_type``.

    Shared setup for the weapon-breach-gate tests below: everyone else moved
    off the crew member's room, the Alien placed there, the weapon handed to
    them directly rather than fetched (the gate tests care about what a
    landed hit does to room damage, not about item pickup).
    """
    crew = next(c for c in sim.state.crew.values()
                if c.alive and c.id != sim.state.android_id)
    room = crew.room_id
    assert room is not None
    for other in sim.state.crew.values():
        if other.id != crew.id:
            other.room_id = None
    assert sim.state.alien is not None
    sim.state.alien.room_id, sim.state.alien.in_duct = room, False
    weapon = next(i for i in sim.state.items.values() if i.type_id == weapon_type)
    weapon.room_id, weapon.holder = None, crew.id
    crew.carried.append(weapon.id)
    crew.holding = weapon.id
    return crew


def test_the_weapon_breach_gates_are_off_under_original() -> None:
    """**DISC-258/DISC-289, DEC-044** — ORIGINAL never applies them, still.

    `$4A8D CMP #$05` (harpoon) and `$4AF6 CMP #$0E` (anything else) read the
    room's damage *before* adding and jump to `hull_breach` if it is already
    at the gate — the ROM's own decoded values. Wiring them in at those exact
    values was tried and reverted (DISC-258, re-run DISC-289): across 16
    seeded games the Alien never took more than 15 of the 50 damage needed,
    and no seed was won. ORIGINAL keeps that gap rather than shipping an
    unwinnable game — `default_simulation`'s `weapon_breach_gates` defaults
    to `False`, and this is the test that pins it there.

    DEC-044 resolved the gap for UPDATED instead (see the test below), by
    retuning the numbers rather than applying the ROM's own — so this test no
    longer asserts what `ROOM_BREACH_GATE_HARPOON`/`_OTHER` equal (those are
    UPDATED's tuned values now, not the ROM's `5`/`14`); it only asserts that
    ORIGINAL's flag being off means no gate fires regardless of the number.
    """
    import random

    from alien_remake.core.orders import Order, OrderType

    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    sim.rng = random.Random(0)
    assert sim.weapon_breach_gates is False, "ORIGINAL's own default"
    crew = _armed_alone_with_alien(sim, "harpn_gun")
    room = crew.room_id
    assert room is not None

    # Push room damage well past ANY plausible gate - a huge number, since
    # the point is that no number matters while the flag is off.
    sim.state.room_damage[room] = 10_000
    sim.queue_order(Order(crew.id, OrderType.ATTACK))
    sim.advance()

    assert sim.state.phase is GamePhase.RUNNING, (
        "a landed hit breached the ship with weapon_breach_gates off - "
        "ORIGINAL must never see this behaviour"
    )


def test_the_weapon_breach_gates_are_retuned_and_on_under_updated() -> None:
    """**DEC-044** — the owner's own acceptance test: 5 hits safe, the 6th not.

    UPDATED turns the decoded gates on (`Simulation(weapon_breach_gates=
    True)`), but at retuned values, not the ROM's `5`/`14` that DISC-289
    proved unwinnable. `ROOM_DAMAGE_PER_ATTACK` stays 6, so
    `ROOM_BREACH_GATE_OTHER` (26) clears `4 * 6 = 24` - a room at zero
    pre-existing damage takes 5 non-harpoon hits (0/6/12/18/24, all under
    26) before a 6th (would-be 30) breaches outright instead of landing.
    """
    import random

    from alien_remake.core.orders import Order, OrderType

    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    sim.rng = random.Random(0)
    sim.weapon_breach_gates = True
    crew = _armed_alone_with_alien(sim, "laser_pist")  # non-harpoon
    room = crew.room_id
    assert room is not None
    assert sim.state.room_damage.get(room, 0) == 0, "must start at zero damage"

    for hit in range(1, 6):
        sim.queue_order(Order(crew.id, OrderType.ATTACK))
        sim.advance()
        assert sim.state.phase is GamePhase.RUNNING, (
            f"hit {hit} of 5 breached the ship - the owner's own target is "
            "at least 5 safe hits from zero damage"
        )
        assert sim.state.room_damage[room] == hit * K.ROOM_DAMAGE_PER_ATTACK

    # Room damage is now 30 (5 hits at +6), already past the gate of 26 -
    # the pre-add check on hit 5 itself still passed (it saw 24, not 30), so
    # that hit landed normally. This 6th hit's check sees the post-hit-5
    # total, 30 >= 26, and breaches outright instead of adding.
    sim.queue_order(Order(crew.id, OrderType.ATTACK))
    sim.advance()
    assert sim.state.phase is GamePhase.LOST, (
        "a 6th hit from a room already at gate-or-above should breach "
        "outright rather than add and wait for the general equality check"
    )


def test_a_hull_breach_incapacitates_the_whole_crew() -> None:
    """**[C $5DB5-$5DC3] DISC-258** — nobody walks away from a hull breach.

    `hull_breach`'s tail is unambiguous::

        5DB5  LDY #$01
        5DB9  STA $7D45,Y     ; every crew member's health -> 1
        5DC1  LDA #$64 / STA $7D45   ; the Alien's own cell -> 100

    Health 1 is below the acting threshold, so the crew are out of the game.
    The remake set three flags and stopped there, so the ending counted six
    people as having come through the ship being holed — and with the android
    alive it reported the Nostromo brought safely home. A player saw exactly
    that and said it looked like a glitch. It was.
    """
    import random

    from alien_remake.core import constants as K

    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    sim.rng = random.Random(0)
    assert any(c.health > 1 for c in sim.state.crew.values() if c.alive)

    room = next(iter(sim.ship.rooms))
    sim.state.room_damage[room] = K.HULL_BREACH_THRESHOLD
    sim.advance()

    assert sim.state.phase is GamePhase.LOST
    assert sim.state.ship_destroyed
    living = [c for c in sim.state.crew.values() if c.alive]
    assert living, "the breach should incapacitate the crew, not delete them"
    assert all(c.health == 1 for c in living), (
        "the crew survived a hull breach at full health — this is what made "
        "the ending report survivors and a competence rating"
    )
    assert not [
        c for c in living if c.health >= K.HEALTH_WOUNDED_AT_LEAST
    ], "someone can still act after the ship was holed"
    assert sim.state.alien is not None and sim.state.alien.damage == 0


def test_updated_is_still_winnable_with_the_breach_gates_on() -> None:
    """**DEC-044** — the whole point of retuning instead of just enabling.

    `tools/winnability_sweep.py 16` (re-run by hand, not in CI - it takes a
    couple of minutes) finds 6 of 16 seeds won with the gates on and
    `UPDATED_ALIEN_DAMAGE_TO_KILL`, against 0 of 16 at the ROM's own 50 -
    landing in the owner's ~30-60% "hard but not impossible" target band.
    Re-running the full sweep on every test run would be too slow for the
    suite; this pins one known-winnable seed instead, so a future change
    that quietly makes UPDATED unwinnable again fails fast, the same
    function DISC-258's original test served for the un-gated question.
    """
    outcome, damage, ticks = winnability_sweep.play(
        0, cap=6000, weapon_breach_gates=True,
    )
    assert outcome == "won", (
        f"seed 0 is a known-winnable UPDATED game (alien damage "
        f"{damage}/{K.UPDATED_ALIEN_DAMAGE_TO_KILL}, phase after {ticks} "
        "ticks) - if this regresses, the retuned gate or "
        "UPDATED_ALIEN_DAMAGE_TO_KILL has moved without re-sweeping"
    )
    assert damage >= K.UPDATED_ALIEN_DAMAGE_TO_KILL


def test_turn_based_updated_is_winnable_at_its_own_ap_budget() -> None:
    """**DEC-045** — same pin, for turn-based UPDATED at `ap=5`.

    `tools/winnability_sweep.py --turns --ap 5 16` finds 5 of 16 seeds won
    (31.25%), the lowest AP value landing in the same ~30-60% band real-time
    UPDATED uses - but only once a DEC-044-forced retreat stopped costing a
    full action point (see `weapon_would_breach`'s own docstring); without
    that fix the same band needed ap~17, which stopped reading as "a few
    actions a turn" at all. Pinned the same way DEC-044's own test is,
    rather than re-running the full sweep here.
    """
    outcome, damage, turns = winnability_sweep.play_turns(
        4, K.UPDATED_TURN_ACTIONS_PER_TURN, weapon_breach_gates=True,
    )
    assert outcome == "won", (
        f"seed 4 at ap={K.UPDATED_TURN_ACTIONS_PER_TURN} is a known-winnable "
        f"turn-based UPDATED game (alien damage "
        f"{damage}/{K.UPDATED_ALIEN_DAMAGE_TO_KILL}, {turns} turns) - if "
        "this regresses, the AP-exemption for a gate-forced retreat or "
        "UPDATED_TURN_ACTIONS_PER_TURN has moved without re-sweeping"
    )
    assert damage >= K.UPDATED_ALIEN_DAMAGE_TO_KILL
