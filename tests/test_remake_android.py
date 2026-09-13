"""The hidden ANDROID (`$64C3`) — D-080.

The instructions say the player is *"not knowing which member of the crew is an
android"*, and the game never prints the word ANDROID anywhere (a screen-code
search of all of ALIEN.prg finds nothing) — you are meant to deduce it from
behaviour. The remake did not model it at all until a player reported seeing it.
"""

from __future__ import annotations

import random

from alien_remake.core import constants
from alien_remake.core.modes import DeathVariant, choose_android, choose_opening_death
from alien_remake.core.scoring import competence_rating
from alien_remake.core.sim import Simulation
from alien_remake.core.special_options import SpecialOption, SpecialOptionType
from alien_remake.core.state import GamePhase


def test_candidate_pools_are_the_rom_tables() -> None:
    """[C $50EC / $50FC] Neither pool is the whole crew."""
    assert constants.OPENING_VICTIM_CANDIDATES == ("dallas", "kane", "lambert")
    assert constants.ANDROID_CANDIDATES == ("dallas", "kane", "ash", "parker")
    # $6062-$6069's hard-coded preset is KANE (victim) + ASH (android) — the
    # film's own pairing, and what identifies $64C3 beyond doubt.
    assert "kane" in constants.OPENING_VICTIM_CANDIDATES
    assert "ash" in constants.ANDROID_CANDIDATES


def test_opening_victim_is_never_outside_the_rom_pool() -> None:
    """The remake used to draw uniformly from all seven, so it could open by
    killing Ripley, Ash, Parker or Brett — which the original never does."""
    roster = ["dallas", "kane", "ripley", "ash", "lambert", "parker", "brett"]
    seen = {
        choose_opening_death(roster, DeathVariant.ORIGINAL, random.Random(s))
        for s in range(300)
    }
    assert seen <= set(constants.OPENING_VICTIM_CANDIDATES)
    assert len(seen) == 3, "all three candidates should be reachable"


def test_android_is_never_the_opening_victim() -> None:
    """[C $5081] `CMP $64C2 / BEQ re-roll` — the ROM re-rolls until they differ."""
    roster = ["dallas", "kane", "ripley", "ash", "lambert", "parker", "brett"]
    for seed in range(200):
        rng = random.Random(seed)
        victim = choose_opening_death(roster, DeathVariant.ORIGINAL, rng)
        android = choose_android(roster, victim, rng)
        assert android != victim
        assert android in constants.ANDROID_CANDIDATES


def test_simulation_picks_an_android_distinct_from_the_victim() -> None:
    for seed in range(40):
        sim = Simulation(rng=random.Random(seed))
        aid = sim.state.android_id
        assert aid in constants.ANDROID_CANDIDATES
        assert aid != sim.state.opening_dead_crew_id


def _stage(seed: int = 3):
    """A sim with a healthy victim parked in the android's room."""
    sim = Simulation(rng=random.Random(seed))
    android = sim.state.crew[sim.state.android_id or "ash"]
    android.alive, android.health = True, 5
    target = next(
        c for c in sim.state.crew.values()
        if c.alive and c.id != android.id and c.health >= 4
    )
    target.room_id = android.room_id
    target.fear = 4
    return sim, android, target


def test_android_wounds_crew_sharing_its_room() -> None:
    """[C $546D] The behaviour a player actually notices."""
    sim, android, target = _stage()
    before = target.health
    sim._apply_android_attack()
    assert target.health == before - 1


