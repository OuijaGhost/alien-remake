"""Command-line interface for ``alientools``.

This is the *only* module that touches stdout / process exit codes; everything
else returns data and raises on error. Subcommands (``inspect``, ``decode``,
``dir``, ``extract``, ``disasm``) are added one at a time and wired
into :func:`build_parser`. For now the package exposes just the ``--smoke``
self-check that the Definition of Done runs on every change.

Contract:
- ``python -m alientools --smoke`` runs an offline self-check and exits 0.
- ``main`` never reads or writes the source ``.nib`` and never touches the
  network; the smoke check is pure (see the invariants in README).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pathlib import Path

from . import __version__, cbmdos, charset, codemap, d64, gamedata, gcr, loader, nib
from . import diskimage
from .m6502 import disasm as m6502

PROG = "alientools"

# Default input: the source nibble dump shipped in the project root. Subcommands
# fall back to this when no path is given (see README -> Which disk image).
DEFAULT_NIB = "Alien (USA, Europe).nib"

# Default output directory for derived artefacts (all generated output goes here).
DEFAULT_OUT = "out"


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser.

    Subcommands register themselves onto the returned ``subparsers`` as they
    ship; keeping the structure here means a new subcommand is one parser plus
    one dispatch branch and nothing else.
    """
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Toolkit for decoding and disassembling the Commodore 64 game "
            "'Alien' from its raw 1541 GCR nibble dump (offline, read-only)."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} {__version__}",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="run the offline self-check (no network, no writes) and exit 0",
    )
    # Subparsers exist now so a new subcommand is only a parser + a dispatch
    # branch. `required=False` because `--smoke` (and bare invocation) are valid
    # without a subcommand.
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = False

    # inspect: parse the MNIB container and print its track/density layout.
    p_inspect = subparsers.add_parser(
        "inspect",
        help="print the MNIB header and per-track density layout (read-only)",
    )
    p_inspect.add_argument(
        "image",
        nargs="?",
        default=DEFAULT_NIB,
        help=f"path to a .nib, .g64 or .d64 image (default: {DEFAULT_NIB!r})",
    )

    # decode: GCR-decode each track to logical sectors and report checksums.
    p_decode = subparsers.add_parser(
        "decode",
        help="GCR-decode tracks to sectors; report good/bad/missing per track",
    )
    p_decode.add_argument(
        "image",
        nargs="?",
        default=DEFAULT_NIB,
        help=f"path to a .nib, .g64 or .d64 image (default: {DEFAULT_NIB!r})",
    )

    # dir: reconstruct the CBM-DOS directory (track 18) and list files.
    p_dir = subparsers.add_parser(
        "dir",
        help="list the CBM-DOS directory (read-only)",
    )
    p_dir.add_argument(
        "image",
        nargs="?",
        default=DEFAULT_NIB,
        help=f"path to a .nib, .g64 or .d64 image (default: {DEFAULT_NIB!r})",
    )

    # extract: export the .d64 and extract the CBM-DOS files to out/.
    p_extract = subparsers.add_parser(
        "extract",
        help="export a .d64 image and extract the CBM-DOS files to out/",
    )
    p_extract.add_argument(
        "image",
        nargs="?",
        default=DEFAULT_NIB,
        help=f"path to a .nib, .g64 or .d64 image (default: {DEFAULT_NIB!r})",
    )
    p_extract.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"output directory for derived artefacts (default: {DEFAULT_OUT!r})",
    )

    # disasm: 6502-disassemble a PRG (or raw region), or the disk's boot file.
    p_disasm = subparsers.add_parser(
        "disasm",
        help="disassemble a PRG to 6502 assembly under out/ (--boot for the loader)",
    )
    p_disasm.add_argument(
        "file",
        nargs="?",
        help="path to a PRG/binary to disassemble (omit with --boot)",
    )
    p_disasm.add_argument(
        "--boot",
        nargs="?",
        const=DEFAULT_NIB,
        metavar="IMAGE",
        help=(
            "disassemble the disk's first-loaded file; optional .nib path "
            f"(default: {DEFAULT_NIB!r}). Also writes a load-chain report."
        ),
    )
    p_disasm.add_argument(
        "--raw",
        metavar="ORIGIN",
        help="treat the input as a raw memory region at ORIGIN (hex, e.g. C000) "
        "instead of a PRG with a 2-byte load header",
    )
    p_disasm.add_argument(
        "--illegal",
        action="store_true",
        help="decode the undocumented opcode set (otherwise emitted as .byte)",
    )
    p_disasm.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"output directory for the listing (default: {DEFAULT_OUT!r})",
    )

    # chars: extract ALIEN's own C64 charset + sprites as derived PNGs (SG).
    p_chars = subparsers.add_parser(
        "chars",
        help="extract the game's C64 character set + sprites to out/ (derived PNGs)",
    )
    p_chars.add_argument(
        "image",
        nargs="?",
        default=DEFAULT_NIB,
        help=f"path to a .nib, .g64 or .d64 image (default: {DEFAULT_NIB!r})",
    )
    p_chars.add_argument(
        "--prg",
        metavar="PATH",
        help="extract from an already-extracted ALIEN PRG instead of the disk",
    )
    p_chars.add_argument(
        "--scale",
        type=int,
        default=1,
        help="nearest-neighbour pixel scale for the PNGs (default: 1)",
    )
    p_chars.add_argument(
        "--multicolor",
        action="store_true",
        help=(
            "also write out/sprites_multicolor.png, decoding every sprite as a "
            "C64 multicolor sprite (12 double-width bit-pair pixels per row). "
            "Needed for sprites the hi-res decode renders as noise, e.g. the "
            "title screen's alien egg (R-03)."
        ),
    )
    p_chars.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"output directory for derived artefacts (default: {DEFAULT_OUT!r})",
    )

    # gamedata: decode the real game tables (map/items/crew/timing) from the PRG.
    p_gamedata = subparsers.add_parser(
        "gamedata",
        help="decode the game's own data tables (rooms/items/crew) from ALIEN.prg",
    )
    p_gamedata.add_argument(
        "prg",
        nargs="?",
        default=str(
            Path(DEFAULT_OUT) / "Alien (USA, Europe)_files" / "ALIEN.prg"
        ),
        help="path to the extracted ALIEN.prg (default: the `extract` output)",
    )
    p_gamedata.add_argument(
        "--emit-python",
        metavar="PATH",
        nargs="?",
        const="src/alien_remake/core/gamedata_snapshot.py",
        help=(
            "write the decoded tables as a generated Python module for the "
            "remake (default path: the remake's gamedata_snapshot.py)"
        ),
    )

    # codemap: recursive-descent trace of ALIEN.prg -> a fully classified
    # (code vs data) annotated disassembly; the "full disassembly" deliverable.
    p_codemap = subparsers.add_parser(
        "codemap",
        help="trace ALIEN.prg control flow; emit a code/data-classified listing",
    )
    p_codemap.add_argument(
        "prg",
        nargs="?",
        default=str(Path(DEFAULT_OUT) / "Alien (USA, Europe)_files" / "ALIEN.prg"),
        help="path to the extracted ALIEN.prg (default: the `extract` output)",
    )
    p_codemap.add_argument(
        "--sym",
        metavar="PATH",
        default="docs/re/alien.sym",
        help="VICE label file to apply to the listing (default: docs/re/alien.sym; "
        "labels are cosmetic — coverage does not depend on them)",
    )
    p_codemap.add_argument(
        "--out",
        metavar="PATH",
        nargs="?",
        const="docs/re/ALIEN.annotated.asm",
        help="write the annotated listing to PATH "
        "(default path: docs/re/ALIEN.annotated.asm)",
    )
    p_codemap.add_argument(
        "--report",
        action="store_true",
        help="print only the byte-class census (no listing written)",
    )

    return parser


