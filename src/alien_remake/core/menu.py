"""The in-game CONTROL-panel menu model (headless, stdlib only).

This is the right-hand panel of the original's play screen (see
``docs/reference/vice-screen-2026070401*.png``): with no crew selected it is the
**CONTROL** list — "Order:" over the crew, then the deck views; selecting a crew
opens that crew's **order menu** — Move To (the room's direct connections), Use
(held item), Get Item (items in the room), Leave Item, Special (Remove Grille /
Scuttle Nostromo / Launch Narcissus / airlock), Quit.

The model is pure: :func:`control_entries` / :func:`crew_entries` turn the live
:class:`~alien_remake.core.sim.Simulation` state into a flat list of
:class:`MenuEntry` (section headers interleaved with selectable options), and
:class:`MenuController` tracks the cursor and, on *fire*, issues the entry's
:class:`~alien_remake.core.orders.Order` / Special Option to the sim or changes
the selection. The pygame backend only draws the entries and forwards up/down/
fire — no game logic there.

Corrected against the full disassembly + live captures: the original's
"move to:" list is the current room's **direct connections** — not every
reachable room. A crew member walks one connection at a time, re-issuing the
order from each room they reach. **Which** connections depends on where they
are: on the surface it is the routing-table graph, and inside a duct it is the
compass graph ([C $779C], P-5/D-086).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from .command_monitor import crew_with_alien, items_in_room
from .alien import duct_move_targets, surface_move_targets
from .crew import CARRY_CAPACITY, CrewMember
from .items import ITEM_TYPES
from .state import GameState
from .nostromo import DECK_NAMES, room_display_name
from .orders import Order, OrderType
from .special_options import SpecialOption, SpecialOptionType
from . import constants
from . import constants as _constants
from . import gamedata_snapshot as _snapshot

# **[C $5776] P2-1 — SPECIAL options are per-room.** `guard_target_alive
# ($56B4)` indexes `$5753,Y` by the acting character's *room* (`$7935,Y`) and
# treats 0 as "nothing here". The initial table is sparse — only four rooms
# carry an entry — so most rooms offer no SPECIAL at all.
SPECIAL_ROOM_SCUTTLE = "commdcentr"   # id 1: SCUTTLE NOSTROMO / OVERRIDE
SPECIAL_ROOM_AIRLOCKS = "corridor_6"  # id 2: BLOWLOCK <-> SEALLOCK, both locks
SPECIAL_ROOM_HYPERSLEEP = "cryo_vault"  # id 3: ENTER HYPERSLEEP
SPECIAL_ROOM_LAUNCH = "narcissus"     # id 5 on room 34 = NARCISSUS (D-123)
#: **[C $55A9/$55AD]** id 6 (FIGHT FIRE) is only ever written for these three
#: room indices — the engine spaces. See `constants.FIRE_ROOM_INDICES`.
FIRE_ROOM_SLUGS: frozenset[str] = frozenset(
    _snapshot.ROOM_SLUGS[i] for i in _constants.FIRE_ROOM_INDICES
)

if TYPE_CHECKING:
    from .sim import Simulation


class MenuCategory(Enum):
    """Which colour band / section an entry belongs to (drives panel colouring)."""

    HEADER = auto()     # a non-selectable section label ("CONTROL", "move to:")
    CREW = auto()       # a crew name on the CONTROL list
    DECK = auto()       # a deck view on the CONTROL list
    INDICATE = auto()   # the INDICATE LOCATION option (opens the room list)
    MOVE_TO = auto()
    USE = auto()
    GET = auto()
    LEAVE = auto()
    SPECIAL = auto()
    QUIT = auto()


@dataclass(frozen=True)
class MenuEntry:
    """One line of the panel. Non-selectable lines are section headers.

    Exactly one action field is set on a selectable entry: ``order`` /
    ``special`` issue to the sim; ``select_crew`` / ``select_deck`` change the
    view; ``back`` returns to the CONTROL list.
    """

    label: str
    category: MenuCategory
    selectable: bool = False
    order: Order | None = None
    special: SpecialOption | None = None
    select_crew: str | None = None
    select_deck: int | None = None
    indicate: bool = False            # opens the INDICATE LOCATION room list
    indicate_room: str | None = None  # a room name in that list → mark it on the map
    get_items: bool = False           # opens the GET ITEM submenu (D-145)
    indicate_page: int | None = None   # INDICATE's "other list" page flip
    back: bool = False
    #: **Not the original** — see `MenuController.turns_on`'s own comment.
    skip_turn: bool = False


def control_entries(sim: Simulation) -> list[MenuEntry]:
    """The CONTROL list shown when no crew is selected: crew to order + decks."""
    entries: list[MenuEntry] = [
        # **[C `upperdeck_0400.bin` cols 30-39] D-052:** the real panel's
        # exact wording and casing, read straight off the captured screen RAM:
        # row0 "CONTROL", row1 "Order:", rows 2-8 the crew names, rows 9-10
        # "indicate"/"location" (lowercase, wrapped over two rows because the
        # panel is only 10 columns wide), rows 11-12 "display"/"level:", rows
        # 13-15 "Upper Deck"/"Middle Deck"/"Lower Deck". The remake had these
        # as uppercase single-line labels that overflowed the panel.
        MenuEntry("CONTROL", MenuCategory.HEADER),
        MenuEntry("Order:", MenuCategory.HEADER),
    ]
    # **R-37 [C $7720], fixed 2026-07-24 (D-042): list ALL crew, including the
    # dead.** The remake used to filter `if crew.alive`, hiding them — but two
    # independent live boots showed the real "Order:" list keeps showing all
    # seven names even with a confirmed-dead member. R-37 was held open
    # pending "what does selecting a dead one actually DO?"; the answer is
    # `guard_alien_present ($7720)`, the real select-a-character handler: it
    # loads the picked index, and if that character is asleep (`$64D1,Y != 0`)
    # or incapacitated (`$7D45,Y < 2`), it draws their status and then
    # **clears the selection (`STA $64FB` = 0)** — bouncing straight back to
    # the CONTROL list without ever opening an order menu. So the entries stay
    # visible and pickable; `MenuController.fire` enforces the bounce.
    for crew in sim.state.crew.values():
        entries.append(
            MenuEntry(crew.name, MenuCategory.CREW, selectable=True, select_crew=crew.id)
        )
    # INDICATE LOCATION (live-captured, D-022): a selectable option that opens a
    # scrollable room-name list; picking a room marks its location on the map.
    # DISPLAY LEVEL heads the three deck buttons (switch which deck is shown).
    entries.append(
        MenuEntry("indicate", MenuCategory.INDICATE, selectable=True, indicate=True)
    )
    entries.append(MenuEntry("location", MenuCategory.INDICATE))  # wrapped row
    entries.append(MenuEntry("display", MenuCategory.HEADER))
    entries.append(MenuEntry("level:", MenuCategory.HEADER))
    for deck in sim.ship.decks():
        name = _deck_name(sim, deck)
        entries.append(
            MenuEntry(name, MenuCategory.DECK, selectable=True, select_deck=deck)
        )
    return entries


#: **[C $73C8/$766F] DISC-236/238 — INDICATE is TWO FIXED PAGES of 19 rows.**
#: `draw_deck_map ($73C8)` copies 19 consecutive 10-byte records out of the
#: room-name table into panel rows 0-18, and the ROM keeps two source offsets::
#:
#:     page 1  src $A712   row 0 "   quit   "   rows 1-17 rooms 0-16
#:                         row 18 "other list"  -> flip to page 2
#:     page 2  src $A7D0   row 0 "other list"   rows 1-17 rooms 17-33
#:                         row 18 "   quit   "  -> exit ($7676 CMP #$08 / BEQ)
#:
#: The cursor row becomes a room id two different ways — `$76A4` `row - 1` on
#: page 1, `$76B4` `row + 16` on page 2 — and both fall out of the single
#: source-offset difference. NARCISSUS (34) is deliberately absent: it is off
#: the deck plans entirely.
#:
#: What was here before was 34 rooms sorted **alphabetically** into one
#: scrolling list. The order, the scrolling and the count were all invented.
INDICATE_ROWS = 19
INDICATE_FIRST_ROOM_ROW, INDICATE_LAST_ROOM_ROW = 1, 17
#: `$76A4 SBC #$01` / `$76B4 ADC #$10` — the per-page row -> room id offsets.
INDICATE_PAGE_BASE: tuple[int, int] = (-1, 16)
#: The ROM's own control labels, decoded from `$A712` / `$A7C6` (both records
#: read "other list", which is why page 2's source is `$A7D0`). The quit row
#: is decoded too (`$A712`/`$A7C6` also carry "quit"), but shown as **"back"**
#: instead (owner's request, 2026-09-05): it only ever steps back one level
#: (`back=True`), same as every other "quit" row in this module, and never
#: exits anything — "quit" reads as "leave the game" to a player, which is
#: not what selecting it does.
INDICATE_LABEL_QUIT = "back"
INDICATE_LABEL_OTHER = "other list"


def indicate_entries(sim: Simulation, page: int = 0) -> list[MenuEntry]:
    """One page of the INDICATE LOCATION list — **[C $73C8] DISC-238.**

    Nineteen rows, exactly as the ROM lays them out. Rows 1-17 are rooms in
    **table order** (not alphabetical); rows 0 and 18 are the two controls,
    whichever way round this page has them.
    """
    from .gamedata_snapshot import ROOM_NAMES, ROOM_SLUGS

    base = INDICATE_PAGE_BASE[page]
    entries: list[MenuEntry] = []
    for row in range(INDICATE_ROWS):
        if INDICATE_FIRST_ROOM_ROW <= row <= INDICATE_LAST_ROOM_ROW:
            rid = row + base
            slug = ROOM_SLUGS[rid]
            entries.append(
                MenuEntry(
                    ROOM_NAMES[rid],
                    MenuCategory.INDICATE,
                    selectable=slug in sim.ship.rooms,
                    indicate_room=slug,
                )
            )
            continue
        # Rows 0 and 18: "quit" and "other list", swapped between the pages.
        quit_row = INDICATE_ROWS - 1 if page == 0 else 0
        if row == quit_row:
            entries.append(
                MenuEntry(INDICATE_LABEL_OTHER, MenuCategory.INDICATE,
                          selectable=True, indicate_page=1 - page)
            )
        else:
            entries.append(
                MenuEntry(INDICATE_LABEL_QUIT, MenuCategory.QUIT,
                          selectable=True, back=True)
            )
    return entries


def get_item_entries(sim: Simulation, crew_id: str) -> list[MenuEntry]:
    """The GET ITEM submenu (D-145): what is actually in this crew member's
    room, opened by the single "Get item" row on the main panel — the shape
    every panel in the player's own recording shows."""
    crew = sim.state.crew[crew_id]
    entries: list[MenuEntry] = [
        MenuEntry("GET ITEM:", MenuCategory.HEADER),
        # [C $A715] decoded as "quit"; shown as "back" (owner's request,
        # 2026-09-05) — see `INDICATE_LABEL_QUIT`'s own comment on why.
        MenuEntry("back", MenuCategory.QUIT, selectable=True, back=True),
    ]
    if crew.room_id is None:
        return entries
    for item in items_in_room(sim.state, crew.room_id):
        entries.append(
            MenuEntry(
                _item_label(item.type_id, sim.state, item.id),
                MenuCategory.GET,
                selectable=True,
                order=Order(crew_id, OrderType.GET_ITEM, item.id),
            )
        )
    return entries


