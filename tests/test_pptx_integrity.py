"""Package-level integrity checks for rendered PPTX output.

Goal: catch structural corruption that triggers PowerPoint repair prompts.
"""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from slide_automation.renderer import render_deck


_R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _collect_rids_from_xml(xml_bytes: bytes) -> set[str]:
    root = ET.fromstring(xml_bytes)
    rids: set[str] = set()
    for el in root.iter():
        rid = el.attrib.get(f"{{{_R_NS}}}id")
        if rid:
            rids.add(rid)
    return rids


def _rel_ids_from_rels(rels_bytes: bytes) -> set[str]:
    root = ET.fromstring(rels_bytes)
    return {
        rel.attrib["Id"]
        for rel in root.findall(f"{{{_REL_NS}}}Relationship")
        if "Id" in rel.attrib
    }


class TestRenderedPptxIntegrity(unittest.TestCase):
    def test_rendered_slides_have_no_ole_or_tags_rels_and_no_ole_xml(self) -> None:
        """Donor cloning must not embed OLE add-ins or slide tags parts in output."""
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "cover", "title": "Hello", "subtitle": "Sub", "date": "2026"},
            ],
        }

        repo_root = Path(__file__).resolve().parents[1]
        donor = repo_root / "templates" / "Sloan_Donor_Deck.pptx"

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.pptx"
            render_deck(donor, payload, out)

            with zipfile.ZipFile(out, "r") as z:
                for name in z.namelist():
                    if not name.startswith("ppt/slides/_rels/slide") or not name.endswith(
                        ".xml.rels"
                    ):
                        continue
                    root = ET.fromstring(z.read(name))
                    for rel in root.findall(f"{{{_REL_NS}}}Relationship"):
                        rtype = rel.attrib.get("Type", "")
                        self.assertNotIn(
                            "oleObject",
                            rtype,
                            msg=f"unexpected OLE rel in {name}: {rtype}",
                        )
                        self.assertNotIn(
                            "/relationships/tags",
                            rtype,
                            msg=f"unexpected tags rel in {name}: {rtype}",
                        )
                for name in z.namelist():
                    if not name.startswith("ppt/slides/slide") or "_rels" in name:
                        continue
                    if not name.endswith(".xml"):
                        continue
                    body = z.read(name)
                    self.assertNotIn(b"p:oleObj", body)
                    self.assertNotIn(b"<p:oleObj", body)

    def test_minimal_cover_deck_has_no_unresolved_rids(self) -> None:
        # Cover slide donor may contain think-cell OLE on the file; output must omit it.
        payload = {
            "deck_title": "T",
            "slides": [
                {"type": "cover", "title": "Hello", "subtitle": "Sub", "date": "2026"},
            ],
        }

        repo_root = Path(__file__).resolve().parents[1]
        donor = repo_root / "templates" / "Sloan_Donor_Deck.pptx"

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.pptx"
            render_deck(donor, payload, out)

            with zipfile.ZipFile(out, "r") as z:
                names = set(z.namelist())
                slide_parts = sorted(
                    n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")
                )
                self.assertGreaterEqual(len(slide_parts), 1)

                for slide_part in slide_parts:
                    rels_part = (
                        slide_part.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
                    )
                    xml_rids = _collect_rids_from_xml(z.read(slide_part))
                    if not xml_rids:
                        continue
                    self.assertIn(rels_part, names, msg=f"missing rels for {slide_part}")
                    rel_ids = _rel_ids_from_rels(z.read(rels_part))
                    missing = sorted(xml_rids - rel_ids)
                    self.assertEqual(
                        missing,
                        [],
                        msg=f"{slide_part} references rIds not in rels: {missing}",
                    )


if __name__ == "__main__":
    unittest.main()

