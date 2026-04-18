"""Compatibility launcher: ``python src/validate_deck_spec.py`` (same as ``slide-validate``)."""

from slide_automation.validate_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
