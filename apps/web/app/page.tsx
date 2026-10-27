"use client";

import { useEffect, useRef, useState } from "react";
import { completedActions, simulateAction } from "@/lib/simulate";
import { SAMPLE_SKILL, type SkillModel } from "@/lib/skill-model";
import { processToSkill } from "@/lib/process-to-skill";

type Mode = "teach" | "do" | "simulate";
type LearnedProcess = {
  task_summary: string;
  objects: { id: string; label: string; visual_description: string }[];
  states: { id: string; description: string; observable_facts: string[] }[];
  transitions: {
    id: string;
    action: string;
    object_ids: string[];
    from_state: string;
    to_state: string;
    preconditions: string[];
    postconditions: string[];
    evidence: { start_seconds: number; end_seconds: number; observation: string }[];
  }[];
  ordering_observations: { before_transition_id: string; after_transition_id: string; evidence: { start_seconds: number; end_seconds: number; observation: string }[] }[];
  uncertainties: string[];
  _run?: { model?: string; usage?: { input_tokens?: number; output_tokens?: number }; source?: { duration_seconds?: number } };
  _validation?: string;
};
type LearnerObservation = {
  events: { time_seconds: number; action: string; state_id: string; assessment: "consistent" | "divergent" | "unclear"; object_ids: string[]; evidence: string }[];
  divergences: { time_seconds: number; process_difference: string; object_ids: string[]; evidence: string }[];
  recovery_status: "no_divergence_observed" | "underway" | "recovered" | "unclear";
  uncertainties: string[];
  _run?: { model?: string; usage?: { input_tokens?: number; output_tokens?: number } };
};

function AssemblyView({ state, model }: { state: string[]; model: SkillModel }) {
  if (model.status === "learned-from-demonstration") {
    const stateNames = (model.states ?? []).filter((item) => state.includes(item.id));
    return <div className="learned-state-view"><div className="eyebrow">STATE OBSERVED IN THE DEMONSTRATION</div>{stateNames.length ? stateNames.map((item) => <div className="learned-state-chip" key={item.id}><span>◉</span>{item.label}</div>) : <div className="learned-state-chip muted">No matching state in this candidate model</div>}<p>State transitions are shown as the model described them; this view does not simulate physical forces or geometry.</p></div>;
  }
  const washer = state.includes("washer_seated");
  const bracket = state.includes("bracket_mounted");
  const bolt = state.includes("fastener_inserted");
  return (
    <div className="assembly-scene" aria-label="Illustrative assembly state">
      <div className="scene-glow" />
      <div className="part-label label-bracket">SUPPORT BRACKET</div>
      <div className="part-label label-washer">SPACER RING</div>
      <div className="part-label label-base">MOUNTING BASE</div>
      <div className="assembly">
        {bolt && <div className="bolt-part"><span /></div>}
        {bracket && <div className="bracket-part"><span /></div>}
        {washer && <div className="washer-part"><span /></div>}
        <div className="base-part"><span /></div>
      </div>
      <div className="scene-caption">STATE VIEW · PROCEDURAL, NOT PHYSICS</div>
    </div>
  );
}

function VideoPreview({ src }: { src: string }) {
  return <video className="video-preview" src={src} controls playsInline />;
}

