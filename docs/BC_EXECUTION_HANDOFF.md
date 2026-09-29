# Behavior cloning execution handoff

## Preconditions

BC training may start only after at least one validated human dentist teleoperation session exists.

Run:

```bash
python scripts/imitation/preflight_bc_training.py \
  --teleop-session-manifest results/teleop_sessions/<session_id>/session_manifest.json
```

For the first engineering check, the default minimum is 3 episodes.

## Split rule

The scientific split unit is the **tooth**, never individual frames.

Create a split manifest:

```bash
python scripts/imitation/create_tooth_split.py \
  --session-manifests results/teleop_sessions/*/session_manifest.json \
  --test-tooth 25 \
  --out runs/bc/tooth_split.json
```

A single-tooth engineering dataset can be used to debug the pipeline, but not for held-out tooth generalization claims.

## Train

Use the existing trainer:

```bash
python scripts/imitation/train_behavior_cloning.py ...
```

The policy remains:
27-D state → MLP [256, 256, 128] → 6-D delta-pose action.

Hard runtime action bounds remain:
- translation <= 0.25 mm/step
- rotation <= 2 degrees/step

## Evaluate

Use the existing held-out evaluator:

```bash
python scripts/imitation/evaluate_behavior_cloning.py ...
```

Report:
- mean / median / p95 translation action error (mm)
- mean / median / p95 rotation action error (degrees)
- action-bound violations

Do not describe these as preparation accuracy.

## Archive the run

```bash
python scripts/imitation/ingest_bc_run.py \
  --split-manifest runs/bc/tooth_split.json \
  --config configs/behavior_cloning.yaml \
  --checkpoint runs/bc/model.pt \
  --torchscript runs/bc/model.ts \
  --evaluation-report runs/bc/evaluation.json \
  --repo-commit "$(git rev-parse HEAD)"
```

The archive hashes the checkpoint, TorchScript model, config, split and evaluation report for reproducibility.
