from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.study_state import evaluate_study_state


def test_default_is_engineering_only():
    s = evaluate_study_state()
    assert s.state == "ENGINEERING_ONLY"
    assert not s.safety_verified
    assert not s.rl_accuracy_ready


def test_safety_result_advances_to_safety_validated(tmp_path):
    p = tmp_path / "safety.json"
    p.write_text(json.dumps({
        "pass": True,
        "contact_detected": True,
        "safety_rollout_accepted": False
    }))
    s = evaluate_study_state(forced_contact_result=p)
    assert s.state == "SAFETY_VALIDATED"
    assert s.rl_safety_ready
    assert not s.rl_accuracy_ready


def test_expert_teleop_advances_to_bc_ready(tmp_path):
    safety = tmp_path / "s.json"
    safety.write_text(json.dumps({
        "pass": True,
        "contact_detected": True,
        "safety_rollout_accepted": False
    }))
    teleop = tmp_path / "t.json"
    teleop.write_text(json.dumps({
        "session_type": "dentist_teleoperation",
        "human_expert_demonstration": True,
        "validation_pass": True,
        "episode_count": 3
    }))
    s = evaluate_study_state(forced_contact_result=safety, teleop_session_manifest=teleop)
    assert s.state == "BC_TRAINING_READY"


def test_full_artifacts_advance_to_hybrid_accuracy_ready(tmp_path):
    safety = tmp_path / "s.json"
    safety.write_text(json.dumps({
        "pass": True,
        "contact_detected": True,
        "safety_rollout_accepted": False
    }))
    target = tmp_path / "target.json"
    target.write_text(json.dumps({
        "status": "validated_target",
        "mesh_file": "target.stl",
        "mesh_sha256": "abc",
        "source_expert_supervised": True,
        "technical_geometry_qa_pass": True,
        "accuracy_rewards_unlocked": True
    }))
    teleop = tmp_path / "teleop.json"
    teleop.write_text(json.dumps({
        "session_type": "dentist_teleoperation",
        "human_expert_demonstration": True,
        "validation_pass": True,
        "episode_count": 5
    }))
    bc = tmp_path / "bc.json"
    bc.write_text(json.dumps({
        "run_type": "behavior_cloning_training",
        "artifacts": {"torchscript": {"sha256": "xyz"}}
    }))

    s = evaluate_study_state(
        forced_contact_result=safety,
        validated_target_manifest=target,
        teleop_session_manifest=teleop,
        bc_run_manifest=bc,
    )
    assert s.state == "HYBRID_ACCURACY_READY"
    assert s.rl_accuracy_ready
