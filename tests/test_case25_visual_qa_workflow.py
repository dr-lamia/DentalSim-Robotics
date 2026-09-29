from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FINALIZE = ROOT / "scripts" / "validation" / "finalize_case25_visual_qa.py"
PREPARE = ROOT / "scripts" / "validation" / "prepare_case25_visual_qa.py"

VISUAL = [
    "correct_tooth_identity",
    "complete_prepared_surface",
    "axial_surfaces_complete",
    "occlusal_surface_complete",
    "no_adjacent_tooth_contamination",
    "no_unacceptable_gingival_contamination",
    "suitable_as_reference_geometry",
]

def test_prepare_visual_qa_is_closed_by_default(tmp_path):
    out = tmp_path / "qa.json"
    subprocess.run([
        sys.executable, str(PREPARE),
        "--operator-id", "expert_a",
        "--review-date", "2026-09-29",
        "--out", str(out)
    ], check=True)
    d = json.loads(out.read_text())
    for k in VISUAL:
        assert d["criteria"][k] == "REVIEW_REQUIRED"
    assert d["criteria"]["scale_verified"] == "pass"
    assert d["criteria"]["orientation_verified"] == "pass"
    assert d["overall_decision"] == "REVIEW_REQUIRED"

def test_finalize_rejects_incomplete_visual_qa(tmp_path):
    qa = json.loads((ROOT / "review_templates" / "case25_technical_geometry_qa_reduced.json").read_text())
    qa["operator_id"] = "expert_a"
    qa["review_date"] = "2026-09-29"
    p = tmp_path / "qa.json"
    p.write_text(json.dumps(qa))
    proc = subprocess.run([
        sys.executable, str(FINALIZE),
        "--mesh", str(tmp_path / "missing.stl"),
        "--qa", str(p)
    ])
    assert proc.returncode != 0
