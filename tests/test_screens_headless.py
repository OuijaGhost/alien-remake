"""`screens/` must stay readable without pygame, and keep saying what the ROM says.

DISC-240 moved the decoded screen tables out of `render/play.py` and
`render/frontend.py`, which hard-import pygame at module level. The whole point
of the move is that this data is ROM truth rather than a drawing decision, so
the load-bearing test is the *import* one: if `screens` ever grows a pygame
dependency, the extraction has quietly undone itself.

That check runs in a subprocess. Blocking pygame in-process is not trustworthy
here — 21 of this suite's test files import it, so by the time these tests run
it is already in `sys.modules` and a `meta_path` blocker would be a no-op.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

from alien_remake.core.menu import MenuCategory
from alien_remake.screens import ending, panels

#: `pytest`'s own `pythonpath = ["src"]` (pyproject.toml) is what lets this
#: whole suite import `alien_remake` with no install at all - but that only
#: applies inside the pytest process. A subprocess started fresh does not
#: inherit it and needs its own `PYTHONPATH`, or this test fails on any
#: checkout that has not also run `pip install -e .` (DISC-004's editable
#: install is the *recommended* way to run the game, not a precondition for
#: the test suite to pass).
_SRC = str(Path(__file__).resolve().parent.parent / "src")

# The three panels are all 19 rows (DISC-232/235/236) — the crew order panel,
# CONTROL `$7000`, and INDICATE `$7440`. Painting fewer left the black strip at
# the bottom of the crew menu that prompted DISC-232.
PANEL_ROWS = 19


def _run_without_pygame(body: str) -> subprocess.CompletedProcess[str]:
    """Execute ``body`` in a fresh interpreter where importing pygame fails."""
    script = textwrap.dedent("""
        import sys, importlib.abc
        class Blocker(importlib.abc.MetaPathFinder):
            def find_spec(self, name, path=None, target=None):
                if name == "pygame" or name.startswith("pygame."):
                    raise ImportError("pygame blocked")
                return None
        sys.meta_path.insert(0, Blocker())
        try:
            import pygame
        except ImportError:
            pass
        else:
            raise AssertionError("blocker failed: pygame still importable")
    """) + textwrap.dedent(body)
    env = dict(os.environ)
    env["PYTHONPATH"] = _SRC + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, env=env,
    )


def test_screens_imports_with_pygame_unavailable() -> None:
    """The extraction's whole purpose: ROM data readable without a display."""
    done = _run_without_pygame("""
        from alien_remake.screens import panels, ending
        assert panels.PANEL_SECTIONS and ending.ENDING_ROWS
        print("ok")
    """)
    assert done.returncode == 0, f"screens needs pygame now:\n{done.stderr}"
    assert "ok" in done.stdout


def test_render_play_still_needs_pygame() -> None:
    """The control: `render/` is where the pygame dependency is *supposed* to be.

    Without this, `test_screens_imports_with_pygame_unavailable` would keep
    passing even if the blocker silently stopped working.
    """
    done = _run_without_pygame("""
        try:
            import alien_remake.render.play
        except ImportError:
            print("still-needs-pygame")
    """)
    assert "still-needs-pygame" in done.stdout


def test_all_three_panels_cover_exactly_19_rows_with_no_gaps() -> None:
    """Every row 0-18 painted by every screen — the DISC-232 black-strip bug."""
    for name, sections in (
        ("crew", panels.PANEL_SECTIONS),
        ("control", panels.CONTROL_SECTIONS),
        ("indicate", panels.INDICATE_SECTIONS),
    ):
        painted = [r for first, last, _ in sections for r in range(first, last + 1)]
        assert sorted(painted) == list(range(PANEL_ROWS)), f"{name} panel has a gap"


def test_panel_colours_are_indices_not_rgb() -> None:
    """`screens/` holds what colour RAM holds; RGB conversion is the renderer's job.

    A regression here means someone moved `c64.rgb()` back down the stack, which
    is what re-couples this layer to a rendering choice.
    """
    for sections in (
        panels.PANEL_SECTIONS, panels.CONTROL_SECTIONS, panels.INDICATE_SECTIONS,
    ):
        for _, _, colour in sections:
            assert isinstance(colour, int) and 0 <= colour <= 15
    for _, _, colour in panels.BOTTOM_BANDS:
        assert isinstance(colour, int) and 0 <= colour <= 15
    for colour in panels.BAND_COLOUR.values():
        assert isinstance(colour, int) and 0 <= colour <= 15


