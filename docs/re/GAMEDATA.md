# The game's data tables, recovered from ALIEN.prg

Rooms, doors, ducts, items, crew and the per-character timing tables — where
each lives in the program, how it is laid out, and the evidence for reading it
that way.

These replaced a design built from the manual plus guesses. The manual describes
mechanics the program does not implement and omits several it does, which is why
this project's rule is *the code is the truth, the manual is a hint*.

    python -m alientools gamedata                 re-derive from your own disk
    python -m alientools gamedata --emit-python   regenerate the remake's copy

The remake reads a generated snapshot (`core/gamedata_snapshot.py`) rather than
decoding at startup. It is derived — never hand-edit it; a test compares it
byte-for-byte against a fresh decode.

All addresses are C64 memory addresses; `ALIEN.prg` loads at `$2000`.

## 1. The headline discovery: the game is data-driven, and the data survives

The gameplay model — map, items, characters, timing — is stored as plain
tables in the program image, not woven into code. Everything below is decoded
losslessly from those tables.

### 1.1 Rooms ($A71C, 36 × 10-byte screen-code records)

36 named locations, ids 0–35: AIRLOCK 1/2, ARMOURY, CARGOPOD 1–3, COMMDCENTR,
COMPUTER, CORRIDOR 1–7, CRYO VAULT, ENGINEERNG, "OTHER LIST" ×2 (see §5),
ENGINE 1–3, ENG STORES, INFIRMARY, INF STORES, LABORATORY, LAB STORES,
LIFE SUPPT, LIVNG QTRS, MESS, RECRTNAREA, STORES 1–3, SHUTTLEBAY, SHTTLSTORE.

**Verification:** the endgame RAM capture (`everyonedeadbutparkerandjones.bin`)
shows `MOVE TO: SHUTTLEBAY` rendered on screen while the ordered crew member's
location byte reads `$22` (34) — pinning the id↔name alignment. The sprite
code's `CMP #$22` (SHUTTLEBAY) check corroborates.

### 1.2 The map ($80D3 deck table; $80F5/$8117/$8139/$815B compass tables; $8676 grilles)

- **Deck table** (34 entries, values 4/5/6): 10/14/10 rooms per deck — the
  middle deck largest, matching the deck screenshots. **Which raw value is
  which deck is now LIVE-CONFIRMED (FV-2i, 2026-07-11): 4=UPPER, 5=MIDDLE,
  6=LOWER** — the remake's original guess (`4=upper`) was correct. Confirmed
  via the user driving INDICATE LOCATION live: room 0 (AIRLOCK 1, `$80D3`
  entry `4`) displayed under the "UPPER DECK" header; room 6 (COMMDCENTR,
  entry `5`) displayed under "MIDDLE DECK" (already independently confirmed
  by the 10/14/10 room-count match). `04`=UPPER is unambiguous (room 0's
  identity has no table-alignment risk); `06`=LOWER follows by elimination.
- **Four compass-neighbor tables** (N/S/E/W, one byte per room, sitting
  directly after the direction words `NORTH SOUTH EAST WEST IN DUCT` at
  `$8080`). "No exit" is encoded as the room's own id. Read together by the
  neighbor routine at `$8F66` and the Alien's movement at `$8AA2`.
- **Consistency proof:** every edge is mutual as an undirected graph. Pairs
  often bend direction (a→E→b, b→N→a) — exactly how an isometric deck plan
  with ladders behaves; all deck-crossing edges are mutual, and they are the
  ladders the game's own key text names (`LADDER UP` / `LADDER DOWN`).
- **Grille table:** every room has a grille except **CORRIDOR 6**.
- SHUTTLEBAY/SHTTLSTORE (the Narcissus) are off all four tables — reachable
  only via the shuttle specials, which is why `MOTHER REFUSES LAUNCH` exists.

### 1.3 Items ($82CF types, $82E3 rooms, names at $7C7D)

20 instances, **fixed** starting rooms (no shuffling):

