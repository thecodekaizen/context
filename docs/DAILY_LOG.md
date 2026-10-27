# Hackathon daily log

## Tue Oct 27 — Day 1

### Shipped

- Raw-only Muse discovery CLI with structured evidence references, deterministic citation validation, and a tentative-language rejection guard.
- Project-level Muse memory extraction with stable topic tags, source-linked temporal memories, repository-root caching, and a local spend ledger.
- Temporal comparison output now keeps continuity evidence separate from the themes driving the candidate shift.
- Interactive CLI review flow: creator context, keep/revise/reject/defer, exact `CONFIRM`, and a source-linked direction note.
- All output/session data stays in ignored local folders; source artifacts in the repo are synthetic.

### Evidence

- [Neighborhood Atlas direct raw-discovery scorecard](experiments/results/neighborhood-atlas-2026-10-27.md): overall **FAIL** because the full finding was unqualified; the ablation correctly withheld it.
- [Tiny Type Lab direct raw-discovery scorecard](experiments/results/type-foundry-2026-10-27.md): preregistered full and ablation checks **PASS**.
- [Tiny Type Lab memory-path smoke](experiments/results/project-memory-pipeline-smoke-2026-10-27.md): exploratory prompt iteration; not independent validation.
- [Roomtone batch-memory scorecard](experiments/results/roomtone-memory-2026-10-27.md): preregistered full and ablation checks **PASS**.
- [Paper Satellites raw-discovery scorecard](experiments/results/paper-satellites-2026-10-27.md): full case passed; ablation **FAILED** because Muse promoted an early two-voice pilot into a project-level evolution claim. The preregistered minimal-reasoning setting also differed from the runner's high-reasoning setting; both limitations are recorded.

### Verification and spend

- `python -m unittest discover -s backend/tests -v`: 20 passed.
- `python -m thread_engine.evaluate`: 6/6 seed cases matched.
- Local token-based estimated spend: **$0.080430** after the Paper Satellites calls; check the Meta Billing dashboard for actual usage.

### Next engineering focus

Use a new, consented or synthetic archive that was not used to shape the prompts; test source ingestion and memory quality on multimodal input only if time and rights-safe material permit. Keep the CLI as the product surface unless the creator changes that scope.
