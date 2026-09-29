#!/usr/bin/env python3
"""Prepare an exocad single-crown case for DentalSim-Robotics.

Outputs are engineering assets, not a clinically validated segmentation.
"""
from __future__ import annotations
import argparse, json, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from trimesh.registration import icp

def _floats(el):
    return [float(x) for x in el.itertext() if x.strip()]

def _tooth(root, fdi: int):
    for t in root.findall('.//Tooth'):
        if t.findtext('Number') == str(fdi):
            return t
    raise ValueError(f'FDI tooth {fdi} not found in constructionInfo')

def _transform_row(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    p = np.c_[points, np.ones(len(points))] @ matrix
    return p[:, :3] / p[:, 3, None]

def _mesh(path: Path, kind: str) -> trimesh.Trimesh:
    obj = trimesh.load(str(path), file_type=kind, force='mesh')
    if not isinstance(obj, trimesh.Trimesh):
        raise TypeError(f'{path} did not load as a mesh')
    return obj

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--upper', required=True, type=Path)
    ap.add_argument('--tooth-model', required=True, type=Path)
    ap.add_argument('--design', required=True, type=Path)
    ap.add_argument('--construction-info', required=True, type=Path)
    ap.add_argument('--fdi', required=True, type=int)
    ap.add_argument('--out-dir', required=True, type=Path)
    ap.add_argument('--roi-pad-mm', type=float, default=1.0)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    root = ET.parse(args.construction_info).getroot()
    tooth = _tooth(root, args.fdi)
    recon = tooth.findtext('ReconstructionType')
    margin_el = tooth.find('Margin')
    if margin_el is None:
        raise ValueError('No preparation margin found')
    margin_design = np.array([
        [float(v.findtext('x')), float(v.findtext('y')), float(v.findtext('z'))]
        for v in margin_el.findall('Vec3')
    ])

    matrix_el = root.find('.//MatrixToScanDataFiles')
    if matrix_el is None:
        raise ValueError('MatrixToScanDataFiles not found')
    matrix_to_scan = np.array(_floats(matrix_el), dtype=float).reshape(4, 4)
    design_to_scan = np.linalg.inv(matrix_to_scan)
    margin_scan = _transform_row(margin_design, design_to_scan)

    upper = _mesh(args.upper, 'ply')
    tooth_model = _mesh(args.tooth_model, 'obj')
    design = _mesh(args.design, 'stl')

    design_scan = design.copy()
    design_scan.vertices = _transform_row(design.vertices, design_to_scan)

    source = tooth_model.vertices[::5]
    target = design_scan.vertices[::5]
    icp_matrix, _, icp_cost = icp(
        source, target, initial=np.eye(4), threshold=1e-6,
        max_iterations=100, reflection=False, scale=False
    )
    tooth_aligned = tooth_model.copy()
    tooth_aligned.apply_transform(icp_matrix)

    tree = cKDTree(design_scan.vertices)
    distances, _ = tree.query(tooth_aligned.vertices[::10], k=1)

    mn = design_scan.bounds[0] - args.roi_pad_mm
    mx = design_scan.bounds[1] + args.roi_pad_mm
    centers = upper.triangles_center
    face_idx = np.where(np.all((centers >= mn) & (centers <= mx), axis=1))[0]
    if len(face_idx) == 0:
        raise RuntimeError('No upper-arch faces intersect mapped design ROI')
    roi = upper.submesh([face_idx], append=False, repair=False)[0]

    design_scan.export(args.out_dir / f'fdi{args.fdi}_design_scan_frame.stl')
    tooth_aligned.export(args.out_dir / f'fdi{args.fdi}_anatomical_start_aligned.stl')
    roi.export(args.out_dir / f'fdi{args.fdi}_prepared_arch_roi.ply')
    np.savetxt(args.out_dir / f'fdi{args.fdi}_margin_scan.csv', margin_scan,
               delimiter=',', header='x_mm,y_mm,z_mm', comments='')

    report = {
        'fdi': args.fdi,
        'reconstruction_type': recon,
        'coordinate_mapping': 'design_to_scan = inverse(MatrixToScanDataFiles), row-vector convention',
        'margin_points': int(len(margin_scan)),
        'margin_scan_bounds_mm': np.round([margin_scan.min(0), margin_scan.max(0)], 6).tolist(),
        'design_scan_bounds_mm': np.round(design_scan.bounds, 6).tolist(),
        'anatomical_start_aligned_bounds_mm': np.round(tooth_aligned.bounds, 6).tolist(),
        'prepared_arch_roi_bounds_mm': np.round(roi.bounds, 6).tolist(),
        'prepared_arch_roi_faces': int(len(roi.faces)),
        'icp_cost': float(icp_cost),
        'aligned_to_design_nearest_distance_mm': {
            'median': float(np.median(distances)),
            'mean': float(np.mean(distances)),
            'p95': float(np.percentile(distances, 95)),
        },
        'status': 'engineering_alignment_ready_exact_preparation_segmentation_pending',
        'warning': 'Do not treat prepared_arch_roi as an exact preparation mesh until the stump surface is segmented and visually verified.'
    }
    (args.out_dir / 'case_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
