"""Author a disclosed cache-qualification case, separate from frozen evaluation.

Actual local Python timings are rendered as an illustrative recording. Synthetic
diagnostic audio assists alignment; it is not speech or an end-user workload.
This script creates media and labels, never content-admission receipts.
"""

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.media import digest

WIDTH, HEIGHT, FPS, DURATION = 1280, 720, 4, 18
PANEL = (960, 120, 1250, 610)


def font(size):
    candidates = [
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise RuntimeError("Install a TrueType sans font before rendering this case")


def command(*args):
    subprocess.run(args, check=True)


def measure():
    rows = []
    for index in range(FPS * DURATION):
        key = f"controlled-cache-key-{index}".encode()
        started = time.perf_counter_ns()
        value = hashlib.pbkdf2_hmac("sha256", key, b"demo-only", 12000)
        cold_ns = time.perf_counter_ns() - started
        cache = {key: value}
        repeats = 10000
        started = time.perf_counter_ns()
        for _ in range(repeats):
            cached = cache[key]
        warm_ns = (time.perf_counter_ns() - started) / repeats
        assert cached == value
        rows.append({"batch": index + 1, "cold_ns": cold_ns, "warm_ns": warm_ns})
    return rows


def frame(index, rows):
    im = Image.new("RGB", (WIDTH, HEIGHT), "#07090e")
    draw = ImageDraw.Draw(im)

    def text(x, y, value, size=24, color="#e6edf3"):
        draw.text((x, y), value, font=font(size), fill=color)

    elapsed = index / FPS
    row = rows[index]
    text(32, 25, "CACHE LOOKUP LATENCY", 34)
    text(
        32,
        75,
        "Authored technical demonstration · actual local Python timings",
        21,
        "#9aaabb",
    )
    draw.rounded_rectangle(
        (32, 120, 930, 610), radius=12, fill="#0d1117", outline="#293344"
    )
    text(60, 145, "Measured lookup", 25, "#38bdf8")
    text(60, 190, f"{row['warm_ns'] / 1000:.3f} µs", 58)
    text(60, 270, "Per dictionary read · 10,000 repeated reads / batch", 22, "#aab8c8")
    # Each bar is a real measured batch, not invented performance data.
    history = rows[: index + 1]
    scale = max(r["warm_ns"] for r in rows)
    for n, result in enumerate(history):
        height = round(170 * result["warm_ns"] / scale)
        x = 60 + n * 11
        draw.rectangle((x, 520 - height, x + 7, 520), fill="#38bdf8")
    text(60, 550, f"Batch {index + 1:02d} / 72     source clock {elapsed:06.2f} s", 24)
    draw.rounded_rectangle(PANEL, radius=12, fill="#141824", outline="#57657a")
    qualified = 6 <= elapsed < 10
    text(980, 145, "TEST CONDITIONS", 23, "#fbbf24")
    if qualified:
        for y, line in zip(
            (210, 250, 310, 350, 415, 455),
            (
                "WARM CACHE ONLY",
                "Cache pre-populated",
                "COLD-START SETUP",
                "IS EXCLUDED",
                "Not an end-to-end",
                "speedup claim",
            ),
        ):
            text(980, y, line, 23, "#fbbf24")
        cold_ms = statistics.median(r["cold_ns"] for r in rows) / 1e6
        text(980, 535, f"Cold setup: {cold_ms:.2f} ms", 20)
    else:
        for y, line in zip(
            (210, 250, 310, 350, 410),
            (
                "Python dictionary",
                "Single local process",
                "Measured on this",
                "machine only",
                "See test conditions",
            ),
        ):
            text(980, y, line, 22)
    text(
        32,
        640,
        "CONTROLLED CASE · synthetic diagnostic tone, no speech · no commercial product claim",
        20,
        "#aab8c8",
    )
    draw.rectangle(
        (32, 685, 32 + round(1216 * (index + 1) / len(rows)), 693), fill="#10b981"
    )
    return im


def build(output):
    output.mkdir(parents=True, exist_ok=False)
    frames = output / "frames"
    frames.mkdir()
    rows = measure()
    (output / "measurements.json").write_text(json.dumps(rows, indent=2))
    for index in range(len(rows)):
        frame(index, rows).save(frames / f"{index:03}.png")
    source = output / "source.mp4"
    command(
        "ffmpeg",
        "-v",
        "error",
        "-n",
        "-framerate",
        str(FPS),
        "-i",
        str(frames / "%03d.png"),
        "-f",
        "lavfi",
        "-i",
        "aevalsrc=0.06*sin(2*PI*(137*t+19*t*t+2*sin(5*t))):s=16000:d=18",
        "-t",
        str(DURATION),
        "-r",
        "24",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(source),
    )
    omission = output / "omission.mp4"
    command(
        "ffmpeg",
        "-v",
        "error",
        "-n",
        "-i",
        str(source),
        "-filter_complex",
        "[0:v]trim=0:6,setpts=PTS-STARTPTS[v0];[0:a]atrim=0:6,asetpts=PTS-STARTPTS[a0];"
        "[0:v]trim=10:18,setpts=PTS-STARTPTS[v1];[0:a]atrim=10:18,asetpts=PTS-STARTPTS[a1];"
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(omission),
    )
    crop = output / "crop.mp4"
    command(
        "ffmpeg",
        "-v",
        "error",
        "-n",
        "-i",
        str(source),
        "-vf",
        "crop=960:720:0:0",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(crop),
    )
    # Ground truth is fixed here before model calls. Never pass labels to retrieval.
    manifest = {
        "scope": "Authored cache-qualification illustration, actual Python microtimings; not independent field evaluation or commercial performance proof.",
        "license": "CC0-1.0 for authored case media and labels",
        "source": {"file": source.name, "sha256": digest(source), "duration": DURATION},
        "cases": [
            {
                "file": omission.name,
                "sha256": digest(omission),
                "expected_omissions": [[6, 10]],
                "edit_position": 6,
            },
            {
                "file": crop.name,
                "sha256": digest(crop),
                "expected_omissions": [],
                "retained_box": [0, 0, 960, 720],
            },
            {
                "file": source.name,
                "sha256": digest(source),
                "expected_omissions": [],
                "control": "byte-identical source",
            },
        ],
        "qualification": {
            "source_interval": [6, 10],
            "panel_box": list(PANEL),
            "text": "WARM CACHE ONLY; COLD-START SETUP IS EXCLUDED; Not an end-to-end speedup claim",
        },
        "sam_test": {
            "frame_seconds": 7,
            "prompt": "right-side test conditions panel",
            "minimum_panel_recall": 0.7,
            "minimum_iou": 0.5,
        },
        "disclosures": [
            "No speech or people",
            "Synthetic tone assists acoustic alignment",
            "72 actual timing batches rendered at 4 Hz and encoded at 24 fps",
            "Model interpretation not supplied or pre-scripted",
            "No domain admission is created automatically",
        ],
    }
    (output / "case-manifest.json").write_text(json.dumps(manifest, indent=2))
    # Contact sheets contain every unique authored frame for full visual review.
    for start in range(0, len(rows), 18):
        sheet = Image.new("RGB", (1280, 1080), "#07090e")
        for n in range(start, min(start + 18, len(rows))):
            thumbnail = frame(n, rows).resize((426, 240))
            x, y = (n - start) % 3 * 426, (n - start) // 3 * 180
            thumbnail = thumbnail.resize((320, 180))
            sheet.paste(thumbnail, (x, y))
        sheet.save(output / f"review-{start // 18:02}.jpg")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