def run_smoke() -> int:
    """Offline self-check: prove the package imports and the CLI is wired.

    Deliberately pure — it does not open the source ``.nib``, write anything, or
    touch the network. Returns 0 on success so it can gate every change.
    """
    # ASCII only: the CLI must not assume a UTF-8 console (legacy Windows code
    # pages would raise UnicodeEncodeError and fail the smoke gate).
    print(f"{PROG} {__version__} - smoke OK (offline, read-only)")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 = success)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.smoke:
        return run_smoke()

    if args.command is None:
        # No subcommand and no --smoke: show help. Treated as a usage issue.
        parser.print_help(sys.stderr)
        return 2

    if args.command == "inspect":
        return _cmd_inspect(args.image)

    if args.command == "decode":
        return _cmd_decode(args.image)

    if args.command == "dir":
        return _cmd_dir(args.image)

    if args.command == "extract":
        return _cmd_extract(args.image, args.out)

    if args.command == "disasm":
        return _cmd_disasm(args)

    if args.command == "chars":
        return _cmd_chars(args)

    if args.command == "gamedata":
        return _cmd_gamedata(args)

    if args.command == "codemap":
        return _cmd_codemap(args)

    # Defensive: argparse only accepts registered subcommands, so this is
    # unreachable in practice.
    parser.error(f"unknown command: {args.command!r}")
    return 2  # pragma: no cover - argparse.error raises SystemExit


