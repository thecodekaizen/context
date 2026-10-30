"""Deterministic source retrieval contracts; mocked model output is not inference evidence."""

import asyncio
import json
import shutil

import pytest
from context_core import source_catalog
from context_core.dossier import investigate
from context_core.library import add_source
from context_core.source_catalog import register
from context_core.source_video import discover_source_videos


@pytest.fixture
def catalog(tmp_path, monkeypatch, reviewed_clips):
    root = tmp_path / "catalog"
    monkeypatch.setattr(source_catalog, "CATALOG_ROOT", root)
    return root


def add_candidate(path, title="Technical recording", tags=()):
    return register(
        path,
        title=title,
        origin_url="https://github.com/example/technical-demo",
        license="Synthetic test fixture, not third-party footage",
        tags=tags,
    )


def job(tmp_path, clips, name):
    directory = tmp_path / "jobs" / name
    directory.mkdir(parents=True)
    shutil.copyfile(clips, directory / "video.mp4")
    return directory


def test_registration_does_not_approve_unknown_media(tmp_path, catalog):
    from context_core.domain_policy import DomainAdmissionError

    unknown = tmp_path / "claimed-benchmark.mp4"
    unknown.write_bytes(b"unreviewed content")
    with pytest.raises(DomainAdmissionError):
        add_candidate(unknown)
    assert not list(catalog.glob("records/*.json"))


def test_caption_rank_is_not_a_correspondence_verdict(clips, catalog, tmp_path):
    add_candidate(clips / "unknown.mp4", "Exact claimed benchmark", ["exact", "claim"])
    directory = job(tmp_path, clips / "omission.mp4", "unmatched")
    trace, evidence, path, selected = asyncio.run(
        discover_source_videos(
            directory, {"source_video_queries": ["Exact claimed benchmark"]}
        )
    )
    assert trace["status"] == "no_match"
    assert evidence is path is selected is None
    assert trace["candidates"][0]["status"] == "indexed_candidate"
    assert (directory / "source-video-retrieval.json").exists()


def test_automatic_match_with_no_source_id_or_caption(clips, catalog, tmp_path):
    wanted = add_candidate(clips / "original.mp4", "Reviewed CLI tutorial")
    add_candidate(clips / "unknown.mp4", "Different technical clip")
    directory = job(tmp_path, clips / "omission.mp4", "matched")
    trace, evidence, path, selected = asyncio.run(discover_source_videos(directory, {}))
    assert trace["status"] == "matched"
    assert selected["title"] == "Reviewed CLI tutorial"
    assert selected["source_id"] == wanted.sha256
    assert evidence["source"]["sha256"] == wanted.sha256
    assert path.is_file()
    assert trace["queries"] == []
    assert selected["discovery"] == "registered_technical_catalog"


def test_ties_across_local_and_catalog_sources_remain_ambiguous(
    clips, catalog, tmp_path
):
    local = tmp_path / "library"
    add_source(local, clips / "original.mp4", "Private reference")
    add_candidate(clips / "recompressed.mp4", "Near duplicate registered reference")
    directory = job(tmp_path, clips / "omission.mp4", "ambiguous")
    trace, evidence, path, selected = asyncio.run(
        discover_source_videos(directory, {}, library_root=local)
    )
    assert trace["status"] == "ambiguous"
    assert evidence is path is selected is None
    assert len(trace["alignment_selection"]["candidates"]) == 2


def test_duplicate_bytes_participate_once(clips, catalog, tmp_path):
    local = tmp_path / "library"
    add_source(local, clips / "original.mp4", "Private reference")
    add_candidate(clips / "original.mp4", "Same registered bytes")
    directory = job(tmp_path, clips / "omission.mp4", "duplicate")
    trace, evidence, _, _ = asyncio.run(
        discover_source_videos(directory, {}, library_root=local)
    )
    assert trace["status"] == "matched" and evidence
    assert any(c["status"] == "duplicate_bytes" for c in trace["candidates"])
    assert len(trace["alignment_selection"]["candidates"]) == 1


