# Repository working agreements

## Product boundary

SHOWME turns demonstrations into understanding. It learns a constrained process model from an expert's multimodal demonstration, observes another person's attempt, detects and grounds meaningful divergence, guides recovery, and can later answer procedural what-if questions.

## Hackathon constraints

- SHOWME is the authoritative product direction. THREAD code, fixtures, and research are legacy material; inspect before reuse and preserve useful infrastructure.
- The proof-of-magic experiment precedes application UI. Do not claim a capability until it passes a recorded, repeatable experiment.
- P0 is one short physical task: learn from an expert video, observe a correct learner attempt and deliberate error, detect the divergence, and recognize recovery.
- Separate model observations, process hypotheses, human-authored ground truth, deterministic checks, and evaluation results. Never expose evaluation labels to the model.
- Keep provenance for every observation: source clip, frame/time reference, model/version, and whether the statement is observed or inferred.
- Use Meta models substantively in the demo path. Muse Spark provides multimodal interpretation; SAM provides object masks/tracks, not process reasoning. Verify API behavior and cost before depending on it.
- Do not represent a constrained procedural simulation as physics simulation. Do not let simulation displace the P0 observation-and-recovery loop.
- Start with local, prerecorded clips. No robotics control, arbitrary YouTube ingestion, general skill library, authentication, or production infrastructure in P0.
- Keep secrets and private media out of Git. Prefer hands-only recordings and remove clips and derived data when no longer needed.
- Keep model providers behind a narrow adapter. Treat model output as untrusted input and validate it before state changes or guidance.
- The official demo is three minutes and must clearly identify work built during Oct 27–Nov 4, 2026.

## Learning while building

- Explain the engineering concept and why it matters before a meaningful implementation task.
- Give one bounded exercise at a time with observable acceptance criteria. Leave conceptually important implementation to the user; handle repetitive setup and generated boilerplate.
- Review the user's implementation candidly, explain tradeoffs, and continue with the next exercise. Adapt teaching to the deadline without turning each task into a lecture.
- The process representation and evaluation labels are central reasoning work. Do not silently author them on the user's behalf.

## Current entry point

Read docs/SHOWME_PROOF_OF_MAGIC.md before adding implementation. Existing THREAD documentation, mockups, and UI are not SHOWME specifications.
