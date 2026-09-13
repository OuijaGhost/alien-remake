"""Analog CRT / NTSC presentation. **Not the original — a look, not a fact.**

The game draws a clean 320x200 field; this is the tube it is displayed on. The
separation is deliberate and load-bearing: `_surface` is the remake's fidelity
contract (84 golden renders and every replica test compare it byte-for-byte), so
nothing here ever writes to it. The chain reads that surface and produces the
pixels the window gets, exactly at the seam DISC-242 created::

    draw at 320x200 -> _surface -> [ CRT chain ] -> scale once -> _window
                          ^                                          ^
                     the signal                                   the tube

**Everything runs at native resolution**, which is both the right look and a 16x
performance difference: the same chain at 1280x800 costs ~55 ms a frame against
~5 ms here. Noise generated per output pixel at 4x reads as film grain; noise at
the field's own line pitch reads as a CRT.

**The tube runs faster than the game.** The signal is redrawn at
`TUBE_HZ` (120) regardless of the 30 fps draw rate and the 7.886 Hz simulation,
so the noise, roll and interlace keep moving between game frames — which is what
a real CRT does with a slow source. `advance()` takes real elapsed time, so the
look does not change if the frame rate does.

**Two transients, not one strength of the same one** (owner, 2026-08-16). The
full glitch is a channel losing lock: displacement, roll, inversion. The gentle
one is a *degauss* — a decaying wobble with colour fringing that settles — and
shares no code with it, because a scaled-down scramble read as the same effect
turned down, which is exactly what the owner said it looked like.

Deliberately absent: **barrel and pincushion distortion** (owner's instruction),
and the vignette that usually arrives with them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

#: (width, height, 3) uint8 — the shape `pygame.surfarray.array3d` returns.
Frame = np.ndarray[tuple[int, ...], np.dtype[np.uint8]]
#: A signed working buffer — the noise bank, which is added to a frame and so
#: must be able to go negative.
Signal = np.ndarray[tuple[int, ...], np.dtype[np.int16]]

#: The tube's own refresh, independent of the game's frame rate.
TUBE_HZ = 120.0

#: How long each transient lasts. The full one is **short** — a scramble that
#: outstays its welcome stops reading as a fault and starts reading as an
#: effect. The degauss is long and weak on purpose: a real one is a slow
#: settle, and it must not compete with the glitch it sits next to.
GLITCH_SECONDS = 0.30
DEGAUSS_SECONDS = 0.70

#: How long the static kicks up after a command is accepted. Short: it rides
#: the ROM's own border flash, and that is over in a few frames.
BURST_SECONDS = 0.35

#: Strengths, as passed to `glitch()`. Anything at or below `GLITCH_GENTLE`
#: takes the degauss path.
GLITCH_FULL = 1.0
GLITCH_GENTLE = 0.30

#: Pre-generated noise fields, cycled. Generating 320x200x1 of randomness every
#: frame costs about as much as the rest of the chain put together; a bank of
#: sixteen is indistinguishable in motion at 120 Hz.
_NOISE_FRAMES = 16


@dataclass
class _WaveShape:
    """One firing's randomised curve.

    Re-rolled per glitch so the same displacement never repeats: a transient
    that traces an identical path every time stops reading as interference and
    starts reading as an animation, which is what the owner spotted.
    """

    frequency: float = 1.0
    phase: float = 0.0
    amplitude: float = 1.0
    direction: float = 1.0
    ring: float = 1.0


@dataclass
class CrtSettings:
    """Every effect independently switchable. Defaults are the shipped look.

    `enabled=False` must be **byte-identical to no CRT layer at all** — a guard
    test asserts that against the golden renders, because an "off" switch that
    still touches pixels is worse than no switch.

    The numeric defaults are the owner's, dialled in through
    `tools/crt_bench.py`; change them there first, not here.
    """

    enabled: bool = False
    #: Always-on: the tube itself.
    scanlines: bool = True
    scanline_depth: float = 0.10      # 0 = none, 1 = black alternate lines
    #: Vertical softening under the scanlines. A real beam has a spot profile;
    #: hard-edged one-pixel lines are what makes a naive scanline filter look
    #: digital. 0 keeps the field's own vertical hardness.
    scanline_blur: float = 0.20
    chroma_bleed: bool = True
    chroma_bleed_width: int = 3       # horizontal only; luma stays sharp
    noise: bool = True
    noise_amount: int = 7             # 0-255, keep low: texture not damage
    interlace: bool = False           # alternating field dimmed each tube frame
    bloom: bool = False
    bloom_amount: float = 0.10
    #: Phosphor persistence. An exponential trail, which is what makes the
    #: transients read as analog motion rather than as a slideshow of frames.
    motion_blur: float = 0.60         # 0 = none, ~0.9 = long smear
    #: The slowly rolling raster bar — a mains-hum beat between the signal and
    #: the tube. Speed is in field lines per second, so at 22 a bar crosses a
    #: 200-line field in about nine seconds.
    raster: bool = True
    raster_strength: float = 0.06
    raster_speed: float = 22.0
    raster_height: int = 16
    #: The phosphor mask — the RGB triads the picture is actually made of.
    #: **The one stage that runs at window resolution, and rightly so:** a
    #: shadow mask is a sheet of steel behind the glass, a property of the tube
    #: and not of the signal, so its pitch is in *screen* pixels and does not
    #: scale with the game's. `mask_pitch` is the width of one full triad;
    #: below one triad per game pixel there is nowhere to put three colours, so
    #: the renderer skips it (see `PygameRenderer._mask_surface`).
    mask: bool = False
    mask_pitch: int = 3
    mask_strength: float = 0.15       # 0 = white glass, 1 = pure R/G/B stripes
    mask_stagger: bool = True         # slot mask (offset rows) vs aperture grille
    #: How far the gentle transient bends the picture, in field pixels.
    degauss_warp: float = 2.0
    #: The cathode flash, as a fraction of white. **Both** transients use it
    #: (owner, 2026-08-16): the bright bloom that read well on the deck change
    #: is mixed into the crew/INDICATE glitch too, so the two are one family
    #: rather than two unrelated faults.
    flash_glow: float = 0.40
    #: How far colour is pulled off luma, in field pixels. This is the
    #: character of both transients now, so it is a number rather than a
    #: constant buried in the code.
    chroma_shift_px: float = 6.0
    #: Extra static while the ROM's `wait_keypress_flash ($8660)` border is
    #: running. The rainbow border is the game shouting "command accepted"; on
    #: a real set the same interference would be in the picture too, not
    #: politely confined to the margins.
    burst_noise: int = 26
    #: Transients: the scrambled channel and the degauss.
    glitch: bool = True
    glitch_speed: float = 0.18        # how fast the scramble's motion moves
    wave: bool = True                 # per-row horizontal displacement
    vroll: bool = False               # vertical sync roll
    luma_invert: bool = True          # SSAVI gated-pulse inversion
    chroma_shift: bool = True         # colour displaced from luma

    def replace(self, **kw: object) -> "CrtSettings":
        from dataclasses import replace as _replace

        return _replace(self, **kw)  # type: ignore[arg-type]


class CrtProcessor:
    """Applies :class:`CrtSettings` to a native-resolution frame.

    Holds the phase and the precomputed tables. One instance per renderer; call
    :meth:`advance` with real elapsed seconds and :meth:`process` with the
    field.
    """

    def __init__(self, size: tuple[int, int], settings: CrtSettings | None = None,
                 seed: int = 0) -> None:
        self.width, self.height = size
        self.settings = settings or CrtSettings()
        self._rng = np.random.default_rng(seed)
        self._phase = 0.0
        self._seconds = 0.0
        self._glitch_left = 0.0
        self._glitch_span = GLITCH_SECONDS
        self._glitch_strength = 0.0
        self._burst_left = 0.0
        self._gentle = False
        #: Re-rolled on every firing, so no two glitches trace the same curve
        #: (owner's note). Drawn from the seeded rng, so a given seed still
        #: replays exactly -- the variation is in the look, not in the tests.
        self._shape = _WaveShape()
        self._field = 0
        self._rows = np.arange(self.height)
        self._cols = np.arange(self.width)
        # See `_NOISE_FRAMES`.
        self._noise = [
            self._rng.integers(0, 256, (self.width, self.height, 1), dtype=np.int16)
            for _ in range(_NOISE_FRAMES)
        ]
        self._noise_at = 0
        # Filled on first use; see `_dim`, `_scaled_noise` and `_bar_gains`.
        self._dim_luts: dict[float, Frame] = {}
        self._noise_scaled: list[Signal] = []
        self._noise_amount = -1
        self._bar_key: tuple[int, float] | None = None
        self._bar_cache: list[float] = []
        #: Last output, for the phosphor trail.
        self._prev: Frame | None = None
        #: The cathode bloom's shape, built once; see `_degauss`.
        self._glow: Frame | None = None

    # --- lookup tables --------------------------------------------------
    #
    # Several stages multiply 192,000 bytes by a constant fraction, and numpy
    # does that by promoting the whole array to float. A 256-entry `np.take`
    # gives the identical answer for uint8 input at half the cost, and half of
    # a stage matters when the whole chain has 8.33 ms at `TUBE_HZ`: the tables
    # are what keep 120 Hz reachable on a 1080p display.

    def _dim(self, factor: float) -> Frame:
        """A cached ``value * factor`` table for uint8 pixels.

        Clipped, so factors above 1 are usable — the raster bar brightens as
        well as darkens.
        """
        key = round(factor, 3)
        table = self._dim_luts.get(key)
        if table is None:
            table = np.clip(np.arange(256) * key, 0, 255).astype(np.uint8)
            self._dim_luts[key] = table
        return table

    def _scaled_noise(self, amount: int) -> Signal:
        """This tube frame's noise, pre-multiplied by ``amount``."""
        if self._noise_amount != amount:
            self._noise_scaled = [(n * amount) >> 8 for n in self._noise]
            self._noise_amount = amount
        return self._noise_scaled[self._noise_at]

    def _bar_gains(self, height: int, strength: float) -> list[float]:
        """The rolling bar's per-row gain, brightening then dimming.

        One smooth cycle over the bar's height rather than a step: a hum bar on
        a real set is a beat between two nearly-equal frequencies, so it has no
        edges at all. Quantised to the `_dim` table's own resolution, which
        keeps the whole bar down to a handful of cached tables.
        """
        key = (height, round(strength, 3))
        if self._bar_key != key:
            self._bar_cache = [
                round(1.0 + strength * math.sin(2.0 * math.pi * k / height), 3)
                for k in range(height)
            ]
            self._bar_key = key
        return self._bar_cache

    def _glow_mask(self) -> Frame:
        """A soft elliptical bloom, 255 at the centre of the tube.

        Built once and scaled per frame through the `_dim` tables, because the
        shape never changes and only its brightness does. Wider than it is tall
        and deliberately reaching the edges at a low level: a cathode blooming
        is the whole face of the tube lighting up, not a spotlight on it.
        """
        if self._glow is None:
            x = (np.arange(self.width) - self.width / 2) / (self.width * 0.62)
            y = (np.arange(self.height) - self.height / 2) / (self.height * 0.80)
            falloff = np.clip(1.0 - (x[:, None] ** 2 + y[None, :] ** 2), 0.0, 1.0)
            self._glow = (falloff ** 1.6 * 255).astype(np.uint8)
        return self._glow

    # --- state ---------------------------------------------------------

    def advance(self, dt: float) -> None:
        """Move the tube on by ``dt`` real seconds."""
        self._phase += dt * TUBE_HZ
        self._seconds += dt
        self._field ^= 1
        self._noise_at = (self._noise_at + 1) % _NOISE_FRAMES
        if self._glitch_left > 0.0:
            self._glitch_left = max(0.0, self._glitch_left - dt)
        if self._burst_left > 0.0:
            self._burst_left = max(0.0, self._burst_left - dt)

    def glitch(self, strength: float = GLITCH_FULL) -> None:
        """Fire a view-change transient.

        At or below `GLITCH_GENTLE` this is a degauss; above it, a scramble.
        The stronger of two overlapping calls wins and restarts the timer,
        rather than summing into something neither was meant to be.
        """
        if self._glitch_left > 0.0 and strength < self._glitch_strength:
            return
        self._glitch_strength = strength
        self._gentle = strength <= GLITCH_GENTLE
        self._glitch_span = DEGAUSS_SECONDS if self._gentle else GLITCH_SECONDS
        self._glitch_left = self._glitch_span
        self._shape = _WaveShape(
            frequency=float(self._rng.uniform(0.6, 1.6)),
            phase=float(self._rng.uniform(0.0, 2.0 * math.pi)),
            amplitude=float(self._rng.uniform(0.8, 1.3)),
            direction=1.0 if self._rng.random() < 0.5 else -1.0,
            ring=float(self._rng.uniform(0.85, 1.25)),
        )

    def burst(self) -> None:
        """Kick the static up briefly — fired with the command-accept flash."""
        self._burst_left = BURST_SECONDS

    @property
    def seconds(self) -> float:
        """Tube time, in real seconds. Drives anything outside this module
        that has to move at the tube's rate rather than the game's."""
        return self._seconds

    @property
    def glitching(self) -> bool:
        return self._glitch_left > 0.0 and self.settings.glitch

    @property
    def _glitch_level(self) -> float:
        """Decaying 0..1 — the transient fades rather than cutting out."""
        if not self.glitching:
            return 0.0
        return (self._glitch_left / self._glitch_span) * self._glitch_strength

    # --- the chain -----------------------------------------------------

    def process(self, frame: Frame) -> Frame:
        """``frame`` is (w, h, 3) uint8 from `pygame.surfarray.array3d`.

        Returned array is a new one; the input is never modified, which is what
        keeps `_surface` untouched.
        """
        s = self.settings
        if not s.enabled:
            return frame
        out = frame
        level = self._glitch_level
        if level > 0.0:
            out = (self._degauss(out, level) if self._gentle
                   else self._scramble(out, level))
        out = self._tube(out, already_copied=level > 0.0)
        return out

    def _scramble(self, a: Frame, level: float) -> Frame:
        """The crew/INDICATE transient: colour torn off the picture.

        Led by the **chroma shift** (owner's choice - it is the part that reads
        as an analog signal rather than as a filter), over a displacement wave
        whose shape is re-rolled on every firing, and finished with the same
        cathode flash the deck change uses.
        """
        s = self.settings
        w, h = self.width, self.height
        shape = self._shape
        phase = self._phase * s.glitch_speed * shape.direction + shape.phase

        if s.wave:
            # Per-row horizontal displacement - the TV losing horizontal lock.
            # Indices wrap, so a displaced line loops round rather than leaving
            # a black edge; that wrap is what makes it read as an unsynced CRT
            # rather than a slide.
            amp = 22.0 * level * shape.amplitude
            off = (
                amp * np.sin(self._rows * 0.055 * shape.frequency + phase)
            ).astype(np.int32)
            a = a[(self._cols[:, None] + off[None, :]) % w, self._rows[None, :], :]

        if s.vroll:
            a = np.roll(a, int(phase * 9 * level) % h, axis=1)
        else:
            a = a.copy()

        if s.chroma_shift:
            # **This can produce colours the C64 cannot make** - authentic to a
            # scrambled NTSC signal, inauthentic to the machine. The owner chose
            # the signal (DISC-264), then chose to lead with it (DISC-267).
            self._separate_chroma(a, s.chroma_shift_px * level * shape.direction)

        if s.luma_invert and (int(phase * 0.4) & 1) and level > 0.45:
            # Gated pulse: brief, banded rather than whole-frame, so it reads as
            # a sync fault instead of a photographic negative.
            band = slice(0, h // 2) if (int(phase * 0.8) & 1) else slice(h // 2, h)
            a[:, band, :] = 255 - a[:, band, :]

        return self._flash(a, level)

    def _separate_chroma(self, a: Frame, pixels: float) -> None:
        """Pull red one way and blue the other, in place.

        The one artifact both transients share, so it lives in one method: a
        second copy would drift the moment either is tuned.
        """
        offset = int(round(pixels))
        if offset:
            a[:, :, 0] = np.roll(a[:, :, 0], offset, axis=0)
            a[:, :, 2] = np.roll(a[:, :, 2], -offset, axis=0)

    def _flash(self, a: Frame, envelope: float) -> Frame:
        """The cathode bloom: the face of the tube lighting up, then fading.

        Quantised to 1/100 so a whole transient reuses a handful of cached
        tables instead of building one a frame.
        """
        s = self.settings
        if s.flash_glow <= 0:
            return a
        amount = round(envelope * s.flash_glow, 2)
        if amount <= 0.01:
            return a
        glow = np.take(self._dim(amount), self._glow_mask())
        lit: Frame = np.minimum(
            a.astype(np.uint16) + glow[:, :, None], 255
        ).astype(np.uint8)
        return lit

    def _degauss(self, a: Frame, level: float) -> Frame:
        """The deck-change transient: the same family, an octave down.

        Colour separates and springs back while the picture bends a couple of
        pixels and the tube flashes - a monitor settling rather than a channel
        dropping. It never tears (neighbouring lines stay within a pixel of each
        other) and it never rolls, which is the measurable difference from
        `_scramble` and the thing two tests hold it to.
        """
        s = self.settings
        w, h = self.width, self.height
        shape = self._shape
        # **The decay on its own, without the strength that selected this path.**
        # `level` carries the `GLITCH_GENTLE` factor, so scaling by it as well
        # would make `degauss_warp = 2.0` mean 0.6 pixels and the flash a third
        # of the number set. The gentle transient is already the gentle one; its
        # settings should mean what they say.
        envelope = level / max(self._glitch_strength, 1e-6)
        # ~9 Hz ring under that envelope, jittered per firing, so it visibly
        # settles instead of merely fading and never rings the same way twice.
        swing = math.sin(self._seconds * 56.0 * shape.ring + shape.phase) * envelope

        if s.degauss_warp > 0:
            # A bend, not a tear: less than one cycle across the field, so the
            # per-row difference is a fraction of a pixel.
            amp = s.degauss_warp * swing * shape.amplitude
            off = (
                amp * np.sin(self._rows * (2.2 / max(1, h)) + self._seconds * 3.0)
            ).astype(np.int32)
            a = a[(self._cols[:, None] + off[None, :]) % w, self._rows[None, :], :]
        else:
            a = a.copy()

        if s.chroma_shift:
            # Half the scramble's separation and swinging with the ring, so the
            # colour visibly springs back rather than sliding once.
            self._separate_chroma(a, s.chroma_shift_px * 0.5 * swing)

        if abs(swing) > 0.02:
            # The coil pulling on the supply: everything dips and recovers.
            a = np.take(self._dim(1.0 - 0.10 * abs(swing)), a)

        return self._flash(a, envelope * (0.65 + 0.35 * abs(swing)))

    def _tube(self, a: Frame, *, already_copied: bool) -> Frame:
        """The always-on layer: what the display does to any signal."""
        s = self.settings

        if s.chroma_bleed:
            # **Luma stays sharp; only colour smears.** NTSC gives chroma a
            # fraction of luma's bandwidth, which is why edges hold while colour
            # runs sideways — the single most recognisable artifact of the
            # format. Blurring all three channels instead (the obvious
            # implementation, and the first one here) just looks out of focus:
            # it destroys the hard C64 pixel edges that D-056 exists to protect.
            # Fixed-point, not float: the same arithmetic in float32 measured
            # 5.5 ms a frame against a 8.3 ms budget at 120 Hz, and the eight
            # bits of headroom int16 gives are ample for 0..255 channels.
            # Weights are Rec.601 x256 (77/150/29 sum to 256, so the shift is
            # exact and no rounding drift accumulates across the blur taps).
            k = max(1, s.chroma_bleed_width)
            i = a.astype(np.int16)
            # **The weighted sum is computed in int32 and only then narrowed.**
            # In int16 it overflows on anything bright: white is
            # 77*255 + 150*255 + 29*255 = 65025 against a 32767 ceiling, so
            # highlights wrapped negative and came out dark — a white column
            # measured 189 where it should read 765. The blur itself stays in
            # int16, where the widest value is four taps of +-255.
            luma = (
                (77 * a[:, :, 0].astype(np.int32)
                 + 150 * a[:, :, 1].astype(np.int32)
                 + 29 * a[:, :, 2].astype(np.int32)) >> 8
            ).astype(np.int16)[:, :, None]
            chroma = i - luma
            acc = chroma.copy()
            for shift in range(1, k + 1):
                acc += np.roll(chroma, shift, axis=0)
            a = np.clip(luma + acc // (k + 1), 0, 255).astype(np.uint8)
        elif not already_copied:
            a = a.copy()

        if s.bloom and s.bloom_amount > 0:
            # Phosphor spill: bright areas leak into their neighbours.
            spill = np.maximum(np.roll(a, 1, axis=0), np.roll(a, -1, axis=0))
            a = np.minimum(
                a.astype(np.uint16) + np.take(self._dim(s.bloom_amount), spill),
                255,
            ).astype(np.uint8)

        if s.scanlines and s.scanline_depth > 0:
            # **At the field's own line pitch, never the window's.** Scaling
            # happens after this, so one dark line stays one C64 raster line at
            # every window size — the mistake DISC-261 fixed in the border.
            if s.scanline_blur > 0:
                # Softened *before* the lines go on, not after: blurring the
                # finished pattern averages each dark line with the bright one
                # beside it and cancels the effect outright. This blurs the
                # picture vertically — the beam's spot profile — and the hard
                # line pitch then sits over it, which is the analog order.
                weight = int(min(1.0, s.scanline_blur) * 128)
                if weight:
                    i = a.astype(np.int16)
                    neighbours = (np.roll(i, 1, axis=1) + np.roll(i, -1, axis=1)) >> 1
                    a = (
                        (i * (256 - 2 * weight) + neighbours * (2 * weight)) >> 8
                    ).astype(np.uint8)
            keep = 1.0 - min(1.0, s.scanline_depth)
            a[:, ::2] = np.take(self._dim(keep), a[:, ::2])

        if s.interlace:
            # Alternating field dimmed slightly each tube frame. Gentle on
            # purpose: at a 200-line field this reads as shimmer if overdone.
            a[:, self._field::2] = np.take(self._dim(0.92), a[:, self._field::2])

        if s.raster and s.raster_strength > 0:
            # The bar rolls on **wall-clock seconds**, not the tube phase, so
            # its speed is the number the owner dialled in and nothing else.
            # Only its own rows are touched, which is why a per-row loop beats
            # any whole-frame multiply here.
            height = max(2, s.raster_height)
            gains = self._bar_gains(height, s.raster_strength)
            top = int(self._seconds * s.raster_speed) % self.height
            for k, gain in enumerate(gains):
                row = (top + k) % self.height
                a[:, row] = np.take(self._dim(gain), a[:, row])

        if s.motion_blur > 0:
            # Phosphor persistence, as a one-pole filter over the output. On a
            # still picture it converges and costs nothing visible; under the
            # transients it is what turns a sequence of displaced frames into
            # something that moves.
            weight = int(min(0.9, s.motion_blur) * 256)
            previous = self._prev
            if weight and previous is not None and previous.shape == a.shape:
                a = (
                    (a.astype(np.int16) * (256 - weight)
                     + previous.astype(np.int16) * weight) >> 8
                ).astype(np.uint8)
            self._prev = a

        if s.mask and s.mask_strength > 0:
            # **Pay for the mask before it is applied.** The triads are a
            # multiply at window resolution, and two thirds of every triad are
            # dimmed, so the picture would arrive about a fifth darker than the
            # signal. Real sets answer this by driving the gun harder; so does
            # this, and highlights clip exactly as they do on the glass.
            a = np.take(self._dim(mask_gain(s.mask_strength)), a)

        extra = 0
        if self._burst_left > 0.0 and s.burst_noise > 0:
            extra = int(s.burst_noise * (self._burst_left / BURST_SECONDS))
        if s.noise and (s.noise_amount > 0 or extra > 0):
            # After the trail, so the static stays crisp instead of being
            # averaged into a haze.
            #
            # A burst is scaled on the spot rather than through the cache: the
            # amount changes every frame while it decays, and `_scaled_noise`
            # rebuilds all sixteen fields when it changes — 2M operations a
            # frame to avoid one multiply over 64,000.
            if extra:
                noise = (self._noise[self._noise_at] * (s.noise_amount + extra)) >> 8
            else:
                noise = self._scaled_noise(s.noise_amount)
            a = np.clip(a.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return a


def mask_gain(strength: float) -> float:
    """How much to brighten a signal to survive :func:`shadow_mask`.

    Two of every three subpixels are dimmed by ``strength``, so the mask passes
    ``1 - 2*strength/3`` of the light on average. This is the reciprocal.
    """
    return 1.0 / max(0.05, 1.0 - 2.0 * strength / 3.0)


def shadow_mask(size: tuple[int, int], pitch: int = 3, strength: float = 0.35,
                stagger: bool = True) -> Frame:
    """The tube's phosphor triads, as a multiplier map at **window** size.

    Returned as a plain array so this module stays free of pygame; the renderer
    turns it into a surface once per window size and blits it with
    `BLEND_RGB_MULT`, which SDL does in C at 0.42 ms for 1920x1080 — a numpy
    multiply over two million pixels would cost twenty times that.

    ``stagger`` offsets alternate bands by half a triad, which is a slot mask
    (most colour televisions); without it the result is an aperture grille
    (Trinitrons), whose stripes run unbroken from top to bottom.
    """
    width, height = size
    pitch = max(3, pitch)
    dim = int(round(255 * (1.0 - min(1.0, max(0.0, strength)))))
    mask = np.full((width, height, 3), dim, dtype=np.uint8)
    sub = max(1, pitch // 3)
    columns = np.arange(width)
    if stagger:
        # Bands one triad tall, every other one shifted half a triad along.
        band = (np.arange(height) // pitch) & 1
        offset = (band * (pitch // 2))[None, :]
        phase = (columns[:, None] + offset) % pitch
    else:
        phase = np.broadcast_to(((columns % pitch)[:, None]), (width, height))
    for channel in range(3):
        lit = (phase >= channel * sub) & (phase < (channel + 1) * sub)
        mask[:, :, channel] = np.where(lit, 255, dim)
    return mask


#: The CLI's three faces of `CrtSettings`. `off` must be indistinguishable from
#: a build with no CRT layer at all -- a guard test asserts that against the
#: golden renders, because a switch that still touches pixels is worse than no
#: switch.
def preset(name: str) -> CrtSettings:
    """``off`` / ``subtle`` / ``full`` -- what ``--crt`` selects."""
    if name == "off":
        return CrtSettings(enabled=False)
    if name == "full":
        return CrtSettings(enabled=True)
    if name == "subtle":
        # Enough to read as a tube on a modern flat panel, little enough to
        # forget about. Interlace is the first thing out: it is the most
        # visible of the always-on effects at a 200-line field.
        return CrtSettings(
            enabled=True, scanline_depth=0.06, noise_amount=4,
            raster_strength=0.03, motion_blur=0.45, flash_glow=0.25,
            chroma_shift_px=4.0,
        )
    raise ValueError(f"unknown CRT preset {name!r}")


PRESETS = ("off", "subtle", "full")
