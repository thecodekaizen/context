# Experiment and evaluation protocol

Status: umbrella protocol; individual recorded runs have frozen versioned configurations. The initial smoke used six calls as recorded in its protocol, superseding the earlier illustrative twelve-call allowance below. Local development checks are not the final comparative Meta evaluation. Freeze exact scenario generation, metrics, budgets and thresholds before each comparative run. Development results may motivate amendments, but every amendment creates a new version and invalidates use of earlier cases as held-out evidence.

## 1. Public problem interface

Two heater commands Q1 and Q2 (percent), two noisy temperature observations T1 and T2 (degrees Celsius), elapsed simulated time (seconds), ambient reading where provided, and remaining budget. Observations include timestamps and instrument/noise metadata. The agent knows the allowed model grammar and action limits, not the selected hidden structure, parameters, seed or future measurements.

Public actions: piecewise-constant heater schedule; duration; wait/cool-down; request another observation; stop. Start with a bounded library of legal pulse/step schedules for tractable comparison. A selected-library experiment is disclosed as such. Add continuous action optimization only after this works.

Reset to a declared starting state between independent trials. Charge reset/cool-down time to all methods. Alternatively use continuous trajectories for all methods; do not give one strategy free resets. A rejected or early-stopped experiment still consumes its executed duration and attempted-action slot.

Declare a simulation operating envelope before running. The environment enforces it and logs early termination. Hardware safety is outside this simulation implementation; simulator bounds do not certify a physical experiment.

## 2. Worlds and model knowledge

A: two-body coupled thermal response, randomized effective parameters.
B: a sensor lag or additional thermal state that makes an initial simpler model inadequate.
C: an announced-in-evaluation, unannounced-to-agent condition change during a session, such as altered effective heat loss. This is a stress test only after A/B pass.

No world name, class ID or decisive parameter leaks through session IDs, tool errors, filenames, plot titles or prompts. Candidate families include plausible alternatives for every method allowed structural selection. Include at least one mismatch outside the supported grammar; correct behavior is to report inadequate predictions and uncertainty, not manufacture a correct mechanism.

## 3. Separate modules and records

Keep hidden simulator/evaluator configuration in a process unavailable through agent tools. Training traces, candidate models and held-out schedules are distinct records. The planning model receives only public experiment outputs. Do not send simulator source or evaluation answer keys to Meta.

Split observations into fitting and local validation segments. Model-selection checks use whole unseen input segments or trials, not a random split of autocorrelated neighboring time samples. Final challenge traces remain sealed until the model and prediction are frozen.

The agent may know general thermal equations; that is engineering prior knowledge, not leakage. Do not equate recovery of familiar equations with original scientific discovery.

## 4. Fair comparison methods

B0: common initial step test plus a fixed, useful identification schedule.
B1: random legal experiment selection across paired seeds; repeat it to estimate variation.
B2: conventional active design: numerical fitting and the same full candidate library, selecting experiments by predicted disagreement or a standard information criterion. Include automatic numerical model selection; do not artificially restrict this baseline to a known-wrong family.
B3: direct Meta tool-using agent with the same fitting, prediction and experiment tools, public information and budgets, but without the specialized investigation memory/consistency orchestration.
S: proposed investigator: evidence-linked model revision, numerical candidate fitting and bounded active experiment selection.

All methods get identical observations, legal inputs, simulated experimental time, initial data, reset policy and measurement resolution. Report wall time, fitting compute, Meta calls, token use and cost separately. Both B3 and S use the same Meta model/version and comparable inference limits. Avoid claiming a prompt-only baseline is equivalent to a competent tool-using baseline.

## 5. Metrics

Primary: per-sensor RMSE in degrees Celsius on frozen held-out schedules, plus normalized RMSE using the evaluator's fixed reference response scale. Define a nonzero noise-aware denominator in advance; do not normalize by each method's prediction or chosen excitation.

Efficiency: experimental seconds, resets, action count and energy proxy (integral of commanded power) needed to reach the declared prediction target. If the target is never met, report censored failure at budget exhaustion.

Reliability: violations, invalid models, false confident mechanism claims, uncertainty coverage and repeated-seed variation. A prediction interval requires a defined residual/bootstrap procedure; model disagreement is not automatically calibrated uncertainty.

Change recovery: detection delay, false alarms in unchanged controls, extra experimental budget and error after recovery. Do not score successful recovery from a single deliberately favorable example.

Do not use LLM judging as the primary correctness metric. Parameter or mechanism scores are optional and only valid where identifiability has been checked.

## 6. Staged execution budgets

Development: deterministic local runs; no API cost. Inspect ordinary fitting and conventional active design first.

Initial Meta smoke pilot: two development seeds × at most three decision calls × two scenarios = at most 12 decision calls, no automatic retries. Enforce a maximum output-token count, a total-token ceiling and a recorded price estimate before launch. A dollar guard is only reliable after the actual model price is verified. No live API request is authorized merely by this planning document.

Comparison pilot: ten new paired instances balanced across A/B. Limit each method to the same six additional experiment actions after the common initial trace. This small sample supports a feasibility decision, not broad scientific superiority. Publish all failures and all methods.

Final check: a fresh, frozen set of at least 20 paired instances if cost and runtime permit. If this cannot be run, report the smaller sample and avoid claims of generality. Evaluation outcomes must not feed further tuning on the same test set.

## 7. Decision criteria

First establish that a conventional model can reach a useful absolute prediction threshold above the instrument noise floor. Set that threshold from documented system scale and numerical checks before comparing strategies. No arbitrary claimed accuracy percentage.

Proposed practical improvement threshold for the comparison pilot: at least 20% lower median held-out error at matched experimental budget, or at least 25% lower median experimental time to the same accuracy target, versus the strongest applicable baseline. Select which endpoint is primary before results. Show paired results and spread; a median threshold alone does not establish statistical certainty.

Additional gate: Meta must make at least one consequential, evidence-supported structural or investigative decision. A numerical optimizer doing all meaningful work with model-written narration does not pass the Meta contribution gate.

If there is no advantage, examine whether structure revision, fitting, observability or action choice caused the plateau. Allow one documented narrowing within thermal identification and rerun on fresh cases. Do not add a second application or hide the result behind UI. Decide to continue or stop the contribution claim by the end of the first development day.

## 8. Physical data external check

Locate a public TCLab input/temperature recording, verify its license and meaning, and select separate fitting/validation runs. Record source URL, revision, file hash, units and preprocessing. Hold the test run out. This can check numerical-model behavior on real measurements. It cannot demonstrate that our active strategy collected those measurements or saved real experimental time.

No claim of energy savings, industrial deployment, hardware control or newly discovered physics follows from this experiment.
