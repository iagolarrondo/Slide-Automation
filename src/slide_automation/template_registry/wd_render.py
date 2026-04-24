"""WD-specific slide content application (isolated from Sloan paths)."""

from __future__ import annotations

from typing import Any, Dict, Tuple


def _combine_block(title: str, body: Any) -> str:
    t = (title or "").strip()
    if isinstance(body, list):
        b = "\n".join(str(x) for x in body)
    else:
        b = str(body or "")
    b = b.strip()
    if t and b:
        # WD donor boxes are 2-paragraph title/body regions.
        return f"{t}\n{b}"
    return t or b


def _set_text_preserving_runs(shape: Any, text: str) -> bool:
    """Write text without recreating paragraphs/runs (preserve donor formatting)."""
    if shape is None or not hasattr(shape, "text_frame"):
        return False
    try:
        tf = shape.text_frame
        if not tf.paragraphs:
            return False
        lines = str(text).split("\n")
        paragraphs = tf.paragraphs
        for i, p in enumerate(paragraphs):
            line = lines[i] if i < len(lines) else ""
            runs = p.runs
            if runs:
                runs[0].text = line
                for r in runs[1:]:
                    r.text = ""
            else:
                p.text = line
        return True
    except Exception:
        return False


def _set_paragraph_text_preserving_runs(shape: Any, paragraph_idx: int, text: str) -> bool:
    """Replace one paragraph text in-place while preserving run formatting."""
    if shape is None or not hasattr(shape, "text_frame"):
        return False
    try:
        paragraphs = shape.text_frame.paragraphs
        if paragraph_idx < 0 or paragraph_idx >= len(paragraphs):
            return False
        p = paragraphs[paragraph_idx]
        runs = p.runs
        if runs:
            runs[0].text = str(text)
            for r in runs[1:]:
                r.text = ""
        else:
            p.text = str(text)
        return True
    except Exception:
        return False


def _set_mosaic_tile_title_body(shape: Any, title: Any, body: Any, normalize_text) -> bool:
    """Set mosaic tile title/body in donor-defined paragraphs (p0 title, p2 body)."""
    if shape is None or not hasattr(shape, "text_frame"):
        return False
    ok_title = _set_paragraph_text_preserving_runs(shape, 0, str(title or ""))
    # Donor tiles keep a blank spacer paragraph (p1) and body/bullet paragraph (p2).
    ok_body = _set_paragraph_text_preserving_runs(shape, 2, normalize_text(body))
    return ok_title or ok_body


def _resolve_wd_shape_from_donor_index(
    slide: Any,
    donor_slide: Any,
    donor_idx: int,
    render_module: Any,
) -> Any:
    """Map donor ``shape_index`` to cloned slide index after OLE filtering."""
    if donor_idx < 0:
        return None
    skipped_before = 0
    for i, donor_shape in enumerate(donor_slide.shapes):
        if i >= donor_idx:
            break
        try:
            if donor_shape.shape_type in render_module._OLE_SHAPE_TYPES:
                skipped_before += 1
                continue
        except Exception:
            pass
        try:
            if render_module._should_skip_donor_shape_for_clone(donor_shape):
                skipped_before += 1
        except Exception:
            pass
    mapped_idx = donor_idx - skipped_before
    if 0 <= mapped_idx < len(slide.shapes):
        return slide.shapes[mapped_idx]
    return None


