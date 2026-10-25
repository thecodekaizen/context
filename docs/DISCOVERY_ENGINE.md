# Discovery engine specification

## Goal

Find a small number of useful, evidence-backed hypotheses in a bounded personal archive. The engine is successful when a person can inspect the evidence and decide whether the interpretation fits—not when it produces the most candidates.

## Candidate families

- **Recurring pattern:** a topic, behavior, motivation, or setting reappears across distinct moments.
- **Contradiction/tension:** statements, choices, or goals appear to conflict, with dates and context preserved.
- **Evolution:** an idea, practice, or preference changes over time in a traceable sequence.
- **Cross-domain connection:** related concepts or motifs appear in different areas of life or creative work.

## Pipeline

1. Normalize source metadata and extract bounded, source-linked temporal memories.
2. Partition/query by time, topic, entities, modality, and semantic similarity.
3. Generate candidate hypotheses from retrieved memories using typed output.
4. Retrieve additional supporting evidence and deliberately search for counter-evidence.
5. Score evidence quality, distinctness, temporal coverage, counter-evidence, and user relevance.
6. Deduplicate and rank; withhold candidates below the evidence threshold.
7. Return candidate text, type, evidence references, dates, confidence/uncertainty, counter-evidence, and an investigation prompt.

## Evidence rules

- A candidate needs at least two distinct source moments for a recurrence/evolution claim; a single source may support only a clearly labeled observation.
- Distinguish source facts from model interpretation. Quote or summarize minimally and link to original source.
- Do not infer sensitive traits or diagnose.
- Preserve ambiguity, missing dates, and contradictions. Do not resolve disagreement by averaging.
- A score is a ranking aid, not a calibrated probability unless calibration is demonstrated.

## CLI-first contract

The engine must be callable without the web app: load fixtures or an explicitly supplied dataset, run extraction/retrieval/discovery, and emit inspectable structured results (JSON plus concise human-readable output). It should support deterministic fixture mode and record model/provider versions. The exact command and flags are an implementation decision for Day 1.

## Initial scoring (hypothesis)

Use a transparent rubric rather than a single opaque model score: evidence count and independence, temporal spread, source quality, specificity, contradiction handling, and counter-evidence. Tune thresholds on the evaluation set. Avoid presenting the rubric as statistically calibrated.

## Failure modes to test

Generic insight, unsupported causality, cherry-picked evidence, missed counter-evidence, temporal ordering errors, duplicate candidates, modality-specific hallucination, overconfident sensitive inference, and a user correction that fails to alter the candidate.
