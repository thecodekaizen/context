"""Build eval/hero-v1: a committed, hash-checked bundle for the cache-qualification hero clip.

Numbers in results.json come from a fresh run of the deterministic pipeline on the
bundled media. They are compared with the values stored at authoring time; any
disagreement aborts the build before anything is written.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from context_core.alignment import analyze
from context_core.crop_detector import detect_video_crop
from context_core.grounded_omissions import grounded_omissions

CASE = ROOT / "data/field-validation/cache-qualification-v1"
MUSE_RUN = ROOT / "data/technical-20261030T140841Z-1e14f9"
REVIEWS = ROOT / "data/domain-reviews"
OUT = ROOT / "eval/hero-v1"
SAM_KEEP = [
    "result.json",
    "parsed.json",
    "request-identity.json",
    "input.png",
    "prediction.png",
]
MUSE_DROP = {"id", "store", "background", "instructions"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def probe(path):
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height:format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    data = json.loads(out)
    stream = data["streams"][0]
    return {
        "width": stream["width"],
        "height": stream["height"],
        "duration_seconds": round(float(data["format"]["duration"]), 3),
    }


def sanitized_muse():
    raw = json.loads(
        (MUSE_RUN / "context/audio-change-0/provider-response.json").read_text()
    )
    text = next(
        part["text"]
        for item in raw["output"]
        if item.get("type") == "message"
        for part in item["content"]
        if part.get("type") == "output_text"
    )
    review = json.loads(text)
    created = datetime.fromtimestamp(raw["created_at"], UTC)
    return (
        raw,
        review,
        {
            "model": raw["model"],
            "created_utc": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": raw["status"],
            "usage": {
                k: raw["usage"][k]
                for k in ("input_tokens", "output_tokens", "total_tokens")
            },
            "stripped": [
                "response id",
                "reasoning/message item ids",
                "reasoning item",
                "headers",
                "api key",
            ],
            "live_call_made_during_bundle_build": False,
            "input_media_sha256": {
                "source": digest(MUSE_RUN / "original.mp4"),
                "edited": digest(MUSE_RUN / "edited.mp4"),
            },
            "interpretation": review,
        },
    )


def main():
    case = json.loads((CASE / "case-manifest.json").read_text())
    expected_case = next(c for c in case["cases"] if c["file"] == "omission.mp4")
    crop_case = next(c for c in case["cases"] if c["file"] == "crop.mp4")
    source, omission, crop = (
        CASE / "source.mp4",
        CASE / "omission.mp4",
        CASE / "crop.mp4",
    )

    # Fresh deterministic run.
    evidence = analyze(source, omission)
    omissions = grounded_omissions(evidence)["omissions"]
    crop_fresh = detect_video_crop(source, crop)
    omission_crop = detect_video_crop(source, omission)

    # Compare with values stored at authoring time (case manifest + the saved app run).
    stored_run = json.loads((MUSE_RUN / "evidence.json").read_text())
    stored_om = [
        (f["source_start"], f["source_end"])
        for f in stored_run["findings"]
        if f.get("kind") == "omission"
    ]
    fresh_om = [(o["source_start"], o["source_end"]) for o in omissions]
    expected = [tuple(x) for x in expected_case["expected_omissions"]]
    stored_box = crop_case["retained_box"]
    fresh_box = [crop_fresh["crop_box"][k] for k in ("x", "y", "width", "height")]
    problems = []
    if fresh_om != stored_om or fresh_om != expected:
        problems.append(
            f"omission intervals: fresh={fresh_om} stored_run={stored_om} case_manifest={expected}"
        )
    if fresh_box != stored_box:
        problems.append(f"crop box: fresh={fresh_box} case_manifest={stored_box}")
    if omissions and omissions[0]["edit_position"] != expected_case["edit_position"]:
        problems.append(
            f"edit position: fresh={omissions[0]['edit_position']} case_manifest={expected_case['edit_position']}"
        )
    if problems:
        sys.exit(
            "STORED vs FRESH DISAGREE, nothing written:\n  " + "\n  ".join(problems)
        )

    _raw_muse, review, muse_doc = sanitized_muse()
    if muse_doc["input_media_sha256"] != {
        "source": digest(source),
        "edited": digest(omission),
    }:
        sys.exit("Muse run inputs are not the bundled hero files; nothing written")
    sam = json.loads((CASE / "sam-panel/result.json").read_text())

    first = review["observations"][0]["text"]
    panel_text = (
        [s.strip() for s in first.split("displaying", 1)[1].split(",")]
        if "displaying" in first
        else []
    )
    found = omissions[0]
    boundary = [
        abs(found["source_start"] - expected[0][0]),
        abs(found["source_end"] - expected[0][1]),
    ]

    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ("media", "domain-reviews", "muse", "sam"):
        (OUT / sub).mkdir(parents=True)
    for name, path in (
        ("source.mp4", source),
        ("edited.mp4", omission),
        ("crop.mp4", crop),
    ):
        shutil.copyfile(path, OUT / "media" / name)
    for path in (source, omission, crop):
        shutil.copyfile(
            REVIEWS / f"{digest(path)}.json",
            OUT / "domain-reviews" / f"{digest(path)}.json",
        )
    for name in SAM_KEEP:
        shutil.copyfile(CASE / "sam-panel" / name, OUT / "sam" / name)
    (OUT / "muse/response.json").write_text(json.dumps(muse_doc, indent=2) + "\n")

    results = {
        "scope": case["scope"]
        + " Scripted cut of an authored clip, not field footage.",
        "source_duration_seconds": probe(source)["duration_seconds"],
        "edited_duration_seconds": probe(omission)["duration_seconds"],
        "omission": {
            "expected_interval_seconds": list(expected[0]),
            "detected_interval_seconds": [found["source_start"], found["source_end"]],
            "expected_edit_position_seconds": expected_case["edit_position"],
            "detected_edit_position_seconds": found["edit_position"],
            "boundary_error_seconds": boundary,
            "mean_boundary_error_seconds": sum(boundary) / 2,
            "evidence_modality": found["matched_evidence"]["modality"],
            "pipeline_status_before_audio_grounding": evidence["status"],
        },
        "crop": {
            "source_resolution": list(crop_fresh["source_resolution"]),
            "edited_resolution": list(crop_fresh["edited_resolution"]),
            "retained_box_xywh": fresh_box,
            "area_retained_fraction": crop_fresh["area_retained_fraction"],
            "area_omitted_fraction": crop_fresh["area_omitted_fraction"],
            "omitted_margins": crop_fresh["omitted_margins"],
            "detector": "OpenCV geometry (not SAM)",
            "omission_clip_crop_detected": omission_crop["detected"],
        },
        "muse": {
            "model": muse_doc["model"],
            "created_utc": muse_doc["created_utc"],
            "classification": review["classification"],
            "disclaimer_text_read": panel_text,
            "disclaimer_observation_verbatim": first,
            "disclaimer_seen_in": "source excerpt only (sampled frames)",
            "possible_effect": review["possible_effect"],
            "uncertainty": review["uncertainty"],
            "saved_response": "muse/response.json (saved, not re-run)",
        },
        "sam": {
            "model": sam["model"],
            "prompt": sam["prompt"],
            "frame_seconds": sam["frame_seconds"],
            "mask_count": sam["mask_count"],
            "panel_pixel_recall": sam["panel_pixel_recall"],
            "panel_iou": sam["panel_iou"],
            "passed": sam["passed"],
            "note": "Zero masks on the hero clip: SAM 3.1 contributes nothing here. Experimental.",
        },
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    ffmpeg = subprocess.run(
        ["ffmpeg", "-version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    manifest = {
        "bundle": "hero-v1",
        "clip": "Authored Python cache-qualification illustration (actual local Python timings)",
        "license": case["license"],
        "source_of_raw_clip": "Generated by scripts/build_cache_qualification_case.py; authored by the builder, no third-party footage.",
        "media": {
            "source.mp4": {**probe(source), "role": "raw recording"},
            "edited.mp4": {
                **probe(omission),
                "role": "edited highlight",
                "cut_intervals_seconds": [list(x) for x in expected],
            },
            "crop.mp4": {
                **probe(crop),
                "role": "spatial crop control",
                "crop_box_xywh": stored_box,
            },
        },
        "ffmpeg": ffmpeg,
        "python_pipeline_code": "backend/context_core (alignment, grounded_omissions, crop_detector)",
        "built_by": "scripts/build_hero_bundle.py",
        "files_sha256": {str(p.relative_to(OUT)): digest(p) for p in files},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(results["omission"]),
        json.dumps(results["crop"]["retained_box_xywh"]),
    )


if __name__ == "__main__":
    main()
