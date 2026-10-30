import asyncio
import json

import httpx
import pytest
from context_core.comparison import comparison_evidence, interval_coverage
from context_core.dossier import model_request
from context_core.meta import validate_interpretation
from context_core.source_video import candidate_queries, eligible_metadata


def test_audio_discontinuity_is_not_labeled_visual_authentication():
    evidence = {
        "coverage": 0.425,
        "status": "insufficient_evidence",
        "findings": [],
        "segments": [],
        "edited": {"duration": 10},
        "audio_alignment": {
            "segments": [
                {
                    "kind": "match",
                    "edited_start": 0,
                    "edited_end": 4,
                    "source_start": 20,
                    "source_end": 24,
                },
                {
                    "kind": "match",
                    "edited_start": 4,
                    "edited_end": 10,
                    "source_start": 4,
                    "source_end": 10,
                },
            ]
        },
    }
    result = comparison_evidence(evidence)
    assert result["status"] == "insufficient_evidence"
    assert result["comparison_basis"] == "audio_only"
    assert result["findings"][0]["kind"] == "reordering"
    assert result["findings"][0]["modality"] == "audio"
    assert result["audio_coverage"] == 1


def test_audio_coverage_does_not_double_count_overlap():
    assert (
        interval_coverage(
            [
                {"kind": "match", "edited_start": 0, "edited_end": 5},
                {"kind": "match", "edited_start": 4, "edited_end": 10},
            ],
            10,
        )
        == 1
    )


def test_semantic_verdict_requires_both_source_and_edit_evidence():
    raw = {
        "classification": "meaning_changed",
        "observations": [
            {
                "text": "A qualification",
                "citations": [{"clip_id": "source_context", "start": 0, "end": 1}],
            }
        ],
        "possible_effect": "Definitely misleading",
        "uncertainty": "limited",
    }
    result = validate_interpretation(
        json.dumps(raw),
        [{"id": "source_context", "media": "source", "start": 10, "end": 20}],
    )
    assert result["classification"] == "inconclusive"
    assert "Definitely" not in result["possible_effect"]


def test_source_catalog_scope_and_rights_filter():
    assert eligible_metadata({"nasa_id": "x", "center": "JSC", "media_type": "video"})
    assert not eligible_metadata(
        {
            "nasa_id": "x",
            "center": "JSC",
            "media_type": "video",
            "description": "Copyright third party",
        }
    )
    assert not eligible_metadata({"nasa_id": "x", "media_type": "video"})
    assert (
        len(candidate_queries({"source_video_queries": ["one", "two", "three"]})) == 2
    )


def test_provider_retry_is_bounded_and_failure_recorded(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_API_KEY", "test")
    attempts = []

    def handler(request):
        attempts.append(request)
        return httpx.Response(503, json={"error": "unavailable"})

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(
            model_request(
                "test", transport=httpx.MockTransport(handler), receipt_dir=tmp_path
            )
        )
    assert len(attempts) == 2
    assert len(json.loads((tmp_path / "model-calls.json").read_text())) == 2


def test_long_omission_is_reviewed_as_explicitly_truncated_context():
    from context_core.context_pack import plan_clips

    e = {
        "status": "matched",
        "coverage": 0.9,
        "source": {"duration": 120},
        "edited": {"duration": 14},
        "segments": [],
        "findings": [],
        "audio_alignment": {
            "segments": [
                {
                    "kind": "match",
                    "edited_start": 0,
                    "edited_end": 2.5,
                    "source_start": 11,
                    "source_end": 13.5,
                },
                {
                    "kind": "match",
                    "edited_start": 3,
                    "edited_end": 13.5,
                    "source_start": 57.8,
                    "source_end": 68.3,
                },
            ]
        },
    }
    evidence = comparison_evidence(e)
    finding = evidence["review_targets"][0]
    assert finding["kind"] == "omission"
    clips = plan_clips(evidence, finding["id"])
    assert clips[0]["start"] < 14
    assert clips[0]["end"] > 20
    assert clips[0]["end"] - clips[0]["start"] <= 30
    assert clips[0]["omitted_interval_fully_included"] is False
