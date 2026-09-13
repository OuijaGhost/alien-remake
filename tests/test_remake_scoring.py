"""The endgame COMPETENCE RATING (D-070, `$60A9`-`$62B5`).

Every expected number here is read off the ROM's own ending routine, with the
address inline, so a drift shows up as a citation mismatch rather than a taste
argument.
"""

from __future__ import annotations

from alien_remake.core import scoring
from alien_remake.core.crew import CrewMember, Role
from alien_remake.core.scoring import competence_rating
from alien_remake.core.state import GamePhase, GameState


def _member(cid: str, health: int, fear: int = 4) -> CrewMember:
    return CrewMember(cid, cid.upper(), Role.CAPTAIN, "A", health=health, fear=fear)


def _won(*crew: CrewMember) -> GameState:
    """A WON state, so the `$64CF` damage term is skipped."""
    return GameState(phase=GamePhase.WON, crew={c.id: c for c in crew})


def test_constants_cite_the_rom() -> None:
    assert scoring.SURVIVOR_POINTS == 4      # $61BB ADC #$04
    assert scoring.UNWOUNDED_BONUS == 1      # $61CA INC $6411
    assert scoring.INSANE_PENALTY == 3       # $61FA SBC #$03
    assert scoring.DAMAGE_BUDGET == 70       # $6265 CMP #$46
    assert scoring.DAMAGE_MINOR_ADD == 10    # $6251 ADC #$0A
    assert scoring.DAMAGE_MAJOR_ADD == 25    # $625D ADC #$19
    assert scoring.SCORE_OVERFLOW_AT == 101  # $621D CMP #$65
    assert scoring.ROOM_SLOTS == 34          # $626A CPY #$22


def test_healthy_survivor_scores_five() -> None:
    """$61BB +4 for surviving, $61CA +1 more at health >= 4."""
    assert competence_rating(_won(_member("a", health=5))) == 5


def test_wounded_survivor_scores_four() -> None:
    """health 2-3 clears the $61B0 floor but misses the $61C6 bonus."""
    assert competence_rating(_won(_member("a", health=3))) == 4


def test_incapacitated_crew_score_nothing() -> None:
    """$61B0 CMP #$02 / BCC -> skipped entirely, not counted as a survivor."""
    assert competence_rating(_won(_member("a", health=1))) == 0
    assert competence_rating(_won(_member("a", health=0))) == 0


def test_insane_survivor_costs_three() -> None:
    """$61E2 reads composure; exactly 0 appends "IS INSANE" and $61FA subtracts 3."""
    sane = _member("a", health=5, fear=4)
    insane = _member("b", health=5, fear=0)
    assert insane.is_insane and not sane.is_insane
    assert competence_rating(_won(sane)) == 5
    assert competence_rating(_won(insane)) == 5 - 3


def test_scores_accumulate_across_the_roster() -> None:
    state = _won(
        _member("a", health=6),          # +5
        _member("b", health=2),          # +4
        _member("c", health=5, fear=0),  # +5 -3
        _member("d", health=1),          # skipped
    )
    assert competence_rating(state) == 5 + 4 + (5 - 3)


def test_overflow_clamps_to_zero() -> None:
    """$621D CMP #$65 / BCS -> LDA #$00. 21 healthy survivors would be 105."""
    crew = [_member(f"c{i}", health=5) for i in range(21)]
    assert competence_rating(_won(*crew)) == 0


# --- the ship-condition term, only on the lost ending ($6229 gate) -----------

def _lost(damage: dict[str, int], *crew: CrewMember) -> GameState:
    """A LOST state. Note an EMPTY roster is not neutral: with nobody alive the
    ROM seeds `$6411` with 120 (the eggs-unleashed base, `$611C`), which the
    `$621D` clamp turns into 0 — so tests isolating the damage term must supply
    at least one survivor."""
    return GameState(
        phase=GamePhase.LOST,
        crew={c.id: c for c in crew},
        room_damage=damage,
    )


def test_undamaged_ship_earns_the_full_budget_on_a_loss() -> None:
    """$626E: `70 - $640F`, and an untouched ship has $640F == 0."""
    assert competence_rating(_lost({}, _member("a", health=5))) == 5 + 70


def test_minor_and_major_damage_use_the_rom_bands() -> None:
    """A room at 5-14 adds its raw value +10; at 15+ it adds raw +25."""
    live = _member("a", health=3)          # +4, no unwounded bonus, base 0
    # one room at 6 -> 6 + 10 = 16 -> bonus 70-16 = 54
    assert competence_rating(_lost({"r": 6}, live)) == 4 + 70 - 16
    # one room at 20 -> 20 + 25 = 45 -> bonus 70-45 = 25
    assert competence_rating(_lost({"r": 20}, live)) == 4 + 70 - 45
    # below the minor band: raw only
    assert competence_rating(_lost({"r": 4}, live)) == 4 + 70 - 4


def test_a_wrecked_ship_forfeits_the_bonus_entirely() -> None:
    """$6265 BCS $627B stops the walk and skips $626E — so it is NO bonus, not
    a bonus of zero. Two rooms at 20 reach 90, past the 70 budget."""
    assert competence_rating(_lost({"a": 20, "b": 20}, _member("x", health=5))) == 5


def test_damage_term_is_skipped_unless_the_game_was_lost() -> None:
    """$6229 LDA $64CF / BNE -> $627B. The same damage scores differently."""
    crew = _member("a", health=5)
    won = GameState(phase=GamePhase.WON, crew={"a": crew}, room_damage={"r": 4})
    assert competence_rating(won) == 5
    assert competence_rating(_lost({"r": 4}, crew)) == 5 + (70 - 4)


# --- the base score seeded from the Alien's fate (D-077) ---------------------

def test_alien_dead_seeds_the_score_with_five() -> None:
    """$60DF `LDA #$05 / STA $6411`, set BEFORE the survivor accrual.

    Corroborated live: a capture showing "The Alien is dead" / "All crew lost"
    reported exactly "Competence Rating: 05%" — base 5, nobody left to accrue,
    and a wrecked ship forfeiting the damage bonus.
    """
    from alien_remake.core.alien import Alien
    from alien_remake.core.scoring import SCORE_ALIEN_DEAD

    dead_alien = Alien(room_id=None, alive=False)
    st = GameState(phase=GamePhase.WON, alien=dead_alien,
                   crew={"a": _member("a", health=5)})
    assert competence_rating(st) == SCORE_ALIEN_DEAD + 5


def test_no_survivors_seeds_120_which_clamps_to_zero() -> None:
    """$611C `LDA #$78` = 120, deliberately past the $621D clamp, so the
    eggs-unleashed ending scores 0."""
    from alien_remake.core.scoring import SCORE_EGGS_UNLEASHED

    assert SCORE_EGGS_UNLEASHED >= 101
    st = GameState(phase=GamePhase.WON, crew={"a": _member("a", health=0)})
    assert competence_rating(st) == 0
