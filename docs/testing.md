# Smoke and regression tests

Use a mapped Sloan working copy, e.g. `templates/Sloan_Template.pptx`, then render from the repo root:

```bash
# After ``pip install -e .``: ``slide-validate --input ...`` / ``slide-render ...``
python src/validate_deck_spec.py --input "examples/<file>.json"

python src/main.py \
  --template "templates/Sloan_Template.pptx" \
  --input "examples/<file>.json" \
  --output "output/<file>.pptx"
```

## Example JSON decks (smoke / regression)

| File | What to validate |
|------|------------------|
| `example_deck_v1.json` | Fast end-to-end smoke: cover, agenda, divider, standard 1/2/3 blocks, footers, short titles—confirms core paths without heavy content. |
| `example_deck_full_v1.json` | **Primary layout sweep:** at least one slide per supported `type` (including big blocks and image layouts)—placeholder mapping and layout indices. |
| `example_deck_big_blocks_v1.json` | `standard_2_block_big_left` and `standard_2_block_big_right` only—dominant vs secondary block mapping. |
| `example_deck_image_content_v1.json` | `narrow_image_content` and `wide_image_content`—image placeholder + content title/body. Image paths in JSON must exist on disk. |
| `slide_automation_rollout_recommendation_spec.json` | Long titles and block labels—exercises **verbatim** title rendering plus stderr **`[title-length]`** advisory warnings when copy exceeds layout guidance. |
| `internal_slide_automation_deck_spec.json` | Alternate realistic storyline with a **subset** of layouts—second opinion on mapping and copy length without repeating the full matrix. |
| `footer_visual_regression_v1.json` | Footer strings of different lengths on standard layouts—**native** footer placeholders only; if the template does not materialize footer shapes on the slide, nothing will appear (expected per renderer rules). |

## Automated tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Currently includes **title verbatim + advisory warning** checks (`tests/test_title_fitting_regression.py`).
