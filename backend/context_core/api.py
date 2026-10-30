import json
import os
import re
import shutil
import threading
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import httpx
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from .alignment import analyze
from .context_pack import build_pack
from .dossier_api import router as dossier_router
from .fixtures import generate
from .library import add_source, list_sources, rank_sources
from .media import playback_file, save_evidence
from .meta import evidence_signature, interpret, require_grounded_omission
from .prelude import run_prelude_investigation
from .providers import configured

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
app = FastAPI(title="CONTEXT", version="0.3.0")
lock = threading.Lock()


@app.middleware("http")
async def local_origin(request: Request, call_next):
    if request.method in {
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    } and request.url.path.startswith("/api/"):
        origin = request.headers.get("origin")
        allowed = {str(request.base_url).rstrip("/")}
        if request.client and request.client.host in {"127.0.0.1", "::1", "testclient"}:
            allowed.update({"http://127.0.0.1:5173", "http://localhost:5173"})
        if origin and origin.rstrip("/") not in allowed:
            return JSONResponse(
                {"detail": "Cross-origin engine requests are not allowed"},
                status_code=403,
            )
    return await call_next(request)


def investigation(directory, source_name=None, edited_name=None):
    result = analyze(directory / "original.mp4", directory / "edited.mp4")
    if source_name:
        result["source"]["name"] = Path(source_name).name[:120]
    if edited_name:
        result["edited"]["name"] = Path(edited_name).name[:120]
    return save_evidence(directory, result)


async def save_upload(file, target):
    size = 0
    try:
        with target.open("wb") as out:
            while block := await file.read(1024 * 1024):
                size += len(block)
                if size > 200 * 1024 * 1024:
                    raise HTTPException(413, "Each video must be under 200 MB")
                out.write(block)
    finally:
        await file.close()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "meta_configured": bool(os.getenv("MODEL_API_KEY")),
        "semantic_example_id": "83767ad0f4c44a6e93cac7b7eea7dc48"
        if (DATA / "83767ad0f4c44a6e93cac7b7eea7dc48/dossier.json").is_file()
        else None,
        "film_demo_available": (DATA / "evaluation/source.mp4").is_file()
        and (DATA / "evaluation/omission.mp4").is_file(),
    }


@app.post("/api/analyze")
async def upload(
    original: Annotated[UploadFile, File()], edited: Annotated[UploadFile, File()]
):
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running. Try again shortly.")
    directory = DATA / uuid4().hex
    directory.mkdir()
    try:
        for name, file in [("original", original), ("edited", edited)]:
            await save_upload(file, directory / f"{name}.mp4")
        return await run_in_threadpool(
            investigation, directory, original.filename, edited.filename
        )
    except ValueError as exc:
        shutil.rmtree(directory, ignore_errors=True)
        raise HTTPException(422, str(exc)) from exc
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    finally:
        lock.release()


@app.post("/api/demo")
async def demo():
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    try:
        directory = DATA / "demo"
        if not (directory / "omission.mp4").exists():
            await run_in_threadpool(generate, directory)
        shutil.copyfile(directory / "omission.mp4", directory / "edited.mp4")
        return await run_in_threadpool(investigation, directory)
    finally:
        lock.release()


@app.post("/api/demo/film")
async def film_demo():
    if (
        not (DATA / "evaluation/source.mp4").is_file()
        or not (DATA / "evaluation/omission.mp4").is_file()
    ):
        raise HTTPException(
            404,
            "Optional film example is not installed. Run the evaluation download first.",
        )
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    directory = DATA / uuid4().hex
    directory.mkdir()
    try:
        shutil.copyfile(DATA / "evaluation/source.mp4", directory / "original.mp4")
        shutil.copyfile(DATA / "evaluation/omission.mp4", directory / "edited.mp4")
        result = await run_in_threadpool(
            analyze, directory / "original.mp4", directory / "edited.mp4"
        )
        result["source"].update(
            name="Big Buck Bunny — licensed film excerpt",
            provenance={
                "title": "Big Buck Bunny (2008)",
                "attribution": "(c) copyright 2008, Blender Foundation / www.bigbuckbunny.org",
                "license": "CC BY 3.0",
                "url": "https://peach.blender.org/about/",
                "original_window_seconds": [40, 64],
                "transformations": "Trimmed, transcoded and edited for a controlled omission example. Published variant has no audio.",
            },
        )
        return await run_in_threadpool(save_evidence, directory, result)
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    finally:
        lock.release()


