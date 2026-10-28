# Seven-day delivery and progress

Planning date: 28 October 2026, Asia/Kolkata. Seven development days: 28 October–3 November. Reserve 4 November for submission issues. Official deadline: 4 November, 9 PM Eastern, which is 5 November, 7:30 AM IST after the US daylight-saving transition. Aim to be submission-ready on 3 November.

Status legend: [ ] not done; [x] complete. A task is complete only with its stated artifact/evidence.

## Planning completed

- [x] Concrete first application selected: two-heater thermal model calibration.
- [x] Existing simulator/reference sources identified; TCLab repository license inspected.
- [x] Product workflow, architecture, comparison protocol and demo specified.
- [ ] Public physical-data file downloaded, license verified and data semantics inspected. Published examples were identified; no usable local evaluation dataset is confirmed yet.
- [ ] Protocol constants and numerical thresholds frozen.
- [x] Initial numerical implementation and 18-case development comparison; see the milestone note below. This is not the held-out comparison or a Meta result.

## Day 1 — 28 October: establish the evidence

Morning / first 2 hours:
- [ ] Inspect existing numerical dependencies, Meta adapter and project instruction boundaries.
- [ ] Record exact upstream revision/license for simulator/reference code.
- [x] Implement the public experiment contract and a separate hidden thermal simulator (separate process; no OS sandbox).
- [x] Implement numerical fitting, unseen-schedule prediction and error scoring (ARX baseline; not the planned mechanistic grammar).
- [x] Run fixed and random schedule development comparisons locally.
- [ ] Freeze useful prediction thresholds and verify noise-floor assumptions.

Next 2 hours:
- [x] Implement a regularized D-optimal ARX design baseline across the supported candidate library; its information criterion remains an approximation under output noise.
- [ ] Check underdetermined and unsupported cases. Independent prediction errors must expose failures.
- [ ] Freeze initial protocol and development/test seed separation before Meta comparison calls.

Next 2–4 hours:
- [x] Implement a bounded Meta Responses decision adapter using the existing endpoint/credential convention; local mocked-transport checks pass. Live behavior remains untested.
- [x] Run the bounded integration smoke pilot: six Meta calls, estimated $0.0463. Both policies reproduced D-optimal choices; no benefit from the investigation prompt was observed.
- [ ] Run the paired comparison pilot if the smoke pilot is valid.
- [ ] Publish a continuation decision with all methods and failures. If speed/cost prevents the comparison, report that as unresolved instead of marking the day successful.

Acceptance: a saved run contains an experiment, model fit, prediction committed before held-out observations, independent score and comparison. A screenshot or persuasive explanation is insufficient. Day 1 earns the claim or exposes its weakness.

## Day 2 — 29 October: make the investigation persistent

- [ ] Versioned candidate models and evidence-linked revisions.
- [ ] Reliable budget accounting, stop/resume and duplicate-action prevention.
- [ ] Bounded investigation API using existing backend conventions.
- [ ] Direct Meta baseline receives equivalent tools and limits.

Acceptance: resume an interrupted run without repeating the last experiment; each revision links to a measured result.

## Day 3 — 30 October: build the investigation workspace

- [ ] Two-heater schematic with actual input and measurement states.
- [ ] Candidate overlays with clear measured/predicted distinction.
- [ ] Proposed-experiment card: objective, schedule, predicted disagreement, cost.
- [ ] Run/pause/stop, remaining budget, and evidence inspector.

Acceptance: a user can follow a complete stored/live simulated investigation without opening a terminal. Replay is explicitly labeled.

## Day 4 — 31 October: make the challenge interactive

- [ ] User chooses an unseen legal input schedule and freezes a prediction.
- [ ] Independent challenge execution and per-sensor error display.
- [ ] Add condition-change detection/recovery only if A/B investigations work.
- [ ] Add an unchanged control for change-detection false alarms.

Acceptance: a changed input can falsify the displayed model, and failure remains visible.

## Day 5 — 1 November: perform final validation

- [ ] Fresh paired evaluation set, strongest conventional baseline and uncertainty/failure report.
- [ ] Real-recording external check if a licensed dataset is available.
- [ ] Measure API cost, end-to-end latency and realistic demo duration.
- [ ] Claims audit: every accuracy, experiment-saving or recovery claim links to a result.

Acceptance: reproducible report and raw artifacts, with simulation/replay distinctions and complete failures.

## Day 6 — 2 November: polish and package

- [ ] Clear user copy, accessible controls, readable plots and responsive layout.
- [ ] Clean installation instructions, dependency versions, sources and license notices.
- [ ] Separate our hackathon contribution from upstream tools and older code.
- [ ] Make repo public when authorized at submission stage; prior user preference was to defer public visibility.
- [ ] Demo rehearsal with actual measured runtime; label cuts/time compression.

Acceptance: another person can run the documented scenario and reproduce its recorded outcome.

## Day 7 — 3 November: record and prepare submission

