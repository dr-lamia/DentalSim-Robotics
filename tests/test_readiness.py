from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.readiness import evaluate_readiness


def test_readiness_closed_by_default():
    r = evaluate_readiness(repo_root=ROOT)
    assert r.simulator_independent_ci
    assert r.case_assets_present
    assert r.isaac_stage_authored
    assert not r.forced_contact_verified
    assert not r.validated_target_available
    assert not r.preparation_rl_allowed
    assert not r.manuscript_accuracy_outcomes_allowed


def test_validated_target_and_contact_unlock_preparation_rl(tmp_path):
    manifest = tmp_path / "validated.json"
    manifest.write_text(json.dumps({
        "status": "validated_target",
        "mesh_file": "fdi25_validated_target_v2.stl",
        "mesh_sha256": "abc",
        "accuracy_rewards_unlocked": True,
        "reviewers": [
            {"reviewer_id": "expert_a"},
            {"reviewer_id": "expert_b"}
        ]
    }))

    contact = tmp_path / "contact.json"
    contact.write_text(json.dumps({
        "pass": True,
        "contact_detected": True,
        "safety_rollout_accepted": False
    }))

    r = evaluate_readiness(
        repo_root=ROOT,
        validated_target_manifest=manifest,
        forced_contact_result=contact,
    )
    assert r.validated_target_available
    assert r.forced_contact_verified
    assert r.preparation_rl_allowed
    assert r.manuscript_accuracy_outcomes_allowed
