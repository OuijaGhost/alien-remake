"""Tests for the item catalog, pick-up/hand-off, and the Command Monitor.

From the disassembly: the catalog and every instance's starting room now come from
ALIEN.prg's own item tables — real names (the manual's "taser" is the game's
LASER PISTOL), fixed placement (the three lasers in the ARMOURY), no RNG.
Order *validation* (an item must actually be in the crew's room, and not
already held) is exercised through the Simulation, matching the pattern in
test_remake_crew.py.
"""

from __future__ import annotations

from alien_remake.core.alien import Alien
from alien_remake.core.command_monitor import damage_report, items_in_room
from alien_remake.core.crew import CrewMember, Role
from alien_remake.core.items import ITEM_CATALOG, ItemInstance, spawn_items
from alien_remake.core.map import Junction, Room, ShipMap
from alien_remake.core.orders import Order, OrderOutcome, OrderType
from alien_remake.core.sim import Simulation
from alien_remake.core.state import GameState

import needs                                       # noqa: E402


def _line_ship() -> ShipMap:
    m = ShipMap()
    for i, rid in enumerate("ABCD"):
        m.add_room(Room(rid, 0, rid, i, 0))
    m.add_door("A", "B")
    m.add_door("B", "C")
    m.add_door("C", "D")
    return m


def _sim_with_crew_at(room: str, ship: ShipMap) -> Simulation:
    # alien=Alien(room_id=None) keeps these item-validation tests Alien-free
    # (added Alien proximity/combat, out of scope here).
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)},
        alien=Alien(room_id=None),
    )
    return Simulation(state=state, ship=ship)


# --- catalog + spawn ------------------------------------------------------------

def test_catalog_is_the_games_own() -> None:
    # Real type ids/names/counts from the item tables ($82CF/$7C7D). The
    # manual's counts were right; its "taser" is the game's LASER PISTOL,
    # and THERMLANCE exists as a type with no spawned instance.
    counts = {t.id: t.count for t in ITEM_CATALOG}
    assert counts == {
        "elctrc_prd": 3,
        "incineratr": 3,
        "tracker": 2,
        "fire_extng": 4,
        "harpn_gun": 1,
        "laser_pist": 3,
        "net": 1,
        "cat_box": 1,
        "spanner": 2,
        "thermlance": 0,
    }
    assert sum(counts.values()) == 20
    names = {t.id: t.name for t in ITEM_CATALOG}
    assert names["laser_pist"] == "Laser Pist"
    assert names["elctrc_prd"] == "Elctrc Prd"


def test_spawn_items_uses_the_real_fixed_placement() -> None:
    from alien_remake.core.nostromo import nostromo_ship

    items = spawn_items(nostromo_ship())
    assert len(items) == 20
    # The clincher adjacency from the tables: all three laser pistols start
    # in the ARMOURY.
    lasers = [i for i in items.values() if i.type_id == "laser_pist"]
    assert [i.room_id for i in lasers] == ["armoury", "armoury", "armoury"]
    # And the cat box starts in the INFIRMARY.
    # **D-123:** the item table `$82E3` stores room *ids*, which did not
    # change — but the NAME of room 23 did. The cat box has always been
    # in room 23; a flat read of `$A71C` called that "Infirmary", and
    # honouring the table's 2-record gap makes it **LABORATORY**.
    assert items["cat_box_1"].room_id == "laboratory"
    assert all(i.holder is None for i in items.values())


def test_spawn_items_is_deterministic() -> None:
    from alien_remake.core.nostromo import nostromo_ship

    ship = nostromo_ship()
    a = spawn_items(ship)
    b = spawn_items(ship)
    assert {k: v.room_id for k, v in a.items()} == {k: v.room_id for k, v in b.items()}


def test_spawn_items_with_no_rooms_leaves_items_unplaced() -> None:
    items = spawn_items(ShipMap())
    assert len(items) == 20
    assert all(item.room_id is None for item in items.values())


