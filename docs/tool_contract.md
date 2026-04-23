# Slide automation — tool contract (API & CLI)

**Primary workflow:** deck spec JSON (from any LLM, hand-written file, or internal tool) on your machine → **`slide-validate`** / **`slide-build`** / **`slide-render`** using **`slide_automation.api`**. No network is required for rendering.

This document describes the repository as a **two-stage** capability: **deck-spec generation** (editorial, LLM-heavy) vs **PPT rendering** (deterministic, template-bound).

Related docs:

- Editorial rules for specs: [`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md)
- Sloan layout / placeholder rules: [`slide_layout_specs_sloan_poc.md`](slide_layout_specs_sloan_poc.md)
- Smoke JSON and tests: [`testing.md`](testing.md)

---

## Public API / CLI surface (v1)

The following are the **stable callable surface** for v1. Prefer **`slide_automation.api`** (or the **`slide_automation`** package root—same exports) over importing **`slide_automation.renderer`** or **`slide_automation.utils`** directly unless you need internals.

**Do not rename** these public symbols or console script entry points for cosmetic reasons. Intentional renames or signature changes should align with a **versioned** release (e.g. a future v2) and this contract should be updated in the same change.

### Python API (`slide_automation.api`)

| Symbol | Role |
|--------|------|
| **`load_json`** | Read a deck JSON file from disk → `dict`. |
| **`validate_deck_spec`** | Structural + required-field validation and advisory title/block length warnings → `(errors: list[str], warnings: list[str])`. |
| **`render_deck`** | Render an in-memory deck spec to a `.pptx` on disk → `Path`. |

The lighter **`validate_deck_payload`** (errors only, as used before render in the default CLI) is also exported from the same module; see §4.

### CLI (after `pip install -e .`)

| Command | Role |
|---------|------|
| **`slide-validate`** | Validate a deck JSON file (`--input`, optional ``--template-id``, optional `--quiet-warnings`). |
| **`slide-render`** | Render JSON → PPTX (`--input`, `--output`, optional `--template-id`, optional `--template` donor path override, optional `--quiet`). |
| **`slide-build`** | **One-step local workflow:** `validate_deck_spec` then `render_deck` if valid (`--input` *or* `--latest-from DIR`, optional `--template-id`, optional `--template`, optional `--output`, optional `--quiet-warnings`). Default output: `./output/<input-stem>.pptx`. See [`local_one_step_render.md`](local_one_step_render.md). |

**Repo shims** — `python src/main.py` and `python src/validate_deck_spec.py` — invoke the same implementations and remain supported for local use with `PYTHONPATH=src`; they are not a second public naming layer.

---

## 1. Purpose

**Goal**  
Enable reliable automation: an agent produces (or edits) a **structured deck spec**, then invokes a **renderer** to produce an editable **`.pptx`** from a selected template donor deck (currently Sloan or WD).

**Scope of this repo today**  
The codebase is **render-complete** for a defined JSON shape and template map. The **v1 public surface** is `slide_automation.api` plus **`slide-render`** / **`slide-validate`** / **`slide-build`** (see above); `src/main.py` shims mirror the render CLI for workflows that do not use an editable install.

**Out of scope for this document**  
OAuth, hosted template storage, and full schema validation beyond the current lightweight checks.

---

## 2. Deck-spec generation vs PPT rendering

| Stage | Role | Owner | Input | Output |
|--------|------|--------|--------|--------|
| **Deck-spec generation** | Turn goals, sources, and storyline into **JSON** that matches renderer expectations. | **Agent + human editorial rules** ([`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md)) | Natural language, project files, prior thread | `dict` / JSON file: `deck_title`, `slides[]` with `"type"` and per-slide fields |
| **PPT rendering** | Map spec → **python-pptx** using a **template profile** (slide map + agenda mode) + **donor `.pptx`**. | **This repo** (`renderer.render_deck`, `template_registry`, `utils`) | Parsed spec `dict`, donor path, output path | Written `.pptx` on disk |

**Critical distinction**  
- **Generation** owns message quality, length for layout, and slide-type choice for storytelling.  
- **Rendering** owns placeholder writes, agenda table behavior, images, footer/slide-number **when native placeholders exist**, and **stderr advisory `[title-length]`** warnings—it does **not** rewrite titles for fit.

An agent should **not** expect the renderer to fix a weak spec.

---

## 3. Inputs, outputs, assumptions, limitations

### 3.1 Inputs (rendering stage)

| Input | Required | Description |
|--------|----------|-------------|
| **Deck spec** | Yes | JSON object: top-level `deck_title` (string), `slides` (non-empty array). Each slide has `"type"` ∈ supported set (see `utils.SUPPORTED_SLIDE_TYPES`). |
| **Template / donor path** | Yes (resolved) | Default donor comes from **`--template-id`** (built-in registry; default **`sloan`**). Override the file with **`--template`** when needed. Slide-type mapping lives in `src/slide_automation/template_registry/` (Sloan + WD implemented). |
| **Output path** | Yes | Destination `.pptx` (parent dirs created if needed). |
| **Image paths** (image slides) | If those slides are used | Must be valid paths to image files on the machine running the renderer. |

### 3.2 Outputs (rendering stage)

| Output | Description |
|--------|-------------|
| **`.pptx` file** | Resolved absolute path returned by `render_deck`. |
| **stderr** | Optional `[title-length]` advisory lines for long titles/block titles (non-fatal). |
| **stdout** (CLI) | Optional `Deck generated: …` unless `--quiet`. |
| **Exit code** (CLI) | `0` success, `2` validation errors, `1` other errors. |

