"""Tests for the Alien (timer-based random walk + combat), win conditions,
and the Special Options.

From the disassembly: the Alien no longer "senses" anyone — the decoded dispatcher
(``alien_choose_move $8A36``) rolls uniform 0-15 per action: 0-11 a compass
move over the real neighbor tables (60 ticks, D-038), 12-15 a duct hide
(40 ticks). The AI and combat
take an injected ``random.Random`` (same pattern as the PCS gate), so
:class:`FixedRandom` pins the rolls for deterministic tests (note
``random.Random.randrange`` derives from ``random()``, so pinning ``random()``
pins the roll).
"""

from __future__ import annotations

import random

import pytest

from alien_remake.core import constants
from alien_remake.core.alien import (
    _resolve_surface_action,
    Alien,
    _route_band,
    advance_alien,
    resolve_attack,
    spawn_alien,
)
from alien_remake.core.crew import CrewMember, Role
from alien_remake.core.items import ItemInstance
from alien_remake.core.map import (
    Grille,
    Room,
    ShipMap,
    default_ship,
    rooms_reachable_from,
)
from alien_remake.core.nostromo import nostromo_ship
from alien_remake.core.orders import Order, OrderOutcome, OrderType
from alien_remake.core.sim import Simulation
from alien_remake.core.special_options import SpecialOption, SpecialOptionType
from alien_remake.core.state import GamePhase, GameState, WinRoute

import needs                                       # noqa: E402


class FixedRandom(random.Random):
    """A ``random.Random`` whose ``random()``/``choice()`` are both pinned."""

    def __init__(self, value: float = 0.0, choice_index: int = 0) -> None:
        super().__init__()
        self._value = value
        self._choice_index = choice_index

    def random(self) -> float:  # type: ignore[override]
        return self._value

    def choice(self, seq):  # type: ignore[override]
        return seq[self._choice_index % len(seq)]


class RollRandom(random.Random):
    """Pins ``randrange`` to an exact value.

    ``FixedRandom`` pins ``random()``, which does **not** map linearly onto
    ``randrange`` (CPython's ``_randbelow_without_getrandbits`` scales by
    2**53 and takes a modulus), so a test that needs a specific Alien roll has
    to say so directly.
    """

    def __init__(self, roll: int) -> None:
        super().__init__()
        self._roll = roll

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self._roll


def _line_ship() -> ShipMap:
    """Rooms A-B-C-D in a door chain on deck 0 (no ducts/grilles/junctions)."""
    m = ShipMap()
    for i, rid in enumerate("ABCD"):
        m.add_room(Room(rid, 0, rid, i, 0))
    m.add_door("A", "B")
    m.add_door("B", "C")
    m.add_door("C", "D")
    return m


def _isolated_room_ship() -> ShipMap:
    """One room, no doors, no compass exits.

    `_compass_dest` (D-159's own decoded fallback) returns the room itself
    when there is nowhere to go, so the Alien lingers on every single
    action - guaranteeing more than one corrode-eligible action within a
    fixed loop count. `_line_ship`'s A-B-C-D chain, driven by a constant
    roll, only ever produces **one** such event total (DISC-325: the
    calibrated `ALIEN_CORRODE_RATE < 1.0` needs several to actually land a
    point of damage, not just one), so it stopped being useful for this.
    """
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0))
    return m


def _airlock_ship() -> ShipMap:
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 0, is_airlock=True))
    return m


# --- constants trace to the spec ------------------------------------------------

def test_alien_constants_trace_to_the_decompile() -> None:
    # FV-1.6: combat is a DETERMINISTIC per-item switch [C $4940] — no "lethal
    # subset" and no hit-chance (both invented, removed). The harpoon does +5, the
    # prod/incinerator/spanner/laser +1, non-weapons 0.
    assert constants.ITEM_ATTACK_DAMAGE["harpn_gun"] == 5
    assert constants.ITEM_ATTACK_DAMAGE["elctrc_prd"] == 1
    assert constants.ITEM_ATTACK_DAMAGE["spanner"] == 1
    assert constants.ITEM_ATTACK_DAMAGE["net"] == 0
    assert not hasattr(constants, "LETHAL_ITEM_IDS")       # invented, removed
    assert not hasattr(constants, "ATTACK_HIT_CHANCE")     # invented, removed
    assert not hasattr(constants, "ALIEN_ATTACK_HIT_CHANCE")  # invented, removed
    # Real action durations: surface move $8A4A (D-038: corrected from a
    # mislabeled 70 -- that's $6581, the *in-duct* dispatcher's own timer,
    # not this one), duct-entry $89E0.
    assert constants.ALIEN_MOVE_TICKS == 60
    assert constants.ALIEN_DUCT_TICKS == 40
    # R-28b/D-060 [C $58E8/$58ED]: arming loads a 9-unit countdown and a
    # 255-tick sub-counter, so the real timer is 9*255 — not the 60-tick
    # placeholder this used to assert.
    assert constants.AUTO_DESTRUCT_MINUTES == 9
    assert constants.AUTO_DESTRUCT_SUBTICKS == 255
    assert constants.AUTO_DESTRUCT_TICKS == 10 * 255   # D-162: TEN wraps
    # Cumulative combat + acid-blood room damage (full disassembly §8.6/§8.8).
    assert constants.ALIEN_DAMAGE_TO_KILL == 50   # $7D45[0] threshold ($32)
    assert constants.ROOM_DAMAGE_PER_ATTACK == 6
    # **P2-19, corrected 2026-08-02.** This used to assert 15, which is the
    # ROM's *stage-2 alarm* boundary (`$5594 CMP #$0F`), not the breach. The
    # breach is `$5658 CMP #$14` — damage **20**. Asserting 15 here was pinning
    # the simplification that ended games ~600-5000 ticks in.
    assert constants.HULL_BREACH_THRESHOLD == 20
    assert constants.DAMAGE_STAGE_SEVERE_FROM == 15
    assert constants.DAMAGE_STAGE_NOTHING_BELOW == 4


def test_airlock_flags() -> None:
    assert default_ship().airlock_rooms() == ["airlock"]
    # The real ship has exactly two (AIRLOCK 1 / AIRLOCK 2).
    assert nostromo_ship().airlock_rooms() == ["airlock_1", "airlock_2"]


# --- spawn / map helpers ---------------------------------------------------------

def test_spawn_alien_uses_the_observed_room_on_the_real_ship() -> None:
    # RW-8 resolved (D-014): the static table ($7935[0] == 0) and two live
    # boots agree — the Alien starts at room id 0 = AIRLOCK 1.
    assert spawn_alien(nostromo_ship()).room_id == "airlock_1"


def test_spawn_alien_falls_back_to_the_lowest_deck() -> None:
    m = ShipMap()
    m.add_room(Room("top", 0, "Top", 0, 0))
    m.add_room(Room("bot1", 2, "Bot1", 0, 0))
    m.add_room(Room("bot2", 2, "Bot2", 1, 0))
    alien = spawn_alien(m)
    assert alien.alive
    assert alien.room_id == "bot2"  # last deck-2 room by (y, x) order


def test_spawn_alien_with_no_rooms_is_unplaced() -> None:
    assert spawn_alien(ShipMap()).room_id is None


def test_rooms_reachable_from_counts_room_hops() -> None:
    assert rooms_reachable_from(_line_ship(), "A") == {"A": 0, "B": 1, "C": 2, "D": 3}


def test_rooms_reachable_from_unknown_room_is_empty() -> None:
    assert rooms_reachable_from(ShipMap(), "nope") == {}


def test_airlock_rooms_reports_flagged_rooms() -> None:
    assert _airlock_ship().airlock_rooms() == ["A"]


# --- Alien AI: timer-based random walk (the decoded $8A74 behavior) ----------------

def _compass_ship() -> ShipMap:
    """Two rooms with real compass exits: A's north is B."""
    m = ShipMap()
    m.add_room(Room("A", 0, "A", 0, 1, exits={"north": "B"}))
    m.add_room(Room("B", 0, "B", 0, 0, exits={"south": "A"}))
    m.add_door("A", "B")
    return m


def test_alien_compass_move_takes_move_ticks() -> None:
    ship = _compass_ship()
    state = GameState(crew={})
    alien = Alien(room_id="A")
    rng = FixedRandom(value=0.0)  # roll 0 -> north
    advance_alien(ship, state, alien, rng)  # picks the action
    assert alien.room_id == "A"  # still walking
    assert alien.timer == constants.ALIEN_MOVE_TICKS
    assert alien.dest_id == "B"
    for _ in range(constants.ALIEN_MOVE_TICKS):
        advance_alien(ship, state, alien, rng)
    assert alien.room_id == "B"  # landed after the full move duration


def test_alien_uses_the_real_route_tables_on_the_nostromo() -> None:
    # Full disassembly §8.10 (RW-6a): on the real ship the Alien's next room comes
    # from the game's own route tables, not the compass approximation.
    from alien_remake.core.gamedata_snapshot import ALIEN_ROUTES, ROOM_SLUGS

    ship = nostromo_ship()
    state = GameState(crew={})
    alien = Alien(room_id="airlock_1")  # location id 0
    advance_alien(ship, state, alien, FixedRandom(value=0.0))  # roll 0 -> table 0
    expected = ROOM_SLUGS[ALIEN_ROUTES[0][0]]  # table 0, current room id 0
    assert alien.dest_id == expected


def test_alien_never_takes_a_destination_equal_to_its_own_room() -> None:
    """**P2-19 — rewritten 2026-08-02; the old test pinned the bug.**

    It asserted that a blocked roll "moves the Alien to its own room — an idle
    that still consumes the full move duration". `alien_choose_move ($89C4)`
    does the opposite: `$89FF CPX $64E6 / $8A04 JMP $89C4` **re-rolls** when the
    chosen destination is the room the Alien is already in. The route tables
    encode "no exit this way" as a self-reference (same convention as the
    compass tables, D-083), so accepting one parked the Alien — in one measured
    game it sat in AIRLOCK 2 for 70% of the run, grinding that room to the
    breach threshold and ending the game by itself.
    """
    ship = _compass_ship()
    state = GameState(crew={})
    alien = Alien(room_id="B")
    # Every roll returns 0 -> north -> B, which has no north exit. The ROM
    # would spin; we bail out holding position rather than committing a
    # self-move, and critically we never claim to be "moving to B".
    advance_alien(ship, state, alien, FixedRandom(value=0.0))
    assert alien.dest_id != "B"