def _deck_name(sim: Simulation, deck: int) -> str:
    return DECK_NAMES.get(deck, f"DECK {deck}")


def _reachable_move_targets(sim: Simulation, crew_id: str) -> list[str]:
    """The MOVE TO destinations — **which list depends on where they are**.

    [C $779C] P-5: the game keeps two "move to" menus and picks between them on
    the character's in-duct flag::

        779C  LDA $6501,Y
        779F  BEQ $77A7    ; on the SURFACE -> $7860, built from the ROUTING
                           ;   tables (`SURFACE_EXITS` / `door_neighbors`)
        77A4  JMP $81D7    ; IN A DUCT      -> $81EF, built from the COMPASS
                           ;   tables (`duct_exits`)

    So a crew member who has gone through a grille navigates a *different*
    graph, and that is the whole point of the ducting: it reaches rooms the
    doors do not. R-16's note that this is "the compass exits" was right about
    it being direct connections and wrong about which table (D-086).

    Only direct connections are ever offered, in either graph — a crew member
    walks one link at a time, re-issuing the order from each new room.

    **[C $7860 / $81EF] D-167, PV-02/PV-33 — this is a decoded WALK, not a
    sorted set.** The list the panel shows is built into `$7917,Y` (read back
    at `$7B4E` as `$7914,Y` because the cursor row starts at 3), and the two
    builders do **not** agree with each other:

    * **surface** (`$7860`): walk the five route tables in order; skip an entry
      equal to the *last accepted* one (`$7883 CMP $7947`); and if an entry
      equals the **current room**, `$7888 BEQ $7908` **ends the whole list** —
      later tables are never consulted.
    * **duct** (`$81EF`): walk the four compass tables; an entry equal to the
      current room is merely **skipped** (`$81F2 BEQ next`), not a terminator,
      and there is no last-accepted dedupe because each slot is labelled with
      its own direction word.

    Sorting a set got the *contents* right for 34 of 35 rooms but the **order**
    wrong for 10 of them — and order is not cosmetic here, because the cursor
    is positional.
    """
    crew = sim.state.crew[crew_id]
    if crew.room_id is None:
        return []
    if crew.in_duct:
        return list(duct_move_targets(sim.ship, crew.room_id).values())
    return surface_move_targets(sim.ship, crew.room_id)


#: **[C $8080]** the ten-character labels `$81EF` copies for each in-duct exit:
#: `$807F` NORTH, `$8093` EAST, `$8089` SOUTH, `$809D` WEST — each prefixed by
#: its own arrow glyph. Inside the ducting the menu names **directions, not
#: rooms**, which is what makes duct travel disorienting: you are told
#: which way you can go, never where it leads.
DUCT_DIRECTION_ORDER: tuple[str, ...] = ("north", "east", "south", "west")
DUCT_DIRECTION_LABELS: dict[str, str] = {
    "north": "NORTH", "east": "EAST", "south": "SOUTH", "west": "WEST",
}


