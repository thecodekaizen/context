import React, { useState, useEffect } from 'react';
import type { Finding } from './types';
import { Header } from './components/Header';
import { DatasetToolbar } from './components/DatasetToolbar';
import { VideoDesk } from './components/VideoDesk';
import { FindingInspector } from './components/FindingInspector';
import { ImportModal } from './components/ImportModal';
import { ReceiptModal } from './components/ReceiptModal';
import { EmbedDrawer } from './components/EmbedDrawer';

import { REAL_DATASET_CLIPS } from './data/real-datasets';
import { RECORDED_RECEIPT } from './data/recorded-example';

import {
  checkBackendHealth,
  createJob,
} from './data/api-client';

export const App: React.FC = () => {
  // Navigation & mode
  const [appMode, setAppMode] = useState<'real_dataset' | 'live_upload'>('real_dataset');
  const [selectedClipId, setSelectedClipId] = useState<string>('vehicle_surface');
  const [redactionStyle, setRedactionStyle] = useState<'natural' | 'opaque'>('natural');
  const [isPairedView, setIsPairedView] = useState<boolean>(true);

  // Playback state
  const [currentTimeMs, setCurrentTimeMs] = useState<number>(0);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  // Modals
  const [receiptModalOpen, setReceiptModalOpen] = useState(false);
  const [embedDrawerOpen, setEmbedDrawerOpen] = useState(false);
  const [importModalOpen, setImportModalOpen] = useState(false);

  // Backend connection state
  const [backendOnline, setBackendOnline] = useState(false);

  // Live job execution state
  const [liveJob, setLiveJob] = useState<any | null>(null);
  const [liveSourceUrl, setLiveSourceUrl] = useState<string | null>(null);
  const [liveExportUrl, setLiveExportUrl] = useState<string | null>(null);
  const [liveReceipt, setLiveReceipt] = useState<any | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Check backend health periodically
  useEffect(() => {
    checkBackendHealth().then(setBackendOnline);
    const interval = setInterval(() => {
      checkBackendHealth().then(setBackendOnline);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const activeClip = REAL_DATASET_CLIPS[selectedClipId] || REAL_DATASET_CLIPS.vehicle_surface;

  // Determine active media URLs based on mode and redaction style
  let primaryVideoUrl = '';
  let secondaryVideoUrl = '';
  let primaryBadgeLabel = '';
  let secondaryBadgeLabel = '';

  if (appMode === 'real_dataset') {
    if (activeClip.isTriView) {
      primaryVideoUrl = activeClip.naturalUrl;
      secondaryVideoUrl = activeClip.sourceUrl;
      primaryBadgeLabel = 'Tri-View: Original vs Opaque vs Natural (Synced)';
      secondaryBadgeLabel = 'Original Input';
    } else if (redactionStyle === 'natural') {
      primaryVideoUrl = activeClip.naturalUrl;
      secondaryVideoUrl = activeClip.sourceUrl;
      primaryBadgeLabel = '🛡 Natural Replacement (DEMO Plate / Face Blur)';
      secondaryBadgeLabel = 'Original Unredacted Source';
    } else {
      primaryVideoUrl = activeClip.opaqueUrl;
      secondaryVideoUrl = activeClip.sourceUrl;
      primaryBadgeLabel = '⬛ Opaque Baseline (Hard Black Squares)';
      secondaryBadgeLabel = 'Original Unredacted Source';
    }
  } else {
    // Live job mode
    primaryVideoUrl = liveExportUrl || liveSourceUrl || '';
    secondaryVideoUrl = liveSourceUrl || '';
    primaryBadgeLabel = liveExportUrl
      ? redactionStyle === 'natural'
        ? '🛡 Live Export: Natural Replacement'
        : '⬛ Live Export: Opaque Redaction'
      : 'Uploaded Media';
    secondaryBadgeLabel = 'Original Source Video';
  }

  // Handle live custom upload
  const handleLiveUpload = async (file: File) => {
    setUploading(true);
    setUploadError(null);
    try {
      const sourceObjUrl = URL.createObjectURL(file);
      setLiveSourceUrl(sourceObjUrl);

      // Create job on backend
      const job = await createJob(file);
      setLiveJob(job);
      setUploading(false);
      setImportModalOpen(false);

      // Upload does not establish detections, a reviewed timeline, or original values.
      setLiveExportUrl(null);
      setLiveReceipt(null);
      setUploadError('Video uploaded. Processing needs detected or reviewed privacy targets. For natural replacement, supply the original identifier and a matching track through the API or SDK. No export has been created.');
      setProcessing(false);
    } catch (err: any) {
      setUploading(false);
      setProcessing(false);
      setUploadError(err.message || 'Processing failed on local engine');
    }
  };

  return (
    <div className="veil-app">
      <Header
        mode={appMode}
        onToggleMode={(m) => {
          setAppMode(m);
          if (m === 'live_upload') {
            setImportModalOpen(true);
          }
        }}
        onOpenEmbed={() => setEmbedDrawerOpen(true)}
        onOpenReceipt={() => setReceiptModalOpen(true)}
        backendOnline={backendOnline}
      />

      <main className="app-main" id="main-content">
        {/* Top Control Bar */}
        {appMode === 'real_dataset' ? (
          <DatasetToolbar
            selectedClipId={selectedClipId}
            onSelectClip={(id) => {
              setSelectedClipId(id);
              setCurrentTimeMs(0);
            }}
            redactionStyle={redactionStyle}
            onChangeStyle={setRedactionStyle}
            isPairedView={isPairedView}
            onTogglePaired={() => setIsPairedView(!isPairedView)}
          />
        ) : (
          <div className="dataset-toolbar live-banner">
            <div className="clip-selector-group">
              <span className="toolbar-label">Live API Session:</span>
              <span className="live-job-tag">
                {liveJob ? `Job ID: ${liveJob.id} (${liveJob.status})` : 'No custom video loaded'}
              </span>
            </div>

            <div className="style-selector-group">
              <button
                className="primary"
                onClick={() => setImportModalOpen(true)}
                disabled={uploading || processing}
              >
                {uploading ? 'Uploading...' : processing ? 'Processing...' : '📁 Upload New Video File'}
              </button>

              <button
                className={`style-pill-btn natural ${redactionStyle === 'natural' ? 'active' : ''}`}
                onClick={() => setRedactionStyle('natural')}
              >
                🛡 Natural Mode
              </button>

              <button
                className={`style-pill-btn opaque ${redactionStyle === 'opaque' ? 'active' : ''}`}
                onClick={() => setRedactionStyle('opaque')}
              >
                ⬛ Opaque Mode
              </button>
            </div>
          </div>
        )}

        {/* Video Desk Viewport & Inspector Split */}
        <div className="main-workbench">
          <div className="video-desk-container">
            <VideoDesk
              primaryUrl={primaryVideoUrl}
              secondaryUrl={secondaryVideoUrl}
              primaryBadge={primaryBadgeLabel}
              secondaryBadge={secondaryBadgeLabel}
              currentTimeMs={currentTimeMs}
              onSeek={setCurrentTimeMs}
              selectedFinding={selectedFinding}
              isPairedView={isPairedView}
              onTogglePaired={() => setIsPairedView(!isPairedView)}
              isTriView={appMode === 'real_dataset' && activeClip.isTriView}
            />
          </div>

          <aside className="inspector-container">
            <FindingInspector
              clip={activeClip}
              redactionStyle={redactionStyle}
              onOpenReceipt={() => setReceiptModalOpen(true)}
              selectedFinding={selectedFinding}
              onSelectFinding={setSelectedFinding}
            />
          </aside>
        </div>
      </main>

      {/* Modals & Drawers */}
      <ImportModal
        isOpen={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onUploadFile={handleLiveUpload}
        onSelectRecordedExample={() => {
          setAppMode('real_dataset');
          setSelectedClipId('vehicle_surface');
        }}
        uploading={uploading}
        uploadError={uploadError}
      />

      <ReceiptModal
        isOpen={receiptModalOpen}
        onClose={() => setReceiptModalOpen(false)}
        receipt={liveReceipt || RECORDED_RECEIPT}
      />

      <EmbedDrawer
        isOpen={embedDrawerOpen}
        onClose={() => setEmbedDrawerOpen(false)}
      />
    </div>
  );
};

export default App;
