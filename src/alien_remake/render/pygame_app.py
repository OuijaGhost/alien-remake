"""The pygame rendering/input backend — the one third-party-dep module.

This is the **only** module in the project that imports pygame (DECISIONS D-009);
it is loaded lazily by :mod:`alien_remake.__main__`, so nothing requires pygame
unless the player actually launches the graphical mode. It satisfies the
:class:`~alien_remake.render.base.Renderer` protocol.

This was kept deliberately thin, then gained the per-deck map, drawn with the
game's **own** extracted C64 tiles (DECISIONS D-009) via an optional
:class:`~alien_remake.render.tiles.TileSet`. The crew roster gives each
member's state of mind (the PCS, GAME_SPEC §5) and an authentic keyboard-cursor
order entry (DECISIONS D-010 #1): pick a crew member, point the target cursor,
issue an order verb — the crew may obey or refuse per the PCS. Items add the
Command Monitor overlay (``C`` toggles it) — Damage Reports for the watched deck
and a Weapons & Tools list for the selected crew's room, cycled with ``Tab`` so
``G`` picks up a specific item instead of a whole room. The renderer draws the Alien
(a red ``X``) and Jones (a yellow ``j``) on the map, and adds the Special
Options (`O`/`P` open/seal the targeted airlock, `N` launches the Narcissus,
`X` starts auto-destruct, `H` toggles the selected crew's hypersleep, `J`
catches Jones) via a second poll method, `poll_special_options`. The audio layer loops
`out/intro.wav` at startup via `pygame.mixer` (`loops=-1`, matching the real
title screen — DECISIONS D-016) — best-effort: a missing file or unavailable
audio device just skips playback (this is decorative polish, not gameplay
logic, so it fails soft rather than raising). The WAV itself is the
emulated-real SID intro rendered by `alien_remake.audio.intro` (DECISIONS
D-010 #3), not invented here. The active game mode is on the
status line (GAME_SPEC §9/§11 #6).

**Fidelity fix:** the
per-deck map previously drew a uniform grid of identical placeholder tiles —
recognizably *a* map, but nothing like the real screen. `deck_backdrop.py`
decodes the real captured screen RAM for each deck (`docs/reference/
*_0400.bin`) through the same authentic charset SG already extracts, so the
actual room shapes/walls now render when those captures are present; the
per-room placeholder grid is the fallback when they aren't (e.g. a fresh clone
without that reference material).
"""

from __future__ import annotations

import io
import sys
from typing import Any
import time
from collections import deque
from pathlib import Path
from typing import Sequence

import pygame  # the project's one optional runtime dependency (D-009)

from .. import assets, media
from ..core import constants
from ..core.flow import SELECTION_OPTIONS, GameFlow, InputEvent, Screen
from ..core.map import ShipMap
from ..core.menu import GENTLE_VIEW_CHANGE, MenuCategory, MenuController
from ..core.options import OptionsModel
from ..core.modes import FrontEnd
from ..core.nostromo import NARCISSUS
from ..core.orders import Order
from ..core.sim import Simulation
from ..core.special_options import SpecialOption
from ..core import ductmap, opening_name, sound
from ..core import gamedata_snapshot as data
from ..core.crew import CrewMember
from ..core.scoring import competence_rating
from ..audio import sfx
from ..core.state import GamePhase, GameState, WinRoute
# Shared geometry/timing (D-191). Re-exported: the tests import these names
# from `pygame_app`, which stays the render package's facade.
from .layout import (  # noqa: F401
    _BASIC_POKE_S, _BORDER_REVEAL_POKES, _C64_CELL, _COLS, _FRAME_HZ, _HEIGHT,
    _KEY_SLOT_COL, _KEY_SLOT_ROW, _PORTRAIT_SLOTS, _ROWS, _SPIRAL_COLS,
    _SPIRAL_ROWS, _SPIRAL_START_COLOUR, _SPIRAL_T1, _SPIRAL_T2,
    _SPRITE_BANK_BASE, _TEXT_REVEAL_RATE, _WIDTH,
)
from . import audio
from .audio import AudioMixin
from .crt import (
    GLITCH_FULL,
    GLITCH_GENTLE,
    TUBE_HZ,
    CrtProcessor,
    CrtSettings,
    shadow_mask,
)
from .endscreen import EndScreenMixin
from .frontend import _ENDING_ALIEN_DEAD, _ENDING_NARCISSUS, FrontEndMixin
from .layout import _CELL, _MAP_COLS  # noqa: F401
from ..screens.panels import PANEL_COL as _PANEL_COL
from .play import PlayMixin
from .text import TextMixin
from . import c64, romfont
from . import debug_overlay
from .debug_overlay import DebugOverlayMixin
from .deck_backdrop import DeckBackdrop, load_deck_backdrops
from .tiles import TileSet
from alientools.charset import Bitmap

_SCALE = 2


# docs/reference/*_0400.bin are optional oracle captures (deck_backdrop.py);
# missing entirely on a fresh clone that doesn't carry them is fine — the
# placeholder grid is the fallback.
_DEFAULT_REFERENCE_DIR = Path("archive") / "reference"




# The VIC border register `$D020` framing the field. The **play** screen sets
# it BLUE ([C $7013] DISASSEMBLY §6.5), but the loader's front-end screens run
# with it BLACK — read live from the machine on the WELCOME menu 2026-08-01
# (`vice_vicii_get_state` -> `border_color` 0). D-064.
_BORDER_COLOUR = c64.rgb(c64.BLUE)

#: Where the CRT layer is allowed to run. **Every screen (owner's call,
#: 2026-08-28), reversing the in-game-only rule DISC-264 recorded.** The
#: original reasoning was that the loader screens are seen before a player has
#: agreed to anything, so they should stay exactly as decoded. The owner's
#: position is the simpler one: a tube is a tube from the moment it is on, and
#: switching the effect in at the play screen reads as a glitch rather than as
#: a choice. `None` means "no restriction"; the `crt` setting is the only gate.
_CRT_SCREENS: frozenset[Screen] | None = None
#: How long the `wait_keypress_flash` rainbow lasts, in renderer frames. The
#: ROM's loop is bounded by `$8666 INC $6514 / BNE` (256 iterations) and by the
#: player letting go of the key; a short burst is the visible equivalent.
_BORDER_FLASH_FRAMES = 6
# Colour-key sentinel for transparent ROM-font cells (D-065). Magenta is
# outside the 16-entry C64 palette, so it can never collide with real ink.
_ROM_TEXT_CLEAR = (255, 0, 255)
# **R-02 (D-051): a real VIC border.** On a C64 the 320x200 text area is the
# whole addressable screen and the border is *outside* it — the remake used to
# paint a 6px frame *over* the field, eating two columns/rows of the 40x25
# grid and pushing the map/panel out of alignment. Now `_surface` is exactly
# the 40x25 field and it is blitted into a larger bordered window
# (`_present`), so column/row arithmetic is exact.
#: Fullscreen toggle: F11 (desktop convention) or Alt+Enter (game convention).
#: Neither collides with the original's own input, which is the four directions
#: plus fire. Alt+Enter has to be tested *before* the key tables, because Return
#: is bound to FIRE and would otherwise swallow it.
#: Pad buttons for the two inputs a gamepad otherwise cannot reach. Standard
#: layout: 0 = south/A, 1 = east/B, 6 = back/select. See `_poll_joystick` for
#: why these are dedicated buttons and not fire.
_JOY_BTN_SELECT_FULL = 0
_JOY_BTN_SELECT_SHORT = 1
_JOY_BTN_QUIT = 6


def _is_fullscreen_key(event: pygame.event.Event) -> bool:
    if event.key == pygame.K_F11:
        return True
    return event.key == pygame.K_RETURN and bool(event.mod & pygame.KMOD_ALT)

_BORDER_X = 32   # unscaled px of border left/right of the 320px field
_BORDER_Y = 32   # unscaled px of border above/below the 200px field

# --- WELCOME screen, transcribed live from the running disk (D-064) ----------
# [C-live 2026-08-01] Read out of the real machine while the loader's WELCOME
# menu was on screen: screen RAM `$0400`, colour RAM `$D800` (bank `io`), and
# the VIC/sprite registers. Not eyeballed from a screenshot.
#
# The ring is solid blocks (screen code `$A0`) over a 16-entry colour ramp.
# Corner precedence proves the draw order is top -> right -> bottom -> left
# (see `_draw_welcome_border`), so later sides win where they overlap.
_WELCOME_BORDER_CHAR = 0xA0





# The captured backdrop's left columns are the ship map; the rest is the
# CONTROL side panel's static labels (already drawn separately by
# `_draw_menu_panel`, with live data) — cropped off here so the two don't
# overlap. Read off the real captures (docs/reference/*_0400.bin): wall/floor
# glyphs never extend past column ~24, and the panel text never starts before
# column ~30, so the split at 30 clears both with margin.

# Menu-screen keys -> abstract InputEvents (title/selection/opening/end). Space
# and Return both fire (the original's joystick button; the user confirmed space
# fired). Arrows move the menu cursor; 1/2 are the Control:1/Control:2 shortcuts.
_MENU_KEYS = {
    pygame.K_UP: InputEvent.UP,
    pygame.K_DOWN: InputEvent.DOWN,
    pygame.K_LEFT: InputEvent.LEFT,
    pygame.K_RIGHT: InputEvent.RIGHT,
    pygame.K_SPACE: InputEvent.FIRE,
    pygame.K_RETURN: InputEvent.FIRE,
    pygame.K_1: InputEvent.SELECT_FULL,
    pygame.K_2: InputEvent.SELECT_SHORT,
    # Not the original: the selection screen's two extra rows (`core.options`,
    # `Screen.MANUAL`). Bare keys, unlike the ROM's Ctrl+1/Ctrl+2 - see
    # `InputEvent.SELECT_INSTRUCTIONS`.
    pygame.K_3: InputEvent.SELECT_INSTRUCTIONS,
    pygame.K_4: InputEvent.SELECT_OPTIONS,
    # CR5: bare "5" opens CREDITS, same shape as 3/4 - not a Ctrl chord, the
    # ROM has nothing here to imitate the polarity of.
    pygame.K_5: InputEvent.SELECT_CREDITS,
    pygame.K_y: InputEvent.YES,          # instructions "Y OR N"
    pygame.K_n: InputEvent.NO,
    # D-175: the WELCOME menu's Q loads the EXITO advert, it does not exit.
    pygame.K_q: InputEvent.QUIT_TO_ADVERT,
}

_MENU_FG = c64.rgb(c64.BLACK)


_WIN_MESSAGES = {
    WinRoute.EVACUATED: _ENDING_NARCISSUS,
    WinRoute.ALIEN_KILLED: _ENDING_ALIEN_DEAD,
    WinRoute.ALIEN_AIRLOCKED: _ENDING_ALIEN_DEAD,
}

# **[C $9528-$954C] D-144/D-147, live-confirmed.** `setup_cursor_sprite` —
# the routine `menu_option_dispatch` calls for a character in NARCISSUS
# instead of any deck-template loader — reuses **sprite 0** as the moon
# outside the cockpit window: pointer `$07F8 = $D1` (the very next sprite
# after the title's 8 egg sprites, exactly as the user spotted on the sprite
# sheet), colour WHITE (`$D027 = 1`), position ($D000,$D001) = (172, 50), and
# `$D01B = 1` — that register is sprite-to-background **priority**, not
# multicolor (the live capture reads `$D01C = 0`): the moon is a HIRES white
# sprite drawn BEHIND character ink, so the window frame occludes it and it
# shows only through the window's cut-out cells.
_MOON_POINTER = 0xD1





_MOON_VIC_POS = (172, 50)

# **[C-live] D-147 — the NARCISSUS cockpit, THE REAL MACHINE'S OWN BYTES.**
# The earlier reconstruction quantised the player's screenshot into colour
# blocks (D-146's grid); this replaces it with the actual screen RAM and
# colour RAM read out of the running game: a crew member was poked into room
# 34 and the ROM's own selection routine (`guard_alien_present $7720`) was
# executed in place via a self-restoring patch to `main_loop`'s first JSR
# (`tools/vice-mcp/capture_cockpit_real.py`), then `$0400`/`$D800` dumped.
# Saved as oracle captures in the project's standard format:
# `docs/reference/narcissus_0400.bin` / `narcissus_d800.bin`.
#
# What the dump shows: the whole picture is THREE glyphs — `$20` (full ink:
# this cut-out charset's `$20` is all-0 bits = solid colour), `$A0` (no ink =
# black cut-through: the window, the corner wedges), and `$EE`/`$EF` (the
# instrument dials) — with the art carried almost entirely by COLOUR RAM
# (greys 12/15/11, brown 9 for the chairs). That is why no 540-byte template
# exists anywhere in the PRG and every static search failed: the cockpit is
# procedure + colour, not a stored screen.
_COCKPIT_ROWS_USED = 19            # rows 0-18 of the capture carry the art


