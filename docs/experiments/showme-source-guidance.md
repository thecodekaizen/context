# Derive source-linked guidance

October 28. Optional local JSON POST `/api/skills/guidance` takes `{process, report, report_kind}`. Report kind is `joint-inspection` or `joint-recovery`; supply a current version validated backend report, not simulated results. The report must name the selected transition and canonical process fingerprint. Previous model revisions cannot silently guide the active model.

Returns `{guidance}` with a bounded decision: continue_observing, request_view, review_difference or review_reported_recovery. Response includes affected objects, modeled action, target state facts, video/PDF citations and reported relationship evidence. This endpoint makes no paid call or media upload.

A modeled action is a source-linked reference, not a proven undo/repair operation. `repair_steps` is empty and `repair_status` remains not_established because a single demonstration and a difference report do not establish a safe recovery procedure. Do not render a “fix now” instruction from the modeled action. Request better evidence or open the cited step when a specific repair has not been learned/confirmed.

Recovery status is rederived from same-joint relationship evidence. A stale or tampered status is rejected. A reported match does not certify task completion. Client-supplied report metadata is consistency/provenance context, not authentication or independent pixel verification.

The inspection process fingerprint now uses the same canonical algorithm as task sessions and recovery comparisons; older historical report fingerprints may differ and should not be silently migrated into active guidance.

121 local backend tests pass. No new visual accuracy or physical repair result follows from these controlled software checks. Antigravity can integrate this response in the existing evidence panel without introducing another mutable task history.
