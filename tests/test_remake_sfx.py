"""The four decoded sound effects, and the ROM tests that gate them (D-088/D-090).

The load-bearing test here is :func:`test_transcribed_writes_match_the_prg_bytes`
— it re-reads the immediate operands out of ``ALIEN.prg`` itself, so a typo in
the transcription fails rather than quietly shipping a sound the machine never
made. Everything else checks that the derivation stays derived: durations come
from the 6581 envelope tables the routines' own AD nibbles select, and the
alert's clip length comes from the voice-3 frequency the routine writes.
"""

from __future__ import annotations

import struct
from pathlib import Path
from types import SimpleNamespace

import pytest

from alien_remake.audio import sfx
from alien_remake.audio.sid import ATTACK_MS, DECAY_RELEASE_MS
from alien_remake.core import sound
from alien_remake.core.sound import SoundCue

_PRG = Path("out") / "Alien (USA, Europe)_files" / "ALIEN.prg"
_LOAD_ADDR = 0x2000


def _prg() -> bytes:
    if not _PRG.exists():
        pytest.skip("ALIEN.prg not extracted (run `alientools extract` first)")
    data = _PRG.read_bytes()
    load = int.from_bytes(data[:2], "little")
    assert load == _LOAD_ADDR, f"unexpected load address ${load:04X}"
    return data[2:]


def _immediates(rom: bytes, start: int, count: int) -> list[tuple[int, int]]:
    """Read ``count`` consecutive `LDA #imm / STA $D4xx` pairs from ``start``.

    Returns ``(sid_register_offset, immediate)`` — exactly the shape the module
    stores, so the comparison is direct.
    """
    out: list[tuple[int, int]] = []
    off = start - _LOAD_ADDR
    for _ in range(count):
        assert rom[off] == 0xA9, f"expected LDA #imm at ${off + _LOAD_ADDR:04X}"
        imm = rom[off + 1]
        assert rom[off + 2] == 0x8D, f"expected STA abs at ${off + _LOAD_ADDR + 2:04X}"
        addr = rom[off + 3] | (rom[off + 4] << 8)
        assert 0xD400 <= addr <= 0xD418, f"${addr:04X} is not a SID register"
        out.append((addr - 0xD400, imm))
        off += 5
    return out


@pytest.mark.parametrize(
    "start, writes",
    [
        (0x4E47, sfx.BLIP_A),    # sfx_blip_a, past its `LDA $64BB / BNE` guard
        (0x4E61, sfx.BLIP_B),    # sfx_blip_b, likewise
        (0x5904, sfx.BLOWLOCK),  # blowlock_sfx starts with the stores
    ],
)
def test_transcribed_writes_match_the_prg_bytes(
    start: int, writes: tuple[sfx.SidWrite, ...]
) -> None:
    rom = _prg()
    assert _immediates(rom, start, len(writes)) == [(w.reg, w.value) for w in writes]


def test_alert_init_matches_the_prg_bytes() -> None:
    """`begin_active_play ($4F90)`'s SID block, $4FA5 to the closing RTS.

    Checked as raw bytes rather than via :func:`_immediates` because the
    routine shares one `LDA` across two stores twice over (`#$10` -> `$D404` +
    `$D40B`, `#$F0` -> `$D406` + `$D40D`).
    """
    rom = _prg()
    assert rom[0x4FA5 - _LOAD_ADDR : 0x4FCB - _LOAD_ADDR] == bytes((
        0xA9, 0x10, 0x8D, 0x04, 0xD4, 0x8D, 0x0B, 0xD4,   # v1+v2 ctrl = $10
        0xA9, 0xF0, 0x8D, 0x06, 0xD4, 0x8D, 0x0D, 0xD4,   # v1+v2 SR   = $F0
        0xA9, 0x00, 0x8D, 0x0F, 0xD4,                     # v3 freq hi = $00
        0xA9, 0x20, 0x8D, 0x0E, 0xD4, 0x8D, 0x12, 0xD4,   # v3 freq lo + ctrl
        0xA9, 0x11, 0x8D, 0x04, 0xD4, 0x8D, 0x0B, 0xD4,   # both gates ON
        0x60,
    ))
    # The transcription carries exactly those register/value pairs, in order.
    assert [(w.reg, w.value) for w in sfx.ALERT_INIT] == [
        (0x04, 0x10), (0x0B, 0x10), (0x06, 0xF0), (0x0D, 0xF0),
        (0x0F, 0x00), (0x0E, 0x20), (0x12, 0x20), (0x04, 0x11), (0x0B, 0x11),
    ]


def test_the_alert_modulator_matches_the_irq_handler_bytes() -> None:
    """[C $4E76] `LDA $D41B / LSR / STA $D401 / CLC / ADC #$40 / STA $D408` —
    voice 3's oscillator drives both audible voices, a fixed $40 apart."""
    rom = _prg()
    assert rom[0x4E76 - _LOAD_ADDR : 0x4E83 - _LOAD_ADDR] == bytes((
        0xAD, 0x1B, 0xD4,        # LDA $D41B  (osc3)
        0x4A,                    # LSR A
        0x8D, 0x01, 0xD4,        # STA $D401  (voice 1 freq hi)
        0x18, 0x69, 0x40,        # CLC / ADC #$40
        0x8D, 0x08, 0xD4,        # STA $D408  (voice 2 freq hi)
    ))


def test_resting_state_matches_pause_clear_active() -> None:
    """`pause_clear_active ($501E)` — the state normal play leaves the chip in.

    Not checked byte-for-byte by :func:`_immediates`, because this routine
    reuses one `LDA` across two stores (`$5026 LDA #$10` feeds both `$D404`
    and `$D40B`) and so is not a run of pairs. What matters — and what is
    asserted — is the property the blips depend on: **voice 2's sustain and
    release are both zero**, which is why they decay to silence instead of
    droning (D-088).
    """
    rom = _prg()
    assert rom[0x5026 - _LOAD_ADDR : 0x502E - _LOAD_ADDR] == bytes(
        (0xA9, 0x10, 0x8D, 0x04, 0xD4, 0x8D, 0x0B, 0xD4)
    )
    assert rom[0x5040 - _LOAD_ADDR : 0x5048 - _LOAD_ADDR] == bytes(
        (0xA9, 0x00, 0x8D, 0x06, 0xD4, 0x8D, 0x0D, 0xD4)
    )
    by_reg = {w.reg: w.value for w in sfx.RESTING_STATE}
    assert by_reg[0x0D] == 0x00  # voice 2 SR: sustain 0, release 0
    assert by_reg[0x04] == 0x10 and by_reg[0x0B] == 0x10  # both gates off


def test_the_two_blips_differ_only_in_frequency() -> None:
    """$8C8D picks between them on the grille flag, so the *only* thing that
    distinguishes 'grille' from 'movement' is voice 2's frequency-high byte."""
    a = [(w.reg, w.value) for w in sfx.BLIP_A]
    b = [(w.reg, w.value) for w in sfx.BLIP_B]
    differing = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert differing == [1]
    assert a[1] == (0x08, 0x01)  # deep rumble
    assert b[1] == (0x08, 0x50)  # bright hiss


def test_durations_are_derived_from_the_envelope_tables() -> None:
    """Not chosen: the AD nibble the routine writes indexes the published 6581
    tables the synth already uses."""
    assert sfx.BLIP_SECONDS == (ATTACK_MS[0xC] + DECAY_RELEASE_MS[0x0]) / 1000.0
    assert sfx.BLOWLOCK_SECONDS == (ATTACK_MS[0x0] + DECAY_RELEASE_MS[0xD]) / 1000.0
    # The airlock is the inverse envelope of the blips — a crack, not a swell.
    assert sfx.BLOWLOCK_SECONDS > sfx.BLIP_SECONDS


def test_alert_clip_is_one_whole_lfo_period_so_it_loops() -> None:
    """Voice 3 runs free at freq $0020; one ramp is one siren sweep."""
    assert sfx.ALERT_LFO_HZ == pytest.approx(1.8792, abs=1e-3)
    pcm = sfx.render_alert(periods=1, sample_rate=22_050)
    assert len(pcm) // 2 == int(sfx.ALERT_PERIOD_S * 22_050)


@pytest.mark.parametrize("effect", sfx.EFFECTS)
def test_every_effect_renders_audible_pcm(effect: str) -> None:
    pcm = sfx.render(effect, sample_rate=22_050)
    samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    assert samples, f"{effect} rendered nothing"
    assert max(abs(s) for s in samples) > 1000, f"{effect} is effectively silent"
    assert max(abs(s) for s in samples) <= 32767


def test_unknown_effect_is_refused_not_guessed() -> None:
    with pytest.raises(ValueError):
        sfx.render("footsteps")


# --- the ROM's gating tests -------------------------------------------------

def test_attack_alert_only_sounds_for_the_selected_character() -> None:
    """[C $8CE1] `CPY $64FB / BNE $8D26` — the siren and the animation are one
    branch, which is why the player remembers them arriving together."""
    cue = SoundCue(sound.ATTACK_ALERT, crew_id="lambert")
    assert sound.audible(cue, "lambert", attacking=True)
    assert not sound.audible(cue, "parker", attacking=True)
    assert not sound.audible(cue, None, attacking=True)


def test_movement_blips_are_muted_during_an_attack() -> None:
    """[C $4E42/$4E5C] both blip routines open `LDA $64BB / BNE <rts>`."""
    for effect in (sound.MOVEMENT, sound.GRILLE):
        cue = SoundCue(effect)
        assert sound.audible(cue, "ripley", attacking=False)
        assert not sound.audible(cue, "ripley", attacking=True)


def test_the_airlock_has_no_guard_at_all() -> None:
    """`blowlock_sfx ($5904)` starts straight in on the stores — no `$64BB`
    test, and it is not selection-gated."""
    cue = SoundCue(sound.AIRLOCK)
    for selected in (None, "ripley"):
        for attacking in (False, True):
            assert sound.audible(cue, selected, attacking=attacking)


# --- the simulation raises them ---------------------------------------------

def test_blowing_an_airlock_raises_the_airlock_cue() -> None:
    from alien_remake.core.sim import Simulation

    sim = Simulation()
    room = sim.ship.airlock_rooms()[0]
    sim.state.sound_cues.clear()
    assert sim._open_airlock(room) is True
    assert [c.effect for c in sim.state.sound_cues] == [sound.AIRLOCK]


def test_a_tick_with_no_movement_raises_no_blip() -> None:
    """The blip is tied to a *completed* move (`reset_attack_state`'s two
    callers are both on the movement path), not to the tick itself."""
    import random

    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(7))
    # Freeze everything that can move, then advance one tick.
    if sim.state.alien is not None:
        sim.state.alien.alive = False
    sim.state.jones_caught = True
    sim.advance()
    assert sound.MOVEMENT not in [c.effect for c in sim.state.sound_cues]
    assert sound.GRILLE not in [c.effect for c in sim.state.sound_cues]


# --- Jones's run (R-39, D-089) ----------------------------------------------

def _crew(room: str, *, alive: bool = True, in_duct: bool = False):
    from alien_remake.core.crew import CrewMember

    return CrewMember(id="ripley", name="Ripley", role="WARRANT OFFICER",
                      room_id=room, alive=alive, in_duct=in_duct)


