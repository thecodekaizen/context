import json
import pytest
from context_core.dossier import (
    extract_json_text,
    validate_analysis,
    validate_assessment,
)
from context_core.retrieval import inspect_source, public_url, search_receipts
from fastapi.testclient import TestClient
from context_core.api import app

client = TestClient(app)


def test_extract_json_text():
    assert extract_json_text('```json\n{"summary": "test"}\n```') == '{"summary": "test"}'
    assert extract_json_text('Prefix text {"summary": "test"} suffix') == '{"summary": "test"}'
    assert extract_json_text('{"summary": "test"}') == '{"summary": "test"}'


def test_validate_analysis_robustness():
    media = {"analyzed_seconds": 90.0, "has_audio": True}
    raw = json.dumps({
        "summary": "Launch video overview",
        "observations": [
            {"id": f"obs{i}", "text": f"Event {i}", "start": i, "end": i + 1, "modality": "visual"}
            for i in range(25)
        ],
        "claims": [
            {"id": "c1", "text": "Artemis I had astronauts", "origin": "supplied_caption", "start": 0, "end": 0},
            {"id": "c2", "text": "Liftoff confirmed", "origin": "speech", "start": 5, "end": 10},
        ],
        "search_queries": ["Artemis I astronauts"],
        "unknowns": ["Mission crew status"],
    })
    analysis = validate_analysis(raw, media, "Artemis I had astronauts")
    assert len(analysis["observations"]) == 25
    assert len(analysis["claims"]) == 2
    assert analysis["claims"][0]["start"] is None
    assert analysis["claims"][0]["end"] is None
    assert analysis["claims"][1]["start"] == 5.0
    assert analysis["claims"][1]["end"] == 10.0


def test_validate_analysis_silent_audio():
    media = {"analyzed_seconds": 60.0, "has_audio": False}
    raw = json.dumps({
        "summary": "Silent video",
        "observations": [{"id": "obs1", "text": "Sound event", "start": 0, "end": 2, "modality": "audio"}],
        "claims": [{"id": "c1", "text": "Spoken text", "origin": "speech", "start": 0, "end": 2}],
    })
    analysis = validate_analysis(raw, media, "")
    assert analysis["observations"][0]["modality"] == "visual"
    assert analysis["claims"][0]["origin"] == "on_screen"


def test_validate_assessment_excerpts():
    analysis = {
        "claims": [
            {"id": "c1", "text": "Artemis I carried astronauts to the Moon.", "origin": "supplied_caption"},
            {"id": "c2", "text": "Rocket was blue", "origin": "on_screen"},
        ]
    }
    sources = [
        {
            "id": "source-0",
            "url": "https://www.nasa.gov/mission/artemis-i/",
            "fetch_status": "fetched",
            "text": "Artemis I was an uncrewed flight test to the Moon.",
        }
    ]
    raw_assessment = json.dumps({
        "summary": "Investigation completed",
        "findings": [
            {
                "claim_id": "c1",
                "verdict": "contradicted",
                "explanation": "Official documents state the mission was uncrewed.",
                "source_refs": [{"source_id": "source-0", "excerpt": "uncrewed flight test"}],
            },
            {
                "claim_id": "c2",
                "verdict": "supported",
                "explanation": "Claim with hallucinated source quote.",
                "source_refs": [{"source_id": "source-0", "excerpt": "The rocket was painted bright blue"}],
            },
        ],
        "provenance": "NASA records",
        "missing_evidence": [],
    })
    res = validate_assessment(raw_assessment, analysis, sources)
    f1 = next(f for f in res["findings"] if f["claim_id"] == "c1")
    assert f1["verdict"] == "contradicted"
    assert len(f1["source_refs"]) == 1

    f2 = next(f for f in res["findings"] if f["claim_id"] == "c2")
    # Because hallucinated quote was rejected and valid citations were empty, verdict becomes inconclusive
    assert f2["verdict"] == "inconclusive"
    assert len(f2["source_refs"]) == 0


def test_public_url_validation():
    assert public_url("https://www.nasa.gov/mission/artemis-i/") == "https://www.nasa.gov/mission/artemis-i/"
    assert public_url("https://en.wikipedia.org/wiki/Artemis_1") == "https://en.wikipedia.org/wiki/Artemis_1"
    
    # Media URLs
    assert "images-assets.nasa.gov/video/test.mp4" in public_url(
        "http://images-assets.nasa.gov/video/test.mp4", media=True
    )
    
    with pytest.raises(ValueError, match="outside the current public-domain coverage"):
        public_url("https://random-unverified-blog.xyz/post")

    with pytest.raises(ValueError, match="Supported URLs are direct MP4/WebM/MOV"):
        public_url("https://images-assets.nasa.gov/video/test.exe", media=True)


def test_search_receipts():
    payload = {
        "output": [
            {
                "type": "web_search_call",
                "results": [
                    {"title": "Artemis I", "url": "https://www.nasa.gov/artemis-i/", "snippet": "Uncrewed mission"}
                ]
            }
        ]
    }
    sources, searched = search_receipts(payload)
    assert searched is True
    assert len(sources) == 1
    assert sources[0]["url"] == "https://www.nasa.gov/artemis-i/"


def test_dossiers_api(tmp_path, monkeypatch):
    from context_core import api
    directory = tmp_path / "appdata"
    directory.mkdir()
    monkeypatch.setattr(api, "DATA", directory)

    dossier_dir = directory / "test1234567890abcdef1234567890ab"
    dossier_dir.mkdir()
    dossier_data = {
        "id": dossier_dir.name,
        "mode": "single_video",
        "status": "complete",
        "stage": "complete",
        "caption": "Test caption",
        "sources": [],
    }
    (dossier_dir / "dossier.json").write_text(json.dumps(dossier_data))

    r = client.get(f"/api/dossiers/{dossier_dir.name}")
    assert r.status_code == 200
    assert r.json()["id"] == dossier_dir.name

    r_list = client.get("/api/dossiers")
    assert r_list.status_code == 200
    assert len(r_list.json()["dossiers"]) == 1