- [ ] Record <=3-minute demo.
- [ ] Verify video/repository access and submission fields.
- [ ] Prepare concise impact, Meta role, technical contribution and limitations descriptions.
- [ ] Submit once user confirms final external submission, or hand over exact completed submission assets for the user's own submission.

Acceptance: complete submission assets and links, ready before the final deadline buffer.

## 4 November — buffer

Fix submission/access failures only unless a critical correctness issue requires a repair. Preserve the reproducible demonstrated version.

## Priorities

P0: valid lab contract; fitting; strong baseline; meaningful Meta investigation; independently scored unseen prediction; evidence ledger.
P1: interactive challenge; readable explanatory workspace; replay and export; model revision from mismatch.
P2: condition-change recovery; recorded-hardware external check; optional voice input.

Avoid scope expansion into arbitrary physical systems, vision reconstruction, robot control, connected hardware, autonomous shell/code execution, multi-agent proliferation, authentication or marketplaces.

## Budget

The user previously reported roughly $150 initial credits; current remaining balance is unknown. Do not treat that old figure as current. Verify price/model and balance if available before estimating a paid batch. Bound calls and output tokens, save responses, disable automatic retries, and record usage. Reserve capacity for evaluation and demo instead of spending it on repeated exploratory runs.

## Milestone 1 result — 28 October

Implemented an original two-node thermal simulator with optional sensor delay, two numerical ARX predictor families, fixed/random/simple disagreement strategies, a budgeted subprocess lab interface and prediction commitments. All 18 development cases complete; 11 invariant/numerical checks pass. Runtime: Python 3.12.14, NumPy (exact version saved in the run config). No Meta calls.

Median per-sensor RMSE in degrees Celsius, three development seeds each:

| System | Fixed | Random | Simple disagreement |
|---|---:|---:|---:|
| Coupled | 0.0188 | 0.0525 | 0.0259 |
| Sensor delay | 0.1755 | 0.4163 | 0.1791 |

Fixed schedules are strongest in this small development run. The disagreement heuristic has no demonstrated advantage. The stronger conventional active-design baseline, Meta investigation decisions, fresh challenge families, physical-data check and product UI remain outstanding. The ARX baseline does not recover a physical mechanism.

A validation-handling bug was corrected: a stable fit on all data may remain provisional when a reduced-data validation fold is unstable; the result must not claim complete validation. The original failed run remains available locally. Public recorded results use the corrected run.


## Milestone 2 — experiment selection and offline Meta adapter

Implemented regularized D-optimal regressor design, explicit evidence-citing decisions, a six-call/$1 guarded Meta adapter, cache/no-repeat handling and offline run review. A model-selection issue was corrected: independently validated models take priority over provisional models; their incomparable fallback scores are no longer mixed.

All 24 development runs complete and 23 tests pass. No live Meta request was made, including after the user's credit-preservation instruction. A dry run of the proposed pilot displays its protocol without loading credentials or creating output.

D-optimal median RMSE: coupled 0.0162°C, sensor delay 0.2438°C. Fixed remains stronger on the delay cases. Meta's scientific contribution, structural generation and held-out advantage remain unproven. The next evidence step is the bounded integration pilot and then a fresh paired comparison; it must not be confused with a completed contribution gate.


## Milestone 3 — live integration result and executable physical models

The six-call pilot completed on the frozen development case. Mean per-sensor prediction errors: fixed 0.1946°C; random 0.4135°C; disagreement 0.8469°C; D-optimal 0.3692°C; direct Meta 0.3692°C; investigation Meta 0.3692°C. Both Meta policies chose staggered then left-pulse, and submitted ARX order two. This integration works, but no advantage was demonstrated. The six calls used 26,830 input tokens and 3,001 output tokens; the local rate-based estimate is $0.04629175. This is not a confirmed billing balance. No additional model calls were made in this milestone.

Added bounded executable thermal models: two heat-flow nodes with positive effective loss, coupling and input coefficients; optional shared sensor lag; constrained numerical fitting; exact discrete prediction; whole-trial model validation; and export/re-execution with strict specification parsing. No generated Python is executed.

Two known development cases use the same three fixed experiments. The selected families match the simulated configurations, with 0.01240°C and 0.01234°C prediction RMSE. This gain is from a supplied physical family and numerical fitting. Meta has not generated a new mechanism or demonstrated a contribution to these results. Thirty tests pass including the optional scientific suite.

Next unresolved gate: a substantive Meta investigation role and improvement relative to a strong physical-model baseline, evaluated on fresh cases. Keep the paid pilot exhausted, preserve its original outputs, and do not continue spending credits by rephrasing the same experiment-selection prompt.


## Fresh simulated-system validation — October 28

Completed 30 fresh systems and three challenges per system, comparing physical calibration and ARX on identical training data. Evidence: `experiments/thermal-investigator/results/fresh-validation-2026-10-28/REPORT.md`. All 60 supported-family physical predictions stay below 0.3°C RMSE. Nonlinear stress causes eight threshold failures; training validation flags only one. Reliability detection is unresolved. No Meta calls. The suite now has 33 passing tests. Next: prospective model-adequacy checks using new excitation, before any stronger reliability claim.
