#!/usr/bin/env bash
# Quiet runner: last 30 lines only. Use -m to skip live/slow tests once you know the marker names.
.venv/bin/python -m pytest -q -x "$@" 2>&1 | tail -30