def test_jones_runs_only_when_a_crew_member_is_selected_in_his_room() -> None:
    """[C $88CC] the four tests in `guard_6580`, in order."""
    from alien_remake.render.play import jones_run_armed

    # All four pass.
    assert jones_run_armed("galley", False, _crew("galley"))
    # `$88F9 CMP $64F7` — different room.
    assert not jones_run_armed("galley", False, _crew("bridge"))
    # `$8901 BEQ` — nothing selected.
    assert not jones_run_armed("galley", False, None)
    # `$8907 LDA $6501,Y / BNE` — the selection is inside a duct.
    assert not jones_run_armed("galley", False, _crew("galley", in_duct=True))
    # No cat left to run.
    assert not jones_run_armed("galley", True, _crew("galley"))
    assert not jones_run_armed(None, False, _crew("galley"))


def test_jones_frames_are_the_roms_five_slot_cycle() -> None:
    """[C $4F7A] `INC $64C0` from $C4, wrapping at `CMP #$C9` — five frames."""
    from alien_remake.render.play import _JONES_FRAMES, _SPRITE_SLOT_BASE

    slots = tuple(i + _SPRITE_SLOT_BASE for i in _JONES_FRAMES)
    assert slots == (0xC4, 0xC5, 0xC6, 0xC7, 0xC8)


def test_jones_frames_decode_to_a_moving_quadruped() -> None:
    """The five slots must actually differ (a run cycle, not one repeated
    glyph) and each must carry ink — the evidence that $C4-$C8 is an animation
    rather than an arbitrary five-slot window."""
    from alien_remake.render.play import _JONES_FRAMES
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    if not charset.exists():
        pytest.skip("out/charset.bin not present")
    tiles = load(charset)
    bitmaps = [tuple(tuple(r) for r in tiles.sprites[i]) for i in _JONES_FRAMES]
    assert len(set(bitmaps)) == 5, "frames should all differ"
    for bmp in bitmaps:
        assert any(any(row) for row in bmp)


def test_jones_run_geometry_matches_the_rom() -> None:
    """[C $4F5E/$4F65/$4FFC] X starts at 0, steps 4, ends at $F0; Y is $92."""
    from alien_remake.render.play import _JONES_Y
    from alien_remake.render.layout import _JONES_X_END, _JONES_X_START, _JONES_X_STEP

    assert (_JONES_X_START, _JONES_X_STEP, _JONES_X_END) == (0x00, 4, 0xF0)
    assert _JONES_Y == 0x92
    # 60 ticks to cross, at the IRQ rate — a brief dash, not a permanent marker.
    assert (_JONES_X_END - _JONES_X_START) // _JONES_X_STEP == 60


# --- the game's own sound legend (D-093) -------------------------------------

def test_the_demo_captions_match_the_prg_strings() -> None:
    """[C $4390] The DECK PLAN KEY screen plays each sound under a caption.

    This is the naming evidence for the whole SFX set: it confirms the
    grille/movement split independently of `reset_attack_state`'s `$651B`
    branch, and it names the tracker alarm outright.
    """
    rom = _prg()

    def text(addr: int, n: int) -> str:
        out = []
        for b in rom[addr - _LOAD_ADDR : addr - _LOAD_ADDR + n]:
            c = b & 0x7F
            out.append(chr(64 + c) if 1 <= c <= 26 else " ")
        return " ".join("".join(out).split())

    assert text(0x44C1, 21) == sfx.DEMO_CAPTION_STEM
    assert text(0x44D6, 42) == sfx.DEMO_CAPTIONS["heartbeat"]
    assert text(0x4500, 42) == sfx.DEMO_CAPTIONS["grille"]
    assert text(0x4554, 42) == sfx.DEMO_CAPTIONS["movement"]
    assert text(0x452A, 42) == sfx.DEMO_CAPTIONS["tracker_alarm"]


def test_the_demo_plays_each_sound_right_after_its_caption() -> None:
    """The pairing is the evidence, so pin the call sites too: caption copy,
    then the sound, in that order."""
    rom = _prg()
    # $439F JSR sfx_blip_a, $43B8 JSR sfx_blip_b, $43CB LDA #$21 / STA $64B6
    assert rom[0x439F - _LOAD_ADDR : 0x43A2 - _LOAD_ADDR] == bytes((0x20, 0x42, 0x4E))
    assert rom[0x43B8 - _LOAD_ADDR : 0x43BB - _LOAD_ADDR] == bytes((0x20, 0x5C, 0x4E))
    assert rom[0x43CB - _LOAD_ADDR : 0x43D0 - _LOAD_ADDR] == bytes(
        (0xA9, 0x21, 0x8D, 0xB6, 0x64)
    )
    # $436C JSR fear_alert — the heartbeat, for the first caption.
    assert rom[0x436C - _LOAD_ADDR : 0x436F - _LOAD_ADDR] == bytes((0x20, 0x16, 0x4E))


def test_tracker_alarm_is_a_pulse_train_at_the_roms_divider() -> None:
    """[C $65CB] `$4D03 = $12`, pulsed by the IRQ at `$4DD7` — 18 jiffies."""
    rom = _prg()
    assert rom[0x65C9 - _LOAD_ADDR : 0x65CE - _LOAD_ADDR] == bytes(
        (0xA9, 0x12, 0x8D, 0x03, 0x4D)
    )
    assert sfx.TRACKER_DIVIDER == 0x12
    assert sfx.TRACKER_PERIOD_S == pytest.approx(0.30, abs=1e-6)
    pcm = sfx.render_pulse(
        sfx.TRACKER_VOICE_SETUP, sfx.TRACKER_VOICE, sfx.TRACKER_CONTROL_ON,
        sfx.TRACKER_DIVIDER, periods=3, sample_rate=22_050,
    )
    assert len(pcm) // 2 == 3 * int(0.30 * 22_050)


def test_heartbeat_rate_is_the_roms_composure_ladder() -> None:
    """[C $4E16] 40/30/23/15 IRQ ticks for composure >=4/3/2/else — the heart
    **races** as the character loses their nerve (D-061)."""
    rom = _prg()
    assert rom[0x4E1D - _LOAD_ADDR : 0x4E1F - _LOAD_ADDR] == bytes((0xA9, 0x28))
    assert rom[0x4E2F - _LOAD_ADDR : 0x4E31 - _LOAD_ADDR] == bytes((0xA9, 0x1E))
    assert rom[0x4E38 - _LOAD_ADDR : 0x4E3A - _LOAD_ADDR] == bytes((0xA9, 0x17))
    assert rom[0x4E3D - _LOAD_ADDR : 0x4E3F - _LOAD_ADDR] == bytes((0xA9, 0x0F))
    assert [sfx.heartbeat_divider(c) for c in (5, 4, 3, 2, 1, 0)] == [40, 40, 30, 23, 15, 15]
    # And it agrees with the value the sim already used for the visual pulse.
    from alien_remake.core import constants
    for c in range(6):
        assert sfx.heartbeat_divider(c) == constants.heartbeat_divider(c)


def test_tracker_alarm_is_not_selection_gated() -> None:
    """The player reports it sounds whoever is selected, and the ROM agrees:
    `$8DF0`'s only guard is "no attack sequence running" (`$6562`)."""
    cue = SoundCue(sound.TRACKER_ALARM)
    for selected in (None, "ripley", "parker"):
        assert sound.audible(cue, selected, attacking=False)
    assert not sound.audible(cue, "ripley", attacking=True)


def test_the_tracker_ping_is_a_looped_pulse_not_a_per_detection_cue() -> None:
    """**[C $4DD7/$4D03] D-150 — the ping is a continuous IRQ pulse.**

    `$4DD7` counts `$64B8` down and, on each wrap, re-gates voice 3 with
    whatever `$64B6` holds — reloading the divider from **`$4D03` = `$12` =
    18 IRQ ticks** (60/18 ~= 3.3 Hz). So while the alarm latch is armed the
    ping simply runs at that fixed rate; nothing fires a fresh sound per
    detection. The remake used to push a one-shot `SoundCue` every time a
    scan found something, stacking overlapping clips — the "pings are fast"
    the player reported.
    """
    import random

    from alien_remake.core.sim import Simulation

    # The divider is the ROM's own byte, not a chosen rate.
    rom = _prg()
    assert rom[0x4D03 - _LOAD_ADDR] == 0x12
    assert sfx.TRACKER_DIVIDER == 0x12
    assert sfx.TRACKER_PERIOD_S == pytest.approx(0x12 / sfx.IRQ_HZ)

    sim = Simulation(rng=random.Random(3))
    user = next(c for c in sim.state.crew.values() if c.alive)
    sim.state.sound_cues.clear()
    sim._use_tracker(user.id)
    # Whatever the scan concludes, it must not raise a per-detection cue.
    assert sound.TRACKER_ALARM not in [c.effect for c in sim.state.sound_cues]


# --- the attack composite (R-40, D-096) --------------------------------------

def test_attack_composite_geometry_matches_sub_4e87() -> None:
    """[C $4E87] the setup routine's own coordinates, expansion and colour."""
    from alien_remake.render.play import (
        _ATTACK_COLOUR,
        _ATTACK_EXPAND,
        _ATTACK_X,
        _ATTACK_Y,
    )
    rom = _prg()
    # $D01D / $D017 = $F0 -> sprites 4-7 expanded in both axes.
    assert rom[0x4EA4 - _LOAD_ADDR : 0x4EAC - _LOAD_ADDR] == bytes(
        (0xA9, 0xF0, 0x8D, 0x17, 0xD0, 0x8D, 0x1D, 0xD0)
    )
    assert _ATTACK_EXPAND == 2
    # X: $5A to sprites 4 and 6, $8A to sprites 5 and 7.
    assert rom[0x4EAC - _LOAD_ADDR : 0x4EB4 - _LOAD_ADDR] == bytes(
        (0xA9, 0x5A, 0x8D, 0x08, 0xD0, 0x8D, 0x0C, 0xD0)
    )
    assert rom[0x4EB4 - _LOAD_ADDR : 0x4EBC - _LOAD_ADDR] == bytes(
        (0xA9, 0x8A, 0x8D, 0x0A, 0xD0, 0x8D, 0x0E, 0xD0)
    )
    assert _ATTACK_X == (0x5A, 0x8A)
    # Y: $37 and $8B are the two raster bands ($4D72 / $4D9E), $61 is 6/7.
    assert rom[0x4D72 - _LOAD_ADDR : 0x4D74 - _LOAD_ADDR] == bytes((0xA9, 0x8B))
    assert rom[0x4D9E - _LOAD_ADDR : 0x4DA0 - _LOAD_ADDR] == bytes((0xA9, 0x37))
    assert rom[0x4EBC - _LOAD_ADDR : 0x4EBE - _LOAD_ADDR] == bytes((0xA9, 0x61))
    assert _ATTACK_Y == (0x37, 0x61, 0x8B)
    assert _ATTACK_COLOUR == 0x05                      # $4E8C LDA #$05


