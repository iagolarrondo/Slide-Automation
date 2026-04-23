"""Template profile model for multi-donor rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


# Agenda: Sloan donor table + row-aligned logos (current production behavior).
AGENDA_SLOAN_DONOR_TABLE = "sloan_donor_table"
# Generic: write agenda_items into mapped placeholder / body fallback (for future templates).
AGENDA_PLACEHOLDER_LIST = "placeholder_list"


@dataclass(frozen=True)
class TemplateProfile:
    """Bundled configuration for one donor-deck family."""

    id: str
    label: str
    default_donor_relative: str
    slide_type_map: Dict[str, Dict[str, Any]]
    agenda_render_mode: str
    is_implemented: bool
