"""Derive rule-of-three 95% upper bounds on the benign false-alarm rate into eval/upper_bounds.json.

execution-v1 and real-v1 are reported separately and never pooled.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITES = {
    "execution-v1": ROOT / "eval/execution-v1/full-results/results.json",
    "real-v1": ROOT / "eval/real-v1/results.json",
}


def main():
    out = {
        "method": "Rule of three: with 0 false alarms in n benign cases, the 95% upper bound on the false-alarm rate is about 3/n. Scripted edits only; assumes independent cases, which these (several recipes per source) are not, so treat as indicative.",
        "suites": {},
    }
    for name, path in SUITES.items():
        cases = [c for c in json.loads(path.read_text())["cases"] if c["benign"]]
        alarms = sum(c["predicted"] > 0 for c in cases)
        entry = {"results_file": str(path.relative_to(ROOT)), "benign_cases": len(cases), "false_alarms": alarms}
        entry["upper_bound_95"] = round(3 / len(cases), 4) if alarms == 0 else None
        out["suites"][name] = entry
    (ROOT / "eval/upper_bounds.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["suites"]))


if __name__ == "__main__":
    main()
