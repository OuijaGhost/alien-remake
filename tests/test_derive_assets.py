"""`--derive-assets`: one command to turn the user's own disk into the game (DISC-252).

Nothing the game draws or plays can be shipped — the charset, the sprites, the
loader's BASIC and the SID intro are all the 1984 game's data — so every install
derives them locally. Before this, the three commands that do it were only
discoverable by reading `assets.report()`'s stderr and running them by hand.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alien_remake.__main__ import _find_nib, main


def test_a_missing_nib_is_reported_not_crashed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("alien_remake.__main__._find_nib", lambda: None)
    assert main(["--derive-assets"]) == 2
    err = capsys.readouterr().err
    assert "no disk image found" in err
    assert "--derive-assets" in err, "the message must show how to fix it"


def test_an_explicit_path_that_does_not_exist_is_reported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--derive-assets", str(tmp_path / "nope.nib")]) == 2
    assert "no disk image found" in capsys.readouterr().err


def test_find_nib_looks_in_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _find_nib() is None or _find_nib().suffix == ".nib"
    (tmp_path / "Some Disk.nib").write_bytes(b"x")
    found = _find_nib()
    assert found is not None and found.name == "Some Disk.nib"


def test_the_flag_does_not_start_a_game(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """It must return before any renderer or simulation is built."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("alien_remake.__main__._find_nib", lambda: None)

    def explode(*a: object, **k: object) -> None:  # pragma: no cover
        raise AssertionError("--derive-assets started the game")

    monkeypatch.setattr("alien_remake.__main__.default_simulation", explode)
    monkeypatch.setattr("alien_remake.__main__.run_app", explode)
    assert main(["--derive-assets"]) == 2


