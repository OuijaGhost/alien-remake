# FAITHFULNESS.md — the remake's provenance ledger

The FV program's deliverable (`todo.md` → "★ FV", DECISIONS D-023). One table per
audited module: **every** behaviour/constant/table in `src/alien_remake/` carries a
provenance tag, so "does the remake match the original?" is answerable by reading,
not by hoping.

| Tag | Meaning |
|---|---|
| `[C $addr]` | Traces to a named routine/table in the disassembly. **This is the goal.** |
| `[?]` | Genuinely needs the running game to settle. Must cite its FV-2 item. |
| `[INVENTED]` | No basis in the code. **Must be removed or replaced** — never ships knowingly. |
| `[REMAKE]` | Scaffolding with no original counterpart (test seams, synthetic-map fallbacks). Legitimate, but must be inert on the real ship. |

A module is **FV-clean** only when it has zero `[INVENTED]` and every `[?]` is filed
with the exact cell/capture that closes it.

## Current status (2026-08-16)

| | |
|---|---|
| `[C $addr]` citations in `src/alien_remake` | **420**, over **1,155** distinct ROM addresses |
| `[INVENTED]` | **0** — pinned by `test_no_live_invented_marker_survives_in_the_source` |
| `[?]` | **40 live**, in 16 files; `constants.py` holds 11 of them |
| subroutines reached but unexplained | 0 (`UNDOCUMENTED.md`) |
| bytes of `ALIEN.prg` unclassified | **0** — the codemap census accounts for all 40,961 |

The census splits as: 8,192 graphics bank (decoded to charset + sprites), 15,775
reached as code, 12,064 data tables/text/templates, 4,930 `$FF` work-RAM and
padding. Nothing falls outside those four.

Coverage is not the same as correctness. This paragraph used to say **no win
route is reachable**, citing DISC-199 — a claim DISC-204 closed the same day by
finding the cause (the hull-breach test is a strict *equality*, `$5658 CMP #$14`,
on a counter that only ever INCs, so a room that overshot 20 became permanently
safe). The note outlived its own fix by eight days.

All three routes are now demonstrated end to end in `tests/test_winnability.py`
(DISC-253): ALIEN_KILLED by a scripted hunter, EVACUATED once the survivors fit
the evac room's capacity, and ALIEN_AIRLOCKED by venting a wounded creature.

### Where the remaining `[?]` are

Run `grep -rn '\[?\]' src/alien_remake` for the live list — but note that a few
hits are prose recording a `[?]` that was *closed*, so grep overcounts. Re-audited
2026-08-16; what is genuinely open falls into three groups.

**Structural — a known divergence, reasoned and deliberate:**

- **The hull-breach check shape.** The ROM gates *pre-add, per hit* and tests a
  strict equality (`$5658 CMP #$14`); the remake checks post-add, per tick,
  with `>=`. This is not an oversight: DISC-204 showed the equality is why a
  room that overshot 20 became permanently safe and the game unwinnable, and
  the remake's damage can arrive in a single 15-point harpoon step. Closing the
  gap means restructuring the check, not editing a constant.

**Calibration — needs the running game, listed in `VICE_CHECKS.md`:**

- `ROOM_DAMAGE_ALIEN_PER_ACTION`'s magnitude (correctly *gated* since DISC-199).
- The crew fear/obey numeric ranges, and the tracker's precision and the
  extinguisher's amount (`sim/orders.py`).
- Encounter odds in a newly-entered room (`alien.py`).

**Presentation — cosmetic, and flagged as such:**

- Front-end card durations, the breach spiral's pace (the one thing in
  `endscreen.py` not decoded), the joystick repeat rate, one placeholder red,
  and the per-glyph meaning of ALIEN's custom charset.

**Removed from this list (2026-08-16):** "the panic-wander precedence — three
ROM paths reach `char_wander` and which wins when several apply is unresolved".
No live `[?]` corresponds to it any more; the revealed android's turn is decoded
as an explicit ordered branch chain (`$52FC`/`$5309`/`$5311`/`$5339`) in
`sim/__init__.py`, where the ROM's own branch order *is* the precedence.

### The module-by-module audit

The July 2026 FV programme's full per-module record — what was traced, what was
`[?]`, what was invented and removed — is in
`archive/history/faithfulness-audit-2026-07.md`. It is the reasoning behind most
of the citations in the source, but it is frozen: module boundaries and several
of its conclusions have moved since.
