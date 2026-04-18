"""Compatibility launcher: ``python src/main.py`` (same as ``slide-render`` after install)."""

from slide_automation.main import main

if __name__ == "__main__":
    raise SystemExit(main())
