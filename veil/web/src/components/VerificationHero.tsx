import React, { useState } from 'react';
import type { VerificationHeroData, VideoVersion } from '../types';

interface VerificationHeroProps {
  heroData: VerificationHeroData;
  onInspectExposedFrame: () => void;
  onSetVideoVersion: (version: VideoVersion) => void;
  currentVideoVersion: VideoVersion;
}

export const VerificationHero: React.FC<VerificationHeroProps> = ({
  heroData,
  onInspectExposedFrame,
  onSetVideoVersion,
  currentVideoVersion,
}) => {
  const [activeStep, setActiveStep] = useState<1 | 2 | 3 | 4>(1);

  return (
    <div className="hero-alert-card" aria-label="Hero Output Verification Alert">
      <div className="hero-alert-header">
        <span className="hero-alert-badge">Verification Audit</span>
        <div>
          <h2 className="hero-alert-title">A phone number is still visible.</h2>
          <span style={{ fontSize: '11px', color: 'var(--color-accent-red)', fontFamily: 'var(--font-mono)' }}>
            Caught at {heroData.exposedTimestamp_label} (Frame {heroData.frameIndex})
          </span>
        </div>
      </div>

      <p className="hero-alert-body">
        The initial redaction export covered the driver face and vehicle license plate, but left the printed delivery phone number unredacted. The post-export verifier caught the residual text on exported pixels.
      </p>

      {/* Progression Steps Selector */}
      <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
        <button
          className={`toggle-btn ${activeStep === 1 ? 'active' : ''}`}
          onClick={() => { setActiveStep(1); onSetVideoVersion('redacted'); }}
          title="Initial export where printed number was omitted"
        >
          1. Missed Export
        </button>
        <button
          className={`toggle-btn ${activeStep === 2 ? 'active' : ''}`}
          onClick={() => { setActiveStep(2); onSetVideoVersion('redacted'); onInspectExposedFrame(); }}
          title="Pixel inspection flagging remaining phone number"
        >
          2. Finding
        </button>
        <button
          className={`toggle-btn ${activeStep === 3 ? 'active' : ''}`}
          onClick={() => { setActiveStep(3); onSetVideoVersion('repaired'); }}
          title="Single-digit repair rejected by auditor"
        >
          3. Rejected Repair
        </button>
        <button
          className={`toggle-btn ${activeStep === 4 ? 'active' : ''}`}
          onClick={() => { setActiveStep(4); onSetVideoVersion('protected'); }}
          title="Whole-field repair passed review"
        >
          4. Corrected Export
        </button>
      </div>

      {/* Step 1 & 2: Omitted Number & Inspection */}
      {(activeStep === 1 || activeStep === 2) && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ position: 'relative' }}>
            <img
              src={heroData.frameImageUrl}
              alt="Exported frame at 00:07.500 showing exposed phone number on placard"
              className="hero-evidence-image"
            />
            <div
              style={{
                position: 'absolute',
                left: '52%',
                top: '46%',
                width: '18%',
                height: '12%',
                border: '2px solid var(--color-accent-red)',
                background: 'rgba(255, 120, 111, 0.3)',
                borderRadius: '2px',
                pointerEvents: 'none',
              }}
            />
          </div>

          <div style={{ fontSize: '12px', background: 'rgba(0,0,0,0.4)', padding: '8px 10px', borderRadius: '6px' }}>
            <strong style={{ color: 'var(--color-accent-red)' }}>Verifier Finding: </strong>
            <span>{heroData.returnedReason}</span>
          </div>

          <div className="hero-actions">
            <button className="danger" onClick={onInspectExposedFrame}>
              🔍 Inspect exposed frame at 00:07.500
            </button>
            <button
              onClick={() => { setActiveStep(3); onSetVideoVersion('repaired'); }}
              title="View the recorded first repair attempt"
            >
              View recorded repair attempt →
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Rejected Single-Digit Repair */}
      {activeStep === 3 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <img
            src={heroData.rejectedRepairImageUrl}
            alt="Single digit box covering only '2' on placard"
            className="hero-evidence-image"
          />

          <div style={{ fontSize: '12px', background: 'rgba(255, 120, 111, 0.1)', border: '1px solid var(--color-accent-red)', padding: '8px 10px', borderRadius: '6px' }}>
            <strong style={{ color: 'var(--color-accent-red)' }}>Audit Rejected: </strong>
            <span>{heroData.rejectedRepairReason}</span>
          </div>

          <div className="hero-actions">
            <button
              className="primary"
              onClick={() => { setActiveStep(4); onSetVideoVersion('protected'); }}
            >
              View corrected whole-field export →
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Corrected Whole-Field Export */}
      {activeStep === 4 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <img
            src={heroData.correctedRepairImageUrl}
            alt="Whole placard covered by opaque rectangle"
            className="hero-evidence-image"
          />

          <div style={{ fontSize: '12px', background: 'rgba(132, 224, 180, 0.1)', border: '1px solid var(--color-accent-mint)', padding: '8px 10px', borderRadius: '6px' }}>
            <strong style={{ color: 'var(--color-accent-mint)' }}>Passed Verification: </strong>
            <span>Whole-field bounding box tracks across placard movement. All phone digits completely covered.</span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className={currentVideoVersion === 'protected' ? 'primary' : ''}
              onClick={() => onSetVideoVersion('protected')}
            >
              ▶ Play corrected MP4
            </button>
            <button
              onClick={() => onSetVideoVersion('redacted')}
            >
              Compare with missed export
            </button>
          </div>
        </div>
      )}

      {/* Scoped 3-Sample Verification Result */}
      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: '10px', marginTop: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
          <span style={{ color: 'var(--color-accent-mint)', fontWeight: 600, fontSize: '12px' }}>✓</span>
          <strong style={{ fontSize: '12px', color: 'var(--color-text-main)' }}>
            No exposure reported in 3 sampled frames.
          </strong>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
          {heroData.sampledPasses.map((sample) => (
            <div key={sample.timestamp_label} style={{ fontSize: '10px', textAlign: 'center' }}>
              <img
                src={sample.imageUrl}
                alt={`Sample frame at ${sample.timestamp_label}`}
                style={{ width: '100%', borderRadius: '4px', border: '1px solid var(--color-border-subtle)', marginBottom: '2px' }}
              />
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)' }}>
                {sample.timestamp_label}
              </span>
            </div>
          ))}
        </div>

        <p style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '8px', lineHeight: 1.4 }}>
          {heroData.scopeDisclaimer}
        </p>
      </div>
    </div>
  );
};
