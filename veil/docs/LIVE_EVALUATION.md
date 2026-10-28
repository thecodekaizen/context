# Live pipeline evaluation — 28 October 2026

One approved composited 18-second synthetic clip, three development runs. These are iterative engineering tests on the same fixture, not independent benchmark samples or a held-out evaluation. No real-person media or fixture labels entered inference.

## Observed sequence

| Run | Observation | Outcome |
| --- | --- | --- |
| live-pipeline-001 | Source detection/render succeeded. Spark output audit used normalized-looking coordinates despite pixel request. Adapter rejected out-of-range boxes. | Failed audit preserved; no invalid repair attempted. 5 model requests, estimated $0.08397 including reconstructed failed-response token usage. |
| live-pipeline-002 | Explicit normalized-coordinate schema fixed the contract. Verifier found seeded phone omission and natural plate-character segmentation miss. Repair initially dropped a plate fragment; another repair passed sample audit but lost tracking and blacked out 109/180 frames. | Degraded result, not accepted as a useful output. 10 model requests total, estimated $0.09859. |
| live-pipeline-003 | Whole-box SAM plate seeding replaced character point seeding. Independent local OCR and Spark found deliberately omitted phone. Whole-field repair followed by fresh output audit. | No exposure observed in 3 output samples; full-frame fixture-region/audio checks below. 8 requests, estimated $0.09069. |

Additional estimated API cost across these development runs: **$0.27325**. Costs are not reconciled billing. Earlier Phase 1 smoke cost remains separate. No automatic request retries. All runs and failed outputs are preserved; a privacy audit reporting no exposure does not override degraded utility.

## Latest run measurements

- Output decodes all 180 frames; H.264 video and AAC audio.
- Visible plate rectangle black-pixel coverage: minimum 1.0 across all fixture frames. Known gray occluder pixels are excluded in this evaluation-only metric. Full-rectangle minimum remains 0.5348 because it includes that occluder.
- Printed-digit rectangle black-pixel coverage: minimum 1.0 across all 180 frames.
- Audio samples during known synthetic spoken-number interval: RMS 0, max absolute amplitude 0.
- Source duration 18.000 s; rendered container 18.005 s (video duration 18.000 s). Do not claim bit-identical container timing.
- Near-full-frame blackouts: 0/180 (heuristic: over 95% black pixels).
- Output audit: frames at 2000, 7600 and 16000 ms; no exposures reported. Fresh exported-audio transcript empty. Local macOS OCR completed on those samples, with no phone-like sequences found.
- Same local OCR independently found the omitted phone in the initial export. It receives exported images, not source findings or expected values. Generic numeric pattern classification can produce false positives.

## Limits

This is **one synthetic fixture**, not a real-camera test or evidence of general recall, precision, plate accuracy or code-switching support. Source/output sampling can miss short exposures. The current protector tracks one plate and one printed-number field; separate moving objects need stronger association. Local OCR is macOS-specific and phone-pattern based. Voice can misread digits. Face boxes were inspected but no pixel-accurate face recall ground truth exists. No zero-leak guarantee.

## Evidence

`artifacts/live-pipeline-003/` contains initial/final MP4s, source-derived geometry, raw provider responses, independent OCR results, revision-bound audits, call ledger, receipt and evaluation-only coverage checks. Runs 001/002 retain failure evidence. `artifacts/live-results.json` indexes the runs.
