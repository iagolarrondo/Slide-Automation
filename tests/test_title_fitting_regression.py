"""Regression tests for title-like field handling (verbatim + advisory warnings)."""

from __future__ import annotations

import io
import contextlib
import unittest

from slide_automation.renderer import (
    _prepare_block_title,
    _prepare_main_title,
)


class TestTitleVerbatimPolicy(unittest.TestCase):
    """Renderer must not semantically shorten main or block titles."""

    def test_main_title_passes_through_unshortened(self) -> None:
        long_title = (
            "The current solution combines a structured deck spec with a template-aware renderer"
        )
        out = _prepare_main_title(long_title, "standard_2_block")
        self.assertEqual(
            out,
            "The current solution combines a structured deck spec with a template-aware renderer",
        )
        self.assertGreater(len(out), 58)

    def test_block_title_passes_through_unshortened(self) -> None:
        label = "Why this architecture matters"
        out = _prepare_block_title(label, "standard_2_block", "right_block_title")
        self.assertEqual(out, label)
        self.assertGreater(len(out), 16)

    def test_whitespace_normalization_only(self) -> None:
        messy = "  Too   many    spaces\t\n  "
        out = _prepare_main_title(messy, "standard_1_block")
        self.assertEqual(out, "Too many spaces")

    def test_stderr_warning_when_main_title_over_advisory(self) -> None:
        long_title = "x" * 80
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            _prepare_main_title(long_title, "standard_2_block")
        err = buf.getvalue()
        self.assertIn("[title-length]", err)
        self.assertIn("title", err)


if __name__ == "__main__":
    unittest.main()
