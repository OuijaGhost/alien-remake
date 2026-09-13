"""The order pipeline: a player command, from the panel to the world.

Split out of the 1,980-line `sim.py` (DISC-196). One order's life:

    queue_order()      the panel hands us an Order; it overwrites any pending
                       one for that crew member and arms their turn timer
    _process_orders()  each tick, whoever is due gets one step
    _apply_order()     dispatch on verb: MOVE / USE / GET / ATTACK / ...
    _resolve_*()       the verb's own rules

Two things worth knowing before editing here:

- **An order is a standing intention, not an action.** MOVE re-runs one room per
  turn until it arrives, re-arming the crew member's timer each step. Collapsing
  that into a single event at click time is the mistake this project has made
  most often.
- **Orders can be silently dropped.** The android ignores them, and a panicking
  or incapacitated crew member never reaches the dispatch. Both are ROM
  behaviour, not bugs.
"""

from __future__ import annotations

import random
from collections import deque

from .. import constants, gamedata_snapshot
from ..alien import (
    JONES_ROLL_SIDES,
    add_room_damage,
    advance_alien,
    jones_dest,
    panic_dest,
    resolve_attack,
    restore_stowed_char,
    spawn_alien,
    tracker_zone,
    weapon_would_breach,
)
from ..constants import (
    AUTO_DESTRUCT_OVERRIDE_ABOVE,
    AUTO_DESTRUCT_SUBTICKS,
    AUTO_DESTRUCT_TICKS,
    CROWD_THRESHOLD,
    FEAR_BUMP_CORPSE,
    FEAR_BUMP_CROWDED,
    HULL_BREACH_THRESHOLD,
    ITEM_DESTROYED_ON_ATTACK,
    ROOM_CAPACITY,
    ROOM_DAMAGE_PER_ATTACK,
    ROOM_DAMAGE_PER_ATTACK_HARPOON,
)
from ..crew import (
    CARRY_CAPACITY,
    CrewMember,
    assign_start_rooms,
    default_crew,
    morale_word,
)
from ..items import spawn_items
from ..map import Direction, ShipMap, move_cursor, shortest_room_path
from ..modes import DeathVariant, GameMode, choose_android, choose_opening_death
from ..nostromo import nostromo_ship
from ..sound import (
    AIRLOCK,
    ATTACK_ALERT,
    GRILLE,
    MOVEMENT,
    TRACKER_ALARM,
    SoundCue,
)
from ..orders import (
    SURVIVING_OUTCOMES,
    Order,
    OrderOutcome,
    OrderType,
)
from ..special_options import SpecialOption, SpecialOptionType
from ..state import GamePhase, GameState, WinRoute
from .protocol import SimulationState


