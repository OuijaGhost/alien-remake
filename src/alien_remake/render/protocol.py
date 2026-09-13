"""The attribute surface `PygameRenderer` shares with its mixins.

`PygameRenderer` was split across modules (D-191), and the pieces are mixins
rather than free functions because the renderer's state — surfaces, caches,
audio channels, per-screen frame counters — is genuinely shared.

Under mypy's `strict = true` a mixin that reads `self._surface` cannot
type-check alone. Declaring the shared attributes here once, and having both the
mixins and `PygameRenderer` inherit it, gives mypy the whole picture in every
module: a typo becomes an error instead of an `AttributeError` on the first
frame that happens to take that branch.

**Annotations only, no values.** `PygameRenderer.__init__` stays the single
place any of these is actually initialised.
"""

from __future__ import annotations

from collections import deque

from pathlib import Path

from typing import Any

import pygame

from ..core.crew import CrewMember  # noqa: F401
from ..core.menu import MenuController
from ..core.map import ShipMap
from ..core.sim import Simulation
from ..core.state import GameState
from . import romfont
from .deck_backdrop import DeckBackdrop
from .tiles import TileSet


class RendererState:  # noqa: B024
    """Shared renderer state, declared for the mixins' benefit."""

    # --- audio ------------------------------------------------------------
    #: Lazily-rendered SFX; `None` means "tried and unavailable" (D-088).
    _sfx_cache: dict[str, object | None]
    _intro_wav: Path | None
    _music_playing: bool
    #: The looping heartbeat bed and the composure it was rendered for (D-145).
    _heartbeat_channel: object | None
    _heartbeat_composure: int | None
    _heartbeat_rate: int | None
    _glyph_cache: dict[object, pygame.Surface]
    # Debug-overlay instrumentation (Ctrl+3). Not the original — see
    # `debug_overlay.py`.
    _dbg_frames: "deque[float]"
    _dbg_latency: "deque[float]"
    _dbg_last_present: float | None
    _dbg_input_at: float | None
    _dbg_memory: float | None
    _dbg_memory_at: float
    _dbg_last_tick: int
    _dbg_tick_at: float
    _dbg_tick_rate: float
    _dbg_overlay_ms: float
    _dbg_panel: pygame.Surface | None
    _dbg_panel_at: float
    #: Cached `SamplePlayer.loudness_report()` result — computed once, since
    #: it reads and analyses every recording found. `None` until first asked
    #: for. Not the original — see `audio.loudness`'s own module docstring.
    _dbg_audio_spec: list[Any] | None
    #: The tracker ping's channel — one continuous pulse, not a one-shot (D-150).
    _tracker_channel: object | None
    #: **T6.** Carried from `flow` each `draw()` — see `pygame_app.py`'s
    #: `PLAYING` branch and `debug_overlay._blit_turn_indicator`.
    _turns_on: bool
    _turn_count: int
    _turn_actor: str
    #: **Initiative (2026-09-05), not the original.** `None` when the current
    #: actor is a creature slot (no action-point budget applies) or when no
    #: initiative has been rolled at all.
    _turn_actions_left: int | None

    # --- the attack sequence (D-090/D-096/D-139) --------------------------
    _attacking: bool
    _attacking_crew_id: str | None
    _border_flash: int

    # --- the in-game CONTROL panel ----------------------------------------
    _menu: MenuController | None

    # --- surfaces & scale --------------------------------------------------
    _surface: pygame.Surface
    _ship: ShipMap | None
    _sim: Simulation | None
    _tile_cache: dict[int, pygame.Surface]
    _backdrop_cache: dict[int, pygame.Surface]
    #: Supplied sprites (D4), misses included — the alien is six a frame.
    _sprite_art_cache: dict[int, pygame.Surface | None]
    #: Supplied art with a varying ROM colour washed in (D4, `_signalled`).
    _sprite_wash_cache: dict[tuple[object, tuple[int, int, int]], pygame.Surface]
    #: Supplied deck plans (D3), misses included so a deck with no art is not
    #: re-searched every frame. Separate from `_backdrop_cache`, which holds
    #: the drawn result rather than the source.
    _deck_art_cache: dict[int, pygame.Surface | None]
    _backdrops: dict[int, DeckBackdrop]
    #: Jones's X while a run is in progress; `None` = not running (D-089).
    _jones_x: int | None
    _last_state: GameState | None
    _view_deck: int
    #: (crew id, room id) the map last followed, so a *move* can be told
    #: from a still frame (W1).
    _followed_where: tuple[str, str] | None
    #: Set by the wheel: hold this deck rather than snapping back (W1).
    _deck_override: bool
    _debug_markers: bool
    #: Where `_draw_menu_panel` actually put each entry: index into
    #: `MenuController.entries()` -> panel row, or `None` for a line that is
    #: off-screen this frame. **P2/P3** — pointer hit-testing inverts *this*
    #: rather than recomputing the layout, because the panel does not place
    #: entry N on row N: the crew panel and the CONTROL list both use fixed
    #: ROM slot maps, and the INDICATE room list scrolls. A second copy of that
    #: arithmetic would be a second thing to keep in step, and clicks would
    #: drift from what is drawn the moment it fell behind.
    _panel_placement: list[int | None]
    #: Clickable regions the *current* screen drew, in 320x200 field pixels.
    #: **P4-P6.** Each front-end screen records what it put on screen and the
    #: pointer inverts that, for the same reason `_panel_placement` exists: the
    #: three screens use three coordinate systems (the panel is character
    #: cells, the chooser is pixels at a 12px pitch, the manual is a footer
    #: strip), and a second copy of any of them is a second thing to keep in
    #: step. Rebuilt every frame, so a region cannot outlive what drew it.
    _hot: list[tuple[pygame.Rect, str, int]]
    #: Which hot region the pointer is over, or `None` — P5's hover feedback.
    _hover: tuple[str, int] | None
    #: The options model the last `_draw_options` drew (P4).
    _options_model: Any
    #: The startup report the boot screen draws (B1/B2).
    startup_report: Any
    #: Sampled-audio player, or None (S1/S2).
    _samples: Any
    #: Whether interface cues may sound at all (the `sound` row).
    _ui_sound: bool
    #: The developer-mode testing keys, key -> what it does. Declared because
    #: the overlay reads it to list them on screen.
    DEV_KEYS: dict[int, str]
    #: The window the field is composed into. Declared because the debug panel
    #: is drawn onto it directly (it lives in the border, outside the field).
    _window: pygame.Surface
    #: When each interface cue last sounded, in `pygame.time.get_ticks()`
    #: milliseconds — the S6 retrigger floor (`render.audio.CUE_FLOOR_MS`).
    _cue_last_ms: dict[str, int]
    #: Whether the game's own effects come from recordings.
    _sampled_game_audio: bool
    _clock_ref: tuple[float, float] | None

    def _start_attack_composite(self, crew_id: str) -> None:
        raise NotImplementedError  # declaration only

    def _stop_attack_composite(self) -> None:
        raise NotImplementedError  # declaration only


    def _update_heartbeat(self, state: GameState) -> None:
        raise NotImplementedError  # declaration only


    def _update_tracker_ping(self, state: GameState) -> None:
        raise NotImplementedError  # declaration only
    _romfont: romfont.RomFont | None
    _rom_shifted: bool
    _tiles: TileSet | None
    _title_egg: pygame.Surface | None
    _frame_count: int

    # --- per-screen entry frames, so each animation runs from a local zero ---
    #: D-143/D-175/D-176. Without these, the WELCOME sweep, the quit advert and
    #: the legend screens would animate off the app's *global* frame count — so
    #: how long the player dwelt on the previous screen would change what they
    #: see next.
    _welcome_entered_frame: int | None
    _exit_entered_frame: int | None
    _legend_entered_frame: int | None
    _legend_played: int

    # --- methods the mixins call but do not own ------------------------------
    # Declared so each mixin type-checks alone (see this module's docstring).
    # These are the genuinely shared primitives: presentation, the text
    # renderers, the sprite cache, `_sound` (owned by `AudioMixin`), and the two
    # Narcissus screens that both the front end and the ending draw.

    def _hot_clear(self) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _hot_add(self, rect: pygame.Rect, kind: str, index: int = 0) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _hot_cells(self, col: int, row: int, width: int, kind: str,
                   index: int = 0) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _present(self, border: tuple[int, int, int] | None = None) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _blit_sprite(self, index: int, cx: int, cy: int,
                     colour: tuple[int, int, int], *,
                     varies: bool = False) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_portrait(self, crew_id: str, index: int, cx: int, cy: int,
                       colour: tuple[int, int, int], *,
                       varies: bool = False) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _supplied_sprite(self, index: int) -> pygame.Surface | None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _signalled(self, art: pygame.Surface, key: object,
                   colour: tuple[int, int, int]) -> pygame.Surface:
        raise NotImplementedError  # declaration only; see this module's docstring


    # The shared text helpers, which live in `text.py` (DISC-251). Declared
    # here for the same reason the state attributes are: `endscreen.py` and
    # `frontend.py` call them without defining them, and each mixin has to
    # type-check on its own under `strict = true`.
    def _draw_debug_overlay(self, state: GameState) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_debug_panel(self) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def field_rect(self) -> pygame.Rect:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _debug_mark_input(self) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _debug_mark_present(self) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_cells(self, text: str, col: int, row: int,
                    colour: tuple[int, int, int], *,
                    bg: tuple[int, int, int] | None = None,
                    c64_font: bool = False) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_wrapped(
        self, text: str, col: int, row: int, fg: tuple[int, int, int],
        *, c64_font: bool = False,
    ) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_center(self, text: str, y: int, colour: tuple[int, int, int], *, big: bool=False, bg: tuple[int, int, int] | None=None, c64_font: bool=True) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_at(self, text: str, x: int, y: int, colour: tuple[int, int, int], *, bg: tuple[int, int, int] | None=None, c64_font: bool=True) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_c64_text(self, codes: 'list[int] | bytes', col: int, row: int, colour: tuple[int, int, int]) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_tm(self, x: int, y: int) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_screen_code(self, code: int, col: int, row: int, fg: tuple[int, int, int]) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_petscii(self, raw: str, col: int, row: int, fg: tuple[int, int, int], bg: tuple[int, int, int]) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_center_keyed(self, segments: tuple[tuple[str, tuple[int, int, int] | None], ...], y: int, colour: tuple[int, int, int]) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring

    def _blit_codes(self, codes: "list[int]", col: int, row: int,
                    colour: tuple[int, int, int]) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _c64_or_sysfont(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
        *,
        big: bool = False,
        c64_font: bool = True,
    ) -> pygame.Surface:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _render_c64_text(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
    ) -> pygame.Surface | None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _render_rom_text(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
    ) -> pygame.Surface | None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _sprite_surface(self, index: int, colour: tuple[int, int, int]) -> pygame.Surface | None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _draw_narcissus_moon(self) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _draw_narcissus_cockpit(self) -> None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _load_cockpit_capture(self) -> tuple[list[int], list[int]] | None:
        raise NotImplementedError  # declaration only; see this module's docstring


    def _sound(self, effect: str) -> object | None:
        raise NotImplementedError  # declaration only; see this module's docstring
