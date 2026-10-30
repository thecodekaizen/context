# Meta AI Tooling: Ablation Study & Empirical Lift Report

**Run ID:** `20261029T184520Z-cb6473`  
**Date:** October 29, 2026 18:52:58 UTC  
**Evaluation Purpose:** Quantify the exact empirical contribution of Meta Muse Spark 1.2 and 1.3 over deterministic algorithms and closed-book baselines.

## Summary Matrix: Architectural Tier Comparison

| Capability / Dimension | Tier 1: Deterministic Baseline | Tier 2: Closed-Book Multimodal | Tier 3: Full CONTEXT Pipeline |
|---|---|---|---|
| **Temporal Sequence Alignment** | **Supported** (4Hz visual distance + 2kHz FFT audio) | Not evaluated | **Supported** (inherited deterministic engine) |
| **Edit Boundary Detection** | **Supported** (cut timecodes measured) | Unsupported | **Supported** (modalities separated) |
| **Audiovisual Scene Understanding** | Unsupported (pixel numbers only) | **Supported** (`muse-spark-1.2`) | **Supported** (`muse-spark-1.2`) |
| **Spoken Speech & Claim Extraction** | Unsupported | **Supported** | **Supported** |
| **Factual Claim Verification** | Unsupported | **Withheld** (0 citations; strict guard prevents hallucination) | **Supported** (`muse-spark-1.3` live search + exact citations) |
| **Harmless vs Deceptive Edit Discrimination** | Unsupported (treats all cuts identically) | Unsupported (no external evidence) | **Supported** (identifies removed qualifications vs routine cuts) |
| **False Accusation on Routine Edits** | **High Risk** (labels cuts without understanding) | None (no verdicts returned) | **Low / Guarded** (classifies harmless shortening) |

## Case-by-Case Breakdown

### Case: `case_1_honest_qualification` (honest_shortening)
- **Tier 1 (Deterministic):** Matched source `NASA Artemis I Mission Journey (Official Reference)`, visual coverage 67.5%, detected 2 omissions. *Limitation:* Extracted 0 claims and cannot verify caption.
- **Tier 2 (Closed-Book):** Extracted 1 claims. *Limitation:* Without external document search, citation guard forced verdict to inconclusive (0 citations verified).
- **Tier 3 (Full CONTEXT):** Retrieved 8 primary sources, verified 4 citations, caption verdict: `inconclusive`, semantic classifications: `['harmless_edit', 'inconclusive']`.

### Case: `case_2_captioned_omission` (deceptive_omission_with_false_caption)
- **Tier 1 (Deterministic):** Matched source `NASA Artemis I Mission Journey (Official Reference)`, visual coverage 86.3%, detected 0 omissions. *Limitation:* Extracted 0 claims and cannot verify caption.
- **Tier 2 (Closed-Book):** Extracted 1 claims. *Limitation:* Without external document search, citation guard forced verdict to inconclusive (0 citations verified).
- **Tier 3 (Full CONTEXT):** Retrieved 8 primary sources, verified 4 citations, caption verdict: `contradicted`, semantic classifications: `['meaning_changed']`.

### Case: `case_3_chronology_reorder` (reordered_chronology)
- **Tier 1 (Deterministic):** Matched source `NASA Artemis I Mission Journey (Official Reference)`, visual coverage 42.5%, detected 0 omissions. *Limitation:* Extracted 0 claims and cannot verify caption.
- **Tier 2 (Closed-Book):** Extracted 1 claims. *Limitation:* Without external document search, citation guard forced verdict to inconclusive (0 citations verified).
- **Tier 3 (Full CONTEXT):** Retrieved 8 primary sources, verified 4 citations, caption verdict: `inconclusive`, semantic classifications: `['inconclusive']`.
