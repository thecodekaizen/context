# CONTEXT
### See the whole story.

A local video evidence workstation for the Meta Global AI Developer Hackathon 2026.
Compare a published edit with its original recording, reconstruct the source
sequence, and click an omission to watch the missing footage.

## Run

Prerequisites: Python 3.12+ with compatible NumPy wheels, Node 20.19+ or 22.12+,
FFmpeg and FFprobe on PATH. This checkout was tested with Python 3.15 and Node 24.

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
npm ci --prefix web
npm run build --prefix web
.venv/bin/uvicorn context_core.api:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Select both videos and **Trace the edit**, or click
**Try generated case**. The demo creates real FFmpeg footage and independently
cuts seconds 4–8 out of its source; the inference receives only the video files.
Click **Reveal missing context** to hear/watch the original interval. Linked
playback follows matches and jumps across cuts; reveal switches to independent
source playback and stops at the interval boundary. The original is muted during
linked playback to avoid overlapping audio; unmute it when inspecting context.

For frontend development, run `npm run dev --prefix web` alongside the API.
The Vite server proxies `/api` to port 8000. Rebuild for production changes.

## Verify

```sh
.venv/bin/pytest -q
npm run build --prefix web
cd web
npx playwright install chromium
npx playwright test
```

12 backend tests cover copy, trim, omission, reordering, repetition,
rescaling/recompression, unknown and ambiguous static sources, invalid media,
real multipart uploads, persisted evidence, and HTTP range playback.
Two Chromium tests exercise the real generated analysis, source reveal,
evidence download, browser errors and mobile overflow. The API must be running.

## Evidence engine

`backend/context_core/media.py` probes duration, codec, resolution and audio;
FFmpeg decodes timestamped 4 Hz RGB samples reduced to 24×16 spatial features.
`alignment.py` compares sampled frames, rejects poor or temporally ambiguous
matches, groups continuous correspondences, and detects uncovered source
intervals, backward chronology, and repeated source spans. Source and edit
SHA-256 hashes anchor each saved report. JSON includes sampling method,
threshold, confidence (a similarity score, **not** a calibrated probability),
segments, findings and limitations. Boundary tolerance is ±0.5 seconds.

The CLI can compare an edit against one or several provided local sources:

```sh
PYTHONPATH=backend .venv/bin/python -m context_core data/demo/edited.mp4 data/demo/original.mp4 --output /tmp/context-evidence.json
```

Multiple sources produce candidates ranked by coverage; this is a local source
collection comparison, not internet-wide discovery. Each candidate is decoded
again; caching and collection indexing remain future work.

## Meta status

Official API docs were verified on October 29, 2026; see
[verification notes](docs/meta-verification.md). An optional, validated
`meta.interpret()` adapter targets Muse Spark 1.3 on the documented Responses API.
It is not exposed in the UI and has **not** completed live inference: no
`MODEL_API_KEY` is configured. The deterministic MVP does not require a key.
The adapter sends alignment metadata only, so it cannot infer scene semantics.
Multimodal interpretation with timestamped video/audio evidence remains the
next integration milestone; this is not yet a submission-ready Meta AI demo.

## Scope and limitations

- Local trusted workstation, no authentication; bind to loopback only.
- Up to 10 minutes and 200 MB per upload; one analysis at a time per process.
- Visual sequence evidence only. No transcription, factual verdict, speaker
  intent inference, or deepfake detection. Omission alone is not deception.
- Static/repeated-looking scenes are rejected conservatively. Heavy cropping,
  overlays, speed changes, color shifts, and unrelated lookalike footage need
  stronger feature matching and broader real-world evaluation.
- Tests use synthetic moving video; results are not real-world accuracy claims.
- Uploads and evidence persist under ignored `data/`; remove them manually when
  no longer needed. Videos are served with byte ranges. JSON is downloadable.
- FFmpeg invocations use argument lists, timeouts and duration limits. This MVP
  does not isolate malicious media decoders; do not expose it as a public service.

Deadline: November 4, 2026, 9 PM ET (November 5, 7:30 AM IST).
