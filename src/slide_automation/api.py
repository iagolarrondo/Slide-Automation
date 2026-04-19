"""Stable public entry points for local CLIs and scripts.

Prefer importing from this module rather than reaching into ``renderer`` or ``utils``
directly, so names stay stable as internals evolve.
"""

from __future__ import annotations

from .renderer import render_deck
from .utils import (
    SUPPORTED_SLIDE_TYPES,
    load_json,
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
