# Case 15 segmentation QA

## Result
A preparation-stump candidate was extracted from the real prepared arch, but it is **not accepted as ground-truth preparation geometry**.

The candidate is a single connected body with:
- 15,310 faces
- 7,883 vertices

However, the transformed exocad preparation margin remains too far from the nearest vertices of the prepared arch:
- median: 2.193 mm
- P95: 3.407 mm
- maximum: 3.715 mm

The current hard QA threshold is 0.50 mm median distance.

## Interpretation
This means the transformed margin and the scanned mesh are not yet proven to share the exact boundary representation needed for outcome scoring.

The candidate may be used for:
- engineering visualization
- testing scene import
- camera placement
- bur path debugging
- collision-system development

It must **not** yet be used for:
- 3D preparation-accuracy ground truth
- RL reward based on final surface accuracy
- manuscript outcome reporting

## Strong visual evidence
The exocad preparation-margin autosave screenshot clearly shows FDI 15 as the prepared stump in the arch.

## Next preferred routes
1. Recover the actual preparation/die surface directly from an exocad scene or exported mesh, if available.
2. Use an expert-verified manual 3D segmentation of the prepared stump.
3. Use a new case where the isolated prepared die is directly exported from the scanner/CAD software.

Until one of these routes is completed, the repository must keep the candidate status explicit.
