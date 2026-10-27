# SHOWME stock-video integration smoke

**Date:** 2026-10-27
**Result type:** API integration smoke only; not an evaluation of SHOWME's core capability

## Source and handling

Used the short `pingpong.mp4` public test clip referenced by Meta's official [SAM API basics cookbook](https://dev.meta.ai/docs/cookbook/sam-api-basics). The source video stayed under `/private/tmp`; derived frames, model inputs, and raw model outputs stayed under the ignored `.showme-runs/` folder and are not committed.

## Runs

1. `learn-video` uploaded a silent 720p-or-smaller copy to Muse Spark 1.3. The API returned a structurally valid candidate with 7 objects, 5 states, and 4 transitions; all cross-references and transition evidence intervals passed local checks.
2. `observe-video` used the same clip as both the demonstration and learner input. It returned 5 timestamped events, 0 divergences, and `no_divergence_observed`; local state-ID and timestamp checks passed.

## What this proves

- Meta video upload and Responses API calls work from the CLI.
- Structured outputs parse, and local process/observation validators accept this smoke output.
- Local preprocessing detects audio and creates a silent model-input copy.

## What this does not prove

The same stock clip was used twice, so this does not test transfer to another person, deliberate mistake detection, or recovery. The model also asserted that the ball travelled over the net while listing uncertainty about whether it crossed or hit the net. Structured JSON and valid timestamps do not guarantee semantic consistency. A controlled task recording and stronger claim checks are still required.

## API usage estimate

Muse Spark reported 3,822 input tokens and 1,893 output tokens across the two calls. Using the listed standard rates of $1.25 per million input tokens and $4.25 per million output tokens, the token-rate estimate is about **$0.0128** total. This is an estimate; verify the actual balance in Meta Billing. [Current pricing](https://dev.meta.ai/docs/pricing-rate-limits)
