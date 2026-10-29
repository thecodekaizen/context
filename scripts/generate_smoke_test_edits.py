"""Generate 5 test edits for the 45-minute CONTEXT smoke-test gate.
1. honest_shortening_1 (harmless shortening, not misleading)
2. honest_shortening_2 (harmless shortening, not misleading)
3. deceptive_omission (context cut, misleading)
4. reorder (causal/chronological inversion, misleading)
5. reversed_claim (polarity/meaning inversion, misleading)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from context_core.alignment import analyze
from context_core.media import run
SOURCE = ROOT / "data/real-investigation-input/download.mp4"
OUT_DIR = ROOT / "data/smoke_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EDITS = {
    "honest_shortening_1": {
        "ground_truth": "not_misleading",
        "description": "Opening statement trimmed cleanly (0s to 20s). Meaning preserved.",
        "intervals": [(1.0, 20.0)],
        "reorder": False,
    },
    "honest_shortening_2": {
        "ground_truth": "not_misleading",
        "description": "Launch director poll and liftoff sequence (47s to 72s). Self-contained, meaning preserved.",
        "intervals": [(47.0, 72.0)],
        "reorder": False,
    },
    "deceptive_omission": {
        "ground_truth": "misleading",
        "description": "Omits opening qualification (1.0-12.0) and middle mission context, splicing pad view directly into Mars return.",
        "intervals": [(12.0, 20.0), (84.0, 90.0)],
        "reorder": False,
    },
    "reorder": {
        "ground_truth": "misleading",
        "description": "Swaps liftoff (57-72s) before launch authorization (45-53s). Inverts causal order.",
        "intervals": [(57.0, 72.0), (45.0, 53.0)],
        "reorder": True,
    },
    "reversed_claim": {
        "ground_truth": "misleading",
        "description": "Cuts intro qualification 'Fifty years after' leaving only 'we last left footprints... live on pad 39B'.",
        "intervals": [(3.5, 10.0), (12.0, 19.0)],
        "reorder": False,
    },
}


def build_edit(name, spec):
    target = OUT_DIR / f"{name}.mp4"
    parts = spec["intervals"]
    graph = ";".join(
        f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}];"
        f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]"
        for i, (a, b) in enumerate(parts)
    )
    v_inputs = "".join(f"[v{i}]" for i in range(len(parts)))
    a_inputs = "".join(f"[a{i}]" for i in range(len(parts)))
    graph += f";{v_inputs}concat=n={len(parts)}:v=1:a=0[vout];{a_inputs}concat=n={len(parts)}:v=0:a=1[aout]"
    run([
        "ffmpeg", "-v", "error", "-y",
        "-i", str(SOURCE),
        "-filter_complex", graph,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        str(target),
    ])
    return target


def run_benchmark():
    results = {}
    print("=" * 70)
    print("CONTEXT SMOKE-TEST GATE: DATASET GENERATION & TEMPORAL ALIGNMENT")
    print("=" * 70)
    print(f"Source video: {SOURCE.name} (Duration: 151.5s, NASA Artemis I Talk)")

    for name, spec in EDITS.items():
        print(f"\n--- Generating {name} ---")
        path = build_edit(name, spec)
        print(f"Target built: {path.name} (size: {path.stat().st_size} bytes)")

        # Run temporal alignment
        print("Running deterministic visual sequence alignment...")
        alignment = analyze(SOURCE, path)
        coverage = alignment.get("coverage", 0)
        findings = alignment.get("findings", [])
        segments = alignment.get("segments", [])

        # Measure temporal error against known ground truth cut points
        first_interval = spec["intervals"][0]
        match_segments = [s for s in segments if s.get("kind") == "match" and s.get("source_start") is not None]
        if match_segments:
            detected_source_start = match_segments[0]["source_start"]
            expected_source_start = first_interval[0]
            temporal_error = abs(detected_source_start - expected_source_start)
        else:
            temporal_error = 999.0

        print(f"Alignment coverage: {coverage:.1%}")
        print(f"Detected initial source start: {detected_source_start}s (Expected: {first_interval[0]}s, Error: {temporal_error:.2f}s)")
        print(f"Detected omissions/intervals: {len(findings)}")

        results[name] = {
            "name": name,
            "ground_truth": spec["ground_truth"],
            "description": spec["description"],
            "intervals": spec["intervals"],
            "temporal_error_seconds": round(temporal_error, 2),
            "alignment_passed": temporal_error <= 2.0,
            "coverage": round(coverage, 3),
            "findings_count": len(findings),
        }

    out_file = OUT_DIR / "smoke_test_alignment.json"
    out_file.write_text(json.dumps(results, indent=2))
    print(f"\nAlignment benchmark results saved to {out_file}")
    return results


if __name__ == "__main__":
    run_benchmark()
