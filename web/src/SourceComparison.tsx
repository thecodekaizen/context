import { useRef, useState } from "react";
import { ForensicPlayer } from "./ForensicPlayer";
import { GroundingBadge } from "./AuditArtifacts";
import type { Review } from "./types";
import type { Dossier } from "./types";

export function SourceComparison({ dossier }: { dossier: Dossier }) {
  const source = useRef<HTMLVideoElement>(null);
  const edited = useRef<HTMLVideoElement>(null);
  const pending = useRef<{ source?: number; edited?: number }>({});
  const [linked, setLinked] = useState(true);
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
        {matched.discovery === "registered_technical_catalog"
          ? "Retrieved from registered technical source catalog"
          : matched.discovery === "NASA_catalog_search"
            ? "Legacy catalog provenance (historical record)"
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
      <ForensicPlayer
        key={dossier.id}
        media={matched.media}
        sourceRef={source}
        editedRef={edited}
        segments={segments || []}
        findings={matched.findings || []}
        editedDuration={dossier.media?.duration || 0}
        linked={linked}
        onLink={setLinked}
        onEditedUpdate={synchronize}
        onLoaded={(kind) => {
          apply(kind);
          setMediaErrors((x) => ({ ...x, [kind]: undefined }));
        }}
        onError={(kind) => {
          setLinked(false);
          setMediaErrors((x) => ({
            ...x,
            [kind]: `${kind === "source" ? "Source" : "Submitted"} video could not be loaded.`,
          }));
        }}
        onReveal={(finding) => seek("source", finding.source_start)}
        crop={cropAnalysis}
      />
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
              Measured spatial geometry. Peripheral elements outside the crop
              window are omitted in submitted clip.
            </p>
          </article>
        )}
        {comparison.reviews.map((review, index) => (
          <article className="card-box" key={review.finding_id || index}>
            {review.interpretation && review.model && (
              <GroundingBadge
                review={review as Review}
                finding={review.finding}
                grounded={
                  review.status === "complete" &&
                  review.finding.kind === "omission"
                }
              />
            )}
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
        whole-video truth verdict.{" "}
        {dossier.pipeline === "deterministic_first"
          ? "The supplied caption remains unverified."
          : "Historical caption claims have separate document-backed assessments below."}
      </p>
    </section>
  );
}
