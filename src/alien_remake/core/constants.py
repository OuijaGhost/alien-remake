"""Fixed simulation constants for the Alien remake core.

Every value traces to ``docs/spec/GAME_SPEC.md``. Values the spec marks ``[?]``
(calibration parameters not recoverable from the manual + structural decompile)
are flagged here too and tuned in playtest; they have deliberately simple
starting defaults.

**Every placeholder marker in this package is filed.** See the **placeholder
register (`PV-nn`)** at the end of ``todo.md``: one entry per open placeholder,
each naming the routine that would settle it (``[static]``) or the capture that
would measure it (``[live]``). A ratchet test
(``tests/test_fv3_drift_guards.py::test_placeholder_count_does_not_grow``)
fails if the marker count grows without a matching PV entry. Closing one means
citing an address or a capture — **never** deleting the marker because the
value "looks right".

(This paragraph deliberately spells out "placeholder marker" rather than using
the marker itself, so the pointer does not inflate the count it describes.)
"""

from __future__ import annotations

from .gamedata_snapshot import MORALE_WORDS as _MORALE_WORDS

# --- Timing -------------------------------------------------------------------
# **One remake tick = one pass of the ROM's main loop at $719D.** That loop is
# free-running, not frame-locked, and it is what decrements the per-character
# action timers, so it — not the IRQ — is the world clock.
#
# The IRQ ($4D19) is a red herring for game logic: its divider reloads #$08 but
# fires on the wrap below zero, so it ticks every NINE jiffies, and the four
# routines it drives are sprite animation and sound only.
#
# Move costs, in loop units: Alien 60 per surface move and 40 in a duct; crew
# 3-4 per room (per-crew, `gamedata_snapshot.CREW_WALK_TICKS`); Jones moves
# once every 40 passes (`JONES_MOVE_TICKS`, `$88B6`) — not "5", which was an
# earlier `[?]` byte (`JONES_WALK_TICKS`) that D-153/D-156 later showed lands
# on `var_frame_divider` and was never a cat timer at all.
#
# Derivation: DISCOVERIES D-038, D-063, D-153, D-156.
JIFFY_HZ = 60.0
IRQ_JIFFIES_PER_ANIM_TICK = 9
# The IRQ-derived animation rate (~6.67 Hz). Kept because it is what the IRQ
# actually paces; it is NOT the world clock (that was the old approximation).
ANIM_HZ = JIFFY_HZ / IRQ_JIFFIES_PER_ANIM_TICK

# Measured on the real disk under emulation, not inferred: an execution
# checkpoint on `main_loop ($719D)` counted 158 passes against 19,739,184
# emulated cycles (20.035 s) = **7.886 Hz**, i.e. ~124,900 cycles per pass.
# Counting emulated cycles rather than wall time makes it immune to host
# latency. The spread across shorter trials (7.83-8.30 Hz) is real: the loop is
# free-running, so a pass is ~6.36 PAL frames but not a whole number of them.
#
# Corroborated in the same capture: the Alien's action timer `$64EE[0]`
# decremented exactly once per counted pass, reloading 60 and 40 — the surface
# and in-duct costs from the decoded tables.
#
# Derivation: DISCOVERIES D-063, D-075.
MAIN_LOOP_HZ = 7.886
# One remake tick = one main-loop pass, so the world clock IS the loop rate.
TICK_HZ = MAIN_LOOP_HZ

# --- Oxygen: there isn't any ---------------------------------------------------
# The C64 game has **no oxygen system**, so neither does the remake. The
# manual's 7,500-unit budget documents a mechanic the shipped game never
# implemented, and modelling it here used to end every run after ~7,500 ticks.
#
# Four independent checks agree: no monotonically-decreasing cell exists
# anywhere in game RAM during play; the program's 117 strings contain no
# OXYGEN/AIR/SUFFOCATE (only "AIRLOCK"); the status line ($7A10) decodes to
# damage and morale only; and the jiffy clock $A0-$A2 is never read in the whole
# classified region.
#
# Derivation: DISCOVERIES D-062.

# --- Personality Control System (GAME_SPEC §5, §11 #1) -----------------------
# Each crew member has a hidden state-of-mind value in `$7D55`, running **0..10
# and capped at 10** by `raise_crowd_fear ($4CE8)`. **0 is BROKEN, 10 is calm** —
# it is composure, not fear, and reading the polarity backwards inverts every
# comparison in the file (see the word table below). Mother surfaces it
# qualitatively; it does not gate whether an order is obeyed.
FEAR_MIN = 0
FEAR_MAX = 10

# There is no obey-probability curve: the decoded order path has no compliance
# roll, so crew obey regardless of composure. What composure *does* drive is the
# action tempo (`fear_alert $4E16`) and a panic branch (`$52C0` ->
# `char_wander $5203`), implemented in `sim._apply_panic_wander`.
#
# A panicking crew member does not flee in a chosen direction — `char_wander`
# re-rolls the RNG and picks from the **same five route tables the Alien uses**
# ($7A82/$7AA5/$7AC8), so panic is an Alien-style random walk.
#
# Three paths reach it and their precedence is still unresolved: co-location
# with the Alien ($5252), low health ($528A, `$7D45,Y < 4`), and a third
# ($52A4-$52E3) that additionally needs the Alien to have taken >= 6 damage
# before it scans for a co-located, disturbed, healthy crew member.
#
# Derivation: DISCOVERIES D-018, D-026.

# The five words Mother reports for a crew member's state of mind.
#
# **High is GOOD.** [C $7DC5] `fear_band` indexes a 10-byte-stride string table
# at $7D13 with `idx = 4 - value`, clamped to 0 for value >= 5 — so 0/1/2/3 map
# to BROKEN/SHAKEN/UNEASY/STABLE and anything >= 4 reads CONFIDENT. The remake
# calls the value *composure* for that reason; reading it as "fear" inverts
# every comparison, a mistake that survived here for weeks.
#
# Gotcha: the word on screen **lags the real value**. `fear_band` runs only from
# `init_char_turn`, and only when the turn rotation reaches the crew member the
# panel is showing, so `$6571` (displayed) trails `$7D55` (true). Two crew can
# show the same word on different underlying values.
#
# Derivation and the live captures: DISCOVERIES D-024, D-059.
ITEM_COMPOSURE: dict[str, int] = {
    "elctrc_prd": 1,
    "incineratr": 2,
    "fire_extng": 1,
    "harpn_gun": 2,
    "laser_pist": 2,
    "spanner": 1,
    # tracker / net / cat_box: `$45D3` = $FF, no composure effect at all.
}

# The words themselves live in the game's own `$7D13` table, decoded into
# `gamedata_snapshot.MORALE_WORDS`, so their case is the ROM's ("confident",
# not "CONFIDENT"). Aliased here because this is where callers look.
MORALE_BANDS: tuple[str, ...] = _MORALE_WORDS

# --- The Alien: movement + combat ---------------------------------------------
# Each time the Alien picks an action, `alien_choose_move ($8A36)` rolls uniform
# 0-15 ($888F): **0-11 is a surface move** to a neighbour drawn from one of five
# roll-banded route tables (`ROUTE_BAND_BOUNDS`), costing 60 units; **12-15 is
# entering its room's duct** through the grille, costing 40. No grille means the
# duct rolls are re-rolled among the surface outcomes.
#
# There is **no hunt**: nothing in the routine senses or seeks the nearest crew
# member. The Alien is a weighted random walk, and modelling it as a stalker is
# the single biggest way to get its feel wrong.
#
# `$6581` (=70) is *not* this timer. It belongs to `alien_ai ($8A74)`, the
# separate in-duct dispatcher that walks duct-to-duct via `$80F5`/`$8117`/
# `$8139`/`$815B`. The remake simplifies that to "hide in the same room for
# `ALIEN_DUCT_TICKS`, then re-emerge", so no code path uses 70 today.
#
# Derivation: DISCOVERIES D-038.
ALIEN_MOVE_TICKS = 60   # [C $8A4A] surface-move timer (was 70, corrected)
# **CLOSED 2026-09-05 (P9-B goal session, live capture).** This used to read
# "[?] FV-2 live observation (2026-07-11): watched ... for 50 continuous real
# seconds ... NEITHER changed at all. This is a bounding data point, not a
# rate ... 50s wasn't long enough ... a clean rate calibration needs a much
# longer (multi-minute) observation window." That window has now been run:
# 600s idle, no input, sampling `$7935`/`$653F` once a second. Within a
# single sustained room-linger (the Alien re-deciding "stay" repeatedly), the
# room-damage array incremented at ~7-8s intervals - matching
# `ALIEN_MOVE_TICKS=60` at the measured real-hardware rate (`MAIN_LOOP_HZ`
# ~7.886 Hz) almost exactly: 60/7.886 ≈ 7.61s predicted. FV-2's "bounding, not
# a rate" caveat no longer applies; the 60-tick timer is now live-confirmed,
# not just decoded. Full capture: DISC-319.
ALIEN_DUCT_TICKS = 40   # [C $89E0] enter-duct timer, unaffected by D-038
ALIEN_ROLL_SIDES = 16
# Duct threshold is 12: `alien_choose_move ($8A36)` does `CMP #$0C / BCC` — roll
# 0-11 picks a surface route table, roll 12-15 enters a duct (§8.10).
ALIEN_DUCT_THRESHOLD = 12   # roll >= 12 -> duct

# --- The Alien IN the ducts — decoded [C $8A74], P-6 2026-08-02 --------------
# `alien_ai ($8A74)` is a *separate* roller from the surface one, and it walks
# the **compass (duct) graph**, one band per direction::
#
#     8A9E  CMP #$03 / BCS   ; roll 0-2  -> $80F5,Y  NORTH
#     8AB4  CMP #$06 / BCS   ; roll 3-5  -> $8117,Y  EAST
#     8ABE  CMP #$09 / BCS   ; roll 6-8  -> $8139,Y  SOUTH
#     8AC8                   ; roll 9-12 -> $815B,Y  WEST
#     8AA5  ADC #$80         ; bit 7 set = "still in the ducts"
#     8AAB  LDA $6581        ; ...for the Alien's normal move duration
#
# and roll **13-15** takes `$8A92 LDA $7935 / STA $64E6` — the destination is
# the current room **without** bit 7, which `alien_apply_move` reads as
# *emerge here* (`$8B6F BCC $8B7E`). That is how the Alien comes back out.
ALIEN_DUCT_DIR_BANDS = (3, 6, 9)   # $8A9E/$8AB4/$8ABE — upper edges of N/E/S
ALIEN_DUCT_EMERGE_FROM = 13        # $8A8B CMP #$0D / BCC -> move; else emerge
# `$8A7A`: while the Alien's current room still HAS its grille, roll 15 is
# re-rolled ($8A7C-$8A83) — so a trapped Alien is slightly likelier to keep
# crawling than to try to come out.
ALIEN_DUCT_BLOCKED_REROLL = 15

