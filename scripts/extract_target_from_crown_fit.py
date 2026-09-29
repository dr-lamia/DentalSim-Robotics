#!/usr/bin/env python3
"""Extract a restoration-anchored prepared-tooth candidate from a real exocad case.

This is an engineering candidate only until an expert approves the boundary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--upper-jaw", type=Path, required=True)
    p.add_argument("--crown", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--proximity-mm", type=float, default=0.8)
    p.add_argument("--footprint-pad-mm", type=float, default=0.4)
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    upper = trimesh.load(str(args.upper_jaw), force="mesh")
    crown = trimesh.load(str(args.crown), force="mesh")

    face_centers = upper.triangles_center
    mn, mx = crown.bounds
    pad = args.footprint_pad_mm

    footprint = (
        (face_centers[:, 0] >= mn[0] - pad)
        & (face_centers[:, 0] <= mx[0] + pad)
        & (face_centers[:, 1] >= mn[1] - pad)
        & (face_centers[:, 1] <= mx[1] + pad)
        & (face_centers[:, 2] >= mn[2] - 1.0)
        & (face_centers[:, 2] <= mx[2] + 0.5)
    )

    footprint_idx = np.where(footprint)[0]
    if len(footprint_idx) == 0:
        raise RuntimeError("No upper-jaw faces overlap the crown footprint")

    crown_tree = cKDTree(crown.vertices)
    distances, _ = crown_tree.query(face_centers[footprint], k=1)

    selected = footprint_idx[distances <= args.proximity_mm]
    if len(selected) == 0:
        raise RuntimeError("No faces selected by crown proximity")

    candidate_all = upper.submesh([selected], append=True, repair=False)
    components = sorted(
        candidate_all.split(only_watertight=False),
        key=lambda m: len(m.faces),
        reverse=True,
    )
    candidate = components[0]

    roi = upper.submesh([footprint_idx], append=True, repair=False)

    candidate.export(
        args.out_dir / "prepared_target_candidate_REQUIRES_EXPERT_REVIEW.stl"
    )
    roi.export(args.out_dir / "local_jaw_roi.stl")
    crown.export(args.out_dir / "crown_reference.stl")

    sample = candidate.vertices[:: max(1, len(candidate.vertices) // 5000)]
    dv, _ = crown_tree.query(sample)

    report = {
        "method": (
            "upper-jaw faces inside crown footprint and within the requested "
            "nearest-crown-vertex threshold; largest connected component retained"
        ),
        "proximity_threshold_mm": args.proximity_mm,
        "threshold_status": (
            "engineering selection only; not a clinical tolerance"
        ),
        "candidate_faces": int(len(candidate.faces)),
        "candidate_vertices": int(len(candidate.vertices)),
        "candidate_components_retained": 1,
        "candidate_watertight": bool(candidate.is_watertight),
        "candidate_bounds_mm": np.round(candidate.bounds, 6).tolist(),
        "candidate_to_crown_vertex_distance_mm": {
            "median": float(np.median(dv)),
            "p95": float(np.percentile(dv, 95)),
            "max": float(np.max(dv)),
        },
        "status": "expert_review_required_before_ground_truth",
    }

    (args.out_dir / "candidate_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
