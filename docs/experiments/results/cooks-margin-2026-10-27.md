# Cook's Margin evidence-stage result

**Preregistration:** [`../cooks-margin-preregistration.md`](../cooks-margin-preregistration.md)  
**Run date:** 2026-10-27  
**Model:** `muse-spark-1.3`; raw-discovery prompt v3; reasoning effort `high`.

## Results

### Complete case: PASS (4/4 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Direction and continuity | PASS | Finding describes expansion from a personal recipe notebook to a shared neighbor-contributed collection, while keeping the author's original recipes. |
| Temporal support | PASS | It cites early `cook-001` (2024-02-03), `cook-002` (2024-05-19), and later `cook-005` (2025-09-14), `cook-006` (2026-04-02). |
| Evidence stages and provenance | PASS | `cook-003` and `cook-004` were experimental, `cook-005` planned, and `cook-006` released. All cited IDs and dates matched. |
| Restraint | PASS | The finding says “appears to have evolved”; it does not claim the personal notebook was abandoned or invent a cause. |

### Ablation: INCONCLUSIVE

The one preregistered call returned output that the CLI could not parse as JSON and exited with `Muse returned invalid JSON`. The usage ledger shows 4,096 output tokens, equal to the configured output cap, so truncation is plausible but not confirmed: this runner does not retain the API's incomplete-response details for raw discovery. No retry was made, as required by the fixed procedure.

### Overall: INCONCLUSIVE; overall pass criteria not met

The full case demonstrates that this call returned the intended stage distinctions. Because the ablation result is unavailable, this evaluation cannot determine whether the current prompt and stage labels prevent a premature project-level claim when released evidence is removed. Do not count this as a full/ablation success.

## Exact input hashes

SHA-256 of the prompt plus projected archive sent to the API:

- Complete `raw.json`: `7aa8c2b92cefe03ad423901d2ea0dd69d1873dbdfe43529ad4c5a0177f7e500d`
- Ablation `ablation-before-release.json`: `abf6724b8e1deb01f4faccec54671209befd20f72997f4b6c5948aae04ab78fb`

## Usage

| Case | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|
| Complete | 738 | 2,568 | $0.011837 |
| Ablation (invalid JSON) | 653 | 4,096 | $0.018224 |
| **Total** | **1,391** | **6,664** | **$0.030061** |

The local cumulative token-based estimate after the two calls was **$0.110491**. Confirm actual usage in Meta Billing.

## Interpretation boundary

This is a single constructed synthetic case. The complete-case labels are consistent with the authored artifact statuses, but one complete result does not establish classification accuracy. The missing ablation result means this test neither validates nor falsifies whether evidence-stage labels improve restraint. Repeatability, real-world transfer, and calibrated uncertainty remain untested.
