#!/usr/bin/env python3
"""Case-25 target v2 extraction from exocad margin footprint.

This produces a visible preparation-surface candidate only. It does not
promote the mesh to scientific ground truth.
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh
from shapely import Polygon, contains_xy


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--upper-jaw", type=Path, required=True)
    p.add_argument("--construction-info", type=Path, required=True)
    p.add_argument("--fdi", type=int, default=25)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--margin-buffer-mm", type=float, default=0.15)
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    upper = trimesh.load(str(args.upper_jaw), force="mesh")
    root = ET.parse(args.construction_info).getroot()
    tooth = next(t for t in root.findall(".//Tooth") if t.findtext("Number") == str(args.fdi))

    margin = np.array([
        [float(v.findtext("x")), float(v.findtext("y")), float(v.findtext("z"))]
        for v in tooth.find("Margin").findall("Vec3")
    ])

    poly = Polygon(margin[:, :2]).buffer(args.margin_buffer_mm)
    fc = upper.triangles_center
    inside = contains_xy(poly, fc[:, 0], fc[:, 1])
    selected = np.where(inside)[0]
    if len(selected) == 0:
        raise RuntimeError("No upper-jaw faces found inside margin footprint")

    candidate_all = upper.submesh([selected], append=True, repair=False)
    components = sorted(
        candidate_all.split(only_watertight=False),
        key=lambda m: len(m.faces),
        reverse=True,
    )
    candidate = components[0]

    out_mesh = args.out_dir / (
        f"fdi{args.fdi}_visible_preparation_candidate_v2_REQUIRES_EXPERT_REVIEW.stl"
    )
    candidate.export(out_mesh)

    report = {
        "fdi": args.fdi,
        "reconstruction_type": tooth.findtext("ReconstructionType"),
        "candidate_version": 2,
        "margin_points": int(len(margin)),
        "margin_buffer_mm": args.margin_buffer_mm,
        "candidate_faces": int(len(candidate.faces)),
        "candidate_vertices": int(len(candidate.vertices)),
        "candidate_body_count": int(candidate.body_count),
        "candidate_watertight": bool(candidate.is_watertight),
        "candidate_bounds_mm": np.round(candidate.bounds, 6).tolist(),
        "status": "expert_review_required_before_ground_truth",
    }
    (args.out_dir / "case25_target_v2_QA.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
