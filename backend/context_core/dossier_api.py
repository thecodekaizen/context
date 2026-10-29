"""Single-input jobs, persistence, and media; comparison API stays separate."""

import json
import os
import re
from pathlib import Path
from threading import Lock
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .dossier import investigate, write
from .retrieval import download_video


def router(data_root, lock: Lock):
    api = APIRouter(prefix="/api/dossiers")

    def directory(identifier):
        if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", identifier):
            raise HTTPException(404)
        target = data_root() / identifier
        if not (target / "dossier.json").is_file():
            raise HTTPException(404)
        return target

    async def process(target, caption, provenance):
        try:
            await investigate(target, caption, provenance)
        finally:
            lock.release()

    @api.post("", status_code=202)
    async def create(
        background: BackgroundTasks,
        video: Annotated[UploadFile | None, File()] = None,
        url: Annotated[str, Form()] = "",
        caption: Annotated[str, Form(max_length=4000)] = "",
    ):
        if bool(video) == bool(url.strip()):
            raise HTTPException(
                422, "Submit one video upload OR one supported direct-media URL"
            )
        if not os.getenv("MODEL_API_KEY"):
            raise HTTPException(
                503, "Meta credentials are unavailable; investigation cannot start"
            )
        if not lock.acquire(blocking=False):
            raise HTTPException(429, "An investigation is already running")
        target = data_root() / uuid4().hex
        target.mkdir(parents=True)
        try:
            if video:
                size = 0
                with (target / "video.mp4").open("wb") as out:
                    while chunk := await video.read(1024 * 1024):
                        size += len(chunk)
                        if size > 200 * 1024 * 1024:
                            raise ValueError("Video exceeds 200 MB")
                        out.write(chunk)
                await video.close()
                provenance = {
                    "method": "upload",
                    "filename": Path(video.filename or "video").name,
                    "original_recording_supplied": False,
                }
            else:
                provenance = await download_video(url.strip(), target / "video.mp4")
            write(
                target,
                {
                    "id": target.name,
                    "mode": "single_video",
                    "status": "running",
                    "stage": "queued",
                    "caption": caption,
                    "sources": [],
                },
            )
            background.add_task(process, target, caption, provenance)
            return {
                "id": target.name,
                "status": "running",
                "poll_url": f"/api/dossiers/{target.name}",
            }
        except Exception as exc:
            lock.release()
            if isinstance(exc, ValueError):
                raise HTTPException(422, str(exc)) from exc
            raise

    @api.get("")
    def recent():
        files = sorted(
            data_root().glob("*/dossier.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:25]
        return {"dossiers": [json.loads(f.read_text()) for f in files]}

    @api.get("/{identifier}")
    def get(identifier: str):
        return json.loads((directory(identifier) / "dossier.json").read_text())

    @api.get("/{identifier}/media/{filename}")
    def media(identifier: str, filename: str):
        if filename not in {
            "video.mp4",
            "preview.mp4",
            "analysis.mp4",
            "dossier.json",
        } and filename not in {f"frame-{i}.jpg" for i in range(8)}:
            raise HTTPException(404)
        path = directory(identifier) / filename
        if not path.is_file():
            raise HTTPException(404)
        return FileResponse(path)

    return api
