"""The renderer's audio half: SFX, the heartbeat bed, and the intro tune.

Split out of :mod:`.pygame_app` (D-191), which had grown past 3,400 lines. This
is its most separable slice: seven methods touching eleven attributes and no
module-level state at all.

Sound in this game is not decoration — the ROM *gates* it, and the gates are
mechanics:

- `$8CE1 CPY $64FB` plays the attack siren only for the **selected** character
  (D-139), so who you are watching changes what you hear.
- `$4E16` reloads the heartbeat's IRQ divider from composure (D-145), so a
  calmer crew member's heart audibly beats slower.
- `$4DD7`'s tracker ping is one continuously-running pulse, not a per-detection
  one-shot (D-150) — stacking one-shots is what made the pings machine-gun.

Mixed into `PygameRenderer` rather than made free functions because these are
stateful (channels, caches, the "attack on screen" latch) and that state is
shared with the drawing half. See :mod:`.protocol` for how the shared
attributes are declared.
"""

from __future__ import annotations

import io
import time

import pygame  # the project's one optional runtime dependency (D-009)

from .. import assets
from ..audio import sfx
from ..core import constants, sound
from ..core.flow import Screen
from ..core.state import GameState
from .protocol import RendererState



#: How many channels the mixer opens with. **Mono by default, and that is not
#: an aesthetic choice**: the SID is a mono chip and stereo doubles what every
#: clip costs resident — measured at **22.8 MB mono against 45.6 MB stereo**
#: for this project's own wavs, which is worse than the 10.1 MB 5.1 blow-up
#: DISC-255 fixed. So it follows the `game_audio` setting: it goes to 2 only
#: when sampled audio is switched on, which is when someone has supplied
#: stereo recordings and is asking to hear them.
_channels = 1


def set_channels(count: int) -> None:
    """Choose mono or stereo for the *next* mixer open.

    Must be called before `pygame.init()` to have any effect on the first open,
    which is why the renderer takes it as a constructor argument.
    """
    global _channels
    _channels = 2 if count >= 2 else 1


def pre_init_mixer() -> None:
    """Ask for the chosen layout *before* `pygame.init()` opens one.

    `pygame.init()` initialises every module including the mixer, so by the time
    any of this module's code runs the device layout is already chosen.
    `pre_init` records the request for that later open; `allowedchanges=0`
    forbids SDL substituting the device's own layout for it.
    """
    try:
        pygame.mixer.pre_init(
            frequency=sfx.EXPORT_SAMPLE_RATE, size=-16, channels=_channels,
            allowedchanges=0,
        )
    except (pygame.error, TypeError):  # pragma: no cover - device dependent
        pass


def init_mixer() -> None:
    """Open the mixer at the chosen layout, and hold SDL to it.

    The SID is a mono chip; there is no stereo anywhere in the original, so
    :data:`_channels` is 1 unless sampled audio asked otherwise. Left to itself
    SDL negotiates the *device's* layout, which on a 5.1 output means every clip
    is decoded to six channels — measured at **10.1 MB resident for 1.7 MB of
    wav** (DISC-255). `allowedchanges=0` forbids that substitution either way,
    so the clips stay the shape they were rendered in.

    A no-op once the mixer is up, like `pygame.mixer.init()` itself, so the
    per-effect call sites can keep calling it. Falls back to a default mixer if
    a device will not accept the request — more memory is better than no sound.
    """
    if pygame.mixer.get_init() is not None:
        return
    try:
        pygame.mixer.init(
            frequency=sfx.EXPORT_SAMPLE_RATE, size=-16, channels=_channels,
            allowedchanges=0,
        )
    except (pygame.error, TypeError):  # pragma: no cover - device dependent
        try:
            init_mixer()
        except pygame.error:
            pass

