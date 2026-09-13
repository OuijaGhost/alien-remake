"""Shared test setup.

The one thing here is isolation from the machine the suite happens to run on.
"""

from __future__ import annotations

import pytest

from alien_remake import assets


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers",
        "real_user_data: read the machine's own data directory, not a "
        "temporary one — for the two tests that check the platform convention "
        "itself.",
    )


@pytest.fixture(autouse=True)
def _isolate_user_data(request, tmp_path, monkeypatch) -> None:
    """Point the per-user data directory at a fresh temporary one.

    `settings.path()` resolves through `assets._user_data_dir()`, which on
    Windows reads `LOCALAPPDATA` and elsewhere `XDG_DATA_HOME` — so **any test
    that calls `__main__.main()` reads whatever settings file the developer
    happens to have**, and passes or fails according to how they last left the
    in-game options screen.

    That is not hypothetical: `test_remake_cli_death_default.py` asserts that
    running with no `--death` flag uses the original's draw, and it began
    failing the moment the owner set OPENING DEATH to `random` while playing.
    The test was right, the game was right, and the suite was reading a file
    that belongs to neither.

    Autouse and function-scoped, so every test gets an empty directory and no
    test can leave a settings file behind for the next one. The two tests that
    assert the *convention* (that the path follows LOCALAPPDATA / XDG) opt out
    with `@pytest.mark.real_user_data`, since redirecting the thing under test
    would make them pass against anything.
    """
    if request.node.get_closest_marker("real_user_data"):
        return
    monkeypatch.setattr(assets, "_user_data_dir", lambda: tmp_path / "user-data")
