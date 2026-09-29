# Case 25 target validation v2

The v2 candidate uses the native upper-jaw STL and the exocad preparation-margin footprint.

## Source facts
- FDI: 25
- Reconstruction: AnatomicCrown
- Preparation margin: 297 points
- MatrixToScanDataFiles: identity
- Candidate: one connected visible preparation-surface component

## v2 candidate
- 12,864 faces
- 6,557 vertices
- non-watertight visible surface
- status: `expert_review_required_before_ground_truth`

## Important interpretation
The exocad margin is not coincident with the visible upper-jaw scan surface. Therefore margin coordinates are used as a footprint/selection cue, not as a literal measured preparation edge for automatic acceptance.

## Promotion rule
The mesh must not become `validated_target` until:
1. two independent prosthodontist reviews are recorded;
2. both reviewers accept the mesh after any required edits;
3. tooth identity, complete visible boundary, complete axial/occlusal surfaces, and contamination checks all pass;
4. the final reviewed file checksum is locked.

Use `scripts/validate_target_approval.py` to enforce this gate.
