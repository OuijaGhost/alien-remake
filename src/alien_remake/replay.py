"""Reading a session log back. **L5 / R1-R6.**

The journal writes delta-encoded JSON Lines: after the first line, each row
carries only what *changed*, so a line in the middle of a file is a handful of
fields whose meaning depends on every line above it. That is the right shape to
write — 27 KB a minute instead of 285 — and the wrong shape to read.

Built for one workflow, which the owner stated plainly: *"my plan was to simply
give them to an AI assistant and ask why something happened in playtesting."* That is not
a log viewer, and building one would have been building the wrong thing. What it
needs instead is output that is **small enough to paste** and **legible to
someone who has never read this codebase** — hence the summary, the legend, and
the deliberate absence of a timeline widget.

Three ways in
-------------
* :func:`states` resolves the deltas back to full pictures (R1).
* :func:`summarise` turns a run into a page of prose with tick numbers (R4) —
  the thing most likely to be pasted into a conversation.
* :func:`window` slices around a moment (R2/R3), for when the summary says
  *something happened around here* and the next question is *what exactly*.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .core import constants

#: What the fields mean, for a reader who has never seen this game's source.
#: Printed with the summary because a log that has to be explained in a covering
#: message is a log that will be misread when the covering message is forgotten.
#: The two that actually catch people are the first two.
LEGEND: tuple[tuple[str, str], ...] = (
    ("fear", "counts UP: 0 is composed, 10 is broken. The morale word is "
             "derived from it, so a rising number is a crew member getting "
             "worse."),
    # **Per character, not a flat 4.** The first draft of this line said
    # "counts down from CREW_START_HEALTH" (4); the crew actually start on
    # 4, 5 or 6 depending on who they are, which the very first summary
    # printed as "parker health 6 -> 5" and contradicted its own legend.
    ("health", f"counts DOWN, and each crew member has their own maximum "
               f"(4 to 6 - Parker is the toughest). Below "
               f"{constants.CREW_INCAPACITATED_BELOW} is incapacitated."),
    ("timer", "ticks left on whatever this character is doing. Non-zero means "
              "busy, which is why a new order appears to do nothing."),
    ("room", "where they are. `in_duct` is a separate space - a character in "
             "the ducting is not in the room of the same name."),
    ("tick", f"the simulation's own clock, {constants.TICK_HZ:.2f} per second. "
             f"Divide by that for seconds of play."),
    ("damage", "room damage. A room is holed at "
               f"{constants.HULL_BREACH_THRESHOLD}, and the test is an "
               "equality - a room carried past it is safe forever."),
    ("cues", "sounds the tick fired."),
    ("event", "a line the game raised rather than a state: an order issued, or "
              "a developer-mode change. `dev` events mean somebody reached in."),
)


@dataclass
class Tick:
    """One tick, resolved to a complete picture."""

    tick: int
    state: dict[str, Any]
    #: Events recorded between this tick and the last (orders, dev changes).
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def seconds(self) -> float:
        return self.tick / constants.TICK_HZ

    @property
    def crew(self) -> dict[str, Any]:
        crew: dict[str, Any] = self.state.get("crew", {})
        return crew


def _apply(base: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    """One delta onto the running state. The inverse of `journal._delta`.

    Three rules, and the third is the one that bites: a key written as ``None``
    means *cleared*, not *unchanged*. The journal writes it that way precisely
    so a fire going out can be told from a fire still burning, and a reader that
    treats null as absent would show every extinguished fire as eternal.
    """
    if row.get("full"):
        out = {k: v for k, v in row.items() if k != "full"}
        return out
    out = dict(base)
    for key, value in row.items():
        if key == "crew":
            crew = dict(out.get("crew", {}))
            crew.update(value)
            out["crew"] = crew
        elif value is None:
            out.pop(key, None)
        else:
            out[key] = value
    out["tick"] = row.get("tick", out.get("tick"))
    return out


def read(path: Path) -> Iterator[dict[str, Any]]:
    """Every parsable line. A truncated last line is skipped, not fatal.

    A crash mid-write is exactly when the file matters most, so the reader has
    to survive the half-line the crash left behind.
    """
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row


def states(path: Path) -> list[Tick]:
    """**R1.** The whole run, every tick resolved to a full picture.

    Events are attached to the tick that follows them, because an order is
    issued *between* ticks and what a reader wants to see is the order next to
    what happened after it.
    """
    out: list[Tick] = []
    running: dict[str, Any] = {}
    pending: list[dict[str, Any]] = []
    for row in read(path):
        if "event" in row:
            pending.append(row)
            continue
        running = _apply(running, row)
        out.append(Tick(int(running.get("tick", 0)), running, pending))
        pending = []
    return out


def window(
    ticks: Sequence[Tick],
    *,
    around: int | None = None,
    span: int = 40,
    first: int | None = None,
    last: int | None = None,
    crew: str | None = None,
    room: str | None = None,
) -> list[Tick]:
    """**R2/R3.** A slice, by tick range or around a moment, optionally filtered.

    ``around`` is the one that gets used: the summary says a thing happened near
    tick N and the next question is always what led up to it.
    """
    if around is not None:
        first, last = around - span, around + span
    chosen = [
        t for t in ticks
        if (first is None or t.tick >= first) and (last is None or t.tick <= last)
    ]
    if crew is not None:
        chosen = [t for t in chosen if crew in t.crew]
    if room is not None:
        chosen = [
            t for t in chosen
            if any(c.get("room") == room for c in t.crew.values())
            or (t.state.get("alien") or {}).get("room") == room
            or t.state.get("jones_room") == room
        ]
    return chosen


def _clock(tick: int) -> str:
    total = int(tick / constants.TICK_HZ)
    return f"{total // 60}m{total % 60:02d}s"


def _events(ticks: Sequence[Tick]) -> list[str]:
    """**R6.** What was asked for, and what became of it.

    The state alone cannot tell a refused order from one never given — both
    look like a character standing still — and "I told them to go and they
    didn't" is the commonest kind of playtest report there is.
    """
    out: list[str] = []
    for t in ticks:
        for ev in t.events:
            kind = ev.get("event", "?")
            fields = {k: v for k, v in ev.items() if k != "event"}
            detail = " ".join(f"{k}={v}" for k, v in fields.items())
            out.append(f"  {_clock(t.tick):>7} t{t.tick:<6} {kind:<10} {detail}")
    return out


def _opening_position(first: Tick) -> list[str]:
    """Where everyone was when recording began. **R4, and a real omission.**

    The summary lists *changes*, which meant the opening victim never appeared
    in it at all: they are dead before the first recorded tick, so they never
    transition from alive to dead and nothing was ever printed about them. A
    reader could study the whole report and not learn that a crew member was
    lying dead in the mess for the entire session — which is exactly what
    happened, and prompted a question about who had been "killed so quickly".

    Every state the file opens on is stated now, so the report is a complete
    account rather than a diff against an unstated baseline.
    """
    rows = ["## Where it started", ""]
    dead = []
    for cid, c in sorted(first.crew.items()):
        where = c.get("room") or "?"
        if not c.get("alive"):
            dead.append(cid)
            rows.append(f"  {cid:<9} {where:<12} DEAD before recording began")
        elif not c.get("awake"):
            rows.append(f"  {cid:<9} {where:<12} asleep")
        else:
            rows.append(
                f"  {cid:<9} {where:<12} health {c.get('health')}, "
                f"fear {c.get('fear')}"
            )
    alien = (first.state.get("alien") or {}).get("room")
    rows.append(f"  {'ALIEN':<9} {str(alien):<12}")
    if dead:
        rows += [
            "",
            f"  {', '.join(dead)} {'is' if len(dead) == 1 else 'are'} the "
            f"opening death - killed before play starts, not during this run.",
        ]
    rows.append("")
    return rows


def summarise(path: Path) -> str:
    """**R4.** A run in a page: what happened, in events rather than states.

    Deliberately prose with tick numbers rather than a table. It is written to
    be pasted into a conversation and asked about, so it has to carry enough
    context to be read cold — which is also why the legend is on the end rather
    than in a separate document nobody will open.
    """
    ticks = states(path)
    if not ticks:
        return f"{path.name}: no complete ticks recorded."

    lines = [
        f"# {path.name}",
        "",
        f"{len(ticks)} ticks recorded, ending at t{ticks[-1].tick} "
        f"({_clock(ticks[-1].tick)} of play).",
        "",
    ]
    lines += _opening_position(ticks[0])
    lines += ["## What happened", ""]

    # Crew: first sighting, then every death and every duct crossing.
    prev = ticks[0]
    story: list[str] = []
    for t in ticks[1:]:
        for cid, now in t.crew.items():
            was = prev.crew.get(cid)
            if was is None:
                continue
            if was.get("alive") and not now.get("alive"):
                story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} {cid} died "
                             f"in {now.get('room')}")
            if was.get("room") != now.get("room"):
                story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} {cid} -> "
                             f"{now.get('room')}")
            if was.get("health") != now.get("health"):
                story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} {cid} health "
                             f"{was.get('health')} -> {now.get('health')}")
        a0 = (prev.state.get("alien") or {}).get("room")
        a1 = (t.state.get("alien") or {}).get("room")
        if a0 != a1:
            story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} ALIEN -> {a1}")
        if prev.state.get("notice") != t.state.get("notice") and t.state.get("notice"):
            story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} notice: "
                         f"{t.state['notice']}")
        for key in ("fire", "alarm"):
            if prev.state.get(key) != t.state.get(key) and t.state.get(key):
                story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} {key}: "
                             f"{t.state[key]}")
        if prev.state.get("phase") != t.state.get("phase"):
            story.append(f"  {_clock(t.tick):>7} t{t.tick:<6} PHASE -> "
                         f"{t.state.get('phase')}")
        prev = t
    lines += story or ["  (nothing changed)"]

    events = _events(ticks)
    if events:
        lines += ["", "## Orders and developer changes", ""] + events

    final = ticks[-1].state
    lines += ["", "## Where it ended", "",
              f"  phase   {final.get('phase')}",
              f"  alien   {(final.get('alien') or {}).get('room')}",
              f"  jones   {final.get('jones_room')}"]
    damage = final.get("damage") or {}
    if damage:
        lines.append(f"  damage  {damage}")
    lines += ["", "## Reading this", ""]
    lines += [f"  {name:<8} {why}" for name, why in LEGEND]
    return "\n".join(lines)
