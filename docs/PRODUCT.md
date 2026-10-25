# Product brief

## One sentence

THREAD is a multimodal personal creative intelligence system that turns personal history into temporal memories, discovers evidence-backed insights, and helps a person investigate and confirm meaning before creating artifacts.

## Problem

A person's photos, notes, voice recordings, messages, documents, and creative work hold useful patterns across time. These materials are fragmented, hard to revisit, and easy to misread when an AI compresses them into a confident narrative. Most creative tools start at generation; THREAD starts with evidence and understanding.

## Product promise

Help people see what has been changing, recurring, conflicting, or connecting across their own history—and make it easy to inspect why THREAD thinks so.

## Core model

1. **History → memories.** Ingest a deliberately bounded set of user-provided multimodal items. Extract time, modality, entities, topics, and concise memory records with source provenance.
2. **Memories → candidates.** Find recurring patterns, contradictions, evolution, and cross-domain connections. Each candidate is a hypothesis with evidence, time span, confidence, and counter-evidence where available.
3. **Candidates → investigation.** Retrieve supporting and disconfirming material; test whether a candidate is specific, temporally coherent, and adequately evidenced. Suppress weak or redundant candidates.
4. **Investigation → interview.** Ask a small number of grounded, open questions. The user can confirm, revise, reject, or defer an interpretation.
5. **Confirmed insight → artifact.** Only after human confirmation, offer a useful creation path such as a personal essay, project brief, creative prompt, or timeline.

## User and use case

Initial user: a reflective, creative person with a small personal archive who wants to understand their evolving interests and turn a meaningful realization into something actionable or expressive.

Hackathon use case: given a curated sample history, show one surprising but defensible insight across time, let the user inspect evidence and challenge it, interview them to develop it, then create one artifact from the confirmed insight.

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
