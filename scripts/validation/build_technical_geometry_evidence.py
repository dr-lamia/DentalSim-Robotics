#!/usr/bin/env python3
"""Build objective technical-geometry evidence for an extracted target mesh.

This script does not decide clinical surface completeness. It verifies the
objective engineering properties that can be derived from the source files:
hash identity, component count, source scan transform, coordinate preservation,
scale preservation, and orientation preservation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_text(root: ET.Element, suffix: str) -> str | None:
    for e in root.iter():
        if e.tag.endswith(suffix) and e.text:
            return e.text
    return None


def parse_scan_matrix(root: ET.Element) -> np.ndarray:
    node = next((e for e in root.iter() if e.tag.endswith("MatrixToScanDataFiles")), None)
    if node is None:
        raise ValueError("MatrixToScanDataFiles not found")
    vals = {c.tag.split("}")[-1]: float(c.text) for c in node if c.text}
    return np.array([[vals[f"_{i}{j}"] for j in range(4)] for i in range(4)], dtype=float)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--source-jaw", type=Path, required=True)
    p.add_argument("--construction-info", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--case-label", default="deidentified_case")
    p.add_argument("--fdi", type=int, required=True)
    p.add_argument("--candidate-version", type=int, required=True)
    p.add_argument("--source-expert-supervised", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    candidate = trimesh.load_mesh(args.candidate, process=True)
    source_jaw = trimesh.load_mesh(args.source_jaw, process=False)
    root = ET.parse(args.construction_info).getroot()
    matrix = parse_scan_matrix(root)
    matrix_error = float(np.max(np.abs(matrix - np.eye(4))))

    tree = cKDTree(source_jaw.vertices)
    distances, _ = tree.query(candidate.vertices, k=1)

    components = len(candidate.split(only_watertight=False))
    actual_sha = sha256_file(args.candidate)
    coordinates_preserved = bool(np.max(distances) <= 1e-6)
    transform_identity = bool(matrix_error <= 1e-12)

    report = {
        "schema_version": 1,
        "case_label": args.case_label,
        "fdi": args.fdi,
        "candidate_version": args.candidate_version,
        "candidate_sha256": actual_sha,
        "expected_sha256": args.expected_sha256.lower(),
        "source_expert_supervised": args.source_expert_supervised,
        "source_metadata": {
            "reconstruction_type": first_text(root, "ReconstructionType"),
            "tooth_scan_file_name": first_text(root, "ToothScanFileName"),
            "margin_bottom_type": first_text(root, "MarginBottomType"),
            "matrix_to_scan_data_files": matrix.tolist(),
            "matrix_identity_max_abs_error": matrix_error,
        },
        "candidate_geometry": {
            "vertices": int(len(candidate.vertices)),
            "faces": int(len(candidate.faces)),
            "connected_components": int(components),
            "watertight": bool(candidate.is_watertight),
            "bounds_mm": candidate.bounds.tolist(),
            "extents_mm": candidate.extents.tolist(),
            "surface_area_mm2": float(candidate.area),
        },
        "source_coordinate_consistency": {
            "candidate_vertices_tested": int(len(candidate.vertices)),
            "nearest_source_jaw_vertex_median_mm": float(np.median(distances)),
            "nearest_source_jaw_vertex_p95_mm": float(np.percentile(distances, 95)),
            "nearest_source_jaw_vertex_max_mm": float(np.max(distances)),
            "fraction_exact_within_1e-6_mm": float(np.mean(distances <= 1e-6)),
            "pass": coordinates_preserved,
        },
        "objective_checks": {
            "mesh_hash_matches_locked_candidate": "pass" if actual_sha == args.expected_sha256.lower() else "fail",
            "single_connected_component": "pass" if components == 1 else "fail",
            "source_scan_transform_identity": "pass" if transform_identity else "fail",
            "candidate_preserves_source_scan_coordinates": "pass" if coordinates_preserved else "fail",
            "scale_preserved_from_source_scan": "pass" if coordinates_preserved and transform_identity else "fail",
            "orientation_preserved_from_source_scan": "pass" if coordinates_preserved and transform_identity else "fail",
        },
        "human_confirmation_still_required": [
            "correct_tooth_identity_visual_confirmation",
            "complete_prepared_surface",
            "axial_surfaces_complete",
            "occlusal_surface_complete",
            "no_adjacent_tooth_contamination",
            "no_unacceptable_gingival_contamination",
            "suitable_as_reference_geometry",
        ],
    }

    objective_pass = all(v == "pass" for v in report["objective_checks"].values())
    report["status"] = (
        "objective_technical_checks_pass_visual_confirmation_pending"
        if objective_pass
        else "objective_technical_checks_failed"
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not objective_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
