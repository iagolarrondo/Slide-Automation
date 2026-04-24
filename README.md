# Slide Automation

Turn a **model-agnostic JSON deck spec** into an **editable PowerPoint** using `python-pptx` and template-specific donor decks.

**You own:** deck-spec JSON generation (any LLM or editor).  
**This repo owns:** validation and deterministic local rendering into PowerPoint.

---

## Happy Path

1. Generate a deck-spec JSON file. Use [`docs/deck_generation_source_of_truth.md`](docs/deck_generation_source_of_truth.md) for editorial rules and [`docs/slide_layout_specs_sloan_poc.md`](docs/slide_layout_specs_sloan_poc.md) for slide-type selection. If you want paste-in LLM instructions, use the canonical bootstrap at [`docs/llm_project_bootstrap_multitemplate_tightened.md`](docs/llm_project_bootstrap_multitemplate_tightened.md).
2. Save the JSON anywhere convenient. The repo includes:
   - [`examples/example_deck.json`](examples/example_deck.json) (Sloan)
   - [`examples/example_deck_wd.json`](examples/example_deck_wd.json) (WD)
   - [`examples/example_deck_wd_full_catalog.json`](examples/example_deck_wd_full_catalog.json) (WD full catalog smoke)
3. From the repo root, run:

```bash
bin/deck --input examples/example_deck.json
```

This resolves the template from JSON ``template_id`` when set, otherwise **Sloan** (`templates/Sloan_Donor_Deck.pptx`). Override with ``--template-id sloan`` or ``--template-id wd``. To point at another donor file while keeping the same slide map, add ``--template /path/to/donor.pptx``.

**WD decks:** use ``wd_*`` slide types (see [`docs/wd_donor_inventory.md`](docs/wd_donor_inventory.md)) and either top-level ``"template_id": "wd"`` or ``slide-build --template-id wd``. Example JSON: [`examples/example_deck_wd.json`](examples/example_deck_wd.json).

This is the recommended path. It prepares the venv if needed, installs the package, validates the JSON, and writes `output/<spec-stem>.pptx`.

If you already have an activated venv and editable install, you can call `slide-build` directly. See [`docs/local_one_step_render.md`](docs/local_one_step_render.md).

### macOS: pick JSON anywhere, render, open PowerPoint

**Recommended (double-click):** in Finder, open the repo and double-click **`Mac Deck Render.command`**. A file dialog asks for your deck-spec JSON (anywhere on disk). The file is copied to `input/deck_spec.json`, then rendered via the repo-local module path (`PYTHONPATH=src python3 -m slide_automation.build_cli ...`) to `output/<original-basename>.pptx`, and opened in Microsoft PowerPoint.

If the JSON includes top-level `template_id`, the launcher passes it as `--template-id <value>`; if absent, default template resolution applies.

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
| [`docs/wd_donor_inventory.md`](docs/wd_donor_inventory.md) | **WD donor deck** — slide index ↔ JSON `wd_*` types, placeholders, agenda variants. |
| [`docs/tool_contract.md`](docs/tool_contract.md) | **Stable API & CLI** — `slide_automation.api`, `slide-validate`, `slide-render`, `slide-build`. |
| [`docs/local_one_step_render.md`](docs/local_one_step_render.md) | **`slide-build`** and `bin/deck` usage. |
| [`docs/testing.md`](docs/testing.md) | Smoke commands and unit tests. |
| [`docs/llm_project_bootstrap_multitemplate_tightened.md`](docs/llm_project_bootstrap_multitemplate_tightened.md) | Canonical multi-template bootstrap to paste into an LLM workspace. |
| [`schemas/deck_schema_v1.json`](schemas/deck_schema_v1.json) | Structural reference (validator is lightweight; schema may lag slightly). |

---

## Repo layout (lean)

| Path | Contents |
|------|----------|
| `src/slide_automation/` | Package: `api`, `renderer`, `template_registry` (Sloan + WD), `template_map` (Sloan shim), `utils`, CLIs |
| `src/main.py`, `src/validate_deck_spec.py` | Shims (`PYTHONPATH=src`) mirroring CLIs |
| `src/inspect_template.py` | Inspect donor slides, shape indices, and placeholder markers |
| `templates/` | Donor decks: `Sloan_Donor_Deck.pptx`, `WD_Template_Donor.pptx` |
| `examples/` | Example JSON (`example_deck.json`, `example_deck_wd.json`) and assets |
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

## Donor Mapping Setup

1. Inspect donor slides: `python src/inspect_template.py --template-id sloan` or `python src/inspect_template.py --template-id wd`.
2. Align mappings in:
   - Sloan: `src/slide_automation/template_registry/sloan.py`
   - WD: `src/slide_automation/template_registry/wd.py` (+ `docs/wd_donor_inventory.md`)
3. Validate and render a small spec, then adjust mapping as needed.

---

## Supported template families

Template families are selected by JSON ``template_id`` (or CLI `--template-id`):

- **Sloan (`template_id: "sloan"` or omitted)**: classic `cover` / `agenda` / `standard_*` types.
- **WD (`template_id: "wd"`)**: `wd_*` slide types documented in [`docs/wd_donor_inventory.md`](docs/wd_donor_inventory.md), including:
  `wd_cover`, `wd_agenda_3`, `wd_agenda_4`, `wd_agenda_5`, `wd_agenda_6`, `wd_divider`,
  `wd_section_intro`, `wd_two_column`, `wd_two_column_alt`, `wd_three_column`, `wd_four_column`,
  `wd_mosaic_4`, `wd_mosaic_6`, `wd_mosaic_8`, `wd_tile_4`, `wd_tile_5`, `wd_tile_6`,
  `wd_one_block_grouped`, `wd_one_block_placeholder`.

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

For WD fields and per-slide editable targets, use [`docs/wd_donor_inventory.md`](docs/wd_donor_inventory.md).

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

Smoke renders:

```bash
PYTHONPATH=src python3 -m slide_automation.build_cli --template-id sloan --input examples/example_deck.json --output output/example_deck_sloan_smoke.pptx
PYTHONPATH=src python3 -m slide_automation.build_cli --template-id wd --input examples/example_deck_wd_full_catalog.json --output output/example_deck_wd_full_catalog.pptx
```

See [`docs/testing.md`](docs/testing.md).

---

## Known limitations

- Validation is intentionally lightweight (not full JSON Schema enforcement).
- **Agenda** rendering depends on donor table shape/materialization; if absent, renderer falls back to generated table/text.
