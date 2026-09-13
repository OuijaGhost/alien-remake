# VICE capture checklist — things to settle against the running game

> **Status (2026-08-17): every item below has been answered, and the unticked
> boxes are stale.** This file is the live-capture *scratchpad* - it records what
> to watch and how. The answers went into `todo.md`'s FV-2 list, into
> `DISCOVERIES.md`, and into the code; nobody came back to tick the boxes here.
>
> Thirteen boxes are still empty and **not one of them is outstanding work**:
> most were settled by static trace rather than by a capture, which is why no
> capture session ever ticked them. `todo.md` FV-2 is the authoritative status,
> item by item, with the discovery that closed each one.
>
> Kept because the *instructions* are still good: if you need to re-derive one
> of these values against the running game, the watchpoints and the procedure
> below are what to use.

> **Task tracking now lives in `todo.md` → FV-2** (Faithfulness Verification
> Program). Those FV-2 boxes are the authoritative to-do list and cross-reference
> each item here; this file remains the **live-capture working notes** — the setup
> findings, the cell addresses, and the how-to. Update both: tick FV-2 in todo.md
> and record the captured value + method here.

Items here need the **live vice-mcp oracle** (an emulator harness (not published), DECISIONS D-019)
to resolve — they are calibration values or branch polarities that the static
disassembly leaves `[?]`. Reach active play, then watchpoint / step / read the
cells below. Tick a box when captured and fold the value into the code + registers.

## Live-setup findings (2026-07-09) — reaching active play

Driving the running game via the MCP surfaced the real mechanics of the boot:

- **The joystick is NOT the problem.** Control port 2 already has a joystick on
  the C64 (`joystick_ports: 2`); `vice_joystick_tap {port:2, fire:true}` injects
  into it and works (it advanced the title screen). No resource attach is needed
  (and `JoyPort2Device` isn't even an exposed resource in this MCP build — only
  `WarpMode/Speed/SidModel/...` are, via `vice_machine_config_set`).
- **WARP was the real cause of the "resets to menu" symptom.** With `WarpMode=0`
  the game runs live and STABLE — the front-end reaches the real CONTROL panel
  (DALLAS…BRETT, the three decks, the UPPER-DECK map) and the Alien roams
  (`$7935[0]` cycles) with no reset. Reliable entry: `reach_active_play.py`
  (warp *through* the slow front-end, then drop warp).
- **CORRECTION (user + code, 2026-07-09): the game is PLAYABLE from the start —
  `$64BB` was the wrong flag.** The user recalls: notice of the dead crew member,
  then you're put **straight into the game controlling the crew**, and *moving a
  character is what makes the Alien start*. The code agrees: the **main loop
  `$719D`** runs continuously from boot (`JSR $6483` input · `$7453` · `$7216`
  char_pump = crew/Alien movement · `$5684` · `$5A26`), so crew/Alien logic is
  live immediately. `$64BB` only gates the **IRQ sprite-animation** updates
  (`$4EE8` returns early when 0) and a special-case key check in `$6483` — NOT the
  core game logic. The live screenshot (`out/vice_shots/01_opening.png`) shows the
  real CONTROL panel + "…HAS BEEN KILLED BY THE ALIEN" — exactly the game's start.
  So there is **no "reach active play" blocker**; the earlier framing was wrong.
- **SUPERSEDED (2026-07-10, D-014): the joystick DOES work — the MCP's "port 1"
  is the C64's control port 2.** Injecting on MCP **port 1** visibly drives
  `$DC00` (CIA1 Port A = control port 2, the register this game polls); MCP
  "port 2" reaches nothing. Every conclusion in the note below was drawn while
  injecting on the dead port. Use `{"port": 1}` in all `vice_joystick_*` calls
  (`reach_active_play.py`/`drive_move_order.py` updated). A warp-free boot +
  port-1 taps now shows the CONTROL panel's colour-RAM highlights responding to
  input. Remaining input work: pin the **panel-cursor cell** (it is not
  `$64FB`) by diffing `$6400-$65FF` across a single down-tap, then script a
  full MOVE order and watch a crew slot in `$7935` change.
