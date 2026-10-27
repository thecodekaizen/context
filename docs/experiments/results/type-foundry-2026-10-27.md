# Tiny Type Lab controlled experiment result

**Preregistration:** [`../type-foundry-preregistration.md`](../type-foundry-preregistration.md)  
**Run date:** 2026-10-27  
**Model:** `muse-spark-1.3` Standard, reasoning effort `high`; raw discovery prompt v2  
**Run artifacts:** `.thread-experiment-runs/type-foundry/20261027/` (local and git-ignored)

## Results

### Complete case: PASS (5/5 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Independent direction | PASS | Muse described a broadening from a code-editor/terminal monospace face to code, explanatory text, and compact labels. |
| Temporal contrast | PASS | It cited `type-001` (2023-02-10) and later artifacts `type-004` (2024-05-14), `type-005` (2025-01-09), and `type-006` (2025-08-18). |
| Continuity | PASS | The finding says code remains a showcase use case; `type-006` supports that continuity. |
| Traceability | PASS | Every cited artifact ID and date matched the raw archive. It also surfaced `type-003` and `type-006` as complicating evidence. |
| Epistemic restraint | PASS | The finding itself says the project “appears to have broadened.” The local wording guard accepted it. |

### Ablation: PASS

With only `type-001`–`type-003`, Muse returned an empty candidate and said the archive was insufficient to establish evolution. It did not repeat the full-case conclusion without the later evidence.

### Overall: PASS under preregistered criteria

Both the full case and the decisive-evidence ablation passed. No prompt changes or reruns were made after inspecting either output.

## Usage

| Case | Input tokens | Output tokens (including reasoning) | Estimated cost |
|---|---:|---:|---:|
| Complete | 633 | 2,583 | $0.011769 |
| Ablation | 395 | 2,294 | $0.010243 |
| **Total** | **1,028** | **4,877** | **$0.022012** |

Cost is the local token-based estimate; confirm actual billing in Meta Billing.

## Interpretation boundary

This is one additional controlled test on a fictional, compact archive authored around the preregistered expected evolution. It shows that this run recovered the pattern from raw source artifacts, included continuity/counter-evidence, and withheld the finding after the decisive evidence was removed. It does not establish repeatability, calibrated uncertainty, real-world transfer, or product effectiveness. The earlier Neighborhood Atlas preregistration remains an overall **FAIL**; that scorecard is unchanged.
