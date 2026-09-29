# Dental PPO / NVIDIA RSL-RL handoff

NVIDIA's current `i4h-workflow-train-rl` skill uses maintained online RL
profiles and requires the Workflow, Scene, objective, model, reset and runtime
contracts to be checked before training.

## Dental mapping

The intended future profile is:

`rl/profiles/dental_crown_prep.yaml`

The locked interfaces are:

- observation dimension: 27
- action dimension: 6
- action translation unit: metres
- action rotation unit: radians
- max translation: 0.25 mm/step
- max rotation: 2 deg/step
- protected-contact termination: immediate failure

## Two-stage RL use

### Stage A — engineering/safety RL
Allowed with the current Case-15 engineering scene:
- smooth motion
- action regularity
- collision avoidance
- protected-contact termination
- reset behavior

Not allowed:
- target surface reward
- finish-line reward
- taper reward
- preparation-success claim

### Stage B — preparation RL
Enabled only after a validated target preparation exists.

Adds:
- progress-to-target reward
- surface-deviation reward
- finish-line reward
- taper reward
- over-reduction penalty
- clinically meaningful success termination

## Initialization study

Three policy conditions can eventually be compared on the same locked teeth:
- BC only
- PPO from random initialization
- BC-initialized PPO

The repository should report each condition using identical rollout metrics.
No method should be declared superior without the planned statistical analysis.

## NVIDIA execution lifecycle

Follow the maintained NVIDIA sequence:
1. resolve the exact i4h-workflows checkout
2. validate scene/objective/action/reset contracts
3. dry-run the requested profile
4. preflight CUDA/Isaac Lab runtime
5. train in the foreground
6. evaluate simulator success
7. export the policy
8. validate through the normal Workflow runner

The current ChatGPT environment cannot perform the CUDA/Isaac Lab training step.