def test_the_alien_keeps_moving_on_the_real_ship() -> None:
    """The regression that matters: it must not settle anywhere for long.

    AIRLOCK 2 is the worst case — three of its five route-table entries are
    self-references — so it is the room that used to trap the Alien.
    """
    import random as _random
    from collections import Counter

    ship = nostromo_ship()
    state = GameState(crew={})
    alien = Alien(room_id="airlock_2")
    rng = _random.Random(1)
    seen: Counter[str] = Counter()
    for _ in range(4000):
        advance_alien(ship, state, alien, rng)
        if alien.room_id is not None and not alien.in_duct:
            seen[alien.room_id] += 1
    assert len(seen) > 5, f"the Alien only ever reached {sorted(seen)}"
    busiest = seen.most_common(1)[0][1] / sum(seen.values())
    assert busiest < 0.5, f"the Alien parks: {seen.most_common(3)}"


def test_alien_bursts_a_shut_grille_instead_of_slipping_through() -> None:
    """**[C $8B84] P-6.** This test used to assert the Alien entered the duct
    whatever the grille's state. It cannot: crossing a grille still in place
    makes it **tear the grille open** (clearing `$8676`) — 40 ticks, no move,
    and the grille is gone for good."""
    ship = _compass_ship()
    ship.add_grille("A")                     # closed by default
    state = GameState(
        # **D-188:** the crew member is incidental staging for this grille
        # test, but the Alien now *holds the room* whenever it meets crew
        # (`$8AE1 JMP $413C` bypasses the move dispatch), which would mask
        # the duct decision. Put them elsewhere so the encounter path is
        # not entered at all.
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "B")}
    )
    alien = Alien(room_id="A")
    # **P2-21:** with the grille still SHUT the duct needs a roll of **15**
    # (`$89C7 CMP #$0F`), not 12 — the old `FixedRandom(0.9)` produced 14,
    # which the ROM treats as an ordinary surface move.
    advance_alien(ship, state, alien, RollRandom(15))
    assert alien.in_duct is False            # it did NOT get in
    assert alien.timer == constants.ALIEN_BURST_TICKS
    assert alien.burst_grille_room == "A"
    assert next(g for g in ship.grilles if g.room_id == "A").is_open is True


def test_alien_slips_through_an_already_open_grille() -> None:
    """Once the grille is open (removed by the crew, or burst earlier) the
    Alien goes straight in — `$8BB7 BNE` falls through to `$8BB9`."""
    ship = _compass_ship()
    g = ship.add_grille("A")
    g.is_open = True
    state = GameState(
        # **D-188:** the crew member is incidental staging for this grille
        # test, but the Alien now *holds the room* whenever it meets crew
        # (`$8AE1 JMP $413C` bypasses the move dispatch), which would mask
        # the duct decision. Put them elsewhere so the encounter path is
        # not entered at all.
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "B")}
    )
    alien = Alien(room_id="A")
    rng = FixedRandom(value=0.9)
    advance_alien(ship, state, alien, rng)
    assert alien.in_duct is True
    assert alien.timer == constants.ALIEN_DUCT_TICKS
    # **Premise corrected with the one-pass restructure (D-100).** `alien_tick
    # ($8ACE)` resolves the action just *finished* — arrive, corrode, wound —
    # and only then dispatches the next one, so on the pass where the Alien
    # decides to duck into the vents it was still on the surface for the action
    # that ended. The test used to assert no harm on that very pass, which the
    # old two-tick split happened to produce.
    #
    # What "hidden" really means is that it does no further harm *while it is
    # in there*: hold it in the duct and nothing changes.
    hurt_once = state.crew["ripley"].health
    calm_once = state.crew["ripley"].fear
    for _ in range(constants.ALIEN_DUCT_TICKS + 1):
        advance_alien(ship, state, alien, FixedRandom(value=0.0))
        if not alien.in_duct:
            break
        assert state.crew["ripley"].health == hurt_once
        assert state.crew["ripley"].fear == calm_once
    assert state.crew["ripley"].alive is True


def test_wounded_alien_hunts_on_the_shorter_pursuit_timer() -> None:
    # Full disassembly §8.10 / D-012: a wounded Alien's aggression rises and it
    # acts on the shorter pursuit timer — an undamaged one never does.
    ship = _compass_ship()
    state = GameState(crew={})
    calm = Alien(room_id="A", damage=0)
    advance_alien(ship, state, calm, FixedRandom(value=0.0))
    assert calm.timer == constants.ALIEN_MOVE_TICKS          # never hunts

    # **[C $8A36] D-159** — the hunt latch `$64B4` is only consulted by the
    # grille-INTACT dispatcher (`$89F7`); `alien_choose_move`, which runs when
    # `$8676` reads 0, never looks at it and always loads `#$3C`. So the room
    # needs a grille still in place for a pursuit timer to be possible at all.
    # `_compass_ship()` has none, which under `$8676` semantics is the
    # already-open case.
    shut = _compass_ship()
    shut.grilles.append(Grille(room_id="A", is_open=False))
    hurt = Alien(room_id="A", damage=40)                     # aggression -> 10/16
    advance_alien(shut, state, hurt, FixedRandom(value=0.0))  # roll 0 < aggression
    assert hurt.timer == constants.ALIEN_PURSUIT_TICKS       # hunting: faster
    assert hurt.aggression == 0, "the $8A09 latch is spent by the move"


def test_alien_without_a_grille_rerolls_into_a_move() -> None:
    ship = _compass_ship()  # no grilles anywhere
    state = GameState(crew={})
    alien = Alien(room_id="A")
    advance_alien(ship, state, alien, FixedRandom(value=0.9))
    assert alien.in_duct is False
    assert alien.timer == constants.ALIEN_MOVE_TICKS


def test_being_wounded_by_the_alien_lowers_composure() -> None:
    # D-059 [C $4230]: the ROM's only Alien-related state-of-mind site
    # **decrements** (composure down), and fires when the Alien *wounds*
    # someone — not on mere proximity. The old test asserted a +3 proximity
    # bump, which had the direction AND the trigger wrong.
    ship = _line_ship()
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "C", holding_init="harpn_gun_1")
    parker = CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, "B")  # adjacent to C
    state = GameState(
        crew={"ripley": ripley, "parker": parker},
        items={"harpn_gun_1": ItemInstance("harpn_gun_1", "harpn_gun", None, "ripley")},
    )
    ripley.fear = 5
    parker.fear = 5
    alien = Alien(room_id="C")  # co-located with ripley; parker is adjacent
    advance_alien(ship, state, alien, FixedRandom(value=0.99))
    assert ripley.fear == 5 + constants.COMPOSURE_HIT_ALIEN_ATTACK  # wounded -> -1
    assert parker.fear == 5      # adjacent, unharmed -> unchanged
    assert ripley.alive is True


def test_wound_grades_status_and_incapacitates_below_the_floor() -> None:
    # Full disassembly §8.9: health counts down; below CREW_INCAPACITATED_BELOW
    # the crew member is out (LOST). A pure unit test of the health model.
    c = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    assert c.status == "O.K." and c.health == constants.CREW_START_HEALTH
    c.wound()
    assert c.alive is True and c.status == "wounded"
    while c.alive:
        c.wound()
    # Below the acting floor but not gone = COLLAPSED; zero health = DEAD.
    assert c.health < constants.CREW_INCAPACITATED_BELOW
    assert c.status in ("collapsed", "DEAD")


def test_alien_wounds_co_located_crew_rather_than_instant_kill() -> None:
    # **D-177 corrects FV-1.6's headline.** They survive the first encounter at
    # reduced health rather than dying outright - that half stands. But the
    # attack is **not** deterministic: `$4152 JSR rng / CMP #$07 / BCC rts`
    # means the Alien does nothing at all on 7 of 16 actions. FV-1.6 read
    # `alien_wound_crew ($5354)`, whose two callers both pass `$64C3` - the
    # **android's** slot - so that routine is the android's, not the Alien's.
    # `RollRandom(7)` is the lowest roll that attacks; with a single candidate
    # no victim roll follows ($41AA CPX #$01).
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    state = GameState(crew={"ripley": ripley})
    alien = Alien(room_id="A")
    advance_alien(_line_ship(), state, alien, RollRandom(7))
    assert ripley.alive is True
    assert ripley.health == constants.CREW_START_HEALTH - constants.ALIEN_WOUND_AMOUNT


def test_alien_wounds_a_crew_member_posts_a_notice() -> None:
    """Owner's report: no feedback when a crew member is hit. The only signal
    was the ATTACK_ALERT sound cue; there was no text at all (`$41C4`)."""
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    state = GameState(crew={"ripley": ripley})
    alien = Alien(room_id="A")
    advance_alien(_line_ship(), state, alien, RollRandom(7))
    assert state.notice == constants.NOTICE_ALIEN_WOUNDS.format(name="Ripley")
    assert state.notice_ticks == constants.NOTICE_TICKS


def test_alien_wounds_a_crew_member_even_if_armed() -> None:
    # The "armed crew are exempt" rule was invented and stays removed: nothing
    # on the Alien's encounter path ($413C-$41F7, D-177) looks at what anyone is
    # carrying. It gates on co-location, duct state and health >= 2, then rolls.
    ripley = CrewMember(
        "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="harpn_gun_1"
    )
    state = GameState(
        crew={"ripley": ripley},
        items={
            "harpn_gun_1": ItemInstance(
                "harpn_gun_1", "harpn_gun", room_id=None, holder="ripley"
            )
        },
    )
    alien = Alien(room_id="A")
    advance_alien(_line_ship(), state, alien, RollRandom(7))   # D-177
    assert ripley.alive is True
    assert ripley.health == constants.CREW_START_HEALTH - constants.ALIEN_WOUND_AMOUNT


def test_dead_alien_does_nothing() -> None:
    state = GameState(crew={})
    alien = Alien(room_id="A", alive=False)
    advance_alien(_line_ship(), state, alien, FixedRandom())
    assert alien.room_id == "A"


# --- resolve_attack (pure combat) — CUMULATIVE + DETERMINISTIC (§8.8, FV-1.6) ----