def _grille_is_open(sim: Simulation, room_id: str | None) -> bool:
    """Has this room's grille been removed or burst? ([C $8676] 0 = gone)."""
    if room_id is None:
        return False
    return any(g.room_id == room_id and g.is_open for g in sim.ship.grilles)


def _move_to_entries(sim: Simulation, crew_id: str) -> list[MenuEntry]:
    """The MOVE TO block, exactly as the ROM composes it.

    Three ROM facts, all in `draw_grille_option ($86F0)` and `$81EF`:

    * **In a duct the destinations are compass words**, built by `$81EF` from
      the four compass tables, each self-reference skipped and each survivor
      labelled from the `$8080` word block — never a room name.
    * **An open grille is itself a MOVE TO entry** (`$8729` writes "GRILLE"
      to `$046E`, the MOVE TO column) — the deliberate way in and out of the
      ducting.
    * `$86F3 CPY #$22 / BEQ` — SHUTTLEBAY never offers it.
    """
    crew = sim.state.crew[crew_id]
    out: list[MenuEntry] = []
    if crew.room_id is None:
        return out
    if crew.in_duct:
        exits = sim.ship.duct_exits(crew.room_id)
        for direction in DUCT_DIRECTION_ORDER:
            dest = exits.get(direction)
            if dest is None or dest == crew.room_id:
                continue                    # `$81F2 CMP $7934 / BEQ` — no exit
            out.append(
                MenuEntry(
                    DUCT_DIRECTION_LABELS[direction],
                    MenuCategory.MOVE_TO,
                    selectable=True,
                    order=Order(crew_id, OrderType.MOVE_TO, dest),
                )
            )
    else:
        for room_id in _reachable_move_targets(sim, crew_id):
            out.append(
                MenuEntry(
                    _room_label(room_id),
                    MenuCategory.MOVE_TO,
                    selectable=True,
                    order=Order(crew_id, OrderType.MOVE_TO, room_id),
                )
            )
    if crew.room_id != SPECIAL_ROOM_LAUNCH and _grille_is_open(sim, crew.room_id):
        out.append(
            MenuEntry(
                "GRILLE",                   # [C $86BE] the 10-char record
                MenuCategory.MOVE_TO,
                selectable=True,
                order=Order(crew_id, OrderType.USE_GRILLE),
            )
        )
    return out


def has_functional_companion(sim: Simulation, crew: CrewMember) -> bool:
    """Is another *functional* crew member sharing this position? — [C $4581].

    `find_colocated_crew` scans slots 1-7 for an X other than Y that matches on
    **room** (`$7935`) and **duct state** (`$6501`), and is itself usable:
    health >= 2 (`$45AA CMP #$02 / BCC`) and composure != 0 (`$45B1 BNE`). It
    returns 8 when nobody qualifies.
    """
    for other in sim.state.crew.values():
        if other.id == crew.id:
            continue
        if other.room_id != crew.room_id or other.in_duct != crew.in_duct:
            continue
        if other.health < constants.CREW_INCAPACITATED_BELOW:
            continue
        if sim.effective_composure(other) != 0:
            return True
    return False


def can_be_commanded(sim: Simulation, crew: CrewMember) -> bool:
    """The ROM's own four-part selection gate — **[C $7720]**.

    `guard_alien_present` bounces a pick by writing `STA $64FB` = 0, and it
    does so on **four** conditions::

        773B  LDA $64D1,Y / BNE bounce   ; in hypersleep
        7740  CPY $64CC   / BEQ bounce   ; the slot `$64CC` names (android path)
        7745  LDA $7D45,Y / CMP #$02
              BCC bounce                 ; health below 2
        7757  LDA $6571,Y / BNE ok       ; composure 0 ...
        7768  JSR find_colocated_crew
              CPX #$08 / BEQ bounce      ; ...and nobody functional alongside

    The last one is the interesting one and the remake had never modelled it:
    a crew member whose composure has hit zero can still be commanded **so long
    as someone functional is in the room with them** — alone, they are lost to
    you. That is the mechanic behind a player's guess that some characters
    "start as Insane".
    """
    if not crew.awake:                                      # $773B
        return False
    if crew.id == sim.state.locked_crew_id:                 # $7740
        return False
    if crew.health < constants.CREW_INCAPACITATED_BELOW:    # $7745
        return False
    # [C $7757] `LDA $6571,Y / BNE ok` — the EFFECTIVE composure (D-151).
    if sim.effective_composure(crew) == 0 and not has_functional_companion(sim, crew):
        return False                                        # $7757 / $7768
    return True


def _get_jones_offered(sim: Simulation, crew: CrewMember) -> bool:
    """Is the "GET JONES" row on the panel? — **[C $88F4-$8927] D-160.**

    `guard_6580`'s four gates, the same ones that raise the "JONES IS HERE"
    notice and arm the cat's run::

        88F4  LDA $657D / CMP $64F7 / BNE   ; Jones in the DISPLAYED room
        88FE  LDY $64FB / BEQ               ; a character is selected
        8903  CPY #$08  / BCS               ; ...and it is a crew slot
        8907  LDA $6501,Y / BNE             ; ...on the surface, not in a duct

    The remake's displayed room is the selected crew member's room, which
    collapses the first two into "Jones is standing where this crew member
    is". Note the ROM does **not** require them to be holding a catcher — the
    option appears regardless, and `$8784`'s `$829A` test then decides whether
    the grab can do anything. Offering it empty-handed is faithful.
    """
    if sim.state.jones_caught or sim.state.jones_room_id is None:
        return False
    if not crew.alive or crew.in_duct:
        return False
    return crew.room_id == sim.state.jones_room_id


