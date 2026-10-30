"""Ten frozen screen-content crops; concept prompts only, no truth masks sent."""

import argparse
import base64
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

import httpx
import numpy as np
from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.media import digest, run

BASE = ROOT / "eval/execution-v1/sam-gate"


def prepare():
    BASE.mkdir(exist_ok=True)
    if (BASE / "manifest.json").exists():
        raise ValueError("SAM labels already frozen")
    cases = []
    for index in range(10):
        source = (
            ROOT
            / "eval/execution-v1/sources"
            / f"{['sort', 'cache', 'serialize'][index % 3]}.mp4"
        )
        image = BASE / f"crop-{index:02}.png"
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-n",
                "-ss",
                str(2 + index),
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-vf",
                "crop=840:460:0:140",
                str(image),
            ]
        )
        pixels = np.asarray(Image.open(image).convert("RGB")).astype(int)
        truth = (
            (pixels[:, :, 1] > 140)
            & (pixels[:, :, 1] - pixels[:, :, 0] > 45)
            & (pixels[:, :, 1] - pixels[:, :, 2] > 10)
        )
        if truth.sum() < 100:
            raise ValueError("Insufficient chart-bar pixels before inference")
        mask_path = image.with_name(image.stem + "-truth.png")
        Image.fromarray((truth * 255).astype("uint8")).save(mask_path)
        cases.append(
            {
                "image": image.name,
                "sha256": digest(image),
                "truth": mask_path.name,
                "truth_sha256": digest(mask_path),
                "source_sha256": digest(source),
            }
        )
    manifest = {
        "model": "sam-3.1",
        "prompt": "green vertical bars in the bar chart",
        "minimum_pixel_recall": 0.7,
        "minimum_iou": 0.5,
        "minimum_successful_crop_fraction": 0.7,
        "scope": "10 screen-content crops across three controlled JavaScript benchmark recordings, not natural tutorial footage. Color-derived masks from known authored chart bars, frozen before API calls. No boxes or truth masks sent to model. Passing this narrow gate does not validate occlusion or identity tracking.",
        "cases": cases,
    }
    (BASE / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Frozen ten crop masks and pass thresholds before requests")


def evaluate(replay=False):
    sys.path.insert(0, str(ROOT / "data/execution-gates/tools"))
    from meta_sam_parser import (
        CompletedOutcome,
        decode_mask_to_raster,
        image_segmentation_format,
    )

    load_dotenv(ROOT / ".env")
    manifest = json.loads((BASE / "manifest.json").read_text())
    output = BASE / ("rescored-results" if replay else "results")
    output.mkdir(exist_ok=False)
    rows = []
    with httpx.Client(timeout=120) as client:
        for case in manifest["cases"]:
            image_path, truth_path = BASE / case["image"], BASE / case["truth"]
            if (
                digest(image_path) != case["sha256"]
                or digest(truth_path) != case["truth_sha256"]
            ):
                raise ValueError("Frozen SAM input or label changed")
            body = {
                "model": manifest["model"],
                "stream": True,
                "metadata": {"mask_encoding": "one_bit"},
                "input": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": manifest["prompt"]},
                            {
                                "type": "input_image",
                                "image_url": "data:image/png;base64,"
                                + base64.b64encode(image_path.read_bytes()).decode(),
                            },
                        ],
                    }
                ],
            }
            parser = image_segmentation_format().create_parser()
            events = []
            completed = False
            row = {"image": case["image"], "passed": False}
            try:
                if replay:
                    events = json.loads(
                        (
                            BASE / "results" / (image_path.stem + "-events.json")
                        ).read_text()
                    )
                    for event in events:
                        if event["type"] == "response.output_text.delta":
                            parser.push(event["delta"])
                        if event["type"] == "response.completed":
                            completed = True
                else:
                    with client.stream(
                        "POST",
                        "https://api.meta.ai/v1/responses",
                        headers={
                            "Authorization": "Bearer " + os.environ["MODEL_API_KEY"]
                        },
                        json=body,
                    ) as response:
                        response.raise_for_status()
                        for line in response.iter_lines():
                            if (
                                line.startswith("data:")
                                and line[5:].strip() != "[DONE]"
                            ):
                                event = json.loads(line[5:].strip())
                                events.append(event)
                                if event["type"] == "response.output_text.delta":
                                    parser.push(event["delta"])
                                if event["type"] == "response.completed":
                                    completed = True
                if not completed:
                    raise ValueError("SAM stream did not complete")
                parsed = parser.finish(CompletedOutcome()).result
                if any(item.severity == "error" for item in parsed.diagnostics):
                    raise ValueError("Malformed SAM mask output")
                truth = np.asarray(Image.open(truth_path)) > 0
                predicted = np.zeros(truth.shape, dtype=bool)
                masks = [record for record in parsed.records if record.kind == "mask"]
                for record in masks:
                    raster = np.frombuffer(
                        decode_mask_to_raster(record.mask), dtype="uint8"
                    ).reshape(record.mask.height, record.mask.width)
                    bounds = record.bounds
                    left, top, right, bottom = (
                        round(value)
                        for value in (
                            bounds.left,
                            bounds.top,
                            bounds.right,
                            bounds.bottom,
                        )
                    )
                    if (
                        not 0 <= left < right <= truth.shape[1]
                        or not 0 <= top < bottom <= truth.shape[0]
                    ):
                        raise ValueError("SAM mask bounds outside crop")
                    resized = (
                        np.asarray(
                            Image.fromarray(raster).resize(
                                (right - left, bottom - top), Image.Resampling.NEAREST
                            )
                        )
                        > 0
                    )
                    predicted[top:bottom, left:right] |= resized
                intersection = int((truth & predicted).sum())
                recall = intersection / int(truth.sum())
                union = int((truth | predicted).sum())
                overlap = intersection / union if union else 0
                row.update(
                    pixel_recall=recall,
                    iou=overlap,
                    mask_count=len(masks),
                    passed=recall >= manifest["minimum_pixel_recall"]
                    and overlap >= manifest["minimum_iou"],
                )
                Image.fromarray((predicted * 255).astype("uint8")).save(
                    output / (image_path.stem + "-prediction.png")
                )
                (output / (image_path.stem + "-parsed.json")).write_text(
                    json.dumps(asdict(parsed), indent=2)
                )
            except (httpx.HTTPError, ValueError) as error:
                row["error"] = str(error)[:300]
            (output / (image_path.stem + "-events.json")).write_text(
                json.dumps(events, indent=2)
            )
            rows.append(row)
            print(json.dumps(row), flush=True)
            report = {
                "manifest_sha256": digest(BASE / "manifest.json"),
                "scope": manifest["scope"],
                "cases": rows,
                "successful_crop_fraction": sum(item["passed"] for item in rows) / 10,
                "passed": len(rows) == 10
                and sum(item["passed"] for item in rows) / 10
                >= manifest["minimum_successful_crop_fraction"],
            }
            (output / "results.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "run", "replay"])
    args = parser.parse_args()
    prepare() if args.action == "prepare" else evaluate(args.action == "replay")
