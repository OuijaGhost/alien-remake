"""The session log records every run, under every preset (owner, 2026-08-29).

It used to follow the DEVELOPER row. The owner's reason for changing that is
the honest one: a bug you can only reproduce once is worth nothing if the
recorder happened to be off at the time, and playtesting is exactly when you do
not yet know which run will matter.

Two things then need holding down. It has to record **under ORIGINAL** — which
is a claim about where DEC-039's line falls, not an oversight — and it has to
do it **silently**, because a boot card that appears on every launch is one
nobody reads (B5). Always-on also introduces a failure the opt-in version never
had: a folder that grows until somebody notices.
"""

from __future__ import annotations

import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from alien_remake.core import journal as journal_module  # noqa: E402
from alien_remake.core.journal import Journal, _prune  # noqa: E402
from alien_remake.core.options import PROFILES  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402


def _run(directory, ticks: int = 12) -> Journal:
    """A journal fed a few ticks of a real simulation."""
    sim = Simulation()
    journal = Journal(directory)
    journal.set_enabled(True)
    for _ in range(ticks):
        sim.advance()
        journal.record(sim.state)
    journal.close()
    return journal


# --- it records, and it records under ORIGINAL --------------------------------

def test_a_plain_run_leaves_a_log(tmp_path) -> None:
    journal = _run(tmp_path)
    assert journal.path is not None
    assert journal.path.exists()
    assert journal.path.read_text(encoding="utf-8").strip()


def test_the_original_preset_does_not_switch_it_off() -> None:
    """The preset governs what the player sees and how the game plays; a file
    written outside the game is neither. So there is no `journal` key in either
    profile — nothing about the preset can reach it.
    """
    for name, profile in PROFILES.items():
        assert "journal" not in profile, name
        assert "log" not in profile, name


def test_developer_mode_no_longer_gates_recording() -> None:
    """`__main__` must enable it outright, and must not turn it off when the
    DEVELOPER row goes off — that would throw away the recording of the very
    session someone is investigating.
    """
    import pathlib

    import alien_remake.__main__ as main_module

    source = pathlib.Path(main_module.__file__).read_text(encoding="utf-8")
    assert "journal.set_enabled(True)" in source
    assert "journal.set_enabled(developer_on)" not in source
    assert 'journal.set_enabled(args.developer == "on")' not in source


def test_it_says_nothing_unless_developer_mode_is_on() -> None:
    """The "silently" half. `bool(report)` decides whether the boot card is
    shown at all, so an unconditional line would give every launch a card."""
    import pathlib

    import alien_remake.__main__ as main_module

    source = pathlib.Path(main_module.__file__).read_text(encoding="utf-8")
    line = source.index('report.info(f"recording to {logs}")')
    before = source[:line]
    assert before.rstrip().endswith(":") or 'if args.developer == "on":' in before
    assert 'if args.developer == "on":' in before


def test_a_run_that_never_starts_leaves_no_file(tmp_path) -> None:
    """The file appears with its first line. Always-on must not mean a 0-byte
    log for every launch someone quits from the menu."""
    journal = Journal(tmp_path)
    journal.set_enabled(True)
    journal.close()
    assert list(tmp_path.glob("*.jsonl")) == []


def test_the_lines_are_readable_json(tmp_path) -> None:
    journal = _run(tmp_path)
    assert journal.path is not None
    for line in journal.path.read_text(encoding="utf-8").splitlines():
        assert json.loads(line)


# --- and it does not fill the disk ---------------------------------------------

def test_old_logs_are_pruned(tmp_path) -> None:
    for n in range(30):
        (tmp_path / f"session-2026082{n // 10}-0000{n % 10:02d}.jsonl").write_text(
            "{}\n", encoding="utf-8"
        )
    _prune(tmp_path, keep=5)
    assert len(list(tmp_path.glob("session-*.jsonl"))) == 5


def test_pruning_keeps_the_newest(tmp_path) -> None:
    """Sorted by name, which for a `%Y%m%d-%H%M%S` stamp is sorted by time —
    and does not trust mtimes, which a copy or a sync rewrites."""
    names = [f"session-20260829-0000{n:02d}.jsonl" for n in range(10)]
    for name in names:
        (tmp_path / name).write_text("{}\n", encoding="utf-8")
    _prune(tmp_path, keep=3)
    left = sorted(p.name for p in tmp_path.glob("session-*.jsonl"))
    assert left == names[-3:]


def test_pruning_touches_nothing_it_did_not_write(tmp_path) -> None:
    """Turning a feature on by default is not a licence to tidy someone's disk.

    Only this module's own `session-<stamp>.jsonl` files are candidates: not
    everything in the folder, not other extensions, and nothing recursive.
    """
    keep_these = [
        tmp_path / "notes.txt",
        tmp_path / "session-notes.md",
        tmp_path / "crash.log",
        tmp_path / "important.jsonl",
    ]
    for path in keep_these:
        path.write_text("mine", encoding="utf-8")
    nested = tmp_path / "old"
    nested.mkdir()
    (nested / "session-20260101-000000.jsonl").write_text("{}", encoding="utf-8")
    for n in range(5):
        (tmp_path / f"session-20260829-00000{n}.jsonl").write_text("{}", encoding="utf-8")

    _prune(tmp_path, keep=1)

    for path in keep_these:
        assert path.exists(), f"{path.name} was deleted"
    assert (nested / "session-20260101-000000.jsonl").exists(), "recursed"
    assert len(list(tmp_path.glob("session-2026*.jsonl"))) == 1


def test_recording_prunes_as_it_opens(tmp_path) -> None:
    """The cap has to hold in the running game, not only when called by hand."""
    for n in range(journal_module.KEEP_SESSIONS + 10):
        (tmp_path / f"session-20260829-{n:06d}.jsonl").write_text(
            "{}\n", encoding="utf-8"
        )
    _run(tmp_path)
    left = list(tmp_path.glob("session-*.jsonl"))
    assert len(left) == journal_module.KEEP_SESSIONS, len(left)


def test_the_run_being_recorded_is_never_the_one_pruned(tmp_path) -> None:
    """Pruned before opening, and to `KEEP_SESSIONS - 1`, so the new file is
    not competing with the cap it just made room under."""
    for n in range(journal_module.KEEP_SESSIONS + 5):
        (tmp_path / f"session-20260829-{n:06d}.jsonl").write_text(
            "{}\n", encoding="utf-8"
        )
    journal = _run(tmp_path)
    assert journal.path is not None
    assert journal.path.exists(), "the log deleted itself"


def test_a_pruning_failure_does_not_lose_the_recording(tmp_path, monkeypatch) -> None:
    """Failing to tidy up is not a reason to lose the evidence."""
    def boom(*args, **kwargs):
        raise OSError("no")

    monkeypatch.setattr(journal_module.Path, "glob", boom)
    journal = _run(tmp_path)
    assert journal.path is not None and journal.path.exists()


def test_pruning_a_missing_directory_is_not_an_error(tmp_path) -> None:
    assert _prune(tmp_path / "nowhere", keep=3) == []
