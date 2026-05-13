/**
 * HeadFade Ingestion Client SDK
 *
 * TypeScript client for the HeadFade ingestion pipeline API.
 * Handles: signed URL upload → Judge6 gate → forensic analysis → remix tree.
 */

import type {
  IngestionStage,
  IngestRequest,
  IngestResponse,
  Judge6Verdict,
  NukeMyDataRequest,
  NukeMyDataResponse,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_HEADFADE_API_URL ?? "http://localhost:8000";

interface IngestStartResult {
  jobId: string;
  videoId: string;
  signedUploadUrl: string;
  stage: IngestionStage;
}

interface IngestConfirmResult {
  status: string;
  job_id: string;
  video_id?: string;
  judge6_decision?: string;
  remix_node_id?: string;
  reason?: string;
  categories?: string[];
}

interface IngestStatusResult {
  job_id: string;
  video_id: string;
  stage: IngestionStage;
  judge6_decision?: string;
  error?: string;
}

/**
 * Start the ingestion pipeline. Returns a signed GCS upload URL.
 */
export async function startIngestion(
  req: IngestRequest & { creatorId: string },
): Promise<IngestStartResult> {
  const res = await fetch(`${API_BASE}/api/ingest/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: req.title,
      description: req.description,
      ground_truth: req.groundTruth,
      creator_id: req.creatorId,
      parent_remix_node_id: req.parentRemixNodeId ?? null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Failed to start ingestion");
  }

  const data = await res.json();
  return {
    jobId: data.job_id,
    videoId: data.video_id,
    signedUploadUrl: data.signed_upload_url,
    stage: data.stage,
  };
}

/**
 * Upload a video file directly to GCS using the signed URL.
 */
export async function uploadToGCS(
  signedUrl: string,
  file: File,
  onProgress?: (progress: number) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", signedUrl);
    xhr.setRequestHeader("Content-Type", "video/mp4");

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`));
      }
    });

    xhr.addEventListener("error", () => reject(new Error("Upload failed")));
    xhr.send(file);
  });
}

/**
 * Confirm upload and trigger Judge6 + forensic analysis.
 */
export async function confirmUpload(
  jobId: string,
): Promise<IngestConfirmResult> {
  const res = await fetch(`${API_BASE}/api/ingest/confirm/${jobId}`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Failed to confirm upload");
  }

  return res.json();
}

/**
 * Poll ingestion job status.
 */
export async function getIngestionStatus(
  jobId: string,
): Promise<IngestStatusResult> {
  const res = await fetch(`${API_BASE}/api/ingest/status/${jobId}`);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Failed to get status");
  }

  return res.json();
}

/**
 * Full ingestion flow: start → upload → confirm → poll until complete.
 */
export async function ingestVideo(
  req: IngestRequest & { creatorId: string },
  file: File,
  callbacks?: {
    onUploadProgress?: (progress: number) => void;
    onStageChange?: (stage: IngestionStage) => void;
  },
): Promise<IngestConfirmResult> {
  // Step 1: Start ingestion
  const start = await startIngestion(req);
  callbacks?.onStageChange?.("UPLOADING_TO_GCS" as IngestionStage);

  // Step 2: Upload to GCS
  await uploadToGCS(start.signedUploadUrl, file, callbacks?.onUploadProgress);
  callbacks?.onStageChange?.("JUDGE6_SCANNING" as IngestionStage);

  // Step 3: Confirm and trigger pipeline
  const result = await confirmUpload(start.jobId);
  callbacks?.onStageChange?.(result.status as IngestionStage);

  return result;
}

/**
 * Request cryptographic shredding (GDPR "right to deletion").
 */
export async function nukeMyData(
  req: NukeMyDataRequest,
): Promise<NukeMyDataResponse> {
  const res = await fetch(`${API_BASE}/api/account/nuke`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: req.userId,
      confirmation_phrase: req.confirmationPhrase,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Failed to delete data");
  }

  const data = await res.json();
  return {
    success: data.success,
    nodesOrphaned: data.nodes_orphaned,
    piiFieldsPurged: data.pii_fields_purged,
    completedAt: data.completed_at,
  };
}
