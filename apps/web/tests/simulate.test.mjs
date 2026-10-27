import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

async function loadTypeScript(relativePath) {
  const source = await readFile(new URL(relativePath, import.meta.url), "utf8");
  const javascript = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  return import(`data:text/javascript;base64,${Buffer.from(javascript).toString("base64")}`);
}

const { simulateAction } = await loadTypeScript("../lib/simulate.ts");
const { processToSkill } = await loadTypeScript("../lib/process-to-skill.ts");

function modelFor(constraint, { fromState = "start" } = {}) {
  return {
    id: "test-skill",
    title: "Test skill",
    status: "learned-from-demonstration",
    objects: [],
    initialState: ["start"],
    actions: [{
      id: "attach-part",
      label: "Attach part",
      objectId: "part",
      constraints: constraint ? [constraint] : [],
      produces: ["attached"],
      fromState,
      toState: "attached",
      explanation: "Attach the part.",
      recovery: "Return to the demonstrated state.",
    }],
  };
}

test("a proposed constraint stays visible but does not block a transition", () => {
  const proposed = {
    id: "possible-support-order",
    description: "The support may need to be attached first.",
    status: "proposed",
    source: "model-hypothesis",
  };

  const result = simulateAction(modelFor(proposed), ["start"], "attach-part");

  assert.equal(result.accepted, true);
  assert.deepEqual(result.state, ["attached"]);
});

test("a confirmed constraint blocks with the missing state and its provenance", () => {
  const confirmed = {
    id: "support-before-part",
    requiredState: "support-attached",
    status: "confirmed",
    source: "expert-narration",
    evidence: [{ startSeconds: 2, endSeconds: 3, observation: "Expert says the support must be attached first." }],
  };

  const result = simulateAction(modelFor(confirmed), ["start"], "attach-part");

  assert.equal(result.accepted, false);
  assert.equal(result.kind, "blocked");
  assert.deepEqual(result.missing, ["support-attached"]);
  assert.equal(result.blockedBy[0].source, "expert-narration");
});

test("an unobserved action order is reported as unknown, not as a confirmed violation", () => {
  const result = simulateAction(modelFor(undefined, { fromState: "other-state" }), ["start"], "attach-part");

  assert.equal(result.accepted, false);
  assert.equal(result.kind, "unobserved");
  assert.equal(result.missing[0], "other-state");
});

test("preconditions from one learned trace stay proposed when converted to the shared model", () => {
  const skill = processToSkill({
    task_summary: "Attach a part",
    objects: [{ id: "part", label: "Part", visual_description: "A small part." }],
    states: [{ id: "start", description: "Part is loose." }, { id: "attached", description: "Part is attached." }],
    transitions: [{
      id: "attach-part",
      action: "Attach part",
      object_ids: ["part"],
      from_state: "start",
      to_state: "attached",
      preconditions: ["Support must be attached first."],
      postconditions: [],
      evidence: [{ start_seconds: 1, end_seconds: 2, observation: "The part is attached." }],
    }],
  });

  assert.deepEqual(skill.actions[0].constraints, [{
    id: "attach-part-hypothesis-1",
    description: "Support must be attached first.",
    status: "proposed",
    source: "model-hypothesis",
  }]);
  assert.equal(simulateAction(skill, ["start"], "attach-part").accepted, true);
});

test("an explicit human mapping promotes only that precondition and keeps its state requirement", () => {
  const skill = processToSkill({
    task_summary: "Attach a part",
    objects: [{ id: "part", label: "Part", visual_description: "A small part." }],
    states: [{ id: "start", description: "Part is loose." }, { id: "support-ready", description: "Support is attached." }, { id: "attached", description: "Part is attached." }],
    transitions: [{
      id: "attach-part",
      action: "Attach part",
      object_ids: ["part"],
      from_state: "start",
      to_state: "attached",
      preconditions: ["Support must be attached first.", "The part must be visible."],
      postconditions: [],
      evidence: [],
    }],
    human_confirmed_constraints: [{ transition_id: "attach-part", precondition_index: 0, required_state: "support-ready" }],
  });

  assert.deepEqual(skill.actions[0].constraints.map((constraint) => constraint.status), ["confirmed", "proposed"]);
  assert.equal(skill.actions[0].constraints[0].requiredState, "support-ready");
  assert.equal(skill.actions[0].constraints[0].source, "human-confirmation");
  assert.equal(simulateAction(skill, ["start"], "attach-part").kind, "blocked");
});
