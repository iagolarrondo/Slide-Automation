"""CLI: render deck JSON to PPTX."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .api import load_json, render_deck, validate_deck_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a PowerPoint deck from structured JSON and a .pptx template."
    )
    parser.add_argument("--template", required=True, help="Path to source .potx/.pptx template file.")
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
        errors = validate_deck_payload(payload)
        if errors:
            print("Validation errors found:")
            for err in errors:
                print(f"  - {err}")
            return 2

        output = render_deck(
            template_path=Path(args.template),
            payload=payload,
            output_path=Path(args.output),
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
