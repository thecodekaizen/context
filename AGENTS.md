# Repository working agreements

## Locked direction: VEIL

VEIL is the final hackathon project: an API-first multimodal video privacy engine. Detect. Redact. Verify. No further product pivots. Work in `veil/`; read its AGENTS.md, README.md, docs/PRODUCT.md, docs/IMPLEMENTATION.md and docs/MODEL_CAPABILITIES.md.

Previous THREAD, SHOWME and Experimental Investigator code remains historical. Preserve reusable infrastructure and unrelated uncommitted work. The preceding instructions are archived in docs/archive/AGENTS_INVESTIGATOR_2026-10-28.md; they do not override VEIL.

## Execution

Prioritize real core-engine artifacts, independent exported-media inspection, repair and receipts before API/SDK, then reference UI. No mocks presented as inference success. Keep ground truth out of inference. Record failures, actual model calls, latency, estimated costs and limitations. Test and inspect generated media. Synthetic or explicitly consented footage only; document transfers to Meta. No employer code/data/IP, secrets, .env or real personal footage in Git. Never claim zero leaks or fully local processing when cloud models are used.

The user explicitly authorizes assistant implementation for this hackathon. Explain important concepts briefly; do not block authorized work with learning exercises or repeated approval checkpoints. Existing authorization for scoped commits and pushes persists. Keep the repository private until submission visibility is explicitly authorized. Submission requires public repository and at most three-minute demo; internal target 3 November 2026.
