"""Pre-rendered sound effects: same audio, without the first-use hitch (DISC-254).

Synthesising each clip on first use is correct but slow — measured at **809 ms
for the airlock**, whose clip is nine seconds long, landing exactly as the
player commits to blowing the lock. `--derive-assets` renders them once instead.

The load-bearing test here is
:func:`test_the_cached_clip_is_the_same_audio_as_synthesising` — a cache that
plays something *different* would be a silent fidelity bug, and the whole point
of deriving from the ROM's own SID writes would be lost.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.audio import sfx
from alien_remake.core import constants as K


def test_export_writes_one_clip_per_effect_and_per_heartbeat_rate(
    tmp_path: Path,
) -> None:
    written = sfx.export_all(tmp_path)
    names = {p.name for p in written}

    for effect in sfx.EFFECTS:
        if effect == "heartbeat":
            continue
        assert f"sfx_{effect}.wav" in names

    # `fear_alert ($4E16)` buckets composure with `min(composure, 4)`, so the
    # eleven fear values collapse to four dividers — four files, not eleven.
    dividers = {K.heartbeat_divider(c) for c in range(11)}
    assert len(dividers) == 4
    for divider in dividers:
        assert f"sfx_heartbeat_{divider}.wav" in names
    assert len(written) == len(sfx.EFFECTS) - 1 + len(dividers)


def test_the_cached_clip_is_the_same_audio_as_synthesising(tmp_path: Path) -> None:
    """A cache that plays a different sound is worse than no cache at all."""
    sfx.export_all(tmp_path)
    rate = sfx.EXPORT_SAMPLE_RATE

    for effect in sfx.EFFECTS:
        if effect == "heartbeat":
            continue
        on_disk = (tmp_path / f"sfx_{effect}.wav").read_bytes()
        fresh = sfx.wav_bytes(sfx.render(effect, sample_rate=rate), rate)
        assert on_disk == fresh, f"{effect}: the exported wav is not the ROM's sound"

    for composure in (0, 2, 3, 4):
        divider = K.heartbeat_divider(composure)
        on_disk = (tmp_path / f"sfx_heartbeat_{divider}.wav").read_bytes()
        fresh = sfx.wav_bytes(
            sfx.render("heartbeat", sample_rate=rate, composure=composure), rate
        )
        assert on_disk == fresh, f"heartbeat@{divider}: exported wav differs"


def test_every_pulse_clip_is_a_whole_number_of_beats() -> None:
    """A loop whose length is not a whole beat drifts a little every repeat.

    `render_pulse` emits `periods` blocks of exactly `per_beat` samples, so the
    seam lands on a beat boundary. Asserted because this is the property that
    makes `play(loops=-1)` sound continuous rather than stuttering — and the
    tempo complaint that prompted DISC-254 looked exactly like a broken seam
    before it turned out to be a restart.
    """
    rate = sfx.EXPORT_SAMPLE_RATE
    for composure in (0, 2, 3, 4):
        divider = K.heartbeat_divider(composure)
        pcm = sfx.render("heartbeat", sample_rate=rate, composure=composure)
        samples = len(pcm) // 2
        per_beat = round(divider * rate / sfx.IRQ_HZ)
        assert samples % per_beat == 0, (
            f"heartbeat@{divider}: {samples} samples is "
            f"{samples / per_beat:.3f} beats — the loop seam falls mid-beat"
        )


def test_the_renderer_falls_back_to_synthesis_when_no_clip_is_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The export is an optimisation, never a requirement."""
    from alien_remake import assets
    from alien_remake.render.pygame_app import PygameRenderer

    monkeypatch.setattr(assets, "asset_roots", lambda: (tmp_path,))
    r = PygameRenderer(scale=2, tiles=None, intro_wav=None)
    try:
        assert assets.find("sfx_airlock.wav") is None
        assert r._sound("airlock") is not None, "synthesis fallback broke"
    finally:
        r.close()
