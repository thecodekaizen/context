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