def test_the_revealed_androids_victim_gates_are_the_52f1_scan() -> None:
    """**[C $5313-$5331] D-152 — the gates the REVEALED android really uses.**

    The old version of this test cited `$5459`, which belongs to a different
    routine (`sub_char_special` action code 3). The revealed android's own
    turn is `$52F1`, and its scan differs: it skips a victim **inside a
    duct**, and its composure test reads the **BASE** cell (`$7D55`) and
    skips only on **exactly 0** — not the effective value against a
    threshold of 2. So merely shaken crew ARE fair game.
    """
    sim, android, target = _stage()
    sim.state.android_revealed = True
    # Keep the Alien away: $52FC makes the android flee rather than attack
    # when it shares a room with the surfaced creature.
    assert sim.state.alien is not None
    sim.state.alien.room_id = None

    # Base composure 1 -> still attacked ($5324 skips only on 0).
    target.fear = 1
    before = target.health
    sim._apply_android_attack()
    assert target.health == before - 1, "shaken is not spared; only 0 is"

    # Base composure 0 -> skipped.
    sim2, android2, target2 = _stage(seed=5)
    sim2.state.android_revealed = True
    assert sim2.state.alien is not None
    sim2.state.alien.room_id = None
    target2.fear = 0
    for mate in sim2.state.crew.values():
        if mate.id != android2.id and mate.room_id == android2.room_id:
            mate.fear = 0            # nobody else in the room is a target
    before2 = target2.health
    sim2._apply_android_attack()
    assert target2.health == before2

    # Health < 2 -> skipped ($531D).
    sim3, android3, target3 = _stage(seed=7)
    sim3.state.android_revealed = True
    assert sim3.state.alien is not None
    sim3.state.alien.room_id = None
    for mate in sim3.state.crew.values():
        if mate.id != android3.id and mate.room_id == android3.room_id:
            mate.health = 1
    healths = {
        c.id: c.health for c in sim3.state.crew.values()
        if c.id != android3.id and c.room_id == android3.room_id
    }
    sim3._apply_android_attack()
    for cid, h in healths.items():
        assert sim3.state.crew[cid].health == h, "collapsed crew are left alone"


def test_the_revealed_android_cannot_reach_into_a_duct() -> None:
    """**[C $5318] `LDA $6501,Y / BNE skip`** — a victim inside the ducting is
    skipped outright. We never checked this, so the android could hurt crew
    hiding in the walls."""
    sim, android, target = _stage()
    sim.state.android_revealed = True
    assert sim.state.alien is not None
    sim.state.alien.room_id = None
    for mate in sim.state.crew.values():
        if mate.id != android.id and mate.room_id == android.room_id:
            mate.in_duct = True
    healths = {
        c.id: c.health for c in sim.state.crew.values()
        if c.id != android.id and c.room_id == android.room_id
    }
    sim._apply_android_attack()
    for cid, h in healths.items():
        assert sim.state.crew[cid].health == h


def test_the_revealed_android_flees_a_surfaced_alien_instead_of_attacking() -> None:
    """**[C $52FC-$5306]** Sharing a room with the *surfaced* Alien sends the
    android to `char_wander` before the victim scan is ever reached — it runs
    rather than attacking. A ducted Alien is not an encounter, so the scan
    proceeds as normal."""
    sim, android, target = _stage()
    sim.state.android_revealed = True
    assert sim.state.alien is not None
    sim.state.alien.room_id = android.room_id
    sim.state.alien.in_duct = False
    target.fear = 4
    before = target.health
    sim._apply_android_attack()
    # The load-bearing assertion is that the victim scan was never reached.
    # (Whether it visibly moves is a separate matter: the ROM's route tables
    # contain self-loops, so `char_wander` legitimately leaves it put in some
    # rooms -- see test_panic_in_a_self_looping_room_leaves_the_crew_put.)
    assert target.health == before, "it should flee, not attack"

    # ...and a DUCTED Alien is not an encounter ($5301), so the scan runs.
    sim.state.alien.in_duct = True
    sim._apply_android_attack()
    assert target.health == before - 1


def test_android_ignores_crew_in_other_rooms() -> None:
    sim, android, target = _stage()
    other = next(
        c for c in sim.state.crew.values()
        if c.alive and c.id not in (android.id, target.id)
    )
    other.room_id = "cryo_vault" if android.room_id != "cryo_vault" else "computer"
    before = other.health
    sim._apply_android_attack()
    assert other.health == before


def test_android_cannot_enter_hypersleep() -> None:
    """[C $593C] `guard_target_is_player` RTSes for the android."""
    sim = Simulation(rng=random.Random(7))
    aid = sim.state.android_id
    assert aid is not None
    # ENTER HYPERSLEEP is also room-gated to the CRYO VAULT (D-028), so put
    # both candidates there — this isolates the android gate from that one.
    android = sim.state.crew[aid]
    other = next(c for c in sim.state.crew.values() if c.alive and c.id != aid)
    android.room_id = other.room_id = "cryo_vault"
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.ENTER_HYPERSLEEP, crew_id=aid)
    ), "the android must be refused"
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.ENTER_HYPERSLEEP, crew_id=other.id)
    ), "a normal crew member in the vault must succeed"


