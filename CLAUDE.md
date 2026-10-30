# CONTEXT: hackathon project (Meta Global AI Developer Hackathon, Indie track, solo)

Internal deadline: Wed Nov 4, noon ET (22:30 IST). Official hard stop 9 PM ET. Public repo, new commits only.

## What it is
Pre-publication QA for technical videos: given a raw recording and an edited highlight, find what the
edit removed (cut intervals, crops) with deterministic alignment, show both side by side, export an
evidence dossier. Domain: developer tutorials, benchmarks, product demos ONLY. No news, politics, war,
real public figures.

## Non-negotiable rules
1. Deterministic first. The aligner proves an omission exists; the Meta model (Muse Spark) may only
   explain an omission tied to a matched interval. No match => "no material omission".
2. Never edit frozen eval labels/manifests (execution-v1). Never change a label after seeing a result.
3. Never claim more than the repo proves: no "proof", "verdict", "no existing tool can". Say "evidence".
4. SAM 3.1 is experimental here (passes only the frozen chart-bar replay). Do not claim it as core.
5. Every number in the demo must exist in a committed results file. Disclose: evals are scripted cuts.

## Commands (VERIFY in the first session, then fix this section)
- Tests: `bash scripts/t.sh`   Build: `cd web && npm run build`   Python: pytest
- Secrets live in .env (never read, never commit).

## Working style (token discipline)
- Read only files named in the task. No repo-wide scans; use Grep, then Read a line range.
- Run tests only via scripts/t.sh. Never paste long logs.
- Small diffs. One task per session. Commit after each green task.
- State lives in docs/HANDOFF.md. Update it (max 15 lines) before ending a session.
- Final replies: 5 lines max (done / failing / next / blockers / decision needed).

## Compact instructions
When compacting keep: current task, failing tests, decisions made, files touched, deadline.
