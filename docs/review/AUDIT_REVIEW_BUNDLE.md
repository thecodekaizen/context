# AUDIT_SUMMARY.md

# Independent audit summary — 29 October 2026

Audited active repository at `d61e860`. [Full verdict](docs/audit/01_EXECUTIVE_VERDICT.md) · [Capability matrix](docs/audit/02_VISION_VS_IMPLEMENTATION.md) · [Executed evidence](docs/audit/04_DATASETS_AND_TEST_RESULTS.md) · [Next-work backlog](docs/audit/07_EXECUTION_BACKLOG.md).

1. **What we wanted:** one reusable video-intelligence engine: CONTEXT investigates claims/provenance; PRELUDE anticipates physical risk; VEIL protects exported media; CONTROL measures experiments. AI interprets, algorithms measure, physics constrains, evidence verifies.

2. **What we have:** a real single-video CONTEXT dossier, a conservative visual/audio comparator and small local source index, plus a separate PRELUDE flow/blob-and-model experiment. Shared media foundations exist; common cross-lens observations/tracks/jobs do not. VEIL/CONTROL are not integrated.

3. **What actually works:** 82 backend tests and six existing browser tests passed; production build passed. A fresh real browser upload completed video → Spark observations → live search → eight fetched sources → checked quotes → dossier → decoded playback. It retained seven observations, six claims and four supported/two inconclusive assessments. Four expected local corpus sources matched; one expected no-match case rejected. These are bounded integration results, not general accuracy.

4. **What only appears proven:** PRELUDE's successful E2E warning is mocked. Published 100% sensitivity contradicts inherited raw 0/2 positives detected. Fresh benchmark: one missed positive, two correct negatives, one provider 503 excluded by the runner. Separate later-cutoff UI inference did return a cue, but retrospective model cue time is not prospective alert time. A local probe accepted −100s as a cue and displayed a 104.5s lead. Citation validation also accepted a whitespace-only excerpt as support in a local probe. Corpus claim precision is never scored; its negative contains footage from the indexed movie. One complete dossier retained zero observations after schema rejection.

5. **What is missing:** automatic matching of independently discovered online original videos, a complete primary source-to-semantic-edit workflow, independent source-disjoint evaluation, valid actor tracking/physical warning measurements, privacy-export integration and scientific analysis. Also partial recovery/cancellation, loaded responsive layout, keyboard evidence targets, theme/overlay controls and a validated export action. Ruff reports 20 issues; frontend format check flags five files.

6. **How close to a winning-caliber demo:** a credible foundation, not ready for the broad claims. Independent competitive-readiness judgment: **4.5/10**; assumed impact/Meta/technical/demo weights give **5.38/10**, not an official score. The deadline is confirmed on the official event page; the weights remain planning assumptions. A focused, honest CONTEXT demonstration is feasible; completing the universal vision within the week is not.

7. **Exactly what Codex should implement next, after review:** first fix benchmark accounting/labels and unsupported documentation claims. Then connect `library.rank_sources` and actual supported audio/visual edits to `context_pack.build_pack` + `meta.interpret`, carrying bounded source/edit evidence into the primary dossier. Preserve uncertainty when boundaries fail. Add explicit partial/provider-failure states, then prove contradiction, meaningful edit and harmless abstention on new rights-cleared sources. Keep the player alongside findings and fix loaded overflow/keyboard navigation. PRELUDE remains conditional; defer CONTROL and greenfield privacy work.

No feature implementation was changed and no follow-on implementation was started. Audit reports, screenshots, model receipts and generated test/build artifacts are the only outputs. [Evidence index](docs/audit/08_EVIDENCE_INDEX.md).


---

# 02_VISION_VS_IMPLEMENTATION.md

Audit date: 29 October 2026. Repository: `/Users/thecodekaizen/Code/Projects/hackathons/context`. Audited HEAD: `d61e8607b94fc61381c324be0a94d3e9f98038f7`. Source was initially clean. No feature code was changed. See [evidence index](08_EVIDENCE_INDEX.md) for reproducible paths and the distinction between inherited and fresh evidence.

# Vision versus implementation

