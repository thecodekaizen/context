"""Admission checks guard work boundaries, not a claimed content classifier."""

import asyncio
import json
from datetime import UTC, datetime

import pytest
from context_core import api, domain_policy
from context_core.domain_policy import (
    ALLOWED_CATEGORIES,
    EXCLUSIONS,
    DomainAdmissionError,
    DomainReview,
    ExclusionChecks,
    decision_for_hash,
    evaluate_domain,
    require_files,
)
from context_core.media import digest
from fastapi.testclient import TestClient

SHA = "a" * 64


def review(**changes):
    return DomainReview(
        **{
            "sha256": SHA,
            "category": "software_benchmark",
            "exclusions": ExclusionChecks(**dict.fromkeys(EXCLUSIONS, False)),
            "basis": "operator_review",
            "reviewer": "Test operator",
            "rationale": "Full-file test review, including audio and margins",
            "reviewed_at": datetime(2026, 10, 29, tzinfo=UTC),
            **changes,
        }
    )


@pytest.fixture
def isolated_domain(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DATA", tmp_path / "jobs")
    api.DATA.mkdir()
    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", tmp_path / "reviews")
    return TestClient(api.app)


@pytest.mark.parametrize("category", sorted(ALLOWED_CATEGORIES))
def test_allowed_categories_need_full_review(category):
    decision = evaluate_domain(SHA, review(category=category))
    assert decision.status == "eligible"
    assert decision.review.reviewer == "Test operator"


@pytest.mark.parametrize("exclusion", EXCLUSIONS)
def test_exclusions_override_allowed_category(exclusion):
    checks = dict.fromkeys(EXCLUSIONS, False)
    checks[exclusion] = True
    result = evaluate_domain(SHA, review(exclusions=ExclusionChecks(**checks)))
    assert result.status == "excluded"
    assert exclusion in result.reason


@pytest.mark.parametrize(
    "receipt",
    [
        None,
        review(sha256="b" * 64),
        review(basis="user_declaration"),
        review(category="unknown"),
        review(exclusions=ExclusionChecks()),
        review(exclusions=ExclusionChecks(politics=False)),
        review(policy_version="obsolete"),
        review(reviewer="  "),
        review(rationale="  "),
        review(reviewed_at=datetime(2026, 10, 29)),
    ],
)
def test_incomplete_or_untrusted_review_is_unresolved(receipt):
    assert evaluate_domain(SHA, receipt).status == "insufficient_evidence"


def test_other_content_is_excluded():
    assert evaluate_domain(SHA, review(category="documentary")).status == "excluded"


def test_known_fixture_is_admitted_by_exact_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", tmp_path)
    source = domain_policy.ROOT / "eval/execution-v1/sources/sort.mp4"
    report = require_files({"source": source})
    assert report["source"]["review"]["basis"] == "frozen_fixture"
    changed = tmp_path / "sort.mp4"
    changed.write_bytes(source.read_bytes() + b"altered")
    with pytest.raises(DomainAdmissionError):
        require_files({"source": changed})


def test_manifest_changes_do_not_silently_expand_admission(tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"sources": {"fake": {"sha256": SHA}}, "cases": []}))
    monkeypatch.setattr(domain_policy, "MANIFEST", manifest)
    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", tmp_path / "reviews")
    assert decision_for_hash(SHA).status == "insufficient_evidence"


@pytest.mark.parametrize("contents", ["{broken", '{"basis":"frozen_fixture"}'])
def test_invalid_local_receipt_cannot_fall_back_to_fixture(
    contents, tmp_path, monkeypatch
):
    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", tmp_path)
    sha256 = digest(domain_policy.ROOT / "eval/execution-v1/sources/sort.mp4")
    (tmp_path / f"{sha256}.json").write_text(contents)
    assert decision_for_hash(sha256).status == "insufficient_evidence"


def test_local_exclusion_overrides_frozen_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", tmp_path)
    sha256 = digest(domain_policy.ROOT / "eval/execution-v1/sources/sort.mp4")
    receipt = review(sha256=sha256, exclusions=ExclusionChecks(news=True))
    (tmp_path / f"{sha256}.json").write_text(receipt.model_dump_json())
    assert decision_for_hash(sha256).status == "excluded"


