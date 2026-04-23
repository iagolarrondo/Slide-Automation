"""Built-in template profiles (Sloan, WD) and registry helpers."""

from .registry import (
    default_donor_path,
    get_template_profile,
    list_template_ids,
    repo_root,
    resolve_cli_donor_path,
)
from .sloan import (
    DONOR_SLIDE_CONFIG,
    SLIDE_TYPE_MAP,
    DonorSlideMapping,
    SLOAN_PROFILE,
    get_donor_mapping,
)
from .wd import WD_CONTENT_INDICES, WD_PROFILE, WD_SLIDE_TYPE_MAP

__all__ = [
    "DONOR_SLIDE_CONFIG",
    "SLIDE_TYPE_MAP",
    "DonorSlideMapping",
    "SLOAN_PROFILE",
    "WD_PROFILE",
    "WD_SLIDE_TYPE_MAP",
    "WD_CONTENT_INDICES",
    "default_donor_path",
    "get_donor_mapping",
    "get_template_profile",
    "list_template_ids",
    "repo_root",
    "resolve_cli_donor_path",
]
