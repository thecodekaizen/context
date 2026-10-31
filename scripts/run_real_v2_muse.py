"""eval/real-v2-muse: Muse review on real-v1 talks, checked in code against contract.json.

Scripted cuts, recorded responses. `--dry` builds packs and checks admission with no API call.
"""

import argparse
import asyncio
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
from dotenv import load_dotenv

from context_core.alignment import analyze
from context_core.comparison import comparison_evidence
from context_core.context_pack import build_pack
from context_core.domain_policy import require_hashes
from context_core.media import digest
from context_core.meta import interpret

BASE = ROOT / "eval/real-v2-muse"
WORK = ROOT / "data/real-v2-muse"
TOL = 0.5
INTENT = re.compile(
    r"misleading|deceiv|decepti|manipulat|conceal|\bhid(e|ing|den)\b|cover(ing)? up|"
    r"dishonest|intentional|on purpose|agenda|propaganda",
    re.I,
)


def texts(interp):
    yield interp["possible_effect"]
    yield interp["uncertainty"]
    for o in interp["observations"]:
        yield o["text"]


def check(interp, omission):
    lo, hi = omission["source_start"] - TOL, omission["source_end"] + TOL
    src = [c for o in interp["observations"] for c in o["citations"] if c["media"] == "source"]
    out_of_interval = [c for c in src if not (lo <= c["media_start"] and c["media_end"] <= hi)]
    intent = [t for t in texts(interp) if INTENT.search(t)]
    checks = {
        "schema": bool(interp["observations"]),
        "timestamps_in_interval": bool(src) and not out_of_interval,
        "no_intent_claims": not intent,
        "abstains_when_ungrounded": not (
            interp["classification"] != "inconclusive" and not interp["observations"]
        ),
    }
    checks["case_pass"] = all(checks.values())
    return checks, {"out_of_interval_citations": out_of_interval, "intent_matches": intent}


async def run_case(case_id, sources, manifest, dry):
    case = next(c for c in manifest["cases"] if c["id"] == case_id)
    source = ROOT / sources[case["source"]]["clip_path"]
    target = ROOT / case["video"]
    d = WORK / case_id
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, d / "original.mp4")
    shutil.copyfile(target, d / "edited.mp4")
    evidence = comparison_evidence(analyze(source, target))
    evidence["selection_status"] = "matched"
    finding = evidence["review_targets"][0]
    evidence["findings"] = evidence["findings"] + (
        [finding] if finding not in evidence["findings"] else []
    )
    clips = build_pack(d, evidence, finding["id"])
    hashes = {"source": evidence["source"]["sha256"], "edited": evidence["edited"]["sha256"]}
    if dry:
        require_hashes(hashes)
        return {"id": case_id, "dry": True, "finding": finding, "clips": [
            {k: v for k, v in c.items() if k in ("id", "start", "end")} for c in clips]}
    review = await interpret(evidence, finding["id"], clips)
    om = review["omission_evidence"]
    checks, detail = check(review["interpretation"], om)
    raw = d / "context" / finding["id"] / "provider-response.json"
    resp = BASE / "responses" / f"{case_id}.json"
    payload = json.loads(raw.read_text())
    resp.write_text(json.dumps({
        "case": case_id, "model": payload.get("model"), "usage": payload.get("usage"),
        "omitted_interval": [om["source_start"], om["source_end"]],
        "clips": review["clips"], "interpretation": review["interpretation"],
        "checks": checks, "check_detail": detail,
        "disclosure": "scripted cuts, recorded responses",
    }, indent=2))
    return {"id": case_id, "omitted_interval": [om["source_start"], om["source_end"]],
            "classification": review["interpretation"]["classification"], **checks}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    load_dotenv(ROOT / ".env")
    contract = json.loads((BASE / "contract.json").read_text())
    manifest = json.loads((ROOT / "eval/real-v1/manifest.json").read_text())
    sources = json.loads((ROOT / "eval/real-v1/sources.json").read_text())["sources"]
    (BASE / "responses").mkdir(exist_ok=True)
    rows = []
    for cid in contract["cases"]:
        if args.only and cid != args.only:
            continue
        try:
            rows.append(await run_case(cid, sources, manifest, args.dry))
        except Exception as exc:  # recorded, never dropped
            rows.append({"id": cid, "error": repr(exc), "case_pass": False})
        print(json.dumps(rows[-1], default=str)[:400], flush=True)
    if not args.dry:
        passed = sum(1 for r in rows if r.get("case_pass"))
        (BASE / "results.json").write_text(json.dumps({
            "contract_sha256": digest(BASE / "contract.json"),
            "disclosure": "scripted cuts, recorded responses; 4 clips, not a rate estimate",
            "n_cases": len(rows), "n_passed": passed, "target": 3, "target_met": passed >= 3,
            "cases": rows,
        }, indent=2))


asyncio.run(main())
