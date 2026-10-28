import React, { useState, useEffect } from 'react';
import type { StageId, OperatingMode, Finding, VideoVersion, LocalJob } from './types';
import { Header } from './components/Header';
import { StageNav } from './components/StageNav';
import { VideoDesk } from './components/VideoDesk';
import { FindingInspector } from './components/FindingInspector';
import { VerificationHero } from './components/VerificationHero';
import { Timeline } from './components/Timeline';
import { ImportModal } from './components/ImportModal';
import { ReceiptModal } from './components/ReceiptModal';
import { EmbedDrawer } from './components/EmbedDrawer';

import {
  RECORDED_FINDINGS,
  RECORDED_VERIFICATION_HERO,
  RECORDED_RECEIPT,
} from './data/recorded-example';

import {
  checkBackendHealth,
  createJob,
  redactJob,
  getExportUrl,
} from './data/api-client';

export const App: React.FC = () => {
  const [mode, setMode] = useState<OperatingMode>('recorded');
  const [stage, setStage] = useState<StageId>('verify');
  const [videoVersion, setVideoVersion] = useState<VideoVersion>('redacted');
  const [currentTimeMs, setCurrentTimeMs] = useState<number>(7500);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(RECORDED_FINDINGS[3]); // Default to hero residual

  // Modals
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [receiptModalOpen, setReceiptModalOpen] = useState(false);
  const [embedDrawerOpen, setEmbedDrawerOpen] = useState(false);

  // Live state
  const [backendOnline, setBackendOnline] = useState(false);
  const [liveJob, setLiveJob] = useState<LocalJob | null>(null);
  const [liveSourceUrl, setLiveSourceUrl] = useState<string | null>(null);
  const [liveExportUrl, setLiveExportUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Check loopback API status on mount
  useEffect(() => {
    checkBackendHealth().then(setBackendOnline);
    const interval = setInterval(() => {
      checkBackendHealth().then(setBackendOnline);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Update video version automatically when changing stages in recorded mode
  const handleSelectStage = (newStage: StageId) => {
    setStage(newStage);
    if (mode === 'recorded') {
      if (newStage === 'import' || newStage === 'detect') {
        setVideoVersion('source');
      } else if (newStage === 'redact' || newStage === 'verify') {
        setVideoVersion('redacted');
        if (newStage === 'verify') {
          setCurrentTimeMs(7500);
          setSelectedFinding(RECORDED_FINDINGS[3]);
        }
      } else if (newStage === 'repair') {
        setVideoVersion('repaired');
      } else if (newStage === 'export') {
        setVideoVersion('protected');
      }
    }
  };

  const handleInspectExposedFrame = () => {
    setVideoVersion('redacted');
    setCurrentTimeMs(7500);
    setSelectedFinding(RECORDED_FINDINGS[3]);
  };

  const handleSelectFindingById = (id: string) => {
    const match = RECORDED_FINDINGS.find((f) => f.id === id);
    if (match) {
      setSelectedFinding(match);
      setCurrentTimeMs(match.start_ms);
    }
  };

  // Live API File Upload
  const handleLiveUpload = async (file: File) => {
    setUploading(true);
    setUploadError(null);
    try {
      const job = await createJob(file);
      setLiveJob(job);
      setLiveSourceUrl(URL.createObjectURL(file));
      setMode('live');
      setStage('redact');
      setImportModalOpen(false);
    } catch (err: any) {
      setUploadError(err.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // Live Redact Render
  const handleLiveRedact = async () => {
    if (!liveJob) return;
    try {
      // Fetch saved smoke timeline to render
      const res = await fetch('/artifacts/timeline.json');
      const timeline = await res.json();
      const updatedJob = await redactJob(liveJob.id, timeline);
      setLiveJob(updatedJob);
      setLiveExportUrl(getExportUrl(liveJob.id));
      setStage('export');
    } catch (err: any) {
      alert(`Render error: ${err.detail || err.message}`);
    }
  };

  return (
    <div className="app-container">
      <Header
        mode={mode}
        onToggleMode={(m) => setMode(m)}
        onOpenEmbed={() => setEmbedDrawerOpen(true)}
        onOpenReceipt={() => setReceiptModalOpen(true)}
        backendOnline={backendOnline}
      />

      <StageNav
        currentStage={stage}
        onSelectStage={handleSelectStage}
        hasResidualAlert={mode === 'recorded'}
      />

      <main className="workspace-grid">
        {/* Left Column: Video Desk & Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <VideoDesk
            currentStage={stage}
            videoVersion={videoVersion}
            onSetVideoVersion={setVideoVersion}
            currentTimeMs={currentTimeMs}
            onSeek={setCurrentTimeMs}
            selectedFinding={selectedFinding}
            liveSourceUrl={liveSourceUrl}
            liveExportUrl={liveExportUrl}
            mode={mode}
          />

          <Timeline
            currentTimeMs={currentTimeMs}
            durationMs={18000}
            onSeek={setCurrentTimeMs}
            onSelectFindingById={handleSelectFindingById}
          />
        </div>

        {/* Right Column: Findings Inspector & Hero Verification Surface */}
        <aside className="desk-sidebar">
          {stage === 'verify' || stage === 'repair' ? (
            <VerificationHero
              heroData={RECORDED_VERIFICATION_HERO}
              onInspectExposedFrame={handleInspectExposedFrame}
              onSetVideoVersion={setVideoVersion}
              currentVideoVersion={videoVersion}
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {stage === 'import' && (
                <div className="sidebar-panel">
                  <h3 className="panel-title">Stage 1: Media Import</h3>
                  <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                    {mode === 'recorded'
                      ? 'Archived 18-second synthetic clip with fictional face, moving license plate, printed phone placard, and spoken phone digits.'
                      : 'Upload a video to the local engine for private processing.'}
                  </p>
                  <button className="primary" onClick={() => setImportModalOpen(true)}>
                    {mode === 'recorded' ? 'Open Import Dialog' : 'Upload Video to Job'}
                  </button>
                </div>
              )}

              {stage === 'redact' && mode === 'live' && (
                <div className="sidebar-panel">
                  <h3 className="panel-title">Stage 3: Render Redaction</h3>
                  <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                    Apply client-supplied reviewed timeline to current job #{liveJob?.id}.
                  </p>
                  <button className="primary" onClick={handleLiveRedact}>
                    Render Redacted MP4
                  </button>
                </div>
              )}

              {stage === 'export' && (
                <div className="sidebar-panel">
                  <h3 className="panel-title">Stage 6: Export & Receipts</h3>
                  <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                    Exported video with applied frame-accurate visual covers and muted audio interval.
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <a
                      href={mode === 'recorded' ? '/artifacts/protected.mp4' : (liveExportUrl || '#')}
                      download="veil-redacted.mp4"
                      className="primary"
                      style={{ textDecoration: 'none', textAlign: 'center', padding: '8px 14px', borderRadius: '8px' }}
                    >
                      Download Redacted MP4
                    </a>
                    <button onClick={() => setReceiptModalOpen(true)}>
                      Download Audit Receipt
                    </button>
                  </div>
                </div>
              )}

              <FindingInspector
                findings={RECORDED_FINDINGS}
                selectedFinding={selectedFinding}
                onSelectFinding={setSelectedFinding}
                onSeek={setCurrentTimeMs}
              />
            </div>
          )}
        </aside>
      </main>

      {/* Audit Scope Footer Bar */}
      <footer className="audit-scope-bar">
        <div className="scope-text">
          <span className="scope-icon">🛡</span>
          <span>
            <strong>Verification Scope:</strong> No exposure reported in 3 sampled frames (00:02.000, 00:07.500, 00:16.000). Other frames may contain missed exposures.
          </span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => setReceiptModalOpen(true)} className="toggle-btn">
            View Receipt
          </button>
          <a
            href={mode === 'recorded' ? '/artifacts/protected.mp4' : (liveExportUrl || '#')}
            download="veil-protected.mp4"
            className="toggle-btn"
            style={{ textDecoration: 'none' }}
          >
            Download Protected MP4
          </a>
        </div>
      </footer>

      {/* Dialog Modals & Drawers */}
      <ImportModal
        isOpen={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onUploadFile={handleLiveUpload}
        onSelectRecordedExample={() => {
          setMode('recorded');
          setStage('verify');
          setVideoVersion('redacted');
          setCurrentTimeMs(7500);
        }}
        uploading={uploading}
        uploadError={uploadError}
      />

      <ReceiptModal
        isOpen={receiptModalOpen}
        onClose={() => setReceiptModalOpen(false)}
        receipt={RECORDED_RECEIPT}
      />

      <EmbedDrawer
        isOpen={embedDrawerOpen}
        onClose={() => setEmbedDrawerOpen(false)}
      />
    </div>
  );
};
export default App;
