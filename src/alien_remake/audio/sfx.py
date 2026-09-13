"""The game's sound effects, transcribed from ``ALIEN.prg``'s own SID writes.

Provenance — this closes the "SFX are absent" record
-----------------------------------------------------------
R-21 previously concluded that the game has **no** sound effects, on the
grounds that no SFX *dispatcher* (a table-driven "play sound N" routine, like
the intro player's) exists in ``ALIEN.prg``. That conclusion was too broad and
is corrected here: the game has no dispatcher because it doesn't need one — the
effects are **open-coded runs of direct SID stores** at their call sites. Five
of them are decoded below, each cited to its routine.

Nothing in this module is designed; every register value is a byte read out of
the disassembly, and the durations are derived from the 6581 envelope tables
the routines' own AD nibbles select (:mod:`alien_remake.audio.sid`). The
waveforms are produced by the same :class:`~alien_remake.audio.sid.SidSynth`
that renders the intro, so an effect sounds like whatever the chip does with
those writes — not like what a designer thought it should sound like.

The resting SID state matters
-----------------------------
These routines are *partial* writes: ``sfx_blip_a`` sets voice 2's frequency,
AD and control and touches nothing else, so the sound it makes depends on the
sustain/release left in ``$D40D`` by whatever ran before. During normal play
that state is established by ``pause_clear_active ($501E)``, which zeroes
voice 2's SR — so the blips decay to silence rather than sustaining. Rendering
an effect therefore means "apply :data:`RESTING_STATE`, then apply the
routine", which is exactly the order the machine sees.

Not modelled — and CLOSED, not open
------------------------------------
The **motion-sensor ping** the player remembers is *not here* — ``check_tracker
($595A)``, the routine that prints the "<NAME> ... MOVEMENT" readout when
``$6509`` flags a sensed crew member, makes no SID write at all, and neither
does the code that sets ``$6509`` (``$7352``). This paragraph used to end there,
with ``sfx_blip_b`` left an open ``[?]`` "candidate" for the tracker's own
sound and a live-capture task filed to settle it by watching ``$651B``
alongside the SID writes.

**PV-24, closed 2026-08-07 (D-178) — ``sfx_blip_b`` is not the tracker sound,
and the real one is already implemented, separately, in this module.** The
tracker's alarm is a **re-gated voice-3 pulse train**, not a blip at all: six
call sites pin it — ``$4DF5``/``$4DFF`` (voice 3's resting frequency/AD,
:data:`TRACKER_VOICE_SETUP` below), ``$65CB`` (the divider, ``$12`` =
:data:`TRACKER_DIVIDER`), ``$4DD7``-``$4DEA`` (the IRQ that counts it down and
re-gates voice 3), ``$8DF6`` (``LDA #$21`` arms it, :data:`TRACKER_CONTROL_ON`
below), ``$8C82`` (silences it) — and ``$43CB``, which fires the identical
``#$21`` write under the caption "THE TRACKER ALARM." on the game's own DECK
PLAN KEY / sound-legend screen. The game names its own sound; that is the tie
the earlier ``[?]`` was waiting for. This module already renders it correctly
as its own effect (``"tracker_alarm"`` in :data:`EFFECTS`, via
:func:`render_pulse`) — a continuously-repeating pulse train, structurally
distinct from :data:`BLIP_A`/:data:`BLIP_B`'s one-shot blips, which really are
just the grille/movement pair `reset_attack_state` selects between and were
never the tracker at all.
"""

from __future__ import annotations

from pathlib import Path

import array
from dataclasses import dataclass

from .sid import ATTACK_MS, DECAY_RELEASE_MS, PAL_CLOCK_HZ, SidSynth

#: The measured jiffy/IRQ rate on this PAL disk (see core.constants JIFFY_HZ).
IRQ_HZ = 60.0
CYCLES_PER_IRQ = PAL_CLOCK_HZ / IRQ_HZ

#: `LDA #imm` (2) + `STA abs` (4) — the shape of every store in these routines.
_STORE_CYCLES = 6


@dataclass(frozen=True)
class SidWrite:
    """One store to a SID register, with the cycles spent reaching it."""

    cycles: int
    reg: int
    value: int


def _seq(*pairs: tuple[int, int]) -> tuple[SidWrite, ...]:
    """A run of `LDA #v / STA $D4xx` stores, 6 cycles apart."""
    return tuple(SidWrite(_STORE_CYCLES, reg, value) for reg, value in pairs)


# --------------------------------------------------------------- resting state

