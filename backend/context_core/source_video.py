"""Retrieve reviewed technical candidates, then independently test correspondence.

The registered catalog is bounded and operator-managed. This is not web-wide
reverse-video search. Titles and captions select candidates, never prove identity.
"""

import json
import re
import shutil
from pathlib import Path

from starlette.concurrency import run_in_threadpool

from . import source_catalog
from .domain_policy import DomainAdmissionError, require_files
from .library import MAX_SOURCES, add_source, list_sources, rank_sources

MAX_CANDIDATES = 4


def candidate_queries(analysis):
    queries = analysis.get("source_video_queries", []) or analysis.get(
        "search_queries", []
    )
    return list(
        dict.fromkeys(
            q.strip()[:160] for q in queries if isinstance(q, str) and q.strip()
        )
    )[:2]


async def discover_source_videos(
    directory, analysis, *, library_root=None, catalog_root=None
):
    directory = Path(directory)
    index = directory / "retrieved-library"
    catalog_root = (
        Path(catalog_root) if catalog_root is not None else source_catalog.CATALOG_ROOT
    )
    trace = {
        "provider": "Reviewed technical source catalog and local collection",
        "scope": "At most four registered technical candidates plus admitted local references, capped at twenty indexed sources. No internet-wide search or model-generated identity claims.",
        "queries": candidate_queries(analysis),
        "candidates": [],
        "status": "source_unavailable",
        "selection_method": "Untrusted caption words rank catalog titles and tags; deterministic correspondence independently selects media.",
    }
    selected_records = {}

    def persist():
        (directory / "source-video-retrieval.json").write_text(
            json.dumps(trace, indent=2)
        )

    # User-provided references participate in the same index/margin decision.
    # Do not choose winners independently and then conceal a cross-index tie.
    if library_root is not None:
        for meta in list_sources(library_root):
            record = {
                "title": meta["name"],
                "source_id": meta["id"],
                "discovery": "local_collection",
                "status": "unavailable",
            }
            trace["candidates"].append(record)
            try:
                if not re.fullmatch(r"[a-f0-9]{64}", meta["id"]):
                    raise ValueError("Invalid local source identity")
                path = Path(library_root) / meta["id"] / "original.mp4"
                admission = await run_in_threadpool(require_files, {"source": path})
                if (
                    admission["source"]["sha256"] != meta["sha256"]
                    or meta["id"] != meta["sha256"]
                ):
                    raise ValueError("Local source bytes changed; rebuild its index")
                destination = index / meta["id"]
                destination.mkdir(parents=True, exist_ok=True)
                for name in ("original.mp4", "metadata.json", "features.npz"):
                    shutil.copyfile(
                        Path(library_root) / meta["id"] / name, destination / name
                    )
                record.update(
                    status="indexed_candidate",
                    sha256=meta["sha256"],
                    domain_admission=admission,
                )
                selected_records[meta["id"]] = record
            except (DomainAdmissionError, ValueError, OSError) as exc:
                record.update(status="excluded_or_unavailable", reason=str(exc)[:400])
    try:
        entries = source_catalog.rank_records(
            source_catalog.records(catalog_root), trace["queries"], MAX_CANDIDATES
        )
    except (ValueError, OSError) as exc:
        entries = []
        trace["catalog_error"] = str(exc)[:300]
    for entry in entries:
        record = {
            **entry.model_dump(),
            "asset_url": entry.origin_url,
            "discovery": "registered_technical_catalog",
            "status": "unavailable",
        }
        trace["candidates"].append(record)
        if entry.sha256 in selected_records:
            record.update(
                status="duplicate_bytes",
                reason="Same bytes already participate through the local collection",
            )
            continue
        if len(selected_records) >= MAX_SOURCES:
            record.update(
                status="budget_exhausted",
                reason="Twenty-source deterministic comparison budget reached",
            )
            continue
        try:
            path = catalog_root / "media" / f"{entry.sha256}.mp4"
            admission = await run_in_threadpool(require_files, {"candidate": path})
            if admission["candidate"]["sha256"] != entry.sha256:
                raise ValueError(
                    "Catalog bytes do not match the registered fingerprint"
                )
            meta = await run_in_threadpool(add_source, index, path, entry.title)
            record.update(
                status="indexed_candidate",
                source_id=meta["id"],
                domain_admission=admission,
            )
            selected_records[meta["id"]] = record
        except (DomainAdmissionError, ValueError, OSError) as exc:
            record.update(status="excluded_or_unavailable", reason=str(exc)[:400])
    persist()
    if not selected_records:
        return trace, None, None, None
    report, evidence = await run_in_threadpool(
        rank_sources, index, directory / "video.mp4", admitted_only=True
    )
    trace.update(status=report["status"], alignment_selection=report)
    persist()
    if evidence is None:
        return trace, None, None, None
    selected = selected_records[report["candidates"][0]["id"]]
    return trace, evidence, index / selected["source_id"] / "original.mp4", selected