# ASCII -> the game's own screen-code charset.
#
# **This font is NOT standard PETSCII.** Lower-case a-z are `$01-$1A`, capitals
# are the same +`$80` (the high bit is *case*, not reverse video), space is
# `$A0`, `:` is `$1C`, `%` is `$A5`, `,` is `$AC`, and the digits live at
# `$B0-$B9` in the reverse-video half rather than at the textbook `$30-$39`.
#
# **`$AE` is a period that renders BLANK** — all 1-bits, like the space. That
# is not a decode error: `$7CEB` holds `8F AE 8B AE` for the status word "O.K."
# and the `$7A10` template uses runs of `$AE` as dotted fill, so `$AE` is what
# the ROM writes where a period belongs and this charset simply has no period
# glyph. Mapping it reproduces the ROM's bytes; dropping it would send the
# whole string to SysFont.
#
# **What will bite you:** anything not in this map is deliberately absent, not
# forgotten. `_render_c64_text` returns None for a string containing one and
# the caller falls back to the system font — which is the intended behaviour,
# because a guessed glyph ships a wrong picture that looks authentic. Add a
# character only after rendering it out of `out/charset.bin` and looking at it;
# two entries here were assumed from byte positions and disproven exactly that
# way.
#
# Derivation: DISCOVERIES D-039 (the mapping and the two disproven
# assumptions), D-078 (the digits), P-7 (the period).
_ASCII_TO_SCREEN_CODE: dict[str, int] = {
    " ": 0xA0, ":": 0x1C, "%": 0xA5, ".": 0xAE, ",": 0xAC,
}
for _i, _c in enumerate("abcdefghijklmnopqrstuvwxyz"):
    _ASCII_TO_SCREEN_CODE[_c] = _i + 1
    _ASCII_TO_SCREEN_CODE[_c.upper()] = (_i + 1) | 0x80
for _d in range(10):
    _ASCII_TO_SCREEN_CODE[str(_d)] = 0xB0 + _d      # [C, D-078]
del _i, _c, _d






# **[C $4F5E-$4F78] D-146 — the run LOOPS; $F0 is only the stop line.**
# `update_3` does `LDA $D006 / ADC #$04 / STA $D006` each step, then
# `CMP #$F0 / BCC $4F7A` — below $F0 it just animates on. At/past $F0 it
# checks `$64BA` (the stop REQUEST, set by selecting a character `$7732`,
# the attack starting `$4FA2`, or map re-entry `$7083`): only then does it
# blank the sprite (`$D007 = 0`) and clear the run flag. With no stop
# pending the add simply continues and **wraps 8-bit through $FF -> $00** —
# the cat re-enters from the left seamlessly and keeps crossing until told
# to stop, and even then finishes its current crossing to the right edge.
# `maybe_clear_64ba ($4FF1)` is the starter (X=0, Y=$92, frame $C4) — and a
# second call while already running just clears the pending stop, which is
# what keeps the loop alive while Jones stays in the selected crew member's
# room ($88F9-$8919 re-fires it every scan pass).







# R-05 (2026-07-24): the Alien's real on-map sprite, replacing the red "X"
# placeholder. `update_1 ($4EE8)` animates it: `tbl_alien_anim ($4EDC)` = the
# 12-byte sequence below, each entry a frame **value** (0-3) that gets
# `ADC #$A0` into a sprite pointer — i.e. only **4 distinct frames** exist
# (pointers $A0-$A3 = `TileSet.sprites[0..3]`, the same pointer-relative
# indexing already used by `_CHAR_SPRITE`/`_PORTRAIT_SLOTS`, cross-checked:
# `_PORTRAIT_SLOTS[0]=29` = pointer `$BD` = `$07F8`'s first byte, confirmed
# elsewhere in this file's own history), ping-ponged 0→1→1→2→2→3→3→2→2→1→1→0
# — a pulse/breathe cycle, not a walk-cycle. **Confirmed [C $D015]: single-
# colour, not multicolor** — `main_dispatch ($5ECE)`, the last code to touch
# `$D01C` (sprite-multicolor enable) before active play, clears it to 0; no
# code between there and `begin_active_play` re-enables it.
# **PV-28 (colour half) closed 2026-08-07 (D-170) - it is GREEN, and it was
# always static.** `$4E8E LDA #$05` then `STA $D02B / $D02C / $D02D / $D02E`
# sets sprites **4, 5, 6 and 7 all to colour 5** in one go, and `$D015 = $F0`
# at `begin_active_play` enables exactly those four - so whichever channel the
# creature occupies, it is green. This was tagged as needing a live capture;
# an operand scan for stores into `$D027-$D02E` answered it in seconds. (Green
# also matches the title screen's egg, `init_c $5DEB`, all sprite colour 5.)
_ALIEN_SPRITE_COLOUR = 5          # [C $4E8E] VIC green
# **Stale `[?]` removed 2026-09-05 (P9-B goal session):** this line used to
# read "colour below is kept as the pre-R-05 placeholder red, still `[?]`" —
# but the frame table two lines up is already cited as `tbl_alien_anim
# ($4EDC)`, the ROM's own 12-byte sequence, and the colour just above is
# `[C $4E8E]`-confirmed green (D-170). There has been no placeholder red, and
# nothing left uncalibrated, since R-05 replaced the "X" marker with the real
# sprite; the note was simply never updated when both closed.
_ALIEN_SPRITE_FRAMES = (0, 1, 1, 2, 2, 3, 3, 2, 2, 1, 1, 0)
# **PV-28 closed 2026-08-07 (D-180) - fully derived, and there is no divider
# inside `update_1` at all.** `$64BF` is the frame *index*, not a counter:
# `$4EEE DEC $64BF / BPL / LDA #$0B / STA $64BF` walks the 12-entry table at
# `$4EDC` backwards and wraps, one entry per call. The division happens one
# level up, in `game_tick_dispatch ($4D19)`::
#
#     4D19  DEC $6579 / BPL $4D2F      ; 9 IRQs per trigger
#     4D1E  LDA #$08 / STA $6579
#     4D23  JSR update_1
#
# and `$4D08`'s `LDA $D019 / AND #$81 / CMP #$81 / BEQ irq_raster_split` sends
# only the *raster* interrupt to the sprite multiplexer, so `game_tick_dispatch`
# runs on the ordinary 60 Hz jiffy IRQ. 60/9 = **6.67 Hz**, one frame every 9
# jiffies - which is what the old comment said, and it was right.
#
# The `[?]` was really about units: this is a count of **C64 jiffies**, and the
# renderer's own counter runs at `_FRAME_HZ`. Derive it rather than reuse the 9.
_ALIEN_ANIM_HZ = 60.0 / 9.0        # [C $4D19] 6.67 Hz
_ALIEN_SPRITE_FRAME_TICKS = max(1, round(_FRAME_HZ / _ALIEN_ANIM_HZ))


# The emulated-real SID intro (alien_remake.audio.intro), a derived
# artifact under out/ — never a source. Best-effort playback; see close().
_DEFAULT_INTRO_WAV = assets.find("intro.wav")



















