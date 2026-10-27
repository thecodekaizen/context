# Inspect original-resolution evidence locally

Use `python -m showme inspect-frames VIDEO --times 3 11 15 17.5 23 29 --output NEW_PRIVATE_DIRECTORY` with `PYTHONPATH=backend` and the backend Python environment. This command never calls a provider. Prefer an ignored `.showme-runs/` output directory.

It preserves selected source-resolution PNG frames and hashes, source identity and requested seek times. Requested seek time is not claimed to be the exact encoded frame presentation timestamp. Existing outputs are never overwritten; decode failures remove only the newly created packet. No expected answer or correctness label is generated.

## October 28 inspection

Extracted six frames from original IMG_7670.MOV to the private source-comparison run. Examined the 11-second and 23-second frames alongside the previously saved contact sheet and official step 17/18 diagram crop. Wing hinge/connector surfaces are visible in portions of the sequence, but hands obscure relevant attachment contact during reattachment. This inspection does not independently establish a held wrong-facing attachment or a verified correction. No new media upload was made.

## Engineering purpose

Whole-video summaries can merge distinct geometric states. Preserve source frames first, then compare specific visible landmarks with the source diagram, recording uncertain relationships rather than substituting a coarse assembled-state label. Selected evidence times are inspection choices, not independent benchmark labels. Keep annotations separate from inference input.

Five controlled local tests cover invalid timestamps, source-time bounds, stable packet hashes, overwrite protection and partial-output cleanup. Full SHOWME backend suite: 71 checks passed. These are software checks, not perception accuracy results.
