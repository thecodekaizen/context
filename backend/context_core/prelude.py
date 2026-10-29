"""PRELUDE: Anticipatory roadway hazard analysis strictly prior to incidents.

Offline research/replay only. Monocular pixel trajectories and optical flow
do not represent metric physical ground truth. Not for real-time driving safety.
"""

import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import cv2
import httpx
import numpy as np
from pydantic import BaseModel, Field

from .media import probe

MODEL = "muse-spark-1.2"
DISCLAIMER = (
    "Offline research/replay only. Monocular pixel trajectories do not represent "
    "metric physical ground truth. Not for real-time driving safety or collision prevention."
)


class TrajectoryPoint(BaseModel):
    time: float
    box: list[float] = Field(description="[ymin, xmin, ymax, xmax] normalized to [0, 1]")
    velocity: list[float] = Field(description="[vx, vy] normalized frame velocity per second")
    area: float = Field(description="Normalized bounding box area")


class ActorTrack(BaseModel):
    track_id: str
    label: str
    trajectory: list[TrajectoryPoint]
    is_hazard: bool = False
    looming_rate: float = 0.0
    lateral_crossing_velocity: float = 0.0


class PreludeFinding(BaseModel):
    hazard_detected: bool
    risk_level: str = Field(description="'nominal' | 'low' | 'medium' | 'high' | 'critical'")
    t_cue_seconds: float | None = None
    t_incident_seconds: float | None = None
    lead_time_seconds: float | None = None
    conflict_type: str
    summary: str
    hazard_actor: str | None = None
    kinematic_signals: dict[str, Any] = Field(default_factory=dict)
    observations: list[str] = Field(default_factory=list)
    uncertainty: str
    disclaimer: str = DISCLAIMER


class PreludeDossier(BaseModel):
    video_id: str
    video_path: str
    duration: float
    t_cutoff: float
    t_incident: float | None = None
    lead_time: float | None = None
    hazard_detected: bool
    risk_level: str
    finding: PreludeFinding
    actors: list[ActorTrack]
    timeline_events: list[dict[str, Any]]
    disclaimer: str = DISCLAIMER


def extract_pre_incident_frames(
    video_path: Path | str,
    t_cutoff: float,
    fps: int = 5,
    width: int = 640,
    height: int = 360,
) -> tuple[np.ndarray, list[float]]:
    """Strictly slice and decode video frames up to t_cutoff.

    Hard leak-proof cutoff: frames with t > t_cutoff NEVER reach downstream processing.
    """
    video_path = Path(video_path).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Use FFmpeg to decode raw frames strictly bounded by -t t_cutoff
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-i",
        str(video_path),
        "-t",
        f"{t_cutoff:.3f}",
        "-an",
        "-vf",
        f"fps={fps},scale={width}:{height}",
        "-pix_fmt",
        "bgr24",
        "-f",
        "rawvideo",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    raw = proc.stdout
    frame_size = width * height * 3
    num_frames = len(raw) // frame_size
    if num_frames == 0:
        raise ValueError(f"No decodable frames found prior to t_cutoff={t_cutoff}")

    frames = np.frombuffer(raw, dtype=np.uint8).reshape((num_frames, height, width, 3))
    timestamps = [round(i / fps, 3) for i in range(num_frames)]
    return frames, timestamps


