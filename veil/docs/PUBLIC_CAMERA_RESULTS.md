# Real-camera background, measured temporal repair

## Source and scope

Downloaded the actual 20,154,891-byte Pexels camera video **Computers on the Office Table**, by **Kampus Production**. [Source](https://www.pexels.com/video/computers-on-the-office-table-8347238/) · [Pexels license](https://www.pexels.com/license/).

An eight-second 360×640, 12 fps crop of this empty-office footage was reviewed locally, including all 96 frames in a contact sheet. Synthetic phone fields, the previously generated fictional portrait and synthetic speech were composited onto it. Only this privacy-safe hybrid was sent to Meta. No real stranger's face, phone or plate was used as a target. This is **not** a naturally occurring personal-data benchmark or real-plate test.

Protocol, footage and answer key were frozen in `e13f52f` before live calls. Keys stayed in `evaluation-only/`; inference, tracking and repair did not load them. The test has a moving phone field lasting 39 frames and a distinct brief field lasting 3 frames. The face source panel is not pixel-exact face ground truth.

## Paired repair result

Both repair plans consumed the exact same initial exported-file audit. Legacy repair propagated the earliest field across the full clip with optical-flow/full-frame fallback. New repair associated timestamped observations and limited their lifetimes.

| Measurement | Legacy repair | Presence-bounded repair |
| --- | ---: | ---: |
| Primary phone frames with complete rectangle cover | 39/39 | 39/39 |
| Brief second phone frames with complete rectangle cover | 0/3 | 3/3 |
| Near-full-frame blackouts | 14/96 | 0/96 |
| Planned phone mask area outside true phone-presence intervals | 94.99% | 14.44% |
| Known spoken-number interval maximum audio amplitude | 0 | 0 |

The planned-area metric is a diagnostic, not an independent false-positive rate; it sums track areas and can double-count overlaps. Output rectangle coverage, blackouts and audio amplitude were checked from actual MP4 bytes. Black-pixel coverage does not prove zero residual information.

The controlled loop used **7 real Meta requests**, approximately **$0.0294055**, and 42.43 seconds including both local comparison renders. The output verifier observed both deliberately unprotected numbers, new repair rendered them, and fresh verification reported no exposure in the model/OCR samples. API costs are estimates, not reconciled billing.

## Normal protection check

A separate fixed control used the same unchanged input with **no seeded omission**. Source OCR formed bounded phone tracklets before rendering; no repair was needed. It used **5 real requests**, approximately **$0.02641275**, and 32.25 seconds. Independent all-frame evaluation found complete rectangle cover in **42/42 sensitive phone frames**, zero near-full-frame blackouts and silence over the known spoken-number interval. Planned phone mask area outside phone-presence intervals was 15.01%.

Combined test budget: **12 actual requests**, estimated **$0.05581825**, no automatic retries. The normal check was added after the paired result on the same development case; it was not a separate preregistered sample and is not another independent benchmark sample.

## Algorithm

1. Use recognized phone digits to associate observations, preferring local OCR geometry over duplicate contextual boxes for that identifier.
2. Apply an image-plane spatial gate and split associations across time gaps over 500 ms. The gate is heuristic, not a calibrated probability or physical speed guarantee.
3. Estimate box-coordinate velocity as the median finite difference in pixels/second.
4. Build a conservative per-frame envelope from adjacent measured boxes; outside the first/last measurement, project velocity only within a 250 ms margin.
5. Keep separate field lifetimes and identifiers separate, rather than carrying one field through the full video. Cap tracklets at 64; fail rather than silently dropping overflow.
6. Re-inspect the exported pixels/audio. Audit evidence is tied to the current export hash/revision and remains sampled.

These are 2D image/time calculations. No arbitrary physics simulator or general motion guarantee is claimed. Rapid unobserved motion, OCR errors, identical-text objects, very brief exposures and long benign identifiers remain limitations. Unknown phone strings and non-phone residuals retain the conservative legacy fallback; its utility warnings remain visible.

## Evidence

- `artifacts/public-footage-001/challenge.mp4`: real background plus declared synthetic targets.
- `run/initial-export.mp4`: deliberate phone omissions for verifier challenge.
- `run/legacy-repair.mp4` and `run/final-export.mp4`: paired comparison.
- `normal-run/final-export.mp4`: ordinary automatic protection, no omission.
- `evaluation-only/results.json`: independent frame/audio measurements and limitations.
- `run/provider-evidence/`, `normal-run/provider-evidence/`: actual model responses, masks, observations, call ledgers, lifetimes and receipts.
- `usage-summary.json`: bounded costs.

The raw downloaded stock asset stays local; fetch it reproducibly with `scripts/fetch_public_footage.py`, which checks the recorded SHA-256 and caps download size. No model calls occur during download or fixture creation.

## Reproduce in a fresh directory

```sh
python scripts/fetch_public_footage.py --output artifacts/public-footage-002
python scripts/make_public_camera_challenge.py --root artifacts/public-footage-002
# Start API with MODEL_API_KEY and default request cap 12.
python scripts/run_public_camera.py --root artifacts/public-footage-002
# For the separate normal check, use VEIL_MAX_MODEL_CALLS=5 when starting its service.
python scripts/run_public_normal.py --root artifacts/public-footage-002
```

Run scripts deliberately; each refuses to overwrite an existing run. Live requests require cloud/media authorization. Store private jobs locally and never commit actual personal data. The local runners archive provider evidence automatically from the service storage; set VEIL_JOBS_DIR consistently if it differs from the default. Then run `python scripts/evaluate_public_camera.py --root artifacts/public-footage-002` for the all-frame comparison. One hybrid case does not establish general recall or a zero-leak guarantee.