def test_simulation_populates_items_when_state_has_none() -> None:
    sim = Simulation()
    assert len(sim.state.items) == 20


# --- GET_ITEM / LEAVE_ITEM validation via the sim --------------------------------

def test_get_item_picks_up_an_item_in_the_crews_room() -> None:
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.state.items = {"laser_pist_1": ItemInstance("laser_pist_1", "laser_pist", room_id="A")}
    sim.queue_order(Order("ripley", OrderType.GET_ITEM, "laser_pist_1"))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.COMPLETED
    assert sim.state.crew["ripley"].holding == "laser_pist_1"
    item = sim.state.items["laser_pist_1"]
    assert item.room_id is None and item.holder == "ripley"


def test_get_item_blocked_when_item_is_in_a_different_room() -> None:
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.state.items = {"laser_pist_1": ItemInstance("laser_pist_1", "laser_pist", room_id="B")}
    sim.queue_order(Order("ripley", OrderType.GET_ITEM, "laser_pist_1"))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.state.crew["ripley"].holding is None


def test_get_item_blocked_when_already_held_by_someone_else() -> None:
    ship = _line_ship()
    state = GameState(
        crew={
            "ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A"),
            "parker": CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, "A"),
        },
        items={"laser_pist_1": ItemInstance("laser_pist_1", "laser_pist", room_id=None, holder="parker")},
        alien=Alien(room_id=None),
    )
    sim = Simulation(state=state, ship=ship)
    sim.queue_order(Order("ripley", OrderType.GET_ITEM, "laser_pist_1"))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED
    assert sim.state.crew["ripley"].holding is None


def test_get_item_unknown_id_is_blocked() -> None:
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.state.items = {}
    sim.queue_order(Order("ripley", OrderType.GET_ITEM, "nope"))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED


def test_leave_item_with_nothing_held_is_blocked() -> None:
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.queue_order(Order("ripley", OrderType.LEAVE_ITEM))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED


def test_leave_item_drops_it_in_the_crews_current_room() -> None:
    ship = _line_ship()
    sim = _sim_with_crew_at("A", ship)
    sim.state.items = {"laser_pist_1": ItemInstance("laser_pist_1", "laser_pist", room_id=None, holder="ripley")}
    sim.state.crew["ripley"].holding = "laser_pist_1"
    sim.queue_order(Order("ripley", OrderType.LEAVE_ITEM))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.COMPLETED
    item = sim.state.items["laser_pist_1"]
    assert item.room_id == "A" and item.holder is None


# --- Command Monitor: Damage Reports + Weapons & Tools ---------------------------

def _grille_ship() -> ShipMap:
    m = ShipMap()
    m.add_room(Room("A", 0, "Bridge", 0, 0))
    m.add_room(Room("B", 0, "Galley", 1, 0))
    m.add_junction(Junction("jA", 0, 0, 0))
    m.add_grille("A", "jA")
    m.add_door("A", "B")
    return m


def test_damage_report_lists_grille_state_occupants_and_items() -> None:
    ship = _grille_ship()
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")},
        items={"laser_pist_1": ItemInstance("laser_pist_1", "laser_pist", room_id="A")},
    )
    reports = {r.room_id: r for r in damage_report(ship, state, deck=0)}
    assert reports["A"].grille_open is False
    assert reports["A"].occupant_names == ("Ripley",)
    assert reports["A"].item_ids == ("laser_pist_1",)
    assert reports["B"].occupant_names == ()
    assert reports["B"].item_ids == ()

    ship.open_grille("A", "jA")
    reports = {r.room_id: r for r in damage_report(ship, state, deck=0)}
    assert reports["A"].grille_open is True


def test_damage_report_excludes_dead_crew() -> None:
    ship = _grille_ship()
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A", alive=False)}
    )
    reports = {r.room_id: r for r in damage_report(ship, state, deck=0)}
    assert reports["A"].occupant_names == ()


