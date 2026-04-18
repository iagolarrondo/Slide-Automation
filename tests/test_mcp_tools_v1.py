"""Smoke tests for MCP v1 tool handlers (dict payloads)."""

from __future__ import annotations

import unittest

from slide_automation.mcp.tools_v1 import tool_validate_deck_spec


class TestMcpValidateTool(unittest.TestCase):
    def test_missing_path(self) -> None:
        r = tool_validate_deck_spec({})
        self.assertFalse(r["ok"])
        self.assertEqual(r["error_code"], "file_not_found")

    def test_unknown_slide_type(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        bad = {"deck_title": "T", "slides": [{"type": "nope", "title": "x"}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(bad, f)
            p = f.name
        try:
            r = tool_validate_deck_spec({"deck_spec_path": p})
            self.assertFalse(r["ok"])
            self.assertEqual(r["error_code"], "validation_failed")
            self.assertTrue(r["errors"])
        finally:
            Path(p).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
