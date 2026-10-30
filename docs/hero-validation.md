# Judge-ready demonstration: evidence audit

Updated October 30, 2026. Scope is locked to consequential-edit review of technical
recordings. Retrieval expansion, terminal-aligner research, new models and platform
integrations are deferred while this demonstration is validated.

## First supporting run

Registered the existing CC0 sort source in the reviewed catalog, then ran:

```sh
.venv/bin/python scripts/run_technical_investigation.py data/execution-v1/edits/sort-omission.mp4 --with-meta
```

No expected source ID, caption or deletion label was passed to the investigation.
The source was deliberately registered; this is catalog retrieval, not web discovery.

- Run: `data/technical-20261030T140014Z-f8d4ab/` (local ignored evidence).
- Automatically selected: `Controlled JavaScript sort benchmark (CC0)`.
- Source SHA-256: `d77ac16b591bf5a58a3921ec8f31a74fe82b8f226eb2925b52637ef088166608`.
- Edit SHA-256: `b46aa975930f8bb6c42d28b34990a01b9f6d078dadfdc036adfdcc08289832b5`.
- Recovered source interval: **5.000–10.000 s**, edit position **5.000 s**.
- Grounding: **audio**, confidence 1.0. The soundtrack is a disclosed synthetic
  sweep, not speech. Audio correspondence does not authenticate images.
- One completed `muse-spark-1.2` review: **inconclusive**.
- Model request: 16.437 s; 3,025 input tokens and 3,153 output tokens.
- Citations passed window validation. Semantic accuracy was not independently
  scored. No whole-video analysis or web fact-check ran.
- Initial sandbox run failed DNS and retained measured evidence. The subsequent
  authorized network-enabled run completed with no failure-log entries.

Muse observed the benchmark header, qualification text, green bars and changing
measurements. It did not establish changed meaning. Its hypothetical discussion
of omitted speech is not evidence of speech: the soundtrack is synthetic.

## Spatial attribution

Inspected the cache crop fixture: text is visibly truncated at the image edges.
It supports crop geometry, not a claim that a whole disclaimer disappears.
`crop_detector.py` computes bounds and margins with OpenCV. Its optional
`sam_segmentation` field does not establish operational SAM integration.

Replayed `scripts/run_sam_gate.py`: **10/10 passed**, each above 99.9% pixel
recall. The prompt asks for green chart bars in ten frozen images. This re-scores
saved model events, not fresh inference. Current results:
`eval/execution-v1/sam-gate/rescored-results/results.json`.
The historical `results/results.json` retains an older decoder failure.
This experiment does not validate disclaimer recognition, occlusion, temporal
identity persistence or a live SAM-powered margin overlay.

## Frozen evaluation recheck

`run_execution_eval.py` passes: **15/15 intervals** across 12 positive cases,
**0.0 s** mean boundary error, **0/18** benign omission alarms, 30 cases total.
Manifest SHA-256 remains:
`bb58b2c4be1e13c2219072f98ad03e3377ecb1a5ff48276b8bb5b30be5701159`.
These are controlled deletion results, not semantic-effect accuracy.
The external hyperfine two-second deletion remains a known miss with zero Meta
calls; see [source-discovery.md](source-discovery.md).

## Original hero decision and acceptance

**Keep sort and cache as supporting demonstrations. Neither is a verified
consequential-edit hero.** The old crash/100x narrative is unsupported.

Next: one disclosed, purpose-recorded technical demo with a visible qualification
that changes the reading of a result. Preserve the complete recording and recipe
separately from frozen evaluation. Remove the qualification temporally; use a
second derivative for a peripheral crop. Do not fabricate commercial results.

Before recording the final presentation:

1. Review complete media for domain admission and permission.
2. Submit only the edit and recover its registered source.
3. Recover the known interval without changing frozen fixtures or lowering
   ambiguity thresholds to fit this example.
4. Inspect actual bounded Meta output, including inconclusive judgments, against
   the footage. Citation bounds alone are insufficient semantic validation.
5. Include an unedited control and the known external failure.
6. Integrate actual SAM masks with saved provenance, or present the segmentation
   experiment separately. Never rename geometry as AI.

Then update screen recordings and builder narration. The revised
[demo-script.md](demo-script.md) is a truthful supporting-demo draft; it is not yet
a final hero story. No release, publication or submission has been performed.


## Cache qualification case — implemented and tested

The next case is now implemented by `scripts/build_cache_qualification_case.py`.
It renders actual Python dictionary-read and PBKDF2 preparation timings into an
explicitly authored technical illustration. It is not captured independent field
footage. Generated media, measurements, pre-model labels, full-state decoded
contact sheets and results live in `data/field-validation/cache-qualification-v1/`.
No frozen benchmark file or aligner threshold was changed.

