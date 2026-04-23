"""Slide automation: JSON deck specs → PowerPoint (multi-template engine; Sloan default)."""

from __future__ import annotations

from .api import (
    SUPPORTED_SLIDE_TYPES,
    SUPPORTED_WD_SLIDE_TYPES,
    effective_template_id,
    load_json,
    render_deck,
    supported_slide_types,
    validate_deck_payload,
    validate_deck_spec,
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
