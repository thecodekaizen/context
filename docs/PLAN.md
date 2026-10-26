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
| 0 | Mon Oct 26 | Kickoff; capture rules and rubric; claim credits when form is available; build the CLI slice, local workflow API, and first user-facing investigation flow on synthetic data | Browser flow demonstrates discover → inspect → challenge → confirm → create; API enforces confirmation; fixture CLI still produces source-linked evidence and counter-evidence |
| 1 | Tue Oct 27 | Verify Meta API access; run the first Muse Spark extraction; define source format and typed memory contract | One Meta-backed task runs on a rights-safe fixture, or a documented access blocker with an approved open-weight fallback |
| 2 | Wed Oct 28 | Refine source and temporal-memory model; provenance; extraction quality | CLI emits dated, source-linked memories from the actual model path |
| 3 | Thu Oct 29 | Temporal analysis and one candidate family | CLI emits one specific evolution hypothesis with evidence references |
| 4 | Fri Oct 30 | Counter-evidence, uncertainty, adversarial cases; attend open-model workshop if useful | Unsupported or generic claims are withheld; evaluation notes recorded |
| 5 | Sat Oct 31 | Challenge/revision state and explicit user disposition | Claim can be revised, rejected, deferred, or confirmed |
| 6 | Sun Nov 1 | Confirmed-insight artifact gate; stabilize backend CLI path | Artifact requires confirmed insight and preserves evidence lineage |
| 7 | Mon Nov 2 | Minimal web experience on top of the CLI/backend contract | Discover → inspect → challenge → confirm → artifact works end to end |
| 8 | Tue Nov 3 | Demo polish, three-minute video, accessibility/error states, submission draft | Video and submission draft ready; final questions raised before deadline day |
| 9 | Wed Nov 4 | Final office hours, freeze, verify public repo/video/contributors, submit before 9 PM ET | Submission receipt recorded before cutoff |

## Work sequence

**CLI-first gate:** do not build frontend workflow until the Meta-backed discovery engine can run from the CLI against fixtures and return structured, source-linked results with counter-evidence. The web app can be scaffolded mechanically, but product UI work waits for this gate.

## Operating cadence

- Keep a concise daily log of what was built during the event and link it to commits.
- End each day with a runnable state and the next risk.
- Maintain a spend alert and stay within available model credits.
- Cache model extraction by content and prompt version; inspect token usage after each live run. Treat $150 as a hard project budget, with a manual stop well before credits are exhausted.
- Do not include personal data or assets without clear rights and consent.
- Keep at least one full evening for the demo video and submission checks.
