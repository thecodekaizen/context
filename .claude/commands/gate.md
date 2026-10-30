---
description: Run eval + tests and report pass/fail against fixed thresholds
---
Run `bash scripts/t.sh`. Run the eval entrypoint documented in README (find it with Grep, do not scan the repo).
Thresholds (fixed): interval recall >= 80%, benign false alarms < 10%, scored separately.
Report: numbers, PASS/FAIL, and any regression versus docs/AUDIT.md. 5 lines max. Do not change code.
