from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_batch_intake_contains_seven_library_sources():
    d = json.loads((ROOT / "results" / "preparation_library_batch_intake.json").read_text())
    assert len(d["sources"]) == 7


def test_batch_intake_has_hashes_and_no_auto_validation():
    d = json.loads((ROOT / "results" / "preparation_library_batch_intake.json").read_text())
    for s in d["sources"]:
        assert len(s["sha256"]) == 64
        assert s["status"] == "geometry_described_review_scope_required"
