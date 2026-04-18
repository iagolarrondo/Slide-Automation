"""CLI: validate deck JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .api import load_json, validate_deck_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate deck spec JSON (slide types, required fields, advisory title lengths)."
    )
    parser.add_argument("--input", required=True, help="Path to deck JSON file.")
    parser.add_argument(
        "--quiet-warnings",
        action="store_true",
        help="Suppress advisory length warnings (errors still print).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = load_json(args.input)
    except FileNotFoundError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    errors, warnings = validate_deck_spec(payload)

    if not args.quiet_warnings:
        for w in warnings:
            print(f"Warning: {w}", file=sys.stderr)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 2

    if warnings and not args.quiet_warnings:
        print(f"Deck spec is valid ({len(warnings)} length warning(s) on stderr).")
    else:
        print("Deck spec is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
