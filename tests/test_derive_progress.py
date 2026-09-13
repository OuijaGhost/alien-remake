"""F-1's decision-free half: derivation as a generator, not just a CLI print.

The point is that a future first-run screen can drive this without a subprocess
and without scraping stdout. These tests exercise the generator directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.__main__ import DeriveStep, derive_assets_from

NIB = Path(__file__).resolve().parent.parent / "Alien (USA, Europe).nib"


def test_a_missing_disk_yields_a_failed_step(tmp_path: Path) -> None:
    """No exception a caller has to catch - a failed step, same as any other."""
    steps = list(derive_assets_from(tmp_path / "nope.nib"))
    assert steps, "yielded nothing at all for a missing image"
    assert not steps[0].ok


def test_derive_step_is_a_plain_named_tuple() -> None:
    """So a caller can pattern-match it without importing anything exotic."""
    step = DeriveStep("example", True)
    assert step.label == "example" and step.ok is True
    label, ok = step               # unpacks like a tuple
    assert (label, ok) == ("example", True)


@pytest.mark.skipif(not NIB.exists(), reason="no .nib in this checkout")
def test_deriving_from_the_real_disk_yields_five_ok_steps(tmp_path: Path) -> None:
    """End to end, against the real image, from a clean directory.

    Five stages: extract, chars, intro, sfx, BASIC listing. All report ok=True
    on a real disk - the listing step is best-effort but still ok even when it
    cannot run, by design (a first run must reach the game either way).
    """
    import os

    old_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        steps = list(derive_assets_from(NIB))
    finally:
        os.chdir(old_cwd)

    assert len(steps) == 5, [s.label for s in steps]
    assert all(s.ok for s in steps), steps
    assert (tmp_path / "out" / "charset.bin").exists()
    assert (tmp_path / "out" / "intro.wav").exists()


def test_the_cli_path_still_prints_and_returns_the_old_shape(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """The refactor must not change `--derive-assets`'s own behaviour."""
    from alien_remake.__main__ import _derive_assets

    rc = _derive_assets(str(tmp_path / "missing.nib"))
    assert rc == 2
    assert "no disk image found" in capsys.readouterr().err
