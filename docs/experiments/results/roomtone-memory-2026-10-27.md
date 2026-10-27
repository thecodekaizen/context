# Roomtone project-memory experiment result

**Preregistration:** [`../roomtone-memory-preregistration.md`](../roomtone-memory-preregistration.md)  
**Run date:** 2026-10-27  
**Extraction model:** `muse-spark-1.3` Standard, minimal reasoning; one batch request per archive  
**Run artifacts:** `.thread-experiment-runs/roomtone/20261027/` (local and git-ignored)

## Results

### Full archive: PASS (5/5 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Direction | PASS | The memory comparison returned: “Across this project, emphasis appears to move from 'sound diary' toward 'shared collection' in the dated artifacts.” |
| Temporal support | PASS | Three early source records (`room-001`–`room-003`, 2023) support the personal sound diary; three later records (`room-004`–`room-006`, 2024–2025) support the shared collection. |
| Continuity | PASS | `field recording` persists in all three later memories; continuity evidence links `room-004`, `room-005`, and `room-006`. The final source says phone recording remains the way to add sounds. |
| Traceability | PASS | Every source ID/date in the result matches the raw archive. No fabricated references appeared. |
| Restraint | PASS | The hypothesis says “appears to move,” avoids invented causes or personality claims, and includes the midpoint-method caveat. |

### Ablation: PASS

With only `room-001`–`room-004`, the comparison returned no sufficiently supported evolution. It did not treat a single collaborator request as proof that a shared library had become the project's developed direction.

### Overall: PASS under preregistered criteria

Both full and ablation conditions passed. The prompt was not tuned and neither case was rerun after inspecting outputs.

## Usage

| Case | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|
| Full archive | 550 | 742 | $0.003841 |
| Ablation | 414 | 449 | $0.002426 |
| **Total** | **964** | **1,191** | **$0.006267** |

Local estimate only; confirm actual charges in Meta Billing.

## Interpretation boundary

This is a preregistered pass on one small synthetic archive. It is an independent test of the final batch-memory prompt relative to the earlier Type Lab prompt-development smoke test, but it does not establish real-world accuracy, repeatability, or general transfer. The direct raw-discovery scorecards remain separate: Neighborhood Atlas failed its wording criterion; Tiny Type Lab direct raw discovery passed its criteria.
