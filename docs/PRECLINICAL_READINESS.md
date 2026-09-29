# Preclinical readiness gate

DentalSim-Robotics now has a single project-level readiness checker.

## Current state

With no external runtime artifacts supplied, the expected state is:

- simulator-independent CI: ready
- Case-25 candidate assets/config: ready
- Isaac stage code: ready
- forced-contact result: pending
- real dentist teleoperation dataset: pending
- behavior-cloning checkpoint: pending
- validated target manifest: pending
- preparation RL: blocked
- manuscript accuracy outcomes: blocked

This is intentional.

## Command

```bash
python scripts/status/check_readiness.py
```

After Isaac contact validation:

```bash
python scripts/status/check_readiness.py \
  --forced-contact-result runs/forced_contact_result.json
```

After target promotion and BC training:

```bash
python scripts/status/check_readiness.py \
  --forced-contact-result runs/forced_contact_result.json \
  --validated-target-manifest assets/validated_targets/case25/validated_target_manifest.json \
  --teleop-hdf5 data/expert_teleop.hdf5 \
  --bc-policy runs/bc/dental_bc_v1.pt
```

## Unlock rule

Preparation RL and manuscript preparation-accuracy outcomes require both:

1. a formally promoted target manifest, and
2. a passing Isaac forced-contact negative test.

Teleoperation and BC readiness are reported separately because they are needed for the BC and hybrid branches but not for a random-initialized PPO baseline.

## Why this matters

The repository can now distinguish three states without relying on human memory:

- `ENGINEERING_ONLY`
- safety-validated but target-unvalidated
- `PREPARATION_ACCURACY_UNLOCKED`

This prevents accidental scientific claims from engineering-only simulations.
