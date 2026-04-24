"""Behavior tests for divider numbering and footer clearing/replacement."""

from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from slide_automation.renderer import render_deck


def _all_text_in_slide_xml(xml_bytes: bytes) -> str:
    # Extract all <a:t> runs concatenated, rough but stable for assertions.
    root = ET.fromstring(xml_bytes)
    texts = []
    for el in root.iter():
        if el.tag.endswith("}t") and el.text:
            texts.append(el.text)
    return "\n".join(texts)


class TestDividerAndFooterBehavior(unittest.TestCase):
    def _render_bytes(self, payload: dict) -> bytes:
        repo_root = Path(__file__).resolve().parents[1]
        donor = repo_root / "templates" / "Sloan_Donor_Deck.pptx"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.pptx"
            render_deck(donor, payload, out)
            return out.read_bytes()

    def test_divider_section_number_is_zero_padded(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "divider", "title": "My Section", "section_number": 2},
            ],
        }
        pptx_bytes = self._render_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(pptx_bytes), "r") as z:
            slide_xml = z.read("ppt/slides/slide11.xml")
            text = _all_text_in_slide_xml(slide_xml)
            self.assertIn("My Section", text)
            self.assertIn("02", text)
            self.assertNotIn("Section 2", text)

    def test_divider_section_number_legacy_parsed_from_section_title(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "divider", "title": "My Section", "section_title": "Section 3"},
            ],
        }
        pptx_bytes = self._render_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(pptx_bytes), "r") as z:
            slide_xml = z.read("ppt/slides/slide11.xml")
            text = _all_text_in_slide_xml(slide_xml)
            self.assertIn("03", text)
            self.assertNotIn("Section 3", text)

    def test_sloan_divider_behavior_unchanged(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "divider", "title": "Alpha", "section_number": 9},
                {"type": "divider", "title": "Beta", "section_title": "Section 4"},
            ],
        }
        pptx_bytes = self._render_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(pptx_bytes), "r") as z:
            s1 = _all_text_in_slide_xml(z.read("ppt/slides/slide11.xml"))
            s2 = _all_text_in_slide_xml(z.read("ppt/slides/slide12.xml"))
            self.assertIn("09", s1)
            self.assertIn("Alpha", s1)
            self.assertIn("04", s2)
            self.assertIn("Beta", s2)

    def test_footer_cleared_when_absent(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {
                    "type": "standard_1_block",
                    "title": "Heading",
                    "section_title": "S",
                    "block_title": "B",
                    "block_body": ["x"],
                    # no footer
                }
            ],
        }
        pptx_bytes = self._render_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(pptx_bytes), "r") as z:
            slide_xml = z.read("ppt/slides/slide11.xml")
            text = _all_text_in_slide_xml(slide_xml)
            # Donor placeholder text must not remain.
            self.assertNotIn("Footer", text)

    def test_footer_replaced_when_present(self) -> None:
        payload = {
            "deck_title": "T",
            "slides": [
                {
                    "type": "standard_1_block",
                    "title": "Heading",
                    "section_title": "S",
                    "block_title": "B",
                    "block_body": ["x"],
                    "footer": "CONFIDENTIAL",
                }
            ],
        }
        pptx_bytes = self._render_bytes(payload)
        with zipfile.ZipFile(io.BytesIO(pptx_bytes), "r") as z:
            slide_xml = z.read("ppt/slides/slide11.xml")
            text = _all_text_in_slide_xml(slide_xml)
            self.assertIn("CONFIDENTIAL", text)


if __name__ == "__main__":
    unittest.main()

