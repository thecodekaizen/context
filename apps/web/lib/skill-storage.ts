const STORAGE_KEY = "showme.reviewed-skill.v1";

export type SavedProcess = {
  task_summary: string;
  objects: { id: string; label: string; visual_description: string }[];
  states: { id: string; description: string; observable_facts: string[] }[];
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
  ordering_observations: { before_transition_id: string; after_transition_id: string; evidence: { start_seconds: number; end_seconds: number; observation: string }[] }[];
  uncertainties: string[];
  _run?: { model?: string; usage?: { input_tokens?: number; output_tokens?: number }; source?: { duration_seconds?: number } };
  _validation?: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function isSavedProcess(value: unknown): value is SavedProcess {
  if (!isRecord(value) || typeof value.task_summary !== "string" || !Array.isArray(value.objects) || !Array.isArray(value.states) || !Array.isArray(value.transitions) || !Array.isArray(value.ordering_observations) || !Array.isArray(value.uncertainties)) return false;
  const isEvidence = (item: unknown) => isRecord(item) && typeof item.start_seconds === "number" && Number.isFinite(item.start_seconds) && typeof item.end_seconds === "number" && Number.isFinite(item.end_seconds) && typeof item.observation === "string";
  if (!value.objects.every((item) => isRecord(item) && typeof item.id === "string" && typeof item.label === "string" && typeof item.visual_description === "string")) return false;
  if (!value.states.every((item) => isRecord(item) && typeof item.id === "string" && typeof item.description === "string" && Array.isArray(item.observable_facts) && item.observable_facts.every((fact) => typeof fact === "string"))) return false;
  if (!value.transitions.every((item) => isRecord(item) && typeof item.id === "string" && typeof item.action === "string" && typeof item.from_state === "string" && typeof item.to_state === "string" && Array.isArray(item.object_ids) && item.object_ids.every((id) => typeof id === "string") && Array.isArray(item.preconditions) && item.preconditions.every((fact) => typeof fact === "string") && Array.isArray(item.postconditions) && item.postconditions.every((fact) => typeof fact === "string") && Array.isArray(item.evidence) && item.evidence.every(isEvidence))) return false;
  if (!value.ordering_observations.every((item) => isRecord(item) && typeof item.before_transition_id === "string" && typeof item.after_transition_id === "string" && Array.isArray(item.evidence) && item.evidence.every(isEvidence))) return false;
  return value.uncertainties.every((item) => typeof item === "string");
}

export function loadReviewedProcess(): SavedProcess | null {
  try {
    const serialized = localStorage.getItem(STORAGE_KEY);
    if (!serialized) return null;
    const saved: unknown = JSON.parse(serialized);
    if (!isRecord(saved) || saved.version !== 1 || !isSavedProcess(saved.process)) return null;
    return saved.process;
  } catch {
    return null;
  }
}

export function saveReviewedProcess(process: SavedProcess) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, process }));
  } catch {
    // Storage may be unavailable or full; the in-memory skill remains usable.
  }
}

export function clearReviewedProcess() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Clearing local persistence is best effort in restricted browser contexts.
  }
}
