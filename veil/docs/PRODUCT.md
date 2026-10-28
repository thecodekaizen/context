# Locked product: VEIL

Detect. Redact. Verify.

Video publishers can miss sensitive information that moves, appears briefly or is spoken. VEIL provides an API-first engine to detect privacy findings, apply time-aligned visual/audio redactions and inspect the actual exported file for remaining exposures. It repairs detected misses and produces a machine-readable receipt. It cannot certify zero leaks.

Input: short MP4 with audio, privacy policy, eventually manual regions/intervals.
Output: redacted MP4, frame-specific findings, audio intervals, scoped verification report and receipt.

P0: faces, plates, synthetic spoken phone; tracking; visual cover; audio mute; exported-file verification; deliberately missed redaction detected and repaired; receipt; HTTP API. Python SDK demonstrates integration. Core uses Python, Pydantic, OpenCV, FFmpeg and Meta adapters; local job files, no infrastructure services without demonstrated need.

P1 after P0: broad text/documents, Hinglish, manual adjustment, side-by-side preview and timeline. Current printed phone is an intentionally omitted verification challenge, not evidence that general text detection works.

P2 cut: real-time, plugins/mobile, accounts, billing, cloud storage, advanced tracking, optional open weights.

Internal submission target: 3 November 2026. Reference interface must consume the same API as SDK and never duplicate engine logic. Three-minute demo: synthetic exposures → real detection → actual redacted export → verifier catches miss → repair → measured evidence and integration.
