import React from 'react';
import type { StageId } from '../types';

interface StageNavProps {
  currentStage: StageId;
  onSelectStage: (stage: StageId) => void;
  hasResidualAlert: boolean;
}

interface StageItem {
  id: StageId;
  stepNum: string;
  label: string;
  isAlert?: boolean;
}

export const StageNav: React.FC<StageNavProps> = ({
  currentStage,
  onSelectStage,
  hasResidualAlert,
}) => {
  const stages: StageItem[] = [
    { id: 'import', stepNum: '01', label: 'Import' },
    { id: 'detect', stepNum: '02', label: 'Detect' },
    { id: 'redact', stepNum: '03', label: 'Redact & Compare' },
    { id: 'verify', stepNum: '04', label: 'Verify (Hero)', isAlert: hasResidualAlert },
    { id: 'repair', stepNum: '05', label: 'Repair Progression' },
    { id: 'export', stepNum: '06', label: 'Export & Audit' },
  ];

  return (
    <nav className="stage-nav" aria-label="Privacy Pipeline Stages">
      {stages.map((stage) => {
        const isActive = currentStage === stage.id;
        const classes = [
          'stage-tab',
          isActive ? 'active' : '',
          stage.isAlert ? 'hero-alert' : '',
        ].filter(Boolean).join(' ');

        return (
          <button
            key={stage.id}
            className={classes}
            onClick={() => onSelectStage(stage.id)}
            aria-current={isActive ? 'step' : undefined}
          >
            <span className="stage-step-num">{stage.stepNum}</span>
            <span>{stage.label}</span>
            {stage.isAlert && <span style={{ color: 'var(--color-accent-red)' }}>⚠</span>}
          </button>
        );
      })}
    </nav>
  );
};
