import asyncio
import json

import httpx
import pytest
from context_core.alignment import analyze
from context_core.context_pack import build_pack, plan_clips
from context_core.media import digest, probe
from context_core.meta import interpret, validate_interpretation

pytestmark = pytest.mark.usefixtures("reviewed_clips")


@pytest.fixture
def evidence(clips):
    return analyze(clips / "original.mp4", clips / "omission.mp4")


def answer(clip_id="source_context", start=2, end=3):
    return json.dumps(
        {
            "observations": [
                {
                    "text": "A visible sequence is present.",
                    "citations": [{"clip_id": clip_id, "start": start, "end": end}],
                }
            ],
            "possible_effect": "Meaning cannot be established from this test.",
            "uncertainty": "Synthetic footage; no dialogue.",
        }
    )


def test_pack(clips, evidence, tmp_path):
    import shutil

    shutil.copy(clips / "original.mp4", tmp_path / "original.mp4")
    shutil.copy(clips / "omission.mp4", tmp_path / "edited.mp4")
    pack = build_pack(tmp_path, evidence, "f0")
    assert pack[0]["start"] == 2 and pack[0]["end"] == 10
    for clip in pack:
        assert (
            abs(probe(clip["path"])["duration"] - (clip["end"] - clip["start"])) < 0.2
        )
        assert len(clip["sha256"]) == 64
        assert not clip["has_audio"]
        assert len(clip["frames"]) == 3
        for frame in clip["frames"]:
            assert 0 <= frame["clip_local_seconds"] < clip["end"] - clip["start"]
            assert frame["media_seconds"] == clip["start"] + frame["clip_local_seconds"]
            assert digest(frame["path"]) == frame["sha256"]


def test_citation_translation(evidence):
    pack = plan_clips(evidence, "f0")
    result = validate_interpretation(answer(), pack)
    cite = result["observations"][0]["citations"][0]
    assert (
        cite["media"] == "source"
        and cite["media_start"] == 4
        and cite["media_end"] == 5
    )


@pytest.mark.parametrize(
    "clip,start,end",
    [
        ("invented", 0, 1),
        ("source_context", 0, 40),
        ("source_context", 3, 2),
        ("source_context", -1, 1),
        ("source_context", 0, float("nan")),
    ],
)
def test_invalid_citations(evidence, clip, start, end):
    with pytest.raises(ValueError):
        validate_interpretation(answer(clip, start, end), plan_clips(evidence, "f0"))


def test_invalid_finding(evidence):
    with pytest.raises(ValueError):
        plan_clips(evidence, "../../escape")
    evidence["status"] = "insufficient_evidence"
    with pytest.raises(ValueError):
        plan_clips(evidence, "f0")


def test_meta_request(evidence, tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    pack = plan_clips(evidence, "f0")
    for clip in pack:
        path = tmp_path / (clip["id"] + ".mp4")
        path.write_bytes(b"test-video")
        clip.update(path=str(path), has_audio=False, sha256="test")
        frame = tmp_path / (clip["id"] + ".jpg")
        frame.write_bytes(b"mocked-image-payload")
        clip["frames"] = [
            {
                "path": str(frame),
                "sha256": digest(frame),
                "clip_local_seconds": 1.0,
                "media_seconds": clip["start"] + 1.0,
            }
        ]

    def handler(request):
        body = json.loads(request.content)
        assert body["model"] == "muse-spark-1.2"
        videos = [c for c in body["input"][0]["content"] if c["type"] == "input_video"]
        assert len(videos) == 2 and all(
            v["video_url"].startswith("data:video/mp4;base64,") for v in videos
        )
        assert "path" not in body["input"][0]["content"][0]["text"]
        images = [c for c in body["input"][0]["content"] if c["type"] == "input_image"]
        assert len(images) == 2
        assert all(c["image_url"].startswith("data:image/jpeg;base64,") for c in images)
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": answer()}],
                    }
                ],
            },
        )

    result = asyncio.run(
        interpret(evidence, "f0", pack, transport=httpx.MockTransport(handler))
    )
    assert result["basis"] == "bounded_video_excerpts"
    assert result["citation_status"] == "bounds_checked_not_independently_verified"
    assert all("path" not in f for c in result["clips"] for f in c["frames"])


@pytest.mark.parametrize("invalid", ["outside_window", "changed_bytes", "too_many"])
def test_invalid_bounded_frames_never_reach_provider(
    evidence, tmp_path, monkeypatch, invalid
):
    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    pack = plan_clips(evidence, "f0")
    for clip in pack:
        video = tmp_path / (clip["id"] + ".mp4")
        video.write_bytes(b"mock-video")
        image = tmp_path / (clip["id"] + ".jpg")
        image.write_bytes(b"mock-image")
        clip.update(
            path=str(video),
            has_audio=False,
            sha256=digest(video),
            frames=[
                {
                    "path": str(image),
                    "sha256": digest(image),
                    "clip_local_seconds": 1.0,
                }
            ],
        )
    if invalid == "outside_window":
        pack[0]["frames"][0]["clip_local_seconds"] = pack[0]["end"] - pack[0]["start"]
    elif invalid == "changed_bytes":
        pack[0]["frames"][0]["sha256"] = "0" * 64
    else:
        pack[0]["frames"] *= 4

    def forbidden(request):
        pytest.fail("Invalid bounded frame reached the network transport")

    with pytest.raises(ValueError, match="[Ff]rame"):
        asyncio.run(
            interpret(evidence, "f0", pack, transport=httpx.MockTransport(forbidden))
        )


def test_missing_key(evidence, monkeypatch):
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MODEL_API_KEY"):
        asyncio.run(interpret(evidence, "f0", []))


def test_audio_survives_extraction(clips, evidence, tmp_path):
    from context_core.media import run

    for source, name in [
        ("original.mp4", "original.mp4"),
        ("omission.mp4", "edited.mp4"),
    ]:
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(clips / source),
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=16000",
                "-map",
                "0:v",
                "-map",
                "1:a",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(tmp_path / name),
            ]
        )
    evidence["source"]["has_audio"] = True
    evidence["edited"]["has_audio"] = True
    pack = build_pack(tmp_path, evidence, "f0")
    assert all(probe(c["path"])["has_audio"] for c in pack)
