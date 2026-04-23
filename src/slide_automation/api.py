"""Stable public entry points for local CLIs and scripts.

Prefer importing from this module rather than reaching into ``renderer`` or ``utils``
directly, so names stay stable as internals evolve.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .renderer import render_deck as _renderer_render_deck
from .template_registry.registry import get_template_profile
from .utils import (
    SUPPORTED_SLIDE_TYPES,
    SUPPORTED_WD_SLIDE_TYPES,
    effective_template_id,
    load_json,
    supported_slide_types,
    validate_deck_payload,
    validate_deck_spec,
)


def render_deck(
    template_path: str | Path,
    payload: Dict[str, Any],
    output_path: str | Path,
    *,
    template_id: str | None = None,
    slide_type_map: Dict[str, Dict[str, Any]] | None = None,
    agenda_render_mode: str | None = None,
) -> Path:
    """Render deck JSON to ``.pptx``.

    Args:
        template_path: Donor ``.pptx`` / ``.potx`` used for layout cloning.
        payload: Parsed deck spec.
        output_path: Destination ``.pptx``.
        template_id: When set, loads ``slide_type_map`` / ``agenda_render_mode`` from the
            built-in registry unless those kwargs are provided explicitly.
        slide_type_map: Optional mapping override (advanced / tests).
        agenda_render_mode: Optional agenda strategy override.

    Returns:
        Resolved output path.
    """
    if template_id is not None:
        profile = get_template_profile(template_id)
        if not profile.is_implemented:
            raise ValueError(f"Template {template_id!r} is not implemented yet.")
        if slide_type_map is None:
            slide_type_map = profile.slide_type_map
        if agenda_render_mode is None:
            agenda_render_mode = profile.agenda_render_mode
    return _renderer_render_deck(
        template_path,
        payload,
        output_path,
        slide_type_map=slide_type_map,
        agenda_render_mode=agenda_render_mode,
    )


__all__ = [
    "load_json",
    "validate_deck_spec",
    "validate_deck_payload",
    "render_deck",
    "SUPPORTED_SLIDE_TYPES",
    "SUPPORTED_WD_SLIDE_TYPES",
    "supported_slide_types",
    "effective_template_id",
]
