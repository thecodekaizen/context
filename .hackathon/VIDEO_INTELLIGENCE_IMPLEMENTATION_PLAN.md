# VIDEO INTELLIGENCE ENGINE — MASTER IMPLEMENTATION & EVALUATION PLAN

**Project:** CONTEXT Vision Studio / reusable multimodal video-intelligence engine  
**Workstream:** Meta Global AI Developer Hackathon 2026  
**Plan date:** 29 October 2026 (Asia/Kolkata)  
**Submission deadline:** 4 November 2026, 9:00 PM ET = 5 November 2026, 7:30 AM IST  
**Operating style:** Autonomous hackathon execution; no peer-programming exercises.  
**Status:** Planning and integration document. No claims here imply the current implementation passes these gates.

---

## 0. Executive decision

**Build one video-first investigation studio, backed by a reusable evidence/time-alignment engine, with four domain lenses.** The lenses share media ingestion, timestamps, audio, visual observations, object tracks, citations, model adapters, job state, and the viewer. They do **not** share arbitrary domain judgments or a single giant `analyze_everything` prompt.

- **P0 — CONTEXT** (flagship, must work): single video or supported URL → scene/claim analysis → independent source search when available → evidence dossier. Existing deterministic alignment is a supporting tool. Preserve the existing working prototype and its 51 backend/8 browser tests as reported by Codex, but independently rerun and audit them.
- **P1 — PRELUDE** (credible second technical demonstration, conditional): pre-incident dashcam footage → tracked agents and time-ordered risk cues → grounded visual risk indication. **Research/offline replay only**, not real-time driver assistance.
- **P1.5 — VEIL** (reuse, conditional): existing redaction API → privacy-region overlay → privacy-safe output → independent final-export check; do not rebuild or promise universal natural replacement.
- **P2 — CONTROL** (optional stretch / post-hackathon): identify procedural states and variables, distinguish observations from causal hypotheses, suggest controls. The full scientific-validation product does not fit the remaining week.

**Winning demonstration:** One product, two genuinely useful and visually distinct intelligent modes, plus a working privacy action if integration is inexpensive. The common engine is an engineering contribution demonstrated by the same evidence/time-series primitives powering both modes. Do not promise a real/fake oracle or certified crash prevention.

### Immediate product guardrails

1. A user can start with **one video**; a known source is optional, never required at intake.
2. Findings must carry evidence and an epistemic status: `observed`, `matched`, `inferred`, or `unverified`.
3. Not finding a source is **not** proof of fabrication. Detecting a cut is **not** proof of deception.
4. A redacted video isn't guaranteed private; a risk cue isn't a calibrated collision probability; a perceived confound isn't proof of causality.
5. No synthetic demo data masquerades as model output. Original UI prototypes explicitly contain fictional sample cases.
6. Dataset licenses and consent restrictions are first-class engineering constraints.
7. No publishing, external production deployment, hackathon submission, or release tagging without explicit user approval.

---

## 1. What currently exists, and how to reuse it

### Current state as reported by Codex (needs local audit)

The existing CONTEXT repo reportedly already supports original/edited upload, local source discovery (up to 20 originals), FFmpeg sampling, deterministic temporal alignment, omissions/reordering/repetition, a dual-video UI, evidence JSON, and a real Muse Spark 1.2 analysis call with evidence timestamp validation. The reported 51 backend / 8 browser tests mainly cover controlled cases. **Do not discard any of this.**

### UX assets already prepared

The supplied React prototype (`CONTEXT_Vision_Studio_React.zip`) contains React 19, Vite 6, Tailwind 3, Lucide React, a four-mode video-first workspace, source/evidence drawer, timeline, light/dark themes, and seeded scenarios in `src/data.js`. It is **not connected to the backend**. React UI integration must replace seeded findings with API-backed investigation jobs and must not accidentally label user uploads as analyzed. The standalone HTML preview is a visual reference, not an inference engine.

### Mandatory first repository audit

- Verify paths, current git status, actual server APIs, packages, test commands, model version and authenticated API behavior.
- Confirm whether the existing backend is already `FastAPI`, which storage it uses, how job IDs map to media and where hashes/citations are stored.
- Confirm whether existing `src/App.jsx` UI uses real video or merely SVG placeholder scenes.
- Preserve green tests; add evidence-contract adapter tests before making design changes.
- Create a snapshot branch and a rollback point. Do not replace the existing frontend wholesale; selectively integrate components from the UX prototype.

---

## 2. User journeys & experience contract

### First-time experience

1. User arrives at a **hero media drop zone** with a drag/drop video option, supported URL field, and two or three real **sample investigations** clearly identified as examples.
2. User presses **Investigate**. System immediately shows media information and an honest processing pipeline: `Inspecting video` → `Extracting speech and events` → `Searching evidence` → `Checking claims` → `Preparing dossier`.
3. Main view stays video-first: a 16:9 media canvas and an adjacent intelligence panel; under them, a dense interactive timeline with colored, evidence-backed event pins.
4. Selecting a finding seeks the video, highlights the relevant region or transcript, and opens provenance/evidence. If a source video is found, show a synchronized split view and `Reveal what was missing`.
5. Users can switch lenses without reuploading; if the chosen analyzer has not run, show `Run PRELUDE analysis`, not invented overlays.
6. End with a **shareable evidence dossier**, including sources, limitations, method/model versions, and report creation timestamp.

### Four task lenses

**CONTEXT / Investigate:** "What does this video show, what's claimed, what's missing, and what can we actually substantiate?" Subviews: Summary, Claims, Sources, Timeline, Comparison. Never force a single true/false label; use evidence-specific states (`supported`, `contradicted`, `insufficient evidence`, `source unavailable`).

