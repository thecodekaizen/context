# Coordinate implementation

| Owner | Files and responsibility |
| --- | --- |
| Antigravity | `apps/web/`, product interaction, visual scene, accessible UI, frontend tests; assigned design documents/assets |
| Codex | `backend/showme/`, backend tests, model adapters/prompts, evaluation and perception evidence |
| Integration lead | Shared contracts, root docs, source review, explicit staging, commits/push and submission claims |

## Before editing

Inspect Git status. Do not reset, overwrite or stage another agent's changes. In a shared checkout, separate file ownership is essential. Only the integration lead performs Git commits while agents are editing. An externally configured separate checkout may exchange reviewed commits instead; do not assume it exists.

Frontend types and Python process JSON are separate representations joined by `process-to-skill.ts`. Propose contract changes with fields, optionality, provenance, migration and tests before either side changes them. Do not invent backend endpoints to unblock a mockup.

Frontend work may use explicitly illustrative fixtures. Do not alter experiment ground truth, prompts, models or thresholds to fit the UI. Do not upload private videos or make paid calls as part of visual QA.

Report: changed files; implemented behavior; checks actually run; unsupported states; contract requests. Product work continues when perception is blocked. Capability claims remain gated on validation.