def compute_actor_tracks(
    frames: np.ndarray,
    timestamps: list[float],
    width: int = 640,
    height: int = 360,
) -> tuple[list[ActorTrack], dict[str, Any]]:
    """Compute 2D kinematic tracks, optical flow vectors, and looming expansion rates."""
    num_frames = len(frames)
    if num_frames < 2:
        return [], {"peak_lateral_flow": 0.0, "peak_looming": 0.0}

    # Region of Interest: ignore top 25% (sky) and bottom 15% (ego hood)
    roi_top = int(height * 0.25)
    roi_bottom = int(height * 0.85)

    tracks: list[ActorTrack] = []
    lateral_flows: list[float] = []
    looming_rates: list[float] = []

    # Focus of expansion (FOE) estimate: center of road vanishing point
    foe_x, foe_y = width // 2, int(height * 0.45)

    prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    active_boxes: list[dict[str, Any]] = []

    for idx in range(1, num_frames):
        t = timestamps[idx]
        dt = t - timestamps[idx - 1] if idx > 0 else 0.2
        if dt <= 0:
            dt = 0.2

        curr_gray = cv2.cvtColor(frames[idx], cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )

        # Lateral flow anomaly: motion across radial expansion rays from FOE
        y_coords, x_coords = np.mgrid[roi_top:roi_bottom, 0:width]
        dx = x_coords - foe_x
        dy = y_coords - foe_y
        dist = np.hypot(dx, dy) + 1e-5
        rx = dx / dist
        ry = dy / dist

        roi_u = flow[roi_top:roi_bottom, :, 0]
        roi_v = flow[roi_top:roi_bottom, :, 1]

        # Cross product of velocity with radial unit vector = perpendicular/lateral flow
        perp_flow = np.abs(roi_u * ry - roi_v * rx)
        peak_lateral = float(np.percentile(perp_flow, 98))
        lateral_flows.append(peak_lateral)

        # Detect moving foreground regions
        diff = cv2.absdiff(curr_gray, prev_gray)
        _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
        thresh[:roi_top, :] = 0
        thresh[roi_bottom:, :] = 0

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        frame_boxes = []

        for c in contours:
            area = cv2.contourArea(c)
            if area > 450:  # significant actor size
                x, y, w, h = cv2.boundingRect(c)
                # normalized box [ymin, xmin, ymax, xmax]
                norm_box = [round(y / height, 4), round(x / width, 4), round((y + h) / height, 4), round((x + w) / width, 4)]
                norm_area = round((w * h) / (width * height), 5)

                # Mean flow inside box
                box_u = float(np.mean(flow[y:y+h, x:x+w, 0])) / width
                box_v = float(np.mean(flow[y:y+h, x:x+w, 1])) / height
                vel = [round(box_u / dt, 4), round(box_v / dt, 4)]

                frame_boxes.append({
                    "time": t,
                    "box": norm_box,
                    "velocity": vel,
                    "area": norm_area,
                    "cx": (x + w / 2) / width,
                    "cy": (y + h / 2) / height,
                })

        active_boxes.append({"time": t, "boxes": frame_boxes})
        prev_gray = curr_gray

    # Correlate bounding boxes across consecutive frames into coherent actor tracks
    track_counter = 1
    current_tracks: dict[int, list[dict[str, Any]]] = {}

    for fb in active_boxes:
        t = fb["time"]
        for box in fb["boxes"]:
            matched = False
            for tid, history in current_tracks.items():
                last_pt = history[-1]
                # Distance threshold for track continuity
                dist = np.hypot(box["cx"] - last_pt["cx"], box["cy"] - last_pt["cy"])
                if dist < 0.12 and abs(t - last_pt["time"]) <= 0.45:
                    history.append(box)
                    matched = True
                    break
            if not matched:
                current_tracks[track_counter] = [box]
                track_counter += 1

    # Filter significant tracks (persisting for >= 3 frames)
    for tid, history in current_tracks.items():
        if len(history) >= 3:
            traj_pts = [
                TrajectoryPoint(
                    time=pt["time"],
                    box=pt["box"],
                    velocity=pt["velocity"],
                    area=pt["area"],
                )
                for pt in history
            ]

            # Compute looming expansion rate: (A_final - A_init) / (A_init * dt)
            a_init = history[0]["area"]
            a_final = history[-1]["area"]
            total_dt = history[-1]["time"] - history[0]["time"]
            looming = float((a_final - a_init) / (a_init * total_dt)) if a_init > 0 and total_dt > 0 else 0.0
            looming_rates.append(looming)

            # Lateral crossing velocity (absolute horizontal motion toward center)
            lat_v = float(np.mean([abs(pt["velocity"][0]) for pt in history]))

            is_hz = (looming > 1.2 or lat_v > 0.15) and any(
                0.2 < pt["cx"] < 0.8 for pt in history
            )

            tracks.append(
                ActorTrack(
                    track_id=f"actor_{tid}",
                    label="crossing_vehicle" if lat_v > 0.12 else "vehicle",
                    trajectory=traj_pts,
                    is_hazard=is_hz,
                    looming_rate=round(looming, 3),
                    lateral_crossing_velocity=round(lat_v, 3),
                )
            )

    kinematics_summary = {
        "peak_lateral_flow": round(float(np.max(lateral_flows)) if lateral_flows else 0.0, 3),
        "mean_lateral_flow": round(float(np.mean(lateral_flows)) if lateral_flows else 0.0, 3),
        "peak_looming_rate": round(float(np.max(looming_rates)) if looming_rates else 0.0, 3),
        "active_tracks_count": len(tracks),
    }

    return tracks, kinematics_summary


