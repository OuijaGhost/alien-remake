"""Everything the suite reads out of `out/` is still there (O4).

The cleanup that emptied `out/` computed what to keep from **what the program
loads** — `assets.KNOWN_ASSETS` and the loader's own patterns. That is the
wrong question on its own. The `.d64` and the MENU1 listing are not loaded by
the game at all, but two tests open them directly, and moving them turned
passing tests into *skipped* ones: 1079 passed became 1077 passed, 2 skipped.

A skip is a quieter failure than a red test. It was caught by comparing counts
across runs, which is not a method. So this names the files the suite itself
depends on, and fails loudly if one goes missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake import assets

#: Files under `out/` that the **test suite** opens directly — not the game.
#: Each names the test that would otherwise skip in silence.
SUITE_INPUTS: tuple[tuple[str, str], ...] = (
    ("Alien (USA, Europe).d64", "test_diskimage.py::the assembled image"),
    ("MENU1_EXITO.bas.txt",
     "test_fv3_frontend_capture.py::the instructions-prompt colours"),
)


@pytest.mark.parametrize("name,used_by", SUITE_INPUTS)
def test_a_file_the_suite_reads_is_still_present(name: str, used_by: str) -> None:
    path = Path(assets.DERIVED_DIR) / name
    assert path.is_file(), (
        f"{name} is gone, so {used_by} will skip rather than fail. It is not "
        f"loaded by the game, which is exactly why a keep-set built from "
        f"`assets.KNOWN_ASSETS` will not protect it."
    )


def test_everything_the_game_loads_is_still_present() -> None:
    """The other half: the assets the program itself resolves.

    Two are legitimately absent on most machines (`basic.bin`, `chargen.bin`
    are captured from a real C64), so this asserts only that what *was* there
    has not been swept away by a tidy-up.
    """
    optional = {"basic_rom", "chargen"}
    for key, parts, why, _how in assets.KNOWN_ASSETS:
        if key in optional:
            continue
        assert assets.find(*parts) is not None, f"{'/'.join(parts)} - {why}"
