# HANDOFF (keep under 40 lines; update at end of every session)
Updated: Sat Oct 31 2026, ~02:00 IST
## Status
- Phase: FIX
- Decision: FIX (docs/AUDIT.md). G1/G2 pass; G3, G5, G6 fail but fixable in ~3.5 h. No pivot.
## Done
- Audit written (docs/AUDIT.md). Tests 172 pass, web build green, eval reproduces (ffmpeg 8.1.2 only).
- Off-domain cleanup committed (0b1736e, c8340d2): film demo, Big Buck Bunny eval, Artemis web suite and test strings removed.
## Failing / risks
- G3: hero clip has no committed bundle or app entry; /api/demo/benchmark and /crop 404 in Docker (eval/ + edit MP4s not in image).
- G6: hero numbers only in prose; no committed terminal-abstain result; README says 171 tests (now 172); hero-validation.md:22 says 5-10 s (should be 6-10).
- docs/AUDIT.md G5 row wrongly says NASA dossier was committed (it was gitignored).
## Next (ordered)
1. Commit hero bundle (eval/hero-v1/): MP4s, case-manifest, 3 domain reviews, evidence, Muse response, SAM panel result.
2. Add POST /api/demo/hero + UI button; Docker COPY eval/ and make benchmark edit MP4s available.
3. Fix README test count, hero-validation 5->6 s; commit or cut the terminal-abstain claim.
## Facts to not re-derive
- Hero clip: cache qualification, 18 s     - Cut interval(s): 6.0-10.0 s (edit at 6.0)     - Eval results file: eval/execution-v1/full-results/results.json
- Option 3 deferred: NASA allowlist in retrieval.py, ablation scripts/docs; revisit after hero bundle if README links to them.
