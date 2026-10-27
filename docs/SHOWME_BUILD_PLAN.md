# SHOWME hackathon build plan

**Window:** October 27–November 4, 2026
**Submission:** November 4, 9:00 PM ET
**Rule:** each phase earns the next. If a phase fails, narrow the task before adding UI.

**Status (Oct 27):** Phase 0 repo footing is in place and pushed. Phase 1 preprocessing, Muse adapter, and process validation are implemented and covered by tests, but not yet run on a real demonstration. Phase 2 now has a CLI observer and deterministic output checks. A stock-video API smoke passed, but same-clip reuse does not test learner transfer or error recovery. No P0 capability claim has passed yet.

## Phase 0 — Repo and experiment footing (Oct 27)

**Goal:** make the experiment reproducible, private by default, and easy to inspect.

- Preserve useful THREAD infrastructure but isolate the active SHOWME package.
- Pre-register the proof question, candidate task, clip protocol, and failure criteria.
- Add local-only video inspection/frame sampling and run artifact paths.

**Exit:** CLI help works; the repo has an explicit experiment protocol; no private clip or key is tracked.

## Phase 1 — Learn one demonstration (Oct 27–28)

**Goal:** Muse Spark proposes an evidence-linked process from one short MP4.

- Keep the process small: objects, observable states, transitions, constraints, uncertainty, timestamps.
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

## Phase 4 — Procedural what-if visual (Nov 1–2)

**Goal:** answer one bounded “what if I do this step early?” question from the learned process model.

- Deterministic process logic predicts the violated prerequisite and resulting process state.
- If the task benefits from 3D, render before/after states with Three.js / React Three Fiber.
- Do not add a physics engine unless the selected task requires collisions or forces.

**Exit:** a judge can change one action and see the predicted state and violated constraint; the displayed outcome agrees with deterministic state logic.

## Phase 5 — Demo hardening and submission (Nov 2–4)

**Goal:** present only capabilities that survive repeatable checks.

- Capture the controlled evaluation clips and save a separate private answer key.
- Run the exact 3-minute demo flow twice from a clean start; keep raw model outputs and failures.
- Make the public repo and setup instructions reproducible; remove secrets and private media.
- Submit before 9:00 PM ET on Nov 4, with all contributors and a public demo video.

**Exit:** the P0 loop works in the final demo; no unverified simulation claim; repo and video are accessible.

## Kill / scope rules

- If learning fails, simplify the physical task and improve observability; do not add UI.
- If observation cannot distinguish correct from wrong, narrow object count, camera variation, or task states.
- If SAM is unstable, retain timestamped frame evidence and omit the overlay.
- If P0 is not reliable by Nov 1, drop simulation and spend the remaining time on evidence, recovery, and demo repeatability.
