"""Recheck timing only; retain original scores, labels and model receipts."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.alignment import analyze
from context_core.media import digest
from run_smoke_test_classification import measure_boundaries

root = ROOT / "data/gate-v2"
original = json.loads((root / "results.json").read_text())
manifest = json.loads((root / "manifest.json").read_text())
assert digest(root / "manifest.json") == original["manifest_sha256"]
report = {
    "original_results_sha256": digest(root / "results.json"),
    "changes": "No recipes, labels, media or Meta classifications changed. Added per-quarter audio corroboration to reject windows straddling a splice; require >=0.5s support within the tested piece to exclude frame-grid spillover from its neighbor.",
    "semantic_correct": original["semantic_correct"],
    "honest_edits_not_accused": original["honest_edits_not_accused"],
    "scope": original["scope"],
    "results": [],
}
for previous in original["results"]:
    name = previous["case"]
    spec = manifest["cases"][name]
    assert digest(root / f"{name}.mp4") == spec["sha256"]
    alignment = analyze(root / manifest["source"], root / f"{name}.mp4")
    audio = alignment["audio_alignment"]["segments"]
    timing = measure_boundaries(
        {"segments": alignment["segments"] + audio}, spec["intervals"]
    )
    row = {
        "case": name,
        "decision": previous["decision"],
        "timing": timing,
        "audio_segments": audio,
        "visual_timing": measure_boundaries(alignment, spec["intervals"]),
    }
    report["results"].append(row)
    print(name, "timing", timing["passed"], flush=True)
report["all_boundaries_pass"] = all(
    row["timing"]["passed"] for row in report["results"]
)
report["scoped_smoke_passed"] = (
    report["all_boundaries_pass"]
    and report["semantic_correct"] >= 4
    and report["honest_edits_not_accused"]
)
report["original_bare_cut_gate_passed"] = False
(root / "timing-recheck.json").write_text(json.dumps(report, indent=2))
print(
    json.dumps(
        {
            key: report[key]
            for key in (
                "semantic_correct",
                "honest_edits_not_accused",
                "all_boundaries_pass",
                "scoped_smoke_passed",
            )
        }
    ),
    flush=True,
)