def test_invalid_hash_does_not_access_review_store(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid hashes must not trigger file access")

    monkeypatch.setattr(domain_policy, "review_for_hash", forbidden)
    assert decision_for_hash("../../secrets").status == "insufficient_evidence"


@pytest.mark.parametrize(
    "endpoint,fields",
    [
        ("/api/analyze", ["original", "edited"]),
        ("/api/library", ["original"]),
        ("/api/library/search", ["edited"]),
    ],
)
def test_unreviewed_upload_stops_before_work(
    isolated_domain, monkeypatch, endpoint, fields
):
    def forbidden(*args, **kwargs):
        pytest.fail("Unreviewed content must not reach analysis or indexing")

    monkeypatch.setattr(api, "analyze", forbidden)
    monkeypatch.setattr(api, "add_source", forbidden)
    monkeypatch.setattr(api, "rank_sources", forbidden)
    result = isolated_domain.post(
        endpoint,
        data={"category": "software_benchmark"},
        files={key: ("trusted-benchmark.mp4", b"unreviewed footage") for key in fields},
    )
    assert result.status_code == 422, result.text
    assert all(
        d["status"] == "insufficient_evidence"
        for d in result.json()["domain_admission"].values()
    )
    assert not list(api.DATA.iterdir())
    assert not api.lock.locked()


def test_rejected_dossier_cannot_schedule_or_index(isolated_domain, monkeypatch):
    from context_core import dossier_api

    monkeypatch.setenv("MODEL_API_KEY", "test")

    async def forbidden(*args, **kwargs):
        pytest.fail("Unreviewed content must not schedule a model workflow")

    monkeypatch.setattr(dossier_api, "investigate", forbidden)
    result = isolated_domain.post(
        "/api/dossiers", files={"video": ("tutorial.mp4", b"unknown")}
    )
    assert result.status_code == 422
    assert not list(api.DATA.iterdir())
    assert not api.lock.locked()


def test_unreviewed_reference_is_rejected_before_indexing(
    isolated_domain, reviewed_clips, clips, monkeypatch
):
    from context_core import dossier_api

    monkeypatch.setenv("MODEL_API_KEY", "test")

    def forbidden(*args, **kwargs):
        pytest.fail("Unreviewed reference must not be indexed")

    monkeypatch.setattr(dossier_api, "add_source", forbidden)
    result = isolated_domain.post(
        "/api/dossiers",
        files={
            "video": ("tutorial.mp4", (clips / "omission.mp4").read_bytes()),
            "reference": ("original.mp4", b"unreviewed source"),
        },
    )
    assert result.status_code == 422
    assert (
        result.json()["domain_admission"]["source"]["status"] == "insufficient_evidence"
    )
    assert not list(api.DATA.iterdir())


def test_saved_review_cache_does_not_bypass_revoked_admission(
    isolated_domain, reviewed_clips, clips, monkeypatch
):
    from context_core.meta import evidence_signature

    response = isolated_domain.post(
        "/api/analyze",
        files={
            "original": ("original.mp4", (clips / "original.mp4").read_bytes()),
            "edited": ("edited.mp4", (clips / "omission.mp4").read_bytes()),
        },
    )
    assert response.status_code == 200
    evidence = response.json()
    target = api.DATA / evidence["id"]
    (target / "interpretation-f0.json").write_text(
        json.dumps(
            {
                "evidence_signature": evidence_signature(evidence, "f0"),
                "finding_id": "f0",
            }
        )
    )
    sha256 = evidence["source"]["sha256"]
    (domain_policy.REVIEW_ROOT / f"{sha256}.json").write_text(
        review(
            sha256=sha256, exclusions=ExclusionChecks(politics=True)
        ).model_dump_json()
    )

    async def forbidden(*args, **kwargs):
        pytest.fail("Revocation must stop cached and new model review")

    monkeypatch.setattr(api, "interpret", forbidden)
    result = isolated_domain.post(f"/api/investigations/{evidence['id']}/interpret/f0")
    assert result.status_code == 403
    assert result.json()["domain_admission"]["source"]["status"] == "excluded"
    # Historical evidence is still inspectable; it is not reanalyzed.
    assert (
        isolated_domain.get(f"/api/investigations/{evidence['id']}").status_code == 200
    )


def test_direct_semantic_call_is_also_gated(clips, isolated_domain, monkeypatch):
    from context_core import meta
    from context_core.alignment import analyze

    evidence = analyze(clips / "original.mp4", clips / "omission.mp4")

    async def forbidden(*args, **kwargs):
        pytest.fail("Admission must run before transport")

    monkeypatch.setattr(meta, "request", forbidden)
    with pytest.raises(DomainAdmissionError):
        asyncio.run(meta.interpret(evidence, "f0", []))


def test_deferred_roadway_workflow_is_excluded(isolated_domain, monkeypatch):
    async def forbidden(*args, **kwargs):
        pytest.fail("Excluded workflow cannot run")

    monkeypatch.setattr(api, "run_prelude_investigation", forbidden)
    assert (
        isolated_domain.post(
            "/api/prelude/investigate?sample_id=near_crash_011"
        ).status_code
        == 403
    )


def test_missing_media_is_unresolved_without_work(tmp_path):
    with pytest.raises(DomainAdmissionError) as error:
        require_files({"source": tmp_path / "missing.mp4"})
    assert error.value.status_code == 422
    assert error.value.decisions["source"].status == "insufficient_evidence"


def test_saved_evidence_cannot_substitute_different_admitted_bytes(
    isolated_domain, reviewed_clips, clips
):
    response = isolated_domain.post(
        "/api/analyze",
        files={
            "original": ("original.mp4", (clips / "original.mp4").read_bytes()),
            "edited": ("edited.mp4", (clips / "omission.mp4").read_bytes()),
        },
    )
    evidence = response.json()
    (api.DATA / evidence["id"] / "original.mp4").write_bytes(
        (clips / "copy.mp4").read_bytes()
    )
    result = isolated_domain.post(f"/api/investigations/{evidence['id']}/interpret/f0")
    assert result.status_code == 422
    assert "fingerprints" in result.json()["detail"]


def test_unreviewed_legacy_library_source_never_reaches_matcher(
    clips, tmp_path, reviewed_clips, monkeypatch
):
    from context_core import library

    root = tmp_path / "library"
    meta = library.add_source(root, clips / "original.mp4", "claimed tutorial")
    (domain_policy.REVIEW_ROOT / f"{meta['sha256']}.json").unlink()

    def forbidden(*args, **kwargs):
        pytest.fail(
            "Unreviewed legacy source must be removed before decoding or matching"
        )

    monkeypatch.setattr(library, "sample", forbidden)
    with pytest.raises(ValueError, match="Add an original"):
        library.rank_sources(root, clips / "omission.mp4", admitted_only=True)


def test_review_cli_requires_actual_operator_attestation_and_preserves_history(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.syspath_prepend(str(domain_policy.ROOT))
    from scripts.review_content import main

    monkeypatch.setattr(domain_policy, "REVIEW_ROOT", tmp_path / "reviews")
    media = tmp_path / "test.mp4"
    media.write_bytes(b"synthetic operator review contract fixture")
    args = [
        str(media),
        "--category",
        "product_demo",
        "--reviewer",
        "Test operator",
        "--rationale",
        "Simulated full-file review for CLI contract",
    ]
    with pytest.raises(SystemExit):
        main(args)
    assert not domain_policy.REVIEW_ROOT.exists()
    assert main([*args, "--reviewed-entire-file"]) == 0
    assert decision_for_hash(digest(media)).status == "eligible"
    with pytest.raises(SystemExit):
        main([*args, "--reviewed-entire-file"])
    assert (
        main([*args, "--reviewed-entire-file", "--replace", "--excluded", "news"]) == 0
    )
    assert decision_for_hash(digest(media)).status == "excluded"
    assert len(list((domain_policy.REVIEW_ROOT / "history").glob("*.json"))) == 1
    assert "operator_review" in capsys.readouterr().out


def test_changed_library_bytes_cannot_reuse_old_features(
    clips, tmp_path, reviewed_clips, monkeypatch
):
    from context_core import library

    root = tmp_path / "library"
    meta = library.add_source(root, clips / "original.mp4", "source")
    (root / meta["id"] / "original.mp4").write_bytes((clips / "copy.mp4").read_bytes())

    def forbidden(*args, **kwargs):
        pytest.fail("Admitted but changed bytes must not reuse a stale feature index")

    monkeypatch.setattr(library, "sample", forbidden)
    with pytest.raises(ValueError, match="Add an original"):
        library.rank_sources(root, clips / "omission.mp4", admitted_only=True)
