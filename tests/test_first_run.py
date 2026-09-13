"""The first-run edition question, and the mouse rule that follows from it.

Two things the owner asked for on 2026-08-29, and they are really one thing:
the game asks once, at the very start, whether you want it updated-and-expanded
or as the 1984 disk plays it — and ORIGINAL means *original*, so the mouse goes
with the rest of the additions.

The second half **reverses the call of 2026-08-28**, which had the pointer live
under ORIGINAL on the grounds that an input device is not a rule change.
`test_the_pointer_works_under_the_original_preset` held it to that and is gone;
`test_the_pointer_is_dead_under_the_original_preset` below replaces it, so the
reversal is visible in the history rather than looking like the old rule was
never there.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from alien_remake import settings  # noqa: E402
from alien_remake.core import options  # noqa: E402
from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.render.layout import _WIDTH  # noqa: E402
from alien_remake.render.pygame_app import PygameRenderer  # noqa: E402


def _asking(**kwargs: object) -> tuple[GameFlow, list[dict[str, str]]]:
    """A flow sitting on the question, recording what it commits."""
    saved: list[dict[str, str]] = []
    flow = GameFlow(ask_edition=True, **kwargs)  # type: ignore[arg-type]
    flow.on_options_saved = saved.append
    return flow, saved


def _row_for(profile: str) -> int:
    return next(
        i for i, e in enumerate(options.EDITIONS) if e.profile == profile
    )


# --- it is the first thing, and it decides what follows ----------------------

def test_the_question_comes_before_everything() -> None:
    flow, _ = _asking()
    assert flow.screen is Screen.FIRST_RUN


def test_it_comes_before_the_boot_report_and_hands_over_to_it() -> None:
    """Ordering that matters: the report is the remake's own card, and it would
    be skipped outright if the question simply replaced it."""
    flow, _ = _asking(show_boot=True)
    assert flow.screen is Screen.FIRST_RUN
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.BOOT


def test_without_a_boot_report_it_hands_over_to_the_loader() -> None:
    flow, _ = _asking(show_boot=False)
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.LOADING_MENU


def test_a_normal_launch_does_not_ask() -> None:
    assert GameFlow().screen is not Screen.FIRST_RUN


# --- answering ---------------------------------------------------------------

def test_choosing_original_sets_every_original_value() -> None:
    flow, saved = _asking()
    flow.edition_row = _row_for("original")
    flow.handle(InputEvent.FIRE)

    assert flow.options.profile == "original"
    assert saved, "the answer was applied but never committed"
    for key, value in options.PROFILES["original"].items():
        assert saved[-1][key] == value, key


def test_original_gets_the_full_length_intro() -> None:
    """The owner's words: in original mode, the full length intro happens.

    That is `front_end = classic` — the whole loader chain, the LOADING cards,
    the WELCOME menu and the instructions prompt — rather than the three-screen
    quick boot. Pinned here as well as in the profile because it is the part of
    the answer a player actually *sees*, and a profile edit could drop it
    without anything else noticing.
    """
    flow, saved = _asking()
    flow.edition_row = _row_for("original")
    flow.handle(InputEvent.FIRE)
    assert saved[-1]["front_end"] == "classic"


def test_choosing_updated_turns_the_additions_on() -> None:
    flow, saved = _asking()
    flow.edition_row = _row_for("updated")
    flow.handle(InputEvent.FIRE)
    assert flow.options.profile == "updated"
    assert saved[-1]["crt"] != "off"


def test_the_answer_is_committed_so_it_is_never_asked_twice() -> None:
    """The commit is the whole mechanism: it writes the settings file, and the
    file's existence is what `__main__` reads to decide not to ask again."""
    flow, saved = _asking()
    flow.handle(InputEvent.FIRE)
    assert len(saved) == 1


