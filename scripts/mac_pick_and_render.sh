#!/usr/bin/env bash
# macOS: pick a deck-spec JSON (file dialog or path arg), copy to canonical repo input,
# render with repo-local build module, open PowerPoint on success.
#
# Usage:
#   scripts/mac_pick_and_render.sh                    # shows file picker
#   scripts/mac_pick_and_render.sh /path/to/spec.json # skip picker
#
# Requires: macOS, python3 on PATH (3.9+)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$REPO_ROOT/.venv"
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

resolve_template_id() {
  local json_path="$1"
  python3 - "$json_path" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    obj = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("")
    raise SystemExit(0)

tid = obj.get("template_id") or obj.get("template")
if isinstance(tid, str) and tid.strip():
    print(tid.strip())
else:
    print("")
PY
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

  local template_id
  template_id="$(resolve_template_id "$CANON_JSON")"

  local -a cmd
  cmd=(python3 -m slide_automation.build_cli --input "$CANON_JSON" --output "$out")
  if [[ -n "$template_id" ]]; then
    cmd+=(--template-id "$template_id")
  fi

  echo "Selected JSON: $src" >&2
  if [[ -n "$template_id" ]]; then
    echo "Resolved template_id: $template_id" >&2
  else
    echo "Resolved template_id: <default>" >&2
  fi
  echo -n "Render command: PYTHONPATH=src" >&2
  printf ' %q' "${cmd[@]}" >&2
  echo >&2

  echo "Rendering -> $out" >&2
  PYTHONPATH=src "${cmd[@]}"

  echo "Opening PowerPoint ..." >&2
  if ! open -a "Microsoft PowerPoint" "$out" 2>/dev/null; then
    open "$out"
  fi

  echo "Done: $out" >&2
}

main "$@"
