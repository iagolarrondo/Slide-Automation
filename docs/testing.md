# Smoke and regression tests

Recommended smoke path: run one Sloan and one WD render from the repo root.

```bash
# After ``pip install -e .``: ``slide-validate --input ...`` / ``slide-render ...``
python src/validate_deck_spec.py --input "examples/example_deck.json"

python src/main.py \
  --input "examples/example_deck.json" \
  --output "output/example_deck.pptx"
```

Preferred one-step path (default **Sloan** donor under the repo root):

```bash
bin/deck --input examples/example_deck.json
```

Equivalent installed CLI:

```bash
slide-build --input "examples/example_deck.json"
```

Explicit donor path (same mapping as **Sloan**):

```bash
slide-build --template "templates/Sloan_Donor_Deck.pptx" --input "examples/example_deck.json"
```

WD profile (JSON may set ``"template_id": "wd"`` instead):

```bash
slide-build --input examples/example_deck_wd.json
# or explicitly:
slide-build --template-id wd --input examples/example_deck_wd.json
```

WD full-catalog smoke (recommended before release):

```bash
slide-build --template-id wd --input examples/example_deck_wd_full_catalog.json \
  --output output/example_deck_wd_full_catalog.pptx
```

## Example JSON

| File | Role |
|------|------|
| [`examples/example_deck.json`](../examples/example_deck.json) | Reference deck spec (realistic multi-slide storyline). Use for smoke renders after template or mapping changes. |
| [`examples/example_deck_wd.json`](../examples/example_deck_wd.json) | WD example deck with representative `wd_*` types. |
| [`examples/example_deck_wd_full_catalog.json`](../examples/example_deck_wd_full_catalog.json) | WD full-catalog smoke deck (all supported WD slide variants). |

Add your own JSON under `examples/` or elsewhere; keep image paths valid on disk when using image layouts.

## Automated tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

**Test modules:** `test_validate_deck_spec`, `test_validate_wd`, `test_build_cli` (pick-latest + `slide-build`), `test_donor_mapping`, `test_pptx_integrity` (OLE/tags + rId integrity on donor output), `test_agenda_slide` (table + logos + centering), `test_divider_and_footer_behavior`, `test_title_fitting_regression`, `test_wd_rendering_fidelity`.