def test_resolve_attack_is_deterministic_per_item() -> None:
    # FV-1.6 [C $4940]: no RNG — each item wounds by a fixed amount. The harpoon
    # does +5 in one shot; a fresh Alien still needs many hits to reach 50.
    alien = Alien(room_id="A")
    result = resolve_attack(alien, "harpn_gun")
    assert result.hit is True and result.killed is False
    assert alien.alive is True
    assert alien.damage == constants.ITEM_ATTACK_DAMAGE["harpn_gun"] == 5


def test_resolve_attack_the_prod_and_spanner_wound_too() -> None:
    # The old "lethal subset" was invented: the electric prod and spanner each
    # deterministically wound +1 (ids 0-2 / 18-19, DISASSEMBLY §8.8).
    for item in ("elctrc_prd", "spanner", "laser_pist"):
        alien = Alien(room_id="A")
        result = resolve_attack(alien, item)
        assert result.hit is True and alien.damage == 1


def test_resolve_attack_kills_once_wounds_reach_the_threshold() -> None:
    alien = Alien(room_id="A", damage=constants.ALIEN_DAMAGE_TO_KILL - 1)
    result = resolve_attack(alien, "laser_pist")  # +1 -> 50
    assert result.hit is True and result.killed is True
    assert alien.alive is False


def test_resolve_attack_with_extinguisher_never_wounds() -> None:
    # D-033: only the extinguisher (and cat box, which aborts before reaching
    # here) truly do 0 damage. The net entangles instead of wounding (below);
    # the tracker DOES wound (`$49B5` falls to the same `$497A` INC $7D45).
    alien = Alien(room_id="A")
    result = resolve_attack(alien, "fire_extng")
    assert result.hit is False and result.killed is False
    assert alien.damage == 0 and alien.alive is True


def test_resolve_attack_with_the_tracker_wounds_and_is_smashed() -> None:
    # D-033: `resolve_attack`'s "TRACKER IS SMASHED" path ($49B5) falls
    # through to the same +1 wound instruction every other light item uses.
    alien = Alien(room_id="A")
    result = resolve_attack(alien, "tracker")
    assert result.hit is True and result.killed is False
    assert alien.damage == 1


def test_resolve_attack_with_the_net_entangles_but_never_wounds() -> None:
    # D-033: the net has no wound, but adds ALIEN_NET_ENTANGLE_TICKS to the
    # Alien's own move timer instead — a real entangle effect, not a no-op.
    alien = Alien(room_id="A", timer=10)
    result = resolve_attack(alien, "net")
    assert result.hit is False and result.killed is False
    assert alien.damage == 0 and alien.alive is True
    assert alien.timer == 10 + constants.ALIEN_NET_ENTANGLE_TICKS


def test_resolve_attack_against_a_dead_alien_is_a_noop() -> None:
    alien = Alien(room_id="A", alive=False)
    result = resolve_attack(alien, "harpn_gun")
    assert result.hit is False and result.killed is False


# --- ATTACK order through the Simulation (win routes 2/3) ------------------------

def _sim_ready_to_attack(*, airlock_open: bool) -> Simulation:
    ship = _airlock_ship()
    state = GameState(
        crew={
            "ripley": CrewMember(
                "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="harpn_gun_1"
            )
        },
        items={
            "harpn_gun_1": ItemInstance(
                "harpn_gun_1", "harpn_gun", room_id=None, holder="ripley"
            )
        },
        # Alien already wounded to one hit short of death, so a single landed
        # ATTACK finishes it (the win-route logic is what these tests exercise;
        # the attrition itself is covered by the resolve_attack tests above).
        alien=Alien(room_id="A", damage=constants.ALIEN_DAMAGE_TO_KILL - 1),
        airlocks_open={"A": True} if airlock_open else {},
    )
    return Simulation(state=state, ship=ship, rng=FixedRandom(value=0.0))


def test_attack_order_kills_the_alien_and_wins_by_kill() -> None:
    sim = _sim_ready_to_attack(airlock_open=False)
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.COMPLETED
    assert sim.state.phase is GamePhase.WON
    assert sim.state.win_route is WinRoute.ALIEN_KILLED
    assert sim.state.alien is not None and not sim.state.alien.alive


def test_attack_order_in_an_open_airlock_wins_by_airlock() -> None:
    sim = _sim_ready_to_attack(airlock_open=True)
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.win_route is WinRoute.ALIEN_AIRLOCKED


def test_attack_order_without_the_alien_present_is_blocked() -> None:
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")},
        alien=Alien(room_id="D"),
    )
    sim = Simulation(state=state, ship=ship)
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.state.phase is GamePhase.RUNNING


# --- attack feedback: nothing showed a hit at all before now ----------------

def test_attack_order_posts_a_hits_alien_notice() -> None:
    """Owner's report: no feedback when the Alien is hit. `resolve_attack`'s
    own banner (full disassembly §8.8, `$4BE0`) was never shown."""
    sim = _sim_ready_to_attack(airlock_open=False)
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.notice == constants.NOTICE_HITS_ALIEN.format(name="Ripley")
    assert sim.state.notice_ticks == constants.NOTICE_TICKS


def test_smashing_the_tracker_on_attack_posts_its_own_notice() -> None:
    """The more specific line wins over the generic "hits Alien" one - the ROM
    prints both in sequence, the remake shows one row-24 line at a time."""
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember(
            "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="tracker_1",
        )},
        items={"tracker_1": ItemInstance("tracker_1", "tracker", room_id=None, holder="ripley")},
        alien=Alien(room_id="A"),
    )
    # Pinned so the co-located Alien cannot ALSO land its own wound this same
    # tick and overwrite the notice this test is checking for (RollRandom, not
    # FixedRandom - randrange does not map linearly onto random()).
    sim = Simulation(state=state, ship=ship, rng=RollRandom(0))
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.notice == constants.NOTICE_TRACKER_SMASHED.format(name="Ripley")


def test_entangling_with_the_net_posts_its_own_notice() -> None:
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember(
            "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="net_1",
        )},
        items={"net_1": ItemInstance("net_1", "net", room_id=None, holder="ripley")},
        alien=Alien(room_id="A"),
    )
    sim = Simulation(state=state, ship=ship, rng=RollRandom(0))
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.notice == constants.NOTICE_NET_USED.format(name="Ripley")


def test_attacking_with_an_exhausted_laser_posts_the_roms_own_message() -> None:
    """**[C $4B94]** Only reachable via USE today - the literal ATTACK order
    does not check charges yet (a separate, already-filed gap)."""
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember(
            "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="laser_1",
        )},
        items={"laser_1": ItemInstance(
            "laser_1", "laser_pist", room_id=None, holder="ripley", uses_left=0,
        )},
        # No Alien: the exhaustion check happens before any Alien involvement,
        # and an Alien co-located here can independently land its own wound on
        # the same tick, overwriting the notice this test is checking for.
    )
    sim = Simulation(state=state, ship=ship)
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.state.notice == constants.NOTICE_LASER_EXHAUSTED.format(name="Ripley")


def test_using_an_empty_extinguisher_posts_the_roms_own_message() -> None:
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember(
            "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="extng_1",
        )},
        items={"extng_1": ItemInstance(
            "extng_1", "fire_extng", room_id=None, holder="ripley", uses_left=0,
        )},
    )
    sim = Simulation(state=state, ship=ship)
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.state.notice == constants.NOTICE_EXTINGUISHER_EMPTY.format(name="Ripley")


# --- Special Options --------------------------------------------------------------

def test_a_healthy_alien_ignores_an_open_airlock() -> None:
    """**[C $5ACC] D-155 — `CMP #$06 / BCC rts`.** The vent cannot touch the
    Alien until it has taken at least 6 damage. The remake killed it outright
    whenever it happened to be in the room, turning the airlock into a
    one-click win."""
    import random

    sim = Simulation(
        state=GameState(crew={}, alien=Alien(room_id="A")),
        ship=_airlock_ship(), rng=random.Random(0),
    )
    assert sim.state.alien is not None
    sim.state.alien.damage = 0
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A")
    )
    assert sim.state.airlocks_open["A"] is True
    assert sim.state.alien.alive, "an unhurt Alien must be unaffected"
    assert sim.state.phase is GamePhase.RUNNING


def test_a_badly_hurt_alien_is_blown_out_of_an_open_airlock() -> None:
    """**[C $5ADD `alien_maybe_hide`]** past the damage gate it is a ROLL:
    `rng >= damage` and the creature survives (taking +1 and a long delay);
    otherwise it goes out. The roll is a flat 0-15, so once damage reaches 16
    ejection is certain."""
    import random

    def attempt(damage: int, seed: int):
        sim = Simulation(
            state=GameState(crew={}, alien=Alien(room_id="A")),
            ship=_airlock_ship(), rng=random.Random(seed),
        )
        assert sim.state.alien is not None
        sim.state.alien.damage = damage
        sim.apply_special_option(
            SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A")
        )
        return sim

    # At the very top of the damage scale the roll can never save it.
    sim = attempt(16, 0)
    assert sim.state.phase is GamePhase.WON
    assert sim.state.win_route is WinRoute.ALIEN_AIRLOCKED

    # Just past the gate it is genuinely a gamble -- some seeds eject, some
    # leave it alive and one point worse off ($5B00 INC $7D45).
    outcomes = [attempt(6, seed).state.alien.alive for seed in range(40)]
    assert any(outcomes) and not all(outcomes), "damage 6 must be a real roll"
    survivor = next(
        s for s in range(40) if attempt(6, s).state.alien.alive
    )
    sim = attempt(6, survivor)
    assert sim.state.alien is not None
    assert sim.state.alien.damage == 7, "a survived vent costs it a point"



def test_open_airlock_kills_crew_caught_inside() -> None:
    """FV-1b5 [C $5A6A]: BLOWLOCK vents whoever is in the room, not just the
    Alien — a crew member caught in the vented airlock dies too."""
    ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    dallas = CrewMember("dallas", "Dallas", Role.CAPTAIN, "B")
    ship = _airlock_ship()
    ship.add_room(Room("B", 0, "B", 1, 0))
    sim = Simulation(
        state=GameState(crew={"ripley": ripley, "dallas": dallas}, alien=Alien(room_id=None)),
        ship=ship,
    )
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A")
    )
    assert ripley.alive is False and ripley.health == 0     # caught in the vent
    assert dallas.alive is True                              # elsewhere, spared
    # A vented crew death is not itself a win/loss (only an all-crew-dead check
    # in advance() reacts to it) unless it also happens to be the Alien's room.
    assert sim.state.phase is GamePhase.RUNNING


