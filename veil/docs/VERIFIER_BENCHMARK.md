# Additional-scene verifier result

Protocol and fixtures were committed as `67edcb3` before live inference. This is a targeted development test of an anticipated sampling blind spot, not a held-out model or general-accuracy benchmark.

## Cases and measurements

Three new 8-second, 12 fps composited exports: persistent face/plate/printed phone/spoken phone, one 250 ms printed-phone exposure, and one clean control containing short ordinary labels/numbers. The fictional portrait and synthetic voice are reused assets. Answer keys were loaded only by the evaluation script after inference; input hashes were checked unchanged.

| Case | Positive category-events | Original three-frame audit | Same cloud results + denser local OCR |
| --- | ---: | ---: | ---: |
| Persistent exposures | 4 | 4 detected | 4 detected |
| Brief phone exposure | 1 | 0 detected | 1 detected |
| Clean control | 0 | No false alarm | No false alarm |

The original audit sampled frames at 917, 3333 and 7083 ms. The brief exposure existed only at 2000–2250 ms. Independent local OCR sampled 33 frames per clip at a generic 250 ms cadence plus the final frame, and found the brief number at 2000 ms.

Six real Meta requests total: three Spark exported-frame reviews and three exported-audio Voice requests. Estimated cost **$0.0142505**, not reconciled billing. The denser comparison made **zero additional cloud calls**. Measured local OCR time was about 1.65–1.84 seconds per 8-second clip on this machine; no throughput guarantee. Sparse baseline outputs remain unchanged. Dense combined reports reuse those exact Spark/Voice results and are labeled as a local augmentation, not new cloud inference.

## Engineering change

The engine now keeps Spark's three-frame contextual review while running independent local OCR on a bounded 250 ms schedule. It records both coverage scopes. Frames seen only by OCR retain OCR provenance and their actual timestamps; no continuous leak interval is invented from a single observation. Failed or unavailable OCR yields `review_incomplete` when no other residual is known, rather than a passing review. The API receipt carries check status and sampling coverage for its exact export hash/revision.

Native OCR runs in batches of at most 32 frames. Sampling has a hard 512-frame cap and never silently reduces coverage to fit it. Very low-fps inputs cannot provide observations faster than their actual frames. More frequent OCR does not improve the face/plate model's temporal sampling.

## Limits and next evaluation

- Five category-events across two positive clips, one clean control. Report counts, not a general recall percentage.
- Category/time matches; no bounding-box accuracy or pixel-level face metric.
- This brief exposure was chosen to test the known blind spot; no claim of unseen-task generalization.
- Exposures shorter than cadence may still fall between OCR samples.
- Numeric-pattern classification can flag ordinary long identifiers; this negative control tested short labels only.
- Voice again misread exact digits; the test measures detection of a spoken phone-like event, not digit accuracy or precise word timing.
- Local OCR is macOS-specific; other platforms need a working independent adapter.
- This tests verification of candidate exports, **not end-to-end redaction/repair on these three new scenes**. Short-lived objects need presence-aware tracking before claiming useful automatic repair.
- No real-camera data or zero-leak guarantee.

Evidence: `artifacts/verifier-benchmark-001/evaluation-only/results.json`, baseline reports and call ledgers, `dense-ocr.json`, `dense-combined-report.json`, and timing records. Next tests should include shorter/misaligned exposures, long benign identifiers, multiple independent moving fields and independent temporal redaction evaluation.


## Reproduce intentionally

From the Python package directory, generate a **new** output root rather than replacing historical evidence:

```sh
python scripts/make_verifier_benchmark.py --output artifacts/verifier-benchmark-002
python scripts/run_verifier_benchmark.py --root artifacts/verifier-benchmark-002 --env-file .env
python scripts/compare_dense_verification.py --root artifacts/verifier-benchmark-002
python scripts/evaluate_verifier_benchmark.py --root artifacts/verifier-benchmark-002
```

Only the second command calls Meta (up to six requests). It explicitly selects the sparse-OCR baseline mode even though the production auditor now defaults to denser OCR. The remaining comparison is local only. The guard refuses to rerun a started baseline. The fixture generator requires the committed original portrait/speech assets and macOS font; independent OCR requires macOS Vision. These are development comparisons, not sealed benchmark scores.
