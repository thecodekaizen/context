import type { SkillAction, SkillModel } from "./skill-model";

export type SimulationResult =
  | { accepted: true; state: string[]; action: SkillAction; message: string }
  | { accepted: false; state: string[]; action: SkillAction; missing: string[]; kind: "blocked" | "unobserved"; message: string };

/** Apply one proposed action against preconditions from the same Skill Model. */
export function simulateAction(
  model: SkillModel,
  currentState: string[],
  actionId: string,
): SimulationResult {
  const action = model.actions.find((candidate) => candidate.id === actionId);
  if (!action) throw new Error(`Unknown action: ${actionId}`);

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

  const missing = action.requires.filter((condition) => !currentState.includes(condition));
  if (missing.length > 0) {
    return {
      accepted: false,
      state: currentState,
      action,
      missing,
      kind: "blocked",
      message: `This action cannot be completed yet. ${action.explanation}`,
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
