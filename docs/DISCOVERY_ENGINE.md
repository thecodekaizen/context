# Discovery engine specification

## Goal

Find one useful, evidence-backed hypothesis about how a creative project changes over time. The creator must be able to inspect its source material and decide whether the interpretation fits. The hackathon prototype is about the work, not profiling the creator.

## Primary candidate: evolution in a project

Trace how a theme, constraint, visual motif, or direction changes across dated artifacts from one project. Each candidate is a falsifiable hypothesis with a time span, supporting evidence, counter-evidence where found, and uncertainty. Do not infer personality, psychological traits, or unsupported causes.

A second family (such as cross-project motif or a genuine contradiction) is P1 only after the evolution path works end to end.

## Pipeline

1. Normalize source metadata and extract bounded, source-linked temporal memories.
2. Partition and retrieve by project, time, topic, entities, modality, and semantic similarity.
3. Generate one candidate hypothesis from retrieved memories using typed output.
4. Retrieve additional supporting evidence and deliberately search for counter-evidence.
5. Score evidence quality, temporal coverage, specificity, and counter-evidence transparently.
6. Withhold generic, weak, or redundant candidates.
7. Return candidate text, dates, evidence references, uncertainty, counter-evidence, and an investigation prompt.

## Evidence rules

- An evolution claim needs at least two distinct dated source moments; a single source may support only a clearly labeled observation.
- Distinguish source content from model interpretation. Link each statement to the original item or span.
- Do not infer sensitive traits, diagnose, or claim why the creator changed unless sources establish that explanation.
- Preserve ambiguity, missing dates, and contradictory evidence; do not resolve them by averaging.
- A score ranks candidates; it is not a calibrated probability unless calibration is demonstrated.
- The Meta model contributes to the working project path. Application logic validates typed outputs and provenance; model prose alone is never evidence.

## CLI-first contract

The engine must run without the web app: load a synthetic fixture, call the configured Meta model task, run discovery, and emit inspectable structured results (JSON plus concise human-readable output). Record model/provider version and source IDs. Support deterministic fixture mode for evaluation and fallback. Choose the exact command and flags after checking the current Meta API quickstart.

## Initial scoring hypothesis

Use a transparent rubric rather than one opaque model score: distinct source support, temporal spread, source quality, claim specificity, and counter-evidence handling. Tune against the small synthetic/adversarial set. Do not present the result as statistically calibrated.

## Failure modes to test

Generic insights, unsupported causality, cherry-picked evidence, missed counter-evidence, chronology errors, duplicate candidates, model hallucinations, and a correction that fails to change the interpretation.
