import { useId, useRef } from "react";
import type { Dossier, Evidence, Finding, Review } from "./types";
import { timecode, measuredFindings } from "./ForensicPlayer";

export function GroundingBadge({
  review,
  finding,
  grounded,
}: {
  review: Review;
  finding?: Finding;
  grounded: boolean;
}) {
  return (
    <div className={`grounding-badge ${grounded ? "is-grounded" : ""}`}>
      <div>
        <span className="precision-dot" />
        <strong>
          {grounded && finding
            ? `GROUNDED INTERVAL · ${timecode(finding.source_start)} — ${timecode(finding.source_end)}`
            : "BOUNDED MODEL INTERPRETATION"}
        </strong>
        <span className="audit-seal">◇ AUDIT TRACE</span>
      </div>
      <p>
        {review.model} ·{" "}
        {grounded ? "Deterministic gate checked" : "Inspect interval evidence"}{" "}
        · Citation bounds checked
      </p>
      <small>
        Timestamp validation constrains references. It does not certify semantic
        accuracy.
      </small>
    </div>
  );
}

export function ArtifactExport({
  evidence,
  dossier,
}: {
  evidence?: Evidence | null;
  dossier?: Dossier | null;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const title = useId();
  const id = evidence?.id || dossier?.id;
  const sourceHash = evidence?.source.sha256 || dossier?.media?.sha256;
  const findings = measuredFindings(
    evidence?.findings || dossier?.matched_source?.findings || [],
    evidence?.omission_evidence,
  );
  const segments =
    evidence?.segments || dossier?.matched_source?.segments || [];
  const confidence = segments
    .filter((s) => s.kind === "match")
    .map((s) => s.confidence);
  const mean = confidence.length
    ? confidence.reduce((a, b) => a + b, 0) / confidence.length
    : null;
  const editedHash = evidence?.edited.sha256;
  return (
    <>
      <button
        className="export-trigger quiet"
        disabled={!id}
        onClick={() => dialog.current?.showModal()}
      >
        ↗ Export Forensic Dossier
      </button>
      <dialog
        ref={dialog}
        className="audit-dialog"
        aria-labelledby={title}
        onClick={(event) => {
          if (event.target === event.currentTarget) dialog.current?.close();
        }}
      >
        <div className="report-actions">
          <span className="micro-label">EXECUTIVE AUDIT PREVIEW</span>
          <button
            className="quiet"
            aria-label="Close export preview"
            onClick={() => dialog.current?.close()}
          >
            ✕
          </button>
        </div>
        <article className="print-report">
          <div className="report-brand">
            CONTEXT <span>/ EVIDENCE RECORD</span>
          </div>
          <h2 id={title}>Forensic investigation dossier</h2>
          <p className="report-id">CASE / {id}</p>
          <div className="report-summary">
            <div>
              <span>VISUAL COVERAGE</span>
              <strong>
                {evidence?.coverage != null
                  ? `${(evidence.coverage * 100).toFixed(1)}%`
                  : "Not available"}
              </strong>
            </div>
            <div>
              <span>MATCH CONFIDENCE · MEAN</span>
              <strong>
                {mean == null ? "Not available" : mean.toFixed(4)}
              </strong>
            </div>
            <div>
              <span>MEASURED FINDINGS</span>
              <strong>{findings.length}</strong>
            </div>
          </div>
          <h3>
            Media fingerprints <span>SHA-256</span>
          </h3>
          <dl className="fingerprints">
            <dt>{evidence ? "Original source" : "Submitted media"}</dt>
            <dd>{sourceHash || "Not supplied by API"}</dd>
            {evidence && (
              <>
                <dt>Published edit</dt>
                <dd>{editedHash || "Not supplied by API"}</dd>
              </>
            )}
          </dl>
          <h3>Measured intervals</h3>
          {findings.length ? (
            <table>
              <thead>
                <tr>
                  <th>Finding</th>
                  <th>Source start</th>
                  <th>Source end</th>
                </tr>
              </thead>
              <tbody>
                {findings.map((f) => (
                  <tr key={f.id}>
                    <td>{f.kind.replaceAll("_", " ")}</td>
                    <td>{timecode(f.source_start)}</td>
                    <td>{timecode(f.source_end)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No measured interval findings in this record.</p>
          )}
          {(evidence?.domain_admission || dossier?.domain_admission) && (
            <>
              <h3>Admission at processing time</h3>
              {Object.entries(
                evidence?.domain_admission || dossier?.domain_admission || {},
              ).map(([name, decision]) => (
                <p key={name}>
                  <strong>
                    {name}: {decision.status.replaceAll("_", " ")}
                  </strong>{" "}
                  · {decision.review?.category.replaceAll("_", " ")} ·{" "}
                  {decision.review?.basis === "frozen_fixture"
                    ? "Pinned controlled fixture"
                    : "Local operator review"}
                  . {decision.reason}
                </p>
              ))}
              <p>
                Operator admission is a recorded review, not automatic content
                classification or a guarantee of semantic accuracy.
              </p>
            </>
          )}
          <h3>Scope & limitations</h3>
          <p>
            Correspondence establishes media relationships, not intent or
            deception. Confidence is the mean of matched interval scores; it is
            not a probability of truth. Fingerprints identify media bytes and
            are not a digital signature.
          </p>
          {evidence?.limitations.map((text, i) => (
            <p key={i}>{text}</p>
          ))}
          {dossier?.comparison?.scope && <p>{dossier.comparison.scope}</p>}
        </article>
        <div className="report-actions">
          <span>Print-ready · Save as PDF in your browser</span>
          <button onClick={() => window.print()}>Print / Save PDF ↗</button>
        </div>
      </dialog>
    </>
  );
}
