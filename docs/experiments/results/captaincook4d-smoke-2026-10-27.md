# CaptainCook4D smoke evaluation — 2026-10-27

**Status: fail for P0; useful exploratory evidence only.** This is not a product capability claim.

## Question

Can Muse Spark learn a short physical process from one demonstration, accept a separate normal attempt, and detect an annotated ordering error from another attempt?

## Data and protocol

We used five short crops from CaptainCook4D's Pan Fried Tofu procedure. The official project page describes 384 recordings, with separate normal and deliberate-error activities, and states that the data is under Apache License 2.0. The annotation repository contains per-recording action and error labels and documents participant consent. See [project page](https://captaincook4d.github.io/captain-cook/), [annotation repository](https://github.com/CaptainCook4D/annotations), and [official downloader](https://github.com/CaptainCook4D/downloader).

The source clips and labels remain outside this repository. Model inputs were neutral short crops; annotation labels and condition names were not sent in prompts or uploaded filenames.

| Role | Recording | Ground truth | Crop in source |
|---|---|---|---:|
| Learn A | `25_1` | Normal Pan Fried Tofu; remove pan from heat, then flip tofu | 930–1090 s (wide retry: 970–1090 s was the first pass) |
| Control B | `25_11` | Normal Pan Fried Tofu | 645–720 s |
| Error C | `25_22` | Flip before removing pan from heat (annotated order error) | 800–940 s |
| Error D | `25_4` | Flip before removing pan from heat (annotated order error); same environment ID as A | 890–1000 s |

Run outputs are in `/private/tmp/showme-stock-clips-2026-10-27/captaincook-runs/`; source videos and annotation files are elsewhere under that temporary directory. No source video, annotation file, or model response was added to Git.

## Results

### First learn + observation passes

- A learned process with 5 states and 5 transitions; local process-reference validation passed.
- The learned transitions described cube placement, browning, and pan movement. It did **not** represent the critical “remove pan from heat before flipping” action or a corresponding ordering constraint.
- B, a separately annotated normal attempt, produced 2 model-reported divergences. These included pan relocation and a different visible browning progression. This is a false-positive control result.
- C, an annotated ordering-error attempt, produced 0 divergences and `no_divergence_observed`. This is a false negative for the target mistake.

### Wider-context retry

- A wider expert crop produced 5 states and 4 transitions; reference validation passed.
- The widened learn still omitted the remove-from-heat action. It added incidental order rules such as monitoring before touching cubes and turning while the pan remains on the stovetop.
- D, an annotated ordering-error attempt from the same environment ID as A, produced 3 divergences and `recovery_status: underway`. The reported divergences concerned burner placement, utensil location, and cube appearance. It did not identify the annotated flip-before-removal violation. These are not valid detections of the target error.

Across the five calls, usage was 160,345 input tokens and 6,541 output tokens. The calls used `muse-spark-1.3`. Local schema/reference validation passing means only that the returned structure is parseable and internally referential; it does not mean the process or assessment is correct.

## Conclusion

This protocol does **not** pass the P0 proof. The current pipeline turns one clip's incidental scene layout and action order into supposed process rules, then either rejects a normal variant or misses the labeled error. The result is consistent with an under-specified process representation and sparse observation, not evidence of learned procedural understanding.

Do not add UI or SAM to hide this failure. The next experiment should narrow to a short, visually explicit task with a clear reversible mistake and recovery, use an expert clip that shows the decisive precondition and postcondition, and define the human answer key before running inference. The model representation needs to distinguish task constraints from incidental placement and allow valid action variation. Keep evaluation labels out of the model input.

## Attribution and use

CaptainCook4D is attributed to its authors; source media remains in a local temporary directory and is not redistributed here. The project page states Apache 2.0 for the dataset and the annotation repository records IRB approval and participant consent. Recheck the current dataset terms before any public demo or redistribution.
