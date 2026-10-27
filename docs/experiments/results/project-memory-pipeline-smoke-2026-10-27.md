# Project memory pipeline smoke test

**Date:** 2026-10-27  
**Status:** Exploratory engineering check; not preregistered or scored.  
**Input:** The raw-only Tiny Type Lab archive.  
**Model:** `muse-spark-1.3` Standard, Responses API structured output.

## What worked

- One bounded project-level request returned exactly six memories, one per raw artifact.
- The application copied source IDs, dates, modalities, and titles from the archive. Muse supplied only summaries and topic tags.
- The batch output used stable tags across the archive: `developer tools` early, `text readability` later, and `code readability` throughout.
- The deterministic comparison produced the candidate “Across this project, emphasis appears to move from 'developer tools' toward 'text readability' in the dated artifacts.”
- Continuity evidence separately links `code readability` to later artifacts `type-004`, `type-005`, and `type-006`.
- A second CLI run loaded the memory cache and made zero API requests.

## Iteration history and limits

An initial per-artifact request hit its 256-token output cap before returning content. The output cap was raised, and six per-artifact extractions completed, but their open-vocabulary tags were inconsistent and the exact-tag temporal comparison withheld a finding. This motivated the current one-request-per-project design, where the model can use a shared topic vocabulary across dates.

The final batch request used 567 input tokens and 763 output tokens, with a local estimated cost of **$0.003952**. Total recorded estimated spend across this project’s Meta calls is about **$0.051904**. Billing may differ; the estimate is a local token calculation.

Because the extraction approach was changed after inspecting outputs on this synthetic archive, this smoke result is not independent evaluation evidence. It demonstrates only that the current CLI path can create source-linked memories and feed them to the comparison. The direct raw-discovery benchmark scorecards remain separate and unchanged.

Full output is local under `.thread-experiment-runs/type-foundry/20261027/` and is git-ignored.
