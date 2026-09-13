"""FV-3.1 — drift-guards for every decoded/captured value folded into the remake.

Each assertion pins a number (or table) to the **specific ROM address or
capture** it was decoded from, with that citation inline. The point is not to
re-test behaviour — the behavioural suites already do that — but to make a
*silent* edit of a decoded constant fail a gate.

Several of these guard values that were actively **wrong** at some point and
were only caught by a later audit; the comment on each records which, so the
test doubles as a record of what has already drifted once.
"""

from __future__ import annotations

import re

import pytest

from alien_remake.core import constants
from alien_remake.core.crew import START_FEAR, START_HEALTH
from alien_remake.core.gamedata_snapshot import (
    ALIEN_ROUTES,
    CREW_NAMES,
    CREW_WALK_TICKS,
    ITEMS,
    JONES_WALK_TICKS,
    MORALE_WORDS,
    ROOM_SLUGS,
    ROOMS,
    STATUS_WORDS,
)

import needs                                       # noqa: E402


# --- the Alien -----------------------------------------------------------------

def test_alien_timers_and_roll_bands() -> None:
    # D-038 corrected ALIEN_MOVE_TICKS 70 -> 60: `alien_choose_move ($8A36)`'s
    # surface branches all converge on `$8A4A: LDA #$3C`. The old 70 (`$6581`)
    # belongs to `alien_ai ($8A74)`'s *separate* in-duct dispatcher.
    assert constants.ALIEN_MOVE_TICKS == 60          # [C $8A4A]
    assert constants.ALIEN_DUCT_TICKS == 40          # [C $89E0]
    assert constants.ALIEN_ROLL_SIDES == 16          # [C $888F] rng is 0-15
    assert constants.ALIEN_DUCT_THRESHOLD == 12      # [C $8A39] CMP #$0C
    assert constants.ROUTE_BAND_BOUNDS == (3, 5, 7, 9)   # [C $8A50-$8A64]
    assert constants.ALIEN_PURSUIT_TICKS == 20       # [C $8A0C] LDA #$14
    assert constants.AGGRESSION_DAMAGE_DIVISOR == 4  # [C $4C9F] two LSRs


def test_panic_wander_uses_its_own_band_mapping() -> None:
    # D-043: panic (`char_wander $5203`) does NOT reuse the Alien's band
    # mapping — only tables 2/3/4, with 3 and 4 each appearing twice.
    from alien_remake.core.alien import _panic_route_band

    assert [_panic_route_band(r) for r in range(16)] == (
        [4, 4, 4] + [3, 3, 3] + [2, 2, 2] + [3, 3, 3] + [4, 4, 4, 4]
    )


def test_alien_route_tables_are_the_real_five() -> None:
    # RW-6a: five roll-banded tables, non-uniformly sized (a decode bug once
    # assumed they were evenly spaced).
    assert len(ALIEN_ROUTES) == 5
    assert all(len(t) >= 34 for t in ALIEN_ROUTES)


# --- combat --------------------------------------------------------------------

def test_item_attack_damage_table() -> None:
    dmg = constants.ITEM_ATTACK_DAMAGE
    assert dmg["harpn_gun"] == 5     # [C $49F6] ADC #$05, guaranteed
    assert dmg["elctrc_prd"] == 1    # [C $4976] CMP #$06 / BCC -> INC $7D45
    assert dmg["incineratr"] == 1
    assert dmg["spanner"] == 1       # [C $498D] CMP #$12 / BCS
    assert dmg["laser_pist"] == 1
    # D-033 corrected the tracker 0 -> 1: `$49B5` falls through to `$497A`.
    assert dmg["tracker"] == 1
    assert dmg["net"] == 0           # no wound, but it entangles (below)
    assert dmg["fire_extng"] == 0 and dmg["cat_box"] == 0
    assert constants.ALIEN_DAMAGE_TO_KILL == 50      # [C $4980] CMP #$32


def test_net_entangle_and_destroy_on_use() -> None:
    # D-033: `$49A2-$49A8` adds $50 to the Alien's own move timer; both the
    # net and the tracker are consumed by `clear_object_at_loc2`.
    assert constants.ALIEN_NET_ENTANGLE_TICKS == 80
    assert constants.ITEM_DESTROYED_ON_ATTACK == frozenset({"net", "tracker"})


def test_room_damage_paths_and_alarm_threshold() -> None:
    # D-027: the harpoon (item id 12) takes the +15 path, everything else +6.
    assert constants.ROOM_DAMAGE_PER_ATTACK == 6              # [C $4AFD]
    assert constants.ROOM_DAMAGE_PER_ATTACK_HARPOON == 15     # [C $4A95]
    # D-044: the alarm latch threshold.
    assert constants.ROOM_ALARM_DAMAGE_THRESHOLD == 4         # [C $558C]


def test_removed_inventions_stay_removed() -> None:
    """Each of these was a real invention caught by an audit; a future edit
    must not quietly reintroduce one."""
    for gone in (
        "LETHAL_ITEM_IDS",          # FV-1.6: no lethal subset exists
        "ATTACK_HIT_CHANCE",        # FV-1.6: `CMP #$06` is an item id, not a roll
        "ALIEN_ATTACK_HIT_CHANCE",  # FV-1.6: the Alien wounds deterministically
        "EXTINGUISHER_REPAIR",      # D-044: the ROM never repairs room damage
    ):
        assert not hasattr(constants, gone), f"{gone} was reintroduced"


# --- crew / PCS ----------------------------------------------------------------

def test_crew_start_tables() -> None:
    assert CREW_NAMES == (
        "Dallas", "Kane", "Ripley", "Ash", "Lambert", "Parker", "Brett",
    )
    assert START_HEALTH == (6, 5, 4, 5, 4, 6, 5)     # [C $7D4D]
    assert START_FEAR == (4, 4, 3, 4, 3, 4, 3)       # [C $7D5D]
    assert CREW_WALK_TICKS == (4, 4, 3, 4, 3, 4, 3)  # [C $6586]
    assert JONES_WALK_TICKS == 5                     # [C $6586] slot 8


