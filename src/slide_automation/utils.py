"""Utility helpers for JSON loading and lightweight deck validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

SUPPORTED_SLIDE_TYPES = {
    "cover",
    "agenda",
    "divider",
    "standard_1_block",
    "standard_2_block",
    "standard_3_block",
    "standard_2_block_big_left",
    "standard_2_block_big_right",
    "narrow_image_content",
    "wide_image_content",
}


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


def validate_deck_payload(payload: Dict[str, Any]) -> List[str]:
    """Perform lightweight validation for v1 deck payload shape.

    This is intentionally simpler than full JSON schema validation. It checks core
    fields required by renderer behavior and gives readable error messages.

    Args:
        payload: Parsed deck JSON object.

    Returns:
        A list of human-readable validation errors. Empty means valid.
    """
    errors: List[str] = []

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

        if slide_type not in SUPPORTED_SLIDE_TYPES:
            errors.append(
                f"{prefix}.type must be one of {sorted(SUPPORTED_SLIDE_TYPES)}; got: {slide_type!r}."
            )

        if slide_type != "agenda" and (not isinstance(title, str) or not title.strip()):
            errors.append(f"{prefix}.title must be a non-empty string.")

        # Type-specific checks
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
}
_HEADING_ADVISORY_MAX_NONSPACE = 86


def _main_title_advisory_max(slide_type: str) -> int:
    return _HEADING_ADVISORY_MAX_NONSPACE


def _norm_ws(text: str) -> str:
    return " ".join(text.split()).strip()


def _nonspace_len(text: str) -> int:
    return len("".join(text.split()))


def _block_title_advisory_max(slide_type: str, field: str) -> int:
    if slide_type == "standard_3_block":
        return 18
    if slide_type == "standard_2_block" and field in {"left_block_title", "right_block_title"}:
        return 20
    if slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
        return 22
    if slide_type in {"narrow_image_content", "wide_image_content"}:
        return 22
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
        # Backward compatible:
        # - Preferred: section_number (int)
        # - Legacy: section_title (often "Section 2") used by renderer to infer number.
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
    elif slide_type == "standard_2_block":
        block_keys = ["left_block_title", "right_block_title"]
    elif slide_type == "standard_3_block":
        block_keys = ["block_1_title", "block_2_title", "block_3_title"]
    elif slide_type in {"standard_2_block_big_left", "standard_2_block_big_right"}:
        block_keys = ["dominant_block_title", "secondary_block_title"]
    elif slide_type in {"narrow_image_content", "wide_image_content"}:
        block_keys = ["content_block_title"]

    for key in block_keys:
        val = slide.get(key)
        if isinstance(val, str) and val.strip():
            warn_field(key, val, _block_title_advisory_max(slide_type, key))

    return warnings


def validate_deck_spec(payload: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate a deck spec for strict local CLIs and optional hosts: structural errors + advisory length warnings.

    Returns:
        (errors, warnings). When errors is empty, the spec is acceptable to pass to ``render_deck``
        (subject to template mapping). Warnings do not block rendering.
    """
    errors = validate_deck_payload(payload)
    warnings: List[str] = []

    slides = payload.get("slides")
    if not isinstance(slides, list):
        return errors, warnings

    for i, slide in enumerate(slides):
        prefix = f"slides[{i}]"
        if not isinstance(slide, dict):
            continue
        slide_type = slide.get("type")
        if slide_type not in SUPPORTED_SLIDE_TYPES:
            continue
        sdict = cast(Dict[str, Any], slide)
        st = cast(str, slide_type)
        errors.extend(_required_field_errors(sdict, prefix, st))
        warnings.extend(_length_warnings_for_slide(sdict, prefix, st))

    return errors, warnings
