from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "teleop" / "preflight_expert_session.py"


def test_expert_session_schema_exists():
    p = ROOT / "configs" / "expert_teleop_session_schema.yaml"
    assert p.exists()
    t = p.read_text()
    assert "scripted_or_mock_must_not_be_labelled_expert" in t
    assert "success_requires_zero_protected_contacts" in t


def test_preflight_rejects_unverified_safety(tmp_path):
    r = tmp_path / "bad.json"
    r.write_text(json.dumps({
        "pass": False,
        "contact_detected": False,
        "safety_rollout_accepted": None
    }))
    proc = subprocess.run([
        sys.executable, str(PREFLIGHT),
        "--operator-id", "expert_a",
        "--operator-role", "prosthodontist",
        "--scene-id", "case15_engineering_validation",
        "--tooth-id", "15",
        "--forced-contact-result", str(r)
    ])
    assert proc.returncode != 0


def test_preflight_accepts_verified_safety(tmp_path):
    r = tmp_path / "ok.json"
    r.write_text(json.dumps({
        "pass": True,
        "contact_detected": True,
        "safety_rollout_accepted": False
    }))
    proc = subprocess.run([
        sys.executable, str(PREFLIGHT),
        "--operator-id", "expert_a",
        "--operator-role", "prosthodontist",
        "--scene-id", "case15_engineering_validation",
        "--tooth-id", "15",
        "--forced-contact-result", str(r)
    ])
    assert proc.returncode == 0
