# BC→PPO / PPO execution handoff

DentalSim-Robotics separates **safety learning** from **preparation-accuracy learning**.

## Four explicit modes

1. `ppo_random_safety`
2. `bc_initialized_ppo_safety`
3. `ppo_random_accuracy`
4. `bc_initialized_ppo_accuracy`

## Safety modes

Safety modes may run after the real Isaac forced-contact test passes.

They may optimize:
- protected-contact avoidance
- action smoothness
- action regularity

They may **not** use:
- surface-deviation reward
- finish-line reward
- taper reward
- over-reduction reward
- preparation-accuracy success

## Accuracy modes

Accuracy modes require both:
- passing Isaac safety gate
- promoted validated target manifest

Preflight example:

```bash
python scripts/rl/preflight_rl_training.py \
  --mode bc_initialized_ppo_accuracy \
  --forced-contact-result results/isaac_runs/<run>/forced_contact_result.json \
  --validated-target-manifest assets/validated_targets/case25/validated_target_manifest.json \
  --bc-run-manifest results/bc_runs/<run>/bc_run_manifest.json
```

The command exits non-zero if any required gate is missing.

## BC initialization

BC-initialized modes require an archived BC run manifest containing the exact exported TorchScript hash.

This creates a reproducible lineage:

expert teleoperation → BC dataset → BC model → PPO initialization → PPO checkpoint.

## Experimental comparison

The future study comparison remains neutral:

- human teleoperation
- BC
- PPO from random initialization
- BC-initialized PPO

Use the same evaluation protocol and report all predefined outcomes without auto-selecting a winner.

## Provenance archive

After training/evaluation:

```bash
python scripts/rl/ingest_rl_run.py \
  --mode bc_initialized_ppo_accuracy \
  --config configs/rl_ppo_profile.yaml \
  --checkpoint runs/ppo/policy.pt \
  --evaluation-report runs/ppo/evaluation.json \
  --repo-commit "$(git rev-parse HEAD)" \
  --forced-contact-result results/isaac_runs/<run>/forced_contact_result.json \
  --validated-target-manifest assets/validated_targets/case25/validated_target_manifest.json \
  --bc-run-manifest results/bc_runs/<run>/bc_run_manifest.json
```
