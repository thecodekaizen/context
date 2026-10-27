# SHOWME hackathon daily log

This log records SHOWME work only. Earlier entries described the retired THREAD direction and are preserved in Git history; do not use them as current progress evidence.

## Tue Oct 27 — Day 1

### Current phase

**Phase 1 — learn one demonstration: in progress.** The CLI can prepare a clip, call Muse Spark, validate a candidate process, observe a learner clip, and validate timestamped observations. This is infrastructure, not proof that the capability works reliably.

### Evidence and outcome

- The CaptainCook4D stock-footage evaluation is **P0 FAIL**. Muse omitted the decisive action during learning and missed the annotated ordering error during observation. It also produced no divergence on a normal control, but the prompt and expert crop changed between runs, so that apparent improvement is confounded.
- The result is documented in [`captaincook4d-ordering-observation-v2-2026-10-27.md`](experiments/results/captaincook4d-ordering-observation-v2-2026-10-27.md). Earlier exploratory results are in the neighboring `experiments/results/` files.
- The stock footage remains useful for pipeline checks and failure analysis. It does not establish the SHOWME thesis.
- Process and observation validation has automated tests; the latest run recorded in the experiment notes passed the CLI/test checks, but these do not replace a successful behavioral evaluation.

### Decisions

- Keep the CLI experiment as the current work; do not build the SHOWME UI, SAM overlays, or simulation on a failed P0 result.
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
| SAM visual grounding | Not started | Begin only after baseline state distinctions pass |
| Procedural what-if simulation | Not started | Begin only after P0 passes |
| SHOWME app and visual mockups | Two concept mockups; app implementation gated | See [`SHOWME_APP_PLAN.md`](SHOWME_APP_PLAN.md); example assembly is illustrative only |
| Demo video and submission | Not started | Only show capabilities that pass evaluation |