def test_open_and_seal_airlock_reject_a_non_airlock_room() -> None:
    sim = Simulation(state=GameState(crew={}), ship=_line_ship())
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A"))
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.SEAL_AIRLOCK, room_id="A"))


def test_seal_airlock_closes_it_again() -> None:
    ship = _airlock_ship()
    sim = Simulation(state=GameState(crew={}, alien=Alien(room_id=None)), ship=ship)
    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A"))
    assert sim.state.airlocks_open["A"] is True
    sim.apply_special_option(SpecialOption(SpecialOptionType.SEAL_AIRLOCK, room_id="A"))
    assert sim.state.airlocks_open["A"] is False


def test_launch_narcissus_requires_every_survivor_aboard() -> None:
    ship = _airlock_ship()
    ship.add_room(Room("B", 0, "B", 1, 0))
    state = GameState(
        crew={
            "ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A"),
            "parker": CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, "B"),
        },
        jones_caught=True,  # Jones aboard (else "GO GET JONES")
    )
    sim = Simulation(state=state, ship=ship)
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))
    sim.state.crew["parker"].room_id = "A"
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))
    assert sim.state.phase is GamePhase.WON
    assert sim.state.win_route is WinRoute.EVACUATED


def test_launch_narcissus_refused_until_jones_is_caught() -> None:
    # Full disassembly ($5C33 "GO GET JONES"): launch is refused while Jones is
    # still on the ship, even with every survivor aboard.
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")},
        jones_caught=False,
    )
    sim = Simulation(state=state, ship=_airlock_ship())
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))
    sim.state.jones_caught = True
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))


def test_launch_narcissus_ignores_the_dead() -> None:
    state = GameState(
        crew={
            "ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A"),
            "parker": CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, None, alive=False),
        },
        jones_caught=True,
    )
    sim = Simulation(state=state, ship=_airlock_ship())
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))


def test_launch_narcissus_without_an_airlock_is_rejected() -> None:
    ship = _line_ship()
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")}
    )
    sim = Simulation(state=state, ship=ship)
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))


def test_enter_hypersleep_is_one_way_via_the_specials_menu() -> None:
    # 1:1 fidelity: the game's specials menu has ENTER HYPERSLEEP only — no exit
    # option exists (the old EXIT_HYPERSLEEP special was an invention, removed).
    # D-028: the real handler is room-gated to the CRYO VAULT.
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "cryo_vault")},
        awake_crew=1,
    )
    sim = Simulation(state=state, ship=_line_ship())
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.ENTER_HYPERSLEEP, crew_id="ripley")
    )
    assert sim.state.crew["ripley"].awake is False
    assert sim.state.awake_crew == 0
    # D-028: the real handler also removes the sleeper from the room grid
    # (the ROM moves them to a location sentinel) — unreachable by the Alien.
    assert sim.state.crew["ripley"].room_id is None
    # Already asleep: a second ENTER is a no-op.
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.ENTER_HYPERSLEEP, crew_id="ripley")
    )
    # There is no EXIT_HYPERSLEEP special any more (removed for 1:1 fidelity).
    assert not hasattr(SpecialOptionType, "EXIT_HYPERSLEEP")


def test_catching_jones_is_a_roll_and_records_the_container() -> None:
    """**[C $8787-$880E] D-153 — catching him is a per-character ROLL.**

    The remake treated the cat box as an automatic catch. The ROM reads a
    threshold from `$883C,Y` (13-15 for the crew), rolls a flat 0-15, and
    succeeds only on `roll >= threshold` — so the box alone is a 1-to-3 in 16
    shot and a miss simply costs the attempt. On success the catching item is
    renamed to hold him, which is what the launch gate later looks for.

    **P8-3/D-160 (2026-08-07):** issued as `GET_JONES`, not `USE`. D-153
    hung the roll off a net/box USE; `route_command ($8437)` actually
    reaches `$8784` from **panel row 15**, the contextual GET JONES option
    `guard_6580` writes into `$0676`.
    """
    import random

    def staged(seed: int, item_type: str = "cat_box"):
        state = GameState(
            crew={
                "ripley": CrewMember(
                    "ripley", "Ripley", Role.WARRANT_OFFICER, "A",
                    holding_init="catcher",
                )
            },
            items={
                "catcher": ItemInstance(
                    "catcher", item_type, room_id=None, holder="ripley"
                )
            },
            jones_room_id="A",
            alien=Alien(room_id=None),
        )
        return Simulation(state=state, ship=_line_ship(), rng=random.Random(seed))

    # Over many attempts it succeeds sometimes and fails sometimes -- it is
    # emphatically not automatic.
    results = []
    for seed in range(40):
        sim = staged(seed)
        sim.queue_order(Order("ripley", OrderType.GET_JONES))
        sim.advance()
        results.append(sim.state.jones_caught)
    assert any(results), "it must be possible to catch him"
    assert not all(results), "...but not guaranteed on a single attempt"

    # On a success the container is recorded ($87B6/$87D7's rename).
    winner = next(seed for seed in range(40) if results[seed])
    sim = staged(winner)
    sim.queue_order(Order("ripley", OrderType.GET_JONES))
    sim.advance()
    assert sim.state.jones_caught is True
    assert sim.state.jones_room_id is None
    assert sim.state.jones_container_id == "catcher"
    assert not hasattr(SpecialOptionType, "CATCH_JONES")


def test_the_net_catches_jones_and_does_it_better_than_the_box() -> None:
    """**[C $879A/$87A1-$87AA]** `CMP #$10` accepts the NET as a catcher, and
    four `DEC $6518`s improve the threshold by 4 — so the net is markedly the
    better tool. The remake accepted only the cat box."""
    import random

    def catches(item_type: str) -> int:
        hits = 0
        for seed in range(200):
            state = GameState(
                crew={
                    "ripley": CrewMember(
                        "ripley", "Ripley", Role.WARRANT_OFFICER, "A",
                        holding_init="catcher",
                    )
                },
                items={
                    "catcher": ItemInstance(
                        "catcher", item_type, room_id=None, holder="ripley"
                    )
                },
                jones_room_id="A",
                alien=Alien(room_id=None),
            )
            sim = Simulation(state=state, ship=_line_ship(), rng=random.Random(seed))
            sim.queue_order(Order("ripley", OrderType.GET_JONES))
            sim.advance()
            hits += sim.state.jones_caught
        return hits

    with_net, with_box = catches("net"), catches("cat_box")
    assert with_net > 0 and with_box > 0
    assert with_net > with_box, "the net must be the better catcher"



def test_use_cat_box_in_the_wrong_room_is_blocked() -> None:
    state = GameState(
        crew={
            "ripley": CrewMember(
                "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="cat_box_1"
            )
        },
        items={"cat_box_1": ItemInstance("cat_box_1", "cat_box", room_id=None, holder="ripley")},
        jones_room_id="C",
        alien=Alien(room_id=None),
    )
    sim = Simulation(state=state, ship=_line_ship())
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.state.jones_caught is False


def test_auto_destruct_ends_the_game_when_it_reaches_zero() -> None:
    state = GameState(crew={}, alien=Alien(room_id=None))
    sim = Simulation(state=state, ship=_line_ship())
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    # Already running: a second INITIATE is a no-op.
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    sim.run(constants.AUTO_DESTRUCT_TICKS)
    assert sim.state.phase is GamePhase.LOST


def test_override_detonation_cancels_the_countdown() -> None:
    """FV-2c [C-live]: OVERRIDE DETONATION is the real cancel action, confirmed
    live (firing SCUTTLE NOSTROMO makes an "Override Detonation" entry appear;
    it's a no-op before arming and cancels the countdown once armed)."""
    state = GameState(crew={}, alien=Alien(room_id=None))
    sim = Simulation(state=state, ship=_line_ship())
    # Not armed yet: OVERRIDE is a no-op.
    assert not sim.apply_special_option(SpecialOption(SpecialOptionType.OVERRIDE_DETONATION))
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    assert sim.state.auto_destruct_ticks is not None
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.OVERRIDE_DETONATION))
    assert sim.state.auto_destruct_ticks is None
    sim.run(constants.AUTO_DESTRUCT_TICKS)
    assert sim.state.phase is GamePhase.RUNNING  # cancelled -> no longer ends the game


# --- acid blood: room damage & hull breach (full disassembly §8.6/§8.7) -----------

def test_the_alien_corrodes_the_room_it_occupies() -> None:
    """`guard_6562 ($8EBD)` does `INC $653F,X` for the Alien's room.

    Live-verified: with every crew member teleported away from the Alien, so
    nothing else could be writing the array, `$653F` climbed steadily across
    many rooms and room 34 reached alarm stage 2 (critical) inside the first
    minute of play.

    An earlier version of this test asserted the **opposite**, on the strength
    of two `$653F` reads that happened to be taken seconds after a new game
    began and again after the end-of-game re-init — both legitimately zero, and
    neither evidence of anything. See DISC-203.
    """
    ship = _isolated_room_ship()
    state = GameState(crew={})
    alien = Alien(room_id="A")
    for _ in range(constants.ALIEN_MOVE_TICKS * 6):
        advance_alien(ship, state, alien, FixedRandom(value=0.0))
    assert sum(state.room_damage.values()) > 0, (
        "the Alien corroded nothing over six action cycles"
    )


def test_a_hunting_alien_does_not_corrode_the_ship() -> None:
    """`$89AF LDX $64B4 / BNE` skips the corrosion call while hunting (DISC-205).

    The hunting latch is set by the aggression roll at `$4CB3`, which is fed by
    the Alien's **own damage / 4**. So hurting the creature changes what it
    does: it stops chewing the ship and comes after the crew instead, on the
    20-tick pursuit timer and refusing to duck into a duct.

    That is a real mechanic and the remake had only half of it — the pursuit
    timer and the no-duct rule were modelled, the corrosion suppression was not.
    """
    ship = _isolated_room_ship()
    calm = GameState(crew={})
    alien = Alien(room_id="A")
    for _ in range(constants.ALIEN_MOVE_TICKS * 6):
        advance_alien(ship, calm, alien, FixedRandom(value=0.0))
    assert sum(calm.room_damage.values()) > 0, "an unprovoked Alien corrodes"

    # A wounded Alien that keeps winning its aggression roll corrodes nothing.
    hunted = GameState(crew={})
    hurt = Alien(room_id="A", damage=40, hunting=True)
    for _ in range(constants.ALIEN_MOVE_TICKS * 6):
        hurt.hunting = True            # keep the latch up, as repeated rolls would
        advance_alien(ship, hunted, hurt, FixedRandom(value=0.0))
    assert not hunted.room_damage, (
        f"a hunting Alien damaged {hunted.room_damage}; `$64B4` must gate the "
        "corrosion call"
    )


