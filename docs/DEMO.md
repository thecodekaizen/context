# Hero demo

> **Archived THREAD demo:** use [`../design/flows/demo-flow.md`](../design/flows/demo-flow.md) for the current SHOWME target flow. That flow remains a target until the proof passes; it is not a validated capability claim.

## Narrative

“THREAD traced how this creative project changed over time, showed me the evidence on both sides, and helped me decide what to make next.”

## Three-minute submission video

The submission requires a three-minute demo video. Keep the story to one project, one evolution claim, a few source fragments, one challenge/correction, one explicit confirmation, and one small artifact. State which functionality was built during the hackathon; distinguish it from the pre-event repository foundation. Show the Meta model’s actual role in the flow.

## Demo flow

1. **Introduce the archive.** Use a rights-safe synthetic creative-project archive spanning several dates. Show that each item has a source and date.
2. **Discover.** Run `thread-discover <archive.json> --raw-muse --review`; Muse proposes a source-linked evolution and the CLI opens the creator review in the same workflow. If there is no candidate, the interview does not start.
3. **Inspect evidence.** Open a timeline and source fragments. Show supporting evidence and one counterexample or uncertainty.
4. **Challenge.** Inspect the model-classified chronology and collect concrete creator context; ask what part of the earlier direction should remain important.
5. **Disposition.** Keep or revise the interpretation, reject it, or defer it. Rejection and deferral produce no artifact.
6. **Confirm.** The creator must type `CONFIRM` for the final interpretation. Any other response leaves it unconfirmed.
7. **Create.** Write one local direction note grounded in the confirmed insight, with source IDs and evidence lineage. The session and note stay under ignored `.thread-output/`.

## Demo safety net

Keep a deterministic fixture and precomputed structured result available. If a live model call fails, continue to evidence inspection and interview using the fixture. Clearly disclose when the result is fixture-backed. Never switch to an unsupported insight just to preserve the story.

## Demo assets

- Curated fixture with source records, dates, intended candidate, counter-evidence, and evaluation notes.
- Short screen recording as a fallback.
- One-page explanation of the evidence and what would falsify the interpretation.

See `design/flows/demo-flow.md` for the interaction flow.
