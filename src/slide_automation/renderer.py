"""Deck rendering logic using python-pptx and template mapping."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any, Dict, Optional

from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from .template_map import SLIDE_TYPE_MAP

CONTENT_MAIN_TITLE_TYPES = {
    "standard_1_block",
    "standard_2_block",
    "standard_3_block",
    "standard_2_block_big_left",
    "standard_2_block_big_right",
    "narrow_image_content",
    "wide_image_content",
}


def _clear_existing_slides(prs: Any) -> None:
    """Remove pre-existing slides from template-backed presentations."""
    slide_ids = list(prs.slides._sldIdLst)  # type: ignore[attr-defined]
    for slide_id in slide_ids:
        rel_id = slide_id.rId
        prs.part.drop_rel(rel_id)
        prs.slides._sldIdLst.remove(slide_id)  # type: ignore[attr-defined]


def _get_placeholder_by_idx(slide: Any, placeholder_idx: Optional[int]) -> Any:
    """Return placeholder object by index, or None when index is unavailable.

    python-pptx placeholders are keyed by placeholder format index. If your map does
    not yet define indices, we return None and renderer can fallback to title/body.
    """
    if placeholder_idx is None:
        return None

    try:
        return slide.placeholders[placeholder_idx]
    except Exception:
        return None


def _set_text(placeholder: Any, text: str) -> bool:
    """Set text in a placeholder safely.

    Returns:
        True when text was written, False otherwise.
    """
    if placeholder is None:
        return False
    try:
        placeholder.text = text
        return True
    except Exception:
        return False


def _normalize_text(value: Any) -> str:
    """Convert scalar/list values to placeholder text.

    Lists are rendered as plain lines so template bullet styles can apply.
    """
    def _strip_manual_bullet_prefix(text: str) -> str:
        # Remove common manual bullet prefixes; rely on PPT placeholder styling.
        return re.sub(r"^\s*(?:[-*•]\s+|\d+[\.\)]\s+)", "", text).strip()

    if isinstance(value, list):
        return "\n".join(_strip_manual_bullet_prefix(str(item)) for item in value)
    return _strip_manual_bullet_prefix(str(value))


def _clean_heading(text: str) -> str:
    """Light normalization for title-like fields: whitespace and stray edge punctuation."""
    text = " ".join(text.split()).strip()
    return text.strip(" ,;:-")


# Advisory character counts for stderr warnings only (editorial length is spec-owned).
_BLOCK_TITLE_ADVISORY_MAX_CHARS = 16


def _main_title_max_chars(slide_type: str) -> int:
    """Advisory main-title length threshold for warnings (by layout family)."""
    if slide_type in {"narrow_image_content", "wide_image_content"}:
        return 52
    if slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
        return 56
    if slide_type in {"standard_1_block", "standard_2_block", "standard_3_block"}:
        return 58
    return 120


def _warn_title_length(slide_type: str, field: str, text: str, limit: int) -> None:
    """Emit a non-fatal warning when a title-like field exceeds an advisory length."""
    if len(text) <= limit:
        return
    print(
        f"[title-length] {slide_type}.{field}: {len(text)} chars (advisory max {limit}); "
        "rendering verbatim — shorten in the deck spec if layout overflow occurs",
        file=sys.stderr,
    )


def _prepare_main_title(text: str, slide_type: str) -> str:
    """Normalize whitespace; warn if likely long for layout; never shorten semantically."""
    prepared = _clean_heading(text)
    _warn_title_length(slide_type, "title", prepared, _main_title_max_chars(slide_type))
    return prepared


def _prepare_block_title(text: str, slide_type: str, field: str) -> str:
    """Normalize whitespace; warn if likely long for layout; never shorten semantically."""
    prepared = _clean_heading(text)
    _warn_title_length(slide_type, field, prepared, _BLOCK_TITLE_ADVISORY_MAX_CHARS)
    return prepared


def _set_title(slide: Any, text: str, slide_type: str) -> bool:
    """Set slide title using mapped placeholder first, then fallback title shape."""
    if slide_type in CONTENT_MAIN_TITLE_TYPES:
        text = _prepare_main_title(text, slide_type)
    else:
        text = _clean_heading(text)
    mapping = slide._layout_mapping  # type: ignore[attr-defined]
    target_idx = mapping.get("title")
    ph = _get_placeholder_by_idx(slide, target_idx)
    if _set_text(ph, text):
        return True

    # Fallback: native title shape when available.
    if getattr(slide.shapes, "title", None) is not None:
        try:
            slide.shapes.title.text = text
            return True
        except Exception:
            return False

    return False


def _set_body_or_placeholder(slide: Any, key: str, value: Any) -> bool:
    """Set text to mapped placeholder key or fallback to a body placeholder."""
    mapping = slide._layout_mapping  # type: ignore[attr-defined]
    target_idx = mapping.get(key)
    ph = _get_placeholder_by_idx(slide, target_idx)
    text = _normalize_text(value)
    if _set_text(ph, text):
        return True

    # If a specific mapped placeholder index exists but is unavailable on the created
    # slide, do not fallback into unrelated placeholders (prevents content overwrite).
    if target_idx is not None and ph is None:
        return False

    # Fallback to first non-title placeholder with text frame.
    for candidate in slide.placeholders:
        try:
            if candidate == slide.shapes.title:
                continue
        except Exception:
            pass

        if hasattr(candidate, "text_frame"):
            try:
                candidate.text = text
                return True
            except Exception:
                continue
    return False


def _set_footer_and_slide_number(
    slide: Any,
    footer_value: Any,
    slide_number: int,
) -> None:
    """Write footer and slide number only into native materialized placeholders.

    python-pptx often does not materialize FOOTER / SLIDE_NUMBER placeholders on
    slides created from layouts. In that case we skip silently (no ad hoc shapes).
    """
    mapping = slide._layout_mapping  # type: ignore[attr-defined]
    footer_idx = mapping.get("footer")
    footer_text = _normalize_text(footer_value).strip()

    # Determine slide-number placeholder index from layout definition.
    slide_number_idx: Optional[int] = None
    for ph in slide.slide_layout.placeholders:
        try:
            if str(ph.placeholder_format.type).startswith("SLIDE_NUMBER"):
                slide_number_idx = ph.placeholder_format.idx
                break
        except Exception:
            continue

    if isinstance(footer_idx, int) and footer_text:
        footer_ph = _get_placeholder_by_idx(slide, footer_idx)
        if footer_ph is not None:
            try:
                ph_type = str(footer_ph.placeholder_format.type)
            except Exception:
                ph_type = ""
            if ph_type.startswith("FOOTER"):
                _set_text(footer_ph, footer_text)

    if isinstance(slide_number_idx, int):
        slide_number_ph = _get_placeholder_by_idx(slide, slide_number_idx)
        if slide_number_ph is not None:
            try:
                ph_type = str(slide_number_ph.placeholder_format.type)
            except Exception:
                ph_type = ""
            if ph_type.startswith("SLIDE_NUMBER"):
                _set_text(slide_number_ph, str(slide_number))


def _set_image_on_placeholder(slide: Any, key: str, image_path: Any) -> bool:
    """Insert image into mapped picture placeholder (or geometry fallback)."""
    path = Path(str(image_path)) if image_path is not None else None
    if path is None or not path.exists():
        return False

    mapping = slide._layout_mapping  # type: ignore[attr-defined]
    target_idx = mapping.get(key)
    placeholder = _get_placeholder_by_idx(slide, target_idx)
    if placeholder is None:
        return False

    try:
        placeholder.insert_picture(str(path))
        return True
    except Exception:
        pass

    # Fallback to placeholder geometry if direct insert is unavailable.
    try:
        slide.shapes.add_picture(
            str(path),
            placeholder.left,
            placeholder.top,
            placeholder.width,
            placeholder.height,
        )
        return True
    except Exception:
        return False


def _render_agenda_table(slide: Any, agenda_items: Any) -> bool:
    """Render agenda items into the mapped agenda table placeholder.

    We preserve template formatting by writing into existing table cells only.
    python-pptx does not provide a clean public API to append new table rows, so
    if there are more agenda items than table rows we put overflow text in the
    last row as a robust fallback.
    """
    items = agenda_items if isinstance(agenda_items, list) else []
    items_text = [str(item) for item in items]

    mapping = slide._layout_mapping  # type: ignore[attr-defined]
    target_idx = mapping.get("agenda_items")
    placeholder = _get_placeholder_by_idx(slide, target_idx)
    def _write_cell(cell: Any, text: str, align: Any) -> None:
        """Write text with simple neutral formatting."""
        text_frame = cell.text_frame
        text_frame.clear()
        paragraph = text_frame.paragraphs[0]
        paragraph.text = text
        paragraph.alignment = align
        text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    if placeholder is None or not getattr(placeholder, "has_table", False):
        # Robust fallback: if placeholder exists, place a programmatic table.
        if placeholder is not None:
            try:
                rows = max(1, len(items_text))
                cols = 2
                shape = slide.shapes.add_table(
                    rows,
                    cols,
                    placeholder.left,
                    placeholder.top,
                    placeholder.width,
                    placeholder.height,
                )
                table = shape.table
                # Keep numbering narrow and content wide.
                table.columns[0].width = int(placeholder.width * 0.16)
                table.columns[1].width = int(placeholder.width * 0.84)

                for row_idx in range(rows):
                    number_text = str(row_idx + 1) if row_idx < len(items_text) else ""
                    title_text = items_text[row_idx] if row_idx < len(items_text) else ""
                    _write_cell(table.cell(row_idx, 0), number_text, PP_ALIGN.CENTER)
                    _write_cell(table.cell(row_idx, 1), title_text, PP_ALIGN.LEFT)
                return True
            except Exception:
                pass

        # Final fallback: bullet-like text in mapped/fallback placeholder.
        return _set_body_or_placeholder(slide, "agenda_items", items_text)

    table = placeholder.table
    row_count = len(table.rows)
    if row_count == 0:
        return False

    column_count = len(table.columns)
    use_two_columns = column_count >= 2

    for row_idx, item_text in enumerate(items_text[:row_count]):
        if use_two_columns:
            _write_cell(table.cell(row_idx, 0), str(row_idx + 1), PP_ALIGN.CENTER)
            _write_cell(table.cell(row_idx, 1), item_text, PP_ALIGN.LEFT)
        else:
            _write_cell(table.cell(row_idx, 0), f"{row_idx + 1}. {item_text}", PP_ALIGN.LEFT)

    # If there are more items than rows, append them into last row as fallback.
    if len(items_text) > row_count:
        overflow = items_text[row_count - 1 :]
        if use_two_columns:
            _write_cell(table.cell(row_count - 1, 0), str(row_count), PP_ALIGN.CENTER)
            _write_cell(table.cell(row_count - 1, 1), "\n".join(overflow), PP_ALIGN.LEFT)
        else:
            _write_cell(
                table.cell(row_count - 1, 0),
                f"{row_count}. " + "\n".join(overflow),
                PP_ALIGN.LEFT,
            )

    # Clear remaining unused rows for clean output.
    for row_idx in range(len(items_text), row_count):
        if use_two_columns:
            _write_cell(table.cell(row_idx, 0), "", PP_ALIGN.CENTER)
            _write_cell(table.cell(row_idx, 1), "", PP_ALIGN.LEFT)
        else:
            _write_cell(table.cell(row_idx, 0), "", PP_ALIGN.LEFT)

    return True


def render_deck(
    template_path: str | Path,
    payload: Dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Render a PPTX file from deck payload and template.

    Args:
        template_path: Existing .potx or .pptx template path.
        payload: Parsed and validated deck payload.
        output_path: Destination .pptx path.

    Returns:
        Resolved output path.

    Raises:
        FileNotFoundError: If template is missing.
        ValueError: If slide type mapping is invalid.
    """
    template = Path(template_path)
    if not template.exists():
        raise FileNotFoundError(f"Template file not found: {template}")

    prs = Presentation(str(template))
    if len(prs.slides) > 0:
        _clear_existing_slides(prs)

    for slide_number, slide_data in enumerate(payload.get("slides", []), start=1):
        slide_type = slide_data.get("type")
        if slide_type not in SLIDE_TYPE_MAP:
            raise ValueError(f"Unsupported slide type in mapping: {slide_type!r}")

        config = SLIDE_TYPE_MAP[slide_type]
        layout_index = config.get("layout_index")
        placeholder_map = config.get("placeholders", {})

        if not isinstance(layout_index, int):
            raise ValueError(f"layout_index for slide type '{slide_type}' must be an integer.")

        if layout_index < 0 or layout_index >= len(prs.slide_layouts):
            raise ValueError(
                f"layout_index {layout_index} for '{slide_type}' is out of range "
                f"(template has {len(prs.slide_layouts)} layouts)."
            )

        layout = prs.slide_layouts[layout_index]
        slide = prs.slides.add_slide(layout)
        slide._layout_mapping = placeholder_map  # type: ignore[attr-defined]

        # Agenda is a special layout: title text is baked into template.
        if slide_type != "agenda":
            title = str(slide_data.get("title", ""))
            if title:
                _set_title(slide, title, slide_type)

        if slide_type == "cover":
            if "subtitle" in slide_data:
                _set_body_or_placeholder(slide, "subtitle", slide_data.get("subtitle", ""))
            if "date" in slide_data:
                _set_body_or_placeholder(slide, "date", slide_data.get("date", ""))

        elif slide_type == "agenda":
            if "agenda_items" in slide_data:
                _render_agenda_table(slide, slide_data.get("agenda_items", []))

        elif slide_type == "divider":
            if "section_title" in slide_data:
                _set_body_or_placeholder(slide, "section_title", slide_data.get("section_title", ""))

        elif slide_type == "standard_1_block":
            for key in ("section_title", "block_title", "block_body"):
                if key in slide_data:
                    if key == "block_title":
                        original = str(slide_data.get(key, ""))
                        prepared = _prepare_block_title(original, slide_type, key)
                        _set_body_or_placeholder(slide, key, prepared)
                    else:
                        _set_body_or_placeholder(slide, key, slide_data.get(key, ""))
            _set_footer_and_slide_number(slide, slide_data.get("footer", ""), slide_number)

        elif slide_type == "standard_2_block":
            for key in (
                "section_title",
                "left_block_title",
                "left_block_body",
                "right_block_title",
                "right_block_body",
            ):
                if key in slide_data:
                    if key in {"left_block_title", "right_block_title"}:
                        original = str(slide_data.get(key, ""))
                        prepared = _prepare_block_title(original, slide_type, key)
                        _set_body_or_placeholder(slide, key, prepared)
                    else:
                        _set_body_or_placeholder(slide, key, slide_data.get(key, ""))
            _set_footer_and_slide_number(slide, slide_data.get("footer", ""), slide_number)

        elif slide_type == "standard_3_block":
            for key in (
                "section_title",
                "block_1_title",
                "block_1_body",
                "block_2_title",
                "block_2_body",
                "block_3_title",
                "block_3_body",
            ):
                if key in slide_data:
                    if key in {"block_1_title", "block_2_title", "block_3_title"}:
                        original = str(slide_data.get(key, ""))
                        prepared = _prepare_block_title(original, slide_type, key)
                        _set_body_or_placeholder(slide, key, prepared)
                    else:
                        _set_body_or_placeholder(slide, key, slide_data.get(key, ""))
            _set_footer_and_slide_number(slide, slide_data.get("footer", ""), slide_number)

        elif slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
            for key in (
                "section_title",
                "dominant_block_title",
                "dominant_block_body",
                "secondary_block_title",
                "secondary_block_body",
            ):
                if key in slide_data:
                    if key in {"dominant_block_title", "secondary_block_title"}:
                        original = str(slide_data.get(key, ""))
                        prepared = _prepare_block_title(original, slide_type, key)
                        _set_body_or_placeholder(slide, key, prepared)
                    else:
                        _set_body_or_placeholder(slide, key, slide_data.get(key, ""))
            _set_footer_and_slide_number(slide, slide_data.get("footer", ""), slide_number)

        elif slide_type in {"narrow_image_content", "wide_image_content"}:
            for key in ("section_title", "content_block_title", "content_block_body"):
                if key in slide_data:
                    if key == "content_block_title":
                        original = str(slide_data.get(key, ""))
                        prepared = _prepare_block_title(original, slide_type, key)
                        _set_body_or_placeholder(slide, key, prepared)
                    else:
                        _set_body_or_placeholder(slide, key, slide_data.get(key, ""))
            if "image" in slide_data:
                _set_image_on_placeholder(slide, "image", slide_data.get("image"))
            _set_footer_and_slide_number(slide, slide_data.get("footer", ""), slide_number)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(destination))
    return destination.resolve()
