"""Test SAM on the predeclared cache panel; persist real masks and all failures.

Standalone single-frame experiment, not operational tracking or a semantic verdict.
Requires reviewed source bytes. Only the image and concept prompt go to SAM.
"""

import argparse
import base64
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

import httpx
import numpy as np
from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "data/execution-gates/tools"))
from context_core.crop_detector import extract_frame
from context_core.domain_policy import require_files
from context_core.media import digest


def evaluate(directory, *, replay=False):
    from meta_sam_parser import (
        CompletedOutcome,
        decode_mask_to_raster,
        image_segmentation_format,
    )

    manifest_path = directory / "case-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    source = directory / manifest["source"]["file"]
    require_files({"source": source})
    if digest(source) != manifest["source"]["sha256"]:
        raise ValueError("Case source bytes changed")
    output = directory / "sam-panel"
    output.mkdir(exist_ok=True)
    test = manifest["sam_test"]
    pixels = extract_frame(source, test["frame_seconds"])
    frame_path = output / "input.png"
    Image.fromarray(pixels).save(frame_path)
    identity = {
        "manifest_sha256": digest(manifest_path),
        "source_sha256": digest(source),
        "input_sha256": digest(frame_path),
        "frame_seconds": test["frame_seconds"],
        "prompt": test["prompt"],
        "model": "sam-3.1",
    }
    identity_path = output / "request-identity.json"
    if identity_path.exists() and json.loads(identity_path.read_text()) != identity:
        raise ValueError("Existing SAM run belongs to different inputs or labels")
    identity_path.write_text(json.dumps(identity, indent=2))
    events_path = output / "events.json"
    if events_path.exists() and not replay:
        raise ValueError("A run exists; use --replay or a new case directory")
    report = {
        **identity,
        "scope": "One authored panel in one frame; no tracking, OCR, semantic effect or production integration claim.",
        "replay": replay,
        "passed": False,
    }
    events = []
    started = time.monotonic()
    try:
        if replay:
            events = json.loads(events_path.read_text())
        else:
            load_dotenv(ROOT / ".env")
            body = {
                "model": "sam-3.1",
                "stream": True,
                "metadata": {"mask_encoding": "one_bit"},
                "input": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": test["prompt"]},
                            {
                                "type": "input_image",
                                "image_url": "data:image/png;base64,"
                                + base64.b64encode(frame_path.read_bytes()).decode(),
                            },
                        ],
                    }
                ],
            }
            with (
                httpx.Client(timeout=120) as client,
                client.stream(
                    "POST",
                    "https://api.meta.ai/v1/responses",
                    headers={"Authorization": "Bearer " + os.environ["MODEL_API_KEY"]},
                    json=body,
                ) as response,
            ):
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data:") and line[5:].strip() != "[DONE]":
                        events.append(json.loads(line[5:].strip()))
        parser = image_segmentation_format().create_parser()
        completed = False
        for event in events:
            if event["type"] == "response.output_text.delta":
                parser.push(event["delta"])
            if event["type"] == "response.completed":
                completed = True
        if not completed:
            raise ValueError("SAM response did not complete")
        parsed = parser.finish(CompletedOutcome()).result
        if any(d.severity == "error" for d in parsed.diagnostics):
            raise ValueError("Malformed SAM mask response")
        (output / "parsed.json").write_text(json.dumps(asdict(parsed), indent=2))
        predicted = np.zeros(pixels.shape[:2], dtype=bool)
        masks = [r for r in parsed.records if r.kind == "mask"]
        for record in masks:
            raster = np.frombuffer(
                decode_mask_to_raster(record.mask), dtype="uint8"
            ).reshape(record.mask.height, record.mask.width)
            bounds = record.bounds
            left, top, right, bottom = [
                round(v) for v in (bounds.left, bounds.top, bounds.right, bounds.bottom)
            ]
            if not (
                0 <= left < right <= pixels.shape[1]
                and 0 <= top < bottom <= pixels.shape[0]
            ):
                raise ValueError("Mask bounds outside input frame")
            resized = (
                np.asarray(
                    Image.fromarray(raster).resize(
                        (right - left, bottom - top), Image.Resampling.NEAREST
                    )
                )
                > 0
            )
            predicted[top:bottom, left:right] |= resized
        truth = np.zeros_like(predicted)
        left, top, right, bottom = manifest["qualification"]["panel_box"]
        truth[top:bottom, left:right] = True
        intersection = int((predicted & truth).sum())
        recall = intersection / int(truth.sum())
        union = int((predicted | truth).sum())
        iou = intersection / union if union else 0
        # The crop is exactly x=0..960 in source pixels; label used only in scoring.
        removed = (
            predicted[:, 960:].sum() / predicted.sum() if predicted.any() else None
        )
        Image.fromarray((predicted * 255).astype("uint8")).save(
            output / "prediction.png"
        )
        overlay = pixels.copy()
        overlay[predicted] = (
            0.55 * pixels[predicted] + 0.45 * np.array([244, 63, 94])
        ).astype("uint8")
        Image.fromarray(overlay).save(output / "overlay.png")
        report.update(
            mask_count=len(masks),
            panel_pixel_recall=recall,
            panel_iou=iou,
            predicted_mask_fraction_outside_retained_crop=float(removed)
            if removed is not None
            else None,
            passed=recall >= test["minimum_panel_recall"]
            and iou >= test["minimum_iou"],
        )
    except (httpx.HTTPError, ValueError, OSError, KeyError) as exc:
        report["error"] = str(exc)[:400]
    finally:
        if not replay:
            events_path.write_text(json.dumps(events, indent=2))
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        (output / ("replay-result.json" if replay else "result.json")).write_text(
            json.dumps(report, indent=2)
        )
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    raise SystemExit(evaluate(args.directory, replay=args.replay))
