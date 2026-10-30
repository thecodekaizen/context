"""Measured, modality-specific edit evidence and bounded semantic review."""

import itertools
import json
import shutil
from pathlib import Path

import httpx
from starlette.concurrency import run_in_threadpool

from .context_pack import build_pack
from .crop_detector import detect_video_crop
from .media import save_evidence
from .meta import interpret


def interval_coverage(segments, duration):
    intervals = sorted(
        (s["edited_start"], s["edited_end"])
        for s in segments
        if s.get("kind") == "match"
    )
    total = 0.0
    end = 0.0
    for a, b in intervals:
        total += max(0.0, min(duration, b) - max(a, end))
        end = max(end, b)
    return total / duration if duration else 0.0


def comparison_evidence(evidence):
    """Never turn audio matches into image correspondences.

    Audio discontinuities are independently inspectable edits to the soundtrack.
    They may corroborate a scene change but cannot authenticate the images.
    """
    audio = evidence.get("audio_alignment", {}).get("segments", [])
    audio_cov = interval_coverage(audio, evidence["edited"]["duration"])
    extra = []
    for previous, current in itertools.pairwise(audio):
        edit_gap = current["edited_start"] - previous["edited_end"]
        source_gap = current["source_start"] - previous["source_end"]
        if not -0.05 <= edit_gap <= 1.0:
            continue
        kind = None
        if source_gap - edit_gap >= 0.5:
            kind = "omission"
            a, b = previous["source_end"], current["source_start"]
        elif current["source_start"] < previous["source_start"] - 0.5:
            kind = "reordering"
            a, b = current["source_start"], current["source_end"]
        if kind:
            extra.append(
                {
                    "id": f"audio-change-{len(extra)}",
                    "kind": kind,
                    "modality": "audio",
                    "source_start": a,
                    "source_end": b,
                    "edited_start": current["edited_start"],
                    "edited_end": current["edited_end"],
                    "uncertainty": "Soundtrack correspondence only; does not establish identical images or editorial intent.",
                }
            )
    visual = [
        {**f, "modality": f.get("modality", "visual")}
        for f in evidence["findings"]
        if f.get("modality") != "audio"
    ]
    changes = visual + extra
    lane = (
        evidence["segments"]
        if evidence["coverage"] >= 0.6
        else audio
        if audio_cov >= 0.6
        else []
    )
    matches = [s for s in lane if s["kind"] == "match"]
    review_targets = sorted(
        changes,
        key=lambda f: (f.get("edited_start") is None, f["kind"] != "reordering"),
    )
    # A faithful excerpt also deserves review; no edit finding is required.
    if not review_targets and matches:
        s = max(matches, key=lambda m: m["edited_end"] - m["edited_start"])
        length = min(24, s["edited_end"] - s["edited_start"])
        review_targets = [
            {
                "id": "matched-excerpt",
                "kind": "matched_excerpt",
                "modality": "visual" if evidence["coverage"] >= 0.6 else "audio",
                "source_start": s["source_start"],
                "source_end": s["source_start"] + length,
                "edited_start": s["edited_start"],
                "edited_end": s["edited_start"] + length,
            }
        ]
    return {
        **evidence,
        "findings": changes,
        "comparison_segments": lane,
        "comparison_basis": "visual" if evidence["coverage"] >= 0.6 else "audio_only",
        "audio_coverage": round(audio_cov, 3),
        "review_targets": review_targets[:2],
    }


async def attach_comparison(
    directory, data, evidence, source_path, source_record, *, caption=""
):
    directory = Path(directory)
    evidence = comparison_evidence(evidence)
    evidence["selection_status"] = "matched"
    evidence["source"].update(name=source_record["title"], provenance=source_record)
    if Path(source_path).resolve() != (directory / "original.mp4").resolve():
        shutil.copyfile(source_path, directory / "original.mp4")
    shutil.copyfile(directory / "video.mp4", directory / "edited.mp4")

    try:
        crop_analysis = await run_in_threadpool(
            detect_video_crop, Path(source_path), directory / "edited.mp4"
        )
    except (OSError, ValueError, RuntimeError):
        crop_analysis = {"detected": False, "confidence": 0.0, "omitted_margins": []}

    if crop_analysis.get("detected"):
        crop_finding = {
            "id": "spatial-crop-reframe",
            "kind": "spatial_crop_reframe",
            "modality": "visual",
            "source_start": 0.0,
            "source_end": evidence["source"]["duration"],
            "edited_start": 0.0,
            "edited_end": evidence["edited"]["duration"],
            "crop_box": crop_analysis.get("crop_box"),
            "area_omitted_fraction": crop_analysis.get("area_omitted_fraction"),
            "omitted_margins": crop_analysis.get("omitted_margins", []),
            "explanation": crop_analysis.get("explanation"),
        }
        evidence["findings"].append(crop_finding)

    await run_in_threadpool(save_evidence, directory, evidence)
    data["matched_source"] = {
        "status": "matched",
        "source_id": evidence["source"]["sha256"],
        "source_name": source_record["title"],
        "coverage": evidence["coverage"],
        "audio_coverage": evidence["audio_coverage"],
        "basis": evidence["comparison_basis"],
        "discovery": source_record.get("discovery", "local_collection"),
        "source_url": source_record.get("asset_url"),
        "investigation_id": directory.name,
        "finding_count": len(evidence["findings"]),
        "findings": evidence["findings"],
        "segments": evidence["segments"],
        "audio_alignment": evidence.get("audio_alignment"),
        "media": evidence["media"],
        "crop_analysis": crop_analysis,
    }
    data["manipulation"] = {
        "status": "Source comparison available",
        "reason": "Measured image and soundtrack correspondences are separate. Edits do not establish deception; inspect bounded semantic evidence below.",
    }
    data["comparison"] = {
        "status": "running",
        "basis": evidence["comparison_basis"],
        "scope": "At most two source/edit windows (each ≤30 seconds); long omitted intervals may be only partly inspected. Not a whole-video truth or authenticity verdict.",
        "reviews": [],
        "measured_findings": evidence["findings"],
        "crop_analysis": crop_analysis,
    }
    for finding in evidence["review_targets"]:
        # Keep the conservative visual alignment status; a separately accepted
        # audio match permits audiovisual inspection, not image authentication.
        target_evidence = {
            **evidence,
            "findings": evidence["findings"]
            + ([finding] if finding not in evidence["findings"] else []),
        }
        try:
            clips = await run_in_threadpool(
                build_pack, directory, target_evidence, finding["id"]
            )
            review = await interpret(
                target_evidence, finding["id"], clips, caption=caption
            )
            data["comparison"]["reviews"].append(
                {"status": "complete", "finding": finding, **review}
            )
        except (ValueError, OSError, httpx.HTTPError) as exc:
            data["comparison"]["reviews"].append(
                {"status": "unavailable", "finding": finding, "error": str(exc)[:300]}
            )
            data["failure_log"].append(
                "Bounded source comparison unavailable; measured evidence retained"
            )
    data["comparison"]["status"] = (
        "complete"
        if data["comparison"]["reviews"]
        and all(x["status"] == "complete" for x in data["comparison"]["reviews"])
        else "partial"
    )
    (directory / "comparison.json").write_text(json.dumps(data["comparison"], indent=2))
    return data