def _open(image_path: str) -> diskimage.DiskImage | int:
    """Load any supported image, or print why not and return an exit code."""
    try:
        return diskimage.load(image_path)
    except FileNotFoundError:
        print(f"{PROG}: file not found: {image_path}", file=sys.stderr)
        return 2
    except (nib.NibError, diskimage.ImageError) as exc:
        print(f"{PROG}: cannot read image: {exc}", file=sys.stderr)
        return 1


def _cmd_inspect(image_path: str) -> int:
    """Print the container's track/density layout. Read-only."""
    image = _open(image_path)
    if isinstance(image, int):
        return image
    if image.container is not None:
        print(nib.format_inspect(image.container))
        return 0
    # A .d64 has no container to inspect and a .g64 has no MNIB header, so
    # report the geometry that does exist rather than pretending.
    print(f"File:    {image.path}")
    print(f"Format:  {image.kind.upper()}")
    print(f"Tracks:  {len(image.decoded)}")
    if not image.carries_protection:
        print("Note:    a .d64 stores only what a 1541 could read normally, so")
        print("         this disk's copy protection is not in the file at all.")
    return 0


def _cmd_decode(image_path: str) -> int:
    """Decode to logical sectors and print a per-track report. Read-only."""
    image = _open(image_path)
    if isinstance(image, int):
        return image
    if image.container is not None:
        print(gcr.format_decode(image.container))
        return 0
    print(gcr.format_tracks(image.decoded, source=image.path))
    return 0


def _cmd_dir(image_path: str) -> int:
    """Reconstruct and print the CBM-DOS directory. Read-only."""
    image = _open(image_path)
    if isinstance(image, int):
        return image
    smap = cbmdos.build_sector_map(image.decoded)
    try:
        print(cbmdos.format_dir(smap))
    except cbmdos.CbmDosError as exc:
        print(f"{PROG}: cannot read directory: {exc}", file=sys.stderr)
        return 1
    return 0


def _cmd_extract(image_path: str, out_dir: str) -> int:
    """Export the ``.d64`` and extract the CBM-DOS files under ``out_dir``."""
    image = _open(image_path)
    if isinstance(image, int):
        return image

    decoded = image.decoded
    out = Path(out_dir)
    stem = Path(image_path).stem

    # Derived artefact 1: the assembled .d64 image.
    d64_image = d64.assemble(decoded)
    d64_path = d64.export(d64_image, out / f"{stem}.d64")
    print(d64.format_assembly(d64_image))
    print(f"Wrote:   {d64_path}")

    # Derived artefact 2: the extracted CBM-DOS files.
    smap = cbmdos.build_sector_map(decoded)
    try:
        entries = cbmdos.read_directory(smap)
    except cbmdos.CbmDosError as exc:
        print(f"{PROG}: cannot read directory: {exc}", file=sys.stderr)
        return 1

    files_dir = out / f"{stem}_files"
    files_dir.mkdir(parents=True, exist_ok=True)
    print(f"Files:   {len(entries)} in directory")
    for entry in entries:
        data, complete = cbmdos.extract_file(smap, entry)
        dest = files_dir / entry.filename()
        dest.write_bytes(data)
        flag = "" if complete else "  (PARTIAL - chain incomplete)"
        print(f"  {entry.type_name} {entry.name_text:<18} {len(data):>6} bytes -> {dest.name}{flag}")
    return 0


