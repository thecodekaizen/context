# Product contract

## Purpose

Help an engineer learn a useful predictive model of a thermal system with limited experiments. The product recommends and runs informative experiments in a simulator, compares competing models, exposes remaining uncertainty, and tests future predictions.

Primary outcome: predict both measured temperatures under a new heater-input schedule within a declared error target, using a recorded experimental budget.

## Why this application

Two nearby heated components interact. A short temperature trace may be consistent with different heat-transfer rates, delayed sensor readings or different model structures. Additional measurements take time. The system must choose interventions that distinguish explanations and determine when the current model is inadequate.

The first testbed is thermal rather than the illustrative moving-object example. TCLab provides a concrete engineering reference, two controllable inputs, two observations, an offline simulator and published experiments. No new hardware is required for the simulation proof.

## Final hackathon workflow

1. Open a thermal-system investigation. See a schematic, available controls, observed temperatures, declared operating envelope and remaining experimental budget.
2. Give a concrete goal: identify temperature response under a new heater schedule.
3. Run the common initial experiment. See provisional candidate models and the evidence that supports or challenges each.
4. The investigator proposes the next experiment and explains which candidate predictions it will distinguish. Inspect and approve it, or use bounded automatic mode within the declared envelope.
5. Run the experiment. Predictions are stored before measurements are revealed. Show measured and predicted traces together.
6. Update fitted models. Explain rejected candidates and unsupported distinctions. Numerical tools determine fit and error.
7. Challenge the learned model with an unseen input. Score the prediction independently.
8. Optionally change a hidden system condition. Observe that the old model fails, gather new evidence and revise it. Changes have evaluator timestamps and are not revealed to the agent in advance.
9. Export the experiment ledger, model specification, prediction traces and comparison report.

## Visible surfaces

A single investigation workspace contains three tasks:
- Investigate: system schematic, experiment timeline, input controls, candidate predictions and remaining budget.
- Challenge: freeze a model, run an unseen schedule, inspect the resulting error and failure modes.
- Inspect evidence: open any model decision and trace it to the experiment and numerical result that caused it.

The interface may animate heaters and temperature flow from computed state. Colors and animations are explanatory displays, not additional sensor measurements. Evaluation figures must show exact units, axes and simulation timestamps.

## Claim boundaries

Simulation runs are labeled simulation. Evaluation on recorded hardware data is labeled replay. Hardware experiments require actual connected hardware and a separate integration review. Replay data never stands in for an experiment that the agent selected and physically executed.

The bounded model grammar is supplied engineering knowledge. Selecting a known model structure is not invention of a new physical law. Exact hidden parameters are not always identifiable; useful predictions can be accepted while mechanism ambiguity remains explicit.

No requirement to use every Meta model. Spark's substantive role is proposing/revising model structure and planning investigations from evidence. If ordinary numerical selection provides the same outcome without that reasoning, report it.

## Intended contribution

Evaluate whether evidence-driven model-structure revision plus numerical experiment selection improves prediction per experimental budget, especially when the initial model is inadequate or conditions change. This is an unproven contribution hypothesis. Established system identification and active experimental design are prior art.
