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
4. **Investigation / ECHO:** user challenges a claim; the system updates its interpretation with attribution. (ECHO is a proposed product interaction name, not a locked brand decision.)
5. **Interview:** one grounded question at a time, with skip/reject/revise controls.
6. **Insight confirmation:** user edits wording and explicitly confirms.
7. **Artifact:** one generated output, with links back to confirmed insight and evidence.

## Demo constraints

Keep to one candidate and one artifact. Do not imply continuous monitoring. Show fixture disclosure if the model path is mocked. The UI must let the user reject the interpretation and still finish the flow honestly.
