"""Compare a learner clip with a learned process without seeing evaluation labels."""

from __future__ import annotations

import json
import math
from typing import Any

from .meta import MuseSparkClient


def observation_schema(process: dict[str, Any]) -> dict[str, Any]:
    state_ids = [item["id"] for item in process["states"]]
    object_ids = [item["id"] for item in process["objects"]]
    state_choices = [*state_ids, "unknown"]
    object_choices = [*object_ids, "unknown"]
    return {
        "type": "object",
        "properties": {
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "time_seconds": {"type": "number", "minimum": 0},
                        "action": {"type": "string"},
                        "state_id": {"type": "string", "enum": state_choices},
                        "assessment": {"type": "string", "enum": ["consistent", "divergent", "unclear"]},
                        "object_ids": {"type": "array", "items": {"type": "string", "enum": object_choices}},
                        "evidence": {"type": "string"},
                    },
                    "required": ["time_seconds", "action", "state_id", "assessment", "object_ids", "evidence"],
                    "additionalProperties": False,
                },
            },
            "divergences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "time_seconds": {"type": "number", "minimum": 0},
                        "process_difference": {"type": "string"},
                        "object_ids": {"type": "array", "items": {"type": "string", "enum": object_choices}},
                        "evidence": {"type": "string"},
                    },
                    "required": ["time_seconds", "process_difference", "object_ids", "evidence"],
                    "additionalProperties": False,
                },
            },
            "recovery_status": {
                "type": "string",
                "enum": ["no_divergence_observed", "underway", "recovered", "unclear"],
            },
            "uncertainties": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["events", "divergences", "recovery_status", "uncertainties"],
        "additionalProperties": False,
    }


def observation_prompt(process: dict[str, Any], duration_seconds: float) -> str:
    clean_process = {key: value for key, value in process.items() if not key.startswith("_")}
    return (
        "Compare this learner video with the process learned from an expert. "
        "The process is a hypothesis, and the learner clip may be correct, divergent, "
        "ambiguous, or recovered; do not assume which. Do not infer unseen events. "
        "The learned clip is only one observed trace: its ordering_observations describe "
        "what happened before what in that clip, not required prerequisites. Do not call "
        "a learner divergent only because they perform those actions in another order. "
        "Report divergence only when the visible learner state conflicts with a clearly "
        "described process state; treat uncertain dependencies as uncertainty. "
        "Return time-stamped visible events in chronological order. Mark a state 'unknown' "
        "when the video cannot support a match. Use only declared state/object IDs or "
        "'unknown'. Include evidence that a reviewer can locate in the clip. Do not "
        "claim recovery unless the clip visibly returns to a process-consistent state. "
        f"All times must be in [0, {duration_seconds:.3f}) seconds.\n\n"
        f"Learned process:\n{json.dumps(clean_process, ensure_ascii=False, sort_keys=True)}"
    )


def validate_observation(
    observation: dict[str, Any], process: dict[str, Any], duration_seconds: float,
) -> None:
    """Fail closed on invented process IDs, invalid timestamps, or unsupported recovery."""
    if not isinstance(observation, dict):
        raise ValueError("observation must be an object")
    state_ids = {item["id"] for item in process["states"]}
    object_ids = {item["id"] for item in process["objects"]}
    events = observation.get("events")
    divergences = observation.get("divergences")
    if not isinstance(events, list) or not isinstance(divergences, list):
        raise ValueError("observation events and divergences must be arrays")

    prior_time = -1.0
    for index, event in enumerate(events):
        timestamp = _valid_time(event, duration_seconds, f"event {index}")
        if timestamp < prior_time:
            raise ValueError("observation events must be chronological")
        prior_time = timestamp
        if event.get("state_id") != "unknown" and event.get("state_id") not in state_ids:
            raise ValueError(f"event {index} references an unknown state_id")
        if event.get("assessment") not in {"consistent", "divergent", "unclear"}:
            raise ValueError(f"event {index} has an invalid assessment")
        if not isinstance(event.get("evidence"), str) or not event["evidence"].strip():
            raise ValueError(f"event {index} needs inspectable evidence")
        _validate_objects(event.get("object_ids"), object_ids, f"event {index}")

    divergence_times: list[float] = []
    for index, divergence in enumerate(divergences):
        divergence_times.append(_valid_time(divergence, duration_seconds, f"divergence {index}"))
        if not isinstance(divergence.get("evidence"), str) or not divergence["evidence"].strip():
            raise ValueError(f"divergence {index} needs inspectable evidence")
        _validate_objects(divergence.get("object_ids"), object_ids, f"divergence {index}")

    status = observation.get("recovery_status")
    allowed_statuses = {"no_divergence_observed", "underway", "recovered", "unclear"}
    if status not in allowed_statuses:
        raise ValueError("observation has an invalid recovery_status")
    has_divergent_event = any(event.get("assessment") == "divergent" for event in events)
    if has_divergent_event and not divergence_times:
        raise ValueError("divergent events need at least one divergence record")
    if status == "no_divergence_observed" and (divergence_times or has_divergent_event):
        raise ValueError("recovery status conflicts with reported divergences")
    if status == "recovered":
        if not divergence_times:
            raise ValueError("recovery cannot be marked without a visible divergence")
        first_divergence = min(divergence_times)
        if not any(
            event.get("assessment") == "consistent"
            and event.get("state_id") in state_ids
            and event.get("time_seconds", -1) > first_divergence
            for event in events
        ):
            raise ValueError("recovery needs a later process-consistent event")


