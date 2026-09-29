from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "rl" / "preflight_rl_training.py"


def _safety(path):
    path.write_text(json.dumps({
        "pass": True,
        "contact_detected": True,
        "safety_rollout_accepted": False
    }))


def test_safety_ppo_does_not_require_validated_target(tmp_path):
    s = tmp_path / "safety.json"; _safety(s)
    proc = subprocess.run([
        sys.executable, str(PREFLIGHT),
        "--mode", "ppo_random_safety",
        "--forced-contact-result", str(s)
    ])
    assert proc.returncode == 0


def test_accuracy_ppo_requires_validated_target(tmp_path):
    s = tmp_path / "safety.json"; _safety(s)
    proc = subprocess.run([
        sys.executable, str(PREFLIGHT),
        "--mode", "ppo_random_accuracy",
        "--forced-contact-result", str(s)
    ])
    assert proc.returncode != 0


def test_bc_initialized_mode_requires_bc_manifest(tmp_path):
    s = tmp_path / "safety.json"; _safety(s)
    proc = subprocess.run([
        sys.executable, str(PREFLIGHT),
        "--mode", "bc_initialized_ppo_safety",
        "--forced-contact-result", str(s)
    ])
    assert proc.returncode != 0


def test_accuracy_bc_mode_accepts_all_gates(tmp_path):
    s = tmp_path / "safety.json"; _safety(s)
    t = tmp_path / "target.json"
    t.write_text(json.dumps({
        "status": "validated_target",
        "accuracy_rewards_unlocked": True,
        "mesh_sha256": "targetsha"
    }))
    b = tmp_path / "bc.json"
    b.write_text(json.dumps({
        "run_type": "behavior_cloning_training",
        "artifacts": {"torchscript": {"sha256": "bcsha"}}
    }))
    proc = subprocess.run([
        sys.executable, str(PREFLIGHT),
        "--mode", "bc_initialized_ppo_accuracy",
        "--forced-contact-result", str(s),
        "--validated-target-manifest", str(t),
        "--bc-run-manifest", str(b)
    ])
    assert proc.returncode == 0


def test_rl_mode_config_locks_geometric_rewards():
    text = (ROOT / "configs" / "rl_training_modes.yaml").read_text()
    assert "validated_target_required: false" in text
    assert "surface_progress: false" in text
    assert "validated_target_required: true" in text
    assert "surface_progress: true" in text
