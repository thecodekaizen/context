# Meta capabilities — checked 28 October 2026

Labels: **documented** means official documentation; **observed** means our saved real API response; **unverified** means not established. Latencies are individual requests, not service guarantees. Standard mode only; no contributor variants.

## SAM

- Exact ID: `sam-3.1`; `POST https://api.meta.ai/v1/responses`.
- Request: Responses message with `input_text` naming one concept, and `input_image.image_url` or `input_video.file_id`. Video first uploads to `/v1/files` with `purpose=user_data`. Spatial prompts use source pixel coordinates, for example `<20f>7<|point;x=696;y=270;w=960;h=540|>`.
- Stream contains frame/object-indexed boxes and encoded masks. We use official `meta-sam-parser==0.1.0`, require completed outcome, decode masks and normalize boxes. Frame order is not necessarily chronological for bidirectional propagation. Confidence remains null.
- Documented: MP4/MOV using supported codecs; up to 15,000 frames and 16 objects per video frame. General Files upload ceiling is 1 GiB; a distinct SAM-specific byte ceiling was not established. Full occlusion identity recovery is not guaranteed.
- Observed: one face region and decoded mask in all 180 frames. Plate concept prompt returned zero matches in both image and video. Spark-seeded plate tracking returned 180 regions and decoded masks. A phone-field point segmented one digit, so this approach was rejected for whole-field repair.
- Latency and provisional frame-based costs are in `calls.json`. Video request estimate: 180 input frames × $0.0002 = $0.036; provider-billed frame usage has not been reconciled. Image: $0.0025.

Sources: [prompts](https://dev.meta.ai/docs/sam/segmenting), [parser](https://dev.meta.ai/docs/sam/client-libraries), [wire format](https://dev.meta.ai/docs/sam/reading-segmentation), [files](https://dev.meta.ai/docs/file-handling).

## Voice

- Exact ID: `muse-voice-transcribe-1.0`; `POST https://api.meta.ai/v1/asr/transcribe`.
- Multipart parts: `request` JSON with `mode=ENDPOINTING`, model, `audioEncoding=WAV`, `languageBias=[English]`; and `audio` WAV. Bearer authentication.
- Response: transcript, audioDurationMs, sessionId, turns containing turnId/startMs/endMs/transcript. Turn timestamps only; no word timestamps or confidence scores.
- Documented inputs: mono 16-bit PCM WAV at 16 or 24 kHz, request up to 32 MB and audio up to ten minutes. Code switching is documented but untested here.
- Observed: speech turns returned, but spoken `202-555-0146` became `55460146`. Exact-number recognition therefore failed. Redactor conservatively mutes the full detected speech envelope plus 500 ms padding, rather than relying on individual digits. Exported-audio transcription was empty; local audio inspection independently measured zero amplitude throughout the known speech interval.
- Price: $0.18/audio hour; 18 seconds estimated $0.0009. Per-call observed latency is recorded.

Source: [speech to text](https://dev.meta.ai/docs/speech-to-text).

## Spark

- Exact ID: `muse-spark-1.3`; `POST https://api.meta.ai/v1/responses`.
- Request: `input_text` and JPEG data URL `input_image`; structured JSON schema response via `text.format`. Saved scripts contain the exact schemas. No tools or web search requested.
- Observed: classified and localized face, fake plate and printed number. Fresh exported-frame review found the omitted number; another fresh review rejected a repair covering only one digit. Final review inspected actual exported frames at 2, 7.5 and 16 seconds and reported no exposures in those samples.
- This is a second pass on output pixels, using the same model family: independent of protector metadata, not independent of all correlated model errors. OCR and separate visual detector audits remain unimplemented.
- Generic inline media ceiling documented as 50 MB; specific image count/size limits were not exhaustively tested. Video-native Spark ingestion is not used in this experiment.
- Price: $1.25/M input tokens, $4.25/M output, $0.15/M cached input. Ledger retains actual token usage and estimates; dashboard billing is not reconciled.

Sources: [image understanding](https://dev.meta.ai/docs/image-understanding), [pricing](https://dev.meta.ai/docs/pricing-rate-limits).

## Fixture generation only

`muse-image-1.0`, `/v1/images/generations`, generated a fictional portrait from text with external tools disabled. Cost $0.01. This is fixture preparation, not a claimed engine capability. Synthetic speech was generated locally with macOS Samantha. No real person's media was uploaded.
