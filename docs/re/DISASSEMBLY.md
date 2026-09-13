# How ALIEN.prg works

A walk through the program: the loader chain, the interrupt, the main loop and
its clock, and what each routine does. Written before the Python rewrite, and
the rewrite is written from it.

Claims here were checked against the **running** program in an emulator — set a
breakpoint, step it, read the bytes — not inferred from reading alone. Where a
value could not be settled that way it is marked `[?]`.

Companions: [`alien.sym`](alien.sym) (VICE labels, so a live disassembly is
symbolic), [`GAMEDATA.md`](GAMEDATA.md) (the data tables), and
[`ALIEN.annotated.asm`](ALIEN.annotated.asm) (the classified listing).

**Status legend:** ✅ confirmed live · 🟡 static-derived, not yet stepped ·
⬜ not yet analysed. This document is built incrementally; ⬜ regions are listed
in the routine catalog (§9) with their entry addresses so they can be picked up
one at a time.

---

## 1. Methodology

The program loads at `$2000` (`ALIEN.prg`), entered via `SYS 16384` (`$4000`).
`$2000–$3FFF` is the graphics bank (charset + sprites — SG); code starts at
`$4000`. The workflow for each region:

1. `vice_disassemble <addr>` (symbolic) to read it.
2. `vice_checkpoint_add`/`vice_watch_add` + `vice_execution_step` to confirm what
   it does to memory/registers while running.
3. Name the routine in `alien.sym`; annotate it here.

## 2. Memory map (while ALIEN is loaded & running)

| Range | Contents |
|---|---|
| `$0000–$00FF` | Zero page. KERNAL + game scratch (`$FB/$FC`, `$FD/$FE` pointers used by the screen/char routines). |
| `$0100–$01FF` | CPU stack. |
| `$0200–$03FF` | KERNAL work area + **indirect vectors**. `$0314/$0315` = IRQ vector (set to `$4D08`). `$0328`, `$0291` patched at entry. |
| `$0400–$07E7` | **Screen RAM** (40×25). The map + CONTROL panel + status are rendered here. |
| `$07F8–$07FF` | **Sprite pointers** (8). Set to `$BD–$C3` (= sprite slots 29–35) for the crew portraits on the selection screen. |
| `$2000–$27FF` | **Charset** (256 glyphs) — VIC char base pointed here (`$400A`: `$D018` ← `$08` within bank). |
| `$2800–$3FFF` | **Sprite** data. Slot *N* at `$2800 + N×64`; pointer value = `(addr−bank)/64`. E.g. pointer `$BD` → `$2F40` → slot 29. |
| `$4000–~$C000` | **Game code + data tables** (see §9 and GAMEDATA.md). |
| `$5EC0–$5ECD` | Portrait sprite X/Y table (7×2 bytes) copied to `$D000`. |
| `$6xxx` | Game **variables** block (`$64xx` timers/flags, `$6579` frame divider, `$6581` alien-move ticks, `$6586` walk ticks, `$65xx` char state). |
| `$79xx` | `$7935` char-location table (9 slots). |
| `$7A3A` | Routing tables (5×36) — Alien scripted moves `[?]`. |
| `$80D3.. $815B` | Room deck + N/S/E/W neighbour tables. `$8676` grille table. |
| `$82CF/$82E3` | Item type/room tables. `$7C7D` item names. `$A71C` room names. |
| `$887E/$888F` | RNG output table + RNG routine. |
| `$9039` | Title-screen SID music player. |
| `$D000–$D3FF` | VIC-II (`$D000` sprite pos, `$D015` enable, `$D018` char/screen base, `$D019/$D01A` IRQ, `$D027+` sprite colours). |
| `$D400–$D7FF` | SID. `$D800–$DBE7` colour RAM. `$DC00` CIA1 (joystick port 2 / keyboard). |
| `$E000–$FFFF` | KERNAL ROM. |

## 3. Boot / load chain ✅ (driven live 2026-07-08)

The disk boots exactly as the static analysis predicted, confirmed by driving
it in VICE (`vice_keyboard_type`/`vice_display_screenshot`):

1. **Green Valley/ShareData back-up notice** ("MAKE A BACK-UP COPY…", press any key).
2. **"WELCOME TO ALIEN … 1 ALIEN / 2 QUIT"** front-end. Press `1`.
3. Disk loads the ALIEN module → ALIEN's own **"DO YOU WANT INSTRUCTIONS? (Y/N)"**
   (`$443C` text). Press `N`.
4. **"LOADING…. / PLUG JOYSTICK INTO PORT TWO"** (a second load stage; the game
   comes in segments — R-11).
5. **Game-selection screen** (portraits + Control:1 Full / Control:2 Short),
   drawn by `main_dispatch` (§6). **Input (R-18):** the loop at `$5F36` reads
   the KERNAL keyboard latch **`$91`** — `$FA` = **Ctrl+1** → Full Game, `$F3`
   = **Ctrl+2** → Short Scenario (the on-screen "Control:1/Control:2" is
   literally the **Ctrl key + 1/2** held together, which is why a bare "1"
   keypress does nothing — the two-key chord produces those `$91` column
   patterns). Writes the choice to `var_game_mode ($4303)`, `JMP start_game
   ($7013)`.

## 3.5. Live-oracle session — driving the game & findings ✅ (2026-07-08)

Booting into gameplay under vice-mcp and observing live confirmed several
things and clarified the method for future passes:

- **Getting in-game past the Ctrl+1 chord:** the selection loop polls `$91`; a
  scripted keypress didn't reproduce the chord's latch value, so the reliable
  path is to **write `$91=$FA` while paused and run** (the loop re-reads `$91`
  and takes the Full-Game branch). `var_game_mode ($4303)` then drives
  `start_game`.
- **Start positions confirmed live:** `tbl_char_location ($7935)` read
  `[0,6,6,6,27,27,27,0,0]` — Alien in room 0, crew in COMMDCENTR(6)×3 +
  LIFE SUPPT(27)×3, Jones/Brett room 0 — **exactly** GAMEDATA.md's values.
- **Time base = the KERNAL jiffy clock** (`$A0/$A1/$A2`), which advances while
  the game runs; the `$6400+` game-var block does *not* free-run — it changes
  only as characters act. This supports the "TOOH/oxygen = elapsed jiffies"
  hypothesis (R-22) rather than a dedicated down-counter.
- **Wounding is real (R-26):** the status line showed "Alien wounds Ripley"
  (a WOUNDED state, distinct from killed).
- **Game-over handler `game_over_wait ($6469)`:** `LDA kernal_last_key ($C5) /
  CMP #$40 / BEQ` (wait for any key) → `JSR init_c ($5DEB)` → `JMP
  main_dispatch ($5ECE)` (back to the selection screen). In **warp** with no
  player input the Alien clears the crew in seconds, so the game reaches this
  handler almost immediately.

**Method for the next live pass** (to watchpoint oxygen/morale and trace the
CONTROL-panel order code): **disable warp** (`vice_machine_config_set` with
`{"resources":{"WarpMode":0}}`), reach active play, and single-step / diff while
it advances. `vice_checkpoint_add` on `resolve_char_move ($5156)` catches a
crew step.

### Live pass 2 (warp off) — the opening + the oxygen question

> **★ CORRECTION 2026-08-01 (D-075) — `$64BB` is NOT "game active".** Everything
> in this section that calls it `var_game_active` is mislabelled. Tracing its
> only setter proves it: `begin_active_play ($4F90)` sets `$64BB = 1` and then
> enables **sprites 4-7** (`$D015 = $F0`) and programs an SFX; `stop_active_play
> ($5017)` clears it and restores **sprites 0-3** (`$D015 = $0F`). Its only
> caller chain is `$8CF3` → `begin_active_seq ($8D1A)` → `$4F90`, and `$8CF3`
> sits in the path that displays the string at `$8C76` — which decodes to
> **"ATTACK"**. So `$64BB` flags an **Alien attack / encounter sequence**, a
> cinematic burst with its own sprite set and sound, not "the game is being
> played". That also explains `update_1` below animating the Alien sprite while
> it is set (the attack cutaway) without contradicting D-041/D-046, which
> established the Alien is never drawn on the *map*.
>
> **Consequences:** (1) `pause_check ($6483)` returning early while `$64BB != 0`
> now reads sensibly — you cannot pause mid-attack. (2) Every prior attempt to
> "reach active play" by waiting for `$64BB == 1` was waiting for an **Alien
> attack**, which is why it never fired. (3) **R-29's caveat is retracted**: its
> main-loop rate was sampled with `$64BB = 0`, which is *normal play*, not a
> pre-play state — the measurement needed no such qualification.


- **A nested busy-wait `delay_loop ($7560)`** (`INX/BNE ... INY/BNE`) is used by
  the **front-end/title sequence** — the screenshot at `$7560` was
  the **title screen** (egg + "ALIEN" letters animating + the Conrad epigraph),
  *before* the game-selection portraits and the opening-death. (A prior turn's
  attribution of `$7560` to the opening-death scenario conflated the title and
  the opening — corrected here.) `var_game_active ($64BB)` separately gates the
  game logic: crew/Alien movement and the `update_*` sprite routines
  (`update_1` returns early if `$64BB`==0) do not run until active play begins
  and sets `$64BB = 1`.
- **The front-end sequence is: title (egg/epigraph) → game-selection (portraits,
  Ctrl+1) → opening-death → play.** Scripted boot with fixed sleeps is
  timing-fragile, so use **`tools/vice-mcp/boot_to_play.py`** — it detects each
  screen from screen RAM (`$0400`) and sends the right input, reliably reaching
  the play screen (tested: notice→welcome→instructions→title→selection→play in
  ~15 s). Forcing `$64BB=1` to skip ahead is **unstable** (game resets to menu).
- **The play screen appears during the opening-death display while `$64BB`
  (game_active) is still 0** — the game spins in the `$7560` busy-wait showing
  "<name> has been killed by the ALIEN"; active play (crew/Alien movement, the
  `$4843` order-gate update) begins only when `$64BB` flips to 1.
- **`begin_active_play ($4F90)`** is the routine that sets `$64BB=1` (+ sprite/
  timer setup); its sole caller is **`begin_active_seq ($8D1A)`** =
  `JSR $7EE5 / JSR $4F90 / STA $64EE` (Alien timer), called from `$8CF3`.
  `pause_clear_active ($501E)` sets `$64BB=0`.
- **The opening→play transition is a TIMEOUT** (confirmed by the user playing
  normally: "it's a time out to get past the screen of who got killed" — no
  input). The "<name> has been killed" screen shows for a fixed delay, then
  `$8CF3`→`begin_active_seq ($8D1A)`→`begin_active_play ($4F90)` fires and
  `$64BB` flips to 1. My headless attempts to observe it failed because state
  manipulation (forced flags / PC jumps / warp) broke the normal timeout flow —
  a **clean boot left running at normal speed advances on its own** (`$8CF3`'s
  caller counts the delay down; the exact counter is `$64E5`/`$64E4`-adjacent,
  seen incrementing in the capture). Reusable snapshot via `vice_snapshot_save`
  (needs a **`name`** param); the user's `the live captures (not published)walking.vsf` is a live
  mid-order snapshot.

### Issuing a MOVE order (from the user's before/after capture) ✅

