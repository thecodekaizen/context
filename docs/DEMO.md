# SHOWME demo

> **Product:** SHOWME turns demonstrations into understanding. Teach creates one process model; Do checks a learner's attempt against it; Simulate tests another step order using that same model.

This plan is for the Meta Global AI Developer Hackathon submission. It is a target, not a claim that every capability has passed evaluation. Use [`../design/flows/demo-flow.md`](../design/flows/demo-flow.md) for the gated three-minute script and current fallback.

## The story

“Tutorials can show you what to do. They can’t see what you’re doing.”

Show one physical task. SHOWME proposes a process model from an expert demonstration. A learner tries the task; SHOWME checks the recorded attempt, identifies any evidence-backed difference, and supports inspection. Then use the same model to test a different step order.

The two moments to earn are:

1. **SHOWME caught my mistake.** The report must identify the actual visible divergence and link to inspectable evidence.
2. **SHOWME showed what would happen instead.** Simulate must use the same reviewed process model and clearly label a procedural preview as distinct from physical simulation.

## Three-minute submission video

The submission video is limited to three minutes. Start with the real task, not an architecture diagram or a generic product tour. Show only functionality built during the hackathon and identify the pre-event repository foundation accurately.

Use the time-coded plan in [`../design/flows/demo-flow.md`](../design/flows/demo-flow.md). Keep the selected task, clips, evidence timestamps, and spoken claims consistent. If a capability gate fails, remove that claim from the cut or show the limitation plainly.

## Demo safety rules

- Keep the human-authored answer key separate from model inputs and public files.
- Use consented footage and assets with rights for processing and public release.
- Preserve original model outputs and compare them against independently recorded ground truth; do not edit away misses or false alarms.
- Label fixture behavior, model proposals, and unvalidated reports. One successful run is a prototype result, not a reliability claim.
- Never imply that SAM segmentation proves a process error, that a single clip proves a required order, or that the current procedural preview is physics simulation.

## Current fallback

If the matched physical-task evaluation is not ready, present the current app as an integration prototype. Show Teach’s proposed model and timestamped evidence, inspect a separate learner-video analysis as a model report, and use Simulate only as a procedural preview. State what remains unvalidated. Do not present the sample stacked-mount fixture as a learned LEGO task.

See [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md) for implementation status and [`LEGO_RECORDING_GUIDE.md`](LEGO_RECORDING_GUIDE.md) for the matched clip protocol.
