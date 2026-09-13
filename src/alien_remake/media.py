"""What you can replace, where it goes, and whether it is there.

A dictionary of the game's replaceable media. It exists because the answer to
"can I change that, and what do I call the file?" was spread across three
modules and a README, and a player should not have to read source to find out.

**Generated, not written.** Every row is derived from the code that actually
loads the thing — `assets.KNOWN_ASSETS` for the derived data, `audio.sfx` and
`audio.samples` for the sounds — so a slot cannot be added without appearing
here, and this file cannot describe a slot that no longer exists. A
hand-maintained list of file names is a list that goes stale the first time
somebody renames one.

It also states plainly what is **not** replaceable yet. The graphics, the deck
layouts, the crew portraits and the glyphs all come out of the disk image and
have no override path today; saying so is more useful than leaving them off the
list and letting a reader assume they were missed.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

from . import assets
from .core.crew import ROSTER
from .core.nostromo import DECK_NAMES
from .audio import samples, sfx


@dataclass(frozen=True)
class Slot:
    """One thing that can be supplied or replaced."""

    key: str
    kind: str
    where: str
    what: str
    how: str = ""
    #: Files found for it right now, if it is the kind that can be counted.
    present: tuple[Path, ...] = ()
    #: What happens if you put your **own** file here instead of the derived
    #: one. Empty where substituting makes no sense, or where the path exists
    #: but is not documented yet — an empty string is the honest answer for a
    #: slot nobody has worked out the story for, and it keeps this from
    #: implying every derived file is swappable.
    swap: str = ""

    @property
    def status(self) -> str:
        if not self.present:
            return "absent"
        return "present" if len(self.present) == 1 else f"{len(self.present)} files"


def _sound_player() -> samples.SamplePlayer:
    directory = next(
        (root / samples.DIRECTORY for root in assets.asset_roots()
         if (root / samples.DIRECTORY).is_dir()),
        None,
    )
    return samples.SamplePlayer(directory)


def slots() -> list[Slot]:
    """Every replaceable slot, with what is currently in it."""
    out: list[Slot] = []

    # --- derived from your own disk image -----------------------------------
    for key, parts, why, how in assets.KNOWN_ASSETS:
        found = assets.find(*parts)
        out.append(Slot(
            key=key,
            kind="derived",
            where="/".join(parts),
            what=why,
            how=how,
            present=(found,) if found is not None else (),
            swap=SWAPPABLE.get(key, ""),
        ))

    # --- portraits you supply (D1) -------------------------------------------
    # Enumerated from the roster rather than listed, so a crew change cannot
    # leave this describing six portraits or eight.
    for crew_id, name, _role in ROSTER:
        found = portrait_path(crew_id)
        out.append(Slot(
            key=f"portrait/{crew_id}",
            kind="portrait (yours)",
            where=f"{PORTRAIT_DIR}/{crew_id}{PORTRAIT_EXT}",
            what=f"{name} on the selection screen and the CONTROL panel; "
                 f"{PORTRAIT_SIZE[0]}x{PORTRAIT_SIZE[1]}, transparency kept",
            present=(found,) if found is not None else (),
        ))

    # --- a charset you supply (D2) -------------------------------------------
    glyphs = assets.find(GLYPH_DIR, GLYPH_FILE)
    out.append(Slot(
        key="glyphs",
        kind="glyphs (yours)",
        where=f"{GLYPH_DIR}/{GLYPH_FILE}",
        what="the 8K $2000-$3FFF charset region, or a whole ALIEN prg to take "
             "it from; drawn in place of the game's own letters and map tiles",
        present=(glyphs,) if glyphs is not None else (),
    ))

    # --- deck plans you supply (D3) -------------------------------------------
    for deck, name in sorted(DECK_NAMES.items()):
        found = map_path(deck)
        out.append(Slot(
            key=f"map/{map_name(deck)}",
            kind="map art (yours)",
            where=f"{MAP_DIR}/{map_name(deck)}{MAP_EXT}",
            what=f"the {name} plan; {MAP_SIZE[0]}x{MAP_SIZE[1]}, drawn in "
                 f"place of the deck the game builds from its own screen codes",
            present=(found,) if found is not None else (),
        ))

    # --- sprites you supply (D4) ----------------------------------------------
    for index in sorted(SPRITE_ROLES):
        found = sprite_path(index)
        out.append(Slot(
            key=f"sprite/{index}",
            kind="sprite (yours)",
            where=f"{SPRITE_DIR}/{index}{SPRITE_EXT}",
            what=f"{SPRITE_ROLES[index]}; "
                 f"{SPRITE_SIZE[0]}x{SPRITE_SIZE[1]}, transparency kept",
            present=(found,) if found is not None else (),
        ))
    title = title_art_path()
    out.append(Slot(
        key="title_egg",
        kind="sprite (yours)",
        where=TITLE_ART,
        what=f"the title screen's alien egg; "
             f"{TITLE_ART_SIZE[0]}x{TITLE_ART_SIZE[1]}, transparent around it",
        present=(title,) if title is not None else (),
    ))

    # --- sounds you supply ---------------------------------------------------
    player = _sound_player()
    for effect in sfx.EFFECTS:
        out.append(Slot(
            key=effect,
            kind="sound (the game's own)",
            where=f"{samples.DIRECTORY}/{effect}.wav  or  "
                  f"{samples.DIRECTORY}/{effect}/*.wav",
            what="replaces the emulated SID effect when GAME AUDIO is 'sampled'",
            present=tuple(player.variants(effect)),
        ))
    for cue in samples.UI_CUES:
        out.append(Slot(
            key=cue,
            kind="sound (added)",
            where=f"{samples.DIRECTORY}/{cue}.wav  or  "
                  f"{samples.DIRECTORY}/{cue}/*.wav",
            what="an interface sound the original does not have; needs SOUND 'all'",
            present=tuple(player.variants(cue)),
        ))
    return out


#: **D1 — crew portraits.** Where a supplied portrait goes, and how big it is.
#:
#: Kept here rather than in the renderer so this module stays the single place
#: that knows where a replaceable file lives: the loader imports these, so the
#: dictionary cannot describe a folder nothing reads.
PORTRAIT_DIR = "portraits"
PORTRAIT_EXT = ".png"

#: The canvas, in pixels. **A C64 hardware sprite is 24x21**, which is what the
#: decoded portrait table positions and what the selection screen spaces 40px
#: apart — so a supplied image is scaled to it rather than drawn at its own
#: size. Drawn native, a large portrait would simply cover its neighbours, and
#: the layout it would break is decoded (`_PORTRAIT_X`), not a choice.
PORTRAIT_SIZE = (24, 21)


def portrait_path(crew_id: str) -> Path | None:
    """A supplied portrait for one crew member, or ``None``.

    The same root-priority search as every other asset, so a portrait in a root
    ahead of `out/` wins — see :func:`~alien_remake.assets.find`.
    """
    return assets.find(PORTRAIT_DIR, f"{crew_id}{PORTRAIT_EXT}")


#: **D2 — the character set.** A replacement charset was always *possible* —
#: `assets.find` takes the first `charset.bin` on the root path — but the only
#: way to use one was to overwrite the derived artefact, which throws away the
#: thing you extracted from your own disk to make room for the thing you drew.
#: This is a separate name, searched first, so both can exist at once.
GLYPH_DIR = "glyphs"
GLYPH_FILE = "charset.bin"


def charset_path() -> Path | None:
    """The charset to draw with: your own if you supplied one, else derived.

    Either form the loader already accepts — the 8 KiB `$2000-$3FFF` region
    dump, or a whole `ALIEN` PRG it can pull the region out of.
    """
    return assets.find(GLYPH_DIR, GLYPH_FILE) or assets.find(GLYPH_FILE)


#: **D3 — the deck plans.** One image per deck, replacing the map the game
#: draws from its own screen codes.
MAP_DIR = "map"
MAP_EXT = ".png"

#: The map field, in pixels: `_MAP_COLS` (30) glyphs across by the 18 rows of a
#: deck plan, at 8x8 each. A supplied image is scaled to it — the panel starts
#: at column 30 and the status rows below are drawn live, so anything larger
#: would be drawing over screen furniture rather than over the map.
MAP_SIZE = (240, 144)


def map_name(deck: int) -> str:
    """The filename stem for one deck — `upper`, `middle`, `lower`.

    Taken from :data:`~alien_remake.core.nostromo.DECK_NAMES` rather than
    written out again, so a deck cannot be renamed in one place only.
    """
    return DECK_NAMES.get(deck, f"deck{deck}").split()[0].lower()


def map_path(deck: int) -> Path | None:
    """A supplied deck plan, or ``None``."""
    return assets.find(MAP_DIR, f"{map_name(deck)}{MAP_EXT}")


#: **D4 — the sprites, and only the sprites.**
#:
#: The owner's ruling on D4 (2026-08-29) is what makes this safe to build:
#: *"the layout should be the same. This is just to replace the graphics that
#: make the layout. These should be interchangeable with the original game and
#: not change the gameplay in any way."* So a file here changes pixels and
#: nothing else — never a position, never a size, never a rule. Every sprite is
#: still drawn where the decoded tables put it, at the size the VIC gives it.
#:
#: **Addressed by slot index, not by an invented name.** The alien alone is 21
#: tiles (a 2x3 grid of X/Y-expanded sprites over four animation frames), and
#: naming those would mean making up a taxonomy the ROM does not have. The
#: index is what the machine uses; :data:`SPRITE_ROLES` is what says which is
#: which, and `--media` prints it beside each one.
SPRITE_DIR = "sprites"
SPRITE_EXT = ".png"

#: How strongly a *varying* ROM colour is washed over supplied art, 0-255.
#: Half strength: enough that the heartbeat still reads as a beat and a duct
#: still reads as a duct, without burying the picture underneath. See
#: `PygameRenderer._signalled` for why only some colours get this treatment.
SIGNAL_WASH = 128

#: A C64 hardware sprite: 24x21. Supplied art is scaled to it, for the same
#: reason the portraits are — the positions it lands on are decoded.
SPRITE_SIZE = (24, 21)


def sprite_path(index: int) -> Path | None:
    """A supplied image for one sprite slot, or ``None``."""
    return assets.find(SPRITE_DIR, f"{index}{SPRITE_EXT}")


def _sprite_roles() -> dict[int, str]:
    """Which drawn sprite is which, by slot index.

    Written out here rather than imported, because `render.play` — where the
    decoded tables live — imports pygame, and this module is deliberately
    headless so `--media` works on a machine with no display.
    ``test_the_sprite_roles_match_the_decoded_tables`` reads those tables and
    fails if these drift from them, so the copy cannot rot quietly.

    The seven portrait slots are deliberately **absent**: they are addressed by
    crew id under `portraits/` (D1), and offering the same picture two ways is
    how two files end up disagreeing about Ripley.
    """
    roles: dict[int, str] = {24: "the selected crew member's map marker"}
    # `_POINTER_FRAMES` — the INDICATE animation, $BC $BB $BA $B9.
    for n, index in enumerate((28, 27, 26, 25), start=1):
        roles[index] = f"the INDICATE pointer, frame {n} of 4"
    # `_JONES_FRAMES` — $C4..$C8, the cat's run.
    for n, index in enumerate(range(36, 41), start=1):
        roles[index] = f"Jones crossing the screen, frame {n} of 5"
    # `_ATTACK_SLOTS` + `_ATTACK_STATIC_SLOT` — the attacking alien is a 2x3
    # grid of expanded sprites, five of whose six cells animate over four
    # frames. Named by where they sit rather than by what they look like,
    # because only the whole grid is a picture of anything.
    corners = {0: "top left", 4: "top right", 8: "middle left",
               12: "middle right", 16: "bottom left"}
    for base, where in corners.items():
        for frame in range(4):
            roles[base + frame] = (
                f"the attacking alien, {where}, frame {frame + 1} of 4"
            )
    roles[20] = "the attacking alien, bottom right (it does not animate)"
    roles[49] = "the moon pointer on the ending screen"
    return roles


#: Slot index -> what it is. See :func:`_sprite_roles`.
SPRITE_ROLES: dict[int, str] = _sprite_roles()

#: **D4 — the title screen's alien egg.** Not a sprite slot like the rest: the
#: ROM composes it from eight *multicolor* sprites, whose bit-pair pixels the
#: single-colour sprite bitmaps cannot represent, so the remake builds it as one
#: image. A replacement is that image — full screen, transparent where the egg
#: is not.
TITLE_ART = "title_egg.png"
TITLE_ART_SIZE = (320, 200)


def title_art_path() -> Path | None:
    """A supplied title egg, or ``None``."""
    return assets.find(TITLE_ART)


#: **CR2 — the same manifest shape `audio.samples` already uses**, one file per
#: media folder. `samples.py`'s own manifest exists because a downloaded file's
#: name carries its provenance and renaming it to a cue name throws that away;
#: the same is true of art someone draws or downloads for `portraits/`, `map/`
#: or `sprites/`, so this is that mechanism generalised rather than a second
#: one invented beside it. One TOML file per folder, keyed by the filename it
#: describes (not by a cue name — a folder here holds several unrelated files,
#: where a sound cue is one thing with variants):
#:
#:     # portraits/manifest.toml
#:     [ripley.png]
#:     title = "Ripley portrait"
#:     author = "Jane Artist"
#:     source = "https://example.com/..."
#:     licence = "CC-BY 4.0"
#:
#: Entirely optional, exactly like the sound one: a file with no manifest entry
#: is simply present and uncredited, never an error.
MEDIA_MANIFEST = "manifest.toml"


def _read_media_manifest(directory: Path) -> dict[str, dict[str, str]]:
    """Load ``manifest.toml`` from one media folder. A broken one is ignored.

    The same contract as `audio.samples._read_manifest`, kept as a free
    function here rather than imported from there — that module is reached
    from the audio path and stays scoped to sound; this one is reached from
    every media kind and stays scoped to files.
    """
    path = directory / MEDIA_MANIFEST
    try:
        import tomllib

        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {
        str(name): {str(k): str(v) for k, v in table.items()}
        for name, table in raw.items()
        if isinstance(table, dict)
    }


def _media_credit(path: Path | None) -> dict[str, str] | None:
    """The manifest entry for one supplied file, if it names a source.

    Looked up by filename within the file's own directory, so a portrait and a
    sprite sharing a name (unlikely, but the folders are separate) cannot
    collide.
    """
    if path is None:
        return None
    entry = _read_media_manifest(path.parent).get(path.name)
    if not entry or not (entry.get("title") or entry.get("author")):
        return None
    return {"file": path.name, **entry}


#: How wide `--media` aims to print. Not a hard limit — a long filename or a
#: long reason still runs over rather than being cut — but what the wrapped
#: prose is measured against.
_REPORT_WIDTH = 78

#: **D5.** Derived files you may replace with your own, and what happens when
#: you do. The mechanism is not new — `assets.find` walks the roots in priority
#: order and takes the first hit, so a file of the right name in a root ahead of
#: `out/` already wins. What was missing is anybody *saying* so: the dictionary
#: listed the intro as a thing to generate and, two lists further down, said
#: music was not replaceable at all. Both could not be true.
#:
#: Keyed on :data:`~alien_remake.assets.KNOWN_ASSETS` keys. A key absent here is
#: not a claim that it cannot be swapped — only that the swap has no documented
#: story yet, which is what D2 and D3 are for.
SWAPPABLE: dict[str, str] = {
    "intro": "drop your own intro.wav in a root ahead of out/ and it plays "
             "instead of the emulated SID - any length, it loops as the "
             "original does",
    "charset": f"put a different charset at {GLYPH_DIR}/{GLYPH_FILE} and it is "
               f"used instead - this derived file stays where it is, so you "
               f"keep what came off your own disk",
}

#: **CR3 — the project's own sources.** Written out here rather than left to
#: the README alone, because the credits screen is in-game and a player who
#: never reads a README should still be able to see whose work this is.
#: Wording matches `README.md`'s own Credits section verbatim - one fact, one
#: place, copied rather than re-derived so the two cannot drift apart.
#:
#: **The disassembly is deliberately not a row here** (owner, 2026-09-04):
#: it is documentation about the game, not a credit a player needs to see on
#: this screen — `docs/re/` still says so for anyone who goes looking.
PROJECT_CREDITS: tuple[dict[str, str], ...] = (
    {
        "title": "Alien",
        "author": "Paul Clansey, for Mind Games / Argus Press Software",
        "source": "the 1984 Commodore 64 game this project is a remake of",
    },
    {
        "title": "This remake",
        "author": "OuijaGhost",
    },
)


def credits() -> list[dict[str, str]]:
    """Everything a credits screen has to say, in one call.

    **CR1 — nothing here is invented; every row already exists somewhere.**
    Sound credits come from `audio.samples.SamplePlayer.credits()`, which reads
    `sounds.toml`; art credits come from the manifests CR2 just added to
    `portraits/`, `map/` and `sprites/`; the project's own sources are
    :data:`PROJECT_CREDITS`. A screen that read anything else would be
    inventing an acknowledgement instead of reporting one that is already
    written down.

    Ordered project sources first (what this *is*), then supplied media in the
    order a player encounters it (portraits, map, sprites, sounds) — not
    alphabetically, which would scatter related credits at random.
    """
    out = list(PROJECT_CREDITS)
    for crew_id, _name, _role in ROSTER:
        entry = _media_credit(portrait_path(crew_id))
        if entry:
            out.append(entry)
    for deck in sorted(DECK_NAMES):
        entry = _media_credit(map_path(deck))
        if entry:
            out.append(entry)
    for index in sorted(SPRITE_ROLES):
        entry = _media_credit(sprite_path(index))
        if entry:
            out.append(entry)
    entry = _media_credit(title_art_path())
    if entry:
        out.append(entry)
    for row in _sound_player().credits():
        out.append({
            "title": row.get("title", row["cue"]),
            "author": row.get("author", ""),
            # **File name shown too (owner, 2026-09-04)**: a player who wants
            # to find the actual clip on their own disk, or match this row to
            # one in their `sounds/` folder, needs the name — the title alone
            # is the recording's own name, not necessarily the file's.
            "file": row.get("file", ""),
            "licence": row.get("licence", ""),
            "source": row.get("source", ""),
        })
    return out


#: Screen width the credits screen wraps to (`_COLS` in `render/frontend.py`
#: - kept as a literal here rather than imported, so this module stays free
#: of a render-layer dependency).
_CREDITS_WIDTH = 40


def credits_lines(width: int = _CREDITS_WIDTH) -> list[str]:
    """`credits()`, laid out as the exact lines a screen should show.

    **Wrapped, not truncated** (owner, 2026-09-04): the credits screen used
    to cut every line at the field width, which silently dropped the back
    half of anything longer — a Freesound.org URL, most licence names. This
    is the one place that wrapping happens, so `core.flow.GameFlow.
    credits_pages()` (counting pages) and `render.frontend._draw_credits`
    (drawing them) can share it and never disagree about how many lines a
    page holds.

    Field order per entry: title, author, file, licence, source — a blank
    line separates entries. Continuation lines carry a two-space indent so a
    wrapped author/file/licence/source line still reads as "under" its
    title rather than a new one.
    """
    import textwrap

    lines: list[str] = []
    for entry in credits():
        lines.extend(textwrap.wrap(entry.get("title", ""), width) or [""])
        for key in ("author", "file", "licence", "source"):
            value = entry.get(key, "")
            if value:
                lines.extend(
                    textwrap.wrap(
                        "  " + value, width, subsequent_indent="  "
                    )
                )
        lines.append("")
    return lines


#: Things a reader will look for and not find. Listed so their absence is a
#: stated fact rather than an oversight — and so this file is the one place to
#: update when one of them becomes replaceable.
NOT_YET: tuple[tuple[str, str], ...] = (
    ("layouts", "deliberately, not for want of a mechanism: the owner's "
                "ruling is that the layout stays the original's and only the "
                "art inside it is yours to change, so nothing here can move a "
                "thing or resize it"),
)


#: What a file has to *be*, per kind of slot, so nobody has to guess. The
#: numbers are not preferences: the mixer opens at `sfx.EXPORT_SAMPLE_RATE` and
#: a sprite is 24x21 because the VIC says so, and both are stated here rather
#: than left to be discovered by supplying something that comes out wrong.
REQUIREMENTS: dict[str, str] = {
    "derived": "whatever the extractor produces - see `make it with` below",
    "glyphs (yours)": "an 8192-byte $2000-$3FFF charset region dump, or a "
                      "whole ALIEN .prg to take the region from",
    "portrait (yours)": "PNG, 24x21, transparency kept; anything larger is "
                        "scaled down to that",
    "map art (yours)": "PNG, 240x144 (30 columns x 18 rows of 8x8 cells); "
                       "anything larger is scaled down to that",
    "sprite (yours)": "PNG, 24x21 - one C64 hardware sprite - with "
                      "transparency; `title_egg.png` is 320x200 instead",
    "sound (the game's own)": "WAV. 44100 Hz is the mixer's rate, so that is "
                             "what avoids a resample; 16-bit, mono or stereo. "
                             "Stereo only opens the mixer in stereo when GAME "
                             "AUDIO is 'sampled'",
    "sound (added)": "WAV, 44100 Hz 16-bit, mono or stereo. A cue may be a "
                     "folder of several files, and one is picked at random",
}


#: What each sound actually *is*. Without this every effect row read
#: "replaces the emulated SID effect", which tells somebody choosing a
#: recording nothing at all about what they are choosing it for.
SOUND_MEANING: dict[str, str] = {
    "heartbeat": "the selected crew member's heartbeat - it beats faster as "
                 "their composure drops",
    "grille": "a duct grille being opened or shut",
    "movement": "the blip as a crew member arrives in a room",
    "tracker_alarm": "the motion tracker's ping when the Alien is detected",
    "airlock": "an airlock cycling, and the crack of one being blown",
    "attack_alert": "the siren while the Alien is attacking - only for the "
                    "crew member you are watching",
    "menu_move": "the cursor moving to another row",
    "menu_change": "an option's value changing",
    "menu_select": "picking a different crew member",
    "screen_enter": "arriving on a new screen",
    "crt_warmup": "the tube warming up, once, at the first frame drawn",
}


def requirement(kind: str) -> str:
    """What a file of this slot's kind has to be. Empty if unstated."""
    return REQUIREMENTS.get(kind, "")