class PygameRenderer(
    AudioMixin, TextMixin, EndScreenMixin, FrontEndMixin, PlayMixin,
    DebugOverlayMixin,
):
    """Minimal pygame backend: map view, crew/PCS panel, keyboard order entry."""

    def __init__(
        self,
        scale: int = _SCALE,
        ship: ShipMap | None = None,
        tiles: TileSet | None = None,
        intro_wav: Path | None = _DEFAULT_INTRO_WAV,
        reference_dir: Path = _DEFAULT_REFERENCE_DIR,
        front_end: FrontEnd = FrontEnd.QUICK,
        crt: CrtSettings | None = None,
        startup_report: Any = None,
        sound: str = "game",
        game_audio: str = "original",
    ) -> None:
        # **Mono, before anything else (DISC-255).** `pygame.init()` brings the
        # mixer up too, and SDL will otherwise negotiate the *device's* layout —
        # on a 5.1 output that decodes every mono SID clip to six channels,
        # measured at 10.1 MB resident for 1.7 MB of wav. `pre_init` is the only
        # hook that lands before `pygame.init()` opens it.
        # **The mixer layout is decided here and cannot move later**, so the
        # two audio settings are constructor arguments rather than something
        # set afterwards: `pre_init` is the only hook before `pygame.init()`
        # opens the device. Stereo only when sampled audio is on — it doubles
        # what every clip costs resident (22.8 MB against 45.6 MB, measured),
        # and the SID is a mono chip.
        self._ui_sound = sound == "all"
        self._sampled_game_audio = game_audio == "enhanced"
        if self._sampled_game_audio or self._ui_sound:
            audio.set_channels(2)
        audio.pre_init_mixer()
        pygame.init()
        # R-02: the *window* includes the VIC border; `_surface` is the exact
        # 320x200 (40x25 cell) field everything else draws into.
        #
        # **The draw surface is NATIVE (DISC-242).** It used to be built at
        # `_WIDTH * scale`, and every draw call pre-multiplied its own
        # coordinates by a draw-scale attribute, so the game only looked right
        # at integer multiples typed in at construction. Everything now draws at
        # 320x200 and `_present` scales once, so there is no per-call factor
        # left in the drawing code and no draw scale to keep in step with it.
        # `_window_scale` below sizes the *window* only; change it and the
        # picture is unaffected, which is the whole point.
        self._window_scale = max(1, scale)
        self._windowed_size = (
            (_WIDTH + 2 * _BORDER_X) * self._window_scale,
            (_HEIGHT + 2 * _BORDER_Y) * self._window_scale,
        )
        self._window = pygame.display.set_mode(
            self._windowed_size, pygame.RESIZABLE
        )
        self._fullscreen = False
        self._surface = pygame.Surface((_WIDTH, _HEIGHT))
        # **The CRT layer never touches `_surface`** -- it reads it at present
        # time and writes the window (DISC-264). The processor is built on
        # first use, not here: its pre-generated noise bank is ~2 MB, which a
        # player who leaves the effect off should not pay for.
        self.crt = crt or CrtSettings()
        self._crt: CrtProcessor | None = None
        self._crt_live = False          # this screen may run the CRT
        self._crt_epoch = 0             # last `MenuController.view_epoch` seen
        self._crt_deck: int | None = None       # last deck the map was showing
        self._crt_crew_deck: tuple[str, int] | None = None
        self._crt_at = time.perf_counter()
        self._last_border = _BORDER_COLOUR
        #: Reused scaling destination; see `_blit_field`.
        self._scaled: pygame.Surface | None = None
        #: The phosphor mask, cached against everything that shapes it.
        self._mask: pygame.Surface | None = None
        self._mask_key: tuple[object, ...] | None = None
        #: The whole screen at native resolution -- field *and* VIC border --
        #: which is what the CRT chain runs on. See `_tube_layout`.
        self._canvas: pygame.Surface | None = None
        self._canvas_key: tuple[int, int, int] | None = None
        #: Whether the last frame was a command-accept flash, so a tube refresh
        #: between game frames keeps painting one.
        self._flashing = False
        pygame.display.set_caption("Alien (remake)")
        # **No anti-aliasing anywhere (D-056).** A C64 draws hard pixels; every
        # `render(...)` below passes `antialias=False`, because blended edges
        # produce colours outside the 16-entry palette and read as "modern".
        # D-065: the loader screens' real font, when the chargen ROM is
        # findable. `None` simply means the SysFont path below stays in use.
        self._romfont = romfont.load()
        # Which chargen bank the current screen uses (see `_render_rom_text`).
        self._rom_shifted = False
        # Native sizes: these render onto the native `_surface` and are scaled
        # with everything else at present time.
        self._font = pygame.font.SysFont("monospace", 7)
        self._font_big = pygame.font.SysFont("monospace", 16, bold=True)
        self._ship = ship
        self._tiles = tiles
        self._tile_cache: dict[int, pygame.Surface] = {}
        self._sprite_cache: dict[tuple[int, tuple[int, int, int]], pygame.Surface] = {}
        # R-01: cache for real-charset text renders, keyed by the exact call —
        # rebuilt from raw pixels each time otherwise, unlike SysFont's own
        # internal caching, and this text is drawn every frame.
        self._text_cache: dict[
            tuple[str, tuple[int, int, int], tuple[int, int, int] | None], pygame.Surface
        ] = {}
        self._backdrops: dict[int, DeckBackdrop] = load_deck_backdrops(reference_dir)
        #: Supplied sprites and their washes (D4). See `_supplied_sprite`.
        self._sprite_art_cache: dict[int, pygame.Surface | None] = {}
        self._sprite_wash_cache: dict[
            tuple[object, tuple[int, int, int]], pygame.Surface
        ] = {}
        #: Supplied deck plans (D3). See `_supplied_deck_art`.
        self._deck_art_cache: dict[int, pygame.Surface | None] = {}
        self._reference_dir = reference_dir
        # D-147: the cockpit capture cache — None = not tried, () = missing.
        self._cockpit_capture: tuple[list[int], list[int]] | tuple[()] | None = None
        self._backdrop_cache: dict[int, pygame.Surface] = {}
        self._quit = False
        # The SID intro tune is scoped to the intro phase (title + selection),
        # matching the original's `$60A8` gate — it starts on the title and stops
        # once the game begins (see `_update_intro_music`).
        self._intro_wav = intro_wav
        self._music_playing = False
        # Lazily-rendered SFX (D-088). `None` means "tried and unavailable", so
        # a machine with no audio device pays the render cost at most once.
        self._sfx_cache: dict[str, object | None] = {}
        # Jones's X while a run is in progress; None = not running (D-089).
        self._jones_x: int | None = None
        # D-146: this remake's `$64BA` — a stop has been requested; the cat
        # finishes its current crossing to $F0 before vanishing.
        self._jones_stop = False
        # `$64BB`/`$6562`: an attack sequence is on screen (D-090/D-096).
        self._attacking = False
        # **[C $8CE1] D-139** — the victim whose attack sequence is active, so
        # `render()` can drop the composite the instant the player selects
        # someone else. `$8CE1 CPY $64FB` gates the siren+animation to the
        # SELECTED character; extended here to hold continuously, not just at
        # trigger time, per the user's explicit request.
        self._attacking_crew_id: str | None = None
        # Frames left of the `wait_keypress_flash` border rainbow.
        self._border_flash = 0
        # **D-143** — the frame WELCOME was entered, so its border sweep and
        # sequential text growth animate from a local zero rather than the
        # app's global frame count (which depends on how long the player
        # dwelt on the NOTICE screen first). Reset in `draw()` on any screen
        # that isn't WELCOME so re-entering it (unlikely in practice) replays
        # the build-up rather than resuming mid-way.
        self._welcome_entered_frame: int | None = None
        self._exit_entered_frame: int | None = None      # D-175
        self._legend_entered_frame: int | None = None    # D-176
        self._legend_played = 0                          # D-176
        # **D-145** — the looping heartbeat bed and the composure it was
        # rendered for (`None` = not playing). Re-rendered whenever the
        # selected character's composure changes the rate (`fear_alert
        # $4E16`); see `_update_heartbeat`.
        self._heartbeat_channel: object | None = None
        self._heartbeat_composure: int | None = None
        self._heartbeat_rate: int | None = None
        self._glyph_cache: dict[object, pygame.Surface] = {}
        # Debug-overlay counters (Ctrl+3). Three perf_counter() calls a frame,
        # left live rather than branched around: measured well under a
        # microsecond, and history that only starts when you enable the overlay
        # would show nothing for the first two seconds.
        self._dbg_frames: deque[float] = deque(maxlen=debug_overlay.HISTORY)
        self._dbg_latency: deque[float] = deque(maxlen=debug_overlay.HISTORY)
        self._dbg_last_present: float | None = None
        self._dbg_input_at: float | None = None
        self._dbg_memory: float | None = None
        self._dbg_memory_at = 0.0
        self._dbg_last_tick = 0
        self._dbg_tick_at = 0.0
        self._dbg_tick_rate = 0.0
        self._dbg_overlay_ms = 0.0
        self._dbg_panel: pygame.Surface | None = None
        self._dbg_audio_spec: list[Any] | None = None
        self._dbg_panel_at = 0.0
        # **D-150** — the tracker ping is a continuously-running IRQ pulse
        # (`$4DD7`, divider `$4D03` = 18 ticks), looped while the alarm latch
        # is armed. Not a per-detection one-shot; stacking those is what made
        # the pings machine-gun.
        self._tracker_channel: object | None = None
        # Which deck the CONTROL panel is currently displaying (set from
        # GameState.deck each render).
        self._view_deck = 0
        #: Debug marker overlay (Ctrl+3 on the selection screen). Not the
        #: original — see `_draw_debug_markers`.
        self._debug_markers = False
        #: Filled by `_draw_menu_panel` each frame it draws (P2/P3).
        self._panel_placement: list[int | None] = []
        #: P4-P6: clickable regions the current screen drew.
        self._hot: list[tuple[pygame.Rect, str, int]] = []
        self._hover: tuple[str, int] | None = None
        #: Where startup diagnostics go. A constructor argument rather
        #: than an attribute set afterwards, because `_open_joystick`
        #: runs during construction and its message is one of them (B1).
        self.startup_report: Any = startup_report
        #: The sampled-audio player (S1/S2). Built even when both audio
        #: settings are off, so switching one on mid-run finds it there.
        from ..audio.samples import DIRECTORY as _SOUND_DIR, SamplePlayer
        from .. import assets as _assets
        _dir = next(
            (r / _SOUND_DIR for r in _assets.asset_roots()
             if (r / _SOUND_DIR).is_dir()), None,
        )
        self._samples: Any = SamplePlayer(_dir)
        #: What the last drawn frame showed, so `_emit_for` can tell a
        #: change from a repeat without the input handlers reporting it.
        self._cue_screen: Any = None
        self._cue_row: int | None = None
        self._cue_values: tuple[Any, ...] = ()
        #: Whether the CRT warm-up has already sounded this run (S4).
        self._warmed_up = False
        #: The crew member selected on the last drawn frame, so a swap
        #: can be told from a repeat.
        self._cue_crew: str | None = None
        #: When each interface cue last sounded (S6). Empty until one does, so
        #: the first of every cue is always heard.
        self._cue_last_ms: dict[str, int] = {}
        #: Supplied crew portraits (D1), misses included so a roster with none
        #: is not re-searched every frame.
        self._portrait_cache: dict[str, pygame.Surface | None] = {}
        #: See `_followed_where` / `_deck_override` on the protocol (W1).
        self._followed_where: tuple[str, str] | None = None
        self._deck_override = False
        #: The options model the last `_draw_options` drew, so a click
        #: can address a row absolutely (P4). Recorded rather than
        #: reached for, so it cannot name a screen that is not showing.
        self._options_model: OptionsModel | None = None
        #: Which front end is running — the selection screen's key scheme
        #: and prompt both follow it (DISC-263).
        self._front_end = front_end
        #: Is the mouse live? Off under the ORIGINAL preset — the rule is
        #: `options.pointer_allowed` and the switch is `set_pointer_enabled`,
        #: which the app throws from the settings before the first frame.
        self._pointer_enabled = True
        #: (wall, monotonic) sample; their divergence detects a resume.
        self._clock_ref: tuple[float, float] | None = None
        self._last_state: GameState | None = None
        # Per-frame input buffers, all filled by the single `poll_input` event
        # drain and read back by the app loop: abstract menu events, play-screen
        # orders, and play-screen Special Options (the last two are legacy — the
        # in-game CONTROL panel now drives orders through `_menu` directly).
        self._pending_input: list[InputEvent] = []
        self._pending_orders: list[Order] = []
        self._pending_specials: list[SpecialOption] = []
        #: Skip-turn (2026-09-05), not the original — see `_handle_play_key`.
        self._pending_skip_turn = False
        # The in-game CONTROL-panel menu (created when play begins in `draw`).
        self._sim: Simulation | None = None
        self._menu: MenuController | None = None
        #: **T6.** Carried from `flow` each `draw()` (see that call site) so
        #: `_blit_turn_indicator` can read them without `render(state)`
        #: needing to grow a second parameter. False/0 until the play screen
        #: is first reached.
        self._turns_on = False
        self._turn_count = 0
        self._turn_actor = ""
        self._turn_actions_left: int | None = None
        # Cached, pre-scaled composite of the title's 8-sprite multicolor egg
        # (built once from the game's own sprite data — see _title_egg_surface).
        self._title_egg: pygame.Surface | None = None
        # Frame counter, for the INDICATE LOCATION marker flash (D-022).
        self._frame_count = 0
        # R-18: a real joystick, standing in for the original's **port 2**
        # (`$DC00`) — the only control the game reads during play, per the
        # loader's own "PLUG JOYSTICK INTO PORT TWO" card. Optional: the
        # keyboard scheme stays fully functional when none is attached.
        self._joystick: pygame.joystick.JoystickType | None = None
        self._open_joystick()
        # Edge-detect + auto-repeat state for the analogue/hat axes, so a held
        # direction repeats at a steady rate instead of firing every frame
        # (the original's cursor repeat; rate is `[?]`, tuned for feel).
        self._joy_last: tuple[int, int] = (0, 0)
        self._joy_repeat_in = 0
        self._joy_fire_was_down = False
        self._joy_buttons_was: frozenset[int] = frozenset()

    def set_crt(self, crt: CrtSettings | None) -> None:
        """Swap the CRT presentation — the options screen's `crt` row.

        Two different things are called "the CRT" here and they must not be
        confused: :attr:`crt` is the *settings* (what `crt.preset` returns) and
        :attr:`_crt` is the :class:`CrtProcessor` built from them, sized to the
        canvas. Assigning settings into the processor slot leaves the next
        frame calling `advance()` on a dataclass, which takes the whole program
        down — that is exactly what happened when this was first written.

        So: replace the settings, then drop the processor. `_tube_layout` builds
        a fresh one on the next frame, sized correctly and reading the new
        settings; the CRT is a pure post-process, so there is nothing else to
        unwind.
        """
        self.crt = crt or CrtSettings()
        self._crt = None

    #: Set by the app to the journal's `note`, when developer mode records.
    on_menu_action: Any = None

    def _on_menu_action(self, kind: str, fields: dict[str, Any]) -> None:
        """Forward a panel action to whatever is listening (the journal)."""
        if self.on_menu_action is not None:
            self.on_menu_action(kind, **fields)

    def set_audio(self, sound: str, game_audio: str) -> None:
        """Apply the two audio rows — the options screen drives this.

        Which cues may sound, and where the game's own effects come from, both
        change at once: the sfx cache is dropped so the next effect is fetched
        from whichever source is now chosen.

        **What cannot change here is the mixer's layout.** It is fixed at the
        one `pygame.init()`, so switching sampled audio on mid-run plays stereo
        files through a mono mixer — audible, correct, downmixed. It opens in
        stereo from the next launch, because the setting is saved.
        """
        self._ui_sound = sound == "all"
        sampled = game_audio == "enhanced"
        if sampled != self._sampled_game_audio:
            self._sampled_game_audio = sampled
            self._sfx_cache.clear()

    def set_developer(self, on: bool) -> None:
        """Turn the development overlay on or off — the DEVELOPER option row.

        This used to be two key chords on the selection screen (`0`, and Ctrl+3
        shaped after the ROM's real Ctrl+1/Ctrl+2). Undiscoverable if you did
        not already know, and unreachable on a machine with no keyboard, which
        is the same gap the options screen exists to close. It is a setting now.
        """
        self._debug_markers = on

    def set_pointer_enabled(self, on: bool) -> None:
        """Turn the mouse on or off — **ORIGINAL has none**.

        The rule lives in :func:`~alien_remake.core.options.pointer_allowed`,
        which reads it off the whole profile; this is only the switch it
        throws. The system cursor goes with it: an arrow that moves over the
        picture and does nothing at all is worse than no arrow, because it
        reads as a game that has stopped responding rather than as a machine
        that never had a mouse.

        Guarded, because a dummy-video or headless build may have no cursor to
        hide, and losing the pointer setting must not take down a game that
        otherwise runs.
        """
        self._pointer_enabled = on
        try:
            pygame.mouse.set_visible(on)
        except pygame.error:
            pass

    def set_front_end(self, front_end: FrontEnd) -> None:
        """Follow the flow's front end — the options screen's `front_end` row.

        The renderer keeps its own copy to decide what the selection screen
        prints and whether the Ctrl chord is required, so the two must move
        together or the screen instructs one thing and obeys another.
        """
        self._front_end = front_end

    def _draw_border_noise(self) -> None:
        """The `wait_keypress_flash ($8660)` border, as raster bands.

        The ROM runs `INC $D020` on **every input poll** — thousands of times a
        second — so `$D020` changes many times *within a single displayed
        frame* and the border comes out as a dense stack of horizontal colour
        bands. That is the "colourful rainbow noise" the player describes.
        Stepping one palette entry per rendered frame, as we did, produced a
        slow readable cycle instead: the right colours at the wrong rate.
        Drawn here as bands so a single frame carries the whole palette.
        """
        h = self._window.get_height()
        w = self._window.get_width()
        # **One C64 raster line per band, in window pixels (DISC-261).** This
        # read `max(1, s)` until DISC-242's sweep rewrote every `s` away — and
        # this one was not a coordinate, it was a *thickness*. Left at 1 the
        # bands became one screen pixel each, so at 4x the border showed 800
        # hair-thin stripes instead of 200 raster lines: the same colours at
        # four times the resolution the rest of the picture is drawn at.
        band = max(1, self.field_rect().height // _HEIGHT)
        offset = self._frame_count * 5
        for y in range(0, h, band):
            colour = c64.rgb((y // band + offset) % 16)
            self._window.fill(colour, (0, y, w, band))

    def _present(self, border: tuple[int, int, int] | None = None) -> None:
        """Blit the 40x25 field into the bordered window and flip.

        ``border`` overrides the VIC border colour for screens that don't use
        the play screen's blue (D-064: the loader front-end runs it black).

        **The flash wins over any passed ``border`` (DISC-221).** `_border_flash`
        is only ever armed by `_handle_play_key`, and the play screen started
        passing its own explicit colour once SCUTTLE's flash shipped
        (`_play_border`, DISC-212) — so this used to require `border is None`
        to fire, which the play screen can now never satisfy, and the "command
        accepted" rainbow silently stopped appearing. In the ROM the two never
        overlap anyway: `wait_keypress_flash ($8660)` blocks the main loop
        while it runs, so `mainloop_sub_5a26`'s scuttle toggle isn't ticking at
        the same time — the flash is safe to prioritise unconditionally.
        """
        self._advance_tube()
        if self._border_flash > 0:
            self._border_flash -= 1
            self._flashing = True
            self._paint()
            pygame.display.flip()
            return
        self._flashing = False
        self._last_border = border if border is not None else _BORDER_COLOUR
        self._paint()
        pygame.display.flip()
        self._debug_mark_present()

    def _toggle_fullscreen(self) -> None:
        """Swap between the windowed size and a desktop-resolution fullscreen.

        `set_mode` rather than `pygame.display.toggle_fullscreen()`, which is
        documented as working on only some platforms and silently no-ops on the
        rest. The windowed size is remembered so leaving fullscreen restores it
        instead of snapping back to the default.
        """
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self._window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self._window = pygame.display.set_mode(
                self._windowed_size, pygame.RESIZABLE
            )

    def field_rect(self) -> pygame.Rect:
        """Where the 320x200 field lands in the current window.

        **Integer scaling only (D-056).** A C64 draws hard pixels; a fractional
        factor makes some source pixels two window-pixels wide and their
        neighbours three, which reads as shimmer on a pixel-art field. So the
        factor is the largest whole number that fits, and the field is centred.

        **The fit is measured on the field, not on the field plus its border.**
        Requiring the bordered 384x264 composition to fit costs a whole scale
        step at most real display sizes - at 1366x768 it gave 2x and filled 24%
        of the screen where 3x fits comfortably and fills 55%. The border is
        whatever is left over, so it is thinner than a literal 32*scale at large
        window sizes and exactly 32 at the native one. That is the more faithful
        reading anyway: a VIC border on a real television varies with the set's
        overscan rather than being a fixed number of pixels.

        There is no letterboxing to see, because the leftover is painted in the
        border colour the screen is already using - indistinguishable from the
        border itself. The border is elastic; the field never distorts.

        1280x800 is the pleasing case: 320x200 is exactly 16:10, so the field
        lands at 4x filling the display precisely, with no border at all.
        """
        win_w, win_h = self._window.get_size()
        scale = max(1, min(win_w // _WIDTH, win_h // _HEIGHT))
        width, height = _WIDTH * scale, _HEIGHT * scale
        return pygame.Rect(
            (win_w - width) // 2, (win_h - height) // 2, width, height
        )

    def _blit_field(self) -> None:
        """Scale the native field onto the window. The one scaling step.

        `pygame.transform.scale` onto a plain software surface, deliberately:
        `pygame.SCALED`/`vsync` would move this to an SDL renderer with a GL
        context, which is the thing that can be invalidated when a machine
        resumes from sleep. Software blits survive that. See `todo.md`.
        """
        rect = self.field_rect()
        source = self._surface
        if rect.size == (_WIDTH, _HEIGHT):
            self._window.blit(source, rect.topleft)
            return
        # **Scale into a surface we keep**, rather than letting `transform.scale`
        # allocate a new one every call. Measured at 1920x1080: 2.23 ms a frame
        # allocating, 0.45 ms reusing. That is nearly a quarter of the 8.33 ms
        # the tube has at 120 Hz, spent on nothing but malloc.
        if self._scaled is None or self._scaled.get_size() != rect.size:
            self._scaled = pygame.Surface(rect.size)
        pygame.transform.scale(source, rect.size, self._scaled)
        mask = self._mask_surface(rect.size)
        if mask is not None:
            self._scaled.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self._window.blit(self._scaled, rect.topleft)

    def _mask_surface(self, size: tuple[int, int]) -> pygame.Surface | None:
        """The tube's phosphor triads, sized to the window. `None` if not shown.

        **The only stage that runs after scaling, and the only one that should.**
        A shadow mask is a sheet of perforated steel behind the glass: its pitch
        belongs to the tube, not to the signal, so it stays a fixed number of
        screen pixels while the game's pixels grow with the window. That is also
        the only way it can exist at all — three phosphors need three subpixels,
        and at 1:1 there is no room for them.

        So it is skipped below one triad per game pixel, where it would eat the
        picture instead of drawing it. Built once per window size and applied
        with `BLEND_RGB_MULT`, which SDL does in C: 0.42 ms at 1920x1080.
        """
        settings = self.crt
        if not (self._crt_running() and settings.mask and settings.mask_strength > 0):
            return None
        scale = size[0] // _WIDTH
        if scale < max(3, settings.mask_pitch):
            return None
        key = (size, settings.mask_pitch, round(settings.mask_strength, 3),
               settings.mask_stagger)
        if self._mask_key != key or self._mask is None:
            self._mask = pygame.surfarray.make_surface(
                shadow_mask(size, settings.mask_pitch, settings.mask_strength,
                            settings.mask_stagger)
            )
            self._mask_key = key
        return self._mask

    # --- the CRT layer (DISC-264) -------------------------------------------

    def _crt_running(self) -> bool:
        """Is the tube on *and* on a screen that gets it?"""
        return self.crt.enabled and self._crt_live

    def _paint(self) -> None:
        """Put the frame on the window, through the tube if it is running.

        With the layer off this is what it always was: fill the border, scale
        the field into it. With the layer on, **the border goes through the
        chain too** (owner, DISC-268). A VIC border is part of the picture the
        tube is showing -- scanlines stopping at the edge of the game field is
        the giveaway that this is a filter on a sprite rather than a screen.
        """
        if not self._crt_running():
            if self._flashing:
                self._draw_border_noise()
            else:
                self._window.fill(self._last_border)
            self._blit_field()
            self._blit_debug_panel()
            self._blit_turn_indicator()
            return

        canvas, offset, origin, scale = self._tube_layout()
        if self._flashing:
            self._fill_border_noise(canvas)
        else:
            canvas.fill(self._last_border)
        canvas.blit(self._surface, offset)

        processor = self._crt
        assert processor is not None                 # built by `_tube_layout`
        lit = pygame.surfarray.make_surface(
            processor.process(pygame.surfarray.array3d(canvas))
        )
        size = (canvas.get_width() * scale, canvas.get_height() * scale)
        if self._scaled is None or self._scaled.get_size() != size:
            self._scaled = pygame.Surface(size)
        pygame.transform.scale(lit, size, self._scaled)
        mask = self._mask_surface(size)
        if mask is not None:
            self._scaled.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self._window.blit(self._scaled, origin)

    def _tube_layout(
        self,
    ) -> tuple[pygame.Surface, tuple[int, int], tuple[int, int], int]:
        """The native-resolution whole screen: canvas, field offset, origin, scale.

        The canvas is the window divided by the field's own integer scale, so
        the chain still runs at C64 resolution however large the window is --
        at 1920x1080 it is 384x216 against the field's 320x200, which is the
        whole cost of covering the border.

        The field's offset inside the canvas is rounded *up* from `field_rect`,
        and the canvas is then hung at whatever negative origin makes the two
        agree exactly. Otherwise the picture would shift by up to `scale-1`
        pixels the moment the CRT layer came on, which is precisely the class of
        bug the golden renders exist to catch.
        """
        window = self._window.get_size()
        rect = self.field_rect()
        scale = max(1, rect.width // _WIDTH)
        offset = (-(-rect.x // scale), -(-rect.y // scale))     # ceil
        origin = (rect.x - offset[0] * scale, rect.y - offset[1] * scale)
        size = (
            -(-(window[0] - origin[0]) // scale),
            -(-(window[1] - origin[1]) // scale),
        )
        key = (size[0], size[1], scale)
        if self._canvas_key != key or self._canvas is None:
            self._canvas = pygame.Surface(size)
            self._canvas_key = key
            # The processor is sized to the canvas, so its noise bank and row
            # tables match; a stale one would raise on the first index.
            self._crt = CrtProcessor(size, self.crt)
        elif self._crt is None:
            self._crt = CrtProcessor(size, self.crt)
        return self._canvas, offset, origin, scale

    def _fill_border_noise(self, canvas: pygame.Surface) -> None:
        """`wait_keypress_flash ($8660)`, drawn into the canvas at native pitch.

        One raster line per band, which is one canvas pixel -- the window-space
        arithmetic DISC-261 needed is gone, because the canvas *is* raster
        lines. Stepped by tube time rather than by frame count so the bands keep
        moving through the refreshes between game frames.
        """
        step = int(self._crt.seconds * 300) if self._crt is not None \
            else self._frame_count * 5
        width, height = canvas.get_size()
        for y in range(height):
            canvas.fill(c64.rgb((y + step) % 16), (0, y, width, 1))

    def _advance_tube(self) -> None:
        """Move the tube on by however long really passed.

        Wall-clock, not a frame count, because the tube and the game run at
        different rates on purpose: the signal is drawn at 30 fps and the
        simulation ticks at 7.886 Hz, while the phosphor, the noise and the
        roll keep moving at `TUBE_HZ`. A long stall (a breakpoint, a dragged
        window) is clamped rather than fast-forwarded through.
        """
        now = time.perf_counter()
        elapsed, self._crt_at = now - self._crt_at, now
        if self._crt is not None:
            self._crt.advance(min(elapsed, 0.25))

    def _retube(self) -> None:
        """Redraw the *same* field with the tube one step further on.

        This is what makes the effect run at 120 Hz over a 30 fps game: no
        game state is read, nothing is redrawn into `_surface`, and the frame
        the player is looking at is unchanged underneath. The command-accept
        flash keeps running through these refreshes rather than freezing on
        whichever band it reached when the game frame ended.
        """
        self._advance_tube()
        self._paint()
        pygame.display.flip()

    def idle(self, seconds: float) -> None:
        """Spend the frame's leftover time on the tube instead of sleeping.

        The app loop calls this in place of `time.sleep` at the end of a frame.
        With the layer off it *is* that sleep. With it on, the leftover is
        divided into `TUBE_HZ` slices and the tube is re-presented on each one,
        which is where the owner's "120 fps regardless of the game's frame
        rate" comes from -- the game keeps drawing 30 times a second and the
        display keeps refreshing 120 times a second, as a real set does with a
        slow source.

        The final part-slice is slept through rather than squeezed, so a tube
        frame never delays the game frame that is due.
        """
        if seconds <= 0:
            return
        if not self._crt_running():
            time.sleep(seconds)
            return
        period = 1.0 / TUBE_HZ
        deadline = time.perf_counter() + seconds
        while True:
            left = deadline - time.perf_counter()
            if left <= period:
                if left > 0:
                    time.sleep(left)
                return
            time.sleep(period)
            self._retube()

    def _deck_moved(self) -> bool:
        """Did the displayed deck, or the selected crew member's, change?

        Reads and updates the remembered values in one pass, so a caller that
        only wants to *consume* the change can ignore the answer.
        """
        moved = False
        sim = self._sim
        if sim is not None:
            deck = sim.state.deck
            if self._crt_deck is not None and deck != self._crt_deck:
                moved = True
            self._crt_deck = deck

            here = None
            selected = self._menu.selected_crew if self._menu is not None else None
            if selected is not None:
                crew = sim.state.crew.get(selected)
                room = (
                    sim.ship.rooms.get(crew.room_id)
                    if crew is not None and crew.room_id is not None
                    else None
                )
                if room is not None:
                    here = (selected, room.deck)
            if (
                here is not None
                and self._crt_crew_deck is not None
                and here[0] == self._crt_crew_deck[0]
                and here[1] != self._crt_crew_deck[1]
            ):
                moved = True
            self._crt_crew_deck = here
        return moved

    def _crt_follow_menu(self, screen: Screen) -> None:
        """Fire the view-change glitch the menu asked for, if any.

        The menu bumps a counter (`MenuController.view_epoch`) rather than
        calling in here, so nothing on the sim side of the boundary knows the
        CRT layer exists. The epoch is consumed even when the layer is off or
        the screen is not eligible, or every queued change would go off at once
        the moment the game reaches the play screen.
        """
        menu = self._menu
        if menu is None:
            return
        epoch, strength = menu.view_epoch, menu.view_epoch_strength
        if epoch == self._crt_epoch:
            # **Then watch the state, rather than trusting the wiring.**
            # DISC-268 wired the view changes by name and still missed one,
            # because INDICATE changes deck without looking like a deck change.
            # `state.deck` moving is the thing itself: whatever caused it, the
            # map just jumped a floor and the tube should say so. Crew moving
            # between decks is the other half of what the owner means by
            # "changing floors" (DISC-269), and no view change accompanies it
            # at all -- the map simply stops showing them.
            strength = GENTLE_VIEW_CHANGE
            if not self._deck_moved():
                return
        else:
            self._crt_epoch = epoch
            self._deck_moved()          # consume, so it does not fire twice
        if (self.crt.enabled and self._crt is not None
                and (_CRT_SCREENS is None or screen in _CRT_SCREENS)):
            # **Classify on the midpoint, then use the layer's own constants.**
            # Passing the menu's number straight through coupled two modules by
            # a value that had to match exactly, and when `GLITCH_GENTLE` moved
            # from 0.35 to 0.30 the menu's 0.35 quietly stopped being gentle:
            # every deck change took the scramble path (DISC-268).
            self._crt.glitch(GLITCH_GENTLE if strength <= 0.5 else GLITCH_FULL)






    def _render_c64_text(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
    ) -> pygame.Surface | None:
        """Render ``text`` (unscaled) through the game's own charset.

        R-01: the real replacement for ``pygame.font.SysFont`` — every
        character must be in the confirmed ``_ASCII_TO_SCREEN_CODE`` mapping
        (case-sensitive; unmapped characters, including anything not yet
        cross-validated against a real decoded string, fail the whole call).
        Returns ``None`` when there's no tileset or the text contains any
        unconfirmed character, so the caller can fall back to
        :attr:`_font` — this never silently guesses a glyph.

        **`fg` is the ink; the letter is the glyph's 0-bits (DISC-225).**
        ALIEN's charset is cut-out — confirmed by rendering `out/charset.bin`
        both ways against `docs/reference/narcissus_0400.bin` and comparing:
        the 0-bit reading produces readable "Narcissus : damage 00%", the
        1-bit reading produces the same shapes in the complementary colour.
        `_blit_codes` already draws it this way (`if not on: ... # cut-out
        font: the 0-bits are the ink`); this function drew `fg` at the
        **1-bits** instead — the majority/paper-shaped pixels, not the
        letter. Every existing caller happened to still look right because
        each one passed its (paper, ink) pair in *(fg, bg)* position, which
        cancels the inversion when `bg` is given (`surf.fill(bg)` then `fg`
        overpaints everything except the letter, so the letter ends up
        showing `bg`). The `bg=None` path has no fill to cancel against, so
        a caller relying on it painted a solid ink-coloured block with a
        paper-coloured letter-shaped hole — invisible in the many callers
        that always supply `bg`, and exactly what the opening death notice's
        message showed once it started using this path (DISC-220's `c64_font
        =True` fix moved it here without a compensating `bg`).
        """
        if self._tiles is None:
            return None
        codes: list[int] = []
        for ch in text:
            code = _ASCII_TO_SCREEN_CODE.get(ch)
            if code is None:
                return None
            codes.append(code)
        key = (text, fg, bg)
        cached = self._text_cache.get(key)
        if cached is not None:
            return cached
        w = max(len(codes), 1) * _C64_CELL
        surf = pygame.Surface((w, _C64_CELL))
        if bg is not None:
            surf.fill(bg)
        else:
            colorkey = (255, 0, 255) if fg != (255, 0, 255) else (0, 255, 0)
            surf.set_colorkey(colorkey)
            surf.fill(colorkey)
        for i, code in enumerate(codes):
            glyph = self._tiles.glyph(code)
            for y, line in enumerate(glyph):
                for x, on in enumerate(line):
                    if not on:      # cut-out font: the 0-bits are the ink
                        surf.set_at((i * _C64_CELL + x, y), fg)
        self._text_cache[key] = surf
        return surf

    def _c64_or_sysfont(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
        *,
        big: bool = False,
        c64_font: bool = True,
    ) -> pygame.Surface:
        """Cached front for :meth:`_render_glyph` — see `_GLYPH_CACHE_MAX`."""
        if len(text) > self._GLYPH_CACHE_MAX_LEN:
            return self._render_glyph(text, fg, bg, big=big, c64_font=c64_font)
        key = (text, fg, bg, big, c64_font)
        hit = self._glyph_cache.get(key)
        if hit is None:
            hit = self._render_glyph(text, fg, bg, big=big, c64_font=c64_font)
            if len(self._glyph_cache) >= self._GLYPH_CACHE_MAX:
                self._glyph_cache.clear()
            self._glyph_cache[key] = hit
        return hit

    #: Rendered-glyph cache. A character in a given colour rasterises to the
    #: same pixels every time, and `_blit_cells` asks for one **per character
    #: per frame** — profiled at 511 calls a frame on the instructions screen,
    #: 15,330 rasterisations a second, and the single largest per-frame cost in
    #: the game (DISC-255). Keyed on everything that changes the output.
    #:
    #: Bounded because the key includes the text: `_blit_at` passes whole
    #: strings, and an unbounded dict would grow with every distinct status
    #: line. Short entries are the ones worth keeping — those are the
    #: per-character ones the hot loop asks for.
    _GLYPH_CACHE_MAX = 512
    _GLYPH_CACHE_MAX_LEN = 4

    def _render_glyph(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
        *,
        big: bool = False,
        c64_font: bool = True,
    ) -> pygame.Surface:
        """Real charset when every character is confirmed, else SysFont.

        **`c64_font=False` is not a fallback — it is the faithful choice for
        the front-end screens (D-047).** LOADING / NOTICE / WELCOME /
        INSTRUCTIONS are drawn by the *loader* programs (`MENU`/`MENUA`/
        `MENU1`), which run before `ALIEN.prg` ever points the VIC at its own
        charset (`set_charbase $400A` sets `$D018` -> `$2000`). They therefore
        use the **standard C64 ROM font** — thin light strokes on black, as
        `docs/reference/menu1.png` plainly shows — not ALIEN's custom cut-out
        font. Passing the custom charset there was an R-01 regression.
        """
        rendered = self._render_c64_text(text, fg, bg) if c64_font else None
        if rendered is not None:
            return pygame.transform.scale(
                rendered, (rendered.get_width(), rendered.get_height())
            )
        if not c64_font and not big:
            # D-065: the loader screens' real font is the machine's chargen
            # ROM. Use it when available; SysFont stays the fallback.
            rom = self._render_rom_text(text, fg, bg)
            if rom is not None:
                return rom
        font = self._font_big if big else self._font
        # **DISC-225.** This used to special-case `c64_font and bg is not
        # None` by swapping in `bg` as the ink, on the theory that in-game
        # callers pass `(paper, ink)` as `(fg, bg)` for ALIEN's cut-out font.
        # That theory is what was actually broken: `_render_c64_text` had fg
        # and the glyph's ink bit inverted, and every caller had been
        # hand-tuned to compensate by passing its (paper, ink) pair swapped
        # into (fg, bg). Both are fixed now — `fg` is simply the ink and
        # `bg` the optional fill, same as the `c64_font=False` path below —
        # so this fallback needs no special case at all.
        return font.render(text, False, fg) if bg is None else font.render(text, False, fg, bg)

    def _render_rom_text(
        self,
        text: str,
        fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
    ) -> pygame.Surface | None:
        """Render ``text`` in the real C64 ROM font (D-065), or ``None``.

        Returns ``None`` when the chargen ROM isn't present or any character is
        unmapped, so the caller falls back to SysFont rather than drawing a
        guessed glyph. Each character is a true 8x8 cell, so a string is exactly
        ``8 * len(text)`` unscaled pixels wide — which is what makes the column
        positions transcribed from the live capture line up.

        ``self._rom_shifted`` picks the bank: NOTICE is genuinely mixed-case
        (bank 1) while WELCOME is capitals (bank 0).
        """
        if self._romfont is None:
            return None
        rows = self._romfont.text_rows(text, shifted=self._rom_shifted)
        if rows is None:
            return None
        surf = pygame.Surface((8 * len(rows), 8))
        if bg is None:
            surf.set_colorkey(_ROM_TEXT_CLEAR)
            surf.fill(_ROM_TEXT_CLEAR)
        else:
            surf.fill(bg)
        for i, glyph in enumerate(rows):
            for y, bits in enumerate(glyph):
                for x in range(8):
                    if bits & (0x80 >> x):
                        surf.fill(fg, ((i * 8 + x), y, 1, 1))
        return surf

    def _supplied_sprite(self, index: int) -> pygame.Surface | None:
        """A sprite the player supplied, or ``None``. **D4.**

        Scaled to :data:`~alien_remake.media.SPRITE_SIZE`, which is what a C64
        hardware sprite is. The owner's ruling on D4 is that a supplied file
        changes the picture and nothing else — so the size is taken from the
        machine and never from the file, and every caller goes on drawing it
        exactly where the decoded tables say.

        Cached with the misses: the alien is six sprites a frame and the map
        redraws every frame, so a filesystem search per sprite per frame is not
        a thing that can be allowed to happen.
        """
        if index in self._sprite_art_cache:
            return self._sprite_art_cache[index]
        surface: pygame.Surface | None = None
        path = media.sprite_path(index)
        if path is not None:
            try:
                loaded = pygame.image.load(str(path)).convert_alpha()
                surface = pygame.transform.smoothscale(
                    loaded, media.SPRITE_SIZE
                )
            except Exception:      # pragma: no cover - depends on the file
                surface = None
        self._sprite_art_cache[index] = surface
        return surface

    def _signalled(self, art: pygame.Surface, key: object,
                   colour: tuple[int, int, int]) -> pygame.Surface:
        """Supplied art with a **varying** ROM colour washed over it. **D4.**

        Most sprites are drawn in a fixed ink — Jones is always colour 8, the
        alien always 5 — and there the colour is decoration a supplied picture
        simply replaces.

        Two are not. The selected crew member's marker cycles black-grey-white
        on the ROM's own heartbeat ramp (`$4ED4`, reloaded every 7 ticks), and
        the marker portrait is black in a room and white in a duct (`$6501,Y`).
        Those colours *say something*, and art drawn flat over them would delete
        a signal the original gives the player — which is exactly what the
        owner's "not change the gameplay in any way" rules out. So here the
        colour is kept, as a half-strength wash: the picture survives, and so
        does the beat and the duct.

        Cached per (key, colour); both signals cycle through a handful of
        values, so the set stays small.
        """
        cache_key = (key, colour)
        if cache_key not in self._sprite_wash_cache:
            washed = art.copy()
            wash = pygame.Surface(art.get_size(), pygame.SRCALPHA)
            wash.fill((*colour, media.SIGNAL_WASH))
            washed.blit(wash, (0, 0))
            self._sprite_wash_cache[cache_key] = washed
        return self._sprite_wash_cache[cache_key]

    def _sprite_surface(self, index: int, colour: tuple[int, int, int]) -> pygame.Surface | None:
        """A cached 24x21 Surface for sprite ``index`` drawn in ``colour`` (0=clear).

        A supplied image (**D4**) is answered first and returned as authored —
        there is no single ink to re-colour it to. `_blit_sprite`'s `varies`
        flag is how the two callers whose colour carries information ask for it
        back; see :meth:`_signalled`.
        """
        supplied = self._supplied_sprite(index)
        if supplied is not None:
            return supplied
        if self._tiles is None or index >= len(self._tiles.sprites):
            return None
        key = (index, colour)
        if key not in self._sprite_cache:
            bmp = self._tiles.sprites[index]
            # A magenta sentinel is the transparent colour, so ``colour`` may
            # itself be black (a black face on the green selection screen).
            clear = (255, 0, 255)
            surf = pygame.Surface((len(bmp[0]), len(bmp)))
            surf.set_colorkey(clear)
            surf.fill(clear)
            for r, line in enumerate(bmp):
                for c, on in enumerate(line):
                    if on:
                        surf.set_at((c, r), colour)
            self._sprite_cache[key] = surf
        return self._sprite_cache[key]

    def _portrait_surface(self, crew_id: str) -> pygame.Surface | None:
        """A supplied portrait for one crew member, or ``None``. **D1.**

        Where the file lives is :func:`alien_remake.media.portrait_path`, so
        the dictionary that *documents* the folder is the same code that reads
        it and the two cannot describe different places.

        Scaled to :data:`~alien_remake.media.PORTRAIT_SIZE`, because the
        positions it is drawn at are decoded (`_PORTRAIT_X`, 40px apart) and a
        native-size image would simply cover its neighbours.

        Cached including the misses, so a full roster with no portraits costs
        seven `find` calls once rather than seven every frame. That does mean a
        portrait added while the game is running is not picked up until the
        next launch, which is the right trade for a file nobody edits mid-game.

        Best-effort: a corrupt or unreadable image falls back to the ROM's own
        sprite rather than taking the screen down. Someone's PNG is not a
        reason for the game to stop.
        """
        if crew_id in self._portrait_cache:
            return self._portrait_cache[crew_id]
        surface: pygame.Surface | None = None
        path = media.portrait_path(crew_id)
        if path is not None:
            try:
                loaded = pygame.image.load(str(path)).convert_alpha()
                surface = pygame.transform.smoothscale(
                    loaded, media.PORTRAIT_SIZE
                )
            except Exception:      # pragma: no cover - depends on the file
                surface = None
        self._portrait_cache[crew_id] = surface
        return surface

    def _blit_portrait(self, crew_id: str, index: int, cx: int, cy: int,
                       colour: tuple[int, int, int], *,
                       varies: bool = False) -> None:
        """One crew portrait: the player's own if they supplied it. **D1.**

        Falls through to :meth:`_blit_sprite` otherwise, which is the decoded
        path and stays the default — so an install with no `portraits` folder
        draws exactly what it drew before.

        **`colour` is ignored for a supplied image, and that is deliberate.**
        The ROM's portraits are one-colour sprites recoloured per screen
        (`$5EEF` zeroes `$D027-$D02E`, so the selection screen draws them black
        on green). Recolouring somebody's artwork to a single ink would throw
        away the thing they supplied. Substituting the file is the choice to
        leave that behind.
        """
        surface = self._portrait_surface(crew_id)
        if surface is None:
            self._blit_sprite(index, cx, cy, colour, varies=varies)
            return
        # **D4 corrects a gap D1 left.** On the play screen this sprite is
        # black in a room and white in a duct (`$6501,Y`) — a decoded signal,
        # not decoration — and a supplied portrait drawn flat deleted it.
        if varies:
            surface = self._signalled(surface, crew_id, colour)
        w, h = surface.get_width(), surface.get_height()
        self._surface.blit(surface, (cx - w // 2, cy - h // 2))

    def _blit_sprite(self, index: int, cx: int, cy: int,
                     colour: tuple[int, int, int], *,
                     varies: bool = False) -> None:
        """Blit sprite ``index`` centred on native pixel ``(cx, cy)``.

        The `scale` parameter went with DISC-242: sprites are drawn at native
        size like everything else, and `_present` scales the whole field.

        `varies` says that ``colour`` is *information* rather than ink — the
        heartbeat ramp, so far. It only affects a supplied image, which would
        otherwise be drawn flat and lose the beat. Declared by the caller
        because only the caller knows whether the colour it is passing changes.
        """
        surf = self._sprite_surface(index, colour)
        if surf is None:
            return
        if varies and self._supplied_sprite(index) is not None:
            surf = self._signalled(surf, index, colour)
        w, h = surf.get_width(), surf.get_height()
        self._surface.blit(surf, (cx - w // 2, cy - h // 2))



    # --- input --------------------------------------------------------------
    def poll_input(self, screen: Screen) -> list[InputEvent]:
        """Drain this frame's events exactly once and classify them by screen.

        On the menu screens (title/selection/opening/end) keys become abstract
        :class:`InputEvent`s for the :class:`GameFlow`. On the play screen they
        run the in-game control scheme (crew select, target cursor, order/
        Special-Option verbs — see :meth:`_handle_play_key`), filling the order/
        special buffers that :meth:`poll_orders` / :meth:`poll_special_options`
        return. Escape or the window close always requests quit.
        """
        self._pending_input = []
        self._pending_orders = []
        self._pending_specials = []
        # Once per frame: has the machine just come back from sleep? If so the
        # audio device is probably gone and the mixer needs rebuilding, or the
        # game plays on in silence (see `check_for_resume`).
        self._debug_mark_input()
        self.check_for_resume()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit = True
                self._pending_input.append(InputEvent.QUIT)
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                # P3-10: hot-plug, so a stick connected after launch works.
                self._open_joystick()
            elif event.type == pygame.VIDEORESIZE and not self._fullscreen:
                # Re-`set_mode` rather than trusting the display surface to
                # follow: `field_rect` reads the window size every frame, so the
                # new geometry is picked up on the next `_present` with no other
                # state to update.
                self._windowed_size = (event.w, event.h)
                self._window = pygame.display.set_mode(
                    self._windowed_size, pygame.RESIZABLE
                )
            elif not self._pointer_enabled and event.type in (
                pygame.MOUSEWHEEL, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
            ):
                # **ORIGINAL has no pointer** (`options.pointer_allowed`). One
                # gate at the event, not three inside the handlers: dropping
                # the events means no hover state either, so nothing downstream
                # can be left half-lit by a mouse that is supposed to be gone.
                continue
            elif event.type == pygame.MOUSEWHEEL:
                self._pointer_wheel(event.y, screen)
            elif event.type == pygame.MOUSEMOTION:
                self._pointer_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # P2/P3. The ROM has one fire control, and the left button is
                # it.
                self._pointer_down(event.pos, screen)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # **Not the original** (owner's request). Right-click is not a
                # new capability, just a second way to reach one that already
                # exists: the panel's own "back" row (labelled "quit" in the
                # decoded ROM, `[C $A715]` - shown as "back" since 2026-09-05,
                # see `core/menu.py`'s own comment), already reachable from
                # the keyboard via Escape (DISC-262) - back out one level, from
                # a crew member's order list to the CONTROL list, so a mouse
                # player can deselect and pick someone else without switching
                # to the keyboard. Scoped to the play screen only, the same as
                # Escape's own panel-backing-out behaviour; it does nothing on
                # the front-end screens, where a right-click has no ROM action
                # to stand in for.
                if screen is Screen.PLAYING and self._menu is not None:
                    self._menu.back()
            elif event.type == pygame.KEYDOWN and _is_fullscreen_key(event):
                self._toggle_fullscreen()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # **Escape is the panel's own `back` row (DISC-262).**
                    # During play it does exactly what choosing "back" in the
                    # PCS menu does — backs out one level, from a crew member's
                    # order list to the CONTROL list — so it is an undo for
                    # "I opened the wrong menu", not an exit.
                    #
                    # Off the play screen there is no panel to back out of, so
                    # it abandons to the front end instead (DISC-261). It never
                    # closes the program: the original's only exit is `Q QUIT`,
                    # and the quick front end does not even show that screen.
                    if screen is Screen.PLAYING and self._menu is not None:
                        self._menu.back()
                    else:
                        self._pending_input.append(InputEvent.ABANDON)
                elif screen is Screen.PLAYING:
                    self._handle_play_key(event.key)
                else:
                    menu_event = _MENU_KEYS.get(event.key)
                    # [C R-32/D-018]: the real GAME_SELECTION loop ($5F36)
                    # polls for the Ctrl+1/Ctrl+2 CHORD specifically, not a bare
                    # "1"/"2" (unlike WELCOME's genuinely-bare "1 ALIEN"/"Q QUIT",
                    # which must stay unmodified). Found by FV-1c1 as an
                    # unenforced gap; fixed here.
                    # **[C R-32/D-018] The chord is CLASSIC-only (DISC-263).**
                    # `$5F36` polls for Ctrl+1/Ctrl+2 specifically, and FV-1c1
                    # found that unenforced. The quick front end takes bare 1
                    # and 2 instead and says so on screen, so requiring the
                    # chord there would print one instruction and obey another.
                    if (
                        screen is Screen.GAME_SELECTION
                        and menu_event in (InputEvent.SELECT_FULL, InputEvent.SELECT_SHORT)
                        and self._front_end is FrontEnd.CLASSIC
                        and not (event.mod & pygame.KMOD_CTRL)
                    ):
                        menu_event = None
                    if menu_event is not None:
                        # **P3-8.** "Q QUIT" is a real option on the WELCOME
                        # screen ($5F59's menu text), but the event was only
                        # forwarded to the flow — which ignores it there — so
                        # nothing happened. A menu QUIT ends the program, the
                        # same as Escape or closing the window.
                        if menu_event is InputEvent.QUIT:
                            self._quit = True
                        self._pending_input.append(menu_event)
        self._poll_joystick(screen)
        return self._pending_input

    #: Frames a held joystick direction waits before repeating, then between
    #: repeats. **[C $71B0/$7453] PV-31 closed 2026-08-07 (D-165) — DERIVED,
    #: not tuned.** `read_input ($71B0)` reads `$C5` and `$DC00` once per
    #: main-loop pass and drops a direction into `$71AF`; `sub_7453` then acts
    #: on it and calls `delay_routine`. There is **no repeat counter, no
    #: debounce and no acceleration anywhere** — the cursor simply steps once
    #: per pass while a direction is held, so the busy-wait *is* the repeat
    #: rate. Two consequences: the cadence is `MAIN_LOOP_HZ`, and there is
    #: **no initial delay** — the old 12-frame (0.4 s) pause before repeating
    #: was an invention, and is why the remake's cursor felt sticky compared
    #: with the original's immediate run.
    _JOY_REPEAT_RATE = max(1, round(_FRAME_HZ / constants.MAIN_LOOP_HZ))
    _JOY_REPEAT_DELAY = _JOY_REPEAT_RATE
    #: Beyond this an analogue stick counts as pushed (ignored for d-pad hats).
    _JOY_DEADZONE = 0.5

    def _report(self, text: str, *, warning: bool = False) -> None:
        """Add a line to the startup report, or print it if none is listening.

        **B1.** The renderer is constructed before anything can draw, so it
        cannot show its own diagnostics; it hands them to the report and the
        boot screen shows them later. Falling back to `print` keeps the message
        for a test or a caller that never set one, rather than losing it.
        """
        if self.startup_report is not None:
            if warning:
                self.startup_report.warn(text)
            else:
                self.startup_report.info(text)
        else:
            print(f"alien-remake: {text}", file=sys.stderr)

    def _open_joystick(self) -> None:
        """Attach the first joystick, and **say so**.

        Detection used to run once at construction and in silence, so a stick
        plugged in later was never seen and a player had no way to tell whether
        the game had found one — the whole basis of "the arrow keys respond,
        the joystick does not". Now re-runnable (see `JOYDEVICEADDED` in
        `poll_input`) and it prints what it found.
        """
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self._joystick = pygame.joystick.Joystick(0)
                self._joystick.init()
                self._report(
                    f"joystick attached ({self._joystick.get_name()}) "
                    f"- port 2, as the loader asks"
                )
            else:
                self._joystick = None
                self._report(
                    "no joystick; using the keyboard (arrows/WS move, "
                    "Space or Return fires)"
                )
        except pygame.error as exc:  # pragma: no cover - needs real hardware
            self._joystick = None
            self._report(f"joystick unavailable ({exc})", warning=True)

    def _joy_direction(self) -> tuple[int, int]:
        """Current stick/hat direction as (dx, dy), each -1/0/+1."""
        joy = self._joystick
        if joy is None:
            return (0, 0)
        dx = dy = 0
        if joy.get_numhats() > 0:
            hx, hy = joy.get_hat(0)
            # pygame hats are y-up; screen rows are y-down.
            dx, dy = int(hx), -int(hy)
        if dx == 0 and dy == 0 and joy.get_numaxes() >= 2:
            ax, ay = joy.get_axis(0), joy.get_axis(1)
            dx = int(ax > self._JOY_DEADZONE) - int(ax < -self._JOY_DEADZONE)
            dy = int(ay > self._JOY_DEADZONE) - int(ay < -self._JOY_DEADZONE)
        return (dx, dy)

    def _poll_joystick(self, screen: Screen) -> None:
        """Translate the joystick into the same events the keyboard produces.

        R-18: the original is joystick-only during play (port 2, `$DC00`) —
        the loader even prints "PLUG JOYSTICK INTO PORT TWO". A direction
        fires once on push, then auto-repeats while held; the button maps to
        FIRE on menus and to the CONTROL panel's fire on the play screen.
        """
        if self._joystick is None:
            return
        dx, dy = self._joy_direction()
        # Edge-trigger, then auto-repeat while a direction is held.
        if (dx, dy) != self._joy_last:
            self._joy_last = (dx, dy)
            self._joy_repeat_in = self._JOY_REPEAT_DELAY
            emit = dx != 0 or dy != 0
        elif dx or dy:
            self._joy_repeat_in -= 1
            emit = self._joy_repeat_in <= 0
            if emit:
                self._joy_repeat_in = self._JOY_REPEAT_RATE
        else:
            emit = False
        if emit:
            if screen is Screen.PLAYING:
                if dy < 0:
                    self._handle_play_key(pygame.K_UP)
                elif dy > 0:
                    self._handle_play_key(pygame.K_DOWN)
                elif dx < 0:
                    self._handle_play_key(pygame.K_LEFT)
            else:
                for delta, ev in (
                    (dy < 0, InputEvent.UP), (dy > 0, InputEvent.DOWN),
                    (dx < 0, InputEvent.LEFT), (dx > 0, InputEvent.RIGHT),
                ):
                    if delta:
                        self._pending_input.append(ev)
        # The single button: fire on the press edge only.
        pressed = frozenset(
            b for b in range(self._joystick.get_numbuttons())
            if self._joystick.get_button(b)
        )
        new_presses = pressed - self._joy_buttons_was
        self._joy_buttons_was = pressed
        fire_down = bool(pressed)

        # **Pad-only bindings — a keymap, not a mechanic (DISC-248).**
        # Two of the game's inputs have no pad equivalent: Escape, and the
        # selection screen's Ctrl+1/Ctrl+2 chord. Without them a pad cannot
        # start a game at all.
        #
        # These are bound to *dedicated* buttons rather than to fire, and that
        # distinction is the whole point. FV-1c1/1c2 removed an invented
        # up/down cursor and fire-select from the selection screen, because the
        # ROM has neither — `$5F36` polls for the chord for the option you
        # want. Making fire pick the full game would put that invention
        # straight back. Binding "1" and "2" to two buttons keeps the ROM's
        # model exactly and changes only which physical control produces them.
        if _JOY_BTN_QUIT in new_presses:
            # Same rule as Escape (DISC-261): back out, and only quit from the
            # top menu.
            if screen is Screen.WELCOME:
                self._quit = True
                self._pending_input.append(InputEvent.QUIT)
            else:
                self._pending_input.append(InputEvent.ABANDON)
            return
        if screen is Screen.GAME_SELECTION:
            for button, chord in (
                (_JOY_BTN_SELECT_FULL, InputEvent.SELECT_FULL),
                (_JOY_BTN_SELECT_SHORT, InputEvent.SELECT_SHORT),
            ):
                if button in new_presses:
                    self._pending_input.append(chord)
            # Fire does nothing on this screen in the ROM, so it does nothing
            # here either.
            self._joy_fire_was_down = fire_down
            return

        if fire_down and not self._joy_fire_was_down:
            if screen is Screen.PLAYING:
                self._handle_play_key(pygame.K_SPACE)
            else:
                self._pending_input.append(InputEvent.FIRE)
        self._joy_fire_was_down = fire_down

    # --- pointer input (P2-P7) ----------------------------------------------

    #: How far outside its drawn box a region still counts as hit, in field
    #: pixels. **P6.** A row is 8 field pixels tall; at the 3-4x window scale a
    #: Steam Deck uses that is 24-32 real pixels — fine for a mouse, marginal
    #: for a fingertip.
    #:
    #: **Applied as "nearest within this distance", not as a bigger box.** The
    #: first attempt inflated every region and a test caught it immediately:
    #: the rows are *adjacent*, so any outward growth at all makes two of them
    #: claim the same pixels, and which one wins is whichever was recorded
    #: first. Falling back to the nearest region instead is unambiguous by
    #: construction — an exact hit always wins, and a miss resolves to one
    #: answer rather than to an ordering accident. It also still helps where
    #: the help is wanted: the outer edges of a list, and regions with no
    #: neighbour.
    POINTER_SLOP = 3

    def _hot_clear(self) -> None:
        """Start a frame's region list. Called by each screen that records."""
        self._hot = []

    def _hot_add(self, rect: pygame.Rect, kind: str, index: int = 0) -> None:
        """Record one clickable region, in field pixels."""
        self._hot.append((rect, kind, index))

    def _hot_cells(self, col: int, row: int, width: int, kind: str,
                   index: int = 0) -> None:
        """Record a region given as character cells — the common case."""
        self._hot_add(
            pygame.Rect(col * _C64_CELL, row * _C64_CELL,
                        width * _C64_CELL, _C64_CELL),
            kind, index,
        )

    def _hot_at(self, pos: tuple[int, int]) -> tuple[str, int] | None:
        """Which region a *window* position is over.

        An exact hit wins outright. Otherwise the nearest region within
        :data:`POINTER_SLOP` answers, so a fingertip that lands just off a row
        still does what it obviously meant — see POINTER_SLOP for why this is
        a distance and not a bigger box.
        """
        canvas = self._canvas_pos(pos)
        if canvas is None:
            return None
        nearest: tuple[float, str, int] | None = None
        for rect, kind, index in self._hot:
            if rect.collidepoint(canvas):
                return (kind, index)
            dx = max(rect.left - canvas[0], 0, canvas[0] - (rect.right - 1))
            dy = max(rect.top - canvas[1], 0, canvas[1] - (rect.bottom - 1))
            distance = (dx * dx + dy * dy) ** 0.5
            if distance <= self.POINTER_SLOP and (
                nearest is None or distance < nearest[0]
            ):
                nearest = (distance, kind, index)
        return (nearest[1], nearest[2]) if nearest else None



    def _canvas_pos(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        """Window pixel -> 320x200 field pixel, or ``None`` if outside it.

        `field_rect()` already knows where the field lands and at what integer
        scale (D-056), so this is its inverse and there is no second copy of
        the layout to keep in step.
        """
        rect = self.field_rect()
        if not rect.collidepoint(pos):
            return None
        scale = max(1, rect.width // _WIDTH)
        return ((pos[0] - rect.x) // scale, (pos[1] - rect.y) // scale)

    def panel_entry_at(self, pos: tuple[int, int]) -> int | None:
        """Which `MenuController.entries()` index a window position is over.

        ``None`` when the position is outside the field, left of the panel, or
        on a row no entry was drawn on. Inverts `_panel_placement`, which is
        what the last frame actually drew — see its declaration for why this
        does not recompute the layout.
        """
        canvas = self._canvas_pos(pos)
        if canvas is None:
            return None
        col, row = canvas[0] // _C64_CELL, canvas[1] // _C64_CELL
        if col < _PANEL_COL:
            return None
        for index, placed_row in enumerate(self._panel_placement):
            if placed_row == row:
                return index
        return None

    def _pointer_down(self, pos: tuple[int, int], screen: Screen) -> None:
        """One pointer press. **The single path for mouse and, later, touch.**

        `MOUSEBUTTONDOWN` feeds this today. A touch screen feeds the same
        method: pygame delivers `FINGERDOWN` with **normalised 0..1**
        coordinates, so the only difference is multiplying by the window size
        before calling in. Keeping that difference to one multiplication is the
        whole reason this is a method rather than inline event handling.
        """
        if screen is not Screen.PLAYING:
            self._pointer_front_end(pos, screen)
            return
        if self._menu is None:
            return
        index = self.panel_entry_at(pos)
        if index is None:
            # **M3 — a room on the map.** The region carries the panel's own
            # entry index, so this fires the same `MenuEntry` the menu would
            # have: one path to a MOVE TO, and the PCS gate, the countdown and
            # the journal line all behave identically. **M5:** with nobody
            # selected there are no destinations, so no regions, so nothing
            # here can happen.
            hit = self._hot_at(pos)
            if hit is not None and hit[0] == "room":
                index = hit[1]
            else:
                return
        if not self._menu.select_index(index):
            return
        # A click is "put the cursor there and fire", which is what the
        # keyboard does in two steps — so it goes through the same fire path,
        # border flash and CRT burst included, rather than a second one that
        # could drift.
        self._fire_menu()

    def _pointer_front_end(self, pos: tuple[int, int], screen: Screen) -> None:
        """A click on one of the front-end screens. **P4.**

        Each action is expressed as the :class:`InputEvent` the keyboard would
        have produced, and queued the same way, so the pointer adds a *way in*
        and never a second set of rules. The options screen is the exception
        that proves it: its rows are addressed absolutely, which no key can do,
        so the row is set first and the existing LEFT/RIGHT events do the rest.
        """
        hit = self._hot_at(pos)
        if hit is None:
            return
        kind, index = hit
        if kind == "selection":
            # CR5: a 5th row exists only off ORIGINAL, so this list is built to
            # match what `_draw_selection` actually drew rather than a fixed
            # tuple - a click past the drawn rows must not IndexError, and a
            # fixed four-tuple would once CREDITS became the fifth.
            events = [
                InputEvent.SELECT_FULL, InputEvent.SELECT_SHORT,
                InputEvent.SELECT_INSTRUCTIONS, InputEvent.SELECT_OPTIONS,
            ]
            from ..core.options import is_original
            if self._options_model is not None and not is_original(
                self._options_model.as_dict()
            ):
                events.append(InputEvent.SELECT_CREDITS)
            if index < len(events):
                self._pending_input.append(events[index])
        elif kind in ("option_row", "option_less", "option_more"):
            if self._options_model is not None:
                self._options_model.row = index
            if kind == "option_less":
                self._pending_input.append(InputEvent.LEFT)
            elif kind == "option_more":
                self._pending_input.append(InputEvent.RIGHT)
        elif kind == "options_done":
            self._pending_input.append(InputEvent.FIRE)
        elif kind == "manual_next":
            self._pending_input.append(InputEvent.FIRE)
        elif kind == "manual_back":
            self._pending_input.append(InputEvent.LEFT)
        elif kind == "edition":
            # The first-run answers are "1" and "2" to the keyboard, so the
            # click sends exactly those. Nothing about the choice is addressed
            # absolutely, which is why this needs no model of its own the way
            # the options rows do.
            self._pending_input.append(
                (InputEvent.SELECT_FULL, InputEvent.SELECT_SHORT)[index]
            )
        elif kind == "boot_done":
            self._pending_input.append(InputEvent.FIRE)
        elif kind == "manual_done":
            self._pending_input.append(InputEvent.ABANDON)

    def _emit_for(self, flow: GameFlow) -> None:
        """Sound the interface cues this frame earned. **S3.**

        Driven from the draw, by comparing against what was last drawn, rather
        than from the input handler: the keyboard, the pointer and the joystick
        all move the same cursor, and hanging cues off each of them would be
        three places to keep in step and three chances to double up.

        A screen change and a row change in the same frame sound once, as the
        screen: arriving somewhere is the bigger event, and two blips together
        read as a fault.
        """
        from ..audio import samples

        screen = flow.screen
        # **S4 — the tube warming up, once, at the first frame drawn.**
        # Gated on the CRT actually being on: a warm-up sound over a picture
        # that is not a tube is a sound for a thing that is not happening.
        if not self._warmed_up:
            self._warmed_up = True
            if self.crt.enabled:
                self.emit(samples.CRT_WARMUP)
        # **The character swap.** Picking a different crew member is the one
        # in-game selection a player makes constantly, and `MENU_SELECT` was in
        # the cue vocabulary with nothing raising it — so a file dropped in
        # under that name would have been silent. Compared against the last
        # frame like every other cue, so the keyboard, the pointer and the
        # joystick all reach it by the same route.
        crew = self._menu.selected_crew if self._menu is not None else None
        if crew != self._cue_crew:
            self._cue_crew = crew
            if crew is not None:
                self.emit(samples.MENU_SELECT)
        row = flow.options.row if screen is Screen.OPTIONS else None
        values = (
            tuple(flow.options.values.items())
            if screen is Screen.OPTIONS else ()
        )
        if screen is not self._cue_screen:
            self._cue_screen, self._cue_row, self._cue_values = (
                screen, row, values,
            )
            self.emit(samples.SCREEN_ENTER)
            return
        if values != self._cue_values:
            self.emit(samples.MENU_CHANGE)
        elif row != self._cue_row:
            self.emit(samples.MENU_MOVE)
        self._cue_row, self._cue_values = row, values

    def _pointer_wheel(self, amount: int, screen: Screen) -> None:
        """The wheel. **W1/W5.**

        On the play screen it changes floor, which is the point: the map shows
        one deck, so a destination up or down a ladder could be ordered from
        the panel but never clicked. It drives `Simulation.select_deck` — the
        same call the panel's own three deck rows make — rather than a view
        variable of its own, because `_view_deck` is overwritten from
        `GameState.deck` on every draw and setting it directly does nothing.
        So the map, the marker, the pointer and the panel all follow one piece
        of state (**W6**).

        **Up means up.** Deck 0 is the upper deck, so scrolling up *lowers* the
        number. Clamped rather than wrapped: a wheel that jumps from the top of
        the ship to the bottom reads as a glitch.

        Elsewhere it does what the arrow keys do on that screen (**W5**) — a
        wheel that works on one screen and is dead on the next feels broken.
        """
        if amount == 0:
            return
        if screen is Screen.PLAYING:
            if self._sim is None:
                return
            decks = sorted(self._sim.ship.decks())
            if not decks:
                return
            here = self._sim.state.deck
            index = decks.index(here) if here in decks else 0
            target = decks[max(0, min(len(decks) - 1, index - amount))]
            if target != here:
                self._sim.select_deck(target)
                # A deliberate change: hold it until the selected character
                # actually moves, rather than snapping straight back.
                self._deck_override = True
            return
        step = InputEvent.UP if amount > 0 else InputEvent.DOWN
        if screen in (Screen.MANUAL, Screen.CREDITS):
            # The manual pages rather than scrolling, and its own keys are
            # left/right, so the wheel turns pages in the reading direction.
            # CREDITS shares this exactly - it is the same paging mechanism.
            step = InputEvent.LEFT if amount > 0 else InputEvent.FIRE
        self._pending_input.append(step)

    def _pointer_motion(self, pos: tuple[int, int]) -> None:
        """Track what the pointer is over, for P5's hover highlight.

        Presentation only: the next frame draws the hovered row differently and
        nothing else changes, so a mouse resting on a row can never alter the
        game — which matters most on the options screen, where the rows *are*
        the settings.
        """
        self._hover = self._hot_at(pos)
        # **M4.** Tell the panel which room is under the pointer so the ROM's
        # own location animation plays over it. Cleared when the pointer is
        # elsewhere, so the box does not linger on a room the mouse has left.
        if self._menu is not None:
            room = None
            if self._hover is not None and self._hover[0] == "room":
                entries = self._menu.entries()
                index = self._hover[1]
                if 0 <= index < len(entries):
                    order = entries[index].order
                    room = order.target if order is not None else None
                    # **W2 — hovering aims.** The owner's call, reversing M4's
                    # "hover is purely visual". The consequence is the point:
                    # after hovering a room the space bar fires *that* room,
                    # because that is what aiming means. Silent by
                    # construction — the cue bus compares the *selected crew*
                    # and the screen, neither of which a hover touches, so no
                    # blip and no panel churn as the pointer crosses rooms.
                    self._menu.select_index(index)
            self._menu.hovered_room_id = room

    def _fire_menu(self) -> None:
        """Fire the highlighted panel row (shared by space, the pad and a click)."""
        if self._menu is None:
            return
        self._menu.fire()
        # [C $8660] P2-12: the border rainbows while the game waits for
        # the player to acknowledge — the "command accepted" feedback.
        self._border_flash = _BORDER_FLASH_FRAMES
        # And the picture goes with it (owner, DISC-268): on a real set the
        # interference that rainbows the border is in the frame too.
        if self._crt is not None and self._crt_running():
            self._crt.burst()

    #: **Not the original.** Developer-mode keys for playtesting, live only
    #: while DEVELOPER is on. Function keys deliberately: the panel uses the
    #: arrows, space, return, escape and the number row, and a testing control
    #: that shadowed one of those would be a bug waiting to be reported as a
    #: gameplay bug.
    DEV_KEYS: dict[int, str] = {
        pygame.K_F1: "fear -1 (calmer)",
        pygame.K_F2: "fear +1 (more afraid)",
        pygame.K_F3: "alien: act / still",
        pygame.K_F4: "jones: act / still",
        pygame.K_F5: "reveal the android",
    }

    def _dev_key(self, key: int) -> bool:
        """One developer-mode testing key. Returns whether it consumed the key.

        Everything it does is a state change and every state change is written
        to the session log, because a run somebody reached into is a run whose
        log has to say so — otherwise it is evidence about a game that never
        happened.
        """
        if key not in self.DEV_KEYS or self._sim is None:
            return False
        from ..core import devtools

        state = self._sim.state
        note: str | None = None
        if key == pygame.K_F1:
            note = devtools.adjust_fear(state, self._menu.selected_crew
                                        if self._menu else None, -1)
        elif key == pygame.K_F2:
            note = devtools.adjust_fear(state, self._menu.selected_crew
                                        if self._menu else None, +1)
        elif key == pygame.K_F3:
            note = self._sim.dev.cycle_alien()
        elif key == pygame.K_F4:
            note = self._sim.dev.cycle_jones()
        elif key == pygame.K_F5:
            note = devtools.reveal_android(state)
        if note and self.on_menu_action is not None:
            self.on_menu_action("dev", change=note)
        return True

    def _handle_play_key(self, key: int) -> None:
        """Drive the in-game CONTROL panel: up/down move the cursor, space/return
        fire, left backs out of a crew's order menu to the CONTROL list.

        Space and the joystick button both fire (the user confirmed space fired
        in the original); orders/Special Options are issued straight to the sim
        by the :class:`MenuController`, not buffered.
        """
        if self._menu is None:
            return
        # **Developer-mode testing keys.** Function keys, so they cannot
        # collide with anything the panel uses, and dead unless developer mode
        # is on — see `_dev_key`.
        if self._debug_markers and self._dev_key(key):
            return
        if key in (pygame.K_UP, pygame.K_w):
            self._menu.move(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._menu.move(1)
        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            self._fire_menu()
        elif key == pygame.K_LEFT:
            self._menu.back()
        elif key == pygame.K_k and self._turns_on:
            # **Skip turn (2026-09-05), not the original.** No other letter
            # key is bound on this screen (every other verb is a menu row,
            # navigated by cursor + fire), so 'K' is free — mnemonic "sKip",
            # and read back every frame by `poll_skip_turn`. Gated on
            # `_turns_on` (last set by `draw()`, so up to one frame stale —
            # the same lag `_crt_live` already tolerates) purely so a stray
            # K in real-time mode does nothing rather than silently arming a
            # flag nothing ever drains.
            self._pending_skip_turn = True

    def poll_skip_turn(self) -> bool:
        """Whether skipping was requested since the last call — the `K` key
        (`_handle_play_key`) or the CONTROL panel's own "Skip turn" row
        (`MenuController.skip_turn_requested`), two ways to ask for the same
        thing. **Not the original.**"""
        skip = self._pending_skip_turn
        self._pending_skip_turn = False
        if self._menu is not None and self._menu.skip_turn_requested:
            skip = True
            self._menu.skip_turn_requested = False
        return skip

    def select_crew(self, crew_id: str) -> None:
        """**Not the original.** Initiative's own hook (`app.run_app`): jump
        the CONTROL panel to ``crew_id``'s order menu the way picking their
        row would, so a turn-based player is not left staring at whoever's
        menu happened to be open when the turn passed."""
        if self._menu is not None:
            self._menu.select_crew_directly(crew_id)

    def poll_orders(self) -> list[Order]:
        """Legacy AppRenderer hook: the CONTROL panel now issues orders straight
        to the sim (see :class:`MenuController`), so this is always empty."""
        out, self._pending_orders = self._pending_orders, []
        return out

    def poll_special_options(self) -> list[SpecialOption]:
        """Return Special Options queued during the last ``poll_input()`` drain."""
        specials, self._pending_specials = self._pending_specials, []
        return specials

    # --- screen dispatch ----------------------------------------------------
    def draw(self, flow: GameFlow) -> None:
        """Draw whichever screen the flow is on (the app loop's per-frame call)."""
        # **the frame counter must advance on EVERY screen.** It used to
        # be incremented inside `render()`, which only runs on the play screen,
        # so every front-end animation keyed off it stood still: the GREEN
        # VALLEY colour-RAM spiral (D-104) and the WELCOME marquee chase
        # (D-119) were both implemented, unit-tested and frozen in the actual
        # game. The unit tests passed because they set `_frame_count` by hand —
        # a good reminder that testing a draw call is not testing the loop.
        self._frame_count += 1
        self._crt_live = (_CRT_SCREENS is None
                           or flow.screen in _CRT_SCREENS)
        self._crt_follow_menu(flow.screen)
        self._update_intro_music(flow.screen)
        if flow.screen is not Screen.WELCOME:
            self._welcome_entered_frame = None  # D-143
        if flow.screen is not Screen.EXIT_ADVERT:
            self._exit_entered_frame = None     # D-175
        # The manual's last page shows the same legend and reveals it the same
        # way (owner, 2026-08-29), so it resets the same counters — otherwise
        # opening the manual after the SHORT introduction would show a legend
        # already finished, silently.
        showing_legend = flow.screen is Screen.INTRO_LEGEND or (
            flow.screen is Screen.MANUAL and flow.manual_showing_legend
        )
        if not showing_legend:
            self._legend_entered_frame = None    # D-176
            self._legend_played = 0
        if flow.screen is not Screen.PLAYING and self._heartbeat_channel is not None:
            # D-145: the heartbeat belongs to the play screen only.
            try:
                self._heartbeat_channel.stop()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                pass
            self._heartbeat_channel = None
            self._heartbeat_composure = None
            # Clear the rate too, or leaving the play screen and coming back
            # early-returns on a stale match and the bed never restarts
            # (DISC-254).
            self._heartbeat_rate = None
        if flow.screen is not Screen.PLAYING and self._tracker_channel is not None:
            try:
                self._tracker_channel.stop()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - no audio device
                pass
            self._tracker_channel = None
        self._emit_for(flow)
        if flow.screen is Screen.FIRST_RUN:
            self._draw_first_run(flow)
        elif flow.screen is Screen.BOOT:
            self._draw_boot(flow)
        elif flow.screen is Screen.LOADING_MENU:
            self._draw_loading_menu(flow)
        elif flow.screen is Screen.NOTICE:
            self._draw_notice(flow)
        elif flow.screen is Screen.WELCOME:
            self._draw_welcome(flow)
        elif flow.screen is Screen.EXIT_ADVERT:
            self._draw_exit_advert(flow)
        elif flow.screen is Screen.INTRO_PROMPT:
            self._draw_intro_prompt(flow)
        elif flow.screen is Screen.INTRO_LEGEND:
            self._draw_intro_legend(flow)
        elif flow.screen is Screen.INSTRUCTIONS:
            self._draw_instructions(flow)
        elif flow.screen is Screen.INSTRUCTION_PAGES:
            self._draw_instruction_pages(flow)
        elif flow.screen is Screen.LOADING_PLAY:
            self._draw_loading_play(flow)
        elif flow.screen is Screen.TITLE:
            self._draw_title(flow)
        elif flow.screen is Screen.GAME_SELECTION:
            self._draw_selection(flow)
        elif flow.screen is Screen.MANUAL:
            self._draw_manual(flow)
        elif flow.screen is Screen.CREDITS:
            self._draw_credits(flow)
        elif flow.screen is Screen.OPTIONS:
            self._draw_options(flow)
        elif flow.screen is Screen.OPENING:
            self._draw_opening(flow)
        elif flow.screen is Screen.PLAYING and flow.sim is not None:
            # The Simulation is built at game start (after selection), so adopt
            # its ship + build the CONTROL-panel menu on the first play frame.
            if self._sim is not flow.sim:
                self._sim = flow.sim
                self._ship = flow.sim.ship
                self._menu = MenuController(flow.sim)
                # Carry the journal hook onto each new panel: a fresh
                # game builds a new controller, and a recording that
                # stopped at the first restart would be worse than none.
                self._menu.on_action = self._on_menu_action
            # **T6.** `render(state)` never sees `flow`, and the turn count is
            # deliberately a `GameFlow` presentation counter, not a
            # `GameState` fact (see its own docstring) - so it is carried
            # across here, the same way `_sim`/`_ship` are adopted above.
            self._turns_on = flow.options.values.get("turns") == "on"
            # **Not the original.** The panel has no other way to know this
            # (it is built from `sim` alone) — see `MenuController.turns_on`'s
            # own comment. `_menu` can still be `None` here in a test that
            # pre-sets `_sim` without going through the construction branch
            # above (several older fixtures do), so this is a plain guard,
            # not an invariant to assert.
            if self._menu is not None:
                self._menu.turns_on = self._turns_on
            self._turn_count = flow.turn_count
            # **Initiative (2026-09-04), not the original.** Same carry-across
            # reasoning as `_turn_count` above: `flow.current_turn_actor()`
            # reads `GameFlow`'s own initiative state, which `render(state)`
            # cannot see.
            actor = flow.current_turn_actor()
            crew_actor = flow.sim.state.crew.get(actor) if actor else None
            is_crew_actor = crew_actor is not None
            self._turn_actor = (
                crew_actor.name.upper() if crew_actor is not None
                else (actor or "").upper()
            )
            # **Action points (2026-09-05), not the original.** `None` for a
            # creature slot — `TURN_ACTIONS_PER_TURN` never applied to it in
            # the first place, so showing "0 LEFT" would claim a budget that
            # was never spent rather than never granted.
            self._turn_actions_left = (
                flow.turn_actions_left if is_crew_actor else None
            )
            self.render(flow.sim.state)
        elif flow.screen is Screen.ENDED and flow.sim is not None:
            self._draw_end(flow)



    def _blit_codes(self, codes: "list[int]", col: int, row: int,
                    colour: tuple[int, int, int]) -> None:
        """Blit raw **screen codes** on the character grid (D-081).

        The opening's garbled name is arbitrary BASIC ROM bytes, not text, so it
        cannot go through the ASCII map — it has to be drawn as the codes the
        original actually puts in screen RAM.
        """
        if self._tiles is None:
            return
        for i, code in enumerate(codes):
            glyph = self._tiles.glyph(code & 0xFF)
            cx, cy = (col + i) * 8, row * 8
            for y, line in enumerate(glyph):
                for x, on in enumerate(line):
                    if not on:      # cut-out font: the 0-bits are the ink
                        self._surface.fill(
                            colour, ((cx + x), (cy + y), 1, 1))





    def _draw_narcissus_moon(self) -> None:
        """Sprite 0 as `setup_cursor_sprite` leaves it — pointer `$D1`,
        **hires** white, at VIC (172, 50) (D-147: `$D01C = 0` live; `$D01B`
        is the sprite-BEHIND-background priority bit, not multicolor). Set
        bits are the sprite; drawn before the glyph ink so full-ink cells
        occlude it — exactly the VIC's behind-foreground priority."""
        if self._tiles is None:
            return
        region = self._tiles.region
        off = _MOON_POINTER * 64 - _SPRITE_BANK_BASE
        data = region[off:off + 63]
        x0, y0 = _MOON_VIC_POS[0] - 24, _MOON_VIC_POS[1] - 50
        white = c64.rgb(c64.WHITE)
        for row in range(21):
            for bcol in range(3):
                b = data[row * 3 + bcol]
                for bit in range(8):
                    if b & (0x80 >> bit):
                        x = x0 + bcol * 8 + bit
                        self._surface.fill(white, (x, (y0 + row), 1, 1))

    def _load_cockpit_capture(self) -> tuple[list[int], list[int]] | None:
        """The real machine's cockpit screen+colour RAM (D-147), or None.

        `docs/reference/narcissus_0400.bin` / `narcissus_d800.bin`, captured
        live by `tools/vice-mcp/capture_cockpit_real.py` — same 2-byte
        load-address format as the deck captures. Cached after first load.
        """
        if self._cockpit_capture is not None:
            return self._cockpit_capture if self._cockpit_capture else None
        base = self._reference_dir
        try:
            scr = (base / "narcissus_0400.bin").read_bytes()[2:]
            col = (base / "narcissus_d800.bin").read_bytes()[2:]
        except OSError:
            self._cockpit_capture = ()
            return None
        self._cockpit_capture = (list(scr), [b & 0x0F for b in col])
        return self._cockpit_capture

    def _draw_narcissus_cockpit(self) -> None:
        """**[C $5134-$513B / C-live] D-144/D-147 — the NARCISSUS cockpit.**

        The trigger is ROM-decoded (`menu_option_dispatch` loads no deck
        template for room 34 and repurposes sprite 0 as the moon); the
        picture itself is the **real machine's own screen + colour RAM**,
        captured by running the ROM's selection routine live with a crew
        member poked into room 34 (D-147). It is drawn here exactly as the
        VIC draws it: per-cell glyph ink (this cut-out charset's 0-bits) in
        that cell's colour-RAM colour over the black `$D021` field, with the
        moon sprite between the two (priority-behind, `$D01B`).

        Rows 0-17 of the capture are drawn; the capture's row 18 (a light
        grey floor strip) sits where this renderer's status band lives and
        would be covered anyway. Without the capture files or a tileset the
        area stays black + moon (graceful, like the deck fallback).
        """
        # Black field first (the capture's $D021 is 0 on this screen).
        self._surface.fill(
            c64.rgb(c64.BLACK), (0, 0, _MAP_COLS * 8, 18 * 8)
        )
        self._draw_narcissus_moon()
        cap = self._load_cockpit_capture()
        if cap is None or self._tiles is None:
            return
        scr, col = cap
        for row in range(min(_COCKPIT_ROWS_USED, 18)):
            for c in range(_MAP_COLS):
                code = scr[row * 40 + c]
                colour = c64.rgb(col[row * 40 + c])
                glyph = self._tiles.glyph(code)
                cx, cy = c * _C64_CELL, row * _C64_CELL
                for y, line in enumerate(glyph):
                    for x, on in enumerate(line):
                        # **Set bits are the foreground here** — the same
                        # polarity `_rasterize_backdrop` uses for the deck
                        # maps, NOT the front-end screens' cut-out model.
                        # In this charset `$A0` is all-1s (solid: the hull)
                        # and `$20` all-0s (clear: the window, through which
                        # the moon sprite shows).
                        if on:
                            self._surface.fill(
                                colour, ((cx + x), (cy + y), 1, 1)
                            )



























    def _draw_border(self) -> None:
        """No-op: R-02 moved the border outside the field (see `_present`)."""







        # **Neither the Alien NOR Jones appears on the deck map (D-041,
        # D-046).** Both were drawn here as persistent markers; both were
        # inventions. The decisive proof is the game's own **deck-plan key**
        # (`$4460`, part of the instructions text), which enumerates exactly
        # five map symbols:
        #     "Location Ptr" · "Grille" · "Ladder Up" ·
        #     "Character Postn" · "Ladder Down"
        # — no Alien symbol and no cat symbol. What the map shows is the
        # location pointer, grilles, ladders and *crew* positions, full stop.
        # Movement by anything else is learned only from the ambiguous
        # TRACKER alarm ("SOMETHING moving between locations.", `$453C`) —
        # see `sim._use_tracker` and DISASSEMBLY §8.9b.
        # `_ALIEN_SPRITE_FRAMES`/`_blit_sprite` are kept: that frame data is
        # real (decoded from `update_1`) and correct, just not used here.

    def should_quit(self) -> bool:
        return self._quit

    def close(self) -> None:
        pygame.quit()
