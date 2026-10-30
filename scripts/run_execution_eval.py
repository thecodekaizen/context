"""Convenience runner for frozen execution evaluation suite."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from scripts.execution_eval import evaluate

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "full"
    report = evaluate(full=(action in ("full", "--full")))
    sys.exit(2 if report["kill_switch"] else 0 if report["passed"] else 1)
