# HANDOFF (keep under 40 lines; update at end of every session)
Updated: Sat Oct 31 2026, ~02:20 IST
## Status
- Phase: FIX
- Decision: FIX (docs/AUDIT.md). G1/G2/G3/G5 now pass; G6 partly fixed (README/script/story claims done). No pivot.
## Done
- Audit written (docs/AUDIT.md). Tests 172 pass, web build green, eval reproduces (ffmpeg 8.1.2 only).
- Hero bundle committed (fe01363): eval/hero-v1/ (1.0 MB), results.json derived from fresh run; rebuild: scripts/build_hero_bundle.py.
- Off-domain cleanup committed (0b1736e, c8340d2): film demo, Big Buck Bunny eval, Artemis web suite and test strings removed.
- Hero demo path committed (8446196): /api/demo/hero, UI button, Docker fix; 172 tests pass, web build green. Not pushed.
- Claims pass committed (878a1cb): README/demo-script/story.json fixed against eval/hero-v1 + execution-v1 results; AUDIT G5, hero-validation 6 s, 172 tests. Not pushed.
## Failing / risks
- Hero button only API-verified in Docker, never click-tested in a browser.
- Terminal-abstain claim cut (46.3% only in prose docs). Render (11.5 MB) predates script edits: re-render before submit.
- SAM gate: original run errored on mask parsing; passing figures are the rescored replay (disclosed in README).
- Open: docs/*.md (model-card, submission, source-discovery, domain-admission, release-notes) still cite hyperfine/184 tests; demo script only partly rewritten.
## Next (ordered)
1. Click-test hero button in a real browser.
2. Fix remaining docs/*.md claims (hyperfine, 184 tests); then rewrite demo script and re-render video.
## Facts to not re-derive
- Hero: eval/hero-v1 (omission found via AUDIO match; visual alone = insufficient_evidence; Muse saw panel text in source only). Clip: cache qualification, 18 s     - Cut interval(s): 6.0-10.0 s (edit at 6.0)     - Eval results file: eval/execution-v1/full-results/results.json
- Option 3 deferred: NASA allowlist in retrieval.py, ablation scripts/docs; revisit after hero bundle if README links to them.
