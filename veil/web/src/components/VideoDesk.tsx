import React, { useRef, useEffect, useState, useCallback } from 'react';
import type { Finding, VideoVersion } from '../types';
import { RECORDED_MEDIA_PATHS } from '../data/recorded-example';

interface VideoDeskProps {
  currentStage: string;
  videoVersion: VideoVersion;
  onSetVideoVersion: (version: VideoVersion) => void;
  currentTimeMs: number;
  onSeek: (ms: number) => void;
  selectedFinding: Finding | null;
  liveSourceUrl?: string | null;
  liveExportUrl?: string | null;
  mode: 'recorded' | 'live';
}

function formatTime(ms: number): string {
  const totalSeconds = Math.max(0, ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  const fraction = Math.floor((totalSeconds % 1) * 1000);
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(fraction).padStart(3, '0')}`;
}

export const VideoDesk: React.FC<VideoDeskProps> = ({
  videoVersion,
  onSetVideoVersion,
  currentTimeMs,
  onSeek,
  selectedFinding,
  liveSourceUrl,
  liveExportUrl,
  mode,
}) => {
  const primaryVideoRef = useRef<HTMLVideoElement>(null);
  const secondaryVideoRef = useRef<HTMLVideoElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [durationMs, setDurationMs] = useState(18000);
  const [isPairedView, setIsPairedView] = useState(true);
  const [showOverlays, setShowOverlays] = useState(true);

  // Determine media URLs
  let primaryUrl = '';
  let secondaryUrl = '';
  let primaryBadge = '';
  let secondaryBadge = '';

  if (mode === 'recorded') {
    primaryUrl = RECORDED_MEDIA_PATHS[videoVersion].url;
    primaryBadge = RECORDED_MEDIA_PATHS[videoVersion].badge;
    secondaryUrl = RECORDED_MEDIA_PATHS.source.url;
    secondaryBadge = RECORDED_MEDIA_PATHS.source.badge;
  } else {
    primaryUrl = liveExportUrl || liveSourceUrl || '';
    primaryBadge = liveExportUrl ? 'Exported Redaction' : 'Live Source Media';
    secondaryUrl = liveSourceUrl || '';
    secondaryBadge = 'Original Input';
  }

  // Handle external seeks
  useEffect(() => {
    const targetSeconds = currentTimeMs / 1000;
    if (primaryVideoRef.current && Math.abs(primaryVideoRef.current.currentTime - targetSeconds) > 0.15) {
      primaryVideoRef.current.currentTime = targetSeconds;
    }
    if (secondaryVideoRef.current && Math.abs(secondaryVideoRef.current.currentTime - targetSeconds) > 0.15) {
      secondaryVideoRef.current.currentTime = targetSeconds;
    }
  }, [currentTimeMs]);

  const handleTimeUpdate = useCallback(() => {
    if (!primaryVideoRef.current) return;
    const currentMs = Math.round(primaryVideoRef.current.currentTime * 1000);
    onSeek(currentMs);

    // Sync secondary video if paired
    if (secondaryVideoRef.current && isPairedView) {
      const diff = Math.abs(secondaryVideoRef.current.currentTime - primaryVideoRef.current.currentTime);
      if (diff > 0.1) {
        secondaryVideoRef.current.currentTime = primaryVideoRef.current.currentTime;
      }
    }
  }, [onSeek, isPairedView]);

  const togglePlay = () => {
    if (!primaryVideoRef.current) return;
    if (isPlaying) {
      primaryVideoRef.current.pause();
      secondaryVideoRef.current?.pause();
      setIsPlaying(false);
    } else {
      primaryVideoRef.current.play().catch(() => {});
      if (isPairedView) {
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

  // Check if phone residual is visible at current time
  const isResidualTime = currentTimeMs >= 7000 && currentTimeMs <= 8500;
  const isHeroResidual = selectedFinding?.id === 'phone-residual-01' || isResidualTime;

  return (
    <section className="video-desk" aria-label="Video Inspection Surface">
      <div className={isPairedView ? 'paired-desk' : 'player-container'}>
        {/* Primary Screen (Export / Processed Media) */}
        <div className="video-pane">
          <div className={`pane-badge ${isResidualTime && videoVersion === 'redacted' ? 'alert' : 'clean'}`}>
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

          {/* Real-time Bounding Box Overlays */}
          {showOverlays && (
            <div className="overlay-canvas" aria-hidden="true">
              {/* Highlight residual omitted phone number at 00:07.500 */}
              {isHeroResidual && videoVersion === 'redacted' && (
                <div
                  className="box-highlight exposed-residual"
                  style={{
                    left: '52%',
                    top: '46%',
                    width: '18%',
                    height: '12%',
                  }}
                  title="Unprotected residual phone number detected"
                />
              )}

              {/* Show selected finding bounding box */}
              {selectedFinding?.highlightBox && !isHeroResidual && (
                <div
                  className="box-highlight"
                  style={{
                    left: '42%',
                    top: '20%',
                    width: '16%',
                    height: '24%',
                  }}
                  title={selectedFinding.title}
                />
              )}
            </div>
          )}
        </div>

        {/* Secondary Screen (Source Reference in Paired View) */}
        {isPairedView && (
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

      {/* Desk Controls Bar */}
      <div className="desk-controls">
        <div className="playback-buttons">
          <button onClick={togglePlay} className="primary" aria-label={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? '⏸ Pause' : '▶ Play'}
          </button>
          <button onClick={() => onSeek(0)} aria-label="Rewind to start">
            ⏮ 00:00.000
          </button>
          <button onClick={() => onSeek(7500)} className={isResidualTime ? 'danger' : ''} aria-label="Seek to residual exposure at 00:07.500">
            ⚠ Seek to Residual (00:07.500)
          </button>
        </div>

        <div className="timestamp-display" aria-label="Current video timestamp">
          {formatTime(currentTimeMs)} / {formatTime(durationMs)}
        </div>

        <div className="toggle-group">
          {mode === 'recorded' && (
            <select
              value={videoVersion}
              onChange={(e) => onSetVideoVersion(e.target.value as VideoVersion)}
              className="toggle-btn"
              aria-label="Select export version to inspect"
            >
              <option value="redacted">Export 1: Missed Placard Number</option>
              <option value="repaired">Export 2: Rejected 1-Digit Repair</option>
              <option value="protected">Export 3: Corrected Full Cover</option>
              <option value="source">Original Unredacted Footage</option>
            </select>
          )}

          <button
            className={`toggle-btn ${isPairedView ? 'active' : ''}`}
            onClick={() => setIsPairedView(!isPairedView)}
            aria-pressed={isPairedView}
          >
            {isPairedView ? 'Side-by-Side: On' : 'Single View'}
          </button>

          <button
            className={`toggle-btn ${showOverlays ? 'active' : ''}`}
            onClick={() => setShowOverlays(!showOverlays)}
            aria-pressed={showOverlays}
          >
            {showOverlays ? 'Overlays: On' : 'Overlays: Off'}
          </button>
        </div>
      </div>
    </section>
  );
};
