"""CLI: render deck JSON to PPTX."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .api import load_json, render_deck, validate_deck_payload
from .template_registry.registry import get_template_profile, resolve_cli_donor_path
from .utils import effective_template_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a PowerPoint deck from structured JSON and a .pptx template."
    )
    parser.add_argument(
        "--template-id",
        default=None,
        metavar="ID",
        help=(
            "Built-in template profile. When omitted, uses JSON ``template_id`` / ``template`` "
            "if set, else ``sloan``. Use --template to override donor path only."
        ),
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to source .potx/.pptx donor deck. If omitted, uses the repo default for the resolved template.",
    )
    parser.add_argument("--input", required=True, help="Path to input deck JSON file.")
    parser.add_argument("--output", required=True, help="Path to output .pptx file.")
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress the success line (exit code still 0 on success).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = load_json(args.input)
        template_id = effective_template_id(payload, args.template_id)
        try:
            profile = get_template_profile(template_id)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        if not profile.is_implemented:
            print(
                f"Error: template {template_id!r} is not implemented in this repo build.",
                file=sys.stderr,
            )
            return 1

        errors = validate_deck_payload(payload, template_id=args.template_id)
        if errors:
            print("Validation errors found:")
            for err in errors:
                print(f"  - {err}")
            return 2

        template_path = resolve_cli_donor_path(
            template_id=template_id,
            template_override=args.template,
        )
        output = render_deck(
            template_path=template_path,
            payload=payload,
            output_path=Path(args.output),
            slide_type_map=profile.slide_type_map,
            agenda_render_mode=profile.agenda_render_mode,
        )
        if not args.quiet:
            print(f"Deck generated: {output}")
        return 0

    except FileNotFoundError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Validation/render error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
