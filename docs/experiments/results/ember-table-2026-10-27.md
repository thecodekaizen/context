# Ember Table endpoint-support result

**Preregistration:** [`../ember-table-preregistration.md`](../ember-table-preregistration.md)  
**Run date:** 2026-10-27  
**Model:** `muse-spark-1.3`, Standard, minimal reasoning, raw-discovery prompt v4; automatic SDK retries disabled. The preregistered inputs and criteria were pushed in `8263462` before either call. Both calls completed once with `status=completed`.

## Results

### Full archive: FAIL (3/4 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Direction and continuity | **FAIL** | The candidate says the project “appears to shift” toward a shared seasonal collection with contributor recipes and retained illustrations, but does not explicitly say the collection was completed. The source observation for `ember-006` does identify a finished, shared first booklet. |
| Endpoint support | PASS | Supporting list cites early `ember-001`/`ember-002` and late `ember-005`/`ember-006`, including the decisive release. |
| Stages and provenance | PASS | `ember-003`/`ember-004` experimental, `ember-005` planned, and `ember-006` released; cited IDs and dates match. |
| Restraint | PASS | Uses tentative “appears to” language, invents no cause, and does not claim the personal notebook disappeared. |

### Ablation: PASS

With `ember-006` removed, Muse returned an empty candidate. It treated `ember-003` and `ember-004` as experiments and `ember-005` as a proposal, and stated that the archive did not establish a realized evolution. This meets the preregistered ablation criterion.

### Overall: FAIL under the preregistered criteria

The endpoint gate allowed the full candidate and the ablation produced no finding, so this fresh case passes that limited behavior check. The full candidate still missed the explicit completed-booklet detail, leaving the overall content evaluation short of its preregistered bar. This one synthetic case does not establish general reliability or real-world transfer.

## Exact input hashes

SHA-256 of the exact prompt plus projected raw archive sent to the API:

- Full: `10c6e3de2ab1af94b55514fc99b2370b9ba4bd69b9ddd3eb88f2278dbdcede47`
- Ablation: `f202513b5c847313ede5666a4554cdcc2456f35720b87ddb2dc0de48b6c08806`

## Usage

| Case | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|
| Full | 783 | 847 | $0.004579 |
| Ablation | 692 | 763 | $0.004108 |
| **Total** | **1,475** | **1,610** | **$0.008687** |

The local cumulative token-based estimate after these calls was **$0.139361**. This is not Meta's billing total; confirm actual usage in Meta Billing.
