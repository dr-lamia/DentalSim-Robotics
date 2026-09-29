"""Metric and reward utilities for DentalSim-Robotics.

These functions deliberately separate clinically interpretable metrics from
simulator-specific code so the same validation logic can be used for teleop,
AI-assisted, and autonomous rollouts.
"""
from dataclasses import dataclass


@dataclass
class PrepMetrics:
    mean_surface_deviation_mm: float
    p95_surface_deviation_mm: float
    finish_line_mean_deviation_mm: float
    taper_error_deg: float
    over_reduction_mm: float
    adjacent_collision_count: int
    pulp_min_distance_mm: float
    smoothness_score: float = 1.0
    undercut_count: int = 0


@dataclass
class ScoreConfig:
    w_surface: float = 4.0
    w_margin: float = 2.0
    w_taper: float = 1.5
    w_over_reduction: float = 4.0
    w_collision: float = 10.0
    w_pulp: float = 10.0
    w_undercut: float = 3.0
    w_smoothness: float = 0.5
    safe_pulp_distance_mm: float = 0.5


def safety_pass(m: PrepMetrics, cfg: ScoreConfig = ScoreConfig()) -> bool:
    return (
        m.adjacent_collision_count == 0
        and m.pulp_min_distance_mm >= cfg.safe_pulp_distance_mm
    )


def reward(m: PrepMetrics, cfg: ScoreConfig = ScoreConfig()) -> float:
    pulp_violation = max(0.0, cfg.safe_pulp_distance_mm - m.pulp_min_distance_mm)
    return (
        -cfg.w_surface * m.mean_surface_deviation_mm
        -cfg.w_margin * m.finish_line_mean_deviation_mm
        -cfg.w_taper * abs(m.taper_error_deg)
        -cfg.w_over_reduction * max(0.0, m.over_reduction_mm)
        -cfg.w_collision * m.adjacent_collision_count
        -cfg.w_pulp * pulp_violation
        -cfg.w_undercut * m.undercut_count
        +cfg.w_smoothness * m.smoothness_score
    )


def task_success(m: PrepMetrics) -> bool:
    return (
        safety_pass(m)
        and m.mean_surface_deviation_mm <= 0.30
        and m.p95_surface_deviation_mm <= 0.60
        and m.finish_line_mean_deviation_mm <= 0.40
        and abs(m.taper_error_deg) <= 5.0
    )
