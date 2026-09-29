#!/usr/bin/env python3
"""Validate and archive a real dentist teleoperation dataset with provenance."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "teleop" / "validate_teleop_hdf5.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hdf5", type=Path, required=True)
    p.add_argument("--operator-id", required=True)
    p.add_argument("--operator-role", choices=["dentist", "prosthodontist"], required=True)
    p.add_argument("--machine-label", required=True)
    p.add_argument("--isaac-version", required=True)
    p.add_argument("--repo-commit", required=True)
    p.add_argument("--scene-id", required=True)
    p.add_argument("--tooth-id", required=True)
    p.add_argument("--out-dir", type=Path, default=ROOT / "results" / "teleop_sessions")
    args = p.parse_args()

    if not args.hdf5.exists():
        raise SystemExit(f"Missing HDF5: {args.hdf5}")

    validation_json = args.hdf5.with_suffix(".validation.json")
    proc = subprocess.run([
        sys.executable, str(VALIDATOR), str(args.hdf5),
        "--json-out", str(validation_json)
    ], text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        print("STATUS: TELEOP DATASET REJECTED", file=sys.stderr)
        raise SystemExit(proc.returncode)

    report = json.loads(validation_json.read_text(encoding="utf-8"))
    if report.get("episode_count", 0) < 1:
        raise SystemExit("No episodes found")

    session_id = datetime.now(timezone.utc).strftime("teleop_%Y%m%dT%H%M%SZ")
    dest = args.out_dir / session_id
    dest.mkdir(parents=True, exist_ok=False)

    h5_dest = dest / "expert_teleop.hdf5"
    report_dest = dest / "validation_report.json"
    shutil.copy2(args.hdf5, h5_dest)
    shutil.copy2(validation_json, report_dest)

    manifest = {
        "schema_version": 1,
        "session_type": "dentist_teleoperation",
        "session_id": session_id,
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "operator_id": args.operator_id,
        "operator_role": args.operator_role,
        "machine_label": args.machine_label,
        "isaac_version": args.isaac_version,
        "repo_commit": args.repo_commit,
        "scene_id": args.scene_id,
        "tooth_id": args.tooth_id,
        "input_mode": "teleop",
        "human_expert_demonstration": True,
        "hdf5_file": h5_dest.name,
        "hdf5_sha256": sha256_file(h5_dest),
        "validation_report": report_dest.name,
        "validation_report_sha256": sha256_file(report_dest),
        "episode_count": report.get("episode_count"),
        "validation_pass": report.get("pass") is True,
        "expert_label_rule": "Scripted/mock trajectories must never use human_expert_demonstration=true."
    }

    (dest / "session_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    latest = args.out_dir / "latest_valid_expert_teleop.json"
    latest.write_text(json.dumps({
        "session_id": session_id,
        "session_manifest": str((dest / "session_manifest.json").relative_to(ROOT)),
        "hdf5": str(h5_dest.relative_to(ROOT)),
        "hdf5_sha256": manifest["hdf5_sha256"]
    }, indent=2), encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    print("STATUS: EXPERT TELEOP INGESTED")
    print(
        "NEXT: python scripts/status/check_readiness.py "
        f"--teleop-hdf5 {h5_dest.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
