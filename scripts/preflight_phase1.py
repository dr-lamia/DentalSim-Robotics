#!/usr/bin/env python3
"""Check whether Phase-1 is ready to move into NVIDIA Isaac scene authoring."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.baseline_controller import finish_line_ring
from dentalsim.isaac_adapter import isaac_available, phase1_scene_plan, validate_asset_files
from dentalsim.scene_contract import path_length_mm

plan = phase1_scene_plan(ROOT)
missing = validate_asset_files(plan)
path = finish_line_ring()
print("DentalSim-Robotics Phase-1 preflight")
print(f"Scene assets declared: {len(plan.assets)}")
print(f"Baseline waypoints: {len(path)}")
print(f"Baseline path length: {path_length_mm(path):.2f} mm")
print(f"Isaac import available: {isaac_available()}")
if missing:
    print("Missing required meshes:")
    for item in missing:
        print(f"  - {item}")
    print("STATUS: CONTRACT READY / ASSETS NOT READY")
    raise SystemExit(2)
print("STATUS: ASSETS READY FOR ISAAC AUTHORING")
