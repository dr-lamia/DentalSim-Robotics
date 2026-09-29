#!/usr/bin/env python3
"""Verify the output of the Isaac forced-contact negative test."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def verify(path: Path) -> dict:
    if not path.exists():
        return {"pass": False, "issues": ["missing_result_file"]}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"pass": False, "issues": [f"invalid_json:{type(exc).__name__}"]}

    issues = []
    if data.get("test") != "forced_protected_contact_negative_test":
        issues.append("unexpected_test_name")
    if data.get("contact_detected") is not True:
        issues.append("contact_not_detected")
    if data.get("pass") is not True:
        issues.append("negative_test_not_passed")
    if data.get("safety_rollout_accepted") is not False:
        issues.append("unsafe_rollout_not_explicitly_rejected")

    return {
        "pass": not issues,
        "issues": issues,
        "contact_step": data.get("contact_step"),
        "raw_contact_records": data.get("raw_contact_records"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("result_json", type=Path)
    args = p.parse_args()

    report = verify(args.result_json)
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
