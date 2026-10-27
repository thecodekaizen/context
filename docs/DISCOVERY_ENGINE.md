# Discovery engine specification

> **Archived THREAD discovery spec:** the active SHOWME problem is learning a process from a demonstration and observing another attempt. See [`SHOWME_PROOF_OF_MAGIC.md`](SHOWME_PROOF_OF_MAGIC.md). Do not use this creative-project discovery spec as a SHOWME requirement.

## Goal

Find one useful, evidence-backed hypothesis about how a creative project changes over time. The creator must be able to inspect its source material and decide whether the interpretation fits. The hackathon prototype is about the work, not profiling the creator.

## Primary candidate: evolution in a project

Trace how a theme, constraint, visual motif, or direction changes across dated artifacts from one project. Each candidate is a falsifiable hypothesis with a time span, supporting evidence, counter-evidence where found, and uncertainty. Do not infer personality, psychological traits, or unsupported causes.

A second family (such as cross-project motif or a genuine contradiction) is P1 only after the evolution path works end to end.

## Pipeline

1. Validate dated source metadata and build an explicit raw-only project archive.
2. Ask Muse to identify one possible evolution from the whole dated archive, not from hand-assigned theme labels.
3. Return observations separately from the candidate interpretation. Each observation labels the source's evidence stage as planned, experimental, ongoing, released, or unclear. Require supporting and complicating artifact references.
4. Validate response shape, evidence-stage values, artifact IDs, dates, and minimum temporal support locally. Reject fabricated references. The stage is a model classification of source status, not ground truth or a calibrated confidence score; the CLI displays it for human inspection. Incomplete or failed API status/reason is reported and cached so retrying does not spend again. In the temporal-memory route, copy source metadata locally and expose persistent topics separately from candidate-shift evidence.
5. Withhold a non-empty finding if it lacks explicit tentative wording; label accepted candidates as unconfirmed and preserve model-stated limitations. This lexical gate catches overconfident phrasing but does not calibrate the model's uncertainty.
6. Let the creator inspect, challenge, revise, reject, or confirm it before producing an artifact.

Two model-backed CLI paths are available for comparison: `--extract-memories` exposes source-linked memory extraction without a discovery step; `--provider meta` combines extraction with deterministic temporal theme comparison; and `--raw-muse` asks Muse to form and evidence a candidate directly from the raw archive. Persistent storage, broad retrieval, and multiple candidate families remain later work; they must not be represented as already implemented.

## Evidence rules

- An evolution claim needs supporting citations anchored in both the earliest and latest chronological quarters of the dated archive; a middle-stage experiment cannot substitute for the starting direction. A single source may support only a clearly labeled observation. This deterministic guard is a heuristic, not a learned change-point model, and requires independent evaluation.
- Distinguish source content from model interpretation. Link each statement to the original item or span.
- Do not infer sensitive traits, diagnose, or claim why the creator changed unless sources establish that explanation.
- Preserve ambiguity, missing dates, and contradictory evidence; do not resolve them by averaging.
- Keep a proposal, rehearsal, prototype, or pilot distinct from ongoing practice and a released work. Do not describe an experiment as an adopted project direction unless later evidence supports that interpretation.
- A score ranks candidates; it is not a calibrated probability unless calibration is demonstrated.
- The Meta model contributes to the working project path. Application logic validates typed outputs and provenance; model prose alone is never evidence.

## CLI-first contract

The engine runs without the web app. `thread-discover <dataset> --extract-memories --json` prints Muse-produced dated memories whose source provenance is copied locally. `thread-discover <dataset> --provider meta --json` runs extraction and deterministic temporal comparison on raw-only datasets. `thread-discover <dataset> --raw-muse --json` directly asks Muse Spark for a hypothesis and validates structured output and source references locally. `thread-discover <dataset> --raw-muse --review` carries that validated raw finding into the interview, disposition, exact-confirmation, and direction-note flow while retaining observed source stages and provenance. Empty candidates skip the interview. Fixture mode remains deterministic for local development.

## Initial scoring hypothesis

Use a transparent rubric rather than one opaque model score: distinct source support, temporal spread, source quality, claim specificity, and counter-evidence handling. Tune against the small synthetic/adversarial set. Do not present the result as statistically calibrated.

## Failure modes to test

Generic insights, unsupported causality, cherry-picked evidence, missed counter-evidence, chronology errors, duplicate candidates, model hallucinations, and a correction that fails to change the interpretation.
