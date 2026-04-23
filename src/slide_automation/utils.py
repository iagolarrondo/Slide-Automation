"""Utility helpers for JSON loading and lightweight deck validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

from .template_registry.sloan import SLIDE_TYPE_MAP as _SLOAN_SLIDE_TYPE_MAP
from .template_registry.wd import WD_CONTENT_INDICES, WD_SLIDE_TYPE_MAP

# Sloan slide types (default JSON contract).
SUPPORTED_SLIDE_TYPES = set(_SLOAN_SLIDE_TYPE_MAP)
SUPPORTED_WD_SLIDE_TYPES = frozenset(WD_SLIDE_TYPE_MAP.keys())


def supported_slide_types(template_id: str) -> frozenset[str]:
    """Slide ``type`` strings allowed for a built-in ``template_id``."""
    tid = (template_id or "sloan").strip().lower()
    if tid == "wd":
        return frozenset(WD_SLIDE_TYPE_MAP.keys())
    return frozenset(_SLOAN_SLIDE_TYPE_MAP.keys())


def effective_template_id(payload: Dict[str, Any], cli_template_id: str | None = None) -> str:
    """Resolve template family: explicit CLI ``--template-id``, then JSON, else ``sloan``.

    When ``cli_template_id`` is omitted or empty, ``payload['template_id']`` /
    ``payload['template']`` is used when present so deck JSON can declare ``wd``.
    """
    if cli_template_id is not None and str(cli_template_id).strip():
        return str(cli_template_id).strip().lower()
    tid = payload.get("template_id") or payload.get("template")
    if isinstance(tid, str) and tid.strip():
        return tid.strip().lower()
    return "sloan"


def load_json(path: str | Path) -> Dict[str, Any]:
    """Load and parse a JSON file into a dictionary.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If JSON is invalid or top-level is not an object.
    """
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {json_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Top-level JSON value must be an object.")

    return data


def validate_deck_payload(payload: Dict[str, Any], *, template_id: str | None = None) -> List[str]:
    """Perform lightweight validation for deck payload shape.

    Args:
        payload: Parsed deck JSON object.
        template_id: Optional built-in template (``sloan`` / ``wd``). When omitted, uses
            ``effective_template_id(payload)``.

    Returns:
        A list of human-readable validation errors. Empty means valid.
    """
    errors: List[str] = []
    tid = effective_template_id(payload, cli_template_id=template_id)
    allowed = supported_slide_types(tid)

    deck_title = payload.get("deck_title")
    if not isinstance(deck_title, str) or not deck_title.strip():
        errors.append("'deck_title' must be a non-empty string.")

    slides = payload.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("'slides' must be a non-empty array.")
        return errors

    for i, slide in enumerate(slides):
        prefix = f"slides[{i}]"
        if not isinstance(slide, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        slide_type = slide.get("type")
        title = slide.get("title")

        if slide_type not in allowed:
            errors.append(
                f"{prefix}.type must be one of {sorted(allowed)}; got: {slide_type!r}."
            )

        title_exempt = slide_type in {
            "agenda",
            "wd_agenda_3",
            "wd_agenda_4",
            "wd_agenda_5",
            "wd_agenda_6",
        }
        if slide_type == "wd_divider" and slide.get("section_number") is not None:
            title_exempt = True

        if not title_exempt and (not isinstance(title, str) or not title.strip()):
            errors.append(f"{prefix}.title must be a non-empty string.")

        # --- Sloan type-specific checks ---
        if slide_type == "agenda":
            agenda_items = slide.get("agenda_items", [])
            if not isinstance(agenda_items, list) or not all(isinstance(x, str) for x in agenda_items):
                errors.append(f"{prefix}.agenda_items must be an array of strings for agenda slides.")

        if slide_type == "divider":
            if "section_title" in slide and not isinstance(slide.get("section_title"), str):
                errors.append(f"{prefix}.section_title must be a string when provided.")
            if "section_number" in slide and not isinstance(slide.get("section_number"), (int, str)):
                errors.append(f"{prefix}.section_number must be an int or numeric string when provided.")

        if slide_type == "standard_1_block":
            if "block_title" in slide and not isinstance(slide.get("block_title"), str):
                errors.append(f"{prefix}.block_title must be a string when provided.")
            if "block_body" in slide and not isinstance(slide.get("block_body"), (str, list)):
                errors.append(f"{prefix}.block_body must be a string or array of strings when provided.")

        if slide_type == "standard_2_block":
            for key in ("left_block_title", "right_block_title"):
                if key in slide and not isinstance(slide.get(key), str):
                    errors.append(f"{prefix}.{key} must be a string when provided.")
            for key in ("left_block_body", "right_block_body"):
                if key in slide and not isinstance(slide.get(key), (str, list)):
                    errors.append(f"{prefix}.{key} must be a string or array of strings when provided.")

        if slide_type == "standard_3_block":
            for key in ("block_1_title", "block_2_title", "block_3_title"):
                if key in slide and not isinstance(slide.get(key), str):
                    errors.append(f"{prefix}.{key} must be a string when provided.")
            for key in ("block_1_body", "block_2_body", "block_3_body"):
                if key in slide and not isinstance(slide.get(key), (str, list)):
                    errors.append(f"{prefix}.{key} must be a string or array of strings when provided.")

        if slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
            for key in ("dominant_block_title", "secondary_block_title"):
                if key in slide and not isinstance(slide.get(key), str):
                    errors.append(f"{prefix}.{key} must be a string when provided.")
            for key in ("dominant_block_body", "secondary_block_body"):
                if key in slide and not isinstance(slide.get(key), (str, list)):
                    errors.append(f"{prefix}.{key} must be a string or array of strings when provided.")

        if slide_type in {"narrow_image_content", "wide_image_content"}:
            if "content_block_title" in slide and not isinstance(slide.get("content_block_title"), str):
                errors.append(f"{prefix}.content_block_title must be a string when provided.")
            if "content_block_body" in slide and not isinstance(slide.get("content_block_body"), (str, list)):
                errors.append(f"{prefix}.content_block_body must be a string or array of strings when provided.")
            if "image" in slide and not isinstance(slide.get("image"), str):
                errors.append(f"{prefix}.image must be a string path when provided.")

        # --- WD type-specific checks ---
        if slide_type == "wd_cover":
            if "presenter" in slide and not isinstance(slide.get("presenter"), str):
                errors.append(f"{prefix}.presenter must be a string when provided.")
            if "subtitle" in slide and not isinstance(slide.get("subtitle"), str):
                errors.append(f"{prefix}.subtitle must be a string when provided.")
            if "date" in slide and not isinstance(slide.get("date"), str):
                errors.append(f"{prefix}.date must be a string when provided.")
        if slide_type == "wd_section_intro":
            for key in ("box_1_title", "box_1_body", "box_2_title", "box_2_body"):
                if key in slide and not isinstance(slide.get(key), str):
                    errors.append(f"{prefix}.{key} must be a string when provided.")

        if slide_type in {"wd_agenda_3", "wd_agenda_4", "wd_agenda_5", "wd_agenda_6"}:
            n = int(str(slide_type).rsplit("_", 1)[-1])
            items = slide.get("agenda_items", [])
            if not isinstance(items, list) or not all(isinstance(x, str) for x in items):
                errors.append(f"{prefix}.agenda_items must be an array of strings.")
            elif len(items) != n:
                errors.append(
                    f"{prefix}.agenda_items must contain exactly {n} strings for {slide_type!r} "
                    f"(got {len(items)})."
                )
            elif not all(x.strip() for x in items):
                errors.append(f"{prefix}.agenda_items entries must be non-empty strings.")
            if "agenda_heading" in slide and not isinstance(slide.get("agenda_heading"), str):
                errors.append(f"{prefix}.agenda_heading must be a string when provided.")

        if slide_type == "wd_divider":
            if "section_title" in slide and not isinstance(slide.get("section_title"), str):
                errors.append(f"{prefix}.section_title must be a string when provided.")
            if "section_number" in slide and not isinstance(slide.get("section_number"), (int, str)):
                errors.append(f"{prefix}.section_number must be an int or numeric string when provided.")

        if slide_type in {"wd_two_column", "wd_two_column_alt"}:
            for key in ("left_block_title", "right_block_title"):
                if key in slide and not isinstance(slide.get(key), str):
                    errors.append(f"{prefix}.{key} must be a string when provided.")
            for key in ("left_block_body", "right_block_body"):
                if key in slide and not isinstance(slide.get(key), (str, list)):
                    errors.append(f"{prefix}.{key} must be a string or array of strings when provided.")

        if slide_type == "wd_three_column":
            for key in ("block_1_title", "block_2_title", "block_3_title"):
                if key in slide and not isinstance(slide.get(key), str):
                    errors.append(f"{prefix}.{key} must be a string when provided.")
            for key in ("block_1_body", "block_2_body", "block_3_body"):
                if key in slide and not isinstance(slide.get(key), (str, list)):
                    errors.append(f"{prefix}.{key} must be a string or array of strings when provided.")

        if slide_type == "wd_four_column":
            for k in range(1, 5):
                kt = f"block_{k}_title"
                kb = f"block_{k}_body"
                if kt in slide and not isinstance(slide.get(kt), str):
                    errors.append(f"{prefix}.{kt} must be a string when provided.")
                if kb in slide and not isinstance(slide.get(kb), (str, list)):
                    errors.append(f"{prefix}.{kb} must be a string or array of strings when provided.")

        if slide_type in WD_CONTENT_INDICES:
            tiles = slide.get("tiles", [])
            exp = len(WD_CONTENT_INDICES[str(slide_type)])
            if not isinstance(tiles, list):
                errors.append(f"{prefix}.tiles must be an array for {slide_type!r}.")
            elif len(tiles) != exp:
                errors.append(f"{prefix}.tiles must contain exactly {exp} objects for {slide_type!r}.")
            else:
                for j, cell in enumerate(tiles):
                    if not isinstance(cell, dict):
                        errors.append(f"{prefix}.tiles[{j}] must be an object.")
                        continue
                    if "title" in cell and not isinstance(cell.get("title"), str):
                        errors.append(f"{prefix}.tiles[{j}].title must be a string when provided.")
                    if "body" in cell and not isinstance(cell.get("body"), (str, list)):
                        errors.append(f"{prefix}.tiles[{j}].body must be a string or list when provided.")

    return errors


# Advisory limits aligned with renderer stderr hints (editorial; not enforced at render).
_CONTENT_MAIN_TITLE_TYPES = {
    "standard_1_block",
    "standard_2_block",
    "standard_3_block",
    "standard_2_block_big_left",
    "standard_2_block_big_right",
    "narrow_image_content",
    "wide_image_content",
    "wd_cover",
    "wd_section_intro",
    "wd_two_column",
    "wd_two_column_alt",
    "wd_three_column",
    "wd_four_column",
    "wd_mosaic_4",
    "wd_mosaic_6",
    "wd_mosaic_8",
    "wd_tile_4",
    "wd_tile_5",
    "wd_tile_6",
}
_HEADING_ADVISORY_MAX_NONSPACE = 86


def _main_title_advisory_max(slide_type: str) -> int:
    return _HEADING_ADVISORY_MAX_NONSPACE


def _norm_ws(text: str) -> str:
    return " ".join(text.split()).strip()


def _nonspace_len(text: str) -> int:
    return len("".join(text.split()))


def _block_title_advisory_max(slide_type: str, field: str) -> int:
    if slide_type == "standard_3_block" or slide_type == "wd_three_column":
        return 18
    if slide_type in {"standard_2_block", "wd_two_column", "wd_two_column_alt"} and field in {
        "left_block_title",
        "right_block_title",
    }:
        return 20
    if slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
        return 22
    if slide_type in {"narrow_image_content", "wide_image_content"}:
        return 22
    if slide_type == "wd_four_column" and field.startswith("block_") and field.endswith("_title"):
        return 18
    return 24


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_body(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(x, str) and x.strip() for x in value)
    return False


def _required_field_errors(slide: Dict[str, Any], prefix: str, slide_type: str) -> List[str]:
    """Errors for missing required keys by slide type (stricter than render-time presence)."""
    err: List[str] = []

    def req_str(key: str) -> None:
        if key not in slide:
            err.append(f"{prefix}: missing required field {key!r} for type {slide_type!r}.")
        elif not _non_empty_str(slide.get(key)):
            err.append(f"{prefix}.{key} must be a non-empty string.")

    def req_body(key: str) -> None:
        if key not in slide:
            err.append(f"{prefix}: missing required field {key!r} for type {slide_type!r}.")
        elif not _non_empty_body(slide.get(key)):
            err.append(f"{prefix}.{key} must be a non-empty string or non-empty array of strings.")

    if str(slide_type).startswith("wd_"):
        return _required_field_errors_wd(slide, prefix, slide_type, err, req_str, req_body)

    if slide_type == "agenda":
        if "agenda_items" not in slide or not isinstance(slide.get("agenda_items"), list):
            err.append(f"{prefix}.agenda_items is required and must be an array for agenda slides.")
        elif not slide["agenda_items"]:
            err.append(f"{prefix}.agenda_items must be a non-empty array.")
        elif not all(isinstance(x, str) and x.strip() for x in slide["agenda_items"]):
            err.append(f"{prefix}.agenda_items must be a non-empty array of non-empty strings.")
        return err

    if slide_type == "cover":
        return err

    if slide_type == "divider":
        if "section_number" not in slide:
            req_str("section_title")
        return err

    if slide_type == "standard_1_block":
        req_str("section_title")
        req_str("block_title")
        req_body("block_body")
        return err

    if slide_type == "standard_2_block":
        req_str("section_title")
        req_str("left_block_title")
        req_body("left_block_body")
        req_str("right_block_title")
        req_body("right_block_body")
        return err

    if slide_type == "standard_3_block":
        req_str("section_title")
        for k in ("block_1_title", "block_1_body", "block_2_title", "block_2_body", "block_3_title", "block_3_body"):
            if k.endswith("_body"):
                req_body(k)
            else:
                req_str(k)
        return err

    if slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
        req_str("section_title")
        req_str("dominant_block_title")
        req_body("dominant_block_body")
        req_str("secondary_block_title")
        req_body("secondary_block_body")
        return err

    if slide_type in {"narrow_image_content", "wide_image_content"}:
        req_str("section_title")
        if "image" not in slide or not isinstance(slide.get("image"), str) or not str(slide["image"]).strip():
            err.append(f"{prefix}.image must be a non-empty string path.")
        req_str("content_block_title")
        req_body("content_block_body")
        return err

    return err


def _required_field_errors_wd(
    slide: Dict[str, Any],
    prefix: str,
    slide_type: str,
    err: List[str],
    req_str,
    req_body,
) -> List[str]:
    if slide_type == "wd_cover":
        return err

    if slide_type in {"wd_agenda_3", "wd_agenda_4", "wd_agenda_5", "wd_agenda_6"}:
        n = int(slide_type.rsplit("_", 1)[-1])
        if "agenda_items" not in slide or not isinstance(slide.get("agenda_items"), list):
            err.append(f"{prefix}.agenda_items is required for {slide_type!r}.")
        elif len(slide["agenda_items"]) != n:
            err.append(f"{prefix}.agenda_items must have exactly {n} entries for {slide_type!r}.")
        elif not all(isinstance(x, str) and x.strip() for x in slide["agenda_items"]):
            err.append(f"{prefix}.agenda_items must be non-empty strings.")
        return err

    if slide_type == "wd_divider":
        if not _non_empty_str(slide.get("title")) and slide.get("section_number") is None:
            err.append(f"{prefix}: wd_divider requires non-empty title and/or section_number.")
        return err

    if slide_type == "wd_section_intro":
        req_str("title")
        req_str("section_title")
        return err

    if slide_type in {"wd_two_column", "wd_two_column_alt"}:
        req_str("section_title")
        req_str("left_block_title")
        req_body("left_block_body")
        req_str("right_block_title")
        req_body("right_block_body")
        return err

    if slide_type == "wd_three_column":
        req_str("section_title")
        for k in ("block_1_title", "block_1_body", "block_2_title", "block_2_body", "block_3_title", "block_3_body"):
            if k.endswith("_body"):
                req_body(k)
            else:
                req_str(k)
        return err

    if slide_type == "wd_four_column":
        req_str("section_title")
        for k in range(1, 5):
            req_str(f"block_{k}_title")
            req_body(f"block_{k}_body")
        return err

    if slide_type in WD_CONTENT_INDICES:
        req_str("section_title")
        exp = len(WD_CONTENT_INDICES[slide_type])
        if "tiles" not in slide or not isinstance(slide.get("tiles"), list):
            err.append(f"{prefix}.tiles is required for {slide_type!r}.")
        elif len(slide["tiles"]) != exp:
            err.append(f"{prefix}.tiles must have length {exp} for {slide_type!r}.")
        else:
            for j, cell in enumerate(slide["tiles"]):
                if not isinstance(cell, dict):
                    err.append(f"{prefix}.tiles[{j}] must be an object.")
                    continue
                if not (_non_empty_str(cell.get("title")) or _non_empty_body(cell.get("body"))):
                    err.append(
                        f"{prefix}.tiles[{j}] needs a non-empty title and/or body for {slide_type!r}."
                    )
        return err

    return err


def _length_warnings_for_slide(slide: Dict[str, Any], prefix: str, slide_type: str) -> List[str]:
    warnings: List[str] = []

    def warn_field(field: str, text: str, limit: int) -> None:
        n = _nonspace_len(_norm_ws(text))
        if n > limit:
            warnings.append(
                f"{prefix}.{field}: {n} non-space chars (advisory max {limit}); "
                "may overflow in PowerPoint — shorten in the spec if needed."
            )

    title = slide.get("title")
    if slide_type in _CONTENT_MAIN_TITLE_TYPES and isinstance(title, str) and title.strip():
        warn_field("title", title, _main_title_advisory_max(slide_type))

    block_keys: List[str] = []
    if slide_type == "standard_1_block":
        block_keys = ["block_title"]
    elif slide_type in {"standard_2_block", "wd_two_column", "wd_two_column_alt"}:
        block_keys = ["left_block_title", "right_block_title"]
    elif slide_type in {"standard_3_block", "wd_three_column"}:
        block_keys = ["block_1_title", "block_2_title", "block_3_title"]
    elif slide_type == "wd_four_column":
        block_keys = ["block_1_title", "block_2_title", "block_3_title", "block_4_title"]
    elif slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
        block_keys = ["dominant_block_title", "secondary_block_title"]
    elif slide_type in {"narrow_image_content", "wide_image_content"}:
        block_keys = ["content_block_title"]

    for key in block_keys:
        val = slide.get(key)
        if isinstance(val, str) and val.strip():
            warn_field(key, val, _block_title_advisory_max(slide_type, key))

    return warnings


def validate_deck_spec(
    payload: Dict[str, Any],
    *,
    template_id: str | None = None,
) -> Tuple[List[str], List[str]]:
    """Validate a deck spec: structural errors + advisory length warnings.

    Args:
        payload: Deck JSON object.
        template_id: Optional ``sloan`` / ``wd`` override; otherwise inferred from
            ``payload['template_id']`` / ``payload['template']`` (see ``effective_template_id``).

    Returns:
        (errors, warnings). When errors is empty, the spec is acceptable to pass to ``render_deck``
        for the matching template. Warnings do not block rendering.
    """
    errors = validate_deck_payload(payload, template_id=template_id)
    warnings: List[str] = []

    slides = payload.get("slides")
    if not isinstance(slides, list):
        return errors, warnings

    tid = effective_template_id(payload, cli_template_id=template_id)
    allowed = supported_slide_types(tid)

    for i, slide in enumerate(slides):
        prefix = f"slides[{i}]"
        if not isinstance(slide, dict):
            continue
        slide_type = slide.get("type")
        if slide_type not in allowed:
            continue
        sdict = cast(Dict[str, Any], slide)
        st = cast(str, slide_type)
        errors.extend(_required_field_errors(sdict, prefix, st))
        warnings.extend(_length_warnings_for_slide(sdict, prefix, st))

    return errors, warnings
