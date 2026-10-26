# Evaluation strategy

## Evaluation objective

Evaluate whether THREAD finds a specific change in a creative project, grounds it in traceable dated artifacts, includes challenging evidence, communicates uncertainty, and responds to creator correction. Fluency alone is not success. Avoid tests that reward personality profiling or generic chat over source documents.

## Fixture tiers

- **Synthetic:** controlled creative-project timelines with known theme/direction evolution and expected supporting evidence.
- **Adversarial:** sparse, ambiguous, contradictory, duplicated, or misdated artifacts; include negative cases where no valid evolution claim exists.
- **Real (optional):** only rights-cleared, voluntarily supplied material. Prefer synthetic for the public demo; never commit private data.

## Stage metrics

- Extraction: source attribution, temporal normalization, and unsupported-detail rate.
- Retrieval: recall and relevance for known project changes; counter-evidence recall.
- Discovery: evidence sufficiency, specificity about the work, usefulness, duplicate rate, and false discovery rate on negative cases.
- Calibration/communication: whether caveats match the evidence; do not claim calibrated probabilities without labeled data.
- Correction: whether user-provided context changes, narrows, or rejects the hypothesis appropriately.
- Artifact: fidelity to the confirmed project insight, source traceability, and no unsupported additions.
- Meta-model contribution: identify which task uses the Meta model and inspect its output on the same fixture; the model must be part of the demonstrated working path.

## Human review rubric

Score the featured candidate 1–5 for evidence support, specificity to the creative work, temporal coherence, usefulness, uncertainty honesty, and responsiveness to counter-evidence. Record failure labels and whether the reviewer would inspect/interview further.

## Minimum evaluation set

Build a small set for clear evolution, false evolution from two unrelated artifacts, missing-date trap, duplicate source, misleading causal leap, and sparse/no-insight case. Each includes the expected claim behavior and known counter-evidence.

## Demo release gate

The selected claim has traceable primary evidence and a plausible counter-reading; the Meta model contributes visibly to the workflow; the CLI returns structured source-linked output; the creator can reject or revise; artifact generation requires explicit confirmation. Preserve a short scorecard and document failures rather than hiding them.
