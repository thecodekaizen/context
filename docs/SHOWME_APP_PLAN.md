# SHOWME app experience and mockup plan

**Status:** experience outline only; no SHOWME screens or mockups have been built.
**Gate:** keep app implementation behind the P0 experiment gate in [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md). Planning screens now does not mean the capability is proven.

## Experience principle

SHOWME is a camera-first, task-scoped guide. The learner should see the work area and the next useful intervention, not a generic chat or analytics dashboard. Every warning must be tied to visible evidence and allow the learner to inspect or correct it.

The interface serves two demo moments:

1. **Catch the mistake:** recognize progress, detect a meaningful divergence, point to the relevant object or location, and explain the observed evidence.
2. **Show the alternative:** let the learner ask a bounded “what if?” question and visualize the predicted procedural state and violated prerequisite.

## Planned screen/state sequence

| Order | Screen or state | What the learner sees / does | Gate |
|---|---|---|---|
| 1 | Skill selection / setup | Choose the single learned task; see camera, privacy, and task boundaries | Minimal; no account system |
| 2 | Learn from demonstration | Video capture/import, narration status, extracted objects/actions/states, and evidence frames; review/edit the candidate process | After learning output is inspectable |
| 3 | Camera-first guidance | Live or prerecorded learner view, current step, acknowledged progress, and an unobtrusive observe state | After CLI recognizes correct states reliably |
| 4 | Divergence intervention | Freeze/highlight the evidence frame, name the suspected mismatch with uncertainty, explain what differed, offer “show me” or dismiss | After a deliberate mistake is detected with evidence |
| 5 | Recovery | Observe correction, confirm the state is back on a valid path, then resume guidance | After a separate recovery attempt passes |
| 6 | What-if simulator | Select a bounded action order; show predicted process state and prerequisite violation, with a visual before/after | P1 only, after P0; procedural state visualization first |
| 7 | Skill result / shareable procedure | Review the learned process and evidence; export a compact skill record if useful | Only if time remains and core demo is stable |

These are states in one guided task flow, not a commitment to seven separate routes or a broad product surface. For the hackathon, a single focused camera/workspace screen with progressive overlays may serve screens 3–6.

## Mockups to create

Create in this order, after the physical task and evidence vocabulary are stable:

1. `01-guided-task.png` — normal progress in the camera-first workspace.
2. `02-divergence.png` — deliberate mistake, grounded highlight, evidence and recovery prompt.
3. `03-recovery.png` — corrected state recognized and guidance resumed.
4. `04-what-if.png` — procedural alternative and resulting state visualization, only if P0 passes.
5. `05-learn-review.png` — expert demonstration with extracted steps and inspectable evidence.

For each mockup, record the task state shown, the evidence backing each claim, interaction behavior, and any capability still represented as a prototype. Use SHOWME naming and content. The existing `00-thread-direction-board.png` is archived THREAD exploration, not a SHOWME design reference.

## Visual behavior requirements

- Keep the physical scene dominant; guidance should not obscure hands, objects, or the relevant workspace.
- Distinguish **observed**, **inferred**, and **uncertain** information in plain language.
- Ground warnings in a frame/time and, when available, a segmentation mask. Never imply SAM establishes procedural correctness.
- Make pause, dismiss, and “I did that intentionally” available during interventions.
- Show step status as observed progress, not as a rigid coordinate/timestamp script.
- “What if?” output must be labeled as a procedural prediction; do not depict unsupported physical simulation.
- Include a visible camera/privacy state and avoid recording beyond the chosen task session.

## Current UI inventory

- `apps/web/` is a pre-pivot THREAD prototype. It is not the SHOWME app and should not be shown as hackathon product work.
- No SHOWME mockup is currently present in `design/mockups/`.
- The proof-of-magic CLI and evaluation are the active product work until P0 passes.
