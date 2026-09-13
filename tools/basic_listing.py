"""Detokenise the loader's BASIC programs into `out/MENU1_EXITO.bas.txt`.

    python tools/basic_listing.py

**Why this exists.** A clean flight from nothing but the `.nib` found the one
thing `--derive-assets` could not produce. `MENU1.prg` and `EXITO.prg` are
extracted as tokenised BASIC, and the *listing* — the readable form — is what
`test_fv3_frontend_capture.py` reads to check the instructions prompt takes its
colours from the loader's own `CHR$` codes. Nothing regenerated it, so a fresh
clone could not reproduce the test corpus and the `out/` guard failed rather
than skipped.

The format is the one the existing listing already used, because the tests match
against it: PETSCII control codes as `{n}`, one line per BASIC line, a banner
per program.

**This is not an interpretation.** Tokens `$80`-`$CB` are Commodore BASIC V2's
own keyword table, in order, and the mapping is a fact about the machine rather
than a reading of this game — which is why it can live in a tool rather than
needing a `[C]` citation against ALIEN's disassembly.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from alien_remake import assets  # noqa: E402

#: Commodore BASIC V2 keywords, token `$80` upward. The order is the ROM's.
TOKENS = (
    "END", "FOR", "NEXT", "DATA", "INPUT#", "INPUT", "DIM", "READ",
    "LET", "GOTO", "RUN", "IF", "RESTORE", "GOSUB", "RETURN", "REM",
    "STOP", "ON", "WAIT", "LOAD", "SAVE", "VERIFY", "DEF", "POKE",
    "PRINT#", "PRINT", "CONT", "LIST", "CLR", "CMD", "SYS", "OPEN",
    "CLOSE", "GET", "NEW", "TAB(", "TO", "FN", "SPC(", "THEN",
    "NOT", "STEP", "+", "-", "*", "/", "^", "AND",
    "OR", ">", "=", "<", "SGN", "INT", "ABS", "USR",
    "FRE", "POS", "SQR", "RND", "LOG", "EXP", "COS", "SIN",
    "TAN", "ATN", "PEEK", "LEN", "STR$", "VAL", "ASC", "CHR$",
    "LEFT$", "RIGHT$", "MID$", "GO",
)

#: PETSCII codes that are printable as themselves. Everything else inside a
#: string becomes `{n}` - which is what makes a colour change like `{158}`
#: visible in the listing at all, and is the whole reason the tests read this.
def _petscii(byte: int) -> str:
    if byte == 0x22:                       # the quote itself
        return '"'
    if 0x20 <= byte <= 0x5F:
        return chr(byte)
    if 0x60 <= byte <= 0x7E:
        return chr(byte).upper()
    return "{" + str(byte) + "}"


def _listing(data: bytes) -> tuple[str, int, int]:
    """One PRG to a listing: the text, the line count, and its load address.

    A BASIC program is a chain of lines - two bytes of "address of the next
    line" (which is why the chain ends at `$0000`), two of line number, then the
    tokenised text and a terminator.
    """
    load = data[0] | (data[1] << 8)
    text, count = _detokenise_body(data[2:])
    return text, count, load


def _detokenise_body(body: bytes) -> tuple[str, int]:
    """The line chain, minus the two-byte load address.

    `in_string` is the part that matters: inside quotes a byte over `$80` is a
    graphics character, not a keyword, and detokenising it would turn the
    loader's own screen art into words.
    """
    out: list[str] = []
    pos = 0
    while pos + 4 <= len(body):
        if (body[pos] | (body[pos + 1] << 8)) == 0:
            break
        number = body[pos + 2] | (body[pos + 3] << 8)
        pos += 4
        text: list[str] = []
        in_string = False
        while pos < len(body) and body[pos] != 0:
            byte = body[pos]
            if byte == 0x22:
                in_string = not in_string
                text.append('"')
            elif byte >= 0x80 and not in_string:
                index = byte - 0x80
                text.append(TOKENS[index] if index < len(TOKENS) else f"{{{byte}}}")
            else:
                text.append(_petscii(byte))
            pos += 1
        pos += 1
        out.append(f"{number} {''.join(text)}")
    return "\n".join(out), len(out)


OUT_NAME = "MENU1_EXITO.bas.txt"
PROGRAMS = ("MENU1.prg", "EXITO.prg")


def main() -> int:
    files = assets.find(assets.FILES_DIR)
    if files is None or not files.is_dir():
        print(
            "the loader's PRGs are not extracted yet. Run:\n"
            "    python -m alien_remake --derive-assets \"Alien (USA, Europe).nib\"",
            file=sys.stderr,
        )
        return 2

    chunks: list[str] = []
    for name in PROGRAMS:
        prg = files / name
        if not prg.is_file():
            print(f"missing {prg}", file=sys.stderr)
            return 2
        text, count, load = _listing(prg.read_bytes())
        chunks.append(
            f"===== {name}  (load ${load:04X}, {count} BASIC lines) =====\n{text}"
        )

    out = Path(assets.DERIVED_DIR) / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(chunks) + "\n", encoding="utf-8", newline="")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