The canonical vision is in `.hackathon/VIDEO_INTELLIGENCE_VISION_DECISIONS.md` and the full implementation plan. The React ZIP's `context-studio/UX_SPEC.md` describes one persistent player/playhead with four question-oriented lenses. It explicitly labels its seeded scenarios as illustrative. The active repository has evolved from comparator → single-video dossier → local-corpus integration → PRELUDE; it has not implemented the full shared observation/track/transformation architecture.

The governing principle is only partially realized: algorithms genuinely measure temporal correspondence; AI genuinely interprets video and documents; physics is a limited heuristic in PRELUDE; evidence checks verify citation existence and bounds, not factual truth or semantic entailment.

Status vocabulary: **VERIFIED** = executed on a real input with inspectable output; **IMPLEMENTED, UNVERIFIED** = inspected code without sufficient execution; **PARTIAL** = working stages, incomplete outcome; **MOCKED** = fixture inference for the specified demonstration; **BROKEN** = attempted execution failed; **MISSING** = no meaningful active implementation. These labels apply to a bounded capability, never universal accuracy.

Effort below assumes one experienced full-time engineer, existing local tooling and working API credit. A day is about 6 focused hours; rights/annotation waiting time is additional. P0 blocks an honest hero demonstration, P1 materially limits usefulness/reliability, P2 improves experience, P3 is beyond this deadline.

