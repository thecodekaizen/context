import React, { useState } from 'react';

interface EmbedDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EmbedDrawer: React.FC<EmbedDrawerProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const pythonSnippet = `from veil import VeilClient

# 1. Connect to local or remote VEIL engine API
with VeilClient(base_url="http://127.0.0.1:8018") as client:
    # 2. Upload video job
    job = client.create_job("raw_input.mp4")

    # 3. Apply reviewed frame-aligned privacy timeline
    # Note: Timeline contains validated geometry reviewed by caller or detection pass
    client.process(job["id"], timeline)

    # 4. Fetch machine-readable receipt & download redacted media
    receipt = client.receipt(job["id"])
    client.download(job["id"], "redacted_export.mp4")
`;

  const handleCopy = () => {
    navigator.clipboard.writeText(pythonSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="embed-title">
      <div className="modal-content" style={{ maxWidth: '640px' }}>
        <div className="modal-header">
          <div>
            <h2 id="embed-title" className="modal-title">Embed VEIL Privacy Engine</h2>
            <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
              Python SDK & HTTP API Integration
            </span>
          </div>
          <button onClick={onClose} aria-label="Close drawer">✕</button>
        </div>

        <p style={{ color: 'var(--color-text-secondary)', fontSize: '13px' }}>
          VEIL is designed as an embeddable engine. Third-party video pipelines upload footage, submit a validated timeline, and stream redacted media with cryptographic receipts.
        </p>

        <div style={{ position: 'relative' }}>
          <pre style={{
            background: '#04070A',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: '8px',
            padding: '14px',
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            color: '#A8DDF0',
            overflowX: 'auto',
            lineHeight: 1.5,
          }}>
            {pythonSnippet}
          </pre>
          <button
            onClick={handleCopy}
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              fontSize: '11px',
              padding: '4px 8px',
            }}
          >
            {copied ? '✓ Copied' : 'Copy Code'}
          </button>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', lineHeight: 1.4 }}>
          <strong>Architecture Note:</strong> The HTTP API currently renders a client-supplied reviewed timeline. Automatic detection and post-export verification will be exposed via <code>/v1/jobs/&#123;id&#125;/detect</code> and <code>/v1/jobs/&#123;id&#125;/verify</code> as core pipeline integration completes.
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
          <button className="primary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};