| type | name (game's own) | count | starts at |
|---|---|---|---|
| 1 | ELCTRC PRD | 3 | ENGINE 3, ENG STORES, INF STORES |
| 2 | INCINERATR | 3 | COMMDCENTR ×2, ENGINEERNG |
| 3 | TRACKER | 2 | COMMDCENTR, ENGINEERNG |
| 4 | FIRE EXTNG | 4 | OTHER LIST ×2, ENGINE 1, LIFE SUPPT |
| 5 | HARPN GUN | 1 | STORES 2 |
| 6 | LASER PIST | 3 | **ARMOURY ×3** |
| 7 | NET | 1 | INF STORES |
| 8 | CAT BOX | 1 | INFIRMARY |
| 9 | SPANNER | 2 | RECRTNAREA, ENGINE 2 |
| 10 | THERMLANCE | 0 | (type exists, never spawned) |

**Verification:** the code reads three items' location slots at *fixed*
addresses — `$82E9`/`$82EA` are exactly items 6/7 (the two TRACKERs — the
"HAS A READING" feature) and `$82F4` is item 17 (the CAT BOX — "SEES JONES IS
HERE"). Both special-cased items land on the right types only with this
alignment. The manual's counts were exactly right; its **"taser" is the
game's LASER PISTOL** (no taser exists in the program).

Consumables are real ("…S LASER IS EXAUSTED", "…S EXTINGUISHER IS EMPTY",
"…S TRACKER IS SMASHED") — not yet modelled in the remake `[?]` (filed).

### 1.4 Characters ($7935 locations; $6586 walk durations; $6581 alien move)

Nine character slots: **0 = the Alien, 1–7 = crew in CONTROL-panel order
(DALLAS, KANE, RIPLEY, ASH, LAMBERT, PARKER, BRETT), 8 = Jones**. `$FE` =
removed/dead-without-a-body.

- Static start: DALLAS/KANE/RIPLEY in COMMDCENTR, ASH/LAMBERT/PARKER in
  LIFE SUPPT (BRETT placed at init — the captures show him joining the
  LIFE SUPPT group).
- The one captured session shows **LAMBERT** as the opening death and the
  Alien starting in **CARGOPOD 2**; a single capture can't prove either is
  fixed rather than randomized `[?]`.
- Walk durations (main-loop units per room move): Dallas 4, Kane 4,
  Ripley 3, Ash 4, Lambert 3, Parker 4, Brett 3, Jones 5. The Alien's
  surface move is **60** (`$8A4A`), not 70 — **corrected D-038,
  2026-07-24**: `$6581` (=70) is real ROM data but belongs to the
  in-duct dispatcher's own duct-to-duct timer, not the general compass
  move; see §1.5's correction note below.

**Verification:** across the four captures from that same run only slot 0 changes
(CARGOPOD 2 → STORES 2 — the Alien moving); in the endgame capture PARKER's
slot reads SHUTTLEBAY while the screen shows him being ordered there.

### 1.5 The Alien's real AI (routine $8A74)

**CORRECTION (D-038, 2026-07-24 de-invention audit round 2):** `$8A74`
(`alien_ai`) is NOT the Alien's main per-action dispatcher — it's a
separate, **in-duct** dispatcher (checked only while the Alien is already
hidden in the duct network: it re-rolls and picks among the duct-neighbor
tables `$80F5`/`$8117`/`$8139`/`$815B` to keep moving duct-to-duct, or
re-emerges). The description below (0–12/13–15 roll split, 70/40-unit
timers) is `alien_ai`'s *own* internal roll, not the general compass-move
decision. The **real top-level dispatcher is `alien_choose_move ($8A36)`**,
called each time the Alien needs a new action: it rolls uniform 0–15 and
splits **0–11 (12/16) → surface move** (reading the five 36-entry routing
tables at `$7A3A` etc., **60-unit** moves, confirmed at `$8A4A: LDA #$3C`)
vs **12–15 (4/16) → enter the duct** (**40-unit** hide, "ALIEN GONE THROUGH
GRILLE"). The paragraph below's "separate path... probably scripted
pursuit `[?]`" note undersold this: the `$7A3A` tables aren't a rare/
scripted special case, they're the Alien's **normal, everyday surface
movement** — confirmed and already wired into `alien_remake.core.constants
.ALIEN_MOVE_TICKS` (corrected 70→60) and `ALIEN_ROUTES`. This file's
own decoded facts (the "$7A3A ... 60-unit moves" note two paragraphs below)
already had the right numbers; they just hadn't been connected to correct
the `$8A74`/`70` mislabeling above. Left as historical text below rather
than fully rewritten (this file is largely a Phase 1 toolkit reference,
out of scope for a full rewrite in this remake-focused pass) — trust the
correction above and `docs/re/DISASSEMBLY.md` §8.10 / `constants.py` over
the paragraph that follows.

Each time its action timer runs out it rolls **uniform 0–15** (the RNG at
`$888F` mixes the jiffy clock through an identity table at `$887E`):

- **0–12** (13/16): one compass move — 0–2 N, 3–5 S, 6–8 E, **9–12 W** (a
  built-in west bias) — reading the same neighbor tables. A blocked direction
  still consumes the action (it "moves to" its own room: an idle). Takes
  **70** units.
- **13–15** (3/16): slips through its room's grille into the duct, hidden,
  for **40** units ("ALIEN GONE THROUGH GRILLE").

**There is no sensing/hunting of the nearest crew member in this routine.**
Five 36-entry routing tables at `$7A3A` (next-room hops, 60-unit moves) are
used by a separate path whose trigger wasn't pinned down `[?]` — probably
scripted pursuit; deliberately not guessed at in the remake.

### 1.6 Timing: how the game actually paces

- The IRQ (`$4D08`) divider at `$4D19` reloads `#$08` and fires on the wrap
  below zero → the IRQ tick is every **9** jiffies (not 8 frames as the behaviour spec
  recorded) — and the four routines it calls (`$4EE8/$4F19/$4F52/$4FCB`)
  are **sprite-animation/sound updates only**. GAME_SPEC §2's "the IRQ drives
  four game-update routines at ~6 Hz" was wrong on both counts.
- World state advances from the **free-running main loop** at `$719D`
  (pause-check `$6483` → sprite/screen work → the character pump `$7216`,
  which decrements the per-character action timers and resolves whoever hits
  zero). The *ratios* between all durations above are ground truth; the
  absolute loop rate is machine-paced and not yet measured `[?]` — the remake
  keeps a ~6.67 Hz calibration default.

### 1.7 Words, menus, endings (screen-code text throughout the image)

- **Status words** (`$7CEA`): O.K. / WOUNDED / COLLAPSED / DEAD — the crew
  have physical states beyond alive/dead (and an `IS INSANE` ending exists).
  Not yet modelled `[?]` (filed).
- **Morale words**: CONFIDENT / STABLE / UNEASY / SHAKEN / BROKEN (the remake
  previously invented Calm/Nervous/Afraid/Panicking).
- **Order menu** (`$A86E`, seen live in the endgame capture): MOVE TO /
  ITEMS PRESENT → GET ITEM / LEAVE ITEM / USE / ATTACK / SPECIAL / QUIT.
- **Specials** (`$57B6`): BLOWLOCK 1/2, SEALLOCK 1/2, ENTER HYPERSLEEP,
  BOARD NARCISSUS, LAUNCH NARCISSUS, OVERRIDE DETONATION, **FIGHT FIRE**.
- **Systems-damage strings** (`$548D`): STRUCTURAL DAMAGE TO…, PARTIAL
  SYSTEMS CONTROL LOSS, COMPUTER/CRYOGENICS MALFUNCTION, FIRE IN…,
  NARCISSUS STATUS RED, SHIP WILL DESTRUCT IN __ MINS — a whole
  damage/fire/malfunction system the remake doesn't model `[?]` (filed).
- **Endings** (`$6314`): "…BRINGS THE NOSTROMO BACK TO EARTH", "THE NOSTROMO
  IS DESTROYED", "THE ALIEN AND ITS EGGS ARE UNLEASHED UPON THE PLANET",
  "ALL CREW LOST", plus a **COMPETENCE RATING** grade `[?]` (filed).
- **Title** (`$5F59`): GAME SELECTION — 1 FULL GAME / 2 SHORT SCENARIO,
  "PAUL CLANSEY ©1984 CONCEPT SOFTWARE"; epigraph "WE LIVE AS WE DREAM —
  ALONE (JOSEPH CONRAD)".

## 2. What the audit changed in the remake

| Area | Was (manual+guess) | Now (code) |
|---|---|---|
| Map | 3 eyeballed deck grids (SM), rule-generated doors | The real 34-room graph, names, decks, compass exits, ladders, grilles |
| Items | 9 invented ids incl. "taser", shuffled placement | The game's 10 types (LASER PIST, THERMLANCE…), 20 fixed placements |
| Crew start | round-robin on the top deck | COMMDCENTR ×3 + LIFE SUPPT ×4 (real) |
| Opening death | Kane (film canon guess) | Lambert (observed in the captures) `[?]` |
| Crew speed | one room per tick, uniform | per-crew 3–4 ticks/room; Jones 5 (real $6586 table) |
| Alien AI | senses nearest crew, BFS-hunts, 1 room/tick | uniform-roll route-table surface walk **60 ticks/move** (corrected from 70, D-038) + duct hides 40 `[C]` |
| Morale words | Calm…Panicking (invented) | CONFIDENT…BROKEN (real $7CEA) |
| Evacuation | survivors gather in an "airlock" | survivors gather in the SHUTTLEBAY; airlocks are the two real BLOW/SEAL locks |
| Short mode | drops the lowest deck | same topology (nothing in the data supports a smaller map) `[?]` budget-only |
| Tick constants | 8 PAL frames → 6.25 Hz "game tick" | 9 jiffies for the anim/sound IRQ; world = main-loop units, rate `[?]` |

## 3. Open items (real, filed, deliberately not guessed)

1. The `$7A3A` routing tables' trigger (scripted Alien pursuit?) — decode the
   caller at `$8A36`'s context.
2. Consumables (laser charge, extinguisher fill, tracker smashing) and the
   WOUNDED/COLLAPSED/INSANE crew states.
3. The fire/structural-damage/malfunction system and FIGHT FIRE special.
4. The real morale *mechanics* (what moves crew between CONFIDENT…BROKEN and
   how that gates orders) — the remake's PCS gate remains an approximation.
5. ~~Oxygen/TOOH~~ **CLOSED 2026-08-01 (D-062): there is no oxygen system.**
   No counter exists (R-22 RAM scan), no OXYGEN/AIR/TOOH string exists in the
   complete 117-string inventory, the status template `$7A10` carries only
   DAMAGE and MORALE, and the jiffy clock `$A0-$A2` is never read. The
   parenthetical this item used to carry — "`$7A1B` reads the jiffy clock for
   the status display" — was **wrong**: `$7A1B` is the `'%'` byte *inside* that
   template, i.e. data, not code. The manual's 7,500-unit budget documents a
   mechanic the shipped game never implemented.
6. ~~Absolute main-loop rate~~ **CLOSED 2026-08-01 (D-063): 7.886 Hz.**
   Measured with a non-stopping checkpoint on `$719D` (pass count) bracketed by
   `vice_cycles_stopwatch` (emulated cycles): 158 passes / 20.035 s. That is
   ~6.36 PAL frames per pass, free-running. `$64EE[0]` decremented exactly once
   per counted pass, with reloads of 60 and 40 — corroborating the decoded
   move-cost tables.
7. Which raw deck value (4/5/6) is the game's "UPPER DECK", and the real
   per-deck screen layout (would also fix marker alignment on the backdrops).
8. "OTHER LIST" rooms 17/18: real in-game labels to confirm (menu-pagination
   artifacts vs. actual room names).