**PRELUDE / Anticipate:** "What potential hazard was visible *before* the event?" Overlay past object tracks, estimated movement, risk cue interval and outcome (after replay only). Before-event inference must never receive the later incident frames.

**VEIL / Protect:** "What should be concealed before sharing?" Privacy overlays, editable regions, an export preview, audio privacy flags and an independent check of the rendered file.

**CONTROL / Experiment:** "What was changed and is the claimed conclusion warranted?" Tools and materials, observed state changes, purported dependent/independent variables, potential confounds and uncertainty. Experimental truth must not be inferred solely from a procedural video.

### Visual design system

- Existing design direction: dark graphite, highly legible light mode, near-monochrome typography, **one vibrant periwinkle accent**. Reserve amber for warnings and green for verified workflow status; never imply truth by color alone.
- Video should occupy ~60–70% of desktop workspace width; adapt to stacked viewer/timeline/panel on mobile.
- Hover/press transitions 150–300 ms; visible focus, keyboard seeking (`J/K/L`, arrow keys), shortcuts and reduced-motion support.
- Real model boxes should interpolate from timestamped geometry, track identities through video, hide on insufficient confidence, and never show illustrative tracked actors for uploaded videos.
- Evidence has depth: click a marker → pin on track → timeline zoom → seek synchronized source → inspect original and retrieved citations.
- Loading must show partial findings progressively. Model timeouts/unsupported URLs/denied permissions must be visible and recoverable.

### UX acceptance gates

- On cold load, user reaches upload or sample in <=2 actions.
- Full flow works with mouse **and** keyboard; screen readers announce findings and timecodes.
- No horizontal overflow at 375px, 768px, 1280px and 1600px viewport widths.
- Every finding click seeks within 0.5 s of its intended time; evidence map and video playhead remain synchronized.
- User-selected synthetic sample clearly says **Sample / illustrative**. Uploaded, unanalyzed video says **Not analyzed**.
- No fake "verified" badges, confidence percentages without calibration, or generic chat transcript dominating the experience.

---

## 3. Architecture and ownership boundaries

```text
                    Browser / Upload / Supported URL
                                  |
                           Ingestion API
                    (validate, probe, hash, store)
                                  |
                        Analysis Job Orchestrator
             (states, retry, cache, cancellation, events)
                                  |
                      SHARED VIDEO CORE (SDK seed)
        +-----------+----------+-----------+-----------+
        |           |          |           |           |
     FFmpeg      Frames /    Speech /   Temporal     Evidence &
     media       keyframes   metadata   features    provenance
        |           |          |           |           |
        +-----------+----------+-----------+-----------+
                                  |
                 Model Adapter / Retrieval Tools
                Muse Spark; Muse Voice; SAM 3.1;
             fingerprint search; claim search; CV math
                                  |
                 Task-specific analyzers, separately tested
        +-------------+-------------+-------------+-------------+
        | CONTEXT     | PRELUDE     | VEIL        | CONTROL     |
        | provenance, | tracks,     | regions,    | observed    |
        | retrieval,  | velocities, | transforms, | variables,  |
        | claims      | risk cues   | audit       | hypotheses  |
        +-------------+-------------+-------------+-------------+
                                  |
                         Evidence Event Store
                                  |
                          Studio Frontend
                 Player / overlays / timeline / dossier
```

**Keep Python for the video engine and current backend stack, React/TypeScript for UI.** For the hackathon prefer local jobs and a SQLite metadata index to distributed queues. If async jobs already exist, keep them. Uploads and derived clips live under a configurable local object directory, not in Git. Add a simple storage adapter interface without deploying cloud resources until required.

### Proposed repo layout (adapt existing structure)

```text
context/
  apps/web/                     # Existing UI, progressively migrated
  services/api/                 # Existing FastAPI/back end
  packages/video-core/          # Media, frame/audio sampling, alignment, evidence
  packages/domain-context/      # Claim extraction, retrieval, review
  packages/domain-prelude/      # Object tracks, temporal hazard analysis
  packages/domain-veil/         # Privacy masks, export, audit adapter
  packages/domain-control/      # Experimental analysis (later)
  eval/
    manifests/                  # Versioned dataset manifests, no raw media
    adapters/                   # One benchmark-specific adapter each
    ground_truth/               # Non-public/no leaked labels as required
    scripts/                    # Evaluation harness and metric reports
    reports/                    # Aggregated summaries, no restricted clips
  docs/
    architecture.md
    model-card.md
    data-rights.md
    evaluation.md
    demo-script.md
  tests/
```

**Rule:** Don't spend an entire day physically rearranging an already working repo. Maintain boundaries in code first; restructure only if clearly valuable.

---

## 4. Shared data contracts

The backend owns the facts; frontend visualizes them. Use typed Pydantic + generated TS types (OpenAPI generated or manual minimal equivalent). A minimal normalized finding:

```json
{
  "id": "finding_042",
  "investigation_id": "inv_001",
  "lens": "context",
  "kind": "potential_context_omission",
  "start_ms": 8200,
  "end_ms": 11900,
  "epistemic_status": "matched",
  "summary": "A section is absent between two aligned source intervals.",
  "evidence": [
    {"asset_id":"source_004", "start_ms":46800,"end_ms":51500,"method":"frame_audio_alignment"}
  ],
  "source_links": [],
  "geometry": null,
  "uncertainty": "Semantic effect of omitted interval not independently established.",
  "model": {"provider":"meta", "id":"muse-spark-1.2", "version":"configured"}
}
```

Other stable event types:

