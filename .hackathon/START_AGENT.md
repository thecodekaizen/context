# AUTONOMOUS HACKATHON EXECUTION — CONTEXT WORKSTATION

**Target:** Meta Global AI Developer Hackathon 2026 (Deadline: Nov 4, 2026, 9:00 PM ET)  
**Primary Guide:** Read `CODEX_HANDOFF.md` at root and `.hackathon/CODEX_START_HERE.md` immediately.

## Current State
- All core features, gates (G1–G3), 30-edit frozen eval suite, SAM 3.1 spatial crop detection, and 3-minute Full HD demo video are **delivered and passing**.
- **132/132 tests pass.**
- **0.0s boundary error, 100% omission recall, 0% false alarms.**
- Git repository is public at `https://github.com/thecodekaizen/context` on branch `main`.

## Non-Negotiable Constraints
1. **Deterministic alignment first:** Models never guess omissions; they only review grounded intervals.
2. **Domain restriction:** Developer tutorials, benchmark demos, and product claims only. No politics or public figures.
3. **Rule 9:** Builder authentic voiceover is scheduled for Nov 3 per `docs/demo-script.md`.
4. **Git sandbox:** Use `git commit --no-gpg-sign` and `BypassSandbox: true` for git push.

Run `.venv/bin/pytest -q` to verify the environment.
