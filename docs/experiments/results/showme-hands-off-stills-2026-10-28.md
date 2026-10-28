# Compare five hands-off assembly views

October 28. Five explicitly approved comparisons using resized IMG_7671–7675, the official step17/18 diagram crop and baseline process T18. Same joint-inspection v1 prompt, one call per image, no retry and no expected mistake label. Originals unchanged; resized copies were visually checked before provider use. An initial local sips conversion rendered black and was discarded without upload; ffmpeg copies were used instead.

| Input | Reported result | Latency |
| --- | --- | --- |
| IMG_7671 | matches | 9.51 s |
| IMG_7672 | matches | 9.28 s |
| IMG_7673 | matches | 4.15 s |
| IMG_7674 | unclear | 5.84 s |
| IMG_7675 | unclear | 15.11 s |

After inference, the user confirmed all five depict the same unchanged assembly. That context is recorded privately as evaluation context; it was never sent in the inference prompts. Different visibility can justify different certainty, so this alone does not prove contradictory physical verdicts. No incorrect/correct pair or correction sequence is established.

## Failure found

The first matches relied heavily on bilateral arrangement. IMG_7673's explanation said the central round detail faced inward in the reference, inconsistent with the outward-facing detail in the inspected diagram. Thus matching result strings are not reliable correctness evidence. The five runs do not establish a detected mistake. Keep this source-reading error visible rather than counting three passes.

## Implemented response

Joint-inspection v2 requires each compared relation to name its type (contact, facing, overall_arrangement) and visibility separately for source and learner. Occluded/ambiguous relationships cannot establish a match or difference. A joint verdict requires at least one visible contact/facing comparison; silhouette alone is insufficient. These are consistency guards over model reports, not independent pixel verification. A model can still misread a visible source, so source semantic accuracy remains an evaluation requirement.

98 local backend checks pass. v2 has not been rerun against Meta; approved five-call budget exhausted without retries. Private original/derived hashes, prompts and raw responses are under ignored `.showme-runs/lego-still-joints-20261028/`. Photos and evaluation context are excluded from Git.
