"""Backward-compatible re-exports for Sloan donor slide mapping.

New code should import from ``slide_automation.template_registry.sloan`` (or
``slide_automation.template_registry``) instead.
"""

from __future__ import annotations

from .template_registry.sloan import (
    DONOR_SLIDE_CONFIG,
    SLIDE_TYPE_MAP,
    DonorSlideMapping,
    get_donor_mapping,
)

__all__ = [
    "DONOR_SLIDE_CONFIG",
    "SLIDE_TYPE_MAP",
    "DonorSlideMapping",
    "get_donor_mapping",
]