@app.post("/api/demo/benchmark")
async def benchmark_demo():
    source = ROOT / "eval/execution-v1/sources/sort.mp4"
    edited = ROOT / "data/execution-v1/edits/sort-omission.mp4"
    if not source.is_file() or not edited.is_file():
        raise HTTPException(404, "Restore the frozen execution fixtures first")
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    directory = DATA / "execution-benchmark"
    directory.mkdir(exist_ok=True)
    try:
        shutil.copyfile(source, directory / "original.mp4")
        shutil.copyfile(edited, directory / "edited.mp4")
        result = await run_in_threadpool(
            investigation,
            directory,
            "Controlled JavaScript sort benchmark (CC0)",
            "Scripted benchmark omission",
        )
        return result
    finally:
        lock.release()


@app.post("/api/demo/crop")
async def crop_demo():
    source = ROOT / "eval/execution-v1/sources/cache.mp4"
    edited = ROOT / "data/execution-v1/edits/cache-crop_omission.mp4"
    if not source.is_file() or not edited.is_file():
        raise HTTPException(404, "Restore the frozen execution fixtures first")
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    directory = DATA / "execution-crop-demo"
    directory.mkdir(exist_ok=True)
    try:
        shutil.copyfile(source, directory / "original.mp4")
        shutil.copyfile(edited, directory / "edited.mp4")
        result = await run_in_threadpool(
            investigation,
            directory,
            "Controlled JavaScript cache benchmark (CC0)",
            "Spatial crop & peripheral context omission",
        )
        return result
    finally:
        lock.release()


@app.get("/api/media/{identifier}/{filename}")
def media(identifier: str, filename: str):
    if not valid_identifier(identifier) or filename not in {
        "original.mp4",
        "edited.mp4",
        "original-preview.mp4",
        "edited-preview.mp4",
        "evidence.json",
    }:
        raise HTTPException(404)
    path = DATA / identifier / filename
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


@app.post("/api/investigations/{identifier}/interpret/{finding_id}")
async def review(identifier: str, finding_id: str):
    if not valid_identifier(identifier):
        raise HTTPException(404)
    directory = DATA / identifier
    if not (directory / "evidence.json").is_file():
        raise HTTPException(404, "Investigation does not exist")
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    try:
        evidence = json.loads((directory / "evidence.json").read_text())
        require_grounded_omission(evidence, finding_id)
        signature = evidence_signature(evidence, finding_id)
        cached = directory / f"interpretation-{finding_id}.json"
        if cached.is_file():
            previous = json.loads(cached.read_text())
            if previous.get("evidence_signature") == signature:
                return {**previous, "cached": True}
        if not configured():
            raise HTTPException(
                503,
                "Meta analysis unavailable: configure MODEL_API_KEY in the server environment.",
            )
        clips = await run_in_threadpool(build_pack, directory, evidence, finding_id)
        result = await interpret(evidence, finding_id, clips)
        # Save separately so model statements never become deterministic findings.
        target = directory / f"interpretation-{finding_id}.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, indent=2))
        temporary.replace(target)
        return result
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            502,
            "Meta request failed. Check account access and server configuration; measured evidence is unchanged.",
        ) from exc
    finally:
        lock.release()


def valid_identifier(identifier):
    return bool(re.match(r"^[a-zA-Z0-9_-]{1,64}$", identifier))


