# SHOWME final app plan

**Product definition is locked:** see [`PRODUCT.md`](PRODUCT.md). The app has exactly three surfaces—Teach, Do, Simulate—and one shared Skill Model. Concept images are design references, not implemented screens or capability evidence.

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
- Accept a bounded natural-language “what if?” or let the user edit an action sequence directly. The current local interpreter handles explicit before/after/first requests by matching action and names of every involved object in the active Skill Model; ambiguous or unmatched wording is rejected. The model preserves multi-part action relationships from the learned process instead of dropping all but its first object.
- Show the interpreted order for review; only after the user accepts does it update the editable proposal. The user explicitly runs the deterministic simulator afterward.
- Run the alternative against the same Skill Model and play through its deterministic state changes with timed playback or manual stepping. Continuous physical animation awaits the selected task geometry.
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
- [`03-teach-skill-model-review.png`](../design/mockups/03-teach-skill-model-review.png): concept for demonstration capture/playback and human review of the evidence-linked Skill Model.

Current implementation screenshots are under [`design/screenshots`](../design/screenshots/README.md) and are embedded in the root README. They document the local prototype separately from these concept mockups.

The current mockups use an illustrative washer/bracket assembly. It is not the selected task or evidence that mistake detection works. Once the 4–6-piece task is selected, make Teach, Do, and Simulate use that same task vocabulary and visual assets.

## Implementation status

- Teach supports video upload/browser-camera recording and optional task-instruction PDF upload. With a PDF, Muse Spark can derive intended steps from the reference even when the video omits them, while keeping manual page/step citations separate from timestamped video evidence. Both files are sent only when the user explicitly requests process generation; the candidate still requires human review.
- Do can also record a learner attempt locally or accept an uploaded clip; both Teach and Do previews can download the clip to the user's device. **Learn this skill** and **Observe attempt** remain explicit model-call actions. Camera streams are stopped when the user leaves that surface.

- Product contract: locked in [`PRODUCT.md`](PRODUCT.md).
- Concept mockups: three created for Do, Simulate, and Teach; the new Teach concept is generated design art, not an app screen.
- SHOWME web prototype: Teach, Do, and Simulate are implemented in `apps/web/` over a shared Skill Model. Teach accepts uploaded or browser-recorded video and requires human review before activating the candidate; model-proposed prerequisites stay unenforced unless the reviewer explicitly maps one to an observed state. Do supports local clip recording/upload, explicit single-frame checks, a local session timeline of the last 12 manual frame checks, and recorded learner-clip analysis; it does not continuously track state. When a reviewed process includes manual citations, learner-clip analysis returns one status and next action for every cited transition, links visible checks to timestamps, and keeps absent or unclear steps distinct from mismatches. Divergences and recovery remain model-reported claims that need human review. After a snapshot, the user can explicitly send one named Skill Model object and the same still frame to SAM 3.1; after learner-clip analysis, each reported divergence can also send one selected timestamp frame and a named object to SAM. The backend decodes returned boxes/masks with Meta's official parser, and Do overlays those regions on the captured image. Both are opt-in single-frame calls. SAM can return no match, and its phrase-based segmentation does not validate task correctness. Simulate lets users reorder actions, deterministically replays the proposed sequence from the model's initial state, and supports timed Play/Pause/Replay plus manual stepping, stopping on confirmed constraints or reporting an unobserved transition. A model-driven transition map now highlights completed, current, and upcoming states for both the illustrative fixture and reviewed models, including every involved part and model evidence when available. A bounded local “what if?” interpreter can propose an alternate order from explicit action/object names; the user previews and accepts the order before running simulation. It does not call an LLM or infer unrestricted intent. After a clear one-frame match in Do, the learner can explicitly open Simulate from that state; only actions remaining in the observed linear trace are included. Unclear, possible-divergence, and unmapped states cannot seed this flow. After a run, Simulate compares the remaining reference trace’s final modeled state with the alternative’s final modeled state, using the same Skill Model and distinguishing an observed trace from the illustrative fixture. The current scene view is procedural, not geometric or physical simulation; task-specific geometry awaits selection of the LEGO procedure.
- A reviewed process can be persisted in browser-local storage; learner videos and camera frames are not saved by the app.
- The prototype has not passed the matched controlled experiment. Previous footage experiments have produced both a missed annotated error and a separate single-clip extraction smoke test; see the linked run reports in [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md).
- Current technical evidence and build sequence: [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md) and [`SHOWME_PROOF_OF_MAGIC.md`](SHOWME_PROOF_OF_MAGIC.md).
