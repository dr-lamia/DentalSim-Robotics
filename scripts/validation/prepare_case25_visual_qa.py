#!/usr/bin/env python3
"""Create a blank visual confirmation form for Case 25."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "review_templates" / "case25_technical_geometry_qa_reduced.json"

VISUAL = [
    "correct_tooth_identity",
    "complete_prepared_surface",
    "axial_surfaces_complete",
    "occlusal_surface_complete",
    "no_adjacent_tooth_contamination",
    "no_unacceptable_gingival_contamination",
    "suitable_as_reference_geometry",
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--operator-id", required=True)
    p.add_argument("--review-date", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    d = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    d["operator_id"] = args.operator_id.strip()
    d["review_date"] = args.review_date.strip()
    for key in VISUAL:
        d["criteria"][key] = "REVIEW_REQUIRED"
    d["overall_decision"] = "REVIEW_REQUIRED"
    d["comments"] = ""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(d, indent=2), encoding="utf-8")
    print(args.out)

if __name__ == "__main__":
    main()
