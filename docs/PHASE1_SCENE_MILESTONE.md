# Phase-1 scene milestone — path-following baseline

## Purpose
Before imitation learning or reinforcement learning, prove that the dental coordinate system, bur motion, camera views, safety sensors and recording pipeline are correct.

## Scene
- Tooth 11: workpiece
- Tooth 12 and tooth 21: protected adjacent anatomy
- Expert target preparation: hidden reference geometry, not a collision body
- Diamond bur: controlled tool
- Three views: overview, occlusal and labial

## Baseline task
The bur approaches a predefined elliptical finish-line path, follows one full ring, and retreats. This is **not** claimed as autonomous crown preparation. It is an engineering baseline for validating the simulator.

## Required tests
1. Mesh registration: original and target preparation overlap in the same coordinate frame.
2. Unit check: 1 mm in the dental mesh becomes 0.001 m at the Isaac API boundary.
3. Action-limit check: no command exceeds 0.25 mm translation or 2 degrees rotation per control step.
4. Protected-contact negative test: intentionally touch tooth 12 or 21 and verify failure/emergency stop.
5. Pulp-clearance negative test: inject a simulated pulp-distance value below 0.50 mm and verify failure.
6. Clean reset: after a safety failure, reset and repeat a safe trajectory.
7. Camera verification: all three declared views show the same task and are recorded with the rollout.
8. HDF5 contract: state, action, camera and success fields are populated before teleoperation data collection starts.

## Gate to teleoperation
Do not collect expert demonstrations until all eight checks pass.

## Gate to RL
Do not train PPO until a rule-based or manually commanded safe path can complete repeatably and the forced-contact negative test is proven to reject success.