class OrderMixin(SimulationState):
    """`Simulation`'s order pipeline. Mixed in by `sim/__init__.py`."""

    def queue_order(self, order: Order) -> None:
        """Accept a player order — **[C $7B02-$7B69] D-168/PV-34.**

        Two things the ROM does that a queue does not. Issuing an order
        **overwrites** whatever that character had pending — `$7B02` zeroes
        both `$650C,Y` (the action code) and `$64EE,Y` (the clock) before the
        new action is armed, so there is exactly one pending action per
        character and re-ordering restarts the countdown. And the clock is
        armed **here**, at issue time (`$7B69 LDA #$40 / STA $64EE,Y / JSR
        compute_action_delay`), not lazily when the order is first serviced.

        The remake's `_orders` list could hold several live orders for the
        same character at once, which is how two conflicting MOVE_TOs ended up
        racing each other.
        """
        crew = self.state.crew.get(order.crew_id)
        # $7B02: drop any pending action for this character first.
        keep = [o for o in self._orders if o.crew_id != order.crew_id]
        self._orders.clear()
        self._orders.extend(keep)
        self._orders.append(order)
        if crew is not None:
            crew.step_timer = (                                   # $7B69
                self._action_base_ticks(order, crew)
                + self._action_delay_for(crew)                    # $7B6E
            )
    @property
    def pending_orders(self) -> int:
        """How many queued orders are awaiting a (further) tick."""
        return len(self._orders)
    # --- order processing (PCS) --------------------------------------------
    def _apply_order(self, order: Order) -> OrderOutcome:
        """Apply an *obeyed* order to the world; return the resulting outcome.

        Only called once the PCS gate says OBEY. ``MOVE_TO`` steps one room along
        the shortest room path (GAME_SPEC §3) and stays queued until it arrives;
        ``REMOVE_GRILL`` opens the grille(s) in the crew's room; ``GET_ITEM``/
        ``LEAVE_ITEM`` move an :class:`~alien_remake.core.items.ItemInstance`
        between a room and the crew's hand (GAME_SPEC §10); ``ATTACK``
        resolves combat against the Alien (see ``_resolve_attack_order``).
        """
        crew = self.state.crew[order.crew_id]
        if crew.room_id is None:
            return OrderOutcome.BLOCKED
        if self._android_ignores_order(crew):
            # [C $5294-$5299] D-080b: the pending action is zeroed and skipped.
            # No message and no refusal — the order simply evaporates, which is
            # what a player experiences as "it stopped responding to my input".
            return OrderOutcome.BLOCKED

        if order.type is OrderType.MOVE_TO:
            assert order.target is not None  # INVALID-checked upstream
            if crew.room_id == order.target:
                crew.in_duct = False
                crew.step_timer = 0
                return OrderOutcome.COMPLETED
            # **[C $779C] P-5 — which graph the step uses depends on where the
            # crew member is.** The game offers only *direct* connections, from
            # the routing graph on the surface (`$7860`) or the compass graph
            # inside a duct (`$81EF`). A duct step is additionally gated on the
            # room's grille being open — that is what REMVGRILLE is for.
            duct_step = self._duct_step_target(crew, order.target)
            if duct_step is not None:
                next_room = duct_step
                path = [crew.room_id, next_room]
            else:
                walk = shortest_room_path(self.ship, crew.room_id, order.target)
                if walk is None or len(walk) < 2:
                    crew.step_timer = 0
                    return OrderOutcome.BLOCKED
                path, next_room = walk, walk[1]
            # Room capacity (R-16b, D-018): if the next room already holds
            # ROOM_CAPACITY others, wait here rather than entering — no walk
            # progress until a slot frees.
            if self._room_occupants(next_room, exclude=crew.id) >= ROOM_CAPACITY:
                return OrderOutcome.IN_TRANSIT
            # **[C $7B69] P3-2 — the real room-move duration.** The move
            # handler loads a flat `#$40` (64) into `$64EE,Y` and *then* calls
            # `compute_action_delay`, which ADDS the per-slot and per-health
            # terms. Healthy that is ~71 ticks (~9 s at 7.886 Hz); on 2 health
            # it is ~119 (~15 s). This used to use the `$6586` table alone
            # (3-4 ticks, half a second) — about 18x too fast, which is why
            # movement read as instant.
            # **D-168/PV-34** — the countdown is not run here any more. It is
            # armed by `queue_order` (`$7B69`) and decremented once per pass by
            # `_pump_characters` (`$7226`), so a move, a panic roll and the
            # android's turn all read the same `$64EE,Y`. A direct
            # `_apply_order` call with a zero clock acts immediately, which is
            # what the unit tests want.
            if crew.step_timer > 0:
                return OrderOutcome.IN_TRANSIT
            # **[C, D-083] the duct step.** A step between two rooms with no
            # door between them went through the ducts — the ROM's per-character
            # `$6501,Y` flag, surfaced by `place_selected_char_sprite ($6667)`,
            # which colours the portrait from exactly this flag.
            #
            # D-083 replaces the old "room -> junction -> ... -> room" guess:
            # the original's ducts join **rooms directly** via four compass
            # tables (`ShipMap.duct_exits`), and a move is a duct move exactly
            # when the destination is a duct neighbour rather than a door one.
            # The ROM marks such a destination by setting bit 7 on it and then
            # `$7373 SBC #$80 / STA $7935,Y / LDA #$01 / STA $6501,Y`.
            # P2-2: `in_duct` is no longer *derived* from the step. A duct
            # step is only offered to someone already inside (see
            # `_duct_step_target`), and getting in or out is `_use_grille`.
            crew.room_id = next_room
            if crew.room_id == order.target:
                return OrderOutcome.COMPLETED
            # Not there yet: re-arm for the next leg. `resolve_char_move` does
            # the same (`$5193 STA $64E6,Y` then `$519B LDA #$28 / STA
            # $64EE,Y`) — one link per action, never a free multi-room walk.
            crew.step_timer = (
                constants.MOVE_ACTION_TICKS + self._action_delay_for(crew)
            )
            return OrderOutcome.IN_TRANSIT

        if order.type is OrderType.GET_JONES:
            # [C $8784] P8-3/D-160. The menu layer only offers this row when
            # `guard_6580`'s gates pass, which is the remake's analogue of
            # `$8787 CMP #$A0` (the option actually being on screen).
            return (
                OrderOutcome.COMPLETED if self._catch_jones(crew.id)
                else OrderOutcome.BLOCKED      # a missed roll costs the attempt
            )

        if order.type is OrderType.USE_GRILLE:
            # [C $86F0/$8729] P2-2: crossing an already-open grille, chosen
            # from the MOVE TO column. Never implicit.
            return self._use_grille(crew)

        if order.type is OrderType.REMOVE_GRILL:
            opened = [
                g for g in self.ship.grilles if g.room_id == crew.room_id
            ]
            if not opened:
                crew.step_timer = 0
                return OrderOutcome.BLOCKED
            # **[C $845A-$8465] D-166 — it is not instant; it is the SLOWEST
            # action in the game.** The handler loads the per-character table
            # `$403A,Y` into `$64EE,Y` and adds `compute_action_delay` on top,
            # exactly as the move does with its flat `#$40`. That is 80 passes
            # (~10 s) for Parker or Brett and **180 (~23 s)** for Ripley or
            # Lambert, before the health term. The remake opened the grille on
            # the same tick the order was issued, which removed both the
            # commitment and the characterisation.
            if crew.step_timer > 0:                     # D-168: pumped, not
                return OrderOutcome.IN_TRANSIT          #   self-decremented
            for g in opened:
                g.is_open = True
            return OrderOutcome.COMPLETED

        if order.type is OrderType.GET_ITEM:
            assert order.target is not None  # INVALID-checked upstream
            item = self.state.items.get(order.target)
            if item is None or item.holder is not None or item.room_id != crew.room_id:
                return OrderOutcome.BLOCKED
            # [C $829A/$829B] P2-16: two hands, and no more.
            if len(crew.carried) >= CARRY_CAPACITY:
                return OrderOutcome.BLOCKED
            item.room_id = None
            item.holder = crew.id
            crew.carried.append(item.id)
            self._apply_item_composure(crew, item.type_id, +1)   # $45B9 = 2
            self._charge_action_delay(crew)      # [C $8460]
            return OrderOutcome.COMPLETED

        if order.type is OrderType.LEAVE_ITEM:
            # **[C $8512] P2-16 — LIFO.** `LDY $829B / CPY #$FF / BEQ $8527`
            # tries one specific slot *first* and only falls back to the other
            # when it is empty, so the two carried items do not come off in
            # pickup order. Play confirms which way round: pick up the
            # incinerator then the tracker and it is the **tracker** — the most
            # recent — that is put down first.
            if not crew.carried:
                return OrderOutcome.BLOCKED
            item = self.state.items.get(crew.carried.pop())
            if item is not None:
                item.holder = None
                item.room_id = crew.room_id
                self._apply_item_composure(crew, item.type_id, -1)  # $45B9 = 3
            self._charge_action_delay(crew)      # [C $8460]
            return OrderOutcome.COMPLETED

        if order.type is OrderType.ATTACK:
            outcome = self._resolve_attack_order(crew.id, crew.room_id)
            self._charge_action_delay(crew)      # [C $48FC]
            return outcome

        if order.type is OrderType.USE:
            outcome = self._resolve_use_order(crew, crew.room_id)
            self._charge_action_delay(crew)      # [C $7B6E]
            return outcome

        if order.type is OrderType.SELECT_ITEM:
            # **[C $829A/$829B] Bring the spare to hand (DISC-261).** The ROM
            # keeps two carry slots and every action reads the first; `$4679`
            # reaches the second only by copying `$829B` over `$829A`. Choosing
            # the lower panel row does that copy permanently.
            #
            # No action delay: this is a change of grip, not a turn. Charging
            # for it would make carrying two items strictly worse than one.
            if order.target is None or order.target not in crew.carried:
                return OrderOutcome.BLOCKED
            crew.holding = order.target
            return OrderOutcome.COMPLETED

        raise AssertionError(f"unhandled order type: {order.type}")  # pragma: no cover
    def _resolve_use_order(self, crew: CrewMember, room_id: str) -> OrderOutcome:
        """Resolve a ``USE`` of the held item — the effect depends on the item.

        FV-1.5 provenance (docs/re/FAITHFULNESS.md): the utility effects are the
        modelled ones — the **tracker** takes a reading (its precision is `[?]`),
        the **extinguisher** fights the room's acid/fire damage (amount `[?]`),
        the **cat box** catches Jones. There is **no "stun"** — the earlier "net /
        electric prod stun it" comment described a mechanic FV-1.1 removed.

        **D-033 (2026-07-24), resolves the old "USE-vs-ATTACK for weapons is
        `[?]`" note:** tracing `sub_char_special ($8749)`'s default branch (any
        pending action that isn't the grille-open or `$5439` cases) leads
        straight into `$4911`→`resolve_attack ($4940)` — there is only **one**
        combat/item-effect dispatcher in the ROM, reached the same way whether
        the queued action came from ATTACK or a weapon-like USE. So the fallback
        below is confirmed correct, not a guess: net/spanner/thermlance/the
        weapons really do attack when "used". The **net is not message-only** —
        it entangles the Alien (delays its move timer) and is consumed, same
        real effect whether reached via USE or ATTACK (`constants.
        ALIEN_NET_ENTANGLE_TICKS`, `alien.resolve_attack`). The tracker's own
        smash-on-attack (+1 wound, destroyed) only fires via the literal ATTACK
        order, since USE routes tracker to `_use_tracker`'s scan instead — that
        split is real too (the ROM's scan and smash are different code paths).
        Charge-based items (extinguisher `$4B37`=3, laser=10) spend one charge
        on a successful use and jam once exhausted ("…IS EXAUSTED/EMPTY").
        """
        item = self.state.items.get(crew.holding) if crew.holding is not None else None
        if item is None:
            return OrderOutcome.BLOCKED
        if item.exhausted:
            # **[C $4B57/$4B94] "...IS EXAUSTED/EMPTY" - the ROM's own message
            # for a charge-based item run dry.** Only reachable via USE today;
            # the literal ATTACK order does not check charges at all (a
            # separate, already-filed gap - see `resolve_attack`'s docstring).
            if item.type_id == "fire_extng":
                self._post_notice(
                    constants.NOTICE_EXTINGUISHER_EMPTY.format(name=crew.name)
                )
            elif item.type_id == "laser_pist":
                self._post_notice(
                    constants.NOTICE_LASER_EXHAUSTED.format(name=crew.name)
                )
            return OrderOutcome.BLOCKED
        t = item.type_id
        # **[C $8787] D-153 — a catcher used where Jones is tries the catch.**
        # `$879A CMP #$10` (the NET) and `$87C9 CMP #$11` (the CAT BOX) are
        # both accepted, so the net has two jobs: it catches the cat here, and
        # still entangles the Alien through the ordinary attack path below
        # when Jones is not the thing in front of you (D-033). Routing the net
        # straight to `_resolve_attack_order` meant it could never catch him.
        # **P8-3/D-160 (2026-08-07): the USE shortcut is GONE.** D-153 routed a
        # net/box USE where Jones stands into `_catch_jones`. `$8784` is not
        # reachable from USE at all — `route_command ($8437)` reaches it from
        # **panel row 15**, and its own `LDA $0676 / CMP #$A0` gate means the
        # option has to be on screen. USE of either item goes where every other
        # item goes, `resolve_attack ($4940)`. The catch now lives on
        # `OrderType.GET_JONES`.
        if t == "tracker":
            outcome = self._use_tracker(crew.id)
        elif t == "fire_extng":
            outcome = self._use_extinguisher(room_id)
        else:
            # Any other item (weapons + net/spanner/thermlance) attacks — D-033
            # confirms USE and ATTACK share the same ROM dispatcher for these,
            # not a guess. Damage/effect is deterministic per item
            # (constants.ITEM_ATTACK_DAMAGE / ALIEN_NET_ENTANGLE_TICKS).
            outcome = self._resolve_attack_order(crew.id, room_id)
        # Spend a charge only on a use that actually took effect.
        if item.uses_left is not None and outcome is OrderOutcome.COMPLETED:
            item.uses_left = max(0, item.uses_left - 1)
        return outcome
    def _tracker_detects(self, holder: CrewMember) -> bool:
        """Does a tracker held by ``holder`` read anything? — **[C $8D71,
        $8F0B, $8F1B] D-150.**

        The range is `alien.tracker_zone`: the holder's own room plus its
        five route-table neighbours (`$6565..$656A`). Within that zone the
        ROM applies two different rules, and the distinction is the whole
        point of the device:

        * **The holder's own room** (`X == 0`, `$8F2D-$8F3B`) only reads a
          character who is **inside a duct** (`$6501,Y != 0`) and alive — you
          can already see anyone standing next to you, so only something in
          the walls registers.
        * **A neighbouring room** (`X != 0`, `$8F3E-$8F50`) reads a character
          who is **on the surface**, alive, and whose room genuinely differs
          from the holder's.

        The loop runs slots 0-7, and slot 0 is the **Alien** — so the same
        scan covers the creature and the crew with no special case. Jones is
        checked separately first (`$8DDC LDX #$01` -> `$8F0B`), starting at
        index **1**, i.e. the five neighbours only and never the holder's own
        room, and gated on `$6580` (the cat being loose at all).

        This replaces the old ship-wide "is anything anywhere else?" test,
        which had been an explicit `[?]` placeholder and made the tracker
        read positive essentially always.
        """
        room = holder.room_id
        if room is None:
            return False
        zone = tracker_zone(room)
        if not zone:
            # Synthetic test maps aren't in the ROM's route tables; fall back
            # to the ship's own direct connections so the zone rule still
            # applies (same spirit as `_room_marker_px`'s grid fallback).
            zone = [room] + list(self.ship.door_neighbors(room))
        neighbours = zone[1:]

        # Jones first ($8F0B, X = 1..5: neighbours only).
        if (
            not self.state.jones_caught
            and self.state.jones_room_id is not None
            and self.state.jones_room_id in neighbours
        ):
            return True

        # Then every character slot; slot 0 is the Alien ($8F1B).
        actors: list[tuple[str | None, bool, bool]] = []
        alien = self.state.alien
        if alien is not None:
            actors.append((alien.room_id, getattr(alien, "in_duct", False),
                           alien.alive))
        for crew in self.state.crew.values():
            if crew.id == holder.id:
                continue
            actors.append((crew.room_id, crew.in_duct, crew.alive))

        for actor_room, in_duct, alive in actors:
            if actor_room is None or not alive:
                continue
            if actor_room == room:
                if in_duct:                      # $8F31: same room, in a duct
                    return True
                continue
            if not in_duct and actor_room in neighbours:   # $8F3E: adjacent
                return True
        return False
    def _scan_trackers(self) -> None:
        """Re-arm or silence the tracker alarm — **[C $72F9/$72FC] D-150.**

        `reset_attack_state ($8C80)` **clears `$64B6`** and `check_6562
        ($8E32)` immediately re-arms it, back to back on every move pass. So
        the alarm is not an event that fires and lingers: it is a **latch
        recomputed from scratch**, armed only while a tracker is actually
        *held* (`resolve_char_display_loc` returns false for an item whose
        location byte is a room rather than `$A0 + slot`) and something is in
        range. Putting the tracker down therefore silences it on the next
        pass — the player's report that it kept tracking after being dropped
        was this recomputation missing.
        """
        armed = False
        for crew in self.state.crew.values():
            if not crew.alive:
                continue
            item = (
                self.state.items.get(crew.holding)
                if crew.holding is not None else None
            )
            if item is None or item.type_id != "tracker":
                continue
            if self._tracker_detects(crew):
                armed = True
                break
        self.state.tracker_alarm = armed
    def _use_tracker(self, user_id: str | None = None) -> OrderOutcome:
        """An explicit USE of a held tracker — the same scan, on demand.

        **D-129** established the tracker needs no USE order to work (the
        alarm is armed passively by `check_6562` whenever a move resolves);
        **D-150** replaces this routine's old ship-wide test with the ROM's
        real zone rule (`_tracker_detects`). Kept because USE remains a valid
        order for the item, and the ROM's own scan is what it should run.
        """
        user = self.state.crew.get(user_id) if user_id is not None else None
        if user is None:
            self.state.tracker_alarm = False
            return OrderOutcome.BLOCKED
        self.state.tracker_alarm = self._tracker_detects(user)
        return OrderOutcome.COMPLETED
    def _use_extinguisher(self, room_id: str) -> OrderOutcome:
        """Fire extinguisher: silence the room's damage alarm. **It does NOT repair.**

        **CORRECTED 2026-07-24 (D-044); the old behaviour was an invention.**
        It did `room_damage -= EXTINGUISHER_REPAIR`, i.e. repaired the ship.
        The real FIGHT FIRE handler (`$5889`, the ROM's only extinguisher
        code path) **never touches `$653F`** — the structural-damage
        accumulator — at all. Its only state writes are `$651C,X = 0` (the
        per-room damage *alarm stage*), `$5753,X = 0` (remove the special
        from the menu) and `$64D0 = 0`, then it prints "FIRE OUT" (`$5950`).

        And `damage_room_b ($5587)` only re-raises the alarm when
        `$651C,X == 0` **and** the raw damage is still `>= 4` — which it
        always is, because `$653F` only ever grows. So:

        * a room's structural damage is **permanent**; nothing in the game
          ever reduces it, and enough of it still breaches the hull;
        * the extinguisher is **recurring alarm-silencing**, not a repair —
          the alarm simply comes back on the next damage tick.

        Modelled with a real `state.room_alarm` latch (the `$651C` stage)
        instead of deriving the warning from `room_damage`.
        """
        damage = self.state.room_damage.get(room_id, 0)
        if damage <= 0 or not self.state.room_alarm.get(room_id):
            return OrderOutcome.BLOCKED  # no active fire/alarm to fight
        # `$58CA-$58D2`: STA $651C,X = 0 (alarm cleared) — and *only* that.
        # `room_damage` is deliberately left untouched.
        self.state.room_alarm[room_id] = 0
        return OrderOutcome.COMPLETED
    def _resolve_attack_order(self, crew_id: str, room_id: str) -> OrderOutcome:
        """Resolve an obeyed ``ATTACK`` (GAME_SPEC §5) against the Alien.

        Needs the Alien present in the crew member's room. FV-1.6 [C $4940]:
        damage is **deterministic per item** (``constants.ITEM_ATTACK_DAMAGE``) —
        there is no hit chance. The order outcome is always ``COMPLETED`` (the
        attempt was made) whether or not the item actually wounds. A kill in an
        *open* airlock room blasts the Alien out (win route 3); anywhere else
        it's a plain kill (win route 2).

        D-033: the net (entangle, no wound) and the tracker (+1 wound) are both
        **consumed outright** by this specific use (`clear_object_at_loc2` in the
        ROM, `constants.ITEM_DESTROYED_ON_ATTACK` here) — the item instance is
        removed from the world, not merely charge-decremented.
        """
        alien = self.state.alien
        if alien is None or not alien.alive or alien.room_id != room_id:
            return OrderOutcome.BLOCKED
        crew = self.state.crew[crew_id]
        item = self.state.items.get(crew.holding) if crew.holding is not None else None
        item_type_id = item.type_id if item is not None else None
        result = resolve_attack(
            alien, item_type_id,
            damage_to_kill=(
                constants.UPDATED_ALIEN_DAMAGE_TO_KILL
                if self.weapon_breach_gates else constants.ALIEN_DAMAGE_TO_KILL
            ),
        )
        # **[C $4940/$4BE0, full disassembly §8.8] resolve_attack's own
        # banner - nothing showed this before now, a completed attack was a
        # state change nobody saw.** The ROM prints "HITS ALIEN" and then,
        # for the two destroyed-on-attack items, a second line naming what
        # broke (`$4B22`/`$4B1E`) - real sequential banners on real hardware.
        # The remake shows one row-24 line at a time (`_post_notice` simply
        # overwrites), so the more specific line wins where there is one.
        notice = constants.NOTICE_HITS_ALIEN
        if item is not None and item_type_id in ITEM_DESTROYED_ON_ATTACK:
            del self.state.items[item.id]
            crew.holding = None
            if item_type_id == "tracker":
                notice = constants.NOTICE_TRACKER_SMASHED
            elif item_type_id == "net":
                notice = constants.NOTICE_NET_USED
        self._post_notice(notice.format(name=crew.name))
        # Acid blood: a landed hit spills acid + firefight damage into the room
        # (full disassembly §8.6 — this is why shooting the Alien wrecks a room).
        # FV-2.6/D-027: the harpoon hits much harder than any other weapon here
        # too (+15 vs +6) — real per-item ROM behaviour, not a guess.
        if result.hit:
            amount = (
                ROOM_DAMAGE_PER_ATTACK_HARPOON
                if item_type_id == "harpn_gun"
                else ROOM_DAMAGE_PER_ATTACK
            )
            # **[C $4A87 / $4AF0] The ROM's PRE-ADD breach gate.** DEC-044:
            # ORIGINAL never applies this — `self.weapon_breach_gates` is
            # False there, so a landed hit always just adds, exactly the gap
            # DISC-258 recorded. UPDATED turns it on, retuned (DEC-044) so
            # the numbers that made DISC-289's sweep unwinnable no longer
            # apply here: a landed hit reads the room's *current* damage
            # first (`weapon_would_breach`, shared with `app.py`'s DEC-045
            # retreat-is-free check) and — like the ROM's own `JMP
            # hull_breach` — ends the game outright if it is already at/past
            # the gate, rather than adding and waiting for the general
            # post-add equality check in `advance()` to notice on some later
            # tick.
            if (self.weapon_breach_gates
                    and weapon_would_breach(self.state, room_id, item_type_id)):
                self._hull_breach()
            else:
                add_room_damage(self.state, room_id, amount)
        if result.killed:
            room = self.ship.rooms.get(room_id)
            airlocked = bool(
                room is not None
                and room.is_airlock
                and self.state.airlocks_open.get(room_id, False)
            )
            self.state.win_route = (
                WinRoute.ALIEN_AIRLOCKED if airlocked else WinRoute.ALIEN_KILLED
            )
            self.state.phase = GamePhase.WON
        return OrderOutcome.COMPLETED
    def _action_delay_for(self, crew: CrewMember) -> int:
        """`compute_action_delay ($4042)`'s value for this crew member."""
        return constants.action_delay(self._slot_of(crew), crew.health)
    def _apply_item_composure(
        self, crew: CrewMember, type_id: str, sign: int
    ) -> None:
        """Gaining or losing a weapon moves composure - **[C $45E7] D-181.**

        `scripted_event_check` fires on the *transition*: event code 2 when the
        held item changes (`$85B1`) and 3 when it is lost (`$4690`/`$8530`).
        It indexes `$45D3` by the item and either INCs once (`$4665`, effect 0)
        or twice (`$466B` jumping back to `$4662`, effect 1) - mirrored by
        `$4622`/`$4639` on the losing side. So the better the weapon, the more
        it steadies you, and the worse it feels to put down.

        The tracker, net and cat box are exempt (`$45D3` = `$FF`): `$45FD`
        routes the two tracker instances to their `$656E`/`$656F` bookkeeping
        instead, and the other two fall straight to an `RTS`.
        """
        delta = constants.ITEM_COMPOSURE.get(type_id)
        if delta:
            crew.bump_fear(sign * delta)
    def _charge_action_delay(self, crew: CrewMember) -> None:
        """Make the character busy after acting — **[C $4042] P2-7**.

        `compute_action_delay` runs before ATTACK (`$48FC`), USE (`$7B6E`) and
        GET/LEAVE ITEM (`$8460`), and **adds** its result to the character's
        own countdown rather than replacing it. The health term dominates: on
        2 health it is **+48 ticks** (~6 s at the measured main-loop rate), on
        3 it is +16, and from 4 up it is nothing — so a wounded crew member
        becomes markedly slow to do anything at all.
        """
        crew.step_timer += self._action_delay_for(crew)
    def _resolve_order(self, order: Order) -> OrderOutcome:
        """Validate and apply one order.

        1:1 fidelity: there is **no obedience gate** — the decoded program has no
        compliance roll on the order path (D-018: an ordered crew member walks to
        the written destination after their action-timer delay, regardless of
        fear). The old OBEY/DELAY/REFUSE PCS roll was an invention and is gone;
        fear's real effects (tempo, panic branch) are tracked in
        `docs/re/VICE_CHECKS.md` until a live capture calibrates them.
        """
        crew = self.state.crew.get(order.crew_id)
        if crew is None or not crew.alive:
            return OrderOutcome.INVALID
        if order.type in (OrderType.MOVE_TO, OrderType.GET_ITEM) and order.target is None:
            return OrderOutcome.INVALID
        return self._apply_order(order)
    def _process_orders(self) -> None:
        """Consume the order queue for one tick, re-queuing the survivors."""
        pending = list(self._orders)
        self._orders.clear()
        outcomes: list[tuple[Order, OrderOutcome]] = []
        for order in pending:
            outcome = self._resolve_order(order)
            outcomes.append((order, outcome))
            if outcome in SURVIVING_OUTCOMES:
                self._orders.append(order)
        self.last_outcomes = outcomes
    def _duct_step_target(self, crew: CrewMember, target: str) -> str | None:
        """``target`` as a **duct** step from ``crew``'s room, or ``None``.

        [C $779C / $81EF] P-5. A duct step is available when the target is one
        of the current room's compass neighbours **and** that room's grille has
        been removed (or burst open by the Alien). Returns ``None`` when the
        move is not a duct move, so the caller falls back to the surface graph.

        The ROM expresses this by handing the mover a destination with **bit 7
        set**; `$7373` strips it and raises `$6501,Y`.
        """
        if crew.room_id is None:
            return None
        # **P2-2, corrected 2026-08-02.** This used to convert a *surface* move
        # into a duct move whenever the target happened to be a duct neighbour
        # and the room's grille was open — so removing a grille and then
        # ordering an ordinary move silently put the crew member into the
        # ducting instead of the room they asked for. The ROM never does that:
        # entering the ducting is its own menu choice, "MOVE TO: GRILLE"
        # (`$8729` writes the label into the MOVE TO column `$046E`), handled
        # by `_use_grille`. A duct step is therefore only ever available to
        # someone **already inside** the ducting.
        if not crew.in_duct:
            return None
        if target not in self.ship.duct_exits(crew.room_id).values():
            return None
        return target
    def _use_grille(self, crew: CrewMember) -> OrderOutcome:
        """Cross this room's grille — **[C $86F0/$8729] P2-2**.

        Once a grille has been removed, `draw_grille_option` stops offering
        "REMVGRILLE" in the SPECIAL column and writes **"GRILLE"** into the
        **MOVE TO** column instead, so crossing it is a destination the player
        picks. It toggles the character between the room and the ducting at the
        same location — in, and back out again — which is also how the in-duct
        menu (`$81EF`, compass directions only) is escaped.

        Blocked while the grille is still in place: that is what REMVGRILLE is
        for, and the ROM simply does not draw the option (`$86FA BEQ`).
        """
        if crew.room_id is None:
            return OrderOutcome.BLOCKED
        grille = next(
            (g for g in self.ship.grilles if g.room_id == crew.room_id), None
        )
        if grille is None or not grille.is_open:
            return OrderOutcome.BLOCKED
        entering = not crew.in_duct
        crew.in_duct = entering
        if entering and crew.fear >= constants.DUCT_ENTRY_COMPOSURE_GATE:
            # [C $737E-$738D] Going in costs one composure — but only if there
            # is any to lose (`$7381 CMP #$02 / BCC`). Staying inside then
            # *raises* it each tick (`$729C`, D-059: hiding is reassuring), so
            # the two are not in conflict. Coming back out costs nothing.
            crew.bump_fear(-constants.DUCT_ENTRY_COMPOSURE_COST)
        return OrderOutcome.COMPLETED
    def _action_base_ticks(self, order: Order, crew: CrewMember) -> int:
        """The base duration an order arms `$64EE,Y` with, before the delay.

        **[C] D-168.** Each action code loads its own literal or table entry
        and *then* lets `compute_action_delay` add the per-slot and per-health
        terms on top::

            MOVE        $7B69  LDA #$40      (64)
            REMVGRILLE  $845A  LDA $403A,Y   (80-180, D-166)
            ATTACK/USE  $48F7  LDA #$28      (40)
        """
        if order.type is OrderType.REMOVE_GRILL:
            return constants.grille_action_ticks(self._slot_of(crew))
        if order.type in (OrderType.ATTACK, OrderType.USE):
            return constants.ATTACK_ACTION_TICKS
        return constants.MOVE_ACTION_TICKS
