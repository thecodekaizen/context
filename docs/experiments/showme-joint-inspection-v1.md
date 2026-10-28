# Inspect a selected joint against source evidence

Implemented October 28. Local software verification only; real visual accuracy remains unvalidated.

## Purpose

Whole-video summaries have reported contradictory coarse assembly judgments. This alternative examines one selected process transition with a source diagram/frame and a learner frame, explicitly separating the visible landmarks in each. It does not replace temporal observation or certify the full assembly.

## Integration contract for Antigravity

Explicit multipart POST `/api/skills/inspect-joint`:

- `reference_image`: selected JPEG or PNG source diagram/frame.
- `learner_image`: selected JPEG or PNG learner frame.
- `process_json`: existing reviewed backend process JSON, not the frontend SkillModel projection.
- `transition_id`: one declared process transition.

Each image uses the existing 5 MiB snapshot limit. The request sends both selected images and selected transition context to Meta and uses credits. Trigger only through an explicit user action with that disclosure. The backend does not fetch a diagram or take a camera frame automatically.

Success returns `{status, inspection}`. `status` is `matches`, `possible_difference`, or `unclear`. Each relation contains declared affected `object_ids`, separate `reference_landmark` and `learner_landmark`, `assessment` (`matches`, `differs`, `unclear`) and an explanation. Overall matches requires nonempty all-matching relations; possible_difference requires a conflicting relation. Unclear requires view guidance. Invalid input/output returns an error, not usable guidance.

`inspection._run` includes selected transition, prompt/model metadata, source/learner image hashes, semantic process hash and an explicit selected-joint scope. No image bytes are persisted by the endpoint. Provider retention still applies; do not describe this as local-only analysis.

## UI boundary

Label it “Inspect this joint”, present both source and learner evidence, and let users inspect the landmark comparison. A match concerns reported visible relationships only. Do not mark all steps complete, infer recovery, or overwrite a temporal observation from this result. View guidance helps acquire evidence; it is not a proven repair instruction. Diagram crops and source selection remain disclosed human inputs, not claimed automatic segmentation.

## Verification

83 SHOWME backend checks pass, including paired-image MIME/ordering, HTTP forwarding, unknown-transition rejection before inference, declared-object enforcement, conflict/match consistency, uncertainty guidance and image provenance. Controlled responses establish software behavior only. No Meta request was made for this feature.

The prompt uses the existing Responses image-content adapter pattern. Multi-image live provider behavior, visual accuracy, latency and cost remain to be measured before demo claims.

## Runnable experiment and first live results

Use `python -m showme inspect-joint PROCESS SOURCE_IMAGE LEARNER_IMAGE --transition ID --output NEW_DIRECTORY`. This is an explicit paid action. Exact prompt, selected input hashes, process and raw output are retained privately even if semantic guards reject the response. Existing run directories are not overwritten; no automatic retry occurs.

Three approved comparisons have now run, all unclear due to hidden joint contact. See `results/showme-joint-images-2026-10-28.md`. Provider multi-image request behavior worked for these calls. No orientation detection claim follows. Combined backend checks: 95 passed before the metadata-only process fingerprint addition.

## v2 additive response fields — October 28

Each relation now also supplies `relationship` (`contact`, `facing`, `overall_arrangement`), `reference_visibility` and `learner_visibility` (`visible`, `occluded`, `ambiguous`). Matches/differences require visible evidence in both inputs; overall joint verdicts require a specific contact/facing comparison. Existing top-level status fields are unchanged. Version is `showme-joint-inspection-v2`. Previously saved v1 reports remain historical artifacts and do not satisfy the new validator automatically. See `results/showme-hands-off-stills-2026-10-28.md` for the live v1 failure that motivated this change.

## v3 relationship target

Optional multipart `relationship_target` on `/api/skills/inspect-joint` is `all` (default), `contact`, or `facing`. CLI equivalent: `--relationship facing`. A selected facing question must not demand hidden contact proof or return contact rows. Guidance validates that the report stays within its recorded target. The target describes what to inspect, never which outcome to return. This is a narrower assessment scope, not a proven perception improvement. See the v2 run report for the observed all-unclear outcome that motivated separating these questions.
