"""Rendering / input / audio backends for the Alien remake.

The core talks only to the :class:`~alien_remake.render.base.Renderer` protocol,
so backends are interchangeable: :class:`~alien_remake.render.base.NullRenderer`
(stdlib, headless) and the pygame backend in
:mod:`alien_remake.render.pygame_app` (the one optional third-party dependency).
``pygame_app`` is intentionally *not* imported here, so importing this package
never requires pygame.
"""

from __future__ import annotations
