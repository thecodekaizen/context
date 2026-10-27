# SHOWME hackathon daily log

This log records SHOWME work only. Earlier entries described the retired THREAD direction and are preserved in Git history; do not use them as current progress evidence.

## Tue Oct 27 — Day 1

### Product decision locked

- SHOWME has exactly three app surfaces: **Teach → Do → Simulate**, all centered on one shared Skill Model. Teach creates it; Do maintains learner state and supports intervention/recovery; Simulate explores alternatives against that same model.
- The hackathon focuses on one safe 4–6-piece assembly with an obvious ordering or orientation constraint. Arbitrary task learning and general-purpose physics are outside the claim.
- See [`PRODUCT.md`](PRODUCT.md) for the locked definition. Product/architecture exploration is closed; remaining choices are task selection and implementation details supported by evidence.

### Current phase

**Phase 1 — learn one demonstration: in progress.** The CLI can prepare a clip, call Muse Spark, validate a candidate process, observe a learner clip, and validate timestamped observations. This is infrastructure, not proof that the capability works reliably.

### Evidence and outcome

- The CaptainCook4D stock-footage evaluation is **P0 FAIL**. Muse omitted the decisive action during learning and missed the annotated ordering error during observation. It also produced no divergence on a normal control, but the prompt and expert crop changed between runs, so that apparent improvement is confounded.
- The result is documented in [`captaincook4d-ordering-observation-v2-2026-10-27.md`](experiments/results/captaincook4d-ordering-observation-v2-2026-10-27.md). Earlier exploratory results are in the neighboring `experiments/results/` files.
- The stock footage remains useful for pipeline checks and failure analysis. It does not establish the SHOWME thesis.
- Process and observation validation has automated tests; the latest run recorded in the experiment notes passed the CLI/test checks, but these do not replace a successful behavioral evaluation.

### Decisions

- This was a provisional experiment gate and is superseded as a product-plan decision by the locked SHOWME product. The app is now being built in parallel, while the failed P0 result still blocks any claim that task understanding is validated.
- Next, choose a short, safe, visually discrete task with a small number of objects and a clearly visible, recoverable mistake. Record our own controlled clips if available footage cannot provide matched learn/control/error/recovery attempts.
- Reuse the exact same expert process for separate correct, error, and recovery attempts. Keep expected labels out of model prompts and preserve the human answer key separately.

### Next step

Run the controlled task with matched clips, inspect the learned process and evidence, and score correct-state acceptance, error detection, and recovery recognition separately. Update [`SHOWME_BUILD_PLAN.md`](SHOWME_BUILD_PLAN.md) and this log with the result before advancing phases.

## Progress ledger

| Workstream | Status | Evidence / next gate |
|---|---|---|
| Experiment CLI and local validation | Implemented; continue hardening | `backend/showme/`, `backend/tests/` |
| Learn a procedure from a demonstration | In progress; not validated | Pass repeated evidence-linked extraction on the selected controlled task |
| Recognize correct learner state | Not passed | Matched learner clip; measure false alarms |
| Detect a deliberate divergence | Not passed | Matched error clip; detect the withheld target with frame evidence |
| Recognize recovery | Not passed | Separate recovery clip; verify restored valid state |
| Do-session continuity | Partial prototype | Last 12 explicit still-frame checks appear in a local timeline; no inference between frames |
| SAM visual grounding | Integrated for explicit stills; task validation pending | Repeat masks on the selected task and actual divergence frame; SAM does not confirm procedural errors |
| Procedural what-if simulation | Implemented for fixture and reviewed Skill Models; task-specific visual consequence pending | Deterministic action reordering/playback and a model-driven transition map; physical-task evidence and geometry still needed |
| SHOWME app | Teach, Do, Simulate prototype implemented; physical-task capability not validated | Browser recording/upload, candidate review, snapshot/clip observation, procedural simulation; see [`SHOWME_APP_PLAN.md`](SHOWME_APP_PLAN.md) |
| Demo video and submission | Not started | Only show capabilities that pass evaluation |

### Implementation checkpoint — Teach camera recording

- Added browser-camera recording to Teach alongside file upload. The browser creates a local WebM or MP4 clip and routes it through the existing video preview and learning request flow.
- Recording does not upload automatically; selecting **Learn this skill** is the explicit model-call boundary. Camera tracks stop after recording or when the app unmounts.
- This is capture plumbing, not evidence that SHOWME can infer a reliable skill. The matched LEGO demonstration/correct/error/recovery evaluation remains the next scientific gate.
- Verification: all 7 web tests, TypeScript check, and production build passed. A temporary fake-camera browser run started and stopped MediaRecorder, produced a local preview, enabled **Learn this skill**, and stopped the camera without making a model request. The Teach screenshot in [`design/screenshots/`](../design/screenshots/README.md) shows the new capture control.

