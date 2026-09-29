from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_prepare_review_template_clears_default_acceptance(tmp_path):
    out = tmp_path / "review.json"
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "validation" / "prepare_expert_review.py"),
        "--reviewer-id", "expert_a",
        "--review-date", "2026-09-29",
        "--out", str(out),
    ], check=True)
    d = json.loads(out.read_text())
    assert d["reviewer_id"] == "expert_a"
    assert d["overall_decision"] == "REVIEW_REQUIRED"
    assert set(d["criteria"].values()) == {"REVIEW_REQUIRED"}


def test_review_template_hash_matches_locked_manifest():
    template = json.loads((ROOT / "review_templates" / "case25_target_review_template.json").read_text())
    manifest = json.loads((ROOT / "configs" / "case25_target_candidate_v2_manifest.json").read_text())
    assert template["mesh_sha256"] == manifest["sha256"]
