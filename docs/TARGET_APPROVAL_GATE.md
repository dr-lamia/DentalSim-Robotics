# Target approval gate

DentalSim-Robotics uses a **closed-by-default target gate**.

## Locked candidate

Case: `2025-12-16_02241-018`  
FDI: `25`  
Candidate version: `2`  
SHA-256: `400972eb83df4f34510863cd023e04d453ad843eda96b4a4169da9f7d71a91e2`

Every review must reference this exact hash. If the mesh changes, existing approvals do not apply.

## Promotion requirements

1. At least two independent reviews.
2. Distinct reviewer pseudonyms.
3. Same case, tooth, version, and mesh hash.
4. Every geometric criterion = `pass`.
5. Both overall decisions = `accept`.
6. Candidate file hash still matches the locked manifest.

`accept_after_edit` does not promote a target. An edited mesh becomes a new candidate/version and must be reviewed again.

## Promotion output

Only a passing run creates:
- `fdi25_validated_target_v2.stl`
- `validated_target_manifest.json`

## Reward lock

Target-dependent terms remain disabled unless that validated manifest exists:
- surface-deviation reward
- finish-line reward
- taper reward
- over-reduction reward
- preparation-complete termination
- scientific preparation-accuracy outcomes

Safety-only functions remain available without a validated target.
