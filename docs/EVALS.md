# Evaluation strategy

## Hackathon judging alignment

The live kickoff rubric weights impact 30%, Meta AI tooling 25%, technical depth 20%, and demo 25%. Stage 1 is pass/fail on theme fit and reasonable Meta-model use. Therefore, verify that THREAD solves a clear creative-work problem, uses the Meta model for a substantive multimodal/temporal step rather than a token API call, has a technically credible evidence-and-counter-evidence pipeline, and tells the story in a three-minute demo.

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
- Meta-model contribution: Muse Spark receives raw dated artifacts and proposes a temporal finding; deterministic application code checks that its evidence IDs and dates exist and that a claim spans distinct dates. Do not pass hand-authored themes or expected answers into the request. Record model ID/provider and cost. Keep the finding explicitly unconfirmed until creator disposition.

## Human review rubric

Score the featured candidate 1–5 for evidence support, specificity to the creative work, temporal coherence, usefulness, uncertainty honesty, and responsiveness to counter-evidence. Record failure labels and whether the reviewer would inspect/interview further.

## Minimum evaluation set

Build a small set for clear evolution, false evolution from two unrelated artifacts, missing-date trap, duplicate source, misleading causal leap, and sparse/no-insight case. Each includes the expected claim behavior and known counter-evidence.

## Seed-data baseline

Run `python -m thread_engine.evaluate` from `backend/` to compare fixture discovery with the labeled cases in `datasets/synthetic/evaluation-cases.json`. The current set covers a clear shift with counter-evidence, a stable project, mixed project IDs, a genuine shift whose vocabulary changes, an impossible calendar date, and duplicate source provenance. Mixed projects, malformed dates, and duplicate sources are rejected during dataset loading with stable error codes; a valid archive with no candidate remains a normal “no finding” outcome. The vocabulary-change seed confirms that project assignment—not shared words—defines the comparison boundary. This relies on trustworthy project IDs, so a future importer must avoid grouping unrelated sources under one project. Add new cases with expected behavior before changing the algorithm, so the same archive can reveal regressions.

## Demo release gate

The selected claim has traceable primary evidence and a plausible counter-reading; the Meta model contributes visibly to the workflow; the CLI returns structured source-linked output; the creator can reject or revise; artifact generation requires explicit confirmation. Preserve a short scorecard and document failures rather than hiding them.

## Raw Muse discovery experiment

The preregistered Neighborhood Atlas experiment used Muse Spark 1.3 Standard over raw artifacts and a decisive-evidence ablation. The complete case recovered the expected direction and the ablation withheld it, but the full result failed the preregistered language-calibration criterion because the model stated the interpretation as settled (`shifted`) rather than tentative. See [the scorecard](experiments/results/neighborhood-atlas-2026-10-27.md). Do not count the deterministic fixture baseline or this one synthetic result as real-world validation.

The CLI now withholds non-empty candidates that lack explicit tentative wording. This is a deterministic lexical guard added in response to the failure; it does not change the scorecard, prove calibration, or establish that a qualified claim is factually sound. Evaluate it separately on new cases before treating it as effective.
