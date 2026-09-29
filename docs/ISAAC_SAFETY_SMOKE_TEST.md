# Isaac safety smoke test

The simulator-independent test suite is green. The next engineering gate is now a single Isaac-side command.

## Required local inputs

The Case-15 engineering asset folder must contain:

- `fdi15_anatomical_start_aligned.stl`
- `prepared_stump_candidate_NOT_GROUND_TRUTH.stl`
- `protected_side_A_roi.ply`
- `protected_side_B_roi.ply`
- `fdi15_design_scan_frame.stl`

These assets are intentionally not committed to the public repository.

## Run

From the repository root:

```bash
bash scripts/isaac/run_case15_safety_smoke.sh \
  /path/to/isaac-sim/python.sh \
  assets/case15 \
  runs/case15_smoke
```

The command performs four sequential gates:

1. converts the real dental meshes to USD;
2. authors the Case-15 engineering scene;
3. deliberately drives the virtual bur into protected anatomy;
4. independently verifies the result JSON.

## Passing result

A pass requires all of the following:

```json
{
  "contact_detected": true,
  "safety_rollout_accepted": false,
  "pass": true
}
```

No-contact is a failure.

## Result artifact

A passing run creates:

`runs/case15_smoke/forced_contact_result.json`

Feed that directly into the project readiness checker:

```bash
python scripts/status/check_readiness.py \
  --forced-contact-result runs/case15_smoke/forced_contact_result.json
```

This unlocks the **safety-validated** state only. It does not unlock preparation-accuracy rewards until the Case-25 target is separately promoted after expert review.
