# Ember Table endpoint-support preregistration

**Status:** preregistered before any Muse call. This fresh synthetic case checks whether raw discovery anchors a creative-project evolution in the archive's beginning and ending, and whether it keeps experiments and proposals distinct from a completed release.

## Expected finding

Ember Table appears to evolve from the creator's personal illustrated recipe notebook toward a seasonal booklet with recipes contributed by supper-group members, while retaining the creator's linocut illustrations.

This expectation is for human scoring only. Muse receives only the raw archive projection, never this document or its labels.

## Evidence and ablation

- Early personal direction: `ember-001` and `ember-002` describe a private recipe notebook and the creator's own cooking and illustrations.
- `ember-003` is one readability test at a single supper, not ongoing co-authorship.
- `ember-004` is a private layout prototype, explicitly not collected or published.
- `ember-005` is a proposal only; no group recipes have been gathered.
- Decisive completed direction: `ember-006` documents a completed and shared booklet with twelve credited contributors and retained linocuts.
- Ablation `datasets/synthetic/experiments/ember-table/ablation-before-booklet.json` removes `ember-006`.

## Fixed procedure

- Commit and push both raw-only inputs and this preregistration before calling Muse.
- Run the CLI once on the full archive and once on the ablation, without prompt changes or retries after inspecting outputs.
- Use `muse-spark-1.3`, Standard, minimal reasoning, raw-discovery prompt v4, and the current local endpoint-support validation.
- Record input hashes, observations and stages, candidate wording, support/complicating citations, response status, usage, and protocol deviations.

## Pass criteria

### Full archive

1. Candidate describes the move from personal recipes to a completed contributor booklet while retaining the creator's linocuts.
2. Supporting citations include at least one of `ember-001`/`ember-002` and `ember-006`.
3. Stages: `ember-003` experimental, `ember-004` experimental, `ember-005` planned, and `ember-006` released.
4. Candidate uses tentative wording, invents no cause, and does not say the personal practice disappeared.

### Ablation

Pass if there is no candidate, or if any candidate is explicitly bounded to the experiments/proposal and does not state or imply that a contributor booklet was completed, adopted, or released. A candidate claiming an established co-authored booklet fails.

Overall success requires every full criterion and the ablation criterion. This is a single controlled synthetic test, not evidence of real-world reliability or generalization. Any post-hoc response replay is only a regression check and must be reported separately.
