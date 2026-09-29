# Case 25 visual confirmation completion

Objective technical QA is already complete for the locked Case-25 v2 candidate.

The final target-validation step is now a seven-item visual confirmation.

## Create a blank confirmation record

```bash
python scripts/validation/prepare_case25_visual_qa.py \
  --operator-id REVIEWER_PSEUDONYM \
  --review-date YYYY-MM-DD \
  --out reviews/case25_visual_qa.json
```

Scale and orientation remain pre-verified as `pass`.
The seven visual items remain `REVIEW_REQUIRED`.

## Confirm the seven visual items

For each, change `REVIEW_REQUIRED` to either `pass` or `fail`:

- correct tooth identity
- complete prepared surface
- complete axial surfaces
- complete occlusal surface
- no adjacent-tooth contamination
- no unacceptable gingival contamination
- suitable as reference geometry

Then set:

```json
"overall_decision": "accept"
```

only if all seven are acceptable.

## Finalize

```bash
python scripts/validation/finalize_case25_visual_qa.py \
  --mesh path/to/fdi25_visible_preparation_candidate_v2_REQUIRES_EXPERT_REVIEW.stl \
  --qa reviews/case25_visual_qa.json
```

If a real Isaac forced-contact result is already available, add:

```bash
--forced-contact-result results/isaac_runs/<run>/forced_contact_result.json
```

The command will:

1. reject incomplete or failed visual QA;
2. re-check the exact candidate hash;
3. create the validated target manifest;
4. print the updated top-level study state.

No target is promoted from an incomplete form.