#: **[C $501E]** `pause_clear_active` — the SID as normal play leaves it. Both
#: audible voices sit on triangle with the gate *off*; voice 2's sustain and
#: release are zero, which is what makes the blips one-shots.
RESTING_STATE: tuple[SidWrite, ...] = _seq(
    (0x04, 0x10),  # $D404 voice 1 control: triangle, gate off
    (0x0B, 0x10),  # $D40B voice 2 control: triangle, gate off
    (0x01, 0x08),  # $D401 voice 1 freq hi
    (0x13, 0x08),  # $D413 voice 3 AD
    (0x0F, 0x32),  # $D40F voice 3 freq hi
    (0x05, 0x28),  # $D405 voice 1 AD: attack 2, decay 8
    (0x06, 0x00),  # $D406 voice 1 SR: sustain 0, release 0
    (0x0D, 0x00),  # $D40D voice 2 SR: sustain 0, release 0
)

#: Master volume. **[C $9013 / $663D]** the game runs the chip at full volume;
#: filter mode bits stay clear, so the SFX voices are unfiltered.
_VOLUME: tuple[SidWrite, ...] = _seq((0x18, 0x0F))


# ------------------------------------------------------------------- one-shots

#: **[C $4E42]** `sfx_blip_a` — voice 2, **noise**, frequency `$0100`: a deep,
#: slow-clocking rumble. Selected by `reset_attack_state ($8C8D)` when the
#: grille-burst flag `$651B` is set, i.e. this is the **grille** sound.
BLIP_A: tuple[SidWrite, ...] = _seq(
    (0x0B, 0x80),  # noise, gate off  -> release
    (0x08, 0x01),  # voice 2 freq hi = $01
    (0x0C, 0xC0),  # voice 2 AD: attack $C (1000 ms), decay 0
    (0x0B, 0x81),  # noise, gate on   -> attack
)

#: **[C $4E5C]** `sfx_blip_b` — identical but frequency `$5000`, a bright hiss.
#: The `else` branch of the same selector ($8C98), i.e. the **movement** sound.
BLIP_B: tuple[SidWrite, ...] = _seq(
    (0x0B, 0x80),
    (0x08, 0x50),  # voice 2 freq hi = $50
    (0x0C, 0xC0),
    (0x0B, 0x81),
)

#: **[C $5904]** `blowlock_sfx` — the airlock. Same voice, frequency `$9600`,
#: but the envelope is inverted: attack 0 (2 ms) into decay $D (9000 ms), so it
#: cracks and then bleeds away instead of swelling.
BLOWLOCK: tuple[SidWrite, ...] = _seq(
    (0x0B, 0x80),
    (0x08, 0x96),  # voice 2 freq hi = $96
    (0x0C, 0x0D),  # voice 2 AD: attack 0, decay $D
    (0x0B, 0x81),
)

#: **[C $4F90]** `begin_active_play` — the Alien-attack alert. Voices 1 and 2
#: are gated on together (triangle, sustain 15, release 0) and voice 3 is left
#: *ungated* on sawtooth at frequency `$0020`, purely as a free-running LFO.
ALERT_INIT: tuple[SidWrite, ...] = _seq(
    (0x04, 0x10),  # voice 1 control: triangle, gate off
    (0x0B, 0x10),  # voice 2 control: triangle, gate off
    (0x06, 0xF0),  # voice 1 SR: sustain 15, release 0
    (0x0D, 0xF0),  # voice 2 SR: sustain 15, release 0
    (0x0F, 0x00),  # voice 3 freq hi
    (0x0E, 0x20),  # voice 3 freq lo -> freq $0020
    (0x12, 0x20),  # voice 3 control: sawtooth, gate off (LFO only)
    (0x04, 0x11),  # voice 1: triangle + GATE ON
    (0x0B, 0x11),  # voice 2: triangle + GATE ON
)

#: Voice 3's LFO frequency in Hz, from the `$0020` the routine writes. One full
#: ramp is one sweep of the siren, so a clip this long loops seamlessly.
ALERT_LFO_HZ = 0x0020 * PAL_CLOCK_HZ / 16_777_216.0
ALERT_PERIOD_S = 1.0 / ALERT_LFO_HZ


# ------------------------------------------------------- the tracker alarm

