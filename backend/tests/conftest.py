import pytest
from context_core.fixtures import generate


@pytest.fixture(scope="session")
def clips(tmp_path_factory):
    return generate(tmp_path_factory.mktemp("media"))


@pytest.fixture
def reviewed_clips(clips, tmp_path, monkeypatch):
    """Simulated operator receipts for API contract fixtures, not content validation."""
    from datetime import UTC, datetime

    from context_core import domain_policy
    from context_core.domain_policy import DomainReview, ExclusionChecks
    from context_core.media import digest

    reviews = tmp_path / "test-domain-reviews"
    reviews.mkdir()
    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", reviews)

    def review_file(path):
        sha256 = digest(path)
        receipt = DomainReview(
            sha256=sha256,
            category="developer_tutorial",
            exclusions=ExclusionChecks(
                **dict.fromkeys(domain_policy.EXCLUSIONS, False)
            ),
            basis="operator_review",
            reviewer="Simulated reviewer for automated API contract tests",
            rationale="Synthetic test fixture; this receipt tests policy plumbing, not actual domain classification.",
            reviewed_at=datetime.now(UTC),
        )
        (reviews / f"{sha256}.json").write_text(receipt.model_dump_json())
        return receipt

    for path in clips.glob("*.mp4"):
        review_file(path)
    return review_file