def test_items_in_room_filters_and_sorts_by_id() -> None:
    state = GameState(
        items={
            "laser_pist_2": ItemInstance("laser_pist_2", "laser_pist", room_id="A"),
            "laser_pist_1": ItemInstance("laser_pist_1", "laser_pist", room_id="A"),
            "net_1": ItemInstance("net_1", "net", room_id="B"),
        }
    )
    assert [i.id for i in items_in_room(state, "A")] == ["laser_pist_1", "laser_pist_2"]
    assert items_in_room(state, "B")[0].id == "net_1"
    assert items_in_room(state, "C") == []


# --- R-17: per-item USE effects ---------------------------------------------------

def _use_sim(item_type: str, *, alien_room: str | None = "A", uses: int | None = None):
    """A crew member in room A holding one item, Alien staged in ``alien_room``.

    Seeds the RNG so the Alien's own (unrelated) behaviour can't make the USE
    outcome flaky.
    """
    import random

    from alien_remake.core import constants
    held = ItemInstance("it_1", item_type, room_id=None, holder="ripley", uses_left=uses)
    state = GameState(
        crew={"ripley": CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A",
                                   holding_init="it_1")},
        items={"it_1": held},
        alien=Alien(room_id=alien_room),
    )
    return Simulation(state=state, ship=_line_ship(), rng=random.Random(1234)), held, constants


def test_use_weapon_wounds_the_alien() -> None:
    import random
    sim, _held, _c = _use_sim("harpn_gun")
    sim.rng = random.Random(0)
    before = sim.state.alien.damage  # type: ignore[union-attr]
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    # A landed hit raises the Alien's wound counter (may miss on some seeds, so
    # try a few deterministic seeds until one lands).
    for seed in range(10):
        if sim.state.alien.damage > before:  # type: ignore[union-attr]
            break
        sim.rng = random.Random(seed)
        sim.queue_order(Order("ripley", OrderType.USE))
        sim.advance()
    assert sim.state.alien.damage > before  # type: ignore[union-attr]


def test_use_non_lethal_item_is_a_harmless_swing() -> None:
    # 1:1 fidelity: the net's real effect is unconfirmed by the disassembly, so
    # USE is a plain ATTACK swing that never wounds (no invented "stun").
    sim, _held, _c = _use_sim("net")
    before = sim.state.alien.damage  # type: ignore[union-attr]
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.state.alien.damage == before  # type: ignore[union-attr]
    assert sim.state.alien.alive  # type: ignore[union-attr]


def test_use_tracker_raises_an_ambiguous_alarm_and_is_not_charge_based() -> None:
    """FV-1.5: the tracker is NOT charge-based; D-041: the alarm names neither
    a room nor an entity. **D-150:** the range is the holder's room plus its
    direct neighbours, so the target has to actually be in range.
    """
    # Alien in "B" -- adjacent to Ripley's "A" on the line ship.
    sim, held, _c = _use_sim("tracker", alien_room="B")
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.state.tracker_alarm is True
    assert not hasattr(sim.state, "alien_reading_room")  # invention removed
    assert held.uses_left is None                        # not consumed
    # Still usable, repeatedly.
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.state.tracker_alarm is True


def test_tracker_alarm_is_silent_when_nothing_else_is_moving() -> None:
    # D-041: with no Alien, no Jones, and no other crew anywhere, there is
    # nothing to detect — the alarm must stay quiet rather than always firing.
    # The fixture has exactly one crew member (Ripley, the tracker user), so
    # clearing the Alien and Jones leaves genuinely nothing else moving.
    sim, _held, _c = _use_sim("tracker", alien_room=None)
    sim.state.jones_room_id = None
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.state.tracker_alarm is False