# **Bursting out** ([C $8B84]). Whenever the Alien tries to cross a grille that
# is still in place — emerging into a room (`$8B7F`) or ducking into one from
# the surface (`$8BB4`) — it does not move. It **clears that room's `$8676`
# grille byte** (the grille is gone for good), pauses `$8B8C LDA #$28` = 40
# ticks, and raises the event flag `$651B` — the "GRILLE BURSTS OPEN" message
# at `$8BC4`.
ALIEN_BURST_TICKS = 40             # $8B8C LDA #$28
# On the real ship the surface move reads one of five route tables by roll band
# (0-2, 3-4, 5-6, 7-8, 9-11 → tables 0..4). ROUTE_BAND_BOUNDS are the upper
# edges of the first four bands (§8.10).
ROUTE_BAND_BOUNDS = (3, 5, 7, 9)

# **[C $89BF] The Alien has two movement distributions, chosen by the grille.**
# `alien_ai_dispatch` reads its room in the `$8676` grille table — nonzero while
# the grille is intact, zeroed once removed or burst — and branches:
#
#   * grille **open**  -> `alien_choose_move ($8A36)`: ducts on 12-15 (**25%**),
#     twelve surface outcomes split 3/2/2/2/3 across the route tables.
#   * grille **shut**  -> `$89C4`: ducts on 15 only (**6.25%**), fifteen surface
#     outcomes split evenly 3/3/3/3/3.
#
# So the Alien is **four times more likely to take a duct whose grille is already
# open**, and ranges more widely on the surface when it cannot. Opening a grille
# genuinely invites it in.
#
# Derivation: DISCOVERIES D-087.
ALIEN_DUCT_THRESHOLD_GRILLE_OPEN = 12   # $8A39 CMP #$0C
ALIEN_DUCT_THRESHOLD_GRILLE_SHUT = 15   # $89C7 CMP #$0F
ROUTE_BAND_BOUNDS_GRILLE_OPEN = (3, 5, 7, 9)     # $8A40/$8A50/$8A5A/$8A64
ROUTE_BAND_BOUNDS_GRILLE_SHUT = (3, 6, 9, 12)    # $89E8/$8A12/$8A1C/$8A26

# **[C $8AAB `LDA $6581`]** duct-to-duct travel has its OWN duration — the
# `$6581` byte (70), not the surface move's literal `$3C` (60). D-038 corrected
# `ALIEN_MOVE_TICKS` from 70 to 60 and noted `$6581` belonged to "a distinct,
# currently-unmodeled mechanic"; that mechanic is now modelled (P-6), so the
# value comes back for the case it actually belongs to. **Crawling the ducts is
# slower than walking a corridor**, which is why the Alien can vanish for a
# long stretch and then reappear somewhere far away.
ALIEN_DUCT_TRAVEL_TICKS = 70
# Compass fallback (synthetic maps without the real route tables): roll bands
# 0-2 N, 3-5 S, 6-8 E, else W.
ALIEN_DIR_BOUNDS = (3, 6, 9)

# Escalating pursuit (full disassembly §8.10, D-012): a WOUNDED Alien hunts
# harder. The hunt lock `$64B4` is set when `rng(0-15) < $4781`, where the
# aggression accumulator `$4781` grows by `alien_damage/4` each action; while
# hunting the Alien acts on the shorter pursuit timer (`$14` = 20) instead of the
# normal 70. So the more you wound it, the faster it comes after you.
ALIEN_PURSUIT_TICKS = 20        # `$14` move timer while hunting
AGGRESSION_DAMAGE_DIVISOR = 4   # `$4781 += $7D45[0] / 4` per action

# (The invented `LETHAL_ITEM_IDS` "lethal subset" was removed in FV-1.6, 2026-07-11:
# there is no lethal subset and no kill odds — combat is deterministic per item.
# "Can this item wound the Alien?" is now `ITEM_ATTACK_DAMAGE[id] > 0`.)

# --- Attack damage per item [C $4940] -----------------------------------------
# `resolve_attack ($4940)` dispatches on the **item instance id** (found by
# `find_room_object`, stashed at `$4BEF`). There is no RNG on this path at all —
# damage is a pure function of what you swung.
#
#   $FF        no object, abort            |  $11 (CAT BOX)  abort
#   < 6        +1 wound                    |  ELCTRC PRD 0-2, INCINERATR 3-5
#   >= $12     +1 wound                    |  SPANNER 18-19
#   $10 NET    no wound; entangles         |  `ALIEN_NET_ENTANGLE_TICKS`
#   6-7 TRACKER  +1 wound, item destroyed  |  "TRACKER IS SMASHED"
#   8-11 FIRE EXTNG  no wound, charge path
#   $0C HARPN GUN    **+5, guaranteed**    |  `$49F2 ADC #$05`
#   13-15 LASER PIST charge path, then +1
#
# Every wound path re-tests `CMP #$32`, so the Alien dies at 50 accumulated.
ITEM_ATTACK_DAMAGE: dict[str, int] = {
    "elctrc_prd": 1,    # ids 0-2   ($4976 CMP #$06 / BCC -> INC $7D45)
    "incineratr": 1,    # ids 3-5
    "spanner": 1,       # ids 18-19 ($498D CMP #$12 / BCS -> INC $7D45)
    "harpn_gun": 5,     # id 12     ($49F6 ADC #$05) — one shot, always lands
    "laser_pist": 1,    # ids 13-15 (after the charge check)
    "net": 0,           # id 16 — no wound, but a real entangle effect: see
                        # ALIEN_NET_ENTANGLE_TICKS below (D-033).
    # D-033 (2026-07-24), corrected from 0: the "TRACKER SMASHED" path
    # (`$49B5`) falls through to `JMP $497A`, the same `INC $7D45` wound
    # every other +1 item uses — an earlier pass at this trace missed the
    # trailing jump and wrote "no wound". The tracker is also destroyed on
    # this specific use (`clear_object_at_loc2`), same as the net below.
    "tracker": 1,       # ids 6-7 — smashed on the Alien, +1 wound, destroyed
    "fire_extng": 0,    # ids 8-11 — fights fire, no wound
    "cat_box": 0,       # id 17 — rejected outright
}
# Items consumed outright the moment they land this specific attack use
# (`clear_object_at_loc2` at both `$49AB` (net) and `$49C2` (tracker), D-033)
# — distinct from the charge-based items above, which merely decrement.
ITEM_DESTROYED_ON_ATTACK: frozenset[str] = frozenset({"net", "tracker"})
# The net's real effect (D-033, `$49A2-$49A8`): entangling the Alien adds a
# flat 80 ticks to its own move timer (`$64EE += $50`), delaying its next
# move — a genuine crowd-control item, not a no-op message.
ALIEN_NET_ENTANGLE_TICKS = 80

# --- Alien combat: CUMULATIVE wound damage (full disassembly, DISASSEMBLY §8.8) ---
# The decoded combat routine `resolve_attack ($4940)` does NOT kill in one shot.
# A landed hit runs `INC $7D45[0]` (the Alien's wound counter); the Alien dies
# only once that counter reaches `$32` (50). So killing it is a war of attrition,
# not a lucky single blow — the earlier single-shot ATTACK_KILL_CHANCE model was
# an approximation and is replaced by this.
ALIEN_DAMAGE_TO_KILL = 50   # [C $4980/$49FB] `CMP #$32` -> endgame_dispatch
#: **DEC-044, UPDATED only.** ORIGINAL keeps the ROM's own 50 - ROOM_
#: BREACH_GATE_HARPOON/OTHER above only fire for UPDATED, so ORIGINAL's
#: fight is unaffected and needed no re-derivation. UPDATED's own gate means
#: one room can no longer absorb the swings a 50-wound fight needs, so
#: `tools/winnability_sweep.py` re-swept this alongside the AP sweep: 50
#: wins 0/16 seeds even with a gate-aware, room-hopping scripted hunter; 10
#: lands 6/16 (37.5%), inside the "hard but not impossible" ~30-60% band the
#: owner set as the target for a default difficulty. A real player - who
#: stashes items, remembers which rooms are burnt out, and reads the
#: tracker rather than blindly re-approaching - should clear that bar more
#: often than the scripted bot does, not less.
UPDATED_ALIEN_DAMAGE_TO_KILL = 10
# (The invented `ATTACK_HIT_CHANCE = 6/16` and `ATTACK_WOUND_AMOUNT` were removed
# in FV-1.6: `resolve_attack` never rolls — the `CMP #$06` at $4976 compares the
# item instance id, not an RNG value. Per-item damage is `ITEM_ATTACK_DAMAGE`.)

