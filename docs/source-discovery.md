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

## External-media exploration — not part of the evidence

An earlier exploratory run on a publicly posted terminal benchmark animation is not backed by a committed results file, so no figures from it are cited here. Its media and artifacts are not in the repository. Repetitive or static terminal scenes are an untested boundary: no result is claimed for them.

An exact-byte SHA-256 identity path in source selection matches an identical file with full correspondence and zero omissions. It does not relax thresholds for different files.

## What this validates and what remains

Tests validate byte-bound admission, provenance persistence, source selection without expected IDs, cross-index ambiguity, no model before grounding, bounded clip dispatch, and faithful-result restoration. Mock model responses test transport/schema contracts, not semantic accuracy.

Nothing here establishes omission recall on natural technical footage, independent semantic accuracy, or disclaimer segmentation. Frozen execution-v1 labels and thresholds were not changed.