def _disasm_summary(load: int, instrs: list[m6502.Instruction]) -> str:
    """One-line summary of a disassembly: load address + item counts."""
    data_items = sum(1 for ins in instrs if ins.is_data)
    code_items = len(instrs) - data_items
    return (
        f"load ${load:04X}  {code_items} instructions, "
        f"{data_items} data byte(s)"
    )


def _write_listing(instrs: list[m6502.Instruction], dest: Path) -> None:
    """Render and write a listing as ASCII (the CLI must not assume UTF-8)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(m6502.format_listing(instrs) + "\n", encoding="ascii")


def _cmd_disasm(args: argparse.Namespace) -> int:
    """Disassemble a PRG/raw region, or the disk's boot file, to ``out/``."""
    out_dir = Path(args.out)
    if args.boot is not None:
        return _disasm_boot(args.boot, out_dir, illegal=args.illegal)
    if args.file is None:
        print(f"{PROG}: disasm needs a FILE argument or --boot", file=sys.stderr)
        return 2
    return _disasm_file(args.file, out_dir, raw=args.raw, illegal=args.illegal)


def _disasm_file(
    path: str, out_dir: Path, *, raw: str | None, illegal: bool
) -> int:
    """Disassemble a PRG (or, with ``raw``, a raw region at a hex origin)."""
    src = Path(path)
    try:
        data = src.read_bytes()
    except FileNotFoundError:
        print(f"{PROG}: file not found: {path}", file=sys.stderr)
        return 2

    if raw is not None:
        try:
            origin = int(raw, 16)
        except ValueError:
            print(f"{PROG}: --raw origin not hex: {raw!r}", file=sys.stderr)
            return 2
        if not 0 <= origin <= 0xFFFF:
            print(f"{PROG}: --raw origin out of 16-bit range: {raw!r}", file=sys.stderr)
            return 2
        load = origin
        instrs = m6502.disassemble_memory(data, origin, illegal=illegal)
    else:
        try:
            load, instrs = m6502.disassemble_prg(data, illegal=illegal)
        except ValueError as exc:
            print(f"{PROG}: not a valid PRG: {exc}", file=sys.stderr)
            return 1

    dest = out_dir / f"{src.stem}.asm"
    _write_listing(instrs, dest)
    print(_disasm_summary(load, instrs))
    print(f"Wrote:   {dest}")
    return 0


