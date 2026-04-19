from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DonorSlideMapping:
    donor_slide_number: int
    expected_layout_name: str
    placeholders: Dict[str, Any]


DONOR_SLIDE_CONFIG: Dict[str, DonorSlideMapping] = {
    "cover": DonorSlideMapping(
        donor_slide_number=1,
        expected_layout_name="Cover",
        placeholders={
            "title": 0,
            "subtitle": 1,
            "date": 11,
        },
    ),
    "agenda": DonorSlideMapping(
        donor_slide_number=2,
        expected_layout_name="Agenga",
        placeholders={
            "agenda_items": {"shape_index": 0},
        },
    ),
    "divider": DonorSlideMapping(
        donor_slide_number=3,
        expected_layout_name="Divider",
        placeholders={
            "title": 0,
            # Divider numeric box (large number) is a body placeholder at idx=11.
            "section_number": 11,
        },
    ),
    "standard_1_block": DonorSlideMapping(
        donor_slide_number=4,
        expected_layout_name="Standard – 1 Block",
        placeholders={
            "title": 0,
            "footer": 13,
            "section_title": 17,
            "block_title": 15,
            "block_body": 16,
        },
    ),
    "standard_2_block": DonorSlideMapping(
        donor_slide_number=5,
        expected_layout_name="Standard – 2 Blocks",
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
    "standard_3_block": DonorSlideMapping(
        donor_slide_number=6,
        expected_layout_name="Standard – 3 Blocks",
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
    "standard_2_block_big_left": DonorSlideMapping(
        donor_slide_number=7,
        expected_layout_name="Standard – 2 Blocks – Big Left",
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
    "standard_2_block_big_right": DonorSlideMapping(
        donor_slide_number=8,
        expected_layout_name="Standard – 2 Blocks – Big Right",
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
    "narrow_image_content": DonorSlideMapping(
        donor_slide_number=9,
        expected_layout_name="Narrow Image and Content",
        placeholders={
            "title": 0,
            "footer": 14,
            "section_title": 17,
            "content_block_title": 23,
            "content_block_body": 22,
        },
    ),
    "wide_image_content": DonorSlideMapping(
        donor_slide_number=10,
        expected_layout_name="Wide Image and Content",
        placeholders={
            "title": 0,
            "footer": 10,
            "section_title": 17,
            "content_block_title": 2,
            "content_block_body": 2,
        },
    ),
}

SLIDE_TYPE_MAP: Dict[str, Dict[str, Any]] = {
    slide_type: {
        "donor_slide_number": mapping.donor_slide_number,
        "expected_layout_name": mapping.expected_layout_name,
        "placeholders": mapping.placeholders,
    }
    for slide_type, mapping in DONOR_SLIDE_CONFIG.items()
}


def get_donor_mapping(slide_type: str) -> Optional[DonorSlideMapping]:
    return DONOR_SLIDE_CONFIG.get(slide_type)
