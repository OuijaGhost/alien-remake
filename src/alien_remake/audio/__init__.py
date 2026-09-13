"""The intro-tune audio pipeline.

Three layers, each independently testable:

- :mod:`.mos6502` — a minimal NMOS 6502 CPU emulator (legal opcodes only,
  fail-loud on anything else), built on the disassembler's opcode table.
- :mod:`.sid` — an approximate software MOS 6581 (SID) synthesizer that turns a
  stream of register writes into PCM samples.
- :mod:`.intro` — the driver: loads the real ``ALIEN.prg``, runs the game's own
  init + IRQ-driven music player under emulation, captures every ``$D400–$D418``
  write, and renders the *actual* intro tune to ``out/intro.wav``
  (DECISIONS D-010 #3: the tune is emulated from the real code, not
  re-transcribed).

Everything here is stdlib-only (plus the project's own ``alientools`` opcode
table); pygame is not imported.
"""
