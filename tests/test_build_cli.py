"""Tests for slide-build (validate + render CLI helpers)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

from slide_automation.build_cli import default_output_path, main, pick_latest_json


class TestPickLatestJson(unittest.TestCase):
    def test_picks_newest_by_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            older = d / "older.json"
            newer = d / "newer.json"
            older.write_text("{}")
            time.sleep(0.05)
            newer.write_text("{}")
            chosen = pick_latest_json(d)
            self.assertEqual(chosen.resolve(), newer.resolve())

    def test_empty_dir_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                pick_latest_json(Path(tmp))

    def test_not_a_dir_raises(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            p = f.name
        try:
            with self.assertRaises(ValueError):
                pick_latest_json(Path(p))
        finally:
            os.unlink(p)


class TestDefaultOutputPath(unittest.TestCase):
    def test_stem_under_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            inp = cwd / "specs" / "my_deck.json"
            out = default_output_path(inp, cwd=cwd)
            self.assertEqual(out, (cwd / "output" / "my_deck.pptx").resolve())


class TestBuildCliMain(unittest.TestCase):
    def test_validation_failure_returns_2(self) -> None:
        bad = {"deck_title": "T", "slides": [{"type": "nope", "title": "x"}]}
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            deck = tmp_path / "bad.json"
            deck.write_text(json.dumps(bad))
            old_argv = sys.argv
            try:
                sys.argv = [
                    "slide-build",
                    "--template",
                    str(tmp_path / "fake.pptx"),
                    "--input",
                    str(deck),
                ]
                code = main()
            finally:
                sys.argv = old_argv
            self.assertEqual(code, 2)

    def test_latest_from_prints_and_validates(self) -> None:
        bad = {"deck_title": "T", "slides": [{"type": "nope", "title": "x"}]}
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            deck = tmp_path / "only.json"
            deck.write_text(json.dumps(bad))
            old_argv = sys.argv
            try:
                sys.argv = [
                    "slide-build",
                    "--template",
                    str(tmp_path / "fake.pptx"),
                    "--latest-from",
                    str(tmp_path),
                ]
                err = StringIO()
                with mock.patch("sys.stderr", err):
                    code = main()
            finally:
                sys.argv = old_argv
            self.assertEqual(code, 2)
            self.assertIn("Using deck spec:", err.getvalue())
            self.assertIn(str(deck.resolve()), err.getvalue())


if __name__ == "__main__":
    unittest.main()