def test_use_extinguisher_silences_the_alarm_but_never_repairs() -> None:
    # D-044 [C $5889/$58CA]: the real FIGHT FIRE handler clears the `$651C`
    # alarm latch and NOTHING else — it never touches `$653F`, so structural
    # damage is permanent. The old "room_damage -= EXTINGUISHER_REPAIR" was an
    # invented repair mechanic and the constant is deleted.
    from alien_remake.core import constants

    assert not hasattr(constants, "EXTINGUISHER_REPAIR")  # invention removed
    sim, held, _c = _use_sim("fire_extng", alien_room=None, uses=4)
    sim.state.room_damage["A"] = 10
    sim.state.room_alarm["A"] = 1          # an alarm is sounding
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.state.room_alarm["A"] == 0  # silenced
    assert sim.state.room_damage["A"] == 10  # damage UNCHANGED - never repaired
    assert held.uses_left == 3


def test_room_alarm_returns_on_the_next_damage_tick() -> None:
    # D-044: `damage_room_b ($5587)` re-raises `$651C` whenever it reads 0 and
    # the raw damage is still >= 4 (which it always is, since damage only
    # grows) — so silencing a fire is recurring maintenance, not a fix.
    from alien_remake.core.alien import add_room_damage

    sim, _held, _c = _use_sim("fire_extng", alien_room=None, uses=4)
    sim.state.room_damage["A"] = 10
    sim.state.room_alarm["A"] = 0          # just silenced
    add_room_damage(sim.state, "A", 1)     # any further damage
    assert sim.state.room_alarm["A"] == 1  # alarm is back


def test_exhausted_consumable_cannot_be_used() -> None:
    # FV-1.5: exercise exhaustion with a REAL charge-based item — the fire
    # extinguisher ($4B37=3) — not the (uncharged) tracker. No Alien in play.
    sim, held, _c = _use_sim("fire_extng", alien_room=None, uses=1)
    sim.state.room_damage["A"] = 10
    sim.state.room_alarm["A"] = 1    # D-044: an alarm must be sounding to fight
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()  # fights the fire, spends the last charge
    assert held.exhausted
    sim.state.room_alarm["A"] = 1    # alarm returns, but the extinguisher is spent
    sim.queue_order(Order("ripley", OrderType.USE))
    sim.advance()
    assert sim.last_outcomes[0][1] is OrderOutcome.BLOCKED


# --- display model: structural damage + crew status (UI surfacing) ----------------

def test_damage_report_surfaces_structural_damage_and_stage() -> None:
    from alien_remake.core import constants
    from alien_remake.core.command_monitor import damage_report
    ship = _line_ship()
    # P2-19: the three bands are the ROM's own (`damage_room_b $5587`) —
    # below 4 nothing is raised at all, 4..14 is stage 1, 15+ is stage 2.
    state = GameState(room_damage={"A": constants.DAMAGE_STAGE_SEVERE_FROM,
                                   "B": 3, "D": 8})
    reports = {r.room_id: r for r in damage_report(ship, state, deck=0)}
    assert reports["A"].damage_stage == 2       # severe ($5594 CMP #$0F)
    assert reports["B"].damage_stage == 0       # [C $558F] below 4: no alarm
    assert reports["C"].damage_stage == 0       # intact
    assert reports["A"].damage == constants.DAMAGE_STAGE_SEVERE_FROM


def test_structural_warnings_lists_damaged_rooms_worst_first() -> None:
    from alien_remake.core.command_monitor import structural_warnings
    ship = _line_ship()
    state = GameState(room_damage={"A": 4, "C": 12, "B": 0})
    warned = structural_warnings(ship, state)
    assert [r.room_id for r in warned] == ["C", "A"]  # worst first; B intact omitted


def test_crew_status_reports_status_and_morale() -> None:
    from alien_remake.core.command_monitor import crew_status
    hurt = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    hurt.wound()
    state = GameState(crew={"ripley": hurt})
    line = crew_status(state)[0]
    assert line.name == "Ripley" and line.status == "wounded"
    assert line.morale in ("confident", "stable", "uneasy", "shaken", "broken")


# --- FV-1.1 provenance drift-guards: item charges are the DECODED $4B47 values ---


