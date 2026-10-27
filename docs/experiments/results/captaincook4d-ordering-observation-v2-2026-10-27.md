# CaptainCook4D ordering-observation v2 — 2026-10-27

**Result: exploratory improvement on one normal control; P0 still fails.** This is not a capability claim.

## Question

After changing the process contract so one demonstration records observed order without turning it into a requirement, does the pipeline reduce false alarms on a separate normal attempt while retaining detection of the annotated order error?

## Protocol

Used the same local, rights-cleared CaptainCook4D Pan Fried Tofu crops as the prior smoke. Labels remained local and were not provided to Muse. The expert clip was relearned with process prompt v2; the learned process was then held fixed for both learner observations.

| Role | Clip | Ground truth |
|---|---|---|
| Learn | `clip-a2.mp4` (160.0 s) | Normal procedure |
| Control | `clip-b.mp4` (75.0 s) | Normal procedure |
| Error | `clip-c.mp4` (140.0 s) | Flip before removing pan from heat (annotated order error) |

All media, annotations, and raw model outputs stayed under `/private/tmp/showme-stock-clips-2026-10-27/` and are not committed.

## Results

- Learning returned 6 states and 5 evidence-backed transitions; local validation passed. It still omitted the critical remove-pan-from-heat-before-flipping event. The learned actions focused on moving the pan, handling tongs, turning cubes, and shaking the pan.
- The normal control produced 6 events, 0 divergences, and `no_divergence_observed`. In the previous smoke, a different 120-second expert crop and earlier observer prompt produced 2 divergences for the normal control, including an order-swap report.
- The annotated order-error clip produced 6 events, 0 divergences, and `no_divergence_observed`: the target error was missed again.

## Interpretation

The control result is consistent with fewer false alarms after the prompt/schema change, but this is not a clean ablation: the expert clip duration/content and the learned process changed along with the prompt. We cannot attribute the control improvement to the ordering-observation change alone.

The main failure remains. Muse did not learn the decisive event from the demonstration, so the observer had no reliable representation of the annotated violation to check. The new contract did not fix process extraction. The error run's “consistent” labels are not evidence of understanding; they conflict with the human annotation and show the current observer can confidently miss the target.

**P0 status: FAIL.** The stock cooking footage is useful for integration and failure analysis, not for the core proof. Do not proceed to UI, SAM overlays, or simulation on this evidence. Next experiment should use a short, human-recorded, visually discrete task with a small number of objects, a demonstrated invariant, and a deliberately wrong but recoverable state. Keep the same exact expert process fixed across normal, error, and recovery attempts.

## API usage

The three successful calls reported 100,291 input tokens and 4,354 output tokens. At the documented standard rates used by the earlier smoke estimate, this is approximately **$0.144**. Confirm the actual balance in Meta Billing. One earlier sandbox-blocked connection attempt returned before an API response and is excluded.

## Files

- Learned process: `/private/tmp/showme-stock-clips-2026-10-27/captaincook-runs/v2-run-a-network/process.json`
- Normal control: `/private/tmp/showme-stock-clips-2026-10-27/captaincook-runs/v2-run-b-network/observation.json`
- Annotated order error: `/private/tmp/showme-stock-clips-2026-10-27/captaincook-runs/v2-run-c-network/observation.json`
