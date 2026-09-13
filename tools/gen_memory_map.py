"""Generate `docs/re/MEMORY_MAP.md` — every ROM address the remake cites.

Derived, never hand-edited. Run after changing citations:

    python tools/gen_memory_map.py

**Why this exists.** The remake's fidelity argument rests on ~345 `[C $addr]`
citations scattered through `src/alien_remake`, each tying a value or behaviour
to the routine it came from. That is the right place for them — a modder about
to change a line needs to know it is not arbitrary — but scattered is a poor
shape for two other jobs:

* looking an address up (which module relies on `$7569`? all of them?), and
* surviving a decision to thin the comments, which would otherwise take the
  provenance with it.

So this walks the source, pairs every cited address with its name from
`docs/re/alien.sym` and the labels in the annotated disassembly, and writes one
sorted table. It is a *reference*, not a source: the citations in the code stay
authoritative, and this file is regenerated from them.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "alien_remake"
SYM = ROOT / "docs" / "re" / "alien.sym"
ASM = ROOT / "docs" / "re" / "ALIEN.annotated.asm"
OUT = ROOT / "docs" / "re" / "MEMORY_MAP.md"

ADDR = re.compile(r"\$([0-9A-F]{4})\b")


def _symbol_names() -> dict[int, str]:
    """Address -> name, from the VICE symbol file and the listing's labels."""
    names: dict[int, str] = {}
    if SYM.exists():
        for line in SYM.read_text(encoding="utf-8").split("\n"):
            m = re.match(r"al C:([0-9a-fA-F]{4})\s+\.(\S+)", line.strip())
            if m:
                names[int(m.group(1), 16)] = m.group(2)
    if ASM.exists():
        pending: str | None = None
        for line in ASM.read_text(encoding="utf-8", errors="replace").split("\n"):
            label = re.match(r"^([a-z_][a-z_0-9]*):\s*$", line)
            if label:
                pending = label.group(1)
                continue
            if pending:
                at = re.match(r"^([0-9A-F]{4})\s", line)
                if at:
                    names.setdefault(int(at.group(1), 16), pending)
                pending = None
    return names


def _citations() -> dict[int, dict[str, list[int]]]:
    """Address -> {module: [line numbers]} for every mention in the package."""
    found: dict[int, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(SRC).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            for hit in ADDR.finditer(line):
                found[int(hit.group(1), 16)][rel].append(lineno)
    return found


def render() -> str:
    names = _symbol_names()
    cites = _citations()
    per_module: dict[str, set[int]] = defaultdict(set)
    for addr, mods in cites.items():
        for mod in mods:
            per_module[mod].add(addr)

    named = sum(1 for a in cites if a in names)
    out = [
        "# MEMORY_MAP.md — every ROM address the remake cites",
        "",
        "**Generated. Do not hand-edit** — run `python tools/gen_memory_map.py`.",
        "",
        "The remake's fidelity argument rests on citations tying each value or",
        "behaviour to the routine it came from. Those live in the source, where",
        "someone about to change a line will see them. This is the index: the same",
        "facts sorted by address, so you can ask *what relies on `$7569`?* without",
        "grepping, and so the provenance survives independently of the comments.",
        "",
        "Names come from `alien.sym` and the labels in `ALIEN.annotated.asm`; an",
        "address with no name is usually a data cell rather than a routine entry.",
        "",
        "| | |",
        "|---|---|",
        f"| distinct addresses cited | **{len(cites)}** |",
        f"| of those, named in the disassembly | **{named}** |",
        f"| modules carrying citations | **{len(per_module)}** |",
        "",
        "## By address",
        "",
        "| address | name | referenced from |",
        "|---|---|---|",
    ]
    for addr in sorted(cites):
        label = f"`{names[addr]}`" if addr in names else "—"
        where = "<br>".join(
            f"`{mod}`:{', '.join(str(n) for n in sorted(set(lines))[:6])}"
            + ("…" if len(set(lines)) > 6 else "")
            for mod, lines in sorted(cites[addr].items())
        )
        out.append(f"| `${addr:04X}` | {label} | {where} |")

    out += ["", "## By module", "",
            "How much of each module is anchored to the ROM.", "",
            "| module | distinct addresses |", "|---|---|"]
    for mod in sorted(per_module, key=lambda m: -len(per_module[m])):
        out.append(f"| `{mod}` | {len(per_module[mod])} |")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