def crew_entries(sim: Simulation, crew_id: str) -> list[MenuEntry]:
    """The order menu for one crew member (the panel after selecting them)."""
    crew = sim.state.crew[crew_id]
    entries: list[MenuEntry] = [MenuEntry(crew.name, MenuCategory.HEADER)]

    # Move To: the room's direct connections (R-16; see _reachable_move_targets).
    entries.append(MenuEntry("move to:", MenuCategory.HEADER))    # [C $A898]
    entries.extend(_move_to_entries(sim, crew_id))

    # Use: the held item — its effect depends on the item. [C $4940] weapons
    # wound (see constants.ITEM_ATTACK_DAMAGE), tracker reads, extinguisher fights
    # acid damage, cat box catches Jones; the NET is message-only. (The earlier
    # "net/prod stun" comment described an invented mechanic FV-1.1 removed — there
    # is no stun. The sim dispatches on the item type; FV-1b2 audits the effects.)
    # **[C $83AF/$83C6] Both carried items are listed (DISC-261).** A crew
    # member has two carry slots and the panel has two rows for them
    # (`PANEL_SLOT_USE_FIRST/LAST` = 9 and 10, DISC-232). `list_room_items`
    # fills them from the object's own location byte::
    #
    #     83AA  CMP $8299   ; location == slot + $A0 -> row 9  ($0586), $829A
    #     83C1  CMP $7947   ; location == slot + $80 -> row 10 ($05AE), $829B
    #
    # `$829A` is the **active** slot: every action reads it (`$45EE`, `$4646`),
    # and `$4679` reaches the second item only by temporarily copying `$829B`
    # over `$829A` and restoring it afterwards. So the top row is the one in
    # hand and the row beneath it is the spare.
    #
    # The remake showed only `crew.holding` — the spare was carried but
    # invisible, and there was no way to swap to it.
    entries.append(MenuEntry("use:", MenuCategory.HEADER))        # [C $A8DF]
    for item_id in _carried_in_slot_order(crew):
        held = sim.state.items.get(item_id)
        if held is None or held.exhausted:
            continue
        active = item_id == crew.holding
        entries.append(
            MenuEntry(
                _item_label(held.type_id, sim.state, held.id),
                MenuCategory.USE,
                selectable=True,
                # Firing the top row uses the item in hand; firing the spare
                # brings it to hand instead of using it, which is the swap.
                order=Order(
                    crew_id,
                    OrderType.USE if active else OrderType.SELECT_ITEM,
                    None if active else item_id,
                ),
            )
        )

    # Get Item — **ONE row, not a list of the room's items (D-145).**
    # [C-live] Every panel in the player's recording shows a single "Get item"
    # row (e.g. "use: / Incinerotr / Get item / Leave item / Special:"), never
    # the room's contents inline; picking it opens a submenu of what is
    # actually there. This used to enumerate every item straight onto the main
    # panel, which both mis-shaped the menu and leaked the room's contents
    # before the player asked. The submenu itself is `get_item_entries`.
    if crew.room_id is not None and items_in_room(sim.state, crew.room_id):
        entries.append(
            MenuEntry(
                "Get item",
                MenuCategory.GET,
                selectable=True,
                get_items=True,
            )
        )

    # Leave Item: only if carrying something.
    if crew.holding is not None:
        entries.append(
            MenuEntry(
                "Leave item",   # [C $82B5]
                MenuCategory.LEAVE,
                selectable=True,
                order=Order(crew_id, OrderType.LEAVE_ITEM),
            )
        )

    # **[C $8860 -> $0676 / $8437] P8-3, D-160 — "GET JONES".**
    # `guard_6580 ($88CC)` writes the 10-char label `$8860` into `$0676`
    # (panel row 15, column 30) on **every pass** in which the cat is in the
    # displayed room with a surfaced crew member selected, and blanks it again
    # (`$88E8`) as soon as that stops holding. `route_command ($8437)` sends
    # that row to `$8784`. So it is a genuine, contextual panel option — the
    # same four gates as the "JONES IS HERE" notice, which is why it reuses
    # them rather than re-deriving. **PV-03 closed 2026-08-07 (D-169):**
    # `$891E LDA $64FC / BEQ $8924` also guards the write, and `$64FC` is the
    # **GET ITEM submenu open** flag - `$8573` sets it at the end of the
    # room-item list draw, `$858D` clears it on exit, and `guard_alien_present`
    # clears it again at `$7797` whenever a character is (re)selected. The two
    # share the same panel real estate, so GET JONES is simply not drawn while
    # the item list is up. The remake gets this **free**: `MenuController.
    # entries()` routes to `get_item_entries` while `getting_item` is set and
    # never reaches here, so the gate holds by construction.
    if _get_jones_offered(sim, crew):
        entries.append(
            MenuEntry(
                "GET JONES",
                MenuCategory.SPECIAL,
                selectable=True,
                order=Order(crew_id, OrderType.GET_JONES),
            )
        )

    # Special: context-sensitive ship/room actions.
    entries.append(MenuEntry("Special:", MenuCategory.HEADER))    # [C $7CE2]
    entries.extend(_special_entries(sim, crew_id))

    # [C $A715] decoded as "quit"; shown as "back" (owner's request,
    # 2026-09-05) — see `INDICATE_LABEL_QUIT`'s own comment on why.
    entries.append(MenuEntry("back", MenuCategory.QUIT, selectable=True, back=True))
    return entries


