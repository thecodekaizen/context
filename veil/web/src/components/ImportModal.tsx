import React, { useState } from 'react';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadFile: (file: File) => Promise<void>;
  onSelectRecordedExample: () => void;
  uploading: boolean;
  uploadError: string | null;
}

export const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onUploadFile,
  onSelectRecordedExample,
  uploading,
  uploadError,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;
    await onUploadFile(selectedFile);
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="import-title">
      <div className="modal-content">
        <div className="modal-header">
          <h2 id="import-title" className="modal-title">Check a video for privacy exposures</h2>
          <button onClick={onClose} aria-label="Close dialog">✕</button>
        </div>

        <p style={{ color: 'var(--color-text-secondary)', fontSize: '13px' }}>
          Find faces, plate identifiers and spoken phone numbers, then inspect the exported result.
        </p>

        {/* Upload Limits Box */}
        <div style={{ background: 'var(--color-control-bg)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--color-border-subtle)', fontSize: '12px', color: 'var(--color-text-muted)' }}>
          <div><strong>Engine Input Limits:</strong> MP4 or MOV, max 100 MiB, up to 60s duration, max 1080p, audio stream required, constant frame rate.</div>
          <div style={{ marginTop: '4px', color: 'var(--color-text-secondary)' }}>
            🔒 <em>Note:</em> Uploading transfers the video only to your local loopback engine (<code>http://127.0.0.1:8018</code>). No cloud inference or third-party transfer occurs upon upload.
          </div>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragActive ? 'var(--color-accent-protect)' : 'var(--color-border-subtle)'}`,
            borderRadius: '12px',
            padding: '32px 16px',
            textAlign: 'center',
            background: dragActive ? 'rgba(105, 221, 243, 0.05)' : 'rgba(0,0,0,0.2)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div style={{ fontSize: '24px' }}>📁</div>
          <div style={{ fontSize: '14px', fontWeight: 500 }}>
            {selectedFile ? selectedFile.name : 'Drag and drop an MP4 file here, or click to browse'}
          </div>
          {selectedFile && (
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
              Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MiB
            </div>
          )}
          <input
            type="file"
            accept="video/mp4,video/quicktime"
            onChange={handleFileChange}
            id="video-file-input"
            style={{ display: 'none' }}
          />
          <label htmlFor="video-file-input">
            <span className="toggle-btn" style={{ cursor: 'pointer', display: 'inline-block' }}>
              Choose File
            </span>
          </label>
        </div>

        {uploadError && (
          <div style={{ color: 'var(--color-accent-red)', fontSize: '12px', background: 'rgba(255, 120, 111, 0.1)', padding: '8px 12px', borderRadius: '6px' }}>
            ⚠ {uploadError}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
          <button
            onClick={() => {
              onSelectRecordedExample();
              onClose();
            }}
            title="Inspect the completed smoke-test demonstration with real saved Meta model responses"
          >
            Open Recorded Example
          </button>

          <button
            className="primary"
            disabled={!selectedFile || uploading}
            onClick={handleUploadSubmit}
          >
            {uploading ? 'Uploading to Local Engine...' : 'Upload Video to Engine'}
          </button>
        </div>
      </div>
    </div>
  );
};
