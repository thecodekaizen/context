# 10-day hackathon plan

**Dates:** Monday, Oct 26 through Wednesday, Nov 4, 2026 (inclusive). Confirm official submission/demo deadlines and time zone on Day 1. Plan for a working vertical slice by Nov 1 and reserve Nov 2–4 for reliability, demo polish, and submission.

## Scope

### P0 — must work

- One bounded, user-provided or synthetic multimodal archive path (start with the modalities the Meta Model API spike confirms).
- Temporal memory records with source provenance.
- CLI discovery for at least two candidate families, evidence links, counter-evidence, and uncertainty.
- One human review/interview path with confirm, revise, reject.
- One artifact type gated on confirmed insight.
- Minimal Next.js flow: discover → inspect timeline/evidence → interview → confirm → artifact.
- Deterministic fixtures, evaluation scorecard, and demo fallback.

### P1 — only after P0 works

- Additional candidate families and stronger deduplication.
- Better visual timeline/connection map, richer filtering, another artifact type.
- More than one supported input modality, based on API and time feasibility.

### P2 — explicitly out of scope unless all P0 is stable

- Continuous sync, broad connectors, social graph or collaborative features.
- Mobile app, accounts/permissions infrastructure, production multi-tenancy.
- General-purpose agent, autonomous actions, arbitrary artifact studio.
- Exhaustive multimodal ingestion, fine-tuning, elaborate personalization.

## Kill list

Cut these first if schedule slips: extra modalities, extra insight families, multiple artifact formats, animated constellation/map, complex auth, broad import integrations, streaming/live model UX, advanced ranking, and decorative motion. Protect provenance, counter-evidence, the CLI vertical slice, user correction, explicit confirmation, and one complete artifact path.

## Day-by-day execution

| Day | Date | Focus | Exit criterion |
|---|---|---|---|
| 1 | Mon Oct 26 | Repo and environment check; verify Meta Model API modalities/access; define contracts; synthetic fixtures; CLI spike | One fixture passes through extraction/discovery CLI; risks and confirmed model capabilities documented |
| 2 | Tue Oct 27 | Source/memory schema; ingestion and provenance | Imported fixture yields inspectable, source-linked temporal memories |
| 3 | Wed Oct 28 | Retrieval and candidate generation | CLI returns candidates for recurrence/evolution with evidence references |
| 4 | Thu Oct 29 | Counter-evidence, scoring, dedup, adversarial fixtures | Weak/unsupported candidates are withheld; scorecard run and failures logged |
| 5 | Fri Oct 30 | Investigation and interview state | User can challenge, revise, reject, or confirm; state is persisted |
| 6 | Sat Oct 31 | Artifact gate and backend vertical slice | Artifact generation requires confirmed insight and preserves lineage |
| 7 | Sun Nov 1 | Minimal Next.js workflow wired to backend/fixtures | Full P0 flow works end-to-end once; no frontend precedes CLI proof |
| 8 | Mon Nov 2 | Visual polish from mockups; accessibility and empty/error states | Readable evidence timeline and clear uncertainty/correction interaction |
| 9 | Tue Nov 3 | Regression, demo script, fallback recording, rehearsal | Demo completes repeatedly; fallback and model-failure behavior verified |
| 10 | Wed Nov 4 | Final freeze, submission, final rehearsal | Submitted on time; stable demo build and concise project narrative ready |

## Work sequence

**CLI-first gate:** do not build frontend workflows until the discovery engine can run from the CLI against fixtures and return source-linked structured results. The web app may be scaffolded lightly, but product UI work waits for this gate.

## Operating cadence

- End each day with a runnable commit, a short decision log, and a named next risk.
- Keep a 30-minute schedule buffer each day.
- Make one person responsible for demo data provenance and final narrative.
- Verify actual event requirements and API terms early; adjust scope from evidence.
