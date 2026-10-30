import { useEffect, useRef, useState } from "react";
import type { CSSProperties, RefObject } from "react";
import type { CropAnalysis, Evidence, Finding, Segment } from "./types";

export const timecode = (seconds: number) => {
  const ms = Math.max(
    0,
    Math.round((Number.isFinite(seconds) ? seconds : 0) * 1000),
  );
  return `${String(Math.floor(ms / 60000)).padStart(2, "0")}:${String(Math.floor(ms / 1000) % 60).padStart(2, "0")}.${String(ms % 1000).padStart(3, "0")}`;
};

// Presentation union only: synthetic display IDs are never sent to model endpoints.
export function measuredFindings(
  findings: Finding[],
  groundedOmissions?: Evidence["omission_evidence"],
): Finding[] {
  const measuredCuts: Finding[] = [...findings];
  for (const [index, interval] of (
    groundedOmissions?.omissions || []
  ).entries()) {
    if (
      !measuredCuts.some(
        (f) =>
          f.kind === "omission" &&
          Math.abs(f.source_start - interval.source_start) < 0.01 &&
          Math.abs(f.source_end - interval.source_end) < 0.01,
      )
    ) {
      measuredCuts.push({
        id: `grounded-cut-${index}`,
        kind: "omission",
        source_start: interval.source_start,
        source_end: interval.source_end,
        edited_start: interval.edit_position,
        modality: interval.matched_evidence.modality,
      });
    }
  }
  return measuredCuts;
}

export function SpatialOverlay({
  crop,
  opacity,
}: {
  crop: CropAnalysis;
  opacity: number;
}) {
  const box = crop.crop_box,
    resolution = crop.source_resolution;
  if (!crop.detected || !box || !resolution) return null;
  const [w, h] = resolution;
  const arm = Math.min(w, h) * 0.035;
  return (
    <svg
      className="spatial-overlay"
      viewBox={`0 0 ${w} ${h}`}
      aria-hidden="true"
    >
      <g opacity={opacity}>
        {crop.omitted_margins?.map((m) => (
          <rect
            key={m.name}
            {...{ x: m.x, y: m.y, width: m.width, height: m.height }}
            fill="#f43f5e"
            fillOpacity=".55"
          />
        ))}
      </g>
      <g
        stroke="#ffffff"
        strokeOpacity=".16"
        strokeWidth="1"
        vectorEffect="non-scaling-stroke"
      >
        <path d={`M ${w / 2} 0 V ${h} M 0 ${h / 2} H ${w}`} />
      </g>
      <rect
        {...box}
        fill="none"
        stroke="#10b981"
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
      <g
        className="crop-reticles"
        stroke="#6ee7b7"
        strokeWidth="4"
        fill="none"
        vectorEffect="non-scaling-stroke"
      >
        {[
          [box.x, box.y, 1, 1],
          [box.x + box.width, box.y, -1, 1],
          [box.x, box.y + box.height, 1, -1],
          [box.x + box.width, box.y + box.height, -1, -1],
        ].map(([x, y, dx, dy], i) => (
          <path key={i} d={`M ${x + dx * arm} ${y} H ${x} V ${y + dy * arm}`} />
        ))}
      </g>
    </svg>
  );
}

interface Props {
  media: { source: string; edited: string };
  sourceRef: RefObject<HTMLVideoElement | null>;
  editedRef: RefObject<HTMLVideoElement | null>;
  segments: Segment[];
  findings: Finding[];
  groundedOmissions?: Evidence["omission_evidence"];
  editedDuration: number;
  linked: boolean;
  onLink: (linked: boolean) => void;
  onEditedUpdate: () => void;
  onSourceUpdate?: () => void;
  onReveal: (finding: Finding) => void;
  crop?: CropAnalysis;
  onLoaded?: (media: "source" | "edited") => void;
  onError?: (media: "source" | "edited") => void;
}

