# Physical scale calibration for direct preparation STL sources

The direct preparation STL files render like isolated preparation objects, but their native coordinate extents must **not** be assumed to be millimetres.

The STL format itself carries geometry but no unit field. The files have a `3Shape` binary header, but the physical scale for this particular exported preparation library still needs source-specific confirmation.

## Rule

No millimetre-based endpoint or reward may use a direct STL source until a hash-locked scale calibration exists.

Examples of acceptable calibration references:
- a known scanner/CAD measurement from the same source case;
- a documented tooth dimension measured in the source software;
- a physical reference dimension associated with the scan.

Do not derive scale merely by forcing the tooth to match an assumed average tooth size.

## Command

```bash
python scripts/validation/calibrate_stl_scale.py \
  --mesh path/to/preparation.stl \
  --source-id prep_full_veneer_01 \
  --native-distance NATIVE_VALUE \
  --known-distance-mm KNOWN_MM \
  --measurement-description "..." \
  --measured-by REVIEWER_ID \
  --measurement-date YYYY-MM-DD \
  --out results/scale/prep_full_veneer_01.json
```

The output records:

`scale_mm_per_native_unit = known_distance_mm / native_distance`

and locks the calibration to the exact mesh SHA-256.