def test_deriving_is_not_automatic_on_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A game that silently writes ~9 MB on first launch is worse than one that
    tells you what to run. `--headless` must not derive anything."""
    monkeypatch.chdir(tmp_path)
    called: list[str] = []
    monkeypatch.setattr(
        "alien_remake.__main__._derive_assets",
        lambda nib: called.append("derived") or 0,
    )
    assert main(["--headless", "2"]) == 0
    assert called == [], "launching the game derived assets behind the user's back"
    assert not (tmp_path / "out").exists()


# --- F-1: the first-run wizard ----------------------------------------------

class _FakeWidget:
    """Stands in for every tkinter widget the wizard touches — enough to
    record what it was told to draw, and nothing that opens a real window."""

    def __init__(self, *a: object, text: str = "", command=None, **k: object) -> None:  # type: ignore[no-untyped-def]
        self.text = text
        self.command = command

    def pack(self, *a: object, **k: object) -> None:
        pass

    def config(self, *, text: str | None = None, **k: object) -> None:
        if text is not None:
            self.text = text

    def cget(self, name: str) -> str:
        return self.text

    def destroy(self) -> None:
        pass


class _FakeRoot(_FakeWidget):
    """The `tk.Tk()` instance. `mainloop()` runs the queued command
    synchronously instead of opening an event loop, which is what lets a
    test drive "click Browse" / "click Skip" without a real window ever
    existing."""

    def __init__(self) -> None:
        super().__init__()
        self.next_action: str | None = None  # set by the test before mainloop()
        self.children: list[_FakeWidget] = []
        self.destroyed = False

    def title(self, *a: object) -> None: pass
    def resizable(self, *a: object) -> None: pass
    def protocol(self, *a: object) -> None: pass
    def eval(self, *a: object) -> None: pass
    def deiconify(self) -> None: pass
    def update(self) -> None: pass
    def winfo_children(self) -> list[_FakeWidget]: return self.children
    def after(self, ms: int, fn) -> None: pass  # type: ignore[no-untyped-def]

    def mainloop(self) -> None:
        # The test arranges `next_action` to name which button "click" this
        # `mainloop()` call stands for; `quit()` is a no-op here since there
        # is no real loop to break out of.
        if self.next_action == "browse":
            for w in self.children:
                if isinstance(w, _FakeWidget) and w.text == "Browse..." and w.command:
                    w.command()
        elif self.next_action == "skip":
            for w in self.children:
                if isinstance(w, _FakeWidget) and w.text == "Skip" and w.command:
                    w.command()

    def quit(self) -> None:
        pass

    def destroy(self) -> None:
        self.destroyed = True


def _fake_tkinter(monkeypatch: pytest.MonkeyPatch, *, picked: str | None):
    """Installs a fake `tkinter` (+ `tkinter.filedialog`) module so
    `_first_run_asset_wizard` never opens a real window, and arranges the
    picker to return `picked` (or nothing, for "cancelled")."""
    import sys
    import types

    root_holder: dict[str, _FakeRoot] = {}

    def make_widget(parent, *a, **k):  # type: ignore[no-untyped-def]
        w = _FakeWidget(*a, **k)
        if isinstance(parent, _FakeRoot):
            parent.children.append(w)
        return w

    fake_tk = types.ModuleType("tkinter")
    fake_tk.Tk = lambda: root_holder.setdefault("root", _FakeRoot())  # type: ignore[attr-defined]
    fake_tk.Label = make_widget  # type: ignore[attr-defined]
    fake_tk.Button = make_widget  # type: ignore[attr-defined]
    fake_tk.Frame = lambda parent, **k: parent  # type: ignore[attr-defined]

    fake_filedialog = types.ModuleType("tkinter.filedialog")
    fake_filedialog.askopenfilename = lambda **k: picked or ""  # type: ignore[attr-defined]
    fake_tk.filedialog = fake_filedialog  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "tkinter", fake_tk)
    monkeypatch.setitem(sys.modules, "tkinter.filedialog", fake_filedialog)
    return root_holder


def test_the_wizard_returns_false_when_the_user_cancels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from alien_remake.__main__ import _first_run_asset_wizard

    root_holder = _fake_tkinter(monkeypatch, picked=None)
    # `mainloop()` fires once for the ask-screen; tell the fake root that
    # this call stands for clicking "Skip".
    original_mainloop = _FakeRoot.mainloop

    def patched_mainloop(self: _FakeRoot) -> None:
        self.next_action = "skip"
        original_mainloop(self)

    monkeypatch.setattr(_FakeRoot, "mainloop", patched_mainloop)
    assert _first_run_asset_wizard() is False
    assert root_holder["root"].destroyed


def test_the_wizard_derives_assets_from_the_chosen_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from alien_remake.__main__ import DeriveStep, _first_run_asset_wizard

    nib = tmp_path / "Alien.nib"
    nib.write_bytes(b"")
    root_holder = _fake_tkinter(monkeypatch, picked=str(nib))

    calls = []
    monkeypatch.setattr(
        "alien_remake.__main__.derive_assets_from",
        lambda path: calls.append(path) or iter(
            [DeriveStep("extracting the disk", True),
             DeriveStep("decoding the charset and sprites", True)]
        ),
    )

    seen_mainloops = {"n": 0}
    original_mainloop = _FakeRoot.mainloop

    def patched_mainloop(self: _FakeRoot) -> None:
        seen_mainloops["n"] += 1
        if seen_mainloops["n"] == 1:
            self.next_action = "browse"
        original_mainloop(self)

    monkeypatch.setattr(_FakeRoot, "mainloop", patched_mainloop)
    assert _first_run_asset_wizard() is True
    assert calls == [nib]
    assert root_holder["root"].destroyed


def test_the_wizard_reports_a_failed_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from alien_remake.__main__ import DeriveStep, _first_run_asset_wizard

    nib = tmp_path / "Alien.nib"
    nib.write_bytes(b"")
    _fake_tkinter(monkeypatch, picked=str(nib))
    monkeypatch.setattr(
        "alien_remake.__main__.derive_assets_from",
        lambda path: iter([DeriveStep("extracting the disk", False)]),
    )

    original_mainloop = _FakeRoot.mainloop

    def patched_mainloop(self: _FakeRoot) -> None:
        self.next_action = "browse"
        original_mainloop(self)

    monkeypatch.setattr(_FakeRoot, "mainloop", patched_mainloop)
    assert _first_run_asset_wizard() is False
