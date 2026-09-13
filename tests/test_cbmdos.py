"""Tests for reconstructing the CBM-DOS filesystem from decoded sectors.

A hand-built synthetic disk (BAM + one directory sector + a two-sector file
chain) checks directory parsing, chain following, the lossless last-sector
byte-count rule, and partial-chain reporting; then the real source ``.nib`` is
checked for its actual directory (MENU/ALIEN/... PRGs) and a complete extract.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alientools import cbmdos, cli, gcr, nib

import needs                                       # noqa: E402

REAL_NIB = Path(__file__).resolve().parent.parent / "Alien (USA, Europe).nib"


def _sec(data: bytes) -> gcr.SectorResult:
    return gcr.SectorResult(
        track=0,
        sector=0,
        header_ok=True,
        data_ok=True,
        data=data.ljust(256, b"\x00")[:256],
    )


def _bam(name: bytes, *, first_dir: tuple[int, int] = (18, 1)) -> bytes:
    data = bytearray(256)
    data[0], data[1] = first_dir
    data[2] = 0x41  # 'A'
    data[144 : 144 + len(name)] = name
    for i in range(144 + len(name), 160):
        data[i] = cbmdos.PAD
    data[162:164] = b"AB"
    data[165:167] = b"2A"
    return bytes(data)


def _dir_entry(name: bytes, ftype: int, start: tuple[int, int], size: int) -> bytes:
    e = bytearray(32)
    e[2] = ftype | cbmdos.TYPE_CLOSED
    e[3], e[4] = start
    e[5 : 5 + len(name)] = name
    for i in range(5 + len(name), 21):
        e[i] = cbmdos.PAD
    e[28] = size & 0xFF
    e[29] = (size >> 8) & 0xFF
    return bytes(e)


def _synthetic_disk() -> cbmdos.SectorMap:
    smap: cbmdos.SectorMap = {}
    smap[(18, 0)] = _sec(_bam(b"TESTDISK"))
    # One directory sector with a single PRG "HELLO" starting at 1/0; end of chain.
    dir_data = bytearray(256)
    dir_data[0], dir_data[1] = 0, 0  # no further directory sectors
    dir_data[0:32] = _dir_entry(b"HELLO", 2, (1, 0), 2)
    smap[(18, 1)] = _sec(bytes(dir_data))
    # File chain: 1/0 -> 1/1, then 1/1 is the last sector.
    s0 = bytearray(256)
    s0[0], s0[1] = 1, 1  # link to 1/1
    s0[2:256] = bytes(range(254))
    smap[(1, 0)] = _sec(bytes(s0))
    s1 = bytearray(256)
    s1[0], s1[1] = 0, 5  # last sector; last used byte index = 5 -> 4 data bytes
    s1[2:6] = b"DONE"
    smap[(1, 1)] = _sec(bytes(s1))
    return smap


# --- the synthetic disk -------------------------------------------------------


def test_read_bam() -> None:
    bam = cbmdos.read_bam(_synthetic_disk())
    assert bam.name_text == "TESTDISK"
    assert bam.dos_type == b"2A"
    assert (bam.first_dir_track, bam.first_dir_sector) == (18, 1)


def test_read_directory() -> None:
    entries = cbmdos.read_directory(_synthetic_disk())
    assert len(entries) == 1
    e = entries[0]
    assert e.name_text == "HELLO"
    assert e.type_name == "PRG"
    assert e.closed and not e.locked
    assert (e.start_track, e.start_sector) == (1, 0)
    assert e.filename() == "HELLO.prg"


def test_extract_file_follows_chain_losslessly() -> None:
    smap = _synthetic_disk()
    entry = cbmdos.read_directory(smap)[0]
    data, complete = cbmdos.extract_file(smap, entry)
    assert complete
    # 254 bytes from the full first sector + 4 from the (truncated) last sector.
    assert data == bytes(range(254)) + b"DONE"


def test_partial_chain_is_reported_not_crashed() -> None:
    smap = _synthetic_disk()
    del smap[(1, 1)]  # drop the second sector -> chain is now incomplete
    entry = cbmdos.read_directory(smap)[0]
    data, complete = cbmdos.extract_file(smap, entry)
    assert not complete
    assert data == bytes(range(254))  # bytes recovered before the gap


def test_missing_directory_raises() -> None:
    with pytest.raises(cbmdos.CbmDosError):
        cbmdos.read_bam({})


# --- the real source image ----------------------------------------------------


def test_real_nib_directory() -> None:
    needs.need(needs.NIB)
    smap = cbmdos.build_sector_map(gcr.decode_image(nib.read_nib(REAL_NIB)))
    bam = cbmdos.read_bam(smap)
    assert bam.name_text == "OCG0549"
    names = {e.name_text for e in cbmdos.read_directory(smap)}
    # The game's main program plus the menu/loader files are all present.
    assert {"ALIEN", "MENU", "INSTRUCTIONS"} <= names


def test_real_nib_files_extract_completely() -> None:
    needs.need(needs.NIB)
    smap = cbmdos.build_sector_map(gcr.decode_image(nib.read_nib(REAL_NIB)))
    by_name = {e.name_text: e for e in cbmdos.read_directory(smap)}
    alien = by_name["ALIEN"]
    data, complete = cbmdos.extract_file(smap, alien)
    assert complete
    # ALIEN is a PRG: first two bytes are the little-endian load address ($2000).
    assert data[0] | (data[1] << 8) == 0x2000
    assert len(data) > 40000  # the bulk of the game's code


# --- the dir / extract subcommands --------------------------------------------


def test_dir_command_on_real_nib(capsys: pytest.CaptureFixture[str]) -> None:
    needs.need(needs.NIB)
    rc = cli.main(["dir", str(REAL_NIB)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "ALIEN" in out and "PRG" in out
    assert "file(s)" in out


def test_dir_missing_file_returns_2(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["dir", "no-such-file.nib"])
    assert rc == 2
    assert "not found" in capsys.readouterr().err


def test_extract_command_writes_d64_and_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    needs.need(needs.NIB)
    rc = cli.main(["extract", str(REAL_NIB), "--out", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "174848 bytes" in out
    # The .d64 image and a non-empty files directory are both written.
    d64s = list(tmp_path.glob("*.d64"))
    assert len(d64s) == 1 and len(d64s[0].read_bytes()) == 174848
    files = list((tmp_path).glob("*_files/*"))
    assert any(f.name == "ALIEN.prg" and len(f.read_bytes()) > 40000 for f in files)