def test_android_does_not_count_toward_the_competence_rating() -> None:
    """[C $61A5] It is skipped before the health test, however well it did."""
    sim = Simulation(rng=random.Random(11))
    state = sim.state
    state.phase = GamePhase.WON
    for c in state.crew.values():
        c.alive, c.health, c.fear = False, 0, 4
    android = state.crew[state.android_id or "ash"]
    android.alive, android.health = True, 6
    # A lone surviving android scores nothing for the player.
    assert competence_rating(state) == 0


# --- the behaviour the player actually remembers: dropped orders (D-080b) ----

def _with_alien(seed: int = 3):
    sim = Simulation(rng=random.Random(seed))
    android = sim.state.crew[sim.state.android_id or "ash"]
    android.alive, android.health, android.in_duct = True, 5, False
    assert sim.state.alien is not None
    sim.state.alien.room_id = android.room_id
    return sim, android


def test_android_silently_drops_orders_while_with_the_alien() -> None:
    """[C $5294-$5299] The pending action is zeroed and skipped — no message,
    no refusal. This is what reads as "it stopped responding to my input"."""
    from alien_remake.core.orders import Order, OrderOutcome, OrderType

    sim, android = _with_alien()
    outcome = sim._apply_order(Order(android.id, OrderType.REMOVE_GRILL))
    assert outcome is OrderOutcome.BLOCKED
    assert sim._android_ignores_order(android)


def test_android_obeys_normally_when_the_alien_is_elsewhere() -> None:
    """The gate is co-location with the Alien, not the android itself."""
    sim, android = _with_alien()
    assert sim.state.alien is not None
    sim.state.alien.room_id = (
        "cryo_vault" if android.room_id != "cryo_vault" else "computer"
    )
    assert not sim._android_ignores_order(android)


def test_a_hurt_android_panics_instead_of_stonewalling() -> None:
    """[C $528A/$528F] Below health 4 the ROM goes to `char_wander`, so the
    silent-drop path does not apply."""
    sim, android = _with_alien()
    android.health = constants.ANDROID_OBEY_MIN_HEALTH - 1
    assert not sim._android_ignores_order(android)


def test_ordinary_crew_are_never_ignored() -> None:
    sim, android = _with_alien()
    other = next(
        c for c in sim.state.crew.values() if c.alive and c.id != android.id
    )
    other.room_id = android.room_id
    assert not sim._android_ignores_order(other)


# --- being found out ($64CC) -------------------------------------------------

def test_android_is_revealed_only_after_the_alien_is_hurt() -> None:
    """[C $52A7] `LDA $7D45 / CMP #$06` — the crew must have been fighting it."""
    sim, android = _with_alien(seed=9)
    assert sim.state.alien is not None
    witness = next(
        c for c in sim.state.crew.values()
        if c.alive and c.id != android.id
    )
    witness.room_id, witness.in_duct = android.room_id, False
    witness.health, witness.fear = 5, 4

    sim.state.alien.damage = constants.ANDROID_REVEAL_ALIEN_DAMAGE - 1
    sim._reveal_android()
    assert not sim.state.android_revealed

    sim.state.alien.damage = constants.ANDROID_REVEAL_ALIEN_DAMAGE
    sim._reveal_android()
    assert sim.state.android_revealed


def test_reveal_needs_a_witness_in_the_androids_room() -> None:
    sim, android = _with_alien(seed=13)
    assert sim.state.alien is not None
    sim.state.alien.damage = constants.ANDROID_REVEAL_ALIEN_DAMAGE + 4
    for c in sim.state.crew.values():
        if c.id != android.id:
            c.room_id = "cryo_vault" if android.room_id != "cryo_vault" else "computer"
    sim._reveal_android()
    assert not sim.state.android_revealed


def test_a_broken_witness_does_not_reveal_it() -> None:
    """[C $52CA] `LDA $7D55,Y / BEQ skip` — composure 0 is skipped."""
    sim, android = _with_alien(seed=17)
    assert sim.state.alien is not None
    sim.state.alien.damage = constants.ANDROID_REVEAL_ALIEN_DAMAGE + 4
    for c in sim.state.crew.values():
        if c.id != android.id:
            c.room_id, c.in_duct = android.room_id, False
            c.health, c.fear = 5, constants.FEAR_MIN     # broken
    sim._reveal_android()
    assert not sim.state.android_revealed


# --- the ACTIVATED path, once $64CC is set (D-084) ---------------------------

