# Validated-target pathway — Case 25

## Why Case 25 is stronger than Case 15

Case `2025-12-16_02241-018` includes:
- native upper-jaw STL
- native lower-jaw STL
- crown STL
- tooth-model OBJ
- preparation-margin CAD stage
- construction metadata

Its `MatrixToScanDataFiles` is the identity matrix, so there is no scan/CAD coordinate-transform ambiguity.

## Restoration-anchored extraction

Instead of trusting the stored margin as the exact scanned preparation boundary, the extraction uses the fitted crown as a spatial anchor:

1. restrict the native upper-jaw STL to the crown footprint;
2. compute nearest-crown-vertex distance for upper-jaw face centers;
3. retain faces within 0.8 mm;
4. retain the largest connected component.

The 0.8-mm value is an engineering extraction threshold selected from the observed distance distribution. It is **not** a clinical tolerance.

## Candidate result

The current candidate contains:
- 14,809 faces
- 7,694 vertices
- one connected body

Candidate-to-crown nearest-vertex distance:
- median: 0.391 mm
- P95: 0.778 mm
- maximum: 0.923 mm

## Ground-truth gate

The candidate is not promoted automatically.

Before it becomes the target-preparation mesh, the boundary must be reviewed in 3D against:
- the native upper-jaw scan;
- the crown reference;
- the exocad preparation-margin screenshot.

### Recommended expert review

Two calibrated prosthodontists independently review:
1. complete circumferential finish-line inclusion;
2. absence of adjacent-tooth/gingival contamination;
3. complete axial and occlusal preparation surface;
4. no obvious missing preparation surface;
5. correct FDI tooth identity.

Each records:
- Accept
- Accept after edit
- Reject

If both accept, the mesh can be locked as the target.
If one requests edits, perform the edit and repeat review.
If reviewers disagree, adjudicate jointly and preserve the final review record.

## Scientific rule

Until that review is complete, this candidate may be imported into Isaac for scene engineering but cannot drive preparation-accuracy reward or manuscript accuracy outcomes.
