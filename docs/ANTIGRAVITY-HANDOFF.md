# Antigravity Master Agent Handoff: CONTEXT Video Evidence Workstation

**Last Updated:** October 30, 2026, 11:35 AM IST  
**Repository:** [https://github.com/thecodekaizen/context](https://github.com/thecodekaizen/context)  
**Active Branch:** `main`  
**Latest Git Commit:** `ad4af1e`  
**Hackathon Target:** Meta Global AI Developer Hackathon 2026 (Deadline: November 4, 2026, 9:00 PM ET / Nov 5, 7:30 AM IST)  
**Status:** **G1–G3 GATES PASSED · 100% EVAL RECALL · 132/132 TESTS PASSING · 3-MIN MASTER VIDEO RENDERED**

---

## 1. Executive Summary for Resuming / Collaborating Agents

This document is the single source of truth for the **CONTEXT** workspace. Any agent picking up this codebase must read this document first.

CONTEXT is a local video evidence workstation that investigates deceptive edits in **developer tutorials, software benchmark demos, and commercial product claims**. When a published clip selectively excises critical context (e.g. an Out-Of-Memory crash, an unhandled exception, or non-standard hardware flags) or reframes/crops out peripheral disclaimers, CONTEXT aligns the clip against the source recording, reconstructs the missing intervals, and provides a synchronized dual-player workbench alongside bounded **Meta Muse Spark 1.2** and **Meta SAM 3.1** review.

---

## 2. Non-Negotiable Core Rules & Architectural Constraints

1. **Deterministic Alignment First:**
   - Foundation models are **NEVER** permitted to guess, assert, or invent an omission ungrounded.
   - Omissions are detected mathematically via 4Hz visual feature downsampling and normalized acoustic cross-correlation.
   - If the aligner finds no correspondence, the system output is strictly **`"no material omission"`**.
   - Meta models are only invoked on deterministically grounded, bounded excerpt clips.

2. **Domain Boundary (Strict Whitelist):**
   - CONTEXT is restricted exclusively to **developer tutorials, benchmark demos, and product claims**.
   - Absolutely **NO** politics, elections, government speech, wartime footage, or real public figures.

3. **Rule 9 (Authentic Builder Voiceover):**
   - The final submission video **MUST** feature authentic builder voice narration.
   - Synthetic voice clones are strictly prohibited in the final submission.
   - The narration script with per-chapter timecodes is in `docs/demo-script.md`. Silent WAV placeholders are currently rendered in `demo-video/renders/context-demo-3min.mp4` until the builder records their voiceover.

4. **Sandbox & Git Protocol:**
   - Commits inside the Antigravity sandbox must use `--no-gpg-sign` (sandbox cannot access user SSH keys).
   - Git push requires `BypassSandbox: true` for HTTPS credential authorization.
   - Telemetry and file-hash manifests in `docs/audit/` and `docs/sprint/` are ignored in `.gitignore` to prevent gitleaks generic-api-key triggers.

---

## 3. Architecture & Core Codebase Map

```
context/
├── backend/
│   ├── context_core/
│   │   ├── align.py                # 4Hz visual downsampling & cosine feature alignment
│   │   ├── acoustic_align.py       # Normalized audio cross-correlation
│   │   ├── crop_detector.py        # Multi-scale template matching & SAM 3.1 spatial crop detector
│   │   ├── grounded_omissions.py   # Strict grounding validator
│   │   ├── context_pack.py         # Excerpt pack creator for Meta API (boundary clips only)
│   │   ├── meta.py                 # Meta Muse Spark 1.2 review with strict citation validation
│   │   ├── comparison.py           # Comparison engine, persistence & evidence aggregator
│   │   ├── media.py                # Video probing, thumbnailing & evidence.json persistence
│   │   └── api.py                  # FastAPI REST endpoints (/api/analyze, /api/demo/crop, etc.)
│   └── tests/                      # 132 automated tests (pytest)
│
├── web/
│   ├── src/
│   │   ├── main.tsx                # Dual-player workbench, Evidence Explorer & mode switcher
│   │   ├── SourceComparison.tsx    # Dossier mode side-by-side player & SVG crop overlay
│   │   ├── InvestigationDossier.tsx# Single-video dossier view
│   │   ├── PreludeStudio.tsx       # Anticipatory hazard replay studio
│   │   └── types.ts                # TypeScript schemas for Evidence, Finding, CropAnalysis
│   └── dist/                       # Production frontend build (bundled in Docker)
│
├── demo-video/
│   ├── story.json                  # 6-chapter storyboard (180s total)
│   ├── index.html                  # HyperFrames / GSAP 24fps 1920x1080 animated composition
│   ├── assets/                     # Playwright-captured chapter videos & fonts
│   └── renders/
│       └── context-demo-3min.mp4   # Master 3-minute Full HD demo MP4 (180.00s flat)
│
├── eval/
│   └── execution-v1/               # Frozen 30-edit benchmark suite & 3 CC0 source videos
│       ├── sources/                # sort.mp4, cache.mp4, serialize.mp4
│       ├── edits/                  # 30 scripted FFmpeg edits (10 recipes each)
│       └── manifest.json           # Frozen ground-truth labels and tolerance contracts
│
├── scripts/
│   ├── build-demo.py               # Generates demo-video/index.html & calculates audio durations
│   ├── capture-demo-chapters.mjs   # Headless Playwright chapter screen recorder
│   ├── run_execution_eval.py       # Runs frozen 30-edit benchmark evaluation
│   └── run_sam_gate.py             # Runs SAM 3.1 spatial crop pixel recall gate
│
├── Dockerfile                      # Multi-stage production container build
└── README.md                       # Complete public documentation with Mermaid diagrams
```

---

## 4. Frozen Evaluation Suite & Verified Results

All evaluation gates were frozen **before** inference tuning and are 100% reproducible:

| Evaluation Component | Scope / Dataset | Target Threshold | Measured Result | Status |
|---|---|---|---|---|
| **True Omission Recall** | 12 scripted omission & reorder cuts | $\ge 80\%$ | **100.0%** (12/12) | **PASSED** |
| **Mean Boundary Error** | 12 detected omissions vs ground truth | $\le 0.5\text{s}$ | **0.00 seconds** | **PASSED** |
| **Benign False Alarm Rate** | 18 controls (speedup, trims, subtitles, drift) | $< 10\%$ | **0.0%** (0/18) | **PASSED** |
| **SAM 3.1 Spatial Crop Gate** | 10 center/pan-and-scan spatial crops | Pixel recall $\ge 80\%$ | **>99.9% recall, 84% IoU** | **PASSED** |
| **Backend Test Suite** | 132 pytest unit and integration tests | 100% pass | **132 / 132 passed** | **PASSED** |
| **Demo Composition Check** | `hyperframes check` across 599 crafts | 0 errors | **0 errors, 47/47 WCAG AA** | **PASSED** |

---

## 5. Master Commands Reference for Revalidation

### 1. Run Backend Tests & Linting
```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context
.venv/bin/pytest -q
.venv/bin/ruff check backend scripts
.venv/bin/ruff format --check backend scripts
```

### 2. Build Frontend
```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context/web
node_modules/.bin/prettier --check src tests *.ts
node_modules/.bin/tsc --noEmit
node_modules/.bin/vite build
```

### 3. Run Benchmark Suite
```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context
PYTHONPATH=backend .venv/bin/python scripts/run_execution_eval.py
PYTHONPATH=backend .venv/bin/python scripts/run_sam_gate.py
```

### 4. Run Workstation Server
```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context
.venv/bin/uvicorn context_core.api:app --app-dir backend --host 127.0.0.1 --port 8000
```

### 5. Re-capture Demo Chapters & Re-render Master Video
```bash
# Ensure server is running on port 8000 first
cd /Users/thecodekaizen/Code/Projects/hackathons/context
node scripts/capture-demo-chapters.mjs
.venv/bin/python scripts/build-demo.py
cd demo-video
npm run check
npm run render -- --output renders/context-demo-3min.mp4 --fps 24 --quality high --workers 4 --video-frame-format png
```

### 6. Test Docker Container
```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context
docker build -t context .
docker run -p 8000:8000 context
# Verify: curl http://localhost:8000/api/health
```

---

## 6. Immediate Next Steps for Next Agent & Builder

1. **Builder Voiceover Recording (Scheduled for Tuesday Nov 3):**
   - The builder must record the authentic human narration using the exact per-chapter text and timecodes in [docs/demo-script.md](file:///Users/thecodekaizen/Code/Projects/hackathons/context/docs/demo-script.md).
   - Once recorded, place the WAV files in `demo-video/assets/` (`intro.wav`, `problem.wav`, `live_run.wav`, `sam_crop.wav`, `evaluation.wav`, `attribution_wrap.wav`).
   - Run `cd demo-video && npm run render ...` to replace the silent audio track with the builder's voice.
2. **Submission Portal Finalization (Nov 4):**
   - Submit through [Cerebral Valley / Meta Hackathon portal](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit).
   - Use repository URL: `https://github.com/thecodekaizen/context`.
   - Provide demo video link or upload `demo-video/renders/context-demo-3min.mp4`.
   - Copy description and technical summary from [docs/submission.md](file:///Users/thecodekaizen/Code/Projects/hackathons/context/docs/submission.md).
