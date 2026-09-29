#!/usr/bin/env python3
"""Create a hash-locked physical scale calibration for a unitless STL."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--native-distance", type=float, required=True)
    p.add_argument("--known-distance-mm", type=float, required=True)
    p.add_argument("--measurement-description", required=True)
    p.add_argument("--measured-by", required=True)
    p.add_argument("--measurement-date", required=True)
    p.add_argument("--out", type=Path, required=True)
    args=p.parse_args()

    if args.native_distance <= 0 or args.known_distance_mm <= 0:
        raise SystemExit("Distances must be positive.")

    scale=args.known_distance_mm/args.native_distance
    record={
      "schema_version":1,
      "calibration_type":"stl_physical_scale",
      "source_id":args.source_id,
      "mesh_file":args.mesh.name,
      "mesh_sha256":sha256_file(args.mesh),
      "native_distance":args.native_distance,
      "known_distance_mm":args.known_distance_mm,
      "scale_mm_per_native_unit":scale,
      "measurement_description":args.measurement_description,
      "measured_by":args.measured_by,
      "measurement_date":args.measurement_date,
      "created_utc":datetime.now(timezone.utc).isoformat(),
      "status":"physical_scale_calibrated"
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record,indent=2))

if __name__=="__main__":
    main()
