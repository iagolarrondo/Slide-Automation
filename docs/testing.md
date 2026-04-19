# Smoke and regression tests

Recommended smoke path: use the donor deck `templates/Sloan_Donor_Deck.pptx` from the repo root.

```bash
# After ``pip install -e .``: ``slide-validate --input ...`` / ``slide-render ...``
python src/validate_deck_spec.py --input "examples/example_deck.json"

python src/main.py \
  --template "templates/Sloan_Donor_Deck.pptx" \
  --input "examples/example_deck.json" \
  --output "output/example_deck.pptx"
```

Preferred one-step path:

```bash
bin/deck --template templates/Sloan_Donor_Deck.pptx --input examples/example_deck.json
```

Equivalent installed CLI:

```bash
slide-build --template "templates/Sloan_Donor_Deck.pptx" --input "examples/example_deck.json"
```

## Example JSON

| File | Role |
|------|------|
| [`examples/example_deck.json`](../examples/example_deck.json) | Reference deck spec (realistic multi-slide storyline). Use for smoke renders after template or mapping changes. |

Add your own JSON under `examples/` or elsewhere; keep image paths valid on disk when using image layouts.

## Automated tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

**Test modules:** `test_validate_deck_spec`, `test_build_cli` (pick-latest + `slide-build`), `test_donor_mapping`, `test_pptx_integrity` (OLE/tags + rId integrity on donor output), `test_agenda_slide` (table + logos + centering), `test_divider_and_footer_behavior`, `test_title_fitting_regression`.
