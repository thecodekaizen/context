import json
import os
import shutil
import threading
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from .alignment import analyze
from .context_pack import build_pack
from .dossier_api import router as dossier_router
from .fixtures import generate
from .library import add_source, list_sources, rank_sources
from .media import playback_file
from .meta import evidence_signature, interpret

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
app = FastAPI(title="CONTEXT", version="0.2.0")
lock = threading.Lock()


def save_evidence(directory, result):
    result["id"] = directory.name
    result["media"] = {}
    for kind, filename in [("source", "original"), ("edited", "edited")]:
        playback = playback_file(
            directory / f"{filename}.mp4", directory / f"{filename}-preview.mp4"
        )
        result["media"][kind] = f"/api/media/{directory.name}/{playback.name}"
    temporary = directory / "evidence.tmp"
    temporary.write_text(json.dumps(result, indent=2))
    temporary.replace(directory / "evidence.json")
    return result


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
        signature = evidence_signature(evidence, finding_id)
        cached = directory / f"interpretation-{finding_id}.json"
        if cached.is_file():
            previous = json.loads(cached.read_text())
            if previous.get("evidence_signature") == signature:
                return {**previous, "cached": True}
        if not os.getenv("MODEL_API_KEY"):
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
    return (
        identifier == "demo"
        or len(identifier) == 32
        and all(c in "0123456789abcdef" for c in identifier)
    )


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


app.include_router(dossier_router(lambda: DATA, lock))

if (ROOT / "web/dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "web/dist", html=True), name="web")
