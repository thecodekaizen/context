# Public-camera hybrid experiment — freeze before live calls

Source: Pexels video 8347238, “Computers on the Office Table,” Kampus Production. Page: https://www.pexels.com/video/computers-on-the-office-table-8347238/ . License: https://www.pexels.com/license/ . Downloaded public asset SHA-256: `47c2ecc4a76533f84d95ed0f88703df7e282d3c23ab730b38511bf1424258264` (20,154,891 bytes). The source page describes an empty office; all 96 frames of the derived eight-second preview were visually inspected in a contact sheet, with no people or personal text observed. No public person's face or identifier is used as a privacy target.

This is real-camera **background footage with declared synthetic exposures**, not a real-person privacy benchmark. The fictional portrait and synthetic narration reuse approved fixture assets. Fake printed phone fields: one moving field in frames 15–53 (1250–4500 ms), another field in frames 75–77 (6250–6500 ms). Speech begins at 1000 ms. These intervals are evaluation keys only; do not send them to inference or tracking code.

Objective: verify a complete real model loop while fixing over-redaction caused by unbounded object lifetime. Use real Spark source observations, SAM face tracking and Voice transcription. Deliberately omit printed-phone protection to challenge the exported-media verifier. It must observe both fields without the answer key. Compare:

1. Legacy local repair: one initial phone field seed, optical flow propagated over the entire clip with full-frame fallback after loss.
2. Presence-bounded repair: associate actual OCR observations by recognized digits and spatial coherence, split at temporal gaps, render per-frame envelopes only within bounded observation neighborhoods.

Use the exact same fresh output-audit observations for both local repair plans. Do not provide truth boxes/times to either. The new algorithm's input is the actual independently observed output evidence. This is a targeted development case, not a held-out comparison or statistical improvement claim.

Budget: one real end-to-end test, at most 12 model requests, no automatic retries. Input is the approved hybrid clip. Record every call, upload and cleanup; no real-person media. Source detection, initial exported-file audit and post-repair audit must be separate. Preserve both legacy and new outputs.

Evaluate separately from inference: all-frame black coverage over known phone text rectangles; speech sample amplitude; decode count/duration; number of near-full-frame blackouts; fraction of planned mask area outside known phone existence intervals; recognition of both independent phone events in actual audit evidence; API cost/latency and utility warnings. The face panel is not pixel-exact facial ground truth. Report misses, uncertainty and broad masks honestly. No anonymity or zero-leak guarantee. Real plates are not tested by this fixture.
