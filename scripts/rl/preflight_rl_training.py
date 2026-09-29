#!/usr/bin/env python3
"""Preflight PPO / BC→PPO training with explicit scientific gates."""
from __future__ import annotations
import argparse, json
from pathlib import Path


ACCURACY_MODES = {"ppo_random_accuracy", "bc_initialized_ppo_accuracy"}
BC_MODES = {"bc_initialized_ppo_safety", "bc_initialized_ppo_accuracy"}


def load(path: Path | None):
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=[
        "ppo_random_safety",
        "ppo_random_accuracy",
        "bc_initialized_ppo_safety",
        "bc_initialized_ppo_accuracy",
    ])
    p.add_argument("--forced-contact-result", type=Path, required=True)
    p.add_argument("--validated-target-manifest", type=Path)
    p.add_argument("--bc-run-manifest", type=Path)
    args = p.parse_args()

    issues = []

    safety = load(args.forced_contact_result) or {}
    if safety.get("pass") is not True:
        issues.append("forced_contact_test_not_passed")
    if safety.get("contact_detected") is not True:
        issues.append("protected_contact_not_verified")
    if safety.get("safety_rollout_accepted") is not False:
        issues.append("unsafe_rollout_rejection_not_verified")

    target = load(args.validated_target_manifest) if args.validated_target_manifest else None
    target_valid = bool(
        target
        and target.get("status") == "validated_target"
        and target.get("accuracy_rewards_unlocked") is True
        and (target.get("mesh_sha256") or target.get("sha256"))
    )

    bc = load(args.bc_run_manifest) if args.bc_run_manifest else None
    bc_valid = bool(
        bc
        and bc.get("run_type") == "behavior_cloning_training"
        and bc.get("artifacts", {}).get("torchscript", {}).get("sha256")
    )

    if args.mode in ACCURACY_MODES and not target_valid:
        issues.append("validated_target_required_for_accuracy_mode")

    if args.mode in BC_MODES and not bc_valid:
        issues.append("validated_bc_run_required_for_bc_initialization")

    report = {
        "ready": not issues,
        "mode": args.mode,
        "forced_contact_verified": not any(x.startswith("forced_contact") or x.startswith("protected_contact") or x.startswith("unsafe_rollout") for x in issues),
        "validated_target_available": target_valid,
        "bc_initialization_available": bc_valid,
        "geometric_rewards_allowed": args.mode in ACCURACY_MODES and target_valid,
        "issues": issues,
    }
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
