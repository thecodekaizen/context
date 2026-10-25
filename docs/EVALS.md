# Evaluation strategy

## Evaluation objective

Evaluate whether THREAD discovers specific, useful interpretations that are supported by traceable evidence, handles uncertainty and contradiction honestly, and incorporates user judgment. Fluency alone is not success.

## Dataset tiers

- **Synthetic:** controlled timelines with known patterns, contradictions, and evolution; use for repeatable checks and edge cases.
- **Adversarial:** deliberately ambiguous, sparse, contradictory, misdated, duplicated, or tempting-to-overclaim material. Include negative examples with no valid insight.
- **Real (optional):** only voluntarily supplied and consented material; minimize scope, redact where possible, and never check it into git.

## Stage metrics

- Extraction: source attribution accuracy, temporal normalization accuracy, unsupported-detail rate.
- Retrieval: evidence recall and relevance for known target patterns; counter-evidence recall.
- Discovery: evidence sufficiency, specificity, usefulness, novelty, duplicate rate, and false discovery rate on negative cases.
- Calibration/communication: confidence ordering and whether caveats match evidence. Do not claim calibrated probability without enough labeled cases.
- Interview: grounding, non-leading wording, acceptance of correction, and explicit confirmation state.
- Artifact: fidelity to confirmed insight, source traceability, and no unsupported additions.

## Human review rubric

For each surfaced candidate, reviewers score 1–5: (1) evidence support, (2) specificity, (3) temporal coherence, (4) usefulness/surprise, (5) uncertainty honesty, and (6) respectfulness. Record major failure labels and whether the reviewer would inspect/interview further.

## Minimum Day-0 evaluation set

Prepare small, inspectable fixtures: clear recurrence, genuine evolution, apparent contradiction explained by context, cross-domain motif, sparse-data no-insight case, misleading coincidence, date-order trap, duplicate sources, and an unsupported causal leap trap. Each includes expected evidence and known counter-evidence.

## Release gate for demo

The chosen hero insight must have traceable primary evidence and a plausible counter-reading; the CLI must return source-linked structured output; the interview must allow rejection/revision; generation must require explicit confirmation. Keep a short manual scorecard and document failures rather than hiding them.
