# Hero demo

## Narrative

“THREAD noticed something changing in my own history, can show me exactly why, and helps me decide what it means before making anything from it.”

## 3–5 minute flow

1. **Introduce the archive.** Use a curated, consented/synthetic multimodal sample spanning several dates. Show that each item has a source and date.
2. **Discover.** Run the CLI discovery result prepared for the demo; show one strong candidate about a recurring pattern, contradiction, evolution, or cross-domain connection.
3. **Inspect evidence.** Open a timeline and source fragments. Show supporting evidence and one counterexample or uncertainty.
4. **Challenge.** The user questions or corrects the interpretation. THREAD acknowledges the correction and revises, rejects, or reframes the candidate.
5. **Interview.** Ask a grounded question that helps the user articulate what the pattern means.
6. **Confirm.** User explicitly confirms or edits the insight.
7. **Create.** Generate one artifact grounded in the confirmed insight, with its evidence lineage visible.

## Demo safety net

Keep a deterministic fixture and precomputed structured result available. If a live model call fails, continue to evidence inspection and interview using the fixture. Clearly disclose when the result is fixture-backed. Never switch to an unsupported insight just to preserve the story.

## Demo assets

- Curated fixture with source records, dates, intended candidate, counter-evidence, and evaluation notes.
- Short screen recording as a fallback.
- One-page explanation of the evidence and what would falsify the interpretation.

See `design/flows/demo-flow.md` for the interaction flow.
