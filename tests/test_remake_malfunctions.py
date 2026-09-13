"""Systems malfunctions (D-072/D-073, `$5587` -> `$55C1`).

The trigger was the missing piece: `damage_room_b ($5587)` latches a room's
`$651C` alarm at `$55A6` and then falls **straight through** to the message
dispatcher at `$55C1`, so the banner and the alarm are one event.
"""

from __future__ import annotations

from alien_remake.core import constants
from alien_remake.core.alien import add_room_damage
from alien_remake.core.gamedata_snapshot import ROOM_SLUGS
from alien_remake.core.state import GameState

import needs                                       # noqa: E402


def _room(idx: int) -> str:
    return ROOM_SLUGS[idx]


def test_message_table_matches_the_rom_blob() -> None:
    """[C $54C6 + lengths $5473 / offsets $547C] — decoded byte-exactly."""
    m = constants.MALFUNCTION_MESSAGES
    assert m[1] == "PARTIAL SYSTEMS CONTROL LOSS"   # len 28
    assert m[2] == "COMPUTER MALFUNCTION"           # len 20
    assert m[3] == "CRYOGENICS MALFUNCTION"         # len 22
    assert m[4] == "FIRE IN "                       # len 8, + room name
    assert m[5] == "ENVIRONMENTAL IRREGULARITIES"   # len 28
    assert m[6] == "NARCISSUS STATUS RED"           # len 20
    assert len(m[7]) == 30 and len(m[8]) == 30      # the two auto-destruct lines


def test_per_room_table_is_the_static_rom_assignment() -> None:
    """[C $54A3] Never written anywhere in the program. The semantics line up
    3-for-3, which is what cross-validates the ROOM_SLUGS ordering.

    **Rewritten 2026-08-07 (D-164) to read the PRG rather than a literal.** The
    hardcoded dict was missing room **34 (NARCISSUS)**, which really does carry
    type 6 — and because both the constant and the assertion said the same
    wrong thing, the test agreed with the bug. Decoding the table here means
    the source of truth is the binary, not a transcription of it.
    """
    needs.need(needs.ALIEN_PRG)
    import pathlib

    prg = pathlib.Path("out/Alien (USA, Europe)_files/ALIEN.prg").read_bytes()
    load = prg[0] | prg[1] << 8
    mem = prg[2:]
    table = list(mem[0x54A3 - load : 0x54A3 - load + len(ROOM_SLUGS)])
    decoded = {i: v for i, v in enumerate(table) if v}

    assert constants.ROOM_MALFUNCTION_TYPE == decoded
    assert decoded[34] == 6, "the NARCISSUS carries NARCISSUS STATUS RED"
    assert ROOM_SLUGS[6] == "commdcentr"    # -> systems control loss
    assert ROOM_SLUGS[7] == "computer"      # -> COMPUTER MALFUNCTION
    assert ROOM_SLUGS[15] == "cryo_vault"   # -> CRYOGENICS MALFUNCTION


def test_no_banner_below_the_alarm_threshold() -> None:
    """$558C CMP #$04 / BCS — under 4 the routine RTSes at $5593."""
    state = GameState()
    add_room_damage(state, _room(7), constants.ROOM_ALARM_DAMAGE_THRESHOLD - 1)
    assert state.malfunction is None
    assert not state.room_alarm


def test_banner_raises_with_the_alarm() -> None:
    state = GameState()
    add_room_damage(state, _room(7), constants.ROOM_ALARM_DAMAGE_THRESHOLD)
    assert state.room_alarm[_room(7)] == 1
    assert state.malfunction == "COMPUTER MALFUNCTION"


def test_rooms_without_an_entry_raise_no_banner() -> None:
    """$55C4 BEQ — a room whose `$54A3` byte is 0 shows nothing, even though
    its alarm still latches."""
    state = GameState()
    quiet = _room(0)
    assert 0 not in constants.ROOM_MALFUNCTION_TYPE
    add_room_damage(state, quiet, 10)
    assert state.room_alarm[quiet] == 1
    assert state.malfunction is None


def test_fire_rooms_append_the_room_name_and_set_the_fire_flag() -> None:
    """$55F2 appends the room name for type 4 only; $55B1 writes 6 into
    `$5753,X` for exactly the 17-19 band."""
    for idx in (17, 18, 19):
        state = GameState()
        room = _room(idx)
        add_room_damage(state, room, 5)
        assert state.malfunction is not None
        assert state.malfunction.startswith("FIRE IN ")
        assert state.malfunction != "FIRE IN "          # a name was appended
        assert state.room_fire[room] == constants.ROOM_FIRE_FLAG


def test_non_fire_malfunctions_do_not_set_the_fire_flag() -> None:
    state = GameState()
    add_room_damage(state, _room(15), 6)
    assert state.malfunction == "CRYOGENICS MALFUNCTION"
    assert not state.room_fire


def test_fight_fire_clears_the_fire_flag_too() -> None:
    """$58CF STA $5753,X — the extinguisher clears the fire flag alongside the
    alarm latch (D-066)."""
    import random

    from alien_remake.core.sim import Simulation
    from alien_remake.core.special_options import SpecialOption, SpecialOptionType

    sim = Simulation(rng=random.Random(9))
    crew = next(c for c in sim.state.crew.values() if c.alive)
    room = _room(19)
    crew.room_id = room
    ext = next(i for i in sim.state.items.values() if i.type_id == "fire_extng")
    ext.room_id, ext.holder = room, None
    add_room_damage(sim.state, room, 5)
    assert sim.state.room_fire[room] == constants.ROOM_FIRE_FLAG
    assert sim.apply_special_option(
        SpecialOption(SpecialOptionType.FIGHT_FIRE, crew_id=crew.id)
    )
    assert room not in sim.state.room_fire
    assert not sim.state.room_alarm.get(room)


def test_alarm_latch_means_the_banner_fires_once_per_silencing() -> None:
    """$559E LDA $651C,X / BNE — a one-way latch, so more damage on an already
    alarming room does not re-raise it."""
    state = GameState()
    add_room_damage(state, _room(7), 5)
    state.malfunction = None
    add_room_damage(state, _room(7), 5)     # still alarming
    assert state.malfunction is None
