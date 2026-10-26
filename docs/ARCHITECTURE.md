# Architecture proposal

## Proposed stack

- **Backend:** Python, FastAPI, Pydantic; a CLI entry point for the same core discovery services.
- **Data:** PostgreSQL for users, source items, extracted memories, candidates, evidence links, interviews, confirmations, and artifacts; pgvector for semantic retrieval.
- **Web:** Next.js, TypeScript. Keep the client focused on evidence inspection, candidate review, interview, and artifact presentation.
- **Model:** Meta Model API accessed through a narrow provider adapter. Use the API only for supported multimodal interpretation/generation tasks; keep orchestration, data contracts, provenance, evaluation, and product policy in our code.

Validate API availability, modalities, rate limits, privacy terms, and output reliability on Day 1. The hackathon rules require Meta models in the project, so a Meta model must contribute to the main demo path; a deterministic/synthetic fixture path makes development repeatable and provides a fallback if a live call fails. Do not claim a capability until verified against current API docs and a small experiment.

## Logical components

1. **Import boundary:** accepts an explicit, small set of user-provided files or prepared fixtures; validates types and records source metadata. No broad account scraping or background collection in hackathon scope.
2. **Memory extraction:** creates normalized temporal memories with source IDs, extracted facts/phrases, modality, timestamps, and model provenance.
3. **Index and retrieval:** relational filters for time and metadata plus vector similarity for related memories. Retrieval must return source references, not just generated summaries.
4. **Discovery engine:** proposes candidates by pattern family, gathers evidence, seeks counter-evidence, scores and ranks, and emits a typed candidate record.
5. **Investigation and interview:** creates grounded questions and stores user response and explicit disposition (confirmed, revised, rejected, deferred).
6. **Artifact generation:** accepts only a confirmed insight ID and selected evidence/context; stores the output and links it back to the insight.
7. **API and web:** expose the workflow; web is downstream of the CLI-proven engine.

## Model API boundary

Define an internal `ModelProvider` interface with task-specific methods and typed inputs/outputs. The adapter owns authentication, request formatting, retries, timeouts, and response parsing. Application services own schemas, policy, provenance, validation, and fallback. Persist provider/model/version and source IDs with every model-derived extraction. Avoid putting secrets in the client or logs.

Model output is untrusted input: validate structured responses, reject missing evidence references, and never let model prose silently become a fact, confirmed insight, or executable action. Build a fixture provider for repeatable local development and evaluation.

## Data flow

`source item → memory extraction → temporal/semantic retrieval → candidate hypothesis → evidence + counter-evidence → user interview/disposition → confirmed insight → artifact`

Each transition is explicit and persisted. No direct source-item-to-artifact shortcut in the hero flow.

## Day-1 architecture spike

Verify the Meta Model API integration boundary with one supported sample task, establish the Python/Next.js project skeleton, define the core typed contracts, and run a CLI vertical slice on fixtures. Defer detailed service decomposition until this succeeds.
