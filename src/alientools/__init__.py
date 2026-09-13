"""alientools — pure-Python, stdlib-only toolkit for the C64 game *Alien*.

Reads the read-only `MNIB-1541-RAW` nibble dump, decodes GCR to logical
sectors, reconstructs the CBM-DOS filesystem, and disassembles the 6502 code
(Part I). The package exposes a single CLI entry point: ``python -m alientools``.

Phase 1 is stdlib-only by design (see DECISIONS.md D-001). Modules are added one
on top of this skeleton; see ARCHITECTURE.md for the intended
layout.
"""

__version__ = "0.0.0"

__all__ = ["__version__"]
