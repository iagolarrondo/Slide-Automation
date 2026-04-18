"""CLI: validate deck spec (strict), then render to PPTX in one step."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .api import load_json, render_deck, validate_deck_spec


def pick_latest_json(directory: Path) -> Path:
    """Return the newest ``*.json`` in ``directory`` (non-recursive). Tie-break by name."""
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    candidates = list(directory.glob("*.json"))
    if not candidates:
        raise ValueError(f"No .json files in {directory}")
    return max(candidates, key=lambda p: (p.stat().st_mtime, p.name))


def default_output_path(input_json: Path, cwd: Path | None = None) -> Path:
    """``output/<stem>.pptx`` under ``cwd`` (default: current working directory)."""
    root = cwd or Path.cwd()
    return (root / "output" / f"{input_json.stem}.pptx").resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a deck JSON (same checks as slide-validate), then render to PPTX "
            "if validation passes. Default output: ./output/<input-stem>.pptx"
        )
    )
    parser.add_argument("--template", required=True, help="Path to source .potx/.pptx template.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="Path to deck JSON file.")
    src.add_argument(
        "--latest-from",
        metavar="DIR",
        help="Use the most recently modified *.json in this directory (non-recursive).",
    )
    parser.add_argument(
        "--output",
        help="Output .pptx path. If omitted, writes to output/<input-basename>.pptx under cwd.",
    )
    parser.add_argument(
        "--quiet-warnings",
        action="store_true",
        help="Suppress advisory length warnings (stderr); validation errors still print.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.input:
            input_path = Path(args.input).expanduser().resolve()
        else:
            latest_dir = Path(args.latest_from).expanduser().resolve()
            try:
                input_path = pick_latest_json(latest_dir).resolve()
            except ValueError as exc:
                print(f"Error: {exc}", file=sys.stderr)
                return 1
            print(f"Using deck spec: {input_path}", file=sys.stderr)

        try:
            payload = load_json(input_path)
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

        if args.output:
            output_path = Path(args.output).expanduser().resolve()
        else:
            output_path = default_output_path(input_path)

        template_path = Path(args.template).expanduser().resolve()

        try:
            written = render_deck(
                template_path=template_path,
                payload=payload,
                output_path=output_path,
            )
        except FileNotFoundError as exc:
            print(f"File error: {exc}", file=sys.stderr)
            return 1
        except ValueError as exc:
            print(f"Render error: {exc}", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"I/O error: {exc}", file=sys.stderr)
            return 1

        print(written)
        return 0

    except KeyboardInterrupt:  # pragma: no cover
        print("Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