- **UPDATE (D-014, live): input confirmed working — FIRE cycles `$64FB`.** A
  fresh boot + port-1 taps: `FIRE` moved `$64FB` 0→16→8 and the panel highlights
  shifted, while the Alien hunted (`$7935[0]` 0→5→14) — proving orders reach the
  game. `$64FB` is the panel cursor/mode: `$7453` routes input to deck-nav when
  `$64FB==0` and to the crew-action handler **`$75D5`** otherwise. A blind
  fire/up/down sequence didn't make a crew walk. Partial trace of `$75D5`: a
  selected crew (`$64FB` 1-7) routes to the order menu `$7AEB`; items ≥8 are the
  deck/option entries (my blind FIRE hit option 16, not a crew). `$7440` is a
  **colour/attribute table (all 14 = panel light-blue), NOT the cursor→item
  map** — the exact item indexing didn't decode cleanly statically. **Next step
  is empirical, not static:** on a live boot, sweep `$64E5`/FIRE combinations and
  watch `$64FB` reach a value 1-7 (a crew), then open its order menu and watch a
  `$7935[1..7]` slot change. Costly at real-time boot (~3 min) — best done as a
  dedicated interactive session. With warp off the Alien kills undefended crew in
  ~1-2 min, so act promptly.
- **(superseded) earlier root-cause note, kept for history:** The input handler `$71B0` IS called every main loop (via
  `$7453`), so the game polls the joystick at `$DC00` — but `vice_joystick_set/
  tap` never reaches it: a direct read of `$DC00` returns `$7F` (idle) for every
  injected state, AND a direct `vice_memory_write $DC00` is overwritten by the
  CIA's joystick lines on the next read. The only settable machine resources are
  `WarpMode/Speed/SidModel/CIA1Model/CIA2Model` — **no joyport device resource is
  exposed** (`JoyPort2Device`/`JoyDevice2`/`Joystick2`/… all "Unknown resource"),
  so the injection can't be wired to `$DC00`. **Conclusion:** live joystick-driven
  capture is not possible with this MCP build as-is. Options: (a) drive the game
  by writing the game's own order cells directly (D-018: a MOVE writes `$64FB` +
  `$64E6,slot`), bypassing input — but must first get past the opening gate;
  (b) run a full GTK VICE with a **keyset joystick** mapped to keys the MCP can
  send via `vice_keyboard_*`; (c) accept the static-disassembly answers already
  obtained (e.g. the LAUNCH conditions, D-013) and leave pure calibration `[?]`.
- **(earlier) input is fully gated in the opening death-display.**
  In the boot state, NO input registers — keyboard space/return, joystick fire,
  and held directions all leave `$64BB=0`, `$64FB=0`, and the input-handler's
  result cell **`$71AF` stays 0**, i.e. the joystick reader `$71B0` is not being
  called. The "…HAS BEEN KILLED BY THE ALIEN" row persists indefinitely. So the
  game is genuinely spinning in the opening and consuming no input until it
  transitions. This is a real contradiction to resolve BEFORE any capture:
  the **code** reaches `$64BB=1` only via the Alien's first attack
  (`$8CF3`→`$8D1A`→`$4F90`), but the **user recalls** playing from the start with
  *their* move starting the Alien. Settle it with a focused static trace of the
  opening loop (`$7560` busy-wait? who calls `$71B0`? what clears the death row?)
  rather than more live input trial-and-error — every input approach tried
  (keyboard, joystick chord/tap/hold, PC-jump to `$7013`, mode write, Alien
  location nudge) fails to get past the death display.
- **Actual remaining task — drive the joystick navigation.** Input reads the
  port-2 joystick at `$DC00` (`$71B0`: `CMP #$7F` = idle). The MCP
  `vice_joystick_set/tap` uses `direction:"down"|"up"|...` (a string) + `fire`;
  the CONTROL-panel selection cursor is a **colour-RAM highlight** (not a char
  change), so confirm navigation by reading `$D800+` colour RAM, not `$0400`.
  Note a direct `vice_memory_read $DC00` returns a stale `$7F` (VICE merges the
  joystick at CPU-read time), so verify via the on-screen cursor / a crew member
  actually moving, not by reading `$DC00`.
