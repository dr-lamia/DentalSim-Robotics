from pathlib import Path
import sys
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "validation"))

from render_target_inspection_views import render


def test_renderer_outputs_seven_views_and_sheet(tmp_path):
    mesh = trimesh.creation.box(extents=[1.0, 2.0, 3.0])
    mesh_path = tmp_path / "mesh.stl"
    mesh.export(mesh_path)
    out = tmp_path / "views"
    summary = render(mesh_path, out, dpi=80)

    assert len(summary["views"]) == 7
    assert (out / "candidate_multiview_sheet.png").exists()
    assert (out / "inspection_summary.json").exists()


def test_renderer_uses_orientation_neutral_labels(tmp_path):
    mesh = trimesh.creation.icosphere(subdivisions=1, radius=1.0)
    mesh_path = tmp_path / "mesh.stl"
    mesh.export(mesh_path)
    out = tmp_path / "views"
    summary = render(mesh_path, out, dpi=80)

    names = " ".join(summary["views"]).lower()
    assert "buccal" not in names
    assert "lingual" not in names
    assert "mesial" not in names
    assert "distal" not in names
