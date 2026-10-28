/**
 * VEIL Frontend Type Contracts
 * Mirrors veil.core.models and recorded demonstration artifacts.
 */

export type FrameBox = [x1: number, y1: number, x2: number, y2: number];

export interface FrameRegion {
  frame: number;
  box: FrameBox;
  confidence?: number | null;
}

export type VisualCategory = 'face' | 'license_plate' | 'phone_number';

export interface VisualTrack {
  id: string;
  category: VisualCategory;
  source: string;
  action: 'cover';
  regions: FrameRegion[];
}

export interface AudioInterval {
  start_ms: number;
  end_ms: number;
  category: 'spoken_phone';
  source: string;
}

export interface Timeline {
  duration_ms: number;
  fps: number;
  width: number;
  height: number;
  visual_tracks: VisualTrack[];
  audio_intervals: AudioInterval[];
}

export type StageId = 'import' | 'detect' | 'redact' | 'verify' | 'repair' | 'export';

export type OperatingMode = 'recorded' | 'live';

export type VideoVersion = 'source' | 'redacted' | 'repaired' | 'protected';

export type FindingStatus = 
  | 'detected' 
  | 'protected' 
  | 'unprotected_residual' 
  | 'repair_rejected' 
  | 'repair_completed';

export interface Finding {
  id: string;
  title: string;
  category: VisualCategory | 'spoken_phone';
  start_ms: number;
  end_ms: number;
  source: string;
  status: FindingStatus;
  statusLabel: string;
  description: string;
  thumbnailUrl?: string;
  highlightBox?: FrameBox;
  confidence: number | null; // Null unless supplied by provider
  trackId?: string;
}

export interface VerificationSample {
  timestamp_s: number;
  timestamp_label: string;
  imageUrl: string;
  status: 'clean' | 'exposed';
  modelReview: string;
}

export interface VerificationHeroData {
  exposedTimestamp_ms: number;
  exposedTimestamp_label: string;
  frameIndex: number;
  frameImageUrl: string;
  returnedReason: string;
  exposedFieldLocation: FrameBox;
  rejectedRepairImageUrl: string;
  rejectedRepairReason: string;
  correctedRepairImageUrl: string;
  sampledPasses: VerificationSample[];
  scopeDisclaimer: string;
}

export interface RecordedReceipt {
  version: string;
  input_sha256?: string;
  output_sha256?: string;
  created_at: string;
  duration_seconds: number;
  visual_regions_covered: number;
  audio_intervals_muted: number;
  model_calls_estimated_cost_usd: number;
  verified_samples_count: number;
  limitations: string[];
}

export interface LocalJob {
  id: string;
  status: 'created' | 'rendering' | 'rendered' | 'failed';
  media?: {
    width: number;
    height: number;
    fps: number;
    duration_ms: number;
    size_bytes: number;
  };
  created_at?: string;
  rendered_at?: string;
  error?: string;
}
