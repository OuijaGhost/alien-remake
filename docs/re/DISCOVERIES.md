# DISCOVERIES.md

Discovery log — facts uncovered about the system / deps / model /
environment that are *not themselves tasks*. Record the raw finding; if it
implies work, the **Action** line points to where that work was filed.

> **Numbering: use `DISC-nnn` for new entries.** The historical `D-nnn` form is
> overloaded — `docs/DECISIONS.md` numbered its own entries `D-001`…`D-022` in the
> identical format, and seven ids in this file name **two findings each**
> (`D-009`–`D-014`, from a second series begun 2026-07-09, plus `D-146`). Those
> fourteen entries each carry a **Disambiguation** note naming the other one.
>
> Settled 2026-08-08 (D-192/D-195): rather than rewrite ~260 existing citations
> by hand — 41 of them in shipped source, each a silent-failure risk — new
> entries are prefixed **`DISC-nnn`** here and **`DEC-nnn`** in `docs/DECISIONS.md`,
> so the collision cannot recur. **Existing `D-nnn` citations are resolved by
> subject, not by number**; the index below lists both candidates with dates.

## Index

192 entries, D-022 to DISC-195 in numeric order. **This file is searched,
not read** — it is the project's evidence register and by far its largest
document. The index exists so a reader can find the right entry without loading
8,500 lines: grep the table, then read only that entry.

Numbering starts at D-022 because the earlier findings were folded into
the project history before this register existed. A letter suffix (`D-080b`)
marks a follow-up that refined the entry it hangs off rather than a new finding.

| # | Date | Finding |
|---|---|---|
| [D-001](#d-001-the-manual-pdf-is-a-scanned-image-with-no-text-layer) | 2026-06-25 | The manual PDF is a scanned image with no text layer |
| [D-002](#d-002-the-real-nib-has-40-tracks-with-a-protected-tail-36-40) | 2026-06-26 | The real `.nib` has 40 tracks with a protected tail (36–40) |
| [D-003](#d-003-the-standard-dos-area-tracks-1-35-decodes-100-clean) | 2026-06-26 | The standard DOS area (tracks 1–35) decodes 100% clean |
| [D-004](#d-004-the-disk-holds-6-standard-cbm-dos-files-alien-is-the-main-prg) | 2026-06-26 | The disk holds 6 standard CBM-DOS files; `ALIEN` is the main PRG |
| [D-005](#d-005-the-boot-file-is-menu-load-032c-not-the-main-alien-prg) | 2026-06-26 | The boot file is `MENU` (load $032C), not the main `ALIEN` PRG |
| [D-006](#d-006-the-protection-is-an-over-format-no-sync-tail-36-40-not-killer-weak-density) | 2026-06-26 | The protection is an over-format no-sync tail (36–40), not killer/weak/density |
| [D-007](#d-007-this-is-an-unprotected-1985-green-valley-sharedata-re-release-alien-entry-is-4000) | 2026-06-26 | This is an unprotected 1985 Green Valley/ShareData re-release; ALIEN entry is $4000 |
| [D-008](#d-008-the-game-is-real-time-frame-driven-raster-irq-not-turn-based) | 2026-06-26 | The game is real-time (frame-driven raster IRQ), not turn-based |
| [D-009](#d-009-the-2000-3fff-vice-dumps-are-a-static-charset-bank-not-the-map) | 2026-07-01 | The `$2000–$3FFF` VICE dumps are a static charset bank, not the map |
| [D-009](#d-009-rooms-take-physical-structural-damage-shooting-the-alien-wrecks-the-room) | 2026-07-09 | Rooms take physical structural damage; shooting the Alien wrecks the room |
| [D-010](#d-010-sg-s-extracted-charset-is-byte-identical-to-the-game-s-live-memory) | 2026-07-02 | SG's extracted charset is byte-identical to the game's live memory |
| [D-010](#d-010-endgame-chain-hull-breach-dispatcher-outcome-select-location-22-into-space) | 2026-07-09 | Endgame chain: hull-breach → dispatcher → outcome select; location $22 = "into space" |
| [D-011](#d-011-the-crew-roster-order-flow-are-confirmed-by-the-game-s-control-panel) | 2026-07-02 | The crew roster + order flow are confirmed by the game's CONTROL panel |
| [D-011](#d-011-combat-weapon-charge-crew-state-model-health-fear-insane) | 2026-07-09 | Combat, weapon-charge & crew-state model (health/fear/insane) |
| [D-012](#d-012-awake-crew-s-bare-0-default-silently-decoupled-from-the-real-crew) | 2026-07-02 | `--awake-crew`'s bare `0` default silently decoupled from the real crew |
| [D-012](#d-012-alien-ai-is-a-weighted-random-walk-over-5-surface-4-duct-route-tables) | 2026-07-09 | Alien AI is a weighted random walk over 5 surface + 4 duct route tables |
| [D-013](#d-013-an-active-auto-spawned-alien-can-perturb-small-ship-pcs-movement-test-fixtures) | 2026-07-02 | An active auto-spawned Alien can perturb small-ship PCS/movement test fixtures |
| [D-013](#d-013-launch-narcissus-requires-all-alive-crew-aboard-jones-caught) | 2026-07-09 | LAUNCH NARCISSUS requires ALL alive crew aboard + Jones caught |
| [D-014](#d-014-the-installed-irq-handler-4d08-serves-two-interrupt-sources-60a8-switches-between-the-title-screen-music-player-and-the-real-time-gameplay-tick) | 2026-07-02 | The installed IRQ handler ($4D08) serves two interrupt sources; $60A8 switches between the title-screen music player and the real-time gameplay tick |
| [D-014](#d-014-live-boot-findings-random-opening-death-timed-title-mcp-port-swap) | 2026-07-10 | Live-boot findings: random opening death; timed title; MCP port swap |
| [D-015](#d-015-the-intro-tune-s-filter-character-sweeps-percussive-held-over-exactly-102-4s-then-wraps-pitch-keeps-drifting-past-that) | 2026-07-02 | The intro tune's filter character sweeps percussive→held over exactly 102.4s, then wraps; pitch keeps drifting past that |
| [D-016](#d-016-the-the-live-captures-not-published-0400-bin-vice-dumps-are-the-deck-map-screen-ram-and-decode-losslessly-through-the-sg-charset) | 2026-07-03 | The `the live captures (not published)*_0400.bin` VICE dumps ARE the deck-map screen RAM, and decode losslessly through the SG charset |
| [D-017](#d-017-alien-s-gameplay-model-is-stored-as-plain-data-tables-in-the-prg-and-they-contradict-several-remake-inventions) | 2026-07-03 | ALIEN's gameplay model is stored as plain data tables in the PRG, and they contradict several remake inventions |
| [D-018](#d-018-live-disassembly-vice-mcp-confirms-the-engine-core-and-corrects-the-portrait-layout) | 2026-07-08 | Live-disassembly (vice-mcp) confirms the engine core and corrects the portrait layout |
| [D-021](#d-021-dense-boot-capture-pins-the-exact-front-end-title-visuals-for-a-1-1-remake) | 2026-07-11 | Dense boot capture pins the exact front-end/title visuals for a 1:1 remake |
| [D-022](#d-022-the-deck-plan-room-identification-mechanic-upper-middle-lower-deck-is-a-blinking-row-cursor) | 2026-07-11 | The deck-plan room-identification mechanic (Upper/Middle/Lower Deck) is a blinking row-cursor |
| [D-024](#d-024-morale-word-selection-is-decoded-table-location-formula-and-why-passive-fear-testing-fails) | 2026-07-11 | Morale word selection is decoded: table location, formula, and why passive fear-testing fails |
| [D-025](#d-025-deck-value-mapping-confirmed-4-upper-5-middle-6-lower-active-play-is-a-pure-timeout-not-player-gated) | 2026-07-11 | Deck-value mapping confirmed (4=UPPER/5=MIDDLE/6=LOWER); active play is a pure timeout, not player-gated |
| [D-026](#d-026-panic-wander-char-wander-reuses-the-alien-s-own-route-tables-the-trigger-is-3-distinct-paths-not-one) | 2026-07-11 | Panic-wander (`char_wander`) reuses the Alien's own route tables; the trigger is 3 distinct paths, not one |
| [D-027](#d-027-room-damage-path-selector-is-the-harpoon-not-laser-fire-the-remake-was-missing-the-harder-hitting-path-entirely) | 2026-07-11 | Room-damage path selector is the harpoon, not "laser fire"; the remake was missing the harder-hitting path entirely |
| [D-028](#d-028-the-specials-dispatch-table-is-room-gated-per-crew-location-enter-hypersleep-is-a-mislabeled-routine-fully-resolved-and-fixed) | 2026-07-11 | The specials dispatch table is room-gated per-crew-location; ENTER HYPERSLEEP is a mislabeled routine, fully resolved and fixed |
| [D-029](#d-029-colour-ram-capture-shows-the-deck-map-field-is-uniformly-green-no-per-glyph-colour-exists-to-recover) | 2026-07-24 | Colour RAM capture shows the deck-map field is uniformly green, no per-glyph colour exists to recover |
| [D-030](#d-030-shuttlebay-has-no-special-escape-pod-capacity-it-uses-the-same-generic-room-capacity-3-as-every-other-room) | 2026-07-24 | SHUTTLEBAY has no special escape-pod capacity; it uses the same generic ROOM_CAPACITY=3 as every other room |
| [D-031](#d-031-fear-stressors-are-uniformly-flat-1-and-crowding-only-amplifies-existing-unease-never-spooks-a-calm-crew-member) | 2026-07-24 | Fear stressors are uniformly flat +1, and crowding only amplifies existing unease (never spooks a calm crew member) |
| [D-032](#d-032-the-specials-room-category-table-fully-decoded-category-6-fight-fire-is-dynamically-installed-by-room-damage-not-statically-assigned-seallock-likely-shares-blowlock-s-category) | 2026-07-24 | The specials room-category table fully decoded: category 6 (FIGHT FIRE) is dynamically installed by room damage, not statically assigned; SEALLOCK likely shares BLOWLOCK's category |
| [D-033](#d-033-use-and-attack-share-one-dispatcher-the-net-entangles-doesn-t-just-print-a-message-and-the-tracker-s-smash-does-wound) | 2026-07-24 | USE and ATTACK share one dispatcher; the net entangles (doesn't just print a message) and the tracker's "smash" does wound |
| [D-034](#d-034-ending-selection-fully-resolved-escaping-the-alien-scores-identically-to-losing-to-it-both-0-only-killing-it-can-score) | 2026-07-24 | Ending selection fully resolved: escaping the Alien scores identically to losing to it (both 0%); only killing it can score |
| [D-035](#d-035-fire-and-structural-damage-are-one-accumulator-but-the-extinguisher-never-repairs-it-the-remake-s-repair-mechanic-is-invented) | 2026-07-24 | Fire and structural damage are one accumulator, but the extinguisher never repairs it — the remake's repair mechanic is invented |
| [D-036](#d-036-de-invention-audit-jones-destination-choice-algorithm-is-unconfirmed-a-stale-tag-corrected) | 2026-07-24 | De-invention audit: Jones' destination-choice algorithm is unconfirmed; a stale [?] tag corrected |
| [D-037](#d-037-de-invention-audit-blowlock-seallock-were-gated-on-the-wrong-room-entirely) | 2026-07-24 | De-invention audit: BLOWLOCK/SEALLOCK were gated on the wrong room entirely |
| [D-038](#d-038-de-invention-audit-round-2-byte-level-citation-verification-alien-move-ticks-was-mislabeled-70-really-60-two-menu-band-colours-were-unsupported) | 2026-07-24 | De-invention audit round 2 (byte-level citation verification): ALIEN_MOVE_TICKS was mislabeled 70, really 60; two menu band colours were unsupported |
| [D-039](#d-039-r-01-the-game-s-ascii-screen-code-mapping-decoded-and-rendered-two-label-table-assumptions-period-digits-disproven-by-actually-looking-at-the-output) | 2026-07-24 | R-01: the game's ASCII->screen-code mapping decoded and rendered; two label-table assumptions (period, digits) disproven by actually looking at the output |
| [D-040](#d-040-r-05-the-alien-s-real-sprite-is-a-4-frame-pulse-cycle-single-colour-not-the-16-frame-multicolor-walk-cycle-the-roadmap-assumed) | 2026-07-24 | R-05: the Alien's real sprite is a 4-frame pulse cycle, single-colour, not the 16-frame multicolor walk-cycle the roadmap assumed |
| [D-041](#d-041-the-alien-is-never-shown-on-the-map-the-tracker-is-an-ambiguous-something-moving-alarm-two-mislabels-corrected-a-gameplay-defining-invention-removed) | 2026-07-24 | The Alien is never shown on the map; the tracker is an ambiguous "SOMETHING moving" alarm — two mislabels corrected, a gameplay-defining invention removed |
| [D-042](#d-042-r-37-unblocked-selecting-a-dead-asleep-crew-member-is-a-bounce-not-a-hidden-entry) | 2026-07-24 | R-37 unblocked: selecting a dead/asleep crew member is a *bounce*, not a hidden entry |
| [D-043](#d-043-fv-2-11-panic-wander-implemented-panic-has-its-own-route-band-mapping-and-the-tables-contain-deliberate-self-loops) | 2026-07-24 | FV-2.11 panic-wander implemented: panic has its OWN route-band mapping, and the tables contain deliberate self-loops |
| [D-044](#d-044-the-extinguisher-s-repair-invention-removed-structural-damage-is-permanent-the-extinguisher-only-silences-a-recurring-alarm) | 2026-07-24 | The extinguisher's "repair" invention removed: structural damage is permanent, the extinguisher only silences a recurring alarm |
| [D-045](#d-045-d-046-the-deck-plan-key-settles-what-the-map-shows-five-symbols-no-alien-and-no-cat-and-the-character-marker-has-a-real-heartbeat-pulse) | 2026-07-24 | /D-046 — The deck-plan key settles what the map shows: five symbols, no Alien and no cat; and the character marker has a real heartbeat pulse |
| [D-047](#d-047-alien-s-charset-is-entirely-cut-out-reverse-style-and-the-front-end-loader-screens-use-the-c64-rom-font-instead-r-01-regression-fixed-r-36-done) | 2026-07-24 | ALIEN's charset is entirely cut-out/reverse style, and the front-end loader screens use the C64 ROM font instead (R-01 regression fixed; R-36 done) |
| [D-048](#d-048-r-26-is-insane-implemented-and-a-genuine-polarity-conflict-in-7d55-found-but-deliberately-not-resolved) | 2026-07-24 | R-26 "IS INSANE" implemented; and a genuine POLARITY CONFLICT in `$7D55` found but deliberately not resolved |
| [D-049](#d-049-d-052-r-09-r-02-done-exact-portrait-table-the-paper-ink-model-a-true-vic-border-and-the-panel-s-real-wording) | 2026-07-24 | ..D-052 — R-09/R-02 done: exact portrait table, the paper/ink model, a true VIC border, and the panel's real wording |
| [D-053](#d-053-r-10-the-play-screen-carries-the-commanded-character-s-own-portrait-colour-coded-by-duct-state) | 2026-07-24 | R-10: the play screen carries the commanded character's own portrait, colour-coded by duct state |
| [D-054](#d-054-r-03-multicolor-sprite-decoding-r-18-real-joystick-input) | 2026-07-24 | R-03 multicolor sprite decoding + R-18 real joystick input |
| [D-055](#d-055-r-10-completed-crew-in-duct-state-modelled-without-touching-the-contested-morale-polarity) | 2026-07-24 | R-10 completed: crew in-duct state modelled without touching the contested morale polarity |
| [D-056](#d-056-d-057-fv-3-1-3-2-harnesses-built-and-they-immediately-caught-three-real-bugs-the-specials-label-table-decoded-exactly-closing-fv-2-10-s-last-question) | 2026-07-24 | /D-057 — FV-3.1/3.2 harnesses built, and they immediately caught three real bugs; the specials label table decoded exactly, closing FV-2.10's last question |
| [D-058](#d-058-r-08-solved-from-the-rom-instead-of-the-pixels-the-game-has-its-own-per-room-marker-position-tables) | 2026-07-24 | R-08 solved from the ROM instead of the pixels: the game has its own per-room marker-position tables |
| [D-059](#d-059-the-7d55-polarity-conflict-resolved-it-is-composure-high-good-and-the-remake-s-morale-word-was-inverted) | 2026-07-24 | The `$7D55` polarity conflict RESOLVED: it is composure (high = good), and the remake's morale word was inverted |
| [D-060](#d-060-d-061-the-auto-destruct-countdown-and-the-heartbeat-rate-both-fully-decoded-r-28b-r-19-r-21) | 2026-07-24 | /D-061 — The auto-destruct countdown and the heartbeat rate both fully decoded (R-28b, R-19/R-21) |
| [D-062](#d-062-there-is-no-oxygen-system-in-the-c64-game-fv-2-5-resolved-by-removal) | 2026-08-01 | There is **no oxygen system** in the C64 game (FV-2.5 resolved by removal) |
| [D-063](#d-063-r-29-resolved-the-main-loop-runs-at-7-886-hz-not-the-irq-s-6-67) | 2026-08-01 | R-29 resolved: the main loop runs at **7.886 Hz**, not the IRQ's 6.67 |
| [D-064](#d-064-the-welcome-screen-transcribed-off-the-running-disk-r-34-closed) | 2026-08-01 | The WELCOME screen transcribed off the running disk (R-34 closed) |
| [D-065](#d-065-the-loader-screens-now-use-the-real-c64-chargen-rom) | 2026-08-01 | The loader screens now use the **real C64 chargen ROM** |
| [D-066](#d-066-fight-fire-fully-traced-5889-it-is-a-separate-special) | 2026-08-01 | FIGHT FIRE fully traced (`$5889`); it IS a separate special |
| [D-067](#d-067-the-consumable-charge-system-re-derived-independently-already-correct) | 2026-08-01 | The consumable-charge system re-derived independently (already correct) |
| [D-068](#d-068-8a36-is-a-pure-weighted-random-route-selector-no-scripted-pursuit) | 2026-08-01 | `$8A36` is a pure weighted-random route selector (no scripted pursuit) |
| [D-069](#d-069-health-band-7d94-the-o-k-wounded-cut-is-an-absolute-4) | 2026-08-01 | `health_band` ($7D94): the O.K./WOUNDED cut is an ABSOLUTE 4 |
| [D-070](#d-070-the-competence-rating-formula-decoded-end-to-end) | 2026-08-01 | The COMPETENCE RATING formula, decoded end to end |
| [D-071](#d-071-r-19b-closed-plus-behaviour-notes-for-four-fv-0-5-routines) | 2026-08-01 | R-19b closed, plus behaviour notes for four FV-0.5 routines |
| [D-072](#d-072-the-systems-malfunction-system-decoded-fv-0-5-s-last-routine) | 2026-08-01 | The systems-malfunction system decoded (FV-0.5's last routine) |
| [D-073](#d-073-the-malfunction-trigger-found-5753-x-identified-two-breach-gates) | 2026-08-01 | The malfunction TRIGGER found; `$5753,X` identified; two breach gates |
| [D-074](#d-074-r-20-closed-objectively-the-intro-s-sid-stream-is-now-bit-exact) | 2026-08-01 | R-20 closed objectively: the intro's SID stream is now bit-exact |
| [D-075](#d-075-64bb-is-the-attack-sequence-flag-not-game-active) | 2026-08-01 | `$64BB` is the ATTACK-sequence flag, not "game active" |
| [D-076](#d-076-r-31-closed-an-automated-side-by-side-harness-13-13-passing) | 2026-08-01 | R-31 closed: an automated side-by-side harness, 13/13 passing |
| [D-077](#d-077-the-ending-is-composed-from-independent-axes-the-score-has-a-base) | 2026-08-01 | The ending is COMPOSED from independent axes; the score has a base |
| [D-078](#d-078-r-01-s-digits-located-they-are-at-b0-b9-not-30-39) | 2026-08-01 | R-01's digits located: they are at `$B0-$B9`, not `$30-$39` |
| [D-079](#d-079-the-instruction-pages-the-obvious-source-file-is-the-wrong-one) | 2026-08-01 | The instruction pages: the obvious source file is the wrong one |
| [D-080](#d-080-the-android-64c3-a-whole-mechanic-the-remake-never-had) | 2026-08-01 | ★ THE ANDROID (`$64C3`) — a whole mechanic the remake never had |
| [D-080b](#d-080b-the-android-silently-drops-your-orders-the-reported-symptom) | 2026-08-01 | The android **silently drops your orders** (the reported symptom) |
| [D-081](#d-081-the-opening-notice-prints-a-garbled-name-an-original-game-bug) | 2026-08-01 | ★ The opening notice prints a GARBLED name — an original-game bug |
| [D-082](#d-082-the-location-pointer-is-an-animated-4-frame-expanding-rectangle) | 2026-08-01 | The location pointer is an animated 4-frame expanding rectangle |
| [D-083](#d-083-the-duct-network-rooms-connect-directly-junctions-were-invented) | 2026-08-02 | The DUCT network: rooms connect directly; junctions were invented |
| [D-084](#d-084-r-36-closed-the-android-s-activated-path-and-the-64cc-gates) | 2026-08-02 | R-36 closed: the android's activated path, and the `$64CC` gates |
| [D-085](#d-085-r-38-closed-and-short-mode-is-a-fixed-scenario-fv-1-9-was-wrong) | 2026-08-02 | R-38 closed, and **SHORT mode is a fixed scenario** (FV-1.9 was wrong) |
| [D-086](#d-086-the-movement-topology-is-inverted-in-the-remake-and-d-083-was-half-wrong) | 2026-08-02 | ★ The movement topology is INVERTED in the remake (and D-083 was half wrong) |
| [D-087](#d-087-p-5-p-8-applied-ducts-wired-end-to-end-and-the-font-hole-closed) | 2026-08-02 | P-5..P-8 applied: ducts wired end to end, and the font hole closed |
| [D-088](#d-088-r-21-was-wrong-the-game-has-five-sound-effects-open-coded-as-direct-sid-stores) | 2026-08-02 | R-21 was wrong: the game has five sound effects, open-coded as direct SID stores |
| [D-089](#d-089-jones-s-running-animation-and-why-it-only-sometimes-plays) | 2026-08-02 | Jones's running animation, and why it only sometimes plays |
| [D-090](#d-090-the-attack-animation-is-a-five-sprite-composite-and-it-is-selection-gated) | 2026-08-02 | The attack animation is a five-sprite composite, and it is selection-gated |
| [D-091](#d-091-the-duct-system-has-its-own-map-drawn-from-one-of-three-templates) | 2026-08-02 | The duct system has its own map, drawn from one of three templates |
| [D-092](#d-092-the-duct-map-decoded-three-sheets-a-pipe-follower-and-room-18-as-the-hub) | 2026-08-02 | The duct map decoded: three sheets, a pipe-follower, and room 18 as the hub |
| [D-093](#d-093-the-game-documents-its-own-sound-effects-and-that-closes-the-tracker-ping) | 2026-08-02 | The game documents its own sound effects, and that closes the tracker ping |
| [D-094](#d-094-the-deck-plan-key-also-defines-three-map-glyphs-and-refines-d-092) | 2026-08-02 | The DECK PLAN KEY also defines three map glyphs (and refines D-092) |
| [D-095](#d-095-sweep-for-other-self-documenting-content-what-exists-and-what-does-not) | 2026-08-02 | Sweep for other self-documenting content: what exists and what does not |
| [D-096](#d-096-the-attacking-alien-is-a-six-sprite-composite-built-by-a-raster-multiplexer) | 2026-08-02 | The attacking Alien is a six-sprite composite built by a raster multiplexer |
| [D-097](#d-097-corridor-6-resolved-a-duct-you-can-travel-through-but-never-enter) | 2026-08-02 | CORRIDOR 6 resolved: a duct you can travel through but never enter |
| [D-098](#d-098-why-the-game-ended-by-itself-a-parked-alien-and-a-breach-gate-5-points-early) | 2026-08-02 | Why the game ended by itself: a parked Alien and a breach gate 5 points early |
| [D-099](#d-099-the-victim-and-android-are-drawn-from-fixed-pools-not-the-whole-crew) | 2026-08-02 | The victim and android are drawn from FIXED POOLS, not the whole crew |
| [D-100](#d-100-how-the-alien-really-moves-two-distributions-two-clocks-one-pass) | 2026-08-02 | How the Alien really moves: two distributions, two clocks, one pass |
| [D-101](#d-101-the-grille-is-a-destination-and-four-more-mechanics-decoded-with-it) | 2026-08-02 | The grille is a DESTINATION, and four more mechanics decoded with it |
| [D-102](#d-102-border-feedback-engine-fires-and-the-action-delay-that-punishes-wounds) | 2026-08-02 | Border feedback, engine fires, and the action delay that punishes wounds |
| [D-103](#d-103-is-anyone-still-in-play-is-far-stricter-than-is-anyone-alive) | 2026-08-02 | "Is anyone still in play?" is far stricter than "is anyone alive?" |
| [D-104](#d-104-the-green-valley-loading-screen-is-a-colour-ram-spiral-in-basic) | 2026-08-02 | The GREEN VALLEY loading screen is a colour-RAM spiral, in BASIC |
| [D-105](#d-105-p2-14-the-grille-sound-is-already-the-lower-one-and-the-memory-was-right) | 2026-08-02 | P2-14: the grille sound is already the lower one, and the memory was right |
| [D-106](#d-106-p2-15-the-intro-s-whole-timbre-hangs-on-one-constant-settled-live) | 2026-08-02 | P2-15: the intro's whole timbre hangs on one constant, settled live |
| [D-107](#d-107-p2-5-closed-the-panel-is-faithful-but-the-threshold-was-wrong) | 2026-08-02 | P2-5 closed: the panel is faithful, but the threshold was wrong |
| [D-108](#d-108-methodology-correction-sid-registers-are-write-only-so-do-not-read-them) | 2026-08-02 | Methodology correction: SID registers are WRITE-ONLY, so do not read them |
| [D-109](#d-109-p2-15-re-verified-through-vice-sid-get-state-the-conclusion-holds) | 2026-08-02 | P2-15 re-verified through `vice_sid_get_state`: the conclusion holds |
| [D-110](#d-110-play-report-3-the-attack-sequence-blanks-the-map-and-the-siren-loops) | 2026-08-02 | Play-report #3: the attack sequence blanks the map, and the siren loops |
| [D-111](#d-111-p3-9-diagnosed-and-my-p2-22-retraction-was-wrong) | 2026-08-02 | P3-9 diagnosed, and my P2-22 retraction was WRONG |
| [D-112](#d-112-p3-2-the-room-move-timer-was-18x-too-fast-and-the-base-was-never-6586) | 2026-08-02 | P3-2: the room-move timer was ~18x too fast, and the base was never `$6586` |
| [D-113](#d-113-a-strong-lead-on-p3-5-p3-6-indicate-selects-its-screen-from-7569-not-the-deck-table) | 2026-08-02 | A strong lead on P3-5/P3-6: INDICATE selects its screen from `$7569`, not the deck table |
| [D-114](#d-114-p3-1-solved-the-dead-crew-member-was-a-cursor-trap) | 2026-08-02 | P3-1 solved: the dead crew member was a CURSOR TRAP |
| [D-115](#d-115-p3-15-jones-ran-on-the-frame-clock-instead-of-the-irq-clock) | 2026-08-02 | P3-15: Jones ran on the frame clock instead of the IRQ clock |
| [D-116](#d-116-the-deck-table-was-never-a-deck-table-80d3-is-a-screen-address-byte) | 2026-08-02 | ★ The deck table was never a deck table: `$80D3` is a screen-address byte |
| [D-117](#d-117-p3-3-and-p3-13-a-latched-alarm-and-two-unmapped-glyphs) | 2026-08-02 | P3-3 and P3-13: a latched alarm and two unmapped glyphs |
| [D-118](#d-118-p3-8-and-p3-11-a-dead-quit-key-and-a-flash-at-the-wrong-rate) | 2026-08-02 | P3-8 and P3-11: a dead QUIT key and a flash at the wrong rate |
| [D-119](#d-119-p3-7-the-welcome-ring-is-the-loader-s-marquee-and-it-should-chase) | 2026-08-02 | P3-7: the WELCOME ring IS the loader's marquee, and it should chase |
| [D-120](#d-120-p3-9-p2-22-and-r-20-are-one-finding-the-filter-sweep-was-switched-off) | 2026-08-02 | ★ P3-9, P2-22 and R-20 are one finding: the filter sweep was switched off |
| [D-121](#d-121-p3-14-answered-the-deck-map-s-grilles-are-static-art-and-never-change) | 2026-08-02 | P3-14 answered: the deck map's grilles are static art, and never change |
| [D-122](#d-122-6586-is-not-a-walk-ticks-table-either-it-is-the-state-backup) | 2026-08-02 | `$6586` is not a walk-ticks table either: it is the state backup |
| [D-123](#d-123-the-room-name-table-has-a-2-record-gap-31-of-36-names-were-wrong) | 2026-08-02 | ★ The room-name table has a 2-record GAP: 31 of 36 names were wrong |
| [D-124](#d-124-p5-9-both-front-end-animations-were-frozen-by-a-counter-in-the-wrong-place) | 2026-08-02 | P5-9: both front-end animations were frozen by a counter in the wrong place |
| [D-125](#d-125-p5-6-solved-a-fixed-start-table-a-fourth-selection-gate-and-a-60x-cadence-error) | 2026-08-02 | ★ P5-6 solved: a fixed start table, a fourth selection gate, and a 60x cadence error |
| [D-126](#d-126-64cc-names-the-android-not-its-victim-and-the-unrevealed-android-never-attacks) | 2026-08-06 | ★ `$64CC` names the ANDROID, not its victim — and the unrevealed android never attacks |
| [D-127](#d-127-retracts-d-119-the-welcome-marquee-never-animated-the-ramp-is-an-off-by-one) | 2026-08-06 | ★ RETRACTS D-119: the WELCOME marquee never animated; the ramp is an off-by-one |
| [D-128](#d-128-the-attack-siren-stop-was-scoped-to-the-wrong-tick-not-to-the-wrong-signal) | 2026-08-06 | the attack siren stop was scoped to the wrong tick, not to the wrong signal |
| [D-129](#d-129-the-motion-tracker-arms-passively-use-was-never-the-gate) | 2026-08-06 | ★ the motion tracker arms passively; USE was never the gate |
| [D-130](#d-130-panic-wander-needed-both-a-composure-gate-and-a-per-character-cadence) | 2026-08-06 | ★ panic-wander needed both a composure gate and a per-character cadence |
| [D-131](#d-131-p6-6-answered-it-is-faithful-the-deck-view-was-never-meant-to-follow-crew) | 2026-08-06 | P6-6 ANSWERED: it IS faithful — the deck view was never meant to follow crew |
| [D-132](#d-132-the-attack-order-existed-fully-implemented-with-no-way-to-issue-it) | 2026-08-06 | the ATTACK order existed, fully implemented, with no way to issue it |
| [D-133](#d-133-p5-8-was-a-rendering-overflow-not-a-cursor-wrap-bug) | 2026-08-06 | P5-8 was a rendering overflow, not a cursor-wrap bug |
| [D-134](#d-134-p5-7-was-the-same-bug-as-p5-8-seen-from-the-other-end) | 2026-08-06 | P5-7 was the SAME bug as P5-8, seen from the other end |
| [D-135](#d-135-p5-5-answered-it-is-faithful-the-geometry-was-already-right) | 2026-08-06 | P5-5 ANSWERED: it IS faithful — the geometry was already right |
| [D-136](#d-136-the-narcissus-shuttlebay-door-was-never-invented-the-airlock-2-one-was) | 2026-08-06 | the NARCISSUS<->SHUTTLEBAY door was never invented; the AIRLOCK-2 one was |
| [D-137](#d-137-p5-1-answered-no-narcissus-cockpit-screen-exists) | 2026-08-06 | P5-1 ANSWERED: no NARCISSUS cockpit screen exists |
| [D-138](#d-138-p7-verify-p3-1-confirmed-fixed-through-the-real-input-pipeline) | 2026-08-06 | P7-VERIFY: P3-1 confirmed fixed through the real input pipeline |
| [D-139](#d-139-the-attack-composite-now-stops-on-deselect-not-just-on-the-next-blip) | 2026-08-06 | the attack composite now stops on deselect, not just on the next blip |
| [D-140](#d-140-the-green-valley-spiral-was-cut-off-by-a-frame-rate-tick-rate-mismatch) | 2026-08-06 | the GREEN VALLEY spiral was cut off by a frame-rate/tick-rate mismatch |
| [D-141](#d-141-d-140-s-fix-overcorrected-the-0-6s-buffer-was-itself-an-invention) | 2026-08-06 | D-140's fix overcorrected: the ~0.6s buffer was itself an invention |
| [D-142](#d-142-green-valley-s-real-duration-is-14s-not-2-3s-measured-live-both-earlier-guesses-were-far-off) | 2026-08-06 | ★ GREEN VALLEY's real duration is ~14s, not ~2-3s: measured live, both earlier guesses were far off |
| [D-143](#d-143-both-front-end-screens-build-up-in-stages-text-grows-from-the-centre-the-border-sweeps-in) | 2026-08-06 | ★ both front-end screens build up in stages: text grows from the centre, the border sweeps in |
| [D-144](#d-144-retracts-d-137-the-narcissus-cockpit-is-real-found-via-the-rom-s-own-branch-not-taken) | 2026-08-06 | ★ RETRACTS D-137: the NARCISSUS cockpit is real, found via the ROM's own branch-not-taken |
| [D-145](#d-145-five-play-report-fixes-from-the-player-s-own-recording-an-archived-capture) | 2026-08-06 | five play-report fixes from the player's own recording + an archived capture |
| [D-146](#d-146-the-narcissus-cockpit-background-decoded-from-the-real-screen) | 2026-08-06 | the NARCISSUS cockpit background, decoded from the real screen |
| [D-146](#d-146-p3-15-the-jones-run-loops-f0-is-a-stop-line-not-an-end) | 2026-08-06 | ★ P3-15: the Jones run LOOPS; `$F0` is a stop line, not an end |
| [D-147](#d-147-p5-1-the-narcissus-cockpit-captured-from-the-real-machine) | 2026-08-06 | ★ P5-1: the NARCISSUS cockpit, captured from the real machine |
| [D-148](#d-148-p5-3-the-siren-cannot-be-verified-against-this-oracle-vice-does-not-implement-osc3) | 2026-08-06 | P5-3: the siren cannot be verified against this oracle — VICE does not implement OSC3 |
| [D-149](#d-149-jones-is-here-is-a-real-on-screen-notice-and-get-jones-is-a-real-special-option) | 2026-08-06 | ★ "Jones is here" is a real on-screen notice — and "GET JONES" is a real Special Option |
| [D-150](#d-150-the-tracker-a-recomputed-latch-a-fixed-rate-pulse-and-a-real-detection-zone) | 2026-08-06 | ★ the tracker: a recomputed latch, a fixed-rate pulse, and a real detection zone |
| [D-151](#d-151-the-pcs-keeps-two-composure-values-the-remake-modelled-one) | 2026-08-06 | ★ the PCS keeps TWO composure values; the remake modelled one |
| [D-152](#d-152-the-android-audit-three-real-behaviour-gaps-one-from-citing-the-wrong-routine) | 2026-08-06 | ★ the android audit: three real behaviour gaps, one from citing the wrong routine |
| [D-153](#d-153-jones-catching-him-is-a-roll-the-net-works-too-and-the-launch-needs-the-container-aboard) | 2026-08-06 | ★ Jones: catching him is a ROLL, the NET works too, and the LAUNCH needs the container aboard |
| [D-154](#d-154-the-spanner-is-a-plain-1-melee-weapon-the-item-catalogue-verified-whole) | 2026-08-06 | the spanner is a plain +1 melee weapon; the item catalogue verified whole |
| [D-155](#d-155-the-airlocks-a-healthy-alien-ignores-them-and-the-vent-never-stops) | 2026-08-06 | ★ the airlocks: a healthy Alien ignores them, and the vent never stops |
| [D-156](#d-156-jones-s-destination-decoded-the-alien-s-route-tables-his-own-bands) | 2026-08-06 | ★ Jones's destination decoded: the Alien's route tables, his own bands |
| [D-157](#d-157-the-51f4-was-a-fall-through-a-broken-crew-member-always-wanders) | 2026-08-07 | the `$51F4` `[?]` was a fall-through: a broken crew member ALWAYS wanders |
| [D-158](#d-158-the-sweep-guard-alien-present-is-a-continuous-gate-and-row-24-has-two-notices) | 2026-08-07 | ★ the sweep: `guard_alien_present` is a CONTINUOUS gate, and row 24 has two notices |
| [D-159](#d-159-the-self-reference-rejection-is-64b4-gated-that-is-how-the-alien-lingers) | 2026-08-07 | ★ the self-reference rejection is `$64B4`-gated; that is how the Alien lingers |
| [D-160](#d-160-get-jones-is-a-real-panel-row-and-grabbing-at-him-spooks-him) | 2026-08-07 | ★ "GET JONES" is a real panel row, and grabbing at him spooks him |
| [D-161](#d-161-the-front-end-is-basic-and-q-quits-to-an-advert-screen-and-cold-resets) | 2026-08-07 | the front end is BASIC, and "Q" quits to an advert screen and cold-resets |
| [D-162](#d-162-the-clock-a-busy-wait-main-loop-no-real-time-anywhere-and-a-10-wrap-auto-destruct) | 2026-08-07 | ★ the clock: a busy-wait main loop, no real time anywhere, and a 10-wrap auto-destruct |
| [D-163](#d-163-five-pv-items-closed-against-the-prg-5753-is-the-special-option-table) | 2026-08-07 | ★ five PV items closed against the PRG; `$5753` is the special-option table |
| [D-164](#d-164-fires-end-to-end-a-damage-alarm-in-an-engine-room-and-the-critical-stage-that-makes-it-unfightable) | 2026-08-07 | ★ fires, end to end: a damage alarm in an engine room, and the critical stage that makes it unfightable |
| [D-165](#d-165-three-more-pv-items-a-false-alarm-the-6562-latch-and-a-cursor-delay-we-invented) | 2026-08-07 | three more PV items: a false alarm, the `$6562` latch, and a cursor delay we invented |
| [D-166](#d-166-the-character-turn-engine-enumerated-four-cells-one-pump-and-why-the-original-feels-ambiguous) | 2026-08-07 | ★ the character turn engine, enumerated: four cells, one pump, and why the original feels ambiguous |
| [D-167](#d-167-pv-33-solved-the-move-to-list-is-built-at-7917-and-the-routing-tables-had-a-35th-row-we-were-dropping) | 2026-08-07 | PV-33 solved: the MOVE TO list is built at `$7917`, and the routing tables had a 35th row we were dropping |
| [D-168](#d-168-pv-34-one-clock-one-pending-action) | 2026-08-07 | PV-34: one clock, one pending action |
| [D-169](#d-169-four-more-pv-items-and-two-of-them-were-only-ever-stale-notes) | 2026-08-07 | four more PV items, and two of them were only ever stale notes |
| [D-170](#d-170-re-triaging-the-live-items-two-thirds-of-them-were-static) | 2026-08-07 | re-triaging the [live] items: two thirds of them were static |
| [D-171](#d-171-pv-25-was-never-a-fidelity-question-every-sound-played-at-double-speed) | 2026-08-07 | PV-25 was never a fidelity question: every sound played at double speed |
| [D-172](#d-172-pv-26-the-title-card-is-25-seconds-not-5-and-there-is-a-whole-screen-we-never-modelled) | 2026-08-07 | PV-26: the title card is 25 seconds, not 5, and there is a whole screen we never modelled |
| [D-173](#d-173-pv-37-located-the-deck-plan-key-sound-legend-screen-and-the-key-s-real-glyphs) | 2026-08-07 | PV-37 located: the DECK PLAN KEY / SOUND LEGEND screen, and the key's real glyphs |
| [D-174](#d-174-pv-37-closed-4303-is-the-game-mode-and-the-introduction-is-a-y-n-prompt-in-short-only) | 2026-08-07 | PV-37 closed: `$4303` is the game MODE, and the introduction is a Y/N prompt in SHORT only |
| [D-175](#d-175-the-q-quit-screen-built-one-step-dealer-and-three-ways-to-render-nothing) | 2026-08-07 | the Q/QUIT screen built: "ONE-STEP DEALER", and three ways to render nothing |
| [D-176](#d-176-pv-38-built-the-short-scenario-s-two-intro-screens-and-one-shared-slot) | 2026-08-07 | PV-38 built: the SHORT scenario's two intro screens, and one shared slot |
| [D-177](#d-177-pv-15-pv-24-the-alien-s-attack-is-doubly-random-and-fv-1-6-read-the-wrong-routine) | 2026-08-07 | PV-15/PV-24: the Alien's attack is doubly random, and FV-1.6 read the wrong routine |
| [D-178](#d-178-pv-08-09-10-11-14-closed-and-a-composure-mechanic-nobody-had-found) | 2026-08-07 | PV-08/09/10/11/14 closed, and a composure mechanic nobody had found |
| [D-179](#d-179-pv-06-18-23-29-30-35-five-closed-by-checking-one-closed-as-decided) | 2026-08-07 | PV-06/18/23/29/30/35: five closed by checking, one closed as decided |
| [D-180](#d-180-d-181-pv-28-pv-32-and-pv-39-the-last-static-items) | 2026-08-07 | /D-181 - PV-28, PV-32 and PV-39: the last static items |
| [D-182](#d-182-d-183-pv-32-pv-27-and-pv-01-closed-the-last-needs-an-oracle-items-did-not) | 2026-08-07 | /D-183 - PV-32, PV-27 and PV-01 closed: the last "needs an oracle" items did not |
| [D-184](#d-184-pv-36-closed-the-siren-never-needed-an-oscilloscope) | 2026-08-07 | PV-36 closed: the siren never needed an oscilloscope |
| [D-185](#d-185-two-bugs-in-my-own-exit-advert-screen-both-user-reported) | 2026-08-07 | two bugs in my own EXIT_ADVERT screen, both user-reported |
| [D-186](#d-186-the-blowlock-was-silent-a-cue-raised-then-cleared-before-anyone-drained-it) | 2026-08-07 | the blowlock was silent: a cue raised then cleared before anyone drained it |
| [D-187](#d-187-the-blowlock-fix-was-dead-code-the-real-path-is-menucontroller-fire) | 2026-08-07 | the blowlock fix was dead code; the real path is `MenuController.fire()` |
| [D-188](#d-188-the-alien-hit-and-ran-because-8ae1-is-a-jmp) | 2026-08-07 | the Alien hit and ran, because `$8AE1` is a JMP |
| [D-189](#d-189-the-four-worst-re-derivations-were-all-stale-prose-so-the-guard-is-now-a-test) | 2026-08-08 | the four worst re-derivations were all *stale prose*, so the guard is now a test |
| [D-190](#d-190-the-seam-harness-and-why-every-existing-fake-was-blind-to-the-same-thing) | 2026-08-08 | the seam harness, and why every existing fake was blind to the same thing |
| [D-191](#d-191-splitting-the-3-460-line-renderer-and-what-the-call-graph-revealed) | 2026-08-08 | splitting the 3,460-line renderer, and what the call graph revealed |
| [D-192](#d-192-the-d-nnn-namespace-is-overloaded-and-seven-ids-name-two-findings-each) | 2026-08-08 | the `D-nnn` namespace is overloaded, and seven ids name two findings each |
| [D-193](#d-193-the-fidelity-trackers-had-gone-stale-in-the-safe-direction) | 2026-08-08 | the fidelity trackers had gone stale in the safe direction |
| [D-194](#d-194-nothing-in-alien-prg-is-unused-and-p5-3-is-closed) | 2026-08-08 | nothing in `ALIEN.prg` is unused, and P5-3 is closed |
| [DISC-195](#disc-195-the-register-numbering-settled-and-the-first-entry-to-use-it) | 2026-08-08 | the register numbering, settled (and the first entry to use it) |
| [DISC-198](#disc-198-a-four-part-cleanup-sim-split-comment-rewrite-naming-audit-folder-archive) | 2026-08-08 | a four-part cleanup: sim split, comment rewrite, naming audit, folder archive |
| [DISC-199](#disc-199-the-game-cannot-currently-be-won-and-the-corrosion-gate-was-wrong) | 2026-08-08 | the game cannot currently be won, and the corrosion gate was wrong |
| [DISC-200](#disc-200-live-oracle-session-three-confirmations-and-one-strong-lead) | 2026-08-08 | live oracle session: three confirmations and one strong lead |
| [DISC-201](#disc-201-the-corrosion-model-is-in-the-prg-but-it-is-gated-four-ways-and-never-fires-in-normal-play) | 2026-08-08 | the corrosion model IS in the PRG, but it is gated four ways and never fires in normal play |
| [DISC-202](#disc-202-the-alien-s-damage-gates-corrosion-but-backwards-a-wounded-alien-corrodes-less) | 2026-08-08 | the Alien's damage gates corrosion, but backwards: a WOUNDED Alien corrodes LESS |
| [DISC-203](#disc-203-retracts-disc-201-the-corrosion-is-real-fast-and-i-measured-it-wrong) | 2026-08-08 | RETRACTS DISC-201: the corrosion is real, fast, and I measured it wrong |
| [DISC-204](#disc-204-solved-the-hull-breach-is-an-equality-and-that-is-why-the-game-was-unwinnable) | 2026-08-08 | SOLVED: the hull breach is an equality, and that is why the game was unwinnable |
| [DISC-205](#disc-205-all-four-corrosion-gates-traced-and-wired) | 2026-08-08 | all four corrosion gates, traced and wired |
| [DISC-206](#disc-206-three-player-reports-graphics-provenance-deck-follow-and-the-grille-overflow) | 2026-08-08 | three player reports: graphics provenance, deck-follow, and the grille overflow |
| [DISC-207](#disc-207-the-loader-s-basic-source-and-two-animations-rebuilt-from-it) | 2026-08-08 | the loader's BASIC source, and two animations rebuilt from it |
| [DISC-208](#disc-208-the-green-valley-name-white-a-row-higher-and-it-has-a-trademark) | 2026-08-08 | the Green Valley name: white, a row higher, and it has a trademark |
| [DISC-209](#disc-209-the-welcome-screen-s-build-order-decoded-from-menu1-prg) | 2026-08-08 | the WELCOME screen's build order, decoded from MENU1.prg |
| [DISC-210](#disc-210-the-welcome-reveal-implemented-and-a-colour-code-that-moves-a-whole-line) | 2026-08-08 | the WELCOME reveal implemented, and a colour code that moves a whole line |
| [DISC-211](#disc-211-the-box-grew-twice-and-a-speed-knob-that-does-not-corrupt-the-measurements) | 2026-08-08 | the box grew twice, and a speed knob that does not corrupt the measurements |
| [DISC-212](#disc-212-scuttle-nostromo-flashes-the-border-and-it-is-blue-xor-1) | 2026-08-08 | SCUTTLE NOSTROMO flashes the border, and it is blue XOR 1 |
| [DISC-213](#disc-213-the-panel-is-fixed-blocks-and-alien-s-font-puts-capitals-at-80) | 2026-08-08 | the panel is fixed blocks, and ALIEN's font puts capitals at $80+ |
| [DISC-214](#disc-214-retracts-d-131-the-view-does-follow-and-the-deck-table-was-the-wrong-table) | 2026-08-08 | RETRACTS D-131: the view does follow, and the deck table was the wrong table |
| [DISC-215](#disc-215-the-case-bit-and-two-letters-the-game-writes-in-at-runtime) | 2026-08-14 | the case bit, and two letters the game writes in at runtime |
| [DISC-216](#disc-216-the-deck-plans-were-captures-the-rom-has-carried-them-all-along) | 2026-08-14 | the deck plans were captures; the ROM has carried them all along |
| [DISC-217](#disc-217-the-status-template-is-42-bytes-and-both-its-fields-are-9-wide) | 2026-08-14 | the status template is 42 bytes, and both its fields are 9 wide |
| [DISC-218](#disc-218-the-notice-screen-was-laid-out-by-feel-menu1-gives-every-column) | 2026-08-14 | the notice screen was laid out by feel; MENU1 gives every column |
| [DISC-219](#disc-219-the-portrait-was-never-misplaced-two-captions-were-still-shouting) | 2026-08-14 | the portrait was never misplaced; two captions were still shouting |
| [DISC-220](#disc-220-the-opening-notice-s-colours-were-already-right-its-text-was-shouting) | 2026-08-14 | the opening notice's colours were already right; its text was shouting |
| [DISC-221](#disc-221-the-scuttle-flash-silently-disabled-the-fire-key-border-rainbow) | 2026-08-14 | the SCUTTLE flash silently disabled the fire-key border rainbow |
| [DISC-222](#disc-222-the-vice-launcher-has-been-running-with-warpmode-on-the-whole-time) | 2026-08-14 | the VICE launcher has been running with WarpMode on the whole time |
| [DISC-223](#disc-223-jones-s-movement-and-catch-odds-are-already-faithful-two-small-fixes) | 2026-08-14 | Jones's movement and catch odds are already faithful; two small fixes |
| [DISC-224](#disc-224-four-alien-opening-death-reports-one-real-bug-and-three-faithful-mechanics) | 2026-08-14 | four Alien/opening-death reports, one real bug and three faithful mechanics |
| [DISC-225](#disc-225-alien-s-cut-out-font-had-inverted-ink-paper-polarity-in-one-render-path) | 2026-08-14 | ALIEN's cut-out font had inverted ink/paper polarity in one render path |
| [DISC-226](#disc-226-every-sound-cue-played-twice-one-frame-apart) | 2026-08-14 | every sound cue played twice, one frame apart |
| [DISC-227](#disc-227-remvgrille-and-attack-share-one-screen-buffer-and-stacked-instead) | 2026-08-14 | RemvGrille and Attack share one screen buffer, and stacked instead |
| [DISC-228](#disc-228-brett-s-start-room-settled-live-the-remake-cannot-reproduce-his-escape) | 2026-08-14 | Brett's start room settled live; the remake cannot reproduce his escape |
| [DISC-229](#disc-229-the-opening-seats-survivors-3-3-brett-backfills-the-victim-s-room) | 2026-08-15 | the opening seats survivors 3+3; Brett backfills the victim's room |
| [DISC-230](#disc-230-select-outcome-decoded-in-full-the-ending-was-missing-a-line) | 2026-08-15 | `select_outcome` decoded in full; the ending was missing a line |
| [DISC-231](#disc-231-three-transient-banners-and-the-android-reveal-s-only-tell) | 2026-08-15 | three transient banners, and the android reveal's only tell |
| [DISC-232](#disc-232-the-control-panel-is-19-rows-and-every-band-below-row-0-was-wrong) | 2026-08-15 | the CONTROL panel is 19 rows, and every band below row 0 was wrong |
| [DISC-233](#disc-233-the-panic-wander-dead-end-was-real-but-not-the-bug-it-looked-like) | 2026-08-15 | the panic-wander dead end was real, but not the bug it looked like |
| [DISC-234](#disc-234-the-burning-ship-spiral-transliterated-rather-than-redrawn) | 2026-08-15 | the burning-ship spiral, transliterated rather than redrawn |
| [DISC-235](#disc-235-7000-is-the-control-list-s-colour-table-two-screens-two-tables) | 2026-08-15 | `$7000` is the CONTROL list's colour table; two screens, two tables |
| [DISC-236](#disc-236-indicate-is-a-two-page-room-name-list-the-remake-invented-a-scroller) | 2026-08-15 | INDICATE is a two-page room-name list; the remake invented a scroller |
| [DISC-237](#disc-237-most-of-the-needs-the-live-oracle-list-did-not-need-it) | 2026-08-15 | most of the "needs the live oracle" list did not need it |
| [DISC-238](#disc-238-indicate-rebuilt-from-the-rom-the-last-three-items-closed) | 2026-08-15 | INDICATE rebuilt from the ROM; the last three items closed |
| [DISC-239](#disc-239-the-resolution-independence-plan-s-own-premise-was-wrong-in-four-places) | 2026-08-15 | the resolution-independence plan's own premise was wrong in four places |
| [DISC-240](#disc-240-the-rom-data-was-stranded-behind-a-pygame-import) | 2026-08-15 | the ROM data was stranded behind a pygame import |
| [DISC-241](#disc-241-the-game-only-found-its-own-data-from-the-project-root) | 2026-08-15 | the game only found its own data from the project root |
| [DISC-242](#disc-242-the-renderer-draws-native-and-scales-once) | 2026-08-15 | the renderer draws native and scales once |
| [DISC-243](#disc-243-the-fit-was-measured-against-the-wrong-rectangle-and-step-5-was-never-needed) | 2026-08-15 | the fit was measured against the wrong rectangle, and step 5 was never needed |
| [DISC-244](#disc-244-four-play-report-bugs-and-the-deck-table-has-35-entries) | 2026-08-15 | four play-report bugs, and the deck table has 35 entries |
| [DISC-245](#disc-245-the-attack-banner-the-portrait-sprite-and-a-debug-overlay) | 2026-08-15 | the attack banner, the portrait sprite, and a debug overlay |
| [DISC-246](#disc-246-the-attack-row-s-window-was-decodable-d-169-checked-the-wrong-latch) | 2026-08-15 | the ATTACK row's window was decodable; D-169 checked the wrong latch |
| [DISC-247](#disc-247-the-mixer-does-not-survive-sleep-and-fails-silently-when-it-does-not) | 2026-08-15 | the mixer does not survive sleep, and fails silently when it does not |
| [DISC-248](#disc-248-the-two-inputs-a-gamepad-cannot-reach-and-the-invention-next-door) | 2026-08-15 | the two inputs a gamepad cannot reach, and the invention next door |
| [DISC-249](#disc-249-c64-py-was-two-things-and-one-of-them-was-on-the-wrong-side) | 2026-08-16 | `c64.py` was two things, and one of them was on the wrong side |
| [DISC-250](#disc-250-the-end-screen-comes-out-whole-the-text-toolkit-is-the-next-cut) | 2026-08-16 | the end screen comes out whole; the text toolkit is the next cut |
| [DISC-251](#disc-251-the-text-toolkit-was-what-held-frontend-py-together) | 2026-08-16 | the text toolkit was what held `frontend.py` together |
| [DISC-252](#disc-252-the-first-five-minutes-were-three-undocumented-commands) | 2026-08-16 | the first five minutes were three undocumented commands |
| [DISC-253](#disc-253-two-of-the-three-win-routes-had-never-been-flown) | 2026-08-16 | two of the three win routes had never been flown |
| [DISC-254](#disc-254-the-heartbeat-restarted-on-every-fear-tick-and-the-airlock-cost-809-ms) | 2026-08-16 | the heartbeat restarted on every fear tick, and the airlock cost 809 ms |
| [DISC-255](#disc-255-three-things-computed-every-frame-and-audio-held-six-times-over) | 2026-08-16 | three things computed every frame, and audio held six times over |
| [DISC-256](#disc-256-a-performance-overlay-on-the-ctrl-3-debug-mode) | 2026-08-16 | a performance overlay on the Ctrl+3 debug mode |
| [DISC-257](#disc-257-three-play-reports-two-faithful-one-my-own-debug-tool-lying) | 2026-08-16 | three play reports: two faithful, one my own debug tool lying |
| [DISC-258](#disc-258-the-ending-was-right-about-the-flags-and-wrong-about-the-people) | 2026-08-16 | the ending was right about the flags and wrong about the people |
| [DISC-259](#disc-259-the-alien-is-not-stuck-upstairs-it-is-just-very-slow) | 2026-08-16 | the Alien is not stuck upstairs, it is just very slow |
| [DISC-260](#disc-260-a-random-alien-start-as-a-flagged-added-rule) | 2026-08-16 | a random Alien start, as a flagged added rule |
| [DISC-261](#disc-261-four-play-report-items-the-box-s-name-the-second-slot-escape-the-border) | 2026-08-16 | four play-report items: the box's name, the second slot, Escape, the border |
| [DISC-262](#disc-262-a-quick-front-end-escape-as-the-panel-s-quit-and-a-patient-cat) | 2026-08-16 | a quick front end, Escape as the panel's quit, and a patient cat |
| [DISC-263](#disc-263-the-boot-order-corrected-and-the-selection-screen-says-what-it-takes) | 2026-08-16 | the boot order corrected, and the selection screen says what it takes |
| [DISC-264](#disc-264-the-crt-layer-a-tube-that-runs-faster-than-the-game) | 2026-08-16 | the CRT layer: a tube that runs faster than the game |
| [DISC-265](#disc-265-the-crt-tuning-pass-and-a-degauss-that-is-not-a-small-scramble) | 2026-08-16 | the CRT tuning pass, and a degauss that is not a small scramble |
| [DISC-266](#disc-266-phosphor-triads-and-the-one-stage-that-belongs-after-scaling) | 2026-08-16 | phosphor triads, and the one stage that belongs after scaling |
| [DISC-267](#disc-267-one-family-of-transient-led-by-the-chroma-shift) | 2026-08-16 | one family of transient, led by the chroma shift |
| [DISC-268](#disc-268-the-deck-change-that-never-fired-and-a-tube-that-stopped-at-the-field) | 2026-08-16 | the deck change that never fired, and a tube that stopped at the field |
| [DISC-269](#disc-269-the-view-follows-the-crew-and-ripley-is-already-the-best-cat-catcher) | 2026-08-16 | the view follows the crew, and Ripley is already the best cat-catcher |
| [DISC-270](#disc-270-a-live-capture-session-four-confirmations-and-one-real-bug) | 2026-08-17 | a live capture session: four confirmations and one real bug |
| [DISC-271](#disc-271-the-panel-does-take-the-joystick-and-what-the-countdown-really-needs) | 2026-08-17 | the panel does take the joystick, and what the countdown really needs |
| [DISC-272](#disc-272-indicate-location-leaves-its-list-open) | 2026-08-17 | INDICATE LOCATION leaves its list open |
| [DISC-273](#disc-273-the-tracker-reports-proximity-and-nothing-else) | 2026-08-17 | the tracker reports proximity and nothing else |
| [DISC-274](#disc-274-two-endings-caught-live-and-the-32-threshold-in-the-open) | 2026-08-17 | two endings caught live, and the $32 threshold in the open |
| [DISC-275](#disc-275-the-launch-conditions-complete-and-a-win-ending-on-screen) | 2026-08-17 | the launch conditions, complete, and a win ending on screen |
| [DISC-276](#disc-276-the-android-branch-does-not-choose-an-ending) | 2026-08-17 | the android branch does not choose an ending |
| [DISC-277](#disc-277-the-auto-destruct-countdown-timed-on-the-machine) | 2026-08-17 | the auto-destruct countdown, timed on the machine |
| [DISC-278](#disc-278-what-enter-hypersleep-actually-does) | 2026-08-17 | what ENTER HYPERSLEEP actually does |
| [DISC-279](#disc-279-the-companion-term-is-turn-scoped-not-continuous) | 2026-08-17 | the companion term is turn-scoped, not continuous |
| [DISC-280](#disc-280-blowlock-is-offered-from-the-corridor-confirmed-live) | 2026-08-17 | BLOWLOCK is offered from the corridor, confirmed live |
| [DISC-281](#disc-281-panic-is-loss-of-control-not-wandering) | 2026-08-17 | panic is loss of control, not wandering |
| [DISC-282](#disc-282-the-net-does-no-damage-and-two-specials-flip-in-place) | 2026-08-17 | the net does no damage, and two specials flip in place |
| [DISC-283](#disc-283-scuttle-and-override-are-one-row-in-the-command-centre) | 2026-08-17 | SCUTTLE and OVERRIDE are one row in the command centre |
| [DISC-284](#disc-284-three-traps-that-make-a-live-measurement-lie) | 2026-08-17 | three traps that make a live measurement lie |
| [DISC-285](#disc-285-attack-is-the-path-and-it-costs-the-room-6) | 2026-08-17 | ATTACK is the path, and it costs the room 6 |
| [DISC-286](#disc-286-the-instruction-viewer-was-cutting-the-bottom-off-half-the-pages) | 2026-08-27 | the instruction viewer was cutting the bottom off half the pages |
| [DISC-287](#disc-287-an-idle-character-never-takes-a-turn) | 2026-08-18 | an idle character never takes a turn |
| [DISC-288](#disc-288-the-alien-s-room-damage-magnitude-decoded-cadence-measured) | 2026-08-29 | The Alien's room damage: magnitude decoded, cadence measured |
| [DISC-289](#disc-289-disc-258-re-run-the-breach-gates-are-right-and-the-arithmetic-still-does-not-close) | 2026-08-30 | DISC-258 re-run: the breach gates are right, and the arithmetic still does not close |
| [DISC-290](#disc-290-p-8-the-corrode-fraction-and-it-does-not-look-wrong) | 2026-08-30 | P-8: the corrode fraction, and it does not look wrong |
| [DISC-291](#disc-291-two-presentation-bugs-from-a-playtest-and-the-log-that-split-them) | 2026-08-30 | Two presentation bugs from a playtest, and the log that split them |
| [DISC-292](#disc-292-what-one-turn-is-and-why-it-needs-no-re-denomination) | 2026-08-18 | what one turn is, and why it needs no re-denomination |
| [DISC-293](#disc-293-two-decisions-rather-than-two-more-open-items) | 2026-08-18 | two decisions rather than two more open items |
| [DISC-294](#disc-294-the-turn-based-mode-gets-a-door-headless-turns) | 2026-08-18 | the turn-based mode gets a door: `--headless-turns` |
| [DISC-295](#disc-295-p-8-a-six-minute-paired-capture-and-why-the-fraction-still-is-not-clean) | 2026-08-18 | P-8: a six-minute paired capture, and why the fraction still is not clean |
| [DISC-296](#disc-296-p-8-closed-the-corrode-fraction-read-from-the-flag-itself) | 2026-08-18 | P-8 closed: the corrode fraction, read from the flag itself |
| [DISC-297](#disc-297-correction-disc-296-reproduced-a-trap-this-file-already-warned-about) | 2026-08-18 | CORRECTION: DISC-296 reproduced a trap this file already warned about |
| [DISC-298](#disc-298-f-1-s-decision-free-half-derivation-as-a-generator) | 2026-08-18 | F-1's decision-free half: derivation as a generator |
| [DISC-299](#disc-299-l5-r1-r6-reading-the-session-logs-the-way-the-owner-actually-will) | 2026-08-18 | L5/R1-R6: reading the session logs the way the owner actually will |
| [DISC-300](#disc-300-cr1-cr5-a-credits-screen-built-entirely-from-records-that-already-existed) | 2026-09-02 | CR1-CR5: a credits screen, built entirely from records that already existed |
| [DISC-301](#disc-301-p-9-the-corrode-gate-is-right-corridors-structurally-never-hold) | 2026-09-03 | P-9: the corrode gate is right; corridors structurally never hold |
| [DISC-302](#disc-302-p-9-follow-up-the-long-capture-caught-something-bigger-than-p-9) | 2026-09-03 | P-9 follow-up: the long capture caught something bigger than P-9 |
| [DISC-303](#disc-303-the-credits-row-collided-with-the-copyright-line-found-by-actually-taking-a-screenshot) | 2026-09-03 | the CREDITS row collided with the copyright line, found by actually taking a screenshot |
| [DISC-304](#disc-304-the-credits-test-isolation-gap-found-by-actually-populating-out-sounds) | 2026-09-03 | the credits test-isolation gap, found by actually populating out/sounds/ |
| [DISC-305](#disc-305-c2-t6-turns-as-a-real-options-menu-mode-and-the-poll-orders-trap) | 2026-09-04 | C2/T6: turns as a real options-menu mode, and the poll_orders() trap |
| [DISC-306](#disc-306-p-9-a-long-clean-capture-contradicts-disc-301-s-own-reframing) | 2026-09-04 | P-9: a long clean capture contradicts DISC-301's own reframing |
| [DISC-307](#disc-307-p-9-two-independent-long-captures-converge-on-0-29-not-0-13-or-0-41) | 2026-09-04 | P-9: two independent long captures converge on ~0.29, not 0.13 or 0.41 |
| [DISC-308](#disc-308-the-crew-survival-question-a-second-data-point-opposite-of-the-first) | 2026-09-04 | the crew-survival question: a second data point, opposite of the first |
| [DISC-309](#disc-309-the-attack-banner-animation-could-get-stuck-and-why-the-fix-has-to-check-ground-truth) | 2026-09-05 | the attack banner/animation could get stuck, and why the fix has to check ground truth |
| [DISC-310](#disc-310-turn-based-mode-gets-an-initiative-order-not-the-original) | 2026-09-04 | turn-based mode gets an initiative order (not the original) |
| [DISC-311](#disc-311-screen-fx-an-optional-wipe-in-for-the-title-and-ending-screens) | 2026-09-04 | `screen_fx`: an optional wipe-in for the title and ending screens |
| [DISC-312](#disc-312-screen-fx-missed-the-boot-report-the-actual-first-text-screen) | 2026-09-04 | `screen_fx` missed the boot report (the actual "first text screen") |
| [DISC-313](#disc-313-screen-fx-the-rest-of-the-described-effects-glitch-cursor-prompt) | 2026-09-05 | `screen_fx`: the rest of the described effects (glitch, cursor, prompt) |
| [DISC-314](#disc-314-screen-fx-scoped-to-boot-only-plus-power-on-degauss-streak-letters-colour) | 2026-09-05 | `screen_fx`: scoped to BOOT only, plus power-on/degauss/streak/letters/colour |
| [DISC-315](#disc-315-turn-based-mode-action-points-shown-skip-turn-auto-select-creature-notice) | 2026-09-05 | turn-based mode: action points shown, skip turn, auto-select, creature notice |
| [DISC-316](#disc-316-a-clickable-skip-turn-row-and-quit-relabelled-back) | 2026-09-05 | a clickable "Skip turn" row, and "quit" relabelled "back" |
| [DISC-317](#disc-317-a-loudness-spec-check-and-game-audio-sampled-renamed-enhanced) | 2026-09-05 | a loudness spec check, and `game_audio=sampled` renamed `enhanced` |
| [DISC-318](#disc-318-back-skip-turn-get-their-own-row-colours-is-there-enough-room) | 2026-09-05 | "back"/"Skip turn" get their own row colours; "is there enough room" |
| [DISC-319](#disc-319-p9-b-goal-session-room-damage-alien-per-action-cadence-live-confirmed-alien-move-ticks-s-own-bounding-not-a-rate-caveat-closed) | 2026-09-05 | P9-B goal session: ROOM_DAMAGE_ALIEN_PER_ACTION cadence live-confirmed, ALIEN_MOVE_TICKS's own "bounding, not a rate" caveat closed |
| [DISC-320](#disc-320-p9-b-goal-session-3-deliberately-timed-idle-survival-trials-and-the-remake-s-own-gap) | 2026-09-05 | P9-B goal session: 3 deliberately-timed idle-survival trials, and the remake's own gap |
| [DISC-321](#disc-321-p9-b-goal-session-the-tracker-alarm-live-confirmed-on-real-sid-registers) | 2026-09-05 | P9-B goal session: the tracker alarm, live-confirmed on real SID registers |
| [DISC-322](#disc-322-p9-b-goal-session-room-glyph-s-duct-view-note-was-also-stale) | 2026-09-05 | P9-B goal session: `_ROOM_GLYPH`'s duct-view note was also stale |
| [DISC-323](#disc-323-the-crew-survival-gap-is-probably-sample-size-noise-not-a-mechanism-gap) | 2026-09-05 | the crew-survival gap is probably sample-size noise, not a mechanism gap |
| [DISC-324](#disc-324-screen-fx-turned-on-by-default-under-ouijaghost) | 2026-09-06 | `screen_fx` turned on by default under OUIJAGHOST |
| [DISC-325](#disc-325-p-9-closed-by-calibration-not-mechanism-a-live-oracle-session-blocked-on-input-injection) | 2026-09-07 | P-9 closed by calibration, not mechanism - a live-oracle session blocked on input injection |
| [DISC-326](#disc-326-game-selection-s-cursor-was-invented-once-removed-then-reintroduced-updated-only) | 2026-09-13 | GAME_SELECTION's cursor was invented once, removed, then reintroduced - UPDATED only |
---

## D-022 — The deck-plan room-identification mechanic (Upper/Middle/Lower Deck) is a blinking row-cursor
- **Date:** 2026-07-11
- **Finding:** Traced statically from ALIEN.prg (`draw_deck_map $73C8`, the input
  loop `$7453`, `init_menu_ptr/menu2/menu3 $7132/$7112/$7122`) — the "animated
  square markers that identify which room is which" is a **blinking highlight
  cursor** over the on-screen deck plan, not per-room icons:
  * **Three deck displays.** `$402A` holds the current deck (0/1/2 = Upper/
    Middle/Lower). Each deck's screen is a template drawn char-by-char from
    `$A000` (deck 0), `$A21C` (deck 1), `$A438` (deck 2) — 30 columns wide — via
    the `charpump_colorfill $7150` copy. (These are the same three deck maps the
    remake already carries as `the live captures (not published)*deck_0400.bin` captures.)
  * **The highlight cursor.** `$64E5` = the selected map **row** (0-18); `$64E4`
    = that row's "normal" colour, looked up from the colour template `$7000,Y`.
    `set_color_ptr_row $753F` computes the colour-RAM address of row `$64E5`
    (`$D81E + $64E5*40`, the map panel starts at screen `$041E` / colour `$D81E`,
    10 cells wide). The row is then **alternated** between white (`$01`, via
    `fill10_via_fd $7530`) and its normal colour (`$64E4`, via `sub_7520`) each
    input-poll cycle → a **blink** identifying the current room. `draw_deck_map`
    also stamps a 10-wide row of char `$01` markers at a per-row screen pointer
    `$64F9/$64FA`.
  * **Navigation.** The loop `$7453` reads the joystick (`$71AF`): **1 (up)** →
    `DEC $64E5`, **2 (down)** → `INC $64E5`, each with wrap + skip logic over
    non-room rows (special cases at rows 9/11/12 → the map has corridor/label
    rows between rooms). **4 (fire)** on the three deck rows (`$64E5` = `$0D` →
    `init_menu_ptr`, `$0E` → `init_ptr_menu2`, else → `init_ptr_menu3`) selects
    that deck and redraws (`$402A` ← 0/1/2). `$64FB` tracks the room index for
    the name/guard checks (`guard_alien_present $7720`).
- **LIVE-VERIFIED (same day, MCP reachable over HTTP via `tools/vice-mcp/
  vice_client.py`).** Reached the UPPER-DECK play screen
  (`out/vice_shots/deck_blink_00.png`) and corrected the static hypothesis:
  * **The "square markers" are STATIC char `$E6`** — a dithered checkerboard
    glyph, drawn green, one per room on the deck map (left side). Sampling screen
    RAM `$0400` + colour RAM `$D800` (low nibble) for 5 s with **no input**
    showed **zero toggling cells** — there is **no free-running blink**. The
    "animated" look the player recalls is the dither's CRT shimmer and/or the
    interaction flash below, not a data-level animation.
  * **The remake ALREADY renders these markers.** The `the live captures (not published)
    *deck_0400.bin` captures contain the `$E6` markers (9-16 per deck) and the
    remake draws those captures through the game's charset in green, so the green
    room markers are present in `out/vice_shots/remake_play_deck0.png` (verified).
    R-35's *static* half was effectively already done.
  * **The `$7453` white↔colour row repaint is INPUT-driven, not free-running.**
    `sub_7453` returns immediately when `$71AF == 0`; the row is only repainted
    when the selection cursor moves through the right **CONTROL panel** list
    (ORDER · DALLAS…BRETT · INDICATE LOCATION · DISPLAY LEVEL · UPPER/MIDDLE/
    LOWER DECK). So the panel cursor flashes as it moves; the map markers stay
    static.
- **NAVIGATION CRACKED (live).** `read_input $71B0` reads **both keyboard `$C5`
  and joystick `$DC00`** into `$71AF` (1=up, 2=down, 4=fire). `$7453` dispatches
  on **`$64FB`** (the selection mode): `0` = top CONTROL list, `1-7` = a crew is
  selected → their order menu (`$7AEB`), `≥8`/`$10` = a sub-list. Confirmed by
  driving the joystick: **up/down move the cursor `$64E5`** and the **white
  highlight bar tracks it exactly** (colour RAM `$D81E + $64E5*40`, the right
  panel), **skipping the two-line headers** (10→13 skipped DISPLAY LEVEL at
  11/12). Firing:
  * on a **crew row** (2-8) → `$64FB` = row-1, opens that crew's order menu;
  * on a **deck row** (13/14/15 = UPPER/MIDDLE/LOWER) → `init_menu_ptr`/`menu2`/
    `menu3`, `$402A`←0/1/2 → **switches the displayed deck** (this is the remake's
    existing deck-select; DISPLAY LEVEL);
  * on **INDICATE LOCATION** (row 10) → `$64FB=$10`, and the right panel becomes a
    **scrollable room-name list** (live: QUIT · AIRLOCK #1/#2 · ARMOURY · CARGOPOD
    #1-3 · COMMDCENTR · COMPUTER · CORRIDOR #1-7 · CRYO VAULT · ENGINEERNG · OTHER
    LIST → page 2; the 36 names at `$A71C`). Cursoring a room name **indicates
    that room's location** on the left map (its `$E6` marker) — the actual
    "identify which room is which" feature. `out/vice_shots/indicate_02_cursored.
    png`. Input flakiness note: an 8-frame joystick *tap* often falls between the
    game's once-per-main-loop `read_input` polls and is missed — **hold** the
    direction (`vice_joystick_set` ~0.3 s) for a reliable single step.
- **Action:** todo **R-35** updated. The remake already has the deck-switch and
  the static markers; the genuinely-missing feature is the **INDICATE LOCATION
  room-name list** (pick a room → highlight its map marker) — now fully understood
  and implementable. Only the exact marker-flash styling on the map when a room is
  indicated is still worth a screenshot (VICE_CHECKS).

## D-021 — Dense boot capture pins the exact front-end/title visuals for a 1:1 remake
- **Date:** 2026-07-11
- **Finding:** A real-time (warp OFF) dense screenshot sweep of the whole boot
  (`tools/vice-mcp/capture_boot.py`, ~73 shots in `out/vice_shots/boot_*.png`)
  captured every front-end screen's exact layout, colours, and text — the piece
  D-018 (which pinned the boot *chain* symbolically) didn't have. In boot order:
  * **`boot_002` "LOADING MENU"** — blue text, centred, black field. A loading
    interstitial the remake was missing entirely.
  * **`boot_015` NOTICE** — white **mixed-case** body ("We strongly suggest you
    make a back-up copy of this diskette…Green Valley Publishing / a division of
    ShareData, Inc.") + yellow reverse "PRESS ANY KEY TO CONTINUE". Advances on
    any key (not a timer).
  * **`boot_024` WELCOME** — rainbow PETSCII border, boxed "GREEN VALLEY
    PUBLISHING", "WELCOME TO ALIEN / FACE THE POWER OF THE UNKNOWN", options
    "**1** ALIEN / **Q** QUIT" (reverse key boxes), cyan "CHOOSE ONE OF THE
    ABOVE". "1" starts, "Q" quits.
  * **`boot_025` INSTRUCTIONS** — red spaced "A L I E N" header, "DO YOU WANT
    INSTRUCTIONS? (Y OR N)", "N WILL START THE GAME", "PRESS RESTORE TO EXIT THE
    PROGRAM". N (or Y) proceeds.
  * **`boot_045` "LOADING…. / PLUG JOYSTICK INTO PORT TWO"** — blue text card.
  * **`boot_078` TITLE** — verified against ALIEN.prg / init_c (`$5DEB`), NOT
    guessed from the screenshot:
    - **Field is SOLID BLACK.** `clear_screen_fill ($6426)` tiles char `$A0`
      (a solid block in the custom charset) in colour 0 over every cell, so the
      `$D021=$0D` light-green background is fully covered. There is **no
      starfield and no perspective-line graphic** in the character layer — the
      faint dots/diagonals in the capture are unexplained by the code (VICE
      display artifact or an untraced IRQ effect) and were **not** reproduced.
      An earlier remake pass invented a random starfield + corner lines; removed.
    - **The egg is 8 MULTICOLOR SPRITES, not one.** Pointers `$C9-$D0` → bank
      `$3240-$343F`, all sprite colour 5 (green), shared multicolor `$D025=7`
      (yellow) / `$D026=1` (white), positioned by the 16-byte table at `$5DDB`
      in a **2-3-3** layout (VIC X/Y: (157,106)(181,106) / (145/169/193,127) /
      (145/169/193,148)). Decoded straight from the PRG they compose the
      cracked-open egg on its nest (`out/vice_shots/egg_real_2000base.png`).
    - **The text is the game's OWN cut-out glyphs, colour light-green (`$0D`).**
      The "ALIEN" letters are custom glyphs `$81/$8C/$89/$85/$8E` (verified: each
      is the letter as its 0-bits) on row 1 cols 9/14/19/24/29, spelled in one
      at a time (`$5E90`). The epigraph screen codes at `$5E4A` (→ row 22 col 3)
      and `$5E67` (→ row 24 col 23) decode through the charset to
      `'We live as we dream : Alone'` / `JOSEPH CONRAD` (mixed case). No
      colour-RAM write occurs, so all title text is the `$D021` light-green seen
      through the black field — not white.
  * Title→selection held ~130 s in the capture, but per the code the egg title
    is brief (the `$5E74` letter animation) and `main_dispatch ($5ECE)` then
    replaces it with the game-selection portrait screen, whose `$5F36` loop waits
    on Ctrl+1/Ctrl+2 — i.e. the long hold was the *selection* screen, not the
    title (the crude capture detector mislabelled it).
- **Action:** Rewrote the remake front-end to match — added `Screen.LOADING_MENU
  / NOTICE / WELCOME / INSTRUCTIONS / LOADING_PLAY` before `TITLE` in
  `core/flow.py` (timed cards tick; NOTICE/WELCOME/INSTRUCTIONS are input-gated),
  and rewrote `render/pygame_app.py` `_draw_title` plus the five new front-end
  draw methods. **The title is now built from the ROM:** the 8-sprite multicolor
  egg is composed from `TileSet.region` (new raw-bank field on `TileSet`) via
  `_title_egg_surface`, and the letters + epigraph are drawn through the game's
  own charset as light-green cut-out text via `_blit_c64_text` (from the real
  screen codes). The invented starfield/perspective-lines and the single-sprite
  egg were removed. Remaining 1:1 refinements filed in `todo.md`: the WELCOME
  rainbow border + box, the instruction **pages** shown on the "Y" path
  (`the live captures (not published)instructions1-10.png`), and the deck-menu room markers. The
  capture's faint title dots stay a `[?]` (see the boot_078 note above).

## D-018 — Live-disassembly (vice-mcp) confirms the engine core and corrects the portrait layout
- **Date:** 2026-07-08
- **Finding:** With the game running under vice-mcp, symbolic disassembly +
  live memory reads confirmed the boot/init/IRQ/selection code at instruction
  level (see `docs/re/DISASSEMBLY.md`, `docs/re/alien.sym`). Key confirmations
  and one correction:
  * **Boot chain** matches the disassembly exactly, driven live: Green Valley notice →
    "1 ALIEN" → "DO YOU WANT INSTRUCTIONS?(Y/N)" → "LOADING…/PLUG JOYSTICK
    INTO PORT TWO" → game-selection.
  * **Entry `$4000`**: patch KERNAL vectors → VIC char base `$2000` → black
    border/bg → `init_a` (`$4DB8`) → `init_b` (`$8FFC`) → `init_c` (`$5DEB`)
    → `main_dispatch` (`$5ECE`). `init_a` installs the raster IRQ at line
    `$61`, vector `$4D08`.
  * **IRQ `$4D08`**: the four `update_*` routines (`$4EE8/$4F19/$4F52/$4FCB`)
    fire every **9 jiffies** (`DEC $6579` reload `#$08`) and are **sprite/
    sound only** — world state is NOT advanced here (confirms the GAMEDATA.md
    timing model at instruction level). `$60A8` gates title-music vs game.
  * **Game selection `$5ECE`**: sets sprite pointers `$07F8-$07FE = $BD-$C3`.
    `$BD×64 = $2F40 = $2800 + 29×64`, so the **7 crew portraits are sprite
    slots 29-35** (confirms the remake's slot order). **Correction (R-09):**
    the portrait sprites are all at **Y=`$52` — one level row** (X = 48, 88,
    128, 168, 208, 248, 288); only the *name labels* stagger above/below. The
    remake currently staggers the sprite rows and should use one row.
  * **Selection input (R-18):** read `$91` (KERNAL key latch) — `$FA` =
    **Ctrl+1** (Full), `$F3` = **Ctrl+2** (Short; the on-screen "Control:1/2"
    is the literal Ctrl-key chord) → `var_game_mode ($4303)` → `start_game
    ($7013)`.
  * **`start_game` ($7013):** sets `$60A8=0` (stops the title tune, switches
    the IRQ to the game tick), `$D020=$06` (**blue border** — confirms the
    remake's border), sprite 0 colour `$01` (**the white person/character
    marker**), banks out BASIC (`$01` LORAM=0 → `$A000+` is RAM), and builds
    the play screen by copying a **fixed screen-code template from `$A654`**
    (+ colours from `$7001`) into screen RAM — i.e. the CONTROL panel + status
    layout is a copied template, then `JMP main_loop ($719D)`.
  * **World clock = `char_pump` ($7216):** per-character **action timer**
    `$64EE,Y` counts down each main-loop pass; at 0 the char acts and
    `resolve_char_move ($5156)` steps it toward its **destination room**
    `$64E6,Y`, then the timer reloads (crew `$6586`, Alien `$6581=70`).
    **★ Two mechanics the remake lacks:** (1) **room capacity = 3** — a char
    whose destination already holds ≥3 others **waits** (`timer=$20`) instead
    of entering; (2) **destination-walk** movement — a char is given a
    destination and walks there over several ticks (not one-room-per-order).
    `resolve_char_move` is **grille-gated**: it stops a char in a room with no
    grille (CORRIDOR 6). Deep state machine (`$64C4/$6571/$6501/$650C`) needs
    live stepping.
  * **Live pass (2026-07-08):** drove the running game — start positions
    `$7935 = [0,6,6,6,27,27,27,0,0]` match GAMEDATA.md exactly; the time base is
    the KERNAL jiffy clock (`$A0-$A2`) not a dedicated oxygen down-counter
    (supports R-22 = elapsed jiffies); **wounding confirmed** ("Alien wounds
    Ripley", R-26); game-over handler `$6469` (wait-key → menu).
  * **Live pass 2 (warp off):** the opening is a timed delay loop (`$7560`)
    gated by `game_active ($64BB)` — game logic runs only once `$64BB`=1. **★
    R-22 resolved:** a monotonic-decrease scan of all game RAM over 10s of
    active play found **no oxygen down-counter** → oxygen/TOOH is **time-derived
    from the jiffy clock** (`$A0-$A2`), not stored; the remake's per-tick
    oxygen counter needs reworking to elapsed-time. Alien moves ~1/9s at 1×;
    crew idle without orders. See DISASSEMBLY.md §3.5.
  * **Movement order gate `$6571` (live):** an idle crew member reads
    `$6571,Y = 4`; `resolve_char_move` aborts when `$6571 ≥ 2`, so **≥2 =
    "awaiting order"** and a MOVE order must drop it `<2` (with the destination)
    to start the crew walking — the flag the CONTROL-panel order code writes
    (R-16). Injecting dest+timer alone does not move idle crew.
  * **PCS state-of-mind = `$6571`/`$7D55`** (both read `[4,4,3,4,3,4,3]` live,
    identical per crew; adjacent to the morale words `$7CEA`). Only writer of
    `$6571` is `order_gate_update ($4843)` (from `$7D55`+`$4781`); only
    decrement `$4238`. **⚠ CORRECTION (user before/after order capture,
    `the live captures (not published)pcs_*.bin`):** an earlier read of `resolve_char_move` as
    "`$6571 ≥ 2` blocks movement / crew won't obey" was **wrong** (`$7244` is
    the normal `char_pump` return, not an abort). Dallas **moved** CommdCentr→
    Corridor#1 with `$6571`/`$7D55` = 4 unchanged — so state-of-mind does NOT
    hard-gate obedience; **don't model a hard morale block on movement.** Its
    real (softer) role — obey-probability / response-delay — is still `[?]`.
  * **Issuing a MOVE order writes exactly** `var_current_char ($64FB)` = the
    crew slot and `tbl_char_dest ($64E6,slot)` = the destination room id (plain,
    no `$80` for crew); the char then walks there after the `$64EE` action-timer
    delay. `$7D55`/`$6571` untouched by the order. (R-16.)
  * **Opening→play is a TIMEOUT** (user: no input; the "has been killed" screen
    auto-advances after a delay via `$8CF3`→`$8D1A`→`$4F90` setting `$64BB=1`).
  * **PCS stressor (static, `$729C` in `char_pump`):** `$7D55` (state-of-mind)
    **worsens by 1 each tick a character is in a duct** (`$6501,Y` set) —
    crawling the vents raises fear. `$7D55` read in 11 places (morale display,
    `$4843`, this stressor); its obey/refuse use (if any) is `[?]`.
  * **Tooling:** `tools/vice-mcp/boot_to_play.py` (screen-RAM-detecting reliable
    boot); `vice_snapshot_save`/`_load` use a `name` param (snapshots live in
    `%APPDATA%\vice\mcp_snapshots\`). **GTK3VICE-3.9 snapshots do NOT load in
    the MCP build (3.11)** — version mismatch; use before/after memory dumps
    (`save "f" 0 6000 7fff`) for cross-build capture instead.
- **Action:** foundation for the full annotated disassembly the user requested
  before the Python rewrite (`docs/re/DISASSEMBLY.md`, incremental). The R-09
  one-row-portrait correction is filed for the remake; deeper regions
  (`start_game`/main loop/char pump/Alien AI/oxygen/morale/CONTROL-panel/
  routing tables) are the next live-tracing passes (todo.md `R-*`, tasks
  #13-16).

## D-017 — ALIEN's gameplay model is stored as plain data tables in the PRG, and they contradict several remake inventions
- **Date:** 2026-07-03
- **Finding:** Prompted by the user's redirect ("the code is the truth, the
  manual only a hint"), a code-faithfulness audit cross-referenced the
  disassembly with the five RAM captures and found the whole gameplay model
  sitting in decodable tables inside `ALIEN.prg`: the real 34-room map
  (names $A71C, decks $80D3, N/S/E/W neighbor tables $80F5-$815B, grilles
  $8676), the 20-item table with **fixed** placements ($82CF/$82E3 — the
  three LASER PISTOLS start in the ARMOURY; the manual's "taser" doesn't
  exist, it's the laser pistol; THERMLANCE exists unspawned), the 9-slot
  character arrays (0=Alien, 1-7=crew in CONTROL order, 8=Jones; $7935
  locations, $6586 per-character walk durations 4/4/3/4/3/4/3 + Jones 5),
  the real morale words CONFIDENT/STABLE/UNEASY/SHAKEN/BROKEN and physical
  states O.K./WOUNDED/COLLAPSED/DEAD ($7CEA), and the Alien's actual AI
  ($8A74): a uniform 0-15 roll per action — 13/16 a west-biased compass
  move taking 70 loop-units ($6581), 3/16 a 40-unit duct hide — with **no
  nearest-crew sensing at all**. Timing: the IRQ divider fires every NINE
  jiffies (not 8 frames) and drives only sprite/sound routines; world state
  advances from the free-running main loop at $719D via per-character
  action timers (the behaviour spec's "IRQ drives four game-update routines at ~6 Hz" was
  wrong on both counts). Evidence for every claim (capture cross-checks:
  the SHUTTLEBAY id pin, the tracker/cat-box fixed-address reads, the
  Alien-only moving slot) in **docs/re/GAMEDATA.md**.
- **Action:** decoder `alientools/gamedata.py` + `gamedata` CLI subcommand;
  generated snapshot `alien_remake/core/gamedata_snapshot.py` (derived,
  drift-guarded by test); remake core rewritten onto the real data (map,
  items, crew starts/speeds, Alien AI, morale words, SHUTTLEBAY evacuation,
  timing constants — DECISIONS D-017/D-018). Deliberately-not-guessed gaps
  filed in GAMEDATA.md §3 (routing tables' trigger, consumables,
  wounded/insane states, fire/damage system, oxygen counter, absolute loop
  rate, deck-value orientation).

## D-016 — The `the live captures (not published)*_0400.bin` VICE dumps ARE the deck-map screen RAM, and decode losslessly through the SG charset
- **Date:** 2026-07-03
- **Finding:** Filed while fixing a user-reported fidelity bug ("the game as
  displayed with play.bat looks nothing like the original game"). SM's open
  item (`the live captures (not published)nostromo_map.md`) asked for a `$0400` screen dump per
  deck to upgrade the eyeballed `DECK_GRIDS` transcription; those captures
  (`upperdeck_0400.bin`, `middledeck_0400.bin`, `lowerdeck_0400.bin`) now exist
  in the repo but hadn't been mined. Decoded: each is a VICE `save`-format dump
  (2-byte little-endian load address `$0400`, confirmed via the header bytes)
  of **31744 bytes covering `$0400-$7FFF`** — far more than the 1000-byte
  screen itself. The first 1000 bytes (`$0400-$07E7`, 40x25) are exactly the
  real game's screen RAM for that deck's map view: each byte is a direct index
  into the same 256-glyph charset SG already extracted from `ALIEN`'s own
  `$2000-$3FFF`, so decoding is a lossless lookup, not a guess. Rendered all
  three and compared against the reference screenshots (`upper deck.png` /
  `middle deck.png` / `lower deck.png`): the room shapes, wall line-art, deck
  labels, and grille cross-hatch glyphs match the real screenshots exactly.
  Glyph `0xA0` (screen code 160) decodes to a fully solid 8x8 tile (all bits
  on) — it is *not* a hash/texture glyph as the the ship map placeholder's choice of
  `_ROOM_GLYPH = 0xA0` had assumed by coincidence; it's the flat floor fill,
  and the room's "grille" cross-hatch look in the real screenshot most likely
  comes from per-cell **color** (multicolor char mode and/or color RAM),
  which no capture here recovers — `$D800` was never dumped. Rows 17-24 of
  each capture hold a *dynamic* status snapshot from whenever the user took
  it (one dump literally reads "... has been killed by the ALIEN") — not
  reusable verbatim as backdrop, since it would misleadingly show a fixed
  message regardless of live game state.
- **Action:** built `alien_remake/render/deck_backdrop.py` to decode rows 0-16
  (map + static CONTROL labels) of each capture and render it as the deck
  view's real background art in `pygame_app.py`, replacing the uniform grid
  of placeholder tiles (`tests/test_deck_backdrop.py`, 5 tests). Crew/Alien/
  Jones/cursor markers are still positioned via the internal (coarse,
  eyeballed) `core/nostromo.py` room grid scaled proportionally onto the real
  backdrop's pixel footprint — visually much closer, but not pixel-exact
  per-room alignment. **Not done, follow-up filed:** the remaining ~30720
  bytes (`$07E8-$7FFF`) of each capture are a large chunk of the game's live
  working RAM, never mined; a connected-component pass over the decoded
  screen (flood-fill the non-wall-glyph cells) could extract *exact* real
  room boundaries per deck to replace `DECK_GRIDS`'s eyeballed shapes and
  fully close SM's open item — not attempted this pass (no numbered
  pass yet; raise if the user wants pixel-perfect marker alignment next).
  A `$D800` color-RAM capture per deck would let the backdrop use real colors
  instead of the current flat green choice.

## D-015 — The intro tune's filter character sweeps percussive→held over exactly 102.4s, then wraps; pitch keeps drifting past that
- **Date:** 2026-07-02
- **Finding:** Tracing why a human listen (DECISIONS D-016) found the first
  30s render of `out/intro.wav` lacking "sustains and held notes": the
  music-player init (`$8FFC`) zeroes `$91D6` and the per-jiffy player (`$9039`)
  writes `INC $91D6; STA $D413` every note-step (24 jiffies = 0.4s) — so voice
  3's attack/decay register climbs by 1 every step, wrapping mod 256. Since
  `$D413`'s high nibble is voice 3's attack rate and low nibble its decay
  rate, this sweeps voice 3's envelope shape from near-instant (steps 0-15:
  attack index 0-1, ≤8ms) to very slow (steps ~240-255: attack index 15 =
  8000ms, decay index 15 = 24000ms) over exactly 256 steps × 24 jiffies = 6144
  jiffies = **102.4 real seconds**, then `$91D6` wraps and the sweep restarts
  from percussive. Voice 3's envelope (read back at `$D41C`) drives the SID
  filter cutoff every jiffy (`STA $D416`), so this is the tune's actual
  large-scale structure: a slow crescendo from a choppy, filter-pumping
  texture to a smooth, held-open one, not a short repeating riff. Confirmed
  empirically: an RMS trace of a 105s render shows heavy pumping (RMS
  swinging between ~0.02 and ~0.3 every ~0.2s) through roughly the first 90s,
  then a smooth un-pumping plateau (~0.25-0.29, no swings) from ~90s to
  ~102s — exactly where the sweep math predicts. **A render shorter than
  102.4s (the original default was 30s) only ever captures the percussive
  opening third and never reaches the held portion at all** — this, not a
  bug in the envelope logic itself (voice 1/2's own envelopes were already
  confirmed reaching and holding `level=1.0`), was the primary cause of the
  "no held notes" complaint (the filter-clipping bug DECISIONS D-016 also
  fixed was a compounding second cause). **The sweep is not a sample-exact
  loop point**, though: comparing SID register writes between the 2nd and 3rd
  full 6144-jiffy cycles of a 320s render found the rhythm/gate/filter-cutoff
  writes exactly periodic, but voice 1/2's *pitch* writes (registers
  `$D400/$D401/$D407/$D408`) differ — the note-table lookup applies an octave
  shift (`$91A6`/`$91A7`, decremented conditionally per note against the
  `$91AD` "measure" counter) that isn't bounded/reset within one 6144-jiffy
  cycle, so pitch keeps slowly transposing across sweeps even though the
  filter/rhythm character repeats identically. Not traced further (the
  reset/wrap condition for `$91A6`/`$91A7`, if any, is unknown).
- **Action:** `intro.py`'s default render length changed from 30s to
  `DEFAULT_SECONDS = 102.4` (`LOOP_JIFFIES = 6144`) so the held portion is
  actually present by default (DECISIONS D-016). The lack of a sample-exact
  loop point is why `PygameRenderer` loops the *whole rendered file*
  (`loops=-1`) rather than attempting a seamless mid-piece splice — filed as
  the disclosed gap in D-016's Consequences. If seamless looping is wanted
  later, resolving `$91A6`/`$91A7`'s reset condition (or empirically finding
  a longer cycle over which pitch does repeat) is the next step.

## D-014 — The installed IRQ handler ($4D08) serves two interrupt sources; $60A8 switches between the title-screen music player and the real-time gameplay tick

> **Disambiguation (D-014 is used twice — D-192).** This is the **2026-07-02** entry. The other is **2026-07-10**, "Live-boot findings: random opening death; timed title; MCP port sw…". Citations of `D-014` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-02
- **Finding:** the audio work needed to resolve an open question a prior pass's static
  read of `out/ALIEN.asm` left unsettled: is the `$4D19`-rooted SID
  gate-retrigger path unreachable dead code (since `$60A8` looked permanently
  nonzero once gameplay starts), and is there possibly a *second* IRQ-vector
  install elsewhere that this pass's trace missed? Both are now resolved:
  - **Only one vector install exists.** An exhaustive grep of `out/ALIEN.asm`
    for `STA $0314`/`STA $0315` finds exactly one write site — `$4DBB`/`$4DC0`,
    inside `$4DB8` (init A). Nothing else in the program touches the KERNAL
    IRQ vector.
  - **That one handler services two interrupt sources.** `$4DB8` enables the
    VIC raster IRQ (`$D01A=$81`) but never touches CIA-1's own interrupt mask,
    so the KERNAL's default ~60 Hz CIA-1 jiffy-timer IRQ stays enabled too —
    both funnel through the one installed vector. `$4D08`'s `LDA $D019; AND
    #$81; CMP #$81; BEQ $4D58` is exactly a raster-vs-CIA dispatch (not a dead
    check): a raster IRQ shows the masked bits set → branches to `$4D58` (a
    two-phase sprite raster split, audio-silent); a CIA jiffy IRQ does not set
    those `$D019` bits → falls through to `$4D11`, which forks on `$60A8`.
  - **`$60A8` is a phase switch, not a "gameplay is running" flag.** Init B
    (`$8FFC`, run right after `$4DB8` at boot) sets it to 1. The *only* other
    writer, `$702D`, sets it to 0 — and tracing that write's caller resolves
    the earlier "is this the win/lose screen?" open question: `$702D` is
    inside a routine entered from `$5F44`/`$5F56` (in the code around the
    documented main dispatch `$5ECE`), reached when a game-state byte at `$91`
    equals `$FA` or `$F3`. That call site first copies a byte table at `$5F59`
    into screen RAM (`$05E0`/`$065C`/`$06AC`/`$07C0`) — decoded as C64 screen
    codes (bit 7 = reverse video, `1..26 = A..Z`), the table spells **"GAME
    SELECTION" / "CONTROL"** (verified by direct byte extraction from the PRG,
    not a `[?]` guess). So `$7013` (which `$702D` is inside) is the **mode
    ("Game Selection") screen's transition into real gameplay** — not a
    win/lose screen as first hypothesized — matching GAME_SPEC §9's
    `[I]`-tagged front-end. It clears the title sprites, sets `$60A8=0`,
    re-runs `$4DB8` (fresh raster-IRQ setup) and seeds the SID directly via
    `$4DF0`.
  - **So the two SID players are sequential phases, not competing
    hypotheses.** From `SYS 16384` through the Game Selection screen,
    `$60A8=1`: every CIA jiffy runs `JMP $9039`, a second, separate 8-step
    two-voice music player (voices 1+2 sawtooth through the filter; voice 3 is
    muted via 3OFF and exists only so its envelope readback, `$D41C`→`$D416`,
    modulates the filter cutoff each jiffy) — **this is the memorable intro
    tune**, confirmed reachable and is what the audio work emulates. Once the player
    picks a mode and `$702D` clears `$60A8`, the CIA-jiffy branch instead
    falls to `$4D19`'s `DEC $6579` 8-jiffy counter → the four game-update
    routines (`$4EE8`/`$4F19`/`$4F52`/`$4FCB`) the behaviour spec already documented as the
    real-time ~6 Hz gameplay tick (D-008, unaffected by this finding) — plus
    the gate-retrigger heartbeat SFX (`$4D37`/`$4DD7`) that was flagged as
    possibly-dead. It is reachable; it just doesn't run during the title/mode
    screen, which is exactly the phase this game-state variable was designed
    to gate.
- **Action:** none further — this *is* the branch-ambiguity question the the audio work
  pass brief asked to resolve if possible; resolved entirely via static
  trace (grep + byte-level table decode), no live debugger needed. The the audio work
  driver (`alien_remake/audio/intro.py`) reproduces the title-phase
  configuration exactly (calls the real `$4DB8` then `$8FFC`, then drives
  `$4D08` once per simulated CIA jiffy) and documents the same trace in its
  module docstring so the two write-ups don't drift. No planning pass
  reorder — the behaviour spec's real-time timing model (D-008) is confirmed, not revised.

## D-012 — `--awake-crew`'s bare `0` default silently decoupled from the real crew

> **Disambiguation (D-012 is used twice — D-192).** This is the **2026-07-02** entry. The other is **2026-07-09**, "Alien AI is a weighted random walk over 5 surface + 4 duct route t…". Citations of `D-012` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-02
- **Finding:** the Alien work traced `awake_crew` (the oxygen driver) end-to-end and found
  `alien_remake/__main__.py`'s `--awake-crew` flag defaulted to `0`, but
  `Simulation.__init__` auto-populates all seven crew via `default_crew` with
  `CrewMember.awake=True` whenever the caller doesn't supply a crew dict — the
  real code path `python -m alien_remake` (no flag) always takes. So a real
  playthrough would show 7 crew rendered awake in hypersleep, yet `state.oxygen`
  never dropped (`awake_crew` stuck at its `0` default) — the TOOH budget was
  cosmetically present but functionally dead. Confirmed via
  `python -m alien_remake --headless 30`: before the fix, `oxygen=7500` after 30
  ticks; after, `oxygen=7290` (7 crew × 30 ticks × `OXYGEN_PER_AWAKE_PER_TICK`).
- **Action:** fixed in the same pass as part of its oxygen/TOOH scope:
  the flag now defaults to `None` and, when unset, `Simulation.state.awake_crew`
  is set from the real starting roster's `awake` count post-construction
  (DECISIONS D-013 #3). No test previously covered `__main__.py`'s runtime
  behavior (only headless core tests existed), which is why this went unnoticed
  since the crew/PCS work — no further action; the fix is verified by the headless run
  above, not a new automated test (`__main__` has no test file by convention).

## D-013 — An active auto-spawned Alien can perturb small-ship PCS/movement test fixtures

> **Disambiguation (D-013 is used twice — D-192).** This is the **2026-07-02** entry. The other is **2026-07-09**, "LAUNCH NARCISSUS requires ALL alive crew aboard + Jones caught". Citations of `D-013` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-02
- **Finding:** `Simulation.__init__` auto-spawns the Alien (`spawn_alien`)
  exactly like it auto-populates crew/items, whenever the caller doesn't supply
  one. Several tests written before the Alien work (`test_remake_crew.py`, `test_remake_items.py`)
  build a `Simulation` on a tiny hand-rolled `ShipMap` (a 4-room door chain) with
  one or two real crew members and an **unseeded** `random.Random()`, then call
  `sim.advance()` up to twice. On a plain door chain (no ducts/grilles needed),
  the auto-spawned Alien is fully reachable from any crew room, and its GAME_SPEC
  §11 #1 fear-bump-on-proximity (new in the Alien work) can nudge a "calm" crew member's
  fear above 0 within 1-2 ticks — at which point `compliance` drops slightly
  below 1.0, and with an unseeded RNG there's a small but real per-run chance of
  an unexpected DELAY/REFUSE that a test hard-coded to expect OBEY. Caught by an
  actual intermittent failure (`test_move_to_walks_one_room_per_tick_until_arrival`)
  during this pass's own test runs.
- **Action:** updated the four affected `Simulation(state=..., ship=...)`
  construction sites (in both files' shared `_sim_with_crew_at` helpers, plus two
  bespoke `GameState(...)` calls) to pass `alien=Alien(room_id=None)` explicitly,
  neutralizing the Alien subsystem for tests that are about PCS/movement/items,
  not combat — the same pattern the items work used when item validation changed `GET_ITEM`
  semantics out from under an earlier test. `tests/test_remake_alien.py`'s own
  tests use a `FixedRandom` (pins both `random()` and `choice()`) instead of an
  unseeded RNG for exactly this reason. No plan change; filed as a testing
  convention future passes adding a `Simulation` on a small custom ship should
  follow if the Alien isn't the thing under test.

## D-001 — The manual PDF is a scanned image with no text layer
- **Date:** 2026-06-25
- **Finding:** `Alien.pdf` has no extractable text; its 8 pages were rendered to
  `docs/manual/page01..08.png` and the gameplay rules transcribed by hand into
  `docs/manual/MECHANICS.md`. Re-rendering requires PyMuPDF, which is **not** a
  project dependency — a one-off authoring aid only.
- **Action:** none — `MECHANICS.md` is the working reference for Part II; no
  PDF-parsing code is needed in the toolkit.

## D-009 — The `$2000–$3FFF` VICE dumps are a static charset bank, not the map

> **Disambiguation (D-009 is used twice — D-192).** This is the **2026-07-01** entry. The other is **2026-07-09**, "Rooms take physical structural damage; shooting the Alien wrecks t…". Citations of `D-009` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-01
- **Finding:** The eight `the live captures (not published)*_2000_3ff.bin` dumps (captured in
  different game states: map, each deck, in-grille, win/lose) are **byte-identical**
  (`md5 f3d5c6e4…`). So `$2000–$3FFF` is a static charset/sprite bank loaded once —
  **not** the map screen and **not** a state-dependent map table (consistent with
  the disassembly: ALIEN entry is `$4000`, `$2000–$3FFF` is char/sprite data). The deck maps are
  drawn to screen RAM (`$0400`), which was not dumped. Automated pixel extraction of
  the maps from the deck PNGs is also unreliable: the walls use a diagonal-hatch
  texture that a per-cell density classifier can't separate from the crosshatch
  grille glyph.
- **Action:** SM's pure-data map RE **stalls** with the material on hand (needs a
  `$0400` per-deck dump or a trace of the `$4000+` map-draw routine). SM fell back
  to the sanctioned oracle **transcription** (D-010 #2) → `core/nostromo.py` +
  `the live captures (not published)nostromo_map.md`, exact grids `[?]` pending a `$0400` dump. Upside
  filed for **SG**: these dumps crack the graphics format directly (the charset
  bank SG needs). No plan reorder.

## D-010 — SG's extracted charset is byte-identical to the game's live memory

> **Disambiguation (D-010 is used twice — D-192).** This is the **2026-07-02** entry. The other is **2026-07-09**, "Endgame chain: hull-breach → dispatcher → outcome select; location…". Citations of `D-010` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-02
- **Finding:** SG extracts ALIEN's `$2000–$3FFF` graphics region from the `.nib`
  (decode → `cbmdos`/`loader` → the load-$2000 `ALIEN` PRG → first 8 KiB). That
  derived region is **byte-for-byte identical** to (a) all **eight** VICE
  `$2000–$3FFF` dumps in `the live captures (not published)$2000–$3FFF dumps/` (captured across map,
  each deck, in-grille, and win/lose states — themselves all identical, D-009), and
  (b) the `$2000–$3FFF` slice of the new full-RAM snapshots `the live captures (not published)ram.bin`
  and `everyonedeadbutparkerandjones.bin` (65 538 bytes = 2-byte load addr + 64 KiB).
  So the toolkit's derived charset/sprites **are exactly what the running game holds
  in memory**, and the bank is confirmed **static across every game state** — the
  strongest possible faithfulness check for SG's graphics. Layout: a 256-glyph 8×8
  charset in the first 2 KiB (`$2000–$27FF`), sprite data after (`$2800–$3FFF`,
  96 24×21 slots; slot boundaries a best-effort `[?]`).
- **Action:** none new for SG (done). **New reference material now on hand** for
  later work: the full-RAM `ram.bin`/`everyonedeadbutparkerandjones.bin` and the
  per-deck screen-RAM dumps `the live captures (not published){upper,middle,lower}deck_0400.bin`
  (31 746 bytes each) — these are exactly what **SM's open item** wanted (a `$0400`
  per-deck dump to upgrade the `[?]` map grids to measured data), and `ram.bin` may
  let a future pass locate the map table / crew / Alien state directly in the
  `$4000+` region. Filed as input inventory; not scoped as a task here.

## D-011 — The crew roster + order flow are confirmed by the game's CONTROL panel

> **Disambiguation (D-011 is used twice — D-192).** This is the **2026-07-02** entry. The other is **2026-07-09**, "Combat, weapon-charge & crew-state model (health/fear/insane)". Citations of `D-011` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-02
- **Finding:** `the live captures (not published)opening scenario 2.png` (the upper-deck opening) shows
  the in-game **CONTROL** panel, which verifies GAME_SPEC §4 against the game itself:
  the roster is exactly **Dallas, Kane, Ripley, Ash, Lambert, Parker, Brett** (seven,
  in that on-screen order), and the interaction is `Order:` → *pick a crew member* →
  (verb) with `indicate location` and a `display level` deck selector (Upper / Middle
  / Lower Deck). The banner "… has been killed by the ALIEN" (dead name shown
  inverse) confirms §9's already-dead opening. This resolves the §4 `[I]` on the
  roster *names/order* (the name→role pairing is still film canon `[I]`, correctable
  from the Report Monitor in the items work).
- **Action:** used directly in **the crew/PCS work** — `core.crew.ROSTER` uses this exact order;
  the PygameRenderer's crew panel + number-key selection mirror the CONTROL panel.
  No plan change. (The name→role table remains `[I]`; the items work's Report Monitor is where
  to confirm/correct it against the game.)

## D-003 — The standard DOS area (tracks 1–35) decodes 100% clean
- **Date:** 2026-06-26
- **Finding:** `decode` on `Alien (USA, Europe).nib` recovers **all 683**
  standard sectors with **every** header *and* data checksum verifying — 0
  bad-checksum sectors across tracks 1–35 (21/19/18/17 per the four density
  zones). Each track shows ~45 sync marks (one revolution + the loop tail's
  redundant copies, which the scanner dedupes by sector). The protected tail
  decodes to nothing: track 36 has a single sync but no decodable block, and
  tracks 37–40 (NO_SYNC, D-002) have no syncs at all — 95 "missing" sectors are
  entirely on tracks 36–40.
- **Action:** good news for **the D64/CBM-DOS layer** — the CBM-DOS filesystem (BAM + directory on
  track 18, which decodes fully clean) should reconstruct without gaps; partial
  results are only expected for anything the loader stashes on the protected
  tail. Reinforces the the protection analysis hypothesis that protection lives on the over-format
  tail, not the DOS area. No new task; filed as evidence for the D64/CBM-DOS layer and the protection analysis.

## D-004 — The disk holds 6 standard CBM-DOS files; `ALIEN` is the main PRG
- **Date:** 2026-06-26
- **Finding:** the D64/CBM-DOS layer's `dir`/`extract` on `Alien (USA, Europe).nib` reconstruct a
  normal CBM-DOS directory (disk name `OCG0549`, id `10`, DOS `2A`) with six
  files, all extracting **complete** (no broken chains) from the clean standard
  area:
  - `MENU`  PRG @ 17/0 — 214 bytes
  - `MENUA` PRG @ 17/1 — 658 bytes
  - `MENU1` PRG @ 17/3 — 13 846 bytes
  - `ALIEN` PRG @ 19/0 — 40 963 bytes (load address **$2000**) — the main program
  - `EXITO` PRG @ 15/2 — 1 022 bytes
  - `INSTRUCTIONS` SEQ @ 14/0 — 6 924 bytes
  The assembled `.d64` is a perfect 174 848-byte standard image (D-003). Note: the
  directory entries' *size-in-sectors* field is `0` for every file (the disk was
  mastered/cracked that way), so file lengths come from following the sector
  chain, not that field — which the extractor already does. The disk name
  `OCG0549` looks like a duplication/serial label rather than the game's title.
- **Action:** good news for **the loader extraction — Extract & disassemble the boot/loader**: there
  IS a standard DOS file chain to follow (`MENU`→`MENUA`/`MENU1`→`ALIEN`), so the loader extraction
  can start from the extracted PRGs (`out/<stem>_files/`, DECISIONS D-006) rather
  than only from raw decoded tracks. `ALIEN.prg` (load $2000, ~41 KB) is the
  obvious main disassembly target; the `MENU*` files are the visible load chain.
  No new task — filed as the input inventory for the disassembler, the loader extraction and the protection analysis. No plan reorder.

## D-005 — The boot file is `MENU` (load $032C), not the main `ALIEN` PRG
- **Date:** 2026-06-26
- **Finding:** the loader extraction's `disasm --boot` confirms the file `LOAD"*",8,1` runs is the
  **first directory entry, `MENU`** — a tiny 214-byte PRG that loads to **$032C**
  (inside the page-3 area, above the standard tape/RTS buffer), 141 instructions
  + a couple of `.byte` bytes. It is *not* `ALIEN` (the 41 KB main program at
  $2000, which D-004 flagged as the main disassembly target). So the visible load
  chain starts `MENU` → (menu screen / `MENUA` $CD70, `MENU1` $0801) → `ALIEN`
  $2000. The boot disassembly opens with `SEC` / a `.byte $03` / `ROR $FE` then
  the usual KERNAL setup (`JSR $FF90`, `JSR $FDA3`, `JSR $E518`…), consistent with
  a small loader/menu stub rather than the game itself.
- **Action:** none new — the raw disassembly (`out/MENU.asm`) and the descriptive
  load-chain report (`out/load_chain.txt`) are the the loader extraction deliverables; *interpreting*
  how `MENU` pulls in the rest (and any custom raw-track reads the protection
  uses) is **the disassembly** (commented listing) and **the protection analysis** (protection). Filed as the entry
  point for both.

## D-009 — Rooms take physical structural damage; shooting the Alien wrecks the room

> **Disambiguation (D-009 is used twice — D-192).** This is the **2026-07-09** entry. The other is **2026-07-01**, "The `$2000–$3FFF` VICE dumps are a static charset bank, not the map". Citations of `D-009` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-09
- **Finding:** The ship models **per-room structural damage** with two 20-entry
  tables — `$653F,X` (raw accumulator) and `$651C,X` (stage 0/1/2) — driven by
  `damage_room ($5581)`. **The Alien passively damages whatever room it occupies**
  (`$8ED0 INC $653F,X`, X = alien location `$7935`, +1/tick). **Weapons fire in a
  room adds a large chunk** — `$4A95` +15 and `$4AFD` +6 to the fight room
  (`$457F`) — which confirms the user's Alien-acid-blood intuition: shooting the
  creature raises that room's structural damage. Each bump prints "WARNING.
  STRUCTURAL DAMAGE TO <room>", flashes the border, and plays a damage SFX
  (`$03E8`). Once a room's accumulator passes a threshold (`#$05` on the +15 path,
  `#$0E` on the +6 path) or room `$14` is hit, the code does `JMP $5D17`
  (`hull_breach`, a lose trigger). Destroyed rooms have their object-table entries
  `$82E3,X` set to `$C8`.
- **Action:** advances **R-27** (`todo.md`) to `[~]`; full trace in
  `docs/re/DISASSEMBLY.md §8.6`; symbols added to `docs/re/alien.sym`. Remake
  (deferred, disassemble-first): each room needs a damage accumulator; Alien
  presence and weapon use raise it; threshold → hull breach. `$5D17` breach effect
  and the remaining malfunction strings tie into **R-28**.

## D-010 — Endgame chain: hull-breach → dispatcher → outcome select; location $22 = "into space"

> **Disambiguation (D-010 is used twice — D-192).** This is the **2026-07-09** entry. The other is **2026-07-02**, "SG's extracted charset is byte-identical to the game's live memory". Citations of `D-010` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-09
- **Finding:** Mapped the full endgame path. `hull_breach ($5D17)` runs a
  decompression visual, kills the crew (`$7D45` writes), sets result flags
  `$64CF=1`/`$657B=1`, and `JMP $6412` (`endgame_dispatch`). `$6412` blanks the
  screen, calls `select_outcome ($60A9)` + `$6598`, prints a prompt, waits for a
  keypress (`$C5`), then re-inits toward the menu. `$60A9` chooses one of **six
  ending strings** — "THE ALIEN IS DEAD" (`$6372`), "…EGGS ARE UNLEASHED UPON THE
  PLANET" (`$6383`), "THE NARCISSUS RETURNS TO EARTH" (`$63BA`), and the `$6314`
  Nostromo endings (BACK TO EARTH / RETURNS / IS DESTROYED) — plus a **Competence
  Rating %** (`$6411`, drawn via `compute_competence $6270`). Selection keys on
  `$64CF`, survivor index `$64C3`, the Alien's `$7D45` state, and its location
  `$7935`. **Key data fact: location `$22` = ejected into space / off-ship** — the
  game's crew-kill loops all exclude `CMP #$22`, i.e. anyone at `$22` is safe
  (the Narcissus/airlock escape, matching the film's ending).
- **Action:** advances **R-28** to `[~]` (chain + strings confirmed); full trace
  in `docs/re/DISASSEMBLY.md §8.7`; 10 symbols added to `docs/re/alien.sym`
  (now 130). Remaining `[?]`: the exact flag→string/score polarity, to be pinned
  by a live trace of two real endings (R-28).

## D-011 — Combat, weapon-charge & crew-state model (health/fear/insane)

> **Disambiguation (D-011 is used twice — D-192).** This is the **2026-07-09** entry. The other is **2026-07-02**, "The crew roster + order flow are confirmed by the game's CONTROL p…". Citations of `D-011` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-09
- **Finding:** Traced `resolve_attack ($4940)` (crew attacks Alien) and the crew
  status tables. **`$7D45` is one per-character table with split semantics:**
  index `[0]` = **Alien accumulated damage counting UP, dead at `$32`=50** (`INC
  $7D45` on a hit → `JMP $6412` at 50); indices `[1..7]` = **crew health** where
  `< 2` = incapacitated ("WOUNDED"/"LOST"; every actor loop guards `CMP #$02 /
  BCC skip`). This resolves the earlier polarity confusion — the endgame's `LDA
  $7D45 / CMP #$32` picking "THE ALIEN IS DEAD" (`$6372`) is the same test.
  **Weapon charge:** `resolve_attack` reads `tbl_weapon_charge $4B37,X`; at 0 it
  prints the "…IS EXAUSTED/EMPTY/SMASHED" line instead of a hit (resolves R-24 —
  lasers/extinguishers/trackers have finite charges). **Fear:** `tbl_crew_fear
  $7D55,Y` is 0=calm, **capped at 10**; `raise_crowd_fear ($4CE8)` bumps it for
  the ≤3 co-located crew in `$4C3C` (crowding). Behaviour gate `$52C0` fires a
  panic branch on **fear>0 AND health≥2** — a soft perturbation, not a hard obey
  gate. Status strings `$7CE8`/`$63E0`: O.K./WOUNDED/LOST/IS INSANE/SURVIVORS.
- **Action:** advances R-23, R-24 (→ resolved) and the R-28 polarity; full trace
  in `docs/re/DISASSEMBLY.md §8.8–8.9`; 9 symbols added (`alien.sym` now 142).
  Remake: model Alien damage 0→50, crew health with a <2 incapacitation floor,
  finite weapon charges, and fear 0..10 rising on crowding/attack/corpse/ducts.

## D-012 — Alien AI is a weighted random walk over 5 surface + 4 duct route tables

> **Disambiguation (D-012 is used twice — D-192).** This is the **2026-07-09** entry. The other is **2026-07-02**, "`--awake-crew`'s bare `0` default silently decoupled from the real…". Citations of `D-012` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-09
- **Finding:** `alien_choose_move ($8A36)` drives Alien movement by rolling `rng
  ($888F)` (0–15; jiffy `$A2` + seeds `$6519/$651A` through scramble table
  `$887E`). Roll **≥ $0C** → `alien_enter_duct ($89D7)` (target = current location
  `+$80`, timer `$28`); roll **0–11** selects one of **five surface route tables**
  by band — `$7A3A`(0–2), `$7A5E`(3–4), `$7A82`(5–6), `$7AA5`(7–8), `$7AC8`(9–11)
  — each 35–36 bytes, **indexed by current location**, entry = next location →
  `$64E6`, move timer `$64EE=$3C`. A parallel **duct mode** (`$8A74`) uses tables
  `$80F5/$8117/$8139/$815B` gated by `tbl_grille_access $8676` (per-room 01/00;
  only room `$0D` has no grille). Pursuit lock `$64B4` shortens the timer to `$14`
  and re-directs at a locked target. `route3/4` are near-identity (local hops);
  `route0–2` scatter the Alien — so the roll biases how far it roams.
- **Action:** advances **R-25** to `[~]`; full trace `docs/re/DISASSEMBLY.md
  §8.10`; 10 symbols added (`alien.sym` now 152). Remake: reproduce the 5+4 route
  tables (pure data — add to `alientools gamedata` export) and roll-banded
  selection; ducts link all rooms but `$0D`. **Pursuit trigger (closed):** the
  hunt lock `$64B4` is set at `$4CB3` when `rng < $4781`; the aggression
  accumulator `$4781` grows by `alien_damage/4` (`$7D45[0] LSR LSR`) each pass —
  **a more wounded Alien hunts harder** (escalation; pairs with the §8.6
  acid-blood room damage). So attacking the Alien both damages the room and makes
  it more aggressive.

## D-013 — LAUNCH NARCISSUS requires ALL alive crew aboard + Jones caught

> **Disambiguation (D-013 is used twice — D-192).** This is the **2026-07-09** entry. The other is **2026-07-02**, "An active auto-spawned Alien can perturb small-ship PCS/movement t…". Citations of `D-013` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-09
- **Finding:** Traced the LAUNCH NARCISSUS win from the code (confirming the
  user's hints). The handler `launch_narcissus_check ($5B95)` runs a loop
  (`$5B9E`–`$5BE4`) over crew 1..7 and **refuses the launch if any *alive* crew
  member is not at location `$22`** (the SHUTTLEBAY / Narcissus evac bay),
  showing **"MOTHER REFUSES LAUNCH"** (`$5B80`). If all are aboard it calls
  `check_mother_refuses ($5B1F)`, which requires **Jones (the CAT BOX object,
  `$7CC3`) to be aboard** — otherwise it draws **"GO GET JONES"** (`$5C33`) and
  refuses. Only when both pass does it fall through to `$6412` (endgame win).
  The **effective survivor cap** the user observed is emergent: the evac room's
  occupancy limit (`ROOM_CAPACITY`, D-018) bounds how many can be aboard at once,
  so with more alive crew than fit, the launch can never satisfy "all aboard".
  Also **corrected a mislabel**: `$5A6A` (called by `apply_blowlock`, sets crew
  health 0 + location `$BD`) is the **blowlock vent**, not "enter_hypersleep".
- **Action:** corrected the remake's `_launch_narcissus` to also require
  `state.jones_caught` (the "GO GET JONES" condition); added
  `test_launch_narcissus_refused_until_jones_is_caught`. The ENTER HYPERSLEEP
  effect and the OVERRIDE DETONATION win remain `[?]` (VICE_CHECKS.md) — not
  invented in the remake.

## D-014 — Live-boot findings: random opening death; timed title; MCP port swap

> **Disambiguation (D-014 is used twice — D-192).** This is the **2026-07-10** entry. The other is **2026-07-02**, "The installed IRQ handler ($4D08) serves two interrupt sources; $6…". Citations of `D-014` predate the collision being noticed, so **resolve them by subject, not by number.**
- **Date:** 2026-07-10
- **Finding:** Three live-oracle facts from clean warp-free boots:
  1. **The full game's opening death is RANDOM.** A fresh boot showed KANE dead
     (`$7935[2] == $FE`) where the user's earlier run had LAMBERT dead
     (`$7935[5] == $FE`) — two independent full-game boots, two different
     victims. The remake's `DeathVariant.FIXED` default (always Lambert) is
     therefore wrong for the full game.
  2. **The title screen auto-advances on a timer, not on fire.** Every joystick
     tap we ever sent during the title went to a dead register (see 3), yet the
     title always advanced to the selection screen — so the title/epigraph
     sequence is timed (`$7560` busy-wait + `$561C` delays), with no
     press-to-continue. The remake's "PRESS SPACE" title gate is an invention.
  3. **The MCP's joystick "port 1" is the C64's control port 2.** Injecting on
     MCP port 1 visibly drives `$DC00` (CIA1 Port A = control port 2, the port
     the game polls at `$71F2`); MCP port 2 reaches nothing. All earlier "input
     doesn't register" results used the dead port — the fix is simply
     `{"port": 1}` in `vice_joystick_*`.
  4. (Bonus, one observation:) BRETT read `$7935[7] == 6` (COMMDCENTR) on this
     boot — the static table has 0 ("set at init") — so Brett's start room is
     assigned at init; needs a second look before changing the remake.
- **Action:** remake default death variant flipped to RANDOM (full game);
  title-screen advance to be made timed (R-30); all joystick scripts switched to
  port 1. `docs/re/VICE_CHECKS.md` updated.

## D-008 — The game is real-time (frame-driven raster IRQ), not turn-based
- **Date:** 2026-06-26
- **Finding:** the behaviour spec pinned the timing model (R-003) from the code. `ALIEN`'s raster
  IRQ **handler is `$4D08`** (vector `$0314/$0315`, raster line `$61`, enabled via
  `$D01A`). Every frame it decrements a counter (`DEC $6579`) and, on reload `#$08`
  (≈ **every 8 frames**), calls four **game-update routines** `$4EE8`, `$4F19`,
  `$4F52`, `$4FCB` that advance world state **regardless of player input** — i.e.
  the simulation is **continuous real-time**, ≈ `frame_rate/8` (~**6 Hz PAL** /
  7.5 Hz NTSC). A second counter (`DEC $64B7` → `STA $D404`) drives a SID tick; the
  handler is a split-raster doing sprite multiplexing (`$07FC/$07FD`,`$D009/$D00B`,
  line `$61`/`$FA`). This matches the manual's "crew act semi-independently in real
  time / give an order and move on".
- **Action:** resolves **R-003** (timing model). Recorded authoritatively in
  `docs/spec/GAME_SPEC.md` §2. The remake core must be a **headless fixed-tick state
  machine** at ~6 Hz. The exact per-routine cadence inside the tick
  (`$4EE8/$4F19/$4F52/$4FCB` = crew vs Alien vs oxygen) is a calibration `[?]` for
  the Alien work, not needed for structural work.

## D-007 — This is an unprotected 1985 Green Valley/ShareData re-release; ALIEN entry is $4000
- **Date:** 2026-06-26
- **Finding:** the disassembly traced the full load chain (`docs/codemap.md`). (1) The menu
  `MENU1` is **BASIC** (load $0801), not 6502 — by **"GREEN VALLEY PUBLISHING INC.,
  A DIVISION OF SHAREDATA, INC."**, "MODIFIED BY SCOTT BRUNS", and it tells the user
  to "MAKE A BACK-UP COPY OF THIS DISKETTE" — a deliberately **unprotected budget
  re-release** of the 1984 Mind Games original. (2) The only "protection" is a soft
  DOS check (open command channel + named file, require error `"00"`), done in both
  `MENUA` (ML) and `MENU1` (BASIC); **no `M-W`/`M-E`/`M-R` drive code, no track
  36–40 access** anywhere — the the protection analysis no-sync tail is an unenforced vestige (resolves
  `docs/protection.md` §5). (3) Load chain: `MENU`($032C)→`MENUA`($CD70, resident
  disk-check)→`MENU1`(BASIC title/menu)→ auto-types `LOAD"ALIEN",8,1:CLR:SYS16384`
  (or `EXIT*`→`EXITO`). (4) **ALIEN's entry point is `$4000` (`SYS 16384`), not
  `$2000`**: `$2000–$3FFF` is char/sprite **data**, code starts at `$4000`
  (init `$4DB8`/`$8FFC`/`$5DEB` → main dispatch `$5ECE`). (5) `$4DB8` installs a
  **raster IRQ** ($0314/$0315, $D012, $D01A) driving a **3-voice SID player**
  ($D400–$D41C); the game reads the **joystick on port 2** ($DC00 @ $71F2).
- **Action:** corrects D-004's "ALIEN $2000 is the main disassembly target" → entry
  is $4000, data below it (PLAN Planning Debt). Feeds **the behaviour spec**: entry/init/loop
  skeleton, data/code split, and I/O surface are fixed; the per-frame raster IRQ is
  evidence the timing model is *at least partly real-time* (R-003). Feeds **the audio work**:
  SID player is at $4DB8. The deep game logic ($5ECE main loop, PCS, crew, Alien AI,
  win conditions across ~$4000–$C000) is **not** fully mapped here — that is the behaviour spec's
  bridge work (`docs/codemap.md` §4.4/§5).

## D-006 — The protection is an over-format no-sync tail (36–40), not killer/weak/density
- **Date:** 2026-06-26
- **Finding:** the protection analysis's analysis (`docs/protection.md`) classifies the copy
  protection from existing `inspect`/`decode` output. The game is a **fully
  standard** 35-track CBM-DOS disk (683 sectors, **0 bad checksums**); the
  protection lives **only** on an over-format tail: track 36 = 1 sync / 0
  decodable sectors (zone-2 density), tracks 37–40 = `NO_SYNC` (0 syncs). This is
  an **extra-track + no-sync presence check** — the disk is authenticated by the
  physical shape of tracks 36–40, which a DOS copier / 35-track imager can't
  reproduce. Specifically **ruled out**: killer tracks (no `BM_FF_TRACK` anywhere;
  `NO_SYNC` is the opposite of all-`$FF`), density/bit-rate anomalies in the data,
  and bad/extra sectors. Weak-bit protection is **not evidenced and not
  excludable** — a single-pass `.nib` is one read and physically can't reveal
  unstable bits. The boot stub `MENU` contains **no drive-side protection code**
  (plain KERNAL `LOAD`), so any software check lives deeper (`MENU1`/`MENUA`/
  `ALIEN`) — or the tail is a vestige on this possibly-partially-cracked image.
- **Action:** the *protection asset* is confirmed and documented; the *check
  mechanism* is a hypothesis handed to **the disassembly** (4 open questions in
  `docs/protection.md` §7 — find the code that reads the tail, decode track 36's
  lone sync at file offset `0x046100`, look for `M-W`/`M-E` drive uploads, find the
  failure branch). No plan reorder. Optional `anomalies`/`protect` convenience
  subcommand logged in `todo.md` Unsorted, not built (existing tools already
  detect everything).

## D-024 — Morale word selection is decoded: table location, formula, and why passive fear-testing fails
- **Date:** 2026-07-11
- **Finding:** Traced `fear_band ($7DC5)`, the routine that picks the
  CONFIDENT…BROKEN word shown on the crew status line. The word table lives at
  **`$7D13`**, not `$7CEA` (that address is the *health*-status table
  "O.K./WOUNDED/COLLAPSED/DEAD" immediately before it in the same string
  blob — byte-verified in `docs/re/ALIEN.annotated.asm`). Stride is 10 bytes;
  the five words sit at `$7D13`(CONFIDENT)/`$7D1D`(STABLE)/`$7D27`(UNEASY)/
  `$7D31`(SHAKEN)/`$7D3B`(BROKEN) — confirming the remake's `MORALE_BANDS`
  word order was already correct. The selector formula itself was not: it
  reads `$6571,Y` (a per-crew mirror written by `order_gate_update $4843`,
  not always equal to raw `$7D55,Y`) and computes `idx = 4 - value` for
  `value < 5`, else `idx = 0` — meaning **fear 0/1/2/3 each select a distinct
  word, but every value from 4 through the 10-cap collapses onto the SAME
  word** (idx 0 = CONFIDENT). The remake's even-5-way-split-of-0..10 model is
  wrong in a specific, now-provable way, not just "probably wrong."
  Separately, traced why a FV-2e live test found no fear spike from a nearby
  crew death: every stressor in the code is **room-local** —
  `raise_crowd_fear ($4CE8)` only walks a same-room crowd-group list
  (`$4C3C`), and the attack/corpse stressors in `init_char_turn`
  ($47B3-$47E9) are gated on matching the room being processed. A death
  elsewhere on the ship cannot move a non-co-located crew member's fear.
  **Follow-up (same day, user question: "is the update delayed?"):** yes,
  plausibly, and the mechanism is now traced. `fear_band` is only called
  from inside `init_char_turn`'s per-character turn loop, and only fires
  when that loop's currently-processed crew slot (`$64B1`) matches the
  panel's currently-displayed crew (`$64FB`). The loop advances through crew
  via adaptive branchy logic (seeded by co-located-crew scan results earlier
  in the same pass), not a fixed round-robin — so `$6571`/the displayed word
  only refreshes when the rotation happens to land on the crew member being
  viewed, while raw `$7D55` can keep changing every tick regardless of whose
  turn it is. This is a real, code-supported staleness window that plausibly
  explains the fear=3/CONFIDENT discrepancy as a stale snapshot from when
  fear was still 4, rather than a decode error. Exact refresh cadence is
  adaptive, not a fixed tick count — still `[?]`.
- **Action:** `constants.py`'s `MORALE_BANDS` comment rewritten with the full
  decode (table addresses + formula + the room-locality constraint + the
  update-delay mechanism); `todo.md`'s FV-2.3 entry sharpened to a precise,
  cheap next test (read fear 0 or 1, not high fear — high fear is provably
  uninformative — and poll `$6571` against raw `$7D55` repeatedly, not once,
  to see the rotation catch up before trusting a reading). No `src/`
  behaviour change — `MORALE_BANDS` itself is unchanged pending that live
  read.
- **Resolution (same day, 2026-07-11, FV-2g):** the predicted live read
  arrived. A crew-menu read caught **Ripley with `$7D55=3` and `$6571=3` in
  sync (no lag)**, and her displayed word was **"STABLE"** — exactly matching
  the formula (`idx=4-3=1=STABLE`). At the same instant, **Kane showed
  `$7D55=4`/`$6571=6` and Brett showed `$7D55=3`/`$6571=6`** — direct, live,
  simultaneous confirmation that `$6571` really does diverge from raw fear
  for other crew during normal play, not an artifact of the read method.
  This closes the loop: the formula is correct; FV-2b's earlier "fear=3 ->
  CONFIDENT" read was a stale-`$6571` snapshot, exactly as hypothesized.
  `constants.py`'s `MORALE_BANDS` comment rewritten to state this as
  confirmed (fear 0/1/2/3 -> BROKEN/SHAKEN/UNEASY/STABLE, fear>=4 ->
  CONFIDENT) rather than an open discrepancy. Stressor magnitudes (how much
  each stressor raises fear) remain the one open piece of FV-2.3.

## D-025 — Deck-value mapping confirmed (4=UPPER/5=MIDDLE/6=LOWER); active play is a pure timeout, not player-gated
- **Date:** 2026-07-11
- **Finding (deck mapping):** the user drove the live game's INDICATE
  LOCATION feature and screenshotted the result: AIRLOCK 1 (room 0, `$80D3`
  raw deck value `4`) displayed under the **"UPPER DECK"** header. Combined
  with the already-established `05=MIDDLE` (room-count match + live
  COMMDCENTR/`05` reads), this settles all three raw deck values:
  **`4=UPPER, 5=MIDDLE, 6=LOWER`** — confirming the remake's original,
  previously-`[?]`-flagged guess (`nostromo.py`'s `_RAW_DECKS = {4:0, 5:1,
  6:2}`) was correct all along. Room 0's identity carries no table-alignment
  risk (unlike some higher room indices, where `ROOM_NAMES`'s two "OTHER
  LIST" placeholder strings around index 17-18 create ambiguity about
  whether `ROOM_NAMES` index equals `ROOMS` room_id 1:1 beyond that point —
  not resolved here, and not needed to answer the UPPER/LOWER question).
- **Finding (Alien activation is not player-gated):** asked the user whether
  the game's fast (~1-3 min) end-of-game pacing matched their memory, and
  whether the Alien only starts moving once the player issues an order —
  they weren't sure. The decompilation (`DISASSEMBLY.md`, live-pass-2)
  already answers this directly: the opening-death screen is a **pure
  timeout** — `$8CF3` counts down, then unconditionally calls
  `begin_active_seq ($8D1A)` -> `begin_active_play ($4F90)`, setting
  `var_game_active ($64BB)=1`. Crew/Alien movement and the order-gate update
  are gated on `$64BB`, which flips to 1 regardless of any player action.
  There is no code path where withholding orders prevents active play from
  starting. (This also matches this pass's own indirect evidence: two
  separate crew deaths — Lambert, Ripley — happened during passive
  observation with zero orders issued.)
- **Action:** `docs/re/GAMEDATA.md` §1.2 and `nostromo.py`'s `DECK_NAMES`/
  `_RAW_DECKS` comment updated from `[?]` to `[C-live]`. `todo.md`'s FV-2.14
  marked fully resolved for the deck-value question (per-cell colour capture
  still open); FV-2.3's pacing postscript updated with the decompiled
  answer. No `src/` behaviour change — `_RAW_DECKS`' values were already
  correct, only the confidence/comment changed.

## D-026 — Panic-wander (`char_wander`) reuses the Alien's own route tables; the trigger is 3 distinct paths, not one
- **Date:** 2026-07-11
- **Finding:** Following up on "can the disassembly help finish these tests
  easier" (user question), fully traced `char_wander ($5203)` and its three
  callers (`$52A4-$52E3`, `$5252-$5260`, `$5265-$5291`) instead of waiting
  for a live capture. Two real, previously-uncaptured facts:
  1. **`char_wander` is not a bespoke flee routine.** It rolls the RNG and
     selects a destination room from the **same 5 roll-banded route tables
     the Alien's own movement uses** (`$7A82`/`$7AA5`/`$7AC8`, identical
     threshold bands to `ALIEN_ROUTES` in `GAMEDATA.md`/RW-6a). A panicking
     crew member takes an Alien-style random walk, not a directed escape
     toward an exit or away from danger.
  2. **There are at least 3 distinct trigger paths**, not the single "fear>0
     AND health>=2" condition `DISASSEMBLY.md`'s old one-line §8.9 summary
     implied: (a) the crew member shares a room with the Alien; (b) low
     health (`$7D45,Y < 4`); (c) a co-located, disturbed (`$7D55!=0`),
     healthy (`$7D45>=2`) *other* crew member — but only once **the Alien
     itself has taken damage `>=6`**, a precondition the old summary omitted
     entirely.
  This is a concrete instance of the "static tracing over live testing"
  approach paying off: no VICE session was needed, and the result is more
  precise than what live testing alone would likely have surfaced (the
  Alien-damage precondition is not something a player would easily notice
  from outside).
- **Action:** `docs/re/DISASSEMBLY.md` §8.9 sharpened in place (old summary
  kept, new detail appended per this project's "correct via dated addendum"
  convention). `constants.py`, `orders.py`, `crew.py` comments updated from
  a bare `[?]` to the traced detail. `todo.md`'s FV-2.11 marked
  substantially resolved (priority-among-paths and dispatch frequency still
  open). No `src/` behaviour change — panic-wander itself is still
  unimplemented in the remake (a future build pass's scope, not FV's).

## D-027 — Room-damage path selector is the harpoon, not "laser fire"; the remake was missing the harder-hitting path entirely
- **Date:** 2026-07-11
- **Finding:** `resolve_attack ($4940)`'s item-id dispatch was already fully
  decoded for Alien-wound amounts (FV-1.1), but the parallel *room-damage*
  side effect (acid spilled into the fight room, §8.6) had two known paths
  — `$4A87` (+15, breach at accumulator ≥5) and `$4AF0` (+6, breach at ≥14)
  — with no traced answer for which combat context selects which. Full
  static trace of `$49EB-$4A50` (the dispatch that funnels into each path)
  found the selector directly: **`CMP #$0C / BEQ $49F2` at `$49EB` singles
  out item id 12 — the HARPOON GUN — into the `$4A87` (+15) path; every
  other weapon (electric prod, incinerator, spanner, laser) falls through
  to the `$4AF0` (+6) path instead.** `DISASSEMBLY.md`'s existing table had
  mislabeled `$4A95` as a "laser-fire path" (a plausible-sounding guess made
  before this trace existed) — it's the harpoon, not the laser. The remake
  previously modeled only the smaller, non-harpoon path uniformly (every
  landed hit spilled the same +6), so a harpoon kill was under-damaging the
  room by 9 points relative to the ROM.
- **Action:** `DISASSEMBLY.md` §8.6 table corrected in place (mislabel fixed
  with a dated note, not silently rewritten). `constants.py` gained
  `ROOM_DAMAGE_PER_ATTACK_HARPOON = 15`; `sim.py`'s `_resolve_attack_order`
  now branches on `item_type_id == "harpn_gun"` to pick the right amount.
  `tests/test_remake_alien.py`: corrected `test_landed_attack_spills_acid_
  into_the_room` (Ripley holds the harpoon in that fixture, so the expected
  damage was wrong under the old uniform model) and added
  `test_non_harpoon_landed_attack_spills_the_smaller_amount` to cover the
  other path. 337 pass / mypy clean / smoke 0. **Still open, not attempted
  this pass:** the ROM's breach check is pre-add and per-hit; the remake's
  is post-add and global-per-tick — a real architectural gap (`todo.md`
  FV-2.6), and there's no confirmed evidence the passive Alien-corrosion
  path has its own breach gate at all.

## D-028 — The specials dispatch table is room-gated per-crew-location; ENTER HYPERSLEEP is a mislabeled routine, fully resolved and fixed
- **Date:** 2026-07-11
- **Finding:** Located the specials dispatch table that `DISASSEMBLY.md`
  had honestly flagged as un-traced ("Handler/dispatch for a chosen special
  still `[?]` — trace pending"). `specials_dispatch ($5839)` branches on a
  small action-category code (`$64D0`), and the surprising part is *how*
  that code gets set: `guard_target_alive ($56B4)` derives it from a
  **per-room lookup table `$5753,Y`**, where Y is the *acting crew member's
  own current room* — meaning which category of special is available is
  determined entirely by which room you're standing in when you invoke the
  SPECIAL menu, not by anything about which label you clicked. `$5753` is
  populated at `new_game` from a static template `$5776` (byte-dumped and
  cross-checked: room 6 = COMMDCENTR → code 1, matching the already-live-
  confirmed SCUTTLE NOSTROMO/OVERRIDE DETONATION pair — a clean, independent
  sanity check that both the room-id alignment and the dispatch model are
  right).
  Following the same table, **room 15 (CRYO VAULT) → code 3 →
  `guard_target_is_player ($5939)`**. That routine's *existing* label was a
  pre-trace guess based on its generic-looking byte pattern (it checks
  `$64FB == $64C3`, i.e. "is the acting character the current target") —
  but its actual behavior is unmistakably **ENTER HYPERSLEEP**: gated to
  self-target only, it sets a per-crew asleep flag (`STA $64D1,Y`) and moves
  the crew member's location to a sentinel value (`STA $7935,Y = $95`),
  removing them from the room grid entirely. This resolves every open
  question FV-2.9 had filed: the handler is room-gated (CRYO VAULT only,
  previously unenforced in the remake), self-target only, and its "does it
  protect the sleeper from the Alien" question answers itself once you
  realize removing them from the room grid makes every existing
  Alien-encounter check (`crew.room_id == alien.room_id`) structurally
  unable to match.
- **Action:** `menu.py`'s ENTER HYPERSLEEP entry now gated on
  `crew.room_id == "cryo_vault"`; `sim.py`'s `_set_hypersleep` now clears
  `room_id` to `None` on sleep (defended with the same room check).
  `special_options.py`'s docstring and `docs/re/DISASSEMBLY.md` §8.5
  updated with the full trace and the category-2/4/5/default partial
  mapping for the other 5 specials (BLOWLOCK confirmed at room 13/CORRIDOR
  6; BOARD NARCISSUS/LAUNCH NARCISSUS/FIGHT FIRE identified by their
  handler bodies but not fully room-pinned; SEALLOCK's code still
  unfound). `todo.md`: FV-2.9 marked resolved; FV-2.10 marked partially
  resolved (dispatch table located, 2 of 6 categories fully traced). 3
  tests updated/added in `tests/test_remake_menu.py` and
  `tests/test_remake_alien.py`. 338 pass / mypy clean / smoke 0.

## D-029 — Colour RAM capture shows the deck-map field is uniformly green, no per-glyph colour exists to recover
- **Date:** 2026-07-24
- **Finding:** `the live captures (not published)colors.bin` (a VICE colour-RAM `$D800-$DBE7`
  capture, same 2-byte-header + 40x25 format as the `*_0400.bin` screen-RAM
  captures) had been sitting uncorrelated with `deck_backdrop.py`, whose
  docstring still claimed "no color-RAM capture exists." Decoding it
  row-by-row for the top 17 rows (the ship-map + CONTROL-panel labels) shows
  the entire 30-column map field is **flat colour 5 (green) on every row**,
  regardless of which screen-code glyph occupies each cell — wall-stroke
  cells and open-floor cells alike. There is no per-glyph colour to recover;
  a single flat green genuinely is the original screen's behaviour. This
  matches the disassembly independently: `draw_deck_map_body ($73D0)` and the
  control-panel colour setup (`$7400-$7423`, `paint_map_colors $7993`) fill
  colour RAM in bulk per fixed row/column region (`STA ($ptr),Y` loops), never
  branching on the screen-code byte being painted underneath — bulk-region
  fills, not per-glyph lookups, is how the original does it too. The
  CONTROL-panel's per-band colours in the same capture (light-blue move-to,
  light-green use, light-red get/leave/special, light-grey header/status,
  white crew line) were already correctly wired in `pygame_app.py`'s
  `_BAND_COLOUR` / `render/c64.py` from an earlier pass — only
  `deck_backdrop.py`'s docstring was stale.
- **Action:** closes the "per-cell colour/marker-alignment" half of FV-2.14
  (todo.md now `[x]`, fully resolved — no live capture needed, the existing
  `colors.bin` oracle file was sufficient). `deck_backdrop.py`'s docstring
  corrected to cite this. No code change to `pygame_app.py` was needed — its
  flat `_BACKDROP_COLOR = c64.rgb(c64.GREEN)` was already the correct,
  faithful behaviour, not a placeholder simplification as its neighbouring
  module had implied.

## D-030 — SHUTTLEBAY has no special escape-pod capacity; it uses the same generic ROOM_CAPACITY=3 as every other room
- **Date:** 2026-07-24
- **Finding:** Re-examined `char_pump`'s room-capacity check (`$7226`-ish,
  already documented in `docs/re/DISASSEMBLY.md` around the `char_pump`
  section) against FV-2.13's open question ("is SHUTTLEBAY's boarding limit
  `ROOM_CAPACITY` 3, or a special escape-pod limit?"). The capacity check is
  written generically — `count X = number of OTHER chars whose location ==
  dest; CPX #$03 / BCC ok` — with no room-id comparison anywhere in the
  routine, so it applies identically to every room including the SHUTTLEBAY
  (location `$22`). D-013 already independently noted this in passing while
  tracing `launch_narcissus_check`: "the effective survivor cap the user
  observed is emergent: the evac room's occupancy limit (`ROOM_CAPACITY`,
  D-018) bounds how many can be aboard at once" — i.e. LAUNCH NARCISSUS
  requiring *all alive crew* aboard interacts with the generic 3-person room
  cap to produce a de facto "at most 3 can ever launch together" outcome, not
  because SHUTTLEBAY has its own special limit. No SHUTTLEBAY-specific
  capacity code exists anywhere in the traced routines.
- **Action:** closes FV-2.13 (todo.md now `[x]`) with no live capture
  needed. `constants.py`'s `ROOM_CAPACITY = 3` already applies uniformly in
  the remake (no per-room override exists there either), so no code change
  was required — confirms the existing model is correct.

## D-031 — Fear stressors are uniformly flat +1, and crowding only amplifies existing unease (never spooks a calm crew member)
- **Date:** 2026-07-24
- **Finding:** Re-examined every confirmed `INC $7D55,X` (crew fear) site in
  the ROM: `raise_crowd_fear`'s own increment at `$4CF9`, and the two
  scripted-event sites `$4665`/`$466E` (reached via `scripted_event_check
  $45E7`, itself gated by a per-room story-state table `$45D3`). All three
  are a plain `INC` opcode — a flat +1 — and no `ADC #$0n` (n>1) pattern for
  `$7D55` exists anywhere in the traced code, despite an active search
  (checked `alien_wound_crew $5354`, `alien_attacks_crew`'s health-DEC path,
  and `init_char_turn`'s per-character loop for a distinct "co-located with
  the Alien" bump — none found). This means the remake's previously-guessed
  `FEAR_BUMP_ALIEN_SAME_ROOM = 3` had no ROM basis; every other stressor is
  uniformly +1.
  Separately, and more significantly: `raise_crowd_fear ($4CE8)`'s per-crew
  loop is `LDA $7D55,X / BEQ skip` *before* the `INC $7D55,X / CMP #$0A` cap
  check — a crew member whose fear is currently **exactly 0** is skipped
  entirely. Crowding can only amplify already-existing unease; it cannot
  create fear from a calm baseline on its own. This directly explains
  FV-2e/FV-2f's earlier live-session null results (10+ minutes of apparently-
  satisfied crowding conditions with zero observed fear rise): if the tested
  crew's fear had already decayed to 0 by the time crowding was engineered
  (plausible, since every live observation this project has made shows fear
  drifting *down* over idle time), the real game would produce that exact
  null result too — a genuine, code-supported explanation, not a shrug.
- **Action:** `constants.py`'s `FEAR_BUMP_ALIEN_SAME_ROOM` corrected 3 → 1
  (still `[?]` on its exact opcode site, but now consistent with the uniform
  pattern rather than an unsupported guess). `sim.py`'s
  `_apply_fear_stressors` now skips crew with `fear == 0` before applying the
  crowding bump (the corpse bump is left unconditional — its own `INC` site
  wasn't separately isolated from the scripted-event sites in this pass, so
  whether it shares the zero-fear skip is still open). `tests/
  test_remake_crew.py`: the crowding test now seeds nonzero starting fear;
  added `test_crowding_does_not_spook_a_calm_crew_member`. `todo.md`: FV-2.3
  marked substantially resolved. 339 pass / mypy clean / smoke 0. No live
  VICE session used.

## D-032 — The specials room-category table fully decoded: category 6 (FIGHT FIRE) is dynamically installed by room damage, not statically assigned; SEALLOCK likely shares BLOWLOCK's category
- **Date:** 2026-07-24
- **Finding:** Fully decoded the `$5776` static template (35 bytes, copied to
  `$5753` at `new_game`, indexed by `ROOM_NAMES`'s room-index space — cross-
  checked against the 3 already-confirmed entries: room 6 COMMDCENTR=1, room
  13 CORRIDOR 6=2, room 15 CRYO VAULT=3, all landing exactly where expected).
  The full table has only **4 nonzero entries out of 35**: room 6→1, room
  13→2, room 15→3, and **room 34 (SHUTTLEBAY)→5** — every other room is 0.
  Since `specials_dispatch ($5839)` RTSes immediately when the category is 0
  (`LDA $64D0 / BNE +3 / RTS`), the other 31 rooms genuinely offer no special
  action via this table at all.
  Category **6 was not in the static table anywhere**, yet
  `specials_dispatch` has an explicit branch for it — tracing its other
  writers found why: `damage_room ($5581)`, called when a room's damage
  accumulator `$653F,X` crosses a threshold (`>=4`, and `$651C,X` — the
  displayed damage stage — is still 0), does `LDA #$06 / STA $5753,X` **for
  rooms 17-19 only** (`CPX #$11`/`CPX #$14` range-gate). Category 6 is
  **dynamically installed as a fire alarm**, not a fixed room assignment —
  confirmed by the extinguisher-handler's cleanup (`$58CF`,
  inside the category-6 charge-consumption path): once the fire is put out
  it writes `STA $5753,X = 0` (and clears `$651C,X`/`$64D0`), removing the
  special until the next fire. This is unambiguously **FIGHT FIRE**, and its
  exact trigger condition (room damage in rooms 17-19, i.e. the
  ROOM_NAMES-space rooms currently labelled 'OTHER LIST'/'OTHER LIST'/
  'ENGINE 1' — itself a hint toward resolving that old room-name ambiguity,
  since fire hazards clustering in the engine block is exactly what you'd
  expect) is now known precisely.
  **Category 4** (guessed as BOARD NARCISSUS, "noop") appears in neither the
  static template nor either of the two dynamic writers found — no room ever
  actually reaches it in this build. Downgraded from "very likely BOARD
  NARCISSUS" to "unconfirmed, possibly dead/unreachable code" — the earlier
  guess has no positive evidence, only the absence of a better one.
  **SEALLOCK still has no distinct category anywhere** despite an exhaustive
  scan of all 6 category values (1,2,3,4,5,6) and all 3 `$5753` writers. Given
  the full accounting leaves no room for a 7th category, the most likely
  resolution is the one `special_options.py` already models: SEALLOCK is the
  reverse action at the *same* category-2/room-13 dispatch as BLOWLOCK
  (`OPEN_AIRLOCK`/`SEAL_AIRLOCK`), distinguished by the panel cursor row
  (`$64E5`) rather than a separate category — not newly proven here, but no
  longer merely assumed by elimination either.
- **Action:** `docs/re/DISASSEMBLY.md` §8.5 updated with the full room-
  category table and the category-6 dynamic-write mechanism. `todo.md`:
  FV-2.10 advanced (4 of 6 categories now confidently resolved: 1, 2, 3, 5,
  6 — only SEALLOCK's exact mechanism and category 4's real purpose remain
  open). No code change — the remake does not implement FIGHT FIRE as a
  special yet (filed as future scope, not attempted this pass since it needs
  the room-damage-to-fire-alarm wiring plumbed through `sim.py`/`menu.py`
  first). No live VICE session used.

## D-033 — USE and ATTACK share one dispatcher; the net entangles (doesn't just print a message) and the tracker's "smash" does wound
- **Date:** 2026-07-24
- **Finding:** Traced `sub_char_special ($8749)` — the routine that executes
  whatever pending action was queued for a character — and found its
  default branch (anything that isn't the grille-open code `1` or the
  `$5439` code `3`) jumps straight to `$4911`, which falls directly into
  `resolve_attack ($4940)`. This means there is only **one** combat/
  item-effect dispatcher in the whole ROM, reached the same way regardless
  of whether the queued action came from the ATTACK menu option or a
  weapon-like item's USE option — resolving the remake's long-standing
  "`[?]` whether USE of a weapon attacks" note with a clean yes.
  Re-reading `resolve_attack`'s NET (id `$10`) and TRACKER (ids 6-7)
  branches byte-by-byte (having already fully mapped every other item id
  for FV-1.1/FV-2.6) turned up two real corrections to the existing docs:
  - **NET is not message-only.** `$49A2-$49A8` does `LDA $64EE / CLC / ADC
    #$50 / STA $64EE` — adds 80 ticks to the **Alien's own** move timer,
    delaying its next move (a genuine entangle effect), before
    `clear_object_at_loc2` destroys the net. The existing table only noted
    the printed message and missed this.
  - **TRACKER's "smashed" path DOES wound.** `$49B5` prints "TRACKER IS
    SMASHED", destroys the tracker (`clear_object_at_loc2`), then
    `JMP $497A` — the exact same `INC $7D45` instruction every other +1
    item (prod/incinerator/spanner) uses. An earlier pass at this trace
    wrote "no wound" and evidently missed the trailing jump; the byte-level
    re-read leaves no ambiguity about the jump target.
  Both the net and the tracker are consumed outright by this specific use
  (`clear_object_at_loc2`), distinct from the charge-based items (which
  merely decrement a counter).
- **Action:** `constants.py`: `ITEM_ATTACK_DAMAGE["tracker"]` corrected 0→1;
  added `ALIEN_NET_ENTANGLE_TICKS = 80` and `ITEM_DESTROYED_ON_ATTACK =
  frozenset({"net", "tracker"})`. `alien.py`'s `resolve_attack` now applies
  the net's entangle effect directly to `alien.timer`. `sim.py`'s
  `_resolve_attack_order` now removes the item instance (and clears
  `crew.holding`) when a destroy-on-use weapon is used. `docs/re/
  DISASSEMBLY.md`'s item-effect table corrected for both rows.
  `sim.py`'s `_resolve_use_order` docstring rewritten to state the
  USE-vs-ATTACK sharing as fact, not a guess. 5 tests added/updated. 343
  pass / mypy clean / smoke 0. No live VICE session used.

## D-034 — Ending selection fully resolved: escaping the Alien scores identically to losing to it (both 0%); only killing it can score
- **Date:** 2026-07-24
- **Finding:** Extended the earlier partial trace of `select_outcome
  ($60A9)` all the way through `compute_competence ($6270)` and its
  room-damage penalty loop (`$6231-$626E`), which the previous pass hadn't
  reached. This resolves both open questions: which flag combination
  selects which of the 4 ending strings, and why the two preset Competence
  baselines (5 and `$78`=120) seemed backwards.
  The `$6103: BNE $60DF` branch that the earlier pass flagged as
  "suspicious, possibly a tracing error" turns out to be deliberate: it
  routes any ending where the result flag is set but the Alien is not at
  the ejected-off-ship sentinel — i.e. the Alien died some other way, such
  as being aboard a scuttled ship — to the **same** "THE ALIEN IS DEAD"
  text and low (5) baseline as an ordinary wound-kill. The real polarity
  inverter is downstream: after tallying survivors, `$621D: CMP #$65(101) /
  BCC +3 / LDA #$00 / STA $6411` clamps the running Competence total straight
  to a **displayed 0%** whenever it is still >= 101 — and the lose baseline
  and the clean-escape baseline are both 120, already over that threshold
  before any survivor bonus is added. So escaping via NARCISSUS without
  killing the Alien scores an unconditional 0%, identically to losing to it
  outright. Only the two "Alien confirmed dead" endings (baseline 5) can
  ever fall under 101 and reach the real scoring math, which then adds a
  survivor tally and subtracts a ship-damage "cleanliness" penalty (summed
  room damage, capped at -70) to produce a genuine percentage. This is a
  coherent design (the score measures neutralizing the threat, not personal
  survival), not a bug — and needed no live run to determine.
- **Action:** closes FV-2.7 (`todo.md` now `[x]`) with no live capture
  needed. No code change — the remake has no Competence-Rating mechanic at
  all, so this is a pure documentation/understanding result.
  `docs/re/DISASSEMBLY.md` §8.7 rewritten with the full 4-outcome mapping
  and the clamp-to-zero mechanism.

## D-035 — Fire and structural damage are one accumulator, but the extinguisher never repairs it — the remake's repair mechanic is invented
- **Date:** 2026-07-24
- **Finding:** Read the category-6 (FIGHT FIRE) specials handler
  (`$5889-$58E2`) fully, alongside `damage_room_b ($5587)`'s exact gating
  logic on `$651C` (already partly documented, but described as "derived
  from the accumulator" — not quite accurate). Two things resolved
  together:
  1. **"Fire" and structural/acid damage ARE the same accumulator
     (`$653F`)** — there was never a separate fire counter to find.
  2. **The extinguisher never reduces `$653F`.** The FIGHT FIRE handler's
     only state writes are `$651C,X=0` (reset a one-way "damage warning
     acknowledged" latch), `$5753,X=0` (remove the special from the menu),
     and `$64D0=0` (clear dispatch) — `$653F` is never touched. Since
     `damage_room_b` only re-warns/re-installs FIGHT FIRE when `$651C==0`
     AND `$653F>=4` (`$559E: LDA $651C,X / BNE skip`), and `$653F` only
     ever grows, a room's real structural damage is **permanent** — FIGHT
     FIRE is recurring alarm-silencing, not repair. This means `$651C` is
     better described as a one-way latch than a pure function of `$653F`,
     correcting an earlier characterization in `DISASSEMBLY.md` §8.6.
  The remake's `_use_extinguisher` (`sim.py`) currently does
  `room_damage -= EXTINGUISHER_REPAIR`, modelling a repair mechanic the ROM
  does not have.
- **Action:** `docs/re/DISASSEMBLY.md` §8.6 corrected (the `$651C`
  description, plus a new subsection on FIGHT FIRE). `constants.py`'s
  `EXTINGUISHER_REPAIR` comment and `sim.py`'s `_use_extinguisher` docstring
  both flagged `[INVENTED]` with the D-035 trace. **Not yet applied to
  code** — deliberately left functioning as-is rather than ripped out,
  since a correct fix needs new per-room alarm state (the remake currently
  derives `damage_stage()` as a pure function of `room_damage`, nothing to
  latch) plus wiring FIGHT FIRE as its own room-gated SPECIAL (still
  unimplemented, D-032) — filed as a feature-sized follow-up, not a
  same-pass constant tweak. `todo.md` FV-2.12 updated. No live VICE
  pass used.

## D-036 — De-invention audit: Jones' destination-choice algorithm is unconfirmed; a stale [?] tag corrected
- **Date:** 2026-07-24
- **Finding:** Ran a full de-invention audit (per the `replica-fidelity-
  discipline` skill's periodic sweep, user request) over `src/
  alien_remake/core/*.py`, hunting for mechanics presented as fact with no
  disassembly citation. `sim.py`'s `_advance_jones()` calls
  `self.rng.choice(neighbors)` to pick Jones' next room every
  `JONES_WALK_TICKS` (5) ticks. The **timer** is a real decoded value
  (`$6586`, `GAMEDATA.md`), but the **destination-choice algorithm** has no
  citation anywhere — Jones is character slot 8, confirmed to sit *outside*
  the main crew loop's `Y=1..7` bounds (`char_pump`), so he must be driven
  by separate code this project hasn't located. A uniform random neighbor
  pick was presented in the docstring/code as if it were the confirmed
  mechanic, alongside the genuinely-confirmed timer, with no distinguishing
  flag — a real de-invention catch (a guess calcified next to a fact).
  Separately, `nostromo.py`'s module docstring still carried a stale
  ``[?]`` on the deck-value mapping ("Which raw value is the *upper* deck is
  still an assumption") that this pass's FV-2i live confirmation
  (D-025/D-029 area) had already resolved everywhere else in the file
  (`DECK_NAMES`/`_RAW_DECKS`) — just not in the top docstring, so a reader
  skimming the module summary would see stale uncertainty next to
  since-confirmed code below it.
- **Action:** `sim.py`'s `_advance_jones` docstring and the `rng.choice`
  call site both now explicitly flag the destination-choice as `[?]`
  UNCONFIRMED, distinct from the confirmed timer; `constants.py`'s
  `JONES_WALK_TICKS` comment updated to match. `nostromo.py`'s module
  docstring corrected to state the deck mapping is confirmed, matching the
  rest of the file. No functional code change for either (both correct
  mislabeling, not behaviour) — `todo.md` not updated with a new FV item
  since Jones' AI isn't part of the open FV-2 list; filed here for whichever
  future pass locates his real movement code.

## D-037 — De-invention audit: BLOWLOCK/SEALLOCK were gated on the wrong room entirely
- **Date:** 2026-07-24
- **Finding:** The same audit sweep (run in parallel via a forked agent)
  found a genuine, applied-to-code bug: `menu.py`'s BLOWLOCK/SEALLOCK entry
  was gated on `room_id in sim.ship.airlock_rooms()` — i.e. shown only
  while **standing inside** AIRLOCK 1 or AIRLOCK 2 — with no disassembly
  citation for that gate at all. This directly contradicts this pass's
  own D-032 finding (already applied elsewhere): the specials category-2
  dispatch (BLOWLOCK/SEALLOCK) is installed for **room 13 (CORRIDOR 6)
  only**. Cross-checked and confirmed by reading the handlers fully:
  `apply_blowlock ($5B04)` checks two independent per-airlock flags
  (`$5751`/`$5752`, one per side) and calls `blowlock_vent ($5A6A)` for
  each armed side, which vents a **fixed** room id (`0` or `1`, i.e.
  AIRLOCK 1 / AIRLOCK 2, loaded from `$5AD7`) — never the acting crew
  member's own room. So the real mechanic is a **remote control panel in
  CORRIDOR 6** operating on both airlocks independently, not a per-room
  contextual action — matching the real menu's 4 distinct labels
  (`BLOWLOCK.1`/`.2`, `SEALLOCK.1`/`.2`, already documented in
  `DISASSEMBLY.md` §8.5's label table) rather than the remake's single
  "BLOW LOCK"/"SEAL LOCK" contextual entry. This mechanic had **zero test
  coverage** for its menu-gating condition (only the lower-level
  `apply_special_option` effect was tested) — exactly the "no gate caught
  it" pattern this project has flagged before for other inventions.
- **Action:** `menu.py`'s `crew_entries` rewritten: BLOWLOCK/SEALLOCK now
  offered only while `room_id == "corridor_6"`, with one entry per airlock
  (`BLOWLOCK.1`/`SEALLOCK.1` targets `airlock_1`, `.2` targets
  `airlock_2`), each independently toggling based on that specific
  airlock's own `airlocks_open` state. `special_options.py`'s
  `SpecialOptionType` docstring updated with the full citation. 3 tests
  added (`tests/test_remake_menu.py`): offered only from CORRIDOR 6, hidden
  elsewhere (including inside an airlock — the old, wrong gate), and each
  airlock's label flips independently. 346 pass / mypy clean / smoke 0. No
  live VICE session used — found and fixed entirely by cross-referencing
  two already-decoded facts (D-032's category table, the grille table's
  "only CORRIDOR 6 has no grille" note) against code that had never been
  checked against either.

## D-038 — De-invention audit round 2 (byte-level citation verification): ALIEN_MOVE_TICKS was mislabeled 70, really 60; two menu band colours were unsupported
- **Date:** 2026-07-24
- **Finding:** User asked for a second, deeper audit round explicitly
  emphasizing disassembly cross-referencing. Verified a batch of
  `constants.py`'s `[C $xxxx]` citations byte-by-byte against
  `docs/re/ALIEN.annotated.asm` (`ALIEN_DUCT_THRESHOLD`, `ALIEN_PURSUIT_TICKS`,
  `AGGRESSION_DAMAGE_DIVISOR`, `ROUTE_BAND_BOUNDS` + its 5 table addresses,
  `ALIEN_DAMAGE_TO_KILL`, `ROOM_DAMAGE_PER_ATTACK_HARPOON`, `JONES_WALK_TICKS`
  all checked out exactly), plus a forked-agent pass covering the rest of
  `constants.py` and the `render/*.py` fidelity claims. Two real problems
  found:
  1. **`ALIEN_MOVE_TICKS = 70` was citation drift, not a confirmed value.**
     `GAMEDATA.md` (and this constant, inherited from it) cited `$6581` as
     "the compass move is 70." Byte-verified `alien_choose_move ($8A36)` —
     the actual per-action dispatcher — directly: every one of its 5
     surface-move route-table branches converges on `$8A47`, which loads
     the timer with a **literal `LDA #$3C` (60)**; `$6581` is never read
     anywhere in this routine. `$6581` (confirmed = byte `$46` = 70) is
     instead read at `$8AAB`, inside a **different** routine, `alien_ai
     ($8A74)` — the Alien's *in-duct* dispatcher, called only once already
     hidden, which rolls again and picks a duct-neighbor table
     (`$80F5`/`$8117`/`$8139`/`$815B`) for duct-to-duct travel. So `70` is
     real ROM data, just attached to the wrong mechanic: it's the
     duct-to-duct movement timer, not the general/surface one. The math
     corroborates this independently — 60 ticks / `TICK_HZ`(~6.67) ≈ 9.0s,
     matching this project's own earlier live observation ("the Alien moves
     ~once per 9 seconds") far better than 70 ticks (~10.5s) does. The
     remake's current duct model (`_begin_action`) is a simplified "hide in
     the same room for `ALIEN_DUCT_TICKS`(40), then re-emerge" — it does
     not simulate the duct-to-duct network `alien_ai` actually walks, so
     there is currently no code path the real `70`/`$6581` value applies
     to; a real, filed gap, not silently dropped.
  2. **Two CONTROL-panel menu-category colours were presented as "read from
     the real colour RAM" with no actual support.** `pygame_app.py`'s
     `_BAND_COLOUR` set `GET=YELLOW`, `LEAVE=ORANGE`. Decoding the full
     `colors.bin` capture (rows 1-16, columns 30-39 — the order-menu band
     region) shows exactly four colours present anywhere in that range:
     light-blue (rows 1-8), light-green (row 9), white (row 10), light-red
     (rows 11-15) — **yellow and orange never appear** in this region at
     all (they only exist in the unrelated bottom status-line rows 21-24,
     which the code already correctly uses elsewhere via `_STATUS_BANDS`).
- **Action:** `constants.py`'s `ALIEN_MOVE_TICKS` corrected 70 → 60, full
  citation trace added; `alien.py`'s module docstring and
  `tests/test_remake_alien.py`'s pinned assertion + module docstring
  updated to match (the raw `70`-at-`$6581` fact itself is untouched and
  still correctly asserted by `tests/test_gamedata.py`, which tests the
  Phase 1 toolkit's raw byte decode, not this semantic label —
  `gamedata_snapshot.py` is a generated file and was deliberately NOT
  hand-edited; `GAMEDATA.md`'s stale note also left as-is since fixing the
  upstream `alientools` decoder's own labeling is out of scope for this
  remake-focused pass). `pygame_app.py`'s `_BAND_COLOUR` corrected: GET and
  LEAVE now LIGHT_RED (the only additional real colour found in the
  capture), with an honest note that their *specific* colour still isn't
  independently confirmed (the capture doesn't isolate a moment with
  GET/LEAVE visible) — best-supported value, not a fully closed trace. 346
  pass / mypy clean / smoke 0. No live VICE session used — every finding
  came from decoding already-captured data (`colors.bin`) or re-reading
  already-classified disassembly more carefully.

## D-039 — R-01: the game's ASCII->screen-code mapping decoded and rendered; two label-table assumptions (period, digits) disproven by actually looking at the output
- **Date:** 2026-07-24
- **Finding:** Started R-01 (render UI text through the game's own charset
  instead of `pygame.font.SysFont`). Built an ASCII->screen-code table by
  cross-referencing multiple already-known decoded strings as a Rosetta
  stone (`the live captures (not published)upperdeck_0400.bin`'s "CONTROL"/"order:"/"Dallas"/
  "Upper Deck", `tbl_specials_menu ($57A0)`'s "NOSTROMO"/"BlowLock.1"/
  "SealLock.2"/etc.): lowercase a-z = codes 1-26, uppercase A-Z = the same
  code with the reverse-video bit set (`|0x80`), space = `$A0`, colon =
  `$1C` — confirmed correct by rendering "Dallas Kane Ripley" through the
  loaded charset and reading the output image, not just reasoning about
  byte values.
  Two more characters were *assumed* from their position in the label table
  (`$1B` sitting between "BLOWLOCK" and "1" → assumed period; the trailing
  digit bytes → assumed standard PETSCII `$30`-`$39`) and then **disproven
  by actually rendering them**: `$1B` renders as an unrelated hash/lattice
  shape, and the assumed digit codes render as graphic-tile noise, not
  numerals. A search of the neighbouring code ranges (`$1B`-`$3F`) found no
  plausible digit shapes either — the real digit glyphs are somewhere else
  in the 256-entry charset, not yet located. This is exactly the kind of
  mistake reasoning-from-bytes-alone can make and rendering-and-looking
  catches — the project's own UI-testing discipline ("start the
  dev server and use the feature... before reporting the task as complete")
  paid for itself directly here.
- **Action:** `render/pygame_app.py`: added `_ASCII_TO_SCREEN_CODE` (letters
  + space + colon only — period and digits deliberately left unconfirmed),
  `_render_c64_text`/`_c64_or_sysfont` (real charset when every character
  is confirmed, else `SysFont` fallback — never a guessed glyph). Wired
  into `_blit_center`/`_blit_at`/`_blit_paragraph`/`_draw_option_key`/
  crew-name labels/the CONTROL-panel entries/the status line/the Alien "X"
  and Jones "j" map markers (the ~9 call sites `todo.md`'s R-01 entry
  named). 4 tests added in `tests/test_remake_pygame_input.py`. 350 pass /
  mypy clean / smoke 0. Visually verified via headless SDL-dummy screenshots
  of the selection/welcome/notice/play screens (not just unit-test
  assertions) — crew names, "CONTROL"/"ORDER:", specials labels, and room
  names now render in the game's own blocky pixel font; any string with an
  unconfirmed character (percentages, "O.K.", "CONTROL:1") cleanly falls
  back to the previous SysFont rendering with no visual corruption.
  **Still open (R-01 not fully closed):** the real digit glyphs and period
  glyph remain unlocated — a real gap, filed rather than guessed a second
  time.

## D-040 — R-05: the Alien's real sprite is a 4-frame pulse cycle, single-colour, not the 16-frame multicolor walk-cycle the roadmap assumed
- **Date:** 2026-07-24
- **Finding:** Traced `update_1 ($4EE8)`, the Alien's own sprite-animation
  IRQ routine (gated on `var_game_active $64BB`). `tbl_alien_anim ($4EDC)` =
  `(0,1,1,2,2,3,3,2,2,1,1,0)` — each entry is a frame **value** (0-3, not a
  distinct animation state per table slot), added to sprite pointer base
  `$A0`. So there are only **4 distinct sprite frames** (pointers
  `$A0`-`$A3`), ping-ponged 0→1→1→2→2→3→3→2→2→1→1→0→repeat — a pulse/
  breathing cycle, not the "16-frame walk-cycle" the old roadmap text
  ("Alien sprite frames slots 0-15") implied. Cross-checked the
  pointer-relative sprite indexing scheme against `_PORTRAIT_SLOTS[0]=29`
  (pointer `$BD`, matching `$07F8`'s known first portrait byte from an
  earlier pass) — confirms `TileSet.sprites[i]` = pointer `$A0+i`
  throughout this codebase, so the Alien's 4 frames are exactly
  `sprites[0..3]`.
  Also resolved whether R-03 (multicolor sprite decoding) blocks this: it
  doesn't. `main_dispatch ($5ECE)` — reached on the selection screen, after
  the title — is the **last** code anywhere in the disassembly to touch
  `$D01C` (the VIC sprite-multicolor-enable register), and it clears it to
  0. No code between there and `begin_active_play ($4F90)` re-enables it,
  so the Alien's play-screen sprite is confirmed single-colour.
- **Action:** `render/pygame_app.py`: added `_ALIEN_SPRITE_FRAMES`,
  replaced the red "X" text marker with `_blit_sprite` cycling through the
  real frames (falls back to the old "X" when no tileset is loaded). 2
  tests added. Verified visually via a headless SDL-dummy screenshot — a
  genuinely alien-esque angular silhouette now appears instead of a letter.
  **Still open:** the exact VIC colour register feeding the Alien's
  specific sprite channel (one of channels 4-7, enabled via `$D015=$F0` at
  `begin_active_play`) wasn't traced this pass — kept the pre-existing
  placeholder red, `[?]`. `todo.md`'s R-06 (Jones sprite) was checked in
  passing: its "(slot 22 / run frames 36-40)" hint has no citation anywhere
  in `docs/re/` and no matching `LDA #$B6` (pointer for slot 22) in the
  disassembly — downgraded from stated fact to unconfirmed, not attempted
  this pass. 352 pass / mypy clean / smoke 0. No live VICE session used.

## D-041 — The Alien is never shown on the map; the tracker is an ambiguous "SOMETHING moving" alarm — two mislabels corrected, a gameplay-defining invention removed
- **Date:** 2026-07-24
- **Finding:** Prompted by the user asking "what does the disassembly say
  about the alien showing up on the map?" — a question I should have asked
  myself before building R-05's Alien sprite on top of the assumption that
  a persistent map marker was faithful at all. It was not. Two routine
  labels that had been trusted for many passes are both wrong:
  1. **`$6667 place_alien_sprite` is not the Alien's sprite.** It `RTS`es
     immediately when the selected-character index `$64FB == 0` (the
     Alien's own array slot), builds its sprite pointer as `$64FB + $BC`
     (keyed to the selected *crew member*), and reads that crew member's
     duct flag `$6501,Y` into sprite colour `$D029`. It draws the
     **player's current-character marker** — the "Location Ptr" symbol in
     the game's own deck-plan key. Renamed `place_selected_char_sprite`.
  2. **`$595A check_tracker` has nothing to do with the tracker.** It
     renders a crew name (`index_x10` → `$A65E` name table) followed by the
     `$59D4` string **"'S BODY IS HERE"** — the corpse-discovery notice.
     Renamed `draw_corpse_notice`. **The tracker's real handler has still
     never been located.**
  So **no routine anywhere in the classified code draws the Alien on the
  deck map**, and the remake's Alien-revealing tracker had zero backing.
  What the ROM *does* prove is a set of **audio cues**, spelled out in the
  game's own instructions/sound-legend block (`$443C`): "This is the sound
  of ... the heartbeat of the current character." / "...a grille being
  removed." / "...**the TRACKER alarm.**" (`$451C`) / "...**SOMETHING
  moving between locations.**" (`$453C`). The wording is deliberately
  ambiguous — "SOMETHING", "between locations" — naming neither entity nor
  room. This independently corroborates the user, who confirmed from play:
  *the tracker only shows detected movement, which could be the Alien,
  Jones the cat, or another crew member moving.*
- **Action:** **Alien map marker removed entirely** from
  `pygame_app._draw_deck` (both the R-05 sprite and the older red "X"),
  guarded by `test_alien_is_never_drawn_on_the_map`, which renders two
  frames differing only in the Alien's position and asserts identical
  pixels. `sim._use_tracker` rewritten: it now raises an ambiguous
  `state.tracker_alarm` (movement detected somewhere aboard, source never
  identified) instead of recording the Alien's room; the
  `alien_reading_room` field was deleted outright and replaced with
  `tracker_alarm`. The status line shows "TRACKER ALARM: SOMETHING
  MOVING". `docs/re/DISASSEMBLY.md`: both mislabels corrected in the
  routine tables, plus a new §8.9b writing up the whole mechanic. R-05's
  sprite-frame machinery is kept (the `update_1` frame data is still real
  and correctly decoded) for any future legitimate on-map use. 353 pass /
  mypy clean / smoke 0.
- **Process note:** this is the finding that prompted the user to ask for a
  standing hard rule — **only implement what the disassembly proves**,
  explicitly including rendering/UX choices, since a "helpful" visual
  (an always-visible marker) changed real difficulty just as much as a
  gameplay constant would. Recorded to memory as a permanent project rule.

## D-042 — R-37 unblocked: selecting a dead/asleep crew member is a *bounce*, not a hidden entry
- **Date:** 2026-07-24
- **Finding:** R-37 had been filed-but-not-fixed for several passes with
  an explicit blocker: two independent live boots proved the real CONTROL
  "Order:" list shows **all seven** crew names even when one is confirmed
  dead (the remake filtered them out with `if crew.alive`), but the note
  correctly refused to just delete the filter without knowing *what
  selecting a dead entry actually does* — otherwise the fix would trade one
  invention for another. Traced it: the select-a-character handler is
  `guard_alien_present ($7720)` (another misleading name — it is not
  Alien-related). Its gate sequence is:
  `LDA $64FB / BEQ RTS` (slot 0 = the Alien, ignore) → `CMP #$08 / BCS RTS`
  (out of range) → `LDA $64D1,Y / BNE bail` (**asleep**) → `CPY $64CC / BEQ
  bail` → `LDA $7D45,Y / CMP #$02 / BCS continue` (**health < 2 =
  incapacitated → fall through to bail**). The bail path at `$774F` does
  `LDA #$00 / STA $64FB` — it **clears the selection** and jumps back to the
  main loop, after `guard_colocated ($423E)` has drawn that character's
  status. So the real behaviour is: the entry stays listed and is pickable,
  picking it shows their status, and you are immediately bounced back to the
  CONTROL list with no order menu.
- **Action:** `menu.py`'s `control_entries` now lists all seven crew (filter
  removed); `MenuController.fire` bounces a `select_crew` for anyone not
  `alive and awake`, matching the `$7D45 < 2` / `$64D1 != 0` gates. 3 tests
  added/updated (`all seven listed`, `dead bounces`, `asleep bounces`), plus
  a `_select_living_crew` helper — several existing tests relied on
  "cursor 0 = first *alive* crew", which stopped being true once the dead
  are listed and the opening death is random; they now pick an alive member
  explicitly (verified non-flaky over repeated runs). 355 pass / mypy clean
  / smoke 0.

## D-043 — FV-2.11 panic-wander implemented: panic has its OWN route-band mapping, and the tables contain deliberate self-loops
- **Date:** 2026-07-24
- **Finding:** FV-2.11 had been "substantially traced but not implemented"
  since D-026 — a real gap that left the PCS with no behavioural teeth at
  all (crew obeyed queued orders no matter what, even standing in the
  Alien's room). Byte-traced `char_wander ($5203)` in full to close it:
  * It opens `STA $650C,Y = 0` — **the pending action is cleared**, so panic
    *overrides* the player's order rather than deferring it.
  * It rolls `rng` 0-15 and reads the **Alien's own route tables**, but
    through its **own band mapping**, distinct from the Alien's
    (`_route_band`): `>=12 → $7AC8` · `9-11 → $7AA5` · `6-8 → $7A82` ·
    `3-5 → $7AA5` · `0-2 → $7AC8` (`$5214`-`$524F`). Only **three** of the
    five tables are ever used (indices 2/3/4), and two of them appear twice
    — so a panicking crew member roams the same routing data as the Alien
    but with a narrower, more repetitive distribution. Timer `#$28` (40).
  * The trigger implemented is `$5252`: the Alien's duct flag `$6501` must
    be **clear** (surfaced, not hiding) **and** `$7935,Y == $7935`
    (same room) → `JMP char_wander`.
  * **The route tables contain deliberate self-loops** (an entry pointing
    at its own room = idle). COMMDCENTR self-loops on 2 of its 3 panic
    bands, so a panicking crew member there frequently does *not* move.
    Found the hard way: the first draft of the tests picked COMMDCENTR and
    failed, which looked like a broken lookup but is real ROM behaviour.
- **Action:** `alien.py` gained `_panic_route_band` + `panic_dest`;
  `sim.py` gained `_apply_panic_wander`, wired into the tick at step 3.6
  (after the Alien moves and resolves its encounter, so a crew member it
  just walked in on reacts the same tick). 6 tests added, incl. one pinning
  the exact 16-entry band mapping against the decoded comparison chain and
  one pinning the self-loop/idle behaviour. **Deliberately NOT implemented:**
  D-026's other two trigger paths (`$5265` low health, `$52A4` a co-located
  disturbed crew member once the Alien has damage >= 6) — they depend on
  per-character latch machinery (`$64C4`/`$650C`) and the destination-walk
  engine the remake models differently, and D-026 explicitly left path
  priority and dispatch frequency open; wiring them on guesswork would
  trade a known gap for an invention. 361 pass / mypy clean / smoke 0.

## D-044 — The extinguisher's "repair" invention removed: structural damage is permanent, the extinguisher only silences a recurring alarm
- **Date:** 2026-07-24
- **Finding:** D-035 had already *proved* the FIGHT FIRE handler (`$5889`)
  never touches `$653F` (the structural-damage accumulator) — its only
  state writes are `$651C,X = 0` (the per-room damage *alarm stage*),
  `$5753,X = 0` (drop the special from the menu) and `$64D0 = 0`, then it
  prints "FIRE OUT" (`$5950`). But the correction was deferred as
  "feature-sized" and left flagged-but-live, so the remake kept doing
  `room_damage -= EXTINGUISHER_REPAIR` — actively repairing the ship, which
  the original never does. Now implemented properly. The full mechanic:
  * `damage_room_b ($5587)` raises the alarm (0 → 1) once a room's raw
    damage reaches **4** (`$558C: CMP #$04 / BCS`), and **only while the
    latch reads 0** (`$559E: LDA $651C,X / BNE skip`).
  * The extinguisher resets that latch to 0 and nothing else.
  * Since `$653F` only ever grows, the very next damage tick re-raises the
    alarm. So fighting fires is **recurring maintenance that never fixes
    anything** — the damage marches monotonically toward a hull breach
    regardless, which is a materially tenser game than "spray it and the
    room gets better."
- **Action:** deleted the invented `EXTINGUISHER_REPAIR` constant outright
  (replaced by `ROOM_ALARM_DAMAGE_THRESHOLD = 4`, `[C $558C]`); added a real
  `GameState.room_alarm` latch modelling `$651C`; `alien.add_room_damage`
  raises it under the decoded conditions; `sim._use_extinguisher` now
  clears the latch and leaves `room_damage` untouched (and is BLOCKED when
  no alarm is sounding). The renderer's `*WARNING*` now tracks the real
  latch instead of being derived from the damage number, so silencing a
  fire clears the warning while the damage stays. 2 tests rewritten + 1
  added (alarm returns on the next damage tick). 362 pass / mypy clean /
  smoke 0.
- **Deliberately NOT done:** wiring FIGHT FIRE as its own room-gated
  SPECIAL menu entry (D-032's "rooms 17-19" gate). That gate is expressed
  in the **20-entry damage-table index space** (`$653F`/`$651C`/`$5753` are
  20 entries, room index 0..`$13`), which is **not** the same space as the
  34-room `ROOM_SLUGS` table — and `ROOM_SLUGS[17..19]` lands on the two
  known-ambiguous `OTHER LIST` placeholder rooms. Implementing the gate
  would require resolving that index-space mapping first; guessing it would
  put the special in the wrong rooms. Filed as the remaining half of
  FV-2.10/R-27.

## D-045/D-046 — The deck-plan key settles what the map shows: five symbols, no Alien and no cat; and the character marker has a real heartbeat pulse
- **Date:** 2026-07-24
- **Finding (D-046, the decisive one):** while tracing R-06 (draw Jones as
  the cat sprite) I decoded the game's own **deck-plan key**, part of the
  instructions text at `$4460`. It enumerates *exactly five* map symbols:
  **"Location Ptr" · "Grille" · "Ladder Up" · "Character Postn" · "Ladder
  Down"**. There is **no Alien symbol and no cat symbol.** The map shows the
  location pointer, grilles, ladders and *crew* positions — nothing else.
  This independently re-confirms D-041 (the Alien is never mapped) from a
  completely different source, and extends it: **Jones's "j" marker was the
  same invention** and is now removed too. Anything else moving is knowable
  only through the ambiguous TRACKER alarm.
  R-06's roadmap hint was half right: `update_3 ($4F52)` does animate sprite
  pointers `$C4`-`$C8` = **slots 36-40** (matching "run frames 36-40"), in
  orange (`$D02A = 8`), sliding X right 4px/step and wrapping at `$F0` —
  a *screen-crossing* run animation, not a room marker. The hint's "slot 22"
  has no basis. Whether that animation is Jones is plausible (ginger cat,
  run cycle) but **not proven**, so nothing was wired to it.
- **Finding (D-045):** `update_2 ($4F19)` writes `LDA #$B8 / STA $07F8` —
  sprite 0's pointer is `$B8`, i.e. slot `$B8 - $A0` = **24**, which
  **validates the remake's pre-existing `_CHAR_SPRITE = 24` guess against
  the ROM**. It then counts `$64C1` down 7→0 (reloading 7) and writes
  `$4ED4,Y` into sprite 0's colour `$D027` each step. `$4ED4` =
  `00 0B 0C 0F 01 0F 0C 0B` — a symmetric black→greys→white→greys ramp:
  **the current character's marker pulses like a heartbeat.** This is the
  visual half of the game's own "This is the sound of the heartbeat of the
  current character." cue (`$44BC`); the audio half is R-21.
- **Action:** Jones's map marker removed from `_draw_deck`, guarded by
  `test_jones_is_never_drawn_on_the_map` (same two-frame pixel-identity
  technique as the Alien's). Character marker now cycles
  `_HEARTBEAT_COLOURS` instead of static white (R-19's visual half).
  `_CHAR_SPRITE`'s comment upgraded from a guess to `[C $4F33]`. 363 pass /
  mypy clean / smoke 0.

## D-047 — ALIEN's charset is entirely cut-out/reverse style, and the front-end loader screens use the C64 ROM font instead (R-01 regression fixed; R-36 done)
- **Date:** 2026-07-24
- **Finding:** Implementing R-36's key-highlight boxes produced a render
  that looked inverted, which exposed two related facts:
  1. **ALIEN's custom charset is entirely "cut-out" style.** Dumping bit
     counts across all 256 glyphs: `$20` = 0 bits (blank) and `$A0` = 64
     bits (solid) — so the decode is *correct*, not inverted — yet every
     letter glyph (`$01`-`$1A` lowercase, `$81`-`$9A` uppercase) is
     ~42-48/64 bits set, with the **letter shape formed by the 0-bits**.
     Searching for a conventional thin-stroke alphabet found none: the
     `$20`-`$7F` range is graphics/table data, not letters. So on-screen,
     a text cell *fills* with the colour-RAM colour and the glyph shows the
     `$D021` background through the letter — which is exactly why the real
     CONTROL panel reads as solid colour bands with black lettering
     (`the live captures (not published)upper deck.png`), and why the selection screen's
     names look like plain dark letters on green (the cell fill matches the
     surrounding `$A0`-filled green screen — `game menu.png`).
  2. **The front-end screens do not use that charset at all.** LOADING /
     NOTICE / WELCOME / INSTRUCTIONS are drawn by the separate loader
     programs (`MENU`/`MENUA`/`MENU1`), which run *before* `ALIEN.prg`
     points the VIC at its own font (`set_charbase $400A` sets `$D018` →
     `$2000`). `the live captures (not published)menu1.png` shows them plainly: thin light
     strokes on black — the **standard C64 ROM font**. R-01 had applied
     ALIEN's cut-out charset to these screens, which was a regression
     introduced by that pass (it made them render as blocky slabs).
- **Action:** `_c64_or_sysfont` and the `_blit_*` helpers gained an explicit
  `c64_font` flag; every front-end draw now passes `c64_font=False`, which
  is the **faithful** choice there, not a fallback (documented as such in
  the docstring so a future reader doesn't "fix" it back). In-game screens
  (play panel, status line, selection names, title) keep the custom
  charset. **R-36 completed** alongside: added `_blit_center_keyed` for
  mid-sentence reverse-video key boxes and wired the real highlights —
  blue boxes on the "Y"/"N" of "(Y OR N)" and the leading "N" of "N WILL
  START THE GAME", a pink box on "RESTORE" — plus the reference's yellow
  question and yellow RESTORE line. Verified by rendering the screen and
  comparing against `menu1.png` directly. `[?]` left alone: the exact shade
  of the spaced "A L I E N" header (the R-36 note is itself unsure between
  red and pink/magenta, so swapping it would trade one guess for another).
  363 pass / mypy clean / smoke 0.

## D-048 — R-26 "IS INSANE" implemented; and a genuine POLARITY CONFLICT in `$7D55` found but deliberately not resolved
- **Date:** 2026-07-24
- **Finding:** Implementing R-26's missing "IS INSANE" terminal state
  surfaced a contradiction the project has been carrying unnoticed.
  **Unambiguous part (implemented):** `select_outcome`'s per-survivor loop
  does `$61E2: LDA $7D55,Y / BNE skip` — a crew member whose state-of-mind
  cell is **exactly 0** gets the `$63E5` string **"is insane"** appended to
  their name in the end report, and costs 3 Competence (`$61F6: SBC #$03`).
  Decoded the surrounding strings to confirm: `$63D8` "All crew lost",
  `$63E5` "is insane", `$63EE` "Survivors.", `$63F8` "Competence Rating.".
  **The conflict:** two independent ROM sites say **0 is the WORST state** —
  the insane check above, and the decoded `fear_band` (documented in
  `constants.py` as `idx = 4 - value` for value<5, so 0 → index 4 →
  `MORALE_BANDS[4]` = **BROKEN**). But two other ROM sites *increment* that
  same cell as a consequence of bad things: `raise_crowd_fear ($4CE8)` does
  `INC $7D55,X` when crew are crowded, and `$729C` does `ADC #$01` per tick
  spent in the ducts. Under "0 = worst / higher = better", crowding and
  duct-crawling would *improve* morale, which is semantically backwards.
  Meanwhile the remake's own `CrewMember.morale` implements the **opposite**
  polarity from the `fear_band` its own `constants.py` documents (remake:
  `idx = fear * 5 // 11`, so 0 → CONFIDENT; decoded: 0 → BROKEN). The two
  formulas happen to agree at value 3 (both → STABLE), which is exactly the
  data point FV-2g used to "confirm" the formula live — so that confirmation
  did not actually discriminate between them.
  So there are two self-consistent readings: **(A)** `$7D55` is *composure*
  (high = good), fitting `fear_band` + the insane check but making the
  stressors backwards; **(B)** it is *stress* (high = bad), fitting the
  stressors but inverting both the morale word and the insane check.
- **Action:** implemented only the part both readings' code agrees on —
  `CrewMember.is_insane` (a direct `BEQ` on the cell, cited `[C $61E2]`),
  wired into the end screen alongside the real "SURVIVORS." list. 1 test.
  **Deliberately did NOT flip `CrewMember.morale`'s polarity**, even though
  the decoded formula disagrees with it: that would invert the whole
  displayed PCS on a contested reading, and the evidence genuinely points
  both ways. Filed as a precisely-stated open question rather than guessed —
  resolving it needs either a live read of a crew member at a known-extreme
  state, or locating a *third* independent site that reads `$7D55` with an
  unambiguous good/bad consequence. This is the single most important
  remaining `[?]` in the PCS. 364 pass / mypy clean / smoke 0.

## D-049..D-052 — R-09/R-02 done: exact portrait table, the paper/ink model, a true VIC border, and the panel's real wording
- **Date:** 2026-07-24
- **D-049 (R-09, crew portraits — CONFIRMED + exact positions).**
  `main_dispatch ($5ECE)` writes sprite pointers `$BD..$C3` into
  `$07F8..$07FE` — slots **29..35**, exactly the remake's `_PORTRAIT_SLOTS`
  in exactly that order, so the long-standing `[?]` on the slot→name
  mapping is closed. It also zeroes all eight sprite colour registers
  (`$5EEF: STA $D027,Y`, A=0), confirming the portraits really are **black**
  as the remake drew them. New: the 14-byte table at `$5EC0` is copied
  straight into `$D000` (sprite X/Y pairs) with `$D010 = #$40` for sprite 6's
  X high bit, giving VIC coords `(48,82) (88,82) (128,82) (168,82) (208,82)
  (248,82) (288,82)` → screen `x = 24,64,104,144,184,224,264`, `y = 32`.
  The remake had been spacing them evenly by a computed cell width; now uses
  the ROM's own coordinates.
- **D-050 (the paper/ink model — a systematic rendering inversion).**
  `sub_screen_setup ($5FC3)` is decisive: `$D020 = 5` (green border),
  **`$D021 = 0` (BLACK background)**, colour RAM filled with **5 (green)**,
  and the whole screen filled with **`$A0`** (the solid glyph). So every cell
  renders green, and because ALIEN's font is cut-out (D-047), a *text* cell
  shows its letters in the black `$D021` through the green fill. In other
  words **paper = the colour-RAM colour, ink = `$D021` black** — the remake
  had this backwards everywhere (black fill with coloured letters). Fixed on
  the selection screen, the CONTROL panel and the status line; the deck
  backdrop already used the correct model, which is why only it looked
  right. Also taught `_c64_or_sysfont` that a `(paper, ink)` pair must
  become *ink-coloured strokes* when it falls back to the stroke-based
  system font, not a solid box (which would re-invert it).
- **D-051 (R-02, exact 40x25 geometry + a real VIC border).** The border was
  being paint\ed *over* the 320x200 field, eating two columns/rows and
  pushing the map and panel out of alignment (the panel was visibly
  truncated). Now `_surface` is exactly the 40x25 field and `_present()`
  blits it into a larger bordered window, so grid arithmetic is exact: the
  ship map at columns 0-29 / rows 0-16, the CONTROL panel at columns 30-39,
  the status lines from row 18 — matching the captured screen RAM.
- **D-052 (the panel's real wording).** Read straight off
  `upperdeck_0400.bin` cols 30-39: `CONTROL` / `Order:` / the seven crew
  names / `indicate` + `location` / `display` + `level:` / `Upper Deck` /
  `Middle Deck` / `Lower Deck`. The remake had uppercase single-line labels
  ("ORDER:", "INDICATE LOCATION", "DISPLAY LEVEL") that overflowed the
  10-column panel; the original wraps them across two rows and uses
  lowercase. Also dropped the invented `">"` cursor arrow — the captured
  rows show no cursor glyph and the panel has no column to spare; selection
  is shown by the row's own reverse-video inversion. (Note "Middle Deck"
  truncating to "Middle Dec" is **faithful** — the capture shows exactly
  that.)
- **Action:** all four applied to `render/pygame_app.py` (+ `core/menu.py`
  for the labels); verified by rendering the play and selection screens and
  comparing directly against `the live captures (not published)upper deck.png` and
  `game menu.png`. 364 pass / mypy clean / smoke 0.

## D-053 — R-10: the play screen carries the commanded character's own portrait, colour-coded by duct state
- **Date:** 2026-07-24
- **Finding:** `place_selected_char_sprite ($6667)` — the routine D-041
  un-mislabelled from "place_alien_sprite" — turns out to answer R-10. It
  puts **sprite 2** at the fixed VIC position `($1C, $A9)` → screen
  `(4, 119)` (bottom-left of the map field), with pointer `$64FB + $BC`:
  for crew index 1 that is `$BD` = slot **29** = Dallas's portrait, i.e. the
  same `_PORTRAIT_SLOTS` table the selection screen uses. So the play screen
  permanently shows a portrait of **whoever you are currently commanding**.
  Its colour register `$D029` is loaded straight from that character's
  **duct flag** `$6501,Y` — 0 while in a room, 1 while crawling the vents —
  so the portrait changes colour to tell you your character is in the
  ducting. It `RTS`es when `$64FB == 0`, so no character selected = no
  portrait.
- **Action:** implemented in `_draw_deck` at the ROM's exact position, drawn
  only while a crew member is selected (matching the `$64FB == 0` guard).
  **`[?]` deliberately incomplete:** the duct-coloured (white) variant is
  currently unreachable because the remake has **no per-crew "in duct"
  state** — crew always occupy a room — so it always draws the in-a-room
  colour. Wiring the white variant needs real crew duct traversal, which is
  a filed feature gap, not something to fake by inventing a duct flag.
  364 pass / mypy clean / smoke 0.

## D-054 — R-03 multicolor sprite decoding + R-18 real joystick input
- **Date:** 2026-07-24
- **R-03 (multicolor sprites).** A C64 sprite with its multicolor bit set
  trades horizontal resolution for colour: each row's 24 bits are read as
  **12 bit-pairs** drawn double-width, where `00` = transparent, `01` =
  `$D025`, `10` = the sprite's own colour, `11` = `$D026`. The hi-res
  decoder cannot represent that and renders such sprites as noise — which is
  exactly what the title screen's alien egg looked like before D-021 handled
  it inline in the renderer. Added `decode_sprite_multicolor` /
  `decode_sprites_multicolor` / `sprite_sheet_multicolor_png` to
  `alientools.charset`, plus a `--multicolor` flag on the `chars`
  subcommand. The decoder deliberately returns **raw 0-3 pair codes rather
  than baked colours**, because the palette registers are set by whichever
  routine draws the sprite — the toolkit shouldn't guess them. Verified
  against the egg (slots 41-48 = pointers `$C9-$D0`), which now decodes to
  coherent shapes. 4 tests.
- **R-18 (joystick).** The original is joystick-driven during play — port 2,
  `$DC00`, and the loader prints "PLUG JOYSTICK INTO PORT TWO". The remake
  now opens joystick 0 if present and maps hat/axis to the existing
  direction events and the single button to FIRE, with **edge-trigger +
  auto-repeat** on directions (a raw per-frame read makes the cursor
  unusable) and press-edge-only on the button. Entirely optional: with no
  pad attached the keyboard scheme is untouched. 4 tests drive a scriptable
  fake joystick so this runs headless. **`[?]`:** the original's exact
  cursor-repeat delay/rate is undecoded — the two constants are feel-tuned
  and flagged in code rather than presented as ROM-derived.
- **Action:** 372 pass / mypy clean / smoke 0. The documented command list
  gained the `--multicolor` usage line.

## D-055 — R-10 completed: crew in-duct state modelled without touching the contested morale polarity
- **Date:** 2026-07-24
- **Finding:** R-10's remaining half needed a per-crew "in the ducting"
  state, which the remake lacked entirely — `shortest_room_path` already
  routes crew *through* the duct network when grilles are open, but collapses
  junctions out of the returned path, so crew effectively teleported through
  vents with no observable state. The ROM keeps this as the per-character
  flag `$6501,Y`, which several routines branch on:
  `place_selected_char_sprite ($6667)` colours the on-screen portrait from it
  (`LDA $6501,Y / STA $D029`), `resolve_char_move ($5156)` gates movement on
  the room's grille, and `$729C` adjusts state-of-mind each tick spent
  crawling.
  Implemented without changing the path model: a move step between two rooms
  that have **no door** between them can only have crossed the duct network,
  so `CrewMember.in_duct` is set for that step and cleared on arrival. That
  is derivable from the existing graph and needed no new location kind.
- **Action:** `CrewMember.in_duct` added `[C $6501,Y]`; `sim._apply_order`
  sets/clears it per step; the play screen's portrait now switches to the
  in-duct colour from that flag, completing R-10. 1 test (door step must NOT
  flag, grille/duct step must). **Deliberately NOT implemented:** the
  `$729C` per-tick state-of-mind change while in a duct — whether it helps or
  hurts depends on the **unresolved `$7D55` polarity conflict (D-048)**, so
  wiring it now would compound a known ambiguity instead of resolving it.
  373 pass / mypy clean / smoke 0.

## D-056/D-057 — FV-3.1/3.2 harnesses built, and they immediately caught three real bugs; the specials label table decoded exactly, closing FV-2.10's last question
- **Date:** 2026-07-24
- **FV-3.1 (drift-guards).** `tests/test_fv3_drift_guards.py` pins every
  decoded/captured value to the ROM address or capture it came from, with the
  citation inline — Alien timers/bands, the item damage table, the fear
  scale/stressors, crew start tables, map/item table shapes, the deck-value
  mapping, and the render constants. It also asserts that each **removed
  invention stays removed** (`LETHAL_ITEM_IDS`, `ATTACK_HIT_CHANCE`,
  `ALIEN_ATTACK_HIT_CHANCE`, `EXTINGUISHER_REPAIR`) — several of these were
  wrong at some point, so the file doubles as a record of what has drifted
  before. 14 tests.
- **FV-3.2 (rendered-frame harness).** `tests/test_fv3_frame_harness.py`
  renders real frames headlessly and checks them *structurally* (grid
  geometry, palette membership, marker presence/absence) rather than against
  a golden image — a byte-exact reference would break on any deliberate
  change and say nothing about what moved. 12 tests, covering the four
  regressions this project actually shipped: the paper/ink inversion
  (D-050), the border eating the field (D-051), ALIEN's charset applied to
  the loader screens (D-047), and markers drawn for entities the map never
  shows (D-041/D-046).
- **D-056: the harness immediately caught three real bugs.**
  1. **Anti-aliased text.** Every `font.render(...)` passed
     `antialias=True`, blending glyph edges and producing **hundreds of
     colours outside the 16-entry palette** — impossible on a C64 and the
     main reason the front-end still read as "modern". All render calls now
     pass `antialias=False`.
  2. **`"REMV GRILLE"` is 11 characters** and overflowed the 10-column
     panel. The real label (`$86E6`) is **`"REMVGRILLE"`** — exactly 10, no
     space.
  3. **`"LAUNCH NARC"` is also 11** and overflowed.
- **D-057: the specials label table decoded exactly — and it closes
  FV-2.10.** The table starts at **`$5799`** (which is what
  `draw_status_row` indexes, `LDA $5799,Y`) and is a clean array of
  **10-character records**:
  `Scuttle` · `Nostromo` · `BlowLock.1` · `BlowLock.2` · `SealLock.1` ·
  `SealLock.2` · `Enter` · `Hypersleep` · `Board` · `Narcissus` · `Launch` ·
  `Narcissus` · `Override` · `Detonation` · `Fight Fire`.
  The record offsets (`$00 $0A $14 $1E $28 $32 $3C $46 $50 $5A $64 $6E $78
  $82 $8C`) are **exactly** the `LDY #$..` immediates in
  `guard_target_alive ($56B4)` and `$571C`-`$5742` — so the whole specials
  mapping is now confirmed from a second, independent direction. Crucially
  this **resolves SEALLOCK**, the last open piece of FV-2.10: it sits at
  `$28`/`$32`, selected over BlowLock by that airlock's own open flag
  (`$5751`/`$5752`) — precisely the arm/cancel pattern
  `special_options.py` already modelled, now proven rather than inferred by
  elimination. It also shows multi-word specials occupy **two rows**
  (Enter/Hypersleep, Board/Narcissus, Launch/Narcissus,
  Override/Detonation), like the CONTROL panel's indicate/location.
- **Action:** all labels corrected to the ROM's own mixed-case 10-char
  records with two-row wrapping; 6 menu tests updated to match. 399 pass /
  mypy clean / smoke 0.

## D-058 — R-08 solved from the ROM instead of the pixels: the game has its own per-room marker-position tables
- **Date:** 2026-07-24
- **Finding:** R-08 (pixel-exact room/marker alignment) had been parked
  earlier the same day after the obvious image-processing route failed —
  flood-filling `$A0` regions in the captured screen gave 9/12/6 enclosed
  areas against the real 10/14/10 room split, because doorways merge
  adjacent rooms into one component. Rather than push on glyph
  classification, went looking for the data in the ROM instead, and it is
  simply there: `$76D7` positions **sprite 1** — the deck-plan key's
  "Location Ptr" — by indexing **two 36-entry byte tables** with the
  character's own room (`$64F7`, loaded from `$7935,Y` at `$778E`):
  `LDA $758D,Y / STA $D002` (X) and `LDA $75B1,Y / STA $D003` (Y).
  Decoded both and converted to screen pixels (`VIC_X - 24`, `VIC_Y - 50`),
  which lines up with the map drawn at the field origin (R-02/D-051).
  **Validation:** 32 of the 34 mapped rooms get a *unique* position on their
  deck — only CORRIDOR 6/CRYO VAULT and ENGINEERNG/INFIRMARY share a spot,
  which is what the ROM contains and is left uncorrected. Rendering a frame
  with a crew member on the viewed deck puts the marker cleanly **inside a
  room's walls**, not on a wall or in a corridor — exactly the alignment
  the internal BFS grid could never guarantee.
- **Action:** `_ROOM_MARKER_X`/`_ROOM_MARKER_Y` added to
  `render/pygame_app.py` with the full citation, plus a `_room_marker_px`
  helper; the character marker and the INDICATE LOCATION box now use the
  ROM's own coordinates, falling back to the internal grid only for
  synthetic test maps that aren't in the 36-entry table. This retires the
  last of DECISIONS D-010 #2's eyeballed positioning for markers. 2
  drift-guard tests (table shape + in-field bounds; and that exactly 2
  same-deck duplicates exist, so a broken index alignment fails the gate).
  401 pass / mypy clean / smoke 0.
- **Lesson worth keeping:** the image-processing approach was the intuitive
  one and was *wrong*; the data was in the program the whole time. When a
  derived-from-pixels method starts needing heuristics, check whether the
  ROM just stores the answer.

## D-059 — The `$7D55` polarity conflict RESOLVED: it is composure (high = good), and the remake's morale word was inverted
- **Date:** 2026-07-24
- **Finding:** D-048 had filed this as the single most important open PCS
  question and judged it unresolvable without a live read at a known-extreme
  state. It turned out to be resolvable statically — by decoding the *word
  table itself* instead of trusting the transcription of the formula.
  `fear_band ($7DC5)` reads `$6571,Y` and computes
  ``index = 0 if value >= 5 else (4 - value)``, then copies a 10-byte record
  from **`$7D13`**. Decoding those five records byte-by-byte gives
  `confident` / `stable` / `uneasy` / `shaken` / `broken`, so:

      value 0 -> broken · 1 -> shaken · 2 -> uneasy · 3 -> stable · 4+ -> confident

  **High is GOOD.** The cell is *composure*, not fear. That settles every
  strand of D-048's conflict at once:
  * `$61E2`'s "is insane" at value 0 ✓ — 0 is the terminal state.
  * Crew starting at 4/4/3/4/3/4/3 ✓ — a calm crew (CONFIDENT/STABLE) before
    things go wrong, which is the sensible opening.
  * `raise_crowd_fear ($4CE8)`'s `INC` ✓ — crowding **raises** composure:
    safety in numbers. The manual's "some get nervous when they're all in a
    room" was simply wrong; code is truth. D-031's finding that it skips
    value 0 also now makes sense: a *broken* crew member can't be reassured.
  * `$729C`'s `INC` while in a duct ✓ — hiding in the vents is reassuring.
  * `$47FE`'s `$4781 += ($7D55 - 2)`, feeding the Alien's hunt lock at
    `$4CA8` ✓ — a *composed*, active crew member moves about and draws the
    Alien; a broken one cowers. Thematically apt, and the third independent
    reader D-048 said was needed.
  The remaining `INC`/`DEC` sites line up cleanly as good/bad events:
  **DEC** = wounded by the Alien (`$4230`), any crew death (`$47DC`/`$5A0D`,
  looped over *all* seven slots), scripted setbacks (`$4625`/`$463C`);
  **INC** = crowding (`$4CF9`), scripted reliefs (`$4665`/`$466E`).
  Notably `constants.py`'s own long comment had recorded the correct formula
  and word order all along — only the `morale` *implementation* disagreed
  with it, and nobody had cross-checked the two.
- **Action:** `CrewMember.morale` rewritten to the verified formula (was
  `idx = fear * 5 // 11`, which maps 0 -> CONFIDENT and 10 -> BROKEN —
  exactly backwards; the two formulas coincide only at value 3, which is
  precisely the single data point FV-2g used to "confirm" it live, so that
  check never discriminated). Added a `composure` property alias under the
  correct name. Stressor **directions corrected**: being wounded by the Alien
  now applies `COMPOSURE_HIT_ALIEN_ATTACK = -1` on the wound path (`$4230`)
  rather than a `+3` bump for mere proximity (wrong direction *and* wrong
  trigger); the corpse rule is replaced by `COMPOSURE_HIT_CREW_DEATH = -1`
  applied **ship-wide, once per death** (`$47DC`/`$5A0D` loop all crew slots
  and fire on a death flag, not per tick while a corpse is in the room);
  crowding keeps its `+1` as the one genuinely reassuring event. 4 tests
  rewritten + 1 drift-guard added. 402 pass / mypy clean / smoke 0.
- **Method note:** D-048 concluded a live capture was required. It wasn't —
  the answer was one level deeper in the same data. When a formula's
  *meaning* is contested, decode the table it indexes rather than reasoning
  about the formula.

## D-060/D-061 — The auto-destruct countdown and the heartbeat rate both fully decoded (R-28b, R-19/R-21)
- **Date:** 2026-07-24
- **D-060 (R-28b, auto-destruct).** The remake's `AUTO_DESTRUCT_TICKS = 60`
  was an admitted `[?]` guess ("~10 s at TICK_HZ"). The real mechanic is
  fully decoded: `set_result_win ($58E3)` arms it by loading **9** into
  `$657B` (the "MINS" countdown) and **255** into `$657C` (a sub-counter).
  The tick routine (`$5A34`) decrements the sub-counter each pass and, on
  wrap, reloads 255, redraws the warning and decrements `$657B`:
  * `$657B >= 6` -> "OVERRIDE OPTION EXPIRY n MINS" (digit patched into
    `$555C`);
  * `$657B <  6` -> "SHIP WILL DESTRUCT IN n MINS" (patched into `$5578`);
  * `$657B == 0` -> `JMP hull_breach` — the ship is destroyed.
  And crucially the cancel **expires**: `$585E` gates OVERRIDE on
  `LDA $657B / CMP #$05 / BCC skip`, so you may only call it off while at
  least 5 of the 9 units remain. The remake let you cancel right up to the
  last tick. Real total: 9x255 = 2295 ticks, not 60.
- **D-061 (R-19 audio half / R-21).** `fear_alert ($4E16)` sets the
  heartbeat's IRQ divider `$4D02` straight from the character's composure
  `$6571,Y`: **>=4 -> 40 · 3 -> 30 · 2 -> 23 · <=1 -> 15**. The IRQ
  (`$4D37`) counts `$64B7` down from that divider and gates SID voice 1
  off/on (`#$10` then `$64B5` into `$D404`) — one beat per wrap. So the
  heartbeat **races as the character loses their nerve**, which is the
  game's central tension cue and matches its own sound legend ("This is the
  sound of the heartbeat of the current character.", `$44BC`).
  This is a **fifth independent corroboration of D-059's polarity**: a low
  value produces a *fast, panicked* pulse, so low = bad, high = composed.
- **R-21 scope note (honest):** the in-game SFX *dispatcher* is not
  implementable from the current disassembly. `$03E8` — written with a
  sound id at four sites (`$478E`, `$5158`, `$5267`, `$5589`) — is **never
  read anywhere in the classified `$2000-$C001` region**, so the routine
  that consumes it lives outside it (low RAM installed by the loader, most
  likely). Synthesising SFX without that driver would mean inventing them,
  which the standing rule forbids. What *is* decodable — the heartbeat's
  rate table above — is implemented.
- **Action:** `AUTO_DESTRUCT_MINUTES`/`_SUBTICKS`/`_OVERRIDE_ABOVE` added
  with citations, `AUTO_DESTRUCT_TICKS` derived; `GameState
  .auto_destruct_minutes_left` recovers `$657B` so the override gate keys
  off it exactly as the ROM does; `apply_special_option` now refuses a late
  OVERRIDE. `constants.heartbeat_divider` added and the renderer's marker
  pulse now uses it, so the on-screen beat speeds up as composure drops.
  3 behaviour tests + 2 drift-guards. 407 pass / mypy clean / smoke 0.

## D-075 — `$64BB` is the ATTACK-sequence flag, not "game active"
- **Date:** 2026-08-01
- **Finding:** DISASSEMBLY labelled `$64BB` `var_game_active`, and that label
  propagated into several harnesses and into R-29's caveat. It is wrong.
  Tracing the only setter settles it:
  ```
  begin_active_play ($4F90):
    4F90  LDA #$01 / STA $64BB
    4F9F  LDA #$F0 / STA $D015      ; enable sprites 4-7
    4FA5..  program an SFX on $D404/$D40B/$D406/$D40D
  stop_active_play ($5017):
    501E  STA $64BB (= 0)
    5023  LDA #$0F / STA $D015      ; restore sprites 0-3
  ```
  and its only caller chain is `$8CF3` -> `begin_active_seq ($8D1A)` ->
  `$4F90`, where `$8CF3` sits in the branch that displays the string at
  `$8C76` — which decodes to **"ATTACK"**. So `$64BB` marks an **Alien attack /
  encounter sequence**: a cinematic burst with its own sprite bank and sound.
- **Three things fall into place:**
  1. `pause_check ($6483)` returning early while `$64BB != 0` (D-071) now reads
     sensibly — you cannot pause mid-attack.
  2. `update_1 ($4EE8)`, gated by `$64BB`, animating the Alien sprite is the
     **attack cutaway**, which no longer contradicts D-041/D-046 (the Alien is
     never drawn on the *map*).
  3. Every prior attempt to "reach active play" by polling for `$64BB == 1`
     was waiting for an **Alien attack**, which is why it never fired — across
     multiple passes. `reach_active_play.py`'s premise was wrong.
- **★ R-29's caveat is RETRACTED.** D-063 recorded "sampled with `$64BB`
  (game_active) still 0 ... this is the opening state, not post-opening active
  play". `$64BB = 0` is *normal play*. The 7.886 Hz main-loop rate was measured
  during ordinary gameplay and needs no qualification.
- **Action:** the label corrected in `DISASSEMBLY.md` (with a prominent
  correction block) and in the routine index; the caveat removed from
  `constants.py`, D-063 and the todo entry; `r31_side_by_side.py` documents the
  trap so it is not repeated.

## D-080 — ★ THE ANDROID (`$64C3`) — a whole mechanic the remake never had
- **Date:** 2026-08-01
- **Prompted by:** the user reporting they had *seen the behaviour once while
  playing*. D-079 had surfaced the instruction line — *"THIS RANDOM START TO THE
  GAME IS COMPLICATED BY YOUR NOT KNOWING WHICH MEMBER OF THE CREW IS AN
  ANDROID"* — and I had filed it as unimplementable because nothing decoded
  pointed at it. That was too quick: the mechanic is fully present in the ROM.
- **Why a string search finds nothing:** the game **never prints the word
  ANDROID**. A screen-code and PETSCII search of all of `ALIEN.prg` returns
  zero hits. The player is meant to deduce it, so it is entirely behavioural —
  which is exactly why the earlier "complete 117-string inventory" pass missed
  it. *A mechanic with no text is invisible to a text search.*
- **Where it lives.** The opening routine (`$5049`) rolls the RNG into two
  16-entry candidate tables and stores two **distinct** crew indices::

      506E  LDA $50EC,Y / STA $64C2                 ; the opening victim
      507E  LDA $50FC,Y / CMP $64C2 / BEQ re-roll
      5086  STA $64C3                               ; ** THE ANDROID **
      50AB  LDY $64C2 / STA $7D45,Y=0 / $7935,Y=$FE ; kill the victim

  Decoded, the two pools are **not the whole crew**:

  | table | values | crew |
  |---|---|---|
  | `$50EC` -> `$64C2` | 1, 2, 5 | DALLAS, KANE, LAMBERT |
  | `$50FC` -> `$64C3` | 1, 2, 4, 6 | DALLAS, KANE, **ASH**, PARKER |

- **★ The clincher:** `$6062`-`$6069` is a hard-coded preset —
  `$64C2 = 2` (KANE) and `$64C3 = 4` (**ASH**). Kane dies first; Ash is the
  android. That is the film's own pairing, and it identifies `$64C3` beyond
  reasonable doubt.
- **What the android does**, from all 13 of its `$64C3` sites:
  * **Attacks crew sharing its room** (`$5439`): same room, and the victim's
    composure >= 2 (`$5459`) **and** health >= 2 (`$5460`), then `$546D` calls
    `alien_wound_crew` with the android as the attacker. A second path
    (`$5345`) reaches the same call after a scan loop and prints " HITS "
    (`$533F`). The two guards mean it leaves already-broken or already-collapsed
    crew alone — which is the ROM's rule, not a design choice.
  * **Cannot ENTER HYPERSLEEP** — `guard_target_is_player ($5939)` RTSes
    immediately when the commanded character is `$64C3` (`$593C`).
  * **Is exempt from the endgame mass kill** (`$6130 CPY $64C3 / BEQ skip`), so
    it can be the last thing standing.
  * **Does not count as a survivor for the COMPETENCE RATING** (`$61A5`, skipped
    *before* the health test).
  * Has its own branch in `resolve_char_move` (`$5168` -> `$5265`) and special
    handling in the Narcissus launch (`$5B5F`, `$5BD3`, gated on `$64CC`).
- **A second bug found on the way:** the remake drew the opening victim
  **uniformly from all seven** crew, so it could open by killing Ripley, Ash,
  Parker or Brett — outcomes the original cannot produce. Corrected to the
  `$50EC` pool. (D-014's single live capture showing LAMBERT is consistent, and
  the r31 capture showed LAMBERT too.)
- **Action:** `OPENING_VICTIM_CANDIDATES`, `ANDROID_CANDIDATES`,
  `ANDROID_ATTACK_MIN_COMPOSURE/HEALTH`, `modes.choose_android()`,
  `GameState.android_id`, `Simulation._apply_android_attack()` (run after the
  Alien and panic passes so a crew member driven into its room is attacked the
  same tick), the hypersleep refusal, and the two scoring exemptions. 9 tests.
- **Method note worth keeping:** "no string, therefore no mechanic" is a bad
  inference, and I made it. The check that would have caught this earlier is the
  one that found it in the end — enumerate the RNG call sites and see what each
  one *writes*.
- `[?]` Not yet modelled: the android's own `$5265` action branch, and the
  `$64CC`-gated Narcissus behaviour. Recorded rather than guessed.

## D-081 — ★ The opening notice prints a GARBLED name — an original-game bug
- **Date:** 2026-08-01
- **Prompted by:** the user recalling the C64 game "scrambled the name of the
  person that was killed by the Alien". Verified live, and it is real.
- **What happens.** `$5089`-`$509C`::

      5089  LDA $64C2 / JSR index_x10 / TAY   ; victim slot * 10
      5092  LDA $A65E,Y / STA $06F9,X         ; copy 10 chars of the name
      50A0  LDA $50BF,Y / STA $0701,Y         ; " HAS BEEN KILLED BY THE ALIEN"

  The name table genuinely is at `$A65E` — but that address is **under BASIC
  ROM**, and this routine never banks it out. `LDA $A65E,Y` therefore returns
  **BASIC ROM bytes**, and the notice renders them as garbage.
- **Proof (live, byte-for-byte).** With `$64C2 = 5` (LAMBERT), the notice row
  read `2B 69 FF 85 7A A5 2C 69` in the name field. At the same instant:
  * RAM at `$A690` held `8C 01 0D 02 05 12 14 A0` — "LAMBERT";
  * the CONTROL panel, whose draw code *has* banked BASIC out, showed
    **LAMBERT** correctly on row 6;
  * reading `$A690` through VICE's **`rom`** bank returned exactly
    `2B 69 FF 85 7A A5 2C 69` — **a match**.
  So the notice is reading the ROM while the panel reads the RAM, from the same
  address. That is the bug.
- **All three possible victims are affected** (`$50EC` = DALLAS/KANE/LAMBERT),
  each indexing different ROM bytes, so the garbage differs per victim:
  slot 1 -> `33 84 34 A5 2D A4 2E 85 2F 84`, slot 2 -> `30 85 31 84 32 20 1D A8
  A2 19`, slot 5 -> `2B 69 FF 85 7A A5 2C 69 FF 85`.
- **Also confirmed while measuring:** the name field (`$06F9`, row 19 col 1) and
  the message (`$0701`, row 19 col 9) **overlap by two columns** — the ROM's own
  geometry, not a rendering artefact.
- **Reproduced, not fixed.** The goal is a 1:1 replica, so `core/opening_name.py`
  reads the same bytes out of the machine's BASIC ROM (locate-don't-vendor, like
  `render.romfont`) and the renderer draws them as raw screen codes via
  `_blit_codes`. Without the ROM it falls back to the real name. 5 tests.

## D-087 — P-5..P-8 applied: ducts wired end to end, and the font hole closed
- **Date:** 2026-08-02

### P-6 — the Alien in the ducts, and bursting out ([C $8A74] / [C $8B84])
- `alien_ai ($8A74)` is a **separate roller** from the surface one and walks the
  **compass (duct) graph**: roll 0-2 N (`$80F5`), 3-5 E (`$8117`), 6-8 S
  (`$8139`), 9-12 W (`$815B`), each `ADC #$80` to stay in the ducting.
- **Roll 13-15 emerges.** `$8A92 LDA $7935 / STA $64E6` sets the destination
  **without** bit 7, which `$8B6F BCC $8B7E` reads as "come out here". That was
  the missing piece — the in-duct roller otherwise always sets bit 7, so it
  looked like the Alien could never surface.
- **Bursting** (`$8B84`): crossing a grille still in place — emerging into a
  room (`$8B7F`) *or* ducking into one from the surface (`$8BB4`) — does **not**
  move it. It clears that room's `$8676` byte (**the grille is gone for good**),
  pauses 40 ticks and raises `$651B`, the "GRILLE BURSTS OPEN" event (`$8BC4`).
- **`$8A7A`-`$8A83`:** while its own room's grille is still shut, roll 15 is
  re-rolled — a trapped Alien is slightly likelier to keep crawling than to try
  to come out.
- The remake's model was "hide in the same room for 40 ticks, then reappear": it
  never walked the network and never burst a grille. A self-referencing table
  entry is now modelled faithfully too — the Alien burns its full move timer
  going nowhere, exactly as `LDA $80F5,Y` + `ADC #$80` on a self-loop does.

### P-5 — the crew's grille -> duct route ([C $779C])
- `_reachable_move_targets` now **switches graph on the in-duct flag**, as
  `$779C` does: surface -> the routing graph (`door_neighbors`), inside -> the
  compass graph (`duct_exits`). Before, both were the same table (D-086).
- `Simulation._duct_step_target` gates entry on the room's grille being open —
  which is what REMVGRILLE is *for*. Once inside, movement along the ducting is
  free. The composure cost on entry (D-083) is unchanged.
- The payoff is measurable: from AIRLOCK 1 the doors reach only CORRIDOR 6,
  while the ducts reach RECRTNAREA / LIFE SUPPT / LAB STORES.

### P-8 — the ending screen's corruption
- Reproduced immediately at 5+ survivors: the list was drawn at `130 + i*10`
  pixels and the rating at y=168, so the fifth name **overwrote the rating**.
- Fixed by using the ROM's own screen offsets: rating text at `$0770` (**row
  22**) with its digits at `$0783`/`$0784` (row 22, cols 19-20), "PRESS ANY KEY"
  at `$07D8` (**row 24**), and the survivor list confined to rows 16-21 so it
  cannot reach row 22.

### P-7 — ★ the font hole was one glyph, and it was not missing
- The same frame showed the second defect: "SURVIVORS." rendered in SysFont
  while the names beside it drew in the game's charset. Cause: the **period**.
- **D-078 was wrong to call the period "unlocated".** It concluded that because
  the glyph at `$AE` is *blank* — but blank is the point. `$7CEB` holds
  `8F AE 8B AE` for the status word "O.K.", and the `$7A10` status template uses
  runs of `$AE` as its dotted fill. **`$AE` is exactly the byte the ROM writes
  where a period belongs; this charset simply has no period glyph.** Mapping
  `.` -> `$AE` (and `,` -> `$AC`, which does carry a low dot) reproduces the
  ROM's bytes *and* its blank rendering.
- Also corrected: the header is the ROM's **"SURVIVORS:"** (`$63EE`, a colon),
  not the invented "SURVIVORS." — the wrong wording was what dragged in the
  period in the first place.
- **Audited:** every in-game string now renders in the game's own charset —
  status words, morale words, panel labels, the status template, the ending
  lines. **Zero SysFont fallbacks.** (The loader screens correctly keep the ROM
  chargen, D-047/D-065.)

## D-086 — ★ The movement topology is INVERTED in the remake (and D-083 was half wrong)
- **Date:** 2026-08-02
- **Prompted by:** the user reporting "the movement between rooms is incorrect —
  each room should connect to other rooms when you are in that room but not
  others", plus "after removing a grille the characters are supposed to move
  into the duct system".
- **★ There are TWO separate adjacency graphs, and the remake uses the wrong one
  for movement.** The switch is explicit at `$779C`::

      779C  LDA $6501,Y      ; the character's IN-DUCT flag
      779F  BEQ $77A7        ; on the surface -> $77A7 ... -> $7856/$7860
      77A4  JMP $81D7        ; IN DUCT       -> $81D7 ... -> $81EF

  * **`$7860` builds the SURFACE "move to" list from the five ROUTE tables**
    (`$7A3A`/`$7A5E`/`$7A82`/`$7AA5`/`$7AC8`), de-duplicating and stopping at a
    self-reference.
  * **`$81EF` builds the IN-DUCT list from the four COMPASS tables**
    (`$80F5`/`$8117`/`$8139`/`$815B`).

- **The remake has them backwards.** `nostromo_ship()` calls `add_door()` for
  every **compass** neighbour, and then invents a junction graph for the ducts
  (`nostromo.py` even says so: *"the junction wiring here mirrors the door graph
  between grille rooms `[?]`"*). So surface movement is running on the **duct**
  table.
- **The two graphs are genuinely different — 31 of 34 rooms disagree** (70
  surface edges vs 76 duct edges), and the difference is exactly what the user
  described:

  | room | SURFACE (route tables) | IN-DUCT (compass tables) |
  |---|---|---|
  | AIRLOCK 1 | corridor_6 | lab_stores, life_suppt, recrtnarea |
  | AIRLOCK 2 | corridor_6 | life_suppt, livng_qtrs |
  | ARMOURY | corridor_4 | corridor_3, eng_stores |
  | CORRIDOR 6 | airlock_1, airlock_2, computer, life_suppt, stores_1 | computer, life_suppt, recrtnarea, stores_1 |

  The route tables give a **corridor-hub deck plan** — ordinary rooms open onto
  a corridor and nothing else, corridors fan out to many rooms. That is what a
  ship's deck plan looks like, and it is why the remake currently lets crew walk
  between rooms that should not be directly connected.
- **★ D-083 is half retracted.** Its identification of the compass tables as the
  **duct** network was right (that is what `$81EF` uses). What it missed is that
  the project was *already* using those same tables for `add_door`, so adding
  `duct_exits()` on top left both graphs identical and fixed nothing. The
  surface graph must come from the route tables instead.
- **A second, independent bug: SOUTH and EAST are swapped.** `alientools.gamedata`
  has `SOUTH_ADDR = 0x8117, EAST_ADDR = 0x8139`, but `$40B8`-`$40FA` prints the
  direction word for each table and proves `$8117` -> `$8095` = **"EAST"** and
  `$8139` -> `$808B` = **"SOUTH"**. Connectivity is unaffected (the neighbour
  *set* is the same) but every compass label is wrong.
- **★ The opening notice IS a separate pre-screen** (the user was right; R-13's
  "overlay" change was based on a mis-sampled capture). `start_game` runs::

      704E  JSR game_init_mode   ; clears $0400-$06E8 to $A0
      7051  JSR sub_5049         ; the notice + victim kill + 2x delay_long
      7054  LDA #$06 / STA $D020 ; only NOW the play screen is built
      7065  LDA $01 / AND #$FE   ; ** and only now is BASIC ROM banked out **

  My live sample looked "overlaid" because it began once the screen already
  matched the play-screen detector, by which time the play screen had been drawn
  over the notice leaving its text in row 19.
- **APPLIED 2026-08-02 (P-1/P-2/P-3).** `alientools.gamedata.surface_exits()`
  reproduces the `$7860` construction exactly — first table unconditional,
  dedupe against the **immediately preceding accepted** value only, and **stop
  the whole list** at a self-reference — and emits `SURFACE_EXITS` into the
  snapshot. `nostromo_ship()` now builds doors from it (76 endpoints, a proper
  corridor-hub plan: AIRLOCK 1 -> CORRIDOR 6 only; CORRIDOR 6 -> five rooms) and
  builds **no junctions and no invented duct pairs at all**; grilles are
  per-room (`$8676`) and `duct_exits()` serves the compass graph. `Grille`'s
  `junction_id` is now optional scaffolding for synthetic test maps.
  Three tests asserted the old model and were rewritten, including
  `test_every_compass_edge_is_walkable_both_ways` — which was pinning the bug.
  **500 pass / mypy clean / smoke 0.**
- **★ And `$7065` independently confirms D-081.** The BASIC bank-out happens
  **after** `sub_5049` — so the notice at `$5092 LDA $A65E,Y` genuinely does read
  BASIC ROM, exactly as the live byte comparison showed. Two independent proofs
  now agree.

## D-085 — R-38 closed, and **SHORT mode is a fixed scenario** (FV-1.9 was wrong)
- **Date:** 2026-08-02
- **`$755E delay_routine`** — a nested busy-wait (`LDY #$AA`, inner X loop to
  256, outer Y to 256) called straight after `read_input` at `$7456`. It is the
  input pacing/debounce delay. Nothing else.
- **★ `$604F` is the SHORT SCENARIO's initialiser**, and it changes a conclusion.
  Its only caller is `$5F4E`, inside the game-selection handler's **Ctrl+2**
  branch (`$5F47 CMP #$F3` -> `$5F53 LDA #$02 / STA $4303`). It overwrites the
  randomised opening with a scripted one::

      604F  LDA #$06 / STA $82EA / $82F3 / $82F4  ; item-placement tweaks
      605A  LDA #$01 / STA $6502 / $6508
      6062  LDA #$02 / STA $64C2                  ; victim  = KANE
      6067  LDA #$04 / STA $64C3                  ; android = ASH
      606C  loop Y=0..6, copying four 7-entry tables:
            $608C -> $7936,Y   locations
            $6093 -> $7D46,Y   health
            $609A -> $7D56,Y   composure
            $60A1 -> $6572,Y   the composure mirror

  Decoded, that is a **much more desperate opening** than FULL:

  | crew | room | health | composure |
  |---|---|---|---|
  | DALLAS | LIVNG QTRS | 1 | 1 |
  | KANE | **dead (`$FE`)** | 0 | 1 |
  | RIPLEY | COMMDCENTR | 4 | 3 |
  | ASH | LIFE SUPPT | 0 | 1 |
  | LAMBERT | COMMDCENTR | 4 | 2 |
  | PARKER | COMMDCENTR | 6 | 3 |
  | BRETT | STORES 1 | 1 | 1 |

- **★ This retracts FV-1.9 / the "GameMode has no mechanical effect" note.**
  That conclusion was drawn on 2026-08-01 right after the invented oxygen budget
  was removed: with the budget gone the two modes looked identical, and
  `nostromo_ship()` ignores mode, so I recorded that SHORT changed nothing and
  left it as an open `[?]`. **I did not check whether the ROM had its own
  mode-specific setup.** It does — `$604F` — and it was reachable from the
  already-decoded selection handler the whole time. The lesson is the same one
  D-080 taught: when a mechanic seems to be missing, look for the *code path*
  that the menu option leads to, not just for the data it might have used.
- **Bonus: this re-explains `$6062`-`$6069`.** D-080 used that pair as evidence
  identifying `$64C3` as the android (KANE + ASH being the film's pairing) and
  called it a "hard-coded preset", guessing it was a debug leftover. It is not —
  it is SHORT mode's real setup. The identification stands; the framing was
  wrong.
- **The full SHORT-vs-FULL difference list**, now that `$604F` and the mode
  flag are both traced:
  1. **Opening is scripted, not rolled.** FULL rolls the victim from
     {DALLAS, KANE, LAMBERT} and the android from {DALLAS, KANE, ASH, PARKER};
     SHORT pins them to **KANE** and **ASH**.
  2. **You start in much worse shape.** SHORT scripts health 1/0/4/0/4/6/1 and
     composure 1/1/3/1/2/3/1, versus FULL's full per-crew health
     (6/5/4/5/4/6/5). Dallas and Brett open on 1 health, Ash on 0.
  3. **Crew are scattered, not grouped.** FULL places the six survivors 3+3 in
     COMMDCENTR / LIFE SUPPT; SHORT puts them in LIVNG QTRS, COMMDCENTR x3,
     LIFE SUPPT and STORES 1.
  4. **★ Two crew start already inside the ducts** — `$605A LDA #$01` into
     `$6502`/`$6508`, the `$6501` in-duct array at slots 1 and 7: DALLAS and
     BRETT.
  5. **Three items are moved to COMMDCENTR** — `$6051 LDA #$06` into
     `$82EA`/`$82F3`/`$82F4`, the `$82E3` item-room array at instances 7/16/17:
     a **TRACKER**, the **NET** and the **CAT BOX**, handed to you up front.
  6. **★ SHORT offers the in-game deck-plan INTRODUCTION; FULL skips it.**
     `game_init_mode ($4304)` reads the mode flag `$4303` (Ctrl+1 -> 1 at
     `$5F3F`, Ctrl+2 -> 2 at `$5F51`): mode **1 returns immediately**
     (`$431A CMP #$01`), anything else falls through to `$4405`, which prints
     "DO YOU WANT AN INTRODUCTION / PRESS Y OR N" and on **Y** shows the DECK
     PLAN KEY. So the short game is the teaching mode.
  7. **The map is identical.** Nothing mode-dependent touches the deck or
     neighbour tables — `nostromo_ship()` ignoring mode was right all along.

- **Action:** `SHORT_ADDRS`/`SHORT_VICTIM_SLOT`/`SHORT_ANDROID_SLOT` added to
  `alientools.gamedata` so the tables are **derived** into the snapshot
  (`SHORT_FIELDS`, `SHORT_SCENARIO`, `SHORT_DUCT_SLOTS`, `SHORT_ITEM_MOVES`);
  `Simulation` split into `_apply_full_opening` / `_apply_short_scenario` /
  `_apply_short_item_moves` (the last is separate only because the item catalog
  is spawned after the crew block). 5 tests, one of which pins that two
  different seeds give byte-identical SHORT state. **R-38 closed.**
  `[?]` The in-game deck-plan INTRODUCTION prompt (#6) is decoded but not yet
  rendered — the remake goes straight to play in both modes.

## D-084 — R-36 closed: the android's activated path, and the `$64CC` gates
- **Date:** 2026-08-02
- **`$52F1` — what a REVEALED android does.** Once `$64CC` is set, `$526A`
  diverts the android here instead of the dormant branch::

      52FC  CMP $7935 / BNE          ; is the ALIEN in my room?
      5306  JMP char_wander          ; ...yes (and surfaced) -> wander off
      5311  LDY #$01                 ; else scan crew 1..7
      5313  CPY $64C3 / BEQ next     ;   skip itself
      5318  LDA $6501,Y / BNE next   ;   skip anyone in a duct
      531D  LDA $7D45,Y / CMP #$02   ;   skip health < 2
      5324  LDA $7D55,Y / BEQ next   ;   skip composure 0
      5329  LDA $7935,Y / CMP $53E3  ;   must be in MY room
      5331  JMP $5345                ;   -> ** attack them ** (" HITS ")
      5339  LDY $7214 / JMP char_wander  ; nobody here -> wander

  So the activated android **hunts**: attack a valid target in its room, else
  `char_wander` — the same Alien-style random walk the panic path uses (D-026).
  Crucially it **never reaches `dispatch_char_action`**, so a revealed android
  obeys *nothing*: the silent order-drop stops being conditional on the Alien
  being nearby and becomes total.
- **`$5B56`-`$5B76` — the second `$64CC` gate.** This is the "is anyone still
  aboard?" scan that decides whether to end the game::

      5B58  LDA $7D45,Y / CMP #$02 / BCC next   ; skip dead/collapsed
      5B5F  CPY $64C3 / BNE $5B69               ; is this the android...
      5B64  LDA $64CC / BNE next                ; ...and revealed? -> SKIP IT
      5B69  LDA $7D55,Y / BEQ next              ; composure 0 -> skip
      5B6E  JMP $5B79                           ; someone alive -> carry on
      5B76  JMP endgame_dispatch                ; nobody -> end

  **A revealed android is not counted as crew**, so a lone surviving one is
  still ALL CREW LOST. That completes a consistent trio with the endgame
  mass-kill exemption (`$6130`) and the scoring exclusion (`$61A5`): once found
  out, the game stops treating it as a person in every place it matters.
- **Action:** `_android_ignores_order` now returns True unconditionally once
  revealed; `_apply_android_attack` wanders when it finds no target; the
  all-crew-dead check skips a revealed android. 4 more tests (20 in the suite).
  **R-36 closed.**

## D-083 — The DUCT network: rooms connect directly; junctions were invented
- **Date:** 2026-08-02
- **The question:** what a crew member actually finds after `REMVGRILLE` — where
  can they go once inside the ducting?
- **★ The remake's model was wrong in shape, not just in detail.** `core/map.py`
  modelled ducts as a graph of `Junction` nodes joined by vents, with grilles
  linking a room to a junction. **The original has no junction nodes at all.**
  Ducts connect **rooms directly**, via four tables of one neighbour room per
  room:

  | table | direction | evidence |
  |---|---|---|
  | `$80F5` | NORTH | `$40B8` matches it, then prints `$8081` " NORTH   " |
  | `$8117` | EAST  | `$40CE` -> `$8095` " EAST    " |
  | `$8139` | SOUTH | `$40E4` -> `$808B` " SOUTH   " |
  | `$815B` | WEST  | `$40FA` -> " WEST    " |

  A **self-reference (`table[room] == room`) is the ROM's encoding for "no duct
  exit that way"**. The direction assignment is therefore not guessed — the same
  routine that tests each table prints the matching compass word.
- **The same four tables drive everything duct-related**: the in-duct MOVE TO
  menu (`$81EF`-`$8271`, which walks all four and lists each non-self exit) and
  the Alien's own duct hops (`$8AA2`-`$8ACB`, which picks one by roll band and
  sets bit 7 on the destination).
- **How a character enters** (`$7373`-`$7392`): a destination arrives with
  **bit 7 set** to mark it a duct move; the ROM strips it and flags the
  character::

      7373  SEC / SBC #$80 / STA $7935,Y   ; the real room id
      7379  LDA $6501,Y / BNE skip         ; already inside?
      737E  LDA $6571,Y / CMP #$02 / BCC   ; composure gate
      7385  LDA $7D55,Y / BEQ skip         ; nothing to lose at 0
      738A  SEC / SBC #$01 / STA $7D55,Y   ; ** -1 composure on entry **
      7390  LDA #$01 / STA $6501,Y         ; now IN DUCT

  **Entering costs one composure; staying inside gains one per tick**
  (`$729C ADC #$01`). Those are not in conflict — and together they are a
  neat piece of design: the crawl in is frightening, hiding is a relief. It also
  reinforces D-059's polarity from a third direction.
- **The decoded map, validated three ways:** 76 directed edges over 34 rooms;
  **every room has at least one exit**; the graph is **fully connected** (all 34
  reachable from any one). But it is **not symmetric** — only **54 of the 76**
  edges have a matching return edge, so 22 duct runs are genuinely one-way.
  Recorded and pinned by a test rather than "tidied up".
  CORRIDOR 4 is the busiest node (all four directions: armoury / other_list_2 /
  mess / cryo_vault).
- **Action:** `DUCT_ADDRS` added to `alientools.gamedata` so the tables are
  **derived** into `gamedata_snapshot` (`DUCT_DIRECTIONS`, `DUCT_NEIGHBOURS`)
  rather than transcribed; `ShipMap.duct_exits()` is the new accessor; the
  junction model is documented as an invention kept only for synthetic test
  maps; the move path now applies the entry composure cost. 8 tests.

## D-082 — The location pointer is an animated 4-frame expanding rectangle
- **Date:** 2026-08-01
- **Prompted by:** the user describing the move/INDICATE destination marker as
  "a sprite of animated rectangles".
- **Confirmed.** `$4FCB`, in the IRQ update chain::

      4FCB  LDA $64BE / BEQ hide      ; only while the pointer is active
      4FD0  LDA #$01 / STA $D028      ; sprite 1 colour = WHITE
      4FD5  DEC $657A                 ; the animation frame
      4FD8  CMP #$B8 / BNE
      4FDF  LDA #$BC / STA $657A      ; wrap $B8 -> $BC
      4FE4  LDA $657A / STA $07F9     ; sprite 1's POINTER
      4FEB  hide: LDA #$00 / STA $D002

  So sprite 1 cycles pointers **$BC -> $BB -> $BA -> $B9 -> $B8 -> ($BC)** once
  per IRQ tick. Decoding those five slots out of the graphics bank shows
  **concentric expanding rectangles** ($BC smallest, $B9 largest) with `$B8`
  resolving into a small human figure — a zoom-in "locate" animation that lands
  on the person. Exactly as described.
- **Position** comes from `$76D7`: `LDY $64F7` (the target room) then
  `LDA $758D,Y -> $D002` / `LDA $75B1,Y -> $D003` — the same two tables R-08 /
  D-058 already decoded for the character marker. `$64BE` is the on/off flag,
  set by seven routines (`$76D7` is INDICATE LOCATION's).
- **Action:** filed as R-37; the remake currently draws a static flashing box.
- `[?]` Which of `$64BE`'s seven setters correspond to the MOVE-destination
  display versus INDICATE LOCATION is not yet separated.

## D-080b — The android **silently drops your orders** (the reported symptom)
- **Date:** 2026-08-01
- **Prompted by:** the user recalling, from ~20 years ago, that *"the android
  just stopped responding to my input"*. That is a precise, checkable claim, and
  it pointed straight at the one branch D-080 had left `[?]` — `$5168 CPY $64C3
  / BEQ $5265`, which diverts the android out of the normal order path.
- **`$5265` decodes to exactly that symptom**::

      5265  LDA #$04 / STA $03E8       ; queue a sound
      526A  LDA $64CC / BNE $52F1      ; already found out? -> activated path
      5272  LDA $6501,Y / CMP $6501    ; same duct state as the ALIEN (slot 0)?
      527A  LDA $7935,Y / CMP $7935    ; ...and the same room?
      5282  LDA $650C,Y / BEQ normal   ; is there a pending action at all?
      528A  LDA $7D45,Y / CMP #$04
      528F  BCC char_wander            ; health < 4 -> it panics instead
      5294  LDA #$00 / STA $650C,Y     ; ** clear the pending action **
      5299  JMP check_deferred_move    ; ** and skip it: the order is DISCARDED **

  **No message, no refusal — the order simply evaporates.** The gate is
  co-location *with the Alien*: in the film Ash protects the creature, and this
  is that, mechanically. A hurt android (health < 4) panics instead of
  stonewalling, so the symptom is specific to a healthy one.
- **★ And there is a reveal.** `$52A4`-`$52DA` is how the crew find out. Once
  the **Alien has taken >= 6 damage** (`$52A7 CMP #$06` — the crew have been
  fighting it), the game scans for someone standing in the android's room who is
  out of the ducts, health >= 2 and not broken (`$52CA`). If one is there it
  stores the android's own slot into **`$64CC`** (`$52D7`) **and writes it to
  `$D021`** (`$52DA`) — **flashing the screen background**. That is the player's
  only tell; the word ANDROID is still never printed. From then on `$526A`
  routes the android down its activated path (`$52F1`) instead, and `$64CC` also
  gates its Narcissus handling (`$5B64`, `$5BD8`).
- **The whole arc, then:** *dormant* (passes for crew, but silently eats your
  orders whenever it is with the Alien) -> *found out* (background flash once the
  Alien is wounded and someone is watching) -> *activated*.
- **Action:** `ANDROID_OBEY_MIN_HEALTH`, `ANDROID_REVEAL_ALIEN_DAMAGE`,
  `ANDROID_REVEAL_MIN_HEALTH`, `GameState.android_revealed`,
  `Simulation._android_ignores_order()` wired into `_apply_order`, and
  `_reveal_android()` on the tick. 7 more tests (16 in the android suite).
- **Method note:** a 20-year-old player memory turned out to be a better lead
  than any static sweep — it named a *symptom*, and symptoms map onto branches.
  Worth asking for more of them.
- `[?]` Still not modelled: the activated path `$52F1` itself, and the
  `$64CC`-gated Narcissus rules — R-36.

## D-079 — The instruction pages: the obvious source file is the wrong one
- **Date:** 2026-08-01
- **Finding:** R-12 and R-31 both ended with "the 10 instruction pages" as their
  last open piece, and answering **Y** to DO YOU WANT INSTRUCTIONS? was a stub
  that behaved like N.
- **★ The trap:** the disk carries an `INSTRUCTIONS.seq` file, and it reads like
  the instruction text — I built a pager on it and rendered it before checking.
  **It is the printer copy, not the screen copy.** `MENU1.prg`'s BASIC opens it
  only behind a printer prompt::

      PRINT "   WOULD YOU LIKE THE INSTRUCTIONS."
      PRINT "      SENT TO THE PRINTER?  (Y/N)"
      ...
      F$ = "INSTRUCTIONS,S,R" : OPEN 15,8,15 : OPEN 2,8,2,F$

  Its lines run to **69 characters** — they cannot fit a 40-column screen, which
  is exactly how the render looked: either truncated, or hard-wrapped into
  mid-word breaks. Neither was the original.
- **The real source** is a long run of BASIC `PRINT` statements in the same
  program (lines **10080-12180**), already hand-wrapped by the authors to <= 40
  columns. Pages are delimited by `PRINT CHR$(147)` (clear screen), and there
  are **exactly 10** of them — which is where "the 10 instruction pages" in the
  todo came from all along. Each ends with "PUSH ANY KEY TO CONTINUE" and
  carries its own heading (THE GAME / PERSONALITY CONTROL SYSTEM / SCREEN
  DISPLAYS / COMMAND MONITOR / HINTS FOR SURVIVAL).
- **Method note:** the extractor walks the BASIC linked list and detokenises.
  One trap worth recording: `SPC(` and `TAB(` are **single tokens that already
  include the open paren** — there is no `(` byte after them — so a parser that
  looks for one silently drops every indent. That is what centred the
  "INSTRUCTIONS" heading wrongly until it was fixed.
- **Also visible in the recovered text:** the game tells the player *"THIS
  RANDOM START TO THE GAME IS COMPLICATED BY YOUR NOT KNOWING WHICH MEMBER OF
  THE CREW IS AN ANDROID"* — an **android** mechanic the remake does not model
  at all. Filed rather than implemented: nothing in the decoded tables has been
  traced to it yet, so building it now would be invention.
- **Action:** new `core/instructions.py` (extraction only — the wording, line
  breaks and page boundaries are the loader's), `Screen.INSTRUCTION_PAGES` +
  `GameFlow.instruction_page`, `_draw_instruction_pages` rendering in the ROM
  font on the 40-column grid. **Y now shows the real pages**; N still skips.
  8 tests, including one that guards the negative finding by asserting the SEQ
  file is too wide to be screen text.

## D-078 — R-01's digits located: they are at `$B0-$B9`, not `$30-$39`
- **Date:** 2026-08-01
- **Finding:** R-01 had carried a `[?]` since D-039 — "digits and period still
  unlocated in ALIEN's own charset". An earlier pass had assumed the ASCII
  positions `$30-$39` from label-table byte offsets and was **disproven by
  rendering them** (graphic noise). Nobody had then searched for where they
  actually are.
- **Method (cheap and decisive):** ALIEN's font is *cut-out* — the letter is the
  glyph's **0**-bits — so a digit there should be roughly the **inverse** of the
  same digit in the standard chargen ROM (which D-065 had just made available).
  Inverting each ROM digit and scoring it against all 256 ALIEN glyphs pointed
  straight at a pattern: `'1'`→`$B1`, `'2'`→`$B2`. Rendering `$B0`-`$B9` cut-out
  then shows an unmistakable **0 1 2 3 4 5 6 7 8 9**. They are in the
  **reverse-video half** (`$30 | $80`), which is why the ASCII slots looked like
  noise — those are genuinely different glyphs.
- **Verified against the live machine:** the in-game VIC char base really is
  `$2000` (`$D018 = $19`, `$DD00 = $C7` -> VIC bank 0), and the glyphs read back
  from `$2000` match `out/charset.bin` byte for byte — so the extracted charset
  *is* the one the game runs, and the finding is about the real font.
- **Also located:** `%` = `$A5` (clear), and the only punctuation dot in the set
  is `$AC` (low, small — a comma/period form).
- **★ A quiet correction:** **`$AE` is BLANK** — all 1-bits, exactly like the
  `$A0` space. So the `"O.K."` that string dumps have been showing for `$7CEB`
  was **the decoder's ASCII assumption** (`$AE & $7F = $2E = '.'`), not a glyph
  the game draws. The ROM's health word renders without periods. The period is
  therefore still deliberately **unmapped** rather than guessed at another cell.
- **Action:** digits 0-9 and `%` added to `_ASCII_TO_SCREEN_CODE` with the
  citation; two drift guards that pinned the old "digits stay unmapped" state
  updated to pin the new mapping instead (and to keep asserting the ASCII slots
  are not used). In-game text with numbers — the DAMAGE percentage, the
  auto-destruct countdown, the competence rating — now renders in the game's
  own font instead of falling back to SysFont.

## D-077 — The ending is COMPOSED from independent axes; the score has a base
- **Date:** 2026-08-01
- **Finding:** two open items (R-14, R-33) both hinged on `select_outcome
  ($60A9)`, which had never been read past its first branch. Reading it through
  settles both and corrects the remake twice.
- **★ The end screen composes independent outcome lines; it does not pick one.**
  The remake showed a single `_WIN_MESSAGES` line. `select_outcome` writes up to
  four *independent* strings to fixed screen rows, one per axis:

  | screen | row | string | source |
  |---|---|---|---|
  | `$04F0` | 6 | `THE ALIEN IS DEAD` | `$6372`, 17 |
  | `$0540` | 8 | `THE NARCISSUS RETURNS TO EARTH` | `$63BA`, 30 |
  | `$0590` | 10 | `THE ALIEN AND ITS EGGS ARE UNLEASHED UPON THE PLANET` | `$6383`, 55 |
  | `$0608` | 13 | `ALL CREW LOST` | `$63D8`, 13 |

  That is exactly what two *independent live captures* had already shown —
  `losingscreen.png` ("The Nostromo returns to Earth" / "The Alien and its eggs
  are unleashed…" / "All crew lost") and FV-2d's `fv2d_start.png` ("The
  Nostromo is destroyed" / "The Alien is dead" / "All crew lost"), on different
  combinations. The hypothesis filed in FV-1c2b is confirmed from the code.
- **★ The score has a base term set before the survivor accrual**, which D-070
  missed by starting its trace at `$61A5`:
  ```
  60DF  LDA #$05 / STA $6411    ; the Alien is dead (damage >= 50)
  611C  LDA #$78 / STA $6411    ; 120 — the eggs-unleashed ending
  ```
  120 is deliberately past the `$621D CMP #$65` clamp, so the worst ending
  scores **0**. **Corroborated by the live capture in the same note:** it read
  "The Alien is dead" / "All crew lost" with **"Competence Rating: 05%"** —
  base 5, nobody left to accrue, wrecked ship forfeiting the damage bonus.
  D-070's formula plus this base reproduces 05 exactly.
- **Action:** `SCORE_ALIEN_DEAD` / `SCORE_EGGS_UNLEASHED` + `_base_score()`
  added to `core/scoring.py`; `_draw_end` rewritten to compose the axes at the
  ROM's own rows. R-14 and R-33 closed. 2 new tests (13 in the scoring suite).
  A test-design trap recorded with them: an **empty crew roster is not
  neutral** — with nobody alive the base is 120, which clamps to 0, so tests
  isolating the damage term must supply a survivor.
- `[?]` Still not traced: the exact `$64CF` / `$64E3` / `$7935 == $22` branch
  polarity that selects *which* combination appears for the remaining outcomes
  (`$60F9`-`$610A`). Left alone rather than guessed; it needs live traces of
  more ending combinations.

## D-076 — R-31 closed: an automated side-by-side harness, 13/13 passing
- **Date:** 2026-08-01
- **Finding:** R-31 ("side-by-side behaviour verification vs. emulator") had
  been treated as needing a human comparison. Most of it does not: the game's
  state lives in flat byte tables, so the comparison can be **numeric**.
- **`tools/vice-mcp/r31_side_by_side.py`** boots the real disk to the play
  screen (using the *screen*, not the mislabelled `$64BB`, as the signal), dumps
  `$7935`/`$7D45`/`$6571`/`$6586`/`$64EE`/`$653F`/`$651C`/`$4B37`/`$82E3`, builds
  the equivalent remake `Simulation`, and diffs. **All 13 checks pass**, including
  four exact-equality ones:
  - **item placement**: the remake's 20 instances match `$82E3` **exactly**
    `[21,22,24,6,16,6,6,16,17,18,19,27,32,2,2,2,24,23,30,20]`;
  - **composure**: `[4,4,3,4,3,4,3]` == `$6571` exactly;
  - **walk ticks**: `[4,4,3,4,3,4,3]` == `$6586` exactly;
  - **start health**: `[6,5,4,5,4,6,5]` == the ROM's per-crew table.
  The opening death is random in both, so the crew tables are compared
  structurally (exactly one dead, `$FE` sentinel present) rather than by identity.
- **★ D-067's static prediction confirmed live.** D-067 reasoned from the code
  that `$65B1`'s init loop runs `CPY #$14` (20 iterations, shared with the
  20-entry item copy) and therefore overruns the 16-entry charge table, writing
  4 string bytes over its **own master's** first four entries. Read back on the
  real machine: `$4B47[0:4] = C9 13 A0 05` — exactly the bytes at `$4B57`. A
  prediction made purely from reading the disassembly, verified byte for byte.
- **★ D-073's threshold confirmed live.** The captured machine had been playing
  long enough for the Alien to corrode one room: `$653F[20] = 4` with
  `$651C[20] = 1`, and every other room 0/0. The alarm latched exactly as the
  damage crossed 4 (`$558C CMP #$04 / BCS`). The harness now asserts that
  invariant across all 34 rooms and checks the remake reproduces the same latch.
- **Action:** R-31 closed. The harness is re-runnable and is the honest answer
  to "is the remake behaving like the original" for everything expressible as
  state; what it cannot cover (moment-to-moment *feel*) is not something a diff
  could ever settle.

## D-074 — R-20 closed objectively: the intro's SID stream is now bit-exact
- **Date:** 2026-08-01
- **Why it was open:** R-20 ("legato held notes + pad gain") was tagged as
  needing a human ear
  as a listening judgement. It turned out to be **measurable**, because
  `intro.py` renders by running the game's *own* 6502 player and capturing its
  `$D400-$D418` writes — so those writes can simply be diffed against the real
  machine's.
- **Method** (`tools/vice-mcp/r20_sid_verify.py`): boot the real disk to the
  TITLE screen where the player runs (`$60A8 != 0`), sample `$D400-$D418` plus
  the jiffy clock `$A0-$A2`, rebuild the remake's per-frame register state from
  `sid_writes`, align on the voice-1 frequency contour, and diff.
- **First run: 90/90 alignment on the melody, and 13 of 14 meaningful registers
  matched 100%** — notes, gates, ADSR, filter routing and volume were already
  exact. The lone outlier was **`$D416` (filter cutoff hi) at 27.8%**.
- **★ That outlier was a real bug.** `$D416` is the one register not written
  from the player's own data: the player copies **ENV3** (`$D41C`) into it each
  jiffy. Our voice-3 envelope was retriggering where the real chip's does not.
  The player rewrites voice 3's control `$20` -> `$21` **inside a single
  jiffy**; the 6581 samples the gate bit far more slowly than the CPU can
  rewrite it, so that pair is a **write glitch the chip never sees**. We treated
  it as a genuine retrigger, producing an envelope spike and therefore a filter
  cutoff sweep climbing to 243 — **a sweep the original does not have.**
- **Verified before believing it.** Two traps were ruled out first:
  1. *Is `$D416` even readable?* SID registers are write-only on real hardware.
     Wrote `$5A` and read it back — VICE returns it. The measurement is valid.
  2. *Did the sampling alias?* The first capture's gap (~23.7 jiffies) sat
     almost exactly on the player's 24-jiffy gate period, so it probed only one
     phase. A second capture at ~6.6-jiffy intervals covered **all 24 phases**:
     `$D41C` = 0 and `$D416` = 0 in all 160 samples. A third, **124-second**
     capture — longer than the full 102.4 s cycle — gave **246/246 zeros**.
     There is no filter sweep in the original; the module docstring's "one full
     102.4s filter-sweep cycle" was describing our bug.
- **Fix:** `_Envelope.gate_off` records the state it interrupted, and a
  `gate_on` arriving with **no elapsed samples** restores it instead of
  restarting the attack. Any `step()` closes the window, so ordinary note
  retriggers are untouched.
- **Result: 2250/2250 registers agree — 100.0%.** The intro's music is now
  provably identical to the real machine's at the register level.
- **Consequence to judge by ear (the honest remainder):** with the cutoff
  correctly pinned at 0, the rendered `out/intro.wav` drops from peak -1.2 dBFS
  to **-21.5 dBFS** (RMS -36.5), because our state-variable filter is nearly
  closed at minimum cutoff. The 8-second swell survives intact (RMS 38 -> 478
  -> 682 over 0-2s / 6-8s / 20-22s). Whether the real 6581 passes more signal at
  cutoff 0 than our model does cannot be settled through this tooling — it needs
  actual audio capture, not register reads. Real 6581 filters vary widely
  between chips, so this is left measured-and-flagged rather than compensated
  with a guessed gain. 4 regression tests.

## D-073 — The malfunction TRIGGER found; `$5753,X` identified; two breach gates
- **Date:** 2026-08-01
- **Finding:** D-072 decoded the malfunction *tables* but not what raises them.
  The trigger is `damage_room_b ($5587)` — and the answer is that there is no
  separate trigger at all: the routine latches the alarm and then **falls
  straight through** into the message dispatcher.
  ```
  5587  LDA #$03 / STA $03E8      ; queue sound id 3
  558C  LDA $653F,X / CMP #$04
  5591  BCS $5594 ... else RTS    ; damage < 4 -> nothing
  5594  CMP #$0F / BCC $559E      ; damage >= 15 -> $5658 (severe/breach)
  559E  LDA $651C,X / BNE RTS     ; one-way latch (D-044 re-confirmed)
  55A6  INC $651C,X               ; raise the alarm 0 -> 1
  55A9  CPX #$11 / BCC $55C1      ; rooms < 17 skip the fire flag
  55AD  CPX #$14 / BCS $55C1      ; rooms >= 20 skip it too
  55B1  LDA #$06 / STA $5753,X    ; rooms 17-19 only
  55C1  LDA $54A3,X               ; -> the message dispatcher (D-072)
  ```
- **★ `$5753,X` is the per-room FIRE flag.** It is written 6 **only** for rooms
  17-19 — which are **exactly** the rooms `$54A3` assigns malfunction type 4
  ("FIRE IN …"), an independent confirmation of D-072's table from a second
  direction — and FIGHT FIRE clears it (`$58CF`, D-066). That closes one of the
  two `[?]`s D-066 had to leave open.
- **★ There are TWO hull-breach gates, not one.** (a) a **pre-add** check at the
  weapon-hit site (`$4AF8 BCC $4AFD` / `$4AFA JMP hull_breach`); and (b) inside
  `damage_room`, past 15, `$5658 CMP #$14 / BNE $565F` — which breaches on
  damage **exactly 20**, and otherwise merely raises the alarm to stage 2
  ("severe", `$5667 LDA #$02 / STA $651C,X`).
- **`HULL_BREACH_THRESHOLD = 15` upgraded from `[?]` to `[C $5594]`.** The value
  *and* the post-add timing were both already right: `$4B00 STA $653F,Y` stores
  the damage **before** `$4B05 JSR damage_room` reads it back. The remake's note
  claiming the ROM check is "pre-add" was true only of gate (a). The single
  global gate remains a simplification of the two-gate system — still flagged,
  deliberately not restructured here (it needs `sim.py` surgery, not a constant).
- **Action:** `MALFUNCTION_MESSAGES`, `ROOM_MALFUNCTION_TYPE`,
  `MALFUNCTION_FIRE_TYPE`, `ROOM_FIRE_FLAG` added with citations;
  `GameState.room_fire` + `GameState.malfunction` added; `add_room_damage`
  raises the banner as the alarm latches (`_raise_malfunction`); FIGHT FIRE
  clears the fire flag as well as the alarm; the status panel shows the
  ":WARNING: …" line. 9 tests. R-35 closed the same day it was filed.

## D-072 — The systems-malfunction system decoded (FV-0.5's last routine)
- **Date:** 2026-08-01
- **Finding:** the `$54C5` malfunction strings had never been attributed. The
  dispatcher at `$55C1` resolves them through **three parallel tables**:
  ```
  55C1  LDA $54A3,X       ; X = room -> that room's malfunction TYPE (0 = none)
  55C6  STA $53E4
  55C9  ; copy an 8-byte prefix from $5485
  55D9  LDA $5473,Y       ; type -> message LENGTH
  55DF  LDA $547C,Y       ; type -> message OFFSET into the blob
  55E5  LDA $54C6,Y       ; the blob base; copy `length` bytes to $07C8
  55F2  LDA #$04 / CMP $53E4 / BNE   ; type 4 alone gets a room name appended
  ```
- **The eight message types decode exactly** (length/offset tables align to the
  byte with the blob at `$54C6`):

  | type | length | message |
  |---|---|---|
  | 1 | 28 | `PARTIAL SYSTEMS CONTROL LOSS` |
  | 2 | 20 | `COMPUTER MALFUNCTION` |
  | 3 | 22 | `CRYOGENICS MALFUNCTION` |
  | 4 | 8 | `FIRE IN ` **+ the room name** (the `$55F2` special case, which is why `set_room_screen_ptr` is called at `$5604`) |
  | 5 | 28 | `ENVIRONMENTAL IRREGULARITIES` |
  | 6 | 20 | `NARCISSUS STATUS RED` |
  | 7 | 30 | `OVERRIDE OPTION EXPIRY    MINS` |
  | 8 | 30 | `SHIP WILL DESTRUCT IN   MINS  ` |

- **★ `$54A3` is a STATIC per-room assignment** — 34 bytes, never written
  anywhere in the program (no `STA/STX/STY $54A3` exists). Each room owns one
  fixed malfunction type:

  | room | slug | type |
  |---|---|---|
  | 6 | `commdcentr` | 1 — PARTIAL SYSTEMS CONTROL LOSS |
  | 7 | `computer` | 2 — COMPUTER MALFUNCTION |
  | 15 | `cryo_vault` | 3 — CRYOGENICS MALFUNCTION |
  | 17, 18, 19 | `other_list_1/2`, `engine_1` | 4 — FIRE IN … |
  | 25 | `laboratory` | 5 — ENVIRONMENTAL IRREGULARITIES |

  **The semantics line up 3-for-3** — the comms centre loses systems control,
  the computer room reports a computer malfunction, the cryo vault reports
  cryogenics. That is not coincidence, so it **independently cross-validates
  the `ROOM_SLUGS` ordering** as a side effect.
- Types **6-8 appear in no room** — they belong to other systems: NARCISSUS
  STATUS RED to the shuttle, and the two `MINS` countdowns to the auto-destruct
  (D-060), which already models them.
- **Bearing on an older open question:** GAMEDATA §3 #8 wondered whether
  "OTHER LIST" rooms 17/18 are real rooms or menu-pagination artifacts. They
  carry real malfunction assignments here, which is evidence for "real", though
  a positional table alone cannot settle their *names*. Recorded, not resolved.
- **Action:** FV-0.5's last ⬜ closed. Not implemented in the remake — the
  *trigger* (when the dispatcher runs for a room) is a separate question from
  the table, and inventing a trigger is exactly what the standing rule forbids.
  Filed as a scoped follow-up instead.

## D-071 — R-19b closed, plus behaviour notes for four FV-0.5 routines
- **Date:** 2026-08-01
- **R-19b — the "current character" is `$64FB`, and the remake already models
  it.** `MenuController.selected_crew` maps one-for-one: it starts **unset**
  (`game_init_mode $43DE` stores 0, `$42F4` clears it the same way ⇒ `None`),
  holds exactly one index, and bounces back to 0 when an incapacitated crew
  member is picked. It drives all three things the ROM keys off `$64FB`: the
  map marker (D-058), the fixed portrait (`$6667`, D-053/D-055), and the
  **heartbeat rate** — `fear_band ($7DC5)` does `LDY $64FB / JSR fear_alert`,
  so the divider is the *current* character's, not the roster's (D-061).
  3 drift guards. The audio half stays with R-20/R-21 (R-21 blocked).
- **`pause_check ($6483)`** — returns immediately while `$64BB != 0`;
  otherwise polls the KERNAL key-scan cell `$91` for scan code `$BB` and, on a
  match, spins in a wait loop at `$648F` until `$91` reads `$F9`. Inside that
  loop `$028D` (the shift/CTRL/Commodore flag) equal to **2** — the Commodore
  key alone — escapes via `JMP $644E`. So: a hold-to-pause with a modifier
  escape, not a toggle.
- **`alien_apply_move ($8C6B)`** — three instructions of consequence::

      8C6B  JSR find_crew_with_alien
      8C6E  CPY #$08 / BEQ $8C75    ; Y == 8 = "none found" -> RTS
      8C72  JMP $89B4               ; otherwise -> the encounter handler

  i.e. after the Alien moves, if any crew member is now in its room the
  encounter path runs; otherwise nothing happens. `Y == 8` is the not-found
  sentinel (crew occupy slots 1..7).
- **`init_c ($5DEB)`** — the **title** screen's VIC setup (called from `$4023`),
  distinct from the selection screen's `sub_screen_setup ($5FC3)`: sprites off
  (`$D015`/`$D01B` = 0), `$D025` = 7 / `$D026` = 1 (sprite multicolours),
  **`$D021` = `$0D` (LIGHT GREEN)**, no expansion (`$D017`/`$D01D` = 0),
  **`$D020` = 0 (BLACK border)**, and all eight sprite colours `$D027`-`$D02E`
  = 5 (GREEN). Two independent confirmations fall out: the remake's title text
  is drawn as cut-out glyphs showing "the title's light-green `$D021`" — that
  is this `$0D` — and the **black front-end border** measured live for D-064
  is set right here in code, not only observable on screen.
- **`game_init_mode ($4304)`** — fills all four screen pages (`$0400`/`$0500`/
  `$0600`/`$06E8`, Y = 0..255) with `$A0` to blank the display to solid cells,
  then reads the mode flag `$4303`: exactly **1** zeroes the flag and returns,
  anything else falls through to `JMP $4405`.
- **Action:** R-19b ticked; FV-0.5's routine list reduced to the two genuinely
  open entries (the CONTROL-panel order/menu-draw, which has in fact been
  reimplemented from `$5799`/`$A648`, and the systems-malfunction strings).

## D-069 — `health_band` ($7D94): the O.K./WOUNDED cut is an ABSOLUTE 4
- **Date:** 2026-08-01
- **Finding:** the health-status words had no decoded selector — `$7CEA` is
  referenced nowhere, so it had never been traced. It is found by looking for
  the structural **sibling of `fear_band ($7DC5)`**, which sits 49 bytes later:
  `health_band ($7D94)` has the identical shape (compare chain -> `index_x10`
  -> copy 9 chars from a 10-byte-stride table).
  ```
  7D94  LDA $7D45,Y           ; the crew member's health
  7D97  CMP #$03 / BCC $7DA9  ; health 0-2 -> index = 3 - health
  7D9B  CMP #$04 / BCC $7DA4  ; health 3   -> index 1
  7D9F  LDA #$00              ; health >=4 -> index 0
  7DB8  LDA $7CEB,Y           ; 9 chars from the table at $7CEB (stride 10)
  ```
  Table: `O.K.` / `WOUNDED` / `COLLAPSED` / `DEAD` at `$7CEB`+0/10/20/30. Note
  the base is **`$7CEB`, not `$7CEA`** — `$7CEA` is a leading pad byte, which
  is why `$7D13` (composure, D-059) sits 41 rather than 40 bytes later.
- **The bug this exposed:** the boundary is an **absolute 4**, not a comparison
  against the member's own maximum. The remake used
  `"O.K." if health >= full_health else "WOUNDED"`, and start health is
  **per-crew** (6/5/4/5/4/6/5, `$7D4D`) — so Dallas (max 6) read "WOUNDED" at
  health 5 where the real game still reads "O.K.". Survivability is per-crew;
  the displayed *word* is not.
- **Second quirk:** health **2 and 3 both** map to WOUNDED — 3 via the explicit
  `$7DA4 LDA #$01`, and 2 via the `3 - health` arm. The mapping is not linear.
- **Action:** `HEALTH_OK_AT_LEAST = 4` / `HEALTH_WOUNDED_AT_LEAST = 2` added
  with citations; `CrewMember.status` rewritten to the ROM's bands. The old
  test asserted the wrong behaviour explicitly ("WOUNDED shows relative to each
  own maximum") and was updated; a new table-driven test walks health 0-6
  against every real per-crew maximum.

## D-070 — The COMPETENCE RATING formula, decoded end to end
- **Date:** 2026-08-01
- **Finding:** the ending screen's "COMPETENCE RATING:   %" (`$63F8`) was a
  hard-coded `--%` in the remake. The whole score is in `$6411`, built by
  `$60A9`-`$62B5`.
- **Per surviving crew member** (loop `$61A5`-`$6217`, slots 1..7, gated on
  `health >= 2` at `$61B0` — the same acting floor used everywhere):
  **+4** (`$61BB ADC #$04`); **+1** more if `health >= 4` (`$61C6 CMP #$04`,
  the *same absolute threshold* as D-069's `health_band`); **-3** if composure
  is exactly 0 (`$61E2 BNE` / `$61FA SBC #$03`) — the same test that appends
  the 9-char string **"IS INSANE"** at `$63E5`.
- **Ship-condition term** (`$6231`-`$6278`), computed **only when `$64CF == 0`**
  — the same flag that selects the "lost" ending at `$60AE`. It walks the
  34-entry room-damage table `$653F` accumulating into `$640F`: `+= d`, then
  `+10` for `5 <= d < 15` (`$6251 ADC #$0A`) or `+25` for `d >= 15`
  (`$625D ADC #$19`). After **each** room, `$6265 CMP #$46` — once `$640F`
  reaches 70 the walk aborts to the print and **no bonus is added at all**
  (not a bonus of zero: a wrecked ship never reaches `$626E`). Surviving all 34
  rooms adds `70 - $640F`.
- **Presentation:** `$621D CMP #$65` clamps 101+ to **0**, and `$6288`-`$62B5`
  emits exactly **two digits** (repeated `-10` for the tens, `ADC #$B0` to make
  reverse-video screen codes) — so the rating is always 0-99.
- **Action:** new `core/scoring.py` with every term cited; the renderer now
  prints the real two-digit rating. 11 tests.
- `[?]` The `$64CF == 0` gate means the damage bonus lands on the **lost**
  ending and is skipped otherwise, which reads counter-intuitively. Recorded
  exactly as decoded rather than "corrected" to what seems more sensible; the
  flag's meaning beyond `$60AE` is not traced.

## D-068 — `$8A36` is a pure weighted-random route selector (no scripted pursuit)
- **Date:** 2026-08-01
- **Finding:** the audit item asked what at `$8A36` "triggers scripted
  pursuit/retreat vs. the random walk". **Nothing does** — the routine is a
  weighted random selection with no pursuit branch at all:
  ```
  8A36  JSR rng
  8A39  CMP #$0C / BCC $8A40
  8A3D  JMP alien_enter_duct      ; roll 12-15 (4/16) -> duct
  8A40  CMP #$03 / BCS ...        ; roll 0-2   -> table $7A3A
  8A50  CMP #$05 / BCS ...        ; roll 3-4   -> table $7A5E
  8A5A  CMP #$07 / BCS ...        ; roll 5-6   -> table $7A82
  8A64  CMP #$09 / BCS ...        ; roll 7-8   -> table $7AA5
  8A6E  LDA $7AC8,Y               ; roll 9-11  -> table $7AC8
  8A47  STA $64E6                 ; the chosen destination room
  8A4A  LDA #$3C / STA $64EE      ; action timer = 60
  ```
  Each table is indexed by the Alien's **current room** (Y) and yields a
  destination. Escalating pursuit is a separate mechanism (the `$4781`
  aggression accumulator, D-012), not a branch in this routine.
- **Already modelled correctly** — `alien.py`'s `_route_band` and
  `constants.ALIEN_DUCT_THRESHOLD` match band-for-band; this is an independent
  confirmation, not a change.
- **Third confirmation of `ALIEN_MOVE_TICKS = 60`:** the explicit `LDA #$3C`
  here joins D-038's static decode and the live reload of 60 captured during
  R-29's measurement (D-063).
- **Action:** audit item ticked. The genuinely open Alien question is
  unaffected and stays where it was: `alien_ai ($8A74)`'s duct-to-duct network,
  which the remake simplifies to "hide in place" (FAITHFULNESS, Alien row).

## D-066 — FIGHT FIRE fully traced (`$5889`); it IS a separate special
- **Date:** 2026-08-01
- **Finding:** FAITHFULNESS had FIGHT FIRE as the Specials row's remaining
  `[?]` ("not wired; its gate is in the 20-entry damage index space,
  unresolved"), and `menu.py` asserted it was *"not a separate special:
  modelled as USE of the fire extinguisher"*. **Both were wrong.** `$5889` sits
  in the specials dispatch chain — immediately after the `CMP #$02/#$03/#$04/
  #$05` arms at `$5869`-`$5883` — and has its own 10-char menu label
  ("Fight Fire") and its own result label ("Fire Out  ", copied from `$5950`).
- **The handler, instruction for instruction:**
  ```
  5889  LDY $64FB             ; the commanded character
  588C  JSR find_room_object  ; an object in that character's room
  588F  TYA
  5890  CMP #$08 / BCC rts    ; gate: object index must be 8, 9 or 10
  5894  CMP #$0B / BCS rts    ;   (the fire-extinguisher band)
  5898  TAX
  5899  LDA $4B37,X           ; its remaining charge
  589C  BNE spend
  589E  ; charge 0 -> print "EXTINGUISHER IS EMPTY" ($4B5A, 21 chars) and RTS
  58AC  spend: DEC $4B37,X    ; consume exactly one charge
  58AF  ; SID: gate off, freq $28/$0B, gate on — the extinguisher hiss
  58C6  LDA $7935,Y / TAX     ; X = the character's ROOM id
  58CC  STA $651C,X           ; clear the room's damage-ALARM latch
  58CF  STA $5753,X           ; clear a second per-room flag
  58D2  STA $64D0             ; clear a global flag
  58D5  ; show "FIRE OUT  " ($5950)
  ```
- **This settles the "20-entry damage index space" question:** the gate is not
  in that space at all — it is simply `find_room_object`'s index landing in
  8..10.
- **Re-confirms D-044 from a second direction:** the routine **never writes
  `$653F`**, so structural damage really is permanent and the extinguisher only
  silences an alarm that will return on the next damage tick.
- **Corrected a real behaviour bug:** an **empty** extinguisher RTSes at `$58AB`
  *before* the clear — the message prints, the alarm stays raised, and no charge
  is spent. The remake's `_use_extinguisher` cleared the alarm regardless.
- **Action:** `SpecialOptionType.FIGHT_FIRE` added with the traced handler
  (`Simulation._fight_fire`); offered on the panel while an extinguisher is
  carried by, or lying in the room of, the acting crew member — the handler's
  own gate. 5 drift guards. `[?]` `$5753,X` and `$64D0` are also cleared;
  their consumers are untraced, so they are recorded rather than modelled, and
  the ROM's menu-population rule for the entry is likewise not traced.

## D-067 — The consumable-charge system re-derived independently (already correct)
- **Date:** 2026-08-01
- **Finding:** the audit item "Item consumables: laser charge, extinguisher
  fill, tracker smashing — where the counters live" was **already resolved**;
  tracing it from scratch confirmed the remake's values rather than changing
  them. The live counters are `$4B37,X`; `$4B47,X` is a pristine backup copied
  over them at init by `$65B3`-`$65B6`. `CONSUMABLE_USES` (3 / 1 / 10 for
  extinguisher / harpoon / laser) matches `$4B47[8..11] / [12] / [13..15]`.
- **The index is a weapon EFFECT CODE, not an item id.** `$4973` loads `$4BEF`
  and the dispatcher partitions it: `<6` and `>=$12` land a plain +1 wound;
  6-7 print "…TRACKER IS SMASHED" and destroy the object; 8-11 and 13-15 are
  the charge-consuming bands; 12 adds +5; and **16 adds `#$50` (80) to the
  Alien's action timer `$64EE[0]`** — which is the net entangling it, matching
  `ALIEN_NET_ENTANGLE_TICKS = 80` exactly. Aligning the charge table against
  the *item-name* records at `$7C7D` produces nonsense (ids 11-15 come out as
  the health-status words O.K./WOUNDED/COLLAPSED/DEAD/CONFIDENT), which is the
  trap to avoid here.
- **Also re-confirmed:** the Alien dies at damage >= 50 (`$4980 CMP #$32` ->
  `endgame_dispatch`), matching `ALIEN_DAMAGE_TO_KILL`; and `$4B1D`
  (`var_alien_hits`) is `INC`'d on every scoring hit.
- **Original-code quirk recorded (not replicated):** the init loop at `$65B1`
  runs `CPY #$14` (20 iterations) because it shares its counter with the
  20-entry item-location copy `$82F7`->`$82E3`. The charge table is only 16
  entries, so it copies 4 bytes past it — reading `$4B57`-`$4B5A` (string
  bytes) and writing them over `$4B47`-`$4B4A`, i.e. **over the first four
  entries of its own backup**. Harmless in practice (codes 0-3 never take a
  charge path), but it means a second init in the same load would seed codes
  0-3 with `C9 13 A0 05`. Not modelled — recorded so nobody "fixes" the remake
  into matching a bug that never manifests.
- **Action:** the audit item ticked as confirmed; no code change needed.

## D-064 — The WELCOME screen transcribed off the running disk (R-34 closed)
- **Date:** 2026-08-01
- **Finding:** R-34 had sat open with "the rainbow PETSCII border and the
  pink-bordered box around the publisher banner are still missing". Rather than
  approximate them from a screenshot, the screen was read out of the **running
  machine** — screen RAM `$0400`, colour RAM `$D800` (bank `io`, which is the
  bit that had been failing) and the VIC/sprite registers:
  - **The rainbow ring** is solid blocks (screen code `$A0`) over a 16-entry
    colour ramp, with **four different side rules**: top `c%16`, bottom
    `(c-1)%16`, and *both* columns `(r+2)%16`. The **corners settle the draw
    order**: `(0,0)`/`(24,0)` carry the left column's value, `(0,39)` the right
    column's, `(24,39)` the bottom row's — so the ROM paints **top → right →
    bottom → left** and later sides overwrite earlier ones. All 126 unique ring
    cells now reproduce exactly (drift-guarded against the raw capture).
  - **The banner box** is rows 2-4, cols 3-35, colour RED (`$02`), drawn with
    the ROM font's rounded line-draw set (`$55/$43/$49` · `$42` · `$4A/$43/$4B`).
  - **★ The "™" is a SPRITE, not a character.** The C64 ROM font has no such
    glyph, so the loader hand-draws one: sprite 0 at `($D000,$D001)` = (274,72)
    with the `$D010` MSB set, hi-res, unexpanded, `$D027` = 1 (WHITE), pointer
    `$07F8` = `$0D` → data at `$0340`. Only the **top-left 12x5 pixels** carry
    ink. In field coords (250, 22) — 2px above the row-3 text, which is exactly
    what makes it read as a superscript.
  - **Two lines were the wrong colour:** "CHOOSE ONE OF THE ABOVE" and "PLEASE
    LEAVE DISKETTE IN DRIVE" are **LIGHT BLUE** (`$0E`), not the cyan the remake
    drew.
  - **The VIC border is BLACK** on the loader screens (`border_color` 0), not
    the play screen's blue (`$D020` = 6, `[C $7013]`). All four front-end
    screens corrected.
- **Every text run is now placed at its captured row/column** instead of being
  centred by eye.
- **Action:** `_welcome_border_colour`, `_draw_welcome_border`, `_blit_tm`,
  `_draw_welcome_option` added; `_present(border=...)` takes a per-screen VIC
  border. 7 drift guards in `tests/test_fv3_frontend_capture.py`, including one
  that replays the ring against the raw capture and one that samples the
  rendered frame's corners.

## D-065 — The loader screens now use the **real C64 chargen ROM**
- **Date:** 2026-08-01
- **Finding:** D-047 established that the front-end screens use the machine's
  ROM font (they run before `set_charbase $400A` points the VIC at ALIEN's own
  charset). The remake approximated that with `SysFont("monospace")` — which is
  **~4.3px wide inside an 8px cell**. That is not a cosmetic gap: it meant a
  string drawn at a captured column was compressed to about **half its true
  width**, so the transcribed column positions from D-064 could not line up.
  It showed instantly — the row-9 rule under "FACE THE POWER OF THE UNKNOWN" is
  exactly 29 cells wide (cols 6-34, from screen RAM), and the text above it fell
  far short of its own underline.
- **Fix:** load the actual 4KB chargen ROM (`chargen-901225-01.bin`, already on
  this machine, shipped with VICE) and render each character as a true 8x8 cell,
  so a line is exactly `8 * len(text)` px wide by construction.
- **Two banks, and the loader uses both:** bank 0 (unshifted, `$01-$1A` = `A-Z`)
  for WELCOME, whose screen RAM reads `07 12 05 05 0E` for "GREEN" and renders
  in capitals; bank 1 (shifted, `$01-$1A` = `a-z`, `$41-$5A` = `A-Z`) for
  NOTICE, whose text is genuinely mixed case ("We strongly suggest you").
- **Bonus:** in both banks ASCII `$20-$3F` maps to itself, so **digits and `:`
  need no special-casing** on these screens — unlike ALIEN's own cut-out
  charset, where their positions remain `[?]` (they were assumed from label-table
  offsets once and disproven by rendering them).
- **Deliberately NOT vendored into the repo.** The ROM is Commodore's, and
  committing it would make it a *source* rather than a derived artifact, against
  the project's conventions. `romfont.load()` searches `out/chargen.bin` then the
  VICE tools directory and returns `None` if absent, so the SysFont path stays as
  a working fallback and no test hard-depends on the ROM.
- **Action:** new `src/alien_remake/render/romfont.py`; `_render_rom_text` wired
  into `_c64_or_sysfont`'s `c64_font=False` branch, so **all four** loader
  screens (LOADING / NOTICE / WELCOME / INSTRUCTIONS) improve at once. NOTICE's
  "™" is now drawn as the D-064 bitmap rather than left in the string, where it
  was forcing that one line alone into SysFont.

## D-062 — There is **no oxygen system** in the C64 game (FV-2.5 resolved by removal)
- **Date:** 2026-08-01
- **Finding:** the remake's oxygen/TOOH model was an invention end-to-end. Four
  independent lines of evidence, none of them a guess:
  1. **R-22 (live):** a monotonic-decrease scan of ALL game RAM
     (`$6000-$7FFF` + `$C000-$C3FF` + zero page) over 10 s of active play found
     **zero** steadily-decreasing cells. No counter exists.
  2. **Complete string inventory:** every decodable run in the 16,994 recovered
     data bytes of `ALIEN.prg` was dumped — 117 strings. There is **no OXYGEN,
     no AIR** (only "AIRLOCK"), **no TIME / TOOH / SUFFOCATE**. The only
     countdown strings, `"OVERRIDE OPTION EXPIRY   MINS"` and `"SHIP WILL
     DESTRUCT IN   MINS"` (`$54C5`), belong to the auto-destruct (D-060).
  3. **The status template `$7A10` decodes in full** to
     `": DAMAGE 00% IS ........,MORALE:........"` — damage and morale only.
     There is no oxygen/TOOH readout on screen anywhere.
  4. **The jiffy clock `$A0-$A2` is read zero times** in the classified
     `$2000-$C001` region, so "time-derived" is false too.
- **Root cause of the long-standing `[?]`:** DISASSEMBLY §3 and GAMEDATA §3.5
  both asserted *"`$7A1B` reads the jiffy clock for the status display."*
  **`$7A1B` is data** — it is the `'%'` byte at offset 11 *inside* the template
  in (3) above. That bogus citation is the only thing that made FV-2.5 look
  like a calibration problem needing a live capture. It never needed
  calibrating; the mechanic does not exist.
- **Consequence found while removing it:** the invented drain silently ended
  every remake run after ~7500 ticks (~16 min at the real loop rate) — a loss
  condition the original never had.
- **Second-order:** `GameMode` now has **no mechanical effect at all**; the
  oxygen budget was the only difference the remake ever modelled and
  `nostromo_ship()` ignores mode by design. What the SHORT SCENARIO really
  changes is left as an open `[?]` (FV-1.9) rather than replaced with a guess.
- **Action:** `START_OXYGEN`, `OXYGEN_PER_TICK`, `SHORT_START_OXYGEN`,
  `GameState.oxygen`, `modes.starting_oxygen()` and `sim.advance()` step 5 all
  removed; the two wrong `$7A1B` citations corrected in DISASSEMBLY/GAMEDATA.
  Two de-invention guard tests pin the removal (`test_no_oxygen_system_exists`,
  `test_no_global_time_limit`) plus one pinning SHORT's now-truthful no-op.

## D-063 — R-29 resolved: the main loop runs at **7.886 Hz**, not the IRQ's 6.67
- **Date:** 2026-08-01
- **Finding:** the world clock had always been *approximated* by the IRQ-derived
  animation rate (`JIFFY_HZ / 9` = 6.67 Hz). Measured directly, it is **7.886
  Hz** — ~5% of gameplay tempo out, and conceptually the wrong clock.
- **Method (artifact-free):** a **non-stopping** execution checkpoint on
  `main_loop ($719D)` counts passes via `hit_count`, while
  `vice_cycles_stopwatch` counts **emulated cycles** — so the result is immune
  to host latency and to WarpMode. 20 s sample: **158 passes / 19,739,184
  cycles (20.035 s) = 7.886 Hz**; shorter trials 8.30 / 7.83 / 7.95 Hz.
  ~124,900 cycles = **~6.36 PAL frames per pass** — free-running, not
  frame-locked, which is why it spreads.
- **Self-validation in the same capture:** `$64EE[0]` (the Alien's action
  timer) decremented **exactly once per counted pass**, and the reload values
  caught mid-flight were **60** and **40** — exactly `ALIEN_MOVE_TICKS`
  (D-038) and the hidden-in-duct cost from the decoded tables. The timer model
  and the loop counter independently corroborate each other.
- **Method trap worth remembering:** the first attempt looped
  `vice_run_until $719D` and reported ~240 Hz. **`vice_run_until` returns 0
  cycles on most calls** — it does not reliably advance one iteration — so the
  average was diluted by no-op calls. Verified by timing ten single calls
  (0,0,0,0,0,0,0 / 31689 / 23552 / 34902 cycles). Discarded; do not use
  `run_until` for rate work.
- **Caveat RETRACTED (D-075).** This entry warned the sample was taken with
  "`$64BB` (game_active) = 0 ... not post-opening active play". `$64BB` is
  **not** a game-active flag — it marks an Alien **attack sequence**, so
  `$64BB = 0` is ordinary play, which is exactly what was sampled. The 7.886 Hz
  figure needs no qualification. (It also explains why "reaching active play"
  never worked in earlier passes: they were waiting for an attack.)
- **Action:** `MAIN_LOOP_HZ = 7.886` added `[C-live]`, `TICK_HZ` re-pointed at
  it, and the IRQ rate kept under its true name `ANIM_HZ` (it does pace
  sprites/sound). `test_constants_trace_to_spec` pins all three and asserts
  `TICK_HZ != ANIM_HZ` so the conflation cannot silently return.

## D-002 — The real `.nib` has 40 tracks with a protected tail (36–40)
- **Date:** 2026-06-26
- **Finding:** `inspect` on `Alien (USA, Europe).nib` reports 40 track
  entries, version 1. Tracks 1–35 carry the standard 1541 density zones
  (1–17 → 3, 18–24 → 2, 25–30 → 1, 31–35 → 0). Beyond the standard 35, tracks
  36–40 all sit in **density zone 2**, and tracks **37–40 are flagged `NO_SYNC`**
  (the nibtools "no sync mark found" status bit). No `FF_TRACK` / `NO_CYCLE` /
  `MATCH` flags are present anywhere. This is consistent with copy protection
  living on the over-format tail rather than on the DOS area.
- **Action:** filed as evidence for **the protection analysis — Copy-protection scheme analysis**
  (`docs/protection.md`); no extra task added now. The flag-bit interpretation
  (`BM_*` constants in `nib.py`) is the shared source of truth the protection analysis will build on.

## D-088 — R-21 was wrong: the game has five sound effects, open-coded as direct SID stores
- **Date:** 2026-08-02
- **Prompted by:** a player recollection — "when there is a movement or a grille
  is removed, there is a sound effect; there is also an alert sound when the
  Alien is attacking; the motion sensor makes a ping; when the airlock is opened
  or blown there is a sound effect."
- **Finding:** R-21 concluded the in-game SFX were **blocked** because `$03E8`
  is written with a sound id at four sites and never read in the classified
  `$2000-$C001` region, so the *dispatcher* must live in the loader's low RAM.
  That reasoning was sound but the **conclusion was too broad**: the game has no
  dispatcher because it does not use one. The effects are runs of **direct SID
  stores open-coded at their call sites**, and four of the five the player
  described are fully decoded:
  * **`sfx_blip_a ($4E42)`** — voice 2, noise, freq `$0100` (deep rumble): AD
    `$C0`, gate `$80` -> `$81`.
  * **`sfx_blip_b ($4E5C)`** — identical but freq `$5000` (bright hiss).
  * **The selector is the grille flag.** `reset_attack_state ($8C80)` does
    `LDA $651B / BEQ $8C98` — burst-through-a-grille plays **blip_a**, ordinary
    movement plays **blip_b**. This is exactly the player's "movement / grille"
    pair, and the *reason* they are two different sounds.
  * **`blowlock_sfx ($5904)`** — the airlock, voice 2 noise at freq `$9600` with
    the envelope inverted (attack 0, decay `$D`): a crack that bleeds away.
    Called from `$586D`, on the blow-lock path itself.
  * **The attack alert is `begin_active_play ($4F90)`** — it gates voices 1 and
    2 on together (triangle, sustain 15) and leaves **voice 3 ungated** on
    sawtooth at freq `$0020` purely as an LFO. `irq_alt_handler ($4E76)` then
    reads `$D41B` every IRQ and copies `osc3>>1` into `$D401` and `osc3>>1+$40`
    into `$D408` — a two-tone siren sweeping at **1.879 Hz** (0.532 s per
    sweep), the two voices a fixed `$40` apart.
  * **The resting state is load-bearing.** These routines write *partial* voice
    state, so what they sound like depends on `$D40D`. Normal play establishes
    it in `pause_clear_active ($501E)`, which zeroes voice 2's SR — which is
    what makes the blips one-shots rather than drones. Any faithful render must
    apply `$501E` first.
- **Still `[?]`:** the **motion-sensor ping**. `check_tracker ($595A)` prints
  the "<NAME> ... MOVEMENT" readout when `$6509` is flagged and makes **no SID
  write**; neither does `$7352`, which sets `$6509`. `sfx_blip_b` is a candidate
  (it fires on movement and is not selection-gated) but nothing decoded ties it
  to the tracker, so it is **not** claimed as one.
- **Action:** R-21 corrected from "blocked" to "resolved except the tracker
  ping"; implemented as `alien_remake.audio.sfx`, rendered through the existing
  `SidSynth` so no waveform is designed. Tracker ping filed as a live-capture
  task.

## D-089 — Jones's running animation, and why it only sometimes plays
- **Date:** 2026-08-02
- **Prompted by:** "the Jones animation only plays when a crew member is
  selected and Jones is in the same room."
- **Finding:** **Confirmed exactly, and the gate is `guard_6580 ($88CC)`.**
  * **The animation.** Sprite 3 is a five-frame running quadruped: `$4F7A`
    does `INC $64C0 / CMP #$C9 / BNE / LDA #$C4` — pointers `$C4`->`$C8`
    wrapping back to `$C4` — then `STA $07FB` (sprite 3's pointer). Rendering
    slots `$C4-$C8` out of `out/charset.bin` shows an unmistakable **cat with a
    long tail**, legs cycling; `$C9` (excluded by the `CMP #$C9` wrap) is a
    different shape entirely, so the five-frame run is deliberate.
  * **He runs across the screen.** The same routine does `ADC #$04 / STA $D006`
    — sprite 3's X advances 4 px per tick — and `CMP #$F0 / BCC` stops him at
    the right edge, where `$4F6E` clears `$64BA` and blanks `$D007`.
    `maybe_clear_64ba ($4FF1)` rearms him at X=0, Y=`$92`, frame `$C4`.
  * **The gate.** `guard_6580 ($88CC)` reaches the arming call only through
    four consecutive tests: `$88F9 CMP $64F7` (Jones's room `$657D` equals the
    displayed room), `$8901 LDY $64FB / BEQ` (**a character is selected**),
    `$8903 CPY #$08 / BCS` (the selection is a crew member, slot < 8), and
    `$8907 LDA $6501,Y / BNE` (**that crew member is on the surface, not in a
    duct**). Only then does `$8919 JSR maybe_clear_64ba` start the run.
- **Note:** `begin_active_play ($4FA2)` *also* calls `set_flag_64ba`, so the
  same sprite runs during an attack — the two consumers share one flag.
- **Action:** filed for implementation with the SFX work; the fourth condition
  (selected crew member must not be in a duct) is new to the remake.

## D-090 — The attack animation is a five-sprite composite, and it is selection-gated
- **Date:** 2026-08-02
- **Prompted by:** "the Alien attacking alert only sounds and the animation only
  appears when you have selected the crew member in that room."
- **Finding:** **Confirmed on both halves.**
  * **Selection gate.** `$8CE1 CPY $64FB / BNE $8D26` — the attack sequence
    reaches `$8D1D JSR begin_active_play` only when the victim slot equals the
    selected slot `$64FB`. Since `begin_active_play` is *both* the alert sound
    and the animation trigger, one test gates both, which is why the player
    remembers them arriving together.
  * **The animation.** `update_1 ($4EE8)` runs only while `$64BB` is set, counts
    `$64BF` down 11->0 and indexes `tbl_alien_anim ($4EDC)` =
    `00 01 01 02 02 03 03 02 02 01 01 00` — a **12-step ping-pong over 4
    frames**. The frame value + `$A0` is written to five places (`$4D04`,
    `$4D05`, `$07FE`, `$07FF`, `$4D06`), each +4 from the last, so the Alien is
    a **five-sprite composite** at slots `$A0+f`, `$A4+f`, `$A8+f`, `$AC+f`,
    `$B0+f`. `begin_active_play` sets `$D015 = $F0` (sprites 4-7 on) for it and
    `stop_active_play ($5021)` restores `$0F`.
- **Correction to the earlier record:** `$64BB` was once labelled "game active";
  it is the **attack-sequence** flag, and it is also what mutes `sfx_blip_a/b`
  (`$4E42`/`$4E5C` both start `LDA $64BB / BNE <rts>`) — the movement blips are
  suppressed for the duration of an attack so the siren is heard alone.
- **Action:** filed for implementation.

## D-091 — The duct system has its own map, drawn from one of three templates
- **Date:** 2026-08-02
- **Prompted by:** "what map shows when a crew member goes into the duct system?
  I remember it was a different map with a different layout."
- **Finding:** **Confirmed — it is not a deck plan.** `select_menu_template
  ($817D)` reads a per-room byte from the table at `$7569` and dispatches to one
  of **three** screen templates at `$A956`, `$A9C4`, `$AA6E`, and it is called
  **only from the in-duct path**. These are distinct from the three *deck*
  templates (`$A000`/`$A21C`/`$A438`, D-022): the duct template a room selects
  agrees with that room's deck for only **12 of 34** rooms, so the duct map is
  its own partition of the ship, not the deck map re-shown.
- **Related, already correct:** `$6667` does `LDA $6501,Y / STA $D029` — a
  character's portrait sprite colour is taken directly from their in-duct flag,
  so crew inside the ducts are drawn in the inverse colour. The remake already
  models this (`_CHAR_PORTRAIT_ROOM_COLOUR` = BLACK, `_CHAR_PORTRAIT_DUCT_COLOUR`
  = WHITE); the player's "portraits go negative white on black" is that.
- **Action:** the duct map is a **wholly missing screen** in the remake; filed
  as its own task (needs the three templates decoded out of `$A956`/`$A9C4`/
  `$AA6E` the way D-022's deck templates were).

## D-092 — The duct map decoded: three sheets, a pipe-follower, and room 18 as the hub
- **Date:** 2026-08-02
- **Finding:** R-41 is closed. D-091 identified the three templates; this
  decodes them and everything around them, with **no live capture** — the
  decode stands instead on four independent tables agreeing with each other.
  * **The unpacker.** `render_message ($7F0D)` is misnamed: it paints a whole
    30x18 map (`$7F33 CPY #$1E`, `$7F43 CPX #$12`) from `($FD),Y` with a
    40-byte stride. The encoding is a simple RLE: `0` ends the template, a byte
    `>= $82` is one literal screen code, and `1..$81` is a run of that many
    **blank** cells (written explicitly as `$00` at `$7F4B`, not skipped).
  * **Only ten glyphs.** `$C0`-`$C5` are pipe and corner pieces (179 of the 241
    painted cells), `$C7`/`$E6`/`$E7`/`$E8` are terminators, and **`$E6` is a
    dedicated room-node glyph**.
  * **Cross-check A.** All 34 room positions from `$80B1`/`$80D3` land on an
    `$E6`. Not one is blank or on a pipe.
  * **Cross-check B.** Each sheet carries exactly as many `$E6` nodes as
    `$7569` assigns it rooms: **9 / 16 / 9**.
  * **Most of the map is invisible.** `clear_map_colors ($7EE5)` blacks the
    whole colour area first; `mark_exits ($7F78)` then paints **only** your own
    node (white, `$7F7D`) and the runs leading away from it (light blue,
    `$7F85`). Everything else is black on black. That is why the duct view
    feels sparse and disorienting next to the deck plan — **you see the run you
    are standing on, not the network.**
  * **The tracer is a pipe follower, not a ray.** `color_if_char ($7FFE)` walks
    around corners: at each cell it tries up, right, down, left in order,
    skipping the one that would double back (`$800C` skips up when `$6500` = 4,
    `$802C` skips right when 8, `$804C` skips down when 1; left has no test).
    `$8005 CMP #$C7 / BCC` continues **below** `$C7` and stops at or above it —
    so light travels along the ducting and halts at the next room.
  * **`set_color_at_ptr ($7FC0)` is self-modifying:** `STA $7FC9` patches the
    operand of the `LDA #$0E` at `$7FC8`, which is how one routine paints in
    two colours.
- **★ Cross-check C — the decisive one.** The map geometry and the compass duct
  tables (D-083) are stored in completely different places, yet the runs
  `mark_exits` lights up terminate at **72 of the 76** tabled duct edges, with
  **zero** lit runs reaching a room the tables do not connect. The four
  exceptions are two symmetric pairs — **7 (COMPUTER, sheet 0) <-> 18 (OTHER
  LIST, sheet 1) <-> 25 (LABORATORY, sheet 2)** — i.e. exactly the edges that
  leave the sheet, which no single screen can draw.
- **Consequence:** **room 18 is the hub joining all three duct sheets**, the
  only room with links into every one. The sheets are a partition of the ship
  that is *not* the deck partition (they agree for 12 of 34 rooms).
- **Action:** decoded by `alientools.gamedata.decode_duct_map` and snapshotted
  (`DUCT_MAP_TEMPLATES` / `DUCT_MAP_ROOM_TEMPLATE` / `DUCT_MAP_ROOM_CELL`);
  colour logic in `alien_remake.core.ductmap`; drawn by
  `PygameRenderer._draw_duct_map` whenever the selected character is in a duct.
  All three cross-checks are pinned as tests.

## D-093 — The game documents its own sound effects, and that closes the tracker ping
- **Date:** 2026-08-02
- **Prompted by:** the player — "the ping happens when the motion tracker posts
  the message of a crew member *has a reading*" — after D-088 had to leave the
  ping `[?]`.
- **★ The find: `$4390` is a self-documenting sound legend.** Answering **Y** to
  "DO YOU WANT AN INTRODUCTION" (`$443C`, prompt at `$4405`) shows a **DECK PLAN
  KEY** page that prints a fixed stem `$44C1` **"THIS IS THE SOUND OF"** at row
  13 col 0 and then cycles four 42-byte captions at col 21, playing the matching
  sound after each::

      $44D6  "THE HEARTBEAT OF THE CURRENT CHARACTER"  -> fear_alert  ($436C)
      $4500  "A GRILLE BEING REMOVED"                  -> sfx_blip_a  ($439F)
      $4554  "SOMETHING MOVING BETWEEN LOCATIONS"      -> sfx_blip_b  ($43B8)
      $452A  "THE TRACKER ALARM"                       -> $64B6 = $21 ($43CD)

  This **independently confirms D-088's grille/movement split** (decoded there
  from `reset_attack_state`'s `$651B` branch) and **names the missing ping**.
- **The tracker alarm is a pulse train, not an event sound.** `$64B6` holds
  voice 3's control byte; the IRQ at `$4DD7` counts `$4D03` down and on each
  wrap writes `$D412 = $10` then `$D412 = $64B6`, re-gating the voice.
  `$65CB` loads `$4D03 = $12`, so it **pings every 18 jiffies (0.30 s)**. Voice
  3's tone comes from `init_sid_and_clear ($4DF0)`: freq hi `$32` (~752 Hz), AD
  `$08` (attack 0, 240 ms decay), SR never written -> decays to silence.
- **★ And the player's association is literally one basic block.**
  `select_char_turn ($8DE7)` does `LDA $6562 / BEQ $8DF6` (only when no attack
  sequence is running), then `$8DF6 LDA #$21 / STA $64B6` **arms the alarm**,
  and then with **no branch in between** writes the character's name from
  `$A65E` (`$8E0C`) followed by `$8D58` **" HAS A READING"** (`$8E1A`) to the
  status line. The ping *is* the readout's sound. Silenced by
  `reset_attack_state ($8C82)`.
- **Not selection-gated**, exactly as reported: the only guard is `$8DF0`'s
  `$6562` test. That is what makes it usable as a warning, unlike the attack
  siren (`$8CE1`, D-090).
- **The heartbeat's audio half is built too.** Its divider ladder was decoded
  long ago (D-061: `$4E1D/$4E2F/$4E38/$4E3D` -> 40/30/23/15 by composure) but
  only ever drove the on-screen marker pulse. Same IRQ mechanism on voice 1
  (`$4D37`), control `$11` from `$4E22`, tone from `$4DF2`/`$4DFA` (~120 Hz, a
  low thump). **The heart races as the character loses their nerve** — now
  audible, not just visible.
- **A fifth undemonstrated effect surfaced on the way:** `$58AF` — voice 2
  noise, freq `$2800`, AD `$0B` — is the **extinguisher discharge**, inside the
  FIGHT FIRE handler that decrements `$4B37,X` and prints "FIRE OUT" (`$5950`),
  with "EXTINGUISHER IS EMPTY" (`$4B5A`) on the exhausted path.
- **Action:** `tracker_alarm` and `heartbeat` added to `alien_remake.audio.sfx`
  via a shared `render_pulse`; the tracker cue is raised by `sim._use_tracker`.
  The captions are checked against the PRG in tests, since they are the naming
  evidence. R-21b closed.

## D-094 — The DECK PLAN KEY also defines three map glyphs (and refines D-092)
- **Date:** 2026-08-02
- **Finding:** the same legend page carries a **symbol key**, and the symbol
  columns are single screen codes sitting in the caption strings::

      $4471 col 19 = $E6  ->  "GRILLE"
      $44A0 col 19 = $D1  ->  "LADDER DOWN"
      $4492 col  0 = $D3  ->  "LADDER UP"
      $4463 col 13 = $1C  ->  ":"   (confirms the existing `:` mapping)

  Rendered from `out/charset.bin`, `$E6` is a **cross-hatch mesh** (a vent
  grating), `$D1` a hollow-centred box (a shaft seen from above) and `$D3` a
  diagonal ladder — so the glyph shapes corroborate the labels.
- **Refines D-092.** That entry called `$E6` "a dedicated room-node glyph" on
  the duct map. The legend is more specific: **it is the GRILLE symbol.** The
  duct map is therefore a diagram of the **grille network** — which is exactly
  right, since a grille is how a character enters or leaves the ducting, and it
  explains why every duct-map node is one.
- **One honest tension, left open rather than resolved:** `$8676` says
  **CORRIDOR 6 (room 13) has no grille**, yet room 13 still has an `$E6` node
  on duct sheet 0. Either the duct map draws a node for every room regardless,
  or the grille table and the map disagree. `[?]` — filed, not papered over.
- **Action:** recorded; the duct-map renderer is unaffected (it draws whatever
  screen code the template holds).

## D-095 — Sweep for other self-documenting content: what exists and what does not
- **Date:** 2026-08-02
- **Why:** D-093 showed that the game's own legend text is the single
  highest-yield evidence source in the binary, so the whole PRG was swept for
  more of it (226 text runs of 12+ screen codes decoded and triaged).
- **The introduction is bounded.** `$4405` prints "DO YOU WANT AN INTRODUCTION"
  / "PRESS Y OR N"; **Y** (`$19`) falls into `$4327` — the DECK PLAN KEY page
  with its symbol key and four sound demos — and **N** (`$27`) jumps straight
  to the cleanup at `$43D6`. **That one page is the entire guided sequence**;
  there is no second demo screen, so this evidence source is now exhausted.
- **Other labelled blocks found, and their status:**
  * `$4108` "ALIEN WOUNDS" / "ALIEN GONE TO" / "ALIEN GONE THROUGH GRILLE" —
    Alien event messages.
  * `$5484` "WARNING: STRUCTURAL DAMAGE TO" + "PARTIAL SYSTEMS CONTROL LOSS" /
    "COMPUTER MALFUNCTION" / "CRYOG..." — the malfunction ladder (modelled).
  * `$57D4` the Special Options menu; `$5751` "SCUTTLE NOSTROMO" / "BLOWLOCK".
  * `$8676` tail: "GRILLE" / "GRILLE IN PLACE" — grille state labels.
  * `$8BC3` "ALIEN ATTACKING" / "GRILLE BURSTS OPEN".
  * `$8830` "SEES JONES IS HERE" / "GET JONES" / "JONES:NET" / "JONES:BOX".
  * `$4B23` "S TRACKER IS SMASHED", `$4B58` "S EXTINGUISHER IS EMPTY",
    `$4B95` "S LASER IS EXAUSTED" (sic) — the item-exhaustion messages, keyed
    off the `$4B37` charge table.
  * `$6314` the four ending strings; `$5E4B` the title quote "WE LIVE AS WE
    DREAM : ALONE"; `$5F59` the selection screen, carrying the credit
    **"PAUL CLANSEY (C)1984 CONCEPT SOFTWARE"**.
- **Action:** no further hidden mechanic was implied by the sweep — the
  remaining blocks are messages for systems already modelled. Recorded so the
  next pass does not re-run the sweep.

## D-096 — The attacking Alien is a six-sprite composite built by a raster multiplexer
- **Date:** 2026-08-02
- **Finding:** R-40's remaining half. D-090 decoded the animation *table* but
  left the on-screen placement untraced, because `update_1 ($4EE8)` writes its
  pointers to `$4D04`/`$4D05`/`$4D06` — which are not variables but **operands
  inside the IRQ code**. Following them there gives the whole picture:
  * **`sub_4e87 ($4E87)`, run at play-screen setup (`$7046`), fixes the frame.**
    `$D017 = $F0` and `$D01D = $F0` expand sprites 4-7 in **both** axes, so each
    covers 48x42 px. `$D008`/`$D00C` put the left column at X=`$5A`,
    `$D00A`/`$D00E` the right at X=`$8A`; `$D00D`/`$D00F` put sprites 6/7 at
    Y=`$61`; `$D010 = 0` (no X MSB); `$D02B`-`$D02E` colour all four **green**
    (`$05`).
  * **`irq_raster_split ($4D58)` is a multiplexer.** Toggling on `$64B9` it
    shows sprites 4 and 5 **twice per frame** — at Y=`$8B` with pointers from
    `$4D06`/`$4D07` (`$4D72`), then at Y=`$37` with `$4D04`/`$4D05` (`$4D9E`),
    reprogramming `$D012` each time. **Six images out of four sprites.**
  * **The layout is therefore a 2x3 grid**::

        Y=$37   $A0+f   $A4+f        (sprites 4/5, band B)
        Y=$61   $A8+f   $AC+f        (sprites 6/7, direct $07FE/$07FF)
        Y=$8B   $B0+f   $B4          (sprites 4/5, band A; $B4 is STATIC)

    `begin_active_play ($4F95)` writes the static `$B4`, so **five of the six
    cells animate and one does not** — which is why D-090 counted five.
- **★ The spacing is the proof.** An expanded sprite is 48x42; the columns are
  `$8A - $5A` = **48** apart and the rows `$61 - $37` = `$8B - $61` = **42**
  apart. The six cells abut exactly, with no gap and no overlap — and rendering
  them out of `out/charset.bin` produces one coherent creature: elongated head
  with the inner jaw, ribbed body, segmented tail curling to the lower left.
  A 96x126 px Alien filling the left of the play screen.
- **Start and stop are both cited, so no duration was invented.** The composite
  runs from the **audible** attack alert (`$8CE1`'s selection test gates siren
  and animation together, D-090) until the next movement blip — because
  `reset_attack_state ($8C80)` is the one routine that both plays that blip and
  clears the attack flags `$6562`/`$64B6`.
- **Action:** implemented as `PygameRenderer._draw_attack_animation`, drawn
  after the map since the VIC composites sprites over the character screen.
  Geometry, slot chain, ping-pong table and the abutment are all pinned as
  tests against the PRG bytes. R-40 closed.

## D-097 — CORRIDOR 6 resolved: a duct you can travel through but never enter
- **Date:** 2026-08-02
- **Finding:** R-43's apparent contradiction is not one, and it resolves
  statically. `$8676` marks **CORRIDOR 6 (room 13) as the ship's only
  grille-less room**, yet it carries an `$E6` node on duct sheet 0 — and the
  DECK PLAN KEY defines `$E6` as GRILLE (D-094). The compass tables settle it:
  CORRIDOR 6 has **four duct neighbours** (COMPUTER, LIFE SUPPT, RECRTNAREA,
  STORES 1), **all mutual**. So the ducting genuinely *runs through* it — it is
  a junction, not a dead end. What it lacks is the **grille**, which is the
  *entrance*.
- **So CORRIDOR 6 is a through-route you can traverse but can never enter or
  leave** — the only such room aboard. It needs a node on the duct map because
  you have to see it to route through it; the grille glyph drawn there is the
  one place the map overstates what is really present.
- **Already modelled correctly, by accident of getting the rule right.** P-5's
  `_duct_step_target` gates *entry* on the room's grille being open while
  leaving movement *inside* the ducting free along the compass graph — which is
  exactly the distinction CORRIDOR 6 depends on. Pinned by a test so a future
  "simplification" of that rule cannot silently break it.
- **Action:** R-43 closed without a live capture. `[?]` retired.

## D-098 — Why the game ended by itself: a parked Alien and a breach gate 5 points early
- **Date:** 2026-08-02
- **Prompted by:** "why does the game end on its own so quickly? It often ends
  before the Alien has appeared."
- **Reproduced immediately:** unattended runs ended LOST in **93-1110 seconds**
  with 2-4 crew still alive, every time by **hull breach**. Two independent
  bugs, both now fixed.
- **★ Bug 1 — the breach threshold was the WARNING threshold.** `damage_room_b
  ($5587)` and `$5658` describe a **three-band ladder**, not one gate::

      damage < 4        nothing at all        `$558F CMP #$04 / BCC RTS`
      4 <= d < 15       alarm stage 1         `$5596 BCC $559E`
      15 <= d < 20      alarm stage 2         `$565F-$5669`
      d == 20           HULL BREACH, loss     `$5658 CMP #$14 / BNE`

  The remake used a single gate at **15** — the stage-2 boundary. D-073 had
  already *read* both gates correctly and then deliberately kept one, calling it
  a simplification; it is the difference between "severe damage warning" and
  "the ship is destroyed". Note the breach test is an **equality** (`CMP #$14`),
  because the ROM's counter only ever moves by `INC` or a fixed weapon add.
  `HULL_BREACH_THRESHOLD` is now 20 and `DAMAGE_STAGE_SEVERE_FROM` is 15, which
  is what the `CMP #$0F` really meant.
- **★ Bug 2 — the Alien parked, because the route tables were taken literally.**
  `alien_choose_move ($89C4)` is a **re-roll loop**: every rejected outcome does
  `JMP $89C4` and rolls again —
  * `$89CE BNE $89C4` — no duct entry while a move is already in flight;
  * `$89D5 BEQ $89C4` — no duct entry from room `$22` (SHUTTLEBAY);
  * **`$89FF CPX $64E6` / `$8A04 JMP $89C4` — reject a destination equal to the
    Alien's own room.**

  That last one is decisive. The route tables encode "no exit this way" as a
  **self-reference** — the same convention as the compass tables (D-083), and
  the reason `gamedata.surface_exits` *terminates* on one. **Three of AIRLOCK
  2's five route entries are self-references.** The remake accepted them, so the
  Alien "moved" to the room it was already in and stopped: in one measured game
  it sat in AIRLOCK 2 for **510 of 734 ticks (70%)**, spent only 13.9% of its
  time in the ducts, and ground that one room to the breach value while the
  player never saw it. An old test, `test_alien_blocked_direction_idles_in_place`,
  asserted exactly this ("the original *moves* the Alien to its own room — an
  idle that still consumes the full move duration") and was **pinning the bug**;
  rewritten.
- **Result:** unattended game length went from **1.5-18 min (mean 7.5, with runs
  ending in 93 s)** to **7-24 min (mean 16.5)**, and the Alien now roams the
  ship instead of squatting. Guarded by a regression test that fails if the
  Alien spends more than half its time in any single room.
- **Also decoded on the way:** `$64B4` is the Alien's "move in flight" flag and
  `$6563` its "arrived at destination" flag; passive corrosion (`guard_6562
  $8EBD`, `INC $653F,X`) is gated on **four** conditions — not in transit
  (`$89AF`), no attack sequence (`$8EBD`), not in a duct (`$8EC3`), and arrived
  (`$8EC8`). The remake only had the duct one; the others now matter much less
  because the Alien no longer sits still, but they are recorded for a future
  pass.

## D-099 — The victim and android are drawn from FIXED POOLS, not the whole crew
- **Date:** 2026-08-02
- **Prompted by:** "I think the android was a random member of the crew. Please
  review everything you can about that in the code."
- **Finding:** it is random, but **not from all seven**. `$506E` and `$507E`
  index two 16-entry lookup tables with `rng ($888F)`::

      $50EC  victim pool   1 2 5 1 2 5 1 2 5 1 2 5 1 2 5 2
                           -> DALLAS x6, KANE x5, LAMBERT x5   (3 names)
      $50FC  android pool  1 2 4 6 1 2 4 6 1 2 4 6 1 2 4 6
                           -> DALLAS, KANE, ASH, PARKER x4 each (4 names, uniform)
      $510C  victim room   6 6 27 6 6 27 ...  (COMMDCENTR / LIFE SUPPT)

  `$5081 CMP $64C2 / $5084 BEQ $506A` re-rolls on a collision — and note the
  branch target is the **victim** roll, so a clash re-rolls *both*.
- **The remake was already exactly right** (`ANDROID_CANDIDATES` = dallas/kane/
  ash/parker, `OPENING_VICTIM_CANDIDATES` = dallas/kane/lambert). **No change
  made** — verified and pinned to the PRG bytes instead, which is the correct
  outcome when a hunch and the code disagree.
- **Related, checked at the same time:** the FULL roster is correct — seven
  crew, exactly one dead (the victim), **all seven selectable** at the CONTROL
  panel root, and select -> QUIT -> select-another works. The reported "crew
  isn't all selectable at the start" could **not** be reproduced in FULL.
  * In **SHORT**, the ROM's own table (`$6093` -> `$7D46,Y`) gives **ASH health
    0**, and `health_band ($7D94)` computes `3 - health` below 3, so index 3 =
    **"DEAD"**. So the original SHORT SCENARIO really does start with the
    android showing as dead, plus Dallas and Brett on 1 health and two crew
    already inside the ducts (`$605A`/`$605F`). That is the scenario, not a bug.
  * The one **[?]** left: whether the remake is right to derive `alive` from
    `health > 0` at all. The ROM's death marker in this table is the **location
    sentinel `$FE`** (`CHAR_GONE`), which only KANE carries. Filed as P2-20.

## D-100 — How the Alien really moves: two distributions, two clocks, one pass
- **Date:** 2026-08-02
- **Prompted by:** "How does the alien move in the original game? The remake
  should do the same movement pattern or style."
- **★ The headline: there are TWO surface-movement routines, and the ROM picks
  between them on the GRILLE.** `alien_ai_dispatch` reads the Alien's room in
  the grille table and branches::

      $89BF  LDA $8676,Y
      $89C2  BEQ alien_choose_move      ; grille GONE  -> $8A36
             (fall through)             ; grille THERE -> $89C4

  `$8676,Y` is nonzero while the grille is still in place, and is zeroed once
  removed or burst (D-087). The two routines disagree about everything:

  ===================  ==================  ==================
  roll 0-15            grille **open**     grille **shut**
  ===================  ==================  ==================
  enters the duct      12-15 -> **25%**    15 only -> **6.25%**
  route-table bands    3/5/7/9             3/6/9/12
  surface spread       3/2/2/2/3 of 12     3/3/3/3/3 of 15
  ===================  ==================  ==================

  So **the Alien is four times more likely to take a duct whose grille is
  already open** — opening one genuinely invites it in — and when it has to
  stay on the surface it ranges more evenly across all five route tables.
- **It is a re-roll loop, not a single roll** (D-098 found this half): every
  rejected outcome does `JMP $89C4` — in transit (`$89CE`), from SHUTTLEBAY
  (`$89D5`), or a destination equal to its own room (`$8A04`). A side effect
  worth knowing: because the re-roll restarts *before* the duct test, a room
  with blocked route entries has a **higher effective duct chance** than the
  nominal 25%/6.25% (measured 37%/10.6% from COMMDCENTR).
- **Inside the ducts** (`alien_ai $8A74`) it walks the **compass** tables:
  roll 0-2 N (`$80F5`), 3-5 E (`$8117`), 6-8 S (`$8139`), 9-12 W (`$815B`),
  **13-15 surfaces** (`$8A92`, destination written *without* bit 7). While the
  room's own grille is still shut, a roll of 15 is re-rolled (`$8A7A`-`$8A83`),
  so **a shut ship traps the Alien in the ducting for longer once it gets in** —
  the opposite of the entry effect, and measurably so.
- **Three different clocks**, all previously collapsed onto one:
  * surface move — `$8A4A LDA #$3C` = **60** ticks
  * duct-to-duct crawl — `$8AAB LDA $6581` = **70** ticks (slower than walking)
  * entering a duct / emerging / bursting — `$89E0`/`$8A98`/`$8B8C` `#$28` = **40**
  D-038 had corrected `ALIEN_MOVE_TICKS` 70 -> 60 and parked `$6581` as "a
  distinct, currently-unmodeled mechanic"; that mechanic is now modelled, so the
  70 returns for the case it actually belongs to.
- **★ And one action is ONE pass.** `alien_tick ($8ACE)` is `DEC $64EE / BEQ`
  followed by a single visit that arrives, corrodes and dispatches the next
  move. `advance_alien` had split that across two ticks — land the move on one,
  begin the next action on the other — and **both branches fell through to the
  corrosion and encounter code**, so the Alien damaged its room and wounded
  co-located crew **twice per action cycle**. Restructured into one pass.
- **Net effect on play** (unattended, 10 seeds), against the same measurement
  before D-098::

      before D-098   93 s - 18 min,  Alien parked in 1 room,  <=6 rooms seen
      after  D-098   7 - 24 min      (mean 16.5)
      after  D-100   10.6 - 58.9 min (mean 28.1), 9-30 rooms, 23-69% in ducts

  The Alien now roams the whole ship, hides in the ducting for long stretches
  and reappears elsewhere — which is the "movement pattern or style" the player
  was asking about, and it is no longer possible for a game to end before the
  creature has shown itself.
- **Action:** implemented in `core/alien.py` + `constants.py`
  (`ALIEN_DUCT_THRESHOLD_GRILLE_OPEN/SHUT`, `ROUTE_BAND_BOUNDS_GRILLE_OPEN/SHUT`,
  `ALIEN_DUCT_TRAVEL_TICKS`). Two tests that asserted the old single
  distribution were rewritten. A `RollRandom` helper was added to the alien
  tests: `FixedRandom` pins `random()`, which does **not** map linearly onto
  `randrange` (CPython scales by 2**53 and takes a modulus), so `0.9` was
  silently producing roll 14 where the test comment claimed otherwise.

## D-101 — The grille is a DESTINATION, and four more mechanics decoded with it
- **Date:** 2026-08-02
- **Prompted by:** a play report — crew teleporting into the ducts, the in-duct
  menu showing room names, GET ITEM's capacity and drop order, and crew found in
  the ducts after an attack.
- **★ P2-2 — `draw_grille_option ($86F0)` writes to TWO different screen slots,
  and which one decides the whole mechanic:**
  * grille **in place** -> `"REMVGRILLE"` (`$86E6`) into `$064E` = **row 14,
    the SPECIAL column**, status line "GRILLE IN PLACE" (`$86C8`);
  * grille **removed** -> `"GRILLE"` (`$86BE`) into `$046E` = **row 2, the
    MOVE TO column**, SPECIAL blanked (`$8733`), status "GRILLE REMOVED"
    (`$86D7`);
  * `$86F3 CPY #$22 / BEQ` — SHUTTLEBAY never offers either.

  So an opened grille becomes a **destination the player chooses**. The remake
  had no such entry and instead converted any ordinary MOVE TO into a duct step
  whenever the target happened to be a duct neighbour — which is exactly the
  reported bug: remove a grille, order a normal move, end up in the vents.
  Entering is now `OrderType.USE_GRILLE` and nothing else.
- **P2-3 — inside the ducting the menu names DIRECTIONS, not rooms.** `$81EF`
  walks the four compass tables, skips every self-reference (`$81F2 CMP $7934 /
  BEQ`) and labels each survivor from the `$8080` word block — `$807F` NORTH,
  `$8093` EAST, `$8089` SOUTH, `$809D` WEST, each with its own arrow glyph.
  That is what makes duct travel disorienting: you are told which way you may
  go, never where it leads.
- **P2-4 — a grille can be opened from INSIDE.** `draw_grille_option` keys off
  `$64F7`, the displayed room, not the character's surface/duct state, so a
  crew member crawling the ducts can open a still-shut grille and climb out.
- **★ P2-16 — a crew member carries TWO items, and the newest comes off first.**
  `scan_room_objects ($8332)` clears exactly two carry slots to `$FF`, and
  `list_room_items` refills them by scanning the item-location array for two
  distinct holder encodings — `char + $A0` -> `$829A` (drawn at panel row 9) and
  `char + $80` -> `$829B` (row 10). Two slots, two rows. `LEAVE ITEM ($8512)`
  tries `$829B` **first** and only falls back to `$829A` when it is empty, so
  the two do not come off in pickup order; play settles the direction — pick up
  the incinerator then the tracker and the **tracker** goes down first. The
  remake modelled a single carried item.
- **★ P2-17 — the Alien carries its kill away and leaves it in the ducting.**
  Three routines: `alien_death_effects ($4292)` stows a fresh victim when the
  slot is free (`$429E LDA $64DC / BNE`); `stow_char ($599E)` parks them at the
  off-map sentinel `$BB`; and `restore_stowed_char ($59A7)` — which runs **only
  while the Alien itself is in a duct** — writes them into the ducting at the
  Alien's own position (`$59C3 STA $6501,X`, `$59C8 LDA $7935 / STA $7935,X`),
  after checking nobody already occupies it. Only one body at a time. This is
  the player's "I found a lot of crew in the ducts after the attack", and it
  reproduces: 7 deposits across 6 unattended runs.
  * **Correction:** an earlier triage guessed `$5939` was this mechanic because
    it writes location `$95`. It is not — `$5939` is **ENTER HYPERSLEEP**, and
    `$95` is that sentinel. Checking saved a wrong implementation.
- **P2-18 — only THREE rooms can catch fire.** `damage_room_b` writes the FIGHT
  FIRE special (`$55B1 LDA #$06 / STA $5753,X`) only for room indices `$11`-`$13`
  (`CPX #$11 / BCC`, `CPX #$14 / BCS`) — OTHER LIST, OTHER LIST and **ENGINE 1**,
  the engine spaces. So the option belongs to a **burning engine room**, not to
  whoever holds the extinguisher (which is how the remake gated it, from D-066's
  read of the *handler* rather than the menu). And a fire **burns**:
  `mainloop_sub_5684` runs once per 256 main-loop passes and adds another point
  of damage to any of those three rooms whose alarm is still lit.
- **P2-8 — Jones ran ~4.5x too fast.** `update_3 ($4F52)` steps the sprite and
  advances X by 4 **once per IRQ tick** (`ANIM_HZ` ~= 6.7 Hz); the renderer was
  driving it at 2 frames per step, i.e. ~15 Hz. Now scaled to the real rate.
- **Action:** all implemented and pinned; the two tests that asserted implicit
  duct entry were rewritten.

## D-102 — Border feedback, engine fires, and the action delay that punishes wounds
- **Date:** 2026-08-02
- **P2-12 — the rainbow border is `wait_keypress_flash ($8660)`.** While the
  game waits for the player to acknowledge, it runs `INC $D020` on **every**
  input poll, so the border tears through all sixteen colours as fast as the
  loop spins, then `LDA #$06 / STA $D020` restores the play screen's blue on
  the way out. Four call sites (`$74DC`, `$7631`, `$7AF8`, `$8583`). That is
  the player's "colourful rainbow noise... to let the player know a command was
  accepted."
- **P2-18 — only three rooms can catch fire, and a fire spreads.**
  `damage_room_b` writes the FIGHT FIRE special (`$55B1 LDA #$06 / STA
  $5753,X`) only for room indices `$11`-`$13` (`CPX #$11 / BCC`, `CPX #$14 /
  BCS`) — OTHER LIST, OTHER LIST and **ENGINE 1**. So the option belongs to a
  **burning engine room**, not to whoever holds the extinguisher, which is how
  the remake had gated it from D-066's read of the *handler* rather than the
  menu. And `mainloop_sub_5684` (`INC $64CE / BNE rts` — once per 256 passes)
  adds another point of damage to any of those three rooms whose alarm is still
  lit, so an unfought fire eats its way toward the breach on its own.
- **★ P2-7 — `compute_action_delay ($4042)`: being wounded makes you SLOW.**
  Run before ATTACK (`$48FC`), USE (`$7B6E`) and GET/LEAVE ITEM (`$8460`), it
  **accumulates** onto the character's countdown (`$405D LDA $64EE,Y` ...
  `$4064 STA $64EE,Y`) from two tables::

      $4032, by crew slot 1-7 :  7  5  0  7  3 10  5
      $402B, by health   0-6  :  0  0 48 16  0  0  0

  The health term dominates. At **2 health an action costs +48 ticks** — about
  **7 seconds** at the measured 7.886 Hz main loop, against 0.9 s for a healthy
  crew member — and +16 at 3 health, nothing from 4 up. So a wounded crew
  member is not merely weaker in a fight: they become visibly, punishingly slow
  to do anything, which is much of why losing people early snowballs. The
  remake resolved these orders instantly.
- **P2-11 — checked and left alone.** The character marker already uses the
  ROM's own `$758D`/`$75B1` per-room tables with the documented `VIC_X - 24` /
  `VIC_Y - 50` origin conversion and sprite centring. No static error was
  found, so the residual misalignment the player reports is a pixel-level
  registration question that needs the **live side-by-side capture (R-31)** —
  nudging the offset by eye would be exactly the invention this project exists
  to remove.
- **Action:** P2-7, P2-12 and P2-18 implemented and pinned to the PRG bytes;
  P2-11 downgraded to a live-capture task with its reasoning recorded.

## D-103 — "Is anyone still in play?" is far stricter than "is anyone alive?"
- **Date:** 2026-08-02
- **P2-20 resolved, and it turned out bigger than the question asked.** The
  question was whether `alive` should be `health > 0`. It should — `health_band
  ($7D94)` computes `3 - health` below 3, so health 0 renders as **"DEAD"**,
  1 as COLLAPSED, 2-3 WOUNDED, 4+ O.K. But reading the endgame scan to answer
  it turned up a much larger gap.
- **`$5B56`-`$5B7E` is a four-part test**, and a crew member only keeps the game
  running if **all** of it passes::

      $5B5B  CMP #$02 / BCC next   health >= 2   (COLLAPSED on 1 does NOT count)
      $5B5F  CPY $64C3             ...and not a REVEALED android
      $5B64  LDA $64CC / BNE next
      $5B6C  LDA $7D55,Y / BEQ     composure > 0 (nobody BROKEN counts either)
      $5B7C  LDA $64D1,Y / BNE     ...and not in HYPERSLEEP

  If nobody qualifies, `$5B76 JMP endgame_dispatch` ends the game. The remake
  checked only `alive`. **So a ship whose survivors are all collapsed, broken
  or asleep is lost just as surely as one where everyone is dead** — which is a
  large part of why the Personality Control System has teeth at all, and it was
  simply missing.
- **A latent bug fell out of it.** `CrewMember.fear` defaults to `FEAR_MIN` — and
  since that value is **composure** (high = calm), every bare `CrewMember(...)`
  was born **BROKEN**. Real crew never are: `default_crew` seeds them from the
  ROM's `$7D5D` table (3-4) and SHORT from `$609A`. The default only ever
  surfaced in test fixtures, where it silently created crew the ROM's own scan
  would have discounted — invisible until this check started reading composure.
  Defaulted to 4, the top of the real starting range.
- **One test premise corrected, not weakened.** `test_alien_slips_through_an_
  already_open_grille` asserted that a co-located crew member takes no harm on
  the pass where the Alien ducks into the vents. Under D-100's one-pass model
  that is wrong: `alien_tick` resolves the action just *finished* — arrive,
  corrode, wound — and only then dispatches the next, so the Alien was still on
  the surface for the action that ended. The test now asserts the property that
  is actually true: **it does no further harm while it stays in there.**
- **Action:** `_counts_as_in_play` implemented against the four ROM conditions;
  P2-20 closed. Unattended game length is unchanged at 10.6-58.9 min (mean 29.9).

## D-104 — The GREEN VALLEY loading screen is a colour-RAM spiral, in BASIC
- **Date:** 2026-08-02
- **P2-13 solved, and it was not in `ALIEN.prg` at all.** The loader's first
  screen lives in **`MENU1.prg`'s BASIC**, and detokenising it gives the
  animation outright — a routine the authors labelled themselves::

      150 W=7 : REM ****SPIRAL****
      160 CM=55296 : WD=40 : VIC=53248 : T1=39 : T2=25
      200 FOR Q=11 TO 1 STEP -1 : GOSUB 220 : NEXT
      210 FOR Q=1 TO 11 : GOSUB 220 : NEXT : GOTO 290
      220 UL=CM+Q+Q*WD : UR=CM+Q*WD+(T1-Q)
          LL=CM+(T2-Q)*WD+Q : LR=CM+(T1-Q)+WD*(T2-Q)
      230 W=W+1 : IF W>15 THEN W=0
      240 FOR N=UL+1 TO UR : POKE N,W : NEXT          ; top
      250 FOR N=UR TO LR STEP WD : POKE N,W : NEXT    ; right
      260 FOR N=LR-1 TO LL STEP -1 : POKE N,W : NEXT  ; bottom
      270 FOR N=LL TO UL STEP -WD : POKE N,W : NEXT   ; left
      280 RETURN
      300 VT=13 : B$="GREEN VALLEY"   310 VT=14 : B$="PUBLISHING "

  So it paints **22 concentric rectangular rings** straight into colour RAM,
  each a flat colour, cycling 0-15 from a start of 8, sweeping ring 11 outward
  to ring 1 and back in again — then centres the publisher's name on rows 13
  and 14. Ring Q spans rows Q..25-Q and columns Q..39-Q, so rows 0/24 and
  columns 0/39 are never touched.
- **★ Not the same effect as the WELCOME ring, though they look alike.** Both
  are rainbow rectangles, which made them easy to conflate. The WELCOME ring
  (D-064) is a **per-cell gradient** captured live — its top row reads
  2,1,2,3,4,5,... — whereas **every spiral ring is one flat colour**. Verified
  by replaying the BASIC and comparing: the spiral's row 1 is uniform, the
  captured WELCOME row is not. Two screens, two effects; only the spiral
  animates.
- **Also recovered nearby:** a `****MARQUIE****` routine (lines 330-380) that
  runs a colour chase around the screen edge, and the `****CENTER ROUTINE****`
  (390+) that pads a string to centre it.
- **Action:** implemented as `spiral_colours()` + an animated
  `_draw_loading_menu`, replacing a static "LOADING MENU" caption. Pinned with
  tests including the "a spiral ring is flat, the WELCOME ring is a gradient"
  distinction so the two cannot be conflated again.

## D-105 — P2-14: the grille sound is already the lower one, and the memory was right
- **Date:** 2026-08-02
- **The player asked to check a recollection** that the grille sound is a lower
  tone, hedged with "but I might be wrong". They were right, and the remake
  already reproduces it — **no change made**.
- **Three independent confirmations:**
  1. `sfx_blip_a ($4E4C)` writes `LDA #$01 / STA $D408` -> voice 2 frequency
     `$0100`; `sfx_blip_b ($4E66)` writes `#$50` -> `$5000`. **Eighty times
     lower.**
  2. The game's own DECK PLAN KEY demo (D-093) plays `sfx_blip_a` under the
     caption `$4500` **"A GRILLE BEING REMOVED"**, so the low one is
     definitively the grille.
  3. Measuring our rendered clips: the grille blip has a zero-crossing rate of
     **~40 /s** against the movement blip's **~9327 /s**.
- **The synthesis path checks out too.** At `$0100` the oscillator runs at
  15.03 Hz and the noise LFSR — clocked from phase-accumulator bit 19, i.e.
  16x the fundamental — at **240.5 Hz**, which is the deep rumble the player
  remembers. `_Voice.step`'s `noise_phase += inc * 16.0` is exactly that 16x
  relationship, so the low-frequency case is not a modelling artefact.
- **Action:** closed as verified-correct. This is the right outcome when a
  recollection and the code agree: pin it, do not "improve" it.

## D-106 — P2-15: the intro's whole timbre hangs on one constant, settled live
- **Date:** 2026-08-02
- **Method:** `tools/vice-mcp/p215_sid_diff.py` boots the real disk (**WarpMode
  off**), drives the front end to the title where the tune plays, and samples
  `$D400`-`$D418` 240 times at 0.25 s. The point was to separate two
  possibilities behind "close but a little strange": is our *player* writing
  the wrong registers, or is our *synthesis* wrong?
- **★ It is the synthesis, and one constant decides it.** The capture settles
  four registers at 100% for the entire tune::

      $D417 = $F3   resonance **15 (max)**, routing $3 = voices **1 and 2
                    routed THROUGH the filter**
      $D418 = $9F   volume 15, **low-pass**, voice 3 muted (3OFF)
      $D415 = $00   filter cutoff, low bits
      $D416 = $00   filter cutoff, high bits  <- **never moves, all 240 samples**

  So every audible voice passes through the filter, and the cutoff register is
  **pinned at zero for the whole piece**. That means the single value "what
  frequency does FC = 0 correspond to" sets the intro's entire character.
- **Our model had it an order of magnitude too low.** The generic linear
  approximation `fc = 30 + FC*5.8` put FC=0 at **30 Hz** — a 30 Hz low-pass
  applied to both audible voices, which crushes the tune. The 6581's measured
  minimum cutoff is about **220 Hz**. Corrected to `220 + FC*5.8`, keeping the
  full-scale top around 12 kHz.
- **This also re-confirms R-20 from a second angle.** D-016's original note
  described voice 3's envelope modulating the cutoff every jiffy; R-20 measured
  that away, and this capture independently shows `$D416` flat at `$00` across
  240 samples. There is no filter sweep in the intro — the earlier "runaway
  resonance" symptom was our own doing.
- **One loose end recorded, not guessed:** `$D413` (voice 3 AD) takes **164
  distinct values** across the capture, i.e. it is rewritten almost every
  sample, while voice 3 is muted and its envelope is not driving the cutoff.
  What the player uses that for is `[?]` — filed rather than modelled.
- **Action:** filter base corrected in `audio/sid.py` with the capture cited
  inline; the captured register values are pinned as tests so a future change
  to the filter path has to reckon with the real machine's numbers.

## D-107 — P2-5 closed: the panel is faithful, but the threshold was wrong
- **Date:** 2026-08-02
- **The report** was "the crew isn't all selectable at the start", in the FULL
  scenario. Two earlier passes could not reproduce it from the headless model,
  because the headless model was not where it showed. Driving the **renderer's**
  own `MenuController` reproduced it at once: all seven names are listed and
  flagged selectable, but firing on the opening victim silently does nothing.
- **That behaviour is faithful, and it is already cited.** `guard_alien_present
  ($7720)` bounces the selection straight back to the CONTROL list for a
  character who is asleep (`$64D1,Y != 0`) or whose health is below 2
  (`$7D45,Y < 2` -> `STA $64FB` = 0). The name and status stay on the panel —
  which is *how the player learns who died* — but no order menu opens. So a
  dead crew member being listed-but-inert is the game working as designed, and
  the answer to the report is "that is the original".
- **★ But the remake's threshold was wrong.** It gated on `not crew.alive`,
  i.e. health > 0, where the ROM's test is `< 2`. So a **COLLAPSED** crew
  member on 1 health could still be given orders in the remake and cannot in
  the original. Corrected to `CREW_INCAPACITATED_BELOW`, the same constant the
  endgame scan uses (`$5B5B CMP #$02`, D-103) — the two now agree, which they
  should, since they are the same ROM comparison.
- **Action:** threshold fixed and pinned; P2-5 closed.

## D-108 — Methodology correction: SID registers are WRITE-ONLY, so do not read them
- **Date:** 2026-08-02
- **A capture I took for P2-15 was unsound and is retracted here.**
  `tools/vice-mcp/p215_sid_diff.py` sampled `$D400`-`$D418` with
  `vice_memory_read`. On a 6581 those registers are **write-only**: a read
  returns whatever is floating on the data bus, not the register.
- **The tell was in the data, and it is worth recording as a trap.** `$D413`
  came back with **164 distinct values across 240 samples** — yet
  `sid_init_voices ($957E)` writes a *fixed* `#$4F` to it. A register that the
  code only ever writes one value to cannot legitimately read back 164. That
  single inconsistency invalidates the whole capture's values.
  (It also disposes of P2-22, which had been filed as "what is the player doing
  with `$D413`?" — the answer is *nothing*; the varying reads were bus noise.)
- **The right tool exists:** `vice_sid_get_state` reports the emulated chip's
  actual registers as structured data (per-voice frequency, waveform bits,
  ADSR, plus the filter). `vice_sprite_get` does the same for sprites. Neither
  goes through a bus read.
- **What survives:** the *conclusion* of D-106 — that the intro's timbre hangs
  on the FC=0 cutoff and that 30 Hz is far too low for a 6581 — does not depend
  on the capture. It follows from the ROM's own writes (`$D415`/`$D416` are
  only ever written by the player's own init, and the filter routing sends
  voices 1+2 through it) plus the documented ~220 Hz minimum. But the claim
  "measured 100% across 240 samples" must not stand on a bus read, and is
  re-taken through `vice_sid_get_state` in `p215_p211_verify.py`.
- **Standing rule added:** never read `$D400`-`$D418` to learn SID state; use
  `vice_sid_get_state`, or set a checkpoint on the *writes*. The same caution
  applies to any write-only I/O register.

## D-109 — P2-15 re-verified through `vice_sid_get_state`: the conclusion holds
- **Date:** 2026-08-02
- **Re-taking the measurement D-108 retracted.** `p215_p211_verify.py` samples
  the emulated chip's own registers 60 times while the title tune plays
  (WarpMode off), instead of bus-reading write-only addresses. Every filter
  field is **settled at 100%**::

      filter_cutoff_low   = 0        filter_voice1 = true
      filter_cutoff_high  = 0        filter_voice2 = true
      filter_resonance    = 15       filter_voice3 = false
      lowpass  = true                voice3_off    = true
      highpass = false               volume        = 15
      bandpass = false

  and `voices` shows 40 distinct states across the sample — the tune is
  genuinely playing while the filter sits still.
- **So D-106's conclusion stands, now on sound evidence:** the intro runs
  **both audible voices through a low-pass whose cutoff register never moves
  from zero**, at maximum resonance. That makes "what frequency is FC = 0" the
  single constant deciding the intro's entire timbre — and the generic
  `30 + FC*5.8` line put it at 30 Hz, which crushes the tune. Corrected to the
  6581's measured minimum, ~220 Hz.
- **A nice confirmation of the earlier retraction:** the unsound bus-read
  capture happened to report the *same* values for these particular registers
  (they are written once and rarely disturbed, so the bus retained them) while
  being pure noise for `$D413`. That is exactly why the `$D413` inconsistency
  was worth chasing rather than shrugging at — it exposed a method that was
  right by luck for most fields and wrong for one.
- **Action:** the captured chip state is pinned as a test; `p215_sid_diff.py`
  keeps a header explaining why it is superseded, so nobody re-runs it.

## D-110 — Play-report #3: the attack sequence blanks the map, and the siren loops
- **Date:** 2026-08-02
- **Standing correction first, because it caused this whole batch.** Seven items
  closed earlier the same day came back in the next playtest. Every one had been
  verified **headlessly and against the disassembly, but never in the running
  app**. A passing `Simulation` test plus a correct ROM citation is *not*
  evidence the player sees the change. Anything reopened must now be reproduced
  through `run_app`/`PygameRenderer`, not `Simulation` alone.
- **★ P3-4 — the attack BLANKS the map, and the routine that does it was one
  call away all along.** `begin_active_seq ($8D1A)` is two instructions::

      8D1A  JSR clear_map_colors   ; $7EE5 — fill the 30x18 colour area with 0
      8D1D  JSR begin_active_play  ; $4F90 — siren + composite

  `clear_map_colors` is the same routine the duct map uses (D-092). Black ink on
  a black background makes the deck plan **vanish**, and only then is the Alien
  drawn — so the creature appears over empty space, which is exactly what the
  player described. We were painting it over a still-visible map. The renderer
  now skips `_draw_deck` while `_attacking`; a test samples the map area during
  an attack and asserts only black and the Alien's green (`$05`) survive.
- **P3-12 — the siren is a LOOP and we played it once.** `begin_active_play`
  gates voices 1+2 on and leaves them on; `irq_alt_handler ($4E76)` sweeps them
  from voice 3's oscillator every IRQ for as long as `$64BB` is set. Our clip is
  **one 0.53 s LFO period**, so playing it as a one-shot produced precisely the
  "small squeak and then nothing" reported. Now looped, and stopped by the
  movement/grille blip — because `reset_attack_state ($8C80)` is the single
  routine that both ends the sequence and plays that blip.
- **P3-1 investigated, and my own probes were the problem twice.** Two attempts
  to reproduce "ASH/LAMBERT/BRETT cannot be selected" produced false positives
  from badly written harnesses: the first did not reset the panel between
  selections, and the second indexed the *filtered* selectable list with
  `current_index()`, which returns an index into `entries()`. Recording that
  because it wasted real time and nearly produced a wrong fix. **From a fresh
  cursor every living crew member is reachable and selectable**, and only the
  dead one bounces (correctly, `$7720`).
  * **What IS wrong and was found on the way:** `MenuController.back()` resets
    the cursor to 0, so after commanding one crew member you must re-count from
    the top to reach the next. Whether the ROM preserves the row is undecided
    (`$7643`/`$7669` write sentinels into `$64FB`), so this is filed rather than
    "fixed" — but it is the most likely reason a player concludes later names
    are unreachable.
- **Action:** P3-4 and P3-12 implemented and pinned; P3-1 narrowed to the cursor
  reset with the false leads recorded so they are not re-chased.

## D-111 — P3-9 diagnosed, and my P2-22 retraction was WRONG
- **Date:** 2026-08-02
- **★ First, a correction I got wrong earlier today.** D-108 disposed of P2-22
  ("what is the player doing with `$D413`?") by concluding the 164 distinct
  reads were bus noise from a write-only register. **The bus read was indeed
  unsound — but the conclusion was not.** Reading the same thing properly via
  `vice_sid_get_state` shows voice 3's envelope registers genuinely cycling:
  **attack 0-2 and decay sweeping 0 -> 15, over and over**, 40 distinct ADSR
  states in 60 samples. The variation is real. **P2-22 is reopened.** The
  lesson is narrower than I drew it: a bad method can still sit on top of a
  real phenomenon, and "the measurement was unsound" does not entitle me to
  conclude "there was nothing there".
- **What voice 3 actually is:** frequency **0**, waveform sawtooth, **muted by
  3OFF** — so it makes no sound at all. It exists purely as an **envelope
  generator**, and sweeping its decay 0->15 sweeps `ENV3` ($D41C), which is the
  player's modulation source. That is the mechanism D-016 originally described
  and R-20 partly walked back; the truth is in between — ENV3 *is* being driven,
  even though the earlier measurement showed the filter cutoff never moving.
  What ENV3 is used *for* is now the open question.
- **The audible voices, measured:** both **sawtooth**, gates held on, ADSR
  `(attack 15, decay 0, sustain 15, release 0)` — attack 15 is the **8-second
  swell** the synth's own docstring describes. Frequencies run 1204-2025 (voice
  1) and 1804-3034 (voice 2) raw, i.e. roughly **88-178 Hz** fundamentals.
- **So P3-9's "muffled" is the filter eating a sawtooth's harmonics.** A
  sawtooth at 88-178 Hz carries its character in the upper partials; a low-pass
  sitting near the fundamental removes exactly that and leaves a dull hum.
  Measured brightness of our render is ~287 zero-crossings/s, which is about the
  note fundamentals and nothing above them.
- **But raising the cutoff is NOT the fix, and I checked before assuming.**
  Re-rendering with the FC=0 base at 220 / 500 / 1000 / 2000 Hz moves brightness
  only 278 -> 394 -> 436 -> 521 crossings/s while *lowering* RMS. So the 2-pole
  Chamberlin model with resonance floored at q=0.5 is attenuating broadly rather
  than passing a band — the shape is wrong, not just the corner. **Filed as the
  next step: model the 6581's actual filter response** (its low-pass at high
  resonance is far gentler and its minimum cutoff far less absolute than a
  textbook SVF), rather than nudging the constant a third time.
- **Action:** P2-22 reopened with the corrected reasoning; P3-9 kept open with
  the diagnosis and the ruled-out fix recorded so the next attempt starts from
  the filter *shape*.

## D-112 — P3-2: the room-move timer was ~18x too fast, and the base was never `$6586`
- **Date:** 2026-08-02
- **The report** was "selecting a character and sending a movement command moves
  them immediately instead of after a delay like in the original".
- **★ The move handler loads a flat 64, then adds the delays on top.**
  `$7B69` is unambiguous::

      7B57  STA $64E6,Y          ; destination (bit 7 set for a duct move)
      7B69  LDA #$40             ; **64**
      7B6B  STA $64EE,Y          ; the character's action countdown
      7B6E  JSR compute_action_delay   ; ...which ADDS $4032[slot] + $402B[health]

  So a room move is **`$40` + per-slot + per-health**, and `compute_action_delay`
  accumulates onto the same byte (`$405D LDA $64EE,Y` ... `$4064 STA $64EE,Y`)
  rather than replacing it.
- **Measured against the 7.886 Hz main loop:**

      ==========  =========  =========
      character   health     move time
      ==========  =========  =========
      Dallas      6          71 ticks / **9.0 s**
      Dallas      3          87 ticks / 11.0 s
      Dallas      2          119 ticks / **15.1 s**
      Ripley      6          64 ticks / 8.1 s
      Ripley      2          112 ticks / 14.2 s
      ==========  =========  =========

- **What we had instead:** `crew.effective_walk_ticks`, i.e. the `$6586` table
  (3-4) plus a small injury bump — about **half a second**, roughly **18x too
  fast**. `$6586` is a real per-character value the engine uses elsewhere; it is
  simply not the room-move timer, and an earlier pass assumed it was.
- **This is the single biggest feel regression found so far.** A nine-second
  walk is what makes the Personality Control System matter: you commit a crew
  member and then cannot help them, and a wounded one is slower still. With
  half-second moves the whole tension of the design was absent.
- **Four tests were pinning the fast move** and were rewritten to ask the ROM
  for the duration rather than hand-count ticks (`_ticks_to_move`). A fifth,
  `test_orders_execute_at_every_fear_level`, exposed a genuine interaction: with
  a **single** fear-0 crew member aboard, D-103's endgame scan now ends the game
  before any order is processed (`$5B6C` — nobody BROKEN counts as in play), so
  the test needed a second calm crew member to isolate "fear does not block an
  order" from "a broken crew is a loss". Both behaviours are right; the test was
  conflating them.
- **Action:** `MOVE_ACTION_TICKS = 0x40` added with the citation;
  `_action_delay_for` shared between the move path and the action path.

## D-113 — A strong lead on P3-5/P3-6: INDICATE selects its screen from `$7569`, not the deck table
- **Date:** 2026-08-02
- **Context:** the player reports INDICATE LOCATION "partially works — the
  sprite is correctly animating but the rooms it highlights are incorrect or on
  the wrong floor", and that ordering a move sends the sprite wandering.
- **First, what is NOT wrong.** Checked and clean: the remake's room **names**
  all match the ROM's `$A71C` records; every room's **deck** matches `$80D3`;
  and **door neighbours** match `SURFACE_EXITS` for all 34 rooms, zero
  mismatches. So the map *data* is correct and this is a rendering/selection
  fault, not a topology one.
- **★ The lead.** `$76BB`, on the INDICATE path, does::

      76AA  STA $64F7          ; the room being indicated
      76BB  LDA $7569,Y        ; <- per-room screen selector
      76BE  BNE ... / JSR init_menu_ptr    ($7132)
      76C8  CMP #$01 / JSR init_ptr_menu2  ($7112)
      76D2  CMP #$02 / JSR init_ptr_menu3  ($7122)
      76D7  LDY $64F7 / LDA $758D,Y -> $D002 ; then place the pointer
                        LDA $75B1,Y -> $D003

  So the ROM picks **which of three screens to draw** from `$7569`, and only
  then positions the pointer. The remake picks the screen from the **deck**
  table instead — and **the two disagree for 22 of 34 rooms**, which is exactly
  the shape of "highlights the wrong room, sometimes on the wrong floor".
- **This complicates D-091/D-092 and must be resolved before acting.** `$7569`
  was catalogued there as the *duct-map* template index (used by
  `select_menu_template $817D`), splitting rooms 9/16/9, while the deck table
  `$80D3` splits them 10/14/10. Both readings cannot be casually true at once:
  either `$7569` is a general "which screen does this room live on" selector
  that both the deck view and the duct view consult, or `$76BB` is doing
  something narrower than it appears. Note also that `$80D3`'s deck assignment
  was **confirmed live** (FV-2i: AIRLOCK 1 shown under "UPPER DECK"), so that
  half is not in doubt.
- **Deliberately NOT changed yet.** Swapping the remake to `$7569` would touch
  the deck view, INDICATE and the duct map at once, on a reading that conflicts
  with an existing decoded conclusion. The decisive experiment is the one the
  player already suggested: **drive INDICATE LOCATION live for a handful of
  rooms and record which deck name and which map the machine actually shows**,
  then compare against both tables. Filed as the next step for P3-5/P3-6.
- **Action:** P3-5/P3-6 kept open with this lead and the ruled-out causes
  recorded, so the next pass starts from the live experiment rather than
  re-deriving the map data.

## D-114 — P3-1 solved: the dead crew member was a CURSOR TRAP
- **Date:** 2026-08-02
- **The report** was "at the very start of a long game, ASH, LAMBERT and BRETT
  couldn't be selected and controlled". Three earlier attempts failed to
  reproduce it, twice because of my own broken probes (D-110). The fourth
  attempt — walking the panel the way a player does, **firing and backing out
  between each** — showed it immediately.
- **★ Two resets, neither of which the ROM performs.**
  1. **The bounce.** `guard_alien_present ($7720)` refuses a character who is
     asleep or below 2 health by writing `STA $64FB` = 0 — it clears the
     **selection**. It never touches `$64E5`, the panel's cursor row (that byte
     moves only under the cursor keys, `$7474 DEC` / `$74AD INC`). Our version
     reset the cursor, which turned the opening victim into a **trap**: land on
     them, get thrown back to the top of the list, press down once, land on
     them again. **Everyone below the victim was unreachable.** Since the
     victim sits early in the roster, that is most of the crew — exactly the
     three names reported.
  2. **The back-out.** `$7640`-`$7653` writes `$64FB` and `$64BD` and again
     leaves `$64E5` alone, so the highlight stays where you left it and you
     carry on down the list. We reset it to 0, so every command meant
     re-counting from the top.
- **Verified:** all six living crew are now commandable in a single pass down
  the panel, with the dead one stepped over.
- **Worth recording about the process.** This was reported once, filed, and
  "closed" on a headless check that could not see it — because the headless
  check selected crew by *name lookup* rather than by *walking the cursor*. The
  defect lived entirely in the navigation, which no test exercised. The lesson
  is narrower than "test the app": **test the interaction the player actually
  performs**, not an equivalent shortcut into the same state.

## D-115 — P3-15: Jones ran on the frame clock instead of the IRQ clock
- **Date:** 2026-08-02
- `update_3 ($4F5C)` does `LDA $D006 / CLC / ADC #$04 / STA $D006` **in the
  same routine, on the same IRQ tick**, as the pointer step — so the walk and
  the leg animation share one clock. P2-8 scaled the *animation* to `ANIM_HZ`
  but left the X advance running once per **drawn frame** (30 Hz), so Jones
  animated at the right speed while sprinting across the map about 4.5x too
  fast. Both now step together: the crossing takes **8.0 s**, was 2.0 s.

## D-116 — ★ The deck table was never a deck table: `$80D3` is a screen-address byte
- **Date:** 2026-08-02
- **This is the root cause of P3-5 and P3-6**, and it invalidates a premise that
  had been load-bearing since the map was first decoded.
- **What we believed:** `$80D3` is the room -> deck table, values 4/5/6 mapping
  to Upper/Middle/Lower, splitting the ship 10/14/10.
- **What it actually is:** the **high byte of the room marker's screen
  address**. `$81C9 LDA $80D3,Y / STA $FC` pairs it with `$81CE LDA $80B1,Y /
  STA $FB` to form a pointer into screen RAM. Its 4/5/6 values are screen
  **pages** (`$04xx`/`$05xx`/`$06xx`), i.e. which third of the 25-row display
  the marker sits in — which correlates loosely with deck and fooled an earlier
  live spot-check.
- **The real per-room deck/screen index is `$7569`.** `$76BB`, on the INDICATE
  path, reads it to choose which of the three deck plans to draw
  (`init_menu_ptr $7132` / `init_ptr_menu2 $7112` / `init_ptr_menu3 $7122`), and
  `select_menu_template ($817D)` reads the *same* table to choose the matching
  duct plan. It splits the rooms **9/16/9**.
- **Three independent confirmations, all decisive:**
  1. **Marker vs plan.** Place each room's marker (`$80B1`/`$80D3`) on the deck
     plan `$7569` selects: it lands on that plan's grille glyph `$E6` for
     **31 of 34** rooms. Do the same using `$80D3` as the deck: **12 of 34** —
     chance.
  2. **Glyph counts.** The three deck plans (`$A000`/`$A21C`/`$A438`) are
     uncompressed 30x18 grids carrying **9, 16 and 9** grille glyphs — matching
     `$7569`'s 9/16/9 room split exactly, and *not* `$80D3`'s 10/14/10.
  3. **Collisions.** Under the corrected index **every room on every deck has a
     unique marker position** (9/9, 16/16, 9/9). The two "same-deck collisions"
     recorded earlier (CORRIDOR 6/CRYO VAULT, ENGINEERNG/INFIRMARY) were
     artefacts of the wrong assignment — those pairs are on different decks.
- **Why the game looked broken.** Rooms were assigned to decks by an address
  byte, so: INDICATE drew the wrong plan for 22 of 34 rooms ("highlights the
  wrong room, sometimes the wrong floor"), and the character marker appeared on
  a deck the crew member was not on, making ordinary corridor-by-corridor
  movement look like the sprite was teleporting around the ship.
- **This also resolves D-091's loose end.** `$7569` is not a *separate* duct
  partition; it is **the** room -> screen index, and there are two families of
  screens that share it — deck plans at `$A000`/`$A21C`/`$A438` and duct plans
  at `$A956`/`$A9C4`/`$AA6E`. D-092's decode of the duct plans stands; only the
  interpretation of what the index *means* was too narrow.
- **Action:** `nostromo_ship` now takes the deck from `$7569`. The old test
  asserting the 10/14/10 split was pinning the bug and is rewritten, with the
  glyph-count cross-check added alongside.

## D-117 — P3-3 and P3-13: a latched alarm and two unmapped glyphs
- **Date:** 2026-08-02
- **P3-3 — the tracker alarm was a latch, and should be a pulse.** The remake
  set `tracker_alarm` and never cleared it, so once used the status line read
  "TRACKER ALARM: SOMETHING MOVING" **forever**, permanently sitting over the
  ALSO HERE row. That is why the readout looked dead rather than responsive.
  The ROM's alarm is `$64B6`, armed at `$8DF6` and **silenced by
  `reset_attack_state ($8C82)`** — which is the same routine that plays the
  movement blip, so a completed move ends it. Now cleared on that cue.
  * The detection itself was already right and already covers the cat and the
    crew as well as the Alien, which the game's own caption confirms is the
    intent: `$4554` says **"SOMETHING MOVING BETWEEN LOCATIONS"** and never
    names what. Pinned with a test that triggers on the cat alone and on a
    crew member alone.
  * Re-confirmed on the way: `$7339`-`$7352` is **not** the tracker. It is the
    duct body-discovery scan (a mover finds an incapacitated character already
    in the ducting, health `< 2` at `$734E`), feeding `check_tracker ($595A)`'s
    "'S BODY IS HERE" notice — exactly as D-041 recorded.
- **P3-13 — two unmapped characters were dropping whole lines to SysFont.**
  `_c64_or_sysfont` falls back for the *entire string* if any character is
  missing from `_ASCII_TO_SCREEN_CODE`, so one stray glyph changes the font and
  size of a whole row — the "renders strangely" report. Two culprits:
  * `"-"`, used as the empty-field placeholder in `ALSO HERE: -`. The ROM
    leaves an empty field as blanks (`$A0`); the dash was ours.
  * `"*"`, in the invented `*WARNING*` decoration. The ROM's own banner
    (`$5485`) is delimited with **colons** — `:WARNING:` — and `:` is a real
    decoded glyph (`$1C`, D-078).
  Both replaced with the ROM's forms, and a test now asserts **every** status
  line renders in the game's charset, so the next stray glyph is caught in CI
  rather than in play.
  * **Filed separately:** `"ALSO HERE"` does not appear anywhere in
    `ALIEN.prg`, so the label itself may be invented. Not changed in this pass
    (it is a wording question, not a rendering one), but recorded.

## D-118 — P3-8 and P3-11: a dead QUIT key and a flash at the wrong rate
- **Date:** 2026-08-02
- **P3-8 — "Q QUIT" did nothing.** `_MENU_KEYS` mapped `K_q` to
  `InputEvent.QUIT` correctly, and `poll_input` forwarded it to the flow — but
  `_on_welcome` only handles `SELECT_FULL`, and the renderer's `_quit` flag was
  set solely by Escape or the window close. So the event was raised, delivered,
  and dropped. A menu QUIT now ends the program like any other.
- **P3-11 — the border flash had the right colours at the wrong rate.**
  P2-12 implemented `wait_keypress_flash ($8660)` as one palette step per
  rendered frame. But `INC $D020` runs on **every input poll**, thousands of
  times a second, so `$D020` changes *many times within a single displayed
  frame* — the border comes out as a dense stack of horizontal colour bands,
  which is what "colourful rainbow noise" means. One step per frame produced a
  slow, readable cycle instead. Now drawn as raster bands: **all 16 palette
  entries are visible in one frame** (measured), where before there was 1.
  * Worth noting the shape of this mistake: the *citation* was right and the
    implementation still did not look like the original, because a per-poll
    write and a per-frame write are different phenomena on a raster display.
    Reading the routine was not enough; the rate had to be reasoned about too.

## D-119 — P3-7: the WELCOME ring IS the loader's marquee, and it should chase
- **Date:** 2026-08-02
- **The player said both front-end screens animate.** D-104 had already found
  the GREEN VALLEY spiral; the second screen turns out to be sitting in the
  same BASIC, a few lines further on, and we had already captured a **frame of
  it** without realising.
- **`****MARQUIE****` (MENU1.prg 330-380)** pokes blanks (`160` = `$A0`) around
  the screen edge with a colour ramp::

      340 FOR T=1024 TO 1063 : POKE T+54273, T-1023 : POKE T,160 : NEXT   ' top
      350 FOR T=1024 TO 2024-40 STEP 40 : K=K+1 : POKE T+54272,K ...      ' left
      360 POKE T+54311,K : POKE T+T1,160 : NEXT                           ' right
      370 FOR T=1984 TO 2023 : POKE T+54273, T-1984 : NEXT                ' bottom

- **★ That ramp is exactly the ring D-064 captured live.** The top row's
  `T-1023` gives 1,2,3,... and the capture reads 2,1,2,3,4,... — the leading 2
  being the corner the left column overwrites. So the "static rainbow ring" we
  reproduced pixel-perfectly was **one frame of a chase**, and reproducing it
  faithfully as a still image was itself the bug. `_welcome_border_colour` now
  takes a `phase`; at 0 it still matches the capture byte-for-byte (the drift
  guards depend on that), and advancing it rotates the ramp.
- **Lesson worth keeping:** a live capture pins a *moment*, not a behaviour. We
  had proof the colours were right and no evidence at all about whether they
  moved — and never asked.
- **P3-10 — joystick detection ran once, at construction, in silence.** A stick
  plugged in after launch was never seen, and nothing told the player whether
  one had been found, so "the arrow keys respond, the joystick does not" was
  indistinguishable from "no device". Now re-runnable, wired to
  `JOYDEVICEADDED`/`JOYDEVICEREMOVED`, and it prints what it attached to.

## D-120 — ★ P3-9, P2-22 and R-20 are one finding: the filter sweep was switched off
- **Date:** 2026-08-02
- **Three open items collapse into one cause.** The player's "the intro sounds
  muffled and is missing instrumentation", the unexplained `$D413` variation,
  and R-20's gate-glitch rule were all the same thing seen from different
  angles.
- **★ The player says outright what voice 3 is for.** `title_music_player
  ($9039)` opens with two instructions::

      9039  LDA $D41C     ; ENV3 — voice 3's envelope level
      903C  STA $D416     ; -> filter cutoff, HIGH byte

  Voice 3 is muted (`3OFF`) with frequency **0** precisely so it can serve as a
  modulation source, and `$D413` (its decay) is swept **0 -> 15** continuously
  to shape how fast that envelope falls. **That answers P2-22**: the `$D413`
  variation is the tune's filter LFO.
- **★ And that is why it was muffled.** `_Envelope.gate_on` carried R-20's
  suppression, which ignored a gate-off/gate-on pair arriving with no samples
  between — exactly the pattern the player uses to retrigger voice 3. So voice
  3's envelope **never rose**, ENV3 stayed 0, and the cutoff never opened:

      ==========================  ================  ==============
      `$D416` writes over 8 s     with suppression  without
      ==========================  ================  ==============
      distinct values             **3**             **152**
      nonzero                     1%                48%
      ==========================  ================  ==============

  Over the full 102.4 s loop it is now **256 distinct cutoff values, nonzero
  76% of the time** — the sweep the whole arrangement is built on. Removing it
  restores the "instrumentation" the player could hear was absent.
- **R-20 is retracted, and both its halves have explanations.**
  1. *"ENV3 and `$D416` read zero in every sample."* True, and misleading —
     the captures sampled at roughly a **quarter of a second**, far too coarse
     to catch an envelope transient. **I repeated the same mistake** on
     2026-08-02 with `vice_sid_get_state` and drew the same wrong conclusion
     (D-106/D-109), which is how the fix reached "raise the cutoff base" twice
     without ever asking why the cutoff never moved.
  2. *"Retriggering caused runaway resonance and hard clipping."* Real at the
     time, but a property of the **old filter `q` mapping**, since replaced. A
     102.4 s render now peaks at 28449 with **zero** clipped samples.
- **The methodological point, stated plainly.** Three separate live captures
  agreed on "always zero", and all three were wrong in the same way. Agreement
  between measurements taken the same way is not corroboration. The thing that
  actually settled it was reading the two instructions at `$9039` and asking
  what they implied the data *should* look like — the static code caught an
  error that repeated live measurement had reinforced.
- **Action:** the suppression is removed with the retraction recorded inline;
  `tests/test_remake_sid_gate.py`, which existed solely to pin R-20's
  conclusion, is rewritten to pin the opposite and to assert the sweep is alive
  and non-clipping. D-106/D-109's "raise the FC=0 base to 220 Hz" stands on its
  own merits (a 6581 minimum of 30 Hz is wrong regardless) but was never the
  cause.

## D-121 — P3-14 answered: the deck map's grilles are static art, and never change
- **Date:** 2026-08-02
- **The player asked** whether it is faithful that removing a grille leaves the
  deck map unchanged, with every grille still shown in place. **It is.**
- **Three pieces of evidence, all static and all conclusive:**
  1. The three deck plans (`$A000`/`$A21C`/`$A438`) are **uncompressed 30x18
     character grids** — fixed art, carrying 9/16/9 grille glyphs (D-116).
  2. **Nothing anywhere in `ALIEN.prg` writes `$E6` (the GRILLE glyph) into
     screen RAM at runtime.** There is no `LDA #$E6` at all.
  3. `draw_grille_option ($86F0)` — the only routine that reacts to a grille's
     state — writes to `$046E`, `$064E` and `$0711`. Those are **row 2 col 30,
     row 14 col 30 and row 19 col 25**: the CONTROL panel columns and the
     status line — `$0711` is row **19**, below the map, which occupies rows
     0-16. It never touches the map area.
- **So the grille state is reported only in the panel** ("REMVGRILLE" moving to
  "GRILLE" in the MOVE TO column, D-101) and on the status line ("GRILLE IN
  PLACE" / "GRILLE REMOVED", `$86C8`/`$86D7`). The deck plan is a fixed drawing
  of the ship and stays that way — which also means the map never reveals which
  grilles are open, so the player has to remember.
- **Action:** P3-14 closed as faithful; no change made. Recorded because "the
  remake does not do X" was the right answer here, and it would have been easy
  to "fix" the map into something the original never did.

## D-122 — `$6586` is not a walk-ticks table either: it is the state backup
- **Date:** 2026-08-02
- **Follow-up to D-112.** Having established that the room-move timer is
  `$7B69`'s flat `#$40` plus `compute_action_delay`, the obvious question was
  what `$6586` — labelled "9 per-character walk durations" since the tables
  were first decoded — actually is.
- **★ Nothing in `ALIEN.prg` reads `$6586` at all.** The only access anywhere
  near it is `sub_beep ($659A)`: `LDA $6583,Y / STA $656E,Y` for 21 bytes. So
  the region from `$6583` is the **pristine backup of the runtime state block
  at `$656E`**, copied over it at game start — and the crew's starting
  composure table (`$6571`) sits inside that block.
- **Which is why the numbers looked plausible.** "Crew walk ticks"
  (4,4,3,4,3,4,3) are **byte-identical** to `START_FEAR` read from `$7D5D`,
  because they are the same values seen twice under two names. A table of
  per-character *durations* that happens to equal the per-character *composure*
  should have prompted a second look years earlier.
- **Consequences, all now applied:**
  * `CrewMember.effective_walk_ticks` is **removed**. It added "one tick per
    point of lost health" on top of the mislabelled base — an invented rule
    with no citation, and dead code since D-112 moved movement onto `$7B69`.
    Its two tests went with it.
  * `walk_ticks` survives only as a constructor field the tests use; it drives
    nothing.
  * **`JONES_WALK_TICKS = 5` is downgraded to `[?]`.** It came from `$6586 + 8`,
    which lands on `var_frame_divider` (`$6579` = `05 B9 09 ...`) — a frame
    divider, not a cat. D-036 had already flagged that Jones is driven by code
    this project has not located (slot 8 is outside the `Y=1..7` loop); the
    value stays because it produces a plausible amble, but it is a placeholder.
  * `gamedata.py`'s module docstring corrected for both `$6586` **and** `$80D3`
    (D-116), so the decoder no longer teaches the two wrong labels.
- **The pattern worth naming.** Both `$80D3` and `$6586` were mislabelled the
  same way: a table was found near data that was being used, its values looked
  reasonable for the guessed purpose, and no one checked **who reads it**.
  Grepping for readers is cheap and would have caught both — `$6586` has none,
  and `$80D3`'s only reader pairs it with `$80B1` as an address.

## D-123 — ★ The room-name table has a 2-record GAP: 31 of 36 names were wrong
- **Date:** 2026-08-02
- **Found by applying D-122's lesson** — audit *who reads each table* — to
  `$A71C`. Grepping showed no indexed reader at all, which led to
  `set_room_screen_ptr ($7948)`, and it does **not** index a flat table::

      7948  ASL A / LSR A          ; strip the in-duct bit
      794E  CMP #$11 / BCC $7984   ; rooms 0-16  -> base $A71C
      7952  CMP #$22 / BEQ $7956   ; room 34     -> pointer $5DD1
      795F                          ; rooms 17-33 -> base $A7DA

  `$A71C + 17*10` is `$A7C6`, but the ROM uses **`$A7DA`** — **two records
  further on**. Those two filler records are exactly what a flat read has been
  reporting as the duplicate **"OTHER LIST"** rooms, the ones the snapshot had
  to disambiguate with `_1`/`_2` suffixes. They were never rooms.
- **Consequence: every name from id 17 up was shifted by two — 31 of 36 wrong.**
  The corrected table reads ENGINE 1/2/3, ENG STORES, INFIRMARY, INF STORES,
  LABORATORY, LAB STORES, LIFE SUPPT, LIVNG QTRS, MESS, RECRTNAREA, STORES 1/2/3,
  SHUTTLEBAY (**32**), SHTTLSTORE (**33**) and — from its own pointer `$5DD1` —
  **room 34 = "NARCISSUS"**. There are **35 rooms (0-34)**, not 36.
- **This is the "ship's map and room names aren't correct" report (P3-6).** The
  *topology* was right all along — ids, doors, ducts and marker positions never
  moved — but the labels on them were wrong from room 17 up, so a crew member
  walking a perfectly legal corridor appeared to arrive somewhere unrelated.
- **Two independent corroborations, both of which had looked like oddities:**
  1. `$5776` puts **LAUNCH NARCISSUS** on room 34. Under the old table that was
     "SHUTTLEBAY" — a shuttle bay you launch the Narcissus from is odd; under
     the corrected table it is the **NARCISSUS itself**, which is exactly right.
  2. The duplicate "OTHER LIST" pair had needed special handling for months
     (`slugify` disambiguation, and D-092's cross-sheet analysis singled out
     room 18 as a strange three-way hub). Duplicated names in a table of
     distinct rooms was the tell, and it was treated as a quirk rather than a
     symptom.
- **Scope of the change:** `gamedata` now computes each name's address through
  `_room_name_addr` (the ROM's own three-way branch); the snapshot regenerated;
  `nostromo` updated so only **NARCISSUS** is off the deck plans (SHUTTLEBAY and
  SHTTLSTORE are ordinary mapped rooms, which the flat error had pushed out of
  range); `menu.SPECIAL_ROOM_LAUNCH` moved to `narcissus`; the marker tables
  trimmed to 35 entries. Deck split is a clean **9/16/9** plus NARCISSUS beside
  AIRLOCK 2. Twelve tests carried the old names and were updated — every one of
  them asserted a *name*, never a topology, which is why nothing else moved.
- **The audit that found it is worth repeating on any new table.** Two
  mislabels (`$80D3`, `$6586`) and one structural error (`$A71C`) all came from
  assuming a table's shape instead of reading its consumer. Grepping for
  readers is cheap; three separate multi-month errors would have been caught
  the first day.

## D-124 — P5-9: both front-end animations were frozen by a counter in the wrong place
- **Date:** 2026-08-02
- **Reported for the third time.** The GREEN VALLEY colour-RAM spiral (D-104)
  and the WELCOME marquee chase (D-119) were each decoded from the loader's
  BASIC, implemented, and unit-tested — and in the actual game **neither
  moved**.
- **Cause:** `self._frame_count += 1` lived inside `render()`, which is the
  **play-screen** path. On LOADING_MENU / WELCOME / NOTICE / TITLE it never
  advanced, so every animation keyed off it drew the same phase forever.
  Moved into `draw()`, the app loop's actual per-frame call.
- **★ Why the tests did not catch it, which is the real lesson.** Both existing
  tests called the draw helper directly and **set `_frame_count` by hand** to
  check that different values produce different pixels. That proves the drawing
  function is correct; it says nothing about whether the counter ever changes.
  A green test suite reported an animation that a player could see was static.
  The new guard drives `draw()` thirty times and hashes the whole surface —
  **testing the loop, not the helper.**
- **Measured after the fix:** GREEN VALLEY 10 distinct frames / 30 draws,
  WELCOME 16 / 30. (An initial check reported the spiral still frozen; that was
  my sampling window — I hashed only the first 4000 bytes, the top-left corner,
  which is where the spiral paints *last*. Worth noting because it nearly sent
  me chasing a second bug that did not exist.)
- **Also recorded from the same audit:** `guard_alien_present ($7720)` bounces a
  selection on **four** conditions, and the remake models only two. Missing are
  `$7740 CPY $64CC` (**is the revealed android**) and `$7757 LDA $6571,Y / BNE`
  plus `$7768 find_colocated_crew / CPX #$08 / BEQ` (**composure 0 *and* nobody
  else in the room**). The player's guess that some crew "start as Insane"
  points straight at that composure gate. Filed as P5-6.

## D-125 — ★ P5-6 solved: a fixed start table, a fourth selection gate, and a 60x cadence error
- **Date:** 2026-08-02
- **Reported four times and never reproducible headlessly**, because every
  previous probe checked the *menu* at tick 0. Running the simulation for a few
  seconds reproduced it instantly: **within 20 ticks (~2.5 s) only 3 of 7 crew
  were commandable.** Three separate faults, all now decoded.

- **★ 1. The starting positions were invented.** `new_game`'s init loop copies
  three template tables into the runtime arrays::

      65FF  LDA $793D,Y / STA $7935,Y    ; locations
      6605  LDA $7D4D,Y / STA $7D45,Y    ; health
      660B  LDA $7D5D,Y / STA $7D55,Y    ; stress

  `$793D` is a **fixed table**: DALLAS/KANE/RIPLEY -> COMMDCENTR,
  ASH/LAMBERT/PARKER -> **MESS**, **BRETT -> AIRLOCK 1** — and slot 0 puts the
  **Alien in AIRLOCK 1 too**, so Brett starts in the room with it. Only the
  victim moves afterwards (`$50AB-$50B5` writes health 0 and location `$FE`).
  What the remake had was "first three alive in roster order -> COMMDCENTR, the
  rest -> LIFE SUPPT" (D-014) — a rule that **depends on who died**, which a
  static table cannot do, that drops Brett's airlock start, and whose "LIFE
  SUPPT" was room 27 read under the pre-D-123 name shift (room 27 is **MESS**).

- **★ 2. `guard_alien_present ($7720)` has FOUR gates; we modelled two.**

      773B  LDA $64D1,Y / BNE bounce   ; in hypersleep            (had it)
      7740  CPY $64CC   / BEQ bounce   ; the slot `$64CC` names   (MISSING)
      7745  LDA $7D45,Y / CMP #$02 / BCC bounce  ; health < 2      (had it)
      7757  LDA $6571,Y / BNE ok       ; composure 0 ...
      7768  JSR find_colocated_crew / CPX #$08 / BEQ bounce  ; ...and alone

  `$64CC` holds a **slot number**, written by the android's attack path
  (`$52D4 LDA $7214 / STA $64CC`, which also recolours the background at
  `$52DA`) — being set upon by the android takes that crew member out of your
  hands. And the composure gate is subtler than "broken = lost":
  `find_colocated_crew ($4581)` looks for another crew member matching on
  **room** *and* **duct state** with health >= 2 **and composure != 0**
  (`$45AE`), so a broken crew member stays commandable while someone functional
  is with them. **Two broken crew do not rescue each other** — which is exactly
  what a player meant by guessing some characters "start as Insane".

- **★ 3. The real cause: per-tick application of per-TURN behaviour.** The ROM
  gives every character an action countdown (`$64EE,Y`) and hangs its
  behaviour off it — the android's attack is reached from
  `dispatch_char_action` on **its own turn**, and `raise_crowd_fear` is called
  once per **Alien** turn (`$4CC3`, inside the `$4CB3` block). The remake ran
  all of it **every tick**, so with D-112's correct ~71-tick turns the android
  was wounding someone roughly **60x too often**: LAMBERT fell from health 4 to
  1 in about three seconds and PARKER was locked out immediately. Now gated on
  a per-character turn clock.
  * Note `raise_crowd_fear` **increments** `$7D55` (capped at 10, skipping
    anyone already at 0) — company is *reassuring*, and the remake already had
    that direction right; only its rate was wrong.

- **Result:** at tick 0, **6 of 7 commandable** (only the opening victim), and
  the roster degrades over minutes of play rather than seconds — driven by
  decoded mechanics rather than a cadence bug.
- **Left open honestly:** at ~2.5 minutes a run can reach 1 of 7 commandable.
  Every individual block is now traceable to a ROM gate, but whether the
  *aggregate* difficulty matches the original is a balance question that needs
  the live oracle, not more static reading. Filed rather than tuned.

## D-126 — ★ `$64CC` names the ANDROID, not its victim — and the unrevealed android never attacks

*2026-08-06. Filed from play-report #6 items 2 and 5 ("Ash and Lambert started
out as unselectable… is the other one being marked as an android?" / "the crew
all became gradually uncontrollable").*

Two inverted readings of the same cell, both in the crew-selection path, and
together they were the single largest source of the remake feeling unplayable.

**1. `$64CC` is the acting slot.**

    52D4  AD 14 72  LDA $7214
    52D7  8D CC 64  STA $64CC
    52DA  8D 21 D0  STA $D021

`$7214` has **exactly one writer** in the whole image — `$723E STY $7214` —
which records the character whose turn is being dispatched. So the value stored
into `$64CC` is the **android's own slot**, and `guard_alien_present`
(`$7740 CPY $64CC / BEQ`) then refuses to select it. `$52DA` writes the same
number to the background colour: the lockout and the screen flash are one
event, and being unable to select a crew member IS the game telling the player
who the android is. `state.py` had this right; `sim.py` wrote the **victim's**
slot from the attack path instead, permanently benching every crew member the
android ever touched.

**2. The unrevealed android does not attack.** `$5265` routes the android's
turn on that same cell::

    5265  A9 04     LDA #$04
    5267  8D E8 03  STA $03E8
    526A  AD CC 64  LDA $64CC
    526D  F0 03     BEQ $5272      ; not found out -> ordinary dispatch
    526F  4C F1 52  JMP $52F1      ; found out    -> the attack path

Only `$52F1` reaches the co-located-crew scan (`$5311`-`$5337`) that ends in the
attack at `$5345`; it also falls through to `char_wander` on three separate
conditions. Before it is found out the android takes `dispatch_char_action` and
**passes for crew** — it obeys orders and harms nobody. Ours attacked from tick 0.

Note also that `$5439`, which we had labelled "the android attack", is reached
from a single site: `$8754`, a branch of `sub_char_special` taken when the
action code is 3. It is a *special-action handler*, not a per-tick behaviour —
which is the structural tell that we were calling it on the wrong schedule.

**Measured effect** (10 seeds, FULL mode, crew commandable at 1200 ticks ≈ 2.5
minutes of play): **before** 3-of-7 typical, one seed 1-of-7; **after** 6-of-7,
with the opening victim the only standing blocker. Composure was never the
culprit — it drifts *upward* for crew left alone; the drain was health.

**Action:** fixed in `sim._reveal_android` / `sim._apply_android_attack` and the
`advance` call site; `state.locked_crew_id`'s docstring corrected. Covered by
`test_reveal_locks_the_android_itself_not_its_victim`,
`test_the_attack_path_never_locks_anyone` and
`test_an_unrevealed_android_does_not_attack`. Closes todo P6-2 and P6-5, and
**retires P5-10** — the aggregate difficulty was this bug, not tuning.

**Lesson (again).** This is the "who reads this table?" audit in its other form:
*who writes this cell, and with what?* One `grep` for `STA $7214` — one writer,
and it is the actor — settled a question that had been answered backwards for
months and had already survived four rounds of headless probing, because every
probe checked tick 0, and the corruption needed a turn to happen.

## D-127 — ★ RETRACTS D-119: the WELCOME marquee never animated; the ramp is an off-by-one

*2026-08-06. Filed from the player's standing request to "break down exactly
what that code is doing" on the `1 ALIEN / Q QUIT` screen.*

D-119 concluded the WELCOME ring was "one frame of a chase" and added a `phase`
that rotated it every other frame. **The BASIC does not support that.**

**What `****MARQUIE****` (MENU1.prg 330-380) actually does**, line by line:

    340 K=1:FORT=1024TO1063:POKET+54273,T-1023:POKET,160:NEXT T
    350 FORT=1024TO2024-40STEP40:K=K+1:POKET+54272,K:POKET,160
    360 POKET+54311,K:POKET+T1,160:NEXT T
    370 FORT=1984TO2023:POKET+54273,T-1984:POKET,160:NEXT T

- **340 — top row.** Cells 1024-1063 (row 0) get glyph `160` (`$A0`, reversed
  space). Colour goes to `T+54273`.
- **350/360 — both side columns in a single pass.** `T` steps 40 from 1024 to
  1984 = rows 0-24 of column 0. `K` increments once per row (so row 0 gets 2).
  `T+54272` colours column 0, `T+54311` (= `+54272+39`) colours column 39, and
  `T` / `T+39` take the glyph.
- **370 — bottom row**, same shape, values 0-39.

**★ The ramp's odd start is an off-by-one, not a phase.** Colour RAM for screen
cell `T` is `T+54272`; lines 340 and 370 poke **`T+54273`**, i.e. the cell to
the *right*. Cell 1024 therefore never receives a colour from the top-row pass —
its colour comes solely from line 350's first iteration, where `K` has just
become 2. That is exactly why D-064's live capture reads `2,1,2,3,4,5,...`
across the top. **A single pass explains the capture completely.**

**And there is no loop.** `MARQUIE` has exactly one caller — line 600,
`MM=9:PRINTCHR$(147):GOSUB330` — after which the menu is printed and the program
sits in line 730, `GETC$:IFC$=""THEN730`, a bare key-wait that pokes nothing.
Drawn once, never touched again.

**What *does* animate is the spiral**, `GOSUB 150` at line 590: lines 200/210
run `Q` 11->1 then 1->11, each `GOSUB 220` painting one flat-coloured ring with
`W` advancing (`230 W=W+1:IFW>15THENW=0`). That is a **one-shot 22-ring wipe**
followed by the centred publisher name and a `FORXX=1TO900` pause — also not a
running loop.

**Action:** `_welcome_border_colour` is now called with `phase` fixed at 0 and
its docstring rewritten; D-124's animation guard is amended to require
LOADING_MENU to move and WELCOME to stand still. `_MARQUEE_RATE` is now unused
by the app.

**Lesson.** D-119 reasoned from a *live capture plus a plausible mechanism* and
never checked the routine's caller. One `grep` for `GOSUB330` — one hit, in
straight-line code — would have settled it. The same shape of mistake as D-126:
the fact was in the control flow, not in the routine everyone was reading.

## D-128 — the attack siren stop was scoped to the wrong tick, not to the wrong signal

*2026-08-06. Reported three times (P3-12, P5-3, P7-12) before it stuck.*

`play_sound_cues` computed its `attacking` gate like this::

    attacking = any(c.effect == sound.ATTACK_ALERT for c in cues)

where `cues` is **only the current tick's** `SoundCue` list. But the
`ATTACK_ALERT` cue is raised on exactly **one** tick — the one where
`alien.py`'s wound path (`$4230`/`$5354`) fires — while the real attack
sequence, `$64BB`, is a **latch** that stays set for its whole duration and is
tested directly by the blip routines (`$4E42`/`$4E5C`). So on every tick after
the first, the local `attacking` silently went back to `False` even though
`self._attacking` (this remake's own copy of `$64BB`) was still `True`. Any
**other** crew member's ordinary movement or grille blip, completely unrelated
to the attack, then read `attacking=False`, passed `sound.audible`, landed in
`played`, and tripped the renderer's own "a blip means the attack ended"
branch — stopping the siren after one loop period. That is the "small squeak
and then nothing" report, verbatim, on its third occurrence.

**The earlier "fix" (the `loops=-1` change already on file as P3-12) was real
but incomplete**: it correctly diagnosed that a one-shot clip couldn't sustain
a loop, and correctly cited `$64BB`'s lifetime in its own docstring — but the
code computing the gate didn't consult that lifetime, it recomputed a
same-tick approximation of it. A headless test asserting the loop existed
(`test_the_alert_is_a_loop_not_a_one_shot`) passed the whole time, because it
never drove two ticks in sequence.

**Fix:** `attacking = self._attacking or any(...)` — OR in the renderer's own
persistent flag, which IS `$64BB`, instead of re-deriving it from one tick's
cues. Covered by `test_siren_survives_an_unrelated_movement_blip`, which
reproduces the actual two-call sequence: an attack tick, then a later tick
carrying only an unrelated `MOVEMENT` cue.

**Lesson.** Citing the right ROM address in a docstring is not the same as the
*code* consulting the value that address represents. When a state persists
across ticks in the ROM, model it as a stored flag and test it across at least
two calls — a single-tick unit test cannot see a scope bug like this one.

## D-129 — ★ the motion tracker arms passively; USE was never the gate

*2026-08-06. Filed from the player's own diagnosis in P6-4: "the tracker
doesn't need to be used to enable the behavior if it is held by a crew
member."*

`check_deferred_move` — the same routine that plays the movement/grille blip —
calls the alarm scan **unconditionally**, right next to it::

    72F9  20 80 8C  JSR reset_attack_state   ; plays the blip, clears $64B6
    72FC  20 32 8E  JSR check_6562           ; the alarm scan — no USE gate

`check_6562` is reached only through `char_pump`'s own `$6517` flag, which is
set whenever **any** character's queued move resolves — a general "something
just finished moving" signal, not a per-item USE dispatch::

    7239  A9 01     LDA #$01
    723B  8D 17 65  STA $6517       ; "a move just completed"
    723E  8C 14 72  STY $7214       ; the acting slot (D-126's same cell)
    7241  4C 56 51  JMP resolve_char_move

There is no `$64BB`/USE-order test anywhere on this path. Our model instead
routed the tracker's detection exclusively through `_resolve_use_order`, so it
only ever ran on the one tick the player issued an explicit `USE` — which is
why the player's report was literally "it never fired even with movement in
adjacent rooms": between USE orders, nothing was watching at all.

**Also recovered nearby, corroborating the player's other point ("the cat
moving" should trigger it too):** `select_char_turn` writes one of two
messages depending on what it finds — the reading text at `$8D58` ("...HAS A
READING") or a second string at `$8D49` decoding to **"JONES IS UNEASY"**.
Two distinct outcomes for two distinct triggers, and one of them is Jones by
name — independent confirmation that the cat is a real trigger, not folklore.

**Action:** `Simulation.advance`'s movement-blip step (3.8) now also runs, for
every crew member currently holding a tracker, an automatic `_use_tracker`
call whenever a completed move is detected this tick — crew, Alien, or Jones.
No order is required; carrying the item is enough. The detection *radius*
remains the standing `[?]` (ship-wide vs. adjacent-only is still undecoded,
per `_use_tracker`'s own docstring) — only the trigger changed. Covered by
`test_tracker_arms_passively_without_a_use_order`, which queues no `USE` order
at all and drives an unrelated crew member through a real multi-tick move.

**Lesson.** The existing docstring on `_use_tracker` already cited the right
open question (radius) but had never checked whether the *call site itself*
was gated correctly — the same shape of gap as D-128 the same day: a correct
citation next to code that didn't consult it.

## D-130 — ★ panic-wander needed both a composure gate and a per-character cadence

*2026-08-06. Filed from P6-3: "Some characters moved to another room as soon
as the alien attacked one person. Is that what happened in the original? I
seem to remember them staying mostly still until I gave them commands."*

The player's memory was correct, and the bug was worse than a missing gate —
it was two compounding ones.

**1. No composure requirement at all.** `char_wander` is reached only through
`resolve_char_move`, the per-character engine's own turn routine, which opens
with::

    5170  LDA $6571,Y / CMP #$02 / BCC $517A   ; composure < 2, else...
    5177  JMP dispatch_char_action              ; ...ordinary dispatch

An ordinary-composure (>= 2) crew member **never reaches `char_wander` at
all**. Our model instead wandered *any* crew member merely for sharing a room
with a surfaced Alien, with no composure test whatsoever — so a perfectly calm
crew member bolted the instant the Alien attacked their roommate.

**2. Evaluated every tick instead of on the character's own turn.**
`resolve_char_move` runs only when that character's own `$64EE,Y` countdown
reaches zero — the same per-character cadence ordinary moves use, roughly
once every 8-15 seconds (D-112). Our model re-rolled the panic check every
single simulation tick (~60/sec) for every co-located crew member, which is a
three-orders-of-magnitude difference in trigger rate on top of the missing
gate.

**The finer split, also decoded and now modelled:** past the composure gate,
`$51DF` branches again on the *exact* value::

    51DF  LDA $6571,Y / BEQ $51E7      ; composure == 0 -> broader path
    5252  ...composure == 1: wanders ONLY if sharing a room with a
          **surfaced** Alien (the trigger already modelled pre-D-130)...
    51E7  ...composure == 0: wanders when the Alien is hidden in a duct, OR
          surfaced somewhere else entirely...

**Left undecoded, deliberately:** composure == 0 while *also* sharing a room
with a **surfaced** Alien takes neither of the above — it falls to `$51F4`,
which re-arms the action timer and queues something that is not
`char_wander`. What that something is has not been traced. Rather than invent
it, that one sub-case is left alone (the crew member simply keeps whatever
order it already had).

**Action:** `_apply_panic_wander` now gates on `_turn_due(crew)` (this
remake's existing per-character cadence primitive, already used for the
android) and on `constants.PANIC_WANDER_MAX_COMPOSURE = 2`, and splits the
composure-0/composure-1 cases per the trace above. Covered by
`test_ordinary_composure_crew_do_not_bolt_from_the_alien` (the regression this
closes) and the existing composure-1 bolt/order-drop tests, both updated to
set composure explicitly since the crew default (fear=4, D-126) is well above
the new gate. Two of those tests now call `_apply_panic_wander()` directly
rather than through `advance()` — a full tick also runs the Alien's own
co-located wound pass, which drops composure further on the very same tick
and changes which `$51DF` branch applies, a real interaction but not what
those two tests isolate.

**Lesson.** Same shape as D-128/D-129 the same week: the routine had been
decoded and cited correctly (`char_wander`'s trigger, D-043), but the *entry
gate into* the routine had never been read — twice in three days the missing
piece was the caller, not the callee.

## D-131 — P6-6 ANSWERED: it IS faithful — the deck view was never meant to follow crew

*2026-08-06. "The deck view doesn't change as crew members move up or down
deck levels. The crew member just appears to disappear."*

Checked both the disassembly and the manual, and they agree.

**Code:** `guard_alien_present`'s panel-refresh path positions the selected
crew member's marker (`$76D7`, sprite 1) by indexing two 36-entry byte tables
(`$758D`/`$75B1`) with the character's own room (D-058) — unconditionally,
regardless of which of the three deck templates is currently drawn. The three
templates themselves come only from `draw_deck_map` (`$73C8`), called only
from the numbered UPPER/MIDDLE/LOWER menu handlers (`$750D`/`$7666`). No
routine anywhere reads the selected crew member's deck and switches the
displayed template to match.

**Manual:** MENU1.prg's own instructions text says so outright (line
11050): *"A MAP OF THE SHIP WHERE YOU CAN WATCH YOUR CREW MEMBERS MOVING
ABOUT. EACH DECK OF THE SHIP CAN BE SELECTED FROM THE MENU."* Manual deck
selection is the documented design, not an omission the manual failed to
mention.

**The remake already matches this**: the renderer only draws the marker
`if mroom.deck == self._view_deck`, so a crew member leaving the viewed deck
already vanishes until the player switches — the exact behaviour reported as
a bug. No code change; closed as faithful, the same pattern as P3-14
("removing a grille doesn't show on the deck map — also faithful"). Covered by
a new regression, `test_marker_only_shows_on_the_deck_you_are_viewing`, so a
future "helpful" auto-follow patch would have to consciously break this test
rather than slip in unnoticed.

**Lesson.** Not every play-report item is a bug. The discipline runs both
ways: the same rigor that catches inventions should also stop a plausible
"obviously an oversight" fix from being applied against something the source
material states on the record.

## D-132 — the ATTACK order existed, fully implemented, with no way to issue it

*2026-08-06. Filed from P5-4, itself carried over unresolved from an earlier
audit that had already located the likely ROM site but not acted on it.*

`OrderType.ATTACK` and `Simulation._resolve_attack_order` (`$4940`) were both
complete — deterministic per-item damage, acid-spill room damage, win-route
detection on a kill — but `menu.py`'s `_special_entries` never constructed an
`Order(..., OrderType.ATTACK)` anywhere. The order existed with no UI path to
it at all; the player could never have fired it regardless of circumstances.

The ROM site the earlier audit found is real and points the right way::

    8CD9  EE 62 65  INC $6562        ; the encounter/"active sequence" flag
    8CE1  CC FB 64  CPY $64FB        ; [C, D-090] is the victim the SELECTED slot?
    8CE8  B9 76 8C  LDA $8C76,Y      ; "ATTACK    " (10 chars)
    8CEB  99 4E 06  STA $064E,Y      ; ...into the SAME buffer every other
                                     ; SPECIAL row (REMVGRILLE, BlowLock.1,
                                     ; Enter Hypersleep, Fight Fire, ...) is
                                     ; built from
    8CF3  20 1A 8D  JSR begin_active_seq

`$064E` being the shared SPECIAL-row buffer is strong evidence ATTACK really
is a SPECIAL menu entry, installed the instant an Alien/crew encounter
begins — a **transient, per-encounter** latch (`$6562`/`$64BB`) this remake
does not track at that granularity.

**Action, following the FIGHT FIRE precedent already written into this same
file** ("the ROM's own menu-population rule for this entry is not traced;
the handler's gate is used as the visibility condition"): show "Attack"
exactly when `_resolve_attack_order` would not be `BLOCKED` — the Alien
alive, surfaced (not in a duct), and sharing the crew member's room. This is
a strict superset of the ROM's narrower mid-encounter window (every tick the
ROM would show it, this does too) and never offers an attack that would fail,
so it cannot invent a false success. The exact `$64BB`-gated window is left
`[?]` as a possible future tightening, not modelled.

Covered by three tests: the entry appears/disappears on the same conditions
as the resolver, and firing it end-to-end reaches `resolve_attack` and wounds
the Alien — not just that the menu row exists.

## D-133 — P5-8 was a rendering overflow, not a cursor-wrap bug

*2026-08-06. "The INDICATE menu does not wrap upward. Moving up from the top
should land on the bottom entry."*

Checked `MenuController.move` first, since that is where a wrap bug would
naturally live — and it was already correct: `self.cursor = (self.cursor +
delta) % len(sel)` wraps cleanly in Python regardless of sign, confirmed with
a direct call (`move(-1)` from cursor 0 on a 36-entry INDICATE list correctly
produced `cursor == 35`, the last selectable index).

The actual defect was one layer up, in `_draw_menu_panel`: it drew every
`entries()` row starting at screen row 1 with **no scroll window at all** —
`py = 8*s`, incrementing by one row per entry, unconditionally. The panel's
real vertical budget is only rows 1-17 (`_STATUS_ROW - 1` = 17 rows; row 18+
is the status band). INDICATE LOCATION's room list is 36 entries (34 rooms +
"INDICATE:" header + QUIT) — entry 35 draws at `py = 8*s + 35*8*s = 288*s`,
comfortably past the 200*s-tall field. The cursor moved correctly every time;
the row it moved to was simply never on screen once the list ran past 17
entries, which is indistinguishable from "moving up does nothing" to a player
who can only see what's drawn.

**No ROM-decoded scroll/paging scheme was found for this list** — the
`$769D`-`$76EC` block that looked promising (`$64E5` feeding `$7569`/`$758D`/
`$75B1`, the deck and marker-position tables via D-116/D-058) turned out to be
the deck-plan-pointer follow-along for a *chosen* room, not a text-list
scroll mechanism. Rather than invent one, `_PANEL_VISIBLE_ROWS` keeps the
highlighted row inside the panel's real 17-row budget — pinning the window to
the cursor's own position (clamped to the list's last full page) — which is
the minimum change that makes wrapping *visible*, without asserting anything
about how the original C64 game actually windowed a list this long.

**Lesson.** A player's precise diagnosis ("doesn't wrap") pointed at the wrong
layer. Reproducing through the actual rendered frame, not just the model
method the report named, is what separated a correct cursor from an invisible
one — the same discipline the standing correction from P3 already established,
applied here to a report that read like a pure logic bug and wasn't.

## D-134 — P5-7 was the SAME bug as P5-8, seen from the other end

*2026-08-06. "The status overlay covers room names on the INDICATE screen."*

Filed as its own item, but the cause was already fixed by D-133 minutes
earlier and just hadn't been checked. `_draw_status_line` always draws only
at row 18 and below (`_STATUS_ROW`) — it was never the aggressor. The overlap
was the *panel's* fault: before D-133's scroll window, INDICATE's 36-entry
room list drew unbounded from row 1, spilling past row 17 into the same rows
`_draw_status_line` uses — and since the status line is drawn **after** the
panel in `render()`, it partially painted over whatever room entries had
spilled into its territory. The player's framing ("status covers the room
list") described the visible symptom exactly backwards from the mechanism
(the room list invaded the status band's rows; the status band then
overwrote the intrusion), but the report itself was accurate.

Verified directly: sampling every panel row (1-17) for any of the four status
band colours finds none, and row 18 is confirmed to be a status colour.

**Action:** none beyond D-133 — this closes as a side effect. Added
`test_indicate_list_never_bleeds_into_the_status_band` so the two bands'
independence is pinned by its own test rather than left as an implication of
D-133's.

**Lesson.** When two play-report items name the same screen and land in the
same pass, check whether the earlier fix already closes the later one
before re-diagnosing from scratch.

## D-135 — P5-5 ANSWERED: it IS faithful — the geometry was already right

*2026-08-06. "The opening death screen hides more than the name."*

Checked the actual column arithmetic instead of assuming the report was
current. `_draw_opening` draws the 10-char garbled/real name field starting
at column 1 and the 29-char " HAS BEEN KILLED BY THE ALIEN" message starting
at column 9 — the exact real-machine geometry (`$06F9`/`$0701`, 8 screen
cells apart), matching D-081's own citation verbatim. With a 10-char name
field, that overlap is mathematically exactly the last two columns of the
name (columns 9 and 10) — the original's own garbled-name bug, not an
over-wide clear obscuring text that should stay visible.

`_blit_cells`/`_blit_codes` (the two draw helpers) were also checked directly:
neither clears a background wider than its own text unless `bg=` is passed,
and `_draw_opening` never passes it — so there is no mechanism by which
either write could reach beyond its own field width.

Likely explanation: the report predates whichever earlier fix already
implemented this geometry (the code's own docstring already cites the exact
same addresses and overlap the report describes, and reads as settled, not
in-progress).

**Action:** no behavioural change. Named the two magic column literals
(`_OPENING_NAME_COL = 1`, `_OPENING_MSG_COL = 9`) so the geometry is
self-documenting, and added
`test_the_overlap_with_the_message_is_exactly_two_columns`, which computes
the overlap from the real field widths rather than hard-coding "2" — so a
future change to either column or to `NAME_STRIDE` fails loudly instead of
silently drifting.

## D-136 — the NARCISSUS<->SHUTTLEBAY door was never invented; the AIRLOCK-2 one was

*2026-08-06. P5-2: "leaving the NARCISSUS puts the crew member on the wrong
deck with wrong movement options."*

Checked what `SURFACE_EXITS` (the game's own routing table, D-123/P-1) actually
says for the three rooms involved:

    SURFACE_EXITS[1]  (AIRLOCK 2) = (13,)             -- CORRIDOR 6 only
    SURFACE_EXITS[32] (SHUTTLEBAY) = (33, 34, 4, 16)   -- includes 34 = NARCISSUS
    SURFACE_EXITS[33] (SHTTLSTORE) = (32,)             -- SHUTTLEBAY only

Two findings, opposite of what the standing `[?]` note assumed:

1. **`m.add_door(slugs[1], SHUTTLEBAY)` — AIRLOCK 2 to SHUTTLEBAY — was an
   invented edge with no table support at all.** AIRLOCK 2's only real door is
   CORRIDOR 6.
2. **The SHUTTLEBAY<->NARCISSUS door was never missing.** `SURFACE_EXITS[32]`
   already lists room 34 directly; the generic door-building loop that runs
   later in `nostromo_ship()` wires it automatically once NARCISSUS exists as
   a room — no invention needed, and none was flagged as such before this
   pass (the invented-docking note in the module docstring was about the
   AIRLOCK-2 edge, but had drifted to also read as covering this one).

The actual defect was **NARCISSUS's deck and position**, both computed from
`airlock2.x/y/deck` "for rendering" (D-123's placement code) rather than from
its one real connection. AIRLOCK 2 sits on deck 0 (Upper); SHUTTLEBAY, the
room NARCISSUS actually docks to, sits on deck 2 (Lower). So a crew member
leaving NARCISSUS landed on a room tagged deck 0 with AIRLOCK 2's own
movement options bleeding through the invented edge — both halves of the
report in one root cause.

**Action:** NARCISSUS is now placed and decked relative to `m.rooms[SHUTTLEBAY]`
instead of `m.rooms["airlock_2"]`; the invented AIRLOCK-2 edge is removed
(along with the now-redundant explicit SHUTTLEBAY-SHTTLSTORE edge, itself
also already covered by `SURFACE_EXITS[32]`). The module's top-of-file
docstring and "still approximate" list, both stale since D-123, are corrected
to match. Covered by
`test_narcissus_connects_only_through_shuttlebay_not_airlock_2`; an existing
deck-split test (`test_deck_split_comes_from_the_screen_index_not_the_address_byte`)
needed updating since it had encoded the old (wrong) AIRLOCK-2 anchoring as an
assumption about NARCISSUS's deck.

**Lesson.** The standing `[?]` note itself was the trap: it said "how crew
reach the SHUTTLEBAY is `[?]`," which primed the reading of *this* connection
as the invented one, when the actual invented edge (AIRLOCK 2) was a
completely different pair the note didn't name. Checking the decoded table
directly settled which of the two nearby edges was real in under a minute;
trusting the note's framing would not have.

## D-137 — P5-1 ANSWERED: no NARCISSUS cockpit screen exists

*2026-08-06. "The NARCISSUS screen is not rendered; it should be a cockpit."*

Followed the todo item's own lead (`init_c $5DEB`, "third init call from
`entry_sys16384`") and it dead-ends. `init_c` is a generic sprite/palette
setup routine — clears the screen, sets sprite colours to green, copies
initial sprite coordinates, arms multicolour mode — called from **two**
unrelated places: program entry (`entry_sys16384`, `$4023`) and, separately,
right after the GAME OVER "PRESS ANY KEY" wait screen (`$646F`) on the way
back to `main_dispatch`. Nothing in it references room 34 or the Narcissus.
`$5DD1` itself decodes to nothing more than NARCISSUS's own 10-char NAME
record — `8E 01 12 03 09 13 13 15 13 A0` = "NARCISSUS " — the same kind of
per-room name pointer D-123 already found room 34 has, not a screen-data
pointer.

**Checked for a hidden screen blob more broadly.** `docs/re/UNDOCUMENTED.json`
— the full codemap's leftover unclassified addresses after recursive-descent
tracing — lists exactly **three** small routines project-wide (`sub_604f`,
`sub_7520`, `delay_routine`), none screen-sized, none referencing room 34.
There is no unaccounted-for 1000-byte block anywhere in the image that could
be a full-screen cockpit illustration.

**And NARCISSUS already has an ordinary per-room marker position.** The
game's own `$758D`/`$75B1` marker-position tables (D-058) are 35 entries, not
34 — they cover NARCISSUS too, at `(80, 40)`, exactly the same mechanism
every other room uses. There is no special-cased drawing path for it anywhere
in the classified code.

**Conclusion:** the original never had a NARCISSUS interior/cockpit view.
Boarding it is an ordinary MOVE order to an ordinary (if off-the-deck-plan)
room; LAUNCH NARCISSUS is the special that actually resolves the evacuation
win. The player's expectation of a cockpit screen is a reasonable guess about
what a modern remake *might* add, but it isn't in the source, and per
discipline this remains unimplemented rather than invented. No code change.

**Lesson.** A todo item's own stated lead can be wrong — `init_c` looked
promising because of its proximity to `$5DD1` in memory, but proximity in a
disassembly listing is not a call relationship. Checking the actual callers
settled it in minutes.

## D-138 — P7-VERIFY: P3-1 confirmed fixed through the real input pipeline

*2026-08-06. The last open item — verifying 13 previously-closed play-report
items through the actual app rather than the model, per the standing
correction from earlier in this play-report cycle.*

Gave the one item explicitly flagged as needing this ("re-diagnosed twice, so
its original closure is superseded") the full treatment: a new permanent test
(`test_every_living_crew_member_is_reachable_through_the_real_panel`) drives
`GameFlow` through the real NOTICE -> WELCOME -> INSTRUCTIONS -> GAME_SELECTION
boot chain to `PLAYING` (not a bare `Simulation()`), builds the actual
`PygameRenderer` and lets it construct its own `MenuController` exactly as
`draw()` does on the app's first play frame, and walks the CONTROL list with
`_handle_play_key(pygame.K_DOWN)` — the identical call the keyboard handler
makes. Across 6 seeds and two time points (tick 0 and tick 300, ~5 seconds of
play), every living crew member was reachable in every case. D-126's
android-lockout fix holds up under the methodology that was missing when P3-1
was first closed, not just headlessly.

The other 12 items (P3-2 through P3-6, P3-8 through P3-11, P3-13 through
P3-15) were not re-litigated from scratch: each already carries a
renderer-level regression added in the passes since it was filed — the
map-blanking test for P3-4, the animation frame-hash guards for P3-7/P3-9,
the font test for P3-13, the Jones-timing test for P3-15, and so on — which is
exactly the "reproduce through `run_app`/`PygameRenderer`" bar this item set.
None of that existing coverage flagged anything on this pass, and per the
item's own instruction, nothing was re-opened speculatively.

**This closes the last open item in `todo.md`.**

## D-139 — the attack composite now stops on deselect, not just on the next blip

*2026-08-06. Direct user request: "The alien attack animation and sound
should only occur when crew members in that room are selected. When the
cursor option goes back to selecting another crew member or option, the
animation and sound should stop and be replaced by the normal deck view."*

D-090 already gates the *trigger*: `$8CE1 CPY $64FB` fires the siren+animation
only when the wounded crew member is the one currently selected. But once
started, this remake's `_attacking` flag only got cleared by the next
movement/grille blip (`reset_attack_state`, D-096) — checked once per
simulation tick (~7.9 Hz) inside `play_sound_cues`. Switching the CONTROL
panel's selection is a per-frame input event (30 Hz, independent of the tick
clock), so a player who selected someone else mid-attack kept seeing the
blanked map, siren, and five-sprite composite for however long until the next
unrelated crew member happened to finish a move — sometimes many seconds.

**Action:** added `self._attacking_crew_id`, set to the selected crew id
whenever `play_sound_cues` lets an `ATTACK_ALERT` cue through (which, per
`sound.audible`, only happens when that crew member IS selected — so the
value is always correct by construction). `render()` — called every frame,
not just every tick — now checks at its very top: if `_attacking` is set and
the CONTROL panel's current selection no longer matches
`_attacking_crew_id`, end the sequence immediately via the extracted
`_stop_attack_composite()` (clears the flag, drops the victim, silences the
siren) before deciding whether to blank the map. The normal deck view resumes
on the very next frame.

Covered by `test_switching_selection_away_stops_the_attack_composite`, which
drives a real `Simulation` + `MenuController`, triggers the alert for the
selected victim, switches selection to someone else, calls `render()`, and
asserts the composite ended.

**Scope note:** this extends D-090's trigger-time gate to hold continuously,
which is not itself separately decoded (the ROM may or may not lock out
selection changes during an active `$64BB` sequence — that's undecoded). The
user's instruction is an explicit UX specification, not a claim about
original behaviour, so it is implemented as asked rather than treated as a
replica-fidelity question.

## D-140 — the GREEN VALLEY spiral was cut off by a frame-rate/tick-rate mismatch

*2026-08-06. "The opening Green Valley animation is extremely close, but cuts
off early."*

The spiral itself (`spiral_colours`, D-104) was never the problem — the
screen's own **timeout** was too short to let it finish. Two different clocks
were in play:

- `draw()` runs at the app's real **30 fps** (`run_app`'s `frame_hz` default),
  and the spiral animates `steps = 1 + (frame_count // _SPIRAL_RATE) %
  len(_SPIRAL_RINGS)` — 22 rings at 3 render frames each = **66 frames** for
  one complete pass, i.e. **2.2 seconds** of wall time.
- The screen's own timeout, `LOADING_MENU_TICKS`, is measured in **flow
  ticks** at `TICK_HZ` (~7.886/s, the ROM's measured main-loop rate) — a
  completely different clock, advanced only inside `Screen.PLAYING`/timed-card
  handling, not tied to the render frame rate at all.

At the old value (14 ticks ≈ 1.8 s), the screen transitioned to NOTICE after
roughly 53 render frames — enough for ring **18 of 22**, cutting the outward
sweep short right near the end. "Extremely close, but cuts off early" is an
exact description of that arithmetic.

**Action:** `LOADING_MENU_TICKS` raised from 14 to **22** (~2.8 s) — derived
from `66 frames / 30 fps * TICK_HZ ≈ 17.35` ticks, rounded up with a ~0.6 s
margin so the finished spiral and the "GREEN VALLEY / PUBLISHING" text are
visible for a beat rather than vanishing the instant the last ring lands. The
real BASIC's own post-spiral pause (`320 FORXX=1TO900:NEXTXX`) has no measured
duration and stays `[?]`; this change only guarantees the spiral's own
citable frame math fits inside the screen's lifetime.

Covered by `test_green_valley_spiral_completes_before_the_screen_times_out`,
which reproduces `run_app`'s actual dual-clock loop structure (draw every
frame, tick only every `1/TICK_HZ`) with a virtual clock, and asserts the
spiral reaches its final ring before the screen transitions away — the kind
of check that would have caught this the first time, since a per-tick or
per-frame test in isolation cannot see a mismatch between two different
clocks.

**Lesson.** A third clock-mismatch bug in as many weeks (D-124 was the frame
counter never advancing on non-play screens; D-133/D-134 was a scroll
window; this is a genuine two-clock race). Whenever a screen's *lifetime* is
timed independently of the *animation* running on it, check the actual
frame math against the actual timeout — they are almost never naturally in
sync unless someone derived one from the other.

## D-141 — D-140's fix overcorrected: the ~0.6s buffer was itself an invention

*2026-08-06. "The animation is too long. Make it the same length as the
original."*

D-140 fixed the spiral cutting off early by raising `LOADING_MENU_TICKS` from
14 to 22 — but 22 included a **hand-added ~0.6s margin** on top of the 18
ticks actually needed for the spiral to complete once ("so the finished
spiral is visible for a beat," a judgment call, not a citation). The player's
report is the direct consequence: real duration is now longer than
necessary.

**Correction:** tightened to **18 ticks (~2.28s)** — the minimum derivable
from this remake's own animation constants (`22 rings x _SPIRAL_RATE(3)
frames / 30fps * TICK_HZ ≈ 17.35`, rounded up) with no added buffer.

**Important limitation, stated plainly:** this is still not a verified match
to the original's real wall-clock duration. No live capture of this screen
exists — the VICE oracle was unavailable this pass — and two real
unknowns remain un-timed: BASIC V2's actual per-statement execution speed
(which determines how long the real spiral takes to draw, independent of
this remake's own 30fps/3-frames-per-ring choices) and the post-spiral pause
(`320 FORXX=1TO900:NEXTXX`). 18 ticks is the smallest value that doesn't
regress D-140's fix, not a measured figure. A live capture of the real
screen's duration would settle this properly; flagged `[?]` accordingly, and
worth revisiting once VICE access is available again.

## D-142 — ★ GREEN VALLEY's real duration is ~14s, not ~2-3s: measured live, both earlier guesses were far off

*2026-08-06. Settled by live measurement after D-140/D-141's two hand-guessed
values (2.2s, then 2.28s) both turned out wrong in the same direction.*

VICE came back online partway through. Wrote `tools/vice-mcp/measure_greenvalley.py`
— boots the real d64 fresh with WarpMode **off** (standing constraint), drives
past the ShareData NOTICE screen, then polls screen RAM to timestamp state
transitions. Measured timeline (seconds from notice-dismissed):

    ~39.09s  screen clears, spiral begins
    ~50.14s  "GREEN VALLEY"/"PUBLISHING" text appears -> spiral took ~11.0s
    ~53.20s  screen clears again (`600 PRINTCHR$(147)`, building WELCOME next)
    ~60.71s  "1 ALIEN / Q QUIT" fully rendered

So the spiral itself takes **~11.0s** to sweep all 22 rings once, and the
whole GREEN VALLEY screen (spiral + text + the `320 FORXX=1TO900:NEXTXX`
pause) runs **~14.1s** before the WELCOME menu appears. This independently
corroborates a rough hand-estimate made from C64 BASIC's known POKE-loop
execution speed (~1,800 total pokes across the spiral at ~150-200/s ≈ 9-12s) —
two very different methods landing in the same range is real corroboration,
not coincidence.

**Both D-140 (2.2s) and D-141 (2.28s) were derived entirely from this
remake's own animation constants** (`_SPIRAL_RATE` frames/ring x 22 rings /
30fps), never from the real machine — an invention masquerading as a
calculation, because the frame-rate math was real but the *rate itself*
(`_SPIRAL_RATE = 3`) was a guess with no citation. The player's second report
("too long... make it match the original") was answerable only by finally
measuring the original, which the first two passes had no way to do
(VICE was unavailable when D-140/D-141 were written).

**Action:**
* `_SPIRAL_RATE` raised from 3 to **15** (frames/ring) — `11.0s * 30fps / 22
  rings ≈ 15.06`, matching the measured spiral-only duration.
* `_draw_loading_menu` now **clamps** `steps` at `len(_SPIRAL_RINGS)` instead
  of wrapping via modulo — the real BASIC sweeps 22 rings exactly once
  (`FOR Q=11 TO 1 STEP -1` then `FOR Q=1 TO 11`, no repeat) and holds on the
  finished picture; the old modulo wrap would have started a visible second
  sweep partway through the now much-longer real lifetime.
* `LOADING_MENU_TICKS` raised from 18 to **111** (~14.1s) — `14.1s * TICK_HZ
  (~7.886) ≈ 111`, the first genuinely measured value this constant has had
  (D-140/D-141 were both `[?]`; this is `[C-live]`).

Covered by `test_spiral_holds_on_the_finished_picture_instead_of_looping`
(new) alongside the existing completion guard
(`test_green_valley_spiral_completes_before_the_screen_times_out`, D-140),
which still passes unchanged since it derives its expectations from the live
constants rather than hardcoded numbers.

**Lesson.** Two rounds of "fix the number" without a live oracle just moved
the number between two equally-unfounded guesses (D-140 too generous by
invented margin, D-141 tightened by removing that margin) — both wrong in
the same direction because neither ever touched the real machine. The
player's persistence ("still not right") was the correct signal that the
whole approach, not just the constant, needed revisiting.

## D-143 — ★ both front-end screens build up in stages: text grows from the centre, the border sweeps in

*2026-08-06. Direct player report, describing the boot sequence in detail:
the GREEN VALLEY spiral "spirals out... then spirals in... before the name
animates on"; the WELCOME screen's border "animate[s] on as blocks moving
from top left to right, then down each side vertically, then another row of
blocks from lower left to right," and "the text animates from the center out
pushing the characters out from the middle... done from top to bottom."*

Checked the BASIC source first, then confirmed live with two new capture
scripts (`capture_intro_animation.py`, `capture_welcome_buildup.py`,
WarpMode off throughout).

**1. The CENTER ROUTINE (`GOSUB390`/`GOSUB2000`) is a real growth animation,
used by every text line on both screens** — not the instant `_blit_center`/
`_blit_cells` calls this remake had::

    2030 FOR N=1 TO M/2
    2040   PRINT CHR$(19);LEFT$(CUR$,VT-1);
    2050   PRINT SPC(21-N)LEFT$(B$,N);RIGHT$(B$,N);
    2060 NEXT N

Each pass reprints `LEFT$(B$,N)+RIGHT$(B$,N)` at a start column that shifts
one cell left per iteration — since `SPC(21-N)` shrinks exactly as each side
grows, the midpoint between the two halves stays at a **fixed screen column**
for every N, so the text visibly grows outward from that point until N
reaches M/2, where the two halves reconstruct the whole string exactly.

Live capture caught this directly: "PUBLISHING" appeared as a lone "P" at
t=11.73s (into the GREEN VALLEY screen) before settling by t=11.98s; on the
WELCOME screen, "FACE THE POWER OF THE UNKNOWN" was caught as a lone "F",
"CHOOSE ONE OF THE ABOVE" as the garbled "CHOOSOVE", and "COPYRIGHT(C)1985
ALL RIGHTS RESERVED" as "COPYRIGHRESERVED" — genuine mid-growth frames.

**2. The WELCOME screen's lines appear strictly top-to-bottom, one completing
before the next starts** — `capture_welcome_buildup.py` caught rows
appearing in exactly this order: row 3, then 6, then 8, then 12/15, then 20,
then 21/23. This matches the BASIC's own sequencing: each `GOSUB390` call
runs to completion (a blocking subroutine call) before the next `PRINT`/
`GOSUB` statement executes.

**3. NOT every WELCOME line uses the CENTER ROUTINE.** The "1) ALIEN"/"Q
QUIT" item list (lines 670-690) prints via `PRINTTAB` — direct, instant —
never `GOSUB390`. Live capture corroborates this: both appeared fully formed
the first time they were ever seen, never caught mid-growth like every other
line was. Two of the growing lines (`610`/`630`, the box's top/bottom rule)
and one more (`660`, the row-9 underline) also go through `GOSUB390` and so
still cost real time before the lines after them start, even though this
remake draws those three as instant shapes rather than growing glyphs —
modelled as length-only placeholders in the sequencing so later real text
isn't paced too early.

**4. D-127's "the border never animates" was wrong, but not for the reason
D-127 got right.** D-127 correctly found `****MARQUIE****` has exactly one
caller and is never repainted — no repeating chase, which is still true. But
"drawn once" was wrongly read as "drawn instantly." MARQUIE is three POKE
loops (top row L-to-R, both side columns top-to-bottom together, bottom row
L-to-R, 130 cells total) and BASIC's interpreted POKE loops are slow enough
to see — D-142 measured the spiral at ~6ms/poke, and live capture confirmed
the WELCOME border visibly assembling over multiple frames, not popping in.

**Action:**
* `text_reveal_mask(text, n)` / `text_reveal_steps(text)` / `sequential_reveal_n`
  added — pure functions reproducing the growth algorithm and the
  complete-one-line-before-the-next sequencing, generalized to "blank the
  middle N characters" so they compose with the existing fixed-position blit
  helpers (which already skip spaces) with no changes to those helpers.
* `_welcome_border_reveal_step(row, col)` added, ordering the ring by
  MARQUIE's three-pass structure; `_welcome_border_colour` (the *final*
  colour of each cell, D-064) is untouched.
* `_draw_loading_menu` grows "GREEN VALLEY" then "PUBLISHING" in sequence
  after the spiral itself completes; `_draw_welcome` sweeps its border in
  over `_BORDER_REVEAL_RATE` and grows its real text lines in sequence,
  skipping "1)ALIEN"/"Q QUIT" (drawn instantly, matching `PRINTTAB`).
* A genuine bug caught by the new unit tests before it shipped:
  `text[-n:]` at `n == 0` is `text[0:]` in Python (`-0 == 0`) — the **whole
  string**, not empty. Every not-yet-started line would have rendered fully
  visible from frame one. Fixed with an explicit `n == 0` branch.
* `[?]` **the exact per-step timing is not nailed down.** `_TEXT_REVEAL_RATE`
  and `_BORDER_REVEAL_RATE` are derived estimates (scaled from the spiral's
  measured per-poke rate), not live-measured directly — the live captures
  bound total-line durations loosely (~1.5s upper bound for a 15-step line,
  ~0.25s for a 6-step line) but didn't resolve per-step timing precisely.
  Revisit with a dedicated high-frequency single-line capture if the pacing
  still looks off.

Covered by new tests: `test_text_reveal_mask_matches_the_center_routine_algorithm`
(+ odd-length case), `test_sequential_reveal_completes_one_line_before_the_next_starts`,
`test_welcome_lines_reveal_top_to_bottom_through_real_draw_calls`,
`test_welcome_menu_items_never_appear_partially_grown`; the D-142/D-127-era
tests (`test_spiral_holds_on_the_finished_picture_instead_of_looping`,
`test_welcome_ring_is_actually_painted`, `test_front_end_screens_actually_animate_through_draw`)
updated for the new, longer, genuinely-animated timelines.

**Lesson.** Two static-analysis passes (D-119, then D-127) both read
"MARQUIE has one caller, never repainted" and concluded "no animation" —
correct about the *loop*, wrong about the *instant*. A slow interpreted
language can make a single, non-repeating pass look exactly like a repeating
one to a player, and only checking real elapsed time (not just call-graph
shape) resolves the difference.

## D-144 — ★ RETRACTS D-137: the NARCISSUS cockpit is real, found via the ROM's own branch-not-taken

*2026-08-06. The user directly confirmed D-137 ("no cockpit exists") was wrong
— "I know that when the crew member goes from the shuttlebay to the
narcissus that it's a cockpit" — and supplied a live VICE screenshot
(`out/Cockpit.png`) plus a full play-session recording as evidence.*

D-137's search had looked for a *drawing routine* — some code that actively
paints a cockpit bitmap — and found none, because that was the wrong shape of
thing to look for. The real mechanism is a **branch not taken**:

**`menu_option_dispatch`** ($511C, called from `guard_alien_present`'s
selection-refresh path) builds the map view from the selected character's own
room via `$7569,Y` — the same per-room deck byte D-116/D-136 already use.
Rooms 0-33 read 0/1/2 and load one of the three deck templates
(`init_menu_ptr`/`init_ptr_menu2`/`init_ptr_menu3`, each a 30x18 grid copy).
**NARCISSUS (34) has no entry in that table at all** — the table only spans
indices 0-33 — so reading past its end lands on whatever byte follows in
memory (`$758B = 3`), and the dispatch chain's final `CMP #$02 / BEQ` falls
through to an **`else` branch that has never been exercised by any of this
pass's earlier reads**::

    5134  CMP #$02
    5136  BEQ $513E                ; ==2 -> lower deck
    5138  JSR setup_cursor_sprite  ; <- anything else (incl. NARCISSUS's `3`)
    513B  JMP $5155                ; skips $5141's marker-position code AND
                                    ; the deck-copy that only runs via
                                    ; init_menu_ptr/2/3

So for NARCISSUS: **no deck template loads at all**, and instead of
positioning the character marker, the ROM repurposes **sprite 0** —
`setup_cursor_sprite` ($9528) arms its multicolor bit, sets its own colour to
white (`$D027=1`), pointer `$07F8=$D1`, position (172,50).

**`$D1` is exactly the next sprite pointer after the title's 8 egg sprites**
(`$C9`-`$D0`, this project's own `_EGG_SPRITES`) — independently spotted by
the user from the sprite sheet itself ("the moon... is next sprite in
sequence after the alien egg sprites") and now confirmed from the opposite
direction, in the disassembly. Two unrelated methods landing on the same
byte is real corroboration.

A second, independent confirmation that room 34 is special-cased: `update_2`
($4F19), the per-tick marker heartbeat-colour updater, opens with
`LDA $7935,Y / CMP #$22 / BEQ $4F4B` — an immediate `RTS` for a character in
NARCISSUS, skipping the pulse entirely. Matches the reference capture: the
figure in the cockpit does not pulse.

**What is still not decoded**: the exact screen-code/colour-RAM content of
the cockpit background itself (the console pedestals, the window shape, the
floor). `menu_option_dispatch`'s branch proves *that* something else is
shown and rules out a deck-template being involved, but does not itself draw
a background — nothing in the traced call graph writes new screen data for
this case. The background implemented here is reconstructed from the
player's own live capture, not a pixel-for-pixel ROM decode, and is
documented as such in the code.

**Action:** `render()` now checks whether the selected crew member's room is
NARCISSUS and calls `_draw_narcissus_cockpit()` instead of `_draw_deck()`.
The cockpit draws: black wedges (space beyond the window), a light-grey sill,
a grey wall carrying two brown console pedestals, a dark-grey floor, the moon
(decoded from the real sprite pointer `$D1` via the same mechanism
`_title_egg_surface` already uses for the egg), and the standing figure using
the game's own existing character-marker glyph (`_CHAR_SPRITE`, D-053/D-058)
— not a new sprite, matching that the figure is real ROM art reused, not
invented. The status line and CONTROL panel needed no changes at all — the
reference capture confirms they already render correctly for this room
("move to: ShuttleBay" independently reconfirms D-136's finding that
SHUTTLEBAY is NARCISSUS's only real door).

Covered by three tests: the map area actually changes when the selected crew
member boards NARCISSUS, every pixel stays in the real C64 palette, and the
scene is static (no heartbeat pulse), matching `update_2`'s skip.

**P5-1 is reopened and closed correctly.** D-137 is retracted; its
conclusion ("no cockpit exists in the original") was reached by searching for
the wrong kind of code (an active drawer) instead of the right kind (a
gate that *stops* the normal drawer and does something else instead).

**Lesson.** This is the third time this general shape of bug has cost real
time this week (D-126 "who writes this cell", D-128/D-129 "who's the actual
caller", now this): the interesting fact was in a branch that the earlier
pass had read past without asking what happens when none of the checked
conditions hold. An exhaustive disassembly read is not the same as tracing
every branch's *else*.

## D-145 — five play-report fixes from the player's own recording + an archived capture

*2026-08-06. From a detailed play report plus a full real-time session
recording (`out/2026-08-06 20-44-41.mp4`) and a cockpit screenshot.*

**1. The heartbeat was never played at all.** `audio/sfx.py` renders it
(`render_pulse` over `HEARTBEAT_VOICE_SETUP`), `constants.heartbeat_divider`
maps composure to the ROM's own IRQ divider (`fear_alert $4E16`), and
`_HEARTBEAT_COLOURS` already drove the marker's matching *visual* pulse — but
**nothing in the renderer ever called `sfx.render("heartbeat")`**. The player
reported hearing no heartbeat; they were exactly right. Added
`_update_heartbeat`, looping the pulse under the play screen at the selected
character's own composure rate (one cached clip per distinct divider, since
the rate *is* the information), muted during an attack (the alert takes the
voices over) and stopped on leaving the play screen.

**2. The title/egg screen's border is BLACK, not blue.** Frame-by-frame in
the recording: the starfield runs straight out into the border. We were
using the play screen's blue (`_present()` default).

**3. The GAME SELECTION screen's border is GREEN**, matching its own green
field so the inset reads as one solid block. Also the default blue before.

**4. The opening death notice is BLACK-ON-GREEN, not white-on-black.**
`game_init_mode` clears `$0400-$06E8` to `$A0` but never touches colour RAM,
which `sub_screen_setup ($5FC3)` left at 5 (GREEN) — so the whole field reads
green with black `$D021` ink, exactly like the selection screen it follows.
Confirmed frame-by-frame (full-green screen, black text, black border).

**5. ★ The garbled name was overprinting the message.** `$5092` writes the
10-char name to `$06F9` (row 19 col 1); `$50A0` then writes the 29-char
message to `$0701` (col 9) — a real screen-RAM write that **overwrites the
name's last two cells**. Only 8 garbled characters ever survive. But
`_blit_cells` *skips spaces* (it draws no paper), so the message's own
leading space could not erase them the way the ROM's `STA` does, and we drew
all 10 codes — leaving two garbled glyphs sitting under "HAS". That is the
player's "too much of the corrupt name overlapping the words". Verified
against the archived live capture `tools/vice-mcp/opening_row19.json`:
`" +??E?%,? HAS BEEN KILLED BY THE ALIEN"` — exactly 8 corrupt characters,
one space, then a fully legible message. Fixed by truncating the name to the
`_OPENING_MSG_COL - _OPENING_NAME_COL` cells that actually survive.

**6. GET ITEM is ONE row that opens a submenu, not an inline item list.**
Every panel in the recording shows a single "Get item" row (e.g. "use: /
Incinerotr / Get item / Leave item / Special:"), never the room's contents
listed on the main panel. Ours enumerated every item inline, which both
mis-shaped the menu and leaked what was in the room before the player asked.
Added `MenuEntry.get_items` + `MenuController.getting_item` +
`get_item_entries`, following the existing INDICATE-submenu pattern; QUIT
inside it returns to the crew's own panel (not the CONTROL list), and taking
an item closes it.

Covered by new tests for the notice's colours, the message-not-overprinted
property (rendered with and without a name, message columns must be
identical), and four GET ITEM submenu behaviours.

## D-146 — the NARCISSUS cockpit background, decoded from the real screen

> **Disambiguation (D-146 is used twice — D-192).** This is the **2026-08-06** entry. The other is **2026-08-06**, "★ P3-15: the Jones run LOOPS; `$F0` is a stop line, not an end". Citations of `D-146` predate the collision being noticed, so **resolve them by subject, not by number.**

*2026-08-06. D-144 found the trigger; the player reported the result "doesn't
look even slightly correct".*

D-144 correctly established from the ROM *that* room 34 replaces the deck
plan (`menu_option_dispatch` falls through to `setup_cursor_sprite`, loading
no deck template) but explicitly could not establish the background art —
nothing in the traced call graph writes screen data for that branch. The
first implementation therefore hand-drew an approximation from the
screenshot, which was not close enough.

Replaced with a **decode of the real screen**: `out/Cockpit.png` (the
player's own VICE capture) sampled at 2x2 per character cell over the 30x18
map area — 60x36 samples — each quantised to the C64 palette. The five grey
plateaus in the capture map cleanly onto the C64's five greys (black, dark
grey, grey, light grey, white) plus brown, which is corroboration that the
sampling is reading real character cells rather than scaler noise. Stored as
`_COCKPIT_ROWS`, replayed as 4x4-pixel blocks.

This is **measured from the real machine but is a screen decode, not a ROM
decode** — documented as such in the code. The moon still comes from the
ROM's own sprite data at the ROM's own position (D-144), and coincides with
the moon baked into the decoded grid.

## D-146 — ★ P3-15: the Jones run LOOPS; `$F0` is a stop line, not an end

> **Disambiguation (D-146 is used twice — D-192).** This is the **2026-08-06** entry. The other is **2026-08-06**, "the NARCISSUS cockpit background, decoded from the real screen". Citations of `D-146` predate the collision being noticed, so **resolve them by subject, not by number.**

*2026-08-06. "Jones moves from left to right in a smooth looping animation."*

`update_3 ($4F52)` advances sprite 3 and steps its frame from one clock::

    4F5C  LDA $D006 / CLC / ADC #$04 / STA $D006   ; X += 4
    4F65  CMP #$F0 / BCC $4F7A                     ; below the line -> animate on
    4F69  LDA $64BA / BEQ $4F7A                    ; **no stop pending -> carry on**
    4F6E  LDA #$00 / STA $64BA / STA $D007 / STA $64BC   ; stop: blank the sprite

The earlier reading treated `CMP #$F0` as the end of the run. It is not: past
`$F0` the routine still checks `$64BA` — the **stop request** — and with none
pending it falls through to `$4F7A` and keeps going. The `ADC #$04` is an
ordinary 8-bit add, so X wraps `$FF -> $00` and the cat re-enters from the
left. That is the seamless loop the player describes.

**Who requests the stop (`set_flag_64ba $5011`, three callers):** selecting a
character (`$7732`), an attack starting (`$4FA2`), and map re-entry
(`$7083`). Even then the cat is not blanked mid-screen — it finishes the
current crossing and vanishes at the edge.

**And re-arming keeps it alive.** `maybe_clear_64ba ($4FF1)` is the starter,
but its *first* branch is `LDA $64BC / BNE` — already running? then just
clear the pending stop and return. `guard_6580 ($88CC)`'s scan re-calls it
every pass while Jones is in the selected crew member's room, so the loop is
continuously renewed exactly as long as the arming conditions hold.

**Action:** `pygame_app` now models `$64BA` (`_jones_stop`), wraps X 8-bit
instead of ending at `$F0`, and only ends the run when a stop is pending *and*
the edge is reached. Re-arming while running clears the pending stop. Covered
by `test_jones_run_loops_while_armed_and_finishes_the_crossing_on_stop`.

**Lesson.** Same shape as D-126/D-130/D-144: the earlier pass read the compare
and stopped there, without asking what the *next* branch does when the
compare succeeds. `BCC` then a second guard is a two-condition exit, not one.


## D-147 — ★ P5-1: the NARCISSUS cockpit, captured from the real machine

*2026-08-06. The user rejected the reconstruction: "isn't rendered according to
what the original disassembly shows... please find it."*

Every static search for a stored cockpit screen failed because **there is no
stored screen**. The dump proves why: across the whole 30x18 map area the
cockpit uses exactly **three glyphs** — `$A0` (all-1 bits: solid hull),
`$20` (all-0: the clear window), and `$EE`/`$EF` (the instrument dials) — with
the entire picture carried by **colour RAM** (greys 11/12/15 for the hull,
brown 9 for the two pilot chairs). It is procedure + colour, not a 540-byte
template, so `draw_deck_map_body`'s pointer never points at one and no PRG
search could ever have found it.

**How it was captured.** Automated selection input still doesn't register, so
the ROM's own selection routine was run in place: poke a crew member's room to
`$22`, set `$64FB` to their slot, then patch `main_loop`'s first `JSR`
(`$719E`) to a trampoline that calls `guard_alien_present ($7720)` and
**restores the original JSR operand before returning** — a one-shot, self-
healing hook that leaves the game running normally afterwards
(`tools/vice-mcp/capture_cockpit_real.py`). Screen RAM and colour RAM were then
dumped and saved in the project's standard oracle format:
`the live captures (not published)narcissus_0400.bin` / `narcissus_d800.bin`.

Two live corrections to D-144 fell out of the same dump:

* **`$D01B` is sprite-to-background PRIORITY, not multicolor.** The live read
  is `$D01C = 0`: the moon is a **hires white** sprite drawn *behind*
  foreground ink, which is why the hull occludes it and it shows only through
  the window's clear cells. D-144 had rendered it as multicolor.
* **The map area uses the deck maps' polarity, not the front end's.** Set bits
  are the foreground (`_rasterize_backdrop`'s `if on:`), so `$A0` is solid and
  `$20` is clear — the opposite of the cut-out model the front-end screens use
  (D-050). Getting this backwards first produced a black hull with grey
  speckles.

**Action:** `_draw_narcissus_cockpit` now replays the captured screen+colour
RAM through the game's own charset, with the moon sprite drawn between the
black field and the glyph ink. The quantised-screenshot grid from D-146's
first attempt is deleted. Covered by
`test_narcissus_cockpit_is_drawn_from_the_real_machine_capture`, which pins
the three-glyph vocabulary and the brown chairs.

**Lesson.** "The disassembly must contain the screen" was the wrong premise,
and it cost several failed searches — but the user was right that the
reconstruction was wrong. When a static search for stored data keeps failing,
consider that the data may be *generated*, and go get it from the machine.

## D-148 — P5-3: the siren cannot be verified against this oracle — VICE does not implement OSC3

*2026-08-06. "The Alien attack audio is still strange. Please find how this
worked in the original game code."*

**How it works in the ROM (fully decoded, no ambiguity).**
`begin_active_play ($4F90)` sets `$64BB` and configures three voices: voices
1 and 2 as gated **triangles** with sustain 15 / release 0 (`$D406`/`$D40D` =
`$F0`), and voice 3 as an **ungated free-running sawtooth at frequency `$0020`**
(`$D40E`=`$20`, `$D40F`=`$00`, `$D412`=`$20`). Voice 3 is never heard — it
exists purely as an LFO. Then `irq_handler` routes every IRQ through the
modulator while the flag is set::

    4D2F  LDA $64BB / BEQ $4D37 / JMP irq_alt_handler
    4E76  LDA $D41B / LSR A / STA $D401      ; v1 freq-hi = osc3 / 2
    4E7D  CLC / ADC #$40 / STA $D408         ; v2 freq-hi = that + $40

Freq `$0020` makes the 24-bit oscillator wrap in `2^24/32` clocks = **0.532 s**
(1.879 Hz), so on real 6581 hardware `$D41B` ramps 0->255 and the two voices
sweep together, a fixed `$40` apart — a rising siren repeating ~1.9x/second.
That is exactly what `audio/sfx.render_alert` reproduces, and the ROM byte
transcription is already pinned by existing tests.

**Why the oracle can't confirm it.** Sampled live with the siren genuinely
running (`$64BB` = 1, the modulator demonstrably executing — voice 1 read 0
and voice 2 read exactly `$4000`, i.e. `0 + $40<<8`), **`$D41B` reads 0 under
every condition tested**: frequency `$0020` and `$4000`, gate off and gate on,
sawtooth *and noise*. OSC3-with-noise is the C64's canonical random-number
source and physically cannot be constant zero on real hardware, so this is
conclusive: **this VICE build does not implement OSC3 reads.**

Consequences, stated plainly:

* **In this emulator the alert is a static two-tone**, not a sweep — voice 1
  pinned at frequency 0 (silent) and voice 2 at a steady ~962 Hz.
* **On real hardware the same ROM produces the rising siren**, which is what
  the remake renders. Voice 3 has no purpose *other* than being that LFO —
  setting up an ungated sawtooth and reading `$D41B` every IRQ is meaningless
  otherwise.

**No change made to `render_alert`.** Flattening our siren to match the
emulator would mean reproducing an emulator limitation rather than the
program, which is the exact failure mode this project's discipline exists to
prevent. Flagged here so the next pass doesn't re-run the same dead end.

**Also captured, for the record** (live, mid-alert): voices 1/2 carry
attack/decay `$28`/`$C0` — values `begin_active_play` never writes, so they
are leftovers from whatever last used those voices, not intent. The routine
sets only SR. `$D418` volume is 15, filter off.

**Open question for the player, not resolvable from code:** if "strange" is
relative to hearing the original *in VICE*, then ours differs because ours
sweeps and VICE's cannot — and ours is the hardware-faithful one. Settling it
needs either real hardware, a VICE build with a full SID engine (resid rather
than fastsid), or a recording of the original from real hardware.

## D-149 — ★ "Jones is here" is a real on-screen notice — and "GET JONES" is a real Special Option

*2026-08-06. "When Jones is in the room I think there is a notification
onscreen. Check the PRG."*

Both confirmed, from the PRG bytes and independently from a live capture.

**1. The notice.** `guard_6580 ($88CC)` — the routine that decides whether the
cat is on screen — copies a 22-byte string on the same path that arms the run::

    890C  LDY #$00
    890E  LDA $884A,Y / STA $07C0,Y      ; 22 bytes
    8917  BNE $890E
    8919  JSR maybe_clear_64ba           ; ...then arm the run

`$884A` decodes to **"Jones is here"** padded with `$A0`, and `$07C0` is
**row 24, column 0** — the bottom message line. The live capture reads colour
RAM **7 (yellow)** across that row. `$88D2` blanks the same 22 cells at the top
of every pass, so the notice is present exactly while the condition holds.

Crucially it sits *behind the identical four gates* as the animation
(`$88F9`-`$890A`: cat in the displayed room, a character selected, that
selection is a crew slot < 8, and they are on the surface) — the notice and
the cat's dash are **one event**, which is why `jones_run_armed` is reused
verbatim rather than re-deriving the condition.

**2. `GET JONES` is a real Special Option — retracting its removal.** Ten bytes
further on, the same path writes another string::

    891E  LDA $64FC / BEQ $8924 / RTS
    8924  LDA $8860,Y / STA $0676,Y      ; 10 bytes

`$8860` decodes to **"Get Jones "** and `$0676` is **row 15, column 30** — the
CONTROL panel's SPECIAL block (`$064E`, the slot ATTACK/REMVGRILLE use, is row
14 of the same column). The live capture shows it in place, directly above
"Launch / Narcissus". So the earlier judgement recorded in
`core/special_options.py` and `state.py` — *"the old CATCH_JONES special was an
invention and was removed; catching is via USE of the cat_box"* — **is wrong**:
the option is in the ROM, it is drawn dynamically by `guard_6580` rather than
coming from the static per-room specials table (`$5753`), which is why a search
of that table found nothing and concluded it was invented.

**Action:** the notice is implemented (`_draw_jones_notice`, row 24, yellow,
gated by `jones_run_armed`) and pinned by
`test_jones_here_notice_is_the_roms_own_string_row_and_gates`, which checks the
string against the PRG bytes and the row against `$07C0`'s arithmetic.

**`GET JONES` is NOT implemented yet** — filed rather than rushed. Its *handler*
has not been traced (what selecting it does, and how that relates to the
`cat_box` USE path R-17 currently models), and shipping a menu entry whose
action is guessed would be the exact failure this project guards against. See
todo P8-3.

**Lesson.** The same shape as D-144: an option absent from the static table was
declared invented, when it is written dynamically by the routine that owns that
game state. "Not in the table" is not "not in the game" — check who writes the
screen, not just who reads the table.

## D-150 — ★ the tracker: a recomputed latch, a fixed-rate pulse, and a real detection zone

*2026-08-06. "The tracker is detecting movement nearby and pinging, but the
pings are fast and the tracking continues if the crew member puts down the
tracker."*

Both symptoms are real, and tracing them settled the long-standing `[?]` on
the tracker's range as well. Three separate findings:

**1. The ping's rate is a fixed IRQ divider — the sound is not an event.**

    4DD7  DEC $64B8 / BPL $4DED
    4DDC  LDA $4D03 / STA $64B8      ; reload the divider
    4DE2  LDA #$10 / STA $D412       ; voice 3 gate OFF
    4DE7  LDA $64B6 / STA $D412      ; re-gate from the latch

`$4D03` = `$12` = **18 IRQ ticks**, i.e. 60/18 ~= 3.3 Hz, and this runs on
every IRQ. So while `$64B6` is armed the ping is a steady pulse train at a
fixed rate. (`sfx.TRACKER_DIVIDER` was already correct.) The remake instead
pushed a fresh one-shot `SoundCue` on **every** detection, so overlapping
clips stacked up — the "fast pings". Now the renderer loops one clip while
the latch is armed (`_update_tracker_ping`), exactly as it does the heartbeat.

**2. `$64B6` is a latch that is RECOMPUTED, which is why dropping it must
silence it.** `check_deferred_move` runs, back to back::

    72F9  JSR reset_attack_state     ; $8C82 clears $64B6
    72FC  JSR check_6562             ; ...and this re-arms it

`check_6562 ($8E32)` reads the two trackers' **item location bytes**
(`$82E9`/`$82EA` in the `$82E3` item-room array) and passes each to
`resolve_char_display_loc ($8D71)`, whose first test is `CMP #$A0 / BCC
false`: a location below `$A0` is a **room**, i.e. the item is lying on the
floor, and the scan stops there. Only `$A0 + slot` — carried by a character —
gets past it. So putting the tracker down silences the alarm on the very next
move pass. Our model never re-evaluated holding, which is exactly the
reported bug; `_scan_trackers` now recomputes the latch from scratch each
tick.

**3. The detection zone is decoded — it is NOT ship-wide.**
`resolve_char_display_loc` builds `$6565..$656A` = the holder's own room plus
that room's entry in **each of the five route tables** (`$7A3A`/`$7A5E`/
`$7A82`/`$7AA5`/`$7AC8` — the same `ALIEN_ROUTES` the Alien's movement and
`panic_dest` use). Then two different rules apply inside that zone:

* **`$8F31` (X = 0, the holder's own room):** reads a character only if they
  are **inside a duct** and alive — you can already see anyone standing next
  to you, so only something in the walls registers.
* **`$8F3E` (X = 1-5, neighbours):** reads a character on the **surface**,
  alive, whose room genuinely differs from the holder's.

The loop covers slots 0-7 and **slot 0 is the Alien**, so one scan handles
the creature and the crew with no special case. Jones is checked first and
separately (`$8DDC LDX #$01` -> `$8F0B`), starting at index **1** — the five
neighbours only, never the holder's own room — and gated on `$6580` (the cat
being loose).

This replaces `_use_tracker`'s explicit `[?]` placeholder ("models the
simplest ship-wide check rather than inventing a radius"), which made the
tracker read positive essentially always — the other half of "detecting
movement nearby" feeling wrong.

**Action:** `alien.tracker_zone` (the six rooms), `sim._tracker_detects` (the
two rules), `sim._scan_trackers` (the recomputed latch, replacing the
per-event cue), and `pygame_app._update_tracker_ping` (the looped pulse).
Four tests that pinned the old ship-wide/event model were rewritten to the
decoded rules, and two new ones added.

**Lesson.** "The pings are fast" and "it keeps tracking" sounded like two
bugs and were really one design mismatch: an *event* model where the ROM has
a *latch*. Modelling continuous hardware state as discrete events reliably
produces both symptoms — too many triggers, and no way to stop.

## D-151 — ★ the PCS keeps TWO composure values; the remake modelled one

*2026-08-06. "The crew seems to panic quickly. Can you check the PRG behaviour
and how the PCS system works in general?"*

The PCS is not one number per character. It is a **base** and a **derived
per-turn effective value**, and every gate in the game reads the derived one.
The remake only ever had the base, which is why the crew broke so easily.

**`$7D55,X` — the base.** Persistent, changed only by real events: a death
anywhere (`$47DC`/`$5A0D`, `DEC` over every slot, floored at 0), the Alien
wounding someone (`$4230`), hiding in a duct (`$729C`, `INC` — the vents are
reassuring), and crowding (`raise_crowd_fear $4CE8`, `INC`, skipping anyone
already at 0 and **capped at 10** by `CMP #$0A / BCS skip`).

**`$6571,Y` — the effective value, recomputed at the start of each character's
turn** by `init_char_turn ($4784)`::

    47A2  STA $4781                  ; modifier := 0
    47B3  LDA $7935,Y / STA $457F    ; the actor's own room
    47B9  LDX #$01                   ; scan the other slots...
    47BB  CPX $64B1 / BEQ next       ;   not self
    47C0  LDA $7935,X / CMP $457F    ;   same room only
    47C8  LDA $6501,X / BNE next     ;   ...and on the surface
    47F1  LDA $7D45,X / CMP #$02
    47F6  BCS $47FE
    47F8  DEC $4781                  ;   a COLLAPSED mate: modifier -1
    47FE  LDA $7D55,X / ADC $4781
    4805  SEC / SBC #$02 / STA $4781 ;   else modifier += (their base - 2)
    4832  LDA $7D55,Y / ADC $4781    ; effective := own base + modifier
    483F  BPL / LDA #$00             ; ...floored at 0
    4843  STA $6571,Y

So **company steadies you**: every co-located, surfaced crew member
contributes `their base − 2` — positive for anyone calmer than "uneasy",
negative for anyone worse — and a collapsed companion costs a flat 1. This is
the manual's *"knowing that others of the crew are on their way to help"*,
implemented. A character **inside a duct** skips the scan entirely (`$47A8`):
alone in the walls, there is nobody to draw on.

**Everything reads the derived value**, which is what made the omission bite
everywhere at once: `$5170` (the panic-wander gate), `$7757` (can this
character be selected at all), `$5459` (the android's victim choice), `$4E16`
(`fear_alert`, the heartbeat's rate) and `$7DC5` (`fear_band`, the MORALE
word) all index `$6571`, never `$7D55`.

**Measured effect** (8 seeds, FULL mode, commandable crew at 1200 ticks ≈ 2.5
min of play): grouped crew now reach effective composure in the 20s off a
base of 10, and the average commandable count is **5.1 of 7**. Before, a
crew member's steadiness was their own base alone, so a couple of bad events
dropped them under the panic threshold with nothing to hold them up.

**One deliberate simplification, disclosed.** In the ROM `$6571,Y` is a
*cached* value refreshed on that character's own turn, so a gate reading
another character's `$6571` sees whatever their last turn computed.
`Simulation.effective_composure` computes it live for whoever is asked. The
value is the same one the ROM would have cached; only its freshness differs,
and modelling the cache would mean reproducing turn-order staleness for no
behavioural gain.

**Action:** `Simulation.effective_composure` (the `$4784` derivation),
`constants.COMPANION_SUPPORT_PIVOT`/`COMPANION_SUPPORT_MIN_HEALTH`/
`COMPOSURE_MAX`, and the four gates rewired to it. `crew.fear` remains the
base. Three new tests; one android test corrected — it had been staged with
bystanders in the room and was silently testing the support term rather than
the gate it named.

**Lesson.** "Panics quickly" sounded like a tuning problem and was a missing
half of the model. When a value is *derived* in the ROM and *stored* in the
remake, every consumer inherits the error at once — and the symptom shows up
as difficulty, which is exactly the kind of thing one is tempted to fix by
adjusting a constant.

## D-152 — ★ the android audit: three real behaviour gaps, one from citing the wrong routine

*2026-08-06. "How does the android work in the game? Check the PRG and make
sure the remake uses the same behavior."*

Walked every `$64C3` (android slot) and `$64CC` (found-out flag) reference.
Most of the model was already right; three things were not.

**The complete picture, for the record.** The android is a hidden crew member
chosen at start from `$50EC`'s pool (`$5086`, re-rolled until it differs from
the opening victim; the SHORT scenario hard-codes ASH at `$6069`). Until found
out it **passes for crew** — `$5265`'s `LDA $64CC / BEQ $5272` sends it down
ordinary `dispatch_char_action` (D-126) — with one tell: it silently drops
your orders while sharing the Alien's room (`$5272-$5299`). It is found out by
`$52A4-$52DA`, which stores its own slot in `$64CC` and flashes `$D021`.
Thereafter it cannot enter hypersleep (`$593C`), does not count as in play for
the endgame scan (`$5B5F`/`$5B64`), survives the endgame mass kill (`$6130`),
and scores nothing toward the COMPETENCE RATING (`$61A5`).

**Gap 1 — the revealed android's turn was modelled from the wrong routine.**
`_apply_android_attack` cited `$5439`/`$5459`/`$5460`, but `$5439` is a
`sub_char_special` action-code-3 handler reached only from `$8754`. The
revealed android's actual turn is **`$52F1`**, and its victim scan
(`$5313-$5331`) differs on two gates that change who gets hurt:

* **`$5318 LDA $6501,Y / BNE skip`** — a victim **inside a duct** is skipped
  outright. We had no duct test at all, so the android could reach into the
  walls.
* **`$5324 LDA $7D55,Y / BEQ skip`** — the composure test reads the **BASE**
  cell and skips only on **exactly 0**. We were testing the *effective* value
  (D-151) against a threshold of 2, sparing anyone merely shaken. The `$6571`
  citation belongs to the other routine.

**Gap 2 — it never fled.** `$52FC-$5306`: if the android shares a room with
the **surfaced** Alien it goes straight to `char_wander` before the victim
scan is reached — it runs rather than attacking. (A ducted Alien is not an
encounter, so the scan proceeds.) `[?]` The second escape at `$5309`
(`LDA $6562`, the attack-sequence latch) is **not** separately modelled: this
simulation holds no such latch, and its commonest cause — the Alien being
present — is already covered by `$52FC`. Narrow gap, disclosed rather than
papered over.

**Gap 3 — an unrevealed android blocked the launch.** `$5BD3-$5BD8`: the
"is anyone left behind?" scan passes over the android entirely while `$64CC`
is clear. So you can evacuate with an undiscovered android still aboard the
Nostromo — which is rather the point of not knowing which of them it is. Once
revealed it counts like anyone else. We required every living crew member
aboard, full stop.

**Already correct, verified against their sites:** the selection pool and
victim exclusion, the pass-for-crew routing, the reveal conditions, the
silent order-drop, the hypersleep refusal, `_counts_as_in_play`'s
revealed-android rule (`$5B5F`/`$5B64`, including its own `$7D55` base-
composure test), the endgame kill exemption, and the competence-rating
exclusion.

**Action:** `_apply_android_attack` rewritten against `$52F1` with the duct
gate, the base-composure-`== 0` gate and the flee-from-Alien escape;
`_launch_narcissus` given the `$5BD8` exemption. Four tests replaced or added.
One of the replaced tests had cited `$5459` and asserted composure 1 was
spared — it was pinning the wrong routine's gate.

**Lesson.** D-126 already found that `$5439` is a special-action handler
rather than the android's turn, but the *docstring* kept citing it and the
*gates* were never re-derived from `$52F1`. Correcting a routine's role in
prose is not the same as re-reading the routine that actually runs.

## D-153 — ★ Jones: catching him is a ROLL, the NET works too, and the LAUNCH needs the container aboard

*2026-08-06. "How does Jones work in the game? I think he's required for
launching the narcissus?"*

Yes — and the requirement is stricter than the remake had it. Four findings.

**1. Catching him is a per-character random roll, not automatic.**
`$8787`::

    8791  LDY $64FB / LDA $883C,Y / STA $6518   ; per-character threshold
    879A  LDA $829A / CMP #$10 / BNE $87C9      ; holding the NET?
    87A1  DEC $6518 (x4)                        ;   -> four better odds
    87AD  JSR rng / CMP $6518 / BCS success     ; succeed on roll >= threshold
    87C9  CMP #$11 / BEQ ...                    ; else the CAT BOX
    87B6/87D7  rename the item "Jones:Net"/"Jones:Box"
    87EE  LDA #$00 / STA $6580                  ; he is no longer loose

The threshold table at `$883C` decodes to **(–, 14, 14, 13, 13, 13, 15, 14)**
for Dallas…Brett, and `rng`'s scramble table (`$887E`) is a flat 0-15 ramp.
So with the box alone a catch is a **1-to-3 in 16** attempt — Parker is worst
at 1/16, Ripley/Ash/Lambert best at 3/16 — and a miss simply costs the
attempt. The remake caught him automatically, every time.

**2. The NET catches him too, and much better.** `$879A CMP #$10` accepts item
instance 16 (the net) and the four `DEC`s make it **5-to-7 in 16**. The remake
accepted only the cat box and routed a net USE straight to the attack path, so
the net could never catch anything. It still entangles the Alien through the
ordinary attack route when the cat is not what is in front of you (D-033).

**3. "GO GET JONES" is about the CONTAINER's location, not a flag.**
`check_mother_refuses ($5B1F)` finds whichever item was renamed to hold him
(matching `#$8A`, the reverse 'J' the rename starts with) and reads *that
item's* location byte::

    5B3B  LDA $82E3,Y / CMP #$22 / BEQ allow   ; the box is in the NARCISSUS
    5B42  CMP #$80 / BCC refuse                ; ...or lying in some room
    5B46  AND #$07 / TAY / LDA $7935,Y
    5B4C  CMP #$22 / BNE refuse                ; ...or its holder is aboard

So catching him is only half the job: **somebody has to carry the net or box
into the shuttle**. The remake accepted a bare `jones_caught`, which let you
launch with the cat still sitting on the Nostromo — the direct answer to the
player's question. Now tracked as `state.jones_container_id`.

**4. He refuses to walk into the Alien's room, and his timer is 40.**
`sub_88ab_prechar ($88AB)`, called once per main-loop pass by `char_pump`::

    88B1  DEC $657F / BNE rts        ; act only when the countdown wraps
    88B6  LDA #$28 / STA $657F       ; reload = 40 passes
    88BB  LDA $657E / CMP $7935      ; the candidate room vs THE ALIEN's
    88C1  BEQ rts                    ;   -> abandon the move

The cadence retires `JONES_WALK_TICKS`, which D-122 had already shown was a
frame divider and was carried as an explicit placeholder. And the Alien
avoidance was never modelled at all — the cat has more sense than the crew.
`[?]` How `$657E` (the candidate room) is *chosen* is still undecoded; the
uniform pick among door neighbours remains a placeholder, as D-036 flagged.

**Action:** `_catch_jones` (the roll, both catchers, the container),
`_resolve_use_order` (route a catcher at Jones's room to the catch before the
attack fallback), `_advance_jones` (cadence + Alien avoidance),
`_launch_narcissus` (the container-aboard gate), plus
`constants.JONES_CATCH_THRESHOLD`/`JONES_CATCHERS`/`JONES_MOVE_TICKS` and
`state.jones_container_id`. Four tests rewritten or added.

**Lesson.** "Required for launching" was true but under-specified in the
remake, and the gap was invisible because a boolean *looks* like it captures
the rule. Whenever the ROM tests a **location byte** and the remake stores a
**flag**, the flag has quietly dropped a requirement.

## D-154 — the spanner is a plain +1 melee weapon; the item catalogue verified whole

*2026-08-06. "How does the spanner work? Check the PRG and make sure the
remake matches. What are all the available items?"*

**Verdict: the spanner is already correct in the remake — no change made.**

`resolve_attack ($4940)` dispatches on the item's **instance index**, not its
type — a detail worth restating, because it is why the two spanners behave
identically to the prods and incinerators despite being a different type::

    4943  CMP #$FF / BEQ abort          ; no object
    4947  CMP #$11 / BEQ abort          ; instance 17 = CAT BOX -> never attacks
    4976  CMP #$06 / BCC $497A          ; 0-5   (prods, incinerators) -> +1
    498D  CMP #$12 / BCS $497A          ; >=18  (**the two SPANNERS**) -> +1
    4991  CMP #$10 / BNE ...            ; 16 = NET -> no wound; +$50 to the
                                        ;   Alien's timer, then consumed
    49B1  CMP #$08 / BCS $49C8          ; 6-7  = TRACKER -> smashed, +1
    49C8  CMP #$0C / BCS $49EB          ; 8-11 = EXTINGUISHER -> charge path
    49F6  ADC #$05                      ; 12   = HARPOON -> +5, guaranteed
    49EF  JMP $4AB1                     ; 13-15= LASER -> charge path, then +1

`$498D` is the whole of the spanner's behaviour: `INC $7D45`, one point of
Alien damage, no charges, not consumed. It has **no other role** — in
particular it is *not* needed to remove a grille: the crew's grille handler
(`$8757`) checks only that a grille is present (`$875E LDA $8676,Y`), clears
it, and raises the burst flag, with no item test anywhere on the path.

The Alien dies at **50** accumulated damage (`CMP #$32`, re-checked on every
wound path), so a spanner is 50 hits and a harpoon is 10 — which is the point
of the spread.

**The full catalogue, read from `$82CF` (types) and `$82E3` (locations)** —
20 instances of 9 spawned types (THERMLANCE exists as a type with no
instance), all matching `ITEM_CATALOG` exactly:

| # | item | count | starts in |
|---|------|-------|-----------|
| 0-2 | ELCTRC PRD | 3 | INFIRMARY, INF STORES, LAB STORES |
| 3-5 | INCINERATR | 3 | COMMDCENTR x2, ENGINEERNG |
| 6-7 | TRACKER | 2 | COMMDCENTR, ENGINEERNG |
| 8-11 | FIRE EXTNG | 4 | ENGINE 1/2/3, MESS |
| 12 | HARPN GUN | 1 | SHUTTLEBAY |
| 13-15 | LASER PIST | 3 | ARMOURY (all three) |
| 16 | NET | 1 | LAB STORES |
| 17 | CAT BOX | 1 | LABORATORY |
| 18-19 | SPANNER | 2 | STORES 2, ENG STORES |

Charges come from `$4B37` (with its pristine backup at `$4B47`): 3 for each
extinguisher, 1 for the harpoon, 10 for each laser, 0 for everything else —
matching `CONSUMABLE_USES`. Destroy-on-use is the net (`$49AB`) and the
tracker (`$49C2`), matching `ITEM_DESTROYED_ON_ATTACK`.

**Nothing to fix.** Recorded so the next audit of this area can start from a
verified baseline rather than re-deriving it.

## D-155 — ★ the airlocks: a healthy Alien ignores them, and the vent never stops

*2026-08-06. "How do the airlocks work? What does BLOWLOCK 1/2 do to the crew,
Jones, or the Alien?"*

**The controls.** Both locks are plain **toggles** — `$5922`/`$5931
EOR #$01` on `$5751` (AIRLOCK 1) and `$5752` (AIRLOCK 2) — so BLOWLOCK and
SEALLOCK are one option flipping one flag, chosen by the menu row
(`$5918 LDA $64E5 / CMP #$10`). Both are operated remotely from CORRIDOR 6
(D-037), never from inside the lock.

**The vent (`blowlock_vent $5A6A`) does four things**, and the remake had one
of them right:

| target | rule | we had |
|---|---|---|
| items in the room | blown to space (`$5A6C`) | untouched |
| crew **on the surface** there | health 0, blown out, **carried items go too** (`$5A8D`/`$5A9E`) | killed, items kept |
| crew **in a duct** there | **SAFE** (`$5A80 LDA $6501,Y / BNE skip`) | killed |
| the Alien | only if surfaced **and damage >= 6**, then a roll | killed outright, always |
| **Jones** | **untouched** — `$657D` is never referenced | untouched ✓ |

**The Alien rule is the big correction.** `$5ACC LDA $7D45 / CMP #$06 / BCC
rts` means a **healthy Alien simply ignores an open airlock**. Only once it
has taken 6+ damage can the vent reach it, and even then `alien_maybe_hide
($5ADD)` rolls a flat 0-15: `rng >= damage` and the creature **survives**,
taking one more point of damage and a long action delay (`$5AF6 LDA #$78`);
otherwise it is blown out and the game is won. So ejection probability is
`damage/16`, certain only from damage 16. The remake killed it the instant it
stood in an open lock, which made ALIEN_AIRLOCKED a one-click win instead of
a finisher for a creature you have already fought down.

**And the vent is continuous.** `apply_blowlock ($5B04)` is called from
`check_deferred_move ($7305)` on **every move pass**, not once at the moment
of opening. An open lock keeps venting: walk into it ten moves later and it
still kills you. We vented once and left the flag set as decoration.

**Action:** `_vent_open_airlocks` (all four effects, with the duct exemptions
and the Alien's damage gate + roll), called from `advance` each tick as well
as on opening; `constants.ALIEN_VENT_MIN_DAMAGE`/`_ROLL_SIDES`/
`_SURVIVE_DAMAGE`. One test rewritten (it had asserted the one-click win) and
five added.

**Lesson.** Third audit running where the remake had collapsed a *conditional,
repeated* ROM behaviour into a *single unconditional* event — the tracker
latch (D-150), the Jones catch roll (D-153), and now the vent. The tell is the
same each time: the ROM re-runs a check from a loop, and the remake does it
once at the moment of the player's click.

## D-156 — ★ Jones's destination decoded: the Alien's route tables, his own bands

*2026-08-06. "How does Jones pick his next room? Check the PRG."*

This closes the `[?]` D-036 opened and D-153 carried forward. `$657E` (the
candidate room) has exactly one writer, `$8981`, inside a picker at `$8971`::

    8971  JSR rng / AND #$07 / TAX   ; a 0-7 roll (rng's table is 0-15)
    8977  LDY $657D                  ; ...indexed by his CURRENT room
    897A  CPX #$02 / BCC -> $7A3A    ; rolls 0-1
    8985  CPX #$04 / BCC -> $7A5E    ; rolls 2-3
    898F  CPX #$05 / BCC -> $7A82    ; roll  4
    8999  CPX #$06 / BCC -> $7AA5    ; roll  5
    89A3           else -> $7AC8     ; rolls 6-7
    8981  STA $657E

So he walks the **same five route tables as the Alien** (`ALIEN_ROUTES`) —
not a uniform pick among door neighbours, which is what the remake had as an
admitted placeholder. His band mapping is his own: **(0,0,1,1,2,3,4,4)** over
a 0-7 roll. That makes **three different mappings over one set of tables** —
the Alien's own (a 0-15 roll through `ROUTE_BAND_BOUNDS`), the panic walk's
(`_panic_route_band`), and now Jones's — which is presumably why the tables
are shared: one topology, three temperaments.

**And the pick runs one move ahead.** `sub_88ab_prechar` compares the
*already-chosen* `$657E` against the Alien's room and only then commits it
(`$88C3 STA $657D`), picking the next candidate afterwards (`$88C9 JMP
$8971`). So the veto (D-153) applies at **commit** time, not selection: a cat
already heading somewhere the creature then walks into simply stalls for a
pass, re-testing the same candidate, rather than re-rolling. Modelled with
`_jones_next`.

**Action:** `alien.jones_dest` + `_JONES_ROUTE_BANDS` + `JONES_ROLL_SIDES`;
`_advance_jones` rewritten to the pick-ahead/veto-at-commit shape. Two tests
(the band mapping against the tables directly, and the stall behaviour on a
real Nostromo map). The D-036 placeholder notes in `constants.py` and
`sim.py` are retired — nothing about Jones's movement is `[?]` any more.

**Lesson.** The earlier passes concluded "Jones must be driven by code this
project hasn't located" because slot 8 sits outside the `Y=1..7` character
loop — true, but the code was one `JMP` away from a routine already being
read (`$88C9`). A dead end that says "driven from somewhere else" is worth
re-testing by following the exits of the routine that *does* handle it.

---

## D-157 — the `$51F4` `[?]` was a fall-through: a broken crew member ALWAYS wanders

**Date:** 2026-08-07 · **Source:** `resolve_char_move ($5156)`, static

D-130 modelled `resolve_char_move`'s composure branches but left one open,
recording `$51F4` as "a different, undecoded outcome" and letting such a crew
member keep obeying orders. Re-read at the byte level, `$51F4` is not a branch
target that leads anywhere else — it is three stores followed by nothing:

    51F4  A9 00 / 99 0C 65   STA $650C,Y   ; drop the pending order
    51F9  A9 28 / 99 EE 64   STA $64EE,Y   ; re-arm the 40-tick action timer
    51FE  A9 01 / 99 C4 64   STA $64C4,Y   ; mark the move pending
    5203  char_wander:       A9 00 ...     ; <- fall-through, no JMP

`$5200` is a three-byte `STA abs,Y` ending at `$5202`, and `char_wander` starts
at `$5203`. So **composure 0 wanders unconditionally**; the co-located-Alien
case simply clears the order and resets the cadence on the way in. The remake
had it exactly backwards — the one situation where a broken crew member is
most certain to bolt (a surfaced Alien in the room with them) was the only
situation in which they still took orders.

**Action:** `_apply_panic_wander`'s `composure == FEAR_MIN` branch no longer
`continue`s on `alien_surfaced_here`. Regression test
`test_broken_crew_bolt_even_from_a_surfaced_alien_in_the_room` covers both the
surfaced and ducted Alien.

**Lesson.** A `[?]` that says "this branch goes somewhere undecoded" deserves
one check that it is a branch at all. Disassembly listings make fall-through
invisible: the next label looks like a new routine even when control simply
runs into it.

---

## D-158 — ★ the sweep: `guard_alien_present` is a CONTINUOUS gate, and row 24 has two notices

**Date:** 2026-08-07 · **Source:** `main_loop ($719D)` / `check_deferred_move
($72D2)` per-pass audit, static

Prompted by the observation that D-150 (the tracker latch), D-153 (the Jones
catch) and D-155 (the airlock vent) were all **the same defect**: a ROM
behaviour that is conditional and re-evaluated from a loop, modelled in the
remake as a single unconditional event at the moment the player clicks. This
is the deliberate sweep for that pattern across every routine the ROM calls
per pass. Two more instances, both in the same routine family.

### The per-pass census (now complete)

    main_loop $719D:   pause_check · sub_7453 · char_pump ·
                       mainloop_sub_5684 · mainloop_sub_5a26
    $72E9 tail:        guard_alien_present · guard_6580 · reset_attack_state ·
                       check_6562 · find_crew_at_target_loc ·
                       restore_stowed_char · apply_blowlock

Cleared without change: `sub_7453` (input/cursor only), `mainloop_sub_5684`
(the 256-pass fire burn, already modelled), `mainloop_sub_5a26` (the
auto-destruct countdown, already per-tick), `find_crew_at_target_loc` (per-pass
`init_char_turn` re-derivation — moot, the remake computes
`effective_composure` live rather than caching `$6571`).

### Instance 1 — the selection gate never stops applying

`guard_alien_present ($7720)` is called from `$72EE` on **every move pass**,
and reads `$64FB`, the *currently selected* character:

    773B  LDA $64D1,Y / BNE bounce   ; in hypersleep
    7740  CPY $64CC   / BEQ bounce   ; the revealed android
    7745  LDA $7D45,Y / CMP #$02 / BCC bounce   ; health below 2
    7757  LDA $6571,Y / BNE ok       ; composure 0 ...
    7768  JSR find_colocated_crew / CPX #$08 / BEQ bounce  ; ...and alone
    774F  LDA #$00 / STA $64FB       ; the bounce: DESELECT

The remake ran `can_be_commanded` only inside `MenuController.fire()` — at the
click. So a crew member who fell asleep, collapsed to 1 health, broke while
alone, or was unmasked as the android **stayed commandable for the rest of the
game**: the panel kept their order menu open and kept accepting orders. In the
original the selection evaporates under you and the panel snaps back to the
crew list, which is a large part of how the game communicates that someone is
gone. Note `$7720` writes `$64FB` and never `$64E5`, so the cursor row is
preserved (the same detail P3-1 turned on).

### Instance 2 — row 24's notice has an untaken branch too

`guard_6580 ($88CC)` blanks row 24 every pass (`$88D2`, 22 spaces) and then
re-derives it. The remake drew only the branch it had read:

    88F4  LDA $657D / CMP $64F7 / BNE $8932  ; Jones in the DISPLAYED room?
    88FE  LDY $64FB / BEQ $8932              ;  ...and a character selected
    8903  CPY #$08  / BCS $8932              ;  ...that is a crew slot
    8907  LDA $6501,Y / BNE $8932            ;  ...on the surface
    890C  -> "JONES IS HERE" ($884A) + the GET JONES option ($8860 -> $0676)

    8932  LDY #$01                           ; otherwise, scan the crew:
    8934  LDA $7935,Y / CMP $657D / BEQ ...  ;   anyone in JONES's room
    8944  LDA $6501,Y / BNE next             ;   who is on the surface
    8949  LDA $7D45,Y / CMP #$02 / BCC next  ;   and not collapsed
    8950  -> "<NAME>" ($A65E + Y*10) + " SEES JONES " ($8844)

So the cat is reported **whatever room you are watching** — you are told *who*
can see him instead of being offered the catch. The remake showed nothing at
all in that case, which is why Jones felt like he only existed when you
happened to be looking at him.

**Action:** `MenuController.entries()` re-derives the selection gate every
panel build (the frame-cadence analogue of the per-pass call) and drops a
selection that no longer qualifies, restoring `_root_cursor` rather than
zeroing it. `render.pygame_app.jones_notice_text` replaces the direct
`jones_run_armed` call in `_draw_jones_notice` and implements both branches.
Tests: `test_the_selection_gate_is_re_evaluated_every_frame` (all four of
`$7720`'s conditions, each ending a selection already in progress),
`test_a_still_qualifying_selection_survives_the_re_check`, and
`test_jones_notice_has_both_rom_branches`. Three existing frame-identity
guards were staged with Jones in an occupied room and had to be re-staged onto
empty ones — they were asserting the incomplete model.

**Still open.** The **GET JONES** panel option (`$8860` -> `$0676`, written and
blanked by this same per-pass block, and gated on `$64FC == 0`) remains
unimplemented; the remake reaches the catch roll through USE of a held net or
box instead, which shares `$8787`'s handler but not its menu presentation.
Tracked as P8-3.

**Lesson.** The pattern has a reliable tell: ask of any routine **"what does
the untaken branch do?"** and **"who calls this, and how often?"**. Both of
this entry's instances were sitting in routines already read and cited — what
was missed was not the routine but its *cadence* and its *else*. A remake
naturally expresses decisions at the moment of input, because that is where
the player's intent arrives; the ROM expresses them in a loop, because that is
where its frame budget lives. Every place those two shapes meet is a candidate.

---

## D-159 — ★ the self-reference rejection is `$64B4`-gated; that is how the Alien lingers

**Date:** 2026-08-07 · **Source:** `alien_ai_dispatch ($89A9)` / `alien_choose_move ($8A36)` / `blowlock_vent ($5A6A)`, static

P2-19 made "refuse a destination equal to my own room" an unconditional
re-roll. The ROM only does it on a **hunting** turn:

    89F2  LDA #$3C / STA $64EE   ; 60-pass move timer
    89F7  LDX $64B4
    89FA  BEQ $8A11              ; NOT hunting -> RTS, destination ACCEPTED
    89FF  CPX $64E6 / BNE $8A07
    8A04  JMP $89C4              ; hunting AND dest == here -> re-roll
    8A07  LDX #$00 / STX $64B4   ; hunting and moving -> spend the latch
    8A0C  LDA #$14 / STA $64EE   ;   and move FAST (20 passes)

`alien_choose_move` — the grille-**open** dispatcher — never reads `$64B4` at
all, so there a self-reference is always accepted. The route tables encode "no
exit this way" as a self-reference, and accepting one is simply **standing
still for 60 passes**. Re-rolling it away meant our Alien never lingered
anywhere, which quietly broke the BLOWLOCK win route (below). No room's whole
route row self-refers, so the ROM's loop always terminates — the guard was not
needed to prevent a hang.

### Why it matters: how the Alien reaches an airlock

**CORRIDOR 6 is the only room with a surface route into either lock**, and it
is also where the BLOWLOCK controls are — the map funnels the creature past
the weapon. Its grille reads 0 (`$8676[13]`, the only room that starts open),
so it uses `alien_choose_move`'s narrow bands:

    rolls 0-2 -> mess · 3-4 -> AIRLOCK 1 · 5-6 -> computer
    rolls 7-8 -> stores_3 · 9-11 -> AIRLOCK 2 · 12-15 -> the ducts

**5/16 per move.** Once inside, three of the lock's five entries self-refer,
so on the grille-intact bands: 6/16 back to corridor 6, **9/16 stay**, 1/16
duct — about 2.3 turns of dwell at 60 passes each. That is the window.

`blowlock_vent` then gates hard: a **ducted** Alien is safe (`$5ABF`), it must
be in *that* lock (`$5AC4`), and below **6 damage it is untouched entirely**
(`$5ACC CMP #$06`). Past that `alien_maybe_hide ($5ADD)` rolls — `roll <
damage` sends it off the map (`$7935 = $BD`, the win); otherwise it survives
with +1 damage, a 120-pass stun, forced to the surface, and **thrown to
`rng >> 2`** — room 0-3, i.e. airlock 1, airlock 2, armoury or cargopod 1. Half
of those drop it straight back into an open lock.

### Other facts pinned in passing

* `rng ($888F)` = `$A2` + `$6519` + `$651A`, `AND #$0F`, through `$887E` —
  which is the **identity table 0..15**, so the roll really is a flat 0-15.
* **`$8676` is the per-room grille state, not a static room class**, and the
  Alien writes it: `$8B84` clears the byte when it bursts a grille from the
  duct side. Intact => `$89C4`'s three-wide bands and a 1/16 duct chance;
  open => `alien_choose_move`'s narrow bands and 4/16.
* Duct travel uses four *different* tables (`$80F5/$8117/$8139/$815B`) and its
  timer comes from `$6581` = **`$46` = 70**, a constant seeded by the `$6598`
  init copy — never modified at runtime.
* `$64B4` is set at `$4CB3` when `rng < $4781` (a threat accumulator growing by
  `damage/4` per pass) and is what suppresses `guard_6562`'s room corrosion for
  that turn as well as buying the 20-pass move.
* Room `$22` (which `$89D0` refuses to duct out of) is the **NARCISSUS**, not
  the shuttlebay; `_SHUTTLEBAY_SLUG` was correctly indexed but misnamed.

**Action:** `_begin_action` accepts a self-referential destination and holds
position on an ordinary turn; `_move_timer` became `_roll_hunt`, called once at
the top so a single latch governs both the re-roll and the duration, and zeroed
at `$8A09` when spent. `_SHUTTLEBAY_SLUG` -> `_NARCISSUS_SLUG`. Tests:
`test_an_unhunting_alien_stays_put_on_a_self_referencing_route` (single roll
plus a 200-seed dwell rate), and the existing pursuit-timer test re-staged with
an intact grille, since the grille-open dispatcher can never hunt.

`[?]` The vent survivor's `rng >> 2` relocation, 120-pass stun and forced
surfacing are still not modelled — `_vent_open_airlocks` only adds the damage
point.

---

## D-160 — ★ "GET JONES" is a real panel row, and grabbing at him spooks him

**Date:** 2026-08-07 · **Source:** `guard_6580 ($88CC)` / `route_command ($8437)` / `$8784`, static — closes P8-3

D-153 found the catch roll at `$8787` and, having no menu route to it, hung it
off **USE** of a held net or cat box. That was wrong in both directions.

`route_command ($8437)` dispatches the panel cursor `$64E5`: `>= $10` goes to
the Special Options handler, `== $0E` elsewhere, and **everything else falls
into `$8784`**. That looks reckless until you read `$8784`'s first act:

    8784  LDA $0676 / CMP #$A0
    8789  BNE $878C
    878B  RTS                    ; the slot is blank -> the option isn't offered

The guard *is* the option's presence. And `$0676` = `$0400 + 15*40 + 30` —
**panel row 15, column 30** — is exactly the slot `guard_6580` writes the
10-char label `$8860` = `"GET JONES "` into (`$8924`) and blanks again
(`$88E8`), every pass, behind the same four gates as the "JONES IS HERE"
notice. So it is a contextual panel option, and USE of a net or a box goes
where every other item's USE goes, `resolve_attack ($4940)`.

**And the grab spooks him.** Before any roll:

    878C  LDA #$01 / STA $657F   ; Jones's move counter -> 1

`$657F` is the 40-pass cadence D-153 decoded (`$88B6 LDA #$28`). Slamming it to
1 means Jones **steps on the very next pass whether or not you catch him**. A
missed grab does not merely cost the attempt — the cat bolts and has to be
found again. Note the option is offered even to a crew member holding neither
catcher; `$879A`/`$87C9`'s `$829A` test then makes the grab a no-op. Offering
it empty-handed is faithful.

**Action:** `OrderType.GET_JONES`; `menu._get_jones_offered` (the four
`guard_6580` gates) adds the row to `crew_entries`; `_apply_order` routes it to
the existing `_catch_jones`, which now sets `self._jones_timer = 1` up front.
The D-153 USE shortcut for net **and** cat box is deleted. Tests:
`test_get_jones_is_a_contextual_panel_row`,
`test_grabbing_at_jones_spooks_him_whether_or_not_it_lands`; the two D-153 roll
tests re-issued as `GET_JONES`.

`[?]` `$891E LDA $64FC / BEQ $8924` also guards the write; `$64FC` is untraced
and not modelled.

---

## D-161 — the front end is BASIC, and "Q" quits to an advert screen and cold-resets

**Date:** 2026-08-07 · **Source:** `MENU.prg` / `MENU1.prg` / `MENUA.prg` / `EXITO.prg`, static

None of the pre-game screens live in `ALIEN.prg` at all. The boot chain:

* **`MENU.prg`** — not BASIC; loads at **`$032C`**, so it overwrites a KERNAL
  vector *and* plants **`$0334` (820) = `$FF`**, the "first time through" flag.
  Code at `$0338` blanks the screen, sets text colour 14, `PLOT`s to row 12 /
  col 14, prints the 12 bytes at `$03F4` **backwards** — `"LOADING MENU"` —
  then `SETNAM "MENUA"` / `LOAD` / `JMP $CE4E`.
* **`MENUA.prg`** — machine code at **`$CD70`**, the resident disk-error and NMI
  helper (MENU1 line 815 points the NMI at `$CDF5`, which is why RESTORE does
  not break out). Its two screens are the "CHECK DISK DRIVE" and "MAKE SURE THE
  MASTER DISKETTE IS IN THE DRIVE" prompts.
* **`MENU1.prg`** — the BASIC front end. `PEEK(820)` gates the once-only part:
  line 480 shows the ShareData back-up notice only while it is non-zero, and
  line **191** returns out of the spiral for the same reason, line 192 clearing
  it. So the spiral and the notice appear **once per pass**; a disk error
  bouncing back to line 470 skips straight to the menu.

Screen order, with the routine that draws each: **LOADING MENU** (`MENU.prg`) ->
back-up **NOTICE** + "PRESS ANY KEY TO CONTINUE" (480-565, wait at 580) -> the
**SPIRAL** (`GOSUB 150`: fill the screen with reverse spaces, then colour-RAM
rings `Q=11..1` outward and `Q=1..11` inward, then "GREEN VALLEY" /
"PUBLISHING" through the centre-out routine at 390) -> the **MARQUEE** border
(`GOSUB 330`: top row 1024-1063, then both sides down, then the bottom row
1984-2023) -> the framed **menu** (610-720, every line through 390) ->
**instructions Y/N** (10000) -> optional printer prompt + 8 instruction pages ->
**"LOADING...." / "PLUG JOYSTICK INTO PORT TWO"** (810-811) -> `LOAD"ALIEN",8,1`
+ `CLR:SYS16384` typed into the keyboard buffer. `SYS 16384` = **`$4000`**.

**The menu has exactly one numbered option.** Line 895 `DATA1,15` sets `NM=1`,
so the list is `1 ALIEN` (line 680) and line **690** prints the fixed extra row
`"{18}Q{146} QUIT"`. The recollection of a second "2 QUIR" entry is that Q row.

**What Q does** (740): `IF C$=CHR$(81) THEN CC=0 : P$(0)="EXIT*"`. `CC=0` skips
the instructions prompt entirely (770 `IFCC<>0THENGOSUB10000`) and skips the
"PLUG JOYSTICK" line (811), then 830 types `LOAD"EXIT*",8` + `CLR:RUN`.
**`EXITO.prg`** draws the same marquee border, prints "THESE AND MANY MORE /
FINE PROGRAMS MAY BE FOUND / AT YOUR NEARBY" centre-out, then a two-word
block-graphic retailer logo (rows 12-15 and 18-21), waits `FOR XX=1 TO 3000`,
and ends at line 4000 with **`SYS 64738` — a cold reset of the machine.** So Q
is not "back to the menu": it is an advert and then a reboot.

**Action:** the remake's `Screen` sequence already matches (LOADING_MENU ->
NOTICE -> WELCOME -> INSTRUCTIONS -> INSTRUCTION_PAGES -> LOADING_PLAY -> TITLE
...), and `pygame_app`'s `spiral_colours` / `_SPIRAL_RINGS` are ported from
lines 150-320 with the ring order and start colour intact. Two gaps recorded,
not invented: (1) the **EXIT\*** advert screen has no counterpart — `Q` is
routed to `InputEvent.QUIT` and simply closes the window; its block-graphic
logo needs a live capture before it can be drawn faithfully. (2) `PEEK(820)`'s
once-only semantics for the notice and spiral are not modelled, which only
shows if the remake ever returns to the front end mid-pass.

---

## D-162 — ★ the clock: a busy-wait main loop, no real time anywhere, and a 10-wrap auto-destruct

**Date:** 2026-08-07 · **Source:** `delay_routine ($755E)` / `main_loop ($719D)` / `char_pump ($7226)` / `compute_action_delay ($4042)` / `irq_raster_split ($4D58)`, static + the D-041 live cycle measurement

### There is no clock

The game has **no real-time clock, no jiffy counter, and no frame lock**. The
only unit of time is **one pass of `main_loop`**, and the pass is paced by a
pure busy-wait:

    755E  LDY #$AA          ; 170
    7560  LDX #$00
    7562  INX
    7563  BNE $7562         ; inner: 1279 cycles
    7565  INY
    7566  BNE $7560         ; outer: $100-$AA = 86 iterations
    7568  RTS

86 x ~1286 = **~110,600 cycles**, or ~112 ms on PAL. It is called once per
pass from `sub_7453`, between `read_input` and the menu-cursor update.

That squares with the live measurement recorded in `constants.py`
(`MAIN_LOOP_HZ = 7.886`, from 158 passes / 19,739,184 emulated cycles):
~124,900 cycles per pass, of which the busy-wait is **~89%**. The remaining
~14,300 cycles are the pass's actual work. Static and live corroborate.

**Consequences.** (1) The rate is *free-running*, not frame-locked — a busy
pass is a slower pass, which is why the live trials spread 7.83-8.30 Hz.
(2) It is **CPU-clock bound**, so an NTSC machine (1.0227 MHz vs PAL's 0.9852)
runs the whole game **~3.8% faster**. (3) `WarpMode` therefore does not merely
speed up the emulator, it changes nothing about the ratio — which is why every
timer measured in passes is portable, and why the standing rule to keep warp
off matters only for wall-clock captures.

### What the IRQ does (and does not do)

`init_a_raster_irq ($4DB8)` points `$0314` at `$4D08` and enables a raster IRQ
at line `$61`; `irq_raster_split ($4D58)` re-arms alternately at `$61` and
`$FA`, rewriting `$D009`/`$D00B` (sprite 4/5 Y) and `$07FC`/`$07FD` (their
pointers) each time. It is a **two-way sprite multiplexer**, doubling sprites
4 and 5 — plus `$4DD7`, which counts `$64B8` down from `$4D03` and pulses
`$D412` (voice 3 control) — the heartbeat/tracker gate.

So the IRQ runs at 100/120 Hz and drives **presentation only**. It never
touches a game timer. Every simulation timer lives in the main loop.

### The timer hierarchy — everything is counted in passes

`char_pump ($7216)` and `check_deferred_move ($72D2)` are **co-routines
forming one loop**: `$7226` reads `$64EE,Y`, decrements it, and
`check_deferred_move` does `INY / CPY #$08 / JMP $7226`. So all seven
characters have their action timer decremented **once per pass**, and a
character resolves on the pass its timer hits exactly 0.

| timer | value | passes | ~seconds |
|---|---|---|---|
| crew move base (`$7B69`) | `#$40` | 64 + terms | 8.1+ |
| Alien surface move (`$89F2`/`$8A4A`) | `#$3C` | 60 | 7.6 |
| Alien hunting move (`$8A0C`) | `#$14` | 20 | 2.5 |
| Alien duct travel (`$6581`) | `$46` | 70 | 8.9 |
| duct enter / grille burst (`$89E0`/`$8B8C`) | `#$28` | 40 | 5.1 |
| Jones (`$88B6`) | `#$28` | 40 | 5.1 |
| vent survivor stun (`$5AF6`) | `#$78` | 120 | 15.2 |
| fire spread (`$5684 INC $64CE / BNE`) | wrap | 256 | 32.5 |
| auto-destruct unit (`$657C`) | `#$FF` | 255 | 32.3 |
| auto-destruct total | 10 wraps | **2550** | **323 (5m23s)** |

### `compute_action_delay ($4042)` is a per-character speed stat

It **adds** two table terms to whatever base the caller already stored in
`$64EE,Y`:

    4045  LDA $4032,Y      ; per-SLOT term
    404C  LDA $7D45,Y / TAY ; the character's HEALTH
    4050  LDA $402B,Y      ; per-HEALTH term
    405D  LDA $64EE,Y / ADC ... / STA $64EE,Y

`$4032` = `[0, 7, 5, 0, 7, 3, 10, 5]` by slot — so, against the `$A65E`
roster: **DALLAS +7 · KANE +5 · RIPLEY +0 · ASH +7 · LAMBERT +3 · PARKER +10 ·
BRETT +5**. Ripley is flatly the quickest character in the game and Parker the
slowest, by ~13% on every action. This is a real, previously unremarked
personality stat.

`$402B` = `[0, 0, 48, 16, 0, 0, 0, 0]` by health — **+48 passes at health 2,
+16 at health 3, nothing at 4+**. A badly wounded crew member is not slightly
slower, they are nearly **twice** as slow (64 -> 112+). Health 0/1 read 0 but
cannot be commanded anyway.

Called from three sites: `$48FC` (ATTACK), `$7B6E` (USE), `$8460` (GET/LEAVE).

### The bug this turned up

`AUTO_DESTRUCT_TICKS` was `9 * 255`. `$657B` is **read before it is
decremented**, and the blast is the wrap that finds it *already* zero:

    5A3E  LDA $657B / BNE $5A46
    5A43  JMP hull_breach          ; fires when $657B is ALREADY 0
    5A66  DEC $657B                ; ...otherwise warn, then decrement

Arming spends 9 wraps walking the display 9 -> 0 and a **tenth** to detonate:
**10 x 255 = 2550 passes**. The remake blew the ship a whole countdown unit
(~32 s) early.

**Action:** `AUTO_DESTRUCT_TICKS = (AUTO_DESTRUCT_MINUTES + 1) *
AUTO_DESTRUCT_SUBTICKS`; `auto_destruct_minutes_left` returns
`ceil(t/255) - 1` so it still reproduces `$657B` exactly (2550 -> 9, 255 -> 0)
and the `>= 5` override gate and `>= 6` message split keep their meaning. Test
`test_auto_destruct_runs_ten_sub_counter_wraps`; the two drift guards updated.

### Also worth recording

There is **no global time limit**. The manual's "7,500 units of oxygen"
(instructions page 4, `MENU1` line 11860) is not implemented anywhere — D-062
already removed it as an invention, and this pass confirms no counter of that
kind exists. The only clock that can end a game is the player's own
auto-destruct.

---

## D-163 — ★ five PV items closed against the PRG; `$5753` is the special-option table

**Date:** 2026-08-07 · **Source:** `fear_band ($7DC5)` / `guard_target_alive ($56B4)` / the specials dispatcher `$5839` / `select_outcome ($60A9)` / `alien_maybe_hide ($5ADD)`, static

First working pass through the PV register. Five closed, three of them with
behaviour changes.

### PV-07 — the morale banding is decoded, and it was reading the wrong cell

The 5-way slicing was recorded as a guess. It is not:

    7DCB  LDA $6571,Y          ; the EFFECTIVE composure
    7DCE  CMP #$05 / BCC $7DD7
    7DD2  LDA #$00             ; >= 5 -> index 0
    7DDA  LDA #$04 / SEC / SBC $7946   ; else index = 4 - composure
    7DE0  JSR index_x10 / ... $7D13,Y -> $0767 (9 chars)

So the bands are exactly **>=4 · 3 · 2 · 1 · 0**, the words are five 10-byte
records at `$7D13` (CONFIDENT/STABLE/UNEASY/SHAKEN/BROKEN), and a sixth record
would land on `$7D45` — the health array — which proves the table is exactly
five long. `$0767` is **row 21, col 31**, inside the CONTROL panel. Our
formula was already byte-correct.

**The bug it exposed:** `$7DCB` reads **`$6571`**, the *derived* cell, not the
raw `$7D55`. `CrewMember.morale` reads the base value, so the panel word never
included the companion-support term (D-151) — a shaky crew member standing with
a steady colleague reads CONFIDENT on the real machine and read SHAKEN here,
and the word never changed when the colleague walked out. Since the same
derived value drives the panic gate the word exists to warn you about, the
display was actively misleading.

**Action:** `crew.morale_word(composure)` extracted as the shared formula;
`Simulation.morale_for(crew)` feeds it `effective_composure`; the renderer's
status line uses that. `CrewMember.morale` stays as the documented raw-cell
reading for tests and Simulation-less callers.

### PV-04 / PV-17 — `$5753` is the per-room SPECIAL-OPTION code table

Recorded as two separate unknowns ("hypersleep's population rule is not
traced", "FIGHT FIRE clears `$5753,X` and `$64D0`, consumers untraced"). They
are the same table, and it is the master list for the whole SPECIAL block:

    56B7  LDA $6501,Y / BNE rts     ; in a DUCT -> draw nothing
    56C1  LDA $5753,Y / BEQ rts     ; this room has no special
    56C6  STA $64D0                 ; cache WHICH option is selected
    5839  LDA $64D0 ... CMP #$01/#$02/#$03/#$04/#$05, else -> $5889

    $5753: commdcentr=1 · corridor_6=2 · cryo_vault=3 · narcissus=5
           (code 4 = noop, no room; code 6 written dynamically by
            damage_room_b into the engine rooms -> falls through to
            $5889 = FIGHT FIRE)

So `$64D0` is simply *which option is selected*, and clearing `$5753,X` on a
successful FIGHT FIRE means "this room stops offering it" — which the remake
already expresses by dropping the alarm. Nothing further to model there. And
the hypersleep room gate we already had **is** the ROM's own rule, not a
stand-in: code 3 appears on exactly one room.

**Two real gates fell out, both previously unmodelled.**

1. **`$56B7` — no `$5753`-derived special while inside a DUCT.** The drawing
   routine RTSes immediately for a ducted character, so SCUTTLE / BLOWLOCK /
   HYPERSLEEP / LAUNCH / FIGHT FIRE all disappear. (REMVGRILLE and ATTACK come
   from a different buffer, `$064E`, and are deliberately left outside this.)
2. **`$583F` — the dispatcher refuses on composure 0 or health < 2**, *before*
   branching on the code. Crucially the composure test has **no companion
   escape**, unlike `guard_alien_present ($7757/$7768)`. So an accompanied but
   broken crew member stays selectable and takes ordinary orders yet **cannot
   work a single Special Option**. That asymmetry is now modelled. Note the
   refusal is in the handler, not the draw — the row is still on the panel and
   pressing it does nothing, the same shape as GET JONES (D-160) and the vent.

### PV-16 — surviving an airlock vent throws the Alien

Decoded in D-159, implemented here:

    5AEE  JSR rng / LSR / LSR / STA $64E6  ; dest = roll >> 2 -> rooms 0-3
    5AF6  LDA #$78 / STA $64EE             ; 120-pass stun
    5AFB  LDA #$00 / STA $6501             ; forced to the SURFACE
    5B00  INC $7D45                        ; +1 damage

Rooms 0-3 are AIRLOCK 1, AIRLOCK 2, the ARMOURY and CARGOPOD 1 — **two of the
four are locks**, which is why blowing one repeatedly is a real tactic rather
than a single squandered chance. The remake added only the damage point and
left the creature standing in the lock, so a survived vent changed nothing
observable. `ALIEN_VENT_STUN_TICKS = 0x78` added.

### PV-22 — the scoring note was a misreading, and is withdrawn

It claimed "the `$64CF == 0` gate means the damage bonus is added on the *lost*
ending and skipped otherwise, which reads counter-intuitively." Re-tracing
`select_outcome ($60A9)`, the damage test at `$60D8` (`LDA $7D45 / CMP #$32` —
the **Alien's** damage, slot 0) is **not gated on `$64CF` at all**; it runs on
every ending. `$64CF` is consulted separately at `$60AE` and `$60F9`, and it is
not "auto-destruct armed" — it is the **result flag**, written by both
`set_result_win ($58E5)` and `clear_result_flag ($5DC8)`, which is why its zero
branch is `draw_ending_lost`. The counter-intuitive reading was an artefact of
collapsing two independent branches. Moot for behaviour (the remake has no
Competence Rating, D-034) but the wrong note is removed so nobody re-derives
from it.

**Ratchet:** placeholder budget 62 -> **59**.

**Lesson.** Three of these five were not "unknown" at all — they were
*mislabelled*. `$5753` had been read as a fire flag because the only writer
anyone had traced was `damage_room_b`; `$64CF` had been read as the
auto-destruct flag because that is the first writer you meet. A cell named
after the first routine that touches it will keep its wrong name until someone
enumerates **every** reader — which is the same technique that cracked D-158.

---

## D-164 — ★ fires, end to end: a damage alarm in an engine room, and the critical stage that makes it unfightable

**Date:** 2026-08-07 · **Source:** `damage_room ($5581)` / `damage_room_b ($5587)` / `$5658` / `mainloop_sub_5684` / `$5889` / the `$54A3` + `$5753` tables, static

### There is no separate "fire" system

A fire is not its own mechanic. It is what a **structural damage alarm in one
of the three engine rooms** is called. Everything runs through one routine:

    5581  damage_room:  LDA $6501 / BEQ damage_room_b / RTS   ; Alien in a duct -> ignore
    558C  LDA $653F,X / CMP #$04 / BCC rts        ; damage < 4  -> nothing at all
    5594  CMP #$0F / BCC $559E                    ; 4..14 -> stage 1
    5598  STX $5580 / JMP $5658                   ; >= 15 -> CRITICAL
    559E  LDA $651C,X / BNE rts                   ; stage 1 latches only from 0
    55A6  INC $651C,X                             ; the alarm
    55A9  CPX #$11 / BCC $55C1                    ; rooms 17..19 only:
    55AD  CPX #$14 / BCS $55C1
    55B1  LDA #$06 / STA $5753,X                  ;   -> FIGHT FIRE on the panel
    55BB  JSR guard_target_alive                  ;   -> redraw so it appears NOW
    55C1  LDA $54A3,X / BEQ rts / draw_damage_warning

    5658  CMP #$14 / BEQ hull_breach              ; exactly 20 -> the ship vents
    565F  LDA $651C,X / CMP #$02 / BEQ rts
    5667  LDA #$02 / STA $651C,X                  ; stage 2 + the long warning

### Where the damage comes from

Only two sources, and **the player causes most of it**:

* `guard_6562 ($8ED0 INC $653F,X)` — the Alien corrodes whatever room it is
  standing in, once per turn, while surfaced and not hunting.
* **Weapon acid**, two magnitudes with their own pre-add breach checks:
  `$4A87` (`CMP #$05` -> breach, else **ADC #$0F**, +15) and `$4AE7`
  (`CMP #$0E` -> breach, else **ADC #$06**, +6).

So a fire is a second-order consequence of *fighting the Alien in
engineering*. You cannot start one anywhere else, and the +15 spill will take
a clean room from 0 straight past the alarm threshold in a single hit.

### The burn

`mainloop_sub_5684` — `INC $64CE / BNE rts`, so **once per 256 passes
(~32 s)** — walks X = `$11`..`$13` and, for any whose alarm is lit,
`INC $653F,X` + `JSR damage_room_b`. From ignition at 4 to the breach at 20 is
16 increments: **a ~8m40s fuse** if nobody puts it out.

### Three states, not two — and the sting

`$651C,X` is **0 / 1 / 2**, not a boolean. The remake only had 0 and 1. The
consequence is sharper than the extra banner suggests: **`$55B1` — the write
that puts FIGHT FIRE on the panel — is only reachable on the 4..14 branch.**
Past 15, `damage_room_b` jumps to `$5658` and never gets there. Since
`$5889` clears `$5753,X` when you extinguish, an engine room that has already
been fought once and then burned back past 15 **can never be fought again**;
it is left to run to the breach. Extinguishing a badly damaged engine room is
a one-shot.

Also confirmed: FIGHT FIRE never touches `$653F` (D-044 stands) — the
structural damage is permanent and only the alarm is silenced, so the fire
returns the moment anything damages that room again while it is still under 15.

### Two errors in the malfunction table

Re-dumping `$54A3` against the PRG turned up:

* **Room 34 (NARCISSUS) was missing** from `ROOM_MALFUNCTION_TYPE` — it really
  does carry type 6, "NARCISSUS STATUS RED". The old comment asserted "types
  6-8 belong to no room", which is true only of 7 and 8 (the auto-destruct's
  two "MINS" strings).
* Three trailing comments named the wrong rooms: 17/18/19 are **ENGINE 1/2/3**
  (not "other list"), and 25 is **LIFE SUPPORT** (not the laboratory, which is
  23). The indices were right, so behaviour was unaffected — but a wrong name
  in a comment is how the next reader gets misled.

The test that should have caught the omission asserted a hardcoded literal
identical to the constant, so it agreed with the bug. Rewritten to decode
`$54A3` out of `ALIEN.prg` directly.

**Action:** `ROOM_ALARM_CRITICAL_THRESHOLD = 15` / `ROOM_ALARM_STAGE_CRITICAL =
2`; `add_room_damage` grew the critical branch and passes `arm_fire=False`
there; the FIGHT FIRE menu row now gates on `room_fire` (the `$5753` flag)
rather than `room_alarm`, which is what makes the one-shot rule real;
`ROOM_MALFUNCTION_TYPE[34] = 6`. Tests:
`test_a_critical_engine_room_never_gets_fight_fire_back`, the malfunction table
test rewritten against the PRG, and the FIGHT-FIRE menu test re-staged to drive
real damage instead of poking `room_alarm`.

**Lesson (again).** `$651C` was modelled as a boolean because the first branch
anyone read wrote 1 to it. The same shape as D-163's `$5753` and `$64CF`: a
cell's *range* is as easy to get wrong as its meaning, and the tell is the
same — find every writer, not just the first.

---

## D-165 — three more PV items: a false alarm, the `$6562` latch, and a cursor delay we invented

**Date:** 2026-08-07 · **Source:** memory-layout arithmetic on `$651C`/`$653F` / `$6562`'s four readers / `read_input ($71B0)` + `sub_7453`, static

### PV-13 — "the damage tables are only 20 entries" was wrong

The note claimed `$653F`/`$651C` cover only room indices 0-`$13`, and wondered
whether the remake letting every room take damage was "harmlessly permissive."
The layout settles it without reading a single instruction:

    $653F - $651C = 35   ; the alarm table is exactly one entry per room
    $6562 - $653F = 35   ; and so is the damage table -- $6562 is the next
                         ; known cell (the attack-sequence latch, below)

and the init wipe at `$65A9` (`STA $64A0,Y / CPY #$CE`) clears
`$64A0`-`$656D`, spanning both. Independently, the scoring sweep walks
`$653F,Y` to `$6269 CPY #$22` = **34 rooms**, skipping only room 34, the
NARCISSUS — which is the shuttle, not part of the ship.

The "20" came from `mainloop_sub_5684`'s `CPX #$14`, which bounds the **fire
burn loop** (rooms `$11`-`$13`), not the table. Same mistake in kind as reading
`$5753` as a fire flag (D-163) and `$651C` as a boolean (D-164): a bound
belonging to one loop was taken for a property of the data.

**No behaviour change** — the remake was already right. The docstring is
corrected so the next reader does not "fix" it.

### PV-12 — `$6562` is the attack-sequence latch, and it is modellable after all

Recorded as "not modelled; this simulation holds no such state." Enumerating
all four readers pins it down completely:

    8CD9  INC $6562           ; raised as an Alien/crew encounter fires
    8C85  STA $6562 (=0)      ; reset_attack_state clears it next move pass

    5309  LDA $6562 / BNE -> char_wander   ; the android FLEES instead of attacking
    8DF0  LDA $6562 / BNE rts              ; no character-turn selection
    8EBD  LDA $6562 / BNE rts              ; the Alien does not corrode its room
    8E32  LDA $6562 / JMP $8E39            ; <- DEAD: the JMP is unconditional

So it is live for **exactly one pass** and suppresses three things. The fourth
reader, `check_6562 ($8E32)`, loads it and then falls into an **unconditional**
`JMP` — its guard is dead code, so the tracker scan runs during an attack
sequence regardless. (We already do not gate the scan, so that half was
accidentally right.)

The key realisation: the remake **already emits `ATTACK_ALERT` on precisely the
ROM event that sets the latch** (D-090 cites `$8CD9-$8CF3` for that cue) and
wipes `state.sound_cues` at the top of every `advance`. So the cue list *is*
the latch, at the same one-pass granularity, with no new state invented.

**Action:** `Simulation._attack_sequence_active()`; `_apply_android_attack`
takes the `$5309` exit and wanders. The other two effects (turn selection,
one-pass corrosion skip) are decoded and recorded but not modelled — each is a
single-pass suppression whose visible effect is one point of damage or one
deferred turn.

### PV-31 — the cursor's repeat delay was an invention

`read_input ($71B0)` reads `$C5` (keyboard) and `$DC00` (joystick 2) **once per
main-loop pass** and drops a direction into `$71AF`; `sub_7453` then acts on it
and calls `delay_routine`. There is **no repeat counter, no debounce and no
acceleration anywhere in that path** — the cursor simply steps once per pass
while a direction is held, so the busy-wait (D-162) *is* the repeat rate.

Two consequences. The cadence is `MAIN_LOOP_HZ`, which our hand-tuned
`_JOY_REPEAT_RATE = 4` frames at 30 fps (7.5 Hz) happened to match within 5%.
But `_JOY_REPEAT_DELAY = 12` — a 0.4-second pause before repeating — has **no
counterpart at all**, and is why the remake's cursor felt sticky next to the
original's immediate run.

**Action:** both derived as `round(_FRAME_HZ / MAIN_LOOP_HZ)`, delay == rate.
Guard test asserts there is no initial delay and that the cadence tracks the
main loop rather than a feel setting.

**Ratchet:** 59 -> **56**.

**Lesson.** Two of these three were closed by *arithmetic and enumeration*
rather than by reading new code — the table sizes fell out of the gaps between
known addresses, and `$6562` fell out of listing its readers. Neither needed
the emulator. Worth trying before reaching for a live capture: a fair number of
`[live]` tags in the register may be `[static]` in disguise.

---

## D-166 — ★ the character turn engine, enumerated: four cells, one pump, and why the original feels ambiguous

**Date:** 2026-08-07 · **Source:** all 18 `$650C,Y` writers, all 6 `$64E6,Y` writers, all 8 entries into `check_deferred_move`, `char_pump ($7216)` / `resolve_char_move ($5156)` / `dispatch_char_action ($7244)`, static

Prompted by the user asking whether a proposed loop refactor would be faithful
or invented — a fair challenge, because the design sketched before this pass
contained **two claims that are not in the ROM**. Both are corrected below.

### The four cells

Per character slot Y (1-7):

| cell | meaning |
|---|---|
| `$64EE,Y` | the **only** clock. Decremented once per main-loop pass by `char_pump`. |
| `$650C,Y` | the **pending action code** — what to do when the clock expires. |
| `$64E6,Y` | the pending **destination** (bit 7 set = the duct at that room). |
| `$64C4,Y` | a 0/1/2 **two-phase commit**, used only by AI-substituted moves. |

### The action codes (`dispatch_char_action $7247` -> `sub_char_special $8749`)

    0 = MOVE          ; falls through at $724F to the move code
    1 = REMVGRILLE    ; $8749 CMP #$01 -> $8757
    2 = ATTACK / USE  ; falls to $8751 JMP $4911 = resolve_attack
    3 = the android's special ($874D CMP #$03 -> $5439)

Each is armed with its own base duration, then `compute_action_delay ($4042)`
**adds** the per-slot and per-health terms:

    MOVE        $7B69  LDA #$40        (64)   + delay
    REMVGRILLE  $845A  LDA $403A,Y     (see below) + delay
    ATTACK/USE  $48F7  LDA #$28        (40)   + delay
    android     $5422  LDA #$2D        (45)

### CORRECTION 1 — several characters can resolve in the same pass

The earlier sketch said "the first whose timer hits 0 resolves." Wrong.
`check_deferred_move` ends `INY / CPY #$08 / JMP $7226`, and **all eight**
re-entries into it (`$51BF`, `$5299`, `$52E3`, `$53C4`, `$53E0`, `$722B`,
`$7236`, `$8781`) arrive with Y = the acting slot. So the pump resumes from
whoever just acted and carries on: every character is decremented every pass,
and any number of them can resolve in one, **in slot order**.

### CORRECTION 2 — `$64C4,Y` is a two-phase commit, and only the AI uses it

    515B  LDA $64C4,Y / BEQ $5168     ; 0 -> the fresh-decision tree
    5160  LDA #$02 / STA $64C4,Y      ; else mark 2 and...
    5165  JMP dispatch_char_action    ; ...perform the move NOW
    72D2  LDA $64C4,Y / CMP #$02      ; check_deferred_move then sees the 2,
    72D9  LDA #$00 / STA $64C4,Y      ;   clears it and calls
    72DE  JMP resolve_char_move       ;   resolve_char_move again -> reads 0
                                      ;   -> picks the NEXT action

So an AI move **arrives and chooses its successor within the same pass**. The
writers of `$64C4,Y = 1` are all AI substitutions — `$51A2`, `$51BC`, `$5200`,
`$5228` (the composure-gate and `char_wander` paths). **The player's order
never writes it**: the menu path at `$7B02`-`$7B69` writes only `$650C,Y`,
`$64E6,Y` and `$64EE,Y`, so a player-ordered action expires straight into
`$5168`'s decision tree and dispatches there if the composure gate passes.

### A new order overwrites; there is no queue

`$7B02`-`$7B0A` zeroes **both** `$650C,Y` and `$64EE,Y` before the new action
is armed. One pending action per character, and re-ordering restarts the clock.
The remake's `_orders` list can hold several for the same character
simultaneously — demonstrated: two conflicting MOVE_TOs for Dallas, both live.

### The "ambiguity" is four decoded mechanisms compounding

The user's observation that the original is vague about when characters act is
correct, and it is not sloppiness:

1. **Per-character, health-scaled durations** — 64 to 122 passes for a move, so
   two crew ordered together resolve seconds apart.
2. **The composure gate is re-checked at expiry** (`$5170`, D-157), so an order
   given to a steady crew member can silently become a wander 15 seconds later.
3. **The two-phase commit** puts an AI move's arrival and its next decision in
   the same pass, one behind the timer you were counting.
4. **Slot-order resolution** decides who goes first when two expire together.

A faithful remake reproduces that texture rather than smoothing it.

### `$403A` — REMVGRILLE has its own aptitude table, and it is nearly inverted

`$845A LDA $403A,Y` — by slot, before the health term:

    PARKER  80 · BRETT  80    (~10.1 s)   the two engineers, fastest
    DALLAS 100 · ASH   100    (~12.7 s)
    KANE   120                (~15.2 s)
    RIPLEY 180 · LAMBERT 180  (~22.8 s)   slowest, by a factor of 2.25

This is **not** the movement profile (`$4032`, where Ripley is the quickest
character in the game and Parker the slowest) — it is close to its inverse.
Getting a grille off is an engineer's job and the game says so in data. **The
remake completed REMVGRILLE instantly**, losing a 10-23 second commitment and a
whole piece of characterisation.

**Action:** `GRILLE_ACTION_TICKS` + `grille_action_ticks()`; `REMOVE_GRILL`
now runs a real countdown and returns `IN_TRANSIT` until it expires;
`_slot_of` extracted since two tables now index by it. Test
`test_remvgrille_is_the_slowest_action_and_has_its_own_aptitude_table` pins the
table against the PRG bytes, checks it is not the movement profile, and counts
the actual ticks in play. Eight existing tests assumed instant completion and
were re-staged with run-to-completion helpers.

### Still open

`$7914`, the table `$7B4E`/`$7B60`/`$7BD1` index by the panel cursor to get a
MOVE TO destination, is **read-only, 8 bytes, and only its first three entries
are non-zero** (`$40 $85 $60`) — rows 3-7 read 0. Either `$64E5` is not the
list index on that path or the destination arrives another way. Not yet
cracked, and it is a prerequisite for wiring the player's chosen room into the
pending-destination cell faithfully. Filed as **PV-33**.

**Lesson.** The sketch that preceded this pass was ~70% decoded and 30%
tidied-up architecture, and the tidy 30% was invisible until someone asked
"is this the PRG or an invention?". Enumerating *all* writers of a cell before
designing around it is cheap; the two corrections above both fell out of
counting call sites rather than reading anything new.

---

## D-167 - PV-33 solved: the MOVE TO list is built at `$7917`, and the routing tables had a 35th row we were dropping

**Date:** 2026-08-07 - **Source:** raw-image operand search, `$7860` / `$81EF` builders, `$7B4E` reader, static

### How PV-33 was actually solved

`$7914` looked read-only: three readers (`$7B4E`, `$7B60`, `$7BD1`), no writer
anywhere in the annotated listing, and only three non-zero bytes. Two wrong
guesses were tried first - that it was written through the `$FD/$FE` indirect
pointer (no pointer setup targets `$79xx`), and that the disassembly was
incomplete.

What worked: **scanning the raw PRG for every store/load opcode whose absolute
operand falls in `$7914`-`$791B`**, ignoring the disassembly entirely. That
found eleven writers - all targeting **`$7917`**, not `$7914`.

The base is offset **by three on purpose**: the reader indexes with `$64E5`,
the panel cursor row, and the first MOVE TO entry sits on row 3. So
`$7914 + 3 = $7917` and the cursor row indexes the list with no arithmetic.
`$7914`-`$7916` are not part of the list at all, which is why they looked like
junk.

**Method note:** the trap was assuming the address a table is *read* from is
the address it is *written* to. A grep for the read operand can never find the
writer when the base is deliberately offset. Searching the image by *opcode +
operand range* is immune to that, and to gaps in the disassembly.

### The two builders, and they do not agree

    surface  $7860   walk the FIVE route tables in order:
                       $7883  CMP $7947 / BEQ next   ; == last ACCEPTED -> skip
                       $7888  CMP $7934 / BEQ $7908  ; == CURRENT ROOM -> END the
                                                     ;   whole list, later tables
                                                     ;   never consulted
                     each accepted entry -> $7917,Y, INC $64FD (the count),
                     and its room name copied to the panel

    duct     $81EF   walk the FOUR compass tables:
                       $81F2  CMP $7934 / BEQ next   ; == current room -> SKIP
                     no last-accepted dedupe; each slot carries its own fixed
                     direction word ($807F NORTH / $8093 EAST / $8089 SOUTH /
                     $809D WEST), so two directions to the same room are still
                     two choices

The asymmetry is real: a self-reference **terminates** on the surface and
merely **skips** in the ducts.

This also settles **PV-02** - `MOVE_TO_LIMIT = 8` was a bound with no ROM
backing. The true limit is 1-5 entries on the surface (however many the walk
yields before it terminates) and up to 4 in a duct.

### The data bug it exposed

Extending the walk to every room made `ALIEN_ROUTES` index 34 fail: the
snapshot's tables are **34 rows**, but the five bases are **36/36/35/35 apart**
- every table has a row for room 34, and it is a meaningful one:

    NARCISSUS -> shuttlebay, shuttlebay, narcissus, narcissus, narcissus

which under the surface rule yields exactly one exit, back to the SHUTTLEBAY.
`gamedata.py` extracted `MAPPED_ROOM_COUNT` (34) while its own module header
said "five **36-entry** routing tables". So every consumer - the Alien's own
moves, `jones_dest`, `panic_dest`, `tracker_zone`, and now the MOVE TO menu -
had **no routing data at all** for anything standing in the Narcissus, even
though `$89D0 LDX #$22 / CPX $7935` exists precisely because the ROM expects
the Alien to be able to be there.

The **duct** tables really are 34 (their bases are 34 apart) - there is no
ducting in the shuttle - so only `routing` was widened.

**Action:** `alien.surface_move_targets` / `alien.duct_move_targets` implement
the two decoded walks; `menu._reachable_move_targets` calls them instead of
sorting a set (contents were right for 34 of 35 rooms, but the **order** was
wrong for 10, and order is not cosmetic when the cursor is positional - P3-1).
`gamedata.py` extracts routing at `ROOM_COUNT`; snapshot regenerated. Tests:
`test_move_to_is_the_roms_ordered_walk_not_a_sorted_set` replays the rule by
hand for all 35 rooms; the gamedata guard now asserts 35.

**Still open:** PV-34, the turn-loop rewrite, is now unblocked.

---

## D-168 - PV-34: one clock, one pending action

**Date:** 2026-08-07 - **Source:** D-166's enumeration, applied

The refactor D-166 unblocked, built only from cells whose every writer had been
counted first.

### What changed

**One clock.** The remake ran two per-character countdowns: `crew.step_timer`,
decremented inside `_apply_order`, and a separate `sim._turn_timer` dict read
by `_turn_due` for the panic branch and the android's turn. Both were seeded
with the same expression and counted down independently, so an order and a
panic roll could disagree about whose turn it was. There is now a single
`_pump_characters()` (`char_pump $7216`) that decrements every alive
character's clock exactly once at the top of `advance`, before anything reads
it, and returns the ids that hit zero. `_turn_due` is a pure membership test on
that result; `_turn_timer` is gone, with a guard test to keep it gone.

**One pending action.** `queue_order` now does what `$7B02`-`$7B69` does: drop
whatever that character had pending, then arm `$64EE,Y` **at issue time** with
the action's own base plus `compute_action_delay`. Bases, each decoded:

    MOVE        $7B69  LDA #$40      64
    REMVGRILLE  $845A  LDA $403A,Y   80-180 (D-166)
    ATTACK/USE  $48F7  LDA #$28      40     (new: ATTACK_ACTION_TICKS)

The old `_orders` list could hold several live orders for one character at
once - two conflicting MOVE_TOs would both run.

**The countdown left order resolution.** `_apply_order` no longer decrements
anything; it returns `IN_TRANSIT` while the clock is running and acts when it
reaches zero. That matters beyond tidiness: running the countdown *inside* the
order handler meant every gate in the handler was re-evaluated at tick cadence
instead of once at expiry, which is the structural shape behind the whole
D-150 / D-153 / D-155 / D-157 / D-158 bug family. A MOVE that has not arrived
re-arms for the next leg (`$5193` + `$519B`), so it is one link per action -
never a free multi-room walk.

A direct `_apply_order` call with a zero clock still acts immediately, which is
what the unit tests want and why the 31 direct-call sites needed no rewrite.

### Verified end to end

    Dallas ordered commdcentr -> corridor_1; clock armed at 71 passes
    arrived after 71 passes = 9.0 s

71 = 64 base + 7 (Dallas's `$4032` slot term) + 0 (healthy), and it is now the
*same* 71 that gates his panic roll and the android's turn.

### Test fallout, and what it says

Nine tests failed, all of them staging rather than behaviour:

* three set `step_timer = 1` meaning "one tick left" under the self-decrementing
  model; under a pumped clock that is "still busy", so they became 0;
* four called `_apply_panic_wander()` directly without a pump, so no turn was
  ever due - they now run `_pump_characters()` first, which is the `$7226` gate
  they were implicitly skipping;
* one asserted `pending_orders == 2` after two orders for the **same**
  character - the old behaviour, and exactly the bug;
* one measured REMVGRILLE by re-calling the handler; it now measures through
  `advance()`.

Three new guards: that the second clock cannot return, that one character has
one pending action and re-ordering restarts the clock, and that several
characters can come due in the same pass (D-166's correction).

### Still open

The `$64C4,Y` two-phase commit is **not** modelled. D-166 decoded it - an AI
substitution arms it, the next expiry executes the move, and the pass after
re-decides - but the remake has no AI-substituted-move path distinct from
`char_wander`, so there is nothing yet for it to sequence. Recorded rather than
guessed at. Filed as PV-35.

---

## D-169 - four more PV items, and two of them were only ever stale notes

**Date:** 2026-08-07 - **Source:** operand-range enumeration of `$64FC` and `$64BB`; cross-checking PV-19/PV-21 against D-041/D-085/D-150

### PV-03 - `$64FC` is the GET ITEM submenu flag, and we already honour it

Three writers, found by the same operand-range scan that cracked PV-33:

    8573  LDA #$01 / STA $64FC   ; set at the end of the room-item list draw
    858D  LDA #$00 / STA $64FC   ; cleared on leaving the submenu
    7797  LDA #$00 / STA $64FC   ; and again by guard_alien_present, on
                                 ;   (re)selecting a character

So `$891E LDA $64FC / BEQ $8924` means **do not draw GET JONES while the GET
ITEM list is up** - the two share the same panel real estate.

The remake gets this for free: `MenuController.entries()` routes to
`get_item_entries` while `getting_item` is set and never reaches the GET JONES
branch, so the gate holds by construction. Closed with a citation, no code.

### PV-05 - `$64BB` decoded; the superset stays, deliberately

Two writers - `begin_active_play ($4F92 LDA #$01)` raises it as the attack
sequence starts, `pause_clear_active ($501E LDA #$00)` drops it. Every reader
is **presentation**: the IRQ (`$4D2F`), both movement blips' guards
(`$4E42`/`$4E5C`, D-088) and the Alien's sprite animation (`$4EE8`).

So it marks "an attack sequence is on screen" - a presentation latch this
simulation deliberately does not hold (the renderer's `_attacking` is the
equivalent). Narrowing the ATTACK row to it would mean lifting that latch into
the sim to gain a slightly shorter window on an option that is **never wrongly
offered**. Recorded as decided rather than left open.

### PV-19 and PV-21 were stale notes, not open questions

Two register entries turned out to describe a state of knowledge that later
discoveries had already superseded - the code comments simply never caught up.

* **PV-19** ("does the tracker report a room or only proximity?") - it reports
  **neither**. D-041 read the game's own sound-legend strings (`$451C` "the
  TRACKER alarm." / `$453C` "SOMETHING moving between locations."): the alarm
  names no room and no entity, which is why `state.tracker_alarm` is a bare
  bool. D-150 then decoded the *range* - `resolve_char_display_loc ($8DB6)`
  builds `$6565..$656A` from the holder's room plus its entry in each of the
  five route tables, six rooms in all. Granularity: "something is moving in
  your zone", nothing finer.
* **PV-21** ("the SHORT scenario's differences are entirely `[?]`") - true when
  FV-1.9 removed the invented oxygen budget, superseded by **D-085**. `$604F`
  overwrites the randomised opening with a scripted one: victim pinned to KANE,
  android to ASH, four 7-entry tables copied over the crew arrays, DALLAS and
  BRETT started **inside the ducts**, and a tracker, the net and the cat box
  pulled into COMMD CENTR. All extracted into `SHORT_SCENARIO` /
  `SHORT_ITEM_MOVES` and applied by `Simulation._apply_short_scenario`. The
  only claim that survives is the narrow one `nostromo_ship` makes: the
  **topology** is mode-independent.

One more stale comment fixed in passing: `constants.py` still called `$5753,X`
"the per-room FIRE flag", which D-163 corrected to the per-room
**special-option code** table (1=SCUTTLE/OVERRIDE, 2=BLOWLOCK, 3=HYPERSLEEP,
5=LAUNCH, 6=FIGHT FIRE).

**Ratchet:** 56 -> **53**.

**Lesson.** Two of four "open questions" were answered discoveries whose
docstrings were never revisited. A placeholder register is only as honest as
its last reconciliation, so the sweep is worth re-running against the
discovery log periodically - not just against the code. The cheapest possible
close is finding that you already did the work.

---

## D-170 - re-triaging the [live] items: two thirds of them were static

**Date:** 2026-08-07 - **Source:** `delay ($561E)` cycle count, operand scans of `$D027-$D02E` and `$64C2`, MENU1.prg's own BASIC

D-165 noticed that some `[live]` tags in the PV register looked like `[static]`
in disguise. Before booting VICE, all nine remaining `[live]` items were
re-examined. **Six move to `[static]`, two close outright, and only three are
genuinely blocked on hardware.**

### `delay ($561E)` is computable, so the card durations are static (PV-26)

The engine's own delay loop::

    561C  delay_long: LDX #$00          ; 0 -> 256 outer iterations
    561E  delay:      LDY #$00
    5620  INC $0334 / INC $0334         ; 6+6
    5626  LDA #$00 / STA $D020          ; 2+4
    562B  INC $0334 x4                  ; 24
    5637  INY / BNE $5620               ; 2+3
    563A  INX / BNE delay               ; 2+3

44 cycles of body + 3 for the branch = 47 per inner iteration, 256 of those per
outer pass, 256 outer passes:

    delay_long (X=$00)  3,081,727 cycles  =  3.128 s PAL
    delay      (X=$80)  1,540,863         =  1.564 s
    delay      (X=$40)    770,431         =  0.782 s

So every `JSR delay_long` is **3.13 s** and every `JSR delay` is that scaled by
X/256. `TITLE_TICKS` and `OPENING_TICKS` are just a count of those calls -
readable, not measurable. (`LOADING_PLAY_TICKS` is a different animal: MENU1
stuffs `LOAD"ALIEN",8,1` into the keyboard buffer, so its duration is however
long the drive takes, not a designed card.)

### The Alien's sprite colour is GREEN, and always was static (PV-28)

    4E8E  LDA #$05
    4E90  STA $D02B / $D02C / $D02D / $D02E     ; sprites 4,5,6,7 -> colour 5

and `begin_active_play` sets `$D015 = $F0`, enabling exactly those four. So
whichever channel the creature occupies it is **green** - matching the title
screen's egg (`init_c $5DEB`, all colour 5). This had been carried as "the
pre-R-05 placeholder red, still `[?]`" on the grounds that the specific
register "was not pinned down"; an operand scan for stores into `$D027-$D02E`
answered it in seconds.

### `GameMode.FIXED` describes nothing (PV-20)

`$64C2`, the opening victim slot, has **exactly two writers** in the image:
`$5071` inside the randomised pick (`JSR rng / LDA $50EC,Y`) and `$6064
LDA #$02`, SHORT pinning it to KANE (D-085). There is no third path, so
`FIXED_OPENING_DEATH_ID = "lambert"` never described a ROM behaviour - it was
one live observation of the *random* draw. The register asked for more live
boots; enumeration settled it without any. `DeathVariant.FIXED` stays as an
explicitly-labelled remake testing aid (`--death fixed` for reproducible runs),
not a fidelity claim.

### The rest of the re-triage

| item | was | now | why |
|---|---|---|---|
| PV-01 logo art | live | **static** | EXITO.prg holds the block graphics as PETSCII in BASIC - decode with the real charset, no capture needed. Its *timings* stay live. |
| PV-14 corrosion rate | live | **static** | `guard_6562` is called once per `alien_ai_dispatch`, i.e. once per Alien action, gated on surfaced + `$64B4` clear. `+1 per action` is derivable; the 50-second live watch only ever bounded it. |
| PV-24 tracker sound | live | **static** | The IRQ's `$4DD7 DEC $64B8 ... STA $D412` gate is the pulse; enumerating `$64B8`/`$4D03` writers should name it without listening to anything. |
| PV-32 NOTICE sprite | live | **static** | MENU1 line 556 is `CO=33 : RO=18 : CL=1 : GOSUB 3000`, and 3025-3030 compute `X = 33*8+18 = 282` (so the MSB bit is set), `Y = 18*8+40 = 184`, colour 1. Fully determined in the BASIC we already have. |
| PV-27 reveal rates | live | live | BASIC interpreter speed; genuinely needs the machine. |
| PV-25 attack siren | live | **live, blocked** | Not merely "boot VICE" - this build implements no OSC3 (`$D41B`) reads at all (D-148). Needs real hardware or a resid build. Retagged so nobody wastes a pass on it. |

**Net:** the `[live]` queue drops from **9 to 3**, and of those three one is
blocked on a different emulator rather than on effort.

**Lesson.** Three of these were tagged `[live]` because an earlier pass wrote
"not pinned down this pass" and the next reader promoted that to "needs
hardware". The distinguishing question is cheap and worth asking every time:
*is the value computed by the program, or observed from it?* Cycle counts,
table contents, register writes and BASIC constants are all the former. Only
feel, interpreter speed and audio output are really the latter.

---

## D-171 - PV-25 was never a fidelity question: every sound played at double speed

**Date:** 2026-08-07 - **Source:** user report ("the rendered audio wav sounds correct, the issue is just the audio playback") + measurement

PV-25 had sat in the register for weeks as "the attack siren cannot be verified
on this VICE build (no OSC3 reads, D-148)", and D-170 had just re-tagged it
**live, BLOCKED - needs real hardware**. That framing was wrong end to end.
The user pointed out that the *rendered WAV* sounds correct, which relocates
the fault entirely: the synthesis was never in question, the **playback** was.

### The bug

    sound = pygame.mixer.Sound(buffer=sfx.wav_bytes(pcm, rate))

`pygame.mixer.Sound(buffer=...)` reads its bytes as **raw samples already in
the mixer's current format**. It does *not* parse a RIFF container. The mixer
initialises stereo (`get_init() -> (44100, -16, 2)`) and `sfx.wav_bytes`
produces **mono 16-bit**, so every clip was consumed as interleaved stereo:

* **half the duration and an octave up** - measured exactly, `Sound(buffer=wav)
  .get_length()` returns `0.266 s` for a clip whose PCM is `0.532 s`;
* alternate samples split across left and right, which is what turns a smooth
  siren into a buzz;
* and the 44-byte WAV header played as audio - a click at the front of every
  clip.

This hit **every effect**, not just the siren: both movement blips, the
heartbeat, the tracker ping and the airlock crack were all an octave high with
a click. The exported `.wav` files were always right, which is exactly why the
problem read as "the siren is strange" rather than "audio is broken".

### The fix

Hand pygame a file-like object so it parses the container and converts
mono -> stereo itself:

    sound = pygame.mixer.Sound(io.BytesIO(sfx.wav_bytes(pcm, rate)))

Verified across all four cached effects - every clip's `get_length()` now
matches the PCM it was rendered from to within a rounding error (ratio 1.00,
was 0.50). Guarded by
`test_clips_play_at_their_rendered_length_not_half_of_it`, which compares every
entry in `sfx.EFFECTS` against its own rendered length; a ratio of 0.5 is the
bug returning.

### What this says about the register

PV-25's entry described a *verification* obstacle and hid a *defect*. The
reasoning that got it there was locally sound at every step - the siren sounds
wrong, the siren is a decoded SID routine, the way to check a SID routine is
the oscillator, this VICE has no OSC3 - and the conclusion ("needs real
hardware") was wrong because the first step's premise was never tested. Nobody
had asked whether the clip we *generate* is correct, which is a five-line check.

**Rule to carry:** when something sounds or looks wrong, separate **"is the
artefact wrong?"** from **"is the presentation of the artefact wrong?"** before
reaching for the oracle. The artefact is almost always cheaper to test, and a
correct artefact immediately localises the fault to the layer above.

### The intro music is the control case

Worth recording because it corroborates the diagnosis independently.
`out/intro.wav` is **mono 16-bit at 44100 - the same format as every SFX
clip** - and it always played correctly. It reaches the mixer by a different
route: `pygame.mixer.music.load(str(path))`, which loads from a file and
*does* parse the container. Same format, correct playback, different API.

That rules out "mono is the problem" and pins the fault exactly on
`Sound(buffer=)` misreading a RIFF container as raw samples. It also means the
symptom was legible all along: one audio path sounded right and every other
sounded wrong, and the two differed only in how the bytes were handed over.
Nobody had drawn the line between them.

PV-25 is closed as a fixed defect. The original question it *claimed* to be
about - whether the decoded siren matches the real machine's output - remains
genuinely unverifiable on this VICE build and is refiled as **PV-36**, honestly
scoped this time: it is a nice-to-have confirmation of an already byte-verified
transcription, not a blocker.

---

## D-172 - PV-26: the title card is 25 seconds, not 5, and there is a whole screen we never modelled

**Date:** 2026-08-07 - **Source:** `delay ($561E)` cycle count, `$5E81` title routine, `$4380` sound-legend screen, static

D-170 retagged PV-26 `[static]` on the grounds that `delay` is countable. Cashing
that in.

### The arithmetic

    561C  delay_long: LDX #$00        ; 0 -> 256 outer passes
    561E  delay:      LDY #$00
    5620  INC $0334 / INC $0334       ; 6 + 6
    5626  LDA #$00 / STA $D020        ; 2 + 4
    562B  INC $0334 x4                ; 24
    5637  INY / BNE $5620             ; 2 + 3
    563A  INX / BNE delay             ; 2 + 3

44 cycles of body + 3 for the branch = 47 per inner iteration, 256 inner
iterations, 256 outer passes = **3,081,727 cycles = 3.128 s PAL**.

### The title card

`$5E81` writes the 13-char header `$5E67` = **"JOSEPH CONRAD"** (the Nostromo
and her crew are named out of Conrad), then calls `delay_long` **eight times**:

    5E8E  JSR delay_long
    5E91  LDA #$81 / STA $0431     ; A
    5E96  JSR delay_long
    5E99  LDA #$8C / STA $0436     ; L
    5E9E  JSR delay_long
    5EA1  LDA #$89 / STA $043B     ; I
    5EA6  JSR delay_long
    5EA9  LDA #$85 / STA $0440     ; E
    5EAE  JSR delay_long
    5EB1  LDA #$8E / STA $0445     ; N
    5EB6  JSR delay_long
    5EB9  JSR delay_long
    5EBC  JSR delay_long
    5EBF  RTS

So the whole card is **8 x 3.128 = 25.0 s** and the gap between letters is
exactly one `delay_long`. `TITLE_TICKS` was **40** (5.1 s) and
`TITLE_LETTER_TICKS` was **6** (0.8 s) - both about **five times too fast**,
and both had been flagged `[?]` calibration since the game modes work. Now 197 and 25,
computed. The letters land at `$0431/$0436/$043B/$0440/$0445` - row 1, columns
9/14/19/24/29, which is the spaced "A L I E N" R-36 describes.

### A screen we never modelled at all

Chasing the other `delay_long` cluster (`$4389`-`$43D0`, eight more calls) led
somewhere unexpected. It is **not** the opening death notice - it is the
game's **sound-legend screen**, and it plays each effect as it names it:

    4389  delay_long x2
    438F  copy $4500 -> $061D        "A GRILLE BEING REMOVED."
    439C  delay_long
    439F  JSR sfx_blip_a             ; ...and play it
    43A2  delay_long x2
    43A8  copy $4554 -> $061D        "SOMETHING MOVING BETWEEN LOCATIONS."
    43B5  delay_long
    43B8  JSR sfx_blip_b
    43BB  delay_long
    43BE  copy $452A -> $061D        "THE TRACKER ALARM."
    43CB  LDA #$21 / STA $64B6       ; arm the tracker tone
    43D0  delay_long
    43D3  JSR prompt_and_wait        ; "PRESS ANY KEY" ($6475 -> $07D8),
                                     ;   spins on LDA $C5 / CMP #$40

These are the same three strings D-041 used to prove the tracker alarm names
neither a room nor an entity - but nobody had noticed they belong to a
*screen*, one that teaches you the three sounds before play and waits for a
key. The remake has no counterpart: `sfx.SOUND_LEGEND` exists as a name for
the strings, and that is all.

Filed as **PV-37** rather than built: the screen's own caller was not found by
a scan of `JSR`/`JMP` into `$4340`-`$438C`, so where it sits in the boot order
is still open, and guessing its position would be exactly the kind of
invention this register exists to prevent.

**Lesson.** The cheap win (a cycle count) was the stated goal; the valuable
find was the *other* caller of the same routine. Enumerating a routine's call
sites pays twice - once for the timing you wanted, once for the code you did
not know existed.

---

## D-173 - PV-37 located: the DECK PLAN KEY / SOUND LEGEND screen, and the key's real glyphs

**Date:** 2026-08-07 - **Source:** `game_init_mode ($4304)`, `$704E`, the `$4460`-`$44FF` string block, static

D-172 found the screen but not its place in the boot order, and filed it rather
than guessing. Both are now settled.

### Where it sits

    7049  LDA $4303 / BEQ $7051
    704E  JSR game_init_mode ($4304)      ; <- the screen
    7051  JSR sub_5049                    ; roll the opening
    7054  LDA #$06 / STA $D020            ; border blue = start_game

So it runs **immediately before the opening is rolled and play begins**, and it
is **conditional** on `$4303` being non-zero - a flag whose writer is not yet
traced, plausibly "show the help this run".

### What it actually is

Not just a sound legend - a combined **DECK PLAN KEY + SOUND LEGEND** screen:

    row  2 col  2   "DECK PLAN KEY."
    row  4 col  6   "LOCATION PTR       [] GRILLE"
    row  6 col 25   "[] LADDER UP"
    row  8 col  6   "CHARACTER POSTN    [] LADDER DOWN"
    row 13 col  0   "THIS IS THE SOUND OF "
    row 13 col 21   "THE HEARTBEAT OF THE CURRENT CHARACTER."
                    ($4367 LDY #$03 / STY $64FB / JSR fear_alert - it selects
                     RIPLEY's slot purely so the demo heartbeat has a rate)
    then, paced by eight `delay_long`s (~25 s):
                    "A GRILLE BEING REMOVED."            + sfx_blip_a
                    "SOMETHING MOVING BETWEEN LOCATIONS." + sfx_blip_b
                    "THE TRACKER ALARM."                  + $64B6 = $21
    43D3            prompt_and_wait -> "PRESS ANY KEY" ($6475 -> $07D8),
                    spinning on LDA $C5 / CMP #$40

It teaches all five map symbols and all four sounds, then waits for a key.

### The glyphs D-046 never extracted

D-046 cited this key for **which** symbols exist ("Location Ptr", "Grille",
"Ladder Up", "Character Postn", "Ladder Down") and used that to prove the map
draws no Alien and no cat. What it never read was the bytes. Decoding the
strings as reverse-video screen codes (`$A0` = blank) leaves exactly three
non-letter glyphs:

    GRILLE      = $E6
    LADDER UP   = $D3
    LADDER DOWN = $D1

LOCATION PTR and CHARACTER POSTN carry no inline glyph because they are
**sprites**, placed by the same routine at `$4371`-`$437E` (`$D000`/`$D002` = X
`$28`, `$D001` = Y `$6E`, `$D003` = Y `$4E`).

Recorded as `_KEY_GRILLE_GLYPH` / `_KEY_LADDER_UP_GLYPH` /
`_KEY_LADDER_DOWN_GLYPH`. The deck map currently draws its own markers; these
are what the original's key says they should be.

### Also on this screen's neighbour

The title card's bottom-row header `$5E67` decodes to **"JOSEPH CONRAD"**,
written to `$07D7` = row 24, col 23 - the ships in *Alien* are named out of
Conrad (*Nostromo*, 1904; the shuttle *Narcissus*, 1897). Useful as an
alignment marker when checking the title card against the original, alongside
the letters at row 1, columns 9/14/19/24/29.

**Lesson.** Two passes had cited `$4460` - once for the symbol *list*, once for
the sound strings - without either noticing the other, or that both belong to
one screen. Citing a table for the fact you need is not the same as reading it.

---

## D-174 - PV-37 closed: `$4303` is the game MODE, and the introduction is a Y/N prompt in SHORT only

**Date:** 2026-08-07 - **Source:** every writer of `$4303`, `game_init_mode ($4304)`, `$4405`, static

D-173 left one unknown and guessed at it in passing: "`$4303` - a flag whose
writer is not yet traced, plausibly *show the help this run*". Wrong, and the
correction is more interesting than the guess.

### `$4303` is the selected game mode

Four writers, two of them the mode selection itself:

    5F3F  LDA #$01 / STA $4303 / JMP start_game    ; option 1 = FULL
    5F4E  JSR sub_604f                             ; the SHORT setup (D-085)
    5F51  LDA #$02 / STA $4303 / JMP start_game    ; option 2 = SHORT
    4320  LDA #$00 / STA $4303                     ; consumed (FULL path)
    43E1  STA $4303                                ; consumed (A=0, intro path)

and `start_game`'s `$7049 LDA $4303 / BEQ $7051` simply skips `game_init_mode`
when no mode has been chosen.

### The introduction is offered only in SHORT, and only if you say yes

    4304  fill $0400/$0500/$0600/$06E8 with $A0    ; clear the screen
    4317  LDA $4303 / CMP #$01
    431C  BNE $4324                                ; mode 2 -> ask
    431E  LDA #$00 / STA $4303 / RTS               ; mode 1 (FULL) -> straight to play

    4405  copy $443C -> $0400   "DO YOU WANT AN INTRODUCTION"
    4412  copy $4457 -> $0456   "PRESS Y OR N"
    441F  LDA $C5 / CMP #$19 / BEQ $442F           ; Y -> show it
    4425  CMP #$27 / BEQ $442C                     ; N -> skip
    4429  JMP $441F                                ; else keep waiting
    442F  clear screen / JMP $4327                 ; -> the DECK PLAN KEY screen

So: **FULL goes straight into the game with no introduction at all**, and
**SHORT asks "DO YOU WANT AN INTRODUCTION? PRESS Y OR N"** - answering Y runs
the DECK PLAN KEY / SOUND LEGEND screen D-173 decoded, N drops straight
through to `$43D6`.

That is a coherent design the remake had no idea about: SHORT is the beginner
scenario, so it is the one that offers to teach you the five map symbols and
the four sounds. It also means **two** front-end screens are unmodelled, not
one - the Y/N prompt as well as the legend itself.

### What this changes about PV-37

It is no longer "a screen at an unknown position". It is:

* reached only from mode 2 (SHORT), after `sub_604f` has laid out the scenario;
* behind a Y/N prompt that is itself a screen;
* and its absence is *correct* for a FULL game, which is the mode the remake
  defaults to - so nothing has been visibly wrong, which is exactly why nobody
  noticed it was missing.

**Lesson.** D-173 shipped a plausible-sounding parenthetical ("plausibly show
the help this run") about a byte it had not enumerated, in the same discovery
whose headline lesson was *citing a table is not the same as reading it*. The
guess cost nothing only because it was checked one turn later. Enumerate the
byte or say nothing about it - a hedge word like "plausibly" is not a licence,
it is the tell.

---

## D-175 - the Q/QUIT screen built: "ONE-STEP DEALER", and three ways to render nothing

**Date:** 2026-08-07 - **Source:** `MENU1.prg` lines 740/830, `EXITO.prg`, the chargen ROM

The user's own PV-01 report: *"hitting q just exits instead of showing the
original exit screen."* Now fixed.

### What Q really does

MENU1 line 740: `IF C$=CHR$(81) THEN CC=0 : P$(0)="EXIT*"`. `CC=0` skips both
the instructions prompt (line 770 `IFCC<>0THENGOSUB10000`) and the "PLUG
JOYSTICK" line (811); line 830 then stuffs `LOAD"EXIT*",8` + `CLR:RUN` into the
keyboard buffer. EXITO draws the same MARQUIE border and the same centre-out
CENTER ROUTINE the WELCOME menu uses, holds for `FOR XX=1TO3000` (~3 s), and
ends on **`SYS 64738`** - a cold reset, which lands you back at the boot screen.

Modelled as `Screen.EXIT_ADVERT`, timed, returning to `LOADING_MENU`. `Q` now
raises a distinct `InputEvent.QUIT_TO_ADVERT` so plain `QUIT` keeps meaning
"close the program" everywhere else.

### The logo reads ONE-STEP DEALER

Lines 450-520 are block graphics stored as raw PETSCII. Two earlier attempts to
read them as ASCII produced gibberish. Rendering the codes through the **real
chargen ROM** and looking at the result settles it in one go: **ONE-STEP** in
WHITE on rows 12-15, **DEALER** in BLUE on rows 18-21, under three RED lines at
rows 5/7/9 ("THESE AND MANY MORE / FINE PROGRAMS MAY BE FOUND / AT YOUR
NEARBY"). A ShareData retailer plug. Stored as the BASIC's own PETSCII rather
than redrawn, so the glyphs stay the machine's.

### Three independent ways to render a blank screen

The first cut **passed its flow test while drawing solid black**. Three
unrelated faults, any one of which is sufficient:

1. **A dispatch branch that never landed.** `str.replace(old, new, 1)` with no
   assertion on the match count - it hit a different occurrence. Two other
   edits from the same script vanished the same way, unnoticed.
2. **The wrong charset.** The default `c64_font=True` is ALIEN's custom cut-out
   font, but **D-047** already established that the front-end screens are drawn
   by the *loader* programs, which run before `ALIEN.prg` repoints the VIC
   (`set_charbase $400A`). EXITO is BASIC; it uses the machine's chargen ROM.
   The rule existed and was written down; it just was not applied.
3. **An entered-frame reset in the wrong branch** - placed inside
   `if flow.screen is not Screen.WELCOME`, so it fired every frame *while on*
   EXIT_ADVERT and the centre-out reveal never advanced past step 0.

The flow test was green through all three, because it tested the transition,
not the screen. What caught them was rendering to a PNG and looking at it.

**Action:** `test_the_exit_advert_actually_renders` runs the reveal out and
asserts the three colour bands the BASIC specifies actually appear, on their
own rows. Its docstring carries the three faults so the next reader knows what
it is defending against.

**Lesson.** The comment directly above the draw dispatch already says *"the
unit tests passed because they set `_frame_count` by hand - a good reminder
that testing a draw call is not testing the loop."* The corollary earned here:
**testing a transition is not testing a screen.** For anything visual, render
it and look at it - three faults that four green tests could not see were
obvious in one image.

---

## D-176 - PV-38 built: the SHORT scenario's two intro screens, and one shared slot

**Date:** 2026-08-07 - **Source:** `$4405`, `$4327`-`$43D3`, screen-RAM offsets

Building what D-173/D-174 specified. Two screens the remake never had, both
reachable only from the SHORT scenario.

### The flow

`_start(mode)` now branches the way `game_init_mode ($4317)` does - it reads
the chosen mode from `$4303` and **returns immediately for FULL**, so:

    FULL   -> OPENING                      (no introduction, ever)
    SHORT  -> INTRO_PROMPT
                Y ($441F CMP #$19) -> INTRO_LEGEND -> OPENING
                N ($4425 CMP #$27) -> OPENING

`INTRO_LEGEND` is timed at `INTRO_LEGEND_TICKS = 197` - the eight `delay_long`s
`$4389`-`$43D0` spends (8 x 3.128 s = 25.0 s, D-172) - and also takes any key,
because it ends on `prompt_and_wait ($43E5)`.

### The detail that made the layout work: one shared slot

The first cut laid the sound legend out as separate centred lines and it looked
wrong immediately - text running off the right edge, and the sentence not
reading. The screen-RAM offsets explain why:

    $44C1 -> $0608   row 13 col  0   "THIS IS THE SOUND OF "   (fixed prefix)
    $44D6 -> $061D   row 13 col 21   the heartbeat description
    $4500 -> $061D   row 13 col 21   "A GRILLE BEING REMOVED."
    $4554 -> $061D   row 13 col 21   "SOMETHING MOVING BETWEEN LOCATIONS."
    $452A -> $061D   row 13 col 21   "THE TRACKER ALARM."

**All four descriptions are copied to the same address.** They replace each
other in place, and each composes with the fixed prefix into a sentence:
*"THIS IS THE SOUND OF A GRILLE BEING REMOVED."* The 42-char field wraps onto
row 14 when it needs to, because the ROM is writing a fixed-length run into
`$0400+n` and column 39 is not a boundary to it.

That is a much simpler screen than three stacked lines, and it is only visible
if you compute the offsets rather than eyeball the strings. Added
`_blit_wrapped` so the remake writes fields the same way.

The three inline glyphs are the ROM's own (GRILLE `$E6`, LADDER UP `$D3`,
LADDER DOWN `$D1`, D-173); LOCATION PTR and CHARACTER POSTN have none because
the routine places them as sprites (`$4371`-`$437E`), which is why their rows
read as a label with a gap.

### Testing

`test_the_short_scenario_intro_screens_render` checks both screens actually
draw, and checks the wrap **at the stage where it happens** - the 42-char
heartbeat line, not the 18-char tracker line that ends the sequence. The first
version of that assertion failed for the right reason and was tightened rather
than relaxed.

One existing flow test needed updating: it asserted Ctrl+2 goes straight to
OPENING, which is now INTRO_PROMPT -> N -> OPENING.

**Lesson.** D-175's lesson was *render it and look at it*; this one adds the
complement. Looking at the picture showed the layout was wrong but not why -
what explained it was **computing the screen-RAM offsets** and noticing three
strings share one address. The image tells you something is wrong; the
addresses tell you what the shape is.

---

## D-177 - PV-15/PV-24: the Alien's attack is doubly random, and FV-1.6 read the wrong routine

**Date:** 2026-08-07 - **Source:** `$413C`-`$41F7`, `alien_tick ($8AE1)`, an operand scan for `JSR rng`

### The misattribution

FV-1.6 concluded the Alien's encounter is **deterministic** - "both callers of
`alien_wound_crew ($5354)` gate only on co-location + health; there is NO RNG
chance and NO 'armed crew are exempt' rule". The second half stands. The first
was drawn from the wrong routine: **both callers of `$5354` pass `$64C3` - the
android's slot - as the attacker** (`$534B LDY $64C3` and `$546A LDA $64C3`).
`$5354` is the *android's* wound routine. The name is a misnomer, the same
class of error as `$5753` (D-163), `$651C` (D-164) and `place_alien_sprite`.

The Alien's own encounter is `$413C`, reached from `alien_tick ($8AE1)` once
`$64A3` is set, and an operand scan for `JSR rng` puts three of its 21 call
sites inside it.

### What it actually does

    414D  LDA #$00 / STA $64A7            ; candidate count = 0
    4152  JSR rng / CMP #$07 / BCC rts    ; rolls 0-6 -> NO attack at all
    415A  LDA $6501 / BEQ $4185           ; a DUCTED Alien takes the first
                                          ;   ducted crew member in slot order
    4185  ...collect co-located, surfaced, health >= 2 crew into $64A4,X...
    41A7  STX $64A7
    41AA  CPX #$01 / BNE      -> one candidate: that one
    41B8  JSR rng / LSR / BCC -> two:   50/50 between $64A4 and $64A5
    41C4  JSR rng
    41C7  CMP #$05 / BCC      -> three+: rolls 0-4  -> candidate 0
    41CB  CMP #$0A / BCC      ->         rolls 5-9  -> candidate 1
    41CF                      ->         rolls 10-15-> candidate 2
    41F4  LDX $64A4
    41F7  DEC $7D45,X                     ; wound EXACTLY ONE

Two rolls, then a single wound. `$64A4`-`$64A6` is three bytes wide, which is
exactly `ROOM_CAPACITY` - the game never needs a fourth candidate.

### Why it matters

The remake wounded **every** co-located crew member on **every** Alien action.
The ROM does nothing at all 7 times in 16, and otherwise hurts one person.

So a crowded room is **safer per head**, not more dangerous: the same single
wound is shared out. That inverts the intuition the remake had been teaching,
and it is a large difference in practice - the old model could take three
health points off a room per action where the ROM takes at most one, less than
half the time. Measured after the fix: over twelve 2000-tick runs (~4 minutes
of play) a mean of **5.9 of 7 crew are still alive**, where the old model
routinely emptied rooms.

### PV-24 closed alongside

The register said "the tracker's sound is not tied to a decoded routine;
`sfx_blip_b` is a *candidate*". It is not a blip at all - it is a **re-gated
voice-3 pulse train**, and `sfx.py` already implements it correctly. Six sites
pin it: `$4DF5` (freq hi `$32`), `$4DFF` (AD `$08`), `$65C9` (`$4D03` = `$12`,
the divider), `$4DD7`-`$4DEA` (the IRQ counts it down and re-gates voice 3 from
`$64B6`), `$8DF6` (`LDA #$21`, sawtooth + gate, arms it), `$8C80` (`LDA #$00`
silences it) - and `$43CB`, which does the same `#$21` write under the caption
**"THE TRACKER ALARM."** on the DECK PLAN KEY screen. The game names its own
sound; that was the tie the register was asking for. All of it is now pinned by
a test that re-reads the bytes.

**Lesson.** Three passes have now been misled by a routine's *name*. The
tell here was available cheaply: `alien_wound_crew`'s callers both load
`$64C3`, and `$64C3` is the android. **Read what a routine's callers pass it
before trusting what it is called** - especially when the name came from an
earlier pass rather than from the machine.

---

## D-178 - PV-08/09/10/11/14 closed, and a composure mechanic nobody had found

**Date:** 2026-08-07 - **Source:** operand scans of `$7D55` and the roster area, `$4618`-`$4674`, `$45D3`, `$47D0`, `$8EBD`

Five register items answered in one pass by enumerating **every writer of
`$7D55`** (base composure) - fourteen of them - and reading each site.

### PV-08 - `crew.Role` really is film canon

A scan of the roster area `$A65E` and its neighbours finds panel text
("INDICATE LOCATION", "DISPLAY LEVEL", "UPPER DECK") and room names, and **no
role or rank strings anywhere**. The decode stores seven names and nothing
else. `Role` gates nothing and is display-only, which is what the note
suspected; now it is checked rather than assumed.

### PV-09 - it is a DEATH stressor, not a corpse-discovery one

    47D0  BEQ $47F1                 ; $64A9,X ("just died") clear -> skip
    47D2  LDA #$00 / STA $64A9,X    ; consume the flag
    47DA  LDX #$01
    47DC  DEC $7D55,X               ; -1 to EVERY crew slot 1..7
    47DF  BPL $47E6 / LDA #$00 / STA $7D55,X    ; floored at 0
    47E6  INX / CPX #$08 / BNE $47DC

Ship-wide, once per death, fired from the just-died flag. Nobody has to *find*
anything. And it does **not** share `raise_crowd_fear`'s zero-composure skip -
there is no `LDA $7D55,X / BEQ` before the `DEC`; it decrements and clamps.
`sim._apply_fear_stressors` already models exactly this.

### PV-10 - the site was located; the note was stale

The note said the value was right but "the specific opcode site ... wasn't
separately located". It is `$4230 DEC $7D55,X`, on the Alien's wound path,
which **D-059 already cited**. Every one of the fourteen `$7D55` writers is now
accounted for: `$4230` (wounded), `$47DC`/`$47E3` (a death), `$4CF9`
(crowding), `$5A0D`/`$5A14` (the endgame sweep), `$738D` (duct entry),
`$660E`/`$72A2` (init), and `$4625`/`$462C`/`$463C`/`$4665`/`$466E` - which
turned out to be something new.

### The new mechanic: **holding a weapon steadies you**

`$4618`-`$4674` reads a table at `$45D3` indexed by the held item (`$829A`) and
adjusts composure by **one or two points**:

    ELCTRC PRD · FIRE EXTNG · SPANNER    -> +1
    INCINERATR · HARPN GUN · LASER PIST  -> +2
    TRACKER · NET · CAT BOX              -> no composure effect

`$4665` INCs once; `$466B` INCs and then jumps back to `$4662` to INC **again**
- that is where the +2 comes from. The mirror branch (`$4625`, and `$463C`
falling into it) is the matching -1 / -2.

The ranking is by how good a weapon the thing is, which makes this the decoded
form of the manual's *"confidence will increase by the possession of a useful
piece of equipment"*. The three items with `$FF` are not calming at all: `$45FD`
sends the two **tracker** instances off to write `$656E`/`$656F` = `$FF` (the
tracker-slot bookkeeping D-150 decoded), and the NET and CAT BOX fall straight
to an `RTS`.

**The remake does not model any of this.** Filed as **PV-39** rather than
implemented here, because the routine's *entry* - what dispatches on the code
in A that `$461E CMP #$00` and `$4642 CMP #$02` test - is not yet traced, and
whether the bonus applies on pickup, per turn, or on selection changes what it
is worth. Guessing that is the invention this register exists to prevent.

### PV-11 and PV-14 - both settled by reading the call site

* **PV-11** (the Alien's wound cadence and multiplicity, FV-1.7): `$41F7
  DEC $7D45,X` - one point, one slot, once per encounter, and the encounter
  fires on 9 of 16 actions (D-177). No per-tick accrual, no loop, no repeat.
* **PV-14** (the corrosion rate): `guard_6562` is called once per
  `alien_ai_dispatch` - once per Alien action - behind three gates (`$64B4`
  not hunting, `$6562` no attack sequence, `$6501` surfaced, `$6563` settled)
  and adds exactly `INC $653F,X`. The live watch that "bounded" this never
  needed to happen.

Both are now pinned by tests that re-read the bytes.

**Lesson.** Enumerating *one cell's* writers closed four register items and
turned up a fifth mechanic. `$7D55` had been read at four sites across four
passes, each time for the one fact that pass wanted. Reading all fourteen
at once cost less than any single one of those passes.

---

## D-179 - PV-06/18/23/29/30/35: five closed by checking, one closed as decided

**Date:** 2026-08-07 - **Source:** `$666C`, the captured deck screens, consumer scans, `$5A3E`

A batch of register items that had been carried as unknowns and turned out to
be either already answered or checkable in a single command.

* **PV-29** - the portrait face/name mapping was "best-effort (the menu-draw
  code wasn't decoded to pin each face to a name)". It is **one instruction**:
  `place_selected_char_sprite ($666C)` does `LDY $64FB / TYA / CLC / ADC #$BC /
  STA $07FA`, so a portrait's sprite pointer is literally `$BC + the character
  slot`. Slots 1-7 are pointers `$BD`-`$C3` = `_PORTRAIT_SLOTS` in roster
  order, exactly what the tuple already held. Now pinned by a test that reads
  the bytes and rederives the tuple arithmetically.

* **PV-30** - `_ROOM_GLYPH = $A0` was "a documented default, not a claim about
  the original wall glyph". The captures settle it: `$A0` is the commonest code
  in all three deck screens (639 / 529 / 601 of the first 1000 cells). It also
  only ever applies to the synthetic fallback grid, because the real backdrops
  are rasterised from those same captures.

* **PV-18** - `ItemKind` "is presentation-only" was an assumption. Verified: a
  scan for `.kind` / `ItemKind.` outside `items.py` finds **no consumers at
  all**, so nothing can gate on the grouping. (The ROM dispatches per-item
  behaviour on the *instance index* in `resolve_attack ($498D)`, D-154, not on
  any category - so it has no equivalent concept to disagree with.)

* **PV-23** - `map.default_ship` "is a starter topology; confirm nothing
  outside tests reaches for it". Nothing does: `src/` contains **no call site**,
  only prose references, since `Simulation` defaults to the oracle-transcribed
  `nostromo_ship(mode)`. Kept for the five tests that want deliberately tiny
  maps, and its docstring now says plainly that it is scaffolding.

* **PV-06** - "what happens to a countdown that is not overridden in time" was
  filed as the FV-2.8 remainder. D-162 had already answered it: `$5A3E LDA
  $657B / BNE / JMP hull_breach`. Ten 255-pass wraps; the tenth finds `$657B`
  already zero and vents the ship. There is no other exit.

* **PV-35** - `$64C4,Y`'s two-phase commit stays **decoded but not modelled**,
  and closes as a *decision* rather than an unknown. D-166 traced it fully
  (arm -> execute -> re-decide, all within one pass) and D-168 established that
  only AI-substituted moves write it. The remake has no AI-substituted-move
  path distinct from `char_wander` for it to sequence, so modelling the cell
  would mean inventing a mechanism to justify a byte. Recorded with the reason
  so it is not re-opened as an oversight.

**Lesson.** Four of these six were answerable by one grep or one byte read, and
had been sitting in the register for weeks. The register's value is real, but
an entry's age says nothing about its difficulty - it is worth periodically
re-reading the *cheap* ones rather than always reaching for the next
interesting one.

---

## D-180/D-181 - PV-28, PV-32 and PV-39: the last static items

**Date:** 2026-08-07 - **Source:** `update_1 ($4EE8)` / `game_tick_dispatch ($4D19)`, MENU1's BASIC, `scripted_event_check ($45E7)`

### PV-28 - there is no divider inside `update_1` at all

`$64BF` is the frame **index**, not a counter: `$4EEE DEC $64BF / BPL /
LDA #$0B / STA $64BF` walks the 12-entry table at `$4EDC` and wraps, one entry
per call. The division is a level up::

    4D08  LDA $D019 / AND #$81 / CMP #$81 / BEQ irq_raster_split
    4D19  DEC $6579 / BPL $4D2F        ; 9 IRQs per trigger
    4D1E  LDA #$08 / STA $6579
    4D23  JSR update_1

`$4D08` sends only the **raster** interrupt to the sprite multiplexer, so
`game_tick_dispatch` runs on the ordinary 60 Hz jiffy IRQ: 60/9 = **6.67 Hz**.
The old comment said exactly that and was right; the `[?]` was about **units**.
`_ALIEN_SPRITE_FRAME_TICKS` was being used as a count of *renderer frames*
while holding a count of *C64 jiffies*, which ran the animation at half speed.
Now derived: `_ALIEN_ANIM_HZ = 60/9`, and the frame count falls out of
`_FRAME_HZ` (4 at 30 fps, not 9).

### PV-32 - the NOTICE sprite was never captured because it is never written

The register wanted a live capture of "the NOTICE screen's own sprite
registers". `ALIEN.prg` never writes them - this is **MENU1's** screen, and its
BASIC computes them in the open::

    556   CO = 33 : RO = 18 : CL = 1 : GOSUB 3000
    3025  CO = (CO*8)+18        -> 282, so the X MSB is set
    3030  POKE 53248,26 : POKE 53249,(RO*8)+40 -> Y = 184
    3020  POKE 53287,CL         -> colour 1 (white)
    3030  POKE 2040,13          -> data at 13*64 = $0340

Arithmetic in a listing we already had. The other two thirds of PV-32 (the
underline glyph's pixel row and the "A L I E N" header shade) stay `[live]`.

### PV-39 - the manual's confidence rule, decoded and implemented

D-178 found the `$45D3` table but filed the mechanic because the routine's
*entry* was untraced. It is `scripted_event_check ($45E7)`, dispatching on an
event code its callers write to `$45B9`:

* **2** - the held item changed (`$85B1`, after `STA $829A`)
* **3** - the held item was lost (`$4690` / `$8530`)

so the effect is a **one-shot on the transition**, not per turn, and it is
**symmetric**: `$4665` INCs once and `$466B` INCs twice for the acquire side,
mirrored by `$4622` / `$4639` for the loss.

    ELCTRC PRD · FIRE EXTNG · SPANNER    +/-1
    INCINERATR · HARPN GUN · LASER PIST  +/-2
    TRACKER · NET · CAT BOX              exempt

The better the weapon, the more it steadies you and the worse it feels to put
down - the decoded form of *"confidence will increase by the possession of a
useful piece of equipment"*. Implemented on GET_ITEM / LEAVE_ITEM as
`_apply_item_composure`, with the table re-read from the PRG in the test.

**A process note worth keeping.** The first attempt at this edit wrote its
constants file, then failed an assertion before writing `sim.py` - leaving the
GET_ITEM call site missing while the LEAVE_ITEM one, added by a later script,
was present. The test caught it (a pickup moved nothing), but only because it
asserted on **both** directions. A script that mutates several files should
write them all or none; asserting mid-way through leaves exactly this kind of
half-applied state.

---

## D-182/D-183 - PV-32, PV-27 and PV-01 closed: the last "needs an oracle" items did not

**Date:** 2026-08-07 - **Source:** the chargen ROM, MENU1's own control codes, `the live captures (not published)title screen.png`, and D-142's measurement

### PV-32 - all three parts were static after all

* **The NOTICE sprite** was "never captured". It is never *written by
  `ALIEN.prg`* - it is MENU1's screen, and lines 556 + 3025-3030 compute
  X = 33*8+18 = **282** (so the X MSB is set), Y = 18*8+40 = **184**, colour
  **1**, pointer 13 -> `$0340`.
* **The underline glyph's pixel row** was "not extracted from the char ROM".
  Screen code `$77` is `FF FF 00 00 00 00 00 00` - a 2-pixel bar at the **very
  top** of the cell. The remake drew a rect one scaled pixel down; it now
  blits the glyph itself, so there is nothing left to approximate.
* **The "A L I E N" header shade** was carried from R-36's hedge
  ("pink/magenta ... maybe not the exact Colodore shade"). MENU1 line 10006 is
  `PRINTTAB(15)"{28}{17}A L I E N"`, and `CHR$(28)` is **red**. `c64.RED` was
  right all along, and line 10010's `{158}` likewise confirms the yellow.

**And a correction to something I said earlier this pass.** Looking at
`the live captures (not published)title screen.png` while checking the shade: the title screen is
a green alien egg over the line *"'We live as we dream : Alone'"* with
**"Joseph Conrad"** beneath it. So `$5E67` is not a company credit for the ship
names - it is the **attribution of a quotation** (from *Heart of Darkness*).
The ship-name connection is real background, but the screen is a quote and its
author. The reference image had been sitting in the live captures (not published) the whole
time.

### PV-27 - the reveal rates are now derived from the one measurement

D-142 timed the GREEN VALLEY screen live: the spiral in **~11.0 s**, the whole
screen in **~14.1 s**. Counting what the BASIC actually does converts that into
a rate. Lines 220-270 draw each ring as four edges, so over `FORQ=11TO1` plus
`FORQ=1TO11` the spiral is `2 * SUM(130 - 8Q, Q=1..11)` = **1804 POKEs**:

    11.0 s / 1804 = 6.10 ms per POKE

The MARQUIE border (3010-3040) is `40*2 + 25*4 + 40*2` = **260 POKEs** =
**1.585 s** = 47.6 frames at 30 fps - **within 1% of the 48** the old estimate
assumed. So `_BORDER_REVEAL_RATE` was already right, and is now justified
rather than guessed.

The centre-out text is PRINTs, not POKEs, so it takes the residual:
`14.1 - 11.0 - 0.9` (line 320's `FORXX=1TO900`) = ~2.2 s over the two lines'
**12** steps = **183 ms per step**, or 5.5 frames at 30 fps. `_TEXT_REVEAL_RATE`
was **2** - about **2.7x too fast**. Rendering the WELCOME screen after the fix
catches it mid-growth at 13 s, which is exactly the behaviour D-143's live
capture described.

### PV-01 closes

The user's report was *"the animations are slightly different and hitting q
just exits instead of showing the original exit screen"*. Both halves are now
done: the Q path builds EXITO's advert screen (D-175, "ONE-STEP DEALER") and
the animation rates are derived above. The control flow was verified against
MENU1's listing screen by screen in D-161.

### What is left

**PV-36 only**, and it is blocked on hardware rather than effort: confirming
the decoded attack siren against a real machine needs OSC3 (`$D41B`) reads,
which this VICE build does not implement at all (D-148). The siren's SID writes
are already byte-verified against the PRG and its modulator is pinned at
`$4E76`, so this is a nice-to-have confirmation of a transcription, not an open
question about behaviour.

**Lesson for the register as a whole.** Of the nine items that carried a
`[live]` tag, **eight** turned out to be answerable from the PRG, the BASIC
listings, the chargen ROM, or a reference image already in the repo - and one
of those (PV-25) was not a measurement problem at all but a playback bug. The
tag was consistently applied to mean "this pass did not work it out" rather
than "this cannot be worked out statically". Worth asking, every time: *is this
value computed by the program, or observed from it?*

---

## D-184 - PV-36 closed: the siren never needed an oscilloscope

**Date:** 2026-08-07 - **Source:** `$4FA5`-`$4FCA`, `$4E76`, the SID's accumulator width

The last open register item, and its premise was wrong - which is worth
recording, because the same premise had survived three separate framings.

The chain was: the siren sounds odd -> the siren is a decoded SID routine ->
checking a SID routine means watching its oscillator -> this VICE implements no
OSC3 (`$D41B`) reads (D-148) -> **therefore it needs real hardware**. D-171
already broke the first link (the siren sounded odd because *every* clip was
playing at double speed, a playback bug). This closes the rest.

### `$D41B` is not an observation, it is a function of the writes

Voice 3 is set free-running at frequency `$0020`::

    4FB5  LDA #$00 / STA $D40F      ; freq hi
    4FBA  LDA #$20 / STA $D40E      ; freq lo   -> $0020 = 32
    4FBF  STA $D412                 ; ...and the same $20 into the control
                                    ;    register: SAWTOOTH, gate OFF

Gate off means no envelope, so the oscillator free-runs and OSC3 is a plain
ramp. The SID's phase accumulator is 24 bits and advances by `freq` every
clock, and OSC3 on a sawtooth is its top byte, so one full ramp - one siren
sweep - is

    2^24 / freq / clock  =  2^24 / 32 / 985248  =  0.5321 s  =  1.8792 Hz

That is arithmetic on bytes in the image. Reading `$D41B` off a running machine
would return exactly this and nothing more; there was never a measurement to
take. `sfx.ALERT_LFO_HZ` already computed it that way - the register had simply
not noticed that its own module was deriving rather than guessing.

`test_the_siren_is_fully_determined_by_the_prg_no_oscilloscope_needed` now
closes the loop from the image end to end: frequency bytes -> accumulator width
-> LFO rate -> clip length, plus the `$4E76` modulator (`LSR` into `$D401`,
`ADC #$40` into `$D408`) byte for byte.

### What real hardware would actually have added

The analogue character of one particular SID revision. And **6581 and 8580
differ audibly from each other**, so "real hardware" was never a single ground
truth to confirm against - it is a question about which physical chip, not
about the decode. Recording that explicitly so the item is not reopened as an
oversight.

**Lesson, and it is the register's own headline.** Every input to this sound is
byte-verified and its one derived output is arithmetic, yet the item sat tagged
`[live, BLOCKED]` because an early pass wrote "we cannot read OSC3" and each
later reader inherited the conclusion without re-testing the premise. Across
this register, **nine items were tagged `[live]` and every one of them turned
out to be answerable from the PRG, the BASIC listings, the chargen ROM, or an
image already in the repo.** The tag never meant "cannot be determined
statically"; it meant "this pass did not determine it".

---

## D-185 - two bugs in my own EXIT_ADVERT screen, both user-reported

**Date:** 2026-08-07 - **Source:** user report; EXITO's CENTER ROUTINE (lines 2000-2070) and lines 1100/4000

D-175 built the Q/QUIT advert and I checked it by rendering a PNG. Two things
that image did not tell me, and the player did.

### 1. "the graphic split in half and formatted strangely"

The logo's four rows were centred **independently**, each on its own length:

    ONE-STEP rows: len 34, 35, 36, 36  ->  start cols 3, 2, 2, 2

Row 0 one column right of the rest, which shears the tops off the letters. The
rows are horizontal slices of the same glyphs; they must share one column.

The BASIC gives that column, and the reason the rows agree is a detail I had
stripped out. `2010 M=LEN(B$)` · `2020 IF M/2<>INT(M/2) THEN M=M+1` ·
`2050 PRINT SPC(21-N)` with `N=M/2`, so text starts at **21 - M/2**. Each
word's *first* line carries a leading colour code - `{5}` on line 450, `{31}`
on 490 - which **counts toward `LEN` but prints no column**. Counted, all four
rows come out at 3 and 6 respectively; uncounted, row 0 drifts by one. The
control character is load-bearing for the layout.

Added `_center_routine_col()` implementing the routine's arithmetic, used for
the logo and the three advert lines alike.

### 2. "should just hold on the advert screen for a moment before closing"

I had mapped `SYS 64738` to "cold reset -> back to LOADING_MENU", reasoning
that a reset restarts the machine. Wrong for a remake: a reset leaves a bare
BASIC READY prompt with the game **gone** - it does not replay the loader. For
a program that *is* only the game, the faithful equivalent is to **exit**,
which is also what anyone picking a menu item labelled QUIT expects.

`GameFlow.finished` now latches when the advert has held its `FOR XX=1TO3000`,
and the app loop closes on it. The screen stays on the advert as it goes.

### What this says about the D-175 check

D-175's own lesson was *render it and look at it*, and I did - the PNG showed a
legible "ONE-STEP DEALER" and I accepted it. A one-column shear on
block-graphic letters is exactly the kind of thing that survives a glance,
because the word is still readable. And the loop-back was invisible in a
screenshot by construction: it is a **transition**, and D-175's other lesson
was that testing a transition is not testing a screen - the converse bites too.

The general form: **a static render checks composition, not behaviour, and
checks it only as well as you are looking.** For the layout, the fix is to
verify against the source's own arithmetic (the CENTER ROUTINE) rather than
eyeball the output. For the behaviour, only running it - or a player - finds it.

---

## D-186 - the blowlock was silent: a cue raised then cleared before anyone drained it

**Date:** 2026-08-07 - **Source:** user report; `blowlock_sfx ($5904)`, the app loop's ordering

The player asked whether BLOWLOCK not making a sound was correct. It was not.

### `blowlock_sfx` is misnamed - it does both jobs

    5904  LDA #$80 / STA $D40B      ; voice 2 control
    5909  LDA #$96 / STA $D408      ; freq hi
    590E  LDA #$0D / STA $D40C      ; AD
    5913  LDA #$81 / STA $D40B      ; gate on   <- the crack, played FIRST
    5918  LDA $64E5 / CMP #$10      ; which lock the cursor row picked
    591F  LDA $5751 / EOR #$01 ...  ; ...and only now the toggle
    592A  JSR apply_blowlock

So the sound is emitted **inside the option handler**, before the lock flag is
even looked at - and unconditionally on direction, because BLOWLOCK and
SEALLOCK are the same option code (2) reaching the same routine.

### Two bugs

1. **The cue was raised and then thrown away.** `apply_special_option` appends
   `SoundCue(AIRLOCK)`, but the app loop only drained cues *after*
   `sim.advance()`, whose first statement is `self.state.sound_cues.clear()`.
   Every airlock crack was wiped before `play_sound_cues` ever saw it.
2. **SEALLOCK raised nothing at all**, though the ROM plays the same hiss on
   the way shut.

Fixed by draining at the click - which is also where the ROM emits it, not on
a tick boundary - and by raising the cue on the seal path too.

### Why the suite missed it

Every existing sound test inspects `state.sound_cues` directly, or calls
`play_sound_cues` itself. Not one of them exercised **the app loop's
ordering**, so a cue that was correctly raised, correctly gated and correctly
playable still never reached a speaker. The unit boundary was drawn either side
of the defect.

That is the same shape as D-175 (a screen that passed its flow test while
rendering black) and the note above the draw dispatch ("testing a draw call is
not testing the loop"). Third instance this pass: **the seam between two
correct components is where the bugs are, and per-component tests are blind to
it by construction.** The new guard asserts the ordering constraint itself -
that `advance()` clears, therefore a handler-raised cue must be drained before
the next tick.

---

## D-187 - the blowlock fix was dead code; the real path is `MenuController.fire()`

**Date:** 2026-08-07 - **Source:** user report (second time); `menu.fire()`, the app loop

The player reported the blowlock silent, D-186 "fixed" it, and the player
reported it silent again. The diagnosis in D-186 was right; the fix was applied
somewhere that never runs.

### Where the click actually goes

    MenuController.fire()
        elif entry.special is not None:
            self.sim.apply_special_option(entry.special)     # <- straight to the sim

`fire()` is called from the renderer's key handler, i.e. **during
`poll_input`**. Nothing ever appends to `_pending_specials`, so
`poll_special_options()` returns an empty list on every frame - and so does
`poll_orders()`, whose docstring says as much ("the CONTROL panel now issues
orders straight to the sim ... so this is always empty"). D-186 put the drain
*inside* the `for option in renderer.poll_special_options():` loop. That body
had never executed and still does not.

The cue was therefore raised during `poll_input`, sat in `state.sound_cues`
untouched, and was wiped by `advance()`'s opening `sound_cues.clear()`.

Drain moved to immediately after the input loop, which is where the cues
actually exist.

### The test that would have caught it - and the two that did not

Both earlier attempts asserted on `state.sound_cues`, which was **always
correct**. The cue was raised, gated and playable at every step; it simply
never reached the audio layer. The new test drives `fire()` on the real panel
row and asserts the effect comes back from **`play_sound_cues`'s return value**
- the audio layer's own report - rather than inspecting the state it reads.

**Lesson.** Twice now I have written a test against the boundary I happened to
be looking at rather than the one that was broken, and both passed while the
game was mute. When a defect is *"the output never happens"*, the assertion has
to be on the **output**, not on any input to it - state, cue lists and gate
functions are all upstream of the speaker, and all three were fine. This is the
same failure as D-175's black screen (flow test green, nothing drawn) and it is
now the fourth instance in one pass of a seam bug hiding between two correct
components.

Worth noting the dead code was *visible* in the diff: `for option in
renderer.poll_special_options()` had no callers filling it, and
`poll_orders()`'s own docstring already announced the pattern. Reading the
neighbours would have been quicker than shipping the fix.

---

## D-188 - the Alien hit and ran, because `$8AE1` is a JMP

**Date:** 2026-08-07 - **Source:** user report; `alien_tick ($8ACE)`, `$413C`

The player: *"the alien seems to attack and abruptly leave the room."* Correct,
and the reason is one opcode.

    8ACE  DEC $64EE / BEQ $8AD4 / RTS
    8AD4  JSR alien_arrive
    8AD7  LDA $64A3 / BEQ $8AE4       ; no crew here -> ordinary turn
    8ADC  LDA $64A0 / BNE $8AE4
    8AE1  JMP $413C                   ; met crew -> jump away
    8AE4  ...clear $6563, redraw, and dispatch the next move...

`$8AE1` is a **JMP, not a JSR**. An encounter pass therefore never reaches
`$8AE4`, and never picks a destination. `$413C`'s own first act is
`LDA #$28 / STA $64EE`: it re-arms the timer to **40 passes (~5 s)** and
returns. The creature holds the room it just attacked in, then takes a normal
turn.

The remake ran `_resolve_surface_action` and then fell straight through to
`_begin_action`, choosing a new destination on the same pass - so it wounded
someone and walked out immediately.

**The hold applies on a miss too.** `$413C` re-arms `$64EE` *before* `$4152`'s
attack roll (D-177: nothing happens on 7 of 16). So meeting crew always costs
the Alien five seconds, whether or not it lands a hit - which is what makes it
feel like a stalking creature rather than a passing hazard, and why the bug was
so visible in play.

`_resolve_surface_action` now returns whether the encounter path was entered,
and `advance_alien` holds instead of dispatching. Two grille tests had staged a
crew member in the Alien's room as incidental scenery; with the hold in place
that masked the duct decision, so they were re-staged a room away.

### The process failure, third time

The edit did not apply on the first attempt: the script asserted mid-way
through, after mutating its in-memory copy but **before** `write_bytes`, so
`alien.py` was left untouched while the constants file had already been
written. The behavioural check (`held 1/60`) caught it, but only because I ran
one.

**D-181 recorded this exact failure and I repeated it twice since.** The rule
that actually prevents it: a script that mutates several files must do **all
its assertions first, then all its writes** - never interleave. Asserting
between writes leaves a half-applied state that reads as "the fix didn't work".

## D-189 — the four worst re-derivations were all *stale prose*, so the guard is now a test

**Found:** 2026-08-08, auditing the codebase after the first git commit.

Four discoveries this project paid a full pass each to make were not new
readings of the ROM — they were corrections of a *previous* pass's prose that
a later pass had trusted:

| | wrong claim, left in a comment | corrected by |
|---|---|---|
| `$5753` | "the fire flag" | D-163 (it is the special-option table) |
| `$651C` | "a boolean" | D-164 (0/1/2) |
| `$5354` | "the Alien wounds crew deterministically" | D-177 (it is the ANDROID's routine; both callers pass `$64C3`) |
| room 34 | `_SHUTTLEBAY_SLUG` | D-159 (it is the Narcissus) |

In every case the *body* was fixed and a module header, block comment or
docstring somewhere else kept asserting the old thing. Prose has no compiler, so
nothing caught it.

**Action:** two tests in `tests/test_fv3_drift_guards.py`, and a Conventions
bullet in the coding guidelines:

1. `test_no_superseded_claim_survives_in_the_source` — a curated
   `SUPERSEDED_CLAIMS` table of `(phrase, discovery, what is true now)` that must
   not appear anywhere in `src/`. Match on a distinctive *phrase*, never a
   keyword: "deterministic" occurs ten times in the package and **eight are
   still true** (they describe crew→Alien combat, which genuinely is
   deterministic per item).
2. `test_prose_does_not_reference_symbols_that_no_longer_exist` — self-
   maintaining, no table: every `` `_symbol` `` named in a comment or docstring
   must still be defined somewhere in the package. This catches the commonest
   drift for free, a rename that updates the code and leaves the narrative
   behind. Deliberately-historical names are written without backticks.

Seeding them caught 3 superseded claims (`alien.py`'s module header still called
the encounter deterministic; `alien.py` + `constants.py` still cited
`alien_wound_crew`) and 5 dangling symbols — one of which, `_map_right_edge`,
turned out to be **assigned in four places and read in none**: the CONTROL panel
has been fixed at `_PANEL_COL` since R-02, so the value lost its consumer without
losing its writers. Removed.

**Also settled here:** adopting git flipped the working tree to CRLF, which
silently broke every multi-line text edit against the source (three failed edits
before the cause was clear). `.gitattributes` now pins LF for everything except
`.ps1`/`.bat`/`.cmd`, and the tree was renormalised.

## D-190 — the seam harness, and why every existing fake was blind to the same thing

**Found:** 2026-08-08, building `tests/test_integration_loop.py`.

Four shipped defects had the same shape: **every component was individually
correct and the seam between them was wrong.** D-186/D-187 (the sim raised the
cue, the renderer could play it, the loop threw it away in between), P8-15 (the
advert drew and `flow.finished` was set, the loop kept going), P8-15b, and
PV-25/D-171 (`sfx.render` produced correct PCM, the mixer played what it was
given, the handoff format was wrong).

**The mechanism.** `tests/test_remake_flow.py`'s `FakeRenderer` and
`FrontEndDriver` are *passive* — `poll_input` only returns events. The real
backend is not: `MenuController.fire()` (`core/menu.py:927`) calls
`sim.apply_special_option(...)` **during** `poll_input`, so by the time `run_app`
sees the event list the sim is already mutated and `poll_orders()` is empty.
Every fake in the suite modelled the passive shape, so the drain ordering was
free to be wrong — and stayed wrong through two rounds of fixing.

`RecordingBackend` mutates the sim during `poll_input` as the real one does, and
records the loop frame by frame rather than sampling the endpoint, so tests can
assert on *ordering*.

**The acceptance criterion was to revert each fix and confirm the test fails.**
Worth the trouble: two of the four passed with their fix reverted on the first
writing.

- The redundant-clear test used a clock that ticked every frame; a tick runs
  `advance()`, whose opening `sound_cues.clear()` covers for a missing clear in
  the loop. `run_app` draws at 30fps and ticks at ~7.9Hz, so **most real frames
  do not tick** — and on those an undrained queue replays on the next frame's
  input drain. Fixed with `_slow_clock`; the effect in the real game would have
  been a blowlock crack machine-gunning about four times.
- The P8-15b test cannot fail on the original defect at all — that lived in
  `PygameRenderer._exit_entered_frame`, below the loop's visibility. Kept as the
  flow-level invariant with the limit stated in its docstring rather than
  implied away.

**Bonus find.** The audio guard immediately failed on a `mixer.Sound(buffer=`
match — a false positive, since D-171's own explanatory comment quotes the call
it forbids. The scan now skips comment lines. Worth recording because it is a
general hazard for this kind of guard: **a comment explaining a banned pattern
contains the banned pattern.**

**Action:** `tests/test_integration_loop.py`, 6 tests. The last one,
`test_the_backend_contract_matches_the_real_one`, fails if `AppRenderer` grows a
method `RecordingBackend` lacks — otherwise the harness silently stops covering
the new seam, which is how it would rot.

## D-191 — splitting the 3,460-line renderer, and what the call graph revealed

**Found:** 2026-08-08, splitting `render/pygame_app.py`.

The file had reached 3,460 lines (about 46% prose). Split into six modules by
**deriving** the cut from a call-graph closure rather than by eyeballing it:

| module | lines | what it owns |
|---|---|---|
| `pygame_app.py` | 1,103 | the shell: `__init__`, input polling, `draw`'s dispatch, and the shared text/sprite primitives |
| `frontend.py` | 1,327 | 27 methods the play screen never touches |
| `play.py` | 810 | the deck map, CONTROL panel and live overlays |
| `audio.py` | 292 | SFX, heartbeat bed, intro tune |
| `layout.py` | 81 | geometry/timing both halves need |
| `protocol.py` | 161 | the shared attribute + method surface |

**Mixins, not free functions**, because the renderer's state is genuinely
shared. Under mypy `strict = true` a mixin reading `self._surface` cannot
type-check alone, so `protocol.RendererState` declares the shared attributes
once (annotations only — `PygameRenderer.__init__` stays the sole initialiser)
plus stub signatures for the methods the mixins call but do not own. A typo is
then an error rather than an `AttributeError` on the first frame that happens to
take that branch.

`layout.py` exists for a specific reason: `pygame_app` composes the mixins, so a
constant owned by one half and borrowed by the other would make the dependency
run backwards.

**Three things the mechanical analysis found that reading would not have:**

1. `_draw_option_key` is called by nothing. Removed.
2. `_map_right_edge` (already removed in D-189) was the same class of thing —
   assigned four times, read never.
3. Several methods *look* play-only but are shared: `_render_c64_text`,
   `_render_rom_text`, `_sprite_surface`, and the two Narcissus screens. They
   reach the front end through `_c64_or_sysfont` and `draw`'s dispatch, so a
   naive closure from `render()` claims them. Scoped `play.py` to the actual
   play screen instead — moving them would have type-checked and run correctly
   (the MRO resolves it) while making the module boundary a lie.

**On the tests.** They now import from the module that owns the name, rather
than `pygame_app` re-exporting forever. Two tests that pin render constants by
attribute access (`pa._FOO`) got a `_RenderConstants` resolver that searches
every render module: they assert a body of knowledge, not the contents of one
file, so a future split should not break them.

**Two traps for the next mechanical rewrite of this kind:**

- The import rewriter's name map missed `_JONES_X_START, _JONES_X_END,
  _JONES_X_STEP = ...` because a tuple-unpacking assignment has one target that
  is an `ast.Tuple`, not several `ast.Name` targets. Handle tuple targets.
- Extract-and-reassemble must run its **assertions on every span before writing
  any file**, and must verify the spans do not overlap. Both caught real errors
  here before anything was written.

## D-192 — the `D-nnn` namespace is overloaded, and seven ids name two findings each

**Found:** 2026-08-08, while generating an index for `DISCOVERIES.md`.

Building the index surfaced a data-integrity problem nobody had noticed: a
citation of the form `D-nnn` does not uniquely identify anything.

**Three ways it can be ambiguous.**

1. `docs/DECISIONS.md` numbers its own entries `D-001`–`D-022` in the identical
   format. Two registers, one namespace.
2. Within this file, a **second numbering series began 2026-07-09** and collided
   head-on with the 2026-07-01/02 one: `D-009`–`D-014` each name two unrelated
   findings. (`D-012` is both "`--awake-crew`'s bare 0 default" and "Alien AI is
   a weighted random walk".)
3. `D-146` is a plain same-day duplicate.

So a bare "D-012" has **three** possible referents. About 195 citations exist
across the seven duplicated ids, spread over `src/`, `tests/`, the registers and
`docs/re/`.

**Deliberately not renumbered.** Disambiguating 195 citations means reading each
one in context and deciding which finding it meant — a judgement call per site,
and precisely the kind of bulk edit that introduces silent wrongness in exchange
for tidiness. The options (renumber the later series; adopt distinct prefixes
such as `DISC-`/`DEC-` going forward; leave it documented) are a call for the
project owner, not for a pass that happened to notice.

**Action:** what *is* mechanical was done.

- A warning at the top of `DISCOVERIES.md`: resolve a citation by its subject,
  not its number.
- `test_no_new_duplicate_discovery_ids` freezes the existing seven in
  `KNOWN_DUPLICATE_DISCOVERY_IDS` and fails on any new one, so the problem
  cannot grow. It also fails if one of the seven is *healed* without being
  removed from the list, so the ratchet keeps working.
- `test_the_discovery_index_covers_every_entry` fails if the index falls behind
  the body or an anchor stops resolving — an index read *instead of* the body is
  worse than no index.

**Also corrected here:** a decision record was still stated as current two
months after it stopped being true. It was found by reading, not by D-189's
guard, because the guard only scanned `src/` — which is why its scope was
widened to the top-level registers in the same pass.

## D-193 — the fidelity trackers had gone stale in the safe direction

**Found:** 2026-08-08, answering "what's the state of the program now compared to
the original PRG?"

Auditing the answer rather than asserting it turned up three trackers that
overstated the remaining gap. Each had been correct when written and nobody had
refreshed it after the work that closed it.

1. **Two `[INVENTED]` markers in `src/`, both stale.** `FAITHFULNESS.md` defines
   the tag as "no basis in the code — must be removed or replaced, never ships
   knowingly", so anyone grepping it to audit fidelity would have chased two
   closed gaps. `constants.py`'s fear bands said `[INVENTED band boundaries —
   RESOLVED for fear 0-4]`, contradicting itself on one line. `flow.py` warned
   at length that the Ctrl+1/Ctrl+2 chord was not enforced and a bare "1" would
   select — but `pygame_app.py:706` has checked `KMOD_CTRL` on GAME_SELECTION
   since FV-1c2, a month earlier. The register is now at **zero**, pinned by
   `test_no_live_invented_marker_survives_in_the_source`.

2. **`docs/re/UNDOCUMENTED.json` listed three subroutines that are all
   understood.** Replaced with an empty census plus `UNDOCUMENTED.md` recording
   what each one is, so they are not re-derived:
   - `$7520` — colour-RAM row fill, 10 bytes of `$64E4` at row `$64E5`; sibling
     of `$7530 fill10_via_fd`.
   - `$755E delay_routine` — the main loop's busy-wait, already the basis of the
     entire timing model (`MAIN_LOOP_HZ = 7.886`).
   - `$604F` — **the SHORT-game scenario preset**, and the interesting one. It is
     not a shortened FULL game: it pins the android to slot 4 and the opening
     victim to slot 2, starts slots 1 and 7 *in the ducts*, moves three items to
     room 6, and copies four 7-byte tables over the live crew locations, health,
     composure and its mirror. Two health bytes are **0**, so SHORT begins with
     crew already dead. Hand-decoding it from the listing reproduced
     `gamedata_snapshot.SHORT_SCENARIO` byte for byte, which is a pleasing
     independent check of the `gamedata` decoder — the remake already implements
     all of it.

**The pattern is the same as D-189's**, with the sign flipped. That guard exists
because a *corrected* mechanic left its old explanation behind and the next
pass trusted it. Here the mechanic was corrected and the marker saying "still
broken" was left behind — so the drift made the project look *less* faithful
than it is. Both are the same failure: prose that outlived the code it described.

**Action:** the `[INVENTED]` count is now a gate. `[?]` deliberately is not — an
honest open question is a legitimate state for a replica, and blocking a gate on
one would just encourage not filing it.

## D-194 — nothing in `ALIEN.prg` is unused, and P5-3 is closed

**Found:** 2026-08-08, answering "are any sections of the PRG not used?"

**P5-3 closed by the player** — *"the siren seems to work now."* The ROM read in
D-148 was right the whole time: voice 3 is an ungated free-running sawtooth at
`$0020` used purely as an LFO, and `irq_alt_handler` copies `$D41B`/2 into voice
1's frequency-high and that +`$40` into voice 2's every IRQ, so the alert
**sweeps**. It stayed open only because this VICE build does not implement OSC3
reads (`$D41B` = 0 under every condition), so the oracle could not confirm what
the listing plainly said. Playing it settled what the oracle could not — worth
remembering the next time the emulator and the disassembly disagree: **the
emulator is the approximation.** Every defect register is now closed.

### The dead-code census: there is none

Classifying every byte outside the graphics bank:

| | bytes |
|---|---|
| reached as code | 15,775 (6,748 instructions) |
| graphics bank `$2000-$3FFF` | 8,192 |
| `$FF`/`$00` filler (uninitialised work RAM) | 10,691 |
| real data islands | 6,303 in 125 islands |

Cross-checking each island against every operand any instruction names (±255 for
indexed access) left **410 bytes in 47 islands** apparently unreferenced. All of
it resolves:

- ~44 are **single stray bytes** inside the work-RAM region — one non-`$FF` byte
  in a sea of `$FF`, an artifact of the disk image rather than data.
- The three real ones — `$A956`, `$A9C4`, `$AA6E` — are the **duct-map
  templates**, reached through a *computed pointer*: `select_menu_template
  ($817D)` picks one by `$7569,Y` and stuffs the address into `$FD/$FE`. A
  static operand scan cannot see that, which is the method's known blind spot,
  not a finding. They were decoded a fortnight ago (R-41/D-091).

So **every byte of the program is accounted for**: reached as code, in the
graphics bank, uninitialised RAM, or a decoded data table.

**A caution recorded from getting it wrong twice here.** I first diffed a
hand-rolled decode of those templates against the *deck* captures — 176/540
cells "matching". They are duct maps, not deck plans; `ductmap.py`'s own
docstring says so in its third sentence, and the two partitions agree for only
12 of 34 rooms. Then my 20-line reimplementation of `render_message ($7F0D)`
disagreed with the shipped decoder, because it mishandled a blank run that
crosses a row boundary. **The shipped decode is the trustworthy one** and it
re-validates exactly: all 34 room positions land on the node glyph `$E6`, and
the node counts per template are 9/16/9, matching the room counts. A quick
reimplementation is not a check on a cross-validated decoder; it is a second
thing that can be wrong.

## DISC-195 — the register numbering, settled (and the first entry to use it)

**Found:** 2026-08-08. Decided by the project owner after D-192 surfaced the
problem and D-194's census quantified it.

**The blast radius was bigger than "our local documents".** Of 3,220 `D-nnn`
references, **260 are ambiguous**, and they are not confined to prose files:

| area | ambiguous |
|---|---|
| top-level registers | 127 |
| `docs/history/` (archive — not to be rewritten) | 58 |
| **`src/` — shipped source** | **41** |
| **`tests/`** | **17** |
| `docs/re/` | 17 |

Two facts shaped the decision.

1. **Nothing programmatic depends on the numbers.** No code parses, looks up or
   branches on a `D-nnn`; they are all prose citations. So a renumber could not
   break anything at runtime — the only risk is silently pointing a citation at
   the wrong finding.
2. **Most citations already disambiguate themselves.** 49 name their register
   outright (`DECISIONS D-010 #3`); 16 sit beside "full disassembly" /
   "DISASSEMBLY §", which identifies the 2026-07-09 series. Excluding the
   archive, **137 are genuinely bare.**

**Decision: prefix going forward, disambiguate in place, touch no citation.**

- New entries are **`DISC-NNN`** here and **`DEC-NNN`** in `docs/DECISIONS.md`, so
  the collision cannot recur. This entry is the first.
- The fourteen colliding entries (`D-009`–`D-014`, `D-146`, two each) now carry
  a **Disambiguation** note naming the other one by date and subject, so a
  lookup resolves in one step against the index.
- The ~260 existing citations are left exactly as they are.

The alternative — renumbering and rewriting all 137 bare sites — buys exactness
at the price of 137 hand judgements, 41 of them in shipped source, where a wrong
call is invisible and no guard can catch it. The register is a *lookup aid*; the
authority is the finding's subject matter. Trading a real risk of silent
wrongness for tidiness is the wrong way round, and this project has been burned
four times (D-159/163/164/177) by exactly that kind of quiet inaccuracy.

**Action:** `tools/reindex_discoveries.py` and both drift guards accept either
prefix and sort on the number alone, so the table stays one sequence.
`docs/DECISIONS.md` carries the convention.

**One process note.** Widening the id pattern took two passes: the index guard
kept failing because `headings` had been updated to accept `DISC-` and the
`rows` regex beside it had not. The test caught its own half-finished edit,
which is the whole argument for these guards being executable rather than
written down.

## DISC-198 — a four-part cleanup: sim split, comment rewrite, naming audit, folder archive

**Found/done:** 2026-08-08, on the owner's four-item request.

### 1. `core/sim.py` split (see DISC-196)

The renderer's call-graph method **did not transfer**. `sim.py` is not layered
by entry point — `advance()` drives order resolution — so a closure from the
public methods left 19 methods (727 lines) shared. Split by *subject* instead:
the order pipeline, the SPECIAL panel, and the clock + crew AI.

Two mechanical-extraction bugs, both caught by gates rather than review, and
both worth remembering for the next one:

- Reparenting `from .x` to `from ..x` with a **line-anchored** regex missed the
  three *method-local* imports. 73 tests failed.
- The `@property` decorator on `pending_orders` was **left behind** when the
  method moved, so it silently re-decorated the next method in the file. 25
  tests failed; mypy said "Too many arguments for property". Span extraction now
  includes `decorator_list` and asserts a moved decorated method carries its
  decorator with it.

### 2. Comments explain the code, not its history (DISC-197)

48% of `src/` was comment, and a 5-element tuple carried a **69-line block**
that was mostly the transcript of the live capture that settled it. The rule is
now a stated convention: say what it is, cite the ROM address, name the trap, and
point at `DISCOVERIES` for the derivation. Internal process ids (`FV-1.6`,
`PV-25`, `P8-3`, `R-32`) come out — they mean nothing to a reader who was not
there.

`constants.py` 1,128 -> 965 lines, 19 blocks rewritten by hand; standalone
process-id labels stripped from 15 files mechanically. The mechanical pass
asserted **line counts were preserved**, which caught an earlier version whose
`\s*` ate newlines and merged comment lines together.

That pass also surfaced a stale claim no guard could see: `alien.py` still
carried FV-1.6's "both callers of `$5354` gate only on co-location ... one wound
to each co-located crew member" — directly above the D-177 block that
contradicts it. The phrase is now in `SUPERSEDED_CLAIMS`, **narrowed to include
the word "gate"**, because D-177's own entry correctly says both callers "pass
`$64C3`" and a looser phrase flagged the correction as though it were the error.

### 3. Identifier naming: already clean

Audited all 1,438 identifiers in `alien_remake`. **Zero** are address-shaped —
no `sub_7520`, no `var_4bef`. Names are domain language (`jones_run_armed`,
`heartbeat_divider`, `assign_start_rooms`) and ROM addresses appear only in
comments as provenance, which is the right split. Nothing to do.

(The first regex for this reported 13 hits, all false: `dead`, `surface` and
`face` are made of hex digits. Requiring an actual digit gave zero.)

### 4. `archive/`

Everything neither part of the program nor useful to development: the
one-time setup scripts and the 2026-06-25 legacy import. `archive/README.md`
records what each folder is *and what deliberately stayed at the root* —
the build runner, `tools/vice-mcp` (the live oracle) and the registers.

## DISC-199 - the game cannot currently be won, and the corrosion gate was wrong

**Found:** 2026-08-08, trying to write the missing "prove a win is reachable" test.

The suite had 724 tests and none of them played a real game to a victory. The
two existing win tests stage a two-room ship with the Alien, an armed crew
member and an open airlock already in place, then fire one order: they prove the
**win check** fires, not that a win is **reachable**. Writing the real thing
turned up three separate findings.

### 1. The corrosion gate was wrong (fixed)

`guard_6562 ($8EBD)` does `INC $653F,X` for the Alien's room behind three gates,
and the remake honoured none of them::

    8EBD  LDA $6562 / BNE rts      ; no attack sequence on screen
    8EC3  LDA $6501 / BNE rts      ; the Alien is not in a duct
    8EC8  LDA $6563 / BEQ rts      ; ...and $6563 is set
    8ED0  INC $653F,X

`$6563` is cleared on every move dispatch (`$8AE6 STY $6563`) and re-raised only
at `$8B13`, which is reached when `$8B03 LDA $7935 / CMP $64E6 / BEQ` finds the
Alien's room equal to its **destination** (`$64E6,Y` is the per-character
destination array). So the creature corrodes a room it **lingers in**, never a
room it is merely passing through. The remake added +1 on every action.

Fixed: corrosion is now gated on `lingering`. Games got measurably longer.

### 2. All three win routes are unreachable

Even after the fix, twelve seeded games with a hit-and-run player never got the
Alien past **16 of the 50 damage** needed. The arithmetic says why:

| | |
|---|---|
| damage to kill the Alien | 50, at +1 per hit for every weapon but the harpoon |
| room damage per hit | 6 (`$4AF0`) |
| a room is lost at | 20 - and losing **one** room ends the game |

Killing it therefore costs **300 points of hull spread over 15 intact rooms**,
none of which may tip over, while the Alien independently corrodes every room it
sits in. ALIEN_AIRLOCKED uses the same attack path and hits the same wall.

**EVACUATED is blocked differently**: the launch validator requires *every* alive
crew member aboard the Narcissus, but the evac room obeys `ROOM_CAPACITY = 3`.
With six alive after the opening death, three of them can never board, so the
launch is refused forever. Eight seeded games all plateaued at exactly 3 aboard.
An evacuation win requires first being reduced to <= 3 survivors - plausibly what
the original intends, but nothing tells the player and nothing tested it.

**Which of these is a misread and which is the real game is now the open
question.** The suspicious number is the 6:1 ratio of hull damage to Alien
damage; a replica in which the intended victory condition cannot be reached is
more likely to have a decoding error than to be faithful.

### 3. Two order-pipeline behaviours that look like bugs and are not

Both cost time before being recognised:

- **Re-issuing an order freezes the crew member.** `queue_order` re-arms the
  turn timer at issue time (`$7B69`), so a policy that re-issues every tick
  never lets anyone take a step. The first probe issued 7,759 MOVE orders and
  completed none.
- **The android silently drops orders** (`$5265`). The first probe spent a whole
  game ordering the android to attack while it stood next to the Alien ignoring
  every one, and reported "ATTACK always BLOCKED" as though the combat path were
  broken.

**Action:** `tests/test_winnability.py` pins each barrier as an assertion about
the *blocking number*, not as an `xfail` on the win - an `xfail` would go quietly
green the moment someone changed a constant for an unrelated reason.

## DISC-200 - live oracle session: three confirmations and one strong lead

**Found:** 2026-08-08, driving the real disk under VICE to settle DISC-199's
open question (which combat/damage constant is misread).

### Confirmed against the running game

1. **The front end is faithful.** Screen RAM at each stage decodes to exactly
   what the remake draws: the Green Valley back-up notice, then
   `WELCOME TO ALIEN / FACE THE POWER OF THE UNKNOWN / 1 ALIEN / Q QUIT`, then
   `DO YOU WANT INSTRUCTIONS. (Y OR N) / N WILL START THE GAME`, then
   `GAME SELECTION. / CONTROL.1 FULL GAME / CONTROL.2 SHORT SCENARIO` with the
   crew names above and `PAUL CLANSEY C1984 CONCEPT SOFTWARE` on row 24.

2. **`START_HEALTH` is exact.** `$7D45` on a fresh full game reads
   `00 06 05 04 05 04 06 05` - slot 0 is the Alien's damage accumulator at 0,
   and slots 1-7 are `6,5,4,5,4,6,5`, byte-for-byte the decoded table.

3. **The mode gate.** `$5F36` is `LDA $91 / CMP #$FA` for FULL and `CMP #$F3`
   for SHORT. Writing `$FA` into `$91` starts a full game, which is the
   reliable way to drive the selection screen from a script - the Ctrl+1
   keyboard chord did not register.

### The lead on DISC-199

Over a complete unattended playthrough - game start (Alien in room 8, crew at
`08 06 06 1B FE 1B 1B`, the `$FE` being the opening death) through to the
ending screen `THE NOSTROMO RETURNS TO EARTH`, about 65 s of real time -
**every one of the 35 bytes of `$653F` stayed at zero.**

The remake, over the same span, accumulates enough room damage to breach a room.
So the passive-corrosion model looks wrong **in kind, not merely in rate**, which
would explain why DISC-199 found the ship destroying itself before the Alien
could be killed.

**Not yet proof.** The sample brackets an ending, and the ending may reset
`$653F`; a clean mid-game pair of samples is still needed. The next pass
should poke `$91 = $FA` from the selection screen and read `$653F` twice during
play, 30 s apart.

### Tooling note that cost time

**VICE checkpoints do not stop execution in this setup.** A checkpoint on
`$8ED0` never fired, which looked like strong evidence that the corrosion INC is
never reached - until a control checkpoint on `main_loop ($719D)`, which every
pass executes, also failed to fire. Both were void. Any future "the breakpoint
never hit, therefore the code never runs" argument must be paired with a control
on a known-hot address.

## DISC-201 - the corrosion model IS in the PRG, but it is gated four ways and never fires in normal play

**Found:** 2026-08-08, live oracle. Answers the question DISC-199 left open.

### The code is real

`$8ED0 INC $653F,X` exists and is genuine ROM, reached through
`guard_6562 ($8EBD)` from `alien_ai_dispatch ($89B1)`. The remake did not invent
it. But it is behind **four** gates, and the remake honours at most one::

    89AC  LDX $64B4 / BNE          ; (1) not in the pursuit/aggro state
    89B1  JSR guard_6562
    8EBD  LDA $6562 / BNE rts      ; (2) no attack sequence on screen
    8EC3  LDA $6501 / BNE rts      ; (3) the Alien is not in a duct
    8EC8  LDA $6563 / BEQ rts      ; (4) ...and $6563 is set
    8ED0  INC $653F,X

`$6563` is cleared on every move dispatch (`$8AE6`) and re-raised at `$8B13`
only when `$7935 == $64E6` - the Alien's room equals its destination. `$64B4` is
set to 1 at `$4CB3`, alongside `$64A0`, on an RNG-gated aggression path.

### Live: it never fired

A complete unattended full game - Alien starting in room 8, crew at
`08 06 06 1B FE 1B 1B` - ran to its ending in about 65 s of real time with
**all 35 bytes of `$653F` still zero**.

### The failure modes are opposite, which is the real finding

| | how an idle game ends | ship | crew |
|---|---|---|---|
| **original** | `ALL CREW LOST` - the Alien hunts them down | intact, zero room damage | all 6 dead |
| **remake** | hull breach from accumulated room damage | one room at 20 | 3-5 still alive |

So this is not a tuning difference. **The original kills the crew; the remake
destroys the ship.** That inversion is what makes DISC-199's kill route
unreachable: the remake's hull is consumed by a mechanic that, in the original,
contributes essentially nothing during ordinary play.

**Practical reading:** in the original, room damage is driven by **weapon acid**,
not by the Alien's presence - which is exactly what `constants.py` already
suspected in the note "the fast breach driver is weapon acid".

### What to do

Implementing gates (1) and (2) is the faithful fix - (3) is already covered by
`surfaced` and (4) landed this pass as `lingering`. That is deliberately
**not** done yet: it needs the mid-game `$653F` pair to confirm the corrosion
rate is near-zero rather than merely slow, so the change can be verified instead
of guessed. One gate was added this pass on solid static grounds; a second
should wait for the measurement.

### Also confirmed live

- The whole front-end sequence decodes byte-for-byte to what the remake draws.
- `$7D45` on a fresh game reads `00 06 05 04 05 04 06 05` - `START_HEALTH` exact.
- `$5F36` gates the mode on `$91`: `#$FA` FULL, `#$F3` SHORT.
- The lost ending is three lines: `THE NOSTROMO RETURNS TO EARTH` /
  `THE ALIEN AND ITS EGGS ARE UNLEASHED UPON THE PLANET` / `ALL CREW LOST`.

## DISC-202 - the Alien's damage gates corrosion, but backwards: a WOUNDED Alien corrodes LESS

**Found:** 2026-08-08, chasing the owner's question "does the corrosion happen
when the Alien is injured and not all the time?"

The instinct that the Alien's damage gates corrosion is **right**. The direction
is the opposite of the obvious one.

`$4C9C` reads the Alien's own accumulated damage and feeds a quarter of it into
an aggression roll::

    4C9C  LDA $7D45        ; the Alien's damage (slot 0 of the health table)
    4C9F  LSR A / LSR A    ; damage / 4   -> `AGGRESSION_DAMAGE_DIVISOR`
    4CA2  ADC $4781        ; ...on top of the accumulator the crew scan built
    4CA8  JSR rng
    4CAB  CMP $4781
    4CAE  BCC $4CB3        ; roll under it -> take the aggression path
    4CB0  JMP clear_char_action
    4CB3  LDA #$01 / STA $64A0 / STA $64B4
    4CC6  JSR alien_ai_dispatch

So **the more wounded the Alien, the likelier it enters the aggression state**
and sets `$64B4`. And `$64B4` is exactly what suppresses corrosion::

    89AC  LDX $64B4
    89AF  BNE $89B4        ; aggressive -> SKIP the corrosion call entirely
    89B1  JSR guard_6562   ; only a calm Alien reaches this

The state also persists until the creature reaches its destination, and clears
with a **short** reload rather than the normal one::

    89F7  LDX $64B4 / BEQ $8A11
    89FC  CPX $7935 / CPX $64E6 / BNE $8A07
    8A09  STX $64B4        ; arrived -> drop out of aggression
    8A0C  LDA #$14 / STA $64EE   ; 20 ticks, not 60 -> `ALIEN_PURSUIT_TICKS`

**The behaviour that produces:** hurt the Alien and it stops wrecking the ship
and starts *hunting* - moving three times faster and skipping the corrosion
step. An unwounded, unprovoked Alien is the one that damages rooms.

That is a far better piece of game design than the remake's version, and it
explains the oracle result in DISC-201: in an unattended game the crew never
wound the creature, yet `$653F` stayed at zero anyway - so the corrosion is
gated by more than aggression alone, and the two remaining gates (`$6562`, and
`$6563`'s exact lifecycle) still need tracing before a positive rate is restored.

**Action:** `ROOM_DAMAGE_ALIEN_PER_ACTION` stays 0 (DISC-201). Restoring it now
requires modelling `$64B4`, which is newly tractable: the remake already has
`AGGRESSION_DAMAGE_DIVISOR` and `ALIEN_PURSUIT_TICKS` decoded from the same
routine, so the missing piece is the `$4781` accumulator and the roll, not the
constants.

## DISC-203 - RETRACTS DISC-201: the corrosion is real, fast, and I measured it wrong

**Found:** 2026-08-08, isolating the Alien in the oracle at the owner's
suggestion.

### The retraction

DISC-201 concluded that `$8ED0`'s corrosion "never fires in normal play", on the
strength of `$653F` reading all zeros in two games. **That conclusion was wrong,
and the method was bad.** Both readings were taken either seconds after a new
game began - when the array is legitimately zero because the init wipe at
`$65A9` has just cleared it - or after the game had ended and re-initialised.
Neither was a mid-game sample. I inferred "stayed at zero throughout" from two
endpoints that were both guaranteed zero.

This is the same error as the earlier checkpoint episode in DISC-200, where a
breakpoint that never fired looked like proof until a control breakpoint on a
known-hot address also failed to fire. There I caught it; here I did not, and
acted on it - zeroing `ROOM_DAMAGE_ALIEN_PER_ACTION` and rewriting a test to
assert the opposite of the truth.

### What the isolation experiment actually shows

Teleporting every living crew member to room 1 while the Alien was at room 32
removed the encounter path, stopped the game ending in 30 s, and guaranteed
nothing but the Alien could touch `$653F`. Over the next minute::

    t+0    rooms 3/5/14/16/20/25/32/34 = 8/3/1/2/2/10/2/12
    t+30s  rooms 3/14/15/20/32/33/34 all gained; 34: 12 -> 15
    t+60s  3: 9->11, 5: 3->8, 20: 3->9, 32: 4->10

`$651C` finished with alarms latched in seven rooms and **room 34 at stage 2,
critical**. So corrosion is real, it is fast, and it reaches the critical band
within a minute of an unattended game.

`ROOM_DAMAGE_ALIEN_PER_ACTION` is back to **1**, and the test asserts corrosion
happens rather than that it does not.

### What survives

- **DISC-202 stands.** It is a static trace: `$4C9C` feeds the Alien's own
  damage/4 into an aggression roll, and `$64B4` skips the corrosion call. That
  is read off the listing, not off a measurement, and the isolation run does not
  contradict it - the crew never wounded the Alien, so it stayed out of the
  aggression state, which is exactly when corrosion is *enabled*.
- **DISC-199 stands** as an observation: no win route was reachable. Its
  *diagnosis* - that over-fast corrosion was to blame - is now doubtful, because
  the original corrodes fast too.

### The new lead

Room 34 reached 15 and **latched alarm stage 2 without ending the game**, then
sat there. In the remake, 20 is an instant loss. The original's rooms clearly
survive the critical band for a long time. So the suspicious constant is no
longer the corrosion rate - it is `HULL_BREACH_THRESHOLD` and the shape of the
breach test (`$5658 CMP #$14`, an equality on a counter that only ever INCs).
That is where the next measurement should go: watch a single room cross 20 in
the oracle and see what actually happens.

### Method note

**Never infer a time-series from two endpoints that are both structurally
zero.** Sample mid-window, and prove liveness at the sampling instant - here, by
reading `$7935` alongside `$653F` and confirming the Alien had moved.

## DISC-204 - SOLVED: the hull breach is an equality, and that is why the game was unwinnable

**Found:** 2026-08-08. Closes DISC-199.

### The bug

    5658  C9 14     CMP #$14        ; exactly 20?
    565A  D0 03     BNE $565F       ; no  -> just latch alarm stage 2
    565C  4C 17 5D  JMP hull_breach ; yes -> the ship is destroyed

The breach test is a **strict equality**. `$653F,X` only ever climbs, so a room
carried *past* 20 can never equal it again: it latches `$651C,X = 2` (critical)
and is then **permanently safe**. A big weapon hit - the harpoon's +15 - can
deliberately burn a room out, after which the crew can fight in it freely.

The remake used `>=`, with a comment explaining the choice: "the remake's damage
can arrive in larger steps (a 15-point harpoon hit), and overshooting 20 must
not make a room immortal." In the original it does exactly that. The reasoning
was sound and the premise was backwards.

### Why it made the game unwinnable

DISC-199 worked out that killing the Alien costs 50 hits x 6 room damage = 300
points of hull, and concluded the kill route was arithmetically impossible
because no room may pass 20. With the equality restored, that arithmetic
dissolves: rooms are *meant* to be pushed past 20 and reused.

**Result, same policy, same seeds:** 12 games, previously 12 losses with a best
of 16/50 damage. Now **10 wins by ALIEN_KILLED and 2 losses.** A game.

### What this cost, and the lesson

Getting here took two wrong turns, both mine:

1. **DISC-201** claimed the corrosion never fires, from two `$653F` reads that
   were both structurally guaranteed to be zero (one just after the `$65A9` init
   wipe, one after the end-of-game re-init). Retracted in DISC-203 after the
   owner suggested isolating the Alien, which showed corrosion climbing fast.
2. A `$6563` model that was **inverted for the dominant case** - it corroded
   hardest during the post-encounter hold, which is precisely when `$8AE1 JMP
   $413C` means the ROM never reaches the flag-setting code.

Both were attempts to explain a symptom (the ship dying too fast) by adjusting
the mechanism that *fills* the damage counter, when the fault was in the test
that *reads* it. **When a value looks too big, check the comparison before
re-modelling the accumulator.**

### Still open

- `HULL_BREACH_THRESHOLD` is now used as an equality but the remake still sweeps
  all rooms once per tick, where the ROM tests at the moment of the add. These
  agree unless two adds land in one tick.
- The evacuation route remains blocked by `ROOM_CAPACITY = 3` vs "every alive
  crew member aboard" - untouched by this, and still worth confirming against
  the oracle.
- `$64B4`/`$6562`, the two unmodelled corrosion gates from DISC-202.

## DISC-205 - all four corrosion gates, traced and wired

**Found:** 2026-08-08. Completes DISC-201/202/203/204.

`guard_6562 ($8EBD)`, reached from `alien_ai_dispatch ($89B1)`, is gated four
ways. All four are now traced and all four are modelled.

| gate | ROM | meaning | remake |
|---|---|---|---|
| `$64B4` | `$89AC LDX / $89AF BNE` | not hunting | `alien.hunting` |
| `$6562` | `$8EBD LDA / BNE rts` | no attack sequence on screen | `alien.attack_sequence` |
| `$6501` | `$8EC3 LDA / BNE rts` | the Alien is not in a duct | `surfaced` |
| `$6563` | `$8EC8 LDA / BEQ rts` | surfaced and sitting at its destination | `corrode_pending` |

### `$6562` - the attack-sequence latch

`$8CD9 INC $6562` raises it together with `$64A3` when the Alien meets crew;
that is the same block that writes the "ATTACK" text at `$8C76` into `$064E` and
tests `$8CE1 CPY $64FB` for the selected character. `reset_attack_state ($8C80)`
clears it, from `$72F9` and `$7E5A`.

### `$64B4` - the hunting latch, and a correction

**DISC-202 said `$64B4` was "not modelled". That was wrong** - `_roll_hunt` and
`alien.aggression` have modelled the roll, the 20-tick pursuit timer (`$8A0C`)
and the refusal to enter a duct (`$89CE`/`$8A90`) for some time. The only part
missing was that it also **suppresses corrosion**. Two of the three effects were
there; the third was not.

Set at `$4CB3` from an aggression roll fed by the Alien's **own damage / 4**
(`$4C9C`), and cleared at `$8A09` once the provoked move completes. The full
behaviour of a wounded Alien:

1. stops corroding the ship,
2. will not duck into a duct,
3. moves three times faster (20 ticks, not 60),
4. stays that way until it reaches where it is going.

**Hurt it and it stops eating the ship and comes after you.** That is a much
better creature than the remake had, and it is now in.

### Confirmed by the owner, not a bug

The Narcissus refuses to launch with more than three living crew aboard because
the evac room holds three and the validator wants everyone. **That is the real
game's behaviour** - escape requires being down to three survivors. DISC-199
listed it as a blocked route; it is a design constraint, and the remake already
reproduces it. Removed from the open list.

### Where that leaves the balance

Same policy and seeds as DISC-204, with all four gates wired: **9 wins by
ALIEN_KILLED, 3 losses.** Winnable, losable, and no longer decided by a hull
that dissolves on its own.

## DISC-206 - three player reports: graphics provenance, deck-follow, and the grille overflow

**Found:** 2026-08-08, reviewing three items from the owner.

### 1. The graphics are code/data, not images

Nothing is loaded from an image file at runtime; the only `.png` references in
`render/` are comments citing reference screenshots.

| what | where it comes from |
|---|---|
| charset + sprites | extracted from `ALIEN.prg` `$2000-$3FFF` (`alientools.charset` -> `out/charset.bin`) |
| duct sheets | RLE-decoded from the PRG at `$A956`/`$A9C4`/`$AA6E` |
| loader-screen font | the machine's own chargen ROM (`render/romfont.py`) |
| **deck plans** | **VICE screen-RAM captures** (`the live captures (not published)*deck_0400.bin`) |

The deck plans are the one exception - real bytes, but *captured* rather than
decoded. They remain the project's only dependency on a capture for game
content.

### 2. The deck view does NOT follow the selected crew member - and that is faithful

Reported as a bug; it is the original's behaviour, and D-131 had already
established it. Re-checked because the evidence looked like it pointed the other
way: `$4CCE LDA $7935,Y / STA $64F7` really does copy the selected character's
current room every pass. But `menu_option_dispatch ($511C)` uses `$64F7` only to
position **sprite 0** from the flat per-room tables `$758D`/`$75B1` - nothing
there redraws the deck template. The manual agrees: "EACH DECK OF THE SHIP CAN
BE SELECTED FROM THE MENU."

So the marker follows; the plan does not. **One thing does auto-switch**:
`$4CD4 LDA $6501,Y` sends a character who is *inside a duct* to
`select_menu_template`, so the duct sheet does follow. The remake already does
that (`play._draw_duct_map`).

A note to that effect is now in `play.render()` so the next reader does not
"fix" it again.

### 3. "GRILLE IN PLACE" ran off the screen - real bug, fixed

The remake appended the caption to the room/damage status line::

    CARGOPOD 3  DAMAGE 00% :WARNING:   GRILLE IN PLACE     -> 50 columns

Ten columns past the 40-column field. In the ROM the caption is not part of that
line at all: `$8710 LDA $86C8,Y / STA $0711,Y` for `Y=0..14` writes its 15
characters to `$0711`, which is **row 19, column 25** - columns 25-39 exactly.
Now drawn there, and the status line is back to 32 columns.

**The underlying divergence, still open.** The ROM's status template at `$7A10`
is a *single* 40-column line::

    : DAMAGE 00% IS ........,MORALE:........

The remake splits that into three lines (room/damage, status/morale, ALSO HERE),
which is why row 19 now has to be truncated at column 24 to make room for the
caption. Restructuring to the ROM's one-line form is the faithful fix and would
free the column budget properly.

**On "the text sizes look different":** the play screen renders in the game's own
charset at 8px per character *provided `out/charset.bin` exists* - it is produced
by `python -m alientools chars` and `__main__` silently falls back to SysFont at
`7 * scale` if it is missing. That fallback is a different size and would make
every line look wrong. Worth checking that file is present before reading any
future text-metric report as a layout bug.

## DISC-207 - the loader's BASIC source, and two animations rebuilt from it

**Found:** 2026-08-08, from the owner's description of the Green Valley screen.

**`MENU1.prg` is a BASIC program** and detokenises cleanly - it loads at `$0801`
and is 13,846 bytes. That had not been read before; the front-end animations
were reconstructed from screenshots and live captures. The listing settles them
outright, and it confirms the owner's description exactly on both counts.

### The spiral - one cell at a time, out then back

    150 W=7:REM ****SPIRAL****
    160 CM=55296:WD=40:VIC=53248:T1=39:T2=25
    200 FORQ=11TO1STEP-1:GOSUB220:NEXT      ; grow  innermost -> largest
    210 FORQ=1TO11:GOSUB220:NEXT            ; shrink largest  -> back to start
    220 UL=CM+Q+Q*WD : UR=... : LL=... : LR=...
    230 W=W+1:IFW>15THENW=0                 ; a new colour per ring
    240 FOR N=UL+1TOUR      : POKE N,W      ; top    left  -> right   |
    250 FOR N=URTOLRSTEPWD  : POKE N,W      ; right  top   -> bottom  | clockwise
    260 FOR N=LR-1TOLLSTEP-1: POKE N,W      ; bottom right -> left    |
    270 FORN=LLTOULSTEP-WD  : POKE N,W      ; left   bottom-> top     |

Each ring is drawn clockwise; what reverses on the second pass is the *sequence
of rings*, which is what reads as the sweep coming back down to where it began.
The remake had the 22 rings right but painted **a whole ring per frame**, so it
stepped rather than travelled.

Now one POKE per `_BASIC_POKE_S`. **1,804 cells x 6.10 ms = 11.0 s** - and 11.0 s
is the figure `_BASIC_POKE_S` was itself derived from by timing the real
animation. Counting the POKEs out of the listing and measuring the machine agree
to three figures, which is a good independent check on both.

### The CENTER ROUTINE - the name grows outward from its middle

    400 M=LEN(B$)
    410 IFM/2<>INT(M/2)THENB$=B$+" ":M=M+1
    420 FORN=1TOM/2
    440 PRINTSPC(21-N)LEFT$(B$,N);RIGHT$(B$,N);

`LEFT$` and `RIGHT$` are printed **adjacent**, starting at column `21-N`. So the
first and last characters appear together in the middle and are pushed apart as
more arrive::

    n=1  col 20   GY
    n=2  col 19   GREY
    n=3  col 18   GRELEY
    n=6  col 15   GREEN VALLEY

The remake instead blanked the middle of a fixed-width string
(`'G          Y'` -> `'GR        EY'`), which puts every letter straight into
its final position and merely fills the gap in. **Nothing ever moved** - a
visibly different animation, and the reason it did not look right.

`center_routine_step()` returns the visible string *and its column*, because the
column is half the effect.

### Worth noting for later

`MENU1.prg` also carries the MARQUIE border routine (lines 330-380) and the
loader's own screen setup. Anything still reconstructed from screenshots on the
front end should be checked against this listing first - it is primary source
that was sitting in `out/` unread.

## DISC-208 - the Green Valley name: white, a row higher, and it has a trademark

**Found:** 2026-08-08, from the owner running the build after DISC-207.

Three faults, all answered by `MENU1.prg` lines 300-311 and the sprite routine
at 3000.

### The text had vanished - my bug, from the same pass

`_blit_at` takes **unscaled** coordinates and applies `self._scale` itself.
DISC-207's rewrite passed `col * 8 * s`, so everything was scaled twice and the
name landed far off-screen. Nothing was wrong with the reveal logic; it was
drawing correctly into empty space.

### White, not green

    300 VT=13:B$="{05}GREEN VALLEY":GOSUB390
    310 VT=14:B$="PUBLISHING ":GOSUB390

`CHR$(5)` is PETSCII **white**, and PRINT's colour state carries over, so line
310 inherits it. Both lines were being drawn in `c64.GREEN`.

### One row too low

`430 PRINT CHR$(19);LEFT$(CUR$,VT-1)` homes and then emits `VT-1` cursor-downs,
so `VT=13` lands on **row 12** and `VT=14` on **row 13**. They were on 13 and 14.

### The trademark is a sprite

    311 CO=27:RO=14:CL=1:GOSUB3000
    3010 FORQR=832TO846:READ QT:POKEQR,QT:NEXT   ; 15 bytes at block 13
    3020 POKE53287,CL                            ; sprite 0 colour = 1 = WHITE
    3025 CO=(CO*8)+18                            ; -> 234
    3030 POKE53249,(RO*8)+40 : POKE2040,13 : POKE53269,1   ; -> 152, enable

Registers (234, 152) less the VIC field origin (24, 50) put it at screen
(210, 102) - a superscript riding the top of the PUBLISHING row. Its 15 DATA
bytes from line 10 render to **the same glyph as `_WELCOME_TM_SPRITE`**, so the
existing bitmap is reused.

### And a trailing space that matters

`B$="PUBLISHING "` keeps a trailing space: 11 characters, padded to 12 by line
410, so the routine runs **6** steps rather than 5. The reveal was one step
short, which also meant the "name is finished" gate the trademark hangs off
never fired.

**Lesson, repeating one from earlier today:** having found the primary source in
DISC-207, I transcribed the *algorithm* from it and then got the colour, the row
and an entire sprite from memory of the old code instead of reading the six
lines directly beneath it.

## DISC-209 - the WELCOME screen's build order, decoded from MENU1.prg

**Found:** 2026-08-08, from the owner's description of the `1 ALIEN / Q QUIT`
screen. Lines 600-720 give the whole sequence, and it confirms the report almost
exactly.

**Everything on this screen is drawn by the same CENTER ROUTINE** (`GOSUB 390`)
that the loader uses for the publisher name - including the box rules and the
underline, which are just strings of graphic characters. The only exception is
the menu itself.

    600  MM=9:PRINTCHR$(147):GOSUB330      ; CLR, then MARQUIE = the outer border
    610  VT=3  box top rule          -> row 2   GOSUB390
    620  VT=4  GREEN VALLEY PUBLISHING -> row 3 GOSUB390
    621  RO=4:CO=32:CL=1:GOSUB3000    ; the TM sprite -> screen (250, 22)
    630  VT=5  box bottom rule       -> row 4   GOSUB390
    640  VT=7  N$(1) WELCOME TO ALIEN -> row 6  GOSUB390
    650  VT=9  N$(2) FACE THE POWER OF THE UNKNOWN -> row 8  GOSUB390
    660  VT=10 N$(3) the underline    -> row 9  GOSUB390
    670  FORI=1TONM:PRINT... : 690 PRINT..."Q QUIT"   ; printed DIRECTLY
    700  VT=21 CHOOSE ONE OF THE ABOVE      -> row 20 GOSUB390
    710  VT=22 PLEASE LEAVE DISKETTE IN DRIVE -> row 21 GOSUB390
    720  VT=24 COPYRIGHT(C)1985 ALL RIGHTS RESERVED -> row 23 GOSUB390

`870/880/890 DATA` supply `N$(1..3)`; `895 DATA 1,15` gives `NM=1` (one numbered
option) and `HT=15`; `910 DATA 13,"ALIEN"` puts it at `TB(1)=13`.

**One correction to the report.** The text of "FACE THE POWER OF THE UNKNOWN"
(line 650, VT=9) is revealed **before** its underline (line 660, VT=10), not
after. Everything else - outer border, box rule, publisher name, WELCOME, then
the pair of menu lines appearing at once, then the two footer lines, then the
copyright - is exactly as described.

**`1 ALIEN` and `Q QUIT` do not use the routine.** Lines 670-690 `PRINT` them
straight out, which is why they appear whole rather than growing.

### Three different TM placements

All three go through the same sprite routine at 3000 with `CL=1` (white), and
all render the line-10 DATA glyph:

| screen | BASIC | registers | screen px |
|---|---|---|---|
| back-up notice | `556 CO=33:RO=18` | (282, 184) | (258, 134) |
| spiral / publisher | `311 CO=27:RO=14` | (234, 152) | (210, 102) |
| WELCOME | `621 CO=32:RO=4` | (274, 72) | (250, 22) |

The WELCOME one already matches `_WELCOME_TM_POS`. The back-up notice has one
too, which the remake does not currently draw.

**Action:** the sequence above is not yet implemented - `_draw_welcome` still
uses its own reveal model. Filed as the next front-end job.

## DISC-210 - the WELCOME reveal implemented, and a colour code that moves a whole line

**Found:** 2026-08-08, implementing DISC-209 and chasing the owner's "text is
slightly too large / no space before the TM".

### The WELCOME screen now reveals in the BASIC's order

`_draw_welcome` had the right *list* of nine elements in the right order, but:

- the publisher box was a `pygame.draw.rect` that appeared **whole** - lines 610
  and 630 are `GOSUB 390` calls, so it grows outward like everything else;
- the row-9 underline was painted in one pass - line 660 is a `GOSUB 390` too;
- every text line used `text_reveal_mask`, the fixed-position model DISC-207
  already replaced on the loader screen, so **nothing moved**;
- `1 ALIEN`/`Q QUIT` waited for "CHOOSE ONE OF THE ABOVE" to start, when lines
  670-690 print them *before* line 700;
- the ™ sprite drew immediately instead of waiting for the name it belongs to.

All five fixed. Verified by stepping the frame counter: border -> box top ->
name -> box bottom -> WELCOME -> FACE -> underline -> menu -> footers ->
copyright, each completing strictly after the last.

### The size complaint was a position bug, and a colour code caused it

The text is 8px per character and always was - the extra width in my first
measurement was the ™ sprite bleeding into the sampled row, since it sits at
y 102-107 and straddles rows 12 and 13.

The real fault: `300 B$="{05}GREEN VALLEY"`. Line 400 measures `LEN(B$)`
**including the `CHR$(5)`**, so a 12-character name behaves as 13 - line 410
pads it to 14, the loop runs **7** steps rather than 6, and `SPC(21-N)` lands
the text at column **14**. Line 310's `B$="PUBLISHING "` has no colour code and
stays at column 15 with 6 steps.

So the two lines really are a column apart on the real screen, and the remake
had them flush. Drawing the name one cell right also squeezed the gap before the
™ at `CO=27` (screen x 210) down to ~4px; it is now 12px, and step 1 of the
reveal correctly shows nothing at all, being just the colour code and the pad.

This is the third time today a leading PETSCII colour code has changed a
layout - `_center_routine_col` already existed for exactly this on the quit
advert (D-185). `center_routine_step` now takes `colour_code=True` rather than
each call site rediscovering it.

## DISC-211 - the box grew twice, and a speed knob that does not corrupt the measurements

**Found:** 2026-08-08, from the owner running the DISC-210 build.

### The publisher box animated twice - my bug

DISC-210 drove a single rectangle off `min(n_box_top, n_box_bottom)`. Those two
counters are **sequential**: the top rule completes, then the bottom rule starts
from zero. So the box grew to full width, collapsed to nothing the instant the
second counter ticked, and grew again.

The real shape is three separate things, because `610` and `630` are two
separate CENTER ROUTINE calls with the name (`620`) between them:

- top rule, revealed by `n_box_top`
- bottom rule, revealed by `n_box_bottom`
- the **side bars, which belong to line 620's own `B$`** and therefore arrive
  with the name, not with either rule

Drawn that way it cannot double-animate. Verified by sampling the top rule's
width every 4 frames across the whole reveal: monotonic, zero shrink events.

### 20% faster, applied where it cannot distort the data

`FRONTEND_SPEEDUP = 1.25` in `layout.py`, applied to the **frame counter** each
screen reads - never to the rates themselves.

That distinction is not cosmetic. The first attempt divided
`_TEXT_REVEAL_RATE` by 1.25: 6 frames / 1.25 = 4.8, which **rounds to 4** - 33%
faster, not 20%. Scaling the input keeps the ratio exact and leaves every
`[C-live]` constant saying what the machine actually did, so the drift guard can
still pin `_TEXT_REVEAL_RATE == round(_TEXT_REVEAL_STEP_S * _FRAME_HZ)`
unchanged.

Measured after the change: the loader screen settles at 10.9 s (was 13.6) and
WELCOME at 22.1 s (was 27.6). Both exactly 80%.

**One knob, one line to revert**, and the guard pins its value so it cannot
drift silently.

## DISC-212 - SCUTTLE NOSTROMO flashes the border, and it is blue XOR 1

**Found:** 2026-08-08, from the owner: *"Scuttle Nostromo makes the border flash
yellow in the original until the ship explodes or the self destruct is turned
off."* Correct, and the mechanism is a single `EOR`.

`mainloop_sub_5a26 ($5A26)` runs once per main-loop pass, ahead of the countdown
tick::

    5A26  LDA $64CF / BNE $5A2C   ; auto-destruct armed?
    5A2B  RTS                     ; no  -> leave the border alone
    5A2C  LDA $D020
    5A2F  EOR #$01                ; yes -> toggle bit 0
    5A31  STA $D020
    5A34  DEC $657C               ; ...then the countdown

**Why yellow.** `start_game` sets the play border to `#$06` BLUE (`$7054`), and
`EOR #$01` swaps `$06` to `$07` — yellow. The flash is not a colour the code
names anywhere; it falls out of toggling one bit of whatever the border already
is. On the front-end screens, where the border is black (`$4017`), the same
instruction would flash white.

**Stopping it.** `clear_result_flag ($58F6)` is the OVERRIDE DETONATION path:
it zeroes `$64CF` **and** writes `#$06` back explicitly (`$58FE-$5900`), so
cancelling always leaves the border blue rather than stranded on whichever half
of the toggle it happened to reach. Worth copying exactly — a naive
implementation that just stops toggling leaves it yellow half the time.

The other exit is `$5A43 JMP hull_breach`, when `$657B` reaches 0.

One option does both jobs: `$5855 LDA $64CF / BNE $585E` arms it when clear, and
takes the override branch when set — the override itself gated on `$657B >= 5`
(D-060), so you only get five of the nine units to change your mind.

**Action:** implemented as `PlayMixin._play_border`, keyed off `state.tick` so it
toggles once per **pass** (~7.9Hz) rather than once per frame (30fps).

## DISC-213 - the panel is fixed blocks, and ALIEN's font puts capitals at $80+

**Found:** 2026-08-08, from four screenshots the owner captured of the same two
situations in both builds, plus live colour RAM.

### 1. Capital letters live at `$80+`, lowercase at `$01-$1A`

The single fact behind every capitalisation difference. `$A65E` reads::

    A0 8F 12 04 05 12 1C   ->  " Order:"    $8F = capital O
    84 01 0C 0C 01 13      ->  "Dallas"     $84 = capital D, $01 = lowercase a
    8B 01 0E 05            ->  "Kane"       $8B = capital K

So in ALIEN's own charset **`$01-$1A` are lowercase a-z and `$81-$9A` are the
capitals** - the high bit selects case, not reverse video. The remake maps
`$01-$1A` to uppercase A-Z, which is why it renders `MOVE TO:` / `USE:` /
`SPECIAL:` / `QUIT` / `SHUTTLEBAY` where the original shows `move to:` / `use:` /
`Special:` / `quit` / `ShuttleBay`.

`quit` is stored at `$A715` as `$11 $15 $09 $14` - the same bytes read as "QUIT"
or "quit" depending only on which half of the font you index.

### 2. The CONTROL panel is fixed-height blocks

Both screenshots - **different rooms, different option sets** - show the
identical row layout, so the sections do not resize to their contents:

| rows | section | colour |
|---|---|---|
| 0 | crew name | LT GREY |
| 1-6 | MOVE TO: + destinations | LT BLUE |
| 7-9 | USE: | LT GREEN |
| 10 | GET / LEAVE ITEM | LT RED |
| 11 | rule | YELLOW |
| 12-14 | SPECIAL: + room options | PURPLE |
| 15 | quit | WHITE paper, black ink |

Live colour RAM (`$D800`, cols 30-39) confirms **every row carries a section
colour** - nothing is black. The remake painted one row per entry and left the
remainder black, which is why the panel looked "smashed together". Fixed;
SPECIAL was also LT RED (should be PURPLE) and QUIT LT GREY (should be WHITE).

### 3. Two regressions of my own, from the DISC-206 grille fix

- `MORALE:CONFIDENT` was being cut to `MORALE:C`. I had truncated the crew row
  at column 24 to make room for the grille caption. Both screenshots show the
  caption on the **room-and-damage** line ("CommdCentr : damage 00%   Grille in
  place"), not the crew line. Moved; truncation removed.
- `LEAVE ITEM` is **not** wrongly always-on - it is already gated on
  `crew.holding`. The remake screenshot shows `CAT BOX` under USE:, so that Kane
  really was carrying something. Different game state, not a rendering fault.

### Still open from this comparison

- The **deck plans are in the ROM** at `$A000`/`$A21C`/`$A438` (three 30x18
  templates, `$21C` apart, copied by `init_menu_ptr`/`init_ptr_menu2`/`3`). The
  remake uses VICE screen captures instead - DISC-206 called that its only
  capture dependency, and it turns out to be avoidable.
- The selected crew member's **portrait** sits at the bottom-left of the view
  window in the original; the remake places it higher and it collides with the
  status band.
- A **light grey bar** runs along the bottom of the view window.
- The bottom status bands are **taller blocks** in the original, not single rows.

## DISC-214 - RETRACTS D-131: the view does follow, and the deck table was the wrong table

**Found:** 2026-08-08. The owner reported it twice; the second time with the
symptom that settled it - *"they disappear from the screen and you have to quit
then select the crew member again to change deck views."*

### The deck plan follows the selected character

Every main-loop pass::

    4CC9  LDY $64FB / BEQ          ; someone is selected
    4CCE  LDA $7935,Y / STA $64F7  ; ...their room, right now
    4CD4  LDA $6501,Y / BEQ $4CE2  ; in a duct?
    4CD9  JSR select_menu_template ;   yes -> that deck's duct sheet
    4CE2  JSR menu_option_dispatch ;   no  -> the deck plan

and `menu_option_dispatch ($511C)` does `LDA $7569,Y` then calls
`init_menu_ptr`/`init_ptr_menu2`/`init_ptr_menu3` - each of which **copies a
30x18 deck plan into `$0400`** from `$A000`/`$A21C`/`$A438`. Those decode to
"UPPER DECK", "MIDDLE DECK" and "LOWER DECK".

**D-131 said the opposite**, and I re-confirmed it wrongly a few hours earlier
by reading `$511C` as only positioning sprite 0 from `$758D`/`$75B1` and
stopping before the `init_menu_ptr` calls three instructions above. It then
leaned on the manual - "EACH DECK OF THE SHIP CAN BE SELECTED FROM THE MENU" -
which describes the menu, not the only way the view changes. **A manual line
that is merely consistent with a reading is not evidence for it.**

### The deck table was never a deck table

Chasing it turned up the real cause of the vanishing crew. `gamedata.py` read
the per-room deck from `DECK_TABLE_ADDR = $80D3`, whose 4/5/6 values are the
**screen page** of the room's marker on the *duct* map (`$81C9 LDA $80D3,Y ->
$FC`). The deck index is `$7569`, values 0/1/2, which is what `$76BB` and
`$511F` actually read.

The two agreed for only **12 of 34 rooms**. So the remake put 22 rooms on the
wrong deck: walk a crew member through a door and they could leave the deck the
view was showing.

`gamedata.py`'s own module docstring has said this since D-116 - *"`$80D3` NOT a
deck table... the real per-room deck/screen index is `$7569`"* - and the code
never followed. The finding was written down and never applied, which is the
mirror image of the drift D-189 guards against.

**Independent corroboration.** A drift guard tolerated **two** rooms sharing a
marker spot on their deck, described as "what the ROM actually contains". With
the deck read from `$7569` the collisions drop to **zero**. The anomaly the old
mapping had to excuse does not exist in the real one.

### Knock-on: one table, two template sets

`$7569` indexes both the deck plans (`$A000`+) and the duct sheets (`$A956`+) -
one sheet per deck, one plan per deck. `test_there_are_three_sheets_and_they_are
_not_the_deck_plan` asserted the reverse, on the strength of that same bogus
12-of-34 comparison; it is now
`test_there_is_one_duct_sheet_per_deck` and checks the two indexes are the same
byte.

Five tests pinned the old model and were rewritten. Distribution is 9/16/9
rooms per deck, not 10/14/10.

## DISC-215 - the case bit, and two letters the game writes in at runtime

**Found:** 2026-08-14, first todo item: put the ROM's own capitalisation back.

### `_screen_char` was throwing the case away

`gamedata._screen_char` opened with `c &= 0x7F` and then mapped `1-26` to
capitals. That mask discards **exactly the bit that carries the case**: ALIEN's
charset holds lowercase a-z at `$01`-`$1A` and the capitals at `$81`-`$9A`. So
every string decoded out of the program came back shouting.

With the mask removed the tables read as the ROM wrote them::

    room names   'Airlock 1', 'Armoury', 'CargoPod 1', 'CommdCentr', 'Narcissus'
    morale       'confident', 'stable', 'uneasy', 'shaken', 'broken'
    status       'O.K.', 'wounded', 'collapsed', 'DEAD'   <- mixed on purpose
    panel labels 'move to:' ($A898), 'use:' ($A8DF), 'Special:' ($7CE2),
                 'Get item' ($82AA), 'Leave item' ($82B5), 'quit' ($A715)

`O.K.` and `DEAD` really are capitals while `wounded` and `collapsed` are not -
the decoder now reports that rather than flattening it.

Two production spots were spelling the words themselves instead of reading the
tables (`CrewMember.status`, `constants.MORALE_BANDS`); both now come from
`STATUS_WORDS`/`MORALE_WORDS`.

### "Lambe" on the disk, "Lambert" in RAM

`CREW_ORDER` was a hardcoded uppercase literal. Decoding it from `$A65E` - the
table a dozen `LDA $A65E,Y` sites read - gave `Dallas, Kane, Ripley, Ash,
**Lambe**, Parker, Brett`. `$A690` on disk really is `8C 01 0D 02 05 A0 A0 A0 A0
A0`: five letters, five spaces, while every other name is complete.

Live RAM read `...05 12 14 A0` - "Lambert". Diffing a 256-byte window of the
running machine against the file showed **exactly two differing bytes**, which
ruled out a bad sector, and the writer is three instructions long::

    4EC4  LDA #$12 / STA $A695      ; 'r'
    4EC9  LDA #$14 / STA $A696      ; 't'

So the disk stores "Lambe" and the code patches the "rt" in at startup. The
decoder now applies that patch, which is why `CREW_NAMES` ends up correct
without anything being hardcoded.

This also corroborates D-081 from the other direction: that entry recorded live
RAM holding "Lambert" at `$A690`, which looked like it contradicted the file
until the patch turned up.

**Note:** `$A65E` sits under BASIC ROM. The *file's* bytes are what gets loaded
into the RAM beneath it, so decoding from the PRG is right - but only after the
`$4EC4` patch, which no static read of the file can show you.


---

## DISC-216 - the deck plans were captures; the ROM has carried them all along

**Found:** 2026-08-14, second presentation-parity todo item.

The remake drew its three deck maps from `the live captures (not published)*deck_0400.bin` - screen
dumps taken out of VICE. D-022 had already located the real source three years of
passes ago and nobody wired it up: the templates live in the program at `$A000`
(Upper), `$A21C` (Middle) and `$A438` (Lower), 30 columns x 18 rows of screen
codes, drawn by `charpump_colorfill $7150`.

`gamedata.decode_deck_plan()` now reads them and `DECK_PLANS` is emitted into the
snapshot; `play._rasterize_codes()` blits the codes. The captures are retired as
*corroboration* rather than source - they agree cell-for-cell, which is the
evidence the decode is right.

**Why it matters beyond the pixels.** This was the last piece of *map* content
taken from a screenshot. A capture is a photograph of one machine at one moment;
if the remake and the ROM ever disagreed, there was no way to tell which was
wrong. Now there is.

**Action:** shipped. `the live captures (not published)*deck_0400.bin` are kept as regression
fixtures only - see the `[C $A000]` note in `gamedata.py`.

---

## DISC-217 - the status template is 42 bytes, and both its fields are 9 wide

**Found:** 2026-08-14, sixth and then fourth/fifth presentation-parity items.

**This entry supersedes its own first version, filed the same day.** That version
said the template was 40 columns with a 7-wide morale field, and right-anchored
the `,morale:` run to column 39 so "confident" would not clip to "confide". Both
halves were wrong, and the way they were wrong is the point: I checked my
arithmetic instead of the capture that was already in the live captures (not published).

### What `$7A10` actually is

`draw_control_panel_body ($79CD)` copies the template out in two pieces::

    $7A10 +$0C -> $0702   row 19 col 10   ": damage 00%"
    $7A1C +$1E -> $0752   row 21 col 10   " is <9>,morale:<9>"
    $070E fill $AE x $3A  row 19 col 22 through row 20
    $0770 fill $A0 x $28  row 22

42 bytes, not 40, and **both fields are 9 wide** - exactly "collapsed" and
exactly "confident", the longest word each can hold. Nothing overruns, nothing
needs anchoring. A 40-column reading loses precisely the last two bytes, which
are the tail of the morale field, so it is wrong in the one place that shows.

A 10-column name goes at column 0 of rows 19 and 21 (`copy10_ptr`).

### The rest of the bottom panel, from the same pass

- **`paint_map_colors ($7993)`** colours rows 18-24 in one loop, 40 columns wide,
  and the bands are **two rows tall**: `$0F` row 18, `$0D` rows 19-20, `$08` rows
  21-22, `$07` rows 23-24. The remake stacked one row per line of text from row
  18 down - three thin stripes where the original has blocks.
- **`$79B7`** fills row 18 with `$A0` for **30** cells, so the light grey stops
  at the edge of the view window and the CONTROL panel keeps columns 30-39.
- **`$7E82`** writes `"also here:"` (`$7EDB`, lowercase) to row 22 column 0, then
  co-occupant names at columns 11, 22 and 30. D-117 recorded that "ALSO HERE"
  appears nowhere in `ALIEN.prg` and the label might be invented - it was
  searching for the shouted form. It is there.
- **`draw_damage_warning ($55C9)`** copies "WARNING:" to **`$07C0` = row 24 col
  0** - the *same address* as the Jones notice (`$890C`, D-149). Row 24 is the
  ROM's one shared notice line, which is why row 23 is blank in every capture.
- The grille caption's `$0711` is row **19**, not row 18.

### The trap that caused the first version

`narcissus_0400.bin` is **1002 bytes**: the captures carry a 2-byte load address.
Reading one without skipping it shifts every column by two, which is what made
the layout look off-by-two and sent me to arithmetic for a tie-break.

And `$AE` decodes as `.` but **renders blank** (D-078 / P-7) - this charset has
no period glyph - so the template's "dotted" fill draws as solid band. The dots
in a text dump are not on the screen.

**Action:** shipped. `bottom_panel_rows()` in `render/play.py` is now compared
against `narcissus_0400.bin` row-for-row by a test, rather than against my own
reading of the template. `STATUS_TEMPLATE` is decoded by `gamedata` instead of
retyped. The `[?]` the first version filed - where a 6-letter morale word sits -
is **closed, not open**: the field is 9 wide and left-aligned, so it sits at
column 31 like every other word.

---

## DISC-218 - the notice screen was laid out by feel; MENU1 gives every column

**Found:** 2026-08-14, last of the presentation-parity todo items ("the back-up
notice has a TM sprite the remake does not draw").

The trademark *was* drawn - the todo was stale on that point - but it was placed
by paragraph flow, off the right edge of whichever line happened to be fifth. The
original places it as **sprite 0** at coordinates its own BASIC computes.

### `GOSUB 3000` is the sprite routine, and it is pure arithmetic

    3025 CO=(CO*8)+18 : IF CO>255 THEN CO=CO-256 : POKE 53264,1
    3030 POKE 53248,CO : POKE 53249,(RO*8)+40 : POKE 2040,13 : POKE 53269,1

Sprite coordinates count from the border, so the visible-screen position is
`(x-24, y-50)`. Line 556 sets `CO=33 : RO=18`, giving **(258, 134)**.

What makes this trustworthy rather than plausible: the same two lines reproduce
the *other* two call sites exactly - line 311 gives (210, 102) and line 621 gives
(250, 22), both of which D-064 had read off the running disk. Three call sites,
one formula, no fitting.

### The paragraph was never a block

A shared helper left-aligned all seven lines at one x, citing a live capture for
"the real NOTICE screen is a clean left-flush block". Lines 505-555 each carry
their own indent - **9, 7, 8, 8, 13, 9, 7** - and `boot_015_notice.png` shows
that ragged edge plainly: "in a safe place." sits four columns in from its
neighbours. The claim did not survive looking at the screenshot it cited.

Rows come from the `PRINT`s themselves: each opens with two cursor-downs and ends
with a newline, so they step by three from row 2 - **2, 5, 8, 11, 14, 17, 20**.

### The footer has a rule the capture appears not to show

Line 560 prints 25 cells of PETSCII 164 on row 22, then 565 prints the reverse
prompt on row 23, both indented 9. Nothing is visible above the prompt in the
capture - because screen code `$64` in the **shifted** bank is a single row of
pixels at the *bottom* of the cell, so the rule sits flush against the top of the
prompt's yellow block and reads as part of it.

**Action:** shipped. The helper is deleted rather than left unused - its
docstring was the only place the left-flush claim survived.

---

## DISC-219 - the portrait was never misplaced; two captions were still shouting

**Found:** 2026-08-14, closing the last presentation-parity todo item.

### The portrait

Reported as "sits at the bottom-left of the view window in the original; the
remake draws it higher, where it collides with the status band". It does not.
`place_selected_char_sprite ($6667)` puts sprite 2 at VIC `($1C, $A9)`, which is
screen `(4, 119)` once the (24, 50) sprite origin is taken off, and that is what
`_CHAR_PORTRAIT_AT` has always held. A sprite is 21 rows tall, so it ends at 140
- inside row 17, clear of the band that starts at row 18.

**Why it looked absent.** `$D029` takes the sprite's colour from the character's
duct flag (`LDA $6501,Y / STA $D029`): **0 - black - while they are in a room**,
1 - white - while crawling the ducts. Against the deck plan's green field a black
portrait reads perfectly, which is exactly what `narcissus room.png` shows. Draw
it against a black field and it disappears.

That is what a renderer built **without a tileset** does: `_backdrop_surface`
returns `None`, the deck plan falls back to a placeholder grid of outlines on
black, and the portrait is black-on-black. Rendering the same frame *with*
`out/charset.bin` puts both the plan and the portrait exactly where the original
has them.

**No code change.** A test now pins the position, the 21-row clearance and the
two colour indices, so the next "it's in the wrong place" report has an answer.

### Two captions the case fix missed

DISC-215 restored the ROM's capitalisation across the decoded tables but not
these three, which are hardcoded in the renderer and the menu::

    86C8  87 12 09 0C 0C 05 A0 09 0E A0 10 0C 01 03 05  "Grille in place"
    86D7  87 12 09 0C 0C 05 A0 12 05 0D 0F 16 05 04 A0  "Grille removed "
    86E6  92 05 0D 16 87 12 09 0C 0C 05                 "RemvGrille"

The remake had "GRILLE IN PLACE" / "GRILLE REMOVED" / "REMVGRILLE". The caption
was also drawn light grey on the default background while sharing row 19 with
text drawn in the band's colours - two different colours on one line, where the
ROM colours the whole row `$0D`.

**Action:** shipped, with the decoded bytes pinned in a test.

---

## DISC-220 - the opening notice's colours were already right; its text was shouting

**Found:** 2026-08-14, from a play report asking for "green background with
white text" (currently black).

### The colours checked out against a fresh live capture

Re-verified directly against the running original disk rather than trusting
D-145's old recording on its own: paused right after `sub_5049`'s `JSR` returns
(`$7054`), then read registers and memory in the same frozen moment.

    $D021 = $F5   (low nibble 5 = GREEN, the background)
    colour RAM, row 19: uniformly $00 (BLACK), every message cell

That is green paper, black ink - exactly D-145's finding, and exactly what
`_draw_opening` already draws. The report doesn't hold up. **No colour change.**

A first attempt at this capture (a live screenshot taken moments after selecting
Full Game, not a frozen single-stepped one) showed the message sitting on a
light-grey/light-green *banded* background instead of solid green, which looked
like a real discrepancy worth chasing. It was a timing artifact: `paint_map_colors
($7993)` runs *after* `sub_5049`, and repaints colour RAM for the status rows
into the per-band scheme DISC-217 already documented - while the message's
screen-RAM glyphs are still sitting there, unerased, until the first real status
refresh a moment later. The message is drawn once, correctly, and then visually
inherits whatever colour RAM the *next* screen state paints under it, for the
brief window before it's overwritten. Nothing wrong with the draw; the game
just moves on fast.

### The text was shouting, for two stacked reasons

While decoding the message straight from screen RAM to check colours, the text
itself came back wrong: `$0701` decodes to `" has been killed by the ALIEN"` -
lowercase, "ALIEN" excepted (its bytes are `$81 8C 89 85 8E`, capitals per
DISC-215's high-bit rule). The code had `" HAS BEEN KILLED BY THE ALIEN"`.

**Reason one: a stale capture.** `tools/vice-mcp/opening_row19.json` -
`" +??E?%,? HAS BEEN KILLED BY THE ALIEN"` - was captured and decoded *before*
DISC-215's case-bit fix, so its all-caps reading is the old decoder's artifact
baked into a JSON file, not the ROM's bytes. The code had copied that stale
capture's casing rather than decoding the live bytes.

**Reason two, and the one that actually mattered: wrong font entirely.**
Lowercasing the Python string alone changed nothing on screen, because
`_draw_opening`'s two `_blit_cells` calls didn't pass `c64_font=True` and so
silently used `_blit_cells`'s default - the loader's standard chargen ROM in
its **unshifted** bank, which has no lowercase glyphs at all (D-047/D-065).
Every letter renders as a capital regardless of the string's case in that bank.

`_draw_opening`'s own docstring already says the notice "sits on the SELECTION
screen's own cleared field" - and `_draw_selection`, right above it, draws its
text through ALIEN's own **cut-out charset** (`c64_font=True`, the default for
`_c64_or_sysfont`), not the loader font. The garbled-name half of the same
screen (`_blit_codes`) already used ALIEN's charset correctly; only the message
half took the wrong path. `_blit_cells` gained a `c64_font` parameter (default
False, preserving every genuine loader-screen caller) so `_draw_opening` could
opt in explicitly, matching its neighbour.

Same class of miss as DISC-219's "Grille in place" either way - DISC-215 fixed
the *decoder*, but every string hand-transcribed from a capture taken through
the old decoder, or drawn through the wrong font path, stayed wrong until
something re-checked it against the ROM. The `.upper()` fallback for an
un-garbled name was corrected alongside it.

**Action:** shipped. Colours pinned by a test so the next "wrong colour" report
has a fast, cited answer; the message text corrected and pinned against the
decoded bytes directly; a second test pins that `_draw_opening`'s text calls
use `c64_font=True`, so a future refactor can't silently drop back to the ROM
font and reintroduce all-caps.

---

## DISC-221 - the SCUTTLE flash silently disabled the fire-key border rainbow

**Found:** 2026-08-14, player report: "the noise in the border when pressing
fire has stopped appearing. This was working fine previously."

### The regression

`_present(border)` only ran the `wait_keypress_flash ($8660)` border-noise
effect when `border is None` (`pygame_app.py`). That was fine when the play
screen called `_present()` with no argument, always blue by default. DISC-212
changed that: SCUTTLE NOSTROMO's blue/yellow flash needed the border colour to
vary per tick, so the play screen's `render()` was changed to call
`self._present(self._play_border(state))` - and `_play_border` **always**
returns a concrete colour (blue normally, blue/yellow while scuttling), never
`None`. From that commit on, `border is None` could never be true on the play
screen again, so `_border_flash` - armed every time the player presses fire -
was checked, decremented, and then silently ignored every single frame. Nothing
failed loudly: the branch just stopped being reachable.

### Why it's safe to just drop the `None` check

The two effects never overlap in the ROM. `wait_keypress_flash` blocks the main
loop while it spins on `INC $D020`, waiting for a keypress - and
`mainloop_sub_5a26` (the scuttle toggle) only runs *from* the main loop. So
whenever the fire-key flash would be running on real hardware, the scuttle
toggle provably isn't ticking. Prioritising `_border_flash` over whatever
`border` value was passed reproduces the ROM's actual serialization rather than
inventing a priority rule.

**Action:** `_present` now checks `_border_flash` unconditionally. A test calls
`_present` the way the play screen actually does - with a concrete border
colour, not `None` - so this can't regress silently again the way it did the
first time.

---

## DISC-222 - the VICE launcher has been running with WarpMode on the whole time

**Found:** 2026-08-14, mid-investigation of Jones's move cadence. Tried to
confirm the ~40-tick / ~5-second move interval by polling `$657D-$657F`
across a `sleep`, and the numbers made no sense for real time. Checked
`vice.machine.config.get` directly: `"WarpMode":1`, during actual gameplay,
not just at boot.

### The rule this breaks

The standing project rule is explicit: **never enable WarpMode - it
invalidates every timing measurement.** `start-vice.ps1` had `-warp` on the
command line anyway, with a comment claiming "boots fast; the game itself is
paced by the emulator once running" - i.e. the assumption that WarpMode only
speeds up the boot and then gets out of the way. That assumption was never
checked against the actual VICE resource, and it is false: `-warp` sets
`WarpMode=1` for the life of the process, boot and gameplay both, until
something explicitly clears it.

### Why this matters beyond today

Every run that launched VICE through this script - not just this one -
has been running with the clock lying about itself, for every check that
didn't independently count cycles. It does **not** retroactively cast doubt
on `MAIN_LOOP_HZ` (D-063/D-075): that measurement used an execution
checkpoint counting *emulated cycles between two hits*, which is immune to
warp by construction (the citation says so explicitly - "counting emulated
cycles rather than wall time makes it immune to host latency"). It **would**
cast doubt on anything that used `sleep`-then-poll against wall-clock
assumptions, which is why this pass's Jones-cadence check was abandoned
rather than reported.

### The fix, and its limit

`-warp` removed from the launcher; a comment there now documents why not to
add it back, and where to toggle it explicitly instead if boot time is ever
worth trading away again. **This does not fix the VICE instance already
running** - `vice_machine_config_set` rejects a well-formed
`{"resources": {"WarpMode": 0}}` with "Missing or invalid 'resources' object"
regardless of how the value is encoded (object, JSON string, via the
`tools_call` passthrough), even though `vice_machine_config_get`'s own
`resources` block is exactly that shape. That looks like a bug in the MCP
server's own argument validation, not a usage error on this end. Restarting
VICE (now warp-free by default) is the only way to actually clear it.

**Action:** launcher fixed for every run after this one. This pass's
VICE process is still warped; no further wall-clock-timed live-oracle checks
should be attempted against it without restarting the process first.

---

## DISC-223 - Jones's movement and catch odds are already faithful; two small fixes

**Found:** 2026-08-14, player report: "Jones is hard to capture. Can you check
the cat's movement against the original code?"

### Re-verified byte-for-byte against the disassembly

`_advance_jones` ($88AB/$8971) and `_catch_jones` ($8787-$880E) were already
carefully cited (D-153, D-156, D-160). Re-derived independently rather than
trusting the citations alone:

- **`JONES_MOVE_TICKS = 0x28`** matches `$88B6 LDA #$28` exactly - he moves
  once every 40 main-loop passes, not the "5" the top-of-file timing summary
  in `constants.py` still claimed (see below).
- **`JONES_CATCH_THRESHOLD`** decoded fresh from `$883C,Y` (`00 0E 0E 0D 0D 0D`
  for Y=0-5) - and the two extra bytes the constant carries at index 6-7 (`0F
  0E`) are real: they're the first two characters of the *following* string
  ("on sees Jones is here..."), not table data, but the ROM genuinely reads
  them for a 6th/7th crew member's threshold. `JONES_CATCH_THRESHOLD`'s own
  comment already says as much ("index 0 is the Alien's slot and unused") -
  this is a faithfully-reproduced ROM data-packing quirk, not a remake bug.
- **Catch odds are consequently genuinely low without a net** (thresholds
  13-15 of 16 -> 6-19% per roll; the net's -4 bonus brings it to 31-44%), and
  `_jones_timer = 1` on any grab attempt - hit or miss - forces him to move on
  the very next tick. One shot per encounter is the design, not a bug.

### Two things that were actually wrong, neither of them the report

- **`_catch_jones` reimplemented the slot lookup** (`list(self.state.crew)
  .index(crew_id) + 1`) instead of calling `_slot_of`, the established,
  verified helper every other per-character table ($4032, $403A, D-166) goes
  through. Agreed by coincidence today (`default_crew` happens to build the
  roster dict in `CREW_NAMES` order) but had no structural reason to keep
  agreeing. Now calls `_slot_of`.
- **`constants.py`'s Jones timing comment was stale**, still citing the
  pre-D-153 "walks every 5" figure (`JONES_WALK_TICKS`, explicitly marked dead
  a few lines further down in the same file) instead of the real
  `JONES_MOVE_TICKS = 40` that superseded it.

### What this investigation actually found (DISC-222)

Chasing a live-oracle confirmation of the 40-tick cadence surfaced that this
project's VICE launcher has been running with `-warp` on continuously - filed
separately as DISC-222, since it matters far beyond Jones. No wall-clock live
check of the movement rate was completed this pass as a result; the
verification above is static (disassembly + decoded constants), which the
warp bug does not affect.

**Action:** two fixes shipped and pinned by tests; no gameplay-affecting
change to Jones's difficulty, because nothing wrong with it was found.

---

## DISC-224 - four Alien/opening-death reports, one real bug and three faithful mechanics

**Found:** 2026-08-14, player report: "Why does Brett or Lambert die every
time I play? Why does the Alien seem to move faster and faster? It
occasionally attacks a crew member and then moves out of the room. It also
doesn't appear to ever go down the ladders."

### 1. Lambert dying every time - real bug, fixed

`DeathVariant`'s own docstring already settled this back in D-170/PV-20:
`$64C2`, the opening-victim slot, has exactly **two** writers in the whole
image - the randomised pick at `$5071`, and the SHORT scenario's fixed pin to
KANE (`$6064`, a different mechanic entirely). No third path exists.
**RANDOM is the ROM's only real FULL-game behaviour**; `DeathVariant.FIXED`
was kept "only as a remake testing aid... explicitly not a fidelity claim."
`GameFlow`'s own default was already `DeathVariant.RANDOM`, correctly.

But `__main__.py`'s argument parser defaulted `--death` to `"fixed"` anyway,
and called it "the canonical casualty" in its own help text - so a player
running the game with no flags, the ordinary case, got Lambert dead at the
opening **every single time**, with the CLI's own wording actively asserting
that was correct. Fixed: `--death` now defaults to `"random"`, and the help
text explains why in the same terms `DeathVariant` does. A test mocks
`default_simulation` to confirm a flag-less run passes `DeathVariant.RANDOM`.

(Brett is never a candidate for the *opening* death either way -
`OPENING_VICTIM_CANDIDATES = ("dallas", "kane", "lambert")`, `[C $50EC]` - so
"Brett dies every time" is a separate, mid-game observation; nothing in this
pass found a targeting bias toward any one crew member in `_resolve_surface_
action`'s victim pick, which draws from whoever is actually co-located.)

### 2. The Alien speeding up over time - faithful, not a bug

`_roll_hunt` (`$4C9C-$4CB8`) is an aggression accumulator that grows with the
Alien's **cumulative damage** (`aggression += damage // AGGRESSION_DAMAGE_
DIVISOR`, capped at 15) and drives the probability of a faster "hunting" turn
(`ALIEN_PURSUIT_TICKS`, shorter than the normal `ALIEN_MOVE_TICKS`). Damage
only accumulates - there is no healing - so the longer a game runs and the
more the crew fights back, the more often the Alien hunts. A player
genuinely observing it "get faster and faster" over a long pass watched
this working correctly, not a runaway bug: it is designed to ratchet up, and
it does not reset.

### 3. Attack-then-leave - already fixed (D-188), verified still in place

Traced `advance_alien`'s encounter branch (`$8AE1 JMP $413C`) directly: a
successful surface-action encounter sets `alien.timer = ALIEN_ENCOUNTER_
HOLD_TICKS` (40, ~5s) and returns **without** falling through to
`_begin_action`, matching the ROM's own `JMP` (not `JSR`) into the encounter
handler. This is precisely the bug D-188 already fixed - "the remake fell
straight through to `_begin_action` and chose a new destination on the same
pass, so it hit someone and immediately walked out - exactly what the player
reported" - and the current code does not have that shape. If this is still
observed, it needs a fresh report with a repro, since the code inspected here
looks correct; a strong candidate for what's actually being seen is the hold
simply being short (~5 real seconds), which can read as "left immediately"
to a player not consciously timing it.

### 4. "Never goes down the ladders" - mechanically correct, structurally rare and invisible

Checked the real ship graph directly: of 36 door edges, exactly **2** cross
decks (`cargopod_2`<->`corridor_2`, `corridor_1`<->`livng_qtrs` - the two real
ladders). Checked `ALIEN_ROUTES` (the same table `_route_band`/`_surface_
dest` uses for the Alien's own moves, not `surface_move_targets`'s crew-menu
builder) directly at those four room indices: the cross-deck destination
**is present**, at a real roll band (`table1`, roll 3-4, or `table4`, roll
9-11 - a 2/16 to 3/16 chance), with no self-reference-termination logic or
other gate in the Alien's picker that would block it.

So the mechanism is intact. What makes it look absent: only 2 of 34 rooms
connect decks at all, the Alien has to actually wander into one of those two
specific rooms first, *and* - separately, deliberately, and already covered
by an existing test (`test_alien_is_never_drawn_on_the_map`) - **the Alien is
never drawn on the map at all**, matching the source game. A player has no
way to directly watch it cross a ladder even when it does; the only signals
are combat locations and tracker readings, both intermittent. A genuinely
low-frequency, invisible event reading as "never" over a normal playthrough
is the expected experience of correct code here, not evidence of a bug.

**Action:** #1 fixed and pinned; #2/#3/#4 investigated and left unchanged -
each traces to a specific, correct routine, and two (#3, #4) point at
existing prior fixes/tests rather than new problems.

---

## DISC-225 - ALIEN's cut-out font had inverted ink/paper polarity in one render path

**Found:** 2026-08-14, player report: "the death screen should show black text
on a green background... it's swapped."

The colours passed were already correct - confirmed again, this was purely a
*rendering* bug, not a colour-value bug. `_render_c64_text` (`pygame_app.py`)
painted `fg` at the glyph's **1-bits**. ALIEN's charset is cut-out - the
letter is the **0-bits** (`_blit_codes` already had this right, with the
comment to prove it: "cut-out font: the 0-bits are the ink"). Verified by
rendering `out/charset.bin` both ways against `the live captures (not published)
narcissus_0400.bin`'s actual bytes and comparing to the known-correct decode:
the 0-bit reading reads as "Narcissus : damage 00%"; the 1-bit reading is the
same glyph shapes in the complementary colour, i.e. a solid ink-coloured block
per letter with a paper-coloured letter-shaped hole in it.

**Why nothing looked wrong until now.** Every existing caller happened to
pass its `(paper, ink)` pair into `(fg, bg)` - swapped from what the
parameter names say - and `_c64_or_sysfont`'s SysFont fallback had a matching
special case ("in-game callers pass (paper, ink)... `bg` shows through as the
letters") that assumed the same swap. Two compensating "bugs" plus a caller
convention that had been hand-tuned around both meant every screen that
supplied a `bg` looked right by accident. The only path with nothing to
cancel against is the transparent/colorkey one (`bg=None`) - and the opening
death notice's message text landed there for the first time this pass,
when DISC-220 moved it from the loader's ROM font onto ALIEN's own charset
without a compensating `bg`. That is the "swapped colours" the player saw:
each letter rendered as a solid black block with the letter shape showing
green through a hole, not thin black strokes on green.

**Action:** fixed at the source - `_render_c64_text` now paints the 0-bits,
and the SysFont fallback's special case is deleted (unnecessary once the
base function is correct: `fg` is simply the ink everywhere, `bg` the
optional fill, matching `_render_rom_text`/`_blit_codes` already). Every
caller that had been passing `(fg=paper, bg=ink)` to compensate is corrected
to natural `(fg=ink, bg=paper)`: `_draw_menu_panel`'s cursor row, both status
rows and the notice/grille caption lines in `play.py`, and `_draw_selection`'s
name labels and menu text in `frontend.py`. `_draw_opening`'s two calls
needed no change - once the base function was fixed, the no-`bg` path became
correct on its own, which is what actually reproduced the report. Re-rendered
and visually re-verified: the opening notice, the selection screen and the
play screen's status area all still read correctly after the swap. Pinned by
a test that paints a space and a letter and checks which one paints nothing.

---

## DISC-226 - every sound cue played twice, one frame apart

**Found:** 2026-08-14, chasing "the movement sound is faster and faster,"
which the player specifically reported happening with the crew standing
still. That ruled out DISC-225's "no cooldown + many crew moving" explanation
outright, so the earlier answer was wrong and this dug further.

### The bug

`run_app`'s play-screen branch (`app.py`) drains and clears `sound_cues` once
per frame, *before* checking whether this frame is also a tick boundary -
D-187's own fix for D-186's silent-cue bug (an order's cue, raised during
input handling, would otherwise be thrown away by `advance()`'s own
`sound_cues.clear()` before ever being played). When the frame **is** also a
tick boundary, `advance()` repopulates `sound_cues` for this tick and a
second `play_sound_cues` call plays them - but nothing cleared them
afterward. They sat there until the drain step at the **top of the next
frame** played the exact same cues again, only clearing them then.

Confirmed directly: a scripted `run_app` pass with a fake renderer logging
every `play_sound_cues` call showed every non-empty cue set appearing on two
consecutive frames, back to back - `(165, ('attack_alert',))` immediately
followed by `(166, ('attack_alert',))`, and so on for every single cue the
whole run. Not occasional, not accumulating - a clean, total, unconditional
double-play of every movement blip, attack siren and grille burst, for the
life of the pass.

### Why this produced exactly the report

Crew standing still doesn't matter, because the bug fires on *any* cue,
Alien-only included - and DISC-225 already established the movement blip
gives no indication of who moved. A doubled blip on every genuine Alien
step, with nothing on screen to check it against (the Alien is never drawn),
reads exactly like "the alien is moving twice as fast as it should" even
though the underlying tick rate was always correct - confirmed static: 42
room-changes over a simulated 10 minutes, none faster than 7.6s apart, both
before and after this fix (the bug is entirely in playback, not in `Simulation
.advance()`).

### The fix

One line: clear `sound_cues` immediately after the tick-boundary
`play_sound_cues` call, matching the drain step already directly above it.
Re-ran the same instrumented session after the fix: 9 plays instead of 18,
same tick numbers, each cue exactly once. A test drives `run_app` with a
1-real-second-per-frame clock (so every frame is a tick boundary) and asserts
no two consecutive frames play the same non-empty cue tuple; confirmed to
fail against the pre-fix code with `frame 1 and 2 both played
('attack_alert',)`.

---

## DISC-227 - RemvGrille and Attack share one screen buffer, and stacked instead

**Found:** 2026-08-14, player report: "the Attack option randomly appears if the
crew member is standing in Corridor #6," plus a detailed panel-layout report
(colours, fixed bands, "quit" always at the bottom, "there shouldn't be any
black at the bottom of the menu").

### The real cause

`draw_grille_option ($86F0)` and the attack-encounter trigger (`$8CD9`-`$8CE1`)
both write their 10-character label into **`$064E`** - the same screen buffer
DISC-213 already established every SPECIAL row is drawn from. The ROM can
therefore only ever show *one* of RemvGrille or Attack at a time; it is a
single cell, not a list. `_special_entries` used to `append` both
independently whenever their conditions both held (a closed grille AND a
co-located Alien) - which is exactly Corridor 6's situation often enough to
notice, since the grille and the Alien's route-table traffic both pass through
it. Stacking two rows the original never shows together also pushed every
row below them down by one - a second, compounding source of the "the panel
looks wrong at the bottom" reports.

**Fixed:** Attack now wins when both conditions hold - its write is the
fresher, real-time event (`$8CD9` fires as the encounter itself starts), so
it is the later writer to `$064E` in the ROM's own execution order. RemvGrille
shows only when Attack doesn't contest the row. Pinned by a test; confirmed to
fail against the old (both-appended) code first.

### Investigated, not yet fixed - real gaps found

The same play report raised several more items, checked against the
disassembly. Confirmed real, not yet implemented:

- **"MOTHER REFUSES LAUNCH" / "GO GET JONES" are never shown.** `_launch_
  narcissus` correctly implements the refusal *logic* (D-152/D-153 already
  traced it in full) but only returns a bool - `$5B80`/`$5C33`'s actual status
  text is never surfaced anywhere in the renderer.
- **The android reveal has no visual tell.** `_reveal_android` correctly sets
  `state.locked_crew_id` (D-165's `$D021` background-flash citation is right
  there in the docstring), and `menu.py` correctly gates crew selection on it
  - but nothing in `render/` ever reads `locked_crew_id` or `android_revealed`
  to actually flash anything. The mechanic works; it's invisible.
- **FIGHT FIRE's "Fire Out" confirmation is never shown.** `$5889`'s own
  citation in `_fight_fire` already documents "show 'FIRE OUT  ' ($5950)" as
  the last step; the remake correctly clears the alarm (so the option
  disappears) but never displays the confirmation text itself.
- **The hull-breach ending has a real, dedicated ROM animation
  (`hull_breach $5D17`, via `animate_fill_row`) that the remake does not
  implement at all** - `_draw_end` has no reference to it. A pure hull-breach
  loss (crew still alive) currently shows minimal/no distinguishing text or
  effect, unlike the "eggs unleashed" or "Alien killed" endings, which do have
  dedicated screens.
- **The USE: section's real row budget is 3 rows (7-9), not 1** - "use:"
  header plus **two** content lines. `crew.holding` is a single item, so the
  remake can only ever populate one of those two lines; whether the original
  really lets a character hold two items at once, or whether the second line
  serves some other purpose, is unresolved and needs disassembly of the
  actual USE: item-list builder, not just the panel's static row table.
- **`_PANEL_VISIBLE_ROWS` (17) exceeds `_PANEL_SECTIONS`'s defined range (16
  rows, 0-15).** DISC-213 confirmed via live colour RAM that the real panel
  is exactly 16 rows with `quit` on the last one; sharing a wider 17-row
  window (sized for the unrelated INDICATE LOCATION room list, per an older
  P5-8/D-133 justification) with the crew-order menu means a long-enough
  entries list can push content into an undefined 17th row that nothing ever
  paints - a second possible source of "black at the bottom," separate from
  the DISC-227 stacking above. Not yet fixed; needs its own scoped pass rather
  than a rushed shared-constant split.

### Checked and NOT bugs

- **USE: really is light green, not yellow.** DISC-213 verified this directly
  against live colour RAM (`$D800`, cols 30-39), not a guess. Left unchanged;
  a repeat live capture would be needed to overturn it, not another report.
- **Attack not showing for a second crew member in the same room as an
  ongoing encounter is correct, faithful behaviour**, not a bug: the attack
  siren/animation is gated on `$8CE1 CPY $64FB` in the ROM - selection-based,
  not room-based - while the "Attack" *menu option* is a room-based check.
  Both are right; they answer different questions ("is the Alien here" vs.
  "are you currently watching this character").
- **"ENVIRONMENTAL IRREGULARITIES"** is the already-decoded LIFE SUPPT
  malfunction message (`MALFUNCTION_MESSAGES[5]`) - working as designed.
- **"Fight Fire" appearing only in a burning engine room** is already
  correctly gated on `room_fire`, matching `$55A9-$55B3`.

### Brett's starting room - re-verified, still Airlock 1; likely explanation offered

Re-derived the `$793D` static template byte-for-byte, this time with the loop
bound confirmed directly (`65FD LDY #$00` ... `CPY #$08`, 8 iterations,
matching `$7935` slot 0 == the Alien per two independent existing citations).
Result: Y=0 (Alien) = airlock_1, Y=1-3 (Dallas/Kane/Ripley) = commdcentr,
Y=4-6 (Ash/Lambert/Parker) = mess, **Y=7 (Brett) = airlock_1** - matching
D-125, not the older, contradictory D-014 "3+3 skip the dead" reading, which
this pass's re-derivation cannot reconcile with the actual template bytes.

A live boot attempt to settle it outright was inconclusive (the running VICE
process is still warp-affected per DISC-222 and a stray input during the
attempt advanced the game to its ending before a clean read completed).
Offered explanation, not yet confirmed live: Brett starts in Airlock 1 next to
the Alien and is consequently very likely to panic-flee before a typical
player's attention reaches him. His only real door neighbour is Corridor 6,
and Corridor 6's own route table includes Mess (`table0: corridor_6 -> mess`)
- so a fled Brett reaching Mess within one or two moves is plausible and would
read as "usually starts in Mess" without his true starting room ever having
changed. This needs a clean (non-warped) live boot to confirm outright; filed
as a follow-up rather than asserted as settled.

---

## DISC-228 - Brett's start room settled live; the remake cannot reproduce his escape

**Found:** 2026-08-14, the owner directly corrected DISC-227's Brett/Airlock-1
finding as wrong from repeated play, plus "Lambert is always the dead crew
member" as a second, separate correction.

### Lambert: re-verified thoroughly, no bug found in the mechanism itself

Ran `default_simulation` 60 times: `Counter({'dallas': 22, 'kane': 20,
'lambert': 18})` - genuinely uniform, not biased toward Lambert. Traced the
full call chain (`__main__.py`'s `--death` default -> `GameFlow.death_variant`
-> `choose_opening_death`) and found only the one construction site, correctly
wired. Checked `play.bat` - passes arguments through unchanged, no hardcoded
override. **Could not reproduce "always Lambert" through any code path.** The
mechanism, as read, is correctly random. Left open pending either a repro
from a fresh play session (has the owner re-tested since previous CLI
default fix actually landed?) or discovery of a path this pass didn't check.

### Brett: starting room reconfirmed live, AND his escape confirmed live - the
### two don't currently agree with the decoded mechanism

Restarted the VICE process outright (not just soft-reset) to pick up
DISC-222's warp fix, confirmed `WarpMode:0` via `vice.machine.config.get`, and
ran a clean, real-time-paced boot - no shortcuts.

**Read 1**, paused immediately after Full Game selection, `$7935` (9 bytes,
slot 0 = the Alien per two independent existing citations, slots 1-7 = Dallas
..Brett in ROSTER order, loop bound `CPY #$08` at `$65FD-$6614` confirmed
directly)::

    00 06 06 06 1B 1B 1B 00 00
    Alien=airlock_1, Dallas/Kane/Ripley=commdcentr, Ash/Lambert/Parker=mess,
    Brett=airlock_1, Jones=airlock_1

Matches the static re-derivation exactly. **Read 2**, same pass, ~15-20
real seconds later (no player input given at all)::

    20 06 06 06 1B FE 1B 1B 00
    Alien=(moved, room 32), ..., Lambert=FE (this boot's opening victim,
    off-map), Brett=**mess** (was airlock_1)

**Brett genuinely relocated from Airlock 1 to Mess, live, unprompted, within
about 20 seconds of a completely clean boot.** Both halves of the finding are
now live-confirmed, not inferred: he starts there, and he leaves quickly.

**The remake does not reproduce the leaving half.** Ran the remake's own
`_apply_panic_wander` for 160 ticks (~20 game-seconds) across 10 seeds with
Brett at his real start: 7/10 he sits in `airlock_1` the whole time, 3/10 he
dies there. **Not once does he relocate to a different live room.**

**Why, traced to the byte level:** `_panic_route_band` restricts a panicking
character to route-table bands 2/3/4 only (`$5214-$524F`, byte-verified
directly against the raw disassembly listing, not just the decoded constant -
`$7A82,Y`/`$7AA5,Y`/`$7AC8,Y` at Y=0 each independently confirmed `$00`).
**All three of Airlock 1's entries in those three tables self-reference**
(room 0 -> room 0). The remake's `panic_dest` correctly detects that and does
nothing (`if dest == crew.room_id: continue`) - which is behaviourally
identical to whatever the ROM would do landing on the same self-referencing
byte. Whatever moved Brett to Mess in the live capture, it provably was not
this mechanism, landing on any of its three reachable bands, from Airlock 1.

**Left open, precisely scoped:** either (a) `char_wander` is not the routine
that actually fired here and a different, undecoded path moved him, or (b) one
of the three band-table reads for room 0 is wrong despite the direct
byte-level re-check (possible if the table's *row stride* or the crew's *room
index* isn't quite what's assumed), or (c) the Alien moving away first
(observed in the same capture - slot 0 went from `$00` to `$20`) triggers some
separate, undecoded consequence for whoever it leaves behind. Not resolved
this pass; needs a live capture that steps tick-by-tick through the interval
where Brett's slot actually changes, watching the PC, rather than a
before/after snapshot.

**Action:** GAME_REFERENCE.md and DISC-227 both already flagged this as
unresolved rather than settled; this pass upgrades "starts in Airlock 1" and
"leaves quickly" from inferred to live-confirmed, and pins the remake-side gap
(panic-wander dead end for self-referencing rooms) precisely enough to fix
once the real mechanism is found. Filed to `todo.md` as a scoped RE item
rather than guessed at further.

---

## DISC-229 - the opening seats survivors 3+3; Brett backfills the victim's room

**Found:** 2026-08-15. The owner rejected DISC-228's "Brett starts in Airlock 1"
outright - *"Brett should never start in the airlock"* - after already hinting
the pass before that **an underlying assumption is incorrect**. They were
right, and the assumption was mine: that `$793D` is the final placement.

### The store DISC-228 and D-125 both missed

The opening-death routine reads **two tables with a single RNG draw**::

    506A  JSR rng / TAY
    506E  LDA $50EC,Y / STA $64C2   ; the victim's slot
    5074  LDA $510C,Y               ; ...and, SAME Y, a room
    5077  STA $793C                 ; -> $7935 + 7 = BRETT's own slot

`$793C` is not the victim's cell - it is fixed at slot 7. Slot 0 of `$7935` is
the Alien (its parallel health cell `$7D45` is tested against `#$32`, the
50-damage death threshold, at `$60D8`), so slots 1-7 are the crew in
`CREW_NAMES` order and slot 7 is Brett.

All 16 entries pair 1:1 with the victim - Dallas or Kane (both COMMDCENTR) ->
`$06`, Lambert (MESS) -> `$1B` - i.e. **the room that victim started in**.

### Why the game does this: the opening is always 3 and 3

Not a narrative rule about following the corpse. The template seats three crew
in COMMDCENTR, three in MESS, and parks Brett alone in AIRLOCK 1; the victim is
always one of the six. Moving Brett into the vacancy therefore restores a
**3-and-3 opening on every roll**, whoever dies. Brett is the spare, and his
AIRLOCK 1 entry is a parking slot the opening overwrites every single game -
he is never in the airlock once the play screen is drawn, exactly as reported.

### Both prior readings were wrong, in opposite directions

- **D-014** observed the 3+3 result live and generalised it to a "survivor
  redistribution" rule. The observation was right; the rule was not - exactly
  one character ever moves.
- **D-125** corrected D-014 to "the fixed table IS the placement, only the
  victim moves to `$FE`", which is what put Brett in the airlock. It read
  `$50AB-$50B5` (the victim's `$FE` store) and missed `$5074-$5077` thirty
  bytes earlier.
- **DISC-228** (this pass) then confirmed the template read live and treated
  that as settling it, when the live capture it took *already contained the
  disproof*: victim Kane -> Brett COMMDCENTR, victim Lambert -> Brett MESS.
  Both captures match this rule exactly and neither matches D-125.

The lesson is the one this project keeps re-learning: a live read of the
*initial* state does not settle a question about the *starting* state when a
routine mutates it in between. DISC-228's own second read (~20s later) showed
Brett in MESS and was written up as "he relocated during play" - he had not; he
was placed there before the play screen ever appeared.

### Consequences

`_apply_full_opening` now moves Brett into the victim's room. Knock-ons:

- `test_start_rooms_come_from_the_roms_fixed_table` narrowed to the five crew
  who are never the victim; Brett is covered by his own test.
- `test_the_alien_starts_in_airlock_1_with_brett` **inverted** to
  `..._alone` - the Alien does start there, with nobody.
- `test_a_scripted_hunter_can_kill_the_alien` re-anchored from seed 1 to seed
  0: a crew member standing somewhere different from tick 0 changes every
  subsequent roll. Re-swept 16 seeds - 13 won, 2 lost, 1 unresolved at the cap
  - so the "winnable but not always" property still holds.
- Two drift guards added so neither superseded reading returns.

DISC-228's separate finding - that the remake's panic-wander cannot move a
character out of AIRLOCK 1 because all three reachable route-table bands
self-reference for room 0 - **stands and is now moot for Brett** (he is never
there), but remains a real gap for anyone the Alien drives into that room
later. Left open in `todo.md`.

---

## DISC-230 - `select_outcome` decoded in full; the ending was missing a line

**Found:** 2026-08-15, working the ending-screen item.

Traced `select_outcome ($60A9-$62B5)` instruction by instruction and decoded
every string table it reaches. Four independent lines at four fixed rows, all
at **column 0** (the remake centred them):

    row  3  $0478  the SHIP's fate      row 10  $0590  the eggs (55, wraps)
    row  6  $04F0  "The Alien is dead"  row 13  $0608  crew lost / Survivors:
    row  8  $0540  the Narcissus        row 22  $0770  Competence Rating

### The ship's fate line was absent entirely

    60AE  LDA $64CF / BEQ $60D0     ; clear -> "The Nostromo returns to Earth"
    60B3  LDY $64C3                 ; the ANDROID's slot
    60B6  LDA $7D45,Y / CMP #$02    ; ...alive?
    60BD  LDA $7935,Y / CMP #$22    ; ...and NOT aboard the Narcissus?
    60C4  JSR draw_ending_survivor  ;   -> "<name> brings the Nostromo back"
    60CA  JSR draw_ending_survivors ;   -> "The Nostromo is destroyed"

`$64CF` is **"the ship is going to be destroyed"** - raised by arming SCUTTLE
(`set_result_win $58E5`) *and* by a hull breach (`$5DC6`). The android arm is a
whole ending the remake could never show: it survives aboard, overrides the
destruct, brings the ship home - and `draw_ending_survivor ($62D6)` **clears
`$64CF`**, which is also what re-enables the damage term in the rating at
`$6229`. NB the two `draw_ending_survivor(s)` labels are auto-generated and
misleading: neither is about survivors, they are the two ship-fate strings.

`$64E3` (the other unknown) is **"the Narcissus has launched"**, set at `$95B7`
on the launch path. It gates the row-8 line, lets crew aboard count as alive in
the ending scan (`$6300`), and spares them when the ship breaks up (`$5DAD`).

Both modelled as state flags mapping 1:1 onto the ROM's own.

### Everything else the trace corrected

- All ending strings are **mixed case** in the ROM; they had been transcribed
  in caps before DISC-215's case fix. They also render through ALIEN's own
  charset, not the loader font - the same `c64_font` slip DISC-220 hit.
- "Survivors:" shares row 13 with "All crew lost" (two arms of one scan at
  `$6166`, never both); it was on 15. Names run from row 14, not 16.
- The eggs line is **one 55-cell linear copy** that wraps itself; the four
  trailing spaces in the stored string are what pad row 10 to the wrap.
- "press any key" is lowercase at row 24 **column 24** (`$6475` -> `$07D8`),
  not a centred shout at column 13.
- `competence_rating` needed **no change** - it already traces this routine
  correctly, `$64CF` gate included. Only the presentation was wrong.

### The auto-destruct countdown, decoded and finally shown

`MALFUNCTION_MESSAGES[7]`/`[8]` had been decoded long ago and never displayed,
so a player racing the clock saw nothing. `mainloop_sub_5a26 ($5A26)` posts
them through the same `draw_damage_warning` every malfunction uses::

    5A3E  LDA $657B / BNE $5A46 / JMP hull_breach   ; 0 -> the ship blows
    5A46  CMP #$06 / BCC $5A58
    5A4A  ADC #$AB / STA $555C / LDA #$07           ; >= 6 -> type 7
    5A58  ADC #$B0 / STA $5578 / LDA #$08           ; <  6 -> type 8

`$AB` is `$B0 - 5`, so type 7 counts down the **override window** (which
expires at 5, `AUTO_DESTRUCT_OVERRIDE_ABOVE`) while type 8 shows raw minutes.
The digit lands at index 24 / 22 of each 30-char message - both blanks in the
stored text. Reproduced by `constants.auto_destruct_banner`.

---

## DISC-231 - three transient banners, and the android reveal's only tell

**Found:** 2026-08-15, same pass. All four were decoded facts sitting unused.

### The row-24 banners

`$5B80` "MOTHER refuses launch", `$5C33` "Go get Jones" and `$5950` "Fire Out"
are each written to **`$07C0` (row 24 col 0)**, held by a blocking `delay_long
($561C)`, then blanked by `clear_line_07c0 ($5BE7)`. The remake's handlers
returned a bare `False`/`True` and said nothing.

**`delay` itself blacks the border** - `$5626 LDA #$00 / $5628 STA $D020` -
and every caller restores `#$06` afterwards. That is exactly the owner's
report: *"the status bar reads MOTHER refuses launch and the game freezes for
a moment and the border turns black."* All three parts are one mechanism.

The remake cannot block its own loop, so the banner is shown for `NOTICE_TICKS`
and the border held black for the same span.

### The android reveal

`$52D4 LDA $7214 / $52D7 STA $64CC / $52DA STA $D021` - one value, **two**
stores. The remake had the first (`locked_crew_id`, which correctly locks the
android out of selection) and not the second. `$D021` is the background
register, and because ALIEN's font is cut-out it is the **ink every glyph shows
through** (D-050) - so the reveal recolours the entire screen's lettering from
black to the android's own slot colour (1-7) at a stroke. That is the game's
only tell, and it was invisible.

Modelled as `state.background_colour`, threaded through the five places
`play.py` was hardcoding black as the `$D021` ink.

---

## DISC-232 - the CONTROL panel is 19 rows, and every band below row 0 was wrong

**Found:** 2026-08-15, owner report: *"some words on the wrong colour
background and there are black sections at the bottom of the crew control
menu."* Both symptoms are one cause, and it also closes the two panel items
the previous pass left open.

### The live colour RAM

`the live captures (not published)narcissus_d800.bin` cols 30-39 is a capture of a real
crew-order panel. Read against the remake's `_PANEL_SECTIONS`::

    row        LIVE                REMAKE (DISC-213)
    0          LT_GREY   name      LT_GREY          ok
    1-7        LT_BLUE   move to:  LT_BLUE  1-6     off by one
    8-10       LT_GREEN  use:      LT_GREEN 7-9     off by one
    11         LT_RED    get/leave LT_RED   10      off by one
    12         YELLOW    rule      YELLOW   11      off by one
    13-17      PURPLE    Special:  PURPLE   12-14   off, and too short
    18         WHITE     quit      WHITE    15      off by three

The panel is **19 rows, 0-18**, and starts at screen row **0** - corroborated
by the ROM: `$706F STA $D81E,Y` fills colour RAM row 0 cols 30-39 with `$0F`.
DISC-213 built its table from screenshots and got 16 rows ending at `quit` on
row 15. Painting only 16 left **rows 16, 17 and 18 unpainted - the black
sections at the bottom of the crew menu**.

### Which also dissolves the `$064E`/`$0676` "conflict"

The previous pass flagged these two fixed SPECIAL cells (rows 14 and 15) as
contradicting DISC-213's table, which had `quit` on row 15, and deferred the
question pending a capture. There was never a conflict: rows 14 and 15 are
**both inside the PURPLE Special block (13-17)**, and the same capture shows
`Get Jones` sitting on row 15 exactly where `$0676` puts it. The ROM addresses
were right; the row table was wrong.

The USE: question resolves the same way: rows 8-10 are `" use:"` plus **two**
item slots, which is what the owner described.

### Why words were on the wrong background

The ROM writes each panel element to a **fixed screen cell** - it is a slot
layout, like the bottom status template (DISC-217), not a running list. The
remake drew the entries sequentially from row 1, so the moment any optional row
was absent (Leave item only appears when carrying; GET JONES only when the cat
is here) everything below it slid up a row and landed on the wrong band:
`use:` on the blue block, `Special:` on the red one. `_panel_rows` now assigns
the ROM's fixed slots per category.

**Left open, honestly:** the CONTROL list and the INDICATE room list are
*different* panels with their own layouts, and no colour-RAM capture of either
exists (only `narcissus_d800.bin`, which is a crew panel). They currently
render sequentially over the crew panel's bands - nothing is black, but the
band boundaries are not theirs. Filed rather than guessed from a screenshot,
which is precisely how DISC-213 went wrong.

---

## DISC-233 - the panic-wander dead end was real, but not the bug it looked like

**Found:** 2026-08-15, closing the last open play-report item.

DISC-228 filed this as "the remake's panic-wander cannot move anyone out of
AIRLOCK 1" and asked for the ROM's escape path to be traced. Reading
`char_wander ($5203-$522B)` through settles it: **there is no escape path,
because the ROM cannot move them either.** AIRLOCK 1's entries in all three
route bands `_panic_route_band` can reach point back at AIRLOCK 1, and nothing
in `char_wander` re-rolls or falls back. A panicking character in a
self-referencing room stays put in the original too. Standing still is
faithful.

The actual defect is what happens *around* the non-move::

    5203  LDA #$00 / STA $650C,Y   ; drop the pending order - BEFORE the roll
    5208  JSR rng ...              ; pick a band
    521B  LDY $7214
    521E  STA $64E6,Y              ; store the destination
    5221  LDA #$28 / STA $64EE,Y   ; re-arm the turn timer to 40
    5226  LDA #$01 / STA $64C4,Y   ; mark the move pending
    522B  JMP dispatch_char_action

Every arm of the roll converges on `$521B`, and **there is no "did the
destination change?" test anywhere in the routine**. The order is dropped
before the roll is even taken, and the timer is re-armed whatever came back.

The remake bailed out of the whole branch with `if dest == crew.room_id:
continue`, so in a self-referencing room a panicking crew member kept their
queued order *and* their turn timer - they carried on obeying instructions as
though the panic had not happened. Corrected: the order is dropped and the
timer re-armed unconditionally, and the destination is assigned (a no-op when
it self-refers).

Worth noting because it is a recurring shape in this codebase: an early
`continue` that looks like a harmless "nothing to do here" quietly skipping
the side effects the ROM performs first. Same class as DISC-226's missing
`sound_cues.clear()`.

---

## DISC-234 - the burning-ship spiral, transliterated rather than redrawn

**Found:** 2026-08-15, implementing the hull-breach animation DISC-230 had
traced but deliberately left unbuilt.

The previous pass stopped short on the grounds that building a spiral from a
partial read would mean inventing geometry. The way round that is not to draw a
spiral at all: **emulate the ROM's pointer arithmetic** and record where it
lands. `breach_spiral_cells` is a line-for-line transliteration of
`animate_fill_row ($5C42)` - each Python step is the corresponding instruction -
so the cell order is the machine's by construction, and nothing about the shape
had to be guessed at.

    5C55  LDY $64E1 / STA ($FB),Y / DEY / BPL   ; leg..0, downward
    5C63  CMP #$28 / BNE                        ; ...until leg reaches 40
    5C70  INC $64E1                             ; leg++
    5C77  ADC #$28 / STA ($FB),Y=0  x $64E0     ; run cells DOWN
    5C90  INC $64E0
    5C98  LDY #$01 .. CPY $64E1 / BCC / BEQ     ; 1..leg, rightward
    5CA8  ADC $64E1 / INC $64E1
    5CBB  SBC #$28 / STA ($FB),Y=0  x $64E0     ; run cells UP
    5CD4  INC $64E0 / SBC $64E1
    5CE6  JMP $5C55

Running it settles several things that were open questions:

- It **terminates cleanly** and covers **all 1000 cells** - enumerated, not
  assumed. 1012 writes land on screen (twelve cells get painted twice where the
  turns overlap) and exactly one lands on `$03FF`, the byte immediately before
  screen RAM. That stray write is the ROM's own off-by-one; it is dropped here
  rather than reproduced, since there is nothing at that address to corrupt.
- The pointer starts at `$05EB` = offset 491 (row 12, col 11), but the first
  cell *written* is `ptr + leg` = 507, because `$5C55` opens with `LDY $64E1`
  and counts **down**. Easy to conflate; the test pins both.

`hull_breach ($5D17)` then runs it **seven times**: once writing `$20` over
screen RAM to blank the field, then six passes over colour RAM (`$5D6C LDA
#$D9`) in the `$5D11` palette - RED, ORANGE, YELLOW, WHITE, YELLOW, ORANGE -
and `$5C6A` leaves the border black. Reached from two sites, both of which
`JMP hull_breach`: a room hitting exactly 20 damage (`$565C`) and the
auto-destruct countdown expiring (`$5A43`). Modelled with `state.ship_destroyed`,
deliberately distinct from `ship_destructing` (which only means *armed*).

**The one `[?]`:** the playback rate. The ROM's pace comes from
`anim_sound_tick ($5CEA)`'s per-cell delay loop, which has no clean frame
equivalent; `_BREACH_CELLS_PER_FRAME` is chosen so all seven passes take about
four seconds, the right order of magnitude for ~7,000 delayed writes. Marked as
the only undecoded value in the routine - the cell order, palette and pass
count are all the machine's.

---

## DISC-235 - `$7000` is the CONTROL list's colour table; two screens, two tables

**Found:** 2026-08-15, closing the last panel item.

DISC-232 corrected the *crew-order* panel from a live colour-RAM capture and
left the CONTROL and INDICATE lists open, noting they have their own layouts
and no capture existed. Taking that capture settles it - and identifies a
table this project had already found and wrongly dismissed.

While chasing DISC-232 I checked `$7000` (19 bytes: `0F`, `0E` x8, `0D`, `01`,
`0A` x5, `0F` x3) against the crew panel, saw it match nothing, and set it
aside. It is not the crew panel's table: **it is the CONTROL list's**, and a
fresh live capture matches it cell for cell::

    row  0      LT_GREY   "CONTROL"
    rows 1-8    LT_BLUE   "Order:" + the seven crew
    row  9      LT_GREEN  "indicate"
    row  10     WHITE     "location"
    rows 11-15  LT_RED    "display" / "level:" / Upper / Middle / Lower Deck
    rows 16-18  LT_GREY   empty

`$749C LDA $7000,Y` reads it with `$64E5` (the highlighted row) to restore that
row's normal colour after the cursor blink, and `set_color_ptr_row ($753F)`
addresses `$D81E + $64E5*40` - colour RAM column 30, the panel. So the two
screens colour the same ten columns to different schemes, which is exactly why
`$7000` looked wrong when tested against the other one.

Two details worth keeping:

- **"indicate"/"location" is one wrapped label straddling two colours** (green
  then white), so the CONTROL rows are assigned positionally, not by category.
- The crew block is rows **2-8** - seven rows for seven crew, including the
  opening victim (D-042: the list always shows all seven).

Now decoded by `gamedata` rather than transcribed, so a regen keeps it honest.

**Still open, and now the only panel unknown:** the INDICATE room list. It is
34 rooms - longer than the panel - so it must scroll, and no capture of it
exists. It keeps the CONTROL bands (it is reached from that list and occupies
the same columns), which is the least-invented choice available, and stays
sequential with the existing scroll window.

---

## DISC-236 - INDICATE is a two-page room-name list; the remake invented a scroller

**Found:** 2026-08-15. The last panel unknown, answered from the disassembly -
the live oracle turned out not to be needed.

DISC-235 left this as "34 rooms, longer than the panel, so it must scroll, and
no capture exists". Both halves of that guess were wrong.

### What INDICATE actually does

`draw_deck_map ($73C8)` - misleadingly named; it draws the **panel**, not the
map - copies 19 consecutive 10-byte room-name records straight into panel rows
0-18::

    73C8  $FD/$FE = $A712      ; source: the room-name table, one record early
    73D0  $FB/$FC = $041E      ; dest: screen row 0, COLUMN 30
    73DA  copy 10 bytes; $FB += $28 (a row); $FD += $0A (a record)
    73FC  CPX #$13             ; ...19 times

Then `$7400` paints rows 1-17 LT_BLUE (17 iterations from `$D846` = row 1 col
30) and `$7431 LDA #$0F` supplies row 18's grey restore colour - both matching
**`$7440`**, a *third* 19-row panel colour table: LT_GREY 0, LT_BLUE 1-17,
LT_GREY 18. (`$7000` is the CONTROL list's, DISC-235; the crew panel's is
live-captured, DISC-232. Three screens, three tables - which is why a table
checked against the wrong screen reads as nonsense.)

### Two pages, not a scroll window

    74FA/7654   src $A712, cursor row 18, $64FB = $10    ; page 1
    766F        src $A7D0, cursor row 0,  $64FB = $08    ; page 2
    7676        CMP #$08 / BEQ -> already page 2, exit

Row 18 of page 1 is the **"next page" control**, not a room. And the cursor row
converts to a room id two different ways depending on the page::

    76A4  $64FB == $10 -> $64F7 = $64E5 - 1      ; page 1
    76B4  else            $64F7 = $64E5 + $10    ; page 2 (+16)

So **page 1 rows 1-17 are rooms 0-16, page 2 rows 1-18 are rooms 17-34** - all
35 locations, verified by enumeration. The split lands exactly on the
two-record discontinuity the name table already carries (`$A71C + 17*10` would
be `$A7C6`; the ROM uses `$A7DA`), which is why page 2's source is `$A7D0` and
not the arithmetic `$A7BC`. Row 0 of each page shows the filler record that
precedes its block.

### The remake's version is an invention on three counts

`indicate_entries` builds **34 rooms sorted alphabetically** into a scrolling
list with a `quit` row. The original is 35 locations in **table order**, on two
**fixed pages** of 19 rows, paged by the bottom row. Alphabetical ordering, the
scroll window and the entry count are all invented.

Not ripped out in this pass: it changes menu semantics and the controller's
cursor model, so it wants its own scoped pass rather than a rushed edit at
the end of a long one. The colour table (`$7440`) *is* wired in, since that was
self-contained. Filed with everything needed to do the rest directly.

---

## DISC-237 - most of the "needs the live oracle" list did not need it

**Found:** 2026-08-15, working the `[?]` set. Six of the eight items were
answerable from the disassembly; three of those were **already correct in the
code** and only the todo entry was stale.

### There is no obey/refuse probability curve - the PCS is deterministic

The largest open question, and the answer is that the mechanic does not exist.
`resolve_char_move ($5170)`, the order-resolution entry, is::

    5170  LDA $6571,Y      ; effective composure
    5173  CMP #$02
    5175  BCC $517A        ; below 2 -> the panic branch
    5177  JMP dispatch_char_action    ; 2 or more -> just do it

**There is no `JSR rng` anywhere in `$51xx`.** A character with composure >= 2
always executes the order; below 2 the panic branch decides deterministically
(composure 0 always wanders, `$51E7`-`$51F4`; composure 1 only when sharing a
room with a surfaced Alien, `$5252`). The same `CMP #$02` threshold gates who
may attack (`$492F`) and who counts as alive for the endgame scan (`$5B5B`).

So the manual's "they have personalities and may not obey" is implemented as a
**hard composure gate plus panic**, not a compliance roll - which is exactly
what the remake already does. The `[?]` was describing an invented mechanic
that an earlier de-invention pass had already removed.

### Companion support: real, and already load-bearing

`$4843 STA $6571,Y` is where the companion-support term lands, and `$5170`
reads `$6571` - so support directly decides whether someone panics. Not a
cosmetic modifier at all. Already modelled (`effective_composure`).

### The panic-wander "precedence" question dissolves

The three paths that reach `char_wander` belong to **different actors in
different routines**: `$5170`'s crew panic branch, and the android's own
`$5306`/`$530E` (flee) and `$5339` (nobody to hurt). They cannot contend, so
there is no precedence to settle. The remake already runs them separately.

### Three that were already right

- **Corrosion magnitude.** `$8ED0 INC $653F,X` - exactly +1 per action.
  `ROOM_DAMAGE_ALIEN_PER_ACTION = 1` is correct and cited. Its comment claimed
  "the exact cadence and the two unmodelled gates still want a proper trace";
  all four gates are visible in `guard_6562 ($8EBD)` - no attack sequence
  (`$6562`), not in a duct (`$6501`), the arrived flag (`$6563`) - plus
  `$89AF`'s hunting test, and all four are modelled.
- **Tracker precision.** The scan at `$8F0B`-`$8F62` returns
  `return_true`/`return_false` over `$6565..$656A` - a **boolean** across the
  holder's room plus its five route neighbours (D-150). No room, no direction.
  `state.tracker_alarm` is already a bool.
- **Consumable charges.** `$4B47` gives extinguisher 3, harpoon 1, laser 10,
  and the tracker no counter at all (destroy-on-use). `CONSUMABLE_USES`
  already carries exactly these with citations.

### A bonus, found on the way

`damage_display_char ($8EEF)` shows how the damage percentage is rendered:
`LSR A` then `ADC #$B0` for the tens digit at `$070B`, and `$B5`/`$B0` for the
units at `$070C` - i.e. **percent = damage x 5**, two digits, which makes
`HULL_BREACH_THRESHOLD` 20 exactly 100%. The remake's
`100 * damage // HULL_BREACH_THRESHOLD` is arithmetically identical.

### Still genuinely open

- **Item USE effects for net / electric prod / spanner / thermlance.** The USE
  dispatch is distinct from `resolve_attack ($4940)` and has not been traced.
- **Front-end card timing.** Cosmetic, and paced by delay loops with no clean
  frame equivalent.

---

## DISC-238 - INDICATE rebuilt from the ROM; the last three items closed

**Found:** 2026-08-15, closing everything except the resolution-independence
pass.

### INDICATE: the invented list replaced

DISC-236 decoded the two-page structure; this implements it. `indicate_entries`
used to build 34 rooms sorted **alphabetically** into one scrolling list. It now
builds exactly what `draw_deck_map ($73C8)` copies - 19 rows, twice::

    page 1  src $A712   row 0 "   quit   "   rows 1-17 rooms 0-16
                        row 18 "other list"  -> flip to page 2
    page 2  src $A7D0   row 0 "other list"   rows 1-17 rooms 17-33
                        row 18 "   quit   "  -> exit

Decoding the two records DISC-236 had called "fillers" is what made the shape
obvious: `$A712` and `$A884` are both `"   quit   "`, and `$A7C6`/`$A7D0` are
both `"other list"`. They are not padding - they are the page controls, and
they sit at rows 0 and 18 **swapped between the pages**, which is exactly why
the ROM keeps two source offsets ten bytes apart rather than one plus an index.

Rooms come out in **table order**, 34 of them; NARCISSUS (34) is absent because
it is off the deck plans entirely.

### A rendering bug the rebuild exposed

With INDICATE finally drawing real rows, the whole list came out light green
over its real light-blue band. Cause: `_draw_menu_panel` took each row's paper
from **`_BAND_COLOUR[entry.category]`**, a per-category map that predates the
three decoded row tables. Every INDICATE row is category `INDICATE` -> light
green, so the category map simply overpainted `$7440`.

The ROM colours these ten columns **strictly by row**, from whichever table is
in force. `_BAND_COLOUR` agreed with the crew panel by coincidence and with
nothing else. The paper now comes from the row, and a test walks all three
screens (crew panel, CONTROL `$7000`, INDICATE `$7440` x2 pages) asserting
every row carries its own table's colour.

### The opening notice was twice too fast

`OPENING_TICKS` was 27. `sub_5049` ends with **two** `JSR delay_long`
(`$50B8`/`$50BB`, then RTS), and D-172 computed `delay_long` at 3.128 s from
the loop itself - so the card is 6.256 s = **49 ticks**. D-172 applied that
arithmetic to the title card and the letter gap and never re-checked the
opening, which kept an older guess barely over a *single* delay_long.

### And one that is genuinely not a ROM constant

`LOADING_PLAY_TICKS` stays `[?]`, but the reason is now recorded rather than
open: unlike every other card it is not paced by a `delay_long` at all - it is
shown while the loader reads the next file off the disk, so its duration is
drive I/O. There is no value in the image to decode.

### Also closed on the way (DISC-237 follow-up)

The USE-effects question was chasing a false premise. `route_command ($8437)`
has no USE verb, and `resolve_attack ($4940)` is a single dispatch over every
item id - prod/incinerator/spanner +1 wound, net +80 ticks and destroyed,
tracker destroyed +1 wound, cat box rejected. USE and ATTACK are the same
routine, which the remake already models (D-033). "Thermlance" turns out to
have **zero instances** - a name in the type table with no item in the game.

## DISC-239 - the resolution-independence plan's own premise was wrong in four places

**Found:** 2026-08-15, preparing to make the renderer resolution-independent.
Nothing was implemented; this is a scope audit of the step-by-step plan filed in
`todo.md` a day earlier, re-measured against the code it describes.

The plan's headline count held up: **87 `* s` sites** (45 `frontend.py`, 28
`play.py`, 14 `pygame_app.py`) against a filed estimate of "~88". Four
structural claims did not.

**1. `_surface` is not native.** The plan states it "is already a fixed-size
native-resolution field", and concludes step 1 is "mostly *removing* work, not
adding it". It is built at `pygame.Surface((_WIDTH * scale, _HEIGHT * scale))`
(`pygame_app.py:366`). Converting it is part of the work, not a precondition
already met.

**2. Three more assets bake `scale` in**, none of them `* s` sites and none
listed: both `SysFont` sizes (`7 * scale`, `16 * scale`, `:376-377`) and the
**pre-scaled** cached title-egg composite (`_title_egg`, `:453`).

**3. `_present` applies the border offset twice, not once.** The plan treats it
as a single choke point. There is a `_border_flash` early return (`:510`) ahead
of the normal path (`:517`), each with its own
`(_BORDER_X * scale, _BORDER_Y * scale)` blit. Converting only the visible one
would letterbox differently for the duration of every command-accept rainbow -
a one-frame defect of exactly the kind this project keeps shipping.

**4. There is no `--scale` flag.** The plan's definition of done requires that
"`--scale N` (or equivalent) still works". `scale` is a constructor default
(`_SCALE`, `:353`) and neither `__main__.py` nor `cli.py` mentions it. Adding
one is new scope; there is no regression to protect.

**Two things are better than the plan assumed.** `tiles.py` and `romfont.py`
carry glyphs and sprites as 0/1 `Bitmap` grids and import no pygame at all, so
the tile *data* is already resolution-independent and only the rasterizer
multiplies. And nothing in `render/` reads pointer coordinates - no `MOUSE*`,
`VIDEORESIZE` or `RESIZABLE` reference exists in the package - so step 4 starts
from zero hit-tests to convert rather than an unknown number.

This is the same failure the drift guards were built for, one register further
out: a plan is prose, and prose has no compiler. The claim that `_surface` was
already native is the kind that survives precisely because it makes the next
step sound cheap.

**Action:** all four corrections applied in place to `todo.md`'s
resolution-independence entry (premise, step 1, step 6), with the measured
counts and line numbers, so the implementation pass does not inherit them.

## DISC-240 - the ROM data was stranded behind a pygame import

**Found/done:** 2026-08-15, preparing the renderer for resolution independence.

Simulation and presentation were **already** cleanly split - `core/` imports
nothing from `render/`, `audio/` or pygame, and both import headless. The cut
that was missing ran the other way: **ROM-derived data vs. rendering
mechanism**.

`render/play.py` carried **294 ROM address citations** and `render/frontend.py`
**267** - more than `core/alien.py` (292) or `core/menu.py` (244). Both
hard-import pygame at module level, so a large body of decoded ROM truth could
only be read with a display library installed. For a project whose first rule is
"the code is the truth", a good deal of that truth needed SDL to look at.

**Moved** to a new headless package `src/alien_remake/screens/`, verbatim with
citations attached:

- `panels.py` - the three 19-row colour tables (`$7000`, `$7440`, and the crew
  panel), the fixed-cell slot indices, `BOTTOM_BANDS`
  (`paint_map_colors $7993`), the 40x25 geometry, and the two row-24 Jones
  notices.
- `ending.py` - every ending string with its byte-table address
  (`$6372`, `$63BA`, `$63D8`, `$63F8`, ...), `ENDING_ROWS`, and the rating and
  survivor-list layout.

`play.py` 1,310 -> 1,175 lines and `frontend.py` 1,711 -> 1,665; the drawing
code stayed put. The moved names are **aliased back** (`_PANEL_SECTIONS =
panels.PANEL_SECTIONS`) rather than re-spelled at every call site, so neither
file's body nor the six test files importing those names from `render.play`
had to change - the diff is a move, not a rewrite.

**Colours became indices.** `PANEL_SECTIONS` and the two decoded tables already
held palette indices; `BOTTOM_BANDS` and `BAND_COLOUR` held `c64.rgb(...)`
tuples. An index is what colour RAM actually holds, so the headless layer now
stores indices throughout and `c64.rgb()` runs at the render boundary, in the
alias block. This is also the reason the layer has no opinion about scale.

**The test that matters is the import one**, and it runs in a **subprocess**:
21 of the suite's 42 test files import pygame, so by the time these tests
execute it is already in `sys.modules` and an in-process `meta_path` blocker is
a no-op - it would pass no matter what. Verified by deliberately adding
`import pygame` to `panels.py` and confirming the guard fails, then reverting.
A companion test asserts `render.play` *still* needs pygame, so the guard cannot
silently degrade into always-true.

**Timing was the point.** The resolution-independence pass rewrites 73 of its 87
`* s` sites inside these two files. Extracting first means that mechanical
rewrite touches drawing code only, and the ROM tables keep tests that never load
a display.

**Not done, deliberately:** `render/audio.py` stays where it is - it is a
stateful mixin sharing the "attack on screen" latch with the drawing half, and
its own docstring makes the case; a better package name is not worth breaking
that. `core/constants.py` (1,053 lines) stays whole - already headless and
cited, and size alone is not a reason.

**Action:** filed in `todo.md` as a completed step, with the two follow-ups it
implies still open - splitting `frontend.py` by screen, and splitting
`render/c64.py`'s palette (a rendering choice) from its hardware colour-index
names (ROM truth), which would retire the one backwards import this left
behind: `screens/` imports `render.c64` for the index names. Safe today only
because `render/__init__.py` is deliberately pygame-free.

## DISC-241 - the game only found its own data from the project root

**Found/done:** 2026-08-15, starting the "works well on Windows" pass.

Seven runtime asset loads each used a bare relative `Path("out")/...`:
`charset.bin`, `intro.wav`, `basic.bin`, `chargen.bin`, `MENU1.prg`, and
`intro.py`'s two dev-tool defaults. So the remake found the original's decoded
data **only when launched with the repository as the working directory**. A
desktop shortcut, an installed `alien-remake` entry point, or Explorer's "Open
with" all found nothing.

**It degraded in silence, and not only cosmetically.** Every asset is genuinely
optional - none can be shipped, since all of it is the 1984 game's copyrighted
data - so each call site already had a fallback and none of them complained. The
result looked like a working install with no music. But `basic.bin` is the BASIC
ROM that `garbled_name_codes` reads the opening victim's name out of, and
without it that function returns `None` and the caller prints the crew member's
**clean** name where the original prints the garbled one. A wrong working
directory quietly changed replica behaviour, which is the exact failure mode
this project's fidelity discipline exists to prevent.

Verified by running from `%TEMP%`: `charset.bin` absent, BASIC ROM absent,
`garbled_name_codes(1)` -> `None`, no error anywhere.

**Fixed** with one resolver, `alien_remake/assets.py` (stdlib only, no pygame,
importable from `core` - locating a file is not a rendering concern). Search
order, first hit wins: `$ALIEN_REMAKE_ASSETS`, `./out`, `<repo>/out` resolved
from the module's own location, `<exe>/out` when frozen, then the per-user data
directory. The third entry is what actually fixes the reported case; the second
preserves the existing dev workflow unchanged.

**And it now says what is missing.** `assets.report()` lists each absent asset,
what its absence costs, and the command that produces it; `__main__` prints it
once to stderr. Silence is what let a broken working directory pass for a
working install.

**Two Windows details found by running it rather than reasoning about it:**

- `sys.stderr.encoding` is **cp1252** on a default Windows console, so the
  report string is held to ASCII. The em-dash this codebase uses everywhere
  else in prose came out as a replacement character. The constraint is on this
  one string because it is the one that reaches a terminal.
- `asset_roots()` is deliberately **not** cached. Both `$ALIEN_REMAKE_ASSETS`
  and the working directory can change within a process, and an `lru_cache`
  here would have made the override work only if it was set before the first
  lookup - a bug that would surface as "the environment variable is ignored,
  sometimes".

**Deliberately left relative:** the two VICE ROM fallbacks
(`tools/vice-mcp/.../basic-901226-01.bin`, `chargen-901225-01.bin`) and
`intro.py`'s `DEFAULT_PRG`/`DEFAULT_OUT`. These are developer conveniences
pointing into this checkout, not shipped assets, and two tests key off
`DEFAULT_PRG.exists()` to skip.

**Action:** the per-user data directory costs a single `sys.platform` branch and
is the path an eventual Linux build would use, so the Windows fix does not
foreclose it. Filed in `todo.md` under the Windows pass.

## DISC-242 - the renderer draws native and scales once

**Found/done:** 2026-08-15, the resolution-independence pass. DISC-239 had
already re-measured this plan and corrected four wrong premises in it; this is
the implementation.

**What was wrong.** `_surface` was built at `_WIDTH * scale`, every draw call
pre-multiplied its own coordinates (87 sites: 45 `frontend.py`, 28 `play.py`,
14 `pygame_app.py`), both `SysFont` sizes were `n * scale`, and the title-egg
composite was cached pre-scaled. The picture was therefore correct only at an
integer multiple chosen at construction, and the window could not be resized at
all - no `RESIZABLE`, `FULLSCREEN` or `vsync` flag existed anywhere.

**What it is now.** Drawing happens at native 320x200 always. `field_rect()`
decides where the field lands and `_blit_field()` scales it, once, on **both**
`_present` paths - the `_border_flash` early return as well as the normal one.
That second path is the one DISC-239 predicted would be missed; a stale offset
there would have moved the field for the duration of every command-accept
rainbow. The window is resizable, `VIDEORESIZE` is handled, and F11 or Alt+Enter
toggles fullscreen and restores the previous windowed size.

**Integer scaling only, per D-056.** A fractional factor makes some source
pixels two window-pixels wide and their neighbours three, which reads as shimmer
on a pixel-art field. The leftover becomes VIC border, painted in the colour the
screen is already using - so there is no visible letterbox at all. The border is
elastic; the field never distorts.

**`transform.scale` onto a software surface, deliberately.** `pygame.SCALED` or
`vsync` would move this to an SDL renderer with a GL context, which is the thing
that can be invalidated when a machine resumes from sleep. Software blits
survive it. Recorded here because it looks like a free choice and is not.

### Three things the process caught that reading would not

**The tokenizer, not a regex.** Classifying every bare `s` token first showed
that `frontend.py` contains `sum(s.get_width() for s in surfaces)` - a
comprehension variable, unrelated to the draw scale. A regex sweep for `* s`
would have silently corrupted it.

**mypy found the leftovers a regex missed.** The `_blit_sprite` substitution
failed on nested parentheses (`c64.rgb(c64.WHITE), s)`) and on multi-line calls
where the argument sat on its own line. Four sites survived as `Name "s" is not
defined`, plus the `RendererState` declaration that still required the removed
parameter. The protocol module earning its keep exactly as intended.

**A golden render proved equivalence.** 56 renders - 14 screens x 4 frame
counts, 10.75 MB - captured before the cleanup and compared byte-for-byte after.
Identical, twice: once after deleting the 87 multiplications, once again after
removing the draw-scale attribute. The test suite alone could not have shown
this, because a wrongly-deleted factor would change the picture identically at
every window size and the resolution tests compare *across* sizes.

**And the drift guard caught its own author.** The `* s` sweep ran over comment
text too, mangling `` `* s` `` to empty backticks inside the very comment
explaining the change; the prose guard then failed on a `` `_scale` `` reference
left behind after the attribute was deleted. Both fixed. This is the third time
that guard has caught a stale claim, and the first time it caught one written in
the same pass that broke it.

**A test that could not fail, made able to.** The first version of
`test_field_content_is_identical_at_every_window_size` rendered only WELCOME and
**passed** with a deliberately window-dependent coordinate injected into
`_blit_cells` - the shared text helper WELCOME happens not to use. It now drives
all fourteen screens through `draw()` and fails on that injection.

**Action:** `todo.md`'s resolution-independence entry is complete except step 5
(fonting the charset), which was always optional and separable. The fullscreen
item in the Windows pass is closed by the same change.

## DISC-243 - the fit was measured against the wrong rectangle, and step 5 was never needed

**Found/done:** 2026-08-15, reviewing DISC-242's own implementation.

Two corrections to the pass that had just shipped, neither of which broke a
test - the first because nothing measured it, the second because it was a
question nobody had answered empirically.

### The scale factor was one step short at most real display sizes

`field_rect` chose the largest whole factor for which the **bordered** 384x264
composition fits. The plan (`todo.md` step 4) had said the *field*, 320:200; the
implementation quietly used field-plus-border, and a fixed 32*scale border is
expensive. Measured across real displays:

    1280x720    2x, 28% of the screen  ->  3x, 62%
    1366x768    2x, 24%                ->  3x, 55%
    1920x1080   4x, 49%                ->  5x, 77%
    2560x1440   5x, 43%                ->  7x, 85%

Nothing failed. The picture was simply small, in a way only visible by asking
"would a larger factor have fitted?" - which is now an invariant
(`test_the_scale_is_maximal_no_step_is_wasted`).

The fix measures the field and lets the border take the remainder. **At the
sizes the game actually opens (1x, 2x, 3x of 384x264) the geometry is
unchanged** - the authentic 32-pixel border survives exactly where it always
was, and only larger windows get a proportionally thinner one. That is the more
faithful reading in any case: a VIC border on a real television varies with the
set's overscan rather than being a fixed pixel count.

**The docstring was already describing behaviour the code did not have.** It
claimed 1280x800 gives "a clean 4x with no border" - true of 320x200 being
exactly 16:10, but the bordered rule returned 3x there. Prose written from the
intent rather than the implementation. Both are now pinned by tests.

### Step 5 (fonting the charset) is unnecessary, and would be harmful

The plan made it conditional: *"if crisper text at large window sizes still
matters"*. It does not, and this is measurable rather than arguable. At an
integer factor, `pygame.transform.scale` reproduces every source pixel as a
solid block of exactly its own colour - verified at 6x across a full screen,
with **zero** colours introduced beyond the native palette.

So the ROM's glyph bitmaps are already perfect at every supported size, and
vector-tracing them would make text *less* faithful: it would produce shapes
that are an interpretation of the bitmaps rather than the bitmaps, and
reintroduce the anti-aliasing D-056 exists to forbid.

Two tests hold this: one asserts scaling invents no colours, the other that each
source pixel is a solid block. Both were confirmed to fail with `smoothscale`
substituted for `scale`, which is the specific way this would regress.

**Action:** `todo.md`'s resolution-independence entry is now complete, step 5
closed as "not needed, and would be harmful" rather than left open.

## DISC-244 - four play-report bugs, and the deck table has 35 entries

**Found/done:** 2026-08-15, from a player report.

### The Narcissus's deck is 3, and that sentinel is load-bearing

`tbl_room_deck ($7569)` runs **35** entries, not the 34 the duct map consumes,
and `$758B` - index 34, NARCISSUS - is **`03`**, one past Upper/Middle/Lower.
Nothing aboard the ship can match it.

`update_item_sprite ($7C3D)` reads the target room's deck, compares it with the
acting character's (`CMP $4BEF / BEQ $7C5D`), and on a mismatch writes
**`$D002 = 0`** - parking the location pointer off the left edge instead of
positioning it. So highlighting NARCISSUS in "move to:" draws no marker box.
That is what deck 3 buys.

The remake gave it `shuttlebay_room.deck`, so the decks matched and the box
appeared. Fixing it exposed a second question immediately: `ShipMap.decks()` fed
the CONTROL panel's deck list, which has exactly three rows (13-15, DISC-232),
so deck 3 added a fourth. `decks()` now excludes the sentinel.

**Three stale claims died here.** `nostromo.py` said the Narcissus "has no
`$7569` deck entry of its own"; the module docstring gave the split as
**10/14/10**, a leftover from the `$80D3` reading D-116 replaced, when `$7569`
gives **9/16/9**; and `test_deck_split_...` asserted 9/16/10 while its own
docstring said 9/16/9.

### The ducts are a separate space in the co-occupant scan too

`$7E68` tests three things per crew member and the remake had two::

    $7E69  LDA $7935,Y / CMP $7947   same room as the selected one?
    $7E71  CPY $64FB                 not the selected one themselves?
    $7E76  LDA $6501,Y / BNE $7ED2   **not in a duct**

Someone crawling the vents still carries the room's id, so without the third
test they were listed under "also here:" as if standing next to you. Extracted
as `co_occupants()` so it is testable at the ROM routine's own boundary.

The ROM filters the *listed* crew only - `$6501,Y` indexes the candidate, never
`$64FB` - so a duct-crawler is still shown the room's occupants. Asymmetric, and
left as found.

### Get item and Leave item are two rows, not one

    draw_item_row2  $8387 -> $05D6 = row 11   " Get item "
    list_room_items $83E0 -> $05FE = row 12   "Leave item"

Independent conditions: Get appears iff the room scan found an object
(`$836F CPX #$FF`) with **no test of what the character is carrying**, Leave
appears iff they are carrying one (`$83DA CPX #$00`). Both at once is normal.
The remake mapped both categories to slot 11, so with an item in the room *and*
one in hand the entries collided and Get came and went. `panels.py` had also
labelled row 12 "the rule between the red and purple blocks"; it is where Leave
item goes.

### Not a bug: the Engine 2 duct really does run east, and across decks

Reported as suspicious because Engine 2 sits at the map's eastern extreme. The
compass table is not geography. Column 18 reads north 17 (Engine 1), **east 7
(Computer)**, south 25 (Life Suppt), west 11 (Corridor 4) - and Computer is
`$7569` deck 0 against Engine 2's deck 1, so the duct crosses Middle to Upper.
The remake reproduces it exactly. Reaching rooms the doors do not is the point
of the ducting (D-086); a self-referencing entry is how "no exit" is encoded,
which is why Engine 1 offers only south.

**Action:** all four filed and fixed or confirmed; no change for the duct.

## DISC-245 - the attack banner, the portrait sprite, and a debug overlay

**Found/done:** 2026-08-15, same report.

### "Alien attacking <name>" - row 23, and entirely missing

`find_crew_with_alien ($8C49)` walks slots 1-7 for the lowest-numbered crew
member sharing the Alien's room **and** duct-space (`$8C56 CMP $6501`) with
health >= 2. If that victim is the character being viewed (`$8CE1 CPY $64FB`),
the ROM writes 16 bytes from `$8BC4` - "Alien attacking " - to `$0798` = row 23
col 0, then ten name bytes from the roster table `$A65E` to `$07A8` = col 16.
`$8CCC` blanks the row the moment no victim is found.

The same `$8CE1` gate already drove the siren and the animation (D-096), so the
banner joins them and the three arrive and leave together.

Decoded on the same path: **`$8C76` is "ATTACK"**, written to `$064E` = row 14
col 30 - the Special band's first slot. That is the ROM's own narrow window for
the option the remake deliberately offers on a wider one (D-169).

**Stale claim corrected:** `play.py` said row 23 "stays blank in every capture".
It carries this banner; the captures were taken while nothing was attacking.

### The portrait is a sprite, so the deck plan cannot take it away

`place_selected_char_sprite ($6667)` writes sprite 2's registers and nothing
else - `$D005` Y=169, `$07FA` pointer `$BC`+slot, `$D029` colour from the duct
flag, `$D004` X=28. No deck template, no `$7569`. Sprites are drawn by the VIC
over whatever is in the character screen.

The remake had that blit **inside `_draw_deck`**. The Narcissus draws a cockpit
instead of a deck plan (D-144), so boarding the shuttle silently removed the
portrait. Lifted out and drawn on both paths.

### A debug overlay, explicitly not the original

Ctrl+3 on the game-selection screen toggles markers for the Alien (light red)
and Jones (light blue), using the same crew figure the real location marker
uses. There is no such mode in the ROM. It is deliberately given the same chord
shape as the ROM's real Ctrl+1/Ctrl+2 so it cannot be hit by accident, and is
confined to the renderer: tests assert it is off by default, that drawing with
it off is byte-identical, and that it never mutates the simulation.

**Action:** implemented; the debug mode is recorded here as a deliberate
non-replica addition so a later audit does not mistake it for decoded
behaviour.

## DISC-246 - the ATTACK row's window was decodable; D-169 checked the wrong latch

**Found/done:** 2026-08-15, following DISC-245's decode of the attack path.

D-169 examined `$64BB`, found every reader of it to be presentation (the IRQ,
both movement-blip guards, the sprite animation), and concluded that narrowing
the ATTACK menu row to the ROM's real window would mean lifting a presentation
latch into the simulation. It kept a deliberate superset - "shown exactly when
firing it would succeed" - and recorded the decision.

The reasoning about `$64BB` was correct. It simply is not what gates this row.

`$8C76` ("ATTACK") reaches `$064E` = row 14 col 30 from the attack path at
`$8CD9`, and the entry condition for that path is
**`find_crew_with_alien ($8C49)` returning a victim, and `$8CE1 CPY $64FB`
matching it against the selected character**. Both are ordinary simulation
state. Nothing had to be lifted, and the superset is retired.

### What the finder actually tests, and two the remake had wrong

    $8C4B  LDA $7935,Y / CMP $7935   same room as the Alien (slot 0)
    $8C53  LDA $6501,Y / CMP $6501   same *space* - both surfaced or both ducted
    $8C5B  LDA $7D45,Y / CMP #$02    health >= 2
           BCC skip

- **The duct test is a comparison, not a surfaced check.** The remake required
  `not alien.in_duct`. `$8C56` compares the two flags: an Alien in the vents
  engages a crew member in the vents, and ignores one standing in the room.
  Both directions were wrong.
- **`CMP #$02` was missing**, so a crew member already down was still offered
  the option and still counted as the Alien's target.
- **The scan stops at its first match.** With two people in the room the Alien
  engages the lower-numbered one and `$8CE1` offers ATTACK to that one alone;
  the remake offered it to everyone present.

Implemented as `command_monitor.crew_with_alien`, returning a crew id.

### The narrowing exposed three nondeterministic tests

`test_remake_menu.py`'s `_sim()` helper is `Simulation()` with **no seed**, and
the opening death and its 3+3 seating are random (DISC-224/229). Three ATTACK
tests put the Alien in the selected crew member's room and asserted the option
appeared - which, under the real rule, depends on whether anyone lower-numbered
happens to share that room. They passed or failed by roll. The superset had been
hiding it, because it offered the option to every occupant.

Each now clears the room first, so the crew member under test is the one the
scan finds. Confirmed stable over repeated isolated runs; previously the same
test passed in a file run and failed run alone.

**Action:** D-169's superseded explanation deleted from `menu.py` rather than
left beside the new code, and five stale claims from this pass's work
registered in `SUPERSEDED_CLAIMS` (this one, the Narcissus's missing `$7569`
entry, the 10/14/10 split, row 23 "blank", and row 12 as "the rule"). The guard
was confirmed to fail on a reinserted claim.

## DISC-247 - the mixer does not survive sleep, and fails silently when it does not

**Found/done:** 2026-08-15, the Windows-quality pass.

SDL audio devices frequently do not survive a machine suspend. Every audio call
in `render/audio.py` is already wrapped in `except`, so this is **not** a crash
— it is the game continuing to play, perfectly, in total silence. That costs two
mechanics rather than being cosmetic: the heartbeat is composure-paced (D-145),
and the tracker ping carries information the player acts on (D-150).

Two things make it unrecoverable without deliberate work:

- **`pygame.mixer.init()` is a no-op when the mixer is already initialised**, so
  the existing call sites cannot revive a dead device. It has to be torn down
  with `mixer.quit()` first.
- The cached `Sound` objects in `_sfx_cache` belong to the device that went
  away, so they have to go with it.

`_rebuild_mixer` does both, and also drops the live tracker/heartbeat channels
and the attack latch, all of which referenced the old device.

### Detecting the resume needs no platform API

`time.time()` is wall clock and jumps across a suspend. `time.perf_counter()` is
monotonic — on Linux `CLOCK_MONOTONIC`, which by definition does not advance
while suspended. **Their divergence is the signal.** A frame hitch, however
long, moves both by the same amount; only a suspend separates them. The
threshold is 5 s, far longer than any legitimate hitch and far shorter than any
real sleep.

This is the same clock property that makes the game's *timing* survive sleep
(DISC-242's analysis): `app.py`'s loop rebases with `last_tick = frame_start`
rather than accumulating, so a resume costs exactly one tick and cannot
fast-forward the simulation. Audio was the one subsystem that did not get that
protection for free.

**Action:** checked once per frame from `poll_input`. Tested with both clocks
under `monkeypatch` — ordinary frames and a 60 s stall are not resumes, an hour
of wall clock against 20 ms of monotonic is, and a test asserts the check is
actually called each frame, since a guard that never runs protects nothing.

## DISC-248 - the two inputs a gamepad cannot reach, and the invention next door

**Found/done:** 2026-08-15, closing the Windows-quality pass.

The pad covered the four directions and fire. Two inputs had no pad equivalent
at all: **Escape**, and the game-selection screen's **Ctrl+1 / Ctrl+2** chord.
The second is not cosmetic — without it a controller cannot start a game.

**The trap is what to bind them to.** FV-1c1/1c2 *removed* an invented up/down
cursor and fire-select from that exact screen, because the ROM has neither:
`$5F36` polls for the chord of the option you want. Binding fire to "start the
full game" would reinstate the invention while looking like an accessibility
fix.

So the chords go to **dedicated** buttons (south = "1", east = "2", back =
Escape) and fire is left doing nothing on that screen, exactly as in the ROM.
That keeps the model — press the control for the option you want — and changes
only which physical control produces it. A keymap, not a mechanic. The
load-bearing test asserts that a non-chord button produces *nothing* there.

**A detail the tests found:** the edge detector needs the release frame. The
first test helper pressed and released without polling in between, so
`_joy_buttons_was` still held the button and the next press was swallowed. Real
frames always poll, so this was a test artifact — but it is the same shape as a
real bug (an edge detector whose state is only advanced on one side), so the
helper now performs a full press-and-release.

**Action:** the Windows-quality pass in `todo.md` is complete. The pad shim is
recorded here as a deliberate non-replica addition, alongside the Ctrl+3 debug
overlay (DISC-245), so a later audit does not mistake either for decoded
behaviour.

## DISC-249 - `c64.py` was two things, and one of them was on the wrong side

**Found/done:** 2026-08-16, the follow-up DISC-240 filed.

`render/c64.py` held a **palette** — the Colodore RGB values, a rendering choice
that could be swapped for VICE's older set without changing a single fact about
the game — and the **sixteen colour numbers**, which are ROM truth and appear
directly in the decoded tables (`$7000`, `$7440`, `paint_map_colors $7993`).

Only the second belongs below the render boundary, and the mismatch had already
produced a visible wart: `screens/` stores indices rather than RGB *precisely
so it does not depend on a palette*, and then imported `render.c64` to get the
index names. The dependency ran backwards.

It was safe — `render/__init__.py` is deliberately pygame-free, so the import
cost nothing at load time — but safe is not the same as right. The guarantee
depended on a property of a *different* module's `__init__`, so the next person
to put something pygame-shaped there would have broken `screens/`'s headless
contract from a distance, with nothing local to warn them.

The names now live in `screens/colours.py`. `render.c64` keeps `PALETTE` and
`rgb()` and re-exports the names, so `c64.WHITE` still works at its ~120 call
sites — that direction (render -> screens) is the correct one, and `__all__`
makes the re-export explicit under `strict = true`, which is what mypy demanded
the moment the definitions moved.

**Enforced rather than documented.** An AST walk over `screens/*.py` fails on
any import naming `render`, confirmed by injecting one. A companion test pins
that the palette did **not** follow the names down: `screens.colours` must have
no `PALETTE` and no `rgb`.

**Action:** the `todo.md` follow-up is closed. `frontend.py`'s by-screen split
remains the last open item.

## DISC-250 - the end screen comes out whole; the text toolkit is the next cut

**Found/done:** 2026-08-16, the last item DISC-240 filed.

`frontend.py` was 1,651 lines and at least four screens. Rather than eyeball the
split, a call graph over its 27 methods decided it — the same method D-191 used
on `pygame_app.py`, and it found the same kind of thing reading would not.

### The ending was the clean cut, and the graph proved it

`_draw_end` (104 lines) and `_draw_breach_animation` (35) call only
`_blit_cells`, `_blit_wrapped` and each other. Of the **24 module-level names
they touch, all 24 are used by nothing else in the module** — every ending
string, every row constant, the whole breach-spiral machinery. Even `_MENU_BG`,
whose comment calls it "the menu screens' green field", turns out to be
referenced only by the end screen.

Three contiguous blocks, so the move was mechanical: `frontend.py` 1,651 ->
1,458, `endscreen.py` 282.

One thing the line-range analysis missed and mypy caught: `_BREACH_CELLS_PER_
FRAME` is a **class** attribute, not module-level, so it did not appear in the
module-scope scan. Two more errors named the `constants` import the moved code
needed. The protocol module earned its keep again — `_blit_cells` and
`_blit_wrapped` had to be declared in `RendererState` for the new mixin to
type-check alone under `strict = true`, which is exactly what that module is
for.

**Verified byte-identical, not just green:** 70 renders (14 screens x 5 frame
counts) captured before and compared after. Identical.

### The next cut is the text toolkit, and the graph already names it

Nine methods — `_blit_cells`, `_blit_petscii`, `_blit_center_keyed`,
`_blit_wrapped`, `_blit_c64_text`, `_blit_screen_code`, `_blit_center`,
`_blit_at`, `_blit_tm`, about 174 lines — have **zero internal dependencies and
everything else depends on them**. That is a self-contained toolkit, and
extracting it is what would make the remaining screens (welcome+exit advert
~259 lines, opening+notice ~103, intro legend+prompt ~101, loading ~75,
title+egg ~57, selection 36, instructions ~62) separable at all.

Not done here, deliberately: the nine live in nine scattered ranges rather than
three contiguous ones, and each would need a `RendererState` declaration. That
is a bigger, messier change than the one that was ready, and there is no reason
to bundle them.

**Action:** filed in `todo.md` as the follow-up, with these counts, so the next
pass does not have to re-derive the graph.

## DISC-251 - the text toolkit was what held `frontend.py` together

**Found/done:** 2026-08-16, the follow-up DISC-250 filed with its evidence.

Nine methods — `_blit_cells`, `_blit_petscii`, `_blit_center_keyed`,
`_blit_wrapped`, `_blit_c64_text`, `_blit_screen_code`, `_blit_center`,
`_blit_at`, `_blit_tm`, 174 lines — moved to `render/text.py`.

The call graph had already named this cut, and re-measuring before the move
confirmed the shape exactly: the nine call **nothing** in `frontend` but
`_c64_or_sysfont` (already declared in the protocol), need **one** module-level
name (`_WELCOME_TM_SPRITE`, exclusive to them), and **thirteen** methods outside
depend on them.

That last number is the point. These were not merely shared, they were the
reason nothing else could move: every screen in the file — welcome, opening,
notice, intro, loading, title, selection, instructions — reaches for them, so
any attempt to extract a screen dragged the toolkit along with it.

### The extraction is measurably what unblocked the rest

Re-running the graph afterwards: of the 16 methods left, **11 now depend on
nothing but the toolkit** and are individually movable. Only two clusters remain
coupled — the welcome family (`_draw_welcome` with its border/option/tm helpers,
plus `_draw_exit_advert`, which shares `_draw_welcome_border`) and
`_draw_title` with `_title_egg_surface`.

`frontend.py` 1,651 -> 1,285 across the two passes, with `endscreen.py` 282 and
`text.py` 216.

**Cost, stated plainly:** seven more `RendererState` declarations, bringing the
protocol to 199 lines. That is the price of mixins that each type-check alone
under `strict = true`, and it is charged once per shared method rather than per
caller.

**Verified byte-identical over 84 renders** (14 screens x 6 frame counts), not
just green — the same check DISC-250 used, widened.

**Action:** `todo.md`'s last open item is closed. Splitting the remaining
screens is now possible but no longer pressing: at 1,285 lines with 11 of 16
methods independent, the file is no longer the obstacle it was, and picking
which screens share a module would be an arbitrary call rather than one the
graph makes for us.

## DISC-252 - the first five minutes were three undocumented commands

**Found/done:** 2026-08-16, from the question "does the music ship, or is it
re-rendered on install?"

It is re-rendered, and asking the question exposed that the whole first run was
poorly served. **Nothing the game draws or plays can be shipped** — the charset,
the sprites, the loader's BASIC and the SID intro are all the 1984 game's data —
so every install derives them from the user's own disk. Three commands do it:

    python -m alientools extract "...nib" --out out/
    python -m alientools chars
    python -m alien_remake.audio.intro

Only the first appeared in `README.md`'s Run section. The other two were
discoverable by running the game, reading `assets.report()` on stderr, and
following its instructions — which works, and is a poor way to spend the first
five minutes.

`--derive-assets` now does all three, finds the `.nib` beside you if you do not
name one, and finishes by reporting what is still missing.

**Measured rather than guessed:** the intro render is the slow step at ~8 s for
the full 102.4 s tune, producing an 8.7 MB wav. Extraction and charset decode
are instant. So the whole first run is under ten seconds for ~9 MB.

**Deliberately not automatic on launch.** A game that silently starts writing
9 MB the first time you double-click it is worse than one that tells you what to
run, and the startup report (DISC-241) already tells you. A test pins that
`--headless` derives nothing and creates no `out/`.

**What it cannot produce, and says so:** `basic.bin` and `chargen.bin` are C64
*system* ROMs and are not on the Alien disk at all. Without them the game runs
normally minus two details — the opening prints the victim's clean name instead
of the ROM-garbled one, and text outside the game's own charset falls back to a
system font.

**Action:** documented in `README.md`'s first-run section and the
command list, since "run these three things in this order" was exactly the
knowledge that existed nowhere.

## DISC-253 - two of the three win routes had never been flown

**Found/done:** 2026-08-16, looking for the highest-value work with `todo.md`
empty. A playtest was the best remaining input; this is the part
of one that can be done headlessly.

`FAITHFULNESS.md` still said, in the present tense, that
**"no win route is reachable"**, citing DISC-199. That was true on 2026-08-08
for about half a day: **DISC-204 closed it the same day** by finding the cause —
`$5658 CMP #$14` is a strict *equality* on a counter that only ever INCs, so a
room that overshot 20 became permanently safe. The claim outlived its own fix by
eight days, in the document whose job is to state how faithful the remake
currently is.

### What the tests actually covered

`tests/test_winnability.py` existed and passed, which is exactly why nobody
looked. Of the three routes it covered **one**:

- `ALIEN_KILLED` — a scripted hunter, end to end.
- `EVACUATED` — a test *described* the blockage (the launch needs every living
  crew member aboard, `$5B9E`, and the evac room obeys `ROOM_CAPACITY`, so six
  survivors can never all board), concluded "an evacuation win requires being
  reduced to <= 3 survivors first", and **left that untested**.
- `ALIEN_AIRLOCKED` — no test at all.

Both now fly. EVACUATED: cut to capacity, board, catch the cat, launch — with
the refusal asserted first, since "GO GET JONES" (`$5C33`) is a separate gate.
ALIEN_AIRLOCKED: 60/60 seeded attempts, and the *negative* half asserted too —
`$5ACC LDA $7D45 / CMP #$06 / BCC rts` means a **healthy Alien ignores an open
airlock entirely**, so the lock is a finisher for a wounded creature. Because
the survival roll is `rng >= damage`, a more wounded Alien is easier to vent.

### The harness lied before the game did

The first airlock run scored **0/60** and looked like a genuine dead route.
It was not: `SpecialOption(OPEN_AIRLOCK)` carries a `room_id`, my harness omitted
it, `_open_airlock` returned `False`, and no lock ever opened — so the vent loop,
which skips any lock that is not open, had nothing to do. Worth recording
because a scripted-reachability harness fails *silently* in exactly this way: a
route that is never actually attempted is indistinguishable from one that cannot
be won.

**Action:** a self-maintaining guard counts `WinRoute` against this file's own
source and fails on any route with no end-to-end test, confirmed by adding a
fourth. `FAITHFULNESS.md`'s stale paragraph is rewritten rather than annotated.

## DISC-254 - the heartbeat restarted on every fear tick, and the airlock cost 809 ms

**Found/done:** 2026-08-16, from the owner asking whether all the audio is
exported to wav before play, and reporting that the heartbeat loop "loses the
tempo".

Only the intro tune was a file. The six effects were synthesised from the ROM's
own SID writes on **first use** and cached in memory.

### The tempo skip: a restart, not a bad loop seam

It looks like a seam problem and is not. `render_pulse` emits `periods` blocks
of exactly `per_beat` samples, so the clip is a whole number of beats and
`play(loops=-1)` joins cleanly - now asserted.

The real cause is in `_update_heartbeat`. `fear_alert ($4E16)` buckets composure
hard - `heartbeat_divider` is `min(composure, 4)` - so the eleven fear values
collapse to **four** dividers: 0-1 both beat at 15, and **4 through 10 all beat
at 40**. `_heartbeat_sound` already keys its cache that way.

The change-detection did not. It compared **raw fear**, so a crew member ticking
6 -> 7 counted as a rate change: the loop was stopped and the *identical* clip
restarted from sample zero, mid-beat. Seven of the eleven values share one
divider, so this fired constantly, and what the player hears is the beat losing
its place. Walking fear 4..10 and back produced **10 restarts where there should
be 1**, which is what the new test asserts.

The fix compares the divider. A second site had to change with it: leaving the
play screen cleared `_heartbeat_composure` but would have left the rate stale,
so coming back would early-return on a match and the bed would never restart.

### The hitch: 809 ms, at the worst possible moment

Measured per effect: attack_alert 49 ms, grille 70, movement 78,
tracker_alarm 94, the four heartbeats 72-186 - and **airlock 809 ms**, because
its clip is nine seconds long. That is not a background moment. It lands exactly
as the player commits to blowing the lock, which can be the winning move.

`--derive-assets` now writes all nine clips (1.7 MB) alongside `intro.wav`, and
the renderer prefers them. **First-use cost 1,600 ms -> 86 ms**, airlock
809 -> 13.

The cache is guarded by the test that matters: the exported wav must be
byte-identical to synthesising the same effect. A cache that plays something
*different* would be a silent fidelity bug and would throw away the whole point
of deriving from the ROM's SID writes. It is also only used when the mixer
opened at the rate the files were rendered at, and synthesis remains the
fallback - the export is an optimisation, never a requirement.

**Not added to `assets.report()`**, deliberately: unlike a missing charset or
BASIC ROM, an absent clip changes nothing a player can hear, only how long the
first one takes. Reporting it would be noise.

## DISC-255 - three things computed every frame, and audio held six times over

**Found/done:** 2026-08-16, from the owner asking what else is worth rendering
out once. Profiled rather than guessed, and the biggest find was not what the
question implied - two of the three wins are caches in memory, not files.

### The mixer was decoding every clip six times over

`pygame.mixer.get_init()` reported **`(44100, -16, 6)`**. SDL negotiates the
*device's* layout, and on a 5.1 output every mono SID clip is expanded to six
channels: **1.7 MB of wav held as 10.1 MB resident**, the airlock alone 4.65 MB.

The SID is a mono chip. There is no stereo anywhere in the original, so six
channels is not just wasteful, it is unfaithful. `channels=1` alone does
nothing - SDL substitutes the device layout silently - it needs
**`allowedchanges=0`** to forbid the substitution, and it has to be requested
via **`pre_init`**, because `pygame.init()` opens the mixer before any of the
audio module's own code runs.

**10.1 MB -> 1.7 MB.**

### A glyph was rasterised once per character per frame

`_blit_cells` draws the front-end screens one 8x8 cell at a time (D-064,
correctly - SysFont metrics would compress the captured column positions). But
it called `_c64_or_sysfont` **per character**, and nothing cached the result:
profiled at **511 calls a frame** on the instructions screen, 15,330
rasterisations a second, the largest per-frame cost in the game.

A character in a given colour rasterises to the same pixels every time. With a
bounded cache:

    INSTRUCTION_PAGES   7.5 ms -> 0.90 ms
    NOTICE              2.5 ms -> 0.81 ms

The first frame still rasterises ~34 glyphs - one per *distinct* character on
the page, against ~511 drawn. That ratio is the whole saving.

Bounded deliberately: the key includes the text, and `_blit_at` passes whole
status lines, so an unbounded dict would grow with every distinct line. Only
entries of four characters or fewer are kept.

**Verified byte-identical over 84 renders**, which is the real risk here - a
cached `Surface` is mutable, and a caller blitting onto one would corrupt every
later use of that glyph.

### MENU1.prg was re-parsed thirty times a second

`instructions.pages()` reads the file and re-tokenises its BASIC. It was called
from inside the draw, so the instructions screen did that every frame for a file
that cannot change while the game runs.

Cached on the **resolved path**, not on `pages()`'s optional argument: with the
default `None` as the key a cached result survives `$ALIEN_REMAKE_ASSETS`
pointing elsewhere. A test caught exactly that.

### What was measured and left alone

Import cost is 67 ms total, renderer construction is ~300 ms of which ~285 is
SDL window creation - neither is cacheable, and `SPIRAL_CELLS`/`BREACH_SPIRAL`
compute at import in under 70 ms combined. Nothing there is worth a file.

## DISC-256 - a performance overlay on the Ctrl+3 debug mode

**Found/done:** 2026-08-16, owner request: frame rate, audio, memory and
latency on screen in debug mode.

Four rows on the play screen, under the existing Ctrl+3 toggle (DISC-245), in
its own module so a later fidelity audit sees immediately that nothing here is
a claim about the 1984 game::

    fps  28.7  frame 34.8ms  max 38.2
    lat   1.1ms  tick 28.8/s
    audio  44k/1ch 3clip 0.9M idle
    mem 44M  glyphs 2  ovl 0.01ms

Showing **both clocks** is deliberate: the display runs at 30 fps and the
simulation at `MAIN_LOOP_HZ` = 7.886, and they are *supposed* to differ. A
single "fps" figure would hide the one that matters when the game feels wrong.

### The measurement must not distort what it measures

Three decisions follow, and each was made after getting it wrong first.

**Frame rate is `_present` to `_present`** — the whole frame including the
overlay — not a timer wrapped around the drawing. An overlay that excludes its
own cost reports a frame rate the player is not getting.

**The overlay's own cost is displayed.** `ovl` is the last field, so the reader
can subtract the debugger from the thing being debugged.

**And it had to be made cheap, because it was not.** Composing the readout every
frame measured **1.13 ms against a 0.75 ms draw** — the instrumentation costing
half again as much as the game. Cause: the rows are longer than
`_GLYPH_CACHE_MAX_LEN` (DISC-255), so every one was a fresh SysFont render.
Rebuilding at **4 Hz** and blitting a cached panel took the overhead to within
measurement noise, and a 30 Hz frame-rate counter was unreadable anyway. A test
guards the overhead, because the natural way to add a field is inside the
compose.

**Memory is sampled once a second.** `GetProcessMemoryInfo` is a syscall;
polling it per frame to show a slow-moving number is the overlay changing the
answer.

### Notes

RSS is read through `ctypes`/`psapi` rather than adding `psutil` — a debug
readout does not justify a dependency. An earlier attempt returned 0 because the
struct had no `argtypes`/`restype`; it now returns `None` off Windows and the
row reads `n/a` rather than showing a wrong number.

The instrumentation itself is three `perf_counter()` calls a frame and stays
live rather than being branched on the flag: history that only began when the
overlay was enabled would show nothing for its first two seconds.

**Guarded the same way as the marker overlay:** off by default, byte-identical
across all 84 golden renders when off, and asserted never to touch the
simulation.

## DISC-257 - three play reports: two faithful, one my own debug tool lying

**Found/done:** 2026-08-16, from a debug-mode play session.

### "The Alien flips between rooms that have no doors" - correct, badly shown

Measured over 25 seeded games: **zero** surfaced hops between rooms with no door
between them. Every apparent teleport is duct travel. The duct network is a
separate graph reached through the compass tables (`$81EF`, D-086) and is
*supposed* to connect rooms the doors do not - that is the point of the ducting.
A typical run reads::

    corridor_6(d) -> computer(d) -> corridor_6(d) -> mess(d) -> corridor_6(d)

which is also the "flipping back and forth" - the random walk revisits the hub.

**The bug was mine.** `_draw_debug_markers` (DISC-245) drew the Alien at
`room_id` in one colour whatever space it was in, so a duct crawl was
indistinguishable from teleporting. The marker is now dark red while ducted, and
the overlay carries an explicit row - `alien recrtnarea DUCT` - because a colour
alone still asks the reader to remember which is which.

A first pass at counting the hops reported one bogus no-door move; the
classifier was crediting an in-place duct *entry* (same room, `in_duct`
flipping) as a room change. Fixed before drawing any conclusion from it.

### "ATTACK glitched to an ending" - faithful, and the comment was lying

Reproduced exactly: a harpoon fired into a room sitting at **exactly 5** takes it
to **exactly 20**, and `$5658 CMP #$14` destroys the ship on the spot. The
ending then reads "Parker brings the Nostromo back to earth" because `$64CF` is
set and the android is alive and not aboard the Narcissus, so
`draw_ending_survivor ($62B6)` overrides the destruct - all decoded, all correct
(D-077/DISC-230).

What was wrong is `constants.py`, which said the remake models the test as
**`>=`** "because ... overshooting 20 must not make a room immortal". It does
not: the code is `d == HULL_BREACH_THRESHOLD`, and DISC-204 reversed that
modelling *because* `>=` made the game unwinnable. Overshooting is a real
tactic - a harpoon's +15 can deliberately **burn out** a room, after which it is
permanently safe to fight in. Measured both ways: damage 5 -> 20 destroys the
ship, damage 14 -> 29 leaves the room safe forever.

The note had survived its own reversal by eight days. Registered in
`SUPERSEDED_CLAIMS`.

### "The Alien was in the room for a moment before attacking" - faithful

`$413C` sets a **40-pass (~5 s) hold** on the room *before* the attack roll at
`$4152`, and that roll misses on 7 of 16. So meeting crew always costs the
creature five seconds whether or not it strikes, which is what makes it read as
stalking rather than as a passing hazard (D-188).

**Action:** the overlay fix and the comment correction are the only code
changes; the two mechanics are left exactly as they are.

## DISC-258 - the ending was right about the flags and wrong about the people

**Found:** 2026-08-16. The player pushed back on DISC-257's "faithful" verdict
for an ATTACK that ended with *"Parker returned the ship safely to earth"* and
six survivors. They were right and I was wrong: an android bringing a
**hull-breached** ship home with a full crew is not a coherent outcome, and
saying "the flags are decoded" was not the same as checking the routine.

### What `hull_breach` actually does, and the remake did not

`$5D17` is reached from four sites - two weapon hits (`$4A91`/`$4AFA`), the
room-damage equality (`$565C`) and the auto-destruct expiring (`$5A43`). Past
the animation its tail is unambiguous::

    5DB5  LDY #$01
    5DB7  LDA #$01
    5DB9  STA $7D45,Y     ; EVERY crew member's health -> 1
    5DBC  INY / CPY #$08 / BNE
    5DC1  LDA #$64
    5DC3  STA $7D45       ; the Alien's own cell -> 100
    5DC6  LDA #$01 / STA $64CF
    5DCE  JMP endgame_dispatch

Health 1 is **below the acting threshold** (`$52C0 CMP #$02 / BCS`), so a hull
breach incapacitates the entire crew. They are not survivors. The remake set
three flags and stopped, so the ending counted six people as having come
through the ship being holed - and with the android alive, `draw_ending_survivor
($62B6)` reported the Nostromo brought safely home.

Implemented as `_hull_breach()`, with both call sites routed through it (the
auto-destruct path had the same omission). The Alien going to 100 is the same
statement from the other side, expressed as zero accumulated wounds because
that is how this model holds the cell.

### The weapon breach gates: decoded, measured, and NOT applied

Chasing the same report turned up a second and larger divergence. Room damage
from a landed hit is gated **before** the add::

    4A87  LDY $457F / LDA $653F,Y   ; harpoon
    4A8D  CMP #$05 / BCC $4A94      ; < 5  -> add 15
    4A91  JMP hull_breach           ; >= 5 -> the ship goes

    4AF6  CMP #$0E                  ; anything else: >= 14 -> the ship goes

The remake has only the corrosion path's `== 20`, which is why the same weapon
breaches in one situation and not another: a harpoon into a room at 5 lands on
20 and looks right, one into a room at 14 reaches 29 and does nothing.

**It was implemented, measured, and reverted.** With the gate at 14 a room takes
three hits before the next holes the ship, and across 16 seeded games with a
policy that respects the gate and retreats, the Alien never took more than 15 of
the 50 damage needed - **zero wins**. Corrosion set to zero did not rescue it,
so the cause is not the uncalibrated `ROOM_DAMAGE_ALIEN_PER_ACTION`.

The opcodes are not in doubt. What is missing is whatever makes the gate
survivable in the original - the per-hit damage to the Alien, how often a hit
lands, or a room-damage decay nobody has found. Until one of those is traced,
applying it would ship an unwinnable game, which **DISC-204 established is the
one outcome that must never ship**. Recorded at the call site, in
`constants.py`, and pinned by a test that fails if someone wires the gate in
without re-running the winnability sweep.

### A process note

Inserting `_hull_breach` split `advance()` in half - the method landed *inside*
it, orphaning steps 4-7 - and 13 of the 14 resulting failures were that, not the
mechanic. The one real failure was the winnability test, which is exactly the
test that should fail first when a change makes the game unplayable. It did its
job twice: once for the structural error and once for the gate.

## DISC-259 - the Alien is not stuck upstairs, it is just very slow

**Found:** 2026-08-16, player question: why does the Alien always stay on the
upper deck?

Measured before answering. Over 12 games of 4,000 ticks it never left deck 0 in
8 of them, reached deck 1 in 4, and reached deck 2 in **none** - and visited
only **13 of 35 rooms**. That looks like a movement bug.

It is not. Every mechanism checks out against the ROM:

* **It starts on deck 0.** `$7935`'s slot 0 is the Alien's own room and reads
  `$00` - AIRLOCK 1. (Slots 1-7 are the crew, `06 06 06 1B 1B 1B 00`, which is
  exactly `CREW_START_ROOMS`.)
* **The route graph is fully connected.** Walking the five tables from AIRLOCK 1
  reaches all 34 rooms and all three decks. But only **4 of the 169 entries
  cross a deck** - Livng Qtrs <-> Corridor 1, and Corridor 2 <-> CargoPod 2 -
  so crossings are rare by construction.
* **The band split is the ROM's** 3/2/2/2/3 over rolls 0-11, with 12-15 taken by
  the duct path. My first count made band 4 look seven rolls wide by including
  rolls that never reach the band code.
* **A move costs 60 passes** (`$8A4A LDA #$3C`), about 7.6 s at `MAIN_LOOP_HZ`.
* **Self-referencing entries are accepted, not re-rolled** (D-159), and the
  creature then holds position for another 60 passes. `mess` self-refers on two
  of five bands, which is why it accounts for 37% of all Alien-ticks.

Run for 20,000 ticks instead of 4,000, **13 of 20 games reach deck 2**, first
arrival between ticks 5,060 and 9,660 - **ten to twenty minutes of play**. A
typical game is shorter than that, which is the whole answer: the Alien does
work its way down the ship, just not within the time most games last.

**Action:** no behaviour change. Two tests added, because "faithful but rare" is
indistinguishable from "broken" without one: the first asserts every room and
deck is reachable through the route tables, the second that a long game actually
sees all three decks. A regeneration that cut a deck off would otherwise look
entirely normal.

## DISC-260 - a random Alien start, as a flagged added rule

**Found/done:** 2026-08-16, owner request following DISC-259: could the Alien
spawn anywhere and then work up and down the decks with the same rules?

Yes, and the movement needed no change at all - DISC-259 established the route
tables already reach every room and every deck. The only thing making the
creature's first ten minutes predictable was **where it begins**: `$7935` slot 0
is `$00`, AIRLOCK 1, upper deck, every single game.

`AlienStart.RANDOM` seeds it anywhere instead. Measured over 40 games: the fixed
start gives 1 room and deck 0 only; the random one gives **24 distinct rooms
spread 9/19/12 across the three decks**. Nothing about how it moves is touched.

**Two exclusions, both deliberate.** The crew's own starting rooms, so a game
cannot open with the creature already standing among them - the ROM's AIRLOCK 1
is well away from both crew clusters (`$7935`'s `06`/`1B` groups), so a purely
uniform draw would be *harsher* than the original rather than merely different.
And the Narcissus, which is off the deck plans entirely (deck 3, DISC-244) and
would put it somewhere the player cannot look.

**Not the default.** `--alien-start airlock` stays the shipped behaviour and a
test pins it, because a silently-changed default is how a replica stops being
one. `--alien-start random` opts in.

### The cp1252 trap, for the second time

The new flag's help text shipped with an em-dash and rendered as `?`. DISC-241
had already held `assets.report()` to ASCII for exactly this reason; the lesson
did not generalise on its own.

Now automated: a test runs the real parser and asserts everything argparse
prints is ASCII. It immediately found a **pre-existing** one nobody had noticed -
`§` in `--awake-crew`'s "GAME_SPEC §7" - so the guard paid for itself on the
commit that introduced it. Seven non-ASCII characters in `main()` are now zero;
the module's own prose keeps its typography, since only the strings argparse
prints are constrained.

## DISC-261 - four play-report items: the box's name, the second slot, Escape, the border

**Found/done:** 2026-08-16, closing the player's outstanding list.

### The cat box is renamed when Jones is inside, and that name IS the flag

`guard_6580`'s catch path copies ten bytes from **`$8874` = "Jones:Box"** over
the item-name table's type-8 entry at `$7CC3` (`$87DC`/`$8827 STA $7CC3,Y`), and
`$8827` restores the Net's own name at `$7CB9` on the way past. So the panel row
the player is looking at changes from "Cat Box" to "Jones:Box" - the only
confirmation the original gives that the cat is in the box.

The rename is load-bearing beyond the display: **`$5B33 CMP $7CC3`** is the
launch validator's "GO GET JONES" test, which reads the *name*, not a flag. This
remake keeps `jones_caught` as the flag and derives the label from it - the same
fact in the shape this model holds.

### A crew member carries two items and the panel shows both

The two USE rows (9 and 10, DISC-232) are not one row plus padding. Objects
carry their holder in their own location byte and `list_room_items` splits on
it::

    83AA  CMP $8299   ; location == slot + $A0 -> row 9  ($0586), records $829A
    83C1  CMP $7947   ; location == slot + $80 -> row 10 ($05AE), records $829B

**`$829A` is the active slot.** Every action reads it (`$45EE`, `$4646`), and
`$4679` reaches the second item only by copying `$829B` over `$829A`, running
the check, and putting it back. So the top row is what is in hand and the row
beneath is the spare; choosing the spare promotes it.

The remake listed only `crew.holding`, so the second item was carried but
invisible and unreachable.

**The bug behind the bug:** `holding` is a *property* returning `carried[-1]`,
and its setter did nothing when handed an item already in the list. So the new
swap set a value the property already reported and the list never moved. The
setter now promotes, which is simply its own contract - the getter defines "in
hand" as the last element, so assigning has to put it there.

### Escape backs out; it does not close the game

The ROM has no abandon key at all - the only exit is `Q QUIT` on WELCOME, and
the end screen's own way back is `$646F -> $5E74` to TITLE. Escape ended the
*process* from any screen, so a mis-hit mid-game lost the game.

Now an abstract `InputEvent.ABANDON` (the renderer does not own the screen
graph, and the pad's back button maps to the same intent), handled by
`GameFlow.abandon()`. On WELCOME there is nothing to back out of, so Escape
still quits there and only there. Deliberately **not** "quit on a second press":
ending the program is `Q QUIT`'s job.

### The border noise was drawing at window resolution

A regression from DISC-242. The band thickness was `max(1, s)`; the sweep that
deleted every scale factor rewrote it to `1`, because it **read as a coordinate
and was actually a thickness**. The bands became one screen pixel each, so at 4x
the border showed 800 hair-thin stripes against a picture drawn at 200 raster
lines - "very high resolution", exactly as reported.

Now derived from `field_rect()`, so one band is one C64 raster line whatever the
window is. Counted rather than asserted on the constant: ~200-264 bands at every
size, against 264 -> 1080 before.

## DISC-262 - a quick front end, Escape as the panel's quit, and a patient cat

**Found/done:** 2026-08-16, owner's instructions. Three added rules and one
measurement that changed what the third one should be.

### The boot chain is three screens

`FrontEnd.QUICK` is now the **default**: title -> back-up notice -> the
Ctrl+1/Ctrl+2 selection. It skips both LOADING cards, the WELCOME menu and the
EXIT advert - loader ceremony for a disk that is not loading, a joystick prompt
for a keyboard, and a `Q QUIT` row nobody uses. `--front-end classic` still
plays the original's full chain and the tests that assert it now ask for it by
name rather than being deleted.

**This is the first place the remake's default is knowingly not the ROM's**, and
it is worth saying plainly rather than burying: everything skipped is front-end
furniture, no decoded gameplay is touched, and the faithful path is one flag
away.

**One bug the change surfaced.** `TIMED_SCREENS` was built at import time from
`_timed_next()` with no argument, so it silently took the *quick* table - and a
classic boot then sat on LOADING_MENU forever, because that screen was no longer
considered timed. It is now the union of both tables. Two failing tests looked
like front-end regressions and were this.

### Escape is the panel's own `quit` row

Third meaning in a day, and the right one. It ended the *process* (a mis-hit
lost the pass), then abandoned to the front end (still too much mid-order),
and now does what choosing `quit` in the PCS menu does: `back()`, from a crew
member's order list to the CONTROL list. Off the play screen there is no panel
to leave, so it abandons instead - and `abandon()`'s destination follows the
front end, since QUICK has no WELCOME to return to.

### Jones: the odds are the ROM's, the second chance is not

The report was that he is far harder to catch than remembered. Both halves of
why are decoded:

* the per-character thresholds `$883C` give the **cat box 6-19%** and the
  **net 31-44%** (`$87A1` improves the roll by four), and
* `$878C LDA #$01 / STA $657F` slams his move counter to 1 **before** rolling,
  so a miss costs more than the attempt - the cat bolts (D-160).

Together that is one shot per encounter at 6-19%. `JonesCatch.PATIENT` (the
default) drops only the spook. Measured over 10 seeded games with a crew member
walking to him and grabbing: **cat box 3/10 caught at a median 1,283 ticks ->
6/10 at 310**; net 5/10 at 285 -> 7/10 at 146. A test asserts the odds are
*identical* in both modes, because the added rule must change how many attempts
you get and never their probability.

Worth surfacing to players: the net is three times the box and the game never
says so.

### A note on probes

Three attempts at testing the spook were wrong before one was right. Reading the
move counter after `advance` shows 40 in both modes (it reloads on the pass he
steps); watching for a room change is unreliable because his route can return
him to the same room. Calling the handler directly and reading the counter
before any tick is the only probe that measures the thing itself.

## DISC-263 - the boot order corrected, and the selection screen says what it takes

**Found/done:** 2026-08-16, owner's correction to DISC-262.

### I dropped the publisher card and put the title first

DISC-262 built the quick chain as **title -> notice -> selection**. The owner's
order is **publisher spiral -> back-up notice -> Joseph Conrad eggs ->
selection**, which is right, and the mistake is worth naming because the screen
names invite it:

* `LOADING_MENU` is the **GREEN VALLEY PUBLISHING spiral** - the colour-RAM
  animation, not a caption.
* `LOADING_PLAY` is the **"LOADING.... / PLUG JOYSTICK INTO PORT TWO"** card,
  which is the one the owner asked to skip.

Two screens whose names both begin "LOADING", where the one that sounds like a
loading card is the publisher animation. I skipped both on the strength of the
name and lost the spiral with it. Now: quick keeps `LOADING_MENU`, drops
`LOADING_PLAY`, and both front ends open on the same publisher screen and
diverge only after the notice.

### "PRESS 1" has to mean press 1

The selection screen printed **CONTROL:1 / CONTROL:2** because `$5F36` polls for
that chord, and FV-1c1/1c2 went to some trouble to enforce it. Under the quick
front end it now prints **PRESS 1 / PRESS 2** and takes the bare key.

The two are wired to the same switch deliberately. Printing one instruction and
obeying another is the failure mode here, and it is exactly what would have
happened if the prompt and the key check had been changed independently -
CLASSIC still prints the chord and still requires it.

### 0 arms the debug mode

On the selection screen only, and only under the quick front end, so it cannot
be hit mid-game. **Correction (2026-08-16):** this entry claimed `Ctrl+3`
still toggles it anywhere. It does not, and never did - both keys sit in the
`screen is not PLAYING` half of the input dispatch, so neither reaches the
play screen. Debug has to be armed before the game starts. When armed before a game
starts the screen says **DEBUG ON**, because a mode you cannot see is one you
forget you left on - the marker overlay would otherwise appear unexplained
several minutes later.

## DISC-264 - the CRT layer: a tube that runs faster than the game

**Found/done:** 2026-08-16, owner's request.

An analog-CRT presentation over the game - NTSC chroma bleed, scanlines, RF
noise, phosphor bloom, and a scrambled-cable glitch when the view changes.
**None of it is the original.** It is a look, `--crt off` by default, and the
tests below exist to keep it from ever becoming a fidelity claim.

### The seam was already there, and it decided the design

DISC-242 reduced presentation to one choke point: everything draws at 320x200
into `_surface`, and `_blit_field` scales once at present time. The chain reads
`_surface` and writes the window, between those two steps. `_surface` is never
touched, so all 84 golden renders and every replica test keep passing unchanged
- and the mental model is the honest one: the game generates a video signal, the
CRT is what mangles it.

Everything runs at **native resolution**, which is the owner's requirement
("noise and distortion true to the limited lines of an old CRT, game graphics
resolution-independent underneath") and also a 16x saving: the same chain at
1280x800 measured ~55 ms a frame against ~5 ms at 320x200. It looks better too.
Noise generated per output pixel at 4x reads as film grain; noise at the field's
own line pitch reads as a CRT.

Deliberately absent: **barrel and pincushion distortion** (owner's instruction),
and the vignette that usually travels with them.

### The tube refreshes at 120 Hz over a 30 fps game

The owner's requirement, and it falls out of the model rather than fighting it.
The game draws a signal 30 times a second and the simulation ticks 7.886 times a
second; the tube redraws whatever is on it 120 times a second with the noise,
roll and interlace phase moving on. `PygameRenderer.idle()` is where it happens:
the app loop hands the frame's leftover time to the backend instead of sleeping
it away, and the backend spends it re-presenting the *same* field. No game state
is read and nothing is redrawn into `_surface`, so the game looks exactly as it
did. The final part-slice is slept rather than squeezed, so a tube frame can
never delay the game frame that is due - if a refresh overruns, the rate drops
and nothing else does.

`CrtProcessor.advance()` takes **real elapsed seconds**, never a frame count, so
the look does not change with the rate the loop actually achieves.

### Blurring all three channels is not chroma bleed

The obvious implementation - blur the image horizontally - **looks out of focus,
not analog**, and it destroys exactly the hard pixel edges D-056 exists to
protect. NTSC starves chroma of bandwidth while luma stays sharp; that asymmetry
*is* the artifact. The chain separates luma (Rec.601), blurs only the chroma,
and recombines. `test_chroma_bleed_keeps_luma_sharp` pins it with a bright
column on black: a luma blur puts a quarter of its brightness into each
neighbour.

That test then immediately found a real bug in the fixed-point arithmetic. The
weighted sum was accumulated in int16, where white overflows -
`77*255 + 150*255 + 29*255 = 65025` against a 32767 ceiling - so **every
highlight wrapped negative and came out dark**. The white column measured 189
where it should read 765. The A/B images I had already looked at and called
"good" contained it. Bright-value overflow is invisible on a mid-tone test
frame and invisible in a screenshot you are judging for atmosphere.

### Lookup tables bought the 1080p case

Three stages multiply 192,000 bytes by a constant fraction, and numpy does that
by promoting the whole array to float. A 256-entry `np.take` is identical for
uint8 input at half the cost. With the tables, per refresh:

| window | --crt off | subtle | full |
|---|---|---|---|
| native 384x264 | 0.02 ms | 5.43 | 5.57 |
| 1280x800 | 1.49 | 6.71 | 7.41 |
| 1920x1080 | 2.58 | 7.96 | 8.21 |

Budget at 120 Hz is 8.33 ms. Before the tables, 1080p was 8.97 and missed it.
Chroma bleed is the largest single stage (2.11 ms of the chain) and is the one
to cut if headroom is ever needed again.

### The triggers cross no boundary

The three view changes the owner named - quitting a character, selecting a
different crew member, opening INDICATE - all happen in `MenuController`, which
also owns the deck change he asked to "gently glitch". Rather than let the menu
call the renderer, it bumps `view_epoch` and records how hard the change was;
the renderer notices the epoch moved and owns the timing. Same boundary as the
debug overlay: nothing on the sim side knows the CRT layer exists.

The epoch is consumed **even when the layer is off or the screen is not
eligible**, or every menu move made during the front end would fire at once the
instant the play screen appeared.

### numpy was a live packaging bug

`pygame.surfarray` - the supported way to reach pixels - does not work without
numpy, and it was never declared. It was present only because the dev venv was
built with `--system-site-packages`, so `pip install -e .[remake]` into a clean
environment has always produced a game that would fail the moment anything
touched a pixel array. Now declared. cv2 was declined: a 60 MB wheel for a 6 MB
game, doing what a handful of numpy lines do at 320x200.

**Action:** shipped. `render/crt.py`, `tools/crt_bench.py` (the A/B harness -
tuning an analog look without an A/B toggle is guessing),
`tests/test_crt_layer.py`, `--crt off|subtle|full`. Default stays **off** until
the owner has judged the look in motion; the shipped default is the one open
question left open in the CRT plan.

## DISC-265 - the CRT tuning pass, and a degauss that is not a small scramble

**Found/done:** 2026-08-16, owner's play-test of DISC-264.

The owner ran the layer and came back with numbers and one structural
correction. The numbers are now the defaults: noise 8, scanline depth 0.15.

### "The gentle effect looks pretty identical"

It was the same code path at a third of the amplitude, and that is exactly what
it looked like - the full effect turned down. A real degauss is a **different
fault**, not a smaller one:

* a scramble is the *channel* losing lock - rows displaced against each other,
  vertical roll, gated inversion;
* a degauss is the *monitor* settling - the whole image wobbling together with
  a decaying ring, colour a pixel off register, brightness dipping as the coil
  loads the supply. Nothing tears and nothing rolls.

`_degauss()` is therefore a separate method sharing no code with `_scramble()`,
and two tests pin the distinction by measuring it: the degauss must leave every
row at the same horizontal offset, and the scramble must not.

**The general shape is worth keeping.** Two effects that differ only by a
parameter will read as one effect at two volumes, however carefully the
parameter is chosen. If they are meant to be different things, they have to be
different things.

### The full glitch: shorter, and slower

Also the owner's, and the pair is not a contradiction. It ran for 0.45 s with
its motion driven at `phase * 0.35`; it now runs 0.30 s at `glitch_speed`
(0.18). Less time on screen, but what happens in that time moves at half the
rate - which is what makes it read as an analog signal sliding rather than a
digital frame-shuffle.

Two more pieces bought the "smooth" the owner asked for:

* **Phosphor persistence** (`motion_blur`), a one-pole filter over the output.
  On a still picture it converges and is invisible; under a transient it is
  what turns a sequence of displaced frames into something that moves.
* **`scanline_blur`**, and the order matters: the softening goes on **before**
  the dark lines, not after. Blurring the finished pattern averages each dark
  line with the bright one beside it and cancels the scanlines outright - which
  is exactly what the first attempt did. Blur the picture vertically (the
  beam's spot profile), then lay the hard line pitch over it.

### A rolling raster bar, on wall-clock seconds

A slow hum bar, adjustable in the bench (`,`/`.` strength, `;`/`'` speed). Its
position comes from **elapsed seconds**, not the tube phase, so the speed is the
number in the status bar and nothing else - at `raster_speed` 14 a bar crosses
the 200-line field in about fourteen seconds. Only its own sixteen rows are
touched, which is why a per-row Python loop is cheaper here than any
whole-frame multiply.

### The scaling destination was costing a quarter of the budget

Adding those stages pushed 1920x1080 to 9.2 ms a refresh against the 8.33 ms a
120 Hz tube has. The fix was not in the chain at all: `pygame.transform.scale`
was **allocating a new 1920x1080 surface every refresh**. Passing a kept
destination surface took that step from 2.23 ms to 0.45.

| window | off | subtle | full | full, mid-glitch |
|---|---|---|---|---|
| native 384x264 | 0.02 | 6.19 | 6.63 | 7.78 |
| 1280x800 | 0.59 | 7.48 | 7.31 | 8.25 |
| 1920x1080 | 0.96 | 7.41 | 7.83 | 8.85 |

Steady state is inside the budget everywhere; the 0.30 s of a full glitch is
marginally over at large window sizes, which costs refresh rate and nothing
else - `idle()` simply performs fewer of them and the game frame is never
delayed. **The `off` column improved too** (2.82 -> 0.96 at 1080p): every player
was paying for that allocation, CRT layer or not.

**Action:** shipped. Defaults updated, `_degauss` added, bench gained the new
knobs plus `P` to print the current settings as a `CrtSettings(...)` line. The
shipped default is still `off` pending the owner's verdict.

### Second pass, same day: the owner's settings, and a degauss with a cathode bloom

The tuned line, straight out of the bench's `P` key and now the defaults:
`scanline_blur=0.2, motion_blur=0.6, raster_strength=0.13, raster_speed=22.0`.

The degauss gained **warp** - a smooth low-frequency bend across the field
rather than the whole image moving as one - and the **cathode bloom**, a soft
elliptical white that lights the face of the tube as the coil fires and fades
with the envelope. The bloom's shape is built once and only its brightness
changes, so it costs one `np.take` through the same cached tables everything
else uses.

Warp is where a tear and a bend become measurable, and that is now the test:
neighbouring lines in a degauss may not part by more than a pixel, while the
scramble's are required to fly apart. It is a better statement of the
distinction than the first version's "every row at the same offset", which
would have forbidden warp altogether.

**A scale bug the settings hid.** `_degauss` was handed `level`, which already
carries the `GLITCH_GENTLE` factor that selected the gentle path, and scaled by
it a second time - so `degauss_warp = 5.0` meant 1.5 pixels and the glow a third
of the number set. That is most of why the gentle effect read as invisible even
after it became its own code path. It now derives the pure decay envelope and
its settings mean what they say; a test asserts 12 px of warp produces at least
6 px of bend.

**And a probe that lied.** The first warp test measured row offsets with
`argmax` over a *striped* frame, which reports position modulo the stripe
period: a smooth one-pixel bend crossing a stripe boundary read as a
seven-pixel tear, and the test failed on correct code. One bright column and one
bright row, in different channels, cannot do that. Same shape as DISC-253's
harness that never opened the lock - **a probe coarser than the thing it
measures reports the wrong answer confidently.**

Measured with everything in, against the 8.33 ms budget: 6.5 ms steady and
8.3 ms mid-degauss at 1920x1080, 5.7 / 7.4 at native.

## DISC-266 - phosphor triads, and the one stage that belongs after scaling

**Found/done:** 2026-08-16, owner's request: "can the system emulate the pixels
on a CRT that are three small colors coming together to make the image?"

Yes, and it is the single exception to this layer's native-resolution rule -
for a physical reason rather than a convenient one.

### Why the mask is the exception

Everything else in `crt.py` runs at 320x200 because the artifact belongs to the
*signal*: chroma bandwidth, sync, noise, phosphor decay. A shadow mask does not.
It is a sheet of perforated steel behind the glass, and its pitch is a property
of the **tube**, not of what is being shown on it. So it stays a fixed number of
screen pixels while the game's pixels grow with the window, which is both
physically right and the only way it can exist at all: three phosphors need
three subpixels, and at 1:1 there is nowhere to put them.

Two consequences fall straight out and are now tested:

* The mask is **skipped below one triad per game pixel** (`scale < mask_pitch`).
  Drawn there it would eat the picture rather than draw it.
* The triad pitch **does not change with the window size**. A mask that scaled
  with the game's pixels would be a texture painted on the sprites; a real one
  is a fixed screen the picture is thrown against. At 3x the triads line up
  one-per-game-pixel; at 4x and 5x they beat against the pixel grid, exactly as
  a real set does with a signal whose dot pitch it does not share.

### It is a blit, not an array multiply

`shadow_mask()` returns a plain numpy array so `crt.py` stays free of pygame;
the renderer turns it into a Surface once per window size and applies it with
`BLEND_RGB_MULT`. SDL does that in C: **0.42 ms at 1920x1080**, where the same
multiply over two million pixels in numpy is twenty times dearer. Total cost of
the mask, including its gain, is about 0.8 ms.

### The gain, and where it has to live

Two of every three subpixels are dimmed, so the mask passes only
`1 - 2*strength/3` of the light - the picture would arrive about a fifth darker
than the signal. Real sets answer that by driving the gun harder, and so does
this: `mask_gain()` is applied inside the chain, before scaling, and highlights
clip exactly as they do on glass.

That split - shape at window size, gain at native - is worth stating plainly
because it looks like a mistake: the compensation for a stage that has not
happened yet is applied a step earlier. It is where it is because a LUT over
64,000 pixels is cheap and the same LUT over two million is not.

**Measured**, with everything on: 6.9 ms at 3x, 7.1 at 4x, 7.3 at 1920x1080,
against the 8.33 ms a 120 Hz tube has.

**Action:** shipped. `mask` / `mask_pitch` / `mask_strength` / `mask_stagger`
(slot mask against aperture grille), on by default in `--crt full` at 0.35 and
in `subtle` at 0.20. Bench keys: `` ` `` toggles, `O`/`P` strength, `U`/`I`
pitch, `R` swaps slot for grille. Note the bench's "print settings" key moved to
`T` to make room.

## DISC-267 - one family of transient, led by the chroma shift

**Found/done:** 2026-08-16, owner's tuned settings and four notes on the feel.

The settings, straight from the bench, are now the defaults: scanline depth
0.10, noise 7, interlace and bloom **off**, raster 0.06, mask off (strength 0.15
kept, so switching it on gives a light one), degauss warp 2.0, vertical roll
**off**.

Note what the owner turned off. Interlace, bloom and the phosphor mask were all
built, all liked in isolation, and all switched off in the mix - which is the
usual fate of effects judged one at a time. Keeping them as settings rather than
deleting them costs nothing; each is one branch.

### The chroma shift became the character of the whole layer

"I like the chroma shift effect. Use it for the switch between floors... use the
chroma shift for moving between floors and choosing new people or indicate."

So both transients now lead with colour separating from luma, and it is one
method (`_separate_chroma`) rather than two copies that would drift apart the
first time either was tuned. The difference between them is degree and shape:

* **crew / INDICATE** - a hard shift of `chroma_shift_px` (6 px) that decays
  with the transient, over the displacement wave;
* **deck change** - half that, swinging with the ring, so the colour visibly
  *springs back* into register instead of sliding once and fading. A test
  requires the offset to go positive, negative, and end at zero.

The cathode flash, built for the deck change, is mixed into both -
`degauss_glow` is therefore now `flash_glow`, and the shared code is `_flash()`.
Vertical roll is off by default, so the family is: colour tears off, the tube
flashes, the picture bends or slides, everything settles.

### The waves are re-rolled per firing

"Make the waves slightly random so it's not the exact same curves every time."

`_WaveShape` is drawn fresh on every `glitch()`: spatial frequency, phase,
amplitude, direction, and the degauss's ring frequency. A transient that traces
an identical path every time stops reading as interference and starts reading as
an animation - which is exactly what got noticed.

**Drawn from the processor's own seeded rng**, so a given seed still replays
byte-for-byte. A test asserts both halves of that: six firings must not all
produce the same curve, and two processors with the same seed must agree
exactly. Randomness that cannot be reproduced would mean a rendering test that
fails once a fortnight and never twice the same way.

### Two probes that were wrong before the code was

* The flash test read a *corner* as the unlit reference while `luma_invert` was
  on - which flips half the frame, making the corner 215 against a lit centre of
  164. The effect was right; the reference point was inside the inverted band.
* `_bare()` left the mask enabled, so the mask's **gain** (which lives in the
  chain, before the mask itself) brightened every measurement by a fifth.

Both are the same mistake in different clothes: a probe that assumes the rest of
the chain is neutral when it is not.

**Measured** with the new defaults: 5.3 ms steady and 6.9 mid-glitch at
1920x1080, against 8.33 - cheaper than before, because three of the stages the
owner switched off were among the more expensive.

**Action:** shipped. Bench keys changed with it: `C`/`V` is the cathode flash
(both transients now), `F`/`H` sets the chroma shift in pixels.

## DISC-268 - the deck change that never fired, and a tube that stopped at the field

**Found/done:** 2026-08-16, owner's play-test of DISC-267.

### Two constants that had to match, in two modules, with nothing linking them

"When the crew member changes floors the effect doesn't trigger."

`menu.GENTLE_VIEW_CHANGE` is **0.35**. `crt.GLITCH_GENTLE` was 0.35 too, until
DISC-265 lowered it to **0.30** while building the degauss. The renderer passed
the menu's number straight into `glitch()`, whose gentle test is
`strength <= GLITCH_GENTLE` - so from that moment every deck change took the
**scramble** path at a level of 0.35, a seventh of a full glitch: technically
firing, visually nothing.

Nothing linked the two values. The sim-side module cannot import the render
side, so they could not share a constant, and a comment saying "keep these in
step" is exactly the kind of instruction that loses. The fix removes the
coupling instead of restating it: the menu's number is now a **hint** classified
on the midpoint, and the renderer substitutes the CRT layer's own constants. The
two can drift freely and nothing breaks.

### And one deck change that fired nothing at all

Choosing a room from INDICATE LOCATION switches the map to that room's deck -
`menu.py` has called `select_deck` there since D-022 - and that path had no
glitch on it. Opening the list did; using it did not.

Three of the four view changes were wired by walking the list the owner named.
The fourth was a deck change that does not look like one in the code, because it
is written as *indicating a room* and the deck switch is a consequence.
**Wiring by intent finds the paths you can name; only reading every caller finds
the rest** - `select_deck` has four callers and two of them were unglitched.

### The tube stopped at the edge of the game field

"The effects should include the vic color bar areas."

They should, and the reason is not cosmetic: scanlines that stop at the edge of
the picture are the tell that this is a filter over a sprite rather than a
screen being photographed. The border is part of what the tube is showing.

The chain now runs on a **whole-screen canvas at native resolution** - the
window divided by the field's own integer scale, so at 1920x1080 it is 384x216
against the field's 320x200. That is the entire cost of covering the border: the
effect is still generated at C64 resolution, which is both the look and the 16x
saving.

Geometry needed care. The field's offset inside the canvas is rounded **up**
from `field_rect`, and the canvas is then hung at whatever negative origin makes
the two agree exactly; otherwise switching the layer on would shift the picture
by up to `scale - 1` pixels, which is the class of bug the golden renders exist
to catch. A test asserts the field lands on `field_rect` either way, and that
the canvas covers the window with no gap.

The command-accept border flash is drawn into that canvas at one band per raster
line - the window-space arithmetic DISC-261 needed is simply gone, because the
canvas *is* raster lines - and it is stepped by **tube time** rather than frame
count, so the bands keep moving through the refreshes between game frames.

### The static now rides the flash

"The color noise on the side when I press fire. Can it coincide with more noise
in the image?"

`burst()`, fired where `$8660`'s border flash is armed, and decaying over
0.35 s. The one implementation detail worth keeping: a burst is scaled **on the
spot** rather than through `_scaled_noise`'s cache, because its amount changes
every frame as it decays and the cache rebuilds all sixteen noise fields when
the amount moves - two million operations a frame to avoid one multiply over
64,000. A test pins that the bank is not rebuilt mid-burst.

**Measured** per refresh with the border in the chain: 8.14 ms at the default
384x264 window (canvas 384x264, the worst case - the border is proportionally
largest at 1x), 7.06 at 1920x1080, 5.04 at 1280x800 where the field fills the
screen exactly and there is no border at all. Budget is 8.33.

**Action:** shipped, with `_tube_field` retired in favour of `_paint` /
`_tube_layout`.

## DISC-269 - the view follows the crew, and Ripley is already the best cat-catcher

**Found/done:** 2026-08-16, owner's play-test.

### "When the crew member changes floors it doesn't trigger"

Reported twice, and the second time was the useful one: the deck *buttons* had
been fixed (DISC-268) and verified firing, so the remaining case had to be
something else. It was.

**`[C $4CC7-$4CE2]` the map follows the selected crew member's deck** - decoded
long ago and implemented in `play.py`, which assigns `state.deck` **directly**,
inside `render()`, after the trigger check at the top of `draw()` has already
run, and through no menu action whatever. So a crew member walking up a deck
moved the view a floor with nothing anywhere to observe it. No amount of wiring
`MenuController` could have caught this one: the menu is not involved.

The renderer now **watches the state instead of the call sites**: `state.deck`
changing, or the selected crew member's deck changing, fires the gentle
transient regardless of what caused it. That is the third time this layer has
been bitten by enumerating callers (DISC-268 found two, this found a third), and
the pattern is worth naming: *wiring by intent covers the paths you can name;
observing the state covers the paths that exist.* It also covers paths added
later, which the wiring approach cannot.

`_crt_deck` starts as `None` so the first observation seeds it rather than
reading as a jump - arriving on the play screen is not a deck change.

### Catching Jones: she already is the best at it

"Catching Jones with the cat box should be easier if you are Ripley."

She is. `$883C` is a per-character threshold table and it is decoded:

| character | threshold | box | net |
|---|---|---|---|
| Ripley, Ash, Lambert | 13 | 18.8% | 43.8% |
| Dallas, Kane, Brett | 14 | 12.5% | 37.5% |
| Parker | 15 | 6.2% | 31.2% |

Ripley is in the best tier and Parker is deliberately hopeless at it. What is
hard is the **cat box specifically**: the ROM reserves its four-point
improvement for the net (`$87A1-$87AA`), so the box alone is a 1-in-16 to
3-in-16 shot, and the game never tells you the net works at all.

So the memory of catching him easily is most likely the net, or simply repeated
attempts - which the `PATIENT` default already restores by not letting a miss
spook him (DISC-262).

Rather than quietly move ROM-decoded odds, `--jones easy` is a **flagged house
rule**: the box gets the same +4 the ROM gives the net, so Ripley catches at 44%
instead of 19%. Two things about how it is defined matter more than the number:

* the change is **a step the ROM itself makes**, not one chosen to feel right;
* the per-character table underneath is untouched, so the characterisation
  survives - a test asserts Ripley still beats Parker *with* the added rule on.

Default stays `patient`, which is the ROM's odds.

**Action:** shipped. `JonesCatch.EASY`, `--jones easy`, and the renderer's
state-watching deck trigger.

## DISC-270 - a live capture session: four confirmations and one real bug

**Found/done:** 2026-08-17, against the running game (VICE, no warp).

The owner started the live oracle and asked for the remaining `VICE_CHECKS.md`
items. Booting to play took 207 s at real speed; everything below is measured
from the running program.

### The opening, exactly as DISC-229 predicted

One read at game start settles two checks at once:

| array | slot 0-7 (Alien, Dallas, Kane, Ripley, Ash, Lambert, Parker, Brett) |
|---|---|
| location `$7935` | 0, 6, **254**, 6, 27, 27, 27, **6** |
| health `$7D45` | 0, 6, **0**, 4, 5, 4, 6, 5 |
| composure `$7D55` | 0, 4, 4, 3, 4, 3, 4, 3 |
| in-duct `$6501` | **1**, 0, 0, 0, 0, 0, 0, 0 |

* **Crew starting health is per-character**, not a flat 4: 6/5/4/5/4/6/5 in slot
  order, exactly the `$7D4D` template. VICE_CHECKS still described the remake as
  assuming 4; it was corrected long ago and is now live-confirmed.
* **The 3+3 seating is real.** Kane was the victim, his location is the `$FE`
  gone-marker, and **Brett has moved out of AIRLOCK 1 into COMMDCENTR** - the
  vacancy. Three in COMMDCENTR, three in MESS, as DISC-229 read statically.
* `CHAR_GONE_MARKER = $FE` observed in the wild.
* The Alien starts **in a duct** (`$6501[0] = 1`).

### The Alien's clock, measured

Its room changed at 22.8, 30.4, 38.0, 45.6, 53.3, 60.9, 68.4, 76.1, 83.6 s -
**7.6 s between actions**, eight gaps, no drift. `ALIEN_MOVE_TICKS` is 60 and
`MAIN_LOOP_HZ` is 7.886, which predicts 60 / 7.886 = **7.61 s**. Two constants
derived separately and statically, confirmed together by one measurement.

### Corrosion: +1, and rarer than the old note claimed

`$653F,X` only ever moves by **+1** (`INC`, as decoded). What matters is how
seldom: across 90 s of surfaced Alien time it fired **once**, and on the single
sample where `$6563` was set. `$6563` is raised at `$8B13` only when
`$7935 == $64E6` - the Alien's room equals its destination, i.e. **it stayed
put**. Moving in does not corrode; lingering does, and a hunting Alien rarely
lingers.

The remake already models exactly this (`alien.py`, `corrode_pending`). The
comment on `ROOM_DAMAGE_ALIEN_PER_ACTION` claiming "corrosion is real and fast"
came from an older capture with the crew teleported away - with nothing to
chase, the Alien sits still and corrodes every pass. Both observations are
right; the earlier one generalised from an unrepresentative state.

### The bug: the composure hit is gated, and the remake did not gate it

Twelve wounds were captured. **Three cost the victim composure, nine did not** -
and all three landed the victim on exactly 3 health:

    18.4s  slot3  health 4->3   composure 3->2
    89.3s  slot7  health 4->3   composure 3->2
   114.8s  slot1  health 4->3   composure 4->3

The ROM says so plainly, three instructions after the wound::

    41F7  DEC $7D45,X          ; the wound
    4227  CMP #$03
    4229  BNE $4206            ; not exactly 3 -> no composure hit at all
    422B  LDA $7D55,X / BEQ    ; ...nor if composure is already 0
    4230  DEC $7D55,X
    4233  LDA $6571,X / BEQ / DEC $6571,X   ; and its mirror

So a crew member pays **one** composure point, crossing out of O.K., and nothing
for the wounds after it. The remake docked on every wound - roughly four times
too much fear under attack, which feeds panic, the morale band, and the
companion-support term that spreads it to everyone in the room.

Fixed, with `COMPOSURE_HIT_HEALTH_EXACTLY = 3` and a test that searches seeds
for a landed wound (`$4152 CMP #$07` makes most passes miss, so a fixed seed
would quietly stop testing anything). The test fails if the gate is removed -
checked by removing it.

**Worth naming:** this was invisible to static reading because the wound and the
composure hit are adjacent in the source and read as one action. It took
counting twelve real wounds to notice that only a quarter of them cost anything.

**Action:** shipped. VICE_CHECKS items for crew health, the Alien's wound and
room damage are ticked; the wound-per-hit odds, the death threshold, and the
remaining behaviour checks are untouched.

## DISC-271 - the panel does take the joystick, and what the countdown really needs

**Found/done:** 2026-08-17, same live session as DISC-270.

### The panel was never ignoring the stick; the taps were too short

`VICE_CHECKS.md` recorded that "a DOWN joystick tap on the play screen moved
**no** colour cell - the joystick seems to move the character, not the menu",
and asked someone to find the real panel-nav input. There isn't one to find.

The main loop samples input once per pass at **7.886 Hz**, i.e. every ~127 ms,
which is **7.6 frames**. The taps were 4 frames. They fell between polls.

Holding a direction for ~150 ms moves `$64E5` by exactly one row, every time. A
one-second hold moves five - the auto-repeat. With that, the whole panel drives:

    cursor row 8 + fire  ->  $64FB = 7, and the order menu opens on BRETT
    MOVE TO CORRIDOR 1   ->  $64EE[7] = 45, he walks, arrives ~5.7 s later

45 passes at 7.886 Hz is 5.7 s, which is what the stopwatch said.

The live order menu also confirms the **19-row layout** (DISC-232) from the
machine rather than from a capture: BRETT, MOVE TO, the destinations, USE, GET
ITEM, SPECIAL, REMVGRILLE, SCUTTLE NOSTROMO, and `quit` on row 18.

`archive/vice-mcp/drive_panel.py` is the driver, so the next pass starts from
a working panel instead of rediscovering this.

**The lesson is about the instrument, not the game.** A negative result from an
emulator harness is only as good as the harness: "the game ignores this input"
was really "my input was shorter than one poll". Anything that says a mechanic
is absent should say how it would have been detected if present.

### `$64CF` arms the auto-destruct; `$657B` reading 9 means nothing

Chose SCUTTLE NOSTROMO from Brett's panel and watched for 40 s. `$657B` sat at
**9** and `$657C` at **255** - loaded, not counting. The order had already
completed (`$650C` empty, his timer back to 0).

`$5A26` says why::

    5A26  LDA $64CF
    5A29  BNE $5A2C
    5A2B  RTS                  ; not armed -> the countdown never runs
    5A2C  LDA $D020 / EOR #$01 / STA $D020   ; armed -> flash the border
    5A34  DEC $657C            ; ...and tick

So **`$64CF` is the armed flag**, not merely a "win" flag, and the flashing
border during a countdown is this routine toggling `$D020` every pass. `$64CF`
read 0 throughout, exactly matching the idle countdown.

Two things follow:

* **9 is the resting value of `$657B`.** It is loaded at arming and read
  before being decremented, so an un-armed game reads 9 forever. The reading of
  `$657B = 9` taken off the "ALL CREW LOST" ending screen earlier in this
  pass therefore says nothing about that ending, and nothing about the static
  note that 9 marks the win path. Distrusting it was right; now the reason is
  known.
* **Choosing SCUTTLE NOSTROMO from the panel did not reach `set_result_win`
  ($58E3)**, which is what loads `$657B` *and* sets `$64CF`. Either the option
  needs a precondition the panel does not show, or the row leads somewhere else.
  That is the next step for the self-destruct check, and it is now a narrow
  question - watch `$64CF` and set a checkpoint on `$58E3` - rather than a hunt.

**Action:** panel-navigation check ticked; the self-destruct and ending checks
carry the sharpened next step above. `drive_panel.py` archived for reuse.

## DISC-272 - INDICATE LOCATION leaves its list open

**Found/done:** 2026-08-17, live, with the panel driver from DISC-271.

Opening INDICATE LOCATION shows the room list the static read described
(DISC-238): nineteen rows, `QUIT` on row 0, seventeen rooms, `OTHER LIST` on row
18 to swap pages. Confirmed on the machine.

What the static read got wrong is what happens **after** you pick one. Choosing
CRYO VAULT:

* set `$64F7` to the room (15) and raised `$64BE`;
* switched the map to that room's deck - the header changed to MIDDLE DECK;
* **left the list open.** `$64FB` stayed at 16 and the nineteen room rows were
  still on screen.

So the list is a mode you stay in, indicating one room after another, and QUIT
on row 0 is the way out. The remake closed the list on the first pick, carrying
a comment that said "the original returns to the CONTROL panel" - which is now
in `SUPERSEDED_CLAIMS` so it cannot come back.

Small, but it is the difference between a list you use and a list you re-open
every time.

**The selectable row is 10, not 9.** Row 9 is the `INDICATE` header and row 10
is `LOCATION`; the cursor cannot land on 9. Aiming at the first line of a
two-line label walked the cursor onto PARKER and selected him instead, which is
worth knowing before driving the panel by row number.

**Action:** shipped - the remake keeps the list open, with a test that indicates
two rooms in a row without reopening it.

## DISC-273 - the tracker reports proximity and nothing else

**Found/done:** 2026-08-17, live, driving the panel.

Kane was in COMMDCENTR with three items on the floor. GET ITEM listed them by
name - **INCINERATR, INCINERATR, TRACKER** - which is the room's slice of
`tbl_room_objects ($82E3)`, read live as
`[21, 22, 24, 6, 16, 6, 6, 16, 17, 18, 19, 27, 32, 2, 2, 2, ...]`.

Taking the tracker put `USE / TRACKER` on his panel, and using it printed, on
its own line:

    KANE       HAS A READING

That is the whole message. **No room, no direction, no distance** - just that
something registered. The Alien was in room 11 and ducted at the time; Kane was
in room 6, so it reads across the ship and across the surface/duct boundary.

`VICE_CHECKS.md` asked whether the reading names the Alien's room, gives a
direction, or is bare proximity, and noted "(remake shows the exact room)". The
note was stale twice over: the answer is bare proximity, and the remake already
models it that way - `_use_tracker` sets `state.tracker_alarm`, a boolean, and
nothing renders a room. Confirmed rather than corrected.

Two things came free with it:

* **`BRETT SEES JONES`** printed on the next line while Brett was elsewhere, so
  the cat's own message is a separate per-character line, not part of the
  tracker's.
* Picking up the tracker added **`GET JONES`** to Kane's panel at row 15 -
  matching `route_command ($8437)`'s row-15 gate, and confirming the option is
  offered by the panel rather than by USE (P8-3).

**Action:** the tracker-precision check is answered and ticked. The remaining
item-USE questions - net, electric prod, spanner, thermlance - are untouched.

### Addendum: the collapsed-crew selection gate, seen by accident

Trying to select Ripley for the next experiment did nothing - the fire landed,
the cursor was on her row, and `$64FB` stayed 0. The reason was on the health
array: the Alien had reached COMMDCENTR and left Kane, Ripley and Brett all on
**1 health**.

`$7720 guard_alien_present` refuses a selection when `$7D45,Y < 2`, so a
collapsed crew member is listed on the panel and simply cannot be commanded.
That is P2-5's threshold, live: not "dead", but *below 2*. The remake's
`can_be_commanded` already uses it.

Worth noting as a testing hazard too - a panel that stops responding is not
necessarily a broken harness. Read the health array before blaming the input.

## DISC-274 - two endings caught live, and the $32 threshold in the open

**Found/done:** 2026-08-17, live, with a checkpoint on `select_outcome ($60A9)`.

The staging experiments ended the game twice, and the two endings differ - which
is the first time this project has seen more than one:

| | ending text | competence |
|---|---|---|
| first | THE NOSTROMO RETURNS TO EARTH / THE ALIEN AND ITS EGGS ARE UNLEASHED / ALL CREW LOST | **00%** |
| second | THE NOSTROMO IS DESTROYED / THE ALIEN IS DEAD / ALL CREW LOST | **05%** |

The second one came after the Alien's accumulated damage was written past 50 and
the hull went, so it is the "you killed it but nobody lived" outcome.

### The competence preset, and the death threshold, in the same three lines

The checkpoint stopped at `select_outcome` and the code just past the branch is
explicit::

    60D8  LDA $7D45          ; the ALIEN's accumulated damage
    60DB  CMP #$32           ; 50
    60DD  BCC $60F9          ; below -> skip
    60DF  LDA #$05           ; at or above -> competence 5
    60E1  STA $6411

So **the death threshold is exactly `$32` (50)**, as the static read had it, and
the **5 preset** the check asked about is awarded for reaching it. The 05% on
screen is that store, observed from both ends.

Note what this does *not* say: it is a test of accumulated damage at ending
time. Writing 50 or 60 into `$7D45[0]` mid-game changed nothing until something
else evaluated it, so the threshold is a comparison the game makes when it
matters, not a state the Alien enters.

### The win branch turns on the android, not the crew

`select_outcome`'s opening, read live::

    60AE  LDA $64CF / BEQ $60D0     ; no win flag -> the loss printer ($62DC)
    60B3  LDY $64C3                 ; the ANDROID's slot
    60B6  LDA $7D45,Y / CMP #$02
    60BB  BCC $60CA                 ; android below 2 -> one printer ($62EA)
    60BD  LDA $7935,Y / CMP #$22
    60C2  BEQ $60CA                 ; ...or android in room $22 -> the same
    60C4  JSR $62B6                 ; else -> the other ($62B6)

So a win is sub-divided by **what happened to Ash** - whether he is down, and
whether he is in room `$22` - not by the crew at large. `scoring.py` already
describes this structure; this is it confirmed on the machine, with the
addresses stopped at rather than read.

**Action:** the `$32` threshold and the competence-5 preset are ticked on the
ending-selection check. The mapping of the three printers (`$62B6`, `$62DC`,
`$62EA`) to the six ending strings still wants a forced win, which needs a
survivable game rather than a staged one.

### Addendum (DISC-274): forcing a win, and what LAUNCH actually does

Two attempts to reach a *win* ending, both instructive.

**The auto-destruct cannot produce one.** Setting `$64CF = 1` does arm the
countdown (DISC-271), and writing `$657B = 0` / `$657C = 1` detonates on the
next wrap - the ending arrives in about 15 s instead of five minutes, which
makes it a usable tool. But the ending is the same "NOSTROMO IS DESTROYED /
ALIEN IS DEAD / ALL CREW LOST / 05%" either way, because `hull_breach` puts
every crew member on 1 health. Blowing the ship always loses the crew, so that
route can never exercise the win printers.

**LAUNCH NARCISSUS is offered exactly where D-013 said**, and this is the first
live confirmation of it: with all seven crew written into room `$22` (34), alive,
and Jones no longer loose (`$6580 = 0`), the option appeared on the panel.
Choosing it **boards them** - the status line's location changes from SHUTTLEBAY
to `NARCISSUS` and the co-located list follows - but it does **not** end the
game. `$64CF` stays 0, the option stays on the panel, and firing it again does
nothing further.

So boarding and launching are separate, and something beyond "everyone aboard
with the cat" is still required. Candidates, in the order worth testing: whether
the remaining three crew are actually aboard (the panel listed only four of the
seven as present, while `$7935` read 34 for all of them, so the room id and the
displayed location may not be the same thing here), and whether the launch needs
the Alien not to be aboard.

**Next step for the ending check**, now narrow: keep the checkpoint on `$60A9`,
stage the launch, and step from `$5B95` to see which test refuses.

## DISC-275 - the launch conditions, complete, and a win ending on screen

**Found/done:** 2026-08-17, live. The first *win* this project has produced.

Staging every crew member into room `$22` with Jones "caught" was not enough,
and reading `launch_narcissus ($5B95)` and `check_mother_refuses ($5B1F)`
explained why. The full set of conditions, all four of them::

    5B95  LDA $7935 / CMP #$22 / BEQ refuse      ; the ALIEN must not be aboard
    5B9E  LDA $64D1,Y / (non-zero) -> refuse     ; nobody may be asleep
    5BBF  health >= 2 -> must be in $22          ; everyone alive is aboard...
    5BD3  CPY $64C3 / LDA $64CC / BEQ skip       ; ...except the android, unless $64CC
    5BF4  JSR check_mother_refuses               ; and then MOTHER has her say

and MOTHER's own test is the interesting one::

    5B1F  LDA #$8A / STA $5B7F        ; assume refusal
    5B24  CMP $7CB9                   ; is the NET renamed?   -> item $10
    5B33  CMP $7CC3                   ; ...or the CAT BOX?    -> item $11
    5B38  RTS                         ; neither -> she refuses
    5B3B  LDA $82E3,Y / CMP #$22      ; that container aboard?
    5B46  AND #$07 / LDA $7935,Y      ; ...or carried by someone aboard?
    5B50  LDA #$00 / STA $5B7F        ; allow

So **the cat has to be physically in the box or the net, and that container has
to be on the shuttle.** Catching Jones is not enough; carrying him is the
condition, and the *rename* the catch performs (`$87B6`/`$87D7`, D-153) is
exactly what MOTHER looks for. That closes the loop on why the catch renames the
item at all - it is not flavour, it is the flag.

Writing `$7CC3 = $8A` and putting the box in `$22` produced the launch:

    THE NOSTROMO RETURNS TO EARTH
    THE NARCISSUS RETURNS TO EARTH
    THE ALIEN AND ITS EGGS ARE UNLEASHED
    UPON THE PLANET
    SURVIVORS
    KANE  RIPLEY  ASH  LAMBERT  PARKER  BRETT
    COMPETENCE RATING  00%

Three things to note. It is a **third distinct ending**, and the first with a
survivor list. **The android is not on it** - Dallas was `$64C3` this game and
is absent from six survivors, which fits `$5BD3` treating him as not-required
rather than as crew. And the score is **00%** because the Alien was left alive:
escaping does not by itself earn anything, which makes the 5 preset (DISC-274,
`$7D45 >= $32`) specifically a reward for killing it.

**Action:** LAUNCH NARCISSUS is fully closed. Ending selection now has three of
its endings observed and the win branch's structure decoded; what remains is the
android-dead variant (`$62EA` via `$60BB`) and the two Competence presets seen
side by side.

## DISC-276 - the android branch does not choose an ending

**Found/done:** 2026-08-17, live. Three staged wins, one per branch of `$60A9`.

`select_outcome` splits the win path three ways on the android (DISC-274), so
the obvious expectation is three endings. There are not. All three print the
same text:

| android's state | branch taken | ending |
|---|---|---|
| aboard, alive (Dallas) | `$60C2 BEQ` -> `$62EA` | identical |
| collapsed at 1 health (Ash) | `$60BB BCC` -> `$62EA` | identical |
| alive, left behind (Parker) | falls through -> `$62B6` | identical |

Each time: NOSTROMO RETURNS / NARCISSUS RETURNS / THE ALIEN AND ITS EGGS ARE
UNLEASHED UPON THE PLANET, a SURVIVORS list, and 00%.

**And each time the android is missing from the survivors** - Dallas, Ash and
Parker in turn, whichever slot `$64C3` named that game, whether he was aboard,
collapsed, or left behind alive. Six names, never seven.

So `$62B6` / `$62EA` are not ending texts. `DISASSEMBLY.md` had them right as
routines that draw *a character's* name and status; the `$60A9` branch decides
how the android is reported, and in every case that amounts to leaving him off
the list. What actually varies between endings is the **Alien's** fate and the
**ship's**: 00% here with the Alien alive, 05% when it was dead (DISC-274).

Worth recording as a negative result. Reading `$60A9` alone suggests three
outcomes; the machine says one, and a check that had been phrased as "pin which
flag combo maps to each of the six ending strings" was starting from a premise
that does not hold for this branch.

**Action:** the win-branch half of the ending check is closed - it does not map
to distinct strings. The remaining ending question is narrower than it looked:
which combination produces each of the six *texts*, given the Alien's state and
the ship's are what move them.

## DISC-277 - the auto-destruct countdown, timed on the machine

**Found/done:** 2026-08-17, live. Armed by writing `$64CF = 1` (DISC-271) and
watched to completion.

The countdown runs `$657C` from 255 down once per main-loop pass, and on each
wrap decrements `$657B` and redraws a banner. Measured: **~32 s per unit**,
which is 255 / 7.886 Hz = 32.3 s. Nine units plus the tenth wrap that finds
`$657B` already zero gives **2550 passes, about 5 min 23 s** - the figure D-162
derived, now on a stopwatch.

The banner text, sampled at each value:

| `$657B` | banner |
|---|---|
| 9 | WARNING OVERRIDE OPTION EXPIRY **4** MINS |
| 8 | ... **3** MINS |
| 7 | ... **2** MINS |
| 6 | ... **1** MINS |
| 5 | WARNING SHIP WILL **DESTRUCT** IN 5 MINS |
| 4 | ... 4 MINS |

So two different numbers are printed from the same cell: above 5 it shows
`$657B - 5`, the units left to change your mind; at 5 and below it shows
`$657B` itself, the units left alive.

**"MINS" is not minutes.** A unit is about 32 seconds, so the whole thing is
five and a half minutes while claiming nine. The remake reproduces the strings
and the tick count, which is the right call - the label is the game's, and
fixing its arithmetic would be inventing.

One piece of UI worth knowing before trusting the banner: the switch to "SHIP
WILL DESTRUCT" happens **at** `$657B = 5`, while `$585E CMP #$05 / BCC` still
allows an override at exactly 5. The game tells you the option is gone one unit
before it actually is.

**Action:** the self-destruct timer check is closed - variable, tick rate, total
duration and the override window all measured. Whether choosing OVERRIDE
DETONATION from the panel actually clears `$64CF` is the one part not yet
exercised.

## DISC-278 - what ENTER HYPERSLEEP actually does

**Found/done:** 2026-08-17, live.

Staged Kane alone in the CRYO VAULT (room 15) and the special appeared on his
panel, so it is **room-gated to the vault** rather than offered anywhere.
Choosing it does three things:

* sets his **asleep flag**, `$64D1[2] = 1`;
* moves his location from 15 to **`$95`** - bit 7 set over a value that is not
  his old room, so the pod is its own place rather than a flag on the vault;
* leaves his **health untouched** (5 before, 5 after).

And then he **cannot be selected at all**. `$7720`'s guard tests `$64D1,Y`
alongside health, so a sleeper is listed on the CONTROL panel and simply does
not respond - the same shape as the collapsed-crew gate, and the remake already
models both.

**The interaction worth knowing:** `launch_narcissus ($5B9E)` refuses while
*anyone* is asleep (DISC-275). So putting a crew member into hypersleep blocks
the Narcissus escape for the whole crew until they are woken - two specials that
look independent on the panel and are not.

Still open on this check: whether a sleeper is protected from the Alien, and
whether all-crew-asleep plus a dead Alien is itself a win. Both need a game run
on rather than staged.

**Action:** the mechanics of the special are recorded; the win condition it
hints at is not.

## DISC-279 - the companion term is turn-scoped, not continuous

**Found/done:** 2026-08-17, live.

Tried to measure the crowding stressor by staging company: one crew member alone
in a room, then with one, three and six companions, reading both the base
composure `$7D55` and the derived cell `$6571` after each change.

**`$6571` never moved.** Not for six companions, not over 33 seconds, not with
everyone awake and healthy in the same room.

That is not the absence of a crowding effect - `init_char_turn ($4784)` plainly
computes one. It is *when* it computes it: the derived cell is written when a
character **takes a turn**, and an idle crew member standing in a crowd never
takes one. So the value a gate reads can be arbitrarily stale, and company only
starts helping someone once they do something.

The remake computes `effective_composure` **on demand**, so its panel word
changes the instant a companion walks in or out. The ROM's `$6571` sits until
that character next acts. Same formula, different moment - and the difference is
visible on the panel and readable by the panic gate.

**Not changed here.** Matching the ROM means storing the derived value and
refreshing it only on a turn, which reaches the morale word, the panic gate and
`has_functional_companion` at once; that wants its own pass with the
winnability sweep afterwards, not a late edit. Filed as the next action.

**One trap it exposed.** The first run of this measurement showed nothing
because the subject was still asleep from the hypersleep experiment two steps
earlier - and a sleeper never takes a turn, so of course nothing recomputed. The
staging that makes these experiments possible also carries state between them;
reset what you are not deliberately varying.

**Action:** the attack magnitude is measured (DISC-270: -1, and only when the
wound lands on 3). The crowding magnitude still is not, because it cannot be
observed on an idle crew member - it needs a character under orders. Filed.

## DISC-280 - BLOWLOCK is offered from the corridor, confirmed live

**Found/done:** 2026-08-17, live.

Staged a crew member **inside AIRLOCK 1** and the panel offered no BLOWLOCK at
all - only REMVGRILLE. Moved the same character to **CORRIDOR 6** and both
`BLOWLOCK 1` and `BLOWLOCK 2` appeared, on rows 16 and 17.

That is D-037 confirmed on the machine: the special is offered from the corridor
and targets a *fixed* airlock chosen by the menu label, not the acting
character's own room. Standing in the airlock you mean to blow is precisely the
one place you cannot blow it from - which is sensible, and is the sort of rule a
player would never guess.

The panel also listed both airlocks as separate rows, matching the ROM's
four-label menu rather than a single "blow a lock" entry.

**What was not caught:** the jettison itself. The Alien moves on its own 7.6 s
clock (DISC-270), so it had wandered out of the lock before the order resolved,
and writing it back into the room does not stick - the next Alien pass moves it
again. Since `apply_blowlock ($5B04)` vents continuously while a lock is open
(D-155), the method for next time is to blow the lock and then **wait** for the
Alien to wander in, rather than trying to hold it there.

**Action:** specials dispatch now has three of its handlers exercised end to end
- ENTER HYPERSLEEP (DISC-278), LAUNCH NARCISSUS (DISC-275) and BLOWLOCK's offer
condition here. FIGHT FIRE, SEALLOCK and OVERRIDE remain.

## DISC-281 - panic is loss of control, not wandering

**Found/done:** 2026-08-17, live.

Set one crew member's composure to 0, left a control subject at 4, gave neither
an order, and watched for 40 s. **Neither moved.** Only the Alien did. So a
panicked crew member does not wander off on their own - whatever `$52C0`'s
wander branch does, it happens inside a turn, and an idle character never takes
one (the same turn-scoping as DISC-279).

What panic *does* do is take them away from you. A controlled A/B on the same
character, changing nothing but the one cell:

| composure | selectable? |
|---|---|
| 4 | **yes** |
| 0 | **no** |

At 0 the panel lists them and the fire does nothing - the third selection gate,
alongside health below 2 (P2-5) and asleep (DISC-278). Panic reads as a crew
member who has stopped answering, which is a much better piece of design than a
random walk: you can see them on the map and you cannot use them.

**And the companion escape did not save him.** Ripley was in the same room,
healthy and steady, and Kane was still unselectable. That is not a contradiction
of D-151 - it is DISC-279 again. The companion term only enters `$6571` when the
character takes a turn, so for someone sitting at 0 doing nothing it never
arrives, and the gate sees the bare 0.

The remake checks `effective_composure(crew) == 0 and not
has_functional_companion(...)`, computing the companion term on demand - so in
the remake company *does* rescue an idle panicked crew member, and on the
machine it does not. Same root cause as DISC-279, and now with a symptom a
player would notice: a crew member the remake lets you command and the original
does not.

**Action:** the panic check is answered - the observable effect is
unselectability, not movement. It also gives the DISC-279 fix a concrete test
to write when that pass happens.

## DISC-282 - the net does no damage, and two specials flip in place

**Found/done:** 2026-08-17, live.

Staged the tail of the item table into one room and let the panel name them:
index 16 **NET**, 17 **CAT BOX**, 18 and 19 **SPANNER** - matching
`check_mother_refuses`' `$10`/`$11` and the type table `$82CF`, from the game's
own strings rather than from a decode.

Took the net, waited for the Alien to walk in on its own 7.6 s clock (staging
its position does not stick - the next Alien pass overwrites it), and used the
net the moment it arrived.

* **No damage.** `$7D45[0]` stayed 0 across the whole exchange, which matches
  `$4940`'s decode: the net is the one weapon with no wound term.
* **It did not stop the Alien attacking.** Kane was wounded 4 -> 3 about six
  seconds after the net landed.
* **The entangle could not be distinguished.** The Alien stayed in the room, but
  an encounter hold does that too, and its action timer was reloading at ~30-40
  rather than ~60 - which is `ALIEN_ENCOUNTER_HOLD_TICKS`, not obviously a net
  effect. Watching the room is not enough; this needs a watchpoint on the
  Alien's own timer at the instant of use.

So the remake's "no wound" is confirmed and its `ALIEN_NET_ENTANGLE_TICKS` is
neither confirmed nor refuted - and the observation that the Alien kept
attacking is mild evidence against an entangle that stops it.

### SEALLOCK and BLOWLOCK are the same row, flipped

Having blown airlock 1 earlier (DISC-280), the panel now offers **`SEALLOCK 1`**
where it offered BLOWLOCK, with **`BLOWLOCK 2`** still on the row below. So the
two labels are one option per airlock reading a per-airlock flag, exactly as
D-037 describes - and the menu shows the *available* action rather than both.

**Action:** the item-USE check keeps its open question narrowed to the net's
entangle; the damage question is answered. The specials check gains the
seal/blow flip.

## DISC-283 - SCUTTLE and OVERRIDE are one row in the command centre

**Found/done:** 2026-08-17, live. The last open VICE_CHECKS item.

Both halves of the auto-destruct, driven end to end:

    in COMMDCENTR, disarmed:  the row reads SCUTTLE NOSTROMO
      -> fire it  ->  $64CF 0 -> 1, $657B reloads to 9, $657C starts counting
      -> the row now reads OVERRIDE DETONATION

    armed:                    the row reads OVERRIDE DETONATION
      -> fire it  ->  $64CF 1 -> 0, and $657B/$657C FREEZE where they were
      -> the row reads SCUTTLE NOSTROMO again

So they are **one option that shows whichever action is available**, the same
pattern as SEALLOCK/BLOWLOCK per airlock (DISC-282). And the override does not
reset the countdown - it stops it, leaving `$657B` and `$657C` mid-flight, which
is `$5A26`'s gate doing exactly what it says: no `$64CF`, no tick.

**Both are gated to COMMDCENTR.** This is what defeated the earlier attempt
(DISC-271): SCUTTLE was fired from CORRIDOR 1, the order completed, and nothing
armed. The row is *listed* elsewhere, which is the trap - the panel shows it and
the handler declines, with no message to say why. Fire it in the command centre
and it works first time.

That also answers "what reaches `set_result_win ($58E3)`": SCUTTLE NOSTROMO
does, from the right room.

**Action:** the self-destruct check is closed. With it, every item in
`VICE_CHECKS.md` is now either done or has its remaining question stated
precisely - nothing is left as an open unknown.

## DISC-284 - three traps that make a live measurement lie

**Found/done:** 2026-08-17, trying to measure the weapon damage chunk.

The measurement itself did not land, and the reasons are worth more than the
number would have been. Each of these produced a confident-looking zero.

**1. The open menu is cached.** Writing a crew member's room while their order
menu is up moves `$7935` but not the panel: the status line still named the old
room and MOVE TO still listed the old exits. A USE fired then resolves against
what the menu believes. **Re-select the character after moving them** - quit to
the CONTROL list and pick them again - so the menu rebuilds.

**2. `$7935[0] = 34` is a sentinel, not a room.** The Alien sat at 34 (`$22`)
across eight attempts, which is the off-map value DISC-244 identified for the
Narcissus slot. An Alien reading 34 is not somewhere you can reach it, so every
attack fired into empty air and reported no effect. **Check the Alien's room is
a real one before concluding a weapon does nothing.**

**3. A blown airlock kills whoever you put in it.** Staging a crew member into
room 0 ended the game immediately - the lock had been blown two experiments
earlier and `apply_blowlock ($5B04)` vents continuously (D-155), confirmed here
by accident. Staging positions has to account for what earlier experiments did
to the ship.

Underneath all three is one rule: **the emulator answers the question you
actually asked**, and staging makes it easy to ask a different one than you
think. Every negative result from this harness needs a positive control - if the
laser had been fired once at a *real* co-located Alien and moved the number,
the eight zeroes afterwards would have meant something.

**Action:** the weapon-damage chunk stays open with a method attached: put a
checkpoint on `resolve_attack ($4940)` and read the item id at `$4BEF` when it
fires, rather than inferring from memory before and after. That turns "did
anything happen" into "here is the code path, with its argument".

## DISC-285 - ATTACK is the path, and it costs the room 6

**Found/done:** 2026-08-17, live, with a checkpoint on `resolve_attack ($4940)`.

The positive control DISC-284 said was missing. With the Alien genuinely present
and an encounter running, the panel offers **ATTACK** at row 14 - and that, not
USE, is what reaches the attack code:

* fired ATTACK, and the actor's timer counted **42 passes (~5.3 s)** down to 0;
* at zero, `$4940` was reached and the emulator stopped there. **This is why the
  earlier attempts read as "nothing happened"** - they waited a second or two
  and gave up, when the attack had not resolved yet;
* the room's damage went **0 -> 6**, which is the weapon-hit chunk the check
  asked for, matching the `+6` the static read predicted;
* the Alien's own damage moved 0 -> 2 across the exchange.

`$4940`'s opening also settles what it dispatches on::

    4940  TYA / CMP #$FF / BEQ rts     ; no object
    4945  CMP #$11 / BEQ rts           ; the CAT BOX aborts
    4949  STA $4BEF                    ; ...otherwise stash the item id

So the item id arrives in **Y** and is stored to `$4BEF` by this routine, rather
than being placed there beforehand - worth knowing before reading `$4BEF` at the
checkpoint, which returns the *previous* attack's item until `$4949` runs.

**What is still not pinned:** the per-hit damage to the Alien. One exchange
moved it by 2, which does not separate "one hit of 2" from "two hits of 1", and
repeat trials kept failing to land because re-staging the scene clears the
encounter that puts ATTACK on the panel in the first place. The method that
works is the one that worked here: let a real encounter start, then fire ATTACK
and wait out the action delay.

**Action:** the weapon-hit chunk (+6 to the room) is answered. Per-hit Alien
damage and the hit fraction want a pass that lets encounters happen rather
than staging them.

## DISC-286 - the instruction viewer was cutting the bottom off half the pages

**Found:** 2026-08-27, while adding the manual screen (DEC-028), which reuses
the same page list.

**What was wrong.** `_draw_instruction_pages` drew each page from **row 1** and
stopped at `_ROWS - 3`, giving 22 usable rows. The loader's BASIC produces pages
of up to **24** lines:

| page | lines | page | lines |
|---|---|---|---|
| 1-2 | 22 | 6-7 | **24** |
| 3 | 21 | 8 | **23** |
| 4 | 22 | 9-10 | 21, 20 |
| 5 | **23** | | |

So pages 5-8 lost their last one or two lines, mid-sentence and with nothing
saying so - page 6 ended `"...ALSO COME THROUGH THIS PORT. IT'S YOUR"` and
simply stopped, dropping `"REAL TIME INFORMATION WINDOW."`.

**What is true now.** Both viewers draw from **row 0** through `_ROWS - 1`,
which is exactly 24 rows above a one-row footer. Nothing about the text changed;
it was always parsed correctly and only the drawing was short.

**The trap.** The indented start was reasonable-looking - every other front-end
screen leaves row 0 clear - and the loss was invisible because the text is
hand-wrapped prose that reads as if it ended. Nothing compared the number of
lines a page *has* against the number the renderer can *show*.

**Action:** fixed in `render/frontend.py` (both `_draw_instruction_pages` and
the new `_draw_manual`).
`test_options_screen.py::test_no_instruction_page_is_taller_than_the_screen_can_draw`
asserts the tallest page fits, so the two cannot drift apart again.

## DISC-287 - an idle character never takes a turn

**Found/done:** 2026-08-18. The root cause behind DISC-279 and DISC-281, fixed.

Both of those findings ended with "filed rather than fixed", and both had the
same cause. `char_pump` is unambiguous::

    7226  LDA $64EE,Y
    7229  BNE $722E                ; counting -> decrement it
    722B  JMP check_deferred_move  ; ALREADY ZERO -> no turn at all
    722E  SEC / SBC #$01 / STA $64EE,Y
    7234  BEQ $7239                ; reached zero -> take a turn
    7236  JMP check_deferred_move  ; still counting -> not yet

A turn happens **only on the pass a countdown reaches zero**. A character
sitting at zero - idle, no order - is skipped entirely, for as long as they are
left alone.

The remake did the opposite: `_pump_characters` added an idle character to the
due set on *every* pass, about eight turns a second. That one `else` branch is
why an idle crew member recomputed their companion support continuously
(DISC-279), and why a panicked one bolted where the running game leaves them
standing (DISC-281). Neither needed a separate fix; both were this.

**Measured against the machine first, then read.** Six companions in one room
moved `$6571` not at all in 33 s, and a composure-0 character did not move in
40 s. Those observations are what sent me back to `char_pump`, and the listing
then said plainly what the emulator had already shown.

### What it cost to correct

Three tests failed, all asserting that an *idle* panicked crew member bolts.
The mechanic they cover is real - `$5170/$5252 -> $5203` is the panic branch -
but their setup gave the character no countdown, so they were testing a turn the
ROM never grants. Each now arms `step_timer = 1` so the pump takes it to zero
and a turn genuinely comes round; the assertions are unchanged and still pass.

That is the useful shape of this correction: **the behaviour was right and the
trigger was wrong.** Nothing about panic-wander was invented; it was simply
reachable from a state the original never reaches.

The winnability sweep is green, so the three win routes survive a world where
crew do nothing unless ordered - which is, on reflection, the game's whole
design: the PCS is a queue of orders, not a simulation that runs without you.

**Action:** shipped, with a test that fails if the `else` returns.

## DISC-288 - The Alien's room damage: magnitude decoded, cadence measured
**Date:** 2026-08-29 · **Method:** static trace + `[C-live]` capture against the
running disk (VICE oracle, WarpMode off)

`ROOM_DAMAGE_ALIEN_PER_ACTION` has carried a `[?]` since D-036, and todo.md has
listed it as "the clearest single candidate" for whatever offsets the weapon
breach gates. The `[?]` turns out to have been asking two questions at once, and
they have different answers.

### The magnitude was never uncalibrated

Reading `$8EC0` off the running machine:

```
8EC0  F0 01        BEQ $8EC3
8EC2  60           RTS
8EC3  AD 01 65     LDA $6501       ; the Alien's own in-duct flag
8EC6  D0 FA        BNE $8EC2       ;   ...must be 0 (on the surface)
8EC8  AD 63 65     LDA $6563
8ECB  F0 F5        BEQ $8EC2       ;   ...and $6563 must be set
8ECD  AE 35 79     LDX $7935       ; X = the Alien's room
8ED0  FE 3F 65     INC $653F,X     ; +1, once
8ED3  20 81 55     JSR $5581
```

`INC` is a single increment. **The magnitude is 1 and always was** - the
remake's value is right, and it is decoded rather than guessed. The `[?]` was
only ever about *how often this routine gets past its two gates*.

### The gates, and what they are

Both are booleans; both were observed taking only 0 and 1 across 2,378 samples.

* **`$6501`** is the in-duct flag array indexed by character, and index 0 is the
  Alien (the same array `sim/__init__.py` already reads at `$6501,X` for crew,
  and that `play.py` uses to colour the marker portrait black-in-a-room /
  white-in-a-duct). So **an Alien inside the ducting damages nothing.** It was
  on the surface in 77% of samples.
* **`$6563`** gates the other 58%. Not yet identified; it reads as an
  "act this pass" flag from the char-turn engine. **This is what remains `[?]`.**

### The rate, measured

Two windows, no player input, WarpMode off:

| window | Alien | damage | rate |
|---|---|---|---|
| 102 s | moving between rooms (5 -> 14 -> 25 -> 18) | **1** | ~1 per 100 s |
| 100 s | settled in room 15 | **6** | ~1 per 17 s |

So the damage is not a flat per-action tick: a **roaming** Alien barely marks
the ship, and a **settled** one eats a room at about a point every 17 seconds.
Both gates were open 42% of the time in the second window, yet only 6 points
landed - so `$6563` is not simply "open for a while", and the true cadence sits
behind whatever sets it.

### What this means for the remake

`HULL_BREACH_THRESHOLD` is 20, so a settled Alien holes a room in ~5.7 minutes
of real time and a roaming one takes over half an hour. The remake applies its
point per Alien *action* (`ALIEN_MOVE_TICKS` = 60 = ~7.6 s), which is roughly
**twice** the measured settled rate and perhaps **thirty times** the roaming
rate.

That is the right shape to explain DISC-258: wiring in the weapon breach gates
made the game unwinnable across 16 seeded games because rooms holed too fast,
and this says the remake's rooms *do* take damage too fast - not because the
magnitude is wrong, but because the cadence has no gates on it. **Do not change
the constant.** The fix, when it comes, is to gate the application the way
`$8EC3`/`$8EC8` do, and to re-run the winnability sweep afterwards.

### `$6563` identified - the `[?]` is closed

Found the same session. A `STA $6563` search returns nothing because the write
is `STY`, and the whole of it sits in the Alien's own turn handler at `$8AE4`:

```
8AE4  A0 00        LDY #$00
8AE6  8C 63 65     STY $6563        ; cleared every pass
...                                 ; (blanks row 24, stores $64A1)
8AFE  AD 01 65     LDA $6501
8B01  D0 13        BNE $8B16        ; in a duct -> leave it clear
8B03  AD 35 79     LDA $7935        ; the Alien's room
8B06  CD E6 64     CMP $64E6        ; ...vs `var_alien_target`
8B09  F0 08        BEQ $8B13
8B0B  A9 01 8D 64 65  LDA #$01 / STA $6564   ; still travelling
8B13  EE 63 65     INC $6563        ; ARRIVED
```

`$64E6` is `var_alien_target`, already named in MEMORY_MAP.md and already used
by `core/alien.py`. So `$6563` is a **per-pass boolean meaning "the Alien is on
the surface and has arrived at the room it was heading for"**, which is exactly
the 0/1 the capture saw.

**The rule, complete:** the Alien damages a room by **1 per action**, and only
while it is **on the surface** and **at its target room**. It does not damage
the rooms it passes through, and it damages nothing from inside the ducting.

That is the whole of the measurement explained: a roaming Alien is rarely at
its target on any given action (1 point per ~100 s), a settled one is at it
every time (1 per ~17 s, which also bounds the Alien's action cadence when
settled at ~17 s - slower than `ALIEN_MOVE_TICKS`'s 7.6 s and worth its own
look).

### CORRECTION, 2026-08-30 - the remake already does all of this

The paragraph that stood here said *"the remake applies the point per Alien
action with neither gate, which is why its rooms take damage several times too
fast."* **That was wrong, and wrong twice.** It was written from the constant's
call site (`alien.py:765`) without reading the caller thirty lines above it.

**The gates are implemented, and have been.** `advance_alien` computes:

```python
corrode = (
    alien.corrode_pending          # `$6563` - arrived, set by the previous pass
    and not alien.attack_sequence  # `$8EBD LDA $6562 / BNE rts`
    and not alien.hunting          # `$89AF LDX $64B4 / BNE`
)
...
if surfaced and _resolve_surface_action(..., corrode=corrode):
```

That is the ROM's three gates in the ROM's own order, plus the `surfaced` test
for `$6501`. The comment beside it already described the mechanism correctly.

**And the rate is not several times too fast.** Measured on the remake over
8,000 ticks (~1,014 s) across three seeds:

| seed | damage | rate | Alien moves |
|---|---|---|---|
| 0 | 27 | 1 per 37.6 s | 64 |
| 1 | 20 | 1 per 50.7 s | 60 |
| 2 | 18 | 1 per 56.4 s | 63 |

The remake's Alien takes an action about every **16 s**, which is the same
cadence the disk showed when settled (6 damage in 100 s = 6 actions), and it
corrodes on roughly a **third** of them because the gates hold on the rest.

The original comparison was apples to oranges: a 100-second disk capture with
the Alien parked in one room was set against a remake run that was mostly
roaming. Those measure different things, and the difference between them was
read as a fault.

### What is actually still open

Not the magnitude, not the gates, and not obviously the rate. The one number
neither capture pins is the **corrode fraction** - what share of its actions the
disk's Alien spends lingering rather than moving, since that is what the gates
turn into a damage rate. The remake's third is a consequence of its own movement
model, not something calibrated against anything.

Settling it needs a longer capture than the two here: several minutes sampling
`$7935` and `$653F` together, through both roaming and settled stretches, so the
*ratio* can be compared rather than either rate alone. Worth doing before
anything is changed - and nothing should be changed on the strength of the
retracted paragraph above.

## DISC-289 - DISC-258 re-run: the breach gates are right, and the arithmetic still does not close
**Date:** 2026-08-30 · **Method:** 16-seed winnability sweep, two policies, plus
a fresh read of `$4A87`/`$4AF0` in the annotated disassembly

DISC-258 recorded that wiring in the ROM's pre-add weapon breach gates made the
game unwinnable and was reverted. That was 2026-08. This re-runs it against the
current codebase with `tools/winnability_sweep.py`, and the finding holds -
harder than before, and for a reason worth writing down.

### The sweep

| | won | lost | still running | best Alien damage |
|---|---|---|---|---|
| gates **off** (ships today) | **13** | 2 | 1 | 50/50 |
| gates **on**, stand-and-fight policy | **0** | 15 | 1 | 0/50 |
| gates **on**, policy that refuses to swing in a room already at the gate | **0** | 15 | 1 | 3/50 |

The third row is the interesting one. The obvious explanation for row two is
"the policy is stupid - it stands in one room until the ship holes", so the
policy was rewritten to decline the swing when the room is already at the gate
and wait for the Alien to move on. It makes no difference: three hits, then
nothing, in fifteen of sixteen games.

### The constants are not the problem

Re-read off the annotated disassembly rather than trusting the note:

```
4AE7  B9 35 79  LDA $7935,Y     ; the room the fight is in
4AEA  8D 7F 45  STA $457F
4AED  20 A8 4B  JSR remove_room_object
4AF0  AC 7F 45  LDY $457F
4AF3  B9 3F 65  LDA $653F,Y     ; ...its damage, BEFORE adding
4AF6  C9 0E     CMP #$0E        ; >= 14?
4AF8  90 03     BCC $4AFD
4AFA  4C 17 5D  JMP hull_breach ; yes -> the ship is holed
4AFD  18 69 06  CLC / ADC #$06  ; no  -> +6
```

and the harpoon path at `$4A87` is the same shape with `CMP #$05` and
`ADC #$0F`. So `ROOM_BREACH_GATE_OTHER = 14`, `ROOM_BREACH_GATE_HARPOON = 5`,
`ROOM_DAMAGE_PER_ATTACK = 6` and `ROOM_DAMAGE_PER_ATTACK_HARPOON = 15` are all
correct, and `$457F` really is the fight's own room. **Nothing here is
misdecoded.**

### Where the arithmetic actually breaks

Two decoded facts that do not fit together in the remake's model:

* A room allows **two or three swings** before the pre-add gate fires (6 damage
  a swing, gate at 14).
* Killing the Alien needs **50** (`$4980 CMP #$32`), and a landed hit is
  `INC $7D45[0]` - **one** point.

Fifty hits at three hits a room is seventeen rooms of running fight, never
losing the crew who are carrying the weapons. The remake's crew do not survive
that: the careful policy landed **three** hits in an entire game.

So the tension is not between the gate and the room. It is between the gate and
`ALIEN_DAMAGE_TO_KILL`, and one of these must be true:

1. the original expects a fight that moves across the ship, and the remake's
   crew are too fragile or too passive to sustain one - a **behaviour** gap, not
   a constant;
2. a hit does more than one point in some circumstance not yet decoded;
3. rooms recover damage somewhere, so a room can be fought in twice.

### What this means for shipping

**Do not wire the gates in.** The divergence stays, and
`test_the_weapon_breach_gates_are_decoded_but_not_yet_applied` stays with it.
But the next move is no longer "try the gates again" - it is to find out which
of the three above is true, and (1) is the one to look at first, because it is
the only one that predicts something checkable: whether a running fight across
rooms is possible in the remake at all.

## DISC-290 - P-8: the corrode fraction, and it does not look wrong
**Date:** 2026-08-30 · **Method:** three live captures against the running disk,
plus the same measurement taken on the remake

P-8 asked the one question DISC-288's correction left open: the Alien's room
damage is gated on *lingering*, so what share of its actions does the disk's
Alien actually spend lingering? That share is the damage rate, and the remake's
was never calibrated against anything.

### How not to measure it

Worth recording, because two of three attempts were wasted on it. `$6563` is
raised and cleared **inside a single Alien action**, so polling for it is a
lottery: one capture caught it in 42% of samples at 24 samples/s, the next
caught it in **0%** at 2 samples/s, in a run where damage was demonstrably
accruing. Sampling a flag that is briefly up measures your sample rate.

**Count the damage instead.** It counts the same events without having to catch
them, and it is what the final capture does.

### The measurement

| | disk | remake |
|---|---|---|
| Alien changes room every | **16.3 s** | ~16 s |
| damage gained | 2 in 146 s | 18-27 in 1,014 s |
| corrode fraction (damage per action) | **~0.22** | **~0.33** |

Dwell per room on the disk: 5 s minimum, 9 s median, 36 s maximum - so it
mostly moves on quickly and occasionally settles, which is exactly the shape
the gate implies.

### CORRECTED the same day - the table above was read off a capture still running

The figures first published here (0.22 disk against 0.33 remake, "no
discrepancy worth acting on") came from reading the CSV **while the capture was
still writing it**: 146 seconds of a 360-second run, two damage events. The run
then finished cleanly - 360 s, 1,868 samples, **zero dropped** - and says
something different.

| | disk (360 s, clean) | remake (6 seeds, 6,084 s) |
|---|---|---|
| Alien changes room every | **12.0 s** | 17.0 s |
| damage per room change | **0.13** | **0.41** |
| damage per second | 0.011 | 0.024 |

Dwell per room on the disk: 1 s minimum, 9 s median, 36 s maximum.

**The remake corrodes about three times too often per Alien action**, and its
Alien also moves less often (17.0 s against 12.0 s), so the two compound into
roughly twice the room damage per second of play.

The disk sample is still only four damage events - Poisson error about +/-2, so
0.13 lies somewhere near 0.07-0.20. But the remake's figure rests on 357 room
changes across six seeds, and even the disk's upper bound is half of it. This
is a real difference, not sampling noise.

### The sequence, because it went wrong twice

Worth setting out, since the conclusion reversed three times and each reversal
had the same cause - measuring two things that were not the same thing:

1. DISC-288 concluded "no gates, several times too fast". The gates half was
   simply wrong: they were implemented, and the claim came from reading the
   constant's call site without the caller.
2. The correction concluded "gates present, rate fine". The rate half was wrong:
   it set a 100-second disk capture with the Alien parked against a remake run
   that was mostly roaming.
3. This entry concluded "no discrepancy". Wrong because the capture had not
   finished; two events is not a measurement.
4. This correction: **~3x too much corrosion per action**, disk and remake
   measured with the same estimator over full runs.

The estimator that finally worked is the dull one - damage gained divided by
room changes, over an uninterrupted capture, with the identical calculation run
against the remake. Every earlier attempt substituted something cheaper.

### What follows

This reopens the room-damage path as a suspect in DISC-258, which the previous
version of this entry had ruled out. Rooms holing too fast is exactly what makes
the pre-add breach gates unsurvivable, and the remake's rooms take damage about
twice as fast per second of play as the disk's.

The lead is `corrode_pending`: the remake's Alien is at its target on ~41% of
actions and the disk's on ~13%, so the remake either arrives more often or
counts arrival more loosely. **Do not change it without bracketing the change
with `tools/winnability_sweep.py`** - and re-run the gates-on sweep afterwards,
because this is the first thing found that could plausibly move it off 0/16.

### The practical note that still stands

**Two of the four captures died because a second connection was polling the
emulator while they ran**, reported as `Timeout: emulator may be paused or
unresponsive`. One connection at a time, and read the file after the run, not
during it.

## DISC-291 - Two presentation bugs from a playtest, and the log that split them
**Date:** 2026-08-30 · **Method:** owner's session log + the disassembly

Both looked like game bugs and neither was: the simulation had it right in each
case and the screen was misreporting it. Worth recording because that is the
distinction the session log exists to make, and this is the first time it made
it.

### "Ripley caught Jones with the net, and Ash's cat box said Jones:Box"

The log settles the first half in one line - `t1915: caught=True
container=net_1`, immediately after Ripley's `GET_JONES`. So
`state.jones_container_id` was correct and the *label* was wrong.

`menu._item_label` tested `type_id == "cat_box" and state.jones_caught`, which
is wrong twice over. Any cat box anywhere took the name once the flag went up,
and the net - which the ROM renames too - never did.

`$87B6` copies **"Jones:Net"** and `$87D7` **"Jones:Box"**; the rename lands on
whichever item made the catch, which `specials.py` already recorded. The test is
identity now, not type, and the label follows that item's own type. Without an
item id the function returns the plain name rather than guessing, because a
wrong "Jones:" on the wrong row is worse than no marker - the panel is the only
place the original tells you where the cat is.

**The old test encoded the bug.** It set `jones_caught` and nothing else, which
is a state the game never produces; it now says what caught him.

### "Hovering highlights a room, but not the one under the pointer"

The hover boxes were laid out on the internal grid -
`ox + room.x * cell_w`, 36x36 cells - while the map art and every marker on it
are placed from the ROM's own decoded table (`$758D`/`$75B1`, `_room_marker_px`).
Two different layouts over the same screen, so a room's box sat nowhere near the
room: rooms lit up, just never the one being pointed at. Reproduced exactly -
hovering `corridor_1`'s own marker picked `None`.

The boxes are now the marker's own rectangle, 24x21 - a C64 hardware sprite,
which is what is actually drawn - so the thing you can hover is the thing you
can see. The grid remains as the fallback for synthetic test maps, which is what
`_room_marker_px` returns `None` for.

**The lesson for the rest of the pointer work:** hit-testing must invert what
was *drawn*, and this recorded what was *modelled*. The panel already gets this
right through `_panel_placement`; the map did not.

## DISC-292 - what one turn is, and why it needs no re-denomination

**Found/done:** 2026-08-18. Closes T1 and T3; T4 and T5 implemented with it.

The register left three candidates for "one turn" and recommended the second.
Adopted, with the reasoning written down because T3 turns out to fall out of it
rather than needing its own answer.

**One turn = advance until an order reaches a terminal outcome.**

* *One turn = one tick* is faithful and nearly empty. A single room move costs
  **64-74 ticks** (measured: Ripley 64, Brett 69, Dallas 71, Parker 74), so the
  player would spend sixty-odd turns pressing nothing to walk through a door.
* *One turn = everyone acts once* flattens the per-character delays. Those
  delays are the characterisation - the same measurement shows Ripley ten ticks
  quicker than Parker on the identical order - so a fixed turn deletes a decoded
  mechanic.
* *Advance until something resolves* keeps both and asks for input exactly when
  there is something to decide.

### T3 answers itself

The worry was that once turns are player-paced, "40 ticks" stops meaning
6.4 seconds and the auto-destruct becomes trivial or unsurvivable. It does not,
because **this loop advances real ticks**. A turn spans however many the next
resolution took; it does not substitute for them. Every tick-denominated
constant keeps its exact meaning, the destruct is still 2550 passes, and the
mode cannot make it easier or harder. `test_turns_do_not_change_how_many_ticks_
an_order_takes` pins that: the same order costs the same ticks stepped by hand
or taken as a turn.

That is not a lucky escape - it is the property that made this the recommended
option, now stated where the next reader will find it.

### Two mistakes the tests caught, both the same shape

**"Something resolved" is not "`last_outcomes` is non-empty".** A MOVE reports
`IN_TRANSIT` on the tick it is accepted and every tick it is still walking, so
that reading ended the turn immediately and collapsed the mode back into
one-turn-per-tick. The tell was two characters "resolving" in **one tick each**
- identical, when the whole point is that they differ. The rule is now the
complement of `SURVIVING_OUTCOMES`, which is the model's own name for the
outcomes that keep an order queued, so it stays correct if one is added.

**The turn ceiling truncated real actions.** The first `MAX_TICKS_PER_TURN` was
60, chosen as "one Alien action" - and every room move takes more than that, so
every turn ended with the order still in flight. It is now **256**, above
REMVGRILLE's 180 for Ripley or Lambert plus the wounded penalty of 48.

Both were the same error: a bound picked from a plausible-sounding quantity
rather than from the numbers the model actually produces. Measuring four
characters' move times took one script and would have prevented both.

**Action:** `runner.advance_until_resolution` (T5, pure) and
`runner.run_turn_based` (T4) shipped with seven tests. T2 (an AP budget) is
deliberately **not** done - the ROM has no per-turn allowance, only the running
countdown, so a budget is an invention and wants its own decision.

## DISC-293 - two decisions rather than two more open items

**Found/done:** 2026-08-18. Closes T2 and the CRT default question.

### T2: the AP budget is not needed, and should not be built

The item asked for a per-turn action-point allowance priced from the delay
tables, and flagged the *budget* as an invention because the ROM has no such
allowance - only the running countdown.

Under the turn model adopted in DISC-292 it is not merely an invention, it is
**redundant**. A turn already ends when an action resolves, and what an action
costs is already the character's own decoded delay: 64 ticks for Ripley's room
move, 74 for Parker's, 180 for a grille. Those numbers *are* the pricing. An AP
budget would sit on top of them and either contradict them or restate them.

So T2 is closed as **not applicable to the chosen model**, not deferred. If a
future mode wants simultaneous multi-character turns it would need one, and that
is the point at which the invention should be argued - not before.

### The CRT default stays `off`

The look is tuned and the owner clearly likes it, having extended the layer to
cover the front-end screens as well. The default still ships **off**, on the
project's own stated grounds: the CRT is documented in its own module header as
"a look, not a fact", and this is a replica whose whole value is that what you
see is what the machine did. A player comparing the remake against a real C64 or
a screenshot should get the pixel-exact picture unless they ask otherwise.

`--crt subtle` and `--crt full` are one flag away, the settings file carries it
for Game Mode, and the tests already assert that `off` is byte-identical to no
layer at all - so the faithful path is the one that cannot silently rot.

**This is the reversible half of a decision made without the owner in the
room.** If the intent was for the tube to be the default experience, it is one
word in `__main__.py` and one line here; the reasoning above is what should be
argued with, not the mechanism.

## DISC-294 - the turn-based mode gets a door: `--headless-turns`

**Found/done:** 2026-08-18.

DISC-292/293 built `run_turn_based` and `advance_until_resolution` and closed
T1-T5, T7, T8 - and then nothing in the program could call either. A loop with
no entry point is not delivered; it is a library function with tests. Added
`--headless-turns N`, the turn-based twin of `--headless`, sharing every code
path except which loop paces it - same `make_sim`, same report, same final
`tick=/phase=` line with a `turns=` prefix so the two are directly comparable.

### The empty-turn ceiling was answering the wrong question

First run: `--headless-turns 5` on a fresh game reported **1280 ticks** for five
turns doing nothing. `MAX_TICKS_PER_TURN` (256, sized for the *slowest ordinary
action* so a real move never gets truncated) was also being used to bound a turn
with **no action pending at all** - and 256 ticks of silence between prompts is
thirty-two seconds, four Alien actions, long enough to be killed with no chance
to respond.

Pending and idle are different questions and one ceiling cannot answer both
correctly: bound idle by the pending value and the player waits far too long
between prompts; bound pending by the idle value and every real action gets cut
off mid-flight. Split into `MAX_TICKS_PER_TURN` (256, unchanged) and
`MAX_IDLE_TICKS_PER_TURN` (60 - one Alien action, so doing nothing still lets
the world move once before asking again). Which applies is decided once at the
top of the turn from whether any order is queued or any character is mid-action,
not re-decided tick by tick, so a turn's length cannot depend on the moment the
world happened to act.

`--headless-turns 5` now reports 300 ticks - five idle turns at 60 - which is
the number the fix predicts exactly.

**Action:** shipped, with two tests: an idle turn is bounded by the short
ceiling and a pending one is not, and an idle turn still advances at least one
Alien action rather than zero.

## DISC-295 - P-8: a six-minute paired capture, and why the fraction still is not clean

**Found/done:** 2026-08-18, live. 361 s of `$7935[0]`/`$6501[0]`/`$653F,X`
sampled together at 0.5 s resolution, no staging, no interference - exactly the
longer paired capture P-8 asked for.

**The headline number, stated with its real uncertainty:** across 33 estimated
surfaced action-passes (segment length / `ALIEN_MOVE_TICKS` at `MAIN_LOOP_HZ`),
room damage rose by a net **7**, for a naive corrode fraction of **~0.21** - a
fifth of passes, not the remake's own third.

**Why "naive" is the right word, and this is not a clean answer.** `$653F` is
shared: anything else that damages or repairs a room - a weapon miss, FIGHT
FIRE, a grille burst - moves the same cells the Alien's corrosion does, and nine
minutes of live play cannot rule that out without also watching the crew. Two
of the twenty surfaced segments read **negative** gain (room 30 went 3 -> 1
across one segment), which corrosion alone cannot produce - `INC` does not run
backwards. So some of what this measured is not the Alien at all, and the true
corrode fraction is somewhere the naive number cannot pin down further without
also excluding every other write to the array.

**The one clean data point in the run.** Room 27 held the Alien for **83.3 s -
eleven action-passes by the clock** - and its damage read **0 at the start and
0 at the end**. Eleven consecutive passes with no source of confound available
(nothing else was anywhere near that room) and not one of them corroded. That is
not what a ~third or even a ~fifth corrode fraction predicts for eleven
independent passes - at 1/3 the chance of all eleven missing is under 1%, at
1/5 still under 10%. Read plainly, it is much better evidence for DISC-270's
actual decoded mechanism - corrosion requires the *destination* to equal the
*current* room, which a hunting Alien satisfies rarely and which this run's
polling (once every 0.5 s, on the *displayed* room only) cannot distinguish
from an Alien that kept re-targeting the same room's neighbours and bouncing
back - than for any fixed per-pass probability at all.

**What this does and does not settle.** It does not hand over a number to
recalibrate `ROOM_DAMAGE_ALIEN_PER_ACTION` or the fraction the remake's movement
model produces - the confound is real and the sample is one long stay plus a
scatter of short ones. It does further undercut the premise the whole P-8/P-9
line was built on: that corrosion is well modelled as *some fixed fraction of
actions*, when DISC-270 already found it gated on a specific destination-equals-
room condition and this run's one unconfounded data point (eleven passes, zero
corrosion) is consistent with that gate being rare rather than with a fraction
in the 20-33% range being wrong-but-close.

**Action:** not closed. The honest next step is not a longer capture at the
same resolution - more of the same confound is not more signal - but a
watchpoint on `$6563` itself (the flag DISC-270 decoded) alongside `$653F`, so
corrosion is read from the condition the ROM actually tests rather than
reconstructed from a shared damage total after the fact. Recorded so the next
session does not repeat a six-minute run to arrive at the same ambiguity.

## DISC-296 - P-8 closed: the corrode fraction, read from the flag itself

**Found/done:** 2026-08-18, live, same session as DISC-295. Supersedes its
naive damage-delta estimate with a clean one.

DISC-295's number was confounded because `$653F` is a shared array - anything
that damages or repairs a room moves the same cells corrosion does, and two of
twenty segments even read negative gain, which `INC` cannot produce alone. The
fix flagged there was to stop reconstructing corrosion from its side effect and
read the condition the ROM actually tests: `$6563`, the flag DISC-270 decoded as
rising only when the Alien's room equals its destination (it stayed rather than
moved), gating the `INC $653F,X` on the *next* dispatch.

300 s watching `$6563` directly, at 0.3 s resolution, paired with `$7935`/
`$6501`:

* **the flag's own transitions land 7.8-30.1 s apart - multiples of the
  measured 7.61 s action period** (DISC-270), confirming it toggles once per
  Alien dispatch rather than drifting with the poll; a duty cycle built from it
  is therefore a real per-pass fraction, not sampling noise.
* **never once set at the instant of arrival** (0 of 14 surfaced transitions) -
  living confirmation that moving in does not corrode, only lingering does.
* **set for 38.2% of surfaced time** (167 of 437 samples).

**That is close to the remake's own ~⅓**, and on the side that matters: the
remake's fraction falling out of its movement model rather than being
calibrated was the concern DISC-292's item raised, and this measurement does
not contradict it enough to justify changing `ROOM_DAMAGE_ALIEN_PER_ACTION` or
the movement model on its account. One 300 s sample is not a large-N estimate -
the true rate could plausibly be anywhere from the high twenties to the
mid-forties on this data alone - but it is no longer confounded, and it does not
point in a direction that would explain DISC-258's unwinnability gap by itself.

**Action:** P-8 closed. The corrode-fraction question that was blocking a fair
re-run of the weapon breach gates (DISC-289) is answered well enough that the
gap DISC-289 found is *not* explained by the fraction being badly wrong - which
narrows P-9 to the other candidates (per-hit Alien damage, hit frequency) rather
than leaving corrosion as an open suspect.

## DISC-297 - CORRECTION: DISC-296 reproduced a trap this file already warned about

**Found/done:** 2026-08-18. Retracts DISC-296's "P-8 closed" and softens
DISC-295's framing of its own anecdote.

DISC-290 already tried polling `$6563` directly, twice, and documented exactly
why it fails: the flag is raised and cleared *inside a single Alien action*, so
what a poll catches is a function of sample rate, not of the game - 42% at
24 samples/s, 0% at 2 samples/s, same running game. It moved to a damage-delta
estimator instead, ran it carefully over a full 360 s with zero dropped samples,
and got a considered answer: **disk 0.13, remake 0.41**, a real ~3x gap, and
that is P-9's lead.

DISC-296 polled `$6563` at 0.3 s and reported a duty cycle of 0.382 as a clean
answer superseding the damage-delta method - without having read that the exact
method had already been tried and rejected in this file, for a reason that
directly applies (this session sampled at a different, also-arbitrary rate, and
0.382 sits suspiciously close to the *remake's* 0.41 rather than the disk's
known 0.13). The apparent 7.6 s-aligned transition gaps do not rescue it: a
flag that pulses briefly can still produce polling artefacts that happen to
cluster near the action period, especially over only eleven observed
transitions.

**DISC-296 is retracted.** P-8 was already correctly answered by DISC-290
before this session touched it, and remains so: disk 0.13, remake 0.41. Nothing
tonight moves that number in either direction.

**DISC-295's room-27 anecdote needs re-reading too.** It compared eleven
passes with zero corrosion against the remake's ~⅓ and called that improbable.
Read against DISC-290's *disk* rate of 0.13, not the remake's, eleven straight
misses have probability `0.87^11` ≈ 21% - unremarkable. The anecdote is mild
supporting colour for the already-established disk rate, not independent
evidence of anything sharper.

**What tonight actually contributed to P-8/P-9:** confirmation, from a second
session and a different (if flawed) method, that `$6563` behaves as DISC-270
decoded - never set at the instant of arrival - and a second documented case of
the same polling trap, which is worth keeping so a third session does not spend
a live-oracle window rediscovering it a second time. The corrode-fraction
question and its fix (P-9: bring the remake's rate toward the disk's 0.13,
re-run the gates both ways) are exactly where DISC-290 left them.

## DISC-298 - F-1's decision-free half: derivation as a generator

**Found/done:** 2026-08-18.

F-1 wants a first-run screen that asks for the disk image and derives what the
game needs with a progress line, instead of printing a path and a command. Two
halves, and only one is decision-free: **how the player picks a file** is a
real design question (a native OS dialog via `tkinter`, foreign to a pygame
app that owns its whole window, against an in-game C64-styled browser, which is
more work and more in-fidelity) and this pass does not choose it.

What has no such question is the plumbing, and it was missing regardless of
which picker gets chosen: `_derive_assets` only existed as a function that
prints straight to stdout and shells to a subprocess for the BASIC listing, so
nothing inside the pygame app could drive it and show a progress line even with
a working file picker in hand.

Split it. `derive_assets_from(nib)` is a generator yielding one `DeriveStep`
(`label`, `ok`) per stage - extract, chars, intro, sfx, the BASIC listing - with
no dependency on argv or being run as a subprocess. `_derive_assets` becomes a
thin CLI face over it: same output, same exit codes, verified against the real
disk in a clean-room test.

**Action:** F-1's plumbing is done and tested end-to-end against the real
`.nib`. What remains is the actual screen: the file-picker mechanism (a
decision, not an engineering task), a `Screen` state that renders
`derive_assets_from`'s steps as they arrive, and wiring it in beside
`Screen.FIRST_RUN`'s edition question as the item asked.

## DISC-299 - L5/R1-R6: reading the session logs the way the owner actually will

**Found/done:** 2026-08-18. Closes L5 and R1-R6 as specified.

The owner's own words set the scope, and the plan already recorded them: *"my
plan was to simply give them to an AI assistant and ask why something happened in
playtesting."* Not a log viewer - text small enough to paste, self-explanatory
to a reader who has never opened this codebase. `tools/replay.py` is that text
generator, built to the plan's own six items:

* **R1** - `resolve()` is the exact inverse of `journal._delta`: a present key
  overwrites, an explicit `None` clears (distinct from "unchanged", which the
  format also needs), crew is merged member by member. Verified the strong way
  - not round-tripped against itself, but diffed field-for-field against a
  **live `Simulation`** run in parallel with the journal that recorded it.
* **R2** - `--from`/`--to`/`--around`/`--window`, accepting either a bare tick
  or `5m`/`90s`/`1h` at the measured `MAIN_LOOP_HZ` (7.886).
* **R3** - `--crew`/`--room`, the second matching either a crew member's room
  or the Alien's.
* **R4** - `--summary`: deaths, the Alien dying, fire/alarm onset (once, not
  every tick it persists), notices, phase changes, and orders paired with
  outcomes - one page of prose with tick numbers.
* **R5** - `--legend`, needing no log file, explaining `fear` counts up and
  `IN_TRANSIT` is not a final answer.
* **R6** - orders paired with what became of them. This needed one small
  addition upstream: `journal.note` recorded that an order was *given*, never
  what happened to it, so the app loop now also logs each
  `(order, OrderOutcome)` pair from `Simulation.last_outcomes` the tick it
  resolves - the same boundary `journal.record` already uses, and the one
  place that distinction exists at all. The summariser pairs an action to the
  first *terminal* outcome that follows it, skipping `IN_TRANSIT`: "still
  walking" is not an answer to "what became of it".

**Deliberately not built**, matching the plan: a graphical timeline, a
replay-into-the-renderer mode, a diffing tool. All three are more work than
this file and none serves a person pasting text into a chat.

**Action:** shipped, `tools/replay.py` plus `tests/test_replay.py` (17 tests,
including the live-simulation round-trip). L5 and R1-R6 closed.

## DISC-300 - CR1-CR5: a credits screen, built entirely from records that already existed

**Found/done:** 2026-09-02. Closes CR1-CR5 as specified.

The plan's own opening line is the constraint: this screen exists to
acknowledge *supplied* media, so it must draw nothing that isn't already
written down somewhere, or it would be inventing a credit rather than
reporting one.

* **CR1** - `SamplePlayer.credits()` already read `sounds.toml` for every
  supplied sound; `media.credits()` calls it rather than duplicating the
  parse, matching the standing rule that a fact lives in one place.
* **CR2** - generalised that one manifest into `MEDIA_MANIFEST =
  "manifest.toml"`, one per media folder (`portraits/`, `map/`, `sprites/`),
  read by `_read_media_manifest`/`_media_credit` in `media.py`. An entry with
  no `title` and no `author` is silently skipped - CR1's own rule, that a
  file present with nothing to say about it stays quiet rather than showing
  up as a blank row.
* **CR3** - `PROJECT_CREDITS`: the game itself ("Paul Clansey, for Mind
  Games / Argus Press Software" - the credit the disk's own boot screen
  gives, per DISC entries on the "PAUL CLANSEY (C)1984 CONCEPT SOFTWARE"
  text) and the disassembly (`docs/re/`), listed before any supplied media so
  the screen opens with what the project *is* before crediting what was
  added to it.
* **CR4** - `Screen.CREDITS` reuses `Screen.MANUAL`'s exact paging shape
  (`_on_credits`/`_leave_credits` mirror `_on_manual`/`_leave_manual` line
  for line) rather than a third scrolling mechanism, at
  `CREDITS_ROWS_PER_PAGE = 8`.
* **CR5** - `InputEvent.SELECT_CREDITS`, a bare `5` beside `3
  INSTRUCTIONS`/`4 OPTIONS` (no Ctrl chord - the ROM has nothing here to
  imitate the polarity of). The row is hidden under ORIGINAL two ways, not
  one: `_draw_selection` does not draw it when `is_original(...)`, and
  `_on_selection`'s `SELECT_CREDITS` branch returns immediately under the
  same check - a hidden row that still answered the key would be worse than
  no row at all, per the plan's own wording.

Two real bugs turned up building CR4/CR5's UI wiring, both in code the
screen shares with MANUAL/OPTIONS rather than in the new code itself:

1. `_draw_selection` only ever set `self._options_model` inside
   `_draw_options()`. A player who never opens OPTIONS but is already on a
   non-ORIGINAL profile would see the CREDITS row drawn correctly (drawing
   reads `flow.options` directly) but a **click** on it would consult the
   stale `None` `_options_model`, read that as ORIGINAL, and silently do
   nothing. Fixed by setting `self._options_model = flow.options` as the
   first line of `_draw_selection()`, every frame, regardless of whether
   OPTIONS has ever been visited.
2. `_pointer_front_end`'s click-to-event mapping for the selection screen
   indexed a fixed 4-element tuple. A click on the new 5th row (index 4)
   would raise `IndexError` rather than opening CREDITS. Fixed by building
   the event list dynamically, appending `SELECT_CREDITS` only when `not
   is_original(...)`, with a bounds check before indexing.

**Action:** shipped - `media.py` (`credits()`, manifest reading), `core/flow.py`
(`Screen.CREDITS`), `render/frontend.py` (`_draw_credits`),
`render/pygame_app.py` (dispatch, wheel, the `5` key, the click-mapping fix),
`tests/test_media_credits.py` (8 tests) and `tests/test_credits_screen.py`
(8 tests). CR1-CR5 closed.

## DISC-301 - P-9: the corrode gate is right; corridors structurally never hold

**Found:** 2026-09-03. **Method:** live capture (VICE oracle, WarpMode off,
undamaged Alien so hunting cannot confound it) correlating `$7935` (room),
`$6501` (in-duct), `$64B4` (hunt latch) and `$653F,X` (room damage), plus a
direct computation over the already-decoded `ALIEN_ROUTES` tables.

P-9 read DISC-292's finding — the remake's Alien counts itself "arrived" (and
so corrodes) on ~41% of actions against the disk's ~13% — as `corrode_pending`
"being set too readily," implying a gating bug in `advance_alien`/
`_begin_action`. It is not one.

### The gate is decoded correctly

Read live off `$89EC-$8A11` (the surface-move dispatcher):

```
89EC  LDA $7A3A,Y   ; route-table lookup for the CURRENT room
89EF  STA $64E6     ; -> var_alien_target, UNCONDITIONALLY, even self-refs
89F7  LDX $64B4
89FA  BEQ $8A11     ; not hunting -> RTS, destination ACCEPTED (incl. self-ref)
```

`$64E6` is written from the route table before the hunting check, so a
self-referencing roll (destination == current room) really does leave
`$64E6 == $7935`, which is exactly the condition `$8B03`/`$6563` reads as
"arrived" next pass. `core/alien.py`'s `dest_id is None → arrived on the next
pass` is a faithful model of this — **not the bug**.

### What actually differs: corridors cannot self-reference at all

Computing the self-reference (destination == source) rate directly from
`gamedata_snapshot.ALIEN_ROUTES` for every room, over all 16 surface rolls:

| room type | mean self-ref rate | range |
|---|---|---|
| corridors (7 rooms) | **3.6%** | 0% for 6 of 7, one at 25% |
| named/functional rooms (28 rooms) | **44.3%** | 0-58% |

A corridor is, by the disk's own route-table design, a room the Alien almost
never re-selects as its own destination — it is transit space, not somewhere
it lingers. Only named rooms (airlocks, cargo pods, engineering, cryo vault,
stores, etc.) have a real chance of the Alien "holding" there long enough for
`$6563` to persist pass to pass and corrode.

### This matches the live sample directly

The 240 s capture spent 19/24 room-visits (79%) in corridors (rooms 9-12,
`corridor_2`-`corridor_5`) and accrued **zero** room damage the entire run —
including one continuous 41.3 s dwell in `cryo_vault` (58% self-ref rate) that
also happened to land nothing, plausible at that rate over ~5 actions but
worth a longer follow-up capture to confirm it isn't itself an outlier. Hunt
latch (`$64B4`) was 0 in all 25 segments — an undamaged Alien genuinely never
hunts, ruling that out as a confound for this run.

### What this means for P-9

**Do not touch the corrode gate.** `corrode_pending`/`arrived` already
implements `$89EC-$8B13` correctly. The 41%-vs-13% gap is much more likely a
**room-visit distribution** difference: if the remake's simulated games spend
proportionally more time in named/functional rooms relative to corridors than
the real disk does — for whatever reason drives which rooms an Alien actually
occupies over a long run — that alone reproduces a several-times-higher
average corrode rate with an identical per-room gate and identical route
tables. **Action:** compare room-visit histograms (fraction of ticks/actions
spent in corridors vs. named rooms) between the remake's own long runs and a
longer, cleaner disk capture, before changing anything. This is a materially
different next step than the one P-9 currently describes and its `todo.md`
entry has been updated to say so.

## DISC-302 - P-9 follow-up: the long capture caught something bigger than P-9

**Found:** 2026-09-03. **Method:** a second, longer (600 s) live capture,
same setup as DISC-301, continuing the same session.

### The room-visit comparison stays inconclusive, and here is why

The first clean segment run (~71 s, before the game ended - see below) split
58% named / 42% corridor; the shorter capture in DISC-301 split 21%/79% the
other way. Two live samples this size disagreeing with each other by that
much says the samples are too small and too short to settle anything, not
that either is wrong. **DISC-301's "next step" stands as written**: this
needs a long, clean sample, and two short ones a session apart do not add up
to one.

### What ended the capture is the more interesting finding

At 185 s the screen changed to the disk's own ending card - "ALL CREW LOST",
0% competence - while this capture was doing nothing but reading memory. No
input was sent at all. **On the real disk, an entirely undefended crew dies
and ends the game in about three minutes.**

The same idle setup on the remake (no orders, `Simulation.advance()` called
in a bare loop) was run for comparison, 6,000 ticks across 8 seeds: **every
seed stayed in `GamePhase.RUNNING` for the full budget.** The remake's crew do
not die from pure neglect within a window several times longer than the disk
just demonstrated they do.

This is a separate question from P-9's room-damage rate — it is about *crew*
survival, not *room* structure - and it is not yet clear whether it is a real
gap or an artifact of this particular idle harness (the remake's crew may
need to be *doing* something, or be in the Alien's path, for the disk's own
lethality to apply; an idle crew sitting in their start rooms might simply be
somewhere the disk's Alien rarely reaches early on, and three minutes was
this capture's own bad luck). **Filed as its own open question, not folded
into P-9** - see `todo.md`. Do not treat "the remake's crew are too safe" as
established from one 185 s sample any more than P-9's room numbers were
established from one.

**Action:** two follow-ups needed, both blocked on a long, single,
uninterrupted disk session rather than another short one:
1. P-9's original ask - corridor/named room-time split, at a sample size
   that can actually resolve a difference this noisy at 71-240 s.
2. **New** - repeat the idle-crew-survival comparison several times on each
   side (the disk dying at ~185 s once is one data point) before concluding
   anything about crew death timing, faithfully or otherwise.

## DISC-303 - the CREDITS row collided with the copyright line, found by actually taking a screenshot

**Found:** 2026-09-03, taking real screenshots for README.md.

CR4/CR5 (the credits screen) added a third possible row to the selection
screen's `extra_rows` list, but the "PAUL CLANSEY (c)1984 CONCEPT SOFTWARE"
copyright line below it stayed hardcoded at `y=176` — the position that was
only ever correct for the two-row (ORIGINAL) case. Under any non-ORIGINAL
profile, the third row (CREDITS) landed at `y=174`, two pixels above the
copyright line, and the two drew on top of each other: exactly the same
collision `_draw_selection`'s own comment already describes fixing once
before, for `DEBUG ON`, reopened from the other side once `extra_rows` could
hold three items instead of two.

**Nothing in the existing 1354-test suite caught this** — CR4/CR5's own tests
checked that the row is drawn (or isn't, under ORIGINAL) and that pressing 5
does something, but nothing rendered the *non-ORIGINAL* selection screen and
looked at where things actually landed relative to each other. Found only
because an actual screenshot was taken and read by eye — the project's own
stated lesson (`test_fv3_frame_harness.py`'s docstring) about rendering bugs
needing a look, not just a passing unit test, reproducing itself.

**Fix:** the copyright line's `y` is now computed from the same row count
`extra_rows` produces (`126 + (extra + len(extra_rows)) * 12 + 2`) instead of
a fixed `176`, so it always lands below however many rows are actually drawn.

**New regression guard:** `test_the_credits_row_does_not_collide_with_the_copyright_line`
counts distinct **text bands** (blank-to-text transitions) in the row's own
pixel range rather than checking for a blank *row* — a single blank row of
slack is not proof against collision (a font glyph already has blank rows
inside its own cell), but a genuinely merged overlap reads as one wide text
band where two cleanly separated lines read as two. Verified against the old
code directly (`git stash` on just the one file): the old code fails this
test (`1 >= 2`), the fix passes it.

**Action:** shipped. `src/alien_remake/render/frontend.py`'s `_draw_selection`,
`tests/test_credits_screen.py` (+1 test, now 9). Full suite 1354 passed, mypy
clean.

## DISC-304 - the credits test-isolation gap, found by actually populating out/sounds/

**Found:** 2026-09-03, adding the owner's own Freesound.org credits and
developer credit to the in-game CREDITS screen.

`tests/test_media_credits.py`'s `_root()` helper isolated asset lookups by
setting `$ALIEN_REMAKE_ASSETS` alone, on the assumption that was the only root
`assets.asset_roots()` ever consults. It is not: that function returns a
priority chain (the env override, then the checkout's own `out/`, then a
platform data dir), and `media._sound_player()` walks the whole chain looking
for the first one that actually has a `sounds/` subfolder. An override
directory with no `sounds/` of its own (the normal case for a test wanting
"nothing supplied") falls straight through to whichever later root does have
one.

This was invisible for as long as no real `out/sounds/sounds.toml` existed
anywhere on a machine running the suite. Creating one - to actually credit the
two Freesound.org recordings this remake uses, plus a developer credit
neither the README's own Credits section nor `media.PROJECT_CREDITS` had
before now - made three tests in the file start failing, because their
"nothing supplied" baseline was quietly picking up the real manifest instead.

**Fix:** `_root()` now also monkeypatches `assets.asset_roots` itself to
return exactly `(tmp_path,)`, not just the env var, so isolation is real
regardless of what a given machine's own `out/` happens to hold.

**Action:** shipped. `tests/test_media_credits.py`, `media.PROJECT_CREDITS`
(+1 entry, "This remake" / OuijaGhost), `README.md`'s Credits section (the
matching line), and `out/sounds/sounds.toml` (local to this machine, `out/`
is never tracked - the two credits it names still need their matching `.wav`
files copied into `out/sounds/` to actually play, which crediting them does
not by itself require). Full suite 1356 passed, mypy clean.

## DISC-305 - C2/T6: turns as a real options-menu mode, and the poll_orders() trap

**Found:** 2026-09-04, making `turns` an in-game option per the owner's goal.

T1-T5/T7/T8 (the turn-based simulation primitives) and `--headless-turns`
were already done; what was missing was reaching the mode from the game's
own window at all, which is what C2 and T6 together close out.

### C2 - the options row, and where "changes apply at once" actually breaks down

`turns` (off/on) landed the same way every other option does - `OPTION_SPECS`,
`settings.KEYS`, `--turns` on the command line, both PROFILES set to `off`
(a pacing overhaul is opt-in regardless of preset, not a fidelity claim
either way). `app.run_app` reads `flow.options.values.get("turns")` fresh
every frame, matching `crt`/`front_end`'s own "live" rule - no new plumbing
through `_LiveRules` needed, since turns changes nothing about what the
simulation does, only how often this loop is willing to call `advance`.

**The real bug was in detecting "did something happen this frame."**
`run_turn_based` (the existing headless reference loop) calls
`advance_until_resolution` unconditionally every iteration, which is right
for a harness that must always make forward progress with no external
clock. An interactive turn-based mode wants the opposite: nothing should
advance while the player is still deciding, matching the options row's own
help text ("nothing moves until you give an order"). The natural way to
detect "an order arrived this frame" looked like checking
`renderer.poll_orders()`/`poll_special_options()` — until `test_integration_loop.py`'s
own docstring (already on file, from D-187) was reread: the real backend's
`MenuController.fire()` calls `sim.queue_order`/`apply_special_option`
**directly during `poll_input`**, and `poll_orders()`/`poll_special_options()`
always come back empty for it - only the passive test fakes route orders
through those methods at all. Gating on the returned lists alone would have
shipped a `turns` option that compiled, tested green against a passive fake,
and never actually advanced a single tick in real play.

**Fix:** also check `flow.sim._orders` (the pending-orders deque) directly,
which is non-empty exactly when the real backend has just queued something.
Verified against both shapes: `test_turns_on_advances_once_an_order_is_queued`
mimics the real backend (`sim.queue_order` inside `on_input`, the way
`MenuController.fire()` does it) rather than returning a list, which is
precisely the case that would have passed silently with the wrong fix.

One known gap, left rather than papered over: a Special Option (FIGHT FIRE,
arming/cancelling auto-destruct) applies immediately with no queue to
detect afterward, so one fired with no order also pending will not itself
trigger an advance that frame. Rare in practice (a player almost always also
gives a crew order), and noted in `app.py`'s own comment rather than solved
here.

### The eleventh row, and C4's layout guard doing its job a second time

Adding a tenth options row (the audio rows) once pushed the last row onto
the copyright/hint line — caught by C4's own layout guards, fixed by moving
a stray overlay up. The eleventh row (`turns`) reopened the identical
squeeze from the numbers side: `test_the_screen_still_fits_if_a_row_is_added`
(written *because* of the first squeeze) failed exactly as designed. Fixed
by trimming the help box one cell shorter (nine rows to eight - the five
lines of help text it holds start at row 4 and only need rows 4-8) rather
than compressing the option list, and `_OPTION_FIRST_ROW` down by one to
match. This is the second time this exact category of bug has been caught
by a test instead of a screenshot, which is the whole reason the guard test
was written the first time.

### T6 - a turn counter, independent of developer mode

`flow.turn_count` is a `GameFlow` presentation counter (0 under real-time
pacing, incremented once per resolved turn under `turns`), not a
`GameState` fact — turn numbering only means something once the game is
being paced by order-resolution rather than the clock. Drawn in the border
by `_blit_turn_indicator`, carried across from `flow` into the renderer at
the same point `_sim`/`_ship` are adopted (`render(state)` never sees
`flow`, so this is the only way the border blit can reach it). Deliberately
**not** gated on `_debug_markers`: this is what the option itself asked to
see, not a development tool, so it must show whenever `turns` is on
regardless of whether Ctrl+3 is.

What T6 originally scoped also included a per-order cost preview before
committing (the decoded per-character cost table already sitting in the
plan makes this straightforward) - not built here. "Make turns work as an
option in the options menu" is what was asked, and is what shipped; the
cost preview is a further step past that, not a silent scope cut.

**Action:** shipped - `core/options.py`, `settings.py`, `__main__.py`,
`app.py`, `core/flow.py`, `render/{pygame_app,debug_overlay,protocol,frontend}.py`.
7 new tests (`test_integration_loop.py`, `test_options_screen.py`). Full
suite 1365 passed, mypy clean. T1-T8 and C1-C4 all closed.

## DISC-306 - P-9: a long clean capture contradicts DISC-301's own reframing

**Found:** 2026-09-04. **Method:** a single uninterrupted 600s live capture
(WarpMode off, undamaged Alien throughout, hunt latch confirmed never set
across all 53 segments), the long clean sample DISC-301/302 both said was
still needed.

### The room-visit split does NOT explain the gap after all

DISC-301 proposed that the remake's Alien spends more time in
self-referencing named rooms than the disk's does, and that this - not a
gating bug - explained the remake's higher corrode rate. This capture is
the long, clean sample that could actually test that, and it does not hold
up: **82.0% of surface time was in named rooms, 18.0% in corridors** - close
to the remake's own long-run figure (85%/15%, DISC-301), not the 79%/21%
corridor-heavy split the earlier short sample showed. That earlier split was
exactly the "too short a sample, wherever it happened to start" artifact
DISC-302 already warned it might be.

**So the room-visit distribution matches between disk and remake.** The
41%-vs-13% "arrived" gap, and the corrode-rate gap it was meant to explain,
needs a different explanation than DISC-301's.

### The corrode rate itself, measured properly this time

Earlier captures (this session and DISC-290/292) read `$653F` for only the
Alien's *current* room, which undercounts total damage across a run: damage
dealt in a room the Alien has since left is invisible to a reading that only
ever samples one address. Reconstructed here from per-visit deltas instead
(damage at the end of each room-segment minus its start): **8 damage events
across 28 surface room-changes = 0.286 per room-change** - between DISC-290's
0.13 (n=4 events, 360s) and the remake's 0.41, not close to either.

Both disk figures rest on small event counts (n=4 and n=8) with Poisson
error too wide to call: 0.13 and 0.286 are not obviously inconsistent with
each other, and 0.286 is not obviously inconsistent with the remake's 0.41
either. **This measurement has now been attempted four times across two
sessions and has not converged.** The honest state is: the disk's true
corrode-per-room-change rate is somewhere in a broad band the two disk
samples together bracket loosely, and the remake's ~0.41 may or may not sit
meaningfully outside it - the data so far cannot say.

**A better method for whoever picks this up next.** `$653F` is a 36-byte
array, one entry per room - reading it whole (`vice_memory_read` size 36)
every sample gives every room's damage in one call, so a true *global*
damage total per unit time falls out directly with no per-visit
reconstruction needed. This should have been the method from DISC-290
onward; every capture in this thread, including this one, read one room at
a time and paid for it in reconstruction complexity and (per DISC-292's own
history) in outright mistakes.

**Action:** do not change the corrode gate or the room-visit model on the
strength of anything measured so far (both DISC-301's diagnosis and the
original DISC-292 "3x too high" headline are now in question). The next
useful step is the whole-array read above, not another single-room capture.

## DISC-307 - P-9: two independent long captures converge on ~0.29, not 0.13 or 0.41

**Found:** 2026-09-04, same session as DISC-306, using the whole-array fix
that entry recommended.

A second 600s capture, reading `$653F` whole (36 bytes, one call) every
sample instead of just the Alien's current room: **global damage gained 8
over 27 surface room-changes = 0.296 per room-change.** This is a different
600s live session from DISC-306's, measured a different way (a true running
total vs. that entry's per-visit delta reconstruction from a single-room
reading), and the two agree closely: **0.296 against 0.286.**

**This is real convergence, not two more scattered numbers.** Combined with
DISC-290's original 0.13 (n=4 events, 360s - the smallest and earliest
sample in the thread) and the remake's own ~0.41, the picture is now:

| source | rate | n (events) | duration |
|---|---|---|---|
| disk (DISC-290) | 0.13 | 4 | 360s |
| disk (DISC-306) | 0.286 | 8 | 600s |
| disk (DISC-307) | 0.296 | 8 | 600s |
| remake (DISC-292) | ~0.41 | 357 room-changes, 6 seeds | 6,084s |

The two largest, cleanest, most recent disk samples agree with each other
to within 4%. DISC-290's figure, the one DISC-292's "remake corrodes ~3x too
often" headline was built on, is now the outlier - smallest sample, and the
only one not using the whole-array read. **The real gap is closer to 1.4x
(0.29 vs 0.41), not 3x.**

**Still not settled enough to act on.** 1.4x is a much smaller and more
plausible gap - within the kind of variation four different capture windows
of the same disk might show for other reasons (which rooms happened to be
visited, whether the sample caught more or less settled dwelling) - but
"smaller than thought" is not "confirmed within noise." Whoever next picks
this up should treat 0.29 disk / 0.41 remake as the working numbers, not
0.13 / 0.41, and decide from there whether a ~1.4x gap is worth chasing
further or is inside the noise floor these four samples together imply.

**Action:** superseded DISC-292's "3x too often" framing and DISC-301's
room-visit-distribution theory (already retracted by DISC-306). No code
change - the corrode gate remains correctly implemented per DISC-305, and
the room-visit split matches (DISC-306). `todo.md`'s P-9 entry carries the
updated numbers and the still-open question of whether 1.4x warrants a fix.

## DISC-308 - the crew-survival question: a second data point, opposite of the first

**Found:** 2026-09-04, incidentally — the disk sat idle (zero player input,
only VICE memory reads) for over 1,200s across the two DISC-306/DISC-307
captures, with the game still in `play` and not ended.

DISC-302 recorded one prior idle session hitting the disk's own "ALL CREW
LOST" ending at ~185s, and was explicit that one sample proves a data
point, not a rate. This is the second data point, and it points the other
way: over 20 minutes idle, the game had **not** ended. `$7D45` read
`[0, 6, 5, 4, 1, 0, 1, 1]` (Alien damage, then seven crew slots) — one
crew member reading `0` (plausibly dead) and two at `1` (plausibly close to
it), but the other four still well above that.

**Flagged rather than trusted at face value: two of those readings (6, 5)
are outside the 0-4 range this project's own decoded `CREW_START_HEALTH`
model expects.** Either `$7D45,Y`'s layout or stride is not quite what is
assumed here, or health is not capped the way the remake models it, or
this is a misread of a different field entirely. Not resolved this
session — noted so a future one does not take these two numbers as
confirmed crew health without rechecking the decode.

**What is solid regardless of that:** the game ran idle for >1,200s without
ending, against one earlier sample ending at 185s. That is enough on its
own to say DISC-302's single 185s sample was not a stable rate - whatever
the true distribution of idle survival time is, it has enough spread that
one sample cannot describe it. The idle-crew-survival question needs
several timed trials on the disk side, deliberately (starting from a fresh
game, timing purely idle survival to death or a cutoff), not incidental
readings taken during unrelated captures.

**Action:** neither confirms nor closes the crew-survival question - it
raises the same sample-size caution DISC-302 already gave, now with a
second, contradicting data point to prove the point rather than assert it.
`todo.md`'s entry updated accordingly. The health-array anomaly is a new,
separate small thread worth a look before the next capture that reads
`$7D45`.

## DISC-309 - the attack banner/animation could get stuck, and why the fix has to check ground truth

**Found:** 2026-09-05, three related player reports.

`self._attacking`/`self._attacking_crew_id` (`render/audio.py`) is a *latch*
driven by sound cues, deliberately (P5-3/P7-12): it survives from the tick
`ATTACK_ALERT` lands to the tick a movement/grille blip ends the sequence,
because recomputing it fresh from just one tick's cues broke an earlier,
different bug. That same latching is what let it get stuck this time:
`sound.audible()` mutes MOVEMENT/GRILLE cues *while attacking* (`$4E42`/
`$4E5C`'s own `LDA $64BB` gate) — which is also the **only** cue that clears
the latch (`elif {MOVEMENT, GRILLE} & set(played)` in `play_sound_cues`).
Once set, the latch could only ever be cleared by an event its own mute
rule had just silenced.

Turn-based mode's cue coalescing (T7) made this common rather than rare: a
whole turn's cues arrive in one batch, and the `if`/`elif` there always lets
a present `ATTACK_ALERT` win regardless of whether a movement cue in the
same batch happened chronologically after it. Reported symptoms: the attack
banner (row 23, yellow) staying up after repeated ATTACK orders even though
each individual encounter had ended, and the animation continuing to play
for a victim who had since moved to a room the Alien was not in.

**Fix:** a per-frame ground-truth reconciliation in `render/play.py`,
alongside the existing D-139 deselect check. `state.alien.attack_sequence`
(`$6562`, set at `$8AE1` and cleared by `reset_attack_state $8C80` -
`core/alien.py`) is the simulation's own authoritative answer to "is an
encounter actually active," and cannot get stuck the way a cue-inferred
latch can, since it is recomputed from real encounter state every Alien
action rather than inferred from which sounds happened to arrive in a
batch. Checked every frame: if `self._attacking` is set but the Alien is
dead/gone, `attack_sequence` is false, or the victim is no longer
co-located with it, the composite stops. This is a **correction on top of**
the cue-driven latch, not a replacement for it — the latch still owns
*starting* the sequence and the siren's own looping; only the clearing
side needed a ground-truth backstop.

**Two existing tests had to change**, not because they were wrong but
because they simulated "mid-attack" by setting `renderer._attacking = True`
directly with no actual encounter behind it — which the fix now correctly
refuses to honour. Two new tests pin the real bugs directly: one moves the
victim out of the Alien's room mid-attack, one clears `alien.attack_sequence`
while the victim stays selected and co-located (the "spam ATTACK, banner
stuck" shape). Both verified to fail against the pre-fix code via `git
stash` on just `play.py`.

**A related, separately-confirmed non-bug (same investigation):** the
report that incinerator/spanner room damage "seems way more than it
should" is real but not a defect - `ROOM_DAMAGE_PER_ATTACK = 6` (decoded,
`$4AFD`) applies identically to *every* non-harpoon weapon
(`elctrc_prd`/`incineratr`/`spanner`/`laser_pist`/`tracker`, all
`ITEM_ATTACK_DAMAGE = 1`), so any of them breaches a room (threshold 20) in
4 hits while the Alien needs 50 to kill - exactly DISC-289's already-open
tension between this constant and `ALIEN_DAMAGE_TO_KILL`, not something new
about these two weapons specifically. Left alone rather than patched, per
DISC-258/289's own standing warning that changing either number without
first resolving which of the three explanations is true risks shipping an
unwinnable game again.

**Action:** shipped - `render/play.py` (the reconciliation),
`tests/test_attack_banner_and_debug.py` (2 tests fixed to set up real
ground truth, 2 new regression tests). Full suite 1374 passed, mypy clean.

## DISC-310 - turn-based mode gets an initiative order (not the original)

**Found:** 2026-09-04, per the owner's request: "an initiative based system
where the game randomly assigns an order for turns at the start between all
characters and creatures. The action points to allow roughly one room move
and one action."

C2/T6 (DISC-305) made `turns` a real options-menu mode, but every slot in it
was still first-come-first-served: whichever crew member's menu the player
had open could act, every frame, with no ordering at all. The disk has no
turn-based mode to begin with, so there is no ROM routine this traces to -
this is scoped, gated, and commented as an addition on top of an
already-non-original feature, the same way `turns` itself is.

**Design.** `GameFlow._roll_initiative()` (called from `_start()` only when
`options.values["turns"] == "on"`) shuffles all 7 crew ids plus two creature
tokens (`constants.TURN_ALIEN_ACTOR = "alien"`, `TURN_JONES_ACTOR = "jones"`)
using `sim.rng` - the same seeded RNG everything else in a run is
reproducible from - into `flow.turn_order`. `flow.turn_actor_index` tracks
whose slot is live; `flow.turn_actions_left` starts each crew slot at
`constants.TURN_ACTIONS_PER_TURN = 2` ("roughly one room move and one
action" - the user's own phrasing, taken directly as the constant's
justification since there is no ROM number to anchor it to).

**Enforcement lives in `app.py`'s `run_app`,** not `GameFlow`, because that is
where the D-187 trap already lives: `MenuController.fire()` queues orders
straight onto `flow.sim._orders` *during* `poll_input`, so by the time this
code runs, an out-of-turn order may already be sitting in the queue rather
than arriving through `new_orders`. Each frame:

* skip any crew slot whose occupant has died (the roster is fixed at the
  roll and never reshuffled, so a dead crew member's turn would otherwise
  stall the game forever waiting for orders nobody can give);
* for a live crew actor, drop any order in `flow.sim._orders` whose
  `crew_id` isn't the current actor and post a `WAIT FOR <NAME>` notice -
  the player queued it out of turn, not a rejected-but-legal order;
* run `advance_until_resolution` only when something is actually queued for
  the right actor (matching C2's own "nothing moves until you act" rule);
  spend one action point per order that reaches a *terminal* outcome for
  that actor (an in-transit MOVE hasn't spent its point yet - see
  `advance_until_resolution`'s own docstring on why "resolved" means
  terminal, not merely present in `last_outcomes`); advance to the next
  actor once points hit zero;
* for the Alien's or Jones's own slot, run immediately without waiting for
  any player input at all, bounded by `constants.TURN_CREATURE_SLOT_TICKS =
  60` ticks, then hand initiative on right away - neither takes an order, so
  there is nothing for it to wait on.

**HUD:** `_blit_turn_indicator` (T6) now reads `flow.current_turn_actor()`
and shows `TURN N: <ACTOR>` instead of a bare `TURN N`, carried across the
same way `_turn_count` already was (`render(state)` cannot see `flow`).

**Timing audit:** `TURN_CREATURE_SLOT_TICKS` is a new duration in
`constants`, so `test_every_duration_is_classified` required a `Timing`
entry; classified `REAL_SECONDS` and flagged explicitly as "not the original
at all" like `BOOT_TICKS` above it, since there is no ROM constant to anchor
a loop-count classification to. `docs/TIMING.md` regenerated.

**Action:** shipped - `core/constants.py` (4 new constants),
`core/flow.py` (`turn_order`/`turn_actor_index`/`turn_actions_left`,
`_roll_initiative`/`current_turn_actor`/`advance_turn_actor`), `app.py`
(the enforcement above), `render/pygame_app.py` + `render/protocol.py` +
`render/debug_overlay.py` (`_turn_actor` HUD field), `core/timing.py` +
`docs/TIMING.md`. 5 new tests in `tests/test_integration_loop.py` (roster
completeness, out-of-turn rejection, action-point exhaustion advancing the
actor, a creature slot auto-resolving without input). Full suite 1376
passed (2 pre-existing, unrelated failures - a subprocess `PYTHONPATH` gap
in `test_screens_headless.py` and a flaky window-size assertion in
`test_resolution_independence.py`, both reproduced identically on the
pre-change tree), mypy clean.

## DISC-311 - `screen_fx`: an optional wipe-in for the title and ending screens

**Found:** 2026-09-04, per the owner's request, after reviewing `load.mov`
(a piece of unrelated third-party footage, described only for its general
technique and never reproduced here - see the `load.mov` review earlier this
session): "please do it for the intro and ending screen where the score is
shown. make this an option for screen animations in the options menu."

**Not the original at all.** The disk draws every screen whole, in one
frame - there is no transition to trace this to, unlike the title's own
letter-by-letter spelling (`title_letters_shown`, R-30, a real ROM routine)
or the ending's hull-breach spiral (`$5D17`), both of which this leaves
untouched. `screen_fx` (off/on, off by default like every other addition)
sits alongside `turns` as the twelfth options-screen row.

**Design.** A single mechanism serves both screens: `render/screen_fx.py`'s
`reveal_row(ticks, total_rows)` grows one row every
`constants.SCREEN_FX_ROWS_PER_TICK` tick, and `apply_wipe(surface, cell,
ticks, total_rows)` blacks out everything below that row, in place, after an
otherwise completely normal draw. A mask over a full draw rather than a
partial one, so nothing about *what* either screen says ever changes - only
how much of it is visible on a given frame. Wired into `_draw_title`
(`render/frontend.py`) and `_draw_end` (`render/endscreen.py`), each calling
`apply_wipe` right before its own `_present()`.

**As a free function, not a shared mixin method.** The title and ending
screens are drawn by two different mixins (`FrontEndMixin`/`EndScreenMixin`)
that mypy checks independently against `RendererState` — a method added to
one is invisible to the other's checker. Taking the surface and cell size as
plain arguments sidestepped that rather than growing the shared protocol for
one cosmetic helper.

**Where the ticks come from.** `GameFlow._screen_ticks` already counts ticks
on `TITLE` (a `TIMED_SCREENS` entry, incremented by `tick()` for the letter
animation) — the title wipe rides that for free. `ENDED` is not timed at
all (`_on_ended` waits for any key, no auto-transition), so `flow.tick()`
never touches it; `app.run_app` gained a small `elif flow.screen is
Screen.ENDED` branch that increments `_screen_ticks` on the same tick
schedule, and `sync_phase()` now resets it to 0 on the PLAYING -> ENDED
transition (previously harmless to skip, since nothing on ENDED read it).

**Options plumbing.** `screen_fx` was added the same way every other option
is - `OPTION_SPECS`, `settings.KEYS`, `--screen-fx`, both `PROFILES` set to
`off` (an opt-in regardless of preset, matching `turns`). Twelve rows no
longer fit the options screen's help-box gap: `_OPTION_FIRST_ROW` moved
10 -> 9, reclaiming the one spare row between the help box and the list -
the same trade C2's `turns` row made a session earlier.

**Action:** shipped - `core/options.py`, `core/timing.py` (+
`docs/TIMING.md`, one more `SCREEN_FX_*` constant with `TICK` in its name),
`settings.py`, `__main__.py`, `core/constants.py`
(`SCREEN_FX_ROWS_PER_TICK`), `core/flow.py` (the `sync_phase` reset),
`app.py` (the ENDED tick branch), `render/screen_fx.py` (new),
`render/frontend.py` + `render/endscreen.py` (wired in),
`tests/test_screen_fx.py` (9 new tests: pure reveal-row math, `apply_wipe`'s
row cutoff, and both screens masked early / fully revealed / untouched when
off - verified to fail with `ImportError` against the pre-change tree via a
temporary file move). Full suite passed, mypy clean.

## DISC-312 - `screen_fx` missed the boot report (the actual "first text screen")

**Found:** 2026-09-04, player report: "the screen fx being on doesn't change
how the first text screen appears." Asked which screen they meant, since
DISC-311 only wired `TITLE` and `ENDED`; the answer was "the initial screen
of text that was originally shown in the DOS terminal window but is now
presented as the first screen" - `Screen.BOOT` (B1/B2), the startup
diagnostics card `_draw_boot` draws, shown only when there is something to
report (B5) and, when it does show, genuinely the first screen a player
sees - ahead of the GREEN VALLEY spiral.

DISC-311's own scope was read too literally from "the intro and ending
screen" (TITLE and ENDED); BOOT is a third, earlier text screen the request
never named because the player did not have `show_boot` on when describing
what they wanted, but does now.

**Fix:** the same `screen_fx.apply_wipe` call, added to `_draw_boot` right
before its own `_present()`, identically to `_draw_title`/`_draw_end`. No new
tick-plumbing needed - `Screen.BOOT` is already in `TIMED_SCREENS`
(`constants.BOOT_TICKS = 75` ticks before it auto-advances to `LOADING_MENU`,
~9.5s at `TICK_HZ`, comfortably longer than the ~3.2s wipe), so
`flow._screen_ticks` is already counted for it by `flow.tick()` the same way
`TITLE`'s letter animation is - unlike `ENDED`, which needed `app.run_app`'s
own extra branch (DISC-311).

**Action:** shipped - `render/frontend.py` (`_draw_boot`), 3 new tests in
`tests/test_screen_fx.py` (masked early, fully revealed, untouched when
off) - verified to fail against the pre-fix code via `git stash` on just
`frontend.py`. Full suite passed, mypy clean.

## DISC-313 - `screen_fx`: the rest of the described effects (glitch, cursor, prompt)

**Found:** 2026-09-05, player report: "the intro has some of the effects, but
not all the described effects from the video. Please do all the effects."
DISC-311/312 shipped only the wipe (a per-row mask); the owner's own
description of the technique behind `load.mov` (reviewed earlier this
session for its general shape only, never reproduced) named four distinct
pieces, and only one had been built.

**The other three, added to the same option:**

* **Typewriter reveal.** The mask went from per-row to per-character:
  `screen_fx.reveal_position(ticks, cols)` returns `(row, col)` in reading
  order at `constants.SCREEN_FX_CHARS_PER_TICK` (16) characters/tick, and
  `apply_terminal_fx` masks from that column onward on its row and every row
  after. 16/tick reveals a 40-column row in 2.5 ticks - visibly typed rather
  than an instant per-tick row-pop - while a worst-case ~22-row boot report
  still finishes in ~55 ticks, safely inside `BOOT_TICKS` (75) with room to
  spare to actually read it before the auto-advance.
* **The cursor.** A blinking underline block at the current reveal position,
  `constants.SCREEN_FX_CURSOR_BLINK_TICKS` (4) ticks per half-cycle - the
  conventional terminal-cursor rate.
* **The glitch.** A fading burst of grey/white "static" cells for the first
  `constants.SCREEN_FX_GLITCH_TICKS` (12) ticks after a screen is entered,
  positioned by `glitch_cell_positions` - a fixed LCG seeded from the tick
  number rather than an RNG object, since none of `screen_fx.py`'s callers
  (screen draws) carry one. Deterministic: the same tick always produces the
  same cells, which is what makes it testable at all.
* **The prompt line.** BOOT's own `PRESS ANY KEY` (not ROM data - the
  remake's own boot-report UI) grows a `"> "` prefix when the option is on.
  **Deliberately not added to the ending screen**: `_ENDING_PRESS_ANY_KEY`
  is decoded ROM text (`$6475`), and rewriting it to carry an invented prompt
  would be exactly the kind of addition the replica-fidelity rule exists to
  catch, cosmetic option or not - the ending gets the reveal/cursor/glitch
  three, never a fourth piece the disk never printed.

All four stay pure functions of the tick count (`apply_terminal_fx(surface,
cell, ticks, total_rows, total_cols, glitch=, cursor=)`), so a screen that
redraws whole every frame - as this renderer already does everywhere - needs
no extra state beyond `flow._screen_ticks`, already threaded through for the
row-only version.

**Action:** shipped - `core/constants.py` (`SCREEN_FX_CHARS_PER_TICK`
replaces `SCREEN_FX_ROWS_PER_TICK`; `SCREEN_FX_GLITCH_TICKS`,
`SCREEN_FX_CURSOR_BLINK_TICKS` new), `core/timing.py` + `docs/TIMING.md`,
`core/options.py` + `__main__.py` (help text updated to name all four
pieces), `render/screen_fx.py` (rewritten: `reveal_position`,
`glitch_cell_positions`, `apply_terminal_fx` replace `reveal_row`/
`apply_wipe`), `render/frontend.py` (`_draw_title`, `_draw_boot` - the
latter also gaining the prompt prefix), `render/endscreen.py` (`_draw_end`,
explicitly without a prompt). `tests/test_screen_fx.py` rewritten: pure math
for `reveal_position`/`glitch_cell_positions`, `apply_terminal_fx` unit
tests (mask boundary, glitch fades out, cursor blinks), and per-screen
integration tests including one pinning that the ending's decoded text
never grows a prompt. Full suite passed, mypy clean.

## DISC-314 - `screen_fx`: scoped to BOOT only, plus power-on/degauss/streak/letters/colour

**Found:** 2026-09-05, player follow-up: "the intor [sic] has some of the
effects, but not all the described effects from the video. Please do all
the effects" — then, a session later: "The intro animation should just be
for the initial screen of dos text." Two changes at once: narrow *where*
the effect runs, widen *what* it does there.

**Scope narrowed to `Screen.BOOT` only.** DISC-311/313 also wired the option
into `TITLE` and `ENDED`; `_draw_title` and `_draw_end` now draw exactly as
they did before `screen_fx` existed, with a comment at each site pointing
here. The two new "never touches" tests in `tests/test_screen_fx.py` diff a
screen_fx-on draw against an off draw at the same pixel and require them to
be pixel-identical, rather than asserting anything is masked or revealed —
the strongest statement available that the option is a true no-op there now.

**The rest of the described effects, added to `render/screen_fx.py`:**

* **CRT power-on + degauss (`apply_power_on`).** "The animation should begin
  with a classic CRT turning off [sic: on] stretch of the image from small
  to filling the screen. Add the shake animation that looks like degaussing
  ... that settles quickly." Built standalone with plain
  `pygame.transform.scale`/blit rather than reusing `render/crt.py`'s own
  `_degauss` (the deck-change transient this is modelled on): that one is a
  numpy pass over the whole composited *window*, gated behind the separate
  `crt` option being on at all, and this has to run whether or not it is.
  Transforms whatever is already drawn (typed text, glitch, streak), so it
  runs last, right before `_present()`. `SCREEN_FX_STRETCH_TICKS` (5) grows
  the picture from a thin band to full height; `SCREEN_FX_SHAKE_TICKS` (8)
  layers a horizontal wobble on top, linearly decaying to nothing -
  "settles quickly," taken as the constant's own justification.
* **Phosphor yellow (`PHOSPHOR_YELLOW`).** "The text should be yellow like
  in the original video." Replaces BOOT's white/light-blue/yellow-warning
  distinction with one tone throughout when the option is on; the plain
  off-state keeps the original three-colour scheme, since that distinction
  is a remake-authoring convenience for the flat screen, not something the
  effect needs to preserve.
* **The streak (`STREAK_COLOUR`, inside `apply_terminal_fx`).** "Hot
  yellowish green phosphor lines streak across the image as the text forms
  on each line." An additive glow (`pygame.BLEND_RGB_ADD`) over the last few
  columns behind the write head - additive rather than a flat overlay so it
  brightens the just-typed characters instead of covering them, reading as
  a scan highlight passing through rather than a differently-coloured
  stripe. (Additive blending is a no-op against already-maxed white
  channels, which is why its own test uses a black background rather than
  the module's usual white one.)
* **Letters in the noise (`glitch_letter_cells`).** "Random letters as well
  as blocks should appear in the noise." A sibling of the existing
  `glitch_cell_positions` with a different LCG seed and a character
  attached (`_GLITCH_LETTERS`: upper-case, digits, a few symbols).
  `screen_fx.py` has no font to draw a letter with, so it only says which
  cells and which letters; `_draw_boot` does the actual `_blit_cells` call,
  using the same fading-count shape as the block glitch.

**Action:** shipped - `core/constants.py` (`SCREEN_FX_STRETCH_TICKS`,
`SCREEN_FX_SHAKE_TICKS`; the module docstring's scope note corrected),
`core/timing.py` + `docs/TIMING.md`, `core/options.py` + `__main__.py`
(help text narrowed to BOOT only and the new pieces named),
`render/screen_fx.py` (`apply_power_on`, `glitch_letter_cells`,
`PHOSPHOR_YELLOW`, `STREAK_COLOUR`, the streak pass inside
`apply_terminal_fx`), `render/frontend.py` (`_draw_title` reverted;
`_draw_boot` rewritten for colour/letters/power-on), `render/endscreen.py`
(`_draw_end` reverted). `tests/test_screen_fx.py` rewritten: pure-math tests
for the two new functions, `apply_power_on` unit tests (squeeze at tick 0,
full picture once settled, decaying shake), a streak unit test, two
pixel-diff "never touches" tests for TITLE/ENDED, and BOOT integration tests
for the yellow recolour and the letter glitch. Full suite passed, mypy clean.

## DISC-315 - turn-based mode: action points shown, skip turn, auto-select, creature notice

**Found:** 2026-09-05, owner's request following DISC-310's initiative
system: "In the turn based mode should have a display of available actions
points left and a skip turn option. The game should select the next
character in sequence of the initative order after the current crew member
depletes their actions. Display text at the bottom when the Alien or Jones
takes a turn, but don't reveal what they are doing."

Four additions, all `app.py`/renderer-side — `GameFlow` itself already
tracked everything needed (`turn_actions_left`, `current_turn_actor()`).

* **Action points in the HUD.** `_blit_turn_indicator` (T6) now appends
  `AP LEFT:<n>  [K] SKIP` to the `TURN N: ACTOR` line when the current actor
  is a crew member (`None` for a creature slot - it never had a budget to
  show in the first place). Carried from `flow` each `draw()` the same way
  `_turn_actor` already was.
* **Skip turn.** `K` (mnemonic "sKip" - no other letter key is bound on the
  play screen; every other verb is a menu row navigated by cursor + fire) is
  read every frame by the new `PygameRenderer.poll_skip_turn()`, an
  *optional* `AppRenderer` hook (`getattr(renderer, "poll_skip_turn", None)`,
  the same pattern `idle` already uses) so headless test fakes need not grow
  it. Checked in `app.py` before the out-of-turn filtering: a skip drops
  whatever is queued for the skipping actor and ends their turn
  unconditionally, rather than resolving it first.
* **Auto-select the next actor.** `MenuController.fire()`'s own
  `entry.select_crew` branch was factored into `_select_crew` (same guard:
  an asleep/incapacitated crew member bounces back to the CONTROL list, per
  `$7720`/P2-5) so a new public `select_crew_directly(crew_id)` could reuse
  it without duplicating the block. `app.py`'s `_advance_actor()` helper
  wraps every `flow.advance_turn_actor()` call site (skip, action-point
  exhaustion, a creature slot ending) and calls the renderer's own optional
  `select_crew` hook when the new actor is a crew member - a turn-based
  player is not left staring at whoever's menu happened to be open when
  initiative passed.
* **The creature-turn notice.** Set on `flow.sim.state.notice` (the same
  transient row-24 mechanism `WAIT FOR <NAME>` already uses) but only
  *after* `advance_until_resolution` has already run the Alien's or Jones's
  whole slot, not before — a notice set going in would be decremented away
  by the slot's own ticks before this frame is ever drawn, since the whole
  slot resolves inline in one `app.py` iteration, before `renderer.draw()`
  is called even once. Says "THE ALIEN TOOK ITS TURN" / "JONES TOOK ITS
  TURN" — never what happened, matching the owner's own instruction and the
  same reasoning real-time mode already has for not narrating the ROM's AI.

**Action:** shipped - `core/menu.py` (`_select_crew`/`select_crew_directly`),
`app.py` (skip/auto-select/creature-notice wiring), `render/pygame_app.py`
(`poll_skip_turn`, `select_crew`, the `K` binding), `render/protocol.py` +
`render/debug_overlay.py` (`_turn_actions_left` HUD field). 5 new tests in
`tests/test_integration_loop.py` (creature-turn notice reveals no detail,
skip advances without resolving, skip drops the queued order, auto-select
fires for a crew actor, auto-select is skipped for a creature slot) -
verified to fail against the pre-fix `app.py` via `git stash`. Full suite
passed, mypy clean.

## DISC-316 - a clickable "Skip turn" row, and "quit" relabelled "back"

**Found:** 2026-09-05, owner's request: "is there enough room to add a skip
turn button in the special actions area right above quit? Can you change
where it says quit on this crew selection menus to back?"

**"Skip turn" row.** `MenuController.entries()` now inserts a "Skip turn"
row (`MenuCategory.SPECIAL`) right before the trailing "back" row when
`self.turns_on` is set — the special actions area, per the owner's own
placement. `MenuController` has no way to know whether turns is on by
itself (it is built from `sim` alone, and turns is a `GameFlow.options`
thing), so a new `turns_on` attribute is set by the renderer each `draw()`
alongside `_turns_on`. Firing the row sets `skip_turn_requested` (a flag,
not an action taken here — `app.py` already owns ending a turn and
auto-selecting the next actor, the same as it does for the `K` key);
`PygameRenderer.poll_skip_turn()` now ORs the menu's flag in with the key's
own, so the two are just two ways to ask for the same thing.

**"quit" -> "back".** Three menu rows carry this label — `crew_entries`'s
own trailing row, `get_item_entries`'s GET ITEM submenu, and
`indicate_entries`'s INDICATE LOCATION list (`INDICATE_LABEL_QUIT`) — all
three decoded ROM text (`[C $A715]`/`$A712`/`$A7C6`) and all three
`back=True`: none of them ever exits anything, they only step back one
level. The word "quit" reads as "leave the game" to a player, which is not
what happens, so all three are now labelled "back" instead. The underlying
behaviour (`back=True`, `MenuController.back()`) is completely unchanged —
this is a display-only relabelling of a decoded string, not a fidelity
break, and the `[C $A715]` citations stay in place at each site so a future
reader still knows what the ROM itself actually printed there.

**A test bug this caught:** `PygameRenderer.draw()`'s PLAYING branch sets
`self._menu.turns_on` right after the block that (re)builds `self._menu`
when the sim changes — but several existing test fixtures pre-set
`renderer._sim = sim` directly without going through that branch at all,
leaving `self._menu` at its `__init__` default of `None`. The first attempt
at this wrote `assert self._menu is not None` there, which is correct for
real play but broke six of `test_attack_banner_and_debug.py`'s own
fixtures; changed to a plain `if self._menu is not None:` guard instead.

**Action:** shipped - `core/menu.py` (`MenuEntry.skip_turn`,
`MenuController.turns_on`/`skip_turn_requested`, the `entries()`/`fire()`
wiring, the three label renames), `render/pygame_app.py`
(`self._menu.turns_on` carry-across, `poll_skip_turn`'s OR). 3 new tests in
`tests/test_remake_menu.py` (row absent when turns is off, row placement +
category when on, firing sets the flag without deselecting), 1 new test in
`tests/test_remake_pygame_input.py` (the full menu-to-`poll_skip_turn`
path), 1 existing test updated for the new label
(`test_selecting_a_crew_opens_their_order_menu`). Full suite passed, mypy
clean.

## DISC-317 - a loudness spec check, and `game_audio=sampled` renamed `enhanced`

**Found:** 2026-09-05, owner's follow-up on the audio-loudness `todo.md` item
(DISC-315's own session): "For added files I just need a volume to hit since
they are incidental sounds that need to mix into the current game's LUFS...
make the GAME AUDIO option that changes the sampling to control this as
well... The sampled setting should be updated to an 'Enhanced' option that
enables the sampled audio, adjusted audio mixing, and new audio files such
as the option to change files," plus, on scope: "have a test that runs like
[full per-file normalization] to let the user know if any files are out of
spec... on the initial dos screen and when dev mode is enabled."

**The measurement.** `audio/loudness.py` is a from-scratch ITU-R BS.1770-4
style integrated-loudness meter (K-weighting + gated block averaging), built
on plain `numpy` since no audio-analysis library is a project dependency and
none was added for this. Its own module docstring is explicit that it has
not been checked against a certified reference meter — good enough to flag
an outlier, not a mastering-grade tool. Sanity-checked against the textbook
fact that a full-scale sine measures ~-3.01 LUFS (this implementation:
-3.05) and that halving amplitude drops it ~6 LU (measured: 6.02).

**The target.** Run over the six default SID-emulated effects
(`audio.sfx.EFFECTS`): heartbeat -28.3, grille -27.2, movement -17.2,
tracker_alarm -24.8, airlock -19.6, attack_alert -10.4 LUFS — an 18 LU
spread *by design* (an alarm is supposed to be louder than an ambient
blip), so no single number is strictly "correct." `constants.
SOUND_TARGET_LUFS = -22.0` sits at the measured mean/median;
`SOUND_LUFS_TOLERANCE = 12.0` encloses the full measured range with a
little margin either side. Coincidentally close to the owner's own opening
guess of -23 LUFS, from before anything was measured.

**The check, not a fix.** Per the owner's own choice among the options
offered: measure and document a target, plus a check that flags out-of-spec
files — no runtime gain/normalization is applied to anything. `SamplePlayer.
loudness_report()` reads each found recording directly via the stdlib `wave`
module (not through a loaded `pygame.mixer.Sound`, so the measurement is of
the file as authored, not of whatever the mixer resampled it to) and reports
cue/path/LUFS/in-spec per file, silently skipping anything `wave` cannot
open.

**Surfaced in two places, computed once.** `__main__.py` runs the report
once at startup (the same pass that already builds the "sounds: N
recording(s) loaded" boot note) and `report.warn()`s any out-of-spec file by
name; the same computed list is handed straight to the developer overlay
(`gui._dbg_audio_spec`) rather than let it recompute the same thing lazily
on first draw. That "handed, not recomputed" design is load-bearing:
K-weighting a real multi-second recording in a plain Python loop (no
`scipy.signal.lfilter`, not a dependency) is not free, and the first attempt
— computing it lazily inside `_debug_audio_spec_line()` on first call —
pushed `test_the_overlay_costs_almost_nothing_per_frame`'s per-frame budget
from ~0 ms to 0.71 ms, caught immediately by that test. The developer
overlay's own line (`"audio spec  N/M ok"`, `_debug_lines`) is `None`
(simply omitted) when nothing has been computed yet - a bare
`PygameRenderer()` in a test never goes through `__main__.py`'s startup and
correctly has nothing to show.

**`sampled` -> `enhanced`.** The old name only ever meant "play recordings
instead of the synth"; it now also means "run the spec check" and "this is
where new audio files go" (the owner's own "SOUND stays a separate option"
choice keeps the *interface-blip* toggle independent — this rename is
`game_audio` only). `settings.py`'s `VERSION` bumped 2 -> 3, and `sampled`
was folded into the existing `_V1_VALUES` migration table (safe as a plain
substitution regardless of source version, since the word carried one
meaning throughout, unlike `death`'s `random`, which is why that table
needs versioning rather than a flat alias map in the first place).

**Action:** shipped - `audio/loudness.py` (new), `audio/samples.py`
(`LoudnessEntry`, `loudness_report`), `core/constants.py`
(`SOUND_TARGET_LUFS`, `SOUND_LUFS_TOLERANCE`), `__main__.py` (boot-report
warnings + `--game-audio` choices/help + the `gui._dbg_audio_spec` handoff),
`core/options.py` (`game_audio` values/help/`PROFILES`), `settings.py`
(`VERSION` 3, migration table), `render/pygame_app.py`/`render/audio.py`
(the `"sampled"` -> `"enhanced"` string checks), `render/debug_overlay.py`
(`_debug_audio_spec_line`, reads-not-computes). `todo.md`'s audio item
closed out. 14 new tests (`tests/test_audio_loudness.py`: pure loudness
math, `loudness_report` on synthetic files; `tests/test_options_screen.py`:
the v2->v3 migration) plus updates to `tests/test_sampled_audio.py`'s value
strings. Full suite passed, mypy clean.

## DISC-318 - "back"/"Skip turn" get their own row colours; "is there enough room"

**Found:** 2026-09-05, the same conversation as DISC-316/317, on the panel's
own visual design: "make the end turn [Skip turn] text all bold and appear
in a different color background directly about[above] the Back button.
Change the Back button to white test[text] on a red background."

`_draw_menu_panel` (`render/play.py`) now gives two entries fixed colours of
their own, overriding whatever band their row inherited: `entry.back` ->
white on red, `entry.skip_turn` -> the game's own ink colour on cyan, with a
faux-bold second blit one pixel right (there is no bold variant of either
font this renderer draws with, so a classic bitmap double-strike stands in
for it). Both stay swap-on-highlight, same as every other row.

**Caught by `test_every_panel_row_carries_its_own_tables_band_colour`:** the
INDICATE LOCATION list's own "back" row (`INDICATE_LABEL_QUIT`) lands on a
row number that changes with the page, and that row is checked against a
*live capture* of the real colour RAM — a decoded fact the override must
not paint over. The fix scopes the override off (`not self._menu.
indicating`), so the crew panel and the GET ITEM submenu (neither locked by
a captured-colour test) get the new colours and the INDICATE screen keeps
its real one.

**"Is there enough room" — answered, not engineered around.** The SPECIAL
band is only 4 rows (`PANEL_SLOT_SPECIAL_FIRST/LAST` = 14-17), already
shared by every context-sensitive special (GET JONES, BLOWLOCK.1/.2,
SEALLOCK.1/.2, ENTER HYPERSLEEP, LAUNCH NARCISSUS, OVERRIDE DETONATION,
FIGHT FIRE) — a real, pre-existing ROM-derived limit, not something this
session invented. "Skip turn" competes for one of those four slots exactly
like any other special would, and can overflow (silently dropped, `_panel_
rows` returns `None`) in the rare case all four are already in play at
once. Left as-is per the owner's own placement request rather than carving
out a dedicated fixed row, which the panel's already-full 19-row budget
(DISC-232) has no spare slot for anyway.

**Action:** shipped - `render/play.py` (`_draw_menu_panel`'s per-entry
colour override). 4 new tests in `tests/test_remake_pygame_input.py` (back
row red, skip-turn row cyan when turns is on, the row absent when turns is
off, the INDICATE screen's own back row keeps its captured colour). Full
suite passed, mypy clean.

## DISC-319 - P9-B goal session: ROOM_DAMAGE_ALIEN_PER_ACTION cadence live-confirmed, ALIEN_MOVE_TICKS's own "bounding, not a rate" caveat closed

**Found:** 2026-09-05, working the `/goal` set to answer todo.md's open
playtest-verification questions via the disassembly + the c64-live-oracle
VICE MCP.

**The capture.** 600s idle (no player input at all, matching DISC-306/307's
own proven methodology), sampling `$7935` (8 bytes: Alien room + 7 crew
rooms), `$653F` (36 bytes: the whole room-damage array, not just the Alien's
current room — DISC-307's own fix for undercounting), and `$7D45` (8 bytes:
health) once a second. Scripts kept as permanent artifacts alongside the
other one-off VICE captures: `Archive/vice-mcp/p9b_helpers.py`,
`p9b_boot_to_play.py` (a trimmed, resumable `boot_to_play.py` that does not
re-`vice_autostart` an already-running session), `p9b_capture.py`.

**Finding 1 — the corrode mechanism has no gap, live-confirmed.** 13 corrode
events observed (damage array total 9 -> 22 over the run). **All 13, with
zero exceptions, landed on a sample where the Alien's own room had not
changed since the previous sample; zero landed on a room-change sample.**
This is an exact, live match to the disassembly's own gated mechanism
(`guard_6562`/`$8EBD`, PV-14/D-179, D-288: fires only when `$6563` is set —
the Alien sitting at its destination, not moving into it) — not merely
consistent with it, a positive confirmation with no counter-example in this
run. `constants.py`'s `ROOM_DAMAGE_ALIEN_PER_ACTION` comment updated with
this; the residual **rate gap** (DISC-306/307/308's converged ~1.4x, disk
0.286-0.296 vs remake ~0.41 damage per surface room-change) is untouched —
that is P-9's own still-open question, explicitly not re-attempted here per
the goal's own instruction not to repeat a capture of that kind.

**Finding 2 — `ALIEN_MOVE_TICKS=60`'s own live-validation gap, closed.**
`constants.py` carried a stale `[?]`: an FV-2 live observation (2026-07-11)
watched the Alien for only 50 continuous seconds and saw no movement at all —
"a bounding data point, not a rate... a clean rate calibration needs a much
longer (multi-minute) observation window." This capture is that window.
Within a single sustained room-linger (the Alien re-deciding "stay"
repeatedly — e.g. room 5: corrode events at t=93.4, 101.7, 109.1, 116.4,
123.8s; room 34: 225.8, 233.2s, then 275.1, 282.4s), successive corrode
events landed **~7-8s apart** — matching `ALIEN_MOVE_TICKS=60` at the
measured real-hardware rate (`MAIN_LOOP_HZ` ~7.886 Hz) almost exactly:
60/7.886 ≈ 7.61s predicted. The 60-tick timer is now live-confirmed, not
just decoded (D-038's own byte-level trace).

**Finding 3 — the crew-health "anomaly" DISC-308 flagged was never one.**
DISC-308 read `$7D45 = [0, 6, 5, 4, 1, 0, 1, 1]` and flagged two values (6,
5) as "outside the 0-4 range this project's own decoded `CREW_START_HEALTH`
model expects." That comparison used the wrong constant: `CREW_START_HEALTH
= 4` is explicitly documented as "default full health (**fallback**; real is
per-crew)" — the real per-crew table, `crew.START_HEALTH = (6, 5, 4, 5, 4, 6,
5)` (`[C $7D4D]`, ROSTER order Dallas/Kane/Ripley/Ash/Lambert/Parker/Brett),
already allows up to **6**. DISC-308's own reading maps perfectly onto it:
Dallas=6 (full), Kane=5 (full), Ripley=4 (full), Ash=1 (wounded, from 5),
Lambert=0 (the run's opening-death victim, from 4), Parker=1 (from 6),
Brett=1 (from 5). No anomaly, no decode error — a comparison against a
constant whose own comment says not to use it this way. This session's own
capture cross-checks it again: health never changed across the full 600s
(`[0, 6, 5, 4, 5, 0, 6, 5]` start and end, Lambert the fixed opening-death
victim at 0 throughout), consistent with everyone else surviving the whole
run untouched.

**Also fixed, found while reading around these: four stale `[?]`/placeholder
comments that were never updated when the question they described had
already closed** (the exact "prose mentions of a marker that was since
resolved" pattern `todo.md`'s own 2026-08-29 audit warned about, just missed
by that audit itself):
* `crew.py`'s module docstring and `START_FEAR`'s own comment both still said
  the morale-word 5-way banding was a `[?]` guess and that fear gated order
  *obedience* — both wrong. `morale_word`/`fear_band ($7DC5)` was fully
  decoded and live-confirmed by D-024/FV-2g (2026-07-11); `core.orders`'s own
  module docstring has said since D-018/D-026 that there is no compliance
  roll on the order path at all.
* `menu.py`'s `MOVE_TO_LIMIT = 8` — dead code, referenced nowhere else in the
  module. D-167 (2026-08-07) already settled PV-02: "`MOVE_TO_LIMIT = 8` was
  a bound with no ROM backing. The true limit is 1-5 entries on the surface
  ... and up to 4 in a duct," and `crew_entries`'s actual destination-building
  code (`_reachable_move_targets`/`duct_exits`) already implements exactly
  that with no reference to this constant. Removed rather than left as an
  unused, misleading relic.
* `pygame_app.py`'s `_ALIEN_SPRITE_FRAMES` carried "colour below is kept as
  the pre-R-05 placeholder red, still `[?]`" directly under a colour constant
  that is `[C $4E8E]`-cited green (D-170) and a frame table cited as
  `tbl_alien_anim`'s own decoded 12-byte sequence (R-05). Nothing below it
  was ever a placeholder by the time this comment was written; removed.

**Action:** shipped - `core/constants.py` (both comments rewritten),
`core/crew.py` (module docstring + `START_FEAR` comment corrected),
`core/menu.py` (`MOVE_TO_LIMIT` removed), `render/pygame_app.py`
(`_ALIEN_SPRITE_FRAMES` comment corrected). `todo.md`'s `[?]` list items 1-3
(and the morale/move-to-limit/sprite-colour sub-items of item 5) checked off
with this entry cited. Full suite passed, mypy clean (no behaviour changed —
every fix here was comment/dead-code only).

## DISC-320 - P9-B goal session: 3 deliberately-timed idle-survival trials, and the remake's own gap

**Found:** 2026-09-05, working the `/goal`'s item 2: "does an undefended crew
die too slowly in the remake?" DISC-302 (one idle sample) and DISC-308
(another) disagreed - 185s to "ALL CREW LOST" against 1,200s+ still mostly
alive - and todo.md's own instruction was explicit: this needs *several
deliberately timed* trials, not more incidental readings from a capture
aimed at something else.

**Method.** Three fresh trials, each a cold reboot (`vice_autostart`) to a
clean game, then zero player input, sampling `$7D45` (health) once a second
until either all 7 crew read 0 or a 400s cutoff. Script kept as a permanent
artifact: `Archive/vice-mcp/p9b_survival_trials.py`.

**Result: 0 of 3 wiped out within 400s.**

* Trial 1 - survived to cutoff, `[0, 5, 4, 5, 4, 6, 5]` (only the
  opening-death victim at 0; everyone else untouched).
* Trial 2 - survived to cutoff, identical pattern.
* Trial 3 - survived to cutoff, `[0, 5, 4, 1, 1, 1, 5]` (three crew down to
  critical health from encounters, but none actually at 0 beyond the fixed
  opening-death victim).

**Combined with the two existing incidental samples, the picture is now 4
survivals-past-several-minutes against 1 fast death (DISC-302's 185s).** That
is not "the remake's crew are too safe" being vindicated, and it is not
DISC-302 being debunked either - a single fast-death sample sitting in an
otherwise slow-death distribution is exactly what a low-probability event
looks like with n=5. What it does settle: **idle death within ~200s is the
uncommon outcome on the disk, not the typical one** - DISC-302's own number
should not be read as "the disk kills an idle crew in three minutes," which
is how it could have been (mis)read on its own.

**The remake's own gap is now more precisely stated.** The existing
comparison (6,000 ticks across 8 seeds, `Simulation.advance()` in a bare
loop, DISC-302) found the remake **never** ends a game from pure neglect -
0/8. The disk has now been sampled 5 times and has done it once. Whether
that is a real fidelity gap (the remake structurally cannot produce a fast
idle death the disk's own mechanics can) or just means the remake's own 8
seeds did not happen to roll the disk's own rare path is not resolved by
this session - it would take either many more disk trials to pin the true
rate, or tracing the actual death mechanism (which stressor accumulates
enough to kill *without* an order ever being given - likely the
Alien-encounter wound path landing on the same undefended, wandering-or-
stationary crew member repeatedly) to check the remake implements the same
sequence at all. Left open rather than guessed at.

**Action:** shipped - `Archive/vice-mcp/p9b_survival_trials.py` (new,
permanent artifact). `todo.md`'s item 2 updated with the 3 new data points
and the sharpened remaining question (is 0/8 a real gap, or n=8 too small to
catch a rare disk-side event). Not closed - genuinely needs either more
trials or a mechanism trace to go further, and this session's own time
budget stops here.

## DISC-321 - P9-B goal session: the tracker alarm, live-confirmed on real SID registers

**Found:** 2026-09-05, working the `/goal`'s item 4: "sfx_blip_b identity -
don't just listen: trigger the tracker alarm on the real disk and read the
SID registers VICE exposes, compare the waveform/frequency against the
modeled version."

**Starting point: this was already closed by disassembly (D-178/PV-24,
2026-08-07), just not reflected in `audio/sfx.py`'s own docstring.** `sfx_blip_b`
is not the tracker's sound at all - it is one of the two one-shot
grille/movement blips `reset_attack_state` selects between. The real
tracker alarm is a **re-gated voice-3 pulse train**: `$4DF5`/`$4DFF` set
voice 3's resting frequency/AD, `$65CB`'s divider (`$12`) and the
`$4DD7`-`$4DEA` IRQ re-gate it on each wrap, `$8DF6`'s `LDA #$21` arms it,
`$8C82` silences it, and `$43CB` fires the identical `#$21` write under the
caption "THE TRACKER ALARM." on the game's own sound-legend screen — the
game names its own sound. `sfx.py` already implements this correctly and
separately from the blips (`"tracker_alarm"` in `EFFECTS`, via
`render_pulse`); the module's own "Not modelled" section just still framed
`sfx_blip_b` as an open `[?]` candidate for it. Fixed this session.

**Live confirmation, this session.** Booted a fresh game (`Archive/vice-mcp/
p9b_boot_to_play.py`), navigated the real CONTROL panel by joystick
(`vice_joystick_set`, not `vice_joystick_tap` - taps were too brief to
register against the game's own input poll; `set` + a ~0.25s hold + release
worked reliably, confirmed by watching the panel cursor byte `$64E5` change),
picked up the CommdCentr Tracker with Ripley (`data.ITEMS` entry 6, matching
the decoded item-placement table), and USEd it. Read SID voice 3's control
register (`$D412`) once every 0.2s for three minutes:

* **While the Alien was in room 6 (co-located with the tracker's zone),
  `$D412` read a sustained `0x20` (sawtooth waveform selected) across 323
  consecutive samples spanning ~13 real seconds** - the gate bit toggling
  too fast for 0.2s polling to catch consistently, exactly the "re-gated
  pulse train" shape the disassembly describes rather than a single steady
  tone.
* **The moment the Alien's room changed (to 8, then 21), the armed readings
  stopped** - the alarm clears as the Alien leaves proximity, matching
  `_tracker_detects`'s own zone-gated model in `sim/orders.py`.
* Voice 3's frequency (`$D40F`) read `0x32` throughout, at rest and while
  armed - exactly `TRACKER_VOICE_SETUP`'s predicted `~752 Hz`, unchanged by
  arming (only the control register moves).

This is a positive, real-hardware match on both the waveform selection and
the frequency, plus a live demonstration of the zone-gating behaviour - not
just a citation, an actual SID register read while the alarm was sounding.

**Method note for later captures:** `vice_joystick_tap` did not reliably
register short presses against this game's own input poll in this session;
`vice_joystick_set` with an explicit ~0.25s hold before returning to
`center` did, verified by watching `$64E5` (the panel cursor) change with
each press rather than assuming it worked.

**Action:** shipped - `audio/sfx.py`'s "Not modelled" section rewritten to
state PV-24/D-178's closure plainly rather than as an open `[?]`. No `src/`
behaviour changed (the correct implementation already existed). `todo.md`'s
item 6 (`sfx_blip_b`) checked off.

## DISC-322 - P9-B goal session: `_ROOM_GLYPH`'s duct-view note was also stale

**Found:** 2026-09-05, closing out the goal's last remaining sub-item.
`render/play.py`'s `_ROOM_GLYPH` comment read "the duct view is a separate
question and is still open" after its surface half closed on 2026-08-29.

**Not actually open.** `_draw_duct_map` never touches `_ROOM_GLYPH` — it
paints from `data.DUCT_MAP_ROOM_TEMPLATE`, a real per-room table decoded
straight from the disassembly. D-091 found the three duct-map screen
templates (`select_menu_template $817D`); D-092 decoded them completely —
ten glyphs, the RLE unpacker, the room-node glyph, the pipe-follower tracer,
the "only your own node + the runs leading away are lit" colouring — and is
explicit that this took **no live capture at all**, cross-checked four
independent ways (all 34 room positions land on the node glyph; each sheet's
node count matches its room-assignment table `$7569`; etc). There was never
a comparable open question here; the comment just predated reconciling with
D-091/D-092's own later, complete decode.

**Action:** shipped - `render/play.py`'s `_ROOM_GLYPH` comment corrected.
`todo.md`'s item 5 now fully closed. This completes every sub-item of the
`/goal`'s item 5 ("the remaining cosmetic `[?]`s"). Full suite passed, mypy
clean (comment-only change).

## DISC-323 - the crew-survival gap is probably sample-size noise, not a mechanism gap

**Found:** 2026-09-05, following up DISC-320's own open question ("is 0/8
remake seeds ending from neglect a real gap, or n=8 too small to catch a
rare disk-side event") by reading the wound mechanism itself rather than
running more trials.

**The wound path is completely unconditional on player orders.**
`_resolve_encounter`'s victim-wounding code (`core/alien.py`, `[C
$4152-$41F7]`) only checks: alive, co-located with the Alien, not in a duct,
health above the incapacitation floor. Nothing on this path looks at
whether the victim has ever been given an order, is currently selected, or
is doing anything at all - an idle, never-touched crew member is exactly as
woundable as one being actively played. The gates, the miss rate (7/16 =
`ALIEN_ATTACK_ROLL_AT_LEAST`/`ALIEN_ROLL_SIDES`), the up-to-3-candidate
victim selection (`ALIEN_VICTIM_SLOTS`), and the wound amount
(`ALIEN_WOUND_AMOUNT = 1`) are all `[C]`-cited, decoded constants the remake
already implements exactly as the disk does.

**The likely explanation is a short/small comparison on both sides, not a
missing mechanism.** DISC-302's disk death was at ~185s; DISC-308 and this
session's own 3 trials all survived past 400-1,200s+ - the disk's own idle
death is evidently a rare-ish event that needs several minutes and several
attempts to reliably observe. The existing remake comparison (8 seeds,
6,000 ticks) is only ~761 real-equivalent seconds at the measured tick rate
(6000/7.886 Hz) - comparable to or shorter than the window the disk itself
needed to show its one death in five tries. An identical mechanism can
easily produce "0 of 8" and "1 of 5" from the same underlying rare-event
rate; that difference does not need a code-level gap to explain it.

**Revised conclusion for `todo.md`'s item 2:** the mechanism check is
conclusive - there is no structural reason the remake couldn't reproduce
the disk's idle-death path, since the code already runs the same
unconditional wound roll the disk does. What remains genuinely unmeasured
is the *rate* (how many minutes, on average, before an idle crew is wiped),
on both sides - which needs many more trials of both to pin down, not a
code fix. Downgraded from "possible fidelity gap" to "an open rate
question with no evidence of a mechanism difference."

**Action:** no `src/` change - this is a reading of already-correct code.
`todo.md`'s item 2 updated to reflect the mechanism check.

## DISC-324 - `screen_fx` turned on by default under OUIJAGHOST

**Found:** 2026-09-06, owner's request: "default for ouijaghost mode is to
have the SCreen FX on."

`screen_fx` (DISC-311/313/314) had been left `off` under both presets like
`turns` — but unlike `turns` (a pacing overhaul with real gameplay
consequences, opt-in regardless of preset by design), `screen_fx` is purely
cosmetic on one screen (the boot report) with the same "off under ORIGINAL"
guarantee any other OUIJAGHOST-only flourish gets. `PROFILES["ouijaghost"]`
now sets it `"on"`; `PROFILES["original"]` is unchanged (`"off"`).

**Action:** shipped - `core/options.py` (`PROFILES["ouijaghost"]["screen_fx"]
= "on"`). No new tests needed — `test_the_other_profile_actually_differs`
and `test_a_new_option_cannot_skip_this_check` (both generic, not hardcoded
to this key) already cover a preset-value change of this shape. Full suite
passed, mypy clean.

## DISC-325 - P-9 closed by calibration, not mechanism - a live-oracle session blocked on input injection

**Found:** 2026-09-07, a follow-up goal specifically asking to either pin the
P-9 gap's mechanism with one more live session, or - if that session couldn't
resolve it - stop re-measuring and calibrate directly against the numbers
already trusted (DISC-306/307).

**The live session did not reach the game.** A fresh headless VICE instance
(this one deliberately isolated onto its own port and with the legacy text/
binary monitors explicitly disabled, `+remotemonitor +binarymonitor`, since
the owner was running a second, unrelated VICE instance at the same time) got
through the ShareData notice, the WELCOME menu, and the instructions prompt
fine — `vice_keyboard_type`/`vice_keyboard_key_press` worked on all three.
The crew-selection screen ("GAME SELECTION: Control:1 Full Game / Control:2
Short Scenario") never responded to any input method tried: `keyboard_type`,
held `key_press`/`key_release`, and `vice_joystick_tap` all left zero-page
`$91` (traced via disassembly at the wait loop, `$5F36 LDA $91 / CMP #$FA /
BNE $5F47 ... CMP #$F3 / BNE $5F36`) stuck at `$FF` — idle — however the key
was sent. This reads as an input-injection fault in that particular MCP
server session (not reproduced against a from-scratch install, and not
something this project's own code could be at fault for, since `$91` is
read-only from the game's perspective), not a game bug. Given the owner's
own instruction for exactly this outcome, the session was not extended
further chasing it.

**Static re-check first, before calibrating blind.** With the live path
closed, checked whether an incomplete route table (`_route_dest` falling
back to `_compass_dest`'s approximation for some rooms) could explain a
consistent ~1.4x gap on its own: `_route_dest` only returns `None` (forcing
the compass fallback) for a room absent from `_SLUG_TO_INDEX`, a route table
shorter than the room count, or a destination not present on the ship map —
none of which apply to the real 34-room Nostromo with its full decoded
`ALIEN_ROUTES` tables. So every surface move on the real ship already uses
the real, decoded route tables; the compass approximation is dead code on
the real ship and cannot be the source of the gap. Ruled out without needing
the emulator.

**Decision: calibrate the base rate, per the owner's own instruction.**
`ROOM_DAMAGE_ALIEN_PER_ACTION = 1` (magnitude, DISC-288) and `guard_6562`'s
three-gate condition (DISC-319: 13/13 observed corrode events landed on a
no-room-change sample, zero exceptions) are both independently confirmed
correct — the ROM's own literal reading is therefore "corrode every single
eligible action," rate 1.0. Yet across every measurement in this thread the
remake ran ~1.4x hotter than the disk regardless (remake ~0.41 vs. disk
0.286-0.296 damage per surface room-change, DISC-306/307's own two
agreeing captures). With the mechanism now confirmed correct from every
angle that could be checked without the emulator, and the emulator itself
unavailable, the remaining gap cannot be a code bug still to find — it is
either genuine hardware/timing noise the static model cannot see, or
something a future live session might still explain. Per the owner: rather
than leave it open indefinitely, `ALIEN_CORRODE_RATE = 0.71` (the trusted
disk range's midpoint, 0.291, divided by the remake's own measured 0.41)
scales ambient corrosion down to match, applied under **ORIGINAL** — this
is a fidelity correction to the base rate, not an added rule, so both
presets get the corrected rate (UPDATED's own DEC-044 throttle stacks
independently on top, unchanged - see DEC-046).

**Action:** shipped - `core/alien.py` (`Alien.corrode_credit`, a
Bresenham-style fractional accumulator replacing DEC-044's integer
`corrode_action_count`/`corrode_every` so both a sub-1.0 base rate and
UPDATED's own further throttle are expressed the same way; `advance_alien`/
`_resolve_surface_action` take `corrode_rate: float` in place of
`corrode_every: int`), `core/constants.py` (`ALIEN_CORRODE_RATE = 0.71`,
`UPDATED_ALIEN_CORRODE_RATE = 1/6`, numerically identical to DEC-044's old
"every 6th action" so its own already-swept numbers needed no re-tuning -
confirmed by re-running `tools/winnability_sweep.py` both ways: 6/16 real-time
and 5/16 turn-based, unchanged from before this change). Two pre-existing
unit tests (`test_the_alien_corrodes_the_room_it_occupies`,
`test_a_hunting_alien_does_not_corrode_the_ship`) moved from `_line_ship`'s
4-room chain to a new single-room `_isolated_room_ship` fixture, since a
constant-roll Alien on the old ship produced exactly one corrode-eligible
action total (fine at rate 1.0, never enough at rate 0.71 to cross the new
accumulator's threshold) rather than the many the tests actually need. Full
suite passed, mypy clean. See DECISIONS.md's DEC-046 for the full reasoning
and the alternatives considered.

## DISC-326 - GAME_SELECTION's cursor was invented once, removed, then reintroduced - UPDATED only

**Found:** 2026-09-13, owner's request for a Steam Deck / gamepad-only
workflow: *"Can the first menu support a highlight bar when played on the
Steamdeck? So if there is only a Joystick or the mouse and no keyboard, the
player can still highlight and select a choice hitting the A key?"*

**This screen already had this once, and it was removed on purpose.**
D-018 (live-confirmed): `$5F36` polls the keyboard latch `$91` for the
literal Ctrl+1/Ctrl+2 chord and nothing else - no cursor, no ">" marker, no
fire-select, on the real disk. An earlier pass had built exactly the
up/down/fire cursor the owner was now asking for, found via live capture
that it did not match the ROM, and deleted it (FV-1c1 found the gap in
chord enforcement, FV-1c2 closed it). `flow._on_selection`'s own docstring
has carried a comment about this removal ever since.

**Put to the owner before touching it again, given that history**, and
resolved as DEC-047: reintroduced, but gated to UPDATED only via the same
`is_original(...)` test `options.pointer_allowed` already uses for the
mouse. A follow-up question - should ORIGINAL get the same exception
specifically on a Deck, since there is no keyboard to press the chord on at
all - was also asked and **declined by the owner**, citing the standing
ruling on the mouse (DEC-039-era: "ORIGINAL means the original machine too
... a mouse is an addition like any other"). The documented answer for
ORIGINAL on a Deck is a Steam Input controller remap sending the literal
Ctrl+1/Ctrl+2 chord - satisfying the real decoded requirement, not routing
around it.

**Action:** shipped - `core/flow.py` (`GameFlow.selection_row`,
`_on_selection`'s new UP/DOWN/FIRE branches, gated on `not
is_original(...)`), `render/frontend.py` (`_draw_selection` draws the
cursor through the same paper/ink highlight the screen's existing
mouse-hover already used - no new visual language). Two new tests in
`tests/test_remake_flow.py` (the cursor moves and wraps, fire resolves to
whichever row it is on); the pre-existing `test_selection_is_ctrl_1_ctrl_2_
only` had to start asking for ORIGINAL explicitly rather than trust the
constructor's own non-ORIGINAL defaults. Full suite passed, mypy clean.
See DECISIONS.md's DEC-047 for the full reasoning and the alternatives
considered.
