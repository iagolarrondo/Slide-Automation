# MCP server runbook (local)

> **Future / optional** — Use this when you intentionally run the MCP stdio server. Normal local rendering does not require MCP; see [`local_one_step_render.md`](local_one_step_render.md) for **`slide-build`**.

Practical steps to launch and debug the **stdio** MCP host for Slide Automation. Contract details: [`mcp_tool_surface_v1.md`](mcp_tool_surface_v1.md), architecture: [`mcp_wrapper.md`](mcp_wrapper.md).

## 1. Required Python version

- **MCP stdio server:** **Python 3.10+** (the `mcp` package does not support 3.9).
- The core library still supports 3.9 for `slide-render` / `slide-validate`; use a **separate 3.10+ venv** for the MCP server if your default is 3.9.

## 2. Create and activate the environment

From the repo root:

```bash
python3.12 -m venv .venv-mcp    # or python3.11 / python3.10
source .venv-mcp/bin/activate   # Windows: .venv-mcp\Scripts\activate
```

Confirm:

```bash
python --version   # should show 3.10.x or newer
```

## 3. Install the MCP extra

Editable install **with** the optional extra (installs `mcp` and wires `slide-automation-mcp`):

```bash
pip install -e ".[mcp-server]"
```

If you use `requirements.txt` for the base app only, you still need the line above (or equivalent) so `mcp` is present.

## 4. Launch the server

Either:

```bash
slide-automation-mcp
```

or:

```bash
python -m slide_automation.mcp.server_stdio
```

**Do not** wrap the process in something that prints to **stdout**; MCP uses stdout for protocol frames. Use **stderr** for ad-hoc debugging if needed.

Point your MCP client (Cursor, Claude Desktop, MCP Inspector, etc.) at this command, with **cwd** and env set so **paths you pass in tool args** resolve (template, deck JSON, output).

## 5. What successful startup looks like

- The process **starts and stays running** (it is waiting on **stdin** for MCP messages).
- **No immediate exit** with an error on stderr (our entrypoint exits early only on Python version or missing `mcp`).
- You may see **little or no output** until a client connects—that is normal for stdio MCP.
- After a client connects and calls tools, results are **structured JSON/dict-shaped** responses per the tool contract (e.g. `ok`, `errors`, `warnings`, `output_path`).

## 6. Common failure modes

| Symptom | Likely cause | What to do |
|--------|----------------|------------|
| Message about **Python >=3.10** and exit | Wrong interpreter | Recreate venv with 3.10+; ensure the client launches **that** `python` / venv `slide-automation-mcp`. |
| **`mcp` package is required** / install hint on stderr | Missing extra or wrong venv | Run `pip install -e ".[mcp-server]"` in the same env the client uses. |
| Import errors for **`slide_automation`** or stale behavior after `git pull` | Editable install not refreshed | `pip install -e ".[mcp-server]"` again from current repo root. |
| Tool returns **`ok: false`**, `error_code: file_not_found` / `invalid_json` | Bad or relative paths from the **client’s cwd** | Use absolute paths or set client cwd to repo root; confirm deck JSON and template `.pptx` exist. |
| **`validation_failed`** | Invalid deck spec | Fix spec or run `slide-validate` / `tool_validate_deck_spec` with same path to see `errors`. |
| **`file_not_found`** for template | Missing Sloan working copy | Add template under `templates/` (or path you pass); not committed in many setups. |
| **`render_failed`** / **`io_error`** | Permissions, bad output dir, corrupt template | Check `output_path` parent exists and is writable; validate template with `inspect_template` / project docs. |

## 7. What this server exposes (today)

- **`validate_deck_spec`** — validates a deck JSON file; returns `ok`, `errors`, `warnings`, etc.
- **`render_deck`** — renders a deck spec to `.pptx` using a template path, optional pre-validation.

## 8. What is intentionally not exposed yet

- **`generate_deck_spec`** — not part of this MCP host; no tool registered until a deterministic generator exists (see [`mcp_tool_surface_v1.md`](mcp_tool_surface_v1.md) / [`mcp_wrapper.md`](mcp_wrapper.md)).