def test_changed_catalog_bytes_cannot_use_a_different_admitted_file(
    clips, catalog, tmp_path
):
    entry = add_candidate(clips / "original.mp4")
    (catalog / "media" / f"{entry.sha256}.mp4").write_bytes(
        (clips / "copy.mp4").read_bytes()
    )
    directory = job(tmp_path, clips / "omission.mp4", "changed")
    trace, evidence, _, _ = asyncio.run(discover_source_videos(directory, {}))
    assert evidence is None and trace["status"] == "source_unavailable"
    assert "fingerprint" in trace["candidates"][0]["reason"]


def test_no_match_never_calls_meta(clips, catalog, tmp_path, monkeypatch):
    from context_core import meta, providers

    async def forbidden(*args, **kwargs):
        pytest.fail("No matching source must result in zero model calls")

    monkeypatch.setattr(meta, "request", forbidden)
    monkeypatch.setattr(providers, "request", forbidden)
    add_candidate(clips / "unknown.mp4")
    directory = job(tmp_path, clips / "omission.mp4", "no-model")
    result = asyncio.run(investigate(directory, "This is a benchmark claim"))
    assert result["status"] == "partial"
    assert result["omission_evidence"]["status"] == "no material omission"
    assert result["comparison"]["reviews"] == []
    assert result["assessment"]["findings"][0]["verdict"] == "inconclusive"
    assert not (directory / "observation-response.json").exists()
    assert not (directory / "search-response.json").exists()


def test_faithful_match_never_calls_meta_and_restores_without_fake_observations(
    clips, catalog, tmp_path, monkeypatch
):
    from context_core import api, meta
    from fastapi.testclient import TestClient

    async def forbidden(*args, **kwargs):
        pytest.fail("Faithful matched excerpt must not trigger semantic review")

    monkeypatch.setattr(meta, "request", forbidden)
    add_candidate(clips / "original.mp4")
    directory = job(tmp_path, clips / "copy.mp4", "faithful")
    monkeypatch.setattr(api, "DATA", directory.parent)
    result = asyncio.run(investigate(directory))
    assert result["status"] == "complete"
    assert result["omission_evidence"]["status"] == "no material omission"
    assert (
        result["comparison"]["semantic_status"] == "not_requested_no_grounded_omission"
    )
    restored = TestClient(api.app).get("/api/dossiers/faithful")
    assert restored.status_code == 200
    assert restored.json()["status"] == "complete"
    assert restored.json()["assessment"]["summary"] == "no material omission"
    assert restored.json()["analysis"]["observations"] == []
    assert restored.json()["validation_version"] == 4


def test_only_grounded_clips_reach_meta(clips, catalog, tmp_path, monkeypatch):
    from context_core import meta

    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    calls = []

    async def mocked_request(inputs, **kwargs):
        calls.append((inputs, kwargs))
        content = inputs[0]["content"]
        assert len([c for c in content if c["type"] == "input_video"]) == 2
        metadata = content[0]["text"]
        assert "Explain ONLY the supplied deterministic internal omission" in metadata
        return {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "classification": "inconclusive",
                                    "observations": [
                                        {
                                            "text": "Mocked bounded observation; not a live inference result.",
                                            "citations": [
                                                {
                                                    "clip_id": "source_context",
                                                    "start": 0,
                                                    "end": 1,
                                                }
                                            ],
                                        }
                                    ],
                                    "possible_effect": "Mock contract only.",
                                    "uncertainty": "Semantic accuracy is untested.",
                                }
                            ),
                        }
                    ],
                }
            ]
        }

    monkeypatch.setattr(meta, "request", mocked_request)
    add_candidate(clips / "original.mp4", "Reviewed tutorial")
    directory = job(tmp_path, clips / "omission.mp4", "omission")
    result = asyncio.run(investigate(directory))
    assert len(calls) == 1
    assert result["status"] == "complete"
    assert result["omission_evidence"]["omissions"][0]["source_start"] == 4
    review = result["comparison"]["reviews"][0]
    assert review["finding"]["kind"] == "omission"
    assert all(c["end"] - c["start"] <= 30 for c in review["clips"])
    assert not (directory / "observation-response.json").exists()
