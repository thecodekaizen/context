# VIDEO INTELLIGENCE PLATFORM — CANONICAL VISION & DECISIONS

Updated 2026-10-29. This is the product north star for the Meta Global AI Developer Hackathon and subsequent indie development. Read this before reducing scope to the easiest technical component.

## 1. What we are actually building

A **unified video-intelligence engine and beautiful video-first investigation studio**. Inputs can include a local video, supported public video URL, indexed recording, or (in the long term) live camera / smart glasses. It combines mathematical measurement, signal processing, temporal algorithms, geometry, computer vision, probabilistic estimation, scientific/physical modeling, retrieval, and Meta multimodal AI. It makes findings inspectable through spatial overlays, evidence graphs, synchronized comparison, clickable timelines, and explicit uncertainty.

**One engine, four application lenses.** They share media time, observations, object tracks, transcripts, evidence provenance, uncertainty and overlays, but domain-specific reasoning is independently implemented and tested. The platform is **not a chatbot wrapper, ordinary video-diff utility, generic dashboard, or unverified AI verdict.**

### CONTEXT — Investigate what is real and what the footage supports (hackathon P0)
- Start from **one video**, with an optional accompanying caption/claim or URL. A user-supplied original video is *optional*, not the normal requirement.
- Understand visible events and speech; identify factual claims; inspect provenance; search accessible external or indexed evidence; find related/earlier versions where possible; compare sources; detect omitted/reordered/repeated spans with timestamped evidence; evaluate whether the interpretation is supported, contradicted, unresolved or insufficiently evidenced.
- Distinguish **authentic media**, **edited media**, **misleadingly presented media**, and **unverified claims**. These are different properties. No universal real/fake oracle exists.
- Hero interaction: evidence-backed visual reveal of important missing context, with clickable source links and synchronized dual playback when a source is found.
- Long-term UX: an intelligent, unobtrusive overlay for online video that surfaces checkable claims/evidence without falsely pretending to know truth.

### PRELUDE — Anticipate visual hazards (hackathon P1, only after research gate)
- Given recorded near-miss footage, use *only frames available before the incident* to detect/track actors, estimate motion and temporal cues, and report possible developing dangers with confidence/uncertainty.
- Uses segmentation/object tracking plus **geometric and kinematic calculations**: do not outsource physical prediction to an LLM alone.
- Overlay tracks, paths, potential conflict zones and associated evidence/timecodes. Validate on safe driving negatives and measure lead time and false alarms.
- **Not a validated real-time driver-assistance system.** Long-term smart-glasses/on-road vision requires hardware, latency, ergonomics and safety validation; don't claim it exists now.

### VEIL — Protect the footage (hackathon P1.5 contingent on existing code reuse)
- Detect private visual or spoken content, track sensitive regions, redact or perform feasible natural replacement, **inspect exported frames/audio independently**, and make privacy edits visible/adjustable.
- Reuse existing VEIL prototype if present. Do not spend the hackathon rebuilding a full video anonymization service or claim perfect privacy.
- Future mode can act as a "protect before sharing" operation for investigations or captured video.

### CONTROL — Analyze experiments and evidence of physical causality (post-hackathon)
- Observe procedures, objects, measured variables, experimental interventions, confounds, conclusions and uncertainty.
- Distinguish a procedural error from *scientific causal validity*. A video alone may lack sufficient information for a causal conclusion.
- This product remains an architecture extension; do not claim implementation until independently verified.

## 2. Scientific and engineering principles

**AI interprets; algorithms measure; physics constrains; evidence verifies.**
- Signal processing: audio/video synchronization, temporal frequency, correlation, noise handling.
- Algorithms/math: retrieval, fingerprints/features, graph alignment, geometric transforms, tracking, optimization, uncertainty.
- CV: segmentation/visual grounding, object tracking and re-identification when justified.
- Physics: explicit motion estimates and error bars; no confident predictions from unconstrained video.
- AI: semantic event/claim understanding, hypothesis generation, natural language explanations; model results must point to actual accessible evidence.
- Audits and held-out datasets: benchmark result, false positive, false negative, latency/cost and failure cases recorded, not hidden.

## 3. UX north star

