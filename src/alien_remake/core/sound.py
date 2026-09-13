"""Sound cues the world raises, and the gate that decides if you hear them.

The C64 game does not have a sound *engine* — it writes the SID directly at
four call sites (D-088). Two of those sites are conditional in ways that are
part of the game's feel rather than its simulation, so this module keeps the
two concerns apart: :class:`SoundCue` records that the machine reached one of
those sites, and :func:`audible` reproduces the ROM's own tests for whether it
actually made a noise.

Why the gate lives here and not in the simulation
-------------------------------------------------
`$8CE1 CPY $64FB / BNE $8D26` compares the victim's slot against `$64FB`, the
**currently selected character** — a UI value. The attack still happens when
you have someone else selected; you simply do not get the siren or the
animation (D-090). So the world raises the cue unconditionally and the
presentation layer, which is the only thing that knows the selection, decides.
The player's report of this ("the alert only sounds when you have selected the
crew member in that room") is exactly the observable shape of that test.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Effect names, matching :data:`alien_remake.audio.sfx.EFFECTS`.
GRILLE = "grille"
MOVEMENT = "movement"
AIRLOCK = "airlock"
ATTACK_ALERT = "attack_alert"
#: The tracker readout's ping. **[C $43CD]** named by the game itself — its
#: DECK PLAN KEY screen plays this sound under the caption "THIS IS THE SOUND
#: OF THE TRACKER ALARM" (D-093). Armed at `$8DF6` (`LDA #$21 / STA $64B6`),
#: silenced by `reset_attack_state ($8C82)`.
TRACKER_ALARM = "tracker_alarm"
#: The ambient pulse under the play screen — "THE HEARTBEAT OF THE CURRENT
#: CHARACTER". Not a cue: it runs continuously and its *rate* carries the
#: information (`fear_alert $4E16`), so the renderer loops it rather than
#: triggering it.
HEARTBEAT = "heartbeat"


@dataclass(frozen=True)
class SoundCue:
    """One SID call site the machine reached this tick.

    ``crew_id`` is set only for :data:`ATTACK_ALERT`, where it is the victim
    whose slot `$8CE1` compares against the selection.
    """

    effect: str
    crew_id: str | None = None


def audible(cue: SoundCue, selected_id: str | None, *, attacking: bool) -> bool:
    """Would the real machine have made this sound, given the UI state?

    Two ROM tests, both citable:

    * **[C $8CE1]** the attack siren fires only when the victim is the selected
      character (D-090).
    * **[C $4E42 / $4E5C]** both blip routines open ``LDA $64BB / BNE <rts>``,
      so the movement and grille blips are **muted for the duration of an
      attack sequence** — the siren is heard alone (D-088). ``attacking`` is
      this remake's `$64BB`.

    The airlock effect (``blowlock_sfx $5904``) has no such guard and always
    sounds.
    """
    if cue.effect == ATTACK_ALERT:
        return cue.crew_id is not None and cue.crew_id == selected_id
    if cue.effect in (MOVEMENT, GRILLE):
        return not attacking
    if cue.effect == TRACKER_ALARM:
        # `$8DF0 LDA $6562 / BEQ $8DF6` — armed only while no attack sequence
        # is running. Deliberately **not** selection-gated: unlike the siren,
        # the alarm sounds whoever you have selected, which is what makes it
        # usable as a warning.
        return not attacking
    return True
