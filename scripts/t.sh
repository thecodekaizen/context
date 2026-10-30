#!/usr/bin/env bash
# Quiet test runner. Prints only the last lines. EDIT the cd/command to match the repo.
set -uo pipefail
[ -d backend ] && cd backend
python -m pytest -q -x 2>&1 | tail -30
