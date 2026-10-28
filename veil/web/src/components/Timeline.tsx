import React, { useRef } from 'react';

interface TimelineProps {
  currentTimeMs: number;
  durationMs: number;
  onSeek: (ms: number) => void;
  onSelectFindingById: (id: string) => void;
}

export const Timeline: React.FC<TimelineProps> = ({
  currentTimeMs,
  durationMs,
  onSeek,
  onSelectFindingById,
}) => {
  const scrubberRef = useRef<HTMLDivElement>(null);

  const handleScrubberClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!scrubberRef.current) return;
    const rect = scrubberRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const fraction = Math.max(0, Math.min(1, clickX / rect.width));
    const targetMs = Math.round(fraction * durationMs);
    onSeek(targetMs);
  };

  const progressPercent = Math.max(0, Math.min(100, (currentTimeMs / durationMs) * 100));

  return (
    <div className="timeline-panel" aria-label="Privacy finding tracks">
      <div className="panel-header">
        <span className="panel-title">Multi-Track Privacy Timeline (00:00 - 00:18)</span>
        <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
          Click anywhere along the timeline to inspect evidence
        </span>
      </div>

      {/* Scrubber Area */}
      <div
        ref={scrubberRef}
        className="timeline-scrubber"
        onClick={handleScrubberClick}
        role="slider"
        aria-label="Video scrubber"
        aria-valuemin={0}
        aria-valuemax={durationMs}
        aria-valuenow={currentTimeMs}
      >
        {/* Track 1: Face (full video) */}
        <div
          className="scrubber-marker face"
          style={{ left: '0%', width: '100%', top: '0', height: '6px' }}
          title="Face track: 0.0s - 18.0s (SAM 3.1 video)"
          onClick={(e) => { e.stopPropagation(); onSelectFindingById('face-01'); }}
        />

        {/* Track 2: Plate (full video) */}
        <div
          className="scrubber-marker plate"
          style={{ left: '0%', width: '100%', top: '7px', height: '6px' }}
          title="Plate track: 0.0s - 18.0s (Spark 1.3 seed + SAM 3.1)"
          onClick={(e) => { e.stopPropagation(); onSelectFindingById('plate-01'); }}
        />

        {/* Track 3: Spoken Phone (1.3s - 5.1s) */}
        <div
          className="scrubber-marker speech"
          style={{ left: `${(1300 / 18000) * 100}%`, width: `${((5100 - 1300) / 18000) * 100}%`, top: '14px', height: '6px' }}
          title="Spoken phone audio interval: 1.3s - 5.1s (Voice ASR Mute)"
          onClick={(e) => { e.stopPropagation(); onSeek(1300); onSelectFindingById('speech-01'); }}
        />

        {/* Track 4: Printed Phone Residual (7.5s - 8.5s) */}
        <div
          className="scrubber-marker phone-residual"
          style={{ left: `${(7500 / 18000) * 100}%`, width: `${(1000 / 18000) * 100}%`, top: '21px', height: '7px' }}
          title="HERO MOMENT: Omitted Placard Phone Number caught at 00:07.500"
          onClick={(e) => { e.stopPropagation(); onSeek(7500); onSelectFindingById('phone-residual-01'); }}
        />

        {/* Playhead Progress Bar */}
        <div className="timeline-progress-bar" style={{ width: `${progressPercent}%` }} />
      </div>

      {/* Tracks Legend */}
      <div className="tracks-legend">
        <div className="legend-item" onClick={() => onSelectFindingById('face-01')} style={{ cursor: 'pointer' }}>
          <span className="legend-dot face" />
          <span>Driver Face (SAM 3.1)</span>
        </div>
        <div className="legend-item" onClick={() => onSelectFindingById('plate-01')} style={{ cursor: 'pointer' }}>
          <span className="legend-dot plate" />
          <span>Vehicle Plate (Spark+SAM)</span>
        </div>
        <div className="legend-item" onClick={() => onSelectFindingById('speech-01')} style={{ cursor: 'pointer' }}>
          <span className="legend-dot speech" />
          <span>Spoken Speech (Voice Mute)</span>
        </div>
        <div className="legend-item" onClick={() => { onSeek(7500); onSelectFindingById('phone-residual-01'); }} style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--color-accent-red)' }}>
          <span className="legend-dot residual" />
          <span>⚠ Residual Phone Exposure (00:07.500)</span>
        </div>
      </div>
    </div>
  );
};
