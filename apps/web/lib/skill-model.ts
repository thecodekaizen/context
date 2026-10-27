/** The small shared contract that Teach, Do, and Simulate will all use. */
export type SkillObject = {
  id: string;
  name: string;
  color: string;
  shape: "base" | "washer" | "bracket" | "bolt" | "component";
  visualDescription?: string;
};

export type SkillAction = {
  id: string;
  label: string;
  objectId: string;
  requires: string[];
  produces: string[];
  /** Candidate states seen in one trace; these are not universal constraints. */
  fromState?: string;
  toState?: string;
  explanation: string;
  recovery: string;
  evidence?: { startSeconds: number; endSeconds: number; observation: string }[];
};

export type SkillModel = {
  id: string;
  title: string;
  status: "illustrative-fixture" | "candidate-needs-review" | "learned-from-demonstration";
  states?: { id: string; label: string }[];
  objects: SkillObject[];
  initialState: string[];
  actions: SkillAction[];
};

/**
 * A transparent interaction fixture, not a claim that this procedure has been
 * learned from video. Replace it with the model returned by Teach later.
 */
export const SAMPLE_SKILL: SkillModel = {
  id: "stacked-mount-fixture",
  title: "Stacked mount assembly",
  status: "illustrative-fixture",
  objects: [
    { id: "base", name: "Mounting base", color: "stone", shape: "base" },
    { id: "washer", name: "Spacer ring", color: "amber", shape: "washer" },
    { id: "bracket", name: "Support bracket", color: "blue", shape: "bracket" },
    { id: "bolt", name: "Fastener", color: "copper", shape: "bolt" },
  ],
  initialState: ["base_ready", "washer_available", "bracket_available", "bolt_available"],
  actions: [
    {
      id: "place-washer",
      label: "Place spacer ring",
      objectId: "washer",
      requires: ["base_ready", "washer_available"],
      produces: ["washer_seated"],
      explanation: "The spacer sits on the base before the bracket covers the joint.",
      recovery: "Lift the bracket, seat the spacer on the base, then replace the bracket.",
    },
    {
      id: "place-bracket",
      label: "Mount support bracket",
      objectId: "bracket",
      requires: ["base_ready", "bracket_available", "washer_seated"],
      produces: ["bracket_mounted"],
      explanation: "The bracket depends on the spacer being seated first.",
      recovery: "Remove the bracket, place the spacer ring, then mount the bracket again.",
    },
    {
      id: "insert-bolt",
      label: "Insert fastener",
      objectId: "bolt",
      requires: ["bracket_mounted", "bolt_available"],
      produces: ["fastener_inserted"],
      explanation: "The fastener locks the mounted bracket to the base.",
      recovery: "Back out the fastener, confirm the spacer is seated, then reassemble in order.",
    },
  ],
};
