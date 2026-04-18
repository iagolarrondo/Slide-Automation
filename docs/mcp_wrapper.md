# MCP wrapper layer (`slide_automation.mcp`)

> **Future / optional integration** — Not part of the day-to-day workflow for most users today (typical path: ChatGPT Project → deck JSON on disk → local **`slide-build`** / **`slide-validate`** + **`slide-render`**). This package and docs remain for when you wire an MCP client or other dict-based host to the same tools.

## What this is

A **thin, transport-agnostic** layer under **`slide_automation.mcp`** that exposes the v1 MCP tool contract as **plain Python callables**: each accepts a **`dict`** payload (aligned with [`mcp_tool_surface_v1.md`](mcp_tool_surface_v1.md)) and returns a **`dict`** result (`ok`, `error_code`, etc.). It **only** calls **`slide_automation.api`** (`load_json`, `validate_deck_spec`, `render_deck`) — no duplicated validation or rendering logic.

The **handlers** stay **SDK-free** (`tools_v1.py`) so tests and other hosts can import them without the `mcp` package. A **minimal stdio MCP server** (`server_stdio.py`) optionally depends on the official SDK and forwards tool calls through **`TOOL_REGISTRY_V1`**.

## Runnable MCP server (stdio)

The MCP Python SDK targets **Python 3.10+**. Install the extra and start the server:

```bash
pip install -e ".[mcp-server]"
slide-automation-mcp
```

Equivalent module invocation:

```bash
python -m slide_automation.mcp.server_stdio
```

The process uses **stdio** for MCP framing; do not print debug output to stdout. Configure your MCP client to launch the command above (working directory and env as you prefer).

**TODOs** (auth, path policy, output handling, future `generate_deck_spec`) are called out in the module docstring at `src/slide_automation/mcp/server_stdio.py`.

## What is implemented

| Piece | Location |
|--------|-----------|
| **`tool_validate_deck_spec`** | `slide_automation.mcp.tools_v1` |
| **`tool_render_deck`** | `slide_automation.mcp.tools_v1` |
| **`TOOL_REGISTRY_V1`** | name → callable map for hosts |
| **Stdio MCP host** | `slide_automation.mcp.server_stdio` (optional `[mcp-server]` extra) |
| **Skeleton / notes** | `slide_automation.mcp.server_skeleton` |

## What is intentionally missing

- **SSE / HTTP MCP transports** and production auth — not implemented here
- **`generate_deck_spec`** — not in v1 (see MCP tool surface doc)
- **Centralized path sandboxing** — documented as TODOs in `server_stdio.py`

## Quick usage (Python)

```python
from slide_automation.mcp import tool_validate_deck_spec, tool_render_deck

r = tool_validate_deck_spec({"deck_spec_path": "/path/to/deck.json"})
# r["ok"] is True or False; see mcp_tool_surface_v1.md for shapes
```

After `pip install -e .`, the `slide_automation.mcp` subpackage is on the default import path. For MCP over stdio, use **`slide-automation-mcp`** (see **Runnable MCP server** above).
