# Inspect the source-aware learner comparison

October 28, 2026. Exploratory single run; not a capability pass.

## Inputs and controls

Explicitly approved payload: compressed IMG_7670 learner clip, saved baseline process (not the unapproved v4 candidate), official LEGO 30727 instruction PDF. No expected error or human answer key was included. One call, no retry. Private hashes, prompt, process copy and raw response are preserved under ignored `.showme-runs/lego-source-comparison-v5-20261028/`.

Muse Spark 1.3, Observe v5; 35.2 seconds; 20,659 input and 2,275 output tokens. The run used the source-aware implementation before the subsequently added automatic semantic process fingerprint; its manifest independently hashes the exact input process file.

## Model output

- At 3 seconds: assembled model reported consistent with S18.
- At 15 seconds: detached wing observed; state unknown, assessed consistent with inspection/disassembly rather than a diagnosed mistake.
- At 17.5 seconds: occluded wing underside unclear.
- At 23 seconds: reattachment reported consistent with S18.
- No divergences; overall no_divergence_observed.
- Reference checks: T1–T17 not shown; T18 matches_reference at 23 seconds. These are model claims, not independent human confirmation.
- Structural validation passed. This confirms usable shape/references, not visual correctness.

## Interpretation

Prior comparisons called detachment a divergence or made questionable size-based diagnoses. This run explicitly had source diagrams and classified the intermediate state as inspection/disassembly. It does not demonstrate successful orientation error detection or recovery. Coarse assembled-state matches cannot establish that every small component is correct.

This run is confounded with earlier comparisons: prompt and reference access changed; the v4 comparison also used a different candidate. No causal accuracy improvement, repeatability rate or false-alarm rate can be inferred. There is no independently labeled attached wrong-orientation state in this report.

## Next core gate

Review visible attachment landmarks against source frames, independently of the model's verdict. Use a fixed reviewed process and fixed prompt for matched correct / wrong-attached / corrected evidence. Do not author the expected mistake into prompts or count an unknown-state inspection as a demonstrated mistake. Existing footage can support this review; no additional recording is automatically required by this run.
