"""Render the game's real SID intro tune by emulating its own player.

**How the original plays the tune** (DISCOVERIES D-014):
``$4DB8`` (init A, run at ``SYS 16384``) points the KERNAL IRQ vector
(``$0314/$0315``) at ``$4D08`` and enables the VIC raster IRQ. That one vector
then serves **two** interrupt sources, and ``$4D08`` dispatches on which fired
by testing ``$D019 & $81``:

- **Raster IRQ** (``$D019 & $81 == $81``) → ``$4D58``: a two-phase raster-split
  sprite update. Nothing audio-related; with ``$60A8`` nonzero it acks and
  chains straight to the KERNAL (``$4D89`` → ``JMP $EA7E``).
- **CIA-1 jiffy timer IRQ** (the KERNAL's ~60 Hz tick; ``$D019`` shows no
  raster bit) → falls through to ``$4D11``, which forks on ``$60A8``:
  - ``$60A8 != 0`` (set by init B ``$8FFC`` at boot — the title/intro phase):
    ``JMP $9039``, the **music player**. Each jiffy it copies voice 3's
    envelope (``$D41C``) to the filter cutoff (``$D416``); every ``$91A1``=24
    jiffies it advances an 8-step two-voice pattern (``$91C6``/``$91CE``,
    note+octave nibbles over the chromatic table at ``$91AE``/``$91BA``),
    re-gating sawtooth voices 1+2 (control ``$20``→``$21``). Init B also sets
    attack=15 (the 8-second swell), sustain=15, routes voices 1+2 through the
    filter ($D417=$F3) and mutes voice 3 via 3OFF ($D418=$9F) — voice 3 exists
    only as the filter's envelope modulator. *This is the intro tune.*
  - ``$60A8 == 0`` (cleared by ``$702D``, entered from the "GAME SELECTION"
    screen — decoded directly from its screen-RAM text table, DISCOVERIES
    D-014 — once the player picks a mode): the real-time gameplay tick — the
    four game-update routines on an 8-jiffy counter (DECISIONS D-008)
    plus the gate-retrigger heartbeat SFX (``$4D37``/``$4DD7``).
  Either way it chains to ``JMP $EA31`` (the KERNAL service that acks the CIA).

This driver reproduces the title-phase configuration exactly: load the real
``ALIEN.prg`` at ``$2000``, call the game's own ``$4DB8`` then ``$8FFC``, then
enter ``$4D08`` once per simulated jiffy (60 Hz) with a ``$D019`` read hook
returning 0 — i.e. every simulated interrupt is a CIA tick, the branch that
carries all audio (raster ticks are audio-silent no-ops in this phase, so they
are not simulated; DECISIONS D-015). A ``$D41C`` hook feeds the synth's live
voice-3 envelope back to the player. Every ``$D400–$D418`` write is applied to
the :class:`~alien_remake.audio.sid.SidSynth` at the current stream position
(sub-jiffy write timing is collapsed to the jiffy boundary — microseconds on
real hardware). PC reaching KERNAL ROM (``$E000+``) ends a jiffy's service.

The PRG is read from ``out/`` (a derived artifact of ``alientools extract``)
and the WAV is written under ``out/`` — sources stay untouched.

Run: ``python -m alien_remake.audio.intro [--seconds 102.4] [--out out/intro.wav]``
"""

from __future__ import annotations

import argparse
import wave
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .mos6502 import Cpu, MemoryBus
from .sid import SidSynth

PRG_LOAD_ADDR = 0x2000
#: Init A — installs the $4D08 IRQ vector + raster setup (run by SYS 16384).
ENTRY_INIT_IRQ = 0x4DB8
#: Init B — music init: $60A8=1, zeroes the sequencer state, seeds the SID.
ENTRY_INIT_MUSIC = 0x8FFC
#: The installed IRQ handler both interrupt sources funnel through.
IRQ_HANDLER = 0x4D08
#: PC entering KERNAL ROM means this jiffy's interrupt service is over.
KERNAL_BASE = 0xE000
#: The KERNAL programs CIA-1 Timer A for a ~60 Hz jiffy on PAL and NTSC alike.
JIFFY_HZ = 60.0

#: The music player's slowest-moving state, voice 3's attack/decay register
#: ($D413, offset 0x13), is overwritten every note-step (24 jiffies) with an
#: incrementing 8-bit counter ($91D6 in the game's own memory) — so its
#: attack/decay character sweeps from percussive (fast) to a slow, held swell
#: over exactly 256 steps = 6144 jiffies = 102.4s (DISCOVERIES D-015), then
#: wraps and repeats. A render shorter than this only ever hears the
#: percussive early portion — the default below covers one full sweep so the
#: held/sustained character (audible from roughly the second half onward) is
#: actually present. Melodic pitch keeps drifting slowly past one sweep (an
#: octave register the player never resets), so this is *not* a sample-exact
#: loop point, just the natural musical unit; DECISIONS D-016 covers the
#: looping choice made from it.
LOOP_JIFFIES = 6144
DEFAULT_SECONDS = LOOP_JIFFIES / JIFFY_HZ  # 102.4s

