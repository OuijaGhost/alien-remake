"""`--jones easy` — an added rule, and the ROM table it does not touch (DISC-269).

The owner remembers catching Jones easily and asked for Ripley to be better at
it. She already is: `$883C` gives her 13 where Parker gets 15, which is the best
tier in the game. What is hard is the **cat box** — the ROM reserves its
four-point improvement for the net (`$87A1`), and the box alone is a 1-in-16 to
3-in-16 shot.

So the added rule is defined as "the box behaves like the net" rather than as an
arbitrary bonus: the size of the change is one the ROM itself makes, and the
per-character table underneath is untouched.
"""

from __future__ import annotations

import random

from alien_remake.core import constants
from alien_remake.core.modes import JonesCatch
from alien_remake.core.sim import Simulation


def _rate(mode: JonesCatch, who: str, item: str, trials: int = 3000) -> float:
    hits = 0
    for seed in range(trials):
        sim = Simulation(rng=random.Random(seed), jones_catch=mode)
        crew = sim.state.crew[who]
        sim.state.jones_room_id = crew.room_id
        thing = next(i for i in sim.state.items.values() if i.type_id == item)
        thing.room_id, thing.holder = None, crew.id
        crew.carried = [thing.id]
        hits += sim._catch_jones(who)
    return hits / trials


def test_ripley_is_already_the_best_at_this_in_the_rom() -> None:
    """Decoded, not an added rule: `$883C` gives her the best tier."""
    from alien_remake.core.gamedata_snapshot import CREW_NAMES

    slots = {name.lower(): i for i, name in enumerate(CREW_NAMES, start=1)}
    table = constants.JONES_CATCH_THRESHOLD
    assert table[slots["ripley"]] == min(table[1:]), "Ripley is not the best tier"
    assert table[slots["parker"]] == max(table[1:]), "Parker is not the worst"
    assert _rate(JonesCatch.PATIENT, "ripley", "cat_box") > _rate(
        JonesCatch.PATIENT, "parker", "cat_box"
    )


def test_easy_gives_the_box_the_net_s_odds_and_nothing_more() -> None:
    box = _rate(JonesCatch.EASY, "ripley", "cat_box")
    net = _rate(JonesCatch.PATIENT, "ripley", "net")
    assert abs(box - net) < 0.02, f"easy box {box:.3f} vs rom net {net:.3f}"


def test_easy_does_not_flatten_the_per_character_table() -> None:
    """The ROM's characterisation has to survive the added rule."""
    assert _rate(JonesCatch.EASY, "ripley", "cat_box") > _rate(
        JonesCatch.EASY, "parker", "cat_box"
    )


def test_the_default_is_still_the_rom_s_odds() -> None:
    """`patient` changes how many attempts you get, never their odds."""
    patient = _rate(JonesCatch.PATIENT, "ripley", "cat_box")
    classic = _rate(JonesCatch.CLASSIC, "ripley", "cat_box")
    assert abs(patient - classic) < 0.02
    assert 0.15 < patient < 0.23, f"the box drifted off its 3-in-16: {patient:.3f}"
