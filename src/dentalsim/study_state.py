"""Study execution state machine for DentalSim-Robotics."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

from .target_gate import target_accuracy_rewards_enabled


@dataclass(frozen=True)
class StudyState:
    state: str
    safety_verified: bool
    target_validated: bool
    expert_teleop_available: bool
    bc_run_available: bool
    rl_safety_ready: bool
    rl_accuracy_ready: bool
    evidence: dict
    blockers: list[str]

    def to_dict(self):
        return asdict(self)


def _load(path: str | Path | None):
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def evaluate_study_state(
    *,
    forced_contact_result: str | Path | None = None,
    validated_target_manifest: str | Path | None = None,
    teleop_session_manifest: str | Path | None = None,
    bc_run_manifest: str | Path | None = None,
) -> StudyState:
    safety = _load(forced_contact_result) or {}
    safety_verified = bool(
        safety.get("pass") is True
        and safety.get("contact_detected") is True
        and safety.get("safety_rollout_accepted") is False
    )

    target_validated = target_accuracy_rewards_enabled(validated_target_manifest)

    teleop = _load(teleop_session_manifest) or {}
    expert_teleop_available = bool(
        teleop.get("session_type") == "dentist_teleoperation"
        and teleop.get("human_expert_demonstration") is True
        and teleop.get("validation_pass") is True
        and int(teleop.get("episode_count") or 0) >= 1
    )

    bc = _load(bc_run_manifest) or {}
    bc_run_available = bool(
        bc.get("run_type") == "behavior_cloning_training"
        and bc.get("artifacts", {}).get("torchscript", {}).get("sha256")
    )

    rl_safety_ready = safety_verified
    rl_accuracy_ready = safety_verified and target_validated

    if rl_accuracy_ready and bc_run_available:
        state = "HYBRID_ACCURACY_READY"
    elif rl_accuracy_ready:
        state = "ACCURACY_RL_READY"
    elif bc_run_available and safety_verified:
        state = "HYBRID_SAFETY_READY"
    elif expert_teleop_available and safety_verified:
        state = "BC_TRAINING_READY"
    elif safety_verified:
        state = "SAFETY_VALIDATED"
    else:
        state = "ENGINEERING_ONLY"

    blockers = []
    if not safety_verified:
        blockers.append("Run and ingest a passing Isaac forced-contact negative test.")
    if not expert_teleop_available:
        blockers.append("Record and ingest a validated human dentist teleoperation session.")
    if not bc_run_available:
        blockers.append("Train, evaluate, and archive a BC model from expert teleoperation data.")
    if not target_validated:
        blockers.append("Complete two-expert Case-25 target approval and promotion.")

    evidence = {
        "forced_contact_result": str(forced_contact_result) if forced_contact_result else None,
        "validated_target_manifest": str(validated_target_manifest) if validated_target_manifest else None,
        "teleop_session_manifest": str(teleop_session_manifest) if teleop_session_manifest else None,
        "bc_run_manifest": str(bc_run_manifest) if bc_run_manifest else None,
    }

    return StudyState(
        state=state,
        safety_verified=safety_verified,
        target_validated=target_validated,
        expert_teleop_available=expert_teleop_available,
        bc_run_available=bc_run_available,
        rl_safety_ready=rl_safety_ready,
        rl_accuracy_ready=rl_accuracy_ready,
        evidence=evidence,
        blockers=blockers,
    )