# **[C $8ED0]** The Alien corrodes the room it occupies: `guard_6562 ($8EBD)`
# does `INC $653F,X` behind four gates —
#
#     $89AC  LDX $64B4 / BNE      ; not in the pursuit/aggro state  [NOT MODELLED]
#     $8EBD  LDA $6562 / BNE rts  ; no attack sequence on screen    [NOT MODELLED]
#     $8EC3  LDA $6501 / BNE rts  ; the Alien is not in a duct      -> `surfaced`
#     $8EC8  LDA $6563 / BEQ rts  ; ...and $6563 is set
#
# **Measured live.** With every crew member teleported away from the Alien so
# nothing else could touch the array, `$653F` climbed steadily across many
# rooms: over one 30 s window rooms 3/14/15/20/32/33/34 all gained, and room 34
# went 12 -> 15 and latched alarm stage 2 (critical) inside the first minute.
# Corrosion is real and fast.
#
# The rate here is one point per action cycle, which is the right order of
# magnitude for that observation. [?] the exact cadence, and the two unmodelled
# gates, still want a proper trace.
#: **The magnitude is decoded; the CADENCE is the `[?]` (DISC-288, measured
#: 2026-08-29, CLOSED the same day).** `$8ED0` is a single `INC`, so one point
#: per application, and that was never in doubt once the opcode was read.
#:
#: **The cadence, now decoded.** `$8EC0` applies it only when both gates pass:
#: `$6501` (the Alien's own in-duct flag - an Alien in the ducting damages
#: nothing) and `$6563`, which `$8AE4` clears every pass and sets only when
#: `$7935 == $64E6`, i.e. the Alien has **arrived at its target room**. So it
#: marks the room it settles in, never the ones it passes through.
#:
#: Measured live with no player input: **6 points in 100 s** with the Alien
#: settled in one room, and **1 in 102 s** while it roamed.
#:
#: **`alien.py` already applies all of this** - `advance_alien` computes
#: `corrode` from the arrived flag, the attack sequence and the hunting latch,
#: and only calls through when surfaced. An earlier note here said the gates
#: were missing; that was read off this call site without looking at the caller
#: and is retracted in DISC-288.
#:
#: **The rate gap (P-9), corrected as of DISC-306/307/308 — DISC-290's 0.13/3x
#: headline is superseded.** DISC-290's 0.13 was the smallest, noisiest sample
#: in the thread (n=4 events, 360s) and undercounted by reading only the
#: Alien's *current* room rather than the whole `$653F` array. Two independent
#: 600s captures reading `$653F` whole agree to within 4%: the disk corrodes
#: at **0.286-0.296** damage per surface room-change, against the remake's
#: **~0.41** - a **~1.4x gap**, not 3x. Still not settled enough to act on
#: (STILL OPEN, todo.md) — 1.4x is real convergence but small enough it could
#: be capture-window variation. **Do not change this value or the corrode gate
#: on the strength of anything measured so far.** Bracket any eventual change
#: with `tools/winnability_sweep.py` both ways.
#:
#: **The mechanism itself has no gap.** A 2026-09-05 live capture (DISC-319,
#: P9-B goal session) found all 13 observed corrode events, with zero
#: exceptions, landed on a sample where the Alien's own room had **not**
#: changed since the previous sample - never on a room-change sample. That is
#: an exact match to the gated mechanism above, live-confirmed on top of the
#: disassembly citation, not just consistent with it.
ROOM_DAMAGE_ALIEN_PER_ACTION = 1  # [C $8ED0] INC $653F,X for the Alien's room
#: **DISC-325/DEC-046 — an empirical calibration, not the ROM's own literal
#: reading, applied under ORIGINAL too.** The gate above (`guard_6562`) was
#: independently confirmed correct down to the exact byte (DISC-319: 13/13
#: observed corrode events landed on a no-room-change sample, zero
#: exceptions) and the magnitude (`ROOM_DAMAGE_ALIEN_PER_ACTION = 1`) was
#: settled separately (DISC-288). The ROM reads as unconditional given
#: those two facts — corrode every time the gate is open, `rate = 1.0` — yet
#: the remake still ran ~1.4x hotter than the disk across many independent
#: measurement sessions (P-9, DISC-292 through DISC-323): remake ~0.41 vs.
#: two independent 600s live captures agreeing within 4% at 0.286-0.296
#: damage per surface room-change (DISC-306/307, the most-trusted numbers
#: in the thread). A further live-oracle session (2026-09-07) meant to find
#: the mechanism was blocked by an input-injection fault in that emulator
#: session unrelated to the game itself, and per the owner's own
#: instruction not to keep re-measuring past that point: calibrated
#: directly to the trusted disk numbers instead of the ROM's literal `1.0`,
#: rather than leaving the gap open indefinitely. `0.71` is
#: `(0.286+0.296)/2 / 0.41`, rounded. Applies to ORIGINAL — this is a
#: fidelity correction to the base rate, not an added rule — via
#: `Alien.corrode_credit`'s accumulator (see its own comment) so it needs no
#: RNG (ORIGINAL's other seeded rolls are untouched).
ALIEN_CORRODE_RATE = 0.71
#: **DEC-044, UPDATED only — independent of `ALIEN_CORRODE_RATE`, not
#: layered on top of it.** `1/6` reproduces DEC-044's original "once every
#: 6 corrode-eligible actions" throttle exactly (6 * 1/6 = 1.0 credit), so
#: DISC-325's ORIGINAL-only rate correction above changes nothing about
#: UPDATED's own already-swept numbers - `Simulation.weapon_breach_gates`
#: selects this value instead of `ALIEN_CORRODE_RATE`, it does not multiply
#: the two together. Composing them was considered and rejected: UPDATED's
#: throttle was tuned against a fixed absolute rate to hit
#: `ALIEN_DAMAGE_TO_KILL`'s own target band (DEC-044), not against
#: whatever ORIGINAL's rate happens to be, and stacking the two would have
#: meant re-sweeping DEC-044/DEC-045 for no benefit.
UPDATED_ALIEN_CORRODE_RATE = 1 / 6
# Room damage from a landed hit comes in two flavours, selected purely by
# **whether the harpoon was used**:
#
#   harpoon ($49EB `CMP #$0C`) -> $4A87: breach if damage >= 5,  else +15
#   anything else              -> $4AF0: breach if damage >= 14, else +6
#
# The harpoon is both the hardest hitter against the Alien and by far the
# messiest for the room it is fired in.
#
# **Known gap:** the ROM's breach check is a *pre-add, per-hit* gate, evaluated
# only at the moment of a landed weapon hit. The remake checks post-add, once
# per tick, against a single `HULL_BREACH_THRESHOLD`. Closing it means
# restructuring the hull-breach check in `sim`, not editing this table.
#
# Derivation: DISCOVERIES D-027.
ROOM_DAMAGE_PER_ATTACK = 6            # non-harpoon landed hit (`$4AFD` +6)
ROOM_DAMAGE_PER_ATTACK_HARPOON = 15   # harpoon landed hit (`$4A95` +15)
#: **[C $4A8D / $4AF6] The weapon breach gates are PRE-ADD (DISC-258).**
#: A landed hit reads the room's *current* damage first and breaches outright
#: if it is already at or past the gate; only below it does the weapon add::
#:
#:     4A87  LDY $457F / LDA $653F,Y      harpoon: the room's damage
#:     4A8D  CMP #$05 / BCC $4A94         < 5  -> add 15
#:     4A91  JMP hull_breach              >= 5 -> the ship goes
#:
#:     4AF0  LDY $457F / LDA $653F,Y      anything else
#:     4AF6  CMP #$0E / BCC $4AFD         < 14 -> add 6
#:     4AFA  JMP hull_breach              >= 14 -> the ship goes
#:
#: **DECODED, NOT APPLIED UNDER ORIGINAL - `[?]` there only.** Wiring these
#: in at the values above was tried, measured and reverted: 16 seeded games,
#: zero wins, because a room holes the ship long before the Alien takes the
#: 50 damage it needs. ORIGINAL keeps them off and the values above exactly
#: as decoded, permanently — this is the one behaviour DEC-039 would
#: otherwise keep matched between the two presets, and DEC-044 records why
#: it doesn't here.
#:
#: **DEC-044 (2026-09-06): retuned below and turned ON under UPDATED.**
#: `ROOM_BREACH_GATE_HARPOON` and `ROOM_BREACH_GATE_OTHER` are only ever read when
#: `Simulation.weapon_breach_gates` is set (see
#: `core/sim/orders.py::_resolve_attack_order`) — never under ORIGINAL, so
#: retuning them here does not touch the ROM's own decoded numbers, which
#: stay on the record just above (`>= 5` / `>= 14`) as what the disk
#: actually does. Chosen instead to satisfy the owner's own target: a room
#: at zero pre-existing damage survives at least 5 landed non-harpoon hits
#: before breaching. `ROOM_DAMAGE_PER_ATTACK` stays 6, so the gate needs to
#: clear `4 * 6 = 24`; `26` does that (hits 1-5 land at 0/6/12/18/24, all
#: under 26; hit 6 would check 30 >= 26 and breach). The harpoon gate is
#: scaled by the same ratio the two per-attack amounts already have
#: (15/6 = 2.5x), not re-derived from scratch — the harpoon stays the
#: messier weapon, it just moves with the other gate rather than being left
#: stale at a number tuned for a threshold that no longer applies to it.
#:
#: `ALIEN_DAMAGE_TO_KILL` was re-swept against these numbers (see
#: `tools/winnability_sweep.py`) rather than left at 50 - a room allows
#: several swings before the gate fires, and the Alien needing fifty
#: one-point hits was already identified as expecting a fight that moves
#: across the ship (DISC-289); whether the remake's crew can sustain one is
#: number. Something else in the original
#: must make it survivable - per-hit damage, hit frequency, or a room-damage
#: decay nobody has traced - and until that is found, applying the gate ships an
#: unwinnable game. **If you wire these up, re-run the winnability sweep first.**
#: Derivation: DISCOVERIES DISC-258, DISC-204.
#: DEC-044: retuned for UPDATED, not the ROM's own `>= 5` — see the comment
#: block above. Scaled from `ROOM_BREACH_GATE_OTHER` by the same 15/6 ratio
#: `ROOM_DAMAGE_PER_ATTACK_HARPOON`/`ROOM_DAMAGE_PER_ATTACK` already have.
ROOM_BREACH_GATE_HARPOON = 65
#: DEC-044: retuned for UPDATED, not the ROM's own `>= 14`. `26` is the
#: smallest value clearing `4 * ROOM_DAMAGE_PER_ATTACK` (24), so 5 landed
#: non-harpoon hits from zero damage always land safely and a 6th breaches.
ROOM_BREACH_GATE_OTHER = 26
# Room damage is a **three-band ladder**, and 15 is the middle band, not death:
#
#     damage < 4        nothing                     ($558F CMP #$04 / BCC)
#     4 <= damage < 15  alarm 1, "WARNING: STRUCTURAL DAMAGE TO ..."
#     15 <= damage < 20 alarm 2, "severe"           ($565F-$5669)
#     damage == 20      HULL BREACH, a loss         ($5658 CMP #$14 / BNE)
#
# Treating 15 as the death gate is what used to end games by themselves in
# 600-5000 ticks, often before the Alien had shown itself.
#
# The ROM's breach test is an **equality** (`$5658 CMP #$14`) and the remake
# matches it — `sim/__init__.py` compares `d == HULL_BREACH_THRESHOLD`.
#
# **This note used to say the opposite** ("modelled as `>=` here ... overshooting
# 20 must not make a room immortal"), describing a decision DISC-204 reversed
# and the code no longer implements. Overshooting 20 *does* leave a room
# permanently safe, and that is the point: a harpoon's +15 can deliberately
# **burn out** a room, after which it is safe to keep fighting in. `>=` turned
# that tactical option into a death sentence and was what made the game
# unwinnable.
#
# The live consequence, since it surprises players: a harpoon fired into a room
# sitting at exactly 5 takes it to exactly 20 and destroys the ship on the spot.
# That is the ROM's behaviour, not a bug (DISC-257).
HULL_BREACH_THRESHOLD = 20
# **[C $5594 `CMP #$0F`]** — 15 is where the alarm escalates to stage 2, which
# is what D-073's "this IS a real ROM threshold" was really pointing at. It is
# now used for exactly that, rather than doubling as the breach gate.
DAMAGE_STAGE_SEVERE_FROM = 15
#: [C $558F `CMP #$04 / BCC RTS`] below 4, a damaged room raises nothing.
DAMAGE_STAGE_NOTHING_BELOW = 4

# **[C $55A9/$55AD] P2-18 — only THREE rooms can catch fire.** `damage_room_b`
# writes the FIGHT FIRE special (`$55B1 LDA #$06 / STA $5753,X`) only for room
# indices `$11`-`$13`, guarded by `CPX #$11 / BCC` and `CPX #$14 / BCS`. Those
# are OTHER LIST, OTHER LIST and **ENGINE 1** — the engine spaces. Elsewhere a
# damaged room raises its warning and that is all; there is nothing to fight.
FIRE_ROOM_INDICES: tuple[int, ...] = (0x11, 0x12, 0x13)
# **[C $5684] a fire BURNS.** `mainloop_sub_5684` runs `INC $64CE / BNE rts`, so
# it fires once every 256 main-loop passes, and then walks those same three
# rooms: any whose alarm byte `$651C,X` is set takes another point of damage
# (`$5690 INC $653F,X`) and re-enters `damage_room_b`. An unfought engine fire
# therefore eats its way toward the breach on its own.
FIRE_SPREAD_EVERY_TICKS = 256



