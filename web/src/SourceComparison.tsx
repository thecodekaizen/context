import { useRef, useState } from "react";
import type { Dossier } from "./types";

export function SourceComparison({ dossier }: { dossier: Dossier }) {
  const source = useRef<HTMLVideoElement>(null);
  const edited = useRef<HTMLVideoElement>(null);
  const pending = useRef<{ source?: number; edited?: number }>({});
  const [linked, setLinked] = useState(true);
  const [showCropOverlay, setShowCropOverlay] = useState(true);
  const [mediaErrors, setMediaErrors] = useState<{
    source?: string;
    edited?: string;
  }>({});
  const comparison = dossier.comparison;
  const matched = dossier.matched_source;
  if (!comparison) return null;
  if (!matched?.media)
    return (
      <section className="comparison-empty card-box" role="status">
        <h3>Source footage comparison</h3>
        <p>{comparison.scope}</p>
        <p>
          No matching source recording was established. Document citations
          cannot fill that gap.
        </p>
      </section>
    );
  const cropAnalysis = matched.crop_analysis || comparison.crop_analysis;
  const segments =
    matched.basis === "audio_only"
      ? matched.audio_alignment?.segments
      : matched.segments;
  const apply = (media: "source" | "edited") => {
    const player = media === "source" ? source.current : edited.current;
    const time = pending.current[media];
    if (player && player.readyState >= 1 && time !== undefined) {
      player.currentTime = time;
      delete pending.current[media];
    }
  };
  const seek = (media: "source" | "edited", time: number) => {
    setLinked(false);
    source.current?.pause();
    edited.current?.pause();
    pending.current[media] = time;
    apply(media);
  };
  const synchronize = () => {
    const e = edited.current,
      s = source.current;
    if (!e || !s || !linked) return;
    const interval = segments?.find(
      (x) =>
        x.kind === "match" &&
        e.currentTime >= x.edited_start &&
        e.currentTime < x.edited_end,
    );
    if (!interval || interval.source_start === null) {
      s.pause();
      return;
    }
    const target =
      interval.source_start + e.currentTime - interval.edited_start;
    if (Math.abs(s.currentTime - target) > 0.15) s.currentTime = target;
    if (!e.paused && s.paused) void s.play().catch(() => {});
  };
  return (
    <section
      id="source-comparison"
      className="source-comparison"
      aria-label="Source footage comparison"
    >
      <header className="comparison-heading">
        <div>
          <span className="card-eyebrow">
            MEASURED EVIDENCE · BOUNDED INTERPRETATION
          </span>
          <h2>What changed in the recording?</h2>
          <p>{comparison.scope}</p>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          {cropAnalysis?.detected && (
            <label>
              <input
                type="checkbox"
                checked={showCropOverlay}
                onChange={(e) => setShowCropOverlay(e.target.checked)}
              />{" "}
              Show spatial crop overlay
            </label>
          )}
          <label>
            <input
              type="checkbox"
              checked={linked}
              onChange={(e) => setLinked(e.target.checked)}
            />{" "}
            Link{" "}
            {matched.basis === "audio_only" ? "soundtrack" : "matched video"}{" "}
            timing
          </label>
        </div>
      </header>
      <p className="comparison-provenance">
        Source: {matched.source_name} ·{" "}
        {matched.discovery === "NASA_catalog_search"
          ? "Discovered through NASA catalog search"
          : "Matched in provided local collection"}
        .{" "}
        {matched.basis === "audio_only"
          ? "Audio match only: matching sound does not authenticate the images."
          : "Visual correspondence is not proof of original authorship."}
      </p>
      {(mediaErrors.source || mediaErrors.edited) && (
        <div role="alert" className="error">
          <p>
            {mediaErrors.source} {mediaErrors.edited}
          </p>
          <button
            className="quiet"
            onClick={() => {
              source.current?.load();
              edited.current?.load();
            }}
          >
            Reload video files
          </button>
          <p>
            Measured evidence remains available. Reloading playback does not
            rerun model analysis.
          </p>
        </div>
      )}
      <div className="comparison-players">
        <div>
          <h3>Submitted footage</h3>
          <video
            ref={edited}
            src={matched.media.edited}
            controls
            playsInline
            preload="metadata"
            onLoadedMetadata={() => {
              apply("edited");
              setMediaErrors((x) => ({ ...x, edited: undefined }));
            }}
            onError={() =>
              setMediaErrors((x) => ({
                ...x,
                edited: "Submitted video could not be loaded.",
              }))
            }
            onTimeUpdate={synchronize}
            onSeeked={synchronize}
            onPlay={synchronize}
            onPause={() => {
              if (linked) source.current?.pause();
            }}
          />
        </div>
        <div style={{ position: "relative" }}>
          <h3>Candidate source · {matched.source_name}</h3>
          <div
            style={{ position: "relative", width: "100%", overflow: "hidden" }}
          >
            <video
              ref={source}
              src={matched.media.source}
              controls
              playsInline
              preload="metadata"
              muted={linked}
              onLoadedMetadata={() => {
                apply("source");
                setMediaErrors((x) => ({ ...x, source: undefined }));
              }}
              onError={() => {
                setLinked(false);
                setMediaErrors((x) => ({
                  ...x,
                  source: "Source video could not be loaded.",
                }));
              }}
            />
            {cropAnalysis?.detected &&
              showCropOverlay &&
              cropAnalysis.crop_box &&
              cropAnalysis.source_resolution && (
                <svg
                  viewBox={`0 0 ${cropAnalysis.source_resolution[0]} ${cropAnalysis.source_resolution[1]}`}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    pointerEvents: "none",
                  }}
                  aria-hidden="true"
                >
                  <rect
                    x={cropAnalysis.crop_box.x}
                    y={cropAnalysis.crop_box.y}
                    width={cropAnalysis.crop_box.width}
                    height={cropAnalysis.crop_box.height}
                    fill="none"
                    stroke="#22c55e"
                    strokeWidth={4}
                    strokeDasharray="8 6"
                  />
                  <text
                    x={cropAnalysis.crop_box.x + 12}
                    y={cropAnalysis.crop_box.y + 28}
                    fill="#22c55e"
                    fontSize="22"
                    fontWeight="bold"
                    style={{ textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}
                  >
                    RETAINED IN EDIT (
                    {((cropAnalysis.area_retained_fraction || 0) * 100).toFixed(
                      0,
                    )}
                    %)
                  </text>
                  {cropAnalysis.omitted_margins?.map((m, idx) => (
                    <g key={idx}>
                      <rect
                        x={m.x}
                        y={m.y}
                        width={m.width}
                        height={m.height}
                        fill="rgba(239, 68, 68, 0.35)"
                        stroke="rgba(239, 68, 68, 0.75)"
                        strokeWidth={2}
                      />
                      <text
                        x={m.x + 8}
                        y={m.y + 24}
                        fill="#fca5a5"
                        fontSize="18"
                        fontWeight="600"
                        style={{ textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}
                      >
                        CUT OUT: {m.name.toUpperCase()}
                      </text>
                    </g>
                  ))}
                </svg>
              )}
          </div>
        </div>
      </div>
      {matched.source_url && (
        <a href={matched.source_url} target="_blank" rel="noreferrer">
          Open acquired source recording ↗
        </a>
      )}
      <div className="comparison-findings">
        {cropAnalysis?.detected && (
          <article
            className="card-box"
            style={{ borderLeft: "3px solid #38bdf8" }}
          >
            <span className="verdict-pill">SPATIAL CROP DETECTED</span>
            <h3>
              Visual reframe ·{" "}
              {((cropAnalysis.area_omitted_fraction || 0) * 100).toFixed(0)}%
              peripheral context omitted
            </h3>
            <p>{cropAnalysis.explanation}</p>
            <div style={{ marginTop: "10px" }}>
              {cropAnalysis.omitted_margins?.map((m, idx) => (
                <span
                  key={idx}
                  style={{
                    display: "inline-block",
                    padding: "3px 8px",
                    background: "rgba(239, 68, 68, 0.15)",
                    border: "1px solid rgba(239, 68, 68, 0.4)",
                    color: "#fca5a5",
                    borderRadius: "4px",
                    fontSize: "12px",
                    marginRight: "8px",
                    marginBottom: "4px",
                  }}
                >
                  Omitted {m.name} margin ({m.width}×{m.height}px)
                </span>
              ))}
            </div>
            <p className="comparison-uncertainty" style={{ marginTop: "12px" }}>
              SAM 3.1 & spatial reframe detector verified. Peripheral elements
              outside the crop window are omitted in submitted clip.
            </p>
          </article>
        )}
        {comparison.reviews.map((review, index) => (
          <article className="card-box" key={review.finding_id || index}>
            <span className="verdict-pill">
              {review.interpretation?.classification?.replaceAll("_", " ") ||
                "Comparison unavailable"}
            </span>
            <h3>
              {review.finding.kind.replaceAll("_", " ")} ·{" "}
              {review.finding.modality || "visual"} evidence
            </h3>
            <p>{review.interpretation?.possible_effect || review.error}</p>
            <details className="comparison-details">
              <summary>
                Inspect timestamped observations (
                {review.interpretation?.observations.length || 0})
              </summary>
              {review.interpretation?.observations.map((observation, n) => (
                <div className="comparison-observation" key={n}>
                  <p>{observation.text}</p>
                  {observation.citations.map((citation, k) => (
                    <button
                      key={k}
                      className="quiet evidence-seek"
                      onClick={() => seek(citation.media, citation.media_start)}
                    >
                      Inspect{" "}
                      {citation.media === "source" ? "source" : "submitted"}{" "}
                      {citation.media_start.toFixed(2)}–
                      {citation.media_end.toFixed(2)}s
                    </button>
                  ))}
                </div>
              ))}
            </details>
            <p className="comparison-uncertainty">
              {review.interpretation?.uncertainty ||
                "Measured correspondences remain available; semantic assessment could not be established."}
            </p>
          </article>
        ))}
      </div>
      <p className="comparison-uncertainty">
        Edits are measured separately from interpretation. A meaning change is a
        model assessment of these excerpts, not proof of deception or a
        whole-video truth verdict. Caption claims have separate document-backed
        assessments below.
      </p>
    </section>
  );
}
