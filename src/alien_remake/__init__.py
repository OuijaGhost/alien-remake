"""Faithful remake of the 1984 C64 game *Alien* (Part II).

Architecture (DECISIONS D-009):

- :mod:`alien_remake.core` — the game logic: a **headless, stdlib-only,
  fixed-tick state machine**. No rendering, no pygame, no wall-clock; fully
  unit-testable. Implements the model in ``docs/spec/GAME_SPEC.md``.
- :mod:`alien_remake.render` — rendering/input/audio behind the
  :class:`~alien_remake.render.base.Renderer` protocol. The **pygame** backend is
  the project's one optional third-party runtime dependency; the headless
  :class:`~alien_remake.render.base.NullRenderer` keeps the core runnable and
  testable without it.
- :mod:`alien_remake.runner` — bridges a :class:`~alien_remake.core.sim.Simulation`
  to a renderer with real-time pacing (the *only* place wall-clock timing lives,
  so the core stays deterministic).

The original game is real-time (~6.25 Hz PAL fixed tick; see GAME_SPEC §2 /
DISCOVERIES D-008), which is why the core is a fixed-tick simulation rather than
a turn loop.
"""

from __future__ import annotations

__version__ = "0.0.0"
