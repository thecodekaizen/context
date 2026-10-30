"""Bounded source acquisition from the official NASA catalog, with actual match tests.

Catalog hits are candidates, never established originals. No gated datasets or
social sites are scraped. The NASA government-media policy excludes third-party
copyrighted assets; preserve credits and exclude explicit third-party notices.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from starlette.concurrency import run_in_threadpool

from .library import add_source, rank_sources
from .retrieval import download_video, public_url

NASA_API = "https://images-api.nasa.gov"
POLICY = "https://www.nasa.gov/nasa-brand-center/images-and-media/"
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


def eligible_metadata(meta):
    if (
        meta.get("media_type") != "video"
        or not meta.get("nasa_id")
        or not meta.get("center")
    ):
        return False
    notice = " ".join(
        str(meta.get(k, "")) for k in ("copyright", "description", "secondary_creator")
    )
    return not re.search(
        r"©|copyright|all rights reserved|courtesy of|licensed (?:by|from)",
        notice,
        re.IGNORECASE,
    )


async def discover_source_videos(directory, analysis, *, transport=None):
    """Acquire <=4 small NASA videos from <=2 actual catalog queries.

    The candidate index is per-job, never the development library. Labels,
    expected source IDs and benchmark metadata are not accepted as inputs.
    """
    directory = Path(directory)
    index = directory / "retrieved-library"
    trace = {
        "provider": "NASA Image and Video Library",
        "scope": "NASA public catalog only",
        "queries": candidate_queries(analysis),
        "actual_queries": [],
        "candidates": [],
        "status": "no_candidates",
    }
    seen = set()
    async with httpx.AsyncClient(
        timeout=25, transport=transport, follow_redirects=False
    ) as client:
        for query in trace["queries"]:
            try:
                response = await client.get(
                    NASA_API + "/search",
                    params={"q": query, "media_type": "video", "page_size": 6},
                )
                response.raise_for_status()
                trace["actual_queries"].append(query)
                items = response.json().get("collection", {}).get("items", [])
                if not items and len(query.split()) > 2:
                    relaxed = " ".join(query.split()[:2])
                    response = await client.get(
                        NASA_API + "/search",
                        params={"q": relaxed, "media_type": "video", "page_size": 6},
                    )
                    response.raise_for_status()
                    trace["actual_queries"].append(relaxed)
                    items = response.json().get("collection", {}).get("items", [])
            except (httpx.HTTPError, ValueError) as exc:
                trace.setdefault("errors", []).append(str(exc)[:300])
                continue
            for item in items:
                meta = (item.get("data") or [{}])[0]
                identity = meta.get("nasa_id")
                if identity in seen or len(seen) >= MAX_CANDIDATES:
                    continue
                seen.add(identity)
                record = {
                    "catalog_id": identity,
                    "title": meta.get("title", ""),
                    "query": query,
                    "metadata": meta,
                    "policy_url": POLICY,
                    "status": "unavailable",
                }
                trace["candidates"].append(record)
                if not eligible_metadata(meta):
                    record.update(
                        status="excluded",
                        reason="Unsupported metadata or third-party rights notice; not acquired",
                    )
                    continue
                try:
                    response = await client.get(
                        NASA_API + "/asset/" + str(identity), params={}
                    )
                    response.raise_for_status()
                    urls = [
                        x.get("href", "")
                        for x in response.json().get("collection", {}).get("items", [])
                    ]
                    urls = [
                        u
                        for u in urls
                        if urlsplit(u).hostname == "images-assets.nasa.gov"
                        and urlsplit(u).path.lower().endswith(".mp4")
                    ]
                    urls.sort(
                        key=lambda u: (
                            "~small.mp4" not in u,
                            "~mobile.mp4" not in u,
                            len(u),
                        )
                    )
                    if not urls:
                        raise ValueError(
                            "No supported MP4 rendition in catalog asset response"
                        )
                    record["asset_url"] = public_url(urls[0], media=True)
                    target = directory / f"candidate-{len(trace['candidates'])}.mp4"
                    record["acquisition"] = await download_video(
                        record["asset_url"], target, max_bytes=50 * 1024 * 1024
                    )
                    meta_index = await run_in_threadpool(
                        add_source, index, target, meta["title"]
                    )
                    record.update(
                        status="indexed_candidate",
                        sha256=meta_index["sha256"],
                        source_id=meta_index["id"],
                        duration=meta_index["duration"],
                    )
                except (httpx.HTTPError, ValueError, OSError) as exc:
                    record.update(status="unavailable", reason=str(exc)[:300])
    trace["status"] = (
        "candidates_acquired"
        if any(c["status"] == "indexed_candidate" for c in trace["candidates"])
        else "source_unavailable"
    )
    (directory / "source-video-retrieval.json").write_text(json.dumps(trace, indent=2))
    if trace["status"] != "candidates_acquired":
        return trace, None, None, None
    report, evidence = await run_in_threadpool(
        rank_sources, index, directory / "video.mp4"
    )
    trace["alignment_selection"] = report
    trace["status"] = report["status"]
    selected = None
    if evidence:
        selected = next(
            c
            for c in trace["candidates"]
            if c.get("source_id") == report["candidates"][0]["id"]
        )
        selected_path = index / selected["source_id"] / "original.mp4"
    else:
        selected_path = None
    (directory / "source-video-retrieval.json").write_text(json.dumps(trace, indent=2))
    return trace, evidence, selected_path, selected
