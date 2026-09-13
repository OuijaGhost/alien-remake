"""Approximate software MOS 6581 (SID) synthesizer.

Turns a stream of SID register writes (offsets ``$00–$18`` from ``$D400``) into
mono float PCM. Good enough to reproduce the intro tune's pitches, rhythm,
envelopes, and filter sweep from the *real* register writes captured by the
emulated player; **not** a cycle-exact SID. Deliberate approximations (all
recorded in DECISIONS D-015):

- **Oscillators** — naive (non-band-limited) triangle/sawtooth/pulse from a
  normalized phase accumulator; ``f_hz = reg * clock / 2**24`` with the PAL
  clock (985 248 Hz). Aliasing is audible only far above this tune's range.
- **Noise** — the real 23-bit LFSR (feedback taps 22/17, output bits
  22,20,16,13,11,7,4,2), clocked at the oscillator's bit-19 rate.
- **Combined waveforms** — approximated as the minimum of the selected outputs
  (the 6581's analog bus fight is not modelled). Unused by this game's players.
- **Ring-mod / sync** (control bits 1–2) — ignored; the game never sets them.
- **ADSR** — the published 6581 rate tables (attack 2 ms → 8 s; decay/release
  3× attack at the same index); linear attack, exponential decay/release.
  Re-gating resumes from the *current* level — the behaviour the intro tune's
  slow 8-second swell depends on (each note re-gates within microseconds, so
  the envelope keeps climbing across notes).
- **Filter** — one Chamberlin state-variable filter with the common linear
  6581 cutoff approximation ``fc ≈ 30 + FC * 5.8`` Hz (clamped for stability),
  LP/BP/HP mode bits, per-voice routing ($D417) and the 3OFF voice-3 mute
  ($D418 bit 7) honoured. The intro tune *depends* on the filter: voices 1+2
  are routed through it and voice 3 — muted by 3OFF — exists only so its
  envelope (readable at $D41C) can modulate the cutoff every jiffy. Resonance
  is floored at ``q=0.5`` (DECISIONS D-016) rather than following the chip's
  register linearly to its self-oscillating extreme: this tune sets resonance
  to its max *and* rewrites the cutoff every jiffy, and a naive digital SVF at
  that combination rings into runaway peaks a bounded analog filter wouldn't
  produce — audible as hard clipping that swamped the sustained pad under
  harsh crackle (caught by a human listen, not the unit tests, which only
  checked boundedness). Final mixdown is a ``tanh`` soft-knee rather than a
  hard clamp, for the same reason.

Stdlib-only; no pygame.
"""

from __future__ import annotations

import array
import math

#: PAL C64 system clock, the reference for the SID frequency formula.
PAL_CLOCK_HZ = 985_248.0

#: 6581 attack times (ms), indexed by the attack nibble 0–15 (published data).
ATTACK_MS: tuple[int, ...] = (
    2, 8, 16, 24, 38, 56, 68, 80, 100, 250, 500, 800, 1000, 3000, 5000, 8000,
)
#: Decay/release times are 3x the attack time at the same index (published).
DECAY_RELEASE_MS: tuple[int, ...] = tuple(3 * t for t in ATTACK_MS)

_IDLE, _ATTACK, _DECAY, _RELEASE = range(4)


