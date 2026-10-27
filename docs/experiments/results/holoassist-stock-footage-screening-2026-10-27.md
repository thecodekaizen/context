# HoloAssist stock-footage screening

**Date:** 2026-10-27  
**Purpose:** Find public, labeled mistake-and-recovery footage for SHOWME's controlled observation experiment.  
**Status:** One HoloAssist GoPro video was retrieved and matched by recording ID to its annotation. It has labeled mistakes and self-corrections. No HoloAssist video was submitted to a model. A separate clean demonstration video for a paired trial has not been found locally.

## What was checked

HoloAssist is an egocentric dataset of people completing practical tasks with an instructor. Its fine-grained action annotations include labels such as `Wrong Action, corrected by student` and `Wrong Action, corrected by instructor verbally`, with timestamps and short explanations. The public annotation mirror lists 1,000 JSON files totaling about 44.4 MB. A partial scan of 799 downloaded annotation files found wrong-action labels in 566 sessions; this is a screening result, not a model evaluation.

Short, low-risk candidates include printer setup and GoPro setup. The local files include `R005-7July-GoPro.mp4` (84 MB) and `R005-7July-GoPro.json` (295 seconds); both identify the same recording. Its labels mark accidental power-on actions at 19.5–21.4 and 42.5–43.2 seconds, plus an attempted battery-door closure while the battery is upside down at 160.5–163.4 seconds. `R076-21July-SmallPrinter` also includes labeled mistakes around positioning a test page and operating a lever. These descriptions and labels are evaluation ground truth: they must stay out of the model's inputs.

## Retrieval constraint and size

The official HoloAssist page lists compressed videos at 144.62 GB for the full archive and labels at 111 MB. A byte-range header scan of the official tar found metadata for `R072-20July-GoPro` but no video member for that session in the scanned archive entries. The full archive was not downloaded. The local `R005` clip and its matching annotation are sufficient for a future observer-only labeled smoke, but not for the product's paired demonstration-to-learner test.

The three IndustReal stock clips already downloaded for the exploratory SHOWME run total **87 MB on disk** (28 MB, 27 MB, and 32 MB). They remain under `/private/tmp/showme-stock-clips-2026-10-27/` and are not committed. The complete Hugging Face ZIP mirror is 2.51 GB; only selected byte ranges were fetched for those three clips.

## Decision

Use the retrieved `R005` recording only for a labeled observer smoke after a process model can be obtained independently. Do not learn the process from this full clip and then score its errors; that leaks the evaluated actions into the learned model. Do not fetch the full 144.62 GB archive to find a paired demonstration. The IndustReal runs remain exploratory only: their exact ground-truth labels have not been matched, so no detection or recovery result should be scored as a hit.

## Sources

- [HoloAssist project and official data sizes/license](https://holoassist.github.io/)
- [HoloAssist annotation schema](https://holoassist.github.io/data_links/README.html)
- [HoloAssist public annotation/video mirror](https://huggingface.co/datasets/SitongGong/HoloAssist/tree/main)
- [IndustReal project, annotations, and license](https://github.com/TimSchoonbeek/IndustReal)
- [IndustReal video archive mirror](https://huggingface.co/datasets/Zzitang/IndustReal/tree/main)
