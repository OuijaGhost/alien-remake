"""Tests for identify the boot/first-loaded file and the ``disasm`` subcommand.

A hand-built synthetic disk (BAM + one directory sector + a small PRG file whose
body is a known 6502 sequence) checks boot-file identification, the load-address
decode and the load-chain report. The ``disasm`` subcommand is exercised in PRG,
raw and boot modes, plus its error paths, against a temp file and the real
source ``.nib``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alientools import cbmdos, cli, gcr, loader, nib

import needs                                       # noqa: E402

REAL_NIB = Path(__file__).resolve().parent.parent / "Alien (USA, Europe).nib"

# A tiny, recognisable 6502 program: LDA #$01 ; RTS  -> bytes A9 01 60.
CODE = b"\xA9\x01\x60"
# As a CBM PRG it is preceded by a 2-byte little-endian load address ($C000).
PRG = b"\x00\xC0" + CODE


def _sec(track: int, sector: int, data: bytes) -> gcr.SectorResult:
    return gcr.SectorResult(
        track=track,
        sector=sector,
        header_ok=True,
        data_ok=True,
        data=data.ljust(256, b"\x00")[:256],
    )


def _track(track_no: int, sectors: list[gcr.SectorResult]) -> gcr.TrackDecode:
    return gcr.TrackDecode(
        halftrack=track_no * 2,
        density=0,
        expected=len(sectors),
        sectors=tuple(sectors),
        sync_count=0,
        flag_names=(),
    )


def _bam(name: bytes) -> bytes:
    data = bytearray(256)
    data[0], data[1] = 18, 1  # first directory sector
    data[2] = 0x41
    data[144 : 144 + len(name)] = name
    for i in range(144 + len(name), 160):
        data[i] = cbmdos.PAD
    data[162:164] = b"AB"
    data[165:167] = b"2A"
    return bytes(data)


def _dir_entry(name: bytes, start: tuple[int, int], size: int) -> bytes:
    e = bytearray(32)
    e[2] = 2 | cbmdos.TYPE_CLOSED  # PRG, closed
    e[3], e[4] = start
    e[5 : 5 + len(name)] = name
    for i in range(5 + len(name), 21):
        e[i] = cbmdos.PAD
    e[28] = size & 0xFF
    e[29] = (size >> 8) & 0xFF
    return bytes(e)


def _synthetic_image() -> loader.DecodedImage:
    """A two-track decode: directory on track 18, a one-sector PRG on track 1."""
    dir_data = bytearray(256)
    dir_data[0], dir_data[1] = 0, 0  # no further directory sectors
    dir_data[0:32] = _dir_entry(b"BOOT", (1, 0), 1)
    # PRG file: one final sector carrying the 5 PRG bytes.
    fsec = bytearray(256)
    fsec[0], fsec[1] = 0, len(PRG) + 1  # last sector; last used byte index
    fsec[2 : 2 + len(PRG)] = PRG
    t18 = _track(18, [_sec(18, 0, _bam(b"SYNTH")), _sec(18, 1, bytes(dir_data))])
    t1 = _track(1, [_sec(1, 0, bytes(fsec))])
    return (t1, t18)


# --- the loader module --------------------------------------------------------


def test_boot_file_is_first_directory_entry() -> None:
    boot = loader.boot_file(_synthetic_image())
    assert boot.entry.name_text == "BOOT"
    assert boot.is_prg
    assert boot.load_address == 0xC000
    assert boot.body_len == len(CODE)
    assert boot.last_address == 0xC000 + len(CODE) - 1
    assert boot.complete
    assert boot.data == PRG


def test_load_directory_keeps_order() -> None:
    files = loader.load_directory(_synthetic_image())
    assert [f.entry.name_text for f in files] == ["BOOT"]


def test_format_load_chain_describes_boot() -> None:
    text = loader.format_load_chain(_synthetic_image())
    assert "SYNTH" in text
    assert "BOOT" in text
    assert "$C000" in text
    assert "loaded first" in text
    # It defers inter-file order to the disassembly rather than asserting it.
    assert "interpreted from the disassembly" in text


def test_boot_file_empty_directory_raises() -> None:
    # A disk whose directory sector has no used entries -> no boot file.
    empty_dir = bytearray(256)
    empty_dir[0], empty_dir[1] = 0, 0
    img = (_track(18, [_sec(18, 0, _bam(b"EMPTY")), _sec(18, 1, bytes(empty_dir))]),)
    with pytest.raises(cbmdos.CbmDosError):
        loader.boot_file(img)


# --- the disasm subcommand ----------------------------------------------------


def test_disasm_prg_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "boot.prg"
    src.write_bytes(PRG)
    rc = cli.main(["disasm", str(src), "--out", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "load $C000" in out
    asm = (tmp_path / "boot.asm").read_text(encoding="ascii")
    assert "LDA #$01" in asm
    assert "RTS" in asm


def test_disasm_raw_region(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "code.bin"
    src.write_bytes(CODE)  # no load header
    rc = cli.main(["disasm", str(src), "--raw", "C000", "--out", str(tmp_path)])
    assert rc == 0
    asm = (tmp_path / "code.asm").read_text(encoding="ascii")
    # First byte is decoded as an instruction at the given origin, not skipped.
    assert asm.startswith("C000")
    assert "LDA #$01" in asm


def test_disasm_needs_file_or_boot(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["disasm"])
    assert rc == 2
    assert "FILE" in capsys.readouterr().err


def test_disasm_missing_file_returns_2(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["disasm", "no-such-file.prg"])
    assert rc == 2
    assert "not found" in capsys.readouterr().err


def test_disasm_too_short_prg_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "tiny.prg"
    src.write_bytes(b"\x00")  # only one byte: no load header
    rc = cli.main(["disasm", str(src), "--out", str(tmp_path)])
    assert rc == 1
    assert "not a valid PRG" in capsys.readouterr().err


def test_disasm_bad_raw_origin_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "code.bin"
    src.write_bytes(CODE)
    rc = cli.main(["disasm", str(src), "--raw", "ZZZZ", "--out", str(tmp_path)])
    assert rc == 2
    assert "not hex" in capsys.readouterr().err


# --- the real source image ----------------------------------------------------


def test_real_nib_boot_is_first_prg() -> None:
    needs.need(needs.NIB)
    decoded = gcr.decode_image(nib.read_nib(REAL_NIB))
    boot = loader.boot_file(decoded)
    smap = cbmdos.build_sector_map(decoded)
    first = cbmdos.read_directory(smap)[0]
    assert boot.entry.name_text == first.name_text  # boot == first dir entry
    assert boot.is_prg and boot.load_address is not None
    assert boot.complete


def test_disasm_boot_on_real_nib(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    needs.need(needs.NIB)
    rc = cli.main(["disasm", "--boot", str(REAL_NIB), "--out", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "BOOT (loaded first)" in out
    assert "OCG0549" in out  # the disk name appears in the load-chain report
    # The load-chain notes and a non-empty boot disassembly are both written.
    assert (tmp_path / "load_chain.txt").read_text(encoding="ascii").strip()
    asms = list(tmp_path.glob("*.asm"))
    assert len(asms) == 1 and asms[0].read_text(encoding="ascii").strip()
