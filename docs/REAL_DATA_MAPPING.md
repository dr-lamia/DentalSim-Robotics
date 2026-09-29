# Real-data mapping from the existing exocad single-crown dataset

## Confirmed Drive case
Case: `2024-08-15_00241-004`

Confirmed metadata from `constructionInfo`:
- FDI tooth: **15**
- Reconstruction type: **AnatomicCrown**
- Available files include:
  - `upper.ply` — prepared maxillary arch scan
  - `lower.ply` — antagonist scan
  - `tooth_model.obj` — anatomical tooth-library model
  - `design.stl` — technician-approved crown design
  - `constructionInfo` — exocad geometry/transformation metadata
  - `scanInfo` / `dentalProject`

## Important interpretation
This is a valuable robotic-simulation source, but it is **not** a direct original-to-prepared tooth pair.

For the robotics experiment:
- `upper.ply` supplies the *real prepared clinical geometry* and neighboring teeth.
- `tooth_model.obj` can supply an *anatomical starting tooth* after alignment to the case coordinate system.
- `design.stl` is the final crown and is useful for restoration-aware validation, but it is not the preparation target itself.
- `constructionInfo` supplies the FDI number, matrices, insertion-axis information and preparation-margin metadata needed to align/segment the case.

## Proposed conversion pipeline
1. Read the exocad transformation matrix from `constructionInfo`.
2. Keep `upper.ply`, `tooth_model.obj`, and `design.stl` in one common coordinate frame.
3. Extract the prepared tooth region from `upper.ply` using the preparation margin / tooth center metadata.
4. Use the extracted real prepared tooth as the **target preparation mesh**.
5. Align and crop `tooth_model.obj` to create the **starting anatomical tooth**.
6. Keep the two neighboring teeth from the same `upper.ply` as protected collision anatomy.
7. Use `design.stl` as an additional restoration-fit reference for later analysis.

## Why this is scientifically useful
The resulting simulation task is not a purely synthetic idealized tooth. The target preparation comes from a real clinical/laboratory workflow, while the starting anatomy comes from the same exocad case context. This supports realistic geometry while keeping the first experiment simulation-only.

## Current case vs planned Phase-1 tooth
The currently confirmed case is tooth 15, not the originally planned central incisor. Therefore:
- it can be used immediately for **engineering validation of the pipeline**;
- the locked scientific Phase-1 experiment should still use FDI 11/21 once a matching case is identified, or the study protocol can be broadened deliberately to single-unit crown preparations across tooth types.

Do not silently relabel tooth 15 as a central incisor.
