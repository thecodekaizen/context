# CONTEXT 0.2 — See the whole story

## Working release

- FFmpeg probing, timestamped visual samples and conservative sequence alignment.
- Supported omission, reordering and repetition findings, with unresolved spans.
- Indexed local source collection, content deduplication and ambiguous-candidate handling.
- Dual players, evidence timelines, missing-context reveal and compatible previews.
- Live Muse Spark 1.2 review of bounded video excerpts with timestamp validation.
- Saved cases and evidence-bound interpretation reuse.
- Source hashes, downloadable evidence JSON and reproducible evaluation.
- Narrated 3:00 full-HD demo with real captures and labeled saved model results.

## Verification

51 backend tests and eight browser tests passed locally with optional licensed
production footage installed. Eleven backend cases and the production-demo
browser case skip without that optional download. CI runs offline deterministic
and mocked-provider tests; no API key is installed in CI. Full provider compatibility
was separately verified with an authenticated local request.

The production-footage regression set found and fixed false omissions caused by
ambiguous scenes and false 1× mappings on speed-changed footage. It is small and
is not a general accuracy benchmark. Crops and color shifts remain limited;
tested speed changes remain unresolved rather than receiving unsupported findings.

## Included release assets

- `context-source.zip`: code and documentation from one exact Git commit.
- `context-demo-3min.mp4`: full-HD H.264/AAC narrated demonstration.
- `context-submission.zip`: source, demo, evaluation and submission documents.
- `manifest.json`: exact revision, artifact sizes and SHA-256 hashes.

The source archive excludes `.env`, API keys, uploaded recordings, local caches,
virtual environments, browser profiles and dependency directories. The empty
`.env.example` is included. Film source data is downloaded separately; its credit
and modifications are disclosed in the README, evaluation and demo.

## Running

See README.md for local setup. The current application is a local workstation,
with no public hosting, accounts or production service guarantees.

## Demo attribution

Big Buck Bunny (2008), (c) copyright 2008, Blender Foundation /
www.bigbuckbunny.org. CC BY 3.0. Excerpts trimmed, transcoded and edited for a
controlled demonstration. https://peach.blender.org/about/
