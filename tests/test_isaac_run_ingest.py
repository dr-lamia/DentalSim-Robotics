from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "isaac" / "verify_forced_contact_result.py"


def test_real_run_schema_exists():
    p = ROOT / "configs" / "isaac_run_manifest_schema.yaml"
    assert p.exists()
    text = p.read_text()
    assert "asset_package_sha256" in text
    assert "repo_commit" in text
    assert "pass_requires" in text


def test_verifier_rejects_result_without_explicit_rejection(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({
        "test": "forced_protected_contact_negative_test",
        "contact_detected": True,
        "pass": True,
        "safety_rollout_accepted": None,
    }))
    proc = subprocess.run([sys.executable, str(VERIFY), str(p)])
    assert proc.returncode != 0


def test_ingest_script_references_verifier():
    text = (ROOT / "scripts" / "isaac" / "ingest_forced_contact_run.py").read_text()
    assert "verify_forced_contact_result.py" in text
    assert "RESULT REJECTED" in text
    assert "sha256_file" in text
