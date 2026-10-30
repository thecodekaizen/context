"""Frozen source-disjoint regression evaluation; no EVID accuracy claims.

Run with configured MODEL_API_KEY. All attempts, failed stages, input hashes,
provider receipts and raw outputs are retained in an immutable run directory.
Expected source IDs/recipes/labels never enter investigate or model prompts.
"""

import argparse
import asyncio
import json
import shutil
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.dossier import investigate
from context_core.library import add_source, rank_sources
from context_core.media import digest


async def evaluate(manifest_path, resume=None):
    manifest_path = manifest_path.resolve()
    resume = resume.resolve() if resume else None
    manifest = json.loads(manifest_path.read_text())
    for filename, expected in manifest["code_sha256"].items():
        if digest(ROOT / filename) != expected:
            raise ValueError(
                f"Code changed after evaluation freeze: {filename}. Preserve prior run and explicitly re-freeze before a new evaluation."
            )
    run_id = (
        resume.name
        if resume
        else datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    )
    output = resume or ROOT / "data/sprint-eval/runs" / run_id
    output.mkdir(parents=True, exist_ok=bool(resume))
    if not resume:
        shutil.copy2(manifest_path, output / "manifest.json")
    elif digest(output / "manifest.json") != digest(manifest_path):
        raise ValueError("Resume manifest differs from frozen run")
    report = {
        "run_id": run_id,
        "manifest_sha256": digest(manifest_path),
        "annotation_status": manifest["annotation_status"],
        "scope": manifest["source_split"],
        "attempted": len(manifest["cases"]),
        "cases": [],
    }
    if resume:
        report = json.loads((output / "results.json").read_text())
    for index, case in enumerate(manifest["cases"]):
        if any(x["case_id"] == case["id"] for x in report["cases"]):
            continue
        started = time.monotonic()
        record = {
            "case_id": case["id"],
            "input_sha256": case["sha256"],
            "category": case["category"],
        }
        print("START", case["id"], flush=True)
        directory = output / f"job-{index:03d}"
        if directory.exists():
            report["interrupted_attempts"] = report.get("interrupted_attempts", 0) + 1
            record["previous_interrupted_job"] = directory.name
            directory = output / (directory.name + "-retry-" + uuid4().hex[:6])
        directory.mkdir()
        record["job_directory"] = str(directory.relative_to(ROOT))
        try:
            video = ROOT / case["video"]
            if digest(video) != case["sha256"]:
                raise ValueError("Evaluation media changed after freeze")
            shutil.copy2(video, directory / "video.mp4")
            library = directory / "library"
            library.mkdir()
            for key in case["library"]:
                source = ROOT / "data/sprint-eval/sources" / f"{key}.mp4"
                if digest(source) != manifest["sources"][key]["sha256"]:
                    raise ValueError("Reference changed after freeze")
                add_source(
                    library, source, manifest["sources"][key]["metadata"]["title"]
                )
            baseline, _ = (
                rank_sources(library, video)
                if case["library"]
                else ({"status": "unindexed"}, None)
            )
            record["algorithm_only_baseline"] = baseline
            dossier = await investigate(
                directory,
                case["caption"],
                {
                    "method": "frozen_evaluation",
                    "filename": video.name,
                    "original_recording_supplied": False,
                },
                library_root=library,
                acquire_sources=case["remote_acquisition"],
            )
            matched = dossier.get("matched_source", {})
            expected = case["expected_source"]
            if expected:
                reference = manifest["sources"][expected]
                catalog_matches = [
                    x
                    for x in dossier.get("source_video_retrieval", {}).get(
                        "candidates", []
                    )
                    if x.get("source_id") == matched.get("source_id")
                    and x.get("catalog_id") == reference["upstream_id"]
                ]
                retrieval_correct = matched.get("status") == "matched" and (
                    matched.get("source_id") == reference["sha256"]
                    or bool(catalog_matches)
                )
            else:
                retrieval_correct = matched.get("status") != "matched"
            reviews = dossier.get("comparison", {}).get("reviews", [])
            semantics = [
                x["interpretation"]["classification"]
                for x in reviews
                if x.get("status") == "complete"
            ]
            target = case.get("expected_semantic")
            if target == "harmless_edit":
                semantic_correct = bool(semantics) and all(
                    x == "harmless_edit" for x in semantics
                )
            elif target == "meaning_changed":
                semantic_correct = "meaning_changed" in semantics
            elif target == "inconclusive":
                semantic_correct = not semantics or all(
                    x == "inconclusive" for x in semantics
                )
            else:
                semantic_correct = None
            caption_ids = {
                x["id"]
                for x in dossier.get("analysis", {}).get("claims", [])
                if x["origin"] == "supplied_caption"
            }
            caption_verdicts = [
                x["verdict"]
                for x in dossier.get("assessment", {}).get("findings", [])
                if x["claim_id"] in caption_ids
            ]
            caption_correct = (
                case["expected_caption_verdict"] in caption_verdicts
                if case.get("expected_caption_verdict")
                else None
            )
            checks = {
                "retrieval": retrieval_correct,
                "semantic": semantic_correct,
                "caption": caption_correct,
            }
            record.update(
                status=dossier["status"],
                retrieval=matched,
                comparison=dossier.get("comparison"),
                semantic_outputs=semantics,
                caption_verdicts=caption_verdicts,
                checks=checks,
                passed=dossier["status"] == "complete"
                and all(v is not False for v in checks.values()),
                validated_observations=len(
                    dossier.get("analysis", {}).get("observations", [])
                ),
                failures=dossier.get("failure_log", []),
            )
        except Exception as exc:  # noqa: BLE001 — retain every attempted case
            record.update(status="error", error=str(exc)[:1000], passed=False)
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        report["cases"].append(record)
        report.update(
            completed=sum(x["status"] == "complete" for x in report["cases"]),
            passed=sum(x["passed"] for x in report["cases"]),
            failed=sum(not x["passed"] for x in report["cases"]),
        )
        (output / "results.json").write_text(json.dumps(report, indent=2))
        print(
            "RESULT",
            case["id"],
            record["status"],
            record.get("checks"),
            record["elapsed_seconds"],
            flush=True,
        )
    print("REPORT", output / "results.json", flush=True)
    return report["passed"] == report["attempted"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "eval/sprint_manifest.json"
    )
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    sys.exit(0 if asyncio.run(evaluate(args.manifest, args.resume)) else 1)
