# SHOWME hackathon build plan

**Window:** October 27–November 4, 2026
**Submission:** November 4, 9:00 PM ET
**Rule:** the submission target includes learning, live or prerecorded learner guidance, mistake detection and recovery, plus an interactive simulation driven by the learned task model. Sequence the work to validate dependencies; if a capability fails, narrow the task and record the limit rather than presenting a fake success.

**Status (Oct 27):** Phase 0 experiment footing is complete. Phase 1 CLI preprocessing, Muse adapter, and process validation are implemented. The stock CaptainCook4D evaluation failed P0: Muse omitted the decisive action and the observer missed the annotated ordering error. A normal control produced no false alarms in a changed setup, so this is confounded and not a pass. No P0 capability claim has passed. The next milestone is a short, safe, visually discrete task with matched learn/correct/error/recovery recordings. Two exploratory SHOWME concept mockups now exist; product UI remains gated on P0. See the [v2 result](experiments/results/captaincook4d-ordering-observation-v2-2026-10-27.md) and [app plan](SHOWME_APP_PLAN.md).

## Phase 0 — Repo and experiment footing (Oct 27)

**Goal:** make the experiment reproducible, private by default, and easy to inspect.

- Preserve useful THREAD infrastructure but isolate the active SHOWME package.
- Pre-register the proof question, candidate task, clip protocol, and failure criteria.
- Add local-only video inspection/frame sampling and run artifact paths.

**Exit:** CLI help works; the repo has an explicit experiment protocol; no private clip or key is tracked.

## Phase 1 — Learn one demonstration (Oct 27–28)

**Goal:** Muse Spark proposes an evidence-linked process from one short MP4.

- Keep the process small: objects, observable states, transitions, evidence-backed ordering observations, uncertainty, timestamps. One demonstration is an observed trace; it cannot establish that an ordering is required.
- Validate JSON shape and cross-references locally; preserve model identity and token counts.
- Use one rights-cleared clip only after local preprocessing and code checks pass.

**Exit:** a repeated run creates a reviewable process artifact whose transitions cite visible times; malformed references fail closed. A fluent but unsupported answer is a fail.

## Phase 2 — Observe a second attempt (Oct 28–30)

**Goal:** use the learned process plus a separate, unlabeled learner clip to classify current state and process divergence.

- Do not include evaluation labels or tell the prompt which clip is wrong.
- Require time/frame evidence for every state claim.
- Compare a correct attempt against one deliberate mistake; record false alarms and misses.

**Exit:** correct progress is accepted, the real divergence is named with visual evidence, and changing object positions does not break the baseline.

## Phase 3 — Ground and recover (Oct 30–Nov 1)

**Goal:** make the detected issue inspectable and recognize correction.

- Integrate SAM 3.1 for object masks/tracks where it adds evidence; it does not decide procedural correctness.
- Observe the recovery clip after the divergence and detect return to a valid state.
- Measure API cost and latency before repeating calls.

**Exit:** an overlay points to the relevant object, and the system recognizes recovery without seeing the human answer key.

## Phase 4 — Interactive task simulation (Nov 1–2)

**Goal:** deliver the second hero moment: change an action order and watch the selected task's physical state change in an interactive simulation driven by the learned process model.

- Convert the learned process into a task-scoped scene model: named parts, initial poses, action-to-state transitions, and prerequisites.
- Let the judge/learner change one action order, step or scrub the resulting sequence, inspect the violated prerequisite, and return to the demonstrated procedure.
- Render actual scene states and object transforms in a Three.js-based 3D view; use deterministic transition/constraint logic so the same question yields the same visible result.
- Use the selected task's real geometry and constraints. Add physical contact/force simulation only if it is needed to demonstrate that task's outcome; do not imply general-purpose physics.

**Exit:** from the learned task representation, a judge can change an action, watch the alternate sequence in 3D, see the resulting incomplete/invalid physical arrangement and its violated prerequisite, and compare it with the demonstrated successful sequence. The rendered state matches deterministic simulation output.

## Phase 5 — Demo hardening and submission (Nov 2–4)

**Goal:** present only capabilities that survive repeatable checks.

- Capture the controlled evaluation clips and save a separate private answer key.
- Run the exact 3-minute demo flow twice from a clean start; keep raw model outputs and failures.
- Make the public repo and setup instructions reproducible; remove secrets and private media.
- Submit before 9:00 PM ET on Nov 4, with all contributors and a public demo video.

**Exit:** both hero moments work in the final demo: SHOWME catches and supports recovery from a learner mistake, and the interactive task simulation shows the consequence of a changed action order. All capability claims match repeatable evidence; repo and video are accessible.

## Kill / scope rules

- If learning or observation fails, simplify the task geometry and state/action vocabulary, then re-run the matched evaluation before connecting it to the app.
- Keep the final UI task-scoped; do not substitute polished overlays for unreliable state recognition.
- If SAM is unstable, retain timestamped frame evidence and omit the overlay.
- If repeated evidence cannot support a perception claim, narrow the task until the final demo's perception and simulation are both truthful and reproducible. The simulator remains part of the submission target, but must not be presented as learning a constraint that was manually inserted without disclosure.

See [`SHOWME_SIMULATION_DESIGN.md`](SHOWME_SIMULATION_DESIGN.md) for the scene/process contract and simulator interactions.
