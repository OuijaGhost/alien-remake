"""Integrated loudness (LUFS), ITU-R BS.1770-4 style — **not ROM-derived**.

Exists for one job: telling a player whether a `.wav` they dropped into the
`sounds/` folder (`audio.samples`) sits anywhere near the game's own mix, so
"enhanced" audio does not suddenly blast or vanish next to the SID-emulated
effects it plays alongside. Nothing about the disassembly or the ROM's own
audio needs this — the C64's SID has no concept of LUFS, and this module is
purely a remake-authoring convenience.

**What this is not.** A from-scratch, unvalidated implementation of the
public BS.1770 algorithm (K-weighting + gated block averaging), built with
plain `numpy` since no audio-analysis library is a project dependency. It has
not been checked against a certified reference meter or a calibrated test
signal from the standard's own conformance suite — treat its numbers as
"close enough to flag an outlier," not as a mastering-grade meter. Good
enough for "is this clip wildly louder or quieter than the rest," which is
the only question `audio.samples`' spec check needs answered.

**Short-clip fallback.** BS.1770's own gated-block algorithm needs at least
one full 400 ms window; several of this game's own effects (a menu blip, the
short blowlock click) are shorter than that. For a signal under one block,
this falls back to an ungated single-block measurement over the whole clip —
still K-weighted, just not gated (gating exists to discount silence and
quiet passages *within* a longer signal, which a sub-400ms clip has none of).
"""

from __future__ import annotations

import math

import numpy as np

#: A 1-D array of float64 samples — same naming convention as `render/crt.py`'s
#: own `Frame`/`Signal` aliases.
Samples = np.ndarray[tuple[int, ...], np.dtype[np.float64]]

#: BS.1770-4's own two-stage K-weighting filter, as a pair of (b, a) biquad
#: coefficient sets. The constants (crossover frequencies, Q, shelf gain) are
#: the standard's own published values — every correct implementation of the
#: algorithm derives the same digital coefficients from them for a given
#: sample rate, which is why these numbers appear, verbatim, in more than one
#: independent BS.1770 implementation.
_SHELF_F0 = 1681.9744509555319
_SHELF_G = 3.99984385397
_SHELF_Q = 0.7071752369554193
_HP_F0 = 38.13547087613982
_HP_Q = 0.5003270373238773

#: The gated-measurement block shape: 400 ms windows, 75% overlap (100 ms
#: hop) — BS.1770-4's own values.
_BLOCK_SECONDS = 0.4
_HOP_SECONDS = 0.1
#: Absolute gate: blocks quieter than this are silence/near-silence and are
#: discounted before the relative gate is even computed.
_ABSOLUTE_GATE_LUFS = -70.0
#: Relative gate: blocks more than this many LU below the *ungated* mean are
#: discounted too — background/silence within an otherwise louder signal.
_RELATIVE_GATE_LU = -10.0


def _shelf_biquad(sample_rate: float) -> tuple[Samples, Samples]:
    k = math.tan(math.pi * _SHELF_F0 / sample_rate)
    vh = 10 ** (_SHELF_G / 20)
    vb = vh ** 0.4996667741545416
    a0 = 1 + k / _SHELF_Q + k * k
    b0 = (vh + vb * k / _SHELF_Q + k * k) / a0
    b1 = 2 * (k * k - vh) / a0
    b2 = (vh - vb * k / _SHELF_Q + k * k) / a0
    a1 = 2 * (k * k - 1) / a0
    a2 = (1 - k / _SHELF_Q + k * k) / a0
    return np.array([b0, b1, b2]), np.array([1.0, a1, a2])


def _highpass_biquad(sample_rate: float) -> tuple[Samples, Samples]:
    k = math.tan(math.pi * _HP_F0 / sample_rate)
    a0 = 1 + k / _HP_Q + k * k
    b0, b1, b2 = 1 / a0, -2 / a0, 1 / a0
    a1 = 2 * (k * k - 1) / a0
    a2 = (1 - k / _HP_Q + k * k) / a0
    return np.array([b0, b1, b2]), np.array([1.0, a1, a2])


def _apply_biquad(x: Samples, b: Samples, a: Samples) -> Samples:
    """Direct-form-II transposed biquad, sample by sample.

    No `scipy.signal.lfilter` here (not a project dependency) — a plain
    Python loop is fine for clips this short (the longest game effect is a
    few seconds), and keeping it dependency-free matches the project's own
    "one approved third-party package" rule (pygame; `numpy` rides along
    with it for `pygame.surfarray`/the CRT layer, DECISIONS D-009).
    """
    y = np.empty_like(x)
    z1 = z2 = 0.0
    b0, b1, b2 = b
    _a0, a1, a2 = a
    for i, xi in enumerate(x):
        yi = b0 * xi + z1
        z1 = b1 * xi - a1 * yi + z2
        z2 = b2 * xi - a2 * yi
        y[i] = yi
    return y


def k_weight(pcm: Samples, sample_rate: int) -> Samples:
    """Apply the BS.1770 K-weighting filter to a mono float signal."""
    b1, a1 = _shelf_biquad(float(sample_rate))
    b2, a2 = _highpass_biquad(float(sample_rate))
    return _apply_biquad(_apply_biquad(pcm, b1, a1), b2, a2)


def integrated_lufs(pcm: Samples, sample_rate: int) -> float:
    """The BS.1770-4 gated integrated loudness of a mono float signal in
    ``[-1, 1]``, in LUFS. See the module docstring for the short-clip
    fallback and the caveats on how much to trust this number.
    """
    weighted = k_weight(np.asarray(pcm, dtype=np.float64), sample_rate)
    block = int(round(_BLOCK_SECONDS * sample_rate))
    hop = int(round(_HOP_SECONDS * sample_rate))
    if len(weighted) < block:
        mean_square = float(np.mean(weighted ** 2)) if len(weighted) else 0.0
        return _lufs(mean_square)

    mean_squares = [
        float(np.mean(weighted[start:start + block] ** 2))
        for start in range(0, len(weighted) - block + 1, hop)
    ]
    gated = [ms for ms in mean_squares if ms > 0 and _lufs(ms) > _ABSOLUTE_GATE_LUFS]
    if not gated:
        return _lufs(0.0)
    relative_threshold = _lufs(float(np.mean(gated))) + _RELATIVE_GATE_LU
    gated = [ms for ms in gated if _lufs(ms) > relative_threshold] or gated
    return _lufs(float(np.mean(gated)))


def _lufs(mean_square: float) -> float:
    if mean_square <= 0:
        return float("-inf")
    return -0.691 + 10 * math.log10(mean_square)


def pcm16_to_float(pcm: bytes) -> Samples:
    """16-bit signed little-endian mono PCM bytes -> float64 in ``[-1, 1]``."""
    ints = np.frombuffer(pcm, dtype="<i2")
    return ints.astype(np.float64) / 32768.0
