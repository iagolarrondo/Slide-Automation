# One-step validate + render

Local-only workflow: run the same **strict** validation as **`slide-validate`** (`validate_deck_spec`), then **`slide-render`** if there are no validation errors. No network required.

## Recommended command

From the **repo root**, use the wrapper:

```bash
cd "/path/to/Slide Automation"
bin/deck --input examples/example_deck.json
```

**Optional — from any directory** (one-time in `~/.zshrc` or `~/.bashrc`; set `ROOT` to your clone):

```bash
export SLIDE_AUTOMATION_ROOT="$HOME/Documents/Cursor Apps/Slide Automation"
alias deck='"$SLIDE_AUTOMATION_ROOT/bin/deck"'
```

Then:

```bash
deck --input "$SLIDE_AUTOMATION_ROOT/examples/example_deck.json"
```

Optional: `--template-id` (when set, overrides JSON) and `--template /path/to/donor.pptx` to override only the file. If you omit both ``--template-id`` and JSON ``template_id``, the profile defaults to **Sloan**.

WD example:

```bash
deck --template-id wd --input "$SLIDE_AUTOMATION_ROOT/examples/example_deck_wd_full_catalog.json"
```

## Equivalent direct script

Use this when you want a **single invocation** from any directory without first `cd`-ing into the repo: it creates **`.venv`** if missing, installs `requirements.txt` + editable package, then runs **`slide-build`**.

Replace the script path with your clone’s absolute path (or use **`bin/deck`** from the repo root — see above):

```bash
"/path/to/Slide Automation/scripts/slide_build_with_setup.sh" \
  --input "/path/to/Slide Automation/examples/example_deck.json"
```

- **Requires:** `python3` on your `PATH` (3.9+). First run creates `.venv` and may take a moment; later runs only refresh installs quietly.
- **Output:** still defaults to **`output/<stem>.pptx` under the repo root** (the script `cd`s there before running `slide-build`).

## Direct CLI

```bash
slide-build --input "examples/my_deck.json"
```

- **Output:** if you omit `--output`, the PPTX is written to **`output/<json-stem>.pptx`** (relative to your shell’s current working directory). Parent directories are created as needed.
- **Explicit output:** `--output path/to/out.pptx`
- **Warnings:** `--quiet-warnings` hides advisory title-length messages on stderr (same idea as `slide-validate`).

**Exit codes:** `0` success, `1` file/JSON/render I/O errors, `2` validation failed (no PPTX written).

## Optional: latest JSON in a folder

```bash
slide-build --latest-from examples/
```

Picks the **most recently modified** `*.json` in that directory only (not subfolders). Prints which file was chosen on stderr.

## See also

- [`tool_contract.md`](tool_contract.md)
- [`testing.md`](testing.md)
