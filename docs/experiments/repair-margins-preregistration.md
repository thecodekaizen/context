# Repair Margins evidence-stage preregistration

**Status:** preregistered before any Muse call. This is a controlled synthetic test of the minimal-reasoning raw-discovery path and its handling of proposal/experiment versus released work.

## Expected finding

Repair Margins appears to expand from the creator's personal workshop repair cards into an illustrated neighborhood guide with residents' methods, while retaining the creator's original repair diagrams.

This human-authored expectation is not model input. Muse receives only a projected raw archive with project ID/title and artifact ID/date/modality/title/content. It must return source-linked observations with evidence-stage labels.

## Evidence and control

- Early personal direction: `repair-001` and `repair-002` describe the creator's own furniture fixes in a personal illustrated booklet.
- `repair-003` is explicitly a one-afternoon prototype test; `repair-004` is a single-sheet annotation pilot that has not been distributed.
- `repair-005` is explicitly an editorial proposal; contributions have not been collected.
- Decisive mature direction: `repair-006` reports a published guide with methods contributed by fourteen residents, while retaining the creator's original diagrams.
- Ablation `datasets/synthetic/experiments/repair-margins/ablation-before-release.json` removes `repair-006`. The remaining test, pilot, and proposal must not be represented as a completed or adopted neighborhood guide.
- Expected stages: `repair-003` and `repair-004` experimental; `repair-005` planned; `repair-006` released.
- Do not include this document, labels, or expected answer in the model input.

## Fixed procedure

- Commit and push the raw archives and this preregistration before calling Muse.
- Run the current `--raw-muse` CLI once on the full archive and once on the ablation. Do not change prompts or rerun either archive after seeing outputs.
- Record exact input hashes, stage labels, candidate, citations, response status, usage, and any failure in a scorecard.
- Model: `muse-spark-1.3`, Standard, reasoning effort `minimal`, raw-discovery prompt v4, structured evidence-stage schema.

## Pass criteria

The full case passes only if:

1. The finding identifies movement from the creator's own repair notebook toward a resident-contributed neighborhood guide, while preserving the original diagrams.
2. It cites at least two early and two later artifacts, including `repair-006` for the released direction.
3. `repair-003` and `repair-004` are experimental, `repair-005` planned, and `repair-006` released; all cited IDs and dates match.
4. The finding is tentative and does not claim the personal work was abandoned or invent a cause.

The ablation passes only if Muse withholds a finding that presents the shared neighborhood guide as an adopted or completed direction. It may describe experiments and a proposal, but must state that a developed guide is not established. It must not label those experiments or proposal as released. Overall success requires both cases to pass. This controlled synthetic result cannot establish real-world reliability or isolate reasoning effort as the cause of any difference.
