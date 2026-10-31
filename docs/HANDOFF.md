# HANDOFF (keep under 40 lines; update at end of every session)
Updated: Sat Oct 31 2026, ~10:20 IST (pushed: main 5d4b962 + this commit)
## Status
- Phase: FIX
- Decision: FIX. Claims audit fixes 1-9 applied (2018a22); real-v1 committed and pushed. Veil dropped (failed its own 90% gate; no rerun on adjusted labels).
## Done
- Audit written (docs/AUDIT.md). Tests 172 pass, web build green, eval reproduces (ffmpeg 8.1.2 only).
- Hero bundle committed (fe01363): eval/hero-v1/ (1.0 MB), results.json derived from fresh run; rebuild: scripts/build_hero_bundle.py.
- Off-domain cleanup committed (0b1736e, c8340d2): film demo, Big Buck Bunny eval, Artemis web suite and test strings removed.
- Hero demo path committed (8446196): /api/demo/hero, UI button, Docker fix; 172 tests pass, web build green. Not pushed.
- Docs claims pass af5fda3 (model-card, submission, source-discovery, release-notes: hyperfine removed, 172 tests). Demo script rewritten (5315b3d, a445f18, c9e5abf): 264 words, reveal-first, Muse 0.009 us sentence. Not pushed.
- Claims pass committed (878a1cb): README/demo-script/story.json fixed against eval/hero-v1 + execution-v1 results; AUDIT G5, hero-validation 6 s, 172 tests. Not pushed.
## Failing / risks
- Hero button only API-verified in Docker, never click-tested in a browser.
- Terminal-abstain claim cut (46.3% only in prose docs). Render (11.5 MB) predates script edits: re-render before submit.
- SAM gate: original run errored on mask parsing; passing figures are the rescored replay (disclosed in README).
- Open: story.json still matches the old script; domain-admission.md, hero-validation.md, ANTIGRAVITY_HANDOFF.md may still mention hyperfine (unchecked).
- Resolved: Muse excerpt offset OK (source excerpt = 4-12 s, so cited 2-5 s = source 6-9 s, inside the cut); script reworded to 'coincide' / 'generic conditions'.
- Open: story.json narration still differs from docs/demo-script.md (264 words); README video size/release link are TBD until re-render.
## Next (ordered)
1. Click-test hero button in a real browser.
2. Align story.json to demo-script (264 words, 7 segments), re-render, then restore README video size/link; check remaining hyperfine mentions.
3. Stopwatch run of script; narrated real clip; one live Muse call to confirm API; claim credits. Deadline Wed Nov 4 22:30 IST.
## Facts to not re-derive
- Hero: eval/hero-v1 (omission found via AUDIO match; visual alone = insufficient_evidence; Muse saw panel text in source only). Clip: cache qualification, 18 s     - Cut interval(s): 6.0-10.0 s (edit at 6.0)     - Eval results file: eval/execution-v1/full-results/results.json
- Option 3 deferred: NASA allowlist in retrieval.py, ablation scripts/docs; revisit after hero bundle if README links to them.
## real-v1 (Oct 31)
- eval/real-v1: 9 FOSDEM 2022 talks, 81 cases. Recall 32/36 = 88.9% (>=80 pass); benign FA 0/45 = 0% (<10 pass). Misses: async_sqlalchemy middle_cut/crop_omission/audio_only, concurrency early_cut.
- Muse Voice (POST api.meta.ai/v1/asr/transcribe, multipart request+audio, ENDPOINTING) on one 60 s clip (python_spyql): 2 turns with startMs/endMs only; no word-level fields. Transcript misheard 'SPyQL' as 'Spikewell'.