def damage_stage(damage: int) -> int:
    """Map a room's raw damage to a 0/1/2 stage (`$651C`): intact/damaged/severe."""
    if damage <= 0:
        return 0
    if damage < DAMAGE_STAGE_NOTHING_BELOW:
        return 0   # [C $558F] below 4 the ROM does not even warn
    if damage < DAMAGE_STAGE_SEVERE_FROM:
        return 1
    return 2

# Composure stressors. **These are deltas to COMPOSURE, where high = calm and
# 0 = broken**, so bad events are NEGATIVE. Every confirmed site in the ROM
# moves the value by exactly 1 — there is no `ADC #$0n` for `$7D55` anywhere.
#
#   down (bad):   `$4230` wounded by the Alien; `$47DC`/`$5A0D` every crew
#                 member loses 1 when anyone dies; `$4625`/`$463C` scripted.
#   up (good):    `$4CF9` crowding — **safety in numbers**, not the manual's
#                 "nervous in a crowd"; `$4665`/`$466E` scripted.
#
# There is no adjacency stressor: proximity to the Alien in a *neighbouring*
# room does nothing. Scale is 0..10.
#
# Derivation: DISCOVERIES D-011, D-031, D-059.
COMPOSURE_HIT_ALIEN_ATTACK = -1   # [C $4230] the Alien wounds you
#: **[C $4227 `CMP #$03 / BNE`] The composure hit above fires only when the
#: wound leaves the victim on EXACTLY this health.** Not on every wound: the
#: ROM tests the new value and skips the `DEC $7D55,X` unless it is 3, so a
#: crew member loses composure once, crossing out of O.K., and never again.
#: Measured live over twelve wounds - three docked composure, and all three
#: landed on 3 (DISCOVERIES DISC-270).
COMPOSURE_HIT_HEALTH_EXACTLY = 3
COMPOSURE_HIT_CREW_DEATH = -1     # [C $47DC/$5A0D] applied to EVERY crew member
FEAR_BUMP_ALIEN_SAME_ROOM = 1   # (legacy name; unused since D-059)
# Crowding: `raise_crowd_fear ($4CE8)` walks up to 3 co-located crew and bumps
# each +1/tick while at least CROWD_THRESHOLD share a room ("some get nervous
# when they're all in a room at once", per the user's play + the decode).
# D-031: the real routine also skips anyone whose fear is currently exactly 0
# (`LDA $7D55,X / BEQ skip` before the `INC`) -- crowding only amplifies
# existing unease, applied in `sim.py`'s `_apply_fear_stressors`.
CROWD_THRESHOLD = 3
FEAR_BUMP_CROWDED = 1
# A crew member whose destination room already holds this many others **waits**
# rather than entering (full disassembly, DISCOVERIES D-018: the `$5156` move
# resolver's capacity check). Same number as the crowding threshold.
ROOM_CAPACITY = 3
# Finding a dead crew member in your room (`$59D5` "'S BODY IS HERE").
FEAR_BUMP_CORPSE = 1

# (The invented `ALIEN_ATTACK_HIT_CHANCE = 0.35` and the "armed crew are never
# auto-attacked" exemption were removed in FV-1.6, 2026-07-11 — that half holds:
# nothing on the encounter path looks at what anyone is carrying. **But FV-1.6's
# "deterministic" claim was wrong (D-177):** it was read off `$5354`, whose two
# callers both pass `$64C3` — the ANDROID's slot — so that routine is the
# android's. The Alien's own encounter is `$413C`, and it rolls twice
# and NO armedness check. A landed attack WOUNDS (DEC health), never instant-kills.
# The exact cadence/multiplicity is woven into the char-turn engine → FV-1.7 [?].)

# --- Crew health / WOUNDED state (full disassembly §8.9, D-011) ---------------
# Crew health is the game's `$7D45[1..7]`, counting DOWN as the Alien wounds a
# crew member (`alien_wound_crew $5354`: DEC `$7D45,X`). A crew member with
# health **below 2** is incapacitated — the actor gate `$52C0` requires
# `CMP #$02 / BCS` to act — i.e. effectively out of the game ("LOST"). Any lesser
# injury shows as "WOUNDED".
# NOTE the REAL starting health is PER-CREW `[C $7D4D]` (crew.START_HEALTH =
# 6/5/4/5/4/6/5, applied by default_crew in FV-1b3b). This scalar is only the
# fallback max for a bare/synthetic CrewMember built without a per-crew value.
CREW_START_HEALTH = 4          # default full health (fallback; real is per-crew)
CREW_INCAPACITATED_BELOW = 2   # health < 2 = incapacitated (the `$52C0` gate)

# [C $7D94] `health_band`, the structural sibling of `fear_band ($7DC5)`. It
# copies a 9-char record from the 10-byte-stride table at `$7CEB`
# (O.K. / WOUNDED / COLLAPSED / DEAD):
#
#     7D97  CMP #$03 / BCC   ; health 0-2 -> index = 3 - health
#     7D9B  CMP #$04 / BCC   ; health 3   -> index 1 (WOUNDED)
#     7D9F  LDA #$00         ; health >=4 -> index 0 (O.K.)
#
# **The O.K./WOUNDED boundary is an absolute 4**, not a fraction of the crew
# member's own maximum. Start health is per-crew (6/5/4/5/4/6/5, `$7D4D`), so
# comparing against `full_health` makes Dallas read WOUNDED at 5 where the real
# game still says O.K. Health 2 and 3 both map to WOUNDED.
HEALTH_OK_AT_LEAST = 4         # `$7D9B CMP #$04` -> index 0 ("O.K.")
HEALTH_WOUNDED_AT_LEAST = 2    # health 2-3 -> index 1 ("WOUNDED")
# **[C $413C] The Alien's encounter is doubly random and wounds exactly ONE.**
# `alien_tick` reaches it via `$8AE1 JMP $413C` once the `$64A3` flag is set:
#
#     4152  JSR rng / CMP #$07 / BCC rts    ; roll 0-6 -> no attack at all
#     415A  LDA $6501 / BEQ $4185           ; ducted Alien takes the FIRST
#                                           ;   ducted crew in slot order
#     4185  ...collect co-located, surfaced, health >= 2 crew into $64A4,X...
#     41A7  CPX #$01 / BNE                  ; one candidate  -> that one
#     41B8  JSR rng / LSR / BCC             ; two            -> 50/50
#     41C4  JSR rng / CMP #$05 / CMP #$0A   ; three+         -> 0-4 / 5-9 / 10-15
#     41F4  LDX $64A4 / DEC $7D45,X         ; wound exactly ONE
#
# So **a crowded room is safer per head**, not more dangerous: one wound is
# shared out. Wounding every co-located crew member on every action -- the
# obvious reading -- makes crowds a death sentence.
#
# Note `alien_wound_crew ($5354)` is a misnomer and is *not* this routine: both
# its callers pass `$64C3`, the android's slot. It is the android's attack.
#
#: **[C $413C `LDA #$28`]** After meeting crew the Alien **holds the room for 40
#: passes (~5 s)**. The `JMP` above means the pass never reaches `$8AE4` and
#: never dispatches a move. Set before the attack roll, so the hold happens on a
#: miss too -- which is what makes it read as a stalking creature rather than a
#: passing hazard.
#
# Derivation: DISCOVERIES D-177, D-188.
ALIEN_ENCOUNTER_HOLD_TICKS = 0x28

ALIEN_ATTACK_ROLL_AT_LEAST = 7      # $4155 CMP #$07 / BCS
#: `$64A4`-`$64A6` is three bytes wide, so at most three candidates are ever
#: collected - which is exactly `ROOM_CAPACITY`.
ALIEN_VICTIM_SLOTS = 3
#: `$41C7`/`$41CB`'s comparison chain over a flat 0-15 roll.
ALIEN_VICTIM_BANDS: tuple[int, ...] = (5, 10)

ALIEN_WOUND_AMOUNT = 1         # one wound per landed Alien attack (DEC `$7D45,X`)

# (Combat is cumulative and deterministic — see `ALIEN_DAMAGE_TO_KILL` /
# `ITEM_ATTACK_DAMAGE` above, DISASSEMBLY §8.8.)

# --- Item charges [C $4B47] ---------------------------------------------------
# `$4B47` is the master charge table, `$4B37` the working copy; `new_game
# ($65B1)` copies 20 entries in the same loop that resets the item-room table,
# so it is indexed by **item instance id (0-19)**, matching
# `gamedata_snapshot.ITEMS`:
#
#   0-2  ELCTRC PRD 0     8-11  FIRE EXTNG 3
#   3-5  INCINERATR 0     12    HARPN GUN  1
#   6-7  TRACKER    0     13-15 LASER PIST 10
#
# Every instance of a type shares one value, so a per-type map is equivalent.
# Only the extinguisher, laser and `$5899` are charge-checked
# (`LDA $4B37,X / BNE / DEC`); a spent item prints its message and the action is
# cancelled. **Charge 0 does not mean "spent"** -- those code paths never touch
# `$4B37` at all, so such items are simply not charge-based and must not be
# given a `uses_left`.
CONSUMABLE_USES: dict[str, int] = {
    "fire_extng": 3,    # $4B47[8..11]
    "harpn_gun": 1,     # $4B47[12]  — one shot
    "laser_pist": 10,   # $4B47[13..15]
}
# The TRACKER is destroy-on-use rather than charge-based: attacking with
# instance 6/7 falls to `$49B5`, which prints "TRACKER IS SMASHED" and calls
# `clear_object_at_loc2`. It still lands a wound on the way through (`$49B5`
# falls into the same `$497A INC $7D45` every other +1 item uses), so it has
# both an entry in `ITEM_ATTACK_DAMAGE` and one in `ITEM_DESTROYED_ON_ATTACK`.
#
# **Fire and structural damage are one accumulator** (`$653F`). The FIGHT FIRE
# handler (`$5889`) never touches it -- it only resets the one-way per-room
# alarm latch `$651C`. So structural damage is **permanent**: nothing in the
# game repairs it, and the extinguisher is recurring alarm-silencing, not a
# repair. `damage_room_b ($5587)` re-raises the alarm once raw damage reaches
# the threshold below (`$558C CMP #$04 / BCS`), and only while the latch reads 0.
#
# Derivation: DISCOVERIES D-033, D-035, D-044.
ROOM_ALARM_DAMAGE_THRESHOLD = 4   # [C $558C] `CMP #$04 / BCS` -> raise `$651C`
#: **[C $5594/$5658] D-164 — `$651C,X` has THREE states, not two.**
#: `damage_room_b` splits on the room's raw damage::
#:
#:     5594  CMP #$0F / BCC $559E     ; 4..14  -> stage 1 (the ordinary alarm)
#:     5598  STX $5580 / JMP $5658    ; >= 15  -> the CRITICAL path
#:     5658  CMP #$14 / BEQ hull_breach   ; exactly 20 -> the ship vents
#:     565F  LDA $651C,X / CMP #$02 / BEQ rts
#:     5667  LDA #$02 / STA $651C,X   ; latch stage 2 and draw the LONG warning
#:
#: The consequence that matters for play: **`$55B1`, which arms FIGHT FIRE by
#: writing 6 into `$5753,X`, is only reachable on the 4..14 path.** Once an
#: engine room's damage passes 15 the option is never re-armed, so a fire you
#: have already fought once in a badly damaged room cannot be fought again.
ROOM_ALARM_CRITICAL_THRESHOLD = 15   # [C $5594] `CMP #$0F`
ROOM_ALARM_STAGE_CRITICAL = 2        # [C $5667] `LDA #$02 / STA $651C,X`