class _Envelope:
    """One voice's ADSR generator; level is a float in [0, 1]."""

    def __init__(self, sample_rate: int) -> None:
        self._fs = float(sample_rate)
        self.level = 0.0
        self._state = _IDLE
        # Set by `gate_off`, cleared by the first `step()` or by `gate_on`.
        self._glitch_state: int | None = None
        self._sustain = 0.0
        self._attack_step = self._step_for(ATTACK_MS[0])
        self._decay_k = self._k_for(DECAY_RELEASE_MS[0])
        self._release_k = self._k_for(DECAY_RELEASE_MS[0])

    def _step_for(self, ms: int) -> float:
        return 1.0 / (self._fs * ms / 1000.0)

    def _k_for(self, ms: int) -> float:
        # Per-sample decay factor: fall to 0.1% of the start in the table time
        # (an exponential stand-in for the 6581's piecewise curve).
        return math.exp(math.log(0.001) / (self._fs * ms / 1000.0))

    def set_ad(self, value: int) -> None:
        self._attack_step = self._step_for(ATTACK_MS[(value >> 4) & 0x0F])
        self._decay_k = self._k_for(DECAY_RELEASE_MS[value & 0x0F])

    def set_sr(self, value: int) -> None:
        self._sustain = ((value >> 4) & 0x0F) / 15.0
        self._release_k = self._k_for(DECAY_RELEASE_MS[value & 0x0F])

    def gate_on(self) -> None:
        """Retrigger the envelope — **[C $9039] R-20 RETRACTED 2026-08-02.**

        This used to ignore a gate-off/gate-on pair that arrived with no
        samples in between, on the strength of R-20's live reading that the
        intro's `ENV3` (`$D41C`) and filter cutoff (`$D416`) were always zero.
        **That reading was a sampling artefact and the suppression was the
        cause of the "muffled, missing instrumentation" report.**

        The player is explicit about what it does::

            9039  LDA $D41C     ; ENV3
            903C  STA $D416     ; -> filter cutoff, high byte

        i.e. **voice 3's envelope drives the cutoff, every call** — and voice 3
        is muted (`3OFF`) with frequency 0 precisely so it can serve as a
        modulation source. `$D413` (its decay) is swept 0->15 continuously to
        shape that sweep, which is the `$D413` variation P2-22 chased.

        With the suppression in place voice 3 never retriggered, so ENV3 stayed
        0, so `$D416` took **3 distinct values in 8 seconds (99% of them 0)**
        and the filter never opened. Removing it gives **152 distinct cutoff
        values, nonzero 48% of the time** — the sweep the tune is built on.

        Both R-20's measurement and my own re-take sampled at ~0.25 s, far too
        coarse to catch an envelope transient, and both concluded "always
        zero". R-20's other worry — that retriggering caused runaway resonance
        and hard clipping — was real at the time but belonged to the old filter
        `q` mapping; a 25 s render now peaks at 27600 with **zero** clipped
        samples.
        """
        self._glitch_state = None
        self._state = _ATTACK

    def gate_off(self) -> None:
        # Remember what we came from, so a same-jiffy re-gate can undo this.
        self._glitch_state = self._state
        self._state = _RELEASE

    def step(self) -> float:
        # Any elapsed sample makes a preceding gate_off real, so a later
        # gate_on is a genuine retrigger rather than a same-jiffy glitch.
        self._glitch_state = None
        state = self._state
        if state == _ATTACK:
            self.level += self._attack_step
            if self.level >= 1.0:
                self.level = 1.0
                self._state = _DECAY
        elif state == _DECAY:
            if self.level > self._sustain:
                self.level = (
                    self._sustain + (self.level - self._sustain) * self._decay_k
                )
                if self.level - self._sustain < 1e-4:
                    self.level = self._sustain
        elif state == _RELEASE:
            if self.level > 0.0:
                self.level *= self._release_k
                if self.level < 1e-4:
                    self.level = 0.0
                    self._state = _IDLE
        return self.level


