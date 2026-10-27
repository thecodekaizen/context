# SHOWME single-frame snapshot API smoke

**Date:** 2026-10-27  
**Result type:** paid integration smoke; not a scored learner evaluation  
**Model:** Muse Spark 1.3 (`muse-spark-1.3`)

## Input

- Source video: [Man Assembling Lego Toys](https://www.pexels.com/video/man-assembling-lego-toys-6666449/), by Roman Odintsov; used under the [Pexels license](https://www.pexels.com/license/).
- Process: the candidate Skill Model generated in the earlier [stock clip trial](../../../experiments/proof-of-magic/stock-clip-trial.md).
- Frame: locally sampled frame at 4 seconds. The still showed a joined grey/yellow piece in one hand and a separate black piece in the other.
- Prompt: one still image compared against the reviewed-process vocabulary; no expected answer or evaluation label was supplied.
- Raw response: `/tmp/showme-snapshot-smoke.json`. Video, frame, and raw response remain outside Git.

## Result

Muse returned `consistent`, state `s1_yellow_joined`, with inspectable evidence that the grey/yellow piece was together while the black piece remained separate. It also listed uncertainty about the small, partially occluded connection and whether the black piece was the intended pin. Local snapshot validation passed, including the state and object ID checks.

The request used 4,922 input tokens and 558 output tokens. At the [published Standard Muse Spark rates](https://dev.meta.ai/docs/pricing-rate-limits), the token estimate is **$0.0085**. This is an estimate; Meta Billing is authoritative.

## What this establishes

- The image-understanding request works end to end through the Meta Responses API using an inline JPEG data URL.
- The snapshot path can return a state from the learned Skill Model and evidence/uncertainty fields, and local validation accepts the result.
- On this frame, the model's assessment agreed with a manual visual check.

## What this does not establish

- This is one frame from the same stock clip used to produce the process model. It is not a held-out person, arrangement, or camera view.
- No mistake, recovery, continuous tracking, live intervention, or SAM grounding was tested.
- A valid structured response is not evidence that the model can reliably distinguish correct from incorrect task execution.

The single-frame path is now an integration-tested prototype capability. The P0 matched correct/mistake/recovery evaluation remains open.