### Implementation checkpoint — Do learner recording

- Do can start recording a learner attempt directly or preview the live camera separately; the resulting clip joins the existing upload/preview path and only reaches Muse Spark after the user selects **Observe attempt**.
- Teach and Do now provide download links for the current clip, so controlled recordings can be saved locally for evaluation and sharing without checking raw footage into Git.
- Switching away from Teach or Do stops that surface's camera stream; stopping a learner recording creates a local clip and releases the camera.
- Verification: the recording lifecycle passed an isolated browser smoke with a fake camera. The clip preview appeared and **Observe attempt** became available without triggering a model call. Web tests, type check, and production build passed.

### Implementation checkpoint — LEGO capture protocol

- Added [`LEGO_RECORDING_GUIDE.md`](LEGO_RECORDING_GUIDE.md) for the planned physical set. It defines the four matched clips (demonstration, correct control, one deliberate divergence, recovery), camera setup, local answer-key separation, and explicit model-call boundaries.
- The LEGO task itself remains unselected until the pieces are inspected. The guide avoids assuming a washer/bracket constraint that may not exist in the set.
- P0 captures video only and strips audio during preprocessing; narration is optional but is not treated as model evidence in this experiment.
- This is experiment preparation, not a result. Capability remains unvalidated until the clips are recorded and evaluated.

### Implementation checkpoint — Do session checkpoints

- Do retains up to 12 successful explicit still-frame checks in a session-local timeline, including time, assessment, identified state/objects, and model evidence.
- Each check remains an explicit paid Muse Spark request. The timeline clears when a different reviewed skill is loaded or forgotten; it is not continuous tracking and does not infer recovery from a sequence of snapshots.
- This is usable before the LEGO set arrives and will let us inspect state changes during the later physical-task test without overstating what the model observed.

### Implementation checkpoint — Simulate state map

- Added a transition map beneath the simulated state view. It reads state labels, action order, and evidence from the same Skill Model used by Teach and Do, and highlights transitions as completed, current, or upcoming while stepping through a what-if sequence.
- The illustrative fixture is labeled separately from a reviewed demonstration. The map is a procedural state preview, not task-specific geometry or physics.
- This work is independent of receiving the LEGO clips; those remain necessary to replace the fixture with the chosen assembly and validate physical-state recognition.
- Verification: the 7 existing web tests passed, TypeScript check passed, and production build completed successfully.

### Implementation checkpoint — Reviewed natural-language what-if

- Added a bounded, local parser for explicit before/after/first ordering requests using action labels and object names from the active Skill Model. It is intentionally not presented as general natural-language understanding and makes no model/API call.
- The parser proposes an order only; SHOWME displays that interpretation for review, applies it only after user confirmation, and still requires an explicit run action before deterministic simulation.
- Added coverage for a named relative move, moving an action first, unmatched input, and self-relative ordering.
- This makes the procedural what-if interaction testable before the LEGO task is selected; state consequences and physical geometry remain limited by the available Skill Model.

### Implementation checkpoint — Reference vs alternative state

- After running a proposed order, Simulate now places the reference trace's final modeled state beside the alternative's final modeled state. Both are derived from the active shared Skill Model.
- The reference is labeled as an observed trace for reviewed skills and as illustrative for the sample fixture; the UI explicitly avoids treating one observed ordering as proof that alternatives are impossible.
- This adds a clear outcome comparison while keeping the scene a procedural state view; LEGO-specific geometry and physical consequences remain pending the selected task and recordings.

### Implementation checkpoint — Multi-object actions

- Updated the shared Skill Model to keep every object ID associated with a learned transition. The previous single-object field discarded secondary parts in actions such as positioning a spacer beneath a bracket.
- The bounded what-if interpreter now resolves an action by any of its associated object names, while keeping action labels as the strongest match.
- Added a regression check for referring to a learned action through a secondary involved part. This prepares the process representation for the actual LEGO procedure without inventing its states or constraints.

- The transition map now displays the names of all parts involved in each action, making multi-object relationships inspectable in the app.

### Implementation checkpoint — Continue simulation from a camera checkpoint

- A clearly consistent, mapped still-frame result in Do now offers an explicit entry into Simulate from that recognized state. The simulator receives only the remaining actions from the reviewed trace; it does not replay earlier steps or guess a state from unclear/divergent frames.
- Simulate now compares the remaining reference trace against the proposed sequence from the same checkpoint. A single still remains only a model-reported state match, not continuous tracking or proof of prior action order.
- Added a pure simulation check for starting a sequence from an explicit state.

