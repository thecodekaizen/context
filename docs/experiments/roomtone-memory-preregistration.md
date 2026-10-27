# Roomtone project-memory preregistration

**Status:** preregistered before any Muse call. This is a controlled synthetic evaluation of the project-level memory path.

## Expected evolution

Roomtone appears to evolve from a personal field-recording diary into a searchable shared sound library for creative collaborators, while personal recording remains the way new sounds enter the project.

## Evidence set and control

- Early personal capture: `room-001`, `room-002`, and `room-003`.
- Collaboration begins: `room-004` records collaborators asking to exchange and reuse recordings.
- Decisive developed direction: `room-005` describes shared collections and team search; `room-006` describes a searchable collaborator library while retaining phone capture.
- Ablation: `datasets/synthetic/experiments/roomtone/ablation-before-library.json` retains artifacts `001`–`004` but removes the two decisive artifacts `005`–`006`. The expected outcome is no sufficiently supported shift to a developed shared-library product; one request from collaborators is not enough to establish that direction.
- The model receives only the project ID/title and raw dated artifact fields. No expected answer, fixture labels, or evaluation notes are passed to Muse.

## Fixed procedure

- Run `--extract-memories` once on the full archive and once on the ablation; inspect but do not tune the prompt.
- Run the deterministic temporal comparison on cached memories for each archive.
- Record source links, continuity evidence, token usage, and any failure. Do not rerun either archive after inspecting results.
- Model: `muse-spark-1.3` Standard, minimal reasoning for batch memory extraction.

## Pass criteria

The full archive passes only if all five conditions hold:

1. **Direction:** candidate identifies evolution from individual capture/archive toward sharing or reuse among creative collaborators.
2. **Temporal support:** evidence connects at least two early artifacts with at least two later artifacts.
3. **Continuity:** later evidence shows recording remains part of the workflow.
4. **Traceability:** every evidence source ID/date matches the raw input; no fabricated sources.
5. **Restraint:** wording describes an apparent evolution/expansion and does not invent a cause or personality trait.

The ablation passes only if discovery is withheld or clearly limited to an early collaboration request, without claiming a developed shared library. Overall success requires both full and ablation cases to pass. This single synthetic result cannot establish real-world reliability.
