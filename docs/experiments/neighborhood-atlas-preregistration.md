# Neighborhood Atlas discovery experiment preregistration

**Status:** Preregistered before any Muse inference.

**Purpose:** A controlled test of THREAD's temporal discovery behavior, not evidence of real-world product effectiveness.

**Fixture source:** `datasets/synthetic/creative-evolution.json`; the model input is isolated at `datasets/synthetic/experiments/neighborhood-atlas/raw.json`.

## Hypothesis

Given only dated raw project artifacts, Muse Spark can independently identify an evidence-backed evolution in a creative project's emphasis, preserve continuity with the earlier goal, and withhold that evolution when its decisive evidence is removed.

## Human-reviewed expected finding

> Neighborhood Atlas appears to evolve from primarily helping people navigate the neighborhood toward documenting and communicating residents’ lived stories, while navigation remains an important part of the project.

This is a human-authored answer key. It and all labels, expected answers, theme annotations, memories, and evaluation files are forbidden from model input.

## Dataset boundary

The complete-case input is `datasets/synthetic/experiments/neighborhood-atlas/raw.json`. It includes only the project title and six dated raw artifacts: identifiers, dates, modalities, titles, and content. It excludes the `memories` array, theme labels, expected answers, evaluation cases, and this document.

The ablation input is `datasets/synthetic/experiments/neighborhood-atlas/ablation-no-story-evidence.json`. It contains only artifacts `artifact-001` through `artifact-003`. It removes the entire pre-registered decisive story-evidence set (`artifact-004` through `artifact-006`).

## Decisive evidence set and expected counter-evidence

- Early navigation emphasis: `artifact-001` (2022-03-14), `artifact-002` (2022-08-02), and `artifact-003` (2023-01-19).
- Later lived-story emphasis: `artifact-004` (2024-06-11), `artifact-005` (2025-02-08), and `artifact-006` (2025-11-21).
- Continuity / counter-evidence: `artifact-006` says the prototype retains a route index for visitors. The correct finding must not imply that navigation disappeared.
- Falsification ablation: remove all of `artifact-004`–`artifact-006`. With only the early artifacts, the model must not claim that resident stories became central; it should report insufficient evidence for that shift.

## Fixed model and run protocol

- Provider/model: Meta Model API, Muse Spark 1.3 (`muse-spark-1.3`), Standard mode.
- API: Responses API at `https://api.meta.ai/v1/responses`.
- Reasoning effort: `high`.
- Maximum output budget: 4096 tokens (including reasoning tokens).
- One inference for the complete case and one for the ablation. No prompt retries or manual steering; retry only a transport/API failure and record it. Save the exact request, response, model ID, timestamp, and usage metadata under ignored `.thread-experiment-runs/`. Never save API keys.
- Present artifacts in chronological order with their original IDs, dates, modality, title, and content.

### Exact prompt for both runs

> Review this dated archive of one creative project. Identify any meaningful evolution in the project's focus over time. If the evidence is insufficient, say so. Separate direct observations from your interpretation. Cite artifact IDs and dates for each part of your interpretation. Include evidence that complicates your interpretation. Do not infer the creator's personality or invent causes. Return concise JSON with keys `observations`, `candidate_finding`, `supporting_artifacts`, `complicating_artifacts`, and `limitations`. Use an empty `candidate_finding` when no evolution is established.

## Pre-registered scoring

Score each criterion as pass/fail from the saved response; do not alter criteria after seeing output.

### Complete case

A complete-case pass requires all of the following:

1. **Independent direction:** Candidate describes the evolution from navigation as the primary practical purpose toward resident stories becoming increasingly central, while navigation continues to matter. A bare list of both themes is insufficient.
2. **Temporal synthesis:** It distinguishes early evidence (`artifact-001`–`003`) from later evidence (`artifact-004`–`006`) and does not claim a more precise transition date than the artifacts support.
3. **Traceability:** It cites at least two distinct early artifacts and at least two distinct later artifacts, accurately tied to their dates and content.
4. **Continuity:** It cites `artifact-006` as evidence that navigation remains part of the project; it does not describe a total replacement.
5. **Epistemic restraint:** It uses qualified language such as “appears,” separates source observations from interpretation, and makes no unsupported causal or personality claim.

### Ablation control

An ablation pass requires that, with only `artifact-001`–`003`, the response does **not** assert a shift toward resident storytelling. It should describe the available navigation evidence and state that the archive does not establish the later direction.

### Overall result

- **PASS (controlled capability only):** every complete-case criterion and the ablation criterion pass.
- **FAIL:** any required criterion fails, the expected conclusion appears in the ablation response, or the model cannot provide artifact-level evidence.
- **INCONCLUSIVE:** API failure after one retry, malformed/unusable output, or an execution/input leak. Inconclusive is not a pass.

No confidence percentage will be reported. This one fictional fixture tests a known pattern and is not a measure of performance on real creator archives or proof that the product works in the wild.

## Contamination controls

Before each call, construct the request from the isolated raw JSON only. Verify that the top-level input keys are exactly `project` and `artifacts`, and each artifact has only `id`, `date`, `modality`, `title`, and `content`. This structural check avoids false alarms when ordinary source text contains words that also appear in the answer key. Keep the prompt generic and do not include this preregistration or its expected-finding sentence. Do not send repository history, the original labeled fixture, or evaluation files. Record a hash of the exact input sent.

## Interpretation boundary

A pass supports only this narrow statement: *Muse can discover this pre-labeled temporal emphasis shift from the raw synthetic artifacts and withhold it under the specified evidence ablation.* It does not establish general discovery quality, real-world transfer, autonomous ongoing monitoring, user value, or product direction. A later test with consented, independently labeled real material would be needed for transfer evidence.

## References

- [Meta Model API quickstart](https://dev.meta.ai/docs/quickstart)
- [Muse Spark model documentation](https://dev.meta.ai/docs/models)
