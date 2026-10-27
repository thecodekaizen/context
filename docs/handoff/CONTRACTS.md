# Preserve shared contracts

## Read executable sources

- `../../apps/web/lib/skill-model.ts`: frontend SkillModel, SkillObject, SkillAction, SkillConstraint, evidence.
- `../../apps/web/lib/process-to-skill.ts`: backend process → frontend model mapping.
- `../../apps/web/lib/simulate.ts`: deterministic replay and blocking rules.
- `../../apps/web/lib/what-if.ts`: supported local interpretation grammar.
- `../../apps/web/lib/task-checkpoint.ts`: historical/current matched-state guidance.
- `../../backend/showme/process.py`, `observe.py`, `api.py`: backend validators and HTTP authority.

Read source before copying a schema. Do not create a competing Skill Model.

## Important invariants

Object IDs and state IDs are stable references, not screen coordinates. A model can be illustrative, candidate or learned; human approval is distinct from structural JSON validity. States retain observable facts. Actions retain all participating objects, source/target states, evidence, explanation and recovery. Proposed model constraints stay unenforced; confirmed constraints need a recorded basis. Source evidence, inferred relationships, hand-authored assets and real observations must remain distinguishable.

A matched terminal state does not prove every action occurred. An unclear/latest failed check cannot turn a historical match into current certainty. Recovery requires relevant later evidence; clicking Continue is not recovery evidence.

## HTTP integration

All inference POSTs use multipart form data. Inspect `api.py` and existing frontend request code for exact response and error shapes; use existing handlers instead of guessing.

| Endpoint | Fields |
| --- | --- |
| GET `/api/health` | No media |
| POST `/api/skills/learn` | `video`, optional `narration`, optional `reference_pdf` |
| POST `/api/skills/observe` | `video`, `process_json`, optional `reference_pdf` |
| POST `/api/skills/observe-snapshot` | JPEG `image`, `process_json` |
| POST `/api/skills/ground-object` | JPEG `image`, `process_json`, `object_id`, `image_width`, `image_height` |

Reference PDF support on Observe is new; frontend wiring remains a task. Sending it must be explicit, not an automatic re-upload. HTTP 422 can represent rejected/unusable model output: show a recoverable error, not successful guidance. Keep keys server-side. Inspect actual file limits before changing controls.

## Scene extension — proposed, not current schema

A separate scene adapter may map semantic object IDs to render assets, task-local poses and visual attachment anchors. It must declare asset source and supported states. Unknown objects use a neutral placeholder; missing geometry never becomes a fabricated learned arrangement. Rendering consumes simulator results and cannot grant procedural validity. Any persisted scene schema needs versioning and contract review first.