def test_the_six_cells_abut_exactly() -> None:
    """The spacing **is** the proof that this is one picture: an expanded
    sprite is 48x42, and the cells are exactly 48 apart in x and 42 in y, so
    they tile edge to edge with no gap and no overlap."""
    from alien_remake.render.play import _ATTACK_EXPAND, _ATTACK_X, _ATTACK_Y

    assert _ATTACK_X[1] - _ATTACK_X[0] == 24 * _ATTACK_EXPAND
    assert _ATTACK_Y[1] - _ATTACK_Y[0] == 21 * _ATTACK_EXPAND
    assert _ATTACK_Y[2] - _ATTACK_Y[1] == 21 * _ATTACK_EXPAND


def test_attack_slots_follow_update_1s_adc_chain() -> None:
    """[C $4EFE-$4F15] `update_1` walks `ADC #$04` five times from `$A0 + f`;
    `begin_active_play ($4F95)` supplies the sixth as a **static** `$B4`."""
    from alien_remake.render.play import _ATTACK_SLOTS, _ATTACK_STATIC_SLOT

    rom = _prg()
    assert rom[0x4F95 - _LOAD_ADDR : 0x4F9A - _LOAD_ADDR] == bytes(
        (0xA9, 0xB4, 0x8D, 0x07, 0x4D)
    )
    assert _ATTACK_STATIC_SLOT == 0xB4
    flat = [s for row in _ATTACK_SLOTS for s in row]
    assert flat == [0xA0, 0xA4, 0xA8, 0xAC, 0xB0, None]


def test_attack_frames_are_the_roms_ping_pong_table() -> None:
    """[C $4EDC] `tbl_alien_anim` — 12 steps over 4 frames, out and back."""
    from alien_remake.render.play import _ATTACK_FRAMES

    rom = _prg()
    assert bytes(_ATTACK_FRAMES) == rom[0x4EDC - _LOAD_ADDR : 0x4EE8 - _LOAD_ADDR]
    assert _ATTACK_FRAMES == (0, 1, 1, 2, 2, 3, 3, 2, 2, 1, 1, 0)
    assert set(_ATTACK_FRAMES) == {0, 1, 2, 3}
    # A ping-pong reads as one creature moving, not a jump-cut loop.
    assert _ATTACK_FRAMES == tuple(reversed(_ATTACK_FRAMES))


def test_the_composite_cells_all_carry_ink() -> None:
    """Six blank-free cells is what makes this one picture rather than an
    arbitrary six-slot window — the same check that identified Jones."""
    from pathlib import Path

    from alien_remake.render.play import (
        _ATTACK_SLOTS,
        _ATTACK_STATIC_SLOT,
        _SPRITE_SLOT_BASE,
    )
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    if not charset.exists():
        pytest.skip("out/charset.bin not present")
    tiles = load(charset)
    for frame in range(4):
        for row in _ATTACK_SLOTS:
            for base in row:
                slot = _ATTACK_STATIC_SLOT if base is None else base + frame
                bmp = tiles.sprites[slot - _SPRITE_SLOT_BASE]
                assert any(any(r) for r in bmp), f"slot ${slot:02X} is blank"


# --- P2-6: the victim and android pools, byte-checked ------------------------

def test_victim_and_android_pools_match_the_rom_tables() -> None:
    """[C $506E/$507E] Both are 16-entry RNG lookup tables, not "any crew".

    A player recalled the android being "a random member of the crew". It is
    random — but drawn from a **four-name pool**, and the victim from a
    **three-name pool**. Pinned to the PRG bytes so neither list can drift.
    """
    from alien_remake.core import constants
    from alien_remake.core import gamedata_snapshot as data

    rom = _prg()
    names = ["(alien)"] + [n.strip().lower() for n in data.CREW_NAMES]

    victim = rom[0x50EC - _LOAD_ADDR : 0x50FC - _LOAD_ADDR]
    android = rom[0x50FC - _LOAD_ADDR : 0x510C - _LOAD_ADDR]
    assert len(victim) == len(android) == 16          # indexed by `rng $888F`

    assert sorted({names[s] for s in victim}) == sorted(
        constants.OPENING_VICTIM_CANDIDATES
    )
    assert sorted({names[s] for s in android}) == sorted(
        constants.ANDROID_CANDIDATES
    )
    # The android pool is uniform (4 x 4); the victim pool is not (6/5/5).
    assert [list(android).count(s) for s in (1, 2, 4, 6)] == [4, 4, 4, 4]


def test_the_android_is_rerolled_until_it_differs_from_the_victim() -> None:
    """[C $5081 `CMP $64C2` / $5084 `BEQ $506A`] — and the branch target is the
    **victim** roll, so a collision re-rolls *both*, not just the android."""
    rom = _prg()
    assert rom[0x507E - _LOAD_ADDR : 0x5086 - _LOAD_ADDR] == bytes((
        0xB9, 0xFC, 0x50,        # LDA $50FC,Y
        0xCD, 0xC2, 0x64,        # CMP $64C2   (the victim)
        0xF0, 0xE4,              # BEQ $506A   (re-roll the victim too)
    ))


# --- P2-12 / P2-18: border feedback and the engine fires ---------------------

def test_border_flash_matches_wait_keypress_flash() -> None:
    """[C $8660] `INC $D020` per input poll, restored to `#$06` on exit."""
    rom = _prg()
    assert rom[0x8660 - _LOAD_ADDR : 0x8663 - _LOAD_ADDR] == bytes(
        (0xEE, 0x20, 0xD0)                       # INC $D020
    )
    assert rom[0x8670 - _LOAD_ADDR : 0x8675 - _LOAD_ADDR] == bytes(
        (0xA9, 0x06, 0x8D, 0x20, 0xD0)           # LDA #$06 / STA $D020
    )
    from alien_remake.render import c64
    from alien_remake.render.pygame_app import _BORDER_COLOUR, _BORDER_FLASH_FRAMES

    assert _BORDER_FLASH_FRAMES > 0
    assert _BORDER_COLOUR == c64.rgb(6)           # what it returns to


def test_only_the_engine_rooms_can_catch_fire() -> None:
    """**[C $55A9/$55AD] P2-18.** `damage_room_b` writes the FIGHT FIRE special
    only for room indices `$11`-`$13`, so the option belongs to a burning
    **engine** room — not to whoever is carrying the extinguisher."""
    from alien_remake.core import constants
    from alien_remake.core import gamedata_snapshot as data
    from alien_remake.core.menu import FIRE_ROOM_SLUGS

    rom = _prg()
    # CPX #$11 / BCC ... CPX #$14 / BCS ... LDA #$06 / STA $5753,X
    assert rom[0x55A9 - _LOAD_ADDR : 0x55AB - _LOAD_ADDR] == bytes((0xE0, 0x11))
    assert rom[0x55AD - _LOAD_ADDR : 0x55AF - _LOAD_ADDR] == bytes((0xE0, 0x14))
    assert rom[0x55B1 - _LOAD_ADDR : 0x55B6 - _LOAD_ADDR] == bytes(
        (0xA9, 0x06, 0x9D, 0x53, 0x57)
    )
    assert constants.FIRE_ROOM_INDICES == (0x11, 0x12, 0x13)
    assert FIRE_ROOM_SLUGS == {data.ROOM_SLUGS[i] for i in (0x11, 0x12, 0x13)}
    # D-123: with the name-table gap honoured, $11-$13 are ENGINE 1/2/3.
    assert [data.ROOM_NAMES[i].strip() for i in (0x11, 0x12, 0x13)] == [
        "Engine 1", "Engine 2", "Engine 3"
    ]


def test_fight_fire_is_offered_by_the_burning_room_not_the_extinguisher() -> None:
    import random

    from alien_remake.core.menu import FIRE_ROOM_SLUGS, crew_entries
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    fire_room = sorted(FIRE_ROOM_SLUGS)[0]

    def specials() -> list[str]:
        return [
            e.label for e in crew_entries(sim, crew.id)
            if e.category.name == "SPECIAL"
        ]

    from alien_remake.core import constants as _c
    from alien_remake.core.alien import add_room_damage

    crew.room_id = fire_room
    assert "Fight Fire" not in specials()          # no alarm yet
    # **D-164** — drive it through real damage rather than poking the alarm:
    # the option is armed by `$55B1 LDA #$06 / STA $5753,X`, which the remake
    # models as `room_fire`, and that write sits on the 4..14 branch only.
    add_room_damage(sim.state, fire_room, _c.ROOM_ALARM_DAMAGE_THRESHOLD)
    assert sim.state.room_alarm[fire_room] == 1
    assert "Fight Fire" in specials()

    # A non-engine room's alarm arms no fire: `$55A9 CPX #$11 / BCC` skips
    # the `$5753` write for anything outside the engine band.
    other = next(
        r for r in sim.ship.rooms if r not in FIRE_ROOM_SLUGS
    )
    crew.room_id = other
    add_room_damage(sim.state, other, _c.ROOM_ALARM_DAMAGE_THRESHOLD)
    assert "Fight Fire" not in specials()


def test_a_critical_engine_room_never_gets_fight_fire_back() -> None:
    """**[C $5594/$5658/$55B1] D-164** — the sharp end of the fire system.

    `damage_room_b` splits at 15: below it, stage-1 alarm **and** `$55B1`
    arming FIGHT FIRE; at or above it, the routine jumps to `$5658`, latches
    `$651C,X` to **2**, and never reaches `$55B1`. So once an engine room is
    past the critical threshold, extinguishing it is a **one-shot** — the
    option is never re-armed and the room is left to burn to the breach.
    """
    import random

    from alien_remake.core import constants as _c
    from alien_remake.core.alien import add_room_damage
    from alien_remake.core.menu import FIRE_ROOM_SLUGS, crew_entries
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    room = sorted(FIRE_ROOM_SLUGS)[0]
    crew.room_id = room

    def specials() -> list[str]:
        return [
            e.label for e in crew_entries(sim, crew.id)
            if e.category.name == "SPECIAL"
        ]

    add_room_damage(sim.state, room, _c.ROOM_ALARM_DAMAGE_THRESHOLD)
    assert "Fight Fire" in specials()

    # Put it out ($58CC/$58CF clear both cells) and let it burn back up past 15.
    sim.state.room_alarm.pop(room, None)
    sim.state.room_fire.pop(room, None)
    add_room_damage(sim.state, room, _c.ROOM_ALARM_CRITICAL_THRESHOLD)

    assert sim.state.room_alarm[room] == _c.ROOM_ALARM_STAGE_CRITICAL   # $5667
    assert room not in sim.state.room_fire, "$55B1 is unreachable past 15"
    assert "Fight Fire" not in specials(), "the option must not come back"


def test_an_unfought_engine_fire_spreads() -> None:
    """[C $5684] `INC $64CE / BNE rts` — once per 256 passes, every lit fire
    room takes another point of damage."""
    import random

    from alien_remake.core import constants
    from alien_remake.core.menu import FIRE_ROOM_SLUGS
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    if sim.state.alien is not None:
        sim.state.alien.alive = False          # isolate the fire from the Alien
    room = sorted(FIRE_ROOM_SLUGS)[0]
    sim.state.room_damage[room] = 5
    sim.state.room_alarm[room] = 1
    before = sim.state.room_damage[room]
    for _ in range(constants.FIRE_SPREAD_EVERY_TICKS + 1):
        sim.advance()
    assert sim.state.room_damage[room] > before