### Implementation checkpoint — SAM still-frame grounding

- Added an explicit **Locate in frame** action after Muse identifies a declared Skill Model object in a manual camera snapshot. It resends that same still to SAM 3.1 and overlays the official parser's mask paths and bounding boxes on the captured image.
- The backend rejects undeclared object IDs, bounds the image dimensions, makes no automatic retry, and returns no raw SAM token payload. SAM is still phrase-based segmentation; it does not verify task correctness or provide live tracking.
- Live smoke: one synthetic repository mockup still returned 9 `button` detections with masks and no parser diagnostics. The screenshot was resized to the app's 1280-pixel maximum and remained in `/tmp`; this validates API + parser + geometry only, not LEGO performance.
- Verification: 7 focused SAM/API tests, the full backend suite, all web tests, TypeScript, and production build passed.

### Implementation checkpoint — Ground a learner divergence frame

- Each recorded-clip divergence with known object IDs now offers a separate SAM grounding action. It pauses the learner preview, seeks to the model-reported timestamp, captures that single frame in-browser, and displays the resulting mask and box below the clip evidence.
- This reuses the existing image endpoint; no video is sent to SAM, and the action does not independently validate the Muse-reported difference. The frame remains transient in browser memory.
- The browser screenshot inspection tool timed out during this checkpoint, so visual confirmation is limited to the successful production build.
- Verification: all 71 backend tests, 13 web tests, TypeScript, and production build passed.

### Status correction — SAM grounding scope

- Updated the build plan and proof-of-magic protocol to reflect the current code: SAM accepts a user-selected still or a single frame at a Muse-reported divergence timestamp. It returns phrase-grounded masks/boxes for inspection.
- The integration smoke does not establish task-level object grounding, persistent tracking, or correctness of the reported divergence. These still require repeated LEGO footage.
- The immediate dependency is now concrete: inspect the set, record matched A/B/C/D clips, run blind evaluation, then decide whether the overlay helps the demo.

### Implementation checkpoint — Skill-specific simulator copy

- Updated Simulate's process-model description to distinguish the sample fixture from a reviewed demonstration model. The reviewed state now explains its evidence and hypothesis caveats instead of saying Teach will replace the fixture later.
- Corrected the locked product document's implementation status to match the existing SAM still-image integration while retaining the explicit limitation that task grounding is not validated.
- Verification: web unit tests, TypeScript check, and production build passed.

### Design checkpoint — Teach concept mockup

- Added `design/mockups/03-teach-skill-model-review.png`, completing the concept set across Teach, Do, and Simulate. It shows the demonstration, candidate Skill Model, timestamped evidence, and human review of a proposed constraint.
- Updated the mockup inventory and README to label this as generated concept art, distinct from actual app screenshots. The depicted block assembly remains illustrative and does not imply task validation.
- Clarified that the October 27 app screenshots predate the SAM still-grounding control, avoiding the impression that they show the latest UI.

### Demo-prep checkpoint — Evidence-gated three-minute cut

- Reworked the demo plan to separate the final target cut from a truthful current-prototype fallback. The script no longer narrates live tracking or recovery as though they are implemented and validated.
- Added time-coded shots, narration, independent recording/evaluation checks, and gates for Teach evidence, Do divergence, SAM grounding, recovery, and same-model simulation.
- Corrected the app-plan mockup count: the concept set now includes Teach, Do, and Simulate; the new Teach asset is concept art, not a built screen.

### Implementation checkpoint — Blocked simulation preview

- A confirmed prerequisite still stops the deterministic simulation at its last valid state. For the explicitly illustrative stacked-mount fixture, Simulate now also shows the attempted bracket position as an amber dashed preview, with copy that says it was not applied and the modeled state is unchanged.
- The overlay is restricted to the illustrative fixture; learned Skill Models continue to use their evidence-linked state map instead of fabricated geometry.
- The existing screenshots predate this visual update and are labeled accordingly. This remains procedural visualization, not physical simulation.

### Demo-prep checkpoint — Current production screenshots

- Re-captured Teach, Do, Simulate, and the blocked what-if from the production build at desktop width, replacing the older README captures. The blocked screen shows the dashed attempted bracket plus the unchanged valid state.
- Visually checked the output and documented that Do is shown with camera off and no SAM result; SAM requires an explicit selected-frame model call. Screenshots remain illustrations of app flows, not evidence of task accuracy.

### Implementation checkpoint — Timed procedural playback

