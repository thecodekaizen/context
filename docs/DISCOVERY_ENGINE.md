# Discovery engine specification

## Goal

Find one useful, evidence-backed hypothesis about how a creative project changes over time. The creator must be able to inspect its source material and decide whether the interpretation fits. The hackathon prototype is about the work, not profiling the creator.

## Primary candidate: evolution in a project

Trace how a theme, constraint, visual motif, or direction changes across dated artifacts from one project. Each candidate is a falsifiable hypothesis with a time span, supporting evidence, counter-evidence where found, and uncertainty. Do not infer personality, psychological traits, or unsupported causes.

A second family (such as cross-project motif or a genuine contradiction) is P1 only after the evolution path works end to end.

## Pipeline

1. Validate dated source metadata and build an explicit raw-only project archive.
2. Ask Muse to identify one possible evolution from the whole dated archive, not from hand-assigned theme labels.
3. Return observations separately from the candidate interpretation. Require supporting and complicating artifact references.
4. Validate response shape, artifact IDs, dates, and minimum temporal support locally. Reject fabricated references.
5. Withhold a non-empty finding if it lacks explicit tentative wording; label accepted candidates as unconfirmed and preserve model-stated limitations. This lexical gate catches overconfident phrasing but does not calibrate the model's uncertainty.
6. Let the creator inspect, challenge, revise, reject, or confirm it before producing an artifact.

The raw archive path is the current CLI vertical slice. Persistent temporal memories, broad retrieval, and multiple candidate families remain later work; they must not be represented as already implemented.

## Evidence rules

- An evolution claim needs at least two distinct dated source moments; a single source may support only a clearly labeled observation.
- Distinguish source content from model interpretation. Link each statement to the original item or span.
- Do not infer sensitive traits, diagnose, or claim why the creator changed unless sources establish that explanation.
- Preserve ambiguity, missing dates, and contradictory evidence; do not resolve them by averaging.
- A score ranks candidates; it is not a calibrated probability unless calibration is demonstrated.
- The Meta model contributes to the working project path. Application logic validates typed outputs and provenance; model prose alone is never evidence.

## CLI-first contract

The engine runs without the web app. `thread-discover <dataset> --raw-muse --json` sends raw dated artifacts to Muse Spark, validates structured output and source references locally, and returns an explicitly unconfirmed finding. The fixture mode remains deterministic for local development. The previous `--provider meta` per-artifact theme extraction path is retained for comparison only.

## Initial scoring hypothesis

Use a transparent rubric rather than one opaque model score: distinct source support, temporal spread, source quality, claim specificity, and counter-evidence handling. Tune against the small synthetic/adversarial set. Do not present the result as statistically calibrated.

## Failure modes to test

Generic insights, unsupported causality, cherry-picked evidence, missed counter-evidence, chronology errors, duplicate candidates, model hallucinations, and a correction that fails to change the interpretation.
