"""The endgame COMPETENCE RATING — decoded from the ROM (D-070).

The ending screen's "COMPETENCE RATING:   %" (`$63F8`) was a `--%` placeholder
in the remake. The real score lives in `$6411` and is built by the ending
routine at `$60A9`-`$62B5`; every term below is read off that code, not chosen.

Per **surviving** crew member (the loop at `$61A5`-`$6217`, slots 1..7, gated on
``health >= 2`` at `$61B0` — the same acting floor used everywhere else)::

    61B7  LDA $6411 / CLC / ADC #$04   ; +4 for surviving
    61C6  CMP #$04 / BCC / INC $6411   ; +1 more if health >= 4 ("O.K.")
    61E2  LDA $7D55,Y / BNE            ; composure 0 (INSANE)...
    61F6  LDA $6411 / SEC / SBC #$03   ; ...costs 3

Note `$61C6`'s `CMP #$04` is the **same absolute threshold** as `health_band`
(D-069) — an unwounded-enough crew member is worth one more point, and the
boundary is not relative to their own maximum.

Then a ship-condition term (`$6231`-`$6278`), which the ROM computes **only
when `$64CF == 0`** — the same flag that selects the "lost" ending at `$60AE`.
It walks the 34-entry room-damage table `$653F` and accumulates into `$640F`::

    d == 0            -> nothing
    d >= 1            -> $640F += d
    5 <= d < 15       -> $640F += 10   ($624D ADC #$0A)
    d >= 15           -> $640F += 25   ($6259 ADC #$19)
    after each room: if $640F >= 70 ($6265 CMP #$46) -> stop, NO bonus
    if it survives all 34 rooms: $6411 += (70 - $640F)   ($626E-$6278)

Finally `$621D CMP #$65` clamps a score of 101 or more to **0**, and
`$6288`-`$62B5` renders the result as exactly **two digits** (repeated
subtraction of 10 for the tens, `ADC #$B0` to make reverse-video screen codes),
so the displayed rating is 0-99.

**PV-22 closed 2026-08-07 (D-163) — the old note here was a misreading.** It
claimed "the `$64CF == 0` gate means the damage bonus is added on the *lost*
ending and skipped otherwise, which reads counter-intuitively." Re-tracing
`select_outcome ($60A9)` shows the branch structure is not that at all::

    60AE  LDA $64CF / BEQ $60D0        ; no result flag -> draw_ending_lost
    60D8  LDA $7D45 / CMP #$32         ; the ALIEN's damage (slot 0), >= 50?
    60DD  BCC $60F9                    ;   no  -> $60F9
    60DF  LDA #$05 / STA $6411         ;   yes -> rating 5, print $6372
    60F9  LDA $64CF / BEQ $611C        ; (damage < 50) lost -> $611C
    60FE  LDA $7935 / CMP #$22 / BNE $60DF   ; Alien not in the NARCISSUS
    6105  LDA $64E3 / BEQ $60DF
    611C  LDA #$78 / STA $6411         ; rating $78

The damage test at `$60D8` is **not gated on `$64CF` at all** — it runs on
every ending. `$64CF` is only consulted *afterwards*, and it is not merely
"auto-destruct armed": it is the **result flag**, written by both
`set_result_win ($58E5)` and `clear_result_flag ($5DC8)`, which is why
`$60AE`'s zero branch is the lost ending. The counter-intuitive reading was an
artefact of collapsing two independent branches into one.

None of this is modelled: the remake has no Competence Rating (D-034), so
`$6411` has no counterpart here. Recorded so the next reader does not re-derive
a wrong conclusion from the old note.
"""

from __future__ import annotations

from .state import GamePhase, GameState

# All [C], addresses inline above.
SURVIVOR_POINTS = 4          # $61BB ADC #$04
UNWOUNDED_BONUS = 1          # $61CA INC   (health >= HEALTH_OK_AT_LEAST)
INSANE_PENALTY = 3           # $61FA SBC #$03
DAMAGE_BUDGET = 70           # $6265 CMP #$46 / $626E LDA #$46
DAMAGE_MINOR_AT = 5          # $6245 CMP #$05
DAMAGE_MAJOR_AT = 15         # $6249 CMP #$0F
DAMAGE_MINOR_ADD = 10        # $6251 ADC #$0A
DAMAGE_MAJOR_ADD = 25        # $625D ADC #$19
SCORE_OVERFLOW_AT = 101      # $621D CMP #$65 -> clamp to 0
ROOM_SLOTS = 34              # $626A CPY #$22

# **Base score, set BEFORE the per-survivor accrual (D-077).** `select_outcome`
# seeds `$6411` from the Alien's fate and then the survivor loop adds to it:
#   $60DF  LDA #$05 / STA $6411   ; the Alien is dead (damage >= 50)
#   $611C  LDA #$78 / STA $6411   ; 120 — the eggs-unleashed ending
# 120 is deliberately past the `$621D CMP #$65` clamp, so that worst outcome
# scores **0**. Corroborated live: a capture showing "The Alien is dead" /
# "All crew lost" reported exactly **"Competence Rating: 05%"** — base 5, no
# survivors to accrue, and a wrecked ship forfeiting the damage bonus.
SCORE_ALIEN_DEAD = 5         # $60DF
SCORE_EGGS_UNLEASHED = 120   # $611C (clamps to 0)


def _damage_score(state: GameState) -> int | None:
    """`$640F` after the room walk, or ``None`` if it hit the budget early.

    ``None`` means the ROM's `$6265 BCS $627B` fired — the walk stops and **no**
    bonus is added at all (not "a bonus of zero"): a badly damaged ship simply
    never reaches `$626E`.
    """
    total = 0
    for damage in list(state.room_damage.values())[:ROOM_SLOTS]:
        if damage > 0:
            total += damage
            if damage >= DAMAGE_MAJOR_AT:
                total += DAMAGE_MAJOR_ADD
            elif damage >= DAMAGE_MINOR_AT:
                total += DAMAGE_MINOR_ADD
        if total >= DAMAGE_BUDGET:
            return None
    return total


def _base_score(state: GameState) -> int:
    """`$6411`'s seed from the Alien's fate, before any survivor accrual."""
    alien = state.alien
    if alien is not None and not alien.alive:
        return SCORE_ALIEN_DEAD          # $60DF
    if not any(c.alive for c in state.crew.values()
               if c.id != state.android_id):
        return SCORE_EGGS_UNLEASHED      # $611C — clamps to 0
    return 0


def competence_rating(state: GameState) -> int:
    """The two-digit COMPETENCE RATING the ending screen prints (0-99)."""
    from . import constants

    score = _base_score(state)
    for crew in state.crew.values():
        # [C $61A5] D-080: the ANDROID is skipped before the health test — it
        # never counts as a survivor for the rating, however well it did.
        if crew.id == state.android_id:
            continue
        if crew.health < constants.CREW_INCAPACITATED_BELOW:
            continue                      # $61B0 CMP #$02 / BCC -> skip
        score += SURVIVOR_POINTS
        if crew.health >= constants.HEALTH_OK_AT_LEAST:
            score += UNWOUNDED_BONUS      # $61C6
        if crew.is_insane:
            score -= INSANE_PENALTY       # $61F6
    if score >= SCORE_OVERFLOW_AT:
        return 0                          # $6221
    if state.phase is GamePhase.LOST:     # the `$64CF == 0` gate
        damage = _damage_score(state)
        if damage is not None:
            score += DAMAGE_BUDGET - damage
    # `$6288`-`$62B5` renders exactly two digits, so the value wraps there.
    return max(0, score) % 100