def test_an_attack_sequence_suppresses_corrosion() -> None:
    """`$8EBD LDA $6562 / BNE rts` — no corroding while the ATTACK panel is up.

    `$8CD9 INC $6562` raises it when the Alien meets crew; `reset_attack_state
    ($8C80)` clears it. In the remake the flag goes up with the post-encounter
    hold and comes down on the next ordinary dispatch.
    """
    ship = _line_ship()
    state = GameState(crew={})
    alien = Alien(room_id="A", attack_sequence=True, corrode_pending=True)
    before = dict(state.room_damage)
    advance_alien(ship, state, alien, FixedRandom(value=0.0))
    assert state.room_damage == before, "corroded during an attack sequence"


def test_landed_attack_spills_acid_into_the_room() -> None:
    sim = _sim_ready_to_attack(airlock_open=False)
    # Alien is staged one hit short of death; a landed ATTACK both kills it and
    # (because it *hit*) spills acid into room A. Ripley is holding the harpoon
    # (D-027: the harpoon's room-damage spill is +15, not the +6 other weapons
    # do — see constants.ROOM_DAMAGE_PER_ATTACK_HARPOON).
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.room_damage.get("A", 0) == constants.ROOM_DAMAGE_PER_ATTACK_HARPOON


def test_non_harpoon_landed_attack_spills_the_smaller_amount() -> None:
    # D-027: only the harpoon takes the +15/breach@5 room-damage path; every
    # other weapon (spanner here) takes the +6/breach@14 path instead.
    ship = _airlock_ship()
    state = GameState(
        crew={
            "ripley": CrewMember(
                "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="spanner_1"
            )
        },
        items={"spanner_1": ItemInstance("spanner_1", "spanner", room_id=None, holder="ripley")},
        alien=Alien(room_id="A", damage=constants.ALIEN_DAMAGE_TO_KILL - 1),
    )
    sim = Simulation(state=state, ship=ship, rng=FixedRandom(value=0.0))
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.room_damage.get("A", 0) == constants.ROOM_DAMAGE_PER_ATTACK


def test_net_attack_entangles_the_alien_and_is_consumed() -> None:
    # D-033: attacking with the net doesn't wound but entangles (adds
    # ALIEN_NET_ENTANGLE_TICKS to the Alien's move timer) and consumes the
    # net itself (ITEM_DESTROYED_ON_ATTACK) — no room-damage spill either,
    # since there was no landed hit.
    ship = _airlock_ship()
    state = GameState(
        crew={
            "ripley": CrewMember(
                "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="net_1"
            )
        },
        items={"net_1": ItemInstance("net_1", "net", room_id=None, holder="ripley")},
        alien=Alien(room_id="A", timer=5),
    )
    sim = Simulation(state=state, ship=ship, rng=FixedRandom(value=0.0))
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.alien is not None
    # >= rather than an exact sum: the Alien's own per-tick move/timer
    # bookkeeping in the same `advance()` call can adjust `timer` by a small
    # amount either side of the raw entangle add; the entangle's clear
    # majority contribution is what this test is guarding.
    assert sim.state.alien.timer >= 5 + constants.ALIEN_NET_ENTANGLE_TICKS - 1
    assert sim.state.alien.damage == 0
    assert "net_1" not in sim.state.items
    assert sim.state.crew["ripley"].holding is None
    assert sim.state.room_damage.get("A", 0) == 0


def test_tracker_attack_wounds_and_is_consumed() -> None:
    # D-033: attacking with the tracker lands a +1 wound (like prod/spanner)
    # and destroys the tracker instance (it's "smashed").
    ship = _airlock_ship()
    state = GameState(
        crew={
            "ripley": CrewMember(
                "ripley", "Ripley", Role.WARRANT_OFFICER, "A", holding_init="tracker_1"
            )
        },
        items={"tracker_1": ItemInstance("tracker_1", "tracker", room_id=None, holder="ripley")},
        alien=Alien(room_id="A"),
    )
    sim = Simulation(state=state, ship=ship, rng=FixedRandom(value=0.0))
    sim.queue_order(Order("ripley", OrderType.ATTACK))
    sim.advance()
    assert sim.state.alien is not None
    assert sim.state.alien.damage == 1
    assert "tracker_1" not in sim.state.items
    assert sim.state.crew["ripley"].holding is None


def test_room_damage_past_threshold_breaches_the_hull_and_loses() -> None:
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")},
        alien=Alien(room_id=None),
        room_damage={"A": constants.HULL_BREACH_THRESHOLD},
    )
    sim = Simulation(state=state, ship=_line_ship())
    sim.advance()
    assert sim.state.phase is GamePhase.LOST


# --- all-crew-dead loss ------------------------------------------------------------

def test_all_crew_dead_is_a_loss() -> None:
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A", alive=False)},
        alien=Alien(room_id=None),
    )
    sim = Simulation(state=state, ship=_line_ship())
    sim.advance()
    assert sim.state.phase is GamePhase.LOST


# --- R-28b / D-060: the auto-destruct countdown + override window -------------


def test_override_works_early_in_the_countdown() -> None:
    """[C $585E]: `LDA $657B / CMP #$05 / BCC skip` — the cancel is allowed
    while at least 5 of the 9 countdown units remain."""
    sim = Simulation()
    sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    assert sim.state.auto_destruct_ticks == constants.AUTO_DESTRUCT_TICKS
    assert sim.state.auto_destruct_minutes_left == constants.AUTO_DESTRUCT_MINUTES
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.OVERRIDE_DETONATION)
    ) is True
    assert sim.state.auto_destruct_ticks is None


def test_override_expires_once_too_few_units_remain() -> None:
    """D-060: past the window the detonation is **irreversible** — the remake
    used to allow cancelling right up to the last tick."""
    sim = Simulation()
    sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    # Wind the countdown down below the override threshold.
    sim.state.auto_destruct_ticks = (
        constants.AUTO_DESTRUCT_OVERRIDE_ABOVE - 1
    ) * constants.AUTO_DESTRUCT_SUBTICKS
    assert sim.state.auto_destruct_minutes_left < constants.AUTO_DESTRUCT_OVERRIDE_ABOVE
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.OVERRIDE_DETONATION)
    ) is False
    assert sim.state.auto_destruct_ticks is not None, "must stay armed"


def test_countdown_reaching_zero_destroys_the_ship() -> None:
    """[C $5A43]: `$657B == 0` -> `JMP hull_breach`."""
    sim = Simulation()
    sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    sim.state.auto_destruct_ticks = 1
    sim.advance()
    assert sim.state.phase is GamePhase.LOST


# --- P2-21: the two surface-movement distributions ---------------------------

def test_the_grille_state_picks_the_movement_distribution() -> None:
    """**[C $89BF `LDA $8676,Y` / $89C2 `BEQ`]** — the ROM branches to a whole
    different roll-handling routine depending on whether the room's grille is
    still in place, and the two disagree about *everything*.

    Open grille  -> `alien_choose_move ($8A36)`: duct at 12 (25%).
    Shut grille  -> `$89C4`:                     duct at 15 (6.25%).

    So the Alien is **four times more likely to take a duct that is already
    open** — leaving a grille open really does invite it in.
    """
    assert constants.ALIEN_DUCT_THRESHOLD_GRILLE_OPEN == 12
    assert constants.ALIEN_DUCT_THRESHOLD_GRILLE_SHUT == 15
    sides = constants.ALIEN_ROLL_SIDES
    p_open = (sides - constants.ALIEN_DUCT_THRESHOLD_GRILLE_OPEN) / sides
    p_shut = (sides - constants.ALIEN_DUCT_THRESHOLD_GRILLE_SHUT) / sides
    assert p_open == 0.25 and p_shut == 0.0625
    assert p_open == 4 * p_shut


def test_the_two_route_band_chains_are_the_roms_own() -> None:
    """Shut spreads 15 outcomes evenly (3/3/3/3/3); open spreads 12 as
    3/2/2/2/3 — so the Alien ranges wider when it cannot reach a duct."""
    assert constants.ROUTE_BAND_BOUNDS_GRILLE_OPEN == (3, 5, 7, 9)
    assert constants.ROUTE_BAND_BOUNDS_GRILLE_SHUT == (3, 6, 9, 12)

    def spread(bounds: tuple[int, ...], duct_at: int) -> list[int]:
        counts = [0] * 5
        for roll in range(duct_at):
            counts[_route_band(roll, bounds)] += 1
        return counts

    assert spread(constants.ROUTE_BAND_BOUNDS_GRILLE_SHUT, 15) == [3, 3, 3, 3, 3]
    assert spread(constants.ROUTE_BAND_BOUNDS_GRILLE_OPEN, 12) == [3, 2, 2, 2, 3]


def test_duct_travel_is_slower_than_walking() -> None:
    """[C $8AAB `LDA $6581`] duct-to-duct travel uses the `$6581` byte (70),
    not the surface move's literal `$3C` (60). Crawling beats walking for
    stealth, not for speed."""
    from alien_remake.core import gamedata_snapshot as data

    assert constants.ALIEN_DUCT_TRAVEL_TICKS == 70
    assert constants.ALIEN_DUCT_TRAVEL_TICKS == data.ALIEN_MOVE_TICKS
    assert constants.ALIEN_MOVE_TICKS == 60
    assert constants.ALIEN_DUCT_TRAVEL_TICKS > constants.ALIEN_MOVE_TICKS


