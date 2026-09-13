"""Tests for the GCR codec and the 1541 sector decoder.

Three layers, smallest first: the raw 4<->5 codec round-trips; a hand-built
synthetic track decodes to the right sector with verified checksums and survives
deliberate corruption (reported, never repaired); and the real source ``.nib``
decodes its standard tracks to the expected sector counts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alientools import cli, gcr, nib

import needs                                       # noqa: E402

REAL_NIB = Path(__file__).resolve().parent.parent / "Alien (USA, Europe).nib"


# --- the raw codec ------------------------------------------------------------


def test_decode_table_is_inverse_of_encode() -> None:
    # Every nibble's 5-bit code decodes back to that nibble; the other 16 codes
    # are flagged illegal.
    for nibble, code in enumerate(gcr.GCR_ENCODE):
        assert gcr.GCR_DECODE[code] == nibble
    assert sum(1 for n in gcr.GCR_DECODE if n < 0) == 16


def test_encode_decode_round_trip_known_block() -> None:
    # A known 4-byte block round-trips byte-for-byte (the decode invariant).
    data = bytes([0x08, 0x00, 0x01, 0x12])
    encoded = gcr.encode(data)
    assert len(encoded) == 5
    assert gcr.decode(encoded) == data


def test_round_trip_all_byte_values() -> None:
    data = bytes(range(256))
    assert gcr.decode(gcr.encode(data)) == data


def test_decode_rejects_illegal_code() -> None:
    # 0x00000 (00000) is not a legal GCR pattern.
    with pytest.raises(gcr.GcrError, match="illegal GCR"):
        gcr.decode(b"\x00\x00\x00\x00\x00")


def test_codec_length_validation() -> None:
    with pytest.raises(gcr.GcrError):
        gcr.encode(b"\x00\x00\x00")  # not a multiple of 4
    with pytest.raises(gcr.GcrError):
        gcr.decode(b"\x00\x00")  # not a multiple of 5


# --- a synthetic track --------------------------------------------------------


def test_scan_one_clean_sector() -> None:
    payload = bytes((i * 7) & 0xFF for i in range(256))
    track = b"\x55" * 4 + gcr.build_sector_image(18, 5, payload) + b"\x55" * 4
    sectors = gcr.scan_sectors(track)
    assert len(sectors) == 1
    s = sectors[0]
    assert (s.track, s.sector) == (18, 5)
    assert s.header_ok and s.data_ok and s.ok
    assert s.status == "ok"
    assert s.data == payload  # lossless: the payload comes back unchanged


def test_scan_multiple_sectors_deduped() -> None:
    img = (
        gcr.build_sector_image(1, 0, bytes(256))
        + gcr.build_sector_image(1, 1, bytes([0xAA]) * 256)
        + gcr.build_sector_image(1, 0, bytes(256))  # duplicate of sector 0
    )
    sectors = gcr.scan_sectors(img)
    assert [s.sector for s in sectors] == [0, 1]  # deduped + sorted


def test_corrupted_data_checksum_is_reported_not_fixed() -> None:
    payload = bytes(256)
    # Hand-build a data block whose stored checksum is wrong, so the block still
    # decodes legally but the verification fails (reported, never "fixed").
    bad = (gcr.data_checksum(payload) ^ 0xFF) & 0xFF
    block = bytes([gcr.DATA_ID]) + payload + bytes([bad, 0x00, 0x00])
    img = (
        b"\xff" * 5
        + gcr.build_header_image(7, 3)
        + b"\x55" * 8
        + b"\xff" * 5
        + gcr.encode(block)
        + b"\x55" * 8
    )
    sectors = gcr.scan_sectors(img)
    assert len(sectors) == 1
    s = sectors[0]
    assert s.header_ok and not s.data_ok
    assert s.status == "bad_data"
    assert not s.ok
    assert s.data == payload  # payload is still recovered, just flagged


def test_no_sync_track_yields_no_sectors() -> None:
    # All-zero track: no sync marks, nothing to decode (a protected/NO_SYNC tail).
    assert gcr.scan_sectors(bytes(0x2000)) == ()


# --- the real source image ----------------------------------------------------


def test_real_nib_standard_tracks_decode() -> None:
    needs.need(needs.NIB)
    image = nib.read_nib(REAL_NIB)
    decoded = {int(d.track_number): d for d in gcr.decode_image(image)}
    # Density zones imply the expected sector counts.
    assert decoded[1].expected == 21
    assert decoded[18].expected == 19
    assert decoded[25].expected == 18
    assert decoded[31].expected == 17
    # The DOS directory track (18) is standard and should decode fully clean.
    t18 = decoded[18]
    assert t18.found == 19 and t18.good == 19 and t18.missing == 0
    # The protected tail decodes to nothing (NO_SYNC).
    assert decoded[37].found == 0


def test_decode_does_not_modify_source() -> None:
    needs.need(needs.NIB)
    import hashlib

    before = hashlib.sha256(REAL_NIB.read_bytes()).hexdigest()
    gcr.decode_image(nib.read_nib(REAL_NIB))
    after = hashlib.sha256(REAL_NIB.read_bytes()).hexdigest()
    assert before == after


# --- the decode subcommand ----------------------------------------------------


def test_decode_command_on_real_nib(capsys: pytest.CaptureFixture[str]) -> None:
    needs.need(needs.NIB)
    rc = cli.main(["decode", str(REAL_NIB)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "MNIB-1541-RAW" in out
    assert "Totals:" in out
    assert "good" in out


def test_decode_missing_file_returns_2(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["decode", "no-such-file.nib"])
    assert rc == 2
    assert "not found" in capsys.readouterr().err
