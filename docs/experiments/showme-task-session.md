# Reconcile a physical task session

Implemented October 28. Deterministic local state projection; no additional inference.

## Endpoint

POST `/api/skills/reconcile-session` with JSON `{process, checks}`. `process` is reviewed backend process JSON. `checks` is at most 100 ordered explicit physical snapshot checks. An empty log returns the current semantic process fingerprint for association with future checks.

Each check has:

```json
{
  "id": "local-check-1",
  "sequence": 1,
  "source": "physical-snapshot",
  "process_sha256": "fingerprint returned for this process",
  "observation": {
    "state_id": "declared-state-id",
    "assessment": "consistent",
    "object_ids": ["declared-object-id"],
    "evidence": "Visible evidence from the snapshot result",
    "uncertainties": [],
    "view_guidance": ""
  }
}
```

Use actual validated snapshot output as observation. Do not create observations from simulation playback or button clicks. IDs must be unique, sequence must strictly increase, and every check must name the same semantic process revision. `_` run metadata is excluded from that fingerprint. The endpoint validates observation structure and model IDs; it is not an authenticity attestation of client-supplied history.

Response `{session}` includes current match, historical last match, last reported issue, unique next trace action when supported, branch ambiguity, and explicit unverified/not-assessed recovery and completion states. It never grants completion from a terminal appearance alone or infers recovery from an unrelated later match. A next trace action is modeled guidance, not proof that the order is required.

## Integration

This endpoint is optional and compatible with existing frontend checkpoint logic. Keep one client observation log as the source of truth rather than introducing a second mutable history. The server retains no session or media. Returning from Simulate should reuse the existing log, not append simulated events. A model revision requires a new log or explicit historical archive; stale observations cannot silently seed the new task.

Current state is the latest explicit check, not continuous camera knowledge. Between checks the physical scene can change. Render observation time in the UI and avoid claiming a live view is verified merely because a prior snapshot matched.

## Checks

93 SHOWME backend tests pass in the combined suite. Session tests exercise uncertainty/history separation, model-revision isolation, simulation rejection, ordered unique events, terminal-state limits, branches, replay determinism/nonmutation and HTTP handling. No paid request or new perception result was produced.
