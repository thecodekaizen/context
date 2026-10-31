"""eval/real-v1: generate scripted edits, freeze labels (prepare), then score the deterministic aligner (run).

No Muse/API calls; the domain-admission gate is not on this path.
"""

import argparse
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
from context_core.alignment import analyze
from context_core.grounded_omissions import grounded_omissions
from context_core.media import digest, run

from scripts.execution_eval import expected_omissions, score

BASE = ROOT / "eval/real-v1"
DATA = ROOT / "data/real-v1"
EDITS = DATA / "edits"
CODE = ["alignment.py", "audio_alignment.py", "grounded_omissions.py", "media.py"]


def label(recipe, duration):
    if recipe["transform"] == "audio_omission":
        start, end = recipe["audio_gap"]
        return [{"source_start": start, "source_end": end, "edit_position": start, "modality": "audio"}]
    return expected_omissions(recipe)


def generate(source, recipe, target):
    d = 270
    graph = []
    intervals = recipe["intervals"]
    for i, (a, b) in enumerate(intervals):
        graph += [
            f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]",
            f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]",
        ]
    graph.append("".join(f"[v{i}][a{i}]" for i in range(len(intervals))) + f"concat=n={len(intervals)}:v=1:a=1[video][audio]")
    t = recipe["transform"]
    vf = {"speed": "setpts=PTS/1.25", "crop": "crop=iw*0.8:ih*0.8,scale=960:540"}.get(t, "null")
    graph.append(f"[video]{vf},format=yuv420p[outv]")
    if t == "audio_omission":
        s, e = recipe["audio_gap"]
        graph += [
            "[audio]asplit[head][tail]",
            f"[head]atrim=0:{s},asetpts=PTS-STARTPTS[ah]",
            f"[tail]atrim={e}:{d},asetpts=PTS-STARTPTS[at]",
            f"[ah][at]concat=n=2:v=0:a=1,apad=whole_dur={d}[outa]",
        ]
    else:
        graph.append(f"[audio]{'atempo=1.25' if t == 'speed' else 'anull'}[outa]")
    run(["ffmpeg", "-v", "error", "-n", "-i", str(source), "-filter_complex", ";".join(graph),
         "-map", "[outv]", "-map", "[outa]", "-c:v", "libx264", "-crf", "32" if t == "reencode" else "22",
         "-c:a", "aac", "-movflags", "+faststart", str(target)])


def prepare():
    manifest_path = BASE / "manifest.json"
    if manifest_path.exists():
        raise SystemExit("manifest.json already frozen; do not regenerate labels")
    contract = json.loads((BASE / "contract.json").read_text())
    sources = json.loads((BASE / "sources.json").read_text())["sources"]
    EDITS.mkdir(parents=True, exist_ok=True)
    cases = []
    for name, src in sources.items():
        if src["excluded"]:
            continue
        for recipe in contract["recipes"]:
            target = EDITS / f"{name}-{recipe['name']}.mp4"
            if not target.exists():
                generate(ROOT / src["clip_path"], recipe, target)
            cases.append({
                "id": f"{name}-{recipe['name']}", "source": name, "recipe": recipe,
                "video": str(target.relative_to(ROOT)), "sha256": digest(target),
                "benign": recipe["benign"], "expected": label(recipe, 270),
            })
    manifest = {
        "contract_sha256": digest(BASE / "contract.json"),
        "sources_sha256": digest(BASE / "sources.json"),
        "clip_sha256": {n: s["clip_sha256"] for n, s in sources.items() if not s["excluded"]},
        "code_sha256": {f: digest(ROOT / "backend/context_core" / f) for f in CODE},
        "python": platform.python_version(),
        "ffmpeg": run(["ffmpeg", "-version"]).decode().splitlines()[0],
        "cases": cases,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Frozen {len(cases)} cases ({sum(c['benign'] for c in cases)} benign) before inference")


def evaluate():
    manifest = json.loads((BASE / "manifest.json").read_text())
    contract = json.loads((BASE / "contract.json").read_text())
    if digest(BASE / "contract.json") != manifest["contract_sha256"]:
        raise SystemExit("contract changed after freeze")
    for f, h in manifest["code_sha256"].items():
        if digest(ROOT / "backend/context_core" / f) != h:
            raise SystemExit(f"aligner code changed after freeze: {f}")
    sources = json.loads((BASE / "sources.json").read_text())["sources"]
    out = BASE / "cases"
    out.mkdir(exist_ok=True)
    rows = []
    for case in manifest["cases"]:
        src = ROOT / sources[case["source"]]["clip_path"]
        target = ROOT / case["video"]
        if digest(target) != case["sha256"]:
            raise SystemExit(f"edited bytes differ from freeze: {case['id']}")
        try:
            evidence = analyze(src, target)
            prediction = grounded_omissions(evidence)
            row = {"id": case["id"], "benign": case["benign"], "error": None,
                   **score(case["expected"], prediction["omissions"], contract)}
            (out / f"{case['id']}.json").write_text(json.dumps({"alignment": evidence, "prediction": prediction}, indent=2))
        except Exception as exc:  # recorded as a failure, never dropped
            row = {"id": case["id"], "benign": case["benign"], "error": repr(exc),
                   "expected": len(case["expected"]), "recovered": 0, "predicted": 0, "boundary_errors_seconds": []}
        rows.append(row)
        print(f"{row['id']}: {row['recovered']}/{row['expected']} rec, {row['predicted']} pred, err={row['error']}", flush=True)
    omit = [r for r in rows if not r["benign"]]
    benign = [r for r in rows if r["benign"]]
    expected = sum(r["expected"] for r in omit)
    recall = sum(r["recovered"] for r in omit) / expected if expected else None
    fa = sum(r["predicted"] > 0 for r in benign) / len(benign) if benign else None
    errs = [e for r in rows for e in r["boundary_errors_seconds"]]
    by_recipe = {}
    for r, c in zip(rows, manifest["cases"]):
        k = by_recipe.setdefault(c["recipe"]["name"], {"cases": 0, "expected": 0, "recovered": 0, "predicted_cases": 0})
        k["cases"] += 1; k["expected"] += r["expected"]; k["recovered"] += r["recovered"]; k["predicted_cases"] += r["predicted"] > 0
    report = {
        "manifest_sha256": digest(BASE / "manifest.json"),
        "n_cases": len(rows), "n_errors": sum(bool(r["error"]) for r in rows),
        "interval_recall": recall, "interval_recall_threshold": contract["minimum_interval_recall"],
        "recall_passed": recall is not None and recall >= contract["minimum_interval_recall"],
        "benign_false_alarm_rate": fa, "false_alarm_threshold_exclusive": contract["maximum_benign_false_alarm_rate_exclusive"],
        "false_alarm_passed": fa is not None and fa < contract["maximum_benign_false_alarm_rate_exclusive"],
        "boundary_error_seconds": sum(errs) / len(errs) if errs else None,
        "kill_switch": recall is not None and recall < contract["kill_below_interval_recall"],
        "by_recipe": by_recipe, "cases": rows,
    }
    report["passed"] = report["recall_passed"] and report["false_alarm_passed"]
    (BASE / "results.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in ("cases", "by_recipe")}))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["prepare", "run"])
    {"prepare": prepare, "run": evaluate}[p.parse_args().action]()