# --- P2-7: acting while wounded is slow --------------------------------------

def test_action_delay_tables_match_the_prg() -> None:
    """**[C $4042] `compute_action_delay`** runs before ATTACK (`$48FC`), USE
    (`$7B6E`) and GET/LEAVE ITEM (`$8460`), and **adds** to the character's own
    countdown (`$405D LDA $64EE,Y` ... `$4064 STA $64EE,Y`)."""
    from alien_remake.core import constants

    rom = _prg()
    block = rom[0x4029 - _LOAD_ADDR : 0x4042 - _LOAD_ADDR]
    assert block[:6] == bytes((0x00, 0x00, 0x00, 0x00, 0x30, 0x10))
    # $402B indexed by health, $4032 by crew slot.
    health_tbl = [rom[0x402B - _LOAD_ADDR + h] for h in range(7)]
    slot_tbl = [rom[0x4032 - _LOAD_ADDR + s] for s in range(1, 8)]
    assert health_tbl == list(constants.ACTION_DELAY_BY_HEALTH)
    assert slot_tbl == list(constants.ACTION_DELAY_BY_SLOT[1:])


def test_a_wounded_crew_member_is_punishingly_slow() -> None:
    """The health term dominates: +48 ticks at 2 health, +16 at 3, nothing from
    4 up. At the measured 7.886 Hz main loop that is ~7 s against ~0.9 s — a
    wounded crew member is not just weaker, they are visibly sluggish."""
    from alien_remake.core import constants

    healthy = constants.action_delay(1, 6)
    hurt = constants.action_delay(1, 2)
    assert constants.ACTION_DELAY_BY_HEALTH[2] == 48
    assert constants.ACTION_DELAY_BY_HEALTH[3] == 16
    assert constants.ACTION_DELAY_BY_HEALTH[4] == 0
    assert hurt > 5 * healthy


def test_taking_an_item_makes_the_crew_member_busy() -> None:
    import random

    from alien_remake.core.orders import Order, OrderType
    from alien_remake.core.sim import Simulation

    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    item = next(i for i in sim.state.items.values() if i.room_id == crew.room_id)
    crew.step_timer = 0
    sim._apply_order(Order(crew.id, OrderType.GET_ITEM, item.id))
    assert crew.step_timer > 0, "acting should cost time"


# --- P2-15: the intro filter, settled by a live capture ----------------------

def test_the_intro_filter_base_matches_the_live_capture() -> None:
    """**[C-live P2-15]** A 240-sample capture of the running disk shows the
    intro plays with `$D417 = $F3` (resonance 15, voices 1+2 routed through the
    filter), `$D418 = $9F` (volume 15, low-pass, voice 3 muted) and — in 100%
    of samples — `$D415/$D416 = $00/$00`.

    So the cutoff register never moves for the whole piece and **every audible
    voice is filtered by whatever FC=0 means**. The generic `30 + FC*5.8` line
    put that at 30 Hz, which crushes the tune; the 6581's measured minimum is
    ~220 Hz. This pins the constant that decides the intro's character.
    """
    from alien_remake.audio.sid import SidSynth

    synth = SidSynth()
    synth.write(0x15, 0x00)
    synth.write(0x16, 0x00)
    synth.write(0x17, 0xF3)
    synth.write(0x18, 0x9F)
    # The coefficient is 2*sin(pi*fc/fs); invert it to recover the cutoff.
    import math

    fc = math.asin(min(1.0, synth._f_coef / 2.0)) * synth.sample_rate / math.pi
    assert 200.0 < fc < 240.0, f"FC=0 should sit near 220 Hz, got {fc:.1f}"

    # ...and full scale still reaches the top of the 6581's range.
    synth.write(0x15, 0x07)
    synth.write(0x16, 0xFF)
    fc_max = 220.0 + 0x7FF * 5.8
    assert 11_000 < fc_max < 13_000


def test_the_captured_filter_registers_are_what_we_model() -> None:
    """The capture's settled values, recorded so a future change to the
    filter path has to reckon with the real machine's numbers."""
    from alien_remake.audio.sid import SidSynth

    synth = SidSynth()
    for reg, value in ((0x15, 0x00), (0x16, 0x00), (0x17, 0xF3), (0x18, 0x9F)):
        synth.write(reg, value)
    assert synth.regs[0x18] & 0x0F == 15          # volume 15
    assert synth.regs[0x18] & 0x10                # low-pass
    assert synth.regs[0x18] & 0x80                # voice 3 muted (3OFF)
    assert synth.regs[0x17] & 0x07 == 0x03        # voices 1+2 filtered
    assert (synth.regs[0x17] >> 4) & 0x0F == 15   # resonance at maximum


def test_the_captured_chip_state_is_what_the_filter_model_assumes() -> None:
    """**[C-live D-109]** 60 samples of `vice_sid_get_state` while the title
    tune plays settle every filter field at 100%: cutoff 0/0, resonance 15,
    low-pass, voices 1+2 filtered, voice 3 muted, volume 15.

    Taken through the chip-state API rather than by reading `$D400`-`$D418`,
    which are write-only (D-108). Pinned so the filter path cannot drift away
    from the machine's own numbers.
    """
    from alien_remake.audio.sid import SidSynth

    synth = SidSynth()
    for reg, value in ((0x15, 0x00), (0x16, 0x00), (0x17, 0xF3), (0x18, 0x9F)):
        synth.write(reg, value)

    fc_reg = ((synth.regs[0x16] << 3) | (synth.regs[0x15] & 0x07)) & 0x7FF
    assert fc_reg == 0, "the captured cutoff register is zero"
    assert (synth.regs[0x17] >> 4) & 0x0F == 15        # filter_resonance
    assert synth.regs[0x17] & 0x01 and synth.regs[0x17] & 0x02   # voices 1+2
    assert not synth.regs[0x17] & 0x04                # voice 3 not filtered
    assert synth.regs[0x18] & 0x10                    # lowpass
    assert not synth.regs[0x18] & 0x20                # not bandpass
    assert not synth.regs[0x18] & 0x40                # not highpass
    assert synth.regs[0x18] & 0x80                    # voice3_off
    assert synth.regs[0x18] & 0x0F == 15              # volume


# --- P3-4 / P3-12: the attack blanks the map, and the siren loops ------------

def test_the_attack_sequence_blanks_the_map_first() -> None:
    """**[C $8D1A] P3-4.** `begin_active_seq` calls `clear_map_colors ($7EE5)`
    — which fills the whole 30x18 colour area with 0 — **before**
    `begin_active_play ($4F90)`. Black ink on a black background makes the deck
    plan vanish, so the Alien appears over empty space rather than on top of a
    still-visible map."""
    rom = _prg()
    assert rom[0x8D1A - _LOAD_ADDR : 0x8D20 - _LOAD_ADDR] == bytes((
        0x20, 0xE5, 0x7E,        # JSR clear_map_colors
        0x20, 0x90, 0x4F,        # JSR begin_active_play
    ))
    # ...and `clear_map_colors` really does write zero over 30x18.
    assert rom[0x7EEE - _LOAD_ADDR : 0x7EF4 - _LOAD_ADDR] == bytes((
        0xA9, 0x00, 0xA0, 0x00, 0x91, 0xFB
    ))


def test_the_renderer_hides_the_deck_while_attacking() -> None:
    import os
    from pathlib import Path

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame = pytest.importorskip("pygame")
    from alien_remake.render import c64
    from alien_remake.render.pygame_app import PygameRenderer
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    if not charset.exists():
        pytest.skip("out/charset.bin not present")
    r = PygameRenderer(scale=2, tiles=load(charset), intro_wav=None)
    try:
        r._surface.fill((0, 0, 0))
        r._attacking = True
        r._frame_count = 0
        r._draw_attack_animation()
        seen = {
            tuple(r._surface.get_at((x, y)))[:3]
            # Native coordinates: the `* 2` was a hardcoded copy of the old
            # draw scale (DISC-242).
            for x in range(0, 240, 6)
            for y in range(0, 136, 6)
        }
        # Only black and the Alien's own green ($05) — no map ink survives.
        assert seen <= {(0, 0, 0), c64.rgb(0x05)}, f"map showing through: {seen}"
    finally:
        pygame.quit()


def test_the_alert_is_a_loop_not_a_one_shot() -> None:
    """**P3-12.** `begin_active_play` gates voices 1+2 on and leaves them on;
    `irq_alt_handler ($4E76)` sweeps them every IRQ for as long as `$64BB` is
    set. Our clip is one LFO period, so it has to be looped — playing it once
    is a "small squeak and then nothing"."""
    from alien_remake.audio import sfx

    # One period is short — far shorter than any attack.
    assert sfx.ALERT_PERIOD_S < 0.6
    # And `reset_attack_state ($8C80)`, which ends the sequence, is the same
    # routine that plays the movement/grille blip — so the blip is the stop cue.
    rom = _prg()
    assert rom[0x8C80 - _LOAD_ADDR : 0x8C88 - _LOAD_ADDR] == bytes((
        0xA9, 0x00, 0x8D, 0xB6, 0x64, 0x8D, 0x62, 0x65
    ))


def test_siren_survives_an_unrelated_movement_blip() -> None:
    """**[C $64BB] P5-3/P7-12 — the third report of the same regression.**

    `$64BB` is a **latch**: it stays set for the whole attack sequence and the
    blip routines (`$4E42`/`$4E5C`) test it directly. `play_sound_cues` used to
    recompute its local `attacking` flag from *only the current tick's cues*,
    but the ATTACK_ALERT cue is raised on exactly one tick (the wound lands).
    So on every later tick `attacking` went back to False, and any *unrelated*
    crew member's movement/grille blip read `attacking=False`, passed
    `sound.audible`, and the renderer's own stop-on-blip logic killed the siren
    — the "small squeak and then nothing" reported three times.

    This must reproduce the failure through the same two-call sequence a real
    game loop uses, not by inspecting the ROM in isolation (that is what let
    the bug survive two previous "fixes").
    """
    import pygame

    from alien_remake.core.sound import ATTACK_ALERT, MOVEMENT, SoundCue
    from alien_remake.core.state import GameState
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(intro_wav=None)
    try:
        victim_id = "kane"
        r._menu = SimpleNamespace(selected_crew=victim_id)

        attack_tick = GameState()
        attack_tick.sound_cues = [SoundCue(ATTACK_ALERT, crew_id=victim_id)]
        played = r.play_sound_cues(attack_tick)
        assert played == ("attack_alert",)
        assert r._attacking

        # A later tick: some OTHER crew member's order completes and blips —
        # nothing to do with the attack still in progress.
        later_tick = GameState()
        later_tick.sound_cues = [SoundCue(MOVEMENT)]
        played = r.play_sound_cues(later_tick)

        assert "movement" not in played, "the blip should be muted mid-attack"
        assert r._attacking, "an unrelated blip must not stop the siren"
    finally:
        pygame.quit()


