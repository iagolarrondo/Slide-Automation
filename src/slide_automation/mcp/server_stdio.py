"""Minimal MCP stdio host for v1 tools (``validate_deck_spec``, ``render_deck``).

Developer note — run locally
----------------------------

Requires **Python 3.10+** (the official ``mcp`` SDK does not support 3.9).

From the repo root, with the package editable and the MCP extra::

    pip install -e ".[mcp-server]"
    slide-automation-mcp

The process speaks **MCP over stdio** (no HTTP). Point your MCP client
(Cursor, Claude Desktop, MCP Inspector, etc.) at the command above, or run::

    python -m slide_automation.mcp.server_stdio

Do not wrap the server in a shell that writes to stdout; MCP frames use stdout.

TODO (out of scope for this skeleton)
-------------------------------------

- **Auth / trust boundary** — today any client that can spawn this process can
  supply arbitrary filesystem paths; decide identity, policy, and whether
  tools should run in a sandbox or behind a broker.
- **Filesystem path policy** — resolve/validate paths (working directory roots,
  allowlists, symlink rules) before passing strings to ``TOOL_REGISTRY_V1``.
- **Output file handling** — retention, quotas, atomic writes, returning bytes
  or signed URLs instead of host-local ``output_path``.
- **Future ``generate_deck_spec``** — register a third tool when a deterministic
  spec generator exists; keep the same thin delegation pattern as below.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any, Dict

from slide_automation.mcp.tools_v1 import TOOL_REGISTRY_V1

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def _build_app() -> "FastMCP":
    """Construct FastMCP with tools backed by ``TOOL_REGISTRY_V1`` (no duplicated logic)."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - exercised when extra missing
        raise RuntimeError(
            "The 'mcp' package is required for the MCP server. "
            "Install with: pip install 'slide-automation[mcp-server]'"
        ) from exc

    app = FastMCP("slide-automation", json_response=True)

    @app.tool()
    def validate_deck_spec(deck_spec_path: str, quiet_warnings: bool = False) -> Dict[str, Any]:
        """Validate deck JSON (types, required fields, advisory title lengths)."""
        return TOOL_REGISTRY_V1["validate_deck_spec"](
            {"deck_spec_path": deck_spec_path, "quiet_warnings": quiet_warnings}
        )

    @app.tool()
    def render_deck(
        template_path: str,
        deck_spec_path: str,
        output_path: str,
        run_validate_first: bool = True,
    ) -> Dict[str, Any]:
        """Render deck JSON to PPTX using the Sloan template working copy."""
        return TOOL_REGISTRY_V1["render_deck"](
            {
                "template_path": template_path,
                "deck_spec_path": deck_spec_path,
                "output_path": output_path,
                "run_validate_first": run_validate_first,
            }
        )

    return app


def main() -> None:
    if sys.version_info < (3, 10):
        print("slide-automation-mcp requires Python >=3.10 (MCP SDK).", file=sys.stderr)
        sys.exit(1)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    try:
        app = _build_app()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
