# CODEX MASTER HANDOFF — CONTEXT Video Evidence Workstation

**Timestamp:** October 30, 2026, 11:37 AM IST  
**Repository:** [https://github.com/thecodekaizen/context](https://github.com/thecodekaizen/context) (Public)  
**Branch:** `main` (Latest commit: `ad4af1e`, working tree clean, pushed to origin)  
**Target Deadline:** Meta Global AI Developer Hackathon 2026 (Nov 4, 2026, 9:00 PM ET / Nov 5, 7:30 AM IST)  
**Status:** **G1–G3 GATES PASSED · 100% BENCHMARK RECALL · 133/133 TESTS PASSING · 3-MIN FULL HD DEMO RENDERED**

---

## 1. Executive Brief for Incoming Codex Agent

Welcome, Codex. All foundation engineering, frozen evaluation suites, spatial crop detection, and demo video rendering are **complete, tested, and passing**.

Do not rebuild the repository or revert to earlier ungrounded concepts. CONTEXT is a **deterministic-first video evidence workstation** that investigates deceptive edits in **developer tutorials, software benchmark demos, and commercial product claims**.

---

## 2. Current Verified System State

| Component | Status | Verification Command | Notes |
|---|---|---|---|
| **Backend Test Suite** | **133/133 Passed** | `.venv/bin/pytest -q` | 100% passing in ~16s |
| **Python Quality** | **0 Warnings / Clean** | `.venv/bin/ruff check backend scripts` | 53 files clean |
| **Frontend App** | **Production Built** | `cd web && npx tsc --noEmit && npx vite build` | React 19 + TS + Vite 7 |
| **Frozen Eval Suite** | **100% Recall, 0.0s Err** | `python scripts/run_execution_eval.py` | 30 edits in `eval/execution-v1` |
| **Benign Controls** | **0.0% False Alarms** | (Included in eval suite) | 18 controls (speed, trims, subs) |
| **SAM 3.1 Spatial Gate** | **10/10 Passed** | `python scripts/run_sam_gate.py` | >99.9% pixel recall, 84% IoU |
| **Demo Composition** | **0 Errors, WCAG AA** | `cd demo-video && npm run check` | Checked across 599 crafts |
| **3-Min Master MP4** | **Rendered & Tracked (8.0 MB)** | `demo-video/renders/context-demo-3min.mp4` | 180.00s, 1080p, 24fps, H.264/AAC |
| **Docker Packaging** | **Multi-stage Ready** | `docker build -t context .` | Node builder + Python runtime |

---

## 3. Strict Architectural Contracts (DO NOT VIOLATE)

1. **Deterministic Alignment First:**
   - Visual: 4Hz multi-scale feature grids (cosine matching).
   - Acoustic: Normalized cross-correlation on audio waveforms.
   - Grounding Gate: If the aligner finds no correspondence, output is strictly **`"no material omission"`**.
   - Foundation models (Meta Muse Spark 1.2) are **NEVER** allowed to assert an ungrounded omission. They only explain verified, bounded clips.

2. **Domain Boundary (Non-Political Whitelist):**
   - Strictly restricted to **developer tutorials, benchmark demos, and commercial product claims**.
   - No politics, elections, wartime footage, or real public figures.

3. **Rule 9 (Authentic Builder Voiceover):**
   - Hackathon Rule 9 requires an authentic human builder voiceover for the final demo video.
   - The master composition is rendered with silent WAV placeholders in `demo-video/assets/`.
   - The human builder will record their voice on Tuesday, Nov 3 using the script in [docs/demo-script.md](docs/demo-script.md).

4. **Git Protocol in Sandbox:**
   - Commit commands require `--no-gpg-sign` (sandbox isolation prevents SSH key access).
   - Push requires `BypassSandbox: true` for HTTPS credentials.
   - Do NOT commit `docs/audit/` or `docs/sprint/` (they contain file hash manifests that trigger gitleaks rules; both are safely in `.gitignore`).

---

## 4. Key Deliverables & File Map

* `backend/context_core/`:
  - `align.py`: 4Hz visual feature extraction and cosine sequence alignment.
  - `acoustic_align.py`: Normalized acoustic waveform cross-correlation.
  - `crop_detector.py`: Multi-scale spatial template matching and SAM 3.1 reframe detector.
  - `grounded_omissions.py`: Omission grounding synthesizer.
  - `context_pack.py`: Excerpt pack builder for bounded Meta requests.
  - `meta.py`: Meta Muse Spark 1.2 review with citation bounds checking.
  - `comparison.py`: Multi-scenario comparison engine and evidence persistence.
  - `api.py`: FastAPI server (`/api/analyze`, `/api/demo/crop`, `/api/investigations/{id}`).
* `web/src/`:
  - `main.tsx`: Dual-player workbench, Evidence Explorer, timeline spans, and SVG crop overlay.
  - `SourceComparison.tsx`: Dossier comparison player with green/red spatial crop overlays.
  - `types.ts`: TypeScript contracts for `Evidence`, `Finding`, and `CropAnalysis`.
* `demo-video/`:
  - `story.json`: 6 chapters: intro (25s), problem (30s), live_run (55s), sam_crop (30s), evaluation (25s), attribution_wrap (15s).
  - `renders/context-demo-3min.mp4`: Rendered 180s master Full HD demo video.
* `eval/execution-v1/`:
  - 30 scripted FFmpeg edits across 3 CC0 benchmark sources (`sort.mp4`, `cache.mp4`, `serialize.mp4`).
* `docs/`:
  - `submission.md`: Hackathon submission text with architecture diagrams and metrics.
  - `demo-script.md`: Spoken narration script with per-chapter timecodes.
  - `evaluation.md`: Frozen benchmark results breakdown.
  - `model-card.md`: Meta AI model integration card (Muse Spark 1.2 & SAM 3.1).
  - `VALIDATION-STATUS.md`: Gate-by-gate pass status report.

---

## 5. Codex Master Commands

```bash
# 1. Run all tests
cd /Users/thecodekaizen/Code/Projects/hackathons/context
.venv/bin/pytest -q

# 2. Check code quality
.venv/bin/ruff check backend scripts
.venv/bin/ruff format --check backend scripts

# 3. Build frontend
cd web && npx tsc --noEmit && npx vite build && cd ..

# 4. Run frozen evaluation suite
PYTHONPATH=backend .venv/bin/python scripts/run_execution_eval.py

# 5. Start development workstation server
.venv/bin/uvicorn context_core.api:app --app-dir backend --host 127.0.0.1 --port 8000

# 6. Re-capture demo chapter screen recordings (requires server running)
node scripts/capture-demo-chapters.mjs
.venv/bin/python scripts/build-demo.py

# 7. Re-render master demo video
cd demo-video
npm run render -- --output renders/context-demo-3min.mp4 --fps 24 --quality high --workers 4 --video-frame-format png
```

---

## 6. Remaining Roadmap for Submission (Nov 3 – Nov 4)

1. **Tuesday, Nov 3 (Builder Voiceover):**
   - Builder records human voiceover matching `docs/demo-script.md`.
   - Place WAV files into `demo-video/assets/`.
   - Run `cd demo-video && npm run render ...` to burn in authentic builder voice.
2. **Wednesday, Nov 4 (Submission Day):**
   - Deadline: 9:00 PM Eastern Time.
   - Portal: [https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit)
   - Submit public GitHub repo link: `https://github.com/thecodekaizen/context`
   - Upload / link `demo-video/renders/context-demo-3min.mp4`
   - Copy description from `docs/submission.md`.
