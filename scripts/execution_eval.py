"""Freeze edit labels before inference and score without passing labels to alignment."""

import argparse
import importlib
import itertools
import json
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.media import digest, run

BASE = ROOT / "eval/execution-v1"
FILES = [
    "__init__.py",
    "media.py",
    "alignment.py",
    "audio_alignment.py",
    "grounded_omissions.py",
]


def expected_omissions(recipe):
    if recipe["transform"] == "audio_omission":
        return [
            {
                "source_start": 5,
                "source_end": 10,
                "edit_position": 5,
                "modality": "audio",
            }
        ]
    intervals = recipe["intervals"]
    covered = sorted(intervals)
    expected = []
    position = 0.0
    for previous, current in itertools.pairwise(intervals):
        position += previous[1] - previous[0]
        cursor, end = previous[1], current[0]
        for left, right in covered:
            if right <= cursor or left >= end:
                continue
            if left > cursor:
                expected.append(
                    {
                        "source_start": cursor,
                        "source_end": left,
                        "edit_position": position,
                        "modality": "visual",
                    }
                )
            cursor = max(cursor, right)
        if cursor < end:
            expected.append(
                {
                    "source_start": cursor,
                    "source_end": end,
                    "edit_position": position,
                    "modality": "visual",
                }
            )
    return expected


def generate_case(source, recipe, target):
    from PIL import Image, ImageDraw

    intervals = recipe["intervals"]
    graph = []
    for index, (start, end) in enumerate(intervals):
        graph.extend(
            [
                f"[0:v]trim={start}:{end},setpts=PTS-STARTPTS[v{index}]",
                f"[0:a]atrim={start}:{end},asetpts=PTS-STARTPTS[a{index}]",
            ]
        )
    graph.append(
        "".join(f"[v{index}][a{index}]" for index in range(len(intervals)))
        + f"concat=n={len(intervals)}:v=1:a=1[video][audio]"
    )
    transform = recipe["transform"]
    video_filter = {
        "speed": "setpts=PTS/1.25",
        "crop": "crop=iw*0.8:ih*0.8,scale=960:640",
    }.get(transform, "null")
    inputs = ["-i", str(source)]
    if transform == "subtitles":
        subtitle = target.parent / "subtitle.png"
        if not subtitle.exists():
            image = Image.new("RGBA", (960, 640), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.rectangle((20, 585, 940, 625), fill="black")
            draw.text(
                (30, 592),
                "Controlled benchmark - measurements vary",
                fill="white",
                font_size=22,
            )
            image.save(subtitle)
        inputs += ["-i", str(subtitle)]
        graph.append("[video][1:v]overlay=0:0,format=yuv420p[outv]")
    else:
        graph.append(f"[video]{video_filter},format=yuv420p[outv]")
    if transform == "audio_omission":
        graph.append("[audio]asplit[head][tail]")
        graph.append("[head]atrim=0:5,asetpts=PTS-STARTPTS[ahead]")
        graph.append("[tail]atrim=10:18,asetpts=PTS-STARTPTS[atail]")
        graph.append("[ahead][atail]concat=n=2:v=0:a=1,apad=whole_dur=18[outa]")
    else:
        graph.append(
            f"[audio]{'atempo=1.25' if transform == 'speed' else 'anull'}[outa]"
        )
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-n",
            *inputs,
            "-filter_complex",
            ";".join(graph),
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-crf",
            "32" if transform == "reencode" else "22",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(target),
        ]
    )


def prepare():
    manifest_path = BASE / "manifest.json"
    if manifest_path.exists():
        raise ValueError(
            "Manifest already frozen; preserve it. Use a new version for new labels."
        )
    contract = json.loads((BASE / "contract.json").read_text())
    sources = {
        name: {
            "path": f"sources/{name}.mp4",
            "sha256": digest(BASE / "sources" / f"{name}.mp4"),
            "license": "CC0-1.0",
        }
        for name in contract["sources"]
    }
    target_dir = ROOT / "data/execution-v1/edits"
    target_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    for name, source in sources.items():
        for recipe in contract["recipes"]:
            identifier = f"{name}-{recipe['name']}"
            target = target_dir / f"{identifier}.mp4"
            if not target.exists():
                generate_case(BASE / source["path"], recipe, target)
            cases.append(
                {
                    "id": identifier,
                    "source": name,
                    "recipe": recipe,
                    "video": str(target.relative_to(ROOT)),
                    "sha256": digest(target),
                    "benign": recipe["benign"],
                    "expected": expected_omissions(recipe),
                }
            )
    snapshot = BASE / "engine/context_core"
    snapshot.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        shutil.copyfile(ROOT / "backend/context_core" / filename, snapshot / filename)
    code = {str(path.relative_to(BASE)): digest(path) for path in snapshot.glob("*.py")}
    code["../../scripts/execution_eval.py"] = digest(Path(__file__))
    manifest = {
        "contract": contract,
        "contract_sha256": digest(BASE / "contract.json"),
        "sources": sources,
        "cases": cases,
        "code_sha256": code,
        "python": platform.python_version(),
        "ffmpeg": run(["ffmpeg", "-version"]).decode().splitlines()[0],
    }
    with manifest_path.open("x") as output:
        json.dump(manifest, output, indent=2)
    print(
        f"Frozen {len(cases)} cases, {sum(case['benign'] for case in cases)} benign, before inference",
        flush=True,
    )


