from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class LayoutMapping:
    layout_name: str
    placeholders: Dict[str, int]


LAYOUT_CONFIG: Dict[str, LayoutMapping] = {
    "cover": LayoutMapping(
        layout_name="Cover",
        placeholders={
            "title": 0,
            "subtitle": 1,
            "background_image": 10,
            "date": 11,
        },
    ),
    "agenda": LayoutMapping(
        layout_name="Agenga",
        placeholders={
            "background_image": 10,
            "agenda_items": 11,
        },
    ),
    "divider": LayoutMapping(
        layout_name="Divider",
        placeholders={
            "title": 0,
            "background_image": 10,
            "optional_subtitle": 11,
            "section_title": 12,
        },
    ),
    "standard_1_block": LayoutMapping(
        layout_name="Standard – 1 Block",
        placeholders={
            "title": 0,
            "footer": 13,
            "section_title": 17,
            "block_title": 15,
            "block_body": 16,
        },
    ),
    "standard_2_block": LayoutMapping(
        layout_name="Standard – 2 Blocks",
        placeholders={
            "title": 0,
            "footer": 13,
            "section_title": 17,
            "left_block_title": 15,
            "left_block_body": 16,
            "right_block_title": 19,
            "right_block_body": 18,
        },
    ),
    "standard_3_block": LayoutMapping(
        layout_name="Standard – 3 Blocks",
        placeholders={
            "title": 0,
            "footer": 13,
            "section_title": 17,
            "block_1_title": 15,
            "block_1_body": 16,
            "block_2_title": 21,
            "block_2_body": 22,
            "block_3_title": 19,
            "block_3_body": 20,
        },
    ),
    "standard_2_block_big_left": LayoutMapping(
        layout_name="Standard – 2 Blocks – Big Left",
        placeholders={
            "title": 0,
            "footer": 13,
            "section_title": 17,
            "dominant_block_title": 15,
            "dominant_block_body": 16,
            "secondary_block_title": 19,
            "secondary_block_body": 20,
        },
    ),
    "standard_2_block_big_right": LayoutMapping(
        layout_name="Standard – 2 Blocks – Big Right",
        placeholders={
            "title": 0,
            "footer": 13,
            "section_title": 17,
            "dominant_block_title": 21,
            "dominant_block_body": 22,
            "secondary_block_title": 15,
            "secondary_block_body": 16,
        },
    ),
    "narrow_image_content": LayoutMapping(
        layout_name="Narrow Image and Content",
        placeholders={
            "title": 0,
            "image": 10,
            "footer": 14,
            "section_title": 17,
            "content_block_title": 2,
            "content_block_body": 22,
        },
    ),
    "wide_image_content": LayoutMapping(
        layout_name="Wide Image and Content",
        placeholders={
            "title": 0,
            "image": 1,
            "footer": 10,
            "section_title": 17,
            "content_block_title": 14,
            "content_block_body": 2,
        },
    ),
}

# Renderer compatibility: slide type -> {"layout_index": int, "placeholders": {...}}
# Keep these indices aligned with your inspected template layout order.
_LAYOUT_INDEX_BY_NAME: Dict[str, int] = {
    "Cover": 0,
    "Agenga": 1,
    "Divider": 2,
    "Standard – 1 Block": 3,
    "Standard – 2 Blocks": 4,
    "Standard – 3 Blocks": 5,
    "Standard – 2 Blocks – Big Left": 6,
    "Standard – 2 Blocks – Big Right": 7,
    "Narrow Image and Content": 8,
    "Wide Image and Content": 9,
}

SLIDE_TYPE_MAP: Dict[str, Dict[str, Any]] = {
    slide_type: {
        "layout_index": _LAYOUT_INDEX_BY_NAME[mapping.layout_name],
        "placeholders": mapping.placeholders,
    }
    for slide_type, mapping in LAYOUT_CONFIG.items()
}


def get_layout_mapping(slide_type: str) -> Optional[LayoutMapping]:
    return LAYOUT_CONFIG.get(slide_type)
