# Standardized target inspection renderer

Use the same seven views for every extracted target candidate:

- +Z
- -Z
- +X
- -X
- +Y
- -Y
- perspective

The renderer intentionally avoids assigning buccal, lingual/palatal, mesial or distal labels unless those anatomical directions are explicitly encoded elsewhere.

Run:

```bash
python scripts/validation/render_target_inspection_views.py \
  --mesh path/to/candidate.stl \
  --out-dir reviews/case25_views
```

Outputs:
- seven PNG views
- one contact sheet
- `inspection_summary.json`

This is a review aid only; it does not auto-approve the candidate.
