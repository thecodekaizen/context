"""Acquire only the frozen NASA assets and regenerate hash-checked local cases.

Explicit --download is required. No dataset agreements are accepted. Media stays
under ignored data/sprint-eval; a hash mismatch never updates frozen expectations.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.media import digest, run
from context_core.retrieval import download_video


def eligible_metadata(meta):
    """Legacy archival fixture check; not CONTEXT content admission."""
    import re

    if (
        meta.get("media_type") != "video"
        or not meta.get("nasa_id")
        or not meta.get("center")
    ):
        return False
    notice = " ".join(
        str(meta.get(k, "")) for k in ("copyright", "description", "secondary_creator")
    )
    return not re.search(
        r"©|copyright|all rights reserved|courtesy of|licensed (?:by|from)",
        notice,
        re.IGNORECASE,
    )


async def prepare(manifest_path):
    manifest = json.loads(manifest_path.read_text())
    base = ROOT / "data/sprint-eval"
    sources = base / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    for key, spec in manifest["sources"].items():
        if not key.replace("_", "").isalnum():
            raise ValueError("Invalid source key")
        path = sources / (key + ".mp4")
        if not path.exists():
            if spec.get("derived_from"):
                run(
                    [
                        "ffmpeg",
                        "-v",
                        "error",
                        "-y",
                        "-i",
                        str(sources / (spec["derived_from"] + ".mp4")),
                        "-c:v",
                        "libx264",
                        "-crf",
                        "19",
                        "-c:a",
                        "aac",
                        str(path),
                    ]
                )
            else:
                if not eligible_metadata(spec["metadata"]):
                    raise ValueError("Asset rights metadata requires review")
                await download_video(spec["url"], path, max_bytes=50 * 1024 * 1024)
        if digest(path) != spec["sha256"]:
            raise ValueError(
                f"Source hash mismatch: {key}; do not change frozen expectations"
            )
    for case in manifest["cases"]:
        target = (ROOT / case["video"]).resolve()
        if not target.is_relative_to(base):
            raise ValueError("Output must remain inside evaluation data directory")
        if not target.exists():
            parts = case["intervals"]
            graph = ";".join(
                f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{j}];[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{j}]"
                for j, (a, b) in enumerate(parts)
            )
            graph += (
                ";"
                + "".join(f"[v{j}][a{j}]" for j in range(len(parts)))
                + f"concat=n={len(parts)}:v=1:a=1[v][a]"
            )
            run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-y",
                    "-i",
                    str(sources / (case["source_key"] + ".mp4")),
                    "-filter_complex",
                    graph,
                    "-map",
                    "[v]",
                    "-map",
                    "[a]",
                    "-c:v",
                    "libx264",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    str(target),
                ]
            )
        if digest(target) != case["sha256"]:
            raise ValueError(
                f"Case hash mismatch: {case['id']}; FFmpeg version may differ. Preserve this manifest and create a new version, never relabel after inference."
            )
    print(
        f"Verified {len(manifest['sources'])} source encodings and {len(manifest['cases'])} frozen cases"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "eval/sprint_manifest.json"
    )
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if not args.download:
        parser.error(
            "Explicit --download required after reviewing manifest source rights/policy"
        )
    asyncio.run(prepare(args.manifest))
