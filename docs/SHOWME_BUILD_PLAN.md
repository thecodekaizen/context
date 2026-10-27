# SHOWME hackathon build plan

**Window:** October 27–November 4, 2026
**Submission:** November 4, 9:00 PM ET
**Product contract:** [`PRODUCT.md`](PRODUCT.md) is locked. Build exactly three surfaces—Teach, Do, Simulate—over one Skill Model. Keep experimental gates and honest evidence, but do not resume product/architecture exploration.

**Status (Oct 27):** Phase 0 footing is complete. The CLI can prepare clips, learn a candidate process, and observe a separate video; process references and evidence are validated. Teach, Do, and Simulate share a Skill Model. Simulate has a state-transition map, deterministic what-if evaluation, timed Play/Pause/Replay, manual stepping, and model evidence where available; the scene remains procedural rather than task geometry. Do retains the last 12 explicit still-frame checks in a session-local timeline; each is a separate paid inference, not continuous tracking, and the list does not infer recovery. A previous CaptainCook4D evaluation missed the annotated ordering error; a normal control had no false alarms but used a changed setup, so it is confounded. A Pexels LEGO clip produced 3 states and 2 timestamped transitions in one Teach smoke test. A separate single-frame Muse Spark request returned a visually consistent state with explicit uncertainty, but reused the learning clip and is only an integration smoke. SAM 3.1 can now segment a user-selected still frame and show masks/boxes for a known object, including a timestamped frame selected from a model-reported clip divergence. This is opt-in visual grounding—not object tracking, proof of a divergence, or validated LEGO performance. A labeled HoloAssist GoPro learner clip is available locally, but a paired clean demonstration was not found in the bounded archive scan. Recovery guidance has not been validated. The user plans to obtain a LEGO set; the actual task remains pending inspection. A capture guide specifies the matched A/B/C/D set, camera setup, local privacy, and blind evaluation boundary. App implementation can continue before the controlled clips arrive; those clips are needed to validate the physical-task capability, not to unblock unrelated UI and integration work. See the [recording guide](LEGO_RECORDING_GUIDE.md), [v2 result](experiments/results/captaincook4d-ordering-observation-v2-2026-10-27.md), [stock clip trial](experiments/proof-of-magic/stock-clip-trial.md), [snapshot smoke](experiments/results/showme-snapshot-smoke-2026-10-27.md), [HoloAssist screening](experiments/results/holoassist-stock-footage-screening-2026-10-27.md), [product definition](PRODUCT.md), and [app plan](SHOWME_APP_PLAN.md).

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
- Use rights-cleared clips for smoke tests only; use a matched, ground-truthed set for capability claims.

**Exit:** a repeated run creates a reviewable process artifact whose transitions cite visible times; malformed references fail closed. A fluent but unsupported answer is a fail.

## Phase 2 — Observe a second attempt (Oct 28–30)

**Goal:** use the learned process plus a separate, unlabeled learner clip to classify current state and process divergence.

- Do not include evaluation labels or tell the prompt which clip is wrong.
- Require time/frame evidence for every state claim.
- Compare a correct attempt against one deliberate mistake; record false alarms and misses.
- Score divergence timestamps against local annotation intervals with `showme score-holoassist`; report exact overlap and any explicitly chosen tolerance separately.

**Exit:** correct progress is accepted, the real divergence is named with visual evidence, and changing object positions does not break the baseline.

## Phase 3 — Ground and recover (Oct 30–Nov 1)

**Goal:** make a model-reported issue visually inspectable and recognize correction.

- SAM 3.1 still-image grounding is integrated for a user-selected known object, including an opt-in frame at a model-reported divergence timestamp. It provides a mask/box for inspection; it does not decide procedural correctness or independently confirm the divergence. Validate this on the selected task before relying on it in the demo.
- Observe the recovery clip after the divergence and detect return to a valid state.
- Measure API cost and latency before repeating calls.

**Exit:** a relevant-object overlay is repeatable on the selected task, and the system recognizes recovery without seeing the human answer key. Current SAM parser/API smoke tests do not meet this task-level exit.

## Phase 4 — Interactive task simulation (Nov 1–2)

**Goal:** deliver Simulate as a mode of the active learned skill: change an action or orientation and visually explore the resulting task state from the same Skill Model.

- Convert the learned process into a task-scoped scene model: named parts, initial poses, action-to-state transitions, and prerequisites.
- Let the judge/learner describe a bounded before/after/first ordering question, review the interpreted action order, then run and step through the resulting sequence; direct reordering remains available. Inspect the violated prerequisite and return to the demonstrated procedure.
- Render actual scene states and object relations in an interactive task view; use deterministic transition/constraint logic so the same question yields the same visible result.
- Use the selected task's real geometry and constraints. Add physical contact/force simulation only if it is needed to demonstrate that task's outcome; do not imply general-purpose physics.

**Exit:** from the active Skill Model, a judge can change an action, watch the alternate sequence, see the resulting incomplete/invalid physical arrangement and its violated prerequisite, compare it with the demonstrated successful sequence, and return to Do. The rendered state matches deterministic simulation output.

## Phase 5 — Demo hardening and submission (Nov 2–4)

**Goal:** present only capabilities that survive repeatable checks.

- Capture the controlled evaluation clips and save a separate private answer key.
- Run the exact 3-minute demo flow twice from a clean start; keep raw model outputs and failures.
- Make the public repo and setup instructions reproducible; remove secrets and private media.
- Submit before 9:00 PM ET on Nov 4, with all contributors and a public demo video.

**Exit:** the complete Teach → Do → Simulate story works in the final demo using one shared Skill Model. SHOWME catches and supports recovery from a learner mistake; the learner enters Simulate, explores an alternative, sees its consequence, and returns to Do. All capability claims match repeatable evidence; repo and video are accessible.

## Kill / scope rules

- If learning or observation fails, simplify the task geometry and state/action vocabulary, then re-run the matched evaluation before connecting it to the app.
- Keep the final UI task-scoped; do not substitute polished overlays for unreliable state recognition.
- If SAM is unstable, retain timestamped frame evidence and omit the overlay.
- If repeated evidence cannot support a perception claim, narrow the task until the final demo's perception and simulation are both truthful and reproducible. The simulator remains part of the submission target, but must not be presented as learning a constraint that was manually inserted without disclosure.

See [`SHOWME_SIMULATION_DESIGN.md`](SHOWME_SIMULATION_DESIGN.md) for the scene/process contract and simulator interactions.

## Immediate next actions

1. When the LEGO set is available, inspect the pieces and choose one short procedure with an observable ordering/orientation constraint and a reversible mistake. Do not assume the washer/bracket example fits the set.
2. Record the matched A/B/C/D clips in [`LEGO_RECORDING_GUIDE.md`](LEGO_RECORDING_GUIDE.md). Keep the human answer key local and separate from model inputs.
3. Run Learn on A, then Observe B/C/D independently. Review each cited frame, score false alarms/misses, and retain raw outputs before using the run to update app behavior.
4. Try the SAM grounding control on a disclosed known object and the actual divergence frame. Count it as useful only if the mask identifies the relevant physical component/location in repeated task footage.
5. Implement recovery guidance and task-specific simulation only against the reviewed Skill Model; label any manually authored constraint as such.

Until the matched clip evaluation passes, the app is an integration prototype. Continuous camera tracking is out of scope for the current validated capability; Do currently uses explicit, user-triggered snapshots and recorded clips.