class _Voice:
    """One SID voice: oscillator + envelope."""

    def __init__(self, sample_rate: int, clock_hz: float) -> None:
        self._fs = float(sample_rate)
        self._clock = clock_hz
        self.freq = 0  # 16-bit frequency register
        self.pw = 0    # 12-bit pulse-width register
        self.control = 0
        self.env = _Envelope(sample_rate)
        self._phase = 0.0
        self._noise_phase = 0.0
        self._lfsr = 0x7FFFFF
        self._noise_out = 0.0

    def set_control(self, value: int) -> None:
        old = self.control
        self.control = value & 0xFF
        if (value ^ old) & 0x01:  # gate bit edge
            if value & 0x01:
                self.env.gate_on()
            else:
                self.env.gate_off()
        if value & 0x08:  # test bit: reset oscillator + noise generator
            self._phase = 0.0
            self._noise_phase = 0.0
            self._lfsr = 0x7FFFFF

    def _clock_lfsr(self) -> None:
        bit = ((self._lfsr >> 22) ^ (self._lfsr >> 17)) & 1
        self._lfsr = ((self._lfsr << 1) | bit) & 0x7FFFFF
        lfsr = self._lfsr
        value = (
            (((lfsr >> 22) & 1) << 7)
            | (((lfsr >> 20) & 1) << 6)
            | (((lfsr >> 16) & 1) << 5)
            | (((lfsr >> 13) & 1) << 4)
            | (((lfsr >> 11) & 1) << 3)
            | (((lfsr >> 7) & 1) << 2)
            | (((lfsr >> 4) & 1) << 1)
            | ((lfsr >> 2) & 1)
        )
        self._noise_out = value / 127.5 - 1.0

    def step(self) -> float:
        """Advance one sample; return the raw waveform output in [-1, 1]."""
        inc = 0.0
        if not (self.control & 0x08):  # test bit holds the oscillator at 0
            inc = self.freq * self._clock / 16777216.0 / self._fs
        self._phase += inc
        if self._phase >= 1.0:
            self._phase -= math.floor(self._phase)
        # The noise LFSR clocks on oscillator bit 19, i.e. 16x the fundamental.
        self._noise_phase += inc * 16.0
        while self._noise_phase >= 1.0:
            self._noise_phase -= 1.0
            self._clock_lfsr()

        select = self.control & 0xF0
        if not select:
            return 0.0
        phase = self._phase
        outs: list[float] = []
        if select & 0x10:  # triangle
            outs.append(4.0 * abs(phase - 0.5) - 1.0)
        if select & 0x20:  # sawtooth
            outs.append(2.0 * phase - 1.0)
        if select & 0x40:  # pulse
            outs.append(1.0 if phase < (self.pw & 0xFFF) / 4096.0 else -1.0)
        if select & 0x80:  # noise
            outs.append(self._noise_out)
        return min(outs)


