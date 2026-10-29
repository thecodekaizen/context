# AUTONOMOUS HACKATHON EXECUTION — VIDEO INTELLIGENCE ENGINE

You are operating in the actual local repo for the Meta Global AI Developer Hackathon 2026. **Start executing immediately.** Deadline: 2026-11-04 21:00 ET. This is a hackathon, not a personal-learning project: no peer-programming exercises, reading assignments, or long plan-only output.

## What to read

First read `.hackathon/VIDEO_INTELLIGENCE_VISION_DECISIONS.md` for the canonical product vision (including CONTEXT, PRELUDE, VEIL, CONTROL, smart-glasses long-term ambition, unified overlays and scientific architecture). Then read `.hackathon/VIDEO_INTELLIGENCE_IMPLEMENTATION_PLAN.md`, `.hackathon/CODEX_START_HERE.md`, and `.hackathon/DATASET_REGISTRY.csv`. They are the authoritative product, architecture, UX, dataset and test plan. Inspect the existing code and identify what already works before modifying anything. Do not assume previous claims of 51 backend and 8 browser tests are verified until you run them.

## Product vision you must preserve

Build **ONE exceptional video-first intelligence studio**, supported by a reusable math + physics + CV + signal processing + algorithms + Meta AI engine:
- **CONTEXT (P0):** start from *one video*, investigate observable events/claims and provenance, search legitimate accessible sources, compare matching originals when available, show verifiable timecodes, uncertainty, and evidence overlays. Two-video diff is a component, NOT the product.
- **PRELUDE (P1 contingent):** early risk cues using actual time-ordered object trajectories and held-out future frames in a research/offline replay; test false positives on normal footage.
- **VEIL (P1.5 contingent):** integrate already-built redaction/protection components if inexpensive; evaluate privacy leaks on actual exported video, not a green status badge.
- **CONTROL (post-hackathon):** preserve separate experiment-analysis module boundaries, do not use time implementing it until P0 and P1 pass.
- Visual frontend: a delightful polished React/Tailwind/Lucide video-first interface with responsive evidence timeline, overlays, meaningful interactive cards/drawers, light/dark and accurate state handling; replace sample data with real API outputs. Existing UX reference archive is `.hackathon/CONTEXT_Vision_Studio_React.zip`.

## Immediate deliverable: real evidence, not scaffolding

1. Inspect repo, git status, existing APIs/tests/CI, protect working code; create a local rollback checkpoint (do not publish).
2. Verify existing tools (ffmpeg, Python, Node), actual Meta API access and existing model calls; never log or commit secrets.
3. Implement dataset registry/rights gate and small licensed benchmark subset. Use real benchmark videos wherever permissions permit, NOT stock footage scraped for training/evals.
4. Run an end-to-end *single-video* CONTEXT case against a source-index corpus with multiple plausible candidates. Keep source ID, edit class, and ground truth entirely hidden during inference. Record retrieval trace, the actual source evidence, clip timestamps, and evaluation errors. Include harmless/negative edits and 'unknown source' cases.
5. Connect the real output to the React evidence workspace: user can upload one video, get an investigation job, click a real finding, seek the actual footage, inspect citations and limitations.
6. Report exact benchmark metrics and failed cases; test semantics distinctly from deterministic alignment. Do not equate edits with lying, or absence of an original with fabrication.
7. Only after P0 passes, attempt a separate PRELUDE model + geometry/tracking spike on pre-incident clips with safe negatives, reporting lead time, false alarm rate and limitations.
8. Reuse VEIL if existing implementation is accessible and integration is low cost. Do not spend critical time rebuilding a redactor.

## Autonomous execution mode

Do the work and run commands/tests. Do not stop at an architectural write-up. Make routine engineering decisions independently. Continue through noncritical failures. Provide short updates with: modified files, tests/benchmarks run, actual evidence, model/tooling usage, blockers, and next implementation step. Do NOT publish, tag releases, submit to hackathon, or deploy publicly without owner approval. Do not delete unrelated projects. No fake detection overlays, fake confidence numbers, hardcoded model findings, or fake citations.

Now inspect the repository and start implementing and running the FIRST real benchmark-backed CONTEXT vertical slice. Do not ask me to choose between already-settled product directions.
