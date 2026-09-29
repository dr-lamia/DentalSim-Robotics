# Behavior cloning milestone

## Why this exists

The first learned controller should be simple and auditable before RL. Behavior cloning (BC) provides a baseline that learns the 6-DOF operator action from the same observation contract that will later be used inside Isaac.

## Dataset rules

Only episodes that:
- are labelled `mode=teleop`
- contain no protected-anatomy contact
- pass the HDF5/action-bound validator

are eligible.

Train/validation splitting is performed by **tooth ID**, never by frame. Frames from one tooth cannot appear in both splits.

## State vector

27 values in this locked order:
1. bur pose: 7
2. bur twist: 6
3. target-relative pose: 7
4. adjacent minimum distance: 1
5. previous action: 6

## Action vector

6 values:
- dx, dy, dz (metres)
- droll, dpitch, dyaw (radians)

The exported runtime clamps every prediction to:
- +/- 0.25 mm translation per step
- +/- 2 degrees rotation per step

## Case-15 restriction

Because Case 15 does not yet have validated preparation-ground-truth segmentation, it can be used only for:
- motor-control pretraining
- safety behavior
- camera/action pipeline testing

It cannot establish preparation-accuracy performance.

## Train

```bash
pip install -r requirements-teleop.txt -r requirements-imitation.txt

python scripts/imitation/train_behavior_cloning.py \
  path/to/teleop_1.hdf5 path/to/teleop_2.hdf5 \
  --output-dir runs/bc_case15
```

Artifacts:
- `dental_bc_v1.pt` TorchScript policy
- `normalization.json`
- `training_history.json`
- `report.json`

## NVIDIA handoff

The current NVIDIA skills catalog includes maintained Isaac-for-Healthcare data mimic and fine-tuning workflows. Once real expert demonstrations exist, our locked observation/action schema should be converted into that maintained pipeline rather than changing the dental dataset ad hoc.
