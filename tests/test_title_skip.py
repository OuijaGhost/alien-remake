"""Enter or Escape on the title card (owner, 2026-08-29).

The request, in the owner's words: *"if a player hits enter or esc while the
initial Alien egg intro is animating the game jumps to the entire logo revealed
and end state of that screen. This times out as it would normally after the
last letter is revealed unless the player hits enter or esc again and it
instead goes to the next screen."*

So two presses mean two different things, and the first one is the subtle one:
it does **not** leave the screen. It removes the waiting-to-read-it and leaves
the card holding for exactly as long as it would have held anyway — the ROM's
three trailing `delay_long`s at $5EB6/$5EB9/$5EBC.

"In the new version", so ORIGINAL refuses it: the card is 25 seconds because
the disk's is (eight `delay_long`s), and a way to cut it short is an addition
like any other.
"""

from __future__ import annotations

from alien_remake.core import constants  # noqa: E402
from alien_remake.core.flow import GameFlow, InputEvent, Screen  # noqa: E402
from alien_remake.core.options import PROFILES  # noqa: E402


def _title(profile: str = "updated") -> GameFlow:
    flow = GameFlow(current_options=dict(PROFILES[profile]))
    flow.screen = Screen.TITLE
    flow._screen_ticks = 0
    return flow


# --- the first press: reveal, do not leave ------------------------------------

def test_the_first_press_finishes_the_word() -> None:
    flow = _title()
    assert flow.title_letters_shown < 5
    assert flow.skip_card() is True
    assert flow.title_letters_shown == 5


def test_the_first_press_does_not_leave_the_screen() -> None:
    """The part that is easy to get wrong: this is not "skip the title"."""
    flow = _title()
    flow.skip_card()
    assert flow.screen is Screen.TITLE


def test_what_is_left_is_the_card_holding_as_it_always_would() -> None:
    """After the fifth letter the ROM does three more `delay_long`s before it
    returns. A skip fast-forwards *to* that, never past it."""
    flow = _title()
    flow.skip_card()
    remaining = constants.TITLE_TICKS - flow._screen_ticks
    expected = constants.TITLE_TICKS - constants.TITLE_REVEALED_TICKS
    assert remaining == expected
    assert remaining > 0, "the skip swallowed the hold as well as the reveal"


def test_the_card_still_times_out_on_its_own_after_a_skip() -> None:
    flow = _title()
    flow.skip_card()
    for _ in range(constants.TITLE_TICKS):
        flow.tick()
        if flow.screen is not Screen.TITLE:
            break
    assert flow.screen is Screen.GAME_SELECTION


# --- the second press: leave ---------------------------------------------------

def test_a_second_press_goes_to_the_next_screen() -> None:
    flow = _title()
    flow.skip_card()
    assert flow.skip_card() is True
    assert flow.screen is Screen.GAME_SELECTION


def test_a_press_after_the_word_finished_by_itself_also_leaves() -> None:
    """A player who simply waited and then pressed is in the same position as
    one who skipped — the state is what decides, not how it was reached."""
    flow = _title()
    flow._screen_ticks = constants.TITLE_REVEALED_TICKS
    assert flow.skip_card() is True
    assert flow.screen is Screen.GAME_SELECTION


# --- both keys, through the ordinary input path --------------------------------

def test_enter_skips() -> None:
    """Enter arrives as FIRE (`_MENU_KEYS[K_RETURN]`)."""
    flow = _title()
    flow.handle(InputEvent.FIRE)
    assert flow.title_letters_shown == 5
    flow.handle(InputEvent.FIRE)
    assert flow.screen is Screen.GAME_SELECTION


def test_escape_skips_rather_than_abandoning() -> None:
    """Escape here means "get on with it": there is no game yet to back out
    of, and the abandon branch must not see this first."""
    flow = _title()
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is Screen.TITLE
    assert flow.title_letters_shown == 5
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is Screen.GAME_SELECTION


def test_nothing_else_disturbs_the_card() -> None:
    """The title takes no input in the original; the skip is the exception, and
    an exception that swallowed the arrow keys would be a different rule."""
    for event in (InputEvent.UP, InputEvent.DOWN, InputEvent.LEFT,
                  InputEvent.RIGHT, InputEvent.SELECT_FULL):
        flow = _title()
        flow.handle(event)
        assert flow.screen is Screen.TITLE, event
        assert flow.title_letters_shown < 5, event


# --- the original does not have it ---------------------------------------------

def test_the_original_refuses_the_skip() -> None:
    flow = _title("original")
    assert flow.skip_card() is False
    assert flow.title_letters_shown < 5
    assert flow.screen is Screen.TITLE


def test_the_original_keeps_the_full_twenty_five_seconds() -> None:
    """Eight `delay_long`s is what the disk spends here, and Enter must not
    shorten it by a single tick or bring a letter forward."""
    flow = _title("original")
    flow.handle(InputEvent.FIRE)
    assert flow._screen_ticks == 0
    assert flow.title_letters_shown < 5
    assert flow.screen is Screen.TITLE


def test_escape_still_abandons_under_the_original() -> None:
    """Refusing the skip returns the key to its ordinary meaning rather than
    swallowing it: `skip_card` returns False, so the abandon branch still runs
    and Escape backs out to the front end as it did before (DISC-261).

    The first version of this test asserted the screen stayed on TITLE, which
    conflated "the skip did nothing" with "the key did nothing" — they are
    different claims and only the first one is true.
    """
    flow = _title("original")
    flow.handle(InputEvent.ABANDON)
    assert flow.screen is Screen.GAME_SELECTION
    assert flow.title_letters_shown == 5, "off the title the word is complete"


def test_the_skip_asks_the_same_question_the_mouse_does() -> None:
    """One definition of "the original", not two that can drift apart."""
    from alien_remake.core import options

    assert options.is_original(PROFILES["original"]) is True
    assert options.is_original(PROFILES["updated"]) is False
    assert options.pointer_allowed(PROFILES["original"]) is False


def test_the_reveal_point_is_derived_from_the_letter_gap() -> None:
    """Written as `4 * TITLE_LETTER_TICKS`, not as 100, so correcting the gap
    corrects the skip with it."""
    assert constants.TITLE_REVEALED_TICKS == 4 * constants.TITLE_LETTER_TICKS
    flow = _title()
    flow._screen_ticks = constants.TITLE_REVEALED_TICKS
    assert flow.title_letters_shown == 5
    flow._screen_ticks = constants.TITLE_REVEALED_TICKS - 1
    assert flow.title_letters_shown == 4