def _set_mapped_text(slide: Any, donor_slide: Any, target: Any, text: str, render_module: Any) -> bool:
    """Set mapped text for WD targets using placeholder idx or donor shape idx."""
    if isinstance(target, int):
        try:
            shape = slide.placeholders[target]
        except Exception:
            shape = None
        return _set_text_preserving_runs(shape, text)
    if isinstance(target, dict):
        if isinstance(target.get("placeholder_idx"), int):
            try:
                shape = slide.placeholders[int(target["placeholder_idx"])]
            except Exception:
                shape = None
            return _set_text_preserving_runs(shape, text)
        if isinstance(target.get("shape_index"), int):
            base_shape = _resolve_wd_shape_from_donor_index(
                slide, donor_slide, int(target["shape_index"]), render_module
            )
            shape = base_shape
            if isinstance(target.get("group_child_index"), int):
                child_idx = int(target["group_child_index"])
                if (
                    base_shape is not None
                    and getattr(base_shape, "shape_type", None) == render_module.MSO_SHAPE_TYPE.GROUP
                    and 0 <= child_idx < len(base_shape.shapes)
                ):
                    shape = base_shape.shapes[child_idx]
                else:
                    return False
            return _set_text_preserving_runs(shape, text)
    return False


def apply_wd_slide(
    prs: Any,
    slide: Any,
    slide_type: str,
    slide_data: Dict[str, Any],
    _slide_number: int,
    config: Dict[str, Any],
    *,
    wd_divider_ordinal: int | None = None,
) -> None:
    """Fill a cloned WD donor slide from ``slide_data`` (mapping already on ``slide``)."""
    # Late import: ``renderer`` imports this module only inside the render loop.
    from slide_automation import renderer as R

    donor_idx = int(config.get("donor_slide_number", 0))
    donor_slide = prs.slides[donor_idx - 1] if donor_idx > 0 else None
    mapping = getattr(slide, "_field_mapping", {})
    editable_keys = set(config.get("wd_editable_keys") or ())

    def _set_key(key: str, text: Any) -> None:
        if key not in editable_keys:
            return
        if donor_slide is None:
            return
        target = mapping.get(key)
        _set_mapped_text(slide, donor_slide, target, R._normalize_text(text), R)

    def _set_donor_shape_idx(donor_shape_idx: int, text: Any) -> None:
        if donor_slide is None:
            return
        shape = _resolve_wd_shape_from_donor_index(slide, donor_slide, int(donor_shape_idx), R)
        _set_text_preserving_runs(shape, R._normalize_text(text))

    if slide_type == "wd_cover":
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "presenter" in slide_data:
            _set_key("presenter", slide_data.get("presenter", ""))
        if "subtitle" in slide_data:
            _set_key("subtitle", slide_data.get("subtitle", ""))
        if "date" in slide_data:
            _set_key("date", slide_data.get("date", ""))
        return

    if slide_type in {"wd_agenda_3", "wd_agenda_4", "wd_agenda_5", "wd_agenda_6"}:
        if "agenda_heading" in slide_data or slide_data.get("title"):
            _set_key("agenda_heading", slide_data.get("agenda_heading") or slide_data.get("title", ""))
        indices = config.get("wd_agenda_item_indices") or ()
        items = slide_data.get("agenda_items", [])
        if not isinstance(items, list):
            items = []
        for i, shape_idx in enumerate(indices):
            text = str(items[i]) if i < len(items) else ""
            _set_donor_shape_idx(int(shape_idx), text)
        return

    if slide_type == "wd_divider":
        line = str(slide_data.get("title") or slide_data.get("section_title") or "").strip()
        target = mapping.get("divider_text")
        shape = None
        if donor_slide is not None and isinstance(target, dict) and isinstance(target.get("shape_index"), int):
            shape = _resolve_wd_shape_from_donor_index(slide, donor_slide, int(target["shape_index"]), R)
        explicit = slide_data.get("section_number", None)
        n_val: int | None = None
        if explicit is not None:
            try:
                n_val = int(str(explicit).strip())
            except Exception:
                n_val = None
        if n_val is None and isinstance(wd_divider_ordinal, int):
            n_val = wd_divider_ordinal
        numeral = f"{max(0, int(n_val or 1)):02d}"
        # Divider donor keeps numeral and section title in separate paragraphs
        # within the same text box: p0 numeral, p1 title.
        ok_num = _set_paragraph_text_preserving_runs(shape, 0, numeral)
        ok_title = _set_paragraph_text_preserving_runs(shape, 1, line)
        if not (ok_num and ok_title):
            _set_key("divider_text", f"{numeral}\n{line}")
        return

    if slide_type == "wd_section_intro":
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        # Slide 7 donor has two semantic boxes: gradient title + dark body.
        # Populate title/body regions separately when provided.
        if "box_1_title" in slide_data:
            _set_key("box_1_title", slide_data.get("box_1_title", ""))
        if "box_1_body" in slide_data:
            _set_key("box_1_body", slide_data.get("box_1_body", ""))
        if "box_2_title" in slide_data:
            _set_key("box_2_title", slide_data.get("box_2_title", ""))
        if "box_2_body" in slide_data:
            _set_key("box_2_body", slide_data.get("box_2_body", ""))
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    if slide_type in {"wd_two_column", "wd_two_column_alt"}:
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        left = _combine_block(
            str(slide_data.get("left_block_title", "")),
            slide_data.get("left_block_body", ""),
        )
        right = _combine_block(
            str(slide_data.get("right_block_title", "")),
            slide_data.get("right_block_body", ""),
        )
        _set_key("left_block", left)
        _set_key("right_block", right)
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    if slide_type == "wd_one_block_grouped":
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        if "block_title" in slide_data:
            _set_key("block_title", slide_data.get("block_title", ""))
        if "block_body" in slide_data:
            _set_key("block_body", slide_data.get("block_body", ""))
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    if slide_type == "wd_one_block_placeholder":
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        target = mapping.get("block")
        wrote_block = False
        if donor_slide is not None and isinstance(target, int):
            try:
                shape = slide.placeholders[target]
            except Exception:
                shape = None
            if shape is not None:
                t = str(slide_data.get("block_title", ""))
                b = R._normalize_text(slide_data.get("block_body", ""))
                ok_t = _set_paragraph_text_preserving_runs(shape, 0, t)
                ok_b = _set_paragraph_text_preserving_runs(shape, 1, b)
                wrote_block = bool(ok_t or ok_b)
        if not wrote_block:
            block = _combine_block(
                str(slide_data.get("block_title", "")),
                slide_data.get("block_body", ""),
            )
            _set_key("block", block)
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    if slide_type == "wd_three_column":
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        for i, key in enumerate(("col_1", "col_2", "col_3"), start=1):
            c = _combine_block(
                str(slide_data.get(f"block_{i}_title", "")),
                slide_data.get(f"block_{i}_body", ""),
            )
            _set_key(key, c)
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    if slide_type == "wd_four_column":
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        for i, key in enumerate(("col_1", "col_2", "col_3", "col_4"), start=1):
            c = _combine_block(
                str(slide_data.get(f"block_{i}_title", "")),
                slide_data.get(f"block_{i}_body", ""),
            )
            _set_key(key, c)
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    if slide_type in {
        "wd_mosaic_4",
        "wd_mosaic_6",
        "wd_mosaic_8",
        "wd_tile_4",
        "wd_tile_5",
        "wd_tile_6",
    }:
        title = str(slide_data.get("title", ""))
        if title:
            _set_key("title", title)
        if "section_title" in slide_data:
            _set_key("section_title", slide_data.get("section_title", ""))
        indices: Tuple[int, ...] = tuple(config.get("wd_content_shape_indices") or ())
        tiles = slide_data.get("tiles", [])
        if not isinstance(tiles, list):
            tiles = []
        for i, shape_idx in enumerate(indices):
            cell: Dict[str, Any] = tiles[i] if i < len(tiles) and isinstance(tiles[i], dict) else {}
            target_shape = None
            if donor_slide is not None:
                target_shape = _resolve_wd_shape_from_donor_index(slide, donor_slide, int(shape_idx), R)
            if target_shape is not None:
                _set_mosaic_tile_title_body(
                    target_shape,
                    cell.get("title", ""),
                    cell.get("body", ""),
                    R._normalize_text,
                )
        if "footer" in slide_data:
            _set_key("footer", slide_data.get("footer", ""))
        return

    raise ValueError(f"Unhandled WD slide type: {slide_type!r}")
