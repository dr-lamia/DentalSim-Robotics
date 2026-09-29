"""Formal expert gate for promotion of a dental preparation target mesh."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json

CRITERIA = (
    "correct_tooth_identity",
    "complete_visible_circumferential_boundary",
    "no_adjacent_tooth_contamination",
    "no_unacceptable_gingival_contamination",
    "axial_preparation_complete",
    "occlusal_preparation_complete",
    "suitable_for_geometric_target_scoring",
)

@dataclass(frozen=True)
class Review:
    reviewer_id: str
    reviewer_role: str
    review_date: str
    case_id: str
    fdi: int
    candidate_version: int
    mesh_sha256: str
    criteria: dict[str, str]
    overall_decision: str
    comments: str = ""

def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_review(path: str | Path) -> Review:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Review(
        reviewer_id=str(d["reviewer_id"]).strip(),
        reviewer_role=str(d["reviewer_role"]).strip(),
        review_date=str(d["review_date"]).strip(),
        case_id=str(d["case_id"]).strip(),
        fdi=int(d["fdi"]),
        candidate_version=int(d["candidate_version"]),
        mesh_sha256=str(d["mesh_sha256"]).strip().lower(),
        criteria=dict(d["criteria"]),
        overall_decision=str(d["overall_decision"]).strip(),
        comments=str(d.get("comments", "")),
    )

def validate_review(review: Review) -> list[str]:
    issues = []
    if not review.reviewer_id:
        issues.append("missing_reviewer_id")
    if review.overall_decision not in {"accept", "accept_after_edit", "reject"}:
        issues.append("invalid_overall_decision")
    for key in CRITERIA:
        if key not in review.criteria:
            issues.append(f"missing_criterion:{key}")
        elif review.criteria[key] not in {"pass", "fail"}:
            issues.append(f"invalid_criterion:{key}")
    return issues

def promotion_report(*, candidate_manifest: dict, mesh_path: str | Path, reviews: list[Review]) -> dict:
    issues = []
    actual_sha = sha256_file(mesh_path)
    expected_sha = str(candidate_manifest["sha256"]).lower()
    if actual_sha != expected_sha:
        issues.append("candidate_mesh_hash_mismatch")
    if len(reviews) < 2:
        issues.append("fewer_than_two_reviews")
    ids = [r.reviewer_id for r in reviews]
    if len(ids) != len(set(ids)):
        issues.append("reviewers_not_independent")
    for i, r in enumerate(reviews, start=1):
        for issue in validate_review(r):
            issues.append(f"review_{i}:{issue}")
        if r.case_id != candidate_manifest["case_id"]:
            issues.append(f"review_{i}:case_id_mismatch")
        if r.fdi != int(candidate_manifest["fdi"]):
            issues.append(f"review_{i}:fdi_mismatch")
        if r.candidate_version != int(candidate_manifest["candidate_version"]):
            issues.append(f"review_{i}:candidate_version_mismatch")
        if r.mesh_sha256 != expected_sha:
            issues.append(f"review_{i}:mesh_hash_mismatch")
        if r.overall_decision != "accept":
            issues.append(f"review_{i}:decision_not_accept")
        for key in CRITERIA:
            if r.criteria.get(key) != "pass":
                issues.append(f"review_{i}:criterion_failed:{key}")
    return {
        "promotable": not issues,
        "issues": issues,
        "case_id": candidate_manifest["case_id"],
        "fdi": int(candidate_manifest["fdi"]),
        "candidate_version": int(candidate_manifest["candidate_version"]),
        "mesh_sha256": expected_sha,
        "reviewer_ids": ids,
    }
