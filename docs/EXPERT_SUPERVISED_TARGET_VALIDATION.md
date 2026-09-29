# Target validation route for expert-supervised clinical cases

All source clinical preparations in this study were completed under expert supervision.

Therefore, target promotion no longer asks a new panel to re-judge the clinical preparation itself. The mandatory remaining step is **technical geometry QA of the extracted reference mesh**.

## What technical QA verifies

- correct tooth identity
- complete prepared surface
- complete axial surfaces
- complete occlusal surface
- no adjacent-tooth contamination
- no unacceptable gingival contamination
- correct scale
- correct orientation
- suitability as reference geometry

## Case 25

The Case-25 v2 candidate remains hash-locked:

`400972eb83df4f34510863cd023e04d453ad843eda96b4a4169da9f7d71a91e2`

Complete:

`review_templates/case25_technical_geometry_qa.json`

Then promote with:

```bash
python scripts/validation/promote_expert_supervised_target.py \
  --candidate-manifest configs/case25_target_candidate_v2_manifest.json \
  --mesh path/to/fdi25_visible_preparation_candidate_v2_REQUIRES_EXPERT_REVIEW.stl \
  --qa review_templates/case25_technical_geometry_qa.json \
  --output-dir assets/validated_targets/case25
```

If any criterion fails, no validated target is created.

## Optional stronger audit

The existing two-independent-reviewer workflow remains available and may be used for manuscript strengthening or a subset reliability study. It is no longer a mandatory prerequisite for accuracy-mode RL when expert supervision of the original clinical case is documented.

## Accuracy-mode gate

Accuracy-mode RL now requires:

1. expert-supervised source case;
2. passing technical geometry QA of the exact extracted mesh;
3. hash-locked validated target manifest;
4. passing Isaac forced-contact safety gate.
