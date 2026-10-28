import pytest
from context_core import api
from context_core.library import add_source, list_sources, rank_sources
from fastapi.testclient import TestClient


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
