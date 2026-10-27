"use client";

import { useEffect, useRef, useState } from "react";
import { completedActions, simulateAction, simulateSequence } from "@/lib/simulate";
import { SAMPLE_SKILL, type SkillModel } from "@/lib/skill-model";
import { processToSkill } from "@/lib/process-to-skill";
import { clearReviewedProcess, loadReviewedProcess, saveReviewedProcess, type SavedProcess } from "@/lib/skill-storage";
import { interpretWhatIf } from "@/lib/what-if";

type Mode = "teach" | "do" | "simulate";
type LearnedProcess = SavedProcess;
type LearnerObservation = {
  events: { time_seconds: number; action: string; state_id: string; assessment: "consistent" | "divergent" | "unclear"; object_ids: string[]; evidence: string }[];
  divergences: { time_seconds: number; process_difference: string; object_ids: string[]; evidence: string }[];
  recovery_status: "no_divergence_observed" | "underway" | "recovered" | "unclear";
  uncertainties: string[];
  _run?: { model?: string; usage?: { input_tokens?: number; output_tokens?: number } };
};
type SnapshotObservation = {
  state_id: string;
  assessment: "consistent" | "possible_divergence" | "unclear";
  object_ids: string[];
  evidence: string;
  uncertainties: string[];
  _run?: { model?: string; usage?: { input_tokens?: number; output_tokens?: number } };
};
type SnapshotCheck = { checkedAt: string; observation: SnapshotObservation };
type GroundedDetection = { object_id: string; box?: { left: number; top: number; right: number; bottom: number }; mask?: { width: number; height: number; bounds: { left: number; top: number; right: number; bottom: number }; path: string } };
type SamGrounding = { model: string; concept: string; image: { width: number; height: number }; detections: GroundedDetection[]; diagnostics: string[] };
type SimulationOrigin = { state: string[]; actionIds: string[]; source: "skill-start" | "camera-checkpoint"; label: string };

function SamOverlayPreview({ grounding, sourceImage }: { grounding: SamGrounding; sourceImage: string }) {
  return <div className="grounding-result"><div className="eyebrow">{grounding.model.toUpperCase()} · {grounding.detections.length} MATCH{grounding.detections.length === 1 ? "" : "ES"}</div>{grounding.detections.length === 0 ? <p>No matching object was segmented in this frame.</p> : <div className="grounding-preview" style={{ aspectRatio: `${grounding.image.width} / ${grounding.image.height}` }}><img src={sourceImage} alt="The selected workspace frame" /><svg viewBox={`0 0 ${grounding.image.width} ${grounding.image.height}`} role="img" aria-label={`SAM segmentation for ${grounding.concept}`}>{grounding.detections.map((detection, index) => <g key={`${detection.object_id}-${index}`}>{detection.mask && <svg x={detection.mask.bounds.left} y={detection.mask.bounds.top} width={detection.mask.bounds.right - detection.mask.bounds.left} height={detection.mask.bounds.bottom - detection.mask.bounds.top} viewBox={`0 0 ${detection.mask.width} ${detection.mask.height}`} preserveAspectRatio="none"><path d={detection.mask.path} className="grounding-mask" /></svg>}{detection.box && <rect x={detection.box.left} y={detection.box.top} width={detection.box.right - detection.box.left} height={detection.box.bottom - detection.box.top} className="grounding-box" />}</g>)}</svg></div>}{grounding.diagnostics.length > 0 && <small>Some mask records could not be parsed: {grounding.diagnostics.join(", ")}</small>}</div>;
}

function SkillTransitionMap({ state, model, activeActionId }: { state: string[]; model: SkillModel; activeActionId?: string }) {
  const stateNames = (model.states ?? []).filter((item) => state.includes(item.id));
  const nextActionId = model.actions.find((action) => !action.produces.every((condition) => state.includes(condition)))?.id;
  const labelFor = (id?: string) => model.states?.find((item) => item.id === id)?.label ?? id?.replaceAll("_", " ") ?? "State not specified";
  const learned = model.status === "learned-from-demonstration";
  return <div className="learned-state-view skill-map-view">
    <div className="eyebrow">CURRENT SIMULATED STATE</div>
    <div className="learned-state-current" aria-live="polite">
      {stateNames.length ? stateNames.map((item) => <div className="learned-state-chip" key={item.id}><span>◉</span>{item.label}</div>) : <div className="learned-state-chip muted">{state.length ? state.map(labelFor).join(" · ") : "No matching state in this model"}</div>}
    </div>
    <div className="skill-state-map" aria-label="Skill Model transition map">
      <div className="skill-state-map-heading"><span>{learned ? "OBSERVED PROCESS TRACE" : "ILLUSTRATIVE PROCESS TRACE"}</span><span>{model.actions.length} transitions</span></div>
      {model.actions.map((action, index) => {
        const complete = action.produces.every((condition) => state.includes(condition));
        const involvedParts = action.objectIds.map((objectId) => model.objects.find((object) => object.id === objectId)?.name).filter((name): name is string => Boolean(name));
        const current = action.id === activeActionId || (!activeActionId && action.id === nextActionId);
        const status = complete ? "complete" : current ? "current" : "pending";
        return <div className={`skill-transition ${status}`} key={action.id} aria-current={current ? "step" : undefined}>
          <div className="skill-transition-marker"><span>{complete ? "✓" : String(index + 1).padStart(2, "0")}</span></div>
          <div className="skill-transition-copy">
            <div className="skill-transition-title"><strong>{action.label}</strong><small>{complete ? "IN SIMULATED STATE" : current ? "CURRENT TRANSITION" : "AHEAD IN TRACE"}</small></div>
            <div className="skill-transition-states"><span>{labelFor(action.fromState ?? (index === 0 ? model.initialState.find((item) => !item.endsWith("_available")) ?? model.initialState[0] : model.actions[index - 1]?.toState ?? model.actions[index - 1]?.produces[0]))}</span><i>→</i><span>{labelFor(action.toState ?? action.produces[0])}</span></div>
            {involvedParts.length > 0 && <small className="skill-transition-parts">PARTS · {involvedParts.join(" + ")}</small>}
            {action.evidence?.[0] && <small className="skill-transition-evidence">Evidence · {action.evidence[0].startSeconds.toFixed(1)}s — {action.evidence[0].observation}</small>}
          </div>
        </div>;
      })}
    </div>
    <p>{learned ? "Transitions come from the reviewed demonstration. This previews process states; it does not simulate physical forces or geometry." : "Illustrative fixture only. This previews procedural state; it does not simulate physical forces or geometry."}</p>
  </div>;
}

function AssemblyView({ state, model, activeActionId }: { state: string[]; model: SkillModel; activeActionId?: string }) {
  if (model.status === "learned-from-demonstration") return <SkillTransitionMap state={state} model={model} activeActionId={activeActionId} />;
  const washer = state.includes("washer_seated");
  const bracket = state.includes("bracket_mounted");
  const bolt = state.includes("fastener_inserted");
  return (
    <>
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
      <SkillTransitionMap state={state} model={model} activeActionId={activeActionId} />
    </>
  );
}

function VideoPreview({ src, videoRef }: { src: string; videoRef?: React.RefObject<HTMLVideoElement | null> }) {
  return <video ref={videoRef} className="video-preview" src={src} controls playsInline />;
}

