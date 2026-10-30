"""Hero demo served only from the committed eval/hero-v1 bundle (no keys, no pipeline run)."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "eval/hero-v1"
MEDIA = {"source": "source.mp4", "edited": "edited.mp4", "crop": "crop.mp4"}

router = APIRouter()


def _load(relative):
    path = BUNDLE / relative
    if not path.is_file():
        raise HTTPException(404, "Hero bundle is not present in this build")
    return json.loads(path.read_text())


def hero_evidence():
    results = _load("results.json")
    manifest = _load("manifest.json")
    muse = _load("muse/response.json")
    cut = results["omission"]["detected_interval_seconds"]
    position = results["omission"]["detected_edit_position_seconds"]
    source_length = results["source_duration_seconds"]
    edited_length = results["edited_duration_seconds"]
    crop = results["crop"]
    x, y, width, height = crop["retained_box_xywh"]
    hashes = manifest["files_sha256"]

    def match(identifier, source, edited):
        return {
            "id": identifier,
            "kind": "match",
            "source_start": source[0],
            "source_end": source[1],
            "edited_start": edited[0],
            "edited_end": edited[1],
            "confidence": None,
        }

    lane = [
        match("hero-before", [0.0, cut[0]], [0.0, position]),
        match("hero-after", [cut[1], source_length], [position, edited_length]),
    ]
    omission = {
        "id": "hero-omission",
        "kind": "omission",
        "modality": results["omission"]["evidence_modality"],
        "source_start": cut[0],
        "source_end": cut[1],
        "edited_start": position,
        "edited_end": position,
    }
    crop_finding = {
        "id": "hero-crop",
        "kind": "spatial_crop_reframe",
        "modality": "visual",
        "source_start": 0.0,
        "source_end": source_length,
        "edited_start": 0.0,
        "edited_end": source_length,
        "crop_box": {"x": x, "y": y, "width": width, "height": height},
        "area_omitted_fraction": crop["area_omitted_fraction"],
        "omitted_margins": crop["omitted_margins"],
        "explanation": f"Retained box {[x, y, width, height]} of the {crop['source_resolution']} frame (geometry, not SAM).",
    }
    base = "/api/demo/hero/media"
    return {
        "id": "hero-v1",
        "status": "matched",
        "coverage": edited_length / source_length,
        "source": {
            "duration": source_length,
            "sha256": hashes["media/source.mp4"],
            "name": "cache-qualification-source.mp4",
            "provenance": {
                "attribution": manifest["clip"],
                "license": manifest["license"],
                "url": "eval/hero-v1/manifest.json",
                "transformations": manifest["source_of_raw_clip"],
            },
        },
        "edited": {
            "duration": edited_length,
            "sha256": hashes["media/edited.mp4"],
        },
        "media": {
            "source": f"{base}/source",
            "edited": f"{base}/edited",
            "crop": f"{base}/crop",
        },
        "segments": lane,
        "audio_alignment": {"status": "analyzed", "segments": lane},
        "findings": [omission, crop_finding],
        "omission_evidence": {
            "status": "grounded",
            "omissions": [
                {
                    "source_start": cut[0],
                    "source_end": cut[1],
                    "edit_position": position,
                    "confidence": None,
                    "matched_evidence": {"modality": omission["modality"]},
                    "explanation": None,
                }
            ],
        },
        "crop_analysis": {
            "detected": True,
            "confidence": None,
            "crop_box": crop_finding["crop_box"],
            "source_resolution": crop["source_resolution"],
            "edited_resolution": crop["edited_resolution"],
            "area_retained_fraction": crop["area_retained_fraction"],
            "area_omitted_fraction": crop["area_omitted_fraction"],
            "omitted_margins": crop["omitted_margins"],
        },
        "limitations": [
            results["scope"],
            "Visual-only matching was insufficient; the omission is evidenced by audio alignment.",
        ],
        "recorded_response": {
            "label": "recorded response",
            "note": "Saved Muse output from eval/hero-v1/muse/response.json; not a live call.",
            "created_utc": muse["created_utc"],
            "review": {
                "cached": True,
                "recorded": True,
                "model": muse["model"],
                "finding_id": omission["id"],
                "interpretation": {
                    "classification": muse["interpretation"]["classification"],
                    "observations": [
                        {"text": o["text"], "citations": []}
                        for o in muse["interpretation"]["observations"]
                    ],
                    "possible_effect": muse["interpretation"]["possible_effect"],
                    "uncertainty": muse["interpretation"]["uncertainty"],
                },
            },
        },
    }


@router.post("/api/demo/hero")
def hero_demo():
    return hero_evidence()


@router.get("/api/demo/hero/media/{name}")
def hero_media(name: str):
    if name not in MEDIA:
        raise HTTPException(404)
    path = BUNDLE / "media" / MEDIA[name]
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path, media_type="video/mp4")
