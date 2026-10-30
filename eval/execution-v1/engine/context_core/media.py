"""Bounded FFmpeg operations; timestamps are seconds relative to decoded start."""

import hashlib
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

RATE = 4
MAX_DURATION = 600


def run(args, timeout=120):
    try:
        return subprocess.run(
            args, check=True, capture_output=True, timeout=timeout
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise ValueError(
            "Media decoding failed: " + exc.stderr.decode(errors="replace")[-500:]
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Media processing timed out") from exc


def probe(path):
    raw = json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ]
        )
    )
    stream = next((s for s in raw["streams"] if s["codec_type"] == "video"), None)
    if not stream:
        raise ValueError("A video stream is required")
    duration = float(raw["format"].get("duration", stream.get("duration", 0)))
    if duration == 0:
        # Browser MediaRecorder WebM has no finalized duration header. Inspect
        # packet timestamps instead of treating a valid recording as empty.
        packets = run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "packet=pts_time,duration_time",
                "-of",
                "csv=p=0",
                str(path),
            ]
        )
        for row in packets.decode().splitlines():
            parts = row.split(",")
            try:
                end = float(parts[0]) + (
                    float(parts[1]) if len(parts) > 1 and parts[1] != "N/A" else 0
                )
                if math.isfinite(end):
                    duration = max(duration, end)
            except ValueError:
                continue
    if not math.isfinite(duration) or not 0 < duration <= MAX_DURATION:
        raise ValueError(f"Video must be between 0 and {MAX_DURATION} seconds")
    return {
        "duration": duration,
        "video_duration": float(stream.get("duration", duration)),
        "frame_rate": stream.get("avg_frame_rate", "0/1"),
        "width": stream["width"],
        "height": stream["height"],
        "codec": stream["codec_name"],
        "pixel_format": stream.get("pix_fmt"),
        "container": raw["format"].get("format_name", ""),
        "audio_codec": next(
            (s.get("codec_name") for s in raw["streams"] if s["codec_type"] == "audio"),
            None,
        ),
        "has_audio": any(s["codec_type"] == "audio" for s in raw["streams"]),
    }


def fingerprints(path):
    # Area reduction suppresses compression noise; retain color and spatial layout.
    raw = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-an",
            "-vf",
            f"fps={RATE},scale=24:16:flags=area",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ]
    )
    frames = (
        np.frombuffer(raw, dtype=np.uint8).reshape(-1, 16 * 24 * 3).astype(np.float32)
        / 255
    )
    if not len(frames):
        raise ValueError("No decodable frames")
    return np.arange(len(frames)) / RATE, frames


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class VideoSamples:
    info: dict
    times: np.ndarray
    frames: np.ndarray
    sha256: str


def sample(path):
    info = probe(path)
    times, frames = fingerprints(path)
    return VideoSamples(info, times, frames, digest(path))


def playback_file(path, target):
    """Keep evidence bytes unchanged; normalize only incompatible player media."""
    info = probe(path)
    if (
        info["codec"] == "h264"
        and info["pixel_format"] in {"yuv420p", "yuvj420p"}
        and "mp4" in info["container"].split(",")
        and info["audio_codec"] in {None, "aac", "mp3"}
    ):
        return Path(path)
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-vf",
            "scale=w='trunc(min(1280,iw)/2)*2':h=-2,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(target),
        ]
    )
    preview = probe(target)
    if abs(preview["duration"] - info["duration"]) > 0.5:
        Path(target).unlink(missing_ok=True)
        raise ValueError(
            "Playback conversion changed timing beyond the supported tolerance"
        )
    return Path(target)


def save_evidence(directory, result):
    directory = Path(directory)
    result["id"] = directory.name
    result["media"] = {}
    for kind, filename in [("source", "original"), ("edited", "edited")]:
        source_path = directory / f"{filename}.mp4"
        if source_path.exists():
            playback = playback_file(source_path, directory / f"{filename}-preview.mp4")
            result["media"][kind] = f"/api/media/{directory.name}/{playback.name}"
    temporary = directory / "evidence.tmp"
    temporary.write_text(json.dumps(result, indent=2))
    temporary.replace(directory / "evidence.json")
    return result
