"""Slide automation: JSON deck specs → PowerPoint (Sloan template)."""

from __future__ import annotations

from .api import (
    SUPPORTED_SLIDE_TYPES,
    load_json,
    render_deck,
    validate_deck_payload,
    validate_deck_spec,
)

__all__ = [
    "load_json",
    "validate_deck_spec",
    "validate_deck_payload",
    "render_deck",
    "SUPPORTED_SLIDE_TYPES",
]
