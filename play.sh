#!/bin/bash
# play.sh -- launch the Alien remake on Linux/macOS (the twin of play.bat).
#
# Run "./play.sh", or point Steam's Add-a-Non-Steam-Game at it. Any arguments
# are passed straight through:
#   ./play.sh --crt full
#   ./play.sh --headless 200
#
# It cds to its own directory first, because the game looks for out/ relative to
# the working directory and Steam launches things from wherever it feels like.
cd "$(dirname "$0")" || exit 1

if [ ! -x ".venv/bin/python" ]; then
    echo "No .venv found in this folder."
    echo "Run the one-time setup first:"
    echo "  ./install-deck.sh          # does it all (Steam Deck / any Linux)"
    echo "or by hand, per docs/INSTALL.md:"
    echo "  python3 -m venv .venv"
    echo "  ./.venv/bin/python -m pip install -e \".[remake]\""
    exit 1
fi

exec ./.venv/bin/python -m alien_remake "$@"
