# Additional-scene verification protocol — frozen before live calls

Scope: exported-media verifier development test, not a full protector benchmark or held-out generalization claim. Three deterministic 8-second 960×540, 12 fps synthetic candidate exports. Each is an actual H.264/AAC MP4. Source assets reuse the previously generated fictional portrait and synthetic speech. No real-person data.

Cases (opaque filenames are used for inference):

1. Persistent exposures: moving fictional portrait, drawn vehicle with fake `TEST 0287` plate, printed `202-555-0189`; synthetic voice says `202-555-0146` beginning at 1 second. Brief partial occlusion of the plate around 4.2–4.6 seconds. Four positive category-events: face, plate, visible phone, spoken phone.
2. Brief exposure: otherwise ordinary scene; printed fake phone only at frames 24–26, i.e. 2000–2250 ms. Silent audio. One positive category-event.
3. Negative: ordinary scene with non-sensitive short labels/numbers and silent audio; no face, plate or phone. No positive events.

Baseline: unchanged verifier, three visual samples plus exported-audio transcription and OCR on those same three samples. Up to two real Meta inference requests per clip (six total), no automatic retries. Errors remain failures. No GT, category labels, expected outputs, omitted intervals or case descriptions are sent to models. Cloud transfers contain only the synthetic candidate export's three frames and extracted audio.

Comparison: independent local OCR at a generic 250 ms cadence plus endpoints on the exact same MP4s. No additional cloud inference. Keep baseline outputs unchanged. This deliberately tests an anticipated sampling blind spot; it is not a blind estimate of average-world recall. No post-result movement of exposure times.

Evaluation-only answer keys remain outside inference work directories. Match a visual observation to an event by category and an observation timestamp inside the known event interval. Spoken-phone events use overlap with reported speech interval. Report detected/total positive category-events, negative-clip false alarms, observed sampled frames, latency and estimated API cost. Category-event recall is not per-pixel localization accuracy or a general precision estimate. Duplicate observations within one event count once. Report unexpected-category findings and model failures separately. Sample size: five positives and one negative clip.

Stop condition: six baseline model requests. Do not rerun failed requests or tune prompts on these cases. If denser OCR improves detection, retain both results and integrate that bounded sampling improvement with regression tests. This does not establish recall for shorter-than-cadence exposures, real-camera footage or additional object classes. No zero-leak claim.
