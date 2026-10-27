# Backend

A standard-library-only CLI baseline is available from this directory:

```sh
python -m thread_engine.cli
python -m thread_engine.cli --json
```

It reads the synthetic creative-project fixture, compares theme prevalence across chronological halves, and prints a source-linked evolution hypothesis plus counter-evidence and caveats. The fixture path uses human-authored theme annotations and makes no API calls.

For the current raw-history discovery path, install the optional client with `pip install -e '.[meta]'`, put `MODEL_API_KEY` in the repository-root `.env` file (already git-ignored), and run from the repository root:

```sh
backend/.venv/bin/python -m thread_engine.cli datasets/synthetic/creative-evolution.json --raw-muse --json
```

`--raw-muse` sends only the project ID/title and dated source artifact fields. It ignores the fixture's `memories` and theme labels. Muse Spark proposes a structured temporal hypothesis with source references; local code rejects unknown artifact IDs, mismatched dates, claims without support from at least two dates, and non-empty findings without explicit tentative wording. This last check is a lexical guard, not calibrated uncertainty; rejected findings are withheld for review. Results are cached by model, prompt version, and raw input in `.thread-cache/`; repeat runs do not spend again. Every accepted finding is marked as requiring human confirmation. The local budget guard uses `THREAD_BUDGET_USD` (default `$150`) and is only an estimate; check Meta Billing and set a spend alert.

To inspect Meta-extracted memories separately, run:

```sh
backend/.venv/bin/python -m thread_engine.cli datasets/synthetic/experiments/type-foundry/raw.json --extract-memories --json
```

`--extract-memories` prints one dated memory per raw artifact, preserving source IDs, dates, modality, and title. Muse sees the bounded archive together so it can apply consistent project topic tags, and returns a concise summary for each item using Responses API structured output. The source metadata is copied locally and checked against the archive. `--provider meta` runs that one project-level extraction followed by the deterministic temporal comparison; it accepts raw-only archives and does not need hand-authored memory labels. Extraction results and token estimates are cached under the repository-root `.thread-cache/`, regardless of the launch directory. The fixture default makes no API calls. Use Standard mode (`muse-spark-1.3`) for project material. Check the [current official pricing](https://dev.meta.ai/docs/pricing-rate-limits) before changing the model or privacy mode.

The source text is synthetic and invented for the demo. Keep real personal material out of this fixture.

## Local workflow API

Install `pip install -e '.[api]'`, then from `backend/` start `uvicorn thread_engine.api:app --reload`. The API exposes `/api/discover` and guarded session routes for challenge, confirmation, and artifact creation. Demo sessions are held in memory; restarting the local server clears them. The API is intended for local development, not public deployment.
