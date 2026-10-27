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
