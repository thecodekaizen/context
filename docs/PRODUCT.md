# Product brief

## One sentence

THREAD is a multimodal creative-project intelligence system that turns a creator’s dated project history into temporal memories, discovers evidence-backed changes in themes and direction, and lets the creator investigate and confirm a finding before creating an artifact.

## Problem

A creator’s sketches, notes, drafts, recordings, and project documents hold evidence of how a body of work changes over time. These materials are fragmented and easy to misread when AI turns them into a confident story. Most creative tools start at generation; THREAD starts by tracing changes in the work back to dated evidence.

## Product promise

Help creators see how themes and directions have changed across a bounded set of projects—and make it easy to inspect, challenge, and correct the evidence behind each finding.

## Core model

1. **History → memories.** Ingest a deliberately bounded set of user-provided multimodal items. Extract time, modality, entities, topics, and concise memory records with source provenance.
2. **Memories → candidates.** Find recurring patterns, contradictions, evolution, and cross-domain connections. Each candidate is a hypothesis with evidence, time span, confidence, and counter-evidence where available.
3. **Candidates → investigation.** Retrieve supporting and disconfirming material; test whether a candidate is specific, temporally coherent, and adequately evidenced. Suppress weak or redundant candidates.
4. **Investigation → interview.** Ask a small number of grounded, open questions. The user can confirm, revise, reject, or defer an interpretation.
5. **Confirmed insight → artifact.** Only after human confirmation, offer a useful creation path such as a personal essay, project brief, creative prompt, or timeline.

## User and use case

Initial user: a creator with a small archive of project artifacts who wants to understand how a specific project’s themes, constraints, or direction have evolved.

Hackathon use case: given a curated synthetic creative-project archive, show one defensible claim about the work over time, let the creator inspect supporting and challenging evidence, revise or confirm the interpretation, then create one small project artifact from the confirmed insight. The product does not assess the creator’s personality or psychological traits.

## Hackathon model requirement

At least one Meta model must contribute to the working product path. Select the model and task only after checking current access and official documentation; record what the model does, what deterministic code validates, and how source provenance survives the call. A fixture provider is for repeatability and fallback, not a substitute for demonstrating Meta-model use in the final demo.

## Product principles

- Evidence before interpretation; interpretation before generation.
- Time is a first-class dimension: preserve dates, sequences, and change.
- Make uncertainty and alternative explanations legible.
- User meaning is authoritative: confirmation is explicit, revocable, and recorded.
- Show provenance at the point of every claim.
- Prefer a few specific discoveries to a feed of generic observations.
- Keep the user in control of what is imported and used.

## Success for the hackathon

A judge can understand the value in a short live demo, trace the featured insight to source items, see the system handle a challenge without defensiveness, and leave with a user-confirmed artifact. See `docs/EVALS.md` and `docs/DEMO.md`.
