"""Tests for the software SID synthesizer (`alien_remake.audio.sid`).

Cannot verify "sounds right" (that is the human audio-output review this
a human has to make), but *can* verify the pipeline mechanically: the produced
waveform has the expected frequency for a given frequency register, the
envelope shape rises/decays/releases as configured, and nothing crashes or
produces NaN/inf/clipped-beyond-range output on edge cases.
"""

from __future__ import annotations

import math

from alien_remake.audio.sid import ATTACK_MS, DECAY_RELEASE_MS, PAL_CLOCK_HZ, SidSynth


def zero_crossings_per_second(samples: list[float], sample_rate: int) -> float:
    crossings = 0
    for a, b in zip(samples, samples[1:]):
        if (a < 0) != (b < 0):
            crossings += 1
    duration = len(samples) / sample_rate
    return (crossings / 2) / duration  # two crossings per cycle


def freq_reg_for_hz(hz: float) -> int:
    return round(hz * 16777216.0 / PAL_CLOCK_HZ)


# --- oscillator frequency ------------------------------------------------------


def test_triangle_frequency_matches_register() -> None:
    sample_rate = 44_100
    target_hz = 440.0
    synth = SidSynth(sample_rate=sample_rate)
    reg = freq_reg_for_hz(target_hz)
    synth.write(0x00, reg & 0xFF)
    synth.write(0x01, (reg >> 8) & 0xFF)
    synth.write(0x04, 0x11)  # triangle, gate on
    synth.write(0x05, 0x00)  # instant attack
    synth.write(0x06, 0xF0)  # full sustain, no decay
    synth.write(0x18, 0x0F)  # volume, no filter routing
    synth.render(sample_rate)  # 1 second
    measured = zero_crossings_per_second(synth.pcm, sample_rate)
    assert abs(measured - target_hz) < target_hz * 0.05


def test_pulse_frequency_matches_register() -> None:
    sample_rate = 44_100
    target_hz = 220.0
    synth = SidSynth(sample_rate=sample_rate)
    reg = freq_reg_for_hz(target_hz)
    synth.write(0x00, reg & 0xFF)
    synth.write(0x01, (reg >> 8) & 0xFF)
    synth.write(0x02, 0x00)
    synth.write(0x03, 0x08)  # 50% pulse width
    synth.write(0x04, 0x41)  # pulse, gate on
    synth.write(0x05, 0x00)
    synth.write(0x06, 0xF0)
    synth.write(0x18, 0x0F)
    synth.render(sample_rate)
    measured = zero_crossings_per_second(synth.pcm, sample_rate)
    assert abs(measured - target_hz) < target_hz * 0.05


def test_frequency_zero_produces_silence_no_crash() -> None:
    synth = SidSynth(sample_rate=8000)
    synth.write(0x04, 0x11)  # triangle, gate on, freq stays 0
    synth.write(0x05, 0x00)  # fastest attack (2ms) so it settles quickly
    synth.write(0x06, 0xF0)
    synth.write(0x18, 0x0F)
    synth.render(8000)
    assert all(math.isfinite(s) for s in synth.pcm)
    # After the (fast) attack settles, a stuck oscillator at freq=0 should sit
    # at a constant level, not swing — check the tail, past the attack ramp.
    tail = synth.pcm[-100:]
    assert max(tail) - min(tail) < 0.01


# --- envelope shape --------------------------------------------------------


