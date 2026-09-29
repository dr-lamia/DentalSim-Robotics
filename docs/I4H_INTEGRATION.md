# NVIDIA Isaac for Healthcare integration

## Current NVIDIA constraint
The current `i4h-workflow-create` skill (v0.8.0) requires exactly one supported specialty:
- laparoscopic-robotics
- ultrasound-robotics
- endoluminal-robotics
- hospital-automation-robotics

There is no native `dental-robotics` specialty today. Therefore this repository does not silently create an I4H workflow under an unrelated specialty.

## Intended workflow id
`dental_crown_prep`

## Once a specialty/integration strategy is explicitly selected
Use NVIDIA's blank-workflow generator first, then add dental assets and behavior incrementally.

Blank creation pattern:
```bash
./scripts/create_blank_environment.py dental_crown_prep --specialty <SUPPORTED_SPECIALTY> --validate
```

Expected generated files:
```text
arena/i4h_arena/assets/dental_crown_prep.py
arena/i4h_arena/scenes/dental_crown_prep.py
arena/i4h_arena/scenes/manifest/dental_crown_prep.yaml
workflows/i4h_workflows/<specialty>/dental_crown_prep.py
workflows/tests/test_dental_crown_prep_contract.py
```

## Scene authoring requirements
Add only after blank creation:
- maxillary central-incisor tooth mesh
- neighboring teeth
- expert target preparation mesh (non-collidable visual/reference layer)
- pulpal safety volume
- gingival/fixture geometry as needed
- dental bur/end effector
- robot embodiment
- contact sensors for tooth/adjacent contacts
- camera(s)
- randomization of tooth pose and morphology

## Teleoperation stage
After `teleop` is declared and visibly verified:
```bash
./run.sh dental_crown_prep --teleop <supported_device> --episodes 5 --attempts 3 --record
```
Human demonstrations must be recorded by a real operator. The agent must not pretend to generate interactive demonstrations unattended.

## RL profile concept
Create `rl/profiles/dental_crown_prep.yaml` and a declarative PPO config. Preserve exact observation/action ordering between training and exported runtime policy.

Suggested initial action contract:
- 6-D relative end-effector pose

Suggested state observations:
- bur pose and velocity
- target-relative pose
- distance-to-target features
- safety distances
- remaining-tooth descriptors
- previous action

## Validation
For exported policy:
```bash
./run.sh dental_crown_prep --policy --checkpoint /absolute/path/policy.pt --episodes 20 --attempts 3 --record verify.hdf5
```
Do not call the system "validated" unless requested episodes complete, success metadata are present, and the HDF5 rollout is inspected.

## Required negative safety test
Deliberately force contact with an adjacent tooth once after authoring/changing the collision rule. Confirm non-zero contact sensing and confirm the rollout is rejected.
