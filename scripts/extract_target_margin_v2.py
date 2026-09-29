#!/usr/bin/env python3
"""Case-25 target candidate v2: margin-footprint extraction.

This produces a visible prepared-surface candidate for expert review.
It does not automatically promote the mesh to scientific ground truth.
"""
from __future__ import annotations
import argparse, json, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from shapely import contains_xy

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upper-jaw",type=Path,required=True)
    p.add_argument("--construction-info",type=Path,required=True)
    p.add_argument("--fdi",type=int,default=25)
    p.add_argument("--buffer-mm",type=float,default=0.15)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)

    upper=trimesh.load(str(args.upper_jaw),force="mesh")
    root=ET.parse(args.construction_info).getroot()
    tooth=next(t for t in root.findall(".//Tooth") if t.findtext("Number")==str(args.fdi))
    margin=np.array([[float(v.findtext("x")),float(v.findtext("y")),float(v.findtext("z"))] for v in tooth.find("Margin").findall("Vec3")])

    poly=Polygon(margin[:,:2]).buffer(args.buffer_mm)
    fc=upper.triangles_center
    inside=contains_xy(poly,fc[:,0],fc[:,1])
    idx=np.where(inside)[0]
    if len(idx)==0:
        raise RuntimeError("No faces fall inside margin footprint")

    all_parts=upper.submesh([idx],append=True,repair=False)
    comps=sorted(all_parts.split(only_watertight=False),key=lambda m:len(m.faces),reverse=True)
    candidate=comps[0]

    tree=cKDTree(candidate.vertices)
    d,_=tree.query(margin,k=1)

    axis_scan=np.array([float(tooth.find("AxisInsertionScanInfo").findtext(k)) for k in ("x","y","z")],dtype=float)
    axis_soft=np.array([float(tooth.find("Axis").findtext(k)) for k in ("x","y","z")],dtype=float)
    axis_scan/=np.linalg.norm(axis_scan)
    axis_soft/=np.linalg.norm(axis_soft)

    out_mesh=args.out_dir/f"fdi{args.fdi}_visible_preparation_candidate_v2_REQUIRES_EXPERT_REVIEW.stl"
    candidate.export(out_mesh)

    report={
        "fdi":args.fdi,
        "reconstruction_type":tooth.findtext("ReconstructionType"),
        "candidate_version":2,
        "margin_points":int(len(margin)),
        "candidate_faces":int(len(candidate.faces)),
        "candidate_vertices":int(len(candidate.vertices)),
        "candidate_body_count":int(candidate.body_count),
        "candidate_watertight":bool(candidate.is_watertight),
        "candidate_bounds_mm":np.round(candidate.bounds,6).tolist(),
        "axis_insertion_scan_info":axis_scan.tolist(),
        "software_axis":axis_soft.tolist(),
        "axis_opposition_angle_deg":float(np.degrees(np.arccos(np.clip(np.dot(axis_scan,axis_soft),-1,1)))),
        "margin_to_candidate_nearest_vertex_mm":{
            "median":float(np.median(d)),
            "p95":float(np.percentile(d,95)),
            "max":float(np.max(d)),
            "min":float(np.min(d)),
        },
        "status":"expert_review_required_before_ground_truth",
        "warning":"Stored exocad margin is not coincident with the visible scan surface; do not use the candidate as ground truth without expert review."
    }
    (args.out_dir/"case25_target_v2_QA.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