def test_consumable_charges_match_decoded_table() -> None:
    """FV-1.1 [C $4B47]: charges are decoded, not the old 5/4/8 guess.

    `new_game ($65B1)` copies the master charge table `$4B47` -> the working copy
    `$4B37` for the 20 item instances. The per-type values are: FIRE EXTNG = 3,
    HARPN GUN = 1 (one shot), LASER PIST = 10. See docs/re/FAITHFULNESS.md and
    DISASSEMBLY.md §8.8. This pins the correction so it cannot silently regress
    (the invented 5/4/8 were unpinned — no test failed when they were wrong).
    """
    from alien_remake.core import constants

    assert constants.CONSUMABLE_USES == {
        "fire_extng": 3,
        "harpn_gun": 1,
        "laser_pist": 10,
    }
    # The TRACKER is destroy-on-use ("TRACKER IS SMASHED" $4B22), NOT charge-based;
    # it must not carry a phantom charge count (the old guess gave it 8).
    assert "tracker" not in constants.CONSUMABLE_USES


def test_attack_damage_is_deterministic_per_item() -> None:
    """FV-1.1 [C $4940]: combat is a switch on item id, not an RNG hit-roll.

    The harpoon does +5 in one guaranteed shot; prod/incinerator/spanner/laser/
    tracker do +1 (D-033: the tracker's "smashed" path does land a wound);
    extinguisher/cat box wound for 0; the net wounds for 0 too but has its own
    entangle effect (see `ALIEN_NET_ENTANGLE_TICKS`). Guards the
    ITEM_ATTACK_DAMAGE table decoded from resolve_attack ($4940).
    """
    from alien_remake.core import constants

    dmg = constants.ITEM_ATTACK_DAMAGE
    assert dmg["harpn_gun"] == 5          # $49F6 ADC #$05, guaranteed
    assert dmg["elctrc_prd"] == dmg["laser_pist"] == dmg["tracker"] == 1
    assert dmg["net"] == dmg["fire_extng"] == dmg["cat_box"] == 0


# --- P2-16: two hands, and the newest item comes off first --------------------

def test_a_crew_member_carries_exactly_two_items() -> None:
    """**[C $8332/$83AF/$83C6]** `scan_room_objects` clears exactly two carry
    slots to `$FF`, and `list_room_items` refills them from the two holder
    encodings — `char + $A0` -> `$829A` (panel row 9) and `char + $80` ->
    `$829B` (row 10). Two slots, two rows, two items."""
    import random

    from alien_remake.core.crew import CARRY_CAPACITY
    from alien_remake.core.orders import Order, OrderType
    from alien_remake.core.sim import Simulation

    assert CARRY_CAPACITY == 2
    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    here = [i for i in sim.state.items.values() if i.room_id == crew.room_id][:3]
    assert len(here) >= 3, "need three items in one room for this test"

    assert sim._apply_order(
        Order(crew.id, OrderType.GET_ITEM, here[0].id)
    ) is OrderOutcome.COMPLETED
    assert sim._apply_order(
        Order(crew.id, OrderType.GET_ITEM, here[1].id)
    ) is OrderOutcome.COMPLETED
    # Hands full.
    assert sim._apply_order(
        Order(crew.id, OrderType.GET_ITEM, here[2].id)
    ) is OrderOutcome.BLOCKED
    assert len(crew.carried) == CARRY_CAPACITY
    assert here[2].room_id == crew.room_id, "the refused item stays put"


