# Thermal Investigator — numerical experiment

This is the first implementation of the experimental-investigator plan. It learns temperature-response predictors from bounded experiments and independently scores a future input schedule. **Current status: numerical baseline only; no Meta investigation decisions yet.**

## Run

Requires Python 3.12+ and NumPy 1.26+:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m thermal_investigator.run --output .runs/my-development-run
.venv/bin/python -m unittest discover -s tests -v
```

Each output directory must be new. `--additional 3` chooses three additional experiments after the common initial trace. `--seeds 11 23 37` selects development instances; those cases are not held out. The lab runs in a separate local process. There is no provider/network call.

The Codex bundled Python runtime also has NumPy available; it was used for the recorded development run. Its absolute path is machine-specific and is not required for ordinary installation.

## What runs

- Original two-node lumped thermal simulation with optional sensor lag, noisy readings, bounded heater commands and fixed-duration experiments.
- Numerical autoregressive predictors of orders one and two, fitted by regularized least squares.
- Whole-trial leave-one-out validation for model selection. If a reduced-data fit is unstable but the full-data model is valid, its validation remains explicitly incomplete.
- Fixed schedules, random schedules and a simple between-family disagreement selector.
- Prediction commitment before challenge results, SHA-256 integrity check, JSON event ledger, error report and SVG trace plot.

This code is not copied from TCLab, and it is not validated against TCLab hardware. Standard heat-balance equations supply the simulator; predictor coefficients do not establish the true mechanism. Candidate models receive observed traces and controls, not hidden coefficients or labels.

## Experimental assumptions

Every trial starts from idealized exact ambient equilibrium. A standardized 300-second reset charge is accounted for; no physical cooling procedure has been verified. Heater commands are limited to 65%, every experiment lasts 120 seconds, and sampling is every two seconds. The simulator enforces a 60°C temperature ceiling; this is not hardware safety certification.

Observed training readings contain 0.08°C Gaussian noise. Evaluation scores against the hidden noise-free sensor trace, explicitly labeled in the result. The 10°C normalization is a fixed development reference scale; absolute RMSE is the interpretable headline metric.

One public challenge input schedule is used here. The output remains sealed until the model's prediction file is written, after which the investigation closes. These are development examples, not the planned randomized held-out evaluation.

All strategies have the same action count, duration and reset charge. Energy proxies vary and are reported; this is a time-budget comparison, not a matched-energy experiment. Numerical disagreement is a heuristic and is not the strongest conventional optimal-design baseline promised in the final protocol.

## Isolation limits

The process boundary prevents accidental imports of hidden state into the predictor. It is not an operating-system sandbox. Future Meta tools must expose only the public lab interface and cannot receive shell/filesystem access, private configuration or challenge output files. The comparison runner knows the development seed; the eventual agent must not.

## Development result

The 18-case run across two systems, three development seeds and three strategies completed after correcting validation handling. Fixed schedules had the lowest median error on both systems. The simple active heuristic has not shown an advantage. No superiority or novelty claim follows from this run.

See `results/development-2026-10-28/REPORT.md` when present in the repository. Full local runs live under ignored `.runs/`.

## Next implementation

1. Implement a stronger conventional active-design baseline and freeze evaluation thresholds/cases.
2. Add evidence-linked Meta decisions through a bounded declarative specification.
3. Compare that investigator and a direct tool-using Meta agent with equal information, models and budgets.
4. Build the product workspace once the scientific decision gate passes.
