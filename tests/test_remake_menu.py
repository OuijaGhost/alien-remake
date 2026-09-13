"""Tests for the CONTROL-panel menu model + controller (headless, no pygame)."""

from __future__ import annotations

from alien_remake.core.menu import (
    MenuCategory,
    MenuController,
    control_entries,
    crew_entries,
)
from alien_remake.core.orders import OrderOutcome, OrderType
from alien_remake.core.modes import JonesCatch
from alien_remake.core.sim import Simulation
from alien_remake.core.special_options import SpecialOptionType


def _sim(**kwargs: object) -> Simulation:
    return Simulation(**kwargs)  # type: ignore[arg-type]  # real ship, crew, items


def test_control_list_has_all_seven_crew_and_decks() -> None:
    # R-37/D-042 [C $7720]: the real "Order:" list shows **all seven** crew
    # names, including the opening death — live-confirmed on two independent
    # boots. The remake used to filter dead crew out (only 6 shown); that was
    # the bug. Picking a dead one is a no-op (see the bounce test below).
    sim = _sim()
    entries = control_entries(sim)
    crew_names = [e.label for e in entries if e.category is MenuCategory.CREW]
    assert len(crew_names) == 7
    assert any(not c.alive for c in sim.state.crew.values())  # one really is dead
    assert all(e.select_crew for e in entries if e.category is MenuCategory.CREW)
    decks = [e for e in entries if e.category is MenuCategory.DECK]
    assert len(decks) == len(sim.ship.decks())


def test_selecting_a_dead_crew_member_bounces_back_to_the_control_list() -> None:
    # R-37/D-042 [C $7720]: `guard_alien_present` shows the picked character's
    # status then CLEARS the selection (`STA $64FB` = 0) when they are
    # incapacitated/dead (`$7D45,Y < 2`) or asleep — no order menu opens.
    sim = _sim()
    dead_id = next(c.id for c in sim.state.crew.values() if not c.alive)
    ctrl = MenuController(sim)
    entries = ctrl.entries()
    idx = next(i for i, e in enumerate(entries) if e.select_crew == dead_id)
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    ctrl.cursor = selectable.index(idx)
    ctrl.fire()
    # `$7720` bounces the SELECTION for a dead character (D-114); the cursor
    # stays put so the list can be walked past them.
    assert ctrl.selected_crew is None


def test_selecting_a_sleeping_crew_member_also_bounces() -> None:
    # Same $7720 gate, the asleep branch (`$64D1,Y != 0`).
    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive and c.awake)
    sim.state.crew[crew_id].awake = False
    ctrl = MenuController(sim)
    entries = ctrl.entries()
    idx = next(i for i, e in enumerate(entries) if e.select_crew == crew_id)
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    ctrl.cursor = selectable.index(idx)
    ctrl.fire()
    assert ctrl.selected_crew is None



def _select_living_crew(ctrl) -> str:
    """Point the cursor at a definitely-alive, awake crew member and fire.

    R-37/D-042: the CONTROL list now includes dead crew (as the original
    does), and the opening death is random — so "cursor 0" is no longer
    reliably a selectable-through crew member. Pick one explicitly.
    """
    crew_id = next(
        c.id for c in ctrl.sim.state.crew.values() if c.alive and c.awake
    )
    entries = ctrl.entries()
    idx = next(i for i, e in enumerate(entries) if e.select_crew == crew_id)
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    ctrl.cursor = selectable.index(idx)
    ctrl.fire()
    return crew_id


def test_selecting_a_crew_opens_their_order_menu() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    _select_living_crew(ctrl)
    assert ctrl.selected_crew is not None
    labels = [e.label for e in ctrl.entries()]
    assert "move to:" in labels
    assert "Special:" in labels
    # [C $A715] decoded as "quit"; shown as "back" (owner's request,
    # 2026-09-05) since it only ever steps back one level, never exits.
    assert "back" in labels


# --- "Skip turn" (2026-09-05), not the original -----------------------------

def test_skip_turn_row_is_absent_when_turns_is_off() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    _select_living_crew(ctrl)
    assert ctrl.turns_on is False
    labels = [e.label for e in ctrl.entries()]
    assert "Skip turn" not in labels


def test_skip_turn_row_sits_in_the_special_area_right_above_back() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    ctrl.turns_on = True
    _select_living_crew(ctrl)
    entries = ctrl.entries()
    labels = [e.label for e in entries]
    assert labels[-2:] == ["Skip turn", "back"], (
        "Skip turn should be the special-area row right above back, per the "
        "owner's own placement request"
    )
    skip_entry = entries[labels.index("Skip turn")]
    assert skip_entry.category is MenuCategory.SPECIAL
    assert skip_entry.selectable


def test_firing_skip_turn_sets_the_request_flag() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    ctrl.turns_on = True
    _select_living_crew(ctrl)
    entries = ctrl.entries()
    idx = next(i for i, e in enumerate(entries) if e.skip_turn)
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    ctrl.cursor = selectable.index(idx)
    ctrl.fire()
    assert ctrl.skip_turn_requested is True
    # Firing it must not itself deselect the crew member or exit the menu -
    # `app.py` (via the renderer's `select_crew` hook) owns moving on.
    assert ctrl.selected_crew is not None


def test_crew_menu_move_to_lists_only_direct_connections() -> None:
    # R-16 (full disassembly): MOVE TO offers the room's DIRECT connections only,
    # not every reachable room — so the targets equal the door-neighbours.
    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    entries = crew_entries(sim, crew.id)
    moves = [e for e in entries if e.category is MenuCategory.MOVE_TO]
    assert moves, "a placed crew member should have somewhere to move"
    assert all(e.order and e.order.type is OrderType.MOVE_TO for e in moves)
    targets = {e.order.target for e in moves if e.order}
    assert targets == set(sim.ship.door_neighbors(crew.room_id))


def test_firing_a_move_queues_the_order_and_stays_on_the_crew_member() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    _select_living_crew(ctrl)
    # Find the first MOVE_TO selectable and point the cursor at it.
    entries = ctrl.entries()
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    move_pos = next(
        k for k, i in enumerate(selectable)
        if entries[i].category is MenuCategory.MOVE_TO
    )
    ctrl.cursor = move_pos
    ctrl.fire()
    assert sim.pending_orders == 1          # the MOVE_TO was queued
    # **P4-4:** the panel now STAYS on the crew member after an order — the
    # ROM's order path never writes `$64FB` (only `reset_alien_turn $83FD`
    # does, and that is the Alien's turn), so several commands can be issued
    # in a row without re-selecting.
    assert ctrl.selected_crew is not None


def test_quit_entry_returns_to_control() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    _select_living_crew(ctrl)
    assert ctrl.selected_crew is not None
    # QUIT is the last selectable entry.
    ctrl.cursor = len(ctrl._selectable(ctrl.entries())) - 1
    ctrl.fire()
    assert ctrl.selected_crew is None


def test_selecting_a_crew_switches_to_their_deck() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    # Put the first crew member on a non-zero deck and select them.
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    target_room = next(r for r in sim.ship.rooms.values() if r.deck == 2)
    sim.state.crew[crew_id].room_id = target_room.id
    sim.state.deck = 0
    entries = ctrl.entries()
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    pos = next(k for k, i in enumerate(selectable) if entries[i].select_crew == crew_id)
    ctrl.cursor = pos
    ctrl.fire()
    assert ctrl.selected_crew == crew_id
    assert sim.state.deck == 2  # the map followed them to their deck


