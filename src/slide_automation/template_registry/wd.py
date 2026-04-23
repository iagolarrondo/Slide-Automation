"""WD donor deck: slide mapping for ``templates/WD_Template_Donor.pptx``.

Agenda uses fixed donor variants (3–6 sections); the LLM picks ``wd_agenda_N`` to match
``len(agenda_items)``. No table row resize or geometry changes at render time.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .models import AGENDA_PLACEHOLDER_LIST, TemplateProfile

# Layout names from the packaged donor (python-pptx).
_L_COVER = "Presentation Title and Subtitle White"
_L_BLANK = "Blank White"
_L_CONTENT = "Title, Subtitle and Content Full White"


def _map_entry(
    donor_slide_number: int,
    expected_layout_name: str,
    placeholders: Dict[str, Any],
    *,
    wd_agenda_item_indices: tuple[int, ...] | None = None,
    wd_content_shape_indices: tuple[int, ...] | None = None,
    wd_editable_keys: tuple[str, ...] | None = None,
) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "donor_slide_number": donor_slide_number,
        "expected_layout_name": expected_layout_name,
        "placeholders": placeholders,
    }
    if wd_agenda_item_indices is not None:
        d["wd_agenda_item_indices"] = wd_agenda_item_indices
    if wd_content_shape_indices is not None:
        d["wd_content_shape_indices"] = wd_content_shape_indices
    if wd_editable_keys is not None:
        d["wd_editable_keys"] = wd_editable_keys
    return d


# Spatial read order for mosaic/tile content shapes (donor inventory).
WD_CONTENT_INDICES: Dict[str, tuple[int, ...]] = {
    "wd_mosaic_4": (4, 5, 7, 6),
    "wd_mosaic_6": (4, 5, 6, 8, 9, 7),
    "wd_mosaic_8": (4, 12, 16, 8, 5, 13, 17, 9),
    "wd_tile_4": (4, 5, 6, 7),
    "wd_tile_5": (4, 5, 6, 7, 8),
    "wd_tile_6": (4, 5, 6, 7, 10, 8),
}

WD_SLIDE_TYPE_MAP: Dict[str, Dict[str, Any]] = {
    "wd_cover": _map_entry(
        1,
        _L_COVER,
        {
            "title": 0,
            "presenter": 11,
            "subtitle": 14,
            "date": 15,
        },
        wd_editable_keys=("title", "presenter", "subtitle", "date"),
    ),
    "wd_agenda_3": _map_entry(
        2,
        _L_BLANK,
        {"agenda_heading": {"shape_index": 6}},
        wd_agenda_item_indices=(7, 12, 11),
        wd_editable_keys=("agenda_heading",),
    ),
    "wd_agenda_4": _map_entry(
        3,
        _L_BLANK,
        {"agenda_heading": {"shape_index": 7}},
        wd_agenda_item_indices=(8, 4, 15, 14),
        wd_editable_keys=("agenda_heading",),
    ),
    "wd_agenda_5": _map_entry(
        4,
        _L_BLANK,
        {"agenda_heading": {"shape_index": 7}},
        wd_agenda_item_indices=(8, 20, 4, 15, 14),
        wd_editable_keys=("agenda_heading",),
    ),
    "wd_agenda_6": _map_entry(
        5,
        _L_BLANK,
        {"agenda_heading": {"shape_index": 7}},
        wd_agenda_item_indices=(8, 20, 4, 15, 23, 14),
        wd_editable_keys=("agenda_heading",),
    ),
    "wd_divider": _map_entry(
        6,
        _L_BLANK,
        {"divider_text": {"shape_index": 2}},
        wd_editable_keys=("divider_text",),
    ),
    "wd_section_intro": _map_entry(
        7,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 4},
            # Donor slide 7 has two grouped content boxes:
            # Group 16 (left): child 1 title, child 0 body
            # Group 13 (right): child 1 title, child 0 body
            "box_1_title": {"shape_index": 6, "group_child_index": 1},
            "box_1_body": {"shape_index": 6, "group_child_index": 0},
            "box_2_title": {"shape_index": 5, "group_child_index": 1},
            "box_2_body": {"shape_index": 5, "group_child_index": 0},
        },
        wd_editable_keys=(
            "title",
            "section_title",
            "footer",
            "box_1_title",
            "box_1_body",
            "box_2_title",
            "box_2_body",
        ),
    ),
    "wd_two_column": _map_entry(
        8,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "left_block": {"shape_index": 1},
            "right_block": {"shape_index": 5},
            "footer": {"shape_index": 6},
        },
        wd_editable_keys=("title", "section_title", "left_block", "right_block", "footer"),
    ),
    "wd_three_column": _map_entry(
        10,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "col_1": {"shape_index": 1},
            "col_2": {"shape_index": 5},
            "col_3": {"shape_index": 6},
            "footer": {"shape_index": 7},
        },
        wd_editable_keys=("title", "section_title", "col_1", "col_2", "col_3", "footer"),
    ),
    "wd_four_column": _map_entry(
        12,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "col_1": {"shape_index": 1},
            "col_2": {"shape_index": 5},
            "col_3": {"shape_index": 7},
            "col_4": {"shape_index": 8},
            "footer": {"shape_index": 6},
        },
        wd_editable_keys=("title", "section_title", "col_1", "col_2", "col_3", "col_4", "footer"),
    ),
    "wd_two_column_alt": _map_entry(
        16,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "left_block": {"shape_index": 1},
            "right_block": {"shape_index": 6},
            "footer": {"shape_index": 5},
        },
        wd_editable_keys=("title", "section_title", "left_block", "right_block", "footer"),
    ),
    "wd_mosaic_4": _map_entry(
        17,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 12},
        },
        wd_content_shape_indices=WD_CONTENT_INDICES["wd_mosaic_4"],
        wd_editable_keys=("title", "section_title", "footer"),
    ),
    "wd_mosaic_6": _map_entry(
        18,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 16},
        },
        wd_content_shape_indices=WD_CONTENT_INDICES["wd_mosaic_6"],
        wd_editable_keys=("title", "section_title", "footer"),
    ),
    "wd_mosaic_8": _map_entry(
        19,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 20},
        },
        wd_content_shape_indices=WD_CONTENT_INDICES["wd_mosaic_8"],
        wd_editable_keys=("title", "section_title", "footer"),
    ),
    "wd_tile_4": _map_entry(
        20,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 9},
        },
        wd_content_shape_indices=WD_CONTENT_INDICES["wd_tile_4"],
        wd_editable_keys=("title", "section_title", "footer"),
    ),
    "wd_tile_5": _map_entry(
        21,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 10},
        },
        wd_content_shape_indices=WD_CONTENT_INDICES["wd_tile_5"],
        wd_editable_keys=("title", "section_title", "footer"),
    ),
    "wd_tile_6": _map_entry(
        22,
        _L_CONTENT,
        {
            "title": 0,
            "section_title": 12,
            "footer": {"shape_index": 9},
        },
        wd_content_shape_indices=WD_CONTENT_INDICES["wd_tile_6"],
        wd_editable_keys=("title", "section_title", "footer"),
    ),
}

WD_DEFAULT_DONOR = "templates/WD_Template_Donor.pptx"

WD_PROFILE = TemplateProfile(
    id="wd",
    label="WD donor deck",
    default_donor_relative=WD_DEFAULT_DONOR,
    slide_type_map=WD_SLIDE_TYPE_MAP,
    agenda_render_mode=AGENDA_PLACEHOLDER_LIST,
    is_implemented=True,
)


def get_wd_mapping(slide_type: str) -> Optional[Dict[str, Any]]:
    return WD_SLIDE_TYPE_MAP.get(slide_type)
