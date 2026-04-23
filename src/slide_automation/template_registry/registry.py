"""Registry of built-in template profiles and donor path resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

from .models import TemplateProfile
from .sloan import SLOAN_PROFILE
from .wd import WD_PROFILE

_TEMPLATE_BY_ID: Dict[str, TemplateProfile] = {
    SLOAN_PROFILE.id: SLOAN_PROFILE,
    WD_PROFILE.id: WD_PROFILE,
}


def repo_root() -> Path:
    """Repository root (directory containing ``src/`` and ``templates/``)."""
    # src/slide_automation/template_registry/registry.py -> parents[3] == repo root
    return Path(__file__).resolve().parents[3]


def list_template_ids() -> Iterable[str]:
    return sorted(_TEMPLATE_BY_ID.keys())


def get_template_profile(template_id: str | None) -> TemplateProfile:
    tid = str(template_id or "sloan").strip().lower()
    profile = _TEMPLATE_BY_ID.get(tid)
    if profile is None:
        known = ", ".join(list_template_ids())
        raise ValueError(f"Unknown template_id {tid!r}. Known ids: {known}.")
    return profile


def default_donor_path(template_id: str | None) -> Path:
    """Absolute path to the default donor deck for ``template_id``."""
    profile = get_template_profile(template_id or "sloan")
    return (repo_root() / profile.default_donor_relative).resolve()


def resolve_cli_donor_path(*, template_id: str | None, template_override: str | Path | None) -> Path:
    """Resolve donor ``.pptx`` path for CLIs: explicit ``--template`` overrides the bundled default."""
    if template_override is not None:
        return Path(template_override).expanduser().resolve()
    return default_donor_path(template_id)