@app.get("/api/investigations")
def recent_investigations():
    paths = sorted(
        (p for p in DATA.glob("*/evidence.json") if valid_identifier(p.parent.name)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:30]
    cases = []
    for path in paths:
        result = json.loads(path.read_text())
        cases.append(
            {
                "id": result["id"],
                "status": result["status"],
                "coverage": result["coverage"],
                "source_name": result["source"].get(
                    "name",
                    "Generated case" if result["id"] == "demo" else "Uploaded source",
                ),
                "finding_count": len(result["findings"]),
            }
        )
    return {"investigations": cases}


@app.get("/api/investigations/{identifier}")
def restore_investigation(identifier: str):
    if (
        not valid_identifier(identifier)
        or not (DATA / identifier / "evidence.json").is_file()
    ):
        raise HTTPException(404, "Investigation does not exist")
    evidence = json.loads((DATA / identifier / "evidence.json").read_text())
    reviews = []
    for finding in evidence["findings"]:
        path = DATA / identifier / f"interpretation-{finding['id']}.json"
        if path.is_file():
            result = json.loads(path.read_text())
            if result.get("evidence_signature") == evidence_signature(
                evidence, finding["id"]
            ):
                reviews.append(result)
    return {"evidence": evidence, "reviews": reviews}


@app.get("/api/library")
def collection():
    return {
        "sources": list_sources(DATA / "library"),
        "scope": "provided_local_collection",
        "limit": 20,
    }


@app.post("/api/library")
async def index_source(original: Annotated[UploadFile, File()]):
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    temporary = DATA / (uuid4().hex + ".upload")
    try:
        name = original.filename or "Untitled source"
        await save_upload(original, temporary)
        return await run_in_threadpool(add_source, DATA / "library", temporary, name)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        temporary.unlink(missing_ok=True)
        lock.release()


@app.post("/api/library/search")
async def search_collection(edited: Annotated[UploadFile, File()]):
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running")
    directory = DATA / uuid4().hex
    directory.mkdir()
    try:
        await save_upload(edited, directory / "edited.mp4")
        report, evidence = await run_in_threadpool(
            rank_sources, DATA / "library", directory / "edited.mp4"
        )
        if evidence is None:
            shutil.rmtree(directory, ignore_errors=True)
            return {"search": report, "evidence": None}
        selected = report["candidates"][0]
        shutil.copyfile(
            DATA / "library" / selected["id"] / "original.mp4",
            directory / "original.mp4",
        )
        evidence["source_selection"] = report
        evidence["source"]["name"] = selected["name"]
        return {
            "search": report,
            "evidence": await run_in_threadpool(save_evidence, directory, evidence),
        }
    except ValueError as exc:
        shutil.rmtree(directory, ignore_errors=True)
        raise HTTPException(422, str(exc)) from exc
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    finally:
        lock.release()


PRELUDE_BENCHMARK_DIR = DATA / "prelude_benchmark"
PRELUDE_SAMPLES = {
    "near_crash_011": {
        "id": "near_crash_011",
        "title": "Australian Dashcam — T-Intersection Yield Failure",
        "description": "Australian road dashcam: oncoming hatchback cuts across path at uncontrolled junction.",
        "filename": "near_crash_011.mp4",
        "t_incident": 7.8,
        "t_cutoff": 7.1,
        "expected_hazard": True,
        "conflict_type": "lateral_encroachment",
    },
    "near_crash_007": {
        "id": "near_crash_007",
        "title": "Australian Dashcam — Residential Junction Near-Miss",
        "description": "Australian road dashcam: crossing vehicle at junction with limited sightline.",
        "filename": "near_crash_007.mp4",
        "t_incident": 4.5,
        "t_cutoff": 4.0,
        "expected_hazard": True,
        "conflict_type": "lateral_encroachment",
    },
    "normal_safe_004": {
        "id": "normal_safe_004",
        "title": "Safe Residential Driving Control",
        "description": "Normal daylight residential driving: vehicle yields stopped at give-way triangle. Negative control.",
        "filename": "normal_safe_004.mp4",
        "t_incident": None,
        "t_cutoff": 3.0,
        "expected_hazard": False,
        "conflict_type": "nominal_flow",
    },
    "normal_safe_061": {
        "id": "normal_safe_061",
        "title": "Safe Suburban Arterial Driving Control",
        "description": "Normal suburban arterial driving with steady lane keeping. Negative control.",
        "filename": "normal_safe_061.mp4",
        "t_incident": None,
        "t_cutoff": 6.0,
        "expected_hazard": False,
        "conflict_type": "nominal_flow",
    },
}


@app.get("/api/prelude/samples")
async def list_prelude_samples():
    """Return available pre-loaded dashcam benchmark scenarios."""
    items = []
    for sid, meta in PRELUDE_SAMPLES.items():
        vpath = PRELUDE_BENCHMARK_DIR / meta["filename"]
        items.append(
            {
                **meta,
                "available": vpath.exists(),
                "media_url": f"/api/prelude/samples/{sid}/media",
            }
        )
    return items


@app.get("/api/prelude/samples/{sample_id}/media")
async def get_prelude_sample_media(sample_id: str):
    """Stream dashcam sample video."""
    sample = PRELUDE_SAMPLES.get(sample_id)
    if not sample:
        raise HTTPException(404, "Sample not found")
    vpath = PRELUDE_BENCHMARK_DIR / sample["filename"]
    if not vpath.exists():
        raise HTTPException(404, "Sample media file not available on disk")
    return FileResponse(vpath, media_type="video/mp4")


@app.post("/api/prelude/investigate")
async def investigate_prelude(
    sample_id: str | None = None,
    t_cutoff: float | None = None,
    t_incident: float | None = None,
    video: UploadFile | None = None,
):
    """Run anticipatory roadway hazard analysis on uploaded dashcam or sample scenario."""
    if not lock.acquire(blocking=False):
        raise HTTPException(429, "An analysis is already running. Try again shortly.")

    try:
        if sample_id:
            sample = PRELUDE_SAMPLES.get(sample_id)
            if not sample:
                raise HTTPException(404, f"Sample '{sample_id}' not found")
            vpath = PRELUDE_BENCHMARK_DIR / sample["filename"]
            if not vpath.exists():
                raise HTTPException(
                    404, f"Sample video file '{sample['filename']}' not found on disk"
                )
            cutoff = t_cutoff if t_cutoff is not None else sample["t_cutoff"]
            incident = t_incident if t_incident is not None else sample["t_incident"]
            dossier = await run_prelude_investigation(
                video_path=vpath,
                t_cutoff=cutoff,
                t_incident=incident,
            )
            dossier_dict = dossier.model_dump()
            dossier_dict["media_url"] = f"/api/prelude/samples/{sample_id}/media"
            return dossier_dict

        if video is None:
            raise HTTPException(
                400, "Either sample_id or video upload must be provided"
            )

        upload_dir = DATA / f"prelude_upload_{uuid4().hex[:12]}"
        upload_dir.mkdir(parents=True, exist_ok=True)
        target_path = upload_dir / "dashcam.mp4"
        await save_upload(video, target_path)

        preview_path = upload_dir / "preview.mp4"
        final_media = await run_in_threadpool(playback_file, target_path, preview_path)

        dossier = await run_prelude_investigation(
            video_path=final_media,
            t_cutoff=t_cutoff,
            t_incident=t_incident,
        )
        dossier_dict = dossier.model_dump()
        dossier_dict["media_url"] = f"/api/media/{upload_dir.name}/{final_media.name}"
        return dossier_dict

    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Prelude analysis error: {exc}") from exc
    finally:
        lock.release()


app.include_router(dossier_router(lambda: DATA, lock))

if (ROOT / "web/dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "web/dist", html=True), name="web")