# **[C $4390]** The game *labels its own sound effects*. A demonstration
# sequence prints a caption, plays a sound, prints the next, and so on:
#
#     $4500 "A GRILLE BEING REMOVED?"          -> `sfx_blip_a`   ($439F)
#     $4554 "SOMETHING MOVING BETWEEN LOCATIONS?" -> `sfx_blip_b` ($43B8)
#     $452A "THE TRACKER ALARM?"               -> `$64B6 = $21`  ($43CD)
#
# which independently confirms the grille/movement split decoded from
# `reset_attack_state`, and names the third sound outright.

#: Voice 3's resting setup, from `init_sid_and_clear ($4DF0)`. Frequency high
#: `$32` (`$4DF7`) with the low byte left at 0 gives `$3200`; AD `$08`
#: (`$4E01`) is attack 0 into a 240 ms decay, and voice 3's SR is never
#: written, so it decays to silence. That is what makes each pulse a *ping*.
TRACKER_VOICE_SETUP: tuple[SidWrite, ...] = _seq(
    (0x0F, 0x32),  # $D40F voice 3 freq hi -> ~752 Hz
    (0x13, 0x08),  # $D413 voice 3 AD: attack 0, decay 8
)
#: **[C $8DF6]** `select_char_turn` arms the alarm with `LDA #$21` — sawtooth
#: plus gate — and `reset_attack_state ($8C82)` writes 0 to silence it.
TRACKER_CONTROL_ON = 0x21
TRACKER_CONTROL_OFF = 0x10
#: **[C $65CB]** `$4D03` is loaded with `$12`, and the IRQ at `$4DD7` counts it
#: down and re-gates voice 3 on each wrap — so the ping repeats every 18
#: jiffies. Unlike the one-shots this is a *pulse train*, not an event sound.
TRACKER_DIVIDER = 0x12
TRACKER_PERIOD_S = TRACKER_DIVIDER / IRQ_HZ
#: Voice 3's registers, as offsets: control, and where the IRQ writes.
TRACKER_VOICE = 2

# ------------------------------------------------------------- the heartbeat

#: The fourth demonstrated sound: **"THE HEARTBEAT OF THE CURRENT CHARACTER"**
#: (`$44D6`). Its divider was decoded long ago (D-061) but only ever drove the
#: on-screen marker pulse — the audio half was parked with R-20/R-21 and is
#: built here.
#:
#: Voice 1's setup also comes from `init_sid_and_clear ($4DF0)`: frequency high
#: `$08` (`$4DF2`) with a zero low byte is `$0800`, about 120 Hz — a low thump —
#: and AD `$28` (`$4DFA`) is a fast attack into a 240 ms decay. `$D406` is
#: zeroed by `pause_clear_active`, so it decays away rather than sustaining.
HEARTBEAT_VOICE_SETUP: tuple[SidWrite, ...] = _seq(
    (0x01, 0x08),  # $D401 voice 1 freq hi -> ~120 Hz
    (0x05, 0x28),  # $D405 voice 1 AD: attack 2, decay 8
    (0x06, 0x00),  # $D406 voice 1 SR: sustain 0, release 0
)
#: **[C $4E22]** `fear_alert` writes `$11` — triangle plus gate — to `$64B5`,
#: which the IRQ at `$4D47` copies into `$D404`.
HEARTBEAT_CONTROL_ON = 0x11
HEARTBEAT_VOICE = 0
#: **[C $4E1D/$4E2F/$4E38/$4E3D]** the divider `fear_alert` picks from the
#: character's composure `$6571,Y`: 40 / 30 / 23 / 15 IRQ ticks for composure
#: >= 4 / 3 / 2 / else. **The heart races as the character loses their nerve.**
HEARTBEAT_DIVIDERS: dict[int, int] = {4: 0x28, 3: 0x1E, 2: 0x17, 0: 0x0F}


def heartbeat_divider(composure: int) -> int:
    """IRQ ticks between beats — `fear_alert ($4E16)`'s own ladder."""
    if composure >= 4:
        return HEARTBEAT_DIVIDERS[4]
    return HEARTBEAT_DIVIDERS.get(composure, HEARTBEAT_DIVIDERS[0])


def _envelope_seconds(ad: int, sustain_is_zero: bool = True) -> float:
    """How long a one-shot lasts, from the AD nibbles the routine writes.

    Attack climbs for ``ATTACK_MS[hi]``; with sustain 0 the decay then runs the
    level to (effectively) zero over ``DECAY_RELEASE_MS[lo]``. Both tables are
    the published 6581 figures already used by the synth, so the duration is
    derived from the ROM's own register value rather than chosen.
    """
    attack = ATTACK_MS[(ad >> 4) & 0x0F]
    decay = DECAY_RELEASE_MS[ad & 0x0F] if sustain_is_zero else 0
    return (attack + decay) / 1000.0


