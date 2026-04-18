"""Inspect template layouts and placeholders for mapping setup.

Usage:
    python src/inspect_template.py --template templates/sloan_template.potx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pptx import Presentation


def parse_args() -> argparse.Namespace:
    """Parse CLI args for template inspection."""
    parser = argparse.ArgumentParser(
        description="Print template slide layouts and placeholders for mapping."
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to .potx/.pptx template file.",
    )
    return parser.parse_args()


def main() -> int:
    """Inspect template and print all layouts and placeholders."""
    args = parse_args()
    template_path = Path(args.template)

    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    try:
        prs = Presentation(str(template_path))
    except Exception as exc:
        print(f"Failed to open template: {exc}", file=sys.stderr)
        return 1

    print(f"Template: {template_path}")
    print(f"Total layouts: {len(prs.slide_layouts)}")
    print("=" * 72)

    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout [{i}]: {layout.name!r}")
        if not layout.placeholders:
            print("  (no placeholders)")
            print("-" * 72)
            continue

        for ph in layout.placeholders:
            # placeholder_format.idx is the index needed for python-pptx lookups.
            ph_idx = ph.placeholder_format.idx
            ph_type = ph.placeholder_format.type
            ph_name = getattr(ph, "name", "")
            print(f"  - idx={ph_idx:<3} type={str(ph_type):<20} name={ph_name!r}")

        print("-" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