def _special_entries(sim: Simulation, crew_id: str) -> list[MenuEntry]:
    # The ROM's ten special labels live at `$57A0`/`$57B6`. Two are not rows
    # here and that is deliberate: BOARD NARCISSUS is a MOVE order to the
    # SHUTTLEBAY, not a special, and OVERRIDE DETONATION only exists once the
    # auto-destruct is running.
    #  * FIGHT FIRE — **[C $5889, D-066 2026-08-01] CORRECTED.** This note used
    #    to read "not a separate special: modelled as USE of the fire
    #    extinguisher" — that was wrong. `$5889` sits in the specials dispatch
    #    chain (right after the `CMP #$02/#$03/#$04/#$05` arms at `$5869`-
    #    `$5883`), has its own 10-char label ("Fight Fire") and its own result
    #    label ("Fire Out  ", `$5950`). Now a real Special Option. Its handler
    #    gates on `find_room_object` returning index 8-10 (the extinguisher
    #    band), so it is offered while the acting crew member's room holds one.
    #    **PV-04 closed 2026-08-07 (D-163):** the population rule IS traced —
    #    `guard_target_alive ($56C1)` reads the per-room code table `$5753,Y`,
    #    and code 3 (HYPERSLEEP) appears on exactly one room, the CRYO VAULT.
    #    The room gate below is therefore the ROM's own rule, not a stand-in.
    #  * SCUTTLE NOSTROMO / OVERRIDE DETONATION — **[C-live, corrected FV-2c
    #    2026-07-11]**: FV-1b5 wrongly flagged this "invented, direction
    #    inverted" — a live crew menu read confirmed the real two-line entry
    #    "SCUTTLE" / "NOSTROMO" really exists (the decoded specials table's
    #    "NOSTROMO" label was misread as a header, not an action name), and
    #    firing it live armed the ship + made an "Override Detonation" entry
    #    appear — confirming the real arm/cancel pair. Label corrected below;
    #    OVERRIDE DETONATION added, shown only once armed.
    # See docs/re/FAITHFULNESS.md for the full writeup.
    crew = sim.state.crew[crew_id]
    out: list[MenuEntry] = []
    room_id = crew.room_id
    # **[C $56B7] PV-04/D-163 — no `$5753`-derived special while in a DUCT.**
    # `guard_target_alive ($56B4)`, the routine that *draws* the row, opens
    # `LDY $64FB / LDA $6501,Y / BEQ $56BD` and RTSes otherwise, so a crew
    # member inside the ducting is offered none of SCUTTLE / BLOWLOCK /
    # HYPERSLEEP / LAUNCH / FIGHT FIRE. REMVGRILLE and ATTACK are drawn from a
    # different buffer (`$064E`, via `draw_grille_option $86F0` and `$8CE1`)
    # and are deliberately left outside this gate.
    in_duct = crew.in_duct

    # **[C $86F0 / $8C76, both write $064E] RemvGrille and Attack share one
    # screen cell, so the panel can never show both.** Whichever wrote last
    # wins, and that is Attack whenever the Alien is here: `$8CD9` fires as the
    # encounter starts. Listing both stacks a row the original never shows and
    # pushes everything below it down.
    #
    # ATTACK's window is `find_crew_with_alien ($8C49)` returning *this*
    # character (`$8CE1 CPY $64FB`). Three details in that scan are easy to
    # drop, and each one offers the row where the ROM shows none: `$8C56`
    # compares both duct flags (a ducted Alien engages a ducted crew member and
    # ignores one standing in the room), `$8C5B CMP #$02` skips anyone already
    # down, and the scan stops at its first match, so with two people in a room
    # only the lower-numbered one is engaged.
    # Derivation: DISCOVERIES DISC-227, DISC-246.
    attacking_here = crew_with_alien(sim.state) == crew_id
    grille_closed_here = room_id is not None and any(
        g.room_id == room_id and not g.is_open for g in sim.ship.grilles
    )
    # Remove Grille — only where the room has a (closed) grille, and only
    # when Attack isn't also claiming the row this pass.
    if grille_closed_here and not attacking_here:
        out.append(
            MenuEntry(
                # **[C $86E6] D-056:** the label decodes to "RemvGrille" —
                # exactly 10 characters, filling the 10-column panel with no
                # space. The remake's "REMV GRILLE" was 11 and overflowed.
                "RemvGrille",
                MenuCategory.SPECIAL,
                selectable=True,
                order=Order(crew_id, OrderType.REMOVE_GRILL),
            )
        )
    # Attack - **[C $8C76 -> $064E via $8CD9].** Written as the encounter
    # starts, into the same buffer the other SPECIAL rows use. The window is
    # `crew_with_alien(state) == crew_id`, computed above; see that call for the
    # three tests the ROM's scan applies.
    # Derivation: DISCOVERIES DISC-246, D-132, D-169.
    if attacking_here:
        out.append(
            MenuEntry(
                "Attack",
                MenuCategory.SPECIAL,
                selectable=True,
                order=Order(crew_id, OrderType.ATTACK),
            )
        )
    # Airlock blow/seal — **CORRECTED (D-037, 2026-07-24 de-invention audit),
    # applied to code.** The old gate (`room_id in airlock_rooms()`, i.e.
    # standing IN the airlock) had no disassembly backing and contradicted
    # D-032: the specials category-2 dispatch
    # (BLOWLOCK/SEALLOCK) is installed for room 13 (**CORRIDOR 6**) only,
    # not the airlock rooms. Confirmed by reading the handlers themselves:
    # `apply_blowlock ($5B04)` checks two independent per-airlock flags
    # (`$5751`/`$5752`) and `blowlock_vent ($5A6A)` vents a FIXED room id
    # (0 or 1, i.e. AIRLOCK 1 / AIRLOCK 2) passed in via `$5AD7` — the target
    # is never the acting crew member's own room. So this is a remote
    # control panel in CORRIDOR 6 operating on both airlocks independently,
    # matching the real menu's four labels (`BLOWLOCK.1`/`.2`,
    # `SEALLOCK.1`/`.2`, DISASSEMBLY.md §8.5) rather than one contextual
    # "this room" option.
    if room_id == SPECIAL_ROOM_AIRLOCKS and not in_duct:            # $56B7
        for airlock_id in sim.ship.airlock_rooms():
            opened = sim.state.airlocks_open.get(airlock_id, False)
            suffix = ".1" if airlock_id == "airlock_1" else ".2"
            out.append(
                MenuEntry(
                    # [C $5799+$14/$1E/$28/$32] D-057: the real 10-char
                    # records are "BlowLock.1/.2" / "SealLock.1/.2", and
                    # `guard_target_alive` picks Seal- over Blow- from that
                    # airlock's own open flag (`$5751`/`$5752`) — exactly the
                    # arm/cancel pattern modelled here.
                    ("SealLock" if opened else "BlowLock") + suffix,
                    MenuCategory.SPECIAL,
                    selectable=True,
                    special=SpecialOption(
                        SpecialOptionType.SEAL_AIRLOCK if opened else SpecialOptionType.OPEN_AIRLOCK,
                        room_id=airlock_id,
                    ),
                )
            )
    # Enter hypersleep — only while awake AND in the CRYO VAULT (FV-2.9/D-028,
    # 2026-07-11): the real handler is room-gated. `resolve_attack`'s sibling
    # specials-dispatch routine ($5839) derives its action code from a
    # per-room lookup table ($5753,Y, keyed by the acting crew's own room),
    # and only room id 15 (CRYO VAULT) maps to code 3 — the routine
    # previously mislabeled `guard_target_is_player` ($5939), which is
    # ENTER HYPERSLEEP's real handler (self-target only; sets a per-crew
    # asleep flag and moves the crew member to a location sentinel, removing
    # them from the room grid entirely — see `Simulation._set_hypersleep`).
    if crew.awake and crew.room_id == SPECIAL_ROOM_HYPERSLEEP and not in_duct:
        out.append(
            MenuEntry(
                # [C $5799+$3C/$46] D-057: two 10-char records = two rows.
                "Enter",
                MenuCategory.SPECIAL,
                selectable=True,
                special=SpecialOption(SpecialOptionType.ENTER_HYPERSLEEP, crew_id=crew_id),
            )
        )
        out.append(MenuEntry("Hypersleep", MenuCategory.SPECIAL))  # wrapped row
    # Launch the Narcissus (win route 1) — **SHUTTLEBAY only.**
    # [C $5776] the initial per-room specials table gives room 34 (SHUTTLEBAY)
    # id **5**, and `guard_target_alive ($56FF CMP #$05)` maps id 5 to the
    # "LAUNCH    " / "NARCISSUS " pair. This option used to be offered in every
    # room, which is what the player reported. [C $5799+$64/$6E] D-057: two
    # separate 10-char records, i.e. two panel rows.
    if room_id == SPECIAL_ROOM_LAUNCH and not in_duct:               # $56B7
        out.append(
            MenuEntry(
                "Launch",
                MenuCategory.SPECIAL,
                selectable=True,
                special=SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS),
            )
        )
        out.append(MenuEntry("Narcissus", MenuCategory.SPECIAL))  # wrapped row
    # FIGHT FIRE — **[C $55A9-$55B3] P2-18, corrected 2026-08-02.** This used
    # to be offered wherever an extinguisher was within reach, on the strength
    # of D-066's read of the *handler* (`$5889`). The **menu entry** is placed
    # by `damage_room_b`, which writes special id 6 into `$5753,X` only for
    # room indices `$11`-`$13` (OTHER LIST / OTHER LIST / ENGINE 1) and only
    # once that room's alarm is raised — so FIGHT FIRE belongs to a **burning
    # engine room**, not to whoever happens to hold the extinguisher. The
    # extinguisher is still needed to *do* it; that check stays in the handler,
    # where the ROM keeps it (`$4B37` charges, "EXTINGUISHER IS EMPTY" $4B5A).
    if (
        room_id is not None
        and not in_duct                                              # $56B7
        and room_id in FIRE_ROOM_SLUGS
        # **[C $5753,X] D-164** — gate on the FIRE flag itself, not on the
        # alarm. `$55B1` writes it only while the room's damage is 4..14, so a
        # room past the critical threshold never gets the option back once it
        # has been extinguished. Keying off `room_alarm` re-offered it forever.
        and sim.state.room_fire.get(room_id)
    ):
        out.append(
            MenuEntry(
                # [C $57D4 blob] the ROM's own 10-char record "Fight Fire".
                "Fight Fire",
                MenuCategory.SPECIAL,
                selectable=True,
                special=SpecialOption(SpecialOptionType.FIGHT_FIRE, crew_id=crew_id),
            )
        )

    # Scuttle Nostromo (arm) / Override Detonation (cancel) — **COMMDCENTR
    # only.** [C $5776] room 6 (COMMDCENTR) is the one room carrying id
    # **1**, and `guard_target_alive ($56C9 CMP #$01)` is what chooses between
    # the two labels: `$56CD LDA $64CF / BEQ $56DF` shows "SCUTTLE / NOSTROMO"
    # (+$00) when nothing is armed and "OVERRIDE / DETONATION" (+$78) when it
    # is — and `$56D2 LDA $657B / CMP #$05 / BCC RTS` **withdraws the override
    # once fewer than 5 of the 9 countdown units remain** (D-060). Like LAUNCH,
    # this pair used to be offered everywhere. [C-live FV-2c] confirmed the
    # arm/cancel pairing itself.
    if room_id != SPECIAL_ROOM_SCUTTLE or in_duct:                   # $56B7
        pass
    elif sim.state.auto_destruct_ticks is None:
        out.append(
            MenuEntry(
                # [C $5799+$00/$0A] D-057: "Scuttle   " / "Nostromo  ".
                "Scuttle",
                MenuCategory.SPECIAL,
                selectable=True,
                special=SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT),
            )
        )
        out.append(MenuEntry("Nostromo", MenuCategory.SPECIAL))  # wrapped row
    else:
        out.append(
            MenuEntry(
                # [C $5799+$78/$82] D-057: "Override  " / "Detonation".
                "Override",
                MenuCategory.SPECIAL,
                selectable=True,
                special=SpecialOption(SpecialOptionType.OVERRIDE_DETONATION),
            )
        )
        out.append(MenuEntry("Detonation", MenuCategory.SPECIAL))  # wrapped row
    return out


