"""MCP host notes and re-export of ``TOOL_REGISTRY_V1``.

**Runnable stdio host:** ``slide_automation.mcp.server_stdio`` (see
``docs/mcp_wrapper.md``). It registers ``validate_deck_spec`` and ``render_deck``
and delegates payloads through ``TOOL_REGISTRY_V1`` — no duplicated validation
or rendering.

TODO (transport / product): SSE or streamable HTTP behind auth; map tool
failures to richer MCP errors if needed; observability (correlation IDs,
stderr for ``[title-length]`` hints). Operational TODOs for trust and paths live
in ``server_stdio``'s module docstring.
"""

from __future__ import annotations

# Re-export for hosts that prefer a single import from "server" module.
from slide_automation.mcp.tools_v1 import TOOL_REGISTRY_V1

__all__ = ["TOOL_REGISTRY_V1"]
