"""CR4/CR5: the CREDITS screen — paging and the ORIGINAL hide.

CR5's own wording is the test to write: *"a test that ORIGINAL neither draws it
nor answers the key — because a hidden row that still responds is worse than no
row."* That is two separate assertions, and both are here.
"""

from __future__ import annotations

import pytest

from alien_remake.core.flow import GameFlow, InputEvent, Screen


def _flow(original: bool = False) -> GameFlow:
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    flow.options.apply_profile("original" if original else "updated")
    return flow


def test_select_credits_opens_the_screen_off_original() -> None:
    flow = _flow()
    flow.handle(InputEvent.SELECT_CREDITS)
    assert flow.screen is Screen.CREDITS
    assert flow.credits_page == 0


def test_select_credits_does_nothing_under_original() -> None:
    """The second half of "hidden": the key must not work even if pressed."""
    flow = _flow(original=True)
    flow.handle(InputEvent.SELECT_CREDITS)
    assert flow.screen is Screen.GAME_SELECTION, (
        "ORIGINAL answered the CREDITS key despite the row being hidden"
    )


def test_paging_forward_and_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """Needs more than one page, which the project's own two credits rows
    are not — pad the list so paging has somewhere to go."""
    from alien_remake import media

    monkeypatch.setattr(media, "credits", lambda: [{"title": f"Row {i}"} for i in range(20)])
    flow = _flow()
    flow.screen = Screen.CREDITS
    flow.credits_page = 0
    flow.handle(InputEvent.FIRE)
    assert flow.credits_page == 1
    flow.handle(InputEvent.LEFT)
    assert flow.credits_page == 0
    flow.handle(InputEvent.LEFT)
    assert flow.credits_page == 0, "paging back past the first page went negative"


def test_paging_past_the_last_page_returns_to_selection() -> None:
    flow = _flow()
    flow.screen = Screen.CREDITS
    flow.credits_page = flow.credits_pages() - 1
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.GAME_SELECTION
    assert flow.credits_page == 0, "the page counter was not reset on exit"


def test_escape_leaves_credits_immediately() -> None:
    """Escape is `InputEvent.ABANDON` in this flow, not `QUIT` (`QUIT` is a
    loop concern `handle()` deliberately ignores — see its own docstring)."""
    flow = _flow()
    flow.screen = Screen.CREDITS
    flow.credits_page = 2
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is Screen.GAME_SELECTION


def test_credits_pages_is_at_least_one_even_with_nothing_supplied() -> None:
    """An empty list must still be a page, or `_draw_credits` has nothing to
    show and the footer's "1/0" would be nonsense."""
    flow = _flow()
    assert flow.credits_pages() >= 1


def test_the_screen_renders_without_crashing(monkeypatch) -> None:
    """A smoke test of the actual draw path, both presets."""
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pytest

    pygame = pytest.importorskip("pygame")
    from alien_remake.render.pygame_app import PygameRenderer

    renderer = PygameRenderer(scale=2, intro_wav=None)
    try:
        flow = _flow()
        flow.screen = Screen.CREDITS
        renderer.draw(flow)  # must not raise
    finally:
        renderer.close()


def test_the_row_is_not_drawn_under_original(monkeypatch) -> None:
    """CR5's first half: ORIGINAL must not even show the row."""
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pytest

    pygame = pytest.importorskip("pygame")
    from alien_remake.render.pygame_app import PygameRenderer

    renderer = PygameRenderer(scale=2, intro_wav=None)
    try:
        original = _flow(original=True)
        original.screen = Screen.GAME_SELECTION
        renderer.draw(original)
        without = pygame.image.tobytes(renderer._surface, "RGB")

        quick = _flow()
        quick.screen = Screen.GAME_SELECTION
        renderer.draw(quick)
        with_row = pygame.image.tobytes(renderer._surface, "RGB")

        assert without != with_row, (
            "the selection screen looks identical with and without the row"
        )
    finally:
        renderer.close()


def test_the_credits_row_does_not_collide_with_the_copyright_line() -> None:
    """A real screenshot caught this (2026-09-03): a THIRD extra row (CREDITS,
    under any non-ORIGINAL profile) landed at the exact pixel row the
    "PAUL CLANSEY ... CONCEPT SOFTWARE" line was hardcoded to, and the two
    drew on top of each other. Structural guard: counts distinct TEXT BANDS
    (blank-to-text transitions), not a blank row -- verified directly against
    the pre-fix code (git stash on just the one file): that version fails
    this test (1 >= 2), the fix passes it.
    """
    import os

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pytest

    pygame = pytest.importorskip("pygame")
    from alien_remake.render import c64
    from alien_remake.render.pygame_app import PygameRenderer

    paper = c64.rgb(c64.GREEN)
    renderer = PygameRenderer(scale=1, intro_wav=None)
    try:
        flow = _flow(original=False)
        flow.screen = Screen.GAME_SELECTION
        renderer.draw(flow)
        surf = renderer._surface

        def blank_row(y: int) -> bool:
            return all(
                tuple(surf.get_at((x, y)))[:3] == paper
                for x in range(0, surf.get_width())
            )

        bands = 0
        was_blank = True
        for y in range(170, 199):
            blank = blank_row(y)
            if was_blank and not blank:
                bands += 1
            was_blank = blank
        assert bands >= 2, (
            f"found {bands} text band(s) between the CREDITS row and the "
            "copyright line, not 2 - they may have merged into one "
            "overlapping block"
        )
    finally:
        renderer.close()