def test_switching_selection_away_stops_the_attack_composite() -> None:
    """**[C $8CE1] D-139 — user-requested behaviour.**

    `$8CE1 CPY $64FB` already gates the siren+animation to the SELECTED
    character at trigger time (D-090). This extends that gate to hold
    continuously: switching the CONTROL panel's selection away from the crew
    member under attack must drop the composite immediately (siren silenced,
    deck view restored), not leave it running until the next unrelated
    movement blip.
    """
    import pygame

    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.core.sound import ATTACK_ALERT, SoundCue
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(intro_wav=None)
    try:
        sim = Simulation()
        r._ship = sim.ship
        menu = MenuController(sim)
        r._menu = menu
        victim = next(c for c in sim.state.crew.values() if c.alive)
        other = next(
            c for c in sim.state.crew.values()
            if c.alive and c.id != victim.id
        )
        menu.selected_crew = victim.id

        sim.state.sound_cues = [SoundCue(ATTACK_ALERT, crew_id=victim.id)]
        r.play_sound_cues(sim.state)
        assert r._attacking
        assert r._attacking_crew_id == victim.id

        # The player selects someone else — the composite must end at once,
        # on the very next render, not wait for a movement/grille blip.
        menu.selected_crew = other.id
        r.render(sim.state, present=False)

        assert not r._attacking, "attack composite must stop on deselect"
        assert r._attacking_crew_id is None
    finally:
        pygame.quit()


def test_jones_run_loops_while_armed_and_finishes_the_crossing_on_stop() -> None:
    """**[C $4F65-$4F78] P3-15/D-146 — the run LOOPS; $F0 is only the stop line.**

    `update_3` adds 4 to sprite 3's X every step; at/past $F0 it checks the
    stop request `$64BA` — with none pending the 8-bit add wraps through
    $FF -> $00 and the cat re-enters from the left, looping seamlessly. When a
    stop IS pending (selection changed `$7732`, attack began `$4FA2`, map
    re-entry `$7083`), the run still finishes its current crossing and ends at
    the edge — never blanked mid-run. The remake used to one-shot the crossing
    and also killed the sprite instantly when the arming condition dropped.
    """
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    import random

    from alien_remake.core.sim import Simulation
    from alien_remake.render.play import _JONES_RATE
    from alien_remake.render.layout import _JONES_X_END
    from alien_remake.render.pygame_app import PygameRenderer
    from alien_remake.core.menu import MenuController

    r = PygameRenderer(intro_wav=None)
    try:
        sim = Simulation(rng=random.Random(0))
        r._ship = sim.ship
        r._menu = MenuController(sim)
        crew = next(c for c in sim.state.crew.values() if c.alive and c.room_id)
        r._menu.selected_crew = crew.id
        sim.state.jones_room_id = crew.room_id
        sim.state.jones_caught = False

        # Drive enough frames for well over one full crossing while armed:
        # the run must WRAP (x returns below the stop line), not end.
        wrapped = False
        seen_past_stop_line = False
        for _ in range(_JONES_RATE * 80):
            r.render(sim.state, present=False)
            x = r._jones_x
            assert x is not None, "the run must not end while armed"
            if x >= _JONES_X_END:
                seen_past_stop_line = True
            if seen_past_stop_line and x < _JONES_X_END:
                wrapped = True
        assert wrapped, "while armed the crossing must loop, not one-shot"

        # Drop the arming condition mid-crossing: the cat keeps going to the
        # right edge, then vanishes.
        sim.state.jones_room_id = next(
            room for room in sim.ship.rooms if room != crew.room_id
        )
        assert r._jones_x is not None
        for _ in range(_JONES_RATE * 80):
            r.render(sim.state, present=False)
            if r._jones_x is None:
                break
        assert r._jones_x is None, "a requested stop must end the run at the edge"
    finally:
        pygame.quit()


def test_jones_here_notice_is_the_roms_own_string_row_and_gates() -> None:
    """**[C $890C-$8917] D-149** — `guard_6580` copies the 22-byte string at
    `$884A` into `$07C0` (row 24, col 0) on the SAME path that arms the cat's
    run, past the SAME four gates. So the notice and the dash are one event.

    Pins the string against the PRG bytes and the row/gating against the ROM,
    so the notice can't drift to a different row or start showing when the
    animation doesn't.
    """
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    import random

    from alien_remake.core.sim import Simulation
    from alien_remake.core.menu import MenuController
    from alien_remake.render import c64
    from alien_remake.render.play import (
        _JONES_NOTICE,
        _JONES_NOTICE_COLOUR,
        _JONES_NOTICE_ROW,
    )
    from alien_remake.render.pygame_app import PygameRenderer

    # The ROM's own bytes: $884A, 22 of them, into $07C0 = row 24 col 0.
    rom = _prg()
    raw = rom[0x884A - _LOAD_ADDR : 0x884A - _LOAD_ADDR + 22]

    def dec(b: int) -> str:
        b &= 0x7F
        return chr(64 + b) if 1 <= b <= 26 else " "

    assert "".join(dec(b) for b in raw).strip() == _JONES_NOTICE
    assert 0x07C0 - 0x0400 == _JONES_NOTICE_ROW * 40    # row 24, col 0
    assert _JONES_NOTICE_COLOUR == 7                    # [C-live] yellow

    r = PygameRenderer(intro_wav=None)
    try:
        sim = Simulation(rng=random.Random(0))
        r._ship = sim.ship
        r._menu = MenuController(sim)
        crew = next(
            c for c in sim.state.crew.values()
            if c.alive and c.room_id and not c.in_duct
        )
        r._menu.selected_crew = crew.id
        s = 1  # DISC-242: the draw surface is native
        yellow = c64.rgb(_JONES_NOTICE_COLOUR)

        def notice_shown() -> bool:
            """Is anything written on row 24?

            This used to sample one pixel for yellow, on the assumption that the
            row is only coloured when the notice is up. It is not:
            `paint_map_colors ($7993)` fills rows 23-24 with `$07` on every
            redraw whether or not there is anything to say, so the band is
            yellow always and only the *ink* moves. Look for the black text.
            """
            y0 = _JONES_NOTICE_ROW * 8 * s
            return any(
                tuple(r._surface.get_at((x, y)))[:3] != yellow
                for y in range(y0, y0 + 8 * s)
                for x in range(0, 30 * 8 * s)
            )

        # Cat in an EMPTY room: row 24 stays blank. D-158 — "elsewhere" is not
        # enough on its own, because `guard_6580`'s untaken branch ($8932)
        # names any crew member who is in Jones's room whichever room the
        # player is watching. The row is blank only when nobody can see him.
        occupied = {c.room_id for c in sim.state.crew.values() if c.alive}
        sim.state.jones_room_id = next(
            room for room in sim.ship.rooms if room not in occupied
        )
        sim.state.jones_caught = False
        r.render(sim.state, present=False)
        assert not notice_shown()

        # Cat in the selected crew member's room: notice appears.
        sim.state.jones_room_id = crew.room_id
        r.render(sim.state, present=False)
        assert notice_shown()

        # Caught: gone again (guard_6580's `$6580` gate).
        sim.state.jones_caught = True
        r.render(sim.state, present=False)
        assert not notice_shown()
    finally:
        pygame.quit()


def test_tracker_ping_loops_while_armed_and_stops_when_disarmed() -> None:
    """**D-150** — the renderer must LOOP one pulse-train clip while the
    latch is armed and stop it the moment it clears (dropping the tracker,
    nothing in range, or an attack taking the voices). Retriggering a clip
    per detection is the "pings are fast" bug."""
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame

    from alien_remake.core.state import GameState
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(intro_wav=None)
    try:
        st = GameState()
        st.tracker_alarm = False
        r._update_tracker_ping(st)
        assert r._tracker_channel is None

        st.tracker_alarm = True
        r._update_tracker_ping(st)
        armed = r._tracker_channel
        # Repeated frames while still armed must NOT restart the clip.
        for _ in range(10):
            r._update_tracker_ping(st)
        assert r._tracker_channel is armed, "the loop must not be retriggered"

        # An attack takes the voices over ($8DF0 refuses to arm).
        r._attacking = True
        r._update_tracker_ping(st)
        assert r._tracker_channel is None
        r._attacking = False

        # Re-arms, then goes silent when the latch clears.
        r._update_tracker_ping(st)
        assert r._tracker_channel is not None
        st.tracker_alarm = False
        r._update_tracker_ping(st)
        assert r._tracker_channel is None
    finally:
        pygame.quit()

def test_clips_play_at_their_rendered_length_not_half_of_it() -> None:
    """**PV-25 / D-171 - the playback bug, not a synthesis bug.**

    `pygame.mixer.Sound(buffer=...)` reads its bytes as **raw samples already
    in the mixer's format**; it does not parse a RIFF container. The mixer
    initialises **stereo** and `sfx.wav_bytes` emits **mono**, so every clip
    was being consumed as interleaved stereo - exactly half the duration, an
    octave up, alternate samples split across the channels - with the 44-byte
    WAV header rendered as a click at the front. The synthesis was right the
    whole time, which is why the exported `.wav` files always sounded correct.

    Guards the fix (hand pygame a file-like object so it parses and converts)
    by comparing every effect's `Sound.get_length()` against the length of the
    PCM it was rendered from. A ratio of 0.5 is the bug returning.
    """
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame

    from alien_remake.audio import sfx
    from alien_remake.render.pygame_app import PygameRenderer

    r = PygameRenderer(intro_wav=None)
    try:
        init = pygame.mixer.get_init()
        if init is None:
            pytest.skip("no mixer available")
        rate = init[0]
        for effect in sfx.EFFECTS:
            clip = r._sound(effect)
            if clip is None:
                continue
            expected = len(sfx.render(effect, sample_rate=rate)) / 2 / rate
            assert clip.get_length() == pytest.approx(expected, rel=0.02), (
                f"{effect}: clip is {clip.get_length():.3f}s but was rendered "
                f"as {expected:.3f}s - mono PCM read as stereo?"
            )
    finally:
        pygame.quit()


