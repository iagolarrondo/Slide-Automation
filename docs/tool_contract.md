# Slide automation — tool contract (API & CLI)

**Primary workflow today:** deck spec JSON (e.g. from **ChatGPT Project** or hand-written files) on your machine → **`slide-validate`** / **`slide-build`** / **`slide-render`** using **`slide_automation.api`**. No MCP or remote hosting is required.

This document also defines how **optional** integrators (agents with tools, MCP hosts) should think about **this repository** as a **two-stage** capability: **deck-spec generation** (editorial, LLM-heavy) vs **PPT rendering** (deterministic, template-bound).

Related docs:

- Editorial rules for specs: [`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md)
- Sloan layout / placeholder rules: [`slide_layout_specs_sloan_poc.md`](slide_layout_specs_sloan_poc.md)
- Smoke JSON and tests: [`testing.md`](testing.md)

---

## Public API / CLI surface (v1)

The following are the **current stable callable surface** for v1: local scripts and CLIs first; **optional** MCP-style integrations second. Prefer **`slide_automation.api`** (or the **`slide_automation`** package root—same exports) over importing **`slide_automation.renderer`** or **`slide_automation.utils`** directly unless you need internals.

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
| **`slide-validate`** | Validate a deck JSON file (`--input`, optional `--quiet-warnings`). |
| **`slide-render`** | Render JSON → PPTX (`--template`, `--input`, `--output`, optional `--quiet`). |
| **`slide-build`** | **One-step local workflow:** `validate_deck_spec` then `render_deck` if valid (`--template`, `--input` *or* `--latest-from DIR`, optional `--output`, optional `--quiet-warnings`). Default output: `./output/<input-stem>.pptx`. See [`local_one_step_render.md`](local_one_step_render.md). |

**Repo shims** — `python src/main.py` and `python src/validate_deck_spec.py` — invoke the same implementations and remain supported for local use with `PYTHONPATH=src`; they are not a second public naming layer.

**MCP-oriented dict handlers** (optional; not required for the ChatGPT Project → local file workflow): **`slide_automation.mcp`** — see [`mcp_wrapper.md`](mcp_wrapper.md) and [`mcp_tool_surface_v1.md`](mcp_tool_surface_v1.md).

---

## 1. Purpose

**Goal**  
Enable reliable automation: an agent produces (or edits) a **structured deck spec**, then invokes a **renderer** to produce an editable **`.pptx`** from a fixed Sloan working template.

**Scope of this repo today**  
The codebase is **render-complete** for a defined JSON shape and template map. The **v1 public surface** is `slide_automation.api` plus **`slide-render`** / **`slide-validate`** / **`slide-build`** (see above); `src/main.py` shims mirror the render CLI for workflows that do not use an editable install.

**Out of scope for this document**  
MCP transport, OAuth, hosted template storage, and full schema validation beyond the current lightweight checks.

---

## 2. Deck-spec generation vs PPT rendering

| Stage | Role | Owner | Input | Output |
|--------|------|--------|--------|--------|
| **Deck-spec generation** | Turn goals, sources, and storyline into **JSON** that matches renderer expectations. | **Agent + human editorial rules** ([`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md)) | Natural language, project files, prior thread | `dict` / JSON file: `deck_title`, `slides[]` with `"type"` and per-slide fields |
| **PPT rendering** | Map spec → **python-pptx** operations using **template_map** + **Sloan .pptx**. | **This repo** (`renderer.render_deck`, `template_map`, `utils`) | Parsed spec `dict`, path to template `.pptx`, output path | Written `.pptx` on disk |

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
| **Template path** | Yes | Filesystem path to Sloan **`.pptx`** working copy (mapped in `src/slide_automation/template_map.py`). |
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
- Template file exists and **layout indices** in `slide_automation/template_map.py` match the inspected template.
- Deck spec uses **`"type"`** on each slide (not `slide_type`).

### 3.4 Limitations

- **Validation** is lightweight (not full JSON Schema parity with `schemas/`).
- **Footer / slide number**: written only to **native** materialized placeholders; often absent; **no** textbox fallback.
- **Title length**: renderer warns but does **not** shorten; overflow is a **spec + PowerPoint** concern.
- **`background_image`** mapped but **not** implemented in renderer.
- **No in-process `generate_deck_spec`** in this repo yet—agents generate JSON by other means (see §5).