def test_bottom_bands_are_two_rows_tall_from_paint_map_colors() -> None:
    """[C paint_map_colors $7993] — blocks, not the thin stripes the remake drew."""
    assert panels.BOTTOM_BANDS == (
        (18, 18, 15),   # $DAD0        light grey
        (19, 20, 13),   # $DAF8/$DB20  light green
        (21, 22, 8),    # $DB48/$DB70  orange
        (23, 24, 7),    # $DB98/$DBC0  yellow
    )


def test_band_colour_covers_every_menu_category() -> None:
    """A missing category falls through to a black row on a real screen."""
    assert set(panels.BAND_COLOUR) == set(MenuCategory)


def test_ending_rows_match_the_rom_screen_addresses() -> None:
    """Row = ($addr - $0400) / 40, straight from `select_outcome $60A9`."""
    for key, addr in (
        ("nostromo", 0x0478), ("alien", 0x04F0), ("ship", 0x0540),
        ("eggs", 0x0590), ("crew", 0x0608),
    ):
        assert ending.ENDING_ROWS[key] == (addr - 0x0400) // 40


def test_ending_strings_kept_the_roms_sentence_case() -> None:
    """DISC-215's case-bit fix: these were transcribed in ALL CAPS before it.

    The high bit is *case*, not reverse video, so shouting here is a decode bug.
    """
    assert ending.ENDING_ALIEN_DEAD == "The Alien is dead"
    assert ending.ENDING_NOSTROMO_DESTROYED == "The Nostromo is destroyed"
    assert ending.ENDING_PRESS_ANY_KEY == "press any key"
    assert ending.ENDING_PRESS_ANY_KEY.islower()


def test_render_layer_still_exposes_the_moved_names() -> None:
    """The aliases are load-bearing: `play.py`'s call sites and other tests use them.

    Dropping one would be caught far away from this change, so pin it here.
    """
    from alien_remake.render import frontend, play

    assert play._PANEL_SECTIONS is panels.PANEL_SECTIONS
    assert play._PANEL_COL == panels.PANEL_COL
    assert play._STATUS_ROW == panels.STATUS_ROW
    assert frontend._ENDING_ROWS is ending.ENDING_ROWS
    # ...but the two colour tables are converted to RGB at this boundary. Assert
    # the conversion, not a palette literal — the palette is c64.py's business.
    from alien_remake.render import c64

    assert play._BOTTOM_BANDS == tuple(
        (first, last, c64.rgb(index)) for first, last, index in panels.BOTTOM_BANDS
    )
    assert play._BAND_COLOUR == {
        cat: c64.rgb(index) for cat, index in panels.BAND_COLOUR.items()
    }


def test_screens_never_imports_render() -> None:
    """The layering, enforced (DISC-249): `render` imports `screens`, never back.

    `screens/` stores colour *indices* rather than RGB specifically so it does
    not depend on a palette — and then imported `render.c64` to get the index
    names, running the dependency backwards. It was only safe because
    `render/__init__.py` is deliberately pygame-free, and safe is not the same
    as right: the next person to put something pygame-shaped in that `__init__`
    would have broken the headless guarantee from a distance.
    """
    import ast
    from pathlib import Path

    package = Path(panels.__file__).parent
    assert package.name == "screens"

    offenders: list[str] = []
    for source in sorted(package.glob("*.py")):
        for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                # `from ..render import c64` -> module="render", level=2
                targets = [node.module or ""]
            else:
                continue
            for target in targets:
                if "render" in target.split("."):
                    offenders.append(f"{source.name}: {target}")

    assert not offenders, (
        f"screens/ must not import render/: {offenders}"
    )


def test_colour_names_live_below_the_render_boundary() -> None:
    """The sixteen numbers are ROM truth; the palette is a rendering choice."""
    from alien_remake.render import c64
    from alien_remake.screens import colours

    for name in ("BLACK", "WHITE", "GREEN", "LIGHT_RED", "LIGHT_GREY"):
        assert getattr(colours, name) == getattr(c64, name), (
            f"{name} drifted between screens.colours and its re-export"
        )
    # The palette itself must NOT have followed them down.
    assert not hasattr(colours, "PALETTE")
    assert not hasattr(colours, "rgb")
    assert hasattr(c64, "PALETTE") and hasattr(c64, "rgb")
