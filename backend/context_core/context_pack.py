"""Small, provenance-linked video excerpts for contextual review."""

from pathlib import Path

from .media import digest, run

MAX_CLIP_SECONDS = 30
MAX_CLIP_BYTES = 8 * 1024 * 1024


def plan_clips(evidence, finding_id):
    if evidence["status"] != "matched":
        raise ValueError("Context review requires a supported source alignment")
    finding = next((f for f in evidence["findings"] if f["id"] == finding_id), None)
    if finding is None:
        raise ValueError("Finding does not exist")
    start, end = finding["source_start"], finding["source_end"]
    if end - start > MAX_CLIP_SECONDS - 4:
        raise ValueError(
            "This interval is too long for bounded review; inspect it manually"
        )
    source_start = max(0, start - 2)
    source_end = min(evidence["source"]["duration"], end + 2)
    if finding.get("edited_start") is not None:
        anchor = finding["edited_start"]
    else:
        # Choose the edit boundary nearest the omitted source interval.
        matches = [s for s in evidence["segments"] if s["kind"] == "match"]
        adjacent = min(
            matches,
            key=lambda s: min(
                abs(s["source_start"] - end), abs(s["source_end"] - start)
            ),
        )
        anchor = (
            adjacent["edited_start"]
            if abs(adjacent["source_start"] - end) < abs(adjacent["source_end"] - start)
            else adjacent["edited_end"]
        )
    edit_start = max(0, anchor - 4)
    edit_end = min(evidence["edited"]["duration"], anchor + 4)
    return [
        {
            "id": "source_context",
            "media": "source",
            "start": source_start,
            "end": source_end,
        },
        {
            "id": "published_context",
            "media": "edited",
            "start": edit_start,
            "end": edit_end,
        },
    ]


def build_pack(directory, evidence, finding_id):
    clips = plan_clips(evidence, finding_id)
    target = Path(directory) / "context" / finding_id
    target.mkdir(parents=True, exist_ok=True)
    for clip in clips:
        src = Path(directory) / (
            "original.mp4" if clip["media"] == "source" else "edited.mp4"
        )
        path = target / (clip["id"] + ".mp4")
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(src),
                "-ss",
                str(clip["start"]),
                "-t",
                str(clip["end"] - clip["start"]),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                "-vf",
                "scale=640:360:force_original_aspect_ratio=decrease,setsar=1",
                "-r",
                "12",
                "-c:v",
                "libx264",
                "-crf",
                "28",
                "-c:a",
                "aac",
                "-b:a",
                "64k",
                "-movflags",
                "+faststart",
                str(path),
            ]
        )
        if path.stat().st_size > MAX_CLIP_BYTES:
            path.unlink()
            raise ValueError("Context clip exceeds the upload size limit")
        clip.update(
            path=str(path),
            sha256=digest(path),
            has_audio=evidence[clip["media"]]["has_audio"],
        )
    return clips