| Capability | Intended behavior | Actual behavior | Status | Evidence | Missing work | Severity | Effort / assumptions |
|---|---|---|---|---|---|---|---|
| Single-video intake | Begin without original | Multipart upload, optional caption; real fresh job completed | VERIFIED | `dossier_api.router.create`; fresh-upload receipt | Broader codec/rotation/VFR testing | P1 | 0.5–1d |
| Online video input | Accessible arbitrary URL | Direct NASA/Wikimedia media allowlist only; no YouTube/social download | PARTIAL | `retrieval.public_url`, `download_video` | Clear coverage; add provider only with licensed access | P1 | 0.5d copy; 2–5d/provider |
| Scene/events | Timed audiovisual observations | Spark video understanding; first 180s only | PARTIAL | `dossier.prepare`, `validate_analysis`; 7 fresh observations | Independent event/time accuracy labels; partial schema handling | P1 | 1–2d small set |
| Speech | Searchable, aligned transcript | Retains audio in model clip; no separate ASR or transcript contract | PARTIAL | `prepare`; `Claim.origin`; no Voice call | Verify spoken quotations, optionally ASR where errors justify it | P1 | 1–2d |
| Claim extraction | Extract verifiable statements | Spark claims plus faithful supplied-caption insertion | VERIFIED | `validate_analysis`; fresh 6 claims | Precision/recall and claim relevance review | P1 | 1d labeling |
| External evidence discovery | Independent credible sources | Real Spark web search receipts and up to 8 fetched documents | VERIFIED | `search_receipts`, `inspect_source`; fresh sources | Measure relevance/coverage; PDF/video handling | P1 | 1–3d |
| Original-video retrieval | Discover unseen recording online | Local four-item index; web search does not download/match found originals | PARTIAL | `library.rank_sources`; `dossier.investigate` | Candidate-video acquisition/verification within supported scope | P0 for broad claim | 2–4d bounded provider |
| Visual alignment | Accurate footage correspondence | 4Hz 24×16 RGB mean absolute distance, ambiguity rejection | VERIFIED | `align_samples`; `test_production_footage_findings` | Honest robustness limits and held-out timestamps | P1 | 0.5–2d |
| Audio matching | Corroborate temporal relations | 2kHz mono normalized FFT correlation; separate evidence | VERIFIED | `audio_alignment.correlate`; audio tests | Correct 16kHz documentation; avoid video-authentication inference | P0 wording | 1–2h |
| Omission/reorder/repetition | Explain measured edits | Good controlled-film coverage; fresh corpus reorder yields zero findings | PARTIAL | `alignment.py`; fresh case 3 | Use audio breakpoints in edit reconstruction without overstating images | P0 | 1–2d |
| Meaning-changing edits | Compare source meaning to edit | Manual comparator review exists; primary dossier verifies documents only | PARTIAL | `meta.interpret`, `context_pack.build_pack`, `investigate` | Connect bounded review to primary evidence | P0 | 1–2d |
| Harmless-edit abstention | Avoid equating cuts with lies | No accusations on tested honest cases; five-case authored comparison gate | PARTIAL | inherited gate timing recheck; fresh corpus | Independent labels and new sources | P0 | 1–2d |
| Citation correctness | Inspect source-backed conclusions | IDs/exact normalized excerpts checked; semantic relation remains model output | PARTIAL | `validate_assessment`; checked excerpts | Reject whitespace-only excerpts; entailment audit, irrelevant-source negatives | P0 | 1d small set |
| Authenticity/deepfake signals | Validated forensic evidence | Explicit `not_established`; no detector/C2PA | MISSING | `investigate` authenticity record | Preserve abstention; dedicated post-deadline evaluation | P3 | 1–3 weeks |
| PRELUDE pre-cutoff pixels | Exclude incident from inference | FFmpeg output duration bound and sampled images | VERIFIED bounded output | `extract_pre_incident_frames`; tests | Source-PTS/sentinel tests; do not claim decoder never touches later reference frames | P1 | 0.5–1d |
| Object detection/segmentation | Grounded persistent actors | Frame differences/contours; blobs heuristically labeled vehicle | PARTIAL | `compute_actor_tracks`; live screenshot | Actual actor validation and IDs; SAM only if it improves measured tracking | P1 conditional | 2–4d |
| Physical risk | Grounded trajectory conflict, uncertainty | Fixed FOE flow and area-change proxies; no calibrated camera/TTC | PARTIAL | `compute_actor_tracks` | Correct units, ego-motion, stable track geometry, uncertainty | P1 conditional | 2–5d prototype |
| Prospective early warning | Alert before incident | Batch pre-cutoff model retrospectively selects cue | PARTIAL | `run_prelude_investigation`; fresh benchmark | Prefix replay, alert commit times, independent incidents | P0 if demoed | 2–3d plus labels |
| PRELUDE robustness | Positive/negative benchmark | Fresh: 1 miss, 2 correct negatives, 1 HTTP 503 | BROKEN on one request; PARTIAL overall | prelude log/summary | Count errors, freeze timing, validate outputs | P0 if demoed | 1–2d |
| VEIL protection | Detect → redact → export → inspect | No active route, dependency or UI; separate older project exists | MISSING integration | active file/API inventory; sibling VEIL | Audit and adapt existing API only after CONTEXT | P2 contingent | 2–4d integration, not promised |
| CONTROL | Measurement/procedure/confounds | No active analyzer/UI | MISSING | active file/API inventory | Post-hackathon measured experiment slice | P3 | 2–6 weeks |
| Reusable evidence contracts | Shared assets/events/tracks/provenance | Comparator v1, dossier v2 and PreludeDossier differ | PARTIAL | `types.ts`, `dossier.py`, `prelude.py` | Minimal asset/time/evidence envelope; keep domain records | P1 | 1–2d incremental |
| Provider orchestration | Cache/retry/batch/cancel/recover | Three bespoke Spark call paths; limited review cache; lock | PARTIAL | `meta.py`, `dossier.py`, `prelude.py` | Shared request receipt and error envelope; bounded retry/recovery | P1 | 1–2d |
| Dataset adapters | Licensed, normalized, reproducible splits | Registries + hardcoded local paths; no generic fetch/rights gate | PARTIAL | `eval/datasets_registry.csv`, runners | Sample identity/license manifests and independent holdout | P0 | 1–2d plus access |
| Unified video workspace | Player remains primary across lenses | Distinct dossier/comparator/PRELUDE states; switching not same asset | PARTIAL | `main.tsx`; screenshots | Shared selected asset/playhead; hide intake after load | P1 | 1–2d |
| Intelligent overlays | Timed, inspectable, toggleable | PRELUDE canvas of real blob geometry; CONTEXT metadata only | PARTIAL | `PreludeStudio`; `InvestigationDossier` | Toggle, accurate labels and evidence-linked intervals | P2 | 0.5–1d |
| Evidence navigation | Click → precise seek → source | Actual observations/claims seek; overview quotations lack direct source links | PARTIAL | browser seeking; `seekTo`; claims links | Keyboard controls and consistent finding-to-source action | P1 | 0.5–1d |
| Dossier export | Inspectable portable report | JSON media endpoint exists; no primary download button | PARTIAL | `dossier_api.media`; frontend | Validated report export (raw file endpoint currently bypasses read revalidation) | P1 | 0.5d |
| Responsive/light/accessibility | Beautiful, usable across sizes | Dark CSS only; loaded views overflow; clickable divs | PARTIAL / MISSING theme | browser width metrics, CSS | Fix layout and semantics; then theme | P1/P2 | 1–2d |
| Job progress/recovery | Partial, error, cancelled states | Stage polling works; errors render misleading complete-summary fallback | PARTIAL | invalid upload screenshot; `main.tsx` | Partial result, visible failure, abort/poll cleanup | P1 | 1–2d |
| Reproducible clean clone | Tests and demo from setup | Local suite passes; E2E saved files in ignored data | PARTIAL | `.gitignore`, E2E spec, CI | Rights-cleared seeded artifacts/acquisition instructions | P1 | 0.5–1d |