#: **S6 — the floor on retriggering an interface cue**, in milliseconds.
#:
#: Derived from the ROM's own cursor cadence rather than picked. `$5F36`'s
#: busy-wait *is* the repeat rate, so a held direction steps once per main
#: loop — `MAIN_LOOP_HZ`, about 127 ms a step, with no initial delay and no
#: acceleration (see `_JOY_REPEAT_RATE`). This is three quarters of that, so
#: every genuine repeat passes with room for frame jitter and nothing faster
#: does.
#:
#: Tying it to the decoded constant rather than to a round number means the two
#: cannot drift: if the cursor cadence is ever corrected, the sound follows it.
CUE_FLOOR_MS = round(750 / constants.MAIN_LOOP_HZ)


def _now_ms() -> int:
    """Milliseconds since pygame started. Wrapped so tests can replace it."""
    return pygame.time.get_ticks()


class AudioMixin(RendererState):
    """`PygameRenderer`'s audio methods.

    Every attribute it reads is declared on :class:`RendererState`, so this
    module type-checks in isolation.
    """


    # --- audio ----------------------------------------------------------
    #: The screens on which the SID intro tune plays (the original's intro phase,
    #: gated by `$60A8 != 0`): the title and the mode-selection screen. It stops
    #: once a game starts (opening/play) and resumes if the player returns here.
    _INTRO_MUSIC_SCREENS = (Screen.TITLE, Screen.GAME_SELECTION)

    def emit(self, cue: str) -> bool:
        """Play an **interface** cue. **S1 — not the original.**

        The world's own sounds go through `GameState.sound_cues`, which the app
        loop drains once a tick and `core.sound.audible` gates by the ROM's own
        tests. This is the other channel: a menu blip has no simulation and no
        tick, and routing it through `GameState` would put presentation state
        into the model — the boundary the debug overlay and the CRT epoch both
        stay on the right side of.

        Silent unless interface sounds are switched on *and* a recording for
        this cue exists (`audio.samples`), so the default game is exactly as
        quiet as the original.

        **Debounced two ways (S6).** A held direction repeats the cursor at the
        ROM's own rate and the pointer can cross rows faster still, so without
        a floor the same blip fires over itself until it is a mush rather than
        a sound:

        * anything arriving inside :data:`CUE_FLOOR_MS` of the last one is
          dropped — not queued, because a delayed blip belongs to a cursor
          step that has already been and gone;
        * and what does get through **cuts the copy already sounding**, so a
          recording longer than the gap between two steps still gives one blip
          per step instead of two overlapping.

        Per cue, not global: a menu blip must not be swallowed by the tube
        warming up behind it, and the two have nothing to do with each other.
        """
        if not self._ui_sound or self._samples is None:
            return False
        now = _now_ms()
        last = self._cue_last_ms.get(cue)
        if last is not None and 0 <= now - last < CUE_FLOOR_MS:
            return False
        self._cue_last_ms[cue] = now
        self._samples.stop(cue)
        return bool(self._samples.play(cue))

    def _sound(self, effect: str) -> object | None:
        """The `pygame.mixer.Sound` for one of the game's own effects, or None.

        Two sources, chosen by the `game_audio` setting. `enhanced` (renamed
        from `sampled` 2026-09-05) looks for a recording of the same name
        first (`audio.samples`) — someone who has
        recorded a real machine can hear it instead of the emulation. Otherwise
        it is rendered from the ROM's own SID writes (:mod:`audio.sfx`) and
        cached.

        Best-effort in the same way as the intro tune: no audio device just
        means silence, never a crash — the *derivation* is the
        correctness-critical part and it is covered by tests, not by playback.
        """
        if effect in self._sfx_cache:
            return self._sfx_cache[effect]
        # A recording only replaces the synth when asked for and when it is
        # actually there; a missing file falls through rather than muting the
        # effect, so a half-finished sound pack degrades to the original.
        if self._sampled_game_audio and self._samples is not None:
            recorded: object | None = self._samples.load(effect)
            if recorded is not None:
                self._sfx_cache[effect] = recorded
                return recorded
        sound: object | None = None
        try:
            init_mixer()
            rate = pygame.mixer.get_init()[0]
            # **Prefer the pre-rendered clip (DISC-254).** Synthesising on first
            # use costs a visible hitch — 809 ms for the airlock, landing as the
            # player commits to blowing the lock. `--derive-assets` writes these
            # once. Only usable if the device opened at the rate they were
            # rendered at; otherwise fall through and synthesise.
            cached = (
                assets.find(f"sfx_{effect}.wav")
                if rate == sfx.EXPORT_SAMPLE_RATE else None
            )
            if cached is not None:
                self._sfx_cache[effect] = pygame.mixer.Sound(str(cached))
                return self._sfx_cache[effect]
            pcm = sfx.render(effect, sample_rate=rate)
            # **PV-25 FIXED 2026-08-07 (D-171) - `buffer=` is not a WAV.**
            # `pygame.mixer.Sound(buffer=...)` reads the bytes as **raw samples
            # already in the mixer's format**; it does not parse a RIFF header.
            # The mixer inits stereo and `sfx.wav_bytes` produces **mono**, so
            # every clip was being read as interleaved stereo: half the
            # duration, an octave up, alternate samples split across the two
            # channels - plus the 44-byte header played as a click. Measured:
            # `Sound(buffer=wav).get_length()` is exactly 0.5x the true length.
            # Handing it a file-like object makes pygame parse the container
            # and convert mono->stereo properly.
            sound = pygame.mixer.Sound(
                io.BytesIO(sfx.wav_bytes(pcm, pygame.mixer.get_init()[0]))
            )
        except (pygame.error, TypeError, ValueError) as exc:  # pragma: no cover
            print(f"alien-remake: sfx {effect!r} skipped ({exc})")
        self._sfx_cache[effect] = sound
        return sound

    def _heartbeat_sound(self, composure: int) -> object | None:
        """The heartbeat pulse rendered at ``composure``'s own rate, cached.

        Separate from :meth:`_sound` because this effect is **not** one clip:
        `fear_alert ($4E16)` reloads the IRQ divider from the character's
        composure, so a calmer crew member's heart beats slower. One clip per
        distinct divider, keyed accordingly.
        """
        key = f"heartbeat@{constants.heartbeat_divider(composure)}"
        if key in self._sfx_cache:
            return self._sfx_cache[key]
        sound: object | None = None
        try:
            init_mixer()
            rate = pygame.mixer.get_init()[0]
            divider = constants.heartbeat_divider(composure)
            cached = (
                assets.find(f"sfx_heartbeat_{divider}.wav")
                if rate == sfx.EXPORT_SAMPLE_RATE else None
            )
            if cached is not None:
                self._sfx_cache[key] = pygame.mixer.Sound(str(cached))
                return self._sfx_cache[key]
            pcm = sfx.render("heartbeat", sample_rate=rate, composure=composure)
            # **PV-25 FIXED 2026-08-07 (D-171) - `buffer=` is not a WAV.**
            # `pygame.mixer.Sound(buffer=...)` reads the bytes as **raw samples
            # already in the mixer's format**; it does not parse a RIFF header.
            # The mixer inits stereo and `sfx.wav_bytes` produces **mono**, so
            # every clip was being read as interleaved stereo: half the
            # duration, an octave up, alternate samples split across the two
            # channels - plus the 44-byte header played as a click. Measured:
            # `Sound(buffer=wav).get_length()` is exactly 0.5x the true length.
            # Handing it a file-like object makes pygame parse the container
            # and convert mono->stereo properly.
            sound = pygame.mixer.Sound(io.BytesIO(sfx.wav_bytes(pcm, rate)))
        except (pygame.error, TypeError, ValueError) as exc:  # pragma: no cover
            print(f"alien-remake: heartbeat skipped ({exc})")
        self._sfx_cache[key] = sound
        return sound

    def _update_tracker_ping(self, state: GameState) -> None:
        """Loop the tracker ping while the alarm latch is armed (D-150).

        **[C $4DD7]** The IRQ counts `$64B8` down and re-gates voice 3 from
        `$64B6` on every wrap, reloading the divider from `$4D03` (`$12` = 18
        ticks, ~3.3 Hz). `$64B6` is a latch — armed by `check_6562` while a
        tracker is held and something is in range, cleared by
        `reset_attack_state` — so the ping is a steady pulse train for as
        long as the latch holds, never a burst per detection.

        Muted during an attack: `$8DF0 LDA $6562 / BEQ` refuses to arm while
        an attack sequence is running, and `begin_active_play` takes the
        voices over regardless.
        """
        want = bool(state.tracker_alarm) and not self._attacking
        if want == (self._tracker_channel is not None):
            return
        if not want:
            try:
                if self._tracker_channel is not None:
                    self._tracker_channel.stop()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                pass
            self._tracker_channel = None
            return
        clip = self._sound(sound.TRACKER_ALARM)
        if clip is not None:
            try:
                self._tracker_channel = clip.play(loops=-1)  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                self._tracker_channel = None

    def _update_heartbeat(self, state: GameState) -> None:
        """Loop the current character's heartbeat under the play screen (D-145).

        **[C $4E16 `fear_alert`]** The heartbeat is the play screen's ambient
        bed — the game's own sound legend names it "THE HEARTBEAT OF THE
        CURRENT CHARACTER" (`sfx.SOUND_LEGEND`) — and its *rate* is the
        information: `fear_alert` reloads the pulse divider from the selected
        character's composure, so it quickens as they come apart. This was
        fully implemented in `audio/sfx.py` (and `_HEARTBEAT_COLOURS` already
        drove the marker's matching colour pulse) but **never actually
        played** — the player reported hearing no heartbeat at all, and they
        were right: nothing in the renderer ever called it.

        Muted while an attack sequence runs, matching `begin_active_play`
        taking the voices over (D-096).
        """
        crew_id = self._menu.selected_crew if self._menu is not None else None
        crew = state.crew.get(crew_id) if crew_id else None
        want = (
            None if (self._attacking or crew is None or not crew.alive)
            else int(crew.fear)
        )
        # **Compare the DIVIDER, not the raw fear (DISC-254).** `fear_alert`
        # buckets composure hard — `min(composure, 4)` — so fear 4..10 all beat
        # at divider 40 and 0..1 both at 15. Only four distinct clips exist, and
        # `_heartbeat_sound` already keys its cache that way.
        #
        # Testing raw fear meant every 6 -> 7 tick counted as a "rate change",
        # stopping the loop and restarting the *identical* clip from sample
        # zero, mid-beat. Seven of the eleven fear values share one divider, so
        # this fired constantly and the heartbeat audibly lost tempo — reported
        # as the beat skipping.
        want_rate = None if want is None else constants.heartbeat_divider(want)
        if want_rate == self._heartbeat_rate:
            return
        # Rate genuinely changed (or it should stop): drop the loop, start anew.
        if self._heartbeat_channel is not None:
            try:
                self._heartbeat_channel.stop()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                pass
            self._heartbeat_channel = None
        self._heartbeat_composure = want
        self._heartbeat_rate = want_rate
        if want is None:
            return
        clip = self._heartbeat_sound(want)
        if clip is not None:
            try:
                self._heartbeat_channel = clip.play(loops=-1)  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                self._heartbeat_channel = None

    def play_sound_cues(self, state: GameState) -> tuple[str, ...]:
        """Play whatever this tick's cues make audible; return their names.

        The gate is :func:`alien_remake.core.sound.audible`, which reproduces
        two ROM tests: the attack siren only fires for the **selected**
        character (`$8CE1 CPY $64FB`), and the movement/grille blips are muted
        while an attack sequence runs (`$4E42`/`$4E5C` both open `LDA $64BB`).
        Returns the names so a headless test can assert the gating without an
        audio device.
        """
        cues = list(state.sound_cues)
        if not cues:
            return ()
        selected = self._menu.selected_crew if self._menu is not None else None
        # **[C $64BB] P5-3/P7-12 — `attacking` must be the LATCH, not a
        # per-tick recomputation.** `$64BB` stays set for the whole attack
        # sequence; the blip routines (`$4E42`/`$4E5C`) test it directly. The
        # ATTACK_ALERT cue, by contrast, is raised only on the ONE tick the
        # wound lands (`alien.py` `$4230`/`$5354`), so recomputing `attacking`
        # from just this tick's cues made it True for one frame and False on
        # every frame after. Any unrelated crew member's movement blip on a
        # later tick then read `attacking=False`, passed `sound.audible`, and
        # the `elif` below stopped the siren — the "small squeak and then
        # nothing" reported three times. `self._attacking`
        # is this remake's own `$64BB`; OR it in.
        attacking = self._attacking or any(
            c.effect == sound.ATTACK_ALERT for c in cues
        )
        played: list[str] = []
        for cue in cues:
            if not sound.audible(cue, selected, attacking=attacking):
                continue
            played.append(cue.effect)
            clip = self._sound(cue.effect)
            if clip is not None:
                # **P3-12.** The attack siren is a **loop**, not an event
                # sound: `begin_active_play ($4F90)` gates voices 1+2 on and
                # `irq_alt_handler ($4E76)` sweeps them from voice 3's
                # oscillator every IRQ for as long as `$64BB` stays set. Our
                # clip is one 0.53 s LFO period, so playing it once was the
                # "small squeak and then nothing" the player heard. Loop it
                # and let `reset_attack_state` stop it (below).
                loops = -1 if cue.effect == sound.ATTACK_ALERT else 0
                clip.play(loops=loops)  # type: ignore[attr-defined]
        # The attack composite's two ends, both the ROM's own (D-096): it
        # starts with the *audible* alert (`$8CE1` gates siren and animation
        # together) and stops on the next movement blip, because
        # `reset_attack_state ($8C80)` is what plays that blip and clears
        # `$6562`/`$64B6`.
        if sound.ATTACK_ALERT in played:
            self._attacking = True
            # `sound.audible` only lets ATTACK_ALERT through when
            # `cue.crew_id == selected`, so any cue landing in `played` here
            # IS the currently-selected crew member.
            self._attacking_crew_id = selected
        elif {sound.MOVEMENT, sound.GRILLE} & set(played):
            # `reset_attack_state ($8C80)` is what ends the sequence, and it is
            # the same routine that plays the movement/grille blip — so the
            # blip arriving is exactly when the siren must stop.
            self._stop_attack_composite()
        # Frames left of the `wait_keypress_flash` border rainbow.
        self._border_flash = 0
        return tuple(played)

    def _start_attack_composite(self, crew_id: str) -> None:
        """Begin (or hand off) the Alien composite for ``crew_id``.

        **Not the ROM's own trigger — a deliberate departure, both presets**
        (owner's request, 2026-09-06; see DECISIONS.md and `play.py`'s own
        comment where this is called). Driven by room co-location, checked
        fresh every frame, rather than the ROM's one-shot per-victim gate —
        so this starts the siren looping only when it was not already
        playing (switching *which* co-located crew member is selected just
        relabels the same ongoing composite, it does not restart the sound).
        """
        if not self._attacking:
            siren = self._sound(sound.ATTACK_ALERT)
            if siren is not None:
                try:
                    siren.play(loops=-1)  # type: ignore[attr-defined]
                except Exception:  # pragma: no cover - no audio device
                    pass
        self._attacking = True
        self._attacking_crew_id = crew_id

    def _stop_attack_composite(self) -> None:
        """End the attack sequence: clear the flag, drop the victim, silence
        the siren. Shared by the room-co-location check in `play.py` and the
        resume/rebuild paths below."""
        self._attacking = False
        self._attacking_crew_id = None
        siren = self._sfx_cache.get(sound.ATTACK_ALERT)
        if siren is not None:
            try:
                siren.stop()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                pass

    def _update_intro_music(self, screen: Screen) -> None:
        """Start/stop the intro tune so it plays only during the intro phase.

        Best-effort: a missing file / no audio device / mixer failure just skips
        playback rather than raising — decorative polish on a game that must run
        headless/in CI. The audio *pipeline* (mos6502/sid/intro) stays
        correctness-critical and fails loud; only this playback is soft.

        Loops (``loops=-1``): the real game holds on the title playing this
        continuously (DECISIONS D-016). The render is one 102.4s filter-sweep
        cycle rather than a sample-exact loop point (D-017), so each repeat has
        an audible seam — a disclosed simplification.
        """
        want = screen in self._INTRO_MUSIC_SCREENS
        if want == self._music_playing:
            return
        if self._intro_wav is None or not self._intro_wav.exists():
            return
        try:
            if want:
                init_mixer()
                pygame.mixer.music.load(str(self._intro_wav))
                pygame.mixer.music.play(loops=-1)
            else:
                pygame.mixer.music.stop()
            self._music_playing = want
        except pygame.error as exc:  # pragma: no cover - needs a real audio device
            print(f"alien-remake: intro music skipped ({exc})")


    #: A suspend shows up as the wall clock jumping ahead of the monotonic one.
    #: Five seconds is far longer than any legitimate frame hitch and far
    #: shorter than any real sleep, so it separates the two cleanly.
    _RESUME_GAP_S = 5.0

    def check_for_resume(self) -> bool:
        """Rebuild the mixer if the machine has just resumed from sleep.

        SDL audio devices frequently do not survive a suspend on any platform.
        Every audio call here is wrapped in `except`, so the failure is not a
        crash — it is **the game continuing to play in total silence**, which
        costs two mechanics: the heartbeat is composure-paced (D-145) and the
        tracker ping carries information the player acts on.

        `pygame.mixer.init()` is a **no-op when the mixer is already
        initialised**, so it cannot revive a dead device on its own; the device
        has to be torn down first and the cached `Sound` objects, which belong
        to the old device, thrown away with it.

        Detecting the resume needs no platform API. `time.time()` is wall clock
        and jumps across a suspend; `time.perf_counter()` is monotonic and (on
        Linux, `CLOCK_MONOTONIC`) does not advance while suspended. Their
        divergence *is* the signal.
        """
        wall, mono = time.time(), time.perf_counter()
        previous = self._clock_ref
        self._clock_ref = (wall, mono)
        if previous is None:
            return False
        gap = (wall - previous[0]) - (mono - previous[1])
        if gap < self._RESUME_GAP_S:
            return False
        self._rebuild_mixer()
        return True

    def _rebuild_mixer(self) -> None:
        """Tear the mixer down and back up, discarding everything it owned."""
        was_playing_music = self._music_playing
        for channel in (self._tracker_channel, self._heartbeat_channel):
            try:
                if channel is not None:
                    channel.stop()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - device already gone
                pass
        self._tracker_channel = None
        self._heartbeat_channel = None
        self._heartbeat_composure = None
        self._heartbeat_rate = None
        self._attacking = False
        self._attacking_crew_id = None
        # The cached Sounds belong to the device that just went away.
        self._sfx_cache.clear()
        self._music_playing = False
        try:
            pygame.mixer.quit()
            init_mixer()
        except Exception as exc:  # pragma: no cover - needs a real device
            print(f"alien-remake: could not rebuild the mixer after resume ({exc})")
            return
        if was_playing_music and self._intro_wav is not None:
            try:
                pygame.mixer.music.load(str(self._intro_wav))
                pygame.mixer.music.play(loops=-1)
                self._music_playing = True
            except Exception:  # pragma: no cover - needs a real device
                pass
