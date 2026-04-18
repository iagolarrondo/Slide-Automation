# Slide Automation (v1)

Generate PowerPoint decks from structured JSON using `python-pptx` and a Sloan template **working copy** (`.pptx`).

## Primary workflow (today)

1. **Generate the deck spec as JSON** — e.g. in a **ChatGPT Project** (or any editor), following the editorial contract in [`docs/deck_generation_source_of_truth.md`](docs/deck_generation_source_of_truth.md).
2. **Save the file on your Mac** — e.g. under this repo’s `examples/` or your own folder.
3. **Validate and render locally** (no MCP, no remote host):
   - **One command:** [`slide-build`](docs/local_one_step_render.md) — strict validation (same checks as `slide-validate`), then writes `output/<spec-stem>.pptx` unless you pass `--output`.
   - **Or two steps:** `slide-validate --input …` then `slide-render --template … --input … --output …`.
   - **Or “everything including venv”:** from repo root, **`bin/deck`** … (same as [`scripts/slide_build_with_setup.sh`](scripts/slide_build_with_setup.sh); see [`docs/local_one_step_render.md`](docs/local_one_step_render.md)).

After `pip install -e .` from a venv, run commands from the repo root (or use absolute paths). Put your Sloan template at something like `templates/Sloan_Template.pptx`.

## Source of truth (documentation)

| Document | Role |
|----------|------|
| [`docs/slide_layout_specs_sloan_poc.md`](docs/slide_layout_specs_sloan_poc.md) | **Renderer / layout**—Sloan template placeholders, per-layout density and limits, when to use each layout family, escalation relative to the PPT mechanics. |
| [`docs/deck_generation_source_of_truth.md`](docs/deck_generation_source_of_truth.md) | **Editorial / spec generation**—storyline, slide and block headings, synthesis vs source, tone, density intent, and workflow before JSON is rendered. |

Code still implements behavior (`src/slide_automation/renderer.py`, `src/slide_automation/template_map.py`); the docs above are the human-facing contracts for **how to use layouts** vs **how to write or generate deck specs**.

## More docs (by use)

| Topic | Document |
|--------|----------|
| **One-step validate + render** | [`docs/local_one_step_render.md`](docs/local_one_step_render.md) |
| **API / CLI contract** | [`docs/tool_contract.md`](docs/tool_contract.md) |
| **Smoke examples & tests** | [`docs/testing.md`](docs/testing.md) |
| **Optional MCP / dict tools** (not day-to-day for most users) | [`docs/mcp_wrapper.md`](docs/mcp_wrapper.md), [`docs/mcp_tool_surface_v1.md`](docs/mcp_tool_surface_v1.md), [`docs/mcp_runbook.md`](docs/mcp_runbook.md) |

## Layout

- `templates/` — Sloan `.pptx` working copy (not committed here; add locally)
- `examples/` — Example deck JSON
- `docs/` — Source-of-truth and supporting docs (see tables above)
- `schemas/` — JSON schema (reference; validator is lightweight)
- `bin/deck` — short wrapper → `scripts/slide_build_with_setup.sh` (venv + install + `slide-build`)
- `src/` — Shims and diagnostics (`main.py`, probes, `inspect_template.py`)
- `src/slide_automation/` — Installable package: `api`, `renderer`, `template_map`, `utils`, CLIs
- `tests/` — Unit tests (e.g. title-fitting regression)
- `output/` — Generated `.pptx`

## Setup

