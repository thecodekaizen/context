# SHOWME app experience and mockup plan

**Status:** experience outline plus two concept mockups. These are visual proposals, not implemented or validated product screens.
**Submission target:** a complete, task-scoped experience: learn a demonstration, guide a learner, detect and recover from divergence, and interactively simulate a changed action order. The screens remain concepts until implemented and tested.

## Experience principle

SHOWME is a camera-first, task-scoped guide. The learner should see the work area and the next useful intervention, not a generic chat or analytics dashboard. Every warning must be tied to visible evidence and allow the learner to inspect or correct it.

The interface serves two demo moments:

1. **Catch the mistake:** recognize progress, detect a meaningful divergence, point to the relevant object or location, and explain the observed evidence.
2. **Show the alternative:** let the learner change an action order and watch a 3D procedural simulation show the resulting arrangement, violated prerequisite, and recovery path.

## Planned screen/state sequence

| Order | Screen or state | What the learner sees / does | Gate |
|---|---|---|---|
| 1 | Skill selection / setup | Choose the single learned task; see camera, privacy, and task boundaries | Minimal; no account system |
| 2 | Learn from demonstration | Video capture/import, narration status, extracted objects/actions/states, and evidence frames; review/edit the candidate process | After learning output is inspectable |
| 3 | Camera-first guidance | Live or prerecorded learner view, current step, acknowledged progress, and an unobtrusive observe state | After CLI recognizes correct states reliably |
| 4 | Divergence intervention | Freeze/highlight the evidence frame, name the suspected mismatch with uncertainty, explain what differed, offer “show me” or dismiss | After a deliberate mistake is detected with evidence |
| 5 | Recovery | Observe correction, confirm the state is back on a valid path, then resume guidance | After a separate recovery attempt passes |
| 6 | Interactive what-if simulator | Change the order of a learned action; scrub or step through a 3D scene showing the resulting physical arrangement, blocked/incomplete state, violated prerequisite, and recovery | Core final-demo moment; must use the same task and process model as learner guidance |
| 7 | Skill result / shareable procedure | Review the learned process and evidence; export a compact skill record if useful | Only if time remains and core demo is stable |

These are states in one guided task flow, not a commitment to seven separate routes or a broad product surface. For the hackathon, a single focused camera/workspace screen with progressive overlays may serve screens 3–6.

## Mockups to create

Create in this order, after the physical task and evidence vocabulary are stable:

1. **Done — concept:** [`01-guided-task-states.png`](../design/mockups/01-guided-task-states.png) — normal progress, a missing-washer warning, and recovery, shown as three states of one camera-first workspace.
2. **Done — concept:** [`02-what-if-procedure-preview.png`](../design/mockups/02-what-if-procedure-preview.png) — alternative step order, predicted process state, and recovery suggestion.
3. **Still to design:** learn/review a demonstration, with extracted steps, uncertain observations, and inspectable evidence frames.

The generated concept mockups use a small motor-mount/washer example only to make the interaction legible. **This is not the selected task or an assertion that SHOWME can detect a missing washer.** Replace the example and revise the screens after the controlled task and evidence vocabulary are chosen. The final demo should implement the what-if screen as a real, interactive 3D procedural simulation driven by the learned process representation, not as a static preview. Its physical fidelity is limited to the chosen task's geometry and state transitions; it does not claim general-purpose physics.

For each mockup, record the task state shown, the evidence backing each claim, interaction behavior, and any capability still represented as a prototype. Use SHOWME naming and content. The existing `00-thread-direction-board.png` is archived THREAD exploration, not a SHOWME design reference.

## Visual behavior requirements

- Keep the physical scene dominant; guidance should not obscure hands, objects, or the relevant workspace.
- Distinguish **observed**, **inferred**, and **uncertain** information in plain language.
- Ground warnings in a frame/time and, when available, a segmentation mask. Never imply SAM establishes procedural correctness.
- Make pause, dismiss, and “I did that intentionally” available during interventions.
- Show step status as observed progress, not as a rigid coordinate/timestamp script.
- Label the simulation's scope clearly: it is an interactive physical-state simulation for the selected task, not a general-purpose physics engine.
- Include a visible camera/privacy state and avoid recording beyond the chosen task session.

## Current UI inventory

- `apps/web/` is a pre-pivot THREAD prototype. It is not the SHOWME app and should not be shown as hackathon product work.
- Both SHOWME mockups are concepts only; no SHOWME screen has been implemented.
- The proof-of-magic CLI and evaluation establish the perception/process model that the complete app and simulator will use.