def test_specials_appear_only_in_the_rooms_that_carry_them() -> None:
    """**P2-1 — rewritten 2026-08-02; the old assertion pinned an invention.**

    It required "Launch" and "Scuttle" in the menu of an arbitrary room, i.e.
    it asserted that these are available everywhere. They are not:
    `guard_target_alive ($56B4)` indexes `$5753,Y` by the acting character's
    **room**, and the initial table (`$5776`) gives only four rooms an entry —
    COMMDCENTR (SCUTTLE/OVERRIDE), CORRIDOR 6 (the airlocks), CRYO VAULT
    (HYPERSLEEP) and SHUTTLEBAY (LAUNCH). A player reported seeing SCUTTLE and
    LAUNCH from anywhere, which is what this test had been protecting.
    """
    from alien_remake.core.menu import (
        SPECIAL_ROOM_AIRLOCKS,
        SPECIAL_ROOM_HYPERSLEEP,
        SPECIAL_ROOM_LAUNCH,
        SPECIAL_ROOM_SCUTTLE,
    )

    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    crew = sim.state.crew[crew_id]

    def labels_in(room: str) -> list[str]:
        crew.room_id = room
        return [e.label for e in crew_entries(sim, crew_id)]

    assert "Launch" in labels_in(SPECIAL_ROOM_LAUNCH)
    assert "Scuttle" in labels_in(SPECIAL_ROOM_SCUTTLE)
    assert "Enter" in labels_in(SPECIAL_ROOM_HYPERSLEEP)
    assert any(l.startswith("BlowLock") for l in labels_in(SPECIAL_ROOM_AIRLOCKS))

    # ...and an ordinary room offers none of them.
    ordinary = next(
        r for r in sim.ship.rooms
        if r not in {
            SPECIAL_ROOM_LAUNCH, SPECIAL_ROOM_SCUTTLE,
            SPECIAL_ROOM_HYPERSLEEP, SPECIAL_ROOM_AIRLOCKS,
        }
    )
    plain = labels_in(ordinary)
    for forbidden in ("Launch", "Scuttle", "Override", "Enter"):
        assert forbidden not in plain, f"{forbidden!r} offered in {ordinary}"
    assert not any(l.startswith(("BlowLock", "SealLock")) for l in plain)


def test_each_special_room_carries_the_id_the_rom_table_gives_it() -> None:
    """The four slugs must match `$5776`'s non-zero entries, by room id."""
    from alien_remake.core import gamedata_snapshot as data
    from alien_remake.core.menu import (
        SPECIAL_ROOM_AIRLOCKS,
        SPECIAL_ROOM_HYPERSLEEP,
        SPECIAL_ROOM_LAUNCH,
        SPECIAL_ROOM_SCUTTLE,
    )

    assert data.ROOM_SLUGS[6] == SPECIAL_ROOM_SCUTTLE
    assert data.ROOM_SLUGS[13] == SPECIAL_ROOM_AIRLOCKS
    assert data.ROOM_SLUGS[15] == SPECIAL_ROOM_HYPERSLEEP
    assert data.ROOM_SLUGS[34] == SPECIAL_ROOM_LAUNCH


def test_special_menu_shows_override_once_armed() -> None:
    # FV-2c [C-live]: SCUTTLE (arm) / OVERRIDE (cancel) are a real matched pair
    # confirmed live — firing SCUTTLE makes the menu show OVERRIDE instead.
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    before = [e.label for e in crew_entries(sim, crew_id)]
    assert "Scuttle" in before and "Override" not in before

    sim.apply_special_option(SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT))
    after = [e.label for e in crew_entries(sim, crew_id)]
    assert "Override" in after and "Scuttle" not in after


def test_special_menu_offers_both_airlocks_only_from_corridor_6() -> None:
    # D-037 (de-invention audit, 2026-07-24): the real BLOWLOCK/SEALLOCK
    # dispatch (specials category 2, D-032) is offered only while standing
    # in CORRIDOR 6, and targets BOTH airlocks as independent options
    # (`apply_blowlock $5B04` checks two separate per-airlock flags), not
    # gated on standing inside an airlock room.
    from alien_remake.core.special_options import SpecialOptionType

    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    sim.state.crew[crew_id].room_id = "corridor_6"
    entries = crew_entries(sim, crew_id)
    labels = [e.label for e in entries]
    assert "BlowLock.1" in labels and "BlowLock.2" in labels

    lock1 = next(e for e in entries if e.label == "BlowLock.1")
    assert lock1.special is not None
    assert lock1.special.type is SpecialOptionType.OPEN_AIRLOCK
    assert lock1.special.room_id == "airlock_1"

    lock2 = next(e for e in entries if e.label == "BlowLock.2")
    assert lock2.special is not None
    assert lock2.special.room_id == "airlock_2"


def test_special_menu_hides_airlock_controls_outside_corridor_6() -> None:
    # D-037: standing IN an airlock is NOT the real gate (that was the
    # invention) -- CORRIDOR 6 is.
    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    sim.state.crew[crew_id].room_id = "airlock_1"
    labels = [e.label for e in crew_entries(sim, crew_id)]
    assert "BlowLock.1" not in labels and "BlowLock.2" not in labels


def test_airlock_menu_label_flips_to_seallock_per_airlock_independently() -> None:
    # D-037: each airlock's open/sealed state is independent -- opening
    # airlock_1 should not affect airlock_2's label.
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    sim.state.crew[crew_id].room_id = "corridor_6"

    sim.apply_special_option(SpecialOption(SpecialOptionType.OPEN_AIRLOCK, room_id="airlock_1"))
    labels = [e.label for e in crew_entries(sim, crew_id)]
    assert "SealLock.1" in labels
    assert "BlowLock.2" in labels  # airlock_2 untouched


def test_special_menu_offers_enter_hypersleep_while_awake() -> None:
    # FV-1b5: ENTER HYPERSLEEP is a real decoded special (`$57A0`) whose handler
    # already worked but wasn't surfaced on the panel — now it is.
    # D-028: the real handler is room-gated to the CRYO VAULT.
    sim = _sim()
    # D-080: the android is refused hypersleep outright ($593C), so this test
    # must pick someone else or it is testing that rule instead of this one.
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.awake and c.id != sim.state.android_id
    )
    sim.state.crew[crew_id].room_id = "cryo_vault"
    entries = crew_entries(sim, crew_id)
    entry = next(e for e in entries if e.label == "Enter")
    assert entry.category is MenuCategory.SPECIAL
    assert entry.special is not None
    assert entry.special.type is SpecialOptionType.ENTER_HYPERSLEEP
    assert entry.special.crew_id == crew_id


def test_special_menu_hides_enter_hypersleep_outside_the_cryo_vault() -> None:
    # D-028: ENTER HYPERSLEEP only appears while standing in the CRYO VAULT.
    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive and c.awake)
    assert sim.state.crew[crew_id].room_id != "cryo_vault"
    labels = [e.label for e in crew_entries(sim, crew_id)]
    assert "Enter" not in labels


def test_special_menu_hides_enter_hypersleep_once_asleep() -> None:
    sim = _sim()
    # D-080: the android is refused hypersleep outright ($593C), so this test
    # must pick someone else or it is testing that rule instead of this one.
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.awake and c.id != sim.state.android_id
    )
    sim.state.crew[crew_id].room_id = "cryo_vault"
    sim.state.crew[crew_id].awake = False
    labels = [e.label for e in crew_entries(sim, crew_id)]
    assert "Enter" not in labels


def test_special_menu_offers_attack_when_sharing_a_room_with_the_alien() -> None:
    """**[C $8CE1-$8CEB, $064E] P5-4/D-132.** There was previously no menu
    path to `OrderType.ATTACK` at all, despite `resolve_attack` and
    `Simulation._resolve_attack_order` being fully implemented. The ROM
    writes "ATTACK" into `$064E` — the same buffer every other SPECIAL row
    is built from — as an encounter starts; this remake doesn't track that
    per-crew latch, so (matching the precedent already set for FIGHT FIRE)
    the option is shown exactly when firing it would succeed.
    """
    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    crew = sim.state.crew[crew_id]
    assert sim.state.alien is not None
    sim.state.alien.room_id = crew.room_id
    sim.state.alien.in_duct = False
    # **DISC-246.** `find_crew_with_alien ($8C49)` stops at its FIRST match, so
    # the Alien engages the lowest-numbered occupant and `$8CE1` offers ATTACK
    # to that one alone. Clear the room so the crew member under test is the one
    # it finds. `_sim()` is unseeded and the opening seating is random
    # (DISC-224), so without this the result depends on who happens to share the
    # room — the old superset offered the option to everyone present and hid it.
    for _other in sim.state.crew.values():
        if _other.id != crew_id and _other.room_id == crew.room_id:
            _other.room_id = None
    entries = crew_entries(sim, crew_id)
    entry = next(e for e in entries if e.label == "Attack")
    assert entry.category is MenuCategory.SPECIAL
    assert entry.order is not None
    assert entry.order.type is OrderType.ATTACK
    assert entry.order.crew_id == crew_id