class SidSynth:
    """Register-write-driven SID model producing mono float PCM.

    Feed writes with :meth:`write` (register offset ``0x00–0x18``), then pull
    samples with :meth:`render`; ``pcm`` accumulates every rendered sample.
    Writes take effect at the current stream position.
    """

    def __init__(
        self, sample_rate: int = 44_100, clock_hz: float = PAL_CLOCK_HZ
    ) -> None:
        self.sample_rate = sample_rate
        self.voices = (
            _Voice(sample_rate, clock_hz),
            _Voice(sample_rate, clock_hz),
            _Voice(sample_rate, clock_hz),
        )
        self.regs = bytearray(0x19)
        self.pcm: list[float] = []
        self._svf_low = 0.0
        self._svf_band = 0.0
        self._f_coef = 0.0
        self._q = 2.0
        self._recalc_filter()

    # ------------------------------------------------------------- registers

    def write(self, reg: int, value: int) -> None:
        reg &= 0x1F
        value &= 0xFF
        if reg >= len(self.regs):
            return  # $19–$1C are read-only on the chip; ignore writes
        self.regs[reg] = value
        if reg < 0x15:
            voice = self.voices[reg // 7]
            slot = reg % 7
            if slot == 0:
                voice.freq = (voice.freq & 0xFF00) | value
            elif slot == 1:
                voice.freq = (voice.freq & 0x00FF) | (value << 8)
            elif slot == 2:
                voice.pw = (voice.pw & 0x0F00) | value
            elif slot == 3:
                voice.pw = (voice.pw & 0x00FF) | ((value & 0x0F) << 8)
            elif slot == 4:
                voice.set_control(value)
            elif slot == 5:
                voice.env.set_ad(value)
            else:
                voice.env.set_sr(value)
        elif reg in (0x15, 0x16, 0x17):
            self._recalc_filter()
        # 0x18 (mode/volume) is read from self.regs during render.

    def _recalc_filter(self) -> None:
        fc_reg = ((self.regs[0x16] << 3) | (self.regs[0x15] & 0x07)) & 0x7FF
        # **[C-live, P2-15, 2026-08-02] the base matters more than the slope.**
        # A 240-sample capture of the real disk playing the intro (WarpMode off,
        # `tools/vice-mcp/p215_sid_diff.py`) shows the tune runs with
        # `$D417 = $F3` (resonance 15, **voices 1 and 2 routed through the
        # filter**), `$D418 = $9F` (volume 15, **low-pass**, voice 3 muted) and
        # — in 100% of samples — `$D415/$D416 = $00/$00`. So the cutoff register
        # never moves for the whole piece, and **every audible voice is filtered
        # by whatever "FC = 0" means**. That single constant therefore sets the
        # intro's entire character.
        #
        # The generic `30 + FC*5.8` line put FC=0 at **30 Hz**, which crushes a
        # tune whose voices all pass through it — audibly "close but a little
        # strange". The 6581's measured minimum cutoff is an order of magnitude
        # higher, around **220 Hz**; keeping the same span to ~12 kHz at full
        # scale gives the slope below.
        fc_hz = 220.0 + fc_reg * 5.8
        fc_hz = min(fc_hz, self.sample_rate / 6.0)  # Chamberlin stability
        self._f_coef = 2.0 * math.sin(math.pi * fc_hz / self.sample_rate)
        resonance = (self.regs[0x17] >> 4) & 0x0F
        # A Chamberlin SVF self-oscillates as q -> 0; the naive 2.0-1.8*res/15
        # mapping this replaced hit q=0.2 at max resonance (this tune's setting,
        # DISCOVERIES D-016) with a *time-varying* cutoff (env3 rewrites $D416
        # every jiffy), which rang the filter into runaway peaks and hard-clipped
        # the mix instead of the sustained pad the real chip's bounded analog
        # resonance produces. Floored at 0.5 — still clearly resonant, stable
        # under a fast-changing cutoff.
        self._q = max(0.5, 2.0 - 1.5 * (resonance / 15.0))

    @property
    def env3(self) -> int:
        """Voice 3's envelope level as the chip's $D41C 8-bit readback."""
        return int(self.voices[2].env.level * 255.0) & 0xFF

    @property
    def osc3(self) -> int:
        """Voice 3's oscillator output as the chip's $D41B 8-bit readback.

        On the 6581 this is the top 8 bits of voice 3's phase accumulator, run
        through the selected waveform. The attack alert (`irq_alt_handler
        $4E76`) reads it every IRQ and copies it into voices 1 and 2's
        frequency-high bytes, so voice 3 acts as a free-running LFO — which is
        why `begin_active_play` ($4F90) leaves voice 3 *ungated* on sawtooth.
        Modelled for the sawtooth case the game actually uses: the raw ramp.
        """
        return int(self.voices[2]._phase * 256.0) & 0xFF

    # ---------------------------------------------------------------- render

    def render(self, n_samples: int) -> None:
        """Append ``n_samples`` mono float samples (clamped to [-1, 1])."""
        mode_vol = self.regs[0x18]
        volume = (mode_vol & 0x0F) / 15.0
        lp = bool(mode_vol & 0x10)
        bp = bool(mode_vol & 0x20)
        hp = bool(mode_vol & 0x40)
        three_off = bool(mode_vol & 0x80)
        filt_route = self.regs[0x17] & 0x07
        f = self._f_coef
        q = self._q
        low = self._svf_low
        band = self._svf_band
        voices = self.voices
        pcm = self.pcm
        for _ in range(n_samples):
            direct = 0.0
            filt_in = 0.0
            for i in (0, 1, 2):
                voice = voices[i]
                sample = voice.step() * voice.env.step()
                if (filt_route >> i) & 1:
                    filt_in += sample
                elif i == 2 and three_off:
                    continue  # 3OFF mutes an unfiltered voice 3
                else:
                    direct += sample
            low += f * band
            high = filt_in - low - q * band
            band += f * high
            filtered = (
                (low if lp else 0.0) + (band if bp else 0.0) + (high if hp else 0.0)
            )
            # tanh: ~identity for the normal range, smoothly compressing the
            # occasional resonant filter peak instead of a hard clamp's
            # flat-top digital clipping (audible as harsh, held-note-obscuring
            # crackle) — closer to an analog chip's soft overload.
            out = math.tanh((direct + filtered) * volume / 3.0)
            pcm.append(out)
        self._svf_low = low
        self._svf_band = band

    def pcm16(self) -> bytes:
        """The accumulated PCM as little-endian signed 16-bit bytes."""
        return array.array(
            "h", (int(s * 32767.0) for s in self.pcm)
        ).tobytes()
