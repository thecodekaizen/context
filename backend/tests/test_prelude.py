"""Tests for PRELUDE anticipatory roadway risk analysis.

Verifies:
1. Hard leak-proof pre-incident cutoff enforcement (future frames never enter).
2. Deterministic kinematic tracking & looming rate computation.
3. Offline replay on near-crash incident (early cue detection and positive lead time).
4. Safe control negative (no false alarms on normal driving).
5. Epistemic boundaries and disclaimers.
"""

import asyncio
from pathlib import Path
import pytest
import httpx

from context_core.prelude import (
    extract_pre_incident_frames,
    compute_actor_tracks,
    run_prelude_investigation,
    DISCLAIMER,
)

BENCHMARK_DIR = Path(__file__).resolve().parents[2] / "data/prelude_benchmark"


def test_leak_proof_cutoff_enforcement():
    """Verify that video extraction strictly honors t_cutoff and never decodes future frames."""
    video_path = BENCHMARK_DIR / "near_crash_007.mp4"
    if not video_path.exists():
        pytest.skip("Benchmark video near_crash_007.mp4 not present")

    t_cutoff = 3.5
    fps = 5
    frames, timestamps = extract_pre_incident_frames(video_path, t_cutoff=t_cutoff, fps=fps)

    assert len(frames) == len(timestamps)
    # Expected number of frames: at 5 fps for 3.5s is around 17-18 frames
    assert len(frames) <= int(t_cutoff * fps) + 1
    assert max(timestamps) <= t_cutoff
    # Verify exact frame dimensions
    assert frames.shape[1] == 360  # height
    assert frames.shape[2] == 640  # width
    assert frames.shape[3] == 3    # BGR channels


def test_leak_proof_cutoff_zero_or_negative_raises():
    video_path = BENCHMARK_DIR / "near_crash_007.mp4"
    if not video_path.exists():
        pytest.skip("Benchmark video not present")

    with pytest.raises(Exception):
        extract_pre_incident_frames(video_path, t_cutoff=0.0)


def test_kinematic_tracking_computes_tracks():
    """Verify that optical flow and tracking identify persistent actor motion."""
    video_path = BENCHMARK_DIR / "near_crash_007.mp4"
    if not video_path.exists():
        pytest.skip("Benchmark video not present")

    frames, timestamps = extract_pre_incident_frames(video_path, t_cutoff=4.0, fps=5)
    tracks, kinematics = compute_actor_tracks(frames, timestamps)

    assert "peak_lateral_flow" in kinematics
    assert "peak_looming_rate" in kinematics
    assert kinematics["peak_lateral_flow"] >= 0.0
    # On near_crash_007, entering vehicle produces non-zero lateral flow
    assert kinematics["peak_lateral_flow"] > 0.5


def test_prelude_mocked_model_schema():
    """Verify model response parsing and dossier construction with mocked transport."""
    video_path = BENCHMARK_DIR / "near_crash_007.mp4"
    if not video_path.exists():
        pytest.skip("Benchmark video not present")

    mock_response = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": (
                            '{\n'
                            '  "hazard_detected": true,\n'
                            '  "risk_level": "high",\n'
                            '  "risk_cue_seconds": 3.8,\n'
                            '  "hazard_actor": "silver pickup truck from right intersection",\n'
                            '  "conflict_type": "lateral_encroachment",\n'
                            '  "observations": ["At t=3.8s, silver pickup enters carriageway from right"],\n'
                            '  "uncertainty": "Offline monocular replay only."\n'
                            '}'
                        ),
                    }
                ],
            }
        ]
    }

    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=mock_response)
    )

    dossier = asyncio.run(
        run_prelude_investigation(
            video_path,
            t_cutoff=4.0,
            t_incident=4.5,
            use_model=True,
            transport=transport,
        )
    )

    assert dossier.hazard_detected is True
    assert dossier.risk_level == "high"
    assert dossier.finding.t_cue_seconds == 3.8
    assert dossier.t_incident == 4.5
    assert dossier.lead_time == 0.7  # 4.5 - 3.8 = 0.7s lead time
    assert dossier.disclaimer == DISCLAIMER
    assert len(dossier.timeline_events) >= 3


def test_prelude_safe_control_negative_mocked():
    """Verify that normal driving produces hazard_detected=False and low risk."""
    video_path = BENCHMARK_DIR / "normal_safe_004.mp4"
    if not video_path.exists():
        pytest.skip("Benchmark video normal_safe_004.mp4 not present")

    mock_response = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": (
                            '{\n'
                            '  "hazard_detected": false,\n'
                            '  "risk_level": "nominal",\n'
                            '  "risk_cue_seconds": null,\n'
                            '  "hazard_actor": null,\n'
                            '  "conflict_type": "nominal_flow",\n'
                            '  "observations": ["Steady forward driving with clear lane ahead"],\n'
                            '  "uncertainty": "No hazard detected prior to cutoff."\n'
                            '}'
                        ),
                    }
                ],
            }
        ]
    }

    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=mock_response)
    )

    dossier = asyncio.run(
        run_prelude_investigation(
            video_path,
            t_cutoff=3.0,
            t_incident=None,
            use_model=True,
            transport=transport,
        )
    )

    assert dossier.hazard_detected is False
    assert dossier.risk_level == "nominal"
    assert dossier.finding.t_cue_seconds is None
    assert dossier.lead_time is None
    assert "No imminent collision hazard detected" in dossier.finding.summary


def test_prelude_deterministic_kinematics_only():
    """Verify fallback when model is disabled or offline."""
    video_path = BENCHMARK_DIR / "near_crash_007.mp4"
    if not video_path.exists():
        pytest.skip("Benchmark video not present")

    dossier = asyncio.run(
        run_prelude_investigation(
            video_path,
            t_cutoff=3.5,
            t_incident=4.5,
            use_model=False,
        )
    )

    assert isinstance(dossier.hazard_detected, bool)
    assert dossier.t_cutoff == 3.5
    assert dossier.duration > 7.0
    assert len(dossier.timeline_events) > 0
    assert "Offline research/replay only" in dossier.disclaimer