def test_the_tracker_alarm_is_a_voice3_pulse_train_not_a_blip() -> None:
    """**PV-24 closed — every constant re-read out of the PRG.**

    The register said "the tracker's sound is not tied to a decoded routine;
    `sfx_blip_b` is a *candidate*". It is not a blip at all. The tracker is a
    **re-gated voice-3 pulse train**, and six independent sites in the image
    pin it::

        4DF5  LDA #$32 / STA $D40F      ; voice 3 freq hi (~752 Hz)
        4DFF  LDA #$08 / STA $D413      ; voice 3 AD: attack 0, decay 8
        65C9  LDA #$12 / STA $4D03      ; the IRQ divider = 18
        4DD7  DEC $64B8 / BPL           ; ...counted down by the IRQ,
        4DDC  LDA $4D03 / STA $64B8     ;    reloaded on each wrap,
        4DE2  LDA #$10 / STA $D412      ;    gate OFF (triangle),
        4DE7  LDA $64B6 / STA $D412     ;    then back to whatever $64B6 holds
        8DF6  LDA #$21 / STA $64B6      ; select_char_turn arms it (saw + gate)
        8C80  LDA #$00 / STA $64B6      ; reset_attack_state silences it
        43CB  LDA #$21 / STA $64B6      ; ...and the DECK PLAN KEY screen does
                                        ;    the same write under the caption
                                        ;    "THE TRACKER ALARM." - the game
                                        ;    naming its own sound.

    That last one is the tie the register was asking for.
    """
    rom = _prg()

    def at(addr: int, n: int) -> bytes:
        return rom[addr - _LOAD_ADDR: addr - _LOAD_ADDR + n]

    assert at(0x4DF5, 5) == bytes((0xA9, 0x32, 0x8D, 0x0F, 0xD4))   # freq hi
    assert at(0x4DFF, 5) == bytes((0xA9, 0x08, 0x8D, 0x13, 0xD4))   # AD
    assert at(0x65C9, 5) == bytes((0xA9, 0x12, 0x8D, 0x03, 0x4D))   # divider
    assert at(0x8DF6, 5) == bytes((0xA9, 0x21, 0x8D, 0xB6, 0x64))   # arm
    assert at(0x8C80, 5) == bytes((0xA9, 0x00, 0x8D, 0xB6, 0x64))   # silence
    assert at(0x43CB, 5) == bytes((0xA9, 0x21, 0x8D, 0xB6, 0x64))   # the demo

    # The IRQ's own re-gate sequence, byte for byte.
    assert at(0x4DD7, 0x16) == bytes((
        0xCE, 0xB8, 0x64,        # DEC $64B8
        0x10, 0x11,              # BPL $4DED
        0xAD, 0x03, 0x4D,        # LDA $4D03
        0x8D, 0xB8, 0x64,        # STA $64B8
        0xA9, 0x10,              # LDA #$10
        0x8D, 0x12, 0xD4,        # STA $D412
        0xAD, 0xB6, 0x64,        # LDA $64B6
        0x8D, 0x12, 0xD4,        # STA $D412
    ))

    # ...and the module's transcription agrees with all of it.
    assert sfx.TRACKER_CONTROL_ON == 0x21
    assert sfx.TRACKER_CONTROL_OFF == 0x10
    assert sfx.TRACKER_DIVIDER == 0x12
    assert dict((w.reg, w.value) for w in sfx.TRACKER_VOICE_SETUP) == {
        0x0F: 0x32, 0x13: 0x08,
    }
    assert sfx.DEMO_CAPTIONS["tracker_alarm"] == "THE TRACKER ALARM"


def test_the_siren_is_fully_determined_by_the_prg_no_oscilloscope_needed() -> None:
    """**PV-36 closed — its premise was wrong.**

    The register asked to "confirm the decoded attack siren against real
    hardware", on the grounds that this VICE implements no OSC3 (`$D41B`)
    reads (D-148). But nothing about the siren needs to be *read*: `$D41B` is
    a deterministic function of what the ROM itself writes.

    Voice 3 is set free-running at frequency `$0020` (`$4FB9 LDA #$00 / STA
    $D40F`, `$4FBE LDA #$20 / STA $D40E`). The SID's phase accumulator is 24
    bits and advances by `freq` every clock, and OSC3 on a sawtooth is its top
    byte — so one full ramp, i.e. one siren sweep, is

        2^24 / freq / clock  =  2^24 / 32 / 985248  =  0.532 s  =  1.879 Hz

    That is arithmetic on bytes in the image. This test derives it from the PRG
    rather than from the module's constant, so the loop is closed end to end:
    frequency bytes -> accumulator width -> LFO rate -> clip length.

    What real hardware would add is the analogue character of one particular
    SID revision — and 6581 and 8580 differ audibly *from each other*, so
    "real hardware" is not a single ground truth to confirm against. It is not
    a fact about the decode.
    """
    rom = _prg()

    def at(addr: int, n: int) -> bytes:
        return rom[addr - _LOAD_ADDR: addr - _LOAD_ADDR + n]

    # Voice 3's frequency, read out of the init block rather than assumed.
    assert at(0x4FB5, 5) == bytes((0xA9, 0x00, 0x8D, 0x0F, 0xD4))   # hi = $00
    assert at(0x4FBA, 5) == bytes((0xA9, 0x20, 0x8D, 0x0E, 0xD4))   # lo = $20
    freq = at(0x4FBB, 1)[0] | (at(0x4FB6, 1)[0] << 8)
    assert freq == 0x0020

    # ...and voice 3's control gets that same `$20` — **sawtooth with the gate
    # OFF** (`$4FBF STA $D412` stores the A still holding $20). No gate means
    # no envelope, so the oscillator free-runs and OSC3 is a plain ramp rather
    # than a note. That is the whole reason it can serve as an LFO.
    assert at(0x4FBF, 3) == bytes((0x8D, 0x12, 0xD4))

    derived_hz = freq * sfx.PAL_CLOCK_HZ / 2 ** 24
    assert sfx.ALERT_LFO_HZ == pytest.approx(derived_hz)
    assert derived_hz == pytest.approx(1.8792, abs=1e-3)
    assert sfx.ALERT_PERIOD_S == pytest.approx(1.0 / derived_hz)

    # The modulator the IRQ applies to that ramp, byte for byte — already
    # covered above, re-asserted here so this test stands alone as the whole
    # chain: osc3 -> voice 1 freq hi, and osc3 + $40 -> voice 2 freq hi.
    assert at(0x4E76, 13) == bytes((
        0xAD, 0x1B, 0xD4,        # LDA $D41B
        0x4A,                    # LSR A
        0x8D, 0x01, 0xD4,        # STA $D401
        0x18, 0x69, 0x40,        # CLC / ADC #$40
        0x8D, 0x08, 0xD4,        # STA $D408
    ))

    # And the rendered clip really is one whole period, so it loops seamlessly.
    pcm = sfx.render_alert(periods=1, sample_rate=22_050)
    assert len(pcm) // 2 == int(sfx.ALERT_PERIOD_S * 22_050)


def test_the_airlock_cue_survives_to_be_played() -> None:
    """**[C $5904] D-186 — the blowlock was silent, and the tests all passed.**

    `blowlock_sfx` writes voice 2 at `$5904`-`$5915` *inside the option
    handler*, before `$591F`/`$592E` even look at which way the flag is about
    to flip. Two consequences the remake had wrong:

    * The cue is raised by `apply_special_option`, but the app loop only
      drained cues **after** `sim.advance()` — whose first act is
      `sound_cues.clear()`. So the airlock crack was raised and discarded every
      single time, and nothing noticed because every existing sound test
      inspected `state.sound_cues` directly rather than the loop's ordering.
    * SEALLOCK reaches the same routine (both are option code 2), so **sealing
      makes the same noise as blowing**. Only the OPEN path raised it.
    """
    import random

    from alien_remake.core import sound as snd
    from alien_remake.core.sim import Simulation
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    for kind in (SpecialOptionType.OPEN_AIRLOCK, SpecialOptionType.SEAL_AIRLOCK):
        sim = Simulation(rng=random.Random(0))
        crew = next(c for c in sim.state.crew.values() if c.alive)
        crew.room_id = "corridor_6"                      # the lock controls
        assert sim.apply_special_option(
            SpecialOption(kind, room_id="airlock_1", crew_id=crew.id)
        )
        raised = [c.effect for c in sim.state.sound_cues]
        assert snd.AIRLOCK in raised, f"{kind.name} must make the noise"
        # ...and it is audible: `blowlock_sfx` has no `$64BB` guard, unlike the
        # movement blips, so nothing mutes it.
        cue = next(c for c in sim.state.sound_cues if c.effect == snd.AIRLOCK)
        assert snd.audible(cue, selected_id=None, attacking=True)
        assert snd.audible(cue, selected_id=None, attacking=False)

        # The ordering bug itself: a tick clears the list, so anything raised
        # by an option handler has to be drained before the next advance().
        sim.advance()
        assert snd.AIRLOCK not in [c.effect for c in sim.state.sound_cues], (
            "advance() clears cues — the app loop must drain at the click"
        )


def test_blowlock_reaches_the_speaker_through_the_real_click_path() -> None:
    """**[C $5904] D-187 — the loop ordering, exercised end to end.**

    D-186 fixed "the blowlock is silent" by draining inside the app loop's
    `poll_special_options` loop. That loop **never iterates**:
    `MenuController.fire()` applies orders and Special Options *straight to the
    sim* during `poll_input`, and nothing ever appends to `_pending_specials`.
    So the fix was dead code and the airlock stayed silent — which the player
    reported again.

    This test drives the path a keypress actually takes — `fire()` on the real
    panel row, then the drain — and asserts the effect comes back from
    `play_sound_cues`, i.e. that it reached the audio layer rather than merely
    being raised. Both previous attempts asserted on `state.sound_cues` and
    passed while the game was mute.
    """
    import os
    import random

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame

    from alien_remake.core import sound as snd
    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render.pygame_app import PygameRenderer

    renderer = PygameRenderer(intro_wav=None)
    try:
        for label in ("BlowLock.1", "BlowLock.2"):
            sim = Simulation(rng=random.Random(0))
            crew = next(c for c in sim.state.crew.values() if c.alive and c.awake)
            crew.room_id = "corridor_6"          # where the lock controls are
            menu = MenuController(sim)
            menu.selected_crew = crew.id
            renderer._menu = menu
            renderer._sim = sim

            entries = menu.entries()
            idx = next(i for i, e in enumerate(entries) if e.label == label)
            selectable = [i for i, e in enumerate(entries) if e.selectable]
            menu.cursor = selectable.index(idx)

            sim.state.sound_cues.clear()
            menu.fire()                          # == what poll_input does
            played = renderer.play_sound_cues(sim.state)   # == the app loop's drain
            assert snd.AIRLOCK in played, f"{label} never reached the audio layer"
    finally:
        pygame.quit()


def test_scuttling_flashes_the_border_yellow_until_it_is_cancelled() -> None:
    """**[C $5A26]** SCUTTLE NOSTROMO flashes the border until it resolves.

    `mainloop_sub_5a26` runs once per main-loop pass and toggles the bottom bit
    of `$D020` whenever the auto-destruct flag `$64CF` is set::

        5A26  LDA $64CF / BNE $5A2C
        5A2B  RTS
        5A2C  LDA $D020 / EOR #$01 / STA $D020
        5A34  DEC $657C

    `start_game` puts the border at `#$06` BLUE (`$7054`), so the toggle swaps
    it to `$07` YELLOW. `clear_result_flag ($58F6)` — the OVERRIDE path — zeroes
    the flag *and* writes `#$06` back explicitly (`$58FE`), so cancelling always
    leaves it blue rather than on whichever half of the toggle it stopped at.
    """
    from alien_remake.render import c64
    from alien_remake.render.play import PlayMixin
    from alien_remake.core.state import GameState

    blue, yellow = c64.rgb(c64.BLUE), c64.rgb(c64.YELLOW)
    state = GameState(crew={})

    # Not armed: steady blue whatever the tick parity.
    for tick in range(4):
        state.tick = tick
        assert PlayMixin._play_border(state) == blue

    # Armed: alternates once per pass.
    state.auto_destruct_ticks = 2550
    seen = []
    for tick in range(6):
        state.tick = tick
        seen.append(PlayMixin._play_border(state))
    assert seen == [blue, yellow] * 3, "the border must toggle every pass"

    # Cancelled mid-flash, on the yellow half: back to blue immediately.
    state.tick = 1
    state.auto_destruct_ticks = None
    assert PlayMixin._play_border(state) == blue