def test_a_revealed_android_obeys_nothing_at_all() -> None:
    """[C $526A] Once `$64CC` is set the android is diverted to `$52F1`, which
    only ever attacks or wanders — it never reaches `dispatch_char_action`. So
    the silent order-drop stops being conditional on the Alien being present."""
    sim = Simulation(rng=random.Random(21))
    android = sim.state.crew[sim.state.android_id or "ash"]
    assert sim.state.alien is not None
    sim.state.alien.room_id = "cryo_vault" if android.room_id != "cryo_vault" else "computer"
    assert not sim._android_ignores_order(android)      # dormant, Alien elsewhere
    sim.state.android_revealed = True
    assert sim._android_ignores_order(android)          # revealed -> always


def test_a_revealed_android_wanders_when_it_finds_nobody() -> None:
    """[C $5339] `char_wander` rather than standing still."""
    sim = Simulation(rng=random.Random(23))
    android = sim.state.crew[sim.state.android_id or "ash"]
    android.alive, android.health = True, 5
    for c in sim.state.crew.values():
        if c.id != android.id:
            c.room_id = "shuttlebay"
    sim.state.android_revealed = True
    start = android.room_id
    moved = False
    for _ in range(12):
        sim._apply_android_attack()
        if android.room_id != start:
            moved = True
            break
    assert moved, "a revealed android with no target should wander"


def test_a_revealed_android_does_not_keep_the_game_alive() -> None:
    """[C $5B5F-$5B67] The "anyone still aboard?" scan skips a revealed
    android, so a lone one is still ALL CREW LOST."""
    from alien_remake.core.state import GamePhase

    sim = Simulation(rng=random.Random(29))
    aid = sim.state.android_id
    assert aid is not None
    for c in sim.state.crew.values():
        if c.id != aid:
            c.alive, c.health = False, 0
    sim.state.crew[aid].alive, sim.state.crew[aid].health = True, 6
    sim.state.android_revealed = True
    sim.advance()
    assert sim.state.phase is GamePhase.LOST


def test_an_UNrevealed_lone_android_still_counts_as_crew() -> None:
    """The exemption is gated on `$64CC`, not on being the android."""
    from alien_remake.core.state import GamePhase

    sim = Simulation(rng=random.Random(31))
    aid = sim.state.android_id
    assert aid is not None
    for c in sim.state.crew.values():
        if c.id != aid:
            c.alive, c.health = False, 0
    sim.state.crew[aid].alive, sim.state.crew[aid].health = True, 6
    sim.state.android_revealed = False
    sim.advance()
    assert sim.state.phase is GamePhase.RUNNING


def test_reveal_locks_the_android_itself_not_its_victim() -> None:
    """[C $52D4] `LDA $7214 / STA $64CC` stores the **acting** slot.

    `$7214` has exactly one writer, `$723E STY $7214`, which records the
    character whose turn is being dispatched — so on the android's reveal the
    value written to `$64CC` is the android's own slot. `guard_alien_present`
    (`$7740 CPY $64CC / BEQ`) then refuses to select it, and `$52DA STA $D021`
    flashes the background with the same number.

    The old model wrote the *victim's* slot from the attack path instead, which
    permanently benched every crew member the android ever touched.
    """
    sim, android = _with_alien(seed=9)
    assert sim.state.alien is not None
    witness = next(
        c for c in sim.state.crew.values() if c.alive and c.id != android.id
    )
    witness.room_id, witness.in_duct = android.room_id, False
    witness.health, witness.fear = 5, 4

    assert sim.state.locked_crew_id is None
    sim.state.alien.damage = constants.ANDROID_REVEAL_ALIEN_DAMAGE
    sim._reveal_android()

    assert sim.state.android_revealed
    assert sim.state.locked_crew_id == android.id
    assert sim.state.locked_crew_id != witness.id


def test_the_attack_path_never_locks_anyone() -> None:
    """[C $5439] The wound handler only wounds; `$64CC` is written at `$52D7`."""
    sim, android, target = _stage()
    sim._apply_android_attack()
    assert target.health < 5
    assert sim.state.locked_crew_id is None


