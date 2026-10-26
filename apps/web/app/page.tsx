"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Evidence = {
  memory_id: string;
  source_id: string;
  date: string;
  title: string;
  summary: string;
  theme: string;
};

type Finding = {
  id: string;
  project_title: string;
  hypothesis: string;
  earlier_theme: string;
  later_theme: string;
  start_date: string;
  end_date: string;
  supporting_evidence: Evidence[];
  counter_evidence: Evidence[];
  uncertainty: string[];
  extraction_provider: string;
  extraction_model: string | null;
  api_usage?: { requests: number; cache_hits: number; estimated_usd: number; cumulative_estimated_usd: number };
};

type Session = { session_id: string; finding: Finding; stage: string; first_question: string };
type Artifact = { title: string; kind: string; body: string; source_ids: string[]; based_on_insight: string };

const API = process.env.NEXT_PUBLIC_THREAD_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API}${path}`, {
      method: body ? "POST" : "GET",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("THREAD’s local engine is not connected. Start the backend, then try again.");
  }
  const payload = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(" ")
      : payload.detail;
    throw new Error(typeof detail === "string" ? detail : "The request could not be completed.");
  }
  return payload as T;
}

function dateLabel(value: string) {
  return new Intl.DateTimeFormat("en", { month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`));
}

export default function Home() {
  const [provider, setProvider] = useState<"fixture" | "meta">("fixture");
  const [session, setSession] = useState<Session | null>(null);
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [stage, setStage] = useState<"welcome" | "evidence" | "challenge" | "confirm" | "created">("welcome");
  const [context, setContext] = useState("");
  const [interviewQuestion, setInterviewQuestion] = useState("");
  const [interviewStep, setInterviewStep] = useState(1);
  const [interpretation, setInterpretation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const started = useRef(false);

  const discover = useCallback(async (selected: "fixture" | "meta" = "fixture") => {
    setBusy(true);
    setError("");
    setArtifact(null);
    try {
      const result = await request<Session>("/api/discover", { provider: selected });
      setSession(result);
      setProvider(selected);
      setStage("welcome");
      setContext("");
      setInterviewQuestion(result.first_question);
      setInterviewStep(1);
      setInterpretation("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Discovery failed.");
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void discover("fixture");
  }, [discover]);

  async function saveChallenge() {
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      const result = await request<{ stage: string; next_question?: string; context?: string }>(
        `/api/sessions/${session.session_id}/challenge`,
        { answer: context },
      );
      if (result.stage === "interviewing" && result.next_question) {
        setInterviewQuestion(result.next_question);
        setInterviewStep(2);
        setContext("");
        return;
      }
      const finalContext = result.context ?? context;
      setContext(finalContext);
      setInterpretation(`The project did not leave ${finding?.earlier_theme ?? "its original purpose"} behind. It made ${finding?.later_theme ?? "its newer direction"} the lead, while keeping the earlier need in view.`);
      setStage("confirm");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save your perspective.");
    } finally {
      setBusy(false);
    }
  }

  async function confirmInsight() {
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      await request(`/api/sessions/${session.session_id}/confirm`, { interpretation });
      const result = await request<{ artifact: Artifact }>(`/api/sessions/${session.session_id}/artifact`, { kind: "direction-note" });
      setArtifact(result.artifact);
      setStage("created");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not confirm this insight.");
    } finally {
      setBusy(false);
    }
  }

  const finding = session?.finding;
  const sources = finding ? [...finding.supporting_evidence, ...finding.counter_evidence] : [];

  return (
    <main className="shell">
      <aside className="rail" aria-label="Primary navigation">
        <div className="brand-mark" aria-label="THREAD">t<span>.</span></div>
        <button className="rail-button active" aria-label="Discover" title="Discover">⌕</button>
        <button className="rail-button" aria-label="Projects" title="Projects" onClick={() => void discover("fixture")}>◫</button>
        <div className="rail-bottom"><span className="avatar">A</span></div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="wordmark">THREAD<span className="wordmark-dot">.</span></div>
          <div className="topbar-center"><span className="live-dot" /> PRIVATE WORKSPACE <span className="topbar-separator">/</span> CREATIVE ARCHIVE</div>
          <div className="topbar-right">
            <label className="provider-label" htmlFor="provider">MODEL</label>
            <select id="provider" value={provider} onChange={(event) => setProvider(event.target.value as "fixture" | "meta")}>
              <option value="fixture">Fixture · no API cost</option>
              <option value="meta">Muse Spark · API</option>
            </select>
            <span className="avatar small">A</span>
          </div>
        </header>

        <div className="content">
          <div className="breadcrumb"><span>PROJECTS</span><span className="slash">/</span><span>{finding?.project_title.toUpperCase() ?? "CREATIVE ARCHIVE"}</span></div>

          {!finding && (
            <section className="welcome-panel">
              <div className="eyebrow">A RESEARCH JOURNAL FOR YOUR WORK</div>
              <h1>See what your work<br />has been becoming.</h1>
              <p>THREAD follows ideas through your dated creative artifacts, then makes the evidence and uncertainty visible for you to inspect.</p>
              <button className="button primary" onClick={() => void discover(provider)} disabled={busy}>{busy ? "Opening the archive…" : "Open the sample project"}<span>↗</span></button>
              <div className="welcome-note"><span className="tiny-spark">✳</span> Synthetic sample data · nothing leaves this workspace</div>
            </section>
          )}

          {finding && (
            <>
              <div className="project-heading">
                <div>
                  <div className="eyebrow">PROJECT STUDY <span className="study-number">NO. 01</span></div>
                  <h1>{finding.project_title}</h1>
                  <p className="project-meta">A dated collection of field notes, sketches, interviews, and drafts <span>·</span> 2022—2025</p>
                </div>
                <button className="text-button" onClick={() => void discover(provider)} disabled={busy}>↻ <span>Re-read archive</span></button>
              </div>

              <div className="stage-line" aria-label="Workflow progress">
                {["Discover", "Inspect", "Interview", "Confirm", "Create"].map((label, index) => {
                  const current = stage === "welcome" ? 0 : stage === "evidence" ? 1 : stage === "challenge" ? 2 : stage === "confirm" ? 3 : 4;
                  return <div className={`stage-item ${index <= current ? "reached" : ""} ${index === current ? "current" : ""}`} key={label}><span>{String(index + 1).padStart(2, "0")}</span>{label}</div>;
                })}
              </div>

              {(stage === "welcome" || stage === "evidence") && (
                <>
                  <section className="finding-intro">
                    <div className="finding-label"><span className="hypothesis-icon">✳</span> A THREAD TO LOOK CLOSER AT <span className="confidence-label">HYPOTHESIS</span></div>
                    <h2>{finding.earlier_theme} <span className="arrow">→</span> {finding.later_theme}</h2>
                    <p className="finding-statement">{finding.hypothesis}</p>
                    <div className="finding-footer"><span>{dateLabel(finding.start_date)} — {dateLabel(finding.end_date)}</span><span className="source-count">{finding.supporting_evidence.length + finding.counter_evidence.length} EVIDENCE FRAGMENTS</span></div>
                  </section>

                  <section className="timeline-section">
                    <div className="section-heading"><div><div className="eyebrow">THE WORK, OVER TIME</div><h3>Follow the shift</h3></div><span className="method-note">THEMES FROM {finding.extraction_provider === "meta" ? finding.extraction_model?.toUpperCase() ?? "META MODEL" : "SYNTHETIC FIXTURE"}</span></div>
                    <div className="timeline">
                      <div className="timeline-rule" />
                      {finding.supporting_evidence.map((item, index) => (
                        <article className={`timeline-entry entry-${index % 3}`} key={`${item.source_id}-${item.theme}`}>
                          <span className="timeline-node" />
                          <div className="entry-date">{dateLabel(item.date)}</div>
                          <div className="entry-card"><div className="entry-top"><span className="entry-type">{item.title.split("—")[0].trim().toUpperCase()}</span><span className="entry-theme">{item.theme}</span></div><h4>{item.title}</h4><p>{item.summary}</p><span className="source-id">SOURCE · {item.source_id}</span></div>
                        </article>
                      ))}
                    </div>
                  </section>

                  <section className="evidence-grid" id="evidence">
                    <div className="evidence-column supporting"><div className="evidence-title"><span className="evidence-mark">+</span><div><div className="eyebrow">WHAT SUPPORTS THE SHIFT</div><h3>Signals in the work</h3></div></div>
                      {finding.supporting_evidence.slice(0, 3).map((item) => <div className="evidence-row" key={`s-${item.source_id}`}><div className="evidence-date">{dateLabel(item.date)}</div><div><h4>{item.title}</h4><p>{item.summary}</p><span className="source-id">{item.source_id} · {item.theme}</span></div></div>)}
                    </div>
                    <div className="evidence-column counter"><div className="evidence-title"><span className="evidence-mark">↗</span><div><div className="eyebrow">WHAT COMPLICATES IT</div><h3>The thread continues</h3></div></div>
                      {finding.counter_evidence.map((item) => <div className="evidence-row" key={`c-${item.source_id}`}><div className="evidence-date">{dateLabel(item.date)}</div><div><h4>{item.title}</h4><p>{item.summary}</p><span className="source-id">{item.source_id} · still includes {item.theme}</span></div></div>)}
                      <div className="counter-reading">This may be an expansion of the project’s purpose, not a replacement of its original goal.</div>
                    </div>
                  </section>

                  <section className="uncertainty"><span className="uncertainty-mark">?</span><div><div className="eyebrow">WHAT THIS CANNOT KNOW</div><p>{finding.uncertainty.join(" ")}</p></div></section>

                  {stage === "welcome" && <div className="actions"><span className="action-caption">A pattern is only useful if it fits your experience.</span><button className="button secondary" onClick={() => setStage("evidence")}>Inspect the evidence <span>↓</span></button><button className="button primary" onClick={() => setStage("challenge")}>Add your perspective <span>↗</span></button></div>}
                  {stage === "evidence" && <div className="actions"><button className="button quiet" onClick={() => setStage("welcome")}>← Back to finding</button><button className="button primary" onClick={() => setStage("challenge")}>Challenge or add context <span>↗</span></button></div>}
                </>
              )}

              {stage === "challenge" && (
                <section className="reflection-panel">
                  <div className="eyebrow">ECHO INTERVIEW · QUESTION {interviewStep} OF 2</div>
                  <h2>{interviewQuestion}</h2>
                  <p>THREAD has found a possible change in the dated work. Your answers can correct the interpretation before it becomes an insight.</p>
                  <label htmlFor="context" className="field-label">Your answer, in your own words</label>
                  <textarea id="context" value={context} onChange={(event) => setContext(event.target.value)} placeholder="Add the context only you would know…" maxLength={1200} />
                  <div className="field-footer"><span>Kept in this local demo session</span><span>{context.length}/1200</span></div>
                  <div className="actions"><button className="button quiet" onClick={() => setStage("evidence")}>← Review evidence</button><button className="button primary" onClick={() => void saveChallenge()} disabled={busy || context.trim().length < 12}>{busy ? "Saving your answer…" : interviewStep === 1 ? "Answer & continue" : "Review interpretation"}<span>↗</span></button></div>
                </section>
              )}

              {stage === "confirm" && (
                <section className="reflection-panel confirm-panel">
                  <div className="eyebrow">A HUMAN-CONFIRMED INSIGHT STARTS HERE</div>
                  <h2>Put the shift in your words.</h2>
                  <div className="context-quote"><span>YOUR CONTEXT</span><p>“{context}”</p></div>
                  <label htmlFor="interpretation" className="field-label">Revise the interpretation, or keep this draft</label>
                  <textarea id="interpretation" value={interpretation} onChange={(event) => setInterpretation(event.target.value)} maxLength={600} />
                  <div className="confirmation-boundary"><span>✓</span><p>Only after you confirm will THREAD make a direction note. It will include your wording and the source trail.</p></div>
                  <div className="actions"><button className="button quiet" onClick={() => setStage("evidence")}>← Review evidence</button><button className="button primary" onClick={() => void confirmInsight()} disabled={busy || interpretation.trim().length < 12}>{busy ? "Creating from confirmed insight…" : "Confirm & create direction note"}<span>↗</span></button></div>
                </section>
              )}

              {stage === "created" && artifact && (
                <section className="artifact-panel">
                  <div className="eyebrow">CREATED FROM YOUR CONFIRMED INSIGHT</div>
                  <div className="artifact-paper"><div className="artifact-stamp">THREAD · DIRECTION NOTE</div><h2>{artifact.title}</h2><pre>{artifact.body}</pre><div className="artifact-sources">EVIDENCE TRAIL <span>{artifact.source_ids.join(" · ")}</span></div></div>
                  <div className="artifact-footer"><span>Insight {artifact.based_on_insight} · grounded in {artifact.source_ids.length} dated sources</span><button className="text-button" onClick={() => setStage("evidence")}>Return to evidence ↗</button></div>
                </section>
              )}
            </>
          )}

          {error && <div className="error-banner" role="alert"><span>!</span><div><strong>Could not continue</strong><p>{error}</p><button onClick={() => void discover(provider)}>Try again</button></div></div>}

          <footer className="footer"><span>THREAD IS A RESEARCH PARTNER, NOT AN AUTHORITY.</span><span>{finding ? `${sources.length} FRAGMENTS · ${finding.extraction_provider.toUpperCase()} EXTRACTION` : "SYNTHETIC SAMPLE · LOCAL DEMO"}</span></footer>
        </div>
      </section>
    </main>
  );
}
