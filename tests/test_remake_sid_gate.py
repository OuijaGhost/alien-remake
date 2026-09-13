"""R-20 RETRACTED — voice 3 DOES retrigger, and the filter sweep depends on it.

**This file used to pin the opposite conclusion.** R-20 (2026-08-01) read a
live capture in which the intro's `ENV3` (`$D41C`) and filter cutoff (`$D416`)
were zero in every sample, concluded that the player's `$20` -> `$21` control
rewrite was a same-jiffy write glitch the chip never sees, and had the envelope
ignore it. That suppression turned out to be the cause of the player's
"muffled, missing instrumentation" report (P3-9, D-120).

The player is explicit::

    9039  LDA $D41C     ; ENV3
    903C  STA $D416     ; -> filter cutoff, high byte

Voice 3 is muted (`3OFF`) with frequency 0 **precisely so it can be a
modulation source**, and `$D413` (its decay) is swept 0->15 continuously to
shape that sweep. With the suppression, voice 3 never retriggered, ENV3 stayed
0, and `$D416` took **3 distinct values in 8 s (99% of them zero)**. Without
it: **152 distinct cutoff values, nonzero 48% of the time.**

Both R-20's capture and a 2026-08-02 re-take sampled at roughly a quarter of a
second — far too coarse to catch an envelope transient — and both concluded
"always zero". The lesson is about sampling rate, not about the chip.
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from alien_remake.audio.sid import _ATTACK, _Envelope


def _env(sr: int = 8000) -> _Envelope:
    e = _Envelope(sr)
    e.set_ad(0x01)     # attack idx 0 (2 ms), decay idx 1 (24 ms)
    e.set_sr(0x00)     # sustain 0, release idx 0
    return e


def test_a_regate_retriggers_the_envelope() -> None:
    """The behaviour R-20 suppressed: gate off then on **does** restart attack.

    Without this the intro's whole filter sweep is dead, because voice 3's
    envelope is what drives it.
    """
    e = _env()
    e.gate_on()
    for _ in range(40):
        e.step()
    level = e.level
    assert level > 0.0
    e.gate_off()
    e.gate_on()
    assert e._state == _ATTACK, "a re-gate must restart the attack phase"


def test_env3_rises_so_the_cutoff_can_sweep() -> None:
    """ENV3 must actually leave zero — that value is copied straight into
    `$D416` by `title_music_player ($9039)`."""
    from alien_remake.audio.sid import SidSynth

    synth = SidSynth(sample_rate=8000)
    synth.write(0x13, 0x09)        # voice 3 AD: a quick attack
    synth.write(0x14, 0xF0)        # voice 3 SR: sustain high
    synth.write(0x12, 0x21)        # sawtooth + gate on
    synth.render(2000)
    assert synth.env3 > 0, "ENV3 stuck at zero means the filter never opens"


def test_the_intro_actually_sweeps_its_filter() -> None:
    """End to end: run the real player and count distinct `$D416` writes.

    With the R-20 suppression this was 3 values, 99% of them zero — the
    "muffled" render. It must be a genuine sweep.
    """
    from collections import Counter

    import alien_remake.audio.sid as sidmod
    from alien_remake.audio import intro

    if not intro.DEFAULT_PRG.exists():
        pytest.skip("ALIEN.prg not extracted")

    written: list[int] = []
    original = sidmod.SidSynth.write

    def spy(self, reg, value):  # type: ignore[no-untyped-def]
        if reg == 0x16:
            written.append(value)
        original(self, reg, value)

    sidmod.SidSynth.write = spy  # type: ignore[method-assign]
    try:
        intro.render_intro(intro.DEFAULT_PRG, seconds=6.0)
    finally:
        sidmod.SidSynth.write = original  # type: ignore[method-assign]

    counts = Counter(written)
    assert len(counts) > 20, f"cutoff barely moves: {sorted(counts)}"
    zero_fraction = counts.get(0, 0) / max(len(written), 1)
    assert zero_fraction < 0.9, f"cutoff is zero {zero_fraction:.0%} of the time"


def test_the_sweep_does_not_clip() -> None:
    """R-20's *other* worry — runaway resonance — belonged to the old filter
    `q` mapping and is gone. A long render must stay inside the rails."""
    from alien_remake.audio import intro

    if not intro.DEFAULT_PRG.exists():
        pytest.skip("ALIEN.prg not extracted")
    render = intro.render_intro(intro.DEFAULT_PRG, seconds=12.0)
    out = Path("out") / "_sid_gate_check.wav"
    out.parent.mkdir(exist_ok=True)
    intro.write_wav(render, out)
    data = out.read_bytes()[44:]
    samples = struct.unpack(f"<{len(data) // 2}h", data)
    clipped = sum(1 for v in samples if abs(v) >= 32700)
    assert clipped == 0, f"{clipped} clipped samples — resonance is running away"