- Source: 18 s, 1280×720, 72 authored states at 4 Hz, encoded at 24 fps.
- Source SHA-256: `ec146856493edcdfb796c9ebe3338851c65141761ec910af8283bbcd0b21053c`.
- Qualification at 6–10 s: “WARM CACHE ONLY”, “COLD-START SETUP IS EXCLUDED”,
  “Not an end-to-end speedup claim”.
- Temporal edit: 14 s, source interval 6–10 s removed.
- Crop: 18 s, left 960×720 retained; the entire conditions panel is outside it.
- Control: complete source bytes, deliberately byte-identical.
- Synthetic diagnostic tone assists correspondence. Content receipts identify the
  reviewer as Codex AI, not the human builder. All unique rendered states were
  reviewed through decoded contact sheets; no speech or people are present.

| Test | Observed result |
|---|---|
| Single edit, no caption/source ID | Correct catalog source selected; audio-grounded 6.000–10.000 s deletion at edit 6.000 s, confidence 0.9998 |
| Crop | Correct source through audio; exact retained box [0, 0, 960, 720], 25% area removed, no temporal omission, zero Muse reviews |
| Byte-identical control | Full match, no crop or omission, zero Muse reviews |
| Original video-only Muse pack | `harmless_edit`; focused on diagnostic audio and missed qualification text |
| Revised Muse pack with bounded frames | `inconclusive`; correctly reads warm-cache/cold-start qualification and explains its potential interpretive effect |
| SAM concept prompt on source frame 7 s | Completed response, zero masks; 0% panel recall and IoU. **Failed** |

Run IDs: video-only `technical-20261030T140537Z-789d5b`; bounded frames
`technical-20261030T140841Z-1e14f9`; crop `technical-20261030T140514Z-5bd00b`;
control `technical-20261030T140514Z-3c31da`. The initial sandboxed attempt failed
DNS; successful live requests used approved network access. Both model outcomes
are retained, not replaced by the more useful run.

### Evidence-pack improvement

The original video pack downsamples to 640×360. It now also includes three
explicitly timed JPEG frames per clip at up to the configured 1280×720 fit,
selected at 25%, 50% and 75% of each same grounded window. Each frame has a
SHA-256 and both local and media time. Uploads reject changed bytes, out-of-window
times and more than three frames. No frame is taken outside the original bounded
windows; no whole-video model call was introduced. Prompt version is
`context-review-v5-bounded-frames`, invalidating old direct-review cache signatures.

The revised live request took 14.312 s, with 10,942 input and 3,520 output tokens.
It cites the source qualification at 6–7 and 8–9 s and contrasts the generic panel
in sampled edited frames. It explicitly says sparse frames cannot prove absence
throughout the clip. This is useful contextual interpretation, **not a verified
changed-meaning verdict**. The comparison is exploratory: frames and explanatory
prompt wording both changed; it does not isolate an image-resolution effect.
Visual matching coverage remains zero on these derivatives. Audio selection and
successful crop geometry do not establish robust visual temporal alignment.

### SAM failure and remaining milestone

`scripts/run_cache_qualification_sam.py` sends only the source frame and the
predeclared concept “right-side test conditions panel”. No truth mask or rectangle
is sent. Its frozen panel target requires recall ≥70% and IoU ≥50%. The result
fails both with zero masks. Raw events, parsed output, blank prediction, overlay,
request identity and replay score are retained. It is a standalone image test;
SAM is not integrated into the operational margin overlay.

This case now demonstrates omission recovery plus meaningful bounded observations.
It does **not** pass the proposed complete hero acceptance: materiality is still
inconclusive and SAM panel segmentation fails. Next work should address those
specific gaps and test an independent technical recording, without retrying prompts
until a favorable verdict appears. The external hyperfine miss remains unresolved.

Backend checks after the evidence-pack change: 184 tests pass, with one existing
Starlette/httpx deprecation warning. Ruff check/format and frontend TS/Vite build
pass. A subsequent focused browser check opened the saved case, verified both players ready at 5.5 s, rendered the actual inconclusive verdict and found no page errors or HTTP failures. Screenshot: `web/test-results/cache-qualification-dossier.png`. Source/edit HTTP range checks both returned 206. No full browser regression or final video render was run in this step.

Focused browser follow-up also played/paused both feeds and clicked the actual source citation at 6 s. The rendered source qualification and edited panel were visually inspected in `web/test-results/cache-qualification-players.png`. Local preview: `http://127.0.0.1:8004/?dossier=technical-20261030T140841Z-1e14f9`.