#: Derived one-shot lengths (see :func:`_envelope_seconds`).
BLIP_SECONDS = _envelope_seconds(0xC0)      # 1.000 + 0.006
BLOWLOCK_SECONDS = _envelope_seconds(0x0D)  # 0.002 + 9.000


def _apply(synth: SidSynth, writes: tuple[SidWrite, ...], sample_rate: int) -> None:
    """Play a run of stores at their real cycle spacing.

    The gap matters. The synth deliberately ignores a gate-off/gate-on pair
    that arrives with no samples in between (the R-20 write-glitch rule), and
    every effect here is exactly such a pair — six cycles apart, which at
    44.1 kHz is a fraction of a sample. Advancing the stream by at least one
    sample between stores keeps the retrigger real, and is *closer* to the
    machine's timing than collapsing the writes to one instant.
    """
    for w in writes:
        n = max(1, round(w.cycles * sample_rate / PAL_CLOCK_HZ))
        synth.render(n)
        synth.write(w.reg, w.value)


def _fresh(sample_rate: int) -> SidSynth:
    synth = SidSynth(sample_rate=sample_rate)
    for writes in (_VOLUME, RESTING_STATE):
        _apply(synth, writes, sample_rate)
    del synth.pcm[:]  # the setup writes are silent, but don't ship the samples
    return synth


def render_oneshot(
    writes: tuple[SidWrite, ...], seconds: float, sample_rate: int = 44_100
) -> bytes:
    """Render a one-shot effect to 16-bit mono PCM."""
    synth = _fresh(sample_rate)
    _apply(synth, writes, sample_rate)
    synth.render(int(seconds * sample_rate))
    return synth.pcm16()


def render_alert(
    periods: int = 1, sample_rate: int = 44_100, irq_hz: float = IRQ_HZ
) -> bytes:
    """Render the attack alert — a loopable clip of whole LFO periods.

    **[C $4E76]** `irq_alt_handler` runs every IRQ and does the modulation::

        LDA $D41B / LSR A / STA $D401      ; voice 1 freq hi = osc3 / 2
        CLC / ADC #$40 / STA $D408         ; voice 2 freq hi = that + $40

    so both voices sweep together, a fixed `$40` apart in the frequency-high
    byte. Voice 3 is never gated; only its oscillator is read.
    """
    synth = _fresh(sample_rate)
    _apply(synth, ALERT_INIT, sample_rate)
    # Drop the handful of samples the setup stores spanned: the alert is a
    # *loop*, so the clip has to be exactly a whole number of LFO periods or
    # every repeat drifts against the sweep.
    del synth.pcm[:]
    total = int(periods * ALERT_PERIOD_S * sample_rate)
    per_irq = max(1, int(sample_rate / irq_hz))
    done = 0
    while done < total:
        osc3 = synth.osc3
        synth.write(0x01, osc3 >> 1)
        synth.write(0x08, ((osc3 >> 1) + 0x40) & 0xFF)
        chunk = min(per_irq, total - done)
        synth.render(chunk)
        done += chunk
    return synth.pcm16()


def render_pulse(
    setup: tuple[SidWrite, ...],
    voice: int,
    control_on: int,
    divider: int,
    periods: int = 4,
    sample_rate: int = 44_100,
    irq_hz: float = IRQ_HZ,
) -> bytes:
    """Render one of the two IRQ-pulsed voices (heartbeat / tracker alarm).

    Both work the same way and neither is an event sound — the IRQ counts a
    divider down and, on each wrap, re-gates the voice::

        DEC $64B7 / BPL +          ; $4D37, or $4DD7 for voice 3
        LDA $4D02 / STA $64B7      ; reload the divider
        LDA #$10  / STA $D404      ; gate OFF
        LDA $64B5 / STA $D404      ; gate ON with the stored waveform

    so the clip is a **pulse train** whose rate is the divider. One period per
    beat, so ``periods`` whole beats loop seamlessly.
    """
    synth = _fresh(sample_rate)
    _apply(synth, setup, sample_rate)
    del synth.pcm[:]
    control = 0x04 + voice * 7
    per_beat = max(1, round(divider * sample_rate / irq_hz))
    for _ in range(periods):
        synth.write(control, TRACKER_CONTROL_OFF)   # `LDA #$10` — gate off
        synth.render(1)
        synth.write(control, control_on)            # re-gate: the beat
        synth.render(per_beat - 1)
    return synth.pcm16()


