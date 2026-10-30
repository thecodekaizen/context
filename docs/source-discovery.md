# Deterministic-first technical source discovery

The active single-input workflow no longer uses NASA catalog search, whole-video Meta observation, model-generated source identities, or generic news fact-checking.

1. Admit the submitted media bytes under the domain policy.
2. Retrieve admitted references from the operator's registered technical catalog and local collection. A supplied reference joins the same index.
3. Compare candidates in one deterministic index. This preserves ambiguity across catalog/local references and deduplicates identical bytes.
4. Derive internal omissions from measured matches on either lane.
5. Ask Muse Spark 1.2 to review at most two bounded omission windows. No match, faithful excerpt, reordering alone, or crop geometry alone cannot start semantic omission review.
6. Persist candidates, exclusions, match scores, abstentions and any bounded review in the dossier. Empty model observations do not invalidate a completed deterministic-only result.

The catalog is **operator-managed and bounded**, not internet-wide reverse-video search. An untrusted caption can rank titles/tags; it cannot establish footage identity or approve content. At most four registered candidates join admitted local references under the twenty-source index limit. Previously indexed but unadmitted legacy references are excluded. URLs identify registered provenance; the active catalog currently retrieves registered local media bytes rather than crawling those URLs.

## Register a reviewed source

After the exact file has passed content admission:

```sh
.venv/bin/python scripts/register_source.py /absolute/path/source.mp4 \
  --title 'Descriptive technical recording title' \
  --source-url 'https://publisher.example/official-source-page' \
  --license 'Actual permission or license record and its scope' \
  --tag benchmark
```

This copies exact media bytes into ignored `data/source-catalog/media/` and writes provenance under `records/`. Registration does not certify original authorship, licensing accuracy, semantic truth or model accuracy. Register permission information accurately; do not assume third-party media is redistributable just because its surrounding project is open source.

## Run a single clip

```sh
.venv/bin/python scripts/run_technical_investigation.py /absolute/path/edit.mp4
```

The command takes no expected source ID or omission labels. Add `--with-meta` to load configured credentials for grounded clips only. A no-match or faithful match still performs zero semantic reviews. Output includes a persistent dossier path and a concise run summary. The browser's “Investigate a single edit” flow uses the same backend.

## External-media validation — October 30

Selected the terminal benchmark animation linked in the [hyperfine README](https://github.com/sharkdp/hyperfine): [published asset](https://github.com/user-attachments/assets/9a5a45d3-df3f-4e0e-8cc9-5d8153f39e48). It displays `hyperfine --warmup 3 'mypy .' 'ty check'`, elapsed times, memory and a comparison summary. This is a publisher-provided technical demo asset; independent authenticity of its displayed benchmark results was not evaluated.

- Inspected all 256 GIF frames (12.8 seconds) in 16 contact sheets; silent terminal-only content. Review identity is explicitly **Codex AI visual reviewer**, not a human review or independent ground truth.
- Normalized all frames to a 20-fps MP4 and padded one black bottom row for H.264 compatibility. The maximum per-frame mean absolute RGB difference was 1.057/255.
- Created a disclosed controlled derivative deleting 3.0–5.0 seconds (frames 60–99). Its retained frames were compared against the expected source-frame sequence; maximum per-frame mean absolute RGB difference was 0.134/255. No content or audio was added.
- Raw GIF SHA-256: `1afa9ab221ec0f8827944fca8a005b2c180df5e944b9ced7b9417e1de4694b5d`.
- Normalized source SHA-256: `3605ef1d02d8c6cd7e1607ee68bfeca71c0b3c835d08e3906557591cd9632e64`.
- Edited SHA-256: `bfe0c26f5aee1fef5dfc4643d53b2109fcceab0446ca3dbe2d0525e4bdf24abe`.

**Result: the omission case failed source selection.** Visual coverage was 46.3%, below the unchanged 60% collection threshold. The pipeline abstained with `no material omission` and an explicit insufficient-correspondence limitation; no Meta request was made, including with credentials enabled. This is a false negative for the known media deletion, not evidence that the edit is faithful. Repeated/static terminal scenes remain an important failure boundary.

The clean control initially also failed the visual selector (50.8% coverage). Added an independent SHA-256 identity path to source selection: exact bytes now match with full correspondence and zero omissions; this does not weaken thresholds for different files or assert original authorship. The underlying conservative visual aligner remains unchanged.

Local artifacts: `data/field-validation/hyperfine-candidate/`, `data/technical-*/dossier.json`, and per-run `source-video-retrieval.json` / `run-summary.json`. The earlier Imgur-hosted asset returned HTTP 429; the current GitHub-hosted asset was retrieved successfully. Media remains ignored and is not included in a release. The repository's MIT documentation license was retained as context; redistribution rights for the external attachment have not been independently certified. Use this asset only for the recorded local evaluation unless permission is established.

## What this validates and what remains

Tests validate byte-bound admission, provenance persistence, source selection without expected IDs, cross-index ambiguity, no model before grounding, bounded clip dispatch, and faithful-result restoration. Mock model responses test transport/schema contracts, not semantic accuracy.

This external-media run validates an honest failure path and an exact-file clean control. It does **not** establish useful omission recall on natural technical footage, independent semantic accuracy, or disclaimer segmentation. The next engineering step is a separately evaluated temporal method for repetitive terminal footage, with no-match and benign controls retained. Frozen execution-v1 labels and thresholds were not changed.