Python 3.9+:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .            # optional: slide-validate, slide-render, slide-build
```

### Optional: MCP stdio server (future / advanced)

Not required for the ChatGPT Project → JSON → local PPT flow above. If you wire an MCP client to this repo, use **Python 3.10+**, `pip install -e ".[mcp-server]"`, and `slide-automation-mcp` — see [`docs/mcp_wrapper.md`](docs/mcp_wrapper.md) and [`docs/mcp_runbook.md`](docs/mcp_runbook.md).

## Public API / CLI surface (v1)

**Stable Python surface:** import from **`slide_automation.api`** (or the **`slide_automation`** package): **`load_json`**, **`validate_deck_spec`**, **`render_deck`**. Prefer these over deep imports into `renderer` / `utils` unless you depend on implementation details.

**Stable CLI surface** (after `pip install -e .`): **`slide-validate`**, **`slide-render`**, **`slide-build`** (validate then render; default output under `output/`). Avoid renaming or aliasing these for tools without a **versioned** contract change—see **`Public API / CLI surface (v1)`** in [`docs/tool_contract.md`](docs/tool_contract.md). Quick ref: [`docs/local_one_step_render.md`](docs/local_one_step_render.md).

## Inspect template → map → validate → render

If you already use **`slide-build`**, you can skip straight to validate+render for day-to-day specs; the steps below are for **first-time template setup** or debugging.

**1. Layouts and placeholder indices**

```bash
python src/inspect_template.py --template "templates/Sloan_Template.pptx"
```

**2. Mapping**

Edit `src/slide_automation/template_map.py` so each slide type’s `layout_index` and `placeholders` match your inspected file.

**3. Validate deck JSON (optional, stricter checks)**

```bash
python src/validate_deck_spec.py --input "examples/example_deck_v1.json"
```

Checks supported `type` values, **required fields per slide type**, and **stderr warnings** for long titles/block titles. Exit **`2`** on validation errors, **`0`** if valid (`--quiet-warnings` hides length warnings).

**4. Render**

From the repo root:

```bash
python src/main.py \
  --template "templates/Sloan_Template.pptx" \
  --input "examples/slide_automation_rollout_recommendation_spec.json" \
  --output "output/render_smoke.pptx"
```

Other one-liners use the same template path, e.g. `examples/example_deck_full_v1.json` → `output/example_deck_full_v1.pptx`.

## Supported slide types

Each slide object uses `"type": "<one of below>"`.

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

## JSON fields (summary)

- **cover**: `title`, optional `subtitle`, `date`
- **agenda**: `agenda_items` (string array)
- **divider**: `title`, `section_title`
- **standard_1_block**: `section_title`, `title`, `block_title`, `block_body`, optional `footer`
- **standard_2_block**: `section_title`, `title`, `left_block_title`, `left_block_body`, `right_block_title`, `right_block_body`, optional `footer`
- **standard_3_block**: `section_title`, `title`, `block_1_title` … `block_3_body`, optional `footer`
- **standard_2_block_big_left / big_right**: `section_title`, `title`, `dominant_block_title`, `dominant_block_body`, `secondary_block_title`, `secondary_block_body`, optional `footer`
- **narrow_image_content / wide_image_content**: `section_title`, `title`, `image`, `content_block_title`, `content_block_body`, optional `footer`

`block_*_body` values may be strings or string arrays (one bullet per line). Use `"type"` (not `slide_type`) per validator.

## Rendering behavior (titles & footer)

**Main and block titles (content layouts)**  
For `standard_*`, `standard_2_block_big_*`, and `*_image_content`, the renderer **does not shorten or rewrite** main titles or block titles (editorial length is owned by the deck spec). It applies **light whitespace normalization** only, prints **`[title-length]`** warnings to **stderr** when text exceeds **advisory** character thresholds, and still writes the **full string** into placeholders. PowerPoint may still wrap or clip visually if copy is too long for the template. Use **`--quiet` / `-q`** to suppress the stdout success line only (warnings remain on stderr).

**Footer and slide number**  
The renderer writes **only** into **native** placeholders that exist on the **created** slide:

- **Footer**: mapped `footer` index must resolve to a shape whose placeholder type starts with `FOOTER`.
- **Slide number**: index is taken from the slide layout’s `SLIDE_NUMBER` placeholder; the same type check applies on the slide instance.

`python-pptx` often **does not materialize** footer/slide-number placeholders on slides even when they appear on the layout. In that case the renderer **skips them silently**. There is **no** text-box or other ad hoc fallback.

## Smoke / regression testing

Which example JSON to run for what purpose (and how to run unit tests) is documented in **`docs/testing.md`**.

## Known limitations

- JSON validation is minimal (types and required keys, not full schema enforcement).
- **Agenda**: special layout; table cells or a programmatic table at mapped geometry; styling may not match the template table exactly.
- **`background_image`** is mapped in `slide_automation/template_map.py` but **not** implemented in the renderer.
- **Images**: `image` must be a valid filesystem path; missing/invalid paths are skipped.
- **Diagnostics** (separate CLIs, verbose by design): `src/inspect_template.py`, `src/placeholder_probe.py`, `src/image_content_probe.py`.

See `schemas/deck_schema_v1.json` for a structural reference (may lag new slide types slightly).
