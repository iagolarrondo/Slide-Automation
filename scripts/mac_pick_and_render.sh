#!/usr/bin/env bash
# macOS: pick a deck-spec JSON (file dialog or path arg), copy to canonical repo input,
# render with donor deck, open PowerPoint on success.
#
# Usage:
#   scripts/mac_pick_and_render.sh                    # shows file picker
#   scripts/mac_pick_and_render.sh /path/to/spec.json # skip picker
#
# Requires: macOS, python3 on PATH (3.9+), donor deck at templates/Sloan_Donor_Deck.pptx

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$REPO_ROOT/.venv"
DONOR="$REPO_ROOT/templates/Sloan_Donor_Deck.pptx"
CANON_JSON="$REPO_ROOT/input/deck_spec.json"

pick_json_via_dialog() {
  # User cancel -> empty string
  osascript <<'APPLESCRIPT' 2>/dev/null || true
try
  set theFile to choose file with prompt "Select deck-spec JSON to render" default location (path to desktop folder)
  return POSIX path of theFile
on error number -128
  return ""
end try
APPLESCRIPT
}

ensure_env() {
  if [[ ! -f "$DONOR" ]]; then
    echo "Donor deck not found: $DONOR" >&2
    exit 1
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
}

main() {
  local src="${1:-}"

  if [[ -z "$src" ]]; then
    src="$(pick_json_via_dialog | tr -d '\r')"
  fi

  if [[ -z "$src" ]]; then
    echo "No file selected." >&2
    exit 0
  fi

  if [[ ! -f "$src" ]]; then
    echo "Not a file: $src" >&2
    exit 1
  fi

  mkdir -p "$REPO_ROOT/input" "$REPO_ROOT/output"

  echo "Copying -> $CANON_JSON" >&2
  cp "$src" "$CANON_JSON"

  local base stem out
  base="$(basename "$src")"
  stem="${base%.*}"
  if [[ -z "$stem" ]]; then
    stem="deck"
  fi
  out="$REPO_ROOT/output/${stem}.pptx"

  ensure_env

  echo "Rendering -> $out" >&2
  slide-build \
    --template "$DONOR" \
    --input "$CANON_JSON" \
    --output "$out"

  echo "Opening PowerPoint ..." >&2
  if ! open -a "Microsoft PowerPoint" "$out" 2>/dev/null; then
    open "$out"
  fi

  echo "Done: $out" >&2
}

main "$@"
