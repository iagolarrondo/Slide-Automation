#!/usr/bin/env bash
# One-shot: ensure repo venv + deps, then run slide-build from repo root.
# Shorter entry from repo root: bin/deck "$@" (same script).
# Usage (from anywhere):
#   bash "/path/to/Slide Automation/scripts/slide_build_with_setup.sh" \
#     --template "templates/Sloan_Template.pptx" --input "examples/example_deck_v1.json"
#
# Requires: python3 on PATH (3.9+). Does not install the MCP extra.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$REPO_ROOT/.venv"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 --template <template.pptx> --input <deck.json> [other slide-build args]" >&2
  echo "Example: $0 --template templates/Sloan_Template.pptx --input examples/example_deck_v1.json" >&2
  exit 2
fi

cd "$REPO_ROOT"

if [[ ! -d "$VENV" ]]; then
  echo "Creating venv at $VENV ..." >&2
  python3 -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

echo "Installing / refreshing dependencies ..." >&2
pip install -q -r "$REPO_ROOT/requirements.txt"
pip install -q -e "$REPO_ROOT"

exec slide-build "$@"