A **minimal, spacious, cinematic video-first product** with contemporary system/Inter-type typography, graphite and light modes, one clear accent, tactile 150–300ms microinteractions, purposeful transitions, responsive layouts and full keyboard affordances. An impressive functional experience, not decorative animation.

The main work surface retains a dominant player. Switchable lenses: Investigate / Anticipate / Protect / Experiment. Overlays and drawers change according to the chosen analysis. Input may be one file or supported URL. Output includes interactive time-aligned findings, evidence dossier, source graph, source/edited comparison, geometric trajectories and privacy regions. The uploaded video must **never** display invented model detections. Sample cases are labeled demos. Unknown/unsupported evidence is shown honestly.

The bundle contains an editable **React/Tailwind/Lucide** prototype with four lenses, theme switcher, sample scene assets, and a standalone HTML preview. See `ux/React_Project.zip`, `ux/Interactive_Preview.html`, `ux/screenshots/`, and `ux/UX_SPEC.md` inside that React zip.

## 4. Deadline, order and no-go boundaries

Hackathon deadline **2026-11-04 21:00 Eastern** (equivalent to **2026-11-05 07:30 IST** at that date). No publishing, release or submission without user approval.

- **P0:** functional CONTEXT single-video investigation; real, legally retrievable evidence; source search against multiple plausible candidates; timestamped dossier and meaningful Meta contributions; held-out, non-manipulated negatives.
- **P1 conditional:** one legitimate PRELUDE pre-incident risk test on benchmark data, after CONTEXT succeeds; evaluate safe negatives, leak-proof pre-incident cutoff.
- **P1.5 optional:** connect genuine VEIL functionality if inexpensive; verify actual exported outputs.
- **P2/future:** CONTROL and public SDK packaging. Include module boundaries, not full feature implementation during the hackathon.

Codex must operate autonomously for hackathon execution. No learning exercises, reading assignments, peer-coding interruptions (that behavior is for the user's **personal indie projects**, not hackathons). Report actual tests, benchmarks, failures, changed files, and working UI. Do not stop at code scaffolding, 51 unit tests or packaging. Escalate only essential access/product decisions and irreversible actions.

## 5. Existing code and provenance

The user's current local CONTEXT prototype reportedly has FFmpeg ingestion, local source index (up to ~20), deterministic alignment, omission/reordering detection, JSON reports, dual video UI, Muse Spark integration, and reported 51 backend / 8 browser tests. **These are prior agent claims**; inspect code and rerun rather than assume. Preserve existing work, do not delete unrelated THREAD/VEIL projects.

Important: This handoff ZIP contains **reference materials**, a frontend prototype and launcher. It **does not contain the user's current local CONTEXT backend**, full original conversation transcripts, API keys, downloaded benchmark media, or a working trained AI engine. Codex must inspect the local repo.

## 6. Evaluation dataset direction

See `DATASET_REGISTRY.csv` and `VIDEO_INTELLIGENCE_IMPLEMENTATION_PLAN.md`. Prioritize:
- CONTEXT: EVID-Bench and independent honest/misleading video edits, source retrieval and meaning assessment.
- PRELUDE: Nexar collision/near-miss plus normal driving; pre-event-only evaluation.
- VEIL: PEViD-UHD, LSVTD or properly licensed plate/screen footage; final-export leakage checking.
- CONTROL: ExpVid for scientific understanding; CaptainCook4D for procedural error only.

Always inspect licenses/permissions before downloading or republishing. Research datasets may be accessible only for research/noncommercial use; prize hackathon demo and public redistribution may be restricted. Stock footage alone usually lacks labeled ground truth. Don't assume stock-footage site licensing permits ML benchmarking.

## 7. What a successful hackathon demonstration looks like

A genuine one-video CONTEXT investigation with independently retrieved or indexed sources, observable reasoning, one-click evidence reveal and an honest harmless-edits negative. If P0 passes, a second **distinct** PRELUDE risk example visibly uses the same time-aligned engine and produces a grounded *pre-incident* warning. VEIL may add an actual protect-before-sharing action. CONTROL is presented as a future application rather than an unbuilt fake capability. The stunning visual interface is connected to real model/output data, not hardcoded examples.
