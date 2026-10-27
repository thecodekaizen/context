# SHOWME proof of magic

**Status:** experiment specification, not a product capability claim
**Product:** SHOWME — Demonstrations into understanding
**Hackathon:** Meta Global AI Developer Hackathon 2026

## Question

Given one short expert demonstration, can the system infer a useful process representation, then recognize a correct attempt, a meaningful physical divergence, and recovery in a separate learner recording—with evidence a person can inspect?

This tests one constrained task. It does not establish general physical intelligence, arbitrary video understanding, or live-camera reliability.

## Task selection criteria

Choose one safe, visually obvious assembly task with roughly 4–6 distinct pieces and a clear ordering or orientation constraint. It must support an expert demonstration, correct learner attempt, deliberate recoverable mistake, recovery, and a useful “what if?” alternative using the same pieces and skill model.

The physical task has not yet been selected. A small LEGO assembly is the current candidate because the user plans to obtain a set, but choose the actual procedure only after inspecting its pieces for visible states, repeatability, safety, and a visually legible alternative consequence. Avoid hidden parts and specialized equipment. The capture procedure is documented in [`LEGO_RECORDING_GUIDE.md`](LEGO_RECORDING_GUIDE.md).

## Stock footage boundary

Licensed stock footage is allowed for integration smoke tests: verify video upload, action descriptions, object segmentation, and output parsing. Those runs are exploratory and are not scored evidence for the core claim.

Stock footage does not replace the matched controlled set below. It usually cannot provide the same task and objects across an expert demonstration, correct attempt, deliberate mistake, and recovery with independent ground truth. Use only footage whose terms permit third-party AI processing and the intended public demo. Keep it out of the public repository unless redistribution is explicitly allowed; record the source and license in the local run manifest. Meta’s own cookbook confirms video upload and SAM video tracking paths, but its code license alone does not establish a license for every bundled media asset. For evaluation, prefer footage you record yourself so rights and ground truth are clear.

## Protocol

Capture hands and work surface only. Keep clips short and camera fixed for the baseline. Leave evaluation labels in a separate human-authored file that is never sent to a model.

| Clip | Recording | Purpose |
|---|---|---|
| A | Expert performs the process once | Learn candidate objects, actions, states, and evidence-backed ordering observations (not requirements) |
| B | Learner performs it correctly with objects repositioned | Check state recognition beyond coordinate replay |
| C | Learner performs one deliberate, visible mistake | Test divergence detection |
| D | Learner recovers and completes the task | Test recovery recognition |

A changed camera angle is a later robustness check, after the fixed-camera baseline. Narration is optional and must not be required for P0; current P0 video preprocessing strips audio, so spoken narration is not model evidence yet. See the recording guide for capture controls and the private answer-key checklist.

## Experimental boundary

- Model inputs: raw clip A for learning; then the resulting process representation plus an unlabeled learner clip for observation.
- Never send expected labels, condition-revealing filenames, or the human answer key.
- Preserve model requests/responses, model ID, timestamps/frame references, and API usage in ignored local run output. Commit only rights-cleared, non-sensitive fixtures that the user explicitly intends to publish.
- Human ground truth is authored independently before inspecting model output.
- A pass requires B to be accepted, C to identify the actual divergence with visual evidence, and D to recognize recovery. A fluent explanation without correct state and evidence is a failure.
- If the model cannot cite a verifiable frame/time for a claim, label that claim ungrounded. Do not use guessed timestamps as proof.

## Candidate architecture

1. Local preprocessing records clip metadata and deterministic frame references, and creates a silent, downscaled copy for P0.
2. Muse Spark receives clip A and proposes structured observations and a process candidate.
3. SAM 3.1 can segment a named object in a user-selected still image. The app can submit a snapshot or capture one frame at a Muse-reported clip timestamp; masks and boxes help inspect object location, but SAM does not judge process correctness or independently confirm Muse's divergence. This integration has only passed API/parser smoke checks, not the controlled task evaluation.
4. Muse Spark receives the learned process plus clips B, C, and D separately and proposes observed states, divergence, and recovery.
5. Local code validates schema, known object/state/action references, and evidence references. It does not convert an unsupported model claim into a fact.
6. A comparison report evaluates outputs against the separate human labels.

Use prerecorded clips for controlled evaluation; the final product's Do mode is camera-first and maintains the learner state through the active task. The final Simulate mode is an interactive, visual exploration of that same task's Skill Model; see [`SHOWME_SIMULATION_DESIGN.md`](SHOWME_SIMULATION_DESIGN.md). Evaluation validates the perception and process representation shared by all three product modes.

## Minimum process representation

The initial JSON contract is in `backend/showme/process.py`. It deliberately separates objects, observable states, transitions, timestamped evidence, ordering observations, and uncertainties. An ordering observation says only that one action happened before another in this clip. One demonstration cannot establish that the order is required. The process is a candidate model, never ground truth.

The first domain invariant is referential integrity: every transition must point to states and objects declared in the same process. Do not add a broad ontology or confidence percentages without calibration data.

### Process reference validation

`validate_references` in `backend/showme/process.py` rejects duplicate object/state/transition IDs, transitions that refer to undefined states or objects, ordering observations that refer to unknown transitions, missing evidence, and evidence intervals outside the source clip. It is deterministic and does not call a model. Targeted tests protect these invariants so unsupported model output cannot silently become a usable process graph.

## First implementation milestone

The first CLI slice now has local video inspection/frame sampling and an opt-in `learn-video` command. `learn-video` creates a silent, downscaled copy, uploads one MP4, asks Muse Spark for the candidate process representation, records token counts, requests one-hour remote-file expiry, attempts deletion after inference, and writes a local run artifact. Muse Spark 1.3 audio understanding is documented as not fully supported, so the P0 visual experiment strips audio; voice evidence remains a later, separate experiment. No model call is made by video preparation alone.

The CLI now also has an opt-in `observe-video` path. It supplies the learned process and a single learner clip to Muse Spark, constrains output state/object IDs to the learned process, checks timestamps against clip duration, and rejects unsupported recovery claims. This code path is not yet tested on real video.

Next experiment milestone (app integration already exists):

- Run learn on a short expert clip and manually inspect the process and evidence.
- Run observe on a correct learner clip and then a deliberate mistake, with neutral filenames and no labels in the prompts.
- Use the existing opt-in SAM still-frame grounding on the selected task after reviewing Muse's baseline state output. Evaluate mask usefulness separately; it provides neither persistent object tracking nor process reasoning.
- Repeat runs and inspect request, response, usage, latency, and failure artifacts.

This experiment milestone makes no real-time camera, generic skill-library, robot-control, or physical-simulation claims. The existing web app is an integration surface for the same experiment, not evidence that the perception capability has passed.

## Kill criteria

Stop or narrow the task if any of these persist after bounded debugging:

- Correct and incorrect states look the same to the model at the chosen camera setup.
- The system succeeds only when the expected mistake is stated in the prompt.
- A small object-position change causes false divergence, or SAM tracks the wrong instance.
- Required state facts are occluded and cannot be made observable without falsifying the demo.
- The result lacks verifiable source frames or cannot identify uncertainty.
- Recovery cannot be recognized from the recording.

Record failures; do not hide them behind UI or hand-authored expected states.
