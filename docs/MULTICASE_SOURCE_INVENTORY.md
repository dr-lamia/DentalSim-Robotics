# Multi-case preparation source inventory

The project now includes a de-identified inventory of expert-supervised
preparation sources available for expansion beyond Case 25.

Current inventory:
- Case-25 exocad candidate
- 2 full-coverage preparation STL sources
- 2 additional partial-coverage preparation STL sources
- 3 three-quarter-crown preparation STL sources:
  - maxillary molar
  - maxillary premolar
  - anterior

Google Drive file IDs/URLs are intentionally excluded from the public repo.

## Local intake

For each downloaded STL:

```bash
python scripts/validation/inventory_preparation_stl.py \
  --stl path/to/source.stl \
  --source-id prep_source_XX \
  --expert-supervised \
  --out results/source_intake/prep_source_XX.json
```

The intake report records:
- SHA-256
- vertices/faces
- connected components
- watertight status
- bounds/extents
- surface area

It deliberately does not infer clinical validity or target eligibility.

## Recommended study use

Use full-coverage preparations for the first autonomous crown-preparation
benchmark. Keep partial-coverage preparations as a later task family rather
than mixing them into the first PPO/BC comparison.

This preserves a coherent primary task while retaining the broader dataset for
future generalization experiments.
