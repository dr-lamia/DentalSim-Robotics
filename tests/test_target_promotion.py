from pathlib import Path
import json
import subprocess
import sys


def test_review_template_has_required_fields():
    root = Path(__file__).resolve().parents[1]
    obj = json.loads((root / "reviews" / "case25" / "review_template.json").read_text())
    assert "reviewer_id" in obj
    assert "mesh_sha256" in obj
    assert obj["decision"] == "accept"
    assert all(obj["criteria"].values())
