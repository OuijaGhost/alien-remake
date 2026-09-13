# Undocumented subroutines — none remain (2026-08-08)

`UNDOCUMENTED.json` is the census of `ALIEN.prg` subroutines that the
disassembly reaches but nobody has explained. **It is now empty.**

It last held three entries, all of which turned out to be already understood —
the file had simply not been refreshed after the work that closed them. Recorded
here so the next reader does not re-derive them:

| routine | callers | what it is |
|---|---|---|
| `$604F sub_604f` | 1 (`$5F4E`) | **The SHORT-game scenario preset.** Reached only on the Ctrl+2 branch. Pins `$64C3` (the android) to slot 4 and `$64C2` (the opening victim) to slot 2, puts slots 1 and 7 in the ducts (`$6502`/`$6508` = 1), moves three items to room 6 (`$82EA`/`$82F3`/`$82F4`), then copies four 7-byte tables from `$608C`/`$6093`/`$609A`/`$60A1` over the live crew locations (`$7936`), health (`$7D46`), composure (`$7D56`) and its mirror (`$6572`). Two of the health bytes are **0**, so SHORT starts with crew already dead. Decoded into `gamedata_snapshot.SHORT_SCENARIO`, `SHORT_ANDROID_SLOT`, `SHORT_VICTIM_SLOT`, `SHORT_DUCT_SLOTS` and `SHORT_ITEM_MOVES`, and applied by `sim.py`. |
| `$7520 sub_7520` | 15 | **Colour-RAM row fill.** `JSR set_color_ptr_row` (which walks `$FD/$FE` from `$D81E` down by `$64E5` rows), then writes the colour in `$64E4` across 10 bytes — the CONTROL panel's per-row colour band. Its sibling `$7530 fill10_via_fd` is the same loop hardcoded to colour 1. |
| `$755E delay_routine` | 1 | **The main loop's busy-wait**, `LDY #$AA` around an inner X loop ≈ 110,600 cycles. It is the basis of the whole timing model — see DISCOVERIES `$755E` / `main_loop ($719D)`, which derive `MAIN_LOOP_HZ = 7.886`. |

**So every subroutine the code map reaches is accounted for.** That is a
statement about *coverage*, not about correctness: see `FAITHFULNESS.md` for the
per-module provenance ledger, which is where "does the remake behave like the
original?" is actually answered.
