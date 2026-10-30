import pytest
from context_core import api
from context_core.library import add_source, list_sources, rank_sources
from fastapi.testclient import TestClient

pytestmark = pytest.mark.usefixtures("reviewed_clips")


def test_index_dedup_and_search(clips, tmp_path):
    collection = tmp_path / "library"
    first = add_source(collection, clips / "original.mp4", "source recording.mp4")
    again = add_source(collection, clips / "original.mp4", "renamed.mp4")
    assert first == again and len(list_sources(collection)) == 1
    add_source(collection, clips / "unknown.mp4", "distractor.mp4")
    report, result = rank_sources(collection, clips / "omission.mp4")
    assert report["status"] == "matched"
    assert report["candidates"][0]["id"] == first["id"]
    assert result["source"]["sha256"] == first["sha256"]
    assert result["findings"][0]["kind"] == "omission"


def test_unknown_source(clips, tmp_path):
    add_source(tmp_path, clips / "original.mp4", "source.mp4")
    report, result = rank_sources(tmp_path, clips / "unknown.mp4")
    assert report["status"] == "no_match" and result is None


def test_similar_sources_are_ambiguous(clips, tmp_path):
    # Different encodes of the same content must not produce a confident choice.
    add_source(tmp_path, clips / "original.mp4", "original.mp4")
    add_source(tmp_path, clips / "recompressed.mp4", "near duplicate.mp4")
    report, result = rank_sources(tmp_path, clips / "omission.mp4")
    assert report["status"] == "ambiguous" and result is None
    assert report["margin"] < report["minimum_margin"]


def test_empty_collection(clips, tmp_path):
    with pytest.raises(ValueError, match="Add an original"):
        rank_sources(tmp_path, clips / "omission.mp4")


def test_collection_end_to_end(clips, tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DATA", tmp_path)
    client = TestClient(api.app)
    for file in ("unknown.mp4", "original.mp4"):
        with (clips / file).open("rb") as f:
            r = client.post("/api/library", files={"original": (file, f, "video/mp4")})
        assert r.status_code == 200, r.text
    assert len(client.get("/api/library").json()["sources"]) == 2
    with (clips / "omission.mp4").open("rb") as f:
        r = client.post(
            "/api/library/search", files={"edited": ("edit.mp4", f, "video/mp4")}
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["search"]["status"] == "matched"
    assert body["evidence"]["source"]["name"] == "original.mp4"
    evidence = client.get(f"/api/media/{body['evidence']['id']}/evidence.json").json()
    assert evidence["source_selection"] == body["search"]
    assert client.get(body["evidence"]["media"]["source"]).status_code == 200


def test_low_visual_coverage_does_not_suppress_independent_audio(monkeypatch, tmp_path):
    import numpy as np
    from context_core import audio_alignment, library
    from context_core.media import VideoSamples

    root = tmp_path / "index"
    (root / "a").mkdir(parents=True)
    meta = {
        "id": "a",
        "name": "reference",
        "sha256": "a",
        "duration": 10,
        "has_audio": True,
    }
    (root / "a/metadata.json").write_text(__import__("json").dumps(meta))
    np.savez(root / "a/features.npz", times=np.array([0]), frames=np.zeros((1, 1152)))
    monkeypatch.setattr(
        library,
        "sample",
        lambda _: VideoSamples(
            {"duration": 10, "has_audio": True},
            np.array([0]),
            np.zeros((1, 1152)),
            "query",
        ),
    )
    monkeypatch.setattr(
        library,
        "align_samples",
        lambda *_: {
            "status": "insufficient_evidence",
            "coverage": 0.1,
            "segments": [],
            "findings": [],
        },
    )
    monkeypatch.setattr(
        audio_alignment,
        "analyze_audio",
        lambda *_: {
            "segments": [
                {
                    "kind": "match",
                    "edited_start": 0,
                    "edited_end": 9,
                    "source_start": 0,
                    "source_end": 9,
                }
            ]
        },
    )
    report, evidence = library.rank_sources(root, "query")
    assert report["status"] == "matched"
    assert report["selection_basis"] == "audio_correspondence"
    assert evidence["coverage"] == 0.1
    assert evidence["status"] == "insufficient_evidence"


def test_exact_bytes_resolve_static_source_without_visual_guessing(clips, tmp_path):
    add_source(tmp_path, clips / "unknown.mp4", "Static technical calibration")
    report, evidence = rank_sources(tmp_path, clips / "unknown.mp4")
    assert report["status"] == "matched"
    assert report["selection_basis"] == "byte_identity"
    assert evidence["method"]["name"] == "sha256-byte-identity"
    assert evidence["coverage"] == 1
    assert evidence["findings"] == []
    assert evidence["segments"][0]["source_start"] == 0