- **(superseded) earlier note: "active play begins only when the Alien attacks"**
  — that was based on the wrong `$64BB` reading; kept below for history:
  - `begin_active_play ($4F90)` (sets `$64BB=1`) is reached **only** via
    `$8D1A`←`$8CF3`←the Alien attack sequence at `$8CD9` ("ATTACK" `$8C76` /
    "GRILLE BURSTS OPEN" `$8BC4`). So the opening is **not a timer** — it runs
    until the Alien reaches a living crew member and attacks, which starts play.
  - **`$4303` (game_mode) reading `0` during the opening was a red herring**: the
    selection loop (`$5F36`) has no timeout — it polls `$91` until `$FA` (Ctrl+1,
    mode=1) or `$F3` (Ctrl+2, mode=2), so reaching `start_game` means the mode
    *was* set; the game then resets `$4303` to 0 after consuming it (`$4320`/
    `$43E1`). Setting the mode directly / jumping PC to `$7013` is NOT needed and
    breaks the main loop (the Alien freezes).
- **Nudge attempt (2026-07-09):** wrote the Alien's location `$7935[0]` to a room
  holding living crew (room 6) with a short action timer. The Alien sat in the
  crew room for ~8 s but `$64BB` **still did not flip** — so co-location alone
  does not fire the opening attack. Note the opening crew already has one member
  pre-killed (`$7D45` shows a 0), i.e. the scenario death happened, yet play
  hasn't begun — so the opening→active handoff is gated by a step in the opening
  scenario (`$4304`/`$5049` setup and the `$6415` caller of the attack routine)
  that a raw location write doesn't satisfy.
- **Recommended next effort (its own focused pass):** trace the opening-scenario
  routines `$4304` (mode setup) and the `$6415`→`$8CD0` attack caller to find the
  exact cell/counter that gates the first attack, then set THAT (not just the
  location). Avoid PC-jumps (they freeze the main loop). This is a real research
  task, not a one-liner — the infrastructure (warp-off live boot, working port-2
  joystick, screen/memory reads) is all in place for it via
  `reach_active_play.py`.

## High value (change gameplay fidelity)