- Added Play/Pause/Replay to the deterministic Simulate sequence. It advances the existing Skill Model transitions at a readable interval, preserves manual stepping, and stops at the last result, including a blocked attempt.
- Resetting, reordering, rerunning, changing the starting checkpoint, or manually stepping stops playback so state cannot drift from the visible sequence. The controls wrap on narrow screens.
- This is timed state progression, not physical animation or a claim of physics simulation. LEGO geometry and real-task verification remain dependent on the user's recordings.

### UX checkpoint — Clearer workflow and capability labels

- Rewrote the Teach, Do, and Simulate headings, descriptions, buttons, and helper text to name the action and outcome. The three stages now appear as a workflow with short descriptions.
- Clarified that Teach proposes a model for review, Do checks a selected frame or separate recording rather than continuously tracking, and Simulate shows modeled states rather than physics.
- Improved type scale, contrast, navigation states, buttons, spacing, and narrow-screen layout. Updated page metadata and README copy to match the actual prototype.
- Existing screenshots predate the updated interface; no screenshot is presented as evidence of capability. The app tests, TypeScript check, and production build passed.

### UX checkpoint — Plain-language status and evidence

- Replaced internal status terms in the process preview with learner-facing labels such as “Next step” and “Applied in model.”
- Clarified the difference between a step observed in one demonstration and a requirement confirmed by a person. Simulation warnings now identify the source in plain language.
- Removed token counts from the learner video review and clarified that the sample procedure was not learned from a video.
- Verification: all 13 existing tests pass, TypeScript passes, and the production build completes. No new capability is claimed by this copy change.

### Documentation checkpoint — SHOWME demo and hackathon alignment

- Replaced the stale THREAD demo narrative with SHOWME's Teach → Do → Simulate story, evidence gates, and honest fallback.
- Updated the participant checklist for the locked SHOWME task, current hackathon requirements, and verified credit claim.
- Marked the old THREAD evaluation strategy as archived and corrected demo-script wording to match the interface and current evidence boundaries.
- The README screenshots still predate the latest copy pass. Browser capture was unavailable in this session; keep the existing date/caveat until fresh screenshots can be captured and reviewed.
# 2026-10-27 — Manual-step checks for learner video

- Added a reference-step ledger to learner-video review. Each transition cited by the instruction PDF must be labeled visible match, possible mismatch, not shown, or unclear, with timestamped evidence where visible and a concrete next action when the clip cannot verify it.
- The API validator now rejects omitted/duplicate/unknown cited steps, unsupported mismatch timestamps, and claims that a not-shown step has a visible timestamp. The Do screen and CLI expose the results.
- Replayed the same 111-second IMG_7663 learner clip against the saved IMG_7660 process and LEGO manual; no second Teach run was needed. Muse Spark 1.3 returned 18 step checks: 15 not shown, 3 visible matches, one possible divergence at 42s, and recovered after later consistent evidence at 60s and 88s. It used 33,305 input and 2,289 output tokens and took 49.2s.
- Reviewed the cited frames against manual page 2. The frames support a possible temporary white-tile misplacement followed by correction. This is one promising observation, not a passed evaluation: the error labels were not preregistered and early steps remain outside the clip.
- SAM 3.1 returned zero detections for the cockpit core and wing assembly at 42s. Visual grounding failed on this close, hand-occluded frame.
- Verification: 80 backend tests, 15 frontend tests, and TypeScript checks pass. The controlled P0 evaluation remains incomplete.


### Implementation checkpoint — recovery evidence and LEGO state exploration

- Separate learner clips produced inconsistent/no-divergence reports and one detached-wing/restored-wing report at 14/22 seconds. This is a coarse state-change signal, not a verified orientation-mistake benchmark. See [the evidence summary](experiments/results/showme-lego-wing-state-2026-10-27.md).
- Fixed backend recovery validation and UI evidence selection: unrelated parts and matches before a later divergence cannot justify recovery. Unknown affected parts remain unverified.
- Updated the generic observation prompt to inspect supported relationships and distinguish physical state changes from learner intent. Baseline videos have not been rerun against the new prompt.
- Added a local learner-review JSON export, including the matching process, to preserve results without repeated model calls. No private footage or expected-error labels are committed.
- Found an extraction gap: both wings share one object ID and the final state lacks explicit facing facts. Teach now requests source-supported attachment/orientation relations; no fresh inference has validated that change.
- Verification: 57 SHOWME backend tests, 21 web tests, and TypeScript checks passed. Browser local export/import tests rejected unrelated recovery evidence and restored the actual 22-second report without a paid inference. Do no longer inherits simulated completion ticks.