@pytest.mark.parametrize("keys,expected", [
    ((InputEvent.DOWN,), 1),
    ((InputEvent.RIGHT,), 1),
    ((InputEvent.UP,), len(options.EDITIONS) - 1),
    ((InputEvent.DOWN, InputEvent.DOWN), 0),
])
def test_any_direction_moves_between_the_answers(
    keys: tuple[InputEvent, ...], expected: int
) -> None:
    flow, _ = _asking()
    for key in keys:
        flow.handle(key)
    assert flow.edition_row == expected


def test_the_number_keys_pick_outright() -> None:
    for event, index in ((InputEvent.SELECT_FULL, 0),
                         (InputEvent.SELECT_SHORT, 1)):
        flow, _ = _asking()
        flow.handle(event)
        assert flow.screen is not Screen.FIRST_RUN
        assert flow.options.profile == options.EDITIONS[index].profile


def test_escape_answers_rather_than_escaping() -> None:
    """There is nothing behind this screen and no unanswered state to carry on
    with, so Escape takes the highlighted answer instead of backing out."""
    flow, saved = _asking()
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is not Screen.FIRST_RUN
    assert saved, "escape left the question unanswered"


def test_every_answer_names_a_real_profile() -> None:
    for edition in options.EDITIONS:
        assert edition.profile in options.PROFILES


def test_the_explanation_fits_its_box() -> None:
    """The same failure as DISC-286 and the options help box: an over-long line
    is truncated on screen rather than wrapped, so the sentence just stops."""
    for edition in options.EDITIONS:
        assert len(edition.lines) <= 5, edition.label
        for line in edition.lines:
            assert len(line) <= options.EDITION_WIDTH, line


# --- the mouse ---------------------------------------------------------------

def test_the_pointer_is_dead_under_the_original_preset() -> None:
    """**Reverses 2026-08-28.** The owner's call is that ORIGINAL means the
    original machine too: it had a joystick and a keyboard and no pointing
    device, so a mouse is an addition and goes off with the others.

    Driven through `poll_input` with a real pygame event rather than by calling
    `_pointer_down`, because the gate is at the event — calling the handler
    directly would walk straight past the thing being tested.
    """
    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow = GameFlow()
    flow.screen = Screen.OPTIONS
    try:
        flow.options.apply_profile("original")
        renderer.set_pointer_enabled(
            options.pointer_allowed(flow.options.values)
        )
        renderer.draw(flow)

        region = next(
            r for r, k, i in renderer._hot if k == "option_row" and i == 2
        )
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        pos = (rect.x + region.centerx * scale, rect.y + region.centery * scale)
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}
        ))
        assert renderer.poll_input(flow.screen) == []
        assert flow.options.row == 0, "the mouse still moved the cursor"
    finally:
        renderer.close()


def test_the_pointer_comes_back_off_the_original_preset() -> None:
    """One row away from ORIGINAL is not the original, so the mouse returns —
    the same rule the preset row already reports when it starts reading
    `custom`."""
    values = dict(options.PROFILES["original"])
    assert options.pointer_allowed(values) is False
    values["crt"] = "subtle"
    assert options.pointer_allowed(values) is True


