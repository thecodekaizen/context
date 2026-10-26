# Backend

A standard-library-only CLI baseline is available from this directory:

```sh
python -m thread_engine.cli
python -m thread_engine.cli --json
```

It reads the synthetic creative-project fixture, compares theme prevalence across chronological halves, and prints a source-linked evolution hypothesis plus counter-evidence and caveats. The fixture path uses human-authored theme annotations and makes no API calls.

After claiming Meta API credits, install the optional client with `pip install -e '.[meta]'`, set `MODEL_API_KEY` in your shell, and run `python -m thread_engine.cli --provider meta --json`. Muse Spark extracts a constrained summary and theme list from each raw source artifact; THREAD's temporal comparison remains local. Results are cached by model, prompt version, and artifact contents in `.thread-cache/`, so rerunning discovery does not repeat paid extraction. The CLI caps each extraction at 256 completion tokens, uses minimal reasoning for this narrow task, and stops when its local cost estimate reaches `THREAD_BUDGET_USD` (default `$150`). It reports token counts and cumulative estimated cost; this local guard is not a billing guarantee, so confirm credits appear in Billing and set Meta's spend alert before live calls. Product UI remains behind the CLI-first gate.

Use Standard mode (`muse-spark-1.3`) for project material. Contributor mode is cheaper, but Meta may use submitted content to improve its models. Check the [current official pricing](https://dev.meta.ai/docs/pricing-rate-limits) before changing the model or privacy mode.

The source text is synthetic and invented for the demo. Keep real personal material out of this fixture.

## Local workflow API

Install `pip install -e '.[api]'`, then from `backend/` start `uvicorn thread_engine.api:app --reload`. The API exposes `/api/discover` and guarded session routes for challenge, confirmation, and artifact creation. Demo sessions are held in memory; restarting the local server clears them. The API is intended for local development, not public deployment.
