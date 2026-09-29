# Phase-1 dental assets

Place the following meshes here before NVIDIA Isaac authoring:

- `tooth_11_unprepared.stl` — maxillary right central incisor, original geometry
- `tooth_11_target_prep.stl` — expert-approved full crown preparation for the same tooth
- `tooth_12.stl` — adjacent maxillary right lateral incisor
- `tooth_21.stl` — adjacent maxillary left central incisor
- `diamond_bur.stl` — simplified or manufacturer-derived bur mesh

## Critical rule
`tooth_11_unprepared.stl` and `tooth_11_target_prep.stl` must share the same coordinate frame and scale. Do not independently center/rotate them after registration.

Preferred export: binary STL or OBJ, millimetre scale, watertight where feasible. Preserve a case ID in the source dataset outside the mesh filename so train/test grouping is possible later.
