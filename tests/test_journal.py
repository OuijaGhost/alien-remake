"""The developer-mode session log.

Its whole value is being trustworthy after the fact: a line that says a room was
at 99% damage has to mean the simulation said so, and a line that is *absent*
has to mean nothing changed — not that the writer dropped it.
"""

from __future__ import annotations

import json
import random

from alien_remake.core.journal import FULL_SNAPSHOT_EVERY, Journal, snapshot
from alien_remake.core.menu import MenuController
from alien_remake.core.sim import Simulation


def _lines(journal: Journal) -> list[dict]:
    assert journal.path is not None
    return [
        json.loads(line)
        for line in journal.path.read_text(encoding="utf-8").splitlines()
    ]


def _recording(tmp_path) -> Journal:
    """An enabled journal. The file appears with its first line, not here."""
    journal = Journal(tmp_path / "logs")
    journal.set_enabled(True)
    return journal


# --- off by default ----------------------------------------------------------

def test_nothing_is_written_until_it_is_enabled(tmp_path) -> None:
    journal = Journal(tmp_path / "logs")
    sim = Simulation(rng=random.Random(1))
    sim.advance()
    assert journal.record(sim.state) is False
    assert journal.path is None
    assert not (tmp_path / "logs").exists(), "a disabled journal made a directory"


def test_a_directory_it_cannot_write_does_not_raise(tmp_path) -> None:
    """Recording is a convenience; losing it must not cost the session."""
    blocker = tmp_path / "blocked"
    blocker.write_text("not a directory", encoding="utf-8")
    journal = Journal(blocker / "logs")
    journal.set_enabled(True)
    sim = Simulation(rng=random.Random(1))
    sim.advance()
    assert journal.record(sim.state) is False
    journal.close()


# --- what a line means -------------------------------------------------------

def test_the_first_line_is_a_full_state(tmp_path) -> None:
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(3))
    sim.advance()
    assert journal.record(sim.state) is True
    journal.close()

    first = _lines(journal)[0]
    assert first.get("full") is True
    assert set(first["crew"]) == set(sim.state.crew), "every crew member"


def test_later_lines_carry_only_what_changed(tmp_path) -> None:
    """The saving that makes a long session readable — and reversible.

    A delta is only useful if it is honest, so this replays the file and
    requires the reconstruction to equal the real state at the end.
    """
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(3))
    for _ in range(120):
        sim.advance()
        journal.record(sim.state)
    journal.close()

    rebuilt: dict = {}
    for line in _lines(journal):
        if line.get("full"):
            rebuilt = {k: v for k, v in line.items() if k not in ("full", "tick")}
            continue
        for key, value in line.items():
            if key == "tick":
                continue
            if key == "crew":
                rebuilt.setdefault("crew", {}).update(value)
            elif value is None:
                rebuilt.pop(key, None)
            else:
                rebuilt[key] = value

    final = snapshot(sim.state)
    del final["tick"]
    assert rebuilt == final, "replaying the deltas does not reproduce the state"


def test_a_full_snapshot_appears_periodically(tmp_path) -> None:
    """So a reader can pick the file up in the middle."""
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(3))
    for _ in range(FULL_SNAPSHOT_EVERY * 3):
        sim.advance()
        journal.record(sim.state)
    journal.close()
    assert sum(1 for line in _lines(journal) if line.get("full")) >= 3


def test_an_unchanged_world_writes_nothing(tmp_path) -> None:
    """The dedupe, driven straight at it: the same state twice is one line."""
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(3))
    sim.advance()
    assert journal.record(sim.state) is True
    assert journal.record(sim.state) is False, "the same state was written twice"
    journal.close()


def test_damage_and_fire_are_recorded_where_they_happen(tmp_path) -> None:
    """The shape of the report a player's description has to be checked against."""
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(3))
    room = next(iter(sim.ship.rooms))
    sim.state.room_damage[room] = 99
    sim.state.room_fire[room] = 4
    sim.advance()
    journal.record(sim.state)
    journal.close()

    full = next(line for line in _lines(journal) if line.get("full"))
    assert full["damage"][room] == 99
    assert full["fire"][room] == 4


def test_rooms_with_nothing_wrong_are_left_out(tmp_path) -> None:
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(3))
    sim.advance()
    journal.record(sim.state)
    journal.close()
    full = next(line for line in _lines(journal) if line.get("full"))
    assert all(n for n in full.get("damage", {}).values())


# --- the panel hook ----------------------------------------------------------

def test_orders_are_recorded_because_the_state_does_not_keep_them(tmp_path) -> None:
    """By the next tick an order is only a changed countdown.

    So what the *player chose* has to be caught as it is chosen — which is the
    half of a bug report the state alone cannot answer.
    """
    journal = _recording(tmp_path)
    sim = Simulation(rng=random.Random(7))
    menu = MenuController(sim)
    menu.on_action = lambda kind, fields: journal.note(kind, **fields)

    entries = menu.entries()
    crew_row = next(i for i, e in enumerate(entries) if e.select_crew is not None)
    menu.select_index(crew_row)
    menu.fire()
    order_row = next(
        (i for i, e in enumerate(menu.entries()) if e.order is not None), None
    )
    if order_row is not None:
        menu.select_index(order_row)
        menu.fire()
    journal.close()

    actions = [line for line in _lines(journal) if line.get("event") == "action"]
    assert actions, "firing the panel recorded nothing"
    assert actions[0]["select_crew"] == entries[crew_row].select_crew
    if order_row is not None:
        assert actions[-1]["order"]["type"], "the order type is what a reader needs"


def test_the_hook_is_inert_when_nothing_is_listening() -> None:
    """The core must not require a journal to exist."""
    sim = Simulation(rng=random.Random(7))
    menu = MenuController(sim)
    assert menu.on_action is None
    row = next(i for i, e in enumerate(menu.entries()) if e.selectable)
    menu.select_index(row)
    menu.fire()          # must not raise


def test_switching_off_and_on_keeps_the_earlier_recording(tmp_path) -> None:
    """Toggling twice inside one second must not erase the first log.

    The filename stamp is only accurate to the second, so without a suffix the
    second run opens the first run's name in "w" mode — and the recording the
    player wanted is gone at the moment they turn recording back on.
    """
    journal = Journal(tmp_path / "logs")
    sim = Simulation(rng=random.Random(3))

    journal.set_enabled(True)
    sim.advance()
    journal.record(sim.state)
    first = journal.path
    journal.set_enabled(False)

    journal.set_enabled(True)
    sim.advance()
    journal.record(sim.state)
    second = journal.path
    journal.close()

    assert first is not None and second is not None
    assert second != first, "the second run reopened the first run's file"
    assert first.exists() and first.read_text(encoding="utf-8").strip(), (
        "the earlier recording was erased"
    )


def test_toggling_without_playing_leaves_no_empty_file(tmp_path) -> None:
    """A real logs folder had 0-byte files in it from exactly this.

    Enabling used to create the file immediately, so turning developer mode on
    and off again — an ordinary thing to do while looking at the options —
    littered the directory of evidence with empties.
    """
    logs = tmp_path / "logs"
    journal = Journal(logs)
    for _ in range(3):
        journal.set_enabled(True)
        journal.set_enabled(False)
    assert not logs.exists() or not list(logs.glob("*.jsonl")), (
        "an idle toggle left a file behind"
    )
