# HANDOFF (keep under 40 lines; update at end of every session)
Updated: Sat Oct 31 2026, ~02:05 IST
## Status
- Phase: FIX
- Decision: FIX (docs/AUDIT.md). G1/G2 pass; G3, G5, G6 fail but fixable in ~3.5 h. No pivot.
## Done
- Audit written (docs/AUDIT.md). Tests 172 pass, web build green, eval reproduces (ffmpeg 8.1.2 only).
- Hero bundle committed (fe01363): eval/hero-v1/ (1.0 MB), results.json derived from fresh run; rebuild: scripts/build_hero_bundle.py.
- Off-domain cleanup committed (0b1736e, c8340d2): film demo, Big Buck Bunny eval, Artemis web suite and test strings removed.
- Hero demo path committed (8446196): /api/demo/hero, UI button, Docker fix; 172 tests pass, web build green. Not pushed.
## Failing / risks
- G3 mostly done: POST /api/demo/hero (backend/context_core/hero.py) + UI button; benchmark/crop demos removed; Dockerfile copies hero bundle. Clean-clone docker verified (API only).
- G6 claims pass applied (README, demo-script, story.json): terminal-abstain claim cut (46.3% only in prose docs, no results file); 0/6 corrected to 0/5; render is 11.5 MB and predates the script edits, so re-render before submit.
- Still open: click-test hero button in a browser; rest of demo script rewrite; docs/*.md (model-card, submission, source-discovery) still mention hyperfine/forensic; release-notes says 184 tests.
## Next (ordered)
1. Click-test hero button in a real browser.
2. Fix remaining docs/*.md claims (hyperfine, 184 tests); then rewrite demo script and re-render video.
## Facts to not re-derive
- Hero: eval/hero-v1 (omission found via AUDIO match; visual alone = insufficient_evidence; Muse saw panel text in source only). Clip: cache qualification, 18 s     - Cut interval(s): 6.0-10.0 s (edit at 6.0)     - Eval results file: eval/execution-v1/full-results/results.json
- Option 3 deferred: NASA allowlist in retrieval.py, ablation scripts/docs; revisit after hero bundle if README links to them.
