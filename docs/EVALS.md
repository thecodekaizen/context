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

The preregistered Neighborhood Atlas experiment used Muse Spark 1.3 Standard over raw artifacts and a decisive-evidence ablation. The complete case recovered the expected direction and the ablation withheld it, but the full result failed the preregistered language-calibration criterion because the model stated the interpretation as settled (`shifted`) rather than tentative. See [the scorecard](experiments/results/neighborhood-atlas-2026-10-27.md).

A second, separately preregistered Tiny Type Lab archive passed its five full-case criteria, and its code-only ablation correctly withheld the evolution. See [that scorecard](experiments/results/type-foundry-2026-10-27.md). Together these are one synthetic fail and one synthetic pass—not evidence of real-world reliability or general transfer.

The CLI now withholds non-empty candidates that lack explicit tentative wording. This is a deterministic lexical guard added in response to the failure; it does not change the scorecard, prove calibration, or establish that a qualified claim is factually sound. Evaluate it separately on new cases before treating it as effective.

The separate project-level memory extraction path has an [exploratory smoke report](experiments/results/project-memory-pipeline-smoke-2026-10-27.md). Its extraction prompt was iterated on the same synthetic archive, so that result demonstrates the code path only and is not independent validation.

The final batch-memory path then passed a separate preregistered Roomtone full/ablation test; see [that scorecard](experiments/results/roomtone-memory-2026-10-27.md). This is a second synthetic domain case for memory extraction, not evidence of real-world reliability or repeatability.

The separately preregistered Paper Satellites raw-discovery full case passed, but the ablation failed: Muse promoted a rehearsal and two-voice pilot into an apparent project-level evolution despite the absence of later ensemble evidence. The preregistration also specified minimal reasoning while the runner used high. Both limitations are recorded in [the scorecard](experiments/results/paper-satellites-2026-10-27.md). The raw-observation contract now exposes source evidence stages (`planned`, `experimental`, `ongoing`, `released`, `unclear`) so this distinction is inspectable; these model-assigned labels are not ground truth and have not yet been validated as a fix.

A later Cook's Margin case returned the expected planned/experimental/released labels on the complete archive. Its ablation call returned invalid JSON at the 4,096-token output cap, so whether the stage distinction prevents overclaiming is **inconclusive**; see [the scorecard](experiments/results/cooks-margin-2026-10-27.md). No retry was made.

The Repair Margins run used minimal reasoning. Its ablation appropriately withheld a completed-guide claim when only experiments and a proposal remained, but the full finding failed temporal support because the supporting-evidence list omitted the early personal-work sources. Both responses completed below the output cap. This differs from Cook's Margin, but the fixtures also differ, so it does not isolate reasoning effort as the cause; see [the scorecard](experiments/results/repair-margins-2026-10-27.md).

In response, local raw-discovery validation first required support citations from both halves of the archive. Cached Repair Margins responses showed that later-only support could be withheld, but the preregistered Pocket Observatory check then failed: the full result omitted map continuity, and the ablation produced a candidate from experiments and a proposal. The midpoint gate admitted it because the third of five sources counted as early. The gate now requires anchors in the earliest and latest chronological quarters. A cached replay allowed Pocket Observatory's full candidate and withheld its ablation, but this is only a regression check against the motivating failure, not independent validation. See [the scorecard](experiments/results/pocket-observatory-2026-10-27.md).