#: The effects the game can ask for, by the name the simulation uses. The first
#: four the game demonstrates by name on its own DECK PLAN KEY screen ($4390);
#: the last two it uses without captioning them.
EFFECTS = (
    "heartbeat", "grille", "movement", "tracker_alarm", "airlock", "attack_alert",
)

#: The captions the game itself prints while playing each sound ($44C1 + the
#: varying tail). Kept verbatim because they are the naming evidence: they
#: independently confirm the grille/movement split decoded from
#: `reset_attack_state`'s `$651B` branch, and they name the tracker alarm.
DEMO_CAPTIONS: dict[str, str] = {
    "heartbeat": "THE HEARTBEAT OF THE CURRENT CHARACTER",
    "grille": "A GRILLE BEING REMOVED",
    "movement": "SOMETHING MOVING BETWEEN LOCATIONS",
    "tracker_alarm": "THE TRACKER ALARM",
}
DEMO_CAPTION_STEM = "THIS IS THE SOUND OF"


def render(
    name: str, sample_rate: int = 44_100, *, composure: int = 4
) -> bytes:
    """Render one named effect to 16-bit mono PCM.

    ``composure`` only affects ``"heartbeat"``, whose rate `fear_alert` derives
    from it.
    """
    if name == "grille":
        return render_oneshot(BLIP_A, BLIP_SECONDS, sample_rate)
    if name == "movement":
        return render_oneshot(BLIP_B, BLIP_SECONDS, sample_rate)
    if name == "airlock":
        return render_oneshot(BLOWLOCK, BLOWLOCK_SECONDS, sample_rate)
    if name == "attack_alert":
        return render_alert(sample_rate=sample_rate)
    if name == "tracker_alarm":
        return render_pulse(
            TRACKER_VOICE_SETUP, TRACKER_VOICE, TRACKER_CONTROL_ON,
            TRACKER_DIVIDER, sample_rate=sample_rate,
        )
    if name == "heartbeat":
        return render_pulse(
            HEARTBEAT_VOICE_SETUP, HEARTBEAT_VOICE, HEARTBEAT_CONTROL_ON,
            heartbeat_divider(composure), sample_rate=sample_rate,
        )
    raise ValueError(f"unknown effect {name!r}; expected one of {EFFECTS}")


def wav_bytes(pcm: bytes, sample_rate: int = 44_100) -> bytes:
    """Wrap mono 16-bit PCM in a RIFF/WAVE container."""
    n = len(pcm)
    header = b"RIFF" + array.array("I", [36 + n]).tobytes() + b"WAVEfmt "
    header += array.array("I", [16]).tobytes()
    header += array.array("H", [1, 1]).tobytes()
    header += array.array("I", [sample_rate, sample_rate * 2]).tobytes()
    header += array.array("H", [2, 16]).tobytes()
    header += b"data" + array.array("I", [n]).tobytes()
    return header + pcm


#: The rate every exported clip is rendered at. The mixer is asked to open at
#: this rate too (`render/audio.py`), so a cached file is used as-is; if a
#: device forces something else, the loader falls back to synthesising.
EXPORT_SAMPLE_RATE = 44_100


def export_all(out_dir: Path, sample_rate: int = EXPORT_SAMPLE_RATE) -> list[Path]:
    """Render every effect to a wav under ``out_dir``, returning what was written.

    Synthesising these at first use costs a visible hitch — measured at **809 ms
    for the airlock**, whose clip is nine seconds long, landing exactly as the
    player commits to blowing the lock. Doing it once at derive time moves that
    cost to install (DISC-254).

    The heartbeat is not one clip: `fear_alert ($4E16)` buckets composure with
    `min(composure, 4)`, so eleven fear values collapse to **four** distinct
    dividers. One file per divider, named by it, matching how the renderer
    caches them.
    """
    from ..core import constants as _K

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name in EFFECTS:
        if name == "heartbeat":
            continue
        path = out_dir / f"sfx_{name}.wav"
        path.write_bytes(wav_bytes(render(name, sample_rate=sample_rate), sample_rate))
        written.append(path)
    for composure in sorted({min(c, 4) for c in range(11)}):
        divider = _K.heartbeat_divider(composure)
        path = out_dir / f"sfx_heartbeat_{divider}.wav"
        if path in written:
            continue
        path.write_bytes(
            wav_bytes(
                render("heartbeat", sample_rate=sample_rate, composure=composure),
                sample_rate,
            )
        )
        written.append(path)
    return written
