> SUPERSEDED — owner correction, October 30, 2026. The strategy and scope decisions below were not authorized and are withdrawn. The reusable video-intelligence platform remains the product vision, CONTEXT its first application, and PRELUDE/CONTROL future intelligence modules. BYOK, local models, SDK, camera, screen and editor integrations remain architectural goals. Consequential-edit review is the first workflow under validation, not permanent market positioning. Retain technical observations below as historical evidence only.

# CONTEXT product decision — 30 October 2026 (IST)

## Decision

Stop expanding and pitching the unified video-intelligence engine. Continue only as a focused context-loss review tool for editors: “Check whether your short edit changes what the original recording means.” This is a product direction, not a claim of validated customer demand or superior model accuracy. Do not restart the architecture. Preserve existing work; remove unrelated modes from the primary journey in the next implementation step.

The first user is an editor, producer or reviewer who has a short edit and access to the recording/library it came from. The decision they need to make is whether to publish the edit unchanged, restore a qualification, or inspect further. Consumer-wide original discovery is not a credible near-deadline dependency. Existing bounded discovery can remain an explicitly scoped convenience; a supplied source/library is a supported first-class path.

## Why the current product feels unsuccessful

1. It explains machinery rather than a job. “Multimodal Single-Video Investigation,” zero-valued fact-check counters, a roadway hazard mode and a separate comparator compete for attention.
2. Its strongest completed case leads with “0 supported, 0 contradicted, 0 inconclusive.” The valuable source-relative finding comes later. The existing copyMarkdownBrief implementation exports document claim findings and source links but omits the source-relative semantic reviews that supply this case’s actual value.
3. A correct source match is infrastructure, not automatically a meaningful discovery. The OSIRIS example finds a source but returns an inconclusive meaning assessment; it does not demonstrate an alarming contextual omission.
4. We have demonstrated model-assisted interpretation on authored NASA edits, not broad online-video verification or customer benefit.

## Evidence inspected

- Actual rendered app at `/?dossier=83767ad0f4c44a6e93cac7b7eea7dc48`, plus the local original, dossier and comparison receipts. Saved result identifies source audio “Artemis 1 is an uncrewed test, meaning no humans are on board this time” versus edited “humans are on board this time.” This is an authored development example; it is not evidence of field performance. Source was available in the local collection.
- `docs/sprint/evidence/remote-live/source-video-retrieval.json`: real NASA catalog queries acquired “How OSIRIS-REx will Steer Itself to Sample an Asteroid”; match selected using audio correspondence. `remote-dossier.json` retains an inconclusive semantic review. This supports bounded acquisition, not internet-wide discovery or proof that the short clip is misleading.
- `scripts/run_registered_gate.py` and `data/gate-v2/results.json`, with five saved classification receipts: the neutral video-pair prompt already identifies the negation removal, the reordered sequence and the caption contradiction, while accepting both authored faithful edits. Alignment results are computed separately and are not supplied in the model request. Labels are not independently human adjudicated. Five matching authored labels do not establish general accuracy; they do establish that this demo’s semantic insight is obtainable through a plain model prompt.
- `scripts/run_meta_ablation.py:run_tier_2_closed_book` hard-codes an inconclusive caption verdict and inability to distinguish edit meaning; it does not request a comparable semantic judgment. Tier 3 capability booleans often indicate output presence rather than correctness. `docs/ablation-report.md` therefore does not establish superiority or low false-accusation risk.
- `docs/sprint/CASE_RESULTS.md`: eight attempted / seven complete / one partial / five all-check passes in the original authored evaluation. Final code changed afterward. Fresh holdout remains unannotated and its scorer needs correction.
- Prior status inspection freshly passed 116 backend tests, nine browser tests, production build, Python lint and frontend formatting. These establish engineering checks, not demand or semantic correctness.

A new qualitative model comparison was attempted but blocked before execution by automatic approval review because it would upload local media without explicit payload authorization. No new provider result is claimed. Existing receipts provided the relevant simpler baseline instead. No customer interviews, time-saving measurements or independently adjudicated fresh cases were performed in this decision review.

## The concrete product

**Input:** short edit and its original recording, or a source collection containing that recording. No long questionnaire.

