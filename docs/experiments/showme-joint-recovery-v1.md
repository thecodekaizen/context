# Compare before/after evidence of the same joint

October 28 implementation. No live provider run for this path yet.

## Contract for Antigravity

Explicit multipart POST `/api/skills/compare-recovery`:

- `reference_image`, `before_image`, `after_image`: selected JPEG/PNG files, each at most 5 MiB.
- `process_json`: reviewed backend process JSON.
- `transition_id`: selected declared transition.
- `before_seconds`, `after_seconds`: finite nonnegative observation times from the same task timeline; after must be later. These are caller-supplied chronology, not verified capture metadata.

The three images and selected process context are sent to Meta only on this explicit action. Disclose the upload and credit use. The backend keeps no media after the request. Provider retention is separate.

Returns `{status, comparison}`. Status is derived locally from the provider's structured relationship observations:

| Status | Required observation pattern |
| --- | --- |
| recovery_reported | At least one prior visible difference; all compared relationships later match; same joint identity and adequate visibility |
| current_difference_reported | At least one visible later difference remains |
| no_prior_difference_reported | Compared relationships match before and after; no demonstrated recovery |
| unclear | Missing/ambiguous relationship evidence or uncertain same-joint identity |

Each relation includes affected IDs, contact/facing category, independent source/before/after evidence and visibility, before/after assessments and same-joint identity. Grouped wing IDs do not establish that the same physical wing was compared. Unknown identity prevents a recovery report. Other unexamined joints remain outside scope.

The deterministic guard does not independently verify pixels or guarantee that the model identified the same physical joint correctly. It prevents inconsistent claims from being accepted as recovery. Call the result reported recovery, not proven task completion. Client timestamps cannot prove physical changes between stills.

## Integration rules

Keep these results separate from simulated recovery. Preserve actual observation history; do not promote this result into a general camera checkpoint or mark skipped steps complete. Display both frames and evidence for review. Do not compare unrelated photos or assign invented before/after timestamps to an unchanged photo set. The five IMG_7671–7675 photos were confirmed unchanged and are a no-change control, not a recovery sequence.

## Verification

112 combined backend checks pass. Added cases cover same-joint identity, still-unfixed relationships, unchanged matching views, hidden contacts, unknown objects, unsupported silhouette-only evidence, missing evidence, invalid chronology, identical images, ordered three-image provider input and HTTP response behavior. No paid calls were made for this implementation. Existing video frames may supply chronological evidence for a future explicitly approved run; success is not assumed.
