# Experimental Investigator — delivery plan

Date: 28 October 2026. Working description, not a cleared brand name.

The user approved planning an ambitious experimental investigator after withdrawing the scientific-scene editor. This bundle defines the selected first application and the evidence required to continue. It does not report a successful experiment or claim a scientific breakthrough.

## Read in this order

1. CONTRIBUTION_REVIEW.md — completed comparison and negative advantage result.
2. STATUS.md — current evidence, gates and delivery consequences.
3. PRODUCT.md — intended user, problem, outcome and interface.
4. PROTOCOL.md — experiments, fair baselines, evaluation and decision gates.
5. ARCHITECTURE.md — engineering, model responsibilities and boundaries.
6. IMPLEMENTATION.md — seven-day tasks, acceptance criteria and progress.
7. DEMO.md — proposed demonstration; claims remain bounded by recorded results.
8. DECISIONS.md — choices, limitations and evidence sources.

## First application

Calibrate a two-heater thermal system: choose experiments, learn a predictive model of two measured temperatures, and recognize when its predictions no longer fit new observations. A TCLab-inspired simulator provides an accessible first testbed. Published physical measurements may support a separate external check after source/license review; static recordings cannot demonstrate active choice of new real experiments.

The intended user is an engineer calibrating a small thermal process. The intended benefit is less experimental effort for a useful predictive model. User demand, performance superiority and transfer to industrial equipment remain unproven.

## Immediate deliverable

A reproducible command-line experiment with a hidden simulator, a numerical fitting baseline, strict experiment budgets, and prediction scoring on unseen inputs. No product UI is necessary to establish this result.

## Scope status

SHOWME, the remnant planner and the scene editor are paused directions. Their historical documents do not specify this experiment. Existing SHOWME code and uncommitted frontend work remain preserved. The current implementation is isolated under `experiments/thermal-investigator` in this checkout. Root AGENTS.md specifies the pivot. Historical frontend work remains preserved; it does not count as the investigator interface.

Implementation and recorded evaluations now exist. Read STATUS.md for current results; the initial planning text is not a completion report.
