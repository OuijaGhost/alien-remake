"""Smoke/skeleton tests: the package imports and the CLI is wired.

No disk parsing yet — these only exercise the machinery the Definition of Done
runs on every change.
"""

from __future__ import annotations

import pytest

import alientools
from alientools import cli


def test_package_imports_and_has_version() -> None:
    assert isinstance(alientools.__version__, str)
    assert alientools.__version__  # non-empty


def test_smoke_returns_zero_and_prints_ok(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["--smoke"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "smoke OK" in out
    assert alientools.__version__ in out


def test_no_args_prints_help_and_signals_usage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = cli.main([])
    assert rc == 2
    assert "usage" in capsys.readouterr().err.lower()


def test_version_flag_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    # argparse's version action raises SystemExit(0).
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert alientools.__version__ in capsys.readouterr().out
