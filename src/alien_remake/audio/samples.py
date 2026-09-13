"""Sampled audio: a second sound system, beside the decoded one.

**Nothing here is derived from the ROM, and that is the point.**
:mod:`alien_remake.audio.sfx` renders the game's own effects by replaying its
SID writes, and its claim — "nothing in this module is designed; every register
value is a byte read out of the disassembly" — has to stay true. So recordings
live here instead, in their own module, on their own path.

Two jobs, one mechanism
-----------------------
* **In-game effects from recordings** rather than from the synth. The
  `game_audio` setting picks: `original` replays the SID and leaves mixing
  untouched, `enhanced` (renamed from `sampled` 2026-09-05 — see
  `core.options`) plays a `.wav` of the same name if one is present, and
  also runs the loudness spec check (`loudness_report`) against whatever it
  finds. Someone recording a real machine can hear it in place of the
  emulation, and the emulation is still what ships.
* **Interface sounds**, which the original has none of: a blip as a menu row
  changes, a tube warming up at boot. These are inventions and are labelled so.

Why sampled files rather than more synthesis
--------------------------------------------
A recording of the real hardware carries what a register-level model does not —
the filter's actual response, the noise floor, the speaker it came out of. The
synth is the honest *derivation*; a recording is the honest *artefact*. Neither
substitutes for the other, so both are offered and the default stays the one
that can be traced to code.

**Stereo costs memory, so it is not the default.** Measured on this project's
own wavs: 22.8 MB resident mono against 45.6 MB stereo. The mixer therefore
opens mono unless sampled audio is switched on — see `render.audio.set_channels`.
Files may be any rate or layout SDL can read; 44.1 kHz stereo is what this is
for, and pygame converts anything else to the mixer's format on load.
"""

from __future__ import annotations

import random
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

#: Where recordings are looked for, under any asset root.
DIRECTORY = "sounds"

#: Optional manifest inside that directory, mapping a cue to a file and to
#: where the file came from.
#:
#: It exists because a downloaded sound arrives with a name that carries its
#: provenance — `838727__sanderboah__computer-crt-monitor-turn-onoff.wav` says
#: who made it and where to find it again — and renaming that to `crt_warmup`
#: throws the provenance away to satisfy a lookup. The manifest keeps both, and
#: the credit fields are what a credits screen will read::
#:
#:     [crt_warmup]
#:     file = "838727__sanderboah__computer-crt-monitor-turn-onoff.wav"
#:     title = "Computer CRT monitor turn on/off"
#:     author = "Sanderboah"
#:     source = "https://freesound.org/people/Sanderboah/sounds/838727/"
#:     licence = "CC0 1.0"
#:
#: Entirely optional: without it, a cue is `<name>.wav` as before.
MANIFEST = "sounds.toml"

#: Interface cues. **Inventions** — the original has no interface sounds at
#: all, which is why they are named here and not in `sfx.EFFECTS`.
MENU_MOVE = "menu_move"
MENU_CHANGE = "menu_change"
MENU_SELECT = "menu_select"
SCREEN_ENTER = "screen_enter"
CRT_WARMUP = "crt_warmup"

#: Every interface cue, for the loader to report on and tests to enumerate.
UI_CUES: tuple[str, ...] = (
    MENU_MOVE, MENU_CHANGE, MENU_SELECT, SCREEN_ENTER, CRT_WARMUP,
)


@dataclass(frozen=True)
class LoudnessEntry:
    """One recording's measured loudness, for `SamplePlayer.loudness_report`.

    **Not the original** — see `audio.loudness`'s own module docstring.
    """

    cue: str
    path: Path
    lufs: float
    in_spec: bool


