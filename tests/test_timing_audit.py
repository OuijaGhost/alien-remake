"""The timing audit (`core/timing.py`, `docs/TIMING.md`, `--timing`).

The audit exists to answer T3 — what a number means once a turn is however long
the player takes — and an audit that has fallen behind the thing it audits is
worse than none, because it will be trusted. So these hold two properties:

* every duration in `constants` is **classified**, so one cannot be added
  without somebody deciding which kind it is;
* the committed document is **current**, so what is readable on GitHub is what
  the code says.
"""

from __future__ import annotations

import ast
import pathlib

from alien_remake.core import constants, timing  # noqa: E402
from alien_remake.core.timing import Denomination  # noqa: E402

#: Names in `constants` that look like durations. Deliberately a *shape* rule
#: rather than a list, so a new `FOO_TICKS` is caught by having been added at
#: all rather than by anyone remembering to list it here.
def _duration_names() -> set[str]:
    source = pathlib.Path(constants.__file__).read_text(encoding="utf-8")
    names: set[str] = set()
    for node in ast.parse(source).body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
        for name in targets:
            if not name.isupper():
                continue
            if "TICK" in name or name.endswith("_HZ") or "JIFF" in name:
                names.add(name)
    return names


def test_every_duration_is_classified() -> None:
    """The guard that keeps the audit honest as the constants change."""
    classified = {t.name for t in timing.TIMINGS}
    missing = _duration_names() - classified
    assert not missing, (
        f"unclassified durations: {sorted(missing)} - decide whether each is a "
        f"loop count or calibrated to real seconds and add it to "
        f"`core/timing.py`, because T3 cannot be answered for a constant "
        f"nobody has looked at"
    )


def test_nothing_is_classified_that_does_not_exist() -> None:
    for entry in timing.TIMINGS:
        assert hasattr(constants, entry.name), entry.name
        assert getattr(constants, entry.name) == entry.value, entry.name


def test_nothing_is_classified_twice() -> None:
    names = [t.name for t in timing.TIMINGS]
    assert len(names) == len(set(names))


def test_every_entry_says_what_and_why() -> None:
    """A classification with no reason attached is an assertion, not an audit —
    and the reason is the part T3 actually needs."""
    for entry in timing.TIMINGS:
        assert entry.what, entry.name
        assert entry.why, entry.name


# --- the classification itself --------------------------------------------------

def test_the_action_costs_are_loop_counts() -> None:
    """They are the AP scale, and the reason the turn-based mode is possible at
    all: a cost in main-loop passes is already a cost in turns."""
    costs = {
        "MOVE_ACTION_TICKS", "ATTACK_ACTION_TICKS", "GRILLE_ACTION_TICKS",
        "ACTION_DELAY_BY_SLOT", "ACTION_DELAY_BY_HEALTH",
    }
    by_name = {t.name: t for t in timing.TIMINGS}
    for name in costs:
        assert by_name[name].kind is Denomination.LOOP_COUNT, name


def test_the_auto_destruct_is_the_one_that_announces_itself() -> None:
    """Mechanically a counter; a promise about minutes in the fiction. That
    conflict is the whole of T3's difficulty and it must not be filed away as
    an ordinary loop count."""
    by_name = {t.name: t for t in timing.TIMINGS}
    assert by_name["AUTO_DESTRUCT_TICKS"].kind is Denomination.REAL_SECONDS
    assert by_name["AUTO_DESTRUCT_MINUTES"].kind is Denomination.REAL_SECONDS


def test_minutes_are_not_divided_by_the_tick_rate() -> None:
    """`AUTO_DESTRUCT_MINUTES` is nine *minutes*. The table printed "1.1 s" for
    it quite happily until somebody read the output."""
    by_name = {t.name: t for t in timing.TIMINGS}
    assert by_name["AUTO_DESTRUCT_MINUTES"].seconds is None
    assert by_name["AUTO_DESTRUCT_TICKS"].seconds is not None


def test_a_tick_count_reports_its_length() -> None:
    by_name = {t.name: t for t in timing.TIMINGS}
    move = by_name["MOVE_ACTION_TICKS"]
    assert move.seconds is not None
    assert abs(move.seconds - constants.MOVE_ACTION_TICKS / constants.TICK_HZ) < 1e-9


def test_rates_have_no_length() -> None:
    for entry in timing.by_kind(Denomination.RATE):
        assert entry.seconds is None, entry.name


def test_each_kind_says_what_becomes_of_it_under_turns() -> None:
    notes = {t.kind: t.turn_note for t in timing.TIMINGS}
    assert "turns" in notes[Denomination.LOOP_COUNT]
    assert "T3" in notes[Denomination.REAL_SECONDS]


# --- the document ----------------------------------------------------------------

def test_the_committed_document_is_current() -> None:
    """`docs/TIMING.md` is generated. If this fails, run:

        python -c "import pathlib; from alien_remake.core import timing; \\
        pathlib.Path('docs/TIMING.md').write_text(timing.describe()+chr(10), \\
        encoding='utf-8', newline='')"
    """
    doc = pathlib.Path(__file__).resolve().parent.parent / "docs" / "TIMING.md"
    assert doc.is_file(), "docs/TIMING.md is missing"
    assert doc.read_text(encoding="utf-8") == timing.describe() + "\n", (
        "docs/TIMING.md is out of date - regenerate it (see this docstring)"
    )


def test_the_document_separates_the_two_kinds_that_matter() -> None:
    text = timing.describe()
    assert "survive player-paced turns" in text
    assert "what T3 must decide" in text
    for entry in timing.TIMINGS:
        assert f"`{entry.name}`" in text, entry.name
