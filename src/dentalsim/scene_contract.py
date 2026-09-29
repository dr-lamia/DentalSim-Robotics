"""Simulator-independent scene contract for Phase-1 crown preparation.

All public values use millimetres/degrees because that is clinically readable.
The Isaac adapter converts geometry to SI units at the API boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Iterable, Sequence


Vec3 = tuple[float, float, float]


def mm_to_m(value_mm: float) -> float:
    return value_mm / 1000.0


def vec_mm_to_m(v: Sequence[float]) -> Vec3:
    if len(v) != 3:
        raise ValueError("Expected a 3-vector")
    return tuple(mm_to_m(float(x)) for x in v)  # type: ignore[return-value]


def euclidean_mm(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Expected two 3-vectors")
    return sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


@dataclass(frozen=True)
class Pose6D:
    x_mm: float
    y_mm: float
    z_mm: float
    rx_deg: float = 0.0
    ry_deg: float = 0.0
    rz_deg: float = 0.0

    @property
    def position_mm(self) -> Vec3:
        return (self.x_mm, self.y_mm, self.z_mm)

    @property
    def position_m(self) -> Vec3:
        return vec_mm_to_m(self.position_mm)


@dataclass(frozen=True)
class SafetyEnvelope:
    adjacent_clearance_mm: float = 0.30
    pulp_clearance_mm: float = 0.50
    max_translation_mm_per_step: float = 0.25
    max_rotation_deg_per_step: float = 2.0
    emergency_stop_on_protected_contact: bool = True

    def validate(self) -> None:
        if self.adjacent_clearance_mm < 0:
            raise ValueError("Adjacent clearance cannot be negative")
        if self.pulp_clearance_mm <= 0:
            raise ValueError("Pulp clearance must be positive")
        if self.max_translation_mm_per_step <= 0:
            raise ValueError("Translation step must be positive")
        if self.max_rotation_deg_per_step <= 0:
            raise ValueError("Rotation step must be positive")


@dataclass
class SafetyState:
    adjacent_min_distance_mm: float
    pulp_min_distance_mm: float
    protected_contact: bool = False
    over_reduction_mm: float = 0.0
    reasons: list[str] = field(default_factory=list)

    def allowed(self, envelope: SafetyEnvelope) -> bool:
        self.reasons.clear()
        if self.protected_contact:
            self.reasons.append("protected_anatomy_contact")
        if self.adjacent_min_distance_mm < envelope.adjacent_clearance_mm:
            self.reasons.append("adjacent_clearance_violation")
        if self.pulp_min_distance_mm < envelope.pulp_clearance_mm:
            self.reasons.append("pulp_clearance_violation")
        return not self.reasons


def bounded_delta(current: Pose6D, requested: Pose6D, envelope: SafetyEnvelope) -> Pose6D:
    """Clamp a requested relative 6-DOF action to the Phase-1 safety limits."""
    envelope.validate()

    def clamp(v: float, limit: float) -> float:
        return max(-limit, min(limit, v))

    return Pose6D(
        current.x_mm + clamp(requested.x_mm, envelope.max_translation_mm_per_step),
        current.y_mm + clamp(requested.y_mm, envelope.max_translation_mm_per_step),
        current.z_mm + clamp(requested.z_mm, envelope.max_translation_mm_per_step),
        current.rx_deg + clamp(requested.rx_deg, envelope.max_rotation_deg_per_step),
        current.ry_deg + clamp(requested.ry_deg, envelope.max_rotation_deg_per_step),
        current.rz_deg + clamp(requested.rz_deg, envelope.max_rotation_deg_per_step),
    )


def path_length_mm(points: Iterable[Pose6D]) -> float:
    pts = list(points)
    return sum(euclidean_mm(a.position_mm, b.position_mm) for a, b in zip(pts, pts[1:]))
