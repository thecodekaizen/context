import React from 'react';
import type { OperatingMode } from '../types';

interface HeaderProps {
  mode: OperatingMode;
  onToggleMode: (mode: OperatingMode) => void;
  onOpenEmbed: () => void;
  onOpenReceipt: () => void;
  backendOnline: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  mode,
  onToggleMode,
  onOpenEmbed,
  onOpenReceipt,
  backendOnline,
}) => {
  return (
    <header className="app-header">
      <div className="brand-section">
        <a href="#" className="brand-logo" aria-label="VEIL Homepage">
          <span className="brand-motif" aria-hidden="true" />
          <span>VEIL</span>
        </a>
        <span className="brand-tagline">Detect. Redact. Verify.</span>
      </div>

      <div className="header-actions">
        {mode === 'recorded' ? (
          <div className="mode-badge" title="Inspecting archived synthetic smoke-test results with saved real Meta inference.">
            <span>●</span>
            <span>Recorded example · saved real inference</span>
          </div>
        ) : (
          <div className={`mode-badge live ${!backendOnline ? 'offline' : ''}`} title="Connected to loopback engine API at http://127.0.0.1:8018">
            <span>●</span>
            <span>Local API {backendOnline ? 'online' : 'offline (127.0.0.1:8018)'}</span>
          </div>
        )}

        <button
          className="toggle-btn"
          onClick={() => onToggleMode(mode === 'recorded' ? 'live' : 'recorded')}
          title="Switch between the recorded demonstration and live API job execution"
        >
          {mode === 'recorded' ? 'Switch to Live API' : 'Switch to Recorded Example'}
        </button>

        <button onClick={onOpenReceipt} className="toggle-btn" title="View machine-readable verification receipt">
          Audit Receipt
        </button>

        <button onClick={onOpenEmbed} className="primary" title="View embeddable Python SDK example">
          Embed Engine
        </button>
      </div>
    </header>
  );
};
