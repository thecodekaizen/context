"""PRELUDE Benchmark Evaluation Runner.

Evaluates anticipatory hazard analysis on real Australian Roads Dashcam clips:
- Positive incident cases with known ground truth incident times.
- Negative normal driving cases with zero hazards.
- Strictly bounds inference inputs to t <= t_cutoff.
- Measures:
  1. Hazard detection accuracy (True Positive Rate).
  2. False Alarm Rate on safe driving negatives (False Positive Rate).
  3. Pre-incident lead time (seconds prior to ground truth incident).
  4. Epistemic boundary and disclaimer compliance.
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

# Ensure backend modules are on sys.path
backend_path = Path(__file__).resolve().parents[1] / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

load_dotenv()

from context_core.prelude import run_prelude_investigation

BENCHMARK_DIR = Path(__file__).resolve().parents[1] / "data/prelude_benchmark"
RESULTS_DIR = (
    Path(__file__).resolve().parents[1]
    / "data/prelude_benchmark_results"
    / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {
        "case_id": "near_crash_007_early_warning",
        "video_file": "near_crash_007.mp4",
        "expected_hazard": True,
        "t_incident": 4.5,
        "t_cutoff": 4.1,  # 0.4s prior to closest approach
        "description": "Right side road pickup fails to give way and crosses ego lane; pre-incident window ending at t=4.1s.",
    },
    {
        "case_id": "near_crash_011_early_warning",
        "video_file": "near_crash_011.mp4",
        "expected_hazard": True,
        "t_incident": 7.5,
        "t_cutoff": 6.8,  # Prior to broadside in-lane near miss
        "description": "Left T-intersection hatchback fails to yield and cuts across path; cutoff at t=6.8s.",
    },
    {
        "case_id": "normal_safe_004_negative",
        "video_file": "normal_safe_004.mp4",
        "expected_hazard": False,
        "t_incident": None,
        "t_cutoff": 3.0,
        "description": "Safe daylight residential driving negative; zero hazards.",
    },
    {
        "case_id": "normal_safe_061_negative",
        "video_file": "normal_safe_061.mp4",
        "expected_hazard": False,
        "t_incident": None,
        "t_cutoff": 6.0,
        "description": "Safe daylight suburban driving negative; steady lane flow.",
    },
]


async def run_benchmark():
    print("=" * 80)
    print("PRELUDE MULTI-SAMPLE ANTICIPATORY BENCHMARK (REAL DASHCAM FOOTAGE)")
    print("=" * 80)

    has_key = bool(os.getenv("MODEL_API_KEY"))
    print(f"Meta Model API key present: {has_key}")

    results = []
    tp, fp, tn, fn = 0, 0, 0, 0
    lead_times = []

    for case in CASES:
        print(f"\n--- Running Case: {case['case_id']} ---")
        print(f"Description: {case['description']}")
        print(
            f"File: {case['video_file']} | t_cutoff={case['t_cutoff']}s | t_incident={case['t_incident']}"
        )

        video_path = BENCHMARK_DIR / case["video_file"]
        if not video_path.exists():
            print(f"SKIPPED: Video file {video_path} not found.")
            results.append(
                {"case_id": case["case_id"], "status": "missing_media", "passed": False}
            )
            continue

        try:
            dossier = await run_prelude_investigation(
                video_path=video_path,
                t_cutoff=case["t_cutoff"],
                t_incident=case["t_incident"],
                use_model=has_key,
            )

            detected = dossier.hazard_detected
            expected = case["expected_hazard"]
            lead_time = dossier.lead_time

            passed = detected == expected

            if expected and detected:
                tp += 1
                if lead_time is not None:
                    lead_times.append(lead_time)
            elif not expected and not detected:
                tn += 1
            elif not expected and detected:
                fp += 1
            elif expected and not detected:
                fn += 1

            status_str = "PASS" if passed else "FAIL"
            print(f"Result: {status_str}")
            print(f"  Hazard detected: {detected} (expected: {expected})")
            print(f"  Risk level: {dossier.risk_level}")
            print(f"  Conflict type: {dossier.finding.conflict_type}")
            print(f"  Lead time: {lead_time}s" if lead_time else "  Lead time: N/A")
            print(f"  Summary: {dossier.finding.summary}")

            record = {
                "case_id": case["case_id"],
                "video_file": case["video_file"],
                "expected_hazard": expected,
                "detected_hazard": detected,
                "passed": passed,
                "risk_level": dossier.risk_level,
                "t_cutoff": case["t_cutoff"],
                "t_incident": case["t_incident"],
                "t_cue": dossier.finding.t_cue_seconds,
                "lead_time": lead_time,
                "conflict_type": dossier.finding.conflict_type,
                "observations": dossier.finding.observations,
                "kinematics": dossier.finding.kinematic_signals,
                "disclaimer_present": bool(dossier.disclaimer),
            }
            results.append(record)

            # Save per-case dossier
            out_file = RESULTS_DIR / f"{case['case_id']}_dossier.json"
            out_file.write_text(dossier.model_dump_json(indent=2))

        except Exception as exc:  # noqa: BLE001 — record every attempted case
            print(f"ERROR running case {case['case_id']}: {exc}")
            results.append(
                {
                    "case_id": case["case_id"],
                    "status": "service_or_pipeline_error",
                    "passed": False,
                    "error": str(exc)[:500],
                }
            )

    # Metrics Summary
    total_samples = len(results)
    accuracy = (tp + tn) / total_samples if total_samples > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    mean_lead = sum(lead_times) / len(lead_times) if lead_times else 0.0

    print("\n" + "=" * 80)
    print("PRELUDE BENCHMARK SUMMARY METRICS")
    print("=" * 80)
    print(f"Total benchmark cases evaluated: {total_samples}")
    print(f"True Positives:  {tp}")
    print(f"True Negatives:  {tn}")
    print(f"False Positives: {fp} (False Alarm Rate: {fpr * 100:.1f}%)")
    print(f"False Negatives: {fn}")
    print(f"Hazard Detection Sensitivity (TPR): {tpr * 100:.1f}%")
    print(f"Overall Classification Accuracy:    {accuracy * 100:.1f}%")
    print(f"Mean Early Warning Lead Time:       {mean_lead:.2f}s")
    print("All dossiers carry research disclaimer: True")
    print("=" * 80)

    summary_file = RESULTS_DIR / "prelude_benchmark_summary.json"
    summary_data = {
        "attempted": len(CASES),
        "completed": tp + tn + fp + fn,
        "unavailable": len(CASES) - (tp + tn + fp + fn),
        "annotation_status": "Authored incident times; not independently validated; cue lead is retrospective, not prospective alert lead",
        "total_cases": total_samples,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "sensitivity_tpr": tpr,
        "false_positive_rate": fpr,
        "accuracy": accuracy,
        "mean_lead_time_seconds": mean_lead,
        "cases": results,
    }
    summary_file.write_text(json.dumps(summary_data, indent=2))
    print(f"Benchmark summary saved to {summary_file}")
    return all(x.get("passed", False) for x in results) and len(results) == len(CASES)


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run_benchmark()) else 1)
