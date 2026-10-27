# SHOWME interactive simulation design

**Product role:** Simulate is one of SHOWME's three modes over the same Skill Model used by Teach and Do. It is not a separate product or a disconnected simulation feature.

## What the user does

At any point in Do, the user can enter Simulate and ask a bounded question such as **“What if I put the cap on before the spacer?”** SHOWME translates that question into an alternate action sequence, lets the user inspect or adjust that sequence, and plays the resulting task state forward. The learner can compare it with the demonstrated successful sequence, see which prerequisite is broken, inspect the resulting physical arrangement, and return to Do without losing skill/task context.

The simulation should feel like changing the task and seeing its consequences, not reading a generated answer beside a static model.

## Shared process model

The learner loop and simulator consume one versioned task representation:

```text
Demonstration + learner observations
            ↓
Evidence-linked process proposal
  objects · states · actions · relations · uncertainty
            ↓ human-inspectable task model
      ┌─────┴─────────┐
      ↓               ↓
Learner guidance   Interactive task simulation
```

The model proposes semantic objects, actions, states, and relationships from the demonstration. Every learned claim carries frame/time evidence. A single demonstrated order is evidence that the order occurred; it is not, by itself, proof that the order is required. A procedural prerequisite must be supported by repeatable observations, a deliberate alternative attempt, or an explicitly disclosed task-specific constraint. Never silently promote a manually configured rule to a learned fact.

At runtime, distinguish **proposed constraints** from **confirmed constraints**. A proposed precondition from one model pass remains visible for review but is not enforced. Simulate may block an action only for a confirmed constraint, and the Skill Model records its source (`expert narration`, `repeatable observation`, `human confirmation`, or an explicitly illustrative fixture) and any supporting evidence. This keeps “not seen in the demonstration” from turning into “impossible” or “unsafe.”

## Minimum shared Skill Model and task scene

Keep the scene contract small and specific to the selected task:

- **Part:** stable semantic ID, display name, render asset, and task-local dimensions/anchor points.
- **Scene state:** part poses/relations and completion flags in a named state.
- **Action primitive:** semantic action ID mapped to an allowed scene transition, such as place, align, insert, attach, or remove.
- **Precondition:** required prior state or spatial relation, with provenance identifying whether it was model-proposed, observed, or configured for rendering.
- **Effect:** resulting scene state, including object transform/attachment and completion status.
- **Evidence link:** source clip and timestamp/frame supporting learned semantics or a constraint.

Example shape (illustrative, not the final task contract):

```json
{
  "action": "place_cap",
  "preconditions": ["spacer_on_base"],
  "effects": ["cap_seated_on_spacer"],
  "evidence": [{"source": "expert-clip", "start_s": 8.2, "end_s": 10.1}],
  "constraint_basis": "validated_task_relation"
}
```

The scene supplies geometry and presentation. It does not supply the procedure's truth. The Skill Model supplies the candidate procedure; local deterministic simulation applies the selected action sequence to scene state and reports exactly which declared precondition or state relation fails.

## Interaction and visual behavior

1. Show the successful demonstrated sequence and current assembly state.
2. Let the user select an action and move it earlier/later, or ask a spoken/text “what if?” question.
3. Show the proposed sequence before running it so the user can edit or cancel.
4. Play the changed sequence as a visual state progression of the task, one action at a time, with timed play/pause, previous/next step, replay, reset, and comparison controls. Playback advances through deterministic model results and stops at the final or blocked step; it does not animate continuous physical motion.
5. At divergence, stop on the resulting physical arrangement; highlight the relation/part involved and name the violated prerequisite.
6. Offer the recovery sequence and allow the user to return to the successful sequence.
7. Keep the simulated state separate from the real camera state. Clearly label it as a simulation and never claim it observed a physical outcome that only exists in the scene.

## Runtime responsibilities

- **Muse Spark:** interpret the bounded “what if?” intent against the learned process and propose the alternate action sequence plus a concise explanation. It does not decide the simulation's resulting geometry.
- **Local process engine:** validate action IDs, apply preconditions/effects, derive the resulting state, and return a structured explanation with provenance. Same model and sequence must produce the same state.
- **Simulation view:** render task parts, poses, attachments, and action transitions. It reflects the deterministic state result; it does not infer correctness from pixels.
- **SAM 3.1:** optionally grounds objects in the physical camera view for mistake explanations. SAM does not power the simulator's procedure logic.

## Final-demo acceptance

- The selected task is consistent across demonstration, learner observation, recovery, and simulation.
- The simulator consumes the reviewed process model rather than a second, hidden hand-authored procedure.
- The user can change an action order and play, pause, step, reset, and compare the visual alternative.
- The scene visibly reaches the predicted physical arrangement or blocked/incomplete state.
- The violated constraint is present in the process model, has a recorded basis, and matches deterministic evaluation output.
- The successful sequence and recovery path remain available.
- A clean-start demo can repeat the same what-if interaction with the same result.

## Fidelity boundary

The target is a **real, interactive visual simulation of one selected procedure**, including its task geometry, state transitions, ordering/orientation constraints, and resulting arrangement. Do not call a static diagram or text-only rule check a simulation. Simulate the chosen task's actual geometry and state changes. Do not imply arbitrary physical-world or general-purpose physics simulation.

The concept screen is [`../design/mockups/02-what-if-procedure-preview.png`](../design/mockups/02-what-if-procedure-preview.png). Its motor-mount illustration is not the final selected task.