**First result:** one reviewable finding, for example: “This cut removes the words ‘no humans.’ The short clip now says humans are aboard.” Label this as a model interpretation and give the two exact media ranges.

**Primary action:** play the edited passage and then the omitted source passage, with enough surrounding context to judge it. The reviewer must be able to hear/see the evidence rather than trust a badge. Ordinary shortening and insufficient evidence receive equally clear treatment.

**Output:** a compact review brief containing the actual compared words/events, source and edit timestamps, source provenance, links to inspect evidence and an explicit unresolved state where appropriate. The reviewer decides what to publish; the software does not infer deception or certify truth.

**Why an application might beat a chat prompt:** finding relevant passages across recordings, reproducible alignment, immediate evidence playback, retained provenance and an exportable review. This workflow advantage must be measured; model intelligence alone is not our differentiator.

## Scope choice

| Option | Decision | Reason |
|---|---|---|
| Unified engine plus CONTEXT/PRELUDE/CONTROL | Stop expanding | No single coherent user decision; evaluation burden exceeds available time. |
| Consumer uploads any viral clip and receives a trustworthy verdict | Reject for this deadline | Unrestricted original retrieval, identity and reliable semantic judgment are not demonstrated. |
| Context-loss review against an available source/library | Pursue with a strict validation gate | Reuses implemented matching, bounded review and playback; source availability is explicit and the result is inspectable. |
| New unrelated hackathon project | Reject now | Would discard working evidence infrastructure without a validated replacement problem. |

## What earns the remaining time

1. Reframe the first screen and result around the editorial question; put the most consequential comparison first. Keep claims research secondary and remove unrelated modes from the hero. Include semantic comparison in the copied brief. Do not imply that UI changes alone validate the product.
2. Use unseen source-disjoint material, including faithful edits, an omitted qualification, reordered events and insufficient evidence. Independently adjudicate the actual meaning before examining predictions. Prefer a genuine documented edit for realism, with appropriate rights, rather than adding more contrived NASA examples.
3. Compare the workflow with a fair plain-model prompt given the same available media. Measure time to the correct supporting passage and time to a reviewable decision, alongside material errors and abstentions. Keep retrieval quality, semantic judgment and UI speed separate.
4. Ask three people who actually edit or review clips to complete a small task without coaching. A favorable reaction is not enough; record whether they find and understand the consequential difference and whether the tool helps them decide what to do.

These are proposed product go/no-go criteria, not scientific accuracy claims: at least two of three target reviewers complete the task unaided and want to use it again; on the small predeclared comparison set the application materially reduces time to the evidence (target: roughly half the manual/chat workflow time) without introducing a material error the baseline avoids; all tested faithful edits avoid an unsupported accusation. Failures stay visible. If these conditions cannot be met by November 1 evening IST, stop further feature work and submit only an honestly scoped research prototype if the owner still chooses to enter.

## Schedule

- October 30–31: focused interface/brief, fair evaluation protocol and independent case review.
- November 1: user/workflow comparison and explicit continue/stop decision. Do not spend this period on new modules or model-provider switching.
- November 2–3: only if the gate is met, stabilize the scoped flow and synchronize demonstration, description and release revision.
- November 4: submission buffer. Official close is November 4, 9 PM ET / November 5, 7:30 AM IST.

## External context (documentation, not a competitive benchmark)

- [InVID verification toolkit](https://www.invid-project.eu/tools-and-services/invid-verification-plugin/) documents a journalist verification workflow including keyframes and reverse search. The user problem has existing tooling; we cannot claim an empty category.
- [Google video-understanding documentation](https://ai.google.dev/gemini-api/docs/video-understanding) documents audiovisual interpretation and timestamped questions. Generic video summaries and timestamped prose are not distinctive by themselves. No Gemini head-to-head test was run.
- [FactCheck.org: deceptively edited Biden video](https://www.factcheck.org/2020/08/biden-video-deceptively-edited-to-make-him-appear-lost/) illustrates selective cuts and removed context as an actual verification problem. It does not establish demand for this product.
- [Meta hackathon dates](https://dev.meta.ai/events/global-hackathon) list November 4, 9 PM ET as the submission deadline.

Bottom-line decision: the current broad product promise is not earned. Preserve the engineering and give the focused editorial workflow one short, measurable chance. Do not call it amazing or spend the remaining days expanding it without that evidence.
