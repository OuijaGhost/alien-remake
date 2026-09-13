"""**DISC-224.** The CLI's `--death` default disagreed with the ROM.

`DeathVariant`'s own docstring already settles this (D-170/PV-20): `$64C2`,
the opening-victim slot, has exactly two writers in the whole image, and
neither is a "fixed" path — RANDOM is the ROM's only real behaviour, and
`DeathVariant.FIXED` exists purely as a remake testing aid ("explicitly not
a fidelity claim"). `GameFlow`'s own default is already `DeathVariant.ORIGINAL`.

But `__main__.py`'s argument parser defaulted `--death` to `"fixed"` anyway,
and its help text called that "the canonical casualty" - so a player running
the game with no flags (the ordinary case) got Lambert dead at the opening
every single time, which is exactly the "why does Lambert die every time I
play?" report this fixes.
"""

from __future__ import annotations

from unittest.mock import patch

from alien_remake.core.modes import DeathVariant, GameMode


def test_the_death_flag_defaults_to_random_not_fixed() -> None:
    """No `--death` flag -> the ROM's real behaviour, not the testing aid."""
    from alien_remake import __main__ as cli

    seen: list[DeathVariant] = []

    def fake_default_simulation(mode: GameMode, variant: DeathVariant, *rest):
        # `*rest` absorbs `alien_start` (DISC-260) and anything added later —
        # this test is about the *death* default, not the signature.
        seen.append(variant)
        raise SystemExit(0)  # short-circuit before any rendering/ticking

    with patch.object(cli, "default_simulation", fake_default_simulation):
        try:
            cli.main(["--headless", "1"])
        except SystemExit:
            pass

    assert seen == [DeathVariant.ORIGINAL], (
        "running with no --death flag must use the ROM's only real variant"
    )
