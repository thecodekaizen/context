# SHOWME Lego Teach Smoke Test — Result

**Run date:** 2026-10-27  
**Preregistration:** [`showme-lego-teach-preregistration-2026-10-27.md`](../showme-lego-teach-preregistration-2026-10-27.md)  
**Model:** `muse-spark-1.3`  
**Input:** one private, user-recorded 15:22 overhead build video; compressed, downscaled to 1280×720, 5 fps, and stripped of audio for this visual-only run. The original was not modified. The video and model response are not committed.

## Result

**Verdict: useful Teach smoke-test result, but strict preregistered pass criteria were not fully met.** The model found the broad build progression, but still represented unproven requirements as transition preconditions.

| Preregistered criterion | Result | Evidence |
|---|---|---|
| Structured process passes local reference validation | Pass | Seven states, seven transitions, four objects; local validator returned `passed`. |
| At least three broad landmarks in chronological order | Pass | The output describes an initial base, a growing gray body, separate black panels, then joining the panels to the body. |
| Evidence intervals overlap the registered windows and support the landmarks | Pass | I reviewed sampled frames around 230 s and 538 s, plus source frames at 900 s and 918 s. They show the growing gray core, separate black panels beside it, and the hands joining the assemblies. The cited transition intervals overlap these visible phases. |
| Do not present one observed order as a required dependency | **Fail** | The model populated `preconditions` such as “small base present” and “early core present.” A single trace shows those conditions in this recording, not that they are required for the task. |
| Mark ambiguous details as uncertain | Pass | It says the exact set and whether the final model is complete are not established; loose bricks remain visible at the end. |

The output is a candidate trace, not an executable skill yet. The “preconditions” field currently mixes observed context with claims that can be read as task requirements. The schema/prompt should be changed to preserve observed context separately from validated constraints before Do or Simulate can safely rely on it.

## Run details

- Local input preparation succeeded for the full 922.6-second video; the 24 stills are local review samples, while Muse received the complete video.
- Muse returned 78,201 input tokens and 1,828 output tokens.
- Estimated standard-mode usage at the published Muse Spark 1.3 rates is about **$0.11**; the actual credit ledger is authoritative. See [Meta Muse Spark pricing](https://dev.meta.ai/models/muse-spark).
- The adapter requested one-hour remote-file expiry and attempted deletion after the response. The local run output, including the model response, remains under `/private/tmp/showme-img7660-learn` and is excluded from Git.
- One video cannot validate learner mistake detection, recovery, camera robustness, or whether the output captures a complete build. Those require a later Do evaluation.

## Next engineering action

Change the process representation so it records **observed context and observed transitions** without labeling them as preconditions. Keep actual required constraints separate and unset unless supported by independent evidence or explicitly confirmed by a human. Then use this same demonstration for Teach and a later learner attempt for Do; do not treat this single trace as proof of requirements.
