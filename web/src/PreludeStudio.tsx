import React, { useEffect, useRef, useState } from "react";
import type { PreludeDossier, PreludeSample } from "./types";

interface PreludeStudioProps {
  onBackToContext: () => void;
}

export function PreludeStudio({ onBackToContext }: PreludeStudioProps) {
  const [samples, setSamples] = useState<PreludeSample[]>([]);
  const [selectedSample, setSelectedSample] = useState<string>("near_crash_011");
  const [dossier, setDossier] = useState<PreludeDossier | null>(null);
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [userCutoff, setUserCutoff] = useState<number | "">("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Fetch available samples
  useEffect(() => {
    fetch("/api/prelude/samples")
      .then((r) => r.json())
      .then((data: PreludeSample[]) => {
        setSamples(data);
        if (data.length > 0) {
          loadSample(data[0].id);
        }
      })
      .catch((err) => {
        setError(`Failed to load dashcam samples: ${err.message}`);
      });
  }, []);

  const loadSample = async (sampleId: string, customCutoff?: number) => {
    setSelectedSample(sampleId);
    setUploadFile(null);
    setBusy(true);
    setError("");
    try {
      let url = `/api/prelude/investigate?sample_id=${encodeURIComponent(sampleId)}`;
      if (customCutoff !== undefined) {
        url += `&t_cutoff=${customCutoff}`;
      }
      const res = await fetch(url, { method: "POST" });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned ${res.status}`);
      }
      const data: PreludeDossier = await res.json();
      setDossier(data);
      setUserCutoff(data.t_cutoff);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  const handleCustomUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setBusy(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("video", uploadFile);
      let url = "/api/prelude/investigate";
      if (typeof userCutoff === "number") {
        url += `?t_cutoff=${userCutoff}`;
      }
      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned ${res.status}`);
      }
      const data: PreludeDossier = await res.json();
      setDossier(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  // Synchronize canvas bounding boxes with video currentTime
  useEffect(() => {
    if (!canvasRef.current || !videoRef.current || !dossier) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Find active actors at currentTime
    const t = currentTime;
    for (const actor of dossier.actors) {
      const pt = actor.trajectory.find(
        (p) => Math.abs(p.time - t) < 0.25
      );
      if (pt) {
        const [ymin, xmin, ymax, xmax] = pt.box;
        const x = xmin * canvas.width;
        const y = ymin * canvas.height;
        const w = (xmax - xmin) * canvas.width;
        const h = (ymax - ymin) * canvas.height;

        const isHazard = actor.is_hazard;
        ctx.strokeStyle = isHazard ? "#f43f5e" : "#06b6d4";
        ctx.lineWidth = isHazard ? 3 : 1.5;
        ctx.strokeRect(x, y, w, h);

        // Fill subtle translucent box
        ctx.fillStyle = isHazard ? "rgba(244, 63, 94, 0.15)" : "rgba(6, 182, 212, 0.1)";
        ctx.fillRect(x, y, w, h);

        // Velocity arrow
        const [vx, vy] = pt.velocity;
        ctx.beginPath();
        ctx.moveTo(x + w / 2, y + h / 2);
        ctx.lineTo(x + w / 2 + vx * canvas.width * 0.4, y + h / 2 + vy * canvas.height * 0.4);
        ctx.strokeStyle = isHazard ? "#fb7185" : "#38bdf8";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = isHazard ? "#f43f5e" : "#06b6d4";
        ctx.font = "bold 11px sans-serif";
        ctx.fillText(
          `${actor.track_id} ${isHazard ? "[HAZARD CUE]" : ""}`,
          x,
          Math.max(12, y - 4)
        );
      }
    }
  }, [currentTime, dossier]);

  const riskBadgeClass = (level: string) => {
    switch (level.toLowerCase()) {
      case "critical":
      case "high":
        return "badge-critical";
      case "medium":
        return "badge-medium";
      default:
        return "badge-nominal";
    }
  };

  return (
    <div className="prelude-studio">
      <header className="prelude-header">
        <div className="prelude-header-left">
          <button className="prelude-back-btn" onClick={onBackToContext}>
            ← Back to CONTEXT Studio
          </button>
          <div className="prelude-lens-tag">LENS: PRELUDE</div>
          <h1 className="prelude-title">Anticipatory Roadway Hazard Intelligence</h1>
        </div>
        <div className="prelude-disclaimer-pill">
          Offline Replay Only • Not Real-Time Safety Assistance
        </div>
      </header>

      {/* Benchmark Sample Selector */}
      <section className="prelude-samples-bar">
        <span className="samples-bar-label">Ground-Truth Dashcam Scenarios:</span>
        <div className="samples-chips">
          {samples.map((s) => (
            <button
              key={s.id}
              className={`sample-chip ${selectedSample === s.id && !uploadFile ? "active" : ""}`}
              onClick={() => loadSample(s.id)}
              disabled={busy}
            >
              <span className={`chip-dot ${s.expected_hazard ? "hazard" : "safe"}`} />
              {s.title}
            </button>
          ))}
        </div>
      </section>

      {error && <div className="prelude-error-banner">{error}</div>}

      <div className="prelude-main-layout">
        {/* Left: Video Player with Overlays */}
        <div className="prelude-player-column">
          <div className="prelude-canvas-container">
            <video
              ref={videoRef}
              src={dossier?.media_url}
              controls
              onTimeUpdate={() => {
                if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
              }}
              className="prelude-video"
            />
            <canvas
              ref={canvasRef}
              width={640}
              height={360}
              className="prelude-overlay-canvas"
            />
            {dossier?.hazard_detected && currentTime >= (dossier.finding.t_cue_seconds || 0) && (
              <div className="prelude-hazard-hud">
                ⚠️ EARLY RISK CUE DETECTED ({dossier.finding.conflict_type})
              </div>
            )}
          </div>

          {/* Timeline and Cutoff Explorer */}
          {dossier && (
            <div className="prelude-timeline-card">
              <div className="timeline-header">
                <span className="timeline-title">Temporal Analysis & Hard Cutoff Horizon</span>
                <span className="timeline-status">
                  Current: {currentTime.toFixed(2)}s / Cutoff: {dossier.t_cutoff.toFixed(2)}s / Total: {dossier.duration.toFixed(2)}s
                </span>
              </div>

              <div className="prelude-timeline-track">
                {/* Pre-incident analysis window */}
                <div
                  className="timeline-window pre-incident"
                  style={{ width: `${(dossier.t_cutoff / dossier.duration) * 100}%` }}
                  title="Frames strictly analyzed prior to cutoff"
                >
                  <span className="window-label">Analyzed Horizon (t ≤ {dossier.t_cutoff}s)</span>
                </div>

                {/* Withheld future window */}
                <div
                  className="timeline-window withheld"
                  style={{ width: `${((dossier.duration - dossier.t_cutoff) / dossier.duration) * 100}%` }}
                  title="Future frames deliberately withheld from model"
                >
                  <span className="window-label">Withheld During Inference</span>
                </div>

                {/* Marker for Early Hazard Cue */}
                {dossier.finding.t_cue_seconds && (
                  <div
                    className="timeline-marker cue-marker"
                    style={{ left: `${(dossier.finding.t_cue_seconds / dossier.duration) * 100}%` }}
                    title={`Early Warning Flagged at t=${dossier.finding.t_cue_seconds}s`}
                  >
                    <div className="marker-pin" />
                    <span className="marker-text">Warning ({dossier.finding.t_cue_seconds}s)</span>
                  </div>
                )}

                {/* Marker for Ground Truth Incident */}
                {dossier.t_incident && (
                  <div
                    className="timeline-marker incident-marker"
                    style={{ left: `${(dossier.t_incident / dossier.duration) * 100}%` }}
                    title={`Ground Truth Incident at t=${dossier.t_incident}s`}
                  >
                    <div className="marker-pin" />
                    <span className="marker-text">Incident ({dossier.t_incident}s)</span>
                  </div>
                )}

                {/* Scrubber indicator */}
                <div
                  className="timeline-scrubber"
                  style={{ left: `${(currentTime / dossier.duration) * 100}%` }}
                />
              </div>

              {/* Cutoff modifier form */}
              <div className="timeline-controls">
                <label className="control-label">
                  Adjust Inference Cutoff (t ≤ sec):
                  <input
                    type="number"
                    step="0.1"
                    min="1.0"
                    max={dossier.duration}
                    value={userCutoff}
                    onChange={(e) => setUserCutoff(e.target.value === "" ? "" : parseFloat(e.target.value))}
                    className="cutoff-input"
                  />
                </label>
                <button
                  className="btn-reanalyze"
                  onClick={() => {
                    if (typeof userCutoff === "number") {
                      loadSample(selectedSample, userCutoff);
                    }
                  }}
                  disabled={busy}
                >
                  {busy ? "Analyzing..." : "Re-evaluate with Cutoff"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Intelligence Dossier Panel */}
        <div className="prelude-intel-column">
          {busy && (
            <div className="prelude-loading-card">
              <div className="spinner" />
              <h3>Evaluating Kinematic Trajectories & Scene Conflict...</h3>
              <p>Strictly bounded to pre-incident frames (t ≤ {userCutoff || "cutoff"}s)</p>
            </div>
          )}

          {!busy && dossier && (
            <div className="prelude-dossier-card">
              {/* Finding Hero Badge */}
              <div className={`hero-risk-panel ${riskBadgeClass(dossier.risk_level)}`}>
                <div className="hero-risk-top">
                  <span className="risk-level-tag">
                    RISK LEVEL: {dossier.risk_level.toUpperCase()}
                  </span>
                  {dossier.lead_time !== null && dossier.lead_time !== undefined && (
                    <span className="lead-time-tag">
                      +{dossier.lead_time.toFixed(2)}s Lead Time
                    </span>
                  )}
                </div>
                <div className="hero-summary-text">{dossier.finding.summary}</div>
                {dossier.finding.hazard_actor && (
                  <div className="hero-actor-text">
                    <strong>Salient Actor:</strong> {dossier.finding.hazard_actor}
                  </div>
                )}
              </div>

              {/* Kinematics Telemetry Grid */}
              <div className="telemetry-grid">
                <div className="telemetry-box">
                  <span className="telemetry-label">Peak Lateral Flow</span>
                  <span className="telemetry-value">
                    {dossier.finding.kinematic_signals.peak_lateral_flow ?? "0.0"} px/s
                  </span>
                  <span className="telemetry-sub">Crossing trajectory anomaly</span>
                </div>
                <div className="telemetry-box">
                  <span className="telemetry-label">Peak Looming Rate (τ)</span>
                  <span className="telemetry-value">
                    {dossier.finding.kinematic_signals.peak_looming_rate ?? "0.0"}
                  </span>
                  <span className="telemetry-sub">Optical expansion dA/dt</span>
                </div>
                <div className="telemetry-box">
                  <span className="telemetry-label">Tracked Road Actors</span>
                  <span className="telemetry-value">{dossier.actors.length}</span>
                  <span className="telemetry-sub">Persistent 2D trajectories</span>
                </div>
              </div>

              {/* Grounded Second-by-Second Observations */}
              <div className="observations-section">
                <h4 className="section-title">Grounded Second-by-Second Evidence</h4>
                <ul className="observations-list">
                  {dossier.finding.observations.map((obs, idx) => (
                    <li key={idx} className="observation-item">
                      <span className="obs-dot" />
                      <span className="obs-text">{obs}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Epistemic Boundaries & Uncertainty */}
              <div className="uncertainty-section">
                <h4 className="section-title">Epistemic Uncertainty & Limitations</h4>
                <p className="uncertainty-text">{dossier.finding.uncertainty}</p>
                <div className="disclaimer-callout">
                  <strong>Notice:</strong> {dossier.disclaimer}
                </div>
              </div>
            </div>
          )}

          {/* Upload Custom Clip Form */}
          <div className="custom-upload-card">
            <h4>Analyze Custom Dashcam Footage</h4>
            <form onSubmit={handleCustomUpload} className="custom-upload-form">
              <input
                type="file"
                accept="video/mp4,video/webm,video/quicktime"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                className="file-picker"
              />
              <button
                type="submit"
                disabled={!uploadFile || busy}
                className="btn-upload-analyze"
              >
                Upload & Run PRELUDE
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