---

## 4. Callable interface (current vs recommended)

Today the **working** pipeline is:

```text
load_json(path) → dict
validate_deck_payload(dict) → list[str]   # empty == ok
render_deck(template_path, payload, output_path) → Path
```

### 4.1 `render_deck` (implemented)

**Signature** (see `src/slide_automation/renderer.py`):

```python
def render_deck(
    template_path: str | Path,
    payload: Dict[str, Any],
    output_path: str | Path,
) -> Path: ...
```

**Contract**  
- **Raises** `FileNotFoundError` if template missing.  
- **Raises** `ValueError` for unsupported `slide.type` or bad `layout_index`.  
- **Does not** validate payload shape; callers should validate first.

**Agent usage**  
Pass an in-memory `dict` (from JSON parse) plus absolute paths for template and output.

---

### 4.2 `validate_deck_spec` (implemented)

**Library**: `utils.validate_deck_spec(payload: Dict[str, Any]) -> tuple[list[str], list[str]]`  
Returns **`(errors, warnings)`**. `errors` combines shape checks from `validate_deck_payload` plus **required-field** rules per slide type. `warnings` lists **advisory title / block-title length** risks (same thresholds as the renderer’s stderr hints). Empty `errors` means the spec is OK to render.

**CLI** (repo root, `PYTHONPATH=src`):

```bash
python src/validate_deck_spec.py --input examples/example_deck_v1.json
```

Exit codes: **`0`** valid (warnings may print to stderr), **`2`** validation errors, **`1`** file/JSON parse errors. Use **`--quiet-warnings`** to hide length warnings.

The older **`validate_deck_payload`** remains the subset used by `main.py` before render; stricter **`validate_deck_spec`** is the basis for agents and future MCP.

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

1. Use ChatGPT (or similar) with [`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md) + [`slide_layout_specs_sloan_poc.md`](slide_layout_specs_sloan_poc.md) as instructions.  
2. Emit JSON matching `validate_deck_*` expectations.  
3. Call `validate_deck_payload` then `render_deck`.

---

## 5. Packaging layout (implemented baseline)

```text
pyproject.toml              # setuptools; scripts slide-render / slide-validate / slide-build (+ optional MCP)
src/
  slide_automation/
    __init__.py               # public re-exports
    api.py                    # stable import surface for tools
    renderer.py
    template_map.py
    utils.py
    main.py                   # slide-render entry
    validate_cli.py           # slide-validate entry
    build_cli.py              # slide-build entry
    mcp/                      # optional dict tools + stdio MCP host (see mcp_wrapper.md)
  main.py                     # shim: python src/main.py
  validate_deck_spec.py       # shim: python src/validate_deck_spec.py
  inspect_template.py
  placeholder_probe.py
  image_content_probe.py
```

**Install:** `pip install -e .` then **`slide-render`** / **`slide-validate`** / **`slide-build`**, or keep using **`PYTHONPATH=src python src/main.py`** without install.

**MCP (optional)**  
An optional **stdio** MCP process ships in-repo (`slide-automation-mcp`, `slide_automation.mcp`). It is **not** part of the default ChatGPT Project → local JSON workflow. Hardened auth, remote hosting, and brokered path policy are still **out of scope** here — see MCP docs TODOs.

---

## 6. Tool-ready checklist

| Item | Status |
|------|--------|
| Deterministic `render_deck` | **Ready** |
| `validate_deck_payload` / `validate_deck_spec` | **Ready** |
| `load_json` | **Ready** |
| `slide_automation.api` + package install | **Ready** |
| CLI, shims, `slide-render` / `slide-validate` | **Ready** |
| Editorial / layout human docs | **Ready** |
| `generate_deck_spec` implementation | **Not built** |
| Optional MCP stdio host + dict handlers | **Available** (`slide_automation.mcp`; install `[mcp-server]` extra) |
| Production MCP auth / multi-tenant hosting | **Not built** |

---

*This file is the integration contract for local use and optional tool hosts. Implementation details may evolve; keep this doc updated when the public API or packaging changes.*
