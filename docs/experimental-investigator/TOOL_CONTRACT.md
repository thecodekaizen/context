# Shared investigation tools

The direct Meta policy, investigator policy and conventional controller can use the same `InvestigationTools` instance bound to one persisted session. These are bounded structured operations, not shell execution or a general agent framework. Existing guarded Meta transport is reused by `decide_with_tools`; no live calls were made during integration.

## Public context

Observed input/temperature traces and metadata are copied through an explicit allowlist. Registered executable models, parent/evidence references, completed numerical fits, observed assessments, previous decisions, legal schedules and remaining budgets are visible. Hidden simulator parameters, future measurements, evaluator labels and arbitrary observation fields are omitted. The context hash identifies the exact evidence snapshot; stale decisions are rejected.

## Operations

| Operation | Effect | Constraints |
|---|---|---|
| fit_candidate | Fit linear, sensor-delay or quadratic-loss family | Known observation IDs, persisted fitting cap, constrained optimizer, no arbitrary code |
| register_revision | Register a fitted candidate as a child of an existing model | Must preserve fitting evidence and cite a measured parent mismatch; core store enforces parent linkage |
| propose_experiment | Return a registered-model/schedule proposal | Legal schedule, available action budget, no unresolved dispatched/prepared action; does not execute |
| stop | Return stop request to controller | Controller must honor it; tool does not itself dispatch or disable unrelated callers |

All fields are explicit and operation-specific unused fields must be null. Explanations cite observed evidence and remain bounded to 2,000 characters. Fits expose training error and explicitly say they are not independently confirmed.

## Persistence and budgets

Fits are content-addressed by family and observed traces. Repeating a completed fit reads the stored result. Reserved/failed fits cannot be retried automatically; each reservation consumes the fitting cap, which cannot be raised by reopening the session. This cap bounds requested solver work, not wall-clock duration. Experiments use the separate action reservation and frozen prediction machinery in `Investigation`.

Decisions have stable IDs and completed decisions replay from storage. A proposal cannot consume a physical action; the controller must explicitly prepare and dispatch it. Unknown external outcomes remain subject to the existing reconciliation rule. Candidate registration and decision recording are separate transactions; interruption between them requires reconciliation rather than claiming atomic exactly-once completion.

## Meta integration and fairness

`MetaDecider.decide_contract` shares the existing persistent call/cost guard, strict JSON response parsing, local validator, response cache and no-retry policy. Legacy ARX decisions still use their original contract. Both new Meta policies receive the same context and schema. Only the investigation instructions differ. This policy distinction does not itself establish novelty or scientific benefit.

Seven added local checks cover hidden-field exclusion, restarted fit caching, immutable caps, invalid/stale decisions, proposals without dispatch, mismatch-linked registration, mocked provider response/cache, and fitting-budget exhaustion. The full suite has 60 tests. Provider transport was mocked; no live capability or accuracy claim follows.

## Next controller milestone

Wire decision → validated tool result → refreshed context into a bounded loop. Honor stop requests, preserve pending outcomes and limit decision/tool steps independently of provider calls. Freeze a direct/investigator/conventional comparison before a paid batch. Keep the matched model library and experimental budget; numerical model selection remains the strongest demonstrated baseline.
