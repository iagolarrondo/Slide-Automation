"""Transport-agnostic MCP v1 tool handlers — delegates to ``slide_automation.api``.

Payload shapes match ``docs/mcp_tool_surface_v1.md``. No MCP SDK dependency here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from slide_automation.api import load_json, render_deck, validate_deck_spec


def _fail(error_code: str, message: str, **extra: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": False, "error_code": error_code, "message": message}
    out.update(extra)
    return out


def tool_validate_deck_spec(payload: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool: ``validate_deck_spec`` — see ``docs/mcp_tool_surface_v1.md``."""
    path = payload.get("deck_spec_path")
    if path is None or not isinstance(path, str) or not path.strip():
        return _fail("file_not_found", "deck_spec_path is required and must be a non-empty string.")
    quiet = bool(payload.get("quiet_warnings", False))
    try:
        deck = load_json(path)
    except FileNotFoundError as exc:
        return _fail("file_not_found", str(exc))
    except ValueError as exc:
        return _fail("invalid_json", str(exc))

    errors, warnings = validate_deck_spec(deck)
    if errors:
        return {
            "ok": False,
            "error_code": "validation_failed",
            "errors": errors,
            "warnings": [] if quiet else warnings,
            "message": "Deck spec failed validation.",
        }
    w: List[str] = [] if quiet else warnings
    return {"ok": True, "errors": [], "warnings": w, "warning_count": len(w)}


def tool_render_deck(payload: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool: ``render_deck`` — see ``docs/mcp_tool_surface_v1.md``."""
    template_path = payload.get("template_path")
    deck_spec_path = payload.get("deck_spec_path")
    output_path = payload.get("output_path")
    for key, val in (
        ("template_path", template_path),
        ("deck_spec_path", deck_spec_path),
        ("output_path", output_path),
    ):
        if val is None or not isinstance(val, str) or not val.strip():
            return _fail(
                "file_not_found",
                f"{key} is required and must be a non-empty string.",
            )

    run_validate_first = payload.get("run_validate_first", True)
    if not isinstance(run_validate_first, bool):
        run_validate_first = True

    validation_warnings: List[str] = []

    if run_validate_first:
        v = tool_validate_deck_spec(
            {"deck_spec_path": deck_spec_path, "quiet_warnings": False}
        )
        if not v.get("ok"):
            return {
                "ok": False,
                "error_code": "validation_failed",
                "errors": v.get("errors", []),
                "warnings": v.get("warnings", []),
                "message": v.get("message", "Validation failed before render."),
            }
        validation_warnings = list(v.get("warnings") or [])

    try:
        deck = load_json(deck_spec_path)
    except FileNotFoundError as exc:
        return _fail("file_not_found", str(exc))
    except ValueError as exc:
        return _fail("invalid_json", str(exc))

    if not Path(template_path).exists():
        return _fail("file_not_found", f"Template not found: {template_path}")

    try:
        resolved = render_deck(
            template_path=Path(template_path),
            payload=deck,
            output_path=Path(output_path),
        )
    except FileNotFoundError as exc:
        return _fail("file_not_found", str(exc))
    except ValueError as exc:
        return _fail("render_failed", str(exc))
    except OSError as exc:
        return _fail("io_error", str(exc))

    return {
        "ok": True,
        "output_path": str(resolved),
        "validation_warnings": validation_warnings,
    }


# Registry for a future MCP host: name -> callable taking a single dict payload.
TOOL_REGISTRY_V1: Dict[str, Any] = {
    "validate_deck_spec": tool_validate_deck_spec,
    "render_deck": tool_render_deck,
}
