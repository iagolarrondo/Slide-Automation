"""Validation rules for WD deck specs."""

from __future__ import annotations

import unittest

from slide_automation.utils import validate_deck_spec


class TestValidateWd(unittest.TestCase):
    def test_wd_agenda_wrong_item_count(self) -> None:
        payload = {
            "deck_title": "T",
            "template_id": "wd",
            "slides": [
                {
                    "type": "wd_agenda_3",
                    "title": "Agenda",
                    "agenda_items": ["only", "two"],
                }
            ],
        }
        errors, _ = validate_deck_spec(payload)
        self.assertTrue(any("exactly 3" in e for e in errors))

    def test_json_template_id_without_cli(self) -> None:
        payload = {
            "deck_title": "T",
            "template_id": "wd",
            "slides": [{"type": "wd_cover", "title": "Hello"}],
        }
        errors, _ = validate_deck_spec(payload)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
