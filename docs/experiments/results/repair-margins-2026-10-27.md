# Repair Margins minimal-reasoning result

**Preregistration:** [`../repair-margins-preregistration.md`](../repair-margins-preregistration.md)  
**Run date:** 2026-10-27  
**Model:** `muse-spark-1.3`; raw-discovery prompt v4; reasoning effort `minimal`; response status `completed` for both calls.

## Results

### Complete case: FAIL (3/4 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Direction and continuity | PASS | The finding describes movement from a personal workshop record toward a resident-contributed neighborhood guide while retaining the original diagrams. |
| Temporal support | FAIL | The supporting-evidence list cites `repair-004`, `repair-005`, and `repair-006`, all later than the initial personal-work artifacts. The observations section describes `repair-001` and `repair-002`, but the candidate's supporting references do not connect those early items to the shift. |
| Evidence stages and provenance | PASS | `repair-003` and `repair-004` were `experimental`, `repair-005` was `planned`, and `repair-006` was `released`. All cited IDs and dates matched. |
| Restraint | PASS | The candidate says “appears to shift,” preserves the original diagrams, and invents no cause. |

### Ablation: PASS

Without `repair-006`, Muse described the collective direction as remaining at the proposal/pilot stage and explicitly said no completed collective guide was evidenced. It did not present the neighborhood guide as an adopted or completed direction. The early test, pilot, and proposal received the expected stages.

### Overall: FAIL under preregistered criteria

The ablation showed appropriate restraint about an uncompleted proposal. The complete case failed because the supporting-evidence list did not cite the early side of the claimed temporal change. Stage labels alone did not make the full finding sufficiently supported.

## Exact input hashes

SHA-256 of the prompt plus projected archive sent to the API:

- Complete `raw.json`: `e7aaddd65fd57f540de0e73534100634cb0b47e2a9e41c896fe02d3315d9eab7`
- Ablation `ablation-before-release.json`: `654f976de3dc169ec0cf788a1d28026f8f4fc50f2371b3704117fb101e3a3cff`

## Usage

| Case | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|
| Complete | 741 | 964 | $0.005023 |
| Ablation | 666 | 977 | $0.004985 |
| **Total** | **1,407** | **1,941** | **$0.010008** |

The local cumulative token-based estimate after these calls was **$0.120499**. Confirm actual usage in Meta Billing.

## Interpretation boundary

Both calls completed below the configured output cap. This differs from the earlier high-reasoning Cook's Margin ablation, which reached the cap, but the fixtures also differ; this pair cannot isolate reasoning effort as the cause. It is one synthetic domain case and does not demonstrate repeatability, calibrated uncertainty, or real-world transfer.
