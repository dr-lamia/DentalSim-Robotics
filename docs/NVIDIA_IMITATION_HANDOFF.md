# NVIDIA imitation/fine-tuning handoff

The live NVIDIA skill catalog currently includes:
- `i4h-workflow-dataset-mimic`
- `i4h-workflow-dataset-convert`
- `i4h-workflow-finetune`
- `i4h-workflow-train-rl`
- `i4h-workflow-validate`

DentalSim-Robotics keeps its dataset contract simulator-independent so expert demonstrations can be reused by those maintained workflows later.

## Locked dental contract

### Observation order
1. bur pose [7]
2. bur twist [6]
3. target-relative pose [7]
4. adjacent minimum distance [1]
5. previous action [6]

Total: 27 values.

### Action order
1. dx
2. dy
3. dz
4. droll
5. dpitch
6. dyaw

Total: 6 values.

### Coordinate conventions
- translation: metres
- rotation: radians
- dental evaluation metrics: millimetres
- quaternion order: qx, qy, qz, qw

## Non-negotiable handoff rule
Any NVIDIA conversion/fine-tuning pipeline must preserve not only tensor dimensions but also:
- feature order
- coordinate frame
- quaternion convention
- normalization
- action scaling
- previous-action semantics
- reset semantics
- protected-contact termination

## Case-15 boundary
Case 15 may be used to prove:
- data conversion
- imitation infrastructure
- action prediction
- motion safety
- contact avoidance

It may not be used to claim:
- clinically accurate preparation
- expert-equivalent reduction
- finish-line accuracy
- autonomous crown-preparation success

until a validated preparation target is available.
