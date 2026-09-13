"""Interactive A/B bench for the CRT layer (`render/crt.py`).

Tuning an analog look without an A/B toggle is guessing, so this exists before
the effect is wired into the game at all. It renders a real game frame, runs the
chain over it at the tube's own 120 Hz, and lets each effect be switched
independently against the clean image.

    python tools/crt_bench.py            # interactive
    python tools/crt_bench.py --shots    # write A/B PNGs and exit

Keys
----
    TAB      hold to see the clean image (the A/B)
    SPACE    fire the full glitch (change character / INDICATE)
    G        fire the degauss (the deck-change one)
    0        toggle the whole layer
    1..9     toggle scanlines / bleed / noise / interlace / bloom /
             wave / vroll / chroma-shift / raster bar

    [ ]      scanline depth          K L   scanline blur
    - =      noise amount            N M   motion blur (phosphor trail)
    , .      raster strength         ; '   raster speed
    < >      glitch speed (how fast the scramble moves)
    Z X      degauss warp            C V   cathode flash (both transients)
    F H      chroma shift, in pixels (the character of both transients)
    O P      phosphor mask strength  U I   mask pitch (triad width, screen px)
    `        mask on/off             R     slot mask <-> aperture grille

The mask is the one stage drawn at window size, so it only appears at 3x and
above -- three phosphors need three subpixels. Run with --scale 4 or 6 to see it
the way a large window does.

    T        print the current settings as a `CrtSettings(...)` line
    S        save a clean/effect PNG pair
    ESC      quit

Everything is live: the numbers in the status bar are the ones to hand back, and
`T` prints them in the form they go into `crt.preset()`.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pygame  # noqa: E402

from alien_remake.core.flow import GameFlow, Screen  # noqa: E402
from alien_remake.core.menu import MenuController  # noqa: E402
from alien_remake.core.sim import Simulation  # noqa: E402
from alien_remake.render.crt import (  # noqa: E402
    GLITCH_GENTLE,
    CrtProcessor,
    CrtSettings,
    shadow_mask,
)
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402
from alien_remake.render.layout import _HEIGHT, _WIDTH  # noqa: E402
from alien_remake.render.tiles import load as load_tiles  # noqa: E402

TOGGLES = [
    ("scanlines", pygame.K_1), ("chroma_bleed", pygame.K_2),
    ("noise", pygame.K_3), ("interlace", pygame.K_4),
    ("bloom", pygame.K_5), ("wave", pygame.K_6),
    ("vroll", pygame.K_7), ("chroma_shift", pygame.K_8),
    ("raster", pygame.K_9),
    ("mask", pygame.K_BACKQUOTE),
]

#: field, (down key, up key), step, low, high. One table so a new knob is one
#: row rather than another `elif` in the event loop.
KNOBS = [
    ("scanline_depth", (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET), 0.05, 0.0, 1.0),
    ("scanline_blur", (pygame.K_k, pygame.K_l), 0.05, 0.0, 1.0),
    ("noise_amount", (pygame.K_MINUS, pygame.K_EQUALS), 1, 0, 64),
    ("motion_blur", (pygame.K_n, pygame.K_m), 0.05, 0.0, 0.9),
    ("raster_strength", (pygame.K_COMMA, pygame.K_PERIOD), 0.01, 0.0, 0.6),
    ("raster_speed", (pygame.K_SEMICOLON, pygame.K_QUOTE), 2.0, 0.0, 120.0),
    ("glitch_speed", (pygame.K_LESS, pygame.K_GREATER), 0.02, 0.0, 1.0),
    ("degauss_warp", (pygame.K_z, pygame.K_x), 0.5, 0.0, 30.0),
    ("flash_glow", (pygame.K_c, pygame.K_v), 0.05, 0.0, 1.0),
    ("chroma_shift_px", (pygame.K_f, pygame.K_h), 1.0, 0.0, 24.0),
    ("mask_strength", (pygame.K_o, pygame.K_p), 0.05, 0.0, 1.0),
    ("mask_pitch", (pygame.K_u, pygame.K_i), 3, 3, 12),
]


def _nudge(settings: CrtSettings, key: int) -> bool:
    """Apply whichever knob owns ``key``. True if one did."""
    for name, (down, up), step, low, high in KNOBS:
        if key not in (down, up):
            continue
        value = getattr(settings, name) + (step if key == up else -step)
        value = min(high, max(low, value))
        setattr(settings, name, round(value, 3) if isinstance(step, float) else value)
        return True
    return False


def _as_code(settings: CrtSettings) -> str:
    """The settings as the line that would go into `crt.preset()`."""
    default = CrtSettings()
    changed = [
        f"{f}={getattr(settings, f)!r}"
        for f in default.__dataclass_fields__
        if f != "enabled" and getattr(settings, f) != getattr(default, f)
    ]
    return "CrtSettings(enabled=True" + "".join(", " + c for c in changed) + ")"


def _ensure_display() -> None:
    """Bring pygame back up.

    `PygameRenderer.close()` calls `pygame.quit()`, which tears down the font
    and display subsystems the bench needs afterwards -- so every helper that
    builds a renderer has to put them back. Skipping this is what made the
    interactive bench die on `SysFont` with "font not initialized" while
    `--shots` survived, purely because the shots path happened to build
    another renderer before it needed a font.
    """
    if not pygame.display.get_init():
        pygame.init()
        pygame.display.set_mode((_WIDTH, _HEIGHT))


def _game_frame(screen: Screen = Screen.PLAYING, seed: int = 1) -> "np.ndarray[Any, np.dtype[np.uint8]]":
    """One real frame of the game, as a (w, h, 3) array.

    An array rather than a Surface because the renderer is closed before this
    returns, and a Surface must not outlive the pygame session that made it.
    """
    charset = ROOT / "out" / "charset.bin"
    tiles = load_tiles(charset) if charset.exists() else None
    renderer = PygameRenderer(scale=2, tiles=tiles, intro_wav=None)
    try:
        sim = Simulation(rng=__import__("random").Random(seed))
        flow = GameFlow()
        flow.screen, flow.sim = screen, sim
        renderer._sim, renderer._ship = sim, sim.ship
        renderer._menu = MenuController(sim)
        renderer._menu.selected_crew = next(
            c.id for c in sim.state.crew.values() if c.alive
        )
        renderer._frame_count = 60
        for _ in range(30):
            sim.advance()
        renderer.draw(flow)
        return pygame.surfarray.array3d(renderer._surface)
    finally:
        renderer.close()


def _to_surface(arr: "np.ndarray[Any, np.dtype[np.uint8]]") -> pygame.Surface:
    return pygame.surfarray.make_surface(arr)


#: Cached like the renderer's, keyed by everything that shapes the triads.
_MASKS: dict[tuple[object, ...], pygame.Surface] = {}


def _mask_for(settings: CrtSettings, size: tuple[int, int]) -> pygame.Surface | None:
    """The phosphor mask at window size, or `None` when it cannot be drawn."""
    if not (settings.enabled and settings.mask and settings.mask_strength > 0):
        return None
    if size[0] // 320 < max(3, settings.mask_pitch):
        return None
    key = (size, settings.mask_pitch, round(settings.mask_strength, 3),
           settings.mask_stagger)
    surface = _MASKS.get(key)
    if surface is None:
        surface = pygame.surfarray.make_surface(
            shadow_mask(size, settings.mask_pitch, settings.mask_strength,
                        settings.mask_stagger)
        )
        _MASKS[key] = surface
    return surface


def _save(surface: pygame.Surface, path: Path, factor: int = 3,
          settings: CrtSettings | None = None) -> Path:
    """Write a PNG, scaled up so the scanline pitch is actually visible.

    The mask goes on *after* the scale, exactly as the renderer does it — a PNG
    saved at native size could not show a triad at all.
    """
    size = (surface.get_width() * factor, surface.get_height() * factor)
    big = pygame.transform.scale(surface, size)
    mask = _mask_for(settings, size) if settings is not None else None
    if mask is not None:
        big.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    pygame.image.save(big, str(path))
    return path


def save_shots(out_dir: Path) -> list[Path]:
    """Write a clean/effect pair per screen, plus a mid-glitch frame."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for screen in (Screen.PLAYING, Screen.GAME_SELECTION):
        arr = _game_frame(screen)
        _ensure_display()
        settings = CrtSettings(enabled=True)
        proc = CrtProcessor((arr.shape[0], arr.shape[1]), settings)

        tag = screen.name.lower()
        written.append(_save(_to_surface(arr), out_dir / f"crt_{tag}_a_clean.png"))

        for _ in range(8):                       # settle the tube phase
            proc.advance(1 / 120)
        written.append(
            _save(_to_surface(proc.process(arr)), out_dir / f"crt_{tag}_b_effect.png",
                  settings=settings)
        )

        proc.glitch()
        for _ in range(6):
            proc.advance(1 / 120)
        written.append(
            _save(_to_surface(proc.process(arr)), out_dir / f"crt_{tag}_c_glitch.png",
                  settings=settings)
        )

        # The degauss, sampled early enough to catch the cathode bloom.
        proc = CrtProcessor((arr.shape[0], arr.shape[1]), CrtSettings(enabled=True))
        for _ in range(8):
            proc.advance(1 / 120)
        proc.glitch(GLITCH_GENTLE)
        for _ in range(3):
            proc.advance(1 / 120)
        written.append(
            _save(_to_surface(proc.process(arr)), out_dir / f"crt_{tag}_d_degauss.png",
                  settings=settings)
        )
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A/B bench for the CRT layer.")
    parser.add_argument("--shots", action="store_true",
                        help="write A/B PNGs to out/crt/ and exit")
    parser.add_argument("--scale", type=int, default=3)
    args = parser.parse_args(argv)

    if args.shots:
        for path in save_shots(ROOT / "out" / "crt"):
            print(f"  wrote {path.relative_to(ROOT)}")
        return 0

    arr = _game_frame()
    _ensure_display()                    # the renderer took pygame down with it
    w, h = arr.shape[0], arr.shape[1]
    window = pygame.display.set_mode((w * args.scale, h * args.scale))
    pygame.display.set_caption("CRT bench — TAB clean, SPACE glitch, ESC quit")
    settings = CrtSettings(enabled=True)
    proc = CrtProcessor((w, h), settings)
    font = pygame.font.SysFont("monospace", 12)
    scaled = pygame.Surface(window.get_size())
    last = time.perf_counter()
    fps = 120.0
    show_clean = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0
                if event.key == pygame.K_TAB:
                    show_clean = True
                elif event.key == pygame.K_SPACE:
                    proc.glitch()
                elif event.key == pygame.K_g:
                    proc.glitch(GLITCH_GENTLE)
                elif event.key == pygame.K_0:
                    settings.enabled = not settings.enabled
                elif event.key == pygame.K_s:
                    for path in save_shots(ROOT / "out" / "crt"):
                        print(f"  wrote {path.relative_to(ROOT)}")
                elif _nudge(settings, event.key):
                    pass
                elif event.key == pygame.K_t:
                    print("  " + _as_code(settings))
                elif event.key == pygame.K_r:
                    settings.mask_stagger = not settings.mask_stagger
                else:
                    for name, key in TOGGLES:
                        if event.key == key:
                            setattr(settings, name, not getattr(settings, name))
            if event.type == pygame.KEYUP and event.key == pygame.K_TAB:
                show_clean = False

        now = time.perf_counter()
        dt = now - last
        proc.advance(dt)
        last = now
        # Smoothed, or the number is unreadable at 120 Hz.
        fps = 0.9 * fps + 0.1 / dt if dt > 0 else fps

        out = arr if show_clean else proc.process(arr)
        pygame.transform.scale(_to_surface(out), window.get_size(), scaled)
        mask = None if show_clean else _mask_for(settings, window.get_size())
        if mask is not None:
            scaled.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        window.blit(scaled, (0, 0))

        on = [n for n, _ in TOGGLES if getattr(settings, n)]
        lines = [
            f"{'CLEAN' if show_clean else 'EFFECT'}  "
            f"layer={'on' if settings.enabled else 'off'}  "
            f"{'GLITCH' if proc.glitching else '      '}  {fps:5.1f} fps",
            f"scan {settings.scanline_depth:.2f}/blur {settings.scanline_blur:.2f}  "
            f"noise {settings.noise_amount}  trail {settings.motion_blur:.2f}  "
            f"bar {settings.raster_strength:.2f}@{settings.raster_speed:.0f}  "
            f"gspeed {settings.glitch_speed:.2f}  "
            f"warp {settings.degauss_warp:.1f}/flash {settings.flash_glow:.2f}  "
            f"chroma {settings.chroma_shift_px:.0f}px",
            " ".join(on),
        ]
        for i, text in enumerate(lines):
            window.blit(font.render(text, False, (0, 255, 0)), (4, 4 + i * 14))
        pygame.display.flip()
        pygame.time.wait(max(0, int(1000 / 120) - 1))


if __name__ == "__main__":
    raise SystemExit(main())
