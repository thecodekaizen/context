import React, { useRef, useState, useEffect } from "react";
import type { Dossier, DossierEvent, DossierFinding } from "./types";

interface Props {
  dossier: Dossier;
  onSelectFinding?: (finding: DossierFinding) => void;
}

const fmtTime = (s: number) => {
  const m = Math.floor(s / 60);
  const sec = (s % 60).toFixed(1);
  return `${m.toString().padStart(2, "0")}:${sec.padStart(4, "0")}`;
};

export function InvestigationDossier({ dossier }: Props) {
  const [tab, setTab] = useState<"overview" | "player" | "claims" | "sources" | "boundaries">("overview");
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [selectedModality, setSelectedModality] = useState<"all" | "visual" | "audio" | "on_screen">("all");
  const [activeEvent, setActiveEvent] = useState<DossierEvent | null>(null);
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const media = dossier.media;
  const analysis = dossier.analysis;
  const assessment = dossier.assessment;
  const findings = assessment?.findings || [];
  const sources = dossier.sources || [];

  const contradictedCount = findings.filter((f) => f.verdict === "contradicted").length;
  const supportedCount = findings.filter((f) => f.verdict === "supported").length;
  const inconclusiveCount = findings.filter((f) => f.verdict === "inconclusive").length;

  const seekTo = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play().catch(() => {});
    }
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const t = videoRef.current.currentTime;
    setCurrentTime(t);
    if (analysis?.observations) {
      const match = analysis.observations.find((obs) => t >= obs.start && t <= obs.end);
      if (match) setActiveEvent(match);
    }
  };

  const filteredObservations = analysis?.observations.filter((obs) => {
    if (selectedModality === "all") return true;
    return obs.modality === selectedModality;
  }) || [];

  return (
    <div className="dossier-container">
      {/* Dossier Header Banner */}
      <section className="dossier-hero">
        <div className="dossier-hero-badge">
          <span className="live-dot" />
          <span>INVESTIGATION DOSSIER</span>
          <span className="badge-sep">•</span>
          <span className="dossier-id">{dossier.id.slice(0, 12)}</span>
          <span className="badge-sep">•</span>
          <span className="dossier-status-pill">{dossier.status.toUpperCase()}</span>
        </div>

        <h1 className="dossier-title">
          {dossier.caption ? `“${dossier.caption}”` : "Multimodal Single-Video Investigation"}
        </h1>

        <div className="dossier-summary-box">
          <div className="summary-label">ASSESSMENT SUMMARY</div>
          <p className="summary-text">
            {assessment?.summary || analysis?.summary || "Investigation complete. Grounded evidence details below."}
          </p>
        </div>

        {/* High-level metrics row */}
        <div className="dossier-metrics">
          <div className="metric-card contradicted">
            <div className="metric-val">{contradictedCount}</div>
            <div className="metric-lbl">Contradicted Claims</div>
          </div>
          <div className="metric-card supported">
            <div className="metric-val">{supportedCount}</div>
            <div className="metric-lbl">Supported Facts</div>
          </div>
          <div className="metric-card inconclusive">
            <div className="metric-val">{inconclusiveCount}</div>
            <div className="metric-lbl">Inconclusive / Unproven</div>
          </div>
          <div className="metric-card sources">
            <div className="metric-val">{sources.filter((s) => s.fetch_status === "fetched").length}</div>
            <div className="metric-lbl">Checked Sources</div>
          </div>
        </div>
      </section>

      {/* Navigation Tabs */}
      <nav className="dossier-nav">
        <button
          className={`dossier-tab ${tab === "overview" ? "active" : ""}`}
          onClick={() => setTab("overview")}
        >
          01 Overview & Dossier
        </button>
        <button
          className={`dossier-tab ${tab === "player" ? "active" : ""}`}
          onClick={() => setTab("player")}
        >
          02 Visual Player & Timeline ({analysis?.observations.length || 0})
        </button>
        <button
          className={`dossier-tab ${tab === "claims" ? "active" : ""}`}
          onClick={() => setTab("claims")}
        >
          03 Claims & Fact-Check ({findings.length})
        </button>
        <button
          className={`dossier-tab ${tab === "sources" ? "active" : ""}`}
          onClick={() => setTab("sources")}
        >
          04 Discovered Sources ({sources.length})
        </button>
        <button
          className={`dossier-tab ${tab === "boundaries" ? "active" : ""}`}
          onClick={() => setTab("boundaries")}
        >
          05 Epistemic Limits & Uncertainty
        </button>
      </nav>

      {/* Tab 1: Overview */}
      {tab === "overview" && (
        <div className="dossier-tab-content">
          <div className="overview-grid">
            {/* Left column: Key Findings and Observations */}
            <div className="overview-left">
              <div className="card-box">
                <div className="card-header">
                  <span className="card-eyebrow">OBSERVATIONS BREAKDOWN</span>
                  <h3>What the Footage Shows</h3>
                </div>
                <p className="section-desc">{analysis?.summary}</p>

                <div className="quick-obs-list">
                  {analysis?.observations.slice(0, 6).map((obs) => (
                    <div
                      key={obs.id}
                      className="quick-obs-item"
                      onClick={() => {
                        setTab("player");
                        seekTo(obs.start);
                      }}
                    >
                      <span className={`modality-pill ${obs.modality}`}>{obs.modality}</span>
                      <span className="time-code">{fmtTime(obs.start)}</span>
                      <span className="obs-text">{obs.text}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Manipulation & Authenticity Status */}
              <div className="status-cards-row">
                <div className="status-card">
                  <div className="status-card-header">
                    <span className="status-dot warning" />
                    <strong>Authenticity Status</strong>
                  </div>
                  <div className="status-val">{dossier.authenticity?.status || "Unproven"}</div>
                  <p className="status-desc">{dossier.authenticity?.reason}</p>
                </div>
                <div className="status-card">
                  <div className="status-card-header">
                    <span className="status-dot neutral" />
                    <strong>Manipulation Status</strong>
                  </div>
                  <div className="status-val">{dossier.manipulation?.status || "Original Not Located"}</div>
                  <p className="status-desc">{dossier.manipulation?.reason}</p>
                </div>
              </div>
            </div>

            {/* Right column: Primary Findings */}
            <div className="overview-right">
              <div className="card-box">
                <div className="card-header">
                  <span className="card-eyebrow">VERIFIED FINDINGS</span>
                  <h3>Claims vs. External Evidence</h3>
                </div>

                <div className="findings-stream">
                  {findings.map((f) => {
                    const claim = analysis?.claims.find((c) => c.id === f.claim_id);
                    return (
                      <div key={f.claim_id} className={`finding-box ${f.verdict}`}>
                        <div className="finding-box-top">
                          <span className={`verdict-pill ${f.verdict}`}>
                            {f.verdict.toUpperCase()}
                          </span>
                          <span className="claim-origin-pill">
                            {claim?.origin?.replace("_", " ").toUpperCase() || "CLAIM"}
                          </span>
                        </div>
                        <div className="claim-quote">“{claim?.text || f.claim_id}”</div>
                        <p className="finding-expl">{f.explanation}</p>

                        {f.source_refs.length > 0 && (
                          <div className="finding-refs">
                            <span className="refs-label">Checked Evidence:</span>
                            {f.source_refs.map((ref, idx) => (
                              <blockquote key={idx} className="evidence-excerpt">
                                “{ref.excerpt}”
                                <span className="ref-source-id">({ref.source_id})</span>
                              </blockquote>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Visual Player & Timeline */}
      {tab === "player" && (
        <div className="dossier-tab-content">
          <div className="player-layout">
            <div className="player-main">
              {media?.media_url ? (
                <div className="video-wrapper">
                  <video
                    ref={videoRef}
                    controls
                    src={media.media_url}
                    onTimeUpdate={handleTimeUpdate}
                    className="cinema-video"
                  />
                  <div className="video-meta-overlay">
                    <span>{fmtTime(currentTime)} / {fmtTime(media.duration)}</span>
                    <span>{media.width}x{media.height} • {media.codec.toUpperCase()}</span>
                  </div>
                </div>
              ) : (
                <div className="no-video">Video playback file unavailable</div>
              )}

              {/* Keyframe Snapshot Reel */}
              {media?.frames && media.frames.length > 0 && (
                <div className="frame-reel">
                  <div className="reel-title">ANALYZED KEYFRAME REEL (CLICK TO SEEK)</div>
                  <div className="reel-scroll">
                    {media.frames.map((frame) => (
                      <div
                        key={frame.id}
                        className={`frame-thumb-box ${Math.abs(currentTime - frame.time) < 5 ? "active" : ""}`}
                        onClick={() => seekTo(frame.time)}
                      >
                        <img src={frame.url} alt={`Frame at ${frame.time}s`} />
                        <span className="frame-time">{fmtTime(frame.time)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Observations Timeline Sidebar */}
            <div className="player-sidebar">
              <div className="sidebar-header">
                <h3>Multimodal Timeline</h3>
                <div className="modality-filters">
                  {(["all", "visual", "audio", "on_screen"] as const).map((m) => (
                    <button
                      key={m}
                      className={`filter-btn ${selectedModality === m ? "active" : ""}`}
                      onClick={() => setSelectedModality(m)}
                    >
                      {m.replace("_", " ")}
                    </button>
                  ))}
                </div>
              </div>

              <div className="timeline-events-list">
                {filteredObservations.map((obs) => {
                  const isActive = activeEvent?.id === obs.id;
                  return (
                    <div
                      key={obs.id}
                      className={`timeline-event-card ${obs.modality} ${isActive ? "active" : ""}`}
                      onClick={() => seekTo(obs.start)}
                    >
                      <div className="event-top">
                        <span className={`modality-badge ${obs.modality}`}>{obs.modality}</span>
                        <span className="event-time">
                          {fmtTime(obs.start)} – {fmtTime(obs.end)}
                        </span>
                      </div>
                      <p className="event-text">{obs.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Claims & Fact-Check */}
      {tab === "claims" && (
        <div className="dossier-tab-content">
          <div className="claims-section">
            <div className="section-heading">
              <h2>Extracted Factual Claims & Evaluation</h2>
              <p>
                Meta models independently extracted claims from spoken commentary, on-screen lower thirds,
                and supplied captions. Claims are grounded strictly against fetched primary documents.
              </p>
            </div>

            <div className="claims-detailed-list">
              {findings.map((f) => {
                const claim = analysis?.claims.find((c) => c.id === f.claim_id);
                return (
                  <div key={f.claim_id} className={`claim-card-detailed ${f.verdict}`}>
                    <div className="card-top-bar">
                      <span className={`verdict-badge ${f.verdict}`}>
                        {f.verdict.toUpperCase()}
                      </span>
                      <span className="origin-tag">
                        Origin: {claim?.origin?.replace("_", " ") || "Claim"}
                      </span>
                      {claim?.start !== undefined && claim?.start !== null && (
                        <button
                          className="jump-time-btn"
                          onClick={() => {
                            setTab("player");
                            seekTo(claim.start || 0);
                          }}
                        >
                          ▶ Jump to {fmtTime(claim.start)}
                        </button>
                      )}
                    </div>

                    <div className="target-claim">
                      <strong>Claim:</strong> “{claim?.text || f.claim_id}”
                    </div>

                    <div className="evaluation-box">
                      <strong>Investigation Finding:</strong>
                      <p>{f.explanation}</p>
                    </div>

                    {f.source_refs.length > 0 && (
                      <div className="source-citations-container">
                        <strong>Checked Citations:</strong>
                        {f.source_refs.map((ref, i) => {
                          const src = sources.find((s) => s.id === ref.source_id);
                          return (
                            <div key={i} className="citation-pill">
                              <span className="cite-badge">✓ Verified Match</span>
                              <span className="cite-excerpt">“{ref.excerpt}”</span>
                              {src && (
                                <a
                                  href={src.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="cite-link"
                                >
                                  Source: {src.title || src.url} ↗
                                </a>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {f.validation?.rejected_source_ids && f.validation.rejected_source_ids.length > 0 && (
                      <div className="rejected-refs-note">
                        Excluded {f.validation.rejected_source_ids.length} unverified or ungrounded citation references.
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Discovered Sources */}
      {tab === "sources" && (
        <div className="dossier-tab-content">
          <div className="sources-section">
            <div className="section-heading">
              <h2>Automatically Discovered Sources</h2>
              <p>
                Sources retrieved via Meta's live search integration. No URLs were manually supplied.
                Full text fetched and cached strictly within verified public domains.
              </p>
            </div>

            <div className="sources-grid">
              {sources.map((s) => (
                <div key={s.id} className="source-card">
                  <div className="source-card-top">
                    <span className="source-id-badge">{s.id}</span>
                    <span className={`fetch-status-badge ${s.fetch_status}`}>
                      {s.fetch_status === "fetched" ? "Fetched (200 OK)" : "Coverage Bound"}
                    </span>
                  </div>

                  <h3 className="source-title">{s.title || s.url}</h3>
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    className="source-url-link"
                  >
                    {s.url} ↗
                  </a>

                  {s.search_snippet && (
                    <p className="search-snippet">{s.search_snippet}</p>
                  )}

                  {s.fetch_status === "fetched" && s.text && (
                    <div className="source-text-drawer">
                      <button
                        className="toggle-text-btn"
                        onClick={() =>
                          setExpandedSource(expandedSource === s.id ? null : s.id)
                        }
                      >
                        {expandedSource === s.id ? "Hide Extracted Text" : `View Extracted Text (${s.text.length} chars)`}
                      </button>
                      {expandedSource === s.id && (
                        <pre className="source-pre">{s.text.slice(0, 3000)}...</pre>
                      )}
                    </div>
                  )}

                  {s.fetch_error && (
                    <div className="fetch-error-box">{s.fetch_error}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Epistemic Limits & Provenance */}
      {tab === "boundaries" && (
        <div className="dossier-tab-content">
          <div className="boundaries-section">
            <div className="section-heading">
              <h2>Epistemic Boundaries & Uncertainty</h2>
              <p>
                CONTEXT strictly enforces honest boundaries: verified event facts do not automatically authenticate
                the uploaded footage itself, and the absence of an original does not equal fabrication.
              </p>
            </div>

            <div className="boundaries-grid">
              <div className="boundary-card">
                <h3>Identified Unknowns</h3>
                <ul className="boundary-list">
                  {analysis?.unknowns.map((u, i) => (
                    <li key={i}>{u}</li>
                  ))}
                </ul>
              </div>

              <div className="boundary-card">
                <h3>Missing Evidence</h3>
                <ul className="boundary-list">
                  {assessment?.missing_evidence.map((m, i) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              </div>

              <div className="boundary-card full-width">
                <h3>Provenance & Methodology</h3>
                <p><strong>Evaluation Input:</strong> {JSON.stringify(dossier.input_provenance)}</p>
                <p><strong>Model Contribution:</strong> Observation extraction by <code>muse-spark-1.2</code>; web search and fact verification by <code>muse-spark-1.3</code>.</p>
                <p><strong>Dossier Assessment:</strong> {assessment?.provenance}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
