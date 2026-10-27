# Pocket Observatory temporal-support preregistration

**Status:** preregistered before any Muse call. This controlled synthetic case tests whether raw discovery cites both early and late evidence and distinguishes a released direction from earlier experiments and plans.

## Expected finding

Pocket Observatory appears to expand from the creator's personal balcony-astronomy notebook into a seasonal almanac of residents' observations, while retaining the creator's original hand-drawn sky maps.

This is a human-authored expectation, not model input. Muse receives only a projected raw archive with project ID/title and artifact ID/date/modality/title/content, and returns source-linked observations with evidence-stage labels.

## Evidence and ablation

- Early personal direction: `sky-001` and `sky-002` describe the creator's own sketches and observations in a personal pocket guide.
- `sky-003` is explicitly a one-night usability test; `sky-004` is a prototype page, not a published group journal.
- `sky-005` is explicitly a proposal; no community issue has been assembled.
- Decisive mature direction: `sky-006` reports the published almanac with contributions from fifteen residents, retaining the original maps.
- Ablation `datasets/synthetic/experiments/pocket-observatory/ablation-before-release.json` removes `sky-006`. The remaining experiment, prototype, and proposal do not establish a released community almanac.
- Expected stages: `sky-003` and `sky-004` experimental, `sky-005` planned, `sky-006` released.
- Do not include this document, labels, or expected answer in the model input.

## Fixed procedure

- Commit and push the raw archives and this preregistration before calling Muse.
- Run the current `--raw-muse` CLI once on the full archive and once on the ablation. No prompt changes or reruns after outputs are inspected.
- Record exact input hashes, stage labels, candidate, supporting citations, response status, usage, and any failure in a scorecard.
- Model: `muse-spark-1.3`, Standard, reasoning effort `minimal`, raw-discovery prompt v4, structured evidence-stage schema, and local timeline-spanning citation gate.

## Pass criteria

The full case passes only if:

1. The candidate describes the move from a personal astronomy notebook to a resident-contributed seasonal almanac, while retaining the creator's maps.
2. The **supporting-artifacts list** cites at least two early artifacts (`sky-001` or `sky-002` plus any other early source) and at least two later artifacts, including `sky-006`.
3. `sky-003`/`sky-004` are experimental, `sky-005` planned, and `sky-006` released; cited IDs and dates match the archive.
4. The claim is tentative and does not invent a cause or claim the personal practice was abandoned.

The ablation passes only if the CLI returns no sufficiently supported evolution candidate. The model may describe the experiments and proposal, but must not represent a community almanac as an adopted or released direction. Overall success requires both cases to pass. This synthetic case cannot establish real-world reliability or repeatability.
