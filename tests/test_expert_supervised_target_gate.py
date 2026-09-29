from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.target_gate import geometric_rewards_enabled, target_accuracy_rewards_enabled


def test_expert_supervised_technical_qa_route_enables_target(tmp_path):
    p = tmp_path / "target.json"
    p.write_text(json.dumps({
        "status": "validated_target",
        "mesh_file": "target.stl",
        "mesh_sha256": "abc",
        "source_expert_supervised": True,
        "technical_geometry_qa_pass": True,
        "accuracy_rewards_unlocked": True
    }))
    assert geometric_rewards_enabled(p)
    assert target_accuracy_rewards_enabled(p)


def test_expert_supervision_without_technical_qa_does_not_enable(tmp_path):
    p = tmp_path / "target.json"
    p.write_text(json.dumps({
        "status": "validated_target",
        "mesh_file": "target.stl",
        "mesh_sha256": "abc",
        "source_expert_supervised": True,
        "technical_geometry_qa_pass": False,
        "accuracy_rewards_unlocked": True
    }))
    assert not target_accuracy_rewards_enabled(p)