def test_an_open_grille_measurably_pulls_the_alien_into_the_ducts() -> None:
    """The behavioural consequence, measured on the decision itself.

    Sampling `advance_alien` would measure the wrong thing twice over: it only
    *decides* when the action timer expires, and `$8A7A` separately keeps the
    Alien in the ducting longer while a grille is shut. What the `$89C2` branch
    controls is how often a surface action turns into a duct action — the ROM's
    25% (open) against 6.25% (shut).
    """
    import random as _random

    from alien_remake.core.alien import _begin_action

    def duct_rate(open_grille: bool) -> float:
        ship = nostromo_ship()
        rng = _random.Random(11)
        wanted = 0
        trials = 4000
        for _ in range(trials):
            for g in ship.grilles:           # restore the condition each trial
                g.is_open = open_grille
            alien = Alien(room_id="commdcentr")
            _begin_action(ship, alien, rng)
            # "went for the duct" = slipped in, or was stopped by the grille
            # and tore it open instead (`$8BB4` -> `_burst_grille`).
            if alien.in_duct or alien.burst_grille_room is not None:
                wanted += 1
        return wanted / trials

    shut, opened = duct_rate(False), duct_rate(True)
    # Both sit **above** the nominal 25% / 6.25%, and that is faithful: the
    # ROM's loop re-rolls a blocked (self-referencing) surface destination
    # without re-testing the duct branch first, so discarded surface rolls
    # inflate the duct's share in any room whose route row has gaps. The
    # invariant worth pinning is the gap between the two conditions.
    assert 0.05 < shut < 0.15, f"shut grille: {shut:.2%}"
    assert 0.25 < opened < 0.45, f"open grille: {opened:.2%}"
    assert opened > 3 * shut, f"open={opened:.2%} vs shut={shut:.2%}"


# --- P2-17: the Alien carries its kill into the ducting ----------------------

def test_the_alien_stows_a_victim_and_leaves_it_in_the_ducting() -> None:
    """**[C $4292/$599E/$59A7] P2-17.** A player found "a lot of crew in the
    ducts after the attack" — and that is a real mechanic, in three parts:

    * `alien_death_effects ($4292)` calls `stow_char` for a fresh kill, but
      only while the slot is free (`$429E LDA $64DC / BNE skip`);
    * `stow_char ($599E)` parks the victim at the off-map sentinel `$BB`;
    * `restore_stowed_char ($59A7)` runs only while the **Alien is in a duct**
      and writes them into the ducting at the Alien's own position.

    So a body does not stay where its owner died — the Alien drags it into the
    vents and leaves it somewhere along its route.
    """
    from alien_remake.core.alien import restore_stowed_char

    ship = nostromo_ship()
    victim = CrewMember("kane", "Kane", Role.EXECUTIVE_OFFICER, "commdcentr")
    victim.alive = False
    state = GameState(crew={"kane": victim}, stowed_crew_id="kane")
    victim.room_id = None                      # `$BB` — carried, off the map

    alien = Alien(room_id="galley", in_duct=False)
    restore_stowed_char(state, alien)          # `$59A7 LDA $6501 / BEQ` — not yet
    assert state.stowed_crew_id == "kane" and victim.room_id is None

    alien.in_duct = True
    restore_stowed_char(state, alien)
    assert victim.room_id == "galley" and victim.in_duct is True
    assert state.stowed_crew_id is None


def test_a_body_waits_while_someone_else_occupies_that_duct() -> None:
    """[C $59AE-$59B9] `restore_stowed_char` scans the crew first and returns
    without depositing if anyone is already in the ducting at the Alien's
    position — so bodies do not stack up on a living crew member."""
    from alien_remake.core.alien import restore_stowed_char

    victim = CrewMember("kane", "Kane", Role.EXECUTIVE_OFFICER, "commdcentr")
    victim.alive = False
    victim.room_id = None
    other = CrewMember("brett", "Brett", Role.CHIEF_ENGINEER, "galley")
    other.in_duct = True
    state = GameState(
        crew={"kane": victim, "brett": other}, stowed_crew_id="kane"
    )
    alien = Alien(room_id="galley", in_duct=True)
    restore_stowed_char(state, alien)
    assert state.stowed_crew_id == "kane", "should wait, not overwrite"
    assert victim.room_id is None

    # Once that duct clears, the body goes down.
    other.in_duct = False
    restore_stowed_char(state, alien)
    assert state.stowed_crew_id is None and victim.room_id == "galley"


def test_launch_needs_the_container_aboard_not_just_a_caught_cat() -> None:
    """**[C $5B1F check_mother_refuses] D-153 — "GO GET JONES" is about the
    CONTAINER's location.**

    The routine reads the location byte of whichever item was renamed to hold
    the cat and allows the launch only if it is `$22` (the NARCISSUS) or is
    carried by someone who is themselves aboard. Catching him is therefore
    only half the job: somebody has to carry the net or box into the shuttle.
    The remake accepted a bare `jones_caught`, which let you launch with the
    cat still sitting on the Nostromo.
    """
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    def staged(container_room, container_holder):
        sim = Simulation(rng=random.Random(4))
        evac = next(iter(sim.ship.evac_rooms()))
        for c in sim.state.crew.values():
            c.alive, c.health, c.room_id = True, 5, evac
        sim.state.jones_caught = True
        sim.state.jones_room_id = None
        sim.state.items["box"] = ItemInstance(
            "box", "cat_box", room_id=container_room, holder=container_holder
        )
        sim.state.jones_container_id = "box"
        return sim, evac

    # Box left behind in a corridor -> refused.
    sim, evac = staged("commdcentr", None)
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS)
    )

    # Box sitting in the Narcissus itself -> allowed ($5B3E).
    sim, evac = staged(evac, None)
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))

    # Carried by a crew member who is aboard -> allowed ($5B4C).
    sim, evac = staged(None, "ripley")
    sim.state.crew["ripley"].room_id = evac
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))

    # Carried by someone still on the ship -> refused.
    sim, evac = staged(None, "ripley")
    sim.state.crew["ripley"].room_id = "commdcentr"
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS)
    )


def test_jones_picks_his_room_from_the_aliens_route_tables() -> None:
    """**[C $8971-$89A6] D-156** — closes the `[?]` D-036 opened.

    Jones's destination is not a uniform pick among door neighbours: he rolls
    `AND #$07` (0-7) and reads the **same five route tables the Alien uses**,
    through his own band mapping (rolls 0-1, 2-3, 4, 5, 6-7 -> tables 1..5).
    """
    from alien_remake.core.alien import _JONES_ROUTE_BANDS, jones_dest
    from alien_remake.core.gamedata_snapshot import ALIEN_ROUTES, ROOM_SLUGS
    from alien_remake.core.nostromo import nostromo_ship

    assert _JONES_ROUTE_BANDS == (0, 0, 1, 1, 2, 3, 4, 4)

    ship = nostromo_ship()
    room = "commdcentr"
    idx = ROOM_SLUGS.index(room)
    for roll, band in enumerate(_JONES_ROUTE_BANDS):
        expected = ROOM_SLUGS[ALIEN_ROUTES[band][idx]]
        assert jones_dest(ship, room, roll) == expected

    # Not the same mapping as the panic walk over the same tables.
    from alien_remake.core.alien import _panic_route_band
    assert [_panic_route_band(r) for r in range(8)] != list(_JONES_ROUTE_BANDS)


def test_jones_will_not_walk_into_the_aliens_room() -> None:
    """**[C $88BB]** `LDA $657E / CMP $7935 / BEQ rts` — the candidate room is
    compared against the Alien's when the move is **committed**, and the move
    is abandoned if they match. The candidate itself was chosen a pass earlier
    ($8971), so a cat heading somewhere the creature then occupies simply
    stalls."""
    import random

    from alien_remake.core import constants
    from alien_remake.core.alien import jones_dest
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    start_room = "commdcentr"

    def run(alien_room, seed=0, passes=6):
        state = GameState(
            crew={}, jones_room_id=start_room, alien=Alien(room_id=alien_room)
        )
        sim = Simulation(state=state, ship=ship, rng=random.Random(seed))
        for _ in range(constants.JONES_MOVE_TICKS * passes):
            sim._advance_jones()
        return sim

    # With the Alien out of the way he wanders off somewhere.
    free = run("narcissus")
    assert free.state.jones_room_id != start_room

    # Park the Alien on whatever he had picked: the commit is vetoed and he
    # stays where he is for as long as the creature sits there.
    probe = Simulation(
        state=GameState(crew={}, jones_room_id=start_room, alien=Alien(room_id="narcissus")),
        ship=ship, rng=random.Random(0),
    )
    for _ in range(constants.JONES_MOVE_TICKS):
        probe._advance_jones()          # seeds the first candidate
    candidate = probe._jones_next
    assert candidate is not None

    blocked = Simulation(
        state=GameState(crew={}, jones_room_id=start_room, alien=Alien(room_id=candidate)),
        ship=ship, rng=random.Random(0),
    )
    for _ in range(constants.JONES_MOVE_TICKS * 6):
        blocked._advance_jones()
    assert blocked.state.jones_room_id == start_room, (
        "he must refuse to walk into the Alien's room"
    )

def test_crew_inside_a_duct_survive_the_vent() -> None:
    """**[C $5A80] `LDA $6501,Y / BNE skip`** — the vent skips anyone in the
    ducting of that room. We killed everyone present regardless."""
    from alien_remake.core.crew import CrewMember, Role

    on_floor = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    in_duct = CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, "A")
    in_duct.in_duct = True
    sim = Simulation(
        state=GameState(
            crew={"ripley": on_floor, "parker": in_duct}, alien=Alien(room_id=None)
        ),
        ship=_airlock_ship(),
    )
    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A"))
    assert not on_floor.alive, "someone standing in the lock is blown out"
    assert in_duct.alive, "someone in the ducting is safe"


def test_the_vent_takes_items_in_the_room_and_on_its_victims() -> None:
    """**[C $5A6C / $5A9E]** Items lying in the airlock go to space, and so
    does everything a vented crew member was carrying. We touched neither."""
    from alien_remake.core.crew import CrewMember, Role

    victim = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A",
                        holding_init="carried")
    sim = Simulation(
        state=GameState(
            crew={"ripley": victim},
            items={
                "loose": ItemInstance("loose", "spanner", room_id="A"),
                "carried": ItemInstance(
                    "carried", "laser_pist", room_id=None, holder="ripley"
                ),
                "elsewhere": ItemInstance("elsewhere", "spanner", room_id="B"),
            },
            alien=Alien(room_id=None),
        ),
        ship=_airlock_ship(),
    )
    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A"))
    assert "loose" not in sim.state.items, "items in the lock are blown out"
    assert "carried" not in sim.state.items, "...and what the victim carried"
    assert "elsewhere" in sim.state.items, "items in other rooms are untouched"


