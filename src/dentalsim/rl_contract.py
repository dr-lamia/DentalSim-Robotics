"""Reward/safety contract for DentalSim-Robotics RL.

Simulator-independent by design so it can be unit-tested without Isaac.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RLStepState:
    progress_mm: float = 0.0
    mean_surface_error_mm: float | None = None
    finish_line_error_mm: float | None = None
    taper_error_deg: float | None = None
    smoothness: float = 1.0
    action_jerk: float = 0.0
    protected_contact: bool = False
    adjacent_clearance_violation: bool = False
    catastrophic_over_reduction: bool = False


@dataclass(frozen=True)
class RLRewardConfig:
    w_progress: float = 4.0
    w_surface: float = 2.0
    w_margin: float = 2.0
    w_taper: float = 1.5
    w_smooth: float = 0.5
    w_jerk: float = 0.2
    p_contact: float = 10.0
    p_clearance: float = 5.0
    p_catastrophic_over_reduction: float = 10.0


def compute_reward(
    state: RLStepState,
    *,
    validated_target_available: bool,
    cfg: RLRewardConfig = RLRewardConfig(),
) -> float:
    r = 0.0

    if validated_target_available:
        r += cfg.w_progress * state.progress_mm
        if state.mean_surface_error_mm is not None:
            r -= cfg.w_surface * state.mean_surface_error_mm
        if state.finish_line_error_mm is not None:
            r -= cfg.w_margin * state.finish_line_error_mm
        if state.taper_error_deg is not None:
            r -= cfg.w_taper * abs(state.taper_error_deg)
        if state.catastrophic_over_reduction:
            r -= cfg.p_catastrophic_over_reduction

    r += cfg.w_smooth * state.smoothness
    r -= cfg.w_jerk * abs(state.action_jerk)

    if state.protected_contact:
        r -= cfg.p_contact
    if state.adjacent_clearance_violation:
        r -= cfg.p_clearance

    return float(r)


def termination_reason(
    state: RLStepState,
    *,
    step: int,
    max_steps: int,
    action_limit_violation: bool = False,
) -> str | None:
    if state.protected_contact:
        return "protected_contact"
    if action_limit_violation:
        return "action_limit_violation"
    if step >= max_steps:
        return "max_steps"
    return None
