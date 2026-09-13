"""Skip a test when the material it needs was never derived on this machine.

The repository ships no game data, so a fresh clone has no disk image, no
extracted `ALIEN.prg` and no character set until the owner runs
`--derive-assets` on their own copy. Tests that read those must **skip**, not
fail: a cold clone reporting two dozen failures reads as a broken project rather
than as an install step not yet taken.
"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

#: The user's own disk image, and the artefacts derived from it.
NIB = REPO / "Alien (USA, Europe).nib"
ALIEN_PRG = REPO / "out" / "Alien (USA, Europe)_files" / "ALIEN.prg"
CHARSET = REPO / "out" / "charset.bin"
#: Live captures from the emulator. Never published (see .gitignore).
REFERENCE = REPO / "archive" / "reference"


def need(*paths: Path) -> None:
    """Skip unless every path exists, naming what to run."""
    for path in paths:
        if not path.exists():
            pytest.skip(
                f"{path.name} not present - run --derive-assets against your own "
                f"disk image first (see docs/INSTALL.md)"
            )
