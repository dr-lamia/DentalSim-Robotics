"""Hard action and rollout safety layer for DentalSim-Robotics policies."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


MAX_TRANSLATION_M = 0.00025
MAX_ROTATION_RAD = np.deg2rad(2.0)


@dataclass(frozen=True)
class SafetyDecision:
    action: np.ndarray
    clipped: bool
    emergency_stop: bool
    reason: str | None


def enforce_action(action_6, *, protected_contact: bool = False) -> SafetyDecision:
    a = np.asarray(action_6, dtype=np.float32).copy()
    if a.shape != (6,):
        raise ValueError(f"Expected 6D action, got {a.shape}")

    if protected_contact:
        return SafetyDecision(
            action=np.zeros(6, dtype=np.float32),
            clipped=False,
            emergency_stop=True,
            reason="protected_contact",
        )

    original = a.copy()
    a[:3] = np.clip(a[:3], -MAX_TRANSLATION_M, MAX_TRANSLATION_M)
    a[3:] = np.clip(a[3:], -MAX_ROTATION_RAD, MAX_ROTATION_RAD)
    clipped = not np.allclose(a, original)

    return SafetyDecision(
        action=a,
        clipped=clipped,
        emergency_stop=False,
        reason="action_clipped" if clipped else None,
    )
