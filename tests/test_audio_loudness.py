"""The loudness spec check (`audio.loudness`, `SamplePlayer.loudness_report`).

**Not the original** — the C64's SID has no concept of LUFS. This exists so a
`.wav` a player drops into `sounds/` for `game_audio=enhanced` can be flagged
if it is wildly louder or quieter than the game's own SID-emulated mix,
rather than found out by ear mid-game. See `audio/loudness.py`'s own module
docstring for what the measurement is (and is not) validated against, and
`constants.SOUND_TARGET_LUFS`'s own comment for where the target number
comes from (measuring the six default effects).
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import numpy as np
import pytest

from alien_remake.audio import loudness, samples, sfx
from alien_remake.core import constants


# --- the pure loudness math ---------------------------------------------------

def _sine(seconds: float, amplitude: float, sample_rate: int = 44100,
          freq: float = 997.0) -> np.ndarray:
    t = np.arange(int(sample_rate * seconds)) / sample_rate
    return amplitude * np.sin(2 * np.pi * freq * t)


def test_full_scale_sine_measures_close_to_minus_3_lufs() -> None:
    """The textbook reference point: a full-scale sine's RMS sits ~3 dB below
    its peak, so BS.1770's own integrated-loudness figure for one lands near
    -3.01 LUFS. `audio/loudness.py`'s own docstring flags this as an
    unvalidated, from-scratch implementation — this is the sanity check that
    it is at least in the right neighbourhood."""
    signal = _sine(1.0, 1.0)
    result = loudness.integrated_lufs(signal, 44100)
    assert -4.0 < result < -2.0


def test_halving_amplitude_drops_loudness_by_about_6_lu() -> None:
    full = loudness.integrated_lufs(_sine(1.0, 1.0), 44100)
    half = loudness.integrated_lufs(_sine(1.0, 0.5), 44100)
    assert 5.0 < (full - half) < 7.0


def test_silence_is_negative_infinity() -> None:
    assert loudness.integrated_lufs(np.zeros(44100), 44100) == float("-inf")


def test_short_clip_uses_the_ungated_fallback() -> None:
    """Under one 400ms block — the short-clip fallback path (see the module
    docstring): must still return a finite number for a real signal, not
    raise or silently treat it as silence."""
    signal = _sine(0.05, 1.0)   # 50ms, well under one BS.1770 block
    result = loudness.integrated_lufs(signal, 44100)
    assert result > float("-inf")


def test_pcm16_to_float_round_trips_full_scale() -> None:
    pcm = struct.pack("<2h", 32767, -32768)
    signal = loudness.pcm16_to_float(pcm)
    assert signal[0] == pytest.approx(1.0, abs=1e-4)
    assert signal[1] == pytest.approx(-1.0, abs=1e-4)


def test_the_games_own_effects_are_within_the_documented_spread() -> None:
    """Pins the numbers `constants.SOUND_TARGET_LUFS`'s own comment cites -
    if the SID synth ever changes enough to move these, the target and
    tolerance need re-deriving, not silently drifting out of sync with them.
    """
    for name in sfx.EFFECTS:
        pcm = sfx.render(name, sample_rate=44100)
        signal = loudness.pcm16_to_float(pcm)
        measured = loudness.integrated_lufs(signal, 44100)
        assert (
            constants.SOUND_TARGET_LUFS - constants.SOUND_LUFS_TOLERANCE
            < measured
            < constants.SOUND_TARGET_LUFS + constants.SOUND_LUFS_TOLERANCE
        ), f"{name}: {measured:.1f} LUFS has drifted outside the documented spread"


# --- SamplePlayer.loudness_report ---------------------------------------------

def _write_wav(path: Path, amplitude: int, seconds: float = 1.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(44100 * seconds)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(44100)
        handle.writeframes(b"".join(
            struct.pack("<h", int(amplitude * math.sin(i / 20)))
            for i in range(frames)
        ))


def test_loudness_report_flags_a_file_louder_than_the_target(tmp_path: Path) -> None:
    player = samples.SamplePlayer(tmp_path)
    # Full-scale (~-3 LUFS) is far above target+tolerance (-22 +/- 10 = -12
    # at the loud end).
    _write_wav(tmp_path / "attack_alert.wav", 32000)
    report = player.loudness_report()
    assert len(report) == 1
    entry = report[0]
    assert entry.cue == "attack_alert"
    assert entry.in_spec is False
    assert entry.lufs > constants.SOUND_TARGET_LUFS + constants.SOUND_LUFS_TOLERANCE


def test_loudness_report_passes_a_file_within_the_target(tmp_path: Path) -> None:
    player = samples.SamplePlayer(tmp_path)
    # Amplitude chosen to land close to the -22 LUFS target itself.
    _write_wav(tmp_path / "grille.wav", 2600)
    report = player.loudness_report()
    assert len(report) == 1
    assert report[0].in_spec is True


def test_loudness_report_is_empty_with_no_sounds_directory() -> None:
    player = samples.SamplePlayer(None)
    assert player.loudness_report() == []


def test_loudness_report_skips_files_it_cannot_open(tmp_path: Path) -> None:
    (tmp_path / "movement.wav").write_bytes(b"not actually a wav file")
    player = samples.SamplePlayer(tmp_path)
    assert player.loudness_report() == []
