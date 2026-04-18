# One-step validate + render (`slide-build`)

Local-only workflow: run the same **strict** validation as **`slide-validate`** (`validate_deck_spec`), then **`slide-render`** if there are no validation errors. No MCP or network.

## Short path (recommended for repeat use)

From the **repo root**, use the tiny wrapper (same as `scripts/slide_build_with_setup.sh`, fewer characters):

```bash
cd "/path/to/Slide Automation"
bin/deck --template templates/Sloan_Template.pptx --input examples/example_deck_v1.json
```

**Optional — from any directory** (one-time in `~/.zshrc` or `~/.bashrc`; set `ROOT` to your clone):

```bash
export SLIDE_AUTOMATION_ROOT="$HOME/Documents/Cursor Apps/Slide Automation"
alias deck='"$SLIDE_AUTOMATION_ROOT/bin/deck"'
```

Then:

```bash
deck --template "$SLIDE_AUTOMATION_ROOT/templates/Sloan_Template.pptx" \
     --input "$SLIDE_AUTOMATION_ROOT/examples/example_deck_v1.json"
```

The alias is optional; the wrapper alone avoids typing the long `scripts/slide_build_with_setup.sh` path whenever your shell is already in the repo.

## Copy-paste: venv + install + build (one command)

Use this when you want a **single invocation** from any directory: it `cd`s to the repo, creates **`.venv`** if missing, installs `requirements.txt` + editable package, then runs **`slide-build`**.

Replace the script path with your clone’s absolute path (or use **`bin/deck`** from the repo root — see above):

```bash
"/path/to/Slide Automation/scripts/slide_build_with_setup.sh" \
  --template "/path/to/Slide Automation/templates/Sloan_Template.pptx" \
  --input "/path/to/Slide Automation/examples/example_deck_v1.json"
```

- **Requires:** `python3` on your `PATH` (3.9+). First run creates `.venv` and may take a moment; later runs only refresh installs quietly.
- **Output:** still defaults to **`output/<stem>.pptx` under the repo root** (the script `cd`s there before running `slide-build`).

## Usage

```bash
slide-build --template "templates/Sloan_Template.pptx" --input "examples/my_deck.json"
```

- **Output:** if you omit `--output`, the PPTX is written to **`output/<json-stem>.pptx`** (relative to your shell’s current working directory). Parent directories are created as needed.
- **Explicit output:** `--output path/to/out.pptx`
- **Warnings:** `--quiet-warnings` hides advisory title-length messages on stderr (same idea as `slide-validate`).

**Exit codes:** `0` success, `1` file/JSON/render I/O errors, `2` validation failed (no PPTX written).

## Latest JSON in a folder (optional)

```bash
slide-build --template "templates/Sloan_Template.pptx" --latest-from examples/
```

Picks the **most recently modified** `*.json` in that directory only (not subfolders). Prints which file was chosen on stderr.

## See also

- [`tool_contract.md`](tool_contract.md) — stable CLI list  
- [`testing.md`](testing.md) — example specs and smoke paths  
