"""The session log: what the world was doing, tick by tick.

**Not the original, and always on** (owner, 2026-08-29). This exists for one
job: when a player says "the crew went to the SHUTTLEBAY for the cat, the Alien
turned up, and the room ended at 99% damage", there should be a file that says
whether that is what happened — instead of a description to reason about and no
evidence either way. A bug you can only reproduce once is worth nothing if the
recorder was switched off at the time, which is what "always" is for.

**Including under the ORIGINAL preset**, and silently. The line DEC-039 drew is
that ORIGINAL governs what the player sees and how the game plays; a file
written outside the game is neither, and the crash log has always installed
unconditionally for the same reason. Nothing about this reaches the screen, the
simulation, or the timing — see :meth:`Journal.record`, which is called from
the app loop after the tick has already resolved.

What it records is the **simulation's own state**, not the renderer's: crew
positions and condition, the Alien, the cat, room damage, fire and alarms, the
notices the game raised and the sound cues it fired. That is the layer a bug in
the game *logic* lives at, and it is the layer that can be replayed against the
disassembly.

Design
------
* **On by default, and cheap.** A line is written only when something changed,
  so a world standing still costs one dict comparison per tick. `set_enabled`
  remains, because a test — and anyone who genuinely wants silence — still
  needs a way to turn it off.
* **Bounded.** Always-on recording that never cleans up is a directory that
  grows until somebody notices, so opening a log prunes older ones down to
  :data:`KEEP_SESSIONS`. Only this module's own files are ever considered; see
  :func:`_prune`.
* **Each line carries what *changed*.** A full snapshot every tick measured at
  756 bytes — 1.4 MB for five minutes of play — almost all of it the same seven
  crew rows written again. Only crew whose row moved are written, so a line is
  usually a handful of fields and the moment a bug happened is visible instead
  of buried. Every :data:`FULL_SNAPSHOT_EVERY` ticks a complete state is
  written anyway, so a reader can resync without replaying from the top.
* **The simulation never writes files.** `Simulation.advance()` stays pure and
  wall-clock-free; the app loop calls `record` after each tick, the same
  boundary the sound-cue drain already uses.
* **JSON Lines**, one object per line, so a truncated file from a crash still
  parses up to the last complete tick — which is exactly the file you want when
  the crash *is* the bug.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .state import GameState

#: Filename stem; the timestamp keeps runs apart.
PREFIX = "session"

#: How many session logs to keep. Recording is always on now, so something has
#: to stop the folder growing forever — and a count is the right limit rather
#: than an age, because what a person wants is "the last few runs", however
#: long ago they played. Generous on purpose: these files are small, and the
#: run you want is often not the last one.
KEEP_SESSIONS = 20

#: How often a complete state is written regardless of what changed. At the
#: 6.25 Hz tick that is about every 16 seconds — often enough to pick the file
#: up in the middle, rare enough not to undo the saving.
FULL_SNAPSHOT_EVERY = 100


def _crew_row(crew: Any) -> dict[str, Any]:
    """One crew member, reduced to what a logic bug shows up in."""
    return {
        "room": crew.room_id,
        "health": crew.health,
        "fear": crew.fear,
        "alive": crew.alive,
        "awake": crew.awake,
        "timer": crew.step_timer,
    }


def snapshot(state: GameState) -> dict[str, Any]:
    """The state worth keeping from one tick.

    Empty and default fields are dropped rather than written as nulls: the
    point of the file is that a reader can see what *is* happening, and a
    hundred keys of `null` on every line hides it.
    """
    out: dict[str, Any] = {
        "tick": state.tick,
        "phase": state.phase.name,
        "crew": {cid: _crew_row(c) for cid, c in state.crew.items()},
    }
    if state.alien is not None:
        out["alien"] = {
            "room": state.alien.room_id,
            "timer": state.alien.timer,
            "alive": state.alien.alive,
        }
    for key, value in (
        ("jones_room", state.jones_room_id),
        ("jones_caught", state.jones_caught),
        ("jones_container", state.jones_container_id),
        ("auto_destruct", state.auto_destruct_ticks),
        ("notice", state.notice),
        ("malfunction", state.malfunction),
        ("tracker_alarm", state.tracker_alarm),
        ("android_revealed", state.android_revealed),
        ("ship_destructing", state.ship_destructing),
        ("ship_destroyed", state.ship_destroyed),
        ("narcissus_launched", state.narcissus_launched),
        ("stowed_crew", state.stowed_crew_id),
        ("locked_crew", state.locked_crew_id),
        ("win_route", state.win_route.name if state.win_route else None),
    ):
        if value:
            out[key] = value
    # Rooms are logged only where something is wrong with them, which is what
    # makes a damage report readable at a glance.
    for key, mapping in (
        ("damage", state.room_damage),
        ("fire", state.room_fire),
        ("alarm", state.room_alarm),
    ):
        live = {room: n for room, n in mapping.items() if n}
        if live:
            out[key] = live
    open_locks = [room for room, is_open in state.airlocks_open.items() if is_open]
    if open_locks:
        out["airlocks_open"] = open_locks
    if state.sound_cues:
        out["cues"] = [
            {"effect": c.effect, "crew": c.crew_id} if c.crew_id
            else c.effect
            for c in state.sound_cues
        ]
    return out


def _delta(row: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    """``row`` reduced to what differs from the previous line.

    ``tick`` always survives, and ``crew`` is thinned member by member rather
    than dropped whole: one character moving should cost one crew row, not
    seven. A key that has *gone* is written as ``None`` so a reader can tell
    "unchanged" from "cleared" — the difference between a fire still burning
    and a fire just put out.
    """
    out: dict[str, Any] = {"tick": row["tick"]}
    for key, value in row.items():
        if key in ("tick", "crew"):
            continue
        if previous.get(key) != value:
            out[key] = value
    for key in previous:
        if key not in row and key != "crew":
            out[key] = None
    before = previous.get("crew", {})
    moved = {
        cid: crew for cid, crew in row["crew"].items() if before.get(cid) != crew
    }
    if moved:
        out["crew"] = moved
    return out


def _prune(directory: Path, keep: int = KEEP_SESSIONS) -> list[Path]:
    """Delete all but the newest ``keep`` session logs. Returns what went.

    **Deliberately narrow about what it will delete.** Only files in this
    directory matching this module's own `session-<stamp>.jsonl` shape are even
    considered — not everything in the folder, not anything recursive, and
    nothing it did not write itself. Turning a feature on by default is not a
    licence to tidy somebody's disk.

    Sorted by name, which is the same order as by time: the stamp is
    `%Y%m%d-%H%M%S`, so it sorts chronologically as text. That avoids trusting
    mtimes, which a copy or a sync can rewrite.

    Never raises. Failing to prune is not a reason to lose the recording.
    """
    if keep < 0:
        return []
    try:
        logs = sorted(
            path for path in directory.glob(f"{PREFIX}-*.jsonl")
            if path.is_file()
        )
    except OSError:
        return []
    removed: list[Path] = []
    for path in logs[:max(0, len(logs) - keep)]:
        try:
            path.unlink()
        except OSError:
            continue
        removed.append(path)
    return removed


class Journal:
    """Writes tick snapshots to a JSON Lines file.

    On unless something turns it off — see the module docstring for why that
    changed, and why it stays on under the ORIGINAL preset.
    """

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory
        self.enabled = False
        self.path: Path | None = None
        self._handle: Any = None
        self._last: dict[str, Any] | None = None
        self._written = 0

    # --- lifecycle ----------------------------------------------------------

    def set_enabled(self, on: bool) -> None:
        """Turn recording on or off — the DEVELOPER options row drives this.

        Turning it on opens a new file, so switching it off and on again starts
        a fresh log rather than interleaving two runs in one.
        """
        if on == self.enabled:
            return
        self.enabled = on
        if not on:
            self.close()
            return
        # Deliberately no `_open()`: the file appears with its first line.
        self._handle = None
        self._last = None
        self._written = 0

    def _open(self) -> None:
        """Create the file. **On the first line written, not on enable.**

        Turning developer mode on and off again without playing used to leave a
        0-byte log behind each time — visible in a real logs folder, and the
        kind of litter that makes a directory of evidence harder to read.
        Nothing is created until there is something to record.
        """
        if self.directory is None:
            return
        # Prune before opening, not after: pruning first means the count is
        # honest (`KEEP_SESSIONS` older runs plus this one being written),
        # and a run cannot delete itself by being the oldest of many.
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            _prune(self.directory, KEEP_SESSIONS - 1)
        except OSError:
            pass
        stamp = time.strftime("%Y%m%d-%H%M%S")
        path = self.directory / f"{PREFIX}-{stamp}.jsonl"
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            # The stamp is only accurate to the second, and toggling developer
            # mode off and on again inside one second is an ordinary thing to
            # do — so a suffix keeps the first recording instead of opening the
            # same name "w" and erasing it.
            n = 2
            while path.exists():
                path = self.directory / f"{PREFIX}-{stamp}-{n}.jsonl"
                n += 1
            self._handle = path.open("w", encoding="utf-8")
        except OSError:
            # A log that cannot be written must not take the game down; the
            # player asked to record, not to risk the session.
            self._handle = None
            return
        self.path = path
        self._last = None
        self._written = 0

    def close(self) -> None:
        if self._handle is not None:
            try:
                self._handle.close()
            except OSError:
                pass
        self._handle = None

    # --- recording ----------------------------------------------------------

    def record(self, state: GameState) -> bool:
        """Write this tick if anything changed. Returns whether it wrote.

        The comparison ignores `tick` itself, so a world that is genuinely
        standing still stays quiet however long it stands.
        """
        if not self.enabled:
            return False
        if self._handle is None:
            self._open()
        if self._handle is None:
            return False
        row = snapshot(state)
        compare = {k: v for k, v in row.items() if k != "tick"}
        if compare == self._last:
            return False
        full = self._written % FULL_SNAPSHOT_EVERY == 0
        previous, self._last = self._last, compare
        if not full and previous is not None:
            row = _delta(row, previous)
        else:
            row["full"] = True
        try:
            self._handle.write(json.dumps(row, separators=(",", ":")) + "\n")
            self._handle.flush()      # a crash is a thing worth logging
        except (OSError, TypeError):
            return False
        self._written += 1
        return True

    def note(self, kind: str, **fields: Any) -> None:
        """Record a discrete event the state does not carry by itself.

        Orders are the case this exists for: the panel issues them straight to
        the simulation, and by the next tick the only trace is a changed timer.
        """
        if not self.enabled:
            return
        if self._handle is None:
            self._open()
        if self._handle is None:
            return
        try:
            self._handle.write(
                json.dumps({"event": kind, **fields}, separators=(",", ":")) + "\n"
            )
            self._handle.flush()
        except (OSError, TypeError):
            pass
