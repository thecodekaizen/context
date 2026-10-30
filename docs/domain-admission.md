# Content admission

CONTEXT's application boundary admits developer tutorials, software benchmarks and commercial product demos. Politics, elections, news, wartime footage and real public figures are excluded, even when another allowed category also applies.

This is **review-based admission, not an automatic video-content classifier**. Selecting a category, renaming an upload, supplying a caption, or hosting it on an allowed domain cannot approve footage. Admission and deterministic omission grounding are independent requirements.

## Trusted evidence

1. Controlled execution-v1 fixtures are recognized by exact SHA-256, from a manifest whose expected hash is pinned in the policy module. Changed fixture bytes or a changed manifest do not silently gain admission.
2. Other files need a server-local operator review of the complete footage, including soundtrack, visible text, peripheral content and public figures. Each receipt binds one exact SHA-256 to a category, all five exclusion checks, reviewer, rationale, review time and policy version. Both source and edit require their own admission; editing an approved source does not automatically approve the edit.

Local reviews live in ignored `data/domain-reviews/`. This directory is an operator trust boundary: anyone who can modify the server's local files can modify its review records. Receipts are not cryptographically signed, authenticated identity proofs, or independent evidence that the operator classified the footage correctly. There is no HTTP self-approval endpoint.

## Record an actual operator review

After inspecting the **entire** file, the named operator can record a decision:

```sh
.venv/bin/python scripts/review_content.py /absolute/path/tutorial.mp4 \
  --category developer_tutorial \
  --reviewer 'Actual reviewer name' \
  --rationale 'Describe the reviewed content and the basis for admitting it' \
  --reviewed-entire-file
```

Categories: `developer_tutorial`, `software_benchmark`, `product_demo`, `other`, `unknown`. To record exclusions, add one or more `--excluded politics`, `--excluded elections`, `--excluded news`, `--excluded wartime`, or `--excluded real_public_figures`. Exclusions override an otherwise allowed category. `unknown` and incomplete exclusion checks remain unresolved.

Review the source and published edit separately, then retry the upload. Byte changes, including re-encoding, require a new review. Use `--replace` only to intentionally revise a receipt for identical bytes; the prior receipt is preserved in `history/`. The agent must not fabricate an operator's review or identity.

## Enforced boundaries

- `/api/analyze`: both files before alignment or crop analysis.
- `/api/library`: before feature extraction/indexing.
- `/api/library/search`: query and each candidate source; unadmitted legacy sources are excluded from matching.
- `/api/dossiers`: submitted video before background scheduling, supplied reference before indexing; URL inputs may be downloaded for hashing but are not analyzed before admission.
- Direct single-video investigation and attached source comparison recheck admission as well.
- Newly acquired source candidates cannot be indexed or compared without admission. The active source path now uses the reviewed technical catalog; see `docs/source-discovery.md`.
- Semantic interpretation rechecks admission, including before returning a cached review. Saved evidence can still be read as historical evidence; reading it does not confer admission for new processing.
- The deferred roadway analysis POST refuses requests. Its saved samples and historical records remain readable.

Unknown/malformed/missing reviews return HTTP 422 with a readable `detail` and structured `domain_admission` decisions. Explicit exclusions return HTTP 403. Rejected uploads are removed and processing locks are released. No category form field can bypass this gate. `GET /api/domain-policy` exposes the current contract without changing it.

## Validation limits and next step

Tests prove policy precedence, byte binding, rejection ordering, lock cleanup and refusal to call analysis/model work. They do not prove automatic content classification: none is implemented. Existing technical regression tests use clearly marked simulated operator receipts for synthetic fixtures; those receipts are isolated in pytest temporary directories.

The external hyperfine demo evaluation and its actual failure result are recorded in `docs/source-discovery.md`. Independent semantic assessment and useful omission recall on natural technical footage remain unvalidated. Admission alone does not validate a match, changed meaning, disclaimer segmentation or deceptive intent.