- `VideoAsset`: id, original URI, local media hash, mime, fps, resolution, duration, permission/license.
- `Observation`: time interval, modality, object/actor id, track coordinates, source/processor version.
- `TranscriptSegment`: start/end, speaker (optional), text, uncertainty; word-level timing only if a provider actually supplies it or a separate alignment method computes it.
- `Claim`: quoted/verbatim claim, linked transcript/caption span, source URLs, interpretation and verdict state.
- `Track`: spatial coordinates, mask references, temporal coverage, tracking confidence/quality; coordinates in source frame and video orientation metadata.
- `Prediction`: horizon, input cutoff time, reason/evidence, computed risk proxy, calibrated probability ONLY if trained and evaluated.
- `Transformation`: mask/object intervals, output hash, source preservation, privacy audit findings.
- `Investigation`: `queued|processing|partial|completed|failed`, progress events, findings, model versions and errors.

Keep the evidence model generic but put **domain conclusions** into separate typed records. Do not squeeze everything into a giant free-text field.

---

## 5. Actual Meta model integration (verified docs; runtime access still must be tested)

| Capability | Model | Real role | Important limitation |
|---|---|---|---|
| Video + scene/claim semantics | `muse-spark-1.2` currently integrated; evaluate `muse-spark-1.3` | Scene description, speaker/claim context, source comparison, typed explanations | Meta warns 1.3 audio understanding may be degraded; use 1.2 or dedicated ASR for audio-heavy cases |
| Track object pixels | `sam-3.1` | Masks and object identities for PRELUDE trajectories and VEIL privacy regions | Masks aren't physics or risk prediction; derive geometry/velocity separately |
| Speech-to-text | Muse Voice Transcribe | Spoken claims and audio privacy review | Official docs explicitly say no word-level timestamps; use segment/alignment logic as needed |
| Search grounding | Muse Spark model's retrieval tools or external search | Candidate claims and source links | A source URL is not proof; verify retrieved page/video content |
| Open weights | Muse Spark Open (optional) | Later self-hosted deployment | 816B total weights impractical on a 24 GB local laptop; do not depend on self-hosting this week |

Official docs: https://dev.meta.ai/docs/models, https://dev.meta.ai/docs/video-understanding, https://dev.meta.ai/docs/sam/overview, https://dev.meta.ai/docs/media-segmentation. Meta SAM endpoint uses `sam-3.1` on Responses API; Meta video docs support file upload via Files API. Check exact API permissions and usage pricing in the actual account before running large evaluation batches.

### Budget and inference strategy

- Reuse files/uploads where supported; cache by video SHA-256 + sampling settings + model version + prompt hash.
- Cheap deterministic pass first (FFmpeg + hashes/features); send short, relevant clips to Muse only if necessary.
- For CONTEXT, separate factual observations from citation-grounded claims and require human-readable evidence IDs in generated output.
- For PRELUDE, use SAM on selected spans rather than every frame of a large video. Track continuity, then compute motion metrics in Python.
- For VEIL, verify export after final encode with a second pass; don't assume tracking overlay equals privacy success.
- Log per-job estimated tokens, frames and spend. Stop spending on tests without ground truth. Never put credentials in the browser or reports.

---

## 6. PUBLIC DATASETS — THIS IS THE MISSING PIECE

**Why earlier testing was weak:** We optimized for a visually clean demo and hand-authored FFmpeg edits. Those validate that the application is wired together, but they do not measure performance on the real-world failure modes we claim to solve. We now adopt proper benchmark adapters and distinct held-out evaluation splits.

### Dataset selection, verified scope and restrictions

#### CONTEXT — priority 1

**EVID-Bench (EMNLP 2026 Findings)**
- Paper: https://aclanthology.org/2026.findings-emnlp.763/
- Dataset: https://huggingface.co/datasets/Kirito-Lab/EVID-Bench
- Code and baseline: https://github.com/yutao1024/EVID-Bench
- 222 manipulated videos; 9 types across AI-generated, single-source and multi-source editing. Manifest exposes `id`, original YouTube `source` IDs, `task.category`, `task.type`, `topic`, and point-level `groundtruth`. Source footage is generally referenced, not guaranteed downloadable.
- **Research-only, CC BY-NC 4.0, access agreement required.** Do not commit dataset media to public Git. Whether a prize-awarding hackathon demonstration or public competitive submission is permitted is **not established**; obtain authorization or use the benchmark only where its research terms clearly allow. Do not leak `source` IDs or answer labels into the retrieval/model prompt. Use source IDs **only for evaluation**.
- Caveat: Manipulated-only dataset; supplement with unaltered/honest-edit negatives. Published 43.24% video-level baseline accuracy is for open-web retrieval + comparison; cannot compare directly against an oracle source-provided experiment.

**Deepfake-Eval-2024 (optional independent authenticity test)**
- Dataset: https://huggingface.co/datasets/nuriachandra/Deepfake-Eval-2024
- Real-world labeled deepfake examples, including 44 hours of video, other media, and multilingual coverage; controlled evaluation only, not a magical authenticity detector.
- Gated; use for evaluation, not training generative models. Check policy and avoid publishing restricted clips. The dataset card reports a 2025 video metadata correction.

**WildFakeBench / FakeAgent (optional later)**
- Paper: https://arxiv.org/abs/2603.25423
- Repo: https://github.com/Aiyistan/FakeAgent
- Large micro-video misinformation benchmark; verify access/license/content restrictions and baseline before use.

#### PRELUDE — priority 2