def _disasm_boot(image_path: str, out_dir: Path, *, illegal: bool) -> int:
    """Extract the disk's first-loaded file, disassemble it, write a load report."""
    image = _open(image_path)
    if isinstance(image, int):
        return image

    decoded = image.decoded
    try:
        boot = loader.boot_file(decoded)
        chain = loader.format_load_chain(decoded)
    except cbmdos.CbmDosError as exc:
        print(f"{PROG}: cannot read loader: {exc}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    # Load-chain notes (descriptive; the interpretation lives in the disassembly docs).
    notes_path = out_dir / "load_chain.txt"
    notes_path.write_text(chain + "\n", encoding="ascii")
    print(chain)
    print(f"\nWrote:   {notes_path}")

    # Raw disassembly of the boot file itself.
    if boot.is_prg:
        load, instrs = m6502.disassemble_prg(boot.data, illegal=illegal)
    else:
        load, instrs = 0, m6502.disassemble_memory(boot.data, 0, illegal=illegal)
    dest = out_dir / f"{boot.entry.filename().rsplit('.', 1)[0]}.asm"
    _write_listing(instrs, dest)
    note = "" if boot.complete else "  (PARTIAL - chain incomplete)"
    print(f"Boot:    {boot.entry.name_text} ({boot.entry.type_name}){note}")
    print(_disasm_summary(load, instrs))
    print(f"Wrote:   {dest}")
    return 0


def _alien_prg_from_nib(image_path: str) -> bytes:
    """Decode the disk and return the ALIEN PRG bytes (load $2000). Read-only."""
    decoded = diskimage.load(image_path).decoded
    for f in loader.load_directory(decoded):
        if f.entry.name_text.strip() == "ALIEN" and f.load_address == charset.CHARSET_LOAD:
            return f.data
    raise charset.CharsetError("no ALIEN PRG (load $2000) in the directory")


def _cmd_chars(args: argparse.Namespace) -> int:
    """Extract ALIEN's charset + sprites to ``out/`` as derived PNGs (SG)."""
    try:
        if args.prg is not None:
            prg = Path(args.prg).read_bytes()
        else:
            prg = _alien_prg_from_nib(args.image)
    except FileNotFoundError as exc:
        print(f"{PROG}: file not found: {exc.filename}", file=sys.stderr)
        return 2
    except nib.NibError as exc:
        print(f"{PROG}: not a valid MNIB image: {exc}", file=sys.stderr)
        return 1
    except (cbmdos.CbmDosError, charset.CharsetError) as exc:
        print(f"{PROG}: cannot locate ALIEN graphics: {exc}", file=sys.stderr)
        return 1

    try:
        assets = charset.decode_assets(prg)
    except charset.CharsetError as exc:
        print(f"{PROG}: not the ALIEN graphics region: {exc}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    scale = max(1, args.scale)

    region_path = out / "charset.bin"
    region_path.write_bytes(assets.region)
    chars_path = out / "charset.png"
    chars_path.write_bytes(charset.charset_png(assets.glyphs, scale=scale))
    sprites_path = out / "sprites.png"
    sprites_path.write_bytes(charset.sprite_sheet_png(assets.sprites, scale=scale))
    mc_path = None
    if getattr(args, "multicolor", False):
        mc_sprites = charset.decode_sprites_multicolor(assets.region)
        mc_path = out / "sprites_multicolor.png"
        mc_path.write_bytes(
            charset.sprite_sheet_multicolor_png(mc_sprites, scale=scale)
        )

    print(f"Region:  ${charset.CHARSET_LOAD:04X}-"
          f"${charset.CHARSET_LOAD + charset.REGION_BYTES - 1:04X} "
          f"({len(assets.region)} bytes)")
    print(f"Charset: {len(assets.glyphs)} glyphs {charset.GLYPH_W}x{charset.GLYPH_H}")
    print(f"Sprites: {len(assets.sprites)} slots {charset.SPRITE_W}x{charset.SPRITE_H}")
    print(f"Wrote:   {region_path}")
    print(f"Wrote:   {chars_path}")
    print(f"Wrote:   {sprites_path}")
    if mc_path is not None:
        print(f"Wrote:   {mc_path}")
    return 0


def _cmd_gamedata(args: argparse.Namespace) -> int:
    """Decode the real game tables from ALIEN.prg; optionally emit the remake's
    generated snapshot module (a derived artifact — never hand-edited)."""
    prg_path = Path(args.prg)
    if not prg_path.exists():
        print(
            f"{PROG}: {prg_path} not found - run "
            f"`python -m alientools extract` first",
            file=sys.stderr,
        )
        return 1
    try:
        gd = gamedata.load_gamedata(prg_path)
    except gamedata.GamedataError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return 1

    if args.emit_python:
        out_path = Path(args.emit_python)
        out_path.write_text(gamedata.emit_python(gd), encoding="utf-8", newline="\n")
        print(f"Wrote:   {out_path}")
        return 0

    print(gamedata.format_report(gd))
    return 0


def _cmd_codemap(args: argparse.Namespace) -> int:
    """Trace ALIEN.prg and emit a code/data-classified disassembly (derived)."""
    prg_path = Path(args.prg)
    if not prg_path.exists():
        print(
            f"{PROG}: {prg_path} not found - run "
            f"`python -m alientools extract` first",
            file=sys.stderr,
        )
        return 1
    try:
        load, body, cm = codemap.build_codemap(prg_path.read_bytes())
    except codemap.CodemapError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return 1

    census = codemap.classify(load, body, cm)
    print(codemap.format_census(census, load, load + len(body)))

    if args.report:
        return 0

    # Labels are cosmetic; a missing sym file is not an error.
    sym_path = Path(args.sym)
    labels = (
        codemap.load_symbols(sym_path.read_text(encoding="utf-8"))
        if sym_path.exists()
        else {}
    )
    listing = codemap.emit_listing(load, body, cm, labels)
    dest = Path(args.out) if args.out else Path("docs/re/ALIEN.annotated.asm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(listing + "\n", encoding="utf-8", newline="\n")
    print(f"Labels:  {len(labels)} applied from {sym_path}" if labels
          else f"Labels:  none ({sym_path} not found)")
    print(f"Wrote:   {dest}")
    return 0
