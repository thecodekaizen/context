import React from 'react';

interface HeaderProps {
  mode: 'real_dataset' | 'live_upload';
  onToggleMode: (mode: 'real_dataset' | 'live_upload') => void;
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
        <div className="brand-logo" aria-label="VEIL Homepage">
          <span className="brand-motif" aria-hidden="true" />
          <span>VEIL</span>
        </div>
        <span className="brand-tagline">Multimodal Video Privacy Engine</span>
      </div>

      <div className="header-actions">
        <div
          className={`mode-badge live ${!backendOnline ? 'offline' : ''}`}
          title="Connected to loopback engine API at http://127.0.0.1:8020"
        >
          <span>●</span>
          <span>Local Engine API {backendOnline ? 'Online (8020)' : 'Offline (127.0.0.1:8020)'}</span>
        </div>

        <button
          className={`toggle-btn ${mode === 'real_dataset' ? 'active-toggle' : ''}`}
          onClick={() => onToggleMode('real_dataset')}
          title="Browse and inspect real dataset benchmark videos"
        >
          🎬 Real Video Testbed
        </button>

        <button
          className={`toggle-btn ${mode === 'live_upload' ? 'active-toggle' : ''}`}
          onClick={() => onToggleMode('live_upload')}
          title="Process a local video file live through the VEIL API"
        >
          📤 Live Job Runner
        </button>

        <button onClick={onOpenReceipt} className="toggle-btn" title="View machine-readable verification receipt">
          Audit Receipt
        </button>

        <button onClick={onOpenEmbed} className="primary" title="View embeddable Python SDK example">
          SDK Integration
        </button>
      </div>
    </header>
  );
};