def test_special_menu_hides_attack_when_the_alien_is_elsewhere_or_ducted() -> None:
    sim = _sim()
    crew_id = next(c.id for c in sim.state.crew.values() if c.alive)
    crew = sim.state.crew[crew_id]
    assert sim.state.alien is not None

    sim.state.alien.room_id = next(
        r for r in sim.ship.rooms if r != crew.room_id
    )
    assert "Attack" not in [e.label for e in crew_entries(sim, crew_id)]

    # **DISC-246** — `$8C56 CMP $6501` compares the two duct flags; it does not
    # ask whether the Alien is surfaced. An Alien in the vents ignores a crew
    # member standing in the room...
    sim.state.alien.room_id = crew.room_id
    sim.state.alien.in_duct = True
    crew.in_duct = False
    assert "Attack" not in [e.label for e in crew_entries(sim, crew_id)]

    # ...and finds one who is also in the vents.
    crew.in_duct = True
    for _other in sim.state.crew.values():
        if _other.id != crew_id and _other.room_id == crew.room_id:
            _other.room_id = None
    assert "Attack" in [e.label for e in crew_entries(sim, crew_id)]


def test_attack_menu_entry_actually_resolves() -> None:
    """The entry must not just appear — firing it must reach the real
    resolver and wound the Alien, closing the loop end to end."""
    sim = _sim()
    # D-080: the android silently drops orders while co-located with the
    # Alien ($5265) — pick someone else or this tests that rule instead.
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.id != sim.state.android_id
    )
    crew = sim.state.crew[crew_id]
    assert sim.state.alien is not None
    sim.state.alien.room_id = crew.room_id
    sim.state.alien.in_duct = False
    # **DISC-246.** `find_crew_with_alien ($8C49)` stops at its FIRST match, so
    # the Alien engages the lowest-numbered occupant and `$8CE1` offers ATTACK
    # to that one alone. Clear the room so the crew member under test is the one
    # it finds. `_sim()` is unseeded and the opening seating is random
    # (DISC-224), so without this the result depends on who happens to share the
    # room — the old superset offered the option to everyone present and hid it.
    for _other in sim.state.crew.values():
        if _other.id != crew_id and _other.room_id == crew.room_id:
            _other.room_id = None
    before = sim.state.alien.damage

    entries = crew_entries(sim, crew_id)
    entry = next(e for e in entries if e.label == "Attack")
    assert entry.order is not None
    outcome = sim._apply_order(entry.order)

    assert outcome is OrderOutcome.COMPLETED
    assert sim.state.alien.damage >= before


def test_firing_enter_hypersleep_puts_the_crew_member_to_sleep() -> None:
    sim = _sim()
    # D-080: the android is refused hypersleep outright ($593C), so this test
    # must pick someone else or it is testing that rule instead of this one.
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.awake and c.id != sim.state.android_id
    )
    sim.state.crew[crew_id].room_id = "cryo_vault"
    ctrl = MenuController(sim)
    ctrl.selected_crew = crew_id
    entries = ctrl.entries()
    idx = next(i for i, e in enumerate(entries) if e.label == "Enter")
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    ctrl.cursor = selectable.index(idx)
    ctrl.fire()
    assert sim.state.crew[crew_id].awake is False
    # **P4-4:** the panel now STAYS on the crew member after an order — the
    # ROM's order path never writes `$64FB` (only `reset_alien_turn $83FD`
    # does, and that is the Alien's turn), so several commands can be issued
    # in a row without re-selecting.
    assert ctrl.selected_crew is not None


def test_selecting_a_deck_switches_the_view() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    entries = ctrl.entries()
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    deck_pos = next(
        k for k, i in enumerate(selectable)
        if entries[i].category is MenuCategory.DECK
    )
    target_deck = entries[selectable[deck_pos]].select_deck
    ctrl.cursor = deck_pos
    ctrl.fire()
    assert sim.state.deck == target_deck


def test_indicate_location_opens_a_room_list_and_marks_a_room() -> None:
    """**[C $73C8/$766F] DISC-238** — two fixed pages of 19 rows, table order.

    This used to assert the list held *every* room at once. `draw_deck_map`
    copies 19 records into panel rows 0-18 and the ROM keeps two source
    offsets: page 1 rows 1-17 are rooms 0-16, page 2 rows 1-17 are rooms
    17-33, with `quit`/`other list` occupying rows 0 and 18 (swapped between
    the pages). NARCISSUS (34) is absent — it is off the deck plans.
    """
    from alien_remake.core.menu import (
        INDICATE_LABEL_OTHER, INDICATE_LAST_ROOM_ROW, INDICATE_ROWS,
    )

    sim = _sim()
    ctrl = MenuController(sim)
    entries = ctrl.entries()
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    ind_pos = next(k for k, i in enumerate(selectable) if entries[i].indicate)
    ctrl.cursor = ind_pos
    ctrl.fire()
    assert ctrl.indicating is True and ctrl.indicate_page == 0

    page1 = ctrl.entries()
    assert len(page1) == INDICATE_ROWS == 19
    rooms1 = [e for e in page1 if e.indicate_room is not None]
    assert len(rooms1) == INDICATE_LAST_ROOM_ROW == 17, "rows 1-17 are rooms"
    assert rooms1[0].label == "Airlock 1" and rooms1[-1].label == "Engineerng"
    assert page1[0].back, "row 0 is quit on page 1"
    assert page1[18].label == INDICATE_LABEL_OTHER, "row 18 flips the page"

    # "other list" swaps the source offset — it does not scroll.
    ctrl.cursor = next(
        k for k, i in enumerate([n for n, e in enumerate(page1) if e.selectable])
        if page1[i].indicate_page is not None
    )
    ctrl.fire()
    assert ctrl.indicate_page == 1 and ctrl.indicating is True
    page2 = ctrl.entries()
    rooms2 = [e for e in page2 if e.indicate_room is not None]
    assert len(rooms2) == 17
    assert rooms2[0].label == "Engine 1" and rooms2[-1].label == "ShttlStore"
    assert page2[0].label == INDICATE_LABEL_OTHER, "the controls swap over"
    assert page2[18].back, "row 18 is quit on page 2"

    # 34 rooms across both pages, in table order, NARCISSUS excluded.
    both = [e.indicate_room for e in rooms1 + rooms2]
    assert len(both) == len(set(both)) == 34
    assert "narcissus" not in both

    # Picking a room marks it and switches deck, and **leaves the list open**
    # (DISC-272, measured live: `$64FB` stays 16 and the room rows stay up, so
    # you can indicate several in a row; QUIT on row 0 is the way out).
    target = rooms2[0]
    room = sim.ship.rooms[target.indicate_room]
    sel = [i for i, e in enumerate(page2) if e.selectable]
    ctrl.cursor = next(
        k for k, i in enumerate(sel)
        if page2[i].indicate_room == target.indicate_room
    )
    ctrl.fire()
    assert ctrl.indicating is True, "the ROM leaves the room list up"
    assert ctrl.indicated_room_id == target.indicate_room
    assert sim.state.deck == room.deck
    # ...and a second room can be indicated without reopening anything.
    second = [e for e in ctrl.entries() if e.indicate_room is not None][1]
    sel = [i for i, e in enumerate(ctrl.entries()) if e.selectable]
    ctrl.cursor = next(
        k for k, i in enumerate(sel)
        if ctrl.entries()[i].indicate_room == second.indicate_room
    )
    ctrl.fire()
    assert ctrl.indicated_room_id == second.indicate_room


def test_indicate_list_quit_returns_to_control() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    ind_pos = next(
        k for k, i in enumerate([j for j, e in enumerate(ctrl.entries()) if e.selectable])
        if ctrl.entries()[i].indicate
    )
    ctrl.cursor = ind_pos
    ctrl.fire()
    assert ctrl.indicating is True
    ctrl.cursor = 0  # QUIT is the first selectable in the room list
    ctrl.fire()
    assert ctrl.indicating is False
    assert ctrl.selected_crew is None


def test_cursor_wraps_within_selectable_entries() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    n = len(ctrl._selectable(ctrl.entries()))
    ctrl.move(-1)
    assert ctrl.cursor == n - 1
    ctrl.move(1)
    assert ctrl.cursor == 0


