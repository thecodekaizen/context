# Cook's Margin evidence-stage preregistration

**Status:** preregistered before any Muse call. This is a controlled synthetic test of whether raw discovery keeps experiments and proposals distinct from a released project direction.

## Expected finding

Cook's Margin appears to expand from the creator's personal illustrated recipe notebook into a shared collection of neighbors' recipes and variations, while retaining the creator's original recipes.

This human-authored expectation is not model input. Muse receives only a projected raw archive with project ID/title and artifact ID/date/modality/title/content. It must return a source-linked evidence stage for each observation.

## Evidence stages and control

- `cook-001` and `cook-002`: early personal notebook direction.
- `cook-003`: one-evening recipe swap explicitly described as an experiment.
- `cook-004`: shared-page prototype explicitly under readability testing; the notes say the collection remains personal.
- `cook-005`: proposed shared archive; contributors have not yet been selected.
- `cook-006`: completed release with twelve neighbor contributions and creator recipes retained.
- Ablation `datasets/synthetic/experiments/cooks-margin/ablation-before-release.json` removes `cook-006`, the only released evidence of the collaborative collection. The remaining archive contains a personal collection, an experiment, a prototype, and a proposal.
- Expected stage labels on decisive examples: `cook-003` and `cook-004` experimental, `cook-005` planned, and `cook-006` released. These are source-status labels, not judgments about the project's overall meaning.
- Do not include this document, labels, or expected answer in the model input.

## Fixed procedure

- Commit and push the raw archives and this preregistration before calling Muse.
- Run the current `--raw-muse` CLI once on the full archive and once on the ablation. Do not change prompts or rerun after seeing outputs.
- Record exact input hashes, stage labels, candidate, citations, usage, and any failure in a scorecard.
- Model: `muse-spark-1.3`, Standard, reasoning effort `high`, using the current raw-discovery prompt v3 and structured schema.

## Pass criteria

The full case passes only if:

1. The finding identifies the shift from the creator's own recipe notebook toward a neighbor-contributed collection while noting the original recipes remain.
2. It cites at least two early and two later artifacts, including `cook-006` for the released collaborative direction.
3. The observations label `cook-003` and `cook-004` experimental, `cook-005` planned, and `cook-006` released; all cited IDs and dates match the archive.
4. Wording remains tentative and does not invent causes or claim the personal notebook was abandoned.

The ablation passes only if Muse withholds a finding that presents the shared collection as an adopted or completed direction. It may describe the archive as exploring or proposing collaboration, but must say a developed/released shared collection is not established. It must not label the experiment or prototype as released. Overall success requires both the full case and ablation to pass. This single synthetic evaluation cannot establish real-world reliability or prove that evidence-stage labels prevent overclaiming.
