#!/usr/bin/env python3
"""Create a reviewer-specific copy of the Case-25 review template."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "review_templates" / "case25_target_review_template.json"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reviewer-id", required=True)
    p.add_argument("--review-date", required=True)
    p.add_argument("--role", default="prosthodontist")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    data["reviewer_id"] = args.reviewer_id.strip()
    data["reviewer_role"] = args.role.strip()
    data["review_date"] = args.review_date.strip()

    # Clear default judgments so the generated file cannot accidentally look
    # like a completed acceptance before the reviewer has assessed the mesh.
    data["criteria"] = {k: "REVIEW_REQUIRED" for k in data["criteria"]}
    data["overall_decision"] = "REVIEW_REQUIRED"
    data["comments"] = ""

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