# --- Systems malfunctions — DECODED [C, D-072/D-073 2026-08-01] --------------
# `damage_room_b ($5587)` is where a room's alarm latches, and the malfunction
# message is displayed as **part of that same event** — that was the missing
# trigger. The dispatcher at `$55C1` then resolves the text through three
# parallel tables: length `$5473,Y`, offset `$547C,Y`, and the blob at `$54C6`.
MALFUNCTION_MESSAGES: dict[int, str] = {
    1: "PARTIAL SYSTEMS CONTROL LOSS",
    2: "COMPUTER MALFUNCTION",
    3: "CRYOGENICS MALFUNCTION",
    4: "FIRE IN ",                      # + the room name ($55F2 special case)
    5: "ENVIRONMENTAL IRREGULARITIES",
    6: "NARCISSUS STATUS RED",
    7: "OVERRIDE OPTION EXPIRY    MINS",
    8: "SHIP WILL DESTRUCT IN   MINS  ",
}
# [C $54A3] The per-room malfunction type — a **static** 34-byte table, never
# written anywhere in the program. Keyed by room INDEX (into `ROOM_SLUGS`).
# The semantics line up 3-for-3 (comms centre loses systems control, the
# computer room reports a computer fault, the cryo vault reports cryogenics),
# which independently cross-validates the ROOM_SLUGS ordering.
# **Re-dumped from `$54A3` 2026-08-07 (D-164).** Two errors were corrected:
# room **34 (NARCISSUS) was missing** — it really does carry type 6 — and three
# of the trailing comments named the wrong rooms (17/18/19 are ENGINE 1/2/3,
# not "other list"; 25 is LIFE SUPPORT, not the laboratory, which is 23).
ROOM_MALFUNCTION_TYPE: dict[int, int] = {
    6: 1,    # commdcentr  -> PARTIAL SYSTEMS CONTROL LOSS
    7: 2,    # computer    -> COMPUTER MALFUNCTION
    15: 3,   # cryo_vault  -> CRYOGENICS MALFUNCTION
    17: 4,   # engine_1    -> FIRE IN ...
    18: 4,   # engine_2    -> FIRE IN ...
    19: 4,   # engine_3    -> FIRE IN ...
    25: 5,   # life_suppt  -> ENVIRONMENTAL IRREGULARITIES
    34: 6,   # narcissus   -> NARCISSUS STATUS RED
}
# Types 7-8 belong to no room: they are the auto-destruct's two "MINS"
# countdown strings (D-060, already modelled).
#: **[C $5A26 `mainloop_sub_5a26`] DISC-230 — the auto-destruct's own banner.**
#: Every time the sub-tick counter `$657C` wraps (reload `#$FF`), one "minute"
#: of `$657B` elapses and the routine posts one of the two countdown strings
#: through `draw_damage_warning ($55C9)`, patching a single digit into it::
#:
#:     5A3E  LDA $657B / BNE $5A46 / JMP hull_breach   ; 0 -> the ship blows
#:     5A46  CMP #$06 / BCC $5A58
#:     5A4A  ADC #$AB / STA $555C / LDA #$07           ; >= 6 -> type 7
#:     5A58  ADC #$B0 / STA $5578 / LDA #$08           ; <  6 -> type 8
#:
#: `$AB` is `$B0 - 5`, so type 7 shows **minutes - 5** — the OVERRIDE window,
#: which expires at 5 (`AUTO_DESTRUCT_OVERRIDE_ABOVE`) — while type 8 shows the
#: raw minutes with the ordinary `#$B0` digit conversion. The digit lands at
#: `$555C`/`$5578`, i.e. these indices into each 30-char message, both of which
#: are blanks in the stored text.
#: **[C $5B80 / $5C33 / $5950] DISC-231 — the transient row-24 banners.**
#: Each is written to `$07C0` (row 24 col 0), held by a blocking `delay_long`
#: ($561C), then blanked by `clear_line_07c0 ($5BE7)`. Decoded from the ROM's
#: own bytes; all three were previously never displayed at all.
NOTICE_MOTHER_REFUSES = "MOTHER refuses launch"   # $5B80, 21
NOTICE_GO_GET_JONES = "Go get Jones"              # $5C33, 12
NOTICE_FIRE_OUT = "Fire Out"                      # $5950, 10 (2 trailing pads)
#: **[C $4940/$4BE0, full disassembly §8.8] resolve_attack's own banner.**
#: Printed for every attack that reaches the Alien, before the per-item
#: dispatch — the ROM shows this whether the item wounds, entangles (the net)
#: or does nothing at all. No feedback for this event existed anywhere in the
#: remake before now; ``add_room_damage``/``resolve_attack`` were both silent.
NOTICE_HITS_ALIEN = "{name} hits Alien"                       # $4BE0
#: **[C $41C4 alien_attacks_crew] "ALIEN WOUNDS <crew>".** Printed when the
#: Alien's own attack lands, alongside the existing `ATTACK_ALERT` sound cue -
#: which was the only feedback this event had before now.
NOTICE_ALIEN_WOUNDS = "Alien wounds {name}"                   # $41C4
#: **[C $4B22/$4B1E, D-033] The tracker and the net are both DESTROYED by an
#: attack (`ITEM_DESTROYED_ON_ATTACK`), and the ROM says so on the same row-24
#: banner.** Wording keeps the ROM's noun, not its exact capitalisation - the
#: three existing banners above already do this (`NOTICE_FIRE_OUT` reads
#: "Fire Out", not the ROM's own all-caps screen text).
NOTICE_TRACKER_SMASHED = "{name}'s tracker is smashed"        # $4B22, 21 ch
NOTICE_NET_USED = "{name}'s net entangles Alien"              # $4B1E
#: **[C $4B57/$4B94] A charge-based item used up.** Only reachable via USE
#: today (`_resolve_use_order`'s exhaustion gate) - the literal ATTACK order
#: does not yet check charges at all, a separate, already-filed gap
#: (`resolve_attack`'s own docstring, alien.py) this does not touch.
NOTICE_EXTINGUISHER_EMPTY = "{name}'s extinguisher is empty"  # $4B57, 24 ch
NOTICE_LASER_EXHAUSTED = "{name}'s laser is exhausted"        # $4B94, 21 ch

#: **Not the original — added at the owner's request (2026-09-05) to give
#: `turns` mode an actual initiative order instead of "whoever gives an
#: order next goes next."** Rolled once per game, not re-rolled each round:
#: a shuffled list of every crew member plus the Alien and Jones, so the
#: sequence a player fights in is fixed for the whole game the way a
#: tabletop initiative roll would be. There is no ROM citation for this -
#: the disk has no turn-based mode at all - so it lives entirely behind the
#: `turns` option and changes nothing about real-time play.
#:
#: Two action points is "roughly one room move and one action" per the
#: owner's own wording: a move costs one, and ATTACK/USE/GET/LEAVE each cost
#: one, so a turn is spent on any combination of two of those before it
#: passes to the next name in the order. The Alien's and Jones's own slots
#: need no budget - they act through their existing autonomous AI for one
#: bounded window and pass immediately.
TURN_ACTIONS_PER_TURN = 2
#: **DEC-045, UPDATED only.** DEC-044's gate-aware retreat makes turn-based
#: UPDATED harder than real-time UPDATED at the ROM-adjacent default of 2 -
#: a forced retreat used to spend a whole action point landing zero
#: progress toward the kill. Two changes together, not either alone:
#: `app.py`'s turn loop (and this tool's own turn-based sweep) now exempts
#: a MOVE_TO from the action-point cost when it was issued from a room
#: `weapon_would_breach` says is too hot to fight in right now, and this
#: constant was re-swept from that fixed baseline rather than the un-fixed
#: one - which needed AP~17 to reach the same target band, a number that
#: stops reading as "a few actions a turn" at all. With the fix,
#: `tools/winnability_sweep.py --turns --ap 2,3,4,5` lands ap=5 at 5/16
#: (31.25%), the lowest value inside the owner's own ~30-60% band; see
#: `flow.py::GameFlow._turn_actions_per_turn`.
UPDATED_TURN_ACTIONS_PER_TURN = 5
#: How many ticks the Alien's or Jones's own initiative slot runs before
#: passing on - long enough for one of their own actions (`ALIEN_MOVE_TICKS`
#: is 60), short enough not to let one slot eat the whole game.
TURN_CREATURE_SLOT_TICKS = 60
#: The two creature participants in the initiative order, alongside however
#: many crew are in `GameState.crew`. Plain strings, not ids into any table -
#: nothing in `GameState` needs a "creature roster," so the turn-order list
#: is the only place these two tokens exist.
TURN_ALIEN_ACTOR = "alien"
TURN_JONES_ACTOR = "jones"
#: **Screen animations (2026-09-04, expanded 2026-09-05, scoped to BOOT only
#: 2026-09-05), not the original at all.** The `screen_fx` option's effect on
#: the boot report screen — **only** that screen (the owner's own words:
#: "the intro animation should just be for the initial screen of dos text");
#: it no longer touches the title or ending screens, which draw exactly as
#: they did before this option existed. Built as an original set inspired by
#: the general shape of an old terminal readout (per the owner's own
#: description of the technique) rather than a reproduction of any specific
#: footage: a CRT power-on stretch and degauss shake as the screen appears,
#: text typed out a character at a time in phosphor yellow behind a blinking
#: cursor and a trailing streak, static that fades as letters and blocks,
#: and a command-style prompt once revealed.
#:
#: 16 characters/tick reveals a 40-column row in 2.5 ticks - visibly typed
#: rather than an instant per-tick row-pop, while still clearing a worst-case
#: ~22-row boot report in ~55 ticks, safely inside `BOOT_TICKS` (75) with
#: room to spare for the player to actually read it before the timeout.
SCREEN_FX_CHARS_PER_TICK = 16
#: How many ticks the static/glitch flourish runs after a screen is entered,
#: fading out as it goes (`render/screen_fx.apply_terminal_fx`). ~1.5 s at
#: `TICK_HZ` - long enough to read as a deliberate flourish, short enough not
#: to still be running by the time there is anything to read underneath it.
SCREEN_FX_GLITCH_TICKS = 12
#: Ticks per half-cycle of the typing cursor's blink. ~0.5 s at `TICK_HZ` -
#: the conventional terminal-cursor rate, not derived from anything ROM-side.
SCREEN_FX_CURSOR_BLINK_TICKS = 4
#: **The CRT power-on stretch (2026-09-05), not the original.** How many
#: ticks the picture takes to grow from a thin horizontal band to full
#: height when the boot report first appears - the classic "tube warming up"
#: shape, in reverse of how one switches off. ~0.6 s at `TICK_HZ`: quick
#: enough to read as a flourish on a screen with a 75-tick timeout, not a wait.
SCREEN_FX_STRETCH_TICKS = 5
#: **The degauss shake (2026-09-05), not the original.** How many ticks the
#: decaying horizontal wobble that rides along with the power-on stretch
#: runs before it settles - "settles quickly," the owner's own phrasing,
#: and the same shape (in miniature) as the CRT layer's own deck-change
#: transient (`render/crt.py`'s `_degauss`), built standalone here since
#: this must run whether or not the separate `crt` option is on.
SCREEN_FX_SHAKE_TICKS = 8
#: **`game_audio=enhanced` loudness target (2026-09-05), not the original at all —**
#: the C64's SID has no concept of LUFS. `audio.loudness.integrated_lufs`
#: (a from-scratch BS.1770-style meter, see that module's own caveats) was
#: run over the six default SID-emulated effects (`audio.sfx.EFFECTS`) to
#: answer "what does this game's own mix actually sound like": heartbeat
#: -28.3, grille -27.2, movement -17.2, tracker_alarm -24.8, airlock -19.6,
#: attack_alert -10.4 LUFS. That is an 18 LU spread by *design* - an alarm is
#: supposed to be louder than an ambient blip - so there is no single "right"
#: number a dropped-in recording should hit exactly. -22.0 sits at the
#: measured mean (-21.2) and median (-22.2); ±12 LU encloses the full
#: measured range (-28.3 to -10.4, an 11.6 LU reach on the loud side) with a
#: little margin either way, so the check flags a
#: clip only once it is louder or quieter than anything the game's own
#: effects already do, not merely "different from the average."
SOUND_TARGET_LUFS = -22.0
SOUND_LUFS_TOLERANCE = 12.0
#: **[C $561C `delay_long` = `LDA #$00 / LDX #$00` then `delay`]** the pause is
#: 256 outer x 256 inner iterations of a ~10-cycle body. The remake cannot
#: block its own loop, so the banner is shown for this many ticks instead and
#: the border held black for the same span (`$5626-$5628 LDA #$00 / STA $D020`,
#: restored to `#$06` by every caller afterwards).
NOTICE_TICKS = 12
#: `$5626` — `delay` blacks the border for its whole duration.
NOTICE_BORDER = 0

