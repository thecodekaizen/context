# HoloAssist stock-footage screening

**Date:** 2026-10-27  
**Purpose:** Find public, labeled mistake-and-recovery footage for SHOWME's controlled observation experiment.  
**Status:** Useful labels found; individual video retrieval not established. No HoloAssist video was submitted to a model.

## What was checked

HoloAssist is an egocentric dataset of people completing practical tasks with an instructor. Its fine-grained action annotations include labels such as `Wrong Action, corrected by student` and `Wrong Action, corrected by instructor verbally`, with timestamps and short explanations. The public annotation mirror lists 1,000 JSON files totaling about 44.4 MB. A partial scan of 799 downloaded annotation files found wrong-action labels in 566 sessions; this is a screening result, not a model evaluation.

Short, low-risk candidates include printer setup and GoPro setup. For example, the 45-second `R072-20July-BigPrinter` annotation labels a wrong-button press at 5.1–5.9 seconds as corrected by the student. The 149-second `R076-21July-SmallPrinter` annotation includes mistakes around positioning a test page and operating a lever. These descriptions and labels are evaluation ground truth: they must stay out of the model's inputs.

## Retrieval constraint and size

The official HoloAssist page lists compressed videos at 144.62 GB for the full archive and labels at 111 MB. The Hugging Face mirror has session annotations, but the checked session folders did not contain individual MP4 files; the videos appear to be held in very large concatenated archive parts. We have not established a reliable per-session byte index, so downloading the full archive is not justified for this experiment.

The three IndustReal stock clips already downloaded for the exploratory SHOWME run total **87 MB on disk** (28 MB, 27 MB, and 32 MB). They remain under `/private/tmp/showme-stock-clips-2026-10-27/` and are not committed. The complete Hugging Face ZIP mirror is 2.51 GB; only selected byte ranges were fetched for those three clips.

## Decision

Keep HoloAssist as a source of evaluation labels and a possible later test set, but do not fetch its 144.62 GB video archive. Continue the immediate experiment with the existing 87 MB IndustReal clips unless a lightweight, per-session HoloAssist video source becomes available. The IndustReal runs are exploratory only: the exact clips' ground-truth labels have not yet been matched, so no detection or recovery result should be scored as a hit.

## Sources

- [HoloAssist project and official data sizes/license](https://holoassist.github.io/)
- [HoloAssist annotation schema](https://holoassist.github.io/data_links/README.html)
- [HoloAssist public annotation/video mirror](https://huggingface.co/datasets/SitongGong/HoloAssist/tree/main)
- [IndustReal project, annotations, and license](https://github.com/TimSchoonbeek/IndustReal)
- [IndustReal video archive mirror](https://huggingface.co/datasets/Zzitang/IndustReal/tree/main)