SID_BASE = 0xD400
SID_LAST = 0xD418
VIC_IRQ_FLAG = 0xD019
SID_OSC3 = 0xD41B
SID_ENV3 = 0xD41C

DEFAULT_PRG = Path("out") / "Alien (USA, Europe)_files" / "ALIEN.prg"
DEFAULT_OUT = Path("out") / "intro.wav"


@dataclass
class IntroRender:
    """The result of one emulated render: audio plus the captured write log."""

    sample_rate: int
    frames: int
    #: Every SID write as ``(jiffy_frame, register_offset, value)``;
    #: frame -1 = writes made by the init routines before the first jiffy.
    sid_writes: list[tuple[int, int, int]]
    synth: SidSynth


def load_prg(path: Path) -> tuple[int, bytes]:
    """Read a CBM PRG file → (load address, body bytes)."""
    raw = path.read_bytes()
    if len(raw) < 3:
        raise ValueError(f"{path} is too short to be a PRG file")
    return raw[0] | (raw[1] << 8), raw[2:]


def render_intro(
    prg_path: Path = DEFAULT_PRG,
    *,
    seconds: float = DEFAULT_SECONDS,
    sample_rate: int = 44_100,
) -> IntroRender:
    """Emulate the original player for ``seconds`` and synthesize the audio."""
    load_addr, body = load_prg(prg_path)
    if load_addr != PRG_LOAD_ADDR:
        raise ValueError(
            f"expected ALIEN.prg to load at ${PRG_LOAD_ADDR:04X}, "
            f"got ${load_addr:04X}"
        )
    bus = MemoryBus()
    bus.load(load_addr, body)
    synth = SidSynth(sample_rate=sample_rate)

    frame = -1  # init-phase writes are logged as frame -1
    writes: list[tuple[int, int, int]] = []

    def on_write(addr: int, value: int) -> None:
        if SID_BASE <= addr <= SID_LAST:
            synth.write(addr - SID_BASE, value)
            writes.append((frame, addr - SID_BASE, value))

    bus.write_listener = on_write
    # Every simulated interrupt is a CIA jiffy tick: $D019 reads "no raster
    # IRQ pending", steering $4D08 down the music/game-tick branch (see module
    # docs; the raster branch is an audio-silent no-op in the intro phase).
    bus.read_hooks[VIC_IRQ_FLAG] = lambda: 0x00
    # The player modulates the filter with voice 3's envelope each jiffy.
    bus.read_hooks[SID_ENV3] = lambda: synth.env3
    bus.read_hooks[SID_OSC3] = lambda: 0x00  # unused on the intro path

    cpu = Cpu(bus)
    # The game's own boot-time init, exactly as SYS 16384 runs it.
    cpu.call(ENTRY_INIT_IRQ, max_instructions=1_000)
    cpu.call(ENTRY_INIT_MUSIC, max_instructions=10_000)

    n_frames = round(seconds * JIFFY_HZ)
    samples_per_frame = sample_rate / JIFFY_HZ
    pending = 0.0
    for frame in range(n_frames):
        cpu.pc = IRQ_HANDLER
        cpu.run(stop=lambda pc: pc >= KERNAL_BASE, max_instructions=200_000)
        pending += samples_per_frame
        whole = int(pending)
        pending -= whole
        synth.render(whole)
    return IntroRender(
        sample_rate=sample_rate,
        frames=n_frames,
        sid_writes=writes,
        synth=synth,
    )


def write_wav(render: IntroRender, out_path: Path) -> None:
    """Write the render's PCM as a mono 16-bit WAV under ``out_path``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(render.sample_rate)
        wav.writeframes(render.synth.pcm16())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alien-intro",
        description=(
            "Render the original C64 'Alien' intro tune to a WAV by emulating "
            "the game's own SID player (DECISIONS D-010 #3)."
        ),
    )
    parser.add_argument(
        "--prg",
        type=Path,
        default=DEFAULT_PRG,
        help="path to the extracted ALIEN.prg (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="output WAV path (default: %(default)s)",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SECONDS,
        help="length to render (default: one full 102.4s filter-sweep cycle)",
    )
    parser.add_argument(
        "--rate", type=int, default=44_100, help="output sample rate"
    )
    args = parser.parse_args(argv)

    result = render_intro(args.prg, seconds=args.seconds, sample_rate=args.rate)
    write_wav(result, args.out)
    peak = max((abs(s) for s in result.synth.pcm), default=0.0)
    print(
        f"wrote {args.out}: {args.seconds:g}s at {args.rate} Hz "
        f"({result.frames} jiffies, {len(result.synth.pcm)} samples, "
        f"{len(result.sid_writes)} SID register writes, peak {peak:.2f})"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
