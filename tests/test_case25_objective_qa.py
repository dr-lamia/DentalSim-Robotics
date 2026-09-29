from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_case25_objective_evidence_is_hash_locked():
    evidence = json.loads((ROOT / "results" / "case25_objective_technical_geometry_evidence.json").read_text())
    candidate = json.loads((ROOT / "configs" / "case25_target_candidate_v2_manifest.json").read_text())
    assert evidence["candidate_sha256"] == candidate["sha256"]
    assert evidence["objective_checks"]["mesh_hash_matches_locked_candidate"] == "pass"


def test_case25_scale_and_orientation_are_objectively_supported():
    evidence = json.loads((ROOT / "results" / "case25_objective_technical_geometry_evidence.json").read_text())
    assert evidence["source_coordinate_consistency"]["nearest_source_jaw_vertex_max_mm"] == 0.0
    assert evidence["objective_checks"]["scale_preserved_from_source_scan"] == "pass"
    assert evidence["objective_checks"]["orientation_preserved_from_source_scan"] == "pass"


def test_reduced_qa_template_does_not_prefill_visual_acceptance():
    qa = json.loads((ROOT / "review_templates" / "case25_technical_geometry_qa_reduced.json").read_text())
    assert qa["criteria"]["scale_verified"] == "pass"
    assert qa["criteria"]["orientation_verified"] == "pass"
    assert qa["criteria"]["complete_prepared_surface"] == "REVIEW_REQUIRED"
    assert qa["overall_decision"] == "REVIEW_REQUIRED"
