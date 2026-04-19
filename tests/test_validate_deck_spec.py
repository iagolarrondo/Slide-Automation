"""Tests for validate_deck_spec (errors + warnings)."""

from __future__ import annotations

import unittest

from slide_automation.utils import validate_deck_spec


class TestValidateDeckSpec(unittest.TestCase):
    def test_valid_minimal_shape(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "cover", "title": "Cover"},
                {
                    "type": "agenda",
                    "agenda_items": ["A", "B"],
                },
                {"type": "divider", "title": "D", "section_title": "S1"},
                {
                    "type": "standard_1_block",
                    "title": "T",
                    "section_title": "S",
                    "block_title": "B",
                    "block_body": ["x"],
                },
            ],
        }
        errors, warnings = validate_deck_spec(payload)
        self.assertEqual(errors, [])

    def test_unknown_slide_type(self) -> None:
        payload = {"deck_title": "T", "slides": [{"type": "not_a_type", "title": "x"}]}
        errors, _ = validate_deck_spec(payload)
        self.assertTrue(any("type must be one of" in e for e in errors))

    def test_divider_allows_section_number_without_section_title(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "divider", "title": "D", "section_number": 2},
            ],
        }
        errors, _ = validate_deck_spec(payload)
        self.assertEqual(errors, [])

    def test_missing_required_standard_1(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {
                    "type": "standard_1_block",
                    "title": "T",
                    "section_title": "S",
                    "block_title": "B",
                }
            ],
        }
        errors, _ = validate_deck_spec(payload)
        self.assertTrue(any("block_body" in e for e in errors))

    def test_length_warning_long_main_title(self) -> None:
        long_t = "x" * 90
        payload = {
            "deck_title": "T",
            "slides": [
                {
                    "type": "standard_2_block",
                    "title": long_t,
                    "section_title": "S",
                    "left_block_title": "L",
                    "left_block_body": ["a"],
                    "right_block_title": "R",
                    "right_block_body": ["b"],
                }
            ],
        }
        errors, warnings = validate_deck_spec(payload)
        self.assertEqual(errors, [])
        self.assertTrue(any("slides[0].title" in w and "advisory max 86" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