- [x] **CONTROL-panel navigation — SOLVED LIVE (2026-08-17, DISC-271).** The
      panel *is* joystick-driven. The old note below ("a DOWN tap moved no
      colour cell") was an artefact of the tap: the main loop samples once per
      pass, every ~127 ms = 7.6 frames, and the taps were 4 frames, so they fell
      between polls. A ~150 ms hold moves `$64E5` by exactly one row; fire on a
      crew row selects them (`$64FB`) and opens the order menu. Driver:
      `archive/vice-mcp/drive_panel.py`.
      **INDICATE LOCATION — DONE (DISC-272).** Opens the paged room list of
      DISC-238; picking a room sets `$64F7`, raises `$64BE`, switches the map to
      that room's deck, and **leaves the list open** (`$64FB` stays 16). The
      remake closed it; corrected.
  *(The original note follows, kept for its detail; its conclusion about the
  joystick is the one DISC-271 overturned.)*
  **CONTROL-panel navigation + INDICATE LOCATION flash (R-35, D-022).**
      Live-verified there is **no idle blink** and the `$E6` room markers are
      static (already rendered by the remake). Still open: how the *right panel*
      selection cursor is driven (a DOWN joystick tap on the play screen moved
      **no** colour cell — the joystick seems to move the character, not the
      menu; find the real panel-nav input, maybe a key or a mode toggle), and
      what the **"INDICATE LOCATION"** option does — drive it and watch whether a
      room marker flashes (the `$7453` white↔`$64E4` row repaint) and whether a
      **room name** (`$A71C`, indexed by `$64FB`) prints. Screenshot the flash.
- [x] **RW-8 — Alien start room — RESOLVED (D-014).** Two fresh live boots +
      the static table all read `$7935[0] == 0` → the Alien starts at **room 0 =
      AIRLOCK 1**. `spawn_alien` corrected (the CARGOPOD 2 reading was a
      misinterpretation). Also resolved from the same boots: the **opening death
      is RANDOM** in the full game (Lambert/Kane/Lambert across three boots —
      remake default flipped to RANDOM), and the six **alive** crew fill
      3×COMMDCENTR + 3×LIFE SUPPT in roster order (`assign_start_rooms`).
- [x] **Crew starting health — CONFIRMED LIVE (2026-08-17, DISC-270).** Read at
      game start: 6/5/4/5/4/6/5 in slot order, i.e. **per character**, matching
      the `$7D4D` template. (The "remake assumes 4" note was itself stale.)
- [~] **Fear stressor magnitudes — attack measured, crowding blocked
      (2026-08-17, DISC-270/DISC-279).** An Alien wound costs **-1**, and only
      when it leaves the victim on exactly 3 health. Crowding could not be
      measured: `$6571` never moved with six companions over 33 s, because
      `init_char_turn` writes it **when a character takes a turn** and an idle
      crew member never does. **Root cause found and FIXED (DISC-287):**
      `char_pump ($7226)` skips a character already at zero, so a turn happens
      only on the pass a countdown reaches zero; the remake was granting an idle
      character a turn every pass.
      *(original)* Watchpoint `$7D55,X`: how much does one
      crowding tick / one Alien attack / finding a corpse add? (remake uses +1/+3.)
- [~] **Alien wound per hit — CONFIRMED LIVE (2026-08-17, DISC-270).** Twelve
      captured wounds, every one exactly **-1** to a single victim. The same
      capture caught the composure hit being **gated on the new health being
      exactly 3** (`$4227 CMP #$03`), which the remake was not doing — fixed.
      **The `$32` death threshold is CONFIRMED (DISC-274):** `$60D8 LDA $7D45 /
      CMP #$32 / BCC` in `select_outcome`, awarding competence 5 — seen from
      both ends, with 05% on the ending screen. Still open: the roll fraction
      that lands a hit.
- [x] **Oxygen rate — CLOSED BY REMOVAL (D-062, 2026-08-01).** There is no
      oxygen system in the program: no counter, no drain, nothing to calibrate.
      The remake's invented one was deleted. `TICK_HZ` was settled separately
      and is now live-confirmed at 7.886 Hz (DISC-270).
- [~] **Room-damage rate — CONFIRMED LIVE (2026-08-17, DISC-270).** `$653F,X`
      moves by **+1**, and only when `$6563` is set — which `$8B13` raises only
      if the Alien's room equals its destination, i.e. it **stayed put**. Over
      90 s of surfaced time that was once. The Alien's action cadence measured
      **7.6 s**, confirming `ALIEN_MOVE_TICKS = 60` at `MAIN_LOOP_HZ = 7.886`
      (60/7.886 = 7.61). **The weapon-hit chunk is +6** (DISC-285): a landed laser
      ATTACK took the room from 0 to 6. Still open: the `$651C` breach stage.

## Win/lose polarity (R-28 remainder)

- [~] **Ending selection — half done (2026-08-17, DISC-274).** Two endings
      observed live: "NOSTROMO RETURNS TO EARTH / ALIEN AND ITS EGGS ARE
      UNLEASHED / ALL CREW LOST" at **00%**, and "NOSTROMO IS DESTROYED / ALIEN
      IS DEAD / ALL CREW LOST" at **05%**. A checkpoint on `$60A9` caught the
      branch structure: `$64CF` selects win vs loss, and the **win** side is
      then sub-divided by the **android** (`$64C3`) — his health against 2, and
      whether he is in room `$22` — choosing between `$62B6` and `$62EA`, with
      `$62DC` the loss printer. The **competence-5 preset** is confirmed.
      **A third ending is now observed (DISC-275)** - the Narcissus escape, with
      a SURVIVORS list that excludes the android, at 00% because the Alien was
      left alive. So the 5 preset is specifically the reward for killing it.
      **The android branch is closed (DISC-276):** all three of its cases were
      staged and all three print the *same* ending text, with the android left
      off the SURVIVORS list every time. `$62B6`/`$62EA` draw a character's
      name and status, not an ending. What moves the ending text is the Alien's
      fate and the ship's - 00% alive, 05% dead.
      *(original)* Force two real endings and read `$64CF`/`$64E3`/
      `$7D45[0]`/`$7935` at `select_outcome ($60A9)` to pin which flag combo maps
      to each of the six ending strings and to the two preset Competence scores
      (5 vs `$78`).
      > **Read them at the breakpoint, not off the ending screen (2026-08-17).**
      > Tried the easy way on a live "ALL CREW LOST" ending and the state was
      > already re-initialised behind it: locations and health back to the
      > `$793D`/`$7D4D` templates, `$64A8` back to 0. The cells still hold
      > *something* -- `$657B` read 9 on that loss, which would contradict the
      > static note that 9 is the win path's marker -- but nothing read after the
      > screen appears can be attributed to the ending. Set the checkpoint.
- [~] **Self-destruct timer — half answered (2026-08-17, DISC-271).** The
      countdown is `$657B` (units) and `$657C` (255-pass sub-counter), and
      **`$5A26 LDA $64CF / BNE / RTS` gates it**: nothing ticks unless `$64CF`
      is set, so that cell is the *armed* flag, and the flashing border during a
      countdown is `$5A2C` toggling `$D020` each pass. Un-armed, `$657B` rests
      at 9 and `$657C` at 255 — so **a reading of 9 proves nothing**.
      **Timed end to end (DISC-277):** ~32 s per unit (255 passes at 7.886 Hz),
      nine units plus a tenth wrap = about 5 min 23 s. The banner prints
      `$657B - 5` while the override is offered and `$657B` itself once it says
      DESTRUCT - and it switches to DESTRUCT at 5 while `$585E` still allows an
      override at exactly 5, so it warns one unit early. A "MIN" is ~32 s.
      Choosing SCUTTLE NOSTROMO from the panel completed as an order but left
      `$64CF` at 0. Still open: what reaches `set_result_win ($58E3)`, and
      whether OVERRIDE from the panel clears `$64CF`.
- [~] **Specials dispatch — three handlers exercised (2026-08-17).**
      **ENTER HYPERSLEEP** (DISC-278): vault-gated, sets `$64D1`, moves the
      sleeper to `$95`, blocks the launch. **LAUNCH NARCISSUS** (DISC-275): four
      conditions including MOTHER's container test, produces a win.
      **BLOWLOCK** (DISC-280): offered from **CORRIDOR 6**, never from inside an
      airlock, both locks as separate rows - D-037 confirmed live. FIGHT FIRE,
      SEALLOCK and OVERRIDE still untested.
      *(original)* Trace the handler for a chosen special from the
      `$57A0` menu (BLOWLOCK/SEALLOCK/HYPERSLEEP/BOARD+LAUNCH NARCISSUS/OVERRIDE
      DETONATION/FIGHT FIRE) to confirm each effect end-to-end.

## PCS / behaviour tuning

- [x] **Panic-wander — ANSWERED (2026-08-17, DISC-281).** A panicked crew
      member does **not** wander: composure 0 and composure 4 subjects both sat
      still for 40 s with no orders. What panic does is make them
      **unselectable** - a controlled A/B on one cell, 4 selectable and 0 not -
      which is the third selection gate after health < 2 and asleep. The
      companion escape did not help, because the companion term only reaches
      `$6571` on a turn (DISC-279), so an idle panicked character never gets it.
      **Fixed at the root (DISC-287)** - the remake no longer gives idle
      characters a turn, so it now agrees with the machine.
      *(original)* The remake now obeys every order (the invented
      obey/refuse gate was removed, A-005). The original DOES have a panic
      branch (`$52C0`: fear>0 & health≥2 → `char_wander $5203` via route table)
      — capture *when* it fires and what it interrupts, so the remake can add
      the real wander instead of a guessed one.
- [x] **LAUNCH NARCISSUS — FULLY CLOSED LIVE (2026-08-17, DISC-275).** Four
      conditions, all decoded and all exercised: the **Alien** must not be in
      `$22`; **nobody asleep** (`$64D1`); every living crew member aboard, the
      **android exempt** unless `$64CC`; and **MOTHER's own test** - the net or
      cat box must be *renamed* (Jones actually inside, which is what the catch's
      rename is for) **and** aboard or carried by someone aboard. Staging that
      produced the project's first win ending, survivor list and all.
      *(original)* **RESOLVED statically (D-013).** Requires
      every alive crew at loc `$22` (SHUTTLEBAY) **and** Jones caught/aboard
      ("MOTHER REFUSES LAUNCH" / "GO GET JONES"). Applied to the remake. Still
      worth a live confirm: the exact SHUTTLEBAY capacity (is it `ROOM_CAPACITY`
      3, or a special escape-pod limit?).
- [~] **ENTER HYPERSLEEP — mechanics CLOSED (2026-08-17, DISC-278).** Offered
      only in the CRYO VAULT. Sets the sleeper's `$64D1` flag, moves them to
      location `$95` (a pod, not the vault with a bit set), leaves health alone,
      and makes them unselectable via `$7720`. **It also blocks the Narcissus
      escape** - `$5B9E` refuses the launch while anyone is asleep. Still open:
      whether a sleeper is safe from the Alien, and whether all-asleep plus a
      dead Alien is a win.
      *(original)* **ENTER HYPERSLEEP real effect** (user hint: a win if the Alien is
      killed/jettisoned; maybe protects a sleeper if the Alien enters the room).
      Its handler wasn't definitively located statically (the `$5A6A` routine is
      the blowlock vent, not hypersleep). Reach play, USE ENTER HYPERSLEEP on a
      crew member, and watch: their location/state (moved to a pod? a flag set?),
      whether the Alien can then kill them, and whether all-crew-asleep +
      Alien-dead ends the game as a win.
