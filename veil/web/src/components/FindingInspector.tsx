import React from 'react';
import type { DatasetClip } from '../data/real-datasets';
import type { RedactionStyle, Finding } from '../types';

interface FindingInspectorProps {
  clip: DatasetClip;
  redactionStyle: RedactionStyle;
  onOpenReceipt: () => void;
  selectedFinding?: Finding | null;
  onSelectFinding?: (finding: Finding) => void;
}

export const FindingInspector: React.FC<FindingInspectorProps> = ({
  clip,
  redactionStyle,
  onOpenReceipt,
  selectedFinding,
  onSelectFinding,
}) => {
  return (
    <div className="sidebar-panel" aria-label="Detected privacy findings and inspection">
      <div className="panel-header">
        <h3 className="panel-title">Active Benchmark Telemetry</h3>
        <span className="badge-pill">{clip.resolution} · {clip.fps} fps</span>
      </div>

      <div className="telemetry-card">
        <div className="telemetry-row">
          <span className="label">Dataset Provenance:</span>
          <span className="value">{clip.badge}</span>
        </div>
        <div className="telemetry-row">
          <span className="label">Active Redaction Mode:</span>
          <span className={`value-badge ${redactionStyle === 'natural' ? 'natural' : 'opaque'}`}>
            {clip.isTriView
              ? 'Synchronized Tri-View'
              : redactionStyle === 'natural'
              ? '🛡 Natural Replacement (DEMO / Blur)'
              : '⬛ Opaque Covers (Hard Black Box)'}
          </span>
        </div>
      </div>

      <div className="section-divider">
        <h4>Protected Targets ({clip.tracks.length})</h4>
      </div>

      <div className="findings-list">
        {clip.tracks.map((t) => {
          const isSelected = selectedFinding?.id === t.id;
          return (
            <div
              key={t.id}
              className={`finding-row ${isSelected ? 'selected' : ''}`}
              style={{ cursor: onSelectFinding ? 'pointer' : 'default' }}
              onClick={() => {
                onSelectFinding?.({
                  id: t.id,
                  title: t.label,
                  category: t.category,
                  start_ms: 0,
                  end_ms: clip.durationMs,
                  source: 'ground_truth',
                  status: 'protected',
                  statusLabel: 'Protected',
                  description: t.naturalDetails,
                });
              }}
            >
              <div className="finding-top">
                <span className="finding-name">{t.label}</span>
                <span className="category-tag">{t.category}</span>
              </div>
              <div className="finding-meta">
                <span className="strategy-tag">
                  {redactionStyle === 'natural' && !clip.isTriView ? t.treatment : 'Opaque Black Rectangle ([y1:y2, x1:x2] = 0)'}
                </span>
              </div>
              <p className="finding-desc">
                {redactionStyle === 'natural' && !clip.isTriView ? t.naturalDetails : 'Standard conservative rectangular cover. Opaque pixels inside the selected region; missed regions remain possible.'}
              </p>
            </div>
          );
        })}
      </div>

      <div className="section-divider">
        <h4>Exported-Pixel OCR Verification</h4>
      </div>

      <div className="audit-metrics-grid">
        <div className="metric-box">
          <span className="metric-num">{clip.auditMetrics.scannedFrames}</span>
          <span className="metric-label">Decoded Frames</span>
        </div>
        <div className="metric-box clean">
          <span className="metric-num">{clip.auditMetrics.residualsFound}</span>
          <span className="metric-label">Leaked Residuals</span>
        </div>
        <div className="metric-box clean">
          <span className="metric-num">{clip.auditMetrics.blackouts}</span>
          <span className="metric-label">Blackout Frames</span>
        </div>
        <div className="metric-box">
          <span className="metric-num">{clip.auditMetrics.meanOutsideDiff}</span>
          <span className="metric-label">Outside Diff</span>
        </div>
      </div>

      <div className="safety-callout">
        <div className="callout-header">
          <span className="callout-icon">ℹ</span>
          <strong>Why Do Black Boxes Ever Appear in Natural Mode?</strong>
        </div>
        <p className="callout-text">
          When tracking fails or replacement corners leave the protective region, VEIL uses an opaque cover. The exported file still needs inspection: incorrect detection regions can leave information exposed. Natural replacement is experimental.
        </p>
      </div>

      <button className="primary receipt-btn" onClick={onOpenReceipt}>
        View Full Machine-Readable Audit Receipt
      </button>
    </div>
  );
};