**Nexar Collision Prediction (CVPRW 2025)**
- Dataset: https://huggingface.co/datasets/nexar-ai/nexar_collision_prediction
- 1,500 annotated dashcam clips, 1280×720 at 30fps, typically ~40 s; about half collision/near-collision vs normal. Temporal incident/alert labels for positive samples. Dataset is ~31.4 GB; select specific files first.
- License `nexar-open-data-license`: allows use with attribution and restrictions including no resale, no privacy violations and no misleading-media creation. Read the actual license. The research dataset is not evidence that a deployed driver-assistance overlay is safe.
- **Critical evaluation:** Clip at `t_cutoff < incident time`; the model must never see crash frames for early prediction. False positives on normal drives matter as much as detection on incidents.

**RiskCueBench (secondary research protocol)**
- Paper: https://aclanthology.org/2026.emnlp-main.2082/
- Labels earliest human-identifiable risk cue clips across four domains. Reproducing its split is useful if the videos/annotations are actually accessible; **availability and license not established from the publication page alone**. Do not assume downloadable raw videos.

#### VEIL — priority 3

**PEViD-UHD (EPFL)**
- Dataset: https://www.epfl.ch/labs/mmspg/downloads/pevid-uhd/
- 26 consented 4K videos, each 13 s, plus resized versions; XML participant/silhouette labels. Excellent for privacy-mask stability, resolution and export correctness.
- **Research-purpose only; no commercial redistribution.** Do not put raw clips into public repository or public promotional demo without confirming allowed use.

**LSVTD (DAVAR lab)**
- Dataset: https://davar-lab.github.io/dataset/lsvtd.html
- 129 videos with temporal text spotting annotations across indoor/outdoor scenarios. Useful for screen/text coverage and drift, but not all text is PII.
- **CC BY-NC-SA 4.0** on images/annotations; comply with attribution/noncommercial/share-alike conditions.

**Privacy VITA (paper / possible access investigation)**
- Paper: https://aclanthology.org/2026.nlpaics-1.27/
- 516 annotated videos across audio, video, image and text. Download/license path not yet independently confirmed; assign Codex to check before using.

**CCPD (auxiliary static images)**
- Repo: https://github.com/detectRecog/CCPD
- Hundreds of thousands of annotated plate **images**, not a video tracking dataset. Good for still-frame plate geometry; cannot validate temporal privacy coverage alone.

#### CONTROL — priority 4

**ExpVid (ICLR 2026)**
- Paper: https://proceedings.iclr.cc/paper_files/paper/2026/hash/86833e97827ff52d297a9fbde5842a81-Abstract-Conference.html
- Benchmarks perception, procedures and scientific reasoning over real experimental videos. Verify actual data access and terms separately; don't assume you can instantly download the underlying experimental videos.

**CaptainCook4D (NeurIPS 2024)**
- Dataset: https://captaincook4d.github.io/captain-cook/
- Repo/downloader: https://github.com/CaptainCook4D/CaptainCook4D
- 384 kitchen procedure recordings (~94.5 hours) with normal/error steps and fine-grained action annotations; Apache 2.0 on released data per project. Supports **procedural state/errors**, not causal validity of controlled scientific experiments. Use only for relevant CONTROL subtask.

### Stock footage: why not just use Pexels / Coverr?

**Stock videos generally lack task ground truth**: no truth labels, incident timestamps, error annotations, underlying original version, validated risk-cue frames, or reliable source provenance. They are useful for visual QA and media robustness, but cannot independently score accuracy.