export default function Home() {
  const [mode, setMode] = useState<Mode>("teach");
  const [model, setModel] = useState<SkillModel>(SAMPLE_SKILL);
  const [state, setState] = useState<string[]>(model.initialState);
  const [result, setResult] = useState<ReturnType<typeof simulateAction> | null>(null);
  const [sequenceDraft, setSequenceDraft] = useState<string[]>(model.actions.map((action) => action.id));
  const [sequenceResult, setSequenceResult] = useState<ReturnType<typeof simulateSequence> | null>(null);
  const [sequenceCursor, setSequenceCursor] = useState(-1);
  const [simulationOrigin, setSimulationOrigin] = useState<SimulationOrigin>({ state: SAMPLE_SKILL.initialState, actionIds: SAMPLE_SKILL.actions.map((action) => action.id), source: "skill-start", label: "Skill start" });
  const [whatIfPrompt, setWhatIfPrompt] = useState("");
  const [whatIfMessage, setWhatIfMessage] = useState("");
  const [whatIfProposal, setWhatIfProposal] = useState<Extract<ReturnType<typeof interpretWhatIf>, { ok: true }> | null>(null);
  const [mediaUrl, setMediaUrl] = useState("");
  const [sourceFile, setSourceFile] = useState<File | null>(null);
  const [demoCameraOn, setDemoCameraOn] = useState(false);
  const [recordingDemo, setRecordingDemo] = useState(false);
  const [demoCaptureError, setDemoCaptureError] = useState("");
  const [cameraOn, setCameraOn] = useState(false);
  const [recordingAttempt, setRecordingAttempt] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [narration, setNarration] = useState("");
  const [learnedProcess, setLearnedProcess] = useState<LearnedProcess | null>(null);
  const [activeProcess, setActiveProcess] = useState<LearnedProcess | null>(null);
  const [candidateReviewed, setCandidateReviewed] = useState(false);
  const [storageReady, setStorageReady] = useState(false);
  const [learnError, setLearnError] = useState("");
  const [learning, setLearning] = useState(false);
  const [learnerFile, setLearnerFile] = useState<File | null>(null);
  const [learnerUrl, setLearnerUrl] = useState("");
  const [observation, setObservation] = useState<LearnerObservation | null>(null);
  const [snapshotObservation, setSnapshotObservation] = useState<SnapshotObservation | null>(null);
  const [snapshotFrame, setSnapshotFrame] = useState<{ blob: Blob; dataUrl: string; width: number; height: number } | null>(null);
  const [grounding, setGrounding] = useState<SamGrounding | null>(null);
  const [groundingObjectId, setGroundingObjectId] = useState("");
  const [groundingError, setGroundingError] = useState("");
  const [groundingBusy, setGroundingBusy] = useState(false);
  const [learnerGrounding, setLearnerGrounding] = useState<{ result: SamGrounding; dataUrl: string; seconds: number; objectId: string } | null>(null);
  const [learnerGroundingError, setLearnerGroundingError] = useState("");
  const [learnerGroundingBusy, setLearnerGroundingBusy] = useState(false);
  const [snapshotHistory, setSnapshotHistory] = useState<SnapshotCheck[]>([]);
  const [snapshotError, setSnapshotError] = useState("");
  const [checkingSnapshot, setCheckingSnapshot] = useState(false);
  const [observeError, setObserveError] = useState("");
  const [observing, setObserving] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const demoVideoRef = useRef<HTMLVideoElement>(null);
  const demoStreamRef = useRef<MediaStream | null>(null);
  const demoRecorderRef = useRef<MediaRecorder | null>(null);
  const demoChunksRef = useRef<Blob[]>([]);
  const attemptRecorderRef = useRef<MediaRecorder | null>(null);
  const attemptChunksRef = useRef<Blob[]>([]);
  const learnerInput = useRef<HTMLInputElement>(null);
  const learnerVideoRef = useRef<HTMLVideoElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    const saved = loadReviewedProcess();
    if (saved) {
      const restoredModel = processToSkill(saved);
      setLearnedProcess(saved);
      setActiveProcess(saved);
      setModel(restoredModel);
      setState(restoredModel.initialState);
      setSequenceDraft(restoredModel.actions.map((action) => action.id));
      setSimulationOrigin({ state: restoredModel.initialState, actionIds: restoredModel.actions.map((action) => action.id), source: "skill-start", label: "Skill start" });
      setCandidateReviewed(true);
      setMode("do");
    }
    setStorageReady(true);
  }, []);

  useEffect(() => {
    if (storageReady && activeProcess) saveReviewedProcess(activeProcess);
  }, [activeProcess, storageReady]);

  useEffect(() => () => {
    if (mediaUrl.startsWith("blob:")) URL.revokeObjectURL(mediaUrl);
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, [mediaUrl]);

  useEffect(() => () => {
    if (learnerUrl.startsWith("blob:")) URL.revokeObjectURL(learnerUrl);
  }, [learnerUrl]);

  useEffect(() => {
    if (demoCameraOn && demoVideoRef.current && demoStreamRef.current) {
      demoVideoRef.current.srcObject = demoStreamRef.current;
    }
  }, [demoCameraOn]);

  useEffect(() => () => {
    if (demoRecorderRef.current?.state === "recording") demoRecorderRef.current.stop();
    if (attemptRecorderRef.current?.state === "recording") attemptRecorderRef.current.stop();
    demoStreamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  useEffect(() => () => {
    if (mode === "teach") {
      if (demoRecorderRef.current?.state === "recording") demoRecorderRef.current.stop();
      demoStreamRef.current?.getTracks().forEach((track) => track.stop());
      demoStreamRef.current = null;
      setDemoCameraOn(false);
      setRecordingDemo(false);
    }
    if (mode === "do") {
      if (attemptRecorderRef.current?.state === "recording") attemptRecorderRef.current.stop();
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setCameraOn(false);
      setRecordingAttempt(false);
    }
  }, [mode]);

  useEffect(() => {
    if (cameraOn && videoRef.current && streamRef.current) videoRef.current.srcObject = streamRef.current;
  }, [cameraOn]);

  function resetSimulation() {
    setState(simulationOrigin.state);
    setResult(null);
    setSequenceDraft(simulationOrigin.actionIds);
    setSequenceResult(null);
    setSequenceCursor(-1);
    setWhatIfProposal(null);
    setWhatIfMessage("");
  }

  function moveSequenceAction(index: number, offset: -1 | 1) {
    const target = index + offset;
    if (target < 0 || target >= sequenceDraft.length) return;
    setSequenceDraft((current) => {
      const next = [...current];
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
    setSequenceResult(null);
    setSequenceCursor(-1);
    setResult(null);
    setWhatIfProposal(null);
    setWhatIfMessage("");
  }

  function runSequenceWhatIf() {
    const next = simulateSequence(model, sequenceDraft, simulationOrigin.state);
    setSequenceResult(next);
    const firstStep = next.steps[0];
    setSequenceCursor(firstStep ? 0 : -1);
    setState(firstStep?.result.state ?? next.initialState);
    setResult(firstStep?.result ?? null);
  }

  function previewNaturalWhatIf() {
    const interpretation = interpretWhatIf(model, sequenceDraft, whatIfPrompt);
    if (!interpretation.ok) {
      setWhatIfProposal(null);
      setWhatIfMessage(interpretation.message);
      return;
    }
    setWhatIfProposal(interpretation);
    setWhatIfMessage("");
  }

  function applyNaturalWhatIf() {
    if (!whatIfProposal) return;
    setSequenceDraft(whatIfProposal.actionIds);
    setSequenceResult(null);
    setSequenceCursor(-1);
    setResult(null);
    setState(simulationOrigin.state);
    setWhatIfProposal(null);
    setWhatIfMessage("Proposed order added below. Review it, then run the simulation.");
  }

  function moveSimulationCursor(offset: -1 | 1) {
    if (!sequenceResult) return;
    const nextCursor = Math.max(0, Math.min(sequenceResult.steps.length - 1, sequenceCursor + offset));
    const step = sequenceResult.steps[nextCursor];
    if (!step) return;
    setSequenceCursor(nextCursor);
    setState(step.result.state);
    setResult(step.result);
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
    if (attemptRecorderRef.current?.state === "recording") {
      attemptRecorderRef.current.stop();
      return;
    }
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOn(false);
  }

  async function startAttemptRecording() {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setCameraError("Camera recording is unavailable here. You can upload a learner clip instead.");
      return;
    }
    try {
      let stream = streamRef.current;
      if (!stream) {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
        streamRef.current = stream;
        setCameraOn(true);
      }
      const mimeType = ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/mp4"]
        .find((candidate) => MediaRecorder.isTypeSupported(candidate));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      attemptChunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) attemptChunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(attemptChunksRef.current, { type: recorder.mimeType || "video/webm" });
        const extension = blob.type.includes("mp4") ? "mp4" : "webm";
        if (blob.size > 0) chooseLearnerVideo(new File([blob], `showme-attempt.${extension}`, { type: blob.type }));
        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        attemptRecorderRef.current = null;
        setRecordingAttempt(false);
        setCameraOn(false);
      };
      attemptRecorderRef.current = recorder;
      recorder.start(1000);
      setRecordingAttempt(true);
      setCameraError("");
    } catch {
      setCameraError("The browser could not start recording. You can upload a learner clip instead.");
    }
  }

  function loadReviewedCandidate() {
    if (!learnedProcess) return;
    const nextModel = processToSkill(learnedProcess);
    setActiveProcess(learnedProcess);
    setModel(nextModel);
    setState(nextModel.initialState);
    setSequenceDraft(nextModel.actions.map((action) => action.id));
    setSimulationOrigin({ state: nextModel.initialState, actionIds: nextModel.actions.map((action) => action.id), source: "skill-start", label: "Skill start" });
    setSequenceResult(null);
    setSequenceCursor(-1);
    setResult(null);
    setWhatIfProposal(null);
    setWhatIfMessage("");
    setSnapshotObservation(null);
    setSnapshotFrame(null);
    setGrounding(null);
    setGroundingError("");
    setSnapshotHistory([]);
    setMode("do");
  }

  function mapConfirmedPrecondition(transitionId: string, preconditionIndex: number, requiredState: string) {
    setLearnedProcess((current) => {
      if (!current) return current;
      const remaining = (current.human_confirmed_constraints ?? []).filter((item) => !(item.transition_id === transitionId && item.precondition_index === preconditionIndex));
      return {
        ...current,
        human_confirmed_constraints: requiredState
          ? [...remaining, { transition_id: transitionId, precondition_index: preconditionIndex, required_state: requiredState }]
          : remaining,
      };
    });
  }

  function forgetReviewedSkill() {
    clearReviewedProcess();
    setActiveProcess(null);
    setLearnedProcess(null);
    setCandidateReviewed(false);
    setModel(SAMPLE_SKILL);
    setState(SAMPLE_SKILL.initialState);
    setSequenceDraft(SAMPLE_SKILL.actions.map((action) => action.id));
    setSimulationOrigin({ state: SAMPLE_SKILL.initialState, actionIds: SAMPLE_SKILL.actions.map((action) => action.id), source: "skill-start", label: "Skill start" });
    setSequenceResult(null);
    setSequenceCursor(-1);
    setResult(null);
    setWhatIfPrompt("");
    setWhatIfProposal(null);
    setWhatIfMessage("");
    setObservation(null);
    setSnapshotObservation(null);
    setSnapshotFrame(null);
    setGrounding(null);
    setGroundingError("");
    setSnapshotHistory([]);
    setLearnerFile(null);
    setLearnerUrl((previous) => {
      if (previous.startsWith("blob:")) URL.revokeObjectURL(previous);
      return "";
    });
    setMode("teach");
  }

  function chooseLearnerVideo(file?: File) {
    if (!file) return;
    setLearnerFile(file);
    setLearnerUrl((previous) => {
      if (previous.startsWith("blob:")) URL.revokeObjectURL(previous);
      return URL.createObjectURL(file);
    });
    setObservation(null);
    setLearnerGrounding(null);
    setLearnerGroundingError("");
    setObserveError("");
  }

  async function observeLearnerVideo() {
    if (!activeProcess || !learnerFile) return;
    setObserving(true);
    setObservation(null);
    setLearnerGrounding(null);
    setLearnerGroundingError("");
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

  async function checkCurrentState() {
    const video = videoRef.current;
    if (!activeProcess || !video || video.videoWidth === 0 || video.videoHeight === 0) {
      setSnapshotError("Start the camera and wait for the workspace image before checking.");
      return;
    }
    setCheckingSnapshot(true);
    setSnapshotError("");
    setSnapshotObservation(null);
    setSnapshotFrame(null);
    setGrounding(null);
    setGroundingError("");
    const checkedAt = new Date().toISOString();
    try {
      const scale = Math.min(1, 1280 / Math.max(video.videoWidth, video.videoHeight));
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
      canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
      const context = canvas.getContext("2d");
      if (!context) throw new Error("Could not capture the current camera frame.");
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const image = await new Promise<Blob>((resolve, reject) => canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("Could not encode the camera frame.")), "image/jpeg", 0.82));
      const form = new FormData();
      form.set("image", image, "snapshot.jpg");
      form.set("process_json", JSON.stringify(activeProcess));
      const api = process.env.NEXT_PUBLIC_SHOWME_API_URL ?? "http://localhost:8000";
      const response = await fetch(`${api}/api/skills/observe-snapshot`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "SHOWME could not inspect this camera frame.");
      const nextObservation = payload.observation as SnapshotObservation;
      setSnapshotFrame({ blob: image, dataUrl: canvas.toDataURL("image/jpeg", 0.82), width: canvas.width, height: canvas.height });
      setGrounding(null);
      setGroundingError("");
      setGroundingObjectId(nextObservation.object_ids.find((id) => id !== "unknown" && activeProcess.objects.some((object) => object.id === id)) ?? "");
      setSnapshotObservation(nextObservation);
      setSnapshotHistory((history) => [...history, { checkedAt, observation: nextObservation }].slice(-12));
    } catch (error) {
      setSnapshotError(error instanceof Error ? error.message : "SHOWME could not reach the local snapshot service.");
    } finally {
      setCheckingSnapshot(false);
    }
  }

  async function groundSnapshotObject() {
    if (!activeProcess || !snapshotFrame || !groundingObjectId) return;
    const object = activeProcess.objects.find((item) => item.id === groundingObjectId);
    if (!object) return;
    setGroundingBusy(true);
    setGroundingError("");
    setGrounding(null);
    try {
      setGrounding(await requestObjectGrounding(snapshotFrame, object.id));
    } catch (error) {
      setGroundingError(error instanceof Error ? error.message : "SHOWME could not reach the SAM grounding service.");
    } finally {
      setGroundingBusy(false);
    }
  }

  async function requestObjectGrounding(frame: { blob: Blob; width: number; height: number }, objectId: string) {
    if (!activeProcess) throw new Error("Load a reviewed Skill Model first.");
    const form = new FormData();
    form.set("image", frame.blob, "snapshot.jpg");
    form.set("process_json", JSON.stringify(activeProcess));
    form.set("object_id", objectId);
    form.set("image_width", String(frame.width));
    form.set("image_height", String(frame.height));
    const api = process.env.NEXT_PUBLIC_SHOWME_API_URL ?? "http://localhost:8000";
    const response = await fetch(`${api}/api/skills/ground-object`, { method: "POST", body: form });
    const payload = await response.json();
    if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "SAM could not locate this object in the selected frame.");
    return payload as SamGrounding;
  }

  async function groundLearnerEvidence(seconds: number, objectId: string) {
    const video = learnerVideoRef.current;
    if (!video || !activeProcess || !activeProcess.objects.some((object) => object.id === objectId)) return;
    setLearnerGroundingBusy(true);
    setLearnerGroundingError("");
    setLearnerGrounding(null);
    try {
      video.pause();
      const target = Math.max(0, Math.min(seconds, Number.isFinite(video.duration) ? video.duration : seconds));
      if (Math.abs(video.currentTime - target) > 0.04) {
        await new Promise<void>((resolve, reject) => {
          const timeout = window.setTimeout(() => finish(new Error("The learner video did not seek to the evidence timestamp.")), 5000);
          const finish = (error?: Error) => {
            window.clearTimeout(timeout);
            video.removeEventListener("seeked", onSeeked);
            error ? reject(error) : resolve();
          };
          const onSeeked = () => finish();
          video.addEventListener("seeked", onSeeked, { once: true });
          video.currentTime = target;
        });
      }
      if (!video.videoWidth || !video.videoHeight) throw new Error("The selected learner frame is not ready yet.");
      const scale = Math.min(1, 1280 / Math.max(video.videoWidth, video.videoHeight));
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
      canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
      const context = canvas.getContext("2d");
      if (!context) throw new Error("Could not capture the learner video frame.");
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob((frame) => frame ? resolve(frame) : reject(new Error("Could not encode the learner frame.")), "image/jpeg", 0.82));
      const dataUrl = canvas.toDataURL("image/jpeg", 0.82);
      const result = await requestObjectGrounding({ blob, width: canvas.width, height: canvas.height }, objectId);
      setLearnerGrounding({ result, dataUrl, seconds: target, objectId });
    } catch (error) {
      setLearnerGroundingError(error instanceof Error ? error.message : "SHOWME could not ground this learner frame.");
    } finally {
      setLearnerGroundingBusy(false);
    }
  }

  function inspectLearnerEvidence(seconds: number) {
    const video = learnerVideoRef.current;
    if (!video) return;
    video.currentTime = Math.max(0, Math.min(seconds, Number.isFinite(video.duration) ? video.duration : seconds));
    void video.play().catch(() => undefined);
  }

  function objectLabels(ids: string[]) {
    if (ids.length === 0) return "No specific object grounded";
    return ids.map((id) => activeProcess?.objects.find((object) => object.id === id)?.label ?? id.replaceAll("_", " ")).join(" · ");
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

  async function startDemoCamera() {
    setDemoCaptureError("");
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setDemoCaptureError("Camera recording is unavailable here. Use a supported browser on localhost or HTTPS, or upload a video.");
      return;
    }
    try {
      demoStreamRef.current?.getTracks().forEach((track) => track.stop());
      demoStreamRef.current = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      setDemoCameraOn(true);
    } catch {
      setDemoCaptureError("Camera permission was not granted. You can still upload a demonstration video.");
    }
  }

  function stopDemoCamera() {
    if (demoRecorderRef.current?.state === "recording") {
      demoRecorderRef.current.stop();
      return;
    }
    demoStreamRef.current?.getTracks().forEach((track) => track.stop());
    demoStreamRef.current = null;
    setDemoCameraOn(false);
  }

  function startDemoRecording() {
    const stream = demoStreamRef.current;
    if (!stream) return;
    try {
      const mimeType = ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/mp4"]
        .find((candidate) => MediaRecorder.isTypeSupported(candidate));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      demoChunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) demoChunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(demoChunksRef.current, { type: recorder.mimeType || "video/webm" });
        const extension = blob.type.includes("mp4") ? "mp4" : "webm";
        if (blob.size > 0) chooseVideo(new File([blob], `showme-demonstration.${extension}`, { type: blob.type }));
        demoStreamRef.current?.getTracks().forEach((track) => track.stop());
        demoStreamRef.current = null;
        demoRecorderRef.current = null;
        setRecordingDemo(false);
        setDemoCameraOn(false);
      };
      demoRecorderRef.current = recorder;
      recorder.start(1000);
      setRecordingDemo(true);
      setDemoCaptureError("");
    } catch {
      setDemoCaptureError("The browser could not start recording. Try uploading a video instead.");
    }
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
  const referenceSequence = simulateSequence(model, simulationOrigin.actionIds, simulationOrigin.state);
  const snapshotActionIndex = snapshotObservation?.assessment === "consistent" && snapshotObservation.state_id !== "unknown"
    ? model.actions.reduce((lastIndex, action, index) => action.toState === snapshotObservation.state_id ? index : lastIndex, -1)
    : -1;
  const snapshotCanContinue = Boolean(activeProcess && snapshotObservation?.assessment === "consistent" && snapshotObservation.state_id !== "unknown" && (model.initialState.includes(snapshotObservation.state_id) || (snapshotActionIndex >= 0 && snapshotActionIndex < model.actions.length - 1)));
  const labelState = (stateId: string) => model.states?.find((item) => item.id === stateId)?.label ?? stateId.replaceAll("_", " ");
  const sequenceStatusLabel = (status: ReturnType<typeof simulateSequence>["status"]) => status === "completed" ? "modeled end state reached" : status === "blocked" ? "stops at confirmed requirement" : "transition not observed";

  function startSimulationFromSnapshot() {
    if (!snapshotCanContinue || !snapshotObservation || snapshotObservation.assessment !== "consistent") return;
    const isInitial = model.initialState.includes(snapshotObservation.state_id);
    const remainingActions = isInitial ? model.actions : model.actions.slice(snapshotActionIndex + 1);
    const origin: SimulationOrigin = {
      state: [snapshotObservation.state_id],
      actionIds: remainingActions.map((action) => action.id),
      source: "camera-checkpoint",
      label: `Frame check · ${labelState(snapshotObservation.state_id)}`,
    };
    setSimulationOrigin(origin);
    setState(origin.state);
    setSequenceDraft(origin.actionIds);
    setSequenceResult(null);
    setSequenceCursor(-1);
    setResult(null);
    setWhatIfProposal(null);
    setWhatIfMessage("");
    setMode("simulate");
  }
  const proposedConstraints = model.actions.flatMap((action) =>
    action.constraints.filter((constraint) => constraint.status === "proposed").map((constraint) => ({ action: action.label, description: constraint.description })),
  );

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
              <div className="fixture-note"><span>i</span><p>{model.status === "learned-from-demonstration" ? `This reviewed model represents one observed trace. It does not prove the process is complete or that another order is impossible. Starting point: ${simulationOrigin.label}.` : "This is an illustrative fixture to make the process model tangible. It has not been learned from a demonstration yet."}</p></div>
              <AssemblyView state={state} model={model} activeActionId={sequenceResult?.steps[sequenceCursor]?.result.action.id ?? result?.action.id} />
              <div className="state-summary"><div><span className="eyebrow">SIMULATED STATE</span><strong>{done.length === model.actions.length ? "Assembly complete" : `${done.length} of ${model.actions.length} actions complete`}</strong></div><span className="state-pip"><i className={result?.accepted === false ? "warning" : ""} /></span></div>
              {result && <div className={`result-callout ${result.accepted ? "success" : result.kind === "unobserved" ? "unobserved" : "blocked"}`} role="status"><span className="result-icon">{result.accepted ? "✓" : result.kind === "unobserved" ? "?" : "!"}</span><div><strong>{result.accepted ? "OBSERVED TRANSITION" : result.kind === "unobserved" ? "ALTERNATIVE NOT OBSERVED" : "CONFIRMED REQUIREMENT NOT MET"}</strong><p>{result.message}</p>{!result.accepted && <small>{result.kind === "unobserved" ? "Evidence needed: another demonstration or human confirmation." : <>Missing state: {result.missing.map((item) => item.replaceAll("_", " ")).join(", ")}<br />Constraint source: {result.blockedBy?.map((constraint) => constraint.source.replaceAll("-", " ")).join(", ")}</>}<br />{result.action.recovery}</small>}</div></div>}
              <div className="what-if"><span className="what-if-mark">?</span><div><strong>What if the steps happened in a different order?</strong><p>Reorder the remaining actions and run the alternative from {simulationOrigin.label}. SHOWME stops at the first confirmed requirement or transition the trace does not support.</p></div></div>
              <section className="natural-what-if">
                <label className="eyebrow" htmlFor="what-if-prompt">DESCRIBE AN ALTERNATIVE</label>
                <div className="natural-what-if-entry"><input id="what-if-prompt" value={whatIfPrompt} onChange={(event) => { setWhatIfPrompt(event.target.value); setWhatIfProposal(null); setWhatIfMessage(""); }} onKeyDown={(event) => { if (event.key === "Enter") previewNaturalWhatIf(); }} placeholder="What if ‘Mount support bracket’ comes before ‘Place spacer ring’?" /><button className="secondary-button" onClick={previewNaturalWhatIf}>Preview order</button></div>
                {whatIfMessage && <p className="natural-what-if-message" role="status">{whatIfMessage}</p>}
                {whatIfProposal && <div className="what-if-proposal" aria-live="polite"><strong>{whatIfProposal.summary}</strong><ol>{whatIfProposal.actionIds.map((actionId, index) => { const action = model.actions.find((item) => item.id === actionId); return action ? <li key={`${actionId}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span>{action.label}</li> : null; })}</ol><button className="text-action" onClick={applyNaturalWhatIf}>Use this order in the simulator →</button></div>}
                <small className="sequence-disclaimer">Review the interpreted order before running the deterministic process simulation.</small>
              </section>
              <div className="sequence-editor"><div className="sequence-editor-heading"><span className="eyebrow">PROPOSED ACTION ORDER</span><span>Move a step to explore an alternative</span></div>{sequenceDraft.map((actionId, index) => {
                const action = model.actions.find((candidate) => candidate.id === actionId);
                if (!action) return null;
                return <div className="sequence-row" key={action.id}><span className="action-number">{String(index + 1).padStart(2, "0")}</span><strong>{action.label}</strong><div className="sequence-movers"><button aria-label={`Move ${action.label} earlier`} disabled={index === 0} onClick={() => moveSequenceAction(index, -1)}>↑</button><button aria-label={`Move ${action.label} later`} disabled={index === sequenceDraft.length - 1} onClick={() => moveSequenceAction(index, 1)}>↓</button></div></div>;
              })}<div className="sequence-controls"><button className="primary-button" onClick={runSequenceWhatIf}>Run this what-if <span>↗</span></button><button className="text-action" onClick={resetSimulation}>Restore demonstrated order</button></div></div>
              {sequenceResult && <section className={`sequence-report sequence-${sequenceResult.status}`} aria-live="polite">
                <div className="eyebrow">DETERMINISTIC PROCEDURE SIMULATION</div>
                <strong>{sequenceResult.status === "completed" ? "The proposed sequence reaches its modeled end state." : sequenceResult.status === "blocked" ? "The sequence stops at a confirmed requirement." : "The next transition was not observed from this state."}</strong>
                <div className="state-comparison" aria-label="Reference and proposed final model states">
                  {[{ title: model.status === "learned-from-demonstration" ? (simulationOrigin.source === "camera-checkpoint" ? "REMAINING OBSERVED TRACE" : "OBSERVED REFERENCE TRACE") : "ILLUSTRATIVE REFERENCE", result: referenceSequence }, { title: "PROPOSED ALTERNATIVE", result: sequenceResult }].map(({ title, result: comparison }) => <div className="state-comparison-card" key={title}>
                    <div><span>{title}</span><small>{sequenceStatusLabel(comparison.status)}</small></div>
                    <div className="comparison-state-list">{comparison.finalState.length ? comparison.finalState.map((stateId) => <span className="comparison-state" key={stateId}>{labelState(stateId)}</span>) : <span className="comparison-empty">No modeled states remain.</span>}</div>
                  </div>)}
                </div>
                <small className="sequence-disclaimer">The comparison uses the same Skill Model. An observed reference trace is evidence of what happened once, not proof that other orders are impossible.</small>
                {sequenceResult.steps.length > 0 && <div className="sequence-playback"><span>STEP {sequenceCursor + 1} OF {sequenceResult.steps.length} · {sequenceResult.steps[sequenceCursor]?.result.action.label}</span><div><button className="secondary-button" disabled={sequenceCursor <= 0} onClick={() => moveSimulationCursor(-1)}>← Previous</button><button className="secondary-button" disabled={sequenceCursor >= sequenceResult.steps.length - 1} onClick={() => moveSimulationCursor(1)}>Next →</button></div></div>}
                <ol>{sequenceResult.steps.map(({ index, result: step }) => <li className={sequenceCursor === index ? "current" : ""} key={`${step.action.id}-${index}`}><span>{step.accepted ? "✓" : step.kind === "blocked" ? "!" : "?"}</span><div><b>{step.action.label}</b><small>{step.accepted ? "Applied to the simulated state." : step.message}{!step.accepted && step.kind === "blocked" && ` Missing: ${step.missing.join(", ")}. Basis: ${step.blockedBy.map((item) => item.source.replaceAll("-", " ")).join(", ")}.`}</small></div></li>)}</ol>
                <small className="sequence-disclaimer">This is a procedural state preview, not a physics simulation or a claim about what happened in the camera view.</small>
              </section>}
            </section>
            <aside className="card model-card">
              <div className="eyebrow">PROCESS MODEL</div><h3>What the skill knows</h3><p className="model-copy">A compact set of objects, states, and action constraints. Teach will eventually replace this fixture with a model inferred from a real demonstration.</p>
              <div className="model-section"><span>OBJECTS</span>{model.objects.map((object) => <div className="model-row" key={object.id}><i className={`object-swatch ${object.color}`} /><span>{object.name}</span><small>{state.some((item) => item.startsWith(object.id) || item.includes(object.id)) ? "IN USE" : "READY"}</small></div>)}</div>
              <div className="model-section"><span>{model.status === "learned-from-demonstration" ? "OBSERVED TRANSITIONS" : "CONFIRMED DEPENDENCY"}</span><div className="dependency-flow">{model.actions.map((action, index) => <div className={state.includes(action.toState ?? action.produces[0]) ? "on" : ""} key={action.id}>{action.label}{model.status === "learned-from-demonstration" && <small className="observed-edge">{action.fromState?.replaceAll("_", " ")} → {action.toState?.replaceAll("_", " ")}</small>}{index < model.actions.length - 1 && <b>↓</b>}</div>)}</div>{proposedConstraints.length > 0 && <div className="hypothesis-list"><span>MODEL HYPOTHESES · NOT ENFORCED</span>{proposedConstraints.map((item, index) => <p key={`${item.action}-${index}`}><b>{item.action}:</b> {item.description}</p>)}</div>}{model.status === "learned-from-demonstration" && <p className="model-copy model-caveat">Observed order is evidence about this clip, not proof of a universal requirement. Proposed preconditions remain hypotheses until confirmed.</p>}</div>
              <div className="model-foot"><span className="status-dot" /> {model.status === "learned-from-demonstration" ? "Transitions grounded in one reviewed trace" : "Deterministic illustrative state fixture"}</div>
            </aside>
          </div>}

          {mode === "teach" && <div className="work-grid teach-grid">
            <section className="card capture-card"><div className="card-heading"><div><div className="eyebrow">STEP 01 · PROVIDE A DEMONSTRATION</div><h2>Show it once.</h2></div><span className="capture-icon">↥</span></div>
              {demoCameraOn && <div className="demo-record-stage"><video ref={demoVideoRef} className="camera-feed" autoPlay muted playsInline /><span className={`record-indicator ${recordingDemo ? "recording" : ""}`}><i /> {recordingDemo ? "RECORDING" : "CAMERA READY"}</span></div>}
              {mediaUrl ? <VideoPreview src={mediaUrl} /> : !demoCameraOn && <button className="upload-drop" onClick={() => fileInput.current?.click()}><span className="upload-symbol">↥</span><strong>Choose a demonstration video</strong><small>MP4, MOV, M4V, or WebM · a short, clear view of the task</small><span className="outline-button">Browse files</span></button>}
              <input ref={fileInput} type="file" accept="video/mp4,video/quicktime,video/x-m4v,video/webm" hidden onChange={(event) => chooseVideo(event.target.files?.[0])} />
              {mediaUrl && <div className="clip-actions"><a className="text-action" href={mediaUrl} download={sourceFile?.name || "showme-demonstration.webm"}>Save this clip ↓</a><button className="text-action replace-video" onClick={() => fileInput.current?.click()}>Choose a different video</button></div>}
              <div className="demo-record-controls">{!demoCameraOn ? <button className="secondary-button" onClick={() => void startDemoCamera()}>Record with camera <span>◎</span></button> : <><button className="primary-button" disabled={recordingDemo} onClick={startDemoRecording}>{recordingDemo ? "Recording…" : "Start recording"}<span>●</span></button><button className="secondary-button" onClick={stopDemoCamera}>{recordingDemo ? "Stop and use this clip" : "Stop camera"}</button></>}<span className="small-note">Camera video stays in this tab. Save the clip or choose Learn to send it for analysis.</span></div>
              {demoCaptureError && <div className="inline-honesty" role="alert">{demoCaptureError}</div>}
              <label className="field-label" htmlFor="narration">WHAT SHOULD SHOWME NOTICE?</label><textarea id="narration" value={narration} onChange={(event) => setNarration(event.target.value)} placeholder="Narrate while you demonstrate: ‘The spacer goes under the bracket…’" />
              <div className="capture-actions"><span className="small-note">Choosing Learn uploads this clip to Meta for inference and may use API credits.</span><button className="primary-button" disabled={!sourceFile || learning || demoCameraOn} onClick={() => void learnFromVideo()}>{learning ? "Learning from video…" : "Learn this skill"}<span>→</span></button></div>
              {learnError && <div className="inline-honesty" role="alert">{learnError}</div>}
              {learnedProcess && <section className="candidate-review" aria-live="polite"><div className="candidate-heading"><div><div className="eyebrow">CANDIDATE PROCESS · HUMAN REVIEW REQUIRED</div><h3>{learnedProcess.task_summary}</h3></div><span className="candidate-state">{learnedProcess._validation === "passed" ? "STRUCTURE CHECK PASSED" : "REVIEW"}</span></div>
                <p className="candidate-warning">This is a hypothesis from one observed trace. The observed order is not treated as a required dependency. Inspect the evidence and uncertainty before allowing this model to guide someone.</p>
                <div className="candidate-columns"><div><span className="eyebrow">OBJECTS · {learnedProcess.objects.length}</span>{learnedProcess.objects.map((object) => <div className="candidate-item" key={object.id}><strong>{object.label}</strong><small>{object.visual_description}</small></div>)}</div><div><span className="eyebrow">OBSERVED ACTIONS · {learnedProcess.transitions.length}</span>{learnedProcess.transitions.map((transition) => <div className="candidate-item" key={transition.id}><strong>{transition.action}</strong><small>{transition.evidence.map((evidence) => `${evidence.start_seconds.toFixed(1)}–${evidence.end_seconds.toFixed(1)}s · ${evidence.observation}`).join(" ")}</small>{transition.preconditions.map((precondition, index) => {
                  const mapped = learnedProcess.human_confirmed_constraints?.find((item) => item.transition_id === transition.id && item.precondition_index === index)?.required_state ?? "";
                  return <label className="tentative-condition condition-review" key={`${transition.id}-precondition-${index}`}><span>{mapped ? "Human-confirmed prerequisite" : "Model-proposed prerequisite · not enforced"}: {precondition}</span><select aria-label={`Map prerequisite for ${transition.action} to an observed state`} value={mapped} onChange={(event) => mapConfirmedPrecondition(transition.id, index, event.target.value)}><option value="">Keep as hypothesis</option>{learnedProcess.states.map((stateOption) => <option value={stateOption.id} key={stateOption.id}>{stateOption.description}</option>)}</select></label>;
                })}</div>)}</div></div>
                <div className="candidate-bottom"><span>{learnedProcess.states.length} states · {learnedProcess.ordering_observations.length} observed ordering notes · {learnedProcess.uncertainties.length} uncertainties</span><span>{learnedProcess._run?.model ?? "Muse Spark"} · {learnedProcess._run?.usage?.input_tokens ?? 0} input tokens</span></div>
                {learnedProcess.uncertainties.length > 0 && <div className="candidate-uncertainties"><strong>Open questions</strong><ul>{learnedProcess.uncertainties.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul></div>}
                <div className="candidate-actions"><label><input type="checkbox" checked={candidateReviewed} onChange={(event) => setCandidateReviewed(event.target.checked)} /><span>I reviewed this candidate. The clip shows observed transitions; model-suggested prerequisites are not enforced from a single trace.</span></label><button className="primary-button" disabled={!candidateReviewed || learnedProcess.transitions.length === 0} onClick={loadReviewedCandidate}>Use this Skill Model <span>→</span></button></div>
              </section>}
            </section>
            <aside className="card learn-card"><div className="eyebrow">THE SKILL MODEL</div><h3>Teach builds the shared model.</h3><p>It should preserve evidence for every inferred transition, and keep uncertain steps visible for review.</p><div className="learn-steps">{["Objects", "Actions", "Before → after states", "Dependencies", "Open questions"].map((item, index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span>{item}</div>)}</div><div className="model-foot"><span className="status-dot muted" /> No model extraction has run in this screen</div></aside>
          </div>}

          {mode === "do" && <div className="work-grid do-grid">
            <section className="card camera-card"><div className="card-heading"><div><div className="eyebrow">STEP 02 · PERFORM THE TASK</div><h2>Keep your hands in view.</h2></div><span className={`record-indicator ${recordingAttempt ? "recording" : ""}`}><i /> {recordingAttempt ? "RECORDING" : cameraOn ? "CAMERA ON" : "CAMERA OFF"}</span></div>
              <div className="camera-stage">{cameraOn ? <video ref={videoRef} className="camera-feed" autoPlay muted playsInline /> : <div className="camera-empty"><span>◎</span><strong>Your workspace will appear here</strong><small>Camera preview stays on this device.</small></div>}<div className="camera-crosshair" /></div>
              <div className="camera-controls">{cameraOn ? <><button className="secondary-button" onClick={stopCamera}>{recordingAttempt ? "Stop and use this clip" : "Stop camera"}</button><button className="primary-button" disabled={recordingAttempt} onClick={() => void startAttemptRecording()}>{recordingAttempt ? "Recording…" : "Record learner attempt"}<span>●</span></button></> : <><button className="secondary-button" onClick={() => void startCamera()}>Start camera <span>◎</span></button><button className="primary-button" onClick={() => void startAttemptRecording()}>Record learner attempt<span>●</span></button></>}<button className="secondary-button" disabled={!cameraOn || recordingAttempt || !activeProcess || checkingSnapshot} onClick={() => void checkCurrentState()}>{checkingSnapshot ? "Checking frame…" : "Check current state"}</button><span className="small-note">Camera stays on this device. Each explicit check sends one still frame to Muse Spark and adds a local session checkpoint.</span></div>
              {cameraError && <div className="inline-honesty">{cameraError}</div>}
              {snapshotError && <div className="inline-honesty" role="alert">{snapshotError}</div>}
              {snapshotObservation && <section className={`snapshot-result snapshot-${snapshotObservation.assessment}`} aria-live="polite"><div className="eyebrow">ONE-FRAME CHECK · {snapshotObservation._run?.model ?? "MUSE SPARK"}</div><strong>{snapshotObservation.assessment === "consistent" ? "Matches a demonstrated state" : snapshotObservation.assessment === "possible_divergence" ? "Possible difference from the demonstrated states" : "The frame is unclear"}</strong><p>{snapshotObservation.evidence}</p><small>{snapshotObservation.state_id === "unknown" ? "No matching state identified" : activeProcess?.states.find((state) => state.id === snapshotObservation.state_id)?.description ?? snapshotObservation.state_id} · {objectLabels(snapshotObservation.object_ids)}</small>{snapshotObservation.uncertainties.length > 0 && <ul>{snapshotObservation.uncertainties.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul>}<small className="snapshot-boundary">A still frame cannot show what happened before it or confirm recovery. This is not continuous tracking.</small>
                {snapshotFrame && activeProcess && snapshotObservation.object_ids.some((id) => id !== "unknown" && activeProcess.objects.some((object) => object.id === id)) && <div className="grounding-panel"><div className="eyebrow">OPTIONAL OBJECT GROUNDING · SAM 3.1</div><p>Ask SAM to find one object Muse mentioned in this exact frame. This extra model call uses API credits.</p><div className="grounding-controls"><select aria-label="Object to locate" value={groundingObjectId} onChange={(event) => setGroundingObjectId(event.target.value)}>{snapshotObservation.object_ids.filter((id) => id !== "unknown").map((id) => activeProcess.objects.find((object) => object.id === id)).filter((object): object is LearnedProcess["objects"][number] => Boolean(object)).map((object) => <option value={object.id} key={object.id}>{object.label}</option>)}</select><button className="secondary-button" disabled={!groundingObjectId || groundingBusy} onClick={() => void groundSnapshotObject()}>{groundingBusy ? "Locating object…" : "Locate in frame"}</button></div>
                  {groundingError && <div className="inline-honesty" role="alert">{groundingError}</div>}
                  {grounding && <><SamOverlayPreview grounding={grounding} sourceImage={snapshotFrame.dataUrl} /><small className="snapshot-boundary">SAM marks visual regions matching the chosen phrase; it does not verify the task state or prove why a step is wrong.</small></>}
                </div>}
                {snapshotCanContinue && <button className="text-action snapshot-simulate" onClick={startSimulationFromSnapshot}>Explore remaining steps from this observed state →</button>}</section>}
              {snapshotHistory.length > 0 && <section className="snapshot-history" aria-label="Camera check history">
                <div className="snapshot-history-heading"><div><span className="eyebrow">SESSION CHECKPOINTS</span><small>Last {snapshotHistory.length} manual frame checks</small></div><button className="text-action" onClick={() => { setSnapshotHistory([]); setSnapshotObservation(null); }}>Clear</button></div>
                <ol className="snapshot-history-list" aria-live="polite">{[...snapshotHistory].reverse().map(({ checkedAt, observation: item }) => <li className={`snapshot-history-item history-${item.assessment}`} key={checkedAt}>
                  <span className="history-marker" aria-hidden="true" />
                  <div className="history-body"><div className="history-meta"><time dateTime={checkedAt}>{checkedAt.slice(11, 16)} UTC</time><strong>{item.assessment === "consistent" ? "MATCH" : item.assessment === "possible_divergence" ? "POSSIBLE DIFFERENCE" : "UNCLEAR"}</strong></div>
                    <p>{item.state_id === "unknown" ? "No matching state identified" : activeProcess?.states.find((candidate) => candidate.id === item.state_id)?.description ?? item.state_id.replaceAll("_", " ")}{item.object_ids.length > 0 && ` · ${objectLabels(item.object_ids)}`}</p><small>{item.evidence}</small>
                  </div>
                </li>)}</ol>
                <p className="snapshot-history-boundary">These are separate, user-requested frame checks. SHOWME does not observe the actions between them or infer recovery from this list.</p>
              </section>}
              <div className="observe-panel"><div className="eyebrow">TEST A RECORDED ATTEMPT</div><h3>Compare a learner clip.</h3><p>Use a separate recording to inspect timestamped events against the reviewed Skill Model. This is clip analysis, not live tracking.</p>
                <button className="upload-drop compact-drop" disabled={cameraOn} onClick={() => learnerInput.current?.click()}><span className="upload-symbol">↥</span><strong>{learnerFile ? learnerFile.name : "Choose learner video"}</strong><small>MP4, MOV, M4V, or WebM · up to 100 MB</small></button>
                <input ref={learnerInput} type="file" accept="video/mp4,video/quicktime,video/x-m4v,video/webm" hidden onChange={(event) => chooseLearnerVideo(event.target.files?.[0])} />
                {learnerUrl && <><VideoPreview src={learnerUrl} videoRef={learnerVideoRef} /><a className="text-action clip-download" href={learnerUrl} download={learnerFile?.name || "showme-attempt.webm"}>Save learner clip ↓</a></>}
                <div className="capture-actions"><span className="small-note">Analysis sends this clip to Meta and may use API credits.</span><button className="primary-button" disabled={!learnerFile || !activeProcess || observing || cameraOn} onClick={() => void observeLearnerVideo()}>{observing ? "Comparing clip…" : "Observe attempt"}<span>→</span></button></div>
                {!activeProcess && <div className="inline-honesty">Teach a demonstration and load its reviewed Skill Model before observing a learner clip.</div>}
                {observeError && <div className="inline-honesty" role="alert">{observeError}</div>}
                {observation && <section className="observation-results" aria-live="polite"><div className="observation-heading"><div><div className="eyebrow">MODEL OBSERVATION · {observation._run?.model ?? "MUSE SPARK"}</div><h4>{observation.recovery_status.replaceAll("_", " ")}</h4></div><span>{observation._run?.usage?.input_tokens ?? 0} INPUT TOKENS</span></div>
                  {(() => {
                    const firstDivergence = observation.divergences.length ? Math.min(...observation.divergences.map((item) => item.time_seconds)) : Number.POSITIVE_INFINITY;
                    const recoveryEvent = observation.events.find((item) => item.assessment === "consistent" && item.state_id !== "unknown" && item.time_seconds > firstDivergence);
                    const recoveryCopy = {
                      no_divergence_observed: ["No divergence reported", "This clip did not produce a visible difference from the reviewed process."],
                      underway: ["Recovery may be underway", "The clip includes a divergence, but SHOWME did not confirm a later process-consistent state."],
                      recovered: ["A later consistent state was observed", "Review the timestamped event before treating the recovery as confirmed."],
                      unclear: ["Recovery is unclear", "The available frames do not support a reliable conclusion about the final state."],
                    }[observation.recovery_status];
                    return <div className={`recovery-summary recovery-${observation.recovery_status}`}><span className="eyebrow">RECOVERY CHECK</span><strong>{recoveryCopy[0]}</strong><p>{recoveryCopy[1]}</p>{recoveryEvent && <button className="text-action" onClick={() => inspectLearnerEvidence(recoveryEvent.time_seconds)}>Review later consistent state · {recoveryEvent.time_seconds.toFixed(1)}s →</button>}</div>;
                  })()}
                  <p className="evidence-review-hint">Select a timestamp to inspect the supporting moment. Locate sends one frame and one object phrase to SAM, using API credits; it segments pixels but does not verify the reported difference.</p>
                  {observation.divergences.length > 0 && <div className="divergence-list"><strong>Differences to inspect · {observation.divergences.length}</strong>{observation.divergences.map((item, index) => <div className="divergence-entry" key={`${item.time_seconds}-${index}`}><button className="evidence-row" onClick={() => inspectLearnerEvidence(item.time_seconds)}><span>{item.time_seconds.toFixed(1)}s</span><div><b>{item.process_difference}</b><p>{item.evidence}</p><small>{objectLabels(item.object_ids)}</small></div></button>{item.object_ids.filter((id) => id !== "unknown" && activeProcess?.objects.some((object) => object.id === id)).map((id) => <button className="ground-evidence-button" disabled={learnerGroundingBusy} key={id} onClick={() => void groundLearnerEvidence(item.time_seconds, id)}>Locate {activeProcess?.objects.find((object) => object.id === id)?.label ?? id} in this frame</button>)}</div>)}</div>}
                  {learnerGroundingError && <div className="inline-honesty" role="alert">{learnerGroundingError}</div>}
                  {learnerGroundingBusy && <p className="evidence-review-hint">Seeking to the selected clip moment and grounding the named object with SAM…</p>}
                  {learnerGrounding && <div className="learner-grounding-result"><div className="eyebrow">CLIP FRAME · {learnerGrounding.seconds.toFixed(1)}s · {activeProcess?.objects.find((object) => object.id === learnerGrounding.objectId)?.label ?? learnerGrounding.objectId}</div><SamOverlayPreview grounding={learnerGrounding.result} sourceImage={learnerGrounding.dataUrl} /><small className="snapshot-boundary">This is SAM segmentation on one Muse-referenced clip timestamp. It does not independently confirm the reported divergence.</small></div>}
                  <div className="observed-events"><strong>Observed events · {observation.events.length}</strong>{observation.events.map((item, index) => <button className="evidence-event" key={`${item.time_seconds}-${index}`} onClick={() => inspectLearnerEvidence(item.time_seconds)}><span>{item.time_seconds.toFixed(1)}s</span><i className={`event-dot ${item.assessment}`} /><div><b>{item.action}</b><p>{item.evidence}</p><small>{objectLabels(item.object_ids)}</small></div><small>{item.assessment.toUpperCase()}</small></button>)}</div>
                  {observation.uncertainties.length > 0 && <div className="candidate-uncertainties"><strong>Uncertain from this clip</strong><ul>{observation.uncertainties.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul></div>}
                </section>}
              </div>
            </section>
            <aside className="card guide-card"><div className="eyebrow">GUIDANCE · {activeProcess ? "REVIEWED SKILL" : "SAMPLE PROCEDURE"}</div><h3>Follow the demonstrated order.</h3><div className="guide-list">{model.actions.map((action, index) => <div className="guide-step" key={action.id}><span className={`guide-check ${state.includes(action.produces[0]) ? "done" : ""}`}>{state.includes(action.produces[0]) ? "✓" : String(index + 1).padStart(2, "0")}</span><div><strong>{action.label}</strong><small>{action.explanation}</small></div></div>)}</div><div className="guide-boundary"><span>i</span><p>Record a learner clip here for review. SHOWME analyzes it only after you select Observe attempt; the camera does not track actions continuously.</p></div><button className="text-action" onClick={() => setMode("simulate")}>Try the process model <span>→</span></button>{activeProcess && <button className="text-action forget-skill" onClick={forgetReviewedSkill}>Forget saved skill</button>}</aside>
          </div>}

          <footer className="page-footer"><span>SHOWME · DEMONSTRATION → PROCESS MODEL → GUIDANCE</span><span>PROTOTYPE BUILD · 2026</span></footer>
        </div>
      </section>
    </main>
  );
}
