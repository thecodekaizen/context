# Contribution review — October 28

## Decision

The current claim of improved calibration from the specialized investigator fails its predeclared local comparison. Do not promote it as a proven scientific advance or a submission-ready winning capability.

## What is established

- Bounded executable thermal models, numerical fitting, strict model-output validation and persistent experiment reservations work.
- The live Meta controller can stage a supplied candidate, reject it on new simulated input, stage another and obtain support on another input. This was shown after development amendments with a deliberately restricted initial family.
- Predictions and measurements are separate, and offline checks reproduce scores and evidence/budget consistency.

## What the fair test found

Both Meta policies started with all three supplied families and identical initial measurements, rather than a known-wrong initial family. Ten paired simulated cases, seven-action ceilings and nine-fit ceilings were frozen before execution. A schema-availability failure required a documented amendment and new instances; all original failures are retained.

| Method | Median RMSE °C |
|---|---:|
| Fixed numerical BIC | 0.005194 |
| Numerical disagreement/BIC | 0.006903 |
| Direct Meta | 0.006682 |
| Investigator Meta | 0.006682 |

The 20% error-improvement gate fails. Investigator and direct Meta tie in every pair. All Meta final models equal the shared initial numerical calibration. Twelve of twenty Meta controllers reach the call cap without explicitly stopping. The known-family task does not show a need for the specialized investigation policy.

## Limits

Five shared parameter seeds generate ten related scenarios. Intervals are descriptive, not broad proof. One pre-existing held input and simulation-only data cannot establish hardware transfer. The intended real-user demand and industrial benefit were not validated. Both Meta variants share persistence/tools and differ only in instructions, so this is a policy ablation, not comparison against an independent agent architecture.

## Evidence and cost

`experiments/thermal-investigator/results/unrestricted-paired-v2-2026-10-28/` contains the frozen protocol, all forty corrected case records, raw provider responses, score report, offline audit and contribution review JSON. Version 1 preserves forty earlier records, including all failed Meta executions. Corrected comparison: 146 calls, estimated $2.1520365. Original failed batch: 27 calls, estimated $0.2752355. Combined estimate $2.427272; no automatic retries. Estimates are not confirmed account billing balances.

## Delivery consequence

The integration gate passes; the comparative contribution gate fails on the current bounded task. Do not continue a UI merely to imply the contribution is proven. Stop paid prompt-only variants here. Reuse the engineering infrastructure, but do not declare a new direction or a new positive scientific claim without a concrete capability, user problem and falsifiable comparison. The user requested proof; a negative result must remain a negative result.
