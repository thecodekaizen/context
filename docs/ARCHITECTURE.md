# Architecture proposal

## Proposed stack

- **Backend:** Python, FastAPI, Pydantic; a CLI entry point for the same core discovery services.
- **Data:** PostgreSQL for users, source items, extracted memories, candidates, evidence links, interviews, confirmations, and artifacts; pgvector for semantic retrieval.
- **Web:** Next.js, TypeScript. Keep the client focused on evidence inspection, candidate review, interview, and artifact presentation.
- **Model:** Meta Model API accessed through a narrow provider adapter. Use the API only for supported multimodal interpretation/generation tasks; keep orchestration, data contracts, provenance, evaluation, and product policy in our code.

Validate API availability, modalities, rate limits, privacy terms, and output reliability on Day 1. The hackathon rules require Meta models in the project, so a Meta model must contribute to the main demo path; a deterministic/synthetic fixture path makes development repeatable and provides a fallback if a live call fails. Do not claim a capability until verified against current API docs and a small experiment.

## Logical components

1. **Import boundary:** accepts an explicit, small set of user-provided files or prepared fixtures; validates types and records source metadata. No broad account scraping or background collection in hackathon scope.
2. **Temporal memory extraction (current CLI slice):** Muse processes the bounded project archive together and creates a concise summary plus consistent open-vocabulary topic tags for every dated artifact. Source ID, date, modality, and title are copied from the source and cannot be model-edited. `--extract-memories` makes the extracted records inspectable; `--provider meta` feeds them to the deterministic temporal comparison.
3. **Raw archive discovery (separate current CLI path):** sends a bounded set of dated source artifacts to Muse and asks for observations, one candidate, supporting evidence, complicating evidence, and limitations. It excludes pre-labeled memories and expected answers.
4. **Evidence validation:** local code verifies output shape and each artifact ID/date against the source archive. An evolution finding needs multiple dated source moments and remains unconfirmed.
5. **Memory/index/retrieval (later):** persistent storage and metadata/vector retrieval can support larger archives after the CLI slice proves useful. Retrieval must preserve original source references.
6. **Discovery engine:** future candidate families can gather further support and counter-evidence, rank candidates, and emit a typed record.
7. **Investigation and interview:** creates grounded questions and stores user response and explicit disposition (confirmed, revised, rejected, deferred).
8. **Artifact generation:** accepts only a confirmed insight ID and selected evidence/context; stores the output and links it back to the insight.
9. **API and web:** expose the workflow; web is downstream of the CLI-proven engine.

## Model API boundary

Define an internal `ModelProvider` interface with task-specific methods and typed inputs/outputs. The adapter owns authentication, request formatting, retries, timeouts, and response parsing. Application services own schemas, policy, provenance, validation, and fallback. Persist provider/model/version and source IDs with every model-derived extraction. Avoid putting secrets in the client or logs.

Model output is untrusted input: validate structured responses, reject missing evidence references, and never let model prose silently become a fact, confirmed insight, or executable action. Build a fixture provider for repeatable local development and evaluation.

## Data flow

`raw dated artifacts → Muse candidate and source-linked observations → creator challenge/disposition → confirmed insight → artifact`

The direct `thread-discover <dataset> --raw-muse --review` path sends only the projected raw archive to Muse, adapts its validated candidate and evidence into the creator-review contract, and preserves model-classified source stages in the session and direction note. The separate `--provider meta --review` path extracts temporal memories first and compares them locally. Neither path may rely on hand-authored theme labels for model-backed claims; keep their results distinct in evaluations.

Each transition is explicit and persisted. No direct source-item-to-artifact shortcut in the hero flow.

## Day-1 architecture spike

Verify the Meta Model API integration boundary with one supported sample task, establish the Python/Next.js project skeleton, define the core typed contracts, and run a CLI vertical slice on fixtures. Defer detailed service decomposition until this succeeds.
