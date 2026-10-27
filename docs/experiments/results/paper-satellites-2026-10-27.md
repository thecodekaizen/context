# Paper Satellites raw-discovery result

**Preregistration:** [`../paper-satellites-preregistration.md`](../paper-satellites-preregistration.md)  
**Run date:** 2026-10-27  
**Model:** `muse-spark-1.3`; raw-discovery prompt v2.  
**Important protocol deviation:** the preregistration specified minimal reasoning, but the committed runner currently sends `reasoning.effort = high`. The calls were made once per archive with that implementation setting. No retries or prompt changes were made. Treat this as a preregistered fixture and criteria with a disclosed model-setting deviation, not a perfectly executed preregistered protocol.

## Results

### Complete case: PASS (5/5 criteria)

| Criterion | Result | Evidence |
|---|---|---|
| Direction | PASS | Muse described movement from standalone printed object stories toward interconnected multi-voice audio scenes, while retaining illustrated text. |
| Temporal support | PASS | It cited early `paper-001` (2024-01-12), `paper-002` (2024-04-08), and later `paper-004` (2025-02-17), `paper-005` (2025-08-06), and `paper-006` (2026-03-11). |
| Continuity | PASS | The finding retains illustrated text as a parallel component, supported explicitly by `paper-006`. |
| Traceability | PASS | Every cited ID/date matched the archive. The response also cited `paper-003`, `paper-004`, and `paper-006` as complicating evidence. |
| Restraint | PASS | The finding begins “appears to evolve”; it does not claim print was abandoned or invent a motive. |

### Ablation: FAIL

The ablation retained only `paper-001`–`paper-004`, including an explicitly experimental read-aloud and a two-voice pilot. Muse nevertheless returned a candidate that the project “appears to evolve” toward interconnected multi-voice audio presentation. It acknowledged the limited four-artifact archive, but did not limit its conclusion to an experiment or say that a developed ensemble direction was not established. This fails the preregistered ablation criterion: early experimentation was enough to trigger a project-level evolution claim.

### Overall: FAIL under the preregistered criteria

The full case recovered the expected pattern. The ablation shows the engine can overread a pilot as a developed direction. The disclosed reasoning-setting mismatch is an additional protocol limitation. No prompt changes or reruns were made after inspecting outputs.

## Exact input hashes

SHA-256 of the exact prompt-plus-projected-archive input string sent to the API:

- Complete `raw.json`: `fc41da7841455fbb6e8a0327e1ee03195de5c893cf0890b27e257aeced8cc199`
- Ablation `ablation-before-ensemble.json`: `00194639a0082129571023747083320881804c6a87826309c2a5a3ec28228ce7`

## Usage

| Case | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|
| Complete | 678 | 2,699 | $0.012318 |
| Ablation | 507 | 2,190 | $0.009941 |
| **Total** | **1,185** | **4,889** | **$0.022259** |

The local cumulative token-based estimate after these calls was **$0.080430**. Confirm actual usage in Meta Billing.

## Interpretation boundary

This is one deliberately constructed synthetic archive. It demonstrates that this Muse run can cite a plausible temporal pattern from raw artifacts, but also that an early pilot can be overinterpreted as a durable direction. It does not establish repeatability, calibrated uncertainty, real-world transfer, or product effectiveness. The model-setting deviation limits comparison with the stated procedure; do not silently revise the preregistration after seeing results.
