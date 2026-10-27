# Repository working agreements

## Product boundary

SHOWME's product definition is locked in [`docs/PRODUCT.md`](docs/PRODUCT.md): exactly three surfaces—Teach, Do, Simulate—over one shared Skill Model. Teach creates it, Do executes against it, and Simulate explores it. Do not reopen product or category exploration; narrow implementation/task details only when evidence requires it.

## Hackathon constraints

- SHOWME is the authoritative product direction. THREAD code, fixtures, and research are legacy material; inspect before reuse and preserve useful infrastructure.
- Keep controlled proof/evaluation work moving alongside the final Teach → Do → Simulate product implementation. Do not claim a capability until it passes a recorded, repeatable experiment.
- The hackathon submission demonstrates one safe assembly task with roughly 4–6 pieces and an observable ordering or orientation constraint: learn it, guide a learner through it, catch and ground a mistake, recognize recovery, then simulate an alternative from the same Skill Model.
- Separate model observations, process hypotheses, human-authored ground truth, deterministic checks, and evaluation results. Never expose evaluation labels to the model.
- Keep provenance for every observation: source clip, frame/time reference, model/version, and whether the statement is observed or inferred.
- Use Meta models substantively in the demo path. Muse Spark provides multimodal interpretation; SAM provides object masks/tracks, not process reasoning. Verify API behavior and cost before depending on it.
- Simulation is a mode of the learned skill, not a separate product. It must use the same Skill Model as Teach and Do, and visually explain alternative state, consequence, violated constraint, and recovery. Do not claim arbitrary physics or arbitrary-task learning.
- Use prerecorded clips for controlled evaluation and a camera-first active task session for the final experience. No robotics control, arbitrary YouTube ingestion, general skill marketplace, authentication, or production infrastructure.
- Keep secrets and private media out of Git. Prefer hands-only recordings and remove clips and derived data when no longer needed.
- Keep model providers behind a narrow adapter. Treat model output as untrusted input and validate it before state changes or guidance.
- The official demo is three minutes and must clearly identify work built during Oct 27–Nov 4, 2026.

## Learning while building

- Explain the engineering concept and why it matters before a meaningful implementation task.
- Give one bounded exercise at a time with observable acceptance criteria. Leave conceptually important implementation to the user; handle repetitive setup and generated boilerplate.
- Review the user's implementation candidly, explain tradeoffs, and continue with the next exercise. Adapt teaching to the deadline without turning each task into a lecture.
- The process representation and evaluation labels are central reasoning work. Do not silently author them on the user's behalf.

## Current entry point

Read docs/PRODUCT.md first for the locked product contract, then docs/SHOWME_PROOF_OF_MAGIC.md for experiment evidence and boundaries. Existing THREAD documentation, mockups, and UI are not SHOWME specifications.
