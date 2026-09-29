"""Project-level readiness gates for DentalSim-Robotics."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

from .target_gate import geometric_rewards_enabled, target_accuracy_rewards_enabled


@dataclass(frozen=True)
class Readiness:
    simulator_independent_ci: bool
    case_assets_present: bool
    isaac_stage_authored: bool
    forced_contact_verified: bool
    teleop_dataset_available: bool
    bc_policy_available: bool
    validated_target_available: bool
    geometric_rewards_enabled: bool
    preparation_rl_allowed: bool
    manuscript_accuracy_outcomes_allowed: bool

    def to_dict(self):
        return asdict(self)


def evaluate_readiness(
    *,
    repo_root: str | Path,
    validated_target_manifest: str | Path | None = None,
    forced_contact_result: str | Path | None = None,
    teleop_hdf5: str | Path | None = None,
    bc_policy: str | Path | None = None,
) -> Readiness:
    root = Path(repo_root)

    # CI readiness is represented locally by the existence of the workflow and
    # test suite; the GitHub service remains the source of truth for run status.
    ci = (root / ".github/workflows/python-contract-tests.yml").exists() and (root / "tests").exists()

    case_assets = (root / "configs/case25_target_candidate_v2_manifest.json").exists()
    isaac_stage = (root / "scripts/isaac/build_case15_stage.py").exists()

    forced_ok = False
    if forced_contact_result:
        p = Path(forced_contact_result)
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                forced_ok = bool(d.get("pass")) and bool(d.get("contact_detected"))
            except Exception:
                forced_ok = False

    teleop_ok = bool(teleop_hdf5 and Path(teleop_hdf5).exists())
    bc_ok = bool(bc_policy and Path(bc_policy).exists())

    validated = target_accuracy_rewards_enabled(validated_target_manifest)
    geometric = geometric_rewards_enabled(validated_target_manifest) or validated

    return Readiness(
        simulator_independent_ci=ci,
        case_assets_present=case_assets,
        isaac_stage_authored=isaac_stage,
        forced_contact_verified=forced_ok,
        teleop_dataset_available=teleop_ok,
        bc_policy_available=bc_ok,
        validated_target_available=validated,
        geometric_rewards_enabled=geometric,
        preparation_rl_allowed=validated and forced_ok,
        manuscript_accuracy_outcomes_allowed=validated and forced_ok,
    )
