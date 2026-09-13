"""Tests for the intro-tune driver (`alien_remake.audio.intro`).

Runs the real emulator over the real `ALIEN.prg` (a short render, to keep the
suite fast) and checks the *pipeline* is sound: it terminates without hanging
or raising, produces a plausible audio artifact, emits the SID writes the
player is known (via static analysis of `out/ALIEN.asm`) to make during init,
and the WAV writer round-trips through the stdlib `wave` module. It does
**not** — cannot — judge whether the tune "sounds right"; that is the human
audio-output review a human has to make.
"""

from __future__ import annotations

import math
import wave
from pathlib import Path

import pytest

from alien_remake.audio.intro import DEFAULT_PRG, render_intro, write_wav

pytestmark = pytest.mark.skipif(
    not DEFAULT_PRG.exists(), reason="extracted ALIEN.prg not present in out/"
)


def test_render_intro_short_clip_terminates_and_produces_audio() -> None:
    result = render_intro(seconds=1.0, sample_rate=8000)
    assert result.frames == 60  # 1 second at the 60 Hz jiffy rate
    assert len(result.synth.pcm) == 8000
    assert all(math.isfinite(s) for s in result.synth.pcm)
    assert all(-1.0 <= s <= 1.0 for s in result.synth.pcm)


def test_render_intro_captures_known_init_writes() -> None:
    # Init B ($8FFC, run right after $4DB8) is known from the disassembly to
    # write $D418=$9F, $D417=$F3, $D413=$97 among others — confirm the real
    # code path actually executed and those writes were captured.
    result = render_intro(seconds=0.1, sample_rate=8000)
    init_writes = {(reg, val) for frame, reg, val in result.sid_writes if frame == -1}
    assert (0x18, 0x9F) in init_writes
    assert (0x17, 0xF3) in init_writes
    assert (0x13, 0x97) in init_writes


def test_render_intro_produces_note_and_gate_writes_over_time() -> None:
    # The player periodically re-gates voices 1/2 ($D404/$D412) with new
    # frequencies ($D400/$D401/$D407/$D408) — confirm this happens across a
    # few seconds of simulated jiffies, not just at init.
    result = render_intro(seconds=3.0, sample_rate=8000)
    post_init = [w for w in result.sid_writes if w[0] >= 0]
    assert post_init  # the player did something after init
    gate_writes = [w for w in post_init if w[1] in (0x04, 0x0B, 0x12)]
    assert len(gate_writes) > 1


def test_render_intro_rejects_wrong_load_address(tmp_path: Path) -> None:
    bad_prg = tmp_path / "bad.prg"
    bad_prg.write_bytes(bytes([0x00, 0x08, 0xEA, 0xEA]))  # loads at $0800
    with pytest.raises(ValueError, match=r"\$2000"):
        render_intro(bad_prg, seconds=0.1)


def test_write_wav_round_trips_via_stdlib(tmp_path: Path) -> None:
    result = render_intro(seconds=0.5, sample_rate=8000)
    out_path = tmp_path / "clip.wav"
    write_wav(result, out_path)
    assert out_path.exists()
    with wave.open(str(out_path), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 8000
        assert wav.getnframes() == 4000
