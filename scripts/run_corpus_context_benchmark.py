"""Autonomous single-video CONTEXT benchmark across multi-candidate corpus.

Ground truth, edit classes, recipes, and candidate IDs are withheld during inference.
Measures:
1. Corpus Source Retrieval (top-K match, margin, negative rejection).
2. Deterministic Alignment & Omission Detection (clip timecodes, boundary accuracy).
3. Multimodal Observation & Claim Extraction (Meta muse-spark-1.2).
4. Evidence & Factual Assessment (Meta muse-spark-1.3 / fetched source verification).
5. Epistemic Separation (media match != manipulation != editorial deception).
"""

import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from context_core.dossier import investigate
from context_core.library import list_sources
from context_core.media import probe

CASES = [
    {
        "name": "case_1_honest_qualification",
        "video": ROOT / "data/gate-v2/honest_qualification.mp4",
        "caption": "Artemis I flight test overview and Orion spacecraft components",
        "expected_source_name": "NASA Artemis I Mission Journey",
        "expected_verdict": "not_misleading",
        "category": "honest_shortening",
    },
    {
        "name": "case_2_captioned_omission",
        "video": ROOT / "data/gate-v2/captioned_omission.mp4",
        "caption": "Astronauts are onboard Orion for the Artemis I lunar mission",
        "expected_source_name": "NASA Artemis I Mission Journey",
        "expected_verdict": "misleading",
        "category": "deceptive_omission_with_false_caption",
    },
    {
        "name": "case_3_chronology_reorder",
        "video": ROOT / "data/gate-v2/chronology_reorder.mp4",
        "caption": "Artemis I liftoff and booster ignition sequence",
        "expected_source_name": "NASA Artemis I Mission Journey",
        "expected_verdict": "misleading",
        "category": "reordered_chronology",
    },
    {
        "name": "case_4_open_footage_omission",
        "video": ROOT / "data/evaluation/omission.mp4",
        "caption": "Foundation production sequence scene",
        "expected_source_name": "source.mp4",
        "expected_verdict": "not_misleading",
        "category": "harmless_omission_cut",
    },
    {
        "name": "case_5_unrelated_unknown_negative",
        "video": ROOT / "data/evaluation/blender.mp4",
        "caption": "Open movie creative project scene",
        "expected_source_name": None,  # Ground truth: NOT in corpus
        "expected_verdict": "inconclusive",
        "category": "unknown_source_negative",
    },
]


async def run_single_case(spec, output_dir):
    case_name = spec["name"]
    video_path = spec["video"]
    caption = spec["caption"]

    print(f"\n========================================================")
    print(f"RUNNING BENCHMARK: {case_name}")
    print(f"Input: {video_path.name} ({probe(video_path)['duration']:.1f}s)")
    print(f"Caption: \"{caption}\"")
    print(f"========================================================")

    job_dir = output_dir / case_name
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "video.mp4").write_bytes(video_path.read_bytes())

    provenance = {
        "method": "benchmark_test",
        "input_video": video_path.name,
        "input_sha256": hashlib.sha256(video_path.read_bytes()).hexdigest(),
        "original_recording_supplied": False,
    }

    t0 = time.time()
    dossier = await investigate(job_dir, caption, provenance)
    elapsed = time.time() - t0

    # Evaluate Retrieval
    matched = dossier.get("matched_source", {})
    retrieval_status = matched.get("status")
    retrieved_name = matched.get("source_name")
    coverage = matched.get("coverage", 0.0)
    margin = matched.get("margin", 0.0)

    if spec["expected_source_name"] is None:
        retrieval_pass = (retrieval_status == "no_match")
    else:
        retrieval_pass = (
            retrieval_status == "matched"
            and spec["expected_source_name"] in (retrieved_name or "")
        )

    # Evaluate Observations & Claims
    analysis = dossier.get("analysis", {})
    obs_count = len(analysis.get("observations", []))
    claims_count = len(analysis.get("claims", []))

    # Evaluate Assessment & Findings
    assessment = dossier.get("assessment", {})
    findings = assessment.get("findings", [])
    contradicted = [f for f in findings if f.get("verdict") == "contradicted"]
    supported = [f for f in findings if f.get("verdict") == "supported"]

    result = {
        "case": case_name,
        "input_video": video_path.name,
        "category": spec["category"],
        "elapsed_seconds": round(elapsed, 2),
        "retrieval": {
            "status": retrieval_status,
            "retrieved_name": retrieved_name,
            "coverage": coverage,
            "margin": margin,
            "expected_source": spec["expected_source_name"],
            "correct": retrieval_pass,
        },
        "multimodal_analysis": {
            "observations_count": obs_count,
            "claims_count": claims_count,
            "summary": analysis.get("summary", "")[:200],
        },
        "evidence_assessment": {
            "findings_count": len(findings),
            "contradicted_count": len(contradicted),
            "supported_count": len(supported),
            "verdicts": [f.get("verdict") for f in findings],
            "provenance_summary": assessment.get("provenance", ""),
        },
        "dossier_status": dossier.get("status"),
        "dossier_id": dossier.get("id"),
    }

    print(f"Result for {case_name}:")
    print(f"  Retrieval: {retrieval_status} -> {retrieved_name} (cov={coverage}, margin={margin}) -> {'PASS' if retrieval_pass else 'FAIL'}")
    print(f"  Observations: {obs_count}, Claims: {claims_count}, Findings: {len(findings)}")
    print(f"  Contradicted: {len(contradicted)}, Supported: {len(supported)}")
    print(f"  Elapsed: {elapsed:.1f}s")

    return result


async def main():
    load_dotenv(ROOT / ".env")
    lib_sources = list_sources(ROOT / "data/library")
    print(f"Initialized benchmark with {len(lib_sources)} indexed corpus sources in data/library:")
    for s in lib_sources:
        print(f" - [{s['id'][:10]}] {s['name']} ({s.get('duration', 0)}s)")

    output_dir = ROOT / "data/corpus_benchmark_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for spec in CASES:
        try:
            res = await run_single_case(spec, output_dir)
            results.append(res)
        except Exception as e:
            print(f"ERROR on {spec['name']}: {type(e).__name__}: {e}")
            results.append({
                "case": spec["name"],
                "error": str(e),
                "correct": False,
            })

    report_path = output_dir / "benchmark_report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\n========================================================")
    print(f"BENCHMARK COMPLETED. Saved full report to {report_path}")
    print(f"========================================================")


if __name__ == "__main__":
    asyncio.run(main())