def test_the_pointer_works_while_the_question_is_still_open() -> None:
    """Nothing is decided yet, so the answer itself is always clickable — the
    one case where a dead mouse would strand a player who has only that."""
    assert options.pointer_allowed({}) is True

    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow, _ = _asking()
    try:
        renderer.draw(flow)
        region = next(r for r, k, i in renderer._hot if k == "edition" and i == 1)
        rect = renderer.field_rect()
        scale = max(1, rect.width // _WIDTH)
        renderer._pending_input = []
        renderer._pointer_down(
            (rect.x + region.centerx * scale, rect.y + region.centery * scale),
            flow.screen,
        )
        for event in renderer._pending_input:
            flow.handle(event)
        assert flow.options.profile == options.EDITIONS[1].profile
    finally:
        renderer.close()


def test_both_answers_are_drawn_and_clickable() -> None:
    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow, _ = _asking()
    try:
        renderer.draw(flow)
        kinds = {(k, i) for _, k, i in renderer._hot}
        for i in range(len(options.EDITIONS)):
            assert ("edition", i) in kinds, f"answer {i} is not clickable"
    finally:
        renderer.close()


# --- when the game asks at all -----------------------------------------------

class _Args:
    """Just enough of an argparse namespace for `settings.is_first_run`."""

    def __init__(self, **values: str) -> None:
        for key, value in {**_DEFAULTS, **values}.items():
            setattr(self, key, value)


_DEFAULTS: dict[str, str] = {
    "crt": "off", "front_end": "quick", "jones": "patient",
    "alien_start": "original", "mode": "full", "death": "original",
    "android": "original", "developer": "off", "sound": "game",
    "game_audio": "original",
}


def test_a_machine_with_no_settings_file_is_asked(tmp_path) -> None:
    assert settings.is_first_run(_Args(), _DEFAULTS, tmp_path / "none.toml")


def test_a_machine_with_a_settings_file_is_not_asked(tmp_path) -> None:
    target = tmp_path / "settings.toml"
    target.write_text('crt = "full"\n', encoding="utf-8")
    assert not settings.is_first_run(_Args(), _DEFAULTS, target)


def test_a_corrupt_settings_file_still_counts_as_having_run_before(
    tmp_path,
) -> None:
    """The trap this rule exists to avoid.

    A broken file reads back as *no settings*, so a check written against
    `settings.load()` would decide the player had never run the game and open
    with a question they answered long ago — then overwrite what was left of
    their file with a profile. Existence is the record that they were asked.
    """
    target = tmp_path / "settings.toml"
    target.write_text("this is not toml [[[", encoding="utf-8")
    assert settings.load(target) == {}
    assert not settings.is_first_run(_Args(), _DEFAULTS, target)


def test_a_command_line_option_suppresses_the_question(tmp_path) -> None:
    """`--crt full` must not be overwritten by a profile the player did not
    ask for. The command line wins here as it does everywhere else."""
    args = _Args(crt="full")
    assert not settings.is_first_run(args, _DEFAULTS, tmp_path / "none.toml")


def test_an_unrelated_flag_does_not_suppress_it(tmp_path) -> None:
    """Only the option keys count. `--scale` or `--fullscreen` say nothing
    about which edition you want."""
    args = _Args()
    args.scale = 4  # type: ignore[attr-defined]
    assert settings.is_first_run(args, _DEFAULTS, tmp_path / "none.toml")


# --- layout -------------------------------------------------------------------

def test_the_box_does_not_close_through_its_own_last_line() -> None:
    """It did, at first: the rule was eight rows tall with five lines of text
    inside it, so the bottom edge was drawn straight through "ADDED ANYWHERE."

    The same class of mistake as DISC-286 and the options screen outgrowing its
    footer, and found the same way — by rendering the screen and looking at it.
    Measured rather than eyeballed here, because a screenshot at this size is
    exactly where a one-row overlap hides.
    """
    from alien_remake.render import c64

    renderer = PygameRenderer(scale=3, intro_wav=None)
    flow, _ = _asking()
    try:
        renderer.draw(flow)
        surface = renderer._surface
        ltblue = c64.rgb(c64.LIGHT_BLUE)
        rules = [
            y for y in range(surface.get_height())
            if sum(1 for x in range(8, 312)
                   if surface.get_at((x, y))[:3] == ltblue) > 250
        ]
        assert len(rules) == 2, f"expected a top and bottom rule, got {rules}"
        top, bottom = rules
        # Five lines of explanation start at row 14; the last ends at row 19.
        assert top < 14 * 8, "the top rule is drawn over the text"
        assert bottom >= 19 * 8, "the bottom rule is drawn over the last line"
        # And the footer has to clear the box it sits under.
        assert bottom < 21 * 8, "the box has grown into the footer"
    finally:
        renderer.close()