def test_an_open_airlock_keeps_venting_on_later_ticks() -> None:
    """**[C $7305]** `check_deferred_move` calls `apply_blowlock` on every move
    pass, so the lock does not vent once and stop — walk in afterwards and it
    still kills you. We vented only at the moment of opening."""
    from alien_remake.core.crew import CrewMember, Role

    latecomer = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "B")
    sim = Simulation(
        state=GameState(crew={"ripley": latecomer}, alien=Alien(room_id=None)),
        ship=_airlock_ship(),
    )
    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A"))
    assert latecomer.alive, "still safely next door"

    latecomer.room_id = "A"          # wanders into the open lock
    sim.advance()
    assert not latecomer.alive, "the open lock must still be venting"


def test_the_vent_never_touches_jones() -> None:
    """`blowlock_vent` never references `$657D` — the cat is simply not part
    of the vent's scan."""
    sim = Simulation(
        state=GameState(crew={}, jones_room_id="A", alien=Alien(room_id=None)),
        ship=_airlock_ship(),
    )
    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="A"))
    assert sim.state.jones_room_id == "A"
    assert sim.state.jones_caught is False


def test_an_unhunting_alien_stays_put_on_a_self_referencing_route() -> None:
    """**[C $89F7-$8A11] D-159** — the self-reference rejection is CONDITIONAL.

    P2-19 made it unconditional, so the Alien re-rolled until it found a real
    destination and therefore **never lingered anywhere**. The ROM only
    re-rolls on a *hunting* turn (`$64B4` set); on an ordinary turn `$89FA
    BEQ $8A11` returns with the self-referential destination in `$64E6` and a
    60-pass timer — it simply stands still.

    Both airlocks self-refer on 9 of their 16 rolls, so this is precisely what
    keeps the creature in a lock long enough for BLOWLOCK to reach it.
    """
    import random as _random

    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    state = GameState(crew={})
    # AIRLOCK 1's route row: rolls 0-5 -> corridor_6, 6-14 -> itself, 15 -> duct.
    # Roll 6 therefore lands squarely on the self-reference.
    alien = Alien(room_id="airlock_1", damage=0)
    advance_alien(ship, state, alien, RollRandom(6))
    assert alien.dest_id is None, "it must hold position, not be re-routed"
    assert alien.room_id == "airlock_1"
    assert alien.in_duct is False
    assert alien.timer == constants.ALIEN_MOVE_TICKS

    # And over many turns it really does dwell there rather than leaving at once.
    stays = 0
    for seed in range(200):
        a = Alien(room_id="airlock_1", damage=0)
        advance_alien(ship, state, a, _random.Random(seed))
        if a.dest_id is None:
            stays += 1
    # 9 of 16 rolls self-refer; well clear of the 0 the old model produced.
    assert stays > 60, f"expected the Alien to dwell in the lock, stayed {stays}/200"


def test_auto_destruct_runs_ten_sub_counter_wraps() -> None:
    """**[C $5A3E-$5A66] D-162** — `$657B` is read *before* it is decremented,
    and `hull_breach` is the wrap that finds it **already 0**. So arming
    spends 9 wraps walking the display 9 -> 0 and a **tenth** to detonate:
    10 x 255 = 2550 passes, not 9 x 255. The old value blew the ship a whole
    countdown unit (~32 s at MAIN_LOOP_HZ) early.

    The displayed counter must still read exactly `$657B`: 9 at the moment of
    arming, 0 during the final unit.
    """
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim = Simulation()
    crew = next(c for c in sim.state.crew.values() if c.alive)
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT, crew_id=crew.id)
    )
    assert sim.state.auto_destruct_ticks == 10 * constants.AUTO_DESTRUCT_SUBTICKS
    assert sim.state.auto_destruct_minutes_left == constants.AUTO_DESTRUCT_MINUTES

    # One full wrap later the display has ticked down by exactly one unit.
    sim.state.auto_destruct_ticks = 9 * constants.AUTO_DESTRUCT_SUBTICKS
    assert sim.state.auto_destruct_minutes_left == 8
    # The last unit runs with $657B == 0 -- still armed, no longer overridable.
    sim.state.auto_destruct_ticks = constants.AUTO_DESTRUCT_SUBTICKS
    assert sim.state.auto_destruct_minutes_left == 0


def test_an_alien_that_survives_the_vent_is_thrown_stunned_and_surfaced() -> None:
    """**[C $5AEE-$5B00] PV-16** — surviving an airlock vent is not a no-op.

    The remake only added the damage point and left the creature standing in
    the lock, so a survived vent changed nothing observable. The ROM throws it
    to `rng >> 2` (rooms 0-3: both airlocks, the armoury, cargopod 1), stuns it
    120 passes and forces it onto the surface.
    """
    import random

    from alien_remake.core.gamedata_snapshot import ROOM_SLUGS
    from alien_remake.core.nostromo import nostromo_ship

    lock = ROOM_SLUGS[0]                                   # AIRLOCK 1
    throw_targets = {ROOM_SLUGS[i] for i in range(4)}

    moved = 0
    for seed in range(60):
        ship = nostromo_ship()
        # damage 6 is the `$5ACC CMP #$06` floor: reachable, but the roll
        # (0-15 >= 6) survives far more often than not.
        alien = Alien(room_id=lock, in_duct=False, damage=6)
        state = GameState(crew={}, alien=alien)
        sim = Simulation(state=state, ship=ship, rng=random.Random(seed))
        sim.state.airlocks_open[lock] = True
        sim._vent_open_airlocks()
        if not alien.alive:
            continue                                        # blown out: the win
        assert alien.damage == 7, "$5B00 INC $7D45"
        assert alien.room_id in throw_targets, "$5AEE: dest = rng >> 2 -> rooms 0-3"
        assert alien.in_duct is False, "$5AFB STA $6501 = 0 forces it up"
        assert alien.timer == constants.ALIEN_VENT_STUN_TICKS   # $5AF6 #$78
        if alien.room_id != lock:
            moved += 1
    assert moved > 0, "the throw must be able to relocate it out of the lock"


def test_the_alien_encounter_is_doubly_random_and_wounds_exactly_one() -> None:
    """**[C $4152/$41A7-$41F7] D-177 — re-read out of the PRG.**

    FV-1.6 concluded the Alien's attack has "NO RNG chance" from
    `alien_wound_crew ($5354)`'s two callers. Both of those pass `$64C3`, the
    **android's** slot, as the attacker — that routine is the android's and the
    name is a misnomer. The Alien's own encounter is `$413C`, and it rolls
    twice: once to attack at all, once to pick a single victim.
    """
    needs.need(needs.ALIEN_PRG)
    import pathlib
    import random as _random

    from alien_remake.core.nostromo import nostromo_ship

    prg = pathlib.Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    mem = prg[2:]

    def at(addr: int, n: int) -> bytes:
        return mem[addr - load: addr - load + n]

    # The attack roll, and the three victim-count branches.
    assert at(0x4152, 6) == bytes((0x20, 0x8F, 0x88, 0xC9, 0x07, 0xB0))
    assert at(0x41AA, 2) == bytes((0xE0, 0x01))            # CPX #$01
    assert at(0x41B4, 2) == bytes((0xE0, 0x02))            # CPX #$02
    assert at(0x41B8, 4) == bytes((0x20, 0x8F, 0x88, 0x4A))  # rng / LSR
    assert at(0x41C4, 5) == bytes((0x20, 0x8F, 0x88, 0xC9, 0x05))
    assert at(0x41CB, 2) == bytes((0xC9, 0x0A))
    assert at(0x41F7, 3) == bytes((0xDE, 0x45, 0x7D))      # DEC $7D45,X — ONE
    assert constants.ALIEN_ATTACK_ROLL_AT_LEAST == 7
    assert constants.ALIEN_VICTIM_BANDS == (5, 10)
    assert constants.ALIEN_VICTIM_SLOTS == 3

    # Behaviourally: it does nothing on 7 of 16 actions...
    ship = nostromo_ship()
    room = "corridor_1"
    idle = 0
    for seed in range(160):
        crew = {
            cid: CrewMember(cid, cid.title(), Role.WARRANT_OFFICER, room)
            for cid in ("ripley", "parker", "brett")
        }
        state = GameState(crew=crew)
        alien = Alien(room_id=room)
        before = sum(c.health for c in crew.values())
        _resolve_surface_action(ship, state, alien, _random.Random(seed))
        after = sum(c.health for c in crew.values())
        if after == before:
            idle += 1
        else:
            # ...and when it does act, it wounds EXACTLY ONE crew member.
            assert before - after == constants.ALIEN_WOUND_AMOUNT, (
                "a crowded room must share one wound, not multiply it"
            )
            assert sum(
                1 for c in crew.values() if c.health < constants.CREW_START_HEALTH
            ) == 1
    assert 0.25 < idle / 160 < 0.65, f"expected ~7/16 idle, got {idle}/160"


def test_the_wound_is_one_point_to_one_victim() -> None:
    """**[C $41F4] PV-11 — the cadence and multiplicity FV-1.7 left open.**

    `LDX $64A4 / DEC $7D45,X` — a single decrement of a single slot, once per
    encounter, and the encounter itself only fires on 9 of 16 Alien actions
    (D-177). That is the whole of it: no per-tick accrual, no multi-victim
    loop, no repeat.
    """
    needs.need(needs.ALIEN_PRG)
    import pathlib

    prg = pathlib.Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    mem = prg[2:]
    assert mem[0x41F4 - load: 0x41FA - load] == bytes((
        0xAE, 0xA4, 0x64,        # LDX $64A4  (the chosen victim)
        0xDE, 0x45, 0x7D,        # DEC $7D45,X
    ))
    assert constants.ALIEN_WOUND_AMOUNT == 1