async def analyze_pre_incident_with_meta(
    frames: np.ndarray,
    timestamps: list[float],
    t_cutoff: float,
    kinematics: dict[str, Any],
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    """Pass sampled pre-incident frames to Meta muse-spark-1.2 with kinematic context."""
    key = os.getenv("MODEL_API_KEY")
    if not key and transport is not None:
        key = "mock-key"
    if not key:
        return {
            "hazard_detected": False,
            "risk_level": "unverified",
            "risk_cue_seconds": None,
            "hazard_actor": None,
            "conflict_type": "api_key_not_configured",
            "observations": ["Meta API key not configured; relying strictly on deterministic kinematics."],
            "uncertainty": "Model verification omitted due to missing API key.",
        }

    # Select representative keyframes across the pre-incident window
    # Ensure dense sampling in the critical final 1.5s leading up to cutoff
    num_frames = len(frames)
    if num_frames <= 10:
        sample_indices = list(range(num_frames))
    else:
        # Sample earlier window sparsely, last 1.5s densely
        cutoff_t = timestamps[-1]
        dense_start_t = max(0.0, cutoff_t - 1.5)
        early_indices = [i for i, t in enumerate(timestamps) if t < dense_start_t]
        dense_indices = [i for i, t in enumerate(timestamps) if t >= dense_start_t]

        step_early = max(1, len(early_indices) // 3)
        selected_early = early_indices[::step_early][:3]

        step_dense = max(1, len(dense_indices) // 6)
        selected_dense = dense_indices[::step_dense]
        if (num_frames - 1) not in selected_dense:
            selected_dense.append(num_frames - 1)

        sample_indices = sorted(set(selected_early + selected_dense))

    content: list[dict[str, Any]] = [
        {
            "type": "input_text",
            "text": (
                f"You are an offline roadway safety research assistant analyzing a dashcam recording. "
                f"These frames are strictly bounded evidence prior to any potential incident, ending at t={t_cutoff:.2f}s. "
                f"Frames after t={t_cutoff:.2f}s are deliberately withheld to evaluate early anticipation. "
                f"Deterministic kinematic telemetry: peak_lateral_flow={kinematics.get('peak_lateral_flow', 0)}, "
                f"peak_looming={kinematics.get('peak_looming_rate', 0)}. "
                "Task: Examine the vehicle paths, intersection geometry, and traffic flow prior to cutoff. "
                "CRITICAL DISTINCTION: "
                "1. Vehicles traveling in adjacent lanes on multi-lane roads, passing in their own lane, parked roadside cars, or stopped vehicles waiting at give-way lines are NOMINAL FLOW (hazard_detected=false, risk_level='nominal'). "
                "2. Only flag hazard_detected=true if an actor actively enters or crosses into the ego travel lane, fails to give way at an intersection, or poses an imminent trajectory collision conflict. "
                "Return ONLY valid JSON matching this schema:\n"
                "{\n"
                '  "hazard_detected": true/false,\n'
                '  "risk_level": "nominal" | "low" | "medium" | "high" | "critical",\n'
                '  "risk_cue_seconds": 3.8 or null,\n'
                '  "hazard_actor": "brief description of actor or null",\n'
                '  "conflict_type": "lateral_encroachment" | "failure_to_yield" | "nominal_flow" | "approaching_obstacle",\n'
                '  "observations": ["At t=X.Xs, description of observed actor action"],\n'
                '  "uncertainty": "limitations and disclaimer"\n'
                "}"
            ),
        }
    ]

    for s_idx in sample_indices:
        t = timestamps[s_idx]
        frame = frames[s_idx]
        # Encode JPEG
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
        content.append({"type": "input_text", "text": f"Pre-incident frame at t={t:.2f}s:"})
        content.append({"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"})

    async with httpx.AsyncClient(timeout=90, transport=transport) as client:
        response = await client.post(
            "https://api.meta.ai/v1/responses",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": MODEL,
                "input": [{"type": "message", "role": "user", "content": content}],
            },
        )
        response.raise_for_status()
        payload = response.json()

    text = "".join(
        c.get("text", "")
        for item in payload.get("output", [])
        if item.get("type") == "message"
        for c in item.get("content", [])
        if c.get("type") == "output_text"
    )

    try:
        # Extract json block if surrounded by markdown fences
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1]
            if clean.endswith("```"):
                clean = clean.rsplit("```", 1)[0]
        data = json.loads(clean.strip())
        return data
    except (json.JSONDecodeError, ValueError, KeyError):
        return {
            "hazard_detected": False,
            "risk_level": "unverified",
            "risk_cue_seconds": None,
            "hazard_actor": None,
            "conflict_type": "parse_fallback",
            "observations": [text[:500]],
            "uncertainty": "Failed to parse structured model response.",
        }


async def run_prelude_investigation(
    video_path: Path | str,
    t_cutoff: float | None = None,
    t_incident: float | None = None,
    use_model: bool = True,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> PreludeDossier:
    """Run full PRELUDE anticipatory analysis with hard leak-proof cutoff."""
    path = Path(video_path).resolve()
    info = probe(path)
    total_duration = info["duration"]

    # If t_cutoff not explicitly provided:
    # If t_incident is provided, default t_cutoff to max(0.5, t_incident - 0.5)
    # Otherwise analyze up to full duration
    if t_cutoff is None:
        if t_incident is not None:
            t_cutoff = max(0.5, round(t_incident - 0.5, 2))
        else:
            t_cutoff = total_duration

    # Strictly enforce bounds
    t_cutoff = min(total_duration, max(0.2, t_cutoff))

    # Hard leak-proof frame extraction (strictly <= t_cutoff)
    frames, timestamps = extract_pre_incident_frames(path, t_cutoff, fps=5)

    # 1. Deterministic kinematic tracking & optical flow
    tracks, kinematics = compute_actor_tracks(frames, timestamps)

    # 2. Multimodal scene understanding with Meta muse-spark-1.2
    if use_model:
        model_result = await analyze_pre_incident_with_meta(
            frames, timestamps, t_cutoff, kinematics, transport=transport
        )
    else:
        # Deterministic kinematic-only fallback
        has_hz_track = any(tr.is_hazard for tr in tracks)
        model_result = {
            "hazard_detected": has_hz_track or kinematics.get("peak_lateral_flow", 0) > 3.0,
            "risk_level": "high" if has_hz_track else "low",
            "risk_cue_seconds": t_cutoff if has_hz_track else None,
            "hazard_actor": "kinematic_crossing_actor" if has_hz_track else None,
            "conflict_type": "lateral_crossing" if has_hz_track else "nominal_flow",
            "observations": [
                f"Kinematics detected {len(tracks)} persistent tracks; peak lateral flow = {kinematics.get('peak_lateral_flow', 0):.2f}"
            ],
            "uncertainty": "Offline kinematic heuristic without model inference.",
        }

    hazard_detected = bool(model_result.get("hazard_detected", False))
    risk_level = model_result.get("risk_level", "low" if not hazard_detected else "high")
    t_cue = model_result.get("risk_cue_seconds")
    if t_cue is not None:
        t_cue = round(float(t_cue), 2)

    lead_time = None
    if hazard_detected and t_cue is not None and t_incident is not None:
        lead_time = round(max(0.0, t_incident - t_cue), 2)

    finding = PreludeFinding(
        hazard_detected=hazard_detected,
        risk_level=risk_level,
        t_cue_seconds=t_cue,
        t_incident_seconds=t_incident,
        lead_time_seconds=lead_time,
        conflict_type=model_result.get("conflict_type", "nominal_flow"),
        summary=(
            f"Pre-incident hazard detected at t={t_cue}s ({lead_time}s lead time before incident at t={t_incident}s)."
            if hazard_detected and lead_time is not None
            else (
                f"Early hazard cue identified at t={t_cue}s prior to cutoff t={t_cutoff}s."
                if hazard_detected
                else f"No imminent collision hazard detected prior to cutoff t={t_cutoff}s; traffic dynamics nominal."
            )
        ),
        hazard_actor=model_result.get("hazard_actor"),
        kinematic_signals=kinematics,
        observations=model_result.get("observations", []),
        uncertainty=model_result.get("uncertainty", "Monocular camera lacks metric ground truth."),
    )

    # Timeline events
    timeline_events = [
        {
            "time": 0.0,
            "kind": "intake",
            "label": "Dashcam Ingestion",
            "detail": f"Duration {total_duration:.1f}s, bounded cutoff at t={t_cutoff:.1f}s",
        }
    ]

    for tr in tracks:
        timeline_events.append({
            "time": tr.trajectory[0].time,
            "kind": "actor_track",
            "label": f"Track: {tr.track_id} ({tr.label})",
            "detail": f"Looming rate: {tr.looming_rate}, lateral velocity: {tr.lateral_crossing_velocity}",
            "is_hazard": tr.is_hazard,
        })

    if hazard_detected and t_cue is not None:
        timeline_events.append({
            "time": t_cue,
            "kind": "early_warning",
            "label": "Early Hazard Cue Flagged",
            "detail": f"Conflict type: {finding.conflict_type} ({finding.hazard_actor})",
            "risk_level": risk_level,
        })

    if t_incident is not None:
        timeline_events.append({
            "time": t_incident,
            "kind": "incident_ground_truth",
            "label": "Ground Truth Incident Moment",
            "detail": f"Replay outcome verification; occurred {lead_time}s after early cue",
        })

    dossier_id = hashlib.sha256(f"{path.name}_{t_cutoff}".encode()).hexdigest()[:16]

    return PreludeDossier(
        video_id=f"prelude_{dossier_id}",
        video_path=str(path),
        duration=total_duration,
        t_cutoff=t_cutoff,
        t_incident=t_incident,
        lead_time=lead_time,
        hazard_detected=hazard_detected,
        risk_level=risk_level,
        finding=finding,
        actors=tracks,
        timeline_events=timeline_events,
    )