### 3.3 Assumptions

- Python 3.9+ with `python-pptx` installed (`requirements.txt`).
- **`pip install -e .`** or **`PYTHONPATH=src`** so the `slide_automation` package resolves.
- Donor file exists and donor slide references in `slide_automation.template_registry.sloan` match the inspected deck (for **`sloan`**).
- Deck spec uses **`"type"`** on each slide (not `slide_type`).

### 3.4 Limitations

- **Validation** is lightweight (not full JSON Schema parity with `schemas/`).
- **Footer / slide number**: written only to **native** materialized placeholders; often absent; **no** textbox fallback.
- **Title length**: renderer warns but does **not** shorten; overflow is a **spec + PowerPoint** concern.
- **No in-process `generate_deck_spec`** in this repo yet—agents generate JSON by other means (see §5).

---

## 4. Callable interface (current vs recommended)

Today the **working** pipeline is:

```text
load_json(path) → dict
validate_deck_payload(dict) → list[str]   # empty == ok
render_deck(template_path, payload, output_path, *, slide_type_map=..., agenda_render_mode=...) → Path
```

### 4.1 `render_deck` (implemented)

**Signature** (see `src/slide_automation/api.py` / `renderer.py`):

```python
def render_deck(
    template_path: str | Path,
    payload: Dict[str, Any],
    output_path: str | Path,
    *,
    template_id: str | None = None,
    slide_type_map: dict[str, dict[str, Any]] | None = None,
    agenda_render_mode: str | None = None,
) -> Path: ...
```

Keyword-only mapping kwargs default to the **Sloan** profile when omitted. Optional **`template_id`** selects a built-in profile unless **`slide_type_map`** / **`agenda_render_mode`** are passed explicitly.

**Contract**  
- **Raises** `FileNotFoundError` if template missing.  
- **Raises** `ValueError` for unsupported `slide.type` or invalid donor-slide mapping.  
- **Does not** validate payload shape; callers should validate first.

**Agent usage**  
Pass an in-memory `dict` (from JSON parse) plus absolute paths for template and output.

---

### 4.2 `validate_deck_spec` (implemented)

**Library**: `utils.validate_deck_spec(payload: Dict[str, Any]) -> tuple[list[str], list[str]]`  
Returns **`(errors, warnings)`**. `errors` combines shape checks from `validate_deck_payload` plus **required-field** rules per slide type. `warnings` lists **advisory title / block-title length** risks (same thresholds as the renderer’s stderr hints). Empty `errors` means the spec is OK to render.

**CLI** (repo root, `PYTHONPATH=src`):

```bash
python src/validate_deck_spec.py --input examples/example_deck.json
```

Exit codes: **`0`** valid (warnings may print to stderr), **`2`** validation errors, **`1`** file/JSON parse errors. Use **`--quiet-warnings`** to hide length warnings.

The older **`validate_deck_payload`** remains the subset used by `main.py` before render; stricter **`validate_deck_spec`** is the basis for **`slide-validate`** / **`slide-build`** and for programmatic validation before `render_deck`.

---

### 4.3 `generate_deck_spec` (future-facing; not in repo)

**Purpose**  
Single entry point for “given context, return a v1 deck **dict** (or write JSON).” That is **LLM + retrieval + editorial policy**; it belongs **outside** `render_deck` or beside it in a future package.

**Proposed signature** (documentation only for now):

```python
def generate_deck_spec(
    *,
    brief: str,
    context_paths: list[Path] | None = None,
    deck_title: str | None = None,
    max_slides: int | None = None,
    audience: str | None = None,
) -> dict[str, Any]:
    """Return a renderer-compatible deck spec dict.

    Not implemented in this repository yet. Implementations may call an LLM,
    read project files, and enforce deck_generation_source_of_truth.md rules.
    """
    raise NotImplementedError
```

**Until implemented**, agents should:

1. Use an LLM (or editor) with [`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md) + [`slide_layout_specs_sloan_poc.md`](slide_layout_specs_sloan_poc.md) as instructions.  
2. Emit JSON matching `validate_deck_*` expectations.  
3. Call `validate_deck_payload` then `render_deck`.

---

## 5. Packaging layout (implemented baseline)

```text
pyproject.toml              # setuptools; scripts slide-render / slide-validate / slide-build
src/
  slide_automation/
    __init__.py               # public re-exports
    api.py                    # stable import surface
    renderer.py
    template_registry/        # built-in profiles (sloan, wd), repo_root + donor resolution
    template_map.py           # backward-compatible Sloan re-exports
    utils.py
    main.py                   # slide-render entry
    validate_cli.py           # slide-validate entry
    build_cli.py              # slide-build entry
  main.py                     # shim: python src/main.py
  validate_deck_spec.py       # shim: python src/validate_deck_spec.py
  inspect_template.py         # template / placeholder inspection
```

**Install:** `pip install -e .` then **`slide-render`** / **`slide-validate`** / **`slide-build`**, or keep using **`PYTHONPATH=src python src/main.py`** without install.

---

## 6. Tool-ready checklist

| Item | Status |
|------|--------|
| Deterministic `render_deck` | **Ready** |
| `validate_deck_payload` / `validate_deck_spec` | **Ready** |
| `load_json` | **Ready** |
| `slide_automation.api` + package install | **Ready** |
| CLI, shims, `slide-render` / `slide-validate` / `slide-build` | **Ready** |
| Editorial / layout human docs | **Ready** |
| `generate_deck_spec` implementation | **Not built** |

---

*This file is the integration contract for local use. Implementation details may evolve; keep this doc updated when the public API or packaging changes.*
