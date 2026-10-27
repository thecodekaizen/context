# Inspect current status

Snapshot: October 28, 2026. Inspect source and Git before acting; this is not a live task database.

| Area | Implemented | Remaining |
| --- | --- | --- |
| Teach | Video capture/upload, optional PDF, evidence-linked extraction, review, local model persistence, inspect state claims | Better claim correction/rejection workflow and source review UX |
| Do | Camera preview, manual frame checks, video comparison, timestamp inspection, report import/export, checkpoint guidance | Complete active-task/recovery UX; continuous observation not implemented |
| Grounding | Opt-in SAM still-frame mask/box integration | Relevant LEGO segmentation not validated |
| Simulate | Shared model, bounded local order interpretation, deterministic replay, play/pause/step, reference comparison | Task geometry, visual arrangement transitions, useful supported recovery visualization |
| Backend | Structured output validation, recovery chronology/object guards, optional PDF on Observe | Real-world accuracy and matched evaluation |
| Submission | README and earlier screenshots | Updated screenshots, clean-start demo, reproducibility and public-repo release |

## Evidence, not optimism

A detached-wing/reattached-wing clip produced an exploratory restoration signal. It does not prove detection of an incorrectly attached orientation. The v4 follow-up produced questionable geometry and a response rejected by timestamp validation. Its candidate is not approved. Latest v5 source-reference support has local software tests, no new model accuracy result.

Two agents delivered local changes before this handoff: checkpoint guidance in Do and optional source PDF for Observe. Reported checks: 29 web tests/typecheck and 65 backend tests passed. Integration lead must review their diffs before treating these as merged/released.

Private raw runs live in ignored `.showme-runs/`; never commit them. Detailed records: `../experiments/results/showme-orientation-v4-2026-10-27.md` and `../experiments/showme-reference-comparison-v5.md`.
