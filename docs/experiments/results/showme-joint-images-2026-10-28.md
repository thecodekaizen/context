# Inspect focused source/learner image comparisons

Three explicitly approved calls, October 28. Baseline process, transition T18, official LEGO 30727 step17/18 reference crop and original IMG_7670 frames at 11, 23 and 29 seconds. Same joint-inspection v1 prompt, no expected correctness labels, no retries. Source selection and transition selection are disclosed human/tool inputs, not automatic discovery.

| Frame seek | Model assessment | Latency |
| --- | --- | --- |
| 11 seconds | unclear | 15.32 seconds |
| 23 seconds | unclear | 14.82 seconds |
| 29 seconds | unclear | 12.20 seconds |

Each response described relevant source landmarks and learner landmarks, but said the wing-to-cockpit contact/facing was occluded by fingers, edge-on angle or blur. Each requested an exposed joint view. All passed structural validation. No response proved an attached orientation error, a match of the joint or recovery.

The samples are selected frames from one clip, not independent task trials. Three unclear results are not a measured error-detection accuracy. A source diagram and a frame alone do not remove occlusion or establish temporal intent. The grouped wing object and whole T18 transition also limit per-joint specificity.

Private prompt, inputs/hashes, baseline process and raw responses are under ignored `.showme-runs/lego-source-comparison-v5-20261028/joint-*` directories. No private images are committed. The CLI preserves raw output before validation and failures without retry; the command is now `showme inspect-joint PROCESS SOURCE_IMAGE LEARNER_IMAGE --transition ID --output NEW_DIRECTORY`.

## Next evidence requirement

Inspect an exposed single wing-to-cockpit joint with a stable view, keeping the source and prompt fixed. Existing clips should be screened for such a view first. If unavailable, one hands-off still exposing the actual contact can resolve this visibility question without asking for another full build recording. Keep independent correctness labels separate from model input. Do not substitute synthetic wrong attachments or fabricated scene geometry for physical evidence.
