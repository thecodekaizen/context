# Tiny Type Lab raw-discovery preregistration

**Status:** preregistered before any Muse call. This is a controlled synthetic CLI test, not evidence of real-world performance.

## Expected finding

Tiny Type Lab appears to broaden from a typeface primarily for code editors and terminals toward a type family for coding plus explanatory text and compact labels, while code remains a central use case.

This phrasing is the human-authored expectation, not input to Muse. Muse receives only `datasets/synthetic/experiments/type-foundry/raw.json` or the ablation archive.

## Evidence and control

- Early baseline: `type-001`, `type-002`, and `type-003` describe a developer-tool/code focus.
- Later evidence: `type-004` introduces printed worksheets and paragraph readability; `type-005` explores explanatory text and compact labels; `type-006` previews text and coding cuts across several media.
- Continuity evidence: `type-006` explicitly retains code as a showcase use case.
- Ablation: `datasets/synthetic/experiments/type-foundry/ablation-code-only.json` removes all three later artifacts. The expected result is no evolution finding, because the remaining archive supports only a stable code-focused project.
- The raw runner must strip any additional fields and send only the project ID/title and artifact ID/date/modality/title/content fields. No expected answer or evaluation criteria are stored in either archive.

## Fixed run procedure

- Model: `muse-spark-1.3`, Standard mode, reasoning effort `high`.
- Run the full archive and the ablation once each using the committed raw-discovery CLI and prompt version.
- Do not tune the prompt or rerun these same cases after inspecting outputs. Any follow-up is a separately preregistered experiment.
- Record model output, source references, token usage, and local cost in a scorecard. Model output is untrusted and must pass local validation.

## Pass criteria

The full case passes only if all five criteria are met:

1. **Independent direction:** identifies a broadening beyond coding toward explanatory text/labels or multiple reading contexts.
2. **Temporal contrast:** supports the interpretation with at least one early and one later source moment.
3. **Continuity:** states that coding remains supported, rather than claiming it was abandoned.
4. **Traceability:** all cited artifact IDs and dates match the raw archive; no material claim lacks relevant evidence.
5. **Epistemic restraint:** the finding itself is explicitly tentative (for example, “appears to”); an unqualified claim fails even if the direction is correct.

The ablation passes only if it returns no candidate finding and communicates that the remaining evidence is insufficient to establish evolution. Overall success requires the full case and ablation both to pass. A lexical hedge guard is only a rejection filter; passing it is not proof of calibrated confidence.
