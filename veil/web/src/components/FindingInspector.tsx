import React from 'react';
import type { Finding } from '../types';

interface FindingInspectorProps {
  findings: Finding[];
  selectedFinding: Finding | null;
  onSelectFinding: (finding: Finding) => void;
  onSeek: (ms: number) => void;
}

export const FindingInspector: React.FC<FindingInspectorProps> = ({
  findings,
  selectedFinding,
  onSelectFinding,
  onSeek,
}) => {
  return (
    <div className="sidebar-panel" aria-label="Detected privacy findings">
      <div className="panel-header">
        <h3 className="panel-title">Detected Findings ({findings.length})</h3>
        <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
          Saved real inference
        </span>
      </div>

      <div className="findings-list">
        {findings.map((f) => {
          const isSelected = selectedFinding?.id === f.id;
          const isResidual = f.status === 'unprotected_residual';

          return (
            <div
              key={f.id}
              className={`finding-row ${isSelected ? 'selected' : ''} ${isResidual ? 'residual-alert' : ''}`}
              onClick={() => {
                onSelectFinding(f);
                onSeek(f.start_ms);
              }}
              role="button"
              tabIndex={0}
              aria-pressed={isSelected}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  onSelectFinding(f);
                  onSeek(f.start_ms);
                }
              }}
            >
              <div className="finding-top">
                <span className="finding-name">{f.title}</span>
                <span className="finding-time">
                  {(f.start_ms / 1000).toFixed(1)}s - {(f.end_ms / 1000).toFixed(1)}s
                </span>
              </div>

              <div className="finding-meta">
                <span>{f.source}</span>
                <span className={`status-chip ${isResidual ? 'residual' : 'protected'}`}>
                  {f.statusLabel}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Finding Detail Card */}
      {selectedFinding && (
        <div style={{ marginTop: '8px', padding: '12px', background: 'var(--color-control-bg)', borderRadius: '8px', border: '1px solid var(--color-border-subtle)', fontSize: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <strong>Finding Details</strong>
            <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-accent-protect)' }}>
              {selectedFinding.id}
            </span>
          </div>

          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '8px', lineHeight: 1.4 }}>
            {selectedFinding.description}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', color: 'var(--color-text-muted)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
            <div>Model Source: {selectedFinding.source}</div>
            <div>
              Confidence: {selectedFinding.confidence !== null ? `${selectedFinding.confidence * 100}%` : 'Null (not supplied by provider)'}
            </div>
          </div>

          <button
            style={{ marginTop: '10px', width: '100%' }}
            onClick={() => onSeek(selectedFinding.start_ms)}
          >
            Seek to finding timestamp ({ (selectedFinding.start_ms / 1000).toFixed(1) }s)
          </button>
        </div>
      )}
    </div>
  );
};
