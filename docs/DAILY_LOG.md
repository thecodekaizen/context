# Hackathon daily log

## Tue Oct 27 — Day 1

### Shipped

- Raw-only Muse discovery CLI with structured evidence references, deterministic citation validation, and a tentative-language rejection guard.
- Project-level Muse memory extraction with stable topic tags, source-linked temporal memories, repository-root caching, and a local spend ledger.
- Temporal comparison output now keeps continuity evidence separate from the themes driving the candidate shift.
- Interactive CLI review flow: creator context, keep/revise/reject/defer, exact `CONFIRM`, and a source-linked direction note.
- Direct raw Muse discoveries can now flow into the same creator-review CLI; the interview shows model-classified source stages and the confirmed note preserves observations, limitations, and source IDs. An empty candidate skips the interview.
- Raw-discovery observations now include a source-linked evidence stage (`planned`, `experimental`, `ongoing`, `released`, or `unclear`), with local validation and CLI timeline display. This makes experiment-vs-release status inspectable; it does not yet prevent unsupported direction claims.
- Raw Muse API status and incomplete-response reasons are now reported and cached on failures; live successful calls show their response status. A cached Cook's Margin replay also caught and fixed a missing project-title display.
- Raw discovery now uses minimal reasoning and includes reasoning effort and output-token cap in cache identity, following the Cook's Margin ablation that exhausted the cap.
- Raw discovery's local gate now requires supporting citations in the earliest and latest chronological quarters. The previous midpoint gate admitted the Pocket Observatory ablation; the strengthened rule withholds its cached candidate while allowing the full candidate, without another API call. This is a post-hoc regression check, not independent validation.
- All output/session data stays in ignored local folders; source artifacts in the repo are synthetic.

### Evidence

- [Neighborhood Atlas direct raw-discovery scorecard](experiments/results/neighborhood-atlas-2026-10-27.md): overall **FAIL** because the full finding was unqualified; the ablation correctly withheld it.
- [Tiny Type Lab direct raw-discovery scorecard](experiments/results/type-foundry-2026-10-27.md): preregistered full and ablation checks **PASS**.
- [Tiny Type Lab memory-path smoke](experiments/results/project-memory-pipeline-smoke-2026-10-27.md): exploratory prompt iteration; not independent validation.
- [Roomtone batch-memory scorecard](experiments/results/roomtone-memory-2026-10-27.md): preregistered full and ablation checks **PASS**.
- [Paper Satellites raw-discovery scorecard](experiments/results/paper-satellites-2026-10-27.md): full case passed; ablation **FAILED** because Muse promoted an early two-voice pilot into a project-level evolution claim. The preregistered minimal-reasoning setting also differed from the runner's high-reasoning setting; both limitations are recorded.
- [Cook's Margin evidence-stage scorecard](experiments/results/cooks-margin-2026-10-27.md): complete case passed with expected source-stage labels; the ablation returned invalid JSON at the output cap, so the overall result is **inconclusive**. No retry was made.
- [Repair Margins minimal-reasoning scorecard](experiments/results/repair-margins-2026-10-27.md): ablation correctly limited the proposal/pilot; full case **failed** temporal support because the supporting list omitted early artifacts. Both calls completed below the output cap.
- [Pocket Observatory temporal-support gate scorecard](experiments/results/pocket-observatory-2026-10-27.md): after the initial sandbox DNS failure, user-requested network-enabled calls completed; full case missed map continuity and ablation candidate was accepted by the weak midpoint gate. Overall **FAIL**.
- [Ember Table endpoint-support scorecard](experiments/results/ember-table-2026-10-27.md): endpoint-supported full case and empty ablation; full hypothesis omitted that the booklet was completed, so overall **FAIL** under frozen criteria.

### Verification and spend

- `python -m unittest discover -s backend/tests -v`: 25 passed after temporal-support validation.
- `python -m thread_engine.evaluate`: 6/6 seed cases matched.
- Local token-based estimated spend: **$0.120499** after the Repair Margins calls; check the Meta Billing dashboard for actual usage.
- Pocket Observatory calls added an estimated **$0.010176**, bringing the local token estimate to **$0.130675**. The CLI now disables SDK transport retries and reports actionable network errors; sandbox DNS access still requires running the CLI with network permission.
- Ember Table calls added an estimated **$0.008687**, bringing the local token estimate to **$0.139361**. Confirm actual totals in Meta Billing.

### Next engineering focus

Use a new, consented or synthetic archive that was not used to shape the prompts; test source ingestion and memory quality on multimodal input only if time and rights-safe material permit. Keep the CLI as the product surface unless the creator changes that scope.
