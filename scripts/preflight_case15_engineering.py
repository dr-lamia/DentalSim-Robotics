#!/usr/bin/env python3
"""Preflight the real Case-15 engineering scene.

This intentionally allows scene engineering while preventing ground-truth
accuracy claims when the segmentation QA gate has failed.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "case15"
RESULTS = ROOT / "results" / "case15_segmentation_QA.json"

required = [
    "fdi15_anatomical_start_aligned.stl",
    "prepared_stump_candidate_NOT_GROUND_TRUTH.stl",
    "protected_side_A_roi.ply",
    "protected_side_B_roi.ply",
    "fdi15_design_scan_frame.stl",
]

missing = [name for name in required if not (ASSETS / name).exists()]
print("DentalSim Case-15 engineering preflight")
if missing:
    print("Missing local case assets:")
    for name in missing:
        print("  -", name)
    print("STATUS: CASE ASSETS NOT INSTALLED")
    raise SystemExit(2)

qa = json.loads(RESULTS.read_text(encoding="utf-8"))
if qa.get("qa_gate_passed"):
    print("Segmentation QA: PASS")
else:
    print("Segmentation QA: FAIL — engineering scene only")
    print("Surface-accuracy reward and scientific success claims remain disabled.")

print("STATUS: READY FOR ISAAC ENGINEERING SCENE")
