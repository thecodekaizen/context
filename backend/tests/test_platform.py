import csv
import io
import json

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.usefixtures("reviewed_clips")


def test_supplied_source_is_private_to_job_and_capture_provenance_preserved(
    tmp_path, clips, monkeypatch
):
    from context_core import api, dossier_api

    monkeypatch.setattr(api, "DATA", tmp_path)
    monkeypatch.setenv("MODEL_API_KEY", "test")
    calls = []

    async def investigate(target, caption, provenance, **kwargs):
        calls.append((target, provenance, kwargs))

    monkeypatch.setattr(dossier_api, "investigate", investigate)
    with TestClient(api.app) as client:
        response = client.post(
            "/api/dossiers",
            data={"input_kind": "camera"},
            files={
                "video": (
                    "camera.webm",
                    (clips / "omission.mp4").read_bytes(),
                    "video/webm",
                ),
                "reference": (
                    "original.mp4",
                    (clips / "original.mp4").read_bytes(),
                    "video/mp4",
                ),
            },
        )
    assert response.status_code == 202
    target, provenance, kwargs = calls[0]
    assert provenance["input_kind"] == "camera"
    assert provenance["original_recording_supplied"]
    assert kwargs["library_root"] == target / "reference-library"
    assert list((target / "reference-library").glob("*/metadata.json"))
    assert not (tmp_path / "library").exists()
    assert not api.lock.locked()


def test_markers_include_semantics_and_escape_formula_text(tmp_path, monkeypatch):
    from context_core import api

    monkeypatch.setattr(api, "DATA", tmp_path)
    target = tmp_path / "case"
    target.mkdir()
    (target / "dossier.json").write_text(
        json.dumps(
            {
                "id": "case",
                "status": "running",
                "comparison": {
                    "reviews": [
                        {
                            "status": "complete",
                            "model": "test",
                            "interpretation": {
                                "classification": "meaning_changed",
                                "observations": [
                                    {
                                        "text": "=HYPERLINK(unsafe)",
                                        "citations": [
                                            {
                                                "media": "source",
                                                "media_start": 1,
                                                "media_end": 2,
                                            }
                                        ],
                                    }
                                ],
                            },
                        }
                    ]
                },
            }
        )
    )
    response = TestClient(api.app).get("/api/dossiers/case/markers.csv")
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert rows[0]["classification"] == "meaning_changed"
    assert rows[0]["observation"].startswith("'=HYPERLINK")
    assert rows[0]["start_seconds"] == "1"


def test_streamed_browser_webm_without_duration_header_is_decodable(tmp_path):
    from context_core.media import probe, run

    target = tmp_path / "capture.webm"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x120:rate=12",
            "-t",
            "2",
            "-c:v",
            "libvpx",
            "-f",
            "webm",
            "-live",
            "1",
            str(target),
        ]
    )
    info = probe(target)
    assert 1.8 <= info["duration"] <= 2.1
    assert info["width"] == 160


def test_cross_site_page_cannot_launch_credentialed_inference():
    from context_core import api

    response = TestClient(api.app).post(
        "/api/dossiers",
        headers={"Origin": "https://untrusted.example"},
        files={"video": ("x.mp4", b"bad")},
    )
    assert response.status_code == 403


def test_audio_tail_does_not_break_observation_frame_extraction(tmp_path):
    from context_core.dossier import prepare
    from context_core.media import run

    target = tmp_path / "video.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=duration=2:size=160x120:rate=12",
            "-f",
            "lavfi",
            "-i",
            "sine=duration=2.25:sample_rate=16000",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(target),
        ]
    )
    result = prepare(tmp_path)
    assert len(result["frames"]) == 8
    assert result["frames"][-1]["time"] < result["video_duration"]
    assert all((tmp_path / f"frame-{i}.jpg").is_file() for i in range(8))