MALFUNCTION_OVERRIDE_TYPE = 7
MALFUNCTION_DESTRUCT_TYPE = 8
MALFUNCTION_OVERRIDE_DIGIT_COL = 24   # $555C - ($54C6 + $7E)
MALFUNCTION_DESTRUCT_DIGIT_COL = 22   # $5578 - ($54C6 + $9C)
#: `$5A46 CMP #$06` — at or above this many minutes the banner is the override
#: warning; below it, the destruct countdown.
AUTO_DESTRUCT_OVERRIDE_BANNER_AT = 6


def auto_destruct_banner(minutes_left: int) -> str | None:
    """The countdown line for `minutes_left`, or ``None`` when not armed.

    **[C $5A3E-$5A63]** Reproduces the ROM's own two-arm choice and its digit
    patch, using the decoded message text rather than re-typing it.
    """
    if minutes_left <= 0:
        return None                                   # $5A43 -> hull_breach
    if minutes_left >= AUTO_DESTRUCT_OVERRIDE_BANNER_AT:
        text = MALFUNCTION_MESSAGES[MALFUNCTION_OVERRIDE_TYPE]
        col = MALFUNCTION_OVERRIDE_DIGIT_COL
        digit = minutes_left - AUTO_DESTRUCT_OVERRIDE_ABOVE   # $AB = $B0 - 5
    else:
        text = MALFUNCTION_MESSAGES[MALFUNCTION_DESTRUCT_TYPE]
        col = MALFUNCTION_DESTRUCT_DIGIT_COL
        digit = minutes_left                                  # $B0
    if not 0 <= digit <= 9:
        return None
    return text[:col] + str(digit) + text[col + 1:]


MALFUNCTION_FIRE_TYPE = 4
# [C $55B1] `LDA #$06 / STA $5753,X`, set only for rooms 17-19 (the `$55A9
# CPX #$11` / `$55AD CPX #$14` bounds) — exactly `$54A3`'s type-4 rooms, an
# independent confirmation of that table. FIGHT FIRE clears it ($58CF, D-066),
# which is what identifies `$5753,X` as carrying the FIGHT FIRE option code.
# **D-163:** `$5753` is the per-room **SPECIAL-OPTION code table**, not a
# fire flag - 1=SCUTTLE/OVERRIDE, 2=BLOWLOCK, 3=HYPERSLEEP, 5=LAUNCH, and
# 6 (written here by `damage_room_b`) = FIGHT FIRE. Clearing it on a
# successful extinguish is exactly "stop offering the option here".
ROOM_FIRE_FLAG = 6
# `resolve_attack ($4940)` is the single dispatcher for both USE and ATTACK on
# the net, electric prod and spanner -- see `sim.orders._resolve_use_order`. The
# net **entangles** rather than wounds (`ALIEN_NET_ENTANGLE_TICKS`). Thermlance
# has no spawned instance anywhere in the game, so its USE effect is moot.
#
# **The tracker reports neither a room nor an entity.** The game's own sound
# legend says only "the TRACKER alarm." / "SOMETHING moving between locations."
# (`$451C`/`$453C`), which is why `state.tracker_alarm` is a bare bool. Its
# range is six rooms: `resolve_char_display_loc ($8DB6)` builds `$6565..$656A`
# from the holder's room plus that room's entry in each of the five route
# tables (`alien.tracker_zone`). Granularity is "something is moving in your
# zone", nothing finer.
#
# Derivation: DISCOVERIES D-041, D-150, D-169.

# --- Jones the cat -------------------------------------------------------------
# Jones runs on the same timer engine as everyone else, not a per-tick
# coin-flip. `sub_88ab_prechar ($88AB)` counts `$657F` down once per main-loop
# pass and reloads it with 40 (`$88B6`) -- see `JONES_MOVE_TICKS`. His
# destination comes from `$8971`: the **Alien's own route tables** through
# Jones's band mapping (`alien.jones_dest`), not a uniform neighbour choice.
#
# The constant below is kept only because `gamedata_snapshot` still carries the
# decoded byte; nothing reads it for Jones's movement.
#
# Derivation: DISCOVERIES D-153, D-156.
JONES_WALK_TICKS = 5

# --- The heartbeat -------------------------------------------------------------
# [C $4E16] `fear_alert` sets the heartbeat's IRQ divider `$4D02` from the crew
# member's composure `$6571,Y`:
#
#     composure >= 4 -> 40   CONFIDENT, slowest
#     composure == 3 -> 30   STABLE
#     composure == 2 -> 23   UNEASY
#     composure <= 1 -> 15   SHAKEN/BROKEN, fastest
#
# The IRQ (`$4D37`) counts `$64B7` down from that divider and gates SID voice 1
# off/on at each wrap -- one beat. The heartbeat **races as composure falls**,
# which is the game's main tension cue ("This is the sound of the heartbeat of
# the current character.", `$44BC`).
HEARTBEAT_DIVIDER_BY_COMPOSURE: dict[int, int] = {4: 40, 3: 30, 2: 23, 1: 15, 0: 15}


def heartbeat_divider(composure: int) -> int:
    """IRQ ticks between heartbeats for a given composure ([C $4E16])."""
    return HEARTBEAT_DIVIDER_BY_COMPOSURE.get(min(composure, 4), 40)


# --- Special Options: auto-destruct (GAME_SPEC §6.2 #3, §8) ------------------
# [C $58E8/$5A34-$5A66/$585E] Arming (`set_result_win $58E3`) loads a 9-unit
# countdown into `$657B` and a 255-pass sub-counter into `$657C`. `$5A34`
# decrements the sub-counter each pass; on wrap it reloads 255, redraws the
# warning and decrements `$657B`:
#
#   $657B >= 6 -> "OVERRIDE OPTION EXPIRY n MINS"
#   $657B <  6 -> "SHIP WILL DESTRUCT IN n MINS"
#   $657B == 0 -> `JMP hull_breach` -- the ship is destroyed
#
# OVERRIDE (`$585E CMP #$05 / BCC`) only cancels while `$657B >= 5`, so you get
# 5 of the 9 units to change your mind; after that the detonation is
# irreversible and you watch the countdown run out.
AUTO_DESTRUCT_MINUTES = 9          # [C $58E8] `$657B` initial value
AUTO_DESTRUCT_SUBTICKS = 255       # [C $58ED/$5A3B] `$657C` reload
AUTO_DESTRUCT_OVERRIDE_ABOVE = 5   # [C $585E] override only while `$657B` >= 5
# Total ticks from arming to destruction.
# **[C $5A3E-$5A66] D-162 — there are TEN sub-counter wraps, not nine.**
# `$657B` is not a count of wraps remaining; it is *read before* being
# decremented, and the detonation is the wrap that finds it **already 0**::
#
#     5A34  DEC $657C / BNE rts       ; 255 passes per wrap
#     5A39  LDA #$FF / STA $657C      ; reload
#     5A3E  LDA $657B / BNE $5A46
#     5A43  JMP hull_breach           ; <- fires when $657B is ALREADY zero
#     5A66  DEC $657B                 ; ...otherwise warn, then decrement
#
# So arming spends 9 wraps walking `$657B` 9 -> 0 and a **tenth** wrap to
# detonate: 10 x 255 = 2550 passes, ~5 min 23 s at MAIN_LOOP_HZ. The old
# `9 * 255` blew the ship ~32 s early.
AUTO_DESTRUCT_TICKS = (AUTO_DESTRUCT_MINUTES + 1) * AUTO_DESTRUCT_SUBTICKS