Diffing `the live captures (not published)pcs_before.bin` → `pcs_after.bin` (Dallas ordered
CommdCentr→Corridor#1) shows an order writes exactly:
- `var_current_char ($64FB)` = the ordered crew slot (**1** = Dallas).
- `tbl_char_dest ($64E6,slot)` = the destination **room id** (`8` = Corridor 1;
  plain room id, no `$80` bit for crew — that bit is Alien-in-transit only).
Then `char_pump` walks the character there after the **action-timer**
(`$64EE,slot`) delay the user described. `$7D55`/`$6571` are **not** touched by
the order. (Other diffs were incidental: the RNG seed `$6519/$651A`, the Alien's
own timer/dest, and screen-draw counters.)

**The "move to:" list (R-16, user-confirmed):** the menu offers the crew's
current room's **direct connections only** — the same-deck compass neighbours
*plus* the up/down-deck links where the room connects that way (the ladders) —
scrolled on the right panel (up/down + fire; sequence crew → verb → room). It is
**not** "all reachable rooms". So the list = the room's real exits from the
neighbour tables (`$80F5/$8117/$8139/$815B`, minus self-loops). **Remake fix:**
`core/menu.py` currently offers reachable-rooms-capped; change it to the room's
direct exits (`Room.exits`), and a single order moves one hop (multi-hop = multi
order). The stable route to a traceable active game
  is to let the opening finish, then issue a real **MOVE order via the joystick
  CONTROL panel** (which drops the crew member's `$6571` gate `<2`); injecting
  `dest`+`timer` on an idle crew member does **not** move it (`$6571 ≥ 2`
  aborts in `resolve_char_move`).
- **Active-play cadence (1×, live):** the **Alien moves ~once per 9 seconds** —
  its timer `$64EE[0]` counts down from 70 at ~8 units/sec (main-loop rate).
  Crew sit idle (`$64EE[1..7] = 0`) with no destination until ordered, so
  nothing moves without player input. `tbl_char_location[2] = $FE` = the
  opening-dead crew member.
- **★ Oxygen/TOOH (R-22) — no down-counter exists.** A monotonic-decrease scan
  of **all** game RAM (`$6000-$7FFF` + `$C000-$C3FF` + zero page) over 10 s of
  active play found **zero** steadily-decreasing cells (only the sound tick
  `$64B7` cycles). So oxygen is **not** a stored per-frame counter — it is
  **not implemented at all** — see D-062 (2026-08-01), which closed this.
  **CORRECTION:** this paragraph used to claim oxygen was "time-derived (the
  jiffy clock `$A0-$A2`; GAMEDATA.md's `$7A1B` reads it for the display)".
  Both halves are wrong. `$7A1B` is **data** — the `'%'` byte inside the status
  template at `$7A10` (`": DAMAGE 00% IS ........,MORALE:........"`) — not a
  routine; and the jiffy clock `$A0-$A2` is read **zero** times anywhere in the
  classified `$2000-$C001` region. Combined with the complete 117-string
  inventory (no OXYGEN/AIR/TOOH text anywhere) and this RAM scan, the C64 game
  simply **has no oxygen system**. The remake's down-counter was an invention
  and has been removed, not reworked.

## 4. Entry + init ✅

```
entry_sys16384 ($4000):
    LDA #$EA / STA $0328        ; patch a KERNAL RAM vector byte with NOP
    LDA #$80 / STA $0291        ; disable Commodore-Shift charset case-switch
set_charbase ($400A):
    LDA $D018 / AND #$F0 / ADC #$08 / STA $D018   ; VIC char base -> $2000 (in bank)
    LDA #$00 / STA $D020 / STA $D021              ; border=black, background=black
    JSR init_a_raster_irq       ; $4DB8
    JSR init_b_music            ; $8FFC
    JSR init_c                  ; $5DEB
    JMP main_dispatch           ; $5ECE
```

```
init_a_raster_irq ($4DB8):        ; ✅
    SEI
    LDA #$08 / STA $0314          ; IRQ vector low
    LDA #$4D / STA $0315          ; IRQ vector high  -> $4D08 (irq_handler)
    LDA #$61 / STA $D012          ; raster compare = line $61 (97)
    LDA $D011 / AND #$7F / STA $D011   ; raster high bit = 0
    LDA #$81 / STA $D01A          ; enable raster IRQ
    CLI / RTS
```

`init_b_music` (`$8FFC`) and `init_c` (`$5DEB`) — 🟡 (init_b sets up the SID
player state incl. the `$91D6` sweep counter, per the audio work; init_c not yet stepped).

## 5. IRQ handler + game tick ✅

```
irq_handler ($4D08):
    LDA $D019 / AND #$81 / CMP #$81 / BEQ $4D58   ; raster+IRQ both set -> raster-split
                                                  ; handler ($4D58, sprite multiplex)
    LDA var_music_mode ($60A8) / BEQ game_tick_dispatch
    JMP title_music_player ($9039)                ; music_mode!=0 -> title tune
game_tick_dispatch ($4D19):
    DEC var_frame_divider ($6579) / BPL $4D2F     ; every 9th jiffy (reload #$08,
    LDA #$08 / STA var_frame_divider              ;   fire on wrap below 0)
    JSR update_1 ($4EE8)     ; sprite animation frame advance
    JSR update_2 ($4F19)     ; sprite update
    JSR update_3 ($4F52)     ; sprite update
    JSR update_4 ($4FCB)     ; sprite update
$4D2F:
    LDA $64BB / BNE $4E76    ; $64BB flag -> alternate handler
    DEC var_sound_tick ($64B7) ...   ; sound register update
```

**Confirmed model:** the raster/CIA IRQ fires the four `update_*` routines every
**9 jiffies**, and they are **sprite-animation + sound** only. World/game state
does NOT advance here — it advances in the free-running main loop (§7). This is
the timing correction from GAMEDATA.md, now live-verified at instruction level.

`update_1` ($4EE8), gated by `$64BB` (the **attack-sequence** flag, D-075), animates the **Alien
sprite** *during an attack cutaway*: `var_anim_frame ($64BF)` cycles 0→11 (12 frames); it indexes
`tbl_alien_anim ($4EDC)`, adds base pointer `$A0` (= sprite slot 0, `$A0×64 =
$2800`), and writes the resulting sprite pointer(s) — so the on-map Alien is the
**animated sprite slots 0-15**, cycled here (R-05: the remake should draw the
Alien as this animation, not a red "X"). `update_2/3/4` similarly drive the
other moving sprites (Jones etc.) + the sound registers.

## 6. Game-selection screen — `main_dispatch` ($5ECE) ✅ — resolves R-09

```
main_dispatch ($5ECE):
    LDA #$00 / STA $D015 / STA $D01C    ; sprites off, sprite-multicolor off
    JSR $5FC3                            ; (screen clear/setup) 🟡
    ; copy 14 bytes $5EC0.. -> $D000 (sprite X/Y for 7 portraits)
    LDA #$40 / STA $D010                 ; sprite 6 X high bit
    ; clear sprite colours $D027-$D02E
    ; sprite pointers $07F8-$07FE = $BD,$BE,$BF,$C0,$C1,$C2,$C3
    LDA #$FF / STA $D015                 ; enable all sprites
    ; copy 4 label strings into screen RAM:
    ;   txt_game_selection ($5F59) -> $05E0
    ;   $5F68 -> $065C ; $5F7F -> $06AC ; $5F9B -> $07C0
```

After drawing, `main_dispatch` falls into the **input loop** (`$5F36`): read
`$91`; on `$FA` (key 1) → `var_game_mode ($4303) = 1` → `JMP start_game
($7013)`; on `$F3` (key 2) → `var_game_mode = 2` → `start_game`. `start_game`
(`$7013`) begins the opening/play (⬜ — next pass).

**Portrait facts (live-read `$5EC0` + pointer math):**
- Sprite pointers `$BD–$C3` → sprite slots **29–35** left-to-right
  (`$BD×64 = $2F40 = $2800 + 29×64`). ✅ (my remake's slot order was right.)
- Positions: **all 7 at Y=`$52` — one level row** (X = 48, 88, 128, 168, 208,
  248, 288). **Correction for the remake (R-09):** the *faces* are a single
  horizontal row; only the *name labels* are staggered above/below. The remake
  currently staggers the sprite rows — should be one row.
- Name↔face mapping (from label X-positions vs face X): Dallas, Kane, Ripley,
  Ash, Lambert, Parker, Brett, left-to-right — matches the remake's
  `_PORTRAIT_LABELS`. (Confirm exactly by reading the name-draw code — ⬜.)

## 6.5. `start_game` ($7013) 🟡 — Ctrl+1/2 → play screen → main loop

Reached from the selection input. Static-derived from `out/ALIEN.asm`:

```
start_game ($7013):
    ; blank the screen + sprites
    LDA #$00 / STA $D000-$D003 (sprite 0/1 pos) / $D010 / $D015 (sprites off)
              / $D021 (bg=black) / $D020 (border=black)
    STA var_music_mode ($60A8)      ; 0 -> IRQ switches from title tune to GAME TICK
    JSR sub_play_setup ($6682)
    LDA #$01 / STA $D027            ; sprite 0 colour = WHITE  (the person/char marker)
    LDA #$03 / STA $D028 / STA $D015 ; sprite 1 colour = cyan; enable sprites 0,1
    JSR $4DF0 (SID setup) / JSR init_a_raster_irq ($4DB8) / JSR sub_4e87 ($4E87)
    LDA var_game_mode ($4303) / BEQ + / JSR game_init_mode ($4304)  ; mode-specific init
    JSR sub_5049 ($5049)
    LDA #$06 / STA $D020            ; border = BLUE ($06) — matches the captured $D020
    ; --- build the play screen from RAM templates ---
    LDA $01 / AND #$FE / STA $01    ; LORAM=0 -> bank out BASIC, RAM at $A000+ visible
                                    ; (this is why the $A71C room-name table is readable)
    ; fill panel colour RAM ($D81E, $DAEE) with $0F (light grey)
    ; copy screen-code template  $A654 (tbl_playscreen_template) -> $041E  (10 cols x 19 rows)
    ; copy colour template        $7001 (tbl_playscreen_colors)   -> $D846  (10 cols x 18 rows)
    ; ... more per-cell setup ...
    SEI / LDX #$32 / TXS / CLI      ; reset the stack
    JMP main_loop ($719D)
```

**Confirmations for the remake:** the **blue border** (`$D020=$06`), the
**white person marker** (sprite 0 colour `$01`), and that the CONTROL-panel +
status **layout is a fixed screen template** at `$A654` (screen codes) with
colours at `$7001` — i.e. the panel text/colour bands the remake hand-builds
are literally a copied template. `game_init_mode ($4304)` is the Full/Short
mode-specific init (also seen exiting via `JMP $719D` at `$42FC`).

## 7. Main loop + character pump 🟡 (static-derived; live-confirm pending)

```
main_loop ($719D):
    JSR pause_check ($6483)        ; STOP/pause handling
    JSR $7453                      ; (screen/sprite refresh)
    JSR char_pump ($7216)          ; per-character update — THE WORLD CLOCK
    JSR $5684                      ; (?)
    JSR $5A26                      ; (?)
    JMP main_loop                  ; ($71AC)
```

### `char_pump` ($7216) — the movement engine

```
char_pump ($7216):
    STA $64F6 / STA var_char_acted ($6517) = 0
    JSR $88AB                          ; RNG/seed advance
    JSR alien_tick ($8ACE)             ; advance the Alien first
    LDY #$01                           ; Y = crew index 1..7 (slot 0 = Alien)
loop ($7226):
    LDA tbl_char_action_timer ($64EE),Y
    BEQ next                           ; timer already 0 -> skip
    DEC it (SBC #1, STA back)
    BNE next                           ; not 0 yet -> skip
    ; --- this character's timer hit 0: resolve its next action ---
    var_char_acted ($6517) = 1
    JMP resolve_char_move ($5156)      ; returns to $7244
$7244:
    LDA $650C,Y / BNE $8749            ; char has pending special -> sub_char_special
    ...
    CPY var_current_char ($64FB) / BEQ + / JSR sub_char_redraw ($73A3)
    LDA tbl_char_dest ($64E6),Y -> $7215   ; the char's DESTINATION room
    CMP #$80 / BCS $732E               ; dest >= $80 -> in-duct / removed handling
    ; --- ROOM-CAPACITY CHECK ---
    count X = number of OTHER chars whose location ($7935,Y) == dest and $6501,Y==0
    CPX #$03 / BCC ok
    LDA #$20 / STA tbl_char_action_timer,Y  ; room already holds >=3 -> WAIT ($20 ticks)
    ...
```

**Confirmed model + new findings:**
- Per-character **action timer** `tbl_char_action_timer ($64EE,Y)` counts down
  each pump; at 0 the char acts and `resolve_char_move ($5156)` picks/executes
  the next room step, then reloads the timer (crew at `tbl_walk_ticks ($6586)`,
  Alien via `alien_choose_move`/`alien_tick` — mostly `60` per surface move
  (`$8A4A`), `40` to enter a duct; `alien_ai`'s own `var_alien_move_ticks
  ($6581) = 70` is a separate duct-to-duct timer, not the general reload —
  corrected D-038, 2026-07-24, see §8.10).
- **Destination-based movement:** each char has a *destination room*
  `tbl_char_dest ($64E6,Y)`; movement steps toward it (not one-room-at-a-time
  orders as the remake models — a char is given a destination and walks there).
- **★ Room capacity limit = 3** (new mechanic, not in the remake): if ≥3 other
  characters already occupy the destination room, the char **waits** (`timer =
  $20`) instead of entering. Filed for the remake (see todo.md).
- `var_current_char ($64FB)` = the character currently being watched/controlled
  (its sprite marker + heartbeat) — matches the remake's "selected crew".

### `resolve_char_move` ($5156) 🟡 partial — a per-character state machine

Steps one character toward its destination, gated by several per-char state
bytes (indexed by char, Y):

- `tbl_char_state2 ($64C4,Y)` — a busy/retry latch (set to 2 while acting).
- `tbl_char_state3 ($6571,Y)` / `tbl_char_morale_or_pcs ($7D55,Y)` — a
  per-character **state-of-mind** value. Live: `$6571` and `$7D55` read
  **identical for the crew** (both `[4,4,3,4,3,4,3]`). The only writer of
  `$6571` is `order_gate_update ($4843)` (from `$7D55`+`$4781`); only decrement
  `$4238`. **⚠ CORRECTION (from the user's before/after order capture,
  `the live captures (not published)pcs_{before,after}.bin`):** an earlier turn read the
  `LDA $6571,Y / CMP #$02 / BCC + / JMP $7244` in `resolve_char_move` as
  "≥2 aborts the move (obedience gate)" — **that was wrong.** `$7244` is the
  *normal return into `char_pump`*, not an abort. In the capture **Dallas
  (slot 1) moved CommdCentr(6)→Corridor#1(8) with `$6571[1] = $7D55[1] = 4`
  unchanged** — so a state-of-mind of 4 does **not** block obedience; crew obey
  fine. `$7D55` is **not** written by an order either (unchanged before→after).
  So `$6571`/`$7D55` is a real per-char state-of-mind (the PCS input), but its
  effect is **softer than a hard movement gate** (likely obey-probability or
  response-delay); its exact role is still `[?]`. **Do not model a hard morale
  block on movement in the remake.** **What worsens it (static, `$729C` in
  `char_pump`):** while a character is **in a duct** (`$6501,Y` set),
  `LDA $7D55,Y / ADC #$01 / STA $7D55,Y` — **state-of-mind gets worse by 1 each
  tick spent crawling the vents** (a real PCS stressor for the remake).
  **The full PCS stressor set (user-confirmed):** `$7D55` rises when a crew
  member is **attacked by the Alien**, **finds a dead crew member**, is
  **crowded with other crew in one room**, or is **in the ducts** (the code
  path here). The morale word (CONFIDENT…BROKEN) shifts accordingly. `$7D55`
  is read in 11 places. The candidate "obey decision" readers (`$52C7`/`$5324`/
  `$5B69`) turn out to test **`$7D55 == 0` vs nonzero**, not magnitude — they
  process *disturbed* characters (e.g. `$52C7` flashes the background `$D021`
  for a char with `$7D55 != 0` in a given room). So **`$7D55` reads as a
  per-character fear/disturbance flag** (0 = calm; rises in ducts and, presumably,
  near the Alien), *not* a graded morale-index obey-gate. It still feeds
  `$6571` via `$4843` and shows as the CONFIDENT…BROKEN word, but there is **no
  simple "morale too low ⇒ refuse order" magnitude test** — the remake's
  compliance-vs-fear curve is an approximation the code doesn't literally have.
  Exact obey semantics remain `[?]` (soft/probabilistic at most).
- `tbl_char_state ($6501,Y)` — the "in duct / hidden" flag (0 = in a room).
- `tbl_char_pending ($650C,Y)` — a pending-action code (the `$8749` special path).
- `var_special_char ($64C3)` — a character singled out for special handling
  (branches to `$5265`).

A confirmed branch: it reads the char's current room `tbl_char_location
($7935,Y)`, indexes the **grille table** `tbl_room_grille ($8676,Y)`, and if the
room has **no grille** (only CORRIDOR 6) it *stops* the char (dest = current
room, `timer=$28`). So duct/grille state directly gates movement. The full
state machine (the `$64C4`/`$6571`/`$650C` transitions, the `$51DF`/`$51C2`/
`$5265` branches, and how a destination is chosen from an *order*) is
branch-heavy and needs **live single-stepping** to state precisely — deferred to
an oracle pass rather than over-read statically. `alien_tick ($8ACE)` /
`alien_ai ($8A74)` and the absolute loop rate (R-29, `vice_cycles_stopwatch`)
are the other next passes.

**★ New mechanic for the remake:** the room-capacity-3 wait (in `char_pump`)
plus the *destination-walk* movement model (a character is assigned a
destination room and walks there over several ticks, deferring when the room is
full) — the remake currently models one-room-per-order steps with no capacity
limit. See DISCOVERIES D-018 / todo.md.

### `alien_ai` ($8A74) + `alien_tick` ($8ACE) ✅ (static; matches the remake)

`alien_tick` is called first each `char_pump`. It decrements the Alien's timer
(`$64EE` slot 0) and, when it hits 0, resolves the finished move (`$5B56`) and
rolls the next action via `alien_ai`:

```
alien_ai ($8A74):
    LDY tbl_char_location ($7935)          ; Y = Alien's current room
    LDA tbl_room_grille ($8676),Y / BEQ noGrille
    ; room HAS a grille -> roll, rejecting 15 (so 0-14):
    JSR rng ($888F) / CMP #$0F / BNE + / (reroll)
noGrille:
    JSR rng ($888F)
    CMP #$0D / BCC compass                 ; roll 0-12 -> compass move
    ; roll >= 13 -> HIDE IN DUCT:
    LDX var_alien_reroll ($64B4) / BNE (reroll)   ; don't duct twice in a row
    LDA $7935 / STA tbl_char_dest ($64E6)  ; dest = current room (stay)
    LDA #$28 / STA $64EE                    ; duct timer = $28 (40 ticks)
    RTS
compass ($8A9E):
    CMP #$03 / BCS + ; roll <3  -> NORTH: LDA tbl_room_north ($80F5),Y
    CMP #$06 / BCS + ; roll <6  -> SOUTH: LDA tbl_room_south ($8117),Y
    CMP #$09 / BCS + ; roll <9  -> EAST:  LDA tbl_room_east  ($8139),Y
                     ; roll 9-12 -> WEST:  LDA tbl_room_west  ($815B),Y
apply ($8AA5):
    CLC / ADC #$80 / STA tbl_char_dest ($64E6)   ; dest = neighbour | $80
    LDA var_alien_move_ticks ($6581) [=70] / STA $64EE
    JMP alien_apply_move ($8C6B)
```

**CORRECTION (D-038, 2026-07-24 de-invention audit round 2) — the snippet
above is `alien_ai ($8A74)`'s own internal logic, not the Alien's main
per-action dispatcher.** `alien_ai` only runs while the Alien is *already*
in the duct network, deciding whether to keep moving duct-to-duct (via the
`$80F5`/`$8117`/`$8139`/`$815B` **duct-neighbor** tables shown above — these
are a compass N/S/E/W lookup for the duct graph specifically, not the
surface map) or re-emerge. The Alien's actual top-level dispatcher,
`alien_choose_move ($8A36)`, uses a **different** roll split (0-11 surface /
12-15 duct-entry, not 0-12/13-15) and a **different** set of tables (the
five 36-entry roll-band route tables `$7A3A`/`$7A5E`/`$7A82`/`$7AA5`/`$7AC8`,
already ported to the remake as `ALIEN_ROUTES`) for its surface moves — see
`docs/re/GAMEDATA.md` §1.5's correction note for the full byte trace. Below
was written against the wrong routine; kept for the record rather than
deleted, but do not trust its roll-threshold/table claims.

**Confirmed — the remake's `core/alien.py` is faithful (with one correction
below):**
- Uniform roll 0-15 (`rng $888F`); **0-12 = compass move** (0-2 N, 3-5 S, 6-8 E,
  **9-12 W** — a built-in west bias), **13+ = duct hide** (needs a grille).
  ✅ matches `ALIEN_DIR_BOUNDS`, `ALIEN_DUCT_THRESHOLD` **for `alien_ai`'s
  own in-duct roll** — `alien_choose_move`'s real surface-vs-duct split is
  0-11/12-15 (`ALIEN_DUCT_THRESHOLD = 12`, still correctly cited in
  `constants.py` since that constant WAS sourced from the right routine).
- ~~Compass move = `$6581` = **70** ticks~~ **CORRECTED: surface move =
  `$8A4A` = 60 ticks** (`$6581`=70 is `alien_ai`'s own duct-to-duct timer,
  a distinct, currently-unmodeled mechanic — D-038); duct-entry hide =
  `$28` = **40** ticks (this one was already right, `$89E0` in
  `alien_choose_move`, not the `$8A98`/`$28` shown in the snippet above
  which is `alien_ai`'s own separate 40-tick reload).
  ✅ `ALIEN_MOVE_TICKS` (60, corrected) / `ALIEN_DUCT_TICKS` (40, unchanged).
- **★ Cross-reference:** the destination is stored as `neighbour | $80` — bit 7
  = "in transit". This is exactly the `CMP #$80 / BCS` test in `char_pump`
  (`tbl_char_dest >= $80` ⇒ still moving). Crew destinations use the same
  encoding.
- Refinement `[?]`: the grille-present path rerolls a 15 (so 0-14) and
  `var_alien_reroll ($64B4)` blocks two ducts in a row — small odds tweaks the
  remake doesn't model. Sensing/hunting is **absent** here, confirming the
  remake's random-walk (not the old sensing model, already corrected).

## 8. Data tables

Fully decoded in **GAMEDATA.md** (room names/decks/neighbours/grilles, item
types/rooms, char locations, walk/alien-move ticks, status/morale words, RNG
table). All are named in `alien.sym`. Re-verify any against live memory with
`vice_memory_read <symbol>`.

## 8.5. Data regions — **do NOT disassemble as code**

The 6502 can't distinguish code from data, so `out/ALIEN.asm` renders every table
below as bogus instructions (e.g. `$5F59` "GAME SELECTION" → `SAX`/`SLO` junk).
Fence these off when reading/annotating. (Addresses are where ALIEN.prg loads,
`$2000+`.) Data-table *contents* are decoded in GAMEDATA.md.

**Graphics bank** (`$2000–$3FFF`): charset `$2000–$27FF` (256×8B glyphs), sprites
`$2800–$3FFF` (96×64B; portraits = slots 29–35 = ptrs `$BD–$C3`, alien anim
0–15, cat 22/36–40, person 24, egg `[?]`).

**Game data tables** (byte tables — look like text in the string scan):

| Addr | Table | Size |
|---|---|---|
| `$4EDC` | alien-anim frame table | 12 |
| `$5EC0` | portrait sprite X/Y | 14 |
| `$6571` | `tbl_char_state3` init (order gate) | 9+ |
| `$6586` | crew walk-ticks | 9 |
| `$7935` | char locations | 9 |
| `$7A3A` | Alien routing tables `[?]` | 5×36 |
| `$7D55` | char fear/state | 9+ |
| `$80D3` | room→deck | 34 |
| `$80F5/$8117/$8139/$815B` | room N/S/E/W neighbours | 34 each |
| `$8676` | room grille flags | 34 |
| `$82CF` | item type ids | 20 |
| `$82E3` | item start rooms | 20 |
| `$887E` | RNG output (identity 0–15) | 16 |
| `$A654` | play-screen char template | ~190 |
| `$7001` | play-screen colour template | ~180 |

**Text / message strings** (10-char records unless noted; `@`=space in scan):

- Front-end: `$5E4B` "WE LIVE AS WE DREAM", `$5E67` "JOSEPH CONRAD", `$5F59`
  "GAME SELECTION", `$5F70` "1 FULL GAME"/"CONTROL", `$5F87` "2 SHORT
  SCENARIO"/"PAUL CLANSEY ©1984 CONCEPT", `$443C` "DO YOU WANT AN
  INTRODUCTION"/"DECK PLAN KEY", `$6475` "PRESS ANY KEY".
- Names/labels: `$6012` crew (portrait order), `$A648` "CONTROL"/"ORDER",
  `$A665` crew (panel order), `$A6D4` "UPPER/MIDDLE/LOWER DECK", `$A71C`/`$A725`
  36 room names, `$7C72` 10 item names, `$7CEF` status (WOUNDED/COLLAPSED/DEAD)
  + morale (CONFIDENT…BROKEN) words, `$8080` NORTH/SOUTH/EAST/WEST/IN DUCT,
  `$A8A0` "DUCTING", `$829C` "ITEMS PRESENT/GET ITEM/LEAVE ITEM", `$A86E`
  "MOVE TO"/"QUIT"/"SHUTTLEBAY", `$A8E3` "SPECIAL", `$7EDB` "ALSO HERE",
  `$7A11` "DAMAGE 00% IS", `$4471` "LOCATION PTR", `$4493` "LADDER UP/DOWN"/
  "CHARACTER POSTN".
- **Gameplay events (reveal mechanics):** `$4108` "ALIEN WOUNDS"/"ALIEN GONE TO"/
  "ALIEN GONE THROUGH GRILLE", `$8BC2` "ALIEN ATTACKING"/"GRILLE BURSTS OPEN",
  `$8C76` "ATTACK", `$4BE0` "HITS ALIEN", `$50BF` "HAS BEEN KILLED BY THE ALIEN",
  `$59D5` "'S BODY IS HERE", `$451C` "THE TRACKER ALARM", `$453C` "SOMETHING
  MOVING BETWEEN LOCATIONS", `$8FED`/`$8D48` "HAS A READING"/"JONES IS UNEASY",
  `$44B4` "THIS IS THE SOUND OF THE HEARTBEAT OF", `$8830` "SEES JONES IS HERE"/
  "GET JONES", `$5C33` "GO GET JONES", `$665D` "CAT BOX", `$76F0` "LIFT".
- **Item consumables (R-24 confirmed):** `$4B23` "'S TRACKER IS SMASHED", `$4B58`
  "'S EXTINGUISHER IS EMPTY", `$4B95` "'S LASER IS EXAUSTED".
- **Special options (R-15):** `tbl_specials_menu ~$57A0` is a table of ten
  fixed-width 10-char labels: `NOSTROMO`, `BLOWLOCK.1`, `BLOWLOCK.2`,
  `SEALLOCK.1`, `SEALLOCK.2`, `ENTER HYPERSLEEP`, `BOARD NARCISSUS`, `LAUNCH
  NARCISSUS`, `OVERRIDE DETONATION`, `FIGHT FIRE`. `$5B7F` "MOTHER REFUSES
  LAUNCH", `$5DD1` "NARCISSUS", `$4500` "A GRILLE BEING REMOVED".
  **Dispatch located (D-028, 2026-07-11, FV-2j):** `specials_dispatch
  ($5839)` branches on `$64D0`, a small action-category code (not a direct
  1:1 index into the 10-entry menu table above). `$64D0` is itself derived
  in `guard_target_alive ($56B4)` from a **per-room lookup table
  `$5753,Y`** (Y = the *acting crew member's own current room*) — i.e.
  which category of special is available is determined by which room you're
  standing in when you invoke it, not by which menu label you clicked.
  `$5753` is populated at `new_game` from a static template at `$5776`
  (34-ish room entries, byte-verified). Known category codes so far:
  - **`1`** — room 6 (COMMDCENTR): `set_result_win`/`clear_result_flag` —
    the SCUTTLE NOSTROMO (arm) / OVERRIDE DETONATION (cancel) pair,
    live-confirmed FV-2c. Makes narrative sense (the bridge is where you'd
    arm ship self-destruct).
  - **`2`** — room 13 (CORRIDOR 6): `blowlock_sfx` -> `apply_blowlock` —
    BLOWLOCK; the specific side (.1 vs .2) is picked *inside* the handler by
    reading the panel cursor row (`$64E5 == $10`), not by a separate
    dispatch code. **D-037 (2026-07-24), applied to code:** `apply_blowlock
    ($5B04)` checks two independent per-airlock flags (`$5751`/`$5752`) and
    calls `blowlock_vent ($5A6A)` for each armed side, passing a *fixed*
    room id (`0` or `1` — AIRLOCK 1 / AIRLOCK 2) via `$5AD7`, never the
    acting crew member's own location. So CORRIDOR 6 is a **remote control
    panel** operating on both airlocks independently — the remake's
    `menu.py` previously gated this on standing *inside* an airlock (no
    citation, contradicted this very finding) and offered only one
    contextual option; corrected to gate on CORRIDOR 6 and offer both
    airlocks as independent `BLOWLOCK.1`/`BLOWLOCK.2` entries.
  - **`3`** — room 15 (CRYO VAULT): `guard_target_is_player ($5939)` — **this
    is ENTER HYPERSLEEP**, not what its pre-trace label suggests. Gated on
    `$64FB (acting crew) == $64C3 (a "target" register)` — i.e. self-target
    only — then sets a per-crew asleep flag (`STA $64D1,Y`) and moves the
    crew member's location to a sentinel (`STA $7935,Y = $95`), removing
    them from the room grid entirely. Applied to the remake: `menu.py` now
    gates the ENTER HYPERSLEEP entry on `crew.room_id == "cryo_vault"`;
    `sim.py`'s `_set_hypersleep` sets `room_id = None` on sleep, which for
    free makes the sleeper unreachable by every Alien-encounter check
    elsewhere (`crew.room_id == alien.room_id` can never match `None`).
  - **`4`** — `noop` (a literal `RTS`, no effect). **D-032 (2026-07-24)
    correction:** the full `$5776` static template was decoded (35 bytes,
    room-index space aligned to `ROOM_NAMES`) and **no room is ever assigned
    category 4**, nor does either of the other two `$5753` writers (below)
    ever write it. The earlier "very likely BOARD NARCISSUS" guess has no
    positive evidence behind it — downgraded to unconfirmed/possibly
    unreachable dead code in this build.
  - **`5`** — `show_mother_refuses` (`$5B95`, "MOTHER REFUSES LAUNCH…").
    **D-032:** the static template assigns category 5 to exactly **one**
    room — room 34 in `ROOM_NAMES`-space, i.e. **SHUTTLEBAY** — a strong,
    independent confirmation this is **LAUNCH NARCISSUS**'s launch-conditions
    check (exactly where you'd expect to invoke it).
  - **`6`** — reads the room's held item, checks item id 8-11 (the FIRE
    EXTNG id range) and does a charge-decrement + SFX: this is **FIGHT
    FIRE**. **D-032:** category 6 does **not** appear anywhere in the static
    `$5776` template — it is **dynamically installed**. `damage_room ($5581)`
    writes `LDA #$06 / STA $5753,X` when a room's damage accumulator
    (`$653F,X`) crosses a threshold, gated to rooms 17-19 in `ROOM_NAMES`-
    space only (`CPX #$11..$14`); the FIGHT FIRE handler itself clears it
    back to 0 (`STA $5753,X`/`$651C,X`/`$64D0` all zeroed at `$58CF`) once
    extinguished. So FIGHT FIRE is a **fire-alarm** special that only
    appears in the SPECIAL menu while one of those 3 rooms is actively
    burning, not a permanently-available option — a real mechanic the remake
    doesn't implement yet (filed as future scope, not attempted this pass).
  Still open: **SEALLOCK's exact mechanism** — an exhaustive scan of the
  full static template plus both dynamic writers found no 7th category
  anywhere, so the existing `special_options.py` model (SEALLOCK is the
  reverse action at BLOWLOCK's own category 2/room 13, side picked by the
  panel cursor row, not a separate category) is the best-supported
  explanation, though not independently proven; category 4's true purpose
  (if it has one at all); and full confirmation of `show_mother_refuses`'s
  and the FIGHT FIRE handler's exact bodies. **Full decoded room-category
  table (D-032), `ROOM_NAMES`-space, only nonzero entries shown:** room 6
  (COMMDCENTR) = 1, room 13 (CORRIDOR 6) = 2, room 15 (CRYO VAULT) = 3, room
  34 (SHUTTLEBAY) = 5 (static); rooms 17-19 = 6 while on fire (dynamic,
  cleared after extinguishing). All other 31 rooms are permanently 0 (no
  special offered there via this table at all — `specials_dispatch` RTSes
  immediately on category 0).
- **Self-destruct timer (R-27/R-28):** `txt_override_expiry ~$5544` "OVERRIDE
  OPTION EXPIRY __ MINS" and `txt_ship_destruct ~$5562` "SHIP WILL DESTRUCT IN __
  MINS" (DESTRUCT bytes at `$556C`, the two "MINS" fields at `$555E`/`$557A`) —
  the countdown printed when detonation is armed; the OVERRIDE DETONATION special
  cancels it. Countdown variable + tick still `[?]`.
- **Fire/damage system (R-27):** `$548D` "STRUCTURAL DAMAGE TO…" (+ the S-macke-
  style system-failure list), `$5950` "FIRE OUT".
- Endgame: `$6314` endings ("BRINGS THE NOSTROMO BACK TO EARTH", "THE NOSTROMO
  IS DESTROYED", …), `$63F8` "COMPETENCE RATING".

## 8.6 Fire / structural-damage system (R-27) — TRACED

The ship tracks physical damage **per room** and can be destroyed. Fully mapped
from `damage_room ($5581)` and its four callers.

**State (two parallel per-room tables, 20 entries, room index 0..$13):**
- `$653F,X` — **raw structural-damage accumulator** for room X. Sources add to
  it; thresholds on it drive everything else. (rooms are addressed internally as
  `location + $40`, held in `$457F` for the current damage event.)
- `$651C,X` — **damage stage, a one-way latch, NOT a pure function of the
  accumulator (D-035, 2026-07-24 correction)**: `0` intact → `1` damaged →
  `2` severe. `damage_room_b ($5587)` only bumps it (and only prints the
  warning / flashes red / plays the SFX) when the accumulator crosses the
  `4`-damage threshold **AND `$651C,X` is still `0`** (`$559E: LDA $651C,X /
  BNE +3(RTS)`) — i.e. it fires once per crossing, then goes quiet until
  something resets `$651C` back to `0`. The FIGHT FIRE special (below) is
  exactly that reset, and it does **not** touch `$653F` — so `$651C`
  decouples from the accumulator once acknowledged, and re-fires the next
  time `damage_room_b` runs while `$653F` is still `>=4` (which it always
  is, since the accumulator only ever grows).

**Damage sources (who calls `damage_room`):**
| Caller | Amount | Meaning |
|--------|--------|---------|
| `$8ED0` (`INC $653F,X`, X=`$7935` alien location) | **+1 / tick** | the **Alien passively corrodes/tears up whatever room it occupies** |
| `$4A95` (~~laser-fire path~~ **HARPOON GUN path**, corrected D-027 2026-07-11) | **+15** | **the harpoon hits the room hard too** — matches the user's Alien-acid intuition: shooting the creature wrecks the room, and the harpoon (its own guaranteed +5-to-Alien weapon, §8.8) is by far the messiest |
| `$4AFD` (any non-harpoon weapon: electric prod/incinerator/spanner/laser) | **+6** | smaller combat damage |
| `$5693` (`JSR $5587`) | via stage path | fire-spread / re-check |

**Which path fires (D-027, 2026-07-11):** traced `resolve_attack ($4940)`'s
item-id dispatch at `$49EB` — `CMP #$0C / BEQ $49F2` singles out item id 12
(the HARPOON GUN) into the `$4A73`→`$4A87` (+15) path; every other weapon
(electric prod 0-2, incinerator 3-5, spanner 18-19, laser 13-15 — none of
them id 12) falls through `$4AB1`→`$4AE7`→`$4AF0` (+6) instead. The earlier
"laser-fire path" label on `$4A95` in the table above was a guess made before
this was traced; it's the harpoon, not the laser. Applied to the remake in
`constants.ROOM_DAMAGE_PER_ATTACK_HARPOON` (FV-2.6, `sim.py`).

**Catastrophe → `hull_breach ($5D17)`:** before adding damage, each combat caller
checks the room's accumulator — `$4A8D CMP #$05` (+15 path) and `$4AF6 CMP #$0E`
(+6 path) — and if already past that threshold does `JMP $5D17` instead of adding
more; room `$14` also jumps straight to `$5D17`. `$5D17` is the hull-breach /
catastrophic-decompression handler (a lose trigger — see R-28). When a room is
destroyed the object table `$82E3,X` entries for that room are set to `$C8`
(removed).

**Remake implication:** model each room with a damage accumulator; the Alien
raises the accumulator of its current room every turn, and firing weapons at it
adds a large chunk. Crossing the threshold breaches the hull (lose). This is a
real original-game mechanic, *not* a manual invention.

**FIGHT FIRE and the extinguisher — RESOLVED, answers the old "fire vs acid,
same accumulator?" question (D-035, 2026-07-24), no live session needed.**
Read the category-6 specials handler (`$5889-$58E2`, §8.5) fully: it checks
item id 8-11 (FIRE EXTNG) is held, decrements its charge (`$4B37,X`), plays
an SFX, then does exactly three state writes — `STA $651C,X=0` (damage stage
reset to intact), `STA $5753,X=0` (removes the FIGHT FIRE special from the
menu), `STA $64D0=0` (clears the active dispatch code) — and prints "FIRE
OUT" (`$5950`). **`$653F,X`, the raw structural-damage accumulator, is never
read or written anywhere in this handler.** So: **"fire" and "acid/
structural damage" are the same single accumulator (`$653F`), not two** —
but **fighting the fire never reduces it.** FIGHT FIRE only resets the
one-way `$651C` latch above, which (a) clears the visible "damaged" warning
display and (b) — combined with `damage_room_b`'s "only re-warn if `$651C`
is back to `0`" gate — makes the FIGHT FIRE special **reappear** the next
time `damage_room_b` runs for that room, since `$653F` never went down and
so is still `>=4`. In other words: a room's real structural damage is
**permanent and cannot be undone** by the extinguisher; FIGHT FIRE is
ongoing maintenance against a recurring alarm, not a repair tool. This
directly means the remake's current `_use_extinguisher` (`sim.py`), which
**reduces `room_damage` by `EXTINGUISHER_REPAIR`**, models an invented
repair mechanic the ROM does not have. **Not yet applied to code** — a
correct fix needs a new per-room "alarm acknowledged" state decoupled from
the raw damage number (the remake currently derives `damage_stage()` as a
pure function of `room_damage`, with no persisted latch to reset), plus
wiring the FIGHT FIRE special itself (still unimplemented, D-032) with its
room 17-19 gate — a small feature, not a one-line constant fix, so filed
rather than rushed this pass. See `DISCOVERIES.md` D-035.

## 8.7 Endgame: hull breach, win/lose selection & Competence Rating (R-28) — TRACED

**Hull breach `$5D17` (a lose path).** Reached from the damage system (§8.6) when
a room is over-damaged. It: turns off sprites (`$D015`), runs a decompression
visual (clears colour RAM, fills the screen with `$A0`, cycles 6 colours ×5 via
`$5C42` using the `$5D11` colour table), **kills the crew** (writes to
`tbl_char_health $7D45`), sets result flags **`$64CF=1`** and **`$657B=1`**, then
`JMP $6412` — the endgame dispatcher.

**Endgame dispatcher `$6412`.** Blanks the screen (`clear_screen_fill $6426`,
fills `$A0`), sets background green, then calls **`select_outcome ($60A9)`** and
`$6598` to compose the result, resets the stack, prints a prompt (`$6475`→`$07D8`),
and **waits for a key** (`LDA $C5 / CMP #$40 / BEQ` = wait for keypress) before
`JSR $5DEB` (re-init back toward the menu, cf. `game_over_wait $6469`).

**Outcome selection `$60A9`** — the win/lose brain. It:
- resets the Competence score `$6411 = 0`;
- branches on the result flag `$64CF` and on the **survivor index `$64C3`**,
  drawing that character's name/status via `$62B6`/`$62EA`/`$62DC`;
- reads the **Alien's state in `tbl_char_health $7D45`** and its **location
  `$7935`** — a location of **`$22` means "ejected into space / off-ship"**
  (crew at `$22` are treated as safe: every crew-kill loop in the game excludes
  `CMP #$22`);
- selects one ending string and a preset Competence score, then loops crew 1..7
  killing any sharing the Alien's location.

**Ending strings (screen-code data, drawn to screen):**
| Addr | Text | Sense |
|------|------|-------|
| `$6372` | "THE ALIEN IS DEAD" | Alien destroyed |
| `$6383` | "THE ALIEN AND ITS EGGS ARE UNLEASHED UPON THE PLANET" | lose (Alien loose) |
| `$63BA` | "THE NARCISSUS RETURNS TO EARTH" | escape/win |
| `$6314` | "…BRINGS THE NOSTROMO BACK TO EARTH" / "THE NOSTROMO RETURNS TO EARTH" / "THE NOSTROMO IS DESTROYED" | Nostromo endings (destroyed = breach) |
| `$63F8` | "COMPETENCE RATING.  __%" | the numeric grade (`$6411`, via `compute_competence $6270`) |

**Full branch trace — RESOLVED BY STATIC TRACE (2026-07-24, FV-2.7, D-034),
no live session needed.** Read `$60A9`-`$627B` byte-by-byte, including
`compute_competence ($6270)` and the room-damage penalty loop just before it
(`$6231-$626E`), which together resolve the "5 vs `$78`, which is better"
question that stalled the previous pass.

Four distinct string/Competence-baseline combinations:
1. **`$7D45[0] >= 50`** (Alien killed by accumulated wounds) → "THE ALIEN IS
   DEAD" (`$6372`), Competence baseline **5**.
2. **`$7D45[0] < 50` AND `$64CF` (result flag) set AND `$7935[0] != $22`**
   (Alien *not* ejected — e.g. killed some other way, such as aboard a
   scuttled ship) → **also** "THE ALIEN IS DEAD", baseline **5**. This is
   the `$6103: BNE $60DF` cross-jump the previous pass flagged as
   "suspicious" — it is not a tracing error, it is deliberate: any ending
   where the Alien is confirmed gone (by wound-death *or* by any other
   means short of literally being ejected alive into space) shares the same
   "ALIEN IS DEAD" text and low baseline.
3. **`$7D45[0] < 50` AND `$64CF` set AND `$7935[0] == $22` AND `$64E3 !=
   0`** (Alien ejected off-ship alive, plus some second flag) → "THE
   NARCISSUS RETURNS TO EARTH" (`$63BA`, the clean escape), but falls
   through to the **same** baseline-`$78` (120) assignment as case 4 below —
   escaping does *not* get the low/good baseline.
4. **Everything else** (`$64CF` clear, or the ejected-Alien-plus-`$64E3`
   condition not met) → "ALIEN AND ITS EGGS UNLEASHED UPON THE PLANET"
   (`$6383`, the lose ending), baseline **120**.

**Why baseline 120 is not "better" than 5 — the real polarity (resolves the
old confusion):** after the per-survivor tally (`$614F`-`$6212`, `ADC #$04`
per surviving crew + a health bonus), `$621D: CMP #$65 (101) / BCC +3 / LDA
#$00 / STA $6411 / JMP $627B` — **if the running total is still >= 101, it is
clamped straight to 0 and the room-damage penalty loop is skipped
entirely.** Baseline 120 already exceeds 101 before any survivor bonus is
even added, so **both the lose ending and the clean NARCISSUS-escape win
display Competence 0%, unconditionally** — the loop can only ever push the
displayed value further from qualifying, never under 101, since it strictly
adds. Only the two "Alien confirmed dead" endings (baseline 5) can end up
under 101 and reach `compute_competence`'s real math: a further loop
(`$6231-$626E`, gated on `$64CF` being set) sums every room's structural
damage `$653F,Y` into a "mess" score `$640F` (with extra +10/+25 penalties
once a room's damage crosses 5 or 15, capped at 70), and `compute_competence`
computes `Competence = (70 - mess) + survivor_tally` — i.e. a genuine 0-100ish
percentage that rewards keeping the ship intact, but **only reachable at all
if the Alien is actually confirmed dead**; escaping without killing it is
scored identically to losing (a flat 0%). This is narratively coherent (the
Competence Rating measures how cleanly you neutralized the threat, not
whether you personally survived) and fully resolves FV-2.7's open question —
no live run was needed to determine the winning-string-to-flag-combination
mapping or the score polarity.
Filed against R-28 as resolved; not implemented in the remake (no
Competence-Rating mechanic exists in `src/` at all, so this is a pure
documentation/understanding win, no code change).

## 8.8 Combat & item-use resolution (R-24) — TRACED

> **CORRECTED 2026-07-11 (FV-1.1). `$4BEF` is NOT a roll — it is the item
> instance id, and combat has NO randomness.** The original text below read the
> `CMP #$06` at `$4976` as an RNG hit-roll; it is a comparison against the **item
> instance id (0-19)**. `$493D JSR find_room_object` returns the object in Y, and
> `resolve_attack` opens with `TYA / STA $4BEF` — so every later `LDA $4BEF / CMP`
> is a *switch on which item the crew member is using*. The `var_attack_roll`
> label in `alien.sym` is a misnomer (read it as `var_attack_item`). This mistake
> is what produced the remake's invented `ATTACK_HIT_CHANCE = 6/16` and its
> "lethal item subset"; both are corrected in FV-1.6.

`resolve_attack ($4940)` runs when a crew member attacks the Alien. It prints the
attacker's name + " HITS ALIEN" (`$4BE0`), then dispatches **deterministically on
the item instance id** in `$4BEF` (ids per `gamedata_snapshot.ITEMS`):

| id | item | effect |
|---|---|---|
| `$FF` | (none found) | abort (`$4943`) |
| `$11` (17) | CAT BOX | abort — cannot attack with it (`$4947`) |
| 0-5 (`< $06`) | ELCTRC PRD ×3, INCINERATR ×3 | `INC $7D45` → **+1** Alien damage |
| 6-7 | TRACKER ×2 | prints "TRACKER IS SMASHED" (`$4B22`, 21 ch) + `clear_object_at_loc2` (**destroyed on this use**), then **`JMP $497A`** — **CORRECTION (D-033, 2026-07-24): this DOES wound, +1**, same as prod/incinerator. An earlier pass at this table missed the trailing `JMP $497A` and wrote "no wound" — re-traced byte-by-byte and the jump target is unambiguous (`$497A: INC $7D45`, the same wound instruction every other +1 item uses). |
| 8-11 | FIRE EXTNG ×4 | charge path (`$49CD`): `LDA $4B37,X` → 0 prints "EXTINGUISHER IS EMPTY" (`$4B57`, 24 ch); else `DEC $4B37,X` |
| `$0C` (12) | HARPN GUN | `LDA $7D45 / CLC / ADC #$05` → **+5** Alien damage, **guaranteed, no roll** (`$49F2`) |
| 13-15 | LASER PIST ×3 | charge path (`$4AB1`): 0 prints "LASER EXAUSTED" (`$4B94`, 21 ch); else `DEC $4B37,X` then wound |
| `$10` (16) | NET | prints the net line (`$4B1E`), **no wound, but a real effect (D-033): `LDA $64EE / CLC / ADC #$50 / STA $64EE`** — adds **80 ticks to the Alien's own move timer** (entangles it, delaying its next move), then `clear_object_at_loc2` (**the net is used up/destroyed**, same as the tracker above). An earlier pass at this table only noted the message and missed the timer add + destruction. |
| 18-19 (`>= $12`) | SPANNER ×2 | `INC $7D45` → **+1** Alien damage |

Every wound path re-tests `CMP #$32` (50) → `JMP $6412` (endgame: Alien dead);
otherwise `INC $4B1D` (running hit count) and continue.

**Charges are per item INSTANCE, and `$4B47` is the master copy.** `new_game
($65B1)` runs `LDA $4B47,Y / STA $4B37,Y` for Y=0..19 (`CPY #$14`) in the *same*
loop that resets the item-room table (`$82F7`→`$82E3`, also 20 entries) — proving
`$4B37`/`$4B47` are indexed by the item instance id, not by weapon or by crew.
Decoded `$4B47`: ids 0-7 = 0, ids 8-11 = **3** (extinguishers), id 12 = **1**
(harpoon — one shot), ids 13-15 = **10** (lasers). Ids 16-19 read 4 bytes that
belong to the following message text (the copy over-runs the 16-byte table), but
those items' code paths never touch `$4B37`, so it is inert. Items whose charge is
0 are **not** "spent" — they are simply not charge-based (confirms + corrects
R-24).

**Polarity note (corrects §8.7):** `$7D45[0]` is the **Alien's accumulated
damage**, counting **up** — `INC` on each hit, **dead at 50**. That is exactly why
the endgame's `LDA $7D45 / CMP #$32` selects **"THE ALIEN IS DEAD"** (`$6372`) at
`≥50`. Indices `$7D45[1..7]` are **crew health**, counting the other way (see §8.9).

## 8.9 Crew state: health, fear & insanity (R-23) — TRACED

Two per-crew tables (indices 1..7), plus a status word shown at endgame.
- **`tbl_char_health $7D45,Y` — crew health.** `< 2` = incapacitated: every actor
  loop guards with `CMP #$02 / BCC skip` (e.g. `$52C0`, `$531D`) so a wounded crew
  member (health `< 2`) stops acting. Maps to the "WOUNDED"/"LOST" status strings.
- **`tbl_crew_fear $7D55,Y` — fear/nerves.** `0` = calm; **capped at 10**.
  `raise_crowd_fear ($4CE8)` walks the `tbl_crowd_group $4C3C` list (up to 3 crew
  sharing a room) and does `LDA $7D55,X … CMP #$0A / BCS skip / INC $7D55,X` — i.e.
  **crew crowded together get more nervous, up to 10** (matches the user's "some
  get nervous when they're all in a room"). Fear also rises when attacked / finding
  a corpse / in the ducts (other `INC $7D55,X` sites: `$4665`,`$466E`,`$4CF9`).
  Behaviour gate `$52C0`: a crew member with **fear > 0 AND health ≥ 2** in the
  relevant location triggers a panic branch (border flash `$D021`, `$64EE=2`),
  rather than obeying normally — fear degrades obedience but is **not** a hard
  gate (consistent with the earlier retraction of the "morale hard-gate" idea).
  **Sharpened (D-026, 2026-07-11, full static trace of `$5203`-`$52F6`):**
  this one-line summary understated it. `$52A4-$52E3` (the block this note
  originally described) additionally requires the **Alien to have taken
  damage `>=6`** (`$7D45[0] >= 6`) before it scans for a co-located,
  disturbed (`$7D55!=0`), healthy (`$7D45>=2`) *other* crew member — it's not
  simply "this crew member is scared and healthy," it's "the Alien is
  already wounded and some other healthy-but-shaken crew member is in the
  room." Separately, **two more, distinct triggers reach `char_wander
  ($5203)` directly**: (a) `$5252-$5260` — the crew member shares a room
  with the Alien (`$7935,Y == $7935[0]`) and isn't in a duct; (b) `$5265-
  $5291` — low health (`$7D45,Y < 4`) under a pending-action check. **And
  `char_wander` itself is not a bespoke "flee" routine** — it rolls the RNG
  and picks a destination from the **same 5 roll-banded route tables the
  Alien's own movement uses** (`$7A82`/`$7AA5`/`$7AC8`, identical thresholds
  to `ALIEN_ROUTES` in GAMEDATA.md/RW-6a): a panicking crew member takes an
  Alien-style random walk, not a directed escape. Not yet resolved: which of
  these paths takes priority when more than one condition applies, and the
  exact dispatch frequency (how often this whole check runs per game tick).
- **Status strings** (`tbl_status_strings $7CE8` / `$63E0`): "O.K.", "WOUNDED",
  "LOST", "IS INSANE", "SURVIVORS" — the per-crew end-of-game report. "IS INSANE"
  (`$63E8`) is the terminal fear state.

## 8.9b The Alien is NEVER shown on the map; the tracker is an ambiguous alarm (D-041) — TRACED

**This is a gameplay-defining mechanic the remake had inverted.** Two
long-standing routine labels turned out to be wrong, and correcting them
removes the remake's ability to see where the Alien is at all:

- **`$6667` was labelled `place_alien_sprite`. It is not the Alien's.** It
  `RTS`es immediately when the selected-character index `$64FB == 0` (the
  Alien's own array slot), computes its sprite pointer as `$64FB + $BC`
  (i.e. keyed to the *selected crew member*), and reads that crew member's
  duct flag `$6501,Y` into sprite colour `$D029`. It draws the **player's
  current character marker**, the "Location Ptr" of the deck-plan key.
- **`$595A` was labelled `check_tracker`. It is the corpse notice.** It
  renders a crew name (`$A65E` name table) + the `$59D4` string
  **"'S BODY IS HERE"**. Nothing tracker-related.

**No routine anywhere in the classified code draws the Alien on the deck
map.** What the ROM *does* have is a set of **audio cues**, spelled out in
the game's own instructions text (the `$443C` block, which doubles as the
deck-plan key and the sound legend):

| Addr | Sound-legend line |
|------|-------------------|
| `$44BC` | "This is the sound of the heartbeat of the current character." |
| `$44FC` | "…a grille being removed." |
| `$451C` | "…**the TRACKER alarm.**" |
| `$453C` | "…**SOMETHING moving between locations.**" |

Note the deliberate wording: **"SOMETHING"**, **"between locations"** — the
game names neither the entity nor a room. This independently corroborates
the user (who played the original): *the tracker only shows detected
movement, which could be the Alien, Jones the cat, or another crew member
moving.* So the Alien's position is learned by inference from ambiguous
audio, never read off the map — a substantially tenser game than the
remake's previous "red X / sprite always visible on the map" model.

**Applied to the remake:** the Alien's map marker was removed entirely
(`pygame_app._draw_deck`), `sim._use_tracker` now raises an ambiguous
`state.tracker_alarm` instead of recording the Alien's room, and the
`alien_reading_room` field was deleted. Guarded by
`test_alien_is_never_drawn_on_the_map` (renders two frames differing only
in the Alien's position and asserts the pixels are identical).
`[?]` still open: the tracker's real range, and whether the alarm is
momentary or latched — undecoded.

## 8.10 Alien AI: movement routing (R-25) — TRACED

**RNG.** `rng ($888F)` returns a pseudo-random **0–15**: it adds the jiffy-clock
low byte (`$A2`) to two rolling seeds (`$6519`/`$651A`), masks `#$0F`, and passes
that through a 16-byte scramble table `tbl_rng_scramble ($887E)`, storing the
result back as the next seed. Every AI/combat dispatch below branches on this roll.

**Alien state variables.**
- `var_alien_target $64E6` — the location the Alien is moving toward.
- `var_alien_move_timer $64EE` — frames until it arrives: **`$3C`(60)** normal
  wander, **`$28`(40)** duct travel, **`$14`(20)** when pursuing.
- `var_alien_pursuit $64B4` — hunt lock; when set the Alien uses the fast,
  directed path and re-locks on its target (`$89F7`…`JMP $89C4`). **Set at
  `$4CB3`** (`LDA #$01 / STA $64A0 / STA $64B4`) **probabilistically and
  escalating**: an aggression accumulator `var_alien_aggression $4781` grows by
  `alien_damage/4` each pass (`LDA $7D45 / LSR / LSR / ADC $4781`), then
  `rng < $4781` → lock pursuit. So **the more wounded the Alien, the more likely
  it is to hunt** — a cornered creature gets deadlier (matches the film's
  escalation, and pairs with the acid-blood room damage of §8.6).
- current location = `$7935` (indexes every table below).

**`alien_choose_move ($8A36)`** — a **weighted random walk**. It rolls `rng`:
- roll **≥ $0C** → `alien_enter_duct ($89D7)`: target = current `+$80` (enter the
  duct at this room), timer `$28`, `JMP $8C6B`.
- roll **0–11** → pick one of **five surface route tables** by band
  (0–2 → `$7A3A`, 3–4 → `$7A5E`, 5–6 → `$7A82`, 7–8 → `$7AA5`, 9–11 → `$7AC8`).
  Each table is **34 entries indexed by current location**; the entry is the next
  location → `$64E6`, timer `$3C`. The five maps differ in "restlessness"
  (`route3/4` are near-identity = short local hops; `route0–2` scatter the Alien
  across the ship), so the roll biases how far it roams. **NB the five tables are
  NOT uniformly spaced — strides are 36/36/35/35** (`$7A3A→$7A5E→$7A82→$7AA5→
  `$7AC8`); a uniform-36 decode reads garbage from tables 3–4. The remake ports
  them (`alientools gamedata` → `ALIEN_ROUTES`, RW-6a). The duct test is
  `roll ≥ $0C` (12), i.e. `CMP #$0C / BCC`.

**Duct/grille mode (`$8A74`).** Gated by `tbl_grille_access $8676,Y` (per-room
`01`=has grille, `00`=none — only room `$0D` lacks one). Uses a parallel set of
four **duct route tables** `$80F5/$8117/$8139/$815B` (same band structure) with the
`+$80` duct-location offset applied to `$64E6`; timer from `$6581`.

**Remake model:** Alien picks a destination each decision tick by rolling 0–15;
≥12 sends it into the ducts, otherwise it follows one of five random surface route
maps keyed on its current room. A separate pursuit flag shortens the move timer and
directs it at a locked target. Ducts connect rooms except room `$0D`. Route tables
are pure data (dump in this section's commit; exported via `alientools gamedata`).

## 9. Routine catalog & remaining work

| Addr | Symbol | Purpose | Status |
|---|---|---|---|
| `$4000` | entry_sys16384 | init + jump to dispatch | ✅ |
| `$4DB8` | init_a_raster_irq | install raster IRQ | ✅ |
| `$8FFC` | init_b_music | SID player init | 🟡 |
| `$5DEB` | init_c | game init | ⬜ |
| `$4D08` | irq_handler | IRQ: raster/tick/music | ✅ |
| `$4EE8` | update_1 | Alien sprite animation (12 frames) | ✅ (static) |
| `$4F19–$4FCB` | update_2..4 | other sprites + sound | 🟡 |
| `$5ECE` | main_dispatch | selection screen | ✅ |
| `$5FC3` | — | screen setup helper | ⬜ |
| `$7013` | start_game | Ctrl+1/2 → build play screen → main loop | 🟡 |
| `$4304` | game_init_mode | Full/Short mode init | ⬜ |
| `$A654` | tbl_playscreen_template | play-screen screen-code template | ✅ (data) |
| `$719D` | main_loop | world loop | 🟡 |
| `$6483` | pause_check | STOP/pause | ⬜ |
| `$7216` | char_pump | per-char world update (timers, room-cap 3) | 🟡 |
| `$5156` | resolve_char_move | step a char toward its dest (grille-gated) | 🟡 partial |
| `$8ACE` | alien_tick | Alien action timer + arrive | ✅ (static) |
| `$8A74` | alien_ai | Alien move decision (roll → compass/duct) | ✅ (static) |
| `$8C6B` | alien_apply_move | apply the chosen Alien move | ⬜ |
| `$7A3A` | tbl_routing | Alien scripted routes | ⬜ (R-16/R-25) |
| `$888F` | rng | uniform 0–15 | ✅ (GAMEDATA) |
| `$9039` | title_music_player | title SID tune | 🟡 |
| `$5581` | damage_room | +stage on `$651C`, print STRUCTURAL DAMAGE, flash border, SFX | ✅ |
| `$653F` | var_room_damage | per-room raw damage accumulator (20 rooms) | ✅ (data) |
| `$5D17` | hull_breach | decompress FX → kill crew → flags `$64CF`/`$657B` → `$6412` | ✅ |
| `$6412` | endgame_dispatch | blank screen → select_outcome → prompt → wait key → re-init | ✅ |
| `$60A9` | select_outcome | pick ending string + Competence from flags/Alien state | 🟡 |
| `$41C4` | alien_attacks_crew | roll `$888F` → "ALIEN WOUNDS <crew>", `DEC $7D45,X` (crew health) | 🟡 |
| `$4940` | resolve_attack | crew hits Alien: **deterministic switch on item id `$4BEF`** (no roll) → `INC $7D45[0]` (+1) or harpoon `ADC #$05`; dead at 50; charge check `$4B37` | ✅ |
| `$4CE8` | raise_crowd_fear | crowded crew (`$4C3C` group) → `INC $7D55,X`, cap 10 | ✅ |
| `$888F` | rng | pseudo-random 0–15 (jiffy `$A2` + seeds `$6519/$651A`, table `$887E`) | ✅ |
| `$8A36` | alien_choose_move | roll → duct (≥12) or 1 of 5 surface route tables | ✅ |
| `$89D7` | alien_enter_duct | target = loc `+$80`, timer $28; + pursuit re-lock | ✅ |
| `$7A3A` | tbl_alien_route0..4 | 5 surface next-room maps (36 bytes each) | ✅ (data) |
| `$80F5` | tbl_alien_duct0..3 | 4 duct next-room maps; grille access `$8676` | ✅ (data) |
| `$7D55` | tbl_crew_fear | per-crew fear 0..10 (0=calm) | ✅ (data) |
| `$6270` | compute_competence | endgame score → 2 digits + "COMPETENCE RATING" | 🟡 |
| `$6314` | tbl_endings | ending message per outcome (drawn ~`$62CB`) | ✅ (data) |
| `$50A0` | show_death_msg | draws "<name> HAS BEEN KILLED BY THE ALIEN" | 🟡 |
| `$6469` | game_over_wait | wait-key → re-init → back to menu | ✅ (live) |
| `$443C` | — | "DO YOU WANT INSTRUCTIONS" | ⬜ (R-12) |
| — | — | oxygen/TOOH counter | ⬜ (R-22) |
| — | — | morale/PCS update | ⬜ (R-23) |
| — | — | order/menu-draw (CONTROL panel) | ⬜ (R-15/R-16) |
| — | — | item USE effects | ⬜ (R-17) |
| — | — | fire/damage system | ⬜ (R-27) |
| — | — | win/lose + competence rating | ⬜ (R-14/R-28) |

**Next passes** (tracked in todo.md `R-*`): step the main loop + char pump live
to confirm §7; watchpoint the oxygen and morale cells to locate R-22/R-23; trace
the CONTROL-panel order code to nail the "move to:" list (R-16); decode the
`$7A3A` routing dispatch (R-25).

## 10. Coverage: the full control-flow-classified disassembly

To satisfy "a fully understood disassembly before any Python," the whole image
is now classified by **recursive-descent tracing** (follow execution from every
known entry point, not a naive linear sweep) rather than guessed. The tracer
seeds from the SYS entry `$4000`, the IRQ handler, and every *code* label in
`alien.sym` (65 seeds), follows branches/JSR/JMP, and marks every reached byte.

**Byte census of the $2000–$C001 image (40,961 bytes):**

| Class | Bytes | Notes |
|-------|-------|-------|
| Graphics bank `$2000–$3FFF` | 8,192 | charset + sprites (data by definition) |
| **Reached as CODE** | **15,775** | 6,748 instructions, from 65 seeds |
| `$FF` work-RAM / padding | 4,930 | uninitialised buffers (e.g. `$6694+`, `$9605+`) |
| Unclassified (data tables + text + screen templates) | 12,064 | 373 spans, mostly already documented in §8.5–8.10 |

So the real executable payload is **~15.8 KB of code (≈57% of the non-graphics,
non-padding payload), and recursive descent reaches essentially all of it** — the
large "gaps" ($9605–$C001, $6694–$7013) are `$FF` work-RAM, and the code-like
score of the one remaining candidate span ($9FBF–$A94C) is the **CONTROL-panel
screen template** (`$A0` space-fill + the menu/crew-name text at `$A654`), not
missed code. No significant code is reachable only through indirect jumps that the
seed set misses.

**Artifact:** `docs/re/ALIEN.annotated.asm` (8,184 lines) — the clean listing:
traced addresses rendered as real 6502 instructions with `alien.sym` labels
applied (incl. resolved JMP/JSR/branch targets), and every non-code byte emitted
as `.byte` rows with an ASCII gloss (never mis-decoded as instructions). This is
the "data vs code" separation made total across the whole image.

**Reproducibility (done — RE-INFRA, DECISIONS D-020):** the tracer + classifier
are now first-class toolkit modules — `alientools.m6502.trace` (`trace_code`) and
`alientools.codemap` — wired to the **`codemap`** subcommand and covered by
`tests/test_codemap.py`. Regenerate the artifact + census with:

```
python -m alientools codemap --report                          # census only
python -m alientools codemap --out docs/re/ALIEN.annotated.asm  # full listing
```

Coverage needs no symbol file: the SYS entry `$4000` plus the IRQ handler
auto-discovered from the `$0314/$0315` vector-install code (2 seeds) reach all
6,748 instructions — identical to seeding every code label. `ALIEN.annotated.asm`
is therefore a **derived** artifact (extract → codemap), not a hand-made file.

### 10.1 FV-0 completeness proof (2026-07-11)

The FV faithfulness program (`todo.md` → "★ FV", DECISIONS D-023) requires the
disassembly be *proven* complete before the remake is audited against it.
"Classified" (§10) is not "complete": a recursive-descent trace can miss code
reached only through **computed flow** (`JMP ($nnnn)`, an RTS jump-table, a
self-modified JMP operand, or a routine copied to RAM and executed there) or
through a **second dynamic entry** (an NMI/BRK handler, or a re-pointed IRQ).
Each of those was checked directly against `ALIEN.prg` (scripted, reproducible;
see the FV-0 analysis). Findings:

- **FV-0.1 — census reconciles exactly.** `8192 gfx + 15775 code + 4930 $FF +
  12064 data = 40961` = the whole `$2000–$C001` image. No byte is unclassified.
- **FV-0.2 — no computed/indirect flow hides code.** In the 6,748 reached
  instructions there are **0** indirect `JMP ($nnnn)`, **0** PHA/PHA/RTS
  jump-table dispatch idioms, and **0** direct `JMP`/`JSR` whose in-range target
  is not already classified as code. Of the 705 absolute `JMP`/`JSR` targets,
  **702 are in-image (every one lands on traced code) and 3 are KERNAL (`$E000+`)
  — zero call into low RAM (`<$2000`) or any buffer**, so no routine is copied to
  RAM and called. The image installs **exactly one** interrupt vector (`STA
  $0314`/`$0315` at `$4DBB`/`$4DC0` → the `$4D08` handler, the trace's IRQ seed)
  and installs **no NMI (`$0318/9`) or BRK (`$0316/7`) handler**. So the only two
  dynamic entry points are `SYS $4000` and IRQ `$4D08` — precisely the two seeds.
  Re-seeding the trace with all 264 `alien.sym` labels adds only 225 "code" bytes
  across 55 tiny spans, and **every one is a `var_`/`tbl_`/`txt_` data label**
  being decoded from its middle (largest 72 B = `tbl_grille_access`); none
  cascades into a new routine. **The reached-code set is therefore closed under
  the game's own static control flow — no reachable code is missing.**
- **FV-0.3 — every data span is attributed.** The 373 unclassified spans sum to
  12064 B (= census `data`), and **none is a control-flow target** (proven by
  FV-0.2), so none is reachable as code. The largest — `$9FBF–$A94B` (2445 B),
  the one span whose byte statistics look code-like — contains
  `tbl_playscreen_template $A654` and is the **CONTROL / play-screen screen-code
  template**, not missed code. The rest resolve to documented categories:
  screen-code text (`txt_game_selection $5F59`, `tbl_room_names $A9C4/$A955`,
  endings `$6313`, prompts `$443C`, damage strings `$5473`), binary game tables
  (routing `$7A10`, room neighbours `$807F`, grille `$8676`, items/crew
  `$7C72`), the `$64A0–$656D` variable block, and sprite/colour tables. (Text
  reads as low-printable because it is stored as C64 screen codes, not ASCII.)

**Residual, and where it is tracked.** (a) A routine *copied into a `$FF` work-RAM
region at runtime and executed there* is the only code-hiding mechanism static
analysis cannot observe directly. FV-0.2 closes it by construction — there is no
call or jump that would ever reach such code (0 indirect `JMP`, 0 calls into low
RAM or into the `$FF`/data regions) — so this is **additive assurance, not a gap**;
it is filed as **FV-2.15** with the live oracle's other captures, to be confirmed
with an *execution-range checkpoint* over `$9605–$C001` / `$6694–$7013` (zero hits
= live proof; note those spans are buffers, so they legitimately fill with *data*
during play — only execution matters). (b) The still-`⬜` routines in §9/§11 need
their *behaviour* stepped, which is a question of **understanding, not
classification**; they are tracked by FV-0.5 and ticked off by FV-1/FV-2 as each
comes up. Neither residual affects the code-vs-data classification.

**FV-0 sign-off — 2026-07-11. VERDICT: the disassembly is COMPLETE.** The trace
reaches all code reachable from the program's only two entry points (`SYS $4000`
and IRQ `$4D08`); nothing is hidden behind computed flow, a copied routine, or a
second interrupt handler; and every one of the 40,961 bytes is classified and
attributed. This is the verified baseline the FV-1 remake audits build on.

## 11. Routine index — driving toward 100% coverage

The `codemap` trace finds **339 distinct routine entries** (JSR/JMP targets in
reached code). §9 catalogs the major ones; this table names the rest so every
entry has a label + a one-line purpose. Progress is tracked at the top; the
labels live in `alien.sym` (applied to `ALIEN.annotated.asm`).

**Coverage:** 339 routine entries = **149 callable subroutines (all named ✅)** +
190 internal `JMP` labels. Every subroutine has a symbol in `alien.sym` and a
one-line purpose below; the internal `JMP` targets live inside those routines.

### Shared utilities / helpers

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$561C` | delay_long | busy-wait (256 outer loops), border→black; timing pause |
| `$561E` | delay | busy-wait, X = duration (callers `LDX #$80`); border→black |
| `$7D65` | index_x10 | `A = A*10` (ASL×3 + 2×add) — index 10-byte records (names) |
| `$791C` | copy10_ptr | copy 10 bytes `($FB)`→`($FD)` (name record → screen) |
| `$7948` | set_room_screen_ptr | compute the screen pointer `$FB/$FC` for a room/loc |
| `$7928` | ptr_down_row | advance screen pointer `$FD/$FE` by +40 (one row) |
| `$7530` | fill10_via_fd | write a 10-byte field of `#$01` via `($FD)` |
| `$7720` | guard_alien_present | early-RTS if `$64FB` (alien target) is 0 |
| `$7D94` | health_band | map crew health `$7D45,Y` to a status band (3/4 thresholds) |
| `$7DC5` | fear_band | map fear `$6571/$7D55,Y` to a band (clamp ≥5) |

### Per-character turn / action

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$4784` | init_char_turn | reset per-turn vars (`$4780-$4783` incl. aggression), SFX, save current char |
| `$7244` | dispatch_char_action | if `$650C,Y` (pending special) set → `JMP sub_char_special` |
| `$72D2` | check_deferred_move | if `$64C4,Y`==2 → clear, `JMP resolve_char_move` |
| `$4BBD` | clear_char_action | clear `$650C,Y`; show "ATTACK" prompt when char == alien target |
| `$5203` | char_wander | crew idle/panic move: roll → `$7AC8` route → set target/timer → dispatch |
| `$45E7` | scripted_event_check | opening-scenario step machine (`$45B9` phase, `$45D3` table) |

### Alien turn / AI plumbing

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$89A9` | alien_ai_dispatch | entry: load loc/pursuit, `JSR $8EBD`, → `alien_ai ($8A74)` |
| `$83F0` | reset_alien_turn | clear `$64BD/BE/FB`, set `$64E4=$0F`, `$700A=1`, → `$7080` |

### Screen / status drawing

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$5705` | draw_status_row | copy five 10-byte fields `$5799`→`$069E` (a status line) |
| `$7FC0` | set_color_at_ptr | write colour `#$0E` to colour RAM under the screen pointer |
| `$749B` | set_room_field | load room attribute `$7000,Y` → `$64E4`, fill a 10-char field |

### Small guards / flag setters

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$8DE1` | return_true | `LDA #$01 / RTS` (constant-true helper) |
| `$56B4` | guard_target_alive | RTS-early if the alien target `$6501,Y` is set |
| `$5011` | set_flag_64ba | set `$64BA = 1` |

### Timing / state (notable — resolves R-23 delay `[?]`)

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$4042` | compute_action_delay | per-char action timer = base(`$4032[type]`) + `$402B[health]` + `$64EE` — **health lengthens a character's action delay** |
| `$4E16` | fear_alert | when fear `$6571,Y ≥ 4`, quicken the IRQ divider (`$4D02=$28`) + set `$64B5=$11` — **fear raises tempo/alertness** |
| `$5017` | stop_active_play | clear `$64BB` (**attack-sequence flag**, D-075); restore sprites 0-3; program SID voice/ADSR |

### Room objects (the `$82E3` per-room object table)

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$45BA` | find_room_object | scan `$82E3` (20) for an object at loc `Y+$A0` → index or `$FF` |
| `$4BA8` | remove_room_object | mark the object for room `$457F` removed (`$82E3←$C8`) |
| `$4BF0` | clear_object_at_loc2 | as above for `char_loc+$80+$20` |

### Screen fill / animation

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$753F` | set_color_ptr_row | point `$FD/$FE` into colour RAM at row `$64E5` |
| `$5C42` | animate_fill_row | fill a row with `$64DD`, ticking `anim_sound_tick` per byte (decompress FX) |
| `$5CEA` | anim_sound_tick | per-frame animation/SID tick (every 256th → `JSR $9277`) |
| `$7C1A` | set_screen_ptr_row | point `$FD/$FE` into screen RAM `$041E` at row `$64E5` |
| `$7F6F` | ptr_fb_to_fd | copy pointer `$FB/$FC` → `$FD/$FE` |
| `$7132` | init_menu_ptr | point `$FD/$FE` at the `$A000` CONTROL-panel template |
| `$5BE7` | clear_line_07c0 | fill screen line `$07C0` with `$A0` (spaces) |
| `$7FFE` | color_if_char | conditionally colour the cell under the pointer |
| `$8EEF` | damage_display_char | map room damage `$653F,X` to a display glyph |

### Names / co-location / neighbours

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$830B` | draw_item_name | copy the 10-byte item name (`$82CF[type]` → `$7C73+`) to screen |
| `$8D71` | resolve_char_display_loc | resolve a neighbour character's display location (`$7935`, alien `+$80`) |
| `$4581` | find_colocated_crew | find another crew member sharing loc, healthy (≥2), afraid — feeds crowd-fear |

### Input

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$8660` | wait_keypress_flash | flash the border and `read_input` until a key (`$71AF`) is pressed |
| `$88CC` | guard_6580 | RTS-early unless `$6580` is set |

### Sprite multiplexer (character sprites on the map)

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$9300` | place_char_sprite | set sprite ptr/X/Y (`$07F8`/`$D000`), enable MSB, seed `$9266` multiplex buffer |
| `$9349` | sprite_bitmask | single-bit mask for sprite index `$935F` |
| `$9360` | scan_sprite_row | walk the `$949E` slot map advancing the screen pointer |

### Room contents / item list panel

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$8330` | scan_room_objects | scan `$82E3` for objects at the current location → build `$82BF` list |
| `$8540` | draw_room_items | draw the room name + its item list (`draw_item_name` per entry), set `$64FC` |

### Encounter / co-location

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$8C49` | find_crew_with_alien | find a crew member sharing the Alien's room (healthy ≥2) |
| `$8C80` | reset_attack_state | clear `$64B6`/`$6562`/`$651B` encounter flags |
| `$8DE4` | return_false | `LDA #$00 / RTS` (constant-false helper) |

### Special commands & endgame effects (R-15)

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$5A6A` | blowlock_vent | vent a room to space (crew there → health 0, location `$BD`); the BLOWLOCK effect — NOT hypersleep (label corrected 2026-07-09) |
| `$5B04` | apply_blowlock | BLOWLOCK: vent airlock side(s) `$5751/$5752` via `blowlock_vent $5A6A` (crew/alien → space) |
| `$5B95` | launch_narcissus_check | LAUNCH: refuse ("MOTHER REFUSES LAUNCH" `$5B80`) unless every alive crew is at loc `$22`; then `check_mother_refuses $5B1F` requires Jones/cat box aboard ("GO GET JONES" `$5C33`) → else refuse; success → `$6412` endgame win |
| `$5904` | blowlock_sfx | airlock SID blip + toggle `$5751`, apply blowlock |
| `$58E3` | set_result_win | set endgame result flags `$64CF=1`, `$657B=9` |
| `$58F6` | clear_result_flag | clear `$64CF`; border→6 |
| `$595A` | ~~check_tracker~~ **draw_corpse_notice** | **MISLABEL CORRECTED (D-041, 2026-07-24):** nothing to do with the tracker. It renders a **crew name** (`index_x10` → the `$A65E` name table → screen `$0770`) followed by the `$59D4` string **"'S BODY IS HERE"** (`$0777`) — i.e. the corpse-discovery notice. `$6509` is the crew index to name, `$64DA`/`$64DB` cache "whose reading is already displayed" so it isn't redrawn every pass. **The tracker's real handler has never been located.** |
| `$5ADD` | alien_maybe_hide | wounded Alien (`rng < $7D45`) hides at `$BD`, set `$64D9` |

### Character relocation / attack resolution

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$5354` | alien_wound_crew | full "ALIEN WOUNDS <crew>": draw names, `DEC $7D45,X`, death at <2 |
| `$42AC` | relocate_object | move an object/body in the `$82E3` table to a new room |
| `$4B6F` | relocate_object_b | variant: remove/relocate object for a computed loc |
| `$599E` | stow_char | park character X at the off-ship pseudo-room `$BB` |
| `$59A7` | restore_stowed_char | restore the stowed `$64DC` char to the Alien's room |
| `$59E4` | reset_kill_and_fear | clear per-crew kill flags `$64A9`, decrement all fear `$7D55` |
| `$4292` | alien_death_effects | consequences when the Alien is nearly destroyed |

### Character panels / prompts

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$4698` | draw_char_status | draw a character's name + health/fear status panel |
| `$46D0` | draw_order_panel | draw the ORDER menu for the selected character |
| `$4730` | find_witness | find a crew member co-located with char `$6515` |
| `$48BA` | find_crew_at_target_loc | find crew at one of the special locs `$656E/6F/70` |
| `$423E` | guard_colocated | guard: RTS unless another crew shares the location |
| `$43E5` | prompt_and_wait | show the `$6475` prompt, wait for a key, blank it |

### SID sound effects

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$4DF0` | init_sid_and_clear | program SID voices/volume; blank a screen region |
| `$4E42` | sfx_blip_a | short SID voice-3 blip (freq `$01C0`) |
| `$4E5C` | sfx_blip_b | short SID voice-3 blip (freq `$50C0`) |

### Menu / misc

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$511C` | menu_option_dispatch | dispatch on menu option `$7569[$64F7]` |
| `$4FF1` | maybe_clear_64ba | clear `$64BA` when `$64BC` set |
| `$5939` | guard_target_is_player | RTS-early if the Alien target is the player char |
| `$594F` | noop | empty routine (`RTS`) |
| `$5587` | damage_room_b | `damage_room` entry that skips the `$6501` guard |
| `$55C9` | draw_damage_warning | draw "WARNING. STRUCTURAL DAMAGE TO <room>" + colour flash |

### Map / screen drawing (play + menus)

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$7080` | draw_map_enter_loop | stop active play, draw the deck map, `JMP main_loop` |
| `$73C8` | draw_deck_map | draw a deck-map screen (template → screen + colour) |
| `$73D0` | draw_deck_map_body | shared body of the deck-map draw |
| `$77C7` | draw_lift_screen | draw the LIFT (elevator) screen |
| `$7993` | paint_map_colors | set the deck map's per-row colours (`$DAxx/$DBxx`) |
| `$79C4` | draw_control_panel | draw the CONTROL panel (current char + order list) |
| `$79CD` | draw_control_panel_body | CONTROL-panel body (no loc recompute) |
| `$7D73` | draw_char_statusline | draw the character status line (O.K./WOUNDED) + scan room |
| `$7EE5` | clear_map_colors | zero the map colour-RAM area |
| `$84AE` | clear_map_area | blank the map display area (`$0446`, colour `$0E`) |
| `$6667` | ~~place_alien_sprite~~ **place_selected_char_sprite** | **MISLABEL CORRECTED (D-041, 2026-07-24):** it positions the sprite for the **currently-selected crew member** (`$64FB`), not the Alien. It `RTS`es immediately when `$64FB == 0` (the Alien's own slot), derives the sprite pointer as `$64FB + $BC`, and reads that *crew member's* duct flag (`$6501,Y`) into the sprite colour `$D029`. Its only caller (`$7794`, inside `guard_alien_present $7720` — itself misnamed, see below) is the CONTROL-panel refresh path. **No routine anywhere draws the Alien on the deck map.** |
| `$9528` | setup_cursor_sprite | set up the map cursor sprite (sprite 0) |
| `$7F0D` | render_message | render a text field with embedded control codes |

### Map navigation — compass neighbours / exits

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$7F78` | mark_exits | highlight the four compass exits of the current cell (`$6500` bit) |
| `$7FD0` | peek_up | move the screen ptr up one row and read the cell |
| `$7FDE` | peek_down | move down one row and read |
| `$7FEB` | peek_left | move left one and read |
| `$7FF5` | peek_right | move right one and read |

### Menus / items / commands

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$817D` | select_menu_template | pick the menu template ptr from `$7569[Y]` |
| `$86F0` | draw_grille_option | draw the grille-related order option (`$8676` gated) |
| `$8387` | draw_item_row2 | draw an item name on the second panel row |
| `$8395` | list_room_items | list the items present in the current room |
| `$84FB` | drop_item | place the held item (`$829B`) into the current room (`$82E3`) |
| `$7C3D` | update_item_sprite | update the selected item's sprite |
| `$8437` | route_command | route a command byte (≥`$10` → special at `$5839`) |
| `$8469` | guard_829a_ff | RTS-early when `$829A` == `$FF` |
| `$7E3C` | begin_item_scan | init the item-scan (guard if Alien present) |
| `$7ED7` | begin_item_scan_w | thin wrapper over `begin_item_scan` |
| `$7112` | init_ptr_menu2 | point `$FD/$FE` at the `$A21C` menu template |
| `$7122` | init_ptr_menu3 | point `$FD/$FE` at the `$A438` menu template |

### Character-turn selection

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$8DE7` | select_char_turn | select char `$7945` for its turn (`init_char_turn`) |
| `$8BE7` | find_crew_at_alien | find a healthy crew member at the Alien's room |
| `$8E32` | check_6562 | load the `$6562` encounter flag |
| `$8EBD` | guard_6562 | RTS-early unless `$6562` is set |

### Endgame ending draws (used by `select_outcome`)

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$62B6` | draw_ending_survivor | draw survivor name + the `$6314` Nostromo ending line |
| `$62DC` | draw_ending_lost | draw the "all lost" ending message (`$633C`) |
| `$62EA` | draw_ending_survivors | draw the survivors ending message (`$6359`) |
| `$5B1F` | check_mother_refuses | LAUNCH: test whether MOTHER refuses launch |
| `$5B95` | show_mother_refuses | draw "MOTHER REFUSES LAUNCH" (`$5B80`) |

### SID music / audio

| Addr | Symbol | Purpose |
|------|--------|---------|
| `$956B` | sid_init_voices | reset/init all three SID voices (control + ADSR) |
| `$91FF` | init_music_and_sprites | program SID note + set up the intro sprites/multiplex buffer |
| `$9277` | multiplex_sprites | the raster sprite multiplexer (`$9266` buffer → `$D000`) |
| `$917B` | sid_scale_freq | shift a 16-bit SID frequency by an octave divider |
| `$9556` | play_note_b | trigger a SID note (voice freqs + `sid_init_voices`) |

**Milestone: all 149 callable subroutines are now named and one-lined.** The
remaining ~60 `codemap` entries are internal `JMP` targets *inside* these
routines (branch destinations), not separate subroutines.