def snapshot_schema(process: dict[str, Any]) -> dict[str, Any]:
    """Constrain one camera-frame assessment to the reviewed process vocabulary."""
    state_ids = [item["id"] for item in process["states"]]
    object_ids = [item["id"] for item in process["objects"]]
    return {
        "type": "object",
        "properties": {
            "state_id": {"type": "string", "enum": [*state_ids, "unknown"]},
            "assessment": {"type": "string", "enum": ["consistent", "possible_divergence", "unclear"]},
            "object_ids": {"type": "array", "items": {"type": "string", "enum": [*object_ids, "unknown"]}},
            "evidence": {"type": "string"},
            "uncertainties": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["state_id", "assessment", "object_ids", "evidence", "uncertainties"],
        "additionalProperties": False,
    }


def snapshot_prompt(process: dict[str, Any]) -> str:
    clean_process = {key: value for key, value in process.items() if not key.startswith("_")}
    return (
        "Inspect this single still image from a learner's physical workspace against the reviewed process model. "
        "This is one snapshot, not a video: do not infer action order, what happened before, recovery, or intent. "
        "Use consistent only when visible facts match a declared process state. Use possible_divergence only "
        "when a visible relationship clearly conflicts with the described states; do not treat an unobserved "
        "action order as a violation. Use unclear when the relevant parts are occluded, too small, or ambiguous. "
        "Use only declared state/object IDs or unknown. Explain the visible evidence plainly, and list uncertainty. "
        f"\n\nReviewed process hypothesis:\n{json.dumps(clean_process, ensure_ascii=False, sort_keys=True)}"
    )


def validate_snapshot(snapshot: dict[str, Any], process: dict[str, Any]) -> None:
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot observation must be an object")
    state_ids = {item["id"] for item in process["states"]}
    object_ids = {item["id"] for item in process["objects"]}
    state_id = snapshot.get("state_id")
    assessment = snapshot.get("assessment")
    if state_id != "unknown" and state_id not in state_ids:
        raise ValueError("snapshot references an unknown state_id")
    if assessment not in {"consistent", "possible_divergence", "unclear"}:
        raise ValueError("snapshot has an invalid assessment")
    if assessment == "consistent" and state_id == "unknown":
        raise ValueError("a consistent snapshot must match a declared state")
    if not isinstance(snapshot.get("evidence"), str) or not snapshot["evidence"].strip():
        raise ValueError("snapshot needs inspectable evidence")
    _validate_objects(snapshot.get("object_ids"), object_ids, "snapshot")
    uncertainties = snapshot.get("uncertainties")
    if not isinstance(uncertainties, list) or not all(isinstance(item, str) for item in uncertainties):
        raise ValueError("snapshot uncertainties must be an array of strings")


def observe_snapshot(
    learner: MuseSparkClient,
    image_path: Any,
    process: dict[str, Any],
) -> dict[str, Any]:
    return learner.analyze_image(
        image_path,
        prompt=snapshot_prompt(process),
        schema=snapshot_schema(process),
        schema_name="showme_snapshot_observation",
        max_output_tokens=1000,
    )


def _valid_time(item: Any, duration: float, label: str) -> float:
    if not isinstance(item, dict):
        raise ValueError(f"{label} must be an object")
    timestamp = item.get("time_seconds")
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise ValueError(f"{label} time_seconds must be numeric")
    if not math.isfinite(timestamp) or not 0 <= timestamp < duration:
        raise ValueError(f"{label} time_seconds must be within the clip")
    return float(timestamp)


def _validate_objects(value: Any, object_ids: set[str], label: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} object_ids must be an array")
    for object_id in value:
        if object_id != "unknown" and object_id not in object_ids:
            raise ValueError(f"{label} references an unknown object_id")


def observe_video(
    learner: MuseSparkClient,
    video_path: Any,
    process: dict[str, Any],
    duration_seconds: float,
) -> dict[str, Any]:
    return learner.analyze_video(
        video_path,
        prompt=observation_prompt(process, duration_seconds),
        schema=observation_schema(process),
        schema_name="showme_learner_observation",
        max_output_tokens=2500,
    )