def test_brett_fills_the_opening_victims_room_from_the_roms_paired_tables() -> None:
    """**[C $5074-$5077] DISC-229** — the opening always seats survivors 3+3.

    The opening-death routine reads TWO tables with one RNG draw: `$50EC,Y`
    gives the victim's slot, and `$510C,Y` — same `Y` — gives a room that is
    stored to **`$793C`**, i.e. `$7935 + 7`, the slot-7 character's own
    location cell. Slot 7 is Brett (slot 0 is the Alien: its parallel health
    cell `$7D45` is tested against `#$32`, the 50-damage death threshold, at
    `$60D8`).

    Every entry pairs the victim with the room that victim started in, so
    Brett always backfills the vacancy and the opening is always three crew
    in COMMDCENTR and three in MESS. `$793D`'s AIRLOCK 1 entry for Brett is a
    parking slot the opening overwrites every game — he is never actually
    there in play, which is what the owner reported and what two live `$7935`
    captures confirmed (victim Kane -> Brett COMMDCENTR, victim Lambert ->
    Brett MESS).
    """
    from alien_remake.core.gamedata_snapshot import CREW_START_ROOMS, ROOM_SLUGS

    rom = _prg()
    victims = rom[0x50EC - _LOAD_ADDR : 0x50FC - _LOAD_ADDR]   # $50EC,Y
    brett_rooms = rom[0x510C - _LOAD_ADDR : 0x511C - _LOAD_ADDR]  # $510C,Y
    assert len(victims) == len(brett_rooms) == 16

    # The store target is Brett's slot, not the victim's: $793C - $7935 == 7.
    assert 0x793C - 0x7935 == 7

    # Only Dallas(1) / Kane(2) / Lambert(5) are ever the victim.
    assert set(victims) == {1, 2, 5}

    # Each entry sends Brett to the room that entry's victim started in.
    for y, (slot, room) in enumerate(zip(victims, brett_rooms)):
        expected = CREW_START_ROOMS[slot - 1]   # CREW_START_ROOMS is 0-based
        assert room == expected, (
            f"Y={y}: victim slot {slot} starts in "
            f"{ROOM_SLUGS[expected]} but Brett is sent to {ROOM_SLUGS[room]}"
        )

    # ...and the room is never AIRLOCK 1, Brett's own template entry.
    assert ROOM_SLUGS[CREW_START_ROOMS[6]] == "airlock_1"  # the parking slot
    assert all(ROOM_SLUGS[r] != "airlock_1" for r in brett_rooms)


def test_the_ending_strings_are_the_roms_own_bytes() -> None:
    """**DISC-230** — every ending line decoded from `ALIEN.prg`, mixed case.

    These were transcribed in ALL CAPS before DISC-215's case-bit fix. The
    ship-fate line at `$0478` (row 3) was missing from the remake entirely.
    """
    from alientools.gamedata import _screen_char
    from alien_remake.render import frontend as F

    rom = _prg()

    def txt(addr: int, n: int) -> str:
        return "".join(
            _screen_char(b) for b in rom[addr - _LOAD_ADDR : addr - _LOAD_ADDR + n]
        )

    assert txt(0x633C, 29) == F._ENDING_NOSTROMO_RETURNS
    assert txt(0x6359, 25) == F._ENDING_NOSTROMO_DESTROYED
    assert txt(0x6314, 40) == F._ENDING_BRINGS_BACK
    assert txt(0x6372, 17) == F._ENDING_ALIEN_DEAD
    assert txt(0x6383, 55) == F._ENDING_EGGS
    assert txt(0x63BA, 30) == F._ENDING_NARCISSUS
    assert txt(0x63D8, 13) == F._ENDING_ALL_CREW_LOST
    assert txt(0x63E5, 9) == F._ENDING_IS_INSANE
    assert txt(0x63EE, 10) == F._ENDING_SURVIVORS
    assert txt(0x63F8, 22) == F._ENDING_COMPETENCE
    assert txt(0x6475, 13) == F._ENDING_PRESS_ANY_KEY

    # ...at the ROM's own rows: row = ($addr - $0400) / 40, all at column 0
    # except the two the ROM itself indents.
    assert F._ENDING_ROWS["nostromo"] == (0x0478 - 0x0400) // 40 == 3
    assert F._ENDING_ROWS["alien"] == (0x04F0 - 0x0400) // 40 == 6
    assert F._ENDING_ROWS["ship"] == (0x0540 - 0x0400) // 40 == 8
    assert F._ENDING_ROWS["eggs"] == (0x0590 - 0x0400) // 40 == 10
    assert F._ENDING_ROWS["crew"] == (0x0608 - 0x0400) // 40 == 13
    assert F._END_SURVIVOR_HEADER_ROW == 13         # shares $0608 with the above
    assert F._END_SURVIVOR_FIRST_ROW == (0x0630 - 0x0400) // 40 == 14
    assert F._END_RATING_ROW == (0x0770 - 0x0400) // 40 == 22
    assert F._END_RATING_DIGIT_COL == (0x0783 - 0x0400) % 40 == 19
    assert F._END_PRESS_KEY_ROW == (0x07D8 - 0x0400) // 40 == 24
    assert F._END_PRESS_KEY_COL == (0x07D8 - 0x0400) % 40 == 24
    assert F._ENDING_BRINGS_BACK_COL == (0x0480 - 0x0400) % 40 == 8


def test_the_auto_destruct_countdown_banner_matches_the_rom() -> None:
    """**[C $5A3E-$5A63] DISC-230** — decoded, and now actually displayed.

    Two arms, one digit patched in. `$AB` is `$B0 - 5`, so the override
    warning counts down the *override* window (which expires at 5) while the
    destruct warning shows the raw minutes.
    """
    from alien_remake.core.constants import (
        AUTO_DESTRUCT_OVERRIDE_ABOVE,
        MALFUNCTION_MESSAGES,
        auto_destruct_banner,
    )

    rom = _prg()
    # $5A4A ADC #$AB / $5A58 ADC #$B0 — the two digit conversions.
    assert rom[0x5A4B - _LOAD_ADDR] == 0x69   # ADC #
    assert rom[0x5A4C - _LOAD_ADDR] == 0xAB
    assert rom[0x5A59 - _LOAD_ADDR] == 0x69   # ADC #
    assert rom[0x5A5A - _LOAD_ADDR] == 0xB0
    assert 0xB0 - 0xAB == AUTO_DESTRUCT_OVERRIDE_ABOVE
    # $5A46 CMP #$06 — the arm boundary.
    assert rom[0x5A47 - _LOAD_ADDR] == 0x06

    assert auto_destruct_banner(9) == "OVERRIDE OPTION EXPIRY  4 MINS"
    assert auto_destruct_banner(6) == "OVERRIDE OPTION EXPIRY  1 MINS"
    assert auto_destruct_banner(5) == "SHIP WILL DESTRUCT IN 5 MINS  "
    assert auto_destruct_banner(1) == "SHIP WILL DESTRUCT IN 1 MINS  "
    assert auto_destruct_banner(0) is None          # $5A43 -> hull_breach
    # The digit always lands in a blank of the stored message, never over text.
    for ty in (7, 8):
        assert len(MALFUNCTION_MESSAGES[ty]) == 30


def test_the_transient_row24_banners_are_the_roms_own_bytes() -> None:
    """**[C $5B80 / $5C33 / $5950] DISC-231** — decoded, and now displayed.

    Each is written to `$07C0` (row 24 col 0), held by a blocking `delay_long`
    ($561C) and then blanked by `clear_line_07c0 ($5BE7)`. All three existed
    only as a bare `return False` in the remake.
    """
    from alientools.gamedata import _screen_char
    from alien_remake.core import constants

    rom = _prg()

    def txt(addr: int, n: int) -> str:
        return "".join(
            _screen_char(b) for b in rom[addr - _LOAD_ADDR : addr - _LOAD_ADDR + n]
        )

    assert txt(0x5B80, 21) == constants.NOTICE_MOTHER_REFUSES
    assert txt(0x5C33, 12) == constants.NOTICE_GO_GET_JONES
    assert txt(0x5950, 10).rstrip() == constants.NOTICE_FIRE_OUT
    assert (0x07C0 - 0x0400) // 40 == 24 and (0x07C0 - 0x0400) % 40 == 0

    # `delay` blacks the border for its whole run ($5626 LDA #$00 / $5628 STA
    # $D020) and callers restore #$06 after — hence "the border turns black".
    assert rom[0x5626 - _LOAD_ADDR] == 0xA9      # LDA #
    assert rom[0x5627 - _LOAD_ADDR] == 0x00      # ...#$00
    assert rom[0x5628 - _LOAD_ADDR] == 0x8D      # STA abs
    assert constants.NOTICE_BORDER == 0


def test_a_refused_launch_posts_mothers_banner_and_blacks_the_border() -> None:
    """DISC-231 end to end: the refusal the owner reported now says so."""
    import random

    from alien_remake.core import constants
    from alien_remake.core.sim import Simulation
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType
    from alien_remake.render import c64
    from alien_remake.render.play import PlayMixin

    sim = Simulation(rng=random.Random(0))
    # Nobody is aboard the shuttle, so `$5B9E`'s scan refuses.
    assert not sim.apply_special_option(
        SpecialOption(SpecialOptionType.LAUNCH_NARCISSUS)
    )
    assert sim.state.notice == constants.NOTICE_MOTHER_REFUSES
    assert sim.state.notice_ticks == constants.NOTICE_TICKS
    assert PlayMixin._play_border(sim.state) == c64.rgb(constants.NOTICE_BORDER)

    # ...and it expires by itself, blanking the row (`clear_line_07c0`).
    for _ in range(constants.NOTICE_TICKS):
        sim.advance()
    assert sim.state.notice is None


def test_the_android_reveal_recolours_every_glyph() -> None:
    """**[C $52DA `STA $D021`] DISC-231** — the reveal's only visual tell.

    The reveal writes the android's own slot number into the VIC background
    register. ALIEN's font is cut-out, so `$D021` is the ink every glyph shows
    through (D-050) — the whole screen's lettering changes colour at once.
    The remake set `locked_crew_id` correctly and showed nothing.
    """
    import random

    from alien_remake.core import constants
    from alien_remake.core.sim import Simulation
    from alien_remake.render import c64
    from alien_remake.render.play import PlayMixin

    rom = _prg()
    # $52D4 LDA $7214 / $52D7 STA $64CC / $52DA STA $D021 — one value, two stores.
    assert rom[0x52D4 - _LOAD_ADDR : 0x52D7 - _LOAD_ADDR] == bytes((0xAD, 0x14, 0x72))
    assert rom[0x52DA - _LOAD_ADDR : 0x52DD - _LOAD_ADDR] == bytes((0x8D, 0x21, 0xD0))

    sim = Simulation(rng=random.Random(0))
    assert sim.state.background_colour == 0            # $7027 — black in play
    assert PlayMixin._ink(sim.state) == c64.rgb(c64.BLACK)

    android = sim.state.crew[sim.state.android_id or ""]
    slot = sim._slot_of(android)
    assert 1 <= slot <= 7
    sim.state.background_colour = slot                  # what $52DA writes
    assert PlayMixin._ink(sim.state) == c64.rgb(slot)
    assert PlayMixin._ink(sim.state) != c64.rgb(c64.BLACK)


