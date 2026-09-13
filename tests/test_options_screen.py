"""The remake-only options and manual screens.

Neither screen exists on the disk, so there is no capture to compare against
and nothing here is a fidelity claim. What these tests pin instead is the part
that *can* silently rot: that the options screen, the command-line flags and
the settings file still describe the same four options with the same values,
and that the manual shows all of the loader's text rather than as much of it
as happens to fit.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from alien_remake import settings  # noqa: E402
from alien_remake.core import instructions, options  # noqa: E402
from alien_remake.core.flow import (  # noqa: E402
    GameFlow, InputEvent, Screen,
)
from alien_remake.core.modes import FrontEnd  # noqa: E402
from alien_remake.render.layout import _COLS, _ROWS  # noqa: E402

#: The loader's instruction text is derived from the player's own disk, so a
#: checkout without `out/` has none. The two tests that page *through* that
#: text need it; everything else here works without it.
needs_instructions = pytest.mark.skipif(
    not instructions.pages(), reason="MENU1.prg not extracted"
)


# --- the three descriptions of the same four options must agree -------------

def _real_specs() -> list[options.OptionSpec]:
    """Every row except the preset, which is derived rather than stored."""
    return [s for s in options.OPTION_SPECS if s.key != options.PRESET_KEY]


def test_every_option_is_a_settings_key() -> None:
    """An option the settings file cannot carry would not survive a restart."""
    for spec in _real_specs():
        assert spec.key in settings.KEYS, spec.key


def test_the_preset_row_is_not_itself_a_setting() -> None:
    """It reads back from the other rows, so storing it would give the file two
    sources of truth for the same thing."""
    assert options.PRESET_KEY not in settings.KEYS
    assert options.PRESET_KEY not in options.OptionsModel().as_dict()


def test_every_option_matches_its_command_line_flag() -> None:
    """Same values, same order, as the flag each option mirrors.

    Read off the real parser rather than restated here: a list copied into the
    test is a list that agrees with itself and nothing else.
    """
    from alien_remake.__main__ import _build_parser

    actions = {a.dest: a for a in _build_parser()._actions}
    for spec in _real_specs():
        assert spec.key in actions, f"no --flag for option {spec.key}"
        assert tuple(actions[spec.key].choices or ()) == spec.values, spec.key


def test_help_lines_fit_the_box() -> None:
    """Over-long help is truncated on screen, not wrapped, so it must fit."""
    for spec in options.OPTION_SPECS:
        assert len(spec.help_text) <= 5, spec.key
        for line in spec.help_text:
            assert len(line) <= options.HELP_WIDTH, (spec.key, line)


# --- the model --------------------------------------------------------------

def test_cursor_and_values_wrap_both_ways() -> None:
    model = options.OptionsModel()
    first = model.spec.key
    model.move(-1)
    assert model.spec.key == options.OPTION_SPECS[-1].key
    model.move(1)
    assert model.spec.key == first

    model.row = 1                      # the first real setting, not the preset
    spec = model.spec
    start = model.values[spec.key]
    for _ in spec.values:
        model.change(1)
    assert model.values[spec.key] == start, "a full cycle returns to the start"
    assert model.change(-1) == spec.values[-1]


def test_model_opens_on_what_is_running_not_the_defaults() -> None:
    model = options.OptionsModel({"crt": "full", "jones": "easy"})
    assert model.values["crt"] == "full"
    assert model.values["jones"] == "easy"
    # A value the running game cannot actually be in falls back rather than
    # putting an unselectable string on screen.
    assert options.OptionsModel({"crt": "nonsense"}).values["crt"] == "off"


# --- persistence ------------------------------------------------------------

def test_settings_round_trip(tmp_path) -> None:
    target = tmp_path / "settings.toml"
    values = {"crt": "full", "front_end": "classic",
              "jones": "easy", "alien_start": "random"}
    assert settings.save(values, target) == target
    assert settings.load(target) == values


def test_saving_never_raises_on_an_unwritable_path(tmp_path) -> None:
    """An options file that cannot be written costs the persistence, not the
    session it was set in — the screen is still usable on a read-only install."""
    blocker = tmp_path / "file"
    blocker.write_text("not a directory", encoding="utf-8")
    assert settings.save({"crt": "off"}, blocker / "settings.toml") is None


# --- the flow ---------------------------------------------------------------

def _at_selection() -> GameFlow:
    flow = GameFlow()
    flow.screen = Screen.GAME_SELECTION
    return flow


def test_options_screen_opens_changes_and_reports_on_leaving() -> None:
    flow = _at_selection()
    saved: list[dict[str, str]] = []
    flow.on_options_saved = saved.append

    flow.handle(InputEvent.SELECT_OPTIONS)
    assert flow.screen is Screen.OPTIONS
    assert flow.options.spec.key == options.PRESET_KEY, "the preset leads"

    flow.options.row = 1
    assert flow.options.spec.key == "crt"
    flow.handle(InputEvent.RIGHT)
    assert flow.options.values["crt"] == "subtle"
    assert saved and saved[-1]["crt"] == "subtle", "applied as it changes"

    flow.handle(InputEvent.DOWN)
    assert flow.options.spec.key == "front_end"

    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.GAME_SELECTION
    assert saved[-1]["crt"] == "subtle"


def test_escape_leaves_the_options_screen_without_dropping_a_game() -> None:
    """ABANDON on OPTIONS returns to the selection screen. It must not take
    the `abandon()` path, which is for a game in progress."""
    flow = _at_selection()
    flow.handle(InputEvent.SELECT_OPTIONS)
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is Screen.GAME_SELECTION


def test_front_end_change_rebuilds_the_timed_transition_table() -> None:
    """Switching front ends must bring the timing table with it, or a boot
    sits forever on a card the other chain never times."""
    flow = GameFlow(front_end=FrontEnd.QUICK)
    before = dict(flow._timed_next)
    flow.set_front_end(FrontEnd.CLASSIC)
    assert flow.front_end is FrontEnd.CLASSIC
    assert flow._timed_next != before
    assert Screen.LOADING_PLAY in flow._timed_next


@needs_instructions
def test_manual_pages_through_the_text_then_the_legend_then_returns() -> None:
    flow = _at_selection()
    flow.handle(InputEvent.SELECT_INSTRUCTIONS)
    assert flow.screen is Screen.MANUAL
    assert flow.manual_page == 0
    assert not flow.manual_showing_legend

    text_pages = len(instructions.pages())
    assert flow.manual_pages() == text_pages + 1, "the legend is the last page"

    for _ in range(text_pages):
        flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.MANUAL
    assert flow.manual_showing_legend, "the deck-plan key comes after the text"

    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.GAME_SELECTION
    assert flow.manual_page == 0, "reopening starts at the beginning"


@needs_instructions
def test_manual_pages_backwards_without_leaving() -> None:
    flow = _at_selection()
    flow.handle(InputEvent.SELECT_INSTRUCTIONS)
    flow.handle(InputEvent.FIRE)
    flow.handle(InputEvent.FIRE)
    assert flow.manual_page == 2
    flow.handle(InputEvent.LEFT)
    assert flow.manual_page == 1
    for _ in range(5):
        flow.handle(InputEvent.LEFT)
    assert flow.manual_page == 0, "backing off page one stops, it does not wrap"
    assert flow.screen is Screen.MANUAL


def test_the_manual_is_reachable_only_from_the_selection_screen() -> None:
    """The two new keys are additions to one screen, not global shortcuts."""
    flow = GameFlow()
    flow.screen = Screen.NOTICE
    flow.handle(InputEvent.SELECT_OPTIONS)
    assert flow.screen is not Screen.OPTIONS


# --- the regression this work uncovered -------------------------------------

def test_no_instruction_page_is_taller_than_the_screen_can_draw() -> None:
    """The loader's longest pages are 24 lines.

    Both viewers draw from row 0 so all 24 fit above a one-row footer. When
    they started at row 1 the last two lines of pages 5-8 were cut mid-sentence
    and nothing said so.
    """
    book = instructions.pages()
    if not book:                       # a checkout without out/ still runs
        return
    drawable = _ROWS - 1
    assert max(len(page) for page in book) <= drawable
    for page in book:
        for line in page:
            assert len(line) <= _COLS


# --- the renderer side, which the model tests cannot reach -------------------

def test_changing_every_option_keeps_the_renderer_drawing() -> None:
    """Drive the options screen through the *real* renderer, not just the model.

    The model tests all pass while the screen is unusable: they never draw a
    frame. The first version of `set_crt` assigned the CRT *settings* into the
    slot holding the CRT *processor*, so the next frame called `advance()` on a
    dataclass and the program died the moment a player pressed left or right.
    Nothing here caught it, because nothing here had drawn anything.

    So: cycle every value of every option, applying each through the same
    setters the app wires up, and draw a frame after each one.
    """
    from alien_remake.core.modes import FrontEnd as _FE
    from alien_remake.render.crt import preset
    from alien_remake.render.pygame_app import PygameRenderer

    gui = PygameRenderer(scale=1, intro_wav=None)
    try:
        flow = _at_selection()

        def apply(values: dict[str, str]) -> None:
            gui.set_crt(preset(values["crt"]))
            front = (_FE.CLASSIC if values["front_end"] == "classic"
                     else _FE.QUICK)
            flow.set_front_end(front)
            gui.set_front_end(front)

        flow.on_options_saved = apply
        flow.handle(InputEvent.SELECT_OPTIONS)
        gui.draw(flow)

        for row, spec in enumerate(options.OPTION_SPECS):
            flow.options.row = row
            for _ in spec.values:                  # a full cycle of each row
                flow.handle(InputEvent.RIGHT)
                gui.draw(flow)                     # the frame that used to die
            assert flow.screen is Screen.OPTIONS, "changing a value must not leave"

        # And the game screen too: that is where the CRT actually processes.
        flow.handle(InputEvent.FIRE)
        assert flow.screen is Screen.GAME_SELECTION
        gui.draw(flow)
    finally:
        gui.close()


# --- the widened pools, and the preset --------------------------------------

def _openings(death: str, android: str, n: int = 300) -> tuple[set, set]:
    """Who dies and who is the android across many seeds."""
    import random

    from alien_remake.core.modes import AndroidVariant, DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    dv = {"random": DeathVariant.ORIGINAL, "any": DeathVariant.RANDOM,
          "fixed": DeathVariant.FIXED}[death]
    av = {"rom": AndroidVariant.ORIGINAL, "any": AndroidVariant.RANDOM}[android]
    dead, droid = set(), set()
    for seed in range(n):
        sim = Simulation(mode=GameMode.FULL, death_variant=dv,
                         android_variant=av, rng=random.Random(seed))
        dead.add(sim.state.opening_dead_crew_id)
        droid.add(sim.state.android_id)
    return dead, droid


def test_the_rom_pools_are_the_rom_tables() -> None:
    """`$50EC` is three names and `$50FC` is four. Widening the added rule must
    not have widened the original underneath it."""
    from alien_remake.core import constants

    dead, droid = _openings("random", "rom")
    assert dead == set(constants.OPENING_VICTIM_CANDIDATES)
    assert droid <= set(constants.ANDROID_CANDIDATES)


def test_any_draws_the_whole_crew() -> None:
    from alien_remake.core.crew import ROSTER

    everyone = {entry[0] for entry in ROSTER}
    dead, droid = _openings("any", "any")
    assert dead == everyone, "the added rule must reach all seven"
    assert droid == everyone


def test_the_android_is_never_the_opening_victim() -> None:
    """The ROM re-rolls while the android equals the victim (`CMP $64C2`).
    Widening the pool must not lose that — a dead android is no mystery."""
    import random

    from alien_remake.core.modes import AndroidVariant, DeathVariant, GameMode
    from alien_remake.core.sim import Simulation

    for seed in range(400):
        sim = Simulation(mode=GameMode.FULL, death_variant=DeathVariant.RANDOM,
                         android_variant=AndroidVariant.RANDOM,
                         rng=random.Random(seed))
        assert sim.state.android_id != sim.state.opening_dead_crew_id


def test_original_preset_is_every_rom_value() -> None:
    """The point of the switch: nothing remake-only survives it.

    Checked against the *specs* rather than a copied list, so adding an option
    without deciding what `original` means for it fails here.
    """
    model = options.OptionsModel()
    model.apply_profile("original")
    assert model.profile == "original"
    for spec in _real_specs():
        assert spec.key in options.PROFILES["original"], (
            f"{spec.key} has no ORIGINAL value — decide what the switch does"
        )
        assert model.values[spec.key] in spec.values


def test_both_profiles_cover_every_row() -> None:
    keys = {s.key for s in _real_specs()}
    for name, profile in options.PROFILES.items():
        assert set(profile) == keys, f"{name} does not cover every option"


def test_the_preset_reads_back_from_the_rows_it_set() -> None:
    model = options.OptionsModel()
    model.apply_profile("original")
    assert model.displayed(options.OPTION_SPECS[0]) == "original"
    # Change one row by hand and the preset stops claiming a profile.
    model.row = 1
    model.change(1)
    assert model.profile == options.CUSTOM


def test_changing_the_preset_row_rewrites_the_others() -> None:
    flow = _at_selection()
    flow.handle(InputEvent.SELECT_OPTIONS)
    assert flow.options.spec.key == options.PRESET_KEY
    flow.handle(InputEvent.LEFT)
    assert flow.options.values == options.PROFILES["original"]
    flow.handle(InputEvent.RIGHT)
    assert flow.options.values == options.PROFILES["updated"]


# --- the settings-file migration --------------------------------------------

def test_a_version_1_file_migrates_to_values_the_screen_can_select(tmp_path) -> None:
    """Every v1 spelling must land on a real v2 value.

    This is the test that was missing: the first migration table mapped
    `android = "rom"` but not `android = "any"`, so a real settings file
    carrying `any` survived load unchanged, matched no branch, and silently
    fell back to the original's four-name draw — losing the setting the player
    had chosen.
    """
    target = tmp_path / "v1.toml"
    target.write_text(
        'crt = "subtle"\n'
        'front_end = "quick"\n'
        'jones = "patient"\n'
        'alien_start = "airlock"\n'
        'death = "any"\n'
        'android = "any"\n',
        encoding="utf-8",
    )
    loaded = settings.load(target)
    valid = {s.key: s.values for s in options.OPTION_SPECS}
    for key, value in loaded.items():
        assert value in valid[key], f"{key}={value!r} is not selectable"
    # `any` named the widened draw in v1 and `random` names it in v2.
    assert loaded["death"] == "random"
    assert loaded["android"] == "random"
    assert loaded["alien_start"] == "original"


def test_version_1_death_random_meant_the_original_draw(tmp_path) -> None:
    """The rename that made versioning necessary.

    v1 `random` meant the original's short list; v2 `random` means the whole
    crew. Read without migrating, an existing player would start losing crew
    members the original never kills.
    """
    target = tmp_path / "v1.toml"
    target.write_text('death = "random"\n', encoding="utf-8")
    assert settings.load(target)["death"] == "original"


def test_a_version_2_file_is_left_alone(tmp_path) -> None:
    target = tmp_path / "v2.toml"
    settings.save({"death": "random", "android": "random"}, target)
    assert f"{settings.VERSION_KEY} = {settings.VERSION}" in target.read_text(
        encoding="utf-8"
    )


def test_a_version_2_file_migrates_game_audio_sampled_to_enhanced(tmp_path) -> None:
    """The rename that made version 3 necessary (2026-09-05): `sampled` no
    longer says the option also runs a loudness spec check and is where new
    audio files go, so it became `enhanced`. A v2 file naming the old value
    must still select something real."""
    target = tmp_path / "v2.toml"
    target.write_text('version = 2\ngame_audio = "sampled"\n', encoding="utf-8")
    loaded = settings.load(target)
    assert loaded["game_audio"] == "enhanced"
    valid = {s.key: s.values for s in options.OPTION_SPECS}
    assert loaded["game_audio"] in valid["game_audio"]


def test_fixed_is_hidden_unless_developer_mode_is_on() -> None:
    model = options.OptionsModel()
    death = next(s for s in options.OPTION_SPECS if s.key == "death")
    assert "fixed" not in model.choices(death)
    model.values["developer"] = "on"
    assert "fixed" in model.choices(death)


def test_a_value_already_set_is_never_yanked_away() -> None:
    """A file written in developer mode, opened without it, keeps its value —
    hiding a choice must not silently change one."""
    model = options.OptionsModel({"death": "fixed", "developer": "off"})
    death = next(s for s in options.OPTION_SPECS if s.key == "death")
    assert model.values["death"] == "fixed"
    assert "fixed" in model.choices(death)


# --- the layout, which grew past its own footer once ------------------------

def _front(screen: Screen):
    """A renderer sitting on one front-end screen, drawn once."""
    from alien_remake.render.pygame_app import PygameRenderer

    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = screen
    renderer.draw(flow)
    return renderer, flow



def test_every_option_row_clears_the_footer() -> None:
    """Adding rows used to push the last one onto the hint line.

    The audio rows took the list to ten and the bottom row started drawing over
    "UP/DOWN PICK" — found by looking at a screenshot, which is not a method.
    The rows are recorded as clickable regions, so their positions can simply
    be asserted.
    """
    from alien_remake.render.layout import _ROWS

    renderer, flow = _front(Screen.OPTIONS)
    try:
        rows = [r for r, k, _ in renderer._hot if k == "option_row"]
        assert rows, "no option rows were drawn"
        hints_row = _ROWS - 3          # "UP/DOWN PICK ..." sits here
        lowest = max(r.bottom for r in rows)
        assert lowest <= hints_row * 8, (
            f"an option row reaches y={lowest}, over the hints at "
            f"y={hints_row * 8}"
        )
    finally:
        renderer.close()


def test_the_help_box_does_not_reach_the_first_option_row() -> None:
    """The other end of the same squeeze: the box grew when the list moved up."""
    renderer, flow = _front(Screen.OPTIONS)
    try:
        rows = [r for r, k, _ in renderer._hot if k == "option_row"]
        top = min(r.top for r in rows)
        # The box is drawn from row 1 and is eight cells tall (2026-09-03,
        # trimmed from nine to make room for the eleventh option row).
        assert top >= 9 * 8, f"the first option row at y={top} overlaps the box"
    finally:
        renderer.close()


def test_the_screen_still_fits_if_a_row_is_added() -> None:
    """The guard that makes the two above useful.

    They pass for today's ten rows; this says what happens at eleven, so the
    next person to add an option is told by a test rather than by a screenshot.
    """
    from alien_remake.render.frontend import _OPTION_FIRST_ROW
    from alien_remake.render.layout import _ROWS

    rows_needed = len(options.OPTION_SPECS) + 1        # +1 for the preset rule
    last_row = _OPTION_FIRST_ROW + rows_needed - 1
    assert last_row < _ROWS - 3, (
        f"{len(options.OPTION_SPECS)} options need row {last_row}; the hints "
        f"are at {_ROWS - 3}. Move _OPTION_FIRST_ROW up or shrink the help box."
    )
