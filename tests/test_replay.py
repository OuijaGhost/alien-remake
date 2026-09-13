"""tools/replay.py — reading session logs the way the owner's workflow uses them.

The owner's own words set the target: *"my plan was to simply give them to
an AI assistant and ask why something happened in playtesting."* So the tests that
matter are round-tripping the delta format faithfully (R1) and the summary
reading as a correct, pasteable page (R4/R6) — not a viewer's worth of UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import replay  # noqa: E402

from alien_remake.core.flow import default_simulation
from alien_remake.core.journal import Journal
from alien_remake.core.modes import DeathVariant, GameMode
from alien_remake.core.orders import Order, OrderType


def _record_a_run(tmp_path: Path, ticks: int = 250) -> Path:
    """A real session log, produced the same way the app loop produces one."""
    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    journal = Journal(tmp_path)
    journal.set_enabled(True)

    crew = next(
        c for c in sim.state.crew.values()
        if c.alive and c.id != sim.state.android_id
    )
    assert crew.room_id is not None
    destination = sim.ship.door_neighbors(crew.room_id)[0]
    sim.queue_order(Order(crew.id, OrderType.MOVE_TO, destination))
    journal.note(
        "action", label=f"MOVE TO {destination}", selected=crew.id,
        order={"type": "MOVE_TO", "target": destination}, special=None,
        select_crew=None, tick=sim.state.tick,
    )
    for _ in range(ticks):
        sim.advance()
        journal.record(sim.state)
        for order, outcome in sim.last_outcomes:
            journal.note(
                "outcome", crew=order.crew_id, type=order.type.name,
                target=order.target, result=outcome.name,
            )
    journal.close()
    assert journal.path is not None
    return journal.path


# --- R1: the resolver is the exact inverse of the recorder -----------------


def test_resolve_matches_the_simulation_it_recorded(tmp_path: Path) -> None:
    """The strongest check available: replay a real run and diff every field
    the log actually carries against the live Simulation that produced it."""
    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    journal = Journal(tmp_path)
    journal.set_enabled(True)
    live_states = []
    for _ in range(150):
        sim.advance()
        journal.record(sim.state)
        from alien_remake.core.journal import snapshot
        live_states.append(snapshot(sim.state))
    journal.close()
    assert journal.path is not None

    resolved = replay.resolve(journal.path)

    # One resolved state per *recorded* tick, i.e. per tick something changed -
    # journal.record() itself skips a standing-still world, so the two lists
    # only line up after re-deriving which ticks were actually written.
    by_tick = {s["tick"]: s for s in live_states}
    assert len(resolved) > 0
    for state in resolved:
        expected = by_tick[state["tick"]]
        assert state == expected, f"mismatch at tick {state['tick']}"


def test_resolve_survives_a_truncated_file(tmp_path: Path) -> None:
    """A crash log is exactly the file you most want to read (journal.py)."""
    path = _record_a_run(tmp_path)
    whole = path.read_text(encoding="utf-8")
    cut = path.with_name("truncated.jsonl")
    cut.write_text(whole[: len(whole) // 2] + '{"tick":999,"crew":{"x"', encoding="utf-8")

    states = replay.resolve(cut)
    assert states, "a truncated file produced nothing at all"
    assert all("tick" in s for s in states)


def test_a_none_field_clears_rather_than_is_ignored(tmp_path: Path) -> None:
    """The delta format's one sharp edge: `None` means "this went away", not
    "unchanged". A resolver that treats them the same reports a fire that was
    put out as still burning."""
    import json

    log = tmp_path / "fire.jsonl"
    log.write_text(
        '\n'.join([
            json.dumps({"tick": 0, "crew": {}, "fire": {"mess": 3}, "full": True}),
            json.dumps({"tick": 1, "fire": None}),
        ]) + "\n",
        encoding="utf-8",
    )
    states = replay.resolve(log)
    assert "fire" not in states[1], "the cleared field was not cleared"


# --- R2: slicing ------------------------------------------------------------


def test_parse_offset_reads_ticks_and_wall_clock() -> None:
    assert replay.parse_offset("500") == 500
    assert replay.parse_offset("1m") == round(60 * 7.886)
    assert replay.parse_offset("30s") == round(30 * 7.886)
    assert replay.parse_offset("1h") == round(3600 * 7.886)


def test_from_to_slices_by_tick(tmp_path: Path) -> None:
    path = _record_a_run(tmp_path)
    states = replay.filter_states(replay.resolve(path), lo=10, hi=20)
    assert states
    assert all(10 <= s["tick"] <= 20 for s in states)


def test_around_centres_a_window(tmp_path: Path) -> None:
    path = _record_a_run(tmp_path)
    all_states = replay.resolve(path)
    centre = all_states[len(all_states) // 2]["tick"]
    states = replay.filter_states(all_states, lo=centre - 5, hi=centre + 5)
    assert all(centre - 5 <= s["tick"] <= centre + 5 for s in states)


# --- R3: filtering -----------------------------------------------------------


def test_crew_filter_keeps_only_states_naming_that_member(tmp_path: Path) -> None:
    path = _record_a_run(tmp_path)
    states = replay.resolve(path)
    filtered = replay.filter_states(states, crew="ripley")
    assert filtered
    assert all("ripley" in s.get("crew", {}) for s in filtered)


def test_room_filter_matches_crew_or_the_alien(tmp_path: Path) -> None:
    path = _record_a_run(tmp_path)
    states = replay.resolve(path)
    some_room = next(iter(states[0]["crew"].values()))["room"]
    filtered = replay.filter_states(states, room=some_room)
    assert filtered
    for s in filtered:
        crew_here = any(c.get("room") == some_room for c in s["crew"].values())
        alien_here = s.get("alien", {}).get("room") == some_room
        assert crew_here or alien_here


# --- R4/R6: the summary ------------------------------------------------------


def test_the_summary_pairs_an_order_with_its_outcome(tmp_path: Path) -> None:
    path = _record_a_run(tmp_path, ticks=250)
    text = replay.summarise(path)
    assert "MOVE_TO" in text
    assert "IN_TRANSIT" not in text, "an in-progress result leaked into the summary"
    assert "COMPLETED" in text or "BLOCKED" in text or "unresolved" in text


def test_the_summary_does_not_narrate_the_opening_death(tmp_path: Path) -> None:
    """The victim is already dead in the very first recorded state - that is a
    scenario premise the player already saw, not a mid-run event."""
    path = _record_a_run(tmp_path, ticks=5)
    states = replay.resolve(path)
    dead_from_the_start = [
        cid for cid, row in states[0]["crew"].items() if not row.get("alive", True)
    ]
    assert dead_from_the_start, "the fixed opening produced no victim - test invalid"
    text = replay.summarise(path)
    for cid in dead_from_the_start:
        assert f"{cid} died" not in text


def test_the_summary_reports_a_later_death(tmp_path: Path) -> None:
    sim = default_simulation(GameMode.FULL, DeathVariant.FIXED)
    journal = Journal(tmp_path)
    journal.set_enabled(True)
    for _ in range(3):
        sim.advance()
        journal.record(sim.state)
    victim = next(c for c in sim.state.crew.values() if c.alive)
    victim.health, victim.alive = 0, False
    sim.advance()
    journal.record(sim.state)
    journal.close()
    assert journal.path is not None

    text = replay.summarise(journal.path)
    assert f"{victim.id} died" in text


def test_developer_interference_is_surfaced_prominently(tmp_path: Path) -> None:
    path = _record_a_run(tmp_path, ticks=5)
    journal = Journal(tmp_path)
    journal.enabled = True
    journal._handle = path.open("a", encoding="utf-8")
    journal.note("dev", change="F1 fear -1 on ripley")
    journal.close()

    text = replay.summarise(path)
    lines = text.splitlines()
    flagged = [i for i, ln in enumerate(lines) if "altered by developer" in ln]
    assert flagged, "developer interference did not appear in the summary at all"
    assert flagged[0] <= 2, "the warning is not near the top of the summary"


def test_an_empty_log_summarises_without_crashing(tmp_path: Path) -> None:
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    assert "empty" in replay.summarise(empty).lower()


# --- R5: the legend -----------------------------------------------------


def test_the_legend_explains_the_fields_a_reader_would_not_know() -> None:
    for term in ("fear", "health", "tick", "IN_TRANSIT"):
        assert term in replay.LEGEND


# --- the CLI itself -----------------------------------------------------


def test_cli_summary_runs_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _record_a_run(tmp_path)
    rc = replay.main([str(path), "--summary"])
    assert rc == 0
    assert capsys.readouterr().out.strip()


def test_cli_reports_a_missing_file_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = replay.main([str(tmp_path / "nope.jsonl")])
    assert rc == 2
    assert "no such file" in capsys.readouterr().err.lower()


def test_cli_legend_needs_no_log_file() -> None:
    assert replay.main(["--legend"]) == 0
