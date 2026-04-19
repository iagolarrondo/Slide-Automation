"""Tests for donor slide mapping configuration."""

from __future__ import annotations

import unittest

from slide_automation.template_map import SLIDE_TYPE_MAP


class TestDonorSlideMap(unittest.TestCase):
    def test_all_slide_types_have_donor_slide_number(self) -> None:
        for slide_type, config in SLIDE_TYPE_MAP.items():
            self.assertIn("donor_slide_number", config, msg=slide_type)
            self.assertIsInstance(config["donor_slide_number"], int, msg=slide_type)
            self.assertGreater(config["donor_slide_number"], 0, msg=slide_type)
            self.assertIn("placeholders", config, msg=slide_type)

    def test_legacy_layout_index_is_removed(self) -> None:
        for slide_type, config in SLIDE_TYPE_MAP.items():
            self.assertNotIn("layout_index", config, msg=slide_type)


if __name__ == "__main__":
    unittest.main()
