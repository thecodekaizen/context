"""Local HTTP bridge for Teach's evidence-linked video learning flow."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .media import inspect_video, make_model_video
from .meta import MuseVideoLearner
from .process import validate_references

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
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
            process = MuseVideoLearner.from_env().learn(
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


def _copy_bounded(upload: UploadFile, destination: Path) -> int:
    total = 0
    with destination.open("wb") as output:
        while chunk := upload.file.read(1024 * 1024):
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Keep the demonstration video under 100 MB.")
            output.write(chunk)
    return total


def _repo_key_exists() -> bool:
    env_file = Path(__file__).resolve().parents[2] / ".env"
    if not env_file.is_file():
        return False
    return any(line.strip().startswith("MODEL_API_KEY=") for line in env_file.read_text(encoding="utf-8").splitlines())