def document() -> str:
    """`docs/MEDIA.md`: every replaceable file, where it goes, what it must be.

    Generated from :func:`slots`, which is itself generated from the loaders —
    so this cannot name a folder nothing reads, and a slot cannot be added
    without appearing. The prose that a reader needs and the code does not know
    lives in :data:`REQUIREMENTS` and in the headings below.
    """
    rows = slots()
    lines = [
        "# Audio and media you can replace",
        "",
        "*Generated by `python -m alien_remake --media-doc`. Do not edit by "
        "hand: `alien_remake.media` is the source, and a test fails if this "
        "file falls behind it.*",
        "",
        "Every file the game will use in place of its own, where to put it, "
        "and what it has to be. Nothing here changes how the game plays or "
        "where anything sits on screen - see the last section.",
        "",
        "## Where files go",
        "",
        "Paths below are relative to an **asset root**. These are searched in "
        "order and the first hit wins, so a file in an earlier root beats the "
        "derived one without replacing it:",
        "",
        f"1. `${assets.ENV_VAR}`, if you have set it",
        f"2. `{assets.DERIVED_DIR}/` in the current directory",
        f"3. `{assets.DERIVED_DIR}/` beside the checkout (or the frozen "
        f"executable)",
        "4. your per-user data directory, next to `settings.toml`",
        "",
        "Run `python -m alien_remake --media` to see those resolved to real "
        "paths on your own machine, and which files it can currently find. "
        "They are deliberately not written out here: they differ per machine, "
        "and a document that hard-codes one person's home directory is a "
        "document that misleads everybody else.",
        "",
        "The point of the search order is that you never have to overwrite "
        "what the extractor produced - put your own work in an earlier root "
        "and delete it to get the original back.",
        "",
    ]

    kinds: list[str] = []
    for slot in rows:
        if slot.kind not in kinds:
            kinds.append(slot.kind)
    titles = {
        "derived": "Derived from your own disk",
        "glyphs (yours)": "The character set",
        "portrait (yours)": "Crew portraits",
        "map art (yours)": "Deck plans",
        "sprite (yours)": "Sprites",
        "sound (the game's own)": "The game's own sound effects",
        "sound (added)": "Interface sounds (not in the original)",
    }
    for kind in kinds:
        lines += [f"## {titles.get(kind, kind)}", ""]
        need = requirement(kind)
        if need:
            lines += [f"**File format:** {need}", ""]
        # No "is it there?" column, deliberately. That answer is true of one
        # machine at one moment, and a committed document that carries it is
        # wrong for every other reader — `--media` is the live view and says so
        # above. It would also make this file impossible to keep current, since
        # the currency test would fail on any machine with a different set of
        # files present.
        lines += ["| put it here | what it replaces |", "|---|---|"]
        for slot in rows:
            if slot.kind != kind:
                continue
            note = SOUND_MEANING.get(slot.key, slot.what)
            if slot.swap:
                note = f"{note} - {slot.swap}"
            elif slot.how:
                note = f"{note} (make it with: `{slot.how}`)"
            lines.append(f"| `{slot.where}` | {note} |")
        lines.append("")

    lines += ["## Not replaceable", ""]
    for name, why in NOT_YET:
        lines.append(f"- **{name}** - {why}")
    lines += [
        "",
        "## What replacing a file cannot do",
        "",
        "Supplying a file changes a picture or a sound. It cannot move "
        "anything, resize anything, or change a rule: every drawn override is "
        "scaled to a size taken from the machine (a hardware sprite is 24x21, "
        "the map field is 240x144), and nothing reads a dimension off your "
        "file. That is the owner's ruling on D4, and DEC-041 records it.",
        "",
        "Two exceptions run the other way, and they are there to *protect* the "
        "game rather than to limit you. The selected crew member's marker "
        "pulses on the ROM's own heartbeat, and the marker portrait is black "
        "in a room and white in a duct. Those colours are telling the player "
        "something, so on those two the game washes its colour over your art "
        "at half strength instead of dropping it - you keep the picture, and "
        "the player keeps the signal.",
        "",
    ]
    return "\n".join(lines)


