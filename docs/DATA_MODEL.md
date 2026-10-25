# Data model (initial proposal)

This is a conceptual schema for the 10-day prototype. Keep source provenance and temporal meaning intact. Exact SQL and migrations are Day-1 implementation work.

## Entities

- **User** — local/demo identity and preferences.
- **SourceItem** — user-provided file or fixture; modality, original filename/reference, content hash, created/observed/ingested timestamps, consent/source notes, storage reference, and processing state.
- **Memory** — normalized temporal record extracted from a source; text/facts, event time or interval, precision/timezone where known, entities/topics, embedding reference, extraction provenance, and confidence/uncertainty. A memory may reference multiple source items.
- **Candidate** — hypothesis text, family, status, time range, score breakdown, uncertainty, engine version, and created time.
- **EvidenceLink** — candidate-to-memory relation labeled supporting, contradicting, or contextual, with rationale and source span/reference.
- **Interview** — candidate, grounded question, response, timestamps, and status.
- **Insight** — user-confirmed or user-revised interpretation; explicit confirmation event, final wording, links to candidates/evidence, and revision history.
- **Artifact** — output type/content, confirmed insight ID, selected evidence/context, generation provenance, and created time.

## Key invariants

- Every Memory resolves to at least one SourceItem.
- Every Candidate evidence link resolves to a Memory and then to a source.
- Candidate status is separate from Insight confirmation. A candidate cannot self-confirm.
- Artifact generation requires an explicit confirmed Insight reference.
- Deletion of a source should permit deletion or invalidation of derived memories and downstream claims.
- Preserve original timestamps and separately store normalized timestamps/precision.

## Privacy and retention

Use only a small, consented sample for the demo. Keep secrets and raw personal content out of logs. Make it possible to remove an imported source and derived records. Never commit private real datasets; `datasets/real/` is a placeholder only.
