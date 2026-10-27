# Neighborhood Atlas controlled experiment result

**Preregistration:** [`../neighborhood-atlas-preregistration.md`](../neighborhood-atlas-preregistration.md)  
**Run date:** 2026-10-27 UTC  
**Model:** `muse-spark-1.3` (Standard), reasoning effort `high`  
**Run artifacts:** `.thread-experiment-runs/neighborhood-atlas/20261027T005716Z/` (local and git-ignored)

## Results

### Complete case: FAIL (4/5 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Independent direction | PASS | Candidate describes movement from navigation utility as primary toward a story-led experience. |
| Temporal synthesis | PASS | Distinguishes 2022–2023 navigation artifacts from 2024–2025 story artifacts without claiming a specific transition date. |
| Traceability | PASS | Cites all six artifact IDs with dates and relevance. |
| Continuity | PASS | Cites `artifact-006` and says navigation is secondary but retained; also notes `artifact-005` keeps place-based structure. |
| Epistemic restraint | FAIL | The candidate finding says “Project focus shifted” as an unqualified conclusion. It does not use the preregistered qualified framing such as “appears.” It does avoid unsupported cause and personality claims, and its limitations note archive gaps. |

### Ablation: PASS

With only artifacts `001`–`003`, the model returned an empty `candidate_finding`, summarized the consistent wayfinding evidence, and said the archive was insufficient to establish evolution.

### Overall: FAIL under preregistered criteria

The model independently reconstructed the expected direction from raw artifacts and withheld it after decisive story evidence was removed. The full result still fails because its main interpretation was more certain in wording than the preregistration permits. Criteria were not changed after seeing the output, and the prompt was not rerun or tuned.

## Usage

| Case | Input tokens | Output tokens (including reasoning) |
|---|---:|---:|
| Complete | 615 | 1,948 |
| Ablation | 385 | 1,390 |
| **Total** | **1,000** | **3,338** |

At the current [Standard Muse Spark rates](https://dev.meta.ai/docs/pricing-rate-limits), estimated token cost is approximately **$0.0154**: $0.00125 input plus $0.01420 output. Confirm final billing in the Meta dashboard.

## Interpretation boundary

This is a controlled result on one fictional, pre-labeled archive. It supports only that this Muse run recovered the expected temporal pattern from the six raw artifacts and withheld it in the specified ablation. It does not establish reliability across runs, real-world transfer, or general THREAD product effectiveness.
