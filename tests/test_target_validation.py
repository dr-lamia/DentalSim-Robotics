from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.target_validation import load_review, promotion_report
from dentalsim.target_gate import target_accuracy_rewards_enabled

def _review(path, reviewer, sha, decision="accept", failed=None):
    criteria = {
        "correct_tooth_identity": "pass",
        "complete_visible_circumferential_boundary": "pass",
        "no_adjacent_tooth_contamination": "pass",
        "no_unacceptable_gingival_contamination": "pass",
        "axial_preparation_complete": "pass",
        "occlusal_preparation_complete": "pass",
        "suitable_for_geometric_target_scoring": "pass",
    }
    if failed:
        criteria[failed] = "fail"
    d = {
        "reviewer_id": reviewer, "reviewer_role": "prosthodontist",
        "review_date": "2026-09-29", "case_id": "case", "fdi": 25,
        "candidate_version": 2, "mesh_sha256": sha, "criteria": criteria,
        "overall_decision": decision,
    }
    path.write_text(json.dumps(d), encoding="utf-8")

def test_requires_two_independent_accepts(tmp_path):
    mesh = tmp_path / "mesh.stl"; mesh.write_bytes(b"locked-mesh")
    sha = hashlib.sha256(mesh.read_bytes()).hexdigest()
    manifest = {"case_id":"case","fdi":25,"candidate_version":2,"sha256":sha}
    r1, r2 = tmp_path/"r1.json", tmp_path/"r2.json"
    _review(r1,"expert_a",sha); _review(r2,"expert_b",sha)
    report = promotion_report(candidate_manifest=manifest, mesh_path=mesh, reviews=[load_review(r1),load_review(r2)])
    assert report["promotable"]

def test_failed_criterion_blocks_promotion(tmp_path):
    mesh = tmp_path / "mesh.stl"; mesh.write_bytes(b"locked-mesh")
    sha = hashlib.sha256(mesh.read_bytes()).hexdigest()
    manifest = {"case_id":"case","fdi":25,"candidate_version":2,"sha256":sha}
    r1, r2 = tmp_path/"r1.json", tmp_path/"r2.json"
    _review(r1,"expert_a",sha); _review(r2,"expert_b",sha,failed="occlusal_preparation_complete")
    report = promotion_report(candidate_manifest=manifest, mesh_path=mesh, reviews=[load_review(r1),load_review(r2)])
    assert not report["promotable"]

def test_accuracy_reward_gate_defaults_closed(tmp_path):
    assert not target_accuracy_rewards_enabled(None)
    assert not target_accuracy_rewards_enabled(tmp_path/"missing.json")

def test_accuracy_reward_gate_opens_for_expert_supervised_technical_qa_target(tmp_path):
    p = tmp_path / "v.json"
    p.write_text(json.dumps({
        "status": "validated_target",
        "mesh_file": "target.stl",
        "mesh_sha256": "abc",
        "source_expert_supervised": True,
        "technical_geometry_qa_pass": True,
        "accuracy_rewards_unlocked": True
    }))
    assert target_accuracy_rewards_enabled(p)
