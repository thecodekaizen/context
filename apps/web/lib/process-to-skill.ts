import type { SkillModel } from "./skill-model";

type ProcessCandidate = {
  task_summary: string;
  objects: { id: string; label: string; visual_description: string }[];
  states: { id: string; description: string }[];
  transitions: {
    id: string;
    action: string;
    object_ids: string[];
    from_state: string;
    to_state: string;
    preconditions: string[];
    postconditions: string[];
    evidence: { start_seconds: number; end_seconds: number; observation: string }[];
  }[];
};

/** Convert a reviewed API candidate into the shared app representation. */
export function processToSkill(
  candidate: ProcessCandidate,
): SkillModel {
  const firstTransition = candidate.transitions[0];
  return {
    id: "learned-process",
    title: candidate.task_summary,
    status: "learned-from-demonstration",
    initialState: firstTransition ? [firstTransition.from_state] : [],
    states: candidate.states.map((state) => ({ id: state.id, label: state.description })),
    objects: candidate.objects.map((object, index) => ({
      id: object.id,
      name: object.label,
      color: ["amber", "blue", "copper", "stone"][index % 4],
      shape: "component",
      visualDescription: object.visual_description,
    })),
    actions: candidate.transitions.map((transition) => ({
      id: transition.id,
      label: transition.action,
      objectId: transition.object_ids[0] ?? "unknown",
      // Free-text model preconditions are shown for review, never executed.
      requires: [],
      produces: [transition.to_state, ...transition.postconditions],
      fromState: transition.from_state,
      toState: transition.to_state,
      explanation: transition.evidence.map((item) => item.observation).join(" "),
      recovery: "Return to a state supported by the demonstration, then review the transition evidence.",
      evidence: transition.evidence.map((item) => ({
        startSeconds: item.start_seconds,
        endSeconds: item.end_seconds,
        observation: item.observation,
      })),
    })),
  };
}
