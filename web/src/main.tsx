import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import type { Segment, Finding, Evidence, Review, Dossier } from "./types";
import { SourceCollection } from "./SourceCollection";
import { RecentInvestigations } from "./RecentInvestigations";
import { InvestigationDossier } from "./InvestigationDossier";
import { PreludeStudio } from "./PreludeStudio";
import { ForensicPlayer, timecode } from "./ForensicPlayer";
import { ArtifactExport, GroundingBadge } from "./AuditArtifacts";
import { BenchmarkHub } from "./BenchmarkHub";

const time = timecode;

function App() {
  // Top-level product view & mode
  const [activeView, setActiveView] = useState<"workbench" | "benchmark">(
    "workbench",
  );
  const [appMode, setAppMode] = useState<
    "investigation" | "prelude" | "comparator"
  >("comparator");

  // Single-video investigation state
  const [dossier, setDossier] = useState<Dossier | null>(null);
  const [dossierInputMode, setDossierInputMode] = useState<"upload" | "url">(
    "upload",
  );
  const [dossierFile, setDossierFile] = useState<File | null>(null);
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [dossierUrl, setDossierUrl] = useState<string>("");
  const [dossierCaption, setDossierCaption] = useState<string>("");
  const [dossierBusy, setDossierBusy] = useState<boolean>(false);
  const [dossierStage, setDossierStage] = useState<string>("queued");
  const [dossierError, setDossierError] = useState<string>("");
  const [recentDossiers, setRecentDossiers] = useState<Dossier[]>([]);
  const pollTimer = useRef<number | null>(null);
  useEffect(
    () => () => {
      if (pollTimer.current !== null) window.clearInterval(pollTimer.current);
    },
    [],
  );

  // Two-video comparator state (supporting capability)
  const [e, setE] = useState<Evidence | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [selected, setSelected] = useState<Finding | null>(null),
    [position, setPosition] = useState(0),
    [sync, setSync] = useState(true);
  const [original, setOriginal] = useState<File | null>(null),
    [edited, setEdited] = useState<File | null>(null);
  const [review, setReview] = useState<Review | null>(null),
    [reviewBusy, setReviewBusy] = useState<string | null>(null),
    [reviewError, setReviewError] = useState("");
  const [collectionBusy, setCollectionBusy] = useState(false);

  // Poll recent dossiers on load
  const loadRecentDossiers = () => {
    fetch("/api/dossiers")
      .then((r) => r.json())
      .then((data) => {
        if (data.dossiers && Array.isArray(data.dossiers)) {
          setRecentDossiers(data.dossiers);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/health", { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => {})
      .catch(() => {});

    loadRecentDossiers();

    // Check query params
    const params = new URLSearchParams(window.location.search);
    const dossierParam = params.get("dossier");
    if (dossierParam) {
      fetchDossier(dossierParam);
    }

    return () => controller.abort();
  }, []);

  const fetchDossier = async (id: string) => {
    setDossierBusy(true);
    setDossierError("");
    try {
      const res = await fetch(`/api/dossiers/${encodeURIComponent(id)}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to load dossier");
      setDossier(data);
      setAppMode("investigation");
      const url = new URL(window.location.href);
      url.searchParams.set("dossier", id);
      window.history.replaceState(null, "", url);
    } catch (err) {
      setDossierError(err instanceof Error ? err.message : "Load failed");
    } finally {
      setDossierBusy(false);
    }
  };

  const openComparatorForCase = async (id: string) => {
    try {
      const res = await fetch(`/api/investigations/${encodeURIComponent(id)}`);
      if (!res.ok) throw new Error("Could not load comparison");
      const data = await res.json();
      acceptEvidence(data.evidence || data);
      setAppMode("comparator");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.error(err);
    }
  };

  const startInvestigation = async (presetTarget?: {
    file?: File;
    url?: string;
    caption?: string;
  }) => {
    setDossier(null);
    setDossierBusy(true);
    setDossierError("");
    setDossierStage("queued");

    try {
      const formData = new FormData();
      if (referenceFile) formData.append("reference", referenceFile);
      const targetUrl =
        presetTarget?.url !== undefined
          ? presetTarget.url
          : dossierInputMode === "url"
            ? dossierUrl.trim()
            : "";
      const targetFile =
        presetTarget?.file !== undefined
          ? presetTarget.file
          : dossierInputMode === "upload"
            ? dossierFile
            : null;
      const targetCaption =
        presetTarget?.caption !== undefined
          ? presetTarget.caption
          : dossierCaption.trim();

      if (targetUrl) {
        formData.append("url", targetUrl);
      } else if (targetFile) {
        formData.append("video", targetFile);
      } else {
        throw new Error("Provide a video file or a direct public video URL.");
      }

      if (targetCaption) {
        formData.append("caption", targetCaption);
      }

      const res = await fetch("/api/dossiers", {
        method: "POST",
        body: formData,
      });

      const init = await res.json();
      if (!res.ok)
        throw new Error(init.detail || "Failed to initiate investigation");

      const id = init.id;
      const startedPolling = Date.now();
      // Poll bounded jobs; stop rather than silently waiting forever.
      if (pollTimer.current !== null) window.clearInterval(pollTimer.current);
      const pollInterval = window.setInterval(async () => {
        try {
          const pollRes = await fetch(
            `/api/dossiers/${encodeURIComponent(id)}`,
          );
          if (!pollRes.ok) throw new Error("Job polling failed");
          if (pollRes.ok) {
            const data: Dossier = await pollRes.json();
            setDossierStage(data.stage);
            setDossier(data);
            if (data.status === "complete" || data.status === "partial") {
              window.clearInterval(pollInterval);
              setDossier(data);
              setDossierBusy(false);
              loadRecentDossiers();
              const url = new URL(window.location.href);
              url.searchParams.set("dossier", id);
              window.history.replaceState(null, "", url);
            } else if (data.status === "error") {
              window.clearInterval(pollInterval);
              setDossier(data);
              setDossierBusy(false);
              setDossierError(data.error || "Investigation failed");
              loadRecentDossiers();
            }
          }
        } catch {
          if (Date.now() - startedPolling > 10 * 60 * 1000) {
            window.clearInterval(pollInterval);
            setDossierBusy(false);
            setDossierError(
              "Stopped waiting after ten minutes. Reload this saved job to inspect retained evidence.",
            );
          }
          // ignore transient poll error
        }
      }, 2500);
      pollTimer.current = pollInterval;
    } catch (err) {
      setDossierBusy(false);
      setDossierError(
        err instanceof Error ? err.message : "Investigation initiation failed",
      );
    }
  };

  // Comparator handlers
  function resetInvestigation() {
    const url = new URL(window.location.href);
    url.searchParams.delete("case");
    window.history.replaceState(null, "", url);
    setE(null);
    setReview(null);
    setReviewError("");
    setSelected(null);
    setPosition(0);
    setSync(true);
    setError("");
  }

  function acceptEvidence(data: Evidence) {
    resetInvestigation();
    setE(data);
    const url = new URL(window.location.href);
    url.searchParams.set("case", data.id);
    window.history.replaceState(null, "", url);
  }

  function restoreEvidence(data: Evidence, savedReview: Review | null) {
    acceptEvidence(data);
    setReview(savedReview ? { ...savedReview, cached: true } : null);
  }

  const source = useRef<HTMLVideoElement>(null);
  const published = useRef<HTMLVideoElement>(null);

  async function analyze(demo: false | true | "benchmark" | "crop" = false) {
    setReview(null);
    setReviewError("");
    setBusy(true);
    setError("");
    setSelected(null);
    try {
      const body = new FormData();
      if (!demo) {
        if (!original || !edited) throw Error("Choose both videos first.");
        body.append("original", original);
        body.append("edited", edited);
      }
      const r = await fetch(
        demo === "benchmark"
          ? "/api/demo/benchmark"
          : demo === "crop"
            ? "/api/demo/crop"
            : demo
              ? "/api/demo"
              : "/api/analyze",
        { method: "POST", ...(!demo ? { body } : {}) },
      );
      const data = await r.json();
      if (!r.ok) throw Error(data.detail || "Analysis failed");
      acceptEvidence(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setBusy(false);
    }
  }

  async function reviewFinding(f: Finding) {
    if (!e) return;
    setReviewBusy(f.id);
    setReviewError("");
    setReview(null);
    try {
      const r = await fetch(`/api/investigations/${e.id}/interpret/${f.id}`, {
        method: "POST",
      });
      const data = await r.json();
      if (!r.ok)
        throw Error(
          typeof data.detail === "string"
            ? data.detail
            : "Model response failed validation.",
        );
      setReview(data);
    } catch (err) {
      setReviewError(
        err instanceof Error ? err.message : "Context review failed",
      );
    } finally {
      setReviewBusy(null);
    }
  }

  function inspectCitation(c: {
    media: "source" | "edited";
    media_start: number;
  }) {
    setSync(false);
    setSelected(null);
    published.current?.pause();
    source.current?.pause();
    const player = c.media === "source" ? source.current : published.current;
    if (player) player.currentTime = c.media_start;
  }

  function seek(s: Segment) {
    setSelected(null);
    setSync(true);
    if (published.current) published.current.currentTime = s.edited_start;
    if (source.current && s.source_start !== null)
      source.current.currentTime = s.source_start;
  }

  function reveal(f: Finding) {
    setSelected(f);
    setSync(false);
    published.current?.pause();
    if (source.current) {
      source.current.currentTime = f.source_start;
      void source.current
        .play()
        .catch(() =>
          setError(
            "Use the original player’s play control to reveal this interval.",
          ),
        );
    }
  }

  function update() {
    const p = published.current,
      o = source.current;
    if (!p || !e) return;
    setPosition(p.currentTime);
    if (!sync || !o) return;
    const s = e.segments.find(
      (s) =>
        s.kind === "match" &&
        p.currentTime >= s.edited_start &&
        p.currentTime < s.edited_end,
    );
    if (s && s.source_start !== null) {
      const target = s.source_start + p.currentTime - s.edited_start;
      if (Math.abs(o.currentTime - target) > 0.15) o.currentTime = target;
      if (!p.paused && o.paused) void o.play().catch(() => {});
    } else {
      o.pause();
    }
  }

  return (
    <main>
      <header>
        <a className="brand" href="/">
          C<span className="brand-eye">◉</span>NTEXT
          <span className="brand-dot">.</span>
        </a>
        <span className="tagline">SEE WHAT THE EDIT CUT OUT</span>
        <span className="local">
          <span className="precision-dot" /> LOCAL EVIDENCE WORKSPACE
        </span>
        <ArtifactExport evidence={e} dossier={dossier} />
      </header>

      {/* Top Product Navigation: Workbench vs Benchmark Suite */}
      <div
        className="product-nav"
        style={{
          display: "flex",
          gap: 12,
          margin: "18px 0 24px 0",
          borderBottom: "1px solid #282f34",
          paddingBottom: 14,
        }}
      >
        <button
          id="btn-nav-workbench"
          className={`mode-tab-btn ${activeView === "workbench" ? "active" : ""}`}
          onClick={() => {
            setActiveView("workbench");
            setAppMode("comparator");
          }}
        >
          <span className="mode-badge-supporting">01 WORKBENCH</span>
          Evidence Explorer & Dual Player
        </button>
        <button
          id="btn-nav-benchmark"
          className={`mode-tab-btn ${activeView === "benchmark" ? "active" : ""}`}
          onClick={() => setActiveView("benchmark")}
        >
          <span className="mode-badge-primary">02 EVALUATION</span>
          Frozen 30-Case Verification
        </button>
      </div>

      <div className="global-telemetry">
        <span>
          <i /> DETERMINISTIC FIRST
        </span>
        <span>VISUAL / 4 Hz FEATURE GRIDS</span>
        <span>ACOUSTIC / CROSS-CORRELATION</span>
        <span className="telemetry-state">
          {busy
            ? "ALIGNING MEDIA"
            : e
              ? `CASE ${e.id.slice(0, 12)}`
              : "READY FOR EVIDENCE"}
        </span>
      </div>

      {activeView === "benchmark" && (
        <BenchmarkHub
          onLoadDemo={(kind) => {
            setActiveView("workbench");
            setAppMode("comparator");
            analyze(kind);
          }}
        />
      )}

      {activeView === "workbench" && (
        <>
          {/* MODE 1: SINGLE-VIDEO INVESTIGATION (PRIMARY WORKFLOW) */}
          {appMode === "investigation" && (
            <section className="single-investigation-flow">
              {/* Launch Box if no active dossier or user wants to submit another */}
              <details className="intake-details" open={!dossier}>
                <summary>Start a new investigation</summary>
                <div className="single-launch-grid">
                  <div className="single-launch-left">
                    <div className="eyebrow">
                      MULTIMODAL VIDEO EVIDENCE DOSSIER
                    </div>
                    <h1>
                      Investigate footage from <span>ONE input.</span>
                    </h1>
                    <p>
                      Upload a reviewed technical demo. CONTEXT searches your
                      registered source catalog and local references, tests
                      correspondence, and asks Meta to explain only grounded
                      omissions. A missing match remains unresolved; this is not
                      an internet-wide video search.
                    </p>

                    {recentDossiers.length > 0 && (
                      <div
                        className="recent-dossiers-box"
                        style={{ marginTop: 20 }}
                      >
                        <div
                          className="card-eyebrow"
                          style={{ marginBottom: 8 }}
                        >
                          PREVIOUS INVESTIGATIONS
                        </div>
                        <div
                          style={{ display: "flex", flexWrap: "wrap", gap: 8 }}
                        >
                          {recentDossiers.slice(0, 4).map((d) => (
                            <button
                              key={d.id}
                              className="mode-tab-btn"
                              style={{ fontSize: 10, padding: "5px 10px" }}
                              onClick={() => fetchDossier(d.id)}
                            >
                              {d.caption
                                ? `“${d.caption.slice(0, 28)}...”`
                                : d.id.slice(0, 8)}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="launch-form-box">
                    <div className="input-mode-tabs">
                      <button
                        className={`input-mode-tab ${dossierInputMode === "upload" ? "active" : ""}`}
                        onClick={() => setDossierInputMode("upload")}
                        disabled={dossierBusy}
                      >
                        Upload Video
                      </button>
                      <button
                        className={`input-mode-tab ${dossierInputMode === "url" ? "active" : ""}`}
                        onClick={() => setDossierInputMode("url")}
                        disabled={dossierBusy}
                      >
                        Public Media URL
                      </button>
                    </div>

                    {dossierInputMode === "upload" ? (
                      <div className="launch-field">
                        <label htmlFor="investigation-video">
                          01 SELECT VIDEO (MP4, WEBM, MOV)
                        </label>
                        <input
                          id="investigation-video"
                          type="file"
                          accept="video/*"
                          disabled={dossierBusy}
                          onChange={(e) => {
                            setDossierFile(e.target.files?.[0] || null);
                          }}
                        />
                      </div>
                    ) : (
                      <div className="launch-field">
                        <label>01 SUPPORTED DIRECT MEDIA URL</label>
                        <input
                          type="url"
                          className="launch-input-text"
                          placeholder="Direct MP4/WebM/MOV URL on a supported host"
                          value={dossierUrl}
                          disabled={dossierBusy}
                          onChange={(e) => setDossierUrl(e.target.value)}
                        />
                      </div>
                    )}

                    {dossierFile && (
                      <p role="status">Attached: {dossierFile.name}</p>
                    )}
                    <div className="launch-field">
                      <label htmlFor="reference-video">
                        SOURCE RECORDING (OPTIONAL)
                      </label>
                      <input
                        id="reference-video"
                        type="file"
                        accept="video/*"
                        disabled={dossierBusy}
                        onChange={(event) =>
                          setReferenceFile(event.target.files?.[0] || null)
                        }
                      />
                      <p>
                        Provide a source for direct correspondence and context
                        review, or let CONTEXT search available sources.
                      </p>
                    </div>
                    <div className="launch-field">
                      <label>02 ACCOMPANYING CLAIM / CAPTION (OPTIONAL)</label>
                      <textarea
                        className="launch-input-textarea"
                        placeholder="e.g. This benchmark claims the faster command has no setup cost."
                        value={dossierCaption}
                        disabled={dossierBusy}
                        onChange={(e) => setDossierCaption(e.target.value)}
                      />
                    </div>

                    <div className="launch-actions">
                      <button
                        className="btn-primary-launch"
                        disabled={
                          dossierBusy ||
                          (dossierInputMode === "upload"
                            ? !dossierFile
                            : !dossierUrl.trim())
                        }
                        onClick={() => startInvestigation()}
                      >
                        {dossierBusy
                          ? "Investigating..."
                          : "Launch Investigation ↗"}
                      </button>
                    </div>
                  </div>
                </div>
              </details>
              {/* Running Progress Card */}
              {dossierBusy && (
                <div className="progress-box">
                  <div className="progress-header">
                    <div className="spinner" />
                    <strong>AUTONOMOUS INVESTIGATION IN PROGRESS</strong>
                    <button
                      className="quiet"
                      onClick={() => {
                        if (pollTimer.current !== null)
                          window.clearInterval(pollTimer.current);
                        setDossierBusy(false);
                        setDossierError(
                          "Stopped waiting in this view. Server analysis may continue; open the saved investigation to inspect its result.",
                        );
                      }}
                    >
                      Stop waiting
                    </button>
                  </div>
                  <div className="pipeline-steps">
                    <div
                      className={`pipeline-step ${dossierStage === "queued" || dossierStage === "analyzing" ? "active" : "done"}`}
                    >
                      <div className="step-num">1</div>
                      <span>Prepare & Frames</span>
                    </div>
                    <div
                      className={`pipeline-step ${dossierStage === "analyzing" ? "active" : dossierStage === "comparing" || dossierStage === "retrieving" || dossierStage === "verifying" || dossierStage === "complete" ? "done" : ""}`}
                    >
                      <div className="step-num">2</div>
                      <span>Reviewed source catalog</span>
                    </div>
                    <div
                      className={`pipeline-step ${dossierStage === "comparing" ? "active" : ["retrieving", "verifying", "complete"].includes(dossierStage) ? "done" : ""}`}
                    >
                      <div className="step-num">3</div>
                      <span>Source Video & Comparison</span>
                    </div>
                    <div
                      className={`pipeline-step ${dossierStage === "retrieving" ? "active" : dossierStage === "verifying" || dossierStage === "complete" ? "done" : ""}`}
                    >
                      <div className="step-num">4</div>
                      <span>Grounding gate</span>
                    </div>
                    <div
                      className={`pipeline-step ${dossierStage === "verifying" ? "active" : dossierStage === "complete" ? "done" : ""}`}
                    >
                      <div className="step-num">5</div>
                      <span>Bounded omission review</span>
                    </div>
                    <div
                      className={`pipeline-step ${dossierStage === "complete" ? "done" : ""}`}
                    >
                      <div className="step-num">6</div>
                      <span>Evidence Dossier</span>
                    </div>
                  </div>
                  <p style={{ color: "#8fa1ae", fontSize: 11, margin: 0 }}>
                    Matching source candidates and checking omission intervals
                    before model review...
                  </p>
                </div>
              )}

              {dossierError && (
                <div
                  className="error"
                  role="alert"
                  style={{ marginBottom: 24 }}
                >
                  {dossierError}
                </div>
              )}

              {/* Dossier Output Component */}
              {dossier && (
                <InvestigationDossier
                  key={dossier.id}
                  dossier={dossier}
                  onOpenComparator={openComparatorForCase}
                />
              )}
            </section>
          )}

          {/* MODE 2: PRELUDE ANTICIPATORY ROADWAY HAZARD LENS */}
          {appMode === "prelude" && (
            <PreludeStudio
              onBackToContext={() => setAppMode("investigation")}
            />
          )}

          {/* MODE 3: TWO-VIDEO COMPARISON (SUPPORTING CAPABILITY) */}
          {appMode === "comparator" && (
            <section className="comparator-flow">
              <div style={{ marginBottom: 16 }} hidden>
                <button
                  type="button"
                  className="chip active"
                  onClick={() => {
                    setAppMode("investigation");
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  &larr; Back to Single-Video Investigation Dossier
                </button>
              </div>
              <details className="media-intake" open={!e}>
                <summary>
                  <span>＋ MEDIA INTAKE</span>
                  <span>
                    {e
                      ? "Change source or published edit"
                      : "Configure evidence pair"}
                  </span>
                </summary>
                <section className="intro">
                  <div>
                    <div className="eyebrow">
                      CONTEXT / DEVELOPER TUTORIALS & BENCHMARK DEMOS
                    </div>
                    <h1>
                      See what the edit
                      <br />
                      <span>cut out.</span>
                    </h1>
                    <p>
                      Compare an edited tutorial or benchmark demo with its
                      source. Inspect the missing passage side by side. Meta can
                      explain only an omission supported by matched source
                      intervals.
                    </p>
                  </div>
                  <aside className="upload">
                    <div className="eyebrow">COMPARE TWO FOOTAGES</div>
                    <button
                      className="quiet single-input-entry"
                      onClick={() => setAppMode("investigation")}
                    >
                      Investigate a single edit ↗
                    </button>
                    <label>
                      01 <span>Original source</span>
                      <input
                        aria-label="Original source"
                        type="file"
                        accept="video/*"
                        disabled={busy || collectionBusy || reviewBusy !== null}
                        onChange={(x) =>
                          setOriginal(x.target.files?.[0] || null)
                        }
                      />
                    </label>
                    <label>
                      02 <span>Published edit</span>
                      <input
                        aria-label="Published edit"
                        type="file"
                        accept="video/*"
                        disabled={busy || collectionBusy || reviewBusy !== null}
                        onChange={(x) => setEdited(x.target.files?.[0] || null)}
                      />
                    </label>
                    <div className="actions">
                      <button
                        disabled={
                          busy ||
                          collectionBusy ||
                          reviewBusy !== null ||
                          !original ||
                          !edited
                        }
                        onClick={() => analyze()}
                      >
                        {busy ? "Analyzing frames…" : "Trace the edit ↗"}
                      </button>
                      <button
                        className="quiet"
                        disabled={busy || collectionBusy || reviewBusy !== null}
                        onClick={() => analyze("benchmark")}
                      >
                        Try benchmark omission →
                      </button>
                      <button
                        className="quiet"
                        disabled={busy || collectionBusy || reviewBusy !== null}
                        onClick={() => analyze("crop")}
                      >
                        Try spatial crop demo →
                      </button>
                    </div>
                    <details className="content-policy-note">
                      <summary>
                        Content admission · technical footage only
                      </summary>
                      <p>
                        Developer tutorials, software benchmarks and product
                        demos. Politics, elections, news, wartime footage and
                        real public figures are excluded. Unfamiliar files need
                        a full local operator review before analysis; selecting
                        a category does not approve a file.
                      </p>
                    </details>
                    <small>
                      Deterministic local processing · up to 10 min / 200 MB per
                      video
                    </small>
                  </aside>
                </section>
              </details>

              {error && (
                <div className="error" role="alert">
                  {error}
                </div>
              )}

              {e?.omission_evidence && (
                <p role="status">
                  {e.omission_evidence.status === "no material omission"
                    ? "no material omission"
                    : `${e.omission_evidence.omissions.length} matched internal omission(s)`}
                  {" · "}Matched media deletion does not establish changed
                  meaning. No match means insufficient evidence.
                </p>
              )}

              {busy && (
                <div role="status" className="progress">
                  PROBING MEDIA <span>→</span> EXTRACTING FRAMES <span>→</span>{" "}
                  RECONSTRUCTING SEQUENCE
                </div>
              )}

              <RecentInvestigations
                currentId={e?.id}
                disabled={busy || collectionBusy || reviewBusy !== null}
                onRestore={restoreEvidence}
                onBusy={setCollectionBusy}
              />
              <details className="collection-drawer" open={!e}>
                <summary>
                  <span>◫ REFERENCE LIBRARY</span>
                  <span>Index and match your source recordings</span>
                </summary>
                <SourceCollection
                  disabled={busy || reviewBusy !== null}
                  onBusy={setCollectionBusy}
                  onReset={resetInvestigation}
                  onEvidence={acceptEvidence}
                />
              </details>

              <section className="workbench">
                <div className="section-top">
                  <span className="eyebrow">
                    {e ? "EVIDENCE EXPLORER" : "AWAITING EVIDENCE"}
                  </span>
                  <div
                    style={{ display: "flex", gap: 8, alignItems: "center" }}
                  >
                    <span className="chip">
                      {e
                        ? `${Math.round(e.coverage * 100)}% VISUAL COVERAGE`
                        : "NO ANALYSIS LOADED"}
                    </span>
                    {e?.crop_analysis?.detected && (
                      <span
                        className="chip"
                        style={{
                          background: "rgba(34, 197, 94, 0.15)",
                          border: "1px solid rgba(34, 197, 94, 0.4)",
                          color: "#86efac",
                        }}
                      >
                        SPATIAL CROP (
                        {(
                          (e.crop_analysis.area_omitted_fraction || 0) * 100
                        ).toFixed(0)}
                        % CUT)
                      </span>
                    )}
                  </div>
                </div>
                {e?.audio_alignment && (
                  <details className="audio-evidence">
                    <summary>
                      Separate audio timing evidence ·{" "}
                      {e.audio_alignment.segments.length} matched passages
                    </summary>
                    <p>
                      These passages match the sound. Visual coverage above
                      describes images separately; matching sound does not
                      authenticate the footage.
                    </p>
                    {e.audio_alignment.reason && (
                      <p>{e.audio_alignment.reason}</p>
                    )}
                    {e.audio_alignment.segments.map((segment) => (
                      <p key={segment.id}>
                        Edit {time(segment.edited_start)}–
                        {time(segment.edited_end)} → Source{" "}
                        {time(segment.source_start ?? 0)}–
                        {time(segment.source_end ?? 0)}
                      </p>
                    ))}
                  </details>
                )}
                {e ? (
                  <ForensicPlayer
                    key={e.id}
                    media={e.media}
                    sourceRef={source}
                    editedRef={published}
                    segments={e.segments}
                    findings={e.findings}
                    groundedOmissions={e.omission_evidence}
                    editedDuration={e.edited.duration}
                    linked={sync}
                    onLink={(value) => {
                      setSelected(null);
                      setSync(value);
                    }}
                    onEditedUpdate={update}
                    onSourceUpdate={() => {
                      if (
                        selected &&
                        source.current &&
                        source.current.currentTime >= selected.source_end
                      )
                        source.current.pause();
                    }}
                    onReveal={reveal}
                    crop={e.crop_analysis}
                  />
                ) : (
                  <div className="empty-workstation">
                    <div className="empty-reticle">⌗</div>
                    <span className="micro-label">
                      EVIDENCE CHANNELS / OFFLINE
                    </span>
                    <h2>The full picture starts here.</h2>
                    <p>
                      Load a published edit and its source to inspect temporal
                      cuts and spatial reframing.
                    </p>
                    <div>
                      <span>01 / PUBLISHED EDIT</span>
                      <span>02 / ORIGINAL SOURCE</span>
                    </div>
                  </div>
                )}

                {e?.source.provenance && (
                  <div className="source-credit">
                    {e.source.provenance.attribution} ·{" "}
                    {e.source.provenance.license} · Controlled edit
                  </div>
                )}

                <div className="timeline">
                  <div className="section-top">
                    <h2>Reconstruct the sequence</h2>
                    <button
                      className="quiet"
                      disabled={!e}
                      onClick={() => {
                        setSelected(null);
                        setSync(!sync);
                      }}
                    >
                      {sync ? "⇄ Linked playback" : "↔ Independent playback"}
                    </button>
                  </div>
                  <div className="legend">
                    <span className="blue">■ Matched footage</span>
                    <span className="orange">■ Omitted from edit</span>
                    <span>■ Unresolved</span>
                  </div>
                  {e ? (
                    <>
                      <div className="track-row">
                        <span>ORIGINAL</span>
                        <div className="track">
                          {e.findings.map((f) => (
                            <div
                              key={f.id}
                              className={`finding-span ${f.kind} ${selected?.id === f.id ? "selected" : ""}`}
                              style={{
                                left: `${(f.source_start / e.source.duration) * 100}%`,
                                width: `${Math.max(0.5, ((f.source_end - f.source_start) / e.source.duration) * 100)}%`,
                              }}
                              onClick={() => reveal(f)}
                              title={`${f.kind} from ${f.source_start.toFixed(1)}s to ${f.source_end.toFixed(1)}s`}
                            />
                          ))}
                        </div>
                      </div>
                      <div className="track-row">
                        <span>EDITED</span>
                        <div className="track">
                          {e.segments.map((s) => (
                            <div
                              key={s.id}
                              className={`segment-span ${s.kind}`}
                              style={{
                                left: `${(s.edited_start / e.edited.duration) * 100}%`,
                                width: `${Math.max(0.5, ((s.edited_end - s.edited_start) / e.edited.duration) * 100)}%`,
                              }}
                              onClick={() => seek(s)}
                              title={`${s.kind} at ${s.edited_start.toFixed(1)}s`}
                            />
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <p className="no-tracks">
                      Load two videos to visualize the sequence diff.
                    </p>
                  )}
                </div>

                {/* Spatial Crop Analysis Card */}
                {e?.crop_analysis?.detected && (
                  <div
                    className="crop-analysis-card"
                    style={{
                      marginTop: 24,
                      padding: 20,
                      borderRadius: 6,
                      background: "#162028",
                      border: "1px solid #22c55e",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        marginBottom: 8,
                      }}
                    >
                      <span
                        style={{
                          background: "#22c55e",
                          color: "#0f172a",
                          fontSize: 10,
                          fontWeight: 800,
                          padding: "2px 8px",
                          borderRadius: 4,
                          letterSpacing: "0.05em",
                        }}
                      >
                        SPATIAL CROP DETECTED
                      </span>
                      <span style={{ fontSize: 13, color: "#94a3b8" }}>
                        Multi-scale spatial geometry · measured bounds
                      </span>
                    </div>
                    <h3
                      style={{
                        margin: "4px 0 8px 0",
                        fontSize: 16,
                        color: "#f8fafc",
                      }}
                    >
                      Visual reframe ·{" "}
                      {(
                        (e.crop_analysis.area_omitted_fraction || 0) * 100
                      ).toFixed(0)}
                      % peripheral context omitted
                    </h3>
                    <p
                      style={{
                        margin: "0 0 10px 0",
                        fontSize: 13,
                        color: "#cbd5e1",
                        lineHeight: 1.5,
                      }}
                    >
                      {e.crop_analysis.explanation}
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {e.crop_analysis.omitted_margins?.map((m, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: "3px 8px",
                            background: "rgba(239, 68, 68, 0.15)",
                            border: "1px solid rgba(239, 68, 68, 0.4)",
                            color: "#fca5a5",
                            borderRadius: "4px",
                            fontSize: "12px",
                          }}
                        >
                          Omitted {m.name} margin ({m.width}×{m.height}px)
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Findings list */}
                {e && e.findings.length > 0 && (
                  <div className="findings-section" style={{ marginTop: 24 }}>
                    <div className="section-top">
                      <h2>Detected intervals ({e.findings.length})</h2>
                    </div>
                    <div className="findings-grid">
                      {e.findings.map((f) => (
                        <div
                          key={f.id}
                          className={`finding-item ${selected?.id === f.id ? "active" : ""}`}
                          onClick={() => reveal(f)}
                        >
                          <div className="finding-kind">
                            {f.kind === "spatial_crop_reframe"
                              ? "SPATIAL CROP / REFRAME"
                              : f.kind.toUpperCase()}
                          </div>
                          <div className="finding-time">
                            {f.kind === "spatial_crop_reframe"
                              ? `Peripheral context omitted: ${((f.area_omitted_fraction || e.crop_analysis?.area_omitted_fraction || 0) * 100).toFixed(0)}% cut`
                              : `Source: ${time(f.source_start)} – ${time(f.source_end)}`}
                          </div>
                          <div
                            className="finding-action-row"
                            style={{ marginTop: 8 }}
                          >
                            {f.kind === "spatial_crop_reframe" ? (
                              <span
                                style={{
                                  fontSize: 10,
                                  color: "#86efac",
                                  background: "rgba(34, 197, 94, 0.15)",
                                  padding: "3px 6px",
                                  borderRadius: 3,
                                }}
                              >
                                Spatial geometry measured
                              </span>
                            ) : (
                              <button
                                className="quiet"
                                style={{ fontSize: 10, padding: "4px 8px" }}
                                disabled={
                                  reviewBusy === f.id ||
                                  !e.omission_evidence?.omissions.some(
                                    (item) =>
                                      Math.abs(
                                        item.source_start - f.source_start,
                                      ) <= 0.5 &&
                                      Math.abs(
                                        item.source_end - f.source_end,
                                      ) <= 0.5,
                                  )
                                }
                                onClick={(ev) => {
                                  ev.stopPropagation();
                                  reviewFinding(f);
                                }}
                              >
                                {reviewBusy === f.id
                                  ? "Reviewing..."
                                  : "Semantic Review ↗"}
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {reviewError && (
                  <p className="error" role="alert">
                    {reviewError}
                  </p>
                )}

                {review && (
                  <div
                    className="semantic-review-card"
                    style={{
                      marginTop: 24,
                      background: "#1a2126",
                      padding: 20,
                      borderRadius: 6,
                      border: "1px solid #364855",
                    }}
                  >
                    <GroundingBadge
                      review={review}
                      finding={e?.findings.find(
                        (f) => f.id === review.finding_id,
                      )}
                      grounded={Boolean(
                        e?.omission_evidence?.omissions.some((o) => {
                          const f = e.findings.find(
                            (item) => item.id === review.finding_id,
                          );
                          return (
                            f &&
                            Math.abs(o.source_start - f.source_start) <= 0.5 &&
                            Math.abs(o.source_end - f.source_end) <= 0.5
                          );
                        }),
                      )}
                    />
                    <h3>Bounded semantic review</h3>
                    <p>
                      <strong>Possible Effect:</strong>{" "}
                      {review.interpretation.possible_effect}
                    </p>
                    <p>
                      <strong>Uncertainty:</strong>{" "}
                      {review.interpretation.uncertainty}
                    </p>
                    {review.interpretation.observations.map((obs, i) => (
                      <div key={i} style={{ marginTop: 8, fontSize: 12 }}>
                        <span>• {obs.text}</span>
                        {obs.citations.map((c, j) => (
                          <button
                            key={j}
                            className="quiet"
                            style={{
                              fontSize: 9,
                              marginLeft: 8,
                              padding: "2px 6px",
                            }}
                            onClick={() => inspectCitation(c)}
                          >
                            Seek {c.media} @ {time(c.media_start)}
                          </button>
                        ))}
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </section>
          )}
        </>
      )}

      <footer>
        <span>CONTEXT Multimodal Video Evidence Workstation</span>
        <span>Meta Global AI Hackathon • November 2026</span>
      </footer>
    </main>
  );
}

const root = document.getElementById("root");
if (root) createRoot(root).render(<App />);