## Architecture fit

There are **two real analyzer paths plus a comparison subsystem**, not four dashboards. Shared FFmpeg/probe/hash/playback and local-source comparison have meaningful reuse. PRELUDE shares `probe`, the API lock and app shell, but has separate extraction, provider calls, risk schemas and frontend player. No common event store, transcript, spatial convention, cancellation or evaluation adapter is established across domains.

Keep this layout. Extract only the useful common pieces: asset identity + seconds/PTS convention, typed evidence references, model request/usage/error receipts, and resumable job state. A package monorepo, distributed queue, generic causality framework or wholesale frontend rewrite would consume the deadline without resolving the observed gaps.


---

# 07_EXECUTION_BACKLOG.md

Audit date: 29 October 2026. Audited HEAD: `d61e8607b94fc61381c324be0a94d3e9f98038f7`. These are proposals, not implementation authorization. [Evidence index](08_EVIDENCE_INDEX.md).

# Execution backlog and go/no-go plan

## Scope and capacity

Keep Python/FastAPI, current React app, source index, conservative alignment, raw provider receipts and saved dossier logic. Do not restart, restructure the repository or introduce distributed infrastructure. The goal before Nov 4, 9 PM ET is two or three independently demonstrated **capabilities**, not four completed lenses.

Estimates assume one engineer, 6 focused hours/day, working existing API access, short rights-cleared clips and access to one independent annotator/reviewer. Rights approval or provider outage is additional elapsed time. Critical subset is roughly **5–7 engineer-days** including review/buffer; the upper bound exceeds comfortable remaining capacity. Start with A1/A2/A3/A4 and C1; cut optional tracks before reducing evidence quality. Tasks are ordered by dependency, not a promise that every item fits.

## Track A — mandatory working-engine proof

### A1. Correct evaluation accounting and freeze the evidence protocol

**Why:** Current 100% claims exceed actual scored behavior; PRELUDE service errors disappear, negative footage overlaps its corpus, and source-known semantic comparisons are called held out.

**Reuse/files:** `scripts/run_corpus_context_benchmark.py`, `scripts/run_prelude_benchmark.py`, `run_registered_gate.py`, `eval/datasets_registry.csv`, existing manifests/receipts, `docs/model-card.md`, `docs/evaluation.md`.

**Dependencies:** None. Obtain actual rights/split metadata before new acquisitions.

**Acceptance:** Each immutable run records commit, sample hash/upstream ID, permission status, split, prompt/model, inference inputs, output, service errors and elapsed/cost. Count every attempted sample; distinguish unavailable from wrong. Expected semantic labels are actually scored. A pure no-match input shares no footage with the corpus. Documentation reports denominators and limitations. No historical failure overwritten.

**Real test:** Rerun the current cases, force one provider failure, and check the attempted/completed/correct totals and nonzero gate failure result. Independently review incident times and label rationale.

**Failure/fallback:** If rights/labels cannot be established, retain development-only labels and remove general accuracy language. Do not obtain a better score by dropping hard cases.

**Risk/effort:** Low code risk, moderate annotation dependency; 0.5–1d. **Critical path: yes.**

### A2. Close retrieval → measured edit → semantic explanation in CONTEXT

**Why:** The primary pipeline can find a reference without explaining its changed meaning; the fresh reorder case had a source but no findings. This is the missing hero interaction.

**Reuse/files:** `library.rank_sources`, `alignment.align_samples`, `audio_alignment`, `context_pack.plan_clips/build_pack`, `meta.interpret/validate_interpretation`, `dossier.investigate`, `dossier_api`, `InvestigationDossier.tsx` and current comparator.

**Dependencies:** A1 scoring; valid matched reference available in the local collection. Do not add open-web acquisition as a hidden dependency.

