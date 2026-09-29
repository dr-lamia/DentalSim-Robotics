# Target promotion gate

A preparation mesh is not considered ground truth merely because it can be segmented or visualized.

## Required evidence
Promotion to `validated_target` requires:
- two independent calibrated prosthodontist reviews;
- both reviewing the exact same STL checksum;
- both decisions = `accept`;
- all seven structural criteria = true.

The validator rejects:
- one-reviewer promotion;
- duplicate reviewer IDs;
- `accept_after_edit` without re-review;
- rejected criteria;
- checksum mismatch.

## Workflow

1. Compute the candidate checksum.
2. Give the same candidate STL to two reviewers.
3. Each reviewer completes a JSON review based on `reviews/case25/review_template.json`.
4. Run:

```bash
python scripts/validate_target_approval.py \
  --candidate path/to/fdi25_visible_preparation_candidate_v2_REQUIRES_EXPERT_REVIEW.stl \
  --review reviewer_1.json \
  --review reviewer_2.json \
  --output-dir validated/case25
```

Only a passing run writes:
- `fdi25_validated_target.stl`
- `validated_target_manifest.json`

Until then, geometric accuracy rewards and manuscript accuracy outcomes remain disabled.