def test_special_option_fires_and_stays_on_the_crew_member() -> None:
    sim = _sim()
    ctrl = MenuController(sim)
    _select_living_crew(ctrl)
    entries = ctrl.entries()
    selectable = [i for i, e in enumerate(entries) if e.selectable]
    scuttle = next(
        k for k, i in enumerate(selectable)
        if entries[i].special
        and entries[i].special.type is SpecialOptionType.INITIATE_AUTO_DESTRUCT
    )
    ctrl.cursor = scuttle
    ctrl.fire()
    assert sim.state.auto_destruct_ticks is not None  # scuttle started
    # **P4-4:** the panel now STAYS on the crew member after an order — the
    # ROM's order path never writes `$64FB` (only `reset_alien_turn $83FD`
    # does, and that is the Alien's turn), so several commands can be issued
    # in a row without re-selecting.
    assert ctrl.selected_crew is not None


# --- P2-5: who can actually be commanded -------------------------------------

def test_a_dead_or_collapsed_crew_member_is_listed_but_cannot_be_commanded() -> None:
    """**[C $7720] `guard_alien_present`** bounces the selection straight back
    to the CONTROL list when `$7D45,Y < 2` or the character is asleep — their
    name and status stay on the panel (that is how you learn who died), but no
    order menu ever opens.

    A player reported "the crew isn't all selectable at the start". This is the
    game working as designed: the opening victim is listed and pickable, and
    picking them does nothing. **The one real bug was the threshold** — the
    remake gated on `alive` (health > 0), so a COLLAPSED crew member on 1
    health could still be commanded. The ROM's constant is 2, the same one the
    endgame scan uses (`$5B5B CMP #$02`, D-103).
    """
    import random

    from alien_remake.core import constants
    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    ctrl = MenuController(sim)
    dead_id = sim.state.opening_dead_crew_id
    assert dead_id is not None

    def try_select(crew_id: str) -> bool:
        ctrl.selected_crew = None
        ctrl.cursor = 0
        entries = ctrl.entries()
        pick = [i for i, e in enumerate(entries) if e.selectable]
        idx = next(
            (k for k, i in enumerate(pick) if entries[i].select_crew == crew_id),
            None,
        )
        assert idx is not None, f"{crew_id} should still be LISTED"
        ctrl.cursor = idx
        ctrl.fire()
        return ctrl.selected_crew == crew_id

    # Every living, healthy, awake crew member can be commanded...
    living = [
        c.id for c in sim.state.crew.values()
        if c.health >= constants.CREW_INCAPACITATED_BELOW and c.awake
    ]
    assert len(living) == 6
    for cid in living:
        assert try_select(cid), f"{cid} should be selectable"

    # ...the opening victim is listed but inert.
    assert not try_select(dead_id)

    # A COLLAPSED survivor (1 health) is inert too — the corrected threshold.
    victim = sim.state.crew[living[0]]
    victim.health = 1
    assert victim.alive is True
    assert not try_select(victim.id), "health 1 is below the ROM's `CMP #$02`"
    victim.health = 2
    assert try_select(victim.id), "health 2 is commandable again"


def test_a_dead_crew_member_does_not_trap_the_cursor() -> None:
    """**[C $7720] P3-1 — the reported bug, pinned.**

    `guard_alien_present` clears the **selection** (`STA $64FB` = 0) and never
    touches `$64E5`, the panel's cursor row. We used to reset the cursor on that
    bounce, which turned the opening victim into a trap: land on them, get
    thrown back to the top, and never reach anyone below. Since the victim sits
    early in the roster that made most of the crew unreachable — the reported
    "ASH, LAMBERT and BRETT couldn't be selected".
    """
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    dead = sim.state.opening_dead_crew_id
    assert dead is not None
    m = MenuController(sim)

    commanded = []
    for _ in range(len(sim.state.crew)):
        m.fire()
        if m.selected_crew:
            commanded.append(m.selected_crew)
            m.back()
        m.move(1)

    living = [
        c.id for c in sim.state.crew.values()
        if c.health >= 2 and c.awake
    ]
    assert commanded == living, "every living crew member in ONE pass"
    assert dead not in commanded


def test_backing_out_returns_the_cursor_where_it_was() -> None:
    """[C $7640-$7653] the back-out path writes `$64FB`/`$64BD` and never
    `$64E5`, so the highlight stays where you left it."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    m = MenuController(sim)
    m.move(1)
    m.move(1)
    m.move(1)
    before = m.cursor
    entry_label = m.entries()[m.current_index()].label
    m.fire()
    if m.selected_crew:
        m.back()
        assert m.cursor == before
        assert m.entries()[m.current_index()].label == entry_label


# --- P4-2 / P4-3 / P4-4: the destination preview and menu persistence --------

def test_hovering_a_move_to_entry_previews_that_room() -> None:
    """**[C $7C3D] P4-2.** While the player browses destinations the ROM keeps
    the location pointer live over the candidate room and arms the animation
    (`$7C6C LDA #$01 / STA $64BE`). We only previewed for INDICATE LOCATION."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.orders import OrderType
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    ctrl = MenuController(sim)
    ctrl.fire()                                   # select the first crew member
    assert ctrl.selected_crew is not None

    entries = ctrl.entries()
    move = next(
        i for i, e in enumerate(entries)
        if e.order is not None and e.order.type is OrderType.MOVE_TO
    )
    ctrl.cursor = [i for i, e in enumerate(entries) if e.selectable].index(move)
    assert ctrl.previewed_room_id == entries[move].order.target

    # A non-MOVE-TO entry previews nothing.
    other = next(
        (i for i, e in enumerate(entries)
         if e.selectable and (e.order is None or e.order.type is not OrderType.MOVE_TO)),
        None,
    )
    if other is not None:
        ctrl.cursor = [i for i, e in enumerate(entries) if e.selectable].index(other)
        assert ctrl.previewed_room_id is None