**Rights matter.** Pexels allows many ordinary creative uses and modifications, but its current Terms prohibit using its API to compile media/metadata for ML/AI training, development, or evaluation datasets without permission (https://help.pexels.com/hc/en-us/articles/900005880463-What-are-the-Terms-and-Conditions). Coverr explicitly forbids using its assets as AI training material or datasets (https://coverr.co/license). **Do not bulk-download either into an AI test dataset without the appropriate rights.**

For demo art use original assets, rights-cleared licensed footage, user-recorded clips, or dataset clips only if license permits public display. Do not imply a depicted person's endorsement or stage deceptive depictions of identifiable real people. For formal benchmarking prioritize dataset terms permitting evaluation, and retain proof of license/consent.

### Small-batch dataset strategy (do not download hundreds of GB)

| Stage | CONTEXT | PRELUDE | VEIL | CONTROL |
|---|---:|---:|---:|---:|
| T0 smoke | 5 synthetic/controlled honest+altered; 2 EVID if access granted | 4 Nexar (2 positive, 2 negative) | 2 PEViD | 2 procedural examples |
| T1 development | 12 EVID (stratify); 8 honest negatives | 12 Nexar (balanced, varied lighting) | 6 PEViD + 4 LSVTD | 6 CaptainCook or ExpVid |
| T2 held-out | 20 unseen EVID + 10 honest negatives | 20 unseen Nexar incl. hard negatives | 10 unseen clips if rights permit | 10 unseen procedures if feasible |
| Post-hackathon | 100+ EVID + independent real-world cases | 100+ Nexar + wider risk domains | Broad multilingual / high-res | Full ExpVid + independent expert review |

Counts are **targets**, contingent on license/access and available clips. Do not pretend T2 is complete if samples are missing. Dev/test splits must be source-disjoint where possible (avoid multiple edits of the same original across splits) to prevent leakage.

### Dataset acquisition workflow

1. Read dataset card, license, access requirement, README, size, label schema, allowed uses, and publication/demo permissions. **Check specifically whether a prize-awarding hackathon, public screenshots, public demos, and model API processing are allowed.** If not clear, request permission or choose a rights-cleared substitute.
2. Keep local media under `data/external/<dataset>/` with `.gitignore`; create manifest YAML/CSV with `id`, `path`, `source_url`, `license`, `allowed_use`, `split`, `label_file`, `sha256`, `notes`.
3. Download only first two accessible items. Decode them with FFprobe/FFmpeg; verify playable duration, audio, frame rate, codec and checksum.
4. Write one adapter per dataset, producing **normalized** samples: `{video, optional_original, ground_truth, cutoff, task, license_metadata}`.
5. Create deterministic seeds and source-disjoint train/dev/test partitions. Preserve an evaluation log and list excluded clips with reasons.
6. Build test harness before tweaking prompts. Labels must never be included in inputs sent to the model. Treat retrieved data as untrusted content, never instructions.
7. Retain dataset source + citation + licensing in internal manifest, include a public **download instructions** script rather than distributing restricted data.

---

## 7. CONTEXT implementation details

### Stage C1 — Single-video investigation

- Accept locally uploaded `.mp4/.mov/.webm` under configured size/duration caps and supported public URLs through a **provider adapter**. Don't assume a YouTube URL is downloadable just because it is searchable. Separate metadata lookup from licensed media access.
- FFprobe validation; hash original; extract shots/keyframes, audio waveform/segments, visual embeddings, OCR/text where available.
- Muse Spark scene summary and *verbatim factual claims* in audio/captions. Separate claims from speculation/opinions. Speech transcription via Muse Voice (or verified available ASR) where useful.
- Search independent sources: distinct spoken phrases, title/caption, visible logos/landmarks if appropriate, metadata, keyframes where allowed, Google Fact Check Claim Search API (has public API key requirement), approved text/video retrieval services.
- Candidate-source ranking: phrase hit → metadata matching → visual frame/embedding validation → deterministic temporal alignment. Do not trust a search snippet alone.
- Claim-evidence verification: supporting, contradictory, unrelated, unverifiable; always include cited URLs and exact aligned times where applicable.
- Render investigation dossier even without original; clearly mark `source_not_found` separately from manipulation evidence.

### Stage C2 — Media authenticity signals

- Parse available C2PA/content credentials **when present**, embedded media metadata, video stream discontinuities and edit history. Missing metadata is neutral.
- A deepfake model may provide a **screening signal** only if independently evaluated; never a universal fake/real badge. Use Deepfake-Eval-2024 for a separate detector benchmark if authorized.
- Maintain separate dimensions: `media_origin`, `editing_evidence`, `claim_support` and `source_provenance`. A real video can contain a false claim; an AI-generated video can be explicitly labeled fictional.

### Stage C3 — Strong evidence explorer

- Player timeline maps every finding to source media, and supports `source unavailable` state gracefully.
- Side-by-side source comparison only when retrieved source is verified; do not silently equate approximate matches.
- Show exactly which evidence would change a conclusion; allow user to challenge a finding and see source references.
- Prove harmless edit abstention: normal highlight with faithful narrative is not automatically labeled misinformation.

### CONTEXT evaluation

- **Retrieval@K:** original source present in top K matches, evaluated on samples with available source; test non-matching negatives.
- **Alignment:** absolute timestamp error, interval IoU, precision/recall of matched intervals, separate recall for omission/reorder/repetition; robustness to recompression, crop, speed variation.
- **Claim extraction:** precision/recall of verifiable statements with human labels; correct transcript and timecode citation.
- **Evidence correctness:** exact supported vs contradictory vs insufficient-evidence accuracy; unsupported citation rate.
- **End-to-end:** video-level and point-level labels where benchmark permits, plus attribution. Do not equate oracle-source vs web-search results or rebrand 5 custom examples as EVID-Bench accuracy.
- **Hallucination guard:** every clickable citation must resolve to a real source and accurate time range; backend rejects nonexistent references.

### CONTEXT gating targets (aspirational internal targets, not prior results)

- T0: 5/5 controlled clip alignments within ±2 s; no incorrectly invented source; all evidence timecodes valid.
- T1: >=80% temporal event detection on local held-out edits, with harmless negatives and report of misses. This is a smoke target, **not equivalent to EVID-Bench**.
- T2: report measured retrieval@5, precision, false accusations, cost and latency on unseen EVID-Bench examples; no minimum invented success rate if results are weaker.
- Fail if the system can't generate a single meaningful cited investigation without an oracle source.

---

## 8. PRELUDE implementation details

### Stage P1 — Offline anticipatory video analysis

1. Load Nexar positive and negative samples, including time-to-event annotations.
2. Define inference **cutoff** before the incident and restrict all model inputs to frames/audio before that cutoff.
3. Use SAM 3.1 where available to track roadway actors over a selected time window; retain stable IDs, masks and boxes.
4. Track centers in image coordinates; estimate velocities and path overlap with uncertainty. Monocular speed/distance estimates are not metric ground truth without camera calibration. Prefer relative pixel trajectories and clearly label them.
5. Muse Spark interprets scene dynamics and generates a *grounded risk cue*, citing observed actors and time window.
6. Alert when corroborated by multiple cues; abstain if tracking unreliable. Offline playback reveals how many seconds before event it first flagged risk; normal footage must rarely flag.
7. Render visual trajectories, risk cue moment, explanations and uncertainty. Provide an `analysis only — not driving assistance` label.

### PRELUDE evaluation

- **Event classification:** precision, recall, F1, AUROC/AUPRC where enough samples, with confidence intervals and class prevalence.
- **Warning lead time:** seconds before annotated event, distribution p50/p90; only for correctly detected positives.
- **False alarms:** fraction of normal clips with alerts and alerts per minute/hours of non-incident footage.
- **Early-inference integrity:** automated test asserts frames >= cutoff are excluded from all model calls, caches and context.
- **Track quality:** box/mask IoU or ID switches on a labeled tracking subset if labels exist; don't claim Nexar supplies all box/track labels without checking.
- **Calibration:** predicted percentages prohibited unless empirically calibrated; `potential path overlap` is safer than `87% chance of crash`.

### Gate

Prove one held-out positive early cue AND one negative safe clip without a fabricated alert. Expand to at least 12 varied held-out clips before presenting predictive performance. If warning depends on the crash frame or fails on safe footage, PRELUDE becomes future research only; remove it from hackathon hero claims.

---

## 9. VEIL implementation details

### Stage V1 — Connect existing privacy engine

- Audit existing VEIL code and working redaction endpoint; if not locally available, no greenfield rebuild this week.
- Map masks/PII findings into shared `Observation` and video overlay UI.
- Add explicit `Analyze privacy → Review → Protect → Export → Audit export` flow.
- Support face or license-plate protective masking as verified; add text/audio disclosure detection only if those modules truly exist and function.
- Use SAM 3.1 for masks/tracking when it improves continuity; keep manual review for misses and partial occlusion.
- Independently examine the **rendered output**, not only in-memory mask coordinates. Verify every sampled frame and interval of PII coverage where annotations allow; use OCR to test residual readable plate/text where applicable.

### VEIL evaluation

- Region recall/frame coverage and false-region rate; false negatives are more harmful than extra redaction.
- Mask coverage for moving actors, temporal gaps and ID switches, reappearance after occlusion, export integrity.
- OCR leakage: original sensitive text cannot remain readable after protection; sampling must include fast motion and short exposures.
- Audio leak rate for spoken PII if supported; prevent adding such a claim without audio benchmark.
- Visual utility score/side-by-side inspection; don't call masks natural replacement.

### Gate

A PEViD / LSVTD sample completes genuine `detect → protect → export → inspect` without unredacted frames in annotated regions at the tested resolution. If not, show VEIL as an **inactive future lens** instead of fake success.

---

## 10. CONTROL implementation details (after core demos)

### Stage X1 — Scientific/procedural reasoning

- First prove observation of tools, step ordering and visually apparent state changes on CaptainCook4D or ExpVid.
- For actual experimental validity, require user-provided hypothesis and alleged manipulated/control variables, independent measurements where available, and model reasoning constrained by observation/evidence.
- Separate `observed change` from `potential confound` and `causal inference`; many videos are not sufficient for causal conclusions.
- Deliver visualization of what variables changed, missing controls and suggested follow-up experiments.

### CONTROL evaluation

- Tool/step detection accuracy and step-order correctness.
- Confound detection precision/recall on manually reviewed controlled examples; deliberately include no-confound negatives.
- Correct abstention when the experiment or claimed conclusion cannot be inferred from available video.
- If benchmark lacks ground truth for causal validity, obtain independent domain-expert review; procedural error labels are not causal labels.

**Hackathon rule:** No CONTROL UI that claims real scientific validity without an evaluated engine. Leave behind only a clear roadmap if time is short.

---

## 11. Unified evaluation harness and testing matrix

### Test levels

| Level | Tool | Must prove | Release gate |
|---|---|---|---|
| Unit | pytest, Vitest | hashing, time math, transcript merging, schemas, adapters, thresholds | Green |
| Video integration | FFmpeg fixtures and actual benchmark clips | decode, sampling, alignment, tracks, source citation, encode | Green on 2 codecs / variable FPS sample |
| Model contract | Recorded golden fixtures + authenticated smoke | valid structured responses, citations, retries, no prompt injection obedience | Green; online API smoke recorded |
| Dataset evaluations | Benchmark adapters, held-out labels | quantitative results and failures, no ground-truth leakage | Full metrics report |
| End-to-end UI | Playwright Chromium + mobile viewport | upload, job status, video seeking, overlays, source inspect, export | Critical flows green |
| Visual regression | Playwright screenshots | layout and responsive stability | Critical views reviewed |
| Accessibility | axe-core, keyboard path | focus, semantics, reduced motion, contrast | No critical violations |
| Security | file fuzzer, dependency scans, adversarial URLs | sandboxing, SSRF, size limits, permissions, API secrets | No critical findings |
| User acceptance | Live walkthrough with 2–3 independent reviewers | understanding of actual findings, correct uncertainty | Review notes recorded |

### Required negative and adversarial cases

**Across domains:** static scene, heavy compression, extreme crop, rotated video, no audio, multilingual speech, background music, duplicate frames, variable FPS, unsupported codec, corrupted file, empty file, 0-byte upload, huge media, slow/failed model response, missing license, inaccessible URL, fake source page, malicious transcript containing instructions, misleading search snippet, object occlusion.

**CONTEXT:** accurate unaltered original, honest shortening, misleading omission, multiple unrelated sources, no match, mixed true/false claims, unavailable source, near-duplicate without shared provenance, false timestamp citation.

**PRELUDE:** normal vehicle crossing, safe adjacent trajectories, positive early collision cue, night/rain, stopped actor, camera shake, occlusion, background vehicles, cutoff leakage attempt.

**VEIL:** short 1–3-frame PII exposure, screen reflection, angled plate, blur/occlusion, tracking jump, audio number with no visual cue, export codec altering mask quality.

**CONTROL:** correct experiment, confounded experiment, visually unclear variable, hidden uncontrolled variable, procedural compliance but unsupported causal claim.

### Fair baselines and ablations

- CONTEXT baseline A: existing frame/video-diff only. Baseline B: Muse Spark without evidence retrieval. Baseline C: retrieved evidence + Muse. Report where improvement arises, including new false positives.
- PRELUDE baseline: Muse-only descriptive risk summary vs SAM tracks + motion features + Muse, with identical pre-event cutoffs.
- VEIL baseline: current detection+redaction vs tracking-enabled export audit; same footage and labels.
- Do not compare different data splits or source-known vs source-unknown tasks as one accuracy number.

### Evaluation artifact contract

Each result should include `run_id`, git commit, dataset name/version/license, split, sample IDs/hashes, inference-time visible input, model IDs, prompts/code versions, warnings, raw predictions, normalized predictions, ground truth available only in evaluation stage, metrics and failures, elapsed seconds, and cost estimates.

Write immutable JSONL per sample plus one concise Markdown/HTML scorecard. Do not distribute media from restricted datasets. Human review must be marked as separate from automated labels.

---

## 12. Development schedule, deadlines and stop rules

**Deadline**: Nov 4 2026, 9:00 PM ET (Nov 5, 7:30 AM IST). Do not leave final upload to the last hour.

| Date (IST) | Primary deliverable | Demonstration of completion | Stop rule |
|---|---|---|---|
| **Oct 29** | Repo audit, UX code adapter, dataset permissions and loader | 2 EVID + 2 Nexar media actually decode, manifests created; existing tests rerun | If datasets gated, use self-recorded + authorized clips, report gate |
| **Oct 30** | Single-video CONTEXT intake and source search | One real investigation with discovered independent candidate evidence; no oracle source input | If retrieval inaccessible, document supported indexed-corpus scope honestly |
| **Oct 31** | CONTEXT claim/evidence pipeline + real UI | Cited evidence dossier, honest-edit negative, timecodes and linked player work | If hallucinated citations persist, disable unsupported verdicts |
| **Nov 1** | PRELUDE SAM/video risk spike | One positive pre-event and one negative safe clip tested; measured warning lead time | If leaks future frames or flags safe clips, defer PRELUDE |
| **Nov 2** | Integrate feasible PRELUDE and/or existing VEIL | Same UI/data engine powers mode switch, actual analysis not seeded cards | Cut unfinished mode(s) completely from hero demo |
| **Nov 3** | Full tests, usability, visual finish, demo selection | Benchmark scorecard, Playwright pass, 3-min dry-run | Freeze new features; fix bugs only |
| **Nov 4** | Final validation, packaging and authorized submission | Public repo README, reproducible setup, demo video, disclosures, uploaded submission | No publication/submission without owner approval |

### Priority when time is constrained

1. Single-video CONTEXT with real independent evidence **and** beautiful visual proof.
2. Dataset-backed CONTEXT results, negatives, and transparent limitations.
3. PRELUDE validated early warning on genuine pre-event footage.
4. VEIL integration using existing code, if effortless and correct.
5. CONTROL, public SDK publication, browser extension, smart glasses: **not in hackathon critical path**.

### Explicit go/no-go gates

- **G0 access:** 2 public/gated data samples legally available and playable per selected domain; Meta credential works with one tiny authenticated call.
- **G1 CONTEXT:** Unseen single video yields real and clickable evidence, or honest abstention; no manually handed source; independent negative correctly left non-misleading.
- **G2 PRELUDE:** At least one pre-event cue and one safe negative; cutoff leakage tests pass.
- **G3 VEIL:** Actual export audit passes benchmarked protective coverage; otherwise hide mode from hero.
- **G4 UX:** Real backend evidence populates viewer; demo-only labels never appear as actual findings.
- **G5 release:** All critical E2E tests green; rights cleared for footage in public video; user explicitly authorizes public release and submission.

---

## 13. CI, deployment, performance, and safety

### CI jobs

- Python `ruff`, `pytest` (unit), OpenAPI validation.
- Frontend TypeScript check, ESLint, `npm run build`, Vitest and Playwright smoke.
- One lightweight public-domain/self-recorded media fixture in repo; benchmark media downloaded separately under licenses.
- Optional nightly external-API contract tests behind protected tokens; no secrets in pull-request logs.
- Dataset benchmark CI is opt-in/on-demand due size and rights; publish aggregate scores, not media.

### Media and system safety

- Limit media MIME, decoded duration, dimensions and size; FFprobe in subprocess with timeouts and untrusted URL safeguards.
- SSRF prevention: public IP/domain allowlist or blocked private/link-local/metadata addresses; don't fetch arbitrary user-provided URLs directly without validation.
- External media retrieval only from authorized services; respect site/API terms and robots/access restrictions.
- Basic content retention policy, user ability to delete temporary media and artifacts.
- Prompt injection defense: audio transcripts, web pages, OCR text and video overlays are data, never privileged instructions. Validate model JSON against schema and source IDs.
- PRELUDE never used for live-driving warnings; report not certified safety assistance.
- CONTEXT cannot accuse a named person of dishonesty without exceptionally strong evidence; avoid unsupported categorical allegations.
- VEIL stores sensitive originals locally where possible; sanitize logs and never send PII to model providers unknowingly.
- For model API, explicitly select Standard vs Contributor mode considering data sharing terms. Confirm account settings before uploading private footage.

### Performance targets (internal estimates, to measure)

- First upload acknowledgement under 2 seconds on local network.
- Partial scene/keyframe overview within 30–60 seconds on a ~30 second clip, hardware dependent.
- Complete investigation within a few minutes for short clips where retrieval is available; report observed p50/p95 rather than guarantee.
- UI seek/overlay synchronization <=0.5 s; avoid rerunning full inference on every click.
- Track API/video/frame spend per mode. Abort unbounded retry loops and show partial results.

---

## 14. Demo storyboard — prove the engine, not the number of tabs

**0:00–0:20** — Viewer is shown an authentic-seeming short video and its claim. "The footage is real. What about the story?"

**0:20–1:10** — Upload the single clip, start CONTEXT. It finds independently indexed or publicly accessible related evidence; reveal a source match and the missing context on a synchronized timeline. Citation links and timestamps are real. Use a rights-cleared, nonpolitical, nonmedical case if the rules impose content restrictions.

**1:10–1:45** — Switch to another honest shortening and demonstrate abstention: an edit is detected, but no unsupported claim of deception is made. Show why evidence status matters.

**1:45–2:25** — Switch to PRELUDE on a separate *pre-event* traffic clip. SAM tracks actors; show grounded motion and warning moment; reveal the subsequent incident only after the prediction has already been captured. If this mode fails its gate, devote time to a second stronger CONTEXT case instead.

**2:25–2:45** — Optional VEIL privacy-aware export using the already working redactor; demonstrate output audit only if real. Otherwise omit.

**2:45–3:00** — Show shared core evidence/time representation, three quantitative evaluation numbers with clear sample sizes, and the product vision: a reusable intelligence layer for video.

**Do not** present the studio as an already validated smart-glasses driving solution, general scientific truth engine, or zero-leak privacy guarantee.

---

## 15. Required deliverables

### Code and working UI
- Single-video intake and analysis job states.
- At least one truly working CONTEXT investigation with linked evidence.
- Existing original/edited alignment preserved as a deep-dive view.
- PRELUDE as a mode only if it passes cutoff and negative-case tests.
- VEIL as a mode only if existing redaction pipeline integrates correctly.
- Shared core modules, model adapters and typed API contracts.
- Polished responsive React/Tailwind/Lucide UI, no seeded outputs for uploaded media.

### Tests and research artifacts
- Dataset registry with direct acquisition links, license/access status, and exact split IDs.
- Scripts to fetch only allowed subsets.
- Recorded model-API smoke/cost tests.
- Unit, integration, E2E and accessible UI checks.
- Per-sample benchmark JSONL; consolidated metric tables, failure gallery, and model ablation table.
- Benchmark report clearly distinguishing controlled tests vs research benchmark vs live real-world test.

### Documentation
- README with truthful feature matrix, unsupported workflows, setup, model credentials and run commands.
- Architecture + data model explanation, licenses/attributions, evaluation protocol, reproducibility commands.
- Demo script and evidence/source citations, test screenshots, actual hardware/service usage.
- Clear limitations and safety caveats.

### Submission (approval-gated)
- Ensure event rules, creation cutoff, permitted assets, public repo requirements and legal constraints are checked against accepted participant instructions.
- Public repo does not contain API keys, restricted dataset media, personal videos or proprietary employer code.
- <=3-minute final demo video with actual working app; distinguish any canned fixture from real inference.
- Submit only after owner explicitly approves.

---

## 16. Codex autonomous execution contract

**Run this plan against the *existing* CONTEXT repository.** First inspect and preserve working code. Avoid discussions replacing execution. Each progress update must report the exact commit, changes, tests actually executed, datasets actually downloaded, measured results and blockers. Do not call a mode "working" without a real inference case and benchmark negative. Do not spend time on further architecture diagrams, generated mockups, releases or SDK marketing until a G1 CONTEXT investigation and its evaluation exist.

### Start-now sequence

1. Confirm git status, test suite, frontend build and Meta API setup, keeping secrets out of logs.
2. Implement `eval/datasets_registry.csv` and `eval/fetch_dataset.py` for EVID-Bench and Nexar (license gates, no unauthorized mass download).
3. Download/inspect **two** legal videos from each; create hashes, normalized manifest and sample adapter tests.
4. Create and run a single-video CONTEXT smoke against a real EVID example without leaking original IDs; show whether source retrieval found anything.
5. Replace one seeded frontend scenario with actual job-driven data and prove timeline click → evidence seek works.
6. Run a harmless-edit negative and report false accusation handling.
7. Only then begin PRELUDE SAM tracking / pre-event risk analysis.

If API access or rights block step 3/4, report the exact blocker and run a **rights-cleared alternative** rather than invent success. Keep shipping within the deadline.

---

## 17. Evidence and links consulted (29 October 2026)

- Meta hackathon official event: https://dev.meta.ai/events/global-hackathon
- Meta models: https://dev.meta.ai/docs/models
- Meta video understanding: https://dev.meta.ai/docs/video-understanding
- SAM segmentation: https://dev.meta.ai/docs/sam/overview
- EVID paper: https://aclanthology.org/2026.findings-emnlp.763/
- EVID dataset: https://huggingface.co/datasets/Kirito-Lab/EVID-Bench
- EVID baseline code: https://github.com/yutao1024/EVID-Bench
- Deepfake-Eval-2024: https://huggingface.co/datasets/nuriachandra/Deepfake-Eval-2024
- Nexar dashcam: https://huggingface.co/datasets/nexar-ai/nexar_collision_prediction
- RiskCue paper: https://aclanthology.org/2026.emnlp-main.2082/
- PEViD-UHD: https://www.epfl.ch/labs/mmspg/downloads/pevid-uhd/
- LSVTD: https://davar-lab.github.io/dataset/lsvtd.html
- Privacy VITA: https://aclanthology.org/2026.nlpaics-1.27/
- CCPD: https://github.com/detectRecog/CCPD
- ExpVid: https://proceedings.iclr.cc/paper_files/paper/2026/hash/86833e97827ff52d297a9fbde5842a81-Abstract-Conference.html
- CaptainCook4D: https://captaincook4d.github.io/captain-cook/
- Google Fact Check Tools API: https://developers.google.com/fact-check/tools/api/
- YouTube Data API: https://developers.google.com/youtube/data/getting-started
- Pexels AI/data restrictions: https://help.pexels.com/hc/en-us/articles/900005880463-What-are-the-Terms-and-Conditions
- Coverr license: https://coverr.co/license