class SamplePlayer:
    """Plays `<root>/sounds/<name>.wav`, if such a file exists.

    Every method is best-effort: a missing file, an unreadable file or no audio
    device at all means that cue is silent, never that the game stops. Sound is
    the one subsystem where failing loudly would be worse than the failure.
    """

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory
        self._cache: dict[str, Any] = {}
        #: Parsed :data:`MANIFEST`, cue -> its table. Empty when there is none.
        self.manifest: dict[str, dict[str, Any]] = self._read_manifest()
        #: Cues asked for that had no file. Reported once, not per play, so a
        #: menu without a blip does not fill a log with the same line.
        self.missing: set[str] = set()
        #: The variant each cue played last, so the next pick can avoid it.
        self._last: dict[str, Path] = {}
        #: The mixer channel each cue is playing on, so a retrigger can cut the
        #: copy already sounding rather than layering on top of it (S6).
        self._channels: dict[str, Any] = {}
        self._rng = random.Random()

    def _read_manifest(self) -> dict[str, dict[str, Any]]:
        """Load :data:`MANIFEST` if it is there. A broken one is ignored.

        Never raises: a typo in an optional credits file must not stop the game
        starting, and the fallback (`<cue>.wav`) still works without it.
        """
        if self.directory is None:
            return {}
        path = self.directory / MANIFEST
        try:
            import tomllib

            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        # Lists survive as lists: `files = [...]` is how a cue names several
        # recordings, and stringifying it would turn them into one nonsense
        # filename.
        def _value(v: Any) -> Any:
            return [str(x) for x in v] if isinstance(v, list) else str(v)

        return {
            cue: {str(k): _value(v) for k, v in table.items()}
            for cue, table in raw.items()
            if isinstance(table, dict)
        }

    def credits(self) -> list[dict[str, Any]]:
        """Every manifest entry that names a source, for a credits screen."""
        return [
            {"cue": cue, **table}
            for cue, table in sorted(self.manifest.items())
            if table.get("title") or table.get("author")
        ]

    def variants(self, name: str) -> list[Path]:
        """Every recording that could serve this cue, in a stable order.

        **A cue is a set, not a file.** Three different clicks for the same
        action sound like a machine; one played three times sounds like a
        sample. Sources, in union so that any of them works:

        * the manifest's ``files = [...]`` — an explicit list;
        * the manifest's ``file = "..."`` — the single-file form;
        * a folder named after the cue, ``sounds/<cue>/*.wav``, holding any
          number of files under any names. **This is the one to use for
          adding more:** drop a file in and it is picked up, with no manifest
          to edit and no renaming, so a downloaded sound keeps the name that
          says where it came from;
        * ``sounds/<cue>.wav``, the plain single file.

        Sorted, so the same folder always enumerates the same way and a test
        can rely on it.
        """
        if self.directory is None:
            return []
        table = self.manifest.get(name, {})
        found: list[Path] = []
        listed = table.get("files")
        if isinstance(listed, list):
            found += [self.directory / str(f) for f in listed]
        if table.get("file"):
            found.append(self.directory / str(table["file"]))
        folder = self.directory / name
        if folder.is_dir():
            found += sorted(folder.glob("*.wav"))
        found.append(self.directory / f"{name}.wav")
        seen: dict[Path, None] = {}
        for path in found:
            if path.is_file():
                seen.setdefault(path, None)
        return list(seen)

    def path_for(self, name: str) -> Path | None:
        """The first recording for this cue, or where a single one would be."""
        options = self.variants(name)
        if options:
            return options[0]
        return None if self.directory is None else self.directory / f"{name}.wav"

    def available(self, name: str) -> bool:
        """Whether at least one recording exists for this cue."""
        return bool(self.variants(name))

    def load(self, name: str, path: Path | None = None) -> Any:
        """The `pygame.mixer.Sound` for a cue (or one exact file), or ``None``.

        Cached per *file*, so a cue with several variants keeps them all rather
        than reloading on every play.
        """
        target = path if path is not None else self.path_for(name)
        if target is None or not target.is_file():
            self.missing.add(name)
            return None
        key = str(target)
        if key in self._cache:
            return self._cache[key]
        sound = None
        try:
            import pygame

            from ..render.audio import init_mixer

            init_mixer()
            sound = pygame.mixer.Sound(str(target))
        except Exception:          # pragma: no cover - device dependent
            sound = None
        self._cache[key] = sound
        return sound

    def play(self, name: str) -> bool:
        """Play one of this cue's recordings. Returns whether one started.

        Chosen at random, **avoiding the one played last** when there is more
        than one to choose from. True randomness clumps — the same clip twice
        or three times in a row is common and reads as a stuck sound, which is
        the opposite of what having variants is for.
        """
        options = self.variants(name)
        if not options:
            self.missing.add(name)
            return False
        if len(options) > 1:
            previous = self._last.get(name)
            choices = [p for p in options if p != previous] or options
        else:
            choices = options
        chosen = self._rng.choice(choices)
        sound = self.load(name, chosen)
        if sound is None:
            return False
        try:
            # The channel is kept so `stop` can cut this copy when the cue
            # retriggers. `play` returns None when every channel is busy,
            # which is not an error — the cue is simply not heard.
            self._channels[name] = sound.play()
        except Exception:          # pragma: no cover - device dependent
            return False
        self._last[name] = chosen
        return True

    def stop(self, name: str) -> bool:
        """Cut this cue if a copy of it is still sounding. **S6.**

        Retriggering a cue that has not finished layers it over itself, and a
        few of those in a row is a mush rather than a sound. Exactly the shape
        of D-150, where stacked one-shots made the tracker pings machine-gun;
        the fix there was one continuously-running pulse, and the fix here is
        one sounding copy per cue.

        Only this cue's own channel is touched, so cutting a menu blip cannot
        silence the tube warming up behind it. Returns whether anything was
        actually stopped.
        """
        channel = self._channels.get(name)
        if channel is None:
            return False
        try:
            if not channel.get_busy():
                return False
            channel.stop()
        except Exception:          # pragma: no cover - device dependent
            return False
        return True

    def found(self) -> list[str]:
        """Which recordings are present, for the startup report."""
        if self.directory is None or not self.directory.is_dir():
            return []
        # A file the manifest already claims is not a cue of its own: without
        # this, `crt_warmup` and the freesound filename backing it both show up
        # and the count of "recordings loaded" is one too many.
        claimed = set()
        for table in self.manifest.values():
            if "file" in table:
                claimed.add(str(table["file"]))
            listed = table.get("files")
            if isinstance(listed, list):
                claimed.update(str(f) for f in listed)
        loose = {
            path.stem for path in self.directory.glob("*.wav")
            if path.is_file() and path.name not in claimed
        }
        # A cue can be a *folder* of variants with no top-level file and no
        # manifest entry at all, which is the way to add more — so the report
        # has to look for those too, or it undercounts what is loaded.
        loose |= {
            child.name for child in self.directory.iterdir()
            if child.is_dir() and any(child.glob("*.wav"))
        }
        return sorted(
            cue for cue in set(self.manifest) | loose if self.available(cue)
        )

    def loudness_report(self) -> list[LoudnessEntry]:
        """Measure every recording found against `constants.SOUND_TARGET_LUFS`
        (see that constant's own comment for where the number comes from).

        **Not the original** — the ROM has no concept of LUFS; this exists so
        a player dropping a `.wav` into `sounds/` can be told it is wildly
        louder or quieter than the game's own mix rather than finding out by
        ear mid-game. Reads each file directly with the stdlib `wave` module
        (not through a loaded `pygame.mixer.Sound`) so the measurement is of
        the file as authored, not of whatever the mixer resampled it to.
        Silently skips a file `wave` cannot open (not 16-bit PCM, or not a
        WAV at all) — this is a courtesy diagnostic, not a loader gate.
        """
        from ..core import constants
        from . import loudness

        out: list[LoudnessEntry] = []
        for cue in self.found():
            for path in self.variants(cue):
                try:
                    with wave.open(str(path), "rb") as wf:
                        if wf.getsampwidth() != 2:
                            continue    # only 16-bit PCM is measured
                        sample_rate = wf.getframerate()
                        channels = wf.getnchannels()
                        frames = wf.readframes(wf.getnframes())
                except (OSError, wave.Error, EOFError):
                    continue
                signal = loudness.pcm16_to_float(frames)
                if channels > 1:
                    signal = signal.reshape(-1, channels).mean(axis=1)
                measured = loudness.integrated_lufs(signal, sample_rate)
                in_spec = (
                    measured != float("-inf")
                    and abs(measured - constants.SOUND_TARGET_LUFS)
                    <= constants.SOUND_LUFS_TOLERANCE
                )
                out.append(LoudnessEntry(cue, path, measured, in_spec))
        return out
