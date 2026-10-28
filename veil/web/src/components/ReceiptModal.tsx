import React from 'react';
import type { RecordedReceipt } from '../types';

interface ReceiptModalProps {
  isOpen: boolean;
  onClose: () => void;
  receipt: RecordedReceipt;
}

export const ReceiptModal: React.FC<ReceiptModalProps> = ({
  isOpen,
  onClose,
  receipt,
}) => {
  if (!isOpen) return null;

  const handleDownloadReceipt = () => {
    const blob = new Blob([JSON.stringify(receipt, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `veil-receipt-${receipt.version}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="receipt-title">
      <div className="modal-content">
        <div className="modal-header">
          <div>
            <h2 id="receipt-title" className="modal-title">Machine-Readable Audit Receipt</h2>
            <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
              Engine Specification v{receipt.version}
            </span>
          </div>
          <button onClick={onClose} aria-label="Close dialog">✕</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '12px' }}>
          <div style={{ background: 'var(--color-control-bg)', padding: '10px', borderRadius: '8px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Input SHA-256</span>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', wordBreak: 'break-all', marginTop: '2px' }}>
              {receipt.input_sha256 || 'N/A'}
            </div>
          </div>
          <div style={{ background: 'var(--color-control-bg)', padding: '10px', borderRadius: '8px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Export SHA-256</span>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', wordBreak: 'break-all', marginTop: '2px' }}>
              {receipt.output_sha256 || 'N/A'}
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', fontSize: '12px', textAlign: 'center' }}>
          <div style={{ background: 'var(--color-control-bg)', padding: '8px', borderRadius: '8px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Visual Covers</span>
            <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-accent-protect)' }}>
              {receipt.visual_regions_covered}
            </div>
          </div>
          <div style={{ background: 'var(--color-control-bg)', padding: '8px', borderRadius: '8px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Audio Mutes</span>
            <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-accent-amber)' }}>
              {receipt.audio_intervals_muted}
            </div>
          </div>
          <div style={{ background: 'var(--color-control-bg)', padding: '8px', borderRadius: '8px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Estimated Cost</span>
            <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-accent-mint)' }}>
              ${receipt.model_calls_estimated_cost_usd.toFixed(2)}
            </div>
          </div>
        </div>

        <div>
          <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Explicit Limitations & Audit Scope:</h4>
          <ul style={{ fontSize: '12px', color: 'var(--color-text-secondary)', paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {receipt.limitations.map((lim, idx) => (
              <li key={idx}>{lim}</li>
            ))}
          </ul>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
          <button onClick={onClose}>Close</button>
          <button className="primary" onClick={handleDownloadReceipt}>
            Download receipt.json
          </button>
        </div>
      </div>
    </div>
  );
};