def test_fear_scale_and_words() -> None:
    assert (constants.FEAR_MIN, constants.FEAR_MAX) == (0, 10)  # [C $4CE8] cap
    assert MORALE_WORDS == ("confident", "stable", "uneasy", "shaken", "broken")
    assert STATUS_WORDS == ("O.K.", "wounded", "collapsed", "DEAD")
    # D-031: every confirmed site moves the value by exactly 1.
    # D-059: **direction matters** — the value is composure (high = calm), so
    # bad events are NEGATIVE and the reassuring one (crowding) is positive.
    assert constants.COMPOSURE_HIT_ALIEN_ATTACK == -1   # [C $4230] wounded
    assert constants.COMPOSURE_HIT_CREW_DEATH == -1     # [C $47DC/$5A0D]
    assert constants.FEAR_BUMP_CROWDED == 1             # [C $4CF9] safety in numbers
    assert constants.CROWD_THRESHOLD == 3               # [C $4CE8] CPY #$03


def test_morale_word_polarity_matches_the_decoded_table() -> None:
    """D-059 [C $7DC5 + $7D13]: `fear_band` is
    ``index = 0 if value >= 5 else (4 - value)`` into
    confident/stable/uneasy/shaken/broken — so **high is GOOD**. The remake
    had this inverted for a long time; the two formulas agree only at value
    3, which is why the earlier live spot-check never caught it."""
    from alien_remake.core.crew import CrewMember, Role

    assert [
        CrewMember("x", "X", Role.CAPTAIN, None, fear=v).morale for v in range(6)
    ] == ["broken", "shaken", "uneasy", "stable", "confident", "confident"]


def test_room_capacity_is_generic() -> None:
    # D-030: `char_pump`'s `CPX #$03` is room-id-agnostic — SHUTTLEBAY has no
    # special escape-pod limit.
    assert constants.ROOM_CAPACITY == 3


# --- map / items ---------------------------------------------------------------

def test_map_and_item_tables() -> None:
    assert len(ROOMS) == 34 and len(ROOM_SLUGS) == 35
    assert len(ITEMS) == 20                          # [C $82CF/$7C7D]
    decks = [r[1] for r in ROOMS]
    # [C $7569] D-116: 0/1/2 with 9/16/9 rooms, not $80D3's 4/5/6 at 10/14/10.
    assert sorted({d: decks.count(d) for d in set(decks)}.items()) == [
        (0, 9), (1, 16), (2, 9)
    ]


def test_deck_value_mapping_is_the_confirmed_one() -> None:
    # D-116: the deck byte is now `$7569`'s own 0/1/2, so the map is identity.
    # It used to translate `$80D3`'s 4/5/6, which are duct-map screen pages.
    from alien_remake.core.nostromo import _RAW_DECKS

    assert _RAW_DECKS == {0: 0, 1: 1, 2: 2}


# --- rendering -----------------------------------------------------------------

class _RenderConstants:
    """Attribute access across every module of the split renderer (D-191).

    The tests below pin *render constants* as a body of knowledge, not the
    contents of one file, so they should not care which module a constant sits
    in — otherwise splitting `pygame_app.py` breaks tests that assert nothing
    about the split. Resolution order is deliberate: the specific modules first,
    `pygame_app` last, so a name that gets re-exported still resolves to its
    real home.

    Raises `AttributeError` naming every module searched, which is a far more
    useful failure than "module has no attribute X" when a constant has simply
    moved again.
    """

    _MODULES = ("layout", "frontend", "audio", "play", "pygame_app")

    def __getattr__(self, name: str) -> object:
        import importlib

        searched = []
        for mod in self._MODULES:
            try:
                module = importlib.import_module(f"alien_remake.render.{mod}")
            except ImportError:
                continue
            searched.append(mod)
            if hasattr(module, name):
                return getattr(module, name)
        raise AttributeError(
            f"{name!r} is in none of alien_remake.render.{{{', '.join(searched)}}}"
        )


def test_render_constants_pinned() -> None:
    pa = _RenderConstants()

    # D-040: `tbl_alien_anim ($4EDC)` — 4 distinct frames, ping-ponged.
    assert pa._ALIEN_SPRITE_FRAMES == (0, 1, 1, 2, 2, 3, 3, 2, 2, 1, 1, 0)
    # D-045: `$4ED4` heartbeat ramp; `$4F33`'s sprite-0 pointer $B8 -> slot 24.
    assert pa._HEARTBEAT_COLOURS == (0x00, 0x0B, 0x0C, 0x0F, 0x01, 0x0F, 0x0C, 0x0B)
    assert pa._CHAR_SPRITE == 24
    # D-049: `$5EF7` pointers $BD..$C3 -> slots 29..35, and the `$5EC0` layout.
    assert pa._PORTRAIT_SLOTS == (29, 30, 31, 32, 33, 34, 35)
    assert pa._PORTRAIT_X == (24, 64, 104, 144, 184, 224, 264)
    assert pa._PORTRAIT_Y == 32
    # D-051: the exact 40x25 split — map cols 0-29, panel cols 30-39.
    assert pa._PANEL_COL == 30 and pa._MAP_COLS == 30


def test_only_confirmed_screen_codes_are_mapped() -> None:
    """Only glyphs actually verified by rendering may be mapped.

    D-047: digits and '.' were once assumed at the ASCII positions `$30-$39`
    and **disproven by rendering them** (graphic noise). **D-078 then located
    the digits for real** — they live in the reverse-video half at `$B0-$B9`,
    found by inverting the chargen ROM's digits and pixel-matching against
    ALIEN's 256 glyphs, then confirmed by rendering `$B0-$B9` cut-out. `%` is
    `$A5`. The period is still NOT mapped: `$AE` turned out to be **blank**
    (all 1-bits, like the `$A0` space), so the "O.K." earlier dumps showed was
    the decoder's ASCII assumption, not a glyph.
    """
    pa = _RenderConstants()

    assert pa._ASCII_TO_SCREEN_CODE["a"] == 1
    assert pa._ASCII_TO_SCREEN_CODE["A"] == 1 | 0x80   # uppercase = +$80
    assert pa._ASCII_TO_SCREEN_CODE[" "] == 0xA0
    assert pa._ASCII_TO_SCREEN_CODE[":"] == 0x1C
    assert pa._ASCII_TO_SCREEN_CODE["%"] == 0xA5
    for d in range(10):                                # [C, D-078]
        assert pa._ASCII_TO_SCREEN_CODE[str(d)] == 0xB0 + d
    assert 0x30 not in pa._ASCII_TO_SCREEN_CODE.values(), "the ASCII slots are noise"
    # **P-7:** the period is `$AE` and the comma `$AC`. D-078 had called the
    # period "unlocated" because `$AE`'s glyph is blank — but blank is the
    # point: `$7CEB` holds `8F AE 8B AE` for "O.K." and the `$7A10` template
    # uses runs of `$AE` as dotted fill, so `$AE` is the byte the ROM writes
    # where a period belongs. This charset simply has no period glyph.
    assert pa._ASCII_TO_SCREEN_CODE["."] == 0xAE
    assert pa._ASCII_TO_SCREEN_CODE[","] == 0xAC
    for unconfirmed in "-*()?":
        assert unconfirmed not in pa._ASCII_TO_SCREEN_CODE, unconfirmed


