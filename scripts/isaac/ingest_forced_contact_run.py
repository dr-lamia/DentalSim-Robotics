#!/usr/bin/env python3
"""Ingest and archive a real Isaac forced-contact result with provenance."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "scripts" / "isaac" / "verify_forced_contact_result.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--result-json", type=Path, required=True)
    p.add_argument("--operator-id", required=True)
    p.add_argument("--machine-label", required=True)
    p.add_argument("--isaac-version", required=True)
    p.add_argument("--repo-commit", required=True)
    p.add_argument("--asset-package", type=Path, required=True)
    p.add_argument("--command", required=True)
    p.add_argument("--out-dir", type=Path, default=ROOT / "results" / "isaac_runs")
    args = p.parse_args()

    proc = subprocess.run(
        [sys.executable, str(VERIFIER), str(args.result_json)],
        text=True,
        capture_output=True,
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        print("STATUS: RESULT REJECTED — verifier did not pass", file=sys.stderr)
        raise SystemExit(proc.returncode)

    raw = json.loads(args.result_json.read_text(encoding="utf-8"))
    run_id = datetime.now(timezone.utc).strftime("isaac_case15_%Y%m%dT%H%M%SZ")
    dest = args.out_dir / run_id
    dest.mkdir(parents=True, exist_ok=False)

    archived_result = dest / "forced_contact_result.json"
    shutil.copy2(args.result_json, archived_result)

    record = {
        "schema_version": 1,
        "run_type": "isaac_case15_forced_contact",
        "run_id": run_id,
        "operator_id": args.operator_id,
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "machine_label": args.machine_label,
        "isaac_version": args.isaac_version,
        "repo_commit": args.repo_commit,
        "asset_package_file": args.asset_package.name,
        "asset_package_sha256": sha256_file(args.asset_package),
        "command": args.command,
        "source_result_file": archived_result.name,
        "source_result_sha256": sha256_file(archived_result),
        "contact_detected": raw.get("contact_detected"),
        "contact_step": raw.get("contact_step"),
        "raw_contact_records": raw.get("raw_contact_records"),
        "safety_rollout_accepted": raw.get("safety_rollout_accepted"),
        "outcome": "pass",
        "verified_by": "scripts/isaac/verify_forced_contact_result.py",
    }

    record_path = dest / "run_manifest.json"
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    latest = args.out_dir / "latest_pass.json"
    latest.write_text(json.dumps({
        "run_id": run_id,
        "run_manifest": str(record_path.relative_to(ROOT)),
        "forced_contact_result": str(archived_result.relative_to(ROOT)),
        "result_sha256": record["source_result_sha256"],
    }, indent=2), encoding="utf-8")

    print(json.dumps(record, indent=2))
    print(f"STATUS: ISAAC RUN INGESTED -> {record_path}")
    print("NEXT:")
    print(
        "python scripts/status/check_readiness.py "
        f"--forced-contact-result {archived_result.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
