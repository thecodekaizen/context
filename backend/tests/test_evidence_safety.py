"""Regression tests for trust failures reproduced in the independent audit."""

import json
import math

import pytest
from context_core.dossier import validate_analysis, validate_assessment
from context_core.meta import validate_interpretation
from context_core.prelude import validate_risk_result


@pytest.mark.parametrize(
    "excerpt", ["   ", "\t\n ", "\u200b\u200b\u200b", "...", "invented quotation"]
)
def test_meaningless_or_missing_excerpt_cannot_support_claim(excerpt):
    result = validate_assessment(
        json.dumps(
            {
                "findings": [
                    {
                        "claim_id": "c",
                        "verdict": "supported",
                        "explanation": "model",
                        "source_refs": [{"source_id": "s", "excerpt": excerpt}],
                    }
                ]
            }
        ),
        {"claims": [{"id": "c"}]},
        [{"id": "s", "fetch_status": "fetched", "text": "An uncrewed flight test."}],
    )
    assert result["findings"][0]["verdict"] == "inconclusive"
    assert result["findings"][0]["source_refs"] == []


@pytest.mark.parametrize("status", ["unavailable", "linked", "error"])
def test_unfetched_source_cannot_support_claim(status):
    result = validate_assessment(
        json.dumps(
            {
                "findings": [
                    {
                        "claim_id": "c",
                        "verdict": "contradicted",
                        "explanation": "model",
                        "source_refs": [
                            {"source_id": "s", "excerpt": "uncrewed flight"}
                        ],
                    }
                ]
            }
        ),
        {"claims": [{"id": "c"}]},
        [{"id": "s", "fetch_status": status, "text": "uncrewed flight"}],
    )
    assert result["findings"][0]["verdict"] == "inconclusive"


def test_conflicting_duplicate_conclusions_are_withheld():
    finding = {
        "claim_id": "c",
        "verdict": "supported",
        "explanation": "model",
        "source_refs": [{"source_id": "s", "excerpt": "uncrewed flight"}],
    }
    result = validate_assessment(
        json.dumps({"findings": [finding, {**finding, "verdict": "contradicted"}]}),
        {"claims": [{"id": "c"}]},
        [{"id": "s", "fetch_status": "fetched", "text": "uncrewed flight"}],
    )
    assert result["findings"][0]["verdict"] == "inconclusive"


@pytest.mark.parametrize(
    "start,end", [(-1, 2), (0, math.inf), (math.nan, 2), (True, 2), (0, 21), (4, 3)]
)
def test_invalid_intervals_never_become_observations(start, end):
    result = validate_analysis(
        json.dumps(
            {
                "observations": [
                    {
                        "id": "o",
                        "text": "event",
                        "start": start,
                        "end": end,
                        "modality": "visual",
                    }
                ]
            }
        ),
        {"analyzed_seconds": 20, "has_audio": True},
        "",
    )
    assert result["observations"] == []


def test_numeric_local_ids_are_namespaced_without_altering_evidence():
    result = validate_analysis(
        json.dumps(
            {
                "observations": [
                    {
                        "id": 1,
                        "text": "event",
                        "start": 1,
                        "end": 2,
                        "modality": "visual",
                    }
                ],
                "claims": [
                    {"id": 1, "text": "quote", "start": 1, "end": 2, "origin": "speech"}
                ],
            }
        ),
        {"analyzed_seconds": 20, "has_audio": True},
        "",
    )
    assert result["observations"][0]["id"] == "observation-1"
    assert result["claims"][0]["id"] == "claim-1"
    assert result["claims"][0]["start"] == 1


@pytest.mark.parametrize(
    "hazard,level,cue",
    [
        ("false", "high", 1),
        (True, "high", -100),
        (True, "high", 30),
        (True, "high", math.nan),
        (True, "nominal", 1),
        (False, "critical", None),
        (False, "nominal", 1),
        (True, "high", True),
    ],
)
def test_invalid_risk_cannot_create_warning_or_safe_claim(hazard, level, cue):
    result = validate_risk_result(
        {"hazard_detected": hazard, "risk_level": level, "risk_cue_seconds": cue}, 5
    )
    assert result["risk_level"] == "unverified"
    assert result["risk_cue_seconds"] is None
    assert result["hazard_detected"] is False


def test_boolean_model_citation_time_rejected():
    with pytest.raises(ValueError):
        validate_interpretation(
            json.dumps(
                {
                    "observations": [
                        {
                            "text": "event",
                            "citations": [{"clip_id": "a", "start": False, "end": 1}],
                        }
                    ],
                    "possible_effect": "uncertain",
                    "uncertainty": "limited",
                }
            ),
            [{"id": "a", "start": 0, "end": 2, "media": "source"}],
        )


def test_invalid_quote_is_withheld_by_final_api_and_download(tmp_path, monkeypatch):
    from context_core import api
    from fastapi.testclient import TestClient

    monkeypatch.setattr(api, "DATA", tmp_path)
    job = tmp_path / "invalid-quote"
    job.mkdir()
    report = {
        "id": job.name,
        "status": "complete",
        "caption": "Crew present",
        "media": {"analyzed_seconds": 10, "has_audio": False},
        "analysis": {
            "observations": [
                {
                    "id": "o",
                    "text": "rocket",
                    "start": 0,
                    "end": 1,
                    "modality": "visual",
                }
            ],
            "claims": [
                {"id": "c", "text": "Crew present", "origin": "supplied_caption"}
            ],
        },
        "assessment": {
            "findings": [
                {
                    "claim_id": "c",
                    "verdict": "supported",
                    "explanation": "unsafe prior output",
                    "source_refs": [{"source_id": "s", "excerpt": "   "}],
                }
            ]
        },
        "sources": [{"id": "s", "fetch_status": "fetched", "text": "uncrewed flight"}],
    }
    (job / "dossier.json").write_text(json.dumps(report))
    client = TestClient(api.app)
    for endpoint in [
        f"/api/dossiers/{job.name}",
        f"/api/dossiers/{job.name}/media/dossier.json",
    ]:
        result = client.get(endpoint)
        assert result.status_code == 200
        finding = result.json()["assessment"]["findings"][0]
        assert finding["verdict"] == "inconclusive"
        assert finding["source_refs"] == []
