import React from 'react';
import { REAL_DATASET_CLIPS } from '../data/real-datasets';
import type { RedactionStyle } from '../types';

interface DatasetToolbarProps {
  selectedClipId: string;
  onSelectClip: (clipId: string) => void;
  redactionStyle: RedactionStyle;
  onChangeStyle: (style: RedactionStyle) => void;
  isPairedView: boolean;
  onTogglePaired: () => void;
}

export const DatasetToolbar: React.FC<DatasetToolbarProps> = ({
  selectedClipId,
  onSelectClip,
  redactionStyle,
  onChangeStyle,
  isPairedView,
  onTogglePaired,
}) => {
  const currentClip = REAL_DATASET_CLIPS[selectedClipId];

  return (
    <div className="dataset-toolbar">
      <div className="clip-selector-group">
        <span className="toolbar-label">Dataset Video:</span>
        <div className="clip-pills">
          {Object.values(REAL_DATASET_CLIPS).map((clip) => {
            const isActive = clip.id === selectedClipId;
            return (
              <button
                key={clip.id}
                className={`clip-pill-btn ${isActive ? 'active' : ''}`}
                onClick={() => onSelectClip(clip.id)}
              >
                <span>{clip.title}</span>
              </button>
            );
          })}
        </div>
      </div>

      {!currentClip?.isTriView && (
        <div className="style-selector-group">
          <span className="toolbar-label">Redaction Style:</span>
          <div className="style-pills">
            <button
              className={`style-pill-btn natural ${redactionStyle === 'natural' ? 'active' : ''}`}
              onClick={() => onChangeStyle('natural')}
              title="Replace sensitive regions with realistic synthetic textures (DEMO plate/PRIVATE screen) and apply Gaussian face blur"
            >
              <span className="dot">●</span>
              <span>🛡 Natural Replacement (DEMO / Face Blur)</span>
            </button>

            <button
              className={`style-pill-btn opaque ${redactionStyle === 'opaque' ? 'active' : ''}`}
              onClick={() => onChangeStyle('opaque')}
              title="Paint solid black rectangles over detected regions (legacy baseline)"
            >
              <span className="dot">●</span>
              <span>⬛ Opaque Boxes (Hard Black Squares)</span>
            </button>
          </div>
        </div>
      )}

      {!currentClip?.isTriView && (
        <div className="view-toggle-group">
          <button
            className={`toggle-btn ${isPairedView ? 'active-toggle' : ''}`}
            onClick={onTogglePaired}
            title="Toggle between side-by-side synchronized comparison and single output view"
          >
            {isPairedView ? '🔲 Paired View (Source vs Output)' : '🖥 Single View'}
          </button>
        </div>
      )}
    </div>
  );
};
