"""The headless game-state model (stdlib only, no rendering, no wall-clock).

Pure data plus the enums that describe outcomes. State *transitions* live in
:mod:`alien_remake.core.sim` so the data stays trivially constructible in tests.
This implements ``docs/spec/GAME_SPEC.md``; it models only the real-time clock
and the tick clock (§2). Crew/PCS, the ship map, items and
the Alien are added as fields on :class:`GameState`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from . import constants
from .alien import Alien
from .crew import CrewMember
from .items import ItemInstance
from .modes import GameMode
from .sound import SoundCue


class GamePhase(Enum):
    """Top-level game outcome (GAME_SPEC §1)."""

    RUNNING = auto()
    WON = auto()
    LOST = auto()


class WinRoute(Enum):
    """The three victory routes (GAME_SPEC §1); recorded when a game is WON."""

    EVACUATED = auto()  # all surviving crew off in the Narcissus
    ALIEN_KILLED = auto()
    ALIEN_AIRLOCKED = auto()


@dataclass
class GameState:
    """The complete simulation state at one tick.

    Fields:

    - ``tick`` — fixed-tick counter (advances at ~``TICK_HZ``, GAME_SPEC §2).
    - ``awake_crew`` — count of crew out of hypersleep. **Informational only.**
      It never drives anything: the oxygen system it once fed was removed
      outright (FV-2.5 / D-062 — the C64 game has none, see `constants.py`).
      Hypersleep itself IS real (the "ENTER HYPERSLEEP" special, `$57D4`), so
      the per-member ``crew[...].awake`` flags stay; this aggregate is just
      kept in lockstep with them by ``Simulation._set_hypersleep``.
    - ``crew`` — the seven crew keyed by id (GAME_SPEC §4/§5). Empty until the
      Simulation populates it (or a test builds a bare state).
    - ``items`` — every item instance keyed by id (GAME_SPEC §10). Empty
      until the Simulation spawns the catalog onto the ship.
    - ``alien`` — the Alien's position + alive flag (GAME_SPEC §11 #2).
      ``None`` until the Simulation spawns it.
    - ``jones_room_id`` / ``jones_caught`` — the cat's position (GAME_SPEC
      §8); caught via USE of the `cat_box` item.
    - ``airlocks_open`` — per-airlock-room open/sealed flag (GAME_SPEC §8);
      absent means sealed. Opening one with the Alien inside kills it (win
      route 3); opening one with any crew inside would matter for a future
      depressurization hazard, not modelled yet.
    - ``auto_destruct_ticks`` — ticks remaining until self-destruct, or ``None``
      if not initiated (GAME_SPEC §8).
    - ``mode`` — short vs. full game length (GAME_SPEC §9); set once at
      ``Simulation`` construction, informational thereafter (drives the ship
      size when the Simulation builds its own state).
    - ``opening_dead_crew_id`` — which crew member was already dead at
      scenario start (GAME_SPEC §9), or ``None`` for a bare test state
      that skipped the opening (the Simulation only sets this when it
      populates the default crew itself).
    - ``phase`` / ``win_route`` — outcome (§1).
    """

    tick: int = 0
    awake_crew: int = 0
    phase: GamePhase = GamePhase.RUNNING
    win_route: WinRoute | None = None
    # Map view: which deck the player is watching + the map cursor (grid
    # coords). The ship topology itself lives in `core.map.ShipMap`, owned by the
    # Simulation, not duplicated here.
    deck: int = 0
    cursor: tuple[int, int] = (0, 0)
    # Crew & PCS: the seven crew by id (GAME_SPEC §4/§5).
    crew: dict[str, CrewMember] = field(default_factory=dict)
    # Items: every item instance by id (GAME_SPEC §10); ShipMap owns no
    # item state, so location lives on the instance (`room_id` xor `holder`).
    items: dict[str, ItemInstance] = field(default_factory=dict)
    # The Alien: None until the Simulation spawns it (or a bare test state
    # that never sees combat).
    alien: Alien | None = None
    # Jones the cat (GAME_SPEC §4/§8): wanders on its own; caught with the
    # `cat_box` item via USE (R-17; the old CATCH_JONES special was removed).
    jones_room_id: str | None = None
    jones_caught: bool = False
    #: **[C $87B6/$87D7] D-153** — WHICH item Jones was caught in. The ROM
    #: renames the catching item ("Jones:Net" / "Jones:Box") and
    #: `check_mother_refuses ($5B1F)` then requires *that item* to be in the
    #: NARCISSUS, or held by someone who is, before the launch is allowed. So
    #: "caught" is not enough — the container has to be carried aboard.
    jones_container_id: str | None = None
    #: **[C $64DC] P2-17 — the crew member the Alien is carrying.**
    #: `alien_death_effects ($4292)` stows a fresh victim with `stow_char
    #: ($599E)`, which parks their location byte at the off-map sentinel `$BB`;
    #: `restore_stowed_char ($59A7)` later drops them **into the ducting at the
    #: Alien's own position**. Only one body at a time (`$42A1 BNE` skips the
    #: stow while the slot is occupied). This is why crew turn up in the ducts
    #: after an attack.
    stowed_crew_id: str | None = None
    #: **[C $52D7] `$64CC`** — a character slot locked out of selection.
    #: `$52D4 LDA $7214 / STA $64CC` writes it on the android's **reveal** path
    #: (and recolours the background, `$52DA STA $D021`). `$7214` holds the
    #: *acting* slot (`$723E STY $7214`), so the value is **the android's own
    #: slot** — the android locks itself out by being found out. The attack
    #: path (`$5439`) never writes it; it only wounds. And
    #: `guard_alien_present ($7740 CPY $64CC / BEQ)` refuses to select whoever
    #: it names. Cleared to 0 by the init wipe at `$65A9`, and slot 0 is the
    #: Alien, so nobody is locked at game start.
    locked_crew_id: str | None = None
    #: SID call sites reached during the current tick (D-088). Cleared at the
    #: top of every `Simulation.advance`; the presentation layer drains it and
    #: applies `sound.audible` to decide what is actually heard.
    sound_cues: list[SoundCue] = field(default_factory=list)
    # Special Options (GAME_SPEC §6.2 #3/§8): airlock open/seal state by
    # room id (absent = sealed) and an auto-destruct countdown (None = not
    # initiated).
    airlocks_open: dict[str, bool] = field(default_factory=dict)
    auto_destruct_ticks: int | None = None

    # Game modes & the opening (GAME_SPEC §9): the active length variant,
    # and which crew member (if any) was found already dead at scenario start.
    mode: GameMode = GameMode.FULL
    opening_dead_crew_id: str | None = None
    # The motion tracker's last result: True when the last USE of a
    # tracker **detected movement somewhere aboard**. **Replaced
    # `alien_reading_room` 2026-07-24 (D-041)** — that field stored the
    # Alien's exact room, an invention with no ROM backing. The game's own
    # sound-legend text proves the tracker is an alarm naming neither a room
    # nor an entity ("the TRACKER alarm." / "SOMETHING moving between
    # locations.", `$451C`/`$453C`), corroborated by the user: a detection
    # could be the Alien, Jones, or another crew member. Presentation only.
    tracker_alarm: bool = False
    # Structural room damage (full disassembly, DISASSEMBLY §8.6 / D-009): the
    # game's per-room damage accumulator `$653F,X`, keyed by room id (absent = 0).
    # The Alien corrodes its current room every tick (acid/tearing) and a landed
    # weapon hit spills acid there; a room past `HULL_BREACH_THRESHOLD` vents to
    # space (a loss). Recorded here so the renderer can show "STRUCTURAL DAMAGE".
    room_damage: dict[str, int] = field(default_factory=dict)
    # Per-room **damage-alarm stage** — the game's `$651C,X` (D-044). A
    # one-way latch, NOT a function of `room_damage`: `damage_room_b ($5587)`
    # raises it (0 -> 1) the first time a room's raw damage crosses 4, and
    # only ever re-raises it while it reads 0. The FIGHT FIRE / extinguisher
    # handler (`$5889`) resets it to 0 — which is *all* it does; it never
    # reduces `room_damage`, so structural damage is permanent and the alarm
    # simply returns on the next damage tick. Absent = 0 = no active alarm.
    room_alarm: dict[str, int] = field(default_factory=dict)
    # Per-room **FIRE flag** — the game's `$5753,X` (D-073). `damage_room_b`
    # writes 6 into it (`$55B1 LDA #$06`) when a room in the 17-19 band latches
    # its alarm; those are exactly the rooms `$54A3` assigns malfunction type 4
    # ("FIRE IN ..."), and FIGHT FIRE clears it alongside the alarm ($58CF,
    # D-066). Absent = no fire.
    room_fire: dict[str, int] = field(default_factory=dict)
    # The malfunction banner currently displayed, or None. Raised by the same
    # event that latches a room's alarm (`damage_room_b $5587` falls straight
    # into the message dispatcher at `$55C1`), from the static per-room table
    # `$54A3` (D-072/D-073).
    malfunction: str | None = None
    #: **[C $07C0 + `delay_long` + `clear_line_07c0`] DISC-231 — the game's
    #: transient banner.** Several handlers write a message to `$07C0` (row 24
    #: col 0), call `delay_long ($561C)`, then blank the row again and restore
    #: the border. Decoded so far: "MOTHER refuses launch" (`$5B80`), "Go get
    #: Jones" (`$5C33`) and "Fire Out  " (`$5950`). None of them were ever
    #: shown by the remake — the handlers returned a bare bool.
    #:
    #: `delay` itself does `LDA #$00 / STA $D020` ($5626-$5628) and every
    #: caller restores `#$06` afterwards, so the border is **black for the
    #: whole pause** — which is exactly the "the game freezes for a moment and
    #: the border turns black" the owner reported on a refused launch.
    notice: str | None = None
    #: Ticks of `notice` left to show, standing in for the ROM's blocking
    #: `delay_long`. The remake cannot block its own loop, so the banner is
    #: timed instead; the border is held black for the same span.
    notice_ticks: int = 0
    #: **[C $52DA `STA $D021`] DISC-231 — the android reveal's only tell.**
    #: The reveal path writes the *acting slot number* straight into the VIC
    #: background register, so `$D021` stops being black and becomes colour
    #: 1-7 (the android's own slot). Because ALIEN's font is cut-out, `$D021`
    #: is the **ink** every glyph shows through (D-050) — so the whole screen's
    #: lettering changes colour at once. That, plus being locked out of
    #: selecting them (`locked_crew_id`), is how the game tells you.
    #:
    #: 0 = black, the normal play-screen value (`$7027 STA $D021`).
    background_colour: int = 0
    # **THE ANDROID** — the game's `$64C3` (D-080). A hidden, randomly-chosen
    # crew member (from DALLAS/KANE/ASH/PARKER, always someone other than the
    # opening victim) who attacks crew sharing its room, cannot enter
    # hypersleep, survives the endgame mass kill, and does not count toward the
    # COMPETENCE RATING. The game never names it on screen — the instructions
    # say the player is "not knowing which member of the crew is an android".
    android_id: str | None = None
    # The game's `$64CC` — set to the android's own slot once it is **found
    # out** (D-080b, `$52D7`), which also writes `$D021` and flashes the screen
    # background. Until then the android passes for crew.
    android_revealed: bool = False

    #: **[C `$64CF`] DISC-230 — "the ship is going to be destroyed".** Set both
    #: by arming SCUTTLE (`set_result_win $58E5`) and by a hull breach
    #: (`$5DC6 LDA #$01 / STA $64CF`), and read by `mainloop_sub_5a26 ($5A26)`
    #: to flash the border. `select_outcome ($60AE)` branches the ending's
    #: first line on it, and `draw_ending_survivor ($62D6)` **clears** it when
    #: the android saves the ship — which is also what re-enables the
    #: damage-bonus term at `$6229`.
    ship_destructing: bool = False
    #: **[C `hull_breach ($5D17)`] DISC-234 — the ship actually blew up.**
    #: Distinct from `ship_destructing`, which only means the destruct is
    #: *armed*: this is set at the two sites that `JMP hull_breach` — a room
    #: reaching exactly 20 damage (`$565C`) and the auto-destruct countdown
    #: running out (`$5A43`) — and it is what runs the burning-ship spiral
    #: before the ending screen.
    ship_destroyed: bool = False
    #: **[C `$64E3`] DISC-230 — the NARCISSUS has launched and is away.** Set
    #: at `$95B7` on the launch path (`$5C18 JSR play_note_b`). It is what lets
    #: crew aboard the shuttle count as alive in the ending scan (`$6300`), and
    #: what spares them when the ship breaks up (`$5DAD`).
    narcissus_launched: bool = False

    @property
    def auto_destruct_minutes_left(self) -> int:
        """Countdown units left (`$657B`), derived from the tick counter.

        [C $5A34] D-060: the ROM keeps a 9-unit "minute" counter and a
        255-tick sub-counter; this recovers the former so the OVERRIDE gate
        (`$585E`, only while >= 5) and the two different warning strings can
        key off it exactly as the original does.

        **D-162:** the `- 1` is not a fudge. `$657B` is read *before* being
        decremented and the blast is the wrap that finds it already 0, so the
        full countdown is **ten** wraps while `$657B` only ever shows 9 down
        to 0. With ``AUTO_DESTRUCT_TICKS`` now 10 x 255, ``ceil(t/255) - 1``
        reproduces `$657B` exactly: 2550 ticks -> 9, 255 ticks -> 0.
        """
        if self.auto_destruct_ticks is None:
            return 0
        wraps = -(-self.auto_destruct_ticks // constants.AUTO_DESTRUCT_SUBTICKS)
        return max(0, wraps - 1)