def _room_label(room_id: str) -> str:
    try:
        return room_display_name(room_id)
    except ValueError:
        return room_id.upper()


#: **[C $8874] DISC-261 — the cat box is renamed once Jones is inside.**
#: `guard_6580`'s catch path copies ten bytes from `$8874` over the item-name
#: table's type-8 entry at `$7CC3` (`$87DC`/`$8827 STA $7CC3,Y`), so the panel
#: row the player is looking at changes from "Cat Box" to this. It is the only
#: confirmation the original gives that the cat is in the box.
#:
#: That rename is also load-bearing elsewhere: `$5B33 CMP $7CC3` is the launch
#: validator's "GO GET JONES" test, which reads the *name* rather than any
#: flag. The remake keeps `state.jones_caught` as the flag and derives the
#: label from it, which is the same fact expressed the way this model holds it.
JONES_BOX_LABEL = "Jones:Box"

#: **[C $87B6]** The other one. `$87B6` copies "Jones:Net" and `$87D7`
#: "Jones:Box" - the ROM renames **whichever item made the catch**, and the net
#: catches him markedly more often than the box does (D-153).
JONES_NET_LABEL = "Jones:Net"

#: Which label each catching item takes, by type.
JONES_LABELS: dict[str, str] = {"net": JONES_NET_LABEL, "cat_box": JONES_BOX_LABEL}


def _carried_in_slot_order(crew: CrewMember) -> list[str]:
    """The crew member's carried items, **active first** (DISC-261).

    Mirrors the ROM's two slots: `$829A` (row 9) is what every action reads,
    `$829B` (row 10) is the spare. `crew.holding` is this model's `$829A`.
    """
    carried = [i for i in crew.carried]
    if crew.holding in carried:
        carried.remove(crew.holding)
        carried.insert(0, crew.holding)
    return carried[:CARRY_CAPACITY]


def _item_label(
    type_id: str,
    state: "GameState | None" = None,
    item_id: str | None = None,
) -> str:
    """The item's panel name. ``state`` and ``item_id`` matter once Jones is in.

    **Corrected 2026-08-30 (owner's playtest).** This used to rename any item of
    type `cat_box` the moment `jones_caught` went true, which was wrong twice:
    Ripley caught him with the **net** and it was *Ash's* box across the ship
    that read "Jones:Box", while the net that actually held him still read
    "Net".

    The ROM renames **the catching item** - `$87B6` copies "Jones:Net" over the
    name table and `$87D7` "Jones:Box" - and `specials.py` already records which
    one that was as `state.jones_container_id`. So the test is identity, not
    type, and the label follows the type of *that* item.

    Without an ``item_id`` the caller cannot be answered precisely, so the plain
    name is returned rather than a guess - a wrong "Jones:" on the wrong row is
    worse than no marker, because the panel is the only place the original tells
    you where the cat is.
    """
    if (
        state is not None
        and state.jones_caught
        and item_id is not None
        and item_id == state.jones_container_id
    ):
        return JONES_LABELS.get(type_id, JONES_BOX_LABEL)
    item = ITEM_TYPES.get(type_id)
    return item.name if item is not None else type_id.upper()


#: How hard a view change glitches the CRT layer, when it is not a full one.
#: Closing a submenu or flipping deck is a smaller event than changing who you
#: are commanding, and the owner asked for the deck change specifically to
#: "gently glitch" (DISC-264).
#:
#: **A hint, not a threshold.** The renderer classifies on the midpoint and
#: substitutes the CRT layer's own constants, so this number never has to equal
#: one over there. It did have to once, and the day `GLITCH_GENTLE` moved from
#: 0.35 to 0.30 every deck change silently started taking the *scramble* path
#: (DISC-268).
GENTLE_VIEW_CHANGE = 0.35


