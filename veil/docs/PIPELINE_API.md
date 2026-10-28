# Live engine/API contract

The engine now exposes bounded real Meta detection, rendering, sampled export inspection and targeted repair. Bind locally; no authentication or hosted privacy guarantee is provided.

## Run

Install the Python package with test dependencies and FFmpeg/ffprobe available. Set `MODEL_API_KEY` in an uncommitted environment or `.env`. `VEIL_ENV_FILE` can select that file. Start from the repository's `veil/` directory:

```sh
python -m uvicorn veil.api.app:create_app --factory --host 127.0.0.1 --port 8019
```

`VEIL_JOBS_DIR` defaults to ignored `artifacts/private/jobs`. The service uses synchronous requests, per-job locks and atomic JSON manifests; no database/queue. A crash can leave a lock requiring manual investigation. Failed jobs are preserved and not retried automatically.

## Routes

1. `POST /v1/jobs`, multipart `video`: local upload, no inference.
2. `POST /v1/jobs/{id}/detect`: sampled Spark observations → SAM face tracking → Spark-seeded whole-box SAM plate tracking → local full-field phone tracking → Voice transcription → validated timeline. No fixture truth is loaded.
3. `POST /v1/jobs/{id}/redact`: omit body to render the detected timeline, or provide a reviewed Timeline JSON. Produces an actual MP4 and decoding receipt.
4. `POST /v1/jobs/{id}/verify`: inspect three frames decoded from **current exported MP4**, transcribe its extracted audio and run independent local OCR where available. It receives no original findings, omission flag or expected answers.
5. `POST /v1/jobs/{id}/repair`: use observed output exposures to track and cover whole-field envelopes; re-render. It invalidates the old audit and preserves the old export revision. Follow with `/verify`.
6. `GET /v1/jobs/{id}`, `/findings`, `/verification`, `/receipt`, `/export`: inspect state, evidence, receipt and download MP4.

Detect/verify/repair require explicit JSON:

```json
{"allow_cloud_transfer":true,"media_is_synthetic_or_consented":true}
```

For controlled tests only, detect also accepts `seed_omit_phone: true`. This omission is recorded in job metadata, never provided to verifier prompts. No browser-side model key or direct model calls. Local upload, render and download remain local; detect/verify send media to Meta and use credits. Repair is currently local but uses the same explicit authorization envelope for workflow clarity.

A job allows at most 12 inference requests; SDK retries are disabled. Files API upload/deletion are recorded separately. Logs preserve completed, invalid and failed responses. Token and frame-based costs are estimates, not billing reconciliation. Missing usage on a failed response is unknown, not free.

## Python SDK

```python
from veil import VeilClient

with VeilClient(base_url="http://127.0.0.1:8019") as client:
    result = client.protect(
        "synthetic.mp4", "redacted.mp4",
        allow_cloud_transfer=True,
        media_is_synthetic_or_consented=True,
        max_repairs=1,
    )
    print(result["verification"])
    print(result["receipt"])
```

This method runs the real pipeline; it does not promise the repair budget suffices. It returns remaining residuals and utility warnings. Explicit stage calls remain available via `create_job`, `cloud_action`, `process`, `verification`, `receipt` and `download`.

## Evidence semantics

- `no_exposure_observed_in_samples` means three sampled frames and the transcription/pattern checks found no exposure. It is not a whole-video safety verdict.
- `residual_observed` requires review/repair. `not_run`, failed and unavailable checks must remain visible.
- Audit report includes export SHA-256 and revision. A repair cannot use an audit for another revision/hash. The API invalidates verification after replacing video bytes.
- Model coordinates are explicitly requested in 0–1000 normalized space, validated and converted at the adapter boundary to source pixels. Invalid boxes stop processing.
- SAM can segment a character rather than a whole sensitive field. Whole-box plate seeding and a documented area-based whole-field fallback protect against that observed failure. The fallback threshold is a heuristic, not a calibrated probability.
- Repair keeps all same-category fragments in the earliest observed frame. The prototype tracks a single envelope per category; separate moving objects need stronger association.
- Tracking loss deliberately fails closed to a full-frame cover. Receipt `media_inspection.utility_status=excessive_masking` flags near-full-black output in over 10% of decoded frames. This is a review heuristic, not an automatic publication decision.

## Local OCR

The independent text signal uses macOS Vision through the included, fixed Swift helper. It reads only exported images, returns phone-like numeric patterns and source boxes, and makes no cloud requests. It requires macOS, `swiftc`, and access to the Vision service. First use compiles a local binary under ignored private storage. Other platforms report unavailable; compiler/runtime errors report failed. These states do not count as a passing independent check. General OCR and plate-specific text classification remain limited.

## Current limits

One synthetic clip has exercised the full pipeline; this is not a recall benchmark. Three-frame sampling misses short exposures. Voice may misread or omit digits. The service currently handles one plate and one printed-number field, plus SAM face tracks; no general scene coverage claim. Media acceptance is limited to short, small, constant-frame-rate MP4s with audio. VFR detection is currently a metadata heuristic. Model-family errors may be correlated. Never claim zero leaks.


## Dense independent audit update

The default verifier now retains three Spark samples while sampling local OCR every 250 ms plus endpoints (bounded to 512 frames, native batches of 32). `coverage` records model frame count, local OCR frame count and maximum OCR gap. `frames` can contain OCR-only observations outside Spark's timestamps; their `source` remains `macos-vision-ocr`. No continuous exposure interval is inferred from one frame. `sample_times_ms` remains Spark's sample list; `independent_ocr.sample_times_ms` gives OCR's separate scope.

If OCR fails or is unavailable and no known residual exists, status is `review_incomplete`, not a passing result. `check_status` and `checks_complete` expose the difference. Known residuals remain `residual_observed` even if OCR fails. Receipt `verification_scope` includes coverage/check statuses bound to the export hash/revision and is invalidated after repair. The SDK returns incomplete reviews for human handling; it does not certify them.

See VERIFIER_BENCHMARK.md: fixed three-clip comparison found 4/5 category-events with the sparse baseline and 5/5 after local augmentation, with zero alarms on one clean clip. Six real requests, estimated $0.0142505; no additional cloud calls for the dense comparison. This is an anticipated sampling test, not general recall or end-to-end repair validation on those new scenes.