def test_room_marker_tables_are_the_decoded_ones() -> None:
    """R-08/D-058 [C $758D/$75B1]: the game's own per-room marker positions,
    indexed by room id and used to place sprite 1 (the deck-plan key's
    "Location Ptr"). 36 entries each, and every one must land inside the
    320x200 field — a stray value would mean the index space is wrong."""
    from alien_remake.render.play import _ROOM_MARKER_X, _ROOM_MARKER_Y

    assert len(_ROOM_MARKER_X) == len(_ROOM_MARKER_Y) == 35
    assert _ROOM_MARKER_X[0] == 112 and _ROOM_MARKER_Y[0] == 24   # AIRLOCK 1
    for x in _ROOM_MARKER_X:
        assert 0 <= x <= 320 - 24, x
    for y in _ROOM_MARKER_Y:
        # Room 2's sprite starts 4px above the text area (a sprite may
        # overhang); everything else sits inside the map rows.
        assert -8 <= y <= 200 - 21, y


def test_room_markers_are_almost_all_unique_per_deck() -> None:
    """Every mapped room gets a unique marker spot on its deck (D-116).

    This used to allow **two** collisions, described as "what the ROM actually
    contains". They were an artefact of reading the deck from `$80D3`, whose
    4/5/6 values are duct-map screen pages rather than decks. Pointing the deck
    at `$7569` — the byte `$76BB` and `$511F` actually use to pick the deck plan
    — drops the collisions to zero.

    That is the corroboration for the change: the anomaly the old mapping had to
    tolerate does not exist in the real one."""
    from collections import defaultdict

    from alien_remake.core.gamedata_snapshot import ROOMS
    from alien_remake.render.play import _ROOM_MARKER_X, _ROOM_MARKER_Y

    seen: dict[tuple[int, int, int], int] = defaultdict(int)
    for room_id, deck, *_rest in ROOMS:
        seen[(deck, _ROOM_MARKER_X[room_id], _ROOM_MARKER_Y[room_id])] += 1
    duplicated = sum(1 for n in seen.values() if n > 1)
    assert duplicated == 0, f"markers collide on {duplicated} spots"


def test_heartbeat_divider_table() -> None:
    """R-19/R-21, D-061 [C $4E16]: `fear_alert` sets the heartbeat's IRQ
    divider `$4D02` from composure — 40/30/23/15 for >=4/3/2/<=1. The pulse
    **races as composure falls**, which independently corroborates D-059's
    polarity (low value = panicked)."""
    assert constants.heartbeat_divider(10) == 40   # CONFIDENT, slowest
    assert constants.heartbeat_divider(4) == 40
    assert constants.heartbeat_divider(3) == 30    # STABLE
    assert constants.heartbeat_divider(2) == 23    # UNEASY
    assert constants.heartbeat_divider(1) == 15    # SHAKEN
    assert constants.heartbeat_divider(0) == 15    # BROKEN, fastest
    # Monotonic: never slower as composure drops.
    rates = [constants.heartbeat_divider(v) for v in range(5)]
    assert rates == sorted(rates), "heartbeat must not slow as composure falls"


def test_auto_destruct_countdown_and_override_window() -> None:
    """R-28b/D-060 [C $58E8/$58ED/$585E]: a 9-unit countdown with a 255-tick
    sub-counter, and the override only works while >= 5 units remain."""
    assert constants.AUTO_DESTRUCT_MINUTES == 9        # [C $58E8]
    assert constants.AUTO_DESTRUCT_SUBTICKS == 255     # [C $58ED/$5A3B]
    assert constants.AUTO_DESTRUCT_OVERRIDE_ABOVE == 5  # [C $585E] CMP #$05
    assert constants.AUTO_DESTRUCT_TICKS == 10 * 255   # D-162: TEN wraps


# --- FIGHT FIRE (D-066, `$5889` traced in full 2026-08-01) -------------------

def test_fight_fire_is_a_real_special_option() -> None:
    """[C $5889] It sits in the specials dispatch chain with its own menu label
    ("Fight Fire") and result label ("Fire Out"). `menu.py` used to assert it
    was "not a separate special"; that note was wrong."""
    from alien_remake.core.special_options import SpecialOptionType

    assert hasattr(SpecialOptionType, "FIGHT_FIRE")


def _fire_sim():
    """A sim with a live alarm in the acting crew member's room + an extinguisher."""
    import random

    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(3))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    room = crew.room_id
    assert room is not None
    ext = next(i for i in sim.state.items.values() if i.type_id == "fire_extng")
    ext.room_id, ext.holder = room, None
    sim.state.room_alarm[room] = 1
    sim.state.room_damage[room] = 7
    return sim, crew, room, ext


def test_fight_fire_silences_the_alarm_but_never_repairs_damage() -> None:
    """[C $5889] The handler clears `$651C,X` (the alarm latch) and never
    touches `$653F` (structural damage) — D-044's conclusion, re-confirmed by
    reading the routine instruction by instruction."""
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim, crew, room, ext = _fire_sim()
    before = sim.state.room_damage[room]
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.FIGHT_FIRE, crew_id=crew.id)
    )
    assert sim.state.room_alarm.get(room, 0) == 0     # alarm silenced
    assert sim.state.room_damage[room] == before      # damage is PERMANENT


def test_fight_fire_spends_exactly_one_charge() -> None:
    """[C $58AC] `DEC $4B37,X` — one charge per successful use."""
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim, crew, room, ext = _fire_sim()
    start = ext.uses_left
    assert start is not None
    sim.apply_special_option(SpecialOption(SpecialOptionType.FIGHT_FIRE, crew_id=crew.id))
    assert ext.uses_left == start - 1