def test_issuing_orders_keeps_the_crew_member_selected() -> None:
    """**P4-4.** Nothing on the ROM's order path writes `$64FB` — the item
    handler ends `$8460 JSR compute_action_delay / STA $650C,Y / RTS`, and the
    only routine clearing the selected slot is `reset_alien_turn ($83FD)`,
    which belongs to the Alien's turn. So several commands can be issued in a
    row; we used to drop to the CONTROL list after every one."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    ctrl = MenuController(sim)
    ctrl.fire()
    who = ctrl.selected_crew
    assert who is not None

    # **D-168/PV-34** - a second order for the SAME character now
    # replaces the first ($7B02 zeroes $650C,Y and $64EE,Y before
    # arming), so the pending count stays at 1 however many times you
    # fire. What this test is about is that firing does not deselect.
    for _ in range(2):
        entries = ctrl.entries()
        idx = next(i for i, e in enumerate(entries) if e.order is not None)
        ctrl.cursor = [i for i, e in enumerate(entries) if e.selectable].index(idx)
        ctrl.fire()
        assert ctrl.selected_crew == who, "must stay on the same crew member"
        assert sim.pending_orders == 1, "one pending action per character"


# --- P5-6: the ROM's four-part selection gate ($7720) ------------------------

def test_the_four_selection_gates_are_the_roms_own() -> None:
    """**[C $7720] P5-6.** `guard_alien_present` bounces a pick by writing
    `STA $64FB` = 0 on **four** conditions, and the remake modelled two::

        773B  LDA $64D1,Y / BNE bounce   ; in hypersleep          (had it)
        7740  CPY $64CC   / BEQ bounce   ; the slot $64CC names   (MISSING)
        7745  LDA $7D45,Y / CMP #$02
              BCC bounce                 ; health below 2         (had it)
        7757  LDA $6571,Y / BNE ok       ; composure 0 ...
        7768  JSR find_colocated_crew
              CPX #$08 / BEQ bounce      ; ...and alone           (MISSING)
    """
    import random

    from alien_remake.core import constants
    from alien_remake.core.menu import can_be_commanded
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = sim.state.crew["dallas"]
    assert can_be_commanded(sim, crew)

    # $773B — hypersleep.
    crew.awake = False
    assert not can_be_commanded(sim, crew)
    crew.awake = True

    # $7740 — the slot `$64CC` names (set on the android's attack path).
    sim.state.locked_crew_id = crew.id
    assert not can_be_commanded(sim, crew)
    sim.state.locked_crew_id = None

    # $7745 — health below 2.
    crew.health = constants.CREW_INCAPACITATED_BELOW - 1
    assert not can_be_commanded(sim, crew)
    crew.health = 5


def test_a_broken_crew_member_can_be_commanded_only_with_company() -> None:
    """**[C $7757/$7768]** — the gate the remake never had. Composure 0 does
    **not** by itself lock someone out: `find_colocated_crew ($4581)` looks for
    another crew member in the same room *and* duct state with health >= 2 and
    composure != 0, and only bounces when there is none (`CPX #$08`).

    So a broken crew member is still commandable while someone functional is
    with them, and lost to you once they are alone. That is the mechanic behind
    a player's guess that some characters "start as Insane".
    """
    import random

    from alien_remake.core.menu import can_be_commanded, has_functional_companion
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    broken = sim.state.crew["dallas"]
    mate = sim.state.crew["ripley"]
    broken.fear = 0
    assert broken.room_id == mate.room_id      # both start in COMMDCENTR

    assert has_functional_companion(sim, broken)
    assert can_be_commanded(sim, broken), "company keeps them usable"

    # Move the companion away -> the broken one is now unreachable.
    mate.room_id = "mess"
    for other in sim.state.crew.values():
        if other.id != broken.id:
            other.room_id = "mess"
    assert not has_functional_companion(sim, broken)
    assert not can_be_commanded(sim, broken)

    # A companion in the DUCTS does not count — `$4581` matches `$6501` too.
    mate.room_id = broken.room_id
    mate.in_duct = True
    assert not has_functional_companion(sim, broken)


# --- D-145: GET ITEM is one row that opens a submenu -------------------------

def test_get_item_is_a_single_row_not_an_inline_item_list() -> None:
    """**[C-live] D-145.** Every panel in the player's own recording shows a
    single "Get item" row (e.g. "use: / Incinerotr / Get item / Leave item /
    Special:"), never the room's contents listed inline. This used to
    enumerate every item straight onto the main panel, which both mis-shaped
    the menu and leaked what was in the room before the player asked.
    """
    from alien_remake.core.command_monitor import items_in_room

    sim = _sim()
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.room_id and items_in_room(sim.state, c.room_id)
    )
    entries = crew_entries(sim, crew_id)
    gets = [e for e in entries if e.category is MenuCategory.GET]
    assert len(gets) == 1, f"expected one GET row, got {[e.label for e in gets]}"
    assert gets[0].get_items is True
    assert gets[0].order is None, "the row itself issues no order; it opens a list"
    # And no room item name leaks onto the main panel.
    room_items = {
        i.type_id.upper() for i in items_in_room(sim.state, sim.state.crew[crew_id].room_id)
    }
    labels = {e.label.upper().replace(" ", "") for e in entries}
    assert not (room_items & labels), "room contents must not show on the main panel"


def test_get_item_row_opens_a_submenu_of_the_rooms_items() -> None:
    from alien_remake.core.command_monitor import items_in_room

    sim = _sim()
    m = MenuController(sim)
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.room_id and items_in_room(sim.state, c.room_id)
    )
    m.selected_crew = crew_id
    entries = m.entries()
    target = next(i for i, e in enumerate(entries) if e.get_items)
    m.cursor = m._selectable(entries).index(target)
    m.fire()

    assert m.getting_item is True
    sub = m.entries()
    assert sub[0].label == "GET ITEM:"
    picks = [e for e in sub if e.order is not None]
    assert picks, "the submenu must list the room's items"
    assert all(e.order.type is OrderType.GET_ITEM for e in picks)


def test_get_item_submenu_quit_returns_to_the_crew_panel_not_the_control_list() -> None:
    from alien_remake.core.command_monitor import items_in_room

    sim = _sim()
    m = MenuController(sim)
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.room_id and items_in_room(sim.state, c.room_id)
    )
    m.selected_crew = crew_id
    m.getting_item = True
    m.back()
    assert m.getting_item is False
    assert m.selected_crew == crew_id, "QUIT in the submenu must not deselect"


def test_taking_an_item_closes_the_submenu() -> None:
    from alien_remake.core.command_monitor import items_in_room

    sim = _sim()
    m = MenuController(sim)
    crew_id = next(
        c.id for c in sim.state.crew.values()
        if c.alive and c.room_id and items_in_room(sim.state, c.room_id)
    )
    m.selected_crew = crew_id
    m.getting_item = True
    sub = m.entries()
    target = next(i for i, e in enumerate(sub) if e.order is not None)
    m.cursor = m._selectable(sub).index(target)
    m.fire()
    assert m.getting_item is False


def _select_a_living_crew_member(ctrl: MenuController) -> str:
    """Drive the controller onto the first commandable crew row and fire."""
    from alien_remake.core.menu import can_be_commanded

    entries = ctrl.entries()
    selectable = [i for i, e in enumerate(entries) if e.select_crew or e.indicate]
    for pos, idx in enumerate(selectable):
        entry = entries[idx]
        if entry.select_crew is None:
            continue
        crew = ctrl.sim.state.crew[entry.select_crew]
        if not can_be_commanded(ctrl.sim, crew):
            continue
        ctrl.cursor = pos
        ctrl.fire()
        assert ctrl.selected_crew == entry.select_crew
        return entry.select_crew
    raise AssertionError("no commandable crew member in the CONTROL list")


def test_the_selection_gate_is_re_evaluated_every_frame() -> None:
    """**[C $72EE -> $7720] D-158** — the pattern: a conditional, *repeated*
    ROM behaviour that the remake had collapsed into a single check at the
    moment of the click.

    `check_deferred_move` calls `guard_alien_present` on **every move pass**,
    and its bounce writes `STA $64FB` = 0 — dropping whoever is *currently*
    selected. The remake only ran `can_be_commanded` inside `fire()`, so a
    crew member who stopped qualifying *after* being picked stayed
    commandable for the rest of the game.

    Each of `guard_alien_present`'s four tests must be able to end a
    selection already in progress, not just refuse a new one.
    """
    from alien_remake.core.constants import CREW_INCAPACITATED_BELOW

    # $7745 `LDA $7D45,Y / CMP #$02 / BCC` -- collapsing to 1 health.
    sim = _sim()
    ctrl = MenuController(sim)
    crew_id = _select_a_living_crew_member(ctrl)
    sim.state.crew[crew_id].health = CREW_INCAPACITATED_BELOW - 1
    ctrl.entries()
    assert ctrl.selected_crew is None, "a collapsed crew member must be dropped"

    # $773B `LDA $64D1,Y / BNE` -- going into hypersleep.
    sim = _sim()
    ctrl = MenuController(sim)
    crew_id = _select_a_living_crew_member(ctrl)
    sim.state.crew[crew_id].awake = False
    ctrl.entries()
    assert ctrl.selected_crew is None, "a sleeping crew member must be dropped"

    # $7740 `CPY $64CC / BEQ` -- being unmasked as the android.
    sim = _sim()
    ctrl = MenuController(sim)
    crew_id = _select_a_living_crew_member(ctrl)
    sim.state.locked_crew_id = crew_id
    ctrl.entries()
    assert ctrl.selected_crew is None, "the revealed android must be dropped"

    # $7757/$7768 -- composure 0 with nobody functional alongside.
    sim = _sim()
    ctrl = MenuController(sim)
    crew_id = _select_a_living_crew_member(ctrl)
    held = sim.state.crew[crew_id]
    for other in sim.state.crew.values():
        if other.id != crew_id:
            other.room_id = None          # clear the room so nobody supports
    held.fear = 0
    assert sim.effective_composure(held) == 0
    ctrl.entries()
    assert ctrl.selected_crew is None, "broken and alone -> dropped"


def test_a_still_qualifying_selection_survives_the_re_check() -> None:
    """The guard must not be trigger-happy: an ordinary crew member stays
    selected across repeated panel builds (`$7757 BNE ok` falls through to
    `draw_char_status`, it does not bounce)."""
    sim = _sim()
    ctrl = MenuController(sim)
    crew_id = _select_a_living_crew_member(ctrl)
    for _ in range(20):
        ctrl.entries()
    assert ctrl.selected_crew == crew_id


def test_jones_notice_has_both_rom_branches() -> None:
    """**[C $88CC/$8932] D-158** — `guard_6580` re-derives row 24 every pass
    and has *two* outcomes; the remake only drew the first, so the cat went
    invisible whenever the player was watching another room."""
    from alien_remake.core.alien import Alien
    from alien_remake.core.constants import CREW_INCAPACITATED_BELOW
    from alien_remake.core.crew import CrewMember, Role
    from alien_remake.core.nostromo import nostromo_ship
    from alien_remake.core.state import GameState
    from alien_remake.render.play import jones_notice_text

    ship = nostromo_ship()
    room = "corridor_1"
    elsewhere = ship.door_neighbors(room)[0]

    def _state(**kw: object) -> GameState:
        ripley = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)
        for k, v in kw.items():
            setattr(ripley, k, v)
        return GameState(
            crew={"ripley": ripley},
            alien=Alien(room_id=elsewhere),
            jones_room_id=room,
        )

    # $890C: Jones in the displayed room, a surfaced crew member selected.
    st = _state()
    assert jones_notice_text(st, st.crew["ripley"]) == "JONES IS HERE"

    # $8932: nobody selected -> the fall-through names whoever sees him.
    assert jones_notice_text(st, None) == "RIPLEY     SEES JONES "

    # $8944 / $8949: a ducted or collapsed witness does not count.
    st = _state(in_duct=True)
    assert jones_notice_text(st, None) is None
    st = _state(health=CREW_INCAPACITATED_BELOW - 1)
    assert jones_notice_text(st, None) is None

    # Nobody in Jones's room at all -> the row stays blank ($88D2).
    st = _state(room_id=elsewhere)
    assert jones_notice_text(st, None) is None


def test_get_jones_is_a_contextual_panel_row() -> None:
    """**[C $8860 -> $0676 / $8437 -> $8784] P8-3, D-160.**

    `guard_6580` writes the "GET JONES " label into the panel slot `$0676`
    every pass the cat is in the displayed room with a surfaced crew member
    selected, and blanks it (`$88E8`) the moment that stops holding.
    `route_command` sends that row (cursor `$0F`, below the `#$10` Special
    band) into the catch handler. It had been removed as an invention and then
    reinstated only as a USE side effect; this is the real thing.
    """
    from alien_remake.core.crew import CrewMember, Role
    from alien_remake.core.orders import OrderType

    def rows(sim: Simulation, crew_id: str) -> list[str]:
        return [e.label for e in crew_entries(sim, crew_id)]

    sim = _sim()
    crew: CrewMember = next(c for c in sim.state.crew.values() if c.alive and c.room_id)

    # Cat elsewhere: no row.
    sim.state.jones_room_id = next(
        r for r in sim.ship.rooms if r != crew.room_id
    )
    assert "GET JONES" not in rows(sim, crew.id)

    # Cat here: the row appears, carrying a GET_JONES order.
    sim.state.jones_room_id = crew.room_id
    entries = crew_entries(sim, crew.id)
    entry = next(e for e in entries if e.label == "GET JONES")
    assert entry.selectable
    assert entry.order is not None and entry.order.type is OrderType.GET_JONES

    # $8907: not while that crew member is inside a duct.
    crew.in_duct = True
    assert "GET JONES" not in rows(sim, crew.id)
    crew.in_duct = False

    # Already caught ($8780's `$6580` gate): gone for good.
    sim.state.jones_caught = True
    assert "GET JONES" not in rows(sim, crew.id)


def test_grabbing_at_jones_spooks_him_whether_or_not_it_lands() -> None:
    """**CLASSIC only since DISC-262** — the default no longer spooks him.

    `$878C` is still what the ROM does and is still asserted here; the house
    rule that keeps him in the room after a miss is opt-out, not a change to
    this finding.
    """
    """**[C $878C `LDA #$01 / STA $657F`] D-160** — the handler slams Jones's
    move counter to 1 *before* rolling, so he steps on the next pass either
    way. A missed grab costs you more than the attempt: the cat bolts."""
    import random

    from alien_remake.core.constants import JONES_MOVE_TICKS

    sim = _sim(jones_catch=JonesCatch.CLASSIC)
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    sim.state.jones_room_id = crew.room_id
    sim.state.jones_caught = False
    sim._jones_timer = JONES_MOVE_TICKS
    sim.rng = random.Random(0)
    sim._catch_jones(crew.id)
    assert sim._jones_timer == 1, "the grab must reset $657F regardless of the roll"


def test_specials_are_refused_when_broken_or_collapsed() -> None:
    """**[C $583F] PV-04/D-163** — the specials dispatcher's own two gates.

    `$5842 LDA $6571,Y / BEQ` and `$5847 LDA $7D45,Y / CMP #$02 / BCC` refuse
    *before* dispatching on the option code. The composure test has **no
    companion escape**, unlike `guard_alien_present ($7757/$7768)` — so an
    accompanied but broken crew member can still take ordinary orders yet
    cannot work a single Special Option. That asymmetry was unmodelled.
    """
    from alien_remake.core.constants import CREW_INCAPACITATED_BELOW
    from alien_remake.core.menu import SPECIAL_ROOM_HYPERSLEEP, can_be_commanded
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    def arm(sim: Simulation, crew_id: str) -> bool:
        # The handler itself is room-gated to the CRYO VAULT ($5939), so stage
        # them there � this test is about $583F's gates, not that one.
        sim.state.crew[crew_id].room_id = SPECIAL_ROOM_HYPERSLEEP
        return sim.apply_special_option(
            SpecialOption(SpecialOptionType.ENTER_HYPERSLEEP, crew_id=crew_id)
        )

    # Baseline: an ordinary crew member's special takes effect.
    sim = _sim()
    ok = next(
        c for c in sim.state.crew.values()
        if c.alive and c.awake and c.id != sim.state.android_id
    )
    assert arm(sim, ok.id) is True

    # $5847: health below 2 -> nothing happens.
    sim = _sim()
    hurt = next(
        c for c in sim.state.crew.values()
        if c.alive and c.awake and c.id != sim.state.android_id
    )
    hurt.health = CREW_INCAPACITATED_BELOW - 1
    assert arm(sim, hurt.id) is False

    # $5842: composure 0 -> nothing, *even with a functional companion* who
    # keeps them selectable through guard_alien_present's own gate.
    sim = _sim()
    broken = next(
        c for c in sim.state.crew.values()
        if c.alive and c.awake and c.id != sim.state.android_id
    )
    mate = next(
        c for c in sim.state.crew.values()
        if c.id != broken.id and c.alive and c.health >= CREW_INCAPACITATED_BELOW
    )
    mate.room_id = broken.room_id
    mate.in_duct = False
    mate.fear = 6
    broken.fear = 0
    assert sim.effective_composure(broken) > 0, "the companion props them up..."
    broken.fear = 0
    for other in sim.state.crew.values():
        if other.id != broken.id:
            other.room_id = None
    assert sim.effective_composure(broken) == 0
    assert arm(sim, broken.id) is False

    # And the asymmetry itself: accompanied-but-broken stays *commandable*.
    sim = _sim()
    b2 = next(c for c in sim.state.crew.values() if c.alive and c.awake)
    m2 = next(
        c for c in sim.state.crew.values()
        if c.id != b2.id and c.alive and c.health >= CREW_INCAPACITATED_BELOW
    )
    m2.room_id, m2.in_duct, m2.fear = b2.room_id, False, 4
    b2.fear = 0
    assert can_be_commanded(sim, b2), "$7768's companion escape still applies"


def test_ducted_crew_are_offered_no_room_specials() -> None:
    """**[C $56B7] PV-04/D-163** — `guard_target_alive` opens `LDA $6501,Y /
    BEQ` and RTSes for anyone inside the ducting, so none of the `$5753`-derived
    rows (SCUTTLE / BLOWLOCK / HYPERSLEEP / LAUNCH / FIGHT FIRE) are drawn."""
    from alien_remake.core.menu import SPECIAL_ROOM_HYPERSLEEP

    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive and c.awake)
    crew.room_id = SPECIAL_ROOM_HYPERSLEEP
    crew.in_duct = False
    labels = [e.label for e in crew_entries(sim, crew.id)]
    assert "Enter" in labels, "on the surface in the CRYO VAULT it is offered"

    crew.in_duct = True
    labels = [e.label for e in crew_entries(sim, crew.id)]
    assert "Enter" not in labels, "$56B7: not from inside the ducting"


def test_the_catch_threshold_uses_the_shared_slot_lookup() -> None:
    """**DISC-222 cleanup.** `_catch_jones` used to reimplement the crew ->
    slot mapping (`list(self.state.crew).index(crew_id) + 1`) instead of
    calling `_slot_of`, the one place this lookup is supposed to live (it
    also backs `$4032`/`$403A`'s per-character tables, D-166). The two agreed
    by coincidence — `default_crew` happens to build the roster dict in
    `CREW_NAMES` order — so this pins that `_slot_of` is what's actually
    driving the threshold now, not a parallel reimplementation that could
    silently diverge from it.
    """
    from alien_remake.core.constants import JONES_CATCH_THRESHOLD

    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    assert JONES_CATCH_THRESHOLD[sim._slot_of(crew)] != 0, (
        "a real crew member must never land on the Alien's unused slot 0"
    )


def test_attack_and_remvgrille_never_share_a_row() -> None:
    """**DISC-227.** `draw_grille_option ($86F0)` and the attack trigger
    (`$8CE1`) both write their 10-char label into `$064E` - the ROM can
    only ever show one, never both. The remake used to `append` each
    independently, stacking two rows the original never shows together.
    Attack wins when both apply (the fresher write, real-time as the
    encounter starts).
    """
    sim = _sim()
    room_id = next(
        g.room_id for g in sim.ship.grilles if not g.is_open
    )  # a real room with a closed grille
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.room_id = room_id
    crew.in_duct = False
    assert sim.state.alien is not None
    sim.state.alien.room_id = room_id
    sim.state.alien.in_duct = False
    sim.state.alien.alive = True

    labels = {e.label for e in crew_entries(sim, crew.id)}
    assert "Attack" in labels
    assert "RemvGrille" not in labels, "Attack must win the shared row"

    sim.state.alien.alive = False
    labels = {e.label for e in crew_entries(sim, crew.id)}
    assert "RemvGrille" in labels, "RemvGrille shows once nothing contests the row"
    assert "Attack" not in labels


def test_get_and_leave_item_occupy_their_own_rows() -> None:
    """**[C $05D6 / $05FE] DISC-244** — two independent rows, not one shared slot.

    `draw_item_row2 ($8387)` writes " Get item " to `$05D6` (row 11) whenever
    the room holds an object, with no test of what the character is carrying.
    `list_room_items ($83E0)` writes "Leave item" to `$05FE` (**row 12**)
    whenever they are carrying one. Both at once is the normal case.

    The remake mapped both categories to slot 11, so with an item in the room
    *and* one in hand they collided and "Get item" appeared only sometimes.
    """
    from alien_remake.core.menu import MenuCategory, MenuEntry
    from alien_remake.render.play import PlayMixin
    from alien_remake.screens import panels

    assert panels.PANEL_SLOT_ITEM == 11
    assert panels.PANEL_SLOT_LEAVE == 12

    entries = [
        MenuEntry("Dallas", MenuCategory.HEADER),
        MenuEntry("Get item", MenuCategory.GET, selectable=True),
        MenuEntry("Leave item", MenuCategory.LEAVE, selectable=True),
    ]
    rows = PlayMixin._panel_rows(entries)
    get_row = rows[entries.index(entries[1])]
    leave_row = rows[entries.index(entries[2])]

    assert get_row == 11, "Get item belongs on row 11 ($05D6)"
    assert leave_row == 12, "Leave item belongs on row 12 ($05FE)"
    assert get_row != leave_row, "they shared a slot and overwrote each other"


def test_get_item_does_not_depend_on_what_the_crew_member_holds() -> None:
    """`$836F CPX #$FF` tests only whether the room scan found anything.

    There is no reference to the carried-item slot on that path, so holding
    something must not suppress "Get item".
    """
    import random

    from alien_remake.core.command_monitor import items_in_room
    from alien_remake.core.menu import MenuCategory, crew_entries
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    room_items = items_in_room(sim.state, crew.room_id)
    if not room_items:
        import pytest
        pytest.skip("no item in this crew member's starting room")

    def has_get() -> bool:
        return any(
            e.category is MenuCategory.GET
            for e in crew_entries(sim, crew.id)
        )

    crew.holding = None
    assert has_get()
    crew.holding = room_items[0].id      # now carrying something
    assert has_get(), "holding an item must not hide Get item"


def test_the_alien_engages_only_the_lowest_numbered_occupant() -> None:
    """**[C $8C49] DISC-246** — the scan stops at its first match.

    With two crew in the room the ROM engages the lower-numbered one, and
    `$8CE1 CPY $64FB` then offers ATTACK to that one alone. The old condition
    (Alien alive, surfaced, same room) offered it to everyone present.
    """
    from alien_remake.core.command_monitor import crew_with_alien

    sim = _sim()
    living = [c for c in sim.state.crew.values() if c.alive]
    first, second = living[0], living[1]
    room = first.room_id
    for c in sim.state.crew.values():
        c.in_duct = False
        if c not in (first, second):
            c.room_id = None
    first.room_id = second.room_id = room
    assert sim.state.alien is not None
    sim.state.alien.room_id = room
    sim.state.alien.in_duct = False

    assert crew_with_alien(sim.state) == first.id
    assert "Attack" in [e.label for e in crew_entries(sim, first.id)]
    assert "Attack" not in [e.label for e in crew_entries(sim, second.id)], (
        "the Alien engages one crew member, not everyone in the room"
    )

    # With the first one out of the way the scan falls through to the second.
    first.room_id = None
    assert crew_with_alien(sim.state) == second.id


def test_the_alien_passes_over_crew_already_down() -> None:
    """**[C $8C5B CMP #$02 / BCC]** — health below 2 is skipped entirely."""
    from alien_remake.core.command_monitor import (
        ATTACK_MIN_HEALTH, crew_with_alien,
    )

    sim = _sim()
    living = [c for c in sim.state.crew.values() if c.alive]
    victim, next_up = living[0], living[1]
    room = victim.room_id
    for c in sim.state.crew.values():
        c.in_duct = False
        if c not in (victim, next_up):
            c.room_id = None
    victim.room_id = next_up.room_id = room
    assert sim.state.alien is not None
    sim.state.alien.room_id = room
    sim.state.alien.in_duct = False

    assert crew_with_alien(sim.state) == victim.id
    victim.health = ATTACK_MIN_HEALTH - 1
    assert crew_with_alien(sim.state) == next_up.id, (
        "a crew member already down is passed over ($8C5B)"
    )


def test_the_duct_test_is_a_comparison_not_a_surfaced_check() -> None:
    """**[C $8C56 CMP $6501]** — both flags must agree, either way round."""
    from alien_remake.core.command_monitor import crew_with_alien

    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive)
    for c in sim.state.crew.values():
        c.in_duct = False
        if c is not crew:
            c.room_id = None
    assert sim.state.alien is not None
    sim.state.alien.room_id = crew.room_id

    for alien_ducted, crew_ducted, found in (
        (False, False, True),    # both in the room
        (True, True, True),      # both in the vents
        (True, False, False),    # Alien in the vents, crew in the room
        (False, True, False),    # crew in the vents, Alien in the room
    ):
        sim.state.alien.in_duct = alien_ducted
        crew.in_duct = crew_ducted
        got = crew_with_alien(sim.state) == crew.id
        assert got is found, (
            f"alien.in_duct={alien_ducted} crew.in_duct={crew_ducted}: "
            f"expected found={found}"
        )


def test_crew_with_alien_walks_the_roms_own_slot_order() -> None:
    """**[C $8C49 LDY #$01] DISC-246** — "first match" is only right in slot order.

    `find_crew_with_alien` scans `$7935` from slot 1 upward (slot 0 is the
    Alien) and stops at the first qualifying crew member, so *which* one it
    finds depends entirely on the ordering. `ROSTER` index i is ROM slot i+1 —
    the same mapping `CREW_START_ROOMS` and `CREW_WALK_TICKS` are indexed by —
    and `state.crew` preserves it.

    If the dict ever stopped preserving that order the scan would silently
    engage the wrong crew member, with nothing else failing.
    """
    from alien_remake.core.command_monitor import crew_with_alien
    from alien_remake.core.crew import ROSTER

    sim = _sim()
    assert list(sim.state.crew) == [cid for cid, _n, _r in ROSTER]

    assert sim.state.alien is not None
    sim.state.alien.in_duct = False
    room = "engine_2"
    for c in sim.state.crew.values():
        c.room_id = None
        c.in_duct = False
    sim.state.alien.room_id = room

    # Put every crew member in the room one at a time, lowest slot last, and
    # check the scan always returns the lowest-numbered occupant.
    for cutoff in range(len(ROSTER), 0, -1):
        for i, (cid, _n, _r) in enumerate(ROSTER):
            sim.state.crew[cid].room_id = room if i < cutoff else None
        alive_in_room = [
            cid for i, (cid, _n, _r) in enumerate(ROSTER)
            if i < cutoff and sim.state.crew[cid].alive
        ]
        if not alive_in_room:
            continue
        assert crew_with_alien(sim.state) == alive_in_room[0], (
            f"with slots 1..{cutoff} present the scan must stop at the first"
        )


def test_both_carried_items_are_listed_with_the_active_one_on_top() -> None:
    """**[C $83AF/$83C6] DISC-261** — two carry slots, two panel rows.

    `list_room_items` fills them from the object's own location byte: `+$A0`
    draws at `$0586` (row 9) and records `$829A`, `+$80` draws at `$05AE`
    (row 10) and records `$829B`. `$829A` is the active slot — every action
    reads it, and `$4679` reaches the second only by copying `$829B` over it
    and restoring afterwards.

    The remake showed only `crew.holding`, so the spare was carried but
    invisible and there was no way to reach it.
    """
    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.carried.clear()
    laser = next(i for i in sim.state.items.values() if i.type_id == "laser_pist")
    tracker = next(i for i in sim.state.items.values() if i.type_id == "tracker")
    for item in (laser, tracker):
        item.room_id, item.holder = None, crew.id
        crew.carried.append(item.id)

    rows = [e for e in crew_entries(sim, crew.id) if e.category is MenuCategory.USE]
    assert len(rows) == 2, f"expected both carried items, got {[r.label for r in rows]}"
    assert rows[0].label == "Tracker", "the item in hand belongs on top"
    assert rows[0].order is not None and rows[0].order.type is OrderType.USE
    assert rows[1].order is not None
    assert rows[1].order.type.name == "SELECT_ITEM"


def test_firing_the_spare_row_brings_it_to_hand() -> None:
    """Choosing the lower row swaps, it does not use (DISC-261)."""
    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.carried.clear()
    laser = next(i for i in sim.state.items.values() if i.type_id == "laser_pist")
    tracker = next(i for i in sim.state.items.values() if i.type_id == "tracker")
    for item in (laser, tracker):
        item.room_id, item.holder = None, crew.id
        crew.carried.append(item.id)
    assert crew.holding == tracker.id

    spare = [
        e for e in crew_entries(sim, crew.id) if e.category is MenuCategory.USE
    ][1]
    assert spare.order is not None
    sim.queue_order(spare.order)
    sim.advance()

    assert crew.holding == laser.id, "the spare did not come to hand"
    assert set(crew.carried) == {laser.id, tracker.id}, "an item was lost"
    rows = [e.label for e in crew_entries(sim, crew.id)
            if e.category is MenuCategory.USE]
    assert rows[0] == "Laser Pist"


def test_assigning_an_already_carried_item_promotes_it() -> None:
    """The property's own contract, which the setter used to break.

    `holding` is defined as `carried[-1]`, so assigning something already in
    the list has to move it there. It was a silent no-op, which is what made
    the swap appear to do nothing.
    """
    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.carried.clear()
    first, second = "item-a", "item-b"
    crew.carried.extend([first, second])
    assert crew.holding == second

    crew.holding = first
    assert crew.holding == first, "assigning a carried item did nothing"
    assert crew.carried == [second, first], "the spare was dropped, not demoted"


def test_the_cat_box_is_renamed_once_jones_is_inside() -> None:
    """**[C $8874] DISC-261** — the only confirmation the original gives.

    `guard_6580`'s catch path copies ten bytes from `$8874` over the item-name
    table's type-8 entry (`$87DC`/`$8827 STA $7CC3,Y`), turning "Cat Box" into
    "Jones:Box" on the panel. `$5B33 CMP $7CC3` — the launch validator's "GO GET
    JONES" test — reads that same name.
    """
    from alien_remake.core.menu import JONES_BOX_LABEL, _item_label

    sim = _sim()
    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.carried.clear()
    box = next(i for i in sim.state.items.values() if i.type_id == "cat_box")
    box.room_id, box.holder = None, crew.id
    crew.carried.append(box.id)

    sim.state.jones_caught = False
    assert _item_label("cat_box", sim.state, box.id) == "Cat Box"
    assert [e.label for e in crew_entries(sim, crew.id)
            if e.category is MenuCategory.USE] == ["Cat Box"]

    # **Say what caught him, 2026-08-30.** This used to set `jones_caught` and
    # nothing else, which matched an implementation that renamed *any* cat box
    # once the flag went up. The owner's playtest found what that costs: Ripley
    # caught him with the net and Ash's box, across the ship, announced it had
    # the cat. `$87B6`/`$87D7` rename the catching item, so the test has to name
    # one - and this is the case where the box is it.
    sim.state.jones_caught = True
    sim.state.jones_container_id = box.id
    assert _item_label("cat_box", sim.state, box.id) == JONES_BOX_LABEL == "Jones:Box"
    assert [e.label for e in crew_entries(sim, crew.id)
            if e.category is MenuCategory.USE] == ["Jones:Box"]


def test_a_patient_cat_stays_put_after_a_missed_grab() -> None:
    """**DISC-262** — the default no longer spooks him; the roll is untouched.

    `$878C` slams Jones's move counter to 1 before rolling, so the ROM gives you
    one attempt per encounter and, with the cat box at 6-19% (`$883C`), that is
    a long hunt. Measured over 10 seeded games with a crew member walking to him
    and grabbing: classic catches 3/10 with a median of 1,283 ticks, patient
    6/10 at 310.
    """
    import random

    from alien_remake.core.constants import JONES_MOVE_TICKS
    from alien_remake.core.modes import JonesCatch
    from alien_remake.core.orders import Order, OrderType

    for mode, spooked in ((JonesCatch.CLASSIC, True), (JonesCatch.PATIENT, False)):
        sim = Simulation(rng=random.Random(3), jones_catch=mode)
        crew = next(c for c in sim.state.crew.values() if c.alive)
        crew.carried.clear()
        crew.room_id = sim.state.jones_room_id
        crew.in_duct = False
        # Empty-handed: the grab is refused before the roll, so this isolates
        # the spook from the outcome.
        sim._jones_timer = JONES_MOVE_TICKS
        # Call the handler directly and read the counter *before* a tick can
        # reload it. Two indirect probes were rejected first: reading it after
        # `advance` shows 40 either way (the reload happens on the pass he
        # steps), and watching for a room change is unreliable because his
        # route can send him back where he was.
        assert not sim._catch_jones(crew.id), "empty-handed grabs cannot land"
        if spooked:
            assert sim._jones_timer == 1, (
                "$878C sets the move counter to 1 — the cat bolts next pass"
            )
        else:
            assert sim._jones_timer == JONES_MOVE_TICKS, (
                "a patient cat's move counter must be left alone"
            )


def test_the_house_rule_does_not_touch_the_catch_odds() -> None:
    """Only the number of attempts changes, never their probability.

    The thresholds are `$883C` and the net's four-point bonus is `$87A1`; both
    stay decoded whichever mode is in force.
    """
    import random

    from alien_remake.core import constants as K
    from alien_remake.core.modes import JonesCatch

    def catches(mode: JonesCatch, item_type: str, trials: int = 400) -> int:
        hits = 0
        for seed in range(trials):
            sim = Simulation(rng=random.Random(seed), jones_catch=mode)
            crew = next(c for c in sim.state.crew.values() if c.alive)
            crew.carried.clear()
            item = next(i for i in sim.state.items.values()
                        if i.type_id == item_type)
            item.room_id, item.holder = None, crew.id
            crew.carried.append(item.id)
            crew.room_id = sim.state.jones_room_id
            crew.in_duct = False
            if sim._catch_jones(crew.id):
                hits += 1
        return hits

    for item_type in ("cat_box", "net"):
        classic = catches(JonesCatch.CLASSIC, item_type)
        patient = catches(JonesCatch.PATIENT, item_type)
        assert classic == patient, (
            f"{item_type}: the added rule changed the odds "
            f"({classic} vs {patient} of 400) — it must only change how many "
            "attempts you get"
        )

    # And the net really is the better tool, as `$87A1` says.
    assert K.JONES_CATCH_NET_BONUS == 4
    assert catches(JonesCatch.PATIENT, "net") > catches(JonesCatch.PATIENT, "cat_box")
