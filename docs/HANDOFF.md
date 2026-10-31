# HANDOFF (keep under 40 lines; update at end of every session)
Updated: Sat Oct 31 2026 ~11:15 IST (submission stages 1-3 + silent video done)
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
- (superseded) story.json now aligned in Stage 2.
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
## real-v2-muse (Stage 1, Oct 31; scripted cuts, recorded responses)
- Contract frozen first (b3df6e5). 4 middle_cut cases, 4 Muse calls total (0 retries), prompt unchanged. Operator (Vishnu Sharma) reviewed the 8 files; reviews recorded via review_content.py.
- Result: 2/4 pass (target 3 NOT met). Passed: type_safety, spyql. Missed: kafka (cited source 97-98 s, in the 2 s margin before the omitted 99-130 s), unicode (cited the whole 98-128 s excerpt, outside 100-130). All 4 classified inconclusive; no intent claims.
- Muse Voice: segment-level startMs/endMs only, no word timestamps; not wired.
- Next: Stage 2. Hero stays honest (do not claim Stage 1 passed). Any prompt change needs 4 NEW clips + disclosure.
## Stage 2 (Oct 31)
- README: real-v2 section, Limitations; story.json aligned to demo-script (266 words). Hero stays the honest inconclusive case (Stage 1 was 2/4).
- /claims: fixed crop attribution (separate fixture), Muse 'excerpt around' wording, README execution-v1 qualifier. No OVERCLAIM left known. Render still predates script: re-render before submit.
## Stage 3 (Oct 31)
- Clean clone (origin 7ff90aa): cold docker build 111 s, ready 0.6 s, hero endpoint 200. Demo path = 2 commands (build, run) + open browser + click hero button (button still not click-tested in a browser).
- gitleaks: 54 commits clean. Internal notes untracked + gitignored (still in history); checklist in docs/SUBMISSION_CHECKLIST.md (not SUBMISSION.md: case-collides with docs/submission.md).
## Video (Oct 31)
- Silent cut built from the live app on :8010: demo-video/out/ (gitignored): context-demo-silent.mp4 (141 s), captions.srt, cue-sheet.md. Build script is in the session scratchpad, not committed. Awaiting narration.wav -> mux, loudness-normalize, <3:00.
## Wrap (Oct 31)
- Done: real-v2-muse 2/4 (target 3 missed, reported); README limitations; story.json=script (266 w); SUBMISSION_CHECKLIST.md; internal notes untracked; hero button click-tested (Playwright); silent cut 141 s in demo-video/out/.
- Failing/open: Stage 1 target missed (hero stays honest case); user has not yet watched the silent cut; committed render in demo-video/renders is stale; README video size/link TBD.
- Next: user reviews silent cut -> narration.wav -> mux/normalize (<3:00) -> human steps in docs/SUBMISSION_CHECKLIST.md. Deadline Wed Nov 4 22:30 IST.
