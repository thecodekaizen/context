"""Reproducible transformations and measured alignment, no inference ground truth input.
Run: PYTHONPATH=backend .venv/bin/python scripts/evaluate.py [--download]
"""

import argparse
import json
import sys
import zipfile
from pathlib import Path

import httpx
from context_core.alignment import analyze
from context_core.media import digest, run

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/evaluation"
URL = "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip"


def download():
    DATA.mkdir(parents=True, exist_ok=True)
    archive = DATA / "blender.zip"
    if not archive.exists():
        with httpx.stream("GET", URL, timeout=120, follow_redirects=True) as r:
            r.raise_for_status()
            with archive.open("wb") as out:
                for block in r.iter_bytes():
                    out.write(block)
    original = DATA / "blender.mp4"
    if not original.exists():
        with zipfile.ZipFile(archive) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(".mp4"))
            with z.open(name) as src, original.open("wb") as out:
                import shutil

                shutil.copyfileobj(src, out)
    return original


def generate(original):
    source = DATA / "source.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            "40",
            "-i",
            str(original),
            "-t",
            "24",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-c:a",
            "aac",
            str(source),
        ]
    )
    recipes = {
        "copy": ([(0, 24)], "null"),
        "omission": ([(0, 8), (14, 24)], "null"),
        "reordered": ([(14, 24), (0, 8), (8, 14)], "null"),
        "repeated": ([(0, 8), (0, 8), (14, 24)], "null"),
        "fractional_trim": ([(2.375, 20.375)], "null"),
        "heavy_compression": ([(0, 24)], "scale=240:134"),
        "brightness": ([(0, 24)], "eq=brightness=0.06"),
        "small_crop": ([(0, 24)], "crop=iw*0.9:ih*0.9,scale=320:180"),
        "overlay": ([(0, 24)], "drawbox=x=10:y=10:w=80:h=20:color=black:t=fill"),
        "speed_change": ([(0, 24)], "setpts=0.8*PTS"),
    }
    for name, (parts, transform) in recipes.items():
        graph = ";".join(
            f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]"
            for i, (a, b) in enumerate(parts)
        )
        graph += (
            ";"
            + "".join(f"[v{i}]" for i in range(len(parts)))
            + f"concat=n={len(parts)}:v=1:a=0,{transform}[out]"
        )
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(source),
                "-filter_complex",
                graph,
                "-map",
                "[out]",
                "-an",
                "-c:v",
                "libx264",
                "-crf",
                "35" if name == "heavy_compression" else "25",
                str(DATA / f"{name}.mp4"),
            ]
        )
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            "200",
            "-i",
            str(original),
            "-t",
            "18",
            "-an",
            "-c:v",
            "libx264",
            str(DATA / "unrelated.mp4"),
        ]
    )
    return source, recipes


def evaluate(source, recipes):
    rows = []
    for name in [*recipes, "unrelated"]:
        result = analyze(source, DATA / f"{name}.mp4")
        matches = [s for s in result["segments"] if s["kind"] == "match"]
        parts = recipes[name][0] if name in recipes else []
        # Score each matched sample against the independently defined edit recipe.
        correct = total = 0
        errors = []
        for segment in matches:
            t = segment["edited_start"]
            while t < segment["edited_end"] - 0.01:
                expected = None
                cursor = 0
                for a, b in parts:
                    if cursor <= t < cursor + b - a:
                        expected = a + (t - cursor) * (
                            1.25 if name == "speed_change" else 1
                        )
                        break
                    cursor += b - a
                predicted = segment["source_start"] + t - segment["edited_start"]
                if expected is not None:
                    err = abs(predicted - expected)
                    errors.append(err)
                    correct += err <= 0.5
                total += 1
                t += 0.25
        rows.append(
            {
                "case": name,
                "status": result["status"],
                "coverage": result["coverage"],
                "findings": [f["kind"] for f in result["findings"]],
                "matched_sample_precision_at_0_5s": round(correct / total, 3)
                if total
                else None,
                "mean_timestamp_error_seconds": round(sum(errors) / len(errors), 3)
                if errors
                else None,
                "supported_transform": name
                not in {"speed_change", "small_crop", "brightness", "overlay"},
            }
        )
    report = {
        "source": "Big Buck Bunny (2008), Blender Foundation",
        "source_url": URL,
        "license": "CC BY 3.0",
        "attribution": "(c) copyright 2008, Blender Foundation / www.bigbuckbunny.org",
        "source_window_seconds": [40, 64],
        "source_sha256": digest(source),
        "scope": "One animated production excerpt with controlled edits; not a broad accuracy benchmark. Audio is excluded from transformed variants. Unsupported transforms are diagnostic stress tests.",
        "results": rows,
    }
    (DATA / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        original = download()
    else:
        original = DATA / "blender.mp4"
        if not original.exists():
            sys.exit("Run once with --download to fetch the licensed Blender source.")
    source, recipes = generate(original)
    evaluate(source, recipes)