export function ForensicPlayer(props: Props) {
  const {
    media,
    sourceRef,
    editedRef,
    segments,
    findings,
    linked,
    onLink,
    crop,
  } = props;
  const [curtain, setCurtain] = useState(false);
  const [split, setSplit] = useState(50);
  const [opacity, setOpacity] = useState(0.5);
  const [showMask, setShowMask] = useState(true);
  const [position, setPosition] = useState(0);
  const [sourcePosition, setSourcePosition] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [hover, setHover] = useState<number | null>(null);
  const [playbackError, setPlaybackError] = useState("");
  const [rate, setRate] = useState(1);
  const reverse = useRef<ReturnType<typeof setInterval> | null>(null);
  const preview = useRef<HTMLVideoElement>(null);
  const latest = useRef(props);
  latest.current = props;
  const duration = props.editedDuration || 0;
  const measuredCuts = measuredFindings(findings, props.groundedOmissions);
  const omissions = measuredCuts
    .filter((f) => f.kind === "omission")
    .sort((a, b) => a.source_start - b.source_start);
  const stopReverse = () => {
    if (reverse.current !== null) clearInterval(reverse.current);
    reverse.current = null;
  };
  useEffect(
    () => () => {
      if (reverse.current !== null) clearInterval(reverse.current);
    },
    [],
  );
  useEffect(() => {
    if (preview.current && preview.current.readyState >= 1 && hover !== null)
      preview.current.currentTime = hover;
  }, [hover]);
  const pause = () => {
    stopReverse();
    editedRef.current?.pause();
    sourceRef.current?.pause();
    setPlaying(false);
    setRate(1);
    setPlaybackError("");
  };
  const seek = (value: number) => {
    const p = latest.current;
    const player = p.editedRef.current;
    if (!player || player.readyState < 1) return;
    player.currentTime = Math.max(0, Math.min(value, p.editedDuration));
    setPosition(player.currentTime);
    const interval = p.segments.find(
      (s) =>
        s.kind === "match" &&
        player.currentTime >= s.edited_start &&
        player.currentTime < s.edited_end,
    );
    if (
      p.linked &&
      interval?.source_start != null &&
      p.sourceRef.current?.readyState
    ) {
      p.sourceRef.current.currentTime =
        interval.source_start + player.currentTime - interval.edited_start;
      setSourcePosition(p.sourceRef.current.currentTime);
    }
    p.onEditedUpdate();
  };
  const play = (speed = 1) => {
    stopReverse();
    setPlaybackError("");
    setRate(speed);
    if (editedRef.current) {
      editedRef.current.playbackRate = speed;
      if (sourceRef.current) sourceRef.current.playbackRate = speed;
      void editedRef.current.play().catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        setPlaying(false);
        setPlaybackError(
          "Playback unavailable. Reload the media or use its native controls.",
        );
      });
    }
  };
  const toggle = () => {
    if (reverse.current || !editedRef.current?.paused) pause();
    else play();
  };
  const shuttleBack = () => {
    pause();
    setRate(-1);
    setPlaying(true);
    reverse.current = setInterval(() => {
      const current = latest.current.editedRef.current?.currentTime || 0;
      if (current <= 0) {
        stopReverse();
        setPlaying(false);
        return;
      }
      seek(current - 0.1);
    }, 100);
  };
  const snap = (direction: -1 | 1) => {
    const t = sourceRef.current?.currentTime || 0;
    const cut =
      direction === 1
        ? omissions.find((f) => f.source_start > t + 0.01)
        : [...omissions].reverse().find((f) => f.source_start < t - 0.01);
    if (cut) {
      pause();
      props.onReveal(cut);
    }
  };
  const commands = useRef({
    toggle,
    pause,
    play,
    shuttleBack,
    snap,
    rate,
    playing,
  });
  commands.current = { toggle, pause, play, shuttleBack, snap, rate, playing };
  useEffect(() => {
    const keyboard = (event: KeyboardEvent) => {
      if (
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.repeat ||
        event.isComposing
      )
        return;
      const target = event.target as HTMLElement;
      if (
        target.closest(
          "input, textarea, select, [contenteditable=true], dialog",
        )
      )
        return;
      // Preserve native activation while allowing shuttle keys after toolbar clicks.
      if (event.key === " " && target.closest("button, a, video")) return;
      const c = commands.current;
      switch (event.key.toLowerCase()) {
        case " ":
          event.preventDefault();
          c.toggle();
          break;
        case "j":
          event.preventDefault();
          c.shuttleBack();
          break;
        case "k":
          event.preventDefault();
          c.pause();
          break;
        case "l":
          event.preventDefault();
          c.play(c.playing && c.rate > 0 ? Math.min(c.rate * 2, 4) : 1);
          break;
        case "[":
          event.preventDefault();
          c.snap(-1);
          break;
        case "]":
          event.preventDefault();
          c.snap(1);
          break;
        case "m":
          event.preventDefault();
          setCurtain((v) => !v);
          break;
      }
    };
    window.addEventListener("keydown", keyboard);
    return () => window.removeEventListener("keydown", keyboard);
  }, []);
  // The API exposes interval confidence, not raw waveform or per-frame features.
  const bins = Math.min(2400, Math.ceil(duration * 4));
  const confidenceBins = Array.from({ length: bins }, (_, i) => {
    const t = (i / bins) * duration;
    return (
      segments.find(
        (s) => s.kind === "match" && t >= s.edited_start && t < s.edited_end,
      )?.confidence ?? 0
    );
  });
  const activeOmission = omissions.find(
    (f) => sourcePosition >= f.source_start && sourcePosition < f.source_end,
  );
  return (
    <div
      className="forensic-player"
      role="region"
      aria-label="Forensic video transport"
      aria-keyshortcuts="Space J K L M"
    >
      <div className="transport-heading">
        <div className="segmented-control" aria-label="Comparison layout">
          <button
            className={!curtain ? "active" : ""}
            aria-pressed={!curtain}
            onClick={() => setCurtain(false)}
          >
            ▥ Side by side
          </button>
          <button
            className={curtain ? "active" : ""}
            aria-pressed={curtain}
            onClick={() => setCurtain(true)}
          >
            ◧ Curtain <kbd>M</kbd>
          </button>
        </div>
        <span className="micro-label">
          {linked ? "TIMELINE LINKED" : "INDEPENDENT FEEDS"}
        </span>
      </div>
      <div
        className={`players forensic-stage ${curtain ? "curtain-mode" : ""}`}
        style={{ "--curtain": `${split}%` } as CSSProperties}
      >
        {(["edited", "source"] as const).map((kind, i) => (
          <div className={`player feed-${kind}`} key={kind}>
            <div className="player-title">
              <span>
                <b>0{i + 1}</b> {i ? "ORIGINAL SOURCE" : "PUBLISHED EDIT"}
              </span>
              <span>{timecode(i ? sourcePosition : position)}</span>
            </div>
            <div className="video-viewport">
              <video
                ref={i ? sourceRef : editedRef}
                src={media[kind]}
                controls={!curtain}
                playsInline
                preload="metadata"
                muted={i === 1 && linked}
                onLoadedMetadata={() => {
                  setPlaybackError("");
                  props.onLoaded?.(kind);
                }}
                onError={() => {
                  setPlaybackError(
                    `${kind === "source" ? "Source" : "Published"} media could not be loaded.`,
                  );
                  props.onError?.(kind);
                }}
                onTimeUpdate={() => {
                  if (i) {
                    setSourcePosition(sourceRef.current?.currentTime || 0);
                    props.onSourceUpdate?.();
                  } else {
                    setPosition(editedRef.current?.currentTime || 0);
                    props.onEditedUpdate();
                  }
                }}
                onPlay={() => {
                  if (!i) {
                    setPlaying(true);
                    props.onEditedUpdate();
                  }
                }}
                onPause={() => {
                  if (!i) {
                    setPlaying(false);
                    if (linked) sourceRef.current?.pause();
                  }
                }}
                onSeeked={() => {
                  if (!i) props.onEditedUpdate();
                }}
              />
              {i === 1 && crop && showMask && (
                <SpatialOverlay crop={crop} opacity={opacity} />
              )}
            </div>
            <div className="player-foot">
              {i ? "SOURCE COORDINATES" : "EDITED CHRONOLOGY"}
              <span className={i ? "blue" : "orange"}>●</span>
            </div>
          </div>
        ))}
        {curtain && (
          <>
            <div className="curtain-rule" style={{ left: `${split}%` }}>
              <span>↔</span>
            </div>
            <input
              className="curtain-slider"
              aria-label="Curtain split position"
              type="range"
              min="0"
              max="100"
              value={split}
              onChange={(e) => setSplit(Number(e.target.value))}
            />
          </>
        )}
      </div>
      {crop?.detected && crop.crop_box && (
        <div className="spatial-hud">
          <div>
            <span className="precision-dot" /> SPATIAL GEOMETRY{" "}
            <strong>
              {crop.crop_box.width}×{crop.crop_box.height}
            </strong>
            <span>Δx +{crop.crop_box.x}px</span>
            <span>Δy +{crop.crop_box.y}px</span>
            <span>
              Area removed{" "}
              {crop.area_omitted_fraction == null
                ? "unavailable"
                : `${(crop.area_omitted_fraction * 100).toFixed(1)}%`}
            </span>
            {crop.source_resolution && (
              <span>
                Width retained{" "}
                {(crop.crop_box.width / crop.source_resolution[0]).toFixed(2)}×
              </span>
            )}
          </div>
          <label>
            <input
              type="checkbox"
              checked={showMask}
              onChange={(e) => setShowMask(e.target.checked)}
            />{" "}
            Crop overlay
          </label>
          <label>
            Mask opacity{" "}
            <input
              aria-label="Peripheral mask opacity"
              type="range"
              min="0"
              max="100"
              value={opacity * 100}
              onChange={(e) => setOpacity(Number(e.target.value) / 100)}
            />
            <output>{Math.round(opacity * 100)}%</output>
          </label>
        </div>
      )}
      <div className="transport-bar">
        <div className="transport-buttons">
          <button
            className="quiet"
            aria-label="Previous omission"
            onClick={() => snap(-1)}
          >
            │‹
          </button>
          <button
            className="play-control"
            aria-label={
              playing ? "Pause synchronized feeds" : "Play synchronized feeds"
            }
            onClick={toggle}
          >
            {playing ? "Ⅱ" : "▶"}
          </button>
          <button
            className="quiet"
            aria-label="Next omission"
            onClick={() => snap(1)}
          >
            ›│
          </button>
        </div>
        <output className="transport-time">
          {timecode(position)} <span>/ {timecode(duration)}</span>
        </output>
        <button
          className="quiet link-control"
          aria-pressed={linked}
          onClick={() => onLink(!linked)}
        >
          {linked ? "⇄ Linked" : "↔ Unlinked"}
        </button>
        <span className="rate-indicator">{rate}×</span>
      </div>
      {playbackError && (
        <p role="alert" className="error">
          {playbackError}
        </p>
      )}
      <div
        className="scrubber-shell"
        onPointerMove={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          setHover(
            Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)) *
              duration,
          );
        }}
        onPointerLeave={() => setHover(null)}
      >
        <div className="confidence-strip" aria-hidden="true">
          <svg
            viewBox={`0 0 ${Math.max(1, bins) * 4} 100`}
            preserveAspectRatio="none"
          >
            {confidenceBins.map((c, i) => {
              const height = Math.max(6, Math.min(1, Math.max(0, c)) * 100);
              return (
                <rect
                  key={i}
                  x={i * 4}
                  y={(100 - height) / 2}
                  width="3"
                  height={height}
                  opacity={c ? 0.4 + c * 0.6 : 0.15}
                  fill="#38bdf8"
                />
              );
            })}
          </svg>
        </div>
        <input
          aria-label="Edited video playhead"
          type="range"
          min="0"
          max={duration}
          step="0.001"
          value={Math.min(position, duration)}
          onChange={(e) => {
            pause();
            seek(Number(e.target.value));
          }}
        />
        {hover !== null && (
          <div
            className="frame-preview"
            style={{
              left: `${Math.max(12, Math.min(88, duration ? (hover / duration) * 100 : 0))}%`,
            }}
          >
            <video
              ref={preview}
              src={media.edited}
              muted
              playsInline
              preload="metadata"
              onLoadedMetadata={() => {
                if (preview.current) preview.current.currentTime = hover;
              }}
            />
            <span>EDIT FRAME · {timecode(hover)}</span>
          </div>
        )}
      </div>
      <div className="timeline-caption">
        <span>ALIGNMENT CONFIDENCE · 4 Hz DISPLAY</span>
        <span>Interval scores · not audio amplitude</span>
      </div>
      <div className="omission-chips">
        {omissions.map((f) => (
          <button
            key={f.id}
            className={`omission-chip ${activeOmission?.id === f.id ? "is-active" : ""}`}
            onClick={() => {
              pause();
              props.onReveal(f);
            }}
          >
            ◈ Omission zone {f.modality ? `· ${f.modality}` : ""}{" "}
            <span>
              {timecode(f.source_start)} — {timecode(f.source_end)}
            </span>
          </button>
        ))}
        {!omissions.length && (
          <span className="micro-label">No measured internal omissions</span>
        )}
      </div>
      <div className="shortcut-legend">
        <span>
          <kbd>Space</kbd> play / pause
        </span>
        <span>
          <kbd>J</kbd>
          <kbd>K</kbd>
          <kbd>L</kbd> shuttle
        </span>
        <span>
          <kbd>[</kbd>
          <kbd>]</kbd> cuts
        </span>
        <span>
          <kbd>M</kbd> curtain
        </span>
      </div>
    </div>
  );
}