def test_envelope_rises_during_attack() -> None:
    sample_rate = 44_100
    synth = SidSynth(sample_rate=sample_rate)
    synth.write(0x00, 0x00)
    synth.write(0x01, 0x10)
    synth.write(0x04, 0x11)  # triangle, gate on
    synth.write(0x05, 0x90)  # attack index 9 = 250ms, decay 0
    synth.write(0x06, 0xF0)  # sustain max
    synth.write(0x18, 0x0F)

    voice = synth.voices[0]
    levels = []
    # sample the envelope level directly across a few render chunks
    for _ in range(10):
        synth.render(sample_rate // 20)  # 50ms chunks
        levels.append(voice.env.level)
    assert levels == sorted(levels)  # monotonically non-decreasing during attack
    assert levels[-1] > levels[0]


def test_envelope_decays_to_sustain() -> None:
    sample_rate = 44_100
    synth = SidSynth(sample_rate=sample_rate)
    synth.write(0x00, 0x00)
    synth.write(0x01, 0x10)
    synth.write(0x04, 0x11)
    synth.write(0x05, 0x08)  # attack index 0 (2ms, fast), decay index 8 (100ms)
    synth.write(0x06, 0x80)  # sustain = 8/15
    synth.write(0x18, 0x0F)

    voice = synth.voices[0]
    synth.render(sample_rate // 2)  # 500ms: well past attack+decay
    sustain_target = 8 / 15
    assert abs(voice.env.level - sustain_target) < 0.02


def test_envelope_releases_on_gate_off() -> None:
    sample_rate = 44_100
    synth = SidSynth(sample_rate=sample_rate)
    synth.write(0x00, 0x00)
    synth.write(0x01, 0x10)
    synth.write(0x04, 0x11)  # gate on
    synth.write(0x05, 0x08)  # fast attack, decay index 8
    synth.write(0x06, 0x8F)  # sustain=8/15, release index 15 (8s, slow)
    synth.write(0x18, 0x0F)
    synth.render(sample_rate // 2)  # settle to sustain
    voice = synth.voices[0]
    level_before = voice.env.level
    assert level_before > 0.0
    synth.write(0x04, 0x10)  # gate off
    synth.render(sample_rate // 20)  # 50ms of release (slow release table)
    assert voice.env.level < level_before  # released, moving toward 0
    assert voice.env.level > 0.0  # release index 15 is 8s -> not yet at 0


def test_attack_and_decay_tables_are_16_entries_and_increasing() -> None:
    assert len(ATTACK_MS) == 16
    assert len(DECAY_RELEASE_MS) == 16
    assert list(ATTACK_MS) == sorted(ATTACK_MS)
    assert list(DECAY_RELEASE_MS) == sorted(DECAY_RELEASE_MS)


# --- no crash / no clipping on edge cases --------------------------------


def test_all_voices_silent_produces_zero_no_crash() -> None:
    synth = SidSynth(sample_rate=8000)
    synth.write(0x18, 0x0F)  # volume up, no waveform selected on any voice
    synth.render(8000)
    assert all(s == 0.0 for s in synth.pcm)


def test_noise_waveform_no_nan_and_bounded() -> None:
    synth = SidSynth(sample_rate=8000)
    synth.write(0x00, 0x50)
    synth.write(0x01, 0x10)
    synth.write(0x04, 0x81)  # noise, gate on
    synth.write(0x05, 0x00)
    synth.write(0x06, 0xF0)
    synth.write(0x18, 0x0F)
    synth.render(8000)
    assert all(math.isfinite(s) for s in synth.pcm)
    assert all(-1.0 <= s <= 1.0 for s in synth.pcm)


def test_output_never_clips_beyond_unit_range_with_all_voices_and_filter() -> None:
    synth = SidSynth(sample_rate=8000)
    for voice_base in (0x00, 0x07, 0x0E):
        synth.write(voice_base + 0, 0x00)
        synth.write(voice_base + 1, 0x20)
        synth.write(voice_base + 4, 0x11)  # triangle
        synth.write(voice_base + 5, 0x00)
        synth.write(voice_base + 6, 0xF0)
    synth.write(0x15, 0xFF)  # filter cutoff max
    synth.write(0x16, 0xFF)
    synth.write(0x17, 0xF7)  # resonance + route all 3 voices through the filter
    synth.write(0x18, 0x1F)  # low-pass, full volume
    synth.render(8000)
    assert all(math.isfinite(s) for s in synth.pcm)
    assert all(-1.0 <= s <= 1.0 for s in synth.pcm)


def test_pcm16_produces_expected_byte_length() -> None:
    synth = SidSynth(sample_rate=1000)
    synth.write(0x18, 0x0F)
    synth.render(500)
    data = synth.pcm16()
    assert len(data) == 500 * 2  # 16-bit mono


def test_env3_readback_is_a_byte() -> None:
    synth = SidSynth(sample_rate=8000)
    synth.write(0x0E, 0x00)
    synth.write(0x0F, 0x10)
    synth.write(0x12, 0x11)  # voice 3 triangle, gate on
    synth.write(0x13, 0x00)
    synth.write(0x14, 0xF0)
    synth.render(4000)
    assert 0 <= synth.env3 <= 255
