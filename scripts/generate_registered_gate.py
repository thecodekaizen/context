import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.media import digest, run

out = ROOT / "data/gate-v2"
source = out / "reference.mp4"
if (out / "results.json").exists() or any(out.glob("classification-receipt-*.json")):
    raise ValueError(
        "Evaluation already started; preserve this dataset and its receipts"
    )
cases = {
    "honest_qualification": {
        "expected": "not_misleading",
        "intervals": [[10.997, 20.974]],
        "rationale": "Preserves both future-crew qualification and explicit no-humans-onboard statement.",
    },
    "honest_launch": {
        "expected": "not_misleading",
        "intervals": [[47.8, 68.388]],
        "rationale": "Complete countdown, ignition and liftoff in original order.",
    },
    "captioned_omission": {
        "expected": "misleading",
        "intervals": [[10.997, 13.6], [57.377, 68.388]],
        "caption": "Artemis I launch: astronauts are onboard Orion.",
        "rationale": "Cuts future-missions and uncrewed/no-humans qualification, then pairs crew-module words and liftoff with a false current-crew caption. Tests the product video-plus-caption use case; it is not a bare-cut-only test.",
    },
    "chronology_reorder": {
        "expected": "misleading",
        "intervals": [[59.746, 68.388], [47.8, 59.746]],
        "rationale": "Booster ignition and liftoff precede engine start/countdown. Reverses an explicit event sequence.",
    },
    "reversed_claim": {
        "expected": "misleading",
        "intervals": [[10.75, 13.6], [18.03, 20.974]],
        "rationale": "Retains astronauts-will-go phrase without future qualification, then retains humans-are-onboard while cutting meaning-no. Opposes original no-human statement. Requires separate transcription audit before scoring.",
    },
}
manifest = {
    "source": "reference.mp4",
    "source_sha256": digest(source),
    "source_caption": "../gate-source-review/jsc2022m000294_TheJourneyofArtemisI.srt",
    "reference_source_offset": 120,
    "label_protocol": "Source-caption-audited recipes fixed before any classification requests. These are authored expected labels, not independent human ground truth. One case deliberately supplies a misleading caption; report this scope variation explicitly. Reversal wording must be audited before scoring.",
    "cases": cases,
    "criteria": {
        "max_boundary_error_seconds": 2,
        "minimum_semantic_correct": 4,
        "both_honest_required": True,
    },
    "classification_started": False,
}
for name, spec in cases.items():
    parts = spec["intervals"]
    graph = ";".join(
        f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]"
        for i, (a, b) in enumerate(parts)
    )
    graph += (
        ";"
        + "".join(f"[v{i}][a{i}]" for i in range(len(parts)))
        + f"concat=n={len(parts)}:v=1:a=1[v][a]"
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
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-crf",
            "22",
            "-c:a",
            "aac",
            str(out / (name + ".mp4")),
        ]
    )
    spec["sha256"] = digest(out / (name + ".mp4"))
(out / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(
    "Prepared five edits and saved preregistered manifest. No classifier requests yet."
)
