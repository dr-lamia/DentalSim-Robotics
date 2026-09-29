from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_standardized_visual_renderer_exists_and_uses_axis_labels():
    p = ROOT / "scripts" / "validation" / "render_target_inspection_views.py"
    text = p.read_text()
    assert "01_plus_Z" in text
    assert "03_plus_X" in text
    assert "07_perspective" in text
    assert "buccal" not in text.lower()
