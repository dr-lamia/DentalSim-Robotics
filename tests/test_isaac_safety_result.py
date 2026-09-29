from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "isaac"))

from verify_forced_contact_result import verify


def test_forced_contact_verifier_accepts_expected_negative_test(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps({
        "test": "forced_protected_contact_negative_test",
        "contact_detected": True,
        "contact_step": 42,
        "raw_contact_records": 3,
        "safety_rollout_accepted": False,
        "pass": True,
    }))
    r = verify(p)
    assert r["pass"]


def test_forced_contact_verifier_rejects_no_contact(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps({
        "test": "forced_protected_contact_negative_test",
        "contact_detected": False,
        "safety_rollout_accepted": None,
        "pass": False,
    }))
    r = verify(p)
    assert not r["pass"]
    assert "contact_not_detected" in r["issues"]


def test_smoke_shell_script_does_not_run_in_ci():
    text = (ROOT / "scripts" / "isaac" / "run_case15_safety_smoke.sh").read_text()
    assert "ISAAC_PYTHON" in text
    assert "verify_forced_contact_result.py" in text
    assert "forced_contact_result.json" in text
