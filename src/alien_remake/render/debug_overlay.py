"""A performance overlay for the Ctrl+3 debug mode. **Not the original.**

There is no such display in the ROM. This is development instrumentation, in
its own module for the same reason the marker overlay is flagged in DISC-245:
so a later fidelity audit can see at a glance that nothing here is a claim
about the 1984 game.

**The measurement must not distort what it measures.** Three rules follow from
that and are worth stating, because each is easy to get wrong:

* Frame rate is read from the interval between `_present` calls — the whole
  frame including this overlay — not from a timer wrapped around the drawing.
  An overlay that excludes its own cost reports a frame rate the player is not
  getting.
* The overlay's own cost is therefore measured and *shown*, so you can tell how
  much of the number is the thing you are debugging and how much is the
  debugger.
* Memory is sampled once a second, not per frame. `GetProcessMemoryInfo` is a
  syscall; reading it 30 times a second to display a number that moves slowly
  would be the overlay changing the answer.

Everything is off unless `_debug_markers` is set, and the instrumentation
itself is three `perf_counter()` calls a frame — measured below a microsecond
in total, so it stays live rather than being branched around.
"""

from __future__ import annotations

import ctypes
import sys
import time
from collections import deque

import pygame  # the project's one optional runtime dependency (D-009)

from ..core.state import GameState
from . import c64
from .protocol import RendererState

#: Frames of history behind the rolling averages. At 30 fps this is two
#: seconds — long enough to be steady, short enough to show a stall.
HISTORY = 60

#: How often the memory syscall is allowed to run.
MEMORY_SAMPLE_S = 1.0

#: How often the readout is re-composed. Two reasons, and the second is the
#: one that actually decided it:
#:
#: * a frame-rate figure updating thirty times a second is unreadable; and
#: * composing it costs more than the frame it is measuring. The lines are
#:   longer than `_GLYPH_CACHE_MAX_LEN`, so every one is a fresh SysFont
#:   render — measured at **1.13 ms against a 0.75 ms draw**. Rebuilding four
#:   times a second and blitting the cached panel drops that by ~87%.
REFRESH_S = 0.25

#: Overlay geometry, in native 320x200 pixels. Top-left, over the map field,
#: which is the least informative part of the play screen while debugging.
_X, _Y, _LINE = 2, 2, 8
_WIDTH = 148
#: The two columns (owner, 2026-08-30): the readout on the left, the testing
#: keys on the right. Widths are generous rather than measured, because the
#: border they sit in is the full window width and there is nothing to compete
#: for — it was *height* that did not fit, which is why there are two columns
#: at all.
_STAT_WIDTH = 152
_KEY_WIDTH = 224


def _rss_mb() -> float | None:
    """Resident set size in MB, or ``None`` where it cannot be read.

    Windows only for now, via `psapi`. Deliberately not a new dependency:
    `psutil` would be the obvious answer and this is a debug readout, not
    something the game needs. Returns ``None`` elsewhere and the row is
    labelled accordingly rather than showing a wrong number.
    """
    if sys.platform != "win32":  # pragma: no cover - platform dependent
        return None
    try:
        size_t = ctypes.c_size_t

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_uint32), ("PageFaultCount", ctypes.c_uint32),
                ("PeakWorkingSetSize", size_t), ("WorkingSetSize", size_t),
                ("QuotaPeakPagedPoolUsage", size_t), ("QuotaPagedPoolUsage", size_t),
                ("QuotaPeakNonPagedPoolUsage", size_t),
                ("QuotaNonPagedPoolUsage", size_t),
                ("PagefileUsage", size_t), ("PeakPagefileUsage", size_t),
            ]

        psapi = ctypes.WinDLL("psapi")
        fn = psapi.GetProcessMemoryInfo
        fn.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_uint32]
        fn.restype = ctypes.c_int
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if not fn(handle, ctypes.byref(counters), counters.cb):
            return None
        return float(counters.WorkingSetSize) / (1024 * 1024)
    except Exception:  # pragma: no cover - never let a readout break the game
        return None


