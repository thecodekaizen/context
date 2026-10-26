# Hero demo interaction flow

```text
Curated archive
  ↓ import + provenance
Temporal memories
  ↓ CLI discovery (fixture or supported live model)
Candidate hypothesis
  ↓ inspect supporting evidence + counter-evidence
User challenges or adds context
  ↓ grounded interview
User revises / rejects / explicitly confirms
  ↓ confirmed insight only
One traceable artifact
```

## Screen sequence

1. **Home / Discover:** archive coverage over time and a concise invitation to review new findings.
2. **Candidate detail:** one specific hypothesis, dates, evidence count, uncertainty, and counter-evidence.
3. **Evidence timeline:** source fragments ordered by time; open each original item.
4. **Investigation / ECHO:** THREAD asks a question grounded in the earlier and later themes. The creator explains what changed.
5. **Interview:** a second question reflects the creator’s answer and asks how the prototype should express the shift. The creator can add context before the provisional interpretation unlocks. (ECHO is a proposed product interaction name, not a locked brand decision.)
6. **Insight confirmation:** user edits wording and explicitly confirms.
7. **Artifact:** one generated output, with links back to confirmed insight and evidence.

## Demo constraints

Keep to one candidate and one artifact. Do not imply continuous monitoring. Show fixture disclosure if the model path is mocked. The UI must let the user reject the interpretation and still finish the flow honestly.
# Demo flow

1. Open the Neighborhood Atlas project and see the evolution hypothesis: emphasis appears to move from wayfinding toward oral history.
2. Follow the dated fragments and compare the supporting evidence with the later route-index counterexample.
3. Read the uncertainty note before accepting or challenging the interpretation.
4. Add creator context that the archive cannot know.
5. Revise the interpretation in the creator's own words and explicitly confirm it.
6. Create a direction note. The local API refuses artifact creation until confirmation and carries the evidence source IDs into the artifact.

The synthetic fixture runs without an API key. Selecting Muse Spark requires a configured Meta Model API key and verified credits; show provider/model provenance and the usage estimate in the demo.
