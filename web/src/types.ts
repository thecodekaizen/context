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
    possible_effect: string;
    uncertainty: string;
  };
};
