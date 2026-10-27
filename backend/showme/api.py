"""Local HTTP bridge for Teach's evidence-linked video learning flow."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Annotated
import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .media import inspect_video, make_model_video
from .meta import MuseSparkClient
from .observe import observe_snapshot, observe_video, validate_observation, validate_snapshot
from .process import validate_references

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
MAX_SNAPSHOT_BYTES = 5 * 1024 * 1024
ALLOWED_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm"}

app = FastAPI(title="SHOWME local skill API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "showme"}


@app.post("/api/skills/learn")
def learn_skill(
    video: Annotated[UploadFile, File(description="Short demonstration video")],
    narration: Annotated[str, Form(max_length=4000)] = "",
) -> dict:
    """Create a candidate process from one video; the model call is billable."""
    suffix = Path(video.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Choose an MP4, MOV, M4V, or WebM video.")
    if not os.environ.get("MODEL_API_KEY") and not _repo_key_exists():
        raise HTTPException(status_code=503, detail="Set MODEL_API_KEY in the repository's local .env file first.")

    try:
        with tempfile.TemporaryDirectory(prefix="showme-teach-") as temporary:
            root = Path(temporary)
            source = root / f"demonstration{suffix}"
            size = _copy_bounded(video, source)
            if size == 0:
                raise ValueError("The selected video is empty.")

            metadata = inspect_video(source)
            model_video = root / "model-input.mp4"
            model_metadata = make_model_video(source, model_video)
            process = MuseSparkClient.from_env().learn(
                model_video,
                duration_seconds=metadata["duration_seconds"],
                narration=narration,
            )
            validate_references(process, duration_seconds=metadata["duration_seconds"])

            # Keep the browser response useful and auditable; don't expose remote
            # provider file IDs that have already been deleted by the adapter.
            run = process.get("_run", {})
            process["_run"] = {
                "model": run.get("model"),
                "prompt_version": run.get("prompt_version"),
                "usage": run.get("usage", {}),
                "source": {
                    "filename": Path(video.filename or "demonstration").name,
                    "size_bytes": size,
                    "duration_seconds": metadata["duration_seconds"],
                    "width": metadata["width"],
                    "height": metadata["height"],
                    "audio_present": metadata["audio_present"],
                },
                "model_video": model_metadata,
            }
            process["_validation"] = "passed"
            return {"process": process, "status": "candidate-needs-human-review"}
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        video.file.close()


@app.post("/api/skills/observe")
def observe_learner(
    video: Annotated[UploadFile, File(description="Learner attempt video")],
    process_json: Annotated[str, Form(max_length=100_000)],
) -> dict:
    """Compare a learner clip against the reviewed candidate process."""
    suffix = _validate_video(video)
    if not os.environ.get("MODEL_API_KEY") and not _repo_key_exists():
        raise HTTPException(status_code=503, detail="Set MODEL_API_KEY in the repository's local .env file first.")
    try:
        process = json.loads(process_json)
        if not isinstance(process, dict):
            raise ValueError("The reviewed process must be a JSON object.")
        source_duration = process.get("_run", {}).get("source", {}).get("duration_seconds")
        validate_references(process, duration_seconds=source_duration)

        with tempfile.TemporaryDirectory(prefix="showme-do-") as temporary:
            root = Path(temporary)
            source = root / f"learner{suffix}"
            size = _copy_bounded(video, source)
            if size == 0:
                raise ValueError("The selected learner video is empty.")

            metadata = inspect_video(source)
            model_video = root / "model-input.mp4"
            model_metadata = make_model_video(source, model_video)
            observation = observe_video(
                MuseSparkClient.from_env(),
                model_video,
                process,
                metadata["duration_seconds"],
            )
            validate_observation(observation, process, metadata["duration_seconds"])
            run = observation.get("_run", {})
            observation["_run"] = {
                "model": run.get("model"),
                "prompt_version": run.get("prompt_version"),
                "usage": run.get("usage", {}),
            }
            return {
                "observation": observation,
                "status": observation["recovery_status"],
                "source": {
                    "filename": Path(video.filename or "learner").name,
                    "size_bytes": size,
                    "duration_seconds": metadata["duration_seconds"],
                },
                "model_video": model_metadata,
            }
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        video.file.close()


@app.post("/api/skills/observe-snapshot")
def observe_learner_snapshot(
    image: Annotated[UploadFile, File(description="One JPEG camera snapshot")],
    process_json: Annotated[str, Form(max_length=100_000)],
) -> dict:
    """Assess one explicitly requested camera frame; this is not continuous tracking."""
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg"} or image.content_type not in {"image/jpeg", "image/jpg"}:
        raise HTTPException(status_code=415, detail="Capture a JPEG snapshot from the camera preview.")
    if not os.environ.get("MODEL_API_KEY") and not _repo_key_exists():
        raise HTTPException(status_code=503, detail="Set MODEL_API_KEY in the repository's local .env file first.")
    try:
        process = json.loads(process_json)
        if not isinstance(process, dict):
            raise ValueError("The reviewed process must be a JSON object.")
        validate_references(process)
        with tempfile.TemporaryDirectory(prefix="showme-snapshot-") as temporary:
            image_path = Path(temporary) / "snapshot.jpg"
            size = _copy_bounded(image, image_path, max_bytes=MAX_SNAPSHOT_BYTES)
            if size == 0:
                raise ValueError("The camera snapshot is empty.")
            observation = observe_snapshot(MuseSparkClient.from_env(), image_path, process)
            validate_snapshot(observation, process)
            run = observation.get("_run", {})
            observation["_run"] = {
                "model": run.get("model"),
                "prompt_version": run.get("prompt_version"),
                "usage": run.get("usage", {}),
            }
            return {"observation": observation, "status": observation["assessment"]}
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        image.file.close()


def _copy_bounded(
    upload: UploadFile,
    destination: Path,
    *,
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> int:
    total = 0
    with destination.open("wb") as output:
        while chunk := upload.file.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                limit = "5 MB" if max_bytes == MAX_SNAPSHOT_BYTES else "100 MB"
                raise HTTPException(status_code=413, detail=f"Keep this upload under {limit}.")
            output.write(chunk)
    return total


def _validate_video(video: UploadFile) -> str:
    suffix = Path(video.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Choose an MP4, MOV, M4V, or WebM video.")
    return suffix


def _repo_key_exists() -> bool:
    env_file = Path(__file__).resolve().parents[2] / ".env"
    if not env_file.is_file():
        return False
    return any(line.strip().startswith("MODEL_API_KEY=") for line in env_file.read_text(encoding="utf-8").splitlines())
