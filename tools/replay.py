"""Read a session log the way the owner's workflow actually uses it.

*"my plan was to simply give them to an AI assistant and ask why something
happened in playtesting."* That is not a log viewer. It is a request for text small enough
to paste and self-explanatory to a reader who has never opened this codebase -
so this tool's only output is text, and its centrepiece is `--summary`: a
run described in prose, with tick numbers, not a table.

    python tools/replay.py path/to/session.jsonl --summary
    python tools/replay.py path/to/session.jsonl --around 900 --window 30
    python tools/replay.py path/to/session.jsonl --from 5m --to 8m --crew ripley
    python tools/replay.py path/to/session.jsonl --legend

Deliberately not built: a graphical timeline, a replay-into-the-renderer mode,
or a diffing tool. All three are more work than this file and none of them
serves a person pasting text into a chat.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Iterator

#: R5. A short legend so a reader who has never seen these fields is not lost.
#: Kept beside the reader rather than in journal.py, because this is the only
#: module that exists to be read by a human rather than by the game.
LEGEND = """\
Fields, for a reader who has not seen this codebase before:

  tick        one simulation step, ~0.127s of game time (7.886 per second)
  phase       RUNNING / WON / LOST - the game's own state
  crew.health 0 (dead) to a per-character max (4-6); below 2 is collapsed
  crew.fear   0 (calm) up to 10 (panicked) - fear counts UP, not down
  crew.awake  false only during ENTER HYPERSLEEP
  crew.timer  ticks left on the character's current action (0 = idle)
  alien.timer ticks left before the Alien's next move/attack
  damage      per-room hull damage, 0-100; a room hits 100 the ship is holed
  fire/alarm  per-room flags, present only where they are actually raised
  event:action   an order or special was chosen from the panel
  event:outcome  what became of it - COMPLETED / IN_TRANSIT / BLOCKED / INVALID
                 (IN_TRANSIT repeats every tick a MOVE is still walking; the
                 order is not stuck, it just is not there yet)
  event:dev      a developer-mode key was used (F1-F5) - the run was interfered
                 with, and this line is exactly what and when