- [x] **OVERRIDE DETONATION / self-destruct — CLOSED (2026-08-17, DISC-283).**
      SCUTTLE and OVERRIDE are **one panel row showing whichever is available**,
      both gated to **COMMDCENTR**. SCUTTLE there sets `$64CF = 1`, reloads
      `$657B` to 9 and starts the tick; OVERRIDE clears `$64CF` and **freezes**
      the counters where they stand rather than resetting them. The earlier
      failure (DISC-271) was firing SCUTTLE from CORRIDOR 1, where the row is
      listed but the handler declines silently. So SCUTTLE is what reaches
      `set_result_win ($58E3)`.
      *(original)* (user hint: destroy the ship +
      Alien while the crew escape on the Narcissus). `set_result_win ($58E3)`
      sets `$64CF=1`, `$657B=9` (distinct from hull-breach's `$657B=1`) — arm the
      detonation live and read the countdown variable, the OVERRIDE window
      (`$5544`/`$5562` "… MINS"), and which ending/Competence it yields.
> **Staging a scenario works; issuing a USE does not, yet (2026-08-17).**
> `vice_memory_write {"address": "$7D46", "data": [6]}` edits game variables
> live, and the program picks them up immediately: writing `$82E3+13 = 6` moved
> a laser pistol from the ARMOURY into COMMDCENTR and the next GET ITEM listed
> it. So the crew, the Alien's room and duct flag, healths and item placement
> can all be arranged, which is what the remaining checks need.
>
> **USE does issue** - correcting a note written earlier the same day. The
> tracker USE printed `HAS A READING` from the same row-9 fire, so the path
> works; what failed was the *laser* USE producing no damage over six attempts.
> Two ordinary explanations, neither ruled out: `resolve_attack ($4940)` rolls,
> so misses are expected, and the panel drifts - a stray fire put the driver in
> the INDICATE list, and by the end Kane had lost the laser and walked into the
> ducts through the grille he had removed.
>
> So the real requirement is a **stable harness**, not a new input discovery:
> assert the expected panel state before each fire and re-establish it when it
> drifts, rather than firing blind in a loop. With that, the same staging
> measures the landed fraction directly, which is the hit-odds check.
>
> Two things confirmed while trying: the Alien's accumulated damage `$7D45[0]`
> is **not polled** - writing 50 or 60 into it changes nothing until a hit
> lands, so the `$32` threshold is tested on the attack path only. And a crew
> member on 1 health cannot be selected at all (`$7720`, health < 2), which
> looks exactly like a broken harness.

- [~] **Item USE effects — the damage question is ANSWERED (2026-08-17,
      DISC-282).** The net was used with the Alien present and did **no
      damage**, matching `$4940`'s decode, and it did **not stop the Alien
      attacking** - Kane was wounded six seconds later. Its *entangle* could not
      be distinguished from the ordinary encounter hold by watching the room;
      that needs a watchpoint on the Alien's action timer at the instant of use.
      Item names read off the panel: 16 NET, 17 CAT BOX, 18/19 SPANNER.
      *(original)* **Item USE effects (R-17).** The remake models only the confirmed effects
      (weapons attack, tracker reading, extinguisher fights fire, cat box). Verify
      the rest against the running game so guesses can be replaced:
      - **net / electric prod / spanner / thermlance** — real USE effect? (remake
        currently treats them as a harmless attack swing — no invented "stun").
      - [x] **tracker precision — ANSWERED LIVE (2026-08-17, DISC-273).** The
        message is exactly `KANE       HAS A READING` and nothing else: no room,
        no direction, no distance. It read with the Alien ducted in room 11 and
        the user in room 6, so it crosses decks and the duct boundary. The
        remake already models it as a boolean alarm, so this confirms rather
        than corrects - and the "(remake shows the exact room)" note here was
        itself wrong.
      - **fire vs structural damage** — is the extinguisher's "fire" the same
        accumulator as the acid structural damage (`$653F`) or a separate system?
      - **consumable charges** — exact starting charges for laser / extinguisher /
        tracker (`$4B37`); remake guesses 5 / 4 / 8.

_Add to this list whenever a static pass leaves a value or branch unresolved._
