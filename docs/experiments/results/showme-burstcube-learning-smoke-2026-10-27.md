# SHOWME stock-video learning smoke — BurstCube handling

**Date:** 2026-10-27  
**Purpose:** exploratory integration smoke test; not scored evidence for the SHOWME P0 claim.

## Source and rights notes

- Clip: [BurstCube Assembly and Testing (SVS14167 - BurstCube Frame)](https://commons.wikimedia.org/wiki/File:BurstCube_Assembly_and_Testing_(SVS14167_-_BurstCube_Frame).webm)
- NASA source page: https://svs.gsfc.nasa.gov/14167
- Commons lists the clip as U.S. public-domain material created by NASA. NASA's [media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) say NASA should be acknowledged, third-party material retains its own rights, and a recognizable person's likeness can require permission for commercial use. Keep this source credit with any reuse and do not imply NASA endorsement.
- The original clip and derived frames/process output remain in `/private/tmp/showme-stock-clips-2026-10-27/`; they are not committed.

## Run

- Source duration: 21.448 s; 3840×2160 WebM with audio.
- SHOWME generated a silent 1280px-bounded MP4 and sampled frames locally, then sent that MP4 to Muse Spark 1.3 using the configured `showme-video-analysis-v1` prompt and strict process schema.
- The model returned 3 objects, 5 states, and 4 transitions. Deterministic process-reference validation passed.
- Usage: 5,594 input tokens and 1,084 output tokens. At the official standard rates ($1.25/M input, $4.25/M output), estimated text-token cost is about **$0.0116**; this is an estimate, not a billing-console measurement. Source: [Meta Model API pricing](https://dev.meta.ai/docs/pricing-rate-limits).
- Process JSON: `/private/tmp/showme-stock-clips-2026-10-27/burstcube-process.json`.
- The first attempt used the system Python and stopped locally because the optional OpenAI client was absent. A second local attempt hit an existing partial output directory. Neither reached the API. The subsequent run used the repository virtual environment and completed once. A sandbox DNS failure was also resolved by running that single inference with network access; no blind model retries were made.

## What Muse observed

The output represented one frame chassis, the operator, and the blue work table. Its sequence was: present the frame, rotate it to show sides, lower it, place it on the table, and adjust its position. Its uncertainty section correctly said the functional identity and whether this was assembly, inspection, or staging could not be established, and no fastening/tool use was confirmed.

The timestamp intervals for the four transitions were inside the clip and visually plausible when compared with the locally sampled frames. That is a manual spot-check, not frame-level ground-truth scoring.

## Interpretation

This shows that the upload path, structured process extraction, timestamped evidence fields, and local referential validation can work on an additional public video. It does **not** show that SHOWME learned an assembly procedure, distinguished a correct attempt from a mistake, handled a different camera/arrangement, grounded objects with SAM, or recognized recovery. The clip is a staged handling sequence with one operator, not the controlled expert/learner set.

Next P0 evidence still requires a small, repeatable hands-only task recorded as separate expert, correct learner, mistake, and recovery clips. Keep the human-authored labels separate from model inputs.

## Same-clip observation plumbing check

The generated process was then supplied to `observe-video` along with the **same source clip**. Muse returned 7 timestamped events, 0 divergences, and `no_divergence_observed`; the CLI's observation checks passed. The events matched the presented/rotated/lowered/placed/adjusted sequence in the source. The output contained no uncertainties, despite the process-learning pass having explicitly recorded uncertainty about the frame's function. This is a useful reminder that the observation output can omit uncertainty and should not be treated as calibrated merely because schema validation passes.

Usage for this call was 6,421 input tokens and 672 output tokens. Estimated standard token cost is about **$0.0109**. Combined with process learning, the two successful calls used 12,015 input and 1,756 output tokens, or about **$0.0225** estimated at the rates above.

This is a same-video replay, not a learner transfer test. The zero-divergence result is expected and says nothing about sensitivity to mistakes, changed object positions, a new camera view, or recovery.
