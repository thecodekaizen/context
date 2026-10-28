import React, { useRef, useEffect, useState, useCallback } from 'react';
import type { Finding } from '../types';

interface VideoDeskProps {
  primaryUrl: string;
  secondaryUrl: string;
  primaryBadge: string;
  secondaryBadge: string;
  currentTimeMs: number;
  onSeek: (ms: number) => void;
  selectedFinding?: Finding | null;
  isPairedView: boolean;
  onTogglePaired: () => void;
  isTriView?: boolean;
}

function formatTime(ms: number): string {
  const totalSeconds = Math.max(0, ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  const fraction = Math.floor((totalSeconds % 1) * 1000);
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(fraction).padStart(3, '0')}`;
}

export const VideoDesk: React.FC<VideoDeskProps> = ({
  primaryUrl,
  secondaryUrl,
  primaryBadge,
  secondaryBadge,
  currentTimeMs,
  onSeek,
  isPairedView,
  isTriView,
}) => {
  const primaryVideoRef = useRef<HTMLVideoElement>(null);
  const secondaryVideoRef = useRef<HTMLVideoElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [durationMs, setDurationMs] = useState(8000);

  // Sync external seek
  useEffect(() => {
    const targetSeconds = currentTimeMs / 1000;
    if (primaryVideoRef.current && Math.abs(primaryVideoRef.current.currentTime - targetSeconds) > 0.15) {
      primaryVideoRef.current.currentTime = targetSeconds;
    }
    if (secondaryVideoRef.current && Math.abs(secondaryVideoRef.current.currentTime - targetSeconds) > 0.15) {
      secondaryVideoRef.current.currentTime = targetSeconds;
    }
  }, [currentTimeMs]);

  // Sync secondary video when primary updates time
  const handleTimeUpdate = useCallback(() => {
    if (!primaryVideoRef.current) return;
    const currentMs = Math.round(primaryVideoRef.current.currentTime * 1000);
    onSeek(currentMs);

    if (secondaryVideoRef.current && isPairedView && !isTriView) {
      const diff = Math.abs(secondaryVideoRef.current.currentTime - primaryVideoRef.current.currentTime);
      if (diff > 0.1) {
        secondaryVideoRef.current.currentTime = primaryVideoRef.current.currentTime;
      }
    }
  }, [onSeek, isPairedView, isTriView]);

  const togglePlay = () => {
    if (!primaryVideoRef.current) return;
    if (isPlaying) {
      primaryVideoRef.current.pause();
      secondaryVideoRef.current?.pause();
      setIsPlaying(false);
    } else {
      primaryVideoRef.current.play().catch(() => {});
      if (isPairedView && !isTriView) {
        secondaryVideoRef.current?.play().catch(() => {});
      }
      setIsPlaying(true);
    }
  };

  const handleLoadedMetadata = () => {
    if (primaryVideoRef.current) {
      const dur = Math.round(primaryVideoRef.current.duration * 1000);
      if (!isNaN(dur) && dur > 0) {
        setDurationMs(dur);
      }
    }
  };

  const handleSliderSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const ms = Number(e.target.value);
    onSeek(ms);
    const sec = ms / 1000;
    if (primaryVideoRef.current) primaryVideoRef.current.currentTime = sec;
    if (secondaryVideoRef.current) secondaryVideoRef.current.currentTime = sec;
  };

  return (
    <section className="video-desk" aria-label="Video Inspection Surface">
      <div className={!isTriView && isPairedView ? 'paired-desk' : 'player-container'}>
        {/* Primary Screen (Redacted or Natural or Tri-View) */}
        <div className="video-pane">
          <div className="pane-badge clean">
            {primaryBadge}
          </div>
          <video
            ref={primaryVideoRef}
            src={primaryUrl}
            className="video-element"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            playsInline
            controls={false}
          />
        </div>

        {/* Secondary Screen (Source Reference in Paired View) */}
        {!isTriView && isPairedView && (
          <div className="video-pane">
            <div className="pane-badge">{secondaryBadge}</div>
            <video
              ref={secondaryVideoRef}
              src={secondaryUrl}
              className="video-element"
              playsInline
              muted
              controls={false}
            />
          </div>
        )}
      </div>

      {/* Scrubber Slider */}
      <div className="scrubber-bar">
        <input
          type="range"
          min={0}
          max={durationMs}
          value={currentTimeMs}
          onChange={handleSliderSeek}
          className="scrub-slider"
          aria-label="Video scrubber"
        />
      </div>

      {/* Desk Controls Bar */}
      <div className="desk-controls">
        <div className="playback-buttons">
          <button onClick={togglePlay} className="primary" aria-label={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? '⏸ Pause' : '▶ Play'}
          </button>
          <button onClick={() => onSeek(0)} aria-label="Rewind to start">
            ⏮ 00:00.000
          </button>
          <button
            onClick={() => {
              const prev = Math.max(0, currentTimeMs - 1000 / 12);
              onSeek(prev);
              if (primaryVideoRef.current) primaryVideoRef.current.currentTime = prev / 1000;
            }}
            title="Step backward 1 frame"
          >
            ◀ Frame
          </button>
          <button
            onClick={() => {
              const next = Math.min(durationMs, currentTimeMs + 1000 / 12);
              onSeek(next);
              if (primaryVideoRef.current) primaryVideoRef.current.currentTime = next / 1000;
            }}
            title="Step forward 1 frame"
          >
            Frame ▶
          </button>
        </div>

        <div className="timestamp-display" aria-label="Current video timestamp">
          {formatTime(currentTimeMs)} / {formatTime(durationMs)}
        </div>

        <div className="toggle-group">
          <span className="mode-indicator-pill">
            {isTriView
              ? 'Tri-View: Original vs Opaque vs Natural'
              : isPairedView
              ? 'Synchronized Dual View'
              : 'Single Export View'}
          </span>
        </div>
      </div>
    </section>
  );
};
