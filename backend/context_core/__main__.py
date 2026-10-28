"""CLI: analyze a pair, or rank an edited clip against a local collection."""

import argparse
import json
from pathlib import Path

from .alignment import analyze

parser = argparse.ArgumentParser(description="CONTEXT visual evidence engine")
parser.add_argument("edited", type=Path)
parser.add_argument("sources", nargs="+", type=Path)
parser.add_argument("--output", type=Path, default=Path("evidence.json"))
args = parser.parse_args()
results = []
for source in args.sources:
    try:
        evidence = analyze(source, args.edited)
        results.append({"path": str(source), "evidence": evidence})
    except ValueError as exc:
        results.append({"path": str(source), "error": str(exc)})
results.sort(key=lambda r: r.get("evidence", {}).get("coverage", -1), reverse=True)
report = (
    results[0]["evidence"]
    if len(results) == 1 and "evidence" in results[0]
    else {"candidates": results, "scope": "provided_local_sources_only"}
)
args.output.write_text(json.dumps(report, indent=2))
print(f"Evidence saved to {args.output}")