def describe() -> str:
    """The dictionary, as text — what `--media` prints."""
    rows = slots()
    width = max(len(s.key) for s in rows)
    lines = [
        "Replaceable media. Files go under any asset root; the first is used.",
        "",
        "Roots searched, in order:",
    ]
    lines += [f"  {root}" for root in assets.asset_roots()]
    lines.append("")
    kind = None
    for slot in rows:
        if slot.kind != kind:
            kind = slot.kind
            lines.append(f"[{kind}]")
        lines.append(f"  {slot.key:<{width}}  {slot.status:>9}  {slot.where}")
        lines.append(f"  {'':<{width}}             {slot.what}")
        if slot.how and not slot.present:
            lines.append(f"  {'':<{width}}             make it with: {slot.how}")
        if slot.swap:
            # A sentence, not a filename, so it wraps — and it wraps against
            # its own indent rather than a round number, or the first version's
            # 60 columns plus 42 of lead ran to 102 and off the terminal.
            lines.append(f"  {'':<{width}}             yours instead:")
            indent = 2 + width + 13 + 2
            for line in textwrap.wrap(slot.swap, max(24, _REPORT_WIDTH - indent)):
                lines.append(f"{' ' * indent}{line}")
    lines.append("")
    lines.append("[not replaceable yet]")
    for name, why in NOT_YET:
        lines.append(f"  {name:<{width}}             {why}")
    return "\n".join(lines)