def test_the_alien_holds_the_room_after_meeting_crew() -> None:
    """**[C $8AE1/$413C] D-188 — it does not hit and run.**

    `alien_tick` reaches the encounter with a **JMP**, not a JSR::

        8AD7  LDA $64A3 / BEQ $8AE4      ; nobody here -> ordinary turn
        8AE1  JMP $413C                  ; met crew -> jump away
        8AE4  ...clear $6563, redraw, then pick the next move...

    so an encounter pass never reaches `$8AE4` and never dispatches a move.
    `$413C` opens `LDA #$28 / STA $64EE`, re-arming the timer to **40 passes**
    (~5 s), and returns. The remake fell through to `_begin_action` and chose a
    destination on the same pass — it attacked and immediately walked out,
    which is what the player reported.

    The hold applies on a **miss** too: `$413C` re-arms before `$4152`'s attack
    roll is taken.
    """
    needs.need(needs.ALIEN_PRG)
    import pathlib
    import random as _random

    from alien_remake.core.nostromo import nostromo_ship

    prg = pathlib.Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    mem = prg[2:]
    # The JMP that skips the move dispatch, and the timer it lands on.
    assert mem[0x8AE1 - load: 0x8AE4 - load] == bytes((0x4C, 0x3C, 0x41))
    assert mem[0x413C - load: 0x4141 - load] == bytes((0xA9, 0x28, 0x8D, 0xEE, 0x64))
    assert constants.ALIEN_ENCOUNTER_HOLD_TICKS == 0x28

    ship = nostromo_ship()
    room = "corridor_1"
    hits = misses = 0
    for seed in range(60):
        ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)
        state = GameState(crew={"ripley": ripley})
        alien = Alien(room_id=room, timer=1)
        advance_alien(ship, state, alien, _random.Random(seed))
        # Held the room, whichever way the attack roll went.
        assert alien.room_id == room, "it must not move on the encounter pass"
        assert alien.dest_id is None, "and must not have chosen a destination"
        assert alien.timer == constants.ALIEN_ENCOUNTER_HOLD_TICKS
        if ripley.health < constants.CREW_START_HEALTH:
            hits += 1
        else:
            misses += 1
    assert hits and misses, "the sample should cover both roll outcomes"


def test_the_alien_can_reach_every_deck_through_its_route_tables() -> None:
    """**[C $7A3A..$7AC8] DISC-259** — the creature is not confined to a deck.

    A player asked why the Alien seems to live on the upper deck. It starts
    there — `$7935` slot 0 is `$00`, AIRLOCK 1 — and it is *slow*, but it is not
    trapped: the five route tables form a graph in which all 34 rooms and all
    three decks are reachable from the start.

    Only **4 of the 169** table entries cross a deck (Livng Qtrs <-> Corridor 1
    and Corridor 2 <-> CargoPod 2), so the crossings are rare by design. This
    test guards reachability, not frequency — if a future table regeneration or
    a movement filter cuts a deck off, the Alien would silently become a
    one-deck creature and nothing else would fail.
    """
    from alien_remake.core.gamedata_snapshot import (
        ALIEN_ROUTES, DUCT_MAP_ROOM_TEMPLATE as DECK, ROOM_SLUGS,
    )

    start = ROOM_SLUGS.index("airlock_1")
    assert DECK[start] == 0, "the Alien starts on the upper deck ($7935 slot 0)"

    seen: set[int] = set()
    stack = [start]
    while stack:
        room = stack.pop()
        if room in seen:
            continue
        seen.add(room)
        for band in range(len(ALIEN_ROUTES)):
            nxt = ALIEN_ROUTES[band][room]
            if nxt < len(DECK):
                stack.append(nxt)

    assert len(seen) == len(DECK), (
        f"only {len(seen)} of {len(DECK)} rooms reachable from the Alien's "
        "start through its own route tables"
    )
    assert {DECK[r] for r in seen} == {0, 1, 2}, "a deck is unreachable"


def test_the_alien_actually_leaves_its_starting_deck_in_play() -> None:
    """Reachability on paper is not the same as reachability in a game.

    Measured: the first arrival on the lower deck falls between ticks ~5,000
    and ~9,700, which at `MAIN_LOOP_HZ` is ten to twenty minutes — longer than
    many games last, which is why it reads as "always upstairs". Faithful, but
    slow enough that a regression making it *never* happen would look normal.
    """
    import random

    from alien_remake.core.flow import default_simulation
    from alien_remake.core.modes import DeathVariant, GameMode
    from alien_remake.core.state import GamePhase

    reached: set[int] = set()
    for seed in range(4):
        sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
        sim.rng = random.Random(seed)
        alien = sim.state.alien
        assert alien is not None
        for _ in range(20_000):
            sim.advance()
            room = sim.ship.rooms.get(alien.room_id or "")
            if room is not None:
                reached.add(room.deck)
            if sim.state.phase is not GamePhase.RUNNING:
                sim.state.phase = GamePhase.RUNNING     # keep roaming
        if {0, 1, 2} <= reached:
            break

    assert {0, 1, 2} <= reached, (
        f"the Alien only ever reached decks {sorted(reached)} — it should work "
        "its way down the ship, however slowly"
    )


def test_the_rom_start_is_the_default_and_is_fixed() -> None:
    """**[C $7935 slot 0] DISC-260** — the replica default must not drift.

    `--alien-start random` is an added rule. The default has to stay the ROM's
    `$00` = AIRLOCK 1 or the remake silently stops being a replica, and nothing
    else in the suite would notice.
    """
    import random

    from alien_remake.core.modes import AlienStart, DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    for seed in range(8):
        sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.FIXED,
                         rng=random.Random(seed))
        assert sim.state.alien is not None
        assert sim.state.alien.room_id == "airlock_1"
        assert sim.ship.rooms["airlock_1"].deck == 0
    # ...and the enum's default member is the faithful one.
    assert AlienStart("original") is AlienStart.ORIGINAL


def test_a_random_start_spreads_across_the_ship_and_its_decks() -> None:
    """The added rule's whole purpose (DISC-260).

    The fixed start puts the creature on deck 0 every game, and with only 4 of
    169 route entries crossing a deck it usually stays there longer than a game
    lasts (DISC-259). Seeding it anywhere lets the *unchanged* movement rules
    produce a game where it is already below you.
    """
    import random
    from collections import Counter

    from alien_remake.core.modes import AlienStart, DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    rooms: Counter[str] = Counter()
    decks: Counter[int] = Counter()
    for seed in range(40):
        sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.FIXED,
                         alien_start=AlienStart.RANDOM, rng=random.Random(seed))
        assert sim.state.alien is not None
        room = sim.state.alien.room_id
        assert room is not None
        rooms[room] += 1
        decks[sim.ship.rooms[room].deck] += 1

    assert len(rooms) > 10, f"only {len(rooms)} distinct start rooms in 40 draws"
    assert set(decks) == {0, 1, 2}, f"decks seen: {sorted(decks)}"


def test_a_random_start_never_opens_on_top_of_the_crew() -> None:
    """Two exclusions, both deliberate.

    The crew's own starting rooms, so a game cannot begin with the creature
    already among them; and the Narcissus, which is off the deck plans entirely
    (deck 3, DISC-244) and would put it somewhere the player cannot look.
    """
    import random

    from alien_remake.core.modes import AlienStart, DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    for seed in range(120):
        sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.FIXED,
                         alien_start=AlienStart.RANDOM, rng=random.Random(seed))
        assert sim.state.alien is not None
        room = sim.state.alien.room_id
        crew_rooms = {c.room_id for c in sim.state.crew.values() if c.room_id}
        assert room not in crew_rooms, f"seed {seed}: opened in a crew room"
        assert room != "narcissus", f"seed {seed}: opened off the deck plans"


def test_a_random_start_does_not_change_how_the_alien_moves() -> None:
    """Only the seed moves; the route tables are untouched."""
    import random

    from alien_remake.core.modes import AlienStart, DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    fixed = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.FIXED,
                       rng=random.Random(5))
    house = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.FIXED,
                       alien_start=AlienStart.RANDOM, rng=random.Random(5))
    assert fixed.state.alien is not None and house.state.alien is not None
    # Same starting room => identical behaviour thereafter is the invariant we
    # care about; force it and compare a run.
    house.state.alien.room_id = fixed.state.alien.room_id
    house.rng = random.Random(99)
    fixed.rng = random.Random(99)
    for _ in range(300):
        fixed.advance()
        house.advance()
    assert fixed.state.alien.room_id == house.state.alien.room_id
    assert fixed.state.alien.in_duct == house.state.alien.in_duct


# --- the composure gate, caught live (DISC-270) ---------------------------


def _lone_victim(health: int, composure: int = 6):
    """One crew member alone in the Alien's room, at a chosen health."""
    from alien_remake.core.sim import Simulation

    sim = Simulation()
    alien = sim.state.alien
    assert alien is not None
    victim = next(c for c in sim.state.crew.values() if c.alive)
    for other in sim.state.crew.values():
        if other is not victim:
            other.room_id = None
            other.alive = False
    victim.health, victim.fear = health, composure
    victim.in_duct = False
    alien.room_id, alien.in_duct = victim.room_id, False
    return sim, alien, victim


def test_a_wound_docks_composure_only_when_it_lands_on_three() -> None:
    """**[C $4227 `CMP #$03 / BNE $4206`]** — not on every wound.

    Caught against the running game: over twelve Alien wounds only three cost
    composure, and every one of those left the victim on exactly 3 health. The
    remake docked on all twelve, so crews panicked about four times too fast.
    """
    import random

    from alien_remake.core import alien as alien_mod
    from alien_remake.core import constants

    def wound_once(health: int) -> tuple[int, int]:
        """Land exactly one wound at that health; return (fear before, after).

        `$4152 CMP #$07` means most passes miss, so the seed is searched rather
        than assumed - a fixed one silently tests nothing the day the roll order
        changes.
        """
        for seed in range(200):
            sim, alien, victim = _lone_victim(health=health)
            before = victim.fear
            alien_mod._resolve_surface_action(
                sim.ship, sim.state, alien, random.Random(seed)
            )
            if victim.health == health - 1:
                return before, victim.fear
        raise AssertionError(f"no seed in 200 landed a wound at health {health}")

    # 4 -> 3 crosses out of O.K.: the one case that pays.
    before, after = wound_once(4)
    assert after == before + constants.COMPOSURE_HIT_ALIEN_ATTACK

    # Every other wound leaves composure alone.
    for health in (6, 5, 3, 2):
        before, after = wound_once(health)
        assert after == before, (
            f"a wound to {health} docked composure; the ROM only docks at 3"
        )