class DebugOverlayMixin(RendererState):
    """Frame rate, audio, memory and latency, drawn when Ctrl+3 is on."""

    # --- instrumentation ----------------------------------------------------

    def _debug_mark_input(self) -> None:
        """Called as input polling starts — the head of the latency window."""
        self._dbg_input_at = time.perf_counter()

    def _debug_mark_present(self) -> None:
        """Called as the frame reaches the screen — the tail of both windows."""
        now = time.perf_counter()
        if self._dbg_last_present is not None:
            self._dbg_frames.append(now - self._dbg_last_present)
        self._dbg_last_present = now
        if self._dbg_input_at is not None:
            self._dbg_latency.append(now - self._dbg_input_at)
            self._dbg_input_at = None

    # --- the readout --------------------------------------------------------

    def _debug_audio_line(self) -> str:
        init = pygame.mixer.get_init()
        if init is None:
            return "audio  off"
        freq, _size, channels = init
        held = 0
        for clip in self._sfx_cache.values():
            raw = getattr(clip, "get_raw", None)
            if raw is not None:
                held += len(raw())
        busy = pygame.mixer.get_busy()
        return (
            f"audio  {freq // 1000}k/{channels}ch "
            f"{len(self._sfx_cache)}clip {held / 1048576:.1f}M "
            f"{'play' if busy else 'idle'}"
        )

    def _debug_audio_spec_line(self) -> str | None:
        """The loudness spec check, in the border alongside the rest of the
        developer readout. **Not the original** — see
        `constants.SOUND_TARGET_LUFS`'s own comment. `None` (the row is
        simply omitted) when there is nothing to show.

        **Reads `self._dbg_audio_spec`, never computes it.** K-weighting and
        gating every recording found is not cheap for a real-world clip (a
        several-second CC0 download, unlike this game's own sub-3s effects),
        and drawing must stay fast every frame — `test_the_overlay_costs_
        almost_nothing_per_frame` measures exactly that. `__main__.py`
        computes the report once at startup (the same pass that already
        builds the boot screen's warnings) and sets this field directly; a
        bare `PygameRenderer()` that never went through that startup path
        simply has nothing to show here, which is correct for it.
        """
        report = self._dbg_audio_spec
        if not report:
            return None
        bad = sum(1 for entry in report if not entry.in_spec)
        ok = len(report) - bad
        suffix = f"  {bad} OUT OF SPEC" if bad else ""
        return f"audio spec  {ok}/{len(report)} ok{suffix}"

    def _debug_lines(self, state: GameState) -> list[str]:
        """The readout's left column. The testing keys are the right one
        (`_debug_key_lines`), so this stays five rows and the panel stays
        short enough for the border it sits in."""
        frames = self._dbg_frames
        if frames:
            avg = sum(frames) / len(frames)
            fps = 1.0 / avg if avg else 0.0
            worst = max(frames) * 1000.0
        else:
            fps, avg, worst = 0.0, 0.0, 0.0
        latency = (
            sum(self._dbg_latency) / len(self._dbg_latency) * 1000.0
            if self._dbg_latency else 0.0
        )

        now = time.perf_counter()
        if now - self._dbg_memory_at >= MEMORY_SAMPLE_S:
            self._dbg_memory = _rss_mb()
            self._dbg_memory_at = now
        memory = (
            f"{self._dbg_memory:.0f}M" if self._dbg_memory is not None else "n/a"
        )

        # Sim ticks are the *game's* clock, not the display's; showing both is
        # the point, because they are deliberately different rates.
        ticks = state.tick - self._dbg_last_tick
        if now - self._dbg_tick_at >= 1.0:
            self._dbg_tick_rate = ticks / (now - self._dbg_tick_at)
            self._dbg_last_tick, self._dbg_tick_at = state.tick, now

        # **Say where the Alien is, and in which space (DISC-257).** The duct
        # network is a separate graph, so a ducted creature hops between rooms
        # with no door between them. Drawing only a marker made that look like
        # teleporting; naming the space removes the ambiguity.
        alien = state.alien
        if alien is None or not alien.alive:
            where = "alien  --"
        else:
            where = (
                f"alien  {(alien.room_id or '?')[:10]} "
                f"{'DUCT' if alien.in_duct else 'room'}"
            )
        lines = [
            f"fps {fps:5.1f}  frame {avg * 1000:4.1f}ms  max {worst:4.1f}",
            where,
            f"lat {latency:5.1f}ms  tick {self._dbg_tick_rate:4.1f}/s",
            self._debug_audio_line(),
            f"mem {memory}  glyphs {len(self._glyph_cache)}  "
            f"ovl {self._dbg_overlay_ms:.2f}ms",
        ]
        spec_line = self._debug_audio_spec_line()
        if spec_line is not None:
            lines.append(spec_line)
        return lines

    def _debug_key_lines(self) -> list[str]:
        """The testing keys, on screen. **Owner, 2026-08-30.**

        They were documented in the README and nowhere a person actually
        looking at the game could see them, which for five function keys with
        no other affordance means they may as well not exist. Listed here
        rather than as a separate panel because there is already exactly one
        thing drawn in the border and one is enough.

        Read from `DEV_KEYS` rather than written out again, so a key added to
        the handler cannot go unlisted - and each row says the *current* state
        of anything that has one, since "F3 alien" tells you nothing about
        whether the Alien is currently frozen.
        """
        rows = ["-- testing keys --"]
        states = self._dev_key_states()
        for key, label in self.DEV_KEYS.items():
            name = pygame.key.name(key).upper()
            state = states.get(key, "")
            rows.append(f"{name:<3} {label}{state}")
        return rows

    def _dev_key_states(self) -> dict[int, str]:
        """What the toggles are currently set to, for the key list.

        Empty for the keys that do a thing rather than hold a state - a fear
        nudge has no "on", and saying so would be noise.
        """
        if self._sim is None:
            return {}
        from ..core.devtools import Freeze

        out: dict[int, str] = {}
        if self._sim.dev.alien is Freeze.STILL:
            out[pygame.K_F3] = "  [STILL]"
        if self._sim.dev.jones is Freeze.STILL:
            out[pygame.K_F4] = "  [STILL]"
        if self._sim.state.android_revealed:
            out[pygame.K_F5] = "  [OUT]"
        return out

    def _draw_debug_overlay(self, state: GameState) -> None:
        """Draw the readout. **Not the original** — Ctrl+3 only."""
        if not self._debug_markers:
            return
        start = now = time.perf_counter()
        if self._dbg_panel is None or now - self._dbg_panel_at >= REFRESH_S:
            # **Two columns, and that is what makes it fit.** Stacked, the
            # stats plus the key list came to 98px, and the border is 64px at
            # 2x and 96px at 3x — so a single column did not fit the strip it
            # was moved into, at either of the two commonest window sizes.
            # Side by side it is ~7 rows instead of ~13, and the top border is
            # 768px wide at 2x, so width was never the scarce thing.
            stats = self._debug_lines(state)
            keys = self._debug_key_lines()
            rows = max(len(stats), len(keys))
            height = _LINE * rows + 2
            panel = pygame.Surface((_STAT_WIDTH + _KEY_WIDTH, height))
            panel.fill(c64.rgb(c64.BLACK))
            # Opaque now that it sits in the border (`_blit_debug_panel`).
            # The 210 was a compromise with the map underneath; there is
            # nothing underneath any more, and a translucent panel over the
            # border colour was simply harder to read for no gain.
            panel.set_alpha(255)
            for column, (x, texts) in enumerate((
                (1, stats), (_STAT_WIDTH + 1, keys),
            )):
                colour = c64.LIGHT_GREEN if column == 0 else c64.YELLOW
                for i, text in enumerate(texts):
                    panel.blit(
                        self._c64_or_sysfont(
                            text, c64.rgb(colour), c64_font=False
                        ),
                        (x, 1 + i * _LINE),
                    )
            self._dbg_panel, self._dbg_panel_at = panel, now
        # **Composed here, blitted in `_blit_debug_panel` (owner, 2026-08-29).**
        # It used to go straight onto the 320x200 field, which put it over the
        # top-left of the ship map — the part of the screen you most need to see
        # while debugging the ship map. The border is dead space that costs
        # nothing to cover, so the panel goes there and the field is left alone.
        # Measured and displayed, so the reader can subtract the debugger from
        # the thing being debugged. This is the *composing* frame's cost on the
        # frames that rebuild, and the blit alone on the rest.
        self._dbg_overlay_ms = (time.perf_counter() - start) * 1000.0

    def _blit_turn_indicator(self) -> None:
        """**T6 — whose turn, what is left.** Not the original.

        Independent of `_debug_markers`: this is a player-facing readout for
        the `turns` option (C2), not a development tool, so it must show
        whenever turns is on regardless of whether Ctrl+3 is. Placed the same
        way as `_blit_debug_panel` — the border, outside the field, never
        scaled — but the two never fight for the same strip in practice: the
        debug panel prefers the strip above the field and this one the strip
        below, so both can be on together without one covering the other.
        """
        if not self._turns_on:
            return
        field = self.field_rect()
        # **Initiative (2026-09-04), not the original.** `_turn_actor` is "" only
        # when `flow.turn_order` itself is empty (turns flipped on mid-run,
        # before a restart rolls one - see `GameFlow._start`), so the label
        # falls back to the plain counter rather than print a bare "TURN 3:".
        label = (
            f"TURN {self._turn_count}: {self._turn_actor}"
            if self._turn_actor
            else f"TURN {self._turn_count}"
        )
        # **Action points + skip (2026-09-05), not the original.**
        # `_turn_actions_left` is `None` for a creature slot (no budget to
        # show) and for the no-actor case above (already covered by
        # `_turn_actor` being empty there too).
        if self._turn_actor and self._turn_actions_left is not None:
            label += f"  AP LEFT:{self._turn_actions_left}  [K] SKIP"
        text = self._c64_or_sysfont(
            label, c64.rgb(c64.YELLOW), c64_font=False
        )
        w, h = text.get_width(), text.get_height()
        if self._window.get_height() - field.bottom >= h + 2:
            at = (max(2, field.left), field.bottom + 1)
        elif field.top >= h + 2:
            at = (max(2, field.left), field.top - h - 1)
        else:
            at = (field.left + 1, field.top + 1)
        self._window.blit(text, at)

    def _blit_debug_panel(self) -> None:
        """Put the readout in the **border**, outside the game field.

        Called from `_paint` after the field is scaled in, so it lands on the
        window rather than on the 320x200 surface — which is the whole point:
        nothing it draws can cover the map, and it is not scaled up with the
        field either, so it stays legible at any window size.

        Placed in whichever border strip actually has room, preferring the top.
        A window with no border at all (an exact fit) falls back to the old
        over-the-field position, because a panel you cannot see is worse than
        one in the way.
        """
        if not self._debug_markers or self._dbg_panel is None:
            return
        field = self.field_rect()
        panel = self._dbg_panel
        w, h = panel.get_width(), panel.get_height()
        if field.top >= h + 2:                      # the strip above the field
            at = (max(2, field.left), field.top - h - 1)
        elif field.left >= w + 2:                   # the strip to its left
            at = (field.left - w - 1, max(2, field.top))
        elif self._window.get_height() - field.bottom >= h + 2:
            at = (max(2, field.left), field.bottom + 1)
        else:                                       # no border to speak of
            at = (field.left + 1, field.top + 1)
        self._window.blit(panel, at)
