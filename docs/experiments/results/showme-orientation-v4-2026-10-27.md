# Orientation extraction follow-up — 2026-10-27

**Outcome: richer candidate facts, failed learner-response validation, orientation capability unproven.** This was an exploratory run on existing media. The original reviewed app model remains active; the fresh candidate was imported into Teach for inspection, without checking approval or using it as the reviewed model.

## Inputs and provenance

One approved Teach call used the existing silent 813.5-second, 640x360, 2 fps derivative of IMG_7660 with the public two-page LEGO 30727 instructions. One separately approved Observe call used the existing silent 34-second derivative of IMG_7670 and the fresh candidate. No expected mistake labels or evaluation timestamps were sent to either call.

Private artifacts are retained in ignored `.showme-runs/lego-orientation-v4-20261027/`: the baseline process, exact Teach and Observe prompts, source hashes, provider outputs, validated Teach candidate, and observation validation failure. The files are not committed. The saved learner-review export retains the earlier baseline result separately.

| Phase | Prompt | Wall time | Input / output tokens | Result |
|---|---|---:|---:|---|
| Teach | `showme-video-analysis-v4` | 227.3 seconds | 85,707 / 4,043 | Format and references valid; content still needs review |
| Observe | `showme-observe-v4` | 26.0 seconds | 13,117 / 2,384 | Rejected by observation validator |

Model: `muse-spark-1.3`. Token counts do not establish dollar cost; no billing estimate is claimed. No automatic retries were made.

## What changed in the representation

The baseline groups both wings under one object ID and gives the final transition only a generic completed-model postcondition. The fresh extraction still groups the wings, but now describes the clip plates facing inward toward the core and the core centered between symmetric wings. The rendered step 17/18 diagrams support the connector-facing and relative-placement distinction.

The candidate also says the cockpit dishes face front and rear. Visual review of step 10 instead shows a small dome above the core and the larger dish/transparent dish at the front. This unsupported or ambiguous wording prevents approving the candidate as an accurate geometric description. The candidate itself notes uncertainty about core orientation. Adding more prose did not guarantee a correct representation.

These are assistant source-review notes, not an independently authored human ground-truth key. No new manually authored orientation rule was inserted into the model or promoted to an enforced requirement.

## Learner comparison and failure

The new observation returned five events and `underway`. It described a detached wing at 14 seconds and reattachment at 22 seconds, but also claimed the visible wings were too small relative to its large-panel expectation. It did not establish that an attached wing faced the wrong direction. The apparent-size claim remains unverified and may reflect image scale, projection, or an incorrect interpretation of the parts.

The output marked manual steps 17 and 18 as possible mismatches at 17 and 22 seconds, while its sole divergence record was timestamped 14 seconds. The validator requires a nearby divergence record for each possible reference mismatch; neither check satisfied the current two-second alignment rule. Although the divergence text described a longer interval, the schema supplies a single divergence timestamp. The response therefore failed structural evidence alignment and was not accepted as an observation. This does not independently establish whether its geometric claim is correct.

Keep this failure visible. Do not relax the validator or relabel the output as a successful orientation catch merely to get a passing result. Whether persistent issues need explicit evidence intervals is a future modeling question; this run has not resolved it.

Both the extraction prompt and observation prompt changed from the earlier baseline, so this is not an isolated test of either prompt change. There is no matched correct control or repeatability score.

## Implementation consequence

Teach previously displayed actions and citations while hiding the target state's observable facts and postconditions. It now provides **Inspect proposed result** for each transition, exposing those model claims with their existing step evidence before approval.

The API-to-shared-model adapter now preserves observable facts instead of discarding them. Simulate displays them as **Expected appearance in this simulation**, explicitly separate from camera observations. Older candidates without those facts remain readable and receive no invented relationships. Arrays are copied so temporary simulated annotations cannot mutate the reviewed source data.

Verification: 23 web tests and TypeScript checking pass. Browser import/expand confirmed that the fresh candidate’s final-state claims are visible and approval remains unchecked. A separate temporary browser tab restored the original reviewed model and displayed its observable facts under Expected appearance in this simulation; that tab was then closed. The original active process was not replaced. These software checks do not validate perception accuracy.

## Next evidence gate

Resolve the source-model geometry before another orientation claim. Compare attachment landmarks and facing relationships rather than relying on generic size adjectives. Preserve the baseline, candidate, and failed response; require a source-supported candidate and matched correct/incorrect attached states before calling orientation detection successful. Existing footage can be inspected further; more recording alone is not a fix for an incorrect process representation.

Source: [official LEGO 30727 instructions](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6609577.pdf).
