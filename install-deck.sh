#!/bin/bash
# install-deck.sh -- one-shot setup for a Steam Deck (or any Linux box).
#
#   ./install-deck.sh
#
# Makes a virtual environment inside this folder and installs the game into it.
# Nothing is written outside this directory and nothing needs root: SteamOS's
# system partition is read-only, and this deliberately never touches it, so
# `steamos-readonly disable` is not needed and should not be used.
set -euo pipefail
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
command -v "$PY" >/dev/null || { echo "No $PY on PATH. Install Python 3.12+."; exit 1; }

echo "==> Creating .venv with $($PY --version)"
"$PY" -m venv .venv

echo "==> Installing the game and its two dependencies"
# Prefer prebuilt wheels: SteamOS has no compiler toolchain by default, and
# building pygame from source there fails in a way that reads as a bug in this
# project rather than a missing gcc.
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/python -m pip install --quiet --only-binary :all: -e ".[remake]" \
  || ./.venv/bin/python -m pip install --quiet -e ".[remake]"

chmod +x play.sh 2>/dev/null || true

echo
echo "Done. Two steps left:"
echo
echo "  1. Copy your own disk image (.nib, .g64 or .d64) into:"
echo "       $(pwd)"
echo "  2. Derive the game's data from it, once:"
echo "       ./.venv/bin/python -m alien_remake --derive-assets"
echo
echo "Then play with:  ./play.sh"
echo "To add it to Steam, point Add-a-Non-Steam-Game at:"
echo "       $(pwd)/play.sh"
