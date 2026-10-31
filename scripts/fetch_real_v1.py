"""Download the eval/real-v1 sources, clip the first 270 s, record hashes and attribution.

Videos go to data/real-v1 (gitignored). Only sources.json is committed.
"""

import json
import subprocess
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.media import digest

OUT = ROOT / "data/real-v1"
SOURCES = ROOT / "eval/real-v1/sources.json"
FRAMES = ROOT / "eval/real-v1/frame_review.json"
CLIP_SECONDS = 270
LICENSE = "CC-BY-2.0-BE"
LICENSE_URL = "http://creativecommons.org/licenses/by/2.0/be/deed.en"
TALKS = [
    ("python_kafka", "Get to know Apache Kafka with Jupyter Notebooks", "Francesco Tisiot"),
    ("python_async_sqlalchemy", "Introducing Asynchronous SQLAlchemy", "Sebastiaan Zeeff"),
    ("python_concurrency_in_webapps", "Handling Concurrency in Web Application", "Haki Benita"),
    ("python_type_safety", "Sleep better with type-safe Python", "Jerry Pussinen"),
    ("python_unicode", "Messing with unicode", "Julin Shaji"),
    ("python_spyql", "SPyQL - SQL with Python in the middle", "Daniel Moura"),
    ("python_mimics", "Mimics - Records operations to replay them later", "Maarten De Paepe"),
    ("python_feature_flags", "Implementing and managing feature flags", "Mehdi Raddadi"),
    ("python_cubicweb", "CubicWeb: bootstraping a web-application from RDF data", "Fabien Amarger"),
]


def probe(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration",
         "-of", "json", str(path)]
    )
    info = json.loads(out)
    return {
        "has_audio": any(s["codec_type"] == "audio" for s in info["streams"]),
        "has_video": any(s["codec_type"] == "video" for s in info["streams"]),
        "duration_seconds": float(info["format"]["duration"]),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = json.loads(FRAMES.read_text()) if FRAMES.exists() else {}
    entries = {}
    for name, title, speaker in TALKS:
        page = f"https://archive.fosdem.org/2022/schedule/event/{name}/"
        url = f"https://video.fosdem.org/2022/D.python/{name}.mp4"
        raw, clip = OUT / f"{name}.raw.mp4", OUT / f"{name}.mp4"
        if not raw.exists():
            urllib.request.urlretrieve(url, raw)
        if not clip.exists():
            subprocess.run(
                ["ffmpeg", "-v", "error", "-n", "-i", str(raw), "-t", str(CLIP_SECONDS),
                 "-c:v", "libx264", "-crf", "22", "-c:a", "aac", "-movflags", "+faststart",
                 str(clip)], check=True)
        frame = OUT / f"{name}.frame.jpg"
        if not frame.exists():
            subprocess.run(
                ["ffmpeg", "-v", "error", "-n", "-ss", "120", "-i", str(clip),
                 "-frames:v", "1", str(frame)], check=True)
        info = probe(clip)
        excluded = None
        if not (info["has_audio"] and info["has_video"]) or info["duration_seconds"] < 60:
            excluded = "technical: missing audio/video stream or corrupt"
        entries[name] = {
            "title": title,
            "speaker": speaker,
            "event": "FOSDEM 2022, Python devroom, 6 Feb 2022",
            "page_url": page,
            "download_url": url,
            "license": LICENSE,
            "license_url": LICENSE_URL,
            "license_verified_on_page": True,
            "attribution": f'"{title}", {speaker}, FOSDEM 2022, CC BY 2.0 BE '
            f"({LICENSE_URL}). Clipped and edited: first {CLIP_SECONDS} s, re-encoded.",
            "raw_sha256": digest(raw),
            "clip_path": f"data/real-v1/{name}.mp4",
            "clip_sha256": digest(clip),
            "clip": {"start": 0, "seconds": CLIP_SECONDS, **info},
            "frame_check": frames.get(name),
            "excluded": excluded,
        }
        print(name, info, excluded, flush=True)
    SOURCES.write_text(
        json.dumps({"fetched_at": datetime.now(UTC).isoformat(), "sources": entries}, indent=2)
    )


if __name__ == "__main__":
    main()
