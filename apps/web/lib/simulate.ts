import type { SkillAction, SkillConstraint, SkillModel } from "./skill-model";

export type SimulationResult =
  | { accepted: true; state: string[]; action: SkillAction; message: string }
  | { accepted: false; state: string[]; action: SkillAction; missing: string[]; kind: "blocked"; message: string; blockedBy: Extract<SkillConstraint, { status: "confirmed" }>[] }
  | { accepted: false; state: string[]; action: SkillAction; missing: string[]; kind: "unobserved"; message: string };

export type SequenceSimulation = {
  status: "completed" | "blocked" | "unobserved";
  initialState: string[];
  finalState: string[];
  steps: { index: number; result: SimulationResult }[];
};

/** Apply one proposed action against preconditions from the same Skill Model. */
export function simulateAction(
  model: SkillModel,
  currentState: string[],
  actionId: string,
): SimulationResult {
  const action = model.actions.find((candidate) => candidate.id === actionId);
  if (!action) throw new Error(`Unknown action: ${actionId}`);

  const blockedBy = action.constraints
    .filter((constraint) => constraint.status === "confirmed")
    .filter((constraint) => !currentState.includes(constraint.requiredState));
  const missing = blockedBy.map((constraint) => constraint.requiredState);
  if (missing.length > 0) {
    return {
      accepted: false,
      state: currentState,
      action,
      missing,
      blockedBy,
      kind: "blocked",
      message: `This action cannot be completed yet. ${action.explanation}`,
    };
  }

  if (model.status === "learned-from-demonstration" && action.fromState && !currentState.includes(action.fromState)) {
    return {
      accepted: false,
      state: currentState,
      action,
      missing: [action.fromState],
      kind: "unobserved",
      message: "This action was not observed from the current state. One demonstration cannot tell us whether the alternative is impossible or unsafe.",
    };
  }

  return {
    accepted: true,
    state: [...new Set([...currentState.filter((item) => item !== action.fromState), ...action.produces])],
    action,
    message: `${action.label} can proceed. ${action.explanation}`,
  };
}

export function completedActions(model: SkillModel, state: string[]) {
  return model.actions.filter((action) => action.produces.every((condition) => state.includes(condition)));
}

/** Replay a proposed order from a clean initial state, stopping at its first failure. */
export function simulateSequence(model: SkillModel, actionIds: string[]): SequenceSimulation {
  const initialState = [...model.initialState];
  let state = [...initialState];
  const steps: SequenceSimulation["steps"] = [];

  for (const [index, actionId] of actionIds.entries()) {
    const result = simulateAction(model, state, actionId);
    steps.push({ index, result });
    if (!result.accepted) {
      return {
        status: result.kind,
        initialState,
        finalState: state,
        steps,
      };
    }
    state = result.state;
  }

  return { status: "completed", initialState, finalState: state, steps };
}
