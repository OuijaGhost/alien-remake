"""Per-frame work that should happen once (DISC-255).

Three things were being recomputed every frame or held six times larger than
necessary. Each fix is guarded by the property that makes it safe rather than
by its speed, because a cache that returns the wrong pixels is worse than a
slow one.
"""

from __future__ import annotations

import random
from pathlib import Path

import pygame
import pytest

from alien_remake.core.flow import GameFlow, Screen
from alien_remake.core.sim import Simulation
from alien_remake.render.pygame_app import PygameRenderer
from alien_remake.render.tiles import load

import needs                                       # noqa: E402


@pytest.fixture
def renderer() -> PygameRenderer:
    charset = Path("out") / "charset.bin"
    r = PygameRenderer(
        scale=2, tiles=load(charset) if charset.exists() else None, intro_wav=None
    )
    yield r
    r.close()


def test_the_mixer_opens_mono(renderer: PygameRenderer) -> None:
    """The SID is a mono chip; there is no stereo in the original.

    Left alone SDL negotiates the *device's* layout, and on a 5.1 output that
    decodes every clip to six channels — 10.1 MB resident for 1.7 MB of wav.
    `pre_init(..., allowedchanges=0)` forbids the substitution. It must run
    before `pygame.init()`, which brings the mixer up itself.
    """
    init = pygame.mixer.get_init()
    if init is None:
        pytest.skip("no audio device")
    frequency, _size, channels = init
    assert channels == 1, (
        f"mixer opened with {channels} channels; every mono clip is being "
        "decoded that many times over"
    )
    assert frequency == 44_100


def test_a_glyph_is_rasterised_once_not_once_per_frame(
    renderer: PygameRenderer,
) -> None:
    """`_blit_cells` asks for one glyph **per character**, every frame.

    Profiled at 511 calls a frame on the instructions screen — 15,330
    rasterisations a second, the largest per-frame cost in the game.
    """
    needs.need(needs.CHARSET)
    calls: list[str] = []
    original = type(renderer)._render_glyph

    def counting(self, text, fg, bg=None, *, big=False, c64_font=True):  # type: ignore[no-untyped-def]
        calls.append(text)
        return original(self, text, fg, bg, big=big, c64_font=c64_font)

    type(renderer)._render_glyph = counting  # type: ignore[assignment]
    try:
        sim = Simulation(rng=random.Random(1))
        flow = GameFlow()
        flow.screen, flow.sim = Screen.INSTRUCTION_PAGES, sim
        renderer._sim, renderer._ship = sim, sim.ship

        renderer.draw(flow)
        first = len(calls)
        calls.clear()
        for _ in range(5):
            renderer.draw(flow)
        # The first frame rasterises each *distinct* glyph once — about 34 on
        # this page, not the ~511 characters drawn. That gap is the saving.
        assert 20 < first < 120, (
            f"{first} rasterisations on a cold frame; expected roughly one per "
            "distinct glyph, so the probe is not seeing the right path"
        )
        assert not calls, (
            f"{len(calls)} glyphs re-rasterised over 5 identical frames"
        )
    finally:
        type(renderer)._render_glyph = original  # type: ignore[assignment]


def test_the_glyph_cache_is_bounded(renderer: PygameRenderer) -> None:
    """The key includes the text, so an unbounded dict would grow forever.

    `_blit_at` passes whole status lines, which are effectively unlimited in
    variety; only short entries are worth keeping.
    """
    from alien_remake.render import c64

    white = c64.rgb(c64.WHITE)
    for i in range(renderer._GLYPH_CACHE_MAX * 2):
        renderer._c64_or_sysfont(f"{i % 10}", white)
    assert len(renderer._glyph_cache) <= renderer._GLYPH_CACHE_MAX

    long_text = "a status line far longer than the cache limit"
    before = len(renderer._glyph_cache)
    renderer._c64_or_sysfont(long_text, white)
    assert len(renderer._glyph_cache) == before, "long strings must not be cached"


def test_instruction_pages_are_parsed_once_per_file(tmp_path: Path) -> None:
    """`pages()` re-read and re-tokenised MENU1.prg on every frame.

    Cached on the **resolved** path, not on the optional argument — with `None`
    as the key a cached result would survive the asset root moving, which a
    test caught.
    """
    from alien_remake.core import instructions

    reads: list[Path] = []
    original = instructions._basic_lines

    def counting(path: Path):  # type: ignore[no-untyped-def]
        reads.append(path)
        return original(path)

    instructions._basic_lines = counting  # type: ignore[assignment]
    instructions._pages_for.cache_clear()
    try:
        first = instructions.pages()
        for _ in range(10):
            instructions.pages()
        if not first:
            pytest.skip("MENU1.prg not extracted")
        assert len(reads) == 1, f"MENU1.prg parsed {len(reads)} times, not once"
    finally:
        instructions._basic_lines = original  # type: ignore[assignment]
        instructions._pages_for.cache_clear()