def test_leaving_an_item_drops_the_most_recent_first() -> None:
    """**[C $8512] LIFO.** `LDY $829B / CPY #$FF / BEQ $8527` tries one slot
    first and only falls back to the other when it is empty, so the two items
    do not come off in pickup order. Play settles which way round: pick up the
    incinerator then the tracker, and the **tracker** is put down first."""
    import random

    from alien_remake.core.orders import Order, OrderType
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    room = crew.room_id
    first, second = [
        i for i in sim.state.items.values() if i.room_id == room
    ][:2]
    sim._apply_order(Order(crew.id, OrderType.GET_ITEM, first.id))
    sim._apply_order(Order(crew.id, OrderType.GET_ITEM, second.id))

    assert sim._apply_order(
        Order(crew.id, OrderType.LEAVE_ITEM)
    ) is OrderOutcome.COMPLETED
    assert second.holder is None and second.room_id == room  # newest, dropped
    assert first.holder == crew.id                            # older, kept
    assert crew.carried == [first.id]
    # `holding` — the one-item view the rest of the code uses — follows suit.
    assert crew.holding == first.id


def test_holding_is_the_most_recent_pickup() -> None:
    from alien_remake.core.crew import CrewMember, Role

    c = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, "A")
    assert c.holding is None
    c.carried.extend(["a", "b"])
    assert c.holding == "b"
    c.holding = None
    assert c.carried == []


def test_the_tracker_alarm_is_recomputed_and_needs_the_tracker_held() -> None:
    """**[C $72F9/$72FC] D-150 — the alarm is a latch RECOMPUTED each pass.**

    `reset_attack_state` clears `$64B6` and `check_6562` re-arms it, back to
    back, on every move pass — so it is armed only while a tracker is
    genuinely *held* and something is in range. The player reported it kept
    tracking after the crew member put the tracker down; that was this
    recomputation missing.
    """
    sim, held, _c = _use_sim("tracker", alien_room="B")
    sim.advance()
    assert sim.state.tracker_alarm is True, "held + something adjacent -> armed"

    # Put it down: the item is now in a room, not carried.
    crew = sim.state.crew["ripley"]
    crew.holding = None
    held.holder = None
    held.room_id = crew.room_id
    sim.advance()
    assert sim.state.tracker_alarm is False, "a dropped tracker must go silent"

    # Pick it up again -> it re-arms.
    held.room_id = None
    held.holder = crew.id
    crew.holding = held.id
    sim.advance()
    assert sim.state.tracker_alarm is True


def test_the_tracker_zone_is_neighbours_plus_same_room_ducts() -> None:
    """**[C $8F0B/$8F1B] D-150 — the two rules inside the zone.**

    A neighbouring room reads a character on the SURFACE; the holder's own
    room reads only a character inside a DUCT (you can already see anyone
    standing beside you). Jones is checked over the neighbours alone.
    """
    sim, _held, _c = _use_sim("tracker", alien_room=None)
    sim.state.jones_caught = True
    ripley = sim.state.crew["ripley"]          # in "A"; neighbour is "B"

    from alien_remake.core.crew import CrewMember, Role
    mate = CrewMember("parker", "Parker", Role.CHIEF_ENGINEER, "B")
    sim.state.crew["parker"] = mate

    # Adjacent, on the surface -> detected.
    sim._scan_trackers()
    assert sim.state.tracker_alarm is True

    # Adjacent but inside a duct -> NOT detected ($8F3E requires surface).
    mate.in_duct = True
    sim._scan_trackers()
    assert sim.state.tracker_alarm is False

    # Same room as the holder, on the surface -> NOT detected (you see them).
    mate.in_duct = False
    mate.room_id = "A"
    sim._scan_trackers()
    assert sim.state.tracker_alarm is False

    # Same room but in a duct -> detected ($8F31).
    mate.in_duct = True
    sim._scan_trackers()
    assert sim.state.tracker_alarm is True

    # Jones alone, in a neighbouring room -> detected.
    sim.state.crew.pop("parker")
    sim.state.jones_caught = False
    sim.state.jones_room_id = "B"
    sim._scan_trackers()
    assert sim.state.tracker_alarm is True


