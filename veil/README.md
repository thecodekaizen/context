# VEIL

> **Latest core integration:** the API now performs real Meta detection, redaction, sampled export auditing and targeted repair. The historical limitations below describe the earlier rendering-only slice. Read the current [API contract](docs/PIPELINE_API.md) and [live evaluation](docs/LIVE_EVALUATION.md). [Play the latest API-produced MP4](artifacts/live-pipeline-003/final-export.mp4). The latest controlled run used 8 real requests (estimated $0.09069); no exposure was reported in three output samples, and all 180 fixture frames passed visible plate/digit coverage checks with no near-full-frame blackouts. This is one synthetic clip, not a general accuracy or zero-leak claim. Current dev port: 8019.

**Detect. Redact. Verify.**

VEIL is an embeddable video privacy engine. It identifies sensitive visual and spoken information, renders redactions, inspects the exported file and repairs detected residual exposures. Automated checks do not guarantee that a video has no leaks.

## Current result: a real 18-second export

[Play the corrected MP4](artifacts/smoke-001/protected.mp4) · [Original synthetic clip](artifacts/smoke-001/input.mp4) · [Results](artifacts/smoke-results.json) · [Receipt](artifacts/smoke-001/receipt.json)

![Corrected export at 7.5 seconds](artifacts/smoke-001/protected-7500.jpg)

Real Meta requests tracked a fictional face and a fake plate. Voice returned speech timestamps; FFmpeg muted the spoken number. Spark inspected the first export and found an unprotected printed number. The first repair covered one digit and failed its audit. A full-field repair then passed three sampled-frame reviews. Local evaluation checked all 180 frames for the fixture's visible plate and printed-digit cover regions and checked the audio samples.

**Limitations:** one composited fixture; no real-camera benchmark, precision/recall study, OCR audit, general automatic API processing yet. Plate concept detection failed and required Spark localization. Voice misread the number, so audio muting is deliberately broad. Face masks were decoded but rendering uses padded boxes, not contour-exact masks. Final review sampled three frames. These results are not a privacy guarantee.

## Run local checks without model charges

Requires Python 3.12+, FFmpeg and ffprobe on PATH. The fixture generator additionally needs macOS `say`.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_media.py --root artifacts/smoke-001
```

## Run the bounded API experiment

Set `MODEL_API_KEY` in a local uncommitted `.env`. Scripts also accept `--env-file`. Only use synthetic or explicitly consented media. Fresh output directories are required: ledgers refuse duplicate calls and automatic retries are disabled. Do not delete the archived ledger to rerun it.

The recorded sequence was: `generate_face.py` → `make_synthetic_clip.py` → `smoke_models.py` → `seed_plate.py` → `render_smoke.py` → `inspect_export.py` → `repair_smoke.py` (preserved failed repair) → `repair_field.py` (corrected export) → `check_media.py`. Each script accepts `--help`; generation uses `--output`, remaining stages use `--root`. Run scripts with `PYTHONPATH=src` or after editable installation. This is a staged experiment harness, not yet a general one-command pipeline.

Full request details, formats, restrictions, latency and cost evidence: [Model capabilities](docs/MODEL_CAPABILITIES.md). Product scope: [Product](docs/PRODUCT.md). Progress: [Implementation](docs/IMPLEMENTATION.md).

## Data handling

Local artifacts contain only synthetic imagery, fake identifiers and synthetic speech. Meta receives the media identified in each call ledger. Original detection results and evaluation truth are excluded from exported-frame audit prompts. Uploaded files are deleted after use where supported; cleanup records are retained. Files remain subject to Meta's service policies; this is not a fully local pipeline or a zero-retention claim. Never commit credentials or actual personal data.

## Use the local API and Python SDK

The API currently renders a **client-supplied reviewed timeline**. It does not yet run automatic detection or a privacy audit. Media decoding checks are identified separately in the receipt. Bind to loopback only; this prototype has no authentication and is not intended for public hosting.

```sh
.venv/bin/python -m uvicorn veil.api.app:create_app --factory --host 127.0.0.1 --port 8018
# In another terminal, from this directory:
.venv/bin/python scripts/api_roundtrip.py
```

The roundtrip uses the archived synthetic clip and saved real-inference geometry, combines the full-field repair, and produces `artifacts/api-export.mp4` and `artifacts/api-roundtrip.json`. It makes zero model calls. Live API docs: `http://127.0.0.1:8018/docs`.

```python
from veil import VeilClient

with VeilClient(base_url="http://127.0.0.1:8018") as client:
    job = client.create_job("sample.mp4")
    # timeline is validated, frame-aligned geometry reviewed by the caller.
    client.process(job["id"], timeline)
    receipt = client.receipt(job["id"])
    client.download(job["id"], "redacted.mp4")
```

Routes: create/read job, POST reviewed timeline to `/v1/jobs/{id}/redact`, read findings/receipt, and download `/v1/jobs/{id}/export`. No `/verify` route is claimed yet. Jobs persist under ignored `artifacts/private/jobs`; processing is synchronous and guarded by per-job filesystem locks. After an interrupted process, inspect the job before manually removing a stale `.lock`. Current input limits: 100 MiB, 60 seconds, 1080p, audio required. Timing support remains constrained to constant-frame-rate clips; the frame-rate metadata check is a rejection heuristic, not an exhaustive VFR validator.

## Build the reference demonstration

Frontend ownership, visual direction, exact current API contracts, recorded/live mode separation and acceptance criteria are in [Antigravity handoff](../ANTIGRAVITY_VEIL.md). The frontend lives in `veil/web/` relative to repository root. GitHub repository: https://github.com/thecodekaizen/veil. Local checkout: `/Users/thecodekaizen/Code/Projects/hackathons/veil`. Historical experiments remain preserved.
