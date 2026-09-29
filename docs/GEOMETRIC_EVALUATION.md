# Geometric evaluation engine

The first validated preparation-accuracy endpoint is now implemented as a
deterministic, bidirectional sampled-surface comparison.

## Primary reported metrics

For a final simulated preparation versus the validated target:

- final → target mean distance (mm)
- final → target median distance (mm)
- final → target p95 distance (mm)
- final → target maximum distance (mm)
- target → final mean / median / p95 / maximum distance
- symmetric bidirectional mean distance
- symmetric bidirectional p95 distance
- fraction of final sampled surface within:
  - 0.25 mm
  - 0.50 mm
  - 1.00 mm

## Gate

The scoring command refuses to run unless the supplied target manifest passes
the target-accuracy gate.

```bash
python scripts/evaluation/score_preparation_geometry.py \
  --final runs/example/final_preparation.stl \
  --target assets/validated_targets/case25/fdi25_validated_target_v2.stl \
  --target-manifest assets/validated_targets/case25/validated_target_manifest.json \
  --out runs/example/geometry_metrics.json
```

## Important limitations

These distances are unsigned. They must not be labelled over-reduction or
under-reduction.

The implementation samples both surfaces and uses nearest-neighbour point-cloud
distances. This is appropriate for open scan surfaces and avoids requiring
watertight meshes.

Finish-line deviation, taper/convergence, signed over-reduction, and remaining
volume remain separate endpoint modules.