def test_tracker_arms_passively_without_a_use_order() -> None:
    """**[C $72FC/$8E32] P6-4 — the tracker needs no USE order at all.**

    `check_deferred_move` calls `check_6562` unconditionally right after the
    movement blip (`$72F9 reset_attack_state` / `$72FC check_6562`), gated
    only on `$6517` — the flag `char_pump` sets whenever ANY character's move
    resolves. There is no `$64BB`/USE-order gate on that call. So merely
    *holding* a tracker should arm the alarm the instant anyone else finishes
    moving — the player should never have to issue an explicit USE order.
    """
    import random

    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    holder = next(c for c in sim.state.crew.values() if c.alive)
    tracker = ItemInstance("auto_trk", "tracker", room_id=None, holder=holder.id)
    sim.state.items["auto_trk"] = tracker
    holder.holding = "auto_trk"

    mover = next(
        c
        for c in sim.state.crew.values()
        if c.alive and c.id != holder.id and c.room_id is not None
    )
    dest = sim.ship.door_neighbors(mover.room_id)[0]
    from alien_remake.core.orders import Order, OrderType

    sim.queue_order(Order(mover.id, OrderType.MOVE_TO, dest))

    sim.state.tracker_alarm = False
    detected_on_arrival = False
    for _ in range(400):
        before = mover.room_id
        sim.advance()
        if mover.room_id != before:  # the move just completed this tick
            detected_on_arrival = sim.state.tracker_alarm
            break
    assert detected_on_arrival, (
        "carrying a tracker should detect an unrelated crew member's "
        "completed move without an explicit USE order"
    )


def test_picking_up_a_weapon_steadies_you_and_dropping_it_does_not() -> None:
    """**[C $45E7/$45D3] PV-39 / D-181 — the manual's confidence rule, decoded.**

    `scripted_event_check ($45E7)` fires on the *transition*: event code 2 when
    the held item changes, 3 when it is lost. It indexes `$45D3` by the item
    and INCs `$7D55` once (`$4665`) or twice (`$466B` jumping back to `$4662`),
    mirrored by `$4622`/`$4639` on the way down. The ranking is by weapon
    quality — which is the decoded form of *"confidence will increase by the
    possession of a useful piece of equipment"*.
    """
    needs.need(needs.ALIEN_PRG)
    import pathlib
    import random

    from alien_remake.core import constants
    from alien_remake.core.orders import Order, OrderType
    from alien_remake.core.sim import Simulation

    # The table itself, read from the PRG rather than transcribed.
    prg = pathlib.Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    table = list(prg[2:][0x45D3 - load: 0x45D3 - load + 20])
    assert table == [0, 0, 0, 1, 1, 1, 0xFF, 0xFF, 0, 0,
                     0, 0, 1, 1, 1, 1, 0xFF, 0xFF, 0, 0]
    # $FF is exempt; 0 is +/-1; 1 is +/-2.
    assert constants.ITEM_COMPOSURE["elctrc_prd"] == 1     # effect 0
    assert constants.ITEM_COMPOSURE["laser_pist"] == 2     # effect 1
    for exempt in ("tracker", "net", "cat_box"):
        assert exempt not in constants.ITEM_COMPOSURE

    def staged(type_id: str):
        sim = Simulation(rng=random.Random(0))
        crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
        crew.carried.clear()
        crew.fear = 4
        for it in list(sim.state.items.values()):
            it.holder = None
            it.room_id = None
        item = next(i for i in sim.state.items.values() if i.type_id == type_id)
        item.room_id = crew.room_id
        return sim, crew, item

    for type_id, expected in (
        ("laser_pist", 2), ("elctrc_prd", 1), ("tracker", 0),
    ):
        sim, crew, item = staged(type_id)
        before = crew.fear
        sim._apply_order(Order(crew.id, OrderType.GET_ITEM, item.id))
        assert crew.fear - before == expected, f"{type_id} on pickup"
        # ...and putting it down costs exactly the same again.
        held = crew.fear
        sim._apply_order(Order(crew.id, OrderType.LEAVE_ITEM))
        assert held - crew.fear == expected, f"{type_id} on drop"
