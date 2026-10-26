# Hero demo

## Narrative

“THREAD traced how this creative project changed over time, showed me the evidence on both sides, and helped me decide what to make next.”

## Three-minute submission video

The submission requires a three-minute demo video. Keep the story to one project, one evolution claim, a few source fragments, one challenge/correction, one explicit confirmation, and one small artifact. State which functionality was built during the hackathon; distinguish it from the pre-event repository foundation. Show the Meta model’s actual role in the flow.

## Demo flow

1. **Introduce the archive.** Use a rights-safe synthetic creative-project archive spanning several dates. Show that each item has a source and date.
2. **Discover.** Run the Meta-backed CLI discovery result prepared for the demo; show one specific evolution claim about the creative work.
3. **Inspect evidence.** Open a timeline and source fragments. Show supporting evidence and one counterexample or uncertainty.
4. **ECHO interview, question one.** Ask what changed between the earlier and later work, and what original need still matters.
5. **ECHO interview, question two.** Reflect the creator’s first answer and ask what a visitor should encounter first. Preserve both answers as creator context before offering a provisional interpretation.
6. **Confirm.** User explicitly confirms or edits the insight.
7. **Create.** Generate one artifact grounded in the confirmed insight, with its evidence lineage visible.

## Demo safety net

Keep a deterministic fixture and precomputed structured result available. If a live model call fails, continue to evidence inspection and interview using the fixture. Clearly disclose when the result is fixture-backed. Never switch to an unsupported insight just to preserve the story.

## Demo assets

- Curated fixture with source records, dates, intended candidate, counter-evidence, and evaluation notes.
- Short screen recording as a fallback.
- One-page explanation of the evidence and what would falsify the interpretation.

See `design/flows/demo-flow.md` for the interaction flow.
