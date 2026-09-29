# Case 25 target candidate v2

## Source facts
The construction metadata identifies tooth 25 as an `AnatomicCrown`.
The case uses a native upper-jaw STL and the CAD/scan transform is the identity matrix.

## Why v2
The first crown-proximity candidate was useful for localization but did not represent the cervical region well enough. V2 therefore uses the stored preparation margin as a 2D footprint and keeps the largest connected upper-jaw surface component within that footprint.

## V2 result
- 297 stored margin points
- 12,864 faces
- 6,557 vertices
- one connected component
- visible prepared-surface z-range approximately 2.04–6.89 mm

The stored margin-to-visible-surface distance remains approximately:
- median 1.65 mm
- P95 2.23 mm

This is not caused by a CAD/scan matrix mismatch; the matrix is identity. Therefore the stored exocad margin should not be treated as a literal surface contour for automatic target certification.

## Interpretation
V2 is currently the best **visible preparation surface candidate** available from the case.

It can be used for:
- expert 3D review
- Isaac scene import
- engineering visualization
- target-edit workflow development

It cannot yet be used for:
- RL preparation-surface reward
- final preparation-accuracy scoring
- manuscript preparation-accuracy outcomes

## Promotion rule
Promote V2 to the locked target mesh only after expert review confirms:
1. correct tooth identity;
2. complete visible circumferential preparation boundary;
3. no adjacent tooth or gingival contamination;
4. complete axial and occlusal prepared surfaces;
5. suitability for geometric simulator scoring.

If edits are required, save the edited mesh as a new version and preserve the review record.
