from pathlib import Path
import sys
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "validation"))

from inventory_preparation_stl import assess


def test_intake_hashes_and_describes_mesh(tmp_path):
    mesh = trimesh.creation.box(extents=[8.0, 7.0, 5.0])
    p = tmp_path / "prep.stl"
    mesh.export(p)

    report = assess(p, "source_01", True)
    assert report["source_id"] == "source_01"
    assert report["source_expert_supervised"] is True
    assert report["geometry"]["faces"] > 0
    assert len(report["sha256"]) == 64


def test_intake_does_not_auto_validate_target(tmp_path):
    mesh = trimesh.creation.box()
    p = tmp_path / "prep.stl"
    mesh.export(p)

    report = assess(p, "source_01", True)
    assert report["status"] == "geometry_described_review_scope_required"
    assert "validated" not in report["status"]