# --- Intro / front-end timing (R-30 / R-13; live-confirmed timed, not gated) --
# The title auto-advances and the opening death notice clears on a timeout —
# neither has a press-to-continue (D-014). The exact durations are calibration
# [?] (measure against the running game, docs/re/VICE_CHECKS.md); these are
# reasonable defaults at TICK_HZ (~6.7): title ~6 s, opening notice ~4 s.
#
# LIVE-CAPTURED boot order (D-021, tools/vice-mcp/capture_boot.py): the disk
# boots into a "LOADING MENU" interstitial, the ShareData back-up NOTICE
# (press-any-key), the "WELCOME TO ALIEN" front-end menu (1 ALIEN / Q QUIT), the
# "DO YOU WANT INSTRUCTIONS? (Y OR N)" prompt, a "LOADING…. / PLUG JOYSTICK INTO
# PORT TWO" interstitial, and only THEN the animated title. The two loading
# interstitials are timed cards (no input); their durations are [?] calibration.
# **PV-26 closed 2026-08-07 (D-172) - COMPUTED, not guessed, and both were
# ~5x too fast.** `delay ($561E)` is a countable loop: body 6+6+2+4+6+6+6+6+2 =
# 44 cycles + a 3-cycle branch = 47 per inner iteration, 256 inner x 256 outer,
# so `delay_long (LDX #$00)` is **3,081,727 cycles = 3.128 s PAL**.
#
# The title routine ($5E81) writes "JOSEPH CONRAD" and then calls `delay_long`
# **eight times**, one before each of A-L-I-E-N ($5E8E/$5E96/$5E9E/$5EA6/$5EAE)
# and three more after ($5EB6/$5EB9/$5EBC) before it RTSes. So the whole card
# is 8 x 3.128 = **25.0 s** and the gap between letters is one `delay_long`.
# At TICK_HZ that is 197 and 25 ticks; the old 40 and 6 made the title flash
# past in 5 seconds. (The letters land at $0431/$0436/$043B/$0440/$0445 - row 1,
# columns 9/14/19/24/29 - which is the spaced "A L I E N" of R-36.)
TITLE_TICKS = 197
#: **[C $50B8/$50BB] DISC-238 — corrected from 27 by D-172's own method.**
#: `sub_5049`, the opening-death notice, ends with **two** `JSR delay_long`
#: back to back before it RTSes. At D-172's computed 3.128 s each that is
#: 6.256 s = 49 ticks. D-172 applied this arithmetic to the title card and the
#: letter gap but never re-checked the opening, which kept an older guess of 27
#: (3.4 s) — barely over one delay_long, so the notice cleared about twice as
#: fast as the original's.
OPENING_TICKS = 49
# **[C-live] D-142 — MEASURED against the real disk image, 2026-08-06**
# (`tools/vice-mcp/measure_greenvalley.py`, WarpMode off per the standing
# constraint). Two earlier passes (D-140/D-141) guessed this from this
# remake's own animation constants alone (2.2-2.8 s) — both far too short.
# BASIC's POKE-loop drawing speed is genuinely slow on real hardware: the
# spiral took **~11.0 s** to sweep its 22 rings once, and the whole GREEN
# VALLEY screen (spiral + "GREEN VALLEY"/"PUBLISHING" text +
# `320 FORXX=1TO900:NEXTXX`) ran **~14.1 s** before the WELCOME menu
# appeared — timestamped by watching screen RAM transition away from the
# spiral's own text back to a cleared screen (`600 PRINTCHR$(147)`, the next
# thing MENU1.prg does once this routine returns). 14.1 s * `TICK_HZ`
# (~7.886) ~= 111 ticks.
LOADING_MENU_TICKS = 111    # "LOADING MENU" interstitial (~14.1 s) [C-live]
#: **[?] — and not a ROM constant at all (DISC-238).** Unlike every other card
#: here, this one is not paced by a `delay_long`: it is shown while the loader
#: reads the next file off the disk, so its duration is drive I/O, not a
#: countable loop. There is no value in the image to decode; it would have to
#: be measured on a real 1541 and would vary with the drive. Left as a
#: plausible ~3 s.
LOADING_PLAY_TICKS = 20
# The title's "ALIEN" is spelled out one letter at a time with a delay between
# each (`$5E90`-`$5EB7`: five reverse-video chars A-L-I-E-N, `delay_long $561C`
# between). Ticks between each letter appearing (5 letters shown by tick 30);
# one `delay_long` apart - see the TITLE_TICKS block above (D-172).
TITLE_LETTER_TICKS = 25
#: When the fifth letter has landed and the card is just holding — the point a
#: skip fast-forwards *to*, not past. Derived from the letter gap rather than
#: written as 100, so the two cannot drift: the first letter is on screen at
#: tick 0, so the fifth arrives four gaps later.
#:
#: **Not the original**, in the sense that the ROM has no skip; but the *value*
#: is, and what remains after it is the three trailing `delay_long`s at $5EB6/
#: $5EB9/$5EBC — about 12 s of the card holding with the word complete.
TITLE_REVEALED_TICKS = 4 * TITLE_LETTER_TICKS

#: **[C EXITO.prg line 1100 `FOR XX=1TO3000`] D-175** - how long the Q/EXIT
#: advert holds before `SYS 64738` resets the machine. An empty BASIC FOR loop
#: runs at roughly 900-1000 iterations/second on a stock C64, so 3000 is about
#: **3.2 s**. Expressed in remake ticks at TICK_HZ.
EXIT_ADVERT_TICKS = 25

#: **[C $4389-$43D0] D-176** - the DECK PLAN KEY / SOUND LEGEND screen is paced
#: by **eight** `delay_long`s before `prompt_and_wait`, and `delay_long` is
#: 3.128 s PAL (D-172). 8 x 3.128 = 25.0 s, expressed in remake ticks. It ends
#: on PRESS ANY KEY, so this is the *unattended* duration, not a hard limit.
INTRO_LEGEND_TICKS = 197

# --- Game modes & the opening (GAME_SPEC §9, §11 #6) --------------------------
# (`SHORT_START_OXYGEN` was removed with the rest of the oxygen system —
# FV-2.5 / D-062, see the block above.
#
# **The note that used to sit here — "this leaves `GameMode` with no mechanical
# effect at all" — was WRONG and is retracted (D-085).** It was written the
# moment the oxygen budget went, when the two modes did look identical; but the
# ROM has its own SHORT setup at **`$604F`**, reached from the Ctrl+2 branch,
# which pins the victim to KANE and the android to ASH and copies four 7-entry
# tables of crew locations/health/composure. SHORT is a **fixed scenario**, not
# a shorter FULL. See `Simulation._apply_short_scenario` and the decoded
# `gamedata_snapshot.SHORT_SCENARIO`.)

# Which crew member is already dead at scenario start in the FIXED death
# variant. The remake had guessed Kane (film canon); the only real-game
# capture so far shows LAMBERT removed at the opening ($7935 slot 5
# = $FE across all four RAM dumps from that same run). One observation
# can't prove the original's choice is fixed rather than random, so this
# stays [?]-flagged, but it now follows the observed data over the guess.
FIXED_OPENING_DEATH_ID = "lambert"

# --- The opening victim and THE ANDROID — decoded [C, D-080 2026-08-01] ------
# `$5049`'s opening routine rolls the RNG into two 16-entry candidate tables and
# stores two **distinct** crew indices:
#
#   $506E  LDA $50EC,Y / STA $64C2   -> the crew member who dies at the opening
#   $507E  LDA $50FC,Y / CMP $64C2 / BEQ re-roll / STA $64C3   -> **the android**
#
# `$50AB` then kills `$64C2` (`$7D45,Y = 0`, `$7935,Y = $FE`), which is the
# "<NAME> HAS BEEN KILLED BY THE ALIEN" notice.
#
# **The victim pool is NOT the whole crew.** `$50EC` contains only 1/2/5 —
# DALLAS, KANE, LAMBERT. The remake drew uniformly from all seven, so it could
# open by killing Ripley, Ash, Parker or Brett, which the original never does.
OPENING_VICTIM_CANDIDATES = ("dallas", "kane", "lambert")     # [C $50EC]

# **The android** (`$64C3`) — the mechanic the instructions describe as "your
# not knowing which member of the crew is an android", and which the remake did
# not model at all. Drawn from `$50FC` = 1/2/4/6 and always re-rolled until it
# differs from the victim. The game never prints the word "ANDROID" anywhere,
# which is why a string search finds nothing: you are meant to deduce it.
#
# `$6062`-`$6069` sets a hard-coded preset of `$64C2 = 2` (KANE) and
# `$64C3 = 4` (**ASH**) — the film's own pairing, which is what identifies
# `$64C3` beyond doubt.
ANDROID_CANDIDATES = ("dallas", "kane", "ash", "parker")      # [C $50FC]

# What the android actually does, from its 13 `$64C3` sites:
#  * **Attacks crew sharing its room** (`$5439`): if the acting crew member is
#    in the android's room with composure >= 2 AND health >= 2, `$546D` calls
#    `alien_wound_crew` with the android as attacker. A second path (`$5345`)
#    does the same after a scan loop, printing " HITS " (`$533F`).
#  * **Cannot ENTER HYPERSLEEP** — `guard_target_is_player ($5939)` returns
#    immediately when the commanded character is `$64C3` (`$593C`).
#  * **Is exempt from the endgame mass kill** (`$6130 CPY $64C3 / BEQ skip`),
#    so it can be the last one standing.
#  * **Does not count as a survivor for the COMPETENCE RATING** (`$61A5`).
ANDROID_ATTACK_MIN_COMPOSURE = 2   # $5459 CMP #$02 / BCC -> no attack
ANDROID_ATTACK_MIN_HEALTH = 2      # $5460 CMP #$02 / BCC -> no attack

# **The android silently DROPS your orders while it is with the Alien**
# ([C $5265], the branch `resolve_char_move` diverts it to at `$5168`). This is
# the behaviour a player notices first — the crew member simply stops responding
# — and it is what prompted the whole D-080 hunt:
#
#   5272  LDA $6501,Y / CMP $6501    ; same duct state as the ALIEN (slot 0)?
#   527A  LDA $7935,Y / CMP $7935    ; ...and the same room?
#   5282  LDA $650C,Y / BEQ normal   ; is there a pending action at all?
#   528A  LDA $7D45,Y / CMP #$04
#   528F  BCC char_wander            ; health < 4 -> it panics instead
#   5294  LDA #$00 / STA $650C,Y     ; ** clear the pending action **
#   5299  JMP check_deferred_move    ; ** and skip it: the order is DISCARDED **
#
# No message, no refusal — the order just evaporates. In the film Ash protects
# the creature, and this is that, mechanically.
ANDROID_OBEY_MIN_HEALTH = 4        # $528A CMP #$04; below it, panic instead

# **How the android gets found out** ([C $52A4-$52DA]). Once the Alien has taken
# `>= 6` damage (`$52A4 LDA $7D45 / CMP #$06`) — i.e. the crew have been
# fighting it — the game scans for a crew member who is in the android's room,
# not in a duct, health >= 2 and composure != 0. If one is there it stores the
# android's own slot into `$64CC` (`$52D7`) **and writes it to `$D021`**
# (`$52DA`), flashing the screen background: the tell. From then on `$526A`
# sends the android down its activated path (`$52F1`) instead.
ANDROID_REVEAL_ALIEN_DAMAGE = 6    # $52A7 CMP #$06
ANDROID_REVEAL_MIN_HEALTH = 2      # $52C3 CMP #$02

# **Panic-wander's own entry gate** ([C `resolve_char_move` $5170-$51EC],
# P6-3, D-130). `char_wander` is reached only from `resolve_char_move` — the
# per-character engine's own turn-resolution routine, run at that character's
# own cadence, not every tick — and only past this test::
#
#   5170  LDA $6571,Y / CMP #$02 / BCC $517A   ; composure >= 2 -> ordinary
#                                               ; dispatch; panic never applies
#   517A  LDA $6501,Y / BNE $5182              ; in a duct -> ordinary dispatch
#   51DF  LDA $6571,Y / BEQ $51E7              ; composure == 0 -> broader path
#   5252  ...same room as a SURFACED Alien...  ; composure == 1 -> only here
#
# So an ordinary-composure crew member (>= 2) NEVER wanders — sharing the
# Alien's room used to be the only test modelled, which sent every crew member
# bolting the instant the Alien attacked anyone, composure notwithstanding.
PANIC_WANDER_MAX_COMPOSURE = 2     # $5170 CMP #$02 / BCC -> panic considered
#: **[C $5221 `LDA #$28 / STA $64EE,Y`] DISC-233** — `char_wander` re-arms the
#: wanderer's own turn timer to 40 passes, and does so **whatever the roll
#: produced**, including a destination equal to the room they are already in.
PANIC_WANDER_TICKS = 0x28