def iou(expected, predicted):
    intersection = max(
        0,
        min(expected["source_end"], predicted["source_end"])
        - max(expected["source_start"], predicted["source_start"]),
    )
    union = max(expected["source_end"], predicted["source_end"]) - min(
        expected["source_start"], predicted["source_start"]
    )
    return intersection / union if union else 0


def score(expected, predicted, contract):
    edges = []
    for expected_index, label in enumerate(expected):
        for predicted_index, found in enumerate(predicted):
            overlap = iou(label, found)
            if (
                overlap >= contract["minimum_interval_iou"]
                and abs(label["edit_position"] - found["edit_position"])
                <= contract["maximum_edit_position_error_seconds"]
            ):
                modality = found["matched_evidence"]["modality"]
                if modality == label["modality"] or label["modality"] == "visual":
                    edges.append((overlap, expected_index, predicted_index))
    assigned = {}

    def augment(expected_index, seen):
        candidates = sorted(
            (edge for edge in edges if edge[1] == expected_index), reverse=True
        )
        for _, _, predicted_index in candidates:
            if predicted_index in seen:
                continue
            seen.add(predicted_index)
            if predicted_index not in assigned or augment(
                assigned[predicted_index], seen
            ):
                assigned[predicted_index] = expected_index
                return True
        return False

    for expected_index in range(len(expected)):
        augment(expected_index, set())
    errors = [
        abs(expected[label][boundary] - predicted[found][boundary])
        for found, label in assigned.items()
        for boundary in ("source_start", "source_end")
    ]
    return {
        "expected": len(expected),
        "recovered": len(assigned),
        "predicted": len(predicted),
        "boundary_errors_seconds": errors,
    }


def evaluate(full=False, output=None):
    manifest = json.loads((BASE / "manifest.json").read_text())
    contract = manifest["contract"]
    if digest(BASE / "contract.json") != manifest["contract_sha256"]:
        raise ValueError("Contract changed after freezing")
    for filename, expected_hash in manifest["code_sha256"].items():
        if digest(BASE / filename) != expected_hash:
            raise ValueError(f"Frozen code changed: {filename}")
    for name in list(sys.modules):
        if name == "context_core" or name.startswith("context_core."):
            del sys.modules[name]
    sys.path.insert(0, str(BASE / "engine"))
    analyze = importlib.import_module("context_core.alignment").analyze
    grounded = importlib.import_module(
        "context_core.grounded_omissions"
    ).grounded_omissions
    output = (
        Path(output)
        if output
        else BASE / ("full-results" if full else "friday-results")
    )
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    selected = (
        manifest["cases"]
        if full
        else [
            next(case for case in manifest["cases"] if case["id"] == identifier)
            for identifier in contract["friday_cases"]
        ]
    )
    for case in selected:
        source = manifest["sources"][case["source"]]
        if digest(BASE / source["path"]) != source["sha256"]:
            raise ValueError("Source changed after freeze")
        target = ROOT / case["video"]
        if not target.exists():
            generate_case(BASE / source["path"], case["recipe"], target)
        if digest(target) != case["sha256"]:
            raise ValueError(
                "Edited bytes differ from freeze; use the recorded FFmpeg version"
            )
        evidence = analyze(BASE / source["path"], target)
        prediction = grounded(evidence)
        (output / f"{case['id']}.json").write_text(
            json.dumps({"alignment": evidence, "prediction": prediction}, indent=2)
        )
        row = {
            "id": case["id"],
            "benign": case["benign"],
            **score(case["expected"], prediction["omissions"], contract),
        }
        rows.append(row)
        print(
            f"{case['id']}: {row['recovered']}/{row['expected']} recovered, {row['predicted']} predicted",
            flush=True,
        )
    total = sum(row["expected"] for row in rows)
    recovered = sum(row["recovered"] for row in rows)
    benign = [row for row in rows if row["benign"]]
    errors = [error for row in rows for error in row["boundary_errors_seconds"]]
    recall = recovered / total if total else None
    false_alarms = (
        sum(row["predicted"] > 0 for row in benign) / len(benign) if benign else None
    )
    report = {
        "manifest_sha256": digest(BASE / "manifest.json"),
        "scope": contract["scope"],
        "interval_recall": recall,
        "boundary_error_seconds": sum(errors) / len(errors) if errors else None,
        "benign_false_alarm_rate": false_alarms,
        "kill_switch": recall is not None
        and recall < contract["kill_below_interval_recall"],
        "passed": recall is not None
        and recall >= contract["minimum_interval_recall"]
        and false_alarms is not None
        and false_alarms < contract["maximum_benign_false_alarm_rate_exclusive"],
        "cases": rows,
    }
    (output / "results.json").write_text(json.dumps(report, indent=2))
    table = [
        "# Frozen execution baseline",
        "",
        contract["scope"],
        "",
        "| Case | Recovered / expected | Predicted omissions | Benign |",
        "|---|---:|---:|---|",
    ]
    table += [
        f"| {row['id']} | {row['recovered']} / {row['expected']} | {row['predicted']} | {row['benign']} |"
        for row in rows
    ]
    table += [
        "",
        f"Interval recall: {recall}; mean boundary error: {report['boundary_error_seconds']} seconds; benign false-alarm rate: {false_alarms}.",
        f"Kill switch: {report['kill_switch']}. Passed: {report['passed']}.",
    ]
    (output / "RESULTS.md").write_text("\n".join(table) + "\n")
    print(
        json.dumps({key: value for key, value in report.items() if key != "cases"}),
        flush=True,
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "friday", "full"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    else:
        report = evaluate(args.action == "full", args.output)
        sys.exit(2 if report["kill_switch"] else 0 if report["passed"] else 1)