**Acceptance:** Source identity is checked; audio correspondences remain explicitly separate from visual evidence. Breakpoint reconstruction uses supported modality-specific intervals without treating matched audio as matched pixels. Primary dossier includes bounded source/edit semantic observations, timestamped citations, uncertainty and a direct player reveal. No deception conclusion from cut existence alone; unavailable semantic review leaves measured edits inspectable.

**Real test:** Honest qualification, authored false-caption omission, chronology reorder and speech-negation edit, plus one new source with new recipes. Inspect each cut boundary and actual surrounding words. Negative must remain non-accusatory; invalid citations fail closed. At least one real browser flow reveals the missing source passage with <=0.5s seek error.

**Failure/fallback:** Unsupported boundaries stay unresolved. If source cannot be matched, still deliver source-linked claim investigation; explicitly omit the source-comparison claim for that case.

**Risk/effort:** Moderate/high timing ambiguity; 1–2d for bounded integration, broader alignment robustness excluded. **Critical path: yes for missing-context hero.**

### A3. Reliable partial results and bounded provider failure recovery

**Why:** Useful measurements currently disappear behind later model failure, empty validated analyses say complete, and polling can run forever.

**Reuse/files:** `dossier.write/investigate`, `dossier_api.read_report/process`, `model_request`, `meta.interpret`, `main.tsx` polling/stage UI. Keep atomic files and local storage.

**Dependencies:** A1 run accounting; no new service required.

**Acceptance:** Distinguish complete, partial, failed and unavailable. All observations rejected => explicit unavailable analysis stage. Preserve measured matches/fetched sources after later error. Record bounded request attempts/timeouts, token usage and retryable status; allow user-triggered retry of failed stage without repeat paid success stages. Startup marks interrupted jobs recoverable. Stop/clean up polling; cancellation communicates whether only UI waiting or server work stopped. Unknown risk never reads nominal. Citation validation rejects normalized-empty/whitespace-only excerpts and other meaningless quote inputs; no supported/contradicted verdict survives without meaningful source evidence.

**Real test:** Short real upload plus controlled 503/timeout/malformed JSON; restart after observations; verify original successful receipts stay unchanged and partial findings remain accessible. Corrupt file must display failure without a complete-success sentence.

**Failure/fallback:** One clear error with retained evidence and manual rerun; no silent loops or blanket automatic replay of expensive stages.

**Risk/effort:** Moderate; 0.75–1.5d for a local, one-worker solution. **Critical path: yes.**

### A4. Freeze a small independent source-disjoint proof set

**Why:** All audited examples are reused development material. A real showcase needs fresh evidence and a documented negative.

**Reuse/files:** Gate manifest hash checks, `scripts/evaluate.py`, corpus runner, dataset registry; add a small normalized eval manifest/adapter only where needed.

**Dependencies:** A1, A2 and rights-cleared media. EVID access is optional, not a deadline dependency.

**Acceptance:** At least six frozen cases across >=2 previously unused source recordings: two honest/unaltered, two meaningful edits, one unrelated and one source-unavailable case; actual source retrieval corpus has plausible distractors. Labels independently reviewed before inference; source IDs/answers withheld from request input. Record retrieval success, matched-interval error, semantic decision, citation entailment review, false accusations, abstention and service failures. Public footage permissions recorded.

**Real test:** Run once with frozen prompts, manually inspect all retained source quotes/timecodes, and show failed examples. No public pretrained exposure claim can be made; 'held out' means held out from this project's development.

**Failure/fallback:** Fewer legally available samples => report exact count and reduced claim scope. If either honest negative is accused or a positive depends on fabricated evidence, no-go for categorical verdict demo.

**Risk/effort:** Annotation/access moderate; 1–2d including review. **Critical path: yes.**

## Track B — high-impact improvements

### B1. Measure Meta's incremental contribution on the same cases

**Why:** Spark is central but benefit over model memory or pure comparison is unquantified.

**Reuse/files:** `dossier.model_request`, `verification_prompt`, A4 runner and raw receipts.

**Dependencies:** A4 frozen cases; fixed budget.

**Acceptance:** Same cases/same annotations compare algorithm-only source matching, video model without retrieved documents, and full fetched-evidence pipeline. Report correct decisions, unsupported assertions, false accusations, unavailable outputs, latency and cost; no different-split comparisons. Do not add models.

