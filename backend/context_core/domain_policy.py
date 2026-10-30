"""Fail-closed content admission, independent of temporal omission grounding.

Only server-local, byte-bound operator reviews and pinned controlled fixtures
are trusted. Filenames, captions and client category declarations are not proof.
"""

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .media import digest

ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = ROOT / "data/domain-reviews"
MANIFEST = ROOT / "eval/execution-v1/manifest.json"
MANIFEST_SHA256 = "bb58b2c4be1e13c2219072f98ad03e3377ecb1a5ff48276b8bb5b30be5701159"
POLICY_VERSION = "context-domain-v1"
ALLOWED_CATEGORIES = frozenset(
    {"developer_tutorial", "software_benchmark", "product_demo"}
)
EXCLUSIONS = ("politics", "elections", "news", "wartime", "real_public_figures")


class ExclusionChecks(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    politics: bool | None = None
    elections: bool | None = None
    news: bool | None = None
    wartime: bool | None = None
    real_public_figures: bool | None = None


class DomainReview(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    policy_version: str = POLICY_VERSION
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    category: str
    exclusions: ExclusionChecks = Field(default_factory=ExclusionChecks)
    basis: Literal["operator_review", "frozen_fixture", "user_declaration"]
    reviewer: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=2000)
    reviewed_at: datetime


class DomainDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    policy_version: str = POLICY_VERSION
    sha256: str
    status: Literal["eligible", "excluded", "insufficient_evidence"]
    reason: str
    review: DomainReview | None = None


def evaluate_domain(sha256: str, review: DomainReview | None) -> DomainDecision:
    """Pure decision: explicit exclusions win, incomplete evidence never passes."""

    def decision(status, reason):
        return DomainDecision(
            sha256=sha256, status=status, reason=reason, review=review
        )

    if review is None or review.sha256 != sha256:
        return decision(
            "insufficient_evidence", "No review is bound to these media bytes."
        )
    if review.basis not in {"operator_review", "frozen_fixture"}:
        return decision(
            "insufficient_evidence", "A client declaration is not a content review."
        )
    if review.policy_version != POLICY_VERSION:
        return decision(
            "insufficient_evidence", "The review uses an unsupported policy version."
        )
    flags = review.exclusions.model_dump()
    excluded = [name for name, value in flags.items() if value is True]
    if excluded:
        return decision("excluded", "Excluded content: " + ", ".join(excluded) + ".")
    if review.category not in ALLOWED_CATEGORIES:
        return decision(
            "insufficient_evidence" if review.category == "unknown" else "excluded",
            "Content is not established as a tutorial, software benchmark or product demo.",
        )
    if any(value is not False for value in flags.values()):
        return decision(
            "insufficient_evidence", "All exclusion checks must be completed."
        )
    if (
        not review.reviewer.strip()
        or not review.rationale.strip()
        or review.reviewed_at.tzinfo is None
    ):
        return decision(
            "insufficient_evidence", "Review provenance is incomplete or invalid."
        )
    return decision(
        "eligible", "Byte-bound review admits this content under the domain policy."
    )


def review_for_hash(sha256: str) -> DomainReview | None:
    # An explicit local review (including a refusal) overrides fixture admission.
    path = REVIEW_ROOT / f"{sha256}.json"
    if path.exists():
        try:
            review = DomainReview.model_validate_json(path.read_text())
            return review if review.basis == "operator_review" else None
        except (OSError, ValidationError):
            return None
    try:
        if digest(MANIFEST) != MANIFEST_SHA256:
            return None
        manifest = json.loads(MANIFEST.read_text())
        hashes = {s["sha256"] for s in manifest["sources"].values()}
        hashes.update(case["sha256"] for case in manifest["cases"])
        if sha256 not in hashes:
            return None
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return DomainReview(
        sha256=sha256,
        category="software_benchmark",
        exclusions=ExclusionChecks(**dict.fromkeys(EXCLUSIONS, False)),
        basis="frozen_fixture",
        reviewer="CONTEXT execution-v1 controlled fixture provenance",
        rationale="Known authored JavaScript benchmark recording or frozen transformation; pinned manifest "
        + MANIFEST_SHA256,
        reviewed_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def decision_for_hash(sha256: str) -> DomainDecision:
    if not re.fullmatch(r"[a-f0-9]{64}", sha256):
        return DomainDecision(
            sha256=sha256,
            status="insufficient_evidence",
            reason="Invalid media fingerprint.",
        )
    return evaluate_domain(sha256, review_for_hash(sha256))


class DomainAdmissionError(Exception):
    def __init__(self, decisions: dict[str, DomainDecision]):
        self.decisions = decisions
        self.status_code = (
            403 if any(d.status == "excluded" for d in decisions.values()) else 422
        )
        reasons = [
            f"{name}: {d.reason}"
            for name, d in decisions.items()
            if d.status != "eligible"
        ]
        super().__init__(
            "Content admission blocked. "
            + " ".join(reasons)
            + " Review the exact files locally before retrying."
        )

    def report(self):
        return {
            name: decision.model_dump(mode="json")
            for name, decision in self.decisions.items()
        }


def require_hashes(hashes: dict[str, str]) -> dict:
    decisions = {name: decision_for_hash(value) for name, value in hashes.items()}
    if not decisions or any(d.status != "eligible" for d in decisions.values()):
        raise DomainAdmissionError(decisions)
    return {
        name: decision.model_dump(mode="json") for name, decision in decisions.items()
    }


def require_files(files: dict[str, Path]) -> dict:
    decisions = {}
    for name, path in files.items():
        try:
            decisions[name] = decision_for_hash(digest(path))
        except OSError:
            decisions[name] = DomainDecision(
                sha256="",
                status="insufficient_evidence",
                reason="Media bytes are unavailable; admission cannot be rechecked.",
            )
    if not decisions or any(d.status != "eligible" for d in decisions.values()):
        raise DomainAdmissionError(decisions)
    return {
        name: decision.model_dump(mode="json") for name, decision in decisions.items()
    }


def require_evidence_files(directory: Path, evidence: dict) -> dict:
    """Recheck current bytes and admission before returning cached or new review."""
    admission = require_files(
        {"source": directory / "original.mp4", "edited": directory / "edited.mp4"}
    )
    if any(admission[name]["sha256"] != evidence[name]["sha256"] for name in admission):
        raise ValueError(
            "Saved evidence fingerprints do not match the current media bytes; rerun analysis."
        )
    return admission
