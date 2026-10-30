# CONTEXT model and capability card — post-audit correction

CONTEXT is a bounded single-video investigation assistant, not a universal truth detector. Spark 1.2 interprets video/audio; Spark 1.3 searches the web and assesses claims against fetched text. Deterministic 4Hz RGB fingerprints and 2kHz audio correlation locate correspondences. Timestamp bounds and quote membership are checked, but do not independently prove semantic truth.

The primary pipeline now searches the official NASA catalog for at most four accessible candidates, filters explicit third-party rights notices, acquires small MP4 renditions under a per-candidate byte cap, and requires actual alignment. Local user-provided sources remain an explicit fallback. This is not unrestricted online-original retrieval. Audio-only matches remain labeled audio-only. Bounded source/edit review separates harmless_edit, meaning_changed and inconclusive; each non-inconclusive interpretation requires citations to both excerpts.

No general accuracy score is established. The audit verified 82 prior backend and six browser tests; post-audit tests/results are recorded separately in docs/sprint. Old 100% claim-precision and PRELUDE sensitivity figures were unsupported and are withdrawn. Development edits are not independent held-out benchmarks, and no EVID-Bench result is claimed.

PRELUDE remains experimental offline replay. Flow contours are motion regions, not validated vehicle detections. Relative region-area growth is not optical tau or metric time to collision. A model-selected cue within a prefix is retrospective, not a warning issued at that time. Failed/unverified inference cannot establish safe traffic. SAM, Muse Voice, VEIL export and CONTROL are not integrated capabilities here.

Media rights are asset-specific. Retain source/credit/policy metadata and do not redistribute restricted benchmark footage. No public deployment or submission is authorized by this card.