export default function Home() {
  const [mode, setMode] = useState<Mode>("simulate");
  const [model, setModel] = useState<SkillModel>(SAMPLE_SKILL);
  const [state, setState] = useState<string[]>(model.initialState);
  const [result, setResult] = useState<ReturnType<typeof simulateAction> | null>(null);
  const [mediaUrl, setMediaUrl] = useState("");
  const [sourceFile, setSourceFile] = useState<File | null>(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [narration, setNarration] = useState("");
  const [learnedProcess, setLearnedProcess] = useState<LearnedProcess | null>(null);
  const [activeProcess, setActiveProcess] = useState<LearnedProcess | null>(null);
  const [candidateReviewed, setCandidateReviewed] = useState(false);
  const [learnError, setLearnError] = useState("");
  const [learning, setLearning] = useState(false);
  const [learnerFile, setLearnerFile] = useState<File | null>(null);
  const [learnerUrl, setLearnerUrl] = useState("");
  const [observation, setObservation] = useState<LearnerObservation | null>(null);
  const [observeError, setObserveError] = useState("");
  const [observing, setObserving] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const learnerInput = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => () => {
    if (mediaUrl.startsWith("blob:")) URL.revokeObjectURL(mediaUrl);
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, [mediaUrl]);

  useEffect(() => () => {
    if (learnerUrl.startsWith("blob:")) URL.revokeObjectURL(learnerUrl);
  }, [learnerUrl]);

  useEffect(() => {
    if (cameraOn && videoRef.current && streamRef.current) videoRef.current.srcObject = streamRef.current;
  }, [cameraOn]);

  function resetSimulation() {
    setState(model.initialState);
    setResult(null);
  }

  function tryAction(actionId: string) {
    const next = simulateAction(model, state, actionId);
    setResult(next);
    if (next.accepted) setState(next.state);
  }

  async function startCamera() {
    setCameraError("");
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError("Camera access is unavailable here. Open SHOWME on localhost or HTTPS.");
      return;
    }
    try {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      setCameraOn(true);
    } catch {
      setCameraError("Camera permission was not granted. You can still inspect the sample procedure.");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOn(false);
  }

  function loadReviewedCandidate() {
    if (!learnedProcess) return;
    const nextModel = processToSkill(learnedProcess);
    setActiveProcess(learnedProcess);
    setModel(nextModel);
    setState(nextModel.initialState);
    setResult(null);
    setMode("simulate");
  }

  function chooseLearnerVideo(file?: File) {
    if (!file) return;
    setLearnerFile(file);
    setLearnerUrl((previous) => {
      if (previous.startsWith("blob:")) URL.revokeObjectURL(previous);
      return URL.createObjectURL(file);
    });
    setObservation(null);
    setObserveError("");
  }

  async function observeLearnerVideo() {
    if (!activeProcess || !learnerFile) return;
    setObserving(true);
    setObservation(null);
    setObserveError("");
    const form = new FormData();
    form.set("video", learnerFile);
    form.set("process_json", JSON.stringify(activeProcess));
    try {
      const api = process.env.NEXT_PUBLIC_SHOWME_API_URL ?? "http://localhost:8000";
      const response = await fetch(`${api}/api/skills/observe`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "SHOWME could not observe this learner video.");
      setObservation(payload.observation as LearnerObservation);
    } catch (error) {
      setObserveError(error instanceof Error ? error.message : "SHOWME could not reach the local observation service.");
    } finally {
      setObserving(false);
    }
  }

  function chooseVideo(file?: File) {
    if (!file) return;
    setSourceFile(file);
    setMediaUrl((previous) => {
      if (previous.startsWith("blob:")) URL.revokeObjectURL(previous);
      return URL.createObjectURL(file);
    });
    setLearnedProcess(null);
    setLearnError("");
  }

  async function learnFromVideo() {
    if (!sourceFile) return;
    setLearning(true);
    setLearnError("");
    setLearnedProcess(null);
    const form = new FormData();
    form.set("video", sourceFile);
    form.set("narration", narration);
    try {
      const api = process.env.NEXT_PUBLIC_SHOWME_API_URL ?? "http://localhost:8000";
      const response = await fetch(`${api}/api/skills/learn`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "SHOWME could not learn from this video.");
      setLearnedProcess(payload.process as LearnedProcess);
      setCandidateReviewed(false);
    } catch (error) {
      setLearnError(error instanceof Error ? error.message : "SHOWME could not reach the local learning service.");
    } finally {
      setLearning(false);
    }
  }

  const done = completedActions(model, state);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#home" aria-label="SHOWME home"><span className="brand-symbol">s</span><span>SHOWME</span></a>
        <div className="sidebar-label">YOUR WORKSPACE</div>
        <button className={`nav-item ${mode === "teach" ? "selected" : ""}`} onClick={() => setMode("teach")}><span className="nav-icon">◉</span> Teach <span className="nav-step">01</span></button>
        <button className={`nav-item ${mode === "do" ? "selected" : ""}`} onClick={() => setMode("do")}><span className="nav-icon">◎</span> Do <span className="nav-step">02</span></button>
        <button className={`nav-item ${mode === "simulate" ? "selected" : ""}`} onClick={() => setMode("simulate")}><span className="nav-icon">⌁</span> Simulate <span className="nav-step">03</span></button>
        <div className="sidebar-bottom"><span className="local-indicator" /> LOCAL PROTOTYPE</div>
      </aside>

      <section className="main-panel">
        <header className="topbar">
          <div className="breadcrumbs">WORKSPACE <span>/</span> {mode.toUpperCase()}</div>
          <div className="model-status"><span className="status-dot" /> {model.status === "learned-from-demonstration" ? "REVIEWED SKILL MODEL" : "ILLUSTRATIVE SKILL FIXTURE"}</div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">SHOWME · {mode === "teach" ? "CAPTURE A DEMONSTRATION" : mode === "do" ? "GUIDED EXECUTION" : "EXPLORE A SKILL MODEL"}</div>
              <h1>{mode === "teach" ? <>Show us<br /><em>how it works.</em></> : mode === "do" ? <>Let’s do<br /><em>this together.</em></> : <>A procedure,<br /><em>in motion.</em></>}</h1>
              <p className="lead">{mode === "teach" ? "Record a demonstration and narrate the details that matter. SHOWME will turn the observed steps into a skill model." : mode === "do" ? "Bring a learner recording beside the reviewed process. SHOWME compares clips and returns timestamped evidence; the live camera remains preview-only." : "Try a proposed action against the same process model. Confirmed fixture rules can block a step; learned traces only show what was observed."}</p>
            </div>
            <div className="product-thesis"><span>THE IDEA</span><p>Tutorials can show you what to do.<br /><strong>They can’t see what you’re doing.</strong></p></div>
          </div>

          <div className="mode-tabs" role="tablist" aria-label="SHOWME modes">
            {(["teach", "do", "simulate"] as const).map((tab, index) => <button key={tab} role="tab" aria-selected={mode === tab} className={mode === tab ? "active" : ""} onClick={() => setMode(tab)}><span>0{index + 1}</span>{tab[0].toUpperCase() + tab.slice(1)}</button>)}
          </div>

          {mode === "simulate" && <div className="work-grid">
            <section className="card simulation-card">
              <div className="card-heading"><div><div className="eyebrow">THE SHARED SKILL MODEL</div><h2>{model.title}</h2></div><button className="text-action" onClick={resetSimulation}>↺ Reset</button></div>
              <div className="fixture-note"><span>i</span><p>{model.status === "learned-from-demonstration" ? "This reviewed model represents one observed trace. It does not prove the process is complete or that another order is impossible." : "This is an illustrative fixture to make the process model tangible. It has not been learned from a demonstration yet."}</p></div>
              <AssemblyView state={state} model={model} />
              <div className="state-summary"><div><span className="eyebrow">CURRENT STATE</span><strong>{done.length === model.actions.length ? "Assembly complete" : `${done.length} of ${model.actions.length} actions complete`}</strong></div><span className="state-pip"><i className={result?.accepted === false ? "warning" : ""} /></span></div>
              {result && <div className={`result-callout ${result.accepted ? "success" : result.kind === "unobserved" ? "unobserved" : "blocked"}`} role="status"><span className="result-icon">{result.accepted ? "✓" : result.kind === "unobserved" ? "?" : "!"}</span><div><strong>{result.accepted ? "OBSERVED TRANSITION" : result.kind === "unobserved" ? "ALTERNATIVE NOT OBSERVED" : "CONFIRMED REQUIREMENT NOT MET"}</strong><p>{result.message}</p>{!result.accepted && <small>{result.kind === "unobserved" ? "Evidence needed: another demonstration or human confirmation." : `Missing state: ${result.missing.map((item) => item.replaceAll("_", " ")).join(", ")}`}<br />{result.action.recovery}</small>}</div></div>}
              <div className="what-if"><span className="what-if-mark">?</span><div><strong>What if I do this next?</strong><p>{model.status === "learned-from-demonstration" ? "Choose an action. SHOWME advances through an evidenced transition or tells you this alternative was not observed." : "Choose an action. SHOWME applies the fixture’s stated requirements and previews the resulting process state."}</p></div></div>
              <div className="action-list">{model.actions.map((action, index) => {
                const finished = action.produces.every((condition) => state.includes(condition));
                return <button className={`action-option ${finished ? "completed" : ""}`} key={action.id} onClick={() => tryAction(action.id)}><span className="action-number">{finished ? "✓" : `0${index + 1}`}</span><span><strong>{action.label}</strong><small>{model.status === "learned-from-demonstration" ? `Observed from: ${action.fromState?.replaceAll("_", " ") ?? "unknown state"}` : `Requires ${action.requires.map((condition) => condition.replaceAll("_", " ")).join(" + ")}`}</small></span><span className="action-arrow">↗</span></button>;
              })}</div>
            </section>
            <aside className="card model-card">
              <div className="eyebrow">PROCESS MODEL</div><h3>What the skill knows</h3><p className="model-copy">A compact set of objects, states, and action constraints. Teach will eventually replace this fixture with a model inferred from a real demonstration.</p>
              <div className="model-section"><span>OBJECTS</span>{model.objects.map((object) => <div className="model-row" key={object.id}><i className={`object-swatch ${object.color}`} /><span>{object.name}</span><small>{state.some((item) => item.startsWith(object.id) || item.includes(object.id)) ? "IN USE" : "READY"}</small></div>)}</div>
              <div className="model-section"><span>{model.status === "learned-from-demonstration" ? "OBSERVED TRANSITIONS" : "CONFIRMED DEPENDENCY"}</span><div className="dependency-flow">{model.actions.map((action, index) => <div className={state.includes(action.toState ?? action.produces[0]) ? "on" : ""} key={action.id}>{action.label}{model.status === "learned-from-demonstration" && <small className="observed-edge">{action.fromState?.replaceAll("_", " ")} → {action.toState?.replaceAll("_", " ")}</small>}{index < model.actions.length - 1 && <b>↓</b>}</div>)}</div>{model.status === "learned-from-demonstration" && <p className="model-copy model-caveat">Observed order is evidence about this clip, not proof of a universal requirement.</p>}</div>
              <div className="model-foot"><span className="status-dot" /> {model.status === "learned-from-demonstration" ? "Transitions grounded in one reviewed trace" : "Deterministic illustrative state fixture"}</div>
            </aside>
          </div>}

          {mode === "teach" && <div className="work-grid teach-grid">
            <section className="card capture-card"><div className="card-heading"><div><div className="eyebrow">STEP 01 · PROVIDE A DEMONSTRATION</div><h2>Show it once.</h2></div><span className="capture-icon">↥</span></div>
              {mediaUrl ? <VideoPreview src={mediaUrl} /> : <button className="upload-drop" onClick={() => fileInput.current?.click()}><span className="upload-symbol">↥</span><strong>Choose a demonstration video</strong><small>MP4 or MOV · a short, clear view of the task</small><span className="outline-button">Browse files</span></button>}
              <input ref={fileInput} type="file" accept="video/*" hidden onChange={(event) => chooseVideo(event.target.files?.[0])} />
              {mediaUrl && <button className="text-action replace-video" onClick={() => fileInput.current?.click()}>Choose a different video</button>}
              <label className="field-label" htmlFor="narration">WHAT SHOULD SHOWME NOTICE?</label><textarea id="narration" value={narration} onChange={(event) => setNarration(event.target.value)} placeholder="Narrate while you demonstrate: ‘The spacer goes under the bracket…’" />
              <div className="capture-actions"><span className="small-note">Choosing Learn uploads this clip to Meta for inference and may use API credits.</span><button className="primary-button" disabled={!sourceFile || learning} onClick={() => void learnFromVideo()}>{learning ? "Learning from video…" : "Learn this skill"}<span>→</span></button></div>
              {learnError && <div className="inline-honesty" role="alert">{learnError}</div>}
              {learnedProcess && <section className="candidate-review" aria-live="polite"><div className="candidate-heading"><div><div className="eyebrow">CANDIDATE PROCESS · HUMAN REVIEW REQUIRED</div><h3>{learnedProcess.task_summary}</h3></div><span className="candidate-state">{learnedProcess._validation === "passed" ? "STRUCTURE CHECK PASSED" : "REVIEW"}</span></div>
                <p className="candidate-warning">This is a hypothesis from one observed trace. The observed order is not treated as a required dependency. Inspect the evidence and uncertainty before allowing this model to guide someone.</p>
                <div className="candidate-columns"><div><span className="eyebrow">OBJECTS · {learnedProcess.objects.length}</span>{learnedProcess.objects.map((object) => <div className="candidate-item" key={object.id}><strong>{object.label}</strong><small>{object.visual_description}</small></div>)}</div><div><span className="eyebrow">OBSERVED ACTIONS · {learnedProcess.transitions.length}</span>{learnedProcess.transitions.map((transition) => <div className="candidate-item" key={transition.id}><strong>{transition.action}</strong><small>{transition.evidence.map((evidence) => `${evidence.start_seconds.toFixed(1)}–${evidence.end_seconds.toFixed(1)}s · ${evidence.observation}`).join(" ")}</small>{transition.preconditions.length > 0 && <small className="tentative-condition">Model-proposed preconditions to verify: {transition.preconditions.join(", ")}</small>}</div>)}</div></div>
                <div className="candidate-bottom"><span>{learnedProcess.states.length} states · {learnedProcess.ordering_observations.length} observed ordering notes · {learnedProcess.uncertainties.length} uncertainties</span><span>{learnedProcess._run?.model ?? "Muse Spark"} · {learnedProcess._run?.usage?.input_tokens ?? 0} input tokens</span></div>
                {learnedProcess.uncertainties.length > 0 && <div className="candidate-uncertainties"><strong>Open questions</strong><ul>{learnedProcess.uncertainties.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul></div>}
                <div className="candidate-actions"><label><input type="checkbox" checked={candidateReviewed} onChange={(event) => setCandidateReviewed(event.target.checked)} /><span>I reviewed this candidate. The clip shows observed transitions; model-suggested prerequisites are not enforced from a single trace.</span></label><button className="primary-button" disabled={!candidateReviewed || learnedProcess.transitions.length === 0} onClick={loadReviewedCandidate}>Use this Skill Model <span>→</span></button></div>
              </section>}
            </section>
            <aside className="card learn-card"><div className="eyebrow">THE SKILL MODEL</div><h3>Teach builds the shared model.</h3><p>It should preserve evidence for every inferred transition, and keep uncertain steps visible for review.</p><div className="learn-steps">{["Objects", "Actions", "Before → after states", "Dependencies", "Open questions"].map((item, index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span>{item}</div>)}</div><div className="model-foot"><span className="status-dot muted" /> No model extraction has run in this screen</div></aside>
          </div>}

          {mode === "do" && <div className="work-grid do-grid">
            <section className="card camera-card"><div className="card-heading"><div><div className="eyebrow">STEP 02 · PERFORM THE TASK</div><h2>Keep your hands in view.</h2></div><span className={`record-indicator ${cameraOn ? "recording" : ""}`}><i /> {cameraOn ? "CAMERA ON" : "CAMERA OFF"}</span></div>
              <div className="camera-stage">{cameraOn ? <video ref={videoRef} className="camera-feed" autoPlay muted playsInline /> : <div className="camera-empty"><span>◎</span><strong>Your workspace will appear here</strong><small>Camera preview stays on this device.</small></div>}<div className="camera-crosshair" /></div>
              <div className="camera-controls">{cameraOn ? <button className="secondary-button" onClick={stopCamera}>Stop camera</button> : <button className="primary-button" onClick={() => void startCamera()}>Start camera <span>◎</span></button>}<span className="small-note">Automatic visual state tracking is not connected yet.</span></div>
              {cameraError && <div className="inline-honesty">{cameraError}</div>}
              <div className="observe-panel"><div className="eyebrow">TEST A RECORDED ATTEMPT</div><h3>Compare a learner clip.</h3><p>Use a separate recording to inspect timestamped events against the reviewed Skill Model. This is clip analysis, not live tracking.</p>
                <button className="upload-drop compact-drop" onClick={() => learnerInput.current?.click()}><span className="upload-symbol">↥</span><strong>{learnerFile ? learnerFile.name : "Choose learner video"}</strong><small>MP4, MOV, M4V, or WebM · up to 100 MB</small></button>
                <input ref={learnerInput} type="file" accept="video/mp4,video/quicktime,video/x-m4v,video/webm" hidden onChange={(event) => chooseLearnerVideo(event.target.files?.[0])} />
                {learnerUrl && <VideoPreview src={learnerUrl} />}
                <div className="capture-actions"><span className="small-note">Analysis sends this clip to Meta and may use API credits.</span><button className="primary-button" disabled={!learnerFile || !activeProcess || observing} onClick={() => void observeLearnerVideo()}>{observing ? "Comparing clip…" : "Observe attempt"}<span>→</span></button></div>
                {!activeProcess && <div className="inline-honesty">Teach a demonstration and load its reviewed Skill Model before observing a learner clip.</div>}
                {observeError && <div className="inline-honesty" role="alert">{observeError}</div>}
                {observation && <section className="observation-results" aria-live="polite"><div className="observation-heading"><div><div className="eyebrow">MODEL OBSERVATION · {observation._run?.model ?? "MUSE SPARK"}</div><h4>{observation.recovery_status.replaceAll("_", " ")}</h4></div><span>{observation._run?.usage?.input_tokens ?? 0} INPUT TOKENS</span></div>
                  {observation.divergences.length > 0 && <div className="divergence-list"><strong>Differences to inspect · {observation.divergences.length}</strong>{observation.divergences.map((item, index) => <article key={`${item.time_seconds}-${index}`}><span>{item.time_seconds.toFixed(1)}s</span><div><b>{item.process_difference}</b><p>{item.evidence}</p></div></article>)}</div>}
                  <div className="observed-events"><strong>Observed events · {observation.events.length}</strong>{observation.events.map((item, index) => <article key={`${item.time_seconds}-${index}`}><span>{item.time_seconds.toFixed(1)}s</span><i className={`event-dot ${item.assessment}`} /><div><b>{item.action}</b><p>{item.evidence}</p></div><small>{item.assessment.toUpperCase()}</small></article>)}</div>
                  {observation.uncertainties.length > 0 && <div className="candidate-uncertainties"><strong>Uncertain from this clip</strong><ul>{observation.uncertainties.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul></div>}
                </section>}
              </div>
            </section>
            <aside className="card guide-card"><div className="eyebrow">GUIDANCE · SAMPLE PROCEDURE</div><h3>Follow the demonstrated order.</h3><div className="guide-list">{model.actions.map((action, index) => <div className="guide-step" key={action.id}><span className={`guide-check ${state.includes(action.produces[0]) ? "done" : ""}`}>{state.includes(action.produces[0]) ? "✓" : String(index + 1).padStart(2, "0")}</span><div><strong>{action.label}</strong><small>{action.explanation}</small></div></div>)}</div><div className="guide-boundary"><span>i</span><p>This screen shows the camera feed and procedure. It does not yet detect learner actions; simulation is active in the Simulate mode.</p></div><button className="text-action" onClick={() => setMode("simulate")}>Try the process model <span>→</span></button></aside>
          </div>}

          <footer className="page-footer"><span>SHOWME · DEMONSTRATION → PROCESS MODEL → GUIDANCE</span><span>PROTOTYPE BUILD · 2026</span></footer>
        </div>
      </section>
    </main>
  );
}
