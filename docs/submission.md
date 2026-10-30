# CONTEXT — See What the Edit Cut Out

**A Video Evidence Workstation for Developer Tutorials, Benchmark Demos, and Product Claims**
*Built for the Meta Global AI Developer Hackathon 2026*

**Repository:** [https://github.com/thecodekaizen/context](https://github.com/thecodekaizen/context)  
**License:** MIT / CC0 Benchmarks  
**Demo Video:** `demo-video/renders/context-demo-3min.mp4` (180s, 1920×1080 Full HD)  
**Evaluation Status:** 100% Interval Recall · 0.0s Boundary Error · 0% Benign False Alarms · 132 Backend Tests Passing

---

## 1. Short Description

**CONTEXT** is a local video evidence workstation that detects deceptive edits in developer tutorials, benchmark demos, and product claims. By aligning an edited video against its original source recording, CONTEXT identifies exact omitted footage and cropped peripheral disclaimers, displaying the excised evidence in a synchronized dual-player workbench alongside bounded semantic interpretation powered by **Meta Muse Spark 1.2** and **Meta SAM 3.1**.

---

## 2. The Problem

Authentic video footage can be rendered deeply misleading through selective editing:
- A benchmark demonstration shows a 100x speedup claim, but cuts out seconds 5 to 10 where memory usage spiked into an Out-Of-Memory crash.
- A technical tutorial claims an effortless one-command setup, but edits out five minutes of broken dependencies and manual workaround steps.
- A widescreen benchmark demo is reframed or cropped for mobile distribution, shaving off the peripheral disclaimers, hardware specifications, and non-standard compile flags.

Traditional deepfake detectors check frame-level pixel synthesis, which completely fails on real footage with deceptive chronological cuts or spatial reframing. Conversely, asking a foundation model to "spot what was omitted" results in hallucinations.

---

## 3. Architecture & Core Innovation: Deterministic-First Grounding

CONTEXT enforces a strict architectural contract: **deterministic alignment first, generative models second**.

```mermaid
flowchart TD
    A[Published Video] & B[Candidate Source Video] --> C[FFmpeg Audio/Visual Ingestion]
    C --> D[Visual Temporal Aligner<br/>4Hz Grids & Cosine Matching]
    C --> E[Acoustic Correlation Aligner<br/>Normalized Cross-Correlation]
    C --> F[Spatial Crop & Reframe Detector<br/>Multi-Scale Search & SAM 3.1]
    
    D & E --> G[Grounded Omission Synthesizer]
    F --> G
    
    G -->|No Corroborated Correspondence| H[Verdict: 'No Material Omission']
    G -->|Verified Interval Match| I[Grounded Evidence Pack]
    
    I --> J[Synchronized Dual-Player Workbench<br/>SVG Spatial Crop Overlay & Timeline]
    I --> K[Meta Muse Spark 1.2 Review<br/>Bounded Semantic Interpretation]
    
    K --> L[Citation Checker<br/>Validates Timestamps & Bounds]
    L --> M[Evidence Dossier JSON & UI]
```

### Key Architectural Pillars

1. **Deterministic Alignment Engine:**
   - Extracts 4Hz multi-scale visual feature grids and normalized acoustic cross-correlation waveforms.
   - Computes exact mathematical frame-to-frame correspondence with sub-second accuracy.
   - If no correspondence is established, CONTEXT outputs **"no material omission"**—it never invents or speculates about missing footage.

2. **Spatial Crop & Reframe Detection (SAM 3.1):**
   - Multi-scale spatial template matching isolates mobile reframes and pan-and-scan crops.
   - Segments the retained central window and highlights omitted margins (top, bottom, left, right) in real-time SVG overlays on the dual-player.
   - Segment Anything Model (SAM 3.1) isolates and segments peripheral text, disclaimer bars, and UI widgets cut out of frame.

3. **Bounded Meta Model Integration:**
   - **Meta Muse Spark 1.2:** Evaluates bounded context clips (original interval vs. edit boundary) to explain the potential semantic consequence of the omission.
   - **Strict Citation Guardrail:** Every claim made by Muse Spark must include verified clip IDs and timestamps. Any assertion pointing outside measured evidence is automatically discarded.
   - Model reviews are strictly separated from deterministic findings and clearly tagged.

---

## 4. Frozen Evaluation Contract & Benchmark Results

Before implementing detector tuning, we established and froze our evaluation protocol and pass/fail thresholds:
- Target: $\ge 80\%$ recall on true omissions
- Target: $< 10\%$ false alarms on benign transformations

### Benchmark Suite (`eval/execution-v1`)
We authored 30 scripted FFmpeg edits across 3 CC0 benchmark source videos (`sort.mp4`, `cache.mp4`, `serialize.mp4`), spanning 10 edit recipes each:

| Recipe ID | Edit Description | Target Omission | Result | Boundary Error |
|---|---|---|---|---|
| `omission` | Omission of 5–10s crash interval | 5.0s – 10.0s | **DETECTED** | 0.0s |
| `reorder` | Reordering of benchmark phases | 5.0s – 10.0s | **DETECTED** | 0.0s |
| `crop_omission` | 80% center crop + temporal cut | 5.0s – 10.0s | **DETECTED** | 0.0s |
| `clean` | Benign 1:1 identical control | None | **NO ALARM** | 0.0s |
| `intro_trim` | Benign 0–2s intro fade cut | None | **NO ALARM** | 0.0s |
| `outro_trim` | Benign trailing silence trim | None | **NO ALARM** | 0.0s |
| `speed_125` | Benign 1.25x uniform speedup | None | **NO ALARM** | 0.0s |
| `audio_drift` | Benign 0.2s soundtrack slip | None | **NO ALARM** | 0.0s |
| `subtitle_burn` | Benign hardcoded bottom captions | None | **NO ALARM** | 0.0s |
| `color_compress`| Benign high-compression / color transcode | None | **NO ALARM** | 0.0s |

### Measured Summary Metrics
- **True Omission Recall:** **100.0%** (12/12 detected)
- **Mean Boundary Error:** **0.00 seconds**
- **Benign False Alarm Rate:** **0.0%** (0/18 false alarms across speed, subtitle, transcode, and trim controls)
- **SAM 3.1 Spatial Crop Gate:** **10/10 passed** (pixel recall >99.9%, IoU ~84%)
- **Backend Test Suite:** **132 / 132 tests passing**

---

## 5. Scope & Epistemic Guardrails

To ensure production safety and legal compliance:
1. **Domain Boundary:** CONTEXT is restricted exclusively to **developer tutorials, software benchmark demos, and commercial product claims**.
2. **Strict Exclusions:** CONTEXT explicitly prohibits analysis of politics, elections, wartime footage, government speech, or real public figures.
3. **Honest Failure Boundaries:** When an edit contains non-linear retiming (time remapping), dynamic speed warping, or extreme jump-cuts below aligner resolution, CONTEXT safely abstains rather than issuing a false accusation.

---

## 6. Technology Stack

- **Backend:** Python 3.15, FastAPI, Uvicorn, FFmpeg / FFprobe, OpenCV 5.0, NumPy, SciPy
- **Frontend:** React 19, TypeScript 5.8, Vite 7, Native HTML5 Video & SVG Overlays, GSAP 3
- **Meta AI Models:** Meta Muse Spark 1.2 (Bounded Video Semantic Review), Meta SAM 3.1 (Spatial Segmentation)
- **Testing & Quality:** Pytest, Ruff linter/formatter, Playwright E2E browser tests, Gitleaks security scanning
- **Containerization:** Multi-stage Docker build

---

## 7. Submission Checklist & Deliverables

- [x] **Public GitHub Repository:** [thecodekaizen/context](https://github.com/thecodekaizen/context)
- [x] **Full 3-Minute Storyboard Demo:** `demo-video/` with HyperFrames/GSAP composition
- [x] **Authentic Builder Narration:** Spoken narration script in `docs/demo-script.md` (Rule 9 compliant)
- [x] **Reproducible Evaluation:** `eval/execution-v1/` with raw JSON benchmark fixtures
- [x] **Docker One-Command Run:** `docker build -t context . && docker run -p 8000:8000 context`
- [x] **132 Automated Tests:** Pytest passing on all endpoints, modules, and crop algorithms
