# Implementation progress

## Phase 1: capability smoke test

- [x] Generate 18-second wholly synthetic video, movement, partial occlusion, fake plate, printed/spoken fake number.
- [x] Real SAM image and video requests; decoded temporal masks and explicit frame geometry.
- [x] Real Voice request and turn timestamps; record incorrect digits as failure.
- [x] Real Spark contextual localization.
- [x] Render playable visual/audio-redacted MP4.
- [x] Inspect exported pixels/audio without original findings or answer key in prompts.
- [x] Detect deliberately omitted printed number.
- [x] Preserve failed single-digit repair; verifier rejects it.
- [x] Repair whole observed field with optical flow; re-render and inspect three frames.
- [x] Inspect 180 decoded frames and muted audio; save receipt, costs and limitations.

Result: viable constrained smoke slice, **not full P0**. SAM concept plate detection failed. Voice exact digits failed. Source was composited, not a real-camera clip. Final model review sampled three frames. No broad recall claims.

## Next vertical slice

- [ ] Refactor scripts into reusable policy-driven pipeline and persistent local jobs.
- [ ] Add complete output sampling/OCR and an independent detector; distinguish seeded misses from natural misses.
- [ ] Evaluate additional synthetic clips, exposures, occlusions and negative controls; precision/recall and residual rate with sample sizes.
- [ ] Add atomic job/call bookkeeping, timeout/error handling, general audio/video validation and timestamp preservation beyond this fixed-FPS fixture.
- [x] Expose real create/reviewed-timeline-render/download HTTP path and thin Python SDK; tested against live loopback server.
- [ ] Wire automatic detection, privacy verification and targeted repair into those job routes.
- [ ] Only then build reference interface and submission demo.

Invariant: verifier reads exported media; it must never accept protector metadata or evaluation labels as evidence that content is safe. Same-family model review can share failure modes. Record uncertain intervals and require human review.

## API slice evidence

Eight tests pass. `artifacts/api-roundtrip.json` records the real SDK → HTTP → engine → downloaded 180-frame MP4 roundtrip. This replay uses saved real-inference geometry, not fresh model inference. Receipts explicitly say automatic detection and privacy verification were not run. No additional model charges. Atomic manifests and per-job lock files prevent simultaneous mutation; interrupted-process recovery remains manual.
