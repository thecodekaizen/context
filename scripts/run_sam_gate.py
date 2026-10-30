"""Convenience runner for frozen SAM 3.1 spatial crop gate."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from scripts.execution_sam_gate import evaluate

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "replay"
    evaluate(replay=(action in ("replay", "--replay")))
