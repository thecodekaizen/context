import json

import pytest
from context_core.api import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_api_storage(tmp_path, monkeypatch):
    from context_core import api

    directory = tmp_path / "appdata"
    directory.mkdir()
    monkeypatch.setattr(api, "DATA", directory)


def test_upload_and_evidence(clips):
    with (
        (clips / "original.mp4").open("rb") as a,
        (clips / "omission.mp4").open("rb") as b,
    ):
        r = client.post(
            "/api/analyze",
            files={
                "original": ("source.mp4", a, "video/mp4"),
                "edited": ("edit.mp4", b, "video/mp4"),
            },
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["findings"][0]["kind"] == "omission"
    saved = client.get(f"/api/media/{data['id']}/evidence.json")
    assert saved.json() == data
    media = client.get(data["media"]["source"], headers={"Range": "bytes=0-99"})
    assert media.status_code == 206
    assert len(media.content) == 100


def test_bad_upload_and_path():
    r = client.post(
        "/api/analyze",
        files={"original": ("bad.mp4", b"bad"), "edited": ("bad.mp4", b"bad")},
    )
    assert r.status_code == 422
    assert client.get("/api/media/demo/secret.env").status_code == 404


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_review_without_key(clips, monkeypatch, tmp_path):
    from context_core import api

    monkeypatch.setattr(api, "DATA", tmp_path)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    r = client.post("/api/demo")
    assert r.status_code == 200
    response = client.post("/api/investigations/demo/interpret/f0")
    assert response.status_code == 503
    assert "MODEL_API_KEY" in response.json()["detail"]
    assert client.post("/api/investigations/not-valid/interpret/f0").status_code == 404


def test_case_restore_and_invalid_id(clips, tmp_path, monkeypatch):
    from context_core import api

    monkeypatch.setattr(api, "DATA", tmp_path)
    with (
        (clips / "original.mp4").open("rb") as a,
        (clips / "omission.mp4").open("rb") as b,
    ):
        r = client.post(
            "/api/analyze",
            files={"original": ("source.mp4", a), "edited": ("edit.mp4", b)},
        )
    evidence = r.json()
    cases = client.get("/api/investigations").json()["investigations"]
    assert cases[0]["id"] == evidence["id"]
    restored = client.get("/api/investigations/" + evidence["id"]).json()
    assert restored["evidence"] == evidence
    assert restored["reviews"] == []
    assert client.get("/api/investigations/not-valid").status_code == 404


def test_review_cache_requires_matching_evidence(clips, tmp_path, monkeypatch):
    from context_core import api
    from context_core.meta import evidence_signature

    monkeypatch.setattr(api, "DATA", tmp_path)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    with (
        (clips / "original.mp4").open("rb") as a,
        (clips / "omission.mp4").open("rb") as b,
    ):
        evidence = client.post(
            "/api/analyze",
            files={"original": ("source.mp4", a), "edited": ("edit.mp4", b)},
        ).json()
    identifier = evidence["id"]
    saved = {
        "evidence_signature": evidence_signature(evidence, "f0"),
        "finding_id": "f0",
        "interpretation": {
            "observations": [],
            "possible_effect": "Test",
            "uncertainty": "Test",
        },
        "model": "test",
    }
    path = tmp_path / identifier / "interpretation-f0.json"
    path.write_text(json.dumps(saved))
    r = client.post(f"/api/investigations/{identifier}/interpret/f0")
    assert r.status_code == 200 and r.json()["cached"]
    assert len(client.get(f"/api/investigations/{identifier}").json()["reviews"]) == 1
    saved["evidence_signature"] = "stale"
    path.write_text(json.dumps(saved))
    assert (
        client.post(f"/api/investigations/{identifier}/interpret/f0").status_code == 503
    )
    assert not client.get(f"/api/investigations/{identifier}").json()["reviews"]


def test_film_example_unavailable(tmp_path, monkeypatch):
    from context_core import api

    monkeypatch.setattr(api, "DATA", tmp_path)
    assert not client.get("/api/health").json()["film_demo_available"]
    assert client.post("/api/demo/film").status_code == 404


def test_incompatible_container_upload_serves_preview(clips, tmp_path, monkeypatch):
    from context_core import api
    from context_core.media import digest, run

    monkeypatch.setattr(api, "DATA", tmp_path)
    original = tmp_path / "input.mkv"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(clips / "original.mp4"),
            "-c",
            "copy",
            str(original),
        ]
    )
    with original.open("rb") as a, (clips / "omission.mp4").open("rb") as b:
        r = client.post(
            "/api/analyze",
            files={"original": ("camera.mkv", a), "edited": ("cut.mp4", b)},
        )
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["source"]["sha256"] == digest(original)
    assert result["source"]["name"] == "camera.mkv"
    assert result["media"]["source"].endswith("original-preview.mp4")
    preview = client.get(result["media"]["source"], headers={"Range": "bytes=0-99"})
    assert preview.status_code == 206 and len(preview.content) == 100


def test_prelude_samples_endpoint():
    r = client.get("/api/prelude/samples")
    assert r.status_code == 200
    samples = r.json()
    assert len(samples) >= 4
    sample_ids = {s["id"] for s in samples}
    assert "near_crash_011" in sample_ids
    assert "normal_safe_004" in sample_ids


def test_prelude_sample_media_endpoint():
    r = client.get("/api/prelude/samples/near_crash_011/media", headers={"Range": "bytes=0-99"})
    assert r.status_code in (200, 206)
    assert len(r.content) > 0


def test_prelude_investigate_sample_endpoint(monkeypatch):
    # Mock model call so test does not require live external API call
    from context_core import prelude

    async def mock_meta(frames, timestamps, t_cutoff, kinematics, **kwargs):
        return {
            "hazard_detected": True,
            "risk_level": "critical",
            "risk_cue_seconds": 6.6,
            "hazard_actor": "silver hatchback",
            "conflict_type": "lateral_encroachment",
            "observations": ["At t=6.6s, silver hatchback enters ego lane"],
            "uncertainty": "Offline monocular replay only.",
        }

    monkeypatch.setattr(prelude, "analyze_pre_incident_with_meta", mock_meta)

    r = client.post("/api/prelude/investigate?sample_id=near_crash_011&t_cutoff=7.1&t_incident=7.8")
    assert r.status_code == 200, r.text
    dossier = r.json()
    assert dossier["hazard_detected"] is True
    assert dossier["risk_level"] == "critical"
    assert dossier["finding"]["t_cue_seconds"] == 6.6
    assert dossier["lead_time"] == 1.2
    assert "media_url" in dossier
    assert "disclaimer" in dossier

