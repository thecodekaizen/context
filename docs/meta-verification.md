# Meta integration verification — 2026-10-29
Official references checked before implementation:
- https://dev.meta.ai/docs/quickstart
- https://dev.meta.ai/docs/models

Confirmed documented base URL https://api.meta.ai/v1, Responses POST /responses,
Bearer MODEL_API_KEY, model muse-spark-1.3, text output in message/output_text.
The catalog documents image/video/audio input; this MVP adapter intentionally sends
only measured alignment metadata. It cannot make content-level judgments.

Adapter: backend/context_core/meta.py. Optional, not invoked by default.
Live authentication, account model availability and actual inference are UNVERIFIED
until a key is supplied in the server environment. No fabricated model output.
Next integration milestone: bounded source clips with audio, timestamped model
citations validated against deterministic evidence, and credentialed integration tests.

## Multimodal integration follow-up
https://dev.meta.ai/docs/video-understanding checked October 29, 2026.
It documents Responses input_video with a public or base64 data video_url.
It also cautions that Muse Spark 1.3 audio quality may be degraded and uses
Muse Spark 1.2 for audio examples. The bounded-video adapter therefore selects
muse-spark-1.2 and sends MP4 clips with retained audio where present.

Current implementation exposes an explicit UI action, creates at most two clips,
validates the returned JSON and clip-local citations, converts citations to full
media timestamps, and saves interpretation separately from deterministic evidence.
No live Meta request has been made; MODEL_API_KEY remains unavailable. Mocked
request/response tests validate our code contract, not provider compatibility.
The earlier metadata-only adapter has been replaced by this bounded-video path.

## Credentialed smoke test — October 29, 2026
Loaded MODEL_API_KEY from CONTEXT's ignored .env, copied with user authorization
from THREAD's environment file. THREAD resolves to the existing VEIL directory;
no source project files were modified. Credential values were never printed.
GET /v1/models returned HTTP 200 and listed muse-spark-1.2.
The real local review endpoint generated source/edit MP4 excerpts and completed
an authenticated Muse Spark 1.2 request: HTTP 200, five observations, all returned
citations passed bounds validation. Result saved under ignored data/demo/.
This establishes live request compatibility, not semantic accuracy on real footage.
Earlier statements of unavailable credentials describe the prior development state.
