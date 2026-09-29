from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def _parse(rel):
    path = ROOT / rel
    assert path.exists()
    ast.parse(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def test_isaac_scripts_parse():
    _parse("scripts/isaac/convert_case15_assets_to_usd.py")
    _parse("scripts/isaac/build_case15_stage.py")
    _parse("scripts/isaac/run_forced_contact_test.py")


def test_stage_has_explicit_mm_to_m_scale():
    text = _parse("scripts/isaac/build_case15_stage.py")
    assert "MM_TO_M = 0.001" in text
    assert "SetStageMetersPerUnit(stage, 1.0)" in text


def test_candidate_is_not_ground_truth():
    text = _parse("scripts/isaac/build_case15_stage.py")
    assert '"PreparedCandidate": ("prepared_candidate.usd", False, False)' in text
    assert "scientificGroundTruth" in text


def test_forced_contact_must_detect_contact_to_pass():
    text = _parse("scripts/isaac/run_forced_contact_test.py")
    assert '"pass": bool(detected)' in text
    assert "if not detected:" in text
