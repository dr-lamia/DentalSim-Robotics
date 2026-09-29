# DentalSim-Robotics

Research scaffold for AI-guided / autonomous dental crown preparation in NVIDIA Isaac for Healthcare.

## Phase 1 objective
Train and validate a simulated policy that prepares a maxillary central incisor toward an expert-defined full-coverage crown preparation while minimizing geometric error and unsafe contact.

## Core research question
Can an AI policy achieve a clinically acceptable target preparation in simulation while preserving tooth structure and avoiding adjacent-tooth damage?

## Modes
1. Expert teleoperation
2. AI-assisted control (later)
3. Autonomous policy

## Primary endpoint
3D surface deviation (mm) between the final preparation and the expert target mesh.

## Secondary endpoints
- axial reduction error
- occlusal/incisal reduction error
- total occlusal convergence error
- finish-line deviation
- undercut occurrence
- over-reduction volume
- remaining tooth volume
- adjacent-tooth collisions
- pulpal-risk violations
- surface smoothness
- completion time / steps
- task success rate

## NVIDIA mapping
- i4h-workflow-create: base workflow scaffold
- i4h-workflow-scene-edit: tooth/bur/robot/cameras/physics
- i4h-workflow-dataset-teleop: expert demonstrations
- i4h-workflow-train-rl: PPO-based policy training
- i4h-workflow-validate: rollout validation

See `docs/I4H_INTEGRATION.md` before creating the actual I4H workflow. The current NVIDIA create skill requires a supported specialty and does not expose dentistry as a native specialty.

## Repository layout
- `configs/` task and reward contracts
- `src/dentalsim/` reusable scoring logic
- `docs/` study protocol and NVIDIA integration plan
- `assets/` placeholders for tooth, target-prep and bur meshes
- `tests/` unit tests for scoring
- `results/` evaluation outputs

## Phase 1 success definition
A rollout succeeds only if all mandatory safety gates pass and the final preparation is within configurable geometric tolerances.

## Current implementation milestone
Phase-1 scene contract is now implemented independent of Isaac Sim:
- registered dental asset contract
- SI-unit conversion boundary for Isaac
- protected adjacent-tooth safety state
- pulp-clearance safety gate
- bounded 6-DOF actions
- deterministic finish-line path-following baseline
- preflight script before live Isaac authoring

Run:
```bash
python scripts/preflight_phase1.py
pytest -q
```

The preflight intentionally fails with `ASSETS NOT READY` until the five required dental meshes are placed in `assets/`. This prevents the project from silently substituting toy geometry for the research experiment.
