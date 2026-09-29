# Case 15 NVIDIA engineering scene

This scene exists so Isaac integration can continue while the exact prepared-stump ground truth is being resolved.

## Allowed now
- import real case geometry
- verify mm-to-m conversion
- position a virtual bur
- create cameras
- test 6-DOF end-effector commands
- test collision detection
- deliberately collide with protected anatomy as a negative safety test
- verify reset behavior
- record engineering trajectories

## Disabled
The following remain disabled because the current stump segmentation QA failed:
- surface-accuracy reward
- autonomous preparation success claims
- RL training against the stump candidate as a target
- scientific comparison with the expert preparation
- manuscript outcome reporting using this candidate

## Why this separation matters
The simulator can be engineered with imperfect reference geometry, but a research endpoint cannot.

## Local asset folder
Place the generated Case-15 engineering package under:

`assets/case15/`

Expected files:
- `fdi15_anatomical_start_aligned.stl`
- `prepared_stump_candidate_NOT_GROUND_TRUTH.stl`
- `protected_side_A_roi.ply`
- `protected_side_B_roi.ply`
- `fdi15_design_scan_frame.stl`

Then run:

```bash
python scripts/preflight_case15_engineering.py
```

Only after that preflight succeeds should the assets be imported into the live NVIDIA Isaac scene.
