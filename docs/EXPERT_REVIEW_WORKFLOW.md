# Expert review workflow

The target-validation step is now executable rather than informal.

## 1. Generate one blank review file per expert

```bash
python scripts/validation/prepare_expert_review.py \
  --reviewer-id expert_a \
  --review-date 2026-09-29 \
  --out reviews/case25/expert_a.json
```

Repeat for expert B.

The generated file intentionally contains `REVIEW_REQUIRED` rather than pre-filled pass/accept values.

## 2. Reviewer completes the JSON independently

Allowed criterion values:
- `pass`
- `fail`

Allowed overall decisions:
- `accept`
- `accept_after_edit`
- `reject`

## 3. Validate the two review files

```bash
python scripts/validation/validate_expert_reviews.py \
  --candidate-manifest configs/case25_target_candidate_v2_manifest.json \
  --reviews reviews/case25/expert_a.json reviews/case25/expert_b.json
```

This checks:
- reviewer independence
- case/tooth/version match
- exact mesh hash
- criterion completeness
- decision consistency

## 4. One-command promotion attempt

```bash
python scripts/validation/finalize_case25_target.py \
  --mesh path/to/fdi25_visible_preparation_candidate_v2_REQUIRES_EXPERT_REVIEW.stl \
  --review-a reviews/case25/expert_a.json \
  --review-b reviews/case25/expert_b.json
```

If every gate passes, the validated target and manifest are created under:

`assets/validated_targets/case25/`

If any gate fails, no validated target is created.

## GitHub issue option

The repository also includes an issue form at:

`.github/ISSUE_TEMPLATE/case25_target_review.yml`

This can be used as a human-readable review record, but the JSON review files remain the machine-readable promotion source of truth.
