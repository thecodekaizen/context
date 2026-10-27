# Hackathon execution plan

**Event:** Oct 26–Nov 4, 2026. **Kickoff:** Mon Oct 26, 12:00 PM GMT-5. The kickoff stream said “Hacking starts now”; the guide lists the formal building period as Oct 27–Nov 4. Record the actual start of each hackathon feature in the daily log and keep all earlier setup clearly marked as pre-event preparation. **Submission deadline:** Wed Nov 4, 9:00 PM ET via the Cerebral Valley platform. The submission needs a CV-platform entry listing every teammate, an accessible three-minute demo video, a public GitHub repository, and submission before the cutoff. The live kickoff rubric weights impact 30%, Meta AI tooling 25%, technical depth 20%, and demo 25%. Check the event platform for any schedule updates.

Do not represent the pre-event repo, docs, or mockups as hackathon-built product features. Keep the existing foundation clearly labeled as pre-event preparation, and make the new product work easy to identify in commits, the demo, and submission text.

## Project framing

THREAD will focus the hackathon demo on **creative-project evolution**: discover how themes, constraints, and directions change across a creator's own dated project artifacts, then let the creator inspect, challenge, and confirm a finding before generating a project brief or another small creative artifact. Do not profile the person or infer personality traits. This is temporal evidence-backed discovery, not a basic RAG answer over documents. The user-facing product is an investigation/workflow, not a dashboard as the main feature; avoid a Streamlit-only demo.

Meta models must be part of the working product path, not just mentioned in the README. On Day 1, verify access and choose a supported model/task from the official Meta Model API docs. Keep a fixture path for repeatability, but the final demo must clearly show where the Meta model contributes.

## Scope

### P0 — must work

- One bounded synthetic creative-project archive with dates, source types, and rights-safe contents.
- One Meta model integrated into the main flow for a verified supported task, behind the provider boundary.
- Temporal memories that retain source provenance.
- CLI discovery of **one** specific evolution/pattern claim, with supporting and counter-evidence plus uncertainty.
- A way for the user to challenge, revise, reject, or confirm the claim.
- One small artifact gated on explicit confirmation.
- Minimal end-to-end demo surface only after the CLI gate passes; deterministic fallback and three-minute video.

### P1 — only after P0 works

- A second discovery family (such as cross-project motif or contradiction), more input modalities, richer timeline, or another artifact type.

### P2 — out of scope

- Personality analysis, psychological profiling, mental-health advice, generic chat over documents, basic RAG as the core value, a Streamlit-only app, a dashboard as the main feature, continuous sync, broad connectors, mobile, production multi-tenancy, autonomous actions, elaborate personalization, and a general-purpose creation studio.

## Kill list

Cut these first if time slips: extra modalities, extra insight families, multiple artifact formats, animated constellation/map, complex auth, integrations, live streaming UX, advanced ranking, and decorative motion. Protect user impact, meaningful Meta model use, temporal source provenance, counter-evidence, the CLI slice, user correction, explicit confirmation, and the three-minute submission video.

## Day-by-day execution

| Day | Date | Focus | Exit criterion |
|---|---|---|---|
| 0 | Mon Oct 26 | Kickoff; capture rules and rubric; prepare repository and synthetic fixtures before formal building | Preparation is clearly separated from event-built product work |
| 1 | Tue Oct 27 | Verify Meta API access; validate raw temporal discovery and memory extraction from the CLI; preregister controlled tests | CLI runs on synthetic archives, returns source-linked evidence, and records controlled results |
| 2 | Wed Oct 28 | Improve temporal-memory quality, provenance, and extraction failure handling | CLI emits dated, source-linked memories from a fresh fixture |
| 3 | Thu Oct 29 | Refine one temporal evolution candidate family and evidence comparison | CLI presents a specific, inspectable evolution hypothesis with supporting and continuity evidence |
| 4 | Fri Oct 30 | Counter-evidence, uncertainty, adversarial cases; attend open-model workshop if useful | Unsupported or generic claims are withheld; evaluation notes recorded |
| 5 | Sat Oct 31 | Improve creator challenge, revision, and disposition flow | Claim can be revised, rejected, deferred, or confirmed from the CLI |
| 6 | Sun Nov 1 | Confirmed-insight artifact gate; stabilize the complete CLI path | Artifact requires explicit confirmation and preserves evidence lineage |
| 7 | Mon Nov 2 | Strengthen the creator-facing CLI experience and demo fixture; reassess whether any visual surface adds enough value | A reliable end-to-end CLI demo works without requiring a frontend |
| 8 | Tue Nov 3 | Demo polish, three-minute video, submission draft | Video and submission draft ready; final questions raised before deadline day |
| 9 | Wed Nov 4 | Final office hours, freeze, verify public repo/video/contributors, submit before 9 PM ET | Submission receipt recorded before cutoff |

## Work sequence

**CLI-first gate:** do not build frontend workflow until the Meta-backed discovery engine can run from the CLI against fixtures and return structured, source-linked results with counter-evidence. The web app can be scaffolded mechanically, but product UI work waits for this gate.

## Current implementation boundary

As of Tue Oct 27, the active product slice is intentionally **CLI-only**, following the creator's direction. The web application is not part of the current build. The CLI now covers raw source → Meta temporal memories → temporal comparison → evidence inspection → creator challenge/revision/rejection/deferral → explicit confirmation → traceable direction note.

The CLI gate is demonstrated on controlled synthetic archives. Do not present synthetic results as proof of real-world reliability. The direct raw-discovery route and project-memory route are separate Meta-backed approaches; keep their evaluations distinct.

## Day 1 progress — Tue Oct 27

- Verified Muse Spark access and ran a raw-only discovery task plus decisive-evidence ablations.
- Added a project-level batch memory extractor so recurring topic tags can be assigned consistently across one archive. Source IDs and dates are copied by local code.
- Added deterministic continuity evidence to distinguish a shift in emphasis from complete replacement.
- Added an interactive CLI creator-review flow with keep/revise/reject/defer outcomes and an exact `CONFIRM` gate before a local direction note is created.
- Ran four controlled synthetic evaluations across raw-discovery and project-memory routes: Neighborhood Atlas failed its wording criterion; Tiny Type Lab direct raw discovery passed; Roomtone batch-memory full/ablation passed; Paper Satellites full passed but its ablation failed by overreading an early pilot. The Paper Satellites preregistration also specified minimal reasoning while the runner used high; this deviation is disclosed. The Type Lab memory-path iteration is exploratory only.
- Latest offline check: 23 unit tests pass; the existing deterministic evaluator matches 6/6 cases. Raw-discovery observations now expose validated evidence-stage labels in CLI output; this is an inspectability improvement, not a validated correction for overclaiming.
- Local token-based spend estimate: about **$0.080430**. This is not the Meta Billing total.
- No public personal data or `.env` secrets are committed; model responses, usage cache, user review sessions, and generated notes remain git-ignored.

See [`DAILY_LOG.md`](DAILY_LOG.md) for the concise day log and experiment links.

## Operating cadence

- Keep a concise daily log of what was built during the event and link it to commits.
- End each day with a runnable state and the next risk.
- Maintain a spend alert and stay within available model credits.
- Cache model extraction by content and prompt version; inspect token usage after each live run. Treat $150 as a hard project budget, with a manual stop well before credits are exhausted.
- Do not include personal data or assets without clear rights and consent.
- Keep at least one full evening for the demo video and submission checks.