**Real test:** All six cases; blind human assessment of quote support. **Fallback:** if retrieval adds no demonstrated benefit, retain useful workflow but remove improvement claims. **Risk/effort:** Moderate budget/reviewer cost; 0.5–1d. **Critical:** desirable after A4, cut before core correctness.

### B2. Bounded external original-video candidate retrieval

**Why:** Local collection search is useful but does not fulfill independently discovering an online original.

**Reuse/files:** `retrieval.search_receipts/select_sources/download_video`, media hashes, `library.rank_sources`, dossier provenance.

**Dependencies:** A2; one legitimate supported source provider with permission and accessible candidate media.

**Acceptance:** One unfamiliar uploaded clip discovers, acquires and aligns a video candidate without supplied original ID. Record each candidate and rejection; document a source-unavailable example. Do not equate document citations with footage match or claim universal social URL support.

**Real test:** Two source-unknown uploads from distinct rights-cleared sources and unrelated distractor; inspect download provenance and aligned intervals. **Fallback:** transparently label collection scope; online document search remains useful. **Risk/effort:** High access/coverage risk, 2–4d/provider. **Critical:** no if submission explicitly claims bounded index scope; yes before any broad original-discovery claim. Do not squeeze into deadline at cost of A4.

### B3. PRELUDE correctness and prospective replay gate — conditional

**Why:** Current positive predictions and units are not valid grounds for the published claims.

**Reuse/files:** `prelude.py`, `api.PRELUDE_SAMPLES`, runner, tests, `PreludeStudio.tsx`.

**Dependencies:** A1 and independent rights/incident annotations; only start after CONTEXT gate passes.

**Acceptance:** Strict booleans/risk enum/finite in-bounds cue; unknown/error distinct from quiet traffic; consistent sample times; px/frame versus px/s fixed; area proxy not tau/TTC. Sentinel source-frame test proves inference boundary. Replay prefixes sequentially and commit alert at each prefix before later frames exist. Lead = incident minus actual alert prefix, not model-backdated cue. Vehicle tracks need labeled actor geometry and one-to-one identity checks, or relabel as motion regions. At least 12 varied unseen positive/negative clips, report all errors, false alarms and availability. Fix upload media-serving whitelist before claiming upload workflow.

**Real test:** Hard safe crossings, turning camera/ego motion and pre-incident positives with independent timestamps. Compare model-only versus flow+model on identical prefixes. **Fallback:** research replay only, excluded from hero and accuracy table if no prospective positive or safe-control failures. **Risk/effort:** High, 2–4d minimum prototype; validation can take longer. **Critical:** no; do not spend CONTEXT's remaining budget here.

## Track C — exceptional exploration of real results

### C1. Make the player persistent and fix loaded-view responsiveness

**Why:** Actual evidence is hard to inspect; loaded views overflow even at 1280px.

**Reuse/files:** `main.tsx`, `InvestigationDossier.tsx`, comparator state, `style.css`; use reference UX layout selectively.

**Dependencies:** None for layout; A2 for semantic reveal.

**Acceptance:** Collapse intake after launch; dominant player remains visible beside selected finding/source on desktop. No horizontal overflow at 375/768/1280/1600 in overview/player/claims/sources/PRELUDE, and player retains useful size. Switching CONTEXT↔comparison keeps the same asset and playhead. Do not rewrite the whole app.

**Real test:** Fresh result, long URLs/claims, error and partial cases at every size; screenshot review and DOM scrollWidth check. **Fallback:** simple stacked player/cards; no decorative layout that hides evidence. **Risk/effort:** Moderate, 0.75–1.25d. **Critical:** yes for compelling, inspectable demo; mobile polish can be narrower if explicitly desktop-only.

### C2. Evidence controls, truthful copy and validated export

**Why:** Mouse-only findings, static overview quote IDs and misleading success labels undermine trust.

**Reuse/files:** `InvestigationDossier.tsx`, `PreludeStudio.tsx`, `main.tsx`, `dossier_api.read_report`, existing focus/reduced-motion CSS.

**Dependencies:** A3 states; A2 evidence links.

**Acceptance:** Semantic keyboard buttons for every seek target; visible focus; finding→video→source within two actions; exact excerpt badge says 'quote located', not truth verified. Show analyzed duration, inference versus measured timing, source scope and saved/fresh run date. Export validated dossier including limitations, versions and hashes. No raw stale-report bypass. An overlay switch only appears for actual generated overlay data.

