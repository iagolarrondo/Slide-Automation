# MCP tool surface — v1 (specification only)

> **Future / optional integration** — For hosts (e.g. MCP) that call validate/render with JSON-shaped payloads. If you only run the renderer on your Mac from files exported by ChatGPT Project, use **`slide_automation.api`** or **`slide-build`** instead; you do not need this doc day-to-day.

This document defines the **MCP-facing tool surface** for slide automation: tool names, payloads, and result shapes. An **optional** stdio MCP host lives in `slide_automation.mcp.server_stdio`; implementers can still map this contract to other transports or hosts.

**Transport-agnostic handlers** (dict in / dict out) live in **`slide_automation.mcp`** — see [`mcp_wrapper.md`](mcp_wrapper.md). Canonical lower-level API remains **`slide_automation.api`** — [`tool_contract.md`](tool_contract.md), **Public API / CLI surface (v1)**.

---

## Conventions (all tools)

- **Paths** are host filesystem strings (absolute paths recommended).
- **Deck spec** is the same object shape as today’s renderer JSON: top-level `deck_title` (string), `slides` (array of slide objects with `"type"` and type-specific fields). See examples under `examples/`.
- **Success** responses should be machine-parseable (e.g. JSON object with a `ok: true` field and tool-specific fields).
- **Failure** should distinguish at least: **invalid input** (bad paths, malformed JSON), **validation failed** (spec does not pass `validate_deck_spec`), **render failed** (template missing, layout error, I/O error).

---

## Tool: `validate_deck_spec`

### Purpose

Check that a deck JSON file (or inlined spec) is structurally acceptable for rendering: supported slide `type` values, required fields per type, and **advisory** title/block-title length warnings. Does **not** write a `.pptx`.

### Input payload (suggested shape)

Minimal, file-based (typical for MCP):

```json
{
  "deck_spec_path": "/abs/path/to/deck.json",
  "quiet_warnings": false
}
```

Optional future variant (not required for v1): `deck_spec` as an inlined JSON object instead of `deck_spec_path` — same schema as file contents.

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| `deck_spec_path` | string | yes | Path to UTF-8 JSON file containing the deck spec. |
| `quiet_warnings` | boolean | no | If true, omit length advisory warnings from the result (errors unchanged). |

### Output payload (success)

```json
{
  "ok": true,
  "errors": [],
  "warnings": [
    "slides[3].title: 99 chars (advisory max 58 for layout); may overflow in PowerPoint — shorten in the spec if needed."
  ],
  "warning_count": 1
}
```

- **`errors`**: always present; empty array means the spec passed validation.
- **`warnings`**: advisory strings (same semantics as today’s validator / renderer hints); may be empty or omitted when `quiet_warnings` is true.

### Failure behavior

| Condition | Suggested tool result |
|-----------|------------------------|
| Missing `deck_spec_path` or file not found | `ok: false`, `error_code`: `"file_not_found"`, human-readable `message`. |
| File is not valid JSON or not a top-level object | `ok: false`, `error_code`: `"invalid_json"`, `message`. |
| Spec fails validation | `ok: false`, `error_code`: `"validation_failed"`, `errors`: array of strings (same as Python `validate_deck_spec` first element), `warnings` optional. |

Exit / transport: map to MCP tool error or structured failure per host conventions; callers must not treat a failed validation as success.

---

## Tool: `render_deck`

### Purpose

Produce a **`.pptx`** on disk from a deck spec JSON file and a Sloan template `.pptx`, using the existing renderer (`render_deck`). Optionally skip render if strict validation fails first (recommended default for agents).

### Input payload (suggested shape)

```json
{
  "template_path": "/abs/path/to/Sloan_Template.pptx",
  "deck_spec_path": "/abs/path/to/deck.json",
  "output_path": "/abs/path/out/rendered.pptx",
  "run_validate_first": true
}
```

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| `template_path` | string | yes | Sloan working `.pptx` template. |
| `deck_spec_path` | string | yes | UTF-8 JSON deck spec. |
| `output_path` | string | yes | Destination `.pptx` (parent directories may be created). |
| `run_validate_first` | boolean | no | Default **true**: run equivalent of `validate_deck_spec` before render; if any **errors**, do not call `render_deck`. |

### Output payload (success)

```json
{
  "ok": true,
  "output_path": "/abs/path/out/rendered.pptx",
  "validation_warnings": []
}
```

If `run_validate_first` is true and warnings exist but no errors, still render and return **`validation_warnings`** (same strings as validate tool) so the client can log them.

### Failure behavior

| Condition | Suggested tool result |
|-----------|------------------------|
| Missing path, template not found, unreadable spec | `ok: false`, `error_code`: `"file_not_found"` or `"invalid_json"`, `message`. |
| `run_validate_first` true and validation has errors | `ok: false`, `error_code`: `"validation_failed"`, `errors`: string array; **no** output file (or remove partial file if created). |
| Template layout / mapping error during render | `ok: false`, `error_code`: `"render_failed"`, `message` (e.g. `ValueError` / `FileNotFoundError` text from Python). |
| Write failure (permissions, disk full) | `ok: false`, `error_code`: `"io_error"`, `message`. |

Renderer may still print **`[title-length]`** lines to stderr during render; MCP implementations may capture stderr into logs; they are **not** tool failures.

---

## Not in MCP v1: `generate_deck_spec`

**Deck-spec generation** (LLM + project context → JSON) is **out of scope** for this MCP v1 surface. Agents should produce or edit JSON using separate instructions (e.g. [`deck_generation_source_of_truth.md`](deck_generation_source_of_truth.md)) and then call **`validate_deck_spec`** and **`render_deck`** only.

A future **v2** MCP surface may add `generate_deck_spec` with its own payload contract when an implementation exists in-repo or behind a defined service.

---

*This file is the MCP tool contract. Keep it in sync with `slide_automation.mcp` tool names and behavior.*
