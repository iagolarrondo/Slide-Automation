"""Optional MCP-oriented thin wrapper over ``slide_automation.api`` (transport-agnostic v1).

Not required for the usual local workflow (deck JSON on disk → ``slide-build`` /
``slide-validate`` + ``slide-render``). Handlers return plain ``dict`` results
aligned with ``docs/mcp_tool_surface_v1.md``. The optional **stdio MCP host**
lives in ``slide_automation.mcp.server_stdio``; see ``docs/mcp_wrapper.md`` and
``server_skeleton`` for context.
"""

from __future__ import annotations

from slide_automation.mcp.tools_v1 import (
    TOOL_REGISTRY_V1,
    tool_render_deck,
    tool_validate_deck_spec,
)

__all__ = [
    "TOOL_REGISTRY_V1",
    "tool_validate_deck_spec",
    "tool_render_deck",
]