**Real test:** Keyboard-only fresh result inspection, source link, seek and export; inspect downloaded JSON against validated API. **Fallback:** downloadable JSON plus clear limitations; no certificate language. **Risk/effort:** Low/moderate, 0.5–1d. **Critical:** yes for copy/keyboard/core links; optional overlay enhancements later.

### C3. Theme and restrained visual polish

**Why:** Helps reference fidelity after functional UX is fixed.

**Reuse/files:** Existing CSS variables, reference light/dark screens; no requirement to introduce Tailwind/Lucide merely for compliance.

**Dependencies:** C1/C2 stable. **Acceptance:** Saved theme, legible status/uncertainty, focus contrast, reduced motion, no color-only truth signals. **Real test:** Loaded real results in both themes at desktop/mobile. **Fallback:** one well-tested dark theme. **Risk/effort:** Low, 0.5–1d. **Critical:** no.

## Track D — post-hackathon

### D1. Integrate existing VEIL without rebuilding it

**Why:** Protect-before-sharing is useful once the investigation is trustworthy. **Reuse/files:** older `/Users/thecodekaizen/Documents/ChatGPT/Hackathons/veil` API/pipeline/export-verifier, active asset/evidence adapter and future Protect UI. **Dependencies:** separate audit of current sibling pipeline, permissions, exact region/time mapping and final-export leakage protocol. **Acceptance:** one consented clip detect→review→export→inspect, source/output hashes, no uncovered labeled frames/audio, honest residual limits. **Test:** motion/occlusion/brief PII and audio controls on actual exported file. **Fallback:** disabled Protect capability, no green privacy badge. **Risk/effort:** Moderate/high, 2–4d integration plus evaluation. **Critical:** no.

### D2. CONTROL measured experiment slice

**Why:** Scientific analysis needs observed quantities before causal explanations. **Reuse/files:** shared media/time/evidence and separate analyzer; historical thermal investigator is research reference, not an integrated video capability. **Dependencies:** rights-cleared experiment, calibration/measurement labels and expert review. **Acceptance:** track one physical quantity/time series with error bounds, observed stages, possible confounds clearly separated from conclusions; no causal inference from procedure alone. **Test:** known physical trajectory plus correct/confounded/insufficient-view negatives. **Fallback:** observations only. **Risk/effort:** High, 2–6 weeks. **Critical:** no.

### D3. Broad platform and scientific robustness

Open-world video retrieval, evaluated authenticity screening/C2PA, calibrated multi-object tracking, metric geometry, diverse multilingual audio, privacy replacement, comprehensive datasets and robust retention/deployment belong after the deadline. Reuse the measured core; introduce common contracts only where a second actual consumer needs them. Acceptance is independent task accuracy/reliability, not the existence of generic classes. Effort: weeks to months; no hackathon promise.

## Recommended critical path until deadline

| Date (IST) | Deliverable | Go/no-go |
|---|---|---|
| Oct 29 remainder | Review audit, preserve failure evidence; agree focused CONTEXT claims | No implementation performed by this audit |
| Oct 30 | A1 + start A2; fix arithmetic/schema claim blockers if retained in any screen | Reproducible attempted/completed accounting and actual source/edit review |
| Oct 31 | Finish bounded A2; A3 partial/error recovery | Fresh single-input source→comparison→meaning evidence and harmless negative |
| Nov 1 | A4 frozen independent set; begin C1 | Stop claiming broad capability if holdout fails; show failure openly |
| Nov 2 | C1/C2 and scoped B1 if budget permits | Real-result mobile/desktop, keyboard, citation and export checks |
| Nov 3 | Repeat frozen evaluation after final changes; clean-clone walkthrough; factual demo rehearsal | No new lenses/models; rights and all claims traceable |
| Nov 4 to Nov 5 07:30 IST | Buffer, final verification and owner-authorized packaging/submission | Freeze earlier; public release/submission is a separate approval |

PRELUDE is not a parallel must-finish task. If CONTEXT consumes the budget, demonstrate three connected CONTEXT capabilities. A compelling source-linked contradiction, measured semantic edit and honest abstention preserve the larger vision without pretending the entire platform exists.
