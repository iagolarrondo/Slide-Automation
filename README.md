# Slide Automation

Turn a **model-agnostic JSON deck spec** into an **editable PowerPoint** using `python-pptx` and a **donor deck**: `templates/Sloan_Donor_Deck.pptx`.

**You own:** deck-spec JSON generation (any LLM or editor).  
**This repo owns:** validation and deterministic local rendering into PowerPoint.

---

## Happy Path

1. Generate a deck-spec JSON file. Use [`docs/deck_generation_source_of_truth.md`](docs/deck_generation_source_of_truth.md) for editorial rules and [`docs/slide_layout_specs_sloan_poc.md`](docs/slide_layout_specs_sloan_poc.md) for slide-type selection. If you want paste-in LLM instructions, use [`docs/llm_project_bootstrap_updated.md`](docs/llm_project_bootstrap_updated.md).
2. Save the JSON anywhere convenient. The repo includes [`examples/example_deck.json`](examples/example_deck.json) as a reference.
3. From the repo root, run:

```bash
bin/deck --template templates/Sloan_Donor_Deck.pptx --input examples/example_deck.json
```

This is the recommended path. It prepares the venv if needed, installs the package, validates the JSON, and writes `output/<spec-stem>.pptx`.

If you already have an activated venv and editable install, you can call `slide-build` directly. See [`docs/local_one_step_render.md`](docs/local_one_step_render.md).

### macOS: pick JSON anywhere, render, open PowerPoint

**Recommended (double-click):** in Finder, open the repo and double-click **`Mac Deck Render.command`**. A file dialog asks for your deck-spec JSON (anywhere on disk). The file is copied to `input/deck_spec.json`, rendered to `output/<original-basename>.pptx`, and opened in Microsoft PowerPoint.

First time: if Terminal says the file is not executable, run once:

```bash
chmod +x "Mac Deck Render.command" scripts/mac_pick_and_render.sh bin/pick-render
```

**One short command** (from repo root, still uses the file picker when given no arguments):

```bash
./bin/pick-render
```

To skip the dialog (e.g. automation), pass the JSON path:

```bash
./bin/pick-render /path/to/spec.json
```

---

## Documentation

| Document | Role |
|----------|------|
| [`docs/deck_generation_source_of_truth.md`](docs/deck_generation_source_of_truth.md) | **Editorial** — how to write or generate specs (storyline, tone, density). |
| [`docs/slide_layout_specs_sloan_poc.md`](docs/slide_layout_specs_sloan_poc.md) | **Slide-type guidance** — when to use each donor-backed slide type and how dense it should be. |
| [`docs/tool_contract.md`](docs/tool_contract.md) | **Stable API & CLI** — `slide_automation.api`, `slide-validate`, `slide-render`, `slide-build`. |
| [`docs/local_one_step_render.md`](docs/local_one_step_render.md) | **`slide-build`** and `bin/deck` usage. |
| [`docs/testing.md`](docs/testing.md) | Smoke commands and unit tests. |
| [`docs/llm_project_bootstrap_updated.md`](docs/llm_project_bootstrap_updated.md) | Optional instructions to paste into an LLM workspace. |
| [`schemas/deck_schema_v1.json`](schemas/deck_schema_v1.json) | Structural reference (validator is lightweight; schema may lag slightly). |

---

## Repo layout (lean)

| Path | Contents |
|------|----------|
| `src/slide_automation/` | Package: `api`, `renderer`, `template_map`, `utils`, CLIs |
| `src/main.py`, `src/validate_deck_spec.py` | Shims (`PYTHONPATH=src`) mirroring CLIs |
| `src/inspect_template.py` | Inspect donor slides, shape indices, and placeholder markers |
| `templates/` | Donor deck used for rendering |
| `examples/` | Example JSON (`example_deck.json`) and assets |
| `schemas/` | JSON schema reference |
| `tests/` | Unit tests |
| `output/` | Default render output (ignored by git) |
| `bin/deck`, `bin/pick-render`, `scripts/slide_build_with_setup.sh`, `scripts/mac_pick_and_render.sh` | Convenience wrappers |
| `Mac Deck Render.command` | macOS double-click launcher (file picker + render + open PPT) |
| `input/` | Last picked JSON copy (`deck_spec.json`; gitignored) |

---

## Setup

Python 3.9+:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

**Public API:** import from **`slide_automation.api`** (or **`slide_automation`**): `load_json`, `validate_deck_spec`, `render_deck`. Prefer these over deep imports unless you need internals.

**CLIs:** `slide-validate`, `slide-render`, `slide-build`.

---

## Donor Deck Setup

1. Inspect donor slides: `python src/inspect_template.py --template "templates/Sloan_Donor_Deck.pptx"`
2. Align `src/slide_automation/template_map.py` with donor slide numbers and field mappings.
3. Validate and render a small spec, then adjust mapping as needed.

---

## Supported slide types

Each slide uses `"type": "<one of below>"`.

| `type` | Purpose |
|--------|---------|
| `cover` | Title slide |
| `agenda` | Agenda table |
| `divider` | Section divider |
| `standard_1_block` | One content block |
| `standard_2_block` | Two columns |
| `standard_3_block` | Three columns |
| `standard_2_block_big_left` | Two blocks, dominant left |
| `standard_2_block_big_right` | Two blocks, dominant right |
| `narrow_image_content` | Narrow image + content |
| `wide_image_content` | Wide image + content |

---

## JSON fields (short reference)

- **cover**: `title`, optional `subtitle`, `date`
- **agenda**: `agenda_items` (string array)
- **divider**: `title`, `section_number` (preferred), optional legacy `section_title`
- **standard_1_block**: `section_title`, `title`, `block_title`, `block_body`, optional `footer`
- **standard_2_block**: `section_title`, `title`, `left_block_title`, `left_block_body`, `right_block_title`, `right_block_body`, optional `footer`
- **standard_3_block**: `section_title`, `title`, `block_1_title` … `block_3_body`, optional `footer`
- **standard_2_block_big_left / big_right**: `section_title`, `title`, `dominant_block_title`, `dominant_block_body`, `secondary_block_title`, `secondary_block_body`, optional `footer`
- **narrow_image_content / wide_image_content**: `section_title`, `title`, `image`, `content_block_title`, `content_block_body`, optional `footer`

`block_*_body` may be a string or string array (one bullet per line). Use `"type"` (not `slide_type`).

---

## Rendering behavior (titles & footer)

**Titles:** The renderer does not shorten main or block titles; it normalizes whitespace and may print **`[title-length]`** warnings to stderr when text exceeds advisory limits. **`--quiet`** on render suppresses the success line only, not warnings.

**Footer / slide number:** Only native placeholders that exist on the created donor-derived slide are written; there is no text-box fallback. Footer placeholders are cleared when no footer value is provided.

**Images:** `image` must be a valid filesystem path; missing paths are skipped.

---

## Testing

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

See [`docs/testing.md`](docs/testing.md).

---

## Known limitations

- Validation is intentionally lightweight (not full JSON Schema enforcement).
- **Agenda** rendering depends on donor table shape/materialization; if absent, renderer falls back to generated table/text.
- `wide_image_content` donor slide currently materializes fewer placeholders than expected; verify field mapping after donor updates.
