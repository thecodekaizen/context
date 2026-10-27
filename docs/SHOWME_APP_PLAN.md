# SHOWME final app plan

**Product definition is locked:** see [`PRODUCT.md`](PRODUCT.md). The app has exactly three surfaces—Teach, Do, Simulate—and one shared Skill Model. The two existing images are concepts, not implemented screens.

## Product shell

One camera-first skill workspace. Its top-level navigation is **Teach · Do · Simulate**. All three modes operate on the currently selected Skill Model. Do not add account flows, dashboards, marketplaces, social feeds, analytics, or generic chat.

## Teach — create the Skill Model

- Record a demonstration in-app or upload a permitted video.
- Allow natural expert narration and retain it as a separate evidence stream when supported.
- Extract 4–6 task objects, actions, observable states, transitions, ordering/orientation relations, candidate constraints, and recovery possibilities.
- Present the resulting Skill Model with clip/frame evidence and uncertainty. Let the expert correct object/action names or reject unsupported constraints before saving the skill.
- Preserve model identity and provenance. Distinguish what the video directly shows from what the system infers.

## Do — execute against the Skill Model

- Start a camera-first task session and show the work area as the primary content.
- Maintain a persistent estimate of current task state across observations; do not treat every frame as an unrelated caption.
- Acknowledge correctly completed actions and present the next relevant guidance.
- On meaningful divergence, pause/flag the task, highlight the grounded object or location, cite the visual evidence, and explain the issue without overstating certainty.
- Offer the applicable recovery path, then continue observing until the learner's state is back on a valid path.
- Keep pause, resume, dismiss/intentional-action, and camera state visible.

## Simulate — explore the same Skill Model

- Make this mode available from an active skill at any point; return to Do without losing the skill or task context.
- Accept a bounded natural-language “what if?” or let the user edit an action sequence directly.
- Translate the request into a proposed alternative sequence; show it for review before applying it.
- Run the alternative against the same Skill Model and visually animate the resulting task state.
- Explain the physical consequence, the specific violated constraint, the evidence/basis for that constraint, and a recovery path.
- Let the user compare the demonstrated valid sequence with the alternative and reset or return to the learner's actual camera state.

## Final demo flow

1. **Teach:** expert demonstrates a single assembly task once, with optional narration; SHOWME creates an evidence-linked Skill Model.
2. **Do:** learner works from a different arrangement or reasonable viewpoint while SHOWME tracks state.
3. **Intervene:** learner intentionally makes a visible mistake; SHOWME highlights and explains it.
4. **Recover:** learner corrects the task; SHOWME recognizes the restored state and resumes.
5. **Simulate:** learner asks “What if I attach this first?”; SHOWME applies it to the same Skill Model and visually explains the result and recovery.

## Visual/mockup inventory

- [`01-guided-task-states.png`](../design/mockups/01-guided-task-states.png): concept states for Do (normal guidance, divergence, recovery).
- [`02-what-if-procedure-preview.png`](../design/mockups/02-what-if-procedure-preview.png): concept for Simulate (alternate sequence and consequence).
- **Teach mockup still needed:** demonstration capture/narration and evidence-linked Skill Model review.

Current implementation screenshots are under [`design/screenshots`](../design/screenshots/README.md) and are embedded in the root README. They document the local prototype separately from these concept mockups.

The current mockups use an illustrative washer/bracket assembly. It is not the selected task or evidence that mistake detection works. Once the 4–6-piece task is selected, make Teach, Do, and Simulate use that same task vocabulary and visual assets.

## Implementation status

- Teach now supports both video upload and browser-camera recording; the recorded clip stays local until the user submits it to Muse Spark for analysis.

- Product contract: locked in [`PRODUCT.md`](PRODUCT.md).
- Concept mockups: two created; Teach concept missing.
- SHOWME web prototype: Teach, Do, and Simulate are implemented in `apps/web/` over a shared Skill Model. Teach accepts video and requires human review before activating the candidate; model-proposed prerequisites stay unenforced unless the reviewer explicitly maps one to an observed state. Do supports explicit single-frame checks and recorded learner-clip analysis; neither is continuous state tracking. Simulate lets users reorder actions, deterministically replays the proposed sequence from the model's initial state, and steps through each resulting state, stopping on confirmed constraints or reporting an unobserved transition. Its current scene view is procedural, not geometric or physical simulation.
- A reviewed process can be persisted in browser-local storage; learner videos and camera frames are not saved by the app.
- The prototype has not passed the matched controlled experiment. Previous footage experiments have produced both a missed annotated error and a separate single-clip extraction smoke test; see the linked run reports in [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md).
- Current technical evidence and build sequence: [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md) and [`SHOWME_PROOF_OF_MAGIC.md`](SHOWME_PROOF_OF_MAGIC.md).
