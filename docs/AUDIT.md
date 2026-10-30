# AUDIT — 2026-10-31 ~02:00 IST (read-only; HEAD ef5052d, tree clean)

| Gate | Result | Evidence |
|---|---|---|
| G1 tests+build green | **PASS** | `scripts/t.sh`: 184 passed. `npm run build`: exit 0. |
| G2 eval reproducible from committed files | **PASS (caveat)** | Re-ran `evaluate(full=True)` to scratch: results.json identical to `eval/execution-v1/full-results/results.json`; manifest sha256 matches. Edit MP4s are NOT committed (`data/` gitignored); they are regenerated and hash-checked, so this only reproduces on ffmpeg 8.1.2 (manifest pin). |
| G3 clean-clone demo ≤3 commands | **FAIL** | Docker: 2 commands, but `/api/demo/benchmark` and `/api/demo/crop` return 404, because the image copies neither `eval/` nor `data/execution-v1/edits`. The hero clip (cache qualification) has no app entry point. Its media, case manifest and domain reviews exist only in gitignored `data/`. On a clean clone a hero upload is refused with `insufficient_evidence` (`domain_policy.py:66`). The local path needs at least 7 commands plus an eval run, a `build_cache_qualification_case.py` run and a manual upload. `.env.example`: present. |
| G4 Meta model contributes on hero clip | **PASS (local only)** | Muse Spark 1.2 is gated by `meta.py:23` (grounded omission or refusal). On the hero 6.0–10.0 s omission it read "WARM CACHE ONLY / COLD-START SETUP IS EXCLUDED" from 3 sampled source frames and returned `inconclusive`. Saved response: `data/technical-20261030T140841Z-1e14f9/context/audio-change-0/provider-response.json`, **gitignored, not committed**. SAM 3.1 on the hero clip: 0 masks, 0% panel recall (`data/field-validation/.../sam-panel/result.json`, not committed). SAM contributes nothing there; crop margins come from OpenCV. |
| G5 domain policy enforced | **PASS (after cleanup)** | Code: per-hash review gate with exclusions politics/news/wartime/public figures (`domain_policy.py:25`), applied on upload and demo paths. The NASA Artemis dossier (`docs/audit/evidence/fresh-upload-dossier.json`) was never committed: `docs/audit/` is gitignored and git history has no such file. The Big Buck Bunny film demo was out of domain and has been removed (c8340d2). |
| G6 script numbers match data | **FAIL (partial)** | Match `full-results/results.json`: 30 cases, 3 sources, 12 positive, 15/15 intervals, 0.0 s boundary error, 0/18 benign, rule of three 3/18 ≈ 16.7%. Match code: 4 Hz (`media.py:12` RATE=4), 184 tests. Hero-clip claims are not in any committed results file, only in prose in `docs/hero-validation.md`: 18→14 s, 6–10 s cut, 25% area crop (960/1280), Muse inconclusive, SAM zero masks. No committed evidence at all for "terminal benchmark abstained". Inconsistencies: `hero-validation.md:22` says 5.000–10.000 s against 6–10 elsewhere; README says "171 tests" twice against the actual 184. |

## Eval numbers as stored (`eval/execution-v1/full-results/results.json`, 30 cases)
Interval recall 1.0 (15/15) · mean boundary error 0.0 s · benign false alarms 0/18 (rate 0.0) · kill switch false · passed true.
Friday 10-case subset: same metrics. SAM gate (`sam-gate/rescored-results`): 10/10 crops, mean pixel recall 0.9995, mean IoU 0.844.
Disclose: all 30 are scripted FFmpeg edits of 3 authored CC0 recordings.

## Recommendation: **FIX** (all fails fixable in about 4 h; no pivot)
G1/G2 already pass, so there are no grounds for a pivot.

| # | Task | Gate | Est |
|---|---|---|---|
| 1 | Commit a hero bundle (e.g. `eval/hero-v1/`): source/omission/crop MP4s, case-manifest, 3 domain reviews, evidence.json, provider-response.json, SAM panel result.json. Frozen copy; do not alter labels. | G3 G4 G6 | 1.0 h |
| 2 | Add `POST /api/demo/hero` serving the committed bundle, plus a UI button. Docker: `COPY eval/` and commit or generate the 2 benchmark edit MP4s so the existing demo buttons work. | G3 | 1.5 h |
| 3 | ~~Remove NASA dossier~~ (never committed, gitignored). Film demo removed (c8340d2). | G5 | done |
| 4 | Either commit a terminal-abstain result file or cut that line from demo-script/story.json. Fix `hero-validation.md:22` (5→6 s) and README 171→184. | G6 | 0.5 h |
| 5 | G2 in Docker: ffmpeg in python:3.12-slim is not 8.1.2, so the eval hash check would fail there. Document "eval reproduces on ffmpeg 8.1.2 only" in the README. | G2 | 0.2 h |

Total ≈ 3.5 h. Do 1→2 first; they unblock the demo recording on Monday.
