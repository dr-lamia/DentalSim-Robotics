#!/usr/bin/env python3
"""Extract an engineering preparation candidate from an exocad arch ROI.

This script deliberately does NOT certify the output as ground truth.
It uses the transformed preparation margin as a spatial anchor, then applies
a QA gate based on the distance from that margin to the scanned arch surface.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely import Polygon, contains_xy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roi", required=True, type=Path)
    ap.add_argument("--margin-csv", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--buffer-mm", type=float, default=0.15)
    ap.add_argument("--margin-surface-median-max-mm", type=float, default=0.50)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    roi = trimesh.load(str(args.roi), force="mesh")
    margin = np.loadtxt(args.margin_csv, delimiter=",", skiprows=1)

    center = margin.mean(axis=0)
    _, _, vh = np.linalg.svd(margin - center, full_matrices=False)
    axes = vh

    margin_local = (margin - center) @ axes.T
    poly = Polygon(margin_local[:, :2])
    if not poly.is_valid:
        poly = poly.buffer(0)
    if not poly.is_valid:
        raise RuntimeError("Preparation-margin polygon is invalid")

    face_centers = roi.triangles_center
    face_local = (face_centers - center) @ axes.T

    inside = contains_xy(poly.buffer(args.buffer_mm), face_local[:, 0], face_local[:, 1])
    crown_side = face_local[:, 2] <= 0.50
    face_idx = np.where(inside & crown_side)[0]
    if len(face_idx) == 0:
        raise RuntimeError("No stump-candidate faces selected")

    stump = roi.submesh([face_idx], append=True, repair=False)

    # Two protected context regions are intentionally called side A/B because
    # mesial/distal identity has not yet been independently verified.
    outside = ~contains_xy(poly.buffer(0.25), face_local[:, 0], face_local[:, 1])
    band = (
        (np.abs(face_local[:, 0]) <= 7.0)
        & (np.abs(face_local[:, 1]) <= 6.0)
        & (face_local[:, 2] <= 0.80)
    )
    side_a_idx = np.where(outside & band & (face_local[:, 0] < -3.5))[0]
    side_b_idx = np.where(outside & band & (face_local[:, 0] > 3.5))[0]

    side_a = roi.submesh([side_a_idx], append=True, repair=False)
    side_b = roi.submesh([side_b_idx], append=True, repair=False)

    # Critical QA: a true margin should be geometrically close to the scan.
    tree = cKDTree(roi.vertices)
    d, _ = tree.query(margin, k=1)
    median_d = float(np.median(d))
    p95_d = float(np.percentile(d, 95))
    max_d = float(np.max(d))
    qa_passed = median_d <= args.margin_surface_median_max_mm

    stump.export(args.out_dir / "prepared_stump_candidate_NOT_GROUND_TRUTH.stl")
    side_a.export(args.out_dir / "protected_side_A_roi.ply")
    side_b.export(args.out_dir / "protected_side_B_roi.ply")

    report = {
        "status": "qa_passed_candidate" if qa_passed else "candidate_only_not_ground_truth",
        "method": (
            "PCA plane from transformed preparation margin; select prepared-arch "
            "faces whose projected centers fall inside a buffered margin polygon "
            "and on the crown/stump side of the margin plane."
        ),
        "candidate": {
            "faces": int(len(stump.faces)),
            "vertices": int(len(stump.vertices)),
            "body_count": int(stump.body_count),
            "watertight": bool(stump.is_watertight),
            "bounds_mm": np.round(stump.bounds, 6).tolist(),
        },
        "margin_to_full_arch_nearest_vertex_mm": {
            "median": median_d,
            "p95": p95_d,
            "max": max_d,
        },
        "qa_threshold_median_mm": args.margin_surface_median_max_mm,
        "qa_gate_passed": bool(qa_passed),
        "warning": (
            "Do not use the stump candidate as preparation ground truth unless "
            "the QA gate passes and the result is visually verified."
        ),
    }
    (args.out_dir / "segmentation_QA.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))

    if not qa_passed:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