# **[C $4784 init_char_turn] D-151 — the companion-support term.**
# Effective composure (`$6571`) = own base (`$7D55`) + the sum over every
# co-located, surfaced crew member of `their base - 2`, with a flat -1 for
# each one who is collapsed (`$47F1 CMP #$02 / BCC -> $47F8 DEC $4781`),
# floored at 0. So a calm companion steadies you and a broken one drags you
# down; the pivot is the ROM's own `SBC #$02` at `$4806`.
COMPANION_SUPPORT_PIVOT = 2        # $4806 SBC #$02
COMPANION_SUPPORT_MIN_HEALTH = 2   # $47F4 CMP #$02
#: **[C $4CF5]** `raise_crowd_fear` refuses to raise past this — the ceiling
#: on base composure (`CMP #$0A / BCS skip`).
COMPOSURE_MAX = 10

# --- Jones the cat -----------------------------------------------------------
# **[C $8787-$880E] D-153 — catching Jones is a RANDOM ROLL, and the NET works
# too.** The handler reads a per-character threshold from `$883C,Y` (indexed by
# the selected crew slot), improves it by 4 when the held item is the NET
# (`$87A1-$87AA`, four `DEC $6518`), then rolls `rng` — whose scramble table
# `$887E` is a plain 0-15 ramp — and succeeds on `CMP $6518 / BCS`, i.e. when
# the roll is **>= the threshold**. So a lower threshold is better, and the net
# is markedly better than the box. Decoded straight from the PRG bytes; index 0
# is the Alien's slot and unused.
JONES_CATCH_THRESHOLD: tuple[int, ...] = (0, 14, 14, 13, 13, 13, 15, 14)
JONES_CATCH_ROLL_SIDES = 16        # $887E is 0..15
JONES_CATCH_NET_BONUS = 4          # $87A1-$87AA: four DECs
#: The two item types that can catch him: `$879A CMP #$10` (the NET) and
#: `$87C9 CMP #$11` (the CAT BOX). Anything else simply RTSes.
JONES_CATCHERS: frozenset[str] = frozenset({"net", "cat_box"})
#: **[C $88B6]** `LDA #$28 / STA $657F` — Jones moves once every 40 passes of
#: `sub_88ab_prechar`, which `char_pump` calls once per main-loop pass. This
#: replaces the old `[?]` `JONES_WALK_TICKS`, whose byte D-122 showed lands on
#: `var_frame_divider` and was never a cat timer at all.
JONES_MOVE_TICKS = 0x28

# --- Airlocks / BLOWLOCK ------------------------------------------------------
# **[C $5A6A `blowlock_vent`] D-155.** An OPEN airlock vents continuously —
# `apply_blowlock ($5B04)` is called from `check_deferred_move ($7305)` on
# every move pass, not once at the moment of opening. What the vent does:
#   * items lying in that room  -> location `$BD` (gone to space), `$5A6C`
#   * crew there ON THE SURFACE -> health 0 AND blown out, `$5A8D`/`$5A92`;
#     everything they carried goes with them (`$5A9E`). Crew inside a DUCT in
#     the same room are SAFE (`$5A80 LDA $6501,Y / BNE skip`).
#   * the Alien -> only if surfaced there (`$5ABF`) **and already hurt**:
#     `$5ACF CMP #$06 / BCC rts` means damage must be >= 6 before the vent can
#     touch it at all. Then `alien_maybe_hide ($5ADD)` rolls: `rng >= damage`
#     and it SURVIVES (taking +1 damage and a long delay); otherwise it is
#     blown out. So a healthy Alien simply ignores an open lock.
#   * Jones -> untouched; `$657D` is never referenced by the vent.
ALIEN_VENT_MIN_DAMAGE = 6      # $5ACF CMP #$06 / BCC rts
ALIEN_VENT_ROLL_SIDES = 16     # rng's scramble table is a flat 0-15
ALIEN_VENT_SURVIVE_DAMAGE = 1  # $5B00 INC $7D45 on a survived vent
#: **[C $5AF6 `LDA #$78`] PV-16** — an Alien that rides out an airlock vent
#: is stunned for 120 main-loop passes (~15 s at MAIN_LOOP_HZ) and forced to
#: the surface (`$5AFB STA $6501` = 0) at a destination of `rng >> 2` — a
#: flat 0-15 roll shifted down, so **rooms 0-3**: airlock 1, airlock 2, the
#: armoury, cargopod 1. Two of the four are locks, which is why blowing one
#: repeatedly is a real tactic and not a single squandered chance.
ALIEN_VENT_STUN_TICKS = 0x78

# --- The DUCT network — decoded [C, D-083 2026-08-02] ------------------------
# The original's ducts connect **rooms directly**, four tables of one neighbour
# room per room: `$80F5` (N), `$8117` (E), `$8139` (S), `$815B` (W), with a
# **self-reference meaning "no duct exit that way"**. There are no junction
# nodes — the remake's `Junction`/`add_duct` model was an invention, kept only
# for synthetic test maps. See `ShipMap.duct_exits()`.
#
# **The two graphs are separate.** Surface doors come from the five ROUTING
# tables (`gamedata_snapshot.SURFACE_EXITS`, the game's own `$7860` menu); only
# the ducts use these compass tables. Wire the ducts to the door graph and the
# duct network silently becomes a copy of it. `$8117`/`$8139` are EAST/SOUTH
# despite reading SOUTH/EAST in the labels.
#
# **[C $7373-$7392]** entering: a destination arrives with bit 7 set to mark it
# a duct move, and the entry costs one composure, gated on `$6571,Y >= 2` and
# skipped at 0. *Entering* is stressful; *staying* inside raises composure every
# tick (`$729C ADC #$01`) - hiding is reassuring once you are hidden.
# Derivation: DISCOVERIES D-086, D-083, D-059, P-1, P-2.
DUCT_ENTRY_COMPOSURE_COST = 1      # $738A SBC #$01
DUCT_ENTRY_COMPOSURE_GATE = 2      # $7381 CMP #$02 / BCC skip

# The character-location table's "removed / dead without a body" marker.
CHAR_GONE_MARKER = 0xFE            # $50B3 LDA #$FE / STA $7935,Y


# --- Action delay: acting while hurt is SLOW ([C $4042] P2-7) -----------------
# `compute_action_delay ($4042)` runs before an ATTACK ($48FC), a USE ($7B6E)
# and a GET/LEAVE ITEM ($8460), and **accumulates** onto the character's own
# timer (`$405D LDA $64EE,Y ... $4064 STA $64EE,Y`):
#
#     delay = ACTION_DELAY_BY_SLOT[slot] + ACTION_DELAY_BY_HEALTH[health]
#
# The health term is the interesting half: a crew member on **2 health takes
# +48 ticks** (about six seconds at the measured 7.886 Hz main loop) and one on
# 3 takes +16, while anyone at 4 or above pays nothing. So a wounded crew
# member is not merely weaker — they become visibly, punishingly slow to do
# anything, which is a large part of why losing people early snowballs.
# **[C $7B69 `LDA #$40 / STA $64EE,Y`] P3-2 — a room move takes 64 ticks,
# BEFORE the per-character and injury delays are added on top.** The move
# handler writes the destination into `$64E6,Y`, loads the countdown with a
# flat **`$40` = 64**, and only *then* calls `compute_action_delay`, which
# **adds** `ACTION_DELAY_BY_SLOT[slot] + ACTION_DELAY_BY_HEALTH[health]`
# (`$405D LDA $64EE,Y ... $4064 STA $64EE,Y`).
#
# So a healthy Dallas takes 64 + 7 + 0 = **71 ticks ~ 9 seconds** at the
# measured 7.886 Hz main loop, and a crew member on 2 health takes
# 64 + 7 + 48 = **119 ticks ~ 15 seconds**. The remake was using the `$6586`
# table (3-4 ticks, about half a second) as the whole duration, which is
# roughly **18x too fast** — the "movement is instant" the player reported.
# `$6586` is a per-character value the engine uses elsewhere; it is not the
# room-move timer.
MOVE_ACTION_TICKS = 0x40
#: **[C $48F7 `LDA #$28`] D-168** — ATTACK and USE arm a flat 40 passes
#: (~5 s) before `compute_action_delay` adds the slot and health terms.
ATTACK_ACTION_TICKS = 0x28
#: **[C $845A `LDA $403A,Y`] D-166 — REMVGRILLE has its OWN per-character
#: duration table, and it is a completely different aptitude profile.**
#: The grille handler loads `$403A,Y` into `$64EE,Y` and then calls
#: `compute_action_delay` on top, exactly as the move does with its flat
#: `#$40`. By slot (`$A65E` order), before the health term::
#:
#:     PARKER  80 · BRETT  80   (~10.1 s)   <- the two engineers, fastest
#:     DALLAS 100 · ASH   100   (~12.7 s)
#:     KANE   120               (~15.2 s)
#:     RIPLEY 180 · LAMBERT 180 (~22.8 s)   <- slowest by a factor of 2.25
#:
#: Note this is **not** the movement profile (`$4032`, where Ripley is the
#: quickest character in the game and Parker the slowest) — it is nearly its
#: inverse. Getting a grille off is an engineer's job, and the game says so in
#: data. The remake completed REMVGRILLE **instantly**, which removed both the
#: 10-23 second commitment and the whole characterisation.
GRILLE_ACTION_TICKS: tuple[int, ...] = (0, 100, 120, 180, 100, 180, 80, 80)


def grille_action_ticks(slot: int) -> int:
    """`$403A,Y` for a character slot (1-7); slot 0/unknown falls back to the
    slowest, so a synthetic test character is never accidentally instant."""
    if 1 <= slot < len(GRILLE_ACTION_TICKS):
        return GRILLE_ACTION_TICKS[slot]
    return max(GRILLE_ACTION_TICKS)
ACTION_DELAY_BY_SLOT: tuple[int, ...] = (0, 7, 5, 0, 7, 3, 10, 5)  # $4032, 1-7
ACTION_DELAY_BY_HEALTH: tuple[int, ...] = (0, 0, 48, 16, 0, 0, 0)  # $402B, 0-6


def action_delay(slot: int, health: int) -> int:
    """Ticks a character is busy after acting — [C $4042]."""
    base = ACTION_DELAY_BY_SLOT[slot] if 0 <= slot < len(ACTION_DELAY_BY_SLOT) else 0
    hurt = (
        ACTION_DELAY_BY_HEALTH[health]
        if 0 <= health < len(ACTION_DELAY_BY_HEALTH) else 0
    )
    return base + hurt


# **Not the original (B2).** How long the boot report holds before the loader
# starts on its own. Twelve seconds at the 6.25 Hz tick: long enough to read a
# path off the screen, short enough that a player who has read it once and does
# not press anything is not kept waiting. Any key or click skips it.
BOOT_TICKS = 75
