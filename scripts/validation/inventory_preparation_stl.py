#!/usr/bin/env python3
"""Create a reproducible geometry-intake report for a preparation STL.

The report describes geometry only. It does not decide whether the mesh is an
isolated tooth, clinically acceptable, or a validated reference target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import trimesh


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assess(path: Path, source_id: str, expert_supervised: bool) -> dict:
    mesh = trimesh.load_mesh(path, process=True)
    components = mesh.split(only_watertight=False)
    component_faces = sorted((len(c.faces) for c in components), reverse=True)

    return {
        "schema_version": 1,
        "source_id": source_id,
        "file_name": path.name,
        "file_size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "source_expert_supervised": expert_supervised,
        "geometry": {
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "connected_components": int(len(components)),
            "largest_component_faces": int(component_faces[0]) if component_faces else 0,
            "watertight": bool(mesh.is_watertight),
            "bounds_native": mesh.bounds.tolist(),
            "extents_native": mesh.extents.tolist(),
            "surface_area_native2": float(mesh.area),
        },
        "status": "geometry_described_review_scope_required",
        "important_note": (
            "Dimensions/component count alone must not be used to certify an "
            "isolated preparation or validated target."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stl", type=Path, required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--expert-supervised", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    report = assess(args.stl, args.source_id, args.expert_supervised)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
