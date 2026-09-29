from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.target_gate import geometric_rewards_enabled, load_validated_target_manifest


def test_no_manifest_disables_geometric_rewards():
    assert geometric_rewards_enabled(None) is False


def test_two_reviewer_manifest_enables(tmp_path):
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps({
        "status": "validated_target",
        "target_file": "target.stl",
        "sha256": "abc",
        "reviewers": ["r1", "r2"],
        "review_count": 2
    }))
    assert geometric_rewards_enabled(p) is True


def test_duplicate_reviewers_do_not_enable(tmp_path):
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps({
        "status": "validated_target",
        "target_file": "target.stl",
        "sha256": "abc",
        "reviewers": ["r1", "r1"],
        "review_count": 2
    }))
    assert geometric_rewards_enabled(p) is False