class MenuController:
    """Cursor + selection state over the panel, driving the sim on *fire*."""

    def __init__(self, sim: Simulation) -> None:
        self.sim = sim
        self.selected_crew: str | None = None
        self.cursor = 0  # index into the current menu's *selectable* entries
        # INDICATE LOCATION state (D-022): whether the room-name list is open,
        # and which room is currently indicated (highlighted on the map). The
        # latter is a render-only concern, so it lives here, not in GameState.
        self.indicating = False
        #: D-145 — the GET ITEM submenu is open (the room's item list).
        self.getting_item = False
        self.indicated_room_id: str | None = None
        #: Which INDICATE page is showing (0 or 1) — [C $64FB $10/$08].
        self.indicate_page = 0
        # **P3-1** — where the highlight sat in the CONTROL list before opening
        # a sub-menu, so backing out returns to it. The ROM keeps one cursor
        # byte (`$64E5`) that the back-out path never resets; modelling it as a
        # remembered root position gives the same observable behaviour without
        # letting a sub-menu row index leak into the crew list.
        self._root_cursor = 0
        #: **Presentation only, and deliberately not a renderer call.** The CRT
        #: layer glitches when the view changes (DISC-264), and the three view
        #: changes the owner named all happen in here. Rather than let the menu
        #: reach into the renderer, it bumps a counter and names how hard the
        #: change was; the renderer notices the epoch moved and owns the timing.
        #: The sim never sees any of it, same boundary as the debug overlay.
        self.view_epoch = 0
        self.view_epoch_strength = 0.0
        #: The room the *pointer* is over, when it is a legal destination.
        #: **M4.** Kept apart from the cursor deliberately: hovering must
        #: change the picture and nothing else (P5), and moving the cursor
        #: would change what the space bar fires -- a mouse resting on the
        #: map must not redirect the keyboard.
        self.hovered_room_id: str | None = None
        #: Set by the app when developer mode is recording; see `fire`.
        self.on_action: Callable[[str, dict[str, Any]], None] | None = None
        #: **Turn-based initiative (2026-09-05), not the original.** Set by
        #: the renderer each frame from `flow.options.values["turns"]` — the
        #: panel has no other way to know, since it is built from `sim`
        #: alone. Gates the "SKIP TURN" row in `entries()`; the disk has no
        #: turn-based mode at all, so there is nothing decoded to conflict
        #: with here.
        self.turns_on = False
        #: Set by `fire()` when the "SKIP TURN" row is chosen; read (and
        #: cleared) by `PygameRenderer.poll_skip_turn()` alongside the `K`
        #: key's own flag - two ways to ask for the same thing.
        self.skip_turn_requested = False

    def entries(self) -> list[MenuEntry]:
        """The current panel's full entry list (headers + selectables)."""
        if self.indicating:
            return indicate_entries(self.sim, self.indicate_page)
        # **[C $72EE -> $7720] D-158 — the selection gate is CONTINUOUS.**
        # `check_deferred_move` calls `guard_alien_present` on **every move
        # pass**, and its bounce (`$774F LDA #$00 / STA $64FB`) drops whoever
        # is *currently* selected, not just whoever was being picked. The
        # remake only ran `can_be_commanded` at the moment of the click, so a
        # crew member who fell asleep, collapsed to 1 health, broke while
        # alone, or was unmasked as the android **stayed commandable
        # indefinitely** — the panel kept their order menu open. Re-deriving
        # it here, where the panel is built each frame, restores the ROM's
        # cadence: the selection evaporates and you are back on the crew list.
        if self.selected_crew is not None:
            held = self.sim.state.crew.get(self.selected_crew)
            if held is None or not can_be_commanded(self.sim, held):
                self.selected_crew = None
                self.getting_item = False
                self.cursor = self._root_cursor      # $7720 never touches $64E5
        if self.selected_crew is None:
            self.getting_item = False
            return control_entries(self.sim)
        if self.getting_item:
            return get_item_entries(self.sim, self.selected_crew)
        entries = crew_entries(self.sim, self.selected_crew)
        if self.turns_on:
            # **Not the original.** In the special actions area, right above
            # "back" — the last row `crew_entries` appends — per the owner's
            # own placement request. `K` already does the same thing; this is
            # the discoverable, click-reachable form of it.
            entries.insert(
                -1,
                MenuEntry("Skip turn", MenuCategory.SPECIAL, selectable=True,
                          skip_turn=True),
            )
        return entries

    def move_destinations(self) -> dict[str, int]:
        """Legal MOVE TO rooms right now -> the entry index that orders each.

        **M2.** The map's clickable rooms are exactly this, read from the panel
        rather than re-derived from the ship graph: the panel already applies
        the surface/duct split (`$779C`), the selection gate (`$7720`) and
        whatever else decides a destination is offerable, and a second copy of
        that reasoning would be a second thing to keep in step. Empty when
        nobody is selected, which is what makes a click on the map inert then.
        """
        out: dict[str, int] = {}
        for index, entry in enumerate(self.entries()):
            order = entry.order
            if (entry.selectable and order is not None
                    and order.type is OrderType.MOVE_TO
                    and order.target is not None):
                out[order.target] = index
        return out

    @property
    def previewed_room_id(self) -> str | None:
        """The room the cursor is hovering, when it is a MOVE TO entry.

        **[C $7C3D]** While the player browses destinations the ROM keeps the
        location pointer live over the candidate room::

            7C3D  LDY $64F7 / LDA $7569,Y / STA $4BEF   ; candidate's deck
            7C46  LDY $64FB / LDA $7935,Y / TAY
            7C4D  LDA $7569,Y / CMP $4BEF
            7C53  BEQ $7C5D                             ; same deck -> place it
            7C55  LDA #$00 / STA $D002                  ; else hide it
            7C5D  LDA $758D,Y -> $D002 ; LDA $75B1,Y -> $D003
            7C6C  LDA #$01 / STA $64BE                  ; arm the animation

        So choosing where to send someone *previews* the destination with the
        same expanding-box animation INDICATE uses — and the pointer is hidden
        when the candidate is on another deck. (Note the deck test reads
        **`$7569`**, independently confirming D-116.)
        """
        idx = self.current_index()
        if idx is None:
            return None
        entry = self.entries()[idx]
        order = entry.order
        if order is None or order.type is not OrderType.MOVE_TO:
            return None
        return order.target

    def _selectable(self, entries: list[MenuEntry]) -> list[int]:
        return [i for i, e in enumerate(entries) if e.selectable]

    def current_index(self) -> int | None:
        """Index into ``entries()`` of the highlighted line, or None if none."""
        entries = self.entries()
        sel = self._selectable(entries)
        if not sel:
            return None
        self.cursor %= len(sel)
        return sel[self.cursor]

    def move(self, delta: int) -> None:
        """Move the cursor by ``delta`` selectable entries (wrapping)."""
        sel = self._selectable(self.entries())
        if sel:
            self.cursor = (self.cursor + delta) % len(sel)

    def select_index(self, entry_index: int) -> bool:
        """Put the cursor on ``entry_index`` of :meth:`entries`. **P1.**

        Absolute placement, for a pointer. The keyboard and joystick only ever
        move the cursor *relatively* (:meth:`move`), which is all the ROM's own
        cursor keys do — but a click names a row outright, and stepping towards
        it would fire the wrong row on the way.

        ``entry_index`` indexes the full list, headers included, because that is
        what a caller reading rows off the screen has. It is converted here to
        the selectable-entry index :attr:`cursor` actually holds; getting that
        conversion wrong is how a click on the fourth *line* selects the fourth
        *option* instead.

        Returns ``False`` and moves nothing for an out-of-range index or a
        non-selectable line (a section header), so a click on "CONTROL" or on
        empty panel is simply ignored rather than snapping the cursor somewhere
        arbitrary.
        """
        entries = self.entries()
        if not 0 <= entry_index < len(entries):
            return False
        if not entries[entry_index].selectable:
            return False
        selectable = self._selectable(entries)
        if entry_index not in selectable:        # defensive: kept in step
            return False
        self.cursor = selectable.index(entry_index)
        return True

    def _view_changed(self, strength: float = 1.0) -> None:
        """Note a view change for the CRT layer. ``strength`` is 0..1."""
        self.view_epoch += 1
        self.view_epoch_strength = strength

    def back(self) -> None:
        """Return to the CONTROL list (close any sub-menu / room list).

        **[C $7640-$7653] P3-1 — the cursor row is PRESERVED.** Backing out
        writes `$64FB` (the selected character) and `$64BD`, but never touches
        **`$64E5`**, the panel's cursor row — that byte is only moved by the
        cursor keys themselves (`$7474 DEC` / `$74AD INC` and their clamps). So
        the highlight stays where you left it and you carry on down the list.

        We used to reset it to 0, which meant that after commanding one crew
        member you had to re-count from the top of the panel to reach the next
        — the likeliest reason a player concludes the later names "cannot be
        selected".
        """
        # D-145: QUIT inside the GET ITEM submenu closes just that submenu and
        # returns to the crew's own order panel -- it does not deselect them.
        if self.getting_item:
            self.getting_item = False
            self.cursor = 0
            self._view_changed(GENTLE_VIEW_CHANGE)
            return
        self._view_changed()
        self.selected_crew = None
        self.indicating = False
        self.cursor = self._root_cursor

    def _select_crew(self, crew_id: str) -> None:
        """Select ``crew_id``'s own order menu — the CONTROL list's
        "select crew" row, factored out so `fire()`'s own branch and
        `select_crew_directly` (initiative's auto-select, not the original)
        share one path rather than two copies of the same guard.
        """
        crew = self.sim.state.crew.get(crew_id)
        # [C $7720] (D-042): `guard_alien_present` bounces the
        # selection straight back to the CONTROL list for a crew member
        # who is asleep (`$64D1,Y != 0`) or incapacitated/dead
        # (`$7D45,Y < 2` -> `STA $64FB` = 0) — their status is shown but
        # no order menu ever opens. So the entry stays listed and
        # pickable, but picking it is a no-op here.
        # **P2-5, threshold corrected 2026-08-02.** The gate used to be
        # `not crew.alive` (health > 0), but `$7720`'s own test is
        # `$7D45,Y < 2` — so a **COLLAPSED** crew member on 1 health cannot
        # be commanded either, not just a dead one. Same constant as the
        # endgame scan (`$5B5B CMP #$02`, D-103) and as
        # `CREW_INCAPACITATED_BELOW`.
        if crew is None or not can_be_commanded(self.sim, crew):
            # **[C $7720] P3-1 — the bounce clears the SELECTION, not the
            # cursor.** `guard_alien_present` does `STA $64FB` = 0; it never
            # touches `$64E5`, the panel's cursor row. We used to reset the
            # cursor here, which turned a dead crew member into a **trap**:
            # you land on them, get thrown back to the top of the list, and
            # can never reach anyone below them. Since the opening victim
            # sits early in the roster, that made most of the crew
            # unreachable — exactly the reported "ASH, LAMBERT and BRETT
            # couldn't be selected". The highlight now stays put.
            return
        self._root_cursor = self.cursor      # P3-1: come back here
        self._view_changed()
        self.selected_crew = crew_id
        self.cursor = 0
        # Selecting a crew member switches the map to the deck they're on
        # (the original does this so you immediately see them).
        if crew.room_id is not None:
            room = self.sim.ship.rooms.get(crew.room_id)
            if room is not None:
                self.sim.select_deck(room.deck)   # already glitched above

    def select_crew_directly(self, crew_id: str) -> None:
        """**Not the original.** Open ``crew_id``'s own order menu the same
        way picking their CONTROL-list row would, without requiring the
        player's cursor to already be on it.

        Initiative's own use for this (`app.run_app`): the disk has no
        turn-based mode at all, so it certainly has no notion of the CONTROL
        panel following whose turn it is — but a player who has to manually
        re-navigate to the next actor every turn is fighting the feature, not
        playing it, so the panel jumps to them the same way choosing their
        row would.
        """
        self._select_crew(crew_id)

    def fire(self) -> None:
        """Activate the highlighted entry: order, special, or change selection."""
        idx = self.current_index()
        if idx is None:
            return
        entry = self.entries()[idx]
        # Developer-mode journal hook. A callback, not a writer: the panel and
        # the simulation stay free of file I/O, exactly as `on_options_saved`
        # does for settings. By the next tick an order leaves no trace but a
        # changed countdown, so what the player *chose* has to be caught here.
        if self.on_action is not None:
            self.on_action("action", {
                "label": entry.label,
                "selected": self.selected_crew,
                "order": (
                    {"type": entry.order.type.name, "target": entry.order.target}
                    if entry.order is not None else None
                ),
                "special": (
                    {"type": entry.special.type.name,
                     "room": entry.special.room_id}
                    if entry.special is not None else None
                ),
                "select_crew": entry.select_crew,
                "tick": self.sim.state.tick,
            })
        if entry.get_items:
            # D-145: open the GET ITEM submenu (the room's own item list).
            self.getting_item = True
            self.cursor = 0
        elif entry.indicate:
            # Open the INDICATE LOCATION room list (D-022).
            self._root_cursor = self.cursor      # P3-1
            self._view_changed()
            self.indicating = True
            self.indicate_page = 0
            self.cursor = 0
        elif entry.indicate_page is not None:
            # **[C $766F-$7697] DISC-238** — "other list" swaps the source
            # offset and redraws the same nineteen rows; it does not scroll.
            self.indicate_page = entry.indicate_page
            self.cursor = 0
        elif entry.indicate_room is not None:
            # Indicate this room: mark it (`$64F7`) and switch the map to its
            # deck. **The list stays open** - measured on the running game, where
            # choosing a room leaves `$64FB` at 16 and the nineteen room rows
            # still on screen, so you can indicate several in a row. Leave via
            # QUIT on row 0. Derivation: DISCOVERIES DISC-272.
            self.indicated_room_id = entry.indicate_room
            room = self.sim.ship.rooms.get(entry.indicate_room)
            if room is not None:
                # Indicating a room on another deck *is* a deck change: the map
                # jumps a floor. It was the one such path with no glitch on it
                # (DISC-268).
                if room.deck != self.sim.state.deck:
                    self._view_changed(GENTLE_VIEW_CHANGE)
                self.sim.select_deck(room.deck)
        elif entry.select_crew is not None:
            self._select_crew(entry.select_crew)
        elif entry.select_deck is not None:
            if entry.select_deck != self.sim.state.deck:
                self._view_changed(GENTLE_VIEW_CHANGE)
            self.sim.select_deck(entry.select_deck)
        elif entry.back:
            self.back()
        elif entry.skip_turn:
            # **Not the original.** Flagged, not acted on here: `app.py` owns
            # ending the actor's turn and auto-selecting the next one, the
            # same as it does for the `K` key — this only says "asked for."
            self.skip_turn_requested = True
        elif entry.order is not None:
            # **issuing an order does NOT deselect the character.**
            # Nothing on the ROM's order path writes `$64FB`: the item handler
            # ends `$8460 JSR compute_action_delay / LDA #$01 / STA $650C,Y /
            # RTS`, and the only routine that clears the selected slot is
            # `reset_alien_turn ($83FD)`, reached from the Alien's own turn —
            # not from a player order. So the panel stays on that crew member
            # and you can issue several commands in a row. We used to drop back
            # to the CONTROL list after every single one.
            self.sim.queue_order(entry.order)
            # D-145: picking an item inside the GET ITEM submenu closes it,
            # back to the crew's own order panel (the item is now taken, so
            # the submenu's list is stale either way).
            self.getting_item = False
            self.cursor = 0
        elif entry.special is not None:
            self.sim.apply_special_option(entry.special)
            self.cursor = 0
