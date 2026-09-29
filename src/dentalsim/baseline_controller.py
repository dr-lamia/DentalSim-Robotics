"""Deterministic Phase-1 baseline: approach, trace finish-line ring, retreat.

This is intentionally not an autonomous dental-preparation policy. It is a
safe engineering baseline used to validate coordinate frames, motion limits,
recording, collision logic and task success plumbing before RL is enabled.
"""
from __future__ import annotations

from math import cos, pi, sin

from .scene_contract import Pose6D


def finish_line_ring(
    center_mm=(0.0, 0.0, -2.0),
    radius_x_mm: float = 4.0,
    radius_y_mm: float = 3.2,
    points: int = 72,
    approach_height_mm: float = 5.0,
    retreat_height_mm: float = 6.0,
) -> list[Pose6D]:
    if points < 8:
        raise ValueError("Use at least 8 ring points")
    cx, cy, cz = map(float, center_mm)
    out = [Pose6D(cx + radius_x_mm, cy, cz + approach_height_mm)]
    for i in range(points + 1):
        theta = 2.0 * pi * i / points
        out.append(
            Pose6D(
                cx + radius_x_mm * cos(theta),
                cy + radius_y_mm * sin(theta),
                cz,
                rz_deg=(theta * 180.0 / pi) + 90.0,
            )
        )
    out.append(Pose6D(cx + radius_x_mm, cy, cz + retreat_height_mm))
    return out
