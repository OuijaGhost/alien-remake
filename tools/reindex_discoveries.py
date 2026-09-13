"""Regenerate `DISCOVERIES.md`'s index table (D-192).

    python tools/reindex_discoveries.py

Run this after adding a discovery. `tests/test_fv3_drift_guards.py::
test_the_discovery_index_covers_every_entry` fails until you do, on purpose: an
index that has quietly fallen behind the body is worse than no index, because
it gets read *instead of* the body.

Rewrites only the table between the `| # | Date | Finding |` header and the
following `---`. Everything else in the file, including the prose above the
index, is left exactly as it was.

Two parsing details that are easy to get wrong, both learned by getting them
wrong:

- ids come in two forms. `D-nnn` is the historical one; **`DISC-nnn` is what
  new entries use** (D-192/D-195), because `DECISIONS.md` numbered its own
  entries `D-001`.. in the identical format and seven ids ended up naming two
  findings each. Both are matched here, and both sort on the number alone so
  the table stays in one sequence.
- ids may carry a **letter suffix** (`D-080b`), so the pattern is
  `D-\\d+[a-z]?`. With `D-\\d+`, `D-080b` silently parses as `D-080` and shows
  up as a phantom duplicate.
- the date is written three different ways across the register's lifetime —
  `**Date:** …`, `**Found:** …`, and a bare leading `*2026-08-06. …*` — so all
  three are tried before giving up.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "docs" / "re" / "DISCOVERIES.md"

HEADING = re.compile(r"^## ((?:DISC-|D-)\d+[a-z]?)\s*(.*)$", re.M)
DATE_PATTERNS = (
    r"\*\*(?:Date|Found)(?:/\w+)?:\*\*\s*(\d{4}-\d{2}-\d{2})",
    r"^\*(\d{4}-\d{2}-\d{2})",
    r"(\d{4}-\d{2}-\d{2})",
)


def date_of(text: str, pos: int) -> str:
    """The entry's date, however that entry happened to write it."""
    head = text[pos : pos + 500]
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, head, re.M)
        if match:
            return match.group(1)
    return "—"


def anchor_for(num: str, title: str) -> str:
    """GitHub's heading anchor: lowercased, non-alphanumerics collapsed to `-`."""
    return "#" + re.sub(r"[^a-z0-9]+", "-", f"{num} {title}".lower()).strip("-")


def sort_key(num: str) -> tuple[int, str]:
    match = re.match(r"(?:DISC-|D-)(\d+)", num)
    assert match is not None
    return int(match.group(1)), num


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    entries = [
        (m.group(1), m.group(2).strip(" —-"), m.start()) for m in HEADING.finditer(text)
    ]
    if not entries:
        print("no ## D-nnn headings found — has the format changed?", file=sys.stderr)
        return 1

    undated = [num for num, _, pos in entries if date_of(text, pos) == "—"]
    if undated:
        print(f"no parseable date for: {undated}", file=sys.stderr)
        return 1

    rows = "\n".join(
        f"| [{num}]({anchor_for(num, title)}) | {date_of(text, pos)} | {title} |"
        for num, title, pos in sorted(entries, key=lambda e: sort_key(e[0]))
    )
    header = "| # | Date | Finding |\n|---|---|---|\n"
    start = text.index(header)
    end = text.index("\n---\n", start)

    lo, hi = entries[0][0], max((e[0] for e in entries), key=sort_key)
    old_count = re.search(r"^(\d+) entries, D-\d+\S* to D-\d+\S*", text, re.M)
    updated = text[:start] + header + rows + text[end:]
    if old_count:
        updated = updated.replace(
            old_count.group(0), f"{len(entries)} entries, {lo} to {hi}", 1
        )

    if updated == text:
        print(f"index already current ({len(entries)} entries)")
        return 0
    TARGET.write_text(updated, encoding="utf-8", newline="\n")
    print(f"index rewritten: {len(entries)} entries, {lo} to {hi}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
