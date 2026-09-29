# Case 25 objective technical-geometry evidence

The objective engineering QA has been run on the exact hash-locked v2 candidate.

## Objective checks: PASS

- candidate SHA-256 matches the locked candidate
- one connected component after normal mesh processing
- MatrixToScanDataFiles is exactly identity
- every one of the 6,557 processed candidate vertices exactly matches a source upper-jaw vertex within 1e-6 mm
- maximum candidate-to-source-jaw nearest-vertex distance = 0.0 mm
- scale is therefore preserved from the source scan
- orientation is therefore preserved from the source scan

Candidate dimensions are approximately:

- 7.879 mm
- 6.031 mm
- 4.850 mm

The surface is intentionally not required to be watertight because it represents a visible scanned preparation surface rather than a closed solid.

## Remaining human visual confirmation

Only the following items remain:

1. visually correct tooth identity
2. complete prepared surface
3. complete axial surfaces
4. complete occlusal surface
5. no adjacent-tooth contamination
6. no unacceptable gingival contamination
7. suitable as reference geometry

Use:

`review_templates/case25_technical_geometry_qa_reduced.json`

Scale and orientation are already set to `pass` from objective evidence and do not need subjective re-review.

Once the remaining seven items are confirmed and the overall decision is set to `accept`, run the expert-supervised target promotion command.
