"""Screen composition decoded from the ROM: layout, colours, strings.

Headless by construction — nothing here imports pygame, so the decoded tables
are readable and testable without a display. ``render/`` imports this package;
never the reverse.
"""

from __future__ import annotations