def test_an_unrevealed_android_does_not_attack() -> None:
    """[C $5265] `$526D BEQ $5272` — with `$64CC` clear the android takes the
    ordinary `dispatch_char_action` road and never reaches the scan at `$52F1`
    that ends in the attack. Only `$526F JMP $52F1`, taken once `$64CC` is set,
    does. Attacking from tick 0 was an invention that ground the android's
    roommate down to health < 2 within the first two minutes of play.
    """
    sim = Simulation(rng=random.Random(5))
    calls: list[bool] = []
    original = sim._apply_android_attack

    def _spy() -> None:
        calls.append(sim.state.android_revealed)
        original()

    sim._apply_android_attack = _spy  # type: ignore[method-assign]

    assert not sim.state.android_revealed
    for _ in range(400):
        sim.advance()

    # It may or may not have been revealed during those 400 ticks, but every
    # attack that did happen must have come *after* the reveal.
    assert all(calls), "the android attacked while still passing for crew"


def test_an_unrevealed_android_does_not_block_the_launch() -> None:
    """**[C $5BD3-$5BD8] D-152.** The left-behind scan passes over the android
    while `$64CC` is clear (`CPY $64C3 / BNE` then `LDA $64CC / BEQ skip`), so
    an undiscovered android left aboard the Nostromo never refuses the launch.
    Once revealed it counts like any other crew member."""
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim = Simulation(rng=random.Random(9))
    aid = sim.state.android_id
    assert aid is not None
    evac = sim.ship.evac_rooms()
    assert evac
    aboard = next(iter(evac))
    # Everyone aboard except the android, and the cat caught.
    for c in sim.state.crew.values():
        c.alive, c.health, c.room_id = True, 5, aboard
    sim.state.crew[aid].room_id = "commdcentr"        # left behind
    sim.state.jones_caught = True

    # Not yet found out -> the launch still succeeds.
    sim.state.android_revealed = False
    assert sim.apply_special_option(SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS))

    # Same setup, but revealed -> it now blocks like anyone else.
    sim2 = Simulation(rng=random.Random(9))
    aid2 = sim2.state.android_id
    assert aid2 is not None
    for c in sim2.state.crew.values():
        c.alive, c.health, c.room_id = True, 5, aboard
    sim2.state.crew[aid2].room_id = "commdcentr"
    sim2.state.jones_caught = True
    sim2.state.android_revealed = True
    assert not sim2.apply_special_option(
        SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS)
    )


def test_the_android_does_not_attack_during_an_attack_sequence() -> None:
    """**[C $5309] PV-12/D-165** — `LDA $6562 / BEQ $5311 / JMP char_wander`.

    `$6562` is the attack-sequence latch: `$8CD9 INC $6562` raises it as an
    Alien/crew encounter fires and `reset_attack_state ($8C85)` clears it on
    the next move pass, so it is live for exactly one pass. While it is up the
    android flees instead of pressing its own attack. The remake emits
    `ATTACK_ALERT` on that same ROM event and wipes the cue list each
    `advance`, so the cue list is the latch.
    """
    import random

    from alien_remake.core.alien import Alien
    from alien_remake.core.crew import CrewMember, Role
    from alien_remake.core.nostromo import nostromo_ship
    from alien_remake.core.sound import ATTACK_ALERT, SoundCue
    from alien_remake.core.state import GameState

    def staged() -> Simulation:
        room = "corridor_1"
        android = CrewMember("ash", "Ash", Role.SCIENCE_OFFICER, room)
        victim = CrewMember("ripley", "Ripley", Role.WARRANT_OFFICER, room)
        state = GameState(
            crew={"ash": android, "ripley": victim},
            alien=Alien(room_id=None),
            android_id="ash",
            android_revealed=True,
        )
        return Simulation(state=state, ship=nostromo_ship(), rng=random.Random(3))

    # Baseline: with no sequence running it wounds its roommate.
    sim = staged()
    before = sim.state.crew["ripley"].health
    sim._apply_android_attack()
    assert sim.state.crew["ripley"].health < before, "it should attack normally"

    # $5309: with the latch up it wanders instead, and nobody is hurt.
    sim = staged()
    before = sim.state.crew["ripley"].health
    sim.state.sound_cues.append(SoundCue(ATTACK_ALERT, crew_id="ripley"))
    assert sim._attack_sequence_active()
    start = sim.state.crew["ash"].room_id
    sim._apply_android_attack()
    assert sim.state.crew["ripley"].health == before, "no attack while $6562 is up"
    assert sim.state.crew["ash"].room_id != start, "char_wander moves it instead"
