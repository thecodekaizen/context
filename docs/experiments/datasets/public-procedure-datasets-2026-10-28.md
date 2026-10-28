# Select public procedure footage for a decisive test

Screened October 28. Use original publishers for annotations, license and acquisition details. Dataset labels stay separate from inference inputs. Availability is not a capability result.

| Dataset | Fit | Current action |
| --- | --- | --- |
| IMPACT v1.1 | Physical angle-grinder assembly/disassembly; bimanual normal/anomaly/recovery labels and multiple views | Downloaded annotations and two selected frontal videos; completed a diagnostic direct-model vs SHOWME pilot |
| IndustReal | Assembly/maintenance with component error states and procedure labels | Backup; existing exploratory videos lack matched official labels locally |
| HoloAssist | Practical tasks with mistakes and human assistance | Existing labeled GoPro learner clip; independent paired clean demonstration remains unresolved |
| Assembly101 | Toy assembly with natural mistakes/corrections and multiview video | Official video repository requires accepting publisher access terms; did not bypass the gate |

## IMPACT acquisition

Official project: https://github.com/Kratos-Wen/IMPACT
Release manifest: https://github.com/Kratos-Wen/IMPACT/blob/main/docs/DATA_RELEASE.md
Dataset: https://huggingface.co/datasets/KratosWen/IMPACT

Downloaded the 8,485,262-byte annotation bundle. The quick-start sample is about 2.8 GiB and lacks explicit recovery segments in its selected three trials, so it was not used for a recovery proof. Inspected remote ZIP directories with HTTP ranges, then retrieved two frontal members from the main archive: ER07AD15_Disassembly_A_001 and A_004 (123,944,157 and 113,993,090 bytes). Each member's byte count and ZIP CRC were checked; local SHA-256 and video frame metadata were recorded. The full 29 GiB front-view archive was not downloaded. Partial early sample-download material was not used.

Dataset license: CC BY-NC-SA 4.0; code has a separate Apache-2.0 license. Keep media out of the application repository. These clips are research evaluation inputs, not automatically cleared production assets or a claim of safe equipment guidance.

## Test outcome

See `../results/showme-impact-pilot-2026-10-28.md`. Both direct model and SHOWME missed the selected annotated issue/recovery. No advantage was established. Do not turn dataset retrieval, a clean normal-control output or software test counts into an error-detection success claim.

Other primary sources:
- https://github.com/TimSchoonbeek/IndustReal
- https://holoassist.github.io/
- https://huggingface.co/datasets/cvml-nus/assembly101