def test_the_hull_breach_spiral_is_the_roms_own_cell_order() -> None:
    """**[C animate_fill_row $5C42] DISC-234** — transliterated, not redrawn.

    `breach_spiral_cells` mirrors the routine's pointer arithmetic instruction
    for instruction, so the order is the machine's. Checked here against the
    properties that arithmetic must produce, plus the ROM bytes that seed it.
    """
    from alien_remake.render.frontend import (
        BREACH_SPIRAL, _BREACH_LEG0, _BREACH_LEG_END, _BREACH_PALETTE,
        _BREACH_RUN0, _BREACH_START,
    )

    rom = _prg()
    # $5C42 LDA #$01 / STA $64E0 ; $5C47 LDA #$10 / STA $64E1
    assert rom[0x5C43 - _LOAD_ADDR] == _BREACH_RUN0 == 1
    assert rom[0x5C48 - _LOAD_ADDR] == _BREACH_LEG0 == 0x10
    # $5C63 CMP #$28 — the terminating leg length.
    assert rom[0x5C67 - _LOAD_ADDR] == _BREACH_LEG_END == 0x28
    # $5C4E LDA #$EB — the low byte; $5D25 LDA #$05 supplies the high byte.
    assert rom[0x5C4F - _LOAD_ADDR] == 0xEB
    assert rom[0x5D26 - _LOAD_ADDR] == 0x05
    # NB `_BREACH_START` is the POINTER ($05EB = offset 491, row 12 col 11);
    # the first cell actually written is `ptr + leg` = 507 (row 12 col 27),
    # because `$5C55` opens with `LDY $64E1` and counts down.
    assert _BREACH_START == 0x05EB - 0x0400 == 491

    # $5D11 — the six-colour fire palette, read straight out of the image.
    assert tuple(rom[0x5D11 - _LOAD_ADDR : 0x5D17 - _LOAD_ADDR]) == _BREACH_PALETTE
    assert _BREACH_PALETTE == (0x02, 0x08, 0x07, 0x01, 0x07, 0x08)

    # The spiral covers the whole 40x25 field — enumerated, not assumed.
    assert set(BREACH_SPIRAL) == set(range(1000))
    assert len(BREACH_SPIRAL) == 1012        # twelve cells painted twice
    assert BREACH_SPIRAL[0] == _BREACH_START + _BREACH_LEG0 == 507

    # It is NOT the loader's spiral (DISC-207) — different start and length.
    from alien_remake.render.frontend import SPIRAL_CELLS

    assert len(SPIRAL_CELLS) != len(BREACH_SPIRAL)


def test_only_a_destroyed_ship_runs_the_breach_animation() -> None:
    """**DISC-234** — `ship_destroyed` is set at the two `JMP hull_breach`
    sites (`$565C` a room hitting exactly 20, `$5A43` the countdown expiring),
    and is distinct from `ship_destructing`, which only means *armed*.
    """
    import random

    from alien_remake.core import constants
    from alien_remake.core.sim import Simulation
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType
    from alien_remake.core.state import GamePhase

    # Merely arming SCUTTLE must NOT mark the ship destroyed.
    sim = Simulation(rng=random.Random(0))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    sim.apply_special_option(
        SpecialOption(SpecialOptionType.INITIATE_AUTO_DESTRUCT, crew_id=crew.id)
    )
    assert sim.state.ship_destructing is True
    assert sim.state.ship_destroyed is False

    # A room reaching exactly 20 does ($565C).
    sim2 = Simulation(rng=random.Random(1))
    room = next(iter(sim2.ship.rooms))
    sim2.state.room_damage[room] = constants.HULL_BREACH_THRESHOLD
    sim2.advance()
    assert sim2.state.phase is GamePhase.LOST
    assert sim2.state.ship_destroyed is True


def test_indicate_is_a_two_page_room_name_list_not_a_scroller() -> None:
    """**[C $73C8/$74FA/$766F] DISC-236** — decoded end to end.

    `draw_deck_map ($73C8)` copies **19 consecutive 10-byte room-name records**
    straight into panel rows 0-18 (`$FB/$FC = $041E` = row 0 col 30, `+$28` a
    row; `$FD/$FE` the source, `+$0A` a record; `CPX #$13` = 19).

    There are exactly **two pages**, not a scroll window:

        74FA/7654  src $A712, cursor row 18, $64FB = $10   ; page 1
        766F       src $A7D0, cursor row 0,  $64FB = $08   ; page 2
        7676       CMP #$08 / BEQ -> already on page 2, exit

    and the cursor row converts to a room id two different ways::

        76A4  $64FB == $10 -> $64F7 = $64E5 - 1     ; page 1
        76B4  else            $64F7 = $64E5 + $10   ; page 2 (+16)

    Page 1 rows 1-17 are rooms 0-16; row 18 is the "next page" control. Page 2
    rows 1-18 are rooms 17-34. That is all 35 locations, and it lands exactly
    on the two-record discontinuity the name table already documents
    (`$A71C + 17*10` would be `$A7C6`; the ROM uses `$A7DA`).
    """
    from alien_remake.core import gamedata_snapshot as data

    rom = _prg()

    # draw_deck_map's geometry.
    assert rom[0x73C9 - _LOAD_ADDR] == 0xA7 and rom[0x73CD - _LOAD_ADDR] == 0x12
    assert rom[0x73D1 - _LOAD_ADDR] == 0x04 and rom[0x73D5 - _LOAD_ADDR] == 0x1E
    assert (0x041E - 0x0400) % 40 == 30      # panel column
    assert rom[0x73FD - _LOAD_ADDR] == 0x13  # CPX #$13 -> 19 rows

    # The two page sources and their sentinels.
    assert rom[0x7662 - _LOAD_ADDR] == 0xEE  # page 1 cursor -> $DAEE (row 18)
    assert rom[0x766A - _LOAD_ADDR] == 0x10  # page 1 sentinel
    assert rom[0x768D - _LOAD_ADDR] == 0xD0  # page 2 source low  -> $A7D0
    assert rom[0x7691 - _LOAD_ADDR] == 0xA7  # page 2 source high
    assert rom[0x7698 - _LOAD_ADDR] == 0x08  # page 2 sentinel

    def name_addr(r: int) -> int:
        return 0xA71C + r * 10 if r < 17 else 0xA7DA + (r - 17) * 10

    for row in range(1, 18):                      # page 1 -> rooms 0-16
        assert 0xA712 + row * 10 == name_addr(row - 1)
    for row in range(1, 19):                      # page 2 -> rooms 17-34
        assert 0xA7D0 + row * 10 == name_addr(row + 16)

    # $7440 — the INDICATE screen's own colour table, a third layout.
    assert tuple(rom[0x7440 - _LOAD_ADDR : 0x7453 - _LOAD_ADDR]) == \
        data.INDICATE_PANEL_COLOURS
    assert data.INDICATE_PANEL_COLOURS == (15,) + (14,) * 17 + (15,)
    assert data.INDICATE_PANEL_COLOURS != data.CONTROL_PANEL_COLOURS


def test_the_opening_notice_holds_for_two_delay_longs() -> None:
    """**[C $50B8/$50BB] DISC-238** — corrected from 27 ticks to 49.

    `sub_5049` ends with **two** `JSR delay_long` back to back. D-172 computed
    `delay_long` at 3.128 s (a countable loop: 47 cycles x 256 x 256) and used
    that to fix the title card and the letter gap, but never re-checked the
    opening, which kept an older guess of 27 ticks — barely over *one*
    delay_long, so the notice cleared about twice as fast as the original's.
    """
    from alien_remake.core.constants import OPENING_TICKS, TICK_HZ

    rom = _prg()
    # Two consecutive JSR $561C at $50B8 and $50BB, then RTS.
    assert rom[0x50B8 - _LOAD_ADDR : 0x50BB - _LOAD_ADDR] == bytes((0x20, 0x1C, 0x56))
    assert rom[0x50BB - _LOAD_ADDR : 0x50BE - _LOAD_ADDR] == bytes((0x20, 0x1C, 0x56))
    assert rom[0x50BE - _LOAD_ADDR] == 0x60      # RTS — no third delay

    delay_long_s = 3.128                          # D-172, computed from $561E
    assert OPENING_TICKS == round(2 * delay_long_s * TICK_HZ)
    assert OPENING_TICKS == 49


def test_the_heartbeat_loop_is_not_restarted_when_the_rate_is_unchanged() -> None:
    """**DISC-254** — the beat lost tempo because it kept restarting.

    `fear_alert ($4E16)` buckets composure hard (`min(composure, 4)`), so fear
    4..10 all beat at divider 40 and 0..1 both at 15 — four distinct clips for
    eleven fear values. `_heartbeat_sound` already keys its cache on the
    divider, but the change-detection compared **raw fear**, so every 6 -> 7
    tick counted as a rate change: the loop was stopped and the *identical*
    clip restarted from sample zero, mid-beat. Seven of the eleven values share
    one divider, so it fired constantly.
    """
    import random
    from pathlib import Path

    from alien_remake.core import constants as K
    from alien_remake.core.menu import MenuController
    from alien_remake.core.sim import Simulation
    from alien_remake.render.pygame_app import PygameRenderer
    from alien_remake.render.tiles import load

    charset = Path("out") / "charset.bin"
    r = PygameRenderer(
        scale=2, tiles=load(charset) if charset.exists() else None, intro_wav=None
    )
    try:
        sim = Simulation(rng=random.Random(0))
        r._sim, r._ship = sim, sim.ship
        r._menu = MenuController(sim)
        crew = next(c for c in sim.state.crew.values() if c.alive)
        r._menu.selected_crew = crew.id
        r._attacking = False

        starts: list[int] = []
        original = type(r)._heartbeat_sound

        def counting(self, composure):          # type: ignore[no-untyped-def]
            starts.append(K.heartbeat_divider(composure))
            return original(self, composure)

        type(r)._heartbeat_sound = counting     # type: ignore[assignment]
        try:
            # Walk fear across the whole band that shares divider 40.
            for fear in (4, 5, 6, 7, 8, 9, 10, 9, 8, 7):
                crew.fear = fear
                r._update_heartbeat(sim.state)
            assert len(starts) == 1, (
                f"the loop restarted {len(starts)} times across fear 4..10, "
                "which all share divider 40 — that is the tempo skip"
            )

            # A real rate change must still restart it.
            crew.fear = 2                        # divider 23
            r._update_heartbeat(sim.state)
            assert len(starts) == 2, "a genuine rate change must restart the bed"
            assert starts == [40, 23]
        finally:
            type(r)._heartbeat_sound = original  # type: ignore[assignment]
    finally:
        r.close()
