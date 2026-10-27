# Paper Satellites raw-discovery preregistration

**Status:** preregistered before any Muse call. This is a controlled synthetic test of raw-artifact temporal discovery, not evidence of real-world reliability.

## Expected finding

Paper Satellites appears to evolve from a collection of short, individually readable illustrated stories toward a connected ensemble audio release with outside performers, while keeping the written illustrated scenes as part of the work.

This is the human-authored expected answer, not model input. Muse may receive only `datasets/synthetic/experiments/paper-satellites/raw.json` or the ablation file, projected to project ID/title and raw artifact ID/date/modality/title/content fields.

## Evidence and control

- Early format and intent: `paper-001` and `paper-002` establish short, standalone written stories with illustrations.
- Transition evidence: `paper-003` reports a read-aloud experiment that suggested interaction between narrators; `paper-004` records a connected two-voice audio pilot.
- Decisive later direction: `paper-005` plans outside performers and linked voice-note scenes; `paper-006` reports an ensemble sequence while retaining illustrated pages.
- Continuity: `paper-006` explicitly says the short illustrated pages remain part of the release.
- Ablation: `datasets/synthetic/experiments/paper-satellites/ablation-before-ensemble.json` keeps `paper-001`–`paper-004` and removes decisive artifacts `paper-005`–`paper-006`. The expected result is no established evolution to an ensemble format: the archive supports experimentation with audio, but not the later participatory release direction or its continuation.
- No expected answer, labels, or evaluation notes are included in either input archive.

## Fixed procedure

- Commit and push this preregistration and both raw archives before calling Muse.
- Run the current `--raw-muse` CLI once on the full archive and once on the ablation, without prompt changes or retries after seeing output.
- Record exact input hashes, result, references, usage, and any failure in a scorecard. Do not rerun either case after inspection; a changed method requires a separately preregistered case.
- Model: `muse-spark-1.3`, Standard, minimal reasoning, using the repository's current raw-discovery prompt.

## Pass criteria

The full archive passes only if all five criteria hold:

1. **Direction:** identifies movement from standalone written/illustrated vignettes toward connected audio/ensemble storytelling, with outside voices if it makes that claim.
2. **Temporal support:** cites at least two distinct early artifacts and at least two later artifacts, including at least one decisive later item (`paper-005` or `paper-006`).
3. **Continuity:** recognizes that illustrated written scenes remain part of the work.
4. **Traceability:** all cited IDs and dates match the supplied archive and support the associated observations.
5. **Restraint:** phrases interpretation tentatively and does not claim writing was abandoned or invent motivation/causality.

The ablation passes only if it withholds a developed ensemble-evolution finding or clearly limits itself to early audio experimentation, and says evidence is insufficient to establish the later collaborative release. Overall success requires both full and ablation cases to pass. This remains one constructed synthetic example.
