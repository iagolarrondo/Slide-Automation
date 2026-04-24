# WD donor deck inventory (`WD_Template_Donor.pptx`)

This document describes the **packaged** WD donor deck: slide order, layouts, and how JSON `type` values map. The authoritative mapping in code is [`src/slide_automation/template_registry/wd.py`](../src/slide_automation/template_registry/wd.py).

## Coexistence with Sloan

- **Sloan** specs use Sloan `type` strings (`cover`, `agenda`, `standard_2_block`, …) and default donor `templates/Sloan_Donor_Deck.pptx`.
- **WD** specs use `wd_*` `type` strings and donor `templates/WD_Template_Donor.pptx`.
- Declare the deck family with top-level `"template_id": "wd"` (or pass `--template-id wd`). When both are present, **CLI `--template-id` wins** over JSON (see `effective_template_id` in `slide_automation.utils`).
- Do not mix Sloan and WD slide `type` values in one deck.

## Global notes

- Many slides include a **think-cell** OLE shape (shape index `0`). The shared renderer skips OLE on clone; do not rely on think-cell in output.
- **Slide number** placeholders exist on most content slides; the shared footer helper updates materialized `SLIDE_NUMBER` placeholders when present.
- **Footer** on WD content slides is usually a **plain text box** named like `TextBox 12` / `TextBox 3`, mapped by `shape_index` in `wd.py` (not a native FOOTER placeholder).

## Slide-by-slide

| Donor # | Layout name | JSON `type` | Role / constraints |
|--------:|---------------|-------------|---------------------|
| 1 | `Presentation Title and Subtitle White` | `wd_cover` | Title `ph 0`, presenter `ph 11`, subtitle `ph 14`, date `ph 15`. Optional JSON `presenter`. |
| 2 | `Blank White` | `wd_agenda_3` | Prebuilt 3-row agenda. **Exactly 3** `agenda_items`. Heading: shape `6` (`title` or `agenda_heading`). Rows: shapes `(7, 12, 11)` top→bottom. |
| 3 | `Blank White` | `wd_agenda_4` | **4** items. Heading shape `7`. Rows `(8, 4, 15, 14)`. |
| 4 | `Blank White` | `wd_agenda_5` | **5** items. Heading shape `7`. Rows `(8, 20, 4, 15, 14)`. |
| 5 | `Blank White` | `wd_agenda_6` | **6** items. Heading shape `7`. Rows `(8, 20, 4, 15, 23, 14)`. |
| 6 | `Blank White` | `wd_divider` | Single line text box `Title 2` at shape `2`. Renderer writes `section_number` + `title` (`01 Title`) when both set. |
| 7 | `Title, Subtitle and Content Full White` | `wd_section_intro` | Title `ph 0`, section strip `ph 12`, footer text box shape `4`. Decorative groups are left as-is. |
| 8 | `Title, Subtitle and Content Full White` | `wd_two_column` | Same field names as Sloan `standard_2_block`: left/right title+body merged with `\n\n` into content shapes `1` and `5`, footer shape `6`. |
| 9–11, 13, 15 | same layout | *(unused in v1 map)* | Alternate **section intro** donors; v1 maps all intros to donor **7** only. |
| 10 | `Title, Subtitle and Content Full White` | `wd_three_column` | Uses Sloan-like `block_1_*` … `block_3_*` keys; columns map to shapes `1`, `5`, `6`; footer `7`. |
| 12 | `Title, Subtitle and Content Full White` | `wd_four_column` | `block_1_*` … `block_4_*` → shapes `1`, `5`, `7`, `8`; footer `6`. |
| 14, 16 | `Title, Subtitle and Content Full White` | `wd_two_column_alt` | Second column shape index differs from slide **8** (donor **16** in map). |
| 17 | `Title, Subtitle and Content Full White` | `wd_mosaic_4` | `tiles`: **4** objects `{title, body}` → shapes `(4,5,7,6)` spatial order. |
| 18 | `Title, Subtitle and Content Full White` | `wd_mosaic_6` | **6** tiles → `(4,5,6,8,9,7)`. |
| 19 | `Title, Subtitle and Content Full White` | `wd_mosaic_8` | **8** tiles → `(4,12,16,8,5,13,17,9)`. |
| 20 | `Title, Subtitle and Content Full White` | `wd_tile_4` | **4** tiles → `(4,5,6,7)`. |
| 21 | `Title, Subtitle and Content Full White` | `wd_tile_5` | **5** tiles → `(4,5,6,7,8)`. |
| 22 | `Title, Subtitle and Content Full White` | `wd_tile_6` | **6** tiles → `(4,5,6,7,10,8)`. |
| 23 | `Title, Subtitle and Content Full White` | `wd_one_block_grouped` | One-block grouped donor. Group shape `5`: title child `1`, body child `0`; title `ph 0`, section `ph 12`, footer shape `4`. |
| 24 | `Title, Subtitle and Content Full White` | `wd_one_block_placeholder` | One-block placeholder donor. Content placeholder `ph 11` (`block`), title `ph 0`, section `ph 12`, footer shape `5`. |

## JSON shapes

- **Columns / two-column**: reuse Sloan field names (`left_block_title`, `left_block_body`, …) where possible.
- **Mosaic / tile**: use `"tiles": [ {"title": "...", "body": "..." }, ... ]` with length exactly matching the slide type.

## Ambiguities / follow-ups

1. **Unused donors 9, 11, 13, 15** — visually similar section intros; confirm with design whether separate `type` values are needed.
2. **2-column donors 14 vs 16** — only **16** is mapped as `wd_two_column_alt`; confirm if slide **14** should be a distinct variant.
3. **Agenda 1–2 sections** — no donor slides in this file; extend the deck or map to closest variant if product requires it.
4. **Image / chart-heavy layouts** — not represented in v1 mapping; add new `wd_*` types when those donors exist.
