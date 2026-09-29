from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "imitation" / "preflight_bc_training.py"


def test_bc_preflight_rejects_mock_session(tmp_path):
    p = tmp_path / "session.json"
    p.write_text(json.dumps({
        "session_type": "mock",
        "human_expert_demonstration": False,
        "input_mode": "scripted",
        "validation_pass": True,
        "episode_count": 10
    }))
    proc = subprocess.run([sys.executable, str(PREFLIGHT), "--teleop-session-manifest", str(p)])
    assert proc.returncode != 0


def test_bc_preflight_accepts_valid_expert_session(tmp_path):
    p = tmp_path / "session.json"
    p.write_text(json.dumps({
        "session_type": "dentist_teleoperation",
        "human_expert_demonstration": True,
        "input_mode": "teleop",
        "validation_pass": True,
        "episode_count": 3,
        "operator_id": "expert_a",
        "tooth_id": "15"
    }))
    proc = subprocess.run([sys.executable, str(PREFLIGHT), "--teleop-session-manifest", str(p)])
    assert proc.returncode == 0


def test_bc_run_schema_forbids_frame_split():
    t = (ROOT / "configs" / "bc_run_manifest_schema.yaml").read_text()
    assert "frame_level_random_split_forbidden" in t
    assert "split_unit: tooth_id" in t
