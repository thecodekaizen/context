# SHOWME product definition

**Status: LOCKED for the Meta Global AI Developer Hackathon 2026.** Do not reopen product/category exploration during implementation. Narrow the chosen task or implementation when evidence requires it; keep the product loop intact.

## Product

**SHOWME is a camera-first AI that learns a physical task from a demonstration, watches another person perform it, catches mistakes, guides recovery, and lets them simulate “what if?” alternatives.**

> SHOWME transforms a visual demonstration into an executable model of a physical procedure.

Simulation is a mode of the learned skill, not a separate product. The **Skill Model is the product**:

- **Teach creates it.**
- **Do executes against it.**
- **Simulate explores it.**

## The three surfaces

### Teach

Record or upload one expert demonstration. The expert may narrate naturally. SHOWME extracts objects, actions, observable states, transitions, dependencies, constraints, and recovery possibilities into an evidence-linked, inspectable Skill Model. Preserve uncertainty; a single observed ordering is not automatically a proven prerequisite.

### Do

The learner points a camera at the workspace and performs the task. SHOWME maintains a persistent estimate of the learner's physical state against the Skill Model. It acknowledges correct progress, highlights meaningful divergence, explains the evidence, gives a recovery path, and recognizes when the learner is back in a valid state.

### Simulate

At any point, the learner asks or selects a bounded alternative such as “What if I attach this first?” SHOWME applies that alternative to the same Skill Model and visually shows the resulting state, constraint violation, consequence, and recovery. The user can return to Do with the learned skill and current physical state intact.

## One coherent loop

```text
Teach ──creates──> Skill Model
                      │
            ┌─────────┴──────────┐
            │                    │
      Do executes it       Simulate explores it
            │                    │
            └── observations ────┘
```

Do and Simulate are two modes over the same task model, not independent AI features or products. Evidence/provenance and model output must remain attached to Skill Model claims so the user can inspect why SHOWME guided or predicted an outcome.

## Hackathon scope

Make **one** visually obvious assembly task spectacular. Choose a safe task with roughly 4–6 distinct pieces and at least one observable ordering or orientation constraint. The final story is:

1. An expert demonstrates it once; SHOWME builds the Skill Model.
2. A learner performs it from a different arrangement or reasonable viewpoint.
3. SHOWME follows progress, catches an intentional mistake, highlights and explains it.
4. The learner corrects the state; SHOWME recognizes recovery.
5. The learner changes an action; Simulate shows the alternative consequence from the same Skill Model.

The controlled recordings used for evaluation can be prerecorded. The final product experience is camera-first and maintains the learner state over an active task session. Verify the supported model/API interaction pattern and latency before claiming live model-streaming; repeated frame/clip observations may be needed.

## Product boundaries

The product has only three surfaces: **Teach, Do, Simulate**. It does not need dashboards, skill marketplaces, social feeds, analytics, accounts, generic chat, broad integrations, arbitrary task support, robot control, or a general-purpose physics engine. Do not claim arbitrary physics or arbitrary-task learning. Simulation must visually explore the learned task model; its physical fidelity is bounded by the selected task and supported evidence.

## Shared implementation contract

The Skill Model must be a single versioned representation used by Teach, Do, and Simulate. It contains only the task's necessary objects, states, actions, transitions, relations/constraints, evidence, uncertainty, and recovery paths. Keep human ground truth and evaluation labels separate. Never claim a hand-authored constraint was learned from the demonstration without disclosing its source.

Technical experiment criteria and current evidence are in [`SHOWME_PROOF_OF_MAGIC.md`](SHOWME_PROOF_OF_MAGIC.md), [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md), and [`DAILY_LOG.md`](DAILY_LOG.md). The app flow is in [`SHOWME_APP_PLAN.md`](SHOWME_APP_PLAN.md); simulation behavior is in [`SHOWME_SIMULATION_DESIGN.md`](SHOWME_SIMULATION_DESIGN.md).
