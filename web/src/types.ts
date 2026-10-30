export type CropAnalysis = {
  detected: boolean;
  confidence: number;
  crop_box?: { x: number; y: number; width: number; height: number };
  source_resolution?: [number, number];
  edited_resolution?: [number, number];
  area_retained_fraction?: number;
  area_omitted_fraction?: number;
  omitted_margins?: {
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
  }[];
  explanation?: string;
};

export type Segment = {
  id: string;
  kind: string;
  edited_start: number;
  edited_end: number;
  source_start: number | null;
  source_end: number | null;
  confidence: number;
};
export type Finding = {
  id: string;
  kind: string;
  source_start: number;
  source_end: number;
  edited_start?: number;
};
export type Evidence = {
  omission_evidence?: {
    status: string;
    omissions: {
      source_start: number;
      source_end: number;
      edit_position: number;
      confidence: number;
      matched_evidence: { modality: string };
      explanation: unknown;
    }[];
  };
  id: string;
  status: string;
  coverage: number;
  source: {
    duration: number;
    sha256: string;
    name?: string;
    provenance?: {
      attribution: string;
      license: string;
      url: string;
      transformations: string;
    };
  };
  edited: { duration: number };
  media: { source: string; edited: string };
  segments: Segment[];
  findings: Finding[];
  limitations: string[];
  crop_analysis?: CropAnalysis;
  audio_alignment?: {
    status: "analyzed" | "unavailable";
    segments: Segment[];
    reason?: string;
  };
};
export type Review = {
  cached?: boolean;
  clips?: {
    id: string;
    media: "source" | "edited";
    start: number;
    end: number;
    has_audio: boolean;
  }[];
  model: string;
  finding_id: string;
  interpretation: {
    observations: {
      text: string;
      citations: {
        media: "source" | "edited";
        media_start: number;
        media_end: number;
        clip_id: string;
      }[];
    }[];
    classification?: "harmless_edit" | "meaning_changed" | "inconclusive";
    possible_effect: string;
    uncertainty: string;
  };
};

export type DossierEvent = {
  id: string;
  text: string;
  start: number;
  end: number;
  modality: "visual" | "audio" | "on_screen";
};

export type DossierClaim = {
  id: string;
  text: string;
  origin: "speech" | "on_screen" | "supplied_caption";
  start?: number | null;
  end?: number | null;
};

export type DossierSource = {
  id: string;
  url: string;
  title: string;
  search_snippet: string;
  discovery: string;
  fetch_status: "fetched" | "unavailable";
  text?: string;
  http_status?: number;
  fetch_error?: string;
  content_sha256?: string;
};

export type DossierFinding = {
  claim_id: string;
  verdict: "supported" | "contradicted" | "inconclusive";
  explanation: string;
  source_refs: { source_id: string; excerpt: string }[];
  validation?: {
    citation_ids_and_excerpts_checked?: boolean;
    rejected_source_ids?: string[];
    semantic_entailment?: string;
  };
};

export type DossierAssessment = {
  summary: string;
  findings: DossierFinding[];
  provenance: string;
  missing_evidence: string[];
  validation?: { rejected_findings: unknown[] };
};

export type DossierMedia = {
  duration: number;
  width: number;
  height: number;
  codec: string;
  has_audio: boolean;
  sha256: string;
  analyzed_seconds: number;
  media_url: string;
  frames: { id: string; time: number; url: string }[];
};

export type Dossier = {
  id: string;
  schema_version?: string;
  model_configuration?: {
    provider: string;
    video_model: string;
    capabilities: { audio: boolean; web_search: boolean };
    media_destination: string;
  };
  mode: "single_video";
  status: "running" | "complete" | "partial" | "error";
  stage:
    | "queued"
    | "analyzing"
    | "comparing"
    | "retrieving"
    | "verifying"
    | "complete"
    | "partial"
    | "error";
  created_at: string;
  caption?: string;
  input_provenance?: {
    source_url?: string;
    catalog_url?: string;
    credit?: string;
    test_caption?: string;
    method?: string;
    filename?: string;
    original_recording_supplied?: boolean;
  };
  media?: DossierMedia;
  analysis?: {
    summary: string;
    validation?: { rejected_items: unknown[] };
    observations: DossierEvent[];
    claims: DossierClaim[];
    search_queries: string[];
    unknowns: string[];
  };
  retrieval?: {
    provider_search_performed: boolean;
    queries_proposed: string[];
    candidate_count: number;
    coverage: string;
    provider_summary?: string;
  };
  sources: DossierSource[];
  assessment?: DossierAssessment;
  authenticity?: {
    status: string;
    reason: string;
  };
  manipulation?: {
    status: string;
    reason: string;
  };
  comparison?: {
    status: string;
    basis?: string;
    scope: string;
    crop_analysis?: CropAnalysis;
    reviews: (Partial<Review> & {
      status: string;
      error?: string;
      finding: Finding & { modality?: string };
    })[];
  };
  source_video_retrieval?: {
    status: string;
    scope: string;
    candidates?: { title: string; status: string; reason?: string }[];
  };
  matched_source?: {
    status: "matched" | "no_match" | "ambiguous" | "unindexed";
    source_id?: string;
    source_name?: string;
    audio_coverage?: number;
    basis?: string;
    discovery?: string;
    source_url?: string;
    crop_analysis?: CropAnalysis;
    media?: { source: string; edited: string };
    coverage?: number;
    margin?: number;
    investigation_id?: string;
    finding_count?: number;
    findings?: Finding[];
    segments?: Segment[];
    audio_alignment?: {
      status: "analyzed" | "unavailable";
      segments: Segment[];
    };
    candidates?: {
      id: string;
      name: string;
      coverage: number;
      score: number;
    }[];
  };
  failure_log?: string[];
  error?: string;
};

export type PreludeTrajectoryPoint = {
  time: number;
  box: [number, number, number, number];
  velocity: [number, number];
  area: number;
};

export type PreludeActorTrack = {
  track_id: string;
  label: string;
  trajectory: PreludeTrajectoryPoint[];
  is_hazard: boolean;
  looming_rate: number;
  lateral_crossing_velocity: number;
};

export type PreludeFinding = {
  hazard_detected: boolean;
  risk_level: "nominal" | "low" | "medium" | "high" | "critical" | string;
  t_cue_seconds?: number | null;
  t_incident_seconds?: number | null;
  lead_time_seconds?: number | null;
  conflict_type: string;
  summary: string;
  hazard_actor?: string | null;
  kinematic_signals: {
    peak_lateral_flow?: number;
    mean_lateral_flow?: number;
    peak_looming_rate?: number;
    active_tracks_count?: number;
  };
  observations: string[];
  uncertainty: string;
  disclaimer: string;
};

export type PreludeDossier = {
  video_id: string;
  video_path: string;
  media_url?: string;
  duration: number;
  t_cutoff: number;
  t_incident?: number | null;
  lead_time?: number | null;
  hazard_detected: boolean;
  risk_level: string;
  finding: PreludeFinding;
  actors: PreludeActorTrack[];
  timeline_events: {
    time: number;
    kind: string;
    label: string;
    detail: string;
    is_hazard?: boolean;
    risk_level?: string;
  }[];
  disclaimer: string;
};

export type PreludeSample = {
  id: string;
  title: string;
  description: string;
  filename: string;
  t_incident?: number | null;
  t_cutoff: number;
  expected_hazard: boolean;
  conflict_type: string;
  available: boolean;
  media_url: string;
};
