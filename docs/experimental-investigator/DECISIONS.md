# Decisions, risks and source record

## D01 — Pursue an ambitious experimental investigator

User explicitly stated willingness to work on hard problems and approved planning this proposal. No prize probability is claimed. The experimental claim must survive comparisons.

## D02 — Choose thermal calibration as the first application

Two heater commands and two temperatures provide concrete experimental inputs/outputs. This translates the abstract unknown-physics example into a recognizable engineering task. Use simulation initially; hardware is optional and not on the critical path.

The working outcome is a useful predictive model under a limited experiment budget. Extrapolation to factories, energy savings or industrial reliability requires additional evidence.

## D03 — Use established numerical methods and disclose supplied knowledge

Fitting and active design are existing fields. Start with a bounded thermal model grammar and existing solvers. Meta's contribution hypothesis is evidence-driven structural/investigative decisions. Strong comparison methods receive the same model library and numerical tools.

## D04 — Evaluate prediction and experimental effort

Exact coefficients may not be identifiable. Report predictions, uncertainty and remaining ambiguity. Do not manufacture a precise physical explanation from insufficient observations.

## D05 — Freeze evaluation and keep ground truth inaccessible

Public source provenance is retained for reproducibility, while world configurations, labels and challenge observations stay outside the runtime agent interface. Our developer can inspect the simulator; the agent doing the experiment cannot. Source familiarity is addressed through randomized hidden instances and fresh held-out cases, not claims that the developer has never seen the equations.

## D06 — Preserve existing work; plan outside the stale checkout

The SHOWME repo has valuable provider/media infrastructure and another agent's uncommitted frontend changes. Existing locked-product documents are historical after the user's pivot. The first experiment should be isolated; update repo instructions and reconcile work ownership before integration. Do not mix old UI claims with the new investigation.

## D07 — Build on the existing Python/Next stack

The build-agents skill was consulted. Its established non-eve-stack exception applies to reuse of the current Python model adapter/backend. Adding a framework would not itself improve the scientific result.

## D08 — Keep Meta integration substantive

Use Spark's confirmed structured/tool reasoning capability, verify exact adapter behavior, and measure its contribution. SAM, voice, image generation and open weights are optional only when needed. A simulation is computed; generated video is not a measurement.

## Major risks and responses

1. A strong conventional active-design method already solves the task: report parity or loss; test the structural-mismatch case fairly. No superior-results claim without a measured advantage.
2. Meta only verbalizes numerical decisions: enforce the substantive-decision gate and inspect the direct-tool agent comparison.
3. Numerical fitting is unstable or parameters unidentifiable: constrain effective models, use repeated initializations and report ambiguity; do not rank by explanation fluency.
4. Public physical recordings lack suitable licenses or independent runs: keep the external check unresolved and label the proof simulation-only. Do not substitute simulated data while claiming hardware evidence.
5. The UI becomes a chart dashboard: make proposed experiments, actions, frozen predictions and challenge results the central workflow.
6. Deadline pressure encourages selecting a successful seed: freeze paired cases and publish every failure. Mark curated demo runs as examples.

## Sources checked on 28 October 2026

- Official hackathon themes and Indie description: https://cerebralvalley.ai/e/meta-ai-developer-hackathon
- Participant details route returned a loading shell during browsing; weighted rubric and public-repo/demo requirements come from the user's supplied guide and kickoff screenshots: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details
- TCLab public Python package, offline model and hardware interface: https://github.com/jckantor/TCLab
- TCLab Apache-2.0 license: https://raw.githubusercontent.com/jckantor/TCLab/master/LICENSE.txt
- TCLab modeling/control reference: https://www.apmonitor.com/pdc/index.php/Main/ArduinoTemperatureControl
- Notre Dame experimental-design notebook describes actual step and sine system-identification tests: https://colab.research.google.com/github/dowlinglab/pyomo-doe/blob/main/notebooks/tclab_model.ipynb
  Search surfaced its text, but direct notebook/raw retrieval failed during this planning pass. A dataset has not been downloaded or approved for reuse.
- Existing interactive thermal fitting/simulation tools: https://apmonitor.com/apps/
- DiscoverPhysics: simulated hidden-law discovery, not an empty field: https://sampsonml.github.io/DiscoverPhysicsLeaderboard/
- Identifiability-focused experimental-agent prior work, preprint: https://arxiv.org/abs/2610.11253
- Autonomous Science Bench: real-data replay and simulated campaigns; live hardware contract is not equivalent to demonstrated hardware operation: https://github.com/Yibo-Wen/as-bench
- Meta documented model roles and Spark version: https://dev.meta.ai/docs/models

Meta pricing was not verified in this planning pass; a guessed pricing route did not load. Budget estimates remain unresolved until the linked official pricing page is read.


## D09 — Implement a numerical ARX baseline before a mechanistic grammar

The first milestone uses first/second-order autoregressive input-output models, not generated physical equations. This establishes numerical prediction, leakage boundaries, action budgets and a comparison floor with NumPy alone. The original heat-balance simulator is not copied from or calibrated to TCLab. Its reset is an explicitly idealized exact-ambient fixture with a fixed time charge. Stronger experimental design and evidence-driven structural modeling remain future work.

The comparison is currently time/action matched, not energy matched. Preserve that distinction in claims. The challenge uses one predeclared input sequence and development instances; it is not the frozen final test.


## D10 — Preserve credits and make provider work explicit

User requested preservation of hackathon credits, then cancelled the Muse configuration detour. No coding-provider configuration was edited and no live Meta experiment was run. Default experiment and pilot dry-run commands incur no API cost. The adapter has a persistent call/cost guard and no automatic retries. An explicit live invocation is distinct from ordinary local development.

Meta Standard pricing verified from https://dev.meta.ai/docs/pricing-rate-limits on 28 October 2026: input $1.25/M, output $4.25/M, cached input $0.15/M. These rates support local estimates; account balance is still unknown.

The new conventional method is D-optimal regressor-information selection averaged per parameter across supplied ARX families, with fixed scaling and regularization. Treat it as an approximation because regressors contain noisy outputs; do not call it globally optimal.


## D11 — Record the negative Meta result and strengthen the actual model representation

Both Meta policies in the first integration smoke pilot chose the conventional D-optimal action sequence and model. Their identical 0.3692°C error was worse than fixed experiments on the same development instance. No investigation benefit was observed. Estimated usage cost: $0.04629175; six calls with no retries. Preserve the result, including raw synthetic-context responses, and do not treat a successful API integration as scientific success.

Implemented a bounded physical representation with effective heat-loss rates, bidirectional coupling, heater gains and optional sensor lag. The supplied model grammar is engineering prior knowledge; selecting/fitting it does not discover arbitrary physics. The independent predictor uses exact matrix-exponential transitions and is checked against the environment's RK4 integration.

SciPy 1.18.1 was installed only in the isolated local experiment virtual environment. The source declares a science optional dependency; base numerical checks still need only NumPy. Sources checked: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html and https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.expm.html .

Model parameters are effective ratios, not individually identified thermal masses or conductances. Numerical sensitivity rank is a local diagnostic, not a formal identifiability certificate. The physical development check has no Meta decisions and does not meet the substantive-Meta contribution gate.
