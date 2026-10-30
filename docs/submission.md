# CONTEXT — inspect what the edit left out

Working submission draft, updated October 30, 2026. Not submitted. Existing video
and release artifacts predate current validation and must be updated before use.

## Product

CONTEXT is a deterministic-first evidence workstation for engineering and DevRel teams to audit technical tutorials, software benchmarks, and product demos before publication. When an editor tightens a raw recording into a marketing highlight, cuts can inadvertently excise vital technical caveats (such as cold-start setup exclusions, warmup flags, or hardware specifications). Given an edited highlight alongside the raw recording (or a candidate from a registered technical catalog), CONTEXT exposes grounded internal omissions and measures spatial crop bounds. Synchronized dual players, millisecond timestamps, and media fingerprints let reviewers inspect the evidence before publishing. Missing footage alone is not evidence of deceptive intent.

## What Meta contributes

Muse Spark 1.2 reviews only bounded excerpts around measured internal omissions, with three higher-resolution timed 720p frames per clip to preserve interface text. It produces cited observations, potential interpretive effects, and explicit uncertainty. Responses referencing clips or times outside the bounded window are rejected; this does not verify semantic correctness. No correspondence means no model review request. Inconclusive outcomes are preserved honestly.

SAM 3.1 is an experimental segmentation component evaluated separately. Its 10-case chart-bar gate passes on saved-response replay, but a live test on the cache conditions panel returned zero masks (failed). Operational margin shading and calipers are computed strictly by deterministic OpenCV geometry; they are not attributed to SAM. CONTEXT does not claim the open-weight prize, as Muse Spark is accessed via the hosted Meta Model API.

## Demonstrated case

An explicitly authored Python cache demonstration displays actual local timings.
Its source qualification says warm cache only, cold-start setup excluded, and no
end-to-end speedup claim. A controlled temporal edit removes source seconds 6–10;
a separate crop removes the right-side panel.

Without a supplied source ID or caption, catalog lookup selects the registered
source. Audio matching finds the exact 6–10 s deletion at edit 6 s (visual alignment alone returned `insufficient_evidence`). Crop
geometry recovers the exact retained 960×720 region of a 1280×720 source, with
25% area removed. The byte-identical control produces no omission or model call.
The soundtrack is a synthetic diagnostic signal; this is authored demonstration
media, not independent field validation. Visual temporal coverage on the edits is
zero, so acoustic success must not be represented as visual authentication.

The Muse response is a saved recording, not re-run. The initial video-only Muse review missed the qualification and called the edit
harmless. Adding bounded timed frames allowed Muse to read the qualification and
explain its possible significance, while remaining inconclusive about changed
meaning. Both results are retained. No verified materiality claim is made.

## Evaluation

Frozen execution-v1: 30 controlled edits across three authored benchmark sources, 12 positive cases containing 15 labeled omission intervals, and 18 benign controls. Latest recheck: 15/15 intervals recovered, 0.0 s mean boundary error, 0/18 benign omission alarms. By the rule of three, 0/18 benign alarms bounds the true false-alarm rate below ~16.7% on this scripted benchmark suite. This measures deterministic deletion detection on scripted edits, not noisy real-world recordings, broad general-video recall, or deceptive intent. The separate cache qualification case is maintained outside the frozen benchmark.

Evaluation edits are scripted cuts of authored recordings; no result is claimed
for natural footage. Catalog matching is bounded local
candidate discovery, not internet-wide reverse video search.

## Submission readiness

The consequential-edit hero remains under validation. SAM panel segmentation and
independent semantic-effect accuracy are unresolved. Record authentic builder
narration, re-render the demonstration from the current script, and check authenticated
portal requirements before submission. No final rule acceptance or publication
has been performed by the agent.

Evidence and reproducible commands: [hero-validation.md](hero-validation.md),
[model-card.md](model-card.md), [source-discovery.md](source-discovery.md),
[demo-script.md](demo-script.md).
