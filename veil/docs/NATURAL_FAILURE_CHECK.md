# Valid geometry is not privacy: local fault injection

28 October 2026. Core diagnostic on the existing `natural-surface-001` synthetic development clip, not a new independent sample or a six-clip benchmark.

## What ran

`run_surface_failure_check.py` intentionally shifts all supplied quads horizontally by 110 pixels and expands fixture-authored protective boxes so those wrong quads still satisfy the renderer's geometric containment checks. No inference receives ground truth. This is a seeded localization fault; it is not a naturally occurring measured tracking failure.

The unchanged renderer produces a mathematically valid but incorrectly located replacement. Independent macOS OCR reads every decoded exported frame and compares text with the planted original identifier/four-character fragments. When it observes a residual, this diagnostic rejects the candidate and renders the same input with the existing opaque renderer for the affected track. It checks that new MP4 independently.

## Results

- Candidate: 72 decoded frames, 72 timestamped residual observations. The renderer's valid transforms did NOT protect the original field. Candidate retained as `rejected-candidate.mp4`.
- Fallback: all 72 frames checked by exported-pixel OCR; no full original value or four-character fragment observed. This is scoped OCR evidence, not a zero-leak guarantee.
- Geometry and fallback boxes in this diagnostic are supplied fixture data, not model detections. Deliberately enlarged fallback is visually destructive and requires review; it is not counted as a natural-editing success.
- Zero model API calls and additional API cost. Latency and exact hashes are in `artifacts/natural-failure-001/results.json`.
- The reject/fallback controller is an experiment script, NOT an integrated natural-mode API behavior. Ordinary VEIL API still uses the established redaction path.

Viewed representative original/rejected/fallback frames at 0, 35 and 71. The rejected candidate visibly leaves original leading digits beside the displaced DEMO plate. The opaque fallback visibly hides a wider area. No independent human preference test has occurred.

## Reproduce

```
PYTHONPATH=src python scripts/run_surface_failure_check.py --root artifacts/natural-surface-001 --output artifacts/natural-failure-NEW --ocr-cache artifacts/private/ocr-cache
```

Requires existing fixture, FFmpeg and native macOS OCR. Refuses to overwrite outputs. Audit evidence is bound to exact rendered-file hashes and preserved separately from render decisions.

## Decision impact

VERIFIED: exported-file inspection detects a deliberately seeded leak that valid projective geometry failed to prevent; conservative re-rendering removes the tested original fragments.
FAILED: the seeded candidate's privacy requirement.
UNTESTED: six real/consented cases, natural visual acceptance, automatic source localization, reviewer preference and API integration. Today's natural-editing acceptance gate remains open. Keep this failure visible rather than increasing the count of successful examples.
