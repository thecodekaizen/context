# IndustReal public-video exploration

**Date:** 2026-10-27
**Result type:** exploratory model transfer check; not a scored evaluation
**Model:** Muse Spark 1.3

## Source and handling

Used three individual MP4s from the IndustReal video archive: `27_main_0_1.mp4`, `27_main_3_1.mp4`, and `27_main_1_3.mp4`. The archive is a 2.51 GB Hugging Face mirror of the dataset; individual ZIP byte ranges were fetched so the archive itself was not downloaded. The upstream project and 4TU record identify IndustReal as Apache-2.0 licensed. The official 4TU file manifest timed out during this run, so the mirror’s exact correspondence to the official version and the selected recordings’ labels still need verification.

The clips are in `/private/tmp/showme-stock-clips-2026-10-27/` and are not committed. They are 1280×720 at 10 FPS. Each clip was submitted separately through the existing SHOWME CLI. The model received only the video and the learned candidate process, not evaluation labels or recording names.

Sources: [IndustReal project and license](https://github.com/TimSchoonbeek/IndustReal), [official 4TU dataset record](https://research.tue.nl/en/datasets/industreal-dataset-of-egocentric-videos-for-procedure-understandi/), [public video archive mirror](https://huggingface.co/datasets/Zzitang/IndustReal/tree/main).

## Runs

1. `27_main_0_1.mp4` → learned candidate with 6 objects, 8 states, and 7 transitions. Local schema and timestamp validation passed. Muse cited visible evidence for the toy vehicle, wheels, beams, bolts, nuts, and a sequence of disassembly/reassembly actions. It also recorded uncertainty about component names and orientation. Usage: 32,441 input and 1,965 output tokens.
2. `27_main_3_1.mp4` → compared against that candidate. Muse returned 9 events, 0 divergences, and `no_divergence_observed`. The clip showed a matching sequence. Usage: 34,945 input and 1,623 output tokens.
3. `27_main_1_3.mp4` → compared against the same candidate. Muse returned 8 events, 1 divergence, and `recovered`. It flagged a detached two-wheel axle subassembly at 139 seconds, then described the completed vehicle at 158 seconds. Usage: 43,785 input and 1,743 output tokens.

## Interpretation

This is not evidence that SHOWME detected a mistake or recovery. No ground-truth labels were available for these particular recordings. The third clip may show a legitimate alternate assembly path: it ends with the vehicle assembled, and the observed detached subassembly is not by itself proof of an error. Calling the final state “recovered” is therefore unsupported by this run. This is a useful warning that the current observer can conflate a process difference with an error and a later valid state with recovery.

The first two runs do show that the existing video path can extract an evidence-timestamped candidate and compare a second real assembly recording without flagging a divergence. They do not prove robustness, correct state recognition, or error detection.

## Next step

Obtain the official labels for these recordings (or choose recordings with publicly inspectable labels), establish the expected state transitions independently, then rerun the observer. The official 4TU metadata API timed out from this environment. Do not score the third run as a hit. No personal recording is needed for this next step.

Total recorded usage: 111,171 input and 5,331 output tokens across three completed inferences. At the pricing rates recorded in the existing stock smoke report, the token-rate estimate is about $0.16; check Meta Billing for the actual charge.