"""

CREW_FIELDS = ("room", "health", "fear", "alive", "awake", "timer")


def parse_offset(text: str, tick_hz: float = 7.886) -> int:
    """R2. A tick number, or a wall-clock offset like ``5m`` / ``90s`` / ``1h``.

    A player describes time in minutes, not ticks, so both forms have to work
    everywhere a tick range is accepted.
    """
    text = text.strip().lower()
    if text.endswith("h"):
        return round(float(text[:-1]) * 3600 * tick_hz)
    if text.endswith("m"):
        return round(float(text[:-1]) * 60 * tick_hz)
    if text.endswith("s"):
        return round(float(text[:-1]) * tick_hz)
    return int(text)


def read_lines(path: Path) -> Iterator[dict[str, Any]]:
    """Yield each JSON object, skipping a truncated final line rather than
    raising - a crash log is exactly the file you most want to read, and it is
    also the one most likely to end mid-write (the module's own docstring)."""
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                return  # the truncated tail; everything before it still reads


def resolve(path: Path) -> list[dict[str, Any]]:
    """R1. Walk the file applying each delta, so every tick is a full state.

    The exact inverse of `journal._delta`: a key present overwrites, a key
    explicitly `None` clears (the delta's way of saying "this went away", not
    "unchanged" - the two are different and the resolver must not conflate
    them), and `crew` is merged member by member, field by field, because a
    delta line only ever carries the members that moved.
    """
    states: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for row in read_lines(path):
        if row.get("event") is not None:
            continue  # a note, not a state line - carried separately
        if row.get("full"):
            current = copy.deepcopy(row)
            current.pop("full", None)
        else:
            tick = row["tick"]
            crew_delta = row.get("crew", {})
            for key, value in row.items():
                if key in ("tick", "crew"):
                    continue
                if value is None:
                    current.pop(key, None)
                else:
                    current[key] = value
            current.setdefault("crew", {})
            for cid, fields in crew_delta.items():
                current["crew"].setdefault(cid, {}).update(fields)
            current["tick"] = tick
        states.append(copy.deepcopy(current))
    return states


def events(path: Path) -> list[dict[str, Any]]:
    """The `event:` lines only, in file order. Not tick-resolved - they need
    no resolving, each one is already complete in itself."""
    return [row for row in read_lines(path) if row.get("event") is not None]


# --- R2/R3: slicing and filtering ------------------------------------------


def in_range(tick: int, lo: int | None, hi: int | None) -> bool:
    return (lo is None or tick >= lo) and (hi is None or tick <= hi)


def filter_states(
    states: list[dict[str, Any]],
    *,
    lo: int | None = None,
    hi: int | None = None,
    crew: str | None = None,
    room: str | None = None,
) -> list[dict[str, Any]]:
    out = []
    for state in states:
        if not in_range(state["tick"], lo, hi):
            continue
        if crew is not None and crew not in state.get("crew", {}):
            continue
        if room is not None:
            here = any(
                c.get("room") == room for c in state.get("crew", {}).values()
            )
            alien_here = state.get("alien", {}).get("room") == room
            if not (here or alien_here):
                continue
        out.append(state)
    return out


# --- R4/R6: the summary ----------------------------------------------------


def summarise(path: Path) -> str:
    """R4 + R6. A run in a page: events in prose, with tick numbers.

    This is the thing meant to be pasted whole. Order outcomes (R6) are paired
    to their action by crew + type + target, taking the first terminal result
    that follows the action line - IN_TRANSIT is not an answer, it means "still
    walking", so it is skipped rather than reported as what happened.
    """
    states = resolve(path)
    notes = events(path)
    lines: list[str] = []

    if not states:
        return "(empty log)"

    # Deaths: the moment `alive` goes False, once per crew member. Seeded from
    # the first recorded state without narrating it - the opening death is a
    # scenario premise the player already saw, not an event mid-run.
    was_alive: dict[str, bool] = {
        cid: row.get("alive", True) for cid, row in states[0].get("crew", {}).items()
    }
    for state in states[1:]:
        for cid, row in state.get("crew", {}).items():
            alive = row.get("alive", was_alive.get(cid, True))
            if was_alive.get(cid, True) and not alive:
                lines.append(f"tick {state['tick']:5d}  {cid} died")
            was_alive[cid] = alive

    # The Alien changing deck-adjacent rooms is too frequent to narrate; what
    # is worth a line is it changing state - dying, or being revealed absent.
    alien_alive = True
    for state in states:
        alien = state.get("alien")
        if alien is not None and alien_alive and not alien.get("alive", True):
            lines.append(f"tick {state['tick']:5d}  the Alien died")
            alien_alive = False

    # Fires and alarms: report onset, not every tick they persist.
    seen_fire: set[str] = set()
    seen_alarm: set[str] = set()
    for state in states:
        for room in state.get("fire", {}):
            if room not in seen_fire:
                lines.append(f"tick {state['tick']:5d}  fire broke out in {room}")
                seen_fire.add(room)
        for room in state.get("alarm", {}):
            if room not in seen_alarm:
                lines.append(
                    f"tick {state['tick']:5d}  the damage alarm sounded in {room}"
                )
                seen_alarm.add(room)

    # Notices, verbatim, once per distinct appearance.
    last_notice = None
    for state in states:
        notice = state.get("notice")
        if notice and notice != last_notice:
            lines.append(f"tick {state['tick']:5d}  notice: {notice}")
        last_notice = notice

    # Win route / phase change.
    last_phase = states[0].get("phase")
    for state in states:
        phase = state.get("phase", last_phase)
        if phase != last_phase:
            route = state.get("win_route")
            suffix = f" ({route})" if route else ""
            lines.append(f"tick {state['tick']:5d}  phase -> {phase}{suffix}")
        last_phase = phase

    # Orders, paired with their outcome (R6).
    actions = [n for n in notes if n["event"] == "action" and n.get("order")]
    outcomes = [n for n in notes if n["event"] == "outcome"]
    used = [False] * len(outcomes)
    for action in actions:
        order = action["order"]
        crew_id, kind, target = action["selected"], order["type"], order.get("target")
        result = None
        for i, out in enumerate(outcomes):
            if used[i]:
                continue
            if out["crew"] != crew_id or out["type"] != kind:
                continue
            if out.get("target") != target:
                continue
            if out["result"] == "IN_TRANSIT":
                continue  # not an answer - still walking
            used[i] = True
            result = out["result"]
            break
        verb = target or ""
        outcome_text = f" -> {result}" if result else " -> (unresolved in this log)"
        lines.append(
            f"tick {action['tick']:5d}  {crew_id}: {kind} {verb}{outcome_text}"
        )

    # Developer interference (P-3): must appear, and near the top, because it
    # changes what the rest of the summary is evidence *of*.
    dev = [n for n in notes if n["event"] == "dev"]
    if dev:
        lines.insert(0, "** this run was altered by developer keys - see below **")
        for n in dev:
            lines.append(f"          dev: {n.get('change')}")

    lines.sort(key=lambda ln: (
        0 if ln.startswith("**") else 1,
        int(ln.split()[1]) if ln.strip() and ln.split()[0] == "tick" else -1,
    ))
    header = (
        f"{path.name}: ticks {states[0]['tick']}-{states[-1]['tick']} "
        f"({len(states)} recorded), {len(actions)} orders given\n"
    )
    return header + ("\n".join(lines) if lines else "(nothing notable happened)")


# --- CLI --------------------------------------------------------------------


def _print_state(state: dict[str, Any]) -> None:
    print(json.dumps(state, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("log", type=Path, nargs="?", help="the .jsonl session file")
    parser.add_argument("--legend", action="store_true", help="print the field legend and exit")
    parser.add_argument("--summary", action="store_true", help="a whole run in a page (R4/R6)")
    parser.add_argument("--from", dest="frm", help="start tick, or 5m/90s/1h")
    parser.add_argument("--to", help="end tick, or 5m/90s/1h")
    parser.add_argument("--around", help="centre tick, or 5m/90s/1h")
    parser.add_argument("--window", type=int, default=20, help="ticks each side of --around")
    parser.add_argument("--crew", help="only states this crew member appears in")
    parser.add_argument("--room", help="only states involving this room")
    args = parser.parse_args(argv)

    if args.legend:
        print(LEGEND)
        return 0

    if args.log is None:
        parser.error("a log file is required unless --legend is given")
    if not args.log.exists():
        print(f"replay: no such file: {args.log}", file=sys.stderr)
        return 2

    if args.summary:
        print(summarise(args.log))
        return 0

    lo = hi = None
    if args.around is not None:
        centre = parse_offset(args.around)
        lo, hi = centre - args.window, centre + args.window
    else:
        if args.frm is not None:
            lo = parse_offset(args.frm)
        if args.to is not None:
            hi = parse_offset(args.to)

    states = filter_states(
        resolve(args.log), lo=lo, hi=hi, crew=args.crew, room=args.room
    )
    for state in states:
        _print_state(state)
    if not states:
        print("(no ticks matched)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
