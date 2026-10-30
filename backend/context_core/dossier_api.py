"""Single-input jobs, persistence, and media; comparison API stays separate."""

import csv
import io
import json
import re
from pathlib import Path
from threading import Lock
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.concurrency import run_in_threadpool

from .dossier import (
    investigate,
    text_output,
    validate_analysis,
    validate_assessment,
    write,
)
from .library import add_source
from .providers import configured
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
            await investigate(
                target,
                caption,
                provenance,
                library_root=target / "reference-library"
                if (target / "reference-library").is_dir()
                else None,
            )
        finally:
            lock.release()

    @api.post("", status_code=202)
    async def create(
        background: BackgroundTasks,
        video: Annotated[UploadFile | None, File()] = None,
        url: Annotated[str, Form()] = "",
        caption: Annotated[str, Form(max_length=4000)] = "",
        reference: Annotated[UploadFile | None, File()] = None,
        input_kind: Annotated[Literal["upload", "camera", "screen"], Form()] = "upload",
    ):
        if bool(video) == bool(url.strip()):
            raise HTTPException(
                422, "Submit one video upload OR one supported direct-media URL"
            )
        if not configured():
            raise HTTPException(
                503,
                "Meta credentials are unavailable; configure MODEL_API_KEY",
            )
        if not lock.acquire(blocking=False):
            raise HTTPException(429, "An investigation is already running")
        target = data_root() / uuid4().hex
        try:
            target.mkdir(parents=True)
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
            provenance["input_kind"] = "url" if url.strip() else input_kind
            if reference:
                source_path = target / "supplied-source.mp4"
                try:
                    size = 0
                    with source_path.open("wb") as out:
                        while block := await reference.read(1024 * 1024):
                            size += len(block)
                            if size > 200 * 1024 * 1024:
                                raise ValueError("Source recording exceeds 200 MB")
                            out.write(block)
                    await run_in_threadpool(
                        add_source,
                        target / "reference-library",
                        source_path,
                        reference.filename or "Supplied source",
                    )
                    provenance["original_recording_supplied"] = True
                finally:
                    await reference.close()
                    source_path.unlink(missing_ok=True)
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

    def validated_report(target):
        report = json.loads((target / "dossier.json").read_text())
        if report.get("status") in {"complete", "partial"}:
            observation = target / "observation-response.json"
            verification = target / "verification-response.json"
            analysis_text = (
                text_output(json.loads(observation.read_text()))
                if observation.exists()
                else json.dumps(report["analysis"])
            )
            assessment_text = (
                text_output(json.loads(verification.read_text()))
                if verification.exists()
                else json.dumps(report.get("assessment", {"findings": []}))
            )
            report["analysis"] = validate_analysis(
                analysis_text, report["media"], report.get("caption", "")
            )
            report["assessment"] = validate_assessment(
                assessment_text, report["analysis"], report.get("sources", [])
            )
            if not report["analysis"]["observations"]:
                report.update(
                    status="partial",
                    stage="partial",
                    error="No validated video observations are available; retained claims are limited to available evidence.",
                )
            report["validation_version"] = 3
        return report

    def read_report(target):
        try:
            return validated_report(target)
        except (ValueError, KeyError, TypeError) as exc:
            report = json.loads((target / "dossier.json").read_text())
            for field in ("analysis", "assessment"):
                report.pop(field, None)
            report.update(
                status="error",
                stage="error",
                error="Saved evidence failed validation; rerun investigation",
                validation_error=type(exc).__name__,
            )
            return report

    @api.get("")
    def recent():
        files = sorted(
            data_root().glob("*/dossier.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:25]
        return {"dossiers": [read_report(f.parent) for f in files]}

    @api.get("/{identifier}")
    def get(identifier: str):
        return read_report(directory(identifier))

    @api.get("/{identifier}/markers.csv")
    def markers(identifier: str):
        report = read_report(directory(identifier))
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "media",
                "start_seconds",
                "end_seconds",
                "classification",
                "observation",
                "model",
                "review_status",
            ]
        )
        for review in report.get("comparison", {}).get("reviews", []):
            if review.get("status") != "complete":
                continue
            interpretation = review.get("interpretation", {})
            for observation in interpretation.get("observations", []):
                for cite in observation.get("citations", []):
                    # Spreadsheet formula escapes preserve text without executing model output.
                    def safe(value):
                        text = str(value)
                        return (
                            "'" + text
                            if text.lstrip().startswith(("=", "+", "-", "@"))
                            else text
                        )

                    writer.writerow(
                        [
                            safe(cite["media"]),
                            cite["media_start"],
                            cite["media_end"],
                            safe(interpretation.get("classification", "inconclusive")),
                            safe(observation["text"]),
                            safe(review.get("model", "")),
                            "model_assessment",
                        ]
                    )
        return Response(
            output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{identifier}-review-markers.csv"'
            },
        )

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
        if filename == "dossier.json":
            return JSONResponse(
                read_report(path.parent),
                headers={
                    "Content-Disposition": f'attachment; filename="{identifier}-dossier.json"'
                },
            )
        return FileResponse(path)

    return api
