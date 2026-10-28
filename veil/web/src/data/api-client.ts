import type { LocalJob, Timeline } from '../types';

const BASE_URL = ''; // Proxied via Vite to http://127.0.0.1:8020

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/openapi.json`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}

export async function createJob(videoFile: File): Promise<LocalJob> {
  const MAX_BYTES = 100 * 1024 * 1024; // 100 MiB limit
  if (videoFile.size > MAX_BYTES) {
    throw new ApiError(422, `Video exceeds 100 MiB limit (${(videoFile.size / 1024 / 1024).toFixed(1)} MiB).`);
  }

  const formData = new FormData();
  formData.append('video', videoFile);

  const res = await fetch(`${BASE_URL}/v1/jobs`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let detail = 'Upload failed';
    try {
      const json = await res.json();
      detail = json.detail || detail;
    } catch {
      // fallback
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

export async function getJob(jobId: string): Promise<LocalJob> {
  const res = await fetch(`${BASE_URL}/v1/jobs/${encodeURIComponent(jobId)}`);
  if (!res.ok) {
    let detail = 'Failed to fetch job';
    try {
      const json = await res.json();
      detail = json.detail || detail;
    } catch {
      // fallback
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

export async function redactJob(jobId: string, timeline?: Timeline): Promise<LocalJob> {
  const res = await fetch(`${BASE_URL}/v1/jobs/${encodeURIComponent(jobId)}/redact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: timeline ? JSON.stringify(timeline) : undefined,
  });

  if (!res.ok) {
    let detail = 'Redaction failed';
    try {
      const json = await res.json();
      detail = json.detail || detail;
    } catch {
      // fallback
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

export async function processNaturalJob(
  jobId: string,
  surfaces: Array<{
    track_id: string;
    start_frame?: number;
    corners?: Array<[number, number]>;
    kind: 'plate' | 'screen' | 'document';
    original_identifiers: string[];
  }>,
  timeline?: Timeline
): Promise<LocalJob> {
  const res = await fetch(`${BASE_URL}/v1/jobs/${encodeURIComponent(jobId)}/natural`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      media_is_synthetic_or_consented: true,
      timeline: timeline || null,
      surfaces,
    }),
  });

  if (!res.ok) {
    let detail = 'Natural replacement failed';
    try {
      const json = await res.json();
      detail = json.detail || detail;
    } catch {
      // fallback
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

export async function getNaturalReview(jobId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/v1/jobs/${encodeURIComponent(jobId)}/natural-review`);
  if (!res.ok) {
    let detail = 'Natural review not ready';
    try {
      const json = await res.json();
      detail = json.detail || detail;
    } catch {
      // fallback
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

export async function getReceipt(jobId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/v1/jobs/${encodeURIComponent(jobId)}/receipt`);
  if (!res.ok) {
    let detail = 'Receipt not ready';
    try {
      const json = await res.json();
      detail = json.detail || detail;
    } catch {
      // fallback
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

export function getExportUrl(jobId: string): string {
  return `${BASE_URL}/v1/jobs/${encodeURIComponent(jobId)}/export`;
}
