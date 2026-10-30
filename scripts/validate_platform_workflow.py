"""First-run comparison on NEW synthetic speech edits, not field accuracy.

Creates labeled fixtures before inference. Both conditions get the same footage.
Agent-authored labels and synthetic speech are explicit; reviewer time is unset.
"""

import argparse
import asyncio
import base64
import json
import random
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.dossier import investigate, model_request, text_output
from context_core.library import add_source
from context_core.media import digest, probe, run
from context_core.meta import validate_interpretation
from context_core.providers import settings

SPEECH = [
    [
        "In this fictional training example.",
        "The side entrance is",
        "not",
        "open to visitors.",
        "This recording describes a simulated inspection.",
    ],
    [
        "This is a fictional product demonstration.",
        "The new version is",
        "not",
        "ready for release.",
        "The statement applies to the prototype shown here.",
    ],
    [
        "This is an invented laboratory report.",
        "The recorded measurement does",
        "not",
        "support the proposed explanation.",
        "Further investigation is necessary.",
    ],
]


def duration(path):
    return float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                str(path),
            ]
        )
    )


def edit(source, target, intervals):
    graph = []
    for i, (a, b) in enumerate(intervals):
        graph.extend(
            [
                f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]",
                f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]",
            ]
        )
    graph.append(
        "".join(f"[v{i}][a{i}]" for i in range(len(intervals)))
        + f"concat=n={len(intervals)}:v=1:a=1[v][a]"
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
            ";".join(graph),
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-crf",
            "24",
            "-c:a",
            "aac",
            str(target),
        ]
    )


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "annotation_status": "Agent-authored, deterministic synthetic speech recipes. No independent human semantic adjudication. Not a real-world accuracy benchmark.",
        "source_split": "Three newly generated sources, six new clips; never previously used by this project. Model pretraining exposure to general sentences is unknown.",
        "cases": [],
    }
    for n, phrases in enumerate(SPEECH):
        folder = out / f"source-{n}"
        folder.mkdir()
        offsets = [0.0]
        for i, phrase in enumerate(phrases):
            aiff = folder / f"part-{i}.aiff"
            run(["say", "-v", "Samantha", "-r", "145", "-o", str(aiff), phrase])
            offsets.append(offsets[-1] + duration(aiff))
        args = ["ffmpeg", "-v", "error", "-y"]
        for i in range(len(phrases)):
            args.extend(["-i", str(folder / f"part-{i}.aiff")])
        graph = (
            "".join(f"[{i}:a]" for i in range(len(phrases)))
            + f"concat=n={len(phrases)}:v=0:a=1[a]"
        )
        wave = folder / "sound.wav"
        run(args + ["-filter_complex", graph, "-map", "[a]", "-ar", "16000", str(wave)])
        source = folder / "recording.mp4"
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc2=size=640x360:rate=12, hue=h={n * 55}",
                "-i",
                str(wave),
                "-t",
                str(offsets[-1]),
                "-c:v",
                "libx264",
                "-crf",
                "24",
                "-c:a",
                "aac",
                "-shortest",
                str(source),
            ]
        )
        for changed in (False, True):
            identifier = f"case-{n * 2 + int(changed):02d}"
            intervals = (
                [[0, offsets[-1]]]
                if not changed
                else [[0, offsets[2]], [offsets[3], offsets[-1]]]
            )
            clip = folder / f"{identifier}.mp4"
            edit(source, clip, intervals)
            manifest["cases"].append(
                {
                    "id": identifier,
                    "source": str(source.relative_to(ROOT)),
                    "video": str(clip.relative_to(ROOT)),
                    "source_sha256": digest(source),
                    "sha256": digest(clip),
                    "expected": "meaning_changed" if changed else "harmless_edit",
                    "target_removed_interval": [offsets[2], offsets[3]]
                    if changed
                    else None,
                    "annotation": "Removes only the spoken negation, reversing the proposition"
                    if changed
                    else "Re-encoded copy retains the entire recording, including fictional framing and negation",
                    "source_transcript_annotation_only": phrases,
                    "edit_recipe_annotation_only": intervals,
                }
            )
    manifest["frozen_files"] = {
        str(p.relative_to(ROOT)): digest(p)
        for pattern in (
            "backend/context_core/*.py",
            "scripts/validate_platform_workflow.py",
            "backend/requirements.lock",
        )
        for p in ROOT.glob(pattern)
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def score(interpretations, expected):
    classifications = [i.get("classification") for i in interpretations]
    changed = "meaning_changed" in classifications
    explicit = bool(classifications)
    predicted = (
        "meaning_changed"
        if changed
        else "harmless_edit"
        if explicit and all(x == "harmless_edit" for x in classifications)
        else "inconclusive"
        if explicit
        else "absent"
    )
    return {
        "prediction": predicted,
        "correct": predicted == expected,
        "missed_consequential_edit": expected == "meaning_changed" and not changed,
        "false_positive": expected == "harmless_edit" and changed,
    }


async def execute(out, manifest):
    if settings().provider != "meta":
        raise ValueError(
            "This comparison explicitly requires the configured Meta multimodal model"
        )
    report = {
        "annotation_status": manifest["annotation_status"],
        "scope": manifest["source_split"],
        "human_review": {
            "completed": 0,
            "accuracy": None,
            "reviewer_completion_seconds": None,
            "reason": "No human reviewer has performed the blinded tasks; system latency is not reviewer time",
        },
        "conditions": "Plain Meta receives full source and edit, neutral comparison prompt, no labels/recipes. CONTEXT receives same media through a per-job source library; remote retrieval disabled in both. Different bounded context selection is part of the application condition.",
        "cases": [],
    }
    cases = list(manifest["cases"])
    random.Random(20261030).shuffle(cases)
    for case in cases:
        source = ROOT / case["source"]
        video = ROOT / case["video"]
        if digest(source) != case["source_sha256"] or digest(video) != case["sha256"]:
            raise ValueError("Media changed after freeze")
        row = {"case_id": case["id"], "expected": case["expected"]}
        order = ["context", "plain_meta"]
        random.Random(case["id"]).shuffle(order)
        for condition in order:
            directory = out / (case["id"] + "-" + condition)
            directory.mkdir()
            started = time.monotonic()
            result = {"status": "started"}
            try:
                if condition == "context":
                    shutil.copy2(video, directory / "video.mp4")
                    library = directory / "library"
                    library.mkdir()
                    add_source(library, source, "Supplied recording")
                    dossier = await investigate(
                        directory,
                        provenance={
                            "method": "synthetic_paired_comparison",
                            "original_recording_supplied": True,
                        },
                        library_root=library,
                        acquire_sources=False,
                    )
                    reviews = dossier.get("comparison", {}).get("reviews", [])
                    interpretations = [
                        x["interpretation"]
                        for x in reviews
                        if x.get("status") == "complete"
                    ]
                    result.update(
                        status=dossier["status"],
                        rejected_reviews=sum(
                            x.get("status") != "complete" for x in reviews
                        ),
                        source_match=dossier.get("matched_source", {}).get("status"),
                    )
                    if case["target_removed_interval"]:
                        a, b = case["target_removed_interval"]
                        result["target_interval_located"] = any(
                            min(b, x["finding"]["source_end"])
                            > max(a, x["finding"]["source_start"])
                            for x in reviews
                            if x.get("status") == "complete"
                            and x.get("interpretation", {}).get("classification")
                            == "meaning_changed"
                        )
                else:
                    clips = [
                        {
                            "id": "source_context",
                            "media": "source",
                            "start": 0,
                            "end": probe(source)["duration"],
                            "has_audio": True,
                        },
                        {
                            "id": "published_context",
                            "media": "edited",
                            "start": 0,
                            "end": probe(video)["duration"],
                            "has_audio": True,
                        },
                    ]
                    prompt = (
                        'Compare the short published recording with its source, including actual speech. Decide whether the edit materially changes an expressed proposition or chronology, preserves meaning, or is inconclusive. Shortening alone is not misleading. Do not infer intent. Use only the media. Return ONLY JSON {"classification":"harmless_edit|meaning_changed|inconclusive","observations":[{"text":"what you observed","citations":[{"clip_id":"source_context or published_context","start":0,"end":1}]}],"possible_effect":"explanation","uncertainty":"limitations"}. Use clip-local timestamps bounded by the durations; cite both videos for a non-inconclusive conclusion. Manifest: '
                        + json.dumps(clips)
                    )
                    content = [{"type": "input_text", "text": prompt}]
                    for label, path in (
                        ("source_context", source),
                        ("published_context", video),
                    ):
                        content.extend(
                            [
                                {"type": "input_text", "text": "Next video: " + label},
                                {
                                    "type": "input_video",
                                    "video_url": "data:video/mp4;base64,"
                                    + base64.b64encode(path.read_bytes()).decode(),
                                },
                            ]
                        )
                    payload = await model_request(
                        [{"role": "user", "content": content}],
                        receipt_dir=directory,
                        stage="plain_meta_comparison",
                    )
                    (directory / "response.json").write_text(
                        json.dumps(payload, indent=2)
                    )
                    interpretation = validate_interpretation(
                        text_output(payload), clips
                    )
                    (directory / "interpretation.json").write_text(
                        json.dumps(interpretation, indent=2)
                    )
                    interpretations = [interpretation]
                    result.update(status="complete", rejected_reviews=0)
                result.update(score(interpretations, case["expected"]))
            except Exception as exc:  # noqa: BLE001 — preserve every failed condition
                result.update(
                    status="error", error=str(exc)[:500], **score([], case["expected"])
                )
            result["system_elapsed_seconds"] = round(time.monotonic() - started, 3)
            result["reviewer_completion_seconds"] = None
            row[condition] = result
            print(case["id"], condition, json.dumps(result), flush=True)
        report["cases"].append(row)
        (out / "results.json").write_text(json.dumps(report, indent=2))
    for condition in ("context", "plain_meta"):
        rows = [x[condition] for x in report["cases"]]
        report[condition] = {
            "attempted": len(rows),
            "correct": sum(x["correct"] for x in rows),
            "accuracy_on_authored_synthetic_cases": sum(x["correct"] for x in rows)
            / len(rows),
            "missed_consequential_edits": sum(
                x["missed_consequential_edit"] for x in rows
            ),
            "false_positives": sum(x["false_positive"] for x in rows),
            "errors": sum(x["status"] == "error" for x in rows),
        }
    (out / "results.json").write_text(json.dumps(report, indent=2))
    print("RESULTS", out / "results.json", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        action="store_true",
        help="Send only these new synthetic fixtures to the configured Meta API",
    )
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    out = (
        ROOT
        / "data/platform-validation"
        / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6])
    )
    manifest = prepare(out)
    print("FROZEN", out / "manifest.json", flush=True)
    if args.run:
        asyncio.run(execute(out, manifest))