def test_empty_extinguisher_fails_and_leaves_the_alarm_up() -> None:
    """[C $589C/$589E] A zero charge prints "…EXTINGUISHER IS EMPTY" and RTSes
    **before** reaching the clear — so the alarm stays raised and no charge is
    spent. The remake previously cleared regardless."""
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim, crew, room, ext = _fire_sim()
    ext.uses_left = 0
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.FIGHT_FIRE, crew_id=crew.id)
    )
    assert sim.state.room_alarm.get(room) == 1        # still alarming
    assert ext.uses_left == 0                          # nothing spent


def test_fight_fire_needs_an_extinguisher_within_reach() -> None:
    """[C $5890/$5894] `find_room_object` must return index 8-10; anything else
    RTSes with no effect."""
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim, crew, room, ext = _fire_sim()
    ext.room_id, ext.holder = None, "nobody"          # out of reach
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.FIGHT_FIRE, crew_id=crew.id)
    )
    assert sim.state.room_alarm.get(room) == 1


# --- R-19b: the "current character" convention ($64FB) -----------------------

def test_current_character_starts_unset_like_the_rom() -> None:
    """[C $43DE] `game_init_mode` stores 0 into `$64FB`, and `$42F4` clears it
    the same way — 0 means "nobody is current". The remake's equivalent is
    `MenuController.selected_crew is None`."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    menu = MenuController(Simulation(rng=random.Random(11)))
    assert menu.selected_crew is None


def test_heartbeat_rate_follows_the_current_characters_composure() -> None:
    """[C $7DC5 -> $4E16] `fear_band` does `LDY $64FB / JSR fear_alert`, so the
    heartbeat divider is read for **the current character**, not the roster or
    the worst-off crew member. D-061's table drives it, and because composure
    is high=good (D-059) the beat must get FASTER as composure falls."""
    from alien_remake.core import constants

    dividers = [constants.heartbeat_divider(c) for c in (4, 3, 2, 1)]
    assert dividers == [40, 30, 23, 15]        # $4E16's own values
    assert dividers == sorted(dividers, reverse=True), "beat must race as composure drops"


def test_one_current_character_at_a_time() -> None:
    """`$64FB` holds a single index; selecting another replaces it rather than
    accumulating, and the ROM bounces a selection of an incapacitated crew
    member back to 0 (`$7D45,Y < 2` -> `STA $64FB`)."""
    import random

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(5))
    menu = MenuController(sim)
    alive = [c.id for c in sim.state.crew.values() if c.alive]
    menu.selected_crew = alive[0]
    assert menu.selected_crew == alive[0]
    menu.selected_crew = alive[1]
    assert menu.selected_crew == alive[1]      # replaced, not added


# --- the placeholder ratchet (PV register, 2026-08-07) ------------------------

#: Live `[?]` markers in `src/alien_remake/` at the moment the PV register was
#: filed. **This number may only go DOWN.** Every `[?]` is an admission that a
#: mechanic is not yet traced to a routine, and the project's whole discipline
#: is that those get closed by citing an address or a capture — never by
#: quietly guessing and deleting the marker, and never by adding new ones
#: without filing them. If this test fails because the count went *up*, the new
#: placeholder needs a `PV-nn` entry in `todo.md` before the count is raised
#: here. If it fails because the count went *down*, that is good news: lower
#: the number and tick the PV item.
_PLACEHOLDER_BUDGET = 42


def _placeholder_count() -> int:
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "src" / "alien_remake"
    return sum(
        p.read_text(encoding="utf-8").count("[?]") for p in root.rglob("*.py")
    )


def test_placeholder_count_does_not_grow() -> None:
    """The `[?]` budget is a ratchet — see `_PLACEHOLDER_BUDGET`."""
    count = _placeholder_count()
    assert count <= _PLACEHOLDER_BUDGET, (
        f"{count - _PLACEHOLDER_BUDGET} new `[?]` placeholder(s) since the PV "
        "register was filed. File each one as a PV-nn item in todo.md (with "
        "the routine or capture that would settle it), then raise "
        "_PLACEHOLDER_BUDGET."
    )


def test_the_pv_register_exists_and_covers_the_placeholders() -> None:
    """`todo.md` must carry a PV item per open placeholder area.

    Guards against the register being deleted or emptied in a later cleanup —
    the placeholders themselves are scattered through docstrings and are easy
    to lose track of, which is exactly why they were centralised.
    """
    from pathlib import Path

    todo = (Path(__file__).resolve().parent.parent / "todo.md").read_text(
        encoding="utf-8"
    )
    assert "Placeholder register (`PV-nn`)" in todo
    filed = todo.count("**PV-")
    assert filed >= 30, f"only {filed} PV items filed; the sweep found 32"


def test_cursor_repeat_has_no_initial_delay_and_runs_at_loop_rate() -> None:
    """**[C $71B0/$7453] PV-31 / D-165** — the cursor's cadence is derived.

    `read_input` reads `$C5` and `$DC00` once per main-loop pass and writes a
    direction to `$71AF`; `sub_7453` acts on it and calls `delay_routine`.
    There is no repeat counter, no debounce and no acceleration anywhere in
    that path — the cursor steps once per pass while a direction is held, so
    the busy-wait *is* the repeat rate, and there is **no initial delay**. The
    old 12-frame pause was an invention.
    """
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    from alien_remake.render.layout import _FRAME_HZ
    from alien_remake.render.pygame_app import PygameRenderer

    rate = PygameRenderer._JOY_REPEAT_RATE
    assert PygameRenderer._JOY_REPEAT_DELAY == rate, "no initial delay in the ROM"
    # And the resulting cadence tracks the main loop, not a hand-picked feel.
    assert _FRAME_HZ / rate == pytest.approx(constants.MAIN_LOOP_HZ, rel=0.1)

# --- PV-34: one clock, one pending action (D-168) ----------------------------

def test_there_is_exactly_one_clock_per_character() -> None:
    """**[C $7216] D-168/PV-34** — `char_pump` decrements `$64EE,Y` once per
    pass and everything that character does hangs off that single expiry.

    The remake ran two: `crew.step_timer`, decremented inside `_apply_order`,
    and a separate `_turn_timer` dict read by `_turn_due` — seeded with the
    same expression and counted down apart, so an order and a panic roll could
    disagree about whose turn it was. `_turn_timer` is gone; this pins that it
    stays gone.
    """
    import random

    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    assert not hasattr(sim, "_turn_timer"), "the second clock must not come back"

    crew = next(c for c in sim.state.crew.values() if c.alive)
    crew.step_timer = 3
    before = crew.step_timer
    sim.advance()
    assert crew.step_timer == before - 1, "exactly one decrement per pass"


def test_one_pending_action_per_character_and_reordering_restarts_the_clock() -> None:
    """**[C $7B02-$7B69] D-168/PV-34.** `$7B02` zeroes both `$650C,Y` and
    `$64EE,Y` before the new action is armed, so a character has exactly one
    pending action and re-ordering restarts the countdown. The remake's queue
    could hold several live orders for one character at once."""
    import random

    from alien_remake.core.orders import Order, OrderType
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
    nbrs = sim.ship.door_neighbors(crew.room_id)
    assert nbrs

    sim.queue_order(Order(crew.id, OrderType.MOVE_TO, nbrs[0]))
    assert sim.pending_orders == 1
    armed = crew.step_timer
    assert armed > 0, "$7B69 arms the clock at ISSUE time"

    sim.advance()
    assert crew.step_timer == armed - 1

    # A second order replaces the first and re-arms from full.
    sim.queue_order(Order(crew.id, OrderType.REMOVE_GRILL))
    assert sim.pending_orders == 1, "one slot, not a queue"
    assert crew.step_timer == (
        constants.grille_action_ticks(sim._slot_of(crew))
        + sim._action_delay_for(crew)
    ), "$7B02 zeroes the clock, $845A re-arms it"

    # Another character keeps their own independent slot.
    other = next(
        c for c in sim.state.crew.values() if c.alive and c.id != crew.id and c.room_id
    )
    sim.queue_order(Order(other.id, OrderType.REMOVE_GRILL))
    assert sim.pending_orders == 2


def test_more_than_one_character_can_resolve_in_the_same_pass() -> None:
    """**[C $72E1] D-166/D-168** — `check_deferred_move` ends `INY / CPY #$08 /
    JMP $7226` and every re-entry arrives with Y = the acting slot, so the pump
    carries on past a resolution. Any number of characters can come due in one
    pass, in slot order."""
    import random

    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    alive = [c for c in sim.state.crew.values() if c.alive][:3]
    assert len(alive) >= 2
    for c in alive:
        c.step_timer = 1
    due = sim._pump_characters()
    assert {c.id for c in alive} <= due, "all of them resolve on the same pass"


def test_title_card_timings_are_computed_from_the_delay_loop() -> None:
    """**[C $561E/$5E81] PV-26 / D-172** — the title's durations are derived.

    `delay ($561E)` is a countable loop — body 6+6+2+4+6+6+6+6+2 = 44 cycles
    plus a 3-cycle branch = 47 per inner iteration, 256 inner x 256 outer — so
    `delay_long (LDX #$00)` is 3,081,727 cycles = **3.128 s PAL**. The title
    routine calls it **eight** times: one before each of A-L-I-E-N and three
    after. These had been carried as `[?]` calibration at 40 and 6 ticks, ~5x
    too fast; a cycle count settles them without touching the emulator.
    """
    inner_body = 6 + 6 + 2 + 4 + 6 + 6 + 6 + 6 + 2   # INC x2 LDA STA INC x4 INY
    inner = 255 * (inner_body + 3) + (inner_body + 2) + 2
    outer = inner + 2 + 3
    cycles = 255 * outer + (inner + 2 + 2)
    delay_long_s = cycles / 985_248                   # PAL
    assert delay_long_s == pytest.approx(3.128, abs=1e-3)

    assert constants.TITLE_TICKS == round(8 * delay_long_s * constants.TICK_HZ)
    assert constants.TITLE_LETTER_TICKS == round(delay_long_s * constants.TICK_HZ)
    # Five letters must be on screen before the card ends, with time to spare
    # for the three trailing delays.
    assert 5 * constants.TITLE_LETTER_TICKS < constants.TITLE_TICKS


def test_portrait_slots_are_the_roms_own_arithmetic() -> None:
    """**[C $6671] PV-29 / D-179** — `$BC + slot`, not a best-effort mapping.

    `place_selected_char_sprite ($666C)` does `LDY $64FB / TYA / CLC /
    ADC #$BC / STA $07FA`: the portrait's sprite pointer is literally the
    character slot plus `$BC`. So slots 1-7 are pointers `$BD`-`$C3`, which is
    `_PORTRAIT_SLOTS` in roster order. The register carried this as "the
    menu-draw code wasn't decoded to pin each face to a name"; it is one
    instruction.
    """
    needs.need(needs.ALIEN_PRG)
    import pathlib

    from alien_remake.render.layout import _PORTRAIT_SLOTS

    prg = pathlib.Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    mem = prg[2:]
    assert mem[0x666C - load: 0x6676 - load] == bytes((
        0xAC, 0xFB, 0x64,        # LDY $64FB   (the selected slot)
        0x98,                    # TYA
        0x18,                    # CLC
        0x69, 0xBC,              # ADC #$BC
        0x8D, 0xFA, 0x07,        # STA $07FA   (sprite 2's pointer)
    ))
    # Pointer = $A0 + tile slot, so tile slot = $BC + character slot - $A0.
    assert tuple(_PORTRAIT_SLOTS) == tuple(0xBC + k - 0xA0 for k in range(1, 8))


def test_room_glyph_matches_the_captured_deck_screens() -> None:
    """**PV-30 / D-179** — `$A0` is what the real deck plans are made of.

    Carried as "a documented default, not a claim about the original wall
    glyph". The three captured deck screens settle it: `$A0` is by far the
    commonest code in every one of them. (It only ever applies to the
    synthetic fallback grid anyway — the real backdrops are rasterised from
    exactly these captures.)
    """
    import collections
    import pathlib

    from alien_remake.render.play import _ROOM_GLYPH

    for name in ("upperdeck_0400.bin", "middledeck_0400.bin", "lowerdeck_0400.bin"):
        path = pathlib.Path("archive/reference") / name
        if not path.exists():
            pytest.skip(f"{name} not captured")
        counts = collections.Counter(path.read_bytes()[:1000])
        assert counts.most_common(1)[0][0] == _ROOM_GLYPH, name


def test_basic_reveal_rates_are_derived_from_the_measurement() -> None:
    """**PV-27 / D-183** — the front-end reveal rates are derived, not tuned.

    D-142 measured the GREEN VALLEY screen live: the spiral swept in ~11.0 s
    and the whole screen took ~14.1 s. Counting what the BASIC does converts
    that into a rate. Lines 220-270 draw each ring as four edges, so over
    `FORQ=11TO1` plus `FORQ=1TO11` the spiral is `2*SUM(130-8Q, Q=1..11)` =
    **1804** POKEs — 6.10 ms each.

    The MARQUIE border is 260 POKEs, i.e. 1.585 s: within 1% of the 48 frames
    the old estimate assumed, which is why `_BORDER_REVEAL_RATE` was already
    right. The centre-out text is PRINTs, so it takes the residual — 14.1 -
    11.0 - 0.9 (line 320's `FORXX=1TO900`) over 12 steps = 183 ms/step.
    """
    pa = _RenderConstants()

    # The spiral's POKE count, recomputed from the BASIC rather than hardcoded.
    pokes = 0
    for _loop in range(2):                      # lines 200 and 210
        for q in range(1, 12):
            top = bottom = (39 - q) - q
            right = left = ((25 - q) - q) + 1
            pokes += top + right + bottom + left
    assert pokes == 1804
    assert pa._BASIC_POKE_S == pytest.approx(11.0 / pokes)
    assert pa._BASIC_POKE_S * 1000 == pytest.approx(6.10, abs=0.01)

    assert pa._BORDER_REVEAL_POKES == 40 * 2 + 25 * 4 + 40 * 2 == 260
    border_s = pa._BORDER_REVEAL_POKES * pa._BASIC_POKE_S
    assert border_s == pytest.approx(1.585, abs=0.01)
    # The old hand-picked 48 frames sits within 1% of the derived duration.
    assert border_s * pa._FRAME_HZ == pytest.approx(48.0, rel=0.02)

    # The text reveal was ~2.7x too fast at 2 frames per step.
    # DISC-211: the measured step is still the measured step; the rate it
    # produces is then divided by the player-directed FRONTEND_SPEEDUP. Pin
    # both halves, so a change to either shows up here.
    assert pa._TEXT_REVEAL_RATE == round(pa._TEXT_REVEAL_STEP_S * pa._FRAME_HZ)
    # DISC-211: the speedup multiplies the frame counter, never these rates, so
    # the measurement above stays exact and the ratio stays exact too.
    assert pa.FRONTEND_SPEEDUP == 1.25
    assert pa._TEXT_REVEAL_RATE >= 5

# --- the stale-claim drift guard (D-189) --------------------------------------
#
# Four discoveries this project made were *caused* by a later reader trusting an
# earlier pass's prose: `$5753` read as a fire flag (D-163), `$651C` as a
# boolean (D-164), `$5354` as the Alien's routine (D-177), `_SHUTTLEBAY_SLUG`
# for room 34 (D-159). Each time the body was corrected and a header, comment or
# docstring elsewhere kept asserting the old thing.
#
# These two tests make that failure mechanical rather than a matter of
# diligence — the same idea as `_PLACEHOLDER_BUDGET` above: encode the
# discipline as a ratchet so it cannot quietly rot.

#: Claims a later discovery **disproved**, which must not survive in `src/`.
#:
#: Match on a distinctive phrase, never a keyword. "deterministic" appears ten
#: times in the package and **eight are still true** — they describe crew->Alien
#: combat (`resolve_attack`, genuinely deterministic per item) or the sim's
#: reproducibility. Only the entries below were the superseded claim.
#:
#: To add a row: paste enough of the wrong sentence to be unambiguous, name the
#: discovery that killed it, and say what is true now.
SUPERSEDED_CLAIMS: tuple[tuple[str, str, str], ...] = (
    (
        "the original returns to the CONTROL panel",
        "DISC-272",
        "measured on the running game: choosing a room from INDICATE LOCATION "
        "leaves the list up -- `$64FB` stays 16 and the nineteen room rows stay "
        "on screen -- so several rooms can be indicated in a row, and QUIT on "
        "row 0 is the way out",
    ),
    (
        "still toggles it anywhere",
        "DISC-263",
        "Ctrl+3 and 0 both sit in the `screen is not PLAYING` half of the "
        "input dispatch, so neither reaches the play screen -- the debug "
        "overlay has to be armed on the selection screen before the game "
        "starts. The claim was written into DISC-263 and the source comment "
        "and was never true",
    ),
    (
        "Modelled as `>=` here",
        "DISC-257",
        "the breach test is an equality in the ROM (`$5658 CMP #$14`) and in "
        "the remake (`d == HULL_BREACH_THRESHOLD`); DISC-204 reversed the `>=` "
        "modelling because it made the game unwinnable, and overshooting 20 to "
        "burn a room out is a real tactic",
    ),
    (
        "no win route is reachable",
        "DISC-253",
        "all three routes are demonstrated end to end in test_winnability.py; "
        "DISC-204 closed DISC-199 the same day it was filed by finding the "
        "hull-breach equality, and the claim outlived its own fix by eight days",
    ),
    (
        "the superset stays deliberately",
        "DISC-246",
        "the ATTACK row's window IS decodable and is now the ROM's own: "
        "`$8C76` reaches `$064E` via `$8CD9`, gated by `find_crew_with_alien "
        "($8C49)` plus `$8CE1 CPY $64FB` -- both plain simulation state. "
        "D-169 was reasoning about `$64BB`, which is presentational but does "
        "not gate this row",
    ),
    (
        "it has no `$7569` deck entry of its own",
        "DISC-244",
        "`tbl_room_deck` has 35 entries and `$758B` gives the Narcissus deck "
        "3 -- a sentinel one past the three real decks, which is exactly what "
        "makes `update_item_sprite ($7C3D)` park its location pointer",
    ),
    (
        "Decks split 10/14/10",
        "DISC-244",
        "`$7569` splits the 34 mapped rooms 9/16/9, with the Narcissus alone "
        "on sentinel deck 3; 10/14/10 came from the `$80D3` reading D-116 "
        "replaced",
    ),
    (
        "row 23 stays blank in every capture",
        "DISC-245",
        "row 23 carries the Alien's attack banner (`$8BC4` -> `$0798`); the "
        "captures were taken while nothing was attacking",
    ),
    (
        "the rule between the red and purple blocks",
        "DISC-244",
        "row 12 is where `Leave item` goes (`list_room_items $83E0` -> "
        "`$05FE`), not a rule",
    ),
    (
        "the panel occupies rows 1-17",
        "DISC-232",
        "the CONTROL panel is rows 0-18 (19 rows), live-confirmed from colour "
        "RAM: LT_GREY 0, LT_BLUE 1-7, LT_GREEN 8-10, LT_RED 11, YELLOW 12, "
        "PURPLE 13-17, WHITE 18",
    ),
    (
        "15 | quit | WHITE paper",
        "DISC-232",
        "`quit` is on row 18, not 15; row 15 is inside the PURPLE Special "
        "block and the live capture shows GET JONES sitting there",
    ),
    (
        "The opening death then moves only the victim",
        "DISC-229",
        "$5074-$5077 also moves BRETT, every game: two tables read with one "
        "RNG draw put him in the victim's vacated room, so the opening always "
        "seats the survivors 3 in COMMDCENTR and 3 in MESS",
    ),
    (
        "new_game genuinely redistributes survivors",
        "DISC-229",
        "exactly one character moves - Brett backfills the victim's room "
        "($5077 STA $793C). D-014 saw the 3+3 result and inferred a general "
        "redistribution rule that does not exist",
    ),
    (
        "the real NOTICE screen is a clean left-flush block",
        "DISC-218",
        "MENU1's lines 505-555 give each line its own indent - 9, 7, 8, 8, 13, "
        "9, 7 - and boot_015_notice.png shows the ragged left edge plainly",
    ),
    (
        "right-anchored to column 39",
        "DISC-217",
        "the `$7A10` template is 42 bytes and its morale field is 9 wide, which "
        "fits 'confident' exactly - nothing overruns, so nothing is anchored. "
        "The 7-wide field that needed anchoring came from reading the template "
        "as 40 columns",
    ),
    (
        "its own full-width 40-column line",
        "DISC-217",
        "the status template is 42 bytes copied out in two pieces, to row 19 "
        "column 10 and row 21 column 10 - it is not one full-width line",
    ),
    (
        '"ALSO HERE" does not appear anywhere',
        "DISC-217",
        "`$7EDB` holds `also here:` in the ROM's own lowercase; D-117 searched "
        "for the shouted form and concluded the label might be invented",
    ),
    (
        "encounter side is real and **deterministic**",
        "D-177",
        "the Alien's encounter rolls twice: `$4152 CMP #$07` skips the attack "
        "entirely on 7 of 16 actions, then one victim is picked from up to three",
    ),
    (
        "both callers of `alien_wound_crew",
        "D-177",
        "both callers of `$5354` pass `$64C3` (the ANDROID's slot) as the "
        "attacker, so it is the android's routine; the Alien's is `$413C`",
    ),
    (
        "callers of `$5354` gate",
        "D-177",
        "the same claim with the routine's name elided. NB the *discriminating* "
        "word is `gate`: DISCOVERIES' own D-177 entry correctly says both "
        "callers `pass $64C3`, so matching on 'callers of `$5354`' alone flags "
        "the correction as if it were the error",
    ),
    (
        "both callers of ``alien_wound_crew",
        "D-177",
        "as above, in reST-quoted form",
    ),
)


def test_no_superseded_claim_survives_in_the_source() -> None:
    """Prose a later discovery disproved must not remain in `src/` or the registers.

    This guards the project's most expensive failure: a corrected mechanic
    whose *explanation* was left behind, so the next reader trusts it. It has
    happened four times (D-159/163/164/177), each time costing a re-derivation
    of something already known.

    **Scope widened 2026-08-08** from `src/` alone, which was too narrow: a
    top-level document was found still asserting an open item that had been
    closed weeks earlier. A false claim in a document is *more* dangerous than
    one in a docstring, because it reads as settled.

    `docs/history/` is deliberately excluded — it is the archive, and its whole
    job is to preserve what was written at the time. `DISCOVERIES.md` and
    `DECISIONS.md` are excluded for the mirror-image reason: they are where a
    superseded claim gets quoted and corrected, so scanning them makes every
    correction look like the error it documents.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    # DISCOVERIES.md and DECISIONS.md are exempt: quoting a superseded claim in
    # order to correct it is exactly their job, and every entry that does so
    # would otherwise fail this test. The guard's purpose is to keep dead claims
    # out of the code and out of the documents that are read as current.
    EXEMPT = {"REVIEW.md", "DISCOVERIES.md", "DECISIONS.md"}
    # Both registers now live under docs/; the scan below walks the root,
    # so they are out of its reach either way. Named for the day it widens.
    targets = sorted((root / "src").rglob("*.py"))
    targets += sorted(p for p in root.glob("*.md") if p.name not in EXEMPT)

    offenders = []
    for path in targets:
        text = path.read_bytes().decode("utf-8", errors="replace")
        for phrase, discovery, truth in SUPERSEDED_CLAIMS:
            for match in re.finditer(re.escape(phrase), text):
                # An annotated history row is fine: the correction travels with
                # the claim. Look ahead for it on the same logical line.
                line_end = text.find("\n", match.end())
                tail = text[match.end(): line_end if line_end != -1 else len(text)]
                if "[SUPERSEDED" in tail:
                    continue
                offenders.append(
                    f"{path.relative_to(root)}: {phrase!r} "
                    f"(disproved by {discovery} — {truth})"
                )
    assert not offenders, "superseded claims still present: " + "; ".join(offenders)


    root = Path(__file__).resolve().parent.parent / "src"
    offenders = []
    for path in sorted(root.rglob("*.py")):
        text = path.read_bytes().decode("utf-8", errors="replace")
        for phrase, discovery, truth in SUPERSEDED_CLAIMS:
            if phrase in text:
                offenders.append(
                    f"{path.relative_to(root)}: {phrase!r} "
                    f"(disproved by {discovery} — {truth})"
                )
    assert not offenders, "superseded claims still in src/: " + "; ".join(offenders)


def test_prose_does_not_reference_symbols_that_no_longer_exist() -> None:
    """Every ``_symbol`` named in a comment or docstring must still be defined.

    The self-maintaining half: no table to curate, and it catches the commonest
    drift for free — a rename that updates the code and leaves the narrative
    pointing at the old name. `_move_timer` survived D-159's rename to
    `_roll_hunt` in `alien.py`'s module header exactly that way.

    Scoped to leading-underscore names, so it only polices this package's own
    private vocabulary where a dangling reference is unambiguously stale.

    **Escape hatch.** Prose that names a *removed* symbol on purpose — the "the
    remake used to run two clocks" kind of narrative — is legitimate history and
    should stay. Write those without backticks (`a separate turn-timer dict`),
    which reads better anyway: backticks mean "you can go look at this."

    It pays for itself beyond prose: `_map_right_edge` was flagged here and
    turned out to be assigned in four places and read in none.
    """
    import ast
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "src" / "alien_remake"

    defined = set()
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_bytes().decode("utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                defined.add(node.attr)

    allowed = defined | {"__main__", "__init__", "__future__"}
    pattern = re.compile(r"``(_[A-Za-z_][A-Za-z0-9_]*)``|`(_[A-Za-z_][A-Za-z0-9_]*)`")

    dangling = []
    for path in sorted(root.rglob("*.py")):
        for n, line in enumerate(
            path.read_bytes().decode("utf-8", errors="replace").splitlines(), 1
        ):
            for match in pattern.finditer(line):
                name = match.group(1) or match.group(2)
                if name and name not in allowed:
                    dangling.append(f"{path.name}:{n} references `{name}`")
    assert not dangling, (
        "prose names symbols that do not exist (a rename left the text behind): "
        + "; ".join(dangling)
    )

#: The `D-nnn` collisions that already exist in `DISCOVERIES.md`, frozen so the
#: problem cannot grow while the fix is pending.
#:
#: Two causes. `D-009`-`D-014` are a second numbering series begun 2026-07-09
#: that collided with the 2026-07-01/02 one; `D-146` is a plain same-day
#: duplicate. Roughly 195 citations point at these seven ids, and disambiguating
#: each by context is a judgement call, so they are recorded rather than
#: silently renumbered.
KNOWN_DUPLICATE_DISCOVERY_IDS = frozenset(
    {"D-009", "D-010", "D-011", "D-012", "D-013", "D-014", "D-146"}
)


def test_no_new_duplicate_discovery_ids() -> None:
    """Every `D-nnn` in `DISCOVERIES.md` must be unique, bar the known seven.

    A duplicated id makes every citation of it ambiguous, and the citation is
    the whole point of the register — `[C $4152] D-177` is worthless if D-177
    could be two different findings. The namespace is already overloaded with
    `DECISIONS.md`, which numbers its own entries the same way; that is
    documented at the top of `DISCOVERIES.md` rather than fixed, because fixing
    it means rewriting ~195 citations by hand.

    This test does the part that *is* mechanical: it stops the problem growing.
    A new duplicate fails here immediately, while the seven historical ones stay
    listed above as a debt rather than an accident.
    """
    import collections
    import re
    from pathlib import Path

    text = (Path(__file__).resolve().parent.parent / "docs" / "re"
     / "DISCOVERIES.md").read_text(
        encoding="utf-8"
    )
    # Headings only — the index table and prose cite ids constantly.
    ids = re.findall(r"^## ((?:DISC-|D-)\d+[a-z]?)\b", text, re.M)
    counts = collections.Counter(ids)
    dupes = {name for name, n in counts.items() if n > 1}

    new = dupes - KNOWN_DUPLICATE_DISCOVERY_IDS
    assert not new, (
        f"new duplicate discovery id(s): {sorted(new)}. Every D-nnn must name "
        "exactly one finding, or every citation of it is ambiguous. Use the next "
        "free number, or a letter suffix (D-080b) for a genuine follow-up."
    )
    healed = KNOWN_DUPLICATE_DISCOVERY_IDS - dupes
    assert not healed, (
        f"{sorted(healed)} are no longer duplicated — remove them from "
        "KNOWN_DUPLICATE_DISCOVERY_IDS so the guard keeps ratcheting."
    )


def test_the_discovery_index_covers_every_entry() -> None:
    """`DISCOVERIES.md`'s index must list every heading, with a working anchor.

    The index exists so a reader can find one entry without loading 8,700
    lines. An index that has quietly fallen behind the body is worse than none,
    because it is read *instead of* the body.
    """
    import re
    from pathlib import Path

    text = (Path(__file__).resolve().parent.parent / "docs" / "re"
     / "DISCOVERIES.md").read_text(
        encoding="utf-8"
    )
    headings = re.findall(r"^## ((?:DISC-|D-)\d+[a-z]?)\s*(.*)$", text, re.M)
    start = text.index("| # | Date | Finding |")
    table = text[start : text.index("\n---\n", start)]
    rows = re.findall(r"^\| \[((?:DISC-|D-)\d+[a-z]?)\]\(#([^)]+)\)", table, re.M)

    assert len(rows) == len(headings), (
        f"index lists {len(rows)} entries but the body has {len(headings)}; "
        "run `python tools/reindex_discoveries.py`"
    )
    anchors = {
        re.sub(r"[^a-z0-9]+", "-", f"{num} {title}".lower()).strip("-")
        for num, title in headings
    }
    broken = [num for num, anchor in rows if anchor not in anchors]
    assert not broken, f"index anchors no longer resolve: {broken}"


def test_no_live_invented_marker_survives_in_the_source() -> None:
    """`src/` must carry zero `[INVENTED]` markers (D-193).

    `docs/re/FAITHFULNESS.md` defines the tag as "no basis in the code — **must
    be removed or replaced**, never ships knowingly". The register reached zero
    on 2026-08-08, so this pins it: a new one is either a real invention that
    must not ship, or a marker left behind after the invention was fixed.

    Both survivors were the second kind, and both had been stale for a month.
    `constants.py`'s fear bands said "INVENTED band boundaries — RESOLVED" on one
    line, contradicting itself. `flow.py` warned that the Ctrl+1/Ctrl+2 chord was
    unenforced and a bare "1" would select — but `pygame_app.py` had been
    checking `KMOD_CTRL` on GAME_SELECTION since FV-1c2. Anyone auditing
    fidelity by grepping this tag would have chased two closed gaps.

    `[?]` is deliberately *not* pinned: an honest open question is a legitimate
    state for a replica, and the register is at zero of those too, but a future
    `[?]` should be filed rather than blocked by a gate.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "src"
    offenders = []
    for path in sorted(root.rglob("*.py")):
        for n, line in enumerate(
            path.read_bytes().decode("utf-8", errors="replace").splitlines(), 1
        ):
            if "[INVENTED" in line:
                offenders.append(f"{path.relative_to(root)}:{n}")
    assert not offenders, (
        "[INVENTED] markers in src/: " + ", ".join(offenders) + ". Either the "
        "behaviour has no basis in the ROM and must not ship, or it was fixed "
        "and the marker outlived it — delete the marker in that case."
    )
