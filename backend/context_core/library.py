"""Disk-backed local collection. Index once; decode an edit once per search."""

import json
import shutil
from pathlib import Path

import numpy as np

from .alignment import align_samples
from .media import VideoSamples, sample

MAX_SOURCES = 20
MIN_COVERAGE = 0.6
MIN_MARGIN = 0.08


def list_sources(root):
    root = Path(root)
    return [json.loads(p.read_text()) for p in sorted(root.glob("*/metadata.json"))]


def add_source(root, path, name):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    samples = sample(path)
    identifier = samples.sha256
    directory = root / identifier
    if (directory / "metadata.json").exists():
        return json.loads((directory / "metadata.json").read_text())
    if len(list_sources(root)) >= MAX_SOURCES:
        raise ValueError(f"The local collection supports up to {MAX_SOURCES} sources")
    directory.mkdir(exist_ok=True)
    try:
        shutil.copyfile(path, directory / "original.mp4")
        np.savez_compressed(
            directory / "features.npz", times=samples.times, frames=samples.frames
        )
        metadata = {
            "id": identifier,
            "name": Path(name).name[:120] or "Untitled source",
            "sha256": identifier,
            **samples.info,
        }
        temporary = directory / "metadata.tmp"
        temporary.write_text(json.dumps(metadata, indent=2))
        temporary.replace(directory / "metadata.json")
        return metadata
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise


def rank_sources(root, edited):
    sources = list_sources(root)
    if not sources:
        raise ValueError("Add an original recording to the local collection first")
    edited_samples = sample(edited)
    candidates = []
    results = {}
    for meta in sources:
        with np.load(
            Path(root) / meta["id"] / "features.npz", allow_pickle=False
        ) as cached:
            original_samples = VideoSamples(
                {k: v for k, v in meta.items() if k not in {"id", "name", "sha256"}},
                cached["times"],
                cached["frames"],
                meta["sha256"],
            )
        evidence = align_samples(original_samples, edited_samples)
        matched = [s for s in evidence["segments"] if s["kind"] == "match"]
        duration = sum(s["edited_end"] - s["edited_start"] for s in matched)
        quality = (
            sum(
                s["confidence"] * (s["edited_end"] - s["edited_start"]) for s in matched
            )
            / duration
            if duration
            else 0
        )
        score = evidence["coverage"] * (0.8 + 0.2 * quality)
        candidates.append(
            {
                "id": meta["id"],
                "name": meta["name"],
                "coverage": evidence["coverage"],
                "score": round(score, 4),
            }
        )
        results[meta["id"]] = evidence
    candidates.sort(key=lambda c: c["score"], reverse=True)
    top = candidates[0]
    margin = (
        top["score"] - candidates[1]["score"] if len(candidates) > 1 else top["score"]
    )
    status = (
        "matched"
        if top["coverage"] >= MIN_COVERAGE and margin >= MIN_MARGIN
        else "ambiguous"
        if top["coverage"] >= MIN_COVERAGE
        else "no_match"
    )
    # Low visual coverage is common in static speaking shots. Compare soundtrack
    # evidence independently across candidates rather than suppressing it behind
    # an arbitrary minimum visual score. Ties remain ambiguous; images stay unverified.
    audio_candidates = []
    if status != "matched" and edited_samples.info.get("has_audio"):
        from .audio_alignment import analyze_audio

        for candidate in candidates[:3]:
            meta = next(m for m in sources if m["id"] == candidate["id"])
            if not meta.get("has_audio"):
                continue
            try:
                audio_result = analyze_audio(
                    Path(root) / meta["id"] / "original.mp4", edited
                )
                intervals = sorted(
                    (x["edited_start"], x["edited_end"])
                    for x in audio_result["segments"]
                )
                duration = 0.0
                right = 0.0
                for left, end in intervals:
                    duration += max(0.0, end - max(left, right))
                    right = max(right, end)
                audio_cov = duration / edited_samples.info["duration"]
                audio_candidates.append((audio_cov, candidate))
                results[candidate["id"]]["audio_alignment"] = {
                    "status": "analyzed",
                    **audio_result,
                }
            except (ValueError, OSError) as exc:
                results[candidate["id"]]["audio_alignment"] = {
                    "status": "unavailable",
                    "segments": [],
                    "reason": str(exc)[:300],
                }
        audio_candidates.sort(key=lambda x: x[0], reverse=True)
        if audio_candidates and audio_candidates[0][0] >= MIN_COVERAGE:
            audio_cov, audio_top = audio_candidates[0]
            audio_margin = audio_cov - (
                audio_candidates[1][0] if len(audio_candidates) > 1 else 0
            )
            if audio_margin >= MIN_MARGIN:
                top = audio_top
                candidates = [top] + [x for x in candidates if x["id"] != top["id"]]
                margin = audio_margin
                status = "matched"
                results[top["id"]]["multimodal_coverage"] = round(audio_cov, 3)
            else:
                status = "ambiguous"
    if status == "matched" and "audio_alignment" not in results[top["id"]]:
        meta = next(m for m in sources if m["id"] == top["id"])
        if meta.get("has_audio") and edited_samples.info.get("has_audio"):
            from .audio_alignment import analyze_audio

            try:
                results[top["id"]]["audio_alignment"] = {
                    "status": "analyzed",
                    **analyze_audio(Path(root) / top["id"] / "original.mp4", edited),
                }
            except (ValueError, OSError) as exc:
                results[top["id"]]["audio_alignment"] = {
                    "status": "unavailable",
                    "segments": [],
                    "reason": str(exc)[:300],
                }
    report = {
        "status": status,
        "scope": "provided_local_collection",
        "selection_basis": "audio_correspondence"
        if results[top["id"]].get("multimodal_coverage")
        else "visual_correspondence",
        "candidates": candidates,
        "margin": round(margin, 4),
        "minimum_margin": MIN_MARGIN,
        "minimum_coverage": MIN_COVERAGE,
    }
    return report, results[top["id"]] if status == "matched" else None
