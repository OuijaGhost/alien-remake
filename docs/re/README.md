# Reverse engineering `ALIEN.prg`

Everything known about the 1984 program, and how it was found out. The remake in
`src/alien_remake/` is written from these documents; when the two disagree, the
disassembly wins.

**None of it contains the game.** These are notes, tables and commentary about a
program you supply yourself. Regenerate the machine-produced parts from your own
disk with `python -m alientools codemap --out docs/re/ALIEN.annotated.asm`.

## Where to start

| you want to… | read |
|---|---|
| understand how the program is put together | [DISASSEMBLY.md](DISASSEMBLY.md) |
| know what lives at an address | [MEMORY_MAP.md](MEMORY_MAP.md) |
| find the map, item, crew or timing tables | [GAMEDATA.md](GAMEDATA.md) |
| check whether a remake behaviour is real | [FAITHFULNESS.md](FAITHFULNESS.md) |
| know *why* something is the way it is | [DISCOVERIES.md](DISCOVERIES.md) |
| read the code itself | [ALIEN.annotated.asm](ALIEN.annotated.asm) |

## The files

**[DISCOVERIES.md](DISCOVERIES.md)** — the evidence log, 264 numbered entries.
Every non-obvious line in the remake cites one (`Derivation: DISCOVERIES
DISC-229`), so this is where "why is this number 14?" is answered. It also
records the wrong answers, on purpose: several cost days to disprove and would
otherwise be re-derived. Append with a new `DISC-NNN`, then run
`python tools/reindex_discoveries.py` — a test fails until the index matches.

**[DISASSEMBLY.md](DISASSEMBLY.md)** — how the program is organised: the loader
chain, the IRQ, the main loop and its 7.886 Hz clock, and the routine-by-routine
walk through the code.

**[MEMORY_MAP.md](MEMORY_MAP.md)** — what every known address holds. The single
most useful file when reading the listing: the game keeps parallel arrays per
character (`$7935` locations, `$7D45` health, `$7D55` composure), and this is
where their layouts are written down.

**[GAMEDATA.md](GAMEDATA.md)** — the decoded tables: rooms, doors, ducts, items,
crew, and the per-character timing tables. `python -m alientools gamedata`
re-derives them from your disk, and `--emit-python` regenerates the remake's
`gamedata_snapshot.py`.

**[FAITHFULNESS.md](FAITHFULNESS.md)** — the provenance ledger. Every claim in
the remake is `[C $addr]` (traced to a routine) or `[?]` (flagged as
uncalibrated). Nothing is `[INVENTED]`, and a test fails if that ever changes.
Currently 420 citations over 1,155 addresses, and 40 open `[?]`.

**[VICE_CHECKS.md](VICE_CHECKS.md)** — how to settle a `[?]` against the running
game in an emulator: watchpoints, procedure, pitfalls. Its checkboxes are stale
(everything in them was answered, mostly by static trace); the instructions are
not.

**[UNDOCUMENTED.md](UNDOCUMENTED.md)** — subroutines the code map reaches that
nobody has explained. **Empty**: every one is accounted for. That is a coverage
statement, not a correctness one.

**[ALIEN.annotated.asm](ALIEN.annotated.asm)** / **[alien.sym](alien.sym)** —
the full listing with every byte classified as code or data, and the symbol file
for VICE. Both are generated; do not hand-edit them.

## How the classification works

A linear sweep of 6502 code mis-decodes the first data table it meets and never
recovers. `alientools codemap` instead follows control flow from the entry
points — the reset vector, the IRQ handler, every `JSR` and branch target — and
marks only what execution can actually reach. What is left over is data, and the
census proves it: **0 of 40,961 bytes unclassified**.

## The rule this project runs on

**The code is the truth; the manual is a hint.** The manual describes mechanics
the program does not implement, and omits several it does. Anything that cannot
be traced to a routine is marked `[?]` and left uncalibrated rather than guessed
into the remake — and where an earlier guess was disproved, the guess was
deleted, not annotated. `DISCOVERIES.md` keeps the corrections so nobody
re-derives them.
